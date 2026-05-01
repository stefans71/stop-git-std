# Skeptic R2 — Calibration Rebuild Design Review (Consolidation)

## §1 Topline (under 150 words)

**SIGN OFF WITH NOTES.** The post-R1 revisions moved my position from DISSENT to conditional sign-off. The three changes that resolved my core R1 concerns: (1) Q9 reframed from ≤3/12 hard floor to ≤5/12 hard + ≤3/12 staged stretch — this breaks the circular dependency I flagged; (2) the enum evolution note + provisional-flag mechanism acknowledges the over-fit risk without collapsing categories prematurely; (3) RULE-3's narrow rewrite with positive-signal evidence (`has_codeql OR releases_count >= 20`) addresses my "ghost rule" concern by requiring observable positive evidence. My surviving concern is the shape enum's `agentic-platform`, `install-script-fetcher`, and `specialized-domain-tool` categories — they still have zero V1.2 empirical support and the provisional flag alone doesn't prevent misclassification on the next 12 scans. I also have a new concern about the `confidence` field's continued lack of behavioral consequence. Neither is a blocker; both are notes for Phase 3 implementation discipline.

## §2 R1-concern resolution table

| R1 concern (my §3/§4/§5) | Resolution status | Revised design section |
|---|---|---|
| **Dissent 1 — Q9 ≤3/12 hard floor unachievable with firm rules** | **RESOLVED.** ≤5/12 hard floor + ≤3/12 staged stretch that auto-promotes when ≥2 of V12x-7/11/12 harness signals land. This breaks the circular dependency. | §9 Q9 (revised post-R1) |
| **Dissent 2 — 9-category enum over-fitted to n=12** | **PARTIALLY RESOLVED.** Enum evolution note + provisional-flag mechanism added. Categories with n=1 are flagged provisional; future non-fitting scans classify as `other` + trigger deferred-ledger entry. However, `agentic-platform`, `install-script-fetcher`, and `specialized-domain-tool` remain as full categories with zero V1.2 empirical support — the provisional flag doesn't distinguish them from n=1 categories like `embedded-firmware` that actually have a V1.2 scan. | §3 enum evolution note (added post-R1) |
| **Dissent 3 — Q2 absence from rule table (30% of overrides)** | **NOT RESOLVED.** The design still has zero Q2 rules. The brief's settled directives table does not include Q2, so this remains an open gap. The design should document Q2 deferral rationale and timeline. | §5 (no Q2 rules) |
| **§3 item 1 — Q2 completely absent** | **NOT RESOLVED.** Same as above. | §5 (no Q2 rules) |
| **§3 item 2 — confidence field has no behavioral consequence** | **NOT RESOLVED.** `confidence` still defined on `ShapeClassification` with no downstream behavioral rule. | §4 `ShapeClassification` NamedTuple |
| **§3 item 3 — no test for shape-classifier stability across harness changes** | **NOT RESOLVED.** No regression test requirement added. | §10 (tests section unchanged) |
| **§4 item 1 — `specialized-domain-tool` should collapse into `other`** | **NOT RESOLVED.** Category kept. Evolution note doesn't address the "catchall that isn't `other`" problem. | §3 (category preserved) |
| **§4 item 2 — `agentic-platform` should collapse into `other`** | **NOT RESOLVED.** Category kept. n=0 in V1.2 scans. | §3 (category preserved) |
| **§4 item 3 — `install-script-fetcher` should collapse into `other`** | **NOT RESOLVED.** Category kept. n=0 in V1.2 scans. | §3 (category preserved) |
| **§4 item 4 — `matched_rule` field should be removed from schema** | **NOT RESOLVED.** Still in `ShapeClassification` NamedTuple. | §4, §10 |
| **§5 — RULE-3 keep-or-drop (I said prune)** | **PARTIALLY RESOLVED.** Narrow rewrite with positive-signal evidence requirement addresses my "ghost rule" concern. The trigger now requires `has_codeql OR releases_count >= 20`, which means it won't fire on wezterm (which I flagged as a false-positive risk). Confidence raised to firm. I can accept this as a narrow tie-breaker. | §5 RULE-3 (revised post-R1) |

## §3 Per-question answers (R2 focus areas A/B/C)

### A. Did the §9 Q9 reframing land correctly?

**ANSWER:** Yes, with one structural concern about the re-validation requirement.

**REASONING:** The staged-promotion mechanism (≤5/12 hard floor, ≤3/12 stretch that auto-promotes when ≥2 of V12x-7/11/12 land) resolves my R1 circular-dependency flag. The arithmetic works: §8 projects ~5/12 overrides with firm rules, so the hard floor is achievable; the stretch target is gated on the precondition that makes it achievable. The "≥2 of 3" gate is the right number — "any 1" is too permissive (a single harness signal could promote the floor before the rule set is ready), and "all 3" is too strict (V12x-7/11/12 are independent backlog items with different timelines). My structural concern: when the stretch target auto-promotes mid-Phase-3-or-later, previously-passing scans that had ≤5/12 overrides may now fail the tighter ≤3/12 floor. The design doesn't specify whether those scans need re-validation. This is manageable — the re-render comparison doc (§8) would catch it — but should be explicit. Codex's "remaining override classes" framing is subsumed by the staged numeric floor; it adds descriptive value but doesn't change the acceptance logic.

### B. Is the new shape-enum evolution note + provisional-flag mechanism adequate?

**ANSWER:** Adequate for Phase 1, but needs two operational additions before Phase 3 implementation.

**REASONING:** The provisional flag is a good start — it acknowledges the over-fit risk without collapsing categories prematurely. But it lacks operational teeth. The design needs: (a) a target n=2 promotion criterion before a provisional category becomes "stable" — currently the evolution note says categories with n=1 are provisional but doesn't say what happens at n=2 (does it auto-promote to stable? does it require a design revision?); (b) a confidence-degradation rule — when `classify_shape()` lands on a provisional category, its confidence should degrade to "medium" at most, and shape-conditional rules that branch on that category should require higher confidence to fire. The browser-extension boundary clarification is adequate: `desktop-application` with `is_privileged_tool` modifier covers the current cases. The `is_privileged_tool` modifier does need sharper definition — "browser extension with broad permissions" is vague. I'd define it as: extension manifest declares `host_permissions` matching `["<all_urls>", "*://*/*", "file:///*"]` or `permissions` including `nativeMessaging` + `tabs` + `cookies`.

### C. Is the rule precedence contract complete?

**ANSWER:** Mostly complete. Two gaps: cross-cell ordering effects and `rule_id` traceability.

**REASONING:** The first-match-wins contract in §2 is well-specified for single-cell evaluation. The auto-fire short-circuit is correct. The gap is cross-cell ordering: when RULE-6 (auto-fire, Q4) AND RULE-1 (base-table, Q1) both fire on different cells in the same scan, there's no cross-cell ordering effect — each cell evaluates independently. But what about RULE-10 (validator guard, cross-cell)? RULE-10 evaluates the *verdict*, which aggregates findings from all cells — if RULE-6 fires Q4=red and RULE-1 fires Q1=amber, the verdict is still finding-severity-driven, not cell-driven. The design should explicitly state that cross-cell ordering effects are zero because cells evaluate independently and verdict is findings-driven. On `rule_id` traceability: yes, the design should require it. Every cell evaluation should record which rule fired (or "fallback" / "override") in the form.json output. The §10 schema addition (`phase_3_advisory.scorecard_hints.<q>.rule_id`) is the right place. This is essential for audit + debugging — without it, a future Phase 5 re-render can't tell why a cell landed at a particular color. I'd make it required, not optional.

## §4 Cross-agent reactions

**AGREE with Codex** on the phase-boundary issue (classify_shape Phase 4 fallback) — this was correctly resolved as a FIX-NOW directive. Also agree with Codex's "remaining override classes" framing as a complementary descriptive tool, though I don't think it needs to be a separate acceptance metric.

**AGREE with Pragmatist** on RULE-3 operator-precedence ambiguity — the revised design's parenthesized trigger resolves this. Also agree with Pragmatist's practical concern about the template-map fallback (no-rule-fired case) — the design added fallback-to-LLM-authored-short_answer behavior post-R1, which addresses this.

**DISAGREE with Codex** on the browser-extension split. Codex wanted a separate `browser-extension` category or a first-class `is_browser_extension` modifier. I think the owner's directive (desktop-application with `is_privileged_tool` modifier) is the right call — a pure browser extension with no native component is still a desktop application from the user's threat-model perspective. Adding a separate category would increase the enum surface for a distinction that the cross-shape modifiers already capture.

**DISAGREE with Pragmatist** on folding RULE-5 into a comment. I value the explicit traceability of naming every rule condition — RULE-5 documents why Q3=amber for ruleset-disclosed repos, which is useful for future audits. The bookkeeping cost (one test, one template key) is negligible.

**Codex surfaced something I missed:** the modifier independence / double-counting risk between `is_privileged_tool` and Q4 rules that both consume dangerous primitives. This needs explicit documentation in the design — a note that `is_privileged_tool` is a shape-level modifier (elevated permissions context) while Q4 rules consume specific dangerous-primitive signals (exec, deserialization, cmd_injection). They're independent axes; double-counting is not a risk because they affect different cells (Q1/Q4 for `is_privileged_tool`, Q4 only for dangerous primitives).

## §5 New dissents (formal record — required even if empty)

**New Dissent 1 — `confidence` field still has no behavioral consequence.**

- **WHAT:** The `ShapeClassification.confidence` field is defined ("high"/"medium"/"low") but no rule, validator check, or fallback behavior depends on it.
- **WHY:** A field that is defined but never consumed is dead weight in the schema. It creates the illusion of graceful degradation without actually providing it. When `classify_shape()` returns `confidence="low"` (which will happen for `other`-category scans and provisional-category scans), the rule table should degrade: shape-conditional rules should not fire, and the fallback advisory color should be preferred. Without this, low-confidence classification silently produces the same output as high-confidence classification, which is worse than not having the field.
- **WHETHER YOU'D BLOCK:** No — this is a Phase 3 implementation concern, not a design blocker. But if Phase 3 ships without a behavioral consequence for `confidence`, I'd flag it as a regression in R3.

**New Dissent 2 — Q2 gap remains undocumented.**

- **WHAT:** The design has zero Q2 rules despite Q2 accounting for 30% of overrides (3 of 10 per audit). The R2 brief's settled directives table does not include Q2, so this remains an open gap.
- **WHY:** The design's scope is "cells" — Q2 is a cell. Excluding it without documentation means 30% of the override problem is unaddressed and unplanned. The design should at minimum state: "Q2 is deferred to Phase 1.5 because Q2 overrides are driven by finding-severity patterns (Kronos: Critical findings drive Q2=red; Xray-core: network-tooling risk drives Q2=red; skills: young-repo sample-floor drives Q2=amber) that require the finding-severity programmaticization work scoped for Phase 1.5." This would make the deferral principled rather than accidental.
- **WHETHER YOU'D BLOCK:** No — not a blocker for Phase 1 acceptance. But the design should add this documentation before Phase 3 implementation starts.

## §6 R3 carry-forwards

1. **Q9 staged floor ratification.** All 3 agents converged in R1 that the original ≤3/12 floor was unachievable. The revised ≤5/12 hard + ≤3/12 staged stretch resolves the circular dependency. R3 should ratify this as settled and confirm the "≥2 of 3" gate.

2. **Shape enum stability review trigger.** All 3 agents flagged enum granularity concerns. R3 should define: after how many additional V1.2 scans (proposal: 12 more, matching the current evidence base) should the enum undergo a stability review? If >2 misclassifications occur in those 12 scans, the enum should collapse to 6 categories (my R1 position) or be revised.

3. **Q2 gap documentation.** R3 should confirm whether the design adds explicit Q2 deferral documentation before Phase 3 implementation. This is a low-cost item (one paragraph in §5 or §7) that prevents future confusion about why Q2 overrides persist.

4. **`confidence` field behavioral consequence.** R3 should decide: (a) add a behavioral rule (low confidence → shape-conditional rules don't fire), (b) remove the field from the schema, or (c) defer to Phase 3 implementation with a requirement that it must be consumed. My position is (a); I expect Pragmatist to prefer (b) and Codex to prefer (c).

5. **`rule_id` traceability requirement.** All 3 agents value traceability. R3 should confirm that `phase_3_advisory.scorecard_hints.<q>.rule_id` is required (not optional) in the Phase 3 implementation, and that the re-render comparison doc records which rule fired per cell.
