import type { Finding } from "../models/finding.ts";
import type { Scores } from "../models/scores.ts";
import type { Decision } from "../models/decision.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { PolicyProfile } from "../models/enums.ts";
import type { EngineContract, RuleCatalog, PolicyProfileConfig, ThresholdConfig } from "../rules/types.ts";

// ── Constraint generation ─────────────────────────────────────────────────────

function generateConstraints(findings: Finding[]): string[] {
  const constraints: string[] = [];
  const categories = new Set(findings.filter((f) => !f.suppressed).map((f) => f.category));

  if (categories.has("supply-chain")) {
    constraints.push("Pin all third-party dependencies to exact versions or commit SHAs.");
  }
  if (categories.has("privilege-escalation") || categories.has("credentials")) {
    constraints.push("Run in a read-only, network-isolated environment during evaluation.");
  }
  if (categories.has("exfiltration") || categories.has("network")) {
    constraints.push("Monitor outbound network connections during execution.");
  }
  if (categories.has("ci-cd") || categories.has("workflow")) {
    constraints.push("Review all CI/CD workflow changes before merging.");
  }
  if (categories.has("obfuscation")) {
    constraints.push("Perform manual code review of obfuscated sections before adoption.");
  }
  if (categories.has("runtime")) {
    constraints.push("Sandbox runtime execution and capture system call traces.");
  }

  return constraints;
}

// ── Threshold helpers ─────────────────────────────────────────────────────────

function activeFindings(findings: Finding[]): Finding[] {
  return findings.filter((f) => !f.suppressed);
}

function meetsThreshold(
  scores: Scores,
  findings: Finding[],
  threshold: ThresholdConfig,
  runtimeFindings: Finding[],
): boolean {
  if (threshold.disabled) return false;

  const active = activeFindings(findings);
  const criticalCount = active.filter((f) => f.severity === "critical").length;
  const highCount = active.filter((f) => f.severity === "high").length;
  const hasRuntimeFindings = runtimeFindings.length > 0;

  // abuse_potential threshold
  if (
    threshold.abuse_potential_gte !== undefined &&
    scores.abuse_potential >= threshold.abuse_potential_gte
  ) {
    return true;
  }
  // critical findings threshold (OR with abuse_potential)
  if (
    threshold.or_critical_findings_gte !== undefined &&
    criticalCount >= threshold.or_critical_findings_gte
  ) {
    return true;
  }
  // exploitability threshold
  if (
    threshold.exploitability_gte !== undefined &&
    scores.exploitability >= threshold.exploitability_gte
  ) {
    return true;
  }
  // high findings threshold (OR with exploitability)
  if (
    threshold.or_high_findings_gte !== undefined &&
    highCount >= threshold.or_high_findings_gte
  ) {
    return true;
  }
  // any runtime findings
  if (threshold.or_any_runtime_findings && hasRuntimeFindings) {
    return true;
  }

  return false;
}

// ── Main export ───────────────────────────────────────────────────────────────

/**
 * Evaluate findings and scores against the configured policy profile.
 *
 * Decision order:
 *   1. hard_stop   → ABORT (with hard_stop_triggered flag)
 *   2. abort threshold
 *   3. caution threshold
 *   4. proceed_with_constraints (any constrain_if_present findings)
 *   5. PROCEED
 */
export function evaluatePolicy(
  findings: Finding[],
  scores: Scores,
  context: AuditContext,
  policyProfile: PolicyProfile,
  contract: EngineContract,
  catalog: RuleCatalog,
): Decision {
  const profileConfig = contract.policy_profiles[policyProfile];
  if (!profileConfig) {
    throw new Error(`Unknown policy profile: ${policyProfile}`);
  }
  const hardStopPatterns: string[] = catalog.policy_baselines.hard_stop_patterns;

  const active = activeFindings(findings);
  const runtimeFindings = active.filter((f) => f.proof_type === "runtime");

  // ── 1. Hard stop ────────────────────────────────────────────────────────────
  const triggeredHardStop = active.filter((f) => hardStopPatterns.includes(f.id));
  if (triggeredHardStop.length > 0) {
    const reasons = triggeredHardStop.map(
      (f) => `Hard-stop rule triggered: ${f.id} — ${f.title}`,
    );
    // Respect hard_stop_behavior from the profile: "abort" → ABORT, "caution" → CAUTION
    const hardStopDecision = profileConfig.hard_stop_behavior === "caution" ? "CAUTION" : "ABORT";
    const constraints =
      hardStopDecision === "CAUTION" ? generateConstraints(active) : [];
    return {
      value: hardStopDecision,
      reasons,
      constraints,
      hard_stop_triggered: true,
      triggered_by_rules: triggeredHardStop.map((f) => f.id),
      manual_review_required: hardStopDecision === "ABORT",
    };
  }

  // ── 2. ABORT threshold ──────────────────────────────────────────────────────
  if (
    !profileConfig.thresholds.abort.disabled &&
    meetsThreshold(scores, findings, profileConfig.thresholds.abort, runtimeFindings)
  ) {
    return {
      value: "ABORT",
      reasons: [
        `Abort threshold exceeded: exploitability=${scores.exploitability}, abuse_potential=${scores.abuse_potential}`,
      ],
      constraints: [],
      hard_stop_triggered: false,
      manual_review_required: true,
    };
  }

  // ── 3. CAUTION threshold ────────────────────────────────────────────────────
  if (
    !profileConfig.thresholds.caution.disabled &&
    meetsThreshold(scores, findings, profileConfig.thresholds.caution, runtimeFindings)
  ) {
    const constraints = generateConstraints(active);
    return {
      value: "CAUTION",
      reasons: [
        `Caution threshold exceeded: exploitability=${scores.exploitability}, abuse_potential=${scores.abuse_potential}`,
      ],
      constraints,
      hard_stop_triggered: false,
      manual_review_required: false,
    };
  }

  // ── 4. PROCEED_WITH_CONSTRAINTS ─────────────────────────────────────────────
  const constrainFindings = active.filter((f) => {
    // Any finding from a rule that has constrain_if_present = true would qualify;
    // approximate by checking medium+ severity with non-low confidence
    return (
      ["medium", "high", "critical"].includes(f.severity) && f.confidence !== "low"
    );
  });

  if (
    !profileConfig.thresholds.proceed_with_constraints.disabled &&
    (constrainFindings.length > 0 ||
      meetsThreshold(
        scores,
        findings,
        profileConfig.thresholds.proceed_with_constraints,
        runtimeFindings,
      ))
  ) {
    const constraints = generateConstraints(active);
    if (constraints.length > 0) {
      return {
        value: "PROCEED_WITH_CONSTRAINTS",
        reasons: [
          `${constrainFindings.length} medium+ confidence finding(s) require mitigations before adoption.`,
        ],
        constraints,
        hard_stop_triggered: false,
        manual_review_required: false,
      };
    }
  }

  // ── 5. PROCEED ──────────────────────────────────────────────────────────────
  return {
    value: "PROCEED",
    reasons: ["No thresholds exceeded and no hard-stop rules triggered."],
    constraints: [],
    hard_stop_triggered: false,
    manual_review_required: false,
  };
}
