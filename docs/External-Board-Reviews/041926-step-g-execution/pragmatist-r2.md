# Pragmatist R2 — Step G Execution Consolidation

**Agent:** Claude Sonnet 4.6 (Pragmatist)
**Date:** 2026-04-19
**Round:** R2 Consolidation

---

## Vote table — all 24 items

| Item | Vote | Rationale |
|---|---|---|
| FN-1 | SECOND | Exact linkage beats ±10% count tolerance. 9.1–9.6 are all falsifiable. Archon-specific clarification closes blind spot #1 correctly. See §8 framing answer below. |
| FN-2 | SECOND | Mandatory `compute.py` + artifact capture closes blind spot #2. The byte-for-byte equality check between `compute-output-<target>.json` and `form.json` is the right enforcement mechanism. |
| FN-3 | SECOND | 4-case smoke suite is tight. Compact-bundle baseline (0.4) being a PASS case, not a fail, is the critical distinction — good that it's explicit. This closes my FN-3 + Q4 secondary. |
| FN-4 | SECOND | Graduated rubric reconciles the §4.4 split cleanly. Gate 1–3/5 = full rollback aligns with my original principle that pipeline-correctness failures cannot be partial-passed. Gate 6 graduated = I accept. One note: "schema-validation failure = target-local retry" is correct — schema failure is authoring error, not renderer bug. |
| FN-5 | SECOND | Explicit grep on `WARNING:` lines is the right call. Exit-code reliance was the latent bug; this closes it. |
| FN-6 | SECOND | Pre-flight comparator cleanliness is belt-and-suspenders. Given 13/13 parity pairs clean post-U-10, expected to pass, but verifying before committing targets is correct hygiene. |
| FN-7 | SECOND | Pilot-and-checkpoint is the right execution shape. The failure-branching logic inside the checkpoint (zustand gate 4/6 fail → one retry; shape-specific vs rubric-level assessment) is well-specified. |
| FN-8 | SECOND | Phase-boundary spot check (6b) is appropriately scoped as manual visual on first target. Authoring-determinism (6c) explicitly deferred and documented — this is the right disposition; don't gate Step G on a property the architecture doesn't yet claim. |
| FN-9 | SECOND | Bundle-complete gate with 3c.1–3c.3 is exactly what closes blind spot #3. Committing the bundle to `scan-bundles/` as a pre-condition for form.json authoring is the right sequencing enforcement. |
| D-1 | CONFIRM | Fresh-HEAD live scan belongs post-Step-G. Not a Step G gate. |
| D-2 | CONFIRM | Phase 3 automation is future-cycle work. FN-2 covers the manual-but-disciplined path for Step G. |
| D-3 | CONFIRM | LLM non-determinism on form.json re-authoring is correctly deferred. FN-8 6c documents it; no Step G gate needed. |
| D-4 | CONFIRM | Schema hardening stays deferred. Active watch during Step G is the right posture — upgrade only if Step G surfaces concrete pain. Don't pre-load schema work onto the acceptance run. |
| D-5 | CONFIRM | Missing-shape fixtures are post-Step-G. Acknowledged limitation in §8.8.7. |
| D-6 | CONFIRM | Manual gate 9.2 (severity per F-ID exact match) is sufficient for Step G. Automate later if Step G surfaces patterns worth scripting. Rejecting ELEVATE here — the manual check in FN-1 is load-bearing; scripting it now adds ceremony without closing a new failure mode for Step G. |
| I-1 | CONFIRM | Provenance ordering discipline — tag BEFORE authoring, per `ordering_constraints`. Correct as new step -2 in §3.3. |
| I-2 | CONFIRM | archon-subset scope boundary already folded into FN-1 Archon-specific clarification. Redundant carry is fine as documentation discipline. |
| I-3 | CONFIRM | zustand-form.json provenance note is important: template-for-shape, not evidence-of-pipeline-correctness. This prevents a future operator from reading "fixture passed" as "pipeline validated on zustand." |
| I-4 | CONFIRM | HEAD state inconsistency acknowledged. `30da757` is current. REPO_MAP sync post-Step-G is fine. |
| I-5 | CONFIRM | zustand-v3 formal_review_rate 29% vs 45% discrepancy is correctly handled: anchor is V2.4 MD/HTML, not fixture. If live pipeline resurfaces the original PR sample and scorecard diverges from fixture but agrees with MD comparator, that is expected behavior. |
| I-6 | CONFIRM | Table vs bullet is rendering variation, not drift. Gate 9.3 checks cell content/color, not presentation tokens. No further action. |
| I-7 | CONFIRM | Shape-coverage gap is an acknowledged Step G limitation. D-5 is the path. Not a blocker. |
| I-8 | CONFIRM | Continuous mode rationale confirmed. No action needed. |
| I-9 | CONFIRM | LLM non-determinism false confidence is documented as D-3 per FN-8 6c. Gate 5 scope (render-determinism, not authoring-determinism) is correctly bounded. |

---

## Discussion

**FN-1 through FN-9 form a tight pre-execution harness.** Steps -2, -1, 0 (provenance tagging → comparator cleanliness → adversarial smoke) happen before any live bundle is authored. Steps 3b, 3c (compute.py capture → bundle-complete gate) happen before form.json authoring. Steps 6b, 7 (phase-boundary spot check → warning-count inspection) happen before gate acceptance. This is correctly sequenced; no reordering needed.

**The one real risk the R2 artifacts don't fully close:** FN-5 specifies parsing `WARNING:` lines from stdout, but doesn't specify WHERE the operator captures that output. In practice, if `--parity` is run interactively without redirecting stdout, the grep check is manual and forgeable. This is acceptable for Step G (operator-in-the-loop validation, not automated CI), but worth a sentence in FN-5 recommending `tee` or redirect: `validate-scanner-report.py --parity <md> <html> 2>&1 | tee parity-output.txt && grep -c '^WARNING:' parity-output.txt`. I am NOT escalating this to a new FN — it's an operational note, not a load-bearing gap. The operator running Step G will be careful; this is not a casual user path.

**FN-4 graduated rubric:** The split in §4.4 was real but the AFTER reconciles it correctly. My original position was gates 1–5 = full rollback, gate 6 graded. FN-4 aligns with that. The addition of "schema validation failure = target-local retry" (behaves like gate 4) is correct — that's authoring error, not renderer error.

**D-6 CONFIRM DEFER is the right call.** Codex and DeepSeek both flagged severity drift as the worst-case scenario; FN-1 gate 9.2 closes it with a zero-tolerance manual check. Scripting an automated severity distribution comparison script before Step G would add two weeks of implementation for a check that one operator can do in five minutes with a markdown diff. The manual check IS load-bearing for Step G; automate only after the pattern recurs.

**No new FIX NOW items.** R2 artifacts are complete. The only open question was whether FN-5 needed output-capture guidance — it doesn't rise to FN-10.

---

## Overall Step G verdict

**SIGN OFF**

All 9 fix artifacts are correctly scoped and falsifiable. The 15 carry-forward dispositions are accurate. The pre-execution harness (steps -2 through 0), execution discipline (3b, 3c), and post-render checks (6b, 7) together close every load-bearing gap identified in R1. The graduated failure rubric (FN-4) replaces the binary rollback with a defensible graduated contract. No remaining items require board action before first target run.

---

## §8 Per-agent framing answers

**FN-1: ±10% evidence-count tolerance vs. exact linkage.**
Exact linkage (every non-OK finding has non-empty `evidence_refs`; every ref resolves to a declared entry) achieves my original intent better than ±10% count. My ±10% was a proxy for "don't fail on minor evidence card count variance between V2.4 rendering styles." The actual risk was dead refs and unreferenced cards — exact linkage tests that directly. Count tolerance was noise; I withdraw it. SECOND on FN-1 as written.

**Blind spots #1–#4 disposition:**
- Blind spot #1 (archon-subset vs. full-catalog comparator): CLOSED by FN-1 Archon-specific clarification.
- Blind spot #2 (phase_4b_computed must be computed, not authored): CLOSED by FN-2 mandatory compute.py + byte-for-byte equality enforcement.
- Blind spot #3 (bundle must be complete before form authoring): CLOSED by FN-9 bundle-complete gate (3c.1–3c.3).
- Blind spot #4 (zustand-v3 formal_review_rate fixture/golden discrepancy): CARRIED as I-5. Anchor is V2.4 MD/HTML. Expected behavior documented. Correctly not a gate.

All four blind spots have adequate dispositions. Step G is ready to run.
