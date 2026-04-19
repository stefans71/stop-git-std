# R2 Review — Skeptic (DeepSeek)

**Verdict:** SIGN OFF WITH DISSENTS (unchanged from R1)

## Response to Owner-Revised Items (§4.1-4.11)

### 4.1 Renaming — SECOND
Two-axis terminology resolves the Path A/B collision cleanly. Continuous/delegated for execution mode, V2.4/V2.5-preview for pipeline. Pragmatic fix.

### 4.2 §8.4 wording fix — SECOND
Clarifies prompt/schema/renderer relationship without contradiction. Accepts Codex's concern.

### 4.3 form.json authoring bridge — SECOND
Mapping table addresses unanimous FIX NOW. Provides concrete guidance missing from §8.8.

### 4.4 Path B gating — ADJUST
**Reason:** Codex's three warnings + shape warning are insufficient guardrails. Operators will still see concrete commands and try them. The "Step G validation only" disclaimer is weak without technical enforcement.

**Change:** Add explicit technical guardrail: "Path B commands require `export STOP_GIT_STD_EXPERIMENTAL=1` before execution. The validator will check for this environment variable when processing V2.5-preview pipeline output."

Rationale: Environment variable is lightweight, non-breaking, and creates actual friction. It's not "overkill" — it's the minimal technical gate that prevents accidental misuse. The project's operator profile (LLMs + technically fluent humans) can handle an env var.

### 4.5 Rollback plan — SECOND
Clear, actionable. Quarantine approach preserves history while removing from main flow.

### 4.6 Prompt cross-reference — SECOND
Minimal, clarifies contract.

### 4.7 Catalog methodology column — SECOND
Useful metadata distinction.

### 4.8 Structural-parity criterion — SECOND
Addresses Pragmatist's concern about validator-clean ≠ sufficient.

### 4.9 CSS line count fix — SECOND
Confirmed: `wc -l docs/scanner-design-system.css` shows 824 lines. Update CLAUDE.md line 46.

### 4.10 FX-3b package validator sync — ADJUST
**Reason:** Parallel commit is architecturally cleaner but creates sequencing risk. If FX-3b sync fails or introduces regressions, U-1 still ships with known buggy validator in package. This violates "bug fix for existing functionality" principle.

**Change:** Sequence as: (1) FX-3b package validator sync, (2) **Test** validator on existing catalog scans, (3) U-1 doc updates. Not "parallel commit" — sequential with validation step.

Rationale: FX-3b affects V2.4 users (package). Shipping U-1 while package has known bug is irresponsible. The fix is self-contained; test step ensures no regressions.

### 4.11 U-10 catalog re-validation — SECOND with timing adjustment
**Timing:** BEFORE Step G, not "post-U-1 if possible." This is data integrity issue affecting existing catalog. If shell-glob evidence corrupted, catalog scans have latent bugs.

**Change:** Schedule U-10 immediately after FX-3b sync, before any Step G scan runs. ~30 min effort catches real bugs.

## Resolution of Splits (§5.1-5.3)

### Split 5.1 — FX-3b timing
**Position:** Sequential with test, not parallel.

**Why moved from R1:** Owner's "parallel commit BEFORE U-1 lands" acknowledges both must land before Step G. I accept this sequencing but insist on validation step between FX-3b sync and U-1. Not blocking U-1 per se, but blocking U-1's *commit* until validator tested.

### Split 5.2 — Gating mechanism
**Position:** Environment variable + warnings (modified from R1).

**Why modified:** Accept Codex's three warnings as necessary documentation. Add env var as technical enforcement. Compromise: warnings educate, env var enforces.

### Split 5.3 — Scan-Readme.md handling
**Position:** SECOND owner proposal.

**Why:** Scan-Readme.md staleness is real. Including in U-1 scope with version bump and catalog count fix addresses Codex's concern. Minimal additional work.

## New FIX NOW Items

1. **Validator env var check:** Add to `validate-scanner-report.py` — if processing V2.5-preview output and `STOP_GIT_STD_EXPERIMENTAL != "1"`, warn/error.
2. **Catalog re-validation timing:** Move U-10 before Step G, not "post-U-1 if possible."

## Approval for Owner to Proceed to R3

**Yes**, with above adjustments.

---

**Summary of dissent positions maintained:**
1. FX-3b must be validated before U-1 commits (sequential with test, not parallel)
2. Path B needs technical guardrail (env var) alongside warnings
3. Catalog re-validation (U-10) before Step G, not deferred

Owner has addressed 2 of 4 original FIX NOW items (CSS line count, form.json bridge). Remaining: FX-3b sequencing adjustment, gating mechanism enhancement.