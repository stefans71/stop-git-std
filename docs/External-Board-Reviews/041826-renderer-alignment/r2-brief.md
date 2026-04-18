# Board R2 Consolidation — Renderer Execution Plan Alignment

**Task:** Respond AGREE / DISAGREE / MODIFY on each consolidated finding below. Per FrontierBoard SOP §4-R2.

**Reviewers:**
- Pragmatist (Claude, fresh session — shippability / proportionality / accuracy lens)
- Systems Thinker (Codex, GPT-5 Codex — architecture / data-flow / downstream effects lens)
- Skeptic (DeepSeek V4 — risk / failure modes / assumptions lens)

**Round:** R2 Consolidation. Skip to R4 confirmation if unanimous on all items.

---

## 0. Agents are stateless — full context inlined

### 0.1. The goal (board-approved across prior rounds)

**V2.3 Round 3 consolidation (2026-04-16) — C12 migration plan:** JSON-first deferred at the time with triggers. Migration plan (when triggers fire):
1. Schema freeze
2. LLM emits JSON+legacy-MD for 2 releases (dual emit)
3. Deterministic renderer
4. Schema-first validator

**Session 4 pipeline review (2026-04-17/18) — 10 rounds, unanimous:** Triggers fired. Approved:
- 8 / 8 / 4 classification (8 automatable / 8 structured-LLM / 4 prose-LLM)
- 9-phase pipeline (tool → validate → compute → structured-LLM → verdict → prose-LLM → assembly → render → validate → git-hook)
- Option C — template placeholder substitution (Jinja2 OR simple string; not locked)
- Phase boundaries are gates (no lazy compute)
- MD canonical; HTML derived from same data model

**Prior R1 on renderer tactics (2026-04-18 earlier) — unanimous:**
- Jinja2 (not split-package, not simple string)
- Fixture enrichment = structural fields only; prose stays sparse (category error to encode LLM prose as test data)
- Schema update before fixture enrichment
- Pre-computed form, no lazy compute

### 0.2. The proposed execution plan under review

Step A: Schema `$defs` update — add missing fields (`verdict_exhibits.groups`, `executable_file_inventory`, `pr_sample_review.rows`, `coverage_detail.rows`, `evidence.entries`, `repo_vitals.rows`, `section_leads`, per-finding `body_paragraphs`/`meta_table`/`how_to_fix`/`duration_label`/`date_label`, `catalog_metadata.prior_scan_note`). Reconcile stale shapes (`action_steps`, `timeline_events`, `phase_5_prose_llm`).

Step B: Refactor `docs/render-md.py` to Jinja2 — thin ~150-line Python + `docs/templates/*.md.j2`.

Step C: Enrich `tests/fixtures/zustand-form.json` against updated schema — structural-LLM fields only, prose stays sparse.

Step D: Flip tests to richer structural assertions (all 13 sections, table row counts, section order).

Step E: Run `validate-scanner-report.py --report` on rendered output.

Step F (later): `render-html.py` via same Jinja2 templates; MD/HTML parity gate.

### 0.3. R1 outputs (unanimous ADJUST verdict) — both agents' words

**Codex R1 alignment (verbatim):**

> **Q1. PARTIAL.** Steps A→B→C→D are the right local order for the renderer work: formalize the contract, refactor the renderer to templates, then enrich the fixture and tighten tests. But this is not a clean "execute step 3" sequence from the V2.3 migration path, because your Step A is still finishing step 1 (`scan-schema.json` is not actually frozen yet) and your Step E is only a spot check, not the full schema-first validator milestone. Also, C7's acceptance-matrix requirement still exists before claiming the pipeline is locked or reliable.
>
> **Q2. ALIGN.** Schema-first is correct.
>
> **Q3. PARTIAL.** Missing: C3 `executable_file_inventory` should require `file_sha`, `line_ranges`, `diff_anchor`; C9 agent-rule-file structures must require/reference `auto_load_tier`; C11 coverage contract must render monorepo count + sampled-inner-package explicitly. C7 zustand alone not enough before locking.
>
> **Q4. PARTIAL.** Step 2 (dual emit for 2 releases) was not clearly completed. Need stronger regression comparison against existing legacy MD artifacts and multiple acceptance-scan shapes.
>
> **Q5. PARTIAL.** Mixing done and not-done work. `scan-schema.json` V1.0 is not a true schema freeze — contract has outrun it, stale shapes. Step A is schema-freeze REPAIR, not purely step-3 execution.
>
> **VERDICT: ADJUST** — keep A→B→C→D, explicitly treat Step A as schema-freeze repair, add C3/C9 contract items, don't claim migration is at clean step 3 or that zustand alone locks it.

**DeepSeek R1 alignment (summary — full at `.board-review-temp/renderer-alignment/deepseek-alignment.md`):**

> **Q1. PARTIAL.** Plan targets step 3 (deterministic renderer) but skips step 2 (dual emit prerequisite). Step A redoes step 1 instead of assuming schema is already frozen.
>
> **Q2. ALIGN.** Schema-first is correct.
>
> **Q3. DRIFT.** Missing C3 F12 fields, C9 auto-load tier, C11 monorepo coverage, C7 acceptance-scan matrix.
>
> **Q4. DRIFT.** Step 2 (dual emit) DID NOT HAPPEN. Pipeline emits HTML-first for legacy scans; zustand fixture exists but no evidence of 2 releases with dual emit.
>
> **Q5. DRIFT.** Redoing step 1 while claiming step 3. Category error.
>
> **VERDICT: ADJUST.** Required: (1) Rename Step A "Complete schema freeze V1.1"; (2) Address dual emit gap with minimal dual-emit test; (3) Include C3/C9/C11; (4) Archon re-run before locking; (5) Clarify "step 3 execution with step 1 completion."

---

## 1. Consolidated findings (C-items)

Below are the R1 findings deduplicated and themed. For each: proposed classification + question for agents.

### C1 — Step A reframing: "schema-freeze repair," not "step-3 prep"

- **Agents:** Both R1 reviewers (PARTIAL / DRIFT convergence)
- **Severity consensus:** **FIX NOW** (plan-framing drift)
- **Issue:** My plan calls Step A "schema $defs update — pre-renderer work." Both R1 reviewers say the schema was never truly frozen — contract drifted before renderer was built. Step A is therefore schema-freeze REPAIR (finishing step 1 of V2.3 C12 migration), not pre-work for step 3.
- **Proposed fix:** Rename Step A to "**Complete schema freeze → V1.1**" and bump `schema_version`. Explicit acknowledgement in the plan that this is finishing migration step 1, not starting step 3.
- **Question:** AGREE / DISAGREE / MODIFY on this framing + rename?

### C2 — Add C3 FIX NOW: File SHA + line range + diff anchor on inventory entries

- **Agents:** Both R1 reviewers
- **Severity consensus:** **FIX NOW** (carries V2.3 Round 3 FIX NOW forward)
- **Issue:** V2.3 consolidation C3 required `File SHA at scanned revision`, `Relevant lines`, `Diff anchor` on every security-critical executable-file inventory card. Current schema has no such requirement on `executable_file_inventory.layer2_entries[]`.
- **Proposed fix:** Add required properties to `executable_file_inventory` entry schema: `file_sha`, `line_ranges`, `diff_anchor`. Make them required for entries where `dangerous_calls != "None"` or kind indicates security relevance.
- **Question:** AGREE / DISAGREE / MODIFY on the scope (required always vs required when security-relevant)?

### C3 — Add C9 FIX NOW: auto_load_tier required on agent-rule-file findings

- **Agents:** Both R1 reviewers
- **Severity consensus:** **FIX NOW** (carries V2.3 Round 3 FIX NOW forward)
- **Issue:** V2.3 consolidation C9 elevated D9 → FIX NOW: every agent-rule-file finding (CLAUDE.md, AGENTS.md, .cursorrules, etc.) must carry an `auto_load_tier` (Always / Conditionally / User-activated / Unknown-default-Tier-1). `auto_load_tier` exists as a `$def` in current schema but is not required on any structure — the FIX NOW never became enforceable.
- **Proposed fix:** On findings with `category` matching agent-rule-file patterns (`supply-chain/agent-rules/*`, `code/agent-rule-file`, etc.), require `auto_load_tier` property.
- **Question:** AGREE / DISAGREE / MODIFY on the trigger for required-ness? Alternative: always required on all findings (safer but noisier)?

### C4 — Add C11 coverage extensions: monorepo + pull_request_target

- **Agents:** Both R1 reviewers
- **Severity consensus:** **FIX NOW** (carries V2.3 Round 3 FIX NOW forward)
- **Issue:** V2.3 consolidation C11 requires monorepo inner-package count + explicit `pull_request_target: N found` line in coverage. Current `coverage_detail` schema has neither.
- **Proposed fix:** Extend `coverage_detail.rows[]` to support structured fields for `inner_package_count`, `sampled_inner_packages[]`, `pull_request_target_usage_count`. Keep Generic row shape for other coverage checks.
- **Question:** AGREE / DISAGREE / MODIFY? Alternative: add a structured `coverage_detail.monorepo` object + `coverage_detail.pr_target_usage` field separate from generic rows.

### C5 — Don't claim contract lock after zustand-only

- **Agents:** Both R1 reviewers
- **Severity consensus:** **DEFER** (trigger: before "pipeline reliable" claim, run C7 matrix)
- **Issue:** V2.3 consolidation C7 required the acceptance-scan matrix (Archon re-run + FastAPI or similar Python + zustand or similar React) before claiming the pipeline is reliable. My plan treats zustand-fixture alone as sufficient — it isn't.
- **Proposed fix:** Document explicitly: renderer ships after Step E validator gate, but contract-lock / "pipeline reliable" claim requires C7 matrix. Add Step G post-renderer: re-scan Archon with full JSON-first pipeline (Archon already has a golden MD).
- **Trigger:** Before any "V1.1 complete" or "pipeline reliable" claim.
- **Question:** AGREE / DISAGREE / MODIFY?

### C6 — Step 2 (dual emit) gap: add minimal dual-emit verification

- **Agents:** Both R1 reviewers
- **Severity consensus:** **DEFER / FIX NOW** (split — Codex says use tests to replace; DeepSeek says run one minimal dual-emit scan before refactor)
- **Issue:** V2.3 C12 migration step 2 was "LLM emits JSON + legacy MD for 2 releases." This never actually happened — session 4 built the JSON investigation form as a design artifact but no real scan has been run producing both JSON and MD in the same release cycle.
- **Proposed fix options:**
  - A (DeepSeek): Before Step B (Jinja2 refactor), run ONE live scan (e.g., Archon re-run) where the LLM emits JSON + the renderer emits MD. Verify the LLM can reliably produce the structured JSON against current schema.
  - B (Codex): Use the C7 acceptance-scan matrix as the dual-emit verification. Each of the 3 scans in the matrix is a live dual-emit test.
- **Proposed consolidated fix:** Combine — make Step G the C7 matrix AND the dual-emit verification. Do NOT block Step B on this (fixture-based testing is sufficient for the refactor). But do not claim "pipeline reliable" until both dual-emit and multi-shape matrix are proven.
- **Question:** AGREE / DISAGREE / MODIFY on combining C5 + C6 into one "Step G = C7 matrix + dual-emit"?

### C7 — R1 agreement: keep Jinja2, structural-only fixture, pre-computed form

- **Agents:** Both R1 reviewers (earlier renderer R1 + today's alignment R1)
- **Severity consensus:** **AGREE** (settled)
- **Issue:** Confirming prior R1 rulings — Jinja2 for Step B, fixture structural-only for Step C, pre-computed form (no lazy compute) throughout.
- **Proposed fix:** No change.
- **Question:** Still AGREE, or has anything changed in light of C1-C6 adjustments? (Expected: all agree, skip to R4.)

---

## 2. Revised execution plan (after C1-C6)

1. **Step A (renamed) — Complete schema freeze → V1.1**
   - Add missing `$defs` (verdict_exhibits, executable_file_inventory, pr_sample_review, coverage_detail, evidence, repo_vitals, section_leads, per-finding extensions)
   - **C2:** Require `file_sha` + `line_ranges` + `diff_anchor` on executable_file_inventory entries
   - **C3:** Require `auto_load_tier` on agent-rule-file findings
   - **C4:** Extend coverage_detail with monorepo + pull_request_target fields
   - Reconcile stale shapes (action_steps, timeline_events, phase_5_prose_llm)
   - Bump `schema_version` to "1.1"
2. **Step B — Refactor render-md.py to Jinja2** (~150 lines Python + templates)
3. **Step C — Enrich zustand-form.json against V1.1** (structural only, prose sparse)
4. **Step D — Flip tests to structural assertions**
5. **Step E — Validator `--report` gate on rendered output**
6. **Step F (later session) — render-html.py** via same Jinja2 templates + MD/HTML parity
7. **Step G (before contract-lock claim) — C7 acceptance matrix + dual-emit verification**: run Archon re-run + one other shape + zustand live scans to verify LLM can produce V1.1-compliant JSON and the renderer produces valid output across shapes.

---

## 3. Your task

Respond to **C1 through C7** with: **AGREE** / **DISAGREE** / **MODIFY**.

For DISAGREE or MODIFY, include: rationale (2-3 sentences) and proposed alternative.

**Output format per item:**
```
### C[N]: AGREE / DISAGREE / MODIFY
[2-3 sentences reasoning; if MODIFY, the alternative]
```

End with one line:
- **`VERDICT: SIGN OFF`** (if AGREE on all) — we skip R3, go to R4 confirmation
- **`VERDICT: REFINE`** (if any DISAGREE/MODIFY) — R3 deliberation needed

**Save your output:**
- Pragmatist (Claude subagent): inline response, saved by facilitator
- Systems Thinker (Codex): `/tmp/codex-r2.md`
- Skeptic (DeepSeek V4): `.board-review-temp/renderer-alignment/deepseek-r2.md`

---

## 4. Files to read (all in /root/tinkering/stop-git-std/)

- `docs/board-review-V23-consolidation.md` — C12 migration plan (lines 134-145 and 217-228 are the key sections)
- `docs/scan-schema.json` — current schema V1.0 (1054 lines)
- `docs/render-md.py` — current renderer (782 lines)
- `tests/fixtures/zustand-form.json` — current fixture (705 lines)
- `docs/GitHub-Scanner-zustand.md` — golden output (602 lines)
- `docs/board-review-data/renderer-r1/` — today's renderer R1 outputs
- `docs/board-review-data/renderer-alignment-r1/` — today's alignment R1 outputs

---

## 5. Reminder on FrontierBoard SOP

Per §4 R2: "Agents respond: AGREE / DISAGREE (with rationale) / MODIFY (with alternative)." Per §4 "Expedited": if R2 unanimous, skip R3 → go to R4 confirmation.

Anonymized prior positions: R1 ADJUST verdict from two agents (one architecture-lens, one risk-lens). No owner directives issued between R1 and R2.
