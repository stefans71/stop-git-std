# Pragmatist (Claude Sonnet 4.6) — FA Review R1

**Reviewer:** Pragmatist · Claude Sonnet 4.6 (fresh subagent session)
**Lens:** Shippability / proportionality / accuracy
**Round:** R1 only (fix-artifact review)

---

### V1: APPROVE — Shape correctness

All 10 FAs match the V1.1 schema. Summary checks:

- **FA-1**: `section_leads.section_01` → `$defs/section_lead`. Both `pill_row` + `summary` are valid optional strings. Clean.
- **FA-2**: `verdict_exhibits.groups[]` → `$defs/verdict_exhibit_group`. Required `headline` + `items` present. Each item carries required `tag` + `claim`.
- **FA-3**: `executable_file_inventory` → container + `$defs/executable_file_inventory_entry`. All 6 required fields present on every entry (path/kind/runtime + file_sha/line_ranges/diff_anchor). Benign rows use HEAD_SHA + null locators; devtools.ts uses SHA + line + anchor. Correct.
- **FA-4**: `pr_sample_review.rows[]` → `$defs/pr_sample_review_row`. 8 rows, all with required `number/what/author/merger`. `flagged` typed boolean|null — sample uses true/false correctly.
- **FA-5**: `timeline_intro` is `["string", "null"]` directly on `phase_4_structured_llm`. Single string addition. Clean.
- **FA-6**: `repo_vitals.rows[]` → `$defs/repo_vitals_row`. Required `metric` + `value` present; `note` optional.
- **FA-7**: `coverage_detail` + `coverage_intro` + `coverage_gaps` all schema-valid. `pr_target_usage.usage_count: 0` satisfies required-integer rule.
- **FA-8**: Items ref `$defs/evidence` with required id/claim/command/result/classification. E1 sample carries all 5 plus optional command_lang/result_lang/result_truncated.
- **FA-9**: Four optional fields added to existing findings; `meta_table[]` → `$defs/meta_table_row` (required label+value on each row). No added `body_paragraphs`.
- **FA-10**: 6 coverage cells, all `status` enum values valid (ok/not_queried/not_available/blocked).

**Brief imprecision note:** FA-8's "Schema ref: `#/$defs/evidence`" technically points to the item def, not the container at `phase_4_structured_llm.evidence`. Not a blocker — the proposed JSON structure is correct against the actual schema — just brief-authoring sloppiness.

### V2: APPROVE — Coverage completeness

After all 10 FAs apply, 8 sections gain content: §01 (FA-1 preferred path), §02 (FA-9 enrichment), §02A (FA-3, previously dark), §03 (FA-4 richer table), §04 (FA-5 intro), §05 (FA-6, previously dark), §06 (FA-7 + FA-10, previously dark), §Verdict exhibits (FA-2), §07 (FA-8, previously dark). No gaps identified.

### V3: APPROVE — Prose discipline

No FA introduces new `body_paragraphs[]`, new `what_this_means`/`what_this_does_not_mean` on F2/F3/F4, or other prose-LLM expansion. All added strings are one-line or two-sentence — not multi-paragraph. FA-9's F0 `how_to_fix` is one imperative paragraph with a markdown link — but `how_to_fix` is a distinct functional field from narrative prose; correct home for this content.

### V4: APPROVE — C2 compliance on FA-3

Faithful implementation of the 2026-04-18 owner directive (file_sha/line_ranges/diff_anchor required on every entry, null for genuinely unresolvable). Benign entries emit `file_sha = HEAD_SHA` + `line_ranges = null` + `diff_anchor = null` — null used SEMANTICALLY (no applicable lines), not as "didn't try." Not smuggling in a `kind`-based sensitive interpretation.

### V5: APPROVE — References resolve

E1 and E3 (referenced by existing `priority_evidence.selections`) are explicitly in FA-8's listed entries. Also closes currently-dangling finding-level `evidence_refs` (E1-E4).

### V6: APPROVE — No unintended drift

All FAs additive. FA-9 enriches existing finding objects with schema-optional fields; no existing field overwritten. FA-10 populates the currently-empty `coverage_status.cells` — the only mutation of a non-empty-by-schema value, and the 6 cells are correctly shaped. No out-of-schema keys introduced.

---

### Per-FA summary

- **FA-1**: APPROVE — Correct `section_lead` shape; minimal prose; enables §01 preferred path.
- **FA-2**: APPROVE — Correct exhibit-group shapes; 1-sentence claims; enables §Verdict exhibits.
- **FA-3**: APPROVE — C2 implemented faithfully; 13 entries enable §02A; null semantics correct.
- **FA-4**: APPROVE — 8 rows, all required fields; enables §03 richer table.
- **FA-5**: APPROVE — Single string; enables §04 intro blockquote.
- **FA-6**: APPROVE — ~18 rows mirrors golden §05; enables §05.
- **FA-7**: APPROVE — Three structured additions; `pr_target_usage.usage_count=0` required-field satisfied; enables §06 main content path.
- **FA-8**: APPROVE — 9 entries correctly shaped; resolves priority_evidence references; enables §07.
- **FA-9**: APPROVE — Optional fields only; no prose expansion; enables §02 card enrichment.
- **FA-10**: APPROVE — Populates empty `coverage_status.cells` with enum-valid `status`; enables §06 fallback + dedup.

---

**VERDICT: APPROVE all FAs**

All 10 are structurally correct, schema-conformant, additive-only, and proportionate. Scope (~490 lines of JSON) is justified: these fields are what the renderer needs to emit the 4 previously-dark sections (§02A, §05, §06, §07) plus enrich the 6 that already render. The 107-test suite covered structural validation; it was silent on these sections because the fields were absent. These FAs close that gap. No FA is over-reach relative to the renderer contract. Proceed to apply.
