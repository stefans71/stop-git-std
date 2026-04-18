# Board R4 Confirmation — Final Renderer Execution Plan

**Round:** R4 Confirmation per FrontierBoard SOP §4-R4. Agents state `SIGN OFF` or `BLOCK`. Complete when all sign off.

**Reviewers:**
- Pragmatist (Claude) — shippability / proportionality / accuracy
- Systems Thinker (Codex) — architecture / data-flow / downstream effects
- Skeptic (DeepSeek V4) — risk / failure modes / assumptions

---

## 1. What you already signed off on (R1 + R2 + R3)

- **R1 (both non-Claude reviewers):** Unanimous ADJUST verdict on the original execution plan.
- **R2 (all 3):** REFINE verdict. C1 and C7 unanimous AGREE. C2, C4, C5, C6 resolved by 2-1 facilitator tiebreak (dissents noted). C3 deferred to R3.
- **R3 (all 3):** SIGN OFF on C3. Majority chose Option X (category-match for V1.1, `$comment` pointer to SD2 V1.2 re-binding). DeepSeek preferred Option Y but did not block.

---

## 2. Final consolidated plan

### Schema resolutions (C1-C4, C7)

| # | Resolution | Dissent noted |
|---|---|---|
| **C1** | Rename Step A: "Complete schema freeze → V1.1". Bump `schema_version`. Explicit acknowledgement this finishes migration step 1. | None |
| **C2** | `executable_file_inventory.layer2_entries[]` entries require `file_sha` + `line_ranges` + `diff_anchor` **when security-relevant** (`dangerous_calls != None` OR `kind` in sensitive set). | Codex: preferred always-required with explicit-null fallback for reproducibility |
| **C3** | `auto_load_tier` required on findings where `category` matches `supply-chain/agent-rules/*`, `code/agent-rule-file`, `code/agent-rule-injection`. Add `$comment` noting V1.2 will re-bind to `domain == "agent"` per SD2. | DeepSeek: preferred Option Y (promote SD2 `domain` field NOW, bind to domain=agent) |
| **C4** | `coverage_detail.monorepo` + `coverage_detail.pr_target_usage` as typed sibling objects (NOT extending generic `rows[]`). | DeepSeek: preferred extending `rows[]` |
| **C7** | Jinja2 for renderer (Step B). Fixture enrichment structural-only; prose stays sparse. Pre-computed form (no lazy compute). | None |

### Process resolutions (C5 + C6)

| # | Resolution | Dissent noted |
|---|---|---|
| **C5+C6** | **Step G** exists as a post-renderer milestone = C7 acceptance-scan matrix + dual-emit verification. Does NOT block Step B (Jinja2 refactor). Renderer ships on Step E. The "pipeline reliable" claim is gated on Step G. | Pragmatist: preferred dropping Step G entirely, just note a claim-boundary |

### Final execution order

1. **Step A — Complete schema freeze → V1.1** (finishes migration step 1)
   - Add missing `$defs` for every field the renderer already reads: `verdict_exhibits.groups`, `executable_file_inventory` (with C2 F12 fields conditional), `pr_sample_review.rows`, `coverage_detail` (with C4 sibling objects), `evidence.entries`, `repo_vitals.rows`, `section_leads`, per-finding `body_paragraphs`/`meta_table`/`how_to_fix`/`duration_label`/`date_label`, `catalog_metadata.prior_scan_note`.
   - Require `auto_load_tier` on agent-rule-file findings per C3 Option X.
   - Reconcile stale shapes: `action_steps`, `timeline_events`, `phase_5_prose_llm`.
   - Bump `schema_version` to `"1.1"`.

2. **Step B — Refactor `docs/render-md.py` to Jinja2** (~150 lines Python + `docs/templates/*.md.j2`). Existing tests (`tests/test_render_md.py`, 26 tests) should still pass.

3. **Step C — Enrich `tests/fixtures/zustand-form.json`** against V1.1 schema. **Structural-LLM fields only.** Prose fields stay sparse.

4. **Step D — Flip tests to richer structural assertions** (all 13 sections present, table row counts match golden, section order matches).

5. **Step E — Validator gate**: `validate-scanner-report.py --report <rendered-output>` must pass. Renderer ships after this.

6. **Step F (later session)** — `render-html.py` using same Jinja2 templates. MD/HTML parity gate (PD2, already in validator).

7. **Step G (before "pipeline reliable" claim)** — C7 acceptance matrix: Archon re-run + one other shape (FastAPI or similar) + zustand. Each scan verifies LLM can emit V1.1-compliant JSON AND renderer produces valid MD+HTML. This is the dual-emit verification AND the acceptance-matrix rolled into one. Does NOT block Step E renderer ship.

---

## 3. Your task — R4 Confirmation

Per SOP §4-R4: respond `SIGN OFF` or `BLOCK` on the **entire consolidated plan above**.

- **SIGN OFF** = you accept the plan as written. Dissents are noted but you are not blocking.
- **BLOCK** = there is something in the final plan that would cause real harm. You must include: (a) which C-item(s) you block on, (b) the specific rationale, (c) what would unblock.

**Response format:**

```
### R4 Confirmation
[One-sentence summary of your position]

[If BLOCK only: enumerate the specific blocking items and rationale.]

VERDICT: SIGN OFF  (or: VERDICT: BLOCK — <summary>)
```

**Save output:**
- Pragmatist (subagent): inline in final message
- Systems Thinker (Codex): `/tmp/codex-r4.md`
- Skeptic (DeepSeek V4): `.board-review-temp/renderer-alignment/deepseek-r4.md`

---

## 4. Context reminders

- Dissents DO NOT mean BLOCK. You can SIGN OFF with a noted disagreement.
- BLOCK is for issues that would actually harm the work — not architectural preferences you stated in R2.
- Per SOP §4-R4: "Complete when all sign off, or owner overrides remaining blocks with rationale."
- Fix-artifact authoring is **NOT** required in this review — all 7 C-items are plan-level items, not concrete-code changes. Implementation will happen after R4 confirmation.

---

## 5. Files to read if you need refresher

- `/root/tinkering/stop-git-std/.board-review-temp/renderer-alignment/r2-brief.md` — full R2 consolidation with C1-C7 context
- `/root/tinkering/stop-git-std/.board-review-temp/renderer-alignment/r3-brief.md` — C3 deliberation options
- `/root/tinkering/stop-git-std/.board-review-temp/renderer-alignment/pragmatist-r2.md`, `codex-r2.md`, `deepseek-r2.md` — prior R2 responses
- `/root/tinkering/stop-git-std/.board-review-temp/renderer-alignment/pragmatist-r3.md`, `codex-r3.md`, `deepseek-r3.md` — R3 responses
- `/root/tinkering/stop-git-std/docs/board-review-V23-consolidation.md` — original V2.3 C9/C11 source requirements
- `/root/tinkering/stop-git-std/docs/scan-schema.json` — current schema V1.0

Everything important is already inlined above. Files are for verification if needed.
