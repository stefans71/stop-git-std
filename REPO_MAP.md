# Repository Map — stop-git-std

**Last audited:** 2026-04-19 03:47 UTC
**HEAD at audit:** `3c09afb` (U-3/FX-4: fixture provenance landed)
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

`docs/scanner-catalog.md` lists entries 1–10 (all `rendering-pipeline: v2.4`). Artifacts at `docs/GitHub-Scanner-<repo>.{html,md}`. Shape coverage: curl-pipe installer (caveman), agentic platform (Archon), JS library (zustand), Rust CLI (fd), Claude-Code skills (gstack), pre-distribution (archon-board-review), Python platform (hermes-agent), web app (postiz-app), plus zustand-v2/v3 revisions + Archon rerun record.

### 1.4 Historical / backfilled artifacts

- `docs/repo-deep-dive-prompt-V2.md` · `V2.1.md` · `V2.2.md` — prompt version archives (current is V2.4 at `docs/repo-deep-dive-prompt.md`)
- `docs/CHANGELOG.md` — prompt version history (V2.1→V2.4)
- `docs/GitHub-Repo-Scan-Form.json` — (check purpose; may be a backfilled artifact)
- `archive/` — old TypeScript static analyzer (101 files, historical; see §3.5)

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

- **HEAD:** session 4 close commit (pending) on top of `4ad4cf6` (Phase 1 tooling) on top of `c0f6dc2` (session 3 close). **V2.5-preview production-cleared.**
- **Tests:** 319/319 passing (289 session-3 + 30 new Phase 1 harness tests under `tests/test_phase_1_harness.py::TestPhase1Harness`).
- **Validator on all V2.5-preview outputs:** `--report` + `--parity` clean on every MD + HTML (4 pairs: zustand-v3, caveman, Archon, markitdown).
- **Parity sweep:** 17/17 MD+HTML pairs clean (13 V2.4 catalog + 4 v2.5-preview).
- **Repo↔package validator:** byte-identical (no package change this session).
- **CSS:** 824 lines (unchanged).
- **Catalog:** 15 entries — 11 `v2.4` + 4 `v2.5-preview`: 3 Step G validation (entries 12-14: zustand-v3, caveman, Archon) + 1 wild (entry 15: markitdown).
- **V2.5-preview status: PRODUCTION-CLEARED 2026-04-20.** Step G acceptance 3/3 + first wild scan (microsoft/markitdown, 112k stars, Python monorepo — outside 3 validated shapes) cleared all 7 applicable gates using harness-gathered Phase 1. Phase 1 is now automated via `docs/phase_1_harness.py` (runs V2.4 prompt Steps 1-8 + A/B/C: gh api + OSSF + osv.dev + gitleaks + package registries + tarball + local grep + README paste scan). Spec at `docs/phase-1-checklist.md`. 30 new tests. D-8 open: harness output is richer than V1.1 schema accepts; current bridge is sidecar (`.board-review-temp/markitdown-scan/phase-1-raw-full.json`) + transformer (`.board-review-temp/markitdown-scan/transform_harness.py`); V1.2 schema hardening is the durable fix.
- **Cross-repo FrontierBoard SOP update** (pushed to stefans71/FrontierBoard main as `e01303a`): pre-archive dissent audit gate mandatory SOP requirement. Canonical at `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md` and `/root/tinkering/FrontierBoard/Git-030126/docs/REVIEW-SOP.md`.

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

- **D-7 + D-8 → Schema V1.2 (design frozen 2026-04-20, implementation pending)** — co-scheduled board review closed 2026-04-20. 3/3 SIGN OFF with owner directives. See `docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` for the canonical record (31-item dissent audit: 14 resolved + 5 deferred with triggers + 9 live preserved dissents + 3 moot; zero silent drops). **Directives:** D1 Q3=B1 harness-canonical (transformer deleted; schema adopts harness names `archived`/`fork`/`default_branch`/etc. + harness shapes natively including nested per-family `dangerous_primitives` + `{verified,total}` for `distribution_channels_verified`); D2 new top-level `phase_3_advisory.scorecard_hints` (keyed object by question ID), `phase_4_structured_llm.scorecard_cells` gains `{rationale, edge_case, suggested_threshold_adjustment, computed_signal_refs, override_reason}`, `phase_3_computed.scorecard_cells` deleted. **Six R3 item resolutions:** (A) override-rationale validator = refs-only + 50-char floor + enum check (no substring requirement); (B) migration script migrates 3 active fixtures only, `step-g-failed-artifact` entries stay V1.1 via `# schema: V1.1` test pin; (C) `override_reason` enum frozen 5-value (`threshold_too_strict` / `threshold_too_lenient` / `missing_qualitative_context` / `rubric_literal_vs_intent` / `other`); (D) no `dangerous_primitives` renderer partial edits — P+C independently grepped and found no current consumer; (E) `agent_rule_files.total_bytes` dropped from schema entirely (no helper); (F) 23-row signal ID vocabulary frozen with question-scoped prefix (`q1_` / `q2_` / `q3_` / `q4_` / `c20_`), exported as `compute.SIGNAL_IDS` frozenset. **V1.2 implementation scope** per CONSOLIDATION §7: schema + harness additions (`has_issues_enabled`, `primary_language`, `topics`, `fork_count`) + compute demotion + validator override-gate + scorecard partial path change + `migrate-v1.1-to-v1.2.py`. Under-a-week deliverable. Post-V1.2 watchpoints (V1.3 and V1.2.x) logged in CONSOLIDATION §8 (override-pattern telemetry trigger: 3 V1.2 scans shipped; 11-scan comparator analysis trigger: V1.2 frozen + telemetry + ≥11 V1.2 scans; community-norms enum expansion trigger: ≥3 missing-qualitative-context overrides citing community norms).
- **Schema hardening** (Codex R2 defer-ledger) — `scan-schema.json` V1.1 doesn't fully formalize the prompt output spec. Gaps: Scanner Integrity section 00 hit-level structure; Section 08 methodology fields beyond version marker. Trigger: after Step G surfaces concrete schema pain.
- **`github-scan-package-V2/` V2.5 refresh** — full docs + renderer sync to package. Trigger: after Step G passes acceptance.
- **V1.1+ roadmap items** (from `docs/board-review-pipeline-methodology.md`): RD1 (automate structured LLM), SD2 (kind+domain typing), RD4 (assumptions field), ~~PD3 (bundle validator)~~ **shipped 2026-04-19 as U-5/PD3** (`885bdcf`), SD3/SD4/SD7/SD8 (V1.2 schema items), SD9/SD10/RD5/PD1/PD4/PD6/PD7 (V2.0+). All triggers documented in the methodology record; none other than PD3 yet fired.
- **Terminology cleanup** (Codex R3 trailing dissent) — Operator Guide §8.1/§8.2 body prose still contains legacy "Path A/B" in explanatory text. Collision bug already fixed in wizard; lingering prose is cleanup, not urgent.
- **Catalog dual-label cosmetic** (Pragmatist R3 noted) — `methodology-used: path-a (continuous)` dual-label is transitional. Footnote-only variant possible later.
- **Haiku 4.5 for V2.5-preview schema-constrained work** — post-Step-G optimization candidate. Assessment 2026-04-19: Haiku too limited for end-to-end V2.4 (synthesis reasoning depth + multi-document consistency), but potentially viable for V2.5-preview since the schema externalizes most of the decision surface. Trigger: after Step G produces a stable V2.5-preview baseline to compare against.
- **V2.4 authorial-variant inventory** (deprecated by the template-is-DOM-contract rule) — 3 variants documented across the catalog (prefix h3, suffix h3, header-span + bare h3). The canonical template is the contract going forward; future delegated scans should fill it verbatim. See `CLAUDE.md` Delegated-mode directive.

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

| Path | Purpose | Status | Last touched |
|---|---|---|---|
| `CLAUDE.md` | Repo operator instructions (cap 250 lines) | release-ready | 2026-04-19 |
| `REPO_MAP.md` | This file — navigation + release status + board runbook | release-ready | 2026-04-19 |
| `AUDIT_TRAIL.md` | Checkpoint log + revert recipes | release-ready | 2026-04-19 |
| `README.md` | Top-level repo intro | release-ready | 2026-04-17 |
| `.gitignore` | Git hygiene | release-ready | 2026-04-13 |
| `docs/SCANNER-OPERATOR-GUIDE.md` | V0.2 end-to-end operator process | release-ready | 2026-04-19 |
| `docs/Scan-Readme.md` | V2.4 human-readable wizard | release-ready | 2026-04-19 |
| `docs/repo-deep-dive-prompt.md` | V2.4 scanner prompt (investigation + output-format spec) | release-ready | 2026-04-19 |
| `docs/GitHub-Repo-Scan-Template.html` | V2.4 HTML template with placeholders | release-ready | 2026-04-17 |
| `docs/scanner-design-system.css` | 824-line mandatory V2.4 CSS | release-ready | 2026-04-17 |
| `docs/validate-scanner-report.py` | Validator (`--report`, `--parity`, `--markdown`, `--template`) | release-ready | 2026-04-18 |
| `docs/compute.py` | Python compute for Phase 3 automatable fields | release-ready | 2026-04-18 |
| `docs/render-md.py` | V2.5-preview MD renderer (117-line Jinja2 shim) | release-ready | 2026-04-18 |
| `docs/render-html.py` | V2.5-preview HTML renderer (135-line Jinja2 shim) | release-ready | 2026-04-18 |
| `docs/scan-schema.json` | V1.1 investigation form schema | release-ready | 2026-04-18 |
| `docs/templates/` | V2.5-preview MD Jinja2 partials (14 files) | release-ready | 2026-04-18 |
| `docs/templates-html/` | V2.5-preview HTML Jinja2 partials (14 files) | release-ready | 2026-04-18 |
| `tests/test_compute.py` | Phase 3 compute tests | release-ready | 2026-04-18 |
| `tests/test_validator.py` | Validator unit tests | release-ready | 2026-04-18 |
| `tests/test_render_md.py` | MD renderer structural tests | release-ready | 2026-04-18 |
| `tests/test_render_html.py` | HTML renderer structural tests | release-ready | 2026-04-18 |
| `tests/test_end_to_end.py` | End-to-end integration tests | release-ready | 2026-04-18 |
| `tests/fixtures/zustand-form.json` | V1.1 fixture — JS library shape | release-ready | 2026-04-18 |
| `tests/fixtures/caveman-form.json` | V1.1 fixture — curl-pipe installer shape | release-ready | 2026-04-18 |
| `tests/fixtures/archon-subset-form.json` | V1.1 fixture — agentic monorepo + C3 auto_load_tier path | release-ready | 2026-04-18 |
| `tests/fixtures/provenance.json` | Fixture provenance ledger (keyed by filename) | release-ready | 2026-04-19 |

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

| Path | Purpose | Status |
|---|---|---|
| `docs/GitHub-Scanner-<repo>.{md,html}` (10 scans × 2 formats) | Completed V2.4 catalog scans | corpus |
| `docs/GitHub-Scanner-Archon-rerun-record.md` | Determinism record for Archon dev-SHA bump | corpus |
| `docs/scanner-catalog.md` | Live catalog (10 entries, rendering-pipeline column) | release-ready (mutates each scan) |

### 3.4 Governance / transparent dev (release-ready)

| Path | Purpose | Status |
|---|---|---|
| `docs/External-Board-Reviews/README.md` | Master index of all board reviews | governance |
| `docs/External-Board-Reviews/041626-celso/` | V2.3 pre-migration review | governance |
| `docs/External-Board-Reviews/041826-renderer-alignment/` | Phase 7 plan A-G | governance |
| `docs/External-Board-Reviews/041826-renderer-impl-verify/` | Step A+B + STEP-E/STEP-F verification records + INDEX | governance |
| `docs/External-Board-Reviews/041826-fixture-enrichment/` | Step C 10-FA review | governance |
| `docs/External-Board-Reviews/041826-step-f-alignment-validation/` | Step F R3 fixes review | governance |
| `docs/External-Board-Reviews/041826-step-g-kickoff/` | U-1 doc integration | governance |
| `docs/board-review-pipeline-methodology.md` | Canonical 8/8/4 + 9-phase architecture record | release-ready (referenced everywhere) |

### 3.5 Historical / pre-current-layout (keep in repo, release-optional)

| Path | Purpose | Status |
|---|---|---|
| `docs/board-review-V21-consolidation.md` / `V22` / `V23` | Older board reviews, pre-`External-Board-Reviews/` layout | historical |
| `docs/board-review-axiom-triage-consolidation.md` + R2 | AXIOM findings triage (V2.3 era) | historical |
| `docs/board-review-operator-guide-consolidation.md` | V0.1 operator guide review | historical |
| `docs/board-review-package-v2-consolidation.md` | V2.4 package review | historical |
| `docs/repo-deep-dive-prompt-V2.md` / `V2.1.md` / `V2.2.md` | Prompt version archives | historical |
| `docs/CHANGELOG.md` | Prompt version changelog | release-ready (references archives) |
| `archive/` | Old TypeScript static analyzer (101 files, pre-pivot) | historical — release-optional as "previous iteration" evidence; can also be excluded |
| `docs/board-review-data/` | Older bundles + path-b-test-prompt.md (23 files) | dev-only (pre-`External-Board-Reviews/` staging area) |
| `docs/GitHub-Repo-Scan-Form.json` | Unclear purpose — pre-schema artifact | dev-only (investigate before release) |

### 3.6 Scratch / runtime (excluded)

| Path | Why excluded |
|---|---|
| `.board-review-temp/` | Session scratch for active board reviews. Should add to `.gitignore`. Currently untracked but visible. |
| `docs/__pycache__/` · `tests/__pycache__/` | Python bytecode cache. Should add to `.gitignore`. |
| `.claude/scheduled_tasks.lock` | Runtime lock. Should add to `.gitignore`. |
| `github-repo-scanner-v2.3.tar.gz` · `.zip` | Release artifacts. Should add to `.gitignore`. |
| `.archon/` | Archon integration data (7 files). Release-status depends on whether Archon is a shipping dependency — flag for review. |

**Recommended `.gitignore` additions:**
```
.board-review-temp/
**/__pycache__/
.claude/scheduled_tasks.lock
*.tar.gz
*.zip
```

---

## Maintenance

- **When to update this file:** on any commit that adds/removes a tracked file from the product-core list, or changes a directory's release status. Run `git log -1 --format='%ai' -- <path>` on each listed file to refresh timestamps.
- **When to audit the release plan:** before each release (V2.4, V2.5, etc.). Confirm every `release-ready` entry is current; every `excluded` is gitignored.
- **Cross-references:** `CLAUDE.md` Navigation block · `AUDIT_TRAIL.md` for checkpoint history · `docs/External-Board-Reviews/README.md` for board-review master index.
