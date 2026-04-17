import { readdirSync } from "fs";
import { join } from "path";
import { emitFinding, scanFileContent } from "../base.ts";
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

export const apiAnalyzer: AnalyzerModule = {
  name: "api",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];

    let allFiles: string[] = [];
    try {
      allFiles = walkFiles(workspace.rootPath);
    } catch {
      // workspace not accessible
    }

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-API-001": {
          // Stub: basic scan for authentication bypass keywords
          const authRegex = /no.?auth|bypass.?auth|skip.?auth|authentication\s*:\s*false/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
            const matches = scanFileContent(f, authRegex);
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
                  pattern: "authentication bypass indicator",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            finding.confidence = "low";
            findings.push(finding);
          }
          break;
        }

        case "GHA-API-002": {
          // Scan for permissive CORS configuration
          const corsRegex = /Access-Control-Allow-Origin\s*:\s*\*|cors\s*\(\s*\{[^}]*origin\s*:\s*['"`]\*['"`]/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
            const matches = scanFileContent(f, corsRegex);
            for (const m of matches) {
              matchedFiles.push(m.path);
              lineNumbers.push(m.lineNumber);
            }
          }

          if (matchedFiles.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "regex_match",
                  records: matchedFiles.map((f, i) => ({
                    file: f,
                    line: lineNumbers[i],
                    pattern: "wildcard CORS origin",
                  })),
                },
                [...new Set(matchedFiles)],
                lineNumbers,
              ),
            );
          }
          break;
        }

        case "GHA-API-003": {
          // Stub: basic scan for missing rate limit indicators
          const rateLimitRegex = /no.?rate.?limit|rateLimit\s*:\s*false|disable.*throttl/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
            const matches = scanFileContent(f, rateLimitRegex);
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
                  pattern: "rate limiting disabled",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            finding.confidence = "low";
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
        module_name: "api",
        status: "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
        warnings: [],
        errors: [],
        coverage: {
          files_scanned: allFiles.length,
        },
      },
    };
  },
};
