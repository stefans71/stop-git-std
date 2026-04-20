# Schema V1.2 R1 — Codex

## Votes (one per question)
- Q1: coordinated — D-7 and D-8 hit the same contracts (`form.json`, renderer partials, gate 6.3, fixtures), so splitting creates two migration waves and duplicated breakage.
- Q2: D7-A1 — compute must remain a required advisory input so overrides are traceable, calibratable, and testable rather than free-form.
- Q3: D8-B1 — the harness should be canonical because it is already the real producer and the sidecar proves V1.1 is the lossy layer.
- Q4: migration-script — clean cut on runtime contract, but provide one deterministic upgrader for the 4 fixtures and any archived V1.1 forms that need re-render.
- Q5: D7-G3 — override semantics need a machine-readable reason category, not just prose, or telemetry and gate enforcement will collapse into reviewer taste.
- Q6: no (deferred to V1.3+) — V1.2 must update renderers for moved scorecard authority, but richer Phase-1 data surfacing in finding cards should stay out.
- Q7: agree — SD2, PD3, package refresh, Scanner-Integrity section-00 restructuring, and D-4 watchpoint schema work are all out of scope.

## Rationale (prose)
The key coupling is that D-7 is not just “move four cells.” Today the trust-scorecard partials in both Markdown and HTML read directly from `phase_3_computed.scorecard_cells`, and tests assert that exact location. Once scorecard authority moves to Phase 4, renderer partials, render tests, fixture shapes, and Step G gate 6.3 all need to move in lockstep. If you stage D-8 first and D-7 later, you regenerate fixtures twice, rewrite the scorecard partials twice, and keep the operator guide in an awkward transitional state where Phase 1 is V1.2-native but the scorecard still pretends to be deterministic authority. That is wasted churn.

The D-8 side is similarly coupled. The transformer is not a harmless adapter; it is performing lossy semantic compression. It drops `dependabot_config`, `ossf_scorecard.http_status`, `pr_review.self_merge_count`, `total_merged_lifetime`, branch-protection counts, and it collapses coverage from ratios/states to booleans. That matters because those fields are exactly the kind of facts Phase 4 needs when it is asked to justify overrides against compute advisories. If D-7 lands while D-8 keeps the lossy bridge, the LLM is being asked to explain overrides from a degraded fact surface. That is a bad authority migration.

I would make the harness shape canonical (`D8-B1`) rather than teaching the harness to emit a renamed “schema dialect.” The harness already speaks the source systems’ language and the sidecar is the empirical spec. Preserving V1.1 names via `oneOf` pushes complexity downstream into renderers, validators, and tests. A `oneOf` schema does not preserve determinism; it preserves ambiguity. The renderer then has to normalize at runtime, and that is exactly how byte-identical re-render guarantees get fragile.

On D-7, `D7-A1` is the right advisory level. Deleting compute removes calibration telemetry. Making compute ignorable removes the only stable comparison baseline. The operator process in §8.8 also depends on explicit phase boundaries: Phase 3 should still emit deterministic signals; Phase 4 may override them, but only against visible, named advisory inputs. That lets gate 6.3 become a real structural check instead of “the LLM said something plausible.”

I do not support broad renderer-surface expansion in V1.2. There is mandatory renderer work here, but it should be narrowly scoped: read scorecards from Phase 4, optionally expose advisory deltas if needed, and keep the rest stable. If you also decide to surface richer dangerous-primitive snippets, self-merge counts, Dependabot config, and transport-level OSSF details in V1.2, you multiply parity risk and blow up the determinism test surface.

The thing that blows up if this coupling is ignored is not one bug, but contract incoherence: operator instructions still describe Step 3b authority one way, renderers read another field, fixtures validate via adapters, and tests stop proving what production does. That is how “preview” pipelines rot.

## FIX NOW items (if any)
- C-1: Define one canonical V1.2 scorecard storage shape now: keyed object vs ordered array. Renderer/test churn is different for each; leaving it implicit will fork implementations.
- C-2: Define `phase_3_advisory` explicitly in schema and operator guide, not just prose. D-7 currently references it without a concrete schema contract.
- C-3: Require `computed_signal_refs` to resolve to named advisory fields and require `override_reason` enum alongside rationale; otherwise gate 6.3 is not automatable.
- C-4: Ship a one-time V1.1→V1.2 migration script with fixture regeneration. Do not solve back-compat with runtime `oneOf`.

## DEFER items (if any)
- C-5: Renderer expansion for richer Phase-1 data in §01/§02 finding cards — defer until V1.3, triggered after V1.2 round-trip and determinism pass on all regenerated fixtures.
- C-6: 11-scan comparator calibration analysis — defer until V1.2 schema is frozen and override telemetry exists, or the analysis will be on the wrong contract.

## INFO items (if any)
- C-7: The current Markdown and HTML scorecard partials are hard-coupled to `phase_3_computed.scorecard_cells`; D-7 necessarily includes renderer edits even if Q6 says “no.”
- C-8: The transformer proves V1.1 is not merely renaming fields; it actively erases counts, ratios, transport status, and per-family structure that may matter for Phase-4 reasoning.
- C-9: `coverage_affirmations.distribution_channels_verified` is currently richer as `"4/5"` than the schema’s boolean. Keeping the boolean blocks honest coverage reporting.

## Open questions the brief missed
- Should `phase_4_structured_llm.scorecard_cells` be a keyed object by canonical question id or an ordered array of cell objects? The brief mixes the two.
- Will gate 6.3 validate override structure from schema alone, or will `validate-scanner-report.py` gain explicit checks for `override_reason`, `computed_signal_refs`, and evidence citation coverage?
- Does the migration script also rewrite archived Step G artifacts used by tests, or only the 4 active fixtures?

## Blind spots
My weakest point here is comparator-authoring ergonomics: I am optimizing for contract clarity and system behavior, not for minimizing LLM prompt complexity during Phase 4 authoring.
