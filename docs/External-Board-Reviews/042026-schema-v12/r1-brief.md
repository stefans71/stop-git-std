# Schema V1.2 Board Review — R1 Brief (Stateless)

**Review topic:** Scan-schema V1.2 design. Co-scheduled deferred items D-7 (scorecard cell authority migration) + D-8 (schema hardening for harness output). Both triggers have fired; this review decides the V1.2 shape before implementation.

**Round:** R1 Blind. Open scoping — all options on the table.

**Agent instruction:** You are one of three agents (Pragmatist / Systems Thinker / Skeptic). You are STATELESS — read this brief as if you've never seen this project. Inline context is sufficient; do not assume prior conversation. Read every file listed in §12 before voting.

---

## 1. What this project is

`stop-git-std` is an LLM-driven GitHub repository security scanner. The operator gives it `owner/repo`, it runs a structured investigation against `gh api` + OSSF Scorecard + osv.dev + package registries + `gitleaks` + tarball extraction + local grep, and emits an MD + HTML security report. 15 scans shipped to date across 8 shape categories.

Two rendering pipelines coexist:

- **V2.4 (default):** LLM authors MD and HTML directly from a findings-bundle. Proven on 11 catalog scans. No schema; no renderer.
- **V2.5-preview (production-cleared 2026-04-20):** JSON-first pipeline. Phase 1 raw data gathered by `docs/phase_1_harness.py` (automated), Phase 3 computed by `docs/compute.py`, Phase 4 structured fields + Phase 5 prose authored by LLM into `form.json`, then rendered deterministically by `docs/render-md.py` + `docs/render-html.py`. Validated against `docs/scan-schema.json` V1.1.

V2.5-preview's appeal vs V2.4:

- Phase 1 no longer LLM-freelanced (harness is deterministic)
- Byte-identical re-renders (fixture-driven regression tests viable)
- Phase boundaries enforced (facts in Phase 1, compute in Phase 3, inference in Phase 4, prose in Phase 5)
- Schema is the contract between pipeline stages

---

## 2. Why this review is happening

The markitdown wild scan (2026-04-20, catalog entry #15, Python monorepo + PyPI + Dockerfile) was the production-clearance trigger. It cleared all 7 applicable gates, BUT it also surfaced two concrete problems that were queued as deferred items D-7 and D-8. Their triggers have now fired. This review decides the V1.2 schema that resolves both.

**D-7 status:** Trigger (1) fired — first V2.5-preview scan on a shape outside the 3 Step G validation shapes {zustand, caveman, Archon}. Scope was already agreed in the SF1 board (docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md, 2026-04-20). This review confirms the scope and resolves remaining open questions.

**D-8 status:** New — added 2026-04-20 during markitdown scan. Harness produces richer fields than V1.1 schema accepts. A transformer + sidecar bridged V1.1 for the wild scan; V1.2 must accept harness output natively so the bridge is deleted.

---

## 3. D-7 scope — scorecard cell authority migration (SF1-board-agreed)

**Current state (V1.1):**

- `docs/compute.py::compute_scorecard_cells(form)` populates `phase_3_computed.scorecard_cells.{does_anyone_check_the_code, do_they_fix_problems_quickly, do_they_tell_you_about_problems, is_it_safe_out_of_the_box}` with `{color, short_answer, inputs}`.
- `compute.py` is deterministic — takes Phase 1 raw data and emits red/amber/green based on thresholds.
- Gate 6.3 of Step G acceptance requires "cell-by-cell match" between compute.py output and the V2.4 comparator MD scorecard.
- SF1 surfaced that compute.py's deterministic thresholds can't faithfully reproduce V2.4-LLM's semantic scorecard judgments (e.g. zustand-v3 Q3 where V2.4 LLM softened red → amber because the repo has a CONTRIBUTING.md and non-vuln PRs show responsiveness, which compute.py can't observe).

**V1.2 target state (agreed in SF1 R3 3/3 CONFIRM):**

- Move scorecard cells from `phase_3_computed.scorecard_cells` to `phase_4_structured_llm.scorecard_cells`.
- New cell shape: `{question, color, short_answer, rationale (cites E-IDs), edge_case, suggested_threshold_adjustment, computed_signal_refs}`.
- Demote `compute_scorecard_cells()` to advisory — it still runs and produces signals, but Phase 4 LLM is the authority and can override.
- Gate 6.3 changes from "cell-by-cell match" to "override-explained": when Phase 4 LLM's color differs from compute.py's, the `rationale` field must cite why.
- Step 3b byte-for-byte equality retained for the other 7 Phase 3 ops (verdict, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised).

**Rider items in SF1 for V1.2:**

- Q3 literal-vs-intent documentation (DeepSeek R4 disobedience concern preserved)
- Q1 Archon governance-floor override — does it stay deterministic in compute.py or migrate to Phase 4?
- 11-scan catalog comparator analysis (post-V1.2, feeds calibration telemetry)
- Override-pattern telemetry — emit a log of every cell where Phase 4 color ≠ compute.py advisory color, for steady-state calibration

**Open R1 question for the board:** "Advisory" is a spectrum. Pick one:

- **D7-A1:** compute.py is called from the pipeline; its output is injected into `phase_3_computed.advisory_scorecard_cells` and made visible to the LLM; LLM MUST consider it and cite `computed_signal_refs` when overriding.
- **D7-A2:** compute.py is called and emitted as Phase 3 field but has zero authority; LLM is free to ignore; `suggested_threshold_adjustment` feedback channel is the only purpose of the advisory.
- **D7-A3:** compute.py deleted entirely for scorecard cells; LLM works only from Phase 1 raw data + the prompt rubric.
- **Propose D7-A4+** if none fit.

---

## 4. D-8 scope — schema hardening for harness output

**Current state (V1.1):**

Phase 1 harness (`docs/phase_1_harness.py`, ~1787 lines) runs the V2.4 prompt Steps 1-8 + A/B/C end-to-end (gh api + OSSF Scorecard API + osv.dev + gitleaks + PyPI/npm/crates.io/RubyGems + tarball + local grep + README paste-scan). 30 tests in `tests/test_phase_1_harness.py`. Shipped in commit `4ad4cf6`.

Its output is structurally richer than schema V1.1 accepts. On markitdown, raw harness output had 25 schema validation errors. A transformer at `.board-review-temp/markitdown-scan/transform_harness.py` (~347 lines) renames/re-wraps fields to V1.1 shape; the full harness output is kept as a sidecar at `phase-1-raw-full.json` for audit/provenance. This is the V1.1 bridge.

**Deltas surfaced by the transformer — what V1.2 schema must decide:**

### 4.1 Field-name deltas (harness uses GitHub API names; V1.1 renames them)

| Harness field | V1.1 schema field | Why the split |
|---|---|---|
| `repo_metadata.archived` | `repo_metadata.is_archived` | V1.1 added `is_` prefix for clarity |
| `repo_metadata.fork` | `repo_metadata.is_fork` | same |
| `repo_metadata.default_branch` | `repo_metadata.default_branch_ref` | V1.1 added `_ref` suffix |
| `pre_flight.api_rate_limit.reset` (epoch int) | `pre_flight.api_rate_limit.reset_at` (ISO string) | V1.1 preferred ISO |
| `dependencies.dependabot_alerts` | `dependencies.dependabot` | V1.1 shortened |
| `dependencies.osv_lookups` | `dependencies.osv_dev` | V1.1 shortened |

### 4.2 Shape deltas (lists vs wrapper objects)

| Harness shape | V1.1 schema shape | Transformer action |
|---|---|---|
| `code_patterns.executable_files: [...]` | `{entries: [...]}` | wrap |
| `code_patterns.install_hooks: [...]` | `{found: bool, hooks: [...]}` | wrap + compute found |
| `code_patterns.agent_rule_files: [...]` | `{entries, count, total_bytes}` | wrap + compute metadata |
| `code_patterns.dangerous_primitives.{exec, deserialization, network, secrets, ...15 families}` each with `files: [{first_match: {line, snippet}}]` | `{hits: [{family, file, line, snippet}], hit_count}` | flatten from per-family nested → flat `hits` array |
| `code_patterns.readme_paste_blocks.{entries, entries_count}` | `{found, blocks}` | rename |
| `dependencies.manifest_files: [{path, format}]` | `[string]` | drop `format`, keep path |
| `pre_flight.symlinks_stripped` (int count) | bool | lossy cast |
| `coverage_affirmations.windows_surface_coverage` ("scanned" \| "skipped") | bool | lossy cast |
| `coverage_affirmations.distribution_channels_verified` ("4/5") | bool | lossy cast (all-or-nothing) |

### 4.3 Fields present in harness, absent from V1.1

| Harness field | Today's fate | What it captures |
|---|---|---|
| `pr_review.self_merge_count` | dropped | absolute count (schema only has rate) |
| `pr_review.security_flagged_count` | dropped (promoted to `security_relevant_prs`) | explicit count |
| `pr_review.total_merged_lifetime` | dropped | denominator for rate-over-time |
| `dependencies.dependabot_config` | dropped | parsed `.github/dependabot.yml` — schedule, open-pr-limit, etc. |
| `ossf_scorecard.http_status` | dropped | transport-level status (indexed/404/503) |
| `branch_protection.*.count` | dropped | count of entries (paginate check) |

### 4.4 The sidecar as V1.2 spec

The sidecar `/root/tinkering/stop-git-std/.board-review-temp/markitdown-scan/phase-1-raw-full.json` (3884 lines) is the concrete specification: every field present in the sidecar is a candidate for V1.2 native acceptance. The transformer is the inverse — every field it drops or re-shapes is a V1.2 design decision.

**Open R1 question for the board:** Which shape wins?

- **D8-B1 (harness-canonical):** V1.2 schema matches harness output field names and shapes. Rename `is_archived` → `archived` etc. Drop the transformer. Harness-emitted forms validate directly. Cost: 4 existing V1.1 fixtures regenerate; renderer partials update; V1.2 is a breaking shape change.
- **D8-B2 (schema-canonical, harness moves):** Harness absorbs the transformer logic and emits schema-native shapes directly. Schema keeps `is_archived` etc. Cost: harness complexity grows; field naming is a two-step lookup (harness does gh api, renames, emits).
- **D8-B3 (third canonical shape):** Both harness and schema adopt new names chosen for clarity — e.g. drop `is_` prefix but keep `_ref` suffix where disambiguating. Cost: biggest breaking change; cleanest long-term.
- **D8-B4 (V1.2 accepts both via `oneOf`):** Schema widens to accept harness-native OR current-V1.1 shapes. Cost: schema complexity; renderer must disambiguate at runtime; V1.1 fixtures remain valid.

---

## 5. Cross-cutting questions

### 5.1 Coordinated or staged?

- **D7+D8 coordinated V1.2:** Single schema bump. One migration. Atomic cutover.
- **Staged (D-8 V1.2 first, D-7 V1.3 second):** D-8 is additive/shape; lower risk. D-7 is a structural authority migration; higher risk. Different risk profiles. But two migrations = two fixture regenerations, two renderer-partial sweeps.

SF1 consolidation said "co-schedule" but did not commit to coordinated. R1 board should confirm or split.

### 5.2 Back-compat: accept V1.1 forms in V1.2?

- **Clean cut:** V1.2 is V1.2. V1.1 forms cannot be re-rendered without a migration script. 4 existing fixtures regenerate. 15 catalog entries keep their V2.4 or V2.5-preview (at V1.1) rendered outputs; new scans target V1.2.
- **`oneOf` back-compat:** V1.2 schema accepts both. Cost: schema complexity and renderer branching. Benefit: migration-free.
- **Migration script:** One-time `migrate-v1.1-to-v1.2.py` converts old forms. Fixtures regenerate via script; hand-authored forms unchanged. Middle path.

### 5.3 Gate 6.3 "override-explained" mechanics

When Phase 4 LLM color ≠ compute.py advisory color, what does "override-explained" structurally require?

- **D7-G1:** `scorecard_cell.rationale` is a free-text field; any prose is acceptable; reviewer judges sufficiency manually.
- **D7-G2:** `scorecard_cell.computed_signal_refs: [string]` MUST be non-empty AND `rationale` must reference at least one listed signal by name.
- **D7-G3:** New required field `override_reason` with an enum of override categories (e.g. `threshold_too_strict`, `threshold_too_lenient`, `missing_qualitative_context`, `rubric_literal_vs_intent`, `other`).
- **D7-G4:** Automated gate (validator-level) — presence of free-text rationale ≥ N chars + `computed_signal_refs` non-empty.

### 5.4 Renderer surface

The sidecar exposes richer per-finding data than today's renderer uses. For example `dangerous_primitives.exec.files[].first_match.snippet` is discarded in the V1.1 flat `hits[]` shape. Question: does V1.2 also include renderer-partial work to surface the richer data in §01/§02 finding cards, or does V1.2 scope stop at schema + compute.py + harness integration and leave renderer enhancements for a V1.3/V2.0 cycle?

### 5.5 Scope guard — what MUST be out

Candidate V1.2 scope creep items from the deferred ledger. Board should fence these out if agreeing, or justify inclusion:

- **SD2 (auto_load_tier re-binding):** C3 trigger moves from `category` regex to `domain=='agent'`. Tempting during V1.2 but belongs in its own review.
- **PD3 bundle validator:** already shipped (`885bdcf`); unrelated.
- **Package V2.5 refresh:** `github-scan-package-V2/` sync; orthogonal release cycle.
- **Scanner-Integrity section 00 hit-level structure:** Codex R2 defer-ledger item; may touch schema but has its own scope.
- **Schema-hardening watchpoint (§8.8.7 D-4):** already enforced procedurally; no schema work needed unless board finds a gap.

---

## 6. What V1.2 will not change

- 7 non-scorecard Phase 3 ops remain byte-for-byte deterministic (`compute_verdict`, `compute_solo_maintainer`, `compute_exhibit_grouping`, `compute_boundary_cases`, `compute_coverage_status`, `compute_methodology`, `compute_f5_silent`).
- Step 3b byte-for-byte equality retained for those 7.
- Phase 4 LLM authoring remains the sole source of findings entries, evidence entries, priority evidence, threat models, action steps, timeline events, capability assessments, catalog metadata, section leads, verdict exhibits, split-axis decision.
- Phase 5 prose remains structurally constrained (what_this_means, what_this_does_not_mean, editorial_caption, per-finding body_paragraphs).
- V2.4 pipeline continues to work without schema (no LLM-authored forms).

---

## 7. The 3 Step G V1.1 fixtures that will regenerate

These are the authoritative V1.1 forms that V1.2 must replace (or accept via migration):

- `tests/fixtures/zustand-form.json` (JS library shape, 10 FAs)
- `tests/fixtures/caveman-form.json` (curl-pipe installer shape)
- `tests/fixtures/archon-subset-form.json` (agentic platform subset, C3 auto_load_tier path)

Plus one not-yet-fixtured form: the markitdown form currently at `.board-review-temp/markitdown-scan/form.json`. V1.2 should confirm whether it becomes a 4th fixture or stays ephemeral.

---

## 8. Evidence tests to run (optional during R1, expected in R2)

The board may want to verify:

- **Round-trip:** Does harness output → V1.2 schema validation → render produce identical MD/HTML byte-for-byte vs the markitdown wild scan?
- **Deterministic re-render:** Does MD5 remain stable across 2 runs on the same `form.json`?
- **Advisory-override telemetry shape:** Can a one-liner sed/grep extract `(cell, advisory_color, llm_color, rationale_first_line)` from a V1.2 form?
- **V1.1 fixture round-trip under D8-B4:** If `oneOf` is adopted, do V1.1 fixtures still validate without modification?

---

## 9. Canonical options summary — what the board must vote on in R1

| ID | Question | Options |
|---|---|---|
| **Q1** | Coordinated V1.2 or staged? | coordinated / D-8-first / D-7-first |
| **Q2** | compute.py authority level (D-7) | D7-A1 / D7-A2 / D7-A3 / propose |
| **Q3** | V1.2 shape winner (D-8) | D8-B1 / D8-B2 / D8-B3 / D8-B4 / propose |
| **Q4** | Back-compat | clean / oneOf / migration-script |
| **Q5** | Override-explained mechanics | D7-G1 / D7-G2 / D7-G3 / D7-G4 |
| **Q6** | Renderer surface in V1.2 | yes (included) / no (deferred to V1.3+) |
| **Q7** | Scope guard | explicit OUT-of-scope list (agree/disagree per item) |

Propose additional questions if you see them.

---

## 10. Decision principles (from prior board SOP)

Per REVIEW-SOP.md §6 (Pragmatist-Codex-Skeptic framing):

- **Pragmatist:** Is this the smallest V1.2 that actually solves D-7 and D-8? What breaks at the operator's hand if we ship this? Is there a no-schema-change alternative (kept out for a reason)?
- **Systems Thinker:** Where does this couple? What second-order effects does migrating scorecard authority have on renderer partials, the V2.5-preview operator process in §8.8, gate 6.3 semantics, and fixture determinism tests?
- **Skeptic:** What assumption in this brief is wrong? What scan shape would embarrass V1.2? Does "override-explained" reduce to "say something and move on" without D7-G2+? What does the 11-scan comparator analysis need but cannot extract from V1.2 as designed?

---

## 11. Required output format

Write to `.board-review-temp/d7-d8-schema-v12/{pragmatist|codex|deepseek}-r1.md` (one file per agent). Structure:

```
# Schema V1.2 R1 — [agent name]

## Votes (one per question)
- Q1: [option] — [one-sentence reason]
- Q2: [option] — [one-sentence reason]
- ...

## Rationale (prose)
[300-700 words]

## FIX NOW items (if any)
- [C-ID]: [crisp finding]

## DEFER items (if any)
- [C-ID]: [item + trigger for lifting]

## INFO items (if any)
- [C-ID]: [observation worth recording]

## Open questions the brief missed
- [question 1]
- [question 2]

## Blind spots
[Brief honest disclosure — where is your perspective weakest on this topic?]
```

Word cap: 1500. Be opinionated. You are in R1 Blind — disagreement is the point.

---

## 12. Files to READ (absolute paths)

Read these before voting. The brief references them but they carry the full context.

- `/root/tinkering/stop-git-std/docs/scan-schema.json` — V1.1 schema (1397 lines) — what's changing
- `/root/tinkering/stop-git-std/.board-review-temp/markitdown-scan/phase-1-raw-full.json` — the D-8 spec (3884 lines) — what V1.2 should accept natively
- `/root/tinkering/stop-git-std/.board-review-temp/markitdown-scan/transform_harness.py` — the deltas in code (347 lines) — every drop/rename is a decision
- `/root/tinkering/stop-git-std/docs/phase_1_harness.py` — the producer (1787 lines) — module docstring + `transform_*` output signatures
- `/root/tinkering/stop-git-std/docs/compute.py` — Phase 3 compute — focus on `compute_scorecard_cells()` (D-7 migration target)
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md` — SF1 board outcome, which scoped D-7
- `/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md` §8.8.7 — D-7 and D-8 entries (ledger form)
- `/root/tinkering/stop-git-std/REPO_MAP.md` §2.5 — deferred ledger (D-7, D-8 entries)
- `/root/tinkering/stop-git-std/tests/fixtures/zustand-form.json` — one example V1.1 fixture (what regenerates)

Optional deeper-context:

- `/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md` lines 740–762 — V2.4 scorecard rubric (Phase 4 LLM authority source)
- `/root/tinkering/stop-git-std/docs/render-md.py` + `docs/render-html.py` — renderer consumers (affected by shape changes)
- `/root/tinkering/stop-git-std/docs/templates/` + `docs/templates-html/` — 14+14 Jinja2 partials

---

## 13. Meta-context (non-voting)

- Review topic surfaced 2026-04-20 session 4 during the markitdown wild scan.
- HEAD at brief authoring: `4512084` on origin/main.
- 319/319 tests passing.
- Operator and pipeline are both comfortable with schema breaking changes if the board chooses D8-B1/B3 — this is pre-v1.0 territory, not post-stable.
- No external deadline. Quality > speed. If R1 is divergent, R2+R3 rounds follow SOP normally.
- Implementation owner: same operator who built harness + transformer. Familiar with every field in scope.
- Board composition reminder: Pragmatist (Claude Sonnet 4.6), Systems Thinker (Codex GPT-5), Skeptic (DeepSeek V4). Each reads this brief cold.
