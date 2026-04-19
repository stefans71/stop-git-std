# Board Review R1 — Skeptic Response

**Reviewer:** Skeptic (DeepSeek V4)
**Date:** 2026-04-19
**Verdict:** SIGN OFF WITH DISSENTS
**Word count:** ~1900

## 1. Verdict

**SIGN OFF WITH DISSENTS.** The Step G execution approach is fundamentally sound but contains critical blind spots in schema drift detection, bundle validator coverage, and failure mode analysis. The 3-target, same-SHA, sequential approach is appropriate, but requires additional safeguards.

## 2. Direct answers to Q1–Q8

### Q1 — Is 3 targets sufficient?
**Answer:** Yes, 3 targets are sufficient **only if** structural-parity gate #6 is rigorously defined. The 3 shapes (JS library, curl-pipe installer, agentic platform) represent distinct architectural patterns. Expanding to 5 would require fixture authoring, which introduces co-dependency. Contracting to 1 loses cross-shape signal. **Dissent:** The "only shapes with V1.1 fixtures" limitation creates a coverage gap that Step G cannot detect. If schema has shape-specific gaps (e.g., missing fields for CLI binary shape), Step G passes but future shapes fail.

### Q2 — Same-SHA rescan vs. fresh HEAD?
**Answer:** Same-SHA rescan is correct for structural-parity validation. Fresh HEAD introduces uncontrolled variables (repo changes) that obscure pipeline validation. The Archon rerun record (`docs/GitHub-Scanner-Archon-rerun-record.md`) already proves determinism across SHA bumps. **Confirm:** pinned-SHA rescan.

### Q3 — How does form.json authoring avoid multica-class drift?
**Answer:** It doesn't. The schema itself is a new drift surface. A schema-valid but semantically-wrong `form.json` could pass all gates. Example: LLM sets `severity: "Info"` instead of `"Warning"` for a finding that V2.4 marked as Warning. Schema validation passes, validator passes, structural-parity gate #6 must catch this. **Problem:** §8.8.5 gate #6 is undefined: "structural parity" lacks tolerance thresholds. Need explicit checklist: finding count exact match (±0), severity distribution exact match, scorecard cell exact match, evidence-card count exact match.

### Q4 — Bundle validator coverage on live bundles?
**Answer:** Insufficient. The `--bundle` validator was tested against 5 archived V2.4 bundles (`docs/validate-scanner-report.py` lines 1-100 show mode description). These bundles were already clean. **FIX NOW:** Before Step G runs, inject deliberate violations into a test bundle and verify `--bundle` catches them. Specifically: synthesis sentence in evidence block, orphan F-ID reference, missing FINDINGS SUMMARY. The 16-test suite may only test positive cases.

### Q5 — Parallel or sequential?
**Answer:** Sequential (zustand → caveman → Archon) is correct for diagnostic learning. Parallel execution risks missing pattern recognition across shapes. However, sequential creates ordering dependency: if zustand fails, caveman and Archon may not run, losing signal. **Recommendation:** Sequential with explicit checkpoint after each target, allowing partial success analysis.

### Q6 — Failure disposition granularity?
**Answer:** Binary quarantine is too coarse. If 17/18 sub-gates pass and 1 fails (e.g., Archon structural-parity mismatch), that's a **Step G partial failure** requiring targeted fix, not full quarantine. **Proposed rubric:** 
- **Full pass:** All 3 targets pass all 6 gates.
- **Partial pass:** ≥2 targets pass all gates, ≤1 target has isolated failure (document as known limitation).
- **Full fail:** ≥2 targets fail any gate, or any target fails validator/parity gates (1-3).

### Q7 — Structural-parity comparator confidence?
**Answer:** All 3 V2.4 comparators are canonical-scorecard-aligned post-U-10 (`6481533`). However, caveman and Archon predate validator fixes (Archon: `eabccb8`, caveman: `34cc07b`). U-10 clean-sweep should have caught latent drift, but **verify:** Run `--parity` on each V2.4 comparator's MD+HTML pair to confirm zero warnings. If warnings exist, comparator is contaminated.

### Q8 — Catch-all blind spots?
**Answer:** The worst failure mode is **semantic inversion with schema compliance**. Example: LLM authors `form.json` where `phase_4_structured_llm.findings.entries[].severity` is systematically one level lower than V2.4 (Critical→Warning, Warning→Info). Schema validation passes (enum valid). Validator passes (structure intact). Parity passes (findings present). Structural-parity gate #6 must detect severity distribution mismatch. **Missing:** Automated severity distribution comparison.

## 3. FIX NOW / DEFER / INFO items

### FIX NOW (block Step G execution)
1. **FN-1: Define structural-parity tolerance thresholds** — §8.8.5 gate #6 needs explicit checklist with zero tolerance for: finding count, severity distribution, scorecard cell values, evidence-card count. Add to operator checklist before first target.
   - **Rationale:** Prevents semantic drift passing as "structural parity."
   - **Resolution:** Amend §8.8.5 with bulleted checklist referencing V2.4 comparator.

2. **FN-2: Smoke-test bundle validator with deliberate violations** — Before authoring live bundles, test `--bundle` mode catches: synthesis in evidence, missing FINDINGS SUMMARY, orphan F-IDs.
   - **Rationale:** Ensures validator detects violations, not just passes clean corpus.
   - **Resolution:** Create test bundle with injected violations, run `--bundle`, confirm exit code 1.

3. **FN-3: Verify V2.4 comparator parity cleanliness** — Run `--parity` on all 3 V2.4 comparator pairs (zustand-v3, caveman, Archon). Any warnings indicate contaminated anchor.
   - **Rationale:** Structural-parity gate requires clean comparator.
   - **Resolution:** If warnings exist, document as known limitation or re-scan.

### DEFER (post-Step G)
1. **DF-1: Schema hardening for missing shapes** — CLI binary (fd), Claude Code skills (gstack), web app (postiz-app), Python platform (hermes-agent) shapes lack fixtures.
   - **Rationale:** Step G cannot validate these shapes; defer to post-Step-G work.
   - **Reference:** §8.8.7 known limitations.

2. **DF-2: Automated severity distribution comparison** — Script to compare V2.5-preview vs V2.4 severity counts.
   - **Rationale:** Catches semantic inversion failure mode.
   - **Reference:** Q8 worst-case scenario.

### INFO (awareness)
1. **IF-1: Continuous mode diagnostic advantage** — Owner's rationale (diagnostic density over cost efficiency) is correct for validation run.
2. **IF-2: Provenance tagging discipline** — `tests/fixtures/provenance.json` entries must be created **before** Step G forms are authored, not retroactively.
3. **IF-3: Rollback contract clarity** — §8.8.6 rollback is binary; partial failure rubric (Q6) should be added.

## 4. Additional blind spots

### 4.1 Evidence reference integrity gap
The validator checks for dead `E*` or `EB-*` references (§8.8.5 gate #4), but does **not** verify that evidence cards referenced in findings actually exist in `phase_4_structured_llm.evidence.entries[]`. A finding could reference `E-42` but `evidence.entries` only goes to `E-41`. Schema validation passes (string type), validator passes (no syntax error). **Detection gap.**

### 4.2 Scorecard cell value drift
`phase_3_computed.scorecard.cells[].value` uses `scorecard_color` enum (red/amber/green). LLM could invert values (red→green) while maintaining schema validity. Structural-parity gate #6 must compare cell-by-cell values against V2.4. **Missing:** Automated cell-value comparison.

### 4.3 Phase boundary contamination
The schema separates facts (Phase 1), inference (Phase 4), synthesis (Phase 5). LLM could place synthesis content in Phase 4 fields (e.g., `what_this_means` prose in `phase_4_structured_llm.action_steps`). Schema validation passes (string type). Validator cannot detect semantic phase violation. **Integrity gap.**

### 4.4 Determinism test incompleteness
Gate #5 tests re-rendering same `form.json` produces byte-identical output. Does **not** test that same `gh api` capture → same `form.json`. Two pipeline runs on same SHA could produce different `form.json` (LLM non-determinism) yet each passes determinism test. **False confidence.**

## 5. Worst-case walkthrough

### Scenario: Systematic severity downgrade
1. **Step G execution:** Operator runs pipeline on zustand at pinned SHA.
2. **LLM behavior:** LLM produces `form.json` with all finding severities downgraded (Critical→Warning, Warning→Info, Info→OK). Schema validation passes (enum values valid).
3. **Rendering:** `render-md.py` + `render-html.py` produce MD+HTML with downgraded severities.
4. **Validator gates:** 
   - Gate #1: `form.json` validates clean ✓
   - Gate #2: `--report` passes (structure intact) ✓
   - Gate #3: `--parity` zero errors/warnings (findings present) ✓
   - Gate #4: Evidence refs resolve ✓
   - Gate #5: Re-render determinism ✓
5. **Structural-parity gate #6:** Operator performs manual comparison. If checklist is vague ("structural parity"), operator may miss severity distribution mismatch. Finding count matches, evidence cards match, but risk assessment is wrong.
6. **Result:** Step G passes, V2.5-preview declared validated, but produces systematically less-severe scans than V2.4.

### Detection requirements:
- **Automated severity distribution comparison:** Script to extract severity counts from V2.5-preview vs V2.4, flag mismatches.
- **Explicit structural-parity checklist:** Must include "severity distribution exact match" item.
- **Scorecard cell comparison:** Cell-by-cell value match requirement.

### Mitigation:
Add to §8.8.5 gate #6: "For each finding in V2.4 scan, there must be a finding in V2.5-preview scan with same F-ID and same severity. Tolerance: zero mismatches."

## 6. Dissent rationale

**Primary dissent:** Structural-parity gate #6 is undefined. Without explicit tolerance thresholds and comparison checklist, semantic drift can pass. This is the core failure mode Step G must catch.

**Secondary dissent:** Bundle validator coverage unproven. The 16-test suite may only validate positive cases; need negative test with deliberate violations.

**Tertiary dissent:** Failure disposition is binary (quarantine vs pass). Need graduated rubric for partial failures.

**Overall:** Step G approach is sound but requires hardening before execution. The 3-target, same-SHA, sequential approach is correct. Continuous mode provides diagnostic advantage. All pre-reqs cleared. **Sign off with dissents** to enforce missing safeguards.