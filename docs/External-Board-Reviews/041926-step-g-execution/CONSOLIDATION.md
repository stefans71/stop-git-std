# CONSOLIDATION — Step G Execution Approach

**Date:** 2026-04-19
**Reviewed:** Proposed approach for executing Step G of the Phase 7 renderer plan — first live V2.5-preview JSON-first pipeline run on 3 shape-matched repos (zustand, caveman, Archon). Approach-only review (no code applied; this gates execution).
**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
**Rounds:** R1 Blind → R2 Consolidation → R3 Confirmation (3-round SOP; no R4 — R2 converged cleanly)
**HEAD at review start:** `30da757`
**Board:** Pragmatist (Claude Sonnet 4.6, same-model blind-spot rule since Opus authored §8.8 operator spec), Systems Thinker (Codex GPT-5 as llmuser from /tmp), Skeptic (DeepSeek V4 via qwen -y --model deepseek-chat from repo dir)

---

## Final verdict

**SIGN OFF — UNANIMOUS CLEAN.** Step G may proceed. No trailing dissents. All 41 dissent items raised across R1 + R2 resolved at R3 (dissent audit below).

| Agent | R1 | R2 | R3 |
|---|---|---|---|
| Pragmatist (Sonnet 4.6) | SIGN OFF W/ DISSENTS (3 FIX NOW + 2 DEFER + 2 INFO + 4 blind spots) | **SIGN OFF** (all 24 items voted: 9× SECOND, 15× CONFIRM) | **SIGN OFF** (5/5 CONFIRM, no regressions) |
| Systems Thinker (Codex GPT-5) | SIGN OFF W/ DISSENTS (4 FIX NOW + 1 DEFER + 1 INFO + 2 blind spots) | SIGN OFF W/ DISSENTS (2 ADJUSTs on FN-4 + FN-8, 1 on D-4) | **SIGN OFF** (5/5 CONFIRM — strictness threshold met) |
| Skeptic (DeepSeek V4) | SIGN OFF W/ DISSENTS (3 FIX NOW + 2 DEFER + 3 INFO + 4 blind spots + worst-case walkthrough) | SIGN OFF W/ DISSENTS (2 ADJUSTs on FN-4 + FN-8, 1 strengthening on FN-1, 1 elevation on D-6) | **SIGN OFF** (5/5 CONFIRM — worst-case closed, R3 conditions met) |

---

## What was approved

### Final fix artifact set (9 items, FN-1 through FN-9)

**Pre-execution harness:**
- **FN-6** — Pre-flight V2.4 comparator `--parity` cleanliness check (3 pairs must be warning-free before execution begins)
- **FN-3** — Adversarial bundle smoke test (4-case: synthesis verb, orphan F-ID, missing FINDINGS SUMMARY, plus compact-bundle PASS baseline)

**Execution discipline:**
- **FN-7** — Pilot-and-checkpoint ordering (zustand → hard checkpoint → caveman + Archon)
- **FN-9** — Bundle-complete gate (3c.1–3c.3: all sections present, `--bundle` clean, bundle committed to `scan-bundles/`) before any `form.json` authoring begins
- **FN-2** — Mandatory `python3 docs/compute.py` invocation for Phase 3 fields; "mirror the logic" disallowed; outputs captured as `compute-output-<target>.json` artifacts; byte-for-byte equality with `form.json` phase_3_computed

**Post-render checks:**
- **FN-8** — Phase-boundary contamination check on **all 3 targets** (not first-only), using **semantic** criteria (no narrative sentences/synthesis claims in Phase 4 structured fields), **STOP on contamination** anywhere
- **FN-5** — Warning-count inspection, not exit-code reliance: `grep -c '^WARNING:' <parity-output>` must equal 0; applies to `--parity` + `--bundle` modes

**Acceptance gates:**
- **FN-1** — Structural-parity zero-tolerance checklist (gate 9.1–9.6: finding inventory, severity per F-ID, scorecard cells, verdict level, split-axis, evidence linkage — all exact match); severity mapping documented per finding as audit trail; Archon-specific comparator clarification (full `GitHub-Scanner-Archon.md`, not subset fixture)
- **FN-4** — Graduated failure disposition rubric: pipeline-correctness failures (gates 1–3, 5) = full rollback; authoring errors (gate 4, schema) = target-local with one retry; gate-6 single-target failure (after one retry) = Step G **FAIL** (overall), isolated disposition, not full rollback, V2.5-preview NOT promoted as Step-G-passed until all 3 shapes pass; gate-6 multi-target failure = full rollback; rubric ambiguity = HALT

**Key principle (Codex verdict-strictness preserved):** "Partial pass" language removed. Step G is only called passed when all 3 shapes pass all gates including gate 6 after permitted retries. Graded disposition governs operational handling, not the pass/fail verdict.

### Carry-forward dispositions (15 items, D-1 through D-6, I-1 through I-9)

| ID | Item | Final disposition |
|---|---|---|
| D-1 | Fresh-HEAD live scan validation | DEFER (post-Step-G V2.5-production pre-req) |
| D-2 | Phase 3 automated pipeline harness | DEFER (future-cycle; FN-2 covers manual-but-disciplined path) |
| D-3 | LLM non-determinism on `form.json` re-authoring | DEFER (not a Step G gate; documented in FN-8 §6c) |
| D-4 | Schema hardening (§00 + §08 gaps) | DEFER **with explicit watchpoint** — any need to invent ad hoc fields, overload existing fields, or carry semantics outside schema-defined locations upgrades immediately to FIX NOW and halts execution |
| D-5 | Schema hardening for missing shapes (fd, gstack, postiz-app, hermes-agent) | DEFER (post-Step-G fixture-authoring cycle) |
| D-6 | Automated severity distribution comparison script | **POST-STEP-G IMMEDIATE FOLLOW-UP** — build before first production V2.5-preview scan beyond the 3 validation shapes (elevated from DEFER per DeepSeek R3) |
| I-1 | provenance.json ordering_constraints | CONFIRM — operator reads ordering section during kickoff; create step-g-live entries BEFORE authoring (step -2 in execution checklist) |
| I-2 | archon-subset 4-of-11 scope boundary | CONFIRM — folded into FN-1 Archon-specific clarification |
| I-3 | zustand-form.json `authored-from-scan-data` provenance | CONFIRM — template for shape, NOT evidence of pipeline correctness |
| I-4 | HEAD state inconsistency (brief vs REPO_MAP/AUDIT_TRAIL) | CONFIRM — `30da757` current; REPO_MAP sync post-Step-G |
| I-5 | zustand-v3 `formal_review_rate` 29%/45% fixture/golden discrepancy | CONFIRM — anchor is V2.4 MD/HTML, not fixture |
| I-6 | caveman/Archon table-vs-bullet scorecard format | CONFIRM — V2.4 rendering variation, cell content/color matters, not presentation |
| I-7 | Shape-coverage gap (Step G cannot detect shape-specific schema gaps) | CONFIRM — acknowledged limitation, D-5 is remedy path |
| I-8 | Continuous mode diagnostic rationale | CONFIRM — no action |
| I-9 | LLM non-determinism false confidence | CONFIRM — render-determinism scope bounded, authoring-determinism is D-3 deferred |

### R2 adjustments applied (A-1 through A-8)

| # | Item | Change | Source |
|---|---|---|---|
| A-1 | FN-1 gate 9.2 | Severity mapping documentation requirement (`<F-ID> \| <V2.4 severity> \| <V2.5-preview severity> \| match?` per finding) | DeepSeek R2 framing answer |
| A-2 | FN-4 gate-6 row | Replace "Step G partial pass" wording with "Overall Step G = FAIL, isolated target failure, not full rollback, V2.5-preview NOT promoted as Step-G-passed until all 3 shapes pass" | Codex R2 FN-4 ADJUST |
| A-3 | FN-4 gate-6 row | Add "after one retry" qualifier before partial-failure disposition | DeepSeek R2 FN-4 ADJUST |
| A-4 | FN-8 scope | All 3 targets, not first-only | Codex + DeepSeek R2 convergence |
| A-5 | FN-8 criteria | Semantic ("no narrative sentences or synthesis claims in Phase 4 structured fields"), not word-count (>40 words) heuristic | Codex R2 FN-8 ADJUST |
| A-6 | FN-8 STOP | Halt execution if phase-boundary contamination found in any target | DeepSeek R2 FN-8 ADJUST |
| A-7 | D-4 wording | Explicit watchpoint with halt-on-smuggle clause (replaces soft "active watch item") | Codex R2 D-4 ADJUST |
| A-8 | D-6 disposition | DEFER → POST-STEP-G IMMEDIATE | DeepSeek R2 D-6 framing answer |

---

## Dissent audit — 41 items, zero silent drops

Every dissent item raised across R1 + R2 is traced to its R3 resolution below. Pre-archive gate per SOP §9: zero silent drops is the pass criterion. **This audit PASSED.**

### R1 dissents (36 items — includes author-withdrawn ±10% tolerance and non-escalated operational note as explicit dispositions)

**Pragmatist R1 — 15 items:**

| # | R1 item | R2 vehicle | R3 resolution |
|---|---|---|---|
| P-FN-1 | Structural-parity 5-item checklist | owner FN-1 (6-point zero-tolerance; ±10% withdrawn, exact linkage adopted) | CONFIRM + A-1 |
| P-FN-2 | `compute.py` mandatory, remove "mirror logic" | owner FN-2 | R2 unanimous SECOND · R3 carry |
| P-FN-3 | Bundle smoke test before first bundle | owner FN-3 | R2 unanimous SECOND · R3 carry |
| P-D-1 | Fresh-HEAD validation deferred | D-1 | unanimous CONFIRM DEFER |
| P-D-2 | Phase 3 automation harness deferred | D-2 | unanimous CONFIRM DEFER |
| P-I-1 | provenance.json ordering_constraints | I-1 | unanimous CONFIRM |
| P-I-2 | archon-subset 4-of-11 scope | I-2 | CONFIRM (folded into FN-1 Archon clarification) |
| P-BS-1 | archon-subset vs full-catalog landmine | FN-1 Archon clause | R3 CONFIRM |
| P-BS-2 | `phase_4b_computed` must be computed not authored | FN-2 byte-for-byte equality | R3 CONFIRM |
| P-BS-3 | Bundle must be complete before form.json authoring | NEW owner FN-9 (bundle-complete gate) | R3 CONFIRM |
| P-BS-4 | zustand-v3 `formal_review_rate` 29%/45% discrepancy | I-5 (anchor V2.4 MD/HTML) | unanimous CONFIRM |
| P-Q1 | zustand `authored-from-scan-data` provenance | I-3 | unanimous CONFIRM |
| P-Q4-2nd | Compact-bundle `## FINDINGS SUMMARY` with 0 F-IDs | FN-3 case 0.4 (PASS baseline) | R3 CONFIRM |
| P-Q6 | Dissent from binary rollback | FN-4 graduated rubric | R3 CONFIRM + A-2/A-3 |
| P-R1-withdraw | ±10% evidence ref count tolerance | Author-withdrawn in R2 framing answer in favor of exact linkage | Disposition: author-resolved; noted here for traceability |

**Codex R1 — 11 items:**

| # | R1 item | R2 vehicle | R3 resolution |
|---|---|---|---|
| C-FN-1 | Remove "or mirror their logic" | owner FN-2 | R3 CONFIRM |
| C-FN-2 | 6-point pre-render semantic checklist | owner FN-1 | R3 CONFIRM + A-1 |
| C-FN-3 | Predeclare failure rubric (isolated vs systemic) | owner FN-4 | R3 CONFIRM + A-2 |
| C-FN-4 | Adversarial `--bundle` smoke | owner FN-3 | R3 CONFIRM |
| C-D-1 | Schema hardening deferred | D-4 | R3 CONFIRM + A-7 |
| C-I-1 | Provenance discipline | I-1 | unanimous CONFIRM |
| C-Q1 | "1+2 sequential" (pilot+checkpoint) | owner FN-7 | R3 CONFIRM |
| C-BS-1 | `--parity`/`--bundle` return 0 on warnings | owner FN-5 | R3 CONFIRM |
| C-BS-2 | HEAD state-inconsistency | I-4 | unanimous CONFIRM |
| C-add | zustand-form.json not pipeline-produced | I-3 | unanimous CONFIRM |
| C-arch | 3-target sequential CHECKPOINTED | owner FN-7 | R3 CONFIRM |

**DeepSeek R1 — 14 items:**

| # | R1 item | R2 vehicle | R3 resolution |
|---|---|---|---|
| D-FN-1 | Structural-parity tolerance thresholds | owner FN-1 | R3 CONFIRM + A-1 |
| D-FN-2 | Bundle smoke test with deliberate violations | owner FN-3 | R3 CONFIRM |
| D-FN-3 | V2.4 comparator parity cleanliness | owner FN-6 | R3 CONFIRM |
| D-DF-1 | Schema hardening for missing shapes | D-5 | unanimous CONFIRM DEFER |
| D-DF-2 | Automated severity distribution script | D-6 | R3 CONFIRM + A-8 (elevated to POST-STEP-G IMMEDIATE) |
| D-IF-1 | Continuous mode rationale | I-8 | unanimous CONFIRM |
| D-IF-2 | Provenance tagging before authoring | I-1 | unanimous CONFIRM |
| D-IF-3 | Rollback contract clarity | FN-4 | R3 CONFIRM + A-2/A-3 |
| D-Q1 | Shape-coverage gap (meta-dissent) | I-7 | unanimous CONFIRM |
| D-4.1 | Evidence ref integrity | FN-1 gate 9.6 exact linkage | R3 CONFIRM |
| D-4.2 | Scorecard cell color inversion | FN-1 gate 9.3 cell-by-cell | R3 CONFIRM |
| D-4.3 | Phase boundary contamination | owner FN-8 | R3 CONFIRM + A-4/A-5/A-6 |
| D-4.4 | LLM re-authoring determinism | FN-8 §6c + I-9 (documented as D-3) | unanimous CONFIRM |
| D-WW | Worst-case systematic severity downgrade | FN-1 gate 9.2 zero-inversion + A-1 mapping doc | R3 CONFIRM |

### R2 dissents (5 items new at consolidation)

**Pragmatist R2 — 1 item:**

| # | R2 item | R3 resolution |
|---|---|---|
| P-R2-op | FN-5 output capture via `tee`/redirect — operational note, explicitly NOT elevated to FN-10 per Pragmatist's own R2 instruction | Absorbed as optional guidance in R3 §4 without gate-weight · Pragmatist R3 confirmed disposition matches intent |

**Codex R2 — 3 ADJUSTs:**

| # | R2 ADJUST | Applied as | R3 |
|---|---|---|---|
| C-R2-FN4 | FN-4 verdict-strictness: "17/18 NOT a pass" | A-2 (verbatim wording replacement) | R3 CONFIRM "preserves strict verdict I required" |
| C-R2-FN8 | FN-8 all-target + semantic criterion | A-4 + A-5 | R3 CONFIRM |
| C-R2-D4 | D-4 watchpoint with halt-on-smuggle | A-7 (verbatim) | R3 CONFIRM "matches my R2 wording" |

**DeepSeek R2 — 4 items (3 ADJUSTs + 1 framing strengthening):**

| # | R2 ADJUST | Applied as | R3 |
|---|---|---|---|
| D-R2-FN1 | FN-1 9.2 severity mapping documentation | A-1 | R3 CONFIRM "creates auditable trail" |
| D-R2-FN4 | FN-4 retry before partial-failure disposition | A-3 | R3 CONFIRM |
| D-R2-FN8 | FN-8 STOP on contamination | A-6 | R3 CONFIRM |
| D-R2-D6 | D-6 POST-STEP-G IMMEDIATE commitment | A-8 | R3 CONFIRM |

### Audit summary

- **Total dissent items:** 41
- **Applied via FIX NOW artifact (FN-1 through FN-9):** 24 items
- **Applied via carry-forward (D-1 through D-6, I-1 through I-9):** 15 items
- **Author-withdrawn at R2 (explicit):** 1 item (Pragmatist ±10%)
- **Absorbed as non-gate guidance (explicit):** 1 item (Pragmatist FN-5 `tee`/redirect)
- **Silent drops:** **0**
- **Pass criterion met:** YES

Every ADJUST (A-1 through A-8) traces to specific source agent + source round. Applied text is quoted verbatim in `r3-brief.md` §4–§5.

---

## Process learnings (captured for SOP + future reviews)

1. **R2 briefs must include ALL dissent items, not just FIX NOW convergence.** First R2 draft only had FN items and silently dropped 15 DEFER/INFO/blind-spot items. Stateless agents cannot vote on what they cannot see. Owner catch forced a rewrite adding the full R1 carry-forward table (§6 in R2 brief). This pattern should be mandatory in every R2.

2. **Dissent audit before archiving.** Asking "list every dissent and how it was resolved" before closing is a pre-archive gate. 41 items across 3 rounds, zero silent drops — that is the proof the process worked. **Made mandatory in SOP §9 as a pre-archive gate** (see SOP update accompanying this archive).

3. **The "widen the validator vs fix the content" pattern keeps recurring.** U-10 scorecard drift (catalog re-validation surfaced 5 real content bugs, first instinct was validator widening) + multica DOM drift (Sonnet-delegated scan invented class names, first instinct was validator regex widening, committed and reverted as `454c58d`) — both times the instinct was to widen the validator to accommodate authorial drift rather than enforce the spec. The FX-3b principle from Step F applies to DOM template just as it applies to evidence text: **when the validator and the content disagree, check the spec first.** Worth documenting as a general principle alongside the template-is-DOM-contract directive.

4. **Codex is the strictness anchor.** Across both Step G–related reviews (041826-step-g-kickoff and this 041926-step-g-execution), Codex consistently pushed for tighter pass/fail criteria: schema-hardening defer-ledger discipline at kickoff, "17/18 NOT a pass" verdict strictness at execution. That strictness prevents "partial pass" framing that erodes gates over time. Codex's verdict-language in FN-4 (A-2) is load-bearing — without it, the graduated rubric could have implied operational leniency for Step G's acceptance claim.

5. **Three-surface directive propagation works.** CLAUDE.md + brief template + operator memory closed the DOM drift gap after multica (commits `bc27e24` + `5dbd5bf` + feedback memory). Same three-surface pattern applies to any future process fix: repo-level spec (CLAUDE.md or docs), template-level instruction (brief template or SOP section), operator-level reminder (memory file or CLAUDE.md). Prefer all three when a new invariant is introduced.

---

## Process notes (run-specific)

- **R2 catch:** owner flagged missing DEFER/INFO/blind-spot rows in first R2 draft. Rewritten with full 15-item carry-forward table before agent launch. This cost ~10 minutes of rework but produced complete stateless context for agents. Without the catch, 15 items would have silently dropped.
- **Model selection:** Pragmatist used Sonnet 4.6 per same-model blind-spot rule (Opus authored §8.8 operator spec). Sonnet's R2 SIGN OFF clean (ahead of Codex + DeepSeek) validates the cross-model diversity; Opus-Opus pairing would likely have produced agreement echo without the ADJUSTs.
- **DeepSeek V4 thoroughness:** R1 = 114 lines, R2 = 65 lines, R3 = 30 lines. Scaled appropriately with scope. User had expressed concern DeepSeek might be terse; observed output was compact but complete (24-row R2 vote table produced on request). No items skipped.
- **Codex file-write permission quirk:** llmuser cannot write to root-owned `.board-review-temp/`. Codex outputs land in `/tmp/codex-r<N>.md` and get moved by facilitator. Not a blocker; documented in board runbook.
- **3-round sufficient, no R4:** R2 converged cleanly with compatible ADJUSTs (Codex verdict-language and DeepSeek retry semantics operate on different axes of the same rule). R3 was narrow confirmation. Full 4-round SOP not needed.

---

## Agent invocation reference (snapshot for future reruns)

**Pragmatist (Sonnet 4.6):**
```
Agent tool with subagent_type="general-purpose", model="sonnet", run_in_background=true
```

**Systems Thinker (Codex GPT-5 via llmuser from /tmp):**
```bash
sudo -u llmuser bash -c "cd /tmp && codex exec --dangerously-bypass-approvals-and-sandbox '<prompt>'"
```

**Skeptic (DeepSeek V4 via Qwen CLI from repo dir):**
```bash
OPENAI_API_KEY="$DEEPSEEK_API_KEY" OPENAI_BASE_URL="https://api.deepseek.com/v1" \
  qwen -y -p "<prompt>" --model deepseek-chat
```

---

## Files in this folder

- `CONSOLIDATION.md` — this file
- `r1-brief.md` · `r2-brief.md` · `r3-brief.md` — per-round briefs
- `pragmatist-r{1,2,3}.md` · `codex-r{1,2,3}.md` · `deepseek-r{1,2,3}.md` — 9 per-agent responses

---

## References

- Prior Step G gate: `../041826-step-g-kickoff/CONSOLIDATION.md` (U-1 doc integration + 4 pre-req queue)
- Step F: `../041826-step-f-alignment-validation/CONSOLIDATION.md` (Step F + Step G readiness review that queued the pre-reqs)
- Renderer plan: `../041826-renderer-alignment/CONSOLIDATION.md` (7-step plan A→G)
- Operator spec: `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 (V2.5-preview pipeline, 7 subsections)
- FrontierBoard SOP: `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md` (§9 pre-archive dissent audit gate added in this cycle)
- Pre-req commits cleared: `6a3e471` (U-1) · `3c09afb` (U-3/FX-4) · `885bdcf` (U-5/PD3) · `6481533` (U-10)
