# Schema V1.2 R2 — Skeptic

## Final vote row (Q1–Q7)
- Q1: coordinated (held)
- Q2: D7-A1 (held)
- Q3: **D8-B2-scoped** (flipped from D8-B3)
- Q4: migration-script (held)
- Q5: **D7-G3** (flipped from D7-G4)
- Q6: no (deferred to V1.3+) (held)
- Q7: explicit OUT-of-scope list (agree) (held)

## Split-1 position (Q3 — shape winner)

**Flip to D8-B2-scoped (Pragmatist's position).**

Reading Codex's D8-B1 (harness-canonical) and Pragmatist's D8-B2-scoped, I see Pragmatist's scoped approach is the honest merger that preserves each agent's strongest point:

1. **Codex's core insight:** The sidecar proves V1.1 is lossy. The transformer drops semantically valuable fields (`dependabot_config`, `ossf_scorecard.http_status`, `pr_review.self_merge_count`, `total_merged_lifetime`, branch-protection counts). These should be preserved in V1.2.

2. **My R1 core insight:** Dangerous_primitives flattening loses family context and snippet data. Type coercion (`symlinks_stripped: int → bool`, `distribution_channels_verified: "4/5" → bool`) loses granularity.

3. **Pragmatist's scoped solution:** Field-name renames (`archived→is_archived`, `fork→is_fork`, `default_branch→default_branch_ref`) move to harness (cheap). Structural deltas (per-family dangerous_primitives, manifest_files.format, lossy casts) get schema-native acceptance. This preserves Codex's semantic preservation AND my data-loss prevention.

**Why not D8-B1 (harness-canonical)?** Because `is_archived` vs `archived` is not just naming—it's a semantic choice about boolean clarity. The schema's `is_` prefix convention is consistent with other boolean fields (`is_fork`, `has_issues_enabled`). Changing all booleans to drop `is_`/`has_` prefixes creates inconsistency with existing schema patterns.

**Why not D8-B3 (third shape)?** The migration cost outweighs the clarity benefit. Pragmatist's scoped approach achieves the same semantic preservation with less churn.

**The price of convergence:** We accept that 6 field renames live in the harness, not the schema. This is acceptable because:
- The harness already knows the GitHub API names
- The renames are trivial string substitutions
- The schema maintains its internal naming consistency

**What scan shape still embarrasses this merged position?** A repo where the harness emits a field that doesn't fit either "rename" or "structural delta" categories—something that requires semantic transformation beyond simple renaming. The transformer's `agent_rule_files.total_bytes` heuristic (line_count × 50) is one example. D8-B2-scoped says "schema accepts harness shape," but the harness shape includes this heuristic. If the heuristic is wrong, V1.2 canonizes it.

## Split-2 position (Q5 — override mechanics)

**Flip to D7-G3 (Codex's position).**

Reading all three positions:
- Pragmatist (D7-G2): `computed_signal_refs` non-empty + rationale names at least one signal
- Codex (D7-G3): `override_reason` enum + `computed_signal_refs`
- My R1 (D7-G4): Automated gate with N-char rationale + `computed_signal_refs`

Codex's D7-G3 is the minimal V1.2 enforcement that makes gate 6.3 structural rather than reviewer-taste. The `override_reason` enum enables semantic-drift telemetry that the 11-scan comparator analysis needs. Without categorization, we can't distinguish "threshold too strict" from "missing qualitative context" from "rubric literal vs intent."

Pragmatist's D7-G2 (rationale must name a signal) is subsumed by D7-G3's stronger requirement. My D7-G4 (N-char gate) is procedural, not structural—it can be added to validator without schema changes.

**The honest merger:** D7-G3 + validator-side N-char check (my D7-G4) + Pragmatist's signal-naming requirement (implied by `computed_signal_refs` non-empty). This is additive, not mutually exclusive.

**What we'll regret:** If we don't categorize overrides, the 11-scan comparator analysis will have to reverse-engineer categories from free text, which is error-prone. The enum forces explicit categorization at authoring time.

## Q6 coupling resolution

**Q6-narrow consensus:** Defer *new* renderer features (finding-card expansion, self_merge_count display, etc.). Mandatory renderer edits forced by D-7/D-8 authority + shape migration DO land in V1.2.

This is what all three agents meant. Codex's tension (C-7) confirms: "The current Markdown and HTML scorecard partials are hard-coupled to `phase_3_computed.scorecard_cells`; D-7 necessarily includes renderer edits even if Q6 says 'no.'"

The renderer must be updated to:
1. Read scorecard cells from `phase_4_structured_llm.scorecard_cells` instead of `phase_3_computed.scorecard_cells`
2. Handle the new scorecard cell shape (`rationale`, `edge_case`, `suggested_threshold_adjustment`, `computed_signal_refs`, `override_reason`)
3. Potentially handle nested `dangerous_primitives` structure if we adopt per-family preservation

These are mandatory for V1.2 to function. "No renderer surface in V1.2" means no *optional* enhancements.

## Open question positions

- **OQ-1:** **Who populates `computed_signal_refs` and what's the signal ID vocabulary?** compute.py must emit stable signal IDs (e.g., `formal_review_rate_below_10`, `no_branch_protection`, `has_contributing_guide`). The LLM references these IDs. Define vocabulary in compute.py docstring and schema `$comment`. **Answer: compute.py defines IDs; LLM references them.**

- **OQ-2:** **Phase 3 container naming conflict.** Use `phase_3_computed.advisory_scorecard_cells` (from brief), not `phase_3_advisory.scorecard_hints` (from SF1). The SF1 text was prose, not schema. Keep `phase_3_computed` container for consistency. **Answer: `phase_3_computed.advisory_scorecard_cells`.**

- **OQ-3:** **Does `phase_3_computed` rename or get a sibling?** Add sub-object `advisory_scorecard_cells` to existing `phase_3_computed`. Do not create new top-level phase. **Answer: sibling sub-object in existing phase_3_computed.**

- **OQ-4:** **`phase_4_structured_llm.scorecard_cells`: keyed object by question ID, or ordered array?** Keyed object by canonical question ID (`does_anyone_check_the_code`, etc.). Enables direct lookup in renderer partials. **Answer: keyed object by question ID.**

- **OQ-5:** **Gate 6.3 — schema-validation alone, or `validate-scanner-report.py` explicit check?** Both. Schema validates structure (`override_reason` enum, `computed_signal_refs` non-empty). Validator adds procedural checks (rationale ≥ N chars, evidence citation coverage). **Answer: schema + validator checks.**

- **OQ-6:** **Migration script scope — 4 active fixtures only, or also archived Step G test artifacts?** All fixtures with `provenance.json` entries, including `step-g-failed-artifact`. Regeneration ensures test consistency. **Answer: all fixtures in provenance.json.**

- **OQ-7:** **Partial Phase 1 failure handling.** Schema should accept `null` for optional substructures (`gitleaks: null`). Add `"nullable": true` to optional Phase 1 objects. **Answer: nullable optional substructures.**

- **OQ-8:** **Catalog entries 1–11 (V2.4-only scans) migration story.** Stay V2.4-rendered indefinitely. Back-author forms only if re-scanned via V2.5-preview. **Answer: stay V2.4-only unless re-scanned.**

- **OQ-9:** **Phase 4 LLM access to sidecar?** LLM gets only schema-valid `phase_1_raw_capture` subset. Sidecar is for audit/provenance, not authoring context. **Answer: schema subset only.**

## Ground-truth bug absorption

- **P1-RENAME:** V1.2 schema must accept `open_issues_count` and `size_kb` (harness already gathers). For `has_issues_enabled`, `primary_language`, `topics`, `fork_count`: either harness gathers them, or schema marks them nullable/optional-but-preserved-when-gathered. **Concrete: Add to harness gathering; schema accepts all.**

- **P2-LOSSY-CAST:** V1.2 schema accepts structured `{verified: int, total: int}` or string fraction for `distribution_channels_verified`. `symlinks_stripped` accepts `integer | boolean`. **Concrete: structured objects for ratios, union types for int/bool.**

- **P3-DOUBLE-ASSIGN:** Delete second assignment in transformer before harness absorption. Low-risk fix. **Concrete: Remove line 218 in transform_harness.py.**

## New disagreement surfaced

Reading other R1 outputs revealed a tension not flagged in my R1: **The renderer's current consumption of `dangerous_primitives.hits[]` vs per-family nesting.**

If V1.2 adopts per-family `dangerous_primitives` structure (as all three agents want), the renderer partials that consume `hits[]` today will break. This contradicts "Q6: no renderer changes." 

Pragmatist's blind spot paragraph raises this: "if the renderer directly consumes `code_patterns.dangerous_primitives.hits[]` today, and V1.2 changes that to a nested structure, then 'defer renderer to V1.3' becomes inconsistent."

This is a **mandatory renderer change** that must be in V1.2 scope. We cannot ship a schema that renderers can't process.

## Rationale (prose)

As Skeptic, my job is to hunt what we'll regret. The merged position on Q3 (D8-B2-scoped) has one regret: it papers over the `agent_rule_files.total_bytes` heuristic problem. The harness computes bytes as `line_count × 50`. If this heuristic is wrong, V1.2 canonizes it. But this is a minor regret compared to the alternative—keeping the transformer or adopting a pure harness-canonical approach that breaks schema naming consistency.

The real regret in the merged Q5 position (D7-G3) is that we're adding schema complexity (`override_reason` enum) that the LLM might ignore or misuse. If the LLM consistently picks `other` as the override reason, the enum becomes decorative. But this is a risk worth taking—without categorization, we have no hope of semantic drift analysis.

The **scan shape that embarrasses the merged position** is a **monorepo with partial governance** (my R1 example). The harness flattens branch protection to a repo-level boolean. Phase 4 LLM might infer "partial protection in critical paths" from file lists, but has no structured way to express it. V1.2's `has_branch_protection: bool` can't capture this nuance. This is a **genuine data loss** we accept because capturing subdirectory-level governance would require radical harness redesign.

The **price of convergence** on Q3 is accepting that field naming is not purely semantic—it's also about consistency with existing schema patterns. We pay with 6 trivial renames in the harness. On Q5, the price is adding an enum that might be misused. Both prices are acceptable.

I flipped from D8-B3 to D8-B2-scoped because Pragmatist's scoped approach achieves the same semantic preservation with less migration cost. I flipped from D7-G4 to D7-G3 because Codex's enum enables the semantic drift analysis the 11-scan comparator needs.

The **unresolved tension** is the renderer coupling for `dangerous_primitives`. This must be resolved before V1.2 ships.

## Unresolved items for R3 (if any)

1. **Renderer `dangerous_primitives` coupling:** Must decide: (a) keep flattened `hits[]` for renderer compatibility, losing family context, or (b) update renderer partials to handle nested structure, adding V1.2 scope.

2. **`agent_rule_files.total_bytes` heuristic:** Should V1.2 accept the heuristic, or require raw line_count and compute bytes in renderer?

3. **Signal ID vocabulary definition:** Need concrete list of compute.py signal IDs for `computed_signal_refs`.

## Blind spots

My perspective remains weakest on **renderer template complexity**. I advocated for per-family `dangerous_primitives` without examining the 14 Jinja2 partials. If updating them is non-trivial, the pragmatic choice might be to keep flattened `hits[]` with a `family` field—still losing snippet data but preserving family context.

Also, I underestimated the **prompt engineering burden** of teaching Phase 4 LLM to use `computed_signal_refs` and `override_reason` enum. If the LLM ignores these structures, our "structural enforcement" is theater. We need evidence from Step G Phase 4 runs.