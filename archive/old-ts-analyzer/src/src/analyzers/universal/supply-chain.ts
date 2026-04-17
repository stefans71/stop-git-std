import { existsSync, readdirSync, statSync } from "fs";
import { join, extname } from "path";
import { emitFinding, readFileContent, scanFileContent } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

const LOCKFILE_MAP: Record<string, string[]> = {
  "package.json": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb"],
  "requirements.txt": ["requirements.txt.lock"],
  "Pipfile": ["Pipfile.lock"],
  "pyproject.toml": ["poetry.lock", "uv.lock"],
  "Gemfile": ["Gemfile.lock"],
  "Cargo.toml": ["Cargo.lock"],
  "go.mod": ["go.sum"],
  "composer.json": ["composer.lock"],
  "pubspec.yaml": ["pubspec.lock"],
};

const BINARY_EXTENSIONS = new Set([
  ".exe", ".dll", ".so", ".dylib", ".bin",
  ".o", ".a", ".lib", ".pyd", ".pyc",
]);

function walkFiles(dir: string, maxDepth = 4, depth = 0): string[] {
  if (depth > maxDepth) return [];
  const results: string[] = [];
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith(".") && entry.name !== ".github") continue;
      if (entry.name === "node_modules" || entry.name === ".git") continue;
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

export const supplyChainAnalyzer: AnalyzerModule = {
  name: "supply_chain",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];
    const root = workspace.rootPath;
    const warnings: string[] = [];

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-SUPPLY-001": {
          // Manifest without lockfile
          const missing: Array<{ manifest: string; expected_lockfiles: string[] }> = [];
          for (const [manifest, lockfiles] of Object.entries(LOCKFILE_MAP)) {
            const manifestPath = `${root}/${manifest}`;
            if (existsSync(manifestPath)) {
              const hasLock = lockfiles.some((lf) => existsSync(`${root}/${lf}`));
              if (!hasLock) {
                missing.push({ manifest, expected_lockfiles: lockfiles });
              }
            }
          }
          if (missing.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "missing_lockfile",
                  records: missing.map((m) => ({
                    manifest: m.manifest,
                    expected_lockfiles: m.expected_lockfiles,
                    detail: `${m.manifest} found but no lockfile present`,
                  })),
                },
                missing.map((m) => `${root}/${m.manifest}`),
              ),
            );
          }
          break;
        }

        case "GHA-SUPPLY-002": {
          // Floating version specs in package.json
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

          const floatingPattern = /^(\^|~|\*|latest|x|>=|>)/;
          const floatingEntries: Array<{ name: string; version: string; section: string }> = [];

          for (const section of ["dependencies", "devDependencies", "peerDependencies"]) {
            const deps = pkg[section] as Record<string, string> | undefined;
            if (!deps) continue;
            for (const [name, version] of Object.entries(deps)) {
              if (floatingPattern.test(String(version)) || version === "*" || version === "latest") {
                floatingEntries.push({ name, version: String(version), section });
              }
            }
          }

          if (floatingEntries.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "floating_versions",
                  records: floatingEntries.map((e) => ({
                    package: e.name,
                    version_spec: e.version,
                    section: e.section,
                    detail: `Floating version spec "${e.version}" for "${e.name}" in ${e.section}`,
                  })),
                },
                [pkgPath],
              ),
            );
          }
          break;
        }

        case "GHA-SUPPLY-003": {
          // Git/URL dependency sources in package.json
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

          const urlPattern = /^(git\+|github:|gitlab:|bitbucket:|https?:\/\/|git:\/\/|file:)/i;
          const urlDeps: Array<{ name: string; source: string; section: string }> = [];

          for (const section of ["dependencies", "devDependencies", "optionalDependencies"]) {
            const deps = pkg[section] as Record<string, string> | undefined;
            if (!deps) continue;
            for (const [name, version] of Object.entries(deps)) {
              if (urlPattern.test(String(version))) {
                urlDeps.push({ name, source: String(version), section });
              }
            }
          }

          if (urlDeps.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "git_url_dependency",
                  records: urlDeps.map((d) => ({
                    package: d.name,
                    source: d.source,
                    section: d.section,
                    detail: `Git/URL dependency source "${d.source}" for "${d.name}"`,
                  })),
                },
                [pkgPath],
              ),
            );
          }
          break;
        }

        case "GHA-SUPPLY-004": {
          // OSV lookup stub — not implemented, emit warning only
          warnings.push(
            "GHA-SUPPLY-004: OSV vulnerability lookup is not implemented in this version. " +
              "Integrate with https://api.osv.dev/v1/query for live CVE checks.",
          );
          break;
        }

        case "GHA-SUPPLY-005": {
          // Binary files by extension
          const allFiles = walkFiles(root, 5);
          const binaryFiles = allFiles.filter((f) => BINARY_EXTENSIONS.has(extname(f).toLowerCase()));

          if (binaryFiles.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "binary_files",
                  records: binaryFiles.slice(0, 50).map((f) => ({
                    path: f.replace(root + "/", ""),
                    extension: extname(f),
                    detail: `Binary file detected: ${f.replace(root + "/", "")}`,
                  })),
                },
                binaryFiles.slice(0, 50),
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
        module_name: "supply_chain",
        status: "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
        warnings,
        errors: [],
      },
    };
  },
};
