import { describe, expect, test } from "bun:test";
import { applyPolicy } from "./policy.ts";
import type { Finding } from "../models/finding.ts";
import type { ScoringResult } from "../models/scores.ts";

function makeFinding(severity: "critical" | "high" | "medium" | "low" | "info"): Finding {
  return {
    id: `test-${severity}`,
    ruleId: "TEST-001",
    category: "secrets",
    severity,
    title: "Test",
    description: "Test",
    evidence: [{ file: "test.ts" }],
    confidence: 0.8,
    tags: [],
  };
}

function makeScores(trust: number, exploit: number, abuse: number): ScoringResult {
  return {
    overall: { trustworthiness: trust, exploitability: exploit, abuse_potential: abuse },
    categories: [],
  };
}

describe("applyPolicy", () => {
  test("PROCEED for clean repo", () => {
    const decision = applyPolicy(makeScores(90, 10, 10), []);
    expect(decision.verdict).toBe("PROCEED");
  });

  test("ABORT for 3+ critical findings", () => {
    const findings = [makeFinding("critical"), makeFinding("critical"), makeFinding("critical")];
    const decision = applyPolicy(makeScores(20, 70, 70), findings);
    expect(decision.verdict).toBe("ABORT");
  });

  test("CAUTION for 1 critical finding", () => {
    const findings = [makeFinding("critical")];
    const decision = applyPolicy(makeScores(40, 50, 50), findings);
    expect(decision.verdict).toBe("CAUTION");
    expect(decision.constraints.length).toBeGreaterThan(0);
  });

  test("PROCEED_WITH_CONSTRAINTS for multiple high findings", () => {
    const findings = [makeFinding("high"), makeFinding("high"), makeFinding("high")];
    const decision = applyPolicy(makeScores(60, 30, 30), findings);
    expect(decision.verdict).toBe("PROCEED_WITH_CONSTRAINTS");
  });

  test("ABORT for extreme exploitability", () => {
    const decision = applyPolicy(makeScores(10, 85, 85), []);
    expect(decision.verdict).toBe("ABORT");
  });
});
