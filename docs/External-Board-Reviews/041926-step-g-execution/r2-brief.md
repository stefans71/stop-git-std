# Board Review R2 (Consolidation) — Step G Execution

**Date:** 2026-04-19
**Reviewing:** Owner's revised execution approach for Step G, incorporating R1 feedback. All 3 R1 responses inlined verbatim below. Fix-artifact-first governance: owner authors concrete BEFORE/AFTER amendments; board votes SECOND / ADJUST / REJECT on each.
**Round:** R2 Consolidation — each agent sees all three R1 responses verbatim
**Rounds planned:** R1 Blind done → R2 Consolidation (this) → R3 Confirmation. Escalate to R4 only if R2 splits materially.
**HEAD at review start:** `30da757`
**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`

**STATELESS.** You agents have no memory of R1. This brief is fully self-contained. All R1 content inlined. Read fresh. Do not read the R1 source files separately — everything you need is here.

---

## 1. Project context (self-contained)

**stop-git-std** is an LLM-driven GitHub repo security auditor. Board-approved architecture: 8/8/4 classification (automatable / structured LLM / prose LLM), 9-phase pipeline (tool-exec → validation → compute → structured-LLM → prose-LLM → assembly → render → validator → git-hook). Invariants: MD canonical, facts/inference/synthesis separation, `head-sha.txt` first durable artifact, validator is the gate.

**Phase 7 renderer plan A→G.** Steps A-F shipped (schema V1.1, Jinja2 renderers for MD + HTML, 3 V1.1 fixtures, validator `--report` + `--parity` clean against back-authored goldens). **Step G is the C7 acceptance matrix** — the first live pipeline run on real scan data.

**Pre-req queue** — all 4 items cleared (U-1, U-3/FX-4, U-5/PD3, U-10). Commits: `6a3e471`, `3c09afb`, `885bdcf`, `6481533`.

**Current state:** HEAD `30da757`, 279/279 tests passing, 13/13 parity pairs clean, repo-vs-package validator byte-identical, CSS 824 lines, 11 V2.4 catalog scans.

**Key reference (skim only, R1 already cited):** `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 (lines 380–468) is the V2.5-preview operator spec. Section 8.8.5 defines 6 gates; section 8.8.6 defines binary rollback; section 8.8.3 contains the phase-to-prompt mapping + 8-step operator checklist.

---

## 2. R1 verdict matrix

| Agent | Model | R1 Verdict | Item count |
|---|---|---|---|
| Pragmatist | Claude Sonnet 4.6 | SIGN OFF WITH DISSENTS | 3 FIX NOW · 2 DEFER · 2 INFO · 4 blind spots |
| Systems Thinker | Codex GPT-5 | SIGN OFF WITH DISSENTS | 4 FIX NOW · 1 DEFER · 1 INFO · 2 blind spots |
| Skeptic | DeepSeek V4 | SIGN OFF WITH DISSENTS | 3 FIX NOW · 2 DEFER · 3 INFO · 4 blind spots |

**Unanimous direction:** approach is right. No BLOCK. Convergent concerns center on 4 themes (unanimous) + 2 themes (2/3) + 1 split on failure-disposition granularity.

---

## 3. R1 responses — verbatim, stateless-safe

### 3.1 Pragmatist R1 (Claude Sonnet 4.6) — full text

```
Verdict: SIGN OFF WITH DISSENTS

Q1 — 3 targets is right. Alternative A (1-target spike) leaves open question: does pipeline
    degrade gracefully on shapes with complex finding sets? Caveman has 9 findings + split
    verdict; Archon has open CVEs + split verdict + monorepo topology. 18-gate matrix earns
    "Step G passed." Alternative B (expand to 5 via co-authoring new fixtures) collapses
    acceptance test — no independent comparator.
    Nuance: zustand-form.json provenance is `authored-from-scan-data` (not back-authored-
    from-golden-md like caveman and archon-subset). Structural-parity comparator for zustand
    is V2.4 zustand-v3 MD/HTML, not the fixture.

Q2 — Confirm pinned-SHA rescan. Fresh-HEAD belongs in a post-Step-G "live scan SOP"
    validation. Encode as deferred pre-req.

Q3 — Primary risk surface. Brief's Q3 treatment incomplete.
    What jsonschema catches: wrong type, missing required, enum violations.
    What jsonschema does NOT catch: correct-enum-wrong-value semantic errors:
      - severity: "Warning" when V2.4 scored "Critical" (valid enum, wrong judgment)
      - phase_3_computed.c20_severity.result: "Warning" when compute.py would produce
        "Critical" (compute.py must run, not be "mirrored")
      - scorecard cell color: "amber" when V2.4 produced "red"
      - phase_4b_computed manual authored vs computed
    Gate #6 as written is a vibe check. No defined tolerance bounds.
    FIX NOW: define 5-item checklist:
      1. Finding count exact match
      2. Severity per F-ID exact match
      3. Scorecard cell colors exact match (all 4)
      4. Verdict level exact match
      5. Evidence ref count ±10%
    Secondary risk — phase_3_computed manual compute: §8.8.3 step 4 says "mirror their
    logic" acceptable. NOT acceptable for Step G. FIX NOW: execution must invoke
    `python3 docs/compute.py` directly.

Q4 — 16-test synthetic coverage + 5 V2.4 bundle corpus is good base.
    Not tested: bundle where synthesis sentence is embedded in section heading parser
    classifies as evidence. The heading-based classification (parse_bundle_regions lines
    655-679) uses keyword matching.
    Accept smoke test as sufficient. Must run BEFORE first Step G bundle.
    ADDITIONAL smoke test: confirm section titled `## FINDINGS SUMMARY` containing zero
    F-IDs but valid prose PASSES (compact-bundle style used in zustand-v3 — check_bundle
    line 748 prints "(no F-IDs parsed)" but does not error).

Q5 — Confirm sequential (zustand → caveman → Archon). Order: zustand (template), caveman
    (complexity: 9 findings, split verdict, shell-globs), Archon (highest: monorepo, CVEs,
    subset/full scope mismatch).

Q6 — DISSENT from binary rollback. Propose graduated rubric:
    | Failure type                           | Disposition                           |
    | Validator gate (1–3) fails on any tgt | Full rollback — §8.8 quarantined     |
    | Evidence refs dead (gate 4)            | Target-local; one retry allowed       |
    | Determinism (gate 5) fails             | Full rollback — renderer bug          |
    | Struct-parity (gate 6) fails 1 of 3    | Target fails, tracked ticket, NOT     |
    |                                        | rollback. 2-of-3 clear = partial pass |
    | Struct-parity fails 2+ of 3            | Full rollback                         |
    Key insight: gates 1–5 = pipeline correctness. Gate 6 = LLM authoring quality.
    A pipeline-correct run with one authoring miss is recoverable without quarantine.

Q7 — Verified. zustand-v3 scorecard lines 29-34 canonical 4-question bullet format; caveman
    lines 71-78 canonical 4-question TABLE format; Archon lines 71-78 canonical 4-question
    TABLE format with emoji (🚨/⚠/✅). All canonical-scorecard-aligned post-U-10. Bullet
    vs table is V2.4 rendering variation, not drift. Safe anchors.

Q8 — See blind spots below.

FIX NOW / DEFER / INFO:

| ID   | Priority  | Item                                                                  |
|------|-----------|-----------------------------------------------------------------------|
| FN-1 | FIX NOW   | Structural-parity 5-item checklist with pass/fail bounds              |
| FN-2 | FIX NOW   | Phase 3 manual compute must use `python3 docs/compute.py`, not mirror |
| FN-3 | FIX NOW   | Bundle smoke test (synthesis verb injection) BEFORE first live bundle |
| D-1  | DEFER     | Fresh-HEAD live scan validation (V2.5 production pre-req)             |
| D-2  | DEFER     | Phase 3 automated pipeline harness (compute.py from Phase 1 auto)     |
| I-1  | INFO      | provenance.json `ordering_constraints` — must be read pre-authoring   |
| I-2  | INFO      | archon-subset covers 4 of 11 Archon findings; subset scope boundary   |

Additional blind spots:
  1. archon-subset scope mismatch is gate-6 landmine. archon-subset-form.json = SUBSET
     (4 of 11 findings). Gate #6 compares live V2.5-preview against V2.4 catalog scan
     (`docs/GitHub-Scanner-Archon.md`), NOT subset fixture. Without clarification, operator
     will get false mismatch.
  2. phase_4b_computed is a derived field that must be computed, not authored. If operator
     authors it manually, schema-valid-but-wrong verdict level reaches renderer.
  3. §8.8.3 checklist step 3 says "run --bundle on findings-bundle.md", step 4 says "author
     form.json from bundle." No explicit gate that bundle must be COMPLETE before form
     authoring begins. Operator could draft form.json mid-bundle, introducing inconsistency.
  4. zustand-v3.md (comparator) was a re-scan of V2.3 zustand. V2.4 zustand-v3 scorecard
     shows "formal-review rate" = Amber, but fixture `zustand-form.json` has
     `formal_review_rate: 29` (29%) while V2.4 MD says "45% formal-review rate." Known
     fixture/golden discrepancy from enrichment using different PR sample. Step G structural
     parity check must target V2.4 MD/HTML, not fixture.

Bottom line: approach correct. FN-1 + FN-2 + FN-3 are execution-sequencing gates.
Address before first target. Blind spot #1 (archon-subset vs full catalog) needs
sentence in execution record.
```

### 3.2 Codex R1 (GPT-5) — full text

```
Verdict: SIGN OFF WITH DISSENTS

The overall Step G shape is right: keep scope to the 3 fixtured shapes, use pinned-SHA
replays for parity, and do not parallelize the first live JSON-first run. But do NOT
execute as currently written without two execution-time additions: pre-render semantic
gate on form.json, and graduated failure rubric. Current contract proves renderer
determinism and MD/HTML parity; does not yet adequately prove bundle→form.json semantic
fidelity. Schema is permissive inside Phases 3–5; guide currently allows operators to
"mirror" compute logic manually, which reintroduces authorial drift into an allegedly
deterministic phase (SCANNER-OPERATOR-GUIDE.md:427-433, scan-schema.json:1031-1121,
scan-schema.json:1123-1368).

Q1 — 3 total is correct, but execution shape should be 1 + 2 sequential, not "all 3 in
     one uninterrupted continuous sweep." Only 3 shapes are fixtured for V1.1
     (SCANNER-OPERATOR-GUIDE.md:382-387). Expanding to 5 mixes fixture authoring with
     acceptance. Contracting to 1 loses cross-shape signal. Run zustand first as pilot,
     hold stop/go review, then run caveman and Archon.

Q2 — Use V2.4 catalog SHAs, not fresh HEAD. Step G's success criterion is structural
     parity against existing scan of same repo, so same-SHA replay is clean isolation
     boundary (SCANNER-OPERATOR-GUIDE.md:444-450). Archon rerun record has partially
     de-risked live-data handling: SHA drift changed counts and tables, but not
     structural finding set or verdict shape (GitHub-Scanner-Archon-rerun-record.md:62-78).

Q3 — Current plan does NOT yet close multica-class drift risk; only relocates from DOM to
     schema semantics. form.json can be schema-valid while omitting or mis-stating key
     semantics because most internals of phase_3_computed, phase_4_structured_llm,
     phase_5_prose_llm are optional (scan-schema.json:1031-1121, 1123-1368).
     Add pre-render semantic checklist per target:
       - Finding inventory exact-match
       - Severity exact-match
       - Scorecard exact-match (all 4 cells and colors)
       - Verdict exact-match (phase_4b_computed.verdict.level derivable from findings)
       - Split-axis exact-match (deployment vs version)
       - Evidence linkage exact-match (every non-OK finding has evidence_refs, every ref
         resolves) (scan-schema.json:515-541, SCANNER-OPERATOR-GUIDE.md:444-450).

Q4 — Run one adversarial smoke test on --bundle before Step G. Validator checks right
     classes of mistakes, but evidence so far is "16 tests + 5 clean corpus bundles,"
     and implementation still lets warning-only outcomes pass with exit 0
     (AUDIT_TRAIL.md:75-89, validate-scanner-report.py:682-798, 837-848). Inject one
     synthesis verb into an evidence block and one orphan F-ID into synthesis; confirm
     both hard-fail.

Q5 — Do NOT parallelize. New failure surface is bundle→form.json; sequential gives
     information reuse without contaminating diagnosis space. Parallel runs would tell
     you "three operators drafted three different forms" but not whether prompt, schema,
     manual compute, or semantic checklist is actual problem. Especially true because
     Step G keeps Phases 4–6 LLM-in-the-loop (SCANNER-OPERATOR-GUIDE.md:464-466).
     Sequential, same operator, hard checkpoint after target 1.

Q6 — 17/18 is NOT a Step G pass. Step G is acceptance gate for "pipeline reliable" claim;
     guide defines pass as all gates on all targets (SCANNER-OPERATOR-GUIDE.md:444-450,
     041826-renderer-alignment/CONSOLIDATION.md:48-56). Failure disposition should be
     graduated:
       - Isolated target failure: overall Step G = fail, failed artifact tagged
         step-g-failed-artifact, other targets retained as evidence, NO full quarantine
         yet.
       - Repeated target failure on same gate, or any defect in compute/schema/validator
         contract: Step G = fail and §8.8 quarantined per rollback.
       - Comparator or rubric ambiguity discovered mid-run: halt immediately; no pass/fail
         claim until rubric fixed.
     Full quarantine reserved for SYSTEMIC defects, not single localized miss.

Q7 — 3 V2.4 comparators trustworthy enough. U-10 revalidated catalog against fixed
     validator and re-canonicalized scorecards/verdicts (REPO_MAP.md:167-176,
     AUDIT_TRAIL.md:105-124). All 3 MD/HTML pairs show canonical 4 scorecard questions
     and aligned verdict banners/headers.

Q8 — Biggest remaining blind spot: guide still permits "invoke docs/compute.py functions
     on Phase 1 data (or mirror their logic)" (SCANNER-OPERATOR-GUIDE.md:427-433). For
     Step G, "mirror their logic" should be disallowed. Deterministic phase cannot be
     hand-reimplemented during acceptance. Require direct compute execution and preserve
     emitted values as artifacts.
     Second blind spot: source packet state-inconsistent. Brief says review-start HEAD
     30da757, while REPO_MAP.md and top AUDIT_TRAIL.md checkpoint still point to earlier
     audit heads (r1-brief.md:7, REPO_MAP.md:3-4, REPO_MAP.md:83, AUDIT_TRAIL.md:20-23).
     Not blocker, but Step G packet should include actual git HEAD in artifact manifest.

FIX NOW / DEFER / INFO:
| ID   | Sev    | Item                                                                 |
|------|--------|----------------------------------------------------------------------|
| FN-1 | High   | Remove "or mirror their logic"; require direct compute.py execution  |
| FN-2 | High   | Add pre-render semantic gate (6-point exact-match checklist)         |
| FN-3 | High   | Predeclare failure rubric before first run (isolated vs systemic)    |
| FN-4 | Med    | Adversarial --bundle smoke test (synthesis verb + orphan F-ID)       |
| D-1  | Med    | Schema hardening (Scanner Integrity + methodology gaps logged)       |
| I-1  | Low    | Provenance discipline — keep tagging live Step G forms               |

Additional blind spots:
  - --parity and --bundle both return 0 when warnings exist. Execution must inspect
    warning count explicitly, not just exit code (validate-scanner-report.py:832-848,
    864-870).
  - zustand-form.json tagged `authored-from-scan-data`, not `pipeline-produced`. Using
    it as template is fine; using similarity to it as evidence of pipeline correctness
    is not (provenance.json:12-21).

Architectural recommendation:
  Architecture wants 3-target sequential, but CHECKPOINTED — not "3-target sequential
  continuous" as single uninterrupted flow, and not parallel. Run target 1, execute
  semantic checklist, decide whether failures are operator-local or systemic, then
  continue. If target 1 passes cleanly, targets 2 and 3 can stay in same session. If
  target 1 fails semantically, stop and fix contract before spending other two targets.
```

### 3.3 DeepSeek R1 (V4) — full text

```
Verdict: SIGN OFF WITH DISSENTS

Step G execution approach is fundamentally sound but contains critical blind spots in
schema drift detection, bundle validator coverage, and failure mode analysis. The
3-target, same-SHA, sequential approach is appropriate, but requires additional
safeguards.

Q1 — Yes, 3 targets sufficient ONLY IF structural-parity gate #6 is rigorously defined.
     3 shapes represent distinct architectural patterns. Expanding to 5 requires fixture
     authoring (co-dependency). Contracting to 1 loses cross-shape signal.
     DISSENT: "only shapes with V1.1 fixtures" limitation creates coverage gap Step G
     cannot detect. If schema has shape-specific gaps (e.g., missing fields for CLI
     binary shape), Step G passes but future shapes fail.

Q2 — Same-SHA rescan correct. Fresh HEAD introduces uncontrolled variables (repo changes).
     Archon rerun record (GitHub-Scanner-Archon-rerun-record.md) proves determinism
     across SHA bumps. Confirm pinned-SHA rescan.

Q3 — It doesn't. Schema itself is new drift surface. Schema-valid but semantically-wrong
     form.json could pass all gates. Example: LLM sets severity: "Info" instead of
     "Warning" for finding V2.4 marked Warning. Schema validation passes, validator
     passes, structural-parity gate #6 must catch this. Problem: §8.8.5 gate #6 is
     undefined — "structural parity" lacks tolerance thresholds. Need explicit checklist:
     finding count exact match (±0), severity distribution exact match, scorecard cell
     exact match, evidence-card count exact match.

Q4 — Insufficient. --bundle validator tested against 5 archived V2.4 bundles (these were
     already clean). FIX NOW: Before Step G runs, inject deliberate violations into test
     bundle and verify --bundle catches them. Specifically: synthesis sentence in evidence
     block, orphan F-ID reference, missing FINDINGS SUMMARY. The 16-test suite may only
     test positive cases.

Q5 — Sequential correct for diagnostic learning. However, sequential creates ordering
     dependency: if zustand fails, caveman + Archon may not run, losing signal.
     Recommendation: sequential with explicit checkpoint after each target.

Q6 — Binary quarantine too coarse. If 17/18 sub-gates pass and 1 fails, that's Step G
     partial failure requiring targeted fix, not full quarantine.
     Proposed rubric:
       - Full pass: all 3 targets pass all 6 gates.
       - Partial pass: ≥2 targets pass all gates, ≤1 target has isolated failure
         (document as known limitation).
       - Full fail: ≥2 targets fail any gate, OR any target fails validator/parity gates
         (1-3).

Q7 — All 3 V2.4 comparators canonical-scorecard-aligned post-U-10 (6481533). However,
     caveman and Archon predate validator fixes. U-10 clean-sweep should have caught
     latent drift, but VERIFY: Run --parity on each V2.4 comparator's MD+HTML pair to
     confirm zero warnings. If warnings exist, comparator is contaminated.

Q8 — Worst failure mode is SEMANTIC INVERSION WITH SCHEMA COMPLIANCE. Example: LLM
     authors form.json where all finding severities systematically one level lower than
     V2.4 (Critical→Warning, Warning→Info). Schema passes (enum valid). Validator passes
     (structure intact). Parity passes (findings present). Structural-parity gate #6
     must detect severity distribution mismatch. Missing: automated severity distribution
     comparison.

FIX NOW / DEFER / INFO:

FIX NOW:
  FN-1: Define structural-parity tolerance thresholds — zero tolerance for: finding
        count, severity distribution, scorecard cell values, evidence-card count.
  FN-2: Smoke-test bundle validator with deliberate violations — synthesis in evidence,
        missing FINDINGS SUMMARY, orphan F-IDs.
  FN-3: Verify V2.4 comparator parity cleanliness — run --parity on all 3 comparator
        MD+HTML pairs; any warnings = contaminated anchor.

DEFER:
  DF-1: Schema hardening for missing shapes — CLI binary (fd), Claude Code skills
        (gstack), web app (postiz-app), Python platform (hermes-agent) lack fixtures.
        Post-Step-G work.
  DF-2: Automated severity distribution comparison script. Catches semantic inversion
        failure mode.

INFO:
  IF-1: Continuous mode diagnostic advantage — owner rationale correct.
  IF-2: Provenance tagging — entries must be created BEFORE Step G forms authored,
        not retroactively.
  IF-3: Rollback contract clarity — §8.8.6 binary; partial failure rubric should be added.

Additional blind spots:
  4.1 Evidence reference integrity gap — validator checks dead E*/EB-* references (gate
      4) but does NOT verify evidence cards referenced in findings actually exist in
      phase_4_structured_llm.evidence.entries[]. Finding could reference E-42 but
      evidence.entries only goes to E-41. Schema passes (string type). Detection gap.
  4.2 Scorecard cell value drift — phase_3_computed.scorecard.cells[].value uses
      scorecard_color enum. LLM could invert values (red→green) while maintaining
      schema validity. Missing: automated cell-value comparison.
  4.3 Phase boundary contamination — schema separates facts (Phase 1), inference (Phase
      4), synthesis (Phase 5). LLM could place synthesis content in Phase 4 fields
      (e.g., what_this_means prose in phase_4_structured_llm.action_steps). Schema
      passes (string type). Validator cannot detect semantic phase violation.
  4.4 Determinism test incompleteness — gate #5 tests re-rendering same form.json
      produces byte-identical output. Does NOT test same gh api capture → same
      form.json. Two pipeline runs on same SHA could produce different form.json (LLM
      non-determinism) yet each passes determinism test. False confidence.

Worst-case walkthrough — Systematic severity downgrade:
  1. Operator runs pipeline on zustand at pinned SHA.
  2. LLM produces form.json with all finding severities downgraded (Critical→Warning,
     Warning→Info, Info→OK). Schema validation passes (enum values valid).
  3. render-md.py + render-html.py produce MD+HTML with downgraded severities.
  4. Gate #1 form.json validates clean ✓. Gate #2 --report passes ✓. Gate #3 --parity
     zero errors/warnings (findings present) ✓. Gate #4 evidence refs resolve ✓.
     Gate #5 re-render determinism ✓.
  5. Structural-parity gate #6: manual comparison. If checklist vague, operator may
     miss severity distribution mismatch. Finding count matches, evidence cards match,
     but risk assessment is wrong.
  6. Result: Step G passes, V2.5-preview declared validated, but produces systematically
     less-severe scans than V2.4.
Mitigation: gate #6 must include "For each finding in V2.4 scan, there must be a
finding in V2.5-preview scan with same F-ID and same severity. Tolerance: zero
mismatches."
```

---

## 4. Convergence analysis — R1 → R2

### 4.1 Unanimous FIX NOW (3/3)

| Theme | Pragmatist | Codex | DeepSeek |
|---|---|---|---|
| Structural-parity gate #6 needs zero-tolerance checklist | FN-1 | FN-2 | FN-1 |
| Bundle validator adversarial smoke test before first live bundle | FN-3 | FN-4 | FN-2 |
| Graduated failure disposition rubric (replace binary rollback) | Q6 dissent | FN-3 | IF-3 + Q6 |

### 4.2 2/3 FIX NOW

| Theme | Raising agents | Dissenting/silent |
|---|---|---|
| Mandatory `python3 docs/compute.py`, remove "mirror logic" | Pragmatist FN-2, Codex FN-1 | DeepSeek implicit via worst-case walkthrough |
| V2.4 comparator `--parity` cleanliness pre-flight | Codex implicit, DeepSeek FN-3 | Pragmatist verified Q7 via scorecard read |

### 4.3 Unique items worth adopting

| Item | Source |
|---|---|
| Pilot-and-checkpoint execution (zustand, checkpoint, then caveman+Archon) | Codex Q5 + architectural rec |
| `--parity`/`--bundle` return 0 on warnings — parse output, not exit code | Codex Q8 blind spot #1 |
| Compact-bundle `## FINDINGS SUMMARY` with 0 F-IDs secondary smoke test | Pragmatist Q4 |
| Bundle-complete-before-form-authoring sequencing gate | Pragmatist blind spot #3 |
| archon-subset vs full-catalog comparator landmine | Pragmatist blind spot #1, DeepSeek 4.1 |
| Phase boundary contamination (synthesis prose in Phase 4 fields) | DeepSeek 4.3 |
| LLM non-determinism (same input, different form.json) | DeepSeek 4.4 |

### 4.4 Split — graduated failure rubric

- **Pragmatist:** gates 1–5 anywhere = full rollback. Gate 6 on 1-of-3 = partial pass, tracked ticket.
- **Codex strictest:** any isolated target failure = overall Step G fail + tagged artifact, but NO full quarantine. Reserve quarantine for systemic defects. Rubric ambiguity mid-run = halt immediately.
- **DeepSeek:** Full pass (3/3 all gates) · Partial pass (≥2 targets all gates + ≤1 isolated) · Full fail (≥2 targets fail any gate OR any validator/parity gate fails).

Owner-proposed reconciliation in FN-4 below; board votes.

---

## 5. Owner-authored fix artifacts (FN-1 through FN-9)

Vote one of **SECOND / ADJUST / REJECT** on each. If ADJUST, quote the textual change.

### FN-1 — Structural-parity checklist with explicit zero-tolerance bounds

**BEFORE** (R1 brief §3.3 step 9):
> 9. Structural-parity diff against the matched V2.4 catalog scan (§8.8.5 gate 6) — findings count, severity distribution, scorecard cells, verdict level, evidence-card count.

**AFTER:**
> 9. **Structural-parity gate #6 — explicit zero-tolerance checklist.** For each target, compare V2.5-preview rendered MD against the V2.4 catalog comparator MD at the same SHA. ALL of the following must be exact match; any mismatch = gate-6 failure for that target:
>
> 9.1 **Finding inventory** — every F-ID in V2.4 comparator maps to exactly one entry in `phase_4_structured_llm.findings.entries[]`. No extras. No missing.
> 9.2 **Severity per F-ID** — each F-ID's `severity` matches V2.4 comparator's severity for the same F-ID. Zero inversions, zero downgrades, zero upgrades. (Closes DeepSeek worst-case.)
> 9.3 **Scorecard cells** — all 4 canonical questions present + all 4 cell colors match V2.4 comparator cell-by-cell (red/amber/green). (Closes DeepSeek 4.2.)
> 9.4 **Verdict level** — `phase_4b_computed.verdict.level` (Critical / Caution / Clean) matches V2.4 comparator's verdict level.
> 9.5 **Split-axis** — if comparator is a split verdict, `phase_4_structured_llm.verdict_split.axis` must match (`deployment` vs `version`, etc.). If comparator is not split, V2.5-preview must not be split.
> 9.6 **Evidence linkage** — every non-OK finding has non-empty `evidence_refs`; every ref resolves to a declared entry in `phase_4_structured_llm.evidence.entries[]`. No dead refs. No unreferenced evidence cards. (Closes DeepSeek 4.1.)
>
> **Archon-specific clarification:** The comparator for Archon is `docs/GitHub-Scanner-Archon.md` (full 11 findings), NOT `tests/fixtures/archon-subset-form.json` (4 findings, renderer-validation scope). Gate #6 for Archon must produce 11 findings matching the full catalog scan. (Closes Pragmatist blind spot #1.)
>
> **Evidence-card count:** NOT a gate. V2.4 catalogs use varying depth (zustand-v3 bullets, caveman + Archon tables). Card count informational only. (Supersedes Pragmatist FN-1 ±10% line: exact linkage beats count tolerance.)

Proposes resolution for: Pragmatist FN-1, Codex FN-2, DeepSeek FN-1, Pragmatist blind spots #1+#2, DeepSeek 4.1–4.2, DeepSeek worst-case walkthrough.

**Pragmatist-specific question:** Your FN-1 allowed evidence ref count ±10%. AFTER drops to exact linkage + informational count. Does this reconcile with your original intent, or do you want the ±10% carried back in?

---

### FN-2 — Mandatory `compute.py` execution (remove "mirror their logic")

**BEFORE** (R1 brief §3.3 step 1, referencing §8.8.3 step 4):
> 3b (not currently in brief) — Phase 3 computed fields manually authored or compute.py mirrored.

**AFTER:** Add to §3.3 execution checklist as new step 3b:
> 3b. **Phase 3 computed fields — MUST invoke `python3 docs/compute.py` directly.** "Mirror the logic manually" is disallowed for Step G. Required invocations per the 8 automatable operations (verdict, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised). Capture emitted values as artifacts at `.board-review-temp/step-g-execution/compute-output-<target>.json` for audit. `phase_3_computed.*` and `phase_4b_computed.verdict.level` in the live `form.json` MUST equal these emitted values byte-for-byte. (Closes Pragmatist blind spot #2: phase_4b_computed must be computed, not authored.)

**Also amend `docs/SCANNER-OPERATOR-GUIDE.md` §8.8.3 step 4** (permanent doc change post-Step-G): replace "or mirror their logic" with "MUST invoke; mirroring manually is disallowed for V2.5-preview scans."

Proposes resolution for: Pragmatist FN-2, Codex FN-1, DeepSeek worst-case walkthrough mitigation.

---

### FN-3 — Adversarial bundle smoke test before first live bundle

**BEFORE** (not in R1 brief):
> (no smoke-test gate in execution sequence)

**AFTER:** Add to §3.3 execution checklist as new step 0:
> 0. **Pre-flight: bundle validator adversarial smoke test.** Before authoring any live bundle, author 4 synthetic bundles (each mutates a clean corpus bundle) and verify `--bundle` behavior:
> 0.1 Inject synthesis verb ("suggests", "indicates", "plausibly") into an evidence block under `## Evidence`. Expected: **exit 1** + flags interpretive-verb-in-evidence.
> 0.2 Inject an orphan F-ID (`F99`) into `## Pattern recognition` that is never declared in `## Findings summary`. Expected: **exit 1** + flags orphan-F-ID.
> 0.3 Delete the `## FINDINGS SUMMARY` section entirely. Expected: **exit 1** + flags missing-required-section.
> 0.4 **Compact-bundle baseline** (Pragmatist Q4 secondary): bundle has `## FINDINGS SUMMARY` containing ZERO F-IDs but valid prose (the zustand-v3 compact style). Expected: **exit 0** with informational note, NOT a failure. Confirms validator distinguishes empty-but-valid from missing.
>
> Each failure-case smoke must hard-fail with nonzero exit AND a specific message. Compact-bundle case must pass. If any test behaves unexpectedly, STOP — bundle validator is not acceptance-ready.

Proposes resolution for: Pragmatist FN-3, Codex FN-4, DeepSeek FN-2, Pragmatist Q4 secondary.

---

### FN-4 — Graduated failure disposition rubric

**BEFORE** (R1 brief §3.5 + §8.8.6 binary rollback):
> If Step G fails: V2.4 continues as ONLY production path; §8.8 is quarantined; failed forms tagged as `step-g-failed-artifact`; package untouched.

**AFTER** (consolidates 3 agent proposals; see §4.4 split above):

| Failure pattern | Disposition |
|---|---|
| Validator gates 1–3 fail on ANY target | **Full rollback** — §8.8 quarantined, failed forms tagged, V2.4 remains only production path. (Pipeline-correctness failure.) |
| Determinism gate 5 fails on ANY target | **Full rollback** — indicates renderer bug in `render-md.py`/`render-html.py`. (Pipeline-correctness failure.) |
| Evidence refs gate 4 fails on 1 target | **Target-local authoring error.** One retry for that target (re-author affected findings). If retry fails → target fails Step G; proceed to other targets; graduate per gate-6 rules. |
| Gate 6 (structural parity) fails on 1 of 3 targets, others clean | **Step G partial pass.** Failing shape tagged `step-g-failed-artifact` in `provenance.json`; issue a tracked remediation ticket; V2.5-preview cleared for the 2 passing shapes only. NO full quarantine. |
| Gate 6 fails on 2+ of 3 targets | **Full rollback** — authoring-quality failure at scale indicates schema or rubric-level defect. |
| ANY gate fails ambiguously (e.g., rubric interpretation dispute mid-run) | **HALT immediately.** Do not claim pass/fail. Escalate to board mini-review before continuing. (Codex FN-3 principle.) |
| Schema-validation failure (form.json invalid against V1.1) | **Target-local authoring error** — one retry; behaves like evidence-refs gate 4 |

**Key principles:**
- Gates 1–3, 5 = **pipeline correctness** → full rollback on any failure.
- Gate 4 + schema validation = **authoring error, target-local, retryable**.
- Gate 6 = **authoring quality, graded** — isolated miss = partial pass, scaled miss = systemic.
- Ambiguity = halt, not pass.

Proposes resolution for: Pragmatist Q6 dissent, Codex FN-3, DeepSeek IF-3 + Q6. Reconciles the §4.4 split.

**Codex-specific question:** You argued strictest ("17/18 NOT a pass"). AFTER splits the difference: gate 6 single-target fail = partial pass (Pragmatist+DeepSeek); gates 1–3 + 5 single-target fail = full rollback (closer to your strictness). SECOND / ADJUST / REJECT?

---

### FN-5 — Explicit warning-count inspection, not exit-code reliance

**BEFORE** (R1 brief §3.3 step 7):
> 7. Gate: validator `--report` on both + `--parity` zero errors AND zero warnings.

**AFTER:**
> 7. **Validator gates — parse output, don't trust exit code alone.** `--parity` and `--bundle` modes both return exit 0 when warnings exist (see `docs/validate-scanner-report.py` lines 832–848, 864–870). Gate check for each target:
> 7.1 `validate-scanner-report.py --report <.html>` → exit 0 required.
> 7.2 `validate-scanner-report.py --markdown <.md>` → exit 0 required.
> 7.3 `validate-scanner-report.py --parity <.md> <.html>` → exit 0 **AND** stdout contains literal `"Parity check clean"` **AND** stdout does NOT contain any `WARNING:` lines. Grep: `grep -c '^WARNING:' <parity-output>` must equal `0`.
> 7.4 `validate-scanner-report.py --bundle <findings-bundle.md>` → exit 0 **AND** zero `WARNING:` lines in stdout.

Proposes resolution for: Codex Q8 blind spot #1.

---

### FN-6 — Pre-flight V2.4 comparator `--parity` cleanliness

**BEFORE** (not in R1 brief):
> (no pre-flight check on V2.4 comparators)

**AFTER:** Add to §3.3 execution checklist as new pre-flight step -1 (before step 0):
> -1. **Pre-flight: comparator cleanliness check.** Run `validate-scanner-report.py --parity <V2.4.md> <V2.4.html>` on each of the 3 comparator pairs (zustand-v3, caveman, Archon). Each must report exit 0 AND zero `WARNING:` lines per FN-5 inspection. If any comparator reports warnings, STOP — the anchor is contaminated; re-scan or document as "comparator-tainted, Step G-deferred for this shape" before proceeding.

Expected result given 2.2 state (13/13 parity pairs clean post-U-10): all 3 pre-flights pass cleanly. Belt-and-suspenders check.

Proposes resolution for: Codex Q8 implicit, DeepSeek FN-3.

---

### FN-7 — Pilot-and-checkpoint execution structure

**BEFORE** (R1 brief §3.2):
> Execution mode — continuous (Path A / primary session). Sequential zustand → caveman → Archon.

**AFTER:** Add to §3.2:
> **Execution ordering: pilot + 2.** Run zustand end-to-end through all 6 gates (including adversarial smoke test, compute.py capture, form.json authoring, render, all gates 1–6). **HARD CHECKPOINT before continuing to caveman or Archon.**
>
> Checkpoint criteria:
> - Zustand passes all 6 gates cleanly → continue to caveman, then Archon sequentially in the same session.
> - Zustand fails on gates 1–3 or 5 (pipeline correctness) → STOP; do NOT spend caveman + Archon on a broken pipeline; trigger rollback per FN-4.
> - Zustand fails on gate 4 or 6 (authoring) → one retry on zustand; if retry passes, continue to caveman + Archon. If retry fails on gate 6, assess whether the failure is shape-specific (continue, accept 2-of-3 partial pass on zustand-less set) or rubric-level (halt).
>
> Rationale: parallel runs would confound the diagnosis space; continuous-uninterrupted could waste caveman + Archon targets if zustand reveals a systemic defect.

Proposes resolution for: Codex Q5 + architectural recommendation, DeepSeek Q5 nuance.

---

### FN-8 — Phase boundary contamination check + LLM non-determinism as deferred

**BEFORE** (not in R1 brief):
> (no explicit safeguard against prose-in-structured-field; no statement on LLM re-authoring determinism)

**AFTER:** Add to §3.3 execution checklist as new step 6b (between render and gate checks):
> 6b. **Phase-boundary spot check.** For each form.json: confirm `phase_4_structured_llm.findings.entries[].*` structured fields (severity, evidence_refs, action_steps) contain ONLY enum values / F-ID refs / short phrases. Prose paragraphs (>40 words, narrative sentences) must live in `phase_5_prose_llm.*`. Manual visual check on first target (zustand); if clean, subsequent targets get same check. (Closes DeepSeek 4.3.)
>
> 6c. **Authoring-determinism is NOT a Step G gate.** Step G does NOT require that the same bundle produce byte-identical `form.json` across re-authoring attempts by the same or different LLM. This is a deferred property — tracked as D-3 in §6 below. Gate #5 only tests render-determinism given a fixed `form.json`. (Documents DeepSeek 4.4 as deferred, not open.)

Proposes resolution for: DeepSeek 4.3 as new gate; DeepSeek 4.4 as documented deferred property.

---

### FN-9 — Bundle-complete-before-form-authoring sequencing gate

**BEFORE** (not in R1 brief; §8.8.3 checklist step 3 = run `--bundle`, step 4 = author form.json):
> (no explicit gate that bundle must be COMPLETE + validator-clean before form.json authoring begins)

**AFTER:** Add to §3.3 execution checklist as new step 3c (between 3b compute.py and step 4 form authoring):
> 3c. **Bundle-complete gate.** Before beginning `form.json` authoring, confirm ALL of:
> 3c.1 `findings-bundle.md` contains all 6 required sections (`## Scan metadata`, `## Evidence`, `## Pattern recognition`, `## FINDINGS SUMMARY`, `## Verdict`, `## Scorecard`).
> 3c.2 `validate-scanner-report.py --bundle <findings-bundle.md>` returns exit 0 + zero `WARNING:` lines.
> 3c.3 Bundle file is saved + committed to `docs/board-review-data/scan-bundles/<repo>-<sha>.md` (per §12 durability rule).
>
> Only after 3c.1–3c.3 succeed may form.json authoring begin. No mid-bundle drafting of form.json. (Closes Pragmatist blind spot #3.)

Proposes resolution for: Pragmatist blind spot #3.

---

## 6. R1 item carry-forward — DEFER / INFO / blind spot dispositions

Every R1 item NOT elevated to FN-1 through FN-9 needs an explicit disposition. Vote **CONFIRM** (adopt as documented) / **ELEVATE** (upgrade to FIX NOW) / **DROP** (not a concern) / **ADJUST** (with textual amendment) per row.

| # | Source | Item | Owner-proposed disposition |
|---|---|---|---|
| D-1 | Pragmatist | **Fresh-HEAD live scan validation** — required before V2.5-preview production use on repos without prior V2.4 catalog entries. | **DEFER** — post-Step-G pre-req for V2.5 production promotion. Add to `REPO_MAP.md` §2.5 deferred ledger under new D-3 slot. |
| D-2 | Pragmatist | **Phase 3 automated pipeline harness** — auto-invoke `compute.py` from Phase 1 data (not operator-manual). | **DEFER** — future-cycle automation; §8.8.7 already documents "Phases 4-6 automation not built." No change in Step G. |
| D-3 | NEW (FN-8) | **LLM non-determinism on form.json re-authoring** — same bundle, different LLM or different session could produce different schema-valid form.json. | **DEFER** — not a Step G gate. Document in §6c of FN-8. Post-Step-G investigation item. |
| D-4 | Codex + DeepSeek | **Schema hardening** — `scan-schema.json` V1.1 doesn't fully formalize the prompt output spec. Gaps: Scanner Integrity §00 hit-level structure; Section 08 methodology beyond version marker. | **DEFER** — already on ledger per Codex R2 add (Step-G-kickoff CONSOLIDATION). Active watch item during Step G; upgrade if Step G surfaces concrete schema pain. No action pre-execution. |
| D-5 | DeepSeek DF-1 | **Schema hardening for missing shapes** — CLI binary (fd), Claude Code skills (gstack), web app (postiz-app), Python platform (hermes-agent) lack V1.1 fixtures. | **DEFER** — already documented in §8.8.7 known limitations. Post-Step-G fixture-authoring cycle. |
| D-6 | DeepSeek DF-2 | **Automated severity distribution comparison script** — mechanical check that V2.5-preview severities match V2.4 comparator. | **DEFER** — FN-1 gate 9.2 makes this a manual check for Step G. Automate later if Step G surfaces patterns worth scripting. |
| I-1 | Pragmatist + DeepSeek | **provenance.json ordering discipline** — live Step G forms must be tagged BEFORE authoring, not retroactively; per `tests/fixtures/provenance.json` lines 46–47 `ordering_constraints`. | **CONFIRM** — operator must read `provenance.json` ordering section during kickoff; create step-g-live entries before authoring begins. Add as new step -2 (before comparator cleanliness check) in §3.3. |
| I-2 | Pragmatist I-2 | **archon-subset covers 4 of 11 findings** — subset scope boundary. | **CONFIRM** — already carried into FN-1 Archon-specific clarification. Redundant carry OK as documentation discipline. |
| I-3 | Codex additional | **zustand-form.json provenance `authored-from-scan-data`** — template-for-shape, NOT evidence-of-pipeline-correctness. | **CONFIRM** — document in Step G record so future operators don't mistake the fixture for a pipeline-produced baseline. Add sentence to FN-1. |
| I-4 | Codex Q8 #2 | **HEAD state inconsistency** — R1 brief says HEAD `30da757`, REPO_MAP.md §2.2 says `5dbd5bf`, AUDIT_TRAIL.md top checkpoint says `3c09afb`. | **CONFIRM** — owner acknowledges; `30da757` is current (session-close commit after REPO_MAP update). REPO_MAP will be re-synced post-Step-G. No action pre-execution. |
| I-5 | Pragmatist blind spot #4 | **zustand-v3 `formal_review_rate` fixture/golden discrepancy** — fixture has 29%, V2.4 MD golden says 45%. Known enrichment-era discrepancy. | **CONFIRM** — Step G structural-parity anchor is V2.4 MD/HTML (not fixture). If live pipeline resurfaces original PR sample, scorecard cell may diverge from fixture but agree with MD comparator. Expected, not a failure. Document in FN-1 as note. |
| I-6 | Pragmatist Q7 | **caveman/Archon table-vs-bullet scorecard format difference** — V2.4 rendering variation, not drift. | **CONFIRM** — gate #6 checks cell content, not presentation tokens. Already implied by FN-1 9.3 "cell colors match cell-by-cell"; no further action. |
| I-7 | DeepSeek Q1 dissent | **Shape-coverage gap** — Step G validates only 3 shapes; schema may have shape-specific gaps for fd/gstack/postiz/hermes that Step G cannot detect. | **CONFIRM** — acknowledged limitation. §8.8.7 already documents this. D-5 is the remediation path. Not a Step G blocker. |
| I-8 | DeepSeek IF-1 | **Continuous mode rationale** — diagnostic density over cost efficiency correct for validation run. | **CONFIRM** — no action. |
| I-9 | DeepSeek 4.4 | **LLM non-determinism false confidence** — gate #5 (re-render) does NOT catch form.json re-authoring variance. | **CONFIRM** — documented as D-3 (see FN-8 6c). No Step G gate change. |

---

## 7. What R2 must produce

### Per fix artifact (FN-1 through FN-9)
Vote **SECOND** (adopt as written) / **ADJUST** (adopt with textual amendment — quote the change) / **REJECT** (do not adopt; provide alternative).

### Per R1 carry-forward item (D-1 through D-6, I-1 through I-9, §6 above)
Vote **CONFIRM** (adopt disposition as written) / **ELEVATE** (upgrade DEFER→FIX NOW or INFO→FIX NOW, with rationale) / **DROP** (not a concern) / **ADJUST** (with textual amendment).

### Overall Step G execution verdict
- **SIGN OFF** — approach + fix artifacts + carry-forward dispositions are adequate; run Step G
- **SIGN OFF WITH DISSENTS** — adequate with non-blocking trailing dissents
- **BLOCK** — approach still missing something load-bearing before first run

### New items (if any)
R2 is consolidation. New FIX NOW items should be rare; if you see one, flag explicitly and keep scope tight.

**Word cap: 2000 words.** Match R2 density of prior reviews. Your R2 response at `.board-review-temp/step-g-execution/<agent>-r2.md`.

---

## 8. Per-agent framing

- **Pragmatist (Sonnet 4.6):** FN-1 AFTER drops your ±10% evidence-count tolerance in favor of exact linkage + informational count. Does this reconcile with your original intent (you wanted a falsifiable test — exact linkage arguably achieves that better than ±10% count)? You also raised 4 blind spots; confirm FN-1 + FN-2 + FN-9 close #1–#3 and I-5 carries #4.
- **Systems Thinker (Codex GPT-5):** FN-4 graduated rubric splits the difference on "17/18 NOT a pass." Gate-6 single-target = partial pass (Pragmatist/DeepSeek position); gates 1–3 + 5 single-target = full rollback (closer to your strictness). SECOND / ADJUST / REJECT? Also: D-4 schema hardening — still CONFIRM DEFER, or Step G pre-req?
- **Skeptic (DeepSeek V4):** your worst-case walkthrough (systematic severity downgrade) is the load-bearing scenario. Does FN-1 gate 9.2 (severity per F-ID exact, zero inversions) fully close it? Do you want D-6 (automated severity distribution script) ELEVATED from DEFER to FIX NOW, or is the manual check in FN-1 9.2 sufficient for Step G?

All three: the goal of R2 is R3-readiness. Name what (if anything) must change for you to reach SECOND on every FN + CONFIRM on every D/I item.
