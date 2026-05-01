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
- **HEAD:** to-be-set-after-commit-2 on `chore/template-side-derivation` (pushed through `9a17a73`).
- **Branch base:** `c748d83` on `main` (post-/compact persistent-state consistency fix; pushed to origin/main).
- **Tree:** clean after commit 2.

### Phase + step
- **Active phase:** Phase 4 — mechanical reformatting moves to template-side. See plan §Phase 4 for the full spec.
- **Step within phase:** Commits 1 + 2 done. **Next: Commit 3 (update authoring template + scan-workflow doc).**

### Commits done in Phase 4
| SHA | One-line summary | Where |
|---|---|---|
| `740bed3` | Plan amendment: drop derive_evidence_facts (4→3 helpers) | `main` |
| `c748d83` | Post-/compact persistent-state consistency fix | `main` |
| `4d7e98c` | **Commit 1**: derivation helpers + 21 tests; no template changes | `chore/template-side-derivation` |
| `9a17a73` | Resumption-doc rewrite (strip CLAUDE.md, self-contained §Current state) | `chore/template-side-derivation` |
| `<commit2>` | **Commit 2**: wire helpers into renderers + 6 templates; byte-identical when LLM rows present | `chore/template-side-derivation` |

### Commits remaining in Phase 4
- **Commit 3 — Update authoring template + scan-workflow doc.** Concrete deliverables:
  - `docs/scan-authoring-template/author_phase_4.py.template` — REPO_VITALS / COVERAGE_DETAIL_ROWS / PR_SAMPLE_ROWS marked optional with comment "template derives from phase_1 when empty."
  - `docs/SCANNER-OPERATOR-GUIDE.md` — paragraph noting template-side derivation + which sections still need LLM authorship (§07 evidence stays LLM-only).
  - Token-weight measurement: count author_phase_4.py.template lines + average chars before/after. Target: ~50% reduction.
  - Acceptance test (verbatim from plan §Phase 4 Completion criteria): re-render skills (or any V1.2 catalog scan) with `REPO_VITALS = []`, `COVERAGE_DETAIL_ROWS = []`, `PR_SAMPLE_ROWS = []` zeroed → output retains the table content (now helper-derived).

### Files to read before writing commit 3 code
1. `docs/scan-authoring-template/author_phase_4.py.template` (current — what gets stripped)
2. `docs/SCANNER-OPERATOR-GUIDE.md` (search for sections that mention REPO_VITALS / repo vitals / PR sample / coverage detail authoring — note where the new "template derives" paragraph belongs)
3. `docs/render_helpers.py` (so the operator-guide paragraph references the right helper names)

**Do NOT read** during commit 3: audit, design doc, board archive, calibration-impl-notes, REPO_MAP, individual catalog scans. Reference-only material.

### Known gotchas for commit 3
1. **The template's three sections must be marked OPTIONAL but not deleted.** The LLM should still be allowed to author them when they want shape-specific commentary (e.g. the "Massively popular for a 3-month-old repo" note on skills' Stars metric). Empty list `[]` triggers the helper fallback; populated list overrides.
2. **Phase 1.5 follow-up gap to mention in operator guide:** harness `pr_review.prs` does NOT populate `author`/`merger` on V1.2 bundles. When the LLM zeroes PR_SAMPLE_ROWS, the derived table shows `?` for those columns. LLM should author rows when this matters.
3. **Token-weight measurement should compare apples-to-apples** — count only the SECTION_LEADS, REPO_VITALS, COVERAGE_DETAIL_ROWS, PR_SAMPLE_ROWS lines + their default placeholders. Don't include the boilerplate comments or imports that don't change.

### Outcome of commit 2 (for resumption-after-/compact context)
- 587 tests passing (added 1 V1.1 fixture-schema test on top of commit 1's 586)
- All 3 fixtures × 2 formats (zustand, caveman, archon-subset; .md + .html) byte-identical before/after — confirms LLM-rows-present path unchanged
- Fallback path verified: zeroing zustand's `repo_vitals.rows` / `coverage_detail.rows` / `pr_sample_review.rows` produces helper-derived content correctly
- Note=None Jinja gotcha fixed in 2 locations (section_05 .md.j2 + .html.j2): `{{ v.get('note', '') }}` → `{{ v.get('note') or '' }}`
- Helper schema-tolerance: `derive_pr_sample` now handles both V1.1 fixture schema (author/merger/any_review-bool) AND V1.2 harness schema (review_decision/any_review_count-int)
- Helper schema EXTENDED to include author + merger fields (always present in dict, may be empty string on V1.2 harness data)

### Token budget note
Each Phase step (one commit) should complete within **~200k tokens**. If you're approaching that limit, commit what's done, update §Current state to reflect the partial state, and stop for `/compact`. Do NOT push past the limit hoping to wrap up — context degrades rapidly past 200k and you'll make decisions you'd reject with a fresh context window.

### What was finished before Phase 4 (high-level only; details in commit history)
Phase 0 audit, Phase 1 calibration design, Phase 2 board review, Phase 3 calibration v2 implementation. All landed on origin/main. Phase 3 outcome detail in `docs/calibration-impl-notes.md`. Phase 3 commit list in `AUDIT_TRAIL.md`. **You should not need to read these to do Phase 4 work** — they are reference material, not resumption material.

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
