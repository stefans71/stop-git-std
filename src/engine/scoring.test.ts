import { describe, expect, test } from "bun:test";
import { scoreFindings } from "./scoring.ts";
import type { Finding } from "../models/finding.ts";

function makeFinding(overrides: Partial<Finding> = {}): Finding {
  return {
    id: "test",
    ruleId: "TEST-001",
    category: "secrets",
    severity: "high",
    title: "Test finding",
    description: "Test",
    evidence: [{ file: "test.ts" }],
    confidence: 0.8,
    tags: [],
    ...overrides,
  };
}

describe("scoreFindings", () => {
  test("returns zero scores for empty findings", () => {
    const result = scoreFindings([]);
    expect(result.overall.trustworthiness).toBe(100);
    expect(result.overall.exploitability).toBe(0);
    expect(result.overall.abuse_potential).toBe(0);
    expect(result.categories).toHaveLength(0);
  });

  test("critical findings produce high exploitability", () => {
    const findings = [
      makeFinding({ severity: "critical", confidence: 1.0 }),
      makeFinding({ severity: "critical", confidence: 1.0, id: "test2", ruleId: "TEST-002" }),
    ];
    const result = scoreFindings(findings);
    expect(result.overall.exploitability).toBeGreaterThan(50);
  });

  test("info findings produce minimal scores", () => {
    const findings = [makeFinding({ severity: "info", confidence: 0.5 })];
    const result = scoreFindings(findings);
    expect(result.overall.exploitability).toBe(0);
    expect(result.overall.trustworthiness).toBe(100);
  });

  test("groups findings by category", () => {
    const findings = [
      makeFinding({ category: "secrets" }),
      makeFinding({ category: "secrets", id: "test2" }),
      makeFinding({ category: "ci-cd", id: "test3" }),
    ];
    const result = scoreFindings(findings);
    expect(result.categories).toHaveLength(2);
    const secretsCat = result.categories.find((c) => c.category === "secrets");
    expect(secretsCat?.findingCount).toBe(2);
  });
});
