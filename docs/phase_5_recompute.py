#!/usr/bin/env python3
"""Phase 5 — recompute calibration v2 advisory + persist for 16 catalog scans.

One-shot migration script. Run from repo root:
    python3 docs/phase_5_recompute.py

For each of the 16 V1.2 bundles in scope (catalog entries 12-27):
  1. Capture old phase_3_advisory.scorecard_hints + phase_4b verdict
  2. Run compute_scorecard_cells_v2(form) to get new advisory + shape
  3. Persist new scorecard_hints + shape_classification back into bundle
  4. Record per-cell old/new comparison into docs/phase_5_comparison_data.json

Verdict (compute_verdict on findings) is unchanged because findings haven't
been re-authored — the comparison records this as no-shift.

Phase 4 LLM scorecard cells are unchanged (still hold the original LLM
judgment). The comparison flags cells where calibration v2 makes the
existing override redundant (advisory now matches LLM color naturally).

After this script: re-render all 16 bundles via render-md.py + render-html.py
to produce updated catalog scans.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))
from compute import compute_scorecard_cells_v2

CELLS = [
    "does_anyone_check_the_code",
    "do_they_fix_problems_quickly",
    "do_they_tell_you_about_problems",
    "is_it_safe_out_of_the_box",
]

# Catalog entries 16-27 — 12 V1.2 wild bundles in scope for Phase 5.
#
# Out of scope:
# - Entries 1-11: V2.4 era hand-authored against V1.1 schema, no V1.2 form.json.
# - Entries 12-14 (Step G pilots): V1.1-schema test artifacts; authoritative
#   phase_4 lives in .board-review-temp/step-g-execution/*.json (V1.1) and
#   re-rendering through V1.2 calibration v2 would require schema-upgrade +
#   Phase 4 re-authoring.
# - Entry 15 (markitdown): V1.2 form.json in .scan-workspaces/ has empty
#   phase_4_structured_llm.scorecard_cells (LLM cells were authored to a .md
#   sidecar bundle, not the JSON form). Re-rendering produces a regression
#   on Q2 because renderer falls back to phase_3 advisory.
ENTRIES = [
    # entry_num, catalog_label, bundle_relpath, output_basename
    (16, "ghostty-org/ghostty (wild)", "docs/scan-bundles/ghostty-dcc39dc.json", "GitHub-Scanner-ghostty-v12"),
    (17, "shiyu-coder/Kronos (wild)", "docs/scan-bundles/Kronos-67b630e.json", "GitHub-Scanner-Kronos-v12"),
    (18, "basecamp/kamal (wild)", "docs/scan-bundles/kamal-6a31d14.json", "GitHub-Scanner-kamal-v12"),
    (19, "XTLS/Xray-core (wild)", "docs/scan-bundles/Xray-core-b465036.json", "GitHub-Scanner-Xray-core-v12"),
    (20, "BatteredBunny/browser_terminal (wild)", "docs/scan-bundles/browser_terminal-9a77c4a.json", "GitHub-Scanner-browser_terminal-v12"),
    (21, "wezterm/wezterm (wild)", "docs/scan-bundles/wezterm-577474d.json", "GitHub-Scanner-wezterm-v12"),
    (22, "QL-Win/QuickLook (wild)", "docs/scan-bundles/QuickLook-0cda83c.json", "GitHub-Scanner-QuickLook-v12"),
    (23, "jtroo/kanata (wild)", "docs/scan-bundles/kanata-1c496c0.json", "GitHub-Scanner-kanata-v12"),
    (24, "freerouting/freerouting (wild)", "docs/scan-bundles/freerouting-c5ad3c7.json", "GitHub-Scanner-freerouting-v12"),
    (25, "wled/WLED (wild)", "docs/scan-bundles/WLED-01328a6.json", "GitHub-Scanner-WLED"),
    (26, "WhiskeySockets/Baileys (wild)", "docs/scan-bundles/Baileys-8e5093c.json", "GitHub-Scanner-Baileys"),
    (27, "mattpocock/skills (wild)", "docs/scan-bundles/skills-b843cb5.json", "GitHub-Scanner-skills"),
]


def classify_shift(advisory_old: str | None, advisory_new: str, phase_4: str | None,
                   override_old: str | None) -> str:
    """One-line summary of what changed for this cell."""
    if advisory_old == advisory_new:
        if phase_4 != advisory_new and override_old:
            return f"unchanged advisory ({advisory_new}); LLM override still required ({override_old})"
        elif phase_4 != advisory_new:
            return f"unchanged advisory ({advisory_new}); LLM override missing reason — pre-v2 era"
        else:
            return f"unchanged advisory ({advisory_new}); LLM aligned (no override needed)"
    # Color shifted
    if phase_4 == advisory_new and override_old:
        return f"advisory {advisory_old}→{advisory_new}; LLM override now redundant (rule-driven match)"
    if phase_4 == advisory_new and not override_old:
        return f"advisory {advisory_old}→{advisory_new}; LLM already at new color (clean)"
    if phase_4 != advisory_new:
        return f"advisory {advisory_old}→{advisory_new}; LLM at {phase_4} (override {'still ' if override_old else 'now '}required)"
    return f"advisory {advisory_old}→{advisory_new}"


def main():
    out_data = {"entries": []}
    for entry_num, label, bundle_rel, basename in ENTRIES:
        bundle_path = REPO_ROOT / bundle_rel
        if not bundle_path.exists():
            print(f"  ✗ entry {entry_num}: {bundle_rel} NOT FOUND")
            sys.exit(1)
        form = json.loads(bundle_path.read_text())

        old_advisory = form.get("phase_3_advisory", {}).get("scorecard_hints", {}) or {}
        old_verdict = form.get("phase_4b_computed", {}).get("verdict", {}).get("level")
        phase_4_cells = form.get("phase_4_structured_llm", {}).get("scorecard_cells", {}) or {}

        v2_out = compute_scorecard_cells_v2(form)
        new_shape = v2_out.pop("shape_classification")

        form.setdefault("phase_3_advisory", {})
        form["phase_3_advisory"]["scorecard_hints"] = {k: v2_out[k] for k in CELLS}
        form["phase_3_advisory"]["shape_classification"] = new_shape

        # Verdict unchanged — findings not re-authored
        new_verdict = old_verdict

        bundle_path.write_text(json.dumps(form, indent=2, default=str))

        cells_data = {}
        for k in CELLS:
            old_color = old_advisory.get(k, {}).get("color")
            new_color = v2_out[k]["color"]
            new_rule = v2_out[k]["rule_id"]
            p4_color = phase_4_cells.get(k, {}).get("color")
            p4_override = phase_4_cells.get(k, {}).get("override_reason")
            cells_data[k] = {
                "advisory_old_color": old_color,
                "advisory_new_color": new_color,
                "advisory_new_rule_id": new_rule,
                "phase_4_color": p4_color,
                "phase_4_override_reason": p4_override,
                "shift_note": classify_shift(old_color, new_color, p4_color, p4_override),
            }

        out_data["entries"].append({
            "entry_num": entry_num,
            "label": label,
            "bundle_path": bundle_rel,
            "output_basename": basename,
            "verdict_old": old_verdict,
            "verdict_new": new_verdict,
            "shape_classification": new_shape,
            "cells": cells_data,
        })
        rule_summary = " ".join(f"{k.split('_')[1][0].upper()}={v2_out[k]['rule_id']}" for k in CELLS)
        print(f"  ✓ entry {entry_num:>2} {label:<42} shape={new_shape['category']:<32} {rule_summary}")

    out_path = REPO_ROOT / "docs" / "phase_5_comparison_data.json"
    out_path.write_text(json.dumps(out_data, indent=2, default=str))
    print(f"\n✓ comparison data: {out_path.relative_to(REPO_ROOT)}")
    print(f"  {len(out_data['entries'])} bundles mutated (phase_3_advisory.scorecard_hints replaced + shape_classification added)")


if __name__ == "__main__":
    main()
