import { describe, expect, test } from "bun:test";
import { normalizeFindings } from "./normalize-findings.ts";
import type { Finding } from "../models/finding.ts";

function makeFinding(overrides: Partial<Finding> = {}): Finding {
  return {
    id: "test",
    ruleId: "TEST-001",
    category: "secrets",
    severity: "high",
    title: "Test",
    description: "Test",
    evidence: [{ file: "test.ts", line: 1, snippet: "test" }],
    confidence: 0.8,
    tags: [],
    ...overrides,
  };
}

describe("normalizeFindings", () => {
  test("deduplicates findings with same ruleId and location", () => {
    const findings = [
      makeFinding({ id: "a" }),
      makeFinding({ id: "b" }), // same ruleId, file, line — duplicate
    ];
    const result = normalizeFindings(findings);
    expect(result).toHaveLength(1);
  });

  test("keeps findings with different locations", () => {
    const findings = [
      makeFinding({ id: "a", evidence: [{ file: "a.ts", line: 1, snippet: "x" }] }),
      makeFinding({ id: "b", evidence: [{ file: "b.ts", line: 1, snippet: "x" }] }),
    ];
    const result = normalizeFindings(findings);
    expect(result).toHaveLength(2);
  });

  test("sorts by severity (critical first)", () => {
    const findings = [
      makeFinding({ id: "low", severity: "low", evidence: [{ file: "a.ts" }] }),
      makeFinding({ id: "crit", severity: "critical", evidence: [{ file: "b.ts" }] }),
      makeFinding({ id: "high", severity: "high", evidence: [{ file: "c.ts" }] }),
    ];
    const result = normalizeFindings(findings);
    expect(result[0]?.severity).toBe("critical");
    expect(result[1]?.severity).toBe("high");
    expect(result[2]?.severity).toBe("low");
  });
});
