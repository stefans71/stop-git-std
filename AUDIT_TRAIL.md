# Audit Trail — Known-Good Checkpoints

Canonical log of milestone commits with the verification state captured at commit time. Purpose: if something breaks, grep this file to find the last known-good state and revert cleanly.

**Conventions:**
- One checkpoint per significant milestone (not per commit).
- Timestamps are canonical commit timestamps from `git log -1 --format='%ai'`.
- Verification state reflects what was tested AT THAT COMMIT, not retroactively.
- Board approval links point to the `CONSOLIDATION.md` authorizing the milestone.
- "Revert to this state" command is `git reset --hard <sha>` — **destructive**; confirm before running.

**Recovery workflow:**
1. Identify the symptom. Recent regression? Check the most recent checkpoint first.
2. Find the last checkpoint where verification was green.
3. Compare `git diff <checkpoint-sha>..HEAD` to see what changed.
4. Revert or cherry-pick as needed.

---

## Checkpoint — 2026-05-02 (session 13) — First post-rebuild scan: multica re-scan (catalog entry 28)

**HEAD:** TBD (filled by post-commit). Tree clean before commit; `docs/scan-bundles/multica-3df95c8.json` + 3 rendered outputs in `docs/scans/catalog/` + scanner-catalog.md row 28 + v12-wild-scan-telemetry.md §1 entry 28 + §10 changelog entry queued.

**Scan target:** multica-ai/multica @ HEAD `3df95c84b8af6f26b6d4fe8ccfcaca74ee977cf1` (pushed 2026-05-01T21:27:22Z). **Re-scan of catalog entry 11** (V2.4 / delegated, 2026-04-19, HEAD `b8907dd`).

**Pipeline:** V2.5-preview / continuous. All 6 phases ran in single session.
- Phase 0: workspace + head-sha.txt (first durable artifact) at `/tmp/scan-multica/`.
- Phase 1: `docs/phase_1_harness.py` — 28 fields populated.
- Phase 2: sanity (SHA consistent, dates chronological, tarball nonempty).
- Phase 3: `compute.py` — shape `library-package` (publishable npm manifest matched first; structurally agentic-platform — diagnosis owed); 4 advisory cells Q1=red Q2=red Q3=red Q4=amber via FALLBACK rules; C20 governance Warning.
- Phase 4: 7 findings authored (5 Warning + 2 Info), 14 evidence entries, 4 scorecard cells (Q1 red ALIGN / Q2 amber OVERRIDE `missing_qualitative_context` / Q3 red ALIGN / Q4 amber ALIGN), split-axis split (cloud CLI vs self-host operator).
- Phase 5: long-form MD (593 lines, 48 KB) + Simple HTML (356 lines, 17 KB self-contained) + Simple MD (32 lines, 2.6 KB) at `docs/scans/catalog/GitHub-Scanner-multica-v25preview*`.
- Phase 6: validator clean — `--report` exit 0 on all 3 outputs; `--form` exit 0 with V1.2 schema CLEAN + gate 6.3 (1 override explained) + gate v2.1 (rule_id present).

**Verdict:** **Caution (split — cloud CLI consumer vs self-host operator)**. Both Caution but self-host carries more config-discipline responsibility.

**Verdict shifts vs prior 2026-04-19 entry 11:**
- **888888 dev-verification-code Critical → Warning** (APP_ENV=production gate landed ~2026-04-18 in window between scans; closed issue #1304).
- **New F1 Warning**: install.sh on macOS/Linux skips SHA256 verification on binary download; install.ps1 on Windows DOES verify checksums.txt — Windows/Unix asymmetry.
- **New F2 Warning**: `protect-main-branch` ruleset declared since 2026-01-15 but `enforcement: disabled` — visible-but-toothless.
- **New F4 Warning**: open issue #1114 (16d) `isBlockedEnvKey allows LD_PRELOAD/NODE_OPTIONS/HTTP_PROXY override via custom_env` — agent-execution privilege escalation, unaddressed since prior scan.
- **Counter-signal**: 5 security issues closed in past 8 days (888888 #1304, shell.openExternal #1115, Hermes filterCustomArgs #1113, /health/realtime #1606, open-redirect #1116) — responsive but queue not shrinking.

**Telemetry deltas:**
- N=13/25 toward V13-3 broadened re-trigger (was 12).
- 11 overrides across 13 wild scans (was 10/12).
- `missing_qualitative_context` × 2 (was × 1) — second consecutive use after skills entry 27. Different driver (skills = sample-floor degeneracy at n=1 PR; multica = closed-within-window counter-signal invisible to compute). Solidifies the case that the enum value covers a real phenomenon class. New V12x backlog item (V12x-16) candidate: weight `closed_within_window` as a Q2 advisory counter-signal.
- Shape misclassification noted: classify_shape() picked `library-package` (publishable npm manifest matched at Step 8) — multica is structurally `agentic-platform`. Diagnosis owed for next session.

**Verification:** 609/609 tests still passing (no source changes). `--report` clean on all 3 outputs. `--form` 0 errors + gate 6.3 + gate v2.1 clean. Operator Guide + CLAUDE.md timestamp convention applied to all modified docs.

**Files committed this session:**
- `docs/scan-bundles/multica-3df95c8.json` (new — 291 KB; bundle preserved per durability rule).
- `docs/scans/catalog/GitHub-Scanner-multica-v25preview.md` (new, 48 KB).
- `docs/scans/catalog/GitHub-Scanner-multica-v25preview-simple.html` (new, 17 KB).
- `docs/scans/catalog/GitHub-Scanner-multica-v25preview-simple.md` (new, 2.6 KB).
- `docs/scanner-catalog.md` (entry 28 added; counts updated 27→28 / 16 v2.5-preview→17; changelog appended; **Last updated:** added).
- `docs/v12-wild-scan-telemetry.md` (§1 roster entry 28; §10 changelog entry; header N=13; **Last updated:** updated).
- `AUDIT_TRAIL.md` (this checkpoint).

---

## Checkpoint — 2026-05-01 (session 12) — Phase 6 + Phase 7 COMPLETE + MERGED → back-to-basics rebuild CLOSED

**HEAD:** post-Phase-7 merge on `origin/main` (filled by post-merge §Current state update; precise SHA recorded in plan §Current state). Back-to-basics calibration rebuild Phases 0-7 all landed. Tree clean. **Plan complete.**

**Phase 6 — MD calibration verification.** Branch `chore/calibration-md-verification` from `5d4ed3b` (Phase 5 close), merged `092b0a3` no-ff. 5 cold-fork consumer tests on rendered MD for catalog entries 16 ghostty / 26 Baileys / 27 skills / 20 browser_terminal / 24 freerouting. **Result: 5 of 5 match.** Pass bar (≥4) cleared.

**Phase 7 — Simple Report HTML.** Branch `feat/simple-report` from post-Phase-6 main. Six commits:
- `e7ce7af` — concept brief `docs/simple-report-concept.md` (329 lines authored from owner-supplied design intent via path γ).
- `ddda083` — implementation: `docs/render-simple.py` + `docs/templates-simple/{simple-report.html.j2,simple-report.md.j2,simple-report.css}` (CSS = 251-line subset of 824-line scanner-design-system) + `tests/test_render_simple.py` (22 tests) + 3 representative sample scans (ghostty/Baileys/skills).
- `fc36117` — §Current state for Phase 7 close (pre-final-decisions).
- `3aa93e1` — workflow integration: 3 owner directives applied to CLAUDE.md (Q3a flip, Q1 reframe, post-scan options) + Operator Guide §4 + §8 Phase 4 contract (4a render-md REQUIRED / 4b render-simple REQUIRED / 4c render-html OPTIONAL / 4d re-run OPTIONAL) + concept doc §8 + §10 updates.
- `293f04a` — batch-render 9 remaining V1.2 Simple Reports (Kronos, kamal, Xray-core, browser_terminal, wezterm, QuickLook, kanata, freerouting, WLED). Total 12 Simple Reports landed for catalog entries 16-27.
- (this commit) — housekeeping (REPO_MAP, AUDIT_TRAIL, scanner-catalog) + §Current state PLAN COMPLETE.

**Tests:** 609/609 passing.

**Verdict distribution across the 12 V1.2 Simple Reports:** 7 Critical (Baileys, Kronos, WLED, Xray-core, browser_terminal, freerouting, kanata) + 5 Caution (QuickLook, ghostty, kamal, skills, wezterm). Verdicts unchanged from Phase 5 baseline (verdict-invariance — `compute_verdict` reads stored findings).

**Workflow contract change (durable):** Phase 4 of the 6-phase scan workflow now produces {long-form MD canonical + Simple Report HTML user-facing} as REQUIRED outputs. Long-form HTML is OPTIONAL auditor view via Phase 4c `docs/render-html.py`. CLAUDE.md wizard Q3a default is now V2.5-preview (V2.4 marked legacy, no Simple Report).

**Post-rebuild follow-up backlog** (queued, none blocking):
- V2.4-bundle → form.json adapter (legacy entries 1-11 cannot produce Simple Reports without it).
- Gate 6.3 backlog resolution (7 cells × 6 entries; option (b) `override_reason` or (c) Q3 softener).
- Q3 FALLBACK regression on 5 entries.
- Full-sentence scorecard short_answers (cosmetic; ship-as-fragmentary today).
- Inline customization + light theme + print stylesheet + README badges (deferred design questions).

**Verification:** 609/609 tests passing; all 12 V1.2 Simple Reports rendered cleanly; long-form Phase 5 deliverables unchanged.

---

## Checkpoint — 2026-05-01 (session 10) — Phase 3 implementation COMPLETE + MERGED to main

**HEAD:** `6657e59` on `origin/main` (post-merge pointer cleanup, on top of merge `9d33799`). Phase 3 merged via `9d33799` (no-ff merge of `chore/calibration-rebuild-impl`). 5 P3 commits + 1 merge commit + 1 cleanup commit pushed to origin. Feature branch `chore/calibration-rebuild-impl` deleted local + remote.

**Pre-merge feature-branch tip:** `e45f2e1` (still reachable via `9d33799^2`).

**Session 10 commits from `4127385` (session 9 close on origin/main) →:**
- `4d7b847` P3.a — classify_shape + cross-shape modifier helpers + cell evaluators landed (12/12 §4 gate pass + 46 new tests at `tests/test_classify_shape.py`)
- `b51b6b8` P3.b/c — cell evaluator + orchestrator tests + privileged_tool drift doc (54 new tests at `tests/test_calibration_rules.py`)
- `79f084a` P3.d/e — schema additions (rule_id REQUIRED, shape_classification) + validator gate v2.1 (9 new tests at `tests/test_validator_v2_rule_id.py`)
- `1688ec5` P3.f — regression suite + RULE-6 third sub-condition INERT + `docs/calibration-impl-notes.md` (42 new tests at `tests/test_calibration_regression.py`)
- `e45f2e1` Phase 3 close — persistent-state updates (plan + CLAUDE.md + AUDIT_TRAIL + REPO_MAP). Pre-merge tip.
- `9d33799` Merge of `chore/calibration-rebuild-impl` to `main` (no-ff).
- `6657e59` Post-merge pointer cleanup (HEAD pointers in plan + CLAUDE.md + AUDIT_TRAIL + REPO_MAP corrected from feature-branch tip to merge SHA).

**Verification state at `1688ec5`:**
- 565/565 tests passing (414 baseline + 151 net new in Phase 3)
- §4 12-bundle classification gate: 12/12 expected categories matched
- Override-reduction: 5 of 10 known cells now rule-driven (~50% reduction → hits design hard-floor ≤5/12 ~42%)
- All 5 CONSOLIDATION §5 carry-forwards addressed
- Spec deviations consolidated at `docs/calibration-impl-notes.md` (9 sections)

**Revert paths:**
- Revert just post-merge pointer cleanup: `git revert 6657e59` (safe — only state-doc pointers)
- Revert just P3.f: `git revert 1688ec5` (now on main; conflicts may surface against the merge — prefer reverting the merge if you want all of P3 out)
- Revert P3.d/e schema + validator: `git revert 79f084a`
- Revert P3.b/c tests: `git revert b51b6b8`
- Revert the entire Phase 3 merge: `git revert -m 1 9d33799` (cleanest path — undoes the whole feature)
- Reset to session 9 close on origin: `git reset --hard 4127385` (DESTRUCTIVE — confirm before running; loses the post-merge pointer-cleanup commit too)

**Files touched (session 10):**
- `docs/compute.py` — calibration v2 module added (~1050 lines net new)
- `docs/scan-schema.json` — scorecard_hint optional fields + new shape_classification $def + optional refs
- `docs/validate-scanner-report.py` — gate v2.1 added to check_form
- `docs/calibration-impl-notes.md` — NEW (9 sections, all spec deviations + outcome)
- `tests/test_classify_shape.py` — NEW (46 tests)
- `tests/test_calibration_rules.py` — NEW (54 tests)
- `tests/test_validator_v2_rule_id.py` — NEW (9 tests)
- `tests/test_calibration_regression.py` — NEW (42 tests; pinned per-bundle/per-cell tuples)
- Persistent-state docs (touched in `e45f2e1` + `6657e59`): `docs/back-to-basics-plan.md` §Current state, `CLAUDE.md` Active work pointer, `AUDIT_TRAIL.md` (this file), `REPO_MAP.md` §2.2.

**No code regressions:** existing 414 tests unchanged; legacy `compute_scorecard_cells()` preserved verbatim — calibration v2 is opt-in via the new `compute_scorecard_cells_v2()` entry point.

---

## Checkpoint — 2026-05-01 (session 9) — Back-to-basics calibration rebuild Phases 0+1+2 (board review CLOSED + ARCHIVED)

**HEAD:** `aeb9c76` on origin/main (session 9 — Phase 2 ARCHIVED).

**Session 9 commits from `dff3886` (session 8 close) →:**

```
aeb9c76 Phase 2 ARCHIVED — CONSOLIDATION.md + 15 round files + persistent-state updates
f42635f Phase 2 R3 close — Q2 explicit-deferral doc fix per 3-of-3 convergent note
9d79e23 Plan §Current state: R3 launching (thin ratification)
cb7407c Phase 2 R2 close — design doc revised per 7 R2 owner directives
d01bcf6 Plan §Current state: R2 launching
91cecd5 Phase 2 R1 close — design doc revised per 7 owner directives
c24c782 Phase 2 launch — design doc §9 sharpened (Q4 compound, Q7 decided, Q9 floor)
66c4ace Phase 1 complete — calibration design v2 doc landed
ccd3251 Phase 0 complete — calibration audit landed
7f22f7d Plan: resolve last-commit SHA in § Current state block
f0c9a96 Back-to-basics calibration rebuild plan + CLAUDE.md auto-resume pointer
```

11 session-9 commits before this archive commit. All on `main`. Pre-session-9 baseline at `dff3886`.

**Verification at checkpoint:**
- 414/414 tests passing (no code changes in any session-9 commit; all docs + plan + audit work)
- Phase 0 audit (`docs/calibration-audit.md`, 274 lines) committed
- Phase 1 design (`docs/calibration-design-v2.md`, twice-revised final state ~900 lines) committed
- Phase 2 archive (`docs/External-Board-Reviews/050126-calibration-rebuild/CONSOLIDATION.md` + 15 round files) committed
- All persistent-state docs (CLAUDE.md, REPO_MAP.md, AUDIT_TRAIL.md, plan, auto-memory) updated to reflect Phase 2 close

**Key outputs (session 9):**

Phase 0 (audit):
- `docs/calibration-audit.md` — empirical baseline; 12 V1.2 wild scan cross-tab; 10 sections; key topline: Q1=red is NOT verdict-discriminating (3 of 6 OSS-default-pattern scans are Caution, 3 are Critical); Q4 IS the verdict-discriminator (5/5 Q4=red are Critical) but Phase 3 rule never reaches red (every Q4=red is a Phase 4 LLM override).

Phase 1 (design):
- `docs/calibration-design-v2.md` — twice-revised final state. 11 sections + revision-history table. Key calls: shape-as-modifier architecture; 9-category closed-enum + 3 cross-shape modifiers (`is_reverse_engineered`, `is_privileged_tool`, `is_solo_maintained`); 10 rules (RULE-1..RULE-10) with confidence labels (firm/lower/n=1-candidate/structural-guard); template-map cell short_answer language; cells-only scope (finding-severities deferred to Phase 1.5); migration plan; staged Q9 hard floor (≤5/12 + ≤3/12 stretch via harness-promotion).

Phase 2 (board review):
- 3-of-3 R3 SIGN OFF (Pragmatist clean SIGN OFF; Codex + DeepSeek SIGN OFF WITH NOTES with deferrals to Phase 3 §10)
- DeepSeek trajectory DISSENT (R1) → SIGN OFF WITH NOTES (R2/R3)
- 16 owner directives applied across 3 rounds (8 R1 + 7 R2 + 1 R3 pre-archive)
- 26-item dissent audit; zero silent drops; zero preserved-live blocking dissents
- Codex's R3 preserved Q2-doc-gap dissent raised-and-resolved-pre-archive via §5 Q2 sub-section
- Archive at `docs/External-Board-Reviews/050126-calibration-rebuild/CONSOLIDATION.md`

Telemetry/scope notes:
- Q2 explicitly deferred (NOT a silent drop) with Phase 1.5 re-entry trigger documented (≥3 Q2 overrides in next 5 wild scans, OR Phase-1 re-render audit miscalls)
- 3 items deferred to Phase 3 implementation (provisional-vs-stable tracking mechanism, `is_privileged_tool` boundary cases, confidence-degradation rules)
- Owner-overrule on RULE-7/8/9 disposition: kept in design with promotion gates (DeepSeek wanted move-to-Phase-1.5-ledger). Promotion gate IS the discipline.

**Revert paths:**
- To revert Phase 2 archive only: `git revert <archive-commit>` — preserves all design + plan work; just removes the archive directory + master index row
- To revert Phase 2 design revisions (R1+R2+R3 directives): `git revert f42635f cb7407c 91cecd5` — destructive; keeps Phase 0 audit + Phase 1 first-draft design only
- To revert all session 9 work: `git reset --hard dff3886` — destructive; returns to session 8 close state. Loses audit + design + board review + archive.
- Pre-session-9 tag: pre-back-to-basics tag does not exist; use SHA `dff3886` as the rollback target.

**Decision points to preserve:**
- The 16 owner directives across 3 rounds are documented in `docs/calibration-design-v2.md` §9 revision history table + `docs/External-Board-Reviews/050126-calibration-rebuild/CONSOLIDATION.md` §3.
- 26-item dissent audit at CONSOLIDATION §4 — every R1/R2/R3 cross-agent concern accounted for. Zero silent drops invariant satisfied per FrontierBoard SOP §4.
- Cells-only scope (Q7) was owner-decided pre-board to avoid doubling board surface area; finding-severity rule-driving is its own Phase 1.5 audit + design.
- Q9 staged floor (≤5/12 hard + ≤3/12 stretch with prospective-only promotion semantics) — owner reframed the original ≤3/12 hard floor after 3-of-3 R1 convergence flagged it as structurally unachievable.
- Phase 3 carry-forwards (5 items at CONSOLIDATION §5) MUST be addressed by Phase 3 implementation — they're not "nice to have," they're follow-on decisions the design intentionally left open.
- The board's substantive contributions: Codex closed the largest single design defect (classify_shape phase boundary FIX-NOW + rule-precedence contract); DeepSeek's R1 DISSENT drove enum over-fit acknowledgment + Q9 reframing; Pragmatist's operational-detail flags (template-map fallback, operator-precedence) became hygiene fixes.

**Next session (Phase 3) entry point:** `docs/back-to-basics-plan.md` §Current state. Work begins on `chore/calibration-rebuild-impl` branch from `main`. Implementation extends `compute.py` per design §10 implementation sketch + addresses CONSOLIDATION §5 carry-forwards.

---

## Checkpoint — 2026-04-30 (session 8 — first wild scan) — mattpocock/skills entry 27 (first Claude Code skills/plugin shape)

**HEAD:** `2aa59bf` on `origin/main` (clean push pending — see verification below; tree clean).

**Session 8 commits from `9b5e5d4` (session 7 close) →:**

```
2aa59bf  Catalog entry 27: mattpocock/skills — first Claude Code skills/plugin V1.2 wild scan
```

**Verification at checkpoint:**
- 414/414 tests passing (no code touched in session 8 — data + docs only)
- 27 catalog entries — 11 V2.4 + 16 v2.5-preview (3 Step G validation + 12 V1.2-schema wild scans entries 16–27)
- All 4 validator gates clean on entry 27: `--report` HTML + `--markdown` MD + `--parity` zero warnings + schema validation
- Q2 override fires `missing_qualitative_context` — first use of this enum value across all 12 V1.2 wild scans (was × 0 at n=11)

**Key outputs (session 8):**

Per-scan outputs (mattpocock/skills entry 27):
- `docs/GitHub-Scanner-skills.md` + `.html`
- `docs/board-review-data/scan-bundles/skills-b843cb5.json`

Telemetry updates:
- `docs/scanner-catalog.md` — row 27 appended; meta-counter 26 → 27 entries; override-enum tally adds first `missing_qualitative_context` fire
- `docs/v12-wild-scan-telemetry.md` — §1 roster row added (n=11 → n=12); §10 changelog entry-27 update; status block notes V13-3 G4-broadened cadence at 12/25 + 1/6 taxonomy-strain events
- `CLAUDE.md` — current-state paragraph rewritten for session 8 (was "session 7 / 26 entries / 11 wild scans / 9 overrides / 404/404 tests" — last was a typo); telemetry block updated to n=12; session-7 typo-fix bundled (404 → 414 tests, was already 414 in audit-trail)
- `REPO_MAP.md` §2.2 — HEAD bumped to `2aa59bf`; session 8 commit chain added; catalog count 26 → 27; override-enum distribution updated to n=12

**Telemetry-significant property of entry 27:**

The Q2 override fires `missing_qualitative_context` — the V13-3 §2 inference at n=11 ("the V13-1 split was correct and complete; missing_qualitative_context catchall hasn't fired post-V13-1 relabel") was n=11-bounded. Entry 27 reopens whether `missing_qualitative_context` is a stable enum value or whether `sample_floor_degeneracy` (or similar) deserves its own enum. The override rationale (1 lifetime merged PR + 0 closed-merged security PRs → 'Yes — they fix problems quickly' over-claims at this evidence floor) is structurally distinct from `signal_vocabulary_gap` (signal didn't capture qualitative context) and `harness_coverage_gap` (harness didn't capture data) — it's "we have signals, but the data is degenerate at sample floor." V13-3 C9 (proposed prune of `missing_qualitative_context` with historical-hold) is now premature; V12x-15 candidate (Q2 sample-floor signal) added to v12-wild-scan-telemetry §8 in spirit (not yet listed as a row).

**Token-burn observation (session 8):**

This single scan consumed ~220k tokens — substantially more than the per-scan budget of recent V1.2 wild scans should require. Diagnosis: read full operator-guide intro + full wezterm `author_phase_4.py` + full wezterm `author_phase_5_6.py` + full compute.py twice (signature lookups that grep would have served) + repeated reads of phase_1 fields that could have been batched. Future scans should: (a) use grep for signature lookups, not full reads; (b) batch phase_1 inspection into 1-2 commands; (c) skip operator-guide re-read when CLAUDE.md context is already loaded; (d) author scripts should reference structural patterns, not be read verbatim. Logged here for session-9 baseline.

**Revert paths:**
- To revert this scan: `git revert 2aa59bf` — preserves all session-7 state; removes catalog entry 27 + telemetry row + 4 doc updates
- Aggressive rollback to session 7 close: `git reset --hard 9b5e5d4` — destructive; removes session-8 commit only

**Decision points to preserve:**
- Q2 override `missing_qualitative_context` rationale: at sample-floor evidence (`total_merged_lifetime` < 5 AND no closed-fix-lag data), Phase 3 advisory's GREEN over-claims; honest answer is amber. Suggested threshold adjustment authored: add `total_merged_lifetime < N` sample-floor signal that returns amber rather than green for new solo projects. THIS IS A V12x-15 CANDIDATE for V1.2.x widening.
- The mattpocock/skills install path is **two-stage** (`npx skills@latest add` routes through vercel-labs/skills npm CLI) AND **rolling** (no release tags — `@latest` resolves to HEAD on main). This is a new shape pattern in the catalog; future plugin-marketplace scans should reuse this Phase 4 framing (F1 + F3 in entry 27 form bundle).
- Harness coverage gap on plugin-shape repos: `agent_rule_files` heuristic captured 1 of 23 markdown rule files (CLAUDE.md only, missed 22 SKILL.md). F5 in entry 27 documents this as a V1.2.x patch candidate (parallel to V13-3 C2 deserialization-regex tightening). Not promoted to V12x backlog row pending owner decision on whether plugin-shape fix belongs in V12x or V1.3 coordinated package.

---

## Checkpoint — 2026-04-20 (session 7) — 2 wild scans (WLED + Baileys) + V13-3 board CLOSE + V1.2.x Priority 1 landing

**HEAD:** `c0d2ba2` on `origin/main` (clean push; tree clean).

**Session 7 commits from `c6e7502` (session 6 close) →:**

```
c0d2ba2  Archive Codex code-review 3-pass iteration for V13-3 landing
fcc4e81  V13-3 CLOSE: comparator-calibration board review + V1.2.x landings
c558b9f  Resolve catalog entry 26 commit hash to 2b295ef
2b295ef  Catalog entry 26: WhiskeySockets/Baileys — V13-3 trigger fires at n=11
f4f3332  Resolve catalog entry 25 commit hash to b3622b5
b3622b5  Catalog entry 25: wled/WLED — first ESP32 IoT firmware scan
```

**Verification at checkpoint:**
- 414/414 tests passing (was 385 at session 6 close; +19 V13-3 tests + pre-existing +10 from other touches)
- 26 catalog entries — 11 V2.4 + 15 v2.5-preview (3 Step G validation + 11 V1.2-schema wild scans entries 16-26)
- V13-3 TRIGGER FIRED at entry 26 Baileys → board review launched → CLOSED 2026-04-20 with 2/3 R3 AGREE + owner directive OD-4
- All 4 validator gates clean on both new scans (WLED + Baileys): MD + HTML + --parity + schema
- V1.2.x code landings cleared Codex code-review after 3-pass iteration (BLOCK → BLOCK → SIGN OFF W/ NOTES)

**Key outputs (session 7):**

Per-scan outputs (WLED entry 25, Baileys entry 26):
- `docs/GitHub-Scanner-WLED.md` + `.html` + `docs/board-review-data/scan-bundles/WLED-01328a6.json`
- `docs/GitHub-Scanner-Baileys.md` + `.html` + `docs/board-review-data/scan-bundles/Baileys-8e5093c.json`

V13-3 board review archive:
- `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/` — CONSOLIDATION.md, r1/r2/r3 briefs, pragmatist/codex/deepseek R1+R2+R3 responses, Codex code-review r1/r2/r3
- 33-item dissent audit; zero silent drops per SOP §4 Pre-Archive Gate

V13-3 V1.2.x code landings (commit `fcc4e81`):
- `docs/phase_1_harness.py` — C2: deserialization regex drops bare `deserialize` keyword (suppresses ArduinoJson FP class)
- `docs/compute.py` — C5: `derive_q4_critical_on_default_path_from_deserialization` + C18: `derive_tool_loads_user_files` + `compute_q4_autofires_from_phase_1` wrapper + Q4 rubric reorder (critical-on-default-path now highest priority); `compute_scorecard_cells(**kwargs, phase_1_raw_capture=...)` auto-fires Q4 red when C5 conditions met
- `docs/phase-1-checklist.md` — A2 row updated to reflect V13-3 C2 language qualifier
- `docs/v13-3-analysis.md` — FROZEN 191-line analysis document mirroring v13-1 template
- `docs/v13-3-fp-dry-run.md` — C20 dry-run: 0 FPs on 11 bundles, 1 true-positive (freerouting)
- `tests/test_compute.py` — +17 tests across TestV13_3_DeriveToolLoadsUserFiles (10), TestV13_3_Q4AutoFireFromDeserialization (7), TestV13_3_ComputeQ4AutofiresFromPhase1 (6), TestV13_3_C5LiveIntegrationInScorecardCells (4)
- `tests/test_phase_1_harness.py` — +2 regression tests (ArduinoJson suppression + unsafe-specific retention)

Telemetry updates:
- `docs/v12-wild-scan-telemetry.md` — §1 roster 10 → 11; §2 distribution signal_vocabulary_gap 67% modal; §3 streak 3-consecutive Q4 breaks; §4 Priority 1b + 1c harness-patch candidates; §5.2 silent-fix 11/11 with 2 documented failures; §7 V13-3 FIRED; §8 V12x backlog V12x-11/12/13 added; §10 changelog entry 26 + V13-3-CLOSE entries
- `docs/scanner-catalog.md` — rows 25 + 26 appended with full per-scan summaries; footer updated (25 → 26 entries; 9 overrides across 11 scans)
- `CLAUDE.md` — current-state paragraph rewritten for session 7 (414 tests, 26 entries, V13-3 RESOLVED); reference list pointer updated
- `docs/External-Board-Reviews/README.md` — V13-3 review row added to chronological index

**Revert paths:**
- To revert V13-3 code landings only: `git revert fcc4e81 c0d2ba2` — preserves catalog + scans; removes the compute/harness/analysis changes
- To revert V13-3 entirely including board-review archive: `git reset --hard c558b9f` — destructive; returns to post-Baileys-scan state (Baileys stays; V13-3 work undone)
- To revert back to session 6 close (pre-WLED): `git reset --hard c6e7502` — destructive; removes all session 7 commits including WLED + Baileys scans

**Decision points to preserve:**
- V13-3 CLOSED by 2/3 R3 AGREE + owner directive OD-4 (Codex R3 unavailable due to OpenAI capacity; R2 positions consistent with resolutions; Codex assigned code-review gate as substantive-review surrogate — THIS PATTERN IS PRECEDENT for future owner-directive closes when one agent is unavailable and their R2 positions are consistent with resolutions)
- Q4 rubric reorder in compute_scorecard_cells: has_critical_on_default_path check moved to highest priority. Was a pre-existing bug exposed by C5 integration tests. Landed in `fcc4e81`.
- compute_scorecard_cells signature widened: new optional `phase_1_raw_capture` kwarg. Backwards-compatible (defaults to None → pre-existing behavior). Future scan drivers should pass phase_1_raw_capture to get C5 auto-fire applied.
- V1.3 deferred ledger populated with 6 items + 2 new-item additions (N1 deserialization primitive taxonomy redesign; N2 statistical CIs on override-rate claims — N2 already applied in v13-3-analysis.md §3.1)
- V13-3 follow-up cadence (G4-broadened): re-trigger on N=25 V1.2 wild scans OR any of 6 taxonomy-strain events

---

## Checkpoint — 2026-04-20 (session 6) — V13-1 resolution + V1.2.x signal widening + D-6 automation + 6 wild scans

**HEAD:** `edf8f57` on `origin/main` (clean push; tree clean).

**Session 6 commits from `be9a1c0` (session 5 close) →:**

```
edf8f57  Catalog entry 24: freerouting/freerouting — first Java scan, Java deserialization RCE
b8be939  Catalog entry 23: jtroo/kanata — second Rust scan, 44% formal review
a52ba7b  Catalog entry 22: QL-Win/QuickLook — first C# scan, Windows-shell integration
5587560  Catalog entry 21: wezterm/wezterm — first Rust V1.2 scan, zero overrides
02be2ef  Catalog entry 20: BatteredBunny/browser_terminal — first browser-extension scan
6f98fb2  Catalog entry 19: XTLS/Xray-core — fourth V1.2 wild scan
baf5dc9  D-6: automated severity-distribution gate 6.2 (Operator Guide §8.8.7)
d803faf  V1.2.x signal widening: V13-1 fix surfaces (owner directive)
5f3984d  V13-1 resolution: expand override_reason enum to 7 values (owner directive)
9f8023f  Catalog entry 17: shiyu-coder/Kronos — second V1.2-schema wild scan
06ef4b7  Catalog entry 18: basecamp/kamal — third V1.2 wild scan, V13-1 telemetry trigger fired
be9a1c0  [session 5 close base — Schema V1.2 LANDED + ghostty entry 16]
```

**Final state:**

- Tests: **385/385 passing** (342 session-5 baseline + 2 V13-1 override tests + 13 V13-1 helper tests + 4 harness pickle-regex tests + 23 D-6 severity-comparator tests + 1 signal-count update)
- Catalog: **24 entries** (11 v2.4 + 13 v2.5-preview; 9 V1.2-schema wild scans = entries 16–24)
- Schema: **V1.2** (unchanged from session 5) + `override_reason_enum` expanded 5→7 values (+`signal_vocabulary_gap`, +`harness_coverage_gap`)
- Compute: `SIGNAL_IDS` expanded 23→25 (+`q1_has_ruleset_protection`, +`q2_oldest_open_security_item_age_days`); new helpers `derive_q1_has_ruleset_protection` + `derive_q2_oldest_open_security_item_age_days`
- Harness: deserialization regex widened (pickle.load, marshal.load, joblib.load, dill.load)
- New tooling: `docs/compare-severity-distribution.py` (D-6 gate-6.2 automation; 23 tests)
- New docs: `docs/v13-1-override-telemetry-analysis.md` (V13-1 analysis) + `docs/v12-wild-scan-telemetry.md` (9-scan cross-analysis)
- Override telemetry: **7 overrides across 9 V1.2 wild scans**; `signal_vocabulary_gap` modal (57%); 3 zero-override scans (wezterm/QuickLook/kanata)

**V13-1 resolution:**
- Analysis at `docs/v13-1-override-telemetry-analysis.md` (§1-7) concluded with owner directive (not board review) to split `missing_qualitative_context` into `signal_vocabulary_gap` (compute.py fix surface) + `harness_coverage_gap` (phase_1_harness.py fix surface).
- 4 existing overrides relabeled (ghostty Q1, Kronos Q2, kamal Q1 → `signal_vocabulary_gap`; Kronos Q4 → `harness_coverage_gap`).
- CONSOLIDATION.md §8 V13-1 marked RESOLVED with §8.1 resolution record; §8.2 records the follow-up V1.2.x signal-widening patch.
- V1.3 escalation triggers preserved.

**V1.2.x signal widening (same session):**
- Added `q1_has_ruleset_protection` signal — closes ghostty Q1 + kamal Q1 override path on future scans.
- Added `q2_oldest_open_security_item_age_days` signal — closes Kronos Q2 override path on future scans. (But also fired red on wezterm entry 21 and Xray-core entry 19 from noisy security-keyword matches — threshold_too_strict override authored in Xray-core; wezterm kept red on release-stall grounds.)
- Harness `dangerous_primitives.deserialization` regex widened — closes Kronos Q4 override path; caught ZERO new issues on subsequent scans (regex no false-negatives either way).

**6 V1.2 wild scans shipped this session (entries 19–24):**

| Entry | Repo | Shape | Verdict | Overrides |
|---|---|---|---|---|
| 19 | XTLS/Xray-core | Go network proxy | Critical | 1 (threshold_too_strict) |
| 20 | BatteredBunny/browser_terminal | Browser ext + Go host | Critical (split) | 1 (harness_coverage_gap) |
| 21 | wezterm/wezterm | Rust terminal | Caution | 0 |
| 22 | QL-Win/QuickLook | C# Windows shell | Caution | 0 |
| 23 | jtroo/kanata | Rust keyboard daemon | Critical | 0 |
| 24 | freerouting/freerouting | Java PCB autorouter | Critical | 1 (signal_vocabulary_gap) |

**Revert paths:**
- Revert entire session 6: `git reset --hard be9a1c0` (session 5 close)
- Revert just the 6 V1.2 wild scans (keep V13-1 resolution + V1.2.x + D-6): `git revert edf8f57 b8be939 a52ba7b 5587560 02be2ef 6f98fb2`
- Revert just V1.2.x signal widening (keep enum split + D-6): `git revert d803faf`
- Revert just V13-1 resolution: `git revert 5f3984d` (would break the 6 wild-scan commits that use relabeled enum values)

**V13-3 progress:** 9 of 11 V1.2 wild scans accumulated (2 more needed for comparator-calibration trigger).

**Harness-patch backlog documented** in `docs/v12-wild-scan-telemetry.md` §4 + §8 — deserialization auto-fire + multi-ecosystem manifest parsing + install-doc URL TLD-deviation are the priority candidates.

---

## Checkpoint — 2026-04-20 (session 5) — Schema V1.2 LANDED + ghostty wild scan (override-explained proven)

**HEAD:** `5f5d1cd` on `origin/main` (clean push; tree clean).

**Session 5 commits from `4512084` (session 4 close) →:**

```
5f5d1cd  Catalog entry 16: ghostty-org/ghostty — first V1.2-schema wild scan
2c5aca0  Schema V1.2 implementation: D-7 + D-8 landing per CONSOLIDATION §7
a0e370e  Schema V1.2 design frozen: D-7 + D-8 board review 3/3 SIGN OFF
4512084  [session 4 close base — V2.5-preview production-cleared, markitdown entry 15]
```

**Final state:**

- Tests: **342/342 passing** (319 session-4 baseline + 23 new V1.2 tests: 10 validator override-gate, 9 migration round-trip, 3 signal vocab, 1 scorecard-path invariant)
- Catalog: **16 entries** (11 v2.4 + 5 v2.5-preview: zustand-v3, caveman, Archon, markitdown, ghostty)
- Parity sweep: **18/18 MD+HTML pairs clean**
- Schema: **V1.2** — harness-canonical shapes + names; transformer deleted; `phase_3_advisory.scorecard_hints` top-level; `phase_4_structured_llm.scorecard_cells` authoritative with `{rationale, edge_case, suggested_threshold_adjustment, computed_signal_refs, override_reason}`; 23-row frozen signal ID vocabulary (`compute.SIGNAL_IDS`); 5-value `override_reason` enum frozen; `agent_rule_files.total_bytes` dropped
- Gate 6.3 semantics: changed from "cell-by-cell match" to **"override-explained"** — validator (`docs/validate-scanner-report.py --form`) enforces rationale ≥50 chars + `computed_signal_refs` non-empty with all refs resolving against `compute.SIGNAL_IDS` + `override_reason` in the 5-value enum, *only when* Phase 4 color differs from Phase 3 advisory color
- **Override-explained proven end-to-end** via ghostty Q1 (advisory red → Phase 4 amber, `override_reason = missing_qualitative_context`, 7 `computed_signal_refs` citing the gap where compute.py's narrow `q1_has_branch_protection` check misses ruleset-based protection)
- Harness = **Phase 1 standard** for V2.5-preview; V1.2 schema accepts harness output natively (no transformer, no sidecar bridge)
- Phase 4/5/6 authoring remains LLM-driven; compute.py runs Phase 3 + advisory + Phase 4b verdict

**Board review archive:** `docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` (3 rounds + 2 owner directives; 3/3 SIGN OFF; 31-item dissent audit with zero silent drops; 9 live preserved dissents + 3 moot-preserved + 5 deferred with triggers).

**V1.2 implementation files:**
- `docs/scan-schema.json` — V1.2 bump + all D1/D2 deltas
- `docs/compute.py` — `SIGNAL_IDS` frozenset + `OVERRIDE_REASON_ENUM` + `compute_scorecard_cells` rewritten to advisory shape
- `docs/phase_1_harness.py` — 4 new fields gathered (`has_issues_enabled`, `primary_language`, `topics`, `fork_count`)
- `docs/validate-scanner-report.py` — new `--form` mode + `validate_override_rationale()`
- `docs/templates/partials/scorecard.md.j2` + `docs/templates-html/partials/scorecard.html.j2` — path change to `phase_4_structured_llm`
- `migrate-v1.1-to-v1.2.py` (repo-root) — idempotent one-time migration, all 3 active fixtures migrated clean
- `tests/test_validator_v12_override.py` + `tests/test_migrate_v12.py` — 19 new tests

**Ghostty scan artifacts:**
- `docs/GitHub-Scanner-ghostty-v12.md` (404 lines) + `.html` (1732 lines)
- `docs/scanner-catalog.md` entry 16
- `.board-review-temp/ghostty-scan/` (gitignored): `head-sha.txt`, `phase-1-raw.json`, `form.json`, `build_form.py`, `author_phase_4.py`, `author_phase_5_6.py`

**Revert paths:**
- Revert entire session: `git reset --hard 4512084` (session 4 close)
- Revert just ghostty scan, keep V1.2 implementation: `git revert 5f5d1cd`
- Revert just V1.2 implementation (keep schema design doc): `git revert 2c5aca0` then `git revert a0e370e`

**D-7 + D-8 status:** CLOSED. Moved from deferred ledger to implemented.

---

## Checkpoint — 2026-04-20 (session 4) — V2.5-preview PRODUCTION-CLEARED via first wild scan

**HEAD:** session 4 close commit (pending) on top of `4ad4cf6` (Phase 1 tooling)

**Session 4 commits from `c0f6dc2` (session 3 close) →:**

```
<session-4-close>  Session 4 close: markitdown wild scan + production clearance + D-8 logged
4ad4cf6            Phase 1 tooling: checklist + harness + tests
c0f6dc2            [session 3 close base]
```

**Final state:**

- Tests: 319/319 passing (289 session-3 + 30 new `tests/test_phase_1_harness.py::TestPhase1Harness`)
- Catalog: 15 entries (11 v2.4 + 4 v2.5-preview: zustand-v3, caveman, Archon, markitdown)
- Parity sweep: 17/17 MD+HTML pairs clean
- V2.5-preview: PRODUCTION-CLEARED 2026-04-20
- Phase 1 automation: `docs/phase_1_harness.py` implements V2.4 prompt Steps 1-8 + A/B/C end-to-end
- D-8 open: V1.2 schema hardening to natively accept harness output (bridge via sidecar + transformer)

**What got done this session:**

1. **Surfaced the Phase 1 ad-hoc gap.** Mid-scan on microsoft/markitdown, acknowledged that the wild-scan attempt was ~60% of the V2.4 prompt's investigation steps because no mapping document or harness existed. Reverted to building tooling before completing the scan.
2. **Authored `docs/phase-1-checklist.md`** — canonical mapping of V2.4 prompt Steps 1-8 + A/B/C to phase_1_raw_capture fields. Every external source (gh api, OSSF Scorecard API, osv.dev, gitleaks, PyPI/npm/crates.io/RubyGems, tarball extraction + local grep, README paste-scan) paired with its target field and failure mode.
3. **Authored `docs/phase_1_harness.py`** — executable implementation. ~60 functions across pre-flight + Steps 1-8 + A-pre + A + C + monorepo + batch-merge + defensive-configs + coverage-affirmations. Fixed V2.4 prompt typo (`tar --no-absolute-names` — bsdtar only; GNU tar default already safe).
4. **Authored `tests/test_phase_1_harness.py`** — 30 unit tests with subprocess mocking; end-to-end smoke test asserts all 28 expected fields populate.
5. **Ran harness on microsoft/markitdown.** Harness surfaced data my ad hoc pass missed, including `archive_unsafe` grep hit on `_zip_converter.py:96` (the exact file in issue #1514) + 2 sibling exposures not separately issue-filed.
6. **Surfaced D-8.** Harness output is richer than V1.1 schema accepts (dangerous_primitives shape, dependencies shape, pr_review extras, etc). Per §8.8.7 watchpoint, halted and offered user option to either harden schema (board review needed) or bridge via sidecar. User chose bridge — `.board-review-temp/markitdown-scan/transform_harness.py` emits V1.1-compliant form + `phase-1-raw-full.json` sidecar preserves richness. D-8 logged for V1.2 schema update.
7. **Harness bug discovered + fixed in-session.** community/profile API doesn't always report `files.security_policy` even when SECURITY.md is present at root (markitdown hit). Added direct-path fallback in harness.
8. **Completed markitdown scan.** Authored Phase 4 findings (F0-F7, 8 total) + evidence (E1-E11) + split-axis (Deployment) + verdict_exhibits + prose from bundle. Schema CLEAN. Rendered MD+HTML deterministically. All 7 applicable gates pass (gate 6 N/A on wild scan).
9. **Real findings from the scan:** 2 live vulns in default install path when processing untrusted files (F1 XXE, F2 Zip Bomb — both with harness-surfaced sibling exposures); F3 disclosure gap (CVE-2025-64512 silent patch); F0 governance softness (ruleset requires PR but 0 approving reviewers, 76 self-merges, no CODEOWNERS).
10. **Session-close commit** — scanner-catalog #15, Operator Guide §8.8 opening + §8.8.7 D-8, REPO_MAP §2.2/§2.4/§2.5, CLAUDE.md, AUDIT_TRAIL. All declare V2.5-preview production-cleared.

**Revert paths:**

- Revert session-close commit → state back at session 3 close; V2.5-preview still Step-G-validated-only.
- Revert `4ad4cf6` → no Phase 1 tooling, no markitdown scan; state back at session 3.
- Cherry-pick to keep tooling but drop markitdown scan: leave `4ad4cf6` in; revert only the session-close commit's MD/HTML/bundle creations.

## Checkpoint — 2026-04-20 (session 3 close) — Step G PASSED 3/3; V2.5-preview Step-G-validated; production-clearance pending first wild scan

**HEAD:** (pending session-close commit on top of `be56935`)

**Session 3 commit chain (from `e267805` → session-close):**

```
<session-close>  Session 3 close: Step G 3/3 PASSED — catalog + guide + REPO_MAP + CLAUDE.md updates
be56935          Step G Archon — ALL 7 GATES PASS, Step G 3/3 complete
ed68fae          Step G caveman (proper redo) — ALL 7 GATES PASS with fresh authoring from bundle
8a23ee8          Revert "Step G caveman — ALL 7 GATES PASS (2nd V2.5-preview scan)"
e24e695          Step G caveman — ALL 7 GATES PASS (2nd V2.5-preview scan) [REVERTED]
2c13324          Step G zustand pilot — ALL 7 GATES PASS (first V2.5-preview scan)
7d300a8          SF1 Phase 1: compute.py scorecard patches + U-11 Archon Q3 correction
7f90a1b          Archive SF1 board review: 4-round resolution, D-7 committed
```

**Final state:**

- Tests: 289/289 passing (10 new SF1 patch tests in `TestSF1ScorecardPatches`)
- Step G acceptance matrix: 3/3 targets, 7 gates each, 12/12 scorecard cells match V2.4, 18/18 finding cards match V2.4 inventory + severity
- Catalog: 14 entries (11 `v2.4` + 3 new `v2.5-preview` at positions 12-14)
- Parity sweep: 16/16 MD+HTML pairs clean (13 V2.4 + 3 V2.5-preview)
- 3 new bundle files at `docs/board-review-data/scan-bundles/`: `zustand-v3-3201328.md` (reconciled), `caveman-c2ed24b.md` (fresh-authored), `Archon-3dedc22.md` (fresh-authored)
- D-7 committed as post-Step-G architecture work (scorecard authority migration V1.1 → V1.2)

**What got done this session:**

1. **SF1 board review** (4 rounds, archived at `docs/External-Board-Reviews/042026-sf1-calibration/`) — resolved the scorecard calibration drift that halted Step G pre-pilot in session 2. Final: hybrid "A-now + C-for-V1.2 + edge_case" with 2-1 G-C-ACCEPT on Archon Q3 Tension-1. DeepSeek D-CANONICAL dissent preserved in CONSOLIDATION §9.
2. **SF1 Phase 1** (commit `7d300a8`) — 4 `docs/compute.py` temporary-compatibility patches (Q1 governance-floor / Q2 closed_fix_lag_days / Q3 has_contributing_guide / Q4 has_warning_on_install_path split) + U-11 single-cell catalog correction (Archon Q3 green → amber). 10 new regression tests.
3. **Step G zustand pilot** (`2c13324`) — first V2.5-preview pass. All 7 gates clear.
4. **Step G caveman attempt + revert + redo** (`e24e695` → `8a23ee8` → `ed68fae`) — first attempt reverted for fixture content reuse on Phase 4 findings; proper redo authored fresh from a new bundle with full discipline.
5. **Step G Archon** (`be56935`) — third and final Step G target. Schema pre-read before Phase 4 authoring avoided the 45-error ping-pong caveman's first attempt hit (Archon: 1 schema error, 1 reshape).
6. **Session-close commit** — scanner-catalog + Operator Guide + REPO_MAP + CLAUDE.md + AUDIT_TRAIL updates. V2.5-preview tagged as Step-G-validated but NOT yet production-cleared (first unfixtured wild scan is the remaining trigger).

**Production-clearance trigger (not yet fired):**

A successful wild scan — live `gh api` capture on a repo outside the 3 validation shapes {zustand, caveman, Archon}, rendering clean through the V2.5-preview pipeline with all 7 gates passing — promotes V2.5-preview from "Step-G-validated on 3 shapes" to "production-cleared." Until then V2.4 stays the default production path. Operator Guide §8.8 opening callout and CLAUDE.md Rendering pipeline note both flag this gap.

**Revert paths:**

- Revert session-close commit → state back at `be56935` (Step G 3/3 complete but catalog/guide/maps not yet updated).
- Revert `be56935` → Archon Step G output removed; 2/3 targets state (zustand + caveman passing).
- Revert `ed68fae` + `be56935` → back to post-SF1-Phase-1 state (`7d300a8`), 0 Step G targets but SF1 patches + U-11 retained.
- Revert `7d300a8` → pre-SF1-Phase-1 state (`7f90a1b`), SF1 archive exists but no compute.py patches applied.
- Revert `7f90a1b` → `e267805`, session 2 state with SF1 HALTED.

## Checkpoint — 2026-04-20 (session 3) — SF1 board resolved (4-round); Phase 1 archival landed

**HEAD:** archival commit (session 3 in progress at time of checkpoint)

**Board outcome:** `docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md`
- R1 Blind: Pragmatist A / Codex new-D / DeepSeek C+
- R2 Consolidation on hybrid "A-now + C-for-V1.2 + edge_case": 1 ACCEPT + 2 ACCEPT-WITH-MODS
- R3 Confirmation on frozen hybrid: 3/3 CONFIRM · 3/3 UNION-ACCEPT on Tension 2 · 1-1-1 on Tension 1
- R4 narrow tiebreaker (Tension 1 only with live `gh api` Archon evidence): 2-1 G-C-ACCEPT (Pragmatist moved from A-CANONICAL). DeepSeek D-CANONICAL dissent preserved.
- Dissent audit: clean across all 4 rounds (zero silent drops, SOP §4 attested)

**What the archival commit contains:**
1. `docs/External-Board-Reviews/042026-sf1-calibration/` — full archive (R1-R4 briefs + 12 agent responses + FINDING-SF1 + CONSOLIDATION)
2. `docs/SCANNER-OPERATOR-GUIDE.md` — D-7 added to post-Step-G ledger (§8.8.7); §8.8.3 Step 3b annotated re: temporary compatibility patches
3. `REPO_MAP.md` — §2.2 state + §2.4 Step G status + §2.5 deferred ledger all updated
4. `CLAUDE.md` — Current state summary + "most recent board decision" pointer updated

**Phase 1 execution state at checkpoint:**
- Gate A (schema): PASS — no schema change needed; `scorecard_cell.inputs` is open object per `python3 -c "import json; print(json.load(open('docs/scan-schema.json'))['\$defs']['scorecard_cell']['properties']['inputs'])"` → `{'type': 'object'}` (no additionalProperties constraint)
- Gate B (zustand F0 type): pending
- Gate C (Archon Q3 ground-truth audit): pending — Pragmatist R4 5-step criteria as audit procedure (read PR #1169/#1217 diffs; check vuln-remediation language; A-CANONICAL outcome if FALSE, D-CANONICAL outcome if TRUE, amber-default if ambiguous)
- 5 compute.py temporary-compatibility patches: not yet applied
- Fixture form updates: not yet applied
- Compute-driver dry-run re-verification: not yet done

**Revert paths:**
- Revert archival commit → previous state, Step G still "HALTED at SF1" per session 2 checkpoint
- Step G Operator Guide §8.8 is NOT in rollback — remains canonical
- `.board-review-temp/step-g-execution/` contents (briefs, R1-R4 responses, finding, gate log, compute driver) retained locally; archive is a copy

## Checkpoint — 2026-04-20 (session 2) — Step G pre-flight passed; HALTED at Finding SF1 (scorecard calibration drift)

**HEAD:** `9840cdf`
**Session commit range (from prior `90b04b7` → `9840cdf`):**
- `9840cdf` Step G pre-flight: validator warning/info reclassification + FN-5 grep fix (3 files, 77+/21-)

**Final state:**
- pytest: `279 passed in 40.78s`
- 13/13 MD+HTML pairs `--parity` clean (validator updated to classify authoring/rendering variations as `ℹ Note:` instead of `⚠ WARNING:`)
- Repo ↔ package validator: byte-identical (no change this session)
- 11 catalog entries (unchanged)
- Commits ahead of origin/main: 1 (will be 2 after session-close commit)

**What got done this session:**

1. **Step G pre-flight Steps -2, -1, 0 all passed** (per §8.8.3 + §8.8.5):
   - Step -2: Provenance entry for `zustand-step-g-form.json` pre-registered in `tests/fixtures/provenance.json` with `step-g-live-pipeline` tag (transitions on gate acceptance or failure)
   - Step -1: V2.4 comparator `--parity` cleanliness sweep — all 3 targets (zustand-v3, caveman, Archon) return exit 0, zero `WARNING:` lines, INFO notes only (non-gating)
   - Step 0: 4-case adversarial bundle validator smoke test — 3 failure cases exit 1 with specific messages, compact-bundle case exits 0 as spec'd

2. **Owner directive pre-flight blocker fix (commit `9840cdf`, U-10 alignment):**
   - FN-5 grep pattern `'^WARNING:'` didn't match validator's emission format (`  ⚠ <text>`); fix: emit `⚠ WARNING:` prefix for real warnings, `ℹ Note:` for info; update grep to substring `WARNING:`
   - `--parity` + `--bundle` warnings reclassified per MD-canonical asymmetry — MD findings not extractable from HTML (authoring variation), compact-bundle style (U-10 approved), section rendering differences, compact-bundle verdict-without-F-IDs → INFO not WARNING; real errors + structural ambiguity warnings retained
   - Attempted compound-F-ID tail paren extraction reverted (false-positive flagged Archon F11+F14 as MD-canonical violation; those are rule-ID references, not finding-card IDs)
   - Operator Guide §8.8.2 step 4 + §8.8.3 Step -1 + §8.8.5 gate 3 updated to reflect INFO non-gating semantics

3. **Step G authoring HALTED at Finding SF1 before zustand pilot started.** Compute driver dry-run on template Phase 1 data surfaced scorecard cell color divergence between `compute.py` output and V2.4 comparator MD. Confirmed systemic across all 3 targets:
   - zustand-v3: Q3 red vs amber, Q4 amber vs green
   - caveman: Q2 green vs amber
   - Archon: Q1 amber vs red, Q3 amber vs green

   §8.8.3 Step 3b (compute.py byte-for-byte equality required) and §8.8.5 gate 6.3 (scorecard cells match comparator cell-by-cell) are **mutually exclusive** under current state. No authoring choice resolves this. Per §8.8.6 ambiguity → HALT rule.

   **Finding document (local-only, `.board-review-temp/` gitignored):** `.board-review-temp/step-g-execution/step-g-finding-SF1-scorecard-calibration.md` (8KB; frames 3 resolution options A/B/C as a DESIGN decision for board review, not a code fix).

**Key decisions made this session (preserve for future sessions):**

1. **FN-5 + FN-6 as originally written were both broken.** Prior AUDIT_TRAIL entries claiming "13/13 pairs clean" relied on exit-code-only check; the `^WARNING:` grep pattern matched nothing because validator emits `⚠` (unicode). Fixed in commit `9840cdf`.

2. **MD-canonical is asymmetric** (re-established formally): HTML may not ADD findings not in MD; MD MAY have F-IDs not explicitly encoded in HTML h3 tags (authoring choice). Validator flags HTML-extras as error; MD→HTML asymmetry is info, not warning.

3. **Step G is HALTED (not failed).** Pre-flight infrastructure is sound. The halt is pre-authoring — zero authoring was done on the zustand pilot form. Template copy in `.board-review-temp/step-g-execution/zustand-step-g-form.json` remains unmodified V2.3 template content. Operator Guide §8.8 remains canonical and is NOT rolled back.

4. **Finding SF1 is the FIRST real Step G acceptance-matrix output.** The halt validates the Step G gate design — it surfaced a systemic calibration gap that could not have been detected by the renderer-validation fixtures. This is exactly what Step G's live-pipeline validation is for.

5. **Board review on SF1 is a DESIGN decision, not a code fix.** Resolution shapes:
   - **A:** Adjust compute.py calibration to match V2.4 LLM judgments (compute.py becomes codification of current catalog)
   - **B:** Keep compute.py strict, re-harmonize V2.4 catalog MDs to match compute.py output (second catalog pass after U-10)
   - **C:** Schema split — move scorecard cells out of `phase_3_computed` into `phase_4_structured_llm` (V1.1 → V1.2 schema change, deferred)
   - See `.board-review-temp/step-g-execution/step-g-finding-SF1-scorecard-calibration.md` for full analysis.

**Files modified but uncommitted at session boundary** (session-close commit pending):
- `AUDIT_TRAIL.md` (this entry)
- `REPO_MAP.md` §2.2 + §2.4
- `/root/.claude/plans/GitHub-scanner-tool-Jaunty-dazzling-poiny.md` (not in repo; local personal state)

**Files created in `.board-review-temp/` (gitignored, local-only):**
- `step-g-execution/compute_driver.py` — two-pass compute driver for Phase 3 + Phase 4b verdict
- `step-g-execution/step-g-finding-SF1-scorecard-calibration.md` — SF1 finding doc for next session's board review
- `step-g-execution/zustand-step-g-form.json` — V2.3 template copy (unmodified — authoring not started)
- `step-g-execution/adversarial/` — 4 synthetic bundles from Step 0 smoke test + base
- `step-g-execution/parity-{zustand-v3,caveman,Archon}-comparator.txt` — parity sweep captures

**Revert paths:**
- Revert to pre-session state: `git reset --hard 90b04b7` (session-close from prior session)
- Revert to post-pre-flight state: HEAD `9840cdf` is the clean pre-flight; no revert needed

---

## Checkpoint — 2026-04-20 — Session close: Step G board-approved + FN-1..FN-9 implemented in Operator Guide §8.8

**HEAD:** `a80f239`
**Cumulative session (spans 2 stop-git-std commits + 1 FrontierBoard upstream commit from `e297161` → `a80f239`):**
- `e297161` Archive 041926-step-g-execution board review — unanimous clean SIGN OFF (14 files, 2079 insertions)
- `a80f239` Implement Step G FN-1..FN-9 + D-4/D-6 carry-forwards in Operator Guide §8.8 (1 file, 104 insertions, 29 deletions)

**Cross-repo FrontierBoard commit (pushed to stefans71/FrontierBoard main):**
- `e01303a` Add mandatory pre-archive dissent audit gate to §4 (SOP update, 1 file, 31 insertions, 2 deletions)

**Final state:**
- pytest: `279 passed in 41.03s`
- 13/13 MD+HTML pairs `--parity` clean (11 catalog entries + zustand + zustand-v2 + agency-agents + open-lovable)
- Repo ↔ package validator: byte-identical (0-line diff, unchanged this session)
- 11 catalog entries (unchanged this session)

**What got done this session:**

1. **Step G execution board review** (3-round, archived at `docs/External-Board-Reviews/041926-step-g-execution/`):
   - R1 Blind: unanimous SIGN OFF W/ DISSENTS (3 agents × 10–15 items each)
   - R2 Consolidation: Pragmatist upgraded to clean SIGN OFF; Codex + DeepSeek SIGN OFF W/ DISSENTS with 4 ADJUSTs between them
   - R3 Confirmation: **all 3 agents clean SIGN OFF**. No R4 needed.
   - Final approved set: 9 fix artifacts (FN-1..FN-9) + 15 carry-forward dispositions (D-1..D-6, I-1..I-9) + 8 adjustments (A-1..A-8)
   - 41-item dissent audit, zero silent drops — first review to use the new pre-archive audit gate

2. **Pre-archive dissent audit made mandatory** in FrontierBoard SOP §4 (new subsection + 2 anti-pattern rows + Quick Reference update). Pushed to `stefans71/FrontierBoard` main as `e01303a`. This session triggered the SOP change after owner caught that the first R2 draft silently dropped 15 DEFER/INFO/blind-spot items.

3. **FN-1..FN-9 + D-4/D-6 implemented in Operator Guide §8.8** (commit `a80f239`):
   - Pre-flight section (new): Step -2 provenance tagging, Step -1 V2.4 comparator cleanliness (FN-6), Step 0 adversarial bundle smoke test 4 cases (FN-3)
   - Authoring reorg: Step 3b mandatory compute.py with byte-for-byte equality (FN-2), Step 3c bundle-complete gate (FN-9)
   - Post-render (new): Step 10 phase-boundary contamination check all-target semantic STOP (FN-8), Step 11 gate acceptance
   - §8.8.2 pilot-and-checkpoint ordering (FN-7) + tee/grep warning-count inspection (FN-5)
   - §8.8.5 gate 6 rewritten as 6.1–6.6 zero-tolerance checklist with severity mapping doc requirement (FN-1) + gate 7 added (FN-8)
   - §8.8.6 renamed + graduated failure disposition rubric (FN-4, Step G NOT passed until all 3 shapes pass all gates; no "partial pass" claim)
   - §8.8.7 D-4 halt-on-smuggle watchpoint + D-6 POST-STEP-G IMMEDIATE commitment

4. **Codex code review of staged diff before commit:**
   - 9 of 11 items APPROVE clean (FN-2, FN-3, FN-4, FN-5, FN-7, FN-8, FN-9, D-4, D-6)
   - 6 of 6 meta-integrity checks PASS (Q-M1 board review citation, Q-M2 test count update, Q-M3 cross-ref consistency, Q-M4 no stale language, Q-M5 phase structure coherent, Q-M6 cross-refs live)
   - FN-1 nit: "No dead refs. No unreferenced evidence cards." in gate 6.6 flagged as exceeding R3-approved text. **Nit applied pre-commit** — trimmed to exact R3 text. (Governance note: that text was in R2 and was SECOND'd; R3 restatement dropped it unintentionally. Owner chose tightest R3 conformance.)
   - FN-6 reject: flagged "or document as comparator-tainted, Step G-deferred for this shape" escape as weakening a hard STOP. **Override documented in commit body** — false positive. The clause IS in R2 board-approved text (line 521) and was SECOND'd by all 3 agents. My review brief paraphrased the decision without the clause; Codex reviewed against my paraphrase. Implementation matches actual board text.

**Key decisions made this session (preserve for future sessions):**

1. **Step G is NOT passed until all 3 targets clear all 7 gates** (Codex verdict-strictness principle preserved in FN-4 A-2 wording). No "partial pass" language. Graded disposition governs operational handling, not the pass/fail verdict.
2. **Pre-archive dissent audit is mandatory SOP gate.** Zero silent drops = pass criterion. Applies to every future board review archive.
3. **R2 briefs must include ALL dissent items** (FIX NOW + DEFER + INFO + blind spots), not just FIX NOW convergence. Stateless agents cannot vote on what they cannot see.
4. **Code-review briefs must quote board decisions verbatim, not paraphrase.** FN-6 false-positive revealed the drafting discipline gap. (Candidate for future SOP improvement: require verbatim quoting, not summary paraphrase, in code-review briefs.)
5. **Schema hardening (D-4) is no longer a soft defer** — now an explicit halt-on-smuggle watchpoint. Any need to invent ad hoc fields / overload existing fields / carry semantics outside schema-defined locations upgrades DEFER → FIX NOW + HALTS execution.
6. **D-6 severity distribution automation** moved from DEFER to POST-STEP-G IMMEDIATE FOLLOW-UP. Must be built before the first production V2.5-preview scan beyond the 3 validation shapes.
7. **FrontierBoard clone topology** on this VPS:
   - `/root/tinkering/FrontierBoard/Git-030126/` — authoritative clone at origin/main (matches upstream including SOP update `e01303a`)
   - `/root/.frontierboard/FrontierBoard/` — non-git reference copy with preserved `.board/` runtime history (past review artifacts). SOP content byte-identical to upstream. Left as-is per owner decision; NOT replaced with fresh clone to preserve `.board/` history.
   - `/root/FrontierBoard/` + `/root/tinkering/FrontierBoard-Main-Review/` — stale clones at `f1ffa1c` with local-only unpushed README polish commits. Left untouched.
   - `/root/tinkering/FrontierBoard-Main/` — 1 commit behind upstream. Left untouched.

**Board approval:** Step G execution approach unanimously approved at R3. Implementation was pre-commit Codex-reviewed (9/11 clean, 2 edge cases adjudicated). Step G execution itself is board-cleared to run.

**Revert paths:**
- Revert to pre-session state: `git reset --hard 30da757` (last commit of prior session — session-close handoff)
- Revert to post-archive, pre-implementation: `git reset --hard e297161` (archive landed but FN items not yet implemented)
- Roll back FrontierBoard SOP change: `git -C /root/tinkering/FrontierBoard/Git-030126 revert e01303a && git -C /root/tinkering/FrontierBoard/Git-030126 push origin main` (destructive to upstream; confirm before executing)

---

## Checkpoint — 2026-04-19 — Session close: Step G pre-reqs all cleared + scan #11 multica

**HEAD:** `5dbd5bf`
**Cumulative session (this session's work spans 7 commits from `3845406` → `5dbd5bf`):**
- `3845406` U-10 partial — validator regex extensions for V2.4 catalog reality
- `b325d05` AUDIT_TRAIL checkpoint for 3845406
- `6481533` U-10 complete — canonical scorecard + Archon verdict clean sweep
- `3434ce5` AUDIT_TRAIL checkpoint for 6481533
- `885bdcf` U-5/PD3 — `--bundle` mode + 16 tests + docs updates + package sync
- `c1d3106` AUDIT_TRAIL checkpoint for 885bdcf
- `d981e9c` .gitignore hygiene per REPO_MAP §3.6
- `f5c523e` Scan #11 multica-ai/multica — Caution (split on Deployment ·)
  (amended to canonical V2.4 DOM after initial Sonnet authorial drift)
- `bc27e24` CLAUDE.md template-is-DOM-contract directive
- `5dbd5bf` path-b-test-prompt.md directive propagation

**Final state:**
- pytest: `279 passed in 39.51s`
- 13/13 MD+HTML pairs `--parity` clean (all 11 catalog entries + zustand-v2 + agency-agents + open-lovable)
- Repo ↔ package validator: byte-identical (0-line diff)
- 11 catalog entries (10 original + multica #11)

**All 4 Step G pre-reqs cleared:**
| Item | Commit | Status |
|---|---|---|
| U-1 V2.5-preview doc integration | `6a3e471` | ✅ |
| U-3/FX-4 fixture provenance ledger | `3c09afb` | ✅ |
| U-5/PD3 bundle/citation validator | `885bdcf` | ✅ |
| U-10 catalog re-validation | `6481533` | ✅ |

**Key decisions made this session (preserve for future sessions):**
1. **Scorecard canonical = V2.3 question set** per the V2.4 prompt (lines 743-758). The "alt" questions (*Can you trust the maintainers?* / *Is it actively maintained?*) observed in 5 HTMLs were authorial drift, NOT a prompt evolution. Fix direction: align HTMLs backward to canonical.
2. **Option A for U-10** — extend validator to match real-world V2.4 HTML variants before deciding which drifts are real content bugs. Three authorial variants documented: prefix h3 `<h3>F0 — Title</h3>`, suffix h3 `<h3>Title (F0 / C20)</h3>`, and header-span + bare h3 (the multica variant, which was subsequently rewritten to canonical).
3. **Template is the DOM contract, not the validator.** When a delegated agent produces DOM drift, rewrite the HTML to canonical — do NOT widen the validator to accept the drift. `226335f` widening was reverted; multica HTML rewritten to canonical template DOM; directive now propagated to CLAUDE.md + path-b-test-prompt.md + feedback memory.
4. **Multica scan baseline for Step G comparison:** Sonnet 4.6 delegated, 23.6 min end-to-end, 40k reported tokens, ~22 gh api calls, ~$1.50-$2.70 at Sonnet pricing. Use as V2.4 baseline; compare against V2.5-preview scans once Step G produces them.
5. **Haiku 4.5 viability:** NOT for end-to-end V2.4 delegated scans (synthesis reasoning depth + multi-document consistency beyond Haiku's reliable window). Potentially viable for V2.5-preview constrained-by-schema work as a post-Step-G optimization, since the schema externalizes much of the decision surface.
6. **U-5/PD3 lenient citation heuristic for MVP** — §11.1 line-ref (`L45`) / evidence-ID (`evidence.Governance`) formats are aspirational; existing V2.4 corpus uses informal citation. Step-G-specific tightening can layer on post-hoc.

**Board approval:** Step G pre-req queue items were queued by `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md`; this session's deliverables execute that plan. No new board review required. Next board-required gate: Step G kickoff itself, before running the first live V2.5-preview Phase 1-6 pipeline.

**Revert paths:**
- `git reset --hard 5dbd5bf` — stay at session-close state
- `git reset --hard c1d3106` — return to pre-gitignore state (loses multica scan + gitignore + directives; keeps U-5/PD3)
- `git reset --hard 3434ce5` — return to pre-U-5/PD3 state (loses all session work from this point)

**Next session starts here.** Read order: CLAUDE.md → REPO_MAP.md §2.2/§2.4/§2.5 → AUDIT_TRAIL.md top (this checkpoint) → `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` → `docs/scanner-catalog.md`. Next work: Step G kickoff board review, then first live V2.5-preview Phase 1-6 pipeline run against a shape-matched target repo.

---

## Checkpoint — 2026-04-19 — U-5/PD3 bundle/citation validator shipped

**HEAD:** `885bdcf`
**Added:** `docs/validate-scanner-report.py` +178 lines (check_bundle + parse_bundle_regions), `--bundle` CLI mode, package mirror; `tests/test_bundle_validator.py` (341 lines, 16 tests). 6 files, 633 ins / 7 del.
**State:** Last pre-Step-G board item cleared. Step G prerequisites now fully done: U-1 (`6a3e471`), U-3/FX-4 (`3c09afb`), U-5/PD3 (`885bdcf`), U-10 (`6481533`).

**Verification at commit time:**
- pytest: `279 passed in 43.56s` (up from 263; +16 new bundle-validator tests)
- Repo ↔ package validator diff: **0 lines**
- `--bundle` smoke test on all 5 V2.4 corpus bundles: clean (2 warnings for V2.4 bundles that name severity without citing F-IDs — lenient heuristic, Step G bundles should cite F-IDs directly)

**Contract (per Operator Guide §9.2.1 + §11.1):**
1. Evidence sections must not contain interpretive verbs (facts-only)
2. Pattern recognition bullets must each use an allowed interpretive verb
3. FINDINGS SUMMARY section exists and non-empty (accepts "Findings" / "Key findings" compact heading variants)
4. Proposed verdict cites at least one F-ID or names a severity level
5. F-IDs referenced in synthesis outside FINDINGS SUMMARY must appear in it (no orphan finding references)

**Design decisions recorded:**
- Lenient citation heuristic for MVP — line-ref (`L45`) / evidence-ID (`evidence.Governance`) formats not required. §11.1 aspirational for V2.5-preview bundles; V2.4 corpus uses informal citation style. Step-G-specific tightening can layer on post-hoc.
- Interpretive-verb leak in evidence = hard error (facts/inference separation is load-bearing).
- Untagged pattern bullet = hard error (inference must be self-identifying).
- Horizontal rules (`---`) and emphasis (`**x**`) correctly excluded from bullet detection via `^[-*]\s+\S` match.
- Compact bundle style (`## Findings` alone) accepted as synthesis — zustand-v3 corpus precedent.

**Documentation updates (in same commit):**
- Operator Guide §9.2.1, §11.1, §14.3, §8.8.7 updated — "deferred" language replaced with `--bundle` invocation.
- `docs/board-review-operator-guide-consolidation.md` DEFER-list entry marked shipped.
- `REPO_MAP.md` §2.4 U-5/PD3 + U-10 both marked done.

**Board approval:** Not required for this commit — board queued the item (`docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §U-5 "APPLY NEXT COMMIT 2-1"), owner-built per spec. Board review will happen at Step G kickoff when this validator gates the first live scan bundle.

**Revert:** `git reset --hard 885bdcf` to stay at bundle-validator-live state. `git reset --hard 3434ce5` to return to pre-U-5 state (loses --bundle mode + 16 tests).

---

## Checkpoint — 2026-04-19 — U-10 complete: canonical scorecard + verdict clean sweep

**HEAD:** `6481533`
**Changed:** 5 HTML scans (scorecard de-drift), 1 MD scan (zustand-v2 scorecard drift on both sides), `docs/GitHub-Scanner-Archon.{md,html}` (verdict metadata), `docs/scanner-catalog.md` (entry 2 verdict), `docs/validate-scanner-report.py` + package mirror (detect_scorecard narrowed to canonical-only). 11 files, 56 ins / 110 del.
**State:** Every catalog scan + zustand-v2 passes `--parity` clean. Canonical 4-question Trust Scorecard is the only accepted set. Archon verdict internally consistent across MD metadata + section heading + HTML banner + catalog row (all Critical).

**Verification at commit time:**
- pytest: `263 passed in 44.80s`
- Repo ↔ package validator diff: **0 lines**
- `--parity` clean on 12 MD+HTML pairs: caveman, Archon, zustand, fd, gstack, archon-board-review, hermes-agent, postiz-app, zustand-v3, zustand-v2, agency-agents, open-lovable

**Source of canonical set:** `docs/repo-deep-dive-prompt.md:743-758` (V2.4 prompt, Trust Scorecard section). Questions:
1. Does anyone check the code?
2. Do they fix problems quickly?
3. Do they tell you about problems?
4. Is it safe out of the box?

**Drift origin:** 5 scans were authored with non-canonical "Can you trust the maintainers?" + "Is it actively maintained?" wording. No prompt version ever defined those — pure authorial drift. Commit `cf6afcd` (2026-04-18) had reverted 4 MDs back to canonical without touching their HTMLs, creating MD↔HTML divergence that `--parity` caught once the regex gaps were closed in `3845406`.

**Board approval:** Not required — fixes align the catalog to the prompt's documented canonical set (no new semantic decisions). Owner-directed clean sweep.

**Revert:** `git reset --hard 6481533` to stay at clean-swept state. `git reset --hard 3845406` returns to validator-narrow-pending state (5 content bugs re-exposed).

---

## Checkpoint — 2026-04-19 — U-10 partial: validator regex extensions for V2.4 catalog

**HEAD:** `3845406`
**Changed:** `docs/validate-scanner-report.py` + package mirror (158 ins/40 del each) + `tests/test_validator.py` (5 ins/4 del). 244 ins / 81 del across 3 files.
**State:** `--parity` now correctly discriminates V2.4 authorial variants. 4 of 9 MD+HTML catalog pairs clean (caveman, zustand, hermes-agent, zustand-v3). 5 remain with real content bugs isolated for separate decision (Archon split-verdict, + 4 scorecard V2.3/V2.4 mismatches).

**Verification at commit time:**
- pytest: `263 passed in 44.84s`
- Repo ↔ package validator diff: **0 lines**
- Package validator `--parity` on zustand V2.4 reference: clean
- U-10 run log in `/tmp/u10-revalidation/` (4 runs showing progressive triage)

**Validator delta vs `ce698d4` Step F R3 state:**
- F-ID pattern extended to accept `.` (F-crates.io)
- MD h3 separator accepts `&middot;`/`·` (hermes-agent style)
- HTML h3 split: finding-card (MD-canonical strict) vs reference-tag (warning)
- Pattern 4 tail-paren ID: only single-F-ID ID-only tails; rejects composites and prose
- Evidence cards filtered by preceding `Evidence N` tag (shared `finding-card` CSS class)
- Scorecard detector accepts V2.3 or V2.4 question set, singular "maintainer" accepted
- Verdict regex reads CSS-stripped body (no CSS rule shadowing)

**Remaining content-bug ledger (deferred, NOT blocking):**
- Archon: MD title "Verdict: Caution (split)" vs HTML verdict-banner class "critical" — authorial inconsistency on which deployment axis drives the primary banner color
- fd, gstack, archon-board-review, postiz-app: MD scorecard reverted to V2.3 in `cf6afcd` (2026-04-18), HTMLs left on V2.4 — needs scorecard-version canonical decision

**Board approval:** Not required (regex tuning only, no semantic behavior change on passing scans; owner-authored). Content-bug resolution (above) may warrant board review before bulk edits — pending owner direction.

**Revert:** `git reset --hard 3845406` to stay at this validator state; `git reset --hard 886eef1` to return to pre-U-10 state (loses validator improvements, re-exposes regex gaps masking real catalog bugs).

---

## Checkpoint — 2026-04-19 03:47 UTC — U-3/FX-4 fixture provenance ledger

**HEAD:** `3c09afb`
**Added:** `tests/fixtures/provenance.json` (54 lines) — Codex separate-file approach for fixture provenance
**State:** Phase 7 renderer Steps A-F complete, U-1 + U-3/FX-4 applied. Step G cleared (pending U-5/PD3 + U-10).

**Verification at commit time:**
- pytest: `263 passed in 42.11s`
- provenance.json validates as JSON; 3 fixtures tagged (zustand: authored-from-scan-data; caveman + archon-subset: back-authored-from-golden-md)
- No regression — same 263 tests as prior checkpoint

**Board approval:** schema-untouched approach approved in `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §5.1 (Codex R3 ADJUST adopted by owner directive 2-1 over Pragmatist+DeepSeek schema-mutation)

**Revert:** `git reset --hard 3c09afb`

---

## Checkpoint — 2026-04-19 00:16 UTC — Step G kickoff board review archived

**HEAD:** `7e285f1`
**Archived:** `docs/External-Board-Reviews/041826-step-g-kickoff/` (R1-R3 full record, 14 files)
**State:** U-1 shipped and confirmed. Step G cleared by 3-0 sign-off.

**Verification at commit time:**
- pytest: 263/263
- Validator `--report` + `--parity` clean on zustand/caveman/archon-subset
- Board: Pragmatist SIGN OFF (R3 upgrade), Codex SIGN OFF WITH DISSENTS (non-blocking terminology debt), DeepSeek SIGN OFF WITH DISSENTS (non-blocking env-var preference)

**Board approval:** `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md`

**Revert:** `git reset --hard 7e285f1` — preserves U-1 doc changes

---

## Checkpoint — 2026-04-19 00:09 UTC — U-1 V2.5-preview docs integrated

**HEAD:** `6a3e471`
**Changed:** 5 docs updated (CLAUDE.md, SCANNER-OPERATOR-GUIDE.md §8.4 + new §8.8, Scan-Readme.md V2.4 refresh, repo-deep-dive-prompt.md one-line cross-ref, scanner-catalog.md rendering-pipeline column). 237 insertions / 73 deletions.
**State:** V2.5-preview pipeline documented as Step-G-experimental across operator-facing docs. Path A/B renamed to continuous/delegated (legacy aliases preserved for catalog flag values). Triple-warning gate in §8.8. Structural-parity criterion for Step G success. Rollback contract.

**Verification at commit time:**
- pytest: `263 passed in 40.33s`
- All 3 fixtures render + validator clean + parity zero errors + zero warnings
- CSS line count: 824 (verified via `wc -l docs/scanner-design-system.css`)

**Board approval:** R2 unanimous direction, R2 split resolutions 2-1 in owner's favor on FX-3b timing + gating mechanism, unanimous on Scan-Readme scope. See `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §5.1/5.2/5.3.

**Revert:** `git reset --hard 6a3e471` — reverts to state before board archive (R3 responses still in `.board-review-temp/step-g-kickoff/`)

---

## Checkpoint — 2026-04-19 00:01 UTC — FX-3b package validator sync

**HEAD:** `60e0bf2`
**Changed:** `github-scan-package-V2/validate-scanner-report.py` (1 file, 12 insertions / 1 deletion). Package validator now byte-identical to repo validator.
**State:** V2.4 package validator bug fixed. Real bug affecting V2.4 scans with shell-glob evidence (demonstrated against caveman shape). Not a V2.5 feature — V2.4 correctness fix.

**Verification at commit time (DeepSeek R2-directed validation step):**
- Repo ↔ package validator diff: **0 lines**
- Package `--report` on V2.4 reference `docs/GitHub-Scanner-zustand.html`: clean
- Package `--parity` on V2.4 reference: all 6 finding IDs matched
- Package `--report` + `--parity` on V2.5-preview zustand render: clean, all 6 finding IDs matched
- Package `--parity` on caveman shell-glob case: **all 9 finding IDs matched, zero errors, zero warnings** (this was the reproducible failure mode FX-3b resolves)

**Board approval:** parallel-commit-before-U-1 approved 2-1 in R2 (`docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §5.1)

**Revert:** `git reset --hard 60e0bf2` — reverts U-1 but keeps package validator fix; OR `git reset --hard 638472d` to also revert the package validator (exposes V2.4 bug again — NOT recommended)

---

## Checkpoint — 2026-04-18 23:25 UTC — Step F R3 fixes (XSS + CSS + parity + comment-strip)

**HEAD:** `ce698d4`
**Changed:** 3 files, 23 insertions / 4 deletions. FX-1 `prior_scan_note` XSS fix. FX-2 CSS autoescape corruption fix (33 `&#39;` occurrences eliminated inside `<style>` blocks). FX-3 parity regex H3 Pattern 3 with strip-tags-first. FX-3b validator comment-strip bug removal (emergent — shell globs in evidence text were eating finding cards).
**State:** V2.5-preview renderer pipeline considered production-ready at the renderer layer. All 3 fixtures produce clean output. Parity check has **zero errors AND zero warnings** (previously 1 warning-level false-negative baseline).

**Verification at commit time:**
- pytest: 263/263 passing
- `&#39;` count inside `<style>` block: **0 across all 3 fixtures** (was 37 on zustand pre-fix)
- Validator `--report` clean on all 3 rendered HTMLs
- Parity: all finding IDs matched — zustand 6/6, caveman 9/9, archon-subset 4/4

**Board approval:** 3-model R3 deliberation adopted Codex's strip-tags-first regex (ADJUST over owner's initial + DeepSeek's DOTALL regex). R4 confirmation SIGN OFF (2) + SIGN OFF WITH DISSENTS (1, bookkeeping pytest-warning nit). See `docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md`.

**Revert:** `git reset --hard ce698d4`

---

## Checkpoint — 2026-04-18 22:35 UTC — Step F HTML renderer + cross-shape fixtures

**HEAD:** `402f933`
**Changed:** 21 files, 4235 insertions. `docs/render-html.py` (117-line shim) + `docs/templates-html/scan-report.html.j2` + 14 partials (~1029 lines) + `tests/fixtures/caveman-form.json` (1305 lines, 9 findings) + `tests/fixtures/archon-subset-form.json` (1199 lines, 4 findings, first V1.1 C3 auto_load_tier exercise) + `tests/test_render_html.py` (117 parameterized tests).
**State:** HTML renderer shipped against 3 cross-shape fixtures. 263 tests passing (up from 146). Known defects at this commit: `prior_scan_note` XSS + CSS escape + parity regex H3 gap + validator comment-strip bug — all resolved in next checkpoint (`ce698d4`).

**Verification at commit time:**
- pytest: 263 passed
- All 3 fixtures render + validator `--report` clean
- `--parity` clean with 1 warning per fixture (baseline false-negative matching reference scan behavior — resolved in R3 fixes)

**Board approval:** Step F alignment review R1-R4 at `docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md` authorized R3 fixes; Step F commit itself is the implementation under review.

**Revert:** `git reset --hard 402f933` — reverts to state before XSS/CSS fixes (known defects)

---

## Checkpoint — 2026-04-18 21:50 UTC — Step E validator gate clean

**HEAD:** `cf8c576`
**Changed:** Verification record only (`docs/External-Board-Reviews/041826-renderer-impl-verify/STEP-E-verification.md`) + INDEX update. No code delta — validator `--report` on zustand-rendered.md exits 0 on first try.
**State:** MD renderer verified clean against V1.1 schema + enriched zustand fixture. Phase 7 Steps A-E complete. Step F (HTML renderer) next.

**Verification at commit time:**
- pytest: 146/146 passing
- `python3 docs/validate-scanner-report.py --report /tmp/rendered.md` → exit 0

**Board approval:** mechanical verification, no board review required per plan

**Revert:** `git reset --hard cf8c576` — state before Step F (HTML renderer doesn't exist at this checkpoint)

---

## Checkpoint — 2026-04-18 14:32 UTC — Step D structural assertion tests

**HEAD:** `aac2b3b`
**Changed:** `tests/test_render_md.py` flipped from exact-match to structural assertions. +39 tests in 9 new classes.
**State:** MD renderer covered by 65 structural tests across 12 classes. 146/146 tests passing (up from 107).

**Verification at commit time:**
- pytest: 146 passed

**Revert:** `git reset --hard aac2b3b`

---

## Checkpoint — 2026-04-18 14:22 UTC — Step C zustand fixture enrichment

**HEAD:** `59224ac`
**Changed:** `tests/fixtures/zustand-form.json` 705 → 1015 lines. 10 fix-artifacts approved by 3-model board (`docs/External-Board-Reviews/041826-fixture-enrichment/` R1 UNANIMOUS 3-0).
**State:** Zustand fixture has all structural-LLM fields populated (executable_file_inventory, PR sample, verdict_exhibits, repo_vitals, coverage_detail, evidence entries, per-finding enrichment). First V1.1-compliant fixture.

**Verification at commit time:**
- pytest: 107 passed
- Fixture validates clean against schema V1.1
- Render output 540 lines (vs golden 602; 62-line gap is prose density — intentional "prose stays sparse" rule)

**Board approval:** `docs/External-Board-Reviews/041826-fixture-enrichment/CONSOLIDATION.md`

**Revert:** `git reset --hard 59224ac`

---

## Checkpoint — 2026-04-18 13:59 UTC — Step A C2 BLOCK resolution

**HEAD:** `c6531bb`
**Changed:** `docs/scan-schema.json` — `file_sha`, `line_ranges`, `diff_anchor` now required-always-nullable on every `executable_file_inventory_entry`.
**State:** V1.1 schema freeze completion. Resolves Codex R2 BLOCK in renderer-impl-verify R1 via owner directive adopting Codex's R2 dissent position.

**Verification at commit time:**
- Fixture (zustand) re-validates clean against updated schema

**Board approval:** `docs/External-Board-Reviews/041826-renderer-impl-verify/` R1 Codex BLOCK resolved by owner directive; final position captured in CONSOLIDATION.

**Revert:** `git reset --hard c6531bb` — state before Step C enrichment

---

## Checkpoint — 2026-04-18 13:47 UTC — Step B render-md.py Jinja2 refactor

**HEAD:** `75db969`
**Changed:** `docs/render-md.py` rewritten 782 → 117 lines as a Jinja2 shim + 15 template files at `docs/templates/` (scan-report.md.j2 top-level + 14 partials, 508 lines total). Thin Python + templates architecture per Option C (board-approved Step F alignment R4).
**State:** MD renderer is template-driven. Formatting logic lives in .j2 files. Shim exposes helpers + renders via FileSystemLoader.

**Verification at commit time:**
- pytest: 107 passed
- `render-md.py tests/fixtures/zustand-form.json` produces a clean MD

**Board approval:** Option C (Jinja2) approved unanimously in `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` R4

**Revert:** `git reset --hard 75db969`

---

## Checkpoint — 2026-04-18 13:33 UTC — Step A schema freeze V1.1

**HEAD:** `2b576bf`
**Changed:** `docs/scan-schema.json` 1054 → 1412 lines. V1.0 → V1.1. Added renderer-driven `$defs` (verdict_exhibit_group/item, executable_file_inventory, pr_sample_review, coverage_detail, repo_vitals_row, section_lead, per_finding_prose_entry, timeline_tone). Reconciled stale shapes. C2 conditional (file_sha/line_ranges/diff_anchor on executable_file_inventory_entry). C3 conditional (auto_load_tier on agent-rule-injection category).
**State:** V1.1 schema is the canonical form contract for the V2.5-preview pipeline. Subsequent fixes (`c6531bb`) refined C2 to required-always-nullable.

**Verification at commit time:**
- Schema is valid JSON; structure reviewed by R4 board

**Board approval:** Step F alignment review R1-R4 at `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`

**Revert:** `git reset --hard 2b576bf` — V1.0 schema state, renderers don't exist yet

---

## Pre-Step-F baseline (2026-04-18 prior)

Tests at 107 (pre-Step-D additions). MD renderer exists post-Step-B. V1.1 schema landed in Step A. Older commits (Step C, D, E, F) not individually checkpointed here — see `git log --oneline` for raw history and `docs/External-Board-Reviews/` for decision context.

**Broad pre-Step-F baseline:** `2b576bf..402f933` is the Steps A-F arc. `ce698d4` is the cleanup-complete point. Everything after `402f933` has ≥263 tests.

---

## Maintenance

- **When to add a checkpoint:** after any commit that represents a named milestone (Step X, U-N, board review archived, significant bug fix landed). Do not add one per mechanical commit.
- **Rebuild instructions:** if you need to regenerate this file from scratch, walk `git log --oneline` looking for "Step", "U-", "FX-", "Archive" prefixes; run `git show <sha>` for each to extract verification state from commit messages.
- **Cross-references:** `REPO_MAP.md` for what currently exists · `docs/External-Board-Reviews/README.md` for board review master index · `CLAUDE.md` for operator entry point.
