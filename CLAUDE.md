# stop-git-std — GitHub Repo Security Scanner

An LLM-driven deep-dive investigation tool that produces security scan reports for GitHub repos. Not a static analyzer — YOU do the investigation via `gh` CLI, synthesize findings, and render HTML + MD reports.

## When the user says "scan" — start the wizard

When the user asks to run a scan (says "scan", "scan <repo>", "investigate", "check this repo", or similar):

1. **If they gave a repo:** extract the `owner/repo` from whatever they provided:
   - Full URL: `https://github.com/NousResearch/hermes-agent` → `NousResearch/hermes-agent`
   - Short form: `NousResearch/hermes-agent` → use as-is
   - Just a name: `hermes-agent` → ask for the owner: "Who owns that repo? Give me `owner/repo`"
   - Verify it exists: `gh api repos/<owner>/<repo> --jq '.full_name'` — if 404, tell the user and ask again
2. **If they didn't give a repo:** ask: "What repo do you want to scan? Paste the GitHub URL or give me the `owner/repo` (e.g., `https://github.com/NousResearch/hermes-agent`)"

Then ask these questions interactively (one at a time, with defaults):

**Q1: Output mode**
- A: Both MD + HTML (default) — full audit trail
- B: HTML only
- C: MD only — cheapest, paste into any LLM for "should I install this?" guidance

**Q2: Execution mode — run it yourself or delegate?**
- continuous (default): you run all 6 phases in this session
- delegated: launch a fresh background agent with the handoff packet — you monitor

(Historical note: these were previously called "Path A" and "Path B"; catalog entries 1–10 use the `methodology-used: path-a` / `path-b` flags. The renamed terminology in CLAUDE.md + Operator Guide resolves a naming collision with the two rendering pipelines introduced in Q3a below.)

**Q3: Which existing scan is closest to this repo's shape?**
Show this table and let them pick (or pick for them if you can tell):
| Shape | Reference |
|---|---|
| JS/TS library (npm, no installer) | `GitHub-Scanner-zustand.html` |
| Compiled CLI with release binaries | `GitHub-Scanner-fd.html` |
| Agentic platform (server + CLI + web) | `GitHub-Scanner-Archon.html` |
| curl-pipe-from-main installer | `GitHub-Scanner-caveman.html` |
| Dense Claude Code skills/tools | `GitHub-Scanner-gstack.html` |
| Tiny / new / pre-distribution | `GitHub-Scanner-archon-board-review.html` |
| Not sure | Default to `GitHub-Scanner-fd.html` |

**Q3a: Rendering pipeline — V2.4 (recommended) or V2.5-preview (Step G operators only)?**
- **Workflow V2.4 (default, recommended):** LLM authors the MD + HTML reports directly from the findings-bundle. Proven on 10 completed catalog scans. Use this for anything that will enter the catalog or be shown to a user.
- **Workflow V2.5-preview (Step G validation only):** LLM authors a `form.json` conforming to `docs/scan-schema.json` V1.1; `docs/render-md.py` + `docs/render-html.py` produce the MD + HTML deterministically. Validated against back-authored fixtures only (zustand, caveman, archon-subset); live-pipeline validation is the open Step G work. See §8.8 of `docs/SCANNER-OPERATOR-GUIDE.md`. **Do NOT use for catalog or production scans.** Last reviewed: 2026-04-19.

Then **execute the scan** following `docs/SCANNER-OPERATOR-GUIDE.md` (6-phase workflow).

### Continuous-mode execution (legacy alias: Path A)
Follow phases 1-6 yourself. Read the Operator Guide for details on each phase. Key files (common to both rendering pipelines):
- `docs/SCANNER-OPERATOR-GUIDE.md` — your process document
- `docs/repo-deep-dive-prompt.md` — what to investigate (Steps 1-8 + A/B/C) + canonical output-format spec (lines ~1106-1490)
- `docs/validate-scanner-report.py` — validator gate (`--report` mode, must exit 0 on both MD and HTML; `--parity` zero errors + zero warnings for V2.5-preview)

Rendering-pipeline-specific files:

**Workflow V2.4 (recommended):**
- `docs/GitHub-Repo-Scan-Template.html` — HTML template with placeholders
- `docs/scanner-design-system.css` — **MANDATORY** CSS (824 lines, copy verbatim into HTML `<style>` block — do NOT truncate or rewrite)

**Workflow V2.5-preview (Step G only):**
- `docs/scan-schema.json` — V1.1 schema (investigation form structure)
- `tests/fixtures/{zustand,caveman,archon-subset}-form.json` — example forms to mirror
- `docs/render-md.py form.json --out GitHub-Scanner-<repo>.md`
- `docs/render-html.py form.json --out GitHub-Scanner-<repo>.html`
- See `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 for the phase-to-prompt mapping + triple-warning gate + rollback contract.

### Delegated-mode execution (legacy alias: Path B)
Assemble the §8.3 handoff packet and delegate to a background agent. Template prompt at `docs/board-review-data/path-b-test-prompt.md`. Adapt for the target repo + chosen reference scan + output mode + rendering pipeline. Monitor and verify when done.

## After the scan completes — ask the user

When a scan finishes (validator clean on all output files), present these options:

> **Scan complete.** `GitHub-Scanner-<repo>.md` and `.html` are ready. What would you like to do?
>
> 1. **View the report** — I'll open the HTML in your browser
> 2. **"Should I install this?"** — I'll summarize the key risks and give you a yes/no recommendation based on the findings
> 3. **Run another scan** — give me the next repo URL
> 4. **Send to board review** — launch a 3-model review on this scan's quality
> 5. **Update the catalog** — add this scan to `docs/scanner-catalog.md` and commit

Wait for the user's choice. If they pick option 2, read the `.md` file and give a concise, actionable answer: overall risk level, the top 1-3 things they should know, and whether you'd recommend installing (with conditions if applicable).

## Key rules

- **MD is canonical.** In Workflow V2.4, Phase 4a produces MD first and Phase 4b derives HTML from it. In Workflow V2.5-preview, both are rendered from the same `form.json` (MD-canonical enforced by the shared form contract). In either pipeline, HTML may not add findings absent from MD — this is the contract the `--parity` validator mode gates.
- **Facts, inference, synthesis are separate.** In the findings-bundle: evidence sections = facts only. Pattern recognition section = inference (tagged). Findings summary = synthesis (citing evidence). See Operator Guide §7.2 + §11. In V2.5-preview the same separation is enforced by the schema's phase boundaries (`phase_1_raw_capture` = facts, `phase_3_computed` + `phase_4_structured_llm` = inference, `phase_5_prose_llm` = synthesis; `phase_4b_computed` is the Python-derived verdict).
- **Validator is the gate.** `python3 docs/validate-scanner-report.py --report <file>` must exit 0 on both MD and HTML. V2.5-preview additionally requires `--parity` zero errors AND zero warnings before Step G acceptance.
- **head-sha.txt is the first durable artifact.** Write it before any gh api call. On Phase 4 success, copy findings-bundle to `docs/board-review-data/scan-bundles/`.
- **Update the catalog** at `docs/scanner-catalog.md` after every completed scan. Include the `rendering-pipeline` column (values: `v2.4` or `v2.5-preview`) alongside the existing `methodology-used` flag.

## Repo structure

```
docs/
  SCANNER-OPERATOR-GUIDE.md         ← V0.2 operator guide (how to run end-to-end)
  Scan-Readme.md                    ← human-readable wizard + reference table
  scanner-design-system.css         ← MANDATORY CSS for all V2.4 HTML scans (copy verbatim)
  repo-deep-dive-prompt.md          ← V2.4 scanner prompt (investigation + output-format spec)
  GitHub-Repo-Scan-Template.html    ← V2.4 HTML template (Workflow V2.4)
  validate-scanner-report.py        ← validator gate (--report, --parity, --markdown, --template)
  scan-schema.json                  ← V1.1 schema for Workflow V2.5-preview form.json
  render-md.py                      ← V2.5-preview MD renderer (Jinja2 shim)
  render-html.py                    ← V2.5-preview HTML renderer (Jinja2 shim)
  templates/                        ← V2.5-preview MD Jinja2 partials
  templates-html/                   ← V2.5-preview HTML Jinja2 partials
  scanner-catalog.md                ← live catalog of completed scans
  GitHub-Scanner-*.{html,md}        ← completed scan artifacts (10 V2.4 scans as of 2026-04-19)
  External-Board-Reviews/           ← archived board review records (R1-R4 consolidations)
  board-review-data/
    path-b-test-prompt.md           ← reusable delegated-mode prompt (legacy Path B)
    scan-bundles/                   ← durable findings-bundle copies
  board-review-*-consolidation.md   ← older flat-file board review records
  repo-deep-dive-prompt-V*.md       ← prompt version archives
tests/
  fixtures/                         ← V1.1-compliant back-authored fixtures (zustand, caveman, archon-subset)
  test_render_md.py / test_render_html.py / test_validator.py / ...
github-scan-package-V2/             ← V2.4 distributable package (predates V2.5-preview; validator synced to repo as of commit 60e0bf2)
archive/                            ← old TypeScript static analyzer (historical)
```

## Current state

- Scanner prompt: V2.4 (investigation + output-format spec)
- Operator Guide: V0.2 (V2.5-preview pipeline documented as Step-G-experimental in §8.8)
- Catalog: 10 V2.4 scans; 0 V2.5-preview scans (Step G is the first live run)
- Phase 7 renderer plan A→G: Steps A-F complete (ce698d4). Step G next — see `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`

## Board reviews

3-model: Pragmatist (Claude Opus 4.7 or Sonnet 4.6 when Opus wrote the artifact) + Systems Thinker (Codex GPT-5 as `llmuser` from `/tmp`) + Skeptic (DeepSeek V4 via `qwen -y --model deepseek-chat` from repo dir). Recent consolidations in `docs/External-Board-Reviews/<MMDDYY>-<topic>/CONSOLIDATION.md`; older flat-file records at `docs/board-review-*-consolidation.md`. Full SOP at `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`.
