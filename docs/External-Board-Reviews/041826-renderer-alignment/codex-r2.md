### C1: AGREE
The rename is correct. The current repo state shows `scan-schema.json` still missing renderer-driving structures while `render-md.py` already consumes them, so Step A is finishing schema freeze in practice, not merely preparing for renderer work.

### C2: MODIFY
The required fields are right, but I would not make them conditional on a renderer-facing heuristic like `dangerous_calls != "None"`. Require `file_sha`, `line_ranges`, and `diff_anchor` for every `layer2_entries[]` row that is emitted at all, and allow explicitly null or sentinel values only when a scan truly cannot resolve them; otherwise you create a branchy contract and lose reproducibility exactly on the rows users will compare most closely.

### C3: MODIFY
Requiring `auto_load_tier` only by category-pattern matching is too soft, because category strings are taxonomy policy and can drift. Require it on any finding or structured card representing an agent-rule/config file artifact, with category-based detection as one implementation path but not the schema boundary; if you cannot isolate that subtype cleanly yet, require it on all findings whose evidence points at agent-rule files rather than all findings globally.

### C4: MODIFY
The coverage extension is needed, but I would keep monorepo and `pull_request_target` as explicit structured objects, not overload generic `coverage_detail.rows[]`. A dedicated `coverage_detail.monorepo` object and `coverage_detail.pr_target_usage` object keeps the contract stable, lets the renderer print those lines deterministically, and avoids teaching consumers to infer semantics from semi-freeform row labels.

### C5: AGREE
Zustand alone is not enough to claim the contract is locked or the pipeline is reliable. The acceptance matrix is the right deferred gate because it tests shape diversity, not just one enriched fixture.

### C6: AGREE
Combining the dual-emit proof with Step G is the right compromise. It keeps Step B unblocked, but it also avoids pretending the migration overlap was already satisfied before there is live evidence across multiple scan shapes.

### C7: AGREE
Nothing in C1-C6 changes the earlier renderer tactics. Jinja2, structural-only fixture enrichment, and pre-computed Phase 3 remain the correct boundaries.

VERDICT: REFINE
