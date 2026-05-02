# V1.2 Wild-Scan Telemetry — Cross-Scan Analysis

**Last updated:** 2026-05-02T11:40:56Z

**Scope:** Catalog entries 16–28 (13 V1.2-schema wild scans).
**Date:** 2026-05-02 (cross-scan tables §2–§9 re-derived for n=13 in session 14, incorporating entry 27 skills + entry 28 multica overrides; numbers read directly from the 13 form.json bundles in `docs/scan-bundles/`).
**Status:** Living document — **V13-3 COMPARATOR-CALIBRATION TRIGGER FIRED at n=11** (entry 26 Baileys closed the counting window; CONSOLIDATION closed 2026-04-20 — see §10). Post-trigger cadence (broadened per OD-4): N=25 V1.2 scans OR any of 6 taxonomy-strain events. Currently **13/25** scans + **2/6** taxonomy-strain events (skills + multica `missing_qualitative_context` consecutive fires). The §9 V13-1 inference no longer holds at n=13 — see §9 for the contraindication of V13-3 deferred Item C9 and the two-path decision deferred to next trigger.
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

**Totals (n=13)**: 13 scans, 11 overrides, 3 zero-override (wezterm 21, QuickLook 22, kanata 23). **V13-3 comparator-calibration trigger fired at n=11; CONSOLIDATION closed 2026-04-20.** Post-trigger cadence: 13/25 toward N=25 OR 2/6 taxonomy-strain events. **Entries 27 + 28 are the two taxonomy-strain fires**: consecutive `missing_qualitative_context` overrides with distinct semantic drivers (skills = sample-floor degeneracy; multica = closed-within-window counter-signal). The n=11-bounded inference "the V13-1 split was correct and complete; the catchall hasn't fired" is broken at n=13 — see §9 for full revision and the contraindication of V13-3 deferred Item C9.

---

## §2 · Override-enum distribution

**11 overrides across 13 scans** (0.85 overrides/scan; 10 of 13 scans fired ≥1 override = 77% scan-level participation).

| `override_reason` | Count | % | Scans |
|---|---|---|---|
| `signal_vocabulary_gap` | **6** | **55%** | ghostty Q1, Kronos Q2, kamal Q1, freerouting Q4, WLED Q4, Baileys Q4 |
| `harness_coverage_gap` | 2 | 18% | Kronos Q4, browser_terminal Q4 |
| `missing_qualitative_context` | **2** | **18%** | **skills Q2 (entry 27), multica Q2 (entry 28)** — first uses since V13-1 relabel; both Q2; consecutive |
| `threshold_too_strict` | 1 | 9% | Xray-core Q2 |
| `threshold_too_lenient` | 0 | 0% | — |
| `rubric_literal_vs_intent` | 0 | 0% | — |
| `other` | 0 | 0% | — |

**Observations (n=13):**

- **`signal_vocabulary_gap` remains modal but no longer dominant** — 55% (was 67% at n=11; trend now 57% → 62% → 67% → 55% across n=9, 10, 11, 13). The 12-percentage-point drop is entirely explained by the two consecutive `missing_qualitative_context` fires (skills + multica) at n=12, 13. The underlying Q4 `signal_vocabulary_gap` problem (Phase 4's default-path-critical judgment lives in a compute-signal category that compute doesn't derive from harness facts) has not improved — it just has new company.
- **3 of 7 enum values unexercised** at n=13 (was 4 of 7 at n=11). `missing_qualitative_context` is now active with two distinct semantic drivers (sample-floor degeneracy on skills; responsive close-rate counter-signal on multica). The n=11-bounded inference "the V13-1 split was correct and complete; the catchall hasn't fired" no longer holds. `threshold_too_lenient`, `rubric_literal_vs_intent`, and `other` remain unused — V1.3 pruning candidates pending.
- **Override still never fires on Q3** across all 13 scans. Q3 (disclosure) has been uniformly red/amber from compute and Phase 4 has never corrected it — including the documented disclosure-handling failures on WLED (25), Baileys (26), and the silent-fix pattern across nearly all entries. The current Q3 rubric is sensitive enough to read the silent-fix pattern without Phase 4 intervention.
- **Q4 still leads but Q2 has caught up.** Q4 was 6/9=67% at n=11; now 5/11=45% at n=13. Q2 was 2/9=22% at n=11; now **4/11=36%** at n=13 — the surge is entirely the two `missing_qualitative_context` fires. Q1=2 (18%), Q3=0. Q2's growth means the override hotspot is no longer single-cell — both Q4 (compute can't derive default-path-critical from grep-able primitives alone) and Q2 (compute can't read responsiveness or sample-floor context from advisory rule-table outputs) need work.

---

## §3 · Zero-override streak

**3 consecutive zero-override scans (unchanged from n=11)**: wezterm (21) → QuickLook (22) → kanata (23). No new zero-override scans at n=12, 13. **Current streak of OVERRIDES: 5** (scans 24, 25, 26, 27, 28 all fire ≥1 override; entries 24-26 fire Q4 `signal_vocabulary_gap`, entries 27-28 fire Q2 `missing_qualitative_context`).

What the zero-override scans had in common:
- **wezterm**: Rust terminal emulator, stalled 807-day release cadence, pure-tool threat model
- **QuickLook**: C# shell extender, 21-plugin parser surface but no new confirmed RCE
- **kanata**: Rust keyboard daemon, 44% formal review (exceptional), ruleset-but-anti-destruction

**Five distinct break-conditions documented across the override streak** (was 3 at n=11):

- **freerouting (24) — language-semantic gap**: a **confirmed, specific, file-reachable RCE class** (Java ObjectInputStream on user-loaded files) that's invisible to `q4_has_critical_on_default_path` (which is set by Phase 4 authoring, not read from `dangerous_primitives.deserialization.hit_count`).
- **WLED (25) — multi-primitive composition + shape context gap**: a **confirmed, specific, remote-exploitable surface** (factory-default webserver has no auth + CORS wildcard + unauthenticated `/reset`) that's invisible to compute because the pattern lives in C++ control-flow (correctPIN gating logic tied to settingsPIN string length), not in a grep-able primitive family. `dangerous_primitives.tls_cors` DID surface the `Access-Control-Allow-Origin: *` hit, but there's no compute derivation that combines `tls_cors_hit + no_auth_primitive_detected + firmware_shape → q4_has_critical_on_default_path=True`.
- **Baileys (26) — README/metadata-level + topic-based shape gap**: a **category-level ToS-violation risk** that's invisible to compute because the threat lives in WhatsApp's terms-of-service enforcement, not in the library's code. The README's own CAUTION-flagged disclaimer ("not affiliated with WhatsApp… do not condone practices that violate the Terms of Service") is a strong signal but no grep-able primitive captures "reverse-engineered platform-API library."
- **skills (27) — sample-floor degeneracy**: at sample-floor evidence (1 lifetime merged PR + 0 closed-merged security PRs) the calibration v2 advisory's GREEN ("Yes — they fix problems quickly") over-claims; honest answer is amber/insufficient-data. The rule reads "low or zero closed-fix-lag = good"; reality is "no data ≠ good." Phase 4 corrected to amber via `missing_qualitative_context` — first use of the enum value at any n.
- **multica (28) — closed-within-window counter-signal**: 5 security issues closed in past 8 days (responsive) sit alongside 4 still open (oldest 16 days). The advisory rule reads only the open-side count and lands red; close-side responsiveness is invisible. The close cadence roughly matches the arrival rate, so on a moving-average view this maintainer IS responsive — Phase 4 corrected to amber.

**Inference (refined at n=13)**: zero-override scans remain possible when compute-signal judgment aligns with Phase 4 judgment; the break happens every time Phase 4 finds a condition that requires one of: (a) language-semantic analysis beyond regex (freerouting); (b) multi-primitive composition + shape context (WLED); (c) README/metadata-level disclaimer parsing + topic-based shape classification (Baileys); **(d) sample-floor handling on Q2 — refusing green when total-merged-lifetime is below threshold (skills)**; **(e) close-rate counter-signal on Q2 — weighting closed-within-window against open count (multica)**. All five are V12x-class harness-or-compute-patch candidates living in different layers — (a)+(b) in Step A regex / compute signal derivation; (c) in Step 7.5 README parsing + Step 1a topic analysis; (d)+(e) in `compute.evaluate_q2()` rule-table refinement. Notably, (d) and (e) are the first non-Q4 break-conditions documented in this catalog.

---

## §4 · Harness-patch candidates (ordered by impact × frequency)

### Priority 1: Deserialization auto-fire for Q4

**Signal added**: compute derives `q4_has_critical_on_default_path = True` when `dangerous_primitives.deserialization.hit_count >= N` AND the tool is documented as loading user files.

**Scans it would auto-resolve**: Kronos Q4 (pickle.load in finetune/dataset.py), **freerouting Q4** (Java ObjectInputStream in BasicBoard.java). 2 of 11 overrides collapse with this single change.

**Open question**: threshold N. Kronos had 0 harness hits (regex miss — now fixed in V1.2.x); freerouting had 35. After the V1.2.x pickle-regex extension, Kronos would hit. A reasonable threshold is `>= 3` plus README-pattern-match for "open file"/"load"/"import" keywords.

**Subtlety from WLED (25)**: the V1.2.x-widened deserialization regex produced 19 **false-positive** hits in WLED's C++ codebase — all `deserializeJson` calls (ArduinoJson, safe). Any auto-fire threshold on raw deserialization hit-count will mis-fire on C/C++/Rust projects using JSON libraries with `deserialize` in the function name. The auto-fire derivation needs a **language qualifier** (pickle→Python, ObjectInputStream→Java, Marshal.load→Ruby) rather than a language-agnostic regex. V12x-9 item now promoted to the Priority 1 scope.

### Priority 1b: Firmware default-no-auth + CORS-wildcard compound signal for Q4

**New class observed on WLED (25)**: the combination of (a) `dangerous_primitives.tls_cors` hit on `Access-Control-Allow-Origin: *` + (b) no auth-enforcement primitive detected on a web-server-shipping tool + (c) install-path terminus being a networked end-user device (firmware, IoT, home-LAN server) = critical-on-default-path.

**Scans it would auto-resolve**: WLED Q4. 1 of 11 overrides.

**Signal-widening proposal**: compute derives `q4_has_critical_on_default_path = True` when `tls_cors.hit_count >= 1` (wildcard Origin/Methods/Headers pattern) AND `auth_bypass.hit_count == 0` (no auth-gate pattern detected) AND shape is `firmware | iot | on-device-webserver`. Shape classification would be a new compute-side input — bootstrappable from README keywords (ESP32, ESP8266, firmware, on-device, LAN webserver) + install-path signals (.bin releases, browser-WebSerial flasher).

### Priority 1c: Reverse-engineered-platform-API shape signal for Q4

**New class observed on Baileys (26)**: README disclaimers acknowledging third-party-client status AND install path terminating at a named platform operator's API (WhatsApp, Discord, Instagram, etc.) AND GitHub topic list containing `reverse-engineering` or `reverse-engineered` → default-path critical (ToS-violation + account-ban risk).

**Scans it would auto-resolve**: Baileys Q4. 1 of 11 overrides. The shape is distinctive enough that other reverse-engineered-API libraries (whatsmeow in Go, discord.py-self, instagrapi, etc.) would also match.

**Signal-widening proposal**: compute derives `q4_has_critical_on_default_path = True` when README (Step 7.5 output) contains disclaimer phrases matching `(not affiliated|not endorsed|not authorized|reverse.?engineered|unofficial.*client)` AND topic list contains `reverse-engineering` OR the library name references a named platform (whatsapp, discord, instagram, telegram-client, facebook-messenger). This sits in the harness's Step 7.5 README paste-scan extension + Step 1a topic-field read; both already produce the raw data. The missing piece is the compound rule in compute that reads them.

**Open question**: whether 'official third-party clients' (e.g., libraries with vendor partnerships) should be excluded. A possible safeguard: require the disclaimer AND the absence of an `authorized_by` metadata signal — though that's likely out-of-scope for a regex/compute-based approach. V1.3 candidate if the false-positive rate is high; V1.2.x candidate if the shape is rare enough that disclaimer+topic is a strong-enough signal in isolation.

### Priority 1d: Sample-floor signal for Q2 advisory function

**New class observed on skills (27)**: at sample-floor evidence (1 lifetime merged PR; 0 closed-merged security PRs) the calibration v2 Q2 advisory rule's GREEN ("Yes — they fix problems quickly") over-claims. The rule reads "low or zero closed-fix-lag = good"; reality is "no data ≠ good." Phase 4 corrected to amber via `missing_qualitative_context` — first use of that enum value at any n.

**Scans it would auto-resolve**: skills Q2. 1 of 11 overrides.

**Signal-widening proposal**: extend `compute.evaluate_q2()` to test `pr_review.total_merged_lifetime < N` (suggested N=5) AND `pr_review.security_flagged_count == 0`. When both true, return amber not green, with `matched_rule` text "sample-floor: insufficient closed-fix-lag data to claim responsiveness." This sits entirely in compute (no new harness data needed). First-class candidate for V1.2.x because no false-positive class is plausible (the rule fires only when both numerators are at floor).

### Priority 1e: Responsive close-rate counter-signal for Q2

**New class observed on multica (28)**: 5 security issues closed in past 8 days (responsive) sit alongside 4 still open (oldest 16 days). The advisory rule reads only the open-side count and lands red; close-side responsiveness is invisible. The close cadence roughly matches the arrival rate, so on a moving-average view this maintainer IS responsive — Phase 4 corrected to amber via `missing_qualitative_context` (second consecutive use of that enum value).

**Scans it would auto-resolve**: multica Q2. 1 of 11 overrides.

**Signal-widening proposal**: extend `compute.evaluate_q2()` to compute `closed_within_window = count(security_issues closed in past 30d)` from the existing harness `issues_and_commits.closed_issues` field (no new collection needed). When `closed_within_window >= open_security_issue_count` AND `closed_within_window >= 3`, return amber instead of red, with `matched_rule` text "responsive close-rate: close-cadence matches arrival rate." Open question: whether to inspect issue *bodies* for security-keyword matches (not just titles) — defer until first false positive observed.

### Priority 2: Multi-ecosystem Maven/Gradle/Cargo/Gomod parsing

**Gap observed across 9 of 13 scans**:
- Go gomod: Xray-core (19), browser_terminal (20) host, multica (28) backend
- Ruby Gemfile.lock: kamal (18)
- Rust Cargo.lock: wezterm (21), kanata (23)
- .NET .csproj / .sln: QuickLook (22)
- Java build.gradle: freerouting (24)
- TypeScript/Bun monorepo: multica (28) frontend (npm parse works but workspace structure surfaces fictitious sub-channels)

Each dumps `runtime_count=0` and `osv total_vulns=0` despite real dep graphs. Scanner workaround each time is Phase 4 annotation. **Single consolidated patch** implementing parser + OSV-query for all 5 ecosystems would close a family of F5/F6-class findings and enable real dep-CVE telemetry.

### Priority 3: Install-doc URL TLD-deviation detection

**Scans affected**: browser_terminal (F0 typosquat URL `chrome.google.cm` in installation.md). 1 of 13 scans.

**Proposed check**: README / install-doc URL parse; flag links whose host matches a known-good domain prefix (e.g., `chrome.google`, `addons.mozilla.org`, `pypi.org`, `rubygems.org`) but with a non-matching TLD or subdomain.

**Impact**: Would have surfaced the browser_terminal Critical without Phase 4 override. Rare-but-high-impact class of finding.

### Priority 4: Distribution-channel detection for language-specific package managers

**Gap observed across 9 of 13 scans**: real distribution channels are frequently not detected:
- GitHub Releases binaries: wezterm, kanata, freerouting, Xray-core
- Homebrew formulas: ghostty, wezterm, kamal, multica
- `gem install` + RubyGems.org: kamal
- `cargo install kanata` + crates.io: kanata (works for single top-level crate, surfaces workspace members as fictitious channels)
- Chrome Web Store + Firefox Add-ons: browser_terminal
- MSI + Scoop + MS Store: QuickLook
- Docker images on ghcr.io: freerouting, multica
- npx / npm / curl-pipe: multica (mixed) + skills (npx-installable plugin marketplace)

**Fix**: introduce channel-detector modules per ecosystem; confirm via live registry lookups (`npm view`, `gem info`, `cargo search`) rather than package-manifest presence alone.

---

## §5 · Cross-shape patterns

### 5.1 · C20 calibration

**C20 rule fires Critical when**: `no_classic AND no_rulesets AND no_rules_on_default AND no_codeowners AND ships_executable_code AND has_recent_release_30d`.

Firing pattern observed (n=13, current bundle data — supersedes the n=11 table which mis-recorded C20 result for ghostty/kamal/freerouting/WLED):

| Scan | Recent release? | C20 result | Verdict |
|---|---|---|---|
| Xray-core (19) | Yes (2d) | **Critical** | Critical |
| kanata (23) | Yes (7d) | **Critical** | Critical |
| Kronos (17) | No releases | Warning | Critical (via F0 pickle RCE) |
| browser_terminal (20) | No (301d) | Warning | Critical (via F0 typosquat) |
| wezterm (21) | No (806d) | Warning | Caution |
| QuickLook (22) | No (499d) | Warning | Caution |
| Baileys (26) | No (150d) | Warning | Critical (via F0 ToS + #1996) |
| skills (27) | No releases | Warning | Caution |
| multica (28) | Yes (0d) | Warning | Caution (split) |
| ghostty (16) | No (1249d) | None | Caution |
| kamal (18) | No (32d) | None | Caution |
| freerouting (24) | No (373d) | None | Critical (via F0 deserialization) |
| WLED (25) | Yes (0d) | None | Critical (via F0 firmware-no-auth) |

**C20 still calibrates well in the directional sense** — both Critical fires (Xray-core, kanata) had active release cadence + governance gates absent. The Warning tier captures most stale-release-but-gates-absent cases. The None cases (ghostty, kamal, freerouting, WLED) all have at least one of: rulesets, rules-on-default, or CODEOWNERS — a partial-protection state where C20 doesn't fire.

**Caveat (unchanged from n=11)**: C20 doesn't catch the ACTUAL critical findings (F0 pickle RCE on Kronos, F0 typosquat on browser_terminal, F0 Java deserialization on freerouting, F0 firmware-no-auth on WLED, F0 ToS-violation on Baileys). Those reach Critical verdict via Phase 4 authoring, not via C20. C20 is one of several Critical pathways, not the main one.

**Note**: 4 of 13 scans (ghostty, kamal, freerouting, WLED) returned `c20_severity.result = null` because at least one governance gate is present (ruleset OR codeowners OR rules-on-default). The current rule treats *any* gate as enough to suppress C20 entirely, even when the present gate is non-load-bearing (e.g., a disabled ruleset). Consider in a future calibration whether `no_codeowners=False` alone should suppress C20 when no other protection exists.

### 5.2 · Silent-fix / zero-advisories consistency

**12 of 13 V1.2 wild scans have 0 published GHSA advisories** (correction: the n=11 table mis-recorded ghostty as 0 — current bundle shows 5 GHSA published since 2024-12-31). Histories range from 2 months (skills) to 12 years (freerouting):

| Scan | Years active | Advisories | Threat surface |
|---|---|---|---|
| ghostty (16) | 4.1 | **5** (2 medium / 3 low; oldest 2024-12-31) | Terminal emulator |
| Kronos (17) | 0.8 | 0 | ML model + Flask webui |
| kamal (18) | 3.3 | 0 | SSH + docker orchestrator |
| Xray-core (19) | 5.4 | 0 | Network proxy (privileged) |
| browser_terminal (20) | 3.0 | 0 | Browser extension + shell bridge |
| wezterm (21) | 8.2 | 0 | Terminal + SSH + Lua exec |
| QuickLook (22) | 9.0 | 0 | 21-plugin parser surface |
| kanata (23) | 4.0 | 0 | Keyboard interceptor |
| freerouting (24) | 11.8 | 0 | Java deserialization surface |
| WLED (25) | 9.3 | 0 | ESP32 firmware + on-device webserver |
| Baileys (26) | 4.3 | 0 | Reverse-engineered WhatsApp Web client |
| skills (27) | 0.2 | 0 | Claude Code skills marketplace (npx-installable) |
| multica (28) | 0.3 | 0 | Agentic platform (TS+Go monorepo, self-host + cloud) |

**Pattern (n=13)**: 12 of 13 catalog repos uniformly skip GHSA publication despite operating privileged tools with documented vulnerability classes. Ghostty stands out as the **single counter-example** — 4 advisories published before V1.2 telemetry began plus 1 in 2026-03 — demonstrating that publication IS achievable when the maintainer/org chooses to use the channel.

**Readings (still applicable)**:
- (a) no security-relevant issues discovered — implausible for this sample
- (b) silent-fix-via-release cadence
- (c) disclosure stops at maintainer

**The ghostty exception strengthens reading (c)**, not weakens it: ghostty has institutional backing (Mitchell Hashimoto / CHIM / Ghostty.org) and explicit security-disclosure infrastructure. The other 12 entries either lack the institutional layer (community projects, solo maintainers) OR have documented disclosure-handling failures (WLED #5340, Baileys PR #1996). The pattern remains: when the institutional layer is missing, GHSA publication doesn't happen.

**WLED + Baileys disclosure-handling failures** (documented since n=11): WLED had a permissions misconfiguration on the private advisory UI; Baileys had a community-submitted vulnerability-fix PR stale-closed after 148 days with the maintainer's promised 'own version' never materializing. Neither scenario produced a GHSA. Both Phase 4 reviews considered Q3 override (amber → red) and declined — the current amber/'partly' framing is treated as adequate.

**Implication for V1.3**: the `community_norms_differ` enum value (CONSOLIDATION §5 R3 Item C) hasn't fired, but the silent-fix pattern at 12/13 documents a stable community norm for non-institutional projects. V13-3 analysis flagged this and held; the n=13 update doesn't change the disposition.

### 5.3 · Maintainer concentration taxonomy

| Pattern | Examples (n=13) |
|---|---|
| Extreme solo (≥95% of top-N) | wezterm (wez 97.2%) |
| High solo (80–95%) | freerouting (Andreas 86.7%), ghostty (mitchellh 85.9%), **skills (mattpocock 87.3%)** |
| Effectively solo (top-1 ≥50% with no peer) | Kronos (top-1 ~59%), kanata (jtroo 78.2%) |
| Two-maintainer (combined ≥85%) | kamal (djmb 55.7% + dhh 31.5% = 87.2%), QuickLook (xupefei + emako combined high) |
| Single author (near-100% of human commits) | browser_terminal (BatteredBunny dominant) |
| Dispersed (top-1 ≤40%) | Xray-core (RPRX 33.5%), **multica (NevilleQingNY 29.7%)** |

**New at n=13**:
- **skills** joins High-solo (87.3%) — typical for a solo curator running a content/marketplace project.
- **multica** joins Dispersed alongside Xray-core — first non-network-proxy entry in this band; agentic-platform shape with multiple contributors at single-digit %.

### 5.4 · Formal PR review rate distribution

Ordered high → low (n=13):

- kanata (23): **44.0%** (formal) / 48.0% (any) — highest formal review rate
- WLED (25): **41.0%** (formal) / 79.0% (any) — second-highest formal; highest any-review rate
- freerouting (24): 9.5% / 32.4%
- multica (28): 5.7% / 5.7% (formal == any; no informal reviews)
- QuickLook (22): 5.1% / 25.5%
- kamal (18): 4.7% / 18.7%
- wezterm (21): 3.3% / 32.7%
- Xray-core (19): 2.3% (formal) / 7.7% (any)
- Kronos (17): 0% / 5.3%
- browser_terminal (20): 0% / 0%
- skills (27): 0% / 0%
- ghostty (16): null / null (sampler returned null this re-render)
- Baileys (26): null / null (closed-without-merge dominates stream — PR-sampler robustness gap, V12x-14)

**Implication (refined at n=13)**: kanata is no longer the lone outlier. **WLED's 41% formal / 79% any-review** is comparable in voluntary-review culture, despite WLED having no governance ruleset. The kanata + WLED pair shows that branch-protection enforcement is not a precondition for high voluntary review; community norms can carry the load on focused-domain projects (keyboard daemon, IoT firmware). Q1 advisory color stays the same — these voluntary-review-high entries still fire red on `q1_has_branch_protection=False`, with Phase 4 leaving as-is. The override hasn't fired on these because the formal-review percentage is "high relative to peers" but still well below the implicit "trustworthy" threshold (which for the calibration v2 ruleset sits closer to 70%+).

---

## §6 · Shape / category coverage

Languages catalogued (post-V1.2, n=13 V1.2 wild scans + markitdown V1.2-style):
- **Python**: Kronos (17), markitdown (15) — ML model + document-conversion library
- **Ruby**: kamal (18)
- **Go**: Xray-core (19), browser_terminal native host (20), multica (28) backend
- **Zig**: ghostty (16)
- **Rust**: wezterm (21), kanata (23)
- **C#**: QuickLook (22)
- **Java**: freerouting (24)
- **C++**: WLED (25) — ESP32 embedded firmware
- **TypeScript / JavaScript**: Baileys (26), multica (28) frontend (Next.js + Electron) — also browser_terminal extension frontend
- **Markdown / skill-content as primary artifact**: skills (27) — first agent-skills-collection shape; primary_language reported as Shell because of installer scripts, but the content is markdown SKILL.md files

Category diversity (n=13 V1.2 wild scans):
- Terminal emulators: ghostty (Zig) + wezterm (Rust) — direct cross-shape comparator pair
- Network / proxy: Xray-core
- Deploy orchestrator: kamal
- Browser extension + native host: browser_terminal
- Windows shell integration: QuickLook
- Keyboard / input daemon: kanata
- ML foundation model: Kronos
- EDA / PCB autorouter: freerouting
- Document conversion: markitdown
- Embedded IoT firmware: WLED — first networked-device-on-home-LAN threat model
- Reverse-engineered platform-API library: Baileys — first ToS-violation-category threat model
- **Claude Code skills/plugin marketplace: skills (NEW)** — first agent-skills-collection shape; npx-installable plugin distribution; sample-floor-degeneracy concerns on Q2 (entire shape is recently-launched)
- **Agentic platform monorepo: multica (NEW)** — first agentic-platform structural shape; TS frontend + Go backend + Docker self-host via GHCR + Homebrew + curl|bash; closed-within-window Q2 counter-signal

Shape distribution per `phase_3_advisory.shape_classification.category` at n=13 (from `compute.classify_shape()`):

| Category | Count | Entries |
|---|---|---|
| desktop-application | 4 | ghostty (16), browser_terminal (20), wezterm (21), QuickLook (22) |
| cli-binary | 3 | kamal (18), Xray-core (19), kanata (23) |
| specialized-domain-tool | 2 | Kronos (17), freerouting (24) |
| library-package | 2 | Baileys (26), multica (28) |
| embedded-firmware | 1 | WLED (25) |
| agent-skills-collection | 1 | skills (27) |

**Classifier observation: multica misclassified as `library-package`.** multica is structurally an agentic platform (Next.js + Electron + Go server + GHCR self-host), but classify_shape() picked `library-package` because the npm-publishable manifest matched first. The `agentic-platform` SHAPE_CATEGORIES enum value exists but is a stub — no detection branch fires. Diagnosis owed for next session; queued in `docs/back-to-basics-plan.md` §Current state Next-session feature work as the agentic-platform classifier branch (compound heuristic recommended: `docker-compose.selfhost*.yml` AND `server/` with non-npm backend manifest AND publishable npm, inserted as Step 7.5 between cli-binary and library-package).

---

## §7 · V13-3 progress

**V13-3 trigger**: 11 V1.2 wild scans (per CONSOLIDATION §8 deferred ledger). **STATUS: TRIGGER FIRED at n=11 (entries 16–26); board review closed 2026-04-20** — see `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/CONSOLIDATION.md` and the §10 Changelog "V13-3 CLOSE" entry below.

**Post-trigger cadence (broadened per OD-4): N=25 V1.2 scans OR any of 6 taxonomy-strain events.**

| Cadence axis | Status at n=13 |
|---|---|
| V1.2 wild scan count | **13 of 25** toward N=25 trigger |
| Taxonomy-strain events fired | **2 of 6** (skills entry 27 = first `missing_qualitative_context` use at any n; multica entry 28 = second consecutive use with distinct semantic driver) |

**The §7 n=11 inference no longer holds at n=13**. The original V13-3 §7 analysis text said "evaluate the override-enum distribution (6 signal_vocabulary_gap / 2 harness_coverage_gap / 1 threshold_too_strict / 0 of the other 4 enum values) for V1.3 pruning candidates" — `missing_qualitative_context` is now exercised twice with two distinct underlying drivers (sample-floor degeneracy on skills; closed-within-window counter-signal on multica). The V13-3 deferred Item C9 ("prune `missing_qualitative_context` with historical-hold") is now contraindicated; see §9 below for the full revision.

**V13-3 analysis scope retained** (from CONSOLIDATION §8): the comparator analysis at pinned V2.4 entries 12–14 (zustand-v3, caveman, Archon) still stands as the cross-pipeline calibration anchor. The cross-shape patterns documented above continue to inform V12x backlog items.

---

## §8 · V1.2.x backlog

Derived from patterns in this document (counts re-derived for n=13):

| ID | Item | Evidence | Priority |
|---|---|---|---|
| V12x-5 | Deserialization auto-fire for Q4 (pattern-based compute signal) | 2/11 overrides; collapses Kronos Q4 + freerouting Q4 | **High** |
| V12x-6 | Multi-ecosystem manifest parsing (Maven/Gradle/Cargo/Gomod/Bundler/.NET) | 9/13 scans hit this coverage gap | **High** |
| V12x-7 | Install-doc URL TLD-deviation detection | 1/13 scans (browser_terminal), high severity when hit | **Medium** |
| V12x-8 | Distribution-channel detection for language-specific package managers | 9/13 scans surface fictitious or missing channels | **Medium** |
| V12x-9 | Dangerous-primitives regex tuning — language qualifier on deserialization family | False positives on 4/13 scans (wezterm, kanata, QuickLook, WLED — ArduinoJson) | **Medium** (Priority 1 requires this fix) |
| V12x-10 | Silent-fix pattern telemetry | **12/13** scans show 0 advisories (ghostty exception: 5 GHSA published) — strong case for Q3 rubric adjustment in V1.3 | Informational → **V1.3 candidate** |
| V12x-11 | Firmware-default-no-auth + CORS-wildcard compound Q4 signal | 1/13 scans (WLED) — Priority 1b | **Medium** |
| V12x-12 | Reverse-engineered-API-library shape Q4 signal (README disclaimer + topic + platform-name) | 1/13 scans (Baileys) — Priority 1c | **Medium** |
| V12x-13 | vendor_keys proximity-context requirement | 1/13 scans (Baileys — `AIza` in WhatsApp protocol dictionary FP) | Low |
| V12x-14 | PR-sampler robustness when closed-without-merge dominates stream | 2/13 scans (Baileys = 0 sample despite 352 lifetime merges; ghostty = null sample at re-render) | Low → **Medium** (now 2 cases) |
| **V12x-15** | **Sample-floor signal for Q2 advisory function** | **1/13 scans (skills) — Priority 1d. Compute returns amber instead of green when `total_merged_lifetime < 5` AND `security_flagged_count == 0`.** | **Medium** |
| **V12x-16** | **Responsive close-rate counter-signal for Q2 advisory function** | **1/13 scans (multica) — Priority 1e. Compute returns amber instead of red when `closed_within_window_30d >= open_security_issue_count` AND `closed_within_window_30d >= 3`.** | **Medium** |
| **V12x-17** | **agentic-platform classifier branch** | multica (28) misclassified as `library-package` because npm manifest matches first; structural shape is `agentic-platform` (currently a stub category). Compound heuristic recommended: `docker-compose.selfhost*.yml` AND `server/` with non-npm backend manifest AND publishable npm, inserted as Step 7.5 between cli-binary and library-package. | **Medium** (likely needs board review since it's calibration v2 scope) |

Each V12x item is additive per board Item F (signal additions are V1.2.x, signal removals are V1.3).

---

## §9 · V13-1 follow-up observations

**The V13-1 split (`missing_qualitative_context` → `signal_vocabulary_gap` + `harness_coverage_gap`) held cleanly across n=11 (entries 16–26).** All 9 overrides at n=11 mapped to the two new labels (6 + 2) plus `threshold_too_strict` (1); the original catchall `missing_qualitative_context` was unused.

**At n=13, the inference no longer holds.** Two consecutive overrides (skills entry 27 + multica entry 28) fire `missing_qualitative_context` with **different underlying semantic drivers**:

| Entry | Q-cell | Driver | Why neither V13-1 split label fits |
|---|---|---|---|
| skills (27) | Q2 | Sample-floor degeneracy: 1 lifetime merged PR + 0 closed-merged security PRs → advisory's GREEN ("they fix problems quickly") over-claims at sample floor | Not `signal_vocabulary_gap` (the rule's vocabulary is fine; rule fires correctly on the data it has). Not `harness_coverage_gap` (harness collected the data faithfully — the underlying numerator is genuinely zero). The mismatch is rule-level: GREEN should not return when sample floor is below threshold. |
| multica (28) | Q2 | Closed-within-window counter-signal: 5 security issues fixed in past 8 days (responsive) sit alongside 4 still open → advisory rule reads only open-side count and lands red; close-side responsiveness is invisible to the rule | Not `signal_vocabulary_gap` (vocabulary is fine). Not `harness_coverage_gap` (harness has the closed-issues data). Not `threshold_too_strict` (a strictness adjustment wouldn't capture the *responsiveness* dimension). The mismatch is qualitative: the maintainer IS responsive on a moving-average view, but the rule reads a snapshot. |

**Both fires are legitimate uses of the catchall enum value**, demonstrating it covers a real and recurring phenomenon class — qualitative context that the rule-based advisory cannot capture. Neither fire could honestly be relabeled to `signal_vocabulary_gap` or `harness_coverage_gap`.

**V13-1 escalation triggers (from CONSOLIDATION §8.1) — re-evaluated at n=13**:
- ✅ No override has fit *none* of the available labels (both used `missing_qualitative_context`, a defined enum value).
- ✅ No override has fit multiple labels with genuine ambiguity (both fires are clearly not `signal_vocabulary_gap` / `harness_coverage_gap` — the catchall is the unambiguous best fit).
- ✅ No Skeptic has flagged the relabeling as inconsistent.

→ **V13-1 split (signal_vocabulary_gap / harness_coverage_gap) remains stable.** The split correctly captures vocabulary + coverage gaps. Escalation triggers above are still ✅.

→ **The V13-3 deferred Item C9 — "prune `missing_qualitative_context` with historical-hold" — is now CONTRAINDICATED.** The catchall is doing real work; pruning it would remove the only enum value that fits both observed driver classes. Two paths forward, deferred to a re-trigger event:

- **Path A (keep the catchall as-is).** `missing_qualitative_context` stays as a stable catchall covering both sample-floor degeneracy and responsive-close counter-signal patterns. Drop Item C9 from the V1.3 pruning slate. Lowest-friction option; preserves backwards compatibility.
- **Path B (split the catchall).** Promote the two observed driver classes into their own enum values: `sample_floor_degeneracy` (skills-shape) and `responsive_close_rate_counter_signal` (multica-shape). Better V12x-15 / V12x-16 telemetry alignment; finer-grained downstream analysis. Requires schema bump + migration of the two existing entries.

**Decision deferred** to the next V13-3 follow-up event (N=25 OR any of the remaining 4 taxonomy-strain events; currently 13/25 + 2/6 strain). If a third `missing_qualitative_context` fire arrives with a *third* distinct semantic driver, escalate to board review immediately rather than wait for the trigger — that would indicate the catchall is genuinely unbounded, not just under-split.

---

## §10 · Changelog

- **2026-04-20** — Document created after 9 V1.2 wild scans. Consolidates observations from catalog entries 16–24 + the V13-1 analysis document.
- **2026-04-20 (entry 25 update)** — Added WLED (25) to roster. signal_vocabulary_gap now modal at 62% (5/8 overrides); 10/10 silent-fix pattern confirmed with a **publicly-documented disclosure-handling failure** (issue #5340 — GHSA-2xwq-cxqw-wfv8). New Priority 1b harness-patch: firmware default-no-auth + CORS-wildcard compound signal. Zero-override streak broken continues (freerouting 24 + WLED 25 both fire signal_vocabulary_gap). V13-3 progress: 10 of 11.
- **2026-04-20 (entry 26 update — V13-3 TRIGGER FIRED)** — Added Baileys (26) to roster. **11 V1.2 wild scans complete.** signal_vocabulary_gap now strongly modal at 67% (6/9 overrides — 3 consecutive Q4 overrides since wezterm streak ended). **11/11 silent-fix pattern** with Baileys adding a second distinct documented failure mode (PR #1996 stale-closed after 148 days, maintainer-promised replacement never materialized). New Priority 1c harness-patch: reverse-engineered-platform-API-library shape signal (README disclaimer phrase detection + topic analysis + platform-name matching). Q4 has become the override hotspot (6 of 9 overrides). V13-3 comparator-calibration analysis is now owed — see §7. TypeScript added as first-class catalog language. Three new V12x backlog items (V12x-11/12/13) derived from Baileys observations; V12x-9 promoted from Low to Medium (4 FP cases now).
- **2026-04-20 (V13-3 CLOSE)** — 042026-v13-3-comparator-calibration board review closed with 2/3 R3 AGREE + owner directive OD-4 (Codex R3 unavailable, R2 positions consistent with all R3 resolutions; Codex assigned code-review gate on staged V1.2.x implementation diff). **V1.2.x landed:** C2 (language-qualifier regex — drops bare `deserialize` keyword; suppresses ArduinoJson FP class), C5 (Q4 auto-fire from unsafe-deserialization hits + tool-loads-user-files condition), C18 (`derive_tool_loads_user_files()` canonical helper), C20 (dry-run FP test at `docs/v13-3-fp-dry-run.md` — 0 FPs on 11 bundles). **V1.3 deferred:** C6 (firmware CORS compound signal), C7 (reverse-eng shape signal with REJECT fallback), C9 (prune `missing_qualitative_context` with historical-hold), C17 (multi-ecosystem manifest parsing), V13-4 (`community_norms_differ` enum addition at N=15 or first Q3 override fire). **Frozen analysis:** `docs/v13-3-analysis.md`. **Follow-up cadence:** G4-broadened — N=25 OR any of 6 taxonomy-strain events. Full CONSOLIDATION at `docs/External-Board-Reviews/042026-v13-3-comparator-calibration/CONSOLIDATION.md`.
- **2026-04-30 (entry 27 update — session 8 first wild scan)** — Added mattpocock/skills (27) to roster. **First Claude Code skills/plugin shape** in V1.2 catalog (47.9k stars, 3 months old, 22 SKILL.md / 1,815 lines, MIT). Q2 override fires `missing_qualitative_context` — **first use of this enum value across all 12 V1.2 wild scans** (was × 0 at n=11). Override rationale: at sample-floor evidence (1 lifetime merged PR + 0 closed-merged security PRs), Phase 3 advisory's GREEN ('Yes — they fix problems quickly') over-claims; honest answer is amber/insufficient-data. Suggested threshold adjustment authored: add `total_merged_lifetime < N` (e.g., 5) sample-floor signal that returns amber rather than green when no closed-fix-lag data exists. **§9 V13-1 inference no longer holds at n=12** — the n=11-bounded claim "missing_qualitative_context catchall hasn't fired post-V13-1 relabel" has its first counterexample. The fire is consistent with V13-3 C9 (prune `missing_qualitative_context` with historical-hold) being premature — the value still has a live use case (sample-floor degeneracy) that doesn't reduce to `signal_vocabulary_gap` or `harness_coverage_gap`. New V12x backlog item (V12x-15) candidate: sample-floor signal for Q2 advisory function. **Taxonomy-strain event** by V13-3 C9-criteria — first use of an enum value previously argued for pruning is a re-evaluation event. V13-3 follow-up still 12/25 toward N=25 cadence; G4 taxonomy-strain count: 1 of 6.
- **2026-05-02 (n=13 re-derivation — session 14)** — Cross-scan tables §2–§9 re-derived from the 13 form.json bundles in `docs/scan-bundles/` (back-to-basics-plan §Current state follow-up #6 closed). Headline shifts: signal_vocabulary_gap modal share dropped 67%→55% as `missing_qualitative_context` fires twice consecutively (skills + multica) with distinct drivers (sample-floor degeneracy + closed-within-window counter-signal); Q4 override hotspot share dropped 67%→45% with Q2 climbing 22%→36%; override streak now 5 (entries 24–28); zero-override scans unchanged at 3 (21/22/23). Five new V12x backlog items derived: V12x-15 (Q2 sample-floor signal), V12x-16 (Q2 close-rate counter-signal), V12x-17 (agentic-platform classifier branch). §5.2 silent-fix corrected from 11/11 to 12/13 (ghostty was mis-recorded as 0 advisories at n=11; current bundle shows 5 GHSA published). §6 shape-classifier table added (desktop-app 4, cli-binary 3, specialized-domain-tool 2, library-package 2 [incl. multica misclassified], embedded-firmware 1, agent-skills-collection 1). §9 V13-1 follow-up rewritten: V13-1 split holds, but `missing_qualitative_context` carries genuine semantic load → V13-3 deferred Item C9 (prune the catchall) is now contraindicated; two paths (keep-as-is OR split into `sample_floor_degeneracy` + `responsive_close_rate_counter_signal`) deferred to next V13-3 trigger event.
- **2026-05-02 (entry 28 update — session 13, re-scan of multica)** — Added multica-ai/multica (28) to roster. **Re-scan of catalog entry 11** (V2.4 / delegated, 2026-04-19, HEAD `b8907dd`) — first re-scan of an existing V2.4 catalog entry through V2.5-preview pipeline at a later SHA (16 days later, HEAD `3df95c8`). 23.5k-star agentic platform — TS+Go monorepo (Next.js + Electron + Go server + Docker self-host via GHCR). **Verdict shift vs prior**: 888888 dev-verification-code Critical → Warning (APP_ENV=production gate landed ~2026-04-18, closed issue #1304 in window between scans); two new Warnings surfaced (install.sh checksum gap on Unix vs install.ps1 SHA256-verify on Windows; ruleset declared but `enforcement: disabled`); one new privesc Warning (#1114 LD_PRELOAD/NODE_OPTIONS bypass on agent custom_env, open since prior scan). **Q2 override fires `missing_qualitative_context` — second consecutive use** (after skills entry 27); pattern now n=2/13 = 15% of V1.2 wild scans land here. Override rationale: 5 security issues closed in past 8 days (888888 #1304, shell.openExternal #1115, Hermes filterCustomArgs #1113, /health/realtime #1606, open-redirect #1116) — the close-side cadence roughly matches the arrival rate (4 still open, oldest 16 days). Phase 3 advisory's RED is read off open-side count alone; the responsiveness counter-signal is invisible to compute. **Taxonomy-strain reinforcement**: two consecutive fires of an enum value previously argued for pruning solidifies the case that `missing_qualitative_context` covers a real phenomenon class — but the two fires have DIFFERENT underlying drivers (skills = sample-floor degeneracy; multica = closed-within-window counter-signal). Either justify keeping the catchall enum as-is, or split into two more-specific enum values. New V12x backlog item (V12x-16) candidate: weight `closed_within_window` as a Q2 advisory counter-signal. **Shape misclassification noted**: classify_shape() picked `library-package` (publishable npm manifest matched first) when multica's structural shape is `agentic-platform` (server + CLI + web + desktop) — diagnosis owed for next session. V13-3 follow-up at 13/25 toward N=25 cadence; G4 taxonomy-strain count: 2 of 6.
