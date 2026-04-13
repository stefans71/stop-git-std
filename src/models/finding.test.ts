import { describe, expect, test } from "bun:test";
import type { Finding, Severity, FindingCategory } from "./finding.ts";

describe("Finding model", () => {
  test("should create a valid finding", () => {
    const finding: Finding = {
      id: "test-001",
      ruleId: "SEC-001",
      category: "secrets",
      severity: "critical",
      title: "Private key detected",
      description: "Private key found",
      evidence: [{ file: "test.pem", line: 1, snippet: "-----BEGIN RSA PRIVATE KEY-----" }],
      remediation: "Remove the key",
      confidence: 0.9,
      tags: ["secrets"],
    };

    expect(finding.id).toBe("test-001");
    expect(finding.severity).toBe("critical");
    expect(finding.evidence).toHaveLength(1);
  });

  test("severity type covers all expected values", () => {
    const severities: Severity[] = ["critical", "high", "medium", "low", "info"];
    expect(severities).toHaveLength(5);
  });

  test("category type covers all expected values", () => {
    const categories: FindingCategory[] = [
      "secrets", "dangerous-execution", "ci-cd", "supply-chain",
      "governance-trust", "infrastructure", "api", "ai-llm",
      "agent-framework", "mcp-server", "skills-plugins", "library-package",
    ];
    expect(categories).toHaveLength(12);
  });
});
