import { existsSync, readdirSync } from "fs";
import { join, extname, basename } from "path";
import { emitFinding, readFileContent, scanFileContent } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", "vendor"]);

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

function getDockerfiles(root: string, profileContainers: string[]): string[] {
  if (profileContainers.length > 0) {
    return profileContainers
      .map((c) => (c.startsWith("/") ? c : join(root, c)))
      .filter((c) => existsSync(c));
  }
  // Discover: files named Dockerfile, Dockerfile.*, *.dockerfile
  return walkFiles(root, 5).filter((f) => {
    const name = basename(f);
    return (
      name === "Dockerfile" ||
      name.startsWith("Dockerfile.") ||
      name.endsWith(".dockerfile") ||
      name.endsWith(".Dockerfile")
    );
  });
}

function getK8sFiles(root: string, profileInfra: string[]): string[] {
  const allYaml = (files: string[]) =>
    files.filter((f) => {
      const ext = extname(f).toLowerCase();
      return ext === ".yaml" || ext === ".yml";
    });

  if (profileInfra.length > 0) {
    return allYaml(
      profileInfra.map((i) => (i.startsWith("/") ? i : join(root, i))).filter((i) => existsSync(i)),
    );
  }

  // Heuristic discovery: k8s/, kubernetes/, deploy/, manifests/, helm/
  const k8sDirs = ["k8s", "kubernetes", "deploy", "manifests", "helm", "charts", "infra"];
  const results: string[] = [];
  for (const dir of k8sDirs) {
    const full = join(root, dir);
    if (existsSync(full)) {
      results.push(...allYaml(walkFiles(full, 5)));
    }
  }
  return results;
}

/**
 * Determine if a Dockerfile has a USER directive (excluding root/0).
 */
function dockerfileHasNonRootUser(content: string): boolean {
  const lines = content.split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    // Match USER <something other than root or 0>
    const m = trimmed.match(/^USER\s+(.+)$/i);
    if (m?.[1]) {
      const userVal = m[1].trim().toLowerCase();
      // USER root or USER 0 is not acceptable
      if (userVal !== "root" && userVal !== "0") {
        return true;
      }
    }
  }
  return false;
}

export const infrastructureAnalyzer: AnalyzerModule = {
  name: "infrastructure",

  async analyze(workspace, profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];
    const root = workspace.rootPath;

    const dockerfiles = getDockerfiles(root, profile.artifacts.containers);
    const k8sFiles = getK8sFiles(root, profile.artifacts.infra);

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-INFRA-001": {
          // Dockerfile missing USER directive (or USER root)
          const vulnerable: Array<{ path: string; detail: string }> = [];

          for (const df of dockerfiles) {
            const content = readFileContent(df);
            if (!content) continue;

            const hasUser = dockerfileHasNonRootUser(content);
            if (!hasUser) {
              vulnerable.push({
                path: df.replace(root + "/", ""),
                detail: `Dockerfile does not set a non-root USER — container runs as root`,
              });
            }
          }

          if (vulnerable.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "dockerfile_no_user",
                  records: vulnerable.map((v) => ({
                    path: v.path,
                    detail: v.detail,
                  })),
                },
                vulnerable.map((v) => join(root, v.path)),
              ),
            );
          }
          break;
        }

        case "GHA-INFRA-002": {
          // FROM with :latest or no tag
          const matches: Array<{ path: string; lineNumber: number; from: string }> = [];
          const affectedFiles: string[] = [];

          // Match FROM lines
          const fromRegex = /^FROM\s+(.+?)(\s+AS\s+\S+)?\s*$/i;

          for (const df of dockerfiles) {
            const content = readFileContent(df);
            if (!content) continue;
            const lines = content.split("\n");

            for (let i = 0; i < lines.length; i++) {
              const line = lines[i]!.trim();
              const m = line.match(fromRegex);
              if (!m?.[1]) continue;

              let image = m[1].trim();
              // Strip AS alias
              image = image.replace(/\s+AS\s+\S+$/i, "").trim();

              // Skip scratch / FROM scratch
              if (image.toLowerCase() === "scratch") continue;

              // Check for :latest or no tag at all
              const colonIdx = image.lastIndexOf(":");
              const slashIdx = image.lastIndexOf("/");
              const atIdx = image.indexOf("@"); // digest pin is fine

              if (atIdx !== -1) continue; // pinned by digest — OK

              if (colonIdx === -1 || colonIdx < slashIdx) {
                // No tag
                matches.push({
                  path: df.replace(root + "/", ""),
                  lineNumber: i + 1,
                  from: image,
                });
                if (!affectedFiles.includes(df)) affectedFiles.push(df);
              } else {
                const tag = image.slice(colonIdx + 1).trim().toLowerCase();
                if (tag === "latest" || tag === "") {
                  matches.push({
                    path: df.replace(root + "/", ""),
                    lineNumber: i + 1,
                    from: image,
                  });
                  if (!affectedFiles.includes(df)) affectedFiles.push(df);
                }
              }
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "dockerfile_latest_tag",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    image: m.from,
                    detail: `FROM image "${m.from}" uses :latest or has no tag at ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-INFRA-003": {
          // K8s RBAC wildcard permissions
          // Look for rules with verbs: ["*"] or resources: ["*"] or apiGroups: ["*"]
          const wildcardRegex = /["']\s*\*\s*["']/;

          const matches: Array<{
            path: string;
            lineNumber: number;
            line: string;
            field: string;
          }> = [];
          const affectedFiles: string[] = [];

          for (const k8sFile of k8sFiles) {
            const content = readFileContent(k8sFile);
            if (!content) continue;

            // Only process RBAC resources
            const isRbac =
              /kind\s*:\s*(ClusterRole|Role|ClusterRoleBinding|RoleBinding)\b/.test(content);
            if (!isRbac) continue;

            const lines = content.split("\n");
            for (let i = 0; i < lines.length; i++) {
              const line = lines[i]!;
              // Match verbs, resources, or apiGroups entries containing wildcard
              if (!wildcardRegex.test(line)) continue;

              let field = "unknown";
              if (/^\s*-?\s*verbs\s*:/i.test(line) || /verbs\s*:\s*\[/.test(line)) {
                field = "verbs";
              } else if (/^\s*-?\s*resources\s*:/i.test(line) || /resources\s*:\s*\[/.test(line)) {
                field = "resources";
              } else if (/^\s*-?\s*apiGroups\s*:/i.test(line) || /apiGroups\s*:\s*\[/.test(line)) {
                field = "apiGroups";
              } else if (wildcardRegex.test(line)) {
                // Catch inline list items - ["*"]
                field = "wildcard_entry";
              }

              // Also check simple "- '*'" pattern lines under verbs/resources blocks
              if (/^\s*-\s*["']?\*["']?\s*$/.test(line)) {
                // Look back to find context
                for (let j = i - 1; j >= Math.max(0, i - 5); j--) {
                  const prev = lines[j]!;
                  if (/^\s*verbs\s*:/.test(prev)) { field = "verbs"; break; }
                  if (/^\s*resources\s*:/.test(prev)) { field = "resources"; break; }
                  if (/^\s*apiGroups\s*:/.test(prev)) { field = "apiGroups"; break; }
                }
              }

              matches.push({
                path: k8sFile.replace(root + "/", ""),
                lineNumber: i + 1,
                line: line.trim().slice(0, 200),
                field,
              });
              if (!affectedFiles.includes(k8sFile)) affectedFiles.push(k8sFile);
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "k8s_rbac_wildcard",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    field: m.field,
                    snippet: m.line,
                    detail: `K8s RBAC wildcard "*" in ${m.field} at ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
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
        module_name: "infrastructure",
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
