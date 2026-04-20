# V1.2 Wild-Scan Telemetry — Cross-Scan Analysis

**Scope:** Catalog entries 16–24 (9 V1.2-schema wild scans).
**Date:** 2026-04-20.
**Status:** Living document — update after each new V1.2 wild scan.
**Related:** [V13-1 override-telemetry analysis](v13-1-override-telemetry-analysis.md) (covered the first 3 scans and drove the V1.2.x signal widening).

This document persists cross-scan patterns that accumulate value over many scans and would otherwise be scattered across per-scan catalog rows and commit messages.

---

## §1 · Scan roster (entries 16–24)

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

**Totals**: 9 scans, 7 overrides, 3 zero-override.

---

## §2 · Override-enum distribution

**7 overrides across 9 scans (78% override-rate at scan level).**

| `override_reason` | Count | % | Scans |
|---|---|---|---|
| `signal_vocabulary_gap` | **4** | **57%** | ghostty Q1, kamal Q1, Kronos Q2, freerouting Q4 |
| `harness_coverage_gap` | 2 | 29% | Kronos Q4, browser_terminal Q4 |
| `threshold_too_strict` | 1 | 14% | Xray-core Q2 |
| `missing_qualitative_context` | 0 | 0% | — |
| `threshold_too_lenient` | 0 | 0% | — |
| `rubric_literal_vs_intent` | 0 | 0% | — |
| `other` | 0 | 0% | — |

**Observations:**

- **`signal_vocabulary_gap` is the modal label** at 57% of overrides. This matches the V13-1 analysis hypothesis that the majority of Phase 4 corrections are compute-side (the signal-vocabulary exists in principle but doesn't cover the needed concept).
- **4 of 7 enum values unexercised** after 9 scans. `missing_qualitative_context` (the pre-V13-1 catchall) hasn't fired once since V13-1 relabeled existing entries — strong signal that the V13-1 split was correct.
- **Override fires on Q1, Q2, Q4 but not Q3** across the 9 scans. Q3 (disclosure) has been uniformly red/amber from compute and Phase 4 hasn't needed to correct it.

---

## §3 · Zero-override streak

**3 consecutive zero-override scans**: wezterm (21) → QuickLook (22) → kanata (23). Streak broken by freerouting (24).

What these shapes had in common:
- **wezterm**: Rust terminal emulator, stalled 807-day release cadence, pure-tool threat model
- **QuickLook**: C# shell extender, 21-plugin parser surface but no new confirmed RCE
- **kanata**: Rust keyboard daemon, 44% formal review (exceptional), ruleset-but-anti-destruction

**What freerouting added that broke the streak**: a **confirmed, specific, file-reachable RCE class** (Java ObjectInputStream on user-loaded files) that's invisible to `q4_has_critical_on_default_path` (which is set by Phase 4 authoring, not read from `dangerous_primitives.deserialization.hit_count`).

**Inference**: zero-override scans are possible when compute-signal judgment aligns with Phase 4 judgment; the break happens when Phase 4 finds a specific critical-on-default-path condition that compute-signal inputs don't automatically surface.

---

## §4 · Harness-patch candidates (ordered by impact × frequency)

### Priority 1: Deserialization auto-fire for Q4

**Signal added**: compute derives `q4_has_critical_on_default_path = True` when `dangerous_primitives.deserialization.hit_count >= N` AND the tool is documented as loading user files.

**Scans it would auto-resolve**: Kronos Q4 (pickle.load in finetune/dataset.py), **freerouting Q4** (Java ObjectInputStream in BasicBoard.java). Two of the seven overrides collapse with this single change.

**Open question**: threshold N. Kronos had 0 harness hits (regex miss — now fixed in V1.2.x); freerouting had 35. After the V1.2.x pickle-regex extension, Kronos would hit. A reasonable threshold is `>= 3` plus README-pattern-match for "open file"/"load"/"import" keywords.

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

**9 of 9 V1.2 wild scans have 0 published GHSA advisories** despite histories ranging from 3 years (kanata) to 12 years (freerouting) on privileged tools:

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

**Pattern**: even active, widely-used privileged tools uniformly skip GHSA publication. Readings are (a) no security-relevant issues discovered (implausible for this sample), (b) silent-fix-via-release cadence, (c) disclosure stops at maintainer.

**Implication for V1.3**: the `community_norms_differ` enum value that DeepSeek preserved as a V1.3 expansion trigger (CONSOLIDATION §5 R3 Item C) hasn't fired — but the silent-fix pattern is NOW the documented community norm for this catalog's shape. Worth revisiting whether Q3's red/amber rubric should adjust.

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

---

## §7 · V13-3 progress

**V13-3 trigger**: 11 V1.2 wild scans (per CONSOLIDATION §8 deferred ledger).

**Status**: **9 of 11** complete (entries 16–24). **2 more wild scans** will trigger the 11-scan comparator-calibration analysis.

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
