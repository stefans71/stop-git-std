#!/usr/bin/env python3
"""D-6 severity-distribution comparison — automates Operator Guide gate 6.2.

Purpose
-------
For a V2.5-preview scan run at a pinned V2.4 SHA, compare finding severities
cell-by-cell against the V2.4 comparator. Produces the severity-mapping
table that §8.8.7 previously required operators to produce manually, and
exits non-zero on any mismatch.

Per Operator Guide §8.8 gate 6.2:
  "Severity per F-ID — each F-ID's `severity` matches V2.4 comparator's
   severity for the same F-ID. Zero inversions, zero downgrades, zero
   upgrades."

This automation was D-6 on the post-Step-G commitments list; per
§8.8.7 it was "NOT indefinitely deferred" and owed before the first
production V2.5-preview scan beyond the 3 validation shapes. Landed
2026-04-20 as part of the V13-1 follow-up cycle.

Usage
-----
  python3 docs/compare-severity-distribution.py \\
      --v24 docs/GitHub-Scanner-zustand-v3.md \\
      --v25 docs/GitHub-Scanner-zustand-v3-v25preview.md \\
      [--target zustand-v3] \\
      [--out .board-review-temp/step-g-execution/severity-mapping-zustand-v3.md]

Each side accepts either a rendered .md report or a .json form.json bundle.
The script detects shape by file extension. Exit 0 when every F-ID in V2.4
maps to a matching severity in V2.5-preview. Exit 1 on any mismatch, missing
finding, or extra finding.

Not a gate on finding-inventory 6.1 (that is handled by the --parity mode
of `docs/validate-scanner-report.py`); this script focuses on 6.2 severity
mapping assuming inventory already aligned.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# V2.4 + V1.2 share this severity vocabulary (matches compute.py + scan-schema.json).
SEVERITY_ENUM = {"Critical", "Warning", "Info", "OK"}

# Primary format (used by 9 of 10 V2.4 scans + all V2.5-preview scans):
#   ### F0 — Warning · Structural · ...    (em dash OR hyphen)
FINDING_HEADER_RE = re.compile(
    r"^###\s+(F\d+)\s*[—\-]\s*(Critical|Warning|Info|OK)\b"
)

# Fallback format (zustand-v3 entry 10 uses summary bullets instead of
# section headers):
#   - **Warning:** ... (F0)
FINDING_BULLET_RE = re.compile(
    r"^\s*-\s+\*\*(Critical|Warning|Info|OK):\*\*.*?\((F\d+)\)\s*$"
)


def extract_from_markdown(path: Path) -> dict[str, str]:
    """Parse a rendered MD report; return {F-ID: severity}.

    Tries the section-header format first (primary). Falls back to
    summary-bullet format if section headers yield zero findings.
    """
    out: dict[str, str] = {}
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = FINDING_HEADER_RE.match(line)
        if m:
            f_id, severity = m.group(1), m.group(2)
            if f_id in out:
                raise ValueError(
                    f"{path.name}: duplicate finding id {f_id} "
                    f"(first seen as {out[f_id]}, now as {severity})"
                )
            out[f_id] = severity

    if out:
        return out

    # Fallback: summary-bullet scans (entry 10 zustand-v3 shape).
    for line in text.splitlines():
        m = FINDING_BULLET_RE.match(line)
        if m:
            severity, f_id = m.group(1), m.group(2)
            if f_id in out:
                raise ValueError(
                    f"{path.name}: duplicate finding id {f_id} "
                    f"(first seen as {out[f_id]}, now as {severity})"
                )
            out[f_id] = severity
    return out


def extract_from_form_json(path: Path) -> dict[str, str]:
    """Parse a form.json bundle; return {F-ID: severity}."""
    form = json.loads(path.read_text(encoding="utf-8"))
    entries = (
        form.get("phase_4_structured_llm", {})
        .get("findings", {})
        .get("entries", [])
    )
    out: dict[str, str] = {}
    for entry in entries:
        f_id = entry.get("id")
        severity = entry.get("severity")
        if not f_id or not severity:
            continue
        if f_id in out:
            raise ValueError(
                f"{path.name}: duplicate finding id {f_id} "
                f"(first seen as {out[f_id]}, now as {severity})"
            )
        if severity not in SEVERITY_ENUM:
            raise ValueError(
                f"{path.name}: finding {f_id} has unknown severity "
                f"{severity!r}; valid = {sorted(SEVERITY_ENUM)}"
            )
        out[f_id] = severity
    return out


def extract(path: Path) -> dict[str, str]:
    """Dispatch by file extension."""
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return extract_from_markdown(path)
    if suffix in {".json"}:
        return extract_from_form_json(path)
    raise ValueError(
        f"{path.name}: unsupported extension {suffix!r}; expected .md or .json"
    )


def compare(
    v24: dict[str, str], v25: dict[str, str]
) -> tuple[list[tuple[str, str, str, bool]], dict[str, int]]:
    """Return (rows, summary) where each row is (F-ID, v24_sev, v25_sev, match).

    F-IDs are the union of both inputs, sorted by numeric suffix. Missing-side
    severities render as the string '—'.
    """
    all_ids = sorted(
        set(v24) | set(v25),
        key=lambda s: int(s[1:]) if s[1:].isdigit() else 0,
    )
    rows: list[tuple[str, str, str, bool]] = []
    mismatches = 0
    missing_v25 = 0
    missing_v24 = 0
    for f_id in all_ids:
        v24_sev = v24.get(f_id, "—")
        v25_sev = v25.get(f_id, "—")
        if f_id not in v24:
            missing_v24 += 1
            match = False
        elif f_id not in v25:
            missing_v25 += 1
            match = False
        else:
            match = (v24_sev == v25_sev)
            if not match:
                mismatches += 1
        rows.append((f_id, v24_sev, v25_sev, match))

    summary = {
        "total": len(all_ids),
        "matches": sum(1 for _, _, _, m in rows if m),
        "mismatches": mismatches,
        "missing_in_v25": missing_v25,
        "missing_in_v24": missing_v24,
    }
    return rows, summary


def render_table(
    rows: list[tuple[str, str, str, bool]],
    summary: dict[str, int],
    target_name: str,
    v24_path: Path,
    v25_path: Path,
) -> str:
    lines: list[str] = []
    lines.append(f"# Severity distribution — {target_name}")
    lines.append("")
    lines.append(f"- **V2.4 comparator:** `{v24_path}`")
    lines.append(f"- **V2.5-preview target:** `{v25_path}`")
    lines.append("")
    lines.append("| F-ID | V2.4 severity | V2.5-preview severity | match? |")
    lines.append("|---|---|---|---|")
    for f_id, v24, v25, match in rows:
        mark = "✓" if match else ("✗ MISSING" if (v24 == "—" or v25 == "—") else "✗ MISMATCH")
        lines.append(f"| {f_id} | {v24} | {v25} | {mark} |")
    lines.append("")
    lines.append(
        f"**Summary:** {summary['matches']}/{summary['total']} match"
        + (f" · {summary['mismatches']} mismatch" if summary["mismatches"] else "")
        + (f" · {summary['missing_in_v25']} missing in V2.5" if summary["missing_in_v25"] else "")
        + (f" · {summary['missing_in_v24']} missing in V2.4" if summary["missing_in_v24"] else "")
    )
    ok = (
        summary["mismatches"] == 0
        and summary["missing_in_v25"] == 0
        and summary["missing_in_v24"] == 0
    )
    lines.append("")
    lines.append("**Result:** " + ("✓ GATE 6.2 PASS" if ok else "✗ GATE 6.2 FAIL"))
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="D-6 severity-distribution comparator (Operator Guide gate 6.2)."
    )
    ap.add_argument("--v24", required=True, type=Path,
                    help="Path to V2.4 comparator .md or .json")
    ap.add_argument("--v25", required=True, type=Path,
                    help="Path to V2.5-preview .md or .json")
    ap.add_argument("--target", default=None,
                    help="Target name for the report header (default: inferred from --v25 stem)")
    ap.add_argument("--out", default=None, type=Path,
                    help="Write the severity-mapping table to this path in addition to stdout")
    args = ap.parse_args(argv)

    for label, path in (("--v24", args.v24), ("--v25", args.v25)):
        if not path.exists():
            print(f"error: {label} path does not exist: {path}", file=sys.stderr)
            return 2

    try:
        v24 = extract(args.v24)
        v25 = extract(args.v25)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    target_name = args.target or args.v25.stem.replace("GitHub-Scanner-", "").replace("-v25preview", "")
    rows, summary = compare(v24, v25)
    report = render_table(rows, summary, target_name, args.v24, args.v25)

    sys.stdout.write(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"\nWrote mapping to {args.out}", file=sys.stderr)

    if summary["mismatches"] or summary["missing_in_v25"] or summary["missing_in_v24"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
