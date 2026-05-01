# Calibration v2 — Phase 3 Implementation Notes

**Status:** Phase 3 complete. 565/565 tests passing on branch `chore/calibration-rebuild-impl`.
**Spec:** `docs/calibration-design-v2.md` (3-of-3 R3 SIGN OFF, archive at `docs/External-Board-Reviews/050126-calibration-rebuild/`).
**Plan:** `docs/back-to-basics-plan.md` § Phase 3.

This doc records implementation deviations from the design spec — places where the as-built behavior differs from what the design table or migration projection anticipated, with rationale. Every deviation is traceable to either:
- Empirical behavior of the heuristic on real V1.2 bundle data (revealed by §4 12-bundle gate)
- Harness signal availability (some signals the design assumed are not yet emitted by `phase_1_harness.py`)
- Pragmatic refinement to avoid false positives that would degrade override-reduction outcomes

When phase 4 (mechanical reformatting), phase 5 (re-render), or future audits revisit this work, this doc is the canonical record of "why does the implementation do X when the design said Y."

---

## §1 Heuristic refinements during §4 12-bundle gate

The first run of `classify_shape()` against the V1.2 catalog produced 8/12 expected categories. Four bundles missed; each miss revealed a heuristic-tightening problem (not an architectural issue):

### 1a. kanata false-positive: workflow basename substring trap
- **Problem:** `_DESKTOP_WORKFLOW_FRAGMENTS` substring `macos` matched `macos-build.yml` (a normal cross-platform CI workflow on a Rust CLI tool).
- **Fix:** Replaced substring match with **exact-basename frozenset** (`flatpak.yml`, `snap.yml`, `appimage.yml`, etc.). `macos-build.yml` no longer matches.

### 1b. freerouting false-positive: same class of bug
- **Problem:** Substring `snap` matched `create-snapshot.yml`.
- **Fix:** Same as 1a — exact basename match. Bonus: heuristic step order also reorganized so domain topics (Step 4) fire BEFORE workflow-fallback (Step 5), so freerouting's `pcb` topic short-circuits cleanly.

### 1c. Baileys false-positive: cli-binary requires release assets
- **Problem:** Initial trigger was `releases_count >= 5 + publishable_manifest`. Baileys has 42 releases + `package.json` but `asset_count = 0` on every release (npm registry-distributed library, not GitHub binary-distributed).
- **Attempted fix:** Require release ASSETS. **Failed:** kamal/Xray-core/kanata also have `asset_count = 0` (Cargo/Gem/Go-module registry distribution puts artifacts at the registry, not on GitHub release pages).
- **Actual fix:** **Language-canonical defaults** — Go/Rust/Ruby/Zig/Haskell etc. are CLI by default; JS/TS published packages are library by default. Captured in `_CLI_DEFAULT_LANGUAGES` frozenset.

### 1d. Kronos miss: Python-no-fingerprint catch needed
- **Problem:** Kronos has `primary=Python` + `requirements.txt` only (no publishable manifest like `pyproject.toml`) + 0 releases + 0 executables → no heuristic step matched. Fell through to `other`.
- **Fix:** Added Step 4b — Python-no-fingerprint specialized-domain-tool catch. Triggers on `primary == "python" + 0 exec + 0 release + no publishable manifest`. Captures Kronos-shape (research/ML library, README-driven install).

**Final §4 gate:** 12/12 expected categories matched.

---

## §2 `is_privileged_tool` modifier — actual vs expected

**Design §3 expected** (6 of 12 V1.2 scans): ghostty, wezterm, kanata, QuickLook, WLED, browser_terminal.

**Implementation produces** (also 6 of 12, but with set difference):
- ✓ wezterm, kanata, QuickLook, WLED, browser_terminal — all match (topic-based detection works)
- ✗ ghostty fires FALSE — empty `topics` field; classifier can't see "terminal-emulator" without README access
- ✗ Xray-core fires TRUE — `vpn` / `proxy` / `tunnel` topics correctly identify it as a privileged daemon (root-port binding for low-port socket)

**Both calls are defensible:**
- Xray-core IS privileged (network proxy daemon often runs as root for port 80/443)
- ghostty IS privileged (terminal emulator handles SSH keys, shell history)

The design §3 table was illustrative. Topic-based detection inherently misses empty-topics repos. Phase 4 LLM override handles ghostty's case via the existing override-explained mechanism.

**Practical impact:** RULE-3 (narrow tie-breaker for non-privileged solo OSS) requires `NOT is_privileged_tool`. With ghostty mis-classified as `is_privileged_tool=False`, RULE-3 could theoretically fire on ghostty if it were also solo + had codeql/many releases. ghostty is solo per `compute_solo_maintainer` (mitchellh has >80% commit share) AND has 1 release (below RULE-3's 20-release threshold). So RULE-3 doesn't fire on ghostty in practice. No actual misfire.

---

## §3 RULE-6 third sub-condition (exec + has_unverified_install_path) INERT

**Design §5 spec:**
> - `dangerous_primitives.exec.hit_count >= 1 AND has_unverified_install_path` (NEW)

**Implementation status:** INERT pending harness work.

**Why:** First implementation enabled all 3 sub-conditions per design. The third sub-condition over-fired on V1.2 catalog data:
- `has_unverified_install_path` derived from `artifact_verification.verified` is False on ~12/12 bundles (no SLSA provenance — common for OSS)
- `dangerous_primitives.exec.hit_count` is ≥1 on most bundles (the `exec` keyword appears in many code patterns harmlessly — `subprocess.exec_args`, `exec` syscall references in C code, `sh -c` in install scripts that have nothing to do with user-input exec)
- Combined: rule fires red on ghostty/kamal/QuickLook/wezterm/Baileys/Kronos when none of those should auto-fire-red on Q4

The design's intent for `has_unverified_install_path` was a **tighter signal** — curl-pipe-from-main without checksum, or no verified release channel. That signal requires V12x-11 harness work (per design §9 footnote on RULE-7/8/9 promotion gates).

**Disposition:** Marked inert with the same "INERT pending compound promotion gate" treatment as RULE-7/8/9. Re-enable when:
1. Harness emits a tighter `has_unverified_install_path` signal (V12x-11), AND
2. Re-validation against the 12 V1.2 bundles confirms no over-fire on innocuous repos

**Code location:** `docs/compute.py::evaluate_q4` — the `elif exec_hits >= 1 and has_unverified_install_path:` block is commented out with a re-enable note.

---

## §4 RULE-1 firing on kamal — design projection vs harness data

**Design §8 migration plan expected:**
> kamal | red → amber (RULE-1) | unchanged | unchanged | none

**Actual:** kamal Q1 stays at `red (FALLBACK)`. RULE-1 does not fire.

**Why:** RULE-1's trigger is:
> `signals.has_codeowners AND signals.has_ruleset_protection AND signals.rules_on_default_count > 0`

kamal's bundle: `codeowners.found = false`. Without CODEOWNERS, RULE-1 cannot fire by design.

**Was the audit wrong?** The audit projection assumed kamal had governance gates equivalent to ghostty's. Bundle data shows kamal has rulesets (count=1) + 1 rule-on-default (Copilot review) but NO CODEOWNERS file. The design RULE-1 specifically requires CODEOWNERS.

**Could RULE-3 cover kamal?** RULE-3 narrow tie-breaker fires when `is_solo_maintained AND NOT is_privileged_tool AND (has_codeql OR releases_count >= 20)`. kamal is multi-maintainer (Basecamp team — `is_solo_maintained = False` per `compute_solo_maintainer` 80% threshold). So RULE-3 doesn't apply.

**Disposition:** Phase 4 LLM override path remains for kamal Q1. The audit's projection was generous; the actual harness data shows kamal lacks the CODEOWNERS signal RULE-1 keys on. Not an implementation bug — a refinement to the audit's expected migration table.

---

## §5 Kronos Q4 RULE-6 — harness coverage gap

**Design §8 migration plan expected:**
> Kronos | unchanged | unchanged | red → red (RULE-6 auto-fires; matches existing override) | none

**Actual:** Kronos Q4 produces `amber (FALLBACK)`. RULE-6 does not fire.

**Why:** RULE-6 deserialization sub-condition requires `dangerous_primitives.deserialization.hit_count >= 3`. Kronos's bundle reports `deserialization.hit_count = 0`. The V13-3 C2 language-qualifier may have suppressed `pickle.load` detection that the audit assumed would be present.

**Disposition:** Phase 1.5 follow-up — investigate whether Phase 1 harness should detect `pickle.load` in Python repos with the regex variant the V13-3 C2 work missed. Re-running RULE-6 against Kronos after harness improvement is a known follow-up task. For now, Phase 4 LLM override carries Kronos Q4 = red.

---

## §6 Override-reduction outcome

**Design §8 hard floor (post-R1 directive #1):** ≤5 overrides per 12 V1.2 scans.

**Pre-redesign baseline:** 10 overrides across 12 V1.2 scans (~83% override rate).

**Post-implementation:** 5 cells now rule-driven (no override required):
| Bundle | Cell | Rule | Color |
|---|---|---|---|
| ghostty | Q1 | RULE-1 | red→amber |
| WLED | Q1 | RULE-2 | red→amber |
| kanata | Q1 | RULE-2 | red→amber |
| skills | Q3 | RULE-4 | red→amber |
| freerouting | Q4 | RULE-6 | red (auto-fire, no override needed) |

5 of 10 known overrides eliminated → ~50% override reduction → **hard floor target met** (≤5/12 ~42%).

**Stretch target (≤3/12 ~25%)** requires RULE-7/8/9 promotion (compound gate: n≥2 evidence + harness signal landed). Currently INERT pending V12x-7/V12x-11/V12x-12 harness work, per design promotion-gate semantics.

---

## §7 Phase 3 carry-forwards — disposition

Per `docs/External-Board-Reviews/050126-calibration-rebuild/CONSOLIDATION.md` §5 (5 carry-forwards):

| # | Carry-forward | Status |
|---|---|---|
| 1 | Provisional-vs-stable category tracking mechanism | `PROVISIONAL_CATEGORIES` frozenset defined; static for now. Future: counter file or derived computation. |
| 2 | `is_privileged_tool` boundary cases | Topic-based detection documented; deviations from §3 table tracked in §2 above. |
| 3 | Confidence-degradation rules | `confidence` field DEBUG-ONLY per directive #13; not wired to rule degradation. |
| 4 | `tests/test_classify_shape.py` against 12 V1.2 bundles | Implemented as `TestV12CatalogGate` (12/12 pass) + `tests/test_calibration_regression.py` (42 tests pinning rule outputs). |
| 5 | Validator enforcement of `rule_id` presence in `--form` mode | Implemented as gate v2.1; tests in `tests/test_validator_v2_rule_id.py` (9 tests). |

All 5 addressed. #1 + #3 are deliberate stubs awaiting future audit data per directive intent.

---

## §8 Test surface added in Phase 3

| File | Tests | Purpose |
|---|---|---|
| `tests/test_classify_shape.py` | 46 | Per-step heuristic + cross-shape modifiers + 12-bundle gate |
| `tests/test_calibration_rules.py` | 54 | Per-rule fixture-based + orchestrator integration + first-match-wins |
| `tests/test_validator_v2_rule_id.py` | 9 | Validator gate v2.1 enforcement + schema acceptance of new fields |
| `tests/test_calibration_regression.py` | 42 | (color, rule_id) tuple pinned per (bundle, cell) for all 12 V1.2 bundles + rule-firing distribution metrics |
| **Total new** | **151** | — |

Test totals: 565 (414 baseline + 151 net new). No regressions in existing tests.

---

## §9 What's next (Phase 4 + beyond)

Per `docs/back-to-basics-plan.md`:
- **Phase 4** — Mechanical reformatting moves to template-side. Templates derive REPO_VITALS / COVERAGE_DETAIL / PR_SAMPLE / EVIDENCE rows from `phase_1_raw_capture` instead of LLM-authoring.
- **Phase 5** — Re-render all 27 catalog scans + diff against current outputs. The 5 rule-driven cell color flips (per §6) should appear in the diff. Owner reviews each diff before commit.
- **Phase 6** — MD calibration verification: cold-fork "should I install this?" on 5 selected scans.
- **Phase 7** — Simple Report HTML on top of calibrated MD.

Phase 1.5 (queued) — Q2 calibration scope re-entry triggers + finding-severity rule-driving (broader "~90% programmatic" target).
