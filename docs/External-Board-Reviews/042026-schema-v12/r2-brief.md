# Schema V1.2 Board Review — R2 Consolidation Brief (Stateless)

**Review topic:** Scan-schema V1.2 design — co-scheduled D-7 (scorecard cell authority migration) + D-8 (schema hardening for harness output).

**Round:** R2 Consolidation. R1 Blind is complete; 3 agents voted independently. This round preserves disagreement where it exists and pushes convergence only where the three R1 positions can honestly be merged.

**Agent instruction:** You are STATELESS — read this brief as if you've never seen the project. All three R1 outputs are inlined verbatim in §9 below. Do not treat your own prior R1 output as already-known context; re-read it here. The R1 brief (§1) covered baseline context in 296 lines; this R2 brief re-briefs only the deltas.

---

## 1. Context refresh (compressed)

`stop-git-std` is an LLM-driven GitHub repo security scanner. Two rendering pipelines coexist: V2.4 (LLM authors MD+HTML directly) and V2.5-preview (JSON-first via `docs/scan-schema.json` V1.1 + `docs/phase_1_harness.py` + `docs/compute.py` + `docs/render-md.py` / `docs/render-html.py`). V2.5-preview was production-cleared 2026-04-20 via the markitdown wild scan (Python monorepo, 112k stars, catalog entry #15), which cleared all 7 applicable Step G gates but surfaced two deferred items whose triggers have now fired:

- **D-7:** scorecard cells move from `phase_3_computed` → `phase_4_structured_llm`; `compute_scorecard_cells()` demoted to advisory; gate 6.3 changes from "cell-by-cell match" to "override-explained." SF1 board (`docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md`) agreed scope; trigger (1) fired on markitdown wild scan.
- **D-8:** schema must accept richer fields emitted by `docs/phase_1_harness.py` (produces strictly richer data than V1.1 accepts; current bridge is `.board-review-temp/markitdown-scan/transform_harness.py` + `phase-1-raw-full.json` sidecar).

Full R1 brief (re-read if you need more): `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/r1-brief.md`.

---

## 2. R1 outcome — vote matrix

| Q | Question | Pragmatist (Sonnet) | Codex (GPT-5) | DeepSeek (V4) | Outcome |
|---|---|---|---|---|---|
| **Q1** | Coordinated or staged? | Coordinated | Coordinated | Coordinated | ✅ **Converged** |
| **Q2** | compute.py authority level | D7-A1 | D7-A1 | D7-A1 | ✅ **Converged** |
| **Q3** | V1.2 shape winner | **D8-B2-scoped** | **D8-B1** | **D8-B3** | ⚠️ **3-way split** |
| **Q4** | Back-compat | Migration-script | Migration-script | Migration-script | ✅ **Converged** |
| **Q5** | Override-explained mechanics | **D7-G2** | **D7-G3** | **D7-G4** | ⚠️ **3-way split** |
| **Q6** | Renderer surface in V1.2 | Deferred (caveat) | Deferred | Deferred | ⚠️ **Converged with Codex caveat (see §4.3)** |
| **Q7** | Scope guard | Agree | Agree | Agree | ✅ **Converged** |

**Converged on 5/7.** Diffs persist on Q3 (shape) and Q5 (override mechanics). Q6 carries a Codex-raised tension (see §4.3) but no vote diff.

---

## 3. Ground truth — Pragmatist's 3 FIX NOW bugs, verified against source

Pragmatist R1 flagged 3 FIX NOW bugs in `.board-review-temp/markitdown-scan/transform_harness.py` and `docs/phase_1_harness.py`. Operator verified all three against source before R2. The bugs are ground truth — other agents should treat them as confirmed, not as claims.

### 3.1 P1-RENAME — silent field drops (CONFIRMED + extended)

- **Claim:** `transform_repo_metadata()` hardcodes `has_issues_enabled: None`, `primary_language: None`, `topics: []` — these are present in the V1.1 zustand fixture but the harness doesn't gather them.
- **Verification:** `docs/phase_1_harness.py::step_1_repo_metadata` (lines 198–214) emits 10 fields: `name`, `description`, `created_at`, `pushed_at`, `stargazer_count`, `archived`, `fork`, `license_spdx`, `default_branch`, `open_issues_count`, `size_kb`. It does NOT emit `has_issues_enabled`, `primary_language`, `topics`, OR `fork_count` (also hardcoded to None in transformer).
- **Operator extension:** The harness DOES emit `open_issues_count` and `size_kb`, but V1.1 schema's `repo_metadata` doesn't accept them — transformer silently drops these too. So the harness-schema surface is bidirectionally lossy on repo_metadata.
- **Implication for V1.2:** either the harness gathers `has_issues_enabled` + `primary_language` + `topics` + `fork_count`, or schema marks them nullable/optional-but-preserved-when-gathered. Independently: schema must accept `open_issues_count` and `size_kb` which the harness already gathers.

### 3.2 P2-LOSSY-CAST — distribution_channels_verified all-or-nothing (CONFIRMED)

- **Claim:** `_transform_coverage_affirmations()` casts `"4/5"` to `False` via all-or-nothing logic (`int(num) == int(denom) and int(denom) > 0`). A repo with 3/5 channels verified reads as `False`, losing granularity.
- **Verification:** `.board-review-temp/markitdown-scan/transform_harness.py` lines 240–254 confirmed. `windows_surface_coverage` has the same pattern: `"scanned"` → `True`, any other string → `False`.
- **Implication for V1.2:** schema should accept `{verified: int, total: int}` or the raw fraction string. Bool loses semantically-meaningful partial-coverage information.

### 3.3 P3-DOUBLE-ASSIGN — branch_protection assigned twice (CONFIRMED)

- **Claim:** `transform_phase_1()` assigns `branch_protection` on line 208 AND line 218 within the same dict literal. Python silently takes the second value.
- **Verification:** `.board-review-temp/markitdown-scan/transform_harness.py` lines 208 and 218 confirmed. Both call `transform_branch_protection(raw.get("branch_protection") or {})` with identical inputs, so the result is correct by accident — but if either call ever changed, one would silently win.
- **Implication for V1.2:** regardless of how D-8 resolves, this bug must be deleted (second assignment removed) before harness absorption. Low-risk fix; must not survive into V1.2 landing.

---

## 4. The two splits — all 3 positions preserved

**Directive:** Do not collapse these splits prematurely. R2 is Consolidation, which means each agent should (a) re-read the other two positions, (b) either argue for merging or honestly defend their R1 position, and (c) explicitly note whether a merged position is possible. If a merged position is NOT possible, say so — the review escalates to R3 Deliberation → R4 Confirmation per SOP.

### 4.1 Q3 — V1.2 shape winner

Three R1 positions, all consistent with D-8 but differing on where the adaptation layer sits:

- **D8-B1 (Codex): Harness-canonical.** V1.2 schema renames fields to match harness output. `is_archived` → `archived`, `is_fork` → `fork`, `default_branch_ref` → `default_branch`, etc. `dangerous_primitives` stays nested per-family. Transformer deleted entirely. Breaking change for fixtures and renderer partials, but the cleanest long-term contract: the sidecar becomes the spec.
- **D8-B2-scoped (Pragmatist): Partial — harness absorbs field renames, schema absorbs shape deltas.** The 6 cheap renames (`archived→is_archived`, `fork→is_fork`, `default_branch→default_branch_ref`, `reset→reset_at` with epoch→ISO, `dependabot_alerts→dependabot`, `osv_lookups→osv_dev`) move into the harness. The structural deltas (per-family `dangerous_primitives` nesting, `manifest_files` object shape with `format`, lossy casts) get schema-native acceptance — V1.2 accepts what the harness emits for these. "Use the right tool for each delta, not one-size-fits-all."
- **D8-B3 (DeepSeek): Third canonical shape.** Neither harness nor V1.1 is right. Drop `is_` prefixes but keep `_ref` suffixes where disambiguating. Cleanest long-term semantic contract; biggest migration cost; both harness and schema change.

**Agreement substrate across all 3:**
- `oneOf` / runtime branching (D8-B4) rejected by everyone. Q4 migration-script is the universal mechanism.
- The transformer MUST go away — it's performing lossy semantic compression and Pragmatist verified 3 bugs in it. Disagreement is only about WHERE its logic lives post-V1.2.
- Nested per-family `dangerous_primitives` should be preserved in SOME form — not flattened (Pragmatist + DeepSeek explicit; Codex via "sidecar proves V1.1 is lossy").
- `dependabot_config`, `ossf_scorecard.http_status` (Codex-debatable), `pr_review.self_merge_count`, `pr_review.total_merged_lifetime` should be accepted somewhere — all three voted to preserve these, differing only in field placement.

**R2 task on Q3:** Either (a) converge on one of B1/B2-scoped/B3 with the other two agents agreeing the merger is honest, (b) define a **B-merged** that incorporates each agent's strongest point (e.g., "harness-canonical for shapes, rename-in-harness for the 6 cheap renames, third-shape only for 2 specific fields where brief calls out ambiguity"), or (c) declare the split unresolvable and escalate to R3.

### 4.2 Q5 — Override-explained mechanics

Three R1 positions, all consistent with D-7 advisory (Q2 unanimous) but differing on structural enforcement:

- **D7-G2 (Pragmatist): `computed_signal_refs` non-empty + rationale names at least one listed signal.** Minimal structural enforcement; validator-checkable via schema. Prevents pure word-salad but doesn't categorize overrides.
- **D7-G3 (Codex): `override_reason` enum + computed_signal_refs (from his C-3).** Categorizes why the LLM overrode (`threshold_too_strict` / `threshold_too_lenient` / `missing_qualitative_context` / `rubric_literal_vs_intent` / `other`). Enables semantic-drift telemetry analysis across scans.
- **D7-G4 (DeepSeek): Automated gate on `validate-scanner-report.py` — non-empty rationale ≥ N chars + `computed_signal_refs` non-empty.** Validator-side enforcement; schema-level structural constraints are weaker but runtime gate is stronger. Minimum-viable telemetry (the N-char rationale is free text, not categorized).

**Agreement substrate:**
- All 3 agree D7-G1 (free text only) collapses to theater. Rejected.
- All 3 agree `computed_signal_refs` must be non-empty. The disagreement is purely on what's layered on top.

**R2 task on Q5:** Each mechanism is additive — they're not mutually exclusive. The honest consolidation question is: **what's the minimum V1.2 enforcement that makes gate 6.3 structural rather than reviewer-taste?** Propose a merged position or defend why your R1 mechanism is sufficient alone.

### 4.3 Q6 — Codex's tension with his own vote

Codex voted "no renderer expansion in V1.2" BUT his INFO item C-7 states: *"The current Markdown and HTML scorecard partials are hard-coupled to `phase_3_computed.scorecard_cells`; D-7 necessarily includes renderer edits even if Q6 says 'no.'"*

Pragmatist's blind spot paragraph raises the same concern independently: "if the renderer directly consumes `code_patterns.dangerous_primitives.hits[]` today, and V1.2 changes that to a nested structure, then 'defer renderer to V1.3' becomes inconsistent."

This is a coupling-discovery, not a vote flip. R2 should resolve whether "Q6 defer" means:

- **Q6-narrow:** defer *NEW* renderer features (finding-card expansion to surface snippets, self_merge_count display, etc.). *Mandatory* renderer edits forced by the D-7 / D-8 authority + shape migration DO land in V1.2.
- **Q6-strict:** no renderer edits in V1.2 at all → then V1.2 cannot ship functional renders → reductio ad absurdum, not viable.
- **Q6-everything:** include all richer Phase-1 surface in V1.2 renderer → all 3 agents explicitly rejected this.

Consensus read: Q6-narrow was what all three meant. R2 should confirm.

---

## 5. The 6 consolidated open questions (not yet answered by R1)

R1 agents surfaced these as things the R1 brief missed. R2 should attempt answers or escalate each:

- **OQ-1 (Pragmatist):** **Who populates `computed_signal_refs` and what's the signal ID vocabulary?** If compute.py advisory signals need stable identifiers for the LLM to reference, someone has to define and freeze that vocabulary before V1.2 ships. Without it, Q2/Q5 requirements are underspecified.
- **OQ-2 (Pragmatist):** **Phase 3 container naming conflict.** SF1 CONSOLIDATION uses `phase_3_advisory.scorecard_hints`; the R1 brief uses `phase_3_computed.advisory_scorecard_cells`. These are different schema paths. The schema must pick one.
- **OQ-3 (Pragmatist):** **Does `phase_3_computed` rename or get a sibling?** If scorecard cells move to Phase 4 but compute.py still runs, does `phase_3_computed` gain a new sub-object (`advisory_scorecard_cells`) or does the schema add a new top-level phase (`phase_3_advisory`)?
- **OQ-4 (Codex):** **`phase_4_structured_llm.scorecard_cells`: keyed object by question ID, or ordered array?** The R1 brief mixes the two. Each choice has different renderer-partial and test implications.
- **OQ-5 (Codex):** **Gate 6.3 — schema-validation alone, or `validate-scanner-report.py` explicit check?** If validator gains explicit checks for `override_reason`, `computed_signal_refs`, and evidence citation coverage, that's new validator surface with its own test plan.
- **OQ-6 (Codex):** **Migration script scope — 4 active fixtures only, or also archived Step G test artifacts?** `tests/fixtures/provenance.json` tracks `step-g-failed-artifact` tags; are those regenerated too?
- **OQ-7 (DeepSeek):** **Partial Phase 1 failure handling.** If `gitleaks` times out but OSSF succeeds, does schema validation fail or accept partial structures? Schema V1.1 has no explicit partial-failure contract.
- **OQ-8 (DeepSeek):** **Catalog entries 1–11 (V2.4-only scans) migration story.** These have no form.json. Stay V2.4-rendered indefinitely, or back-author forms at some trigger?
- **OQ-9 (DeepSeek):** **Phase 4 LLM access to sidecar?** Does the LLM get the richer sidecar `phase-1-raw-full.json` for authoring context, or only the schema-valid `phase_1_raw_capture` subset?

Counted 9 in total; brief originally cited 6; three more surfaced on second look. Let's work all 9.

**R2 task on open questions:** propose an answer per OQ, OR flag the OQ as deferred-to-implementation (with trigger), OR declare unresolvable and escalate to R3. Do not silently drop any.

---

## 6. What R2 must produce

Per SOP §4 R2 Consolidation format:

1. **Per-split position:** read the other two agents' R1 votes. Either (a) agree to merge on one of them, (b) propose a merged position that honors each agent's strongest argument, or (c) reject and hold your R1 position — with reasoning. Explicit flip allowed; unexplained stasis is not.
2. **Per open question (OQ-1 through OQ-9):** proposed answer, or flagged deferred, or escalate.
3. **Ground-truth bugs:** P1/P2/P3 are confirmed. State whether V1.2 design absorbs fixes or whether any bug fix blocks a specific vote.
4. **New disagreement surfaced by R1:** if reading the other two R1 outputs revealed a tension you didn't flag in R1, raise it.
5. **Final vote row:** restated Q1–Q7 position (to detect silent flips).

**You are in R2 Consolidation.** Disagreement is allowed; silent agreement via not-addressing is not. Every split and every OQ must get a position.

---

## 7. Required output format

Write to `.board-review-temp/d7-d8-schema-v12/{pragmatist|codex|deepseek}-r2.md` (one file per agent). Structure:

```
# Schema V1.2 R2 — [agent name]

## Final vote row (Q1–Q7)
- Q1: [option] ([held / flipped from R1])
- Q2: [option] ([held / flipped])
...

## Split-1 position (Q3 — shape winner)
[Propose merger or defend R1 position. Read other two R1 votes (§9 below) before writing.]

## Split-2 position (Q5 — override mechanics)
[Same.]

## Q6 coupling resolution
[Narrow / strict / everything — confirm consensus read or propose alternative.]

## Open question positions
- OQ-1: [answer / deferred / escalate — with reasoning]
- OQ-2: [...]
- ... through OQ-9

## Ground-truth bug absorption
- P1-RENAME: [how V1.2 handles — must be concrete]
- P2-LOSSY-CAST: [...]
- P3-DOUBLE-ASSIGN: [...]

## New disagreement surfaced
[If reading other R1 outputs revealed a new tension — state it. If none, say so.]

## Rationale (prose)
[500–1000 words]

## Unresolved items for R3 (if any)
[What MUST escalate — these become the R3 scope]

## Blind spots
[Same honest disclosure format as R1]
```

Word cap: 2000. Longer than R1 because you're responding to other agents' positions.

---

## 8. Decision principles per agent (reminder)

- **Pragmatist:** smallest V1.2 that solves D-7+D-8. What breaks at operator's hand? Are the merged positions actually smaller than one R1 position, or are we building a Franken-compromise?
- **Systems Thinker:** where do the merged positions couple? Is a merged Q3+Q5 position honest about second-order effects (renderer partials, gate 6.3 automatability, fixture determinism tests), or does it just paper over the split?
- **Skeptic:** what's the scan shape that still embarrasses the merged position? If convergence is possible, what's the price? If not, what's the real reason — genuine disagreement or insufficient shared context?

---

## 9. R1 outputs — VERBATIM

All three R1 responses inlined below. Read all three before writing R2, even the one you authored — stateless means re-read.

### 9.1 Pragmatist R1 (verbatim)

```
# Schema V1.2 R1 — Pragmatist

## Votes (one per question)

- **Q1:** Coordinated V1.2 — both D-7 and D-8 touch `phase_1_raw_capture` and fixtures; splitting means two regeneration passes with no real risk savings.
- **Q2:** D7-A1 — compute.py runs and its output is injected into `phase_3_computed.advisory_scorecard_cells`; Phase 4 LLM MUST cite `computed_signal_refs` when overriding; advisory is visible and structural, not optional.
- **Q3:** D8-B2 (schema-canonical, harness moves) — but scoped: only the 6 cheap field-name renames belong in the harness; the shape deltas (flatten, wrap) stay as schema accepts harness shapes natively for those. See rationale.
- **Q4:** Clean cut with migration script — write `migrate-v1.1-to-v1.2.py`; 3 fixtures regenerate deterministically; no `oneOf` schema complexity; V1.1 forms stay valid against V1.1 schema unchanged.
- **Q5:** D7-G2 — `computed_signal_refs` must be non-empty AND `rationale` must name at least one listed signal; automated gate enforces this; D7-G1 (free text only) collapses to "write something and move on."
- **Q6:** No — renderer surface deferred to V1.3+; V1.2 scope is schema + harness integration; no partial rewrites this cycle.
- **Q7:** SD2, Package V2.5 refresh, Scanner Integrity hit-level structure, D-4 watchpoint are all OUT; all agree per brief; no justification for inclusion.

---

## Rationale

**On Q1 (coordinated vs staged):** D-8 is not purely additive. The field-name renames in D-8 touch `phase_1_raw_capture.repo_metadata` and `pre_flight`, which are also what compute.py reads to produce advisory scorecard signals for D-7. If you do D-8 first, compute.py's input signatures change, and the D-7 advisory cell shape depends on those same fields. Running both together avoids fixture regeneration twice and avoids a half-migrated state where the harness is schema-canonical but compute.py still reads V1.1-named fields.

**On Q3 (D8-B2 scoped vs pure):** Pure D8-B2 (harness absorbs all transformer logic) would balloon the harness. The right split: field-name renames (`archived` → `is_archived`, `fork` → `is_fork`, `default_branch` → `default_branch_ref`, `reset` → epoch-to-ISO conversion, `dependabot_alerts` → `dependabot`, `osv_lookups` → `osv_dev`) are cheap harness changes — the harness just emits the schema-native names from the start. The shape deltas are different: the per-family `dangerous_primitives` structure (15 families × files[]) is harness-semantically correct — it's a natural representation of grep-per-pattern results. V1.2 schema should accept the nested per-family shape natively rather than forcing a flatten into a `hits[]` array at the harness level. The flatten loses the per-family aggregation context that the LLM would want for Phase 4 inference. Similarly, `manifest_files: [{path, format}]` — the harness emits the format field because it knows it; dropping it at transform time is a pure loss. V1.2 should accept it.

For the lossy casts in §4.2: `symlinks_stripped` as an integer count is richer than a bool; V1.2 should accept `integer | boolean`. `distribution_channels_verified` as "4/5" is richer than a bool; V1.2 should accept a string or a structured `{verified, total}` object. These are the cases where the harness has better data and the schema was the weak point.

**On Q2 (advisory authority):** D7-A2 (zero authority, just a feedback channel) is too weak. The whole point of keeping compute.py is that deterministic signals are reproducible and fast to audit. If the LLM can silently ignore them, the `suggested_threshold_adjustment` feedback loop never fires reliably because there's no enforcement that the LLM even looked. D7-A1 (must cite signals when overriding) preserves the feedback loop while still giving Phase 4 final authority.

D7-A3 (delete compute.py scorecard cells entirely) is the worst option: it trades a deterministic checkpoint for pure LLM discretion with no baseline. The compute.py advisory signals are not wrong — they're calibrated for 3 shapes and will grow with the 11-scan comparator analysis. Throwing them away pre-maturely loses institutional knowledge.

**On Q4 (back-compat):** `oneOf` schema complexity is the wrong trade. The renderer must then branch on which shape it received, adding runtime logic that is itself untested. A migration script is 50 lines; fixture regeneration is deterministic; this is the minimal-complexity path. V1.1 forms can still be re-rendered via the migration script — they are not permanently broken.

**On D7 Q1 Archon governance-floor:** The brief asks whether the Archon Q1 governance-floor override stays deterministic in compute.py or migrates to Phase 4. My vote: stays in compute.py as an advisory signal with explicit flag `governance_floor_override: true` in the advisory cell. The override fires because three binary conditions are simultaneously true — that IS deterministic and appropriate for Phase 3. The Phase 4 LLM then decides whether to accept the advisory red or override with rationale. This is cleaner than baking a judgment-call into Phase 4 with no compute.py anchor.

---

## FIX NOW items

- **P1-RENAME:** The transformer's `transform_repo_metadata()` already silently drops `has_issues_enabled`, `primary_language`, and `topics` (all return `None` or `[]` hardcoded). These fields are present in the zustand fixture but the harness doesn't gather them. V1.2 harness must gather them or the schema must mark them nullable-but-present-in-fixture-only. Do not silently diverge.
- **P2-LOSSY-CAST:** `distribution_channels_verified: "4/5"` → `bool` via all-or-nothing cast is a lossy information loss that a finding author cannot recover. V1.2 schema should accept a structured `{verified: int, total: int}` or string fraction. The transformer's current cast is a time bomb for a repo with 3/5 channels verified where compute.py sees `False` but the LLM would see "mostly verified."
- **P3-DOUBLE-ASSIGN:** `transform_phase_1()` assigns `branch_protection` twice (lines 208 and 218 in transform_harness.py). The second assignment (line 218) silently overwrites the first. This is a code bug in the existing transformer that will survive into V1.2 if harness absorbs transformer logic without review.

---

## DEFER items

- **D-RENDERER:** All renderer partial changes (surfacing `first_match.snippet`, per-family dangerous_primitives display) → V1.3 cycle. Not blocking V1.2 correctness.
- **D-TELEMETRY:** Override-pattern telemetry log (emit CSV of `cell, advisory_color, llm_color, rationale_first_line`) → implement alongside the 11-scan comparator analysis, post-V1.2 landing. Trigger: 3 V1.2 scans shipped.
- **D-SD2:** `auto_load_tier` C3 trigger rebinding to `domain=='agent'` → own review cycle per the brief's scope guard.
- **D-MARKITDOWN-FIXTURE:** Whether the markitdown form becomes a 4th fixture → defer until V1.2 schema is stable and form can be regenerated clean. Premature to fixture an ephemeral bridge-generated form.

---

## INFO items

- **I1:** The transformer has a `branch_protection` double-assignment bug (P3-DOUBLE-ASSIGN above) that means `branch_protection.classic.raw_response` is being set from `bp.get("classic", {}).get("body")` on first assignment and then overwritten with the same call on second. Since both calls are identical, the output is correct by accident — but if the harness ever emits different fields under `classic`, one assignment will silently win. Flag for review during harness absorption.
- **I2:** `pr_review.self_merge_count`, `pr_review.total_merged_lifetime`, and `dependencies.dependabot_config` are dropped by the transformer. `self_merge_count` is particularly valuable — the transformer re-derives `self_merge_rate` from it, then drops the denominator. V1.2 should accept the count fields alongside the rate.
- **I3:** `ossf_scorecard.http_status` (transport-level 404/503) being dropped is fine for schema V1.2 — the `indexed: bool` field captures the operational signal. The raw HTTP status is a debug artifact, not a finding input.

---

## Open questions the brief missed

- **Who populates `computed_signal_refs` in Phase 4?** The schema sketch shows it as an LLM-authored list of strings, but compute.py advisory signals need stable identifiers for the LLM to reference. Has anyone defined the signal ID vocabulary? Without it, "must cite `computed_signal_refs`" is underspecified — the LLM will invent names.
- **What is the Phase 3 container name?** The SF1 CONSOLIDATION says `phase_3_advisory.scorecard_hints` but the brief says `phase_3_computed.advisory_scorecard_cells`. These are different field paths. The schema must pick one before implementation.
- **Does `phase_3_computed` rename or get a sibling?** If scorecard cells move to Phase 4 but compute.py still runs and emits advisory signals, does `phase_3_computed` gain a new sub-object (`advisory_scorecard_cells`) or does the schema add `phase_3_advisory` as a new top-level phase? The brief is silent on this; it is a schema topology question with real implementation cost.
- **Are the 11-scan comparator analysis rider items gate-blocking for V1.2 acceptance, or post-V1.2 telemetry?** The brief lists them as "rider items" but doesn't say whether V1.2 ships without them or whether they're part of the V1.2 acceptance criteria.

---

## Blind spots

My weakest area here is the renderer surface (Q6) — I'm deferring it partly because I haven't read `render-md.py` and `render-html.py` deeply enough to know whether the D8-B2 shape changes (accepting nested per-family `dangerous_primitives` in V1.2) require partial rewrites before the renderer can process V1.2 forms at all. If the renderer directly consumes `code_patterns.dangerous_primitives.hits[]` today, and V1.2 changes that to a nested structure, then "defer renderer to V1.3" becomes inconsistent — you can't ship V1.2 forms that the V1.2 renderer can't render. The Systems Thinker should probe this coupling explicitly.
```

### 9.2 Codex R1 (verbatim)

```
# Schema V1.2 R1 — Codex

## Votes (one per question)
- Q1: coordinated — D-7 and D-8 hit the same contracts (`form.json`, renderer partials, gate 6.3, fixtures), so splitting creates two migration waves and duplicated breakage.
- Q2: D7-A1 — compute must remain a required advisory input so overrides are traceable, calibratable, and testable rather than free-form.
- Q3: D8-B1 — the harness should be canonical because it is already the real producer and the sidecar proves V1.1 is the lossy layer.
- Q4: migration-script — clean cut on runtime contract, but provide one deterministic upgrader for the 4 fixtures and any archived V1.1 forms that need re-render.
- Q5: D7-G3 — override semantics need a machine-readable reason category, not just prose, or telemetry and gate enforcement will collapse into reviewer taste.
- Q6: no (deferred to V1.3+) — V1.2 must update renderers for moved scorecard authority, but richer Phase-1 data surfacing in finding cards should stay out.
- Q7: agree — SD2, PD3, package refresh, Scanner-Integrity section-00 restructuring, and D-4 watchpoint schema work are all out of scope.

## Rationale (prose)
The key coupling is that D-7 is not just "move four cells." Today the trust-scorecard partials in both Markdown and HTML read directly from `phase_3_computed.scorecard_cells`, and tests assert that exact location. Once scorecard authority moves to Phase 4, renderer partials, render tests, fixture shapes, and Step G gate 6.3 all need to move in lockstep. If you stage D-8 first and D-7 later, you regenerate fixtures twice, rewrite the scorecard partials twice, and keep the operator guide in an awkward transitional state where Phase 1 is V1.2-native but the scorecard still pretends to be deterministic authority. That is wasted churn.

The D-8 side is similarly coupled. The transformer is not a harmless adapter; it is performing lossy semantic compression. It drops `dependabot_config`, `ossf_scorecard.http_status`, `pr_review.self_merge_count`, `total_merged_lifetime`, branch-protection counts, and it collapses coverage from ratios/states to booleans. That matters because those fields are exactly the kind of facts Phase 4 needs when it is asked to justify overrides against compute advisories. If D-7 lands while D-8 keeps the lossy bridge, the LLM is being asked to explain overrides from a degraded fact surface. That is a bad authority migration.

I would make the harness shape canonical (`D8-B1`) rather than teaching the harness to emit a renamed "schema dialect." The harness already speaks the source systems' language and the sidecar is the empirical spec. Preserving V1.1 names via `oneOf` pushes complexity downstream into renderers, validators, and tests. A `oneOf` schema does not preserve determinism; it preserves ambiguity. The renderer then has to normalize at runtime, and that is exactly how byte-identical re-render guarantees get fragile.

On D-7, `D7-A1` is the right advisory level. Deleting compute removes calibration telemetry. Making compute ignorable removes the only stable comparison baseline. The operator process in §8.8 also depends on explicit phase boundaries: Phase 3 should still emit deterministic signals; Phase 4 may override them, but only against visible, named advisory inputs. That lets gate 6.3 become a real structural check instead of "the LLM said something plausible."

I do not support broad renderer-surface expansion in V1.2. There is mandatory renderer work here, but it should be narrowly scoped: read scorecards from Phase 4, optionally expose advisory deltas if needed, and keep the rest stable. If you also decide to surface richer dangerous-primitive snippets, self-merge counts, Dependabot config, and transport-level OSSF details in V1.2, you multiply parity risk and blow up the determinism test surface.

The thing that blows up if this coupling is ignored is not one bug, but contract incoherence: operator instructions still describe Step 3b authority one way, renderers read another field, fixtures validate via adapters, and tests stop proving what production does. That is how "preview" pipelines rot.

## FIX NOW items (if any)
- C-1: Define one canonical V1.2 scorecard storage shape now: keyed object vs ordered array. Renderer/test churn is different for each; leaving it implicit will fork implementations.
- C-2: Define `phase_3_advisory` explicitly in schema and operator guide, not just prose. D-7 currently references it without a concrete schema contract.
- C-3: Require `computed_signal_refs` to resolve to named advisory fields and require `override_reason` enum alongside rationale; otherwise gate 6.3 is not automatable.
- C-4: Ship a one-time V1.1→V1.2 migration script with fixture regeneration. Do not solve back-compat with runtime `oneOf`.

## DEFER items (if any)
- C-5: Renderer expansion for richer Phase-1 data in §01/§02 finding cards — defer until V1.3, triggered after V1.2 round-trip and determinism pass on all regenerated fixtures.
- C-6: 11-scan comparator calibration analysis — defer until V1.2 schema is frozen and override telemetry exists, or the analysis will be on the wrong contract.

## INFO items (if any)
- C-7: The current Markdown and HTML scorecard partials are hard-coupled to `phase_3_computed.scorecard_cells`; D-7 necessarily includes renderer edits even if Q6 says "no."
- C-8: The transformer proves V1.1 is not merely renaming fields; it actively erases counts, ratios, transport status, and per-family structure that may matter for Phase-4 reasoning.
- C-9: `coverage_affirmations.distribution_channels_verified` is currently richer as `"4/5"` than the schema's boolean. Keeping the boolean blocks honest coverage reporting.

## Open questions the brief missed
- Should `phase_4_structured_llm.scorecard_cells` be a keyed object by canonical question id or an ordered array of cell objects? The brief mixes the two.
- Will gate 6.3 validate override structure from schema alone, or will `validate-scanner-report.py` gain explicit checks for `override_reason`, `computed_signal_refs`, and evidence citation coverage?
- Does the migration script also rewrite archived Step G artifacts used by tests, or only the 4 active fixtures?

## Blind spots
My weakest point here is comparator-authoring ergonomics: I am optimizing for contract clarity and system behavior, not for minimizing LLM prompt complexity during Phase 4 authoring.
```

### 9.3 DeepSeek R1 (verbatim)

```
# Schema V1.2 R1 — Skeptic

## Votes (one per question)
- Q1: **coordinated** — D-7 and D-8 are intrinsically coupled; splitting creates two migration pains and risks schema drift between them.
- Q2: **D7-A1** — compute.py must remain visible as advisory with signal refs; otherwise "override-explained" is just "say something and move on" theater.
- Q3: **D8-B3** — Neither harness nor V1.1 naming is optimal; adopt clean third shape that drops `is_` prefix but keeps `_ref` suffix for clarity.
- Q4: **migration-script** — Clean cut with one-time migration script preserves forward simplicity while enabling V1.1 fixture regeneration.
- Q5: **D7-G4** — Automated gate requiring non-empty rationale ≥ N chars + computed_signal_refs non-empty; free-text alone invites LLM word salad.
- Q6: **no (deferred to V1.3+)** — V1.2 scope should be schema + harness integration only; renderer enhancements are separate complexity.
- Q7: **explicit OUT-of-scope list (agree)** — SD2, PD3, Package V2.5 refresh, Scanner-Integrity section 00, Schema-hardening watchpoint must stay out.

## Rationale (prose)

The fundamental assumption wrong in this brief is that "override-explained" with D7-G1 (free-text rationale) provides meaningful accountability. It doesn't. Without D7-G2+ structural constraints, Phase 4 LLM can write plausible-sounding nonsense that cites nothing, and gate 6.3 becomes a rubber stamp. The zustand Q4 example in the brief shows the danger: V2.4 LLM softened red → amber because of CONTRIBUTING.md and non-vuln PR responsiveness. If compute.py can't observe those signals, how can Phase 4 LLM cite them? It can't—it will invent post-hoc justifications unless forced to reference concrete computed_signal_refs.

The 11-scan comparator analysis needs something V1.2 as designed cannot extract: **semantic drift detection**. V1.2 focuses on threshold calibration (formal<10% → red) but misses when LLM overrides for qualitative reasons outside the rubric (e.g., "this repo has a vibrant community despite low formal review"). The comparator needs a field like `override_category: "threshold" | "qualitative_context" | "rubric_interpretation"` to distinguish calibration fixes from judgment calls.

What scan shape would embarrass V1.2? A **monorepo with mixed governance models**—some subdirectories have branch protection, others don't; some have CODEOWNERS, others don't. The harness flattens these to repo-level booleans, losing the nuance. Phase 4 LLM reading the raw data might spot the pattern, but V1.2's `has_branch_protection: bool` can't capture it, and the LLM has no structured way to express "partial branch protection in critical subpaths."

The dangerous_primitives flattening (per-family → flat hits[]) is a **data loss we'll regret**. The sidecar preserves `exec.files[].first_match.snippet` but the schema discards it. When a security analyst wants to know "what kind of exec calls?" (subprocess.run vs os.system vs eval), they need the family context. The flattening also loses hit distribution across families—3 exec hits vs 1 exec + 1 network + 1 deserialization tells different stories about codebase risk profile.

D-8's field naming debate misses the deeper issue: **type coercion losses**. `symlinks_stripped: int → bool` loses count data that matters for tarball integrity assessment. `distribution_channels_verified: "4/5" → bool` loses granularity—which channel failed? These aren't just naming differences; they're semantic compression that future analyses will need to reverse-engineer from sidecars.

## FIX NOW items (if any)
- **C-1:** Dangerous_primitives flattening must preserve family context in V1.2 schema. Keep per-family structure with hit_count + files[].
- **C-2:** Add `override_category` enum to scorecard_cell schema to enable semantic drift analysis in 11-scan comparator.
- **C-3:** Type coercion fields (symlinks_stripped, distribution_channels_verified) must preserve original granularity or add companion fields.

## DEFER items (if any)
- **D-1:** Renderer partial updates for new fields (e.g., self_merge_count display) — defer to V1.3 to keep V1.2 focused on schema/harness integration.
- **D-2:** Full Scanner-Integrity section 00 hit-level structure — has its own scope trigger (Codex R2 defer-ledger).

## INFO items (if any)
- **I-1:** The transformer's `agent_rule_files.total_bytes` heuristic (line_count × 50) is fragile; V1.2 schema should accept raw line_count and let renderer compute bytes if needed.
- **I-2:** `ossf_scorecard.http_status` dropped by transformer but useful for diagnosing API failures; V1.2 should preserve it.
- **I-3:** `dependencies.dependabot_config` contains schedule/open-pr-limit data valuable for automation assessment; dropping it loses insight.

## Open questions the brief missed
- How does V1.2 handle **partial Phase 1 failures**? If gitleaks times out but OSSF succeeds, does schema validation fail or accept null/partial structures?
- What's the **migration story for catalog entries 1-11** (V2.4 scans without forms)? Will they stay V2.4-only or get back-authored V1.2 forms?
- Does **Phase 4 LLM get access to the sidecar** (phase-1-raw-full.json) for richer context, or only the schema-valid subset?

## Blind spots
My perspective is weakest on the **renderer template complexity** of adopting per-family dangerous_primitives. I'm advocating for richer schema but haven't examined the 14 Jinja2 partials to see if they can gracefully handle nested structures. The pragmatic trade-off might favor flattening for renderer simplicity, but that's data loss we should acknowledge upfront.

Also, I'm skeptical of "advisory" compute.py (D7-A1) but haven't considered the **prompt engineering burden** of teaching Phase 4 LLM to reference computed_signal_refs. If the LLM consistently ignores them, the structure is decorative. We need evidence from Step G Phase 4 runs on whether LLMs naturally cite evidence IDs when available.
```

---

## 10. Files to RE-READ (absolute paths, even if read in R1)

Stateless — don't rely on memory. Re-read these:

- `/root/tinkering/stop-git-std/.board-review-temp/d7-d8-schema-v12/r1-brief.md` (the original brief — §4.2 delta tables are load-bearing; don't paraphrase them from memory)
- `/root/tinkering/stop-git-std/docs/scan-schema.json` (V1.1 — focus on phase_1_raw_capture, phase_3_computed.scorecard_cells, phase_4_structured_llm)
- `/root/tinkering/stop-git-std/.board-review-temp/markitdown-scan/phase-1-raw-full.json` (sidecar — D-8 empirical spec)
- `/root/tinkering/stop-git-std/.board-review-temp/markitdown-scan/transform_harness.py` (every delta; read `transform_phase_1` lines 200-237 specifically to confirm P3 bug)
- `/root/tinkering/stop-git-std/docs/phase_1_harness.py::step_1_repo_metadata` (lines 198-214; confirm P1 scope)
- `/root/tinkering/stop-git-std/docs/compute.py::compute_scorecard_cells` (Phase 3 migration target)
- `/root/tinkering/stop-git-std/docs/render-md.py` + `docs/render-html.py` (Q6 coupling evidence — how do renderers today access `phase_3_computed.scorecard_cells`?)
- `/root/tinkering/stop-git-std/docs/templates/` + `docs/templates-html/` (14+14 Jinja2 partials — scorecard rendering specifically)
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md` (OQ-2 evidence — verify the `phase_3_advisory.scorecard_hints` vs `phase_3_computed.advisory_scorecard_cells` naming conflict)
- `/root/tinkering/stop-git-std/tests/fixtures/provenance.json` (OQ-6 evidence — see what archived artifacts exist)

---

## 11. Meta-context (non-voting)

- R1 Blind results preserved in `.board-review-temp/d7-d8-schema-v12/{pragmatist,codex,deepseek}-r1.md`. R2 outputs go alongside as `-r2.md` files.
- HEAD: `4512084` on origin/main. 319/319 tests.
- Operator authored the R1 brief AND wrote `transform_harness.py` / `phase_1_harness.py`. Operator accepts the 3 P-bugs are real and has not yet fixed them. P3-DOUBLE-ASSIGN specifically is operator negligence; R2 may take it as ground truth without re-litigation.
- Board composition: Pragmatist (Claude Sonnet 4.6) / Systems Thinker (Codex GPT-5) / Skeptic (DeepSeek V4). Each reads this brief cold.
- Per SOP §4: if R2 produces unresolved splits on Q3 or Q5, R3 Deliberation fires automatically. If OQ-1 through OQ-9 cannot be resolved here, they become the R3 scope instead of the votes.
- No external deadline. Quality > speed.
