#!/usr/bin/env python3
"""Tests for docs/compare-severity-distribution.py (D-6 automation).

Covers the 2 extraction formats (section-header primary + summary-bullet
fallback), JSON-form.json extraction, the compare() diff logic, and the
main() exit-code contract.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "_compare_severity",
    REPO / "docs" / "compare-severity-distribution.py",
)
compare_mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare_mod)


# ===========================================================================
# Extraction — MD (section-header form)
# ===========================================================================


def test_extract_md_section_header_format(tmp_path):
    md = tmp_path / "report.md"
    md.write_text(
        "# Some scan\n\n"
        "### F0 — Critical · Ongoing — RCE on install path\n"
        "body body body\n\n"
        "### F1 — Warning · Structural — governance gap\n"
        "### F2 — Info · Hygiene — minor doc gap\n"
        "### F3 — OK — all good\n"
    )
    out = compare_mod.extract_from_markdown(md)
    assert out == {"F0": "Critical", "F1": "Warning", "F2": "Info", "F3": "OK"}


def test_extract_md_tolerates_em_dash_and_hyphen(tmp_path):
    md = tmp_path / "report.md"
    md.write_text(
        "### F0 — Warning · a\n"
        "### F1 - Warning · b\n"  # ASCII hyphen instead of em dash
    )
    out = compare_mod.extract_from_markdown(md)
    assert out == {"F0": "Warning", "F1": "Warning"}


# ===========================================================================
# Extraction — MD (summary-bullet fallback, zustand-v3 shape)
# ===========================================================================


def test_extract_md_summary_bullet_format(tmp_path):
    """zustand-v3 entry 10 shape: summary bullets instead of section headers."""
    md = tmp_path / "report.md"
    md.write_text(
        "# Zustand v3\n\n"
        "Findings summary:\n"
        "- **Warning:** No branch protection on default branch (F0)\n"
        "- **Info:** No SECURITY.md (F1)\n"
        "- **Info:** Four workflows lack token permissions (F2)\n"
        "- **Info:** Docs workflow uses unpinned ref (F3)\n"
    )
    out = compare_mod.extract_from_markdown(md)
    assert out == {"F0": "Warning", "F1": "Info", "F2": "Info", "F3": "Info"}


def test_extract_md_prefers_section_header_when_both_exist(tmp_path):
    """If section headers exist, bullet fallback is NOT invoked even if bullets are present."""
    md = tmp_path / "report.md"
    md.write_text(
        "- **Warning:** summary line (F0)\n"
        "\n### F0 — Info · different — body\n"
    )
    out = compare_mod.extract_from_markdown(md)
    # Section-header takes precedence; bullet form is fallback-only.
    assert out == {"F0": "Info"}


def test_extract_md_duplicate_raises(tmp_path):
    md = tmp_path / "report.md"
    md.write_text(
        "### F0 — Warning · first\n"
        "### F0 — Info · second\n"
    )
    with pytest.raises(ValueError, match="duplicate finding id F0"):
        compare_mod.extract_from_markdown(md)


# ===========================================================================
# Extraction — form.json
# ===========================================================================


def test_extract_json_form_schema(tmp_path):
    form = tmp_path / "form.json"
    form.write_text(json.dumps({
        "phase_4_structured_llm": {
            "findings": {"entries": [
                {"id": "F0", "severity": "Critical", "title": "..."},
                {"id": "F1", "severity": "Warning", "title": "..."},
                {"id": "F2", "severity": "OK", "title": "..."},
            ]},
        },
    }))
    out = compare_mod.extract_from_form_json(form)
    assert out == {"F0": "Critical", "F1": "Warning", "F2": "OK"}


def test_extract_json_unknown_severity_raises(tmp_path):
    form = tmp_path / "form.json"
    form.write_text(json.dumps({
        "phase_4_structured_llm": {
            "findings": {"entries": [
                {"id": "F0", "severity": "Catastrophic"},
            ]},
        },
    }))
    with pytest.raises(ValueError, match="unknown severity"):
        compare_mod.extract_from_form_json(form)


def test_extract_dispatches_by_extension(tmp_path):
    md = tmp_path / "a.md"
    md.write_text("### F0 — OK — fine\n")
    js = tmp_path / "b.json"
    js.write_text(json.dumps({
        "phase_4_structured_llm": {"findings": {"entries": [
            {"id": "F0", "severity": "OK"}
        ]}}
    }))
    assert compare_mod.extract(md) == {"F0": "OK"}
    assert compare_mod.extract(js) == {"F0": "OK"}


def test_extract_unknown_extension_raises(tmp_path):
    p = tmp_path / "report.html"
    p.write_text("<html>...</html>")
    with pytest.raises(ValueError, match="unsupported extension"):
        compare_mod.extract(p)


# ===========================================================================
# compare() diff logic
# ===========================================================================


def test_compare_all_match():
    v24 = {"F0": "Critical", "F1": "Warning"}
    v25 = {"F0": "Critical", "F1": "Warning"}
    rows, summary = compare_mod.compare(v24, v25)
    assert summary == {"total": 2, "matches": 2, "mismatches": 0,
                       "missing_in_v25": 0, "missing_in_v24": 0}
    assert all(row[3] for row in rows)  # all matches


def test_compare_detects_severity_mismatch():
    v24 = {"F0": "Warning"}
    v25 = {"F0": "Info"}  # downgrade
    rows, summary = compare_mod.compare(v24, v25)
    assert summary["mismatches"] == 1
    assert rows[0] == ("F0", "Warning", "Info", False)


def test_compare_detects_missing_in_v25():
    v24 = {"F0": "Warning", "F1": "Info"}
    v25 = {"F0": "Warning"}
    rows, summary = compare_mod.compare(v24, v25)
    assert summary["missing_in_v25"] == 1
    assert summary["mismatches"] == 0
    # F1 row: V2.4 populated, V2.5 missing
    f1_row = [r for r in rows if r[0] == "F1"][0]
    assert f1_row == ("F1", "Info", "—", False)


def test_compare_detects_missing_in_v24():
    v24 = {"F0": "Warning"}
    v25 = {"F0": "Warning", "F5": "Info"}  # extra finding in V2.5
    rows, summary = compare_mod.compare(v24, v25)
    assert summary["missing_in_v24"] == 1
    assert summary["mismatches"] == 0


def test_compare_sorts_by_numeric_fid():
    """F10 should sort after F2, not after F1 (lexicographic would put F10 before F2)."""
    v24 = {"F0": "OK", "F10": "OK", "F2": "OK", "F1": "OK"}
    v25 = {"F0": "OK", "F10": "OK", "F2": "OK", "F1": "OK"}
    rows, _ = compare_mod.compare(v24, v25)
    ids = [r[0] for r in rows]
    assert ids == ["F0", "F1", "F2", "F10"]


# ===========================================================================
# Rendering + end-to-end
# ===========================================================================


def test_render_table_pass_message():
    rows = [("F0", "Warning", "Warning", True)]
    summary = {"total": 1, "matches": 1, "mismatches": 0,
               "missing_in_v25": 0, "missing_in_v24": 0}
    report = compare_mod.render_table(rows, summary, "testing", Path("a.md"), Path("b.md"))
    assert "GATE 6.2 PASS" in report
    assert "1/1 match" in report


def test_render_table_fail_message():
    rows = [("F0", "Warning", "Info", False)]
    summary = {"total": 1, "matches": 0, "mismatches": 1,
               "missing_in_v25": 0, "missing_in_v24": 0}
    report = compare_mod.render_table(rows, summary, "testing", Path("a.md"), Path("b.md"))
    assert "GATE 6.2 FAIL" in report
    assert "1 mismatch" in report


def test_main_exits_0_on_match(tmp_path, capsys):
    v24 = tmp_path / "v24.md"
    v24.write_text("### F0 — Warning · a\n")
    v25 = tmp_path / "v25.md"
    v25.write_text("### F0 — Warning · b\n")
    rc = compare_mod.main(["--v24", str(v24), "--v25", str(v25)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "GATE 6.2 PASS" in out


def test_main_exits_1_on_mismatch(tmp_path, capsys):
    v24 = tmp_path / "v24.md"
    v24.write_text("### F0 — Warning · a\n")
    v25 = tmp_path / "v25.md"
    v25.write_text("### F0 — Info · a\n")
    rc = compare_mod.main(["--v24", str(v24), "--v25", str(v25)])
    assert rc == 1


def test_main_exits_2_on_missing_file(tmp_path):
    v24 = tmp_path / "v24.md"  # does not exist
    v25 = tmp_path / "v25.md"
    v25.write_text("### F0 — OK — fine\n")
    rc = compare_mod.main(["--v24", str(v24), "--v25", str(v25)])
    assert rc == 2


def test_main_writes_out_file(tmp_path):
    v24 = tmp_path / "v24.md"
    v24.write_text("### F0 — Warning · a\n")
    v25 = tmp_path / "v25.md"
    v25.write_text("### F0 — Warning · b\n")
    out = tmp_path / "mapping.md"
    rc = compare_mod.main(["--v24", str(v24), "--v25", str(v25), "--out", str(out)])
    assert rc == 0
    assert out.exists()
    assert "GATE 6.2 PASS" in out.read_text()


# ===========================================================================
# Integration: Step G pairs (real data) — should all PASS
# ===========================================================================


@pytest.mark.parametrize("v24_file,v25_file,expected_count", [
    ("GitHub-Scanner-zustand-v3.md", "GitHub-Scanner-zustand-v3-v25preview.md", 4),
    ("GitHub-Scanner-caveman.md",    "GitHub-Scanner-caveman-v25preview.md",    5),
    ("GitHub-Scanner-Archon.md",     "GitHub-Scanner-Archon-v25preview.md",     9),
])
def test_step_g_pairs_pass_gate_6_2(v24_file, v25_file, expected_count):
    """The 3 Step G validation pairs should all pass automated gate 6.2."""
    v24 = REPO / "docs" / v24_file
    v25 = REPO / "docs" / v25_file
    if not v24.exists() or not v25.exists():
        pytest.skip(f"Step G artifact missing: {v24.name} or {v25.name}")
    rc = compare_mod.main(["--v24", str(v24), "--v25", str(v25)])
    # Either passes (exit 0) or we get a missing-file exit (2); gate 6.2 pairs
    # landed in Step G and should match by construction.
    assert rc == 0, f"Step G pair {v24_file} vs {v25_file} should pass gate 6.2"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
