# Pragmatist R3 — Calibration Rebuild Design Review (Confirmation)

**Role:** Pragmatist (Claude Sonnet 4.6)
**Round:** R3 (Confirmation — final ratification + dissent audit)
**Date:** 2026-05-01

---

## §1 R3 verdict

SIGN OFF. The as-revised design is ready for archive and Phase 3 implementation. All 14 owner directives (7 post-R1, 7 post-R2) were applied correctly and the design is internally consistent. The two concerns I carried forward from R2 — staged-promotion retroactivity scope and `confidence` behavioral consequence — are both resolved by R2 directives 1 and 5 respectively: prospective-only promotion is now stated explicitly, and `confidence` is demoted to debug-only with no rule reading it. My surviving note is that Q2's absence from the rule table remains undocumented in the design body (it is only implicit in §1 Non-Goals and §7), but this is not a blocker given that Phase 3 defers it by design. No new dissents. The design is implementable.

---

## §2 Did the revisions hold

All 14 owner directives were applied correctly. Key verification per section:

- **R1 D1 (Q9 floor):** §9 Q9 states ≤5/12 hard floor with ≤3/12 staged stretch tied to ≥2 of V12x-7/11/12. Correctly implemented.
- **R1 D2 (classify_shape phase boundary):** §4 inputs list is Phase 1 only; step 10 explicitly states "DOES NOT consult phase_4_structured_llm.catalog_metadata.shape." Correctly implemented.
- **R1 D3 (RULE-3 narrow rewrite):** §5 RULE-3 trigger uses explicit parentheses and positive-signal gate (`has_codeql OR releases_count >= 20`). Operator-precedence bug resolved. Correctly implemented.
- **R1 D4 (enum evolution note):** §3 evolution note present; provisional categories named. Correctly implemented.
- **R1 D5 (browser-extension boundary):** §3 clarification present; `desktop-application` ruling explained. Correctly implemented.
- **R1 D6 (rule precedence contract):** §2 first-match-wins contract present; auto-fire short-circuits stated. Correctly implemented.
- **R1 D7 (template-map fallback):** §6 fallback behavior specified; validator warns on miss; errors when both miss + empty. Correctly implemented.
- **R2 D1 (promotion prospective only):** §9 Q9 states "prospective only… existing passing scans are NOT retroactively failed." Correctly implemented.
- **R2 D2 ("remaining override classes" diagnostic-only):** §9 Q9 states "track in comparison doc as diagnostic-only… does NOT gate Phase 1 acceptance." Correctly implemented.
- **R2 D3 (provisional-to-stable at n≥2):** §3 states "promote to stable at n≥2 V1.2 scans classifying cleanly." Correctly implemented.
- **R2 D4 (§10 Phase 3 must resolve):** §10 "Phase 3 must resolve" sub-section present with 3 named items. Correctly implemented.
- **R2 D5 (`confidence` debug-only):** §4 `ShapeClassification` docstring states "DEBUG-ONLY… No rule reads this." Correctly implemented.
- **R2 D6 (`rule_id` required):** §10 `CellEvaluation.rule_id` marked REQUIRED with validator enforcement noted. Correctly implemented.
- **R2 D7 (≥2-of-3 harness threshold confirmed):** §9 Q9 states "≥2 of V12x-7 / V12x-11 / V12x-12 landing is the trigger." Correctly implemented.

No directive was applied incorrectly. No directive introduced a new problem. The design reads as a coherent whole post-revision.

---

## §3 Pre-archive dissent audit (MANDATORY — zero silent drops rule)

All concerns from R1 §3-§5 + R2 §2-§5 across all 3 agents are classified below.

| Concern source | Brief description | Disposition | Citation |
|---|---|---|---|
| Pragmatist R1 §3 item 1 | Fallback template key for no-rule-fired cases unspecified | RESOLVED | §6 template-map fallback: fall back to LLM-authored short_answer; validator warns on miss |
| Pragmatist R1 §3 item 2 | RULE-3 operator-precedence bug | RESOLVED | §5 RULE-3 trigger now explicitly parenthesized |
| Pragmatist R1 §3 item 3 | `classify_shape()` heuristic priority conflicts — first-match-wins not named | RESOLVED | §2 rule precedence contract added |
| Pragmatist R1 §3 item 4 | V12x harness dependency not surfaced in Phase 3 plan | RESOLVED | §9 Q9 ties stretch-target promotion to V12x-7/11/12 landing |
| Pragmatist R1 §4 item 1 | RULE-5 zero behavior change, bookkeeping overhead | MOOT | Owner elected to keep RULE-5 as hygiene; no directive was issued but position is preserved in §5 design rationale. Pragmatist R1 advisory note; not a dissent. |
| Pragmatist R1 §4 item 2 | `confidence` field has no behavioral consequence | RESOLVED | §4 + §10: `confidence` demoted to DEBUG-ONLY per R2 D5; explicitly "no rule reads this" |
| Pragmatist R2 §5 new dissent | Staged-promotion retroactivity scope unspecified | RESOLVED | §9 Q9: "applies prospectively only… existing passing scans are NOT retroactively failed" (R2 D1) |
| Codex R1 §5 dissent (FIX-NOW) | `classify_shape()` must not read Phase 4 LLM output | RESOLVED | §4 inputs restricted to Phase 1 only; fallback dropped (R1 D2) |
| Codex R1 §5 dissent (DEFER-WITH-NOTE) | Q9 ≤3/12 floor too strict for Phase 1 | RESOLVED | ≤5/12 hard floor + ≤3/12 staged stretch (R1 D1) |
| Codex R1 §3 item 1 | Phase ownership of `classify_shape()` under-specified | RESOLVED | §4 revised to Phase 1 inputs only |
| Codex R1 §3 item 2 | Multi-rule precedence not explicit | RESOLVED | §2 first-match-wins contract |
| Codex R1 §3 item 3 | Low-confidence shape handling missing policy | DEFERRED | §10 "Phase 3 must resolve" item 3: confidence-degradation rules deferred to Phase 3 per R2 D4 |
| Codex R1 §3 item 4 | Modifier independence / hidden double-counting risk | DEFERRED | §10 "Phase 3 must resolve" item 2 names `is_privileged_tool` boundary cases; design note in §3 clarifies independent axes (confirmed by DeepSeek R2 §4). Phase 3 codifies the boundary. |
| Codex R1 §4 items (cut list) | Cut Phase 4 shape fallback; simplify template addressing; simplify RULE-3; treat `specialized-domain-tool` as lower-confidence | RESOLVED | All four addressed by R1 directives D2, D3, D4 |
| Codex R2 §5 note 1 | Staged Q9 auto-promotion needs prospective-only contract | RESOLVED | R2 D1 applied to §9 Q9 |
| Codex R2 §5 note 2 | `rule_id` traceability should be required per-cell | RESOLVED | §10 `CellEvaluation.rule_id` marked REQUIRED; validator enforces (R2 D6) |
| Codex R2 §6 carry-forward 3 | Provisional-to-stable at n=2 explicit | RESOLVED | §3 states "promote to stable at n≥2 V1.2 scans classifying cleanly" (R2 D3) |
| Codex R2 §6 carry-forward 4 | `is_privileged_tool` boundary cases need sharpening | DEFERRED | §10 "Phase 3 must resolve" item 2: boundary cases deferred to Phase 3 (R2 D4) |
| Codex R2 §6 carry-forward 5 | `rule_id` required | RESOLVED | Same as Codex R2 §5 note 2 above |
| DeepSeek R1 §5 Dissent 1 (FIX-NOW) | Q9 ≤3/12 floor creates circular dependency | RESOLVED | ≤5/12 hard floor + staged stretch (R1 D1) |
| DeepSeek R1 §5 Dissent 2 (DEFER-WITH-NOTE) | 9-category enum over-fitted to n=12 | RESOLVED | Evolution note + provisional-flag mechanism + n≥2 promotion criterion (R1 D4, R2 D3) |
| DeepSeek R1 §5 Dissent 3 (PRESERVED-FOR-RECORD) | Q2 absent from rule table (30% of overrides) | DEFERRED | Design §1 Non-Goals and §7 establish cells-only scope with Phase 1.5 for finding-severity work. Q2 deferral rationale is implicit. Not addressed as a design-body paragraph — see new §4 note below. |
| DeepSeek R1 §3 item 1 | Q2 completely absent | DEFERRED | Same as above |
| DeepSeek R1 §3 item 2 | `confidence` field has no behavioral consequence | RESOLVED | R2 D5: debug-only, no rule reads it |
| DeepSeek R1 §3 item 3 | No test for classifier stability across harness changes | DEFERRED | §10 test section mentions classifier fixture tests. A harness-change regression contract is not specified — appropriately deferred to Phase 3 implementation which owns the test suite |
| DeepSeek R1 §4 item 1 | `specialized-domain-tool` should collapse | MOOT | Owner elected to keep with provisional flag; evolution note is the response. This is a preserved advisory, not a dissent. `specialized-domain-tool` has n=2 V1.2 scans (freerouting + Kronos) — DeepSeek's count was off (noted in design §9 R2 items NOT changed). |
| DeepSeek R1 §4 item 2 | `agentic-platform` should collapse (n=0 V1.2) | DEFERRED | Kept with provisional flag per R1 D4. Phase 3 implementation will use the n≥2 gate. |
| DeepSeek R1 §4 item 3 | `install-script-fetcher` should collapse (n=0 V1.2) | DEFERRED | Same as above |
| DeepSeek R1 §4 item 4 | `matched_rule` field should be removed from schema | MOOT | `matched_rule` remains on `ShapeClassification` NamedTuple in §4 and §10. This was an advisory not a dissent; owner did not issue a directive on it. It functions as a debug aid alongside the `confidence` debug-only field. Low cost, carries no behavioral weight. |
| DeepSeek R2 §5 Dissent 1 | `confidence` field still has no behavioral consequence | RESOLVED | R2 D5: debug-only explicitly; no rule reads it. This correctly closes the "dead weight" concern by being explicit rather than silent. |
| DeepSeek R2 §5 Dissent 2 | Q2 gap remains undocumented | DEFERRED | See §4 note below — one minor gap survives |
| DeepSeek R2 §6 carry-forward 2 | Enum stability review trigger (after 12 more scans) | DEFERRED | Design doesn't specify a scan-count trigger for enum review. Appropriately a Phase 3 / catalog-maintenance decision. Not a design blocker. |
| DeepSeek R2 §6 carry-forward 3 | Q2 deferral documented | DEFERRED | See §4 — still not a body paragraph in §5 or §7; treated as minor note, not a dissent |
| DeepSeek R2 §6 carry-forward 4 | `confidence` behavioral consequence | RESOLVED | R2 D5: debug-only |
| DeepSeek R2 §6 carry-forward 5 | `rule_id` required | RESOLVED | R2 D6 |

**Silent-drop check:** No concern raised in R1 or R2 by any agent was silently dropped. Every concern is either RESOLVED (design updated), DEFERRED (explicitly named in §10 "Phase 3 must resolve" or in the scope decision), or MOOT (advisory preference not addressed by directive, low cost). Zero silent drops.

---

## §4 New issues introduced by revisions

One minor issue surfaced by the R2 directives that prior rounds could not have flagged:

**Q2 deferral prose still absent from design body.** DeepSeek raised this in R2 Dissent 2 and R2 carry-forward 3. The R2 adjudication table does not include a directive to add a Q2 deferral paragraph. As a result, the design body has zero Q2 rules and no prose statement of why (§5 goes directly from RULE-5 Q3 to RULE-6 Q4). The deferral is correctly implied by §1 Non-Goals ("cells only"), §7 scope decision, and §9 Q7 DECIDED — but a reader starting from §5 will find the gap without context. This is a documentation deficiency, not an architectural one.

**WHAT:** No design-body paragraph explaining Q2 deferral.
**WHY:** A 2-sentence note in §5 (before RULE-6) stating "Q2 has no rules in Phase 1 — Q2 overrides (Kronos, Xray-core, skills) are driven by finding-severity patterns deferred to Phase 1.5 per §7 scope decision" would prevent future readers from thinking Q2 was forgotten rather than intentionally deferred.
**WHETHER YOU'D BLOCK:** No. This is not an architectural issue and does not affect Phase 3 implementability. Phase 3 implementers have §1, §7, and the full board record to understand the deferral. Recommend adding the note as a low-cost hygiene fix, but the archive is clean without it.

---

## §5 Final R3 dissents (formal record)

No R3 dissents — design is ready for archive + Phase 3 implementation.

The Q2 gap noted in §4 is a documentation deficiency worth a one-sentence fix but is not a dissent. All R1 and R2 formal dissents are resolved or appropriately deferred. The design holds under its second revision cycle.

---

## §6 Phase 3 readiness check

The three §10 "Phase 3 must resolve" items are appropriate deferrals:

1. **Provisional-vs-stable tracking mechanism** — criteria are specified (n≥2 V1.2 scans → stable), implementation choice is correctly left to Phase 3. Appropriate.
2. **`is_privileged_tool` boundary cases** — the design provides the known-good classifications (§3 table) and the conceptual boundary (elevated permissions context); Phase 3 codifies heuristics from what `phase_1_raw_capture` actually exposes. Appropriate — cannot pre-specify before seeing the signal surface.
3. **Confidence-degradation rules** — `confidence` is debug-only with no rule reading it (R2 D5). The deferral says "wire to rule degradation only if a future audit shows justifying evidence." This is the right call; pre-engineering degradation behavior without evidence would be speculative. Appropriate.

All three deferrals are: **yes, appropriate.** No item needs to be specified before Phase 3 starts.
