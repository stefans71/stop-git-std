# Skeptic R1 — Calibration Rebuild Design Review

## §1 Topline (under 150 words)

**DISSENT.** The design is directionally correct — shape-awareness and rule-table codification are the right fixes for the over-call problem the audit identified. But it over-claims on three fronts: (1) the projected override reduction from ~83% to ~12% is unsupported by the evidence — the firm rules (RULE-1/2/4/5/6) eliminate at most 4 of 10 overrides, and the n=1 candidate rules (RULE-7/8/9) are explicitly gated on harness work that doesn't exist yet; (2) the shape classifier's 9-category enum is over-fitted to 12 scans — several decision boundaries will produce misclassifications on the next 12 scans; (3) the Q9 hard floor (≤3/12 overrides) is set at a level the design's own projections don't meet without the n=1 candidates promoting, creating a circular dependency. The design should be accepted as a Phase 1 foundation but with the override-reduction target explicitly lowered to ≤5/12 and the n=1 rules moved to a Phase 1.5 deferred ledger.

## §2 Per-question answers (Q1–Q9 from design doc §9)

### Q1 — Shape-as-modifier architectural call

**ANSWER:** Agree with modifier, but the reasoning understates the cost.

**REASONING:** The design claims "the 6 shape-blind rules become 9 copies with no semantic difference" under lookup-key. This is true for the current 12-scan catalog. But the modifier approach means every rule function carries a `shape` parameter it may not use — and when a future rule *does* need shape-awareness, the modifier pattern forces shape-conditional branches inside a single rule body rather than clean per-shape tables. The audit §9 Observation 5 shows shape category correlates with verdict more strongly than Q1 cell color does — this suggests shape-awareness will *grow*, not stay at 4/10 rules. The modifier choice is correct for Phase 1 but the design should acknowledge that if shape-aware rules exceed ~60% of the table, lookup-key becomes the cleaner abstraction. The cost is acceptable for now; the design should flag the tipping point.

### Q2 — 9-category enum scope

**ANSWER:** Too granular for the evidence base. Collapse to 6 categories.

**REASONING:** The 12-scan classification table in §3 shows 12/12 clean classification — but this is circular: the categories were *derived from* those 12 scans. The decision boundaries are fragile. Consider: `agent-skills-collection` is defined by `agent_rule_files.count >= 3 OR primary_language == "Markdown"`. The skills scan has `primary_language: "Shell"` (not Markdown) and 57 tarball files — how many are agent rule files? The heuristic will misclassify the next agent-skills repo that uses YAML or TOML config. `specialized-domain-tool` is a catchall for "doesn't fit" — it's a smell that the category is too fine. `install-script-fetcher` (n=1: caveman, which isn't even a V1.2 scan) has no empirical support in the 12-scan table. Collapse to: `library-package`, `cli-binary`, `desktop-application`, `web-application`, `embedded-firmware`, and `other` (absorbing agent-skills-collection, agentic-platform, install-script-fetcher, specialized-domain-tool into `other` with a sub-classification note). This reduces the surface for misclassification without losing useful discrimination — the cross-shape modifiers (`is_privileged_tool`, `is_reverse_engineered`) carry more signal than the fine category distinctions anyway.

### Q3 — RULE-3 keep-or-drop

**ANSWER:** Prune RULE-3. It's a ghost rule.

**REASONING:** The design itself flags RULE-3 as lower-confidence with n=2 evidence, and acknowledges "RULE-1 + RULE-2 cover most of the same ground." The marginal effect is near-zero: ghostty is already covered by RULE-1 (CODEOWNERS + ruleset + rules-on-default); kamal is already covered by RULE-1. The only case RULE-3 might catch independently is a solo-maintained, non-privileged OSS repo with *no* governance gates and *no* review rate — which is exactly the pattern the design says should stay red (the "no positive signals at all" case). RULE-3's trigger (`shape.is_solo_maintained AND shape.is_privileged_tool == False`) would fire on wezterm (solo, non-privileged) — but wezterm has 0 governance gates and 3.3% review rate. Should Q1 be amber for wezterm? The audit says wezterm is Caution-verdict with Q1=red and no override — the LLM didn't soften it. RULE-3 would create a new amber case the LLM never chose. Keep the agent-skills-collection branch as a note for future shape coverage, but drop the solo-maintained branch.

### Q4 — RULE-7/8/9 promotion gates — compound gate proposal

**ANSWER:** Agree with compound gate. The design should go further: require n≥3, not n≥2.

**REASONING:** The compound gate (n≥2 confirming scans AND harness signal implemented) is correct in principle. But n≥2 is too low for rules that each depend on new harness signals (V12x-11, V12x-7, V12x-12) that don't exist yet. The audit §10 explicitly flags RULE-7/8/9 as "single-scan evidence — treat as candidates pending more shape-coverage scans." With n=2, a single new scan that happens to match the pattern could promote the rule before the harness signal is reliable. Consider: RULE-8 (URL typosquat) — if the next wild scan also has a typosquatted install URL, that's n=2. But the harness signal `install_doc_urls_have_tld_deviation` hasn't been implemented yet (V12x-7 is Priority Medium). The rule would be promoted with no programmatic detection path — every invocation falls through to override, which is worse than not having the rule. The compound gate already prevents this (requires harness signal), but n≥3 adds a buffer against coincidental pattern matches. The cost is low (these are rare patterns; waiting for n=3 is months of scans) and the benefit is avoiding premature rule codification.

### Q5 — RULE-10 as validator warning vs verdict tier

**ANSWER:** Agree with validator warning. But the design understates the false-positive risk.

**REASONING:** The design says "no current scan triggers this" — which means RULE-10 is untestable against the existing catalog. The validator warning will fire zero times on re-render, so we won't know if it's calibrated correctly until a future scan triggers it. The risk: a scan with a legitimate Critical verdict that happens to have all Critical findings classified as kind other than Vulnerability/Supply-Chain (e.g., a governance-only Critical that the owner *intentionally* wants as Critical). The validator warns, the author overrides, and the warning becomes noise. The design should add a calibration mechanism: after 10 production scans, audit how many times RULE-10 fired and how many were false positives. If the false-positive rate exceeds 50%, the trigger condition needs narrowing (e.g., add `AND no finding has severity == "Critical" at all` — if there are Critical findings but none of the right kind, the authoring taxonomy may need expansion, not a warning).

### Q6 — Cell short_answer template-map

**ANSWER:** Agree with template-map. But the template set is incomplete.

**REASONING:** The template-map in §6 covers the rule-defined paths but has no template for the override case. When Phase 4 overrides a cell, the current behavior is free-form text. The design should specify: does the override replace the template key entirely (current behavior, preserved), or does the override mechanism get its own template category (e.g., `q1.amber.override`)? The latter would make override text more consistent but constrains the LLM's freedom — which is the whole point of the override mechanism. The design should explicitly state that overrides bypass the template system entirely (which is the implicit assumption from §2 "Override mechanism preserved"). Also missing: templates for Q2 (green/amber/red) — the design has no Q2 rules, so Q2 templates aren't defined. This is fine for Phase 1 (Q2 stays LLM-authored), but the template-map should at minimum have a `q2.green.default`, `q2.amber.default`, `q2.red.default` fallback so the renderer doesn't crash on Q2 cells.

### Q7 — DECIDED: Scope cells only (Phase 1)

**ANSWER:** No dissent. The deferral is correct.

**REASONING:** The audit covered cells only. Finding-severity rule-driving needs its own audit (what finding patterns exist? what's programmaticizable?). Bundling would double the board surface area and the design would be weaker for it. The design's §7 framing is honest about the "~70% programmatic, not 90%" post-Phase-1 state. This is the right call.

### Q8 — Migration approach (preserve LLM text vs regenerate)

**ANSWER:** Agree with approach 2. But the design needs a concrete rule for what counts as "override."

**REASONING:** The design says "preserve the override-explained content where the LLM's nuance was the right call; regenerate the OSS-default rows with calibrated text." This is correct in spirit but underspecified. Consider: a scan where Phase 4 overrode Q1 from red→amber with `signal_vocabulary_gap`. Under the new rules, RULE-1 now produces Q1=amber deterministically. Should the short_answer be the template text ("Partly — formal governance present...") or the LLM's original override text? The design implies template text (the override is no longer needed). But the LLM's text may contain nuance the template doesn't capture. The rule should be: if the new rule produces the *same color* as the old override, use the template text (the override is resolved). If the new rule produces a *different color* than the old override, preserve the LLM text (the override is still active). This is implicit in the design but should be explicit.

### Q9 — Acceptance threshold for re-render — HARD FLOOR proposal

**ANSWER:** The ≤3/12 floor is too strict for Phase 1. Propose ≤5/12.

**REASONING:** The design's own §8 projection shows ~5/12 overrides remaining with firm rules only (RULE-1/2/4/5/6 eliminate 4 of 10 overrides; 6 remain). To reach ≤3/12, the n=1 candidate rules (RULE-7/8/9) must promote — but they're gated on harness signals that don't exist yet (V12x-11, V12x-7, V12x-12). The design creates a circular dependency: the hard floor requires RULE-7/8/9 to promote, but RULE-7/8/9 can't promote until the harness signals are implemented, which is Phase 3+ work. A ≤5/12 floor is achievable with firm rules alone (projected 6/12, close enough that one additional override might collapse with rule tuning). It also aligns with the design's own "~50% override reduction" projection. The ≤3/12 target should be the Phase 1.5 goal, after RULE-7/8/9 have harness support and can promote.

## §3 Items the design missed or under-specified

1. **Q2 is completely absent from the rule table.** The design has zero Q2 rules. The audit shows 3 Q2 overrides (Kronos, Xray-core, skills) — that's 30% of all overrides. The design's §8 migration table shows "Q2 override stays" for Xray-core with no plan. If the goal is ~80% override reduction, ignoring 30% of the override population is a gap. The design should at minimum document why Q2 is deferred (finding-severity dependency? insufficient signal vocabulary?) rather than leaving it as an unaddressed hole.

2. **The shape classifier's confidence field has no behavioral consequence.** The design defines `confidence: "high" / "medium" / "low"` but never says what happens when confidence is low. Does the rule table degrade? Does the override mechanism become easier to trigger? Does the validator warn? A confidence field with no behavioral consequence is dead weight. The design should specify at minimum: when `confidence == "low"`, the rule table should prefer the fallback advisory color over shape-aware rules (i.e., shape-conditional branches don't fire).

3. **No test for shape-classifier stability across harness changes.** The classifier reads from `phase_1_raw_capture` fields that are themselves evolving (V12x backlog items will add new signals). If V12x-6 adds Maven/Gradle/Cargo parsing, the `dependencies.manifest_files` field changes shape — does the classifier's `library-package` decision boundary shift? The design should specify a regression test: for each of the 12 V1.2 bundles, `classify_shape()` must return the same category after any harness change that doesn't touch the classifier's input fields. This prevents silent reclassification.

## §4 Items you'd cut or simplify

1. **`specialized-domain-tool` category.** It's a catchall for "doesn't fit other categories" — which is what `other` is for. The design's own classification table shows 0 scans in `other` and 2 in `specialized-domain-tool` (Kronos, freerouting). Both could land in `other` with a domain sub-tag. The distinction adds no rule-table value because no rule branches on `specialized-domain-tool` specifically.

2. **`agentic-platform` category.** n=0 in the V1.2 classification table (Archon and hermes-agent are V2.4 scans, not V1.2). The category exists for future scans but has no empirical support. Collapse into `other` until a V1.2 scan actually matches the heuristic.

3. **`install-script-fetcher` category.** n=0 in V1.2 scans (caveman is V2.4). The heuristic (`releases.entries.count == 0 AND executable_files empty AND no GUI`) is likely to misclassify young repos that simply haven't created releases yet. Collapse into `other` with a note.

4. **The `matched_rule` field on `ShapeClassification`.** The design includes `matched_rule: str` (e.g., "agent_rule_files >= 3 + Markdown primary") but this duplicates information already available from the decision tree. It's a debugging aid that should live in logs, not in the schema. Remove it from the `ShapeClassification` NamedTuple; keep it as an internal debug return if needed.

## §5 Dissents (formal record — required even when empty)

**Dissent 1 — Q9 hard floor (≤3/12 overrides)**
- **WHAT:** The Phase 1 acceptance threshold requiring override rate below 25% (≤3 of 12 scans).
- **WHY:** The design's own projections show ~5/12 overrides with firm rules alone. The ≤3/12 target requires RULE-7/8/9 to promote, which is gated on harness signals that don't exist yet. This creates a circular dependency that guarantees Phase 1 fails its own acceptance criteria.
- **WHETHER YOU'D BLOCK:** FIX-NOW — lower the floor to ≤5/12 for Phase 1, move ≤3/12 to Phase 1.5.

**Dissent 2 — 9-category enum over-fitted to n=12**
- **WHAT:** The 9-category shape enum (with 4 categories having zero V1.2 empirical support).
- **WHY:** `agentic-platform`, `install-script-fetcher`, and `specialized-domain-tool` have no V1.2 scan evidence. The decision boundaries were derived from 12 scans and will produce misclassifications on the next 12. The design claims "12/12 classify cleanly" — this is circular because the categories were defined to fit those 12 scans.
- **WHETHER YOU'D BLOCK:** DEFER-WITH-NOTE — accept the 9-category enum for Phase 1 but require a stability review after 12 more V1.2 scans. If >2 misclassifications occur, collapse to 6 categories.

**Dissent 3 — Q2 absence from rule table**
- **WHAT:** The design has zero Q2 rules despite Q2 accounting for 30% of overrides (3 of 10).
- **WHY:** The design's scope is "cells" — Q2 is a cell. Excluding it means 30% of the override problem is unaddressed. The design should at minimum document the deferral rationale and timeline.
- **WHETHER YOU'D BLOCK:** PRESERVED-DISSENT-FOR-RECORD — not a blocker for Phase 1 acceptance, but the design should explicitly state Q2 deferral and timeline.

## §6 R2 carry-forwards (what should the consolidation round focus on)

1. **Q9 hard floor calibration.** The three agents should converge on a Phase 1 acceptance threshold that is achievable with firm rules alone (my position: ≤5/12) vs one that requires n=1 candidate promotion (design's position: ≤3/12). This is the single most consequential disagreement because it determines whether Phase 1 passes or fails.

2. **Shape enum granularity.** The Pragmatist will likely prefer fewer categories (simpler implementation); the Systems Thinker may prefer more (future-proofing). The consolidation should resolve whether `agentic-platform`, `install-script-fetcher`, and `specialized-domain-tool` survive or collapse into `other`.

3. **Q2 gap.** All three agents should weigh in on whether Q2's absence from the rule table is acceptable for Phase 1 or needs a documented timeline. The Pragmatist's "will it work in practice" read is especially relevant here.

4. **RULE-3 keep/prune/restructure.** The design explicitly asks the board to decide. My position is prune. If the Pragmatist or Systems Thinker sees a use case I'm missing, the consolidation should surface it.

5. **Confidence field behavioral consequence.** The design defines `confidence` on `ShapeClassification` but never uses it. The consolidation should decide: (a) remove it, (b) add a behavioral rule (e.g., "low confidence → shape-conditional rules don't fire"), or (c) defer to Phase 3 implementation.
