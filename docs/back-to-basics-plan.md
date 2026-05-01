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

- **Last commit landing this plan:** `91cecd5` (Phase 2 R1 close — design doc revised per 7 owner directives).
- **Active phase:** Phase 2 — board review **R2 launching**. R1 closed: 2 SIGN OFF WITH NOTES (Pragmatist + Codex) + 1 DISSENT (DeepSeek). 3-of-3 converged on Q9 floor (resolved by owner directive ≤5/12 + ≤3/12 staged stretch). Codex FIX-NOW on classify_shape phase boundary (resolved). 7 owner directives applied to design doc.
- **Active step within phase:** R2 brief written at `.board-review-temp/calibration-rebuild/r2-brief.md`. Launching 3 R2 agents in parallel; agents read revised design + all 3 R1 outputs + their own R1 + R2 brief. R2 focus areas: (A) did Q9 reframing land correctly, (B) is enum evolution mechanism adequate, (C) is rule precedence contract complete.
- **Next concrete action:** wait for 3 R2 agent completion notifications. When all 3 are back: if 3-of-3 SIGN OFF, write R3 confirmation brief (lighter — final ratification + dissent audit). If split verdicts persist, R3 carries the unresolved items.
- **Blocked on:** R2 agent completion notifications. Wall-clock estimate: 10-20 min (R2 typically faster than R1 since agents have prior position to anchor against).
- **Audit topline (so a future session can resume without re-reading the audit doc):**
  - Dominant pattern: "OSS minimal-governance default" — 6 of 12 V1.2 scans hit (no protection + 0 rulesets + no CODEOWNERS + low formal review). 3 of those 6 are Caution, 3 are Critical → **Q1=red is NOT verdict-discriminating in current data.**
  - Q3 is similarly decoupled: every Q3=red scan has identical signals, but 2 of 6 Q3=red scans are Caution (skills + QuickLook — both cases where disclosure-machinery absence is proportional to project age/maturity).
  - **Q4 IS the verdict-discriminator**: 5/5 Q4=red scans are Critical; 5/5 Caution scans have Q4=amber. But every Q4=red required Phase 4 LLM override because Phase 3 advisory never reaches red on Q4 (12/12 amber). The override mechanism is doing shape-aware judgment work that should be expressed as rules.
  - Highest-leverage proposed rules from audit §10: RULE-4 (Q3=amber for `repo_age < 180d AND total_merged_lifetime < 5` — fixes skills-class), RULE-1 (Q1=amber when CODEOWNERS+ruleset+rules-on-default present — already overridden 2x), RULE-6 (extend V13-3 C5 deserialization auto-fire to cmd_injection + tool_loads_user_files — eliminates 2 of 5 Q4 overrides). Combined with shape-aware variants, override count projected to drop from ~10/12 to 1-2/12.
- **Branch:** `main`. Phase 1 will also stay on `main` (docs only). Phase 3 onward uses `chore/calibration-rebuild-impl`.

---

## Phases (linear; each has explicit deliverables + commits + completion criteria)

### Phase 0 — Distribution audit  *(in flight)*

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

**Goal:** stop having the LLM re-author harness data into table rows. REPO_VITALS, COVERAGE_DETAIL, PR_SAMPLE, EVIDENCE table rows all derive deterministically from `phase_1_raw_capture`.

**Deliverables:**
- `docs/render-md.py` + `docs/render-html.py` extended with helper functions `derive_repo_vitals(p1)`, `derive_coverage_detail(p1)`, `derive_pr_sample(p1)`, `derive_evidence_facts(p1)`.
- Templates updated to use derived data when phase_4 doesn't supply it (LLM still allowed to override for shape-specific row reordering or commentary).
- `docs/scan-authoring-template/author_phase_4.py.template` updated — those sections are now optional / minimal.
- New tests in `tests/test_render_md.py` + `tests/test_render_html.py` for the derivation helpers.

**Branch:** continue on `chore/calibration-rebuild-impl` (or new branch — TBD by phase 3 outcome).

**Commits (incremental):**
1. Add derivation helpers + tests.
2. Wire helpers into renderers + adjust templates.
3. Update authoring template + scan-workflow doc.

**Completion criteria:** re-rendering a recent V1.2 scan (e.g. skills) produces the same table content with the LLM authoring zero rows. Token-count delta on per-scan authoring should be measurable (target: ~50% reduction in author_phase_4.py token weight).

---

### Phase 5 — Re-render all 27 catalog scans + diff

**Goal:** validate the new calibration against the existing catalog. Some verdicts may shift (intentional). We document each shift + owner reviews before commit.

**Deliverables:**
- `docs/calibration-rebuild-rerender-comparison.md` — for each scan: old verdict / new verdict / cell-color delta / rationale (one-line per scan).
- Re-rendered MD + HTML for all 27 scans → committed to `docs/scans/catalog/` REPLACING the existing files (per the calibration cutover; old versions remain in git history).
- Updated `docs/scanner-catalog.md` table reflecting any verdict shifts.

**Pre-commit gate:** owner reviews the comparison doc and signs off on each verdict shift.

**Branch:** `chore/calibration-rebuild-rerender` (separate from impl branch so the impl can land first).

**Commits:**
1. Add comparison doc + the re-rendered scan files + catalog updates in one cohesive commit.
2. Update CLAUDE.md current-state paragraph + REPO_MAP.md catalog count if it changed.

**Completion criteria:** owner signs off on the rerender comparison; 414+/414+ tests pass; validator clean on every re-rendered file; `--parity` zero-warning on every MD/HTML pair.

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
