#!/usr/bin/env python3
"""render-md.py — Phase 7 Markdown renderer.

Consumes a filled investigation form JSON (validated against scan-schema.json)
and produces a canonical scan report in Markdown. MD is the canonical output;
render-html.py derives HTML from the same JSON (not from this MD).

Usage:
    python3 docs/render-md.py tests/fixtures/zustand-form.json > report.md
    python3 docs/render-md.py --in form.json --out GitHub-Scanner-<repo>.md
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Severity → leading symbol used in section summaries and finding prefixes.
SEV_SYMBOL = {"Critical": "🚨", "Warning": "⚠", "Info": "ℹ", "OK": "✓"}
# Scorecard cell color → table icon used in the Trust Scorecard question table.
CELL_ICON = {"green": "✅", "amber": "⚠", "red": "❌"}
# Scorecard cell color → short answer word for the scorecard icon column.
CELL_WORD = {"green": "Yes", "amber": "Partly", "red": "No"}


def render(form: dict) -> str:
    sections = [
        _hero(form),
        _catalog(form),
        _verdict(form),
        _scorecard(form),
        _section_01(form),
        _section_02(form),
        _section_02a(form),
        _section_03(form),
        _section_04(form),
        _section_05(form),
        _section_06(form),
        _section_07(form),
        _section_08(form),
        _footer(form),
    ]
    return "\n\n".join(s.rstrip() for s in sections if s) + "\n"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _fmt_int(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


def _short_sha(sha: str) -> str:
    return (sha or "")[:7]


def _repo_age_years(created_at: str, scan_date: str) -> str:
    if not created_at:
        return "unknown"
    created = datetime.fromisoformat(created_at[:10])
    scan = datetime.fromisoformat(scan_date[:10]) if scan_date else datetime.now(timezone.utc).replace(tzinfo=None)
    if isinstance(scan, datetime) and scan.tzinfo is not None:
        scan = scan.replace(tzinfo=None)
    years = (scan - created).days // 365
    return f"{years} years" if years != 1 else "1 year"


def _sev_label(sev: str) -> str:
    return sev or "OK"


def _scan_date(form) -> str:
    raw = form.get("_meta", {}).get("scan_started_at") or form.get("_meta", {}).get("scan_completed_at") or ""
    return raw[:10] if raw else "unknown"


# ---------------------------------------------------------------------------
# Hero: title, caption, meta line
# ---------------------------------------------------------------------------

def _hero(form) -> str:
    target = form["target"]
    meta = form.get("_meta", {})
    repo_meta = form["phase_1_raw_capture"]["repo_metadata"]
    head_sha = form["phase_1_raw_capture"]["pre_flight"].get("head_sha", "")
    releases = form["phase_1_raw_capture"].get("releases", {}).get("entries", [])
    latest_tag = releases[0]["tag"] if releases else ""
    scan_date = _scan_date(form)
    caption = form.get("phase_5_prose_llm", {}).get("editorial_caption", {}).get("text", "")
    age = _repo_age_years(repo_meta.get("created_at", ""), scan_date)
    stars = _fmt_int(repo_meta.get("stargazer_count", 0))
    license_ = repo_meta.get("license_spdx") or "None"

    parts = [
        f"# Security Investigation: {target['owner']}/{target['repo']}",
        "",
        f"**Investigated:** {scan_date} | **Applies to:** main @ `{head_sha}`"
        + (f" · {latest_tag}" if latest_tag else "")
        + f" | **Repo age:** {age} | **Stars:** {stars} | **License:** {license_}",
    ]
    if caption:
        parts += ["", f"> {caption}"]
    parts += ["", "---"]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Catalog metadata
# ---------------------------------------------------------------------------

def _catalog(form) -> str:
    target = form["target"]
    catalog = form["phase_4_structured_llm"].get("catalog_metadata", {}) or {}
    repo_meta = form["phase_1_raw_capture"]["repo_metadata"]
    head_sha = form["phase_1_raw_capture"]["pre_flight"].get("head_sha", "")
    releases = form["phase_1_raw_capture"].get("releases", {}).get("entries", [])
    latest_tag = releases[0]["tag"] if releases else "untagged"
    verdict = form.get("phase_4b_computed", {}).get("verdict", {}).get("level", "Unknown")
    split = form["phase_4_structured_llm"].get("split_axis_decision", {}).get("should_split", False)
    verdict_label = f"**{verdict}**" + (" (split — see below)" if split else "")
    scanner_ver = form.get("_meta", {}).get("scanner_version", "unknown")
    scan_date = _scan_date(form)

    rows = [
        ("Report file", f"`GitHub-Scanner-{target['repo']}.md` (+ `.html` companion)"),
        ("Repo", f"[github.com/{target['owner']}/{target['repo']}]({target['url']})"),
        ("Short description", catalog.get("short_description", repo_meta.get("description", ""))),
        ("Category", f"`{catalog.get('category', '')}`"),
        ("Subcategory", f"`{catalog.get('subcategory', '')}`"),
        ("Language", repo_meta.get("primary_language", "")),
        ("License", repo_meta.get("license_spdx", "None")),
        ("Target user", catalog.get("target_user", "")),
        ("Verdict", verdict_label),
        ("Scanned revision", f"`main @ {_short_sha(head_sha)}` (release tag `{latest_tag}`)"),
        ("Commit pinned", f"`{head_sha}`"),
        ("Scanner version", f"`{scanner_ver}`"),
        ("Scan date", f"`{scan_date}`"),
    ]
    prior = catalog.get("prior_scan_note") or f"None — first scan of this repo. Future re-runs should rename this file to `GitHub-Scanner-{target['repo']}-{scan_date}.md` before generating the new report."
    rows.append(("Prior scan", prior))

    lines = ["## Catalog metadata", "", "| Field | Value |", "|-------|-------|"]
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    lines += ["", "---"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Verdict (split-axis aware) + exhibits
# ---------------------------------------------------------------------------

def _verdict(form) -> str:
    verdict_level = form.get("phase_4b_computed", {}).get("verdict", {}).get("level", "Unknown")
    split = form["phase_4_structured_llm"].get("split_axis_decision", {}) or {}
    entries = split.get("entries", [])
    axis = split.get("axis", "")

    if split.get("should_split") and entries:
        title = f"## Verdict: {verdict_level} (split — {axis.capitalize()} axis only)"
    else:
        title = f"## Verdict: {verdict_level}"

    lines = [title, ""]
    if entries:
        for e in entries:
            scope = f"{axis.capitalize()} · {e.get('audience', '')}"
            suffix = f" · {e.get('scope_detail', '')}" if e.get("scope_detail") else ""
            headline = e.get("headline", "")
            summary = e.get("summary", "")
            lines.append(f"### {scope}{suffix} — **{e.get('verdict_level', verdict_level)} — {headline}**")
            lines.append("")
            lines.append(summary)
            lines.append("")

    # Exhibits — only render if the LLM produced explicit groups.
    groups = form["phase_4_structured_llm"].get("verdict_exhibits", {}).get("groups", [])
    if groups:
        lines.append("### Verdict exhibits (grouped for reading speed)")
        lines.append("")
        for g in groups:
            summary = g.get("one_line_summary", "")
            items = g.get("items", [])
            symbol = g.get("symbol", "⚠")
            lines.append("<details>")
            lines.append(f"<summary><strong>{symbol} {g.get('headline', '')} ({len(items)} findings)</strong>")
            if summary:
                lines.append(f"<br><em>{summary}</em></summary>")
            else:
                lines.append("</summary>")
            lines.append("")
            for i, it in enumerate(items, 1):
                lines.append(f"{i}. **{it.get('tag', '')}** — {it.get('claim', '')}")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Trust Scorecard
# ---------------------------------------------------------------------------

SCORECARD_QUESTIONS = [
    ("does_anyone_check_the_code",      "Does anyone check the code?"),
    ("is_it_safe_out_of_the_box",       "Is it safe out of the box?"),
    ("do_they_fix_problems_quickly",    "Do they fix problems quickly?"),
    ("do_they_tell_you_about_problems", "Do they tell you about problems?"),
]


def _scorecard(form) -> str:
    cells = form.get("phase_3_computed", {}).get("scorecard_cells", {}) or {}
    lines = ["## Trust Scorecard", "", "| Question | Answer |", "|----------|--------|"]
    for key, question in SCORECARD_QUESTIONS:
        cell = cells.get(key, {}) or {}
        color = cell.get("color") or "amber"
        icon = CELL_ICON.get(color, "⚠")
        answer = cell.get("short_answer", "")
        # Golden format: `icon **<headline>** — <detail>`. If the short_answer contains
        # ` — ` we split on it; the left side becomes the bolded headline. Otherwise
        # we prepend the color-word as the headline.
        if " — " in answer:
            head, _, tail = answer.partition(" — ")
            cell_text = f"**{head}** — {tail}"
        elif answer:
            cell_text = f"**{CELL_WORD.get(color, 'Partly')}** — {answer}"
        else:
            cell_text = f"**{CELL_WORD.get(color, 'Partly')}**"
        lines.append(f"| {question} | {icon} {cell_text} |")
    lines += ["", "---"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 01 · What should I do?
# ---------------------------------------------------------------------------

def _section_01(form) -> str:
    steps = form["phase_4_structured_llm"].get("action_steps", {}).get("entries", [])
    section_actions = form["phase_4_structured_llm"].get("section_actions", {}).get("entries", [])
    s01 = next((a["action"] for a in section_actions if a.get("section") == "01"), "")
    lead = form["phase_4_structured_llm"].get("section_leads", {}).get("section_01")

    lines = ["## 01 · What should I do?", ""]

    # Summary banner (blockquote)
    if lead:
        lines.append(f"> {lead.get('pill_row', '')}")
        lines.append(">")
        lines.append(f"> {lead.get('summary', '')}")
    else:
        # Fallback summary from action steps count and section action prose
        n = len(steps)
        warn = sum(1 for s in steps if s.get("severity") == "Warning")
        ok = sum(1 for s in steps if s.get("severity") == "OK")
        bits = []
        if ok:
            bits.append(f"✓ {ok} safe step{'s' if ok != 1 else ''}")
        if warn:
            bits.append(f"⚠ {warn} mitigation{'s' if warn != 1 else ''}")
        bits.append(f"{n} step{'s' if n != 1 else ''}")
        lines.append("> " + " · ".join(bits))
        if s01:
            lines.append(">")
            lines.append(f"> {s01}")
    lines.append("")

    for s in steps:
        sev = s.get("severity", "OK")
        sym = SEV_SYMBOL.get(sev, "")
        lines.append(f"### Step {s.get('step', '')}: {s.get('headline', '')} ({sym})")
        lines.append("")
        if s.get("non_technical"):
            lines.append(f"**Non-technical:** {s['non_technical']}")
            lines.append("")
        cmd = s.get("command")
        if cmd:
            lang = s.get("command_lang", "bash")
            lines.append(f"```{lang}")
            lines.append(cmd)
            lines.append("```")
            lines.append("")

    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 02 · What we found (finding cards)
# ---------------------------------------------------------------------------

def _section_02(form) -> str:
    findings = form["phase_4_structured_llm"].get("findings", {}).get("entries", [])
    prose = {
        p["finding_id"]: p
        for p in form.get("phase_5_prose_llm", {}).get("per_finding_prose", {}).get("entries", [])
    }
    section_actions = form["phase_4_structured_llm"].get("section_actions", {}).get("entries", [])
    s02 = next((a["action"] for a in section_actions if a.get("section") == "02"), "")

    counts = {"Critical": 0, "Warning": 0, "Info": 0, "OK": 0}
    for f in findings:
        counts[f.get("severity", "OK")] = counts.get(f.get("severity", "OK"), 0) + 1

    pill_bits = []
    for sev, label in [("Critical", "Critical"), ("Warning", "Warning"), ("Info", "Info"), ("OK", "OK")]:
        if counts[sev]:
            pill_bits.append(f"{SEV_SYMBOL[sev]} {counts[sev]} {label}")

    total = len(findings)
    lines = [
        "## 02 · What we found",
        "",
        "> " + " · ".join(pill_bits),
        ">",
        f"> {total} findings total." + (f" {s02}" if s02 else ""),
    ]
    lines.append("")

    # Render each finding card
    for f in findings:
        lines.append(_render_finding(f, prose.get(f["id"])))
        lines.append("")

    lines.append("---")
    return "\n".join(lines)


def _render_finding(f, prose) -> str:
    sev = f.get("severity", "OK")
    fid = f.get("id", "F?")
    kind = f.get("kind")
    boundary = f.get("boundary_case")
    title = f.get("title", "")
    header_bits = [f"### {fid} — {_sev_label(sev)}"]
    if kind:
        header_bits.append(kind)
    if boundary:
        header_bits.append("boundary case")
    header = " · ".join(header_bits) + f" — {title}"

    out = [header, ""]
    hint = f.get("action_hint")
    if hint:
        bits = []
        if f.get("duration_label"):
            bits.append(f["duration_label"])
        if f.get("date_label"):
            bits.append(f["date_label"])
        bits.append(f"→ {hint}")
        out.append("*" + " · ".join(bits) + "*")
        out.append("")

    if prose:
        # Finding prose paragraphs (body → what this means → what this does NOT mean)
        body = prose.get("body_paragraphs") or []
        for p in body:
            out.append(p)
            out.append("")
        if prose.get("what_we_observed"):
            out.append(f"**What we observed.** {prose['what_we_observed']}")
            out.append("")
        if prose.get("what_this_means"):
            out.append(f"**What this means for you.** {prose['what_this_means']}")
            out.append("")
        if prose.get("what_this_does_not_mean"):
            out.append(f"**What this does NOT mean.** {prose['what_this_does_not_mean']}")
            out.append("")

    # Meta table
    meta_rows = f.get("meta_table") or []
    if meta_rows:
        out.append("| Meta | Value |")
        out.append("|------|-------|")
        for row in meta_rows:
            out.append(f"| {row.get('label', '')} | {row.get('value', '')} |")
        out.append("")

    fix = f.get("how_to_fix")
    if fix:
        out.append(f"**How to fix.** {fix}")
        out.append("")

    return "\n".join(out).rstrip()


# ---------------------------------------------------------------------------
# 02A · Executable file inventory
# ---------------------------------------------------------------------------

def _section_02a(form) -> str:
    inv = form["phase_4_structured_llm"].get("executable_file_inventory", {}) or {}
    summary = inv.get("layer1_summary")
    rows = inv.get("layer2_entries", [])
    exec_files = form["phase_1_raw_capture"].get("code_patterns", {}).get("executable_files", {}).get("entries", [])

    if not (summary or rows):
        # Minimum coverage: emit a terse inventory if the structured field is empty
        # (so the section isn't silently omitted when there are zero executables).
        install_hooks = form["phase_1_raw_capture"].get("code_patterns", {}).get("install_hooks", {}).get("found", False)
        if not exec_files and not install_hooks:
            return ""

    lines = ["## 02A · Executable file inventory", ""]
    if inv.get("lead"):
        lines.append(f"> {inv['lead']}")
        lines.append("")
    if summary:
        lines.append("### Layer 1 — one-line summary")
        lines.append("")
        lines.append(f"- {summary}")
        lines.append("")
    if rows:
        lines.append("### Layer 2 — per-file runtime inventory")
        lines.append("")
        lines.append("| File | Kind | Runtime | Dangerous calls | Network | Notes |")
        lines.append("|------|------|---------|-----------------|---------|-------|")
        for r in rows:
            lines.append(
                f"| `{r.get('path', '')}` | {r.get('kind', '')} | {r.get('runtime', '')} | "
                f"{r.get('dangerous_calls', 'None')} | {r.get('network', 'None')} | {r.get('notes', '')} |"
            )
        lines.append("")
    if inv.get("closing_note"):
        lines.append(inv["closing_note"])
        lines.append("")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 03 · Suspicious code changes (PR sample)
# ---------------------------------------------------------------------------

def _section_03(form) -> str:
    pr = form["phase_1_raw_capture"].get("pr_review", {}) or {}
    sample = pr.get("prs", [])
    review_summary = form["phase_4_structured_llm"].get("pr_sample_review", {}) or {}
    rows = review_summary.get("rows", [])
    if not sample and not rows:
        return ""

    total = pr.get("total_closed_prs", "")
    formal = pr.get("formal_review_rate")
    any_r = pr.get("any_review_rate")
    self_merge = pr.get("self_merge_rate")

    lines = ["## 03 · Suspicious code changes", ""]
    intro = review_summary.get("intro")
    if intro:
        lines.append(f"> {intro}")
        lines.append("")
    else:
        concern_count = sum(1 for r in rows if r.get("flagged"))
        lines.append(f"> ✓ {concern_count} security-concerning PRs · ℹ {len(sample) or len(rows)} recent merges sampled")
        lines.append("")

    lead = (
        f"Sample: the {len(sample)} most recent merged PRs at scan time"
        + (f", plus flagged PRs." if any(r.get("flagged") for r in rows) else ".")
        + (f" Dual review-rate metric on this sample: formal `reviewDecision` set on {formal}% of sampled PRs." if formal is not None else "")
    )
    lines.append(lead)
    lines.append("")

    # Prefer LLM-enriched rows; fall back to raw PR sample.
    if rows:
        lines.append("| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |")
        lines.append("|----|-------------|--------------|-----------|-----------|---------|")
        for r in rows:
            pr_num = r.get("number", "")
            pr_url = r.get("url") or f"https://github.com/{form['target']['owner']}/{form['target']['repo']}/pull/{pr_num}"
            lines.append(
                f"| [#{pr_num}]({pr_url}) | {r.get('what', '')} | {r.get('author', '')} | {r.get('merger', '')} | "
                f"{r.get('reviewed', '')} | {r.get('concern', '')} |"
            )
    else:
        lines.append("| PR | Author | Merger | Formal review | Any review | Self-merge |")
        lines.append("|----|--------|--------|---------------|------------|------------|")
        for p in sample:
            pr_num = p.get("number", "")
            pr_url = f"https://github.com/{form['target']['owner']}/{form['target']['repo']}/pull/{pr_num}"
            lines.append(
                f"| [#{pr_num}]({pr_url}) | {p.get('author', '')} | {p.get('merger', '')} | "
                f"{p.get('formal_review') or '—'} | {'yes' if p.get('any_review') else 'no'} | "
                f"{'yes' if p.get('self_merge') else 'no'} |"
            )
    lines.append("")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 04 · Timeline
# ---------------------------------------------------------------------------

TONE_ICON = {"positive": "🟢", "neutral": "🟡", "negative": "🔴", "warn": "🟠"}


def _section_04(form) -> str:
    events = form["phase_4_structured_llm"].get("timeline_events", {}).get("entries", [])
    if not events:
        return ""

    tone_counts = {}
    for e in events:
        tone_counts[e.get("tone", "neutral")] = tone_counts.get(e.get("tone", "neutral"), 0) + 1

    pill_bits = []
    if tone_counts.get("positive"):
        pill_bits.append(f"✓ {tone_counts['positive']} good")
    if tone_counts.get("neutral"):
        pill_bits.append(f"🟡 {tone_counts['neutral']} neutral")
    if tone_counts.get("negative"):
        pill_bits.append(f"🔴 {tone_counts['negative']} concerning")

    lines = ["## 04 · Timeline", ""]
    intro = form["phase_4_structured_llm"].get("timeline_intro")
    if pill_bits:
        lines.append("> " + " · ".join(pill_bits))
        if intro:
            lines.append(">")
            lines.append(f"> {intro}")
        lines.append("")

    for e in events:
        icon = TONE_ICON.get(e.get("tone", "neutral"), "🟡")
        date = e.get("date", "")
        label = e.get("label", "")
        note = e.get("note", "")
        lines.append(f"- {icon} **{date} · {label}** — {note}")

    lines.append("")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 05 · Repo vitals
# ---------------------------------------------------------------------------

def _section_05(form) -> str:
    vitals = form["phase_4_structured_llm"].get("repo_vitals", {}).get("rows", [])
    if not vitals:
        return ""
    lines = ["## 05 · Repo vitals", "", "| Metric | Value | Note |", "|--------|-------|------|"]
    for v in vitals:
        lines.append(f"| {v.get('metric', '')} | {v.get('value', '')} | {v.get('note', '')} |")
    lines.append("")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 06 · Investigation coverage
# ---------------------------------------------------------------------------

def _section_06(form) -> str:
    coverage = form["phase_3_computed"].get("coverage_status", {}).get("cells", [])
    detail = form["phase_4_structured_llm"].get("coverage_detail", {}).get("rows", [])
    if not coverage and not detail:
        return ""

    status_icon = {"ok": "✅", "partial": "⚠", "blocked": "❌", "not_available": "⚠",
                   "not_indexed": "ℹ", "not_queried": "ℹ", "unknown": "⚠"}

    lines = ["## 06 · Investigation coverage", ""]
    intro = form["phase_4_structured_llm"].get("coverage_intro")
    if intro:
        lines.append(f"> {intro}")
        lines.append("")

    lines.append("| Check | Result |")
    lines.append("|-------|--------|")

    seen_names = set()
    for d in detail:
        lines.append(f"| {d.get('check', '')} | {d.get('result', '')} |")
        seen_names.add(d.get("check"))

    for c in coverage:
        if c.get("name") in seen_names:
            continue
        icon = status_icon.get(c.get("status", "unknown"), "⚠")
        lines.append(f"| {c['name']} | {icon} {c.get('detail', '')} |")

    gaps = form["phase_4_structured_llm"].get("coverage_gaps", {}).get("entries", [])
    if gaps:
        lines.append("")
        lines.append("**Gaps noted:**")
        lines.append("")
        for i, g in enumerate(gaps, 1):
            lines.append(f"{i}. {g}")

    lines.append("")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 07 · Evidence appendix
# ---------------------------------------------------------------------------

def _section_07(form) -> str:
    evidence = form["phase_4_structured_llm"].get("evidence", {}).get("entries", [])
    if not evidence:
        return ""

    priority = form["phase_4_structured_llm"].get("priority_evidence", {}).get("selections", [])
    priority_ids = {p.get("evidence_id") for p in priority}

    total = len(evidence)
    lines = [
        "## 07 · Evidence appendix",
        "",
        f"> ℹ {total} facts · ★ {len(priority_ids)} priority",
        "",
    ]
    intro = form["phase_4_structured_llm"].get("evidence_intro")
    if intro:
        lines.append(intro)
        lines.append("")

    pri = [e for e in evidence if e.get("id") in priority_ids]
    other = [e for e in evidence if e.get("id") not in priority_ids]

    if pri:
        lines.append("### ★ Priority evidence (read first)")
        lines.append("")
        for e in pri:
            lines += _render_evidence_block(e, star=True)

    if other:
        lines.append("### Other evidence")
        lines.append("")
        for e in other:
            lines += _render_evidence_block(e, star=False)

    lines.append("---")
    return "\n".join(lines)


def _render_evidence_block(e, star=False):
    marker = "★ " if star else ""
    out = [f"#### {marker}Evidence {e.get('id', '').lstrip('E')} — {e.get('claim', '')}", ""]
    if e.get("command"):
        lang = e.get("command_lang", "bash")
        out.append(f"```{lang}")
        out.append(e["command"])
        out.append("```")
        out.append("")
    if e.get("result"):
        lang = e.get("result_lang", "")
        out.append("Result:")
        out.append(f"```{lang}" if lang else "```")
        out.append(e["result"])
        out.append("```")
        out.append("")
    classification = e.get("classification")
    if classification:
        out.append(f"*Classification: {classification}*")
        out.append("")
    return out


# ---------------------------------------------------------------------------
# 08 · How this scan works  (static methodology boilerplate)
# ---------------------------------------------------------------------------

METHODOLOGY_BODY = """### What this scan is

This is an **LLM-driven security investigation** — an AI assistant with terminal access used the [GitHub CLI](https://cli.github.com/) and free public APIs to investigate this repo's governance, code patterns, dependencies, and distribution pipeline. It then synthesized its findings into this plain-English report.

This is **not** a static analyzer, penetration test, or formal security audit. It is a trust-assessment tool that answers: "Should I install this?"

### What we checked

| Area | Scope |
|------|-------|
| Governance & Trust | Branch protection, rulesets, CODEOWNERS, SECURITY.md, community health, maintainer account age & activity, code review rates |
| Code Patterns | Dangerous primitives (eval, exec, fetch), hardcoded secrets, executable file inventory, install scripts, README paste-blocks |
| Supply Chain | Dependencies, CI/CD workflows, GitHub Actions SHA-pinning, release pipeline, artifact verification, published-vs-source comparison |
| AI Agent Rules | CLAUDE.md, AGENTS.md, .cursorrules, .mcp.json — files that instruct AI coding assistants. Checked for prompt injection and behavioral manipulation |

### External tools used

| Tool | Purpose |
|------|---------|
| [OSSF Scorecard](https://securityscorecards.dev/) | Independent security rating from the Open Source Security Foundation. Scores 24 practices from 0-10. Free API, no installation needed. |
| [osv.dev](https://osv.dev/) | Google-backed vulnerability database. Used as fallback when GitHub's Dependabot data is not accessible (requires repo admin). |
| [gitleaks](https://gitleaks.io/) (optional) | Scans code history for leaked passwords, API keys, and tokens. Requires installation. If unavailable, gap noted in Coverage. |
| [GitHub CLI](https://cli.github.com/) | Primary data source. All repo metadata, PR history, workflow files, contributor data, and issue history come from authenticated GitHub API calls. |

### What this scan cannot detect

- **Transitive dependency vulnerabilities** — we check direct dependencies but cannot fully resolve the dependency tree without running the package manager
- **Runtime behavior** — we see what the code *could* do, not what it *does* when running
- **Published artifact tampering** — we read the source code but cannot verify that what's published to npm/PyPI matches this source exactly
- **Sophisticated backdoors** — our pattern-matching catches common dangerous primitives but not logic bombs or obfuscated payloads
- **Container image contents** — we read Dockerfiles but cannot inspect built images for extra layers or embedded secrets

For comprehensive vulnerability scanning, pair this report with tools like [Semgrep](https://semgrep.dev/) (code analysis), [Snyk](https://www.snyk.io/) (dependency scanning), or [Trivy](https://aquasecurity.github.io/trivy/) (container scanning)."""


def _section_08(form) -> str:
    methodology = form["phase_3_computed"].get("methodology", {}) or {}
    scanner_ver = methodology.get("scanner_version", "unknown")
    prompt_ver = methodology.get("prompt_version", "unknown")
    guide_ver = methodology.get("guide_version", "unknown")

    version_line = (
        f"Scanner prompt {prompt_ver} · Operator Guide {guide_ver} · "
        f"Validator with XSS checks + verdict-severity coherence · "
        f"[stop-git-std](https://github.com/stefans71/stop-git-std)"
    )

    return "\n".join([
        "## 08 · How this scan works",
        "",
        METHODOLOGY_BODY,
        "",
        "### Scan methodology version",
        "",
        version_line,
        "",
        "---",
    ])


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def _footer(form) -> str:
    target = form["target"]
    meta = form.get("_meta", {})
    head_sha = form["phase_1_raw_capture"]["pre_flight"].get("head_sha", "")
    releases = form["phase_1_raw_capture"].get("releases", {}).get("entries", [])
    latest_tag = releases[0]["tag"] if releases else "untagged"
    scan_date = _scan_date(form)
    scanner_ver = meta.get("scanner_version", "unknown")

    return "\n".join([
        f"*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · "
        f"{scan_date} · scanned main @ `{head_sha}` ({latest_tag}) · scanner {scanner_ver}*",
        "",
        "*This report is an automated investigation, not a professional security audit. "
        "It may miss issues. If you are making a business decision, consult a security professional.*",
    ])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
