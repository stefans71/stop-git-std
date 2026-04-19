# Board Review R1 (Blind) — Step G Execution Kickoff

**Date:** 2026-04-19
**Reviewing:** Proposed approach for executing Step G (first live V2.5-preview Phase 1–6 pipeline run on 3 shape-matched repos). NO pipeline code yet run; this is an approach review.
**Round:** R1 Blind — each agent drafts independently
**Rounds planned:** Blind → Consolidation → Confirmation (3-round SOP; escalate to R4 only if R2 splits)
**HEAD at review start:** `30da757` (session-close doc commit)
**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
**Board composition** (per `REPO_MAP.md` §2.3):
- Pragmatist — Claude Sonnet 4.6 (same-model blind-spot rule; Opus authored Step G operator spec)
- Systems Thinker — Codex GPT-5 via `sudo -u llmuser` from `/tmp`
- Skeptic — DeepSeek V4 via `qwen -y --model deepseek-chat` from repo directory

**STATELESS.** Read fresh. Fix-artifact-first governance: owner proposes approach + draft snippets BEFORE applying. Board assesses approach, blind spots, sequencing.

---

## 1. Project background (self-contained)

**stop-git-std** is an LLM-driven GitHub repo security auditor. Board-approved architecture (canonical record: `docs/board-review-pipeline-methodology.md`):
- 8/8/4 classification (automatable / structured LLM / prose LLM)
- 9-phase pipeline (tool-exec → validation → compute → structured-LLM → prose-LLM → assembly → render → validator → git-hook)
- Invariants: MD canonical, facts/inference/synthesis separation, `head-sha.txt` first durable artifact, validator is the gate

**Phase 7 renderer plan A→G.** Steps A-F shipped (schema V1.1, Jinja2 renderers for MD + HTML, 3 V1.1 fixtures, validator `--report` + `--parity` clean against back-authored goldens). **Step G is the C7 acceptance matrix** — the first live pipeline run on real scan data.

Step G has been gated behind a 4-item pre-req queue from the prior Step-F + Step-G-kickoff board reviews. **As of HEAD `30da757`, all 4 pre-reqs are cleared.**

---

## 2. State of play

### 2.1 Pre-req queue — all cleared

Source: `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §"Unblocked items disposition".

| Item | Scope | Status | Evidence |
|---|---|---|---|
| U-1 | V2.5-preview doc integration (CLAUDE.md Q3a + Operator Guide §8.8 + Scan-Readme) | ✅ `6a3e471` | §8.8.1–8.8.7 inline in operator guide |
| U-3/FX-4 | Fixture provenance via separate `tests/fixtures/provenance.json` | ✅ `3c09afb` | File present, keyed by filename |
| U-5/PD3 | Bundle/citation validator — enforces facts/inference/synthesis separation in `findings-bundle.md` | ✅ `885bdcf` | `--bundle` mode in validator, 16 tests, 5 V2.4 bundle corpus pass |
| U-10 | Re-validate 10 catalog scans with fixed validator | ✅ `6481533` | Canonical scorecard alignment + Archon verdict consistency, all 13/13 MD+HTML pairs clean |

### 2.2 Current repo state

- **Tests:** 279/279 passing (`python3 -m pytest tests/ -q`)
- **Validator on 3 V1.1 fixtures:** `--report` clean + `--parity` zero errors + zero warnings
- **Parity sweep:** 13/13 MD+HTML pairs clean (10 catalog + zustand-v2 + agency-agents + open-lovable + multica)
- **Repo↔package validator diff:** 0 lines (byte-identical)
- **CSS:** 824 lines
- **Catalog:** 11 V2.4 scans (entry #11: multica-ai/multica @ `b8907dd`, `f5c523e` — first delegated Sonnet 4.6 scan, landed with canonical DOM after the template-is-DOM-contract correction)
- **Template-is-DOM-contract directive:** propagated to `CLAUDE.md` + `docs/board-review-data/path-b-test-prompt.md` + session memory. Future delegated scans cannot silently redesign the DOM.

### 2.3 Reference docs for the board

- `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 (the V2.5-preview operator spec — 7 subsections)
- §8.8.3 phase-to-prompt mapping table + 8-step operator checklist
- §8.8.5 Step G success criterion (6 gates including structural-parity vs V2.4)
- §8.8.6 rollback contract (5 clauses)
- §8.8.7 known limitations pre-Step-G

---

## 3. Owner proposal for Step G execution

### 3.1 Target repos — the 3 fixture shapes

| Shape | V1.1 fixture | V2.4 catalog entry (for structural-parity diff) |
|---|---|---|
| JS library | `tests/fixtures/zustand-form.json` | `docs/GitHub-Scanner-zustand-v3.html` / `.md` (catalog #9, `v2.4`) |
| curl-pipe installer | `tests/fixtures/caveman-form.json` | `docs/GitHub-Scanner-caveman.html` / `.md` (catalog #4, `v2.4`) |
| Agentic platform monorepo | `tests/fixtures/archon-subset-form.json` | `docs/GitHub-Scanner-Archon.html` / `.md` (catalog #2, `v2.4`, rerun record `docs/GitHub-Scanner-Archon-rerun-record.md`) |

**Why these 3:** they are the only shapes with back-authored V1.1 fixtures (§8.8 known limitation). Each has a matched V2.4 catalog scan usable as the structural-parity comparator (§8.8.5 gate #6).

**Why not expand to fd / gstack / postiz-app / hermes-agent shapes:** those fixtures don't exist yet. Fixture authoring for new shapes is post-Step-G work (deferred per `REPO_MAP.md` §2.5). Running Step G against an un-fixtured shape means authoring the fixture and the live form in one pass, collapsing the acceptance test.

### 3.2 Execution mode — continuous (Path A / primary session)

Owner proposal: run Step G in continuous mode (same session as primary agent) rather than delegated. Rationale:
- Delegated Path B just surfaced DOM-drift risk on multica (scan #11); V2.5-preview's deterministic renderer eliminates that risk but introduces a new risk surface (the LLM authoring `form.json` against a 1000+ line schema).
- Continuous mode lets the operator interleave schema validation feedback with form drafting.
- Step G is a VALIDATION run, not a production run. Cost efficiency is secondary to diagnostic density.

### 3.3 Authoring method per §8.8.3 8-step operator checklist

For each of the 3 targets:

1. Fresh `gh api` capture at pinned HEAD SHA (the V2.4 catalog scan SHAs are the anchor — re-scan at those same SHAs for apples-to-apples structural-parity comparison).
2. Phase 1–3 identical to V2.4 (capture + validation + bundle).
3. Run `--bundle` validator on `findings-bundle.md` (U-5/PD3 gate — required per §8.8.7 final bullet).
4. Author `form.json` using `tests/fixtures/zustand-form.json` as the shape template, filling with the bundle's evidence + synthesis (§8.8.3 checklist steps 2–6).
5. Validate form against `docs/scan-schema.json` V1.1 (jsonschema Draft 2020-12, must report zero errors).
6. Render MD + HTML via `docs/render-md.py` + `docs/render-html.py`.
7. Gate: validator `--report` on both + `--parity` zero errors AND zero warnings (§8.8.5 gates 1–3).
8. Determinism test: re-render the same `form.json` twice; `diff` must be empty (§8.8.5 gate 5).
9. Structural-parity diff against the matched V2.4 catalog scan (§8.8.5 gate 6) — findings count, severity distribution, scorecard cells, verdict level, evidence-card count.
10. Write `tests/fixtures/provenance.json` entry for each live form (U-3/FX-4 contract: step-g-live-pipeline tag, not back-authored).

### 3.4 Acceptance — §8.8.5 gates (all 6 required)

1. `form.json` validates clean against V1.1 schema (zero errors).
2. Both rendered outputs pass `--report` (exit 0).
3. `--parity` zero errors AND zero warnings.
4. Evidence refs resolve (no dead `E*` or `EB-*`).
5. Re-rendering same `form.json` produces byte-identical MD + HTML.
6. Structural parity vs V2.4 catalog scan of same repo at same SHA.

**Any single failure = Step G fails for that target.** 3-of-3 required for overall Step G pass.

### 3.5 Rollback contract — §8.8.6 (unchanged from board sign-off)

If Step G fails: V2.4 continues as ONLY production path; §8.8 is quarantined; failed forms tagged in provenance.json as `step-g-failed-artifact`; package untouched; schema revision happens in a separate cycle.

### 3.6 What Step G does NOT do

- Does NOT promote any V2.5-preview scan to the catalog (catalog stays V2.4 only until a separate post-Step-G decision).
- Does NOT refresh `github-scan-package-V2/` (deferred to post-Step-G V2.5 refresh cycle — `REPO_MAP.md` §2.5).
- Does NOT update the CLAUDE.md wizard's Q3a default (V2.4 stays the recommended default until Step G proves V2.5-preview out).
- Does NOT build Phase 4–6 automation (structured-LLM / prose-LLM / assembly remain LLM-in-the-loop per §8.8.7).

---

## 4. Blind spots the board should address

### Q1 — Is 3 targets sufficient, or should we expand/contract?

Owner proposal: 3 targets (the only shapes with V1.1 fixtures). Alternative A: run only 1 target (e.g., zustand) as a spike, then decide whether to continue — cheaper but lower signal. Alternative B: expand to 5 by authoring fd + gstack fixtures concurrently — higher coverage but introduces fixture-authoring as a co-dependent variable. Board: confirm 3, argue for 1-target spike, or argue for 5-target expansion.

### Q2 — Same-SHA rescan vs. fresh HEAD?

Owner proposal: rescan at the V2.4 catalog entry's pinned HEAD SHA for apples-to-apples structural-parity. Alternative: scan at current HEAD (whatever each repo is today) to test that the pipeline handles live data, not replayed data. The Archon rerun record (`docs/GitHub-Scanner-Archon-rerun-record.md`) already establishes determinism across SHA bumps for V2.4. Board: confirm pinned-SHA rescan, or require fresh-HEAD to prove live-data handling.

### Q3 — How does the `form.json` authoring step avoid re-introducing the multica-class authorial drift?

V2.4 multica scan drifted DOM because the LLM invented class names. V2.5-preview has a deterministic renderer — the LLM cannot invent class names since the renderer owns the templates. **But the LLM now has a new surface to drift on: the schema itself.** Pressure-testing needed: what if the LLM produces a schema-valid `form.json` with semantically-wrong data (e.g., wrong severity enum, wrong split-axis, wrong scorecard cell values) that passes jsonschema + validator + parity but fails structural-parity vs V2.4? Is the structural-parity gate (§8.8.5 #6) defined tightly enough to catch this? Board: propose a specific structural-parity checklist (finding count tolerance? severity distribution tolerance? scorecard cell exact-match?).

### Q4 — Bundle validator (`--bundle`) coverage on live bundles

U-5/PD3's `--bundle` mode validated against 5 archived V2.4 bundle corpus files. **The Step G operator will author a fresh bundle for each of the 3 targets.** Is the `--bundle` validator tight enough to catch a live-authored bundle that violates fact/inference/synthesis separation, or does it only pass the corpus because the corpus is clean? Board: recommend a smoke test (deliberately inject a synthesis sentence into an evidence block, confirm `--bundle` flags it) before running Step G live, OR accept the 16-test suite as sufficient.

### Q5 — Parallel or sequential across the 3 targets?

Owner proposal: sequential (zustand → caveman → Archon) so each run informs the next. Alternative: parallel in 3 sub-sessions (delegated agents with shared handoff packets) to stress-test the LLM-authoring surface across 3 simultaneous forms. Board: confirm sequential, or argue for parallel with explicit isolation.

### Q6 — Failure disposition granularity

§8.8.6 rollback is binary (Step G pass or quarantine §8.8). But Step G has 3 targets and 6 gates per target = 18 sub-gates. What if 17/18 pass and 1 fails (e.g., Archon fails structural-parity gate #6 only)? Is that a Step G pass with a follow-up fix ticket, or a Step G fail triggering full quarantine? Owner has not decided. Board: propose a graduated failure-disposition rubric.

### Q7 — Structural-parity comparator confidence

Catalog entries #2 (Archon) and #4 (caveman) predate several validator fixes (Archon: `eabccb8`; caveman: `34cc07b`; both pre-Step-F). Entry #9 (zustand-v3) is the most recent of the 3 (`6481533`). Are all 3 V2.4 comparators trustworthy as the structural-parity anchor, or does one of them have latent drift from the pre-canonical-scorecard era? Owner's U-10 clean-sweep should have caught this; confirm. Board: Pragmatist verify zustand-v3, caveman, Archon catalog entries are all canonical-scorecard-aligned post-U-10.

### Q8 — Catch-all blind spots

Open-ended. Especially welcome from the Skeptic: the failure mode is "operator drafts a schema-valid form.json, renderer emits clean MD+HTML, validator passes, but the finding set silently diverges from what a V2.4 LLM would have produced." How do we detect that? What's the worst thing that could happen post-sign-off if we declare Step G passed?

---

## 5. What R1 must produce

### Verdict
SIGN OFF | SIGN OFF WITH DISSENTS | BLOCK (on the approach + execution plan, not on applied code — this is approach review).

### Direct answers to Q1–Q8
Cite files/lines where relevant. If you disagree with owner's defaults, say so with rationale.

### FIX NOW / DEFER / INFO items
Applied to the proposed approach. FIX NOW on approach = "don't run Step G without addressing X first." DEFER = "address after Step G runs." INFO = note for the record.

### Additional blind spots
Things this brief did not surface but you see.

**Word cap:** 2000 words. Match Step F R1 brief density.

---

## 6. Files to READ

- `/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md` §8.8 (lines 380–468) — the V2.5-preview operator spec
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` — the kickoff review that queued the 4 pre-reqs now cleared
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md` — Step F + Step G readiness context
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` — the 7-step plan A→G the board approved
- `/root/tinkering/stop-git-std/docs/scan-schema.json` — V1.1 schema the `form.json` must validate against
- `/root/tinkering/stop-git-std/tests/fixtures/zustand-form.json` — shape template operators will copy
- `/root/tinkering/stop-git-std/tests/fixtures/provenance.json` — U-3/FX-4 provenance ledger (Step G forms get new entries here)
- `/root/tinkering/stop-git-std/docs/validate-scanner-report.py` — `--bundle` mode (U-5/PD3) for the bundle gate
- `/root/tinkering/stop-git-std/REPO_MAP.md` §2.2–§2.5 — current state, board runbook, pre-req status, deferred ledger
- `/root/tinkering/stop-git-std/AUDIT_TRAIL.md` — checkpoint log if you need to verify HEAD state / revert paths

For the 3 V2.4 structural-parity comparators (skim only — you are not reviewing these, you are confirming they are canonical-scorecard-aligned per Q7):
- `/root/tinkering/stop-git-std/docs/GitHub-Scanner-zustand-v3.{md,html}`
- `/root/tinkering/stop-git-std/docs/GitHub-Scanner-caveman.{md,html}`
- `/root/tinkering/stop-git-std/docs/GitHub-Scanner-Archon.{md,html}`

---

## 7. Ground rules / per-agent framing

- **Pragmatist:** risk is hand-waving "the renderer is deterministic therefore Step G is low-risk." Be precise about what Step G validates that back-authored fixtures did NOT validate. Specifically, pressure-test Q3 and Q4.
- **Systems Thinker:** the operator flow has moved from a 2-phase (bundle → MD → HTML) narrative to a 5-phase (bundle → form.json → compute → render → parity) pipeline with LLM-in-the-loop on 2 of them. The architectural risk is the new LLM-authoring surface on `form.json`. Recommend explicit pressure-test gates. Pressure-test Q5 and Q6.
- **Skeptic:** the failure mode is "schema-valid-but-semantically-wrong `form.json` passes every gate." Find more. Pressure-test Q3, Q4, Q8.

All three: cite specific files/lines, not general impressions. This is approach review — your FIX NOW items steer execution sequencing, not patch committed code.
