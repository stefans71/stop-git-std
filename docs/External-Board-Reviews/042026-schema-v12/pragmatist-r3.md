# Schema V1.2 R3 — Pragmatist

## Owner directives acknowledged
- D1 (Q3 = D8-B1 harness-canonical, transformer deleted): **accepted**
- D2 (new top-level `phase_3_advisory` with `scorecard_hints`): **accepted** (I argued for sibling sub-object in `phase_3_computed` in R2; owner resolved on topology-cleanness grounds; Codex's OQ-2/OQ-3 reading is correct and cleaner)

---

## Item A — Q5 rationale-naming floor

**Resolution: (a)** — length-floor only; no substring check

**Reasoning:** Re-reading Codex's position: "structural linkage is stronger than substring check." He is right on the mechanism. The G2 floor I held in R1/R2 (rationale must name at least one listed signal as a substring) is validator theater — an LLM that wants to game it writes "I considered formal_review_rate" as the opening clause and then says whatever it wants. The structural check (ref resolves to a declared signal ID in `compute.py`'s exported vocabulary) is the actual enforcement. A substring check on top adds no semantic value and adds validator complexity. Concrete V1.2 validator: `computed_signal_refs` non-empty, every entry resolves against `SIGNAL_VOCAB` exported from `compute.py`, rationale present and length ≥ 50 chars, `override_reason` is a known enum value. These four checks together make gate 6.3 structural. I am dropping the G2 substring requirement and settling at option (a) + G3 enum.

**Validator pseudocode:**
```python
SIGNAL_VOCAB = compute.SIGNAL_IDS  # module-level frozenset from compute.py
def check_override(cell, advisory_color):
    if cell["color"] == advisory_color: return  # no override, no gate
    assert cell.get("computed_signal_refs"), "override missing computed_signal_refs"
    assert all(r in SIGNAL_VOCAB for r in cell["computed_signal_refs"]), "unknown signal ref"
    assert len(cell.get("rationale", "")) >= 50, "rationale below floor length"
    assert cell.get("override_reason") in OVERRIDE_REASON_ENUM, "invalid override_reason"
```

---

## Item B — OQ-6 migration script scope

**Resolution: (d)** — active fixtures only + explicit rule: archived artifacts stay V1.1 and any test referencing them pins to V1.1 schema via explicit annotation

**Reasoning:** Provenance.json has 4 entries: `zustand-form.json` (authored-from-scan-data, V1.1), `caveman-form.json` (back-authored, V1.1), `archon-subset-form.json` (back-authored, V1.1), `zustand-step-g-form.json` (step-g-live-pipeline, V1.1 — currently still in-flight). The `step-g-failed-artifact` category has zero current fixtures. Codex's R2 position (migrate active + archived Step G) collapses to the same 3–4 files in practice because there are no archived Step G artifacts yet. DeepSeek's "all provenance.json entries" is equivalent here too. The meaningful distinction is the forward-looking rule: when `step-g-failed-artifact` fixtures DO exist in future V1.2 cycles, do they migrate? They should not — failed artifacts are regression witnesses, not live pipeline forms, and migrating them changes what they witness. Explicit annotation (`"schema_version": "V1.1"` in provenance, test-level fixture pinning via `@pytest.mark.schema_v1_1`) is the correct mechanism.

**Files migrated:** 3 active fixtures (`zustand-form.json`, `caveman-form.json`, `archon-subset-form.json`). `zustand-step-g-form.json` migrates on Step G acceptance (provenance transitions to pipeline-produced). Zero archived/failed artifacts migrate. Update `provenance.json` `schema_version` field on each migrated fixture.

---

## Item C — override_reason enum values

**Frozen enum:**
1. `threshold_too_strict` — advisory threshold fired but the rubric's quantitative cutoff is calibrated for a different repo shape; LLM judges the behavior is better than the number suggests (e.g., 8% formal review rate for a 79-contributor Microsoft org repo)
2. `threshold_too_lenient` — advisory color is green/amber but contextual evidence shows the real risk is higher than the threshold captures (e.g., high any-review rate masking functionally-absent review in an Archon-shape solo-maintainer case)
3. `missing_qualitative_context` — threshold is correctly calibrated but Phase 1 raw data lacks a qualitative signal that changes the cell color (e.g., CONTRIBUTING.md present but not gathered by harness; community responsiveness visible in PR behavior but not in a numeric)
4. `rubric_literal_vs_intent` — the V2.4 prompt rubric text, read literally, produces one color; read for intent, produces another; LLM follows intent (this is the zustand Q3 / DeepSeek R4 preserved dissent case)
5. `other` — escape hatch; must still include non-trivial rationale and `computed_signal_refs`

**Reasoning per departure from Codex R1 / DeepSeek R1:** Codex R1 C-3 had 5 values; DeepSeek R1 C-2 had 3. I am adopting Codex's 5-value list with one delta: `threshold_too_strict` and `threshold_too_lenient` are retained as-is because directionality matters for calibration telemetry (both fire the comparator analysis but in opposite calibration directions). `missing_qualitative_context` preserved verbatim — this is the most common real-world case. `rubric_literal_vs_intent` retained — it is the explicitly preserved DeepSeek R4 dissent case from SF1 and belongs in the frozen vocabulary. `other` retained as escape hatch. DeepSeek R1's 3-value list collapses threshold direction into one value, losing the calibration signal. This list is renderer-safe (all 5 values are human-readable short strings) and validator-safe (closed enum comparison).

---

## Item D — renderer dangerous_primitives coupling

**Resolution: (b)** — compute-layer flatten: add `compute.py::flatten_dangerous_primitives(form)` helper that produces a `hits[]`-compatible structure from the nested per-family schema input; renderer partials unchanged

**Reasoning:** I re-read the actual renderer partials. The finding: `dangerous_primitives` is NOT currently consumed by any Jinja2 partial in `docs/templates/` or `docs/templates-html/`. No template references `hits[]`, `hit_count`, `dangerous_primitives`, or `agent_rule_files`. The renderer currently surfaces dangerous primitives only via LLM-authored Phase 4 findings — the raw Phase 1 `code_patterns.dangerous_primitives` block flows through to Phase 4 as context for finding authoring, but it is NOT iterated by the renderer. This changes the Item D calculus significantly: the renderer coupling concern is valid for V1.3 (when we might want to auto-render the family breakdown in §01/§02 finding cards), but it is NOT blocking V1.2 schema acceptance. However, D1's directive to preserve the nested per-family shape in schema still requires the `compute_coverage_status()` function and any future renderer work to be able to consume it. The correct V1.2 preparation is option (b): add a thin `flatten_dangerous_primitives(form)` helper in `compute.py` that emits `{hits: [{family, file, line, snippet}], hit_count: int}` from the nested schema. This is the bridge for any compute.py advisory signal that reads family-level data (e.g., flagging exec hits), and it is the adapter a V1.3 renderer partial would call rather than re-implementing the flatten inline. Zero renderer partial lines touched in V1.2.

**Concrete change location:** `docs/compute.py` — add ~15-line helper `flatten_dangerous_primitives(dp: dict) -> dict` after the existing `compute_coverage_status()` function. Renderer partial lines touched in V1.2: **0**. Schema partial for dangerous_primitives: type accepted as nested per-family object (harness-canonical, D1 directive).

---

## Item E — agent_rule_files total_bytes heuristic

**Resolution: (b)** — require raw `line_count` per entry; compute bytes in `compute.py`; schema does NOT store `total_bytes`

**Reasoning:** The transformer's `total_bytes = sum(line_count × 50)` is the only heuristic in the pipeline — everything else in compute.py is derivable from observable data. Canonizing it in schema locks in the 50-bytes/line constant as a schema guarantee, which is wrong: the actual file encoding, indentation style, and content type (dense code vs sparse YAML) can easily span 30–80 bytes/line. DeepSeek's I-1 concern is correct. Option (c) (true byte count from tarball) is the right long-term answer but requires a harness change that is not trivially safe (tarball may be deleted before byte-count step). Option (b) is the pragmatist choice: the harness already emits per-entry `line_count` (confirmed in the sidecar), so schema accepts `line_count` per entry and `compute.py` derives `total_bytes` at compute time using the same 50-bytes/line heuristic — but the heuristic lives in one place (compute.py, documented as approximate), not frozen into the schema. When V1.3 harness gathers true byte counts, compute.py swaps its derivation and schema adds `file_bytes` per entry without a breaking change.

**Concrete change:** Schema: `agent_rule_files` entries accept `line_count: integer` (already emitted by harness), do NOT include `total_bytes` as a schema field. `compute.py`: add `compute_agent_rule_bytes(entries: list) -> int` returning `sum(e.get("line_count", 0) * 50 for e in entries)`. Renderer partial: calls `compute_agent_rule_bytes` when it needs a byte total for display (V1.3 work). Migration script: drops `total_bytes` from any V1.1 fixture `agent_rule_files` wrapper object that has it.

---

## Item F — signal ID vocabulary

| ID | Type | Derived from | Kind |
|---|---|---|---|
| `formal_review_rate` | number | `pr_review.formal_review_rate` (fraction 0–1) | scorecard_input |
| `any_review_rate` | number | `pr_review.any_review_rate` (fraction 0–1) | scorecard_input |
| `has_branch_protection` | bool | `branch_protection.classic.status == 200` | scorecard_input |
| `has_codeowners` | bool | `codeowners.found` | scorecard_input |
| `is_solo_maintainer` | bool | `phase_3_computed.solo_maintainer.is_solo` | scorecard_input |
| `open_security_issue_count` | number | `issues_and_commits.open_security_issues` | scorecard_input |
| `oldest_open_cve_pr_age_days` | number | `pr_review.oldest_security_pr_age_days` | scorecard_input |
| `has_security_policy` | bool | `community_profile.has_security_policy` | scorecard_input |
| `published_advisory_count` | number | `security_advisories.count` | scorecard_input |
| `has_silent_fixes` | bool | `phase_3_computed.f5_silent` result field | scorecard_input |
| `all_channels_pinned` | bool | `distribution_channels.all_pinned` | scorecard_input |
| `artifact_verified` | bool | `artifact_verification.verified` | scorecard_input |
| `has_critical_on_default_path` | bool | derived: any finding with severity=Critical on default install path | scorecard_input |
| `has_warning_on_install_path` | bool | `install_script_analysis.has_warning` or finding classification | scorecard_input |
| `has_contributing_guide` | bool | `community_profile.has_contributing` | scorecard_input |
| `closed_fix_lag_days` | number | `pr_review.closed_security_pr_lag_days` | scorecard_input |
| `governance_floor_override` | bool | computed: `formal_review_rate < 0.10 AND NOT has_branch_protection AND NOT has_codeowners` | scorecard_input |
| `has_rulesets` | bool | `branch_protection.rulesets` non-empty | supporting |
| `has_rules_on_default` | bool | `branch_protection.rules_on_default` non-empty | supporting |
| `has_recent_release_30d` | bool | `releases.latest_date` within 30 days of scan | supporting |
| `ships_executable_code` | bool | `distribution_channels` includes installable binary/script | supporting |
| `top_contributor_share` | number | `phase_3_computed.solo_maintainer.top_contributor_share` | supporting |
| `ossf_overall_score` | number | `ossf_scorecard.overall_score` | supporting |
| `dependabot_active` | bool | `dependencies.dependabot_alerts.status == "active"` | supporting |

**Draft-subject-to-rename:** `has_critical_on_default_path` and `has_warning_on_install_path` — these derive from LLM-authored finding classification, which makes them Phase 4 outputs, not pure Phase 1 signals. They are currently used as compute.py Q4 inputs (V1.1 parity) but their derivation path is not fully automated. Mark as draft until Phase 1 harness emits these directly from tarball/install-script analysis. Also `closed_fix_lag_days` — the field name in the harness output varies; pin the name before freezing.

**Reasoning on contentious choices:** The 17 scorecard_input signals map directly to `compute_scorecard_cells()` parameters plus the governance-floor-override condition. This is the authoritative set for `phase_3_advisory.scorecard_hints.*.signals[]` because any signal in the advisory computation must be in this list. The 7 supporting signals are ones compute.py reads (e.g., for `compute_c20_severity`) or that the LLM commonly needs when overriding (e.g., OSSF score, Dependabot status) but that don't feed directly into the Q1–Q4 scorecard thresholds. The exported vocabulary in compute.py should be a module-level `frozenset` called `SIGNAL_IDS` populated from both columns. Codex's OQ-1 position (compute.py populates stable signal IDs under `phase_3_advisory.scorecard_hints.<qid>.signals[]`) is correct and matches the D2 directive topology. The LLM's `computed_signal_refs` in Phase 4 must draw from `SIGNAL_IDS`. No signals are added here that cannot currently be derived from existing Phase 1 harness output or Phase 3 compute.py functions — scope creep risk is low.

---

## Unresolved items for R4

None — all 6 items have concrete resolutions ready for V1.2 implementation.

Pre-archive dissent audit note: My R2 OQ-2/OQ-3 position (sibling sub-object in `phase_3_computed`) was resolved by Owner directive D2. Recorded as accepted-dissent, not escalation. DeepSeek's R1 B3 position was resolved by Owner directive D1. No silent drops.

---

## Blind spots

The `has_critical_on_default_path` and `has_warning_on_install_path` signal derivation remains partially manual — they are computed from LLM-authored finding classifications in V1.1, not from raw Phase 1 data. I have flagged them as draft-subject-to-rename but I have not verified how the Phase 4 LLM is currently instructed to set these. If they are not derived from a named harness field, the signal ID vocabulary for Q4 advisory computation is partially circular (Phase 4 LLM sets the signal that the Phase 3 advisory uses to compute Q4's advisory color). This circular dependency is acceptable for V1.2 as a known limitation, but it should be documented in `compute.py`'s `SIGNAL_IDS` docstring.

I also did not re-read `render-html.py` directly — I inferred from `render-md.py` symmetry. The HTML scorecard partial (`scorecard.html.j2`) reads `phase_3_computed.scorecard_cells` at line 16 — same coupling as the MD partial. Both require the 1-line path change to `phase_4_structured_llm.scorecard_cells` under D2. That is confirmed. The HTML `dangerous_primitives` coupling is confirmed absent (no templates reference it).
