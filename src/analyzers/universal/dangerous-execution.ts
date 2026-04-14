import { existsSync, readdirSync } from "fs";
import { join, extname } from "path";
import { emitFinding, readFileContent, scanFileContent } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", "vendor", "__pycache__"]);

function walkFiles(dir: string, maxDepth = 5, depth = 0): string[] {
  if (depth > maxDepth) return [];
  const results: string[] = [];
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (SKIP_DIRS.has(entry.name)) continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        results.push(...walkFiles(full, maxDepth, depth + 1));
      } else {
        results.push(full);
      }
    }
  } catch {
    // ignore permission errors
  }
  return results;
}

export const dangerousExecutionAnalyzer: AnalyzerModule = {
  name: "dangerous_execution",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];
    const root = workspace.rootPath;

    let allFiles: string[] | null = null;
    const getFiles = () => {
      if (!allFiles) allFiles = walkFiles(root, 5);
      return allFiles;
    };

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-EXEC-001": {
          // curl|bash piping pattern
          // Matches: curl ... | bash, curl ... | sh, wget ... | bash, etc.
          const curlBashRegex = /\b(curl|wget)\b[^|#\n]*\|\s*(bash|sh|zsh|fish|dash)\b/;
          const matches: Array<{ path: string; lineNumber: number; line: string }> = [];
          const affectedFiles: string[] = [];

          // Check shell scripts, CI configs, Makefiles, scripts
          const targetExts = new Set([".sh", ".bash", ".zsh", ".yml", ".yaml", ".mk", ""]);
          const targetNames = new Set(["Makefile", "makefile", "GNUmakefile"]);

          for (const filePath of getFiles()) {
            const ext = extname(filePath).toLowerCase();
            const baseName = filePath.split("/").pop() ?? "";
            if (!targetExts.has(ext) && !targetNames.has(baseName)) continue;

            const hits = scanFileContent(filePath, curlBashRegex);
            for (const hit of hits) {
              matches.push({
                path: filePath.replace(root + "/", ""),
                lineNumber: hit.lineNumber,
                line: hit.line.slice(0, 200),
              });
              if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "curl_pipe_shell",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    snippet: m.line,
                    detail: `curl/wget piped to shell at ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-EXEC-002": {
          // package.json lifecycle hooks
          const pkgPath = `${root}/package.json`;
          if (!existsSync(pkgPath)) break;

          const content = readFileContent(pkgPath);
          if (!content) break;

          let pkg: Record<string, unknown>;
          try {
            pkg = JSON.parse(content) as Record<string, unknown>;
          } catch {
            break;
          }

          const dangerousHooks = ["preinstall", "install", "postinstall", "prepublish", "prepare"];
          const scripts = pkg["scripts"] as Record<string, string> | undefined;
          if (!scripts) break;

          const hookMatches: Array<{ hook: string; command: string }> = [];
          for (const hook of dangerousHooks) {
            if (scripts[hook]) {
              hookMatches.push({ hook, command: scripts[hook]! });
            }
          }

          if (hookMatches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "lifecycle_hook",
                  records: hookMatches.map((h) => ({
                    hook: h.hook,
                    command: h.command.slice(0, 200),
                    detail: `Lifecycle hook "${h.hook}" executes: ${h.command.slice(0, 100)}`,
                  })),
                },
                [pkgPath],
              ),
            );
          }
          break;
        }

        case "GHA-EXEC-003": {
          // Python subprocess with shell=True
          const shellTrueRegex = /subprocess\.(call|run|Popen|check_output|check_call)\s*\([^)]*shell\s*=\s*True/;
          const matches: Array<{ path: string; lineNumber: number; line: string }> = [];
          const affectedFiles: string[] = [];

          const pyFiles = getFiles().filter((f) => f.endsWith(".py"));
          for (const filePath of pyFiles) {
            const hits = scanFileContent(filePath, shellTrueRegex);
            for (const hit of hits) {
              matches.push({
                path: filePath.replace(root + "/", ""),
                lineNumber: hit.lineNumber,
                line: hit.line.slice(0, 200),
              });
              if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "subprocess_shell_true",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    snippet: m.line,
                    detail: `subprocess with shell=True at ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-EXEC-004": {
          // Unsafe deserialization
          const matches: Array<{ path: string; lineNumber: number; line: string; type: string }> =
            [];
          const affectedFiles: string[] = [];

          const targetExts = new Set([".py", ".rb", ".js", ".ts", ".php"]);
          const scanFiles = getFiles().filter((f) => targetExts.has(extname(f).toLowerCase()));

          for (const filePath of scanFiles) {
            // pickle.loads
            const pickleHits = scanFileContent(filePath, /\bpickle\.loads?\s*\(/);
            for (const hit of pickleHits) {
              matches.push({
                path: filePath.replace(root + "/", ""),
                lineNumber: hit.lineNumber,
                line: hit.line.slice(0, 200),
                type: "pickle.loads",
              });
              if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
            }

            // yaml.load without SafeLoader
            const content = readFileContent(filePath, 524288);
            if (content) {
              const lines = content.split("\n");
              for (let i = 0; i < lines.length; i++) {
                const line = lines[i]!;
                if (/yaml\.load\s*\(/.test(line) && !/Loader\s*=\s*yaml\.(Safe|Full)Loader/.test(line)) {
                  matches.push({
                    path: filePath.replace(root + "/", ""),
                    lineNumber: i + 1,
                    line: line.trim().slice(0, 200),
                    type: "yaml.load (unsafe)",
                  });
                  if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
                }
                // serialize.*eval patterns
                if (/serialize\.[a-z]*eval\b/i.test(line)) {
                  matches.push({
                    path: filePath.replace(root + "/", ""),
                    lineNumber: i + 1,
                    line: line.trim().slice(0, 200),
                    type: "serialize.*eval",
                  });
                  if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
                }
              }
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "unsafe_deserialization",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    deserialization_type: m.type,
                    snippet: m.line,
                    detail: `Unsafe deserialization (${m.type}) at ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-EXEC-005": {
          // Remote code exec heuristic: fetch + eval in same file
          const matches: Array<{ path: string; fetchLine: number; evalLine: number }> = [];
          const affectedFiles: string[] = [];

          const fetchRegex = /\bfetch\s*\(/;
          const evalRegex = /\beval\s*\(/;

          const jsFiles = getFiles().filter((f) => {
            const ext = extname(f).toLowerCase();
            return ext === ".js" || ext === ".ts" || ext === ".mjs" || ext === ".cjs";
          });

          for (const filePath of jsFiles) {
            const content = readFileContent(filePath, 524288);
            if (!content) continue;

            const fetchHits = scanFileContent(filePath, fetchRegex);
            const evalHits = scanFileContent(filePath, evalRegex);

            if (fetchHits.length > 0 && evalHits.length > 0) {
              matches.push({
                path: filePath.replace(root + "/", ""),
                fetchLine: fetchHits[0]!.lineNumber,
                evalLine: evalHits[0]!.lineNumber,
              });
              affectedFiles.push(filePath);
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "fetch_eval_rce",
                  records: matches.map((m) => ({
                    path: m.path,
                    fetch_line: m.fetchLine,
                    eval_line: m.evalLine,
                    detail: `fetch() and eval() co-located in ${m.path} (fetch:${m.fetchLine}, eval:${m.evalLine})`,
                  })),
                },
                affectedFiles,
                matches.flatMap((m) => [m.fetchLine, m.evalLine]),
              ),
            );
          }
          break;
        }
      }
    }

    return {
      findings,
      moduleResult: {
        module_name: "dangerous_execution",
        status: "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
        warnings: [],
        errors: [],
      },
    };
  },
};
