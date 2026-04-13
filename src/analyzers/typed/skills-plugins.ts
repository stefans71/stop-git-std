import { readdirSync } from "fs";
import { join, basename } from "path";
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

export const skillsPluginsAnalyzer: AnalyzerModule = {
  name: "skills_plugins",

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
        case "GHA-PLUGIN-001": {
          // Scan manifest/plugin JSON files for broad permission declarations
          const manifestFiles = allFiles.filter((f) => {
            const name = basename(f).toLowerCase();
            return name === "plugin.json" || name === "manifest.json" || name === "plugin-manifest.json";
          });

          const broadPermRegex = /"permissions"\s*:\s*\[\s*"\*"/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of manifestFiles) {
            const matches = scanFileContent(f, broadPermRegex);
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
                    pattern: 'broad wildcard permissions declaration',
                  })),
                },
                [...new Set(matchedFiles)],
                lineNumbers,
              ),
            );
          }
          break;
        }

        case "GHA-PLUGIN-002": {
          // Scan for prompt injection patterns in all files
          const injectionRegex = /ignore previous instructions|you are now|system\s*:/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
            const matches = scanFileContent(f, injectionRegex);
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
                    pattern: "prompt injection indicator",
                  })),
                },
                [...new Set(matchedFiles)],
                lineNumbers,
              ),
            );
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
        module_name: "skills_plugins",
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
