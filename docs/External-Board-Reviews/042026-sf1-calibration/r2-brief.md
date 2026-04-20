# SF1 Board Review — R2 Brief (Stateless, Narrow Question)

**Review type:** Targeted consolidation on a hybrid proposal.
**Round:** 2 of up to 3.
**Scope:** NARROW — vote ACCEPT / REJECT / ACCEPT-WITH-MODIFICATIONS on the specific hybrid proposal in §5 of this brief. You may argue for your R1 vote unchanged, but you must engage with the hybrid.
**Your role:** Evaluate whether the hybrid proposal is a durable synthesis OR whether it silently drops something important from your R1 critique. Agents are stateless — all context is inline.

---

## 1. What this project is (short recap)

**stop-git-std** is a GitHub repo security-scanner tool. LLM investigates a target repo via `gh` CLI, produces MD + HTML reports containing Verdict + 4-cell Trust Scorecard + Findings (F-IDs) + Evidence (E-IDs). 11 "catalog" scans exist across 7 repo shapes; all validated under the V2.4 rendering pipeline (LLM authors MD/HTML directly).

A **V2.5-preview** pipeline is currently in validation (Step G acceptance matrix on 3 pinned-SHA targets: zustand-v3 = JS library, caveman = curl-pipe installer, Archon = agentic platform). V2.5 uses a `form.json` intermediate conforming to `docs/scan-schema.json` V1.1. Phase 3 is "deterministic compute" via `docs/compute.py` (8 automatable operations); the scorecard-cell computation (one of those 8) is what SF1 surfaced.

## 2. What SF1 is (short recap)

Step G's compute-driver dry-run produced scorecard cell colors that **do not match** the V2.4 comparator MDs for the same targets. 5 cell mismatches across 3 targets (see Round-1 brief for full evidence):

- zustand-v3 Q3: compute RED vs comparator AMBER
- zustand-v3 Q4: compute AMBER vs comparator GREEN
- caveman Q2: compute GREEN vs comparator AMBER
- Archon Q1: compute AMBER vs comparator RED
- Archon Q3: compute AMBER vs comparator GREEN

§8.8.3 Step 3b (compute.py byte-for-byte authoritative) and §8.8.5 gate 6.3 (scorecard cells cell-by-cell match V2.4 comparator) are **mutually exclusive** under current state. Step G HALTED per §8.8.6 ambiguity rule. Step G is NOT rolled back; zero authoring artifacts exist.

**R1 brief (full technical evidence, including compute.py lines 78–180, V2.4 prompt rubric lines 740–762, all 3 comparator scorecards) is at**: `/root/tinkering/stop-git-std/.board-review-temp/step-g-execution/sf1-r1-brief.md` — reference as needed.

## 3. R1 outcome (vote split)

| Agent | R1 Vote | Summary |
|---|---|---|
| Pragmatist (Claude Sonnet 4.6) | **Option A** — targeted | 5 compute.py patches, 4 new input params, V1.1 unchanged, Step G resumes fastest |
| Systems Thinker (Codex GPT-5) | **New "D"** | Option C target + interim bridge: scorecard compute becomes advisory-diagnostic during bridge; gate 6.3 → discrepancy-review gate; V1.2 formal migration later |
| Skeptic (DeepSeek V4) | **C+** | Go further than C: LLM judgment with `edge_case` flag + `suggested_threshold_adjustment` feedback loop; compute outputs become advisory inputs, not bindings |

**No agent voted Option B.** Re-harmonizing the catalog got zero support.

---

## 4. R1 responses — VERBATIM (full text inlined per SOP §4 dissent-audit rule)

### 4.1 Pragmatist R1 (full)

```
# SF1 R1 — Pragmatist (Claude Sonnet 4.6)

## Vote

Preferred resolution: Option A — with targeted calibration fixes to the 5 mismatching cells, keeping the schema at V1.1 and Step G on its current timeline.

## Rationale

The framing of "which source is canonical" is partially wrong. The real question is: what is compute.py *for*? It was introduced as a faithful codification of the V2.4 prompt rubric. The brief confirms this at §7: "The V2.4 prompt rubric and compute.py's calibration use the same threshold language." But the rubric is ambiguous in exactly the 5 failure cases — which means the LLM had to make judgment calls, and those calls produced the V2.4 catalog. The compute.py author then codified the *rubric's language*, not the *catalog's judgments*, and introduced slightly different interpretations. The 5 mismatches are not evidence that the LLM was "too lenient" (Option B framing) — they are evidence that the rubric leaves room for interpretation and the LLM resolved those gaps in user-correct ways. Option A closes this without schema churn (Option C) or requiring a second catalog harmonization that touches 11 files (Option B). Six months from now I want the pipeline to be running live scans, not still bikeshedding scorecard calibration.

## Resolution details

Apply targeted calibration changes to `docs/compute.py` for the 5 cell mismatches. For each mismatch, the LLM's V2.4 judgment is the better one, and here's why + the concrete code fix:

**Q3 (zustand-v3): compute RED → should be AMBER**

The rubric says Red = "No SECURITY.md OR silent fixes." Zustand has no SECURITY.md, which compute.py correctly reads as red. But the LLM made a softer judgment: "No advisory channel... team has a contributing guide." The rubric's intent for Red is absence of *any* disclosure gesture. A contributing guide is a disclosure gesture (people have a place to report problems) even without a formal SECURITY.md. The compute.py Q3 logic should treat "has_contributing_guide OR has_security_policy" as the amber floor, not "has_security_policy" alone. Concrete change: add `has_contributing_guide: bool` parameter; amber branch becomes `has_security_policy or has_contributing_guide or (published_advisory_count > 0 and not has_silent_fixes)`.

**Q4 (zustand-v3): compute AMBER → should be GREEN**

The rubric says Green = "all channels pinned + artifact verified + no Warning-or-higher findings." compute.py's `has_warning_or_above` flag trips amber. The LLM interpreted Q4 as "safe out of the box" = runtime-surface safety (zero runtime deps, no install scripts, no code-path danger). The Warning finding (F0) was a governance finding, not an install-path finding. The fix is to split `has_warning_or_above` into two signals: `has_warning_on_default_install_path` (triggers amber in Q4) vs general findings elsewhere. This matches the rubric's Q4 definition more precisely — the rubric already says "any finding that applies to a specific user group but not the default install path" = amber. If the warning is *not* on the default install path, it should not block green. Concrete change: rename/split to `has_warning_on_install_path: bool`; use that instead of `has_warning_or_above` in Q4.

**Q2 (caveman): compute GREEN → should be AMBER**

This is the cleanest mismatch to understand. caveman has a merged security PR — no open issues. compute.py sees `open_security_issue_count == 0 AND cve_age == 0` (merged PR has no age) → green. The LLM saw "5-day merge lag" as amber (visible friction). The rubric says Green = "No open security issues AND no open CVE PRs older than 7 days." A 5-day-to-merge PR is not open at query time, so the rubric literally supports green. The LLM was applying extra-rubric judgment. **However**, the LLM's user-correctness intuition is sound — a repo that took 5 days to merge a security fix is not in the same category as one with immediate response. The right fix is to add a `fastest_recent_security_fix_days` or `historical_fix_lag_days` input and apply it as an amber signal: if the most recent closed security fix took >3 days, treat as amber. Concrete change: add `closed_fix_lag_days: int | None`; if `open_security_issue_count == 0 and cve_age <= 7 and (closed_fix_lag_days is None or closed_fix_lag_days <= 3)` = green; if `open == 0 and cve_age <= 7 and closed_fix_lag_days > 3` = amber.

**Q1 (Archon): compute AMBER → should be RED**

compute.py gives amber via `any_rev >= 50` (58% any). The LLM gave red: "8% formal / 58% any · no branch protection · no CODEOWNERS." The prompt rubric says amber = "any-review ≥ 50% OR formal-review ≥ 20%." Archon meets the any threshold. But the LLM overrode because 8% formal + no governance is a qualitatively different situation. The rubric's intent was to allow amber when *one* strong signal exists — but 8% formal with no branch protection is arguably not "any review" in the meaningful sense (it means people click approve without real review). Concrete change: add a "governance floor" override — if `formal < 10 and not has_branch_protection and not has_codeowners`, force red regardless of any-review threshold. This reflects the rubric's spirit over its literal text.

**Q3 (Archon): compute AMBER → should be GREEN**

compute.py gives amber for `has_security_policy AND 0 published_advisories` (amber branch triggers because not all green conditions met). The LLM gave green: "SECURITY.md + public issues." The rubric says Green = "SECURITY.md with private channel AND published advisories for fixed vulns." Archon has a SECURITY.md but 0 published advisories, which by the rubric is amber, not green. This is the one case where the LLM was *arguably* too lenient and compute.py is closer to the rubric's intent. However, the rubric's green condition is very strict ("published advisories for fixed vulns") — a project with a SECURITY.md that has never had a security vulnerability would fail green forever. The practical fix: add `has_reported_fixed_vulns: bool`; if a project has a SECURITY.md but no vulns to report, don't penalize for no published advisories. Concrete: if `has_security_policy and (published_advisory_count > 0 or not has_reported_fixed_vulns)` = green (the "nothing to disclose yet" case). Otherwise amber.

**Implementation summary:** 5 targeted changes, 3 new input parameters (`has_contributing_guide`, `has_warning_on_install_path` replacing `has_warning_or_above` in Q4, `closed_fix_lag_days`, `has_reported_fixed_vulns`). No schema version bump required — `phase_3_computed` inputs change, but V1.1 does not constrain the input field names to compute.py, only the output structure. Update the compute.py function signature, update the 3 Step G fixture forms with the new input values, re-run the dry-run validation. Step G resumes.

## FIX NOW items

1. **Add `has_contributing_guide` to compute.py inputs and Q3 amber logic** — Needed to close zustand-v3 Q3 mismatch.
2. **Split `has_warning_or_above` into install-path vs general in Q4** — Needed to close zustand-v3 Q4 mismatch; rename to `has_warning_on_install_path`.
3. **Add `closed_fix_lag_days` parameter and amber check to Q2** — Needed to close caveman Q2 mismatch.
4. **Add governance-floor override to Q1** — When formal<10% AND no branch protection AND no CODEOWNERS, override any-review amber to red; closes Archon Q1 mismatch.
5. **Add `has_reported_fixed_vulns` parameter to Q3 green check** — Allows projects with SECURITY.md but no vulnerability history to reach green; closes Archon Q3 mismatch.
6. **Update the 3 Step G fixture forms with new input fields** — zustand, caveman, Archon forms need the new parameters populated from the already-captured Phase 1 data.
7. **Re-run compute driver dry-run and confirm all 5 cells now match** — Gate before resuming Step G authoring.

## DEFER items

1. **Update V2.4 prompt rubric to match new calibration language** — The rubric's Q3 and Q1 language will be slightly behind the compute.py logic after these fixes. Not blocking for Step G, but creates technical debt if left indefinitely.
2. **Add regression tests for the 5 previously-mismatching cells** — The existing test suite covers old behavior. New test cases for each of the 5 mismatch scenarios should be added, but this is test hygiene, not a gate.
3. **Clarify the Q4 Warning tier in the rubric** — "no Warning-or-higher findings" is ambiguous about whether governance findings count. A clarifying note would prevent future drift.

## INFO items

1. **The brief claims this is "systemic" but it's 5 cells across 3 targets, not all-cells-across-all-targets.** 7 of 12 cells (Q1×3, Q2×3, Q3×3, Q4×3) match cleanly. "Systemic" overstates it — it's 5 specific calibration gaps, each traceable to a specific rubric ambiguity. This matters because it means the fix is targeted, not a wholesale recalibration.

2. **Option B (declare compute.py canonical) would require re-authoring 11 catalog MDs' scorecard sections.** Looking at the 5 mismatches, the LLM judgments are user-correct in 4 of 5 cases. Forcing compute.py's stricter reading onto the catalog would make several repos look worse than they are (e.g., zustand-v3 going from Green on Q4 to Amber is misleading for a zero-runtime-dependency npm library). Option B optimizes for internal consistency at the cost of external accuracy.

3. **Option C's appeal is architecturally sound** but it solves a future-proofing problem, not the current one. The current problem is 5 specific threshold disagreements, which are resolvable in the current schema. C makes sense as a Phase 2 consideration after Step G completes and the pipeline is running live.

4. **The Q2 caveman case is the most arguable.** The rubric literally supports compute.py's green (merged PR, 0 open issues). If the board disagrees on that one cell, an acceptable alternative is to declare it a compute.py win for Q2 and accept the mismatch as a case where the rubric is clear and the LLM overstepped. This would reduce the fix to 4 cells instead of 5 and allow gate 6.3 to be modified to "all non-Q2-caveman cells match" (or equivalently: re-author the caveman comparator Q2 to green). I'm not proposing this — I think adding `closed_fix_lag_days` is correct and useful — but it's a valid narrowing if the board wants less scope.

## Blind spots

1. **I have not verified what `has_contributing_guide` input data looks like across the 3 targets.** The brief doesn't specify whether the Phase 1 raw capture already includes a contributing-guide flag. If the gh API calls don't surface this, capturing it requires a new gh call — which might mean Phase 1 re-run for zustand. I may be underestimating the data-capture cost of fixing Q3.

2. **I assumed the 3 Step G fixture forms can be updated in place with new input fields without invalidating already-captured Phase 1 data.** If the forms have strict schema validation on inputs (not just outputs), adding new input fields might trigger V1.1 validation errors. I haven't checked the schema's `additionalProperties` setting on the phase_1 input section.

3. **My Q3 Archon fix introduces `has_reported_fixed_vulns` which is a softer signal than the rubric intends.** A security skeptic could argue that "never had a vuln" is not verifiable and that absence of published advisories should always be amber. I'm voting for the practical interpretation, but I acknowledge this is a value call.

4. **I may be wrong about the Q4 zustand-v3 finding being a governance finding rather than an install-path finding.** The brief says "F0 Warning exists" but doesn't specify what F0 is about for zustand. If F0 is an install-path finding (e.g., a lifecycle hook), then compute.py is correct and the LLM was too lenient. I've assumed F0 is a governance/meta finding because zustand is described as a "zero runtime deps, no install scripts" library — but this is an inference, not a verified fact. The board or owner should confirm what F0 is before applying the Q4 fix.
```

### 4.2 Systems Thinker R1 (full)

```
# SF1 R1 — Systems Thinker (Codex GPT-5)

## Vote

Preferred resolution: propose-new — D (Option C as target architecture, with an explicit interim Step G bridge)

## Rationale

The current failure is not mainly a bad threshold problem; it is an authority-boundary problem. Scorecard cells compress evidence, semantics, and user-facing judgment into one output, so forcing them to be both deterministic compute output and the canonical human-readable adjudication will keep recreating drift as new repo shapes appear. Six months from now, the healthy system is one where Phase 3 owns facts and mechanical derivations, Phase 4 owns judgment with constrained rationale, and parity checks validate evidence use rather than pretending judgment is a pure function. Option A hard-codes today's comparator accidents, and Option B hard-codes today's rubric oversimplifications; both increase maintenance burden when calibration drifts again next year. The durable fix is to separate computed signals from adjudicated scorecard cells, then define a temporary bridge so Step G can resume without pretending V1.1 has a clean single authority.

## Resolution details

Proposal D has two parts.

Target architecture:
- Adopt Option C in substance. Remove scorecard cell color authority from `phase_3_computed`.
- Keep Phase 3 responsible for mechanical sub-signals only: review rates, branch protection, solo-maintainer flag, open security item counts, open CVE PR age, policy/advisory/disclosure flags, pinning/verification/default-path exposure flags, and any derived booleans already needed elsewhere.
- Add `phase_4_structured_llm.scorecard` as the sole authority for the four user-facing cells. Each cell should contain at minimum: `question`, `color`, `short_answer`, `rationale`, `evidence_refs`, and `computed_signal_refs`.
- Require the Phase 4 prompt to explain every non-obvious downgrade or upgrade against the computed signals. If the LLM says green where a computed signal looks amber/red, it must name the semantic reason, not just restate facts.

Interim Step G bridge:
- Do not retune `compute.py` to mimic the three comparator scans, and do not rewrite the 11-scan V2.4 catalog to satisfy `compute.py`.
- Freeze the current scorecard portion of `compute.py` as non-canonical for acceptance purposes and treat its output as advisory diagnostics during the bridge.
- Replace gate 6.3 for SF1-related reruns with a discrepancy-review gate: all 4 cells present, rationale cites evidence, and any diff between structured scorecard output and diagnostic compute output is explicitly explained per cell.
- Keep Step 3b byte-for-byte enforcement for the other 7 Phase 3 operations only. Scorecard cells are excluded from byte-for-byte parity until V1.2 lands.
- When V1.2 is ready, delete the scorecard-cell function from `compute.py` or demote it permanently to a non-gating lint/check tool.

Why this is cleaner than A/B/C alone:
- Versus A: it avoids encoding comparator-era judgment drift into logic that will need repeated board intervention.
- Versus B: it avoids a broad catalog rewrite that still leaves the wrong abstraction boundary in place.
- Versus plain C: it adds an operational bridge, so the project has a way to resume Step G without waiting for a perfect schema migration before any progress is possible.

## FIX NOW items

- Define temporary authority split. Update Step G acceptance text so scorecard cells are no longer required to satisfy both gate 6.3 comparator parity and Step 3b compute parity at the same time.
- Mark scorecard compute output diagnostic-only. Document that `compute.py` scorecard cells are advisory during the bridge and cannot fail a run by themselves.
- Draft V1.2 field contract. Write the minimal schema shape for `phase_4_structured_llm.scorecard` before any more pipeline work resumes, so the migration target is concrete.

## DEFER items

- Backfill comparator analysis across all 11 catalog scans. Measure how often V2.4 judgment diverges from strict thresholds beyond the 3 validation targets before deciding whether any computed lint should remain.
- Add override-pattern telemetry. Track recurring reasons the adjudicated scorecard differs from computed signals so future rubric changes are based on observed classes, not anecdotal cases.
- Revisit canonical question wording. Some drift is semantic, especially Q4; tightening the wording may reduce future ambiguity more than threshold changes will.

## INFO items

- The evidence suggests the 4 cells are not equally mechanical; Q3 and Q4 are especially semantic, but Q1 and Q2 also drift once contextual meaning matters. That argues against a per-question patchwork unless the owner is optimizing purely for short-term restart speed.
- If the project instead chooses A, it should be framed as a temporary compatibility patch with an expiry review date, not as the final architecture.
- If the project instead chooses B, it should acknowledge that this is a product decision to prefer strict comparability over user-aligned interpretation; that trade should be explicit, not disguised as bug-fixing.
- My recommendation assumes Step G's purpose is to validate a durable pipeline design, not merely to get one preview workflow over the line quickly.

## Blind spots

- I did not inspect the rest of the renderer/schema code, so I may be underestimating the migration cost from V1.1 to V1.2.
- I am inferring from 3 validation targets plus the catalog descriptions; a full 11-scan audit could reveal that drift is rarer or more patterned than this brief suggests.
- The bridge I propose reduces one hard gate into an explained-diff process, which could introduce reviewer subjectivity if not specified tightly enough.
```

### 4.3 Skeptic R1 (full)

```
# SF1 R1 — Skeptic (DeepSeek V4)

## Vote

Preferred resolution: **C — Schema split V1.1 → V1.2**

## Rationale

All three options are fundamentally flawed because they're solving the wrong problem. The core issue isn't calibration drift—it's that we're trying to automate something that's inherently judgmental. Option A makes compute.py a rubber stamp for past LLM whims, Option B rewrites history to fit a flawed algorithm, and Option C at least acknowledges the truth: scorecard cells are qualitative judgments, not deterministic computations. But even Option C doesn't go far enough—it just moves the problem to a different phase without fixing the underlying design flaw.

## Resolution details

**Option C with a critical modification:** Don't just move scorecard cells to phase_4_structured_llm—eliminate the pretense of deterministic scoring entirely. Replace the 4-cell scorecard with a structured judgment system where the LLM must:
1. For each question, select a color (red/amber/green)
2. Provide a 1-2 sentence rationale citing specific evidence
3. Flag any "edge case" where the evidence conflicts with simple thresholds
4. Optionally suggest threshold adjustments for future calibration

The schema change should look like:
```json
"phase_4_structured_llm": {
  "scorecard_judgments": [
    {
      "question": "Does anyone check the code?",
      "color": "amber",
      "rationale": "65% any-review but no branch protection",
      "edge_case": true,
      "suggested_threshold_adjustment": "Consider lowering formal-review requirement when any-review > 60%"
    }
  ]
}
```

Compute.py should still calculate its "suggested" colors based on current thresholds, but these become advisory inputs to the LLM, not binding outputs.

## FIX NOW items

1. **Schema versioning trap** — Moving to V1.2 creates immediate incompatibility with all existing fixtures. Need a migration path that doesn't break Step G entirely.
2. **LLM judgment consistency** — Without deterministic thresholds, we lose comparability across scans. Need to define what "structured constraints" actually means.
3. **Render pipeline dependency** — Both render-md.py and render-html.py assume phase_3_computed.scorecard_cells exists. This is a breaking change.

## DEFER items

1. **Threshold refinement** — The actual calibration improvements (like distinguishing install-surface from governance) should happen regardless of where authority lives.
2. **Catalog harmonization** — If we keep V2.4 as canonical for now, we need a plan for eventual reconciliation.
3. **Validation gate redesign** — Gate 6.3 needs rethinking if cells become LLM judgments.

## INFO items

**What nobody is saying:** The real problem is that we have 11 "canonical" scans that were authored by an LLM following a prompt that the same LLM apparently ignored in 5 out of 12 cells across 3 targets. That's a 42% disobedience rate on the very rubric we're trying to codify. This suggests either:
1. The rubric is fundamentally flawed/unworkable
2. The LLM is incapable of following it consistently
3. The "canonical" scans aren't actually canonical

**Premise that might be wrong:** That V2.4 scans represent "ground truth." They're LLM outputs, not human-reviewed gold standards. Treating them as canonical creates a circular reference problem.

**Hidden assumption:** That scorecard cells need to be comparable across repos. If they're qualitative judgments, maybe they shouldn't be—maybe each repo gets a bespoke assessment.

## Blind spots

1. **I might be over-indexing on the "judgment vs computation" dichotomy.** Maybe with better thresholds, compute.py could capture the nuance.
2. **I'm assuming schema changes are acceptable.** The project owner might have strong constraints against breaking changes.
3. **I haven't considered the operational cost** of making every scan dependent on LLM judgment quality—this could make the tool less reliable, not more.
4. **The "skeptic" lens might be making me too cynical** about the possibility of finding a workable technical solution.
5. **I'm not accounting for the possibility** that the mismatches are actually bugs in compute.py's implementation of the rubric, not philosophical differences.
```

---

## 5. The hybrid proposal (the narrow thing you are voting on)

**Name:** "A-now + C-for-V1.2 + edge-case annotation"

### Phase 1 — Unblock Step G (this session, on V1.1)

1. Apply Pragmatist's 5 targeted compute.py calibration patches per his R1 Resolution details:
   - Q3 zustand: add `has_contributing_guide: bool` input; amber floor includes `has_contributing_guide OR has_security_policy`.
   - Q4 zustand: split `has_warning_or_above` → `has_warning_on_install_path: bool` for the Q4 gate specifically.
   - Q2 caveman: add `closed_fix_lag_days: int | None`; >3 days drops green to amber.
   - Q1 Archon: add "governance-floor" override — if `formal<10% AND not branch_protection AND not codeowners`, force red.
   - Q3 Archon: add `has_reported_fixed_vulns: bool`; `has_security_policy AND NOT has_reported_fixed_vulns` = green (nothing-to-disclose case).
2. Update the 3 Step G fixture forms with the new input values (from the Phase 1 raw data already captured).
3. Re-run compute-driver dry-run; confirm all 5 cells now match V2.4 comparator cells.
4. Verify schema V1.1 `additionalProperties` setting on Phase 1 input section; adjust if needed to admit new inputs (Pragmatist blind-spot #2).
5. Verify what zustand-v3 F0 Warning actually IS before applying Q4 fix (Pragmatist blind-spot #4). If F0 is install-path, do NOT split `has_warning_or_above` — compute.py is correct and the V2.4 LLM was wrong for Q4 zustand.
6. Step G resumes authoring under current §8.8 spec.

### Phase 2 — Commit to authority-boundary fix post-Step-G (add to deferred ledger as D-7)

Not a vague "maybe later" — a concrete commitment with a measurement trigger and spec sketch.

1. **D-7 on the post-Step-G deferred ledger** — "Scorecard cell authority-boundary migration to V1.2."
2. **Trigger:** After the first 3 live V2.5-preview scans beyond the 3 Step G validation shapes, measure the compute-output vs V2.4-equivalent-judgment delta.
   - If ≥2 cells diverge where the Phase 1 patches don't reach → V1.2 migration goes forward.
   - If all cells hold → D-7 is downgraded to optional polish.
3. **V1.2 schema sketch (approved now, implemented after trigger fires):**
   ```json
   "phase_4_structured_llm": {
     "scorecard_cells": [
       {
         "question": "Does anyone check the code?",
         "color": "red|amber|green",
         "short_answer": "string",
         "rationale": "string — must cite E-IDs",
         "edge_case": true,
         "suggested_threshold_adjustment": "optional string — feedback loop",
         "computed_signal_refs": ["list of compute.py advisory signals considered"]
       }
       // ...4 total
     ]
   }
   ```
4. **When V1.2 lands:**
   - `compute_scorecard_cells()` is demoted from authoritative to advisory; still runs, output surfaces in form as `phase_3_advisory.scorecard_hints` for the LLM to consult.
   - Gate 6.3 changes from "cell-by-cell match" to "cells present + rationale cites evidence + any LLM override of advisory hint is explained in `rationale` AND `edge_case=true`."
   - Step 3b byte-for-byte requirement is **retained** for the other 7 Phase 3 operations (verdict, solo-maintainer, exhibit, boundary, coverage, methodology, F5). Scorecard cells are the ONLY operation moved out.

### Phase 3 — Catalog harmonization is NOT triggered

Option B is explicitly rejected. The 11 V2.4 catalog scans retain their cell colors. compute.py adapts to the LLM judgments via the 5 patches, not the other way around.

---

## 6. Dissent audit — what the hybrid addresses and what it leaves open

**From Pragmatist R1:**
- ✅ Option A's 5 targeted patches are the Phase-1 spine of the hybrid. All 5 land as FIX NOW.
- ✅ Pragmatist's blind-spot #2 (schema `additionalProperties`) promoted to explicit Phase-1 step (hybrid §5.1.4).
- ✅ Pragmatist's blind-spot #4 (Q4 zustand F0 type) promoted to explicit Phase-1 step (hybrid §5.1.5).
- ✅ Pragmatist's INFO #4 (Q2 caveman narrowing option) preserved as a fallback — if Phase-1 step 5 determines `closed_fix_lag_days` isn't cleanly derivable from Phase 1 data, owner can accept compute.py's literal-rubric win on Q2 caveman and adjust gate 6.3 for that one cell instead.
- ✅ Pragmatist's DEFER #1 (update V2.4 prompt rubric to match new calibration) is added to D-7 rider items.
- ✅ Pragmatist's DEFER #2 (regression tests for 5 cells) becomes part of Phase-1 step 3 validation.

**From Systems Thinker R1:**
- ✅ Codex's target architecture (move scorecard authority to Phase 4) IS the V1.2 spec in the hybrid.
- ✅ Codex's "mechanical sub-signals stay in Phase 3" contract preserved (only scorecard cells move).
- ✅ Codex's "LLM rationale must cite evidence and explain overrides" landed as V1.2 gate requirement.
- ❌ Codex's FIX NOW #1 ("Update Step G acceptance text so scorecard cells are no longer required to satisfy both gates at the same time") is REFRAMED rather than addressed. The hybrid keeps both gates in V1.1 by making the 5 compute.py patches align with the V2.4 comparator — which achieves the same operational unblock but through calibration, not authority-split.
- ❌ Codex's "do not retune compute.py to mimic the 3 comparator scans" is DIRECTLY CONTRADICTED by hybrid Phase 1. This is the sharpest dissent the hybrid has to defend. Rebuttal in favor of hybrid: Pragmatist's framing is that the 5 patches fix rubric-ambiguity gaps, not "mimic accidents" — the LLM judgments are rubric-consistent once the rubric is read with normal English-speaker context. Codex is asked to vote on whether he accepts this framing.
- ❌ Codex's "scorecard-cell compute output becomes advisory-diagnostic DURING the bridge" is NOT in Phase 1 of the hybrid — it's deferred to V1.2 post-trigger. Codex may reject this as "kicking the authority-split down the road without a firm timeline."
- ✅ Codex's DEFER items (11-scan backfill, override telemetry, canonical question wording) preserved as D-7 rider items.

**From Skeptic R1:**
- ✅ DeepSeek's `edge_case` field landed as V1.2 structured field.
- ✅ DeepSeek's `suggested_threshold_adjustment` field landed as V1.2 structured field.
- ✅ DeepSeek's "compute.py becomes advisory inputs to LLM, not binding outputs" is the V1.2 contract.
- ❌ DeepSeek's "42% disobedience rate" observation is NOT addressed by the hybrid — the hybrid assumes the V2.4 catalog IS ground truth for the 5 mismatches (Pragmatist's framing). DeepSeek is asked to vote on whether this premise is acceptable.
- ❌ DeepSeek's "are scorecard cells even supposed to be comparable across repos?" challenge is deferred as D-7 rider (Codex's "canonical question wording" DEFER overlaps).
- ❌ DeepSeek's FIX NOW items (schema versioning trap, LLM judgment consistency, render-pipeline breaking change) are all V1.2-timeframe concerns that the hybrid acknowledges but doesn't resolve in Phase 1. The hybrid's bet is that V1.1 with the 5 patches is stable enough to run Step G + a few live scans before V1.2 is designed.

---

## 7. The narrow question

**Is the hybrid proposal in §5 acceptable as a direction?**

Vote one of:
- **ACCEPT** — the hybrid is a durable synthesis; Step G can resume on V1.1 with the 5 patches and D-7 as a firm post-Step-G commitment.
- **REJECT** — the hybrid silently drops something that matters from my R1 critique; state the specific load-bearing dissent that the hybrid fails to address.
- **ACCEPT-WITH-MODIFICATIONS** — the hybrid is close but needs specific change X; state it concretely.

Sub-questions each agent must engage with (pick the ones most load-bearing for your vote):

**For the Pragmatist (R1 voted A):**
- Does adding D-7 as a firm post-Step-G commitment feel like scope creep away from your "ship first" goal, or is it acceptable as post-Step-G future work?
- Are any of your 5 patches fragile enough that you'd rather drop one than accept the hybrid's "verify F0 type before Q4 fix" gate?

**For the Systems Thinker (R1 voted D):**
- Does D-7 with a measurement trigger (3 live scans) give you enough of a commitment to the authority-boundary fix, or does the patch-and-wait approach re-encode the problem you flagged in R1?
- Is there a version of D-7's trigger that's more objective (e.g., "on Nth new repo shape" rather than "on measured drift")?

**For the Skeptic (R1 voted C+):**
- Does your "42% disobedience rate" concern survive the Pragmatist's framing that the mismatches are rubric-ambiguity gaps (not LLM disobedience)? If yes, state the load-bearing reason.
- Is V1.2 with `edge_case` + `suggested_threshold_adjustment` a sufficient manifestation of your R1 judgment-vs-computation critique, even delayed post-Step-G?

**For all 3:**
- Is there a premise in the hybrid that you reject? State it plainly.
- If the owner chose the hybrid, would you want to flag a specific early-warning sign that would justify pulling D-7 forward from post-Step-G to mid-Step-G?

---

## 8. Required output format

```
# SF1 R2 — [Your agent name]

## Verdict on hybrid

ACCEPT / REJECT / ACCEPT-WITH-MODIFICATIONS

## Rationale (3–6 sentences)

[Why this verdict. What moved or didn't move from your R1 position.]

## Engagement with your R1 dissent audit (the items marked ❌ in §6)

[For each of your R1 dissents that the hybrid did NOT address: state whether you accept the hybrid's reframing, or whether the dissent is load-bearing and rejects the hybrid.]

## If ACCEPT-WITH-MODIFICATIONS

[State the specific changes. Be concrete enough to implement.]

## FIX NOW items (new or re-asserted from R1)

[Only items that must be done to make the hybrid work. Zero is fine.]

## DEFER items (anything new or promoted)

[Zero is fine.]

## INFO items

[Anything worth surfacing that doesn't fit above.]

## Blind spots

[Things you might have missed in this R2 analysis.]
```

---

## 9. Meta-context (non-voting)

- This is R2 of up to 3 rounds. If R2 converges (unanimous ACCEPT or ACCEPT-WITH-MODIFICATIONS where modifications overlap), no R3 is needed.
- R2 is narrow: vote on the hybrid specifically. Arguing for your R1 vote unchanged is allowed only if you can show the hybrid fails on a load-bearing dissent.
- Owner is the sole decision-maker. Board is advisory. Your job is to make the strongest case for/against the hybrid so the owner has a real choice.
- **Path forward if REJECT:** R3 would re-examine whether to pursue Option C outright (schema migration now, Step G halted for weeks) or some other synthesis.
- **Path forward if split (e.g., 2 ACCEPT + 1 REJECT):** owner reads the REJECT reasoning and decides.
