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

    def test_q1_governance_floor_forces_red(self):
        """Archon-shape: 8% formal + high any + no protection + no CODEOWNERS → red
        via governance-floor override, even though any >= 50 would normally be amber."""
        kw = self._base_kwargs()
        kw.update(formal_review_rate=8, any_review_rate=58,
                  has_branch_protection=False, has_codeowners=False)
        r = compute_scorecard_cells(**kw)
        assert r["does_anyone_check_the_code"]["color"] == "red"
        assert r["does_anyone_check_the_code"]["inputs"]["governance_floor_triggered"] is True

    def test_q1_governance_floor_not_triggered_if_formal_at_10(self):
        """Threshold boundary: formal >= 10 does not trigger the override."""
        kw = self._base_kwargs()
        kw.update(formal_review_rate=10, any_review_rate=58,
                  has_branch_protection=False, has_codeowners=False)
        r = compute_scorecard_cells(**kw)
        assert r["does_anyone_check_the_code"]["color"] == "amber"
        assert r["does_anyone_check_the_code"]["inputs"]["governance_floor_triggered"] is False

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


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
