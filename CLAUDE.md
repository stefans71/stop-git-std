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

**Q2: Run it yourself or delegate?**
- Path A (default): you run all 6 phases in this session
- Path B: launch a fresh background agent with the handoff packet — you monitor

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

Then **execute the scan** following `docs/SCANNER-OPERATOR-GUIDE.md` (6-phase workflow).

### Path A execution
Follow phases 1-6 yourself. Read the Operator Guide for details on each phase. Key files:
- `docs/SCANNER-OPERATOR-GUIDE.md` — your process document
- `docs/repo-deep-dive-prompt.md` — what to investigate (Steps 1-8 + A/B/C)
- `docs/GitHub-Repo-Scan-Template.html` — HTML template with placeholders
- `docs/scanner-design-system.css` — **MANDATORY** CSS (816 lines, copy verbatim into HTML `<style>` block — do NOT truncate or rewrite)
- `docs/validate-scanner-report.py` — validator gate (`--report` mode, must exit 0)

### Path B execution
Assemble the §8.3 handoff packet and delegate to a background agent. Template prompt at `docs/board-review-data/path-b-test-prompt.md`. Adapt for the target repo + chosen reference scan + output mode. Monitor and verify when done.

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

- **MD is canonical.** Phase 4a produces MD first. Phase 4b derives HTML from it. HTML may not add findings absent from MD.
- **Facts, inference, synthesis are separate.** In the findings-bundle: evidence sections = facts only. Pattern recognition section = inference (tagged). Findings summary = synthesis (citing evidence). See Operator Guide §7.2 + §11.
- **Validator is the gate.** `python3 docs/validate-scanner-report.py --report <file>` must exit 0 on both files.
- **head-sha.txt is the first durable artifact.** Write it before any gh api call. On Phase 4 success, copy findings-bundle to `docs/board-review-data/scan-bundles/`.
- **Update the catalog** at `docs/scanner-catalog.md` after every completed scan.

## Repo structure

```
docs/
  SCANNER-OPERATOR-GUIDE.md         ← V0.1.1 operator guide (how to run end-to-end)
  Scan-Readme.md                    ← human-readable wizard + reference table
  scanner-design-system.css         ← MANDATORY CSS for all HTML scans (copy verbatim)
  repo-deep-dive-prompt.md          ← V2.3 post-R3 scanner prompt
  GitHub-Repo-Scan-Template.html    ← V2.3 aligned HTML template
  validate-scanner-report.py        ← validator gate
  scanner-catalog.md                ← live catalog of completed scans
  GitHub-Scanner-*.{html,md}        ← completed scan artifacts
  board-review-data/
    path-b-test-prompt.md           ← reusable Path B delegation prompt
    scan-bundles/                   ← durable findings-bundle copies
  board-review-*-consolidation.md   ← board review records
  repo-deep-dive-prompt-V*.md       ← prompt version archives
archive/                            ← old TypeScript static analyzer (historical)
```

## Current state

- Scanner prompt: V2.3 post-R3 (locked)
- Operator Guide: V0.1 (board-reviewed, Path B validated)
- Catalog: 6 scans (target: 10 for JSON-first migration)
- 2 rule-calibration observations toward Trigger #2

## Board reviews

3-model: Pragmatist (Claude Opus) + Systems Thinker (Codex) + Skeptic (DeepSeek V3.2). Run from `/tmp/board-*/`. Consolidation records in `docs/board-review-*-consolidation.md`.
