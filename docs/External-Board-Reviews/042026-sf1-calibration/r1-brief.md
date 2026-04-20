# SF1 Board Review — R1 Brief (Stateless)

**Review type:** Design decision, not code fix
**Round:** 1 of up to 3 (Blind). R2/R3 skipped if 3 agents converge.
**Scope:** Open — all options on the table. You may propose a new option if A/B/C each miss.
**Your role:** Vote your preferred resolution + rationale + list FIX NOW / DEFER / INFO items.

---

## 1. What this project is

**stop-git-std** is a GitHub repo security-scanner tool. An LLM (Claude) investigates a target repo via `gh` CLI calls and produces an MD + HTML report containing:

- **Verdict** (Critical / Caution / Clean) with severity banner
- **Trust Scorecard** (4 questions, each colored red/amber/green)
- **Findings** (F-IDs like F0, F1, F5 — scored severity Critical / Warn / Info / OK)
- **Evidence** (E-IDs — raw API output excerpts backing each finding)

The tool has been validated against 11 "catalog" scans (V2.4 LLM-authored MDs) across 7 repo shapes (JS library, CLI binary, agentic platform, curl-pipe installer, Claude skills, tiny, web app).

## 2. Two rendering pipelines

- **Workflow V2.4 (production, 11 scans in catalog):** LLM authors MD + HTML directly from a findings-bundle. Proven, human-readable, flexible. The 11 catalog scans all live at pinned SHAs with validator-clean `--report` + `--parity` output.
- **Workflow V2.5-preview (currently in validation):** LLM authors a **`form.json`** conforming to `docs/scan-schema.json` V1.1 (8 phases, facts/inference/synthesis separated). Deterministic `docs/render-md.py` + `docs/render-html.py` produce MD + HTML from the form. Same validator gates as V2.4 plus structural-parity comparison against the V2.4 catalog at the same SHA.

The V2.5-preview pipeline has **8 automatable Phase-3 operations** codified in `docs/compute.py`:

1. Verdict level (Critical/Caution/Clean)
2. **Scorecard cells** (4 questions × color) ← **SF1 is about this**
3. Solo-maintainer flag
4. Exhibit grouping
5. Boundary cases (recency, review rate split-axis)
6. Coverage status
7. Methodology boilerplate
8. F5 silent/unadvertised classification

## 3. Step G and what it's validating

Step G is the acceptance matrix for the V2.5-preview pipeline: three pinned-SHA targets (zustand-v3 = JS library, caveman = curl-pipe installer, Archon = agentic platform), all must clear 7 gates including:

- Gate 3: `--parity` zero errors + zero warnings
- **Gate 6.3: "Scorecard cells — all 4 canonical questions present + all 4 cell colors match V2.4 comparator cell-by-cell (red/amber/green)."**

And the §8.8.3 Step 3b authoring rule:

- **Step 3b: "Phase 3 computed fields MUST invoke `python3 docs/compute.py` directly. Mirror the logic manually is **disallowed** for Step G. [...] `phase_3_computed.*` and `phase_4b_computed.verdict.level` in the live `form.json` MUST equal these emitted values byte-for-byte."**

The graduated failure rubric at §8.8.6:

- Pipeline-correctness failures (gates 1–3, 5) = **full rollback** of V2.5-preview
- Authoring-quality failures (gate 4, 6) = graded, retryable per-target
- **Ambiguity mid-run = HALT immediately, escalate to board mini-review before continuing**

## 4. The finding that triggered this review

During Step G's pre-pilot compute-driver dry-run (zustand target, Phase 1 raw data from the V2.4 scan already captured), the `docs/compute.py` scorecard-cell output **did not match** the V2.4 comparator MD's scorecard cells. Extending the check to the other 2 targets, **all 3 targets had cell-level mismatches**. 5 cell mismatches total, affecting 4 of the 4 canonical questions at least once across the 3 targets.

This is systemic (all 3 targets), not authoring drift. Gate 6.3 and Step 3b are **mutually exclusive** under current state: you cannot make `form.json` both byte-for-byte match compute.py AND cell-by-cell match the V2.4 comparator. No authoring path resolves it.

Per §8.8.6's "ambiguity mid-run = HALT" rule, Step G was halted pre-authoring. Finding SF1 was authored. Board review is required before Step G can resume.

**SF1 is a Step G finding, NOT a pre-existing bug.** Step G's purpose is to surface exactly this kind of calibration gap between compute.py (the 8 automatable operations) and V2.4 LLM adjudication (the canonical catalog). SF1 validates the gate design — the live-pipeline dry-run caught what renderer-validation fixtures at fixture-time could not.

---

## 5. SF1 Finding Doc (verbatim)

```
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
```

(End of SF1 finding doc verbatim.)

---

## 6. Current `docs/compute.py` scorecard function (verbatim, lines 78–180)

```python
def compute_scorecard_cells(
    formal_review_rate: float | None,
    any_review_rate: float | None,
    has_branch_protection: bool,
    has_codeowners: bool,
    is_solo_maintainer: bool,
    open_security_issue_count: int,
    oldest_cve_pr_age_days: int | None,
    has_security_policy: bool,
    published_advisory_count: int,
    has_silent_fixes: bool,
    all_channels_pinned: bool,
    artifact_verified: bool,
    has_critical_on_default_path: bool,
    has_warning_or_above: bool,
) -> dict:
    """Compute the 4 scorecard cells using the V2.4 calibration table.
    Returns dict with color (red/amber/green) and short_answer per cell."""

    # Q1: Does anyone check the code?
    # V2.4 calibration: Green = any>=60% AND formal>=30% AND branch protection
    # Amber = any>=50% OR formal>=20%
    # Red = any<30% OR (solo-maintainer AND any<40%)
    formal = formal_review_rate or 0
    any_rev = any_review_rate or 0
    if any_rev >= 60 and formal >= 30 and has_branch_protection:
        q1_color = "green"
        q1_answer = "Yes"
    elif any_rev < 30 or (is_solo_maintainer and any_rev < 40):
        q1_color = "red"
        q1_answer = "No"
    elif any_rev >= 50 or formal >= 20:
        q1_color = "amber"
        q1_answer = "Partly"
    else:
        q1_color = "red"
        q1_answer = "No"

    # Q2: Do they fix problems quickly?
    cve_age = oldest_cve_pr_age_days or 0
    if open_security_issue_count == 0 and cve_age <= 7:
        q2_color = "green"
        q2_answer = "Yes"
    elif open_security_issue_count <= 3 and cve_age <= 14:
        q2_color = "amber"
        q2_answer = "Partly"
    else:
        q2_color = "red"
        q2_answer = "No"

    # Q3: Do they tell you about problems?
    if has_security_policy and published_advisory_count > 0 and not has_silent_fixes:
        q3_color = "green"
        q3_answer = "Yes"
    elif has_security_policy or (published_advisory_count > 0 and not has_silent_fixes):
        q3_color = "amber"
        q3_answer = "Partly"
    else:
        q3_color = "red"
        q3_answer = "No"

    # Q4: Is it safe out of the box?
    # V2.4 calibration: Green = all pinned + verified + no Warning+
    # Red = any Critical on default install path
    # Amber = any unverified channel OR group-specific finding
    if all_channels_pinned and artifact_verified and not has_warning_or_above:
        q4_color = "green"
        q4_answer = "Yes"
    elif has_critical_on_default_path:
        q4_color = "red"
        q4_answer = "No"
    elif has_warning_or_above or not all_channels_pinned or not artifact_verified:
        q4_color = "amber"
        q4_answer = "Partly"
    else:
        q4_color = "amber"
        q4_answer = "Partly"
```

## 7. V2.4 LLM prompt — scorecard calibration rubric (verbatim, `docs/repo-deep-dive-prompt.md` lines 740–762)

> The 4-cell trust scorecard must use these thresholds. Different scanners calibrating differently was the failure mode that triggered D10. These thresholds are now binding — they ground every cell so reports are comparable across repos and across scanner runs.
>
> **"Does anyone check the code?"**
> - **Green** — `any-review ≥ 60%` AND `formal-review ≥ 30%` AND branch protection on default branch.
> - **Amber** — `any-review ≥ 50%` OR `formal-review ≥ 20%`, regardless of the other metric. Use the label "Informal" when any-review is strong but formal is weak (e.g., 58% any / 8% formal = amber · "Informal").
> - **Red** — `any-review < 30%` OR (solo maintainer — top contributor >80% of commits — AND `any-review < 40%`). Use the label "Rare" when any-review is very low.
>
> **"Do they fix problems quickly?"**
> - **Green** — No open security issues AND no open CVE PRs older than 7 days.
> - **Amber** — 1–3 open security items OR 1 open CVE PR aged 3–14 days. Use the label "Open fixes, not merged yet" when open security work is in motion.
> - **Red** — 4+ open security items OR any open CVE PR older than 14 days OR abandoned (no commits in 90+ days).
>
> **"Do they tell you about problems?"**
> - **Green** — `SECURITY.md` with private channel AND published advisories for fixed vulns.
> - **Amber** — `SECURITY.md` with private channel BUT no published advisories; OR unadvertised-but-release-noted fixes (F5 class). Use the label "Disclosed in release notes, no advisory" when fixes ship without GHSA.
> - **Red** — No `SECURITY.md` OR silent fixes (F5 class). Use the label "No advisory".
>
> **"Is it safe out of the box?"**
> - **Green** — All distribution channels pinned, artifact verified (not just path verified — see Step 8 tier distinction), AND no Warning-or-higher findings.
> - **Amber** — Any distribution channel unverified OR any finding that applies to a specific user group but not the default install path. Use a split-verdict-compatible label like "Single-user: yes. Shared host: wait for PR #X".
> - **Red** — Any Critical finding that applies to the default install path.

**Critical observation:** The V2.4 prompt rubric and `compute.py`'s calibration use the **same threshold language.** compute.py was intended as a faithful codification. The mismatch is that the LLM, given the rubric, **did not actually follow it** in all 3 comparator MDs — it softened the thresholds based on context not captured in the rubric.

## 8. The 3 V2.4 comparator scorecards (verbatim, what `compute.py` is being graded against)

### 8.1 `docs/GitHub-Scanner-zustand-v3.md` — Trust Scorecard (lines 29–34)

```
## Trust Scorecard

- **Does anyone check the code?** — Amber (Informal). 65% any-review rate and 45% formal-review rate are solid, but no branch protection on the default branch prevents a Green rating. Reviews happen voluntarily, not enforced.
- **Do they fix problems quickly?** — Green. Zero open security issues, zero open CVE PRs. Active maintenance with 30 commits in the last 90 days. v5.0.12 shipped 2026-03-16.
- **Do they tell you about problems?** — Amber (No advisory channel). No SECURITY.md file. No published security advisories. The team has a contributing guide but no documented private disclosure path.
- **Is it safe out of the box?** — Green. npm package verified (v5.0.12 on registry). Zero runtime dependencies. No install scripts, no lifecycle hooks, no dangerous patterns in source code.
```

**compute.py output for zustand-v3 inputs:**
- Q1: 65% any + 45% formal + NO branch protection → amber (prompt says green requires branch protection; amber via any≥50% OR formal≥20%). **compute MATCH.**
- Q2: 0 open + 0 cve_age → green. **compute MATCH.**
- Q3: NO SECURITY.md + 0 advisories → **compute RED**, comparator **Amber**. **MISMATCH.**
- Q4: all channels pinned + verified + F0 Warning exists → **compute AMBER**, comparator **Green**. **MISMATCH.**

### 8.2 `docs/GitHub-Scanner-caveman.md` — Trust Scorecard (lines 71–79)

```
## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | RED **No** — 15% formal review rate (5/33) · no branch protection · no CODEOWNERS |
| Do they fix problems quickly? | AMBER **Slow** — 5-day lag between security PR filed and merged |
| Do they tell you about problems? | RED **No advisory** — zero GitHub Security Advisories ever published, no SECURITY.md at repo root |
| Is it safe out of the box? | RED **No** — F0 governance gap applies to default install path + every distribution channel tracks live `main` |
```

**compute.py output for caveman inputs:**
- Q1: 15% formal + any_rev = ? (likely <50%) → **red** via any<30% or fallthrough. **MATCH** (assuming any_rev < 30%).
- Q2: 0 open issues + 5-day merged CVE (so oldest_cve_pr_age_days = 0, because PR is merged not open) → **compute GREEN**, comparator **Amber**. **MISMATCH.** (The V2.4 LLM used "5-day lag" as an amber signal; compute.py uses "open ages", and a merged PR has age 0.)
- Q3: NO SECURITY.md + 0 advisories → red. **MATCH.**
- Q4: F0 Critical on default path → red. **MATCH.**

### 8.3 `docs/GitHub-Scanner-Archon.md` — Trust Scorecard (lines 71–78)

```
## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | 🚨 **No upstream gate** — 8% formal / 58% any · no branch protection · no CODEOWNERS |
| Do they fix problems quickly? | ⚠ Open fixes, not merged yet |
| Do they tell you about problems? | ✅ Yes — SECURITY.md + public issues |
| Is it safe out of the box? | 🚨 **No** — Critical finding applies to default install path (F0 governance gap) |
```

**compute.py output for Archon inputs:**
- Q1: 8% formal + 58% any + NO branch protection → **compute AMBER** (any≥50%), comparator **RED**. **MISMATCH.**
- Q2: >0 open sec issues + age unknown → amber or red. Assume amber per comparator. **MATCH.**
- Q3: SECURITY.md present + 0 published advisories → **compute AMBER**, comparator **GREEN**. **MISMATCH.**
- Q4: F0 Critical on default path → red. **MATCH.**

---

## 9. The design question

**Where should scorecard cell color authority live?**

### Canonical options

- **Option A — Adjust compute.py calibration to match V2.4 LLM judgments.** Make compute.py softer / context-aware (Q3 "contributing guide OR policy" = amber; Q4 distinguish install-surface from governance; Q1 tighter red on low formal rates; Q2 downgrade green→amber on visible merge friction). **Pro:** aligns 8 automatable ops with catalog reality; Step G proceeds. **Con:** compute.py becomes codification of current-V2.4-LLM-judgment, not independent signal.
- **Option B — Declare compute.py correct; V2.4 LLM was too lenient.** Re-author V2.4 comparator scorecards to match compute.py. **Pro:** deterministic, regression-testable. **Con:** second catalog harmonization (after U-10); arguably V2.4's softer judgments are more user-correct.
- **Option C — Schema split V1.1 → V1.2.** Move scorecard cells OUT of `phase_3_computed` INTO `phase_4_structured_llm.scorecard_cells` (enum color + required rationale per cell). compute.py keeps the other 7 ops. **Pro:** acknowledges cells are judgments not computations. **Con:** schema change; multi-commit; Step G can't resume on V1.1.

### Open scope — propose a 4th/5th option if none fit

You are not restricted to A/B/C. If you see a cleaner resolution (e.g., "apply A to 2 questions but C to the other 2"; "redefine the canonical questions"; "Step G keeps running but drops gate 6.3 to informational"; "gate 6.3 becomes a diff-inspection step, not a must-match"; "per-cell rationale in compute.py with explicit LLM override hook"), propose it and argue for it.

---

## 10. Required output format

Structure your response exactly like this:

```
# SF1 R1 — [Your agent name]

## Vote

Preferred resolution: [A / B / C / propose-new — label]

## Rationale

[2–6 sentences. What matters most about this decision? What would you want the project to look like 6 months from now?]

## Resolution details

If A: which calibration changes exactly, per Q.
If B: what's the re-authoring standard for the catalog.
If C: sketch the schema shape (what replaces `phase_3_computed.scorecard_cells`).
If new: describe the proposal concretely enough to implement.

## FIX NOW items

[Things that block the resolution itself. Zero is fine. Each item: short title + 1 sentence.]

## DEFER items

[Useful but non-blocking. Zero is fine.]

## INFO items

[Anything else worth noting. Blind spots, assumptions you couldn't verify, context that would change your vote.]

## Blind spots

[Things YOU might have missed or that a stronger reviewer would catch in you. Be honest.]
```

---

## 11. Meta-context (non-voting info)

- **Step G is HALTED, not failed.** Operator Guide §8.8 remains canonical. Zero authoring artifacts exist. Pre-flight Steps -2/-1/0 passed (commit `9840cdf`).
- **compute.py lines 78–180 are the only section under consideration.** The other 7 compute functions are not in scope for SF1.
- **11 V2.4 catalog scans exist** across 7 shapes. Re-harmonization (Option B) touches all 11 MD files' scorecard sections.
- **U-10 was a prior catalog harmonization** (backward-align to V2.3 canonical questions). A second harmonization pass is tolerable but not trivial.
- **Schema version V1.1 is current.** V1.2 has no draft yet. Option C implies schema PR + renderer rewrite + test-fixture regeneration.
- **The user is the sole owner** of this project. Board is advisory; owner makes the final call. Your job is to make the strongest case for your vote so the owner has a real choice.
