# Pragmatist R2 — Calibration Rebuild Design Review (Consolidation)

**Role:** Pragmatist (Claude Sonnet 4.6)
**Round:** R2 (Consolidation)
**Date:** 2026-05-01

---

## §1 Topline (under 150 words)

SIGN OFF WITH NOTES. The 8 owner directives resolved my two main R1 concerns: the Q9 floor is now staged and achievable with firm rules alone (≤5/12 hard), and the template-map fallback is explicitly specified. RULE-3 was narrowed with positive-signal triggers and parenthesized for clarity — the operator-precedence bug is gone. The Phase 4 fallback in `classify_shape()` was dropped (Codex's FIX-NOW). My surviving concern is in the provisioning of the staged-promotion mechanism: when the ≤3/12 stretch auto-promotes to a hard floor mid-cycle (after ≥2 of V12x-7/11/12 land), that triggers a re-validation requirement on previously-passing scans that the design does not acknowledge. Additionally, the `confidence` field on `ShapeClassification` still has no behavioral consequence — it is defined but unused in the rule evaluation path.

---

## §2 R1-concern resolution table

| R1 concern | Status | Revised section |
|---|---|---|
| Q9 hard floor (≤3/12) unachievable with firm rules — Phase 3 structurally blocked | **RESOLVED** | §9 Q9 revised: ≤5/12 hard floor + ≤3/12 staged stretch tied to ≥2 harness signal landings |
| Template-map fallback unspecified (no-rule-fired case) | **RESOLVED** | §6 template-map fallback: fall back to LLM-authored short_answer; validator warns on miss; errors only when both miss + empty short_answer |
| RULE-3 operator-precedence ambiguity + n=2 marginal evidence | **PARTIALLY RESOLVED** | §5 RULE-3 rewritten with explicit parentheses and positive-signal trigger (`has_codeql OR releases_count >= 20`). Confidence raised to firm. Not pruned — owner elected keep with narrow rewrite. The pattern is now well-specified; marginal-evidence concern is mitigated by the positive-signal gate. |
| `classify_shape()` no conflict-resolution path (first-match-wins not named) | **RESOLVED** | §2 rule precedence contract added: first-match-wins in priority order, auto-fire short-circuits |
| V12x harness work dependency not surfaced in Phase 3 plan | **PARTIALLY RESOLVED** | §9 Q9 explicitly ties stretch-target promotion to V12x-7/11/12 landing. But Phase 3 implementation treatment of RULE-7/8/9 as stubs (always fall through until harness lands) is still not stated explicitly in §10 implementation sketch. |
| `confidence` field on `ShapeClassification` — no behavioral consequence | **DID NOT RESOLVE** | §4 and §10 still include `confidence: str` with no downstream behavioral contract. The evolution note in §3 adds "provisional" categories but doesn't wire to confidence degradation in rule firing. |
| RULE-5 keep vs fold (zero behavior change, bookkeeping overhead) | **NOT APPLICABLE** | No owner directive on RULE-5. Owner did not change it; still in design as hygiene. My R1 cut recommendation was advisory; the board may still weigh in. |

---

## §3 Per-question answers (R2 focus areas A/B/C only)

### A. Did the §9 Q9 reframing land correctly?

**ANSWER:** Mostly yes, but the staged-promotion mechanism introduces a re-validation requirement the design does not acknowledge.

**REASONING:** The ≤5/12 hard floor is correctly calibrated to the §8 projection (firm rules eliminate ~4-5 of 10 overrides; the hard floor is achievable without RULE-7/8/9). The "≥2 of 3" gate for stretch-promotion is reasonable — it requires meaningful harness convergence (not just one signal) without demanding all three (which might never co-occur). However: when the stretch ≤3/12 auto-promotes to a hard floor mid-Phase-3-or-later, it applies retroactively as a new minimum bar. Any scan that was passing at ≤5/12 would need to be re-evaluated against ≤3/12, which requires RULE-7/8/9 to be active and the scan bundle to be re-rendered. The design does not state whether the auto-promotion triggers a re-render requirement or only gates NEW scans. That gap should be closed before Phase 3 ships — the simplest fix is: "auto-promotion applies to new scans only; existing passing scans are grandfathered at the ≤5/12 floor." On Codex's "remaining override classes" framing: it is a complementary metric worth tracking as diagnostic telemetry (override type distribution), but the raw count floor is simpler to gate on and is sufficient as an acceptance criterion. Subsumed for gating purposes.

---

### B. Is the new shape-enum evolution note + provisional-flag mechanism adequate?

**ANSWER:** Adequate for Phase 3, with two gaps worth noting: no promotion criterion from provisional to stable, and `confidence` is not wired to rule firing.

**REASONING:** The provisional flag + `other`-fallback + deferred-ledger-entry mechanism correctly prevents emergency taxonomy changes and surfaces misclassification. However, the design does not specify when a provisional category becomes stable — "when a second scan arrives" is implied but not stated. A target n=2 promotion criterion before "stable" is the natural completion of the mechanism (parallel to how RULE-7/8/9 require n≥2 before promotion). Without it, provisional categories can remain provisional indefinitely with no resolution path. On sunset rules: the design's evolution note says "the enum is expected to evolve as the catalog grows" — a sunset trigger (provisional + no 2nd scan within X timeframe → reconsidered) would add discipline, but is not blocking for Phase 3 given how slow the catalog grows. On confidence degradation: the `confidence` field on `ShapeClassification` is defined but has no behavioral consequence in the rule evaluation path. The browser-extension boundary clarification adequately covers the `desktop-application` / native-host case; `is_privileged_tool` is the right modifier for extension-permission scope.

---

### C. Is the rule precedence contract complete?

**ANSWER:** Complete for single-cell scenarios. One gap: cross-cell effects of auto-fire rules are not addressed.

**REASONING:** The first-match-wins contract (§2) handles same-cell multi-rule firing cleanly: auto-fire short-circuits, non-auto-fire rules evaluate in priority order, step 5 is pure fallback. The RULE-1-fires-Q1-amber AND RULE-3-also-matches scenario is resolved by ordering: RULE-3 is a shape modifier (step 2) evaluated before RULE-1 (step 4); RULE-3 wins for Q1 if it fires first. The template_key applied is from RULE-3 (`q1.amber.solo_with_positive_signals`), not RULE-1 — which is the right behavior since RULE-3 is more specific. However: when RULE-6 auto-fires on Q4 (step 1), does it affect Q1 evaluation? The design is silent on cross-cell ordering effects. For now this is probably fine (Q4 auto-fire doesn't logically affect Q1), but the contract should state explicitly: "precedence contract applies within a single cell; cross-cell ordering effects are not defined — each cell evaluates independently." A `rule_id` traceability requirement is addressed by `phase_3_advisory.scorecard_hints.<q>.rule_id` in §10 — this is the right design. It should be confirmed as non-optional (required field, not optional) to ensure every audit can trace why a cell landed where it did.

---

## §4 Cross-agent reactions

**Agreement with Codex (Systems Thinker):**
The FIX-NOW on `classify_shape()` phase boundary was the right call and was the most consequential R1 item. Dropping the Phase 4 fallback strengthens the determinism property of the entire redesign; without it, any Phase 3 test that expected a "deterministic" classification was actually running on a hybrid. I fully agree, and the owner directive implementing it is correct.

I also agree with Codex's framing on Q3/Q4 — the "remaining override classes" diagnostic lens is worth tracking even if the raw count floor is the acceptance gate. Codex raised this in §6 R2 carry-forwards; it deserves a tracker field in the comparison doc (§8 migration plan).

**Agreement with DeepSeek (Skeptic):**
The over-fit concern on the 9-category enum was real and the provisional-flag mechanism is the right minimum response. DeepSeek's n=3 gate for RULE-7/8/9 promotion is more conservative than my n≥2 position; I think n≥2 + compound harness gate is sufficient because the compound harness gate already provides the quality floor DeepSeek wants from n≥3. The two conditions are not equivalent but the compound gate addresses the same failure mode.

**Disagreement with DeepSeek:**
DeepSeek's R1 Dissent 2 (collapse 9-category enum to 6) is now resolved by owner directive — kept with evolution note. I don't think collapsing to 6 was necessary; the provisional flag is the right discipline. DeepSeek's Dissent 3 (Q2 absence) is a real gap but not a Phase 3 blocker — Q2 is finding-severity-adjacent and the design's scope decision correctly defers it. I would not block on Q2 absence.

**New item DeepSeek surfaced that I missed:**
The Q2 override gap (3 of 10 overrides are Q2; no Q2 rules). I acknowledged this implicitly in my R1 Q7 response but didn't name it explicitly as a miss. DeepSeek is right that the design should document Q2 deferral rationale and timeline, not leave it as an unaddressed hole.

---

## §5 New dissents (formal record — required even if empty)

**New dissent — staged-promotion re-validation gap:**

- **WHAT:** When the ≤3/12 stretch target auto-promotes to a hard floor (triggered by ≥2 of V12x-7/11/12 landing), the design does not specify whether this re-validation requirement applies to previously-passing scans or only to new scans.
- **WHY:** If the auto-promotion applies retroactively, every scan that passed at ≤5/12 must be re-rendered under RULE-7/8/9 before the new hard floor can be verified. This is a potentially large re-render scope triggered by harness work completing, not by a calibration decision. If it applies only to new scans, that should be stated — "grandfathering" is a policy choice, not an obvious default.
- **WHETHER YOU'D BLOCK:** DEFER-WITH-NOTE — not a blocker for Phase 3 acceptance, but the Phase 3 design should add one sentence clarifying the retroactivity scope before implementation begins.

---

## §6 R3 carry-forwards

1. **Staged-promotion retroactivity scope** (new dissent above): R3 should confirm the owner's intent — does ≤3/12 auto-promotion apply to previously-passing scans or only to new scans? One sentence in §9 Q9 resolves this.

2. **`confidence` field behavioral consequence**: Three agents (Pragmatist R1, Codex R1, DeepSeek R1) all noted this field has no downstream behavioral contract. R3 should finalize: (a) drop it, (b) wire it to shape-conditional rule degradation (low confidence → shape modifier rules don't fire), or (c) treat it as diagnostic-only and move to debug logs. This is a Phase 3 implementation decision; R3 is the last chance to settle it before code is written.

3. **RULE-7/8/9 as Phase 3 stubs**: The implementation sketch (§10) doesn't address how RULE-7/8/9 are handled before their harness signals land. R3 should confirm: RULE-7/8/9 are implemented as stub functions that always return "no match" until the harness signals exist (never falls through to override differently than before). This is the clean implementation path; R3 should ratify it.

4. **Q2 deferral documented**: DeepSeek's Dissent 3 (Q2 absence from rule table) was preserved-for-record in R1. R3 should confirm that a one-paragraph Q2 deferral note is added to §5 or §7 of the design (rationale: finding-severity dependency; timeline: Phase 1.5), so the gap is explicitly acknowledged rather than silently absent.

5. **`rule_id` traceability as non-optional**: The §10 implementation sketch includes `phase_3_advisory.scorecard_hints.<q>.rule_id` as optional. R3 should confirm it is required (not optional) — every cell evaluation must record which rule fired, enabling audit and debugging without extra per-scan archaeology.
