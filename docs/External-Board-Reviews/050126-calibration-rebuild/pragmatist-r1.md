# Pragmatist R1 — Calibration Rebuild Design Review

**Role:** Pragmatist (Claude Sonnet 4.6 — same-model-blind-spot rule; Opus authored the design)
**Round:** R1 (Blind)
**Date:** 2026-04-30

---

## §1 Topline (under 150 words)

SIGN OFF WITH NOTES. The design is sound, audit-grounded, and implementable in a single focused sprint. The core call — shape-as-modifier, unified rule table, template-map short answers — is right for the codebase's current scale and avoids premature abstraction. The firm rules (RULE-1 through RULE-6) have direct empirical anchors and will ship cleanly. The main practical risk is the Q9 acceptance floor: the §8 projection explicitly shows that firm-rules-only puts override rate at ~5/12, which *fails* the ≤3/12 hard floor. That math needs resolving before Phase 3 starts — either the floor loosens, RULE-7/8/9 compound gates are unblocked faster, or additional firm rules are found. The template-map approach also underspecifies fallback behavior (no template key matched — what does the renderer emit?). Both gaps are addressable in Phase 3 without redesign.

---

## §2 Per-question answers (Q1–Q9 from design doc §9)

### Q1 — Shape-as-modifier architectural call

**ANSWER:** Agree with shape-as-modifier.

**REASONING:** The audit data strongly supports it: 6 of 10 audit-derived rules are shape-blind (RULE-1/2/4/5/6/10), meaning a lookup-key table would produce 9×6 = 54 identical rule copies with no semantic difference. The existing `compute_scorecard_cells()` function in `docs/compute.py` already passes flat signal parameters; the modifier approach extends that cleanly by adding a `shape` argument to each `evaluate_qN()` function. The "acceptable cost" of passing unused `shape` to shape-blind rules is trivially low. The alternative (scoring dimension) doesn't fit because `compute_verdict` is findings-severity-driven, not cell-driven — confirmed by audit §3 and design §2.

---

### Q2 — 9-category enum scope

**ANSWER:** Approve as-is; one naming note worth flagging.

**REASONING:** The 12/12 clean classification in design §3 is the right acceptance test. The categories draw sensible boundaries — `install-script-fetcher` vs `cli-binary` vs `library-package` are genuinely distinct risk surfaces. One practical concern: `specialized-domain-tool` is defined by what it is *not* (none of the above + domain keyword), making it the ambiguous bucket. Three of the 12 scans land there (freerouting, Kronos, markitdown). As the catalog grows, this bucket will attract classification debt. A promotion gate (e.g., "when ≥3 scans of a domain type enter, split into its own shape") would be worth noting in the design, but isn't blocking for Phase 3 at n=12.

---

### Q3 — RULE-3 keep-or-drop

**ANSWER:** Prune RULE-3 from the initial implementation; preserve in design doc as a documented candidate.

**REASONING:** The design itself (§5, RULE-3 rationale) admits RULE-3's marginal effect is small because RULE-1 and RULE-2 cover most of the same ground. The trigger `shape.category == "agent-skills-collection" OR shape.is_solo_maintained AND shape.is_privileged_tool == False` also has an operator-precedence ambiguity: Python evaluates `AND` before `OR`, so this reads as `(agent-skills-collection) OR (solo AND not privileged)` — which would match non-solo, non-privileged repos in any shape category. That's almost certainly wrong and needs parentheses either way. More importantly: the evidence (n=2, kamal + ghostty) is already covered by RULE-1, so RULE-3 would be a no-op dead branch in the rule table for the current catalog. Add a comment in the rule file noting the candidate and promotion gate (n≥2 genuine RULE-3-only cases), don't implement the branch yet.

---

### Q4 — RULE-7/8/9 compound promotion gate

**ANSWER:** Agree with the compound gate (n≥2 confirming scans AND harness signal implemented + tested).

**REASONING:** The compound gate is the right call precisely because promoting a rule before the harness signal exists creates a dead rule — the rule can't fire programmatically so every invocation falls through to override, defeating the design's override-reduction goal. This is a practical implementation dependency the design correctly identifies. The one concern: the compound gate means RULE-7/8/9 won't promote quickly (harness signal work is separate backlog items V12x-7/11/12 per design §5), which directly feeds the Q9 floor tension. The board should surface this dependency explicitly in R2 so the owner can decide whether to schedule V12x-7/11/12 in parallel with Phase 3.

---

### Q5 — RULE-10 as validator warning vs verdict tier

**ANSWER:** Agree with validator warning; no dissent on keeping it at warning level.

**REASONING:** The design's rationale is sound: the structural situation (governance-only Critical) currently doesn't appear in any of the 27 catalog scans, so this is prophylactic. A validator warning is the correct minimum intervention — it surfaces the question without forcing schema changes, new verdict formatting branches, or downstream renderer updates. The warning message proposed in §5 is specific enough to be actionable. One implementation note: the check lives in `validate-scanner-report.py --form` mode. The design should confirm this runs during the Phase 5 re-render pipeline, not just at authoring time, to catch any regression introduced by the new rules.

---

### Q6 — Cell short_answer template-map

**ANSWER:** Approve the template-map approach; one gap to address.

**REASONING:** Template-map is strictly better than per-rule literal strings for the stated reason (phrasing can iterate without rule-table churn). The proposed `docs/scorecard-templates.json` schema looks clean. The practical gap: the design doesn't specify what happens when no rule fires and the fallback is the existing advisory color. Does the renderer use the old free-form short_answer from the existing compute logic? Does it emit a sentinel string? The rule evaluation order in §2 ends with "fallback to current advisory color" — but the current advisory short_answer is a string generated inside `compute_scorecard_cells()` (e.g., `"No"` or `"Partly"`) and won't have a template key. The migration approach in §6 needs an explicit fallback: either a `default.*` template key per cell×color, or "preserve existing advisory string as-is when no rule fires."

---

### Q7 — Scope: cells only (DECIDED)

**ANSWER:** Acknowledge as decided; no disagreement.

**REASONING:** The cells-only vs cells+finding-severities question was correctly resolved for this phase. The audit covered cells only (design §7 states this explicitly), and the scope estimate (2-3× the work) is credible based on what finding-severity programmaticization would require (finding-pattern catalog, `compute_findings()` function, LLM narrative-only path, re-classification of 27 catalog findings). Phase 1.5 sequencing is appropriate.

---

### Q8 — Migration approach (preserve LLM override text; regenerate from template otherwise)

**ANSWER:** Agree with approach 2 (preserve LLM text where override fired; regenerate otherwise).

**REASONING:** This is the practical-engineer default: minimize data loss from scan-specific nuance, maximize consistency on the common case. The implementation is straightforward — check `phase_4_structured_llm.scorecard_cells.<q>.override_reason` is non-null; if yes, preserve; if no, regenerate from template. One caution: the migration script needs to handle the case where the existing short_answer was NOT from an override (i.e., the LLM authored a cell color matching the advisory, but with nuanced language) — in that case approach 2 would regenerate from template and lose any LLM nuance. This is probably fine (the LLM nuance on non-overridden cells is likely minor), but should be explicitly acknowledged in the comparison doc (§8: "non-override, LLM-nuance-text cells — replaced with template text").

---

### Q9 — Acceptance threshold (≤3/12 hard floor)

**ANSWER:** The ≤3/12 floor is problematic given the §8 projections. Propose a two-tier acceptance structure.

**REASONING:** The design's own §8 projection is explicit: firm rules only (RULE-1 through RULE-6) get override rate to ~5/12, which *fails* the ≤3/12 floor. Reaching ≤3/12 requires RULE-7/8/9 to promote, which requires (a) n≥2 confirming scans AND (b) harness signals implemented — neither of which is a Phase 3 deliverable. This creates a scenario where Phase 3 ships a complete, correct implementation but fails its own acceptance criteria because the catalog hasn't grown and harness work is pending. Proposed two-tier structure:

- **Phase 3 acceptance (minimum bar):** firm rules (RULE-1/2/4/5/6) reduce override rate to ≤6/12 AND no regressions on any scans that previously had zero overrides (wezterm, kanata, QuickLook).
- **Phase 3 success (target):** ≤3/12 after RULE-7/8/9 promote (deferred until compound gate conditions are met — could be Phase 5 or beyond as catalog grows).

The hard ≤3/12 floor as a *Phase 3 blocker* is unrealistic given the dependency chain. If the board endorses it as stated, Phase 3 is structurally blocked before it starts.

---

## §3 Items the design missed or under-specified

1. **Fallback template key for no-rule-fired cases.** The rule evaluation order ends at "fallback to current advisory color" but doesn't specify whether the renderer uses the old advisory string or a default template key. This will cause an implementation ambiguity in Phase 3. Needs a decision: add `q{N}.{color}.default` keys to `scorecard-templates.json`, or preserve advisory string as-is.

2. **RULE-3 operator-precedence bug.** The trigger `shape.category == "agent-skills-collection" OR shape.is_solo_maintained AND shape.is_privileged_tool == False` is ambiguous in Python without explicit parentheses. As written it evaluates to `(agent-skills-collection) OR (solo AND not privileged)` which is a broader match than likely intended. Should be `(shape.category == "agent-skills-collection") OR (shape.is_solo_maintained AND NOT shape.is_privileged_tool)` — with parentheses explicit in the implementation.

3. **`classify_shape()` heuristic priority conflicts.** The heuristic decision tree has no explicit conflict-resolution path. Example: ghostty is Zig (not in the C++/C embedded check), has GUI binaries (step 4 fires), and has terminal-emulator topic — step 4 correctly wins. But what about a C# GUI app that also has an install script with 0 releases? Steps 3 and 4 could both fire; step 3 comes first. The design should state explicitly whether steps are tried in order with first-match-wins, or whether there's a scoring mechanism. First-match-wins is the simpler implementation; name it.

4. **V12x harness work dependency not surfaced in Phase 3 plan.** RULE-7/8/9 compound gates require V12x-7/11/12 harness signals. The design mentions this (§5 per rule) but doesn't connect it to the back-to-basics-plan phases. Phase 3 will need to either (a) stub out unimplemented harness signals gracefully, or (b) document that RULE-7/8/9 are placeholder rule functions that always fall through until the harness work lands. This implementation choice should be explicit.

---

## §4 Items you'd cut or simplify

1. **RULE-5 (Q3 ruleset-as-disclosure floor).** The design itself labels this "more of a documentation exercise" (§5). The rule already fires as-is in the current `compute_scorecard_cells()` Q3 logic. Including it as a named RULE-N creates bookkeeping overhead (tests, traceability) for zero behavior change. Fold the condition into a comment in the Q3 evaluation function and remove RULE-5 from the numbered rule set. Save the slot for a future rule with actual bite.

2. **`confidence: str` field on `ShapeClassification`.** The `NamedTuple` in §4 and §10 includes a `confidence: str` field ("high"/"medium"/"low"). The design doesn't specify how callers use this field downstream — no rule branches on confidence level, the template-map doesn't condition on it, and the validator doesn't check it. If it's purely diagnostic, it belongs in a log or debug output, not in a `NamedTuple` that's part of the rule evaluation contract. Either use it (e.g., low-confidence forces fallback to advisory), or remove it to simplify the type signature.

---

## §5 Dissents (formal record — required even if empty)

No dissents.

The shape-as-modifier call (Q1), cells-only scope (Q7), and validator-warning-not-tier choice (Q5/RULE-10) are all defensible and I agree with them. My Q9 position (two-tier acceptance structure) is a practical concern about how the acceptance floor is framed, not a design disagreement — I'd frame it as a refinement, not a dissent.

---

## §6 R2 carry-forwards (what should the consolidation round focus on)

1. **Q9 acceptance floor resolution.** The ≤3/12 hard floor as a Phase 3 blocker is inconsistent with the §8 projection that firm-rules-only lands at ~5/12. R2 should converge on: keep the floor but reframe it as a Phase-5-or-later target (after compound gates can fire), OR lower it to ≤6/12 for Phase 3 with ≤3/12 as the Phase 5 target. This is the most important practical decision.

2. **RULE-3 keep vs prune.** The Pragmatist says prune (operator-precedence bug + n=0 marginal evidence beyond RULE-1/2 coverage). R2 should surface whether the other agents agree, and if so, whether to remove it from the numbered rules or retain as a documented candidate with explicit promotion gate.

3. **RULE-5 keep vs fold.** The Pragmatist says fold it into a comment (zero behavior change, bookkeeping overhead). Other agents may disagree if they value the explicit traceability of naming every rule condition. Converge in R2.

4. **Fallback template key specification.** This is a Phase 3 implementation blocker if unresolved: what does the renderer emit when no rule fires? R2 should produce a concrete answer (default template keys or preserve-advisory-string).

5. **V12x harness dependency surfacing.** R2 should confirm whether the Phase 3 implementation plan explicitly handles RULE-7/8/9 as stub-through functions (always fall to advisory until harness signals land) — or whether those rules are deferred entirely from the Phase 3 implementation scope. The answer affects Phase 3 test coverage targets.
