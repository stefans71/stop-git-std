| Item | Vote | Rationale |
|---|---|---|
| FN-1 | SECOND | This closes the main architectural gap: Step G now tests `bundle -> form.json -> render -> parity` at the semantic boundary, not just schema/render shape. Stronger than evidence-card-count tolerance because exact linkage tests isolation boundaries directly. |
| FN-2 | SECOND | Required. Deterministic Phase 3 cannot be hand-reimplemented during acceptance. Direct `compute.py` invocation preserves the compute/render isolation boundary. |
| FN-3 | SECOND | Correct pre-flight. It tests that bundle validation rejects semantic contamination before `form.json` authoring starts. |
| FN-4 | ADJUST | I still do not accept “partial pass” language for Step G as an overall claim. Textual change: replace `Gate 6 fails on 1 of 3 targets, others clean | Step G partial pass. Failing shape tagged step-g-failed-artifact in provenance.json; issue a tracked remediation ticket; V2.5-preview cleared for the 2 passing shapes only. NO full quarantine.` with `Gate 6 fails on 1 of 3 targets, others clean | Overall Step G = FAIL, but treat as isolated target failure, not full rollback. Failing shape tagged step-g-failed-artifact in provenance.json; retain passing targets as diagnostic evidence; V2.5-preview NOT promoted as Step-G-passed until all 3 shapes pass. NO full quarantine unless repeated or systemic.` |
| FN-5 | SECOND | Necessary execution hardening. Warning-bearing success codes are not acceptable gates. |
| FN-6 | SECOND | Good belt-and-suspenders check. A tainted comparator breaks the acceptance boundary. |
| FN-7 | SECOND | This is the right execution shape architecturally: pilot + checkpoint preserves diagnosis quality and prevents wasting later targets on a broken contract. |
| FN-8 | ADJUST | Keep 6b, but tighten the check so it does not drift into style review. Textual change: replace `contain ONLY enum values / F-ID refs / short phrases. Prose paragraphs (>40 words, narrative sentences) must live in phase_5_prose_llm.*. Manual visual check on first target (zustand); if clean, subsequent targets get same check.` with `contain only structured content appropriate to the field type; no narrative sentences or synthesis claims in Phase 4 structured fields. Check all 3 targets, not only the first, because boundary contamination is shape-sensitive.` |
| FN-9 | SECOND | Correct sequencing guard. `form.json` authoring must not begin from an unstable upstream artifact. |
| D-1 | CONFIRM | Fresh-HEAD validation is a production-promotion issue, not a Step G acceptance pre-req. |
| D-2 | CONFIRM | Full automation is desirable but not required once FN-2 forces direct compute execution. |
| D-3 | CONFIRM | Same-bundle re-authoring determinism is a distinct property and can stay deferred. |
| D-4 | ADJUST | Still defer, but wording should be sharper. Textual change: replace `already on ledger ... Active watch item during Step G; upgrade if Step G surfaces concrete schema pain.` with `DEFER, but treat as explicit watchpoint during Step G. Any need to invent ad hoc fields, overload existing fields, or carry semantics outside schema-defined locations upgrades this immediately to FIX NOW and halts execution.` |
| D-5 | CONFIRM | Real gap, but outside Step G scope; fixture expansion is the remedy path. |
| D-6 | CONFIRM | Manual exact-match in FN-1 is sufficient for Step G. Automating it is useful later, not load-bearing now. |
| I-1 | CONFIRM | Pre-authoring provenance is part of artifact discipline and should be explicit. |
| I-2 | CONFIRM | Properly absorbed by FN-1’s Archon clarification. |
| I-3 | CONFIRM | Important boundary note: template fixture is not proof of pipeline correctness. |
| I-4 | CONFIRM | Not blocking if current HEAD is captured in the Step G artifact manifest. |
| I-5 | CONFIRM | Correctly resolved by anchoring parity to V2.4 comparator MD/HTML, not fixture internals. |
| I-6 | CONFIRM | Content parity matters; presentation variation does not. |
| I-7 | CONFIRM | Known coverage limitation, not a reason to block Step G. |
| I-8 | CONFIRM | Agreed. Continuous-with-checkpoint is the right diagnostic mode. |
| I-9 | CONFIRM | Properly documented by D-3 / FN-8; no Step G gate expansion needed. |

Discussion

The revised package is close. FN-1, FN-2, FN-7, and FN-9 are the architectural load-bearers because they define the actual isolation boundaries: complete bundle first, direct compute for deterministic fields, author `form.json` only after upstream validation, then compare rendered output semantically against a pinned comparator. That is the right pipeline contract.

My remaining dissent is concentrated in FN-4. I still do not think Step G can be called a “pass” if one of the three canonical shapes misses gate 6. That would weaken the acceptance meaning from “pipeline reliable across approved fixture shapes” to “mostly reliable.” I agree with the owner that not every isolated gate-6 miss merits quarantine. I do not agree that such a run should count as Step G passed, even partially, for promotion language. Keep the disposition graded operationally, but keep the verdict strict.

FN-8 is directionally right but needs one boundary-focused refinement: contamination checks should be run on all three targets, because shape-specific prompt pressure is exactly where boundary leaks appear. Also, define the check in semantic terms, not arbitrary word count terms.

Overall verdict: SIGN OFF WITH DISSENTS.

Per-agent framing answers

FN-4: ADJUST, not SECOND. The current split-the-difference rubric is operationally better than binary rollback, but I still reject calling a 17/18 outcome a Step G pass. Isolated gate-6 miss should be handled as isolated failure without quarantine, while the overall Step G verdict remains fail-until-3-of-3.

D-4 schema hardening: still DEFER, but only as a watched boundary. It is not a Step G pre-req if the current run can be completed without schema overloading. If Step G forces operators to smuggle semantics through underspecified fields, then schema hardening becomes immediate and execution should halt.

What must change for full clean approval: adopt the FN-4 wording change above, and tighten FN-8 to require all-target phase-boundary checks using semantic rather than stylistic criteria. With those two edits, I would SECOND every FN and CONFIRM every D/I item.
