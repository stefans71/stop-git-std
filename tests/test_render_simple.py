#!/usr/bin/env python3
"""Phase 7 — Simple Report renderer tests.

Coverage per docs/simple-report-concept.md §9:
- Render against 3 representative bundles spanning verdict levels:
  ghostty (Caution OSS-default), Baileys (Critical genuine),
  skills (Caution with V13-3 missing_qualitative_context override).
- Minimal-bundle fallback (missing phase_5_prose_llm + what_this_means).
- HTML self-containment (no external <link>/<script>/<img src=http>).
- HTML/MD parity on scorecard sentences + finding titles + action body.

Run: python3 -m pytest tests/test_render_simple.py -v
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "render_simple", REPO_ROOT / "docs" / "render-simple.py"
)
_render = importlib.util.module_from_spec(_spec)
sys.modules["render_simple"] = _render
_spec.loader.exec_module(_render)

GHOSTTY = REPO_ROOT / "docs" / "scan-bundles" / "ghostty-dcc39dc.json"
BAILEYS = REPO_ROOT / "docs" / "scan-bundles" / "Baileys-8e5093c.json"
SKILLS = REPO_ROOT / "docs" / "scan-bundles" / "skills-b843cb5.json"


def _load(p: Path) -> dict:
    return json.loads(p.read_text())


# ─── Bundle smoke tests ─────────────────────────────────────────────
class TestRendersAgainstRepresentativeBundles:
    def test_ghostty_caution_path(self):
        form = _load(GHOSTTY)
        html = _render.render_html(form)
        md = _render.render_md(form)
        # Caution maps to amber/wait/caution
        assert 'verdict-banner caution' in html
        assert 'class="dot amber"' in html
        assert 'action-card wait' in html
        assert '⚠ Caution' in md
        # All 4 scorecard questions render
        for q in [
            "Does anyone check the code?",
            "Do they fix problems quickly?",
            "Do they tell you about problems?",
            "Is it safe out of the box?",
        ]:
            assert q in html
            assert q in md
        # Top 3 findings rendered (ghostty has 4; top 3 by severity)
        assert html.count('class="finding-card') == 3

    def test_baileys_critical_path(self):
        form = _load(BAILEYS)
        html = _render.render_html(form)
        md = _render.render_md(form)
        assert 'verdict-banner critical' in html
        assert 'class="dot red"' in html
        assert 'action-card stop' in html
        assert '✗ Critical' in md
        # F0 must be first finding (Critical severity)
        # The title contains "Reverse-engineered, unofficial WhatsApp"
        assert 'Reverse-engineered, unofficial WhatsApp' in html
        assert 'Reverse-engineered, unofficial WhatsApp' in md
        # Action body must come from F0 action_hint
        assert 'burner number' in html.lower()
        assert 'burner number' in md.lower()

    def test_skills_caution_with_override_path(self):
        """Entry 27 — first catalog scan with V13-3 missing_qualitative_context
        override at any n (V13-3 §2 reopened). Verifies that the Simple Report
        does not 'shout Critical' on a calibrated-Caution skill collection."""
        form = _load(SKILLS)
        html = _render.render_html(form)
        md = _render.render_md(form)
        assert 'verdict-banner caution' in html
        assert 'action-card wait' in html
        # Q1 LLM cell is red (solo + zero governance), Q3 LLM cell is red
        # (no SECURITY.md), so 2 red rows in scorecard expected
        assert html.count('sc-row red') == 2
        # But verdict overall is Caution
        assert '⚠ Caution' in md
        # First finding must be the solo-maintainer F0
        assert 'Solo-maintainer' in html
        assert 'Solo-maintainer' in md


# ─── Fallback tests ─────────────────────────────────────────────────
def _minimal_form() -> dict:
    """Synthetic minimal V1.2 form missing optional LLM-prose fields."""
    return {
        "schema_version": "1.2.0",
        "_meta": {"scan_completed_at": "2026-05-01T12:00:00+00:00"},
        "target": {"owner": "acme", "repo": "widget", "url": "https://github.com/acme/widget"},
        "phase_1_raw_capture": {
            "pre_flight": {"head_sha": "abc1234567890abcdef"},
            "repo_metadata": {
                "stargazer_count": 42,
                "license_spdx": "MIT",
                "primary_language": "Python",
            },
        },
        "phase_4_structured_llm": {
            "scorecard_cells": {
                "does_anyone_check_the_code":      {"color": "amber"},  # No short_answer
                "do_they_fix_problems_quickly":    {"color": "green"},
                "do_they_tell_you_about_problems": {"color": "red"},
                "is_it_safe_out_of_the_box":       {"color": "amber"},
            },
            "findings": {
                "entries": [
                    {"id": "F0", "severity": "Warning", "title": "T0",
                     "body": "Body 0.", "action_hint": "Be careful."},
                ]
            },
        },
        "phase_4b_computed": {"verdict": {"level": "Caution"}},
        # No phase_5_prose_llm — must trigger fallbacks
    }


class TestFallbacksOnMinimalBundle:
    def test_renders_html_without_phase_5_prose(self):
        form = _minimal_form()
        html = _render.render_html(form)
        # All 5 sections render
        assert "Trust scorecard" in html
        assert "Top concerns" in html
        assert "What should I do" in html
        # Verdict summary fallback synthesizes from level + top finding title
        assert "Caution" in html
        # Cell short_answer fallback: derives 'Partly'/'No'/'Yes' from color
        assert "Partly" in html or "No" in html or "Yes" in html
        # Action body falls back to action_hint
        assert "Be careful" in html

    def test_renders_md_without_phase_5_prose(self):
        form = _minimal_form()
        md = _render.render_md(form)
        assert "## Trust scorecard" in md
        assert "## Top concerns" in md
        assert "## What should I do?" in md
        assert "Be careful" in md

    def test_zero_findings_omits_top_concerns(self):
        form = _minimal_form()
        form["phase_4_structured_llm"]["findings"]["entries"] = []
        html = _render.render_html(form)
        md = _render.render_md(form)
        # Top concerns block omitted entirely when no findings
        assert "Top concerns" not in html
        assert "Top concerns" not in md
        # But action block still renders (verdict-driven static fallback)
        assert "What should I do" in html
        assert "What should I do" in md


# ─── Self-containment + parity ──────────────────────────────────────
class TestHtmlSelfContainment:
    def test_no_external_script_or_img(self):
        form = _load(GHOSTTY)
        html = _render.render_html(form)
        # No <script> tags at all
        assert "<script" not in html.lower()
        # No external <img src="http...">
        for m in re.finditer(r'<img\s+[^>]*src=["\']([^"\']+)["\']', html, re.I):
            src = m.group(1)
            assert not src.startswith("http"), f"External image found: {src}"

    def test_only_external_link_is_google_fonts(self):
        """Per concept doc §7: typography CDN is the only external dep allowed."""
        form = _load(GHOSTTY)
        html = _render.render_html(form)
        # Find all <link href> values
        links = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', html, re.I)
        for href in links:
            if href.startswith("http") or href.startswith("//"):
                assert "fonts.googleapis.com" in href or "fonts.gstatic.com" in href, \
                    f"Unexpected external link: {href}"

    def test_css_is_inlined(self):
        form = _load(GHOSTTY)
        html = _render.render_html(form)
        # Inline <style> block must be present + non-empty
        assert "<style>" in html
        # Sanity: CSS contains the design-system color tokens
        assert "--bg-void" in html
        assert "--cyan-glow" in html
        # No external stylesheet (other than the Google Fonts <link> with rel=stylesheet)
        stylesheets = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', html, re.I)
        # Only Google Fonts allowed
        for ss in stylesheets:
            assert "fonts.googleapis.com" in ss, f"Non-Google-Fonts stylesheet found: {ss}"


class TestHtmlMdParity:
    """HTML and MD must surface the same scorecard answers, finding titles,
    and action body — they are alternate views of the same data."""

    def _ctx(self, form):
        return _render.build_context(form)

    def test_scorecard_questions_match(self):
        form = _load(GHOSTTY)
        html = _render.render_html(form)
        md = _render.render_md(form)
        ctx = self._ctx(form)
        for row in ctx["scorecard_rows"]:
            # Question text must appear in both
            assert row["question"] in html
            assert row["question"] in md
            # Answer string must appear in both (full short_answer for parity)
            if row["answer"]:
                # MD shows the full answer string verbatim
                assert row["answer"] in md
                # HTML shows lead + rest assembled (or full answer in fallback)
                if row["lead"]:
                    assert row["lead"] in html
                    if row["rest"]:
                        assert row["rest"] in html
                else:
                    assert row["answer"] in html

    def test_finding_titles_match(self):
        for bundle in [GHOSTTY, BAILEYS, SKILLS]:
            form = _load(bundle)
            ctx = self._ctx(form)
            html = _render.render_html(form)
            md = _render.render_md(form)
            for f in ctx["top_findings"]:
                assert f["title"] in html, f"Title missing from HTML: {bundle.name} {f['title']}"
                assert f["title"] in md, f"Title missing from MD: {bundle.name} {f['title']}"

    def test_action_body_matches(self):
        for bundle in [GHOSTTY, BAILEYS, SKILLS]:
            form = _load(bundle)
            ctx = self._ctx(form)
            html = _render.render_html(form)
            md = _render.render_md(form)
            assert ctx["action_body"] in html
            assert ctx["action_body"] in md


# ─── Pure-function unit tests ───────────────────────────────────────
class TestSplitShortAnswer:
    def test_em_dash_split(self):
        assert _render.split_short_answer("Partly — ruleset + CODEOWNERS") == \
            ("Partly", "ruleset + CODEOWNERS")

    def test_hyphen_fallback(self):
        assert _render.split_short_answer("Yes - all good") == ("Yes", "all good")

    def test_no_separator_returns_whole_as_rest(self):
        assert _render.split_short_answer("plain text") == ("", "plain text")

    def test_empty_string(self):
        assert _render.split_short_answer("") == ("", "")


class TestPickTopFindings:
    def test_severity_sort_critical_first(self):
        block = {"entries": [
            {"id": "F0", "severity": "Warning"},
            {"id": "F1", "severity": "Critical"},
            {"id": "F2", "severity": "Info"},
            {"id": "F3", "severity": "Warning"},
        ]}
        result = _render.pick_top_findings(block, n=3)
        assert [f["id"] for f in result] == ["F1", "F0", "F3"]

    def test_input_order_tiebreak_within_severity(self):
        block = {"entries": [
            {"id": "F0", "severity": "Warning"},
            {"id": "F1", "severity": "Warning"},
            {"id": "F2", "severity": "Warning"},
        ]}
        result = _render.pick_top_findings(block, n=3)
        assert [f["id"] for f in result] == ["F0", "F1", "F2"]

    def test_handles_missing_findings(self):
        assert _render.pick_top_findings({}, n=3) == []
        assert _render.pick_top_findings({"entries": []}, n=3) == []


class TestFirstSentence:
    def test_simple_sentence(self):
        assert _render.first_sentence("Hello world. Second one.") == "Hello world."

    def test_below_max_chars(self):
        assert _render.first_sentence("short", max_chars=100) == "short"

    def test_truncate_when_no_sentence_boundary(self):
        result = _render.first_sentence("a" * 300, max_chars=100)
        assert result.endswith("…")
        assert len(result) <= 101


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
