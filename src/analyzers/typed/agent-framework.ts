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

export const agentFrameworkAnalyzer: AnalyzerModule = {
  name: "agent_framework",

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
        case "GHA-AGENT-001": {
          // Stub: scan for unrestricted tool/function registration patterns
          const regex = /register.*tool|addTool|tool.*register|allowAllTools|allow_all_tools/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
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
                  pattern: "tool registration keyword",
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

        case "GHA-AGENT-002": {
          // Stub: scan for unbounded agent loop / recursion indicators
          const regex = /while\s*\(\s*true\s*\)|loop_forever|max_iterations\s*=\s*-1|recursion_limit\s*=\s*0/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
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
                  pattern: "unbounded agent loop indicator",
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
        module_name: "agent_framework",
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
