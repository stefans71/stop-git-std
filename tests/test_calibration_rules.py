#!/usr/bin/env python3
"""
Tests for compute.evaluate_q1/q2/q3/q4 + compute_scorecard_cells_v2 —
the calibration v2 rule table (Phase 3 of docs/back-to-basics-plan.md).

Spec: docs/calibration-design-v2.md §5 (rules) + §10 (CellEvaluation contract).

Coverage:
  - evaluate_q1: RULE-1 (governance-floor softener) / RULE-2 (review-rate) /
                 RULE-3 (narrow tie-breaker) / FALLBACK
  - evaluate_q2: NO RULE CHANGES (per directive #16 — explicit deferral);
                 FALLBACK reproduces legacy logic
  - evaluate_q3: RULE-4 (sample-floor — HIGHEST-VALUE) / RULE-5 (ruleset
                 disclosure) / FALLBACK
  - evaluate_q4: RULE-6 (auto-fire: deserialization/cmd_injection/exec) /
                 RULE-7/8/9 INERT (promotion-gated) / FALLBACK
  - compute_scorecard_cells_v2: orchestrator integration + rule_id REQUIRED
                                on every cell + shape_classification embedded
  - First-match-wins precedence

Run: python3 -m pytest tests/test_calibration_rules.py -v
"""

import sys
import pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))
from compute import (
    ShapeClassification, CellEvaluation,
    evaluate_q1, evaluate_q2, evaluate_q3, evaluate_q4,
    compute_scorecard_cells_v2,
    classify_shape,
)


def _shape(category="other", *, is_solo=False, is_priv=False, is_re=False):
    return ShapeClassification(
        category=category,
        is_reverse_engineered=is_re,
        is_privileged_tool=is_priv,
        is_solo_maintained=is_solo,
        confidence="medium",
        matched_rule="test fixture",
    )


# ===========================================================================
# evaluate_q1 — RULE-1 / RULE-2 / RULE-3 / FALLBACK
# ===========================================================================

class TestEvaluateQ1Rule1GovernanceFloor:
    """RULE-1: CODEOWNERS + ruleset + rules-on-default → amber, not red."""

    def test_all_three_governance_gates_fires_amber(self):
        """ghostty / kamal pattern: governance gates present even when
        review rate is low."""
        signals = {
            "has_codeowners": True,
            "has_ruleset_protection": True,
            "rules_on_default_count": 4,
            "formal_review_rate": 5,
            "any_review_rate": 25,
        }
        result = evaluate_q1(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "RULE-1"
        assert result.short_answer_template_key == "q1.amber.governance_present"

    def test_solo_concentration_qualifier_picked(self):
        signals = {
            "has_codeowners": True,
            "has_ruleset_protection": True,
            "rules_on_default_count": 1,
            "formal_review_rate": 5,
            "any_review_rate": 0,
        }
        result = evaluate_q1(signals, _shape(is_solo=True))
        assert result.color == "amber"
        assert result.rule_id == "RULE-1"
        assert "concentration risk" in result.template_vars["concentration_qualifier"]

    def test_missing_codeowners_does_NOT_fire_rule_1(self):
        signals = {
            "has_codeowners": False,
            "has_ruleset_protection": True,
            "rules_on_default_count": 4,
            "formal_review_rate": 5,
            "any_review_rate": 0,
        }
        result = evaluate_q1(signals, _shape())
        assert result.rule_id != "RULE-1"

    def test_missing_ruleset_does_NOT_fire_rule_1(self):
        signals = {
            "has_codeowners": True,
            "has_ruleset_protection": False,
            "rules_on_default_count": 4,
            "formal_review_rate": 5,
            "any_review_rate": 0,
        }
        result = evaluate_q1(signals, _shape())
        assert result.rule_id != "RULE-1"

    def test_zero_rules_on_default_does_NOT_fire_rule_1(self):
        """Ghost ruleset (count >= 1 but rules_on_default == 0) must not trip."""
        signals = {
            "has_codeowners": True,
            "has_ruleset_protection": True,
            "rules_on_default_count": 0,
            "formal_review_rate": 5,
            "any_review_rate": 0,
        }
        result = evaluate_q1(signals, _shape())
        assert result.rule_id != "RULE-1"


class TestEvaluateQ1Rule2ReviewRate:
    """RULE-2: formal_review >= 30 OR any_review >= 60 → amber."""

    def test_formal_30_fires_amber(self):
        """Boundary: 30% formal exactly."""
        signals = {
            "has_codeowners": False,
            "has_ruleset_protection": False,
            "rules_on_default_count": 0,
            "formal_review_rate": 30,
            "any_review_rate": 0,
        }
        result = evaluate_q1(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "RULE-2"

    def test_any_60_fires_amber(self):
        """Boundary: 60% any-review exactly."""
        signals = {
            "has_codeowners": False,
            "has_ruleset_protection": False,
            "formal_review_rate": 0,
            "any_review_rate": 60,
        }
        result = evaluate_q1(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "RULE-2"

    def test_wled_pattern_41_formal_fires_amber(self):
        """WLED-class: 41% formal review on solo-maintained firmware."""
        signals = {
            "has_codeowners": False,
            "has_ruleset_protection": False,
            "formal_review_rate": 41,
            "any_review_rate": 41,
            "pr_sample_size": 30,
        }
        result = evaluate_q1(signals, _shape(is_solo=True, is_priv=True))
        assert result.color == "amber"
        assert result.rule_id == "RULE-2"

    def test_below_thresholds_does_NOT_fire_rule_2(self):
        signals = {
            "formal_review_rate": 15,
            "any_review_rate": 50,
        }
        result = evaluate_q1(signals, _shape())
        assert result.rule_id != "RULE-2"


class TestEvaluateQ1Rule3SoloTieBreaker:
    """RULE-3: solo + NOT privileged + (codeql OR releases >= 20) → amber."""

    def test_solo_codeql_non_privileged_fires(self):
        """kamal-class: solo + Ruby-CLI + CodeQL on."""
        signals = {
            "formal_review_rate": 5,
            "any_review_rate": 5,
            "has_codeql": True,
            "releases_count": 0,
            "has_codeowners": False,
            "has_ruleset_protection": False,
            "rules_on_default_count": 0,
        }
        result = evaluate_q1(signals, _shape(is_solo=True, is_priv=False))
        assert result.color == "amber"
        assert result.rule_id == "RULE-3"

    def test_solo_many_releases_non_privileged_fires(self):
        """20+ releases on a non-privileged solo project."""
        signals = {
            "formal_review_rate": 5,
            "any_review_rate": 5,
            "has_codeql": False,
            "releases_count": 25,
            "has_codeowners": False,
            "has_ruleset_protection": False,
        }
        result = evaluate_q1(signals, _shape(is_solo=True, is_priv=False))
        assert result.color == "amber"
        assert result.rule_id == "RULE-3"

    def test_solo_privileged_does_NOT_fire(self):
        """Solo + PRIVILEGED tool — RULE-3 must not fire (concentration risk
        on privileged tool isn't softened by activity signals)."""
        signals = {
            "formal_review_rate": 5,
            "any_review_rate": 5,
            "has_codeql": True,
            "releases_count": 30,
        }
        result = evaluate_q1(signals, _shape(is_solo=True, is_priv=True))
        assert result.rule_id != "RULE-3"

    def test_non_solo_does_NOT_fire(self):
        """Not solo — RULE-3 only applies to solo OSS shapes."""
        signals = {
            "formal_review_rate": 5,
            "any_review_rate": 5,
            "has_codeql": True,
        }
        result = evaluate_q1(signals, _shape(is_solo=False, is_priv=False))
        assert result.rule_id != "RULE-3"

    def test_solo_no_positive_signal_does_NOT_fire(self):
        """Solo + non-priv but neither codeql nor 20+ releases → fall through."""
        signals = {
            "formal_review_rate": 5,
            "any_review_rate": 5,
            "has_codeql": False,
            "releases_count": 5,
        }
        result = evaluate_q1(signals, _shape(is_solo=True, is_priv=False))
        assert result.rule_id != "RULE-3"


class TestEvaluateQ1Fallback:
    """FALLBACK: legacy compute_scorecard_cells Q1 logic preserved."""

    def test_governance_floor_red(self):
        signals = {
            "formal_review_rate": 5,
            "any_review_rate": 25,
            "has_branch_protection": False,
            "has_ruleset_protection": False,
            "has_codeowners": False,
        }
        result = evaluate_q1(signals, _shape())
        assert result.color == "red"
        assert result.rule_id == "FALLBACK"

    def test_solo_low_review_red(self):
        signals = {
            "formal_review_rate": 12,
            "any_review_rate": 35,
            "has_branch_protection": True,
        }
        result = evaluate_q1(signals, _shape(is_solo=True))
        assert result.color == "red"
        assert result.rule_id == "FALLBACK"

    def test_amber_via_legacy_50pct_any_review(self):
        signals = {
            "formal_review_rate": 15,
            "any_review_rate": 55,
            "has_branch_protection": True,
        }
        result = evaluate_q1(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "FALLBACK"


# ===========================================================================
# evaluate_q2 — NO RULE CHANGES (explicit deferral per directive #16)
# ===========================================================================

class TestEvaluateQ2Deferred:
    """Q2 has no rules; FALLBACK reproduces legacy compute_scorecard_cells Q2."""

    def test_no_open_recent_fix_green(self):
        signals = {
            "open_security_issue_count": 0,
            "oldest_cve_pr_age_days": 0,
            "oldest_open_security_item_age_days": 0,
            "closed_fix_lag_days": None,
        }
        result = evaluate_q2(signals, _shape())
        assert result.color == "green"
        assert result.rule_id == "FALLBACK"

    def test_few_open_recent_amber(self):
        signals = {
            "open_security_issue_count": 2,
            "oldest_cve_pr_age_days": 10,
        }
        result = evaluate_q2(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "FALLBACK"

    def test_many_open_or_old_red(self):
        signals = {
            "open_security_issue_count": 5,
            "oldest_cve_pr_age_days": 60,
        }
        result = evaluate_q2(signals, _shape())
        assert result.color == "red"
        assert result.rule_id == "FALLBACK"

    def test_kronos_pattern_oldest_open_security_item_escalates(self):
        """Kronos: 95-day-old open issue → red even with 0 PR-cve_age."""
        signals = {
            "open_security_issue_count": 1,
            "oldest_cve_pr_age_days": 0,
            "oldest_open_security_item_age_days": 95,
        }
        result = evaluate_q2(signals, _shape())
        assert result.color == "red"

    def test_closed_fix_lag_drops_green_to_amber(self):
        signals = {
            "open_security_issue_count": 0,
            "oldest_cve_pr_age_days": 0,
            "closed_fix_lag_days": 5,
        }
        result = evaluate_q2(signals, _shape())
        assert result.color == "amber"

    def test_q2_never_emits_a_RULE_id(self):
        """Per directive #16, no Q2 rule fires by design."""
        for sigs in [
            {"open_security_issue_count": 0, "oldest_cve_pr_age_days": 0},
            {"open_security_issue_count": 100, "oldest_cve_pr_age_days": 1000},
            {"open_security_issue_count": 0, "closed_fix_lag_days": 999},
        ]:
            result = evaluate_q2(sigs, _shape())
            assert result.rule_id == "FALLBACK"


# ===========================================================================
# evaluate_q3 — RULE-4 / RULE-5 / FALLBACK
# ===========================================================================

class TestEvaluateQ3Rule4SampleFloor:
    """RULE-4 (HIGHEST-VALUE): repo_age < 180 AND total_merged < 5 → amber."""

    def test_skills_class_young_repo_fires(self):
        """skills-shape: 90 days old, 1 lifetime merged PR."""
        signals = {
            "repo_age_days": 90,
            "total_merged_lifetime": 1,
            "has_security_policy": False,
            "published_advisory_count": 0,
        }
        result = evaluate_q3(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "RULE-4"
        assert result.template_vars["repo_age_days"] == 90
        assert result.template_vars["total_merged_lifetime"] == 1

    def test_old_repo_does_NOT_fire(self):
        """360-day-old repo: above sample-floor threshold."""
        signals = {
            "repo_age_days": 360,
            "total_merged_lifetime": 1,
            "has_security_policy": False,
            "published_advisory_count": 0,
        }
        result = evaluate_q3(signals, _shape())
        assert result.rule_id != "RULE-4"

    def test_many_merged_prs_does_NOT_fire(self):
        """Many lifetime PRs: sample-floor doesn't apply."""
        signals = {
            "repo_age_days": 60,
            "total_merged_lifetime": 100,
            "has_security_policy": False,
            "published_advisory_count": 0,
        }
        result = evaluate_q3(signals, _shape())
        assert result.rule_id != "RULE-4"

    def test_age_zero_does_NOT_fire(self):
        """Missing/zero repo_age signal: don't fire (avoid spurious matches)."""
        signals = {
            "repo_age_days": 0,
            "total_merged_lifetime": 0,
        }
        result = evaluate_q3(signals, _shape())
        assert result.rule_id != "RULE-4"


class TestEvaluateQ3Rule5RulesetDisclosure:
    """RULE-5 (HYGIENE): ruleset + published advisories → amber."""

    def test_fires_when_both_present(self):
        signals = {
            "has_ruleset_protection": True,
            "published_advisory_count": 3,
            "has_security_policy": False,
            "has_silent_fixes": False,
            "repo_age_days": 1000,
            "total_merged_lifetime": 100,
        }
        result = evaluate_q3(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "RULE-5"

    def test_no_advisories_does_NOT_fire(self):
        signals = {
            "has_ruleset_protection": True,
            "published_advisory_count": 0,
            "repo_age_days": 1000,
            "total_merged_lifetime": 100,
        }
        result = evaluate_q3(signals, _shape())
        assert result.rule_id != "RULE-5"


class TestEvaluateQ3Fallback:
    """FALLBACK: legacy Q3 logic."""

    def test_full_disclosure_green(self):
        signals = {
            "has_security_policy": True,
            "published_advisory_count": 2,
            "has_silent_fixes": False,
            "repo_age_days": 1000,
            "total_merged_lifetime": 100,
        }
        result = evaluate_q3(signals, _shape())
        assert result.color == "green"
        assert result.rule_id == "FALLBACK"

    def test_partial_disclosure_amber(self):
        signals = {
            "has_security_policy": False,
            "has_contributing_guide": True,
            "published_advisory_count": 0,
            "has_silent_fixes": False,
            "repo_age_days": 1000,
            "total_merged_lifetime": 100,
        }
        result = evaluate_q3(signals, _shape())
        assert result.color == "amber"

    def test_no_disclosure_red(self):
        signals = {
            "has_security_policy": False,
            "has_contributing_guide": False,
            "published_advisory_count": 0,
            "repo_age_days": 1000,
            "total_merged_lifetime": 100,
        }
        result = evaluate_q3(signals, _shape())
        assert result.color == "red"
        assert result.rule_id == "FALLBACK"


# ===========================================================================
# evaluate_q4 — RULE-6 (auto-fire) + INERT RULE-7/8/9 + FALLBACK
# ===========================================================================

class TestEvaluateQ4Rule6AutoFire:
    """RULE-6: 3 sub-conditions, any of which fires red on Q4."""

    def test_deserialization_3_plus_with_user_files_fires(self):
        """V13-3 C5 baseline: deser >= 3 + tool_loads_user_files."""
        signals = {
            "deserialization_hit_count": 5,
            "tool_loads_user_files": True,
            "deserialization_top_file": "BasicBoard.java",
            "all_channels_pinned": True,
            "artifact_verified": True,
            "has_warning_on_install_path": False,
        }
        result = evaluate_q4(signals, _shape())
        assert result.color == "red"
        assert result.rule_id == "RULE-6"
        assert result.auto_fire is True
        assert result.template_vars["primary_pattern"] == "unsafe deserialization"

    def test_cmd_injection_with_user_files_fires(self):
        """RULE-6 NEW sub-condition: cmd_injection >= 1 + tool_loads_user_files."""
        signals = {
            "cmd_injection_hit_count": 1,
            "tool_loads_user_files": True,
            "cmd_injection_top_file": "main.go",
        }
        result = evaluate_q4(signals, _shape())
        assert result.color == "red"
        assert result.rule_id == "RULE-6"
        assert result.template_vars["primary_pattern"] == "command injection"

    def test_exec_with_unverified_install_path_fires(self):
        """RULE-6 NEW sub-condition: exec >= 1 + has_unverified_install_path."""
        signals = {
            "exec_hit_count": 2,
            "has_unverified_install_path": True,
            "exec_top_file": "install.sh",
        }
        result = evaluate_q4(signals, _shape())
        assert result.color == "red"
        assert result.rule_id == "RULE-6"
        assert result.template_vars["primary_pattern"] == "exec on unverified install path"

    def test_deserialization_below_threshold_does_NOT_fire(self):
        """2 hits is below default threshold of 3 — no fire."""
        signals = {
            "deserialization_hit_count": 2,
            "tool_loads_user_files": True,
        }
        result = evaluate_q4(signals, _shape())
        assert result.rule_id != "RULE-6"

    def test_deserialization_without_user_files_does_NOT_fire(self):
        """Internal deserialization only (no file-loading) — no fire (avoids
        false positives on internal RPC libraries)."""
        signals = {
            "deserialization_hit_count": 50,
            "tool_loads_user_files": False,
        }
        result = evaluate_q4(signals, _shape())
        assert result.rule_id != "RULE-6"

    def test_first_match_wins_short_circuits_after_deserialization(self):
        """When multiple sub-conditions match, deserialization fires FIRST."""
        signals = {
            "deserialization_hit_count": 5,
            "tool_loads_user_files": True,
            "cmd_injection_hit_count": 5,  # would also fire
            "exec_hit_count": 5,
            "has_unverified_install_path": True,
        }
        result = evaluate_q4(signals, _shape())
        assert result.template_vars["primary_pattern"] == "unsafe deserialization"


class TestEvaluateQ4LegacyKwarg:
    """Legacy has_critical_on_default_path kwarg path (Phase 4 LLM override
    or legacy explicit override)."""

    def test_legacy_critical_kwarg_fires_red(self):
        signals = {
            "has_critical_on_default_path": True,
        }
        result = evaluate_q4(signals, _shape())
        assert result.color == "red"
        assert result.auto_fire is True
        # rule_id is FALLBACK because RULE-6 didn't fire — this is the
        # explicit-kwarg path, distinct from rule-driven auto-fire.
        assert result.rule_id == "FALLBACK"


class TestEvaluateQ4Fallback:
    """FALLBACK: legacy Q4 logic."""

    def test_all_pinned_verified_no_warning_green(self):
        signals = {
            "all_channels_pinned": True,
            "artifact_verified": True,
            "has_warning_on_install_path": False,
        }
        result = evaluate_q4(signals, _shape())
        assert result.color == "green"
        assert result.rule_id == "FALLBACK"

    def test_install_warning_drops_to_amber(self):
        signals = {
            "all_channels_pinned": True,
            "artifact_verified": True,
            "has_warning_on_install_path": True,
        }
        result = evaluate_q4(signals, _shape())
        assert result.color == "amber"
        assert result.rule_id == "FALLBACK"

    def test_unpinned_drops_to_amber(self):
        signals = {
            "all_channels_pinned": False,
            "artifact_verified": True,
            "has_warning_on_install_path": False,
        }
        result = evaluate_q4(signals, _shape())
        assert result.color == "amber"


class TestEvaluateQ4Rule789Inert:
    """RULE-7/8/9 are intentionally INERT (promotion-gated). Verify they
    don't fire on n=1 patterns until both evidence + harness signals land."""

    def test_firmware_no_auth_does_NOT_fire_today(self):
        """RULE-7 candidate: WLED-shape firmware. INERT until promotion."""
        signals = {
            # No matching signal even theoretically — RULE-7 needs harness work
            # (V12x-11 no_auth_default + cors_wildcard signals).
            "all_channels_pinned": True,
            "artifact_verified": True,
            "has_warning_on_install_path": False,
        }
        result = evaluate_q4(signals, _shape("embedded-firmware"))
        # Without the harness signal, falls through to FALLBACK green.
        assert result.color == "green"
        assert result.rule_id == "FALLBACK"

    def test_reverse_engineered_library_does_NOT_fire_today(self):
        """RULE-9 candidate: Baileys-shape library. INERT until promotion."""
        signals = {
            "all_channels_pinned": True,
            "artifact_verified": True,
            "has_warning_on_install_path": False,
        }
        result = evaluate_q4(signals, _shape("library-package", is_re=True))
        assert result.color == "green"
        assert result.rule_id == "FALLBACK"


# ===========================================================================
# compute_scorecard_cells_v2 — orchestrator integration
# ===========================================================================

class TestComputeScorecardCellsV2Orchestrator:
    """Integration: classify_shape + 4 evaluators + cell-shape contract."""

    def _form(self, **p1_overrides):
        p1 = {
            "repo_metadata": {"primary_language": None, "topics": []},
            "code_patterns": {"agent_rule_files": [], "executable_files": [], "dangerous_primitives": {}},
            "dependencies": {"manifest_files": []},
            "install_script_analysis": {"scripts": []},
            "releases": {"count": 0, "entries": []},
            "contributors": {"top_contributors": [], "total_contributor_count": 0},
        }
        p1.update(p1_overrides)
        return {"phase_1_raw_capture": p1}

    def test_returns_v12_cell_shape(self):
        result = compute_scorecard_cells_v2(self._form(), signals={})
        # V1.2 advisory shape: 4 cells, each with color/short_answer/signals/rule_id
        for cell_key in [
            "does_anyone_check_the_code",
            "do_they_fix_problems_quickly",
            "do_they_tell_you_about_problems",
            "is_it_safe_out_of_the_box",
        ]:
            assert cell_key in result
            cell = result[cell_key]
            assert "color" in cell
            assert "short_answer" in cell
            assert "rule_id" in cell, f"{cell_key}: missing rule_id (directive #14)"
            assert "signals" in cell

    def test_every_cell_has_rule_id_present(self):
        """Directive #14: rule_id REQUIRED on every cell evaluation."""
        result = compute_scorecard_cells_v2(self._form(), signals={})
        valid_rule_ids = {f"RULE-{i}" for i in range(1, 11)} | {"FALLBACK"}
        for cell_key in [
            "does_anyone_check_the_code",
            "do_they_fix_problems_quickly",
            "do_they_tell_you_about_problems",
            "is_it_safe_out_of_the_box",
        ]:
            rid = result[cell_key]["rule_id"]
            assert rid in valid_rule_ids, f"{cell_key} rule_id={rid} not in valid set"

    def test_shape_classification_embedded(self):
        """compute_scorecard_cells_v2 attaches shape_classification dict at top
        level so renderers + downstream consumers can inspect it."""
        result = compute_scorecard_cells_v2(self._form(), signals={})
        assert "shape_classification" in result
        sc = result["shape_classification"]
        assert "category" in sc
        assert "is_reverse_engineered" in sc
        assert "is_privileged_tool" in sc
        assert "is_solo_maintained" in sc
        assert "confidence" in sc
        assert "matched_rule" in sc

    def test_color_short_answer_alignment(self):
        """short_answer must align with color: red→No, amber→Partly, green→Yes."""
        sigs = {
            "has_codeowners": True,
            "has_ruleset_protection": True,
            "rules_on_default_count": 4,
            "formal_review_rate": 5,
            "any_review_rate": 25,
        }
        form = self._form(repo_metadata={"primary_language": "Ruby", "topics": []})
        result = compute_scorecard_cells_v2(form, signals=sigs)
        cell = result["does_anyone_check_the_code"]
        if cell["color"] == "amber":
            assert cell["short_answer"] == "Partly"

    def test_rule_1_fires_when_governance_present(self):
        sigs = {
            "has_codeowners": True,
            "has_ruleset_protection": True,
            "rules_on_default_count": 4,
            "formal_review_rate": 5,
            "any_review_rate": 25,
        }
        result = compute_scorecard_cells_v2(self._form(), signals=sigs)
        assert result["does_anyone_check_the_code"]["rule_id"] == "RULE-1"

    def test_rule_4_fires_for_skills_pattern(self):
        sigs = {
            "repo_age_days": 90,
            "total_merged_lifetime": 1,
            "has_security_policy": False,
            "published_advisory_count": 0,
        }
        result = compute_scorecard_cells_v2(self._form(), signals=sigs)
        assert result["do_they_tell_you_about_problems"]["rule_id"] == "RULE-4"
        assert result["do_they_tell_you_about_problems"]["color"] == "amber"

    def test_rule_6_fires_for_freerouting_pattern(self):
        """freerouting-class: deserialization + tool_loads_user_files."""
        sigs = {
            "deserialization_hit_count": 30,
            "tool_loads_user_files": True,
            "deserialization_top_file": "BasicBoard.java",
        }
        result = compute_scorecard_cells_v2(self._form(), signals=sigs)
        cell = result["is_it_safe_out_of_the_box"]
        assert cell["color"] == "red"
        assert cell["rule_id"] == "RULE-6"
        assert cell["auto_fire"] is True

    def test_template_vars_populated_when_rule_fires(self):
        sigs = {
            "has_codeowners": True,
            "has_ruleset_protection": True,
            "rules_on_default_count": 4,
            "formal_review_rate": 5,
        }
        result = compute_scorecard_cells_v2(self._form(), signals=sigs)
        cell = result["does_anyone_check_the_code"]
        assert "template_vars" in cell
        assert isinstance(cell["template_vars"], dict)
        # RULE-1 specific
        assert "concentration_qualifier" in cell["template_vars"]


# ===========================================================================
# First-match-wins precedence — integrated test
# ===========================================================================

class TestFirstMatchWinsPrecedence:
    """Per design §2 + directive #6: first matching rule short-circuits."""

    def test_rule_1_beats_rule_2(self):
        """RULE-1 + RULE-2 conditions both true → RULE-1 fires (priority order)."""
        signals = {
            # RULE-1 trigger
            "has_codeowners": True,
            "has_ruleset_protection": True,
            "rules_on_default_count": 4,
            # RULE-2 trigger (also satisfied)
            "formal_review_rate": 50,
            "any_review_rate": 80,
        }
        result = evaluate_q1(signals, _shape())
        assert result.rule_id == "RULE-1"

    def test_rule_4_beats_rule_5(self):
        """RULE-4 + RULE-5 conditions both true → RULE-4 fires."""
        signals = {
            # RULE-4 trigger
            "repo_age_days": 90,
            "total_merged_lifetime": 1,
            # RULE-5 trigger (also satisfied)
            "has_ruleset_protection": True,
            "published_advisory_count": 5,
        }
        result = evaluate_q3(signals, _shape())
        assert result.rule_id == "RULE-4"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
