# Progress Check -- Pragmatist

## Verdict: ON TRACK WITH CONDITIONS

Fix 3 bugs in compute.py and 1 schema gap before building renderers. None are architectural -- all are localized fixes. The build order is sound, the form is complete, and the pipeline design is clean.

## Q1: Build order assessment

The build order is correct. Tests before renderers (item 4 before item 7) was the right call -- the validator test suite already caught real bugs in 4 existing scans. The pipeline flows logically: data lineage map informed the schema, the schema informed compute.py, compute.py tests validate the decision trees. Renderers are the right next step. Nothing is missing before building them, provided the 3 compute.py bugs below are fixed first.

## Q2: compute.py review (bugs/edge cases)

**Bug 1 -- Q4 dead code (line 136).** `compute_scorecard_cells`, the "Is it safe out of the box?" block:
```python
elif has_warning_or_above:
    q4_color = "red" if has_warning_or_above else "amber"
```
The `if has_warning_or_above` guard on the elif already guarantees `has_warning_or_above` is True, so the ternary always returns `"red"`. The `else "amber"` branch is unreachable. Per the V2.4 calibration table, red = "any Critical finding on default install path" and amber = "any unverified channel or finding for specific user group." The current code collapses both into red. Fix: the elif should distinguish Critical from Warning-level findings, or this branch should just be `q4_color = "red"` with amber handled in the else clause below (which it already is). As written, the else clause (lines 138-139) producing amber is correct for the "no warnings but unverified channels" case, but Q4 has no input for "unverified channels" -- it only receives `has_warning_or_above`. This means Q4 cannot produce amber when channels are unverified. The function signature needs an `any_channel_unverified: bool` parameter.

**Bug 2 -- Q1 Red threshold mismatch (lines 96-106).** The V2.4 prompt says Red fires when `any-review < 30%` OR (solo-maintainer AND `any-review < 40%`). The code implements `any_rev < 50` and `formal < 20` as the NOT-amber boundary, which means anything below 50/20 falls to red. But the prompt says Red at `any-review < 30%`. A repo with `any_review=35%` and `formal=15%` should be Red per the prompt (any-review < 30% is false, but formal < 20% is true -- however the prompt's Red rule doesn't mention formal at all for the Red gate). The code's fall-through logic actually produces a stricter result than the prompt specifies. Additionally, the solo-maintainer context (>80% contributor with any-review < 40%) is not checked at all -- `compute_scorecard_cells` doesn't receive a `is_solo_maintainer` parameter.

**Bug 3 -- Boundary case `would_change_to` is inverted (line 271).** In `compute_boundary_cases`, for formal review rate near 30%:
```python
"would_change_to": "amber" if formal_review_rate >= 30 else "green"
```
If `formal_review_rate=32` (above threshold, currently contributing to green eligibility), and it dropped below 30, it would change TO amber. So `would_change_to` should be `"amber"` when the value is currently >= 30 (i.e., "if this drops, you'd become amber"). That part is correct. But if `formal_review_rate=28` (below threshold), the `would_change_to` says `"green"` -- meaning "if this rises above 30, you'd become green." That is also correct semantically. So this is actually fine on re-examination. No bug here -- retracted.

**Edge case -- `classify_f5_disclosure` never returns "properly disclosed."** The docstring mentions it but the function only returns "unadvertised" or "silent". The caller must handle the "advisory exists" case before calling this function. This is acceptable if documented, but the docstring is misleading.

**Edge case -- `compute_c20_severity` treats 403 as protection-present.** Line 39: `no_classic = classic_protection_status == 404`. A 403 means "unknown" per the V2.4 prompt ("401/403 = insufficient permissions to check, answer is unknown, do not speculate"). Treating 403 as "not 404, therefore protection exists" is conservative (avoids false positives), which matches the prompt's intent. This is correct behavior.

## Q3: scan-schema.json review (gaps)

**Gap 1 -- Q4 scorecard missing inputs.** The scorecard cell for `is_it_safe_out_of_the_box` has inputs `all_channels_pinned`, `artifact_verified`, `has_warning_or_above_finding` -- but compute.py Q4 cannot distinguish "Warning on default install" (red) from "Warning on specific user group" (amber). The schema should add `has_critical_on_default_path: boolean` or the existing `has_warning_or_above` should be split.

**Gap 2 -- No `auto_load_tier` on finding entries.** The prompt requires auto-load tier on every agent-rule-file finding card (S8/C9). The `finding` $def has no `auto_load_tier` field. Add it as an optional field on the finding object so the renderer can emit tier labels.

**Gap 3 -- `per_finding_prose` entries untyped.** `phase_5_prose_llm.per_finding_prose.entries` is `"type": "array"` with no `items` constraint. Should reference a $def with `finding_id`, `body_paragraphs`, `what_this_means`, `what_this_does_not_mean` to match the V2.4 prompt's per-finding prose requirements.

The schema is otherwise solid. The phase structure matches the pipeline, provenance enums are correct, and the conditional `evidence_refs` requirement on non-OK findings (lines 283-290) is a good enforcement.

## Q4: Investigation form completeness

The form is complete for renderer consumption. All 118 data points from the lineage map have corresponding fields. The `$comment` annotations with DP-numbers provide good traceability. The 23 fixes from the 3-model review are visible (structured capture for agent-rule files, paste blocks, distribution channels, install scripts, artifact verification, batch merge detection, defensive configs, coverage affirmations).

One observation: the form's `phase_4_structured_llm.findings.entries` is an empty array. The renderer will need to handle the case where findings reference evidence by `evidence_refs` IDs -- but there is no top-level `evidence` array in the form. Evidence appears to live inside `phase_1_raw_capture` scattered across sections. The renderer will need a lookup mechanism. This is a design decision for the renderer, not a form gap, but worth noting now.

## Q5: Renderer design recommendation

**Option C** -- template with placeholder substitution. Reasons:

1. The HTML template already exists and has been validated against 6 scans. The CSS design system is 824 lines of tested styles. Starting from scratch (A) or reverse-engineering (B) throws away proven structure.
2. The JSON form's field names map cleanly to template placeholders. The renderer is mechanical: iterate findings, emit cards with the right CSS classes, fill scorecard cells.
3. Template substitution is the easiest to test -- you can diff the renderer's output against a known-good scan (zustand.html) to catch structural regressions.
4. Jinja2 or simple string templating keeps the renderer under 300 lines and fully deterministic.

Start with render-md.py (simpler output format, canonical source), then render-html.py using the template.

## Q6: End-to-end test before renderers?

Yes -- this is the single most valuable thing to do before writing renderer code. Manually fill the investigation form with zustand data, run compute.py, and verify computed outputs match zustand.md. This gives you:

1. A concrete test fixture (zustand-filled-form.json) that becomes the renderer's first integration test.
2. Validation that compute.py's thresholds produce the exact scorecard colors and C20 severity that the existing zustand scan shows.
3. A known-good JSON that exercises every renderer code path (zustand has OK + Warning + Info findings, a solo maintainer, no C20 finding, all 4 scorecard cells populated).

Cost: ~30 minutes to fill the form manually. Payoff: catches any remaining compute.py bugs and gives the renderer a golden-file test from day one.

## Additional findings

1. The `compute_verdict` function maps Info -> "Caution". This means any repo with even a single Info finding (which is nearly all of them) gets a "Caution" verdict. This may be intentional (the prompt says Info findings are still findings), but it means "Clean" verdict is nearly impossible. Verify this matches the intended behavior across existing scans.

2. The `compute_exhibit_grouping` function checks `f.get("category", "").startswith(("vuln/", "supply-chain/"))` but the finding category values in the form aren't constrained to use these prefixes. The schema has `"category": { "type": "string" }` with no enum or pattern. If the LLM writes categories like `"vulnerability"` instead of `"vuln/..."`, exhibit grouping silently produces empty exhibits. Add a category vocabulary to the schema or make grouping more flexible.

3. Tests: 67 passing tests is strong for this stage. The test-before-code discipline is paying off. Keep it for the renderers -- write `test_render_md.py` with the zustand fixture before writing `render_md.py`.
