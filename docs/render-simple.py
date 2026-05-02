#!/usr/bin/env python3
"""render-simple.py — Phase 7 Simple Report renderer.

Reads a V1.2 form.json bundle and emits a one-page polished HTML
+ a paste-ready MD companion. Spec: docs/simple-report-concept.md.

Usage:
    python3 docs/render-simple.py form.json --out-html report.html
    python3 docs/render-simple.py form.json --out-html report.html --out-md report.md
    python3 docs/render-simple.py form.json --out-html report.html --no-md
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / "templates-simple"
CSS_PATH = TEMPLATE_DIR / "simple-report.css"

# ─── Static lookups ─────────────────────────────────────────────────
QUESTION_LABELS = {
    "does_anyone_check_the_code":     "Does anyone check the code?",
    "do_they_fix_problems_quickly":   "Do they fix problems quickly?",
    "do_they_tell_you_about_problems": "Do they tell you about problems?",
    "is_it_safe_out_of_the_box":      "Is it safe out of the box?",
}
QUESTION_ORDER = list(QUESTION_LABELS.keys())

CELL_GLYPH = {"red": "✗", "amber": "⚠", "green": "✓"}
CELL_MD_GLYPH = {"red": "✗", "amber": "⚠", "green": "✓"}

VERDICT_BANNER_CLASS = {"Critical": "critical", "Caution": "caution", "Healthy": "clean"}
VERDICT_DOT_CLASS    = {"Critical": "red",      "Caution": "amber",   "Healthy": "green"}
VERDICT_COLOR_CLASS  = {"Critical": "bad",      "Caution": "warn",    "Healthy": "good"}
VERDICT_MD_GLYPH     = {"Critical": "✗",        "Caution": "⚠",       "Healthy": "✓"}
VERDICT_HEADLINES = {
    "Critical": "Don't install this — material risks identified.",
    "Caution":  "Install with these conditions in mind.",
    "Healthy":  "Safe to install — no material concerns identified.",
}
ACTION_CLASS    = {"Critical": "stop", "Caution": "wait",  "Healthy": "ok-action"}
ACTION_HEADLINE = {
    "Critical": "Don't install this.",
    "Caution":  "Install with these conditions.",
    "Healthy":  "Safe to install.",
}

SEVERITY_ORDER = {"Critical": 0, "Warning": 1, "Info": 2, "OK": 3}
SEVERITY_CLASS = {"Critical": "critical", "Warning": "warning", "Info": "info", "OK": "ok"}
SEVERITY_LABEL = {"Critical": "Critical", "Warning": "Warning", "Info": "Info", "OK": "OK"}


# ─── Helpers ────────────────────────────────────────────────────────
def short_sha(sha: str) -> str:
    return (sha or "")[:7]


def fmt_int(n) -> str:
    if isinstance(n, int):
        return f"{n:,}"
    return str(n) if n is not None else ""


def fmt_scan_date(meta: dict) -> str:
    raw = (meta or {}).get("scan_completed_at") or (meta or {}).get("scan_started_at")
    if not raw:
        return ""
    try:
        # ISO 8601 with optional Z or +HH:MM
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return raw[:10] if isinstance(raw, str) else ""


def split_short_answer(short_answer: str) -> tuple[str, str]:
    """Split 'Partly — ruleset-based...' into ('Partly', 'ruleset-based...').
    Falls back to ('', whole_string) if no ' — ' separator."""
    if not short_answer:
        return ("", "")
    for sep in (" — ", " - ", " – "):  # em-dash, hyphen, en-dash
        if sep in short_answer:
            head, _, tail = short_answer.partition(sep)
            return (head.strip(), tail.strip())
    return ("", short_answer)


def first_sentence(text: str, max_chars: int = 240) -> str:
    """Return the first sentence (or first max_chars) of a paragraph.
    A 'sentence' ends at '. ' or '! ' or '? ' followed by uppercase or paragraph end."""
    if not text:
        return ""
    text = text.strip()
    # Try sentence boundary
    for marker in [". ", "! ", "? "]:
        idx = text.find(marker)
        if 0 < idx < max_chars:
            return text[:idx + 1].strip()
    if len(text) <= max_chars:
        return text
    # Hard truncate at last word boundary before max_chars
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "…"


def pick_top_findings(findings_block: dict, n: int = 3) -> list:
    entries = (findings_block or {}).get("entries", []) or []
    indexed = list(enumerate(entries))
    indexed.sort(key=lambda pair: (SEVERITY_ORDER.get(pair[1].get("severity"), 99), pair[0]))
    return [pair[1] for pair in indexed[:n]]


# Area + status normalizers for the coverage one-liner. Keys are matched against
# the leading `<area>` token of each coverage_gaps entry; missing keys fall through
# to the raw token (with parenthetical aside stripped if it overflows).
_COVERAGE_AREA_SHORT = {
    "OSSF Scorecard": "OSSF",
    "Secrets-in-history (gitleaks)": "gitleaks",
    "Dependabot alert count": "Dependabot",
    "Dependabot alerts": "Dependabot",
    "Org rulesets": "org rulesets",
}
_COVERAGE_STATUS_SHORT = {
    "not_indexed": "not indexed",
    "not_available": "unavailable",
    "scope_restricted": "scope-restricted",
}


def _normalize_coverage_area(area: str) -> str:
    short = _COVERAGE_AREA_SHORT.get(area)
    if short:
        return short
    if len(area) > 28 and "(" in area:
        return area.split("(", 1)[0].strip()
    return area


def _normalize_coverage_status(status: str) -> str:
    s = (status or "").strip().rstrip(".,;:")
    return _COVERAGE_STATUS_SHORT.get(s, s)


def derive_coverage_oneliner(
    p4: dict, *, max_entries: int = 5, max_area_chars: int = 35, max_status_chars: int = 28,
) -> str:
    """Build a terse '<area> <status> · ...' one-liner from coverage_gaps.entries.

    Only consumes entries in the canonical harness/V13-style format
    `"<area> — <status>: <remediation>"` where `<area>` and `<status>` are short
    tokens. Free-prose entries (LLM-authored long sentences without the canonical
    structure) are skipped silently — the result is "" when no canonical entries
    exist, so the template omits the line entirely rather than rendering garbage.
    """
    entries = ((p4 or {}).get("coverage_gaps", {}) or {}).get("entries") or []
    parts = []
    for raw in entries:
        if not isinstance(raw, str) or not raw.strip():
            continue
        if " — " in raw:
            area, _, rest = raw.partition(" — ")
        elif " - " in raw:
            area, _, rest = raw.partition(" - ")
        else:
            continue  # No canonical separator — skip (likely free-prose entry).
        area_short = _normalize_coverage_area(area.strip())
        if not area_short or len(area_short) > max_area_chars:
            continue
        if ":" not in rest:
            continue  # No `<status>: <remediation>` shape — skip.
        status_token = rest.split(":", 1)[0].strip()
        if not status_token or len(status_token) > max_status_chars:
            continue
        status = _normalize_coverage_status(status_token)
        parts.append(f"{area_short} {status}")
    if not parts:
        return ""
    if len(parts) > max_entries:
        parts = parts[:max_entries]
    return " · ".join(parts)


# ─── Build template context ─────────────────────────────────────────
def build_context(form: dict) -> dict:
    target = form.get("target", {}) or {}
    meta = form.get("_meta", {}) or {}
    p1 = form.get("phase_1_raw_capture", {}) or {}
    repo_meta = p1.get("repo_metadata", {}) or {}
    pre_flight = p1.get("pre_flight", {}) or {}

    p4 = form.get("phase_4_structured_llm", {}) or {}
    p4b = form.get("phase_4b_computed", {}) or {}
    p5 = form.get("phase_5_prose_llm", {}) or {}

    # ─ Identity
    repo_owner = target.get("owner", "")
    repo_name = target.get("repo", "")
    repo_url = target.get("url") or f"https://github.com/{repo_owner}/{repo_name}"
    sha = pre_flight.get("head_sha") or ""

    # ─ Verdict
    verdict_obj = p4b.get("verdict", {}) or {}
    verdict_level = verdict_obj.get("level") or "Caution"
    if verdict_level not in VERDICT_BANNER_CLASS:
        verdict_level = "Caution"  # defensive

    # Verdict summary — fallback chain
    editorial = (p5.get("editorial_caption", {}) or {}).get("text") or ""
    if not editorial:
        # Synthesize from verdict + top finding title
        top = pick_top_findings(p4.get("findings", {}), n=1)
        top_title = top[0].get("title", "") if top else ""
        editorial = (
            f"{repo_owner}/{repo_name} is at {verdict_level}."
            + (f" {top_title}." if top_title else "")
        )

    # ─ Scorecard rows
    sc_cells = p4.get("scorecard_cells", {}) or {}
    scorecard_rows = []
    for q in QUESTION_ORDER:
        cell = sc_cells.get(q, {}) or {}
        color = cell.get("color") or "amber"
        if color not in CELL_GLYPH:
            color = "amber"
        sa = cell.get("short_answer") or cell.get("headline") or ""
        if not sa:
            # Fallback — derive from color
            sa = {"red": "No", "amber": "Partly", "green": "Yes"}.get(color, "Partly")
        lead, rest = split_short_answer(sa)
        scorecard_rows.append({
            "question": QUESTION_LABELS[q],
            "color_class": color,
            "glyph": CELL_GLYPH[color],
            "md_glyph": CELL_MD_GLYPH[color],
            "lead": lead,
            "rest": rest,
            "answer": sa,  # Full string for MD
        })

    # ─ Top findings
    top_findings_raw = pick_top_findings(p4.get("findings", {}), n=3)
    top_findings = []
    for f in top_findings_raw:
        sev = f.get("severity") or "Warning"
        if sev not in SEVERITY_CLASS:
            sev = "Warning"
        body = f.get("what_this_means") or f.get("body") or ""
        top_findings.append({
            "severity_class": SEVERITY_CLASS[sev],
            "severity_label": SEVERITY_LABEL[sev],
            "title": f.get("title") or "",
            "body": first_sentence(body, max_chars=300),
        })

    # ─ Action body — fallback chain:
    # 1. Top finding's action_hint (consumer-oriented; written AS action guidance)
    # 2. First sentence of per_finding_prose.entries[0].body_paragraphs[0]
    # 3. Verdict-level static text
    action_body = ""
    if top_findings_raw:
        ah = top_findings_raw[0].get("action_hint") or ""
        if ah:
            action_body = ah.strip()
    if not action_body:
        pf_entries = (p5.get("per_finding_prose", {}) or {}).get("entries", []) or []
        if pf_entries and pf_entries[0].get("body_paragraphs"):
            first_para = pf_entries[0]["body_paragraphs"][0] or ""
            action_body = first_sentence(first_para, max_chars=320)
    if not action_body:
        action_body = {
            "Critical": "Material risks were identified — find an alternative.",
            "Caution":  "There are concerns worth knowing before you install.",
            "Healthy":  "No material concerns were identified at this revision.",
        }[verdict_level]

    return {
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "short_sha": short_sha(sha),
        "scan_date": fmt_scan_date(meta),
        "stars": fmt_int(repo_meta.get("stargazer_count")),
        "license": repo_meta.get("license_spdx") or "",
        "language": repo_meta.get("primary_language") or "",
        "verdict_label": verdict_level,
        "verdict_md_glyph": VERDICT_MD_GLYPH[verdict_level],
        "verdict_banner_class": VERDICT_BANNER_CLASS[verdict_level],
        "verdict_dot_class": VERDICT_DOT_CLASS[verdict_level],
        "verdict_color_class": VERDICT_COLOR_CLASS[verdict_level],
        "verdict_headline": VERDICT_HEADLINES[verdict_level],
        "verdict_summary": editorial,
        "scorecard_rows": scorecard_rows,
        "top_findings": top_findings,
        "action_class": ACTION_CLASS[verdict_level],
        "action_headline": ACTION_HEADLINE[verdict_level],
        "action_body": action_body,
        "coverage_oneliner": derive_coverage_oneliner(p4),
    }


def render_html(form: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)),
                      trim_blocks=False, lstrip_blocks=False, keep_trailing_newline=True)
    template = env.get_template("simple-report.html.j2")
    ctx = build_context(form)
    ctx["css_inline"] = CSS_PATH.read_text()
    return template.render(**ctx)


def render_md(form: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)),
                      trim_blocks=False, lstrip_blocks=False, keep_trailing_newline=True)
    template = env.get_template("simple-report.md.j2")
    return template.render(**build_context(form))


def main():
    ap = argparse.ArgumentParser(description="Render a Simple Report from a V1.2 form.json bundle.")
    ap.add_argument("form_json", help="Path to V1.2 form.json bundle.")
    ap.add_argument("--out-html", required=True, help="Output path for HTML report.")
    ap.add_argument("--out-md", help="Output path for MD companion (default: derive from --out-html).")
    ap.add_argument("--no-md", action="store_true", help="Skip MD output.")
    args = ap.parse_args()

    form = json.loads(Path(args.form_json).read_text())

    out_html = Path(args.out_html)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(render_html(form))
    print(f"✓ wrote {out_html}")

    if not args.no_md:
        out_md = Path(args.out_md) if args.out_md else out_html.with_suffix(".md")
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_md(form))
        print(f"✓ wrote {out_md}")


if __name__ == "__main__":
    main()
