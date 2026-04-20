# Step G Finding SF1 — Scorecard calibration drift: compute.py vs V2.4 comparator MD

**Status:** HALT (owner directive 2026-04-20)
**Surfaced during:** Step G execution pilot — compute driver dry-run on zustand-step-g-form.json Phase 1 data
**Board approval required before Step G resumes:** YES — calibration resolution is a design decision, not a code fix
**Severity in graduated rubric (§8.8.6):** Pipeline-correctness issue (Phase 3 compute gate); Step G cannot proceed until resolved

---

## TL;DR

Running `docs/compute.py`'s scorecard cell calibration on the Phase 1 raw data from each of the 3 Step G targets produces cell colors that **do not match** the V2.4 catalog comparator MD scorecard cells for the same targets. This is systemic (all 3 targets affected, multiple cells each), not authoring drift. Step G gate 6.3 (scorecard parity cell-by-cell) cannot pass until compute.py's calibration is aligned with V2.4 LLM adjudication — or vice-versa.

**This is exactly what Step G is designed to surface** — the calibration gap between the 8 automatable Phase 3 operations (compute.py) and the V2.4 LLM's scorecard judgments. The question is not "is there a bug" — it's "which source is canonical."

---

## Evidence

### Cell mismatches across all 3 comparator targets

| Target | Cell | V2.4 comparator MD | compute.py output | Mismatch |
|---|---|---|---|---|
| zustand-v3 | Q3 Do they tell you about problems? | Amber ("No advisory channel... team has a contributing guide") | red (no-policy + 0 advisories) | ✗ |
| zustand-v3 | Q4 Is it safe out of the box? | Green ("npm verified, zero runtime deps, no install scripts") | amber (has_warning_or_above=true) | ✗ |
| caveman | Q2 Do they fix problems quickly? | Amber ("5-day lag") | green (5 days ≤ 7 threshold) | ✗ |
| Archon | Q1 Does anyone check the code? | Red ("8% formal / 58% any, no protection") | amber (any≥50 branch) | ✗ |
| Archon | Q3 Do they tell you about problems? | Green ("SECURITY.md + public issues") | amber (has_policy OR pub>0) | ✗ |

**Note:** Not every cell is mismatched; several cells match cleanly across all 3 targets. The mismatch is not random — it reflects two distinct philosophies about what each question measures.

### The philosophical difference

**compute.py (deterministic threshold-based):**
- Treats each cell as a single-axis signal with hard thresholds
- Q3: `has_security_policy AND published_advisories > 0 AND not silent_fixes` = green; `OR` of above = amber; else red
- Q4: `all_channels_pinned AND artifact_verified AND NOT has_warning_or_above` = green; `has_critical_on_default_path` = red; else amber
- Q1: `any>=60 AND formal>=30 AND branch_protection` = green; `any<30 OR (solo AND any<40)` = red; else amber via `any>=50 OR formal>=20`
- Q2: `open_sec_issues=0 AND cve_age<=7` = green; `issues<=3 AND cve_age<=14` = amber; else red

**V2.4 comparator MD (LLM adjudication, softer):**
- Weights multiple signals, considers context
- Q3 zustand-v3: "No SECURITY.md BUT team has contributing guide" → soft amber, not hard red
- Q4 zustand-v3: "Is it safe OUT OF THE BOX" interpreted as runtime-surface safety (clean code-path, zero deps), not governance risk → green despite F0 Warning
- Q2 caveman: "5-day merge lag" interpreted as amber (visible friction), not green (≤7 threshold met)
- Q1 Archon: "8% formal, 58% any, no governance" interpreted as red overall, not amber (simple threshold allows amber)
- Q3 Archon: "SECURITY.md + public issues" interpreted as green, bypassing compute.py's "published_advisories > 0" gate

### Impact on Step G acceptance matrix

Per §8.8.5 gate 6.3: "Scorecard cells — all 4 canonical questions present + all 4 cell colors match V2.4 comparator cell-by-cell."

Per §8.8.3 Step 3b: "Phase 3 computed fields MUST invoke `python3 docs/compute.py` directly. 'Mirror the logic manually' is disallowed for Step G. [...] `phase_3_computed.*` and `phase_4b_computed.verdict.level` in the live `form.json` MUST equal these emitted values byte-for-byte."

These two constraints are **mutually exclusive** under the current state: compute.py output ≠ V2.4 comparator cells for the cells listed above. No authoring choice can resolve this — the operator is forbidden from "mirroring" in step 3b, and the comparator is fixed in gate 6.3.

Per §8.8.6 graduated rubric: this is a pipeline-correctness failure class (Phase 3 compute produces non-matching output). Pipeline-correctness failures on any target require **full rollback**.

**Proceeding would trigger full rollback on all 3 targets.** That is the predictable outcome, not an informative one. The finding is already in hand.

---

## The design question for the board

Two (plus one) resolutions. Each has a cost.

### Option A — Adjust compute.py calibration to match V2.4 LLM judgments

Make compute.py softer / context-aware:
- Q3: Accept "contributing guide OR security policy" as amber (not red) when publish-advisory count is zero
- Q4: Distinguish install-time surface (channels, hooks, code-path) from governance concerns; "has_warning_or_above" alone should not drop Q4 below green
- Q1: Tighten red threshold when formal rate drops below 20% even if any-review is higher (Archon case)
- Q2: Downgrade green→amber when maintainer lag indicates friction (caveman case)

**Pro:** Aligns the 8 automatable operations with catalog reality. V2.4 scans continue to render as expected. Step G can proceed with comparator-matching acceptance.

**Con:** Compute.py becomes a codification of current-V2.4-LLM-judgment rather than an independent calibrated signal. Future re-calibration requires board review each time.

### Option B — Declare compute.py correct; V2.4 LLM was too lenient

Compute.py's stricter thresholds are the canonical calibration; V2.4 MD scorecards reflect author-time judgment that should have been tighter. Fix direction: re-author V2.4 comparator scorecards to match compute.py output.

**Pro:** compute.py is deterministic, auditable, easily regression-tested. Future scans get consistent calibration.

**Con:** Requires re-rendering all 11 V2.4 catalog scans to new scorecard cells. U-10 already did one catalog harmonization pass (backward-align to V2.3 canonical questions); this would be a second harmonization on cell colors. Also: the V2.4 LLM adjudications are arguably more user-correct (Q4 = "is the library safe to install out of the box" is clearly different from "does the library have any governance warning anywhere" — treating them as the same is the bug).

### Option C — Split Phase 3 from Phase 4b-sc scorecard authority

Move scorecard cells OUT of `phase_3_computed` and into `phase_4_structured_llm.scorecard_cells` — let the LLM adjudicate each cell with structured-constraints (enum colors, required rationale citing evidence). compute.py retains the other 7 automatable operations (C20 severity, solo-maintainer, exhibit grouping, boundary cases, coverage cells, methodology, F5 disclosure).

**Pro:** Acknowledges the design truth: scorecard cell colors are judgments, not computations. Frees compute.py from calibrating softer human judgments. Retains deterministic status for operations that really are mechanical (verdict level, C20 severity, solo-maintainer).

**Con:** Schema change (V1.1 → V1.2). Re-work Step G fixture forms, renderer, tests. Step G cannot resume on V1.1 — becomes a multi-commit effort before re-starting acceptance runs.

---

## What the board decides

Not "is compute.py buggy" (it's behaving per calibration). Not "is V2.4 MD wrong" (it's reasonable adjudication). The question:

**Where should scorecard cell color authority live?**

1. In compute.py (deterministic, threshold-based, auditable) — Option A requires recalibration to match catalog reality
2. In the V2.4 MD authoring rubric (LLM adjudication, softer) — Option B requires re-harmonizing the catalog
3. In neither exclusively — Option C splits authority cleanly (schema change, deferred)

---

## What the board needs before voting

- This finding document
- Current compute.py scorecard functions (`docs/compute.py` lines 78-180)
- Current V2.4 prompt's scorecard calibration section (`docs/repo-deep-dive-prompt.md` lines 743-758)
- The 3 comparator MDs for reference
- The 5 specific cell-level mismatches with evidence

---

## Step G status while halted

- Pre-flight Steps -2, -1, 0 **remain clean** (commit `9840cdf`).
- Zustand work-in-progress `form.json` is NOT authored further. Current state: template copy in `.board-review-temp/step-g-execution/zustand-step-g-form.json` (unmodified from V2.3 template).
- Provenance entry `zustand-step-g-form.json` remains tagged `step-g-live-pipeline` per §8.8.3 Step -2. Does NOT transition to `step-g-failed-artifact` because this is not a Step G authoring failure — it's a design pre-req halt.
- No impact on the 279/279 tests or 13/13 parity sweep.
- Operator Guide §8.8 is NOT in rollback — it remains the canonical Step G spec; the halt is pre-authoring.

---

## Links

- **Step G execution spec:** `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 (esp. §8.8.3 Step 3b byte-for-byte rule + §8.8.5 gate 6.3 cell-by-cell rule + §8.8.6 pipeline-correctness rollback class)
- **Step G approval:** `docs/External-Board-Reviews/041926-step-g-execution/CONSOLIDATION.md`
- **Compute.py:** `docs/compute.py` (lines 78-180 for scorecard)
- **V2.4 prompt scorecard calibration:** `docs/repo-deep-dive-prompt.md` lines 743-758
- **Comparator MDs:** `docs/GitHub-Scanner-zustand-v3.md`, `docs/GitHub-Scanner-caveman.md`, `docs/GitHub-Scanner-Archon.md`

**Authored:** 2026-04-20 during Step G execution pilot
**Author:** Claude Opus 4.7 operator
**Directive:** Owner 2026-04-20 — halt and frame as a Step G finding, not a pre-existing bug
