# Schema V1.2 Board Review — R3 Deliberation Brief (Stateless, Narrow)

**Review topic:** Scan-schema V1.2 design — co-scheduled D-7 (scorecard cell authority migration) + D-8 (schema hardening for harness output).

**Round:** R3 Deliberation. Narrowed scope. R1 Blind + R2 Consolidation are complete. Owner directives have resolved Q3 (shape) and OQ-2/OQ-3 (container topology). Six substantive items remain.

**Agent instruction:** You are STATELESS — read this brief as if you've never seen this project. R1 Blind and R2 Consolidation outputs are referenced by path (§8) — re-read them at the positions cited. Do not rely on prior memory. R2 was "respond to other agents' R1 positions and propose mergers or escalations." R3 is "close the six remaining substantive items with concrete resolutions — propose final answers that go into schema V1.2."

---

## 1. Context refresh (compressed)

`stop-git-std` is an LLM-driven GitHub repo security scanner. V2.5-preview is the JSON-first pipeline (schema + harness + compute + renderer). Schema V1.1 is being bumped to V1.2 to resolve D-7 (scorecard cell authority migration from `phase_3_computed` → `phase_4_structured_llm`; `compute.py` demoted to advisory) and D-8 (schema accepts richer fields emitted by `docs/phase_1_harness.py` natively).

Full R1 brief: `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/r1-brief.md`
R2 brief: `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/r2-brief.md`
All R1 + R2 outputs: `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/{pragmatist,codex,deepseek}-r{1,2}.md`

---

## 2. Owner directives — FIXED, not re-votable

Owner resolved two items by directive post-R2:

### D1. Q3 — V1.2 shape winner: **D8-B1 (harness-canonical, transformer deleted)**

Basis: 2/3 R2 majority (Pragmatist flipped from B2-scoped → B-merged ≈ B1; Codex held B1). DeepSeek flipped from B3 → B2-scoped on naming-prefix grounds only. Owner resolved on majority.

V1.2 schema adopts harness field names AND shapes natively:

- `archived` / `fork` / `default_branch` (not `is_archived` / `is_fork` / `default_branch_ref`)
- `dependabot_alerts` / `osv_lookups` (not `dependabot` / `osv_dev`)
- `reset` as epoch integer (not `reset_at` as ISO string) — or schema accepts both via union; R3 will not re-open this
- Nested per-family `dangerous_primitives.{exec, deserialization, network, ...}.files[].first_match.{line, snippet}` preserved
- `manifest_files: [{path, format}]` preserved as object list
- `symlinks_stripped: integer` (not bool)
- `distribution_channels_verified: {verified: int, total: int}` or string fraction (NOT bool)
- `windows_surface_coverage: string` status (NOT bool)
- Transformer (`.board-review-temp/markitdown-scan/transform_harness.py`) DELETED from V1.2 landing
- Bug P3-DOUBLE-ASSIGN auto-resolves via deletion

### D2. OQ-2 / OQ-3 — Scorecard advisory container topology: **new top-level `phase_3_advisory` with `scorecard_hints`**

Basis: Codex's R2 reasoning — keeps `phase_3_computed` owning its 7 deterministic outputs unambiguously, and aligns with SF1 CONSOLIDATION wording (which said `phase_3_advisory.scorecard_hints`). Pragmatist + DeepSeek preferred sibling sub-object inside `phase_3_computed`; owner resolved on topology-cleanness grounds.

V1.2 schema gets a NEW top-level phase:

- `phase_3_advisory` — non-authoritative, optional Phase 3 output surface
  - `scorecard_hints` — keyed object by canonical question ID (`does_anyone_check_the_code`, `do_they_fix_problems_quickly`, `do_they_tell_you_about_problems`, `is_it_safe_out_of_the_box`)
    - each key → `{color, short_answer, signals: [{id, value, ...}], $comment?}`
- `phase_3_computed.scorecard_cells` is DELETED (authority moves to Phase 4)
- Scorecard cell authority lives at `phase_4_structured_llm.scorecard_cells` — keyed object by canonical question ID
- `compute_scorecard_cells()` demoted to advisory; its output populates `phase_3_advisory.scorecard_hints`
- 7 other `compute.py` ops remain in `phase_3_computed` unchanged; Step 3b byte-for-byte equality retained for those 7
- Gate 6.3 changes from "cell-by-cell match" to "override-explained" (still TBD in R3 — see §3.1)

These two directives close Q3 and OQ-2/OQ-3. Do not re-open.

---

## 3. The six R3 items

Each item below needs a concrete resolution that goes into V1.2 schema + validator + operator guide. Propose your answer; flag R4 escalation only if consensus is genuinely out of reach.

### 3.1 Item A — Q5 residual: rationale-naming floor

**Context:** Q5 R2 converged on D7-G3+G4 (override_reason enum + validator enforcement + `computed_signal_refs` non-empty). One residual disagreement remains: does `rationale` text need to NAME a signal by string (Pragmatist's G2 floor), or is structural ref linkage sufficient (Codex's position)?

**Positions to date:**

- **Pragmatist R2:** keeps G2 floor ("`rationale` must name at least one listed signal by string"). Added G3 enum on top.
- **Codex R2:** "I would not require free-text mention of signal names if refs are machine-resolved; that is weaker than structural linkage." Structural `computed_signal_refs` non-empty + rationale present + length-floor is sufficient.
- **DeepSeek R2:** flipped to D7-G3; rationale not explicitly addressed.

**R3 question:** For V1.2 validator, when Phase 4 overrides advisory color:

- **(a)** `rationale` length-floor only (Codex) — validator checks length + `computed_signal_refs` non-empty + each ref resolves
- **(b)** `rationale` length-floor + must contain the string of at least one `computed_signal_refs` entry (Pragmatist) — adds an is-a-substring check
- **(c)** other / propose

Resolve (a), (b), or (c) with reasoning. Include a concrete validator pseudo-implementation for your choice (~5 lines).

### 3.2 Item B — OQ-6: migration script scope

**Context:** V1.2 ships with a one-time `migrate-v1.1-to-v1.2.py`. Which forms does it migrate?

**Positions to date:**

- **Pragmatist R2:** active/live-pipeline fixtures only (3 Step G: zustand / caveman / archon-subset). Rationale: minimal scope.
- **Codex R2:** active V1.1 fixtures PLUS archived Step G artifacts used in tests/audit. Update `provenance.json` `schema_version` where migrated. Do NOT bulk-touch V2.4 catalog entries.
- **DeepSeek R2:** all fixtures with entries in `tests/fixtures/provenance.json`, including `step-g-failed-artifact` tags. Rationale: test consistency.

**R3 question:** Which resolves?

- **(a)** Active fixtures only (3 files) — leaves archived Step G artifacts on V1.1 schema; tests that reference them either pin to V1.1 schema or get rewritten.
- **(b)** Active fixtures + archived Step G artifacts — regenerate if test imports; leave untouched if not.
- **(c)** All provenance.json entries — blanket migration.
- **(d)** Active fixtures only + explicit rule: "archived artifacts stay V1.1 and any test referencing them pins to V1.1 schema via explicit annotation."

Resolve with concrete rule and estimate of how many files migrate.

### 3.3 Item C — override_reason enum values (freeze)

**Context:** Q5 consensus requires `override_reason` as a categorical enum. Candidate vocabularies proposed in R1/R2:

- **Codex R1 C-3:** `threshold_too_strict / threshold_too_lenient / missing_qualitative_context / rubric_literal_vs_intent / other`
- **DeepSeek R1 C-2 (pre-flip):** `threshold / qualitative_context / rubric_interpretation`

The enum must be frozen now so validator and renderer test code is deterministic.

**R3 question:** Propose the FROZEN enum for V1.2. Constraints:

- Must be finite (3–8 values is the expected band)
- Must cover: threshold calibration in either direction (LLM thinks advisory threshold is too strict OR too lenient), missing qualitative context (advisory threshold is right but qualitative facts override — e.g., zustand Q3 softened by CONTRIBUTING.md), rubric interpretation (advisory threshold misread the V2.4 prompt rubric — e.g., Q3 literal-vs-intent that SF1 preserved as DeepSeek R4 dissent), and escape hatch (other)
- Renderer and validator must be able to handle every value

Propose concrete enum list. If you accept one of Codex R1's or DeepSeek R1's lists, say why. If you propose a new list, justify the deltas.

### 3.4 Item D — Renderer `dangerous_primitives` coupling (DeepSeek surfaced R2)

**Context:** V1.1 schema + current renderer partials use flat `dangerous_primitives.hits[]`. V1.2 under Owner Directive D1 adopts nested per-family `dangerous_primitives.{exec, ...}.files[].first_match`. The renderer partials that consume `hits[]` will break unless handled.

**Positions to date:**

- **DeepSeek R2:** mandatory V1.2 renderer change. "We cannot ship a schema that renderers can't process."
- **Pragmatist R1 blind spot:** flagged the same coupling; "Systems Thinker should probe this coupling explicitly."
- **Codex R2:** "the renderer does not materially depend on these Phase 1 field names today" — but he was talking about naming, not shapes.

**R3 question:** For V1.2, pick:

- **(a)** Nested partials — update the Jinja2 partial(s) that consume `dangerous_primitives` to iterate over per-family keys. Adds V1.2 renderer scope.
- **(b)** Compute-layer flatten — add a `compute.py::flatten_dangerous_primitives(form)` helper that produces `hits[]` at render time from the nested schema input. Renderer partials unchanged. Schema keeps richer nesting, renderer keeps current shape.
- **(c)** Jinja-macro flatten — do the flatten in Jinja with a `|flatten_families` filter. Renderer partials get a 1-line change to invoke the filter; schema keeps nesting.
- **(d)** other / propose

Resolve with concrete location of the change. Include a rough estimate of renderer partial lines touched.

### 3.5 Item E — `agent_rule_files.total_bytes` heuristic

**Context:** Transformer sets `total_bytes: sum(line_count × 50 for each agent_rule_file)`. Heuristic (50 bytes/line). DeepSeek R1 I-1: "fragile; V1.2 schema should accept raw line_count and let renderer compute bytes if needed."

**R3 question:** For V1.2:

- **(a)** Canonize heuristic — harness emits `total_bytes` directly using the 50-bytes/line heuristic; schema accepts it.
- **(b)** Require raw `line_count` per entry; compute bytes elsewhere — harness emits per-entry `line_count` (already does); renderer or `compute.py` derives `total_bytes = sum(line_count × 50)` at render/compute time; schema does NOT store `total_bytes`.
- **(c)** Gather true byte count from the tarball — harness does a `wc -c` on each agent_rule_file during tarball scan; schema accepts precise `file_bytes`; renderer sums.
- **(d)** other / propose

Resolve with concrete harness/compute/schema change.

### 3.6 Item F — Signal ID vocabulary for `computed_signal_refs`

**Context:** Q2/Q5 require `computed_signal_refs` as a non-empty list of stable signal IDs that the LLM cites when overriding. The vocabulary must exist in `docs/compute.py` and be published somewhere the LLM can see during Phase 4 authoring.

**Background (from SF1 Phase 1 patches):** `docs/compute.py` already has these signal-flavored checks:

- `has_classic_protection`, `has_rulesets`, `has_rules_on_default` (C20 severity inputs)
- `has_codeowners`, `ships_executable_code`, `has_recent_release_30d` (C20)
- `has_contributing_guide`, `has_warning_on_install_path` (SF1 Q3/Q4 patches)
- `closed_fix_lag_days` (SF1 Q2 numeric)
- `governance_floor_override` (SF1 Q1 triple-condition)
- `has_reported_fixed_vulns` (SF1 Q3 Gate C)
- top-contributor-share, formal-review-rate, self-merge-rate, any-review-rate (scorecard inputs)

**R3 question:** Propose the FROZEN V1.2 signal ID vocabulary. Each signal must have:

- **id** — stable snake_case string (e.g., `formal_review_rate_below_10`, `has_contributing_guide`, `governance_floor_override`)
- **type** — `bool` / `number` / `enum` / `object`
- **derived_from** — one-line hint about the Phase 1 field(s) it reads

Structure your proposal as a Markdown table with ~15–25 rows (rough band). Mark which ones are "scorecard inputs" (authoritative source for `phase_3_advisory.scorecard_hints.*.signals[]`) vs "supporting signals" (available for the LLM to cite but not used by compute.py advisory logic).

**Scope note:** The vocabulary freeze is for the FIRST V1.2 shipment. New signals can be added in V1.2.x patches without a schema bump; removing signals requires a bump. State any signal IDs you want to flag as "draft — subject to post-shipment rename" so they're not frozen prematurely.

---

## 4. What R3 must produce

Per SOP §4 R3 Deliberation format — this round proposes FINAL resolutions that go into implementation. Each agent delivers:

1. **Owner-directive acknowledgment** — one line confirming you've accepted D1 (Q3=B1) and D2 (phase_3_advisory topology) as fixed.
2. **Item A resolution:** (a) / (b) / (c) + 5-line validator pseudocode.
3. **Item B resolution:** (a) / (b) / (c) / (d) + file-count estimate.
4. **Item C resolution:** frozen enum list + justification per value.
5. **Item D resolution:** (a) / (b) / (c) / (d) + partial-line estimate.
6. **Item E resolution:** (a) / (b) / (c) / (d) + concrete change description.
7. **Item F resolution:** signal ID table (~15–25 rows) + "scorecard_input" / "supporting" flag per row + "draft" flag on any subject-to-rename items.
8. **Unresolved items for R4** — any of A–F that genuinely cannot resolve in R3.
9. **Blind spots.**

---

## 5. Required output format

Write to `.board-review-temp/d7-d8-schema-v12/{pragmatist|codex|deepseek}-r3.md` (one file per agent). Structure:

```
# Schema V1.2 R3 — [agent name]

## Owner directives acknowledged
- D1 (Q3 = D8-B1 harness-canonical, transformer deleted): accepted / objection with reason
- D2 (new top-level phase_3_advisory with scorecard_hints): accepted / objection with reason

## Item A — Q5 rationale-naming floor
**Resolution:** (a) / (b) / (c)
**Reasoning:** [100–200 words]
**Validator pseudocode:**
```
[5 lines of concrete Python-ish code]
```

## Item B — OQ-6 migration script scope
**Resolution:** (a) / (b) / (c) / (d)
**Reasoning:** [100–200 words]
**Files migrated:** [estimate with list]

## Item C — override_reason enum values
**Frozen enum:**
1. `value_1` — [definition]
2. `value_2` — [definition]
...
**Reasoning per departure from Codex R1 / DeepSeek R1 proposals:** [100–200 words]

## Item D — renderer dangerous_primitives coupling
**Resolution:** (a) / (b) / (c) / (d)
**Reasoning:** [100–200 words]
**Concrete change location:** [file + approx lines touched]

## Item E — agent_rule_files total_bytes heuristic
**Resolution:** (a) / (b) / (c) / (d)
**Reasoning:** [100–200 words]
**Concrete change:** [harness / compute / schema / renderer delta]

## Item F — signal ID vocabulary
| ID | Type | Derived from | Kind |
|---|---|---|---|
| `id_1` | bool | ... | scorecard_input |
| `id_2` | number | ... | supporting |
| ... | ... | ... | ... |
**Draft-subject-to-rename:** [list any signal IDs you want not yet frozen]
**Reasoning on contentious choices:** [100–300 words]

## Unresolved items for R4
- [Item X: why]
- ...
(If none: "None — all 6 items have concrete resolutions ready for V1.2 implementation.")

## Blind spots
[Honest disclosure]
```

Word cap: 2500 (because Item F table is dense). R3 resolutions are load-bearing for implementation — be concrete, not aspirational.

---

## 6. Decision principles per agent (R3)

- **Pragmatist:** smallest V1.2 that actually ships. Each resolution should be implementable in under a week by one operator. Flag any R3 choice that requires a multi-week side-project.
- **Systems Thinker:** where does each resolution couple? Item F vocabulary must be consumable by validator (Item A), enum must be consumable by telemetry analysis, renderer choice (Item D) must not break determinism tests. Surface coupling, not just correctness.
- **Skeptic:** what scan shape embarrasses each resolution? If Item F signal vocabulary is incomplete, what override category becomes uncategorizable? If Item D picks Jinja-macro flatten, what happens when a downstream consumer wants per-family aggregation?

---

## 7. R2 positions on these items — EXTRACTED (for stateless reading)

Read the full R2 files if you want complete context. The positions summarized below are the substantive deltas R3 must resolve.

### 7.1 Item A (Q5 rationale-naming)

- **Pragmatist R2** — G2+G3: "`computed_signal_refs` must be non-empty AND `rationale` must name at least one listed signal"
- **Codex R2** — G3+G4: "I would not require free-text mention of signal names if refs are machine-resolved; that is weaker than structural linkage." Validator checks `computed_signal_refs` non-empty, each ref resolves, rationale present and above floor length.
- **DeepSeek R2** — G3 + validator (flipped from G4): enum + machine-resolved refs is the floor; N-char validator is additive, not structural.

### 7.2 Item B (OQ-6 fixture scope)

- **Pragmatist R2:** active fixtures only (3 Step G files).
- **Codex R2:** active + archived Step G artifacts (update `provenance.json` `schema_version` on migrated). No bulk V2.4 catalog touch.
- **DeepSeek R2:** all fixtures in `provenance.json` including `step-g-failed-artifact`.

### 7.3 Item C (override_reason enum)

- **Codex R1 C-3:** `threshold_too_strict / threshold_too_lenient / missing_qualitative_context / rubric_literal_vs_intent / other` (5)
- **DeepSeek R1 C-2:** `threshold / qualitative_context / rubric_interpretation` (3)
- **Pragmatist:** did not propose a specific enum

### 7.4 Item D (renderer dangerous_primitives)

- **DeepSeek R2:** "mandatory renderer change must be in V1.2 scope. We cannot ship a schema that renderers can't process."
- **Pragmatist R1 blind spot:** same coupling flagged.
- **Codex R2:** focused on Q6 narrow → scorecard partial path only; did NOT explicitly address `dangerous_primitives` renderer coupling because his Q3=B1 logic assumed renderer changes would follow naturally.

### 7.5 Item E (total_bytes heuristic)

- **DeepSeek R1 I-1:** "fragile; V1.2 schema should accept raw line_count and let renderer compute bytes if needed."
- **Pragmatist R2** ground-truth bug absorption: did not specifically address; implicit in "transformer gone."
- **Codex R2:** did not specifically address.

### 7.6 Item F (signal ID vocabulary)

- **Pragmatist R1 open question:** "Has anyone defined the signal ID vocabulary?" — flagged as the underspecified blocker.
- **Pragmatist R2:** "export from compute.py as module constant."
- **Codex R2:** "populate stable signal IDs under `phase_3_advisory.scorecard_hints.<qid>.signals[]`; `computed_signal_refs` must reference those IDs, not prose names."
- **DeepSeek R2:** "compute.py defines IDs; LLM references them." Suggested examples: `formal_review_rate_below_10`, `no_branch_protection`, `has_contributing_guide`.

None proposed a full list.

---

## 8. Files to RE-READ (absolute paths, stateless)

- `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/r1-brief.md` (baseline scope)
- `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/r2-brief.md` (consolidation state)
- `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/pragmatist-r2.md`
- `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/codex-r2.md`
- `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/deepseek-r2.md`
- `/root/tinkering/stop-git-std/docs/scan-schema.json` (for where phase_3_advisory goes + current scorecard shape)
- `/root/tinkering/stop-git-std/docs/compute.py` (Item F — current compute.py surface is the starting point for signal vocabulary)
- `/root/tinkering/stop-git-std/docs/phase_1_harness.py` (Item E — what the harness can reasonably gather)
- `/root/tinkering/stop-git-std/.board-review-temp/markitdown-scan/phase-1-raw-full.json` (Item D — concrete `dangerous_primitives` shape in sidecar)
- `/root/tinkering/stop-git-std/.board-review-temp/markitdown-scan/transform_harness.py` (Item E — the `total_bytes` heuristic at line ~180)
- `/root/tinkering/stop-git-std/docs/templates/` + `docs/templates-html/` (Item D — where `dangerous_primitives` is rendered today)
- `/root/tinkering/stop-git-std/docs/render-md.py` + `docs/render-html.py` (Item D renderer entry points)
- `/root/tinkering/stop-git-std/docs/validate-scanner-report.py` (Item A — where validator logic lives)
- `/root/tinkering/stop-git-std/tests/fixtures/provenance.json` (Item B — archived artifact inventory)
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md` (OQ-2/OQ-3 basis — validates Codex's reading that SF1 used `phase_3_advisory`)

---

## 9. Meta-context (non-voting)

- HEAD: `4512084` on origin/main. 319/319 tests.
- Owner directives D1 and D2 are final. Do not argue them in R3 — R3 scope is items A–F only.
- R3 is Deliberation. If R3 resolves all 6 items cleanly, R4 Confirmation is brief (one pass for sign-off). If any item stays unresolved, R4 becomes focused on that item.
- Board composition: Pragmatist (Claude Sonnet 4.6), Systems Thinker (Codex GPT-5), Skeptic (DeepSeek V4).
- Pre-archive dissent audit rule applies — every dissent surfaced in R1 or R2 must either be resolved by R3 outcome, carried forward as R4 scope, or explicitly recorded as accepted-dissent. No silent drops.
- No external deadline. Quality > speed.
