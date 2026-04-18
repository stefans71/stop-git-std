# Progress Check — Skeptic

## Verdict
**ON TRACK WITH CONDITIONS** — The architecture is sound, but compute.py has critical bugs and schema has gaps that must be fixed before renderers.

## Q1-Q6 answers

**Q1: Are we on track?**
Yes, the build order is logical. The pipeline architecture (8/8/4 classification) is well-designed. However, we must fix compute.py bugs and schema gaps before building renderers.

**Q2: Review compute.py — bugs found**
1. **C20 severity formula bug**: Missing `ships_executable_code` parameter in return dict (line 45). The function uses it but doesn't include it in output.
2. **Scorecard Q4 logic bug**: Line 116-117 has incorrect logic: `q4_color = "red" if has_warning_or_above else "amber"` — this makes Q4 always red when `has_warning_or_above` is True, but the condition should check if `has_warning_or_above` is True AND other conditions fail.
3. **Boundary case detection**: Missing `any_review_rate` threshold check (30% for amber/green boundary).
4. **F5 classification**: Missing import/export of `classify_f5_disclosure` function — it's defined but not exported or used in compute pipeline.

**Q3: Review scan-schema.json — gaps found**
1. **Missing `ships_executable_code` field** in `c20_severity` schema (line ~790).
2. **Missing `auto_load_tier` enum reference** in finding schema — should be referenced for agent rule files.
3. **Missing `f5_classification` field** in phase_3_computed schema.
4. **Schema doesn't enforce `evidence_refs` requirement** for non-OK findings — the `if/then` logic exists but may not be triggered correctly.

**Q4: Review investigation form V1.1**
Complete enough for renderers. The 23 fixes are evident: proper DP references, coverage affirmations, structured comments. All required fields for deterministic output are present. The form captures all data points needed for zustand-quality output.

**Q5: Renderer design question**
**Option C** — Use the HTML template (`GitHub-Repo-Scan-Template.html`) as a literal template with placeholder substitution. This ensures pixel-perfect match to reference implementation and maintains S8 design rules. Reverse-engineering (B) risks drift; from-scratch (A) risks missing subtle CSS classes.

**Q6: Test pipeline end-to-end on zustand?**
**YES, mandatory.** Before building renderers, we must:
1. Manually fill investigation form with zustand data
2. Run compute.py to verify outputs match zustand.md computed fields
3. Validate schema accepts the completed form
This catches integration bugs early and validates the entire pipeline.

## Additional findings

1. **Schema version mismatch**: Form uses `"schema_version": "1.1"` but schema file doesn't define version validation.
2. **Missing test coverage**: compute.py has 30 tests but doesn't cover edge cases found in bugs above.
3. **Phase dependencies unclear**: Schema doesn't enforce phase completion order (e.g., phase_4b depends on phase_4).
4. **Evidence validation**: Schema validates `evidence_refs` array but doesn't ensure referenced evidence IDs exist in phase_1.
5. **Provenance tracking**: Good — all fields have source_type comments (raw/computed/structured_llm/prose_llm).

**Action items before renderers:**
1. Fix compute.py bugs (C20, Q4, boundary cases, F5 export)
2. Patch schema gaps (missing fields, enum references)
3. Run end-to-end test with zustand data
4. Add missing test cases for edge conditions
5. Verify schema version compatibility