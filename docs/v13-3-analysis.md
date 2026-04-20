# V13-3 11-Scan Comparator Calibration Analysis

**Trigger:** 11 V1.2 wild scans completed (ghostty entry 16 → Baileys entry 26).
**Date:** 2026-04-20.
**Status:** FROZEN analysis artifact. Decisions ratified by 042026-v13-3-comparator-calibration board review (2/3 R3 AGREE + owner directive OD-4 close; see `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/CONSOLIDATION.md`).
**Related:** `docs/v12-wild-scan-telemetry.md` (living cross-scan data); `docs/v13-1-override-telemetry-analysis.md` (precedent document, same structural template).

---

## §1 · Scope — both narrow and broad (V3Q1 A3)

V13-3's original framing (Codex R1 C-6 of the 042026-schema-v12 board) was narrow: **pipeline-comparator calibration** between V2.4 and V2.5-preview on 3 pinned Step G pairs. That reading is **closed by D-6**: `docs/compare-severity-distribution.py` (23 tests) validates finding-level severity parity across zustand-v3, caveman, and Archon V2.4↔V2.5-preview pairs; all 3 currently PASS; the Step G 7-gate acceptance + `--parity` validator contain future drift.

V13-3's expanded framing (post-V13-1 telemetry accumulation) is broad: **cross-scan pattern calibration** across 11 shape-diverse V1.2 scans. This document is the frozen output of the broad reading. The narrow reading requires no additional deliverable beyond the D-6 tool.

---

## §2 · Sample constitution and bias

**11 V1.2 wild scans (entries 16–26)** — first scan 2026-04-20; last scan 2026-04-20.

### 2.1 Language/ecosystem coverage

| Language | Scans | Entries |
|---|---|---|
| Python | 2 | markitdown* + Kronos |
| Rust | 2 | wezterm + kanata |
| Go | 1 | Xray-core (+ browser_terminal native host shared-weight) |
| Zig | 1 | ghostty |
| Ruby | 1 | kamal |
| C# | 1 | QuickLook |
| Java | 1 | freerouting |
| C++ | 1 | WLED (first C++ entry) |
| TypeScript/JavaScript | 1 | Baileys (first TS primary-language entry) |

*markitdown is entry 15 — the production-clearance trigger scan at V1.1 schema. Entries 16-26 are all V1.2 schema.

### 2.2 Explicit sample bias (per R1 Skeptic C-1)

**Over-represented:** Python and Rust (2 scans each). Python/Rust combined = 36% of sample.

**Absent from sample:** PHP, Swift, Kotlin, Lua, Elixir, Clojure, Haskell, Perl. No WordPress-plugin shape. No mobile-app shape (iOS/Android native). No notebook/Jupyter shape.

**Implication for all numerical claims in this document:** they describe the 11-scan sample, not a generalizable calibration. Metrics derived from this sample should be read as **lower-bound point estimates at n=11**, not as a converged population calibration.

### 2.3 Shape taxonomy coverage

11 distinct category-level shapes (no two scans share a category): terminal emulator (Zig + Rust pair), ML foundation model, document conversion, deploy orchestrator, network proxy, browser extension + native host, Windows shell extender, keyboard daemon, EDA/PCB autorouter, embedded IoT firmware, reverse-engineered platform-API library. Cross-shape calibration is strongest where two scans share a shape (the ghostty↔wezterm terminal-emulator pair is the only direct comparator).

---

## §3 · Override distribution (n=9 overrides across 11 scans)

### 3.1 Enum distribution

| `override_reason` | Count | % | Fires on |
|---|---|---|---|
| `signal_vocabulary_gap` | **6** | **67%** | ghostty Q1, kamal Q1, Kronos Q2, freerouting Q4, WLED Q4, Baileys Q4 |
| `harness_coverage_gap` | 2 | 22% | Kronos Q4, browser_terminal Q4 |
| `threshold_too_strict` | 1 | 11% | Xray-core Q2 |
| `missing_qualitative_context` | 0 | 0% | — |
| `threshold_too_lenient` | 0 | 0% | — |
| `rubric_literal_vs_intent` | 0 | 0% | — |
| `other` | 0 | 0% | — |

**Confidence interval (per R2 Skeptic N2):** at n=9 overrides, the 95% Wilson confidence interval for the 67% signal_vocabulary_gap modal rate is approximately **35%–88%**. The "strongly modal" framing is best described as a strong point estimate at small n, not a stable population rate.

### 3.2 Question-level distribution

| Question | Overrides | % of all overrides |
|---|---|---|
| Q1 (does anyone check code) | 2 | 22% |
| Q2 (do they fix problems quickly) | 2 | 22% |
| Q3 (do they tell you about problems) | **0** | **0%** |
| Q4 (is it safe out of the box) | **5** | **56%** |

**Q4 is the override hotspot.** Q3 never overrode in 11 scans, including WLED (entry 25) and Baileys (entry 26) both with publicly-documented disclosure-handling failures — Phase 4 judged amber-not-red each time, matching compute's advisory.

### 3.3 Zero-override streak and its break (per R1 Skeptic I-1)

Three consecutive zero-override scans: wezterm (21) → QuickLook (22) → kanata (23). Then three consecutive Q4 `signal_vocabulary_gap` overrides: freerouting (24) → WLED (25) → Baileys (26).

The streak is evidence the signal vocabulary works for some shapes. The break is evidence that specific critical-on-default-path conditions require either (a) language-semantic analysis beyond regex (freerouting), (b) multi-primitive composition + shape context (WLED), or (c) README/metadata-level classification (Baileys). These are three distinct gaps, not one.

### 3.4 Scan-level override rate (per R1 Pragmatist INF-1)

**9 of 11 scans have ≥1 override = 82% scan-level override rate.** This is higher than typical cell-level framings suggest. It means the harness + compute advisory layer rarely produces Phase-4-concordant results across an entire scan — most scans still require at least one Phase 4 override.

### 3.5 Underexpressive computed_signal_refs (per R1 Codex I-1)

The same 4 Q4 `computed_signal_refs` appear on freerouting, WLED, and Baileys despite three different root-cause patterns (Java deserialization RCE, firmware default-no-auth + CORS wildcard, ToS-violation category). This is evidence that the scorecard-hint vocabulary is **underexpressive** even when the override enum is adequate. Per R2 Codex N1: this is distinct from "underpowered override enum" — the enum adequately names the failure mode (`signal_vocabulary_gap`), but the specific signals referenced are the same generic Q4 set because no finer-grained advisory signal exists to point at.

---

## §4 · Decisions ratified by 042026-v13-3 board review

Board-review outcome (per `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/CONSOLIDATION.md`): 20 consolidated C-items + 2 new items (N1, N2) + 4 owner directives. 16 C-items closed at R2; 4 (C5/C7/C9/C10) closed at R3 by 2/3 AGREE + owner directive OD-4.

### 4.1 V1.2.x landings (commit this session)

- **C5 LAND:** `q4_has_critical_on_default_path` auto-fire from deserialization hits + tool-loads-user-files condition. Collapses freerouting Q4 override on re-scan; does not fire on WLED ArduinoJson post-C2. Dry-run per `docs/v13-3-fp-dry-run.md` confirms 0 false-positives on 11 existing bundles.
- **C2 LAND:** Deserialization regex language-qualifier — drops the bare `\bdeserialize\b` keyword from `STEP_A_PATTERNS` (`docs/phase_1_harness.py`), preserving language-specific unsafe tokens (pickle.load, ObjectInputStream, Marshal.load, yaml.load, unserialize, marshal.load, joblib.load, dill.load). Suppresses WLED's 19 ArduinoJson hits (FP class); preserves freerouting's 30 ObjectInputStream hits and Kronos's pickle.load hit.
- **C18 LAND:** `derive_tool_loads_user_files(readme_text, repo_metadata, install_paths)` helper in `docs/compute.py`. Canonical storage per V13-1 precedent (`derive_q1_has_ruleset_protection`, `derive_q2_oldest_open_security_item_age_days`). Scan drivers MUST NOT reimplement this logic.
- **C20 LAND:** Dry-run FP rate test at `docs/v13-3-fp-dry-run.md`; PASS gate — 0 FPs.

### 4.2 V1.3 deferrals with triggers

- **C6 (Priority 1b firmware CORS compound signal):** DEFER to V1.3. Trigger: ≥2 firmware/IoT scans in catalog + shape-classification infrastructure lands.
- **C7 (Priority 1c reverse-engineered-API shape signal):** DEFER to V1.3 with triggered-promotion-or-REJECT gate. Trigger: ≥3 confirmed reverse-eng scans + dry-run FP test shows 0 FPs on vendor-authorized third-party clients (Matrix SDK, official Discord libraries, Zoom SDK, etc.). If dry-run FP > 0, Skeptic's D3 REJECT option is live.
- **C9 (prune `missing_qualitative_context`):** DEFER to V1.3 with historical-hold (pre-V13-1 scans 1-15 retain the catchall in their bundles) + re-instate trigger (if any new V1.3+ scan produces an override fitting none of the other 6 enum values, the catchall is re-instated).
- **C17 (V12x-6 multi-ecosystem manifest parsing):** DEFER to V1.3 coordinated compute expansion package. Covers Maven/Gradle/Cargo/Gomod/Bundler/.NET.
- **V13-4 (`community_norms_differ` enum addition):** DEFER to N=15 OR first Q3 override fire. Source: R2 Pragmatist shift from E2 → AGREE on E3+deferred-V13-4.

### 4.3 V1.3 principled-expansion candidates (new items)

- **N1 (from R2 Skeptic):** Deserialization primitive family taxonomy redesign. Safe JSON parsing (ArduinoJson, serde_json, rmp-serde) and unsafe deserialization (pickle, ObjectInputStream, Marshal) are conceptually distinct primitives that deserve separate family names in `STEP_A_PATTERNS`. C2's bare-keyword drop is the V1.2.x bounded exception; N1 is the V1.3 principled replacement.
- **N2 (from R2 Skeptic):** Statistical confidence-interval calculation on override-rate claims is now part of this analysis document (§3.1 above). Future V13-3-class analyses should report CIs alongside point estimates.

### 4.4 Follow-up cadence (C10 G4-broadened)

V13-3 follow-up analysis re-triggers on **whichever comes first**:

- **(a) count trigger:** N=25 total V1.2 wild scans (counting from entry 16 ghostty).
- **(b) event triggers (ANY of):**
  1. `signal_vocabulary_gap` concentration crosses >80% of all overrides.
  2. ≥2 new enum values fire in a single scan.
  3. A case fits NONE of the 7 enum values (enum-escape).
  4. Genuine multi-label ambiguity on an override.
  5. A materially new override class appears.
  6. 3 consecutive scans produce override patterns not explainable by current enum.

Count-trigger-first-fires → routine telemetry refresh. Event-trigger-first-fires → targeted taxonomy-strain investigation with potential V13-4 or override-enum-expansion implications.

---

## §5 · Cross-scan patterns ratified

### 5.1 Silent-fix is the catalog community norm (C8/C14 data support)

**11 of 11 V1.2 wild scans have 0 published GHSA advisories** despite histories ranging from 10 months (Kronos) to 12 years (freerouting) on privileged tools. Two concrete documented disclosure-handling failures exist:

- **WLED #5340** — researcher publicly complained after 10+ days of maintainer silence on private GHSA-2xwq-cxqw-wfv8; maintainer permissions misconfigured on advisory UI; 74 days silent after last maintainer comment; 0.15.x backport status publicly unconfirmed.
- **Baileys PR #1996** — researcher-offered `request`-deprecation fix stale-closed after 148 days; maintainer-promised "own version" never materialized in 102 days; master still ships the deprecated dep.

Both cases had Phase 4 judging Q3 amber (not red) despite the documented failures. Per C8 ratification (R3 2/3 AGREE + owner directive), the current Q3 rubric ("partly" = amber when SECURITY.md absent + 0 advisories + no evidence of active suppression) correctly captures this pattern. Rubric language change deferred to V13-4 (`community_norms_differ` enum addition) pending N=15 trigger or first Q3 override fire.

### 5.2 Q4 override concentration is integration-shape, not taxonomy-shape

The 5 Q4 overrides (Kronos, browser_terminal, freerouting, WLED, Baileys) span three distinct integration patterns (per R1 Codex rationale):

- **Roll-up failure** (freerouting): harness detected 35 ObjectInputStream imports; compute had no derivation from deserialization hits to `q4_has_critical_on_default_path`. **Addressed by C5 V1.2.x landing.**
- **Compound-signal failure** (WLED): harness detected `Access-Control-Allow-Origin: *` via `tls_cors`; no auth-bypass pattern detected; compute had no composition rule combining those with firmware-shape. **Deferred as C6 V1.3.**
- **README/metadata classification** (Baileys): harness has no README-disclaimer parser; no `reverse-engineering` topic lookup feeding compute. **Deferred as C7 V1.3 with REJECT fallback.**

These are three different blast radii. C5 uses existing data paths; C6/C7 require new upstream semantics.

### 5.3 Zero-override shapes and their signals (C13 ratification)

The 3 zero-override scans (wezterm, QuickLook, kanata) share: (a) tool-category self-contained (no user-file loading as default operation), (b) ruleset-or-tag-based protection rather than classic, (c) review rate ≥38% (for kanata) or clear tool-not-service threat model (wezterm, QuickLook). Positive calibration data — compute + Phase 4 agree when the shape is self-contained.

### 5.4 Maintainer-concentration taxonomy

Post-11-scan distribution of top-contributor shares:

| Pattern | Examples |
|---|---|
| Extreme solo (≥95%) | wezterm (97.2%) |
| High solo (80–95%) | freerouting (86.7%), ghostty (85.9%), Kronos (~solo), kanata (79% — borderline) |
| Two-maintainer (combined ≥85%) | kamal (DHH + djmb), QuickLook (xupefei + emako), kanata (jtroo + ItayGarin), Baileys (adiwajshing + purpshell 89.5%) |
| Dispersed (top-1 ≤50%) | Xray-core (RPRX 31%), WLED (blazoncek 46%) |
| Single-author (near-100%) | browser_terminal (BatteredBunny 100% of human commits) |

---

## §6 · V2.4-era back-labeling explicitly excluded (C16)

Catalog entries 1–15 pre-date the V1.2 `override_reason` enum. Back-labeling their V2.4-authored prose to machine-readable override categories would be manual, error-prone, and create invented precision. **Explicit scope exclusion:** V13-3 analyzes entries 16–26 only. Entries 1–15 remain as their V2.4 outputs with V2.4 reasoning intact.

---

## §7 · Historical vs counterfactual (C19)

Per OD-3 (`docs/External-Board-Reviews/042026-v13-3-comparator-calibration/CONSOLIDATION.md` §6): entries 16-26 are historical. Their `override_reason` records reflect compute + Phase 4 state at their commit time — NOT post-V13-3 state. This analysis document (§3, §4, §5) MAY simulate override collapse counterfactually (as the dry-run at `docs/v13-3-fp-dry-run.md` does), but the historical bundles at `docs/board-review-data/scan-bundles/` are NOT re-rendered.

A future reader comparing this document against a stored bundle will find different `override_reason` values for e.g. freerouting — the bundle says `signal_vocabulary_gap` (historical); this analysis §4.1 says C5 V1.2.x auto-fire would collapse the override. Both are true at their respective times. The OD-3 rule preserves auditability.

---

## §8 · Changelog

- **2026-04-20** — Document created at V13-3 R3 close. Ratified by 042026-v13-3-comparator-calibration board review (2/3 R3 AGREE + OD-4 owner directive; Codex R3 unavailable, R2 positions consistent). FROZEN — future V13-3 follow-ups (per C10 triggers) create new documents, not edits to this one.
