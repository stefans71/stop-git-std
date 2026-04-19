# Board Review R2 (Consolidation) — Step G Kickoff / U-1

**Date:** 2026-04-18
**Reviewing:** U-1 approach + owner's revised proposal incorporating R1 feedback
**Round:** R2 Consolidation — each agent sees all three R1 responses verbatim, votes on converged FIX NOW items and owner's revised draft, resolves 3 splits
**Rounds planned:** R1 Blind done → R2 Consolidation (this) → R3 Confirmation

**STATELESS.** Read fresh. All R1 content inlined below.

---

## 1. Project context (self-contained)

**stop-git-std** is an LLM-driven GitHub repo security auditor. 9-phase pipeline. 8/8/4 classification. Phase 7 renderer plan A→G — Steps A-F done (`ce698d4`). Step G is next — requires operator workflow documented. U-1 is that documentation integration.

**Scope:** update 3 repo-level docs (CLAUDE.md, docs/SCANNER-OPERATOR-GUIDE.md, docs/Scan-Readme.md) + 1-line prompt cross-ref, adopting additive strategy (V2.4 primary, V2.5-preview experimental for Step G operators).

R1 brief at `/root/tinkering/stop-git-std/.board-review-temp/step-g-kickoff/r1-brief.md`. Prior-round records same directory.

---

## 2. R1 Verdict matrix

| Agent | R1 Verdict |
|---|---|
| Pragmatist | SIGN OFF WITH DISSENTS — 4 FIX NOW |
| Codex | SIGN OFF WITH DISSENTS — 4 FIX NOW (different framing) |
| DeepSeek | SIGN OFF WITH DISSENTS — 4 FIX NOW |

**All three agree the additive strategy is correct.** None argue for flipping Path B to primary before Step G. None argue for leaving Path B out of docs entirely.

---

## 3. R1 full text (inlined)

### 3.1 — Pragmatist R1 verbatim

```
Verdict: SIGN OFF WITH DISSENTS

Q1 Additive: YES. Unifying would invert the acceptance gate.
   Sharpening: CLAUDE.md already uses "Path A/B" for delegation (continuous vs delegated).
   Introducing "Path V2.4/V2.5-preview" creates name collision. Rename delegation to
   "Mode A/B" or "Option A/B" so "Path" is reserved for rendering pipeline.

Q2 Prompt: Minimal cross-reference at line ~1106. Not zero-change, not rewrite.

Q3 Catalog: Leave 10 scans alone. Add methodology column to scanner-catalog.md
   distinguishing V2.4-pipeline from V2.5-preview-pipeline entries.

Q4.1 Package guide parity: Accept drift as V2.4→V2.5 boundary.
Q4.2 Validator sync (FX-3b): FIX NOW in PARALLEL COMMIT before U-1. The caveman shape
   specifically uses curl-pipe patterns that FX-3b would corrupt. Not theoretical.
Q4.3 Full package refresh: Post-Step-G future work.

Q5 Safety: Current disclaimer sufficient for this operator profile. No env var needed.
   One rewording: "Use this path only when explicitly running Step G of the renderer
   validation plan" (not "if you are Step G's operator").

Q6 Rollback: Path A continues working throughout. Add to §8.8: Step G success requires
   rendered output structurally comparable to V2.4 scan of same repo, not just
   validator-clean. Validator clean is necessary but not sufficient.

Q7 Blind spots:
  - FIX NOW: Operator can't produce form.json from scratch. §8.8 points at fixture
    but there's no bridge from 1508-line prompt to 9-phase form. Need mapping table:
    Phase 1 raw_capture ← gh api calls per prompt Steps 1-4
    Phase 2 validation ← Steps 5-6
    Phase 3 computed ← derived from 1+2
    Phases 4-5 ← LLM-authored
  - INFO: CSS line count 816→824 drift in CLAUDE.md
  - INFO: Path A/B name collision (see Q1)
  - INFO: Scan-Readme.md line-count annotation drift after §8.8 added

FIX NOW summary:
1. Rename delegation Path A/B
2. Add form.json authoring bridge (mapping table) to §8.8
3. FX-3b package validator sync (parallel commit)
4. Structural-parity criterion in §8.8

Bottom line: Approach sound. Ship additive. Fix form.json bridge and name collision
before commit lands. Track FX-3b sync as immediate follow-on.
```

### 3.2 — Codex R1 verbatim

```
Verdict: SIGN OFF WITH DISSENTS

Q1 Additive is right. Step G exists precisely because JSON-first is not yet live-
   validated. Architecturally, DO NOT present as two permanent "paths." Use two-axis:
     - Execution mode: continuous vs delegated
     - Rendering pipeline: V2.4 direct-authoring vs V2.5-preview JSON-first
   Preserves current Guide semantics in §8 and avoids a second Path A/B taxonomy.

Q2 Minimal prompt update. Output-format section at lines 1106, 1170, 1200, 1353 IS the
   contract. Short note saying this contract is realized either directly by LLM or via
   scan-schema.json + renderers is the cleanest unification layer.

Q3 Leave 10 catalog scans. Catalog gains methodology/version marker.

Q4.1 Accept repo/package drift as explicit version boundary.
Q4.2 Package validator drift scheduled urgently — FX-3b is latent bug, not renderer-only.
   Leaving it indefinitely in package is architecturally inconsistent.
Q4.3 Full refresh post-Step-G.

Q5 Current wording not strong enough. I would not require env var, but I would require
   stronger doc gating — three explicit warnings:
     - "Use only for Step G acceptance runs"
     - "Do not use for catalog scans or user-facing production scans"
     - "Preview pipeline; output not yet considered catalog-grade until Step G passes"
   These warnings in CLAUDE.md, Operator Guide, AND Scan-Readme.md.

Q6 Rollback model:
   - Path A remains only production/default path throughout
   - If Step G fails, revert docs to REMOVE V2.5-preview from entry-point docs, or
     QUARANTINE them into a Step G appendix
   - Do not mutate package
   - Treat failed fixtures as test artifacts, not operator exemplars
   Cleaner than keeping a known-bad preview path in main operator flow.

Q7 Blind spots:
  - Path A/B terminology collision — biggest issue
  - §8.4 already says rendered output contract lives in the prompt (SCANNER-OPERATOR-
    GUIDE.md:347). If U-1 adds schema/renderer docs without updating §8.4, the Guide
    becomes self-contradictory
  - §8.8 doesn't explain form.json authoring; "reference zustand-form.json" is not enough
  - CLAUDE.md currently uses "Path B" for delegation (CLAUDE.md:49). Reusing will break
    the wizard

Schema alignment on output-format spec (V1.1 vs prompt):
  - Schema has: verdict_exhibits, scorecard cells, action steps, findings, executable
    inventory, PR sample, repo vitals, coverage, evidence
  - NOT fully modeled: Scanner Integrity section 00 hit-level file/line/raw-content
    structure; Section 08 methodology (only version modeled, rest implicit/static)
  - Schema is adequate as renderer input, but NOT yet canonical formalization of full
    prompt output spec

Additional blind spot: Scan-Readme.md is stale (V2.3, 6/10 catalog, old Path A/B
semantics). Cannot remain minor afterthought.

FIX NOW:
  - Don't reuse Path A/B for pipeline variants
  - Update prompt with one-line output-contract cross-reference
  - Clarify preview is Step-G-only and non-production (triple warnings)
  - Fix §8.4 wording so prompt/schema/renderers are not in conflict

DEFER:
  - Full package refresh to V2.5 after Step G
  - Schema hardening for explicit Scanner Integrity hit structure

INFO:
  - Repo/package guide parity can be intentionally broken, but only as explicit V2.4
    package vs V2.5-preview repo boundary
```

### 3.3 — DeepSeek R1 verbatim

```
Verdict: SIGN OFF WITH DISSENTS

Q1 Additive is correct with caveats:
   - Path B explicitly gated (more than "experimental" warnings)
   - Clear migration trigger defined (when does Path B become primary?)
   - Rollback plan documented in §8.8
   Dissent: "experimental" label insufficient. Path B should require env var or
   command-line flag: export STOP_GIT_STD_EXPERIMENTAL=1

Q2 Minimal cross-reference only, as owner proposes.

Q3 Leave 10 as V2.4 artifacts. Catalog documents.
   Critical issue: These 10 scans have NEVER been validated against the fixed
   validator (missing FX-3b). Any shell-glob evidence may have been corrupted by the
   comment-strip bug. Latent data corruption.

Q4.1 Accept drift as V2.4-to-V2.5 boundary. Updating both in lockstep creates confusion.
Q4.2 FIX NOW. Missing FX-3 + FX-3b is a REAL bug affecting V2.4 scans. The comment-
   strip bug (FX-3b) eats shell-glob-containing evidence. Affects existing scans
   (caveman has shell globs). Package users deserve the fix.
   Action: Sync validator fixes to package BEFORE U-1 ships. Bug fix, not feature addition.
Q4.3 Post-Step G separate work.

Q5 MAJOR SAFETY CONCERN. Proposed "experimental — Step G validation in progress"
   wording is weak. Operators will see concrete commands and try them.
   Failure mode: Operator runs Path B on non-fixtured repo (e.g., fd CLI binary), hits
   schema edge case, produces invalid JSON, can't debug because §8.8 provides no
   guidance on form.json authoring.
   Fix: Add explicit guardrails:
     1. Environment variable: export STOP_GIT_STD_EXPERIMENTAL=1 to enable Path B
     2. Shape validation warning: "Only validated for 3 shapes: JS library, curl-pipe
        installer, agentic platform"
     3. Debug guidance: What to do when form.json validation fails

Q6 Owner proposal inadequate. "Path B docs update to reflect V1.2" assumes schema
   evolution is trivial. Rollback plan needed in §8.8:
     - "If Step G fails, Path B documentation will be marked DEPRECATED until schema
       issues resolved"
     - "Operators should revert to Path V2.4"
     - "Check docs/External-Board-Reviews/ for Step G status"

Q7 Multiple critical blind spots:
   1. NO guidance on form.json authoring (same as P+C)
   2. Fixture provenance gap — 3 of 6 catalog shapes covered. Missing: CLI binary (fd),
      Claude Code skills (gstack), web app (postiz-app), Python platform (hermes-agent)
   3. Validator bug affects existing catalog (data corruption risk)
   4. No error handling guidance in §8.8
   5. CSS line count discrepancy (816 vs 824)

Additional Skeptic-specific:
   1. Data corruption in catalog scans — 10 scans validated with buggy validator. Any
      shell-glob evidence corrupted. Example: caveman scan with /plugins/*/hooks/*.js
      patterns may be truncated.
   2. Path B creates two classes of operators; new operators may choose Path B
      ("deterministic renderer" sounds more automated)
   3. Documentation rot risk — "Step G validation in progress" has no expiration
   4. Missing shape coverage warning
   5. No provenance for back-authored fixtures (are they exact reconstructions or
      approximations?)

FIX NOW (blocking U-1):
  1. Sync validator fixes to package (FX-3b)
  2. Add explicit guardrails for Path B (env var + shape warnings)
  3. Fix CSS line count inconsistency
  4. Add form.json authoring guidance

DEFER: Full package refresh, catalog re-validation, provenance tagging

Primary dissent: Package validator must be fixed (FX-3b) because it's a real bug
affecting V2.4 users. This isn't "package maintenance" — it's bug fix for existing
functionality.
Secondary dissent: Path B documentation needs actual guardrails, not just "experimental"
wording.
```

---

## 4. Owner's revised proposal (incorporating R1 feedback)

### 4.1 — Renaming (resolves Pragmatist + Codex unanimous FIX NOW)

**Adopt Codex's two-axis terminology:**
- **Execution mode:** *continuous* (run yourself) vs *delegated* (background agent)
- **Rendering pipeline:** *V2.4 direct-authoring* vs *V2.5-preview JSON-first*

In CLAUDE.md wizard:
- Rename Q2's "Path A/Path B" → "Execution mode: continuous vs delegated"
- Rename Q3 to a new Q3 on "Rendering pipeline: V2.4 (recommended) vs V2.5-preview (Step G operators only)"

In SCANNER-OPERATOR-GUIDE.md §8.3:
- Rename "Path A/B" to "continuous/delegated" throughout (it currently uses Path A/B there too — check lines 297 and 311)

This resolves the biggest blind spot without requiring the less-familiar "Mode A/B" language.

### 4.2 — §8.4 wording fix (resolves Codex FIX NOW + §8.4 contradiction)

Current §8.4:
> "The rendered output's required structural elements are specified by the V2.4 prompt..."

Revised §8.4:
> "The rendered output's required structural elements are specified by the V2.4 prompt (`repo-deep-dive-prompt.md`, output-format section lines ~1106-1490). In the V2.5-preview pipeline, this specification is also realized via `docs/scan-schema.json` V1.1 (schema) + Jinja2 templates at `docs/templates/*.md.j2` + `docs/templates-html/*.html.j2` (renderer output). Both pipelines produce output conforming to the same prompt specification."

### 4.3 — form.json authoring bridge (resolves unanimous FIX NOW)

Add to §8.8 a phase-to-prompt mapping table:

| Form phase | Source | Prompt reference |
|---|---|---|
| `phase_1_raw_capture` | `gh api` calls + OSSF + osv.dev | Prompt Pre-flight + Steps 1-4 |
| `phase_2_validation` | Sanity checks on Phase 1 outputs | Prompt Download + extraction + symlink-strip |
| `phase_3_computed` | Python compute functions (`compute.py`) | Deterministic derivation from Phase 1 |
| `phase_4_structured_llm` | LLM produces enum/template-constrained fields | Prompt Steps A/B/C + scorecard calibration |
| `phase_4b_computed` | Python derives verdict from findings | Deterministic from Phase 4 findings |
| `phase_5_prose_llm` | LLM writes what_this_means / body_paragraphs | Prompt output-format spec section Finding cards |
| `phase_6_assembly` | Final JSON merge, provenance tags | N/A (assembly step) |
| `scan_sign_off` | Human or operator-agent approval | Prompt "Required" sections |

Plus a step-by-step checklist for converting a findings-bundle.md into a form.json (3-5 bullets).

### 4.4 — Path B gating (resolves split: 3 different approaches)

Codex's three warnings inline at the top of the V2.5-preview section, in CLAUDE.md, Operator Guide, AND Scan-Readme.md. NO env var (DeepSeek's proposal rejected as overkill for the project's operator profile — LLMs and technically fluent humans).

Wording (inserted atop §8.8):
> **V2.5-preview — Step G validation only. Not for production scans.**
> - Use only for Step G acceptance runs (`docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` §"Step G — C7 acceptance matrix").
> - Do NOT use for catalog scans or user-facing production scans. Use V2.4 (`#### Workflow V2.4` section above) for those.
> - Preview pipeline; output not yet considered catalog-grade until Step G passes.
> - Only validated against 3 shapes: JS library (`tests/fixtures/zustand-form.json`), curl-pipe installer (`caveman-form.json`), agentic platform monorepo (`archon-subset-form.json`). CLI-binary, Claude-Code-skills, web-app, and Python-platform shapes NOT yet fixtured.
> - Last reviewed: 2026-04-18. See `docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md` for most recent board status.

### 4.5 — Rollback plan in §8.8 (resolves Codex + DeepSeek)

If Step G fails:
1. Revert the V2.5-preview subsections from CLAUDE.md's wizard + Operator Guide §8.8, OR quarantine into a Step G appendix at the bottom of the Operator Guide (not in main flow).
2. V2.4 continues as the only production/default path.
3. Any failed Step G form.json files are marked `_fixture_provenance: "step-g-failed-artifact"` and kept as test artifacts, NOT as operator exemplars.
4. Do not mutate `github-scan-package-V2/`.
5. Schema revision (to V1.2 or wherever) happens in a separate cycle; §8.8 is held DEPRECATED during that cycle.

### 4.6 — Prompt cross-reference (resolves unanimous minimal update)

Add one line at the top of `docs/repo-deep-dive-prompt.md` §"Markdown file structure" (line 1093) or "Catalog metadata" (line 1106):
> **Output contract.** The MD structure specified below is the canonical report format. In the V2.5-preview pipeline, this contract is realized via `docs/scan-schema.json` V1.1 + `docs/render-md.py` / `docs/render-html.py`. Both pipelines must produce output conforming to this spec.

### 4.7 — Catalog methodology column (resolves Pragmatist Q3)

Add a column to `docs/scanner-catalog.md` table distinguishing V2.4-pipeline vs V2.5-preview-pipeline entries. Currently all 10 entries are V2.4. Step G's first live scan becomes the first V2.5-preview entry.

### 4.8 — Structural-parity criterion (Pragmatist addition to §8.8)

Add to §8.8 Step G success criterion: "Rendered output must be reviewed against the V2.4 scan of the same repo (where one exists in the catalog) for structural parity. Validator-clean is necessary but not sufficient."

### 4.9 — CSS line count fix (INFO)

Update CLAUDE.md line 46: `816 lines` → `824 lines`. Verify by `wc -l docs/scanner-design-system.css`.

### 4.10 — FX-3b package validator sync

**Owner directive:** PARALLEL COMMIT before U-1 lands (Pragmatist + Codex 2-1 majority over DeepSeek's blocks-U-1 position). Rationale:
- The FX-3b bug fix is self-contained — single-file change to `github-scan-package-V2/validate-scanner-report.py` syncing the validator fix from the repo.
- Not coupled to U-1's doc changes.
- Separating preserves clean commit history and makes revert paths independent.
- If the parallel commit runs into issues, U-1 can still ship — FX-3b affects V2.4 package users only.

Commit order: (1) FX-3b package validator sync, (2) U-1 doc updates.

DeepSeek's BLOCK-U-1 interpretation is accepted insofar as BOTH commits land before any Step G scan runs. The parallel-ness is a packaging concern, not a sequencing concern.

### 4.11 — New item: U-10 catalog re-validation (from DeepSeek's skeptic-specific blind spot)

DeepSeek surfaced that the 10 existing catalog scans were validated with the buggy validator. Shell-glob evidence in caveman (and possibly other scans) may have been silently corrupted during validator runs.

**Proposed U-10:** Re-run `validate-scanner-report.py --parity` on all 10 existing MD/HTML catalog pairs with the fixed validator. If any scans show new parity errors (vs previously "clean"), those are scans where the comment-strip bug was hiding real divergence. Document findings.

**Timing:** DEFER post-U-1, but before Step G if possible. Low effort (~30 min), could catch real bugs.

---

## 5. Splits still to resolve in R2

### Split 5.1 — FX-3b timing
- Pragmatist + Codex: parallel commit (not blocking U-1)
- DeepSeek: blocks U-1 until FX-3b syncs to package
- Owner proposal: parallel commit BEFORE U-1 lands (both hit before Step G)
- **R2 question:** confirm owner proposal or argue for different sequencing

### Split 5.2 — Gating mechanism
- Pragmatist: disclaimer wording + rewording of one sentence
- Codex: three explicit warnings in CLAUDE.md + Operator Guide + Scan-Readme.md
- DeepSeek: environment variable `STOP_GIT_STD_EXPERIMENTAL=1` + shape validation warning
- Owner proposal: Codex's three warnings + "Only validated against 3 shapes" warning + "Last reviewed" date. NO env var.
- **R2 question:** confirm owner proposal or argue for env var

### Split 5.3 — Scan-Readme.md handling
- Codex: Scan-Readme.md cannot remain minor afterthought; staleness is real
- Pragmatist: note line-count drift, handle when snippet authored post-board
- DeepSeek: silent on this
- Owner proposal: include Scan-Readme.md in U-1 scope, with a snippet drafted now (not post-board). Bump its top-line version marker from V2.3 to V2.4, fix the 6/10 → 10/10 catalog count, add a "V2.5-preview in active development — Step G pending" note.
- **R2 question:** confirm owner proposal or argue against Scan-Readme.md inclusion in U-1

---

## 6. What R2 must produce

Under 1500 words (R2 is narrower than R1):

### Verdict (R2)
SIGN OFF | SIGN OFF WITH DISSENTS | BLOCK. State if changed from R1.

### Response to each owner-revised item (§4.1-4.11)
For each: **SECOND** | **ADJUST (with reason)** | **REJECT (with reason)**. If you ADJUST, name the specific change.

### Resolution of the 3 splits (§5.1-5.3)
One position per split. If your R1 position was different, say explicitly why you moved.

### Any new FIX NOW items you see
Only if NEW — do not re-litigate R1 items unless you have concrete new evidence.

### Approval for owner to proceed to R3
Yes/No. If yes, R3 will be the confirmation round after owner applies the agreed changes.

---

## 7. Files to READ

- `/root/tinkering/stop-git-std/.board-review-temp/step-g-kickoff/r1-brief.md` (the R1 brief)
- `/root/tinkering/stop-git-std/.board-review-temp/step-g-kickoff/pragmatist-r1.md`
- `/root/tinkering/stop-git-std/.board-review-temp/step-g-kickoff/codex-r1.md`
- `/root/tinkering/stop-git-std/.board-review-temp/step-g-kickoff/deepseek-r1.md`
- `/root/tinkering/stop-git-std/CLAUDE.md` (103 lines)
- `/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md` (§8, lines 297-420)
- `/root/tinkering/stop-git-std/docs/Scan-Readme.md` (full)
- `/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md` (lines 1093-1106 for output-format intro)
