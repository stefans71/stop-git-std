import { readdirSync } from "fs";
import { join } from "path";
import { emitFinding, scanFileContent, shouldSkipInTypedAnalyzer, classifyFile } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

function walkFiles(dir: string): string[] {
  const results: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "node_modules" || entry.name === ".git") continue;
      results.push(...walkFiles(full));
    } else {
      results.push(full);
    }
  }
  return results;
}

export const aiLlmAnalyzer: AnalyzerModule = {
  name: "ai_llm",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];

    let allFiles: string[] = [];
    try {
      allFiles = walkFiles(workspace.rootPath);
    } catch {
      // workspace not accessible
    }
    const scanFiles = allFiles.filter((f) => !shouldSkipInTypedAnalyzer(f));

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-AI-001": {
          // Stub: basic scan for model execution patterns that may indicate unsafe eval
          const regex = /model.*exec|exec.*model|model.*eval|eval.*model/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of scanFiles) {
            const matches = scanFileContent(f, regex);
            for (const m of matches) {
              matchedFiles.push(m.path);
              lineNumbers.push(m.lineNumber);
            }
          }

          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "regex_match",
                records: matchedFiles.map((f, i) => ({
                  file: f,
                  line: lineNumbers[i],
                  pattern: "model execution keyword",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            const hasCodeMatch = [...new Set(matchedFiles)].some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
          break;
        }

        case "GHA-AI-002": {
          // Stub: basic scan for secret/sensitive data in prompt context
          const regex = /secret.*prompt|prompt.*secret|system.*prompt.*key|api.?key.*prompt/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of scanFiles) {
            const matches = scanFileContent(f, regex);
            for (const m of matches) {
              matchedFiles.push(m.path);
              lineNumbers.push(m.lineNumber);
            }
          }

          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "regex_match",
                records: matchedFiles.map((f, i) => ({
                  file: f,
                  line: lineNumbers[i],
                  pattern: "secret in prompt context",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            const hasCodeMatch = [...new Set(matchedFiles)].some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
          break;
        }

        case "GHA-AI-003": {
          // Scan for missing rate limiting on LLM calls — code files only
          // Config files (.yaml/.json) mentioning LLM providers are expected (they configure
          // which model to use, not call it), so we exclude them to avoid false positives.
          const regex = /rate.*limit|rateLimit|throttl/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          const llmCallRegex = /openai\.|anthropic\.|completion\(|chat\.create|generate\(/i;
          const codeOnlyFiles = scanFiles.filter((f) => classifyFile(f) === "code");
          const filesWithLlmCalls = new Set<string>();
          const filesWithRateLimit = new Set<string>();

          for (const f of codeOnlyFiles) {
            if (scanFileContent(f, llmCallRegex).length > 0) {
              filesWithLlmCalls.add(f);
            }
            if (scanFileContent(f, regex).length > 0) {
              filesWithRateLimit.add(f);
            }
          }

          const unprotected = [...filesWithLlmCalls].filter((f) => !filesWithRateLimit.has(f));

          if (unprotected.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "heuristic",
                records: unprotected.map((f) => ({
                  file: f,
                  pattern: "LLM API call without visible rate limiting",
                })),
              },
              unprotected,
            );
            const hasCodeMatch = unprotected.some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
          break;
        }

        default:
          break;
      }
    }

    return {
      findings,
      moduleResult: {
        module_name: "ai_llm",
        status: "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
        warnings: [],
        errors: [],
        coverage: {
          files_scanned: scanFiles.length,
        },
      },
    };
  },
};
