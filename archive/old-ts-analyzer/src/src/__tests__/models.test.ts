import { test, expect, describe } from "bun:test";
import {
  AuditRequestSchema,
  FindingSchema,
  ScoresSchema,
  DecisionSchema,
} from "../models/index.ts";

describe("AuditRequestSchema", () => {
  test("accepts valid minimal input", () => {
    const result = AuditRequestSchema.safeParse({ repo_target: "https://github.com/org/repo" });
    expect(result.success).toBe(true);
  });

  test("accepts valid full input", () => {
    const result = AuditRequestSchema.safeParse({
      repo_target: "/local/path/to/repo",
      ref: "main",
      target_environment: "ci_runner",
      expected_permissions: ["read:packages"],
      runtime_mode: "install_only",
      adoption_mode: "internal",
      output_formats: ["json", "sarif"],
      enabled_modules: ["secrets"],
      disabled_modules: ["infrastructure"],
      include_paths: ["src/**"],
      exclude_paths: [".git/**"],
      allow_network_during_runtime: true,
      policy_profile: "strict",
      notes: "CI audit run",
    });
    expect(result.success).toBe(true);
  });

  test("rejects missing repo_target", () => {
    const result = AuditRequestSchema.safeParse({ ref: "main" });
    expect(result.success).toBe(false);
  });

  test("rejects empty repo_target string", () => {
    const result = AuditRequestSchema.safeParse({ repo_target: "" });
    expect(result.success).toBe(false);
  });
});

describe("FindingSchema", () => {
  const validFinding = {
    id: "GT-001",
    title: "Missing SECURITY.md",
    category: "governance_trust",
    severity: "medium",
    confidence: "high",
    proof_type: "static",
    axis_impacts: {
      trustworthiness: -10,
      exploitability: 0,
      abuse_potential: 0,
    },
    evidence: {
      type: "file_absence",
      records: [{ file: "SECURITY.md" }],
    },
    remediation: "Add a SECURITY.md file to the repository root.",
  };

  test("accepts a valid finding", () => {
    const result = FindingSchema.safeParse(validFinding);
    expect(result.success).toBe(true);
  });

  test("accepts finding with optional fields", () => {
    const result = FindingSchema.safeParse({
      ...validFinding,
      subcategory: "policy_files",
      module_name: "governance_trust",
      files: ["SECURITY.md"],
      line_numbers: [1],
      mapped_standards: ["SLSA L1"],
      tags: ["governance"],
      suppressed: false,
      suppression_reason: "",
    });
    expect(result.success).toBe(true);
  });

  test("rejects missing id", () => {
    const { id: _id, ...rest } = validFinding;
    const result = FindingSchema.safeParse(rest);
    expect(result.success).toBe(false);
  });

  test("rejects missing title", () => {
    const { title: _title, ...rest } = validFinding;
    const result = FindingSchema.safeParse(rest);
    expect(result.success).toBe(false);
  });

  test("rejects missing axis_impacts", () => {
    const { axis_impacts: _a, ...rest } = validFinding;
    const result = FindingSchema.safeParse(rest);
    expect(result.success).toBe(false);
  });

  test("rejects invalid severity value", () => {
    const result = FindingSchema.safeParse({ ...validFinding, severity: "extreme" });
    expect(result.success).toBe(false);
  });
});

describe("ScoresSchema", () => {
  test("accepts valid scores", () => {
    const result = ScoresSchema.safeParse({
      trustworthiness: 70,
      exploitability: 20,
      abuse_potential: 15,
      confidence: "medium",
    });
    expect(result.success).toBe(true);
  });

  test("accepts scores with optional fields", () => {
    const result = ScoresSchema.safeParse({
      trustworthiness: 100,
      exploitability: 0,
      abuse_potential: 0,
      confidence: "high",
      component_breakdown: { governance: 30 },
      environment_multiplier_applied: 1.2,
    });
    expect(result.success).toBe(true);
  });

  test("rejects trustworthiness below 0", () => {
    const result = ScoresSchema.safeParse({
      trustworthiness: -1,
      exploitability: 20,
      abuse_potential: 15,
      confidence: "medium",
    });
    expect(result.success).toBe(false);
  });

  test("rejects exploitability above 100", () => {
    const result = ScoresSchema.safeParse({
      trustworthiness: 70,
      exploitability: 101,
      abuse_potential: 15,
      confidence: "medium",
    });
    expect(result.success).toBe(false);
  });

  test("rejects abuse_potential above 100", () => {
    const result = ScoresSchema.safeParse({
      trustworthiness: 70,
      exploitability: 20,
      abuse_potential: 200,
      confidence: "medium",
    });
    expect(result.success).toBe(false);
  });

  test("rejects non-integer trustworthiness", () => {
    const result = ScoresSchema.safeParse({
      trustworthiness: 70.5,
      exploitability: 20,
      abuse_potential: 15,
      confidence: "medium",
    });
    expect(result.success).toBe(false);
  });
});

describe("DecisionSchema", () => {
  test("accepts valid PROCEED decision", () => {
    const result = DecisionSchema.safeParse({
      value: "PROCEED",
      reasons: ["All checks passed"],
      constraints: [],
    });
    expect(result.success).toBe(true);
  });

  test("accepts valid ABORT decision with optional fields", () => {
    const result = DecisionSchema.safeParse({
      value: "ABORT",
      reasons: ["Hard stop triggered: secret detected"],
      constraints: ["Remove exposed credentials"],
      hard_stop_triggered: true,
      triggered_by_rules: ["SC-003"],
      manual_review_required: false,
    });
    expect(result.success).toBe(true);
  });

  test("accepts PROCEED_WITH_CONSTRAINTS decision", () => {
    const result = DecisionSchema.safeParse({
      value: "PROCEED_WITH_CONSTRAINTS",
      reasons: ["Unpinned actions found"],
      constraints: ["Pin all GitHub Actions to SHA"],
    });
    expect(result.success).toBe(true);
  });

  test("accepts CAUTION decision", () => {
    const result = DecisionSchema.safeParse({
      value: "CAUTION",
      reasons: ["Elevated abuse potential"],
      constraints: [],
    });
    expect(result.success).toBe(true);
  });

  test("rejects invalid decision value", () => {
    const result = DecisionSchema.safeParse({
      value: "UNKNOWN",
      reasons: [],
      constraints: [],
    });
    expect(result.success).toBe(false);
  });

  test("rejects missing value field", () => {
    const result = DecisionSchema.safeParse({
      reasons: ["some reason"],
      constraints: [],
    });
    expect(result.success).toBe(false);
  });
});
