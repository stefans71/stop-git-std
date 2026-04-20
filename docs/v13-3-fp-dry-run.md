# V13-3 C20 — Harness-Patch Dry-Run on 11 V1.2 Bundles

**Purpose:** V13-3 C20 landing gate (per 042026-v13-3-comparator-calibration board review). Apply the proposed C2 (language-qualifier regex) + C5 (Q4 auto-fire) + C18 (`derive_tool_loads_user_files` helper) to the 11 historical V1.2 scan bundles. Verify zero false-positive auto-fires on the existing corpus before the V1.2.x landing commits.

**Date:** 2026-04-20.
**Scope:** Entries 16-26 (V1.2 wild scans). V2.4-era bundles out of scope per C16.
**HEAD:** `c558b9f`.

---

## 1. Method

For each of the 11 V1.2 scan bundles at `docs/board-review-data/scan-bundles/`:

1. **C2 simulation:** Re-count `dangerous_primitives.deserialization.hit_count` against the post-C2 regex. The C2 change drops the bare `deserialize` keyword from the pattern; unsafe-specific method tokens (`pickle.load`, `ObjectInputStream`, `Marshal.load`, `yaml.load`, `unserialize`, `marshal.load`, `joblib.load`, `dill.load`) are preserved. Snippet-level inspection of each stored hit determines post-C2 retention.
2. **C18 derivation:** Apply `derive_tool_loads_user_files(readme_text=None, repo_metadata=<bundle-meta>)`. Bundle-stored README text is NOT available (harness does not persist full README); topic-list is the available input.
3. **C5 derivation:** Apply `derive_q4_critical_on_default_path_from_deserialization(simulated_dp, repo_metadata=...)` with post-C2 hit_count as input.
4. **Compare to bundle's original `override_reason`** — would the auto-fire collapse the override?

## 2. Results

| Entry | Repo | deser pre | deser post-C2 | loads_user_files | auto_fire | orig override_reason | outcome |
|---|---|---|---|---|---|---|---|
| 16 | ghostty | 0 | 0 | False | False | (no Q4 override) | ✅ no change |
| 17 | Kronos | 0 | 0 | False | False | harness_coverage_gap | ⚠️ see §3.1 |
| 18 | kamal | 0 | 0 | False | False | (no Q4 override) | ✅ no change |
| 19 | Xray-core | 2 | 0 | False | False | (no Q4 override) | ✅ no change |
| 20 | browser_terminal | 0 | 0 | False | False | harness_coverage_gap (typosquat, unrelated class) | ✅ no change; not in scope of C5 |
| 21 | wezterm | 9 | 0 | False | False | (zero-override scan) | ✅ no FP — see §3.2 |
| 22 | QuickLook | 1 | 0 | False | False | (zero-override scan) | ✅ no FP |
| 23 | kanata | 1 | 0 | False | False | (zero-override scan) | ✅ no FP |
| 24 | freerouting | 35 | 30 | True | **True** | signal_vocabulary_gap | **✅ override would COLLAPSE** |
| 25 | WLED | 19 | 0 | False | False | signal_vocabulary_gap (CORS pattern, unrelated class) | ✅ ArduinoJson FP correctly suppressed; not in scope of C5 |
| 26 | Baileys | 2 | 0 | False | False | signal_vocabulary_gap (reverse-eng, unrelated class) | ✅ no change; not in scope of C5 |

**False-positive count: 0.**
**True-positive count: 1 (freerouting).**

## 3. Notable interpretations

### 3.1 Kronos (entry 17) — production re-scan would fire where bundle doesn't

Kronos was scanned before the V13-1 V1.2.x `pickle.loads?` widening landed. Its stored `dangerous_primitives.deserialization.hit_count = 0` is a pre-widening artifact — the regex at scan time matched only `pickle.loads` (plural) and missed the actual `pickle.load(f)` call at `finetune/dataset.py:42`.

Counterfactually, a production re-scan of Kronos today (with current V1.2.x + V13-3 C2 regex) would match the pickle.load call. Combined with a live README-text read at scan time (the harness's Phase 1 step reads README via `gh api`), the tool-loads-user-files condition would likely fire on phrases like "load a pretrained checkpoint" or topic additions. C5 auto-fire would then activate, collapsing the Kronos Q4 override.

This is the intended behavior: Kronos's original override reason was `harness_coverage_gap` — the harness missed pickle.load. Both fixes (V13-1 pickle.loads? widening + V13-3 C5 auto-fire) were needed to collapse this override. The historical bundle doesn't reflect this post-state per OD-3 (frozen historical bundles).

### 3.2 wezterm zero-override preserved (9 pre → 0 post)

wezterm had 9 bundle hits that matched the broad pre-C2 regex, all via the bare `deserialize` keyword in Rust serde-ecosystem code. Post-C2, all 9 are suppressed (correctly — serde's `deserialize` is safe format parsing, not RCE class). wezterm was a zero-override scan at the time; post-C2 it remains zero-override with cleaner signals.

### 3.3 freerouting (entry 24) — the primary intended fire

The freerouting bundle's 35 deserialization hits map to:
- 30 `ObjectInputStream` imports/usage calls across board/, gui/, interactive/, rules/ packages (matched by unsafe-specific token in post-C2 regex)
- 5 matches via generic `deserialize` keyword (dropped by C2)

Post-C2 hit_count = 30. Topics include `pcb`, `pcb-design`, `autorouter` — `derive_tool_loads_user_files` returns True. Threshold (default 3) satisfied. **C5 auto-fire activates → `q4_has_critical_on_default_path = True` without Phase 4 authoring.**

The Phase 3 advisory for freerouting Q4 would now match Phase 4's red judgment directly. The historical override (`signal_vocabulary_gap`) would not be needed on a re-scan.

### 3.4 WLED (entry 25) — 19-FP correctly suppressed

WLED's 19 deserialization hits were all `deserializeJson` calls from the ArduinoJson library — SAFE JSON parsing, not RCE class. Post-C2, every one of these is suppressed (bare `deserialize` keyword dropped, and ArduinoJson's method name doesn't match any unsafe-specific token). Hit count drops to 0 → C5 auto-fire correctly does NOT activate.

The WLED Q4 override was for a different class (CORS wildcard + default-no-auth, not deserialization). That override remains authored-by-Phase-4 per OD-3 historical-bundle preservation; C5 has nothing to do with CORS-pattern overrides.

### 3.5 Entries with unrelated override classes (20, 25, 26)

browser_terminal Q4 override (`harness_coverage_gap`) was for a typosquat URL in install docs — out of C5 scope.
WLED Q4 override was firmware-default-no-auth + CORS wildcard — out of C5 scope (would be addressed by V1.3 Priority 1b C6, deferred).
Baileys Q4 override was reverse-engineered-API category — out of C5 scope (would be addressed by V1.3 Priority 1c C7, deferred).

C5 is narrowly scoped to deserialization-class critical-on-default-path surfaces. The other Q4 override classes stay on Phase 4 authoring until their respective V1.3 items land.

## 4. Verdict

**Gate PASS.** C5 + C2 + C18 produce:
- 1 true-positive fire (freerouting) — collapses an existing override
- 0 false-positive fires (WLED's 19 ArduinoJson calls are correctly suppressed; wezterm's 9 serde calls likewise)
- 0 regressions on zero-override scans

V1.2.x landing cleared for commit pending Codex code-review.
