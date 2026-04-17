### C1: Confidence Semantics (Preserve on Confirm/Ambiguous)
**File:** src/stage2/ast-refiner.ts

BEFORE (lines 67-75):
```ts
    if (classifications.every((c) => c === "dismiss")) {
      finding.suppressed = true;
      finding.suppression_reason =
        "AST analysis: all matches are in non-executable context (string literals, comments, type names)";
    } else if (classifications.some((c) => c === "confirm")) {
      finding.confidence = "high";
    } else {
      // All ambiguous or mix of dismiss+ambiguous
      finding.confidence = "low";
    }
```

AFTER:
```ts
    if (classifications.every((c) => c === "dismiss")) {
      finding.suppressed = true;
      finding.suppression_reason =
        "AST analysis: all matches are in non-executable context (string literals, comments, type names)";
      summary.suppressed_findings += 1;
    } else {
      // Confirm/ambiguous preserve original confidence.
      if (classifications.some((c) => c === "confirm")) summary.confirmed_findings += 1;
      if (classifications.some((c) => c === "ambiguous")) summary.ambiguous_findings += 1;
    }
```

NOTES: This block is shared with C6 (summary). Apply the C6 version of the block (below) if you want to avoid duplicate edits.

---

### C2: Engine Contract — Add Phase 8.5 + Depth Mode + Result Fields
**File:** docs/engine-contract.yaml

BEFORE (lines 113-175):
```yaml
      runtime_mode:
        type: string
        enum_ref: runtime_modes
        default: off
      adoption_mode:
        type: string
        allowed_values:
          - third_party
          - internal
          - fork_review
          - pre_merge
        default: third_party
      output_formats:
        type: array
        items:
          type: string
          allowed_values:
            - json
            - yaml
            - markdown
            - sarif
        default:
          - json
          - markdown
```

AFTER:
```yaml
      runtime_mode:
        type: string
        enum_ref: runtime_modes
        default: off
      depth_mode:
        type: string
        allowed_values:
          - auto
          - quick
          - deep
        default: auto
      adoption_mode:
        type: string
        allowed_values:
          - third_party
          - internal
          - fork_review
          - pre_merge
        default: third_party
      output_formats:
        type: array
        items:
          type: string
          allowed_values:
            - json
            - yaml
            - markdown
            - sarif
        default:
          - json
          - markdown
```

BEFORE (lines 469-495):
```yaml
  decision:
    type: object
    required:
      - value
      - reasons
      - constraints
    properties:
      value:
        type: string
        enum_ref: decision_values
      reasons:
        type: array
        items:
          type: string
      constraints:
        type: array
        items:
          type: string
      hard_stop_triggered:
        type: boolean
      triggered_by_rules:
        type: array
        items:
          type: string
      manual_review_required:
        type: boolean
```

AFTER:
```yaml
  decision:
    type: object
    required:
      - value
      - reasons
      - constraints
    properties:
      value:
        type: string
        enum_ref: decision_values
      reasons:
        type: array
        items:
          type: string
      constraints:
        type: array
        items:
          type: string
      hard_stop_triggered:
        type: boolean
      triggered_by_rules:
        type: array
        items:
          type: string
      manual_review_required:
        type: boolean

  audit_result:
    type: object
    required:
      - manifest
      - context
      - profile
      - findings
      - scores
      - decision
      - module_results
      - coverage
      - reports
    properties:
      manifest:
        type: object
      context:
        type: object
      profile:
        type: object
      findings:
        type: array
        items:
          type: object
      scores:
        type: object
      decision:
        type: object
      module_results:
        type: array
        items:
          type: object
      coverage:
        type: object
      reports:
        type: object
      stage2_recommended:
        type: boolean
      stage2_triggers:
        type: array
        items:
          type: object
          required:
            - finding_id
            - reason
            - recommended_module
          properties:
            finding_id:
              type: string
            reason:
              type: string
            recommended_module:
              type: string
              allowed_values:
                - ast
                - sandbox
                - manual_review
      ast_refinement_summary:
        type: object
        properties:
          findings_considered:
            type: integer
          findings_refined:
            type: integer
          findings_skipped:
            type: integer
          suppressed_findings:
            type: integer
          confirmed_findings:
            type: integer
          ambiguous_findings:
            type: integer
          error_count:
            type: integer
          skips:
            type: array
            items:
              type: object
              required:
                - finding_id
                - reason
              properties:
                finding_id:
                  type: string
                reason:
                  type: string
```

BEFORE (lines 496-507):
```yaml
phase_order:
  - context_capture
  - repository_acquisition
  - inventory_classification
  - module_routing
  - universal_analysis
  - typed_analysis
  - runtime_validation
  - finding_normalization
  - scoring
  - policy_decision
  - reporting
```

AFTER:
```yaml
phase_order:
  - context_capture
  - repository_acquisition
  - inventory_classification
  - module_routing
  - universal_analysis
  - typed_analysis
  - runtime_validation
  - finding_normalization
  - ast_refinement
  - scoring
  - policy_decision
  - reporting
```

BEFORE (lines 632-689):
```yaml
  finding_normalization:
    description: Merge, dedupe, and normalize all findings.
    inputs:
      - universal_findings
      - typed_findings
      - runtime_findings
    outputs:
      - normalized_findings
    required: true
    actions:
      - merge_findings
      - deduplicate_by_rule_and_evidence
      - attach_module_names
      - attach_default_mappings
      - apply_suppressions

  scoring:
    description: Compute axis scores and confidence.
    inputs:
      - normalized_findings
      - repo_profile
      - audit_context
      - module_results
    outputs:
      - scores
    required: true
```

AFTER:
```yaml
  finding_normalization:
    description: Merge, dedupe, and normalize all findings.
    inputs:
      - universal_findings
      - typed_findings
      - runtime_findings
    outputs:
      - normalized_findings
    required: true
    actions:
      - merge_findings
      - deduplicate_by_rule_and_evidence
      - attach_module_names
      - attach_default_mappings
      - apply_suppressions

  ast_refinement:
    description: Validate regex findings with AST and refine suppression/confidence.
    inputs:
      - normalized_findings
      - local_workspace
      - audit_request
    outputs:
      - refined_findings
      - ast_refinement_summary
    required: false
    skip_if:
      any:
        - audit_request.depth_mode == quick
    actions:
      - load_language_parsers
      - classify_match_context
      - suppress_non_executable_matches
      - emit_refinement_summary

  scoring:
    description: Compute axis scores and confidence.
    inputs:
      - refined_findings
      - repo_profile
      - audit_context
      - module_results
    outputs:
      - scores
    required: true
```

BEFORE (lines 665-689):
```yaml
  policy_decision:
    description: Convert findings and scores into final decision.
    inputs:
      - normalized_findings
      - scores
      - audit_context
    outputs:
      - decision
    required: true
    actions:
      - check_hard_stop_rules
      - evaluate_score_thresholds
      - generate_constraints
      - compose_reasons

  reporting:
    description: Generate requested report formats.
    inputs:
      - run_manifest
      - audit_context
      - repo_profile
      - normalized_findings
      - scores
      - decision
      - module_results
    outputs:
      - report_bundle
    required: true
```

AFTER:
```yaml
  policy_decision:
    description: Convert findings and scores into final decision.
    inputs:
      - refined_findings
      - scores
      - audit_context
    outputs:
      - decision
    required: true
    actions:
      - check_hard_stop_rules
      - evaluate_score_thresholds
      - generate_constraints
      - compose_reasons

  reporting:
    description: Generate requested report formats.
    inputs:
      - run_manifest
      - audit_context
      - repo_profile
      - refined_findings
      - scores
      - decision
      - module_results
    outputs:
      - report_bundle
    required: true
```

NOTES: `audit_result` properties are intentionally shallow (object/array) to avoid duplicating the full nested schemas; this is consistent with how the contract currently references artifacts.

---

### C3: Finding-to-Evidence Indexing (Use Evidence Records)
**File:** src/stage2/ast-refiner.ts

BEFORE (lines 27-63):
```ts
  for (const finding of toRefine) {
    const files = finding.files;
    const lineNumbers = finding.line_numbers;

    if (!files || files.length === 0) continue;

    const classifications: AstClassification[] = [];

    for (let i = 0; i < files.length; i++) {
      const rawPath = files[i]!;
      const filePath = isAbsolute(rawPath) ? rawPath : join(workspace.rootPath, rawPath);
      const lineNumber = lineNumbers?.[i];
      if (!lineNumber) continue;

      const parser = await getParserForFile(filePath);
      if (!parser) continue; // unsupported language — skip

      const content = readFileContent(filePath);
      if (!content) continue;

      // Extract match text from the corresponding evidence record for this file
      let matchText = "";
      const rec = finding.evidence.records[i] as Record<string, unknown> | undefined;
      if (rec && typeof rec.match === "string") {
        matchText = rec.match;
      }

      try {
        const result = classifyMatchContext(parser, content, lineNumber, matchText);
        classifications.push(result.classification);
      } catch (err) {
        console.warn(`[ast-refiner] Classification failed for ${rawPath}:${lineNumber}: ${err}`);
        classifications.push("ambiguous");
      } finally {
        parser.delete();
      }
    }
```

AFTER:
```ts
  for (const finding of toRefine) {
    if (!finding.line_numbers || finding.line_numbers.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "missing line_numbers" });
      continue;
    }

    const records = finding.evidence.records as Array<Record<string, unknown>>;
    if (!records || records.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "no evidence records" });
      continue;
    }

    const classifications: AstClassification[] = [];

    for (const rec of records) {
      const rawPath = typeof rec.path === "string"
        ? rec.path
        : typeof rec.file === "string"
          ? rec.file
          : typeof rec.file_path === "string"
            ? rec.file_path
            : undefined;
      const lineNumber = typeof rec.line_number === "number" ? rec.line_number : undefined;
      if (!rawPath || !lineNumber) continue;

      const filePath = isAbsolute(rawPath) ? rawPath : join(workspace.rootPath, rawPath);

      const parser = await getParserForFile(filePath);
      if (!parser) continue; // unsupported language — skip

      const content = readFileContent(filePath);
      if (!content) continue;

      let matchText = "";
      if (typeof rec.match === "string") {
        matchText = rec.match;
      }

      try {
        const result = classifyMatchContext(parser, content, lineNumber, matchText);
        classifications.push(result.classification);
      } catch (err) {
        console.warn(`[ast-refiner] Classification failed for ${rawPath}:${lineNumber}: ${err}`);
        summary.error_count += 1;
        classifications.push("ambiguous");
      } finally {
        parser.delete();
      }
    }
```

NOTES: This block is also updated by C5 (line_numbers guard) and C6 (summary). Apply C3/C5/C6 together to avoid conflicting edits.

---

### C4: STAGE2_MODULE_MAP Coverage Assertion
**File:** src/__tests__/run-audit-stage2.test.ts

BEFORE (lines 1-47):
```ts
import { test, expect, describe } from "bun:test";

/**
 * Tests for Phase 8.5 integration in run-audit.ts.
 * Validates the STAGE2_MODULE_MAP and the conditional guard logic.
 */

describe("STAGE2_MODULE_MAP integration", () => {
  test("STAGE2_MODULE_MAP keys match expected rule IDs", async () => {
    // Dynamic import to mirror Phase 8.5's import pattern
    const mod = await import("../engine/run-audit.ts");
    // The map is module-scoped const, but we can verify the exported runAudit exists
    // and the map is used correctly by checking the module loads without error
    expect(mod.runAudit).toBeDefined();
    expect(typeof mod.runAudit).toBe("function");
  });

  test("ast-refiner module can be dynamically imported (Phase 8.5 import path)", async () => {
    // This mirrors the dynamic import in run-audit.ts:177
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    expect(typeof refineFindings).toBe("function");
  });

  test("refineFindings gracefully handles empty findings array", async () => {
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    const result = await refineFindings(
      [],
      { rootPath: "/nonexistent" } as any,
      "auto",
      ["GHA-AI-001"],
      { "GHA-AI-001": "ast" },
    );
    expect(result).toEqual([]);
  });

  test("refineFindings returns findings unchanged in quick mode", async () => {
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    const findings = [{ id: "GHA-AI-001", suppressed: false } as any];
    const result = await refineFindings(
      findings,
      { rootPath: "/nonexistent" } as any,
      "quick",
      ["GHA-AI-001"],
      { "GHA-AI-001": "ast" },
    );
    expect(result).toBe(findings); // Same reference — no processing
  });
});
```

AFTER:
```ts
import { test, expect, describe } from "bun:test";
import { readFileSync } from "fs";
import { loadRuleCatalog } from "../rules/load-rule-catalog.ts";

/**
 * Tests for Phase 8.5 integration in run-audit.ts.
 * Validates the STAGE2_MODULE_MAP and the conditional guard logic.
 */

describe("STAGE2_MODULE_MAP integration", () => {
  test("hard-stop rules are covered by STAGE2_MODULE_MAP or explicitly exempted", () => {
    const catalog = loadRuleCatalog();
    const hardStops = new Set(catalog.policy_baselines.hard_stop_patterns);

    const source = readFileSync(new URL("../engine/run-audit.ts", import.meta.url), "utf8");
    const mapBody = source.match(/const STAGE2_MODULE_MAP[\s\S]*?=\s*\{([\s\S]*?)\n\};/);
    expect(mapBody).not.toBeNull();

    const mapKeys = new Set<string>();
    const re = /"([A-Z0-9-]+)"\s*:\s*"(ast|sandbox|manual_review)"/g;
    for (const match of mapBody![1]!.matchAll(re)) {
      mapKeys.add(match[1]!);
    }

    const exempt = new Set(["GHA-SECRETS-001", "GHA-CI-004", "GHA-RUNTIME-001", "GHA-RUNTIME-003"]);
    for (const id of hardStops) {
      expect(mapKeys.has(id) || exempt.has(id)).toBe(true);
    }
  });

  test("STAGE2_MODULE_MAP keys match expected rule IDs", async () => {
    // Dynamic import to mirror Phase 8.5's import pattern
    const mod = await import("../engine/run-audit.ts");
    // The map is module-scoped const, but we can verify the exported runAudit exists
    // and the map is used correctly by checking the module loads without error
    expect(mod.runAudit).toBeDefined();
    expect(typeof mod.runAudit).toBe("function");
  });

  test("ast-refiner module can be dynamically imported (Phase 8.5 import path)", async () => {
    // This mirrors the dynamic import in run-audit.ts:177
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    expect(typeof refineFindings).toBe("function");
  });

  test("refineFindings gracefully handles empty findings array", async () => {
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    const result = await refineFindings(
      [],
      { rootPath: "/nonexistent" } as any,
      "auto",
      ["GHA-AI-001"],
      { "GHA-AI-001": "ast" },
    );
    expect(result).toEqual({ findings: [], summary: expect.any(Object) });
  });

  test("refineFindings returns findings unchanged in quick mode", async () => {
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    const findings = [{ id: "GHA-AI-001", suppressed: false } as any];
    const result = await refineFindings(
      findings,
      { rootPath: "/nonexistent" } as any,
      "quick",
      ["GHA-AI-001"],
      { "GHA-AI-001": "ast" },
    );
    expect(result.findings).toBe(findings); // Same reference — no processing
  });
});
```

NOTES: This test parses `src/engine/run-audit.ts` directly to avoid exporting `STAGE2_MODULE_MAP`. If you prefer a typed import, export the map and use that instead.

---

### C5: Guard Missing `line_numbers` + Record Skip Reason
**File:** src/stage2/ast-refiner.ts

BEFORE (lines 27-33):
```ts
  for (const finding of toRefine) {
    const files = finding.files;
    const lineNumbers = finding.line_numbers;

    if (!files || files.length === 0) continue;
```

AFTER:
```ts
  for (const finding of toRefine) {
    if (!finding.line_numbers || finding.line_numbers.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "missing line_numbers" });
      continue;
    }
```

NOTES: This is part of the larger refactor in C3/C6. Apply once with the C3 block.

---

### C6: AST Refinement Observability (Summary + Audit Result Integration)
**File:** src/stage2/ast-refiner.ts

BEFORE (lines 1-16):
```ts
import { getParserForFile } from "./language-map.ts";
import { classifyMatchContext, type AstClassification } from "./ast-classifier.ts";
import { readFileContent } from "../analyzers/base.ts";
import type { Finding } from "../models/finding.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { DepthMode } from "../models/enums.ts";
import { join, isAbsolute } from "path";

export async function refineFindings(
  findings: Finding[],
  workspace: LocalWorkspace,
  depthMode: DepthMode,
  hardStopPatterns: string[],
  stage2ModuleMap: Record<string, string>,
): Promise<Finding[]> {
  if (depthMode === "quick") return findings;
```

AFTER:
```ts
import { getParserForFile } from "./language-map.ts";
import { classifyMatchContext, type AstClassification } from "./ast-classifier.ts";
import { readFileContent } from "../analyzers/base.ts";
import type { Finding } from "../models/finding.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { DepthMode } from "../models/enums.ts";
import { join, isAbsolute } from "path";

export interface AstRefinementSkip {
  finding_id: string;
  reason: string;
}

export interface AstRefinementSummary {
  findings_considered: number;
  findings_refined: number;
  findings_skipped: number;
  suppressed_findings: number;
  confirmed_findings: number;
  ambiguous_findings: number;
  error_count: number;
  skips: AstRefinementSkip[];
}

export async function refineFindings(
  findings: Finding[],
  workspace: LocalWorkspace,
  depthMode: DepthMode,
  hardStopPatterns: string[],
  stage2ModuleMap: Record<string, string>,
): Promise<{ findings: Finding[]; summary: AstRefinementSummary }> {
  const summary: AstRefinementSummary = {
    findings_considered: 0,
    findings_refined: 0,
    findings_skipped: 0,
    suppressed_findings: 0,
    confirmed_findings: 0,
    ambiguous_findings: 0,
    error_count: 0,
    skips: [],
  };

  if (depthMode === "quick") return { findings, summary };
```

BEFORE (lines 25-79):
```ts
  if (toRefine.length === 0) return findings;

  for (const finding of toRefine) {
    const files = finding.files;
    const lineNumbers = finding.line_numbers;

    if (!files || files.length === 0) continue;

    const classifications: AstClassification[] = [];

    for (let i = 0; i < files.length; i++) {
      const rawPath = files[i]!;
      const filePath = isAbsolute(rawPath) ? rawPath : join(workspace.rootPath, rawPath);
      const lineNumber = lineNumbers?.[i];
      if (!lineNumber) continue;

      const parser = await getParserForFile(filePath);
      if (!parser) continue; // unsupported language — skip

      const content = readFileContent(filePath);
      if (!content) continue;

      // Extract match text from the corresponding evidence record for this file
      let matchText = "";
      const rec = finding.evidence.records[i] as Record<string, unknown> | undefined;
      if (rec && typeof rec.match === "string") {
        matchText = rec.match;
      }

      try {
        const result = classifyMatchContext(parser, content, lineNumber, matchText);
        classifications.push(result.classification);
      } catch (err) {
        console.warn(`[ast-refiner] Classification failed for ${rawPath}:${lineNumber}: ${err}`);
        classifications.push("ambiguous");
      } finally {
        parser.delete();
      }
    }

    if (classifications.length === 0) continue;

    if (classifications.every((c) => c === "dismiss")) {
      finding.suppressed = true;
      finding.suppression_reason =
        "AST analysis: all matches are in non-executable context (string literals, comments, type names)";
    } else if (classifications.some((c) => c === "confirm")) {
      finding.confidence = "high";
    } else {
      // All ambiguous or mix of dismiss+ambiguous
      finding.confidence = "low";
    }
  }

  return findings;
```

AFTER:
```ts
  summary.findings_considered = toRefine.length;
  if (toRefine.length === 0) return { findings, summary };

  for (const finding of toRefine) {
    if (!finding.line_numbers || finding.line_numbers.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "missing line_numbers" });
      continue;
    }

    const records = finding.evidence.records as Array<Record<string, unknown>>;
    if (!records || records.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "no evidence records" });
      continue;
    }

    const classifications: AstClassification[] = [];

    for (const rec of records) {
      const rawPath = typeof rec.path === "string"
        ? rec.path
        : typeof rec.file === "string"
          ? rec.file
          : typeof rec.file_path === "string"
            ? rec.file_path
            : undefined;
      const lineNumber = typeof rec.line_number === "number" ? rec.line_number : undefined;
      if (!rawPath || !lineNumber) continue;

      const filePath = isAbsolute(rawPath) ? rawPath : join(workspace.rootPath, rawPath);

      const parser = await getParserForFile(filePath);
      if (!parser) continue; // unsupported language — skip

      const content = readFileContent(filePath);
      if (!content) continue;

      let matchText = "";
      if (typeof rec.match === "string") {
        matchText = rec.match;
      }

      try {
        const result = classifyMatchContext(parser, content, lineNumber, matchText);
        classifications.push(result.classification);
      } catch (err) {
        console.warn(`[ast-refiner] Classification failed for ${rawPath}:${lineNumber}: ${err}`);
        summary.error_count += 1;
        classifications.push("ambiguous");
      } finally {
        parser.delete();
      }
    }

    if (classifications.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "no usable evidence records" });
      continue;
    }

    summary.findings_refined += 1;

    if (classifications.every((c) => c === "dismiss")) {
      finding.suppressed = true;
      finding.suppression_reason =
        "AST analysis: all matches are in non-executable context (string literals, comments, type names)";
      summary.suppressed_findings += 1;
    } else {
      if (classifications.some((c) => c === "confirm")) summary.confirmed_findings += 1;
      if (classifications.some((c) => c === "ambiguous")) summary.ambiguous_findings += 1;
    }
  }

  console.info(
    `[ast-refiner] Summary: refined ${summary.findings_refined}/${summary.findings_considered}, ` +
      `suppressed ${summary.suppressed_findings}, confirm ${summary.confirmed_findings}, ` +
      `ambiguous ${summary.ambiguous_findings}, skipped ${summary.findings_skipped}, ` +
      `errors ${summary.error_count}`,
  );

  return { findings, summary };
```

**File:** src/engine/run-audit.ts

BEFORE (lines 174-185, 245-256):
```ts
  if (request.depth_mode !== "quick") {
    try {
      const { refineFindings } = await import("../stage2/ast-refiner.ts");
      findings = await refineFindings(
        findings,
        workspace,
        request.depth_mode,
        catalog.policy_baselines.hard_stop_patterns,
        STAGE2_MODULE_MAP,
      );
    } catch (err) {
      console.warn(`[ast-refiner] AST refinement failed, continuing with original findings: ${err}`);
    }
  }

  const result: AuditResult = {
    manifest,
    context,
    profile,
    findings,
    scores,
    decision,
    module_results: allModuleResults,
    coverage,
    reports: {},
    ...(stage2_recommended ? { stage2_recommended, stage2_triggers } : {}),
  };
```

AFTER:
```ts
  let ast_refinement_summary: AstRefinementSummary | undefined;

  if (request.depth_mode !== "quick") {
    try {
      const { refineFindings } = await import("../stage2/ast-refiner.ts");
      const refinement = await refineFindings(
        findings,
        workspace,
        request.depth_mode,
        catalog.policy_baselines.hard_stop_patterns,
        STAGE2_MODULE_MAP,
      );
      findings = refinement.findings;
      ast_refinement_summary = refinement.summary;
    } catch (err) {
      console.warn(`[ast-refiner] AST refinement failed, continuing with original findings: ${err}`);
    }
  }

  const result: AuditResult = {
    manifest,
    context,
    profile,
    findings,
    scores,
    decision,
    module_results: allModuleResults,
    coverage,
    reports: {},
    ...(ast_refinement_summary ? { ast_refinement_summary } : {}),
    ...(stage2_recommended ? { stage2_recommended, stage2_triggers } : {}),
  };
```

**File:** src/models/audit-result.ts

BEFORE (lines 21-40):
```ts
export type CoverageReport = z.infer<typeof CoverageReportSchema>;

export interface Stage2Trigger {
  finding_id: string;
  reason: string;
  recommended_module: "ast" | "sandbox" | "manual_review";
}

export interface AuditResult {
  manifest: RunManifest;
  context: AuditContext;
  profile: RepoProfile;
  findings: Finding[];
  scores: Scores;
  decision: Decision;
  module_results: ModuleResult[];
  coverage: CoverageReport;
  reports: Record<string, string>;
  stage2_recommended?: boolean;
  stage2_triggers?: Stage2Trigger[];
}
```

AFTER:
```ts
export type CoverageReport = z.infer<typeof CoverageReportSchema>;

export interface AstRefinementSkip {
  finding_id: string;
  reason: string;
}

export interface AstRefinementSummary {
  findings_considered: number;
  findings_refined: number;
  findings_skipped: number;
  suppressed_findings: number;
  confirmed_findings: number;
  ambiguous_findings: number;
  error_count: number;
  skips: AstRefinementSkip[];
}

export interface Stage2Trigger {
  finding_id: string;
  reason: string;
  recommended_module: "ast" | "sandbox" | "manual_review";
}

export interface AuditResult {
  manifest: RunManifest;
  context: AuditContext;
  profile: RepoProfile;
  findings: Finding[];
  scores: Scores;
  decision: Decision;
  module_results: ModuleResult[];
  coverage: CoverageReport;
  reports: Record<string, string>;
  ast_refinement_summary?: AstRefinementSummary;
  stage2_recommended?: boolean;
  stage2_triggers?: Stage2Trigger[];
}
```

NOTES: This changes the return type of `refineFindings`, so tests that call it need to be updated to expect `{ findings, summary }`.

---

### C8: CLI Flag Mutual Exclusivity
**File:** src/cli.ts

BEFORE (lines 1-22):
```ts
import { Command } from "commander";
import { AuditRequestSchema } from "./models/audit-request.ts";
import { runAudit } from "./engine/run-audit.ts";

const program = new Command()
  .name("stop-git-std")
  .description("Git repository safety auditor")
  .argument("<repo>", "Repository path or URL")
  .option("--ref <ref>", "Git ref to audit", "default_branch")
  .option("--env <environment>", "Target environment", "offline_analysis")
  .option("--policy <profile>", "Policy profile", "balanced")
  .option("--format <formats...>", "Output formats", ["json", "markdown"])
  .option("--output-dir <dir>", "Output directory")
  .option("--include <paths...>", "Include path patterns")
  .option("--exclude <paths...>", "Exclude path patterns")
  .option("--enable-module <modules...>", "Force-enable modules")
  .option("--disable-module <modules...>", "Force-disable modules")
  .option("--runtime-mode <mode>", "Runtime validation mode", "off")
  .option("--adoption-mode <mode>", "Adoption context", "third_party")
  .option("--skip-stage2", "Suppress stage 2 analysis recommendations", false)
  .option("--quick", "Skip AST analysis (regex-only)", false)
  .option("--deep", "Force AST analysis on all findings", false);
```

AFTER:
```ts
import { Command, Option } from "commander";
import { AuditRequestSchema } from "./models/audit-request.ts";
import { runAudit } from "./engine/run-audit.ts";

const program = new Command()
  .name("stop-git-std")
  .description("Git repository safety auditor")
  .argument("<repo>", "Repository path or URL")
  .option("--ref <ref>", "Git ref to audit", "default_branch")
  .option("--env <environment>", "Target environment", "offline_analysis")
  .option("--policy <profile>", "Policy profile", "balanced")
  .option("--format <formats...>", "Output formats", ["json", "markdown"])
  .option("--output-dir <dir>", "Output directory")
  .option("--include <paths...>", "Include path patterns")
  .option("--exclude <paths...>", "Exclude path patterns")
  .option("--enable-module <modules...>", "Force-enable modules")
  .option("--disable-module <modules...>", "Force-disable modules")
  .option("--runtime-mode <mode>", "Runtime validation mode", "off")
  .option("--adoption-mode <mode>", "Adoption context", "third_party")
  .addOption(
    new Option(
      "--skip-stage2",
      "Suppress stage 2 analysis recommendations (cannot be combined with --quick or --deep)",
    ).conflicts(["quick", "deep"]),
  )
  .option("--quick", "Skip AST analysis (regex-only)", false)
  .option("--deep", "Force AST analysis on all findings", false);
```

NOTES: `--quick` and `--deep` already imply `skip_stage2` in `request` construction; the explicit conflict prevents confusing combinations.
