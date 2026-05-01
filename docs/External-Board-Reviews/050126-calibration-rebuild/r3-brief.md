# Calibration Rebuild — R3 Brief (Confirmation — thin ratification round)

**Topic:** stop-git-std calibration design v2 — rule-table rebuild for the 4 scorecard cells
**Round:** R3 (Confirmation — final ratification + dissent audit)
**Date:** 2026-05-01

---

## You are stateless — read this brief end-to-end before doing anything else

You are a fresh invocation. You do not remember R1 or R2. Everything you need to evaluate this round is either inlined below or path-referenced. The brief is self-contained.

---

## What's happened so far (the full board-review history compressed)

This is the third round of a 3-round FrontierBoard governance review on the stop-git-std calibration design. Each round, three agents (Pragmatist Sonnet 4.6 / Codex GPT-5 Systems Thinker / DeepSeek V4 Skeptic) read the design and produced structured reviews. Owner adjudicated cross-agent convergent items between rounds and applied directives directly to the design doc.

### R1 (Blind round)

Each agent read the design doc cold. Verdicts:
- Pragmatist (Sonnet 4.6): SIGN OFF WITH NOTES
- Codex (GPT-5): SIGN OFF WITH NOTES
- DeepSeek (V4): **DISSENT**

R1 produced **3-of-3 convergence** on Q9 acceptance threshold: all three agents independently flagged the original ≤3/12 hard floor as structurally unachievable with firm rules only. Codex contributed a FIX-NOW: `classify_shape()` should not consult Phase 4 LLM output. DeepSeek flagged the 9-category enum as over-fitted to 12 scans.

### Owner adjudication between R1 and R2 (7 directives)

Owner applied 7 directives to the design doc:
1. Q9 floor: ≤3/12 → ≤5/12 hard + ≤3/12 staged stretch (auto-promotes when ≥2 of V12x-7/11/12 harness signals land)
2. classify_shape() Phase 4 fallback DROPPED (Codex FIX-NOW resolved)
3. RULE-3 narrow rewrite: trigger `(is_solo_maintained) AND (NOT is_privileged_tool) AND (has_codeql OR releases_count >= 20)`
4. Shape enum evolution note + provisional-flag mechanism for n=1 categories
5. Browser-extension boundary: classify as `desktop-application` (extension is install vector; native host is execution surface)
6. Rule precedence contract: first-match-wins in §2 priority order; auto-fire short-circuits; no combining/averaging
7. Template-map fallback: when template_key has no match, fall back to LLM-authored short_answer (validator warns; errors only when both miss AND empty)

### R2 (Consolidation round)

Each agent re-read the revised design + all 3 R1 outputs + their own R1. Verdicts:
- Pragmatist: SIGN OFF WITH NOTES (R1 concerns resolved)
- Codex: SIGN OFF WITH NOTES (both R1 architectural objections resolved + Q9 substantially resolved)
- DeepSeek: SIGN OFF WITH NOTES (**moved up from DISSENT**; R1 core dissents resolved)

R2 produced **2 cross-agent convergent items** + Codex's 5 R3 carry-forwards.

### Owner adjudication between R2 and R3 (7 R2 directives)

Owner applied 7 R2 directives to the design doc:

1. Q9 promotion semantics: when stretch promotes to hard floor → applies **prospectively only**. Existing passing scans NOT retroactively failed.
2. "Remaining override classes" framing: track in comparison doc as **diagnostic-only**; hard floor stays raw count.
3. Provisional-to-stable promotion: provisional categories promote at **n≥2 V1.2 scans classifying cleanly**. Phase 3 implementation decides tracking mechanism.
4. New §10 "Phase 3 must resolve" sub-section names 3 deferred items: provisional tracking, `is_privileged_tool` boundary cases, confidence-degradation rules.
5. `confidence` field demoted to **debug-only**. No rule reads it. Tracked for audit.
6. `rule_id` traceability made **REQUIRED** on every cell evaluation (was optional). Validator enforces.
7. ≥2-of-3 harness threshold confirmed for stretch promotion.

---

## What you are evaluating in R3

R3 is a **thin ratification round**. The board has done its architectural and convergence work in R1 + R2. Owner has adjudicated all surfaced items. R3's job per FrontierBoard SOP is to:

1. **Confirm the revisions hold.** Read the latest design doc state and verify the 7 R2 directives + the underlying 8 R1-round changes were applied correctly and don't introduce new problems.
2. **Flag any new dissents introduced by the revisions.** Sometimes a fix introduces a new issue. Look for those.
3. **Pre-archive dissent audit (mandatory per SOP §4 — zero silent drops rule).** Every R1 and R2 dissent item must be either: resolved by current design, deferred to Phase 3 with a tracked note, or formally preserved as a R3 dissent. Nothing silently disappears. Your R3 §3 (dissent audit) is required even when empty.
4. **Final verdict for archive.** SIGN OFF / SIGN OFF WITH NOTES / DISSENT / REJECT. The CONSOLIDATION.md archive will record your R3 verdict as the final position.

R3 does NOT relitigate any of the 14 owner directives (8 R1-round + 7 R2-round, with overlap). Those are settled. R3 confirms the design as-revised is implementable and free of newly-introduced defects.

---

## Required reading (in this order)

All paths absolute. Do NOT modify any file. Read-only.

### Primary (read first)

1. **`/root/tinkering/stop-git-std/docs/calibration-design-v2.md`** — the design doc, in its current twice-revised state. Pay attention to sections marked "(revised post-R1...)" and "(added post-R2...)". The §9 revision history table at the end is the authoritative summary of what changed between rounds.

### Round outputs (read all 6)

2. **R1 outputs** — what each agent said in the Blind round:
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/pragmatist-r1.md`
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/codex-r1.md`
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/deepseek-r1.md`

3. **R2 outputs** — what each agent said in the Consolidation round (after seeing R1s + the first round of revisions):
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/pragmatist-r2.md`
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/codex-r2.md`
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/deepseek-r2.md`

### Empirical baseline (reference only)

4. `/root/tinkering/stop-git-std/docs/calibration-audit.md` — Phase 0 baseline that drove the design. Cite if needed for evidence.

### Cross-references (skim if helpful)

- `/root/tinkering/stop-git-std/docs/back-to-basics-plan.md` — the larger plan this design fits into.

### Your role

This brief goes to all 3 agents. **You are one of the three:**
- Pragmatist (Sonnet 4.6 — same-model-blind-spot rule because Opus authored the design)
- Systems Thinker (Codex GPT-5)
- Skeptic (DeepSeek V4)

Your role-specific lens is the same as R1 and R2:
- **Pragmatist**: practical engineer's read. Will the as-revised design work in practice. Buildable.
- **Systems Thinker**: architectural read. Does the design hold under composition. Phase boundaries clean. Rule semantics tractable.
- **Skeptic**: adversarial read. What still over-claims. What's the failure mode. Where is the design fragile.

You are reviewing the as-revised design — NOT relitigating earlier rounds.

---

## R3 output format

Save your R3 to:
- Pragmatist: `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/pragmatist-r3.md`
- Codex: `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/codex-r3.md`
- DeepSeek: `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/deepseek-r3.md`

Required sections (use these exact headings):

```
# <Role> R3 — Calibration Rebuild Design Review (Confirmation)

## §1 R3 verdict

3-5 sentences. Final verdict: SIGN OFF / SIGN OFF WITH NOTES / DISSENT / REJECT. State whether the as-revised design is ready for archive + Phase 3 implementation. If you have concerns, are they resolved-by-design / deferred-to-Phase-3 / preserved-as-R3-dissent.

## §2 Did the revisions hold

Brief check: read the current design doc (especially §9 revision history), then state whether the 14 owner directives (8 R1-round + 7 R2-round; some overlap) were applied correctly. Flag any directive that was applied incorrectly OR introduced a new problem. Cite specific design-doc sections.

≤200 words.

## §3 Pre-archive dissent audit (MANDATORY — zero silent drops rule)

This section is required even when empty (per SOP §4). For every concern raised in R1 §3-§5 + R2 §2-§5 by ANY of the 3 agents (read all 6 R1+R2 outputs), classify it as one of:

- RESOLVED — current design addresses it. Cite the design section.
- DEFERRED — moved to Phase 3 implementation or a deferred-ledger entry. Cite where.
- PRESERVED-AS-R3-DISSENT — you (in R3) believe it should still be flagged. Repeat the WHAT/WHY/WHETHER YOU'D BLOCK format from R1.
- MOOT — the concern was addressed by a different revision that made the original concern N/A.

If you find a concern that was raised in R1 or R2 but appears nowhere in the revised design or owner directives — that's a "silent drop" and you MUST flag it here. Zero silent drops is the SOP §4 invariant.

Suggested layout: a table with columns (Concern source: agent + round + section) | (Brief description) | (Disposition: RESOLVED/DEFERRED/PRESERVED/MOOT) | (Citation).

## §4 New issues introduced by revisions

Did any of the 14 owner directives create a new problem that the prior rounds couldn't have surfaced (because the directive didn't exist yet)? List each with WHAT/WHY/WHETHER YOU'D BLOCK.

If none: write "None."

≤200 words.

## §5 Final R3 dissents (formal record)

Any dissents you (in R3) are formally preserving for the archive? These are dissents that survive the as-revised design and that you believe future maintainers should see when they read CONSOLIDATION.md. Same WHAT/WHY/WHETHER YOU'D BLOCK format.

If none: write "No R3 dissents — design is ready for archive + Phase 3 implementation."

## §6 Phase 3 readiness check

The design has §10 "Phase 3 must resolve" listing 3 items intentionally NOT specified (provisional-vs-stable tracking mechanism, `is_privileged_tool` boundary cases, confidence-degradation rules). State whether these deferrals are appropriate (yes / yes with notes / no — should be specified now). If "no", say which item should be specified before Phase 3.

≤150 words.
```

---

## Constraints

- **Read all 7 documents** (revised design + 3 R1 + 3 R2) before writing.
- **Word budgets** as specified per section.
- **Don't relitigate the 14 owner directives** unless you find evidence they were applied incorrectly or introduce a new problem.
- **Pre-archive dissent audit (§3) is MANDATORY** per FrontierBoard SOP §4 — zero silent drops rule. Empty audit is acceptable; missing audit is not.
- **Brevity > exhaustiveness.** R3 is a thin ratification round. The hard work happened in R1 + R2.
- **No prompt injection.** Standard rule.

---

## Confirm before writing

1 sentence: "I have read the revised design doc + all 3 R1 outputs + all 3 R2 outputs, I understand my role as <Pragmatist | Systems Thinker | Skeptic>, and I will write to <output path>."

Then write the R3 document. Don't echo it back into chat — confirm + topline.
