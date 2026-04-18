# Renderer Workstream — Cross-Reference Index

**This folder was the implementation-verification review (R1 on Steps A+B diffs). But the full renderer workstream spans 3 linked board reviews across 3 sibling folders.** If you land here looking for "where are we in the renderer build?" — read this file first.

## The 3 related board reviews (chronological)

### 1. Alignment review — `../041826-renderer-alignment/`
**Purpose:** Verify the proposed execution plan for Phase 7 (deterministic renderer) matches the V2.3 C12 4-step migration + session-4 pipeline architecture.
**Rounds:** R1 (blind) → R2 (consolidation) → R3 (deliberation on C3 auto_load_tier) → R4 (confirmation).
**Result:** ALL SIGN OFF with noted dissents. Full consolidated plan in `../041826-renderer-alignment/CONSOLIDATION.md`.
**Outputs:** 7 C-item resolutions (C1-C7) + 7-step execution plan (A through G).

### 2. Implementation verification — `./` (this folder)
**Purpose:** Verify commits `2b576bf` (Step A schema V1.1) and `75db969` (Step B Jinja2 refactor) faithfully implement the approved plan.
**Rounds:** R1.
**Result:** Split verdict — Codex BLOCK on C2 half-implementation + unapproved extras; DeepSeek APPROVE. Owner directive resolved by adopting Codex's R2 dissent position (file_sha/line_ranges/diff_anchor required-always-nullable). Fix landed in `c6531bb`.

### 3. Fixture enrichment — `../041826-fixture-enrichment/`
**Purpose:** Review 10 fix artifacts (FA-1..FA-10) for adding structural-LLM fields to `tests/fixtures/zustand-form.json`.
**Rounds:** R1.
**Result:** UNANIMOUS 3-0 APPROVE — first review using Pragmatist Sonnet 4.6 (memory correction at `feedback_claude_on_board.md`). Applied in `59224ac`.

## Commit log (Step A → D)

| Step | Commit | Description | Tests after |
|------|--------|-------------|-------------|
| A | `2b576bf` | Schema V1.0 → V1.1 (+renderer-driven $defs, stale-shape reconciliation, C2+C3 conditionals, board archive) | 107 |
| B | `75db969` | render-md.py 782 → 117 lines (Jinja2 refactor) + 15 template files | 107 |
| (fix) | `c6531bb` | C2 BLOCK resolution (file_sha/line_ranges/diff_anchor → required-always-nullable) | 107 |
| C | `59224ac` | Fixture enrichment (+310 lines of structural-LLM fields via 10 approved FAs) | 107 |
| D | `aac2b3b` | +39 render structural-assertion tests (9 new classes) | **146** |
| E | _(see verification record)_ | Validator `--report` gate clean on rendered output — no code delta, `STEP-E-verification.md` committed as the test record | 146 |

## Where we are

**Completed:** Steps A, B, C, D, **E**. All committed. 146/146 tests passing. Fixture validates clean against V1.1. Render produces all 13 section headers at 540 lines vs golden 602 (62-line gap is prose density — consistent with "prose stays sparse" rule). Validator `--report` gate exits 0 on rendered output (see `STEP-E-verification.md` for hypothesis / files / expected vs actual).

**Remaining in the workstream:**
- ~~**Step E** — Validator `--report` gate on rendered output.~~ ✅ PASS 2026-04-18. Record: `STEP-E-verification.md`.
- **Step F** (later session) — `render-html.py` using same Jinja2 template architecture. MD/HTML parity gate (PD2 validator mode, already exists).
- **Step G** (before "pipeline reliable" claim) — C7 acceptance matrix + dual-emit verification: Archon re-run + one other shape + zustand, each producing V1.1-compliant JSON + valid MD+HTML.

## Dissents carried forward

- **C2 (DeepSeek)**: preferred extending `coverage_detail.rows[]` rather than typed sibling objects. Final resolution used sibling objects. Noted.
- **C3 (DeepSeek)**: preferred Option Y (promote SD2 `domain` field now). Final resolution Option X (category-match for V1.1, `$comment` pointer to SD2 V1.2 re-binding). Noted.
- **C5+C6 (Pragmatist)**: preferred dropping Step G entirely. Final resolution: Step G exists as post-renderer milestone that does NOT block Step B/E — renderer ships on Step E, "pipeline reliable" claim gated on Step G. Noted.

## Board agent operations summary (for re-running)

See `../README.md` in the parent directory for the full agent-invocation reference. Quick recap:
- **Codex:** `sudo -u llmuser bash -c "cd /tmp && codex exec --dangerously-bypass-approvals-and-sandbox '...'"` — must be `llmuser`, must run from `/tmp`.
- **DeepSeek:** `OPENAI_API_KEY="$DEEPSEEK_API_KEY" OPENAI_BASE_URL="https://api.deepseek.com/v1" qwen -y -p "..." --model deepseek-chat` — must launch from repo dir for workspace access; transient API errors → retry once.
- **Pragmatist:** `Agent` tool with `model: "sonnet"` when Opus wrote the artifact under review; otherwise default (Opus).
- **Minimum 3 agents per round** per SOP §4. Never drop below 3.

## References

- FrontierBoard SOP: `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
- Parent pipeline architecture: `project_pipeline_architecture.md` (memory)
- V2.3 Round 3 C12 migration plan: `docs/board-review-V23-consolidation.md`
- Session 5 status: `project_session5_status.md` (memory) — what shipped in this session + what's next
