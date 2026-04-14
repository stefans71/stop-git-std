import { readdirSync } from "fs";
import { join, extname } from "path";
import { emitFinding, scanFileContent } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

/** Return only the top-level source files (non-recursive) plus index files one level deep. */
function getTopLevelModuleFiles(rootPath: string): string[] {
  const results: string[] = [];
  const sourceExts = new Set([".ts", ".js", ".mjs", ".cjs", ".py", ".rb", ".go", ".java", ".rs"]);

  let entries;
  try {
    entries = readdirSync(rootPath, { withFileTypes: true });
  } catch {
    return results;
  }

  for (const entry of entries) {
    if (entry.name === "node_modules" || entry.name === ".git") continue;
    const full = join(rootPath, entry.name);

    if (entry.isDirectory()) {
      // One level deep: look for index files inside src/, lib/, etc.
      if (["src", "lib", "dist"].includes(entry.name.toLowerCase())) {
        try {
          for (const sub of readdirSync(full, { withFileTypes: true })) {
            if (!sub.isDirectory() && sourceExts.has(extname(sub.name))) {
              results.push(join(full, sub.name));
            }
          }
        } catch {
          // skip
        }
      }
    } else if (sourceExts.has(extname(entry.name))) {
      results.push(full);
    }
  }

  return results;
}

export const libraryPackageAnalyzer: AnalyzerModule = {
  name: "library_package",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];

    const moduleFiles = getTopLevelModuleFiles(workspace.rootPath);

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-PKG-001": {
          // Scan top-level module files for network/process access at module scope
          // Patterns: fetch(, http.get(, net.connect(, child_process, subprocess
          const networkProcessRegex =
            /\bfetch\s*\(|http\.get\s*\(|https\.get\s*\(|net\.connect\s*\(|child_process|subprocess\b/;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of moduleFiles) {
            const matches = scanFileContent(f, networkProcessRegex);
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
                    pattern: "network or process access at module scope",
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
        module_name: "library_package",
        status: "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
        warnings: [],
        errors: [],
        coverage: {
          files_scanned: moduleFiles.length,
        },
      },
    };
  },
};
