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
- **Workflow V2.5-preview (Step G passed on 3 shapes; production-preview):** LLM authors a `form.json` conforming to `docs/scan-schema.json` V1.1; `docs/render-md.py` + `docs/render-html.py` produce the MD + HTML deterministically. Step G acceptance cleared on 3 validation shapes: zustand-v3, caveman, Archon (catalog entries 12-14 tagged `v2.5-preview`). See §8.8 of `docs/SCANNER-OPERATOR-GUIDE.md` + `docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md`. **First unfixtured production scan pending before full production clearance** — continue to use V2.4 as the default production path until a wild scan on an unfixtured repo proves the pipeline works beyond the 3 known shapes. Last reviewed: 2026-04-20.

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

**Template is the DOM contract. Every delegated-scan brief MUST include this directive verbatim:**

> Fill `docs/GitHub-Repo-Scan-Template.html` verbatim. Do NOT invent new class names or redesign the DOM. Reference scans (`GitHub-Scanner-zustand-v3.html`, etc.) are *fill examples* — they show how `{{PLACEHOLDER}}` tokens get replaced with real content. They are NOT the contract. The template is. If a class you want to use is not defined in `docs/scanner-design-system.css`, you are about to invent one — stop and use the closest canonical class. Canonical anchors include: `.page`, `.hero`, `.scan-strip`, `.verdict-banner` with `data-dossier`, `.verdict-entry` + `.verdict-entry-headline` with `.good/.warn/.bad`, `.score-cell`/`.score-label`/`.score-value`, `.section-header` + `.section-number`, `.finding-card` with the F-ID INSIDE the `<h3>` (not a sibling span). The final `--parity` check must pass with ZERO warnings against the unmodified validator — warnings indicate DOM drift and require an HTML rewrite, not a validator widening.

**Why this rule exists:** 2026-04-19 multica scan (Sonnet 4.6 delegated) invented `report-header`/`-body`, `scorecard-cell`/`-question`, `section-num`, sibling `<span class="finding-id">` next to bare `<h3>`, and `<section class="verdict-section">` without the `.verdict-banner` wrapper. `--parity` flagged 2 warnings. First attempt was to widen validator regex (committed + reverted). Correct fix was to rewrite the HTML to canonical DOM. Principle: the validator stays narrow because the markup stays canonical.

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

## Current state (summary)

As of 2026-04-20 session 3: Scanner prompt V2.4, Operator Guide V0.2 (§8.8 implements Step G execution spec with FN-1..FN-9 + D-4/D-6/D-7), 289/289 tests passing, 14 catalog entries (11 V2.4 + 3 new `v2.5-preview` at entries 12-14), Phase 7 renderer Steps A-F complete. **Step G PASSED on 3 validation shapes** — zustand-v3 (commit `2c13324`), caveman (`ed68fae`), Archon (`be56935`). All 3 cleared all 7 acceptance gates (schema, `--report` MD+HTML, `--parity`, evidence refs, determinism, structural parity 6.1-6.6, phase-boundary contamination). SF1 scorecard-calibration resolved via 4-round board (archived at `docs/External-Board-Reviews/042026-sf1-calibration/`); 4 temporary-compatibility compute.py patches + U-11 Archon Q3 catalog correction applied; D-7 committed as post-Step-G architecture work. **V2.5-preview is NOT yet production-cleared** — first unfixtured wild scan on a shape outside {zustand, caveman, Archon} is the remaining trigger. Until then V2.4 stays the default production path.

**For everything else — look in `REPO_MAP.md`:**

- **If you need to find a file** → `REPO_MAP.md` §3 (File/folder index + release status per entry + last-touched)
- **If you need the current plan or next steps** → `REPO_MAP.md` §2 (Architecture, state, Step G queue, deferred ledger)
- **If you need to run the board** (agent invocation commands, failure modes, file staging, recent examples) → `REPO_MAP.md` §2.3 (Board runbook)
- **If you need to revert / recover from a regression** → `AUDIT_TRAIL.md` (checkpoint log with HEAD SHAs, verification state, revert recipes)
- **If you need the board review SOP** → `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
- **If you need the most recent board decision** → `docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md` (SF1 scorecard calibration, 4 rounds, 2026-04-20)
- **If you need the canonical architecture record** (8/8/4, 9-phase pipeline) → `docs/board-review-pipeline-methodology.md`
- **If you need what to investigate during a scan** → `docs/repo-deep-dive-prompt.md` (V2.4, investigation half lines 1-1090 + output-format spec lines 1106-1490)
- **If you need the end-to-end process document** → `docs/SCANNER-OPERATOR-GUIDE.md` (V0.2; §8.8 is the V2.5-preview pipeline)
- **If you're working on the V2.4 distributable package** (not the repo docs) → `github-scan-package-V2/` — note the docs there are intentionally V2.4-snapshot; see `REPO_MAP.md` §3.2 for drift notes.
