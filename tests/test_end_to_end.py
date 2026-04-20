#!/usr/bin/env python3
"""
End-to-end test: zustand investigation form → compute.py → verify outputs.

This is the golden-file integration test the board recommended before
building renderers. It validates that compute.py produces the same
outputs as the manually-verified zustand scan.

Run: python3 -m pytest tests/test_end_to_end.py -v
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))
from compute import (
    compute_c20_severity,
    compute_scorecard_cells,
    compute_solo_maintainer,
    compute_exhibit_grouping,
    compute_boundary_cases,
    compute_coverage_status,
    compute_verdict,
    classify_f5_disclosure,
)

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "zustand-form.json"


def load_fixture():
    """Load the zustand test fixture."""
    assert FIXTURE.exists(), f"Fixture not found: {FIXTURE}"
    with open(FIXTURE) as f:
        return json.load(f)


class TestZustandEndToEnd:
    """Verify compute.py outputs match the zustand gold standard."""

    def test_fixture_loads(self):
        form = load_fixture()
        assert form["schema_version"] in ("1.0", "1.1")
        assert form["target"]["repo"] == "zustand"

    def test_c20_severity_is_warning(self):
        """zustand has no branch protection but release is 31 days old → Warning not Critical"""
        form = load_fixture()
        raw = form["phase_1_raw_capture"]
        bp = raw["branch_protection"]

        result = compute_c20_severity(
            classic_protection_status=bp["classic"]["status"],
            rulesets=bp["rulesets"].get("entries", []),
            rules_on_default=bp["rules_on_default"].get("entries", []),
            has_codeowners=raw["codeowners"]["found"],
            latest_release_date=raw["releases"]["entries"][0]["date"] if raw["releases"]["entries"] else None,
            ships_executable_code=True,  # npm package = executable
            scan_date="2026-04-16",
        )
        assert result["result"] == "Warning", f"Expected Warning, got {result['result']}"
        assert result["no_classic_protection"] is True
        assert result["no_codeowners"] is True

    def test_solo_maintainer_is_false(self):
        """zustand: dai-shi has ~53% of commits, NOT solo maintainer"""
        form = load_fixture()
        contribs = form["phase_1_raw_capture"]["contributors"]["top_contributors"]
        result = compute_solo_maintainer(contribs)
        assert result["is_solo"] is False
        assert result["top_contributor_share"] < 0.80

    def test_scorecard_q1_is_amber(self):
        """zustand: ~29% formal review, ~71% any review, no protection → amber"""
        form = load_fixture()
        raw = form["phase_1_raw_capture"]
        result = compute_scorecard_cells(
            formal_review_rate=raw["pr_review"]["formal_review_rate"],
            any_review_rate=raw["pr_review"]["any_review_rate"],
            has_branch_protection=raw["branch_protection"]["classic"]["status"] == 200,
            has_codeowners=raw["codeowners"]["found"],
            is_solo_maintainer=False,
            open_security_issue_count=len(raw.get("issues_and_commits", {}).get("open_security_issues", [])),
            oldest_cve_pr_age_days=None,
            has_security_policy=raw["community_profile"]["has_security_policy"],
            published_advisory_count=raw["security_advisories"]["count"] or 0,
            has_silent_fixes=False,
            all_channels_pinned=True,  # npm OIDC
            artifact_verified=True,
            has_critical_on_default_path=False,
            has_warning_on_install_path=True,  # F0 is Warning
        )
        assert result["does_anyone_check_the_code"]["color"] == "amber"

    def test_verdict_is_caution(self):
        """zustand: has Warning findings → Caution"""
        form = load_fixture()
        findings = form.get("phase_4_structured_llm", {}).get("findings", {}).get("entries", [])
        if findings:
            result = compute_verdict(findings)
            assert result["level"] == "Caution"

    def test_boundary_case_detected(self):
        """zustand: 31-day release age should flag boundary case"""
        result = compute_boundary_cases(
            latest_release_age_days=31,
            formal_review_rate=29,
            any_review_rate=71,
        )
        # Should detect the C20 30-day boundary
        c20_cases = [c for c in result["cases"] if "C20" in c.get("threshold", "")]
        assert len(c20_cases) > 0, "Should detect C20 boundary case at 31 days"
        assert c20_cases[0]["margin"] == 1

    def test_coverage_status_ossf_indexed(self):
        """zustand: OSSF Scorecard indexed at 5.9/10"""
        form = load_fixture()
        raw = form["phase_1_raw_capture"]
        result = compute_coverage_status(raw)
        ossf_cells = [c for c in result["cells"] if c["name"] == "OSSF Scorecard"]
        assert len(ossf_cells) > 0
        assert ossf_cells[0]["status"] == "ok"

    def test_finding_count(self):
        """zustand has 6 findings: F0, F1, F2, F3, F4, F5"""
        form = load_fixture()
        findings = form.get("phase_4_structured_llm", {}).get("findings", {}).get("entries", [])
        assert len(findings) == 6, f"Expected 6 findings, got {len(findings)}"

    def test_finding_severities(self):
        """zustand: F0=Warning, F1=Warning, F2=OK, F3=OK, F4=OK, F5=Info"""
        form = load_fixture()
        findings = form.get("phase_4_structured_llm", {}).get("findings", {}).get("entries", [])
        if findings:
            sev_map = {f["id"]: f["severity"] for f in findings}
            assert sev_map.get("F0") == "Warning"
            assert sev_map.get("F1") == "Warning"
            assert sev_map.get("F2") == "OK"
            assert sev_map.get("F5") == "Info"

    def test_evidence_refs_on_warnings(self):
        """Non-OK findings must have evidence_refs"""
        form = load_fixture()
        findings = form.get("phase_4_structured_llm", {}).get("findings", {}).get("entries", [])
        for f in findings:
            if f.get("severity") not in ("OK",):
                refs = f.get("evidence_refs", [])
                assert len(refs) > 0, f"Finding {f['id']} (severity={f['severity']}) has no evidence_refs"

    def test_split_axis_is_deployment(self):
        """zustand splits on deployment axis"""
        form = load_fixture()
        split = form.get("phase_4_structured_llm", {}).get("split_axis_decision", {})
        assert split.get("should_split") is True
        assert split.get("axis") == "deployment"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
