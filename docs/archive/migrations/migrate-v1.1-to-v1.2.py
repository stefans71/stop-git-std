#!/usr/bin/env python3
"""
migrate-v1.1-to-v1.2.py — one-time V1.1 → V1.2 form.json migration.

Scope (per docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md §5
Item B + §7.6): migrates 3 ACTIVE fixtures only. Archived step-g-failed-
artifact fixtures stay on V1.1 (regression witnesses).

Targets (hardcoded):
  tests/fixtures/zustand-form.json
  tests/fixtures/caveman-form.json
  tests/fixtures/archon-subset-form.json

Updates tests/fixtures/provenance.json schema_version for migrated entries.

V1.2 deltas applied:
  1. phase_1_raw_capture field-name renames (is_archived→archived etc.)
  2. phase_1_raw_capture shape changes (manifest_files [{path,format}],
     dangerous_primitives nested per-family, bare lists for install_hooks
     /agent_rule_files/executable_files, readme_paste_blocks {entries})
  3. pre_flight.symlinks_stripped bool → integer
  4. pre_flight.api_rate_limit.reset_at ISO → reset epoch int
  5. dependencies.{dependabot→dependabot_alerts, osv_dev→osv_lookups}
  6. phase_3_computed.scorecard_cells → phase_4_structured_llm.scorecard_cells
     with new-shape fields defaulted (rationale/edge_case/etc. = null,
     computed_signal_refs = [], override_reason = null)
  7. New top-level phase_3_advisory.scorecard_hints populated by mirroring
     V1.1 color/short_answer with empty signals list (no override, no
     gate 6.3 firing in migrated fixtures — intentional: fixtures are
     structural, not live pipeline output)
  8. code_patterns.agent_rule_files.total_bytes dropped (Item E)

Usage: python3 migrate-v1.1-to-v1.2.py [--dry-run]

Idempotent: safe to re-run; checks schema_version and skips if already V1.2.
"""

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ACTIVE_FIXTURES = (
    "tests/fixtures/zustand-form.json",
    "tests/fixtures/caveman-form.json",
    "tests/fixtures/archon-subset-form.json",
)
PROVENANCE = "tests/fixtures/provenance.json"

SCORECARD_QUESTION_KEYS = (
    "does_anyone_check_the_code",
    "do_they_fix_problems_quickly",
    "do_they_tell_you_about_problems",
    "is_it_safe_out_of_the_box",
)


def _iso_to_epoch(s):
    if not isinstance(s, str) or not s:
        return None
    try:
        return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def migrate_pre_flight(pf):
    if pf is None:
        return pf
    out = dict(pf)
    # symlinks_stripped bool → integer
    if isinstance(out.get("symlinks_stripped"), bool):
        out["symlinks_stripped"] = 1 if out["symlinks_stripped"] else 0
    # api_rate_limit.reset_at → reset
    arl = out.get("api_rate_limit") or {}
    if "reset_at" in arl:
        reset_epoch = _iso_to_epoch(arl.pop("reset_at"))
        arl["reset"] = reset_epoch
        out["api_rate_limit"] = arl
    return out


def migrate_repo_metadata(rm):
    if rm is None:
        return rm
    out = dict(rm)
    for old, new in (
        ("is_archived", "archived"),
        ("is_fork", "fork"),
        ("default_branch_ref", "default_branch"),
    ):
        if old in out:
            out[new] = out.pop(old)
    return out


def migrate_dependencies(deps):
    if deps is None:
        return deps
    out = dict(deps)
    # dependabot → dependabot_alerts
    if "dependabot" in out and "dependabot_alerts" not in out:
        out["dependabot_alerts"] = out.pop("dependabot")
    # osv_dev → osv_lookups
    if "osv_dev" in out and "osv_lookups" not in out:
        out["osv_lookups"] = out.pop("osv_dev")
    # manifest_files: [string] → [{path, format}]
    mf = out.get("manifest_files")
    if isinstance(mf, list) and mf and isinstance(mf[0], str):
        out["manifest_files"] = [{"path": p, "format": None} for p in mf]
    return out


def _group_hits_by_family(hits):
    """V1.1 flat hits[{family, file, line, snippet}] → V1.2 nested per-family."""
    families = {}
    for h in (hits or []):
        fam = h.get("family") or "exec"
        entry = families.setdefault(fam, {"scanned": True, "files": []})
        entry["files"].append({
            "file": h.get("file"),
            "first_match": {
                "line": h.get("line"),
                "snippet": h.get("snippet"),
            },
        })
    return families


def migrate_code_patterns(cp):
    if cp is None:
        return cp
    out = dict(cp)

    # dangerous_primitives: {hits:[], hit_count} → {scanned, exec:{files}, ...}
    dp = out.get("dangerous_primitives") or {}
    if isinstance(dp, dict) and "hits" in dp:
        hits = dp.get("hits") or []
        families = _group_hits_by_family(hits)
        new_dp = {"scanned": len(hits) > 0 or dp.get("hit_count") is not None, **families}
        if "$comment" in dp:
            new_dp["$comment"] = dp["$comment"]
        out["dangerous_primitives"] = new_dp

    # executable_files: {entries:[]} → bare list; wrap any string entries
    ef = out.get("executable_files")
    if isinstance(ef, dict) and "entries" in ef:
        ef = ef.get("entries") or []
    if isinstance(ef, list):
        out["executable_files"] = [
            {"path": e} if isinstance(e, str) else e for e in ef
        ]

    # install_hooks: {found, hooks:[]} → bare list; wrap strings
    ih = out.get("install_hooks")
    if isinstance(ih, dict) and "hooks" in ih:
        ih = ih.get("hooks") or []
    elif isinstance(ih, dict):
        ih = []
    if isinstance(ih, list):
        out["install_hooks"] = [
            {"path": e} if isinstance(e, str) else e for e in ih
        ]

    # agent_rule_files: {entries, count, total_bytes} → bare list; drop total_bytes; wrap strings
    arf = out.get("agent_rule_files")
    if isinstance(arf, dict) and "entries" in arf:
        arf = arf.get("entries") or []
    if isinstance(arf, list):
        out["agent_rule_files"] = [
            {"path": e} if isinstance(e, str) else e for e in arf
        ]

    # readme_paste_blocks: {found, blocks} → {entries_count, entries}
    rpb = out.get("readme_paste_blocks")
    if isinstance(rpb, dict) and ("blocks" in rpb or "found" in rpb):
        blocks = rpb.get("blocks") or []
        out["readme_paste_blocks"] = {
            "entries_count": len(blocks),
            "entries": blocks,
        }

    return out


def migrate_phase_1(p1):
    if p1 is None:
        return p1
    out = dict(p1)
    out["pre_flight"] = migrate_pre_flight(out.get("pre_flight"))
    out["repo_metadata"] = migrate_repo_metadata(out.get("repo_metadata"))
    if "dependencies" in out:
        out["dependencies"] = migrate_dependencies(out["dependencies"])
    if "code_patterns" in out:
        out["code_patterns"] = migrate_code_patterns(out["code_patterns"])
    return out


def migrate_scorecard(phase_3_computed, phase_3_advisory, phase_4_structured_llm):
    """Move scorecard_cells phase_3 → phase_4 with new shape. Idempotent —
    if the form already has phase_3_advisory.scorecard_hints and
    phase_4_structured_llm.scorecard_cells, preserve them unchanged.
    Returns (new_phase_3, new_phase_3_advisory, new_phase_4)."""
    p3 = dict(phase_3_computed or {})
    p3a = dict(phase_3_advisory or {})
    p4 = dict(phase_4_structured_llm or {})

    old_cells = p3.pop("scorecard_cells", None) or {}

    # If the form already has phase_3_advisory.scorecard_hints populated, it's
    # already V1.2-migrated. Nothing to do on scorecard shape.
    existing_hints = p3a.get("scorecard_hints") or {}
    existing_p4_cells = p4.get("scorecard_cells") or {}
    if existing_hints and existing_p4_cells and not old_cells:
        return p3, p3a, p4

    # Otherwise rebuild from old_cells (V1.1 shape migration path)
    hints = {}
    for key in SCORECARD_QUESTION_KEYS:
        old = old_cells.get(key) or existing_hints.get(key) or {}
        hints[key] = {
            "color": old.get("color"),
            "short_answer": old.get("short_answer"),
            "signals": old.get("signals") or [],
        }

    new_cells = {}
    for key in SCORECARD_QUESTION_KEYS:
        old = old_cells.get(key) or existing_p4_cells.get(key) or {}
        new_cells[key] = {
            "color": old.get("color"),
            "short_answer": old.get("short_answer"),
            "rationale": old.get("rationale"),
            "edge_case": old.get("edge_case"),
            "suggested_threshold_adjustment": old.get("suggested_threshold_adjustment"),
            "computed_signal_refs": old.get("computed_signal_refs") or [],
            "override_reason": old.get("override_reason"),
        }
    p4["scorecard_cells"] = new_cells
    p3a["scorecard_hints"] = hints
    return p3, p3a, p4


def migrate_form(form):
    """Pure transform. Returns new form dict."""
    out = deepcopy(form)

    # Mark version
    out["schema_version"] = "V1.2"

    # Phase 1
    out["phase_1_raw_capture"] = migrate_phase_1(out.get("phase_1_raw_capture"))

    # Scorecard phase move
    new_p3, new_p3_advisory, new_p4 = migrate_scorecard(
        out.get("phase_3_computed"),
        out.get("phase_3_advisory"),
        out.get("phase_4_structured_llm"),
    )
    out["phase_3_computed"] = new_p3
    out["phase_3_advisory"] = new_p3_advisory
    out["phase_4_structured_llm"] = new_p4

    return out


def migrate_fixture(path: Path, dry_run: bool = False):
    """Idempotent: safe to re-run on V1.2 forms (transforms are no-ops on
    already-clean input, fix up any legacy-shape anomalies that survived
    an earlier migration pass)."""
    form = json.loads(path.read_text())
    new_form = migrate_form(form)
    if new_form == form:
        print(f"  ⊙ {path.name}: already V1.2-clean; no changes")
        return False
    action = "would migrate" if dry_run else "migrated"
    if not dry_run:
        path.write_text(json.dumps(new_form, indent=2) + "\n")
    print(f"  ✓ {path.name}: {action} to V1.2")
    return True


def update_provenance(migrated_names, dry_run: bool = False):
    prov_path = Path(PROVENANCE)
    prov = json.loads(prov_path.read_text())
    touched = []
    for name in migrated_names:
        entry = prov.get("fixtures", {}).get(name)
        if entry is None:
            print(f"  ⚠ provenance: {name} not found")
            continue
        if entry.get("schema_version") == "V1.2":
            continue
        entry["schema_version"] = "V1.2"
        entry.setdefault("migration_log", []).append({
            "from": "V1.1",
            "to": "V1.2",
            "migrated_at": datetime.now(timezone.utc).isoformat(),
            "script": "migrate-v1.1-to-v1.2.py",
        })
        touched.append(name)
    prov["last_updated"] = datetime.now(timezone.utc).date().isoformat()
    if dry_run:
        print(f"  ⋯ provenance: would update {len(touched)} entries (dry-run)")
        return
    if touched:
        prov_path.write_text(json.dumps(prov, indent=2) + "\n")
        print(f"  ✓ provenance: updated {len(touched)} entry(s) to V1.2")


def main():
    argv = sys.argv[1:]
    dry_run = "--dry-run" in argv
    repo_root = Path(__file__).resolve().parent
    print(f"V1.1 → V1.2 fixture migration ({'dry-run' if dry_run else 'live'})")
    migrated = []
    for rel in ACTIVE_FIXTURES:
        p = repo_root / rel
        if not p.exists():
            print(f"  ✗ {rel}: file not found")
            return 1
        if migrate_fixture(p, dry_run=dry_run):
            migrated.append(Path(rel).name)
    update_provenance(migrated, dry_run=dry_run)
    print(f"\nDone. Migrated {len(migrated)}/{len(ACTIVE_FIXTURES)} fixtures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
