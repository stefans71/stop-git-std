# Board Final Recommendation — Detection Accuracy & Scoring Calibration

**Date:** 2026-04-14
**Board:** Pragmatist (Claude Opus 4.6), Systems Thinker (Codex GPT-5.2), Skeptic (DeepSeek V3.2)
**Rounds:** 1 (unanimous consensus — Round 2 skipped)
**Consolidation:** `board/detection-review-consolidation.md`

---

## Verdict

| Rating | Score | Assessment |
|--------|-------|------------|
| Detection Accuracy | **2/5** | Universal analyzers work. Typed analyzers produce 37% false positives. |
| Scoring Calibration | **3/5** | Math is correct. Garbage in → garbage out. |
| Actionability | **1/5** | 4/6 repos get ABORT with zero remediation guidance. |
| Overall Maturity | **2/5** | Solid architecture, production-unready typed analyzers. |

Tool got **2/6 decisions right** (Express=PROCEED, onecli=ABORT). Remaining 4 are too aggressive.

---

## 3 Priority Fixes

### FIX 1: Hard-stop rules must gate on confidence

**Problem:** `policy.ts:121` — `active.filter(f => hardStopPatterns.includes(f.id))` ignores confidence. Low-confidence regex stub matches trigger ABORT identically to high-confidence static matches.

**Impact:** Fixes Google WS CLI (ABORT→CAUTION), self-audit (ABORT→PROCEED), partially fixes gstack.

**File:** `src/engine/policy.ts:121`

```typescript
// BEFORE (line 121):
const triggeredHardStop = active.filter((f) => hardStopPatterns.includes(f.id));

// AFTER:
const triggeredHardStop = active.filter(
  (f) => hardStopPatterns.includes(f.id) && f.confidence !== "low"
);
// Low-confidence hard-stop matches are still reported as findings but don't trigger ABORT.
// They become HIGH findings that contribute to scoring thresholds instead.
```

**Verification:** Re-run self-audit — should drop from ABORT to PROCEED/CAUTION. Re-run Google WS CLI — should drop from ABORT to CAUTION.

---

### FIX 2: Generate remediation paths for ABORT decisions

**Problem:** `policy.ts:128-130` — When hard-stop triggers ABORT, constraints array is empty. `generateConstraints()` only runs for CAUTION decisions.

**Impact:** Every ABORT becomes actionable with prioritized fix list.

**File:** `src/engine/policy.ts:120-138`

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
// For ABORT, also add per-finding remediation as constraints
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

Also update the ABORT threshold path (`policy.ts:141-154`) to include constraints:

```typescript
// BEFORE (line 150):
constraints: [],

// AFTER:
constraints: generateConstraints(active),
```

**File:** `src/reporting/terminal.ts`

The terminal reporter already renders constraints when present (lines 302-315). No changes needed — once policy.ts generates constraints for ABORT, they'll appear in the report automatically.

---

### FIX 3: Typed analyzers skip non-code files

**Problem:** All 4 typed analyzers (`ai-llm.ts`, `agent-framework.ts`, `mcp-server.ts`, `skills-plugins.ts`) scan ALL files including `.md`, `.yaml`, `.json`, and test files. This causes false positives on documentation, rule catalogs, test fixtures, and the tool's own source descriptions.

**Impact:** Eliminates ~80% of typed analyzer false positives. FrontierBoard CAUTION→PROCEED. Self-audit FP count drops from 11 to ~2.

**File:** `src/analyzers/base.ts` — Add a helper function:

```typescript
// Add after line 56 (after readFileContent):

const NON_CODE_EXTENSIONS = new Set([".md", ".yaml", ".yml", ".json", ".txt", ".rst", ".adoc"]);
const TEST_PATTERNS = [/__tests__\//, /\.test\.[jt]sx?$/, /\.spec\.[jt]sx?$/, /test\//, /tests\//];

export function isNonCodeFile(filePath: string): boolean {
  const ext = "." + filePath.split(".").pop()?.toLowerCase();
  if (NON_CODE_EXTENSIONS.has(ext)) return true;
  return TEST_PATTERNS.some((p) => p.test(filePath));
}
```

**Files:** Each typed analyzer's `walkFiles` loop — filter out non-code files, OR keep matches but force `confidence = "low"`:

For `src/analyzers/typed/ai-llm.ts`, `agent-framework.ts`, `mcp-server.ts`, `skills-plugins.ts`:

```typescript
// In each analyzer, after building allFiles, add:
import { isNonCodeFile } from "../base.ts";

// Option A: Skip non-code files entirely (recommended for stubs)
const codeFiles = allFiles.filter((f) => !isNonCodeFile(f));
// Then use codeFiles instead of allFiles in the scan loops

// Option B: Keep matches but force low confidence (preserves signal)
// After emitFinding, add:
if (matchedFiles.some((f) => isNonCodeFile(f))) {
  finding.confidence = "low";
}
```

**Recommended approach:** Option A (skip entirely) for now. These are regex stubs — matching on documentation is pure noise. When AST analysis is implemented, switch to Option B to preserve the signal with appropriate confidence downgrade.

---

## Additional Fixes (Lower Priority)

### FIX 4: Distinguish `.env.example` from `.env`

**File:** `src/analyzers/universal/secrets.ts`
**What:** In the GHA-SECRETS-002 check, skip files ending in `.example` or set severity to `info`.

```typescript
// In the secrets analyzer's .env check, add:
if (f.relativePath.endsWith(".example")) {
  finding.severity = "info";
  finding.confidence = "low";
}
```

### FIX 5: Add "recommend deeper analysis" for low-confidence ABORT triggers

**File:** `src/reporting/terminal.ts`
**What:** When the decision is ABORT and any triggering finding has `confidence: "low"`, add a line:

```typescript
// After the decision explanation block (line 87):
if (result.decision.value === "ABORT" || result.decision.value === "CAUTION") {
  const lowConfFindings = result.findings.filter(
    (f) => !f.suppressed && f.confidence === "low" && ["critical", "high"].includes(f.severity)
  );
  if (lowConfFindings.length > 0) {
    lines.push(pc.yellow("  ⚠ " + lowConfFindings.length + " finding(s) detected with low confidence (regex-only)."));
    lines.push(pc.yellow("    Consider AST analysis or manual review to confirm before acting."));
    lines.push("");
  }
}
```

### FIX 6: Implement OSV dependency vulnerability scanning

**File:** `src/analyzers/universal/osv.ts` (currently stubbed)
**What:** Hit the OSV.dev API with dependency manifest data. This is the biggest detection gap — all three agents flagged it.
**Effort:** Significant (new HTTP client, API integration, response parsing). Roadmap item.

---

## Expected Outcomes After FIX 1-3

| Repo | Current Decision | Expected Decision |
|------|-----------------|-------------------|
| expressjs/express | PROCEED | **PROCEED** (unchanged) |
| stefans71/FrontierBoard | CAUTION | **PROCEED** (FP findings become low-confidence, don't trigger thresholds) |
| onecli/onecli | ABORT | **ABORT** (real critical findings survive confidence gate) |
| garrytan/gstack | ABORT | **CAUTION** (real CI-004 survives, agent/AI stubs become low-confidence) |
| googleworkspace/cli | ABORT | **CAUTION** (AI-001 becomes low-confidence, real CI findings drive CAUTION) |
| stop-git-std (self) | ABORT | **PROCEED** (all typed FPs eliminated by file filtering) |

Accuracy improves from **2/6 correct** to **5/6 correct** (gstack may still warrant debate between CAUTION and PROCEED_WITH_CONSTRAINTS).

---

## Process Note

All three board agents reached unanimous consensus on Round 1. The detection accuracy problem is clear-cut: universal analyzers work, typed analyzers don't (for production use), and the policy engine lacks confidence gating. No deliberation was needed.
