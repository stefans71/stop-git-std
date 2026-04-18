#!/usr/bin/env python3
"""
Test suite for validate-scanner-report.py

Locks existing validator behavior against gold-standard scans (zustand)
and synthetic failure cases. Must pass before any validator changes.

Run: python3 -m pytest tests/test_validator.py -v
  or: python3 tests/test_validator.py
"""

import sys
import tempfile
from pathlib import Path

# Add docs/ to path so we can import the validator
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))

# Import validator functions directly
exec(open(REPO_ROOT / "docs" / "validate-scanner-report.py").read())


# ---------------------------------------------------------------------------
# Fixtures — paths to gold-standard test files
# ---------------------------------------------------------------------------

ZUSTAND_MD = REPO_ROOT / "docs" / "GitHub-Scanner-zustand.md"
ZUSTAND_HTML = REPO_ROOT / "docs" / "GitHub-Scanner-zustand.html"
TEMPLATE_HTML = REPO_ROOT / "docs" / "GitHub-Repo-Scan-Template.html"


# ---------------------------------------------------------------------------
# Helper: create a temp file with given content
# ---------------------------------------------------------------------------

def _tmp(content: str, suffix: str = ".md") -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


# ===========================================================================
# MARKDOWN MODE TESTS
# ===========================================================================

class TestMarkdownGoldStandard:
    """zustand.md must pass all checks — it's the gold standard."""

    def test_zustand_md_passes(self):
        errors, warnings = check_markdown(ZUSTAND_MD)
        assert errors == 0, f"Gold standard zustand.md has {errors} error(s)"

    def test_zustand_md_has_all_sections(self):
        raw = ZUSTAND_MD.read_text(encoding="utf-8")
        for section in ["Verdict", "Scorecard", "01", "02 ", "02A", "04", "05", "06", "07", "08"]:
            assert section.lower() in raw.lower() or any(
                s in raw for s in [f"## {section}", f"## 0{section}"]
            ), f"Missing section containing '{section}'"

    def test_zustand_md_has_scorecard_questions(self):
        raw = ZUSTAND_MD.read_text(encoding="utf-8").lower()
        assert "does anyone check the code?" in raw
        assert "do they fix problems quickly?" in raw
        assert "do they tell you about problems?" in raw
        assert "is it safe out of the box?" in raw

    def test_zustand_md_line_count(self):
        lines = ZUSTAND_MD.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 100, f"Only {len(lines)} lines"

    def test_zustand_md_has_numbered_sections(self):
        import re
        raw = ZUSTAND_MD.read_text(encoding="utf-8")
        numbered = re.findall(r"^## 0[0-9A-Za-z]+ ·", raw, re.MULTILINE)
        assert len(numbered) >= 7, f"Only {len(numbered)} numbered sections"

    def test_zustand_md_has_priority_evidence(self):
        raw = ZUSTAND_MD.read_text(encoding="utf-8")
        assert "★" in raw or "priority evidence" in raw.lower() or "START HERE" in raw


class TestMarkdownFailCases:
    """Synthetic MDs that MUST fail specific checks."""

    def test_trivial_md_fails_line_count(self):
        p = _tmp("# Short report\nNot enough content.\n")
        errors, _ = check_markdown(p)
        assert errors > 0
        p.unlink()

    def test_missing_sections_fails(self):
        # Has enough lines but missing required sections
        content = "# Some Report\n" + ("filler line\n" * 150)
        p = _tmp(content)
        errors, _ = check_markdown(p)
        assert errors > 0  # Missing Verdict, Scorecard, etc.
        p.unlink()

    def test_clean_verdict_with_warning_fails(self):
        content = (
            "# Security Investigation\n"
            "## Verdict: Clean\n"
            "## Trust Scorecard\n"
            "| Does anyone check the code? | Yes |\n"
            "| Do they fix problems quickly? | Yes |\n"
            "| Do they tell you about problems? | Yes |\n"
            "| Is it safe out of the box? | Yes |\n"
            "## 01 · What should I do?\n"
            "## 02 · What we found\n"
            "### F0 — Warning: Something bad\n"
            "## 02A · Executable file inventory\n"
            "## 04 · Timeline\n"
            "## 05 · Repo vitals\n"
            "## 06 · Investigation coverage\n"
            "## 07 · Evidence\n"
            "### ★ Priority evidence\n"
            "## 08 · How this scan works\n"
        ) + ("detail line\n" * 80)
        p = _tmp(content)
        errors, _ = check_markdown(p)
        assert errors > 0, "Clean verdict with Warning should fail coherence check"
        p.unlink()

    def test_clean_verdict_with_critical_fails(self):
        content = (
            "# Security Investigation\n"
            "## Verdict: Clean\n"
            "## Trust Scorecard\n"
            "| Does anyone check the code? | Yes |\n"
            "| Do they fix problems quickly? | Yes |\n"
            "| Do they tell you about problems? | Yes |\n"
            "| Is it safe out of the box? | Yes |\n"
            "## 01 · What should I do?\n"
            "## 02 · What we found\n"
            "### F0 — Critical: Major issue\n"
            "## 02A · Executable file inventory\n"
            "## 04 · Timeline\n"
            "## 05 · Repo vitals\n"
            "## 06 · Investigation coverage\n"
            "## 07 · Evidence\n"
            "### ★ Priority evidence\n"
            "## 08 · How this scan works\n"
        ) + ("detail line\n" * 80)
        p = _tmp(content)
        errors, _ = check_markdown(p)
        assert errors > 0, "Clean verdict with Critical should fail"
        p.unlink()

    def test_wrong_scorecard_questions_fails(self):
        content = (
            "# Security Investigation\n"
            "## Verdict\n"
            "Caution\n"
            "## Trust Scorecard\n"
            "| Does anyone check the code? | Yes |\n"
            "| Can you trust the maintainers? | Yes |\n"
            "| Is it actively maintained? | Yes |\n"
            "| Is it safe out of the box? | Yes |\n"
            "## 01 · What should I do?\n"
            "## 02 · What we found\n"
            "## 02A · Executable file inventory\n"
            "## 04 · Timeline\n"
            "## 05 · Repo vitals\n"
            "## 06 · Investigation coverage\n"
            "## 07 · Evidence\n"
            "### ★ Priority evidence\n"
            "## 08 · How this scan works\n"
        ) + ("detail line\n" * 80)
        p = _tmp(content)
        errors, _ = check_markdown(p)
        assert errors > 0, "Wrong scorecard questions should fail"
        p.unlink()

    def test_no_numbered_sections_fails(self):
        content = (
            "# Security Investigation\n"
            "## Verdict\n"
            "Caution\n"
            "## Trust Scorecard\n"
            "| Does anyone check the code? | Yes |\n"
            "| Do they fix problems quickly? | Yes |\n"
            "| Do they tell you about problems? | Yes |\n"
            "| Is it safe out of the box? | Yes |\n"
            "## What should I do?\n"  # No numbering!
            "## What we found\n"
            "## Executable file inventory\n"
            "## Timeline\n"
            "## Repo vitals\n"
            "## Investigation coverage\n"
            "## Evidence\n"
            "### ★ Priority evidence\n"
            "## How this scan works\n"
        ) + ("detail line\n" * 80)
        p = _tmp(content)
        errors, warnings = check_markdown(p)
        # Should at least warn about missing numbered sections
        assert errors > 0 or warnings > 0, "Unnumbered sections should warn or error"
        p.unlink()


# ===========================================================================
# HTML REPORT MODE TESTS
# ===========================================================================

class TestHtmlGoldStandard:
    """zustand.html must pass all checks."""

    def test_zustand_html_passes(self):
        errors, warnings = check(ZUSTAND_HTML, mode="report")
        assert errors == 0, f"Gold standard zustand.html has {errors} error(s)"


class TestHtmlFailCases:
    """Synthetic HTML that MUST fail specific checks."""

    def test_xss_script_tag_fails(self):
        html = "<html><body><script>alert(1)</script></body></html>"
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "Script tag injection should fail"
        p.unlink()

    def test_placeholder_remaining_fails(self):
        html = "<html><body><h1>{{REPO_NAME}}</h1></body></html>"
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "Remaining placeholder should fail"
        p.unlink()

    def test_example_marker_remaining_fails(self):
        html = "<html><body><!-- EXAMPLE-START: finding --><p>test</p><!-- EXAMPLE-END: finding --></body></html>"
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "Remaining EXAMPLE markers should fail"
        p.unlink()

    def test_inline_style_fails(self):
        html = '<html><body><p style="color: red;">Bad</p></body></html>'
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "Inline style should fail S8-1"
        p.unlink()

    def test_px_fontsize_fails(self):
        html = '<html><head><style>body { font-size: 16px; }</style></head><body>test</body></html>'
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "px font-size should fail S8-8"
        p.unlink()

    def test_event_handler_fails(self):
        html = '<html><body><img onerror="alert(1)" src="x"></body></html>'
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "Event handler should fail XSS check"
        p.unlink()

    def test_javascript_url_fails(self):
        html = '<html><body><a href="javascript:alert(1)">click</a></body></html>'
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "javascript: URL should fail"
        p.unlink()

    def test_iframe_fails(self):
        html = '<html><body><iframe src="https://evil.com"></iframe></body></html>'
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors > 0, "iframe should fail"
        p.unlink()

    def test_clean_html_passes(self):
        html = '<html><head><style>body { font-size: 1rem; }</style></head><body><h1>Report</h1><p>Content</p></body></html>'
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="report")
        assert errors == 0, f"Clean minimal HTML should pass, got {errors} error(s)"
        p.unlink()


# ===========================================================================
# TEMPLATE MODE TESTS
# ===========================================================================

class TestTemplateMode:
    """Template validation checks."""

    def test_template_passes(self):
        if TEMPLATE_HTML.exists():
            errors, _ = check(TEMPLATE_HTML, mode="template")
            assert errors == 0, f"Template has {errors} error(s)"

    def test_rendered_report_fails_as_template(self):
        """A rendered report (no placeholders) should fail template mode."""
        html = '<html><head><style>body { font-size: 1rem; }</style></head><body><h1>Report</h1></body></html>'
        p = _tmp(html, suffix=".html")
        errors, _ = check(p, mode="template")
        assert errors > 0, "Rendered report should fail template mode (no placeholders)"
        p.unlink()


# ===========================================================================
# XSS VECTOR DETECTION TESTS
# ===========================================================================

class TestXssDetection:
    """Specific XSS vector tests for find_xss_vectors()."""

    def test_adjustfont_script_whitelisted(self):
        html = '<script>function adjustFont(d){}</script>'
        findings = find_xss_vectors(html)
        assert len(findings) == 0, "adjustFont script should be whitelisted"

    def test_data_url_detected(self):
        html = '<img src="data:text/html,<script>alert(1)</script>">'
        findings = find_xss_vectors(html)
        assert len(findings) > 0, "data: URL should be detected"

    def test_embed_tag_detected(self):
        html = '<embed src="evil.swf">'
        findings = find_xss_vectors(html)
        assert len(findings) > 0, "embed tag should be detected"


# ===========================================================================
# CROSS-SCAN VALIDATION (all 9 backfilled MDs)
# ===========================================================================

class TestAllBackfilledScans:
    """Every backfilled V2.4 MD must pass the markdown validator."""

    SCAN_FILES = [
        "GitHub-Scanner-zustand.md",
        "GitHub-Scanner-fd.md",
        "GitHub-Scanner-Archon.md",
        "GitHub-Scanner-caveman.md",
        "GitHub-Scanner-gstack.md",
        "GitHub-Scanner-archon-board-review.md",
        "GitHub-Scanner-hermes-agent.md",
        "GitHub-Scanner-postiz-app.md",
        "GitHub-Scanner-open-lovable.md",
    ]

    def test_all_scans_pass_markdown_validation(self):
        docs_dir = REPO_ROOT / "docs"
        for filename in self.SCAN_FILES:
            path = docs_dir / filename
            if path.exists():
                errors, _ = check_markdown(path)
                assert errors == 0, f"{filename} has {errors} validation error(s)"


# ===========================================================================
# TAG BALANCE TESTS
# ===========================================================================

class TestTagBalance:
    """Tag balance checker edge cases."""

    def test_balanced_tags(self):
        checker = TagBalanceChecker()
        checker.feed("<div><p>hello</p></div>")
        assert len(checker.stack) == 0
        assert len(checker.errors) == 0

    def test_unclosed_tag(self):
        checker = TagBalanceChecker()
        checker.feed("<div><p>hello</div>")
        assert len(checker.errors) > 0 or len(checker.stack) > 0

    def test_void_tags_ok(self):
        checker = TagBalanceChecker()
        checker.feed("<br><hr><img><meta><link>")
        assert len(checker.stack) == 0
        assert len(checker.errors) == 0

    def test_self_closing_ok(self):
        checker = TagBalanceChecker()
        checker.feed("<br/><hr/><img/>")
        assert len(checker.stack) == 0


# ===========================================================================
# Run as standalone script
# ===========================================================================

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
