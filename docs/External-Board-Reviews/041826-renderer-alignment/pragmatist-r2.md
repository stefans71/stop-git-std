# Pragmatist R2 — Renderer Plan Consolidation

**Reviewer:** Pragmatist (Claude, fresh subagent session)
**Role:** Shippability / proportionality / accuracy lens
**Round:** R2 Consolidation

---

**Overall verdict: REFINE — I AGREE on C1, C2, C3, C7; MODIFY C4, C5, C6 to trim facilitator-introduced ceremony.**

The R1 ADJUST verdict is legitimate for C1/C2/C3 — the renderer is already reading `verdict_exhibits.groups`, `executable_file_inventory`, `pr_sample_review`, `coverage_detail.rows`, `repo_vitals.rows`, `section_leads`, `body_paragraphs` from `phase_4_structured_llm`, and none of those shapes are in the schema. That is real contract drift, not hand-wringing. But the brief's C4/C5/C6 consolidations are where facilitator scope creep is sneaking in.

### C1: AGREE
The contract has demonstrably outrun V1.0 (seven unformalized shapes read by `render-md.py` lines 179/246/360/396/442/547/564). Renaming Step A to "Complete schema freeze → V1.1" and bumping `schema_version` is accurate, not ceremony. It costs nothing beyond a label change and a version string.

### C2: AGREE
C3 (V2.3 FIX NOW) required File SHA + line range + diff anchor on every security-critical executable-file inventory card. On scope: **required when security-relevant, not always** — entries where `dangerous_calls` is non-empty or kind is sensitive. Always-required would force the LLM to fabricate line ranges for benign entries.

### C3: AGREE
Same logic as C2. `auto_load_tier` exists as `$def` but is referenced by nothing. On trigger: **required on agent-rule-file findings only** (category match). "Always required" is the noisier option that would force a meaningless `unknown` on unrelated findings — trains LLMs to treat validator as noise.

### C4: MODIFY
AGREE need, DISAGREE stuffing into `coverage_detail.rows[]`. Monorepo inner-package count and `pull_request_target` usage are structured computed fields, not narrative rows — `phase_1_raw_capture.monorepo.inner_packages` and `phase_1_raw_capture.workflows.pull_request_target_count` already exist as raw captures. **Alternative:** add `coverage_detail.monorepo` and `coverage_detail.pr_target_usage` as typed sibling objects, populated by `compute.py` from existing raw captures. Rows stay generic, structured facts stay structured.

### C5: MODIFY
AGREE the claim "pipeline reliable" shouldn't rest on zustand alone. DISAGREE with formal "Step G" in this plan. **Alternative:** add one-line note — "V1.1 schema-lock and 'pipeline reliable' claims require the C7 acceptance matrix; do not make either claim after Step E" — and leave matrix scheduling to a separate decision. Bolting Step G onto renderer plan conflates workstreams (ship a renderer vs. validate the whole pipeline across shapes) and creates a path where the renderer can't land until three live scans complete.

### C6: MODIFY
"Step 2 dual emit didn't happen" framing is half-facilitator-hand-wringing. V2.3 C12's "LLM emits JSON + legacy MD for 2 releases" was a **pre-JSON-first prerequisite** — confidence-building before JSON-as-source-of-truth. Session 4 approved 8/8/4 + 9-phase pipeline unanimously; re-litigating dual emit is anachronistic. **Alternative:** drop dual emit as standalone concern. The zustand fixture IS the structural verification for the renderer — fixtures are the correct test artifact for a deterministic renderer; live dual-emit is a separate LLM-reliability question. When the next real scan runs under the new pipeline, it produces JSON + MD by construction.

### C7: AGREE
Jinja2, structural-only fixture, pre-computed form — unanimous in prior R1, nothing in C1-C6 changes it. Settled.

---

**Pragmatist frame summary:** C1/C2/C3 are proportionate — small schema edits that fix real enforceability gaps. C4 needs a shape tweak (sibling objects, not rows). C5/C6 are where R1 reviewers over-index on migration-plan linguistic purity; "Step G" packages this over-reach. Treat C7 matrix as separate future concern, note it as claim-boundary, move on.

**VERDICT: REFINE**
