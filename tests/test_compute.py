#!/usr/bin/env python3
"""
Tests for compute.py — the 8 automatable Phase 3 operations.
Each test validates deterministic behavior: same input → same output.

Run: python3 -m pytest tests/test_compute.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))
from compute import *


# ===========================================================================
# C20 Severity
# ===========================================================================

class TestC20Severity:

    def test_all_negative_recent_release_executable_is_critical(self):
        r = compute_c20_severity(404, [], [], False, "2026-04-15", True, "2026-04-17")
        assert r["result"] == "Critical"

    def test_all_negative_no_recent_release_is_warning(self):
        r = compute_c20_severity(404, [], [], False, "2026-02-01", True, "2026-04-17")
        assert r["result"] == "Warning"

    def test_all_negative_no_releases_is_warning(self):
        r = compute_c20_severity(404, [], [], False, None, True, "2026-04-17")
        assert r["result"] == "Warning"

    def test_has_branch_protection_is_none(self):
        r = compute_c20_severity(200, [], [], False, "2026-04-15", True, "2026-04-17")
        assert r["result"] is None

    def test_has_codeowners_is_none(self):
        r = compute_c20_severity(404, [], [], True, "2026-04-15", True, "2026-04-17")
        assert r["result"] is None

    def test_has_rulesets_is_none(self):
        r = compute_c20_severity(404, [{"id": 1}], [], False, "2026-04-15", True, "2026-04-17")
        assert r["result"] is None

    def test_boundary_31_days_is_warning(self):
        """zustand boundary case: 31 days = 1 day outside Critical window"""
        r = compute_c20_severity(404, [], [], False, "2026-03-17", True, "2026-04-17")
        assert r["result"] == "Warning"
        assert r["has_recent_release_30d"] is False

    def test_boundary_30_days_is_critical(self):
        r = compute_c20_severity(404, [], [], False, "2026-03-18", True, "2026-04-17")
        assert r["result"] == "Critical"
        assert r["has_recent_release_30d"] is True

    def test_not_executable_is_warning(self):
        r = compute_c20_severity(404, [], [], False, "2026-04-15", False, "2026-04-17")
        assert r["result"] == "Warning"


# ===========================================================================
# Scorecard Cells
# ===========================================================================

class TestScorecardCells:

    def test_all_green(self):
        r = compute_scorecard_cells(
            formal_review_rate=50, any_review_rate=80,
            has_branch_protection=True, has_codeowners=True,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=0,
            has_security_policy=True, published_advisory_count=2,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_critical_on_default_path=False, has_warning_on_install_path=False,
        )
        assert r["does_anyone_check_the_code"]["color"] == "green"
        assert r["do_they_fix_problems_quickly"]["color"] == "green"
        assert r["do_they_tell_you_about_problems"]["color"] == "green"
        assert r["is_it_safe_out_of_the_box"]["color"] == "green"

    def test_no_reviews_is_red(self):
        r = compute_scorecard_cells(
            formal_review_rate=0, any_review_rate=10,
            has_branch_protection=False, has_codeowners=False,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False,
            all_channels_pinned=False, artifact_verified=False,
            has_critical_on_default_path=False, has_warning_on_install_path=False,
        )
        assert r["does_anyone_check_the_code"]["color"] == "red"

    def test_many_open_issues_is_red(self):
        r = compute_scorecard_cells(
            formal_review_rate=50, any_review_rate=80,
            has_branch_protection=True, has_codeowners=True,
            is_solo_maintainer=False,
            open_security_issue_count=5, oldest_cve_pr_age_days=30,
            has_security_policy=True, published_advisory_count=2,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_critical_on_default_path=False, has_warning_on_install_path=False,
        )
        assert r["do_they_fix_problems_quickly"]["color"] == "red"

    def test_zustand_like_inputs(self):
        """zustand: ~29% formal, no protection, no CODEOWNERS → amber Q1"""
        r = compute_scorecard_cells(
            formal_review_rate=29, any_review_rate=71,
            has_branch_protection=False, has_codeowners=False,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_critical_on_default_path=False, has_warning_on_install_path=True,
        )
        assert r["does_anyone_check_the_code"]["color"] == "amber"

    def test_solo_maintainer_low_review_is_red(self):
        """Solo maintainer with any-review < 40% → red Q1"""
        r = compute_scorecard_cells(
            formal_review_rate=10, any_review_rate=35,
            has_branch_protection=False, has_codeowners=False,
            is_solo_maintainer=True,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_critical_on_default_path=False, has_warning_on_install_path=False,
        )
        assert r["does_anyone_check_the_code"]["color"] == "red"

    def test_q4_critical_on_default_is_red(self):
        """Critical finding on default install path → Q4 red"""
        r = compute_scorecard_cells(
            formal_review_rate=50, any_review_rate=80,
            has_branch_protection=True, has_codeowners=True,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=True, published_advisory_count=2,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_critical_on_default_path=True, has_warning_on_install_path=True,
        )
        assert r["is_it_safe_out_of_the_box"]["color"] == "red"

    def test_q4_warning_no_critical_is_amber(self):
        """Warning finding but no Critical → Q4 amber"""
        r = compute_scorecard_cells(
            formal_review_rate=50, any_review_rate=80,
            has_branch_protection=True, has_codeowners=True,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=True, published_advisory_count=2,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_critical_on_default_path=False, has_warning_on_install_path=True,
        )
        assert r["is_it_safe_out_of_the_box"]["color"] == "amber"


# ===========================================================================
# SF1 Board patches (2026-04-20, temporary V1.1 compatibility)
# ===========================================================================

class TestSF1ScorecardPatches:
    """Regression tests for the 4 scorecard calibration patches from
    docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md."""

    def _base_kwargs(self):
        # Reasonable neutral baseline — caller overrides as needed
        return dict(
            formal_review_rate=50, any_review_rate=80,
            has_branch_protection=True, has_codeowners=True,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=True, published_advisory_count=2,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_critical_on_default_path=False, has_warning_on_install_path=False,
        )

    def _signal_value(self, cell, signal_id):
        """V1.2: scorecard cells emit signals: [{id, value}] (was inputs dict in V1.1)."""
        for sig in cell.get("signals", []):
            if sig.get("id") == signal_id:
                return sig.get("value")
        return None

    def test_q1_governance_floor_forces_red(self):
        """Archon-shape: 8% formal + high any + no protection + no CODEOWNERS → red
        via governance-floor override, even though any >= 50 would normally be amber."""
        kw = self._base_kwargs()
        kw.update(formal_review_rate=8, any_review_rate=58,
                  has_branch_protection=False, has_codeowners=False)
        r = compute_scorecard_cells(**kw)
        assert r["does_anyone_check_the_code"]["color"] == "red"
        assert self._signal_value(r["does_anyone_check_the_code"], "q1_governance_floor_override") is True

    def test_q1_governance_floor_not_triggered_if_formal_at_10(self):
        """Threshold boundary: formal >= 10 does not trigger the override."""
        kw = self._base_kwargs()
        kw.update(formal_review_rate=10, any_review_rate=58,
                  has_branch_protection=False, has_codeowners=False)
        r = compute_scorecard_cells(**kw)
        assert r["does_anyone_check_the_code"]["color"] == "amber"
        assert self._signal_value(r["does_anyone_check_the_code"], "q1_governance_floor_override") is False

    def test_q1_governance_floor_not_triggered_if_branch_protection_present(self):
        """Override requires ALL three gaps — having branch protection cancels it."""
        kw = self._base_kwargs()
        kw.update(formal_review_rate=5, any_review_rate=58,
                  has_branch_protection=True, has_codeowners=False)
        r = compute_scorecard_cells(**kw)
        # With branch protection, governance floor does NOT fire; falls through to standard amber
        assert r["does_anyone_check_the_code"]["color"] == "amber"

    def test_q2_closed_fix_lag_over_3_days_drops_green_to_amber(self):
        """Caveman-shape: 0 open, merged security PR took 5 days → amber, not green."""
        kw = self._base_kwargs()
        kw.update(open_security_issue_count=0, oldest_cve_pr_age_days=None,
                  closed_fix_lag_days=5)
        r = compute_scorecard_cells(**kw)
        assert r["do_they_fix_problems_quickly"]["color"] == "amber"

    def test_q2_closed_fix_lag_at_3_days_stays_green(self):
        """Threshold boundary: lag <= 3 days keeps green."""
        kw = self._base_kwargs()
        kw.update(open_security_issue_count=0, oldest_cve_pr_age_days=None,
                  closed_fix_lag_days=3)
        r = compute_scorecard_cells(**kw)
        assert r["do_they_fix_problems_quickly"]["color"] == "green"

    def test_q2_closed_fix_lag_none_defaults_to_green_when_no_open(self):
        """Default behavior preserved: no closed_fix_lag info → green if no open issues."""
        kw = self._base_kwargs()
        # closed_fix_lag_days not passed → defaults to None
        r = compute_scorecard_cells(**kw)
        assert r["do_they_fix_problems_quickly"]["color"] == "green"

    def test_q3_contributing_guide_alone_is_amber_floor(self):
        """Zustand-shape: no SECURITY.md BUT has contributing guide → amber, not red."""
        kw = self._base_kwargs()
        kw.update(has_security_policy=False, published_advisory_count=0,
                  has_contributing_guide=True)
        r = compute_scorecard_cells(**kw)
        assert r["do_they_tell_you_about_problems"]["color"] == "amber"

    def test_q3_no_policy_no_contributing_guide_is_red(self):
        """No SECURITY.md AND no contributing guide AND no advisories → red (pre-patch behavior preserved)."""
        kw = self._base_kwargs()
        kw.update(has_security_policy=False, published_advisory_count=0,
                  has_contributing_guide=False)
        r = compute_scorecard_cells(**kw)
        assert r["do_they_tell_you_about_problems"]["color"] == "red"

    def test_q4_install_path_scope_separates_governance_from_install(self):
        """Zustand-shape: governance Warning (F0 no branch protection) does NOT block green
        because has_warning_on_install_path is False."""
        kw = self._base_kwargs()
        kw.update(all_channels_pinned=True, artifact_verified=True,
                  has_warning_on_install_path=False)  # F0 is governance, not install
        r = compute_scorecard_cells(**kw)
        assert r["is_it_safe_out_of_the_box"]["color"] == "green"

    def test_q4_install_path_warning_drops_green_to_amber(self):
        """An install-path Warning (e.g. lifecycle hook, postinstall) does block green."""
        kw = self._base_kwargs()
        kw.update(all_channels_pinned=True, artifact_verified=True,
                  has_warning_on_install_path=True)
        r = compute_scorecard_cells(**kw)
        assert r["is_it_safe_out_of_the_box"]["color"] == "amber"


# ===========================================================================
# Solo Maintainer
# ===========================================================================

class TestSoloMaintainer:

    def test_solo_above_80(self):
        contribs = [{"login": "alice", "contributions": 90},
                    {"login": "bob", "contributions": 10}]
        r = compute_solo_maintainer(contribs)
        assert r["is_solo"] is True
        assert "alice" in r["verbatim_sentence"]

    def test_not_solo_below_80(self):
        contribs = [{"login": "alice", "contributions": 70},
                    {"login": "bob", "contributions": 30}]
        r = compute_solo_maintainer(contribs)
        assert r["is_solo"] is False

    def test_empty_contributors(self):
        r = compute_solo_maintainer([])
        assert r["is_solo"] is False


# ===========================================================================
# Exhibit Grouping
# ===========================================================================

class TestExhibitGrouping:

    def test_below_threshold(self):
        findings = [{"id": f"F{i}", "severity": "Warning", "category": "governance/x"} for i in range(5)]
        r = compute_exhibit_grouping(findings)
        assert r["threshold_met"] is False

    def test_above_threshold_groups_correctly(self):
        findings = (
            [{"id": f"F{i}", "severity": "Warning", "category": "vuln/x"} for i in range(3)] +
            [{"id": f"F{i+3}", "severity": "Warning", "category": "governance/x"} for i in range(3)] +
            [{"id": f"F{i+6}", "severity": "OK", "category": "code/x"} for i in range(2)]
        )
        r = compute_exhibit_grouping(findings)
        assert r["threshold_met"] is True
        themes = [e["theme"] for e in r["exhibits"]]
        assert "vuln" in themes
        assert "govern" in themes
        assert "signals" in themes


# ===========================================================================
# Boundary Cases
# ===========================================================================

class TestBoundaryCases:

    def test_31_days_flags_boundary(self):
        r = compute_boundary_cases(31, None, None)
        assert len(r["cases"]) == 1
        assert r["cases"][0]["margin"] == 1

    def test_29_days_flags_inside(self):
        r = compute_boundary_cases(29, None, None)
        assert len(r["cases"]) == 1
        assert r["cases"][0]["margin"] == -1

    def test_60_days_no_boundary(self):
        r = compute_boundary_cases(60, None, None)
        assert len(r["cases"]) == 0


# ===========================================================================
# F5 Silent vs Unadvertised
# ===========================================================================

class TestF5Classification:

    def test_attack_class_in_title_is_unadvertised(self):
        r = classify_f5_disclosure("Hardening release: symlink-safe writes", "", "symlink")
        assert r == "unadvertised"

    def test_security_keyword_in_notes_is_unadvertised(self):
        r = classify_f5_disclosure("v1.6.0", "This release includes a security fix", "buffer overflow")
        assert r == "unadvertised"

    def test_no_mention_is_silent(self):
        r = classify_f5_disclosure("chore: minor improvements", "Bug fixes and performance", "symlink attack")
        assert r == "silent"


# ===========================================================================
# Verdict
# ===========================================================================

class TestVerdict:

    def test_critical_finding_gives_critical(self):
        findings = [{"id": "F0", "severity": "Critical"}, {"id": "F1", "severity": "Warning"}]
        r = compute_verdict(findings)
        assert r["level"] == "Critical"

    def test_warning_only_gives_caution(self):
        findings = [{"id": "F0", "severity": "Warning"}, {"id": "F1", "severity": "OK"}]
        r = compute_verdict(findings)
        assert r["level"] == "Caution"

    def test_ok_only_gives_clean(self):
        findings = [{"id": "F0", "severity": "OK"}]
        r = compute_verdict(findings)
        assert r["level"] == "Clean"

    def test_no_findings_gives_clean(self):
        r = compute_verdict([])
        assert r["level"] == "Clean"

    def test_info_gives_caution(self):
        findings = [{"id": "F0", "severity": "Info"}]
        r = compute_verdict(findings)
        assert r["level"] == "Caution"


# ===========================================================================
# Coverage Status
# ===========================================================================

class TestCoverageStatus:

    def test_basic_coverage(self):
        raw = {
            "pre_flight": {"tarball_extracted": True, "tarball_file_count": 100,
                           "api_rate_limit": {"remaining": 4500, "limit": 5000}},
            "ossf_scorecard": {"queried": True, "indexed": True, "overall_score": 5.9},
            "dependencies": {"runtime_count": 0, "osv_dev": {"queried": False},
                             "dependabot": {"status": "disabled", "error_message": "Disabled"}},
            "gitleaks": {"available": False, "ran": False},
        }
        r = compute_coverage_status(raw)
        names = [c["name"] for c in r["cells"]]
        assert "Tarball extraction" in names
        assert "OSSF Scorecard" in names
        assert any(c["status"] == "ok" for c in r["cells"] if c["name"] == "Tarball extraction")


# ===========================================================================
# V1.2.x V13-1 signal widening helpers
# ===========================================================================

class TestV13_1_RulesetProtectionHelper:
    """derive_q1_has_ruleset_protection — V1.2.x signal widening."""

    def test_no_branch_protection_object_returns_false(self):
        assert derive_q1_has_ruleset_protection(None) is False
        assert derive_q1_has_ruleset_protection({}) is False

    def test_classic_only_returns_false(self):
        bp = {
            "classic": {"status": 200},
            "rulesets": {"count": 0, "entries": []},
            "rules_on_default": {"count": 0, "entries": []},
        }
        assert derive_q1_has_ruleset_protection(bp) is False

    def test_ruleset_and_rules_returns_true(self):
        bp = {
            "classic": {"status": 404},
            "rulesets": {"count": 1, "entries": [{"name": "main-protect"}]},
            "rules_on_default": {"count": 4, "entries": [{"type": "pull_request"}]},
        }
        assert derive_q1_has_ruleset_protection(bp) is True

    def test_ruleset_without_rules_on_default_returns_false(self):
        """Ghost ruleset that doesn't apply to default branch doesn't count."""
        bp = {
            "classic": {"status": 404},
            "rulesets": {"count": 1, "entries": []},
            "rules_on_default": {"count": 0, "entries": []},
        }
        assert derive_q1_has_ruleset_protection(bp) is False

    def test_copilot_only_ruleset_still_counts(self):
        """kamal entry 18 shape: 1 Copilot-review rule. Weak but ≥1."""
        bp = {
            "classic": {"status": 404},
            "rulesets": {"count": 1},
            "rules_on_default": {"count": 1, "entries": [{"type": "copilot_code_review"}]},
        }
        assert derive_q1_has_ruleset_protection(bp) is True


class TestV13_1_SecurityItemAgeHelper:
    """derive_q2_oldest_open_security_item_age_days — V1.2.x signal widening."""

    def test_nothing_matches_returns_none(self):
        r = derive_q2_oldest_open_security_item_age_days(
            {"open_security_issues": []},
            {"entries": []},
            scan_date_iso="2026-04-20",
        )
        assert r is None

    def test_open_issue_returns_age(self):
        """Kronos entry 17 shape: issue #216 opened 2026-01-15 → 95 days."""
        iss = {
            "open_security_issues": [
                {"number": 216, "title": "Security Issue: Unsafe deserialization", "created_at": "2026-01-15T00:00:00Z"}
            ]
        }
        r = derive_q2_oldest_open_security_item_age_days(iss, {}, scan_date_iso="2026-04-20")
        assert r == 95

    def test_security_keyword_pr_returns_age(self):
        prs = {
            "entries": [
                {"number": 249, "title": "fix: replace unsafe pickle.load with restricted unpickler",
                 "created_at": "2026-04-13T00:00:00Z"},
                {"number": 250, "title": "chore: routine bump", "created_at": "2026-04-01T00:00:00Z"},
            ]
        }
        r = derive_q2_oldest_open_security_item_age_days({}, prs, scan_date_iso="2026-04-20")
        # Only PR #249 matches (pickle keyword). #250 is non-security — ignored.
        assert r == 7

    def test_max_of_issue_and_pr(self):
        iss = {"open_security_issues": [
            {"number": 216, "created_at": "2026-01-15T00:00:00Z"},
        ]}
        prs = {"entries": [
            {"number": 249, "title": "fix: security RCE", "created_at": "2026-04-13T00:00:00Z"},
        ]}
        r = derive_q2_oldest_open_security_item_age_days(iss, prs, scan_date_iso="2026-04-20")
        assert r == 95  # max of 95 and 7

    def test_non_security_pr_not_matched(self):
        prs = {"entries": [
            {"number": 100, "title": "feat: new CLI flag", "created_at": "2025-01-01T00:00:00Z"},
        ]}
        r = derive_q2_oldest_open_security_item_age_days({}, prs, scan_date_iso="2026-04-20")
        assert r is None  # PR has no security keyword


class TestV13_1_Q1WidenedGovernanceFloor:
    """compute_scorecard_cells Q1 governance floor reads has_any_branch_protection."""

    def test_ruleset_protection_breaks_governance_floor(self):
        """ghostty entry 16 shape: classic 404 but ruleset present → NOT red via floor."""
        r = compute_scorecard_cells(
            formal_review_rate=0, any_review_rate=30,
            has_branch_protection=False,  # classic 404
            has_ruleset_protection=True,  # ← V1.2.x widening
            has_codeowners=False,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False, all_channels_pinned=True,
            artifact_verified=True, has_critical_on_default_path=False,
            has_warning_on_install_path=False,
        )
        # Without ruleset widening this hits the governance floor (red).
        # With ruleset widening, has_any_branch_protection=True, floor avoided.
        q1 = r["does_anyone_check_the_code"]
        floor_signal = next(s for s in q1["signals"] if s["id"] == "q1_governance_floor_override")
        assert floor_signal["value"] is False
        # Color depends on other signals but should NOT be red-via-floor.
        # any_rev=30 with solo=False means not red, falls to amber via any<50.

    def test_classic_only_same_behavior_as_before(self):
        """Regression: classic-only protection behaves identically to pre-V13-1."""
        r = compute_scorecard_cells(
            formal_review_rate=5, any_review_rate=30,
            has_branch_protection=True, has_codeowners=False,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False, all_channels_pinned=True,
            artifact_verified=True, has_critical_on_default_path=False,
            has_warning_on_install_path=False,
        )
        # Floor: formal<10 AND not has_any_bp (True via classic) AND not codeowners → NOT triggered (bp present)
        q1 = r["does_anyone_check_the_code"]
        floor_signal = next(s for s in q1["signals"] if s["id"] == "q1_governance_floor_override")
        assert floor_signal["value"] is False


class TestV13_1_Q2WidenedEvidence:
    """compute_scorecard_cells Q2 uses max(cve_pr_age, security_item_age)."""

    def test_security_item_age_escalates_q2(self):
        """Kronos entry 17 shape: cve_pr_age=None but issue age=95 days → Q2 red."""
        r = compute_scorecard_cells(
            formal_review_rate=0, any_review_rate=5,
            has_branch_protection=False, has_codeowners=False,
            is_solo_maintainer=False,
            open_security_issue_count=1,
            oldest_cve_pr_age_days=None,
            oldest_open_security_item_age_days=95,  # ← V1.2.x widening
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False, all_channels_pinned=False,
            artifact_verified=False, has_critical_on_default_path=False,
            has_warning_on_install_path=False,
        )
        # cve_age = max(0, 95) = 95; open_security=1; 95>14 → red via else branch
        assert r["do_they_fix_problems_quickly"]["color"] == "red"
        signals = r["do_they_fix_problems_quickly"]["signals"]
        assert any(s["id"] == "q2_oldest_open_security_item_age_days" and s["value"] == 95 for s in signals)

    def test_security_item_age_absent_falls_back(self):
        """Default None for security_item_age: Q2 uses old cve_pr_age logic."""
        r = compute_scorecard_cells(
            formal_review_rate=0, any_review_rate=5,
            has_branch_protection=False, has_codeowners=False,
            is_solo_maintainer=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=0,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False, all_channels_pinned=False,
            artifact_verified=False, has_critical_on_default_path=False,
            has_warning_on_install_path=False,
        )
        # 0 open issues, cve_age=max(0,0)=0, closed_fix_lag=None → green
        assert r["do_they_fix_problems_quickly"]["color"] == "green"


class TestV13_3_DeriveToolLoadsUserFiles:
    """V1.2.x (V13-3 C18, owner directive 2026-04-20): canonical helper for
    'tool loads user files' judgment. Used as precondition for C5 Q4 auto-fire.
    """

    def test_readme_with_open_a_file_phrase_fires(self):
        readme = "freerouting opens a file from disk when the user imports a design..."
        assert derive_tool_loads_user_files(readme, None) is True

    def test_readme_with_load_design_phrase_fires(self):
        readme = "Load a design board for autorouting. Specctra DSN format supported."
        assert derive_tool_loads_user_files(readme, None) is True

    def test_readme_with_parse_document_phrase_fires(self):
        readme = "markitdown parses a document into Markdown. Supports .pdf, .docx, .epub."
        assert derive_tool_loads_user_files(readme, None) is True

    def test_readme_with_load_pickle_in_ml_context_fires(self):
        readme = "Kronos loads a pretrained model checkpoint from Hugging Face."
        assert derive_tool_loads_user_files(readme, None) is True

    def test_topic_document_conversion_fires(self):
        repo_meta = {"topics": ["document-conversion", "pdf", "markdown"]}
        assert derive_tool_loads_user_files(None, repo_meta) is True

    def test_topic_eda_fires(self):
        repo_meta = {"topics": ["eda", "pcb", "autorouter"]}
        assert derive_tool_loads_user_files(None, repo_meta) is True

    def test_topic_ml_fires(self):
        repo_meta = {"topics": ["foundation-model", "pretrained", "pytorch"]}
        assert derive_tool_loads_user_files(None, repo_meta) is True

    def test_no_readme_and_no_metadata_returns_false(self):
        assert derive_tool_loads_user_files(None, None) is False

    def test_readme_without_matching_phrase_returns_false(self):
        readme = "kanata is a keyboard remapping daemon with Lisp-style config."
        assert derive_tool_loads_user_files(readme, None) is False

    def test_irrelevant_topics_return_false(self):
        repo_meta = {"topics": ["terminal-emulator", "rust", "gpu-accelerated"]}
        assert derive_tool_loads_user_files(None, repo_meta) is False


class TestV13_3_Q4AutoFireFromDeserialization:
    """V1.2.x (V13-3 C5): auto-fire q4_has_critical_on_default_path when unsafe
    deserialization hits are present AND tool loads user files. Would have
    collapsed Kronos + freerouting Q4 overrides without Phase 4 authoring.
    """

    def test_freerouting_pattern_auto_fires(self):
        """35 ObjectInputStream hits + README mentions opening files → True."""
        dp = {"deserialization": {"hit_count": 35, "files": []}}
        readme = "freerouting opens a board file and auto-routes traces between components."
        assert derive_q4_critical_on_default_path_from_deserialization(
            dp, readme_text=readme
        ) is True

    def test_kronos_pattern_auto_fires(self):
        """pickle.load hit + ML topic → True. Would collapse Kronos Q4 override."""
        dp = {"deserialization": {"hit_count": 3, "files": []}}
        repo_meta = {"topics": ["foundation-model", "pretrained"]}
        assert derive_q4_critical_on_default_path_from_deserialization(
            dp, repo_metadata=repo_meta
        ) is True

    def test_wled_arduinojson_does_not_fire(self):
        """WLED had 19 ArduinoJson deserializeJson hits — suppressed by V13-3 C2
        language qualifier, so hit_count=0 here. Simulates post-C2 state."""
        dp = {"deserialization": {"hit_count": 0, "files": []}}
        readme = "WLED is a firmware for addressable LEDs over WiFi."
        repo_meta = {"topics": ["esp32", "led", "firmware"]}
        assert derive_q4_critical_on_default_path_from_deserialization(
            dp, readme_text=readme, repo_metadata=repo_meta
        ) is False

    def test_below_threshold_does_not_fire(self):
        """2 hits + loads-files → False (below default threshold of 3)."""
        dp = {"deserialization": {"hit_count": 2, "files": []}}
        readme = "Opens a file and does something."
        assert derive_q4_critical_on_default_path_from_deserialization(
            dp, readme_text=readme
        ) is False

    def test_above_threshold_but_no_user_files_does_not_fire(self):
        """10 hits but README/topics don't indicate file loading → False.
        Avoids firing on internal deserialization."""
        dp = {"deserialization": {"hit_count": 10, "files": []}}
        assert derive_q4_critical_on_default_path_from_deserialization(
            dp, readme_text="An internal RPC library for service-to-service calls."
        ) is False

    def test_missing_dangerous_primitives_returns_false(self):
        assert derive_q4_critical_on_default_path_from_deserialization(
            None, readme_text="opens a file"
        ) is False

    def test_custom_threshold_respected(self):
        """Caller can override threshold; default is 3."""
        dp = {"deserialization": {"hit_count": 5, "files": []}}
        readme = "opens a file"
        assert derive_q4_critical_on_default_path_from_deserialization(
            dp, readme_text=readme, threshold=10
        ) is False
        assert derive_q4_critical_on_default_path_from_deserialization(
            dp, readme_text=readme, threshold=3
        ) is True


class TestV13_3_C5LiveIntegrationInScorecardCells:
    """V1.2.x (V13-3 C5 LIVE INTEGRATION, per Codex code-review r2 gate):
    compute_scorecard_cells() now accepts phase_1_raw_capture and auto-fires
    Q4 red when the deserialization + tool-loads-user-files condition is met.
    This is the production integration point that makes C5 live — no scan
    driver has to remember to pre-compute the auto-fire, it happens inside
    compute_scorecard_cells.
    """

    _BASE_KWARGS = dict(
        formal_review_rate=50, any_review_rate=80,
        has_branch_protection=True, has_codeowners=True,
        is_solo_maintainer=False,
        open_security_issue_count=0, oldest_cve_pr_age_days=0,
        has_security_policy=True, published_advisory_count=2,
        has_silent_fixes=False,
        all_channels_pinned=True, artifact_verified=True,
        has_critical_on_default_path=False,  # Phase-4-authored default
        has_warning_on_install_path=False,
    )

    def test_freerouting_phase_1_upgrades_q4_to_red(self):
        """Baseline kwargs have Q4 green (no critical/warning explicit).
        Passing phase_1_raw_capture with 35 ObjectInputStream hits + pcb topic
        triggers C5 auto-fire → Q4 upgrades to red."""
        p1 = {
            "code_patterns": {
                "dangerous_primitives": {
                    "deserialization": {"hit_count": 35, "files": []},
                }
            },
            "repo_metadata": {"topics": ["pcb", "autorouter"]},
        }
        r = compute_scorecard_cells(**self._BASE_KWARGS, phase_1_raw_capture=p1)
        assert r["is_it_safe_out_of_the_box"]["color"] == "red", (
            "C5 auto-fire should upgrade Q4 from green to red when "
            "phase_1_raw_capture shows unsafe deserialization + pcb topic"
        )

    def test_wled_phase_1_does_not_upgrade_q4(self):
        """ArduinoJson-shape phase_1 (hit_count=0 after C2 suppression) does
        not trigger C5 auto-fire → Q4 stays green."""
        p1 = {
            "code_patterns": {
                "dangerous_primitives": {
                    "deserialization": {"hit_count": 0, "files": []},
                }
            },
            "repo_metadata": {"topics": ["esp32", "led", "firmware"]},
        }
        r = compute_scorecard_cells(**self._BASE_KWARGS, phase_1_raw_capture=p1)
        assert r["is_it_safe_out_of_the_box"]["color"] == "green"

    def test_no_phase_1_preserves_existing_behavior(self):
        """Without phase_1_raw_capture, compute_scorecard_cells behavior is
        unchanged — backwards compatibility for historical scan drivers."""
        r = compute_scorecard_cells(**self._BASE_KWARGS)
        assert r["is_it_safe_out_of_the_box"]["color"] == "green"

    def test_explicit_true_kwarg_not_downgraded_by_nonfiring_phase_1(self):
        """OR-merge semantics: if caller explicitly passed
        has_critical_on_default_path=True but phase_1 doesn't auto-fire, Q4
        stays red. The auto-fire never DOWNGRADES; it only upgrades."""
        kwargs = dict(self._BASE_KWARGS)
        kwargs["has_critical_on_default_path"] = True
        p1 = {
            "code_patterns": {"dangerous_primitives": {"deserialization": {"hit_count": 0, "files": []}}},
            "repo_metadata": {"topics": ["terminal-emulator"]},
        }
        r = compute_scorecard_cells(**kwargs, phase_1_raw_capture=p1)
        assert r["is_it_safe_out_of_the_box"]["color"] == "red"


class TestV13_3_ComputeQ4AutofiresFromPhase1:
    """V1.2.x (V13-3 C5): unit tests for the wrapper. In the integrated design,
    compute_scorecard_cells() calls this wrapper internally when
    phase_1_raw_capture is passed — see TestV13_3_C5LiveIntegrationInScorecardCells
    above for end-to-end coverage. These tests exercise the wrapper in
    isolation (null inputs, missing-code-patterns, negative cases) for unit-
    level regression coverage.
    """

    def test_freerouting_shape_fires(self):
        """Phase-1-shaped input with 35 ObjectInputStream hits + pcb topic →
        auto-fire. Would collapse freerouting Q4 override."""
        p1 = {
            "code_patterns": {
                "dangerous_primitives": {
                    "deserialization": {"hit_count": 35, "files": []},
                }
            },
            "repo_metadata": {"topics": ["pcb", "autorouter", "eda"]},
        }
        r = compute_q4_autofires_from_phase_1(p1)
        assert r["has_critical_on_default_path"] is True
        assert "deserialization_c5" in r["reasons"]

    def test_wled_shape_does_not_fire(self):
        """Phase-1-shaped input with post-C2 hit_count=0 (ArduinoJson
        suppressed) + firmware topics (not in _FILE_LOADING_TOPICS) → no fire.
        Confirms WLED class does not auto-fire."""
        p1 = {
            "code_patterns": {
                "dangerous_primitives": {
                    "deserialization": {"hit_count": 0, "files": []},
                }
            },
            "repo_metadata": {"topics": ["esp32", "led", "firmware"]},
        }
        r = compute_q4_autofires_from_phase_1(p1)
        assert r["has_critical_on_default_path"] is False
        assert r["reasons"] == []

    def test_missing_phase_1_returns_false(self):
        r = compute_q4_autofires_from_phase_1(None)
        assert r == {"has_critical_on_default_path": False, "reasons": []}

    def test_missing_code_patterns_returns_false(self):
        p1 = {"repo_metadata": {"topics": ["pcb"]}}
        r = compute_q4_autofires_from_phase_1(p1)
        assert r["has_critical_on_default_path"] is False

    def test_missing_dangerous_primitives_returns_false(self):
        p1 = {"code_patterns": {}, "repo_metadata": {"topics": ["pcb"]}}
        r = compute_q4_autofires_from_phase_1(p1)
        assert r["has_critical_on_default_path"] is False

    def test_deserialization_without_loads_user_files_does_not_fire(self):
        """20 hits but no matching README/topics → no fire. Avoids firing on
        internal-RPC-only deserialization where file-loading condition is
        absent."""
        p1 = {
            "code_patterns": {
                "dangerous_primitives": {
                    "deserialization": {"hit_count": 20, "files": []},
                }
            },
            "repo_metadata": {"topics": ["rpc", "grpc"]},
        }
        r = compute_q4_autofires_from_phase_1(p1)
        assert r["has_critical_on_default_path"] is False


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
