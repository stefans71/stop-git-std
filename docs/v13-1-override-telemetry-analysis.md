# V13-1 Override-Pattern Telemetry Analysis

**Trigger:** 3 V1.2 wild scans completed (ghostty entry 16, Kronos entry 17, kamal entry 18).
**Date:** 2026-04-20
**Status:** Draft for owner decision (board-review fallback preserved in §6).
**Related:** `docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` §5 (R3 Item C — override_reason enum frozen at 5 values); §8 V13-1 (expansion trigger = ≥3 V1.2 scans).

---

## §1 · Context

Schema V1.2 introduced **gate 6.3 override-explained** with a 5-value `override_reason` enum:

1. `threshold_too_strict` — compute threshold is too conservative for this repo
2. `threshold_too_lenient` — compute threshold is too permissive for this repo
3. `missing_qualitative_context` — compute signals don't capture qualitative nuance
4. `rubric_literal_vs_intent` — compute follows rubric literal, Phase 4 reads intent
5. `other` — catchall

The enum was frozen in R3 Item C per CONSOLIDATION §5, with DeepSeek's dissent preserving `community_norms_differ` as a V1.3 expansion trigger (needs ≥3 observed overrides). **That expansion trigger has now fired.**

CONSOLIDATION §8 V13-1 also tasked the operator with reviewing the override-reason distribution after 3 V1.2 scans to determine whether the current enum is load-bearing or whether any values should be split / dropped / added.

This document is that review.

---

## §2 · Data — 4 overrides across 12 scorecard cells

| # | Scan (entry) | Cell | Advisory → Phase 4 | Direction | Signal refs | `override_reason` |
|---|---|---|---|---|---|---|
| 1 | ghostty (16) | Q1 | red → amber | de-escalate | 7 | `missing_qualitative_context` |
| 2 | Kronos (17) | Q2 | amber → red | escalate | 5 | `missing_qualitative_context` |
| 3 | Kronos (17) | Q4 | amber → red | escalate | 5 | `missing_qualitative_context` |
| 4 | kamal (18) | Q1 | red → amber | de-escalate | 9 | `missing_qualitative_context` |

**Pattern observations:**

- **4 of 4 overrides cite `missing_qualitative_context`** (100%).
- **4 of 5 enum values are unexercised**: `threshold_too_strict`, `threshold_too_lenient`, `rubric_literal_vs_intent`, `other`.
- **Override distribution across cells**: Q1 = 2 (both de-escalate), Q2 = 1 (escalate), Q4 = 1 (escalate), Q3 = 0.
- **Override rate**: 4 / 12 cells = 33% — not rare; the gate 6.3 path is actively used.
- **Direction split**: 2 de-escalations (ruleset-invisibility on Q1) + 2 escalations (sparse compute signals on Kronos Q2/Q4).

---

## §3 · Root-cause analysis — what each override's rationale actually says

Reading the Phase 4 `rationale` fields on each of the 4 overrides, the underlying cause separates into three distinct surfaces:

### 3.1 Ghostty Q1 — de-escalate red → amber
- **Signal at fault:** `q1_has_branch_protection` reads only `classic.status == 200`.
- **Evidence missed by compute:** `branch_protection.rulesets.count=1` + `branch_protection.rules_on_default.count=4` + CODEOWNERS present — all captured in phase_1_raw_capture.
- **Fix surface:** `docs/compute.py` — widen `q1_has_branch_protection` to also fire when `rulesets.count > 0 AND rules_on_default.count > 0`, OR add a new signal `q1_has_ruleset_protection` that reads the ruleset fields.
- **Classification:** **Signal vocabulary gap.** The concept exists (branch protection); the signal's definition is narrower than the concept.

### 3.2 Kamal Q1 — de-escalate red → amber
- **Signal at fault:** Same as ghostty Q1 — `q1_has_branch_protection` misses the Copilot Reviews ruleset.
- **Additional evidence not encoded as any signal:** 71 semver releases over 3 years (release-cadence discipline); CodeQL SAST workflow enabled; dependabot-for-actions config.
- **Fix surface:** `docs/compute.py` — same ruleset fix as ghostty Q1, plus optionally add `q1_has_codeql_workflow` and `q1_has_semver_release_cadence` signals.
- **Classification:** **Signal vocabulary gap.** Same root cause as ghostty Q1; three additional concepts (CodeQL, release cadence, dependabot-for-actions) also lack signals.

### 3.3 Kronos Q2 — escalate amber → red
- **Signal at fault:** `q2_oldest_open_cve_pr_age_days` reads only from PRs tagged with CVE-related labels or security-prefix titles. Returned `None` for Kronos because the unfixed 95-day-old RCE is an *issue* (#216), not a PR.
- **Evidence missed by compute:** Issue #216 body contains "pickle.load" + "remote code execution"; issue is 95 days open; separate fix PR #249 has been sitting 7 days unreviewed.
- **Fix surface:** `docs/compute.py` — widen the signal's input domain. Either rename to `q2_oldest_open_security_item_age_days` reading both issues and PRs with security-keyword title/body matches, or add a sibling signal `q2_oldest_open_security_issue_age_days`. Also add `q2_open_security_fix_pr_age_days` reading PRs whose titles match fix+security keywords.
- **Classification:** **Signal vocabulary gap** (signal domain is too narrow for the concept it claims to measure). The evidence is present in `phase_1_raw_capture.issues_and_commits`; no harness change needed.

### 3.4 Kronos Q4 — escalate amber → red
- **Signal at fault:** `q4_has_critical_on_default_path` derived from `code_patterns.dangerous_primitives.deserialization.hits`. Returned `False` for Kronos because the harness's deserialization regex family did not match `pickle.load` at `finetune/dataset.py:42`.
- **Evidence missed by harness:** `pickle.load` exists at `finetune/dataset.py:42` — confirmed by direct `gh api contents` fetch during scan authoring. The dangerous_primitives regex for the `deserialization` family did not include a pattern that matches `pickle.load` in Python source (or the tarball extraction skipped `finetune/`).
- **Fix surface:** `docs/phase_1_harness.py` — extend the `deserialization` family regex to include `\bpickle\.loads?\b`, `\bmarshal\.loads?\b`, `\byaml\.load\b` (without SafeLoader), `\bjoblib\.load\b`, etc. Alternative fix at compute.py: add a fallback signal `q4_has_critical_issue_disclosed` that title-matches `open_security_issues` for RCE/deserialization/injection keywords.
- **Classification:** **Harness coverage gap.** The evidence IS observable but phase_1_harness.py's pattern-matching code didn't capture it. Even a correctly-scoped compute signal reading from `dangerous_primitives.deserialization.hits` would see the empty list.

### 3.5 Summary of root causes

| Override | Fix surface | Classification |
|---|---|---|
| Ghostty Q1 | compute.py | Signal vocabulary gap |
| Kamal Q1 | compute.py | Signal vocabulary gap |
| Kronos Q2 | compute.py | Signal vocabulary gap (domain too narrow) |
| Kronos Q4 | phase_1_harness.py | Harness coverage gap |

**3 of 4 overrides point to compute.py changes. 1 of 4 points to harness changes.** Both surfaces are fixable — the evidence is observable in every case — but they live in different files and are maintained on different cadences.

---

## §4 · Proposed taxonomy

### 4.1 User's proposed 2-way split
- `signal_vocabulary_gap` — ruleset-invisibility pattern
- `evidence_not_signalable` — sparse-signal-escalation pattern

### 4.2 Alternative 3-way split (recommended)

Expand the enum by adding 2 new values; keep `missing_qualitative_context` for genuinely-judgment cases that don't reduce to a signal change:

1. **`signal_vocabulary_gap`** — compute needs a new or widened signal. The concept or its relevant domain isn't currently read. Fix lives in `docs/compute.py` + `SIGNAL_IDS` frozenset.
2. **`harness_coverage_gap`** — phase_1_raw_capture didn't record the evidence. Even a correctly-scoped compute signal would see nothing. Fix lives in `docs/phase_1_harness.py`.
3. **`missing_qualitative_context`** (retained) — evidence is inherently judgment-based, cannot be reduced to a signal. Expected to be rare; acts as the honest catchall.

Plus keep the existing 3 unused enum values (`threshold_too_strict`, `threshold_too_lenient`, `rubric_literal_vs_intent`, `other`) — they cover distinct conceptual gaps not yet observed but anticipated.

### 4.3 Why 3-way beats 2-way

The user's 2-way split works well for the de-escalation pattern (both ghostty Q1 and kamal Q1 are `signal_vocabulary_gap` — ruleset invisibility). But it strains on Kronos:

- **Kronos Q2**: the signal EXISTS (`q2_oldest_open_cve_pr_age_days`) but its domain is too narrow (PRs only, not issues). Is that `signal_vocabulary_gap` (the domain is part of the vocabulary)? Or `evidence_not_signalable` (evidence was available but not read)? Both labels fit partially.
- **Kronos Q4**: the evidence was *not* in phase_1_raw_capture in the expected form (dangerous_primitives empty). Calling this `evidence_not_signalable` conflates it with Kronos Q2 even though the fix surface is completely different (harness regex vs compute signal widening).

The 3-way split resolves the ambiguity by classifying on **fix surface**, not on severity direction:
- If the fix is in `compute.py`: `signal_vocabulary_gap`.
- If the fix is in `phase_1_harness.py`: `harness_coverage_gap`.
- If no code change would avoid the override: `missing_qualitative_context`.

This mapping is mechanically decidable at override-authoring time ("where would I patch this?") and points the reader of the audit log at the right file to change.

### 4.4 Migration mapping under 3-way split

| Override | Current label | Proposed label |
|---|---|---|
| Ghostty Q1 | `missing_qualitative_context` | `signal_vocabulary_gap` |
| Kamal Q1 | `missing_qualitative_context` | `signal_vocabulary_gap` |
| Kronos Q2 | `missing_qualitative_context` | `signal_vocabulary_gap` |
| Kronos Q4 | `missing_qualitative_context` | `harness_coverage_gap` |

**3 of 4 overrides relabel to `signal_vocabulary_gap` (compute.py fix). 1 relabels to `harness_coverage_gap` (harness fix).** The migration is 100% mechanical per §3's fix-surface analysis.

---

## §5 · Implementation cost

### 5.1 Schema + compute + validator
- `docs/scan-schema.json` — `override_reason_enum.enum` adds 2 strings; no structural change.
- `docs/compute.py` — `OVERRIDE_REASON_ENUM` frozenset adds 2 entries (currently 5, becomes 7).
- `docs/validate-scanner-report.py` — **no change**. The `validate_override_rationale` function reads the enum from compute.py; the validation logic is enum-agnostic.

### 5.2 Tests
- `tests/test_validator_v12_override.py::TestSignalIDVocabulary::test_override_reason_enum_is_exactly_the_5_values` — rename + widen to assert 7 values.
- Add two tests that validate a form with each new enum value passes gate 6.3.

### 5.3 Existing scan relabeling
- `docs/board-review-data/scan-bundles/{ghostty-dcc39dc.json, Archon-3dedc22.json, kamal-6a31d14.json, Kronos-67b630e.json}` — relabel `phase_4_structured_llm.scorecard_cells.<cell>.override_reason` where currently `missing_qualitative_context`.
- `docs/GitHub-Scanner-{ghostty,Kronos,kamal}-v12.{md,html}` — rerender from updated form.json to pick up relabeled overrides (or leave stale with catalog note; rerendering is cleaner).
- `docs/scanner-catalog.md` — update the relevant entry rows' `override_reason = missing_qualitative_context` prose to the new label.

Total: ~10 files changed, ~50 lines of change, one compute.py patch + tests + rerender.

### 5.4 Risk
- **Backwards compatibility**: additive enum change; any existing form.json with `missing_qualitative_context` continues to validate under 7-value enum.
- **Audit-log readability**: improves — `signal_vocabulary_gap` and `harness_coverage_gap` are self-describing; the 4 existing overrides become more informative.
- **Documentation**: CONSOLIDATION.md §5 R3 Item C resolution needs a post-it note saying "7-value enum as of V13-1 analysis"; CONSOLIDATION §8 V13-1 entry needs resolution recording.

---

## §6 · Decision — board review or owner directive?

### 6.1 Arguments for board review
- **Enum changes are contract changes**: scan-schema.json's `override_reason_enum` is part of the V1.2 contract. Contract changes traditionally route through board.
- **The 5-value enum was frozen per board resolution** (R3 Item C, 3/3 SIGN OFF). Reopening it without board assent feels like overriding a closed decision.
- **DeepSeek's preserved dissent** named `community_norms_differ` as a V1.3 candidate. A board review would surface whether DeepSeek sees `signal_vocabulary_gap` and `harness_coverage_gap` as the right additions or still wants its original candidate.
- **External defensibility**: "3 agents + owner resolved this" is a stronger audit trail than "operator decided" for anything anyone might later question.

### 6.2 Arguments for owner directive
- **CONSOLIDATION §8 V13-1 was pre-scheduled for exactly this question.** The deferred ledger's triggers are meant to convert deferred debate into telemetry-driven decisions. V13-1 firing is the board's pre-approved hand-off point.
- **The data is unambiguous**: 4 overrides, all cite the same reason, each one has a cleanly-distinguishable root cause mapped to a fix surface. The analysis in §3 is mechanical, not judgmental.
- **The fix is additive**. No existing override becomes invalid; schema validity is preserved under both 5-value and 7-value enums.
- **Cost of a board review is disproportionate**: a 3-round board review averages 1.5–2 hours of operator orchestration + 3 agent invocations. This question can be answered in 30 minutes of code + rerender.
- **Escalation is always available**: if the owner-directed implementation surfaces ambiguity that wasn't visible at analysis time (e.g., an override in scan #4 that genuinely fits neither new label), the decision can be revisited via board.

### 6.3 Recommendation: **owner directive, implemented now**, with three explicit escalation triggers

Proceed with the 3-way split (add `signal_vocabulary_gap` + `harness_coverage_gap`; retain `missing_qualitative_context` as catchall).

**Escalate to board review if ANY of the following occur between now and the next board session:**

1. A wild-scan override appears that fits **none** of the 3 labels cleanly — indicates the taxonomy is still undercomplete.
2. A wild-scan override fits **multiple** labels and the author genuinely cannot choose — indicates the taxonomy has overlap.
3. DeepSeek (or any future Skeptic agent) flags the relabeling in a post-hoc review as inconsistent with its original R3 dissent.

Otherwise: implement, document in CONSOLIDATION §8 V13-1 with the "resolved by owner directive 2026-04-20" stamp, preserve this analysis document as the rationale.

### 6.4 Reasoning

The R3 board left two explicit legs for future evolution:
- **V13-1 as a scheduled telemetry review** (CONSOLIDATION §8) — designed to be owner-driven.
- **Board re-open on data surprise** — implicit in the overall governance pattern.

We are in the first leg, not the second. The data confirms the hypothesis the board anticipated (the enum might need expansion); nothing in the data contradicts any board position. Owner directive is the lighter-weight path that honors both legs.

---

## §7 · Implementation plan (if owner directive approved)

1. **Update schema**: add 2 strings to `override_reason_enum.enum` in `docs/scan-schema.json`.
2. **Update compute**: add 2 entries to `OVERRIDE_REASON_ENUM` in `docs/compute.py`.
3. **Update tests**: widen `test_override_reason_enum_is_exactly_the_5_values` to 7; add 2 positive tests for new labels.
4. **Relabel existing overrides**: patch the 4 scan bundles in `docs/board-review-data/scan-bundles/` + re-render the 3 affected reports (ghostty / Kronos / kamal — Archon has no override per catalog entry 14).
5. **Update scanner-catalog.md**: fix the override-reason prose in entries 16/17/18.
6. **Update CONSOLIDATION.md**: append a resolution note to §8 V13-1.
7. **Single commit** with all changes. Push.

Estimated scope: ~15 minutes for code + rerender, ~15 minutes for doc updates.

### §7.1 Decision point (for owner)

**Approve implementation as outlined?** If yes, proceed to code. If ambiguous on any point, convert to board kickoff by moving this document to `docs/External-Board-Reviews/042026-v13-1-override-taxonomy/` and running the standard 3-round FrontierBoard review.

---

*Draft prepared 2026-04-20. Author: Claude Opus 4.7 via Claude Code session 6. Reviewed no-one yet.*
