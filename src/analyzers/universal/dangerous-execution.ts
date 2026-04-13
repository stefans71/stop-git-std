import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeDangerousExecution(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "dangerous-execution");
  const findings: Finding[] = [];

  for (const file of profile.inventory.files) {
    for (const rule of rules) {
      if (!rule.pattern) continue;

      // Check fileGlob filter
      if (rule.fileGlob && !matchGlob(file, rule.fileGlob)) continue;

      const fullPath = join(profile.path, file);
      let content: string;
      try {
        content = await readFile(fullPath, "utf-8");
      } catch {
        continue;
      }

      const lines = content.split("\n");
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        const regex = new RegExp(rule.pattern, "i");
        if (regex.test(line)) {
          findings.push(
            createFinding(rule, [
              { file, line: i + 1, snippet: line.trim().slice(0, 200) },
            ]),
          );
        }
      }
    }
  }

  return findings;
}

function matchGlob(file: string, glob: string): boolean {
  // Simple glob matching for fileGlob patterns
  const pattern = glob
    .replace(/\./g, "\\.")
    .replace(/\*/g, ".*")
    .replace(/\?/g, ".");
  return new RegExp(`^${pattern}$`).test(file) || file.endsWith(glob.replace("*", ""));
}

function createFinding(rule: RuleDefinition, evidence: Evidence[]): Finding {
  return {
    id: `${rule.id}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    ruleId: rule.id,
    category: "dangerous-execution",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.85,
    tags: ["universal", "dangerous-execution"],
  };
}
