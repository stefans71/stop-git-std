# Calibration Design v2 — Rule-Table Rebuild

**Status:** Phase 1 deliverable. Authored 2026-05-01 in response to `docs/calibration-audit.md` + owner-confirmed direction.
**Predecessor:** `docs/calibration-audit.md` (Phase 0 empirical baseline).
**Successor:** Phase 2 board review (3-model FrontierBoard governance review on this design).

---

## §1 Goals + Non-Goals

### Goals
- Rebuild scorecard cell calibration so the 4-question short-answer text reads accurately to an LLM consumer asking "should I install this?" — currently the cells over-call risk on the OSS-default solo-maintainer pattern, which biases naive LLM summarizers toward false-cautious answers.
- Move ~80% of cell-color decisions from LLM-override-with-rationale into deterministic rules driven by harness signals + shape classification.
- Land the OSS-default solo-maintainer-no-protection pattern at *appropriate* severity per shape (typically amber Q1/Q3, not red).
- Preserve the override mechanism for genuine outliers — but reduce override frequency from ~10/12 V1.2 scans toward 1-2/12.
- Land RULE-1 through RULE-6 as firm proposals; flag RULE-7/8/9 as n=1 candidates with promotion gates; land RULE-10 as a validator-side authoring guard.

### Non-Goals (this design)
- **Visual / CSS changes** — moot until Simple Report is the consumer-facing output; standard HTML stays the auditor view.
- **Schema changes (large-scale)** — cell short-answer language stays in `phase_4_structured_llm.scorecard_cells.<q>.short_answer`. We may add 1-2 small fields (`shape_classification` at the form level, or a per-cell `rule_id_applied` for traceability), TBD by board review.
- **Verdict-derivation function changes** — `compute_verdict` continues to derive verdict from finding severities. This design touches cells, not the verdict.
- **Finding-severity rule programmaticization** — see §7 scope decision. The audit covered cells; programmaticizing finding-severity assignment is broader and proposed for a follow-up Phase 1.5.
- **Prose authoring** — the LLM still writes the editorial caption, per-finding bodies, and action steps. The mechanical reformatting work (REPO_VITALS, COVERAGE_DETAIL, PR_SAMPLE, EVIDENCE table rows) is Phase 4 of the back-to-basics plan, not this design.

---

## §2 Architecture Overview

### Shape as a modifier (not lookup-key, not separate dimension)

Owner asked me to be explicit about how the shape classifier feeds into the rule table. Three options were on the table:

| Option | Pattern | Tradeoff |
|---|---|---|
| **Lookup key** | Per-shape rule table; `RULES[shape][cell][signals] → color` | Duplication; rule changes need to be applied per-shape; tempts shape-specific calibration drift over time. |
| **Modifier (CHOSEN)** | One unified rule table; rules accept a `shape` parameter and have shape-conditional branches where they need to | Rules stay in one place; shape-awareness is opt-in per rule; clear when a rule is shape-blind vs shape-aware. |
| **Separate scoring dimension** | Shape becomes another input combined at the verdict level | Doesn't fit the architecture — verdict is derived from finding severities, not cells. Cell color rules already aggregate signals; shape needs to feed those rules, not the verdict. |

**Why modifier wins:** the audit data shows ~6 of 10 rule changes are shape-blind (RULE-1, RULE-2, RULE-4, RULE-5, RULE-6, RULE-10), and the shape-aware rules (RULE-3, RULE-7/8/9) are minority cases. A unified table with shape-conditional branches reflects this cleanly. If we go lookup-key, the 6 shape-blind rules become 9 copies (one per shape) with no semantic difference, which is duplication waiting for drift.

The cost of modifier: the rule function gets a `shape` parameter even when it doesn't use it. Acceptable.

### Rule evaluation order

Each cell function (`q1_evaluate`, `q2_evaluate`, `q3_evaluate`, `q4_evaluate`) executes in this order:

```
1. Auto-fire trips (any rule that says "if condition X, immediately return color C")
   — RULE-6 deserialization auto-fire (Q4)
   — RULE-7/8/9 shape-specific Q4 trips (gated by promotion)
   — RULE-10 governance-only authoring guard (cross-cell, evaluated separately)
2. Shape modifiers (rules that adjust thresholds based on shape)
   — RULE-3 Q1 ruleset-disclosure shape qualifier
3. Sample-floor / context modifiers
   — RULE-4 Q3 young-repo softener
   — RULE-5 Q3 ruleset-as-disclosure floor
4. Base rule table (audit's calibration baseline; signal-driven)
   — RULE-1 Q1 governance-floor softener
   — RULE-2 Q1 review-rate softener
5. Fallback to current advisory color (existing compute_scorecard_cells logic)
```

Each rule emits `(color, rule_id, short_answer_template_key)`. The renderer fills the template from signal values. Override mechanism remains as-is for cases the rule table doesn't cover.

### Override mechanism preserved

The Phase 4 LLM-authoritative override gate stays intact. Rules produce a deterministic result; if Phase 4 disagrees, it must explain via `override_reason` (existing 7-value enum). Expected behavior:
- Pre-redesign: ~10 overrides per 12 V1.2 scans (~83% override rate). Most cite `signal_vocabulary_gap` (rules don't capture the relevant signal).
- Post-redesign: 1-2 overrides per 12 V1.2 scans (~12% override rate). Remaining overrides are genuine outliers — shape-novel patterns the rules haven't been calibrated against yet.

If override rate doesn't drop substantially after re-render (Phase 5), the calibration didn't work. Hard signal.

---

## §3 Shape Categories (Closed Enum)

Proposed 9-category enum, derived from grouping the existing `catalog_metadata.shape` text across 27 catalog scans. The enum is exhaustive — every scan must classify into one of these (or land in `other` with a TODO).

| Shape | Examples from current catalog | Decision boundary |
|---|---|---|
| `library-package` | zustand, Baileys | Consumed via package manager (`npm install`, `pip install`, `gem install`, `cargo add`); no standalone binary; no GUI. |
| `cli-binary` | fd, Xray-core, kanata, kamal, wezterm | Standalone CLI tool with binary release artifacts (homebrew/winget/distro packages); user runs from terminal. |
| `agent-skills-collection` | gstack, skills | Markdown-canonical; ≥3 SKILL.md or agent-rule files; install creates symlinks or registers with an agent runtime; post-install Claude executes the markdown. |
| `agentic-platform` | Archon, hermes-agent | Multi-component (server + CLI + web UI typically); hosts LLM workflows or agent orchestration; complex install. |
| `web-application` | postiz-app, multica | Server-side hosted app; Docker-compose or similar self-host; install delivers a long-running web service. |
| `desktop-application` | ghostty, QuickLook, browser_terminal | GUI on user's machine; per-platform binary (.exe, .app, .dmg) or browser extension; user-interactive. |
| `embedded-firmware` | WLED | Cross-compiled to device (ESP32, Arduino, microcontroller); flashed to hardware; runs on user-owned IoT device. |
| `install-script-fetcher` | caveman | Pure curl-pipe-from-main / npx-fetcher / wget-pipe pattern; no formal release tags; install runs an ad-hoc script. |
| `specialized-domain-tool` | freerouting, Kronos, markitdown | Domain-specific tool (EDA, ML model, format parser); install + use pattern doesn't fit other categories cleanly. |
| `other` | (none currently) | Catch-all when classifier can't decide. Forces author attention. |

**Coverage check** — every V1.2 catalog scan must classify cleanly:

| Scan | Proposed shape |
|---|---|
| ghostty | desktop-application |
| Kronos | specialized-domain-tool |
| kamal | cli-binary |
| Xray-core | cli-binary |
| browser_terminal | desktop-application (browser extension + native messaging host) |
| wezterm | desktop-application |
| QuickLook | desktop-application |
| kanata | cli-binary |
| freerouting | specialized-domain-tool |
| WLED | embedded-firmware |
| Baileys | library-package |
| skills | agent-skills-collection |

12/12 classify cleanly. No `other`. ✓

**Cross-shape modifiers (orthogonal to category):**

Some risk patterns cut across shape — they're modifiers, not categories. Proposed boolean flags on the shape classification result:

- `is_reverse_engineered` — true when README contains disclaimer-style language ("unofficial," "reverse-engineered," "ToS may apply") OR `catalog_metadata.shape` text contains the phrase. Affects Q4 — non-engineering risk class. (Currently true: Baileys.)
- `is_privileged_tool` — true when the tool runs with elevated permissions (sudo install scripts, kernel module, system daemon, hardware driver, terminal emulator handling SSH keys). Affects Q1 + Q4 — concentration risk amplified. (Currently true: ghostty, wezterm, kanata, QuickLook, WLED, browser_terminal.)
- `is_solo_maintained` — already computed by `compute_solo_maintainer()`. Surfaced here for rule visibility.

These modifiers are computed by helpers called by `classify_shape()`. They don't need their own enum.

---

## §4 `classify_shape()` Signature + Heuristic

```python
from typing import NamedTuple

class ShapeClassification(NamedTuple):
    category: str           # one of the 9 enum values above
    is_reverse_engineered: bool
    is_privileged_tool: bool
    is_solo_maintained: bool
    confidence: str         # "high" / "medium" / "low" — degraded when no clear signal match
    matched_rule: str       # e.g. "agent_rule_files >= 3 + Markdown primary"

def classify_shape(form: dict) -> ShapeClassification:
    """Classify a scan form into a shape category + cross-shape modifiers.

    Reads from form.phase_1_raw_capture (primary inputs) +
    form.phase_4_structured_llm.catalog_metadata.shape (LLM-authored hint, fallback).

    Returns a ShapeClassification for the rule table to consume.
    Deterministic — same form always produces same classification.
    """
```

**Inputs (read-only):**
- `phase_1_raw_capture.repo_metadata.{primary_language, topics}`
- `phase_1_raw_capture.distribution_channels.channels`
- `phase_1_raw_capture.code_patterns.agent_rule_files` (count + paths)
- `phase_1_raw_capture.code_patterns.executable_files` (count + types)
- `phase_1_raw_capture.releases.entries` (count + asset filenames)
- `phase_1_raw_capture.dependencies.manifest_files`
- `phase_1_raw_capture.install_script_analysis.scripts`
- `phase_1_raw_capture.code_patterns.dangerous_primitives.*` (for cross-shape modifier detection)
- `phase_4_structured_llm.catalog_metadata.shape` (FALLBACK only — LLM-authored prose hint)

**Heuristic decision tree (priority order):**

```
1. agent-skills-collection
   IF code_patterns.agent_rule_files.count >= 3
      OR primary_language == "Markdown"
      OR (".claude-plugin/plugin.json" present in tarball file list)
   → agent-skills-collection

2. embedded-firmware
   IF primary_language IN {"C++", "C"}
      AND (Arduino/ESP/PlatformIO/microcontroller files present
           OR repo_metadata.topics contains "iot"/"firmware"/"embedded")
   → embedded-firmware

3. install-script-fetcher
   IF install_script_analysis.scripts is non-empty
      AND releases.entries.count == 0
      AND code_patterns.executable_files is empty
      AND no GUI binary patterns
   → install-script-fetcher

4. desktop-application
   IF executable_files contains GUI binary types (.exe, .app, .dmg, .AppImage)
      OR primary_language IN {"Swift", "Objective-C", "C#"} AND has GUI patterns
      OR browser-extension manifest present (manifest.json in extension shape)
      OR has terminal-emulator / shell-extension topic
   → desktop-application

5. agentic-platform
   IF (server-side patterns: Dockerfile + WebSocket/HTTP server)
      AND (CLI binary present OR npm/cargo bin entry)
      AND multi-language repo (>2 primary languages with substantial code)
   → agentic-platform

6. web-application
   IF Dockerfile + web-server pattern
      AND no separate CLI distribution
      AND distribution_channels suggests self-host
   → web-application

7. cli-binary
   IF executable_files contains CLI binaries (no GUI)
      AND releases.entries provide platform binaries (homebrew/winget/distro)
   → cli-binary

8. library-package
   IF dependencies.manifest_files indicate package-publish (package.json with bin entry,
      pyproject.toml, Cargo.toml [lib], gemspec)
      AND no standalone executable
      AND no GUI
   → library-package

9. specialized-domain-tool
   IF none of the above match cleanly
      AND catalog_metadata.shape contains domain-keyword (ML, EDA, parser, etc.)
   → specialized-domain-tool

10. Fallback
   → other (with confidence="low", matched_rule="catch-all")
```

**Cross-shape modifier helpers** (called inside `classify_shape()`):

```python
def _detect_reverse_engineered(form) -> bool:
    """README disclaimer phrases ('unofficial', 'reverse-engineered',
    'ToS', 'this client is not affiliated'). Topics check too."""

def _detect_privileged_tool(form) -> bool:
    """Tool runs with elevated permissions: sudo in install scripts,
    kernel module, system daemon, terminal emulator handling SSH keys,
    keyboard/input device driver, browser extension with broad permissions,
    shell extender. Heuristic over executable_files + topics + dangerous
    primitives."""
```

**Validation requirement (Phase 3):** `classify_shape()` runs against all 12 V1.2 catalog scan bundles. Output must match the table in §3 (12/12 expected categories). If any miss, the heuristic needs adjustment before the rule table can rely on it. This is a blocker for Phase 3 implementation.

---

## §5 Rule Table — Cell Calibration

Each rule has: ID, target cell(s), trigger condition, output color, short_answer template key, confidence label, rationale.

### Q1 — "Does anyone check the code?"

#### RULE-1 — Q1 governance-floor softener (FIRM)

- **Trigger:** `signals.has_codeowners AND signals.has_ruleset_protection AND signals.rules_on_default_count > 0`
- **Output:** Q1 = amber (was: red via current rule's solo-maintainer floor)
- **short_answer_template:** `q1.amber.governance_present` → "Partly — formal governance present (CODEOWNERS + ruleset + rules-on-default), but {{`is_solo_maintained` ? "concentration risk remains" : "review-rate signal alone is below threshold"}}."
- **Confidence:** firm (audit: 2/12 scans manually overridden today match this exact pattern; ghostty + kamal).
- **Rationale:** the cell asks "does anyone check the code?" — when 3 governance gates are formally present, the answer is "yes, with caveats," not "no."

#### RULE-2 — Q1 review-rate softener (FIRM)

- **Trigger:** `signals.formal_review_rate >= 30 OR signals.any_review_rate >= 60`
- **Output:** Q1 = amber (was: red if other Q1 trips fire)
- **short_answer_template:** `q1.amber.review_rate_present` → "Partly — {{`formal_review_rate`}}% formal review on the last {{`pr_sample_size`}}-PR sample is above the median for solo-maintained OSS, but no structural enforcement gate."
- **Confidence:** firm (audit: WLED at 41% formal review currently sits at Q1=red — clearly miscalibrated).
- **Rationale:** when the maintainer voluntarily reviews PRs at meaningful rate, the cell answer is "yes, in practice," not "no."

#### RULE-3 — Q1 shape-aware floor (LOWER-CONFIDENCE)

- **Trigger:** `shape.category == "agent-skills-collection" OR shape.is_solo_maintained AND shape.is_privileged_tool == False`
- **Output:** Q1 = amber (was: red on bare governance-floor trip)
- **short_answer_template:** `q1.amber.shape_appropriate` → "Typical for {{`shape.category`}} — solo OSS without formal review gate, but {{`is_privileged_tool ? "tool surface limited" : "no kernel/sudo surface"`}}."
- **Confidence:** **lower** — n=2 evidence (kamal already covered by RULE-1; ghostty also covered by RULE-1). Owner flagged: "include in design but flag as lower-confidence than 1 and 2."
- **Rationale:** acknowledges that shape moderates the meaning of "no formal review." But because RULE-1 + RULE-2 cover most of the same ground, RULE-3's marginal effect may be small. Worth implementing for cases where neither RULE-1 nor RULE-2 fires but the shape clearly carries the OSS-default trust pattern.

### Q3 — "Do they tell you about problems?"

#### RULE-4 — Q3 sample-floor (HIGHEST-VALUE)

- **Trigger:** `signals.repo_age_days < 180 AND signals.total_merged_lifetime < 5`
- **Output:** Q3 = amber (was: red on bare no-SECURITY.md + no-advisories trip)
- **short_answer_template:** `q3.amber.sample_floor` → "Project too young/small to grade — {{`repo_age_days`}}d old with {{`total_merged_lifetime`}} lifetime merged PRs. No SECURITY.md but no opportunity to use one yet."
- **Confidence:** firm — directly addresses the skills case + future young-repo scans.
- **Rationale:** Q3 currently penalizes absence-of-disclosure-machinery as "No," but on a 3-month-old repo with 1 PR, there's no factual basis for inferring suppression. The honest answer at sample-floor is "amber/insufficient evidence," not "red/No." This is the single highest-leverage rule per audit + owner agrees.

#### RULE-5 — Q3 ruleset-as-disclosure floor (HYGIENE)

- **Trigger:** `signals.has_ruleset_protection AND signals.published_advisory_count > 0`
- **Output:** Q3 = amber (was: amber already in current rule, but explicit codification)
- **short_answer_template:** `q3.amber.ruleset_disclosed` → "Partly — {{`published_advisory_count`}} GHSA advisories published + ruleset-based disclosure flow, but no SECURITY.md naming a private channel."
- **Confidence:** firm (already produces amber in current rules; this rule documents why).
- **Rationale:** owner noted RULE-5 is "more of a documentation exercise" — including for hygiene. Makes the trip condition explicit so future audits can reason about it.

### Q4 — "Is it safe out of the box?"

#### RULE-6 — Q4 auto-fire extension (FIRM)

- **Trigger:** `signals.has_critical_on_default_path` is True when ANY of:
  - `dangerous_primitives.deserialization.hit_count >= 3 AND tool_loads_user_files` (existing V13-3 C5 — DON'T regress)
  - `dangerous_primitives.cmd_injection.hit_count >= 1 AND tool_loads_user_files` (NEW)
  - `dangerous_primitives.exec.hit_count >= 1 AND has_unverified_install_path` (NEW)
- **Output:** Q4 = red (auto-fire; was: amber via current advisory)
- **short_answer_template:** `q4.red.exec_pattern` → "No — default path executes user-provided data through {{`primary_pattern`}} ({{`hit_count`}} hits in {{`top_file`}})."
- **Confidence:** firm — extends a proven V13-3 pattern.
- **Rationale:** Q4=red is the actual verdict-discriminator (audit §9 Observation 3) but the current Phase 3 rule never reaches red — every Q4=red has been a Phase 4 LLM override. This rule moves the override into the rule table for the patterns we know well.

#### RULE-7 — Q4 firmware-default-no-auth + CORS-wildcard (n=1 CANDIDATE)

- **Trigger:** `shape.category == "embedded-firmware" AND (has_no_auth_default OR has_cors_wildcard)`
- **Output:** Q4 = red
- **short_answer_template:** `q4.red.firmware_no_auth` → "No — factory-default install has no authentication{{` and CORS wildcard` if cors_wildcard else ``}}; any same-network endpoint controls the device."
- **Confidence:** **n=1 candidate** — only WLED matches today. Promote to firm when n≥2.
- **Promotion gate:** "activates when a second confirming scan enters the catalog" (per owner's RULE-7/8/9 instruction).
- **Dependency:** requires V12x-11 harness work to detect the no-auth + CORS-wildcard signals reliably.

#### RULE-8 — Q4 install-doc URL TLD-deviation (n=1 CANDIDATE)

- **Trigger:** install-doc URL has TLD-deviation pattern (e.g., `chrome.google.cm` instead of `chrome.google.com`)
- **Output:** Q4 = red
- **short_answer_template:** `q4.red.url_typosquat` → "No — install documentation links to a typosquatted URL ({{`detected_url`}} — note `{{`tld_deviation`}}`)."
- **Confidence:** **n=1 candidate** — only browser_terminal matches today.
- **Promotion gate:** n≥2 confirming scans.
- **Dependency:** requires V12x-7 harness work to scan README install commands for URL typosquats.

#### RULE-9 — Q4 reverse-engineered-platform-API library (n=1 CANDIDATE)

- **Trigger:** `shape.category == "library-package" AND shape.is_reverse_engineered AND README contains platform-name + ToS-disclaimer language`
- **Output:** Q4 = red
- **short_answer_template:** `q4.red.reverse_engineered` → "No — library reverse-engineers {{`detected_platform`}} API; ToS violation + account-ban risk inherent to use."
- **Confidence:** **n=1 candidate** — only Baileys matches today.
- **Promotion gate:** n≥2 confirming scans.
- **Dependency:** requires V12x-12 harness work to detect README disclaimers + platform-name signals.

### Cross-cell — Authoring guard

#### RULE-10 — Critical-without-exploitability validator warning (NOT a verdict tier)

Per owner's instruction: implement as **validator-side warning**, not as a new verdict tier.

- **Where:** `docs/validate-scanner-report.py`, new check in `--form` mode (and possibly `--report` mode).
- **Trigger:** `phase_4b_computed.verdict.level == "Critical"` AND no finding has `severity == "Critical"` with `kind IN {"Vulnerability", "Supply-Chain"}`
- **Output:** authoring-time WARNING (not error): `"This scan would land Critical but has no exploitable code or supply-chain finding. Verify that the Critical verdict is justified by the governance-only signal pattern, OR add a more specific finding kind. Consider whether 'Caution' is more accurate."`
- **Effect:** validator exit 0 (no block) but emits the warning. Author decides whether the verdict is correct.
- **Confidence:** structural guard — no current scan triggers this, but the rule shape exists in the data (RULE-1 + RULE-2 + RULE-4 softening could in principle leave a Critical verdict floating without an exploitability anchor).
- **Why warning not error:** owner's framing — "adding verdict tiers has downstream formatting implications." Validator warning is the lighter-weight intervention; it surfaces the question without forcing a structural change.
- **Rationale:** prevents a future bad scan from shipping a Critical verdict that's actually a Caution. The validator is the natural place for "did the author make a judgment they should defend" guards.

---

## §6 New Cell Short-Answer Language

### Template-map approach

Each `(cell × color × shape × condition)` rule emits a **template key**, not the literal short_answer string. The renderer looks up the template from a new file at `docs/scorecard-templates.json` and fills in signal values.

**Why template-map:** keeps the rule table compact, lets short_answer phrasing iterate without rule-table churn, makes the LLM-override path clean (override drops the template_key, replaces with custom text + rationale).

**Schema:**

```json
{
  "q1.amber.governance_present": "Partly — formal governance present (CODEOWNERS + ruleset + rules-on-default), but {{concentration_qualifier}}.",
  "q1.amber.review_rate_present": "Partly — {{formal_review_rate}}% formal review on the last {{pr_sample_size}}-PR sample is above the median for solo-maintained OSS, but no structural enforcement gate.",
  "q1.amber.shape_appropriate": "Typical for {{shape.category}} — solo OSS without formal review gate, but {{privileged_qualifier}}.",
  "q1.red.no_governance": "No — no formal review gate, no CODEOWNERS, no branch protection, no rulesets. Solo direct-push pattern.",

  "q3.amber.sample_floor": "Project too young/small to grade — {{repo_age_days}}d old with {{total_merged_lifetime}} lifetime merged PRs. No SECURITY.md but no opportunity to use one yet.",
  "q3.amber.ruleset_disclosed": "Partly — {{published_advisory_count}} GHSA advisories published + ruleset-based disclosure flow, but no SECURITY.md naming a private channel.",
  "q3.red.no_disclosure": "No — no SECURITY.md, 0 published advisories, no documented private channel.",

  "q4.red.exec_pattern": "No — default path executes user-provided data through {{primary_pattern}} ({{hit_count}} hits in {{top_file}}).",
  "q4.red.firmware_no_auth": "No — factory-default install has no authentication{{cors_qualifier}}; any same-network endpoint controls the device.",
  "q4.red.url_typosquat": "No — install documentation links to a typosquatted URL ({{detected_url}} — note `{{tld_deviation}}`).",
  "q4.red.reverse_engineered": "No — library reverse-engineers {{detected_platform}} API; ToS violation + account-ban risk inherent to use.",
  "q4.amber.install_warns": "Partly — README explains the install path and lists what activates, but {{trust_qualifier}}.",
  "q4.green.verified": "Yes — install path is checksum-verified, source is a trusted distribution channel, no exec patterns on default path."
}
```

### Migration handling for existing scans

Catalog scans authored before this design have free-form short_answer text. Two approaches:

1. **Re-derive from rules** — Phase 5 re-render replaces existing short_answer with the template-derived version. Loses any LLM nuance; gains consistency.
2. **Preserve LLM text where override fired** — when a scan's existing cell color resulted from a Phase 4 override (override_reason is non-null), preserve the LLM short_answer. When the cell color matches what new rules would produce, regenerate from template.

**Recommendation:** approach 2. Keeps the override-explained content where the LLM's nuance was the right call; regenerates the OSS-default rows with calibrated text. Migration script is straightforward.

---

## §7 Scope Decision: Cells Only vs Cells + Finding Severities

### Why this is a question

Owner's "~90% programmatic" target implies programmaticizing **two** layers:
- **Cell colors** (Q1/Q2/Q3/Q4) — what this design covers
- **Finding severity assignment** (which findings are Critical vs Warning vs Info) — broader

The audit covered cells only. Finding severities are LLM-authored today (LLM picks "Critical" or "Warning" per finding). To get to ~90% programmatic on **scoring**, finding severities also need rule-driven derivation.

### What programmaticizing finding severities would require

- A finding-pattern catalog: each detectable signal pattern → finding template (kind + severity + threat_model + action_hint).
- A `compute_findings(form)` function that scans the harness data and emits finding entries.
- A way for the LLM to add narrative-only findings (synthesis observations) without claiming severity.
- Re-classification of existing 27 catalog findings against the new rules.
- More rigorous threat-model framing (since the LLM was carrying that judgment).

This is at minimum 2-3x the scope of cell calibration. It also deserves its own audit before design (what finding patterns exist in the catalog? what severity-driver signals are programmatically derivable?).

### Recommendation: cells in Phase 1, finding severities in Phase 1.5

- **Phase 1 (this design):** ship cell calibration. Audit-driven, lower-risk, owner-validated direction.
- **Phase 1.5 (after Phase 5 re-render shows cell calibration works):** scope a separate finding-severity audit + design. Start by classifying the 27 existing catalog findings into pattern buckets, see what's programmaticizable.
- **Effect on "90% programmatic":** Phase 1 alone moves cell calibration from ~80% manual (LLM-authoritative) to ~95% rule-driven. Finding severities stay LLM-authored at ~50% programmatic (some findings are mechanical, others are judgment). Combined post-Phase-1: maybe 70% programmatic on scoring overall, not 90%. Phase 1.5 closes the gap.

**Open for board / owner:** is Phase 1.5 in scope of this calibration push, or queued separately? The plan's Phase 3 implementation could extend to finding severities if owner+board want it now.

---

## §8 Migration Plan — Re-rendering 27 Catalog Scans

### Process (per back-to-basics-plan §Phase 5)

1. **Pre-tag:** `git tag pre-calibration-rerender HEAD` immediately before the re-render commit.
2. **For each of 27 form bundles in `docs/scan-bundles/*.json` and `docs/scan-bundles/*.md` (V2.4 era):**
   - Apply new rules → compute new cell colors + new short_answer templates
   - Compare to existing scan's cell colors + short_answers
   - Record the diff in `docs/calibration-rebuild-rerender-comparison.md`
3. **Re-render** the 12 V1.2 scans using new rules + new short_answer templates. The 15 V2.4 scans are NOT re-rendered (different schema; preserved as-is per OD-3 historical-bundle rule).
4. **Owner reviews** the comparison doc + signs off on each cell-color shift before commit.

### Expected diffs

Based on audit data, projected changes:

| Scan | Q1 shift | Q3 shift | Q4 shift | Verdict shift? |
|---|---|---|---|---|
| ghostty | red → amber (RULE-1) | unchanged | unchanged | none — verdict is finding-severity-driven |
| Kronos | unchanged (privileged + Critical findings) | unchanged | red → red (RULE-6 auto-fires; matches existing override) | none |
| kamal | red → amber (RULE-1) | unchanged | unchanged | none |
| Xray-core | unchanged | unchanged | unchanged (Q2 override stays) | none |
| browser_terminal | unchanged | unchanged | red → red (RULE-8 if promoted; otherwise stays via override) | none |
| wezterm | unchanged | unchanged | unchanged (zero override scan) | none |
| QuickLook | unchanged | red → amber (RULE-4 doesn't fire — too old; stays red? — verify) | unchanged | none |
| kanata | red → amber (RULE-2: 44% formal review) | unchanged | unchanged | none |
| freerouting | unchanged | unchanged | red → red (RULE-6 auto-fires; matches existing override) | none |
| WLED | red → amber (RULE-2: 38% formal review) | unchanged | red → red (RULE-7 if promoted; otherwise stays via override) | none |
| Baileys | unchanged | unchanged | red → red (RULE-9 if promoted; otherwise stays via override) | none |
| skills | unchanged (no governance gates present) | red → amber (RULE-4 fires) | unchanged | none |

**Summary projections:**
- 4 cells flip Q1 red → amber (ghostty, kamal, kanata, WLED).
- 1 cell flips Q3 red → amber (skills).
- 0 verdicts shift (cell color doesn't drive verdict; finding severities do).
- 4 of ~10 current overrides eliminated (Q1 cases automated by RULE-1/RULE-2).
- 0-3 additional overrides eliminated by RULE-6 if Q4 auto-fire matches LLM judgment exactly.
- Remaining overrides if RULE-7/8/9 stay n=1: ~5 (the LLM-authored Q4 reds for shape-novel cases stay as overrides).

If projections hold: ~50% override reduction in this phase. Closer to the ~80% target after RULE-7/8/9 promote (which requires more wild scans).

### Acceptance criteria

- Owner signs off on the comparison doc.
- All 12 V1.2 re-renders pass `--report` validator + `--parity` zero-warning.
- Test suite passes (will need new tests; see §10).
- `--form` validator on each re-rendered bundle confirms override-explained gate still holds where overrides remain.

---

## §9 Open Questions for Board Review

1. **Shape-as-modifier architectural call** — agree with §2 reasoning, or prefer lookup-key / scoring-dimension?
2. **9-category enum scope** — too granular (collapse some)? too coarse (split some)? The 12-scan classification table in §3 is the empirical grounding.
3. **RULE-3 keep-or-drop** — owner flagged as lower-confidence (n=2 mostly covered by RULE-1). Worth keeping as documentation, or prune from design?
4. **RULE-7/8/9 promotion gates** — owner confirmed "n≥2 confirming scans." Board: agree, or different gate (e.g., "n≥2 + harness-side detection working" — since each rule depends on a harness V12x patch)?
5. **RULE-10 as validator warning vs verdict tier** — owner picked validator warning. Board: agree, or is the structural-protection use case strong enough to warrant a tier addition?
6. **Cell short_answer template-map** — per-cell-color-shape templates as proposed, or freer-form per-rule literal strings?
7. **Scope: cells only (Phase 1) or cells + finding severities (Phase 1+1.5)?** — see §7. Owner+board call.
8. **Migration approach** (preserve LLM text where override fired) — agree, or fully regenerate?
9. **Acceptance threshold for re-render** — what % override reduction counts as "calibration worked"? §8 projects ~50% with RULE-1/2/4/6; ~80% if 7/8/9 also promote. Setting an explicit gate avoids "well, it's better" hand-waving.

---

## §10 Implementation Sketch (Phase 3 preview — not part of this design's commit)

For board context only; Phase 3 will produce its own implementation plan.

### New `compute.py` surface

```python
from typing import NamedTuple

class ShapeClassification(NamedTuple):
    category: str
    is_reverse_engineered: bool
    is_privileged_tool: bool
    is_solo_maintained: bool
    confidence: str
    matched_rule: str

class CellEvaluation(NamedTuple):
    color: str
    short_answer_template_key: str
    template_vars: dict
    rule_id: str               # which rule fired (e.g. "RULE-1")
    auto_fire: bool            # was this an immediate trip vs base-table evaluation

def classify_shape(form: dict) -> ShapeClassification: ...
def evaluate_q1(signals: dict, shape: ShapeClassification) -> CellEvaluation: ...
def evaluate_q2(signals: dict, shape: ShapeClassification) -> CellEvaluation: ...
def evaluate_q3(signals: dict, shape: ShapeClassification) -> CellEvaluation: ...
def evaluate_q4(signals: dict, shape: ShapeClassification) -> CellEvaluation: ...
def compute_scorecard_cells_v2(form: dict) -> dict: ...  # orchestrator

# RULE-10 lives in validator, not compute:
def check_critical_without_exploitability(form: dict) -> list[str]:  # in validator
```

`compute_scorecard_cells()` (the existing function) becomes a backward-compat shim that calls `compute_scorecard_cells_v2()`.

### New tests

- `tests/test_classify_shape.py` — 12 V1.2 bundles → expected category. Plus modifier helper unit tests.
- `tests/test_calibration_rules.py` — per-rule fixture-based tests (constructed signal dicts → expected (color, rule_id)).
- `tests/test_calibration_regression.py` — load each of 12 V1.2 bundles → run new compute → assert produces a documented, owner-signed-off (color, rule_id) tuple.
- `tests/test_validator_critical_without_exploitability.py` — RULE-10 validator check.

Existing 414 tests must continue to pass. New tests target +30-50.

### Schema additions (minimal)

- `phase_3_advisory.scorecard_hints.<q>.rule_id` — string, optional. Records which rule fired (for traceability).
- `phase_4_structured_llm.shape_classification` — object with `{category, is_reverse_engineered, is_privileged_tool, is_solo_maintained, confidence, matched_rule}`. Computed by Phase 3, frozen by Phase 4 LLM (which may override `category` with explanation).

These are additive; no migration needed for V1.2 schema (round-trip stays clean if the new fields are absent — they're optional).

### Backward compatibility

Existing scan bundles validate against V1.2 schema unchanged. New helper functions are additive. The override mechanism on `phase_4_structured_llm.scorecard_cells.<q>` is unchanged — overrides still require rationale + computed_signal_refs + override_reason enum value.

---

## §11 Cross-references

- Predecessor: `docs/calibration-audit.md` (Phase 0 empirical baseline)
- Plan: `docs/back-to-basics-plan.md` § Phase 1 deliverable + § Phase 2 board review
- Existing telemetry: `docs/v12-wild-scan-telemetry.md`
- Existing compute logic to extend: `docs/compute.py::compute_scorecard_cells()`
- Existing rule references: `compute.py` SF1 patches docstring; V13-1 + V13-3 commits
- Validator (RULE-10 home): `docs/validate-scanner-report.py`
