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

export const webAnalyzer: AnalyzerModule = {
  name: "web",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];

    const allFiles = walkFiles(workspace.rootPath);

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-WEB-001": {
          // Scan config files for debug mode indicators
          const configExtensions = /\.(env|json|yaml|yml|toml|ini|conf|config\.js|config\.ts)$/i;
          const debugRegex = /DEBUG\s*=\s*True|debug\s*:\s*true|NODE_ENV\s*[=:]\s*['"]?development['"]?/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
            if (!configExtensions.test(f)) continue;
            const matches = scanFileContent(f, debugRegex);
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
                    pattern: "DEBUG/development mode enabled",
                  })),
                },
                [...new Set(matchedFiles)],
                lineNumbers,
              ),
            );
          }
          break;
        }

        case "GHA-WEB-002": {
          // Stub: scan for unescaped template patterns (Handlebars {{{ }}} or Django | safe)
          const templateRegex = /\{\{\{[\s\S]*?\}\}\}|\|\s*safe/;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of allFiles) {
            const matches = scanFileContent(f, templateRegex);
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
                  pattern: "unescaped template output",
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
        module_name: "web",
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
