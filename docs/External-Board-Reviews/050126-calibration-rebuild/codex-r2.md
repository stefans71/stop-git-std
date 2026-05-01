# Systems Thinker R2 — Calibration Rebuild Design Review (Consolidation)

## §1 Topline (under 150 words)

SIGN OFF WITH NOTES. The post-R1 revisions resolve my two blocking architectural objections: `classify_shape()` is back on a pure Phase-1/3 input boundary (§4), and rule precedence is now explicit first-match-wins (§2). My R1 Q9 dissent is also substantially resolved by the staged floor; the design no longer asks Phase 1 to fail for respecting its own evidence gates. Two concerns survive as notes rather than dissents: low-confidence/provisional shape outcomes still do not have much downstream behavioral consequence beyond `other` + ledger attention (§3-§4), and the staged Q9 auto-promotion needs an explicit re-validation rule so previously-passing runs are not retroactively judged against a stricter bar. The design is now coherent enough to implement, but R3 should ratify those operational contracts.

## §2 R1-concern resolution table

| R1 concern | R2 status | Notes / revised section |
|---|---|---|
| `classify_shape()` depended on Phase 4 LLM output | RESOLVED | §4 now limits inputs to Phase 1 only and explicitly drops `phase_4_structured_llm.catalog_metadata.shape` fallback. |
| Multi-rule precedence was under-specified | RESOLVED | §2 now states first-match-wins, auto-fire short-circuit, no combining/averaging. |
| Low-confidence shape handling lacked policy | PARTIALLY RESOLVED | §3 adds provisional categories and `other` + deferred-ledger flow; §4 still does not define broader downstream behavior for low-confidence-but-not-`other` results. |
| Modifier independence / hidden double-counting risk was blurry | PARTIALLY RESOLVED | §3-§5 are cleaner about modifiers vs Q4 rule signals, but no explicit non-double-counting contract is stated. |
| Cut live Phase 4 shape fallback | RESOLVED | Same fix as first row; §4 revision fully addresses the FIX-NOW. |
| Simplify template addressing to rule-oriented keys | PARTIALLY RESOLVED | §2 already has rules emit `template_key`; §6 still describes `(cell × color × shape × condition)` conceptually, though the examples are effectively rule-oriented. |
| Simplify or remove RULE-3 | RESOLVED | §5 rewrites RULE-3 into a narrow positive-evidence tie-breaker, which matches my R1 fallback position. |
| Treat `specialized-domain-tool` as lower-confidence bucket | PARTIALLY RESOLVED | §3 evolution note/provisional mechanism helps globally, but `specialized-domain-tool` is not explicitly marked lower-confidence than stable categories. |
| Q9 `<=3/12` Phase-1 hard floor was too strict | RESOLVED | §9 now uses `<=5/12` hard floor with `<=3/12` staged promotion tied to harness delivery. |

## §3 Per-question answers (R2 focus areas A/B/C only)

### A. Q9 reframing

- ANSWER: Mostly yes. The `<=5/12` hard floor + `<=3/12` staged stretch is the right reframing, and the `>=2 of 3` gate is the right threshold. Keep my R1 “remaining override classes” framing only as a secondary reporting metric, not as the primary acceptance gate.
- REASONING: §8 and §9 now align the acceptance bar with what firm rules can actually deliver, which removes the earlier structural contradiction. `Any 1` would be too permissive because a single harness signal could collapse one narrow override class without proving the broader Q4 backlog is ready; `all 3` is too strict because the three candidate classes are independent. The missing operational detail is re-validation: once the stretch auto-promotes, new runs should be judged against `<=3/12`, but previously accepted Phase-1 rerenders should remain valid unless rerun under the new harness baseline. “Remaining override classes” still adds diagnostic value because it distinguishes five overrides from one root cause vs five truly different misses, but the numeric floor should remain the formal gate.

### B. Shape-enum evolution

- ANSWER: Adequate with two clarifications for R3: provisional categories should have an explicit n=2 promotion-to-stable rule, and landing on a provisional category should degrade classification confidence. A sunset rule is not necessary yet.
- REASONING: §3’s added evolution note is the right discipline: no emergency taxonomy churn, classify uncertain future cases as `other`, and force a ledger review. But “provisional” only matters if it has an operational meaning. The cleanest contract is: categories with only one in-catalog confirming scan stay provisional until a second confirming scan lands, and `classify_shape()` should return `confidence="medium"` or `low` when it matches one of them. I do not think a time-based sunset is needed now; evidence volume, not elapsed time, is the relevant driver. The browser-extension clarification is directionally sufficient, but `is_privileged_tool` should be sharpened in implementation notes to explicitly include broad extension permissions and native-host execution surfaces.

### C. Rule precedence contract

- ANSWER: Nearly complete. The design should ratify `rule_id` traceability as required, and it should state that precedence is per-cell only, with no cross-cell ordering effects.
- REASONING: §2 now answers the main same-cell ambiguity: first-match-wins, deterministic, no combining. For the specific examples, RULE-6 on Q4 and RULE-1/2 on Q1 do not compete because they target different cells; evaluation order across cells therefore should be irrelevant as long as each cell records its own winner. Where Q1 has multiple matches, ordering already answers the tie: RULE-3 should not overwrite RULE-1 or RULE-2 once either fires. The remaining gap is contractual, not conceptual: §10 treats `rule_id` as an optional schema addition, but the traceability promise in §2 works much better if every evaluated cell records the winning rule (or explicit fallback marker) in machine-readable output.

## §4 Cross-agent reactions

I agree with Pragmatist on two important points: the original Q9 floor was structurally mis-set, and template fallback needed to be explicit. The revised design adopted both, which materially improved implementation clarity.

I also agree with DeepSeek that the enum was derived from a thin sample and needed an evolution discipline. The new provisional-category note is a reasonable answer to that risk without reopening the settled scope.

I disagree with DeepSeek’s R1 call to collapse to six categories. That would have hidden exactly the kind of shape distinctions the redesign is trying to make legible, especially around agent-oriented installs and install-script fetchers. The owner’s compromise of keeping nine categories but marking thinly evidenced ones provisional is the better systems tradeoff.

I disagree with Pragmatist’s R1 suggestion to prune RULE-3 entirely. The revised RULE-3 is no longer a vague “non-privileged solo OSS” softener; it is a positive-evidence tie-breaker, which is a materially different rule and worth keeping.

What I missed in R1 that the others surfaced: DeepSeek was right to push on explicit provisional/stability handling for the enum, and Pragmatist was right that template fallback behavior was an implementation blocker, not just a polish issue.

## §5 New dissents (formal record — required even if empty)

No new dissents.

New notes only:
- WHAT: staged Q9 auto-promotion needs a “prospective only unless rerun” re-validation contract.
- WHY: without it, a scan could pass under `<=5/12` and later be judged as if it had failed under `<=3/12` despite no code or corpus change.
- WHETHER YOU'D BLOCK: no; R3 should ratify it.

- WHAT: `rule_id` traceability should move from optional schema addition to expected output.
- WHY: the precedence contract is much easier to audit and debug if each cell records the winning rule or fallback path.
- WHETHER YOU'D BLOCK: no; strong recommendation for R3.

## §6 R3 carry-forwards

1. Ratify the Q9 staged-floor operational contract: when `<=3/12` auto-promotes, does it apply prospectively only, or require a full rerender/revalidation pass?
2. Ratify that `>=2 of 3` harness signals is the right promotion threshold and that “remaining override classes” is diagnostic telemetry, not the primary gate.
3. Finalize provisional-category behavior: explicit n=2 promotion-to-stable and confidence degradation when a scan lands on a provisional category.
4. Finalize `is_privileged_tool` implementation notes for browser extensions, native hosts, terminal emulators, and similar boundary cases.
5. Ratify `rule_id` traceability as a required per-cell output (including explicit fallback marker) so the precedence contract is fully auditable.
