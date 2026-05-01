#!/usr/bin/env python3
"""Phase 5 — build calibration-rebuild-rerender-comparison.md from comparison data.

Reads docs/phase_5_comparison_data.json (produced by phase_5_recompute.py) and
emits docs/calibration-rebuild-rerender-comparison.md showing per-scan:
  - old verdict / new verdict
  - per-cell advisory shift (with rule_id) + Phase 4 LLM color + override status
  - one-line shift rationale

Stub block at the end notes entries 1-11 are V2.4 era (no V1.2 bundle).
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / "docs" / "phase_5_comparison_data.json"
OUT = REPO_ROOT / "docs" / "calibration-rebuild-rerender-comparison.md"

CELL_LABELS = {
    "does_anyone_check_the_code": "Q1 (review)",
    "do_they_fix_problems_quickly": "Q2 (fix)",
    "do_they_tell_you_about_problems": "Q3 (disclose)",
    "is_it_safe_out_of_the_box": "Q4 (install)",
}

ENTRIES_OUT_OF_SCOPE = [
    # entry_num, label, reason
    (1, "JuliusBrussee/caveman", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (2, "coleam00/Archon", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (3, "coleam00/Archon (re-run)", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (4, "pmndrs/zustand", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (5, "sharkdp/fd", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (6, "grapeot/gstack", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (7, "stefans71/stop-git-std/archon-board-review", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (8, "NousResearch/hermes-agent", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (9, "gitroomhq/postiz-app", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (10, "pmndrs/zustand (V2.4 re-scan)", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (11, "multica-ai/multica", "V2.4 era hand-authored against V1.1 schema — no V1.2 form.json"),
    (12, "pmndrs/zustand (Step G pilot)", "V2.5-preview Step G pilot — phase_4 lives in V1.1 .board-review-temp/step-g-execution/zustand-step-g-form.json; would need V1.1→V1.2 schema upgrade + Phase 4 re-authoring"),
    (13, "JuliusBrussee/caveman (Step G)", "V2.5-preview Step G pilot — phase_4 lives in V1.1 .board-review-temp/step-g-execution/caveman-step-g-form.json; same migration cost"),
    (14, "coleam00/Archon (Step G)", "V2.5-preview Step G pilot — phase_4 lives in V1.1 .board-review-temp/step-g-execution/Archon-step-g-form.json; same migration cost"),
    (15, "microsoft/markitdown (wild)", "V1.2 form.json in .scan-workspaces/markitdown/ has empty phase_4_structured_llm.scorecard_cells (LLM cells were authored to .md sidecar bundle); re-rendering produces Q2 regression"),
]


def gate_63_violations(entries: list) -> list:
    """Cells where new advisory differs from Phase 4 LLM color WITHOUT
    override_reason set. These need Phase 6 attention (re-author Phase 4)."""
    out = []
    for e in entries:
        for cell_key, c in e["cells"].items():
            if (
                c["advisory_new_color"] != c["phase_4_color"]
                and c["phase_4_color"] is not None
                and not c["phase_4_override_reason"]
            ):
                out.append({
                    "entry_num": e["entry_num"],
                    "label": e["label"],
                    "cell": cell_key,
                    "cell_label": CELL_LABELS[cell_key],
                    "advisory_new": c["advisory_new_color"],
                    "advisory_new_rule_id": c["advisory_new_rule_id"],
                    "phase_4": c["phase_4_color"],
                })
    return out


def cell_short(c: dict) -> str:
    """Compact per-cell summary: old→new (rule) | LLM=color [override]."""
    old = c.get("advisory_old_color") or "—"
    new = c.get("advisory_new_color") or "—"
    rule = c.get("advisory_new_rule_id") or "—"
    p4 = c.get("phase_4_color") or "—"
    ov = c.get("phase_4_override_reason")
    arrow = "→" if old != new else "="
    ov_str = f" [override: {ov}]" if ov else ""
    return f"{old}{arrow}{new} ({rule}) | LLM={p4}{ov_str}"


def shift_summary(cells: dict) -> str:
    """One-line rationale across all 4 cells."""
    shifts = [k for k, c in cells.items() if c["advisory_old_color"] != c["advisory_new_color"]]
    redundant_overrides = [
        k for k, c in cells.items()
        if c["advisory_new_color"] == c["phase_4_color"] and c["phase_4_override_reason"]
    ]
    bits = []
    if shifts:
        bits.append(f"{len(shifts)} advisory shift{'s' if len(shifts) > 1 else ''}: {', '.join(CELL_LABELS[k].split()[0] for k in shifts)}")
    if redundant_overrides:
        bits.append(f"{len(redundant_overrides)} override{'s' if len(redundant_overrides) > 1 else ''} now redundant ({', '.join(CELL_LABELS[k].split()[0] for k in redundant_overrides)})")
    if not bits:
        bits.append("no advisory shift; no redundant overrides")
    return "; ".join(bits)


def main():
    data = json.loads(DATA.read_text())
    entries = data["entries"]

    lines = []
    lines.append("# Calibration v2 rerender — comparison report")
    lines.append("")
    lines.append("**Phase 5 of `docs/back-to-basics-plan.md` — owner-review gate before Phase 5 commit 1.**")
    lines.append("")
    entry_nums = sorted(e["entry_num"] for e in entries)
    lines.append(f"Bundles re-evaluated: **{len(entries)} V1.2 catalog scans (entries {entry_nums[0]}-{entry_nums[-1]})**.")
    lines.append("")
    lines.append("Per cell, the table shows: `old_advisory→new_advisory (rule_id) | LLM=phase_4_color [override: reason if any]`. Color codes: `r`=red, `a`=amber, `g`=green, `—`=not present.")
    lines.append("")
    lines.append("## Headline findings")
    lines.append("")

    verdict_shifts = sum(1 for e in entries if e["verdict_old"] != e["verdict_new"])
    advisory_shifts = sum(
        1
        for e in entries
        for c in e["cells"].values()
        if c["advisory_old_color"] != c["advisory_new_color"]
    )
    redundant = sum(
        1
        for e in entries
        for c in e["cells"].values()
        if c["advisory_new_color"] == c["phase_4_color"] and c["phase_4_override_reason"]
    )

    lines.append(f"- **Verdict shifts:** {verdict_shifts} of {len(entries)} (verdict reads `compute_verdict(findings)`; findings unchanged in this rerender, so verdicts are stable by construction).")
    lines.append(f"- **Advisory shifts:** {advisory_shifts} cell(s) across {sum(1 for e in entries if any(c['advisory_old_color'] != c['advisory_new_color'] for c in e['cells'].values()))} entries — calibration v2 advisory differs from legacy advisory.")
    lines.append(f"- **Redundant overrides:** {redundant} cell(s) — Phase 4 LLM previously override-explained but new advisory now matches the LLM color naturally (rule-driven). These are calibration wins.")
    lines.append("")
    lines.append(f"## Per-entry comparison (entries {entry_nums[0]}-{entry_nums[-1]})")
    lines.append("")
    lines.append("| # | Repo | Shape | Verdict (old→new) | Cell shifts (Q1 / Q2 / Q3 / Q4) | Summary |")
    lines.append("|---|---|---|---|---|---|")

    for e in entries:
        verdict = (
            f"**{e['verdict_old']}**"
            if e["verdict_old"] == e["verdict_new"]
            else f"{e['verdict_old']} → **{e['verdict_new']}**"
        )
        shape = e["shape_classification"]["category"]
        cells = e["cells"]
        cell_col = " · ".join(cell_short(cells[k]) for k in CELL_LABELS)
        lines.append(
            f"| {e['entry_num']} | {e['label']} | `{shape}` | {verdict} | {cell_col} | {shift_summary(cells)} |"
        )

    lines.append("")
    lines.append("## Per-entry detail")
    lines.append("")

    for e in entries:
        lines.append(f"### Entry {e['entry_num']} — {e['label']}")
        lines.append("")
        sc = e["shape_classification"]
        lines.append(f"- **Shape:** `{sc['category']}` (confidence={sc['confidence']}, matched_rule={sc['matched_rule']!r})")
        lines.append(
            f"- Solo-maintained: {sc['is_solo_maintained']} · Privileged-tool: {sc['is_privileged_tool']} · Reverse-engineered: {sc['is_reverse_engineered']}"
        )
        lines.append(f"- Verdict (Phase 4b): old=`{e['verdict_old']}` new=`{e['verdict_new']}`")
        lines.append(f"- Bundle: `{e['bundle_path']}`")
        lines.append(f"- Output: `docs/scans/catalog/{e['output_basename']}.md` + `.html`")
        lines.append("")
        lines.append("| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |")
        lines.append("|---|---|---|---|---|---|---|")
        for k, label in CELL_LABELS.items():
            c = e["cells"][k]
            lines.append(
                f"| {label} | `{c['advisory_old_color'] or '—'}` | `{c['advisory_new_color']}` | `{c['advisory_new_rule_id']}` | `{c['phase_4_color'] or '—'}` | {c['phase_4_override_reason'] or '—'} | {c['shift_note']} |"
            )
        lines.append("")

    lines.append("## Out-of-scope entries (1-15)")
    lines.append("")
    lines.append("These remain unchanged on disk. Each row notes why the entry can't flow through V1.2 calibration v2 without separate re-authoring work.")
    lines.append("")
    lines.append("| # | Repo | Reason |")
    lines.append("|---|---|---|")
    for n, label, reason in ENTRIES_OUT_OF_SCOPE:
        lines.append(f"| {n} | {label} | {reason} |")
    lines.append("")
    lines.append("## Phase 6 input — gate 6.3 backlog")
    lines.append("")
    lines.append("Calibration v2 advisory recompute created `phase_3_advisory.scorecard_hints` colors that differ from the original `phase_4_structured_llm.scorecard_cells` colors on the cells listed below. The original Phase 4 LLM judgments did not flag these as overrides because the legacy advisory matched the LLM color in v1; the v2 advisory differs.")
    lines.append("")
    lines.append("Validator gate 6.3 (`--form` mode) requires `override_reason` + rationale + `computed_signal_refs` whenever `phase_3` advisory ≠ `phase_4` LLM color. These cells are now violating that gate at bundle level.")
    lines.append("")
    lines.append("**Owner decision (Phase 5 sign-off): defer (path W).** Phase 5 completion criteria specify validator clean on **rendered files** (`--report` mode) and `--parity` zero-warning on MD/HTML pairs — both of which are clean. The `--form` validator on bundles is not in Phase 5 acceptance scope. Resolution belongs to Phase 6 where Phase 4 LLM cells are re-authored against the calibrated advisory.")
    lines.append("")
    lines.append("**Resolution paths considered (selected: W):**")
    lines.append("- **(X) Backfill** — write generic `override_reason` + rationale on each cell. Rejected: would require new enum value (`phase_5_advisory_shift`) and synthetic rationale that doesn't reflect real LLM judgment.")
    lines.append("- **(Y) Re-author** — Phase 4 LLM regenerates affected cells against new advisory. Rejected: pulls Phase 6 work into Phase 5; out of scope.")
    lines.append("- **(W) Defer** — selected. Document the backlog here as Phase 6 input; bundles carry the gate 6.3 violation as known state.")
    lines.append("")
    violations = gate_63_violations(entries)
    lines.append(f"**Gate 6.3 backlog: {len(violations)} cell(s) across {len({(v['entry_num']) for v in violations})} entries.**")
    lines.append("")
    lines.append("| # | Repo | Cell | New advisory | Rule | Phase 4 LLM | Direction |")
    lines.append("|---|---|---|---|---|---|---|")
    severity_order = {"red": 0, "amber": 1, "green": 2}
    for v in violations:
        adv_idx = severity_order.get(v["advisory_new"], 1)
        p4_idx = severity_order.get(v["phase_4"], 1)
        if adv_idx < p4_idx:
            direction = f"advisory `{v['advisory_new']}` ≠ LLM `{v['phase_4']}` (advisory now stricter)"
        else:
            direction = f"advisory `{v['advisory_new']}` ≠ LLM `{v['phase_4']}` (LLM stricter than rule)"
        lines.append(
            f"| {v['entry_num']} | {v['label']} | {v['cell_label']} | `{v['advisory_new']}` | `{v['advisory_new_rule_id']}` | `{v['phase_4']}` | {direction} |"
        )
    lines.append("")
    lines.append("Phase 6 work item: re-author Phase 4 LLM cells for these 6 cells (or whatever subset the calibrated advisory genuinely changes the right answer for) and update `override_reason` where the LLM still wants to disagree with the rule-driven advisory.")
    lines.append("")
    lines.append("## Owner sign-off")
    lines.append("")
    lines.append("Phase 5 plan body specifies this comparison doc as the pre-commit gate. Owner reviews each verdict shift (zero in this rerender) and each advisory shift before Phase 5 commit 1 lands. Sign-off recorded in the conversation: 12-entry scope (entries 16-27) + (W) defer on gate 6.3 backlog.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"_Generated by `docs/phase_5_build_comparison.py` from `docs/phase_5_comparison_data.json`._")
    lines.append("")

    OUT.write_text("\n".join(lines))
    print(f"✓ wrote {OUT.relative_to(REPO_ROOT)}")
    print(f"  {len(entries)} entries, {advisory_shifts} cell shifts, {redundant} redundant overrides, {verdict_shifts} verdict shifts")


if __name__ == "__main__":
    main()
