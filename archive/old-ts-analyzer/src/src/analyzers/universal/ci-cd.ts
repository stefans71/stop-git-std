import { existsSync, readdirSync, readFileSync } from "fs";
import { join } from "path";
import { emitFinding, readFileContent, scanFileContent } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

function getWorkflowFiles(root: string, profileWorkflows: string[]): string[] {
  // Use profile artifact list if available, otherwise discover
  if (profileWorkflows.length > 0) {
    return profileWorkflows
      .map((w) => (w.startsWith("/") ? w : join(root, w)))
      .filter((w) => existsSync(w));
  }
  const workflowDir = join(root, ".github", "workflows");
  if (!existsSync(workflowDir)) return [];
  try {
    return readdirSync(workflowDir)
      .filter((f) => f.endsWith(".yml") || f.endsWith(".yaml"))
      .map((f) => join(workflowDir, f));
  } catch {
    return [];
  }
}

/**
 * Simple line-by-line YAML key extractor — avoids pulling in a YAML parser.
 * Returns the raw text content of a field by scanning lines.
 */
function extractYamlField(content: string, field: string): string[] {
  const results: string[] = [];
  const lines = content.split("\n");
  for (const line of lines) {
    const m = line.match(new RegExp(`^\\s*${field}\\s*:\\s*(.*)$`));
    if (m?.[1] !== undefined) results.push(m[1].trim());
  }
  return results;
}

export const ciCdAnalyzer: AnalyzerModule = {
  name: "ci_cd",

  async analyze(workspace, profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];
    const root = workspace.rootPath;

    const workflowFiles = getWorkflowFiles(root, profile.artifacts.workflows);

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-CI-001": {
          // pull_request_target trigger in workflow YAML
          const matches: Array<{ path: string; lineNumber: number; line: string }> = [];
          const affectedFiles: string[] = [];

          for (const wf of workflowFiles) {
            const hits = scanFileContent(wf, /pull_request_target/);
            for (const hit of hits) {
              matches.push({
                path: wf.replace(root + "/", ""),
                lineNumber: hit.lineNumber,
                line: hit.line,
              });
              if (!affectedFiles.includes(wf)) affectedFiles.push(wf);
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "pull_request_target_trigger",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    snippet: m.line,
                    detail: `pull_request_target trigger found in ${m.path}:${m.lineNumber} — allows fork PRs to access secrets`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-CI-002": {
          // Broad permissions (write-all)
          const matches: Array<{ path: string; lineNumber: number; line: string }> = [];
          const affectedFiles: string[] = [];

          const writeAllRegex = /permissions\s*:\s*write-all/i;

          for (const wf of workflowFiles) {
            const writeAllHits = scanFileContent(wf, writeAllRegex);
            for (const hit of writeAllHits) {
              matches.push({
                path: wf.replace(root + "/", ""),
                lineNumber: hit.lineNumber,
                line: hit.line,
              });
              if (!affectedFiles.includes(wf)) affectedFiles.push(wf);
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "broad_permissions",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    snippet: m.line,
                    detail: `Broad write-all permissions in ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-CI-003": {
          // Unpinned action references (uses: not pinned to SHA)
          // A pinned ref looks like: uses: owner/action@abcdef1234567890abcdef1234567890abcdef12
          // Unpinned: uses: owner/action@v1, @main, @master, @latest, etc.
          const unpinnedRegex = /^\s*uses\s*:\s*(.+)$/;
          const sha1Regex = /^[a-f0-9]{40}$/;

          const matches: Array<{ path: string; lineNumber: number; uses: string }> = [];
          const affectedFiles: string[] = [];

          for (const wf of workflowFiles) {
            const hits = scanFileContent(wf, unpinnedRegex);
            for (const hit of hits) {
              // Extract the "uses" value
              const usesMatch = hit.line.match(/uses\s*:\s*(.+)/);
              if (!usesMatch?.[1]) continue;
              const usesValue = usesMatch[1].trim().replace(/^['"]|['"]$/g, "");

              // docker:// references are fine
              if (usesValue.startsWith("docker://")) continue;
              // local references ./ are fine
              if (usesValue.startsWith("./")) continue;

              // Extract the ref part (after @)
              const atIdx = usesValue.lastIndexOf("@");
              if (atIdx === -1) {
                // No @ at all — definitely unpinned
                matches.push({
                  path: wf.replace(root + "/", ""),
                  lineNumber: hit.lineNumber,
                  uses: usesValue,
                });
                if (!affectedFiles.includes(wf)) affectedFiles.push(wf);
                continue;
              }

              const ref = usesValue.slice(atIdx + 1).trim();
              if (!sha1Regex.test(ref)) {
                matches.push({
                  path: wf.replace(root + "/", ""),
                  lineNumber: hit.lineNumber,
                  uses: usesValue,
                });
                if (!affectedFiles.includes(wf)) affectedFiles.push(wf);
              }
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "unpinned_action",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    uses: m.uses,
                    detail: `Unpinned action reference "${m.uses}" at ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-CI-004": {
          // Shell injection via ${{ github.event.* }} in run steps
          // Dangerous: run: | ... ${{ github.event.pull_request.title }} ...
          const injectionRegex = /\$\{\{\s*github\.event\.(pull_request|issue|comment|head_commit|inputs)\./;

          const matches: Array<{ path: string; lineNumber: number; line: string; expr: string }> =
            [];
          const affectedFiles: string[] = [];

          for (const wf of workflowFiles) {
            const content = readFileContent(wf);
            if (!content) continue;

            // We need to check if the interpolation appears inside a "run:" block
            // Simple heuristic: if the pattern appears within a few lines of a "run:" line
            const lines = content.split("\n");
            let inRunBlock = false;
            let runIndent = -1;

            for (let i = 0; i < lines.length; i++) {
              const line = lines[i]!;
              const trimmed = line.trimStart();

              // Detect "run:" block start
              if (/^\s*run\s*:/.test(line)) {
                inRunBlock = true;
                runIndent = line.length - trimmed.length;
                // Check same line
                if (injectionRegex.test(line)) {
                  const exprMatch = line.match(/\$\{\{[^}]+\}\}/);
                  matches.push({
                    path: wf.replace(root + "/", ""),
                    lineNumber: i + 1,
                    line: line.trim().slice(0, 200),
                    expr: exprMatch?.[0] ?? "${{ github.event... }}",
                  });
                  if (!affectedFiles.includes(wf)) affectedFiles.push(wf);
                }
                continue;
              }

              // If in run block, check continuation lines
              if (inRunBlock) {
                const indent = line.length - trimmed.length;
                // If we hit a line with same or less indent and it's not empty/continuation
                if (trimmed.length > 0 && indent <= runIndent && !/^[|>]/.test(trimmed)) {
                  inRunBlock = false;
                } else if (injectionRegex.test(line)) {
                  const exprMatch = line.match(/\$\{\{[^}]+\}\}/);
                  matches.push({
                    path: wf.replace(root + "/", ""),
                    lineNumber: i + 1,
                    line: line.trim().slice(0, 200),
                    expr: exprMatch?.[0] ?? "${{ github.event... }}",
                  });
                  if (!affectedFiles.includes(wf)) affectedFiles.push(wf);
                }
              }
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "shell_injection",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    expression: m.expr,
                    snippet: m.line,
                    detail: `Potential shell injection via ${m.expr} in run step at ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-CI-005": {
          // Self-hosted runner with untrusted triggers
          const untrustedTriggers = new Set([
            "pull_request_target",
            "issue_comment",
            "workflow_run",
            "pull_request",
          ]);

          const matches: Array<{
            path: string;
            runnerLine: number;
            triggerLine: number;
            trigger: string;
          }> = [];
          const affectedFiles: string[] = [];

          for (const wf of workflowFiles) {
            const content = readFileContent(wf);
            if (!content) continue;

            const hasSelfHosted = /runs-on\s*:.*self-hosted/.test(content);
            if (!hasSelfHosted) continue;

            const lines = content.split("\n");
            let detectedTrigger = "";
            let triggerLine = -1;

            // Scan "on:" block for untrusted triggers
            for (let i = 0; i < lines.length; i++) {
              const line = lines[i]!;
              for (const trigger of untrustedTriggers) {
                if (new RegExp(`\\b${trigger}\\b`).test(line)) {
                  detectedTrigger = trigger;
                  triggerLine = i + 1;
                  break;
                }
              }
              if (detectedTrigger) break;
            }

            if (!detectedTrigger) continue;

            // Find runner line
            for (let i = 0; i < lines.length; i++) {
              if (/runs-on\s*:.*self-hosted/.test(lines[i]!)) {
                matches.push({
                  path: wf.replace(root + "/", ""),
                  runnerLine: i + 1,
                  triggerLine,
                  trigger: detectedTrigger,
                });
                if (!affectedFiles.includes(wf)) affectedFiles.push(wf);
                break;
              }
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "self_hosted_untrusted_trigger",
                  records: matches.map((m) => ({
                    path: m.path,
                    runner_line: m.runnerLine,
                    trigger_line: m.triggerLine,
                    trigger: m.trigger,
                    detail: `Self-hosted runner with untrusted trigger "${m.trigger}" in ${m.path}`,
                  })),
                },
                affectedFiles,
                matches.flatMap((m) => [m.runnerLine, m.triggerLine]),
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
        module_name: "ci_cd",
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
