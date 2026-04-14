# Plan Modifications v2 — Complete Code Snippets

Fixes all issues found by 3-agent board review of v1:
- C1: Added missing MOD 0 (confidence gate)
- C2: Fixed Commander `--no-*` bug → `--skip-stage2`
- C3: Fixed `isNonCodeFile` semantics for config files
- H1-H4: Per-analyzer BEFORE/AFTER with proper imports and confidence handling
- H5: Added `renderPlainEnglish()` call site
- H6: Added terminal reporter Stage 2 section
- H7: Added missing imports

---

## MOD 0: Confidence gate on hard-stop filter (THE KEYSTONE CHANGE)

**File:** `src/engine/policy.ts:121`

```typescript
// BEFORE (line 121):
  const triggeredHardStop = active.filter((f) => hardStopPatterns.includes(f.id));

// AFTER:
  const triggeredHardStop = active.filter(
    (f) => hardStopPatterns.includes(f.id) && f.confidence !== "low"
  );
```

**Why:** Low-confidence regex stub matches (typed analyzers) no longer trigger ABORT. They remain as findings, affect scoring, and appear in the report — they just can't pull the ABORT trigger. Medium and high confidence findings still trigger hard-stop as before.

---

## MOD 1: Hard-stop ABORT gets constraints + per-finding remediation

**File:** `src/engine/policy.ts:127-137`

```typescript
// BEFORE (lines 127-137):
    const hardStopDecision = profileConfig.hard_stop_behavior === "caution" ? "CAUTION" : "ABORT";
    const constraints =
      hardStopDecision === "CAUTION" ? generateConstraints(active) : [];
    return {
      value: hardStopDecision,
      reasons,
      constraints,
      hard_stop_triggered: true,
      triggered_by_rules: triggeredHardStop.map((f) => f.id),
      manual_review_required: hardStopDecision === "ABORT",
    };

// AFTER:
    const hardStopDecision = profileConfig.hard_stop_behavior === "caution" ? "CAUTION" : "ABORT";
    const constraints = generateConstraints(active);
    if (hardStopDecision === "ABORT") {
      for (const f of triggeredHardStop) {
        if (f.remediation) {
          constraints.push(`[${f.id}] ${f.remediation}`);
        }
      }
      constraints.push("After applying fixes, re-run stop-git-std to verify resolution.");
    }
    return {
      value: hardStopDecision,
      reasons,
      constraints,
      hard_stop_triggered: true,
      triggered_by_rules: triggeredHardStop.map((f) => f.id),
      manual_review_required: hardStopDecision === "ABORT",
    };
```

---

## MOD 1b: Threshold ABORT also gets constraints

**File:** `src/engine/policy.ts:141-154`

```typescript
// BEFORE (lines 141-154):
  if (
    !profileConfig.thresholds.abort.disabled &&
    meetsThreshold(scores, findings, profileConfig.thresholds.abort, runtimeFindings)
  ) {
    return {
      value: "ABORT",
      reasons: [
        `Abort threshold exceeded: exploitability=${scores.exploitability}, abuse_potential=${scores.abuse_potential}`,
      ],
      constraints: [],
      hard_stop_triggered: false,
      manual_review_required: true,
    };
  }

// AFTER:
  if (
    !profileConfig.thresholds.abort.disabled &&
    meetsThreshold(scores, findings, profileConfig.thresholds.abort, runtimeFindings)
  ) {
    const constraints = generateConstraints(active);
    constraints.push("After applying fixes, re-run stop-git-std to verify resolution.");
    return {
      value: "ABORT",
      reasons: [
        `Abort threshold exceeded: exploitability=${scores.exploitability}, abuse_potential=${scores.abuse_potential}`,
      ],
      constraints,
      hard_stop_triggered: false,
      manual_review_required: true,
    };
  }
```

---

## MOD 2: File classification helper

**File:** `src/analyzers/base.ts` — add after line 81 (end of file):

```typescript
// ── File classification for typed analyzers ──────────────────────────────────

const DOC_EXTENSIONS = new Set([".md", ".txt", ".rst", ".adoc"]);
const CONFIG_EXTENSIONS = new Set([".json", ".yaml", ".yml"]);
const TEST_PATTERNS = [/__tests__\//, /\.test\.[jt]sx?$/, /\.spec\.[jt]sx?$/, /\/tests?\//, /\/fixtures?\//];

export type FileClassification = "code" | "doc" | "config" | "test";

export function classifyFile(filePath: string): FileClassification {
  const ext = "." + (filePath.split(".").pop()?.toLowerCase() ?? "");
  if (DOC_EXTENSIONS.has(ext)) return "doc";
  if (CONFIG_EXTENSIONS.has(ext)) return "config";
  if (TEST_PATTERNS.some((p) => p.test(filePath))) return "test";
  return "code";
}

/** Returns true for docs and tests — files that should be skipped by typed analyzers.
 *  Config files (.json/.yaml) return FALSE — they are scanned but findings get confidence downgrade. */
export function shouldSkipInTypedAnalyzer(filePath: string): boolean {
  const cls = classifyFile(filePath);
  return cls === "doc" || cls === "test";
}
```

**Note:** Renamed from `isNonCodeFile` to `shouldSkipInTypedAnalyzer` to match actual semantics. Config files are NOT skipped — they're scanned with confidence downgrade.

---

## MOD 2a: ai-llm.ts — full BEFORE/AFTER

**File:** `src/analyzers/typed/ai-llm.ts`

**Import change (line 3):**
```typescript
// BEFORE:
import { emitFinding, scanFileContent } from "../base.ts";

// AFTER:
import { emitFinding, scanFileContent, shouldSkipInTypedAnalyzer, classifyFile } from "../base.ts";
```

**File filter (after line 33):**
```typescript
// BEFORE (lines 28-33):
    let allFiles: string[] = [];
    try {
      allFiles = walkFiles(workspace.rootPath);
    } catch {
      // workspace not accessible
    }

// AFTER:
    let allFiles: string[] = [];
    try {
      allFiles = walkFiles(workspace.rootPath);
    } catch {
      // workspace not accessible
    }
    // Skip docs/tests; keep code + config (config findings get confidence downgrade)
    const scanFiles = allFiles.filter((f) => !shouldSkipInTypedAnalyzer(f));
```

**GHA-AI-001 scan loop + confidence handling (lines 43-67):**
```typescript
// BEFORE:
          for (const f of allFiles) {
            const matches = scanFileContent(f, regex);
            for (const m of matches) {
              matchedFiles.push(m.path);
              lineNumbers.push(m.lineNumber);
            }
          }

          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "regex_match",
                records: matchedFiles.map((f, i) => ({
                  file: f,
                  line: lineNumbers[i],
                  pattern: "model execution keyword",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            finding.confidence = "low";
            findings.push(finding);
          }

// AFTER:
          for (const f of scanFiles) {
            const matches = scanFileContent(f, regex);
            for (const m of matches) {
              matchedFiles.push(m.path);
              lineNumbers.push(m.lineNumber);
            }
          }

          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "regex_match",
                records: matchedFiles.map((f, i) => ({
                  file: f,
                  line: lineNumbers[i],
                  pattern: "model execution keyword",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            // Code matches get rule default confidence; config-only matches get "low"
            const hasCodeMatch = [...new Set(matchedFiles)].some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
```

**Same pattern for GHA-AI-002 (lines ~77-100):** Replace `allFiles` → `scanFiles`, replace `finding.confidence = "low"` with the `hasCodeMatch` check.

**GHA-AI-003 (lines ~112-142):** Replace both `allFiles` references → `scanFiles`, replace `finding.confidence = "low"` with the `hasCodeMatch` check.

---

## MOD 2b: agent-framework.ts — full BEFORE/AFTER

**File:** `src/analyzers/typed/agent-framework.ts`

**Import change (line 3):**
```typescript
// BEFORE:
import { emitFinding, scanFileContent } from "../base.ts";

// AFTER:
import { emitFinding, scanFileContent, shouldSkipInTypedAnalyzer, classifyFile } from "../base.ts";
```

**File filter (after line 33):** Same as ai-llm.ts — add `const scanFiles = allFiles.filter(...)` after the try/catch.

**GHA-AGENT-001 (lines 43-67):** Replace `allFiles` → `scanFiles`, replace `finding.confidence = "low"` with:
```typescript
            const hasCodeMatch = [...new Set(matchedFiles)].some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
```

**GHA-AGENT-002 (lines ~77-100):** Same pattern.

---

## MOD 2c: mcp-server.ts — full BEFORE/AFTER

**File:** `src/analyzers/typed/mcp-server.ts`

**Import change (line 3):**
```typescript
// BEFORE:
import { emitFinding, scanFileContent } from "../base.ts";

// AFTER:
import { emitFinding, scanFileContent, shouldSkipInTypedAnalyzer, classifyFile } from "../base.ts";
```

**File filter (after line 33):** Same — add `const scanFiles = allFiles.filter(...)`.

**GHA-MCP-001 (lines 47-69):** This rule has a different structure — it compares `filesWithMcp` vs `filesWithAuth`. Replace both `allFiles` loops → `scanFiles`:
```typescript
// BEFORE (lines 47-49):
          for (const f of allFiles) {
            if (scanFileContent(f, regex).length > 0) filesWithMcp.add(f);
            if (scanFileContent(f, authRegex).length > 0) filesWithAuth.add(f);
          }

// AFTER:
          for (const f of scanFiles) {
            if (scanFileContent(f, regex).length > 0) filesWithMcp.add(f);
            if (scanFileContent(f, authRegex).length > 0) filesWithAuth.add(f);
          }
```

Then replace `finding.confidence = "low"` with the `hasCodeMatch` check.

**GHA-MCP-002 (lines ~81-105)** and **GHA-MCP-003 (lines ~115-142):** Same pattern — `allFiles` → `scanFiles`, conditional confidence.

---

## MOD 2d: skills-plugins.ts — full BEFORE/AFTER

**File:** `src/analyzers/typed/skills-plugins.ts`

**Import change (line 2):**
```typescript
// BEFORE:
import { join, basename } from "path";

// No change needed here, but add to the base import on line 3:
// BEFORE:
import { emitFinding, scanFileContent } from "../base.ts";

// AFTER:
import { emitFinding, scanFileContent, shouldSkipInTypedAnalyzer, classifyFile } from "../base.ts";
```

**File filter (after line 33):** Same — add `const scanFiles = allFiles.filter(...)`.

**GHA-PLUGIN-001 (lines 39-73):** This rule already filters to manifest files — leave as-is (it only scans `plugin.json`, `manifest.json`). No change needed for this rule.

**GHA-PLUGIN-002 (lines 76-105):** This is the problematic one — scans ALL files for injection patterns. Change:
```typescript
// BEFORE (line 82):
          for (const f of allFiles) {

// AFTER:
          for (const f of scanFiles) {
```

And restructure the inline push to allow confidence check:
```typescript
// BEFORE (lines 91-105):
          if (matchedFiles.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "regex_match",
                  records: matchedFiles.map((f, i) => ({
                    file: f,
                    line: lineNumbers[i],
                    pattern: "prompt injection indicator",
                  })),
                },
                [...new Set(matchedFiles)],
                lineNumbers,
              ),
            );
          }

// AFTER:
          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "regex_match",
                records: matchedFiles.map((f, i) => ({
                  file: f,
                  line: lineNumbers[i],
                  pattern: "prompt injection indicator",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            const hasCodeMatch = [...new Set(matchedFiles)].some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
```

---

## MOD 3: Plain-English section (with call site)

**File:** `src/reporting/terminal.ts`

**New function** — add after `decisionExplanation()` (after line 87):

```typescript
function renderPlainEnglish(result: AuditResult): string[] {
  const lines: string[] = [];
  const active = result.findings.filter((f) => !f.suppressed);
  const critical = active.filter((f) => f.severity === "critical");
  const high = active.filter((f) => f.severity === "high");
  const medium = active.filter((f) => f.severity === "medium");

  lines.push(pc.bold("  What This Means"));
  lines.push(pc.dim("  " + "─".repeat(30)));
  lines.push("");

  switch (result.decision.value) {
    case "PROCEED":
      lines.push("  No serious issues detected in our static checks. We scanned");
      lines.push(`  ${result.coverage.files_scanned} files and found nothing that would`);
      lines.push("  prevent safe adoption.");
      break;
    case "PROCEED_WITH_CONSTRAINTS":
      lines.push("  We found some issues that need attention before you use this.");
      lines.push("  None are critically dangerous, but the mitigations listed below");
      lines.push("  should be applied first.");
      break;
    case "CAUTION":
      lines.push("  We found issues that deserve a closer look before you use this.");
      lines.push("  Review the findings below and decide whether the risks are");
      lines.push("  acceptable for your use case.");
      break;
    case "ABORT":
      lines.push("  We found serious security issues that should be fixed before");
      lines.push("  you use this. See the specific issues and remediation steps below.");
      break;
  }
  lines.push("");

  // Show critical/high findings in plain English; show medium if few and no critical/high
  const showFindings = [...critical, ...high];
  if (showFindings.length === 0 && medium.length > 0 && medium.length <= 3) {
    showFindings.push(...medium);
  }

  if (showFindings.length > 0) {
    lines.push(`  We found ${showFindings.length} issue(s) worth knowing about:`);
    lines.push("");
    for (const f of showFindings) {
      const explanation = RISK_EXPLANATIONS[f.id];
      if (explanation) {
        lines.push(`  ${pc.dim("•")} ${explanation.plain}`);
      }
    }
    lines.push("");
  }

  return lines;
}
```

**Call site in `renderTerminalReport()`** — insert after reasons, before `lines.push(hr)`:

```typescript
// BEFORE (lines 183-190):
  if (result.decision.reasons.length > 0) {
    for (const r of result.decision.reasons) {
      lines.push(`  ${pc.dim("•")} ${r}`);
    }
    lines.push("");
  }

  lines.push(hr);

// AFTER:
  if (result.decision.reasons.length > 0) {
    for (const r of result.decision.reasons) {
      lines.push(`  ${pc.dim("•")} ${r}`);
    }
    lines.push("");
  }

  // ── Plain English summary ──
  lines.push(...renderPlainEnglish(result));

  lines.push(hr);
```

---

## MOD 4: RISK_EXPLANATIONS restructure

Same as v1 — approved by all 3 agents. No changes needed.

**File:** `src/reporting/terminal.ts:91-146` — replace entire `RISK_EXPLANATIONS` with the `{ technical, plain }` version from v1.

**Usage update at line ~276:**
```typescript
// BEFORE:
  lines.push(`  ${pc.dim("Risk:")}  ${explanation}`);
// AFTER:
  lines.push(`  ${pc.dim("Risk:")}  ${explanation.technical}`);
```

---

## MOD 5: Stage 2 fields + terminal section

**File:** `src/models/audit-result.ts` — same as v1 (approved):

```typescript
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

**File:** `src/reporting/markdown.ts` — same as v1 (approved).

**File:** `src/reporting/sarif.ts` — same as v1 (approved).

**File:** `src/reporting/terminal.ts` — NEW (was missing in v1). Add after constraints section, before coverage (after line 315):

```typescript
  // ── Stage 2 recommendations ──
  if (result.stage2_recommended && result.stage2_triggers && result.stage2_triggers.length > 0) {
    lines.push(hr);
    lines.push("");
    lines.push(pc.bold("  Deeper Analysis Recommended"));
    lines.push(pc.dim("  Static analysis flagged issue(s) with low confidence."));
    lines.push(pc.dim("  A deeper scan could confirm or dismiss these."));
    lines.push("");
    for (const t of result.stage2_triggers) {
      const moduleLabel = t.recommended_module === "ast" ? "Code flow analysis"
        : t.recommended_module === "sandbox" ? "Sandbox execution"
        : "Manual review";
      lines.push(`  ${pc.yellow("→")} ${pc.bold(t.finding_id)}: ${t.reason}`);
      lines.push(`    ${pc.dim("Recommended:")} ${moduleLabel}`);
    }
    lines.push("");
    lines.push(pc.dim("  Future: stop-git-std --deep <repo>"));
    lines.push("");
  }
```

---

## MOD 6: `--skip-stage2` flag (fixed from `--no-stage2`)

**File:** `src/models/audit-request.ts` — add to schema:

```typescript
  skip_stage2: z.boolean().default(false),
```

**File:** `src/cli.ts`

```typescript
// BEFORE (line 19):
  .option("--adoption-mode <mode>", "Adoption context", "third_party");

// AFTER:
  .option("--adoption-mode <mode>", "Adoption context", "third_party")
  .option("--skip-stage2", "Suppress stage 2 analysis recommendations", false);
```

```typescript
// BEFORE (lines 31-43):
  const request = AuditRequestSchema.parse({
    repo_target: repoTarget,
    ref: opts.ref,
    target_environment: opts.env,
    policy_profile: opts.policy,
    output_formats: opts.format,
    include_paths: opts.include ?? [],
    exclude_paths: opts.exclude,
    enabled_modules: opts.enableModule ?? [],
    disabled_modules: opts.disableModule ?? [],
    runtime_mode: opts.runtimeMode,
    adoption_mode: opts.adoptionMode,
  });

// AFTER:
  const request = AuditRequestSchema.parse({
    repo_target: repoTarget,
    ref: opts.ref,
    target_environment: opts.env,
    policy_profile: opts.policy,
    output_formats: opts.format,
    include_paths: opts.include ?? [],
    exclude_paths: opts.exclude,
    enabled_modules: opts.enableModule ?? [],
    disabled_modules: opts.disableModule ?? [],
    runtime_mode: opts.runtimeMode,
    adoption_mode: opts.adoptionMode,
    skip_stage2: opts.skipStage2 ?? false,
  });
```

**File:** `src/engine/run-audit.ts`

**Import change (line 3):**
```typescript
// BEFORE:
import type { AuditResult } from "../models/audit-result.ts";

// AFTER:
import type { AuditResult, Stage2Trigger } from "../models/audit-result.ts";
```

**Stage 2 logic — add after line 174 (after evaluatePolicy), before line 177 (buildCoverageReport):**

```typescript
  // ── Stage 2 escalation detection ───────────────────────────────────────────
  let stage2_recommended = false;
  const stage2_triggers: Stage2Trigger[] = [];

  if (!request.skip_stage2) {
    const hardStopPatterns: string[] = catalog.policy_baselines.hard_stop_patterns;
    const lowConfHardStops = findings.filter(
      (f) => !f.suppressed && hardStopPatterns.includes(f.id) && f.confidence === "low"
    );

    const STAGE2_MODULE_MAP: Record<string, "ast" | "sandbox" | "manual_review"> = {
      "GHA-AI-001": "ast",
      "GHA-AGENT-001": "ast",
      "GHA-MCP-001": "ast",
      "GHA-MCP-003": "ast",
      "GHA-EXEC-004": "ast",
      "GHA-EXEC-005": "ast",
      "GHA-EXEC-001": "sandbox",
      "GHA-EXEC-002": "sandbox",
    };

    for (const f of lowConfHardStops) {
      const mod = STAGE2_MODULE_MAP[f.id] ?? "manual_review";
      const label = mod === "ast" ? "code flow analysis"
        : mod === "sandbox" ? "sandbox execution" : "manual review";
      stage2_triggers.push({
        finding_id: f.id,
        reason: `Low-confidence static match — ${label} could confirm or dismiss this.`,
        recommended_module: mod,
      });
    }

    stage2_recommended = stage2_triggers.length > 0;
  }
```

**Result construction (line 194):**
```typescript
// BEFORE:
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
  };

// AFTER:
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

---

## MOD 7: `.env.example`/`.sample`/`.template`

Same as v1 — approved by all 3 agents. No changes needed.

---

## MOD 8: Test cases (fixed)

**File:** `src/__tests__/policy.test.ts` — add inside the `describe("evaluatePolicy", ...)` block:

Same confidence gate + ABORT constraints tests as v1 — approved by all 3 agents.

**File:** `src/__tests__/base.test.ts` (new file) — FIXED:

```typescript
import { describe, test, expect } from "bun:test";
import { classifyFile, shouldSkipInTypedAnalyzer } from "../analyzers/base.ts";

describe("classifyFile", () => {
  test("classifies .md as doc", () => {
    expect(classifyFile("README.md")).toBe("doc");
    expect(classifyFile("docs/plan.md")).toBe("doc");
  });

  test("classifies .json/.yaml as config", () => {
    expect(classifyFile("package.json")).toBe("config");
    expect(classifyFile("config.yaml")).toBe("config");
    expect(classifyFile("rules.yml")).toBe("config");
  });

  test("classifies test files as test", () => {
    expect(classifyFile("src/__tests__/policy.test.ts")).toBe("test");
    expect(classifyFile("tests/unit/foo.spec.js")).toBe("test");
  });

  test("classifies .ts/.js/.py as code", () => {
    expect(classifyFile("src/engine/policy.ts")).toBe("code");
    expect(classifyFile("lib/index.js")).toBe("code");
    expect(classifyFile("main.py")).toBe("code");
  });
});

describe("shouldSkipInTypedAnalyzer", () => {
  test("returns true for docs — they are skipped entirely", () => {
    expect(shouldSkipInTypedAnalyzer("README.md")).toBe(true);
    expect(shouldSkipInTypedAnalyzer("docs/plan.txt")).toBe(true);
  });

  test("returns true for tests — they are skipped entirely", () => {
    expect(shouldSkipInTypedAnalyzer("src/__tests__/foo.test.ts")).toBe(true);
    expect(shouldSkipInTypedAnalyzer("tests/unit/bar.spec.js")).toBe(true);
  });

  test("returns false for code files — they are scanned normally", () => {
    expect(shouldSkipInTypedAnalyzer("src/engine/policy.ts")).toBe(false);
  });

  test("returns false for config files — they are scanned with confidence downgrade", () => {
    expect(shouldSkipInTypedAnalyzer("package.json")).toBe(false);
    expect(shouldSkipInTypedAnalyzer("config.yaml")).toBe(false);
    // classifyFile still returns "config" for downstream confidence handling
    expect(classifyFile("package.json")).toBe("config");
  });
});
```

---

## Execution Order

1. **MOD 0**: Confidence gate (`policy.ts:121`) — keystone, everything depends on this
2. **MOD 1 + 1b**: ABORT remediation paths (`policy.ts:127-154`)
3. **MOD 2 + 2a-2d**: File classification + typed analyzer updates (`base.ts` + 4 analyzers)
4. **MOD 7**: `.env.example` downgrade (`secrets.ts`)
5. **MOD 4**: RISK_EXPLANATIONS restructure (`terminal.ts`) — must come before MOD 3
6. **MOD 3**: Plain-English section with call site (`terminal.ts`)
7. **MOD 5**: Stage 2 fields + terminal/markdown/SARIF sections
8. **MOD 6**: `--skip-stage2` CLI plumbing (`audit-request.ts`, `cli.ts`, `run-audit.ts`)
9. **MOD 8**: Tests (last — validates everything above)

## Summary

| File | Changes |
|------|---------|
| `src/engine/policy.ts` | MOD 0 (line 121), MOD 1 (lines 127-137), MOD 1b (lines 141-154) |
| `src/analyzers/base.ts` | MOD 2 (new exports: classifyFile, shouldSkipInTypedAnalyzer) |
| `src/analyzers/typed/ai-llm.ts` | MOD 2a (import, scanFiles filter, conditional confidence ×3 rules) |
| `src/analyzers/typed/agent-framework.ts` | MOD 2b (same pattern ×2 rules) |
| `src/analyzers/typed/mcp-server.ts` | MOD 2c (same pattern ×3 rules) |
| `src/analyzers/typed/skills-plugins.ts` | MOD 2d (same pattern, GHA-PLUGIN-002 restructured from inline push) |
| `src/analyzers/universal/secrets.ts` | MOD 7 (.env.example downgrade) |
| `src/reporting/terminal.ts` | MOD 4 (RISK_EXPLANATIONS), MOD 3 (renderPlainEnglish + call site), MOD 5 (Stage 2 section) |
| `src/models/audit-result.ts` | MOD 5 (Stage2Trigger interface + optional fields) |
| `src/models/audit-request.ts` | MOD 6 (skip_stage2 field) |
| `src/cli.ts` | MOD 6 (--skip-stage2 option + plumbing) |
| `src/engine/run-audit.ts` | MOD 6 (Stage2Trigger import + escalation logic + result construction) |
| `src/reporting/markdown.ts` | MOD 5 (Stage 2 section) |
| `src/reporting/sarif.ts` | MOD 5 (Stage 2 properties) |
| `src/__tests__/policy.test.ts` | MOD 8 (confidence gate + ABORT constraints tests) |
| `src/__tests__/base.test.ts` | MOD 8 (new file — file classification tests) |

**Total: 16 files, ~420 lines of changes**

## v1 → v2 Fixes Applied

| Issue | v1 Problem | v2 Fix |
|-------|-----------|--------|
| C1 | Missing confidence gate MOD | Added MOD 0 with exact BEFORE/AFTER |
| C2 | Commander `--no-stage2` bug | Renamed to `--skip-stage2` / `opts.skipStage2` |
| C3 | `isNonCodeFile` test failure | Renamed to `shouldSkipInTypedAnalyzer`, config returns false |
| H1 | Import inside function body | Import at file top in each MOD 2a-2d |
| H2 | `codeFiles` never used | Renamed to `scanFiles`, wired into every loop |
| H3 | Generic snippet for 4 analyzers | Per-analyzer BEFORE/AFTER (MOD 2a-2d) |
| H4 | Existing `confidence="low"` overrides | Replaced with conditional: code→rule default, config→"low" |
| H5 | `renderPlainEnglish()` dead code | Added explicit call site in renderTerminalReport |
| H6 | No terminal Stage 2 section | Added terminal Stage 2 section in MOD 5 |
| H7 | Missing Stage2Trigger import | Added to run-audit.ts import line |
