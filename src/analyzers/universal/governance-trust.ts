import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeGovernanceTrust(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "governance-trust");
  const findings: Finding[] = [];
  const fileSet = new Set(profile.inventory.files);

  // GOV-001: Missing SECURITY.md
  const securityRule = rules.find((r) => r.id === "GOV-001");
  if (securityRule) {
    const hasSecurityMd =
      fileSet.has("SECURITY.md") ||
      fileSet.has("security.md") ||
      fileSet.has(".github/SECURITY.md");
    if (!hasSecurityMd) {
      findings.push(createFinding(securityRule, [{ file: ".", context: "No SECURITY.md found" }]));
    }
  }

  // GOV-002: Missing CODEOWNERS
  const codeownersRule = rules.find((r) => r.id === "GOV-002");
  if (codeownersRule) {
    const hasCodeowners =
      fileSet.has("CODEOWNERS") ||
      fileSet.has(".github/CODEOWNERS") ||
      fileSet.has("docs/CODEOWNERS");
    if (!hasCodeowners) {
      findings.push(createFinding(codeownersRule, [{ file: ".", context: "No CODEOWNERS found" }]));
    }
  }

  // GOV-004: No signed releases (check for signed tags via git)
  // For MVP, check if there's any evidence of signing
  const signedRule = rules.find((r) => r.id === "GOV-004");
  if (signedRule) {
    // Heuristic: look for .asc, .sig files or mention of GPG/signing in CI
    const hasSigningEvidence = profile.inventory.files.some(
      (f) => f.endsWith(".asc") || f.endsWith(".sig"),
    );
    if (!hasSigningEvidence) {
      findings.push(
        createFinding(signedRule, [
          { file: ".", context: "No signed release artifacts found" },
        ]),
      );
    }
  }

  return findings;
}

function createFinding(rule: RuleDefinition, evidence: Evidence[]): Finding {
  return {
    id: `${rule.id}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    ruleId: rule.id,
    category: "governance-trust",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.9,
    tags: ["universal", "governance-trust"],
  };
}
