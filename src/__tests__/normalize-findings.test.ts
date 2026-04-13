import { test, expect, describe } from "bun:test";
import {
  deduplicateFindings,
  normalizeFindings,
  applySuppressions,
} from "../engine/normalize-findings.ts";
import type { Finding } from "../models/finding.ts";
import type { SuppressionEntry } from "../engine/normalize-findings.ts";

// ── Mock helpers ──────────────────────────────────────────────────────────────

function makeFinding(overrides: Partial<Finding> = {}): Finding {
  return {
    id: "TEST-001",
    title: "Test finding",
    category: "supply-chain",
    severity: "medium",
    confidence: "high",
    proof_type: "static",
    axis_impacts: { trustworthiness: 2, exploitability: 2, abuse_potential: 2 },
    evidence: { type: "file_match", records: [] },
    remediation: "Fix it",
    suppressed: false,
    suppression_reason: "",
    ...overrides,
  };
}

const HARD_STOP_PATTERNS = ["GHA-SECRETS-001", "GHA-EXEC-001", "GHA-MCP-001"];

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("deduplicateFindings", () => {
  describe("Deduplication: same id + files + evidence.type → merged", () => {
    test("two identical findings produce a single output finding", () => {
      const f1 = makeFinding({
        id: "DUP-001",
        files: ["src/foo.ts"],
        evidence: { type: "file_match", records: [{ line: 10 }] },
      });
      const f2 = makeFinding({
        id: "DUP-001",
        files: ["src/foo.ts"],
        evidence: { type: "file_match", records: [{ line: 20 }] },
      });
      const result = deduplicateFindings([f1, f2]);
      expect(result).toHaveLength(1);
    });

    test("merged finding has combined evidence records from both duplicates", () => {
      const f1 = makeFinding({
        id: "DUP-001",
        files: ["src/foo.ts"],
        evidence: { type: "file_match", records: [{ line: 10 }] },
      });
      const f2 = makeFinding({
        id: "DUP-001",
        files: ["src/foo.ts"],
        evidence: { type: "file_match", records: [{ line: 20 }] },
      });
      const result = deduplicateFindings([f1, f2]);
      expect(result[0]!.evidence.records).toHaveLength(2);
    });

    test("composite key uses sorted file order", () => {
      // ["b.ts", "a.ts"] and ["a.ts", "b.ts"] should produce the same key
      const f1 = makeFinding({
        id: "DUP-001",
        files: ["b.ts", "a.ts"],
        evidence: { type: "file_match", records: [{ hit: 1 }] },
      });
      const f2 = makeFinding({
        id: "DUP-001",
        files: ["a.ts", "b.ts"],
        evidence: { type: "file_match", records: [{ hit: 2 }] },
      });
      const result = deduplicateFindings([f1, f2]);
      expect(result).toHaveLength(1);
      expect(result[0]!.evidence.records).toHaveLength(2);
    });
  });

  describe("Different keys are NOT merged", () => {
    test("different ids → both kept", () => {
      const f1 = makeFinding({ id: "RULE-001", files: ["a.ts"], evidence: { type: "file_match", records: [] } });
      const f2 = makeFinding({ id: "RULE-002", files: ["a.ts"], evidence: { type: "file_match", records: [] } });
      const result = deduplicateFindings([f1, f2]);
      expect(result).toHaveLength(2);
    });

    test("same id but different files → both kept", () => {
      const f1 = makeFinding({ id: "RULE-001", files: ["a.ts"], evidence: { type: "file_match", records: [] } });
      const f2 = makeFinding({ id: "RULE-001", files: ["b.ts"], evidence: { type: "file_match", records: [] } });
      const result = deduplicateFindings([f1, f2]);
      expect(result).toHaveLength(2);
    });

    test("same id and files but different evidence type → both kept", () => {
      const f1 = makeFinding({ id: "RULE-001", files: ["a.ts"], evidence: { type: "file_match", records: [] } });
      const f2 = makeFinding({ id: "RULE-001", files: ["a.ts"], evidence: { type: "ast_node", records: [] } });
      const result = deduplicateFindings([f1, f2]);
      expect(result).toHaveLength(2);
    });

    test("unique findings are all preserved", () => {
      const findings = [
        makeFinding({ id: "A-001", files: ["x.ts"], evidence: { type: "file_match", records: [] } }),
        makeFinding({ id: "B-001", files: ["y.ts"], evidence: { type: "file_match", records: [] } }),
        makeFinding({ id: "C-001", files: ["z.ts"], evidence: { type: "ast_node", records: [] } }),
      ];
      const result = deduplicateFindings(findings);
      expect(result).toHaveLength(3);
    });
  });

  describe("normalizeFindings merges all finding arrays", () => {
    test("universal + typed findings are merged and deduplicated", () => {
      const universal = [makeFinding({ id: "U-001", files: ["a.ts"], evidence: { type: "file_match", records: [{ u: 1 }] } })];
      const typed = [makeFinding({ id: "U-001", files: ["a.ts"], evidence: { type: "file_match", records: [{ t: 2 }] } })];
      const result = normalizeFindings(universal, typed);
      expect(result).toHaveLength(1);
      expect(result[0]!.evidence.records).toHaveLength(2);
    });

    test("runtime findings are included", () => {
      const universal = [makeFinding({ id: "U-001" })];
      const typed: Finding[] = [];
      const runtime = [makeFinding({ id: "R-001", proof_type: "runtime" })];
      const result = normalizeFindings(universal, typed, runtime);
      expect(result).toHaveLength(2);
    });
  });
});

describe("applySuppressions", () => {
  describe("Suppression applied to matching finding", () => {
    test("matching suppression marks finding as suppressed", () => {
      const finding = makeFinding({ id: "RULE-001" });
      const suppression: SuppressionEntry = {
        rule_id: "RULE-001",
        justification: "False positive in test fixtures",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(true);
    });

    test("suppression_reason is set to justification text", () => {
      const finding = makeFinding({ id: "RULE-001" });
      const suppression: SuppressionEntry = {
        rule_id: "RULE-001",
        justification: "Known safe pattern",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppression_reason).toBe("Known safe pattern");
    });

    test("non-matching suppression leaves finding unsuppressed", () => {
      const finding = makeFinding({ id: "RULE-001" });
      const suppression: SuppressionEntry = {
        rule_id: "RULE-999",
        justification: "Different rule",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(false);
    });

    test("path_globs filter: matching file path → suppressed", () => {
      const finding = makeFinding({
        id: "RULE-001",
        files: ["src/fixtures/test-secrets.ts"],
      });
      const suppression: SuppressionEntry = {
        rule_id: "RULE-001",
        path_globs: ["src/fixtures/**"],
        justification: "Test fixtures only",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(true);
    });

    test("path_globs filter: non-matching file path → NOT suppressed", () => {
      const finding = makeFinding({
        id: "RULE-001",
        files: ["src/production/secrets.ts"],
      });
      const suppression: SuppressionEntry = {
        rule_id: "RULE-001",
        path_globs: ["src/fixtures/**"],
        justification: "Test fixtures only",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(false);
    });
  });

  describe("Hard-stop suppression rejected without override fields (C3)", () => {
    test("hard-stop finding without override fields is NOT suppressed", () => {
      const finding = makeFinding({ id: "GHA-SECRETS-001" });
      const suppression: SuppressionEntry = {
        rule_id: "GHA-SECRETS-001",
        justification: "Attempting suppression without override",
        // override_reason, reviewer_identity, reviewed_commit_sha deliberately omitted
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(false);
    });

    test("hard-stop finding with only partial override fields is NOT suppressed", () => {
      const finding = makeFinding({ id: "GHA-EXEC-001" });
      const suppression: SuppressionEntry = {
        rule_id: "GHA-EXEC-001",
        justification: "Partial override attempt",
        override_reason: "Security team approved",
        // reviewer_identity and reviewed_commit_sha missing
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(false);
    });

    test("non-hard-stop finding suppressed without override fields (allowed)", () => {
      const finding = makeFinding({ id: "SAFE-RULE-001" });
      const suppression: SuppressionEntry = {
        rule_id: "SAFE-RULE-001",
        justification: "Normal suppression no override required",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(true);
    });
  });

  describe("Hard-stop suppression accepted with all override fields", () => {
    test("hard-stop finding WITH all three override fields IS suppressed", () => {
      const finding = makeFinding({ id: "GHA-SECRETS-001" });
      const suppression: SuppressionEntry = {
        rule_id: "GHA-SECRETS-001",
        justification: "Reviewed and approved by security team",
        override_reason: "Secret is a non-sensitive placeholder used in tests",
        reviewer_identity: "security-lead@example.com",
        reviewed_commit_sha: "abc123def456",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppressed).toBe(true);
    });

    test("hard-stop finding with override: suppression_reason is set", () => {
      const finding = makeFinding({ id: "GHA-MCP-001" });
      const suppression: SuppressionEntry = {
        rule_id: "GHA-MCP-001",
        justification: "Approved MCP suppression",
        override_reason: "Not an MCP server in this context",
        reviewer_identity: "lead@example.com",
        reviewed_commit_sha: "deadbeef",
      };
      const result = applySuppressions([finding], [suppression], HARD_STOP_PATTERNS);
      expect(result[0]!.suppression_reason).toBe("Approved MCP suppression");
    });

    test("multiple findings: hard-stop with override suppressed, without override not suppressed", () => {
      const hardStop1 = makeFinding({ id: "GHA-SECRETS-001", title: "With override" });
      const hardStop2 = makeFinding({ id: "GHA-EXEC-001", title: "Without override" });

      const suppressions: SuppressionEntry[] = [
        {
          rule_id: "GHA-SECRETS-001",
          justification: "Full override provided",
          override_reason: "Reviewed",
          reviewer_identity: "reviewer@example.com",
          reviewed_commit_sha: "cafebabe",
        },
        {
          rule_id: "GHA-EXEC-001",
          justification: "Missing override fields",
          // no override fields
        },
      ];

      const result = applySuppressions([hardStop1, hardStop2], suppressions, HARD_STOP_PATTERNS);
      expect(result.find((f) => f.id === "GHA-SECRETS-001")!.suppressed).toBe(true);
      expect(result.find((f) => f.id === "GHA-EXEC-001")!.suppressed).toBe(false);
    });
  });
});
