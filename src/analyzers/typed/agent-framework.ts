import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeAgentFramework(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "agent-framework");
  const findings: Finding[] = [];

  const sourceFiles = profile.inventory.files.filter(
    (f) => f.endsWith(".ts") || f.endsWith(".js") || f.endsWith(".py"),
  );

  // Collect capabilities across all files
  let hasShell = false;
  let hasFileWrite = false;
  let hasNetwork = false;
  let hasApprovalGate = false;
  let hasSharedState = false;
  let hasIsolation = false;
  const capabilityEvidence: Evidence[] = [];

  for (const file of sourceFiles) {
    const fullPath = join(profile.path, file);
    let content: string;
    try {
      content = await readFile(fullPath, "utf-8");
    } catch {
      continue;
    }

    if (/exec|spawn|shell|subprocess|child_process/i.test(content)) {
      hasShell = true;
      capabilityEvidence.push({ file, context: "Shell execution capability" });
    }
    if (/writeFile|fs\.write|open\(.*['"](w|a)['"]/i.test(content)) {
      hasFileWrite = true;
      capabilityEvidence.push({ file, context: "File write capability" });
    }
    if (/fetch|http|axios|request|urllib/i.test(content)) {
      hasNetwork = true;
      capabilityEvidence.push({ file, context: "Network capability" });
    }
    if (/approv|confirm|human.?in.?the.?loop|ask.?user|require.?permission/i.test(content)) {
      hasApprovalGate = true;
    }
    if (/shared.?state|global.?state|shared.?memory|common.?store/i.test(content)) {
      hasSharedState = true;
    }
    if (/isolat|sandbox|separate.?context|per.?agent/i.test(content)) {
      hasIsolation = true;
    }
  }

  // AGENT-001: Unrestricted tool capabilities
  const toolRule = rules.find((r) => r.id === "AGENT-001");
  if (toolRule && hasShell && hasFileWrite && hasNetwork && !hasApprovalGate) {
    findings.push(createFinding(toolRule, capabilityEvidence.slice(0, 3)));
  }

  // AGENT-002: Shared state without isolation
  const stateRule = rules.find((r) => r.id === "AGENT-002");
  if (stateRule && hasSharedState && !hasIsolation) {
    findings.push(
      createFinding(stateRule, [{ file: ".", context: "Shared state detected without isolation boundaries" }]),
    );
  }

  return findings;
}

function createFinding(rule: RuleDefinition, evidence: Evidence[]): Finding {
  return {
    id: `${rule.id}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    ruleId: rule.id,
    category: "agent-framework",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.75,
    tags: ["typed", "agent-framework"],
  };
}
