import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import type { RuleCatalog } from "../../rules/load-rule-catalog.ts";

export async function analyzeLibraryPackage(
  profile: RepoProfile,
  _catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const findings: Finding[] = [];

  // Check package.json for library-specific concerns
  const pkgPath = join(profile.path, "package.json");
  let pkg: Record<string, unknown>;
  try {
    const content = await readFile(pkgPath, "utf-8");
    pkg = JSON.parse(content) as Record<string, unknown>;
  } catch {
    return findings;
  }

  // Check for postinstall scripts (common supply chain attack vector in libraries)
  const scripts = pkg.scripts as Record<string, string> | undefined;
  if (scripts) {
    const dangerousHooks = ["preinstall", "postinstall", "preuninstall"];
    for (const hook of dangerousHooks) {
      if (scripts[hook]) {
        findings.push({
          id: `LIB-HOOK-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
          ruleId: "LIB-001",
          category: "library-package",
          severity: "high",
          title: `Library has ${hook} lifecycle hook`,
          description: `Published library uses ${hook} script which runs on install`,
          evidence: [
            { file: "package.json", snippet: `"${hook}": "${scripts[hook]}"` },
          ],
          remediation: "Review hook contents for malicious behavior",
          confidence: 0.8,
          tags: ["typed", "library-package"],
        });
      }
    }
  }

  // Check if library is private but shouldn't be (or vice versa)
  if (!pkg.private && !pkg.main && !pkg.module && !pkg.exports && !pkg.bin) {
    findings.push({
      id: `LIB-ENTRY-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      ruleId: "LIB-002",
      category: "library-package",
      severity: "info",
      title: "Library missing entry points",
      description: "Package is not private but has no main/module/exports/bin fields",
      evidence: [{ file: "package.json", context: "No entry point fields found" }],
      remediation: "Add main, module, or exports field if publishing",
      confidence: 0.6,
      tags: ["typed", "library-package"],
    });
  }

  return findings;
}
