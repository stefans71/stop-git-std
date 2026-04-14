import type { Scores } from "../models/scores.ts";
import type { Finding } from "../models/finding.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { ModuleResult } from "../models/module-result.ts";
import type { EngineContract } from "../rules/types.ts";
import type { Severity, Confidence } from "../models/enums.ts";

// ── Lookup tables ─────────────────────────────────────────────────────────────

export const SEVERITY_WEIGHTS: Record<string, number> = {
  info: 1,
  low: 3,
  medium: 8,
  high: 15,
  critical: 25,
};

export const CONFIDENCE_MULTIPLIERS: Record<string, number> = {
  low: 0.60,
  medium: 0.85,
  high: 1.00,
};

export const ENVIRONMENT_ABUSE_MULTIPLIERS: Record<string, number> = {
  developer_laptop: 1.25,
  ci_runner: 1.30,
  container_isolated: 0.80,
  offline_analysis: 0.20,
  production_service: 1.40,
};

/** Trust credit values awarded from repo_profile signals (C1/C10). */
export const TRUST_CREDITS = {
  signed_tags_present: 8,
  security_md_present: 3,
  codeowners_present: 2,
  pinned_actions_ratio_high: 4,
} as const satisfies Record<string, number>;

// ── Universal module names (CR6) ─────────────────────────────────────────────

const UNIVERSAL_MODULE_NAMES = [
  "governance_trust",
  "supply_chain",
  "secrets",
  "dangerous_execution",
  "ci_cd",
  "infrastructure",
];

// ── Confidence model (MVP) ────────────────────────────────────────────────────

function computeConfidence(
  findings: Finding[],
  moduleResults: ModuleResult[],
): Confidence {
  const total = moduleResults.length;
  if (total === 0) return "low";

  const failed = moduleResults.filter((m) => m.status === "failed").length;
  const failedRatio = failed / total;

  const universalModules = moduleResults.filter((m) =>
    UNIVERSAL_MODULE_NAMES.includes(m.module_name),
  );
  const universalSuccess =
    universalModules.length > 0 &&
    universalModules.every((m) => m.status === "success" || m.status === "partial");

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

  // Compute trust credits — subtracted from trustworthiness only (CR4: derive from repo_profile, NOT finding absence)
  // Credits are awarded only when the corresponding module completed (success or partial)
  const completedModules = new Set(
    moduleResults
      .filter((m) => m.status === "success" || m.status === "partial")
      .map((m) => m.module_name),
  );

  let trustCredit = 0;

  if (completedModules.has("governance_trust")) {
    // Signed tags: derive from repo_profile field directly
    if (profile.signed_tags_count > 0) {
      trustCredit += TRUST_CREDITS.signed_tags_present;
    }
    // Pinned actions ratio: derive from repo_profile field directly (threshold 0.9 per contract)
    if (profile.pinned_actions_ratio >= 0.9) {
      trustCredit += TRUST_CREDITS.pinned_actions_ratio_high;
    }
    // SECURITY.md: derive from repo_profile artifacts
    const hasSecurityMd = profile.artifacts?.manifests?.some(
      (m) => m.toLowerCase().includes("security.md"),
    );
    if (hasSecurityMd) {
      trustCredit += TRUST_CREDITS.security_md_present;
    }
    // CODEOWNERS: derive from repo_profile artifacts
    const hasCodeowners = profile.artifacts?.manifests?.some(
      (m) => m.toLowerCase().includes("codeowners"),
    );
    if (hasCodeowners) {
      trustCredit += TRUST_CREDITS.codeowners_present;
    }
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
