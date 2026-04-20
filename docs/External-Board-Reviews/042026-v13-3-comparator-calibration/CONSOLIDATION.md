# V13-3 Board Review — 11-scan Comparator Calibration Analysis

**Review topic:** V13-3 (CONSOLIDATION.md §8 row 3, 042026-schema-v12 board) — 11-scan comparator calibration analysis triggered at catalog entry 26 (WhiskeySockets/Baileys), the 11th V1.2-schema wild scan.

**Board composition:** Pragmatist (Claude Sonnet 4.6), Systems Thinker (Codex GPT-5.2), Skeptic (DeepSeek V4.0 via Qwen CLI).

**Date range:** 2026-04-20 (single-session, R1 Blind → R2 Consolidation → R3 Deliberation → owner-directive close).

**Outcome:** **CLOSED** with 2/3 R3 AGREE convergence + owner directive applied on the absent 3rd agent (Codex backend unavailable during R3 window; R2 Codex positions consistent with approved R3 resolutions — see §8 below).

**HEAD at close:** `c558b9f` on origin/main.

---

## 1. Review timeline

| Round | Type | Agents reporting | Outcome |
|---|---|---|---|
| R1 | Blind | 3 / 3 | 7 decision axes + H process question; majority positions on 6/8, 3-way split on V3Q7, converged on V3Q3 unanimously |
| R2 | Consolidation | 3 / 3 | 20 C-items; 16 closed at R2 unanimous or near-unanimous; 4 live items (C5/C7/C9/C10) escalated to R3 |
| R3 | Deliberation (narrow) | 2 / 3 | Pragmatist + Skeptic both 4/4 AGREE on R3 resolutions; Codex unavailable (OpenAI backend "high demand" — 3 retry attempts failed) |
| Close | Owner directive | — | 2/3 convergence + Codex R2 pattern consistent with R3 resolutions; V13-3 closed by owner per §8 below |

---

## 2. R1 vote matrix

| Q | Question | Pragmatist | Codex | DeepSeek |
|---|---|---|---|---|
| V3Q1 | V13-3 scope | A3 both | A3 both | A2 broad |
| V3Q2 | Priority 1 deserialization | B1 land | B1 land | B2 defer |
| V3Q3 | Priority 1b firmware CORS | C2 defer | C2 defer | C2 defer |
| V3Q4 | Priority 1c reverse-eng | D2 defer | D2 defer | D3 reject |
| V3Q5 | Q3 rubric | E2 add enum | E3 keep | E3 keep |
| V3Q6 | V1.3 enum pruning | F2 prune 1 | F2 prune 1 | F3 prune none |
| V3Q7 | Follow-up cadence | G3 conditions | G4 (N=25 OR event) | G2 (N=25) |
| H | Process | H2 directive | H1 full board | H1 full board |

**R1 convergence:** V3Q3 unanimous. Majority on V3Q1/V3Q2/V3Q4/V3Q5/V3Q6. 3-way split on V3Q7.

**Owner directive OD-1 applied before R2:** Continue with full board per H majority (H1 2/3). Pragmatist's H2 (close after R1) dissent noted; applied asymmetrically — unanimous items close at R2, contested items continue to R3.

---

## 3. R2 vote matrix (20 C-items)

| Agent | AGREE | DISAGREE | MODIFY |
|---|---|---|---|
| Pragmatist | 20 | 0 | 0 |
| Codex | 18 | 0 | 2 (C10 broaden, C14 narrow exception clause) |
| DeepSeek | 16 | 3 (C5, C7, C9) | 1 (C10 tighten) |

**Closed at R2 (16 items):** C1, C2, C3, C4, C6, C8, C11, C12, C13, C14 (with Codex's narrow-exception clause accepted), C15, C16, C17, C18, C19, C20.

**Live to R3 (4 items):** C5, C7, C9, C10.

---

## 4. R3 resolutions (owner-authored post-R2; AGREE/BLOCK on each)

### 4.1 C5 — Priority 1 deserialization auto-fire: **LAND V1.2.x with atomic C2/C18/C20 prerequisites**

**Resolution:** Priority 1 compute derivation lands in V1.2.x as the majority position. Atomic co-landing of:
- **C2** (V12x-9 language qualifier regex suppressing ArduinoJson-class C/C++/Rust JSON FPs)
- **C18** (`derive_tool_loads_user_files()` helper in `docs/compute.py`)
- **C20** (dry-run FP test on 11 existing bundles before commit — landing gate)

Skeptic's "primitive taxonomy redesign" concern preserved as new item **N1** seeding V1.3 principled compute expansion. Deserialization primitive family will be revisited in V1.3 with intent of decomposing into language-qualified sub-families. V1.2.x C5 landing is a bounded exception that uses existing data paths.

**Votes:** Pragmatist AGREE, Skeptic AGREE, Codex unavailable (R2 AGREE consistent with resolution).

### 4.2 C7 — Priority 1c reverse-engineered-API shape signal: **DEFER V1.3 with triggered-promotion-or-REJECT gate**

**Resolution:** DEFER as majority position. Promotion trigger: **≥3 confirmed reverse-engineered-API-library scans in V1.2 catalog AND dry-run FP test against bundle corpus shows 0 FPs on vendor-authorized third-party clients (Matrix SDK, official Discord libraries, Zoom SDK, etc.).** If dry-run FP rate is non-zero, Skeptic's D3 REJECT option is live for V1.3 review.

**Votes:** Pragmatist AGREE, Skeptic AGREE, Codex unavailable (R2 AGREE-defer consistent with resolution).

### 4.3 C9 — V1.3 enum pruning of `missing_qualitative_context` only: **APPROVE with historical-hold + re-instate trigger**

**Resolution:** Prune `missing_qualitative_context` in V1.3 with two guardrails:

1. **Historical-hold:** Pre-V13-1 scans (entries 1-15) retain the catchall in their bundles; forward-only removal via `schema_version`-aware validator.
2. **Re-instate trigger:** If any new V1.3+ scan produces an override fitting none of the other 6 enum values, `missing_qualitative_context` is re-instated. Pruning is reversible.

Skeptic's sample-bias concern preserved for the other 3 unused values (`threshold_too_lenient`, `rubric_literal_vs_intent`, `other`) — held as headroom through V1.3; re-evaluated at N=25 wild scans or under the C10 trigger.

**Votes:** Pragmatist AGREE, Skeptic AGREE, Codex unavailable (R2 AGREE consistent with resolution).

### 4.4 C10 — V13-3 follow-up cadence: **G4-broadened — N=25 OR any taxonomy-strain event (superset of all 3 R1 positions)**

**Resolution:** V13-3 follow-up analysis re-triggers on **whichever comes first**:

- **(a) count trigger:** N=25 total V1.2 wild scans (counting from entry 16 ghostty).
- **(b) event triggers (ANY of):**
  1. `signal_vocabulary_gap` concentration crosses >80% of all overrides.
  2. ≥2 new enum values fire in a single scan.
  3. A case fits NONE of the 7 enum values (enum-escape).
  4. Genuine multi-label ambiguity.
  5. A materially new override class appears (Systems R2 broadened condition).
  6. 3 consecutive scans produce override patterns not explainable by current enum (Skeptic R2 modification).

Count-trigger-first-fires → routine telemetry refresh. Event-trigger-first-fires → targeted taxonomy-strain investigation with potential V13-4 or override-enum-expansion implications.

**Votes:** Pragmatist AGREE, Skeptic AGREE, Codex unavailable (R2 MODIFY broadening was explicitly adopted — resolution supersets Codex's R2 position).

---

## 5. Full carry-forward disposition table (20 C-items + N-items)

| ID | Item | Final disposition |
|---|---|---|
| **C1** | Write `docs/v13-3-analysis.md` as frozen A3-scoped document | **FIX NOW** — owner-authored deliverable |
| **C2** | V12x-9 language qualifier regex on deserialization family | **FIX NOW** — atomic prerequisite for C5 |
| **C3** | Freeze entries 16-26 as historical; counterfactual-only | **CONFIRMED** — codified as OD-3 |
| **C4** | Document sample bias explicitly in V13-3 analysis | **FIX NOW** — Skeptic's R1 C-1 absorbed |
| **C5** | V3Q2 Priority 1 deserialization auto-fire (LAND V1.2.x) | **FIX NOW** (V1.2.x landing) with C2/C18/C20 atomic prerequisites; Skeptic taxonomy-redesign → N1 |
| **C6** | V3Q3 Priority 1b firmware CORS (DEFER V1.3) | **DEFER** — trigger: ≥2 firmware/IoT scans + shape-classification infrastructure |
| **C7** | V3Q4 Priority 1c reverse-eng shape (DEFER V1.3) | **DEFER** — trigger: ≥3 confirmed fires + dry-run FP=0; fallback REJECT if FP>0 |
| **C8** | V3Q5 Keep Q3 rubric as-is + deferred V13-4 enum addition | **CONFIRMED** — Pragmatist shifted from E2 to AGREE on E3+deferred; V13-4 enum addition (`community_norms_differ`) deferred to N=15 or first Q3 override fire |
| **C9** | V3Q6 Prune `missing_qualitative_context` in V1.3 | **DEFER** to V1.3 with historical-hold + re-instate trigger guardrails |
| **C10** | V3Q7 V13-3 follow-up cadence | **DEFER** — G4-broadened superset (count N=25 OR any of 6 taxonomy-strain events) |
| **C11** | 82% scan-level override rate worth naming (INFO) | **CONFIRMED** — cite in v13-3-analysis.md |
| **C12** | Same 4 Q4 `computed_signal_refs` on 3 different root causes (INFO) | **CONFIRMED** — cite in v13-3-analysis.md; underexpressive advisory vocabulary |
| **C13** | Zero-override streak (wezterm→QuickLook→kanata) as positive calibration data (INFO) | **CONFIRMED** — cite in v13-3-analysis.md |
| **C14** | `signal_vocabulary_gap` 67% ⇒ principled expansion not one-offs (INFO) | **CONFIRMED** — principle as default for V1.3; C5 narrow V1.2.x exception allowed (Codex R2 MODIFY clause) |
| **C15** | Reading A and Reading B not shared maintenance home (INFO) | **CONFIRMED** — codified in OD-2 (D-6 living; v13-3-analysis.md frozen) |
| **C16** | V1.2-only scope for V13-3; no V2.4-era back-labeling (INFO) | **CONFIRMED** — explicit scope exclusion in v13-3-analysis.md |
| **C17** | V12x-6 multi-ecosystem manifest parsing | **DEFER** to V1.3 coordinated compute expansion package |
| **C18** | Canonical storage of "tool loads user files" derivation in compute.py | **FIX NOW** — C5 prerequisite; `derive_tool_loads_user_files()` helper |
| **C19** | V13-3 analysis document "historical vs counterfactual" section | **FIX NOW** — required section in v13-3-analysis.md |
| **C20** | Dry-run FP rate test for harness patches | **FIX NOW** (C5 landing gate) / **DEFER** (C6/C7 V1.3 promotion gate) |
| **N1** | Deserialization primitive family taxonomy redesign | **V1.3 candidate** (Skeptic R2 — preserved as principled V1.3 work) |
| **N2** | Statistical confidence intervals on 67% modal rate | **CONFIRMED** — calculate in v13-3-analysis.md (Skeptic R2) |
| **OD-1** | Continue with full board per H majority | **CONFIRMED** — applied asymmetrically |
| **OD-2** | `v13-3-analysis.md` as frozen deliverable mirroring v13-1 template | **CONFIRMED** — C1 implementation follows |
| **OD-3** | Entries 16-26 historical; counterfactual-only modeling | **CONFIRMED** — codified, cited in v13-3-analysis.md |

---

## 6. Owner directives applied

**OD-1 (R1 → R2 handoff):** Full board per 2/3 H1. Pragmatist H2 dissent noted; expedited-path applied asymmetrically (close unanimous R2 items, continue contested to R3).

**OD-2 (R2 brief):** V13-3 output is `docs/v13-3-analysis.md` — frozen, mirrors `docs/v13-1-override-telemetry-analysis.md` structure. `docs/v12-wild-scan-telemetry.md` remains living.

**OD-3 (R2 brief):** Entries 16-26 historical. V13-3 may simulate counterfactually; must not re-render bundles or update `override_reason` records.

**OD-4 (R3 close — this directive):** V13-3 CLOSES with 2/3 R3 convergence + owner directive. See §8.

---

## 7. Dissent audit (SOP §4 Pre-Archive Gate — zero silent drops)

Per SOP: *"Every FIX NOW, DEFER, INFO, blind spot, meta-dissent, and non-trivial nuance raised in R1 … must enumerate source (agent + round), R2 vehicle, and final-round resolution."*

### 7.1 R1 items

| R1 source | Item | R2 vehicle | Final resolution |
|---|---|---|---|
| **Pragmatist R1 FN-1** | V12x-9 hard prerequisite for Priority 1 | C2 | **Applied** — atomic with C5 |
| **Pragmatist R1 DEFER V3Q3 C2** | Priority 1b firmware CORS defer | C6 | **Applied** — DEFER V1.3 |
| **Pragmatist R1 DEFER V3Q4 D2** | Priority 1c reverse-eng defer | C7 | **Applied** — DEFER V1.3 with trigger |
| **Pragmatist R1 DEFER V3Q6-remainder** | Keep 3 headroom enum values | C9 | **Applied** — preserved through V1.3 |
| **Pragmatist R1 INF-1** | 82% scan-level override rate | C11 | **Applied** — cite in v13-3-analysis.md |
| **Pragmatist R1 INF-2** | V1.2-only scope; no V2.4 back-labeling | C16 | **Applied** — explicit scope exclusion |
| **Pragmatist R1 INF-3** | Mirror v13-1 doc structure | C1 | **Applied** — OD-2 |
| **Pragmatist R1 OQ-1** | V12x-6 multi-ecosystem parsing scope | C17 | **Applied** — DEFER V1.3 |
| **Pragmatist R1 OQ-2** | Non-retroactivity rule explicit codification | C3/C19 | **Applied** — OD-3 + v13-3-analysis.md section |
| **Pragmatist R1 Blind spot** | Priority 1 threshold mechanics unverified | BS-1 | **Mitigation applied** — C20 dry-run gate + Codex code-review before commit |
| **Codex R1 C-1** | Define V13-3 as A3 in analysis | C1 | **Applied** — OD-2 |
| **Codex R1 C-2** | Priority 1 must ship paired with language-qualified matching | C2 | **Applied** — atomic with C5 |
| **Codex R1 C-3** | Freeze entries 16-26 as historical bundles | C3 | **Applied** — OD-3 |
| **Codex R1 D-1** | Priority 1b firmware CORS defer with dry-run trigger | C6 | **Applied** — DEFER V1.3 |
| **Codex R1 D-2** | Priority 1c reverse-eng defer pending wider comparator | C7 | **Applied** — DEFER V1.3 with trigger |
| **Codex R1 D-3** | Q3 rubric escalation defer | C8 | **Applied** — rubric kept; V13-4 enum addition deferred |
| **Codex R1 I-1** | Same 4 Q4 signal_refs on 3 root causes (underexpressive vocabulary) | C12 | **Applied** — cite in v13-3-analysis.md |
| **Codex R1 I-2** | Reading A (D-6 living) vs Reading B (V13-3 frozen) separate homes | C15 | **Applied** — OD-2 |
| **Codex R1 OQ-1** | Canonical storage of "tool loads user files" derivation | C18 | **Applied** — `derive_tool_loads_user_files()` in compute.py |
| **Codex R1 OQ-2** | v13-3-analysis.md "historical vs counterfactual" section | C19 | **Applied** — required section |
| **Codex R1 Blind spot** | FP profile of shape classifiers outside sampled bundles | BS-2 | **Mitigation applied** — C20 dry-run gate (C5) / V1.3 promotion gate (C6/C7) |
| **Skeptic R1 C-1** | Document sample bias (Python/Rust heavy, missing PHP/Swift/Kotlin/Lua) | C4 | **Applied** — explicit paragraph in v13-3-analysis.md |
| **Skeptic R1 C-2** | Reject "dead enum" narrative; keep all 7 through V1.3 | C9 | **Partially applied** — prune only `missing_qualitative_context` (superseded by V13-1); keep other 3 as headroom (Skeptic's core concern). Historical-hold + re-instate trigger guardrails preserve Skeptic's reversibility requirement |
| **Skeptic R1 D-1** | All Priority 1-3 harness patches → V1.3 | C5/C6/C7 | **Majority overruled on C5** (2/3 land); **applied on C6/C7** (DEFER). Skeptic's concern preserved as N1 (V1.3 taxonomy redesign) |
| **Skeptic R1 D-2** | Q3 rubric adjustment → Never | C8 | **Applied** — rubric kept as-is |
| **Skeptic R1 I-1** | Zero-override streak as positive calibration data | C13 | **Applied** — cite in v13-3-analysis.md |
| **Skeptic R1 I-2** | Principled expansion not one-off patches | C14 | **Applied** — principle as default for V1.3; C5 narrow V1.2.x exception allowed per Codex R2 MODIFY |
| **Skeptic R1 OQ-1** | FP rate dry-run against 11 existing scans | C20 | **Applied** — FIX NOW landing gate for C5 |
| **Skeptic R1 OQ-2** | Phase 4 judgment change if Q4 auto-fires (circular logic concern) | BS-3 | **Unresolved** — preserved as open question for Codex code-review gate to evaluate on staged diff |
| **Skeptic R1 OQ-3** | Hypothetical test cases for 4 unused enum values | (not directly addressed) | **EXPLICIT-DROP with rationale:** Designing hypothetical test cases for unused enum values is V13-3-analysis.md scope creep; deferred to the unsampled-shape triggers already encoded in C9 re-instate trigger and C10 event triggers |
| **Skeptic R1 Blind spot BS-1** | Language qualifier implementation complexity not examined | Preserved | **Mitigation applied** — Codex code-review gate on staged diff before commit (implementation catches this) |
| **Skeptic R1 Blind spot BS-2** | Confidence intervals on 67% modal rate not calculated | N2 | **Applied** — required computation in v13-3-analysis.md |

### 7.2 R2 items

| R2 source | Item | Final resolution |
|---|---|---|
| **Pragmatist R2 meta** | Shifted G3 → G4 (Systems' superset better) | **Applied** — C10 R3 resolution is G4-broadened |
| **Pragmatist R2 meta** | Shifted E2 → AGREE on E3+deferred-V13-4 | **Applied** — C8 |
| **Codex R2 MODIFY C10** | Broaden G4 to "any taxonomy-strain event" | **Applied** — C10 R3 resolution includes Systems condition (5) |
| **Codex R2 MODIFY C14** | Principle as default + narrow V1.2.x exceptions allowed | **Applied** — C14 resolution allows C5 as bounded exception |
| **Codex R2 N1** | Distinguish "underexpressive advisory vocabulary" vs "underpowered override enum" | **Applied** — citation requirement in v13-3-analysis.md |
| **Codex R2 explicit non-escalation** | Not pressing Q3 re-open | **Applied** — C8 stable |
| **Codex R2 explicit non-escalation** | Not pressing reverse-eng REJECT beyond defer | **Applied** — C7 DEFER with trigger |
| **Skeptic R2 DISAGREE C5** | Deserialization taxonomy broken; V1.3 redesign | N1 | **Applied as V1.3 item** |
| **Skeptic R2 DISAGREE-REJECT C7** | ToS-violation not automatable | **Preserved as REJECT fallback** | **Applied** — C7 resolution preserves Skeptic D3 as live alternative if FP gate fails |
| **Skeptic R2 DISAGREE C9** | Sample bias insufficient for pruning | **Guardrails applied** — historical-hold + re-instate trigger mitigate sample-bias concern |
| **Skeptic R2 MODIFY C10** | Tighten toward G2+events | **Applied** — C10 resolution includes Skeptic condition (6) |
| **Skeptic R2 N1** | Taxonomy redesign (duplicate of Skeptic DISAGREE C5) | **Applied as V1.3 item (same as N1)** |
| **Skeptic R2 N2** | Confidence intervals on 67% modal rate | **Applied** — required in v13-3-analysis.md |
| **Skeptic R2 explicit non-escalation C8** | Accept E3 despite R1 E2-equivalent dissent | **Applied** — stable |
| **Skeptic R2 explicit non-escalation C10** | Accept G4 with count floor | **Applied** — G4-broadened resolution preserves count floor |

### 7.3 R3 items

| R3 source | Item | Final resolution |
|---|---|---|
| **Pragmatist R3 Blind spot BS-1 persisting** | Threshold mechanics unverified at code level | **Applied** — Codex code-review gate on staged diff is mandatory |
| **Skeptic R3 Blind spot "Phase 4 circular logic"** | Would Phase 4 override Q4 auto-fire? | **Applied** — Codex code-review gate evaluates this on staged diff |

### 7.4 Pass criterion

**Silent drops: 0.** Every R1/R2/R3 item has explicit disposition: applied, absorbed into another C-item, explicitly dropped with rationale (1 instance, Skeptic OQ-3), preserved as V1.3 work (N1, N2), or flagged for Codex code-review gate (BS-1, BS-3).

Audit passes SOP §4 Pre-Archive Gate.

---

## 8. R3 Codex unavailability — owner directive resolution

**Situation:** Codex GPT-5.2 backend returned persistent "ERROR: We're currently experiencing high demand" on all 3 R3 launch attempts during the R3 window. Error is OpenAI-side capacity, not authentication (confirmed: `codex --version` + `sudo -u llmuser` both functional; R1 + R2 rounds completed without issue earlier in the same session).

**Available R3 data:**
- Pragmatist R3: 4/4 AGREE
- Skeptic R3: 4/4 AGREE
- Codex R3: unavailable

**Owner directive close rationale:**

Codex's R2 positions are already consistent with each R3 resolution:

| R3 resolution | Codex R2 position | Consistency |
|---|---|---|
| **C5** LAND V1.2.x + atomic C2/C18/C20 | R2 AGREE with "only in paired form with C2, C18, and C20" | ✅ Verbatim |
| **C7** DEFER V1.3 + triggered-promotion-or-REJECT gate | R2 AGREE-defer; explicit non-escalation "not pressing rejection beyond defer" | ✅ Consistent |
| **C9** Prune `missing_qualitative_context` only with historical-hold | R2 AGREE — "`missing_qualitative_context` now reads as a superseded catchall; the other three should remain as headroom" | ✅ Consistent |
| **C10** G4-broadened superset | R2 MODIFY broadening G4 to "any taxonomy-strain event" — the R3 resolution literally adopts Codex's R2 modification | ✅ Codex's own modification |

The R3 resolutions were specifically authored to incorporate Codex's R2 MODIFY on C10 and Codex's R2 AGREE + non-escalation posture on C5/C7/C9. Codex's absent R3 vote does not change the resolution; the resolution already matches Codex's stated R2 position across all 4 items.

**Per SOP §4 "Failed agents must be re-run":** Three retry attempts made, each failing with identical backend-capacity error. Per SOP Pre-Round Validation: *"Only proceed with fewer agents if the retry also fails AND the owner explicitly approves continuing with reduced coverage."*

**Owner directive OD-4:** V13-3 CLOSES at R3 with 2/3 agent convergence + documented Codex R2 consistency. Review is archived. Codex is assigned the code-review gate on the staged V1.2.x implementation diff (see §9) — that provides Codex's substantive review on the actual artifacts rather than a vote on their design specification.

**Precedent note:** This is the first V13-series close with an absent agent. The pattern for future review is: if R2 positions align unambiguously with R3 resolutions and the absent agent's role can be recovered downstream (here: code-review gate), owner directive close is defensible. If R2 positions are ambiguous or the agent's role cannot be recovered downstream, defer R3 close until the agent is available.

---

## 9. Implementation roadmap

### 9.1 V1.2.x atomic landing (single commit post-Codex-review)

The following files/changes ship together as one commit:

1. **docs/phase_1_harness.py** — V12x-9 language qualifier on deserialization regex (C2). Pattern restructured to emit per-language family tags: `deserialization.python.pickle`, `deserialization.java.objectinputstream`, `deserialization.ruby.marshal`, `deserialization.safe.json` (ArduinoJson, jq, serde_json, etc. — gated out of critical-path derivation).

2. **docs/compute.py** — three additions:
   - `derive_tool_loads_user_files(readme_text, repo_metadata, install_paths) -> bool` helper (C18). Reads README for keywords like "open file", "load", "import", "parse" plus repo topic analysis.
   - New computed signal `q4_critical_on_default_path_from_deserialization` firing when (deserialization.python.pickle OR deserialization.java.objectinputstream OR deserialization.ruby.marshal).hit_count ≥ 3 AND `derive_tool_loads_user_files()` returns True.
   - Q4 rollup: if new signal fires, `q4_has_critical_on_default_path = True` (advisory).

3. **tests/test_compute.py** — new test class `TestV13_3_DeserializationAutoFire` with positive/negative cases for the helper + signal + Q4 rollup.

4. **tests/test_phase_1_harness.py** — new test class `TestV13_3_LanguageQualifier` confirming ArduinoJson `deserializeJson` suppressed; pickle.load preserved; ObjectInputStream.readObject preserved; Marshal.load preserved.

5. **docs/v13-3-fp-dry-run.md** — C20 artifact: dry-run applied to all 11 V1.2 scan bundles. Reports (a) suppressed safe-JSON hits, (b) preserved unsafe-deserialization hits, (c) simulated Q4 auto-fire outcomes per bundle. Must show 0 FPs before commit lands.

6. **docs/v13-3-analysis.md** — C1/C4/C11/C12/C13/C14/C15/C16/C19 + N1/N2 required sections. Mirrors `docs/v13-1-override-telemetry-analysis.md` template.

### 9.2 Persistent state updates (same commit)

7. **docs/scan-schema.json** — `override_reason_enum` description updated to note V13-3 close + future V1.3 pruning candidate (`missing_qualitative_context` marked as deprecated; no actual enum removal yet since schema stays V1.2).

8. **docs/v12-wild-scan-telemetry.md** — §10 changelog entry noting V13-3 close + Priority 1 landing.

9. **CLAUDE.md** — current-state paragraph updated to note V13-3 RESOLVED via board + owner directive, V1.2.x Priority 1 landed, next V1.3 targets (N1 taxonomy redesign, C6/C7 promotion gates).

10. **REPO_MAP.md §2.5** — V13-3 marked CLOSED; V1.3 items (N1, C6/C7 promotion, C17 multi-ecosystem parsing, V13-4 `community_norms_differ` enum addition trigger) added to deferred ledger.

### 9.3 Codex code-review gate (mandatory before commit)

Per owner directive, run `codex review` (not `codex exec`) on the staged diff before the commit lands. This provides Codex's R3-equivalent review on the actual artifacts rather than the design spec. Review targets:

- **BS-1 (Pragmatist):** threshold mechanics in compute.py (N=3 deserialization hits? language-qualifier regex precisely matches intended families?)
- **BS-3 (Skeptic):** circular-logic check — would Phase 4 override the auto-fire? (implementation-level review)
- **FP coverage:** does `test_phase_1_harness.py` regression-test the ArduinoJson suppression?
- **Derivation helper:** is `derive_tool_loads_user_files()` testable and deterministic?

FIX NOW items from Codex code-review → address and re-review. No commit lands until Codex signs off.

### 9.4 V1.3 items added to deferred ledger

- **N1:** Deserialization primitive family taxonomy redesign (Skeptic's concern). Trigger: C10 count (N=25) or event trigger.
- **C6 promotion:** Priority 1b firmware CORS compound signal. Trigger: ≥2 firmware/IoT scans + shape-classification infrastructure.
- **C7 promotion-or-REJECT:** Priority 1c reverse-engineered-API shape signal. Trigger: ≥3 confirmed fires + dry-run FP test = 0 FPs. If FP > 0, REJECT.
- **C9:** Prune `missing_qualitative_context` with historical-hold + re-instate trigger.
- **C17:** V12x-6 multi-ecosystem manifest parsing (Maven/Gradle/Cargo/Gomod/Bundler/.NET).
- **V13-4:** `community_norms_differ` enum addition. Trigger: N=15 OR first Q3 override fire.

---

## 10. Files produced by this review

Living (this review directory):
- `r1-brief.md` — 366 lines
- `r2-brief.md` — 477 lines
- `r3-brief.md` — 258 lines
- `pragmatist-r1.md` / `pragmatist-r2.md` / `pragmatist-r3.md`
- `codex-r1.md` / `codex-r2.md` (R3 unavailable)
- `deepseek-r1.md` / `deepseek-r2.md` / `deepseek-r3.md`
- `deepseek-r1-raw.log` / `deepseek-r2-raw.log` / `deepseek-r3-raw.log` — Qwen stdout capture
- `codex-r1-raw.log` / `codex-r2-raw.log` / `codex-r3-raw.log` — Codex stdout capture (r3 shows failure)
- `CONSOLIDATION.md` — this document

To be produced during implementation (per §9):
- `docs/v13-3-analysis.md` — frozen analysis artifact (C1)
- `docs/v13-3-fp-dry-run.md` — C20 dry-run artifact

---

## 11. Sign-off

**Review closed:** 2026-04-20 by owner directive OD-4. 2/3 R3 AGREE convergence (Pragmatist + Skeptic); Codex R3 unavailable due to OpenAI backend capacity; Codex R2 positions consistent with all R3 resolutions; Codex assigned code-review gate on staged implementation diff as substantive-review surrogate.

**Dissent audit:** PASS — zero silent drops per SOP §4 Pre-Archive Gate.

**Next step:** Implementation per §9, Codex code-review gate, then commit.
