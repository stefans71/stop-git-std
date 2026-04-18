# Board Verification — Step A + Step B Implementation Diffs

**Task:** Verify the git diffs for Step A (schema V1.1, commit `2b576bf`) and Step B (Jinja2 refactor, commit `75db969`) faithfully implement the board-approved plan. This is an **implementation verification review**, NOT a re-design.

**Reviewers:** Codex (Systems Thinker) + DeepSeek (Skeptic). Pragmatist/Claude skipped — Claude authored both the plan and the implementation, same-model review is a blind spot.

**Round:** R1 only. Single pass. If both AGREE with no drift, we proceed to Step C (fixture enrichment).

**Output verdict per reviewer:**
- `AGREE` — implementation matches the approved plan, no drift
- `FLAG` — note specific drift items (missing work, unapproved additions, semantic errors in conditional rules) but not blocking
- `BLOCK` — implementation diverges from plan in a way that must be corrected before Step C

---

## 1. The approved plan (what you already signed off on)

From `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` — all 3 agents SIGN OFF across 4 rounds on these C-item resolutions:

**C1** — Rename Step A → "Complete schema freeze → V1.1". Bump `schema_version`. Acknowledge this finishes migration step 1 (not step-3 prep).

**C2** — `executable_file_inventory.layer2_entries[]` entries require `file_sha` + `line_ranges` + `diff_anchor` **when security-relevant** (`dangerous_calls != None` OR `kind` in sensitive set). *Codex dissent: preferred always-required with explicit-null fallback.*

**C3** — Option X: `auto_load_tier` required on findings where `category` matches `supply-chain/agent-rules/*`, `code/agent-rule-file`, `code/agent-rule-injection`. Add `$comment` noting V1.2 will re-bind to `domain == "agent"` per SD2. *DeepSeek dissent: preferred Option Y (promote SD2 now).*

**C4** — `coverage_detail.monorepo` + `coverage_detail.pr_target_usage` as typed sibling objects (NOT extending generic `rows[]`). *DeepSeek dissent: preferred extending `rows[]`.*

**C5 + C6** — Step G exists as post-renderer milestone (C7 acceptance matrix + dual-emit verification). Does NOT block Step B. Renderer ships on Step E.

**C7** — Jinja2 for renderer (Step B). Fixture enrichment structural-only; prose stays sparse. Pre-computed form.

**Step B scope (the Jinja2 refactor):** ~150-line thin Python + `docs/templates/*.md.j2` partials. Existing 26-test `tests/test_render_md.py` must still pass. Structural behavior preserved.

**Additional plan items (from Step A brief):** Reconcile stale shapes (`action_steps`, `timeline_events`, `phase_5_prose_llm`). Add `$defs` for every field the renderer reads (verdict_exhibits, executable_file_inventory, pr_sample_review, coverage_detail, evidence.entries, repo_vitals, section_leads, timeline_intro, evidence_intro, coverage_intro, coverage_gaps, catalog_metadata.prior_scan_note, per-finding body_paragraphs/meta_table/how_to_fix/duration_label/date_label).

---

## 2. The implementation (git diffs)

### Commit `2b576bf` — Step A (schema V1.1)

```
Schema freeze V1.1: renderer-driven $defs, stale-shape reconciliation, C2+C3 conditionals

17 files changed, 1308 insertions(+), 36 deletions(-)

docs/scan-schema.json                                                 | 430 +++++++++++++++++++--
docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md | (new)
docs/External-Board-Reviews/041826-renderer-alignment/*.md            | (new — board record)
```

- Schema went from 1054 lines to 1412 lines (+358 lines net for V1.1 work — archive files account for the rest)
- Fixture validates clean against V1.1 (9 errors on V1.0 → 0 errors on V1.1)
- 107/107 tests still passing

### Commit `75db969` — Step B (Jinja2 refactor)

```
Refactor render-md.py to Jinja2 (Step B of renderer plan)

16 files changed, 639 insertions(+), 782 deletions(-)

docs/render-md.py                             | 782 → 117 lines (93% rewrite)
docs/templates/scan-report.md.j2              | 14 lines (new top-level)
docs/templates/partials/*.md.j2 (14 files)    | 508 lines total (new)
```

- Python shim: **117 lines** (target was ~150)
- Templates: 14 partials + 1 top-level = 522 lines across 15 template files
- 107/107 tests passing (26 render tests included)

---

## 3. What I need you to verify

For each numbered check below: respond `AGREE` / `FLAG` / `BLOCK`.

### V1 — C1 execution
Confirm: schema has a top-level `$comment` field explaining V1.1 as schema-freeze repair with board review reference. Schema structure unchanged where not required.

### V2 — C2 execution
Confirm the schema enforces C2: on `executable_file_inventory_entry`, `file_sha` + `line_ranges` + `diff_anchor` are required when `dangerous_calls` is present and non-empty. Check the `allOf` / `if/then` logic is semantically correct (pattern matching, not just property presence).

### V3 — C3 execution
Confirm the schema enforces C3 Option X: on `finding`, `auto_load_tier` is required when `category` matches `supply-chain/agent-rules|code/agent-rule-file|code/agent-rule-injection` patterns. Check the `$comment` references V1.2 SD2 re-binding. Check the regex pattern matches the board's specified prefixes. Check the old `if/then` (evidence_refs required when severity != OK) still works — combined via `allOf`.

### V4 — C4 execution
Confirm `coverage_detail.monorepo` and `coverage_detail.pr_target_usage` are typed sibling objects (NOT added as rows in `coverage_detail.rows[]`). Check their internal shapes support V2.3 Round 3 C11 requirements (inner_package_count, pr_target usage_count even when 0).

### V5 — stale shape reconciliation
Confirm the schema updates for:
- `timeline_event`: `tone`/`note` shape (was `severity`/`description`)
- `action_step`: `step`/`headline`/`severity`/`command` shape (was `number`/`type`/`title`)
- `meta_table_row`: `label`/`value` (was `key`/`value`/`badge`)
- `phase_5_prose_llm.per_finding_prose.entries[]`: typed items with `finding_id`, `body_paragraphs[]`, `what_we_observed`, `what_this_means`, `what_this_does_not_mean`

### V6 — new $defs
Confirm schema adds `$defs` for all renderer-driven structures listed in §1. Check there are no silent drops (things the renderer reads but schema still doesn't describe).

### V7 — Jinja2 thin shim
Confirm `docs/render-md.py` is ~150 lines, does only data loading + env setup + render, and exposes helpers as globals. No per-section formatting logic in Python.

### V8 — Template structure
Confirm `docs/templates/` has one partial per section, top-level just composes. Check template `{%- -%}` whitespace control is consistent. Check templates use form fields that exist in the V1.1 schema (no references to fields not in schema).

### V9 — Test preservation
Confirm all 26 tests in `tests/test_render_md.py` still pass. The Jinja2 refactor should not change structural output — only its implementation.

### V10 — Drift audit
Flag anything added to either commit that wasn't in the approved plan. Flag anything in the plan that didn't land. Examples of drift that would matter:
- New `$defs` beyond what the renderer reads
- Schema fields marked `required` that weren't specified in C1-C7
- Template features (macros, filters) beyond what's needed for the current sections
- C-items only partially implemented

### V11 — Ready for Step C?
Confirm the schema V1.1 + Jinja2 renderer are a stable foundation for Step C (fixture enrichment with structural-LLM fields). Specifically:
- Do the new `$defs` have enough shape to guide fixture authoring?
- Does the renderer gracefully handle the sections that currently skip (§02A, §05, §06, §07)?

---

## 4. Files to read

All in `/root/tinkering/stop-git-std/`:

- `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` — the approved plan
- `docs/scan-schema.json` — post-Step-A (1412 lines)
- `docs/render-md.py` — post-Step-B (117 lines)
- `docs/templates/scan-report.md.j2` — top-level template
- `docs/templates/partials/*.md.j2` — 14 partials
- `tests/test_render_md.py` — 26 tests
- `tests/fixtures/zustand-form.json` — fixture (validates clean against V1.1)
- `tests/render_zustand_output.md` or run `python3 docs/render-md.py tests/fixtures/zustand-form.json` to see current output

**Git commands for diffs:**
```bash
git show 2b576bf -- docs/scan-schema.json  # Step A schema diff
git show 75db969                            # Step B Jinja2 refactor
git log --oneline -5                        # recent commit history
```

---

## 5. Output format

```
## Implementation Verification — <Role>

### V1 — C1 execution: AGREE / FLAG / BLOCK
[1-2 sentences.]

### V2 — C2 execution: AGREE / FLAG / BLOCK
[1-2 sentences. If FLAG, state the specific drift or semantic issue.]

...

### V11 — Ready for Step C: AGREE / FLAG / BLOCK
[1-2 sentences.]

### Drift list (if any)
- Item 1: what it is, impact
- ...

VERDICT: APPROVE (no blocking drift — proceed to Step C) / REFINE (fix flagged items first) / BLOCK (plan-implementation divergence requires fix)
```

**Save output:**
- Codex: `/tmp/codex-impl-verify.md`
- DeepSeek: `.board-review-temp/renderer-impl-verify/deepseek-impl-verify.md`
