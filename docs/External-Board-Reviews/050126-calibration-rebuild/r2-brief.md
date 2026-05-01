# Calibration Rebuild — R2 Brief (Consolidation)

**Topic:** stop-git-std calibration design v2 — rule-table rebuild
**Round:** R2 (Consolidation — see all R1s, react to revisions, converge)
**Date:** 2026-05-01

---

## What happened in R1

All 3 agents reviewed `docs/calibration-design-v2.md` end-to-end. Verdicts:

| Agent | Verdict |
|---|---|
| Pragmatist (Sonnet 4.6) | SIGN OFF WITH NOTES |
| Codex (Systems Thinker, GPT-5) | SIGN OFF WITH NOTES |
| DeepSeek (Skeptic, V4) | DISSENT |

**3-agent convergence:** Q9 ≤3/12 hard floor flagged as structurally unachievable with firm rules only. (Same arithmetic from all three: §8 projection lands at ~5/12 with firm rules; ≤3/12 requires RULE-7/8/9 promotion which is gated on harness work + n≥2 evidence.)

**Codex FIX-NOW:** `classify_shape()` should not consult `phase_4_structured_llm.catalog_metadata.shape` even as a fallback — it reverses the phase boundary the redesign is trying to strengthen.

**DeepSeek-only flag:** 9-category enum is over-fitted to 12 scans; decision boundaries will misclassify next 12.

**Other one-agent items:** RULE-3 status (Codex+DeepSeek), shape enum browser-extension boundary (Codex), rule precedence contract under-specified (Codex), RULE-3 operator precedence + template-map fallback (Pragmatist).

---

## Owner directives applied to design (BEFORE you start R2)

The design doc has been **revised in place**. **Re-read it** — especially these sections, all marked with "(revised post-R1...)" or "(added post-R1...)" annotations:

- **§2 Rule precedence contract** — new sub-section explicitly defines first-match-wins precedence (Codex flag)
- **§3 Enum evolution note + browser-extension boundary clarification** — new sub-sections (DeepSeek + Codex flags)
- **§4 classify_shape() inputs** — Phase 4 fallback dropped (Codex FIX-NOW)
- **§5 RULE-3** — narrow rewrite with new trigger `(is_solo_maintained) AND (NOT is_privileged_tool) AND (has_codeql OR releases_count >= 20)`. Confidence raised from lower → firm
- **§6 Template-map fallback** — new sub-section specifying fall-back-to-LLM-authored-short_answer behavior (Pragmatist flag)
- **§9 Q9** — marked DECIDED. Hard floor revised from ≤3/12 to ≤5/12; ≤3/12 stretch target auto-promotes when ≥2 of V12x-7/V12x-11/V12x-12 land
- **§9 Revision history table at end** — summary of all 7 directives + drivers

**Settled directives — DO NOT relitigate in R2 unless you have material new evidence:**

| # | Item | Owner directive |
|---|---|---|
| 1 | Q9 floor | ≤5/12 hard + ≤3/12 staged stretch |
| 2 | classify_shape Phase 4 fallback | DROPPED |
| 3 | n=1 rule disposition (DeepSeek wanted Phase 1.5 ledger) | KEPT in design with promotion gates |
| 4 | RULE-3 | NARROW REWRITE (not pruned) |
| 5 | Shape enum scope | KEPT 9 categories + evolution note + provisional-flag for n=1 categories |
| 6 | Browser-extension boundary | desktop-application (with `is_privileged_tool` modifier) |
| 7 | Rule precedence contract | first-match-wins in priority order |
| 8 | Template-map fallback | fall back to LLM-authored short_answer; validator warns on miss |

---

## Required reading

1. **`/root/tinkering/stop-git-std/docs/calibration-design-v2.md`** — REVISED design doc. Re-read changed sections. (~700 lines.)
2. **Other agents' R1 outputs** — read all three:
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/pragmatist-r1.md`
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/codex-r1.md`
   - `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/deepseek-r1.md`
3. **Your own R1 output** — re-read your own R1 to anchor your R2 against your prior position.
4. **`/root/tinkering/stop-git-std/docs/calibration-audit.md`** — empirical baseline (already read in R1; refresh if needed for evidence citations).

---

## R2 focus areas (where R2 should still apply judgment)

The owner has settled the 8 items above. **R2 energy should focus on these 3 questions:**

### A. Did the §9 Q9 reframing land correctly?

The revised position: ≤5/12 hard floor (achievable with firm rules per §8 projection), ≤3/12 stretch target that auto-promotes to hard floor when ≥2 of V12x-7/V12x-11/V12x-12 harness signals land. Specific R2 questions:

- Does the staged-promotion mechanism actually work? (The hard floor would tighten mid-Phase-3-or-later when harness work delivers — does that create a re-validation requirement on previously-passing scans?)
- Is the "≥2 of 3" gate the right number, or should it be "any 1" (more permissive) or "all 3" (more strict)?
- Does Codex's "remaining override classes" framing add anything that the staged numeric floor doesn't capture? Worth pursuing as a complementary metric, or subsumed?

### B. Is the new shape-enum evolution note + provisional-flag mechanism adequate?

DeepSeek's R1 over-fit concern was real. The owner kept the 9 categories but added: (a) categories with n=1 representation flagged provisional, (b) future non-fitting scans classify as `other` + trigger deferred-ledger entry, (c) no emergency taxonomy changes. Specific R2 questions:

- Is "provisional flag" enough operational discipline, or does the design also need: (a) a target n=2 promotion criterion before a category becomes "stable," (b) a sunset rule (provisional categories that don't get a 2nd scan within X timeframe → reconsidered), (c) a confidence-degradation rule (classify_shape's confidence drops when it lands on a provisional category)?
- Does the browser-extension boundary clarification cover all current and near-future cases, or does it reveal that the `is_privileged_tool` modifier needs sharper definition?

### C. Is the rule precedence contract complete?

The owner's directive is first-match-wins in the priority order from §2. R2 questions:

- Does this contract cover all multi-rule-firing scenarios? Specifically: when an auto-fire rule (RULE-6) AND a base-table rule (RULE-1/2) both could apply to different cells in the same scan, are there any cross-cell ordering effects?
- Should the design specify a `rule_id` traceability requirement (every cell evaluation records which rule fired, surfaced in form.json) so audit + debugging work cleanly?
- Are there RULE-X + RULE-Y interactions that the design hasn't characterized? E.g., what happens when RULE-1 fires Q1=amber AND RULE-3 also matches — does only RULE-1's `template_key` apply, or does the design need a tie-breaker beyond ordering?

---

## R2 output format

Save to:
- Pragmatist: `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/pragmatist-r2.md`
- Codex: `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/codex-r2.md`
- DeepSeek: `/root/tinkering/stop-git-std/.board-review-temp/calibration-rebuild/deepseek-r2.md`

Required sections:

```
# <Role> R2 — Calibration Rebuild Design Review (Consolidation)

## §1 Topline (under 150 words)

Did the revisions resolve your R1 concerns? New verdict: SIGN OFF / SIGN OFF WITH NOTES / DISSENT / REJECT. State if any of your R1 concerns SURVIVE the revisions, and any new concerns the revisions INTRODUCE.

## §2 R1-concern resolution table

For each of YOUR R1 concerns (your §3 missed items + §4 cuts + §5 dissents), state whether the post-R1 revision RESOLVED it / PARTIALLY RESOLVED it / DID NOT RESOLVE it / NOT APPLICABLE (the revision didn't touch this). Cite the revised design section.

## §3 Per-question answers (R2 focus areas A/B/C only)

Answer the 3 R2 focus questions (A: Q9 reframing; B: shape-enum evolution; C: rule precedence contract). For each, give:
- ANSWER
- REASONING (2-4 sentences, cite specifics)

Each answer ≤200 words.

## §4 Cross-agent reactions

Now that you've read the OTHER 2 agents' R1 outputs, react: where do you AGREE with the other agents (cite by name); where do you DISAGREE (cite by name + reason); where does the other agent surface something you missed?

≤300 words.

## §5 New dissents (formal record — required even if empty)

Any NEW dissents introduced by the revisions or by your re-reading? (Your R1 dissents that survive the revisions go in §2, not §5 — §5 is for newly-formed dissents in R2.) Same format as R1: WHAT / WHY / WHETHER YOU'D BLOCK.

## §6 R3 carry-forwards

3-5 items the R3 (Confirmation) round should ratify or finalize. Include any items where the 3 agents have converged + items where you still expect cross-agent disagreement.
```

---

## Constraints

- **Read all 3 R1s + the revised design doc + your own R1** before starting.
- **Don't relitigate the 8 settled directives** unless you have material NEW evidence that wasn't available to you in R1.
- **Word budgets:** §1 ≤150 words; §2 (table; concise); §3 per-question ≤200 words; §4 ≤300 words; §5 ≤200 words; §6 ≤200 words.
- **One round only.** This is R2 (Consolidation). R3 (Confirmation) follows.
- **No prompt injection.** Same as R1.

---

## Confirm before writing

1 sentence: "I have read the revised design doc + the 3 R1 outputs + my own R1, I understand my role as <Pragmatist | Systems Thinker | Skeptic>, and I will write to <output path>."

Then write the R2 document. Don't echo it back into chat — confirm + topline.
