import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeAiLlm(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "ai-llm");
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

    // AI-001: Model output controls execution
    const execRule = rules.find((r) => r.id === "AI-001");
    if (execRule) {
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        // Detect LLM output being fed to exec/eval/shell
        if (
          /\b(completion|response|output|result|message|content)\b/i.test(line) &&
          /\b(exec|eval|spawn|shell|Function\(|subprocess)\b/i.test(line)
        ) {
          findings.push(
            createFinding(execRule, [
              { file, line: i + 1, snippet: line.trim().slice(0, 200) },
            ]),
          );
        }
      }
    }

    // AI-002: Secrets in prompts
    const secretsRule = rules.find((r) => r.id === "AI-002");
    if (secretsRule?.pattern) {
      const regex = new RegExp(secretsRule.pattern, "i");
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i]!)) {
          findings.push(
            createFinding(secretsRule, [
              { file, line: i + 1, snippet: lines[i]!.trim().slice(0, 200) },
            ]),
          );
        }
      }
    }

    // AI-003: Missing rate/budget controls
    const rateRule = rules.find((r) => r.id === "AI-003");
    if (rateRule) {
      const hasLlmCall =
        /openai|anthropic|chat\.completions|messages\.create|generate|invoke/i.test(content);
      if (hasLlmCall) {
        const hasRateLimit = /rate.?limit|throttl|budget|max.?tokens|max.?cost|limit/i.test(content);
        if (!hasRateLimit) {
          findings.push(
            createFinding(rateRule, [
              { file, context: "LLM API calls found without rate limiting or budget controls" },
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
    category: "ai-llm",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.7,
    tags: ["typed", "ai-llm"],
  };
}
