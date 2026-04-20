# Schema V1.2 R2 — Pragmatist

## Final vote row (Q1–Q7)

- Q1: Coordinated (held — no new argument changes this)
- Q2: D7-A1 (held — advisory with cite-when-overriding is the minimal enforceable contract)
- Q3: **B-merged** (flip from D8-B2-scoped — see Split-1 below)
- Q4: Migration-script (held)
- Q5: **G-merged: D7-G2 + D7-G3 enum** (partial flip — adds override_reason enum from Codex but rejects N-char floor)
- Q6: Q6-narrow (held, confirmed below)
- Q7: Agree (held)

---

## Split-1 position (Q3 — shape winner)

**Proposed merger: B-merged = harness-canonical for ALL field-name deltas + schema-native acceptance for structural shape deltas. Transformer deleted.**

After re-reading all three R1s:

- Codex's D8-B1 (harness-canonical) is right that the harness is the real producer and the sidecar is the empirical spec. The sidecar is 3884 lines; V1.1 was designed without it. Forcing the harness to emit schema-native names (my R1 D8-B2 position) adds complexity to the harness for no semantic gain — the harness already has the correct field names from GitHub's API.
- DeepSeek's D8-B3 (third canonical shape) adds migration cost without solving the core problem. The "drop is_ prefix but keep _ref suffix" rule requires harness + schema + renderer changes simultaneously. That is bigger, not smaller, than B1. I am abandoning my partial support for B3 elements.
- My own R1 was correct on the shape deltas (nested `dangerous_primitives`, `manifest_files` with `format`, lossy casts) — schema must accept harness-native shapes for these. But I was wrong to hold the field-name renames as "cheap harness changes"; they are even cheaper as schema renames, because the harness already uses the right names.

**B-merged concrete decisions:**

1. **Field-name renames (§4.1 of R1 brief):** Schema adopts harness names. `is_archived` → `archived`, `is_fork` → `fork`, `default_branch_ref` → `default_branch`, `reset_at` becomes accept-both (epoch int or ISO string — harness emits epoch, schema can coerce), `dependabot` → `dependabot_alerts` (revert V1.1's shortening), `osv_dev` → `osv_lookups` (same). These 6 renames go in the schema; harness untouched.

2. **Shape deltas (§4.2):** Schema accepts harness-native shapes. `dangerous_primitives` accepts the nested per-family structure `{exec: {files: [{file, first_match: {line, snippet}}]}, ...}` — V1.1's flat `hits[]` is deleted. `manifest_files` accepts `[{path, format}]` not just `[string]`. `symlinks_stripped` accepts `integer | boolean`. `distribution_channels_verified` accepts `string | {verified: int, total: int} | boolean`.

3. **Transformer is deleted** after V1.2 migration script runs.

4. **DeepSeek's strongest point absorbed:** the per-family `dangerous_primitives` structure must be preserved with `hit_count` per family as well as `files[]`. This is D8-B1 semantics, not B2.

This is honest convergence, not Franken-compromise — B1 wins on naming, the shared structural concerns of Pragmatist + DeepSeek win on shape deltas. Codex's B1 position is satisfied because the harness becomes the spec.

---

## Split-2 position (Q5 — override mechanics)

**G-merged: D7-G2 structural requirement + D7-G3 override_reason enum. Reject D7-G4 N-char floor.**

Re-reading the three R1s, DeepSeek's D7-G4 (N-char minimum) is the weakest mechanism. A 50-char rationale requirement blocks word salad but doesn't distinguish "the rubric is too strict for this context" from "I made this up." That distinction is exactly what Codex's `override_reason` enum provides.

Codex is right: an enum enables telemetry analysis (11-scan comparator) without requiring free-text parsing. The enum values `threshold_too_strict / threshold_too_lenient / missing_qualitative_context / rubric_literal_vs_intent / other` are a vocabulary that makes gate 6.3 automatable. A validator can confirm `override_reason` is a known value; it cannot evaluate prose quality.

My R1 D7-G2 requirement (non-empty `computed_signal_refs` + rationale names at least one listed signal) stays as a structural floor — the enum alone doesn't force the LLM to cite what it overrode.

**G-merged = D7-G2 structural floor + D7-G3 enum, both required when LLM color ≠ advisory color.** DeepSeek's N-char floor is dropped — it adds noise without semantic gain over the enum.

---

## Q6 coupling resolution

**Q6-narrow confirmed.** This is what all three agents meant.

Mandatory renderer edits forced by D-7 shape migration DO land in V1.2:
- `scorecard.md.j2` line 1 currently reads `form.get('phase_3_computed', {}).get('scorecard_cells', {})`. After D-7, this must read from `phase_4_structured_llm.scorecard_cells`. This is a 1-line partial edit, not a renderer expansion.
- HTML scorecard partial (`templates-html/`) requires the identical change.

New renderer features (richer Phase-1 data surfacing, per-family dangerous_primitives display, self_merge_count display) stay in V1.3.

Codex's C-7 is therefore a narrower concern than it reads: the mandatory renderer edits are small (path change, not structural rewrite) and should not inflate Q6's scope.

---

## Open question positions

- **OQ-1 (computed_signal_refs vocabulary):** Deferred-to-implementation with a hard constraint: before V1.2 ships, compute.py must emit stable string identifiers per signal (e.g., `"q1.formal_review_rate"`, `"q2.closed_fix_lag_days"`). These IDs are defined as the Phase 3 output keys. The Phase 4 prompt must list them. This is implementation-completable by the operator without another board review.

- **OQ-2 (phase_3_advisory vs phase_3_computed naming):** Resolved here. The advisory scorecard signals stay in `phase_3_computed` as a new sub-object: `phase_3_computed.advisory_scorecard_cells`. Adding a top-level `phase_3_advisory` phase would require schema, renderer, and operator guide changes for no semantic gain. The SF1 CONSOLIDATION used `phase_3_advisory.scorecard_hints` as shorthand prose, not a schema decision. Schema topology: `phase_3_computed` keeps its existing 7 ops plus gains `advisory_scorecard_cells`; `phase_4_structured_llm` gains `scorecard_cells` (with the new D-7 cell shape).

- **OQ-3 (phase_3_computed rename vs sibling):** Resolved via OQ-2 above. `phase_3_computed` gains `advisory_scorecard_cells` as a sub-object. No rename, no new top-level phase.

- **OQ-4 (scorecard_cells keyed object vs ordered array):** Keyed object by question ID. Reason: the renderer partial iterates a known question list (`does_anyone_check_the_code`, `do_they_fix_problems_quickly`, etc.) and accesses cells by key. Switching to an array requires the renderer to search for the matching question at each iteration — more code, less readable, same output. Keyed object is the existing V1.1 pattern; keep it in Phase 4.

- **OQ-5 (gate 6.3 — schema alone vs validator explicit check):** Validator gains explicit check. Schema enforces structural presence (`override_reason` enum, `computed_signal_refs` non-empty); validator additionally checks that `computed_signal_refs` values are drawn from the stable signal ID vocabulary emitted by compute.py. This requires compute.py to export its signal ID list (trivially: a module-level constant). Adds ~15 lines to validator, one test.

- **OQ-6 (migration script scope — 4 active fixtures or also step-g-failed-artifacts):** Migration script targets the 3 active fixtures plus any `step-g-live-pipeline` or `pipeline-produced` forms (none currently in fixtures/ per provenance.json). `step-g-failed-artifact` tagged forms are NOT migrated — they are failed artifacts, not live pipeline outputs. If any failed artifacts are needed for regression testing, they require manual assessment, not automatic migration.

- **OQ-7 (partial Phase 1 failure handling):** Schema accepts partial structures. Any Phase 1 section that failed may be `null` or an empty wrapper object — already the case in V1.1 (most sections are optional). V1.2 makes this explicit in schema `$comment` per section: "nullable when Phase 1 tool not available or timed out." Validator checks completeness at Phase 2 validation (existing field), not at schema validation. No schema structural change needed beyond documentation.

- **OQ-8 (catalog entries 1–11 migration):** Stay V2.4-rendered indefinitely. No back-authoring trigger. If a re-scan of any of those repos is needed, it runs V2.5-preview natively and creates a new catalog entry. Retroactive form authoring produces back-authored fixtures (provenance.json category: "back-authored-from-golden-md") which cannot be used as pipeline evidence. Not worth the effort.

- **OQ-9 (Phase 4 LLM access to sidecar):** Yes — the Phase 4 LLM SHOULD receive the sidecar `phase-1-raw-full.json` as additional context for authorizing overrides and justifying scorecard cells. This does not change the schema (sidecar is not a schema artifact). Operator guide §8.8 should note: "Phase 4 LLM receives both the schema-valid form.json and the phase-1-raw-full.json sidecar for context." This resolves the partial Phase 4 reasoning quality concern DeepSeek raised.

---

## Ground-truth bug absorption

- **P1-RENAME:** V1.2 schema renames harness fields to harness-native names (B-merged). `has_issues_enabled`, `primary_language`, `topics`, `fork_count` are marked nullable-optional in schema — they are not gathered by current harness but must be accepted when present (for hand-enriched forms or future harness expansion). Harness does not need to lie about them. `open_issues_count` and `size_kb` are added to `repo_metadata` as accepted optional integer fields.

- **P2-LOSSY-CAST:** V1.2 schema accepts `distribution_channels_verified` as `string | {verified: int, total: int} | boolean`. `windows_surface_coverage` accepts `"scanned" | "skipped" | boolean`. `symlinks_stripped` accepts `integer | boolean`. The transformer's lossy casts are never executed — harness output validates directly.

- **P3-DOUBLE-ASSIGN:** Bug in transformer, not in schema or harness. Transformer is deleted in V1.2. But before deletion, remove the second `branch_protection` assignment (line 218) so there is no confused state during the migration window. Single-line fix; low risk.

---

## New disagreement surfaced

One tension none of the R1s flagged explicitly: **the scorecard cell shape in Phase 4 is not defined in the current schema.**

V1.1's `scorecard_cell` `$def` has only `{color, short_answer, inputs}`. The D-7 target cell shape adds `{question, rationale, edge_case, suggested_threshold_adjustment, computed_signal_refs, override_reason}`. This new `$def` must be authored for V1.2 and it is the primary schema change for D-7. None of the three R1s described the full new cell shape in concrete JSON Schema terms. This must be resolved before implementation begins — it is not a board-escalation item but an implementation spec gap.

---

## Rationale (prose)

Reading all three R1s together reveals a strong convergence underneath the surface-level split on Q3. Codex and Pragmatist both agree the transformer must die. DeepSeek and Pragmatist both agree the per-family `dangerous_primitives` structure must be preserved. Codex's B1 (harness-canonical naming) and the structural preservation goals of B2/B3 are not in tension — they apply to different decisions. The merged position is genuinely smaller than any single R1 position because it lets each agent's strongest argument apply to the domain where it is correct.

On Q5, the additive argument is decisive. D7-G2 + D7-G3 together cost one extra field in the schema and enable semantic-drift telemetry that D7-G2 alone cannot provide. DeepSeek's N-char floor adds nothing that the enum doesn't already provide more precisely.

The renderer coupling (C-7 Codex, my R1 blind spot) is real but small. The scorecard partial is 27 lines; the path change from `phase_3_computed` to `phase_4_structured_llm` is a single line. Calling this "renderer expansion" is an overstatement. Q6-narrow correctly scopes it: mandatory path migration lands in V1.2; new data surfacing is V1.3.

The signal ID vocabulary for OQ-1 is the most important implementation-completable item. Without stable signal IDs, the D7-G2 requirement becomes "cite something with a string the LLM invents" — which is theater. The fix is to define signal IDs as a module-level constant in compute.py and export it. The validator then checks against it. This is 10 lines of code, not an architecture decision.

The Phase 4 LLM sidecar access (OQ-9) resolves DeepSeek's skepticism about whether LLMs naturally cite evidence IDs: they do, when the evidence is present and named. The sidecar is already produced; making it available to Phase 4 requires no new code.

---

## Unresolved items for R3 (if any)

No board-level unresolvable items. All splits have honest merged positions. OQs are answered or deferred-to-implementation.

One implementation spec gap that MUST be resolved before coding starts: the concrete JSON Schema definition for the new V1.2 `scorecard_cell` in Phase 4 (including `override_reason` enum values, `computed_signal_refs` array type, and whether `rationale` replaces or supplements V1.1's `short_answer`). This is operator-completable without R3.

---

## Blind spots

My weakest area in this R2 is the HTML renderer partial (`templates-html/`). I read the Markdown scorecard partial and confirmed the 1-line path change. I did not read the HTML scorecard partial directly — I am inferring symmetry. If the HTML partial has additional coupling to `phase_3_computed.scorecard_cells` (e.g., conditional rendering based on `inputs` field shape), the mandatory V1.2 renderer edit is larger than "1 line." The Systems Thinker should verify this before implementation.

Also, the `oneOf` for `distribution_channels_verified` (string | object | bool) is syntactically valid in JSON Schema Draft 2020-12 but will require the renderer to handle 3 types. I deferred that renderer work to V1.3, which is consistent — but it means V1.2 forms with the richer type will not display the partial coverage percentage in rendered output. This is an acceptable gap but should be documented in the schema `$comment`.
