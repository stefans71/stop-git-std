import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeSkillsPlugins(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "skills-plugins");
  const findings: Finding[] = [];

  // Look for manifest files
  const manifestFiles = profile.inventory.files.filter(
    (f) =>
      f.endsWith("manifest.json") ||
      f.endsWith("plugin.json") ||
      f.endsWith("skill.json") ||
      f.endsWith("extension.json"),
  );

  // SKILL-001: Broad manifest permissions
  const permRule = rules.find((r) => r.id === "SKILL-001");
  if (permRule) {
    for (const file of manifestFiles) {
      const fullPath = join(profile.path, file);
      let content: string;
      try {
        content = await readFile(fullPath, "utf-8");
      } catch {
        continue;
      }

      try {
        const manifest = JSON.parse(content) as Record<string, unknown>;
        const permissions = manifest.permissions as string[] | undefined;
        if (permissions) {
          const broadPermissions = permissions.filter(
            (p) => p === "*" || p === "all" || p.includes("admin") || p.includes("write"),
          );
          if (broadPermissions.length > 0) {
            findings.push(
              createFinding(permRule, [
                {
                  file,
                  snippet: `permissions: ${JSON.stringify(broadPermissions)}`,
                },
              ]),
            );
          }
        }
      } catch {
        // Invalid JSON
      }
    }
  }

  // SKILL-002: Instruction override
  const overrideRule = rules.find((r) => r.id === "SKILL-002");
  if (overrideRule) {
    const sourceFiles = profile.inventory.files.filter(
      (f) => f.endsWith(".ts") || f.endsWith(".js") || f.endsWith(".py") || f.endsWith(".md"),
    );

    for (const file of sourceFiles) {
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
        if (
          /ignore.*previous.*instructions|disregard.*system.*prompt|override.*safety|bypass.*guardrail/i.test(
            line,
          )
        ) {
          findings.push(
            createFinding(overrideRule, [
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
    category: "skills-plugins",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.7,
    tags: ["typed", "skills-plugins"],
  };
}
