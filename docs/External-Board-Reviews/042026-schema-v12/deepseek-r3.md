# Schema V1.2 R3 — Skeptic

## Owner directives acknowledged
- D1 (Q3 = D8-B1 harness-canonical, transformer deleted): accepted — harness as canonical producer eliminates lossy bridge.
- D2 (new top-level phase_3_advisory with scorecard_hints): accepted — clean topology separation of advisory from deterministic compute.

## Item A — Q5 rationale-naming floor
**Resolution:** (b) — rationale length-floor + must contain the string of at least one `computed_signal_refs` entry

**Reasoning:** As Skeptic, I hunt what embarrasses each resolution. Option (a) length-floor only is embarrassed by LLM word salad that meets length requirement but doesn't engage with signals. Option (b) string-substring requirement is embarrassed by mechanical signal-name dropping without meaningful explanation. However, (b) is strictly better: it forces LLM to at least mention the signal by name, creating a minimal tether between rationale and advisory signals. The scan shape that defeats (b) is LLM writing "signal formal_review_rate_below_10" without explanation, but that's still better than no mention at all. Validator should also check rationale length (≥100 chars) to prevent one-word mentions.

**Validator pseudocode:**
```python
def validate_override_rationale(cell, advisory_signals):
    if cell["color"] != advisory_signals[cell["question"]]["color"]:
        rationale = cell.get("rationale", "")
        refs = cell.get("computed_signal_refs", [])
        if len(rationale) < 100:
            raise ValidationError("Rationale too short for override")
        if not refs:
            raise ValidationError("Override requires computed_signal_refs")
        # Check at least one ref appears in rationale
        ref_in_rationale = any(ref in rationale for ref in refs)
        if not ref_in_rationale:
            raise ValidationError("Rationale must mention at least one referenced signal")
```

## Item B — OQ-6 migration script scope
**Resolution:** (d) — Active fixtures only + explicit rule: "archived artifacts stay V1.1 and any test referencing them pins to V1.1 schema via explicit annotation."

**Reasoning:** The scan shape that embarrasses (a) active fixtures only is when a test references an archived Step G artifact expecting V1.2 schema but gets V1.1. The scan shape that embarrasses (c) all provenance.json entries is when we migrate failed artifacts (`step-g-failed-artifact`) that shouldn't be canonical. Option (d) is the honest middle: migrate only what's live, explicitly annotate tests that use archived artifacts with `# schema: V1.1` comment. This preserves test determinism without canonizing failed artifacts. 

**Files migrated:** 3 files (zustand-form.json, caveman-form.json, archon-subset-form.json). The zustand-step-g-form.json is `step-g-live-pipeline` and will become `pipeline-produced` on acceptance, at which point it should be migrated.

## Item C — override_reason enum values
**Frozen enum:**
1. `threshold_too_strict` — Advisory threshold is too strict for this repo's context
2. `threshold_too_lenient` — Advisory threshold is too lenient given repo risk profile  
3. `missing_qualitative_context` — Advisory threshold is right but qualitative facts override (e.g., CONTRIBUTING.md shows responsiveness)
4. `rubric_literal_vs_intent` — Advisory threshold misreads V2.4 prompt rubric literal vs intent
5. `community_norms_differ` — Repo follows different community norms than rubric assumes
6. `other` — Escape hatch for uncategorizable overrides

**Reasoning per departure from Codex R1 / DeepSeek R1 proposals:** Codex R1 had 5 values, missing `community_norms_differ`. DeepSeek R1 had 3 values (`threshold`, `qualitative_context`, `rubric_interpretation`), too coarse. The scan shape that embarrasses incomplete enum is a repo where LLM overrides for "community norms differ from rubric" (e.g., Python packaging norms vs Node.js). Without this category, such overrides become uncategorizable or forced into `other`. Adding `community_norms_differ` captures this real-world override pattern observed in calibration scans.

## Item D — renderer dangerous_primitives coupling
**Resolution:** (a) — Nested partials — update the Jinja2 partial(s) that consume `dangerous_primitives` to iterate over per-family keys.

**Reasoning:** The scan shape that embarrasses Jinja-macro flatten (c) is when downstream consumer wants per-family aggregation statistics ("3 exec hits vs 1 network hit tells different risk story"). The macro flatten loses family context at render time. Compute-layer flatten (b) pushes complexity to compute.py for renderer convenience. Nested partials (a) preserves the rich structure throughout the pipeline. The renderer change is mandatory for V1.2 to function anyway (per Q6-narrow). 

**Concrete change location:** Create new partial `templates/partials/dangerous_primitives.md.j2` that iterates over per-family keys. Update renderer to use this partial. Approx 30-40 lines touched (new partial + renderer integration).

## Item E — agent_rule_files total_bytes heuristic
**Resolution:** (b) — Require raw `line_count` per entry; compute bytes elsewhere.

**Reasoning:** The scan shape that embarrasses the 50-bytes/line heuristic is a repo with minified JS (200+ bytes/line) or dense config (20 bytes/line). The heuristic becomes wildly inaccurate. Canonizing it (a) locks in systematic bias. True byte count from tarball (c) adds harness complexity for marginal gain. Option (b) is cleanest: harness emits `line_count`, renderer or compute.py derives `total_bytes = sum(line_count × 50)` if needed for display. Schema doesn't store `total_bytes`, avoiding canonization of heuristic.

**Concrete change:** Remove `total_bytes` from schema. Harness continues to emit `line_count` per agent_rule_file. Renderer computes display bytes if needed (e.g., for summary table). Transformer's heuristic line deleted.

## Item F — signal ID vocabulary
| ID | Type | Derived from | Kind |
|---|---|---|---|
| `formal_review_rate_below_10` | number | `pr_review.formal_review_rate` < 10% | scorecard_input |
| `formal_review_rate_below_30` | number | `pr_review.formal_review_rate` < 30% | scorecard_input |
| `any_review_rate_below_30` | number | `pr_review.any_review_rate` < 30% | scorecard_input |
| `any_review_rate_below_60` | number | `pr_review.any_review_rate` < 60% | scorecard_input |
| `has_branch_protection` | bool | `branch_protection.classic` present | scorecard_input |
| `has_codeowners` | bool | `codeowners` file present | scorecard_input |
| `is_solo_maintainer` | bool | top contributor >80% share | scorecard_input |
| `open_security_issue_count_gt_3` | number | `security_issues.open_count` > 3 | scorecard_input |
| `oldest_cve_pr_age_gt_14` | number | oldest open CVE PR > 14 days | scorecard_input |
| `closed_fix_lag_days_gt_3` | number | merged security PR age > 3 days | scorecard_input |
| `has_security_policy` | bool | SECURITY.md present | scorecard_input |
| `has_contributing_guide` | bool | CONTRIBUTING.md present | scorecard_input |
| `published_advisory_count_gt_0` | number | published advisories > 0 | scorecard_input |
| `has_silent_fixes` | bool | silent fixes detected | scorecard_input |
| `all_channels_pinned` | bool | all distribution channels pinned | scorecard_input |
| `artifact_verified` | bool | artifacts cryptographically verified | scorecard_input |
| `has_warning_on_install_path` | bool | warning-level finding on install path | scorecard_input |
| `has_critical_on_default_path` | bool | critical finding on default install path | scorecard_input |
| `governance_floor_override` | bool | formal<10% AND no branch protection AND no codeowners | scorecard_input |
| `has_classic_protection` | bool | classic branch protection status 200 | supporting |
| `has_rulesets` | bool | rulesets present | supporting |
| `has_rules_on_default` | bool | rules on default branch | supporting |
| `ships_executable_code` | bool | tarball contains executable files | supporting |
| `has_recent_release_30d` | bool | latest release within 30 days | supporting |
| `has_reported_fixed_vulns` | bool | repo has reported+fixed vulnerabilities | supporting |
| `top_contributor_share_gt_80` | number | top contributor >80% commits | supporting |

**Draft-subject-to-rename:** `governance_floor_override` (maybe `q1_governance_floor_triggered`), `has_reported_fixed_vulns` (maybe `has_fixed_vulnerability_history`).

**Reasoning on contentious choices:** The scan shape that embarrasses incomplete vocabulary is a repo where LLM needs to cite "has_license_file" or "has_readme" — signals not in compute.py today. We accept this limitation for V1.2; new signals can be added in V1.2.x patches. `governance_floor_override` is a composite signal (3 conditions) that deserves its own ID because it's a distinct override trigger in SF1 calibration. `has_reported_fixed_vulns` is from SF1 Q3 Gate C but not in current compute.py; include it as supporting signal for completeness.

## Unresolved items for R4
None — all 6 items have concrete resolutions ready for V1.2 implementation.

## Blind spots
1. **Renderer template complexity:** I haven't examined the actual Jinja2 partials for `dangerous_primitives`. If they're deeply coupled to flat `hits[]` structure, the nested partials change (Item D) could be more than 30-40 lines.
2. **LLM prompt engineering burden:** The `computed_signal_refs` + `override_reason` + rationale naming requirements (Item A) create significant prompt complexity. If LLM consistently ignores these structures, our "structural enforcement" is theater.
3. **Migration script edge cases:** The "active fixtures only" rule (Item B) assumes we can cleanly identify which tests reference archived artifacts. If tests import fixtures dynamically, annotation becomes fragile.
4. **Enum category misuse:** The `override_reason` enum (Item C) assumes LLM will choose categories accurately. If LLM defaults to `other` or mis-categorizes, telemetry becomes noisy.
5. **Signal ID vocabulary growth:** The frozen vocabulary (Item F) will inevitably need expansion. The process for adding new signals post-V1.2 is undefined.