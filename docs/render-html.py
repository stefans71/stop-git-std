#!/usr/bin/env python3
"""render-html.py — Phase 7 HTML renderer (Jinja2-based).

Parallel emitter to render-md.py. Loads a filled investigation-form JSON,
embeds scanner-design-system.css verbatim into the <style> block, and
renders the HTML report via partials at docs/templates-html/.

Per board-approved plan Step F (docs/External-Board-Reviews/
041826-renderer-alignment/CONSOLIDATION.md), HTML and MD share the same
pre-computed form contract — no lazy compute inside the renderer, no new
findings emitted that are absent from MD (MD is canonical, HTML is
derived).

Usage:
    python3 docs/render-html.py tests/fixtures/zustand-form.json > report.html
    python3 docs/render-html.py --in form.json --out GitHub-Scanner-<repo>.html
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
TEMPLATE_DIR = ROOT / "templates-html"
CSS_PATH = ROOT / "scanner-design-system.css"


# Symbol / cell maps — same semantics as render-md.py so parity is automatic.
SEV_SYMBOL = {"Critical": "🚨", "Warning": "⚠", "Info": "ℹ", "OK": "✓"}
CELL_ICON = {"green": "✅", "amber": "⚠", "red": "❌"}
CELL_WORD = {"green": "Yes", "amber": "Partly", "red": "No"}
TONE_ICON = {"positive": "🟢", "neutral": "🟡", "negative": "🔴", "warn": "🟠"}

# Severity → HTML utility-class map for cards, chips, finding-status tags.
SEV_UTIL_CLASS = {"Critical": "val-bad", "Warning": "val-warn", "Info": "val-info", "OK": "val-good"}
CELL_DOT = {"green": "green", "amber": "amber", "red": "red"}

# Verdict level → banner/dot color. Fixture uses Clean/Caution/Critical per Phase 3 compute.
VERDICT_BANNER_CLASS = {"Clean": "clean", "Caution": "caution", "Critical": "critical"}
VERDICT_DOT_CLASS = {"Clean": "green", "Caution": "amber", "Critical": "red"}
VERDICT_H1_COLOR = {"Clean": "green", "Caution": "amber", "Critical": "red"}
VERDICT_UTIL_CLASS = {"Clean": "val-good", "Caution": "val-warn", "Critical": "val-bad"}


def short_sha(sha):
    return (sha or "")[:7]


def fmt_int(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


def repo_age_years(created_at, scan_date):
    if not created_at:
        return "unknown"
    created = datetime.fromisoformat(created_at[:10])
    scan = datetime.fromisoformat(scan_date[:10]) if scan_date else datetime.now(timezone.utc).replace(tzinfo=None)
    if isinstance(scan, datetime) and scan.tzinfo is not None:
        scan = scan.replace(tzinfo=None)
    years = (scan - created).days // 365
    return f"{years} years" if years != 1 else "1 year"


def _scan_date_of(form):
    raw = form.get("_meta", {}).get("scan_started_at") or form.get("_meta", {}).get("scan_completed_at") or ""
    return raw[:10] if raw else ""


def _load_css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def _build_env():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=select_autoescape(["html", "htm", "j2"]),
    )
    env.globals.update({
        "SEV_SYMBOL": SEV_SYMBOL,
        "CELL_ICON": CELL_ICON,
        "CELL_WORD": CELL_WORD,
        "TONE_ICON": TONE_ICON,
        "SEV_UTIL_CLASS": SEV_UTIL_CLASS,
        "CELL_DOT": CELL_DOT,
        "VERDICT_BANNER_CLASS": VERDICT_BANNER_CLASS,
        "VERDICT_DOT_CLASS": VERDICT_DOT_CLASS,
        "VERDICT_H1_COLOR": VERDICT_H1_COLOR,
        "VERDICT_UTIL_CLASS": VERDICT_UTIL_CLASS,
        "short_sha": short_sha,
        "fmt_int": fmt_int,
        "repo_age_years": repo_age_years,
    })
    return env


def render(form: dict) -> str:
    env = _build_env()
    template = env.get_template("scan-report.html.j2")
    return template.render(
        form=form,
        scan_date=_scan_date_of(form),
        css_content=_load_css(),
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render a filled investigation form JSON to HTML.")
    parser.add_argument("input", nargs="?", help="Path to investigation form JSON")
    parser.add_argument("--in", dest="input_flag", help="(alias) input path")
    parser.add_argument("--out", dest="output", help="Output path (defaults to stdout)")
    args = parser.parse_args(argv)

    input_path = args.input or args.input_flag
    if not input_path:
        parser.error("input path required")

    form = json.loads(Path(input_path).read_text(encoding="utf-8"))
    output = render(form)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
