# Board Review Consolidation — Renderer Execution Plan Alignment

**Date:** 2026-04-18
**Topic:** Phase 7 deterministic renderer execution plan. Alignment check against V2.3 C12 migration plan + session 4 pipeline architecture.
**Rounds completed:** 4 (full SOP)
**Verdict:** ALL 3 SIGN OFF

## Agents

| Role | Model | How invoked |
|------|-------|-------------|
| Pragmatist | Claude Opus (subagent) | `Agent` tool, general-purpose, fresh session per round |
| Systems Thinker | Codex (GPT-5 Codex) | `sudo -u llmuser codex exec --dangerously-bypass-approvals-and-sandbox` from /tmp |
| Skeptic | DeepSeek V4 (deepseek-chat) | `qwen -y -p "..." --model deepseek-chat` from repo dir |

Per `feedback_claude_on_board.md`: Claude-as-Pragmatist was invoked only when reviewing **plans** (not Claude-authored code); the earlier tactical R1 on `render-md.py` itself skipped Pragmatist.

## Round summary

| Round | Outcome |
|-------|---------|
| **R1 Blind** | Codex + DeepSeek: both ADJUST verdicts. Identified contract drift across schema ↔ fixture ↔ renderer ↔ golden. Pragmatist skipped (Claude wrote the plan). |
| **R2 Consolidation** | All 3 agents. C1 + C7 unanimous AGREE; C2/C4/C5/C6 resolved by 2-1 facilitator tiebreak with dissents noted; C3 deferred to R3 (3-way split). |
| **R3 Deliberation** | C3 only (scope for `auto_load_tier` requirement). Two candidate options (X = category-match + defer SD2, Y = promote SD2 `domain` field now). Result: 2 agree Option X (Pragmatist, Codex), 1 agrees Option Y (DeepSeek); all 3 SIGN OFF. |
| **R4 Confirmation** | All 3 SIGN OFF on full consolidated plan. Dissents noted without blocking. |

## Final C-item resolutions

| C | Resolution | Dissent noted |
|---|------------|---------------|
| **C1** | Rename Step A → "Complete schema freeze → V1.1". Bump `schema_version`. Acknowledge this finishes migration step 1 (not step-3 prep). | None |
| **C2** | `executable_file_inventory.layer2_entries[]` entries require `file_sha` + `line_ranges` + `diff_anchor` **when security-relevant** (`dangerous_calls != None` OR `kind` in sensitive set). | Codex: preferred always-required with explicit-null fallback for reproducibility |
| **C3** | **Option X:** `auto_load_tier` required on findings where `category` matches `supply-chain/agent-rules/*`, `code/agent-rule-file`, `code/agent-rule-injection`. Add `$comment` noting V1.2 will re-bind to `domain == "agent"` per SD2 deferred roadmap. | DeepSeek: preferred Option Y (promote SD2 `domain` field NOW, bind to `domain=agent`) |
| **C4** | `coverage_detail.monorepo` + `coverage_detail.pr_target_usage` as typed sibling objects (NOT extending generic `rows[]`). | DeepSeek: preferred extending `rows[]` |
| **C5 + C6** | **Step G** = post-renderer milestone combining C7 acceptance-scan matrix + dual-emit verification. Does NOT block Step B. Renderer ships on Step E. "Pipeline reliable" claim gated on Step G. | Pragmatist: preferred dropping Step G entirely, just noting a claim-boundary |
| **C7** | Jinja2 for renderer (Step B). Fixture enrichment structural-only; prose stays sparse. Pre-computed form (no lazy compute across phases). | None |

## Final execution plan (board-approved)

1. **Step A — Complete schema freeze → V1.1** (finishes migration step 1)
   - Add `$defs` for every field the renderer already reads: `verdict_exhibits.groups`, `executable_file_inventory` (with C2 F12 fields), `pr_sample_review.rows`, `coverage_detail` (with C4 sibling objects), `evidence.entries`, `repo_vitals.rows`, `section_leads`, per-finding `body_paragraphs`/`meta_table`/`how_to_fix`/`duration_label`/`date_label`, `catalog_metadata.prior_scan_note`.
   - Enforce `auto_load_tier` per C3 Option X (category-matched).
   - Reconcile stale shapes: `action_steps`, `timeline_events`, `phase_5_prose_llm`.
   - Bump `schema_version` to `"1.1"`.
2. **Step B — Refactor `docs/render-md.py` to Jinja2** (thin ~150-line Python + `docs/templates/*.md.j2`). Existing `tests/test_render_md.py` (26 tests) should still pass.
3. **Step C — Enrich `tests/fixtures/zustand-form.json`** against V1.1 schema. Structural-LLM fields only. Prose stays sparse.
4. **Step D — Flip tests to richer structural assertions** (all 13 sections, table row counts, section order).
5. **Step E — Validator gate** — `validate-scanner-report.py --report <rendered-output>` must exit 0. Renderer ships after this.
6. **Step F (later session)** — `render-html.py` using same Jinja2 templates. MD/HTML parity (PD2 validator mode, already exists).
7. **Step G (before "pipeline reliable" claim)** — C7 acceptance matrix + dual-emit verification. Archon re-run + one other shape (FastAPI or similar Python) + zustand, each producing V1.1-compliant JSON + valid MD+HTML. Does NOT block Step E renderer ship.

## Key decisions carried forward

- **SD2 (finding `kind` + `domain` orthogonal typing)** — confirmed V1.2 trigger. C3 Option X explicitly schedules re-binding when SD2 lands.
- **Dual emit (migration step 2)** — reframed: zustand fixture = structural test; Step G's live scans = dual-emit verification. No separate dual-emit gate before Step B.
- **Contract lock discipline** — "pipeline reliable" claim requires Step G. No such claim permitted after Step E alone.

## Process notes

- Used FrontierBoard SOP `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`.
- Agents are stateless — every brief inlined all prior-round context + referenced files by absolute path.
- R1 Codex initially failed (auth expired under root); retried as `llmuser` per `feedback_board_review_brief_isolation.md`.
- R1 DeepSeek initially failed (workspace out-of-scope when launched from /tmp); retried from repo dir.
- Pragmatist/Claude skipped on code-under-review (same-model blind spot) per `feedback_claude_on_board.md`; used for plan reviews.
- Total ~40 min end-to-end across 4 rounds with parallel agents per round.

## Round artifacts

- `r1-brief.md`, `codex-r1.md`, `deepseek-r1.md` — R1 alignment check (2 agents)
- `r2-brief.md`, `pragmatist-r2.md`, `codex-r2.md`, `deepseek-r2.md` — R2 consolidation (3 agents)
- `r3-brief.md`, `pragmatist-r3.md`, `codex-r3.md`, `deepseek-r3.md` — R3 deliberation on C3 (3 agents)
- `r4-brief.md`, `pragmatist-r4.md`, `codex-r4.md`, `deepseek-r4.md` — R4 confirmation (3 agents, unanimous SIGN OFF)

## Next action

Execute Step A. Owner may choose to sequence through B-E-G in a single session or split into phased commits. The board-approved plan is durable — implementation can proceed without further board input unless new FIX NOW items surface.
