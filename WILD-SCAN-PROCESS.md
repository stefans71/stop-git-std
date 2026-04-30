# Wild-Scan Process — what runs and what gets recorded

End-to-end map of running a V1.2 wild scan in this repo, from the moment a user says "scan `<owner>/<repo>`" to the moment the scan is committed and feeding back into the system. **Read this if you want to understand what touches what.**

For the operator-facing process documentation (decision points, gates, failure modes), see `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 (V2.5-preview pipeline). This file is the architecture-level overview.

---

## At a glance

```
                         ┌─ docs/repo-deep-dive-prompt.md         (V2.4 prompt — what to investigate)
                         ├─ docs/scan-schema.json                 (V1.2 — structural contract for form.json)
                         ├─ docs/scanner-design-system.css         (visual contract — 824 lines, mandatory)
                         ├─ docs/GitHub-Repo-Scan-Template.html    (DOM contract for delegated scans)
                         └─ docs/templates/ + templates-html/      (Jinja2 partials — render targets)

                         The above are the GOLD-STANDARD anchors.
                         A new scan flows through them.
                         ──────────────────────────────────────────

User: "scan owner/repo"
  │
  ▼
[Wizard, in CLAUDE.md "When the user says 'scan'"]
  Q1 Output: MD+HTML | HTML only | MD only
  Q2 Execution: continuous | delegated
  Q3 Shape: pick from reference table
  Q3a Pipeline: V2.4 (LLM-authored MD/HTML) | V2.5-preview (JSON-first; default for wild scans)
  │
  ▼
[Phase 1 — harness-driven]
  python3 docs/phase_1_harness.py owner/repo --out phase-1-raw.json
    ▸ gh api (repo metadata, contributors, branch protection, codeowners,
              workflows, releases, advisories, PRs, issues, commits, community)
    ▸ OSSF Scorecard API
    ▸ osv.dev (when manifests exist)
    ▸ gitleaks (if installed locally)
    ▸ tarball extraction → local grep for dangerous primitives + agent-rule files + injection scan
    ▸ README paste-scan + install-script analysis
    ▸ defensive-config derivation, monorepo detection, batch-merge detection

[Phase 2 — sanity validation]
  build_form.py (per-scan; lives at .scan-workspaces/<repo>/build_form.py)
    Sanity: SHA consistent, dates chronological, tarball nonempty, etc.

[Phase 3 — Python compute]
  Same build_form.py, calling docs/compute.py:
    ▸ compute_c20_severity                  (governance SPOF severity)
    ▸ compute_solo_maintainer               (top-1 share threshold)
    ▸ compute_methodology                   (versioning boilerplate)
    ▸ compute_coverage_status               (per-tool coverage rollup)
    ▸ compute_scorecard_cells (advisory)    (Q1/Q2/Q3/Q4 hint colors)
        + V13-3 C5: Q4 auto-fire from unsafe-deserialization + tool-loads-user-files
        + V13-1: ruleset-protection signal, oldest-open-security-item-age signal
    Output: phase_3_computed + phase_3_advisory.scorecard_hints sections

[Phase 4 — LLM-authored, structured]
  author_phase_4.py (per-scan; lives at .scan-workspaces/<repo>/author_phase_4.py)
    Author fills these dicts from harness data + reading the actual repo:
      ▸ FINDINGS              (F0..Fn, severity + threat model + action hints)
      ▸ EVIDENCE              (E1..En, facts only, with command + result)
      ▸ SCORECARD_CELLS       (Phase 4 authoritative; can override advisory)
      ▸ CATALOG_METADATA      (category, target_user, shape)
      ▸ REPO_VITALS, COVERAGE_DETAIL_ROWS, COVERAGE_GAPS
      ▸ PR_SAMPLE_ROWS, EXECUTABLE_FILE_INVENTORY
      ▸ ACTION_STEPS, TIMELINE_EVENTS, VERDICT_EXHIBITS, PRIORITY_EVIDENCE
      ▸ SECTION_LEADS, SPLIT_AXIS

  Override-explained gate: when a Phase 4 scorecard color differs from the
  Phase 3 advisory color, validator (--form mode) requires:
    ▸ rationale ≥50 chars
    ▸ computed_signal_refs non-empty (all IDs resolve against compute.SIGNAL_IDS)
    ▸ override_reason in 7-value enum:
        signal_vocabulary_gap | harness_coverage_gap |
        threshold_too_strict | threshold_too_lenient |
        missing_qualitative_context | rubric_literal_vs_intent | other

[Phase 4b — Python verdict]
  Same author_phase_4.py, calling docs/compute.py::compute_verdict
    Derives Critical | Caution | Clean from finding severities (deterministic).

[Phase 5 — LLM-authored prose]
  author_phase_5_6.py (per-scan; lives at .scan-workspaces/<repo>/author_phase_5_6.py)
    Author fills:
      ▸ phase_5_prose_llm.editorial_caption.text
      ▸ phase_5_prose_llm.per_finding_prose (2-3 paragraphs per finding)

[Phase 6 — assembly]
  Same author_phase_5_6.py:
    ▸ phase_6_assembly.{assembled, assembly_timestamp, provenance_complete,
                        evidence_refs_valid, field_count}

[Render]
  python3 docs/render-md.py   form.json --out docs/scans/catalog/GitHub-Scanner-<repo>.md
  python3 docs/render-html.py form.json --out docs/scans/catalog/GitHub-Scanner-<repo>.html

  The MD renderer is a 117-line Jinja2 shim over docs/templates/.
  The HTML renderer is a 135-line Jinja2 shim over docs/templates-html/.
  Both consume the same form.json — MD canonical / HTML may not add findings.

[Validate — gates that must pass]
  python3 docs/validate-scanner-report.py --markdown <md-file>           # exit 0
  python3 docs/validate-scanner-report.py --report   <html-file>         # exit 0
  python3 docs/validate-scanner-report.py --parity   <md> <html>         # exit 0 + zero WARNING: lines

  --form mode: schema validation + override-explained gate
  --bundle mode: findings-bundle.md citation validator (V2.4 path)

[Persist + record]
  cp .scan-workspaces/<repo>/form.json docs/scan-bundles/<repo>-<short-sha>.json
    (durability rule — bundle persists alongside MD+HTML for audit)

  Update docs/scanner-catalog.md
    Append a row: # | repo | HEAD SHA | Date | Verdict | Scope axis | Shape |
                  Methodology | Rendering pipeline | Artifacts links

  Update docs/v12-wild-scan-telemetry.md
    Append a §1 roster row + extend §10 changelog
    If new override fires, recompute §2 enum distribution

  Update CLAUDE.md "Current state" paragraph
    Bump entry count, wild-scan count, telemetry totals

  Update REPO_MAP.md §2.2
    Bump HEAD SHA + add session commit chain + bump catalog count

  Update AUDIT_TRAIL.md
    Add session checkpoint at top (HEAD, verification state, revert paths,
    decision points to preserve, token-burn observation if relevant)

  Update auto-memory at ~/.claude/projects/-root-tinkering-stop-git-std/memory/
    Update or create project_session<N>_status.md + bump MEMORY.md index

[Commit]
  git commit -m "Catalog entry <N>: <owner>/<repo> — <one-line summary>"
  Subsequent persistent-state commit:
  git commit -m "Session <N> persistent-state updates: AUDIT_TRAIL + CLAUDE + REPO_MAP"
```

---

## What gets created vs what gets read

| File | Read | Modified | Created |
|---|---|---|---|
| `docs/repo-deep-dive-prompt.md` | ✅ | | |
| `docs/scan-schema.json` | ✅ | | |
| `docs/scanner-design-system.css` | ✅ (embedded into HTML render) | | |
| `docs/GitHub-Repo-Scan-Template.html` | ✅ (delegated mode only — DOM contract) | | |
| `docs/templates/*.j2`, `docs/templates-html/*.j2` | ✅ | | |
| `docs/compute.py`, `docs/phase_1_harness.py` | ✅ | | |
| `docs/render-md.py`, `docs/render-html.py` | ✅ | | |
| `docs/validate-scanner-report.py` | ✅ | | |
| `.scan-workspaces/<repo>/{phase-1-raw.json, build_form.py, author_phase_*.py, form.json, head-sha.txt}` | | ✅ | ✅ |
| `docs/scans/catalog/GitHub-Scanner-<repo>.{md,html}` | | | ✅ |
| `docs/scan-bundles/<repo>-<sha>.json` | | | ✅ |
| `docs/scanner-catalog.md` | | ✅ (1 row added + meta-counter) | |
| `docs/v12-wild-scan-telemetry.md` | | ✅ (§1 row + §10 entry) | |
| `CLAUDE.md`, `REPO_MAP.md`, `AUDIT_TRAIL.md` | | ✅ (current-state paragraph bumps) | |
| `~/.claude/projects/.../memory/project_session<N>_status.md` | | ✅ or ✅ | sometimes |

The "DO NOT MODIFY" list is the union of everything in the **Read** column above.

---

## Pipelines (V2.4 vs V2.5-preview)

Two render pipelines exist. Either is acceptable for new scans; choose based on what you need.

| Pipeline | Phase 4 author surface | Render | When to use |
|---|---|---|---|
| **V2.4** | LLM authors MD + HTML directly from a `findings-bundle.md` synthesis. The reports are the canonical artifact. | LLM-typed | When clarity-of-prose-flow matters more than determinism (legacy default). |
| **V2.5-preview** | LLM authors a structured `form.json` conforming to `docs/scan-schema.json` V1.2. Renderers convert form → MD + HTML deterministically. | `render-md.py` + `render-html.py` (Jinja2) | When structural parity, deterministic re-render, or programmatic consumers (the upcoming Simple Report) matter. **Production-cleared 2026-04-20.** This is the default for wild scans. |

The `form.json` from V2.5-preview is the durable, machine-readable record of a scan. The MD + HTML are derived views. Future tooling (Simple Report, comparison tools, severity-distribution analysis) reads `form.json`, not the rendered files.

---

## Why this exists

Wild scans accumulate four kinds of value over time:

1. **The scan itself** — does this specific repo merit installation?
2. **Calibration data** — does the rule that fired on this repo fire correctly across the catalog? (Telemetry doc tracks this.)
3. **Shape coverage** — what languages / install-models / threat-models has the harness been exercised against? (Catalog `Shape / structural pattern` column.)
4. **Override patterns** — when does the deterministic Phase 3 advisory disagree with the LLM-authored Phase 4 cells, and why? (Drives V13-* board reviews and V1.2.x harness patches.)

The post-render persistence steps (catalog + telemetry + CLAUDE.md + REPO_MAP.md + AUDIT_TRAIL.md + memory) feed those four streams. Skipping them costs one scan's worth of value-accumulation. The rule is: every scan completes the full sequence above before the session closes.
