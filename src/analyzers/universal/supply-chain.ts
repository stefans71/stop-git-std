import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeSupplyChain(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "supply-chain");
  const findings: Finding[] = [];

  // SC-001: Missing lockfile
  if (!profile.hasLockfile) {
    const rule = rules.find((r) => r.id === "SC-001");
    if (rule) {
      findings.push(createFinding(rule, [{ file: ".", context: "No lockfile found in repository root" }]));
    }
  }

  // SC-004: Vendored binaries
  const binaryRule = rules.find((r) => r.id === "SC-004");
  if (binaryRule?.pattern) {
    const binaryRegex = new RegExp(binaryRule.pattern);
    for (const file of profile.inventory.files) {
      if (binaryRegex.test(file)) {
        findings.push(createFinding(binaryRule, [{ file, snippet: file }]));
      }
    }
  }

  // Content-based rules: SC-002, SC-003 on package.json
  const pkgFiles = profile.inventory.files.filter((f) => f === "package.json" || f.endsWith("/package.json"));
  for (const file of pkgFiles) {
    const fullPath = join(profile.path, file);
    let content: string;
    try {
      content = await readFile(fullPath, "utf-8");
    } catch {
      continue;
    }

    const lines = content.split("\n");
    for (const rule of rules) {
      if (!rule.pattern || rule.filePattern || rule.id === "SC-001" || rule.id === "SC-004") continue;

      const regex = new RegExp(rule.pattern);
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
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
    category: "supply-chain",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.85,
    tags: ["universal", "supply-chain"],
  };
}
