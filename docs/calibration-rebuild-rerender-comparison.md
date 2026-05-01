# Calibration v2 rerender — comparison report

**Phase 5 of `docs/back-to-basics-plan.md` — owner-review gate before Phase 5 commit 1.**

Bundles re-evaluated: **12 V1.2 catalog scans (entries 16-27)**.

Per cell, the table shows: `old_advisory→new_advisory (rule_id) | LLM=phase_4_color [override: reason if any]`. Color codes: `r`=red, `a`=amber, `g`=green, `—`=not present.

## Headline findings

- **Verdict shifts:** 0 of 12 (verdict reads `compute_verdict(findings)`; findings unchanged in this rerender, so verdicts are stable by construction).
- **Advisory shifts:** 10 cell(s) across 7 entries — calibration v2 advisory differs from legacy advisory.
- **Redundant overrides:** 3 cell(s) — Phase 4 LLM previously override-explained but new advisory now matches the LLM color naturally (rule-driven). These are calibration wins.

## Per-entry comparison (entries 16-27)

| # | Repo | Shape | Verdict (old→new) | Cell shifts (Q1 / Q2 / Q3 / Q4) | Summary |
|---|---|---|---|---|---|
| 16 | ghostty-org/ghostty (wild) | `desktop-application` | **Caution** | red→amber (RULE-1) | LLM=amber [override: signal_vocabulary_gap] · green=green (FALLBACK) | LLM=green · amber→red (FALLBACK) | LLM=amber · amber=amber (FALLBACK) | LLM=amber | 2 advisory shifts: Q1, Q3; 1 override now redundant (Q1) |
| 17 | shiyu-coder/Kronos (wild) | `specialized-domain-tool` | **Critical** | red=red (FALLBACK) | LLM=red · amber→red (FALLBACK) | LLM=red [override: signal_vocabulary_gap] · red=red (FALLBACK) | LLM=red · amber=amber (FALLBACK) | LLM=red [override: harness_coverage_gap] | 1 advisory shift: Q2; 1 override now redundant (Q2) |
| 18 | basecamp/kamal (wild) | `cli-binary` | **Caution** | red=red (FALLBACK) | LLM=amber [override: signal_vocabulary_gap] · green=green (FALLBACK) | LLM=green · amber→red (FALLBACK) | LLM=amber · amber=amber (FALLBACK) | LLM=amber | 1 advisory shift: Q3 |
| 19 | XTLS/Xray-core (wild) | `cli-binary` | **Critical** | red=red (FALLBACK) | LLM=red · red=red (FALLBACK) | LLM=amber [override: threshold_too_strict] · amber=amber (FALLBACK) | LLM=amber · amber=amber (FALLBACK) | LLM=amber | no advisory shift; no redundant overrides |
| 20 | BatteredBunny/browser_terminal (wild) | `desktop-application` | **Critical** | red=red (FALLBACK) | LLM=red · green=green (FALLBACK) | LLM=green · red=red (FALLBACK) | LLM=red · amber=amber (FALLBACK) | LLM=red [override: harness_coverage_gap] | no advisory shift; no redundant overrides |
| 21 | wezterm/wezterm (wild) | `desktop-application` | **Caution** | red=red (FALLBACK) | LLM=red · red=red (FALLBACK) | LLM=red · amber→red (FALLBACK) | LLM=amber · amber=amber (FALLBACK) | LLM=amber | 1 advisory shift: Q3 |
| 22 | QL-Win/QuickLook (wild) | `desktop-application` | **Caution** | red=red (FALLBACK) | LLM=red · green=green (FALLBACK) | LLM=green · red=red (FALLBACK) | LLM=red · amber=amber (FALLBACK) | LLM=amber | no advisory shift; no redundant overrides |
| 23 | jtroo/kanata (wild) | `cli-binary` | **Critical** | amber=amber (RULE-2) | LLM=amber · green=green (FALLBACK) | LLM=green · red=red (FALLBACK) | LLM=red · amber=amber (FALLBACK) | LLM=amber | no advisory shift; no redundant overrides |
| 24 | freerouting/freerouting (wild) | `specialized-domain-tool` | **Critical** | red=red (FALLBACK) | LLM=red · green=green (FALLBACK) | LLM=green · amber→red (FALLBACK) | LLM=amber · amber→red (RULE-6) | LLM=red [override: signal_vocabulary_gap] | 2 advisory shifts: Q3, Q4; 1 override now redundant (Q4) |
| 25 | wled/WLED (wild) | `embedded-firmware` | **Critical** | red→amber (RULE-2) | LLM=red · red=red (FALLBACK) | LLM=red · amber→red (FALLBACK) | LLM=amber · amber=amber (FALLBACK) | LLM=red [override: signal_vocabulary_gap] | 2 advisory shifts: Q1, Q3 |
| 26 | WhiskeySockets/Baileys (wild) | `library-package` | **Critical** | red=red (FALLBACK) | LLM=red · red=red (FALLBACK) | LLM=red · red=red (FALLBACK) | LLM=red · amber=amber (FALLBACK) | LLM=red [override: signal_vocabulary_gap] | no advisory shift; no redundant overrides |
| 27 | mattpocock/skills (wild) | `agent-skills-collection` | **Caution** | red=red (FALLBACK) | LLM=red · green=green (FALLBACK) | LLM=amber [override: missing_qualitative_context] · red→amber (RULE-4) | LLM=red · amber=amber (FALLBACK) | LLM=amber | 1 advisory shift: Q3 |

## Per-entry detail

### Entry 16 — ghostty-org/ghostty (wild)

- **Shape:** `desktop-application` (confidence=medium, matched_rule='desktop-packaging workflows (flatpak/snap/AppImage/dmg)')
- Solo-maintained: True · Privileged-tool: False · Reverse-engineered: False
- Verdict (Phase 4b): old=`Caution` new=`Caution`
- Bundle: `docs/scan-bundles/ghostty-dcc39dc.json`
- Output: `docs/scans/catalog/GitHub-Scanner-ghostty-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `amber` | `RULE-1` | `amber` | signal_vocabulary_gap | advisory red→amber; LLM override now redundant (rule-driven match) |
| Q2 (fix) | `green` | `green` | `FALLBACK` | `green` | — | unchanged advisory (green); LLM aligned (no override needed) |
| Q3 (disclose) | `amber` | `red` | `FALLBACK` | `amber` | — | advisory amber→red; LLM at amber (override now required) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |

### Entry 17 — shiyu-coder/Kronos (wild)

- **Shape:** `specialized-domain-tool` (confidence=medium, matched_rule='Python + no exec/release/publish-manifest (research/ML shape)')
- Solo-maintained: False · Privileged-tool: False · Reverse-engineered: False
- Verdict (Phase 4b): old=`Critical` new=`Critical`
- Bundle: `docs/scan-bundles/Kronos-67b630e.json`
- Output: `docs/scans/catalog/GitHub-Scanner-Kronos-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `amber` | `red` | `FALLBACK` | `red` | signal_vocabulary_gap | advisory amber→red; LLM override now redundant (rule-driven match) |
| Q3 (disclose) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `red` | harness_coverage_gap | unchanged advisory (amber); LLM override still required (harness_coverage_gap) |

### Entry 18 — basecamp/kamal (wild)

- **Shape:** `cli-binary` (confidence=high, matched_rule='ruby + >=5 releases + publishable manifest')
- Solo-maintained: False · Privileged-tool: False · Reverse-engineered: False
- Verdict (Phase 4b): old=`Caution` new=`Caution`
- Bundle: `docs/scan-bundles/kamal-6a31d14.json`
- Output: `docs/scans/catalog/GitHub-Scanner-kamal-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `amber` | signal_vocabulary_gap | unchanged advisory (red); LLM override still required (signal_vocabulary_gap) |
| Q2 (fix) | `green` | `green` | `FALLBACK` | `green` | — | unchanged advisory (green); LLM aligned (no override needed) |
| Q3 (disclose) | `amber` | `red` | `FALLBACK` | `amber` | — | advisory amber→red; LLM at amber (override now required) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |

### Entry 19 — XTLS/Xray-core (wild)

- **Shape:** `cli-binary` (confidence=high, matched_rule='go + >=5 releases + publishable manifest')
- Solo-maintained: False · Privileged-tool: True · Reverse-engineered: False
- Verdict (Phase 4b): old=`Critical` new=`Critical`
- Bundle: `docs/scan-bundles/Xray-core-b465036.json`
- Output: `docs/scans/catalog/GitHub-Scanner-Xray-core-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `red` | `red` | `FALLBACK` | `amber` | threshold_too_strict | unchanged advisory (red); LLM override still required (threshold_too_strict) |
| Q3 (disclose) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |

### Entry 20 — BatteredBunny/browser_terminal (wild)

- **Shape:** `desktop-application` (confidence=high, matched_rule='desktop topic (terminal/extension/quicklook/etc.)')
- Solo-maintained: False · Privileged-tool: True · Reverse-engineered: False
- Verdict (Phase 4b): old=`Critical` new=`Critical`
- Bundle: `docs/scan-bundles/browser_terminal-9a77c4a.json`
- Output: `docs/scans/catalog/GitHub-Scanner-browser_terminal-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `green` | `green` | `FALLBACK` | `green` | — | unchanged advisory (green); LLM aligned (no override needed) |
| Q3 (disclose) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `red` | harness_coverage_gap | unchanged advisory (amber); LLM override still required (harness_coverage_gap) |

### Entry 21 — wezterm/wezterm (wild)

- **Shape:** `desktop-application` (confidence=high, matched_rule='desktop topic (terminal/extension/quicklook/etc.)')
- Solo-maintained: True · Privileged-tool: True · Reverse-engineered: False
- Verdict (Phase 4b): old=`Caution` new=`Caution`
- Bundle: `docs/scan-bundles/wezterm-577474d.json`
- Output: `docs/scans/catalog/GitHub-Scanner-wezterm-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q3 (disclose) | `amber` | `red` | `FALLBACK` | `amber` | — | advisory amber→red; LLM at amber (override now required) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |

### Entry 22 — QL-Win/QuickLook (wild)

- **Shape:** `desktop-application` (confidence=high, matched_rule='desktop topic (terminal/extension/quicklook/etc.)')
- Solo-maintained: False · Privileged-tool: True · Reverse-engineered: False
- Verdict (Phase 4b): old=`Caution` new=`Caution`
- Bundle: `docs/scan-bundles/QuickLook-0cda83c.json`
- Output: `docs/scans/catalog/GitHub-Scanner-QuickLook-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `green` | `green` | `FALLBACK` | `green` | — | unchanged advisory (green); LLM aligned (no override needed) |
| Q3 (disclose) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |

### Entry 23 — jtroo/kanata (wild)

- **Shape:** `cli-binary` (confidence=high, matched_rule='rust + >=5 releases + publishable manifest')
- Solo-maintained: False · Privileged-tool: True · Reverse-engineered: False
- Verdict (Phase 4b): old=`Critical` new=`Critical`
- Bundle: `docs/scan-bundles/kanata-1c496c0.json`
- Output: `docs/scans/catalog/GitHub-Scanner-kanata-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `amber` | `amber` | `RULE-2` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |
| Q2 (fix) | `green` | `green` | `FALLBACK` | `green` | — | unchanged advisory (green); LLM aligned (no override needed) |
| Q3 (disclose) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |

### Entry 24 — freerouting/freerouting (wild)

- **Shape:** `specialized-domain-tool` (confidence=high, matched_rule='domain topic (EDA/ML/document-conversion/etc.)')
- Solo-maintained: True · Privileged-tool: False · Reverse-engineered: False
- Verdict (Phase 4b): old=`Critical` new=`Critical`
- Bundle: `docs/scan-bundles/freerouting-c5ad3c7.json`
- Output: `docs/scans/catalog/GitHub-Scanner-freerouting-v12.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `green` | `green` | `FALLBACK` | `green` | — | unchanged advisory (green); LLM aligned (no override needed) |
| Q3 (disclose) | `amber` | `red` | `FALLBACK` | `amber` | — | advisory amber→red; LLM at amber (override now required) |
| Q4 (install) | `amber` | `red` | `RULE-6` | `red` | signal_vocabulary_gap | advisory amber→red; LLM override now redundant (rule-driven match) |

### Entry 25 — wled/WLED (wild)

- **Shape:** `embedded-firmware` (confidence=high, matched_rule='C/C++ primary + firmware/iot/esp topic')
- Solo-maintained: False · Privileged-tool: True · Reverse-engineered: False
- Verdict (Phase 4b): old=`Critical` new=`Critical`
- Bundle: `docs/scan-bundles/WLED-01328a6.json`
- Output: `docs/scans/catalog/GitHub-Scanner-WLED.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `amber` | `RULE-2` | `red` | — | advisory red→amber; LLM at red (override now required) |
| Q2 (fix) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q3 (disclose) | `amber` | `red` | `FALLBACK` | `amber` | — | advisory amber→red; LLM at amber (override now required) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `red` | signal_vocabulary_gap | unchanged advisory (amber); LLM override still required (signal_vocabulary_gap) |

### Entry 26 — WhiskeySockets/Baileys (wild)

- **Shape:** `library-package` (confidence=medium, matched_rule='publishable manifest, library-canonical shape')
- Solo-maintained: False · Privileged-tool: False · Reverse-engineered: True
- Verdict (Phase 4b): old=`Critical` new=`Critical`
- Bundle: `docs/scan-bundles/Baileys-8e5093c.json`
- Output: `docs/scans/catalog/GitHub-Scanner-Baileys.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q3 (disclose) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `red` | signal_vocabulary_gap | unchanged advisory (amber); LLM override still required (signal_vocabulary_gap) |

### Entry 27 — mattpocock/skills (wild)

- **Shape:** `agent-skills-collection` (confidence=high, matched_rule='rule-files present + no exec/manifest/release fingerprint')
- Solo-maintained: True · Privileged-tool: False · Reverse-engineered: False
- Verdict (Phase 4b): old=`Caution` new=`Caution`
- Bundle: `docs/scan-bundles/skills-b843cb5.json`
- Output: `docs/scans/catalog/GitHub-Scanner-skills.md` + `.html`

| Cell | Old advisory | New advisory | Rule | LLM Phase 4 | Override (old) | Shift summary |
|---|---|---|---|---|---|---|
| Q1 (review) | `red` | `red` | `FALLBACK` | `red` | — | unchanged advisory (red); LLM aligned (no override needed) |
| Q2 (fix) | `green` | `green` | `FALLBACK` | `amber` | missing_qualitative_context | unchanged advisory (green); LLM override still required (missing_qualitative_context) |
| Q3 (disclose) | `red` | `amber` | `RULE-4` | `red` | — | advisory red→amber; LLM at red (override now required) |
| Q4 (install) | `amber` | `amber` | `FALLBACK` | `amber` | — | unchanged advisory (amber); LLM aligned (no override needed) |

## Out-of-scope entries (1-15)

These remain unchanged on disk. Each row notes why the entry can't flow through V1.2 calibration v2 without separate re-authoring work.

| # | Repo | Reason |
|---|---|---|
| 1 | JuliusBrussee/caveman | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 2 | coleam00/Archon | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 3 | coleam00/Archon (re-run) | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 4 | pmndrs/zustand | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 5 | sharkdp/fd | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 6 | grapeot/gstack | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 7 | stefans71/stop-git-std/archon-board-review | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 8 | NousResearch/hermes-agent | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 9 | gitroomhq/postiz-app | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 10 | pmndrs/zustand (V2.4 re-scan) | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 11 | multica-ai/multica | V2.4 era hand-authored against V1.1 schema — no V1.2 form.json |
| 12 | pmndrs/zustand (Step G pilot) | V2.5-preview Step G pilot — phase_4 lives in V1.1 .board-review-temp/step-g-execution/zustand-step-g-form.json; would need V1.1→V1.2 schema upgrade + Phase 4 re-authoring |
| 13 | JuliusBrussee/caveman (Step G) | V2.5-preview Step G pilot — phase_4 lives in V1.1 .board-review-temp/step-g-execution/caveman-step-g-form.json; same migration cost |
| 14 | coleam00/Archon (Step G) | V2.5-preview Step G pilot — phase_4 lives in V1.1 .board-review-temp/step-g-execution/Archon-step-g-form.json; same migration cost |
| 15 | microsoft/markitdown (wild) | V1.2 form.json in .scan-workspaces/markitdown/ has empty phase_4_structured_llm.scorecard_cells (LLM cells were authored to .md sidecar bundle); re-rendering produces Q2 regression |

## Phase 6 input — gate 6.3 backlog

Calibration v2 advisory recompute created `phase_3_advisory.scorecard_hints` colors that differ from the original `phase_4_structured_llm.scorecard_cells` colors on the cells listed below. The original Phase 4 LLM judgments did not flag these as overrides because the legacy advisory matched the LLM color in v1; the v2 advisory differs.

Validator gate 6.3 (`--form` mode) requires `override_reason` + rationale + `computed_signal_refs` whenever `phase_3` advisory ≠ `phase_4` LLM color. These cells are now violating that gate at bundle level.

**Owner decision (Phase 5 sign-off): defer (path W).** Phase 5 completion criteria specify validator clean on **rendered files** (`--report` mode) and `--parity` zero-warning on MD/HTML pairs — both of which are clean. The `--form` validator on bundles is not in Phase 5 acceptance scope. Resolution belongs to Phase 6 where Phase 4 LLM cells are re-authored against the calibrated advisory.

**Resolution paths considered (selected: W):**
- **(X) Backfill** — write generic `override_reason` + rationale on each cell. Rejected: would require new enum value (`phase_5_advisory_shift`) and synthetic rationale that doesn't reflect real LLM judgment.
- **(Y) Re-author** — Phase 4 LLM regenerates affected cells against new advisory. Rejected: pulls Phase 6 work into Phase 5; out of scope.
- **(W) Defer** — selected. Document the backlog here as Phase 6 input; bundles carry the gate 6.3 violation as known state.

**Gate 6.3 backlog: 7 cell(s) across 6 entries.**

| # | Repo | Cell | New advisory | Rule | Phase 4 LLM | Direction |
|---|---|---|---|---|---|---|
| 16 | ghostty-org/ghostty (wild) | Q3 (disclose) | `red` | `FALLBACK` | `amber` | advisory `red` ≠ LLM `amber` (advisory now stricter) |
| 18 | basecamp/kamal (wild) | Q3 (disclose) | `red` | `FALLBACK` | `amber` | advisory `red` ≠ LLM `amber` (advisory now stricter) |
| 21 | wezterm/wezterm (wild) | Q3 (disclose) | `red` | `FALLBACK` | `amber` | advisory `red` ≠ LLM `amber` (advisory now stricter) |
| 24 | freerouting/freerouting (wild) | Q3 (disclose) | `red` | `FALLBACK` | `amber` | advisory `red` ≠ LLM `amber` (advisory now stricter) |
| 25 | wled/WLED (wild) | Q1 (review) | `amber` | `RULE-2` | `red` | advisory `amber` ≠ LLM `red` (LLM stricter than rule) |
| 25 | wled/WLED (wild) | Q3 (disclose) | `red` | `FALLBACK` | `amber` | advisory `red` ≠ LLM `amber` (advisory now stricter) |
| 27 | mattpocock/skills (wild) | Q3 (disclose) | `amber` | `RULE-4` | `red` | advisory `amber` ≠ LLM `red` (LLM stricter than rule) |

Phase 6 work item: re-author Phase 4 LLM cells for these 6 cells (or whatever subset the calibrated advisory genuinely changes the right answer for) and update `override_reason` where the LLM still wants to disagree with the rule-driven advisory.

## Owner sign-off

Phase 5 plan body specifies this comparison doc as the pre-commit gate. Owner reviews each verdict shift (zero in this rerender) and each advisory shift before Phase 5 commit 1 lands. Sign-off recorded in the conversation: 12-entry scope (entries 16-27) + (W) defer on gate 6.3 backlog.

---

_Generated by `docs/phase_5_build_comparison.py` from `docs/phase_5_comparison_data.json`._
