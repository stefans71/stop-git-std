# SF1 Board Review — Consolidation (Canonical Record)

**Review type:** Design decision — scorecard-cell authority between `docs/compute.py` and V2.4 LLM comparator MDs.
**Surfaced during:** Step G pre-pilot compute-driver dry-run, 2026-04-20.
**Rounds:** 4 (R1 Blind → R2 Consolidation on hybrid → R3 Confirmation → R4 narrow tiebreaker on Tension 1).
**Board:** Pragmatist (Claude Sonnet 4.6) · Systems Thinker (Codex GPT-5) · Skeptic (DeepSeek V4).
**Finding doc:** [FINDING-SF1.md](FINDING-SF1.md) — root-cause document.
**Outcome:** Resolved. Step G is UNBLOCKED subject to Phase 1 execution.

---

## 1. The question

Step G's compute-driver dry-run surfaced 5 scorecard cell mismatches across the 3 comparator targets (zustand-v3 Q3+Q4, caveman Q2, Archon Q1+Q3) between `docs/compute.py` output and the V2.4 catalog comparator MDs. §8.8.3 Step 3b (compute.py byte-for-byte authoritative) and §8.8.5 gate 6.3 (scorecard cell-by-cell match V2.4 comparator) are mutually exclusive under current state. Step G halted per §8.8.6 ambiguity rule.

**The design question:** Where should scorecard cell color authority live?

---

## 2. R1 votes (Blind)

| Agent | Vote | Summary |
|---|---|---|
| Pragmatist | **Option A** | 5 targeted compute.py patches, 4 new input params, V1.1 unchanged, Step G resumes fastest |
| Systems Thinker | **New "D"** | Option C target architecture + interim bridge (scorecard compute becomes advisory; gate 6.3 → discrepancy-review; V1.2 formal migration later) |
| Skeptic | **C+** | Go further than C — LLM judgment with `edge_case` + `suggested_threshold_adjustment` feedback loop |

**Option B (re-harmonize 11 catalog scans to match compute.py) received zero support.**

## 3. R2 votes on synthesized hybrid "A-now + C-for-V1.2 + edge_case"

| Agent | Verdict | Modifications |
|---|---|---|
| Pragmatist | **ACCEPT** | Implementation clarifications: Gate A (`additionalProperties` check), Gate B emphasis (F0 hard gate); D-7 trigger should require shape diversity + 6-month time fallback |
| Systems Thinker | **ACCEPT-WITH-MODS** | D-7 committed not conditional; two-part trigger (first new repo shape OR 3 live scans); Phase 1 patches annotated "temporary compatibility" |
| Skeptic | **ACCEPT-WITH-MODS** | Gate C (Archon Q3 ground-truth audit); stricter V1.2 trigger (any cell semantic drift); explicit premise that V2.4 = canonical-for-validation-only, not ground truth |

## 4. R3 votes on frozen hybrid (all R2 mods integrated)

| Agent | Verdict | Tension 1 (Archon Q3) | Tension 2 (D-7 trigger) | Dissent audit |
|---|---|---|---|---|
| Pragmatist | **CONFIRM** | A-CANONICAL | UNION-ACCEPT | ☑ Clean |
| Systems Thinker | **CONFIRM** | G-C-ACCEPT | UNION-ACCEPT | ☑ Clean |
| Skeptic | **CONFIRM** | D-CANONICAL | UNION-ACCEPT | ☑ Clean |

**R3 convergences:** 3/3 CONFIRM the hybrid direction · 3/3 UNION-ACCEPT on D-7 trigger · 3/3 attest dissent audit clean. **Tension 1 split 1-1-1.**

## 5. R4 votes on narrow Tension 1 (with live-verified Archon evidence)

| Agent | R3 vote | R4 vote | Movement |
|---|---|---|---|
| Pragmatist | A-CANONICAL | **G-C-ACCEPT** | **Changed** — §7 output analysis unsettled R3 load-bearing assumption |
| Systems Thinker | G-C-ACCEPT | **G-C-ACCEPT** | Held |
| Skeptic | D-CANONICAL | **D-CANONICAL** | Held |

**R4 outcome: 2-1 majority G-C-ACCEPT.** DeepSeek dissent recorded in §9 below.

---

## 6. Final resolution (archival-canonical)

### Phase 1 — Unblock Step G on V1.1

**Three hard pre-patch gates. All three execute before any patch applies.**

**Gate A — Schema `additionalProperties` check** (Pragmatist R2 FIX NOW #1):
Confirm `phase_1_raw_capture` schema `additionalProperties` setting in `docs/scan-schema.json`. If `false`, change to `true` for that block only; document in schema changelog without version bump. Ensures the new input fields don't trigger V1.1 validation errors.

**Gate B — zustand-v3 F0 Warning type verification** (Pragmatist R1 blind-spot #4, R2 FIX NOW #2):
Look up what F0 is for zustand-v3. If install-path → DO NOT apply the Q4 split; compute.py is correct; adjust gate 6.3 for Q4 zustand (accept as LLM-overshoot case, single-cell catalog note). If governance/meta → apply Q4 split as planned.

**Gate C — Archon Q3 ground-truth audit** (majority R4 = G-C-ACCEPT; Pragmatist R4 5-step criteria below):

1. Read diff and commit messages for PRs #1169 and #1217 specifically. Determine whether either addressed a security vulnerability (as opposed to general hardening, code quality, or architecture). Flag language: "fix", "patch", "CVE", "vulnerability", "injection", "auth bypass", similar.
2. Open issues F1 (Codex LPE), F2 (web-dist), F3 (axios CVE) are OPEN, not fixed — they do NOT count toward `has_reported_fixed_vulns` but confirm security posture.
3. **If `has_reported_fixed_vulns = FALSE`** (no prior security fixes found): apply A-CANONICAL patch; Archon Q3 → green. V2.4 comparator Q3 stays green; gate 6.3 passes.
4. **If `has_reported_fixed_vulns = TRUE`** (prior security fixes found, no GHSA published): skip patch (D-CANONICAL outcome); Archon Q3 → amber. V2.4 comparator Q3 requires single-cell catalog correction (green → amber, tagged U-11); gate 6.3 passes on corrected cell.
5. **If ambiguous** (e.g., #1169 is a security refactor but operator cannot determine if it fixed a reportable vuln): default to amber (strict reading), log reasoning in Phase 1 bundle, flag for human review before catalog publication.

**The 5 patches (subject to gate outcomes):**

- **Q3 zustand-v3:** Add `has_contributing_guide: bool` input; amber floor = `has_security_policy OR has_contributing_guide OR (published_advisory_count > 0 AND NOT has_silent_fixes)`.
- **Q4 zustand-v3 (Gate B dependent):** Rename/split `has_warning_or_above` → `has_warning_on_install_path: bool`; use in Q4 instead of general warning flag.
- **Q2 caveman:** Add `closed_fix_lag_days: int | None`. Green requires `closed_fix_lag_days <= 3` when `open == 0 AND cve_age <= 7`; >3 days → amber. Fallback clause preserved: if `closed_fix_lag_days` is not cleanly derivable from Phase 1 data, accept compute.py's literal-rubric green and adjust gate 6.3 for that single cell (Pragmatist R1 INFO #4).
- **Q1 Archon:** Governance-floor override — `formal<10% AND NOT has_branch_protection AND NOT has_codeowners` forces red regardless of any-review threshold. (Acknowledged as judgment-baked-into-Phase-3; in D-7 V1.2 migration scope.)
- **Q3 Archon (Gate C dependent):** Add `has_reported_fixed_vulns: bool`; `has_security_policy AND (published_advisory_count > 0 OR NOT has_reported_fixed_vulns)` = green; else amber.

**Annotation (Codex R2 mod #3):** All 5 patches are explicitly annotated in code comments and commit message as "**temporary compatibility calibration for V1.1 Step G acceptance. Scorecard-cell authority migration to V1.2 (D-7) is the durable fix.**"

**Gate D — Validation:** Update the 3 Step G fixture forms with new inputs (from already-captured Phase 1 data); re-run compute-driver dry-run; confirm all applicable cells now match V2.4 comparator; Step G resumes authoring under §8.8.

### Phase 2 — D-7 committed architecture work (post-Step-G)

**D-7 is COMMITTED, not conditional** (Codex R2 mod #1). The question is timing and urgency, not whether it happens.

**D-7 trigger — disjunctive union (R3 3/3 UNION-ACCEPT; whichever fires first):**

1. **Scope-expansion trigger** (Codex R2): First V2.5-preview scan on a repo shape NOT in the current 7 catalog shapes (JS library, CLI binary, agentic platform, curl-pipe installer, Claude Code skills, tiny, web app) → D-7 starts.
2. **Volume trigger** (Codex + Pragmatist independent convergence): 3 live V2.5-preview scans post-Step-G with AT LEAST 2 different shape categories represented → D-7 starts.
3. **Time fallback** (Pragmatist R2): 6 months post-Step-G, regardless of scan volume → D-7 starts.
4. **Semantic-drift trigger** (DeepSeek R2): Any cell diverges from V2.4-equivalent-judgment for semantic (not threshold-calibration) reasons → D-7 starts with HIGH urgency. Definition of semantic-not-threshold: a cell where the LLM's Phase-4 judgment differs from compute.py's output AND the Phase-1 patch for that question type doesn't explain the difference.

**V1.2 schema sketch (approved now, implemented after trigger):**

```json
"phase_4_structured_llm": {
  "scorecard_cells": [
    {
      "question": "Does anyone check the code? | Do they fix problems quickly? | Do they tell you about problems? | Is it safe out of the box?",
      "color": "red | amber | green",
      "short_answer": "string",
      "rationale": "string — must cite E-IDs",
      "edge_case": true,
      "suggested_threshold_adjustment": "optional string — feedback loop",
      "computed_signal_refs": ["list of compute.py advisory signals considered"]
    }
  ]
}
```

**When V1.2 lands:**
- `compute_scorecard_cells()` demoted from authoritative to advisory; output surfaces as `phase_3_advisory.scorecard_hints` for LLM to consult.
- Gate 6.3 changes from "cell-by-cell match" to "cells present + rationale cites evidence + LLM override of advisory hint explained in `rationale` AND `edge_case=true`."
- Step 3b byte-for-byte requirement RETAINED for the other 7 Phase 3 operations (verdict, solo-maintainer, exhibit, boundary, coverage, methodology, F5). Scorecard cells are the ONLY operation moved out.
- Q1 Archon governance-floor override (Pragmatist R2 blind-spot #3) is in D-7's migration scope.
- Post-V1.2 override-pattern telemetry added (Codex R1 DEFER).

### Phase 3 — Catalog harmonization rejected

Option B (re-authoring 11 V2.4 catalog MDs to match compute.py strict thresholds) explicitly NOT pursued. All 3 agents voted against it.

### Meta premise statement (DeepSeek R2 mod #3)

V2.4 catalog scans are canonical for Step G validation purposes only. V2.4 is NOT claimed as absolute ground truth — it is LLM output, not human-reviewed gold standard. V1.2 post-D-7 establishes proper validation baselines with per-cell rationale + evidence refs.

---

## 7. D-7 ledger entry (verbatim for `docs/SCANNER-OPERATOR-GUIDE.md`)

> **D-7 — Scorecard cell authority-boundary migration (V1.1 → V1.2).** Move scorecard cell colors out of `phase_3_computed.scorecard_cells` into `phase_4_structured_llm.scorecard_cells` with structured-constraint fields (`question`, `color` enum, `short_answer`, `rationale` citing E-IDs, `edge_case` bool, `suggested_threshold_adjustment` optional, `computed_signal_refs`). Demote `compute.py::compute_scorecard_cells()` to advisory — output surfaces as `phase_3_advisory.scorecard_hints` for Phase-4 LLM to consult. Gate 6.3 changes from "cell-by-cell match" to "cells present + rationale cites evidence + LLM override of advisory hint explained." Step 3b byte-for-byte requirement retained for the other 7 Phase 3 operations.
>
> **Trigger** (disjunctive; whichever fires first):
> 1. First V2.5-preview scan on a repo shape NOT in the current 7 catalog shapes.
> 2. 3 live V2.5-preview scans post-Step-G with at least 2 different shape categories.
> 3. 6 months post-Step-G, regardless of scan volume.
> 4. Any cell diverges from V2.4-equivalent-judgment for semantic (not threshold-calibration) reasons; such divergence accelerates urgency.
>
> **Committed, not conditional.** Low observed drift does not cancel D-7 — it only determines urgency/scope.
>
> **Rider items:** 11-scan comparator analysis; override-pattern telemetry; canonical question wording review; rubric literal-vs-intent documentation for Q3 (DeepSeek R4 disobedience concern); Q1 Archon governance-floor revisit (whether the override belongs in Phase 4 or stays as a deterministic rule).

---

## 8. FIX NOW synthesized (final ordered list)

1. **Gate A** — Schema `additionalProperties` check on `phase_1_raw_capture` block; flip to `true` if needed; schema changelog note (no version bump).
2. **Gate B** — Look up zustand-v3 F0 type; decide Q4 split applicability.
3. **Gate C** — Archon Q3 ground-truth audit per 5-step criteria in §6.
4. **Apply 5 patches** to `docs/compute.py` subject to gate outcomes; annotate as temporary compatibility calibration in code comments.
5. **Update the 3 Step G fixture forms** with new input values from already-captured Phase 1 data.
6. **Re-run compute-driver dry-run**; confirm all applicable cells match V2.4 comparator; any residual mismatch resolved per gate outcomes.
7. **Add D-7 to `docs/SCANNER-OPERATOR-GUIDE.md` deferred ledger** per §7 above.
8. **Update commit message** for Phase 1 patches to include the meta premise statement: "V1.1 scorecard cells are temporary compatibility calibration for Step G acceptance; V1.2 (D-7) migrates scorecard authority to Phase 4 structured LLM judgment."
9. **Optional:** Add preamble to `docs/compute.py` module docstring stating the same (Pragmatist R3 INFO #2).

---

## 9. Minority dissent preserved (DeepSeek R4 D-CANONICAL)

The Skeptic argued Archon Q3 should be D-CANONICAL (skip patch, compute.py amber correct, catalog correction), not G-C-ACCEPT. Key argument preserved verbatim:

> The internal inconsistency in the V2.4 comparator MD strengthens my R3 position: the LLM flagged "⚠ 0 published" in the Disclosure section while giving green in the Trust Scorecard, demonstrating it recognized the rubric conflict but chose leniency. This is textbook LLM disobedience — seeing the requirement, acknowledging the gap, then overriding it. The rubric's explicit amber definition for "SECURITY.md with private channel BUT no published advisories" is unambiguous. A brand-new SECURITY.md with zero vulns is precisely the case the rubric's amber category was designed to capture — it's not a bug, it's the intended calibration.

The majority position (G-C-ACCEPT) does not refute this reading — it defers the choice to Gate C on empirical grounds (whether Archon's PRs #1169/#1217 were vuln-remediation). If Gate C finds they were: the D-CANONICAL outcome applies (Skeptic's reading carries). If Gate C finds they were not: A-CANONICAL outcome applies (Pragmatist's reading carries). The Skeptic's rubric-literalism argument survives into D-7 as a rider item for V1.2 "rubric literal-vs-intent documentation for Q3."

---

## 10. Dissent audit — CLEAN

Pre-archive audit confirms: every R1 and R2 dissent from every agent is either (a) integrated into the frozen hybrid, (b) resolved by an R2 modification the objecting agent signed off on, or (c) explicitly carried forward as a D-7 rider. Three R3 attestations (Pragmatist, Codex, DeepSeek) all checked "All addressed or carried forward." Zero silent drops.

---

## 11. Artifacts

- **[FINDING-SF1.md](FINDING-SF1.md)** — root-cause document from 2026-04-20
- **R1:** [r1-brief.md](r1-brief.md) · [pragmatist-r1.md](pragmatist-r1.md) · [codex-r1.md](codex-r1.md) · [deepseek-r1.md](deepseek-r1.md)
- **R2:** [r2-brief.md](r2-brief.md) · [pragmatist-r2.md](pragmatist-r2.md) · [codex-r2.md](codex-r2.md) · [deepseek-r2.md](deepseek-r2.md)
- **R3:** [r3-brief.md](r3-brief.md) · [pragmatist-r3.md](pragmatist-r3.md) · [codex-r3.md](codex-r3.md) · [deepseek-r3.md](deepseek-r3.md)
- **R4:** [r4-brief.md](r4-brief.md) · [pragmatist-r4.md](pragmatist-r4.md) · [codex-r4.md](codex-r4.md) · [deepseek-r4.md](deepseek-r4.md)

---

## 12. Timing

- Authored: 2026-04-20
- R1: ~3 min (parallel)
- R2: ~4 min (parallel)
- R3: ~4 min (parallel)
- R4: ~3 min (parallel)
- Total elapsed: ~30 min (board time) + authoring/consolidation time

## 13. Process notes

- Pragmatist ran as Sonnet 4.6 (same-model blind-spot rule: Opus 4.7 authored the SF1 finding doc).
- Pragmatist changed vote R3 → R4 (A-CANONICAL → G-C-ACCEPT) based on R4 §7 evidence. Good signal that the stateless-with-new-evidence cycle works.
- 3 distinct votes in R3 (A-CANONICAL / G-C-ACCEPT / D-CANONICAL) narrowed to 2-1 majority in R4 via additional Archon-specific evidence (live `gh api` verification + comparator internal inconsistency observation).
- DeepSeek V4 via Qwen CLI (`qwen -y --model deepseek-chat`) ran reliably across all 4 rounds.
- Codex GPT-5 via `sudo -u llmuser codex exec --dangerously-bypass-approvals-and-sandbox` from `/tmp` ran reliably across all 4 rounds.

---

**Status:** Ready for execution. Phase 1 begins with Gate A.
