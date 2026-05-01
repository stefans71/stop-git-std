#!/usr/bin/env python3
"""render-md.py — Phase 7 Markdown renderer (Jinja2-based).

Thin glue layer between a filled investigation form JSON and the Markdown
templates at docs/templates/. Per board-approved plan (Option C, Step B,
docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md),
formatting logic lives in templates; this file only loads data, exposes
helpers, and renders.

Usage:
    python3 docs/render-md.py tests/fixtures/zustand-form.json > report.md
    python3 docs/render-md.py --in form.json --out GitHub-Scanner-<repo>.md
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure sibling render_helpers.py is importable when this script runs
# directly (cwd is repo root, not docs/).
sys.path.insert(0, str(Path(__file__).parent))

from jinja2 import Environment, FileSystemLoader

from render_helpers import (
    derive_coverage_detail,
    derive_pr_sample,
    derive_repo_vitals,
)

TEMPLATE_DIR = Path(__file__).parent / "templates"

# Severity / color / tone maps — exposed to templates as globals.
SEV_SYMBOL = {"Critical": "🚨", "Warning": "⚠", "Info": "ℹ", "OK": "✓"}
CELL_ICON = {"green": "✅", "amber": "⚠", "red": "❌"}
CELL_WORD = {"green": "Yes", "amber": "Partly", "red": "No"}
TONE_ICON = {"positive": "🟢", "neutral": "🟡", "negative": "🔴", "warn": "🟠"}


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


def _build_env():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,  # preserve trailing blank lines at end of each partial
        autoescape=False,  # output is Markdown, not HTML
    )
    env.globals.update({
        "SEV_SYMBOL": SEV_SYMBOL,
        "CELL_ICON": CELL_ICON,
        "CELL_WORD": CELL_WORD,
        "TONE_ICON": TONE_ICON,
        "short_sha": short_sha,
        "fmt_int": fmt_int,
        "repo_age_years": repo_age_years,
        # Phase 4 derivation helpers — templates fall back to these when
        # phase_4_structured_llm doesn't supply rows.
        "derive_repo_vitals": derive_repo_vitals,
        "derive_coverage_detail": derive_coverage_detail,
        "derive_pr_sample": derive_pr_sample,
    })
    return env


def render(form: dict) -> str:
    env = _build_env()
    template = env.get_template("scan-report.md.j2")
    output = template.render(form=form, scan_date=_scan_date_of(form))
    # Collapse 2+ consecutive blank lines → 1 blank line (markdown section spacing).
    lines = output.splitlines()
    cleaned = []
    blank_run = 0
    for line in lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 1:
                cleaned.append(line)
        else:
            blank_run = 0
            cleaned.append(line)
    return "\n".join(cleaned).rstrip() + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render a filled investigation form JSON to Markdown.")
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
