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
