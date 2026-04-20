# Schema V1.2 R2 — Codex

## Final vote row (Q1–Q7)
- Q1: coordinated (held)
- Q2: D7-A1 (held)
- Q3: D8-B1 (held)
- Q4: migration-script (held)
- Q5: D7-G3+G4 (flipped from R1)
- Q6: no, interpreted as Q6-narrow (held)
- Q7: agree (held)

## Split-1 position (Q3 — shape winner)
I do not think Q3 honestly merges. B2-scoped sounds moderate, but systemically it creates a split-brain contract: some deltas are “real” harness output, others are harness-local schema dialect, while the operator guide already says the sidecar is the spec and D-8 should accept harness output natively. That is a Frankenstein compromise, not a clean boundary.

B1 is still the least coupled answer. The harness is the actual producer; the sidecar proves where V1.1 is lossy; the renderer does not materially depend on these Phase 1 field names today; and the migration cost lands once in fixtures/tests/operator docs. B3 is cleaner than B2 philosophically, but it adds a third naming dialect and forces both harness and schema to move without reducing downstream churn.

So I defend B1: make V1.2 harness-canonical, preserve nested `dangerous_primitives`, preserve structured `manifest_files`, preserve counts/ratios/status fields, delete the transformer.

## Split-2 position (Q5 — override mechanics)
This split can merge, but upward, not sideways. My R1 `G3` alone is not sufficient because schema cannot prove the rationale is substantive; DeepSeek is right that validator logic must exist. Pragmatist is right that raw prose alone is theater.

My R2 position is `G3+G4`: require `computed_signal_refs` plus `override_reason` in schema, and add validator checks that when Phase 4 color differs from advisory color, `computed_signal_refs` is non-empty, each ref resolves to a declared advisory signal ID, and `rationale` is present and above a floor length. I would not require free-text mention of signal names if refs are machine-resolved; that is weaker than structural linkage.

## Q6 coupling resolution
Q6 is **narrow**. New renderer surface stays deferred. Mandatory renderer edits caused by D-7/D-8 do land in V1.2: both scorecard partials currently read `phase_3_computed.scorecard_cells`, and `tests/test_render_md.py` asserts that exact path. “No renderer edits at all” is not viable.

## Open question positions
- OQ-1: `compute.py` should populate stable signal IDs under `phase_3_advisory.scorecard_hints.<qid>.signals[]`; `computed_signal_refs` must reference those IDs, not prose names.
- OQ-2: Pick `phase_3_advisory.scorecard_hints`. That is already the SF1 wording and distinguishes advisory from deterministic-computed authority.
- OQ-3: Add a sibling top-level `phase_3_advisory`; do not rename or overload `phase_3_computed`, which still owns the other 7 deterministic outputs.
- OQ-4: Keyed object by canonical question ID. Current renderer/test contract is object lookup, and fixed-cardinality scorecards do not benefit from array semantics.
- OQ-5: Explicit validator check. JSON Schema alone cannot enforce override-only conditions, ref resolution, or evidence-coverage semantics.
- OQ-6: Migrate active V1.1 fixtures plus any archived Step G artifacts used in tests/audit. Do not bulk-touch V2.4 catalog entries. Update `provenance.json` schema_version fields where migrated.
- OQ-7: Accept partial Phase 1 failures structurally, but they must be explicit. Preserve error/status fields and let `phase_2_validation` plus coverage cells mark `partial`/`not_available`; do not pretend missing scans are false negatives.
- OQ-8: Catalog entries 1–11 stay V2.4-only unless a specific implementation/test need justifies back-authoring. No bulk migration project.
- OQ-9: In steady state B1, the sidecar disappears because the schema accepts the rich Phase 1 data directly. Phase 4 should consume the V1.2-native form, not a second hidden fact channel.

## Ground-truth bug absorption
- P1-RENAME: Absorbed by B1. Rename schema to harness names, add already-emitted `open_issues_count` and `size_kb`, keep currently-ungathered fields nullable until harness gathers them, and stop hardcoding dropped metadata in a transformer.
- P2-LOSSY-CAST: Absorbed by preserving native granularity. `symlinks_stripped` should remain an integer count; `distribution_channels_verified` should become structured `{verified,total}` or equivalent non-bool ratio; `windows_surface_coverage` should stay status-like, not bool.
- P3-DOUBLE-ASSIGN: Delete the duplicate `branch_protection` assignment before any absorption work. It is small but must not survive into the V1.2 landing path.

## New disagreement surfaced
The R1s treat Q3 and Q5 as separable, but they are coupled through operator automatability. If Q3 keeps any lossy bridge while Q5 demands override accountability, Phase 4 is being asked to justify overrides against advisory signals using a degraded fact surface. That is a real architecture disagreement, not just a naming preference.

## Rationale (prose)
The decisive system question is where the contract becomes canonical. On the D-8 side, the real producer is the harness, and the current transformer is not a benign adapter; it erases counts, ratios, transport status, and family structure. On the D-7 side, Phase 4 is being given authority to override deterministic scorecard advice. Those two decisions couple tightly: if the authority migration lands while the fact surface remains lossy, override-explained becomes partly synthetic because the LLM is not seeing the same granularity the harness actually gathered. That is why I am not willing to merge onto B2-scoped. B2 sounds smaller, but it creates two truths: “use harness-native shapes when they feel semantically rich, but rename fields in harness when V1.1 names were stylistic.” That is exactly the kind of half-normalized contract that leaks into operator docs, migration scripts, and fixture regeneration logic.

The code supports that read. The scorecard renderers are narrowly coupled to scorecard location, not to the Phase 1 naming debate: both Jinja partials still read `phase_3_computed.scorecard_cells`, and render tests assert that path. That means Q6 should be read narrowly: V1.2 must update the scorecard path and tests, but does not need to surface new Phase 1 richness in findings cards. By contrast, the Phase 1 schema is already where the lossy compromises live: `symlinks_stripped` is boolean in schema but integer in harness, `distribution_channels_verified` is boolean in schema but `"4/5"` in harness and in tests, `manifest_files` loses structure, `dangerous_primitives` gets flattened, and `ossf_scorecard.http_status`/`dependabot_config`/PR counts are dropped entirely. Those are contract defects, not renderer concerns.

Q5 also needs an honest merge. I still think an override category enum is load-bearing because the post-V1.2 comparator work needs to distinguish “threshold calibration” from “qualitative context” from “rubric intent.” But DeepSeek is right that schema-only structure is insufficient. We already learned in Step G reviews that jsonschema catches shape, not semantic correctness. So the minimum credible V1.2 is schema plus validator: schema requires advisory refs and reason category; validator enforces override-only invariants and ref resolution. That is the smallest shape that keeps gate 6.3 structural rather than reviewer taste.

The operator-guide coupling points the same way. §8.8 currently tells operators V1.1 forms must validate clean, Step 3b byte-for-byte applies to Phase 3, and D-7 will move scorecards to `phase_4_structured_llm` with advisory hints. If we choose a mixed Q3 contract, the guide has to explain why some harness fields are canonical and others are schema-renamed before Phase 4 ever sees them. That is needless operator complexity. A single cut is better: V1.2 form shape matches harness output; `phase_3_advisory` becomes the stable advisory namespace; validator carries the conditional override gate; renderers update only where forced.

## Unresolved items for R3 (if any)
- Finalize the advisory signal ID vocabulary and schema shape for `phase_3_advisory.scorecard_hints`.
- Freeze the `override_reason` enum values.
- Decide the exact structured type for coverage ratios/statuses (`distribution_channels_verified`, `windows_surface_coverage`) so migration and tests are deterministic.

## Blind spots
I am still optimizing for contract coherence more than for prompt-authoring ergonomics. If Phase 4 authoring quality drops materially when asked to use explicit advisory refs and categories, that would weaken my confidence in the stricter Q5 merge even though the architecture is cleaner.
