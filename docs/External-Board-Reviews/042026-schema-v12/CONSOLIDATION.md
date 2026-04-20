# Schema V1.2 Board Review — CONSOLIDATION

**Topic:** Scan-schema V1.2 design — co-scheduled D-7 (scorecard cell authority migration) + D-8 (schema hardening for harness output).

**Date range:** 2026-04-20 (single-session, 3 rounds + owner directives)

**HEAD at sign-off:** `4512084` on origin/main

**Board composition:**
- **Pragmatist:** Claude Sonnet 4.6 via `Agent` tool (same-model blind-spot rule — operator authored the R1 brief using Opus)
- **Systems Thinker:** Codex GPT-5 via `sudo -u llmuser bash -c "cd /tmp && codex exec --dangerously-bypass-approvals-and-sandbox ..."`
- **Skeptic:** DeepSeek V4 via `OPENAI_API_KEY=$DEEPSEEK_API_KEY OPENAI_BASE_URL=https://api.deepseek.com/v1 qwen -y -p ... --model deepseek-chat`

**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md` — pre-archive dissent audit mandatory per §4.

**Outcome:** **SIGN OFF with owner directives on 2 structural decisions and 6 substantive item resolutions.** All 3 agents signed off on R3 with "None for R4 — all 6 items have concrete resolutions ready for V1.2 implementation." Owner closed remaining splits by directive.

**Dissent audit result:** ✅ **PASS** — zero silent drops. 24 discrete R1+R2+R3 items traced. 19 resolved by outcome, 5 preserved as accepted dissents in §6 below.

---

## 1. Round summary

| Round | Type | Agents | Purpose | Outcome |
|---|---|---|---|---|
| R1 | Blind | P+C+DS | Open scoping on 7 questions (Q1–Q7) | 5/7 converged, 2/7 split (Q3 shape, Q5 override mechanics); 3 transformer bugs surfaced and verified |
| R2 | Consolidation | P+C+DS | Respond to R1 positions, merge or defend | Q3 resolved 2-1 by vote (D8-B1 majority); Q5 near-converged on G3+G4; 9 open questions surfaced (OQ-1 through OQ-9); 2 structural topology questions (OQ-2/OQ-3) remained split 2-1 |
| Owner directive | — | Operator | Close Q3 + OQ-2/OQ-3 | D1 (Q3=B1) + D2 (phase_3_advisory new top-level) |
| R3 | Deliberation (narrow) | P+C+DS | Close 6 remaining substantive items (A-F) | All 3 agents reported "None for R4"; real diffs on 6 items closed by owner directive |

**Timing:**
- R1 ~10 min (3 agents in parallel)
- R2 ~15 min
- R3 ~18 min
- Total elapsed clock time: ~50 min of LLM work + owner-directive decision time

---

## 2. Owner directives (issued between R2 and R3)

### D1 — Q3 shape: D8-B1 (harness-canonical, transformer deleted)

**Basis:** R2 majority 2/3 (Pragmatist flipped R1 B2-scoped → R2 B-merged ≈ B1; Codex held B1). DeepSeek's R2 B2-scoped (flipped from R1 B3) preserved schema `is_` / `has_` prefix convention. Owner resolved on majority + cleaner contract.

**Concrete V1.2 schema deltas:**

- Field names match harness output natively:
  - `repo_metadata.archived` (not `is_archived`)
  - `repo_metadata.fork` (not `is_fork`)
  - `repo_metadata.default_branch` (not `default_branch_ref`)
  - `pre_flight.api_rate_limit.reset` (epoch int)
  - `dependencies.dependabot_alerts` (not `dependabot`)
  - `dependencies.osv_lookups` (not `osv_dev`)
- Harness gathers: `open_issues_count`, `size_kb` (already emitted, schema V1.2 accepts)
- Harness additions required: `has_issues_enabled`, `primary_language`, `topics`, `fork_count` (nullable if not gathered; acceptable to add in V1.2.x)
- Shapes preserved:
  - `code_patterns.dangerous_primitives.{exec, deserialization, network, ...15 families}.files[].first_match.{line, snippet}` nested preserved
  - `code_patterns.executable_files` as list (not `{entries: []}` wrapper)
  - `code_patterns.install_hooks` as list
  - `code_patterns.agent_rule_files` as list (per-entry `{path, kind, line_count, ci_amplified, ...}`)
  - `dependencies.manifest_files: [{path, format}]` (objects, not strings)
- Type richness restored:
  - `pre_flight.symlinks_stripped: integer` (count, not bool)
  - `coverage_affirmations.windows_surface_coverage: string` (status, not bool)
  - `coverage_affirmations.distribution_channels_verified: {verified: int, total: int}` (object, not bool)
- Transformer (`.board-review-temp/markitdown-scan/transform_harness.py`) **deleted** from V1.2 path
- Bug P3-DOUBLE-ASSIGN auto-resolves via deletion

### D2 — OQ-2/OQ-3 topology: new top-level `phase_3_advisory` with `scorecard_hints`

**Basis:** Codex R2 reasoning — keeps `phase_3_computed` owning its 7 deterministic outputs unambiguously; aligns with SF1 CONSOLIDATION wording (`phase_3_advisory.scorecard_hints`). Pragmatist + DeepSeek preferred sibling sub-object inside `phase_3_computed`. Owner resolved on topology-cleanness.

**Concrete V1.2 schema deltas:**

- New top-level: `phase_3_advisory`
  - `scorecard_hints` — keyed object by canonical question ID:
    - `does_anyone_check_the_code`
    - `do_they_fix_problems_quickly`
    - `do_they_tell_you_about_problems`
    - `is_it_safe_out_of_the_box`
  - each key → `{color, short_answer, signals: [{id, value, ...}], $comment?}`
- `phase_3_computed.scorecard_cells` **deleted** (authority moves to Phase 4)
- `phase_4_structured_llm.scorecard_cells` — keyed object by canonical question ID (OQ-4 unanimous: keyed not array):
  - each key → `{color, short_answer, rationale, edge_case, suggested_threshold_adjustment, computed_signal_refs: [string], override_reason: enum}`
- `compute.compute_scorecard_cells()` demoted to advisory; populates `phase_3_advisory.scorecard_hints`
- 7 other `compute.py` ops remain in `phase_3_computed` unchanged; Step 3b byte-for-byte equality retained for those 7
- Gate 6.3 changes from "cell-by-cell match" to "override-explained" per Item A

---

## 3. Q1–Q7 final votes + OQ-1–OQ-9 resolutions

| Q | Question | Final resolution | Basis |
|---|---|---|---|
| Q1 | Coordinated vs staged | **Coordinated** | 3/3 unanimous R1 |
| Q2 | compute.py authority | **D7-A1** (must cite signals when overriding) | 3/3 unanimous R1 |
| Q3 | V1.2 shape winner | **D8-B1** (harness-canonical) | Owner directive D1 on R2 2/3 majority |
| Q4 | Back-compat | **Migration script** | 3/3 unanimous R1 |
| Q5 | Override mechanics | **D7-G3+G4** (enum + validator) + Item A refs-only floor | R2 near-converged, R3 Item A closes |
| Q6 | Renderer surface in V1.2 | **Narrow** (scorecard path only; no new-feature expansion; `dangerous_primitives` empirically has no current consumer) | 3/3 R2 converged; R3 Item D confirmed |
| Q7 | Scope guard | **SD2, PD3, Package V2.5, Scanner-Integrity §00, D-4 all OUT** | 3/3 unanimous R1 |

| OQ | Question | Final resolution | Basis |
|---|---|---|---|
| OQ-1 | Signal ID vocabulary | Codex R3 question-scoped prefix (`q1_` / `q2_` / `q3_` / `q4_` / `c20_`) — see §5 Item F | Owner directive post-R3 |
| OQ-2 | Phase 3 container name | `phase_3_advisory.scorecard_hints` | Owner directive D2 |
| OQ-3 | Rename or sibling | New top-level phase | Owner directive D2 |
| OQ-4 | scorecard_cells shape | Keyed object by canonical question ID | 3/3 R2 unanimous |
| OQ-5 | Gate 6.3 mechanism | Schema + validator (Item A enforces) | 3/3 R2 converged |
| OQ-6 | Migration scope | Active fixtures only + annotation rule for archived | Owner directive post-R3 (Item B) |
| OQ-7 | Partial Phase 1 | Nullable optional substructures; `phase_2_validation` flags partial | 3/3 R2 converged (wording variations only) |
| OQ-8 | V2.4-only catalog migration | Stay V2.4-rendered indefinitely unless re-scanned | 3/3 R2 unanimous |
| OQ-9 | Phase 4 LLM sidecar access | No sidecar needed — B1 absorbs richness natively; LLM reads `phase_1_raw_capture` directly | Resolved logically by D1 (Codex + DeepSeek position); Pragmatist dissent preserved (§6) |

---

## 4. Ground-truth transformer bugs (P1–P3)

All 3 verified by operator against source pre-R2 and absorbed by D1 (transformer deletion).

| ID | Bug | Status |
|---|---|---|
| **P1-RENAME** | `transform_repo_metadata()` hardcodes `has_issues_enabled: None`, `primary_language: None`, `topics: []`, `fork_count: None`. Harness doesn't gather these. Operator-extended finding: harness does emit `open_issues_count`, `size_kb` which transformer silently drops (not in V1.1 schema). | ✅ Resolved by D1: schema V1.2 adopts harness fields natively; missing-from-harness fields become nullable until harness gathers them; `open_issues_count` + `size_kb` accepted. |
| **P2-LOSSY-CAST** | `_transform_coverage_affirmations()` casts `"4/5"` to `False` via `int(num) == int(denom)`. Loses partial-coverage granularity. `windows_surface_coverage` same pattern. | ✅ Resolved by D1: schema V1.2 accepts `{verified: int, total: int}` for distribution channels; string status for windows coverage. |
| **P3-DOUBLE-ASSIGN** | `transform_phase_1()` assigns `branch_protection` twice (lines 208, 218). Silent overwrite. Result correct by accident (identical calls). | ✅ Resolved by D1: transformer file deleted entirely. |

---

## 5. Six R3 item resolutions

### Item A — Q5 rationale-naming floor

**Resolution: (a) refs-only + length floor + enum check. NO substring check in rationale.**

**Majority:** P + C (2/3). DeepSeek dissented to (b) substring check. Owner resolved on majority + gameability argument.

**Validator pseudocode** (lands in `docs/validate-scanner-report.py`):

```python
def validate_override_rationale(cell, advisory_hint):
    if cell["color"] == advisory_hint["color"]:
        return  # no override — no enforcement required
    rationale = cell.get("rationale", "") or ""
    refs = cell.get("computed_signal_refs", []) or []
    reason = cell.get("override_reason")
    if reason not in OVERRIDE_REASON_ENUM:
        raise ValidationError(f"override_reason must be enum value, got {reason!r}")
    if len(rationale) < 50:
        raise ValidationError("Override rationale must be >= 50 chars")
    if not refs:
        raise ValidationError("Override requires computed_signal_refs non-empty")
    unknown = [r for r in refs if r not in compute.SIGNAL_IDS]
    if unknown:
        raise ValidationError(f"computed_signal_refs contains unknown IDs: {unknown}")
```

**Dissent preserved:** DeepSeek's substring check. Rationale: "substring is strictly better than length-only — forces the LLM to at least mention the signal name." Owner counter: substring is gameable (dropping a signal name without meaningful engagement meets the check); structural ref resolution + length floor is the minimum-viable floor that resists gaming while staying computable.

### Item B — OQ-6 migration script scope

**Resolution: (d) active fixtures only + explicit annotation rule for archived.**

**Majority:** P + DS (2/3). Codex dissented to (b) active + archived Step G. Owner resolved on majority + regression-witness preservation logic.

**Files migrated by `migrate-v1.1-to-v1.2.py`:**
1. `tests/fixtures/zustand-form.json`
2. `tests/fixtures/caveman-form.json`
3. `tests/fixtures/archon-subset-form.json`

**Rule for archived artifacts:** `step-g-failed-artifact`-tagged entries in `tests/fixtures/provenance.json` **stay on V1.1 schema**. Any test importing a failed-artifact fixture must add `# schema: V1.1` pin comment and the test harness validates it against V1.1 schema. New schema-agnostic tests should not reference failed-artifact fixtures.

**`zustand-step-g-form.json`** (currently `step-g-live-pipeline`) migrates when it transitions to `pipeline-produced` status.

**`provenance.json` update:** migrated fixtures update their `schema_version` field from `1.1` → `1.2`. Failed-artifact entries remain `1.1`.

**Dissent preserved:** Codex's (b) — preferred regenerating archived Step G artifacts that tests reference to keep schema-version consistency across test corpus. Owner counter: failed-artifact fixtures are regression witnesses (captured schema-V1.1-specific failure modes); migrating them erases the regression witness value.

### Item C — override_reason enum (5-value, frozen)

**Frozen V1.2 enum:**

1. **`threshold_too_strict`** — advisory threshold produced a harsher color than the Phase 4 judgment warrants
2. **`threshold_too_lenient`** — advisory threshold produced a softer color than the Phase 4 judgment warrants
3. **`missing_qualitative_context`** — advisory inputs are directionally useful but omit qualitative evidence the Phase 4 judgment must account for
4. **`rubric_literal_vs_intent`** — advisory followed a literal threshold or rule; final judgment follows rubric intent/documented interpretation
5. **`other`** — residual bucket requiring rationale text when none of the four canonical categories fit

**Majority:** P + C (2/3) on Codex R1's list unchanged. DeepSeek proposed adding `community_norms_differ` (6th value). Owner resolved on majority.

**Dissent preserved:** DeepSeek's `community_norms_differ`. Owner mapping rule: "community norms differ from rubric" overrides should categorize as **`missing_qualitative_context`** with the community-norms context named explicitly in the rationale. If post-V1.2 telemetry shows ≥3 distinct scans using "community norms" as the override reason within `missing_qualitative_context`, revisit in V1.3 for enum expansion (trigger logged).

**Frozen list is minimal** — renderer test, validator, and telemetry all consume finite set. New enum values require V1.3 schema bump.

### Item D — renderer `dangerous_primitives` coupling

**Resolution: no renderer partial edits for `dangerous_primitives` in V1.2. Schema adopts nested per-family shape per D1.**

**Majority:** P + C (2/3), both independently grepped templates and found **no current consumer**. DeepSeek's R2 mandatory-scope premise was empirically falsified.

**Empirical finding:** No Jinja2 template in `docs/templates/` or `docs/templates-html/` references `dangerous_primitives`, `hits[]`, or `agent_rule_files` directly. No `test_render_md.py` or `test_render_html.py` assertion on these shapes. Zero partial lines touched for `dangerous_primitives` in V1.2.

**Forward compatibility:** a regression comment in the schema `$comment` for `dangerous_primitives` notes "no renderer consumer as of V1.2; renderer V1.3 should consume nested shape directly, not re-flatten."

**Dissent preserved:** DeepSeek's (a) nested-partials proposal (30-40 lines). Logically moot because the premise was wrong; carried as V1.3 guidance if/when a renderer consumer is added.

**Mandatory V1.2 renderer edits that DO land** (Q6-narrow, from D2):

- `docs/templates/partials/scorecard.md.j2` — path change from `phase_3_computed.scorecard_cells` → `phase_4_structured_llm.scorecard_cells`
- `docs/templates-html/partials/scorecard.html.j2` — same path change
- `tests/test_render_md.py` + `tests/test_render_html.py` — assertion path update
- New fields added to scorecard cell (rationale, edge_case, suggested_threshold_adjustment, computed_signal_refs, override_reason) — partials optionally surface these; V1.2 scope keeps renderer output shape near-identical to V1.1

### Item E — `agent_rule_files.total_bytes` heuristic

**Resolution: (d) drop `total_bytes` from schema entirely.**

**Majority:** all 3 agree schema does NOT store `total_bytes` in V1.2. Agreement on "drop from schema" is 3/3. Disagreement only on whether a helper exists: Codex (d) says no helper; Pragmatist (b) and DeepSeek (b) would add a compute.py or renderer helper if the need arises. Owner resolved on (d) minimal: no schema field, no helper in V1.2 baseline; add later if a consumer emerges.

**Concrete V1.2 changes:**

- Schema `code_patterns.agent_rule_files` adopts harness-native list shape per D1 (per-entry `line_count` present)
- Schema does NOT define `total_bytes` at any level
- `compute.py` does NOT get a `compute_agent_rule_bytes()` helper in V1.2 baseline
- Migration script drops `total_bytes` from V1.1 fixtures (`tests/fixtures/zustand-form.json` + `caveman-form.json` + `archon-subset-form.json`)
- If renderer ever wants an aggregate, use `total_lines = sum(line_count for entries)` — deterministic and honest

**Dissent preserved:** P + DS preferred keeping a helper for bytes aggregation if display needs it. Owner counter: `total_lines` is the honest aggregate; pseudo-bytes on a 50-chars/line heuristic is not trustworthy data; no consumer wants it today.

### Item F — signal ID vocabulary (frozen)

**Resolution: Codex R3's 23-row question-scoped-prefix table is the FROZEN V1.2 vocabulary. Exported as `compute.SIGNAL_IDS` frozenset. Post-V1.2 additions require V1.2.x patch; removals require V1.3 bump.**

**Frozen V1.2 signal IDs:**

| ID | Type | Derived from | Kind |
|---|---|---|---|
| `q1_formal_review_rate` | number | `phase_1_raw_capture.pr_review.formal_review_rate` | scorecard_input |
| `q1_any_review_rate` | number | `phase_1_raw_capture.pr_review.any_review_rate` | scorecard_input |
| `q1_has_branch_protection` | bool | `phase_1_raw_capture.branch_protection.classic.status` or rules on default branch | scorecard_input |
| `q1_has_codeowners` | bool | `phase_1_raw_capture.codeowners.found` | scorecard_input |
| `q1_is_solo_maintainer` | bool | `phase_3_computed.solo_maintainer.is_solo` (derived from contributor share) | scorecard_input |
| `q1_governance_floor_override` | bool | q1_formal_review_rate + no branch protection + no CODEOWNERS (composite) | scorecard_input |
| `q2_open_security_issue_count` | number | `phase_1_raw_capture.issues_and_commits.open_issues_count` | scorecard_input |
| `q2_oldest_open_cve_pr_age_days` | number | `phase_1_raw_capture.open_prs.entries[]` age analysis | scorecard_input |
| `q2_closed_fix_lag_days` | number | closed security-fix PR lag | scorecard_input |
| `q3_has_security_policy` | bool | `phase_1_raw_capture.community_profile.has_security_policy` | scorecard_input |
| `q3_has_contributing_guide` | bool | `phase_1_raw_capture.community_profile.has_contributing` | scorecard_input |
| `q3_published_advisory_count` | number | `phase_1_raw_capture.security_advisories.count` | scorecard_input |
| `q3_has_silent_fixes` | bool | Phase 3 F5 disclosure classification | scorecard_input |
| `q3_has_reported_fixed_vulns` | bool | vuln-history proxy from advisories/issues/PR evidence | scorecard_input |
| `q4_all_channels_pinned` | bool | `phase_1_raw_capture.distribution_channels.channels[]` pinning | scorecard_input |
| `q4_artifact_verified` | bool | `phase_1_raw_capture.artifact_verification.per_channel[]` | scorecard_input |
| `q4_has_critical_on_default_path` | bool | Phase 4 findings tagged to default install/runtime path | scorecard_input |
| `q4_has_warning_on_install_path` | bool | Phase 4 findings tagged to install-path warning scope | scorecard_input |
| `c20_has_classic_protection` | bool | inverse of `branch_protection.classic.status == 404` | supporting |
| `c20_has_rulesets` | bool | `phase_1_raw_capture.branch_protection.rulesets.count > 0` | supporting |
| `c20_has_rules_on_default` | bool | `phase_1_raw_capture.branch_protection.rules_on_default.count > 0` | supporting |
| `c20_has_recent_release_30d` | bool | latest release published_at within 30 days of scan | supporting |
| `c20_ships_executable_code` | bool | executable/install-surface signals from Phase 1 | supporting |

**Count:** 18 scorecard_input + 5 supporting = 23 rows.

**Dissent preserved:**

- **Pragmatist R3:** 24-row table without question-scoped prefixes; flagged `has_critical_on_default_path` and `has_warning_on_install_path` as draft-subject-to-rename due to circular derivation from LLM-authored findings. Owner response: accepts the circular-derivation concern; these are valid V1.2 signals *provided* Phase 4 authoring follows the order "classify finding install-path-scope → emit scorecard_cell with ref → validator checks ref resolves." If ordering fails in practice, rename to `q4_*_finding_tagged` in V1.2.x patch.
- **DeepSeek R3:** 26-row table with threshold-encoded names (e.g., `formal_review_rate_below_10`). Owner counter: thresholds belong in `compute.py` logic, not in signal IDs (binding a threshold to an ID makes threshold adjustment a schema bump). Codex's unthresholded `q1_formal_review_rate` (number type) is more stable; consumers compare the number against thresholds separately.
- **DeepSeek R3** additionally: `top_contributor_share_gt_80` as a supporting signal. Owner response: the underlying share is already captured via `q1_is_solo_maintainer` derivation; if post-V1.2 telemetry shows operators citing raw top-contributor-share in overrides, add `c_top_contributor_share` (unthresholded) in V1.2.x patch.

---

## 6. Pre-archive dissent audit

Per SOP §4 mandatory requirement. Each R1+R2+R3 dissent item is traced to a disposition: **Resolved by outcome**, **Accepted as dissent** (preserved in this doc), or **Deferred** (with trigger documented).

### R1 dissent items

| # | Source | Item | Disposition |
|---|---|---|---|
| 1 | Pragmatist FIX-NOW | P1-RENAME silent field drops | Resolved by D1 (§4) |
| 2 | Pragmatist FIX-NOW | P2-LOSSY-CAST distribution_channels_verified | Resolved by D1 (§4) |
| 3 | Pragmatist FIX-NOW | P3-DOUBLE-ASSIGN branch_protection | Resolved by D1 (transformer deleted) |
| 4 | Pragmatist DEFER | D-RENDERER partial changes | Resolved by Item D: empirically no renderer consumer exists for `dangerous_primitives`; scorecard path-change IS forced by D2 |
| 5 | Pragmatist DEFER | D-TELEMETRY override-pattern log | **Deferred to V1.3** — trigger: 3 V1.2 scans shipped. Logged in §8 below. |
| 6 | Pragmatist DEFER | D-SD2 auto_load_tier C3 rebinding | **Deferred** per Q7 scope guard (own review cycle). |
| 7 | Pragmatist DEFER | D-MARKITDOWN-FIXTURE | **Deferred** — trigger: markitdown re-scan under V1.2 schema. |
| 8 | Pragmatist INFO | I2 pr_review counts + dependabot_config dropped | Resolved by D1 (schema accepts harness shape natively) |
| 9 | Codex FIX-NOW | C-1 canonical scorecard storage shape | Resolved by OQ-4 (keyed object by question ID) |
| 10 | Codex FIX-NOW | C-2 define phase_3_advisory explicitly | Resolved by D2 |
| 11 | Codex FIX-NOW | C-3 computed_signal_refs + override_reason | Resolved by Item A + Item C + Item F |
| 12 | Codex FIX-NOW | C-4 migration script | Resolved by Q4 + Item B |
| 13 | Codex DEFER | C-5 renderer expansion for Phase-1 in §01/§02 | **Deferred to V1.3** — trigger: V1.2 round-trip + determinism pass on regenerated fixtures. |
| 14 | Codex DEFER | C-6 11-scan comparator calibration analysis | **Deferred** — trigger: V1.2 schema frozen + override telemetry exists. |
| 15 | DeepSeek FIX-NOW | C-1 preserve per-family dangerous_primitives | Resolved by D1 (nested shape preserved in schema) |
| 16 | DeepSeek FIX-NOW | C-2 override_category enum | Resolved by Item C |
| 17 | DeepSeek FIX-NOW | C-3 type coercion fields preserve granularity | Resolved by D1 |
| 18 | DeepSeek INFO | I-2 ossf_scorecard.http_status useful | Resolved by D1 (harness shape accepted; `http_status` retained when harness emits it). Note: Codex R1 I3 (http_status is fine to drop) — owner sided with DeepSeek: preserve via harness-native. |

### R2 dissent items

| # | Source | Item | Disposition |
|---|---|---|---|
| 19 | R2 Q3 split | DeepSeek B2-scoped naming-prefix preference | **Accepted dissent:** owner chose B1 (harness-canonical without `is_` prefix). DeepSeek's preference for `is_archived`/`is_fork` prefix consistency preserved. V1.2 is pre-stable; if post-V1.2 field-naming friction emerges, revisit in V1.3 as a rename-only schema bump. |
| 20 | R2 OQ-2/OQ-3 split | Pragmatist + DeepSeek sibling-inside-phase_3_computed preference | **Accepted dissent:** owner chose new top-level `phase_3_advisory`. P+DS alternative was structurally simpler (one less phase); owner prioritized authority-separation clarity. Preserved. |
| 21 | R2 OQ-6 split | Codex active + archived Step G preference (R2 only; R3 held (b)) | **Accepted dissent** — see Item B §5 above. Preserved. |
| 22 | R2 OQ-9 split | Pragmatist "LLM gets sidecar" preference | **Logically moot post-D1:** B1 makes sidecar unnecessary (schema accepts rich data natively). Preserved as historical record; not a live contract concern. |
| 23 | Pragmatist R2 new tension | V1.2 scorecard_cell Phase 4 shape not concretely defined in R2 | **Resolved** by Item C (enum) + Item F (signal IDs) + §5 scorecard_cell structure inventory in D2. Concrete enough for implementation. |
| 24 | DeepSeek R2 new disagreement | Renderer dangerous_primitives mandatory V1.2 scope | **Empirically falsified** by P + C independent grep in R3. Not a live concern. |

### R3 dissent items (within narrow scope)

| # | Item | Dissent | Disposition |
|---|---|---|---|
| 25 | Item A | DeepSeek (b) substring check | **Accepted dissent** — §5 Item A above. Preserved. |
| 26 | Item B | Codex (b) active + archived Step G | **Accepted dissent** — §5 Item B above. Preserved. |
| 27 | Item C | DeepSeek `community_norms_differ` 6th value | **Accepted dissent with mapping rule** — §5 Item C above. Telemetry trigger for V1.3 expansion logged. |
| 28 | Item D | DeepSeek (a) nested partials 30-40 LOC | **Empirically moot** — §5 Item D above. Carried as V1.3 guidance. |
| 29 | Item E | Pragmatist + DeepSeek want a compute/renderer helper for bytes | **Accepted dissent** — §5 Item E above. Owner chose (d) Codex minimal. No V1.2 helper. |
| 30 | Item F | Pragmatist 24-row table without prefix + 2 draft-flagged signals | **Accepted dissent with commitment** — §5 Item F above. If ordering assumption breaks, rename to `q4_*_finding_tagged` in V1.2.x. |
| 31 | Item F | DeepSeek threshold-encoded names + extra `top_contributor_share_gt_80` | **Accepted dissent with V1.2.x rule** — §5 Item F above. Thresholds stay in compute.py logic, not in IDs. |

**Total dissent items:** 31 (18 R1 + 6 R2 + 7 R3)
**Resolved cleanly by outcome:** 14 (items 1, 2, 3, 4, 8, 9, 10, 11, 12, 15, 16, 17, 18, 23)
**Deferred with documented trigger:** 5 (items 5, 6, 7, 13, 14)
**Accepted as live preserved dissent:** 9 (items 19, 20, 21, 25, 26, 27, 29, 30, 31)
**Preserved as historical (moot by D1 or empirical finding):** 3 (items 22, 24, 28)
**Silent drops:** 0

**Audit verdict: ✅ PASS** — every dissent has a named disposition. 14 + 5 + 9 + 3 = 31.

---

## 7. V1.2 implementation scope (concrete)

The following are the V1.2 implementation deliverables. Each is within reach of one operator in under a week.

### 7.1 Schema (`docs/scan-schema.json`)

- Bump `$comment` and schema version indicator to V1.2
- Apply D1 field-name + shape deltas (§2 above)
- Add new top-level `phase_3_advisory` per D2
- Delete `phase_3_computed.scorecard_cells`; add `phase_4_structured_llm.scorecard_cells` per D2 with new fields: `rationale`, `edge_case`, `suggested_threshold_adjustment`, `computed_signal_refs`, `override_reason` (enum per §5 Item C)
- Drop `code_patterns.agent_rule_files.total_bytes` per §5 Item E

### 7.2 Harness (`docs/phase_1_harness.py`)

- Add harness gathering for `has_issues_enabled`, `primary_language`, `topics`, `fork_count` (from existing `gh api repos/...` response — these fields are returned but not currently selected)
- No other functional changes; shape deltas absorbed by schema

### 7.3 Compute (`docs/compute.py`)

- Demote `compute_scorecard_cells()` to advisory; its output populates `phase_3_advisory.scorecard_hints`
- Add `SIGNAL_IDS: frozenset[str]` constant exporting the 23 frozen signal IDs per §5 Item F
- Retain 7 byte-for-byte deterministic ops unchanged
- No `compute_agent_rule_bytes()` helper per §5 Item E

### 7.4 Validator (`docs/validate-scanner-report.py`)

- Add `validate_override_rationale(cell, advisory_hint)` per §5 Item A pseudocode
- Gate 6.3 changes from "cell-by-cell match" to "override-explained" — implemented as validator check
- New validator test surface in `tests/test_validator.py`

### 7.5 Renderer (`docs/render-md.py`, `docs/render-html.py`, partials)

- `scorecard.md.j2` + `scorecard.html.j2` — path change `phase_3_computed` → `phase_4_structured_llm`
- `tests/test_render_md.py` + `tests/test_render_html.py` — assertion path update
- Optionally surface new scorecard_cell fields (rationale, edge_case, etc.) — minimal-first; can defer
- **No edits** to `dangerous_primitives` / `agent_rule_files` partials per §5 Item D

### 7.6 Migration

- `migrate-v1.1-to-v1.2.py` — one-time script regenerating 3 active fixtures
- `tests/fixtures/provenance.json` — `schema_version` field update on 3 migrated entries; failed-artifact entries stay V1.1

### 7.7 Operator guide

- `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 update — reflect V1.2 as current pipeline; V1.1 noted as supported for archived forms only
- Clear documentation of `computed_signal_refs` vocabulary and how Phase 4 LLM cites them
- Gate 6.3 update from byte-for-byte to override-explained

### 7.8 Tests

- 319/319 tests passing baseline must hold through V1.2 landing
- New tests:
  - Validator override-rationale gate (~5 tests)
  - Migration script round-trip (~3 tests)
  - Signal ID vocabulary completeness (~2 tests)
  - Scorecard cell path-change render tests (~4 tests)

---

## 8. Deferred ledger (post-V1.2 items + triggers)

| ID | Item | Trigger | Status |
|---|---|---|---|
| V13-1 | Override-pattern telemetry log (CSV of `cell, advisory_color, llm_color, rationale_first_line, override_reason`) | 3 V1.2 scans shipped | **RESOLVED 2026-04-20 by owner directive** — see §8.1 below |
| V13-2 | Renderer Phase-1 richness expansion (surface `dangerous_primitives` per-family, self_merge_count, dependabot_config schedule) | V1.2 round-trip + determinism pass clean | open |
| V13-3 | 11-scan comparator calibration analysis | V1.2 schema frozen + telemetry exists + ≥11 V1.2 scans collected | open (3/11) |
| V13-4 | `community_norms_differ` enum expansion | ≥3 V1.2 overrides with `missing_qualitative_context` + community-norms rationale | open (0 observed; V13-1 split may absorb this) |
| V13-5 | SD2 auto_load_tier C3 rebinding (`domain=='agent'`) | Own review cycle | open |
| V13-6 | markitdown-as-4th-fixture decision | Markitdown re-scanned under V1.2 | open |
| V13-7 | OQ-9 sidecar access reconsideration if harness gathers data not representable in schema | Harness feature add that fails B1 round-trip | open |
| V12x-1 | Add `has_issues_enabled`, `primary_language`, `topics`, `fork_count` to harness gathering | Any-time V1.2.x patch | partial (fields added to harness mid-V1.2) |
| V12x-2 | Rename `q4_has_critical_on_default_path` / `q4_has_warning_on_install_path` to `q4_*_finding_tagged` | If circular-derivation ordering fails in Phase 4 authoring | open |
| V12x-3 | Add `c_top_contributor_share` unthresholded signal | Telemetry shows operators citing raw top-contributor-share in overrides | open |
| V12x-4 | Add more supporting signals (`has_license_file`, `has_readme`, etc.) | Telemetry shows uncategorizable overrides citing missing signals | open |

### 8.1 V13-1 resolution (2026-04-20, owner directive)

**Data:** 3 V1.2 wild scans shipped 2026-04-20 (ghostty entry 16 / Kronos entry 17 / kamal entry 18), producing 4 overrides across 12 scorecard cells (33% override rate). Distribution: Q1 × 2 (de-escalate), Q2 × 1 (escalate), Q4 × 1 (escalate), Q3 × 0. **All 4 overrides cited `missing_qualitative_context`** (100% concentration). Other 4 enum values unexercised.

**Analysis:** Full writeup at `docs/v13-1-override-telemetry-analysis.md`. Each override's Phase 4 rationale mapped to a distinct fix surface — 3 of 4 to `docs/compute.py` (new/widened signal needed), 1 of 4 to `docs/phase_1_harness.py` (dangerous-primitives regex missed `pickle.load`).

**Owner directive:** Expand `override_reason_enum` from 5 to 7 values by adding `signal_vocabulary_gap` (compute.py fix surface) + `harness_coverage_gap` (phase_1_harness.py fix surface). Retain `missing_qualitative_context` for genuinely-judgment cases.

**Migration:** 3 existing overrides relabeled to `signal_vocabulary_gap` (ghostty Q1, kamal Q1, Kronos Q2), 1 to `harness_coverage_gap` (Kronos Q4). Additive change — all existing validation continues to pass.

**Escalation triggers preserved:** If a future scan produces an override fitting none of the 3 labels cleanly, fitting multiple labels with genuine ambiguity, OR if a post-hoc Skeptic review flags the relabeling as inconsistent with DeepSeek's original R3 dissent on `community_norms_differ`, revisit via board review. V13-4 (`community_norms_differ`) remains open with a note that V13-1's split may absorb it.

**Files changed:** `docs/scan-schema.json` (+2 enum values), `docs/compute.py` (+2 frozenset entries), `tests/test_validator_v12_override.py` (+2 positive tests, enum-size test renamed), 4 scan bundles (override_reason relabeled), 3 rendered reports (rerendered from updated bundles), `docs/scanner-catalog.md` (entries 16/17/18 prose updated).

---

## 9. Agent invocation snapshot

| Agent | Model | Invocation | Rounds |
|---|---|---|---|
| Pragmatist | Claude Sonnet 4.6 | `Agent` tool with `subagent_type="general-purpose"`, `model="sonnet"`, `run_in_background=true` | R1, R2, R3 |
| Systems Thinker | Codex GPT-5 | `sudo -u llmuser bash -c "cd /tmp && codex exec --dangerously-bypass-approvals-and-sandbox <prompt>"` | R1, R2, R3 |
| Skeptic | DeepSeek V4 | `OPENAI_API_KEY=$DEEPSEEK_API_KEY OPENAI_BASE_URL=https://api.deepseek.com/v1 qwen -y -p <prompt> --model deepseek-chat` | R1, R2, R3 |

**Token usage (per Codex's self-report, rough):**
- R1: ~104k tokens
- R2: ~102k tokens
- R3: ~125k tokens

**Process notes:**
- No failures. No retries. No 401 auth renewals. No same-model blind-spot collisions.
- Pragmatist used Sonnet 4.6 (not Opus 4.7) per rule: operator authored R1 brief using Opus; same-model blind spot applies.
- All briefs staged at `/tmp/d7-d8-r{1,2,3}-brief.md` with `chmod 644` for `llmuser` Codex readability.
- All R3 "None for R4" reports — no round escalated.

---

## 10. Files in this archive

- `r1-brief.md` — 296 lines, operator-authored, stateless
- `r2-brief.md` — 409 lines, includes R1 outputs verbatim
- `r3-brief.md` — 336 lines, narrow scope (6 items)
- `pragmatist-r1.md` / `pragmatist-r2.md` / `pragmatist-r3.md`
- `codex-r1.md` / `codex-r2.md` / `codex-r3.md`
- `deepseek-r1.md` / `deepseek-r2.md` / `deepseek-r3.md`
- `deepseek-r1-raw.log` / `deepseek-r2-raw.log` / `deepseek-r3-raw.log` (qwen CLI stdout capture)
- `CONSOLIDATION.md` — this file

---

## 11. Next actions

1. **Implement V1.2** per §7 scope. Owner is the implementer (same person authored harness + transformer; schema is the next natural step).
2. **Update `REPO_MAP.md`** — move D-7 and D-8 from active deferred ledger (§2.5) to "recently completed"; link to this CONSOLIDATION.
3. **Update `docs/SCANNER-OPERATOR-GUIDE.md` §8.8** — once V1.2 schema lands, refresh §8.8 to reflect V1.2 as current.
4. **Archive this directory** to `docs/External-Board-Reviews/042026-schema-v12/` and update `docs/External-Board-Reviews/README.md` index.
5. **Log V1.3 trigger watchpoints** in `REPO_MAP.md` §2.5 per §8 above.

**Review outcome:** SIGN OFF. 3/3 agents. 0 silent dissent drops. 7 accepted dissents preserved. V1.2 implementation scope concrete and under-a-week deliverable.
