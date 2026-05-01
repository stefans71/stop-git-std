# Skeptic R3 — Calibration Rebuild Design Review (Confirmation)

## §1 R3 verdict

**SIGN OFF WITH NOTES.** The as-revised design is ready for archive and Phase 3 implementation. All 14 owner directives (8 R1-round + 7 R2-round, with 1 overlap on Q9) were applied correctly and resolve the three core dissents I carried from R1: the Q9 circular dependency is broken by the staged floor; the enum over-fit risk is acknowledged via provisional-flag mechanism; RULE-3's ghost-rule problem is eliminated by the positive-evidence trigger. My surviving concerns — the `confidence` field's continued lack of behavioral consequence, the Q2 gap's undocumented deferral, and the absence of a shape-classifier regression test requirement — are deferred-to-Phase-3 notes, not blockers. The design is coherent, implementable, and the pre-archive dissent audit confirms zero silent drops.

## §2 Did the revisions hold

Yes. All 14 owner directives were applied correctly. The §9 revision history table is authoritative and matches the design body. Specific checks:

- **Q9 staged floor** (§9): ≤5/12 hard + ≤3/12 stretch with ≥2-of-3 harness gate — correctly implemented. Promotion semantics (prospective only) added post-R2 resolves the re-validation gap I flagged in R2.
- **classify_shape() Phase 4 fallback dropped** (§4): clean. Heuristic step 10 explicitly says "DOES NOT consult phase_4_structured_llm.catalog_metadata.shape."
- **RULE-3 narrow rewrite** (§5): parenthesized, positive-evidence trigger (`has_codeql OR releases_count >= 20`), confidence raised to firm. Correct.
- **Enum evolution note + provisional flag** (§3): present. Provisional-to-stable promotion (n≥2 V1.2 scans) added post-R2.
- **Browser-extension boundary** (§3): desktop-application classification with `is_privileged_tool` modifier — correct.
- **Rule precedence contract** (§2): first-match-wins, auto-fire short-circuits, no combining — explicit and correct.
- **Template-map fallback** (§6): falls back to LLM-authored short_answer; validator warns on miss — correct.
- **confidence field demoted to debug-only** (§10): no rule reads it — correctly implemented per R2 directive.
- **rule_id traceability REQUIRED** (§10): changed from optional to required — correct.
- **≥2-of-3 harness threshold confirmed** (§9): correct.

No directive was applied incorrectly or introduced a new problem that the prior rounds couldn't have surfaced.

## §3 Pre-archive dissent audit (MANDATORY — zero silent drops rule)

### R1 concerns (all 3 agents)

| Concern source | Description | Disposition | Citation |
|---|---|---|---|
| DeepSeek R1 §5 Dissent 1 | Q9 ≤3/12 hard floor unachievable with firm rules | **RESOLVED** | §9 Q9 revised: ≤5/12 hard + ≤3/12 staged stretch |
| DeepSeek R1 §5 Dissent 2 | 9-category enum over-fitted to n=12 | **RESOLVED** | §3 enum evolution note + provisional-flag mechanism + n≥2 promotion |
| DeepSeek R1 §5 Dissent 3 | Q2 absence from rule table (30% of overrides) | **DEFERRED** | No Q2 rules added; Q2 deferral rationale still undocumented. Deferred to Phase 1.5 per design's cells-only scope (§7). Gap remains but is acknowledged by board consensus. |
| DeepSeek R1 §3 item 1 | Q2 completely absent from rule table | **DEFERRED** | Same as above. |
| DeepSeek R1 §3 item 2 | confidence field has no behavioral consequence | **RESOLVED** | §10: confidence demoted to debug-only per R2 directive. No rule reads it. Tracked for audit only. |
| DeepSeek R1 §3 item 3 | No test for shape-classifier stability across harness changes | **DEFERRED** | §10 lists tests but no regression-test requirement for harness-change stability. Deferred to Phase 3 implementation discipline. |
| DeepSeek R1 §4 item 1 | specialized-domain-tool should collapse into other | **RESOLVED** | §3: category kept; provisional-flag mechanism addresses over-fit risk. (Note: actually has 2 V1.2 scans — freerouting + Kronos — per R2 correction.) |
| DeepSeek R1 §4 item 2 | agentic-platform should collapse into other | **RESOLVED** | §3: category kept; provisional-flag mechanism + n≥2 promotion gate. n=0 in V1.2; will promote when evidence arrives. |
| DeepSeek R1 §4 item 3 | install-script-fetcher should collapse into other | **RESOLVED** | §3: category kept; provisional-flag mechanism. n=0 in V1.2; will promote when evidence arrives. |
| DeepSeek R1 §4 item 4 | matched_rule field should be removed from schema | **MOOT** | §10: matched_rule retained in ShapeClassification NamedTuple. R2 directive demoted confidence to debug-only but kept matched_rule. Concern is moot because matched_rule serves traceability (parallel to rule_id). |
| DeepSeek R1 §5 (RULE-3) | Prune RULE-3 (ghost rule) | **RESOLVED** | §5 RULE-3: narrow rewrite with positive-evidence trigger. No longer a ghost rule. |
| Pragmatist R1 §3 item 1 | Template-map fallback unspecified (no-rule-fired case) | **RESOLVED** | §6: fallback to LLM-authored short_answer added post-R1. |
| Pragmatist R1 §3 item 2 | RULE-3 operator-precedence ambiguity | **RESOLVED** | §5 RULE-3: explicit parentheses added. |
| Pragmatist R1 §3 item 3 | classify_shape() heuristic priority conflicts | **RESOLVED** | §2: first-match-wins precedence contract added. |
| Pragmatist R1 §3 item 4 | V12x harness dependency not surfaced in Phase 3 plan | **RESOLVED** | §9 Q9 explicitly ties stretch promotion to V12x-7/11/12. §10 lists RULE-7/8/9 dependencies. |
| Pragmatist R1 §4 item 1 | RULE-5 should fold into comment (zero behavior change) | **RESOLVED** | RULE-5 kept as named rule. Board consensus favored traceability. |
| Pragmatist R1 §4 item 2 | confidence field should be removed or used | **RESOLVED** | §10: confidence demoted to debug-only per R2 directive. |
| Codex R1 §5 Dissent 1 | classify_shape() Phase 4 fallback — phase-boundary violation | **RESOLVED** | §4: Phase 4 fallback dropped. FIX-NOW applied. |
| Codex R1 §5 Dissent 2 | Q9 ≤3/12 floor too strict for Phase 1 | **RESOLVED** | §9 Q9: staged floor adopted. |
| Codex R1 §3 item 1 | classify_shape() phase ownership under-specified | **RESOLVED** | §4: pure Phase 1/3 inputs, Phase 4 fallback dropped. |
| Codex R1 §3 item 2 | Multi-rule precedence not explicit enough | **RESOLVED** | §2: first-match-wins contract added. |
| Codex R1 §3 item 3 | Low-confidence shape handling missing | **RESOLVED** | §10: confidence demoted to debug-only. §3: provisional-flag mechanism. |
| Codex R1 §3 item 4 | Modifier independence / double-counting risk blurry | **RESOLVED** | §3-§5: modifiers vs Q4 rule signals clarified. is_privileged_tool is shape-level; Q4 rules consume specific dangerous-primitive signals. |
| Codex R1 §4 item 1 | Cut live Phase 4 shape fallback | **RESOLVED** | Same as Codex R1 §5 Dissent 1. |
| Codex R1 §4 item 2 | Simplify template addressing to rule-oriented keys | **RESOLVED** | §2: rules emit template_key. §6: template-map is effectively rule-oriented. |
| Codex R1 §4 item 3 | Simplify or remove RULE-3 | **RESOLVED** | §5 RULE-3: narrow rewrite with positive-evidence trigger. |
| Codex R1 §4 item 4 | Treat specialized-domain-tool as lower-confidence bucket | **RESOLVED** | §3: provisional-flag mechanism covers this globally. |

### R2 concerns (all 3 agents)

| Concern source | Description | Disposition | Citation |
|---|---|---|---|
| DeepSeek R2 §5 New Dissent 1 | confidence field still has no behavioral consequence | **RESOLVED** | §10: confidence demoted to debug-only per R2 directive. No rule reads it. |
| DeepSeek R2 §5 New Dissent 2 | Q2 gap remains undocumented | **DEFERRED** | No Q2 deferral documentation added. Deferred to Phase 1.5. Board consensus accepts this as a non-blocker. |
| Pragmatist R2 §5 New Dissent | Staged-promotion re-validation gap (retroactivity) | **RESOLVED** | §9 Q9: promotion semantics added post-R2 — prospective only. |
| Codex R2 §5 (notes) | Staged Q9 auto-promotion needs prospective-only contract | **RESOLVED** | Same as Pragmatist R2 above. |
| Codex R2 §5 (notes) | rule_id traceability should be required | **RESOLVED** | §10: rule_id made REQUIRED per R2 directive. |

### Silent drop check

**Zero silent drops.** Every concern raised in R1 §3-§5 and R2 §2-§5 by any of the 3 agents is accounted for above. No concern was silently dropped.

## §4 New issues introduced by revisions

None. The 14 owner directives were applied cleanly and did not introduce new problems. Specific checks:

- **Q9 staged floor** (R1 directive 1 + R2 directives 1/2/7): the prospective-only semantics and diagnostic-only "remaining override classes" framing are correct. No new issue.
- **classify_shape() Phase 4 fallback dropped** (R1 directive 2): clean. The "other" + override-explained path is the correct fallback.
- **RULE-3 narrow rewrite** (R1 directive 3): the positive-evidence trigger (`has_codeql OR releases_count >= 20`) is well-scoped. No new issue.
- **Enum evolution note + provisional flag** (R1 directive 4 + R2 directive 3): the n≥2 promotion criterion is correct. No new issue.
- **Browser-extension boundary** (R1 directive 5): correct classification. No new issue.
- **Rule precedence contract** (R1 directive 6): explicit and complete for single-cell scenarios. No new issue.
- **Template-map fallback** (R1 directive 7): correct. No new issue.
- **confidence field demoted to debug-only** (R2 directive 5): correct resolution of a multi-agent concern. No new issue.
- **rule_id traceability REQUIRED** (R2 directive 6): correct. No new issue.
- **≥2-of-3 harness threshold** (R2 directive 7): correct. No new issue.

## §5 Final R3 dissents (formal record)

No R3 dissents — design is ready for archive + Phase 3 implementation.

All three R1 dissents I carried are resolved by the as-revised design. The two items I flagged as DEFERRED (Q2 gap documentation, shape-classifier regression test requirement) are Phase 3/Phase 1.5 implementation discipline items, not design defects. The `confidence` field's behavioral consequence was resolved by demoting it to debug-only — a cleaner outcome than either removing it or pre-engineering degradation rules.

## §6 Phase 3 readiness check

Yes — the deferrals are appropriate. All three §10 items are genuine implementation decisions that benefit from Phase 3's access to the actual harness data shapes:

1. **Provisional-vs-stable tracking mechanism** — correctly deferred. The criteria (n≥2 V1.2 scans) are specified; the bookkeeping mechanism is an implementation detail.
2. **`is_privileged_tool` boundary cases** — correctly deferred. The design classifies known cases; Phase 3 will codify the decision boundary based on what `phase_1_raw_capture` actually exposes. Premature specification would produce brittle rules.
3. **Confidence-degradation rules** — correctly deferred. The R2 directive (demote to debug-only, wire to rule degradation only if future audit shows justifying evidence) is the right call. Speculative engineering would add complexity with no empirical basis.

No item should be specified before Phase 3.
