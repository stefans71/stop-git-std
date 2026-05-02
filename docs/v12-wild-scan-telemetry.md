# V1.2 Wild-Scan Telemetry — Cross-Scan Analysis

**Last updated:** 2026-05-02T08:29:27Z

**Scope:** Catalog entries 16–28 (13 V1.2-schema wild scans).
**Date:** 2026-05-02 (entry 28 added in session 13; cross-scan tables below not yet re-derived for n=13 — they reflect the n=11 V13-3 trigger window. Entry-27 + entry-28 deltas are captured in §10 Changelog until the n=13 re-derivation lands; see `docs/back-to-basics-plan.md` §Current state follow-up backlog item #6).
**Status:** Living document — **V13-3 COMPARATOR-CALIBRATION TRIGGER FIRED at n=11** (entry 26 Baileys closed the counting window; the follow-up analysis is owed per CONSOLIDATION §8 deferred ledger). Re-trigger threshold for V13-3 follow-up is broadened cadence: N=25 V1.2 scans OR any of 6 taxonomy-strain events (currently 13/25; two taxonomy-strain candidates fire — entry 27 (first `missing_qualitative_context` use) and entry 28 (second consecutive `missing_qualitative_context` use, reinforcing the sample-floor degeneracy / closed-within-window-counter-signal pattern).
**Related:** [V13-1 override-telemetry analysis](v13-1-override-telemetry-analysis.md) (covered the first 3 scans and drove the V1.2.x signal widening).

This document persists cross-scan patterns that accumulate value over many scans and would otherwise be scattered across per-scan catalog rows and commit messages.

---

## §1 · Scan roster (entries 16–28)

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
| 26 | WhiskeySockets/Baileys | Reverse-engineered WhatsApp Web lib | Critical | 1 | Q4 signal_vocabulary_gap (reverse-engineered-API-library ToS risk) |
| 27 | mattpocock/skills | Claude Code skills/plugin | Caution | 1 | Q2 **missing_qualitative_context** (first use of this enum value at any n; sample-floor at 1 lifetime merged PR) |
| 28 | multica-ai/multica (re-scan) | Agentic platform (TS+Go monorepo) | Caution (split) | 1 | Q2 **missing_qualitative_context** (second consecutive use; closed-within-window counter-signal — 5 security issues fixed in past 8 days roughly matches arrival rate) |

**Totals (n=13)**: 13 scans, 11 overrides, 3 zero-override. **V13-3 comparator-calibration trigger originally fired at n=11**; re-trigger threshold N=25 OR any of 6 taxonomy-strain events. **Entries 27 + 28 are taxonomy-strain candidates**: two consecutive `missing_qualitative_context` fires across n=13 V1.2 wild scans (was × 0 at n=11) — the V13-3 §2 inference that "the V13-1 split was correct and complete" was n=11-bounded; n=13 confirms `missing_qualitative_context` is a stable enum value, not a relabel artifact, and reinforces the case that the underlying pattern (sample-floor degeneracy on skills + closed-within-window counter-signal on multica) deserves attention as either compute-signal expansion or sub-enum splitting (`sample_floor_degeneracy` and `responsive_close_rate_invisible_to_open_count`).

---

## §2 · Override-enum distribution

**9 overrides across 11 scans (82% override-rate at scan level).**

| `override_reason` | Count | % | Scans |
|---|---|---|---|
| `signal_vocabulary_gap` | **6** | **67%** | ghostty Q1, kamal Q1, Kronos Q2, freerouting Q4, WLED Q4, **Baileys Q4** |
| `harness_coverage_gap` | 2 | 22% | Kronos Q4, browser_terminal Q4 |
| `threshold_too_strict` | 1 | 11% | Xray-core Q2 |
| `missing_qualitative_context` | 0 | 0% | — |
| `threshold_too_lenient` | 0 | 0% | — |
| `rubric_literal_vs_intent` | 0 | 0% | — |
| `other` | 0 | 0% | — |

**Observations (n=11):**

- **`signal_vocabulary_gap` is strongly modal** at 67% of overrides (trend: 57% → 62% → 67% across n=9, 10, 11). Every Q4 override since wezterm (entry 21, zero) has fired signal_vocabulary_gap — 4 consecutive scans where Phase 4's default-path-critical judgment lives in a compute-signal category that compute doesn't derive from harness facts.
- **4 of 7 enum values unexercised** after 11 scans. `missing_qualitative_context` (the pre-V13-1 catchall) hasn't fired once since V13-1 relabeled existing entries — stronger signal at n=11 that the V13-1 split was correct and complete. `threshold_too_lenient`, `rubric_literal_vs_intent`, and `other` remain unused — candidates for V1.3 enum pruning consideration.
- **Override fires on Q1, Q2, Q4 but not Q3** across all 11 scans. Q3 (disclosure) has been uniformly red/amber from compute and Phase 4 has never corrected it — even in cases with concrete documented disclosure-handling failures (WLED entry 25, Baileys entry 26). This is a consistent data point worth naming: the current Q3 rubric is sensitive enough to read the silent-fix pattern correctly without Phase 4 intervention.
- **Q4 has become the override hotspot.** 6 of 9 overrides are Q4 (67%). Q1 fires 2, Q2 fires 2, Q3 fires 0. Q4's `q4_has_critical_on_default_path` is a Phase-4-authored bool by driver convention — the concept is right but the signal shape is wrong. Every shape requires a different concrete derivation (pickle hit count for ML, ObjectInputStream for Java, CORS+no-auth for IoT firmware, README-disclaimer+platform-API for reverse-engineered libraries). V1.2.x Priority 1–1b harness-patch candidates address the first three; Baileys adds a fourth compound-signal class.

---

## §3 · Zero-override streak

**3 consecutive zero-override scans**: wezterm (21) → QuickLook (22) → kanata (23). Streak broken by freerouting (24), continued-broken by WLED (25), continued-broken by Baileys (26). **Current streak of OVERRIDES: 3** (scans 24, 25, 26 all fire Q4 signal_vocabulary_gap).

What the zero-override scans had in common:
- **wezterm**: Rust terminal emulator, stalled 807-day release cadence, pure-tool threat model
- **QuickLook**: C# shell extender, 21-plugin parser surface but no new confirmed RCE
- **kanata**: Rust keyboard daemon, 44% formal review (exceptional), ruleset-but-anti-destruction

**What freerouting (24) added that broke the streak**: a **confirmed, specific, file-reachable RCE class** (Java ObjectInputStream on user-loaded files) that's invisible to `q4_has_critical_on_default_path` (which is set by Phase 4 authoring, not read from `dangerous_primitives.deserialization.hit_count`).

**What WLED (25) added (2nd break)**: a **confirmed, specific, remote-exploitable surface** (factory-default webserver has no auth + CORS wildcard + unauthenticated `/reset`) that's invisible to compute because the pattern lives in C++ control-flow (correctPIN gating logic tied to settingsPIN string length), not in a grep-able primitive family. `dangerous_primitives.tls_cors` DID surface the `Access-Control-Allow-Origin: *` hit, but there's no compute derivation that combines `tls_cors_hit + no_auth_primitive_detected + firmware_shape → q4_has_critical_on_default_path=True`.

**What Baileys (26) added (3rd break)**: a **category-level ToS-violation risk** that's invisible to compute because the threat lives in WhatsApp's terms-of-service enforcement, not in the library's code. The README's own CAUTION-flagged disclaimer is a strong signal ('not affiliated with WhatsApp… do not condone practices that violate the Terms of Service') but no grep-able primitive captures 'reverse-engineered platform-API library'. This is a distinct pattern from freerouting + WLED — those had grep-able facts that compute couldn't roll up; Baileys has prose-only facts (README disclaimer + topic list `reverse-engineering`) that compute doesn't consider.

**Inference (refined at n=11)**: zero-override scans remain possible when compute-signal judgment aligns with Phase 4 judgment; the break happens every time Phase 4 finds a specific critical-on-default-path condition whose identification requires one of: (a) language-semantic analysis beyond regex (freerouting); (b) multi-primitive composition + shape context (WLED); (c) README/metadata-level disclaimer parsing + topic-based shape classification (Baileys). All three are V12x-class harness-patch candidates but live in different harness layers — (a) in Step A regex, (b) in compute signal derivation, (c) in Step 7.5 README parsing + Step 1a topic analysis.

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

### Priority 1c: Reverse-engineered-platform-API shape signal for Q4

**New class observed on Baileys (26)**: README disclaimers acknowledging third-party-client status AND install path terminating at a named platform operator's API (WhatsApp, Discord, Instagram, etc.) AND GitHub topic list containing `reverse-engineering` or `reverse-engineered` → default-path critical (ToS-violation + account-ban risk).

**Scans it would auto-resolve**: Baileys Q4. The shape is distinctive enough that other reverse-engineered-API libraries (whatsmeow in Go, discord.py-self, instagrapi, etc.) would also match.

**Signal-widening proposal**: compute derives `q4_has_critical_on_default_path = True` when README (Step 7.5 output) contains disclaimer phrases matching `(not affiliated|not endorsed|not authorized|reverse.?engineered|unofficial.*client)` AND topic list contains `reverse-engineering` OR the library name references a named platform (whatsapp, discord, instagram, telegram-client, facebook-messenger). This sits in the harness's Step 7.5 README paste-scan extension + Step 1a topic-field read; both already produce the raw data. The missing piece is the compound rule in compute that reads them.

**Open question**: whether 'official third-party clients' (e.g., libraries with vendor partnerships) should be excluded. A possible safeguard: require the disclaimer AND the absence of an `authorized_by` metadata signal — though that's likely out-of-scope for a regex/compute-based approach. V1.3 candidate if the false-positive rate is high; V1.2.x candidate if the shape is rare enough that disclaimer+topic is a strong-enough signal in isolation.

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

**11 of 11 V1.2 wild scans have 0 published GHSA advisories** despite histories ranging from 10 months (Kronos) to 12 years (freerouting) on privileged tools:

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
| Baileys (26) | 4 | 0 | Reverse-engineered WhatsApp Web client |

**Pattern (n=11)**: even active, widely-used privileged tools uniformly skip GHSA publication. Readings are (a) no security-relevant issues discovered (implausible for this sample), (b) silent-fix-via-release cadence, (c) disclosure stops at maintainer.

**11-for-11 is significant**. At n=9, 10 readings (a), (b), (c) were plausible individually. At n=11 with the documented failure modes on WLED (25) + Baileys (26), reading (c) dominates: disclosure cycles don't reach GHSA publication. The specific mechanisms differ — WLED had a permissions misconfiguration on the private advisory UI; Baileys had a community-submitted vulnerability-fix PR (#1996) stale-closed after 148 days with the maintainer's promised 'own version' never materializing — but both show the same end state (no GHSA published for the identified issue).

**WLED + Baileys documented disclosure-handling failures** are two distinct instances of reading (c) at concrete level: when a researcher identifies a real vulnerability class and attempts to route it through the documented or undocumented channels, the process halts before GHSA publication. This is not the same as 'fix silently via next release' — in both cases, the fix itself did NOT land (WLED 0.15.x backport unconfirmed, Baileys `request` still in master).

**Implication for V1.3**: the `community_norms_differ` enum value that DeepSeek preserved as a V1.3 expansion trigger (CONSOLIDATION §5 R3 Item C) hasn't fired — but the silent-fix pattern is now 11/11, documented enough that it IS the community norm for this catalog's shape. Both WLED and Baileys Phase 4 had strong cases for Q3 override (from amber to red) and in both cases Phase 4 declined — the current amber/'partly' framing is considered adequate. V13-3 analysis should consider whether the Q3 rubric language should mention this pattern explicitly.

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
- **TypeScript / JavaScript**: Baileys (26) — first TS entry as primary language; reverse-engineered API library. Also browser_terminal extension frontend (part of 20).

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
- Reverse-engineered platform-API library: Baileys (new — first ToS-violation-category threat model; category contains whatsmeow, discord.py-self, etc.)

---

## §7 · V13-3 progress

**V13-3 trigger**: 11 V1.2 wild scans (per CONSOLIDATION §8 deferred ledger).

**Status**: **11 of 11 — TRIGGER FIRED.** All 11 V1.2 wild scans complete (entries 16–26). The comparator-calibration analysis is now owed per CONSOLIDATION §8.

**V13-3 analysis scope** (from CONSOLIDATION §8 + this telemetry doc): compare all 11 V1.2 scan outputs against equivalent-SHA V2.4 outputs where comparator exists (the Step G pinned entries 12–14); look for cross-shape calibration patterns now that the wild-scan sample has expanded to 11 entries covering 10 language ecosystems (Zig, Python, Ruby, Go, JS/TS, Rust × 2, C#, Java, C++ firmware) across 11 distinct shape categories; evaluate the override-enum distribution (6 signal_vocabulary_gap / 2 harness_coverage_gap / 1 threshold_too_strict / 0 of the other 4 enum values) for V1.3 pruning candidates; codify the V1.2.x harness-patch candidates (§4 Priority 1/1b/1c) that would collapse most of the Q4 overrides.

V13-3 analysis scope (from CONSOLIDATION §8): compare all V1.2 scan outputs against equivalent-SHA V2.4 outputs where comparator exists (the Step G pinned entries 12–14), plus look for cross-shape calibration patterns now that the wild-scan sample is large enough to generalize from.

---

## §8 · V1.2.x backlog

Derived from patterns in this document:

| ID | Item | Evidence | Priority |
|---|---|---|---|
| V12x-5 | Deserialization auto-fire for Q4 (pattern-based compute signal) | 2/9 overrides; collapses Kronos Q4 + freerouting Q4 | **High** |
| V12x-6 | Multi-ecosystem manifest parsing (Maven/Gradle/Cargo/Gomod/Bundler/.NET) | 7/11 scans hit this coverage gap | **High** |
| V12x-7 | Install-doc URL TLD-deviation detection | 1/11 scans (browser_terminal), high severity when hit | **Medium** |
| V12x-8 | Distribution-channel detection for language-specific package managers | 8/11 scans surface fictitious or missing channels | **Medium** |
| V12x-9 | Dangerous-primitives regex tuning — language qualifier on deserialization family | False positives on 4/11 scans (wezterm, kanata, QuickLook, **WLED** — ArduinoJson) | **Medium** (promoted from Low: 4 FP cases + Priority 1 requires this fix) |
| V12x-10 | Silent-fix pattern telemetry | **11/11** scans show 0 advisories — strong case for Q3 rubric adjustment in V1.3 | Informational → **V1.3 candidate** |
| V12x-11 | Firmware-default-no-auth + CORS-wildcard compound Q4 signal | 1/11 scans (WLED) — Priority 1b | **Medium** |
| V12x-12 | Reverse-engineered-API-library shape Q4 signal (README disclaimer + topic + platform-name) | 1/11 scans (Baileys) — Priority 1c | **Medium** |
| V12x-13 | vendor_keys proximity-context requirement | 1/11 scans (Baileys — `AIza` in WhatsApp protocol dictionary FP) | Low |
| V12x-14 | PR-sampler robustness when closed-without-merge dominates stream | 1/11 scans (Baileys — 0 sample despite 352 lifetime merges) | Low |

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
- **2026-04-20 (entry 26 update — V13-3 TRIGGER FIRED)** — Added Baileys (26) to roster. **11 V1.2 wild scans complete.** signal_vocabulary_gap now strongly modal at 67% (6/9 overrides — 3 consecutive Q4 overrides since wezterm streak ended). **11/11 silent-fix pattern** with Baileys adding a second distinct documented failure mode (PR #1996 stale-closed after 148 days, maintainer-promised replacement never materialized). New Priority 1c harness-patch: reverse-engineered-platform-API-library shape signal (README disclaimer phrase detection + topic analysis + platform-name matching). Q4 has become the override hotspot (6 of 9 overrides). V13-3 comparator-calibration analysis is now owed — see §7. TypeScript added as first-class catalog language. Three new V12x backlog items (V12x-11/12/13) derived from Baileys observations; V12x-9 promoted from Low to Medium (4 FP cases now).
- **2026-04-20 (V13-3 CLOSE)** — 042026-v13-3-comparator-calibration board review closed with 2/3 R3 AGREE + owner directive OD-4 (Codex R3 unavailable, R2 positions consistent with all R3 resolutions; Codex assigned code-review gate on staged V1.2.x implementation diff). **V1.2.x landed:** C2 (language-qualifier regex — drops bare `deserialize` keyword; suppresses ArduinoJson FP class), C5 (Q4 auto-fire from unsafe-deserialization hits + tool-loads-user-files condition), C18 (`derive_tool_loads_user_files()` canonical helper), C20 (dry-run FP test at `docs/v13-3-fp-dry-run.md` — 0 FPs on 11 bundles). **V1.3 deferred:** C6 (firmware CORS compound signal), C7 (reverse-eng shape signal with REJECT fallback), C9 (prune `missing_qualitative_context` with historical-hold), C17 (multi-ecosystem manifest parsing), V13-4 (`community_norms_differ` enum addition at N=15 or first Q3 override fire). **Frozen analysis:** `docs/v13-3-analysis.md`. **Follow-up cadence:** G4-broadened — N=25 OR any of 6 taxonomy-strain events. Full CONSOLIDATION at `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/CONSOLIDATION.md`.
- **2026-04-30 (entry 27 update — session 8 first wild scan)** — Added mattpocock/skills (27) to roster. **First Claude Code skills/plugin shape** in V1.2 catalog (47.9k stars, 3 months old, 22 SKILL.md / 1,815 lines, MIT). Q2 override fires `missing_qualitative_context` — **first use of this enum value across all 12 V1.2 wild scans** (was × 0 at n=11). Override rationale: at sample-floor evidence (1 lifetime merged PR + 0 closed-merged security PRs), Phase 3 advisory's GREEN ('Yes — they fix problems quickly') over-claims; honest answer is amber/insufficient-data. Suggested threshold adjustment authored: add `total_merged_lifetime < N` (e.g., 5) sample-floor signal that returns amber rather than green when no closed-fix-lag data exists. **§9 V13-1 inference no longer holds at n=12** — the n=11-bounded claim "missing_qualitative_context catchall hasn't fired post-V13-1 relabel" has its first counterexample. The fire is consistent with V13-3 C9 (prune `missing_qualitative_context` with historical-hold) being premature — the value still has a live use case (sample-floor degeneracy) that doesn't reduce to `signal_vocabulary_gap` or `harness_coverage_gap`. New V12x backlog item (V12x-15) candidate: sample-floor signal for Q2 advisory function. **Taxonomy-strain event** by V13-3 C9-criteria — first use of an enum value previously argued for pruning is a re-evaluation event. V13-3 follow-up still 12/25 toward N=25 cadence; G4 taxonomy-strain count: 1 of 6.
- **2026-05-02 (entry 28 update — session 13, re-scan of multica)** — Added multica-ai/multica (28) to roster. **Re-scan of catalog entry 11** (V2.4 / delegated, 2026-04-19, HEAD `b8907dd`) — first re-scan of an existing V2.4 catalog entry through V2.5-preview pipeline at a later SHA (16 days later, HEAD `3df95c8`). 23.5k-star agentic platform — TS+Go monorepo (Next.js + Electron + Go server + Docker self-host via GHCR). **Verdict shift vs prior**: 888888 dev-verification-code Critical → Warning (APP_ENV=production gate landed ~2026-04-18, closed issue #1304 in window between scans); two new Warnings surfaced (install.sh checksum gap on Unix vs install.ps1 SHA256-verify on Windows; ruleset declared but `enforcement: disabled`); one new privesc Warning (#1114 LD_PRELOAD/NODE_OPTIONS bypass on agent custom_env, open since prior scan). **Q2 override fires `missing_qualitative_context` — second consecutive use** (after skills entry 27); pattern now n=2/13 = 15% of V1.2 wild scans land here. Override rationale: 5 security issues closed in past 8 days (888888 #1304, shell.openExternal #1115, Hermes filterCustomArgs #1113, /health/realtime #1606, open-redirect #1116) — the close-side cadence roughly matches the arrival rate (4 still open, oldest 16 days). Phase 3 advisory's RED is read off open-side count alone; the responsiveness counter-signal is invisible to compute. **Taxonomy-strain reinforcement**: two consecutive fires of an enum value previously argued for pruning solidifies the case that `missing_qualitative_context` covers a real phenomenon class — but the two fires have DIFFERENT underlying drivers (skills = sample-floor degeneracy; multica = closed-within-window counter-signal). Either justify keeping the catchall enum as-is, or split into two more-specific enum values. New V12x backlog item (V12x-16) candidate: weight `closed_within_window` as a Q2 advisory counter-signal. **Shape misclassification noted**: classify_shape() picked `library-package` (publishable npm manifest matched first) when multica's structural shape is `agentic-platform` (server + CLI + web + desktop) — diagnosis owed for next session. V13-3 follow-up at 13/25 toward N=25 cadence; G4 taxonomy-strain count: 2 of 6.
