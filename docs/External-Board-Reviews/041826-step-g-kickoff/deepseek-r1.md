# Board Review R1 — Skeptic Response

**Reviewer:** Skeptic (DeepSeek V3.2)
**Date:** 2026-04-18
**Verdict:** SIGN OFF WITH DISSENTS
**Word count:** ~1800

## Q1: Is "additive" the right strategy?

**Answer:** Yes, but with critical caveats. Additive documentation (Path A primary, Path B experimental) is correct **only if**:

1. **Path B is explicitly gated** with more than "experimental" warnings. Current proposal relies on wording alone. Operators will see documented commands and try them.
2. **A clear migration trigger** is defined. When does Path B become primary? After Step G succeeds? After N live scans? Unclear.
3. **Rollback plan is documented** in §8.8. What happens if Step G reveals schema defects? How do operators revert?

**Dissent:** The "experimental" label is insufficient guardrail. Path B should require an explicit environment variable or command-line flag to enable, preventing accidental use.

## Q2: Does the V2.4 prompt need updating?

**Answer:** Minimal cross-reference only, as owner proposes. The prompt's output-format section (lines 1106-1490) **is** the rendering contract. Both Path A (LLM authors MD) and Path B (render from form.json) must produce prompt-compliant output.

Add a single cross-reference at line 1106:
```markdown
> **Output format specification** — the exact MD file structure. This specification is also realized via `docs/scan-schema.json` V1.1 + `docs/render-md.py`/`docs/render-html.py` for the JSON-first pipeline (Path V2.5-preview).
```

No rewrite needed. The prompt describes **what** to output, not **how** to produce it.

## Q3: How do we handle the 10 existing catalog scans?

**Answer:** Leave them as V2.4 artifacts **but** we must address the validator bug (Q4.2). The catalog (`docs/scanner-catalog.md`) should document entries 1-10 as V2.4 outputs. Step G adds first V2.5-preview entries.

**Critical issue:** These 10 scans have **never** been validated against the fixed validator (missing FX-3b fix). Any shell-glob evidence (e.g., `/plugins/*/hooks/*.js`) may have been corrupted by the comment-strip bug. This is latent data corruption.

## Q4: Package drift

### Q4.1 — Operator guide parity
**Answer:** Accept drift as V2.4-to-V2.5 boundary marker. Updating both in lockstep creates confusion: package users get experimental Path B documentation for a workflow their package doesn't support (no renderer files). The package is V2.4 snapshot; repo evolves to V2.5-preview.

### Q4.2 — Validator sync
**Answer:** **FIX NOW.** The package validator missing FX-3 + FX-3b is a **real bug** affecting V2.4 scans. The comment-strip bug (FX-3b) eats shell-glob-containing evidence. This affects existing scans (caveman has shell globs). Package users deserve the fix.

**Action:** Sync validator fixes to package **before** U-1 ships. This is a bug fix, not feature addition.

### Q4.3 — Full package refresh
**Answer:** Post-Step G separate work item, correct. V2.5 package should include renderer + schema + fixtures after Step G validates live pipeline.

## Q5: Safety concern with Path B documented pre-validation?

**Answer:** **Major safety concern.** The proposed "experimental — Step G validation in progress" wording is weak. Operators reading the guide will see concrete commands (`python3 docs/render-md.py form.json`) and try them.

**Failure mode:** Operator runs Path B on a non-fixtured repo shape (e.g., CLI binary like fd), hits schema edge case, produces invalid JSON, can't debug because §8.8 provides no guidance on form.json authoring.

**Fix:** Add explicit guardrails:
1. **Environment variable requirement:** `export STOP_GIT_STD_EXPERIMENTAL=1` to enable Path B commands
2. **Shape validation warning:** "Only validated for 3 shapes: JS library, curl-pipe installer, agentic platform"
3. **Debug guidance:** What to do when form.json validation fails

## Q6: Rollback plan if Step G fails?

**Answer:** Owner proposal is inadequate. "Path B docs update to reflect V1.2" assumes schema evolution is trivial. If Step G reveals fundamental schema gaps (e.g., missing fields for CLI binary shape), the fix may require breaking changes.

**Rollback plan needed in §8.8:**
- "If Step G fails, Path B documentation will be marked DEPRECATED until schema issues resolved"
- "Operators should revert to Path V2.4"
- "Check `docs/External-Board-Reviews/` for Step G status"

## Q7: Blind spots in proposed draft?

**Answer:** Multiple critical blind spots:

### 1. **No guidance on form.json authoring**
§8.8 says "author `form.json` conforming to V1.1 schema" but provides zero instruction. How does an operator produce form.json from findings-bundle? This is the **hardest part** of Path B. Without guidance, operators will fail.

### 2. **Fixture provenance gap**
The 3 V1.1 fixtures (zustand, caveman, archon-subset) cover only 3 of 6 catalog shapes. Missing: CLI binary (fd), Claude Code skills (gstack), web app (postiz-app), Python platform (hermes-agent). Step G may uncover schema gaps.

### 3. **Validator bug affects existing catalog**
The comment-strip bug (FX-3b) means all V2.4 scans with shell-glob evidence have potentially corrupted evidence. This should be acknowledged and fixed.

### 4. **No error handling guidance**
What happens when `render-md.py` fails? What are common errors? How to debug schema validation failures? Missing.

### 5. **CSS line count discrepancy**
CLAUDE.md says CSS is 816 lines; SCANNER-OPERATOR-GUIDE.md says 824 lines. Which is correct? This minor inconsistency erodes trust.

## Additional Blind Spots (Skeptic-specific)

### 1. **Data corruption in catalog scans**
The 10 existing catalog scans were validated with buggy validator (missing FX-3b). Any shell-glob evidence is corrupted. Example: caveman scan evidence with `/plugins/*/hooks/*.js` patterns may be truncated. This undermines catalog integrity.

**Action:** Re-validate all catalog scans with fixed validator, note any corruption in catalog metadata.

### 2. **Path B creates two classes of operators**
Experienced operators (repo contributors) know Path B is experimental. New operators (reading guide) see two paths and may choose Path B because it looks more automated ("deterministic renderer"). This creates support burden.

### 3. **Documentation rot risk**
If Step G is delayed or fails, §8.8 becomes stale documentation. "Step G validation in progress" has no expiration. Should include "Last updated: 2026-04-18" and reference to board review records.

### 4. **Missing shape coverage warning**
§8.8 should explicitly warn: "Only validated for 3 shapes: JS library (zustand), curl-pipe installer (caveman), agentic platform (archon-subset). Other shapes (CLI binary, web app, Python platform) not yet exercised."

### 5. **No provenance for back-authored fixtures**
The 3 fixtures are "back-authored reconstructions of goldens." Are they exact reconstructions or approximations? Fidelity matters for Step G validation.

## FIX NOW / DEFER / INFO

### FIX NOW (blocking U-1)
1. **Sync validator fixes to package** (FX-3b comment-strip bug fix) — real bug affecting V2.4 scans
2. **Add explicit guardrails for Path B** — environment variable requirement + shape warnings
3. **Fix CSS line count inconsistency** — 816 vs 824 lines
4. **Add form.json authoring guidance** to §8.8, even if basic

### DEFER (post-U-1)
1. **Full package refresh** — V2.5 after Step G
2. **Catalog scan re-validation** — check for shell-glob evidence corruption
3. **Provenance tagging** for fixtures

### INFO (awareness)
1. **10 catalog scans never validated with fixed validator** — latent data corruption risk
2. **Fixture shape coverage gap** — 3 of 6 catalog shapes covered
3. **Path B support burden** — operators will try it and need help

## Verdict Rationale

**SIGN OFF WITH DISSENTS** because:

1. **Additive approach is correct** but needs stronger guardrails
2. **Critical bug fix (FX-3b) must sync to package** before U-1
3. **Safety concerns with Path B documentation** require explicit gating
4. **Overall direction is sound** but execution details need hardening

The owner's scope decision (repo-only docs, additive paths) is architecturally sound. However, the implementation details create operational risks that must be addressed before U-1 ships.

**Primary dissent:** Package validator must be fixed (FX-3b) because it's a real bug affecting V2.4 users. This isn't "package maintenance" — it's bug fix for existing functionality.

**Secondary dissent:** Path B documentation needs actual guardrails, not just "experimental" wording. Operators will try the commands.