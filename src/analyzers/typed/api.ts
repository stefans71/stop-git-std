import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeApi(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "api");
  const findings: Finding[] = [];

  const sourceFiles = profile.inventory.files.filter(
    (f) => f.endsWith(".ts") || f.endsWith(".js") || f.endsWith(".py"),
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

    // API-001: Missing authentication guard (heuristic: route without auth middleware)
    const authRule = rules.find((r) => r.id === "API-001");
    if (authRule) {
      const routePatterns = [
        /app\.(get|post|put|delete|patch)\s*\(/,
        /router\.(get|post|put|delete|patch)\s*\(/,
        /@(Get|Post|Put|Delete|Patch)\(/,
      ];

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        const isRoute = routePatterns.some((p) => p.test(line));
        if (isRoute) {
          // Check surrounding lines for auth middleware
          const context = lines.slice(Math.max(0, i - 3), i + 3).join("\n");
          const hasAuth = /auth|guard|protect|middleware|jwt|bearer|session/i.test(context);
          if (!hasAuth) {
            findings.push(
              createFinding(authRule, [
                { file, line: i + 1, snippet: line.trim().slice(0, 200) },
              ]),
            );
          }
        }
      }
    }

    // API-002: Permissive CORS
    const corsRule = rules.find((r) => r.id === "API-002");
    if (corsRule?.pattern) {
      const regex = new RegExp(corsRule.pattern, "i");
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i]!)) {
          findings.push(
            createFinding(corsRule, [
              { file, line: i + 1, snippet: lines[i]!.trim().slice(0, 200) },
            ]),
          );
        }
      }
    }

    // API-003: Missing request validation (heuristic: req.body without validation)
    const validationRule = rules.find((r) => r.id === "API-003");
    if (validationRule) {
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        if (/req\.body|request\.body|request\.json/i.test(line)) {
          const context = lines.slice(Math.max(0, i - 5), i + 5).join("\n");
          const hasValidation = /validate|schema|zod|joi|yup|ajv|class-validator/i.test(context);
          if (!hasValidation) {
            findings.push(
              createFinding(validationRule, [
                { file, line: i + 1, snippet: line.trim().slice(0, 200) },
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
    category: "api",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.7,
    tags: ["typed", "api"],
  };
}
