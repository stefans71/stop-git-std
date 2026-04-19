# Pragmatist (Sonnet 4.6) — R1 Step G Execution

**Date:** 2026-04-19
**Verdict:** SIGN OFF WITH DISSENTS

---

## Verdict rationale

The approach is sound. The pre-req queue is genuinely clear (all 4 items verified against AUDIT_TRAIL + CONSOLIDATION docs). Continuous mode is the right call for a validation run. The 3-target scoping is justified and not hand-waving. Two issues need tightening before the first keystone — both are FIX NOW at the execution-sequencing level, not code changes.

The brief does the right thing by explicitly separating "the renderer is deterministic" from "Step G is low-risk." I want to press on exactly what the determinism guarantee covers and what it does not, because I think §3 understates the new risk surface.

---

## Q1 — Is 3 targets sufficient?

**Yes, 3 is the right number for Step G.** Alternative A (1-target spike on zustand) is tempting but would leave an open question: does the pipeline degrade gracefully on shapes with more complex finding sets? Caveman has 9 findings + split verdict; Archon has open CVEs + split verdict + monorepo topology. These are structurally different authoring challenges. Running all 3 gives an 18-gate matrix that actually earns "Step G passed."

Alternative B (expand to 5 by co-authoring new fixtures) is explicitly wrong. It collapses the acceptance test: if the operator is simultaneously authoring the fixture for the first time AND producing the live form.json, there is no independent comparator. The entire point of Step G is to test live pipeline against a known-good baseline.

One nuance: the brief notes that zustand-form.json has provenance `authored-from-scan-data` (not `back-authored-from-golden-md` like caveman and archon-subset — see `tests/fixtures/provenance.json` lines 11–21). This means the structural-parity comparator for zustand is the V2.4 zustand-v3 MD/HTML, not the fixture. That's fine — the gate is against the V2.4 catalog scan, not the fixture. But worth naming explicitly in the execution run record.

---

## Q2 — Same-SHA rescan vs. fresh HEAD?

**Confirm pinned-SHA rescan for Step G.** The brief's rationale is correct. The purpose of Step G is to validate the pipeline architecture, not to discover new findings. Running at fresh HEAD introduces two uncontrolled variables simultaneously: live data variation AND pipeline correctness. If structural-parity gate #6 fails, you can't isolate whether it's a pipeline problem or a repo-change problem.

Fresh-HEAD testing is important but belongs in a post-Step-G "live scan SOP" validation. Encode the deferred item now — it's a deferred pre-req for V2.5-preview being usable for production scans on repos that don't have prior V2.4 catalog entries.

---

## Q3 — Schema-drift risk on form.json authoring

**This is the primary risk surface and the brief's treatment of it (§4, Q3) is incomplete.**

The brief frames the risk correctly ("LLM produces schema-valid-but-semantically-wrong form.json") but then defers entirely to structural-parity gate #6 as the catch. That's insufficient. Here's why:

**What jsonschema catches:** Wrong type, missing required fields, enum violations (e.g., `severity: "Severe"` instead of `"Critical"`), wrong phase structure. The schema enforces these mechanically.

**What jsonschema does NOT catch:** Correct-enum-but-wrong-value semantic errors. For example:
- LLM marks a finding `severity: "Warning"` when V2.4 scored it `"Critical"` (valid enum, wrong judgment)
- LLM populates `phase_3_computed.c20_severity.result: "Warning"` when the compute logic would produce `"Critical"` (compute.py should derive this deterministically, but operator runs it manually per §8.8.3 step 4)
- LLM assigns a scorecard cell `color: "amber"` when V2.4 produced `"red"` (valid enum, semantic drift)
- LLM populates `phase_4b_computed` manually instead of running `compute_verdict` — if compute_verdict is skipped or fudged, the rendered verdict level may disagree with the actual finding set

**What structural-parity gate #6 catches (and its limits):** Gate #6 per §8.8.5 says "rendered output is reviewed against the V2.4 scan of the same repo for structural parity." But the brief's parity checklist is vague — "findings count, severity distribution, scorecard cells, verdict level, evidence-card count." This is a human review step. It has no defined tolerance bounds and no pass/fail criterion beyond "reviewer judgment."

**Specific FIX NOW:** Before Step G runs, define the structural-parity checklist with explicit pass/fail bounds:
1. **Finding count** — exact match required (V2.5-preview must have same number of findings as V2.4 scan of same repo at same SHA)
2. **Severity distribution** — exact match required per finding ID (F0 must be the same severity, not just "roughly similar distribution")
3. **Scorecard cell colors** — exact match required (all 4 cells must match V2.4)
4. **Verdict level** — exact match required (Critical/Caution/Clean)
5. **Evidence ref count** — within ±10% (evidence card prose may differ; count is a proxy for truncation)

Without explicit bounds, gate #6 is a vibe check. With them, it's a falsifiable test.

**Secondary risk — phase_3_computed manual computation:** §8.8.3 step 4 says operators must run `docs/compute.py` functions manually. The compute functions exist but "the pipeline harness calling them from a filled Phase 1 is not yet built." This is explicitly noted in §8.8.3. The risk is that an operator will compute Phase 3 fields by eye rather than by running compute.py, producing subtly wrong scorecard inputs. **FIX NOW: the operator execution checklist must include an explicit `python3 docs/compute.py` invocation for Phase 3 fields, not "or mirror their logic."**

---

## Q4 — Bundle validator coverage on live bundles

**The smoke test the brief proposes is the right call. FIX NOW: run it before the first Step G bundle.** The 16-test suite in `tests/test_bundle_validator.py` has good synthetic coverage (lines 106–163): it tests interpretive-verb-in-evidence fails, pattern-bullet-without-verb fails, missing FINDINGS SUMMARY fails, verdict-without-FID fails, orphan F-ID fails. The corpus tests (lines 82–99) confirm 5 V2.4 bundle files pass.

**What's not tested:** A bundle where a synthesis sentence is embedded in a section heading that the parser classifies as evidence (not synthesis) — the heading-based classification (`parse_bundle_regions`, lines 655–679) uses keyword matching. A live-authored bundle that names its synthesis sections differently could slip interpretation verbs through undetected. For example, if the operator titles a section `## Key risks` instead of `## FINDINGS SUMMARY`, the parser classifies it as evidence and applies the facts-only verb check — which would produce a false failure on a legitimately interpretive section, not a false pass. But the reverse is also possible: an evidence section titled `## Summary of branch protection state` could be classified as synthesis if the operator includes a keyword match.

The brief's proposed smoke test (inject a synthesis sentence into an evidence block, confirm `--bundle` flags it) covers the primary case. Accept this as sufficient with the caveat that it must be run before Step G's first bundle — not concurrently.

**One additional smoke test worth adding:** Confirm that a section titled `## FINDINGS SUMMARY` containing zero F-IDs but valid prose still passes (this is the compact-bundle style used in zustand-v3). The test at line 66–68 in `test_bundle_validator.py` covers the region classification but not whether `check_bundle` reports this as a warning or clean. Cross-reference: `check_bundle` line 748 prints `(no F-IDs parsed)` for this case but does NOT error — correct behavior, but worth confirming with the smoke test.

---

## Q5 — Parallel vs. sequential across 3 targets?

**Confirm sequential (zustand → caveman → Archon).** The brief's rationale is correct. Step G is a validation run, not a stress test of the authoring surface. Parallel runs in delegated sub-sessions would introduce the same DOM-drift risk as multica (each sub-session has different context state; schema drift errors may compound). Sequential allows the operator to incorporate form.json authoring lessons from zustand into caveman, and from caveman into Archon.

Order preference: zustand first because it's the template fixture, caveman second (higher complexity: curl-pipe, 9 findings, split verdict, shell-glob evidence patterns that tripped FX-3b), Archon third (highest complexity: monorepo, open CVEs, subset vs full scope mismatch).

---

## Q6 — Graduated failure-disposition rubric

**The binary rollback is too coarse. Propose a graduated rubric:**

| Failure type | Disposition |
|---|---|
| Validator gate (1–3) fails on any target | Full rollback — §8.8 quarantined |
| Evidence refs dead (gate 4) | Treat as authoring error on that target only; operator re-authors affected findings; target re-runs gate. One-time retry allowed; if second attempt fails, that target fails. |
| Determinism (gate 5) fails | Full rollback — renderer is not deterministic; this is a bug in render-md.py or render-html.py, not an authoring issue |
| Structural-parity (gate 6) fails on 1 of 3 | **DISSENT from binary rollback.** If gates 1–5 pass and only structural-parity fails on a single target, that target fails Step G. Issue a tracked finding ticket (not a rollback). 2-of-3 targets clear = Step G partial pass. V2.5-preview may proceed for the 2 cleared shapes only; the failing shape requires fixture re-authoring + new mini-review before that shape is cleared. |
| Structural-parity (gate 6) fails on 2+ of 3 | Full rollback |

The key insight: gates 1–5 are pipeline correctness. Gate 6 is LLM authoring quality. A pipeline-correct run with one authoring-quality miss is recoverable without quarantine.

---

## Q7 — Structural-parity comparator confidence (spot-check)

**Verified.** Read the three V2.4 catalog scans.

**zustand-v3.md** (catalog #9, most recent): Scorecard uses the canonical 4-question format at lines 29–34. All four questions present: "Does anyone check the code?" / "Do they fix problems quickly?" / "Do they tell you about problems?" / "Is it safe out of the box?" Verdict: Caution. This is the canonical post-U-10 form. **Clean comparator.**

**caveman.md** (catalog #4): Scorecard at lines 71–78 uses a table format with the same 4 canonical questions. Verdict: Critical (split). The questions match the canonical set. Note: caveman uses a `| RED / AMBER | text |` table format rather than bullet format. This is a V2.4 rendering difference, not a content difference — the question set is identical. **Clean comparator**, but the operator must note that structural-parity at gate #6 should check question identities, not table-format-vs-bullets.

**Archon.md** (catalog #2): Scorecard at lines 71–78 uses a table format with emoji severity indicators (🚨 / ⚠ / ✅). Same 4 canonical questions present. Verdict: Critical (split). **Clean comparator.** Note the emoji vs. color-word difference from caveman and zustand — this is V2.4 rendering variation. The V2.5-preview renderer produces a defined format; structural-parity should focus on cell content, not presentation tokens.

**Overall:** All 3 comparators have canonical 4-question scorecard sets and are trustworthy anchors for gate #6. The caveman and Archon table-vs-bullet formatting difference is known V2.4 variation, not drift. Confirmed.

---

## FIX NOW / DEFER / INFO items

| ID | Priority | Item | Rationale | Resolution |
|---|---|---|---|---|
| FN-1 | **FIX NOW** | Structural-parity checklist must define explicit pass/fail bounds before Step G runs | Gate #6 as written is a vibe check; without bounds, two operators could reach opposite verdicts | Author a 5-item explicit checklist (finding count exact, severity per F-ID exact, scorecard colors exact, verdict level exact, evidence ref count ±10%) into the Step G execution record BEFORE running |
| FN-2 | **FIX NOW** | Phase 3 manual compute must specify `python3 docs/compute.py` invocation, not "mirror logic" | §8.8.3 step 4 allows operators to "mirror logic" manually — this creates semantic drift without detection | Step G execution brief must include explicit compute.py invocation instructions for the Phase 3 block; "mirror logic" is not acceptable for a validation run |
| FN-3 | **FIX NOW** | Bundle smoke test must run before the first Step G bundle, not concurrently | Q4 — the corpus tests confirm clean bundles pass but do not confirm dirty bundles fail in all real operator patterns | Run: author one synthetic dirty bundle (synthesis verb in evidence section), confirm `--bundle` flags it, then proceed to live bundle authoring |
| D-1 | DEFER | Fresh-HEAD live scan validation | Post-Step-G deferred item — needed before V2.5-preview production promotion | Add to deferred ledger explicitly as V2.5-preview-production pre-req |
| D-2 | DEFER | Phase 3 pipeline harness (automated compute.py from Phase 1 data) | §8.8.3 already notes this is manual for Step G; automation is a future-cycle item | No action for Step G; just ensure this is on the post-Step-G roadmap |
| I-1 | INFO | provenance.json `ordering_constraints` note re: live Step G forms must be tagged BEFORE catalog promotion | Already documented at `tests/fixtures/provenance.json` lines 46–47; confirm the operator reads this before authoring Step G forms | Review provenance.json ordering_constraints section during Step G kickoff |
| I-2 | INFO | archon-subset-form.json covers only 4 of 11 Archon findings | `provenance.json` line 36–42 documents the subset scope; structural-parity for Archon must account for the subset boundary | Step G execution notes must flag that Archon structural-parity gate #6 compares subset vs full — finding count will NOT match; subset scope boundary must be declared explicitly in the parity check |

---

## Additional blind spots

**1. The archon-subset scope mismatch is a gate-6 landmine.** The brief says "structural-parity diff against the matched V2.4 catalog scan." But `archon-subset-form.json` is explicitly a SUBSET (4 of 11 findings per `provenance.json`). If the Step G live Archon run authors all 11 findings (as a live scan should), the finding count will not match the fixture — but it SHOULD match the V2.4 catalog scan. The brief needs to clarify: gate #6 compares the live V2.5-preview output against the V2.4 catalog scan (`docs/GitHub-Scanner-Archon.md`), NOT against the subset fixture. The subset fixture is for renderer validation only. If the operator confuses these two comparators, they will get a false mismatch.

**2. Phase_4b_computed is a derived field that must be computed, not authored.** The schema has `phase_4b_computed` which is described as Python-derived from `compute_verdict`. If an operator manually authors this field instead of running compute.py, a schema-valid but wrong verdict level could reach the renderer. The structural-parity check on verdict level (gate #6) would catch a wrong verdict, but only if the operator knows to check it. This feeds directly into FN-2.

**3. The §8.8.3 checklist step 3 says "run `--bundle` validator on `findings-bundle.md`."** But §8.8.2 step 2 says "Phases 1–3 unchanged from V2.4." In V2.4 Phase 3 produces the bundle. In V2.5-preview the bundle is an intermediate artifact — it is produced, then consumed to author `form.json`. The operator checklist in §3.3 of the brief reflects this correctly (step 3 = run `--bundle`, step 4 = author form.json from bundle). But there is no explicit step that says "the bundle must be complete before form.json authoring begins." An operator could start drafting form.json mid-bundle and introduce inconsistency. Small sequencing risk, but worth an explicit gate in the execution checklist.

**4. V2.4 zustand-v3.md (the comparator) was itself a re-scan of the original V2.3 zustand scan.** The V2.4 zustand-v3 scorecard shows "formal-review rate" = Amber, but the fixture (`zustand-form.json`) has `formal_review_rate: 29` (29%) while the V2.4 MD says "45% formal-review rate." This is a known fixture/golden discrepancy (the fixture enrichment used a different PR sample than the original V2.4 scan). If the live Step G run at the pinned SHA resurfaces the original V2.4 PR sample data, the scorecard cell color may disagree with the fixture but agree with the V2.4 MD. The structural-parity check should explicitly target the V2.4 MD/HTML, not the fixture. The brief says this but the operator should be aware of the discrepancy.

---

**Bottom line:** The approach is correct. The 4 pre-reqs are verified clean. The three issues I'm flagging (FN-1 explicit structural-parity bounds, FN-2 mandatory compute.py for Phase 3, FN-3 bundle smoke test) are execution-sequencing gates, not architectural problems. Address all three before the first target runs. The archon-subset-vs-full-catalog comparison landmine (blind spot #1) needs a sentence in the execution record to prevent operator confusion.
