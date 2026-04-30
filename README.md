# stop-git-std

LLM-driven GitHub repo security scanner. Produces deep-dive investigation reports that tell non-engineers whether a repo is safe to install.

## How it works

An LLM (Claude Opus / Sonnet, OpenAI Codex GPT-5, or any frontier model with `gh` CLI access) investigates a GitHub repo using a structured prompt + a Python harness, then synthesises findings into a JSON form that drives deterministic MD + HTML report renders.

**Not a static analyzer.** The scanner reads governance signals, PR review patterns, maintainer backgrounds, CI workflow security, install-path verification, advisory hygiene, and agent-rule-file density — things that require judgment, not just pattern matching.

## Quick start

Open this repo in Claude Code (`CLAUDE.md` auto-loads project context), then say:

```
scan https://github.com/<owner>/<repo>
```

You'll be walked through a 4-question wizard (output mode, execution mode, shape reference, render pipeline) and the scan runs end-to-end. Output lands at `docs/scans/catalog/GitHub-Scanner-<repo>.{md,html}`.

To run without Claude Code (operator-driven):

```bash
# Phase 1 — automated harness
python3 docs/phase_1_harness.py <owner>/<repo> --out phase-1-raw.json

# Phase 2-6 — see WILD-SCAN-PROCESS.md + docs/SCANNER-OPERATOR-GUIDE.md §8.8
# Phase 4 + 5 are LLM-in-the-loop; templates at docs/scan-authoring-template/

# Validate after rendering
python3 docs/validate-scanner-report.py --report docs/scans/catalog/GitHub-Scanner-<repo>.html
```

## What's in this repo

| Path | Purpose |
|---|---|
| `WILD-SCAN-PROCESS.md` | End-to-end map of the scan flow — read first. |
| `CLAUDE.md` | Claude Code project context + scan wizard. |
| `REPO_MAP.md` | File/folder index + release status. |
| `AUDIT_TRAIL.md` | Checkpoint log + revert recipes. |
| `docs/SCANNER-OPERATOR-GUIDE.md` | V0.2 6-phase operator process (V2.4 + V2.5-preview pipelines). |
| `docs/Scan-Readme.md` | Standalone wizard for non-Claude-Code operators. |
| `docs/repo-deep-dive-prompt.md` | V2.4 scanner prompt (investigation + output-format spec). |
| `docs/scan-schema.json` | V1.2 JSON schema for the `form.json` contract. |
| `docs/scanner-design-system.css` | 824-line mandatory CSS. |
| `docs/GitHub-Repo-Scan-Template.html` | DOM template (delegated-mode contract). |
| `docs/phase_1_harness.py` · `compute.py` · `render-md.py` · `render-html.py` · `validate-scanner-report.py` · `compare-severity-distribution.py` | Pipeline. |
| `docs/templates/` · `templates-html/` | Jinja2 partials (V2.5-preview). |
| `docs/scan-authoring-template/` | Per-scan authoring script templates (Phase 4/5/6). |
| `docs/scans/catalog/` | All 27 catalog-referenced rendered scans. |
| `docs/scan-bundles/` | Form.json bundles from completed scans (durable record). |
| `docs/scanner-catalog.md` | Live catalog table — verdict, shape, methodology, pipeline. |
| `docs/v12-wild-scan-telemetry.md` · `v13-1-...` · `v13-3-analysis.md` | Cross-scan analysis. |
| `docs/External-Board-Reviews/` | 3-model FrontierBoard governance archive. |
| `docs/archive/` | Historical artifacts (older prompts, board reviews, migrations). See `docs/archive/README.md`. |
| `tests/` | Test suite — 414/414 passing across compute, validator, renderers, end-to-end, harness. |

## Catalog

27 completed scans across 12+ shape categories. Highlights from the V1.2 wild-scan series (entries 16–27):

| Repo | Verdict | Shape |
|---|---|---|
| ghostty-org/ghostty | Caution | Zig terminal emulator |
| shiyu-coder/Kronos | Critical (split) | Python ML foundation model |
| basecamp/kamal | Caution | Ruby deploy orchestrator |
| XTLS/Xray-core | Critical | Go network proxy |
| BatteredBunny/browser_terminal | Critical (split) | Browser extension + Go host |
| wezterm/wezterm | Caution | Rust terminal emulator |
| QL-Win/QuickLook | Caution | C# Windows shell extender |
| jtroo/kanata | Critical | Rust keyboard daemon |
| freerouting/freerouting | Critical | Java PCB auto-router |
| wled/WLED | Critical | ESP32 IoT firmware |
| WhiskeySockets/Baileys | Critical | Reverse-engineered WhatsApp Web lib |
| mattpocock/skills | Caution | Claude Code skills/plugin |

See `docs/scanner-catalog.md` for the full table; `docs/scans/catalog/_exemplar` (`GitHub-Scanner-ghostty-v12`) for the gold-standard rendered output.

## Governance

Every major change goes through a 3-model FrontierBoard review: Pragmatist (Claude Opus or Sonnet) + Systems Thinker (Codex GPT-5) + Skeptic (DeepSeek V4). Decisions land in `docs/External-Board-Reviews/<MMDDYY>-<topic>/CONSOLIDATION.md` with full dissent audit. SOP at `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`.

## Status

V2.5-preview pipeline production-cleared 2026-04-20 (V1.2 schema). 27 catalog entries, 414/414 tests passing. Active development.

## License

MIT
