import type { Scores } from "../models/scores.ts";
import type { Finding } from "../models/finding.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { ModuleResult } from "../models/module-result.ts";
import type { EngineContract } from "../rules/types.ts";
import type { Severity, Confidence } from "../models/enums.ts";

// ── Lookup tables ─────────────────────────────────────────────────────────────

export const SEVERITY_WEIGHTS = {
  info: 1,
  low: 2,
  medium: 4,
  high: 7,
  critical: 10,
} as const satisfies Record<Severity, number>;

export const CONFIDENCE_MULTIPLIERS = {
  low: 0.5,
  medium: 0.75,
  high: 1.0,
} as const satisfies Record<Confidence, number>;

export const ENVIRONMENT_ABUSE_MULTIPLIERS = {
  developer_laptop: 0.6,
  ci_runner: 1.0,
  container_isolated: 0.8,
  offline_analysis: 0.5,
  production_service: 1.5,
} as const satisfies Record<string, number>;

/** Trust credit values awarded from repo_profile signals (C1/C10). */
export const TRUST_CREDITS = {
  signed_tags_present: 8,
  security_md_present: 3,
  codeowners_present: 2,
  pinned_actions_ratio_high: 4,
} as const satisfies Record<string, number>;

// ── Confidence model (MVP) ────────────────────────────────────────────────────

function computeConfidence(
  findings: Finding[],
  moduleResults: ModuleResult[],
): Confidence {
  const total = moduleResults.length;
  if (total === 0) return "low";

  const failed = moduleResults.filter((m) => m.status === "failed").length;
  const failedRatio = failed / total;

  const universalSuccess = moduleResults
    .filter((m) => m.module_name.startsWith("universal"))
    .every((m) => m.status === "success" || m.status === "partial");

  const hasCriticalStatic = findings.some(
    (f) => f.severity === "critical" && f.proof_type === "static",
  );

  if (failedRatio <= 0.1 && (hasCriticalStatic || universalSuccess)) {
    return "high";
  }
  if (failedRatio <= 0.3) {
    return "medium";
  }
  return "low";
}

// ── Score computation ─────────────────────────────────────────────────────────

/**
 * Compute axis scores from findings using the formula:
 *   weighted_axis_value = axis_impact * severity_weight * confidence_multiplier / 10
 *
 * - Environment multiplier applied to abuse_potential ONLY.
 * - Trust credits from repo_profile subtracted from trustworthiness ONLY.
 * - All axes clamped to [0, 100].
 */
export function computeScores(
  findings: Finding[],
  profile: RepoProfile,
  context: AuditContext,
  moduleResults: ModuleResult[],
  contract: EngineContract,
): Scores {
  const envMultiplier =
    ENVIRONMENT_ABUSE_MULTIPLIERS[context.target_environment] ?? 1.0;

  // Accumulate raw axis totals from active (non-suppressed) findings
  let rawTrust = 0;
  let rawExploit = 0;
  let rawAbuse = 0;

  for (const f of findings) {
    if (f.suppressed) continue;

    const sw = SEVERITY_WEIGHTS[f.severity] ?? 1;
    const cm = CONFIDENCE_MULTIPLIERS[f.confidence] ?? 0.5;

    rawTrust += (f.axis_impacts.trustworthiness * sw * cm) / 10;
    rawExploit += (f.axis_impacts.exploitability * sw * cm) / 10;
    rawAbuse += (f.axis_impacts.abuse_potential * sw * cm) / 10;
  }

  // Apply environment multiplier to abuse_potential only
  rawAbuse *= envMultiplier;

  // Compute trust credits — subtracted from trustworthiness only
  // Credits are awarded only when the corresponding module completed (success or partial)
  const completedModules = new Set(
    moduleResults
      .filter((m) => m.status === "success" || m.status === "partial")
      .map((m) => m.module_name),
  );

  let trustCredit = 0;

  if (profile.signed_tags_count > 0 && completedModules.has("universal.governance-trust")) {
    trustCredit += TRUST_CREDITS.signed_tags_present;
  }
  if (profile.pinned_actions_ratio >= 0.8 && completedModules.has("universal.governance-trust")) {
    trustCredit += TRUST_CREDITS.pinned_actions_ratio_high;
  }
  // security_md and codeowners credits require the governance-trust module
  // Their presence is inferred from the profile's high_risk_files (absence of risk signals)
  // For now, check governance-trust module ran; actual file checks happen in the analyzer
  // These signals are surfaced via findings absence — grant credits when module ran with no
  // corresponding findings emitted
  const govModule = moduleResults.find((m) => m.module_name === "universal.governance-trust");
  if (govModule && (govModule.status === "success" || govModule.status === "partial")) {
    const hasSecurityMdFinding = findings.some(
      (f) => f.id === "SGS-GOV-001" && !f.suppressed,
    );
    const hasCodOwnersFinding = findings.some(
      (f) => f.id === "SGS-GOV-002" && !f.suppressed,
    );
    if (!hasSecurityMdFinding) trustCredit += TRUST_CREDITS.security_md_present;
    if (!hasCodOwnersFinding) trustCredit += TRUST_CREDITS.codeowners_present;
  }

  // Clamp to [0, 100]
  function clamp(val: number): number {
    return Math.max(0, Math.min(100, Math.round(val)));
  }

  const trustworthiness = clamp(rawTrust - trustCredit);
  const exploitability = clamp(rawExploit);
  const abuse_potential = clamp(rawAbuse);

  const confidence = computeConfidence(findings, moduleResults);

  return {
    trustworthiness,
    exploitability,
    abuse_potential,
    confidence,
    environment_multiplier_applied: envMultiplier,
    component_breakdown: {
      raw_trustworthiness: Math.round(rawTrust),
      raw_exploitability: Math.round(rawExploit),
      raw_abuse_potential: Math.round(rawAbuse / envMultiplier),
      trust_credit_applied: trustCredit,
    },
  };
}
