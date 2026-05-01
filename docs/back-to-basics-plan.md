# Back-to-Basics Calibration Rebuild — Plan

**Owner goal:** rebuild scoring + cell calibration so ~90% of severity decisions become programmatic (driven by harness signals + shape classification), the OSS-default solo-maintainer pattern lands at ~5–6 out of 10 severity (not ~9), and the resulting MD report leads LLM consumers to calibrated "should I install this?" answers. Then build a Simple Report HTML on top of the new MD baseline.

**Started:** 2026-05-01 (session 8 close / session 9 open)
**Plan owner:** stefans71 (decisions); Claude Opus 4.7 (execution)

---

## How to resume after `/compact` or new session

1. CLAUDE.md auto-loads → it points at this file.
2. Read this file's **§ Current state** block below — it tells you the active phase, the active step, the next concrete action, and what you're blocked on (if anything).
3. If a fork is in flight, do not duplicate its work — wait for the completion notification or check `~/.claude/projects/-root-tinkering-stop-git-std/memory/` for fork-handoff notes.
4. Read the deliverable from the previous phase before starting the next one (named in each phase block below).
5. Each phase ends with one or more git commits + a § Current state update. If the last commit's HEAD doesn't match the § Current state pointer, re-read the commit message for the truth.

When the user says "continue" — start at the **next concrete action** under § Current state.

---

## § Current state (UPDATE AT EACH COMMIT — single source of truth)

**This block is your resumption packet.** It is the only thing you need to read after `/compact` to know what to do next. If something here is wrong or stale, fix it before proceeding.

### HEAD + branch
- **HEAD:** `f2485fc` on `chore/calibration-md-verification` (Phase 6 commit 1 — verification doc; on top of Phase 5 chain `5d4ed3b` ← `17bd4e3` ← `d03c04b` ← `543a1f5` ← `0325204` ← `5ae3dcd` ← Phase 4 chain to `e6b0a3b`). `origin/main` HEAD is `69a7d5c` (the §Current state self-update from end of Phase 5). Phase 6 branch not pushed; awaits owner sign-off before merge.
- **Pre-render tag:** `pre-calibration-rerender` set at `e6b0a3b` — Phase 5 rollback anchor; preserved.
- **Tree:** clean (after this §Current state commit lands).

### Phase + step
- **Phase 6 — COMPLETE on local branch, AWAITING OWNER SIGN-OFF FOR MERGE.** 5 cold-fork consumer tests run on rendered MD for catalog entries 16, 20, 24, 26, 27. **Result: 5 of 5 match.** Pass bar (≥4 of 5) cleared.
- **Next phase: Phase 7 — Simple Report HTML on top of calibrated MD.** See plan §Phase 7 for spec. Do NOT start Phase 7 until owner has signed off on Phase 6 + merged this branch.

### Phase 6 deliverables (on `chore/calibration-md-verification`, NOT yet on main)
| SHA | One-line summary |
|---|---|
| `f2485fc` | Phase 6 commit 1: `docs/calibration-rebuild-md-verification.md` (260 lines; per-scan detail + Q3 attribution analysis + failure-mode coverage table) |
| *(this commit)* | Phase 6 commit 2: §Current state update for Phase 6 close |

### Phase 6 outcome metrics
- **Match count:** 5 of 5 (pass bar ≥4)
  - 16 ghostty Caution → YES-WITH-CAVEATS ✓
  - 26 Baileys Critical → NO ✓
  - 27 skills Caution → YES-WITH-CAVEATS ✓
  - 20 browser_terminal Critical → NO ✓
  - 24 freerouting Critical → NO ✓
- **Failure modes covered:**
  - Over-cautious skill collections (entry 27 V13-3 `missing_qualitative_context` override) — survived cold read.
  - Under-cautious genuine criticals (Baileys, browser_terminal, freerouting) — all three returned NO with calibrated reasoning.
- **Q3 FALLBACK regression — did it skew the test?** No. Rendered MD is sourced from `phase_4_structured_llm.scorecard_cells` (LLM-authored), NOT from `phase_3_advisory.scorecard_hints`. The Phase 5 Q3 advisory drift lives in `phase_3` only and does NOT propagate to consumer-facing MD today. The cold-fork test therefore did NOT stress-test calibration v2 Q3 rule changes — it validated that Phase 4-era LLM cells still lead consumers to the calibrated verdict. See verification doc §"Q3 FALLBACK regression — did it actually matter for this test?" for analysis + Phase 7 implications.

### Phase 6 carry-forward into Phase 7
The gate 6.3 backlog (7 cells across 6 entries: 16 ghostty Q3, 18 kamal Q3, 21 wezterm Q3, 24 freerouting Q3, 25 WLED Q1+Q3, 27 skills Q3) is a `phase_3` ↔ `phase_4` divergence the validator's `--form` mode will eventually demand resolution on. Phase 7 should pick one of:
- **(a)** re-author Phase 4 cells to align with calibration v2 advisory (and accept consumer-facing reports will shift on those 5 entries),
- **(b)** add `override_reason` to existing Phase 4 cells to keep current MD semantics with rule-driven advisory,
- **(c)** soften calibration v2 Q3 rules (introduce a RULE-5-style softener for repos with partial disclosure signals so advisory naturally lands amber, matching legacy + matching the LLM cells already in place).

The cold-fork test does not pick between these — but the test result (5/5 match against current MD) suggests **(b)** or **(c)** are the conservative choices, since (a) would shift consumer-facing semantics that the Phase 6 test already validated as correct.

### Out of scope for Phase 5 (unchanged on disk; carried from prior phase block)
- Entries 1-11: V2.4 era hand-authored against V1.1 schema; no V1.2 form.json exists
- Entries 12-14 (Step G pilots): authoritative phase_4 in `.board-review-temp/step-g-execution/*.json` (V1.1); migration + re-authoring is its own workstream
- Entry 15 (markitdown): V1.2 form.json has empty `phase_4_structured_llm.scorecard_cells` (LLM cells were authored to a `.md` sidecar bundle); re-render would regress Q2

### Next concrete action when work resumes (after owner sign-off)

**Owner action required:** review `docs/calibration-rebuild-md-verification.md` §"Owner sign-off" + approve merge of `chore/calibration-md-verification` to `main` (no-ff).

**After merge — Phase 7: Simple Report HTML.** Per plan §Phase 7:
- **Goal:** the user-facing simple HTML output the project always anticipated, built on calibrated data.
- **Branch:** `feat/simple-report` from `main` (post-Phase-6-merge HEAD).
- **Deliverable:** per `docs/simple-report-concept.md` — `docs/templates-simple/simple-report.html.j2` + `docs/templates-simple/simple-report.md.j2` + `docs/render-simple.py` + `docs/threat-explainer-library.json` + `docs/tool-branding.json`. Wizard Q1 gains option C "Simple."
- **Phase 7 carry-forward:** the Phase 6 carry-forward (gate 6.3 backlog resolution choice — re-author / override_reason / soften rules) should be addressed alongside the Simple Report work, not before it.

### Token budget note
Each Phase step (one commit) should complete within **~200k tokens**. If you're approaching that limit, commit what's done, update §Current state to reflect the partial state, and stop for `/compact`. Do NOT push past the limit hoping to wrap up — context degrades rapidly past 200k and you'll make decisions you'd reject with a fresh context window.

### What was finished before the current phase (high-level only; details in commit history)
Phase 0 audit, Phase 1 calibration design, Phase 2 board review, Phase 3 calibration v2 implementation, Phase 4 template-side derivation, Phase 5 calibration v2 rerender, Phase 6 MD calibration verification (this branch — pre-merge). Phases 0-5 landed on origin/main. Phase 6 awaits owner sign-off + merge. Phase 3 outcome detail in `docs/calibration-impl-notes.md`. Phase 3-5 commit lists in `AUDIT_TRAIL.md` (after that file's session 11 update). **You should not need to read these to do current phase work** — they are reference material, not resumption material.

---

## Phases (linear; each has explicit deliverables + commits + completion criteria)

### Phase 0 — Distribution audit  *(COMPLETE)*

**Goal:** empirical baseline of what the 27 catalog scans actually look like — what cell colors fire on what shapes, where overrides cluster, where the rule table is over-calling vs accurately calling.

**Deliverable:** `docs/calibration-audit.md` (written by the fork). 10-section structure (catalog overview, shape distribution, cell distribution, Q1/Q3 firing patterns, C20 distribution, solo-maintainer prevalence, override clusters, cross-shape observations, recommended rule-table starting points).

**Inputs read:** `docs/scanner-catalog.md`, the 12 V1.2 form.json bundles in `docs/scan-bundles/*.json`, `docs/v12-wild-scan-telemetry.md`.

**Inputs NOT read:** rendered scan outputs (docs/scans/catalog/) — derived data; source of truth is bundles.

**Commits:**
1. Add this plan file + CLAUDE.md pointer.
2. (After audit fork completes) commit `docs/calibration-audit.md`.

**Completion criteria:**
- `docs/calibration-audit.md` exists, is non-trivial, and includes §10 with at least 5 specific rule-table change proposals.
- Owner has read the audit and given a thumbs-up to proceed (or course-correction).

---

### Phase 1 — Calibration design

**Goal:** translate audit findings into a concrete proposed rule table + shape-classifier helper. No code yet.

**Deliverable:** `docs/calibration-design-v2.md`. Sections:
1. Goals + non-goals (severity at OSS-median; shape-aware rules; preserve override mechanism for genuine outliers; ~90% programmatic).
2. New shape categories (closed enum proposal — drawn from existing `catalog_metadata.shape` text + grouping into 6–10 buckets).
3. Proposed `compute.classify_shape(form)` signature + heuristic logic.
4. Proposed `compute.compute_finding_severities(findings_signals, shape)` signature + rule table per shape × per-question.
5. New cell short-answer language (replaces "❌ No — ..." with calibrated phrases like "Typical for solo OSS — no formal review gate, but maintainer has public reputation"). Per shape × per cell color.
6. Migration plan: how 27 existing scans get re-rendered against the new rules; what we expect to change in each verdict.
7. Questions for board review (the design's open calls — what we want the board to weigh in on).

**Inputs:** `docs/calibration-audit.md` (Phase 0 output).

**Commits:**
1. Commit `docs/calibration-design-v2.md`.

**Completion criteria:** owner approves the design (or revises) before Phase 2.

---

### Phase 2 — Board review on the calibration design

**Goal:** 3-model FrontierBoard governance review on the rule-table proposal. This is calibration, not visual — board scope is appropriate.

**Deliverable:** `docs/External-Board-Reviews/<MMDDYY>-calibration-rebuild/CONSOLIDATION.md` with 3 rounds + dissent audit (per SOP §4).

**Process:** standard SOP — see `REPO_MAP.md` §2.3 board runbook.
- Pragmatist: Sonnet 4.6 (Opus authored the design — same-model blind spot rule).
- Systems Thinker: Codex GPT-5 (sudo -u llmuser from /tmp).
- Skeptic: DeepSeek V4 (qwen -y from repo dir).
- Brief at `.board-review-temp/calibration-rebuild/r1-brief.md`.

**Commits:**
1. Archive: `docs/External-Board-Reviews/<MMDDYY>-calibration-rebuild/CONSOLIDATION.md` + r1/r2/r3 briefs + agent responses + dissent audit.
2. Update `docs/External-Board-Reviews/README.md` master index.

**Completion criteria:** all 3 R3 votes recorded; pre-archive dissent audit has zero silent drops; CONSOLIDATION includes FIX NOW + DEFER + dissent items + owner directives.

---

### Phase 3 — Implementation: shape classifier + rule table

**Goal:** build the deterministic severity engine.

**Deliverables:**
- `docs/compute.py` extended with `classify_shape(form)` + `compute_finding_severities(...)` + per-shape rule tables.
- Existing `compute_scorecard_cells()` becomes a thin shim over the new rule table OR is preserved alongside as advisory while the new function takes authority — design call from Phase 1.
- Tests at `tests/test_compute_calibration.py` covering: each shape × each cell × each rule branch + a per-existing-scan regression suite (load form.json from `docs/scan-bundles/`, run new compute, assert it matches what owner expected per Phase 1 §6 migration plan).

**Branch:** `chore/calibration-rebuild-impl`.

**Commits (incremental):**
1. Add shape classifier + tests.
2. Add per-shape rule table + tests.
3. Wire new severity engine into `compute_scorecard_cells()` (or replacement); maintain backwards-compat for callers.
4. Update `docs/scan-schema.json` if any new fields are needed (probably yes — `phase_4_structured_llm.shape_classification` or similar). If schema changes, run `migrate-v1.1-to-v1.2.py` analog or document migration.
5. Final integration commit + 414/414 tests + new tests passing.

**Completion criteria:** test suite passes (likely 450+/450+); existing scans' bundles still validate against schema; the new severity engine produces deterministic output for every existing bundle.

---

### Phase 4 — Implementation: mechanical reformatting moves to template-side

**Goal:** stop having the LLM re-author harness data into table rows. REPO_VITALS, COVERAGE_DETAIL, PR_SAMPLE table rows all derive deterministically from `phase_1_raw_capture`.

**Deliverables:**
- `docs/render-md.py` + `docs/render-html.py` extended with helper functions `derive_repo_vitals(p1)`, `derive_coverage_detail(p1)`, `derive_pr_sample(p1)`.
- Templates updated to use derived data when phase_4 doesn't supply it (LLM still allowed to override for shape-specific row reordering or commentary).
- `docs/scan-authoring-template/author_phase_4.py.template` updated — those sections are now optional / minimal.
- New tests in `tests/test_render_md.py` + `tests/test_render_html.py` for the derivation helpers.

**Why no `derive_evidence_facts`** *(grounded decision, 2026-05-01 session 11):* Original plan listed a 4th helper for "EVIDENCE table rows." Verification on disk (3 V1.2 scans: skills, ghostty-v12, Baileys; 30 evidence entries total) showed section 07 is a list of card-style entries, not a table — and every entry is LLM-authored synthesis combining multiple harness signals with bespoke framing (e.g. skills E1 "mattpocock holds 87.3% top-contributor commit share + TESTPERSONAL is almost certainly a maintainer-owned test/dev account"). Zero entries are pure boilerplate facts. Adjacent sections (02A executable file inventory) are partial mechanical / partial synthesis but not a clean fit either. Conclusion: drop the 4th helper rather than force-fit. Phase 4 ships 3 helpers + wires 3 sections (§03 PR sample, §05 repo vitals, §06 coverage detail). Section 07 stays 100% LLM-authored.

**Branch:** `chore/template-side-derivation` from `main` (Phase 3 outcome was merge to main; new branch is the clean answer to the "TBD by phase 3 outcome" choice).

**Commits (incremental):**
1. Add derivation helpers + tests.
2. Wire helpers into renderers + adjust templates.
3. Update authoring template + scan-workflow doc.

**Completion criteria:** re-rendering a recent V1.2 scan (e.g. skills) produces the same table content with the LLM authoring zero rows. Token-count delta on per-scan authoring should be measurable (target: ~50% reduction in author_phase_4.py token weight).

---

### Phase 5 — Re-render 12 catalog scans (entries 16-27) + diff

**Goal:** validate the new calibration against the existing catalog. Some verdicts may shift (intentional). We document each shift + owner reviews before commit.

**Scope:** 12 entries (16-27) — V1.2 wild scans with complete `form.json` bundles (full phase_4 LLM authoring). Out-of-scope entries:
- Entries 1-11: V2.4 era hand-authored against V1.1 schema, no V1.2 `form.json` exists.
- Entries 12-14 (Step G pilots): authoritative phase_4 in `.board-review-temp/step-g-execution/*.json` (V1.1); would require schema-upgrade + Phase 4 re-authoring.
- Entry 15 (markitdown): V1.2 form.json in `.scan-workspaces/markitdown/` has empty `phase_4_structured_llm.scorecard_cells` (LLM cells were authored to a `.md` sidecar bundle); re-rendering produces a Q2 regression.

**Deliverables:**
- `docs/calibration-rebuild-rerender-comparison.md` — for each entry 16-27: old verdict / new verdict / cell-color delta / rationale (one-line per scan). Entries 1-15 listed in a separate "out of scope" block. Includes "Phase 6 input — gate 6.3 backlog" section documenting the 6 advisory/LLM mismatches that need Phase 4 re-authoring.
- Re-rendered MD + HTML for entries 16-27 → committed to `docs/scans/catalog/` REPLACING the existing files (per the calibration cutover; old versions remain in git history).
- `docs/phase_5_recompute.py` + `docs/phase_5_build_comparison.py` — one-shot migration scripts (kept in repo for traceability).
- `docs/phase_5_comparison_data.json` — structured comparison data driving the doc.
- `docs/compute.py` — defensive patches: `_derive_signals_from_form` coerces naive datetime to UTC, `compute_solo_maintainer` is None-safe on `contributions`. Both are general bug fixes surfaced by Phase 5 inputs.
- `tests/test_validator_v2_rule_id.py` — `_minimal_v12_form()` strips v2 fields + normalizes advisory colors; required because Phase 5 mutates the ghostty bundle that this test uses as scaffold.

**Pre-commit gate:** owner reviews the comparison doc and signs off on each verdict shift.

**Branch:** `chore/calibration-rebuild-rerender` from `main` at `e6b0a3b` (post-Phase 4 merge + §Current state hygiene). Pre-render tag `pre-calibration-rerender` set at the same SHA before any rerender work, since this phase mutates committed scan outputs.

**Commits:**
1. Add comparison doc + the re-rendered scan files + catalog updates in one cohesive commit.
2. Update CLAUDE.md current-state paragraph + REPO_MAP.md catalog count if it changed.

**Completion criteria:** owner signs off on the rerender comparison; 587+/587+ tests pass; validator clean on every re-rendered file; `--parity` zero-warning on every MD/HTML pair.

---

### Phase 6 — MD calibration verification (LLM consumer test)

**Goal:** prove the calibrated MD leads LLM consumers to accurate "should I install this?" answers — not the over-cautious failure mode we identified in session 8.

**Deliverable:** `docs/calibration-rebuild-md-verification.md`. For each of 5 selected scans (1 each across shape categories: Caution-OSS-default like ghostty / Critical-genuine like Baileys / Critical-via-governance-only / Caution-skill-collection like skills / Critical-supply-chain like browser_terminal), run the MD through a fork and ask "should I install this?" cold (no project context). Compare the fork's answer to the calibrated answer.

**Inputs:** the 5 re-rendered MD scans from Phase 5.

**Process:** fork per scan with isolation. Fork prompt: "You're an LLM consumer. The user pasted this MD report and asked 'should I install this?' Give your answer. Don't reference any other knowledge — just react to the report."

**Commits:**
1. Commit verification doc.

**Completion criteria:** the cold fork answers match the calibrated reading on at least 4 of 5 scans. Where they don't, document the gap and add a Phase 7 followup item (likely a prose-clarity tweak to the MD template).

---

### Phase 7 — Simple Report HTML on top of calibrated MD

**Goal:** the user-facing simple HTML output the project always anticipated, built on calibrated data.

**Deliverable:** Per `docs/simple-report-concept.md` — `docs/templates-simple/simple-report.html.j2` + `docs/templates-simple/simple-report.md.j2` + `docs/render-simple.py` + `docs/threat-explainer-library.json` + `docs/tool-branding.json`. Wizard Q1 gains option C "Simple."

**Branch:** `feat/simple-report`.

**Commits (incremental):** as the concept brief outlines.

**Completion criteria:** Simple Report renders cleanly for all 27 scans + validator passes + comparison doc shows it reads naturally to a consumer (re-run the Phase 6 verification on Simple instead of full).

---

## Roll-back contracts

- Each phase is an independent branch (Phase 3+4 may share `chore/calibration-rebuild-impl`). To revert any phase: `git revert <SHA>` or `git reset --hard <pre-phase-SHA>`.
- The audit (Phase 0) is read-only on existing data + adds 1 new doc. Trivial to revert.
- Phase 5 is the only phase that mutates committed scan outputs. Pre-mutation tag: `pre-calibration-rerender` (set immediately before that phase).
- Schema changes in Phase 3 require a migration script analogous to `docs/archive/migrations/migrate-v1.1-to-v1.2.py`.

## Definition of done

The plan is done when:
- `docs/scans/catalog/GitHub-Scanner-skills.md` (and ghostty + the 25 others) reads such that an LLM cold-pasted prompt of "should I install this?" returns a calibrated answer matching the actual risk profile, not a binary-cell-driven over-cautious answer.
- `compute.py` does ≥80% of severity scoring deterministically; LLM authoring is reduced to prose synthesis + ~5 bounded judgment fields.
- A Simple Report HTML exists and renders correctly on all 27 catalog scans.
- All persistent-state docs (CLAUDE.md, REPO_MAP.md, AUDIT_TRAIL.md) reflect the new state.

## What this plan deliberately does NOT include

- Visual polish on the standard HTML report (AT-T2.1/.2/.3-visual from the alarm-tuning Tier 2 queue) — moot once Simple Report is the consumer-facing output and the standard HTML stays the auditor view.
- The `github-scan-package-V2/` refresh — separate task, queued for after this plan completes.
- New wild scans during the rebuild — the rebuild is calibration work, not scan-coverage work. Wild scans resume after Phase 7. (Exception: if owner spots a specific shape gap during Phase 1 design that needs a fresh scan to validate, we can run one.)

## Cross-references

- Audit (Phase 0 fork output): `docs/calibration-audit.md`
- Calibration design (Phase 1): `docs/calibration-design-v2.md`
- Board archive (Phase 2): `docs/External-Board-Reviews/<MMDDYY>-calibration-rebuild/`
- Re-render comparison (Phase 5): `docs/calibration-rebuild-rerender-comparison.md`
- MD verification (Phase 6): `docs/calibration-rebuild-md-verification.md`
- Simple Report concept (Phase 7 spec): `docs/simple-report-concept.md`
- Existing telemetry (audit input): `docs/v12-wild-scan-telemetry.md`
- Existing prompt (will need updating in Phase 3-4): `docs/repo-deep-dive-prompt.md`
- Pipeline architecture (canonical): `docs/board-review-pipeline-methodology.md`
- Board runbook: `REPO_MAP.md` §2.3
