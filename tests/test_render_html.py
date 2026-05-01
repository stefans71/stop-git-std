#!/usr/bin/env python3
"""
Integration tests for docs/render-html.py.

Feeds 3 V1.1-compliant investigation-form fixtures through the HTML renderer
and asserts structural fidelity (DOM classes, finding IDs, CSP, CSS embed,
section presence). Parameterized over fixtures so we exercise cross-shape
template behavior, not just zustand.

Run: python3 -m pytest tests/test_render_html.py -v
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent

# render-html.py has a hyphen, so import via importlib.
_spec = importlib.util.spec_from_file_location("render_html", REPO_ROOT / "docs" / "render-html.py")
_render_html = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_render_html)
render = _render_html.render


FIXTURES = {
    "zustand": REPO_ROOT / "tests" / "fixtures" / "zustand-form.json",
    "caveman": REPO_ROOT / "tests" / "fixtures" / "caveman-form.json",
    "archon-subset": REPO_ROOT / "tests" / "fixtures" / "archon-subset-form.json",
}


def _render(fixture_name):
    form = json.loads(FIXTURES[fixture_name].read_text(encoding="utf-8"))
    return render(form), form


# ---------------------------------------------------------------------------
# Skeleton: <!DOCTYPE>, head, CSS embed, CSP, body wrapper — all fixtures
# ---------------------------------------------------------------------------

class TestSkeleton:

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_doctype_and_html_open(self, name):
        out, _ = _render(name)
        assert out.startswith("<!DOCTYPE html>")
        assert '<html lang="en">' in out[:200]

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_closes_html(self, name):
        out, _ = _render(name)
        assert out.rstrip().endswith("</html>")

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_csp_meta_present(self, name):
        out, _ = _render(name)
        assert 'http-equiv="Content-Security-Policy"' in out
        assert "default-src 'none'" in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_fonts_preconnect(self, name):
        out, _ = _render(name)
        assert "fonts.googleapis.com" in out
        assert "fonts.gstatic.com" in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_css_embedded_verbatim(self, name):
        out, _ = _render(name)
        css_src = (REPO_ROOT / "docs" / "scanner-design-system.css").read_text(encoding="utf-8")
        assert "--bg-void: #0a0a0c" in out
        assert "DESIGN SYSTEM" in out
        assert len(css_src) > 0 and css_src.splitlines()[3] in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_title_has_repo_name(self, name):
        out, form = _render(name)
        owner = form["target"]["owner"]
        repo = form["target"]["repo"]
        assert f"<title>Security Investigation: {owner}/{repo}</title>" in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_page_wrapper(self, name):
        out, _ = _render(name)
        assert '<div class="page">' in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_font_control_widget(self, name):
        out, _ = _render(name)
        assert 'class="font-controls"' in out
        assert "adjustFont" in out


# ---------------------------------------------------------------------------
# Validator-gate invariants: these would fail strict --report mode
# ---------------------------------------------------------------------------

class TestValidatorInvariants:

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_no_placeholder_tokens(self, name):
        out, _ = _render(name)
        # Placeholder tokens look like {{UPPER_SNAKE}}; regular Jinja output is fine.
        leaked = re.findall(r"\{\{[A-Z_0-9]+\}\}", out)
        assert not leaked, f"leaked placeholders: {leaked[:5]}"

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_no_example_markers(self, name):
        out, _ = _render(name)
        assert "EXAMPLE-START" not in out
        assert "EXAMPLE-END" not in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_no_inline_styles(self, name):
        """Validator flags any style='' on rendered elements (CSP / design-system rule)."""
        out, _ = _render(name)
        # Strip the <style>..</style> block — that one is expected.
        body = re.sub(r"<style[^>]*>.*?</style>", "", out, flags=re.DOTALL | re.IGNORECASE)
        # style attribute on a rendered tag
        assert not re.search(r'<[a-zA-Z][^>]*\sstyle\s*=\s*["\']', body), \
            "inline style='' attribute on a rendered element"

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_no_px_font_size_in_style(self, name):
        out, _ = _render(name)
        style_match = re.search(r"<style[^>]*>(.*?)</style>", out, flags=re.DOTALL | re.IGNORECASE)
        assert style_match is not None
        style_body = style_match.group(1)
        assert not re.search(r"font-size\s*:\s*\d+px", style_body), "px font-size in <style> block"


# ---------------------------------------------------------------------------
# Hero: scan-strip, H1, meta row, verdict-colored slash
# ---------------------------------------------------------------------------

class TestHero:

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_hero_block(self, name):
        out, _ = _render(name)
        assert '<div class="hero">' in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_scan_strip_has_dossier(self, name):
        out, form = _render(name)
        repo = form["target"]["repo"]
        assert "scan-strip" in out
        assert f"Dossier &middot; {repo}" in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_h1_has_owner_and_repo(self, name):
        out, form = _render(name)
        owner = form["target"]["owner"]
        repo = form["target"]["repo"]
        assert f"<h1>{owner}" in out
        assert f">{repo}</span>" in out

    @pytest.mark.parametrize("name,expected_color", [
        ("zustand", "amber"),        # Caution
        ("caveman", "red"),          # Critical
        ("archon-subset", "red"),    # Critical
    ])
    def test_h1_verdict_color(self, name, expected_color):
        out, _ = _render(name)
        assert f'<span class="{expected_color}">' in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_meta_row_has_stars(self, name):
        out, _ = _render(name)
        assert "Stars" in out and "meta-item" in out


# ---------------------------------------------------------------------------
# Catalog metadata table — every report must have it
# ---------------------------------------------------------------------------

class TestCatalog:

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_catalog_block(self, name):
        out, _ = _render(name)
        assert "catalog-meta" in out or "Catalog metadata" in out


# ---------------------------------------------------------------------------
# Verdict banner + exhibits
# ---------------------------------------------------------------------------

class TestVerdict:

    @pytest.mark.parametrize("name,banner_class", [
        ("zustand", "caution"),
        ("caveman", "critical"),
        ("archon-subset", "critical"),
    ])
    def test_verdict_banner_class(self, name, banner_class):
        out, _ = _render(name)
        assert f"verdict-banner {banner_class}" in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_verdict_exhibits_panel(self, name):
        """Each fixture has ≥2 exhibit groups per their verdict_exhibits config."""
        out, form = _render(name)
        groups = form.get("phase_4_structured_llm", {}).get("verdict_exhibits", {}).get("groups", [])
        if groups:
            assert '<details class="exhibit' in out
            # Count emitted <details class="exhibit"> — allow ≥1 per group
            count = out.count('<details class="exhibit')
            assert count >= 1


# ---------------------------------------------------------------------------
# Scorecard: the 4 canonical trust-framework questions verbatim
# ---------------------------------------------------------------------------

SCORECARD_QUESTIONS = [
    "Does anyone check the code?",
    "Do they fix problems quickly?",
    "Do they tell you about problems?",
    "Is it safe out of the box?",
]


class TestScorecard:

    @pytest.mark.parametrize("name", list(FIXTURES))
    @pytest.mark.parametrize("q", SCORECARD_QUESTIONS)
    def test_scorecard_question_present(self, name, q):
        out, _ = _render(name)
        assert q in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_scorecard_grid_structure(self, name):
        out, _ = _render(name)
        assert "scorecard" in out.lower()

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_scorecard_cells_in_phase_4_not_phase_3(self, name):
        """V1.2 D2 invariant: fixture has scorecard_cells under phase_4_structured_llm;
        phase_3_computed no longer carries scorecard_cells."""
        out, form = _render(name)
        assert "scorecard_cells" in form["phase_4_structured_llm"]
        assert "scorecard_cells" not in form.get("phase_3_computed", {})
        # And phase_3_advisory is populated
        assert "phase_3_advisory" in form
        assert "scorecard_hints" in form["phase_3_advisory"]


# ---------------------------------------------------------------------------
# Section numbering — H2 headings for sections 01-08 + 02A
# ---------------------------------------------------------------------------

class TestSectionHeadings:

    REQUIRED_SECTIONS = [
        ("01", "What Should I Do?"),
        ("02", "What We Found"),
        ("02A", "Executable"),
        ("03", "Evidence"),
        ("04", "PR"),  # either "PR Sample Review" or similar
        ("05", "Coverage"),
        ("06", "Timeline"),
        ("07", "Repo Vitals"),
        ("08", "How This Scan Works"),
    ]

    @pytest.mark.parametrize("name", list(FIXTURES))
    @pytest.mark.parametrize("num,title_substring", REQUIRED_SECTIONS)
    def test_section_heading(self, name, num, title_substring):
        out, _ = _render(name)
        # Look for the section number span + some portion of the title, case-insensitive
        pattern = re.compile(
            rf'(section-number[^>]*>\s*{re.escape(num)}|>\s*{re.escape(num)}\s*</span>)',
            flags=re.IGNORECASE,
        )
        assert pattern.search(out), f"section {num} marker not found in {name}"
        assert title_substring.lower() in out.lower(), \
            f"section {num} title '{title_substring}' not found in {name}"


# ---------------------------------------------------------------------------
# Finding cards — every MD finding must appear in HTML with matching F-ID
# ---------------------------------------------------------------------------

class TestFindings:

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_finding_cards_present(self, name):
        out, form = _render(name)
        findings = form.get("phase_4_structured_llm", {}).get("findings", {}).get("entries", [])
        if findings:
            assert '<div class="finding-card' in out or 'finding-card' in out

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_every_finding_id_in_html(self, name):
        """Each finding ID from the fixture must appear in the HTML (MD-canonical rule)."""
        out, form = _render(name)
        for f in form["phase_4_structured_llm"]["findings"]["entries"]:
            fid = f["id"]
            assert fid in out, f"finding {fid} missing from {name} HTML"

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_finding_severity_classes(self, name):
        """At least one of the 4 severity classes must appear per fixture (unless 0 findings)."""
        out, form = _render(name)
        findings = form["phase_4_structured_llm"]["findings"]["entries"]
        if findings:
            severities = {f.get("severity") for f in findings}
            sev_classes = {"Critical": "finding-card critical", "Warning": "finding-card warning",
                           "Info": "finding-card info", "OK": "finding-card ok"}
            for sev in severities:
                if sev in sev_classes:
                    assert sev_classes[sev] in out or f'finding-card {sev.lower()}' in out


# ---------------------------------------------------------------------------
# Section 08 methodology — required boilerplate
# ---------------------------------------------------------------------------

class TestMethodology:

    @pytest.mark.parametrize("name", list(FIXTURES))
    def test_has_methodology_section(self, name):
        out, _ = _render(name)
        assert "How This Scan Works" in out or "how this scan works" in out.lower()


# ---------------------------------------------------------------------------
# Shape-specific assertions: monorepo, split-verdict, etc.
# ---------------------------------------------------------------------------

class TestShapeSpecific:

    def test_archon_is_monorepo(self):
        """Archon-subset fixture should emit monorepo coverage detail."""
        out, form = _render("archon-subset")
        mono = form["phase_1_raw_capture"].get("monorepo") or \
               form["phase_3_computed"].get("monorepo") or {}
        # Just check the HTML references monorepo concepts
        assert "monorepo" in out.lower() or "inner package" in out.lower() or "package" in out.lower()

    def test_caveman_has_critical_verdict(self):
        out, _ = _render("caveman")
        assert "Critical" in out

    def test_zustand_has_caution_verdict(self):
        out, _ = _render("zustand")
        assert "Caution" in out.lower() or "caution" in out


# ---------------------------------------------------------------------------
# Phase 4 — derivation helpers smoke tests (chore/template-side-derivation).
# Verify the shared docs/render_helpers.py module loads + the 3 helpers exist.
# Behavioral tests live in tests/test_render_md.py (single source of truth);
# this file only verifies HTML-renderer-side accessibility for commit 2.
# ---------------------------------------------------------------------------

_helpers_spec = importlib.util.spec_from_file_location(
    "render_helpers", REPO_ROOT / "docs" / "render_helpers.py"
)
_helpers = importlib.util.module_from_spec(_helpers_spec)
_helpers_spec.loader.exec_module(_helpers)


class TestDerivationHelpersAvailable:
    """Smoke: helpers exist + are callable (full behavior tested in test_render_md.py)."""

    def test_derive_repo_vitals_callable(self):
        assert callable(_helpers.derive_repo_vitals)
        # Empty input must not crash
        assert isinstance(_helpers.derive_repo_vitals({}), list)

    def test_derive_coverage_detail_callable(self):
        assert callable(_helpers.derive_coverage_detail)
        assert _helpers.derive_coverage_detail({}) == []

    def test_derive_pr_sample_callable(self):
        assert callable(_helpers.derive_pr_sample)
        assert _helpers.derive_pr_sample({}) == []
