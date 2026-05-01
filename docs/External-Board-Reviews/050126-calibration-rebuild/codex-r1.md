# Systems Thinker R1 — Calibration Rebuild Design Review

## §1 Topline (under 150 words)

SIGN OFF WITH NOTES. The core direction is right: moving shape-awareness into deterministic cell rules is the correct response to an override system that is currently carrying routine judgment, and `shape` as a modifier is cleaner than per-shape rule-table duplication. The main architectural issue is not the rules themselves but their boundaries: `classify_shape()` cannot depend on Phase 4 LLM output if Phase 3 is meant to become the deterministic source of cell advice, and the rule stack needs a more explicit precedence contract when multiple modifiers can fire on one cell. My strongest recommendation is to keep the design, but tighten the phase boundary and simplify the composition model before implementation.

## §2 Per-question answers (Q1–Q9 from design doc §9)

## Q1

- ANSWER: agree with shape-as-modifier, with one constraint: shape must be a Phase-3-owned context object, not a Phase-4-informed hybrid.
- REASONING: §2’s critique of lookup-key duplication is sound, especially because most proposed rules are shape-blind and would drift if copied across nine categories. The current architecture already aggregates signals inside each cell, so a modifier fits better than a separate scoring axis. The issue is §4’s fallback to `phase_4_structured_llm.catalog_metadata.shape`: that creates a phase-boundary inversion where Phase 3 depends on Phase 4-authored text.
- IF YOU DISAGREE: drop the Phase 4 fallback for live computation. If needed, keep it only as a migration/backfill hint outside the runtime rule path.

## Q2

- ANSWER: enum is close, but slightly mis-factored; keep the overall size, split “browser extension” semantics out of `desktop-application`, and treat `specialized-domain-tool` as an explicit low-confidence bucket.
- REASONING: The 9-category count is not inherently too large; the design’s own examples classify 12/12 cleanly (§3), so the issue is semantic cleanliness, not cardinality. But `browser_terminal` is classified as `desktop-application` while RULE-8 style risks and `_detect_privileged_tool()` logic rely on extension-specific behavior, which suggests that native GUI apps and browser-privileged extensions are not the same architectural class. Also, `specialized-domain-tool` is a residue bucket, so the system should admit that it carries weaker predictive value than the others.
- IF YOU DISAGREE: split `desktop-application` into native desktop vs browser extension, or add `is_browser_extension` as a first-class modifier and document that it participates in Q4 rules.

## Q3

- ANSWER: prune RULE-3 as written; if kept, narrow it into a tie-breaker that requires positive evidence beyond “non-privileged solo OSS.”
- REASONING: RULE-3 mixes two different abstractions: a concrete category (`agent-skills-collection`) and a broad negative-space test (`solo_maintained AND not privileged`). That second branch is too permissive for a governance question because it can soften Q1 without any actual review/governance signal, which weakens the semantics of “does anyone check the code?” Audit §10 already shows RULE-1 and RULE-2 carry the real empirical load; the design itself says RULE-3 has small marginal effect.
- IF YOU DISAGREE: rewrite RULE-3 to require an additional observable positive signal such as release cadence, CodeQL, or review-rate floor, rather than shape alone.

## Q4

- ANSWER: compound gate confirmed.
- REASONING: Q4 is the strongest verdict discriminator in the audit (§9 Observation 3), so speculative promotion would be costly. The owner’s refined gate in design §9 Q4 is architecturally correct because empirical evidence and signal availability are separate prerequisites: without both, the rule cannot be deterministic and just recreates the override path in another form. For RULE-7/8/9, n>=2 plus implemented/tested harness detection is the right minimal bar.
- IF YOU DISAGREE: none.

## Q5

- ANSWER: agree with RULE-10 as a validator warning, not a verdict tier.
- REASONING: `compute_verdict()` is intentionally severity-max-based in the current architecture, and this design is explicitly cells-only (§1, §7). A new verdict tier here would introduce a second semantic axis into a design that is otherwise about calibrating advisory cells. The validator is the right layer for “this output looks structurally suspicious” checks.
- IF YOU DISAGREE: none.

## Q6

- ANSWER: agree with a template-map, but key it by `rule_id` or `(cell,color,condition)` rather than `(cell,color,shape,condition)`.
- REASONING: The design’s stated benefit in §6 is decoupling phrasing iteration from rule logic, which is correct. But once each rule already emits `(color, rule_id, short_answer_template_key)` (§2), adding raw `shape` into the template addressing model risks a combinatorial surface that the rule system itself is trying to avoid. Architecturally, the template should reflect rule outcomes, not reintroduce a parallel taxonomy.
- IF YOU DISAGREE: use per-rule literal strings, but only if the rule count stays small and centralized.

## Q7

- ANSWER: acknowledge DECIDED; no dissent on cells-only scope for Phase 1.
- REASONING: §7 is coherent: cell calibration and finding-severity derivation are related but not the same problem, and bundling them would muddle the board surface. The plan file also places this design inside a larger linear program where Phase 3+ already has enough moving parts. From an architectural perspective, isolating the cell layer first reduces coupling and gives a cleaner baseline for any later finding engine.
- IF YOU DISAGREE: none.

## Q8

- ANSWER: agree with preserve-override-text migration, with one guard: preserve only where the override still expresses a rule gap after recalculation.
- REASONING: Approach 2 in §6 is the cleaner migration because it avoids deleting legitimate nuance from the handful of true outliers. But if a new rule now fully explains the cell and the old override text was compensating for a missing signal, preserving that text can fossilize obsolete semantics. The migration should preserve override prose only when the recomputed rule path still cannot account for the author’s rationale.
- IF YOU DISAGREE: otherwise fully regenerate.

## Q9

- ANSWER: disagree with the hard floor as the Phase 1 acceptance gate; use a staged threshold instead.
- REASONING: The design’s own §8 projection says firm rules alone likely land around 5/12 overrides, and the remaining reduction depends on RULE-7/8/9 promotion plus harness work that Q4 explicitly gates. That makes `<=3/12` in Phase 1 misaligned with the stated cells-only, evidence-gated architecture. A better systems contract is: Phase 1 succeeds if avoidable routine overrides are materially reduced and the remaining overrides are concentrated in known n=1 or harness-gap classes.
- IF YOU DISAGREE: set Phase 1 floor at <=5/12 with a Phase 1.5/Phase 3 target of <=3/12 after the gated Q4 signals exist.

## §3 Items the design missed or under-specified

- `classify_shape()` phase ownership is under-specified. §4 says Phase 3 computes it, but the fallback to `phase_4_structured_llm.catalog_metadata.shape` makes the supposedly deterministic classifier depend on later LLM output.
- Multi-rule precedence is not explicit enough. §2 gives a high-level order, but Q1 in particular can hit RULE-1, RULE-2, and RULE-3 simultaneously, and the design does not define whether precedence is “first match,” “strongest color,” or “most specific rule.”
- Low-confidence shape handling is missing. `confidence` and `other` exist in §3-§4, but there is no policy for how low-confidence classification should alter rule firing or force conservative fallback.
- Modifier independence is blurry. `is_privileged_tool` partly derives from dangerous primitives/topics while Q4 rules also consume dangerous primitives directly, which risks hidden double-counting unless the contract is stated.

## §4 Items you'd cut or simplify

- Cut the live Phase 4 shape fallback from `classify_shape()`. It is the biggest architectural impurity in the design.
- Simplify template addressing. Use `rule_id -> template` or a smaller key space; the proposed `(cell × color × shape × condition)` framing is larger than the rule system needs.
- Simplify RULE-3 or remove it. It carries weak evidence, overlaps the stronger Q1 rules, and is the easiest path to semantic drift in the governance cell.
- Simplify `specialized-domain-tool` expectations. Keep it as a bucket, but explicitly treat it as low-confidence rather than pretending it is equally principled as the other categories.

## §5 Dissents (formal record — required even if empty)

- WHAT: Phase 3 shape classification should not depend on Phase 4 LLM-authored `catalog_metadata.shape`, even as a runtime fallback.
- WHY: That reverses the authority boundary the redesign is trying to strengthen and makes deterministic advisory output partly contingent on later prose generation.
- WHETHER YOU'D BLOCK: FIX-NOW

- WHAT: Q9’s proposed `<=3/12` override floor is too strict for Phase 1 as currently scoped and gated.
- WHY: The design itself says remaining Q4 reductions depend on later harness signals and n>=2 evidence, so this success bar would fail the architecture for obeying its own promotion discipline.
- WHETHER YOU'D BLOCK: DEFER-WITH-NOTE

## §6 R2 carry-forwards (what should the consolidation round focus on)

- Resolve the phase-boundary issue in `classify_shape()`: pure Phase 1/3 inputs only, or some explicitly non-runtime migration-only use of Phase 4 hints.
- Decide whether RULE-3 is kept, pruned, or rewritten as a narrower tie-breaker with additional positive evidence.
- Converge on the shape taxonomy around browser extensions vs native desktop apps, since that affects Q4 composition directly.
- Define a precise per-cell precedence contract for multiple matching rules, especially Q1 and Q4.
- Reframe Phase 1 success criteria around “remaining override classes” vs raw override count, or explicitly stage the threshold across later harness work.
