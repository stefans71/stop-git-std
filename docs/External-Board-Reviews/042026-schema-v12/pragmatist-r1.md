# Schema V1.2 R1 — Pragmatist

## Votes (one per question)

- **Q1:** Coordinated V1.2 — both D-7 and D-8 touch `phase_1_raw_capture` and fixtures; splitting means two regeneration passes with no real risk savings.
- **Q2:** D7-A1 — compute.py runs and its output is injected into `phase_3_computed.advisory_scorecard_cells`; Phase 4 LLM MUST cite `computed_signal_refs` when overriding; advisory is visible and structural, not optional.
- **Q3:** D8-B2 (schema-canonical, harness moves) — but scoped: only the 6 cheap field-name renames belong in the harness; the shape deltas (flatten, wrap) stay as schema accepts harness shapes natively for those. See rationale.
- **Q4:** Clean cut with migration script — write `migrate-v1.1-to-v1.2.py`; 3 fixtures regenerate deterministically; no `oneOf` schema complexity; V1.1 forms stay valid against V1.1 schema unchanged.
- **Q5:** D7-G2 — `computed_signal_refs` must be non-empty AND `rationale` must name at least one listed signal; automated gate enforces this; D7-G1 (free text only) collapses to "write something and move on."
- **Q6:** No — renderer surface deferred to V1.3+; V1.2 scope is schema + harness integration; no partial rewrites this cycle.
- **Q7:** SD2, Package V2.5 refresh, Scanner Integrity hit-level structure, D-4 watchpoint are all OUT; all agree per brief; no justification for inclusion.

---

## Rationale

**On Q1 (coordinated vs staged):** D-8 is not purely additive. The field-name renames in D-8 touch `phase_1_raw_capture.repo_metadata` and `pre_flight`, which are also what compute.py reads to produce advisory scorecard signals for D-7. If you do D-8 first, compute.py's input signatures change, and the D-7 advisory cell shape depends on those same fields. Running both together avoids fixture regeneration twice and avoids a half-migrated state where the harness is schema-canonical but compute.py still reads V1.1-named fields.

**On Q3 (D8-B2 scoped vs pure):** Pure D8-B2 (harness absorbs all transformer logic) would balloon the harness. The right split: field-name renames (`archived` → `is_archived`, `fork` → `is_fork`, `default_branch` → `default_branch_ref`, `reset` → epoch-to-ISO conversion, `dependabot_alerts` → `dependabot`, `osv_lookups` → `osv_dev`) are cheap harness changes — the harness just emits the schema-native names from the start. The shape deltas are different: the per-family `dangerous_primitives` structure (15 families × files[]) is harness-semantically correct — it's a natural representation of grep-per-pattern results. V1.2 schema should accept the nested per-family shape natively rather than forcing a flatten into a `hits[]` array at the harness level. The flatten loses the per-family aggregation context that the LLM would want for Phase 4 inference. Similarly, `manifest_files: [{path, format}]` — the harness emits the format field because it knows it; dropping it at transform time is a pure loss. V1.2 should accept it.

For the lossy casts in §4.2: `symlinks_stripped` as an integer count is richer than a bool; V1.2 should accept `integer | boolean`. `distribution_channels_verified` as "4/5" is richer than a bool; V1.2 should accept a string or a structured `{verified, total}` object. These are the cases where the harness has better data and the schema was the weak point.

**On Q2 (advisory authority):** D7-A2 (zero authority, just a feedback channel) is too weak. The whole point of keeping compute.py is that deterministic signals are reproducible and fast to audit. If the LLM can silently ignore them, the `suggested_threshold_adjustment` feedback loop never fires reliably because there's no enforcement that the LLM even looked. D7-A1 (must cite signals when overriding) preserves the feedback loop while still giving Phase 4 final authority.

D7-A3 (delete compute.py scorecard cells entirely) is the worst option: it trades a deterministic checkpoint for pure LLM discretion with no baseline. The compute.py advisory signals are not wrong — they're calibrated for 3 shapes and will grow with the 11-scan comparator analysis. Throwing them away pre-maturely loses institutional knowledge.

**On Q4 (back-compat):** `oneOf` schema complexity is the wrong trade. The renderer must then branch on which shape it received, adding runtime logic that is itself untested. A migration script is 50 lines; fixture regeneration is deterministic; this is the minimal-complexity path. V1.1 forms can still be re-rendered via the migration script — they are not permanently broken.

**On D7 Q1 Archon governance-floor:** The brief asks whether the Archon Q1 governance-floor override stays deterministic in compute.py or migrates to Phase 4. My vote: stays in compute.py as an advisory signal with explicit flag `governance_floor_override: true` in the advisory cell. The override fires because three binary conditions are simultaneously true — that IS deterministic and appropriate for Phase 3. The Phase 4 LLM then decides whether to accept the advisory red or override with rationale. This is cleaner than baking a judgment-call into Phase 4 with no compute.py anchor.

---

## FIX NOW items

- **P1-RENAME:** The transformer's `transform_repo_metadata()` already silently drops `has_issues_enabled`, `primary_language`, and `topics` (all return `None` or `[]` hardcoded). These fields are present in the zustand fixture but the harness doesn't gather them. V1.2 harness must gather them or the schema must mark them nullable-but-present-in-fixture-only. Do not silently diverge.
- **P2-LOSSY-CAST:** `distribution_channels_verified: "4/5"` → `bool` via all-or-nothing cast is a lossy information loss that a finding author cannot recover. V1.2 schema should accept a structured `{verified: int, total: int}` or string fraction. The transformer's current cast is a time bomb for a repo with 3/5 channels verified where compute.py sees `False` but the LLM would see "mostly verified."
- **P3-DOUBLE-ASSIGN:** `transform_phase_1()` assigns `branch_protection` twice (lines 208 and 218 in transform_harness.py). The second assignment (line 218) silently overwrites the first. This is a code bug in the existing transformer that will survive into V1.2 if harness absorbs transformer logic without review.

---

## DEFER items

- **D-RENDERER:** All renderer partial changes (surfacing `first_match.snippet`, per-family dangerous_primitives display) → V1.3 cycle. Not blocking V1.2 correctness.
- **D-TELEMETRY:** Override-pattern telemetry log (emit CSV of `cell, advisory_color, llm_color, rationale_first_line`) → implement alongside the 11-scan comparator analysis, post-V1.2 landing. Trigger: 3 V1.2 scans shipped.
- **D-SD2:** `auto_load_tier` C3 trigger rebinding to `domain=='agent'` → own review cycle per the brief's scope guard.
- **D-MARKITDOWN-FIXTURE:** Whether the markitdown form becomes a 4th fixture → defer until V1.2 schema is stable and form can be regenerated clean. Premature to fixture an ephemeral bridge-generated form.

---

## INFO items

- **I1:** The transformer has a `branch_protection` double-assignment bug (P3-DOUBLE-ASSIGN above) that means `branch_protection.classic.raw_response` is being set from `bp.get("classic", {}).get("body")` on first assignment and then overwritten with the same call on second. Since both calls are identical, the output is correct by accident — but if the harness ever emits different fields under `classic`, one assignment will silently win. Flag for review during harness absorption.
- **I2:** `pr_review.self_merge_count`, `pr_review.total_merged_lifetime`, and `dependencies.dependabot_config` are dropped by the transformer. `self_merge_count` is particularly valuable — the transformer re-derives `self_merge_rate` from it, then drops the denominator. V1.2 should accept the count fields alongside the rate.
- **I3:** `ossf_scorecard.http_status` (transport-level 404/503) being dropped is fine for schema V1.2 — the `indexed: bool` field captures the operational signal. The raw HTTP status is a debug artifact, not a finding input.

---

## Open questions the brief missed

- **Who populates `computed_signal_refs` in Phase 4?** The schema sketch shows it as an LLM-authored list of strings, but compute.py advisory signals need stable identifiers for the LLM to reference. Has anyone defined the signal ID vocabulary? Without it, "must cite `computed_signal_refs`" is underspecified — the LLM will invent names.
- **What is the Phase 3 container name?** The SF1 CONSOLIDATION says `phase_3_advisory.scorecard_hints` but the brief says `phase_3_computed.advisory_scorecard_cells`. These are different field paths. The schema must pick one before implementation.
- **Does `phase_3_computed` rename or get a sibling?** If scorecard cells move to Phase 4 but compute.py still runs and emits advisory signals, does `phase_3_computed` gain a new sub-object (`advisory_scorecard_cells`) or does the schema add `phase_3_advisory` as a new top-level phase? The brief is silent on this; it is a schema topology question with real implementation cost.
- **Are the 11-scan comparator analysis rider items gate-blocking for V1.2 acceptance, or post-V1.2 telemetry?** The brief lists them as "rider items" but doesn't say whether V1.2 ships without them or whether they're part of the V1.2 acceptance criteria.

---

## Blind spots

My weakest area here is the renderer surface (Q6) — I'm deferring it partly because I haven't read `render-md.py` and `render-html.py` deeply enough to know whether the D8-B2 shape changes (accepting nested per-family `dangerous_primitives` in V1.2) require partial rewrites before the renderer can process V1.2 forms at all. If the renderer directly consumes `code_patterns.dangerous_primitives.hits[]` today, and V1.2 changes that to a nested structure, then "defer renderer to V1.3" becomes inconsistent — you can't ship V1.2 forms that the V1.2 renderer can't render. The Systems Thinker should probe this coupling explicitly.
