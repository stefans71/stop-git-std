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
- **Workflow V2.5-preview (production-cleared 2026-04-20):** Phase 1 gathered by `docs/phase_1_harness.py` (not by LLM) — runs V2.4 prompt Steps 1-8 + A/B/C end-to-end (gh api + OSSF Scorecard + osv.dev + gitleaks + PyPI/npm/crates.io/RubyGems registries + tarball extraction + local grep + README paste-scan). Then LLM authors Phase 4 findings + Phase 5 prose from bundle, `docs/render-md.py` + `docs/render-html.py` produce MD + HTML deterministically. Step G validated on 3 pinned shapes (catalog entries 12-14) + first wild scan on microsoft/markitdown (Python monorepo — entry 15) fired production-clearance 2026-04-20. See §8.8. Either V2.4 (LLM-authored MD/HTML) or V2.5-preview is acceptable for new scans; V2.5-preview is the right choice when structural parity or deterministic reproducibility matters. Last reviewed: 2026-04-20 session 4.

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

As of 2026-04-20 session 7: Scanner prompt V2.4, Operator Guide V0.2, **scan-schema.json LIVE at V1.2** (with V13-1 enum expansion + V1.2.x signal widening), **385/385 tests passing**, **25 catalog entries** (11 V2.4 + 14 v2.5-preview: 3 Step G validation + **10 V1.2-schema wild scans** — entries 16–25). **10 V1.2 wild scans** cover an increasingly diverse shape space: terminal emulators (ghostty Zig + wezterm Rust), Python ML (Kronos), Python monorepo (markitdown), Ruby deploy orchestrator (kamal), Go network proxy (Xray-core), browser extension + Go native host (browser_terminal), C# Windows shell extender (QuickLook), Rust keyboard daemon (kanata), Java PCB autorouter (freerouting), **embedded ESP32 IoT firmware (WLED — first C++ + networked-home-LAN-device entry)**.

**V13-1 RESOLVED 2026-04-20 by owner directive** (see `docs/v13-1-override-telemetry-analysis.md`): `override_reason_enum` expanded 5→7 values (+`signal_vocabulary_gap`, +`harness_coverage_gap`). **V1.2.x signal widening landed same day** (commit `d803faf`): `SIGNAL_IDS` 23→25 (+`q1_has_ruleset_protection`, +`q2_oldest_open_security_item_age_days`); harness `dangerous_primitives.deserialization` regex widened. **D-6 severity-distribution comparator SHIPPED** at `docs/compare-severity-distribution.py` (Operator Guide §8.8.7; 23 tests; all 3 Step G pairs pass).

**Override telemetry across 10 V1.2 wild scans**: 8 total overrides; `signal_vocabulary_gap` modal at 62% (5 of 8); 3 zero-override scans (wezterm + QuickLook + kanata). 10/10 silent-fix pattern (0 published GHSA advisories across all 10). WLED adds the first **publicly-documented disclosure-handling failure** (issue #5340 → GHSA-2xwq-cxqw-wfv8, 74 days silent). Full cross-scan analysis at **`docs/v12-wild-scan-telemetry.md`** (MUST READ for any V1.2-era decision).

**V13-3 progress: 10 of 11 V1.2 wild scans** — 1 more triggers comparator-calibration analysis.

Phase 1 is **harness-driven**; V1.2 schema accepts harness output natively. Session 7 appends WLED entry 25 on top of `c6e7502`. Next: 1 more V1.2 wild scan to trigger V13-3; V1.2.x harness-patch backlog now includes Priority 1b (firmware default-no-auth + CORS-wildcard compound signal for Q4) per `v12-wild-scan-telemetry.md` §4.

**For everything else — look in `REPO_MAP.md`:**

- **If you need to find a file** → `REPO_MAP.md` §3 (File/folder index + release status per entry + last-touched)
- **If you need the current plan or next steps** → `REPO_MAP.md` §2 (Architecture, state, Step G queue, deferred ledger)
- **If you need to run the board** (agent invocation commands, failure modes, file staging, recent examples) → `REPO_MAP.md` §2.3 (Board runbook)
- **If you need to revert / recover from a regression** → `AUDIT_TRAIL.md` (checkpoint log with HEAD SHAs, verification state, revert recipes)
- **If you need the board review SOP** → `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
- **If you need the most recent board decision** → `docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` (Schema V1.2 design — D-7 + D-8 co-scheduled, 3 rounds + owner directives, 2026-04-20)
- **If you need the cross-scan V1.2 telemetry analysis** → `docs/v12-wild-scan-telemetry.md` (10-scan override-enum distribution + harness-patch candidates + V13-3 progress)
- **If you need the V13-1 owner-directive rationale** → `docs/v13-1-override-telemetry-analysis.md` (enum split from 5→7 values)
- **If you need the canonical architecture record** (8/8/4, 9-phase pipeline) → `docs/board-review-pipeline-methodology.md`
- **If you need what to investigate during a scan** → `docs/repo-deep-dive-prompt.md` (V2.4, investigation half lines 1-1090 + output-format spec lines 1106-1490)
- **If you need the end-to-end process document** → `docs/SCANNER-OPERATOR-GUIDE.md` (V0.2; §8.8 is the V2.5-preview pipeline)
- **If you're working on the V2.4 distributable package** (not the repo docs) → `github-scan-package-V2/` — note the docs there are intentionally V2.4-snapshot; see `REPO_MAP.md` §3.2 for drift notes.
