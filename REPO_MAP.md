# Repository Map — stop-git-std

**Last audited:** 2026-04-30 (session 8 cleanup)
**HEAD at audit:** session 8 cleanup branch (post-reorganize: `docs/scans/catalog/`, `docs/scan-bundles/`, `docs/scan-authoring-template/`, `docs/archive/`, `.scan-workspaces/`)
**Regeneration:** this file is hand-maintained. Run `git log -1 --format='%ai' -- <path>` to verify any listed timestamp.

This is the "where does everything live AND what ships" doc. If you're Claude starting a fresh session, read `CLAUDE.md` first for operating instructions, then come here for the index.

Three sections:
- **§1 Work done** — historical + existing artifacts
- **§2 Current plan + continue-building context** — where we are, next steps, how to run the board
- **§3 File/folder index + release status** — the categorized directory

---

## 1. Work done

### 1.1 Phase 7 renderer plan (A→G)

Canonical plan: `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`

| Step | Status | Key commit(s) |
|---|---|---|
| A — Schema freeze V1.1 (renderer-driven $defs, C2/C3 conditionals) | ✅ Done | `2b576bf` + `c6531bb` |
| B — render-md.py → Jinja2 thin shim + 14 partials | ✅ Done | `75db969` |
| C — Zustand fixture enrichment (10 FAs) | ✅ Done | `59224ac` |
| D — Flip render tests to structural assertions | ✅ Done | `aac2b3b` |
| E — Validator `--report` gate on rendered MD | ✅ Done | `cf8c576` |
| F — HTML renderer + cross-shape fixtures + R3 XSS/CSS/parity fixes | ✅ Done | `402f933` + `ce698d4` |
| — U-1 (Step G doc integration) | ✅ Done | `6a3e471` |
| — FX-3b parallel (package validator sync) | ✅ Done | `60e0bf2` |
| — U-3/FX-4 (fixture provenance) | ✅ Done | `3c09afb` |
| **G — C7 acceptance matrix (live JSON-first pipeline on 3 shapes)** | ⏳ Next, board required | — |

### 1.2 Board reviews archive (`docs/External-Board-Reviews/`, 63 files across 6 folders)

Index master: `docs/External-Board-Reviews/README.md`

| Folder | Scope | Verdict | Rounds |
|---|---|---|---|
| `041626-celso/` | V2.3 pre-migration review | — | — |
| `041826-renderer-alignment/` | Phase 7 renderer plan A-G approval | ALL SIGN OFF | R1-R4 |
| `041826-renderer-impl-verify/` | Steps A+B implementation verification + STEP-E/STEP-F verification records + INDEX cross-ref | APPROVED post-owner-directive | R1 |
| `041826-fixture-enrichment/` | Step C 10-FA review | UNANIMOUS 3-0 APPROVE | R1 |
| `041826-step-f-alignment-validation/` | Step F validation + XSS/CSS/parity fixes | SIGN OFF 2 + W/DISSENTS 1 (bookkeeping) | R1-R4 |
| `041826-step-g-kickoff/` | U-1 doc integration, V2.5-preview pipeline | SIGN OFF 1 + W/DISSENTS 2 (non-blocking) | R1-R3 |

Older flat-file board records (pre-`External-Board-Reviews/` layout, kept for historical reference):
- `docs/board-review-V21-consolidation.md` · `V22` · `V23` — V2.1/V2.2/V2.3 scanner prompt reviews
- `docs/board-review-axiom-triage-consolidation.md` · `axiom-triage-R2-consolidation.md` — AXIOM findings triage
- `docs/board-review-operator-guide-consolidation.md` — V0.1 operator guide review
- `docs/board-review-package-v2-consolidation.md` — V2.4 package review
- `docs/board-review-pipeline-methodology.md` — JSON-first pipeline architecture decision (8/8/4, 9-phase) — canonical pipeline-architecture record

### 1.3 Completed scans (V2.4 catalog, 10 entries)

`docs/scanner-catalog.md` lists entries 1–10 (all `rendering-pipeline: v2.4`). Artifacts at `docs/scans/catalog/GitHub-Scanner-<repo>.{html,md}`. Shape coverage: curl-pipe installer (caveman), agentic platform (Archon), JS library (zustand), Rust CLI (fd), Claude-Code skills (gstack), pre-distribution (archon-board-review), Python platform (hermes-agent), web app (postiz-app), plus zustand-v3 revision + Archon rerun record (zustand-v2 superseded → `docs/archive/scans-superseded/`).

### 1.4 Historical / backfilled artifacts

- `docs/archive/prompts/repo-deep-dive-prompt-V2.md` · `V2.1.md` · `V2.2.md` — prompt version archives (current is V2.4 at `docs/repo-deep-dive-prompt.md`)
- `docs/CHANGELOG.md` — prompt version history (V2.1→V2.4)
- `docs/archive/board-review-data-pre-layout/` — older `board-review-data/` artifacts moved here in session 8 cleanup
- `archive/` (top-level) — old TypeScript static analyzer (101 files, historical; see §3.5)

---

## 2. Current plan + continue-building context

### 2.1 Architecture

**8/8/4 classification** (board-approved, canonical record `docs/board-review-pipeline-methodology.md`):
- 8 Automatable (Python compute) — verdict, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised
- 8 Structured LLM (enum/template constrained) — general vuln severity, split-axis, priority evidence, threat model, action steps, timeline, capability assessment, catalog metadata
- 4 Prose LLM (structural constrained) — what_this_means, what_this_does_NOT_mean, finding body, editorial caption

**9-phase pipeline:** tool-exec → validation → compute → structured-LLM → prose-LLM → assembly → render → validator → git-hook

**Invariants:** MD canonical / facts-inference-synthesis separate / pre-computed form contract / prose stays sparse / validator is the gate

### 2.2 Current state

- **HEAD:** `6657e59` on `origin/main` (post-merge pointer cleanup; session 10 Phase 3 MERGED + pushed at `9d33799`; feature branch `chore/calibration-rebuild-impl` deleted local + remote). Tree clean.
- **Session 10 work (2026-05-01):** Phase 3 of back-to-basics-plan COMPLETE + MERGED + PUSHED. Calibration v2 module landed in `docs/compute.py` (`classify_shape()` + `evaluate_q1/q2/q3/q4` + `compute_scorecard_cells_v2()`). 4 implementation commits on `chore/calibration-rebuild-impl`: `4d7b847` (P3.a heuristic + 12-bundle gate) → `b51b6b8` (P3.b/c rule-eval tests) → `79f084a` (P3.d/e schema + validator gate v2.1) → `1688ec5` (P3.f regression + impl-notes), then `e45f2e1` (Phase 3 close persistent-state) → `9d33799` (no-ff merge to main) → `6657e59` (post-merge pointer cleanup). All 5 CONSOLIDATION §5 carry-forwards addressed. **Override-reduction: 5/10 cells now rule-driven (~50% reduction → hits design hard-floor ≤5/12 ~42%).** Spec deviations consolidated at `docs/calibration-impl-notes.md`. **Phase 4 next** — mechanical reformatting moves to template-side; recommended branch `chore/template-side-derivation` from main. See `docs/back-to-basics-plan.md` §Current state.
- **Session 9 work (2026-05-01):** back-to-basics calibration rebuild. Phase 0 distribution audit + Phase 1 design + Phase 2 board review (3 rounds, 16 owner directives, 26-item dissent audit, 3-of-3 R3 SIGN OFF) + Phase 2 archive at `docs/External-Board-Reviews/050126-calibration-rebuild/`.
- **Session 8 first scan:** `2aa59bf` (catalog entry 27 mattpocock/skills — first Claude Code skills/plugin V1.2 wild scan; Caution; Q2 missing_qualitative_context override — first use of this enum value at any n).
- **Session 7 commits** from `c6e7502` (session 6 close) →: `b3622b5` (WLED catalog entry 25 — first embedded IoT firmware scan, Q4 signal_vocabulary_gap override on CORS+no-auth) → `f4f3332` (WLED catalog hash resolution) → `2b295ef` (Baileys catalog entry 26 — first TS-primary + first reverse-engineered-API scan; **V13-3 TRIGGER FIRED at n=11**) → `c558b9f` (Baileys catalog hash resolution) → `fcc4e81` (V13-3 CLOSE: comparator-calibration board review + V1.2.x Priority 1 landings: C2 language qualifier, C5 Q4 auto-fire, C18 tool-loads-user-files helper, C20 dry-run; Q4 rubric reorder) → `c0d2ba2` (archive Codex code-review 3-pass iteration) → `9b5e5d4` (session 7 persistent-state updates).
- **Tests:** **565/565 passing** (414 session-7 baseline + **151 net new in session 10 Phase 3**: 46 `tests/test_classify_shape.py`, 54 `tests/test_calibration_rules.py`, 9 `tests/test_validator_v2_rule_id.py`, 42 `tests/test_calibration_regression.py`).
- **Parity sweep:** All V1.2 wild scan MD+HTML pairs clean (11 wild scans + 3 Step G pairs).
- **Repo↔package validator:** byte-identical (no package change this session).
- **CSS:** 824 lines (unchanged).
- **Catalog:** **27 entries** — 11 `v2.4` + 16 `v2.5-preview`: 3 Step G validation (12-14) + **12 V1.2-schema wild scans** (entries 16–27). Latest: mattpocock/skills entry 27 (first Claude Code skills/plugin shape; Caution verdict; Q2 missing_qualitative_context override — first use of this enum value at any n).
- **Schema: V1.2 (LIVE)** — unchanged in structure from session 6; `override_reason_enum` stays at 7 values post-V13-1; V1.3 candidate to prune `missing_qualitative_context` with historical-hold guardrail.
- **Compute:** `SIGNAL_IDS` unchanged at 25; `compute_scorecard_cells()` signature widened with optional `phase_1_raw_capture` kwarg that internally invokes `compute_q4_autofires_from_phase_1()` wrapper to OR-merge Q4 auto-fires. New helpers `derive_tool_loads_user_files(readme_text, repo_metadata)` + `derive_q4_critical_on_default_path_from_deserialization(dangerous_primitives, readme_text, repo_metadata, threshold=3)`. Q4 rubric reordered: has_critical_on_default_path check moved to highest priority.
- **Harness:** `dangerous_primitives.deserialization` regex narrowed by V13-3 C2 — bare `\bdeserialize\b` keyword dropped (suppresses ArduinoJson FP class on C/C++/Rust with JSON libraries). Language-specific unsafe tokens preserved (pickle.loads?, ObjectInputStream, Marshal.load, yaml.load, unserialize, marshal.loads?, joblib.load, dill.loads?).
- **New tooling this session:** V1.2.x Priority 1 landings in compute + harness (described above). No new standalone tools.
- **New docs this session:** `docs/v13-3-analysis.md` (FROZEN 191-line analysis mirroring v13-1 template) + `docs/v13-3-fp-dry-run.md` (C20 dry-run artifact; 0 FPs on 11 bundles) + `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/` (full 3-round board review archive + 3 Codex code-review passes + CONSOLIDATION.md with 33-item dissent audit, zero silent drops).
- **Gate 6.3: override-explained** (unchanged). Across 10 overrides in 12 V1.2 wild scans: `signal_vocabulary_gap` × 6 (60%, modal), `harness_coverage_gap` × 2 (20%), `threshold_too_strict` × 1 (10%), **`missing_qualitative_context` × 1 (10%, first fire entry 27)**. 3 of 7 enum values unexercised (was 4 at n=11; entry 27 collapsed `missing_qualitative_context` from unexercised to live).
- **Zero-override streak** at 3 (wezterm → QuickLook → kanata) broken by freerouting → continued breaking through WLED → Baileys (3 consecutive Q4 signal_vocabulary_gap overrides: freerouting/WLED/Baileys).
- **V13-3 CLOSED** — 2/3 R3 AGREE + owner directive OD-4 (Codex R3 unavailable, R2 positions consistent with R3 resolutions; assigned code-review gate on implementation diff; SIGN OFF W/ NOTES after 3-pass iteration). Follow-up re-triggers on N=25 V1.2 wild scans OR any of 6 taxonomy-strain events (see v13-3-analysis.md §4.4).
- **V2.5-preview: PRODUCTION-CLEARED** (unchanged from session 5; harness is the Phase 1 standard; compute_scorecard_cells now auto-fires Q4 from phase_1_raw_capture when passed).
- **Cross-repo FrontierBoard SOP** (unchanged): `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`.

### 2.3 Board runbook — how to run the 3-model governance board

**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`

**Composition** (per SOP §4, minimum 3 agents):
- **Pragmatist** — Claude Sonnet 4.6 when Opus wrote the artifact (same-model blind spot rule); Opus otherwise. Via `Agent` tool.
- **Systems Thinker** — Codex GPT-5. Via `sudo -u llmuser` from `/tmp/`.
- **Skeptic** — DeepSeek V4. Via Qwen CLI from repo directory.

**Rounds:** minimum 3 (Blind → Consolidation → Confirmation). Add R3 Deliberation → R4 Confirmation (4-round) if R2 produces a split verdict.

**Invocation — Pragmatist (Sonnet 4.6):**
```
Agent tool
  subagent_type="general-purpose"
  model="sonnet"   (when Opus wrote the artifact)
  run_in_background=true
  prompt: "You are the Pragmatist on a 3-model FrontierBoard review. Read /tmp/<topic>-<round>-brief.md end-to-end. ... <role specifics>"
```

**Invocation — Systems Thinker (Codex GPT-5):**
```bash
sudo -u llmuser bash -c "cd /tmp && codex exec \
  --dangerously-bypass-approvals-and-sandbox '<prompt>'" \
  > /tmp/<topic>-codex-<round>.log 2>&1
```
Must be `llmuser` (auth tied to that user; running as root → 401 token expired). Must run from `/tmp` (repo-dir CLAUDE.md pulls Codex off-task). Brief file at `/tmp/<topic>-<round>-brief.md`.

**Invocation — Skeptic (DeepSeek V4):**
```bash
OPENAI_API_KEY="$DEEPSEEK_API_KEY" \
OPENAI_BASE_URL="https://api.deepseek.com/v1" \
  qwen -y -p "<prompt>" --model deepseek-chat \
  > .board-review-temp/<topic>/deepseek-<round>-raw.log 2>&1
```
Launch from repo directory (workspace scope includes repo files). `-y` = YOLO mode, required for file writes.

**Failure modes:**
- Codex 401 "token expired" → you're running as root; switch to `llmuser`
- DeepSeek `API Error: Connection error` / `terminated` → transient, retry once (succeeds ~90% of the time)
- Qwen "cannot access file" → launched from wrong directory

**File staging pattern** (during review):
```
.board-review-temp/<topic>/
  r1-brief.md · r2-brief.md · r3-brief.md · r4-brief.md
  pragmatist-r1.md · codex-r1.md · deepseek-r1.md
  pragmatist-r2.md · codex-r2.md · deepseek-r2.md
  (etc.)
  deepseek-r<N>-raw.log    (qwen stdout capture)
```

**Archive pattern** (on sign-off):
```
docs/External-Board-Reviews/<MMDDYY>-<topic>/
  CONSOLIDATION.md       (final record — verdicts, resolutions, dissents, owner directives, agent-invocation snapshot)
  r{1..4}-brief.md
  {pragmatist,codex,deepseek}-r{1..4}.md
```
Then update `docs/External-Board-Reviews/README.md` master index.

**Brief essentials** (agents are STATELESS — re-read file even if you "wrote" it):
1. Full project context from scratch
2. All prior-round outputs inlined verbatim (R2+)
3. Absolute paths for files to READ
4. Required output format (§ structure, word cap)

**Recent examples to model after:**
- 4-round with split verdict: `docs/External-Board-Reviews/041826-step-f-alignment-validation/`
- 3-round with 2-1 owner-directive resolutions: `docs/External-Board-Reviews/041826-step-g-kickoff/`
- Fix-artifact-first governance: R3 brief has owner-authored BEFORE/AFTER, board votes SECOND/ADJUST/REJECT

### 2.4 Step G — PASSED 3/3; V2.5-preview PRODUCTION-CLEARED 2026-04-20

**Production-clearance fired** via first wild scan on microsoft/markitdown (catalog entry #15, Python monorepo + PyPI + Dockerfile — shape outside {zustand, caveman, Archon}). Cleared all 7 applicable gates (gate 6 N/A on wild scan) using harness-gathered Phase 1 data. Phase 1 automation shipped in commit `4ad4cf6` via `docs/phase_1_harness.py` + `docs/phase-1-checklist.md` + 30 tests. See §8.8 of Operator Guide for current state.



**Acceptance matrix** (commits `2c13324`, `ed68fae`, `be56935`):

| # | Target | SHA | Cells (Q1/Q2/Q3/Q4) | Verdict | Split axis | Findings | Commit |
|---|---|---|---|---|---|---|---|
| 1 | pmndrs/zustand v3 | `3201328` | amber/green/amber/green | Caution | none | F0-F3 (4) | `2c13324` |
| 2 | JuliusBrussee/caveman | `c2ed24b` | red/amber/red/red | Critical | Version | F0/F5/F11/F14/F16 (5) | `ed68fae` |
| 3 | coleam00/Archon | `3dedc22` | red/amber/amber/red | Critical | Deployment | F0-F8 (9) | `be56935` |

- 12/12 scorecard cells match V2.4 comparator cell-by-cell.
- 18/18 finding cards (4 + 5 + 9) match V2.4 inventory + severity.
- All 3 targets clear all 7 gates. Deterministic renders (byte-identical MD5 on double-render).

**SF1 board outcome** (`docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md`, 4 rounds, 2026-04-20):

- R1 Blind: Pragmatist A / Codex new-D / DeepSeek C+
- R2 Consolidation on hybrid "A-now + C-for-V1.2 + edge_case": 1 ACCEPT + 2 ACCEPT-WITH-MODS
- R3 Confirmation on frozen hybrid: 3/3 CONFIRM + 3/3 UNION-ACCEPT on D-7 trigger + 1-1-1 on Tension-1
- R4 narrow tiebreaker: 2-1 G-C-ACCEPT (Pragmatist moved from A-CANONICAL to G-C-ACCEPT after the live `gh api` Archon-evidence brief). DeepSeek dissent (D-CANONICAL) preserved
- Dissent audit: clean across all 4 rounds

**Phase 1 delivered** (commits `7f90a1b`, `7d300a8`):

- 4 `docs/compute.py` temporary compatibility patches annotated as V1.1 compatibility-only (Q1 governance-floor override; Q2 `closed_fix_lag_days`; Q3 `has_contributing_guide`; Q4 `has_warning_on_install_path`). Gate C audit (Archon PR #1169 = undisclosed security fix → `has_reported_fixed_vulns=TRUE`) drove D-CANONICAL outcome on Q3 Archon, applied as U-11 single-cell catalog correction (green → amber).
- 10 new tests under `TestSF1ScorecardPatches` (289/289 passing).

**Phase 2 committed** (D-7):

Schema split V1.1 → V1.2: move scorecard cells from `phase_3_computed` to `phase_4_structured_llm.scorecard_cells` with `edge_case` + `suggested_threshold_adjustment` + `computed_signal_refs` structured fields. `compute_scorecard_cells()` demoted to advisory. Gate 6.3 changes from "cell-by-cell match" to "override-explained." Step 3b byte-for-byte retained for the other 7 Phase 3 ops.

D-7 trigger (disjunctive, first-to-fire): first scan on shape outside current 7 catalog shapes / 3 live scans post-Step-G with ≥2 shape categories / 6 months post-Step-G / any semantic-not-threshold drift.

**Production-clearance trigger (NOT YET FIRED):**

V2.5-preview is Step-G-validated on the 3 pinned-SHA validation shapes but is NOT yet production-cleared. The remaining trigger: a successful wild scan — live `gh api` capture on a repo outside {zustand, caveman, Archon}, rendering clean through the V2.5-preview pipeline with all 7 gates passing. Until then, V2.4 stays the default production path. See Operator Guide §8.8 opening callout.

**Option B (catalog harmonization) explicitly rejected** by the SF1 board.

**Pre-flight state (clean, preserved across the halt):**
- Step -2 (provenance): `zustand-step-g-form.json` pre-registered with `step-g-live-pipeline` tag in `tests/fixtures/provenance.json`
- Step -1 (comparator cleanliness): zustand-v3, caveman, Archon all 0 `WARNING:` / 0 errors (after `9840cdf` FN-5 grep + warning reclassification)
- Step 0 (adversarial bundle smoke test): 4 cases behave per spec (3 fail, 1 compact-bundle pass)

**All 4 pre-reqs cleared** per `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md`:

| Item | Scope | Status |
|---|---|---|
| U-1 | V2.5-preview doc integration | ✅ Done (`6a3e471`) |
| U-3/FX-4 | `tests/fixtures/provenance.json` — separate-file approach | ✅ Done (`3c09afb`) |
| U-5/PD3 | Bundle/citation validator | ✅ Done (`885bdcf`) — `--bundle` mode, 16 tests, 5-bundle corpus pass |
| U-10 | Catalog re-validation | ✅ Done (`6481533`) — canonical scorecard alignment, 13/13 pairs clean |

**Step G execution approach — board-approved** per `docs/External-Board-Reviews/041926-step-g-execution/CONSOLIDATION.md` (2026-04-19, unanimous clean R3 SIGN OFF, 41-item dissent audit zero silent drops). Final approved set: 9 fix artifacts (FN-1..FN-9) + 15 carry-forward dispositions (D-1..D-6, I-1..I-9) + 8 adjustments (A-1..A-8).

**FN items fully implemented** in `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 per commit `a80f239` (2026-04-20, Codex-reviewed pre-commit). Operator Guide §8.8 is the canonical Step G execution spec:

| FN | Scope | Location |
|---|---|---|
| FN-1 | Gate 6 zero-tolerance 6-point checklist + severity mapping doc | §8.8.5 gate 6.1–6.6 |
| FN-2 | Mandatory `compute.py` + byte-for-byte equality | §8.8.3 Step 3b |
| FN-3 | Adversarial bundle smoke test (3 fail + 1 pass cases) | §8.8.3 Step 0 |
| FN-4 | Graduated failure rubric (no "partial pass"; gates 1–3/5 rollback, 4/6 retry, 7 STOP, ambiguity HALT) | §8.8.6 |
| FN-5 | `tee` + `grep '^WARNING:'` count-check on `--parity` + `--bundle` | §8.8.2 step 4 |
| FN-6 | V2.4 comparator `--parity` cleanliness pre-flight | §8.8.3 Step -1 |
| FN-7 | Pilot-and-checkpoint ordering (zustand → checkpoint → caveman + Archon) | §8.8.2 |
| FN-8 | Phase-boundary contamination check (all 3 targets, semantic, STOP) | §8.8.3 Step 10 + §8.8.5 gate 7 |
| FN-9 | Bundle-complete gate before form.json authoring | §8.8.3 Step 3c |
| D-4 | Schema hardening halt-on-smuggle watchpoint | §8.8.7 |
| D-6 | Severity distribution automation as POST-STEP-G IMMEDIATE | §8.8.7 |

**Execution target:** 3 shapes with V1.1 fixtures — zustand, caveman, Archon — at their pinned V2.4 catalog SHAs (for apples-to-apples structural-parity comparison vs V2.4 MD/HTML goldens).

**Execution order (per FN-7):** zustand first end-to-end → hard checkpoint → caveman + Archon sequentially in same session. Checkpoint branching: pipeline-correctness pass → continue; pipeline-correctness fail → STOP (rollback per §8.8.6); authoring-only fail → one retry permitted.

**Cross-repo SOP invariant:** pre-archive dissent audit is mandatory per FrontierBoard SOP §4 (commit `e01303a` on stefans71/FrontierBoard main). Applies to the Step G post-execution archive.

**SF1 evidence summary** (for reference):

| Target | Cell | V2.4 comparator MD | compute.py output | Phase 1 patch |
|---|---|---|---|---|
| zustand-v3 | Q3 | Amber (contributing guide softens) | red | `has_contributing_guide` |
| zustand-v3 | Q4 | Green (install/runtime clean) | amber | `has_warning_on_install_path` (Gate B dependent) |
| caveman | Q2 | Amber (5-day lag) | green | `closed_fix_lag_days` |
| Archon | Q1 | Red (8% formal, no gate) | amber | governance-floor override |
| Archon | Q3 | Green (SECURITY.md + public issues) | amber | `has_reported_fixed_vulns` (Gate C dependent) |

Phase 1 gate log: `.board-review-temp/step-g-execution/phase-1-gate-log.md`

### 2.5 Deferred ledger

Non-active items tracked for future trigger:

- **D-7 + D-8 → Schema V1.2 (IMPLEMENTED 2026-04-20)** — co-scheduled board review closed 2026-04-20 (3/3 SIGN OFF with owner directives). Implementation landed in same session: schema bump, harness additions, `compute.SIGNAL_IDS` 23-entry frozenset, validator `--form` mode with gate 6.3 override-explained, scorecard partial path migration, `migrate-v1.1-to-v1.2.py` idempotent migration (all 3 active fixtures migrated clean), 23 new V1.2 tests (342/342 passing). Transformer deleted. **Override-explained proven end-to-end** via ghostty entry 16 Q1 override (advisory red → Phase 4 amber with `missing_qualitative_context` + 7 `computed_signal_refs`). See `docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` for the canonical record (31-item dissent audit: 14 resolved + 5 deferred with triggers + 9 live preserved dissents + 3 moot; zero silent drops).
- **V1.3 watchpoints (deferred per CONSOLIDATION §8 / V13-*)** — triggered from 2026-04-20 V1.2 landing onward:
  - **V13-1 Override-pattern telemetry log** — **RESOLVED 2026-04-20 by owner directive.** See `docs/v13-1-override-telemetry-analysis.md`. 4 existing overrides analyzed → owner directive expanded `override_reason_enum` 5→7 values (+`signal_vocabulary_gap`, +`harness_coverage_gap`); 4 existing overrides relabeled; V1.2.x signal widening (`q1_has_ruleset_protection`, `q2_oldest_open_security_item_age_days`, harness deserialization regex) landed same day as follow-up. CONSOLIDATION §8.1 + §8.2 record the decision.
  - **V13-2 Renderer Phase-1 richness expansion** — triggers met (V1.2 round-trip + determinism pass clean) but not yet executed. Queued for V1.3 cycle or V1.2.x patch.
  - **V13-3 11-scan comparator calibration analysis** — **CLOSED 2026-04-20 by 2/3 R3 AGREE + owner directive OD-4** (Codex R3 unavailable; R2 positions consistent with R3 resolutions; Codex assigned code-review gate as substantive-review surrogate). Board archive: `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/CONSOLIDATION.md` (33-item dissent audit, zero silent drops). Frozen analysis at `docs/v13-3-analysis.md`. V1.2.x Priority 1 landings shipped: C2 language-qualifier regex, C5 Q4 auto-fire, C18 tool-loads-user-files helper, C20 dry-run (0 FPs on 11 bundles). Follow-up re-triggers: N=25 V1.2 wild scans OR any of 6 taxonomy-strain events (§4.4 of analysis).
  - **V13-4 `community_norms_differ` enum expansion** (DeepSeek R3 preserved dissent, now re-framed by V13-3 board). **Trigger refined by V13-3 C8:** N=15 V1.2 wild scans OR first Q3 override fire. **Status: 0 Q3 overrides across 11 scans** (including 2 documented disclosure-handling failures on WLED + Baileys — both judged amber-not-red by Phase 4). V13-4 remains open; V13-3 C8 resolution preserved the enum-addition option without changing the Q3 rubric.
  - **V13-5 SD2 auto_load_tier C3 rebinding** (`domain=='agent'`). Own review cycle. Not advanced this session.
  - **V13-6 markitdown-as-4th-fixture decision.** Trigger: markitdown re-scanned under V1.2. Not advanced (markitdown entry 15 is the single markitdown scan; re-scan under V1.2 would close D-6 consumer debt but not prioritized).
  - **V13-7 OQ-9 sidecar reconsideration** if harness gathers data not representable in schema. Trigger: any harness feature add that fails B1 round-trip. No firings.
  - **V12x-1 gather 4 remaining repo_metadata fields in harness** — SHIPPED session 5 (has_issues_enabled, primary_language, topics, fork_count all populated now).
  - **V12x-2..V12x-4** (original session 5 items): still applicable; none triggered this session.
  - **V12x-5 Deserialization auto-fire for Q4** — **SHIPPED 2026-04-20 as V13-3 C5** (commit `fcc4e81`). `derive_q4_critical_on_default_path_from_deserialization` + `compute_q4_autofires_from_phase_1` wrapper + `compute_scorecard_cells(phase_1_raw_capture=...)` internal integration. Dry-run (`docs/v13-3-fp-dry-run.md`): 1 true-positive (freerouting), 0 FPs on 11 bundles.
  - **V12x-6 Multi-ecosystem manifest parsing** (V13-3 C17 — DEFERRED to V1.3 coordinated compute expansion package) — Maven/Gradle/Cargo/gomod/Bundler/NuGet parsing + OSV-query. Closes the F5/F6-class findings in 7 of 11 V1.2 scans.
  - **V12x-7 Install-doc URL TLD-deviation detection** (medium-priority) — would auto-surface browser_terminal's F0 typosquat without Phase 4 override. 1/11 scans affected.
  - **V12x-8 Language-specific distribution-channel detection** (medium-priority) — 8 of 11 scans surface fictitious or missing channels.
  - **V12x-9 Dangerous-primitives regex language-qualifier** — **SHIPPED 2026-04-20 as V13-3 C2** (commit `fcc4e81`). `STEP_A_PATTERNS["deserialization"]` drops bare `\bdeserialize\b` keyword; language-specific unsafe tokens preserved. Suppresses ArduinoJson / serde FP class (4 scans affected historically: wezterm, kanata, QuickLook, WLED).
  - **V12x-10 Silent-fix pattern telemetry** (V13-3 C8/C14 — DEFERRED; V13-4 trigger refined to N=15 or first Q3 override fire) — 11 of 11 V1.2 scans show 0 published GHSA advisories; 2 documented disclosure-handling failures (WLED #5340, Baileys PR #1996). Q3 rubric unchanged; V13-4 `community_norms_differ` enum-addition option preserved.
  - **V12x-11 Firmware-default-no-auth + CORS-wildcard compound Q4 signal** (V13-3 C6 — DEFERRED V1.3) — new Priority 1b from WLED entry 25. Requires shape-classification infrastructure.
  - **V12x-12 Reverse-engineered-API-library shape Q4 signal** (V13-3 C7 — DEFERRED V1.3 with triggered-promotion-or-REJECT gate) — new Priority 1c from Baileys entry 26. Trigger: ≥3 confirmed fires + dry-run FP test = 0 FPs on vendor-authorized third-party clients.
  - **V12x-13 vendor_keys proximity-context requirement** (low-priority, from Baileys FP on `AIza...` WhatsApp protocol dictionary).
  - **V12x-14 PR-sampler robustness when closed-without-merge dominates stream** (low-priority, from Baileys harness gap — 0 sampled PRs despite 352 merged).
  - **N1 Deserialization primitive family taxonomy redesign** (V13-3 new V1.3 candidate — Skeptic's principled-expansion concern). Safe JSON parsing (ArduinoJson, serde_json) and unsafe deserialization (pickle, ObjectInputStream, Marshal) deserve separate family names in `STEP_A_PATTERNS`. C2 is the V1.2.x bounded exception; N1 is the V1.3 principled replacement.
  - **N2 Statistical CIs on override-rate claims** — already applied to `docs/v13-3-analysis.md` §3.1 (at n=9 overrides, 67% modal rate has 95% CI ≈ 35–88%). Future V13-3-class analyses should continue this practice.
- **D-6 Automated severity distribution comparison script** — **SHIPPED 2026-04-20** at `docs/compare-severity-distribution.py` (23 tests; all 3 Step G pairs pass with 4/4, 5/5, 9/9 matches). See Operator Guide §8.8.7 update — no longer a deferred debt item.
- **Remaining un-wild-scanned shapes** (each expands validation surface when scanned — CONSOLIDATION §1 noted): Rust CLI with release binaries (`sharkdp/fd`), Claude Code skills / dense agent rules (`grapeot/gstack`), web app with Docker defaults (`gitroomhq/postiz-app`), Python platform with open security issues (`NousResearch/hermes-agent`). Each V2.4 catalog entry already exists; a V1.2 re-scan on any of them tests the new schema on that shape + continues the telemetry accumulation toward V13-1 and V13-3. **Directives:** D1 Q3=B1 harness-canonical (transformer deleted; schema adopts harness names `archived`/`fork`/`default_branch`/etc. + harness shapes natively including nested per-family `dangerous_primitives` + `{verified,total}` for `distribution_channels_verified`); D2 new top-level `phase_3_advisory.scorecard_hints` (keyed object by question ID), `phase_4_structured_llm.scorecard_cells` gains `{rationale, edge_case, suggested_threshold_adjustment, computed_signal_refs, override_reason}`, `phase_3_computed.scorecard_cells` deleted. **Six R3 item resolutions:** (A) override-rationale validator = refs-only + 50-char floor + enum check (no substring requirement); (B) migration script migrates 3 active fixtures only, `step-g-failed-artifact` entries stay V1.1 via `# schema: V1.1` test pin; (C) `override_reason` enum frozen 5-value (`threshold_too_strict` / `threshold_too_lenient` / `missing_qualitative_context` / `rubric_literal_vs_intent` / `other`); (D) no `dangerous_primitives` renderer partial edits — P+C independently grepped and found no current consumer; (E) `agent_rule_files.total_bytes` dropped from schema entirely (no helper); (F) 23-row signal ID vocabulary frozen with question-scoped prefix (`q1_` / `q2_` / `q3_` / `q4_` / `c20_`), exported as `compute.SIGNAL_IDS` frozenset. **V1.2 implementation scope** per CONSOLIDATION §7: schema + harness additions (`has_issues_enabled`, `primary_language`, `topics`, `fork_count`) + compute demotion + validator override-gate + scorecard partial path change + `migrate-v1.1-to-v1.2.py`. Under-a-week deliverable. Post-V1.2 watchpoints (V1.3 and V1.2.x) logged in CONSOLIDATION §8 (override-pattern telemetry trigger: 3 V1.2 scans shipped; 11-scan comparator analysis trigger: V1.2 frozen + telemetry + ≥11 V1.2 scans; community-norms enum expansion trigger: ≥3 missing-qualitative-context overrides citing community norms).
- **Schema hardening** (Codex R2 defer-ledger) — `scan-schema.json` V1.1 doesn't fully formalize the prompt output spec. Gaps: Scanner Integrity section 00 hit-level structure; Section 08 methodology fields beyond version marker. Trigger: after Step G surfaces concrete schema pain.
- **`github-scan-package-V2/` V2.5 refresh** — full docs + renderer sync to package. Trigger: after Step G passes acceptance.
- **V1.1+ roadmap items** (from `docs/board-review-pipeline-methodology.md`): RD1 (automate structured LLM), SD2 (kind+domain typing), RD4 (assumptions field), ~~PD3 (bundle validator)~~ **shipped 2026-04-19 as U-5/PD3** (`885bdcf`), SD3/SD4/SD7/SD8 (V1.2 schema items), SD9/SD10/RD5/PD1/PD4/PD6/PD7 (V2.0+). All triggers documented in the methodology record; none other than PD3 yet fired.
- **Terminology cleanup** (Codex R3 trailing dissent) — Operator Guide §8.1/§8.2 body prose still contains legacy "Path A/B" in explanatory text. Collision bug already fixed in wizard; lingering prose is cleanup, not urgent.
- **Catalog dual-label cosmetic** (Pragmatist R3 noted) — `methodology-used: path-a (continuous)` dual-label is transitional. Footnote-only variant possible later.
- **Haiku 4.5 for V2.5-preview schema-constrained work** — post-Step-G optimization candidate. Assessment 2026-04-19: Haiku too limited for end-to-end V2.4 (synthesis reasoning depth + multi-document consistency), but potentially viable for V2.5-preview since the schema externalizes most of the decision surface. Trigger: after Step G produces a stable V2.5-preview baseline to compare against.
- **V2.4 authorial-variant inventory** (deprecated by the template-is-DOM-contract rule) — 3 variants documented across the catalog (prefix h3, suffix h3, header-span + bare h3). The canonical template is the contract going forward; future delegated scans should fill it verbatim. See `CLAUDE.md` Delegated-mode directive.
- **AT-T2 Alarm-tuning Tier 2 board-review queue** — session 8, 2026-04-30. Per the alarm-calibration pass on ghostty / Baileys / Archon V2.4 / Archon V2.5-preview. Tier 1 (authoring-rubric + template polish) shipped this session on `chore/alarm-tuning-tier1`. Tier 2 items require board review before landing because they shift calibration that affects every report:
  - **AT-T2.1 H1 colored-repo-name treatment** — `<h1>owner/<span class="amber|red">repo</span></h1>` paints the repo name itself by verdict color. Visually loud; conflates "repo identity" with "verdict alarm." Options: remove the colored span, soften the color, or move the verdict signal entirely to the scan-strip dot.
  - **AT-T2.2 `.critical` CSS gradient + glow intensity** — current treatment stacks red gradient background + radial-gradient backdrop + box-shadow glow. Genuinely-critical scans (Baileys ToS-violation library) earn this; rule-fired-Critical scans (governance-only C20 with no exploitable code finding) inherit the same intensity. Calibration shift.
  - **AT-T2.3 `.critical.governance-only` CSS variant** — new visual taxonomy for "Critical fired via C20 with no code/CVE finding." Requires rubric for when the variant applies (probably: `phase_4b_computed.verdict.level == 'Critical'` AND no finding has `kind='Vulnerability'` AND `kind='Supply-Chain'` is governance-only). Pairs with AT-T2.2.
  - **AT-T2.4 Scorecard cell rubric — preserve more "Partly — ..." amber when signal mix is mixed** — reduces all-red Q1/Q2/Q3/Q4 walls (Baileys is the first such scan). Calibration shift; could change verdicts on borderline scans.
  - **AT-T2.5 Multi-pathway install-axis split rubric** — owner observation 2026-04-30. Archon V2.4 split on (audience × deployment) with two entries that drove materially different actions (`Install pinned to a tagged release...` vs `Do not run in production until PR #1250 merges`). The schema already supports N entries in `split_axis_decision.entries[]`; the gap is authoring rubric for richer slicing — Local-Windows / Local-Mac / VPS / Container as separate audiences when the install path or threat model differs by OS or deployment context. More authoring work but materially better UX. Decide: does the rubric require multi-axis splits when (and only when) actions diverge across pathways?
  - **AT-T2.6 Single-verdict template fallback** — non-split scans currently render `<h2>{verdict_level}</h2>` (echo of badge) + `<div>See findings below for details.</div>` (filler). Tier 1 §11b mitigates via the editorial-caption rubric, but the template fallback itself is suboptimal. Options: schema field for `verdict_headline` / `verdict_summary` (always-on, replaces the echo+filler); template-side reach into `verdict_exhibits.groups[0].headline` for the H2; or just suppress the echo+filler entirely.
  - **AT-T2.7 Carry split-verdict descriptive prefix through V1.2 schema** — Archon V2.4 had verdict label `"Split verdict · governance gap"` (line 883 of original Archon HTML). V2.5-preview reduced to just `"Critical"` because schema has no field for the descriptive prefix. Information loss. Small additive schema change (`split_axis_decision.label_qualifier` or similar).
  - **Pre-board prep**: re-render of ghostty + Baileys + skills (and 1-2 Critical-via-governance-only scans) using a ★proposed★ branch with AT-T2.1/.2/.3 changes applied; comparison artifacts feed the R1 brief.

---

## 3. File/folder index + release status

Release status key:
- `release-ready` — ships with the open-source release
- `staged-v2.4` — ships as V2.4 distributable; post-Step-G refresh will bump to V2.5
- `corpus` — example scans / test fixtures; ships as demonstration material
- `governance` — board review archives; ships as transparent-dev evidence
- `dev-only` — useful in-repo but NOT in open-source release
- `historical` — older state, kept for reference but not a product concern
- `excluded` — runtime / scratch; should be gitignored

### 3.1 Product core (release-ready)

| Path | Purpose |
|---|---|
| `README.md` | Top-level OSS entry point (rewritten session 8) |
| `CLAUDE.md` | Repo operator instructions + scan wizard |
| `REPO_MAP.md` | This file — navigation + release status + board runbook |
| `AUDIT_TRAIL.md` | Checkpoint log + revert recipes |
| `WILD-SCAN-PROCESS.md` | End-to-end map of the scan flow (session 8 NEW) |
| `.gitignore` | Git hygiene |
| `docs/SCANNER-OPERATOR-GUIDE.md` | V0.2 end-to-end operator process |
| `docs/Scan-Readme.md` | V2.4 human-readable wizard |
| `docs/repo-deep-dive-prompt.md` | V2.4 scanner prompt (investigation + output-format spec) |
| `docs/GitHub-Repo-Scan-Template.html` | V2.4 HTML DOM template |
| `docs/scanner-design-system.css` | 824-line mandatory CSS |
| `docs/validate-scanner-report.py` | Validator (`--report`, `--parity`, `--markdown`, `--form`, `--bundle`) |
| `docs/compute.py` | Python compute for Phase 3 automatable fields |
| `docs/phase_1_harness.py` | Phase 1 automated harness |
| `docs/render-md.py` | V2.5-preview MD renderer (117-line Jinja2 shim) |
| `docs/render-html.py` | V2.5-preview HTML renderer (135-line Jinja2 shim) |
| `docs/compare-severity-distribution.py` | D-6 severity-distribution comparator |
| `docs/scan-schema.json` | **V1.2** investigation form schema (V13-1 + V1.2.x signal widening) |
| `docs/templates/` | V2.5-preview MD Jinja2 partials (14 files) |
| `docs/templates-html/` | V2.5-preview HTML Jinja2 partials (14 files) |
| `docs/scan-authoring-template/` | **NEW (session 8)** Per-scan Phase 4/5/6 authoring templates + README |
| `docs/delegated-scan-template.md` | Delegated-mode scan handoff template (was `board-review-data/path-b-test-prompt.md`) |
| `docs/board-review-pipeline-methodology.md` | Canonical 8/8/4 + 9-phase architecture record |
| `docs/scanner-catalog.md` | Live 27-entry catalog table |
| `docs/v12-wild-scan-telemetry.md` | Cross-scan analysis (12 V1.2 wild scans) |
| `docs/v13-1-override-telemetry-analysis.md` · `v13-3-analysis.md` · `v13-3-fp-dry-run.md` | Frozen telemetry analyses |
| `docs/phase-1-checklist.md` | Step→field mapping for the harness |
| `docs/CHANGELOG.md` | Prompt version history |
| `tests/test_*.py` (9 files) | Test suite — 414/414 passing |
| `tests/fixtures/{zustand,caveman,archon-subset}-form.json` | Canonical V1.1/V1.2 form structural fixtures |
| `tests/fixtures/provenance.json` | Fixture provenance ledger |

### 3.2 Package V2.4 distributable (staged)

`github-scan-package-V2/` — 16 tracked files, self-contained V2.4 release snapshot.

| Path | Status | Notes |
|---|---|---|
| `github-scan-package-V2/CLAUDE.md` | staged-v2.4 | 119 lines, V2.4 Package header. Intentionally drifted from repo `CLAUDE.md` post-U-1. |
| `github-scan-package-V2/SCANNER-OPERATOR-GUIDE.md` | staged-v2.4 | Byte-identical to `docs/SCANNER-OPERATOR-GUIDE.md` BEFORE U-1. Now drifted (no §8.8). |
| `github-scan-package-V2/validate-scanner-report.py` | staged-v2.4 | ✅ Synced to repo in `60e0bf2` (FX-3 + FX-3b bug fixes; not V2.5 features) |
| `github-scan-package-V2/GitHub-Repo-Scan-Template.html` | staged-v2.4 | 10-line drift vs repo |
| `github-scan-package-V2/scanner-design-system.css` | staged-v2.4 | Byte-identical to repo |
| `github-scan-package-V2/repo-deep-dive-prompt.md` | staged-v2.4 | 24-line drift vs repo (repo has V2.5-preview blockquote) |
| `github-scan-package-V2/Scan-Readme.md` | staged-v2.4 | 102-line drift (old V2.3 / Path A/B terminology) |
| `github-scan-package-V2/scanner-catalog.md` | staged-v2.4 | 6 entries (repo has 10). Drift is intentional snapshot. |
| `github-scan-package-V2/CHANGELOG.md` | staged-v2.4 | Prompt version history |
| `github-scan-package-V2/reference/*` | staged-v2.4 | Reference scans bundled with package |

**Post-Step-G**: a dedicated "V2.5 package refresh" commit cycle will sync the package to current repo state (docs + renderer files + fixtures + schema) and bump to `github-scan-package-V2.5/` or similar.

### 3.3 Corpus (release-ready as demonstration)

| Path | Purpose |
|---|---|
| `docs/scans/catalog/GitHub-Scanner-<repo>.{md,html}` (27 scans × 2 formats; Archon-rerun-record .md only) | All catalog-referenced rendered scans |
| `docs/scans/catalog/README.md` | Index + designates `ghostty-v12` as the gold-standard exemplar |
| `docs/scan-bundles/<repo>-<sha>.json` | Form.json bundles (durable per-scan record) |
| `docs/scanner-catalog.md` | Live 27-entry catalog table (mutates each scan) |

### 3.4 Governance / transparent dev (release-ready)

`docs/External-Board-Reviews/README.md` is the master index. As of session 8, it covers 11 archived reviews:

| Review | Scope |
|---|---|
| `041626-celso/` | V2.3 pre-migration review |
| `041826-renderer-alignment/` | Phase 7 plan A-G |
| `041826-renderer-impl-verify/` | Step A+B + STEP-E/STEP-F verification records + INDEX |
| `041826-fixture-enrichment/` | Step C 10-FA review |
| `041826-step-f-alignment-validation/` | Step F R3 fixes review |
| `041826-step-g-kickoff/` | U-1 doc integration |
| `041926-step-g-execution/` | Step G acceptance approach (FN-1..FN-9 + 15 dispositions + 8 adjustments) |
| `042026-schema-v12/` | D-7 + D-8 → V1.2 schema landing (3 rounds + owner directives) |
| `042026-sf1-calibration/` | SF1 scorecard calibration board (4-round split-verdict) |
| `042026-v13-3-comparator-calibration/` | n=11 V1.2 comparator-calibration analysis (3 rounds + OD-4 owner directive + Codex code-review gate) |
| `050126-calibration-rebuild/` | Phase 2 of `docs/back-to-basics-plan.md` — calibration design v2 board review. 3 rounds + 16 owner directives + 26-item dissent audit (zero silent drops). 3-of-3 R3 SIGN OFF. DeepSeek moved DISSENT (R1) → SIGN OFF WITH NOTES (R2/R3). |

### 3.5 Archive (`docs/archive/`) — historical, kept for reference

Per session 8 cleanup, all pre-current-layout artifacts moved to `docs/archive/`. See `docs/archive/README.md` for the full map. Subdirs:

| Subdir | Contents |
|---|---|
| `docs/archive/prompts/` | Older scanner-prompt versions (V2, V2.1, V2.2). Current is `docs/repo-deep-dive-prompt.md` (V2.4). |
| `docs/archive/board-reviews-pre-layout/` | Pre-`External-Board-Reviews/` consolidations (V2.1/V2.2/V2.3 + AXIOM triage + V0.1 operator-guide + V2.4 package reviews). |
| `docs/archive/board-review-temp-orphans/` | 14 R1/R2 brief + agent-response files committed to `.board-review-temp/` before that dir was added to `.gitignore`. Subdir has its own README. |
| `docs/archive/board-review-data-pre-layout/` | Older `docs/board-review-data/` artifacts (axiom-triage-responses, V1 external board brief, V2 package audit + review brief, corrected-MD-structure analysis). |
| `docs/archive/migrations/` | One-time migration scripts that have already executed (e.g., `migrate-v1.1-to-v1.2.py`). |
| `docs/archive/scans-superseded/` | Scan outputs not promoted to catalog OR superseded (agency-agents, open-lovable, zustand-v2). |
| `archive/` (top-level, distinct from `docs/archive/`) | Old TypeScript static analyzer (101 files, pre-pivot). `historical — release-optional`. |

### 3.6 Scratch / runtime (gitignored)

| Path | Purpose |
|---|---|
| `.board-review-temp/` | Active FrontierBoard review scratch (R1/R2/R3 briefs + agent responses + raw logs). Per-review subdirs; archived to `docs/External-Board-Reviews/<MMDDYY>-<topic>/` on sign-off. |
| `.scan-workspaces/<repo>/` | **NEW (session 8)** Per-scan authoring workspaces (`build_form.py` + `author_phase_*.py` + `phase-1-raw.json` + `form.json`). Templates at `docs/scan-authoring-template/`. |
| `**/__pycache__/` | Python bytecode cache |
| `.claude/scheduled_tasks.lock` | Claude Code runtime lock |
| `*.tar.gz`, `*.zip` | Release artifacts (must be regenerated, not committed) |
| `.archon/` | Archon integration tracker (`.board-review-hash`, `.fb-upstream-hash`, `commands/`, `workflows/`). Repo-local; not core to scanner; flag for `.releaseignore` when packaging the OSS distribution. |
| `.claude/skills/` | Repo-local Claude Code skills (1 tracked file: `board-review/SKILL.md`). Ships with repo. |

---

## Maintenance

- **When to update this file:** on any commit that adds/removes a tracked file from the product-core list, or changes a directory's release status. Run `git log -1 --format='%ai' -- <path>` on each listed file to refresh timestamps.
- **When to audit the release plan:** before each release (V2.4, V2.5, etc.). Confirm every `release-ready` entry is current; every `excluded` is gitignored.
- **Cross-references:** `CLAUDE.md` Navigation block · `AUDIT_TRAIL.md` for checkpoint history · `docs/External-Board-Reviews/README.md` for board-review master index.
