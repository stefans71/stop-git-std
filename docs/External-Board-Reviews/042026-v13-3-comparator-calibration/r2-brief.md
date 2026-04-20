# V13-3 Board Review — R2 Consolidation Brief (Stateless)

**Review topic:** V13-3 — 11-scan comparator calibration analysis. Triggered 2026-04-20 at catalog entry 26 (WhiskeySockets/Baileys), the 11th V1.2-schema wild scan.

**Round:** R2 Consolidation. R1 Blind complete — 3 agents voted independently. This round preserves disagreement where it exists and pushes convergence only where the three R1 positions can honestly be merged.

**Agent instruction:** You are **STATELESS** — read this brief as if you've never seen the project. All three R1 outputs are inlined verbatim in §9 below. Do not treat your own prior R1 output as already-known context; re-read it here. The R1 brief is referenced at `/root/tinkering/stop-git-std/.board-review-temp/v13-3-comparator-calibration/r1-brief.md` for full context (366 lines); this R2 brief re-briefs only the deltas and consolidated items.

---

## 1. Context refresh (compressed)

`stop-git-std` is an LLM-driven GitHub repo security scanner. `docs/phase_1_harness.py` gathers facts; `docs/compute.py` derives Phase 3 advisory signals; LLM authors Phase 4 structured findings + Phase 5 prose into a `form.json`; renderers produce MD + HTML; `docs/validate-scanner-report.py` gates. Schema V1.2 is live (shipped 2026-04-20 via D-7 + D-8 board review). V13-1 owner-directive work shipped same session: expanded `override_reason_enum` from 5→7 values (+`signal_vocabulary_gap`, +`harness_coverage_gap`).

**V13-3 trigger (CONSOLIDATION §8 line 397):** "11-scan comparator calibration analysis | V1.2 schema frozen + telemetry exists + ≥11 V1.2 scans collected". Fired at catalog entry 26 (Baileys, 2026-04-20). Analysis is now owed.

**Across 11 V1.2 wild scans (entries 16-26):** 9 overrides total, `signal_vocabulary_gap` 67% modal, `harness_coverage_gap` 22%, `threshold_too_strict` 11%, 4 of 7 enum values unexercised, Q4 is the override hotspot (5/9), 11/11 silent-fix pattern (0 published GHSA advisories) with 2 concretely-documented disclosure-handling failures (WLED #5340, Baileys PR #1996).

Full R1 brief: `/root/tinkering/stop-git-std/.board-review-temp/v13-3-comparator-calibration/r1-brief.md`.

---

## 2. R1 outcome — vote matrix

| Q | Question | Pragmatist | Systems (Codex) | Skeptic (DeepSeek) | Outcome |
|---|---|---|---|---|---|
| **V3Q1** | V13-3 scope | A3 both | A3 both | A2 broad | ⚠️ **2/3 A3, 1 A2** |
| **V3Q2** | Priority 1 deserialization | B1 land | B1 land | B2 defer | ⚠️ **2/3 B1, 1 B2** |
| **V3Q3** | Priority 1b firmware CORS | C2 defer | C2 defer | C2 defer | ✅ **Converged C2** |
| **V3Q4** | Priority 1c reverse-eng | D2 defer | D2 defer | D3 reject | ⚠️ **2/3 D2, 1 D3** |
| **V3Q5** | Q3 rubric | E2 add enum | E3 keep | E3 keep | ⚠️ **2/3 E3, 1 E2** |
| **V3Q6** | V1.3 enum pruning | F2 prune 1 | F2 prune 1 | F3 prune none | ⚠️ **2/3 F2, 1 F3** |
| **V3Q7** | Follow-up cadence | G3 conditions | G4 N=25 or events | G2 N=25 | ⚠️ **3-way split** |
| **H** | Process | H2 directive | H1 full board | H1 full board | ⚠️ **2/3 H1** |

**Converged on 1/8 (V3Q3).** Majority-positioned on 6/8. True 3-way split on V3Q7.

Per SOP §4 Round 2 tiebreaker rules:
- 2-of-3 agree → majority classification, note dissent
- 3-way split → highest severity proposed, flag for R3
- Owner directives override

---

## 3. Owner directives

**OD-1 (on H, process):** Continue with full board. 2/3 voted H1 (full board) and the multi-axis scope + schema/rubric/enum implications justify the R2-R3 cycle cost. Pragmatist's H2 (owner directive after R1) is noted as dissent and applied asymmetrically: **the items where R1 is unanimous or near-unanimous (V3Q3, C1/C3/C4 FIX NOW themes in §4) are candidates for Round-2-close**; items with genuine dissent (V3Q5, V3Q7 especially) continue to R3 if R2 doesn't converge.

**OD-2 (scope ground rule):** V13-3's output is the frozen analysis document `docs/v13-3-analysis.md` mirroring the `docs/v13-1-override-telemetry-analysis.md` structural template. The existing `docs/v12-wild-scan-telemetry.md` remains living (appended after each new wild scan); `v13-3-analysis.md` is the frozen snapshot citing entries 16-26 at their commit SHAs.

**OD-3 (historical bundle rule):** Entries 16-26 are historical. V13-3 MAY simulate override collapse counterfactually (for evaluating Priority 1/1b/1c), but MUST NOT re-render historical bundles or update their `override_reason` records. This codifies the rule from CONSOLIDATION §8.2 final paragraph.

---

## 4. Consolidated R1 items (for R2 voting)

All items from R1 responses (FIX NOW + DEFER + INFO + blind spots + open questions) are consolidated here with C-IDs for R2 voting. **Vote AGREE / DISAGREE / MODIFY on each.** Blank-positioned items are also in scope — if you didn't address the topic in R1, you can still AGREE / DISAGREE / MODIFY in R2.

### 4.1 FIX NOW candidates

**C1 — Write `docs/v13-3-analysis.md` as a frozen A3-scoped document** (from Systems C-1 + Pragmatist INF-3)

Source: Systems said "Define V13-3 as A3 in the written analysis and explicitly state that Reading A is closed by D-6 while Reading B remains the actionable calibration surface." Pragmatist said "The `docs/v13-3-analysis.md` document format should mirror `docs/v13-1-override-telemetry-analysis.md` structurally — that's the established template for this class of analysis and it worked well."

Proposed classification: **FIX NOW**. Owner is willing to author. Pragmatist and Systems positions are compatible; Skeptic did not explicitly address the deliverable-shape question.

**Vote:** AGREE / DISAGREE / MODIFY (propose different shape or deliverable).

**C2 — V12x-9 language qualifier regex on deserialization family is HARD PREREQUISITE for Priority 1 auto-fire** (from Pragmatist FN-1 + Systems C-2)

Source: Pragmatist said "V12x-9 … MUST be treated as a hard prerequisite for V3Q2/Priority 1 auto-fire — not as a parallel-and-maybe item. … If Priority 1 ships without V12x-9, the WLED ArduinoJson FPs will trigger spurious Critical findings." Systems said "Priority 1 must ship paired with language-qualified matching, or it will contaminate Q4 advisory hints on non-deserialization code paths." Skeptic voted B2 (defer Priority 1 entirely); did not separately address the sequencing.

Proposed classification: **FIX NOW conditional on V3Q2 = B1**. If V3Q2 passes B1 (majority), then Priority 1 + V12x-9 ship together atomically. If V3Q2 flips to B2 in R2, C2 becomes moot.

**Vote:** AGREE / DISAGREE / MODIFY (e.g. keep V12x-9 separate, ship Priority 1 without it, defer both).

**C3 — Freeze entries 16-26 as historical bundles; V13-3 analysis models override collapse counterfactually, NOT by re-rendering** (from Systems C-3)

Source: Systems said "Freeze entries 16–26 as historical bundles; V13-3 analysis may model override collapse counterfactually, but must not re-render prior artifacts."

Proposed classification: **FIX NOW** (already codified as OD-3 above). Included here for explicit R2 agreement because all 3 agents implicitly assume it in their rationales. Owner-authored OD-3 version matches Systems' position verbatim.

**Vote:** AGREE / DISAGREE / MODIFY.

**C4 — Document sample bias explicitly in V13-3 analysis** (from Skeptic C-1)

Source: Skeptic said "Document the sample bias explicitly in the V13-3 analysis. State clearly: '11 scans, Python/Rust heavy, missing major ecosystems.'"

Proposed classification: **FIX NOW**. Low-cost, high-value; constrains over-reading from the sample. Pragmatist's INF-1 implicitly agrees (notes the 82% scan-level rate needs explicit naming); Systems did not address.

**Vote:** AGREE / DISAGREE / MODIFY.

### 4.2 DEFER candidates

**C5 — V3Q2: Priority 1 deserialization auto-fire** — R1 voted B1 B1 B2 (2/3 land)

Majority (2/3) land in V1.2.x. Skeptic dissents (B2 defer): "language qualifier is a bigger change than 'additive signal'; it's a semantic rewrite of the deserialization family."

Proposed classification: **LAND as V1.2.x (majority)**, paired with C2 (V12x-9 blocker). Skeptic's dissent preserved; if R2 Skeptic MODIFIES to articulate specific harm, R3 deliberation follows.

**Vote:** AGREE (B1) / DISAGREE (B2) / MODIFY.

**C6 — V3Q3: Priority 1b firmware CORS compound signal** — R1 voted C2 C2 C2 (3/3 defer)

All 3 agents voted C2 (defer to V1.3). No dissent.

Proposed classification: **DEFER to V1.3**. Trigger for re-evaluation: ≥2 additional firmware/IoT shape scans in V1.2 catalog, OR shape-classification infrastructure lands independently.

**Vote:** AGREE / DISAGREE / MODIFY.

**C7 — V3Q4: Priority 1c reverse-engineered-API shape signal** — R1 voted D2 D2 D3

Majority (2/3) defer; Skeptic rejects outright.

Proposed classification: **DEFER to V1.3** with Skeptic's REJECT dissent documented. Trigger for re-evaluation: ≥3 confirmed reverse-engineered-API-library scans in V1.2 catalog (e.g., whatsmeow, discord.py-self, instagrapi — all live candidates), AND dry-run FP test against 11 existing bundles shows 0 FPs.

**Vote:** AGREE (D2 defer) / DISAGREE-REJECT (D3 close permanently) / MODIFY.

**C8 — V3Q5: Q3 rubric adjustment** — R1 voted E2 E3 E3

Majority (2/3) keep rubric (E3). Pragmatist dissents (E2): "add `community_norms_differ` as a V1.3 candidate (DeepSeek's preserved dissent now has telemetric backing at 11/11); rubric change is a bigger cross-scan comparability event than it looks."

Proposed classification: **KEEP Q3 rubric as-is (majority E3)**, BUT add V13-4 follow-up work: re-evaluate `community_norms_differ` enum-addition proposal when 11/11 silent-fix reaches N=15 or when a Q3 override actually fires (first in catalog). This is a dual DEFER — the rubric change AND the enum addition both defer, but with different triggers.

**Vote:** AGREE (E3 + deferred V13-4) / DISAGREE (E2 land now) / MODIFY.

**C9 — V3Q6: V1.3 enum pruning** — R1 voted F2 F2 F3

Majority (2/3) prune `missing_qualitative_context`; Skeptic says keep all 4 unused values.

Skeptic rationale: "4 unused enum values after 11 biased samples doesn't mean they're dead — they're sleeping. … We haven't seen the shapes that would trigger them."

Pragmatist rationale: "11 scans is enough to drop `missing_qualitative_context` (the V13-1 split was designed to absorb it; it hasn't fired since), but not enough to prune `threshold_too_lenient`, `rubric_literal_vs_intent`, or `other`. The sample is heavily skewed."

Proposed classification: **F2 prune `missing_qualitative_context` only in V1.3 (majority)**. Keep `threshold_too_lenient`, `rubric_literal_vs_intent`, `other` as headroom. Skeptic's F3 absorbed: she agrees with not pruning those 3; disagrees on pruning the catchall. The narrow prune of the V13-1-superseded catchall is structurally different from the broader pruning Skeptic opposes.

**Vote:** AGREE / DISAGREE / MODIFY.

**C10 — V3Q7: V13-3 follow-up cadence** — R1 voted G3 / G4 (N=25 OR event) / G2 (N=25)

TRUE 3-WAY SPLIT per SOP §4 R2 rule: "highest severity proposed" means the most restrictive cadence. All 3 are re-trigger flavors:
- G2 (Skeptic): hard count, N=25
- G3 (Pragmatist): condition-based (modal >80%, ≥2 new enums fire, or no-label case)
- G4 (Systems): N=25 OR enum-escape/multi-label event (hybrid of G2+G3)

Systems' G4 is a compound superset of G2 and G3. Pragmatist's G3 is event-only. Skeptic's G2 is count-only.

Proposed classification: **G4 (Systems, superset)**. All 3 positions are satisfied under G4: the count-based trigger (G2) fires first if routine accumulation reaches 25 without the interesting events; the event-based triggers (G3) fire first if something structurally new happens.

**Vote:** AGREE / DISAGREE / MODIFY. This question is flagged for R3 deliberation if R2 doesn't converge.

### 4.3 INFO items (record without voting — preserve for V13-3 analysis document)

**C11 — 82% scan-level override rate is worth naming** (Pragmatist INF-1): "9 of 11 scans have ≥1 override … higher than the brief frames it. … worth naming explicitly in the V13-3 analysis document."

**C12 — Same 4 Q4 `computed_signal_refs` appear on freerouting + WLED + Baileys despite 3 different root causes** (Systems I-1): "useful symptom that the scorecard-hint vocabulary is underexpressive even when the override enum is adequate."

**C13 — Zero-override streak (wezterm → QuickLook → kanata) is positive calibration data** (Skeptic I-1): signal vocabulary works for some shapes; V13-3 should cite this as evidence of when compute is well-calibrated.

**C14 — `signal_vocabulary_gap` 67% suggests compute needs PRINCIPLED expansion, not one-off patches** (Skeptic I-2): Per Skeptic, "the expansion should be principled (new signal families), not one-off patches." Tension with C5 (land Priority 1 as additive signal) — noted but not blocking.

**C15 — Reading A and Reading B should not share maintenance home** (Systems I-2): "D-6 is executable and living; V13-3 analysis should be frozen and cited." Supports OD-2.

**C16 — V1.2-only scope for V13-3; no V2.4-era back-labeling** (Pragmatist INF-2): "Back-labeling V2.4 prose to machine-readable override categories is manual and error-prone. The V13-3 analysis document should note this as an explicit scope exclusion."

### 4.4 Open questions from R1 (R2 should answer or explicitly defer)

**C17 — V12x-6 (multi-ecosystem manifest parsing) scope landing decision** (Pragmatist OQ-1): V12x-6 affects 7 of 11 scans (Maven/Gradle/Cargo/Gomod/Bundler/.NET producing `runtime_count=0`). Brief treats it as a backlog item. Is V12x-6 V1.2.x scope or V1.3 scope?

Proposed classification: **DEFER to V1.3**. V12x-6 requires multi-ecosystem parser work (Java/Ruby/Rust/Go/.NET), substantially larger than Priority 1's additive-regex-plus-compute-derivation. Skeptic's "principled expansion not one-off patches" (C14) argues for bundling V12x-6 with the V1.3 compute expansion.

**Vote:** AGREE (V1.3) / DISAGREE (V1.2.x) / MODIFY.

**C18 — Canonical storage of "tool loads user files" derivation** (Systems OQ-1): If Priority 1 lands, where does operators' judgment about "tool loads user files" live so they don't recreate it ad hoc in scan drivers?

Proposed classification: **FIX NOW conditional on V3Q2=B1**. The derivation must be in `docs/compute.py` (a helper like `derive_tool_loads_user_files(repo_metadata, readme, install_paths) -> bool`), not in scan drivers. Aligns with the V13-1 precedent where `derive_q1_has_ruleset_protection()` and `derive_q2_oldest_open_security_item_age_days()` are in `docs/compute.py`.

**Vote:** AGREE / DISAGREE / MODIFY.

**C19 — V13-3 analysis document should include "historical vs counterfactual" section** (Systems OQ-2): "so later readers do not confuse simulated override collapse with actual bundle contents."

Proposed classification: **FIX NOW** (as section in the v13-3-analysis.md deliverable).

**Vote:** AGREE / DISAGREE / MODIFY.

**C20 — Dry-run FP rate test for harness patches before V1.3 promotion** (Skeptic OQ-1 + Pragmatist blind-spot): Apply proposed patches to 11 existing bundles, count suppressed safe-deserialization hits vs preserved unsafe hits; measure Priority 1c regex FP on 11 bundle READMEs.

Proposed classification: **FIX NOW for C5 (Priority 1)** (dry-run is part of the V1.2.x landing). **DEFER for C6/C7** (dry-run becomes part of V1.3 promotion gate).

**Vote:** AGREE / DISAGREE / MODIFY.

### 4.5 Blind spots raised

Recorded for R3 awareness:

- **BS-1 (Pragmatist):** compute.py derivation specifics for Priority 1 not traced end-to-end; V12x-9 language-qualifier risk on C/C++/Rust genuine unsafe deserialization coverage.
- **BS-2 (Systems):** FP profile of shape classifiers outside sampled bundles not quantified.
- **BS-3 (Skeptic):** implementation complexity of language qualifier not examined; confidence intervals on 67% modal rate not calculated (at n=9 overrides, 95% CI is ~35-90%).

These are not votes — they're context for R3 deliberation if R2 doesn't converge.

---

## 5. Cross-cutting tension — Skeptic's "principled vs one-off" framing

Skeptic (DeepSeek) explicitly framed the Priority 1/1b/1c work as "textbook overfitting" — three patches each solving one observed override. Pragmatist and Systems implicitly accept this for Priority 1 (C5) by requiring language-qualifier pairing (C2), but extend it to Priority 1b/1c via DEFER.

**R2 question to all 3 agents:** does the C5 (land Priority 1 with language qualifier) + C6/C7 (defer Priority 1b/1c) + C14 (Skeptic I-2 "principled expansion") package constitute an acceptable middle path? Or does Skeptic maintain that Priority 1 itself is overfitting and should defer?

If R2 produces Skeptic BLOCK on C5, the review continues to R3 deliberation on C5 specifically.

---

## 6. Voting instructions

**For each C-item in §4 (C1 through C20):**

- **AGREE:** accept proposed classification as-is. One-sentence confirmation.
- **DISAGREE:** reject proposed classification. One-paragraph rationale. Alternative classification required.
- **MODIFY:** accept direction, refine details. State the specific modification + rationale.

**Silent drops are not allowed per SOP §4 Pre-Archive Gate.** If you intentionally decline to vote on an item, state "EXPLICIT-SKIP: <reason>."

---

## 7. Required output format

Write to `.board-review-temp/v13-3-comparator-calibration/{pragmatist|codex|deepseek}-r2.md`. Structure:

```
# V13-3 R2 — [agent name]

## Per-C-item votes

### C1 — [title]
**Vote:** AGREE / DISAGREE / MODIFY
**Rationale:** [1-3 sentences]
[If MODIFY: alternative]

### C2 — [title]
...

[continue through C20]

## Meta-positions
- Did R1 change your mind on anything after reading the other two agents' rationales inlined below? [yes/no + explanation]
- Does the C5 + C6/C7 + C14 package resolve the "principled vs one-off" tension? [yes/no + explanation]

## New items raised at R2 (if any)
- [N1]: [item + severity]

## Explicit non-escalations (if any)
- [list items from R1 you are intentionally not pressing further, with one-line rationale]

## Blind spots (updated if anything changed)
[Brief honest disclosure]
```

**Word cap: 2000.** Be specific. R2 is narrower than R1 — convergence on well-framed items is the goal.

---

## 8. Files to READ (absolute paths)

**Required — re-read:**

- `/root/tinkering/stop-git-std/.board-review-temp/v13-3-comparator-calibration/r1-brief.md` — full R1 brief (366 lines; contains all background context + the 8 vote options + files-to-read list).
- `/root/tinkering/stop-git-std/docs/v12-wild-scan-telemetry.md` — primary 11-scan dataset.
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` — V13-3 entry at §8 line 397; V13-1 owner-directive precedent at §8.1; §8.2 historical-bundle rule.
- `/root/tinkering/stop-git-std/docs/v13-1-override-telemetry-analysis.md` — template for the V13-3 analysis deliverable (C1).
- `/root/tinkering/stop-git-std/docs/compute.py` — compute layer; SIGNAL_IDS frozenset (25 entries); `derive_*` helpers as precedent for C18.

**Reference (sample as needed):**

- `/root/tinkering/stop-git-std/docs/scan-schema.json` — override_reason_enum values.
- `/root/tinkering/stop-git-std/docs/scanner-catalog.md` rows 16-26 — 11 V1.2 wild scans.
- `/root/tinkering/stop-git-std/docs/board-review-data/scan-bundles/Baileys-8e5093c.json` — latest Q4 override example.
- `/root/tinkering/stop-git-std/docs/board-review-data/scan-bundles/WLED-01328a6.json` — prior Q4 override example.
- `/root/tinkering/stop-git-std/docs/phase_1_harness.py` — STEP_A_PATTERNS (deserialization regex for V12x-9 language-qualifier work).

---

## 9. R1 responses — VERBATIM

Per SOP §4: stateless agents can't vote on what they can't see. All three R1 responses are inlined below in full. Re-read them — including your own if you were one of the R1 agents.

### 9.1 Pragmatist R1 (verbatim)

```markdown
# V13-3 R1 — Pragmatist

## Votes

- V3Q1 (scope): **A3** — Confirm D-6 closes the narrow pipeline-comparator reading; the broad cross-scan calibration is the real deliverable V13-3 owes.
- V3Q2 (Priority 1 deserialization): **B1** — Additive signal, CONSOLIDATION Board Item F permits it; language-qualifier prerequisite (V12x-9) must land first in the same commit.
- V3Q3 (Priority 1b firmware CORS): **C2** — New shape-classification input required; that's bigger than additive signal work; defer to V1.3 where shape taxonomy is owned.
- V3Q4 (Priority 1c reverse-eng shape): **D2** — FP risk on authorized third-party clients is real and unquantifiable from 1 observation; need ≥3 confirmed fires before codifying.
- V3Q5 (Q3 rubric): **E2** — Don't change the rubric; add `community_norms_differ` as a V1.3 candidate (DeepSeek's preserved dissent now has telemetric backing at 11/11); rubric change is a bigger cross-scan comparability event than it looks.
- V3Q6 (V1.3 enum pruning): **F2** — Prune only `missing_qualitative_context` (superseded by V13-1 split); keep the other 3 as headroom; 11 scans isn't a balanced sample (Lua/PHP/Swift absent).
- V3Q7 (V13-3 follow-up cadence): **G3** — Condition-triggered is smarter than count-triggered; `signal_vocabulary_gap` at >80%, OR ≥2 new enum values fire in one scan, OR a case fits none are the right tripwires.
- H (process): **H2** — Owner directive after this R1; the scope is multi-axis but the directional answers are clear enough; R2/R3 only if dissent from Systems Thinker or Skeptic is substantive.

---

## Rationale

**On V3Q1 (scope):** The narrow reading (D-6 covers pipeline-level parity, V13-3 closes with a confirmation note) is correct but insufficient. D-6 already passes on all 3 Step G pairs — that question is closed. The interesting V13-3 work is the broad reading: the 11-scan cross-analysis has never been formally written up as a frozen document. The `docs/v12-wild-scan-telemetry.md` is a living doc, not a decision artifact. V13-3's mandate is to produce a citable analysis document (`docs/v13-3-analysis.md`) that closes the deferred-ledger item with evidence rather than just a note.

**On V3Q2 (deserialization Priority 1):** This is the right call, but the sequencing constraint is hard. V12x-9 (language qualifier on the deserialization regex) is a prerequisite — without it, the Priority 1 compute derivation fires on WLED's 19 ArduinoJson FP hits and produces a Critical finding on what is safe JSON parsing. The two must ship atomically: V12x-9 narrows the regex, then Priority 1 auto-fires from the narrowed output. The brief treats V12x-9 as "promoted from Low to Medium" — the operator needs to treat it as mandatory blocker for Priority 1, not just a parallel work item.

**On V3Q3 (firmware CORS, Priority 1b):** This is not an additive signal — it requires a new shape-classification input (firmware vs non-firmware). The shape taxonomy doesn't exist in compute.py today; building it requires a new harness layer reading README keywords + install-path signals. That's not V1.2.x additive; it's infrastructure. Defer to V1.3 where shape-aware compute can be designed cleanly.

**On V3Q4 (reverse-eng shape, Priority 1c):** 1 observation (Baileys). The FP scenario (authorized third-party clients) is real; libraries like the official Discord SDK, Matrix clients, or vendor-blessed bots would match the disclaimer regex. The cost of a false Critical on a legitimate library is high — it destroys trust in the scanner. Defer to V1.3 and collect ≥3 confirmed fires (whatsmeow, discord.py-self, instagrapi are all live candidates) before codifying.

**On V3Q5 (Q3 rubric):** The brief frames this as E1 (escalate to red on documented failure) vs E3 (keep as-is). E1 is the wrong move for comparability reasons: 9 of 11 prior V1.2 scans would remain amber under Q3 while 2 become red — this creates a retroactive comparability break. The 11/11 silent-fix pattern is strong enough that it argues for naming the community norm explicitly in the rubric language, not for moving the threshold. E2 is the right frame: preserve the amber reading as accurate for the current rubric's purpose ("do they have the infrastructure"), and advance `community_norms_differ` as the V1.3 enum value that lets Phase 4 call out the WLED/Baileys pattern without changing the rubric color decision. DeepSeek's R3 Item C dissent (CONSOLIDATION §5 Item C) explicitly preserved this trigger — the data at n=11 makes it fire.

**On V3Q6 (enum pruning):** 11 scans is enough to drop `missing_qualitative_context` (the V13-1 split was designed to absorb it; it hasn't fired since), but not enough to prune `threshold_too_lenient`, `rubric_literal_vs_intent`, or `other`. The sample is heavily skewed: Zig, Rust, C#, Java, Python ML are all represented, but Lua/PHP/Ruby/Swift/Kotlin aren't. A PHP WordPress plugin or a Ruby-on-Rails server gem might produce `rubric_literal_vs_intent` overrides on Q2 or Q3 where "4 security items open" doesn't actually mean "slow fixes." Hold F3-equivalent headroom for those shapes.

**On V3Q7 (follow-up cadence):** Count-based triggers (G2 at 20 or 25) are dumb timers. The right trigger is: something surprising happens in the data. G3's three conditions are precise enough to fire when the taxonomy is strained without firing every 10 scans on routine operation.

**On H (process):** H2. This review covers 7 connected questions. R1 gives the board a round of input; if the three agents converge on the same key votes (particularly B1/B2 on deserialization, C2/C3 on firmware, E2/E3 on Q3 rubric), the owner has enough to act without a full R2/R3 cycle. Full three-round review adds 30-45 minutes of orchestration overhead for decisions that the data makes clear. Escalate only if the Systems Thinker or Skeptic surfaces something this brief missed.

---

## FIX NOW items

- **FN-1:** V12x-9 (language-qualifier regex on deserialization family) MUST be treated as a hard prerequisite for V3Q2/Priority 1 auto-fire — not as a parallel-and-maybe item. The brief lists it as "promoted from Low to Medium"; it should be elevated to blocker. If Priority 1 ships without V12x-9, the WLED ArduinoJson FPs will trigger spurious Critical findings.

---

## DEFER items

- **V3Q3 (C2):** Priority 1b firmware compound signal — defer to V1.3 pending shape-classification infrastructure.
- **V3Q4 (D2):** Priority 1c reverse-engineered-API shape signal — defer to V1.3 pending ≥3 confirmed fire observations.
- **V3Q6-remainder:** `threshold_too_lenient`, `rubric_literal_vs_intent`, `other` — hold at V1.3 pending balanced shape-sample (Lua/PHP/Swift/Kotlin shapes uncovered).

---

## INFO items

- **INF-1:** The 82% scan-level override rate (9 of 11 scans have ≥1 override) is higher than the brief frames it. The 33% cell-level override rate from V13-1 was alarming enough to drive enum expansion. At scan level 82% suggests the harness+compute advisory layer is rarely producing Phase 4-concordant results across an entire scan — worth naming explicitly in the V13-3 analysis document.
- **INF-2:** §8.3's question about V2.4-era back-labeling: recommend V1.2-only scope for V13-3. Back-labeling V2.4 prose to machine-readable override categories is manual and error-prone. The V13-3 analysis document should note this as an explicit scope exclusion, not leave it ambiguous.
- **INF-3:** The `docs/v13-3-analysis.md` document format should mirror `docs/v13-1-override-telemetry-analysis.md` structurally — that's the established template for this class of analysis and it worked well.

---

## Open questions the brief missed

- **OQ-1:** V12x-6 (multi-ecosystem manifest parsing) is Priority 2 in the backlog but isn't a V3Qx vote option — it affects 7 of 11 scans and produces `runtime_count=0 / osv_total_vulns=0` for Maven/Gradle/Cargo/Gomod/Bundler/.NET. Is this on or off the V13-3 scope? The brief treats it as a backlog item without a landing-window decision. V1.2.x or V1.3?
- **OQ-2:** If V3Q2 B1 lands (deserialization auto-fire), entries 17 (Kronos) and 24 (freerouting) would no longer have Q4 overrides if re-processed. But CONSOLIDATION §9 says "existing override records preserved as historical." Does the V13-3 document explicitly codify this non-retroactivity rule, or does it leave it implicit?

---

## Blind spots

My perspective is weakest on the compute.py derivation specifics for Priority 1 — I've read the logic but haven't traced the signal chain from `dangerous_primitives.deserialization.hit_count` through to `q4_has_critical_on_default_path` to verify the threshold mechanics are as described. The "≥3 hits plus README keyword match" threshold N is asserted but not tested. I'm also weakest on whether V12x-9's language-qualifier regex change is truly low-risk or whether suppressing `\bdeserialize\b` in C/C++/Rust creates a coverage blind spot on genuine unsafe deserialization in those languages.
```

### 9.2 Systems Thinker (Codex) R1 (verbatim)

```markdown
# V13-3 R1 — Codex

## Votes
- V3Q1 (scope): A3 — Reading A is already functionally answered by D-6, but V13-3 should explicitly close that loop and then do the broader calibration work because the telemetry is now the larger operational signal.
- V3Q2 (Priority 1 deserialization): B1
- V3Q3 (Priority 1b firmware CORS): C2
- V3Q4 (Priority 1c reverse-eng shape): D2
- V3Q5 (Q3 rubric): E3
- V3Q6 (V1.3 enum pruning): F2
- V3Q7 (V13-3 follow-up cadence): G4-prose — close this pass only after publishing a frozen V13-3 analysis, then re-trigger on whichever comes first: 25 V1.2 wild scans total or any enum-escape / multi-label ambiguity event.
- H (process): H1

## Rationale (prose)
V13-3 is both readings, but asymmetrically. Reading A is not where the risk is anymore. D-6 already covers finding-level parity for the three pinned Step G pairs, and the validator plus seven-gate process contain future drift there. The only useful systems move is to make that closure explicit in the V13-3 artifact so operators stop treating "comparator" as an unresolved pipeline-parity question. The real open loop is Reading B: the live contract between `phase_1_harness.py`, `compute.py`, Phase 4 overrides, validator gate 6.3, and the frozen V1.2 historical bundles.

The key pattern is not merely "Q4 overrides are common." It is that Q4 overrides are common for three different integration reasons. Freerouting is a roll-up failure from harness facts to compute signal. WLED is a compound-signal failure that needs shape context. Baileys is a metadata / README classification problem with obvious false-positive risk. Those are three different blast radii. Treating them as one "Priority 1" family would couple compute changes, README parsing, and shape inference into the same V1.2.x patch stream and make regression attribution harder. That is why B1 is right, but C1 and D1 are premature.

Deserialization auto-fire is the only candidate that is both high-yield and structurally disciplined. It uses existing data paths, aligns with the V13-1 precedent that additive signals are valid V1.2.x work, and directly collapses two known overrides. The main risk is false positives from the widened deserialization family, but the telemetry already surfaced the mitigation: language qualification. That is a bounded harness-plus-compute adjustment with a clean validator story and limited renderer impact because scorecard authority already lives in Phase 4, not Phase 3.

By contrast, firmware default-no-auth plus CORS and reverse-engineered API shape classification both inject new upstream semantics into Phase 1 or compute. They rely on shape classification, README interpretation, or platform-name heuristics that are less stable than primitive-family signals. Landing those in V1.2.x would create silent coupling with scan drivers, fixture expectations, and future operator heuristics, while preserving the same validator surface. That is exactly the kind of change that looks additive in schema terms but is not additive in behavior terms. Defer both to V1.3 or at least to a later V12x patch after explicit dry-run evidence.

I do not support a Q3 rubric change now. The telemetry shows a stable amber outcome with zero overrides, which means the system is internally consistent. WLED and Baileys are not evidence that compute is missing the problem; they are evidence that the current rubric intentionally distinguishes "poor disclosure posture" from "actively hides." If you flip those historical cases to red, you break comparability across the 11-scan bundle set and blur the line between absence of process and adversarial concealment. That is a rubric philosophy change, not calibration.

Enum pruning should also be conservative. `missing_qualitative_context` is now clearly superseded by the V13-1 split, so pruning it in V1.3 improves audit clarity. The other three unused values should stay. Eleven scans across eleven shapes is enough to retire a replaced catchall, not enough to declare future threshold or rubric exceptions dead.

The historical-bundle rule matters: preserve entries 16–26 as historical artifacts. Do not re-render them if signals change. V13-3 should be a frozen document that cites those bundles, not a living section that mutates with later V12x patches. Otherwise the board loses the ability to reason about why overrides existed at the time they were authored.

## FIX NOW items (if any)
- C-1: Define V13-3 as A3 in the written analysis and explicitly state that Reading A is closed by D-6 while Reading B remains the actionable calibration surface.
- C-2: Land Priority 1 only as a paired change: deserialization auto-fire must ship with language-qualified matching, or it will contaminate Q4 advisory hints on non-deserialization code paths.
- C-3: Freeze entries 16–26 as historical bundles; V13-3 analysis may model override collapse counterfactually, but must not re-render prior artifacts.

## DEFER items (if any)
- D-1: Priority 1b firmware default-no-auth + CORS compound signal — defer until a dry-run on the 11 bundles proves shape classification and auth-absence heuristics are not overfitting WLED.
- D-2: Priority 1c reverse-engineered-platform-API signal — defer until a wider comparator set exists; trigger lift when at least 3 scans of that shape or an equivalent dry-run corpus shows acceptable FP rate.
- D-3: Q3 rubric escalation for documented disclosure failure — defer until a broader cross-scan sample shows the amber outcome is masking materially distinct operator action.

## INFO items (if any)
- I-1: The same four Q4 `computed_signal_refs` appear on freerouting, WLED, and Baileys despite three different root causes; that is a useful symptom that the scorecard-hint vocabulary is underexpressive even when the override enum is adequate.
- I-2: Reading A and Reading B should not share a maintenance home. D-6 is executable and living; V13-3 analysis should be frozen and cited.

## Open questions the brief missed
- If Priority 1 lands, where is the canonical derivation for "tool loads user files" stored so operators do not recreate that judgment ad hoc in scan drivers?
- Should the V13-3 document require an explicit "historical vs counterfactual" section so later readers do not confuse simulated override collapse with actual bundle contents?

## Blind spots
My weakest area here is the false-positive profile of the proposed shape classifiers outside the sampled bundles. I can see the coupling risk clearly, but I have not run the broad README/topic dry-runs that would quantify it.
```

### 9.3 Skeptic (DeepSeek) R1 (verbatim)

```markdown
# V13-3 R1 — Skeptic

## Votes
- V3Q1 (scope): **A2** — Broad cross-scan pattern calibration. The narrow comparator is already covered by D-6; the real value is in the 11-scan pattern analysis.
- V3Q2 (Priority 1 deserialization): **B2** — Defer to V1.3. Language qualifier is a bigger change than "additive signal"; it's a semantic rewrite of the deserialization family.
- V3Q3 (Priority 1b firmware CORS): **C2** — Defer to V1.3. Requires shape classification input — a new schema field, not just signal addition.
- V3Q4 (Priority 1c reverse-eng shape): **D3** — Reject. ToS-violation categories are librarian judgment, not automatable. The false-positive risk on vendor-authorized clients is unacceptably high.
- V3Q5 (Q3 rubric adjustment): **E3** — Keep Q3 rubric as-is. Amber correctly captures "partly" across all 11 scans; documented failures are already captured.
- V3Q6 (V1.3 enum pruning): **F3** — Prune none. 11 scans is insufficient evidence; 4 unused values are sleeping, not dead.
- V3Q7 (V13-3 follow-up cadence): **G2** — Trigger at 25 V1.2 wild scans. 11 is too small for stable patterns.
- H (process): **H1** — Full board. Multi-axis scope with schema implications warrants board review.

## Rationale (prose)

The fundamental assumption wrong in this brief is that 11 scans constitute a statistically meaningful sample for calibration decisions. They don't. The 11-scan roster shows heavy bias: Python/Rust over-represented (3 each), while entire ecosystems (PHP, Swift, Kotlin, Lua) are absent. The "4 unused enum values are dead" conclusion is premature — we haven't seen the shapes that would trigger them.

What breaks under adversarial reading? The "Q4 is the override hotspot" pattern (6 of 9 overrides). This isn't a structural flaw — it's sample bias. Q4's `q4_has_critical_on_default_path` is a Phase-4-authored boolean by design. The brief treats this as a problem to fix with harness patches, but that misunderstands the contract: Phase 4 is the judgment layer. Automating Q4 judgments via regex risks false positives that Phase 4 would override anyway, creating circular logic.

The Priority 1-3 harness patches are textbook overfitting. Each patch solves exactly one observed override:
- Priority 1 solves freerouting's Java deserialization (but creates false positives on safe JSON parsing)
- Priority 1b solves WLED's firmware CORS (but requires new shape classification input)
- Priority 1c solves Baileys' ToS-violation (but fails on vendor-authorized clients)

This is the "last bug" fallacy — fixing what we just saw, not building robust signals. The language-qualifier requirement for deserialization (Priority 1) reveals the deeper problem: the deserialization primitive family is conceptually broken. It conflates safe JSON parsing with unsafe pickle/ObjectInputStream. Fixing this requires rethinking the primitive taxonomy, not adding language qualifiers.

The silent-fix pattern (11/11 scans with 0 GHSA advisories) is being misinterpreted. The brief suggests Q3 rubric adjustment, but the data shows Phase 4 correctly renders amber for all 11 scans, including WLED and Baileys with documented disclosure failures. The rubric already works — amber means "partly tells you about problems." The two documented failures don't change the community norm; they confirm it. Changing the rubric to red for documented failures would create inconsistency: why red for WLED/Baileys but amber for the other 9 with identical 0-advisory patterns?

The comparator calibration's original purpose — detecting semantic drift between V2.4 and V2.5-preview — is already satisfied by D-6. The expanded "pattern calibration" scope risks mission creep: we're now debating schema changes (shape classification), primitive family redesigns, and rubric adjustments based on 11 biased samples.

My prior R1 framing about `override_category` for semantic drift detection remains unaddressed. The current 7-value enum doesn't distinguish between "threshold calibration" (fixable via signal tuning) and "judgment call" (inherent to Phase 4's role). Without this distinction, the 11-scan analysis conflates fixable gaps with irreducible judgment.

## FIX NOW items (if any)
- **C-1:** Document the sample bias explicitly in the V13-3 analysis. State clearly: "11 scans, Python/Rust heavy, missing major ecosystems."
- **C-2:** Reject the "dead enum" narrative. Keep all 7 values through V1.3; revisit at 25+ scans.

## DEFER items (if any)
- **D-1:** All Priority 1-3 harness patches → V1.3. They require schema changes (shape classification) or primitive family redesigns.
- **D-2:** Q3 rubric adjustment → Never. The rubric correctly captures the community norm.

## INFO items (if any)
- **I-1:** The zero-override streak (wezterm→QuickLook→kanata) shows the signal vocabulary works for some shapes. This is positive calibration data.
- **I-2:** `signal_vocabulary_gap` at 67% modal suggests compute.py needs expansion, but the expansion should be principled (new signal families), not one-off patches.

## Open questions the brief missed
- What's the **false-positive rate** of the proposed harness patches? Test them against the 11 existing scans.
- How does **Phase 4 judgment change** if we auto-fire Q4 from deserialization hits? Would Phase 4 override the auto-fire?
- What **new shapes** would trigger the 4 unused enum values? Design hypothetical test cases.

## Blind spots
My perspective is weakest on the **implementation complexity** of the language qualifier for deserialization. I'm advocating deferral but haven't examined the regex code to see if language detection is feasible within the current harness architecture.

Also, I'm skeptical of sample size but haven't calculated **confidence intervals** for the 67% `signal_vocabulary_gap` modal rate. At n=9 overrides, the 95% CI is wide (~35-90%). The "strongly modal" claim is statistically weak.
```

---

## 10. Meta-context (non-voting)

- V13-3 R1 launched 2026-04-20; all three R1 reports collected cleanly.
- HEAD at R2 authoring: `c558b9f` on origin/main.
- 385/385 tests passing.
- Operator's directional read after R1: C5 (Priority 1) is the only concrete V1.2.x landing; C6/C7 defer cleanly; C8 keeps Q3 rubric; C9 prunes the V13-1-superseded catchall; C10 is the contested item (V13-3 follow-up cadence).
- If R2 converges, R3 is skipped per SOP §4 Expedited path and R4 Confirmation follows directly. If R2 shows substantive new dissent (e.g., Skeptic BLOCK on C5 with new rationale), R3 Deliberation fires on the contested items only.
- Board composition: Pragmatist (Claude Sonnet 4.6), Systems Thinker (Codex GPT-5.2), Skeptic (DeepSeek V4.0 via Qwen CLI). Each reads this brief cold.
