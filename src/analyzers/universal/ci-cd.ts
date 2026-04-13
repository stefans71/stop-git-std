import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeCiCd(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "ci-cd");
  const findings: Finding[] = [];

  // Only scan workflow files
  const workflowFiles = profile.inventory.files.filter(
    (f) => f.startsWith(".github/workflows/") && (f.endsWith(".yml") || f.endsWith(".yaml")),
  );

  for (const file of workflowFiles) {
    const fullPath = join(profile.path, file);
    let content: string;
    try {
      content = await readFile(fullPath, "utf-8");
    } catch {
      continue;
    }

    const lines = content.split("\n");
    for (const rule of rules) {
      if (!rule.pattern) continue;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        const regex = new RegExp(rule.pattern);
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

function createFinding(rule: RuleDefinition, evidence: Evidence[]): Finding {
  return {
    id: `${rule.id}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    ruleId: rule.id,
    category: "ci-cd",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.9,
    tags: ["universal", "ci-cd"],
  };
}
