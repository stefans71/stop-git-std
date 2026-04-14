import { test, expect, describe } from "bun:test";
import { evaluatePolicy } from "../engine/policy.ts";
import type { Finding } from "../models/finding.ts";
import type { Scores } from "../models/scores.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { EngineContract, RuleCatalog } from "../rules/types.ts";

// ── Mock contract & catalog ───────────────────────────────────────────────────

const mockContract = {
  policy_profiles: {
    strict: {
      hard_stop_behavior: "abort",
      thresholds: {
        abort: { abuse_potential_gte: 50, or_critical_findings_gte: 1 },
        caution: { exploitability_gte: 30, or_high_findings_gte: 2 },
        proceed_with_constraints: { abuse_potential_gte: 10 },
      },
    },
    balanced: {
      hard_stop_behavior: "abort",
      thresholds: {
        abort: { abuse_potential_gte: 70, or_critical_findings_gte: 2 },
        caution: { exploitability_gte: 50, or_high_findings_gte: 4 },
        proceed_with_constraints: { abuse_potential_gte: 20 },
      },
    },
    advisory: {
      hard_stop_behavior: "caution",
      thresholds: {
        abort: { disabled: true },
        caution: { exploitability_gte: 80, or_high_findings_gte: 10 },
        proceed_with_constraints: { abuse_potential_gte: 30 },
      },
    },
  },
} as unknown as EngineContract;

const mockCatalog = {
  policy_baselines: {
    hard_stop_patterns: ["GHA-SECRETS-001", "GHA-EXEC-001", "GHA-MCP-001"],
  },
} as unknown as RuleCatalog;

// ── Mock helpers ──────────────────────────────────────────────────────────────

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

function makeScores(overrides: Partial<Scores> = {}): Scores {
  return {
    trustworthiness: 0,
    exploitability: 0,
    abuse_potential: 0,
    confidence: "high",
    ...overrides,
  };
}

const baseContext: AuditContext = {
  repo_target: "owner/repo",
  ref: "main",
  target_environment: "developer_laptop",
  expected_permissions: [],
  runtime_validation_enabled: false,
};

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("evaluatePolicy", () => {
  describe("Hard-stop triggers ABORT under balanced profile", () => {
    test("finding with hard-stop id → ABORT", () => {
      const finding = makeFinding({ id: "GHA-SECRETS-001", title: "Secrets exposed" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
    });

    test("hard_stop_triggered is true", () => {
      const finding = makeFinding({ id: "GHA-EXEC-001", title: "Exec issue" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.hard_stop_triggered).toBe(true);
    });

    test("triggered_by_rules contains the finding id", () => {
      const finding = makeFinding({ id: "GHA-MCP-001", title: "MCP issue" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.triggered_by_rules).toContain("GHA-MCP-001");
    });

    test("manual_review_required is true", () => {
      const finding = makeFinding({ id: "GHA-SECRETS-001", title: "Secrets exposed" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.manual_review_required).toBe(true);
    });

    test("suppressed hard-stop finding does not trigger ABORT", () => {
      const finding = makeFinding({
        id: "GHA-SECRETS-001",
        title: "Secrets exposed",
        suppressed: true,
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).not.toBe("ABORT");
    });
  });

  describe("No findings → PROCEED", () => {
    test("empty findings array produces PROCEED", () => {
      const decision = evaluatePolicy(
        [],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("PROCEED");
    });

    test("PROCEED has empty constraints", () => {
      const decision = evaluatePolicy(
        [],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.constraints).toHaveLength(0);
    });

    test("PROCEED has hard_stop_triggered false", () => {
      const decision = evaluatePolicy(
        [],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.hard_stop_triggered).toBe(false);
    });
  });

  describe("High exploitability → CAUTION", () => {
    test("exploitability >= balanced caution threshold (50) → CAUTION", () => {
      // balanced caution threshold: exploitability_gte: 50
      const scores = makeScores({ exploitability: 55 });
      const decision = evaluatePolicy(
        [],
        scores,
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("CAUTION");
    });

    test("exploitability below threshold → not CAUTION from threshold alone", () => {
      const scores = makeScores({ exploitability: 30 });
      const decision = evaluatePolicy(
        [],
        scores,
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      // Should be PROCEED since no findings with medium+ severity
      expect(decision.value).toBe("PROCEED");
    });

    test("CAUTION decision has reasons array", () => {
      const scores = makeScores({ exploitability: 55 });
      const decision = evaluatePolicy(
        [],
        scores,
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.reasons.length).toBeGreaterThan(0);
    });
  });

  describe("Advisory profile softens hard-stop to CAUTION", () => {
    test("hard-stop finding under advisory profile → CAUTION (not ABORT)", () => {
      const finding = makeFinding({ id: "GHA-SECRETS-001", title: "Secrets exposed" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "advisory",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("CAUTION");
    });

    test("advisory hard-stop still has hard_stop_triggered true", () => {
      const finding = makeFinding({ id: "GHA-EXEC-001", title: "Exec issue" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "advisory",
        mockContract,
        mockCatalog,
      );
      expect(decision.hard_stop_triggered).toBe(true);
    });

    test("advisory hard-stop does not require manual review", () => {
      const finding = makeFinding({ id: "GHA-MCP-001", title: "MCP issue" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "advisory",
        mockContract,
        mockCatalog,
      );
      expect(decision.manual_review_required).toBe(false);
    });

    test("same finding under strict profile → ABORT", () => {
      const finding = makeFinding({ id: "GHA-SECRETS-001", title: "Secrets exposed" });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "strict",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
    });
  });

  describe("CAUTION decisions include constraints", () => {
    test("CAUTION with supply-chain findings generates supply-chain constraint", () => {
      const scores = makeScores({ exploitability: 55 });
      const finding = makeFinding({ category: "supply-chain", severity: "high" });
      const decision = evaluatePolicy(
        [finding],
        scores,
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("CAUTION");
      expect(decision.constraints.some((c) => c.toLowerCase().includes("pin"))).toBe(true);
    });

    test("CAUTION with ci-cd findings generates workflow constraint", () => {
      const scores = makeScores({ exploitability: 55 });
      const finding = makeFinding({ category: "ci-cd", severity: "high" });
      const decision = evaluatePolicy(
        [finding],
        scores,
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("CAUTION");
      expect(decision.constraints.some((c) => c.toLowerCase().includes("ci"))).toBe(true);
    });

    test("advisory hard-stop CAUTION includes constraints from findings", () => {
      const finding = makeFinding({
        id: "GHA-SECRETS-001",
        title: "Secrets exposed",
        category: "credentials",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "advisory",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("CAUTION");
      expect(Array.isArray(decision.constraints)).toBe(true);
    });
  });

  describe("Confidence gate on hard-stop rules", () => {
    test("low-confidence hard-stop finding does NOT trigger ABORT", () => {
      const finding = makeFinding({
        id: "GHA-SECRETS-001",
        title: "Secrets exposed",
        confidence: "low",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).not.toBe("ABORT");
      expect(decision.hard_stop_triggered).toBeFalsy();
    });

    test("medium-confidence hard-stop finding DOES trigger ABORT", () => {
      const finding = makeFinding({
        id: "GHA-SECRETS-001",
        title: "Secrets exposed",
        confidence: "medium",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.hard_stop_triggered).toBe(true);
    });

    test("high-confidence hard-stop finding DOES trigger ABORT", () => {
      const finding = makeFinding({
        id: "GHA-EXEC-001",
        title: "Exec issue",
        confidence: "high",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.hard_stop_triggered).toBe(true);
    });
  });

  describe("ABORT decisions include constraints", () => {
    test("hard-stop ABORT includes non-empty constraints", () => {
      const finding = makeFinding({
        id: "GHA-EXEC-001",
        title: "Dangerous exec",
        category: "supply-chain",
        confidence: "high",
        remediation: "Pin the download URL and verify checksums.",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.constraints.length).toBeGreaterThan(0);
    });

    test("threshold ABORT includes constraints", () => {
      const finding = makeFinding({ category: "supply-chain" });
      const scores = makeScores({ abuse_potential: 90 });
      const decision = evaluatePolicy(
        [finding],
        scores,
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.constraints.length).toBeGreaterThan(0);
    });
  });

  describe("Unknown policy profile throws", () => {
    test("invalid profile name throws Error", () => {
      expect(() =>
        evaluatePolicy(
          [],
          makeScores(),
          baseContext,
          "nonexistent" as any,
          mockContract,
          mockCatalog,
        ),
      ).toThrow();
    });
  });
});
