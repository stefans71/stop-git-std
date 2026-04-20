# Schema V1.2 R3 — Codex

## Owner directives acknowledged
- D1 (Q3 = D8-B1 harness-canonical, transformer deleted): accepted
- D2 (new top-level phase_3_advisory with scorecard_hints): accepted

## Item A — Q5 rationale-naming floor
**Resolution:** (a)
**Reasoning:** Structural linkage is the stronger contract. Once `computed_signal_refs` points at stable signal IDs emitted under `phase_3_advisory.scorecard_hints.<qid>.signals[]`, forcing free-text prose to repeat one of those snake_case IDs adds noise without improving auditability. It is also a bad fit for Phase 4 authoring quality: the LLM should explain the override in natural language, while the validator checks machine-resolved refs. This couples cleanly to Item F because validator logic becomes pure membership/resolution against the frozen signal vocabulary, not brittle substring matching. It also couples cleanly to telemetry: `override_reason` carries the categorical reason, while `computed_signal_refs` carries the cited advisory inputs. Requiring prose mention of IDs would create a third semi-structured channel that post-V1.2 analysis would have to ignore anyway.
**Validator pseudocode:**
```python
if llm_cell["color"] != advisory_hint["color"]:
    advisory_signal_ids = {s["id"] for s in advisory_hint.get("signals", [])}
    assert len((llm_cell.get("rationale") or "").strip()) >= 40
    refs = llm_cell.get("computed_signal_refs") or []
    assert refs and all(ref in advisory_signal_ids for ref in refs)
    assert llm_cell.get("override_reason") in OVERRIDE_REASON_ENUM
```

## Item B — OQ-6 migration script scope
**Resolution:** (b)
**Reasoning:** Migrate live V1.1 fixtures plus archived Step G artifacts that are already used as audit/test evidence. That is the smallest scope that avoids a split archive where some pipeline-produced or near-pipeline artifacts remain on a dead schema while tests and board records compare them against V1.2 behavior. Option (a) leaves the exact artifacts most likely to be consulted during regression work stranded on V1.1. Option (c) is too broad because `provenance.json` also tracks non-pipeline test fixtures and does not justify bulk-touching every historical asset. Under D1, markitdown’s bridge-generated `form.json` should not be migrated; it should be regenerated from harness-native V1.2 once needed. This keeps the migration deterministic and bounded while preserving audit continuity across Step G.
**Files migrated:** ~7 files total: `tests/fixtures/{zustand-form,caveman-form,archon-subset-form}.json`; `.board-review-temp/step-g-execution/{zustand-step-g-form,caveman-step-g-form,Archon-step-g-form}.json`; `tests/fixtures/provenance.json` schema_version updates.

## Item C — override_reason enum values
**Frozen enum:**
1. `threshold_too_strict` — advisory threshold produced a harsher color than the Phase 4 judgment warrants.
2. `threshold_too_lenient` — advisory threshold produced a softer color than the Phase 4 judgment warrants.
3. `missing_qualitative_context` — advisory inputs are directionally useful but omit qualitative evidence the Phase 4 judgment must account for.
4. `rubric_literal_vs_intent` — advisory followed a literal threshold or rule, but the final judgment follows rubric intent/documented interpretation.
5. `other` — residual bucket requiring rationale text when none of the four canonical categories fit.
**Reasoning per departure from Codex R1 / DeepSeek R1 proposals:** I would freeze the 5-value list from my R1 unchanged. DeepSeek’s shorter vocabulary is too compressed for telemetry because it collapses directional threshold errors into one bucket; post-V1.2 analysis needs to distinguish “too strict” from “too lenient” to recalibrate compute thresholds sanely. I would also not split `other` further in V1.2 because that weakens determinism and increases prompt burden before we have real override volume. This list is finite, directional where needed, and directly consumable by validator rules, telemetry aggregation, and simple renderer disclosure if the category is ever surfaced later.

## Item D — renderer dangerous_primitives coupling
**Resolution:** (d)
**Reasoning:** After re-reading the actual templates and tests, the current renderer is not consuming `code_patterns.dangerous_primitives` at all. The only forced renderer coupling in V1.2 is the scorecard path migration from `phase_3_computed.scorecard_cells` to `phase_4_structured_llm.scorecard_cells`; there is no live `hits[]` dependency to preserve. Adding a flattening adapter now would create a second representation with no consumer, which is exactly the sort of needless compatibility layer that caused D-8 trouble. The clean V1.2 answer is therefore: keep the nested per-family schema shape, make no dangerous-primitives renderer adaptation, and add a regression assertion or comment documenting that renderers are intentionally decoupled from this Phase 1 field until a future section actually needs it. That preserves determinism tests because none of the existing render tests assert on dangerous-primitives shape.
**Concrete change location:** No Jinja partial changes for `dangerous_primitives`; `0` partial lines touched. Mandatory but separate V1.2 renderer/test edits remain in `docs/templates/partials/scorecard.md.j2`, `docs/templates-html/partials/scorecard.html.j2`, and `tests/test_render_md.py` for the scorecard path move.

## Item E — agent_rule_files total_bytes heuristic
**Resolution:** (d)
**Reasoning:** Do not canonize fake bytes. The current `line_count × 50` number is neither raw evidence nor a trustworthy derived metric, and under B1 it would become part of the public contract for no good reason. Option (c) true byte counts are cleaner in principle but widen harness scope and degrade badly under API-tree fallback, where file contents are not always fetched. The least coupled V1.2 answer is to keep the harness-native per-entry `line_count` and drop `total_bytes` from schema entirely. If the renderer later wants a size-like aggregate, it can show file count or total lines, both of which are deterministic and honest. This also avoids poisoning Item F-style signal vocabularies with pseudo-quantitative data that operators may over-interpret.
**Concrete change:** Schema adopts harness-native `code_patterns.agent_rule_files: [{path, kind, line_count, ci_amplified, ...}]` list; migration removes wrapper `{entries,count,total_bytes}`; harness unchanged; renderer omits byte summary; any future aggregate should be `total_lines`, not pseudo-bytes.

## Item F — signal ID vocabulary
| ID | Type | Derived from | Kind |
|---|---|---|---|
| `q1_formal_review_rate` | number | `phase_1_raw_capture.pr_review.formal_review_rate` | scorecard_input |
| `q1_any_review_rate` | number | `phase_1_raw_capture.pr_review.any_review_rate` | scorecard_input |
| `q1_has_branch_protection` | bool | `phase_1_raw_capture.branch_protection.classic.status` or rules on default branch | scorecard_input |
| `q1_has_codeowners` | bool | `phase_1_raw_capture.codeowners.found` | scorecard_input |
| `q1_is_solo_maintainer` | bool | `phase_3_computed.solo_maintainer.is_solo` derived from contributor share | scorecard_input |
| `q1_governance_floor_override` | bool | `q1_formal_review_rate` + no branch protection + no CODEOWNERS | scorecard_input |
| `q2_open_security_issue_count` | number | `phase_1_raw_capture.issues_and_commits.open_issues_count` / open security issue set | scorecard_input |
| `q2_oldest_open_cve_pr_age_days` | number | `phase_1_raw_capture.open_prs.entries[]` age analysis | scorecard_input |
| `q2_closed_fix_lag_days` | number | closed security-fix PR lag derived from Phase 1 PR data | scorecard_input |
| `q3_has_security_policy` | bool | `phase_1_raw_capture.community_profile.has_security_policy` | scorecard_input |
| `q3_has_contributing_guide` | bool | `phase_1_raw_capture.community_profile.has_contributing` | scorecard_input |
| `q3_published_advisory_count` | number | `phase_1_raw_capture.security_advisories.count` | scorecard_input |
| `q3_has_silent_fixes` | bool | Phase 3 F5 disclosure classification against releases/advisories | scorecard_input |
| `q3_has_reported_fixed_vulns` | bool | public vuln-history proxy from advisories/issues/PR evidence | scorecard_input |
| `q4_all_channels_pinned` | bool | `phase_1_raw_capture.distribution_channels.channels[]` pinning state | scorecard_input |
| `q4_artifact_verified` | bool | `phase_1_raw_capture.artifact_verification.per_channel[]` | scorecard_input |
| `q4_has_critical_on_default_path` | bool | Phase 4 findings tagged to default install/runtime path | scorecard_input |
| `q4_has_warning_on_install_path` | bool | Phase 4 findings tagged to install path warning scope | scorecard_input |
| `c20_has_classic_protection` | bool | inverse of `branch_protection.classic.status == 404` | supporting |
| `c20_has_rulesets` | bool | `phase_1_raw_capture.branch_protection.rulesets.count > 0` | supporting |
| `c20_has_rules_on_default` | bool | `phase_1_raw_capture.branch_protection.rules_on_default.count > 0` | supporting |
| `c20_has_recent_release_30d` | bool | `phase_1_raw_capture.releases.entries[0].published_at` vs scan date | supporting |
| `c20_ships_executable_code` | bool | executable/install-surface signals from Phase 1 code/dependency analysis | supporting |
**Draft-subject-to-rename:** None.
**Reasoning on contentious choices:** I am freezing question-scoped IDs for the authoritative advisory signals, not generic prose labels. That makes Item A validator logic trivial: each `computed_signal_refs` entry resolves against the exact IDs emitted under the matching question’s advisory hint. I also kept Q4’s two install-path signals even though they depend on later classification, because V1.2 already assumes advisory scorecard hints can consume computed inputs beyond raw Phase 1 capture; omitting them would make the most important Q4 overrides uncitable. By contrast, I did not freeze every compute intermediate as a first-shipment signal. The C20 support set is enough to let Phase 4 cite governance context without bloating the vocabulary into an unmaintainable ontology. The naming rule should be: stable snake_case, question-scoped for scorecard inputs, family-scoped for supporting signals, and never overloaded with display prose.

## Unresolved items for R4
None — all 6 items have concrete resolutions ready for V1.2 implementation.

## Blind spots
I did not find any live renderer consumption of `dangerous_primitives`, but that conclusion depends on grep-visible template usage in the files I re-read. If a hidden helper or downstream non-test renderer path consumes `hits[]`, Item D would need a compatibility adapter after all. The other uncertainty is prompt ergonomics: the stricter Item A/F contract is architecturally cleaner, but it assumes Phase 4 prompting will reliably teach the LLM to cite signal IDs without degrading rationale quality.
