import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";
import { parseDockerfile } from "../../parsers/dockerfile.ts";

export async function analyzeInfrastructure(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "infrastructure");
  const findings: Finding[] = [];

  // Dockerfile checks
  const dockerfiles = profile.inventory.files.filter(
    (f) => f === "Dockerfile" || f.startsWith("Dockerfile.") || f.endsWith("/Dockerfile"),
  );

  for (const file of dockerfiles) {
    const fullPath = join(profile.path, file);
    const parsed = await parseDockerfile(fullPath);
    if (!parsed) continue;

    // INFRA-001: Docker runs as root
    const rootRule = rules.find((r) => r.id === "INFRA-001");
    if (rootRule && !parsed.hasUserDirective) {
      findings.push(
        createFinding(rootRule, [{ file, context: "No USER directive found — container runs as root" }]),
      );
    }

    // INFRA-002: Latest tag base image
    const latestRule = rules.find((r) => r.id === "INFRA-002");
    if (latestRule) {
      for (const image of parsed.baseImages) {
        if (image.endsWith(":latest") || !image.includes(":")) {
          findings.push(
            createFinding(latestRule, [{ file, snippet: `FROM ${image}` }]),
          );
        }
      }
    }
  }

  // INFRA-003: Broad K8s RBAC
  const rbacRule = rules.find((r) => r.id === "INFRA-003");
  if (rbacRule) {
    const yamlFiles = profile.inventory.files.filter(
      (f) => (f.endsWith(".yaml") || f.endsWith(".yml")) && !f.startsWith(".github/"),
    );
    for (const file of yamlFiles) {
      const fullPath = join(profile.path, file);
      let content: string;
      try {
        content = await readFile(fullPath, "utf-8");
      } catch {
        continue;
      }

      if (rbacRule.pattern) {
        const regex = new RegExp(rbacRule.pattern);
        const lines = content.split("\n");
        for (let i = 0; i < lines.length; i++) {
          if (regex.test(lines[i]!)) {
            findings.push(
              createFinding(rbacRule, [
                { file, line: i + 1, snippet: lines[i]!.trim().slice(0, 200) },
              ]),
            );
          }
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
    category: "infrastructure",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.85,
    tags: ["universal", "infrastructure"],
  };
}
