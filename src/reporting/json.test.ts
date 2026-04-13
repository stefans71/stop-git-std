import { describe, expect, test } from "bun:test";
import { renderJson } from "./json.ts";
import type { AuditResult } from "../engine/run-audit.ts";

function makeResult(): AuditResult {
  return {
    profile: {
      path: "/test/repo",
      name: "test-repo",
      types: ["api"],
      frameworks: [{ name: "express", confidence: 0.9 }],
      inventory: { totalFiles: 10, byExtension: new Map(), files: [] },
      languages: ["TypeScript"],
      hasLockfile: true,
      hasCiConfig: false,
      hasDockerfile: false,
      hasK8sConfig: false,
    },
    findings: [
      {
        id: "test-1",
        ruleId: "SEC-001",
        category: "secrets",
        severity: "critical",
        title: "Private key detected",
        description: "Test",
        evidence: [{ file: "key.pem", line: 1 }],
        confidence: 0.9,
        tags: ["secrets"],
      },
    ],
    scores: {
      overall: { trustworthiness: 50, exploitability: 60, abuse_potential: 40 },
      categories: [{ category: "secrets", score: 60, weight: 1, findingCount: 1 }],
    },
    decision: {
      verdict: "CAUTION",
      scores: { trustworthiness: 50, exploitability: 60, abuse_potential: 40 },
      constraints: [],
      reasoning: "Critical finding detected",
      criticalFindings: 1,
      highFindings: 0,
    },
  };
}

describe("renderJson", () => {
  test("produces valid JSON", () => {
    const output = renderJson(makeResult());
    const parsed = JSON.parse(output);
    expect(parsed).toBeDefined();
  });

  test("includes all top-level sections", () => {
    const output = renderJson(makeResult());
    const parsed = JSON.parse(output);
    expect(parsed.meta).toBeDefined();
    expect(parsed.repository).toBeDefined();
    expect(parsed.decision).toBeDefined();
    expect(parsed.scores).toBeDefined();
    expect(parsed.findings).toBeDefined();
    expect(parsed.summary).toBeDefined();
  });

  test("summary counts match findings", () => {
    const output = renderJson(makeResult());
    const parsed = JSON.parse(output);
    expect(parsed.summary.totalFindings).toBe(1);
    expect(parsed.summary.critical).toBe(1);
  });
});
