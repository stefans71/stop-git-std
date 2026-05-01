# Calibration audit — empirical baseline for rule-table redesign

**Audit date:** 2026-05-01
**Scope:** 27 catalog scans (12 V1.2-schema with structured `form.json` bundles + 15 older V2.4 scans tracked by catalog table only)
**Purpose:** establish what the current rules actually do across the catalog, so the calibration redesign (90% programmatic + shape-aware + median-OSS-pattern lands at ~5–6/10 not ~9/10) has empirical ground truth.

Source-of-truth for V1.2: `docs/scan-bundles/*.json` (12 bundles). Source-of-truth for catalog metadata: `docs/scanner-catalog.md`. Cross-referenced (without duplicating) `docs/v12-wild-scan-telemetry.md` §2 / §10 where useful.

---

## §1 — Catalog overview

**By verdict** (n=27, including 1 re-run determinism record):

| Verdict | Count | % |
|---|---|---|
| Critical | 12 | 44% |
| Caution | 13 | 48% |
| Clean | 1 | 4% |
| (determinism record) | 1 | 4% |

**By methodology**:

| Methodology | Count |
|---|---|
| continuous (Path-A) | 23 |
| delegated (Path-B) | 4 |

**By rendering pipeline**:

| Pipeline | Count | Entries |
|---|---|---|
| `v2.4` | 11 | 1–11 |
| `v2.5-preview` | 16 | 12–27 |

**By primary language** (V1.2-only n=12 since V2.4 catalog rows don't carry language):

| Language | Count |
|---|---|
| Rust | 2 (kanata, wezterm) |
| Go | 2 (Xray-core, browser_terminal) |
| C# / C++ / Java / JavaScript / Python / Ruby / Shell / Zig | 1 each |

**By `catalog_metadata.category`** (V1.2-only):

| Category | Count |
|---|---|
| developer-tooling | 3 (ghostty, skills, wezterm) |
| browser-extension / devops-tooling / eda-tooling / embedded-iot-firmware / input-device-tooling / ml-foundation-model / network-tooling / reverse-engineered-api-library / windows-shell-integration | 1 each |

10 distinct categories across 12 V1.2 scans; only `developer-tooling` is repeated. Shape-coverage is broad but thin per shape.

---

## §2 — Shape distribution (V1.2 scans only, n=12)

Cells abbreviated `r` / `a` / `g` for red / amber / green. Q1=does anyone check, Q2=fix quickly, Q3=tell about problems, Q4=safe out of box. P4-authoritative shown.

| Repo | Lang | Category | Verdict | Q1 Q2 Q3 Q4 | Overrides |
|---|---|---|---|---|---|
| Baileys | JavaScript | reverse-engineered-api-library | Critical | r r r r | Q4=signal_vocabulary_gap |
| Kronos | Python | ml-foundation-model | Critical | r r r r | Q2=signal_vocabulary_gap, Q4=harness_coverage_gap |
| QuickLook | C# | windows-shell-integration | Caution | r g r a | — |
| WLED | C++ | embedded-iot-firmware | Critical | r r a r | Q4=signal_vocabulary_gap |
| Xray-core | Go | network-tooling | Critical | r a a a | Q2=threshold_too_strict |
| browser_terminal | Go | browser-extension | Critical | r g r r | Q4=harness_coverage_gap |
| freerouting | Java | eda-tooling | Critical | r g a r | Q4=signal_vocabulary_gap |
| ghostty | Zig | developer-tooling | Caution | a g a a | Q1=signal_vocabulary_gap |
| kamal | Ruby | devops-tooling | Caution | a g a a | Q1=signal_vocabulary_gap |
| kanata | Rust | input-device-tooling | Critical | a g r a | — |
| skills | Shell | developer-tooling | Caution | r a r a | Q2=missing_qualitative_context |
| wezterm | Rust | developer-tooling | Caution | r r a a | — |

---

## §3 — Scorecard cell distribution (V1.2, n=12)

| Q | P4 (red/amber/green) | P3-advisory (r/a/g) | Overrides | Override reasons |
|---|---|---|---|---|
| Q1 | 9 / 3 / 0 | 11 / 1 / 0 | 2 (both red→amber) | signal_vocabulary_gap × 2 |
| Q2 | 4 / 2 / 6 | 4 / 1 / 7 | 3 (mixed directions) | signal_vocabulary_gap × 1, threshold_too_strict × 1, missing_qualitative_context × 1 |
| Q3 | 6 / 6 / 0 | 6 / 6 / 0 | **0** | — |
| Q4 | 5 / 7 / 0 | 0 / 12 / 0 | 5 (all amber→red) | signal_vocabulary_gap × 3, harness_coverage_gap × 2 |

**Key observations from §3:**
- **Q3 has zero overrides across all 12 scans** — Phase 4 LLM never disagrees with the Phase 3 advisory on Q3. Either the Q3 rule is correctly calibrated, or the LLM has internalized the rule and reproduces it deterministically (more likely; see §5).
- **Q4 is the override hotspot** — 5 of 12 scans (42%) override Q4, all in the same direction (amber→red). The Q4 rule is systematically too lenient on default-install-path danger.
- **Q1 is rule-too-strict in 2 of 12 cases** — both overrides go the other direction (red→amber). The rule fires red on patterns the LLM judges deserve amber.
- **No Q1 / Q3 ever resolves to green in P4 across any scan.** The system has no positive-signal exit condition for these cells.

---

## §4 — Q1 firing patterns: where does Q1 land red?

9 of 12 V1.2 scans have Q1=red in Phase 4. Their signal patterns:

| Repo | solo? | top1 | classic_BP | rulesets | rules_on_default | CODEOWNERS | formal_review_rate | verdict |
|---|---|---|---|---|---|---|---|---|
| Baileys | F | 0.71 | 404 | 0 | 0 | F | n/a | Critical |
| Kronos | F | 0.59 | 404 | 0 | 0 | F | 0% | Critical |
| QuickLook | F | 0.52 | 404 | 0 | 0 | F | 5.1% | **Caution** |
| WLED | F | 0.46 | 404 | 1 | 2 | F | **41%** | Critical |
| Xray-core | F | 0.34 | 404 | 0 | 0 | F | 2.3% | Critical |
| browser_terminal | F | 0.77 | 404 | 0 | 0 | F | 0% | Critical |
| freerouting | T | 0.87 | 404 | 1 | 2 | F | 9.5% | Critical |
| skills | T | 0.87 | 404 | 0 | 0 | F | 0% | **Caution** |
| wezterm | T | 0.97 | 404 | 0 | 0 | F | 3.3% | **Caution** |

**Pattern buckets:**

| Pattern | Count | Description |
|---|---|---|
| **A. "OSS minimal-governance default"** (no classic-BP + 0 rulesets + 0 rules + no CODEOWNERS + low/no formal review) | 6 of 9 (67%) | Baileys, Kronos, Xray-core, browser_terminal, skills, wezterm. **3 Critical + 3 Caution** — verdict is decided elsewhere, not by Q1. |
| **B. "OSS default" but with non-trivial review rate** (≥ 5% formal) | 1 of 9 | QuickLook (5.1%, Caution) — rule still fires red even though there's *some* gate activity. |
| **C. "Has rulesets + rules-on-default but no CODEOWNERS"** | 2 of 9 | WLED (41% formal!), freerouting (9.5%). The presence of rulesets isn't enough to soften red without CODEOWNERS, even when formal review is high (WLED). |

**Q1=amber overrides** (rule-says-red, LLM-says-amber):

| Repo | Pattern | Override reason | Why LLM softened |
|---|---|---|---|
| ghostty | solo + classic_off + **rulesets=1, rules_on_default=4, CODEOWNERS=true** + formal=n/a | signal_vocabulary_gap | Has CODEOWNERS — rule didn't credit it |
| kamal | top1=0.56 + classic_off + rulesets=1, rules_on_default=1 + no CODEOWNERS + 71 semver releases + CodeQL SAST | signal_vocabulary_gap | Compound positive signals (CodeQL + release cadence) the rule doesn't see |

**Headline:** the dominant Q1=red pattern is "OSS minimal-governance default" — present on 50% of all V1.2 scans (6 of 12). Of those 6, half (3) are Caution-verdict and half (3) are Critical-verdict. **Q1=red is not a verdict-driving signal in 3 of 6 cases** (skills, wezterm, QuickLook all land Caution despite Q1=red). **The cell over-calls.**

---

## §5 — Q3 firing patterns: where does Q3 land red?

6 of 12 V1.2 scans have Q3=red. **All 6 share identical signal pattern**: `has_security_md=False AND has_contributing=False AND security_advisories_count=0`.

| Repo | Verdict |
|---|---|
| Baileys | Critical |
| Kronos | Critical |
| QuickLook | **Caution** |
| browser_terminal | Critical |
| kanata | Critical |
| skills | **Caution** |

**Q3=amber scans** (have ≥ 1 disclosure signal):

| Repo | Disclosure signal present | Short answer |
|---|---|---|
| WLED | CONTRIBUTING + CoC | "Partly — CONTRIBUTING + CoC present (health 75%); no SECURITY.md..." |
| Xray-core | SECURITY.md | "Partly — SECURITY.md with private channel, but 0 published advisories in 5.5 years" |
| freerouting | CONTRIBUTING + CoC | "Partly — CONTRIBUTING + CoC present (health 75%) but no SECURITY.md..." |
| ghostty | CONTRIBUTING + 5 advisories | "Partly — 5 GHSA advisories published, but no SECURITY.md" |
| kamal | CONTRIBUTING | "Partly — CONTRIBUTING exists, but no SECURITY.md..." |
| wezterm | CONTRIBUTING | "Partly — CONTRIBUTING present, but no SECURITY.md..." |

**Headline:** Q3 has a **strict binary trip**: presence of *any one* disclosure-adjacent signal (SECURITY.md OR CONTRIBUTING OR ≥1 advisory) lands amber; absence of all three lands red. **No middle ground.** 4 of 6 Q3=red scans are Critical-verdict, but **2 are Caution-verdict** — same critique as Q1, the cell over-calls in those two cases (QuickLook, skills). Both Caution-verdict-with-Q3=red scans are repos where the absence of disclosure machinery is **proportional to project age/maturity** (skills is 3 months old; QuickLook ships defensive-by-design tooling) — a context the rule doesn't see.

---

## §6 — C20 severity distribution

| C20 result | Count | Repos |
|---|---|---|
| Critical | 2 | Xray-core, kanata |
| Warning | 6 | Baileys, Kronos, QuickLook, browser_terminal, skills, wezterm |
| None (no fire) | 4 | WLED, freerouting, ghostty, kamal |

**For the 2 Critical-fires:** both have `has_recent_release_30d=True` AND `ships_executable_code=True`. The rule's "all-governance-negative + recent-release + ships-executable" composite is firing as designed.

**For the 4 no-fires:** all 4 have at least one positive governance signal (rulesets present, OR org-level rules, OR CODEOWNERS) — `all_governance_negative` is False, so the rule short-circuits before checking other conditions.

C20 calibration appears clean by its own logic. The question is whether C20's Warning-tier carries the right weight in downstream verdict computation (currently Warning C20 + a single LLM-authored Critical finding = Critical verdict overall, regardless of governance posture).

---

## §7 — Solo-maintainer prevalence

**`is_solo=True`** (top-1 contributor share > 80% per `compute_solo_maintainer`): 4 of 12.

| Repo | top1 share | Verdict | Q1 cell |
|---|---|---|---|
| freerouting | 0.87 | Critical | red |
| ghostty | 0.86 | **Caution** | amber (overridden) |
| skills | 0.87 | **Caution** | red |
| wezterm | 0.97 | **Caution** | red |

**`is_solo=False`** but with high concentration (top-1 ≥ 0.50): 5 of 8 non-solo scans cluster between 0.50–0.78 share (Baileys 0.71, Kronos 0.59, QuickLook 0.52, kamal 0.56, browser_terminal 0.77, kanata 0.78). The 80% threshold for `is_solo` is a sharp cliff; effective bus-factor concentration is higher than the boolean suggests across the catalog.

**Headline:** of 4 `is_solo=True` scans, only 1 (freerouting, with confirmed Java deserialization RCE) lands Critical. The other 3 are Caution. **Solo-maintainer status alone is NOT a Critical-verdict driver in the current data** — it tilts toward Caution unless an exploitable code-level finding stacks. This is consistent with the owner's "OSS-default solo pattern should land at 5–6/10, not 9/10" observation.

---

## §8 — Override clusters

Total V1.2 overrides: **10 across 12 scans**.

| Scan | Q | direction | Reason | Truncated rationale |
|---|---|---|---|---|
| Baileys | Q4 | amber→red | signal_vocabulary_gap | reverse-engineered unofficial WhatsApp client → ToS violation + account ban |
| Kronos | Q2 | amber→red | signal_vocabulary_gap | 95-day-old RCE issue #216 unfixed, fix PR #249 sitting 7 days unreviewed |
| Kronos | Q4 | amber→red | harness_coverage_gap | install from master + unpinned deps + disclosed RCE on finetune path |
| WLED | Q4 | amber→red | signal_vocabulary_gap | default-install no auth + CORS wildcard on all origins/methods |
| Xray-core | Q2 | red→amber | threshold_too_strict | 0 open security issues + 100 releases (3d old); 77-day hardening proposal not a fix |
| browser_terminal | Q4 | amber→red | harness_coverage_gap | install doc directs Chrome users to typosquat TLD |
| freerouting | Q4 | amber→red | signal_vocabulary_gap | Java deserialization RCE class on user-loaded board files |
| ghostty | Q1 | red→amber | signal_vocabulary_gap | ruleset-based protection + CODEOWNERS, but concentration risk |
| kamal | Q1 | red→amber | signal_vocabulary_gap | Copilot ruleset + CodeQL + 71 semver releases, but 4.7% formal review |
| skills | Q2 | green→amber | missing_qualitative_context | 3-mo repo, 1 lifetime PR, no fix events to grade |

**Reason distribution** (matches `v12-wild-scan-telemetry.md` §2):
- `signal_vocabulary_gap` × 6 (60%) — rule's signal vocabulary doesn't capture the qualitative truth (positive *or* negative)
- `harness_coverage_gap` × 2 (20%) — harness didn't capture the data the rule would need
- `threshold_too_strict` × 1 (10%) — threshold trips on hardening, not vulns
- `missing_qualitative_context` × 1 (10%) — first fire of this enum value at any n; sample-floor degeneracy

**Common theme:** 8 of 10 overrides (80%) are the LLM injecting context the rule cannot see — either positive context that should soften (Q1 overrides), or risk context that should sharpen (Q4 overrides). The override mechanism is currently doing the work of "shape-aware judgment" that should be expressed as rules.

---

## §9 — Cross-shape calibration observations

**Observation 1 — Q1=red is verdict-decoupled.** 9 of 12 scans have Q1=red, but only 6 of those 9 are Critical-verdict (67%). The other 3 (skills, wezterm, QuickLook) are Caution. **Q1=red is not predictive of Critical.** It functions as a constant background signal across the catalog rather than a discriminator.

**Observation 2 — Q3=red is even more decoupled.** 6 of 12 scans have Q3=red (all with the same trip pattern: no SECURITY.md + no CONTRIBUTING + 0 advisories). Of those 6, 4 are Critical and 2 are Caution. The Q3 rule is binary (one signal flips the cell), so it can't distinguish "young repo with no time to need disclosure machinery" (skills) from "established repo deliberately suppressing disclosure" (Baileys). **Q3 needs an age/activity moderator.**

**Observation 3 — Q4 is where verdict actually lives.** 5 of 12 Q4 cells are red after override, and 100% of Q4=red cases are Critical-verdict (Baileys, Kronos, WLED, browser_terminal, freerouting). Conversely, all 5 Caution-verdict scans have Q4=amber (none red). **Q4 is the strongest single predictor of the final verdict in current data.** And every Q4 red required a Phase 4 override — the Phase 3 rule never reaches red on Q4 (advisory output: 12/12 amber).

**Observation 4 — Solo + active is the catalog median pattern.** 4 of 12 are `is_solo=True`; 5 of 8 non-solo scans have top-1 share 0.50–0.78 (effectively concentrated). Of the catalog's "concentrated maintainership" scans (ad hoc 0.50+ threshold = 9 of 12), only 4 are Critical and 5 are Caution — concentration alone is a Caution-tier signal, not Critical. Confirms owner's intuition.

**Observation 5 — Shape category appears to matter for Q3/Q4 even though the rules ignore it.** All 3 `developer-tooling` scans (ghostty, skills, wezterm) land Caution; 0 of 3 land Critical despite all having `is_solo=True` or near-solo concentration. The 9 single-category scans split 7 Critical / 2 Caution (QuickLook, kamal). **Shape category correlates with verdict more strongly than Q1 cell color does.** The rule table is shape-blind; the LLM's Phase 4 judgment is implicitly shape-aware. Encoding shape-awareness in the rule table would close this gap.

**Observation 6 — Override directions are predictable by shape.** All Q1 overrides (red→amber softening) come from solo-or-near-solo OSS scans where positive secondary signals exist (CODEOWNERS, ruleset, CodeQL, semver release cadence). All Q4 overrides (amber→red sharpening) come from scans where the install path has a specific exploitable property the rule didn't see (RCE class, typosquat URL, no-auth firmware default, ToS-violation library category). The override-reason distribution maps cleanly to "positive shape signals not credited" + "negative shape signals not detected."

---

## §10 — Recommended rule-table starting points

10 specific rules the data argues for. Each cites scan evidence. Keyed `RULE-N` for tracking through calibration design.

**RULE-1: For all shapes, when `(top1_share < 0.95 AND has_codeowners=true AND rulesets_count >= 1 AND rules_on_default >= 1)`, Q1 should be `amber` not `red`.**
*Evidence:* ghostty (top1=0.86, has CODEOWNERS, 1 ruleset, 4 rules-on-default) — Phase 4 overrode red→amber with `signal_vocabulary_gap`. Rule should credit the CODEOWNERS-plus-ruleset combination.

**RULE-2: For all shapes, when `(any_review_rate >= 30% OR formal_review_rate >= 30%)`, Q1 should be `amber` not `red` regardless of branch protection.**
*Evidence:* WLED (41% formal review, 86% any-review — second-highest in catalog) currently lands Q1=red; the high review activity is invisible to the rule. WLED Phase 4 didn't override Q1 but the cell is mis-coloring the actual practice.

**RULE-3: For `category in {developer-tooling, devops-tooling}` shapes, when `(rulesets_count >= 1 OR has_codeql=true OR releases_count >= 10)`, Q1 should be `amber` not `red`.**
*Evidence:* kamal — top1=0.56, no CODEOWNERS, but Copilot ruleset + CodeQL + 71 semver releases. Phase 4 overrode red→amber. Shape-aware credit for compound positive signals.

**RULE-4: For Q3, when `(repo_age_days < 180 AND total_merged_lifetime_prs < 5)`, Q3 should be `amber` (with rationale "young repo — no disclosure-track history to grade") not `red`.**
*Evidence:* skills (repo age 87 days, 1 lifetime merged PR) — currently Q3=red on absence-of-policy. The "no opportunity to need a SECURITY.md" case is structurally distinct from "deliberately suppresses disclosure."

**RULE-5: For Q3, when `(security_advisories_count >= 3 AND has_contributing=true AND has_security_policy=false)`, Q3 should be `amber` not `red`.**
*Evidence:* ghostty — 5 GHSA advisories published proves a working disclosure pipeline despite missing SECURITY.md. The current Q3 rule does this (it lands amber for ghostty). Promote this combination from amber-floor signal to a documented amber-trip rule for clarity.

**RULE-6: For Q4, when `(dangerous_primitives.deserialization_unsafe.hits >= 1 OR dangerous_primitives.cmd_injection.hits >= 1) AND tool_loads_user_files=true`, Q4 should be `red` (auto-fire, no LLM override needed).**
*Evidence:* freerouting (Java ObjectInputStream on user-loaded boards), Kronos (pickle.load on finetune path). The V13-3 C5 patch already implements deserialization auto-fire for Q4; extend to cmd_injection. Eliminates 2 of 5 Q4 overrides.

**RULE-7: For Q4, when `category == 'browser-extension' AND install_doc_urls_have_tld_deviation=true`, Q4 should be `red` with rationale "install-doc URL typosquat detected."**
*Evidence:* browser_terminal — chrome.google.cm typosquat in install doc. Rule needs new signal `install_doc_urls_have_tld_deviation` from the harness (V12x-7). 1 of 5 Q4 overrides.

**RULE-8: For Q4, when `category == 'embedded-iot-firmware' AND default_install_no_auth=true AND cors_wildcard=true`, Q4 should be `red` with rationale "firmware default-install LAN-trust with no auth + CORS-wildcard."**
*Evidence:* WLED. New compound signal needed (V12x-11). 1 of 5 Q4 overrides.

**RULE-9: For Q4, when `category == 'reverse-engineered-api-library' AND readme_has_tos_violation_disclaimer=true`, Q4 should be `red` with rationale "reverse-engineered unofficial client — ToS violation + account-ban risk inherent to use."**
*Evidence:* Baileys. New signal needed: harness scans README for "reverse-engineered" / "unofficial client" / specific platform ToS-disclaimer phrasing (V12x-12 candidate). 1 of 5 Q4 overrides.

**RULE-10: For all shapes, when `(verdict candidate is Critical AND no findings have severity=Critical from {kind: Vulnerability, kind: Supply-Chain})`, downgrade to Caution OR introduce a `Critical-via-governance-only` verdict tier.**
*Evidence:* this is the AT-T2.3 question reframed empirically. Currently no V1.2 scan has hit this exact pattern (every Critical-verdict scan in the catalog has at least one Critical Vulnerability or Supply-Chain finding) — but this is the structural protection against "C20 fires Warning + LLM mis-elevates a governance finding to Critical = report says Critical without actual exploitability." Worth defining now before the rule first triggers in production.

---

## Notes for the calibration design phase

- **Scope boundary**: this audit deliberately stays at "what fires when, on what shape." It does NOT propose specific threshold values, new severity scales, or a new verdict-derivation function. Those decisions belong to the calibration-design doc that follows.
- **Sample size caveat**: n=12 V1.2 scans is small. Several rule recommendations (especially RULE-7 / RULE-8 / RULE-9) cite single-scan evidence. They should be treated as candidates pending more shape-coverage scans, not as proven calibrations.
- **Cross-reference to existing telemetry**: `docs/v12-wild-scan-telemetry.md` §4 already proposes Priority 1/1b/1c harness patches that align with RULE-6 / RULE-8 / RULE-9. The calibration-design phase should resolve the bookkeeping (V12x backlog vs RULE-N labeling) so we don't track the same thing in two places.
- **Q3 over-call is the most underweighted finding here**: every Q3=red has the *exact same* signal pattern, regardless of repo age, activity, or shape. A single age-moderator rule (RULE-4) plus a single positive-signal rule (RULE-5) would shift Q3 from "always red on missing-policy" to "amber by default, red only when active suppression is documented." This would meaningfully change the LLM-summary tone for the OSS median pattern.
- **The override-as-rule-substitute pattern**: 8 of 10 overrides encode shape-aware judgment the rule table doesn't capture. The calibration design should aim to convert most of those overrides into RULE-N entries — leaving the override mechanism for genuine novelty, not for routine context-correction.
