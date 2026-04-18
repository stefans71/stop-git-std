# Board Alignment Check — Renderer Execution Plan

**Task:** Verify my proposed execution plan for Phase 7 (deterministic renderer) matches the **already-established** board-approved goal. This is a *direction check*, NOT a re-opening of settled decisions.

**Reviewers:** Codex (Systems Thinker) + DeepSeek (Skeptic). Pragmatist/Claude skipped (Claude wrote the code, will execute).

**Round:** R1 only. ALIGN / DRIFT verdict per question.

---

## 1. Full context — ALL inlined below (agents are stateless)

### 1.1. What the V2.3 Round-3 consolidation established (2026-04-16)

Key excerpt from `docs/board-review-V23-consolidation.md` C12 — **JSON-first deferred at the time with explicit triggers**:

> **C12. D6 (JSON-first) — Systems Thinker says promote now; Pragmatist says defer with triggers; Skeptic says defer pending cross-LLM test. Board consensus: DEFER with explicit triggers.**
>
> Board decision: **DEFER** with explicit re-evaluation triggers (any one triggers V3.0 work):
> 1. Catalog corpus reaches 10 scans.
> 2. A subsequent board review surfaces 3+ rule-skip findings similar to C5 / C6.
> 3. A manual re-run diff between two scans of the same repo becomes impractical.
> 4. A cross-LLM compatibility test fails on GPT-4o or Gemini.
>
> If adopted: Systems Thinker's **4-step migration path** is the recommended plan:
> 1. freeze schema
> 2. LLM emits JSON+legacy-MD for 2 releases
> 3. deterministic renderer
> 4. schema-first validator

**Architecture verdict section from same doc:**

> Decision: DEFER JSON-first to V3.0. Explicit re-evaluation triggers are in C12.
>
> Migration path (when triggered): use Systems Thinker's 4-step plan — schema freeze → dual emit (JSON + legacy MD) for 2 releases → deterministic renderer → schema-first validator.

### 1.2. What session 4's pipeline methodology review established (2026-04-17/18)

Triggers fired (10-scan catalog hit). Board ran 10 further rounds and approved full migration. From `project_pipeline_architecture.md` memory:

- **Classification 8 / 8 / 4:**
  - 8 automatable (Python decision trees): verdict, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology, F5 silent/unadvertised
  - 8 structured LLM (enums+templates): general vuln severity, split-axis, priority evidence, threat model, action steps, timeline, capability assessment, catalog metadata
  - 4 prose LLM (structural constraints): "what this means", "what this does NOT mean", finding body, editorial caption

- **9-phase pipeline:**
  1. Tool exec → raw capture (JSON form, incremental)
  2. Data validation gate
  3. Python computes 8 automatable fields
  4. LLM fills 8 structured fields
  5. LLM writes 4 prose fields
  6. JSON assembly with provenance tags
  7. Python renderer → MD + HTML ← **this is what I'm building**
  8. Validator gate (MD/HTML parity)
  9. Git hook spot-checks (5 commands)

- **Option C unanimous:** template placeholder substitution (Jinja2 OR simple string templating — which one was not locked).
- **Phase boundaries are gates** (no lazy compute across phases).
- **MD is canonical;** HTML derived from same data model.

Also approved in session 4 and already built:
- `docs/compute.py` — 8 functions (431 lines)
- `docs/scan-schema.json` — JSON Schema draft 2020-12, 30 `$defs` (1054 lines, V1.0)
- `docs/GitHub-Repo-Scan-Form.json` — Investigation form V1.1 (23 gap fixes from 3-model review)
- `docs/validate-scanner-report.py` — Validator with 4 modes (--report, --markdown, --template, --parity)
- 81 tests (37 validator + 33 compute + 11 end-to-end)

### 1.3. What today's renderer R1 added (2026-04-18 — both of you voted)

Renderer R1 brief asked 4 questions. Both Codex and DeepSeek returned UNANIMOUS:

**Q1 — Renderer size:** D. Jinja2 (not split-package, not Python-heavy templating).

Codex said: *"`docs/render-md.py` is not just long; it is carrying presentation policy, fallback policy, and contract adaptation in one file. The board-approved architecture already picked template substitution, and the rendered-vs-golden diff shows the missing output is overwhelmingly template content rather than algorithmic logic. A thin renderer plus templates is the only option here that lowers complexity for both Markdown and the upcoming HTML renderer."*

DeepSeek said: *"Jinja2 would reduce Python code to ~150 lines (just data loading + template rendering), move formatting logic to template files where it belongs, enable HTML renderer to share the same templates, and provide better error messages for missing fields."*

**Q2 — Fixture enrichment:** C tight (enrich STRUCTURAL fields only; keep prose sparse).

Codex: *"If a field controls section presence, table shape, grouping, labels, summaries, or evidence layout, it belongs in the fixture; if it is open-ended persuasive prose, keep it minimal."*

DeepSeek: *"Structural fields (pr_sample_review.rows, executable_file_inventory, evidence.entries, repo_vitals.rows, coverage_detail.rows) have mechanical shapes that should be locked into tests. Prose fields are judgment calls that shouldn't be in fixtures. Encoding LLM prose as test data is indeed a category error."*

**Q3 — Schema update timing:** NOW, before fixture enrichment or renderer refactor.

Codex: *"The renderer already depends on fields the schema does not describe, which means the renderer contract is currently informal and drifting. More importantly, the schema is not merely incomplete, it still reflects older shapes in places: `action_steps` and `timeline_events` in schema do not match what the fixture and renderer actually use, and `phase_5_prose_llm` is too loose to validate `body_paragraphs` or similar fields."*

DeepSeek: *"Schema-first development prevents drift. Adding fields to the schema now ensures LLM prompt includes explicit instructions for these fields, future scans produce consistent shapes, validator (Phase 2) can check completeness, renderer expectations are formalized."*

**Q4 — Compute-on-demand:** A. Pre-computed contract. No lazy compute.

Both flagged the same deeper problem: **contract drift across schema ↔ fixture ↔ renderer ↔ golden.** Codex: *"Your main framing is slightly off: the core issue is not 'fixture too thin' by itself. The deeper problem is contract drift across schema, fixture, renderer, and golden. Until that is corrected, line count is secondary."*

---

## 2. My proposed execution plan

Execute step 3 of V2.3's 4-step migration (deterministic renderer), informed by today's R1 refinements (Jinja2 + structural-only fixture):

### Step A: Schema `$defs` update — lock the contract
Update `docs/scan-schema.json` (currently 1054 lines) to add missing `$defs` and properties for every field the renderer references, AND reconcile stale shapes Codex flagged (`action_steps`, `timeline_events`, `phase_5_prose_llm`). Concrete additions:
- `verdict_exhibits.groups[]` (phase_4_structured_llm)
- `executable_file_inventory.layer1_summary` + `layer2_entries[]` (phase_4_structured_llm)
- `pr_sample_review.rows[]` with per-row: number/what/author/merger/reviewed/concern/flagged (phase_4_structured_llm)
- `coverage_detail.rows[]`, `coverage_intro`, `coverage_gaps[]` (phase_4_structured_llm)
- `evidence.entries[]` with id/claim/command/result/classification; `evidence_intro` (phase_4_structured_llm)
- `repo_vitals.rows[]` with metric/value/note (phase_4_structured_llm)
- `timeline_intro`, `section_leads.section_01` (pill_row + summary) (phase_4_structured_llm)
- Per-finding additions: `body_paragraphs[]` (phase_5_prose_llm), `meta_table[]`, `how_to_fix`, `duration_label`, `date_label` (phase_4_structured_llm)
- `catalog_metadata.prior_scan_note` (phase_4_structured_llm)

Reconcile stale: Update existing `action_steps` $def to match what `compute.py` + form actually produce; same for `timeline_events`; tighten `phase_5_prose_llm` to validate body_paragraphs.

### Step B: Refactor render-md.py to Jinja2
- Add `Jinja2` as a project dependency
- Create `docs/templates/scan-report.md.j2` (top-level) and per-section partials in `docs/templates/partials/` (one per section: hero, catalog, verdict, scorecard, action_steps, findings, exec_inventory, pr_sample, timeline, vitals, coverage, evidence, methodology, footer)
- Rewrite `docs/render-md.py` as ~150 lines: load JSON → create Jinja2 environment → render top-level template → emit MD
- Keep existing `tests/test_render_md.py` — structural tests should still pass

### Step C: Enrich `tests/fixtures/zustand-form.json`
Against the updated schema, add all STRUCTURAL-LLM fields (~300-500 lines of JSON). Do NOT add full body paragraphs or multi-paragraph prose — keep `per_finding_prose` entries at current thinness.

### Step D: Flip tests to richer structural assertions
- All 13 sections present
- Table row counts match (evidence 9, vitals N, coverage M, pr_sample rows)
- Section order matches golden
- Prose stays LLM-varying (no full diff-match against zustand.md prose)

### Step E: Validator gate
Run `validate-scanner-report.py --report <rendered-output>` and confirm it passes. If not, note gaps for follow-up.

### Step F: Later session — render-html.py using same Jinja2 templates, MD/HTML parity gate.

---

## 3. What I need you to check

**Q1. Sequence alignment.** Does Steps A→B→C→D→E match the V2.3 4-step migration plan + session-4 pipeline review? Or is the order wrong?

**Q2. Schema-before-refactor.** Today's R1 said schema first. My plan puts schema first (Step A). Confirm: is schema-first the correct prerequisite, or would Jinja2 refactor first expose schema shape issues that A→B→C would miss?

**Q3. Open items I may be missing.** Check the V2.3 consolidation FIX NOW list against my plan. Specifically:
- **C3 F12 fields** (File SHA + line range + diff anchor on inventory cards) — should my new `executable_file_inventory` $def in Step A require these?
- **C9 auto-load tier classification** — should agent-rule-file findings in the schema require an `auto_load_tier` enum field?
- **C10 scorecard calibration table** — already in `compute.py`. Any Schema-level requirement needed?
- **C11 monorepo coverage** — does `coverage_detail` need explicit monorepo fields?
- **C7 acceptance-scan matrix** (Archon + FastAPI + zustand) — is zustand-fixture alone sufficient before locking, or do we need other shapes first?

**Q4. Dependency I'm overlooking.** Step 2 of V2.3's migration was "dual emit (JSON + legacy MD) for 2 releases." Did that actually happen? If not, does skipping it affect test strategy?

**Q5. Done vs in-progress items.** Am I treating any "already-done" work as still-to-do, or any "still-to-do" work as done? e.g. if scan-schema.json V1.0 was the intended "schema freeze" (step 1 of migration), then I'm redefining that step instead of executing step 3.

---

## 4. Output

Save to `.board-review-temp/renderer-alignment/<your-role>-alignment.md`.

- DeepSeek writes to `deepseek-alignment.md`
- Codex writes to `codex-alignment.md`

Short. Per Q1-Q5: ALIGN / PARTIAL / DRIFT + 2-4 sentence reasoning.

End with one line: **`VERDICT: PROCEED`** (plan is aligned, execute as-is) OR **`VERDICT: ADJUST`** (list specific adjustments).

Be blunt. If my plan reinvents already-done work, say so.

---

## 5. Files to read (all in /root/tinkering/stop-git-std/)

- `docs/board-review-V23-consolidation.md` — V2.3 C12 migration plan (293 lines)
- `docs/scan-schema.json` — current schema V1.0 (1054 lines) — check if it's truly a "freeze" or has gaps
- `docs/render-md.py` — current renderer (782 lines)
- `tests/fixtures/zustand-form.json` — current fixture (705 lines)
- `docs/GitHub-Scanner-zustand.md` — golden (602 lines)
- `docs/compute.py` — Phase 3 functions (431 lines)
- `.board-review-temp/renderer-r1/codex-r1-output.md` — today's Codex R1 (35 lines)
- `.board-review-temp/renderer-r1/deepseek-r1-output.md` — today's DeepSeek R1 (137 lines)
- `.board-review-temp/renderer-r1/rendered-zustand.md` — current renderer output on fixture (213 lines)

The 4-step migration plan is only a few sentences in `docs/board-review-V23-consolidation.md` — scan the C12 section and the "Architecture verdict" section (~lines 134-145 and 217-228).
