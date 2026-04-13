import type { Finding } from "../models/finding.ts";
import type { ScoringResult } from "../models/scores.ts";
import type { Decision, DecisionVerdict, Constraint } from "../models/decision.ts";

export function applyPolicy(scores: ScoringResult, findings: readonly Finding[]): Decision {
  const criticalFindings = findings.filter((f) => f.severity === "critical").length;
  const highFindings = findings.filter((f) => f.severity === "high").length;

  const { trustworthiness, exploitability, abuse_potential } = scores.overall;

  let verdict: DecisionVerdict;
  let reasoning: string;
  const constraints: Constraint[] = [];

  // Decision logic
  if (criticalFindings >= 3 || exploitability >= 80 || abuse_potential >= 80) {
    verdict = "ABORT";
    reasoning =
      criticalFindings >= 3
        ? `${criticalFindings} critical findings detected — repo poses unacceptable risk`
        : `Extreme risk scores (exploitability: ${exploitability}, abuse: ${abuse_potential})`;
  } else if (criticalFindings >= 1 || exploitability >= 60 || trustworthiness <= 30) {
    verdict = "CAUTION";
    reasoning = buildCautionReason(criticalFindings, exploitability, trustworthiness);

    if (criticalFindings > 0) {
      constraints.push({
        description: "All critical findings must be reviewed and mitigated before use",
        category: "critical-findings",
        severity: "required",
      });
    }
  } else if (highFindings >= 3 || exploitability >= 40 || trustworthiness <= 50) {
    verdict = "PROCEED_WITH_CONSTRAINTS";
    reasoning = `Moderate risk detected (${highFindings} high findings, trust: ${trustworthiness})`;

    if (highFindings > 0) {
      // Group constraints by category
      const highByCategory = new Map<string, number>();
      for (const f of findings.filter((f) => f.severity === "high")) {
        highByCategory.set(f.category, (highByCategory.get(f.category) ?? 0) + 1);
      }
      for (const [category, count] of highByCategory) {
        constraints.push({
          description: `Address ${count} high-severity finding(s) in ${category}`,
          category,
          severity: "recommended",
        });
      }
    }
  } else {
    verdict = "PROCEED";
    reasoning = `Low risk profile (trust: ${trustworthiness}, exploit: ${exploitability}, abuse: ${abuse_potential})`;
  }

  return {
    verdict,
    scores: scores.overall,
    constraints,
    reasoning,
    criticalFindings,
    highFindings,
  };
}

function buildCautionReason(
  critical: number,
  exploit: number,
  trust: number,
): string {
  const reasons: string[] = [];
  if (critical > 0) reasons.push(`${critical} critical finding(s)`);
  if (exploit >= 60) reasons.push(`high exploitability (${exploit})`);
  if (trust <= 30) reasons.push(`low trustworthiness (${trust})`);
  return `Significant risk: ${reasons.join(", ")}`;
}
