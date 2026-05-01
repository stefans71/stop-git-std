# Calibration Rebuild — Board Review CONSOLIDATION

**Topic:** stop-git-std calibration design v2 — rule-table rebuild for the 4 scorecard cells
**Date:** 2026-05-01 (single-day review across 3 rounds)
**Outcome:** **3-of-3 SIGN OFF** (R3). Design approved for Phase 3 implementation.
**Archive trigger:** Phase 2 of `docs/back-to-basics-plan.md`. Predecessor: Phase 0 audit (`docs/calibration-audit.md`); Phase 1 design (`docs/calibration-design-v2.md`).

---

## §1 Scope + context

The owner observed that the existing scorecard rule table (in `docs/compute.py::compute_scorecard_cells`) over-calls risk on the OSS-default solo-maintainer pattern, biasing the LLM-mediated consumer workflow ("paste .md into LLM, ask 'should I install this?'") toward false-cautious answers. Phase 0 audit confirmed empirically: ~83% of V1.2 wild scans (10 of 12) had a Phase 4 LLM cell-color override, the override mechanism was carrying shape-aware judgment work that should be expressed as deterministic rules, and Q1+Q3 cells in particular fired red on the OSS-default pattern (no protection + low formal review + no SECURITY.md) without distinguishing it from genuine failure modes.

Phase 1 produced `docs/calibration-design-v2.md` — a rule-table rebuild proposing: shape-as-modifier architecture, 9-category closed-enum shape classifier, 10 specific rules (RULE-1 through RULE-10) addressing the audit's findings, template-map cell short_answer language, and migration plan for the 27-scan re-render. The design covers cells only; finding-severity rule-driving is owner-confirmed deferred to a separate Phase 1.5.

This board review (Phase 2) was a 3-model FrontierBoard governance review on the design, followed by archive per FrontierBoard SOP §4.

**Composition:**
- **Pragmatist:** Claude Sonnet 4.6 (same-model-blind-spot rule applies — Opus authored the design)
- **Systems Thinker:** OpenAI Codex GPT-5
- **Skeptic:** DeepSeek V4

---

## §2 Round-by-round verdict trajectory

| Agent | R1 (Blind) | R2 (Consolidation) | R3 (Confirmation) |
|---|---|---|---|
| Pragmatist | SIGN OFF WITH NOTES | SIGN OFF WITH NOTES | **SIGN OFF** (clean) |
| Codex | SIGN OFF WITH NOTES | SIGN OFF WITH NOTES | SIGN OFF WITH NOTES |
| DeepSeek | **DISSENT** | SIGN OFF WITH NOTES | SIGN OFF WITH NOTES |

**Net:** DeepSeek moved DISSENT → conditional sign-off across the 3 rounds. Pragmatist cleaned up to a clean SIGN OFF in R3. Codex stable throughout. **Final R3: 3-of-3 SIGN OFF.**

**Archive disposition:** APPROVED for Phase 3 implementation. No preserved-live blocking dissents. Codex's R3 preserved dissent (Q2 deferral implicit) was raised-and-resolved-pre-archive by the §5 Q2-deferral doc fix in commit `f42635f`.

---

## §3 Owner directives applied across all 3 rounds (15 items)

### R1-round directives (8 items, applied between R1 and R2)

| # | Section affected | Change | Driver |
|---|---|---|---|
| 1 | §9 Q9 | Hard floor revised from ≤3/12 to ≤5/12; stretch target ≤3/12 auto-promotes to hard floor when ≥2 of V12x-7/V12x-11/V12x-12 harness signals land | 3-of-3 R1 convergent (all flagged unachievable with firm rules only) |
| 2 | §4 classify_shape | Drop `phase_4_structured_llm.catalog_metadata.shape` Phase 4 fallback; classifier returns `("other", confidence="low")` when no clean match; preserves Phase 3 deterministic authority | Codex FIX-NOW |
| 3 | §5 RULE-3 | Narrow rewrite — drop agent-skills-collection branch (covered by RULE-4 on Q3); new trigger `(is_solo_maintained) AND (NOT is_privileged_tool) AND (has_codeql OR releases_count >= 20)`; confidence raised lower → firm | Codex + DeepSeek + Pragmatist (operator-precedence flag) |
| 4 | §3 enum + new evolution note | Acknowledge over-fit risk; categories with n=1 representation flagged provisional; future non-fitting scans → `other` + deferred-ledger entry; no emergency taxonomy changes | DeepSeek |
| 5 | §3 browser-extension boundary | Browser extensions with native messaging hosts → `desktop-application` (extension is install vector; native host is execution surface). Modifier `is_privileged_tool` fires when extension permissions are broad | Codex |
| 6 | §2 rule precedence contract | First-match-wins in priority order; auto-fire short-circuits; among non-auto-fire, first matching rule in listed order wins; no combining/averaging | Codex (under-specified flag) |
| 7 | §6 template-map fallback | When template_key has no match, fall back to LLM-authored `short_answer` (not blank/error); validator warns on miss; errors only when both miss AND empty | Pragmatist |
| 8 | §9 Q7 reframed | Q7 (cells-only scope) marked DECIDED with rationale; reduces board's R1 decision load (was originally an open question) | Owner pre-board |

### R2-round directives (7 items, applied between R2 and R3)

| # | Section affected | Change | Driver |
|---|---|---|---|
| 9 | §9 Q9 — Promotion semantics | When ≤3/12 stretch promotes to hard floor: applies **prospectively only**. Existing passing scans NOT retroactively failed (correct at calibration level evaluated under). Diagnostic re-evaluation is a comparison-doc query, not a gate | Codex + Pragmatist convergent |
| 10 | §9 Q9 — "Remaining override classes" framing | Track in comparison doc as **diagnostic-only**. Hard floor remains raw count (≤5/12 → ≤3/12). Class distribution informs next calibration push direction; does NOT gate Phase 1 | Codex (R3 carry-forward) |
| 11 | §3 — Provisional-to-stable promotion | Provisional categories promote to stable at **n≥2 V1.2 scans classifying cleanly**. Phase 3 implementation decides tracking mechanism | Codex + DeepSeek (R3 carry-forward) |
| 12 | §10 — Phase 3 must resolve | New sub-section names 3 items intentionally NOT specified: provisional-vs-stable tracking mechanism, `is_privileged_tool` boundary cases, confidence-degradation rules | Codex (R3 carry-forward) + Pragmatist + DeepSeek |
| 13 | §10 — `confidence` field | DEBUG-ONLY. No rule reads it. Tracked in form.json for audit (correlation between low-confidence classifications and override spikes). Wire to rule degradation only if a future audit shows justifying evidence | Pragmatist + DeepSeek convergent (Codex echoed) |
| 14 | §10 — `rule_id` traceability | REQUIRED on every cell evaluation (changed from optional). Rule_id values: `RULE-1` through `RULE-10` or `FALLBACK`. Validator enforces presence on every cell | Codex (R3 carry-forward) |
| 15 | §9 Q9 — ≥2-of-3 harness threshold | Confirmed: any 2 of {V12x-7, V12x-11, V12x-12} landing is the trigger for stretch-to-hard-floor promotion | Codex (R3 carry-forward) |

### R3-round directive (1 item, applied between R3 and archive — pre-archive doc fix)

| # | Section affected | Change | Driver |
|---|---|---|---|
| 16 | §5 — new Q2 sub-section | Explicit "Q2 — NO RULE CHANGES (explicit deferral)" sub-section added. Documents rationale (audit found Q2 well-calibrated; only 2 of 10 V1.2-scan overrides were Q2; addressed by V1.2.x signal widening rather than rule-table changes; skills sample-floor case routes through RULE-4 on Q3 not Q2). Phase 1.5 re-entry trigger documented (≥3 Q2 overrides in next 5 wild scans, OR Phase-1 re-render audit miscalls). Resolves Codex's preserved R3 dissent | 3-of-3 R3 convergent (Pragmatist + Codex + DeepSeek); Codex preserved dissent → "raised-and-resolved-pre-archive" |

---

## §4 Pre-archive dissent audit (SOP §4 — zero silent drops)

Every concern raised by any agent in any round is classified below. The audit is the SOP §4 invariant — if a concern was raised but does not appear here with a disposition, it was silently dropped and the archive is invalid. **All concerns accounted for.**

### R1 concerns

| Source | Concern | Disposition |
|---|---|---|
| Pragmatist R1 §1 | Q9 ≤3/12 floor unachievable with firm rules only | RESOLVED — directive #1 (staged floor) |
| Pragmatist R1 §3 | RULE-3 trigger has Python operator-precedence ambiguity | RESOLVED — directive #3 (narrow rewrite + parenthesization) |
| Pragmatist R1 §3 | Template-map fallback behavior under-specified | RESOLVED — directive #7 |
| Codex R1 §5 (FIX-NOW) | classify_shape() should not depend on Phase 4 LLM-authored shape, even as runtime fallback | RESOLVED — directive #2 |
| Codex R1 §5 (DEFER-WITH-NOTE) | Q9 ≤3/12 too strict for Phase 1 as currently scoped | RESOLVED — directive #1 |
| Codex R1 §6 | RULE-3 status (keep/prune/narrow-rewrite) | RESOLVED — directive #3 (narrow rewrite chosen) |
| Codex R1 §6 | Browser-extension vs native-desktop shape boundary | RESOLVED — directive #5 |
| Codex R1 §6 | Per-cell precedence contract for multiple matching rules | RESOLVED — directive #6 |
| Codex R1 §6 | Specialized-domain-tool category low-confidence framing | DEFERRED — provisional-flag mechanism (directive #4 + #11) |
| DeepSeek R1 §1 (DISSENT) | Override reduction projection (~83% → ~12%) unsupported by firm rules alone | RESOLVED — directive #1 (staged floor breaks circular dependency) |
| DeepSeek R1 §1 | 9-category enum over-fitted to 12 scans | RESOLVED — directive #4 (evolution note + provisional flag) + #11 (n≥2 promotion) |
| DeepSeek R1 §1 | Q9 hard floor circular dependency | RESOLVED — directive #1 |
| DeepSeek R1 §3 | RULE-7/8/9 should move to Phase 1.5 deferred ledger | NOT RESOLVED (owner directive: stay in design with promotion gates — promotion gate IS the discipline). PRESERVED-AS-OWNER-OVERRULE — DeepSeek's recommendation noted; owner kept rules in design with explicit gates |

### R2 concerns

| Source | Concern | Disposition |
|---|---|---|
| Pragmatist R2 §3 | Staged-promotion retroactivity scope unclear | RESOLVED — directive #9 (prospective-only) |
| Pragmatist R2 §3 | `confidence` field defined-but-unused | RESOLVED — directive #13 (debug-only) |
| Codex R2 §3 | Q9 staged-floor operational contract (re-validation requirement on previously-passing scans) | RESOLVED — directive #9 (prospective-only) |
| Codex R2 §3 | Provisional-category promotion criteria + confidence-degradation | DEFERRED to Phase 3 — directive #11 (n≥2 promotion criterion + Phase 3 implementation choice) + directive #12 (§10 "Phase 3 must resolve" sub-section) |
| Codex R2 §3 | `is_privileged_tool` boundary cases (browser extensions, native hosts, terminal emulators, shell extenders, embedded firmware) | DEFERRED to Phase 3 — directive #12 (§10 "Phase 3 must resolve") |
| Codex R2 §6 | `rule_id` traceability should move from optional to required | RESOLVED — directive #14 (REQUIRED + validator-enforced) |
| Codex R2 §6 | "Remaining override classes" as diagnostic vs primary gate | RESOLVED — directive #10 (diagnostic-only) |
| DeepSeek R2 §3 | 3 enum categories with zero V1.2 evidence (`agentic-platform`, `install-script-fetcher`, `specialized-domain-tool`) | DEFERRED + factual correction — provisional-flag mechanism (directive #4 + #11) is the response. NOTE: `specialized-domain-tool` actually has 2 V1.2 scans (freerouting + Kronos); DeepSeek's count was off |
| DeepSeek R2 §3 | `confidence` field continued lack of behavioral consequence | RESOLVED — directive #13 (debug-only with audit-correlation justification) |
| DeepSeek R2 §5 | Q2 gap undocumented | RESOLVED — directive #16 (R3-round pre-archive doc fix) |

### R3 concerns

| Source | Concern | Disposition |
|---|---|---|
| Pragmatist R3 §4 | Q2's absence from rule table lacks prose explanation in design body | RESOLVED — directive #16 (§5 Q2 sub-section) |
| Codex R3 §5 (preserved dissent) | Q2 remains outside rule-table redesign but design never states deferral explicitly — SOP §4 silent-drop documentation issue | RESOLVED via directive #16 — recorded as "raised-and-resolved-pre-archive" rather than "preserved live" |
| DeepSeek R3 §5 | Q2 gap undocumented deferral | RESOLVED — directive #16 |
| DeepSeek R3 §5 | Shape-classifier regression test requirement absence | DEFERRED to Phase 3 — directive #12 implicitly covers this (§10 "Phase 3 must resolve" + the existing Phase 3 test plan in §10 already calls for tests/test_classify_shape.py against 12 V1.2 bundles, which IS the regression test requirement; DeepSeek's flag is essentially "make sure that test plan is enforced" — Phase 3 implementation discipline) |

**Audit summary:**
- **Total concerns audited:** 26 across 3 rounds × 3 agents
- **RESOLVED in design:** 18
- **DEFERRED to Phase 3 (via §10 "Phase 3 must resolve" + provisional-flag mechanism):** 7
- **PRESERVED live as R3 dissent:** 0
- **NOT RESOLVED with explicit owner overrule (preserved as record):** 1 (DeepSeek's "RULE-7/8/9 to Phase 1.5 ledger" recommendation — owner kept in design with promotion gates; rationale documented in directive #11)
- **Silent drops (concerns raised but not accounted for):** 0 ✓ — SOP §4 invariant satisfied

---

## §5 Phase 3 carry-forwards

The following items are explicitly deferred to Phase 3 implementation per the design's §10 "Phase 3 must resolve" sub-section. Phase 3 implementation MUST address these — they're not "nice to have," they're follow-on decisions the design intentionally left open because they depend on harness signal availability or implementation preference:

1. **Provisional-vs-stable category tracking mechanism** — counter file vs derived-from-catalog computation vs annotation on each `ShapeClassification` result. Owner-decided criteria: n≥2 V1.2 scans classifying cleanly → promote to stable. Phase 3 chooses bookkeeping.
2. **`is_privileged_tool` boundary cases** — boundary specs for: browser extensions (broad vs narrow permissions), native messaging hosts (which permission scope), terminal emulators (SSH-handling vs not), shell extenders (path scope), embedded firmware (always privileged or shape-dependent). The design §3 table classifies KNOWN cases; Phase 3 codifies the decision boundary in the helper based on what `phase_1_raw_capture` actually exposes.
3. **Confidence-degradation rules** — whether `classify_shape` should output lower confidence when landing on a provisional category (vs when lacking input signals vs when matching multiple rules). Owner directive: defer to Phase 3 + future audit data; do not pre-engineer.
4. **Shape-classifier regression test requirement** — `tests/test_classify_shape.py` against all 12 V1.2 bundles must produce expected categories per design §3 table. This is a blocker for `compute_scorecard_cells_v2()` integration.
5. **`rule_id` validator enforcement** — validator must enforce that every cell in `phase_3_advisory.scorecard_hints.<q>` has a `rule_id` field. Add a validator check in `--form` mode.

Additionally, Phase 1.5 re-entry triggers (preserved here so they aren't lost):

- **Q2 calibration scope** — re-enters scope if (a) Phase 1 re-render audit shows Q2 calibration miscalls beyond the 2 V1.2 cases (Kronos, Xray-core), OR (b) the next 5 V1.2 wild scans surface ≥3 Q2 overrides. Likely paired with Phase 1.5 finding-severity rule-driving design.
- **Finding-severity rule-driving (Phase 1.5 separate audit + design)** — the audit covered cells; the broader "~90% programmatic" target also requires programmaticizing finding-severity assignment. Per owner directive (R1-round Q7), this is its own phase, not bundled with cell calibration.

---

## §6 Final verdict + archive disposition

**APPROVED for Phase 3 implementation.** Three-of-three R3 SIGN OFF. Zero preserved-live blocking dissents. Pre-archive dissent audit (SOP §4) confirms zero silent drops across 26 cross-round concerns.

DeepSeek's R1 DISSENT was substantive and contributed to several R1-round revisions (over-fit flag → directive #4; Q9 circular dependency → directive #1). Owner-overrule on RULE-7/8/9 disposition (kept in design with promotion gates rather than moved to Phase 1.5 ledger) is recorded for future reference; rationale was that the promotion gate IS the discipline, and keeping rules in design means they activate the moment evidence arrives.

Codex contributed the architectural FIX-NOW that closed the largest single design defect (classify_shape phase boundary) and the rule-precedence contract that makes the design operationally tractable. Pragmatist contributed the operational-detail flags (template-map fallback, operator-precedence) that surfaced as small but important hygiene fixes. The design as-archived is meaningfully better than the as-authored version because of the board's work.

**Phase 3 implementation may now proceed.** Branch: `chore/calibration-rebuild-impl` (per `docs/back-to-basics-plan.md` § Phase 3). Phase 3 must address the §5 carry-forwards above before completion.

---

## §7 Cross-references

- **Design doc (the artifact reviewed):** `docs/calibration-design-v2.md` (twice-revised as of archive; see §9 revision history of the design doc for change log)
- **Phase 0 audit (empirical baseline):** `docs/calibration-audit.md`
- **Plan (parent project):** `docs/back-to-basics-plan.md` § Phase 1 + Phase 2
- **Round outputs:** `050126-calibration-rebuild/{r1,r2,r3}-brief.md`, `{pragmatist,codex,deepseek}-{r1,r2,r3}.md`
- **DeepSeek raw logs:** `050126-calibration-rebuild/deepseek-{r1,r2,r3}-raw.log`
- **FrontierBoard SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
- **Existing telemetry referenced:** `docs/v12-wild-scan-telemetry.md`

---

## §8 Agent invocation snapshot (for SOP compliance + future replay)

**Pragmatist (Sonnet 4.6):**
```
Agent tool
  subagent_type="general-purpose"
  model="sonnet"   (same-model-blind-spot rule — Opus authored design)
  prompt: per-round brief at /root/tinkering/stop-git-std/.board-review-temp/
          calibration-rebuild/r{1,2,3}-brief.md
```

**Systems Thinker (Codex GPT-5):**
```bash
sudo -u llmuser bash -c "cd /tmp && codex exec \
  --dangerously-bypass-approvals-and-sandbox '<role-specific prompt referencing
   /tmp/calibration-rebuild-r{1,2,3}-brief.md>'" \
  > /tmp/calibration-rebuild-codex-r{1,2,3}-raw.log 2>&1
```

**Skeptic (DeepSeek V4):**
```bash
OPENAI_API_KEY="$DEEPSEEK_API_KEY" \
OPENAI_BASE_URL="https://api.deepseek.com/v1" \
  qwen -y -p "<role-specific prompt referencing
              .board-review-temp/calibration-rebuild/r{1,2,3}-brief.md>" \
  --model deepseek-chat \
  > .board-review-temp/calibration-rebuild/deepseek-r{1,2,3}-raw.log 2>&1
```

All three rounds executed across one session on 2026-05-01. Total wall-clock: ~90 minutes. Total agent token usage: ~360k across 9 invocations + ~45k coordination tokens in main session.
