# V13-3 Board Review — R1 Brief (Stateless)

**Review topic:** V13-3 — 11-scan comparator calibration analysis. Trigger fired 2026-04-20 with catalog entry 26 (WhiskeySockets/Baileys) — the 11th V1.2-schema wild scan.

**Round:** R1 Blind. Open scoping — all options on the table.

**Agent instruction:** You are one of three agents (Pragmatist / Systems Thinker / Skeptic). You are STATELESS — read this brief as if you've never seen this project. Inline context is sufficient; do not assume prior conversation. Read every file listed in §12 before voting.

---

## 1. What this project is

`stop-git-std` is an LLM-driven GitHub repository security scanner. Operator provides `owner/repo`; a harness (`docs/phase_1_harness.py`) runs an automated investigation against `gh api` + OSSF Scorecard + osv.dev + package registries + gitleaks + tarball extraction + local grep; a compute layer (`docs/compute.py`) derives deterministic signals into Phase 3 advisory scorecard cells; an LLM authors Phase 4 structured findings + Phase 5 prose into a `form.json`; renderers produce MD + HTML. Schema V1.2 is live.

**As of this review: 26 catalog entries** (11 V2.4 LLM-authored + 15 V2.5-preview JSON-first). 11 of those are V1.2-schema wild scans (entries 16–26), covering an increasingly diverse shape space: Zig terminal emulator, Python ML model, Python monorepo, Ruby deploy orchestrator, Go network proxy, browser extension + Go native host, Rust terminal, Rust keyboard daemon, C# Windows shell extender, Java EDA tool, C++ IoT firmware, TypeScript reverse-engineered API library.

**385/385 tests passing. HEAD c558b9f on origin/main.**

---

## 2. Why this review is happening

**CONSOLIDATION §8 V13-3 entry (line 397):**

```
| V13-3 | 11-scan comparator calibration analysis
       | V1.2 schema frozen + telemetry exists + ≥11 V1.2 scans collected
       | open (3/11) |
```

**Origin (§7 row 14):** Codex C-6 from the Schema V1.2 board (042026-schema-v12). Deferred with trigger "V1.2 schema frozen + override telemetry exists" because analyzing before V1.2 landed would be "analysis on the wrong contract."

**Codex R1 framing (codex-r1.md:33):**

> "C-6: 11-scan comparator calibration analysis — defer until V1.2 schema is frozen and override telemetry exists, or the analysis will be on the wrong contract."

**DeepSeek R1 framing (deepseek-r1.md:16):**

> "The 11-scan comparator analysis needs something V1.2 as designed cannot extract: **semantic drift detection**. V1.2 focuses on threshold calibration (formal<10% → red) but misses when LLM overrides for qualitative reasons outside the rubric (e.g., 'this repo has a vibrant community despite low formal review'). The comparator needs a field like `override_category: threshold | qualitative_context | rubric_interpretation` to distinguish calibration fixes from judgment calls."

V13-1 owner-directive work partially resolved DeepSeek's concern by splitting the enum 5→7 with `signal_vocabulary_gap` + `harness_coverage_gap` — but the 11-scan cross-analysis has not run.

The trigger has now fired. **Scope, process, and decision options are this review's job.**

---

## 3. What V13-3 means (as surfaced during the V13-1 work + telemetry accumulation)

The name "comparator calibration analysis" originally referenced **V2.4-vs-V2.5-preview pipeline comparison** on pinned SHAs. Three Step G validation pairs exist:

- `zustand-v3` entry 10 (V2.4) ↔ entry 12 (V2.5-preview) — both at SHA `3201328`
- `caveman` entry 1 (V2.4) ↔ entry 13 (V2.5-preview) — both at SHA `c2ed24b`
- `Archon` entry 2 (V2.4) ↔ entry 14 (V2.5-preview) — both at SHA `3dedc22`

D-6 severity-distribution comparator (`docs/compare-severity-distribution.py`, 23 tests, shipped 2026-04-20) validates finding-level parity across those 3 pairs. All 3 currently PASS.

**But the V13-1 work expanded the scope**. Override telemetry across 11 wild scans now provides a larger signal than the 3 fixed-SHA pairs. The `docs/v12-wild-scan-telemetry.md` document persists the cross-scan analysis — 9 overrides across 11 scans, distribution heavily skewed toward `signal_vocabulary_gap` (67% modal).

So "comparator calibration analysis" now has TWO legitimate readings:

- **Reading A (narrow, original):** Pipeline-level comparator — does V2.5-preview produce output comparable to V2.4 on pinned SHAs? Answer: yes, D-6 validates this for finding-level severity distribution. Any further drift is caught by the existing 7-gate Step G acceptance and the `--parity` validator.
- **Reading B (broad, post-V13-1):** Cross-scan pattern calibration — across 11 shape-diverse V1.2 scans, are compute signals adequate, is the override enum stable, is the Q3 rubric calibrated correctly, are the 4 unexercised enum values real headroom or dead weight, and what harness-patch candidates should V1.2.x ratify?

**First R1 question for the board: which reading is V13-3?** Or both? Or something else?

---

## 4. The 11-scan data (facts)

### 4.1 Roster

| # | Repo | Shape | Verdict | Overrides | Override detail |
|---|---|---|---|---|---|
| 16 | ghostty-org/ghostty | Zig terminal emulator | Caution | 1 | Q1 signal_vocabulary_gap (ruleset invisible) |
| 17 | shiyu-coder/Kronos | Python ML foundation model | Critical (split) | 2 | Q2 signal_vocabulary_gap + Q4 harness_coverage_gap |
| 18 | basecamp/kamal | Ruby deploy orchestrator | Caution | 1 | Q1 signal_vocabulary_gap |
| 19 | XTLS/Xray-core | Go network proxy | Critical | 1 | Q2 threshold_too_strict |
| 20 | BatteredBunny/browser_terminal | Browser ext + Go host | Critical (split) | 1 | Q4 harness_coverage_gap (typosquat URL) |
| 21 | wezterm/wezterm | Rust terminal emulator | Caution | **0** | — |
| 22 | QL-Win/QuickLook | C# Windows shell extender | Caution | **0** | — |
| 23 | jtroo/kanata | Rust keyboard daemon | Critical | **0** | — |
| 24 | freerouting/freerouting | Java PCB auto-router | Critical | 1 | Q4 signal_vocabulary_gap (Java deserialization) |
| 25 | wled/WLED | ESP32 IoT firmware | Critical | 1 | Q4 signal_vocabulary_gap (firmware default-no-auth + CORS) |
| 26 | WhiskeySockets/Baileys | Reverse-engineered WhatsApp Web lib | Critical | 1 | Q4 signal_vocabulary_gap (ToS-violation category) |

**Totals:** 11 scans, 9 overrides, 3 zero-override.

### 4.2 Override-enum distribution (n=9)

| `override_reason` | Count | % | Fires on |
|---|---|---|---|
| `signal_vocabulary_gap` | **6** | **67%** | ghostty Q1, kamal Q1, Kronos Q2, freerouting Q4, WLED Q4, Baileys Q4 |
| `harness_coverage_gap` | 2 | 22% | Kronos Q4, browser_terminal Q4 |
| `threshold_too_strict` | 1 | 11% | Xray-core Q2 |
| `missing_qualitative_context` | 0 | 0% | — |
| `threshold_too_lenient` | 0 | 0% | — |
| `rubric_literal_vs_intent` | 0 | 0% | — |
| `other` | 0 | 0% | — |

**Four of seven enum values unexercised.** `missing_qualitative_context` was the pre-V13-1 catchall; the V13-1 split routed prior uses to `signal_vocabulary_gap` + `harness_coverage_gap` and it hasn't fired since.

### 4.3 Question-level distribution

| Question | Overrides | % of all overrides |
|---|---|---|
| Q1 (does anyone check code) | 2 | 22% |
| Q2 (do they fix problems quickly) | 2 | 22% |
| Q3 (do they tell you about problems) | **0** | **0%** |
| Q4 (is it safe out of the box) | **5** | **56%** |

**Q4 is the override hotspot.** 5 of 9 overrides. Q3 never overrides — compute produces colors Phase 4 agrees with, including in cases with concretely-documented disclosure-handling failures (WLED #5340 + Baileys PR #1996).

### 4.4 Silent-fix consistency: 11/11

All 11 V1.2 wild scans have 0 published GHSA advisories across histories ranging from 10 months (Kronos) to 12 years (freerouting). Two of those 11 have **publicly-documented disclosure-handling failures** at concrete PR/issue level:

- **WLED #5340** (2026-02-02, 74 days silent at scan): researcher `breakingsystems` filed private GHSA-2xwq-cxqw-wfv8; 10+ day maintainer silence prompted public complaint; maintainer permissions misconfigured on advisory UI; last maintainer comment 2026-02-06 said 'critical was fixed before; verifying 0.15.x backport' — backport status still unconfirmed publicly.
- **Baileys PR #1996** (2025-10-30 → 2026-03-26, 148 days stale-closed): researcher KaivalyaGauns filed vulnerability-fix PR replacing deprecated `request`/`request-promise-*` (2 CVEs); maintainer purpshell commented 2026-01-08 'we should make our own version of this PR' — 'own version' never materialized; master still ships `request`.

### 4.5 Zero-override streak context

3 consecutive zero-override scans: wezterm (21) → QuickLook (22) → kanata (23). Streak broken at freerouting (24). Since then, 3 consecutive Q4 `signal_vocabulary_gap` overrides (24 + 25 + 26). Pattern: zero-override is possible when compute-signal judgment aligns with Phase 4 judgment; breaks on specific default-path-critical conditions that harness/compute doesn't surface.

---

## 5. V1.2.x harness-patch candidates (telemetry §4)

Three Priority-1-tier candidates surfaced from telemetry. Each would collapse specific overrides and each lives in a different harness layer.

### 5.1 Priority 1: Deserialization auto-fire for Q4 (with language qualifier)

**Compute derivation:** `q4_has_critical_on_default_path = True` when `dangerous_primitives.deserialization.hit_count ≥ N` AND the tool is documented as loading user files.

**Would auto-resolve:** Kronos Q4 (pickle.load in finetune/dataset.py), freerouting Q4 (Java ObjectInputStream, 35 imports). Kronos's V1.2.x pickle-regex extension already landed — freerouting has 35 hits via the widened regex.

**Subtlety surfaced by WLED (25):** the V1.2.x widened deserialization regex matched 19 ArduinoJson `deserializeJson` calls — SAFE JSON parsing, FP. A language qualifier is needed (pickle→Python, ObjectInputStream→Java, Marshal.load→Ruby, `\bdeserialize\b` → skip in C/C++/Rust with JSON-library paths).

### 5.2 Priority 1b: Firmware default-no-auth + CORS-wildcard compound Q4 signal

**Compute derivation:** `q4_has_critical_on_default_path = True` when `tls_cors.hit_count ≥ 1` (wildcard `*`) AND `auth_bypass.hit_count == 0` AND shape is `firmware | iot | on-device-webserver`.

**Would auto-resolve:** WLED Q4.

**New input required:** shape classification from README keywords (ESP32, ESP8266, firmware, on-device, LAN webserver) + install-path signals (.bin releases, WebSerial flasher).

### 5.3 Priority 1c: Reverse-engineered-platform-API shape signal for Q4

**Compute derivation:** `q4_has_critical_on_default_path = True` when README (Step 7.5) contains disclaimer phrases matching `(not affiliated|not endorsed|not authorized|reverse.?engineered|unofficial.*client)` AND topic list contains `reverse-engineering` OR library name references a platform (whatsapp, discord, instagram, telegram-client).

**Would auto-resolve:** Baileys Q4. Other reverse-engineered-API libraries (whatsmeow in Go, discord.py-self, instagrapi) would also match.

**Open: false-positive risk.** Libraries with vendor partnerships (officially-authorized third-party clients) might trigger. Safeguard: require disclaimer AND absence of `authorized_by` metadata — likely out-of-scope for regex/compute. V1.3 candidate if FP rate high; V1.2.x candidate if the shape is rare enough.

### 5.4 Lower-priority V12x backlog items

From telemetry §8:

- V12x-9 deserialization regex language qualifier (Low → Medium, promoted because 4 FP cases + Priority 1 depends on it)
- V12x-10 silent-fix pattern telemetry (escalated to V1.3 candidate at 11/11)
- V12x-11 firmware-no-auth+CORS compound (Medium)
- V12x-12 reverse-engineered-API shape signal (Medium)
- V12x-13 vendor_keys proximity context (Low — Baileys `AIza...` FP in WhatsApp protocol dictionary)
- V12x-14 PR sampler robustness when closed-without-merge dominates (Low — Baileys 0 sample despite 352 merges)

---

## 6. Canonical options the board must vote on

### V3Q1: V13-3 scope

- **A1:** Narrow — pipeline-comparator analysis only. V2.4-vs-V2.5-preview on 3 Step G pairs is already covered by D-6; V13-3 closes with a CONFIRM-D-6-covers-it note. No additional deliverable.
- **A2:** Broad — cross-scan pattern calibration. 11-scan override distribution, Q3 rubric adjustment, V1.2.x harness-patch ratification, V1.3 enum pruning. Produces a V13-3 analysis document at `docs/v13-3-analysis.md` with decisions ratified.
- **A3:** Both — narrow + broad. Confirm D-6 covers Reading A; author Reading B analysis as V13-3-output.
- **A4 (propose):** Something else.

### V3Q2: V1.2.x harness-patch Priority 1 (deserialization language-qualifier + auto-fire)

- **B1:** Land in V1.2.x. Additive compute signal + regex calibration. Collapses Kronos Q4 + freerouting Q4 overrides. Board Item F permits signal additions as V1.2.x.
- **B2:** Defer to V1.3. Scope is big enough it should sit with other signal-calibration work.
- **B3:** Reject. Don't auto-fire Q4 from primitive counts — Phase 4 authoring is the right layer.

### V3Q3: V1.2.x harness-patch Priority 1b (firmware default-no-auth + CORS compound)

- **C1:** Land in V1.2.x.
- **C2:** Defer to V1.3. Requires new shape-classification input; bigger-than-additive change.
- **C3:** Reject. Firmware-default-no-auth is rare enough that Phase 4 override is the right handling.

### V3Q4: V1.2.x harness-patch Priority 1c (reverse-engineered-API shape signal)

- **D1:** Land in V1.2.x.
- **D2:** Defer to V1.3. FP risk on vendor-authorized third-party clients; needs wider calibration data.
- **D3:** Reject. ToS-violation categories are rare and librarian-judgment is sharper than any regex combination.

### V3Q5: Q3 rubric adjustment (silent-fix pattern 11/11 + 2 documented failures)

Current Q3 rubric (from `docs/repo-deep-dive-prompt.md` lines 740–762): amber when SECURITY.md absent + advisories count low; red when actively hides. At 11/11 scans, "amber/partly" has been the uniform Phase 4 decision including for WLED and Baileys where disclosure failure was documented.

- **E1:** Change Q3 rubric language — escalate from amber to red when researcher publicly documents disclosure-handling failure (Baileys PR #1996 + WLED #5340 pattern).
- **E2:** Keep Q3 rubric; add a V1.3 `community_norms_differ` enum value for the silent-fix pattern (DeepSeek's original R3 dissent on V13-4).
- **E3:** Keep Q3 rubric as-is. Amber correctly captures "partly" across all 11 scans; V13-1 enum split absorbed the relevant edge cases; no change needed.
- **E4 (propose):** Something else.

### V3Q6: V1.3 enum pruning of 4 unused values

`missing_qualitative_context`, `threshold_too_lenient`, `rubric_literal_vs_intent`, `other` — unexercised after 11 scans.

- **F1:** Prune all 4 in V1.3. Dead weight; schema is cleaner.
- **F2:** Prune only `missing_qualitative_context` (pre-V13-1 catchall, replaced). Keep `threshold_too_lenient` + `rubric_literal_vs_intent` + `other` as headroom.
- **F3:** Prune none. Keep for future headroom. 11 scans is insufficient evidence of dead-enum status; a broader signal (e.g., 25 scans) should be the trigger.
- **F4 (propose):** Something else.

### V3Q7: V13-3 follow-up cadence

- **G1:** Close V13-3 after this review. No re-trigger scheduled.
- **G2:** V13-3-follow-up triggers at next N (propose N: 20? 25? 50?) V1.2 wild scans for the next pass of the same analysis.
- **G3:** V13-3-follow-up fires when signal_vocabulary_gap modal concentration crosses a threshold (e.g., >80%) OR when 2+ new enum values fire in a single scan OR when a scan produces an override fitting none of the 7 enum values.
- **G4 (propose):** Something else.

---

## 7. Process question — owner directive or full board?

**Facilitator's pre-brief read:** V13-3 is broader-scope than V13-1 (which was closed by owner directive on 2026-04-20 per §8.1). The V13-1 escalation-trigger language (CONSOLIDATION §8.1 last paragraph) explicitly lists "fitting multiple labels with genuine ambiguity" and "Skeptic flags inconsistency with R3 dissent on `community_norms_differ`" as board-review triggers. V13-3's Q3-rubric-adjustment question (V3Q5) intersects directly with DeepSeek's `community_norms_differ` R3 dissent. That's why this R1 is being launched rather than closed by owner directive.

**Open R1 question:** is the facilitator's escalation read correct, or should V13-3 close as owner directive after a lighter-weight consultation?

- **H1:** Full board (this review). Confirmed appropriate for the multi-axis scope (V13-1 enum-split telemetry + V1.2.x harness-patch additions + Q3 rubric + V1.3 enum pruning + V13-3 cadence).
- **H2:** Owner directive after this R1. R1 gives board 1 round of input, owner decides, skip R2/R3 unless dissent is substantive.
- **H3:** Owner-directive entirely. R1 should not have run; recommend closing V13-3 by owner directive on the telemetry data alone.

(Vote H with your preferred option, even if you voted V3Q1 narrowly.)

---

## 8. Cross-cutting questions

### 8.1 What does "comparator calibration" mean when both pipelines are rendering from the same compute.py?

V2.4 scans (catalog entries 1–11) were LLM-authored; V2.5-preview (12–26) are rendered from `form.json` populated by compute.py (deterministic signals) + LLM authoring of Phase 4 + Phase 5. On the 3 Step G pairs (zustand-v3, caveman, Archon), both pipelines wrote compute.py under their respective contracts. The V1.2 schema migration changed scorecard authority — compute is now advisory. So "comparator" may or may not be comparing like to like. Does V13-3's analysis need to account for this?

### 8.2 Sample size: are 11 scans enough to make enum-pruning decisions?

4 of 7 enum values unexercised. But 11 scans across 11 shape categories is not a balanced sample — Python/Rust are over-represented; Lua/PHP/Swift/Kotlin are absent. Is the 4-unexercised-enum-values datapoint a "these are dead" signal or a "haven't seen the shapes that use them yet" signal?

### 8.3 What about the V2.4-era overrides that aren't in the telemetry?

Catalog entries 1–15 (11 V2.4 + 4 V1.1-schema V2.5-preview) didn't record `override_reason` in machine-readable form. Any cross-pipeline drift analysis either (a) excludes them, or (b) back-labels their scorecard decisions from the V2.4 MD prose. Is the V13-3 scope V1.2-only (entries 16–26), or does it include back-labeling?

### 8.4 Does V13-3's output become a versioned document?

`docs/v12-wild-scan-telemetry.md` is living; it's updated after every wild scan. Should V13-3's analysis output be a separate frozen document (`docs/v13-3-analysis.md`) or an appended section in the living telemetry doc? The frozen form is easier to cite; the living form is easier to maintain.

### 8.5 Circular dependency watch

If V1.2.x harness-patches land (Priority 1/1b/1c), previously-overridden scans might have different advisory-vs-Phase-4 relationships. Should entries 16–26 be re-processed with the new signals to test whether overrides collapse? Or should existing override records be preserved as historical and new scans use new signals?

---

## 9. What V13-3 will NOT change

Per CONSOLIDATION §8 rules ("signal additions are V1.2.x, signal removals are V1.3") and the V13-1 scope-limit precedent:

- V1.2 schema freeze stays. No V1.2.x schema field additions/removals.
- Existing V1.2 wild scan bundles (entries 16–26) are historical — not re-rendered.
- The 7-gate Step G acceptance criteria don't change.
- D-6 severity-distribution comparator stays as the finding-level parity check.
- The 7-value `override_reason_enum` stays until V1.3.
- Validator gate semantics don't change.

---

## 10. Evidence tests to run (optional in R1, expected in R2)

- **Override-collapse simulation:** For Priority 1 (deserialization auto-fire), apply the proposed derivation to Kronos + freerouting form.json files and confirm the Phase 3 advisory color flips to match Phase 4 red. Does the override disappear?
- **Regex FP rate check:** Apply the language-qualifier regex proposal to 11 scan bundles. Count safe-deserialization hits suppressed vs unsafe-deserialization hits preserved.
- **Reverse-engineered-shape classifier dry-run:** Apply the V3Q4 D1 regex to 11 scan bundle READMEs. Confirm Baileys fires; confirm others don't false-positive.
- **Q3-rubric counterfactual:** For each of the 11 scans, if V3Q5 E1 landed, would Phase 4 escalate to red? Count how many would flip.

---

## 11. Required output format

Write to `.board-review-temp/v13-3-comparator-calibration/{pragmatist|codex|deepseek}-r1.md` (one file per agent). Structure:

```
# V13-3 R1 — [agent name]

## Votes
- V3Q1 (scope): [A1/A2/A3/A4-prose] — [one-sentence reason]
- V3Q2 (Priority 1 deserialization): [B1/B2/B3]
- V3Q3 (Priority 1b firmware CORS): [C1/C2/C3]
- V3Q4 (Priority 1c reverse-eng shape): [D1/D2/D3]
- V3Q5 (Q3 rubric): [E1/E2/E3/E4-prose]
- V3Q6 (V1.3 enum pruning): [F1/F2/F3/F4-prose]
- V3Q7 (V13-3 follow-up cadence): [G1/G2/G3/G4-prose]
- H (process): [H1/H2/H3]

## Rationale (prose)
[400-800 words]

## FIX NOW items (if any)
- [C-ID]: [crisp finding]

## DEFER items (if any)
- [C-ID]: [item + trigger for lifting]

## INFO items (if any)
- [C-ID]: [observation worth recording]

## Open questions the brief missed
- [question 1]
- [question 2]

## Blind spots
[Brief honest disclosure — where is your perspective weakest on this topic?]
```

**Word cap: 1800.** Be opinionated. You are in R1 Blind — disagreement is the point.

---

## 12. Files to READ (absolute paths)

Read these before voting. The brief summarizes them but they carry the full context.

**Required:**

- `/root/tinkering/stop-git-std/docs/v12-wild-scan-telemetry.md` — **primary data source** — full 11-scan cross-analysis, override distribution, harness-patch candidates.
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` — V13-3 entry at §8 line 397; V13-1 owner-directive precedent at §8.1.
- `/root/tinkering/stop-git-std/docs/v13-1-override-telemetry-analysis.md` — V13-1 analysis document (sets the template for what a V13-3 analysis document might look like).
- `/root/tinkering/stop-git-std/docs/scan-schema.json` — V1.2 schema; `override_reason_enum` definition (7 values after V13-1 expansion).
- `/root/tinkering/stop-git-std/docs/compute.py` — compute layer; current Q1–Q4 derivation rules; SIGNAL_IDS frozenset (25 entries).
- `/root/tinkering/stop-git-std/docs/scanner-catalog.md` — rows 16–26 (the 11 V1.2 wild scans) with per-scan summaries.

**Reference (sample the ones you need):**

- `/root/tinkering/stop-git-std/docs/board-review-data/scan-bundles/Baileys-8e5093c.json` — latest V1.2 form.json (scorecard_cells + override shape in production use).
- `/root/tinkering/stop-git-std/docs/board-review-data/scan-bundles/WLED-01328a6.json` — prior V1.2 bundle, distinct override class.
- `/root/tinkering/stop-git-std/docs/board-review-data/scan-bundles/freerouting-c5ad3c7.json` — third Q4-override example.
- `/root/tinkering/stop-git-std/docs/board-review-data/scan-bundles/wezterm-577474d.json` — zero-override example for contrast.
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/042026-schema-v12/deepseek-r1.md` — DeepSeek's R1 on V1.2, especially the `override_category` framing for V13-3.
- `/root/tinkering/stop-git-std/docs/compare-severity-distribution.py` — D-6 comparator (Reading A covered).
- `/root/tinkering/stop-git-std/docs/phase_1_harness.py` — harness producing Phase 1 output; primitive families in `STEP_A_PATTERNS`.
- `/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md` lines 740–762 — Q1–Q4 rubric that Phase 4 authors against.

---

## 13. Decision principles (from REVIEW-SOP.md)

Per the Pragmatist-Systems-Skeptic framing:

- **Pragmatist:** Is the cheapest V13-3 analysis that actually moves the ball forward? What breaks at the operator's hand if V1.2.x Priority 1/1b/1c land? Are 11 scans enough signal to justify enum pruning or rubric change?
- **Systems Thinker:** How do V1.2.x harness-patches couple with compute.py + the scan drivers + existing fixtures? Does landing Priority 1 before 1b/1c introduce order-of-operations issues? What second-order effects does a Q3-rubric change have on prior-scan comparability?
- **Skeptic:** What assumption in this brief is wrong? Is 11/11 silent-fix pattern evidence of a rubric problem or evidence of a community norm the rubric correctly describes? Are 4 unexercised enum values dead or sleeping? Is the "Q4 is the override hotspot" reading an artifact of sample shape rather than a structural pattern?

---

## 14. Meta-context (non-voting)

- V13-3 trigger fired 2026-04-20 with Baileys entry 26 — the 11th V1.2 wild scan.
- HEAD at brief authoring: `c558b9f` on origin/main.
- 385/385 tests passing.
- Operator is comfortable with either (a) landing V1.2.x harness-patches this session or (b) closing V13-3 with additive-only V1.2.x changes + V1.3 deferrals.
- No external deadline. Quality > speed. R2 + R3 follow SOP normally if R1 is divergent.
- Implementation owner: same operator who built the harness + compute + wrote the V13-1 owner directive. Familiar with every line of `docs/v12-wild-scan-telemetry.md`.
- Board composition: Pragmatist (Claude Sonnet 4.6), Systems Thinker (Codex GPT-5.2), Skeptic (DeepSeek V4.0 via Qwen CLI). Each reads this brief cold.
