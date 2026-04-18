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
            open_security_issue_count=0, oldest_cve_pr_age_days=0,
            has_security_policy=True, published_advisory_count=2,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_warning_or_above=False,
        )
        assert r["does_anyone_check_the_code"]["color"] == "green"
        assert r["do_they_fix_problems_quickly"]["color"] == "green"
        assert r["do_they_tell_you_about_problems"]["color"] == "green"
        assert r["is_it_safe_out_of_the_box"]["color"] == "green"

    def test_no_reviews_is_red(self):
        r = compute_scorecard_cells(
            formal_review_rate=0, any_review_rate=10,
            has_branch_protection=False, has_codeowners=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False,
            all_channels_pinned=False, artifact_verified=False,
            has_warning_or_above=False,
        )
        assert r["does_anyone_check_the_code"]["color"] == "red"

    def test_many_open_issues_is_red(self):
        r = compute_scorecard_cells(
            formal_review_rate=50, any_review_rate=80,
            has_branch_protection=True, has_codeowners=True,
            open_security_issue_count=5, oldest_cve_pr_age_days=30,
            has_security_policy=True, published_advisory_count=2,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_warning_or_above=False,
        )
        assert r["do_they_fix_problems_quickly"]["color"] == "red"

    def test_zustand_like_inputs(self):
        """zustand: ~29% formal, no protection, no CODEOWNERS → amber Q1"""
        r = compute_scorecard_cells(
            formal_review_rate=29, any_review_rate=71,
            has_branch_protection=False, has_codeowners=False,
            open_security_issue_count=0, oldest_cve_pr_age_days=None,
            has_security_policy=False, published_advisory_count=0,
            has_silent_fixes=False,
            all_channels_pinned=True, artifact_verified=True,
            has_warning_or_above=True,
        )
        assert r["does_anyone_check_the_code"]["color"] == "amber"


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
