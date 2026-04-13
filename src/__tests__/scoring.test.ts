import { test, expect, describe } from "bun:test";
import {
  computeScores,
  SEVERITY_WEIGHTS,
  CONFIDENCE_MULTIPLIERS,
  ENVIRONMENT_ABUSE_MULTIPLIERS,
  TRUST_CREDITS,
} from "../engine/scoring.ts";
import type { Finding } from "../models/finding.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { ModuleResult } from "../models/module-result.ts";
import type { EngineContract } from "../rules/types.ts";

// ── Minimal mock helpers ──────────────────────────────────────────────────────

function makeFinding(overrides: Partial<Finding> = {}): Finding {
  return {
    id: "TEST-001",
    title: "Test finding",
    category: "supply-chain",
    severity: "low",
    confidence: "high",
    proof_type: "static",
    axis_impacts: { trustworthiness: 0, exploitability: 0, abuse_potential: 0 },
    evidence: { type: "file_match", records: [] },
    remediation: "Fix it",
    suppressed: false,
    suppression_reason: "",
    ...overrides,
  };
}

function makeProfile(overrides: Partial<RepoProfile> = {}): RepoProfile {
  return {
    languages: [],
    frameworks: [],
    ecosystems: [],
    detected_categories: [],
    artifacts: { manifests: [], workflows: [], containers: [], infra: [], binaries: [] },
    high_risk_files: [],
    signed_tags_count: 0,
    pinned_actions_ratio: 0,
    ...overrides,
  };
}

function makeContext(overrides: Partial<AuditContext> = {}): AuditContext {
  return {
    repo_target: "owner/repo",
    ref: "main",
    target_environment: "developer_laptop",
    expected_permissions: [],
    runtime_validation_enabled: false,
    ...overrides,
  };
}

function makeModuleResult(
  module_name: string,
  status: ModuleResult["status"] = "success",
): ModuleResult {
  return {
    module_name,
    status,
    started_at: "2024-01-01T00:00:00Z",
    completed_at: "2024-01-01T00:00:01Z",
    findings_emitted: 0,
    warnings: [],
    errors: [],
  };
}

/** Minimal EngineContract stub with only the required policy_profiles field. */
const minimalContract = {
  policy_profiles: {
    balanced: {
      hard_stop_behavior: "abort",
      thresholds: {
        abort: { abuse_potential_gte: 70, or_critical_findings_gte: 2 },
        caution: { exploitability_gte: 50, or_high_findings_gte: 4 },
        proceed_with_constraints: { abuse_potential_gte: 20 },
      },
    },
  },
} as unknown as EngineContract;

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("computeScores", () => {
  describe("Clean repo — no findings, all modules success", () => {
    test("trustworthiness is clamped to 0 after trust credits applied", () => {
      const moduleResults = [
        makeModuleResult("universal.governance-trust"),
        makeModuleResult("universal.ci-cd"),
      ];
      const scores = computeScores([], makeProfile(), makeContext(), moduleResults, minimalContract);

      // No findings → raw scores are 0; trust credits push trustworthiness negative → clamped to 0
      expect(scores.trustworthiness).toBe(0);
    });

    test("exploitability is 0", () => {
      const scores = computeScores([], makeProfile(), makeContext(), [], minimalContract);
      expect(scores.exploitability).toBe(0);
    });

    test("abuse_potential is 0", () => {
      const scores = computeScores([], makeProfile(), makeContext(), [], minimalContract);
      expect(scores.abuse_potential).toBe(0);
    });
  });

  describe("Single critical finding with high confidence and full axis impacts", () => {
    // severity_weight(critical) = 10, confidence_mult(high) = 1.0
    // axis_impact = 10 → weighted = 10 * 10 * 1.0 / 10 = 10

    const criticalFinding = makeFinding({
      severity: "critical",
      confidence: "high",
      axis_impacts: { trustworthiness: 10, exploitability: 10, abuse_potential: 10 },
    });

    test("trustworthiness score is > 0", () => {
      const scores = computeScores(
        [criticalFinding],
        makeProfile(),
        makeContext(),
        [],
        minimalContract,
      );
      expect(scores.trustworthiness).toBeGreaterThan(0);
    });

    test("exploitability score is > 0", () => {
      const scores = computeScores(
        [criticalFinding],
        makeProfile(),
        makeContext(),
        [],
        minimalContract,
      );
      expect(scores.exploitability).toBeGreaterThan(0);
    });

    test("abuse_potential score is > 0", () => {
      const scores = computeScores(
        [criticalFinding],
        makeProfile(),
        makeContext(),
        [],
        minimalContract,
      );
      expect(scores.abuse_potential).toBeGreaterThan(0);
    });

    test("formula: trustworthiness = round(axis_impact * severity_weight * confidence_mult / 10)", () => {
      const sw = SEVERITY_WEIGHTS.critical;
      const cm = CONFIDENCE_MULTIPLIERS.high;
      const expected = Math.max(0, Math.min(100, Math.round((10 * sw * cm) / 10)));

      const scores = computeScores(
        [criticalFinding],
        makeProfile(),
        makeContext(),
        [],
        minimalContract,
      );
      // trust credits may reduce the final value; raw_trustworthiness should match formula
      const raw = scores.component_breakdown as Record<string, number>;
      expect(raw.raw_trustworthiness).toBe(expected);
    });

    test("suppressed findings do not contribute to scores", () => {
      const suppressed = makeFinding({
        severity: "critical",
        confidence: "high",
        axis_impacts: { trustworthiness: 10, exploitability: 10, abuse_potential: 10 },
        suppressed: true,
      });
      const scores = computeScores([suppressed], makeProfile(), makeContext(), [], minimalContract);
      expect(scores.exploitability).toBe(0);
      expect(scores.abuse_potential).toBe(0);
    });
  });

  describe("Environment multiplier applies to abuse_potential ONLY", () => {
    const finding = makeFinding({
      severity: "critical",
      confidence: "high",
      axis_impacts: { trustworthiness: 5, exploitability: 5, abuse_potential: 5 },
    });

    test("offline_analysis reduces abuse_potential relative to developer_laptop", () => {
      const offlineScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "offline_analysis" }),
        [],
        minimalContract,
      );
      const laptopScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "developer_laptop" }),
        [],
        minimalContract,
      );
      // offline_analysis multiplier (0.5) < developer_laptop multiplier (0.6) — both below 1
      // abuse_potential for offline_analysis should be <= developer_laptop
      expect(offlineScores.abuse_potential).toBeLessThanOrEqual(laptopScores.abuse_potential);
    });

    test("ci_runner has higher abuse_potential than developer_laptop", () => {
      const ciScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "ci_runner" }),
        [],
        minimalContract,
      );
      const laptopScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "developer_laptop" }),
        [],
        minimalContract,
      );
      // ci_runner multiplier (1.0) > developer_laptop (0.6)
      expect(ciScores.abuse_potential).toBeGreaterThan(laptopScores.abuse_potential);
    });

    test("trustworthiness does not change between environments", () => {
      const offlineScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "offline_analysis" }),
        [],
        minimalContract,
      );
      const ciScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "ci_runner" }),
        [],
        minimalContract,
      );
      expect(offlineScores.trustworthiness).toBe(ciScores.trustworthiness);
    });

    test("exploitability does not change between environments", () => {
      const offlineScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "offline_analysis" }),
        [],
        minimalContract,
      );
      const ciScores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "ci_runner" }),
        [],
        minimalContract,
      );
      expect(offlineScores.exploitability).toBe(ciScores.exploitability);
    });

    test("environment_multiplier_applied is recorded in scores", () => {
      const scores = computeScores(
        [finding],
        makeProfile(),
        makeContext({ target_environment: "offline_analysis" }),
        [],
        minimalContract,
      );
      expect(scores.environment_multiplier_applied).toBe(
        ENVIRONMENT_ABUSE_MULTIPLIERS.offline_analysis,
      );
    });
  });

  describe("Trust credits reduce trustworthiness ONLY (C1/C10)", () => {
    // Use a finding with a real trustworthiness impact so we can see the reduction
    const finding = makeFinding({
      severity: "critical",
      confidence: "high",
      axis_impacts: { trustworthiness: 10, exploitability: 10, abuse_potential: 10 },
    });

    const govModule = makeModuleResult("universal.governance-trust");

    test("SECURITY.md credit reduces trustworthiness", () => {
      // No SGS-GOV-001 finding emitted → security_md_present credit is applied
      const withCreditModules = [govModule];
      const noCreditModules: ModuleResult[] = [];

      const withCredit = computeScores(
        [finding],
        makeProfile(),
        makeContext(),
        withCreditModules,
        minimalContract,
      );
      const noCredit = computeScores(
        [finding],
        makeProfile(),
        makeContext(),
        noCreditModules,
        minimalContract,
      );

      expect(withCredit.trustworthiness).toBeLessThanOrEqual(noCredit.trustworthiness);
    });

    test("signed_tags credit reduces trustworthiness", () => {
      const profile = makeProfile({ signed_tags_count: 3 });
      const moduleResults = [govModule];

      const withCredit = computeScores(
        [finding],
        profile,
        makeContext(),
        moduleResults,
        minimalContract,
      );
      const withoutCredit = computeScores(
        [finding],
        makeProfile({ signed_tags_count: 0 }),
        makeContext(),
        moduleResults,
        minimalContract,
      );

      expect(withCredit.trustworthiness).toBeLessThanOrEqual(withoutCredit.trustworthiness);
    });

    test("trust credits do NOT affect exploitability", () => {
      const profile = makeProfile({ signed_tags_count: 5, pinned_actions_ratio: 1.0 });
      const moduleResults = [govModule];

      const withCredit = computeScores([finding], profile, makeContext(), moduleResults, minimalContract);
      const noCredit = computeScores([finding], makeProfile(), makeContext(), [], minimalContract);

      expect(withCredit.exploitability).toBe(noCredit.exploitability);
    });

    test("trust credits do NOT affect abuse_potential", () => {
      const profile = makeProfile({ signed_tags_count: 5, pinned_actions_ratio: 1.0 });
      const moduleResults = [govModule];

      const withCredit = computeScores([finding], profile, makeContext(), moduleResults, minimalContract);
      const noCredit = computeScores([finding], makeProfile(), makeContext(), [], minimalContract);

      expect(withCredit.abuse_potential).toBe(noCredit.abuse_potential);
    });

    test("trust_credit_applied is tracked in component_breakdown", () => {
      const profile = makeProfile({ signed_tags_count: 3 });
      const scores = computeScores([finding], profile, makeContext(), [govModule], minimalContract);
      const bd = scores.component_breakdown as Record<string, number>;
      expect(bd.trust_credit_applied).toBeGreaterThan(0);
    });
  });

  describe("Confidence model based on failed module ratios", () => {
    test("all modules succeed → high confidence (with critical static finding)", () => {
      const criticalStaticFinding = makeFinding({
        severity: "critical",
        confidence: "high",
        proof_type: "static",
        axis_impacts: { trustworthiness: 5, exploitability: 5, abuse_potential: 5 },
      });
      const moduleResults = [
        makeModuleResult("universal.governance-trust", "success"),
        makeModuleResult("universal.ci-cd", "success"),
      ];
      const scores = computeScores(
        [criticalStaticFinding],
        makeProfile(),
        makeContext(),
        moduleResults,
        minimalContract,
      );
      expect(scores.confidence).toBe("high");
    });

    test("no modules → low confidence", () => {
      const scores = computeScores([], makeProfile(), makeContext(), [], minimalContract);
      expect(scores.confidence).toBe("low");
    });

    test("many failures (>30%) → low confidence", () => {
      const moduleResults = [
        makeModuleResult("universal.governance-trust", "failed"),
        makeModuleResult("universal.ci-cd", "failed"),
        makeModuleResult("universal.secrets", "failed"),
        makeModuleResult("typed.web", "success"),
      ];
      const scores = computeScores([], makeProfile(), makeContext(), moduleResults, minimalContract);
      expect(scores.confidence).toBe("low");
    });

    test("moderate failures (>10% ≤30%) → medium confidence", () => {
      const moduleResults = [
        makeModuleResult("universal.governance-trust", "success"),
        makeModuleResult("universal.ci-cd", "success"),
        makeModuleResult("universal.secrets", "success"),
        makeModuleResult("typed.web", "success"),
        makeModuleResult("typed.api", "success"),
        makeModuleResult("typed.mcp", "failed"),
        makeModuleResult("typed.agent", "success"),
        makeModuleResult("typed.lib", "success"),
        makeModuleResult("typed.infra", "success"),
        makeModuleResult("typed.skills", "failed"),
      ];
      // 2/10 = 20% failed → medium
      const scores = computeScores([], makeProfile(), makeContext(), moduleResults, minimalContract);
      expect(scores.confidence).toBe("medium");
    });
  });

  describe("Score clamping to [0, 100]", () => {
    test("scores cannot exceed 100", () => {
      // Stack many high-impact findings to push totals above 100
      const findings: Finding[] = Array.from({ length: 20 }, (_, i) =>
        makeFinding({
          id: `TEST-${i}`,
          severity: "critical",
          confidence: "high",
          axis_impacts: { trustworthiness: 10, exploitability: 10, abuse_potential: 10 },
        }),
      );
      const scores = computeScores(findings, makeProfile(), makeContext(), [], minimalContract);
      expect(scores.trustworthiness).toBeLessThanOrEqual(100);
      expect(scores.exploitability).toBeLessThanOrEqual(100);
      expect(scores.abuse_potential).toBeLessThanOrEqual(100);
    });

    test("scores cannot be negative", () => {
      const scores = computeScores([], makeProfile(), makeContext(), [], minimalContract);
      expect(scores.trustworthiness).toBeGreaterThanOrEqual(0);
      expect(scores.exploitability).toBeGreaterThanOrEqual(0);
      expect(scores.abuse_potential).toBeGreaterThanOrEqual(0);
    });
  });
});
