# V1.2 Wild-Scan Telemetry — Cross-Scan Analysis

**Scope:** Catalog entries 16–25 (10 V1.2-schema wild scans).
**Date:** 2026-04-20.
**Status:** Living document — update after each new V1.2 wild scan.
**Related:** [V13-1 override-telemetry analysis](v13-1-override-telemetry-analysis.md) (covered the first 3 scans and drove the V1.2.x signal widening).

This document persists cross-scan patterns that accumulate value over many scans and would otherwise be scattered across per-scan catalog rows and commit messages.

---

## §1 · Scan roster (entries 16–25)

| # | Repo | Shape | Verdict | Overrides | Override detail |
|---|---|---|---|---|---|
| 16 | ghostty-org/ghostty | Zig terminal emulator | Caution | 1 | Q1 signal_vocabulary_gap (ruleset invisible) |
| 17 | shiyu-coder/Kronos | Python ML foundation model | Critical (split) | 2 | Q2 signal_vocabulary_gap + Q4 harness_coverage_gap |
| 18 | basecamp/kamal | Ruby deploy orchestrator | Caution | 1 | Q1 signal_vocabulary_gap |
| 19 | XTLS/Xray-core | Go network proxy | Critical | 1 | Q2 threshold_too_strict |
| 20 | BatteredBunny/browser_terminal | Browser extension + Go host | Critical (split) | 1 | Q4 harness_coverage_gap (typosquat URL) |
| 21 | wezterm/wezterm | Rust terminal emulator | Caution | **0** | — |
| 22 | QL-Win/QuickLook | C# Windows shell extender | Caution | **0** | — |
| 23 | jtroo/kanata | Rust keyboard daemon | Critical | **0** | — |
| 24 | freerouting/freerouting | Java PCB auto-router | Critical | 1 | Q4 signal_vocabulary_gap (Java deserialization) |
| 25 | wled/WLED | ESP32 IoT firmware | Critical | 1 | Q4 signal_vocabulary_gap (firmware default-no-auth + CORS wildcard) |

**Totals**: 10 scans, 8 overrides, 3 zero-override.

---

## §2 · Override-enum distribution

**8 overrides across 10 scans (80% override-rate at scan level).**

| `override_reason` | Count | % | Scans |
|---|---|---|---|
| `signal_vocabulary_gap` | **5** | **62%** | ghostty Q1, kamal Q1, Kronos Q2, freerouting Q4, **WLED Q4** |
| `harness_coverage_gap` | 2 | 25% | Kronos Q4, browser_terminal Q4 |
| `threshold_too_strict` | 1 | 13% | Xray-core Q2 |
| `missing_qualitative_context` | 0 | 0% | — |
| `threshold_too_lenient` | 0 | 0% | — |
| `rubric_literal_vs_intent` | 0 | 0% | — |
| `other` | 0 | 0% | — |

**Observations:**

- **`signal_vocabulary_gap` is the modal label** at 62% of overrides (up from 57% at n=9). Each new Q4 override has been signal_vocabulary_gap rather than harness_coverage_gap — the harness is correctly detecting the fact-surface (35 ObjectInputStream imports on freerouting; CORS wildcard + no-auth on WLED) but the compute signal vocabulary doesn't roll those facts up to a cell-level judgment.
- **4 of 7 enum values unexercised** after 10 scans. `missing_qualitative_context` (the pre-V13-1 catchall) hasn't fired once since V13-1 relabeled existing entries — strong signal that the V13-1 split was correct.
- **Override fires on Q1, Q2, Q4 but not Q3** across the 10 scans. Q3 (disclosure) has been uniformly red/amber from compute and Phase 4 hasn't needed to correct it. Notably, WLED entry 25 had a strong case for Q3 override (documented disclosure-handling failure with 74-day silence on GHSA-2xwq-cxqw-wfv8) but Phase 4 kept Q3 at amber — amber already reflects "unclear/partly" which captures the WLED disclosure pattern adequately.

---

## §3 · Zero-override streak

**3 consecutive zero-override scans**: wezterm (21) → QuickLook (22) → kanata (23). Streak broken by freerouting (24), continued-broken by WLED (25).

What the zero-override scans had in common:
- **wezterm**: Rust terminal emulator, stalled 807-day release cadence, pure-tool threat model
- **QuickLook**: C# shell extender, 21-plugin parser surface but no new confirmed RCE
- **kanata**: Rust keyboard daemon, 44% formal review (exceptional), ruleset-but-anti-destruction

**What freerouting (24) added that broke the streak**: a **confirmed, specific, file-reachable RCE class** (Java ObjectInputStream on user-loaded files) that's invisible to `q4_has_critical_on_default_path` (which is set by Phase 4 authoring, not read from `dangerous_primitives.deserialization.hit_count`).

**What WLED (25) added (2nd break)**: a **confirmed, specific, remote-exploitable surface** (factory-default webserver has no auth + CORS wildcard + unauthenticated `/reset`) that's invisible to compute because the pattern lives in C++ control-flow (correctPIN gating logic tied to settingsPIN string length), not in a grep-able primitive family. `dangerous_primitives.tls_cors` DID surface the `Access-Control-Allow-Origin: *` hit, but there's no compute derivation that combines `tls_cors_hit + no_auth_primitive_detected + firmware_shape → q4_has_critical_on_default_path=True`.

**Inference (refined at n=10)**: zero-override scans remain possible when compute-signal judgment aligns with Phase 4 judgment; the break happens every time Phase 4 finds a specific critical-on-default-path condition whose identification requires either (a) language-semantic analysis beyond regex (freerouting) or (b) multi-primitive composition + shape context (WLED). Both are V12x-class harness-patch candidates.

---

## §4 · Harness-patch candidates (ordered by impact × frequency)

### Priority 1: Deserialization auto-fire for Q4

**Signal added**: compute derives `q4_has_critical_on_default_path = True` when `dangerous_primitives.deserialization.hit_count >= N` AND the tool is documented as loading user files.

**Scans it would auto-resolve**: Kronos Q4 (pickle.load in finetune/dataset.py), **freerouting Q4** (Java ObjectInputStream in BasicBoard.java). Two of the eight overrides collapse with this single change.

**Open question**: threshold N. Kronos had 0 harness hits (regex miss — now fixed in V1.2.x); freerouting had 35. After the V1.2.x pickle-regex extension, Kronos would hit. A reasonable threshold is `>= 3` plus README-pattern-match for "open file"/"load"/"import" keywords.

**New subtlety surfaced by WLED (25)**: the V1.2.x-widened deserialization regex produced 19 **false-positive** hits in WLED's C++ codebase — all `deserializeJson` calls (ArduinoJson, safe). Any auto-fire threshold on raw deserialization hit-count will mis-fire on C/C++/Rust projects using JSON libraries with `deserialize` in the function name. The auto-fire derivation needs a **language qualifier** (pickle→Python, ObjectInputStream→Java, Marshal.load→Ruby) rather than a language-agnostic regex. V12x-9 item now promoted to the Priority 1 scope.

### Priority 1b: Firmware default-no-auth + CORS-wildcard compound signal for Q4

**New class observed on WLED (25)**: the combination of (a) `dangerous_primitives.tls_cors` hit on `Access-Control-Allow-Origin: *` + (b) no auth-enforcement primitive detected on a web-server-shipping tool + (c) install-path terminus being a networked end-user device (firmware, IoT, home-LAN server) = critical-on-default-path.

**Scans it would auto-resolve**: WLED Q4.

**Signal-widening proposal**: compute derives `q4_has_critical_on_default_path = True` when `tls_cors.hit_count >= 1` (wildcard Origin/Methods/Headers pattern) AND `auth_bypass.hit_count == 0` (no auth-gate pattern detected) AND shape is `firmware | iot | on-device-webserver`. Shape classification would be a new compute-side input — bootstrappable from README keywords (ESP32, ESP8266, firmware, on-device, LAN webserver) + install-path signals (.bin releases, browser-WebSerial flasher).

### Priority 2: Multi-ecosystem Maven/Gradle/Cargo/Gomod parsing

**Gap observed across 5 of 9 scans** (Xray-core, kamal, wezterm, kanata, QuickLook, freerouting — actually 6):
- Go gomod: Xray-core
- Ruby Gemfile.lock: kamal
- Rust Cargo.lock: wezterm + kanata
- .NET .csproj / .sln: QuickLook
- Java build.gradle: freerouting

Each dumps `runtime_count=0` and `osv total_vulns=0` despite real dep graphs. Scanner workaround each time is Phase 4 annotation. **Single consolidated patch** implementing parser + OSV-query for all 5 ecosystems would close a family of F5/F6-class findings and enable real dep-CVE telemetry.

### Priority 3: Install-doc URL TLD-deviation detection

**Scans affected**: browser_terminal (F0 typosquat URL `chrome.google.cm` in installation.md).

**Proposed check**: README / install-doc URL parse; flag links whose host matches a known-good domain prefix (e.g., `chrome.google`, `addons.mozilla.org`, `pypi.org`, `rubygems.org`) but with a non-matching TLD or subdomain.

**Impact**: Would have surfaced the browser_terminal Critical without Phase 4 override. Rare-but-high-impact class of finding.

### Priority 4: Distribution-channel detection for language-specific package managers

**Gap observed**: real distribution channels are frequently not detected:
- GitHub Releases binaries: wezterm, kanata, freerouting, Xray-core
- Homebrew formulas: ghostty, wezterm, kamal
- `gem install` + RubyGems.org: kamal
- `cargo install kanata` + crates.io: kanata (works for single top-level crate, surfaces workspace members as fictitious channels)
- Chrome Web Store + Firefox Add-ons: browser_terminal
- MSI + Scoop + MS Store: QuickLook
- Docker images on ghcr.io: freerouting

**Fix**: introduce channel-detector modules per ecosystem; confirm via live registry lookups (`npm view`, `gem info`, `cargo search`) rather than package-manifest presence alone.

---

## §5 · Cross-shape patterns

### 5.1 · C20 calibration

**C20 rule fires Critical when**: `no_classic AND no_rulesets AND no_rules_on_default AND no_codeowners AND ships_executable_code AND has_recent_release_30d`.

Firing pattern observed:

| Scan | Recent release? | C20 result | Verdict |
|---|---|---|---|
| Xray-core (19) | Yes (3 days) | **Critical** | Critical |
| kanata (23) | Yes (8 days) | **Critical** | Critical |
| wezterm (21) | No (807 days) | Warning | Caution |
| browser_terminal (20) | No (300 days) | Warning | Critical (via F0 typosquat) |
| freerouting (24) | No (373 days) | None | Critical (via F0 deserialization) |
| ghostty (16) | No (1200+ days) | Warning | Caution |
| QuickLook (22) | Yes | Warning | Caution |
| Kronos (17) | No releases ever | Warning | Critical (via F0 pickle RCE) |
| kamal (18) | Yes | Warning | Caution |

**C20 calibration is working well** — it correctly identifies "active release cadence + no governance gates" as the conditions under which unreviewed commits reach users fastest. Stale-release repos dodge C20 because the pathway is blunted even if the gates are equally absent.

**Caveat**: C20 doesn't catch the ACTUAL critical findings (F0 pickle RCE on Kronos, F0 typosquat on browser_terminal, F0 Java deserialization on freerouting). Those reach Critical verdict via Phase 4 authoring, not via C20. C20 is one of several Critical pathways, not the main one.

### 5.2 · Silent-fix / zero-advisories consistency

**10 of 10 V1.2 wild scans have 0 published GHSA advisories** despite histories ranging from 10 months (Kronos) to 12 years (freerouting) on privileged tools:

| Scan | Years active | Advisories | Threat surface |
|---|---|---|---|
| ghostty (16) | 4 | 0 | Terminal emulator |
| Kronos (17) | 10 months | 0 | ML model + Flask webui |
| kamal (18) | 3 | 0 | SSH + docker orchestrator |
| Xray-core (19) | 5.5 | 0 | Network proxy (privileged) |
| browser_terminal (20) | 3 | 0 | Browser extension + shell bridge |
| wezterm (21) | 8 | 0 | Terminal + SSH + Lua exec |
| QuickLook (22) | 9 | 0 | 21-plugin parser surface |
| kanata (23) | 4 | 0 | Keyboard interceptor |
| freerouting (24) | 12 | 0 | Java deserialization surface |
| WLED (25) | 9 | 0 | ESP32 firmware + on-device webserver |

**Pattern (n=10)**: even active, widely-used privileged tools uniformly skip GHSA publication. Readings are (a) no security-relevant issues discovered (implausible for this sample), (b) silent-fix-via-release cadence, (c) disclosure stops at maintainer.

**WLED strengthens reading (c)**: WLED (25) has a **publicly-documented disclosure-handling failure** — issue #5340 shows a researcher had to escalate publicly after 10+ days of maintainer silence on a private GHSA, and once a maintainer responded he said the critical had been 'reported before and fixed' without publishing a GHSA for either the old fix or the new report. That's a specific instance of the silent-fix pattern where the maintainer's framing confirms the pattern is deliberate ('other issues reported are very fairly basic rather than significant discoveries') rather than accidental.

**Implication for V1.3**: the `community_norms_differ` enum value that DeepSeek preserved as a V1.3 expansion trigger (CONSOLIDATION §5 R3 Item C) hasn't fired — but the silent-fix pattern is NOW the documented community norm for this catalog's shape. WLED's documented process failure (private-advisory permissions misconfigured, maintainer couldn't view own project's advisory) is a sharper version of the pattern worth revisiting whether Q3's red/amber rubric should adjust. Specifically: when a researcher publicly documents disclosure-handling failure on a repo with 0 published advisories, should Q3 escalate from amber to red?

### 5.3 · Maintainer concentration taxonomy

| Pattern | Examples |
|---|---|
| Extreme solo (≥95%) | wezterm (97.2%) |
| High solo (80–95%) | freerouting (86.7%), ghostty (85.9%), Kronos (59% top-1 but effectively solo), kanata (79% — just below 80% threshold) |
| Two-maintainer (combined ≥85%) | kamal (DHH+djmb 85%), QuickLook (xupefei+emako 94%), kanata (jtroo+ItayGarin 91%) |
| Dispersed (top-1 ≤40%) | Xray-core (31% RPRX with dependabot-bot as #2) |
| Single author (near-100%) | browser_terminal (BatteredBunny 100% of human commits) |

### 5.4 · Formal PR review rate distribution

Ordered high → low:
- kanata: **44%** (highest)
- freerouting: 9.5%
- Xray-core: 7.7%
- QuickLook: 5.1%
- kamal: 4.7%
- Xray-core formal: 2.3% (formal-only; any-review 7.7%)
- wezterm: 3.3%
- Kronos: 0%
- browser_terminal: 0%

**Implication**: kanata is an outlier. Voluntary review culture ≠ branch-protection enforcement — but it does change the Q1 advisory color (kanata Q1 = amber without override; all others Q1 = red without correction to amber).

---

## §6 · Shape / category coverage

Languages catalogued (post-V1.2):
- **Python**: Kronos (17), markitdown (15) — ML model + document-conversion library
- **Ruby**: kamal (18)
- **Go**: Xray-core (19), browser_terminal native host (20)
- **Zig**: ghostty (16)
- **Rust**: wezterm (21), kanata (23)
- **C#**: QuickLook (22)
- **Java**: freerouting (24)
- **C++**: WLED (25) — first C++ entry; ESP32 embedded firmware
- **JS/TS**: browser_terminal extension frontend (part of 20)

Category diversity:
- Terminal emulators: ghostty (Zig) + wezterm (Rust) — direct cross-shape comparator pair for V13-3
- Network / proxy: Xray-core
- Deploy orchestrator: kamal
- Browser extension: browser_terminal
- Windows shell integration: QuickLook
- Keyboard / input daemon: kanata
- ML foundation model: Kronos
- EDA / PCB autorouter: freerouting
- Document conversion: markitdown
- Embedded IoT firmware: WLED (new — first networked-device-on-home-LAN threat model)

---

## §7 · V13-3 progress

**V13-3 trigger**: 11 V1.2 wild scans (per CONSOLIDATION §8 deferred ledger).

**Status**: **10 of 11** complete (entries 16–25). **1 more wild scan** will trigger the 11-scan comparator-calibration analysis.

V13-3 analysis scope (from CONSOLIDATION §8): compare all V1.2 scan outputs against equivalent-SHA V2.4 outputs where comparator exists (the Step G pinned entries 12–14), plus look for cross-shape calibration patterns now that the wild-scan sample is large enough to generalize from.

---

## §8 · V1.2.x backlog

Derived from patterns in this document:

| ID | Item | Evidence | Priority |
|---|---|---|---|
| V12x-5 | Deserialization auto-fire for Q4 (pattern-based compute signal) | 2/7 overrides; collapses Kronos Q4 + freerouting Q4 | **High** |
| V12x-6 | Multi-ecosystem manifest parsing (Maven/Gradle/Cargo/Gomod/Bundler/.NET) | 6/9 scans hit this coverage gap | **High** |
| V12x-7 | Install-doc URL TLD-deviation detection | 1/9 scans (browser_terminal), high severity when hit | **Medium** |
| V12x-8 | Distribution-channel detection for language-specific package managers | 7/9 scans surface fictitious or missing channels | **Medium** |
| V12x-9 | Dangerous-primitives regex tuning for Rust serde, bundled minified JS | False positives on 3/9 scans (wezterm, kanata, QuickLook) | Low |
| V12x-10 | Silent-fix pattern telemetry | 9/9 scans show 0 advisories — might merit a Q3 rubric adjustment in V1.3 | Informational |

Each V12x item is additive per board Item F (signal additions are V1.2.x, signal removals are V1.3).

---

## §9 · V13-1 follow-up observations

The V13-1 split (`missing_qualitative_context` → `signal_vocabulary_gap` + `harness_coverage_gap`) has held up across 6 new scans (entries 19–24) with no ambiguous cases. The original `missing_qualitative_context` catchall hasn't fired post-V13-1 relabel. The two new labels account for 86% of overrides (6 of 7); `threshold_too_strict` covers the remaining 14% (Xray-core Q2).

**V13-1 escalation triggers (from CONSOLIDATION §8.1)**:
- ✅ No override has fit none of the 3 labels
- ✅ No override has fit multiple labels with genuine ambiguity
- ✅ No Skeptic has flagged the relabeling as inconsistent

→ **V13-1 taxonomy remains stable.** No board-review escalation needed.

---

## §10 · Changelog

- **2026-04-20** — Document created after 9 V1.2 wild scans. Consolidates observations from catalog entries 16–24 + the V13-1 analysis document.
- **2026-04-20 (entry 25 update)** — Added WLED (25) to roster. signal_vocabulary_gap now modal at 62% (5/8 overrides); 10/10 silent-fix pattern confirmed with a **publicly-documented disclosure-handling failure** (issue #5340 — GHSA-2xwq-cxqw-wfv8). New Priority 1b harness-patch: firmware default-no-auth + CORS-wildcard compound signal. Zero-override streak broken continues (freerouting 24 + WLED 25 both fire signal_vocabulary_gap). V13-3 progress: 10 of 11.
