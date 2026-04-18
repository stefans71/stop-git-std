# CONSOLIDATION — Step F Alignment Validation + Step G Readiness

**Date:** 2026-04-18
**Reviewed:** Commit `402f933` (Step F: HTML renderer + 2 new V1.1 fixtures) → owner fixes in commit `ce698d4` (Step F R3 fixes)
**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
**Rounds:** R1 Blind → R2 Consolidation → R3 Deliberation → R4 Confirmation (full 4-round SOP, not expedited — R1 was split 1-BLOCK-2-DISSENT)
**Board:** Pragmatist (Claude Sonnet 4.6, per same-model rule since Opus wrote Step F), Systems Thinker (Codex GPT-5), Skeptic (DeepSeek V4 via Qwen CLI)

---

## Final verdict

**SIGN OFF.** Step F is ready. Step G is next per the 7-step renderer plan (`../041826-renderer-alignment/CONSOLIDATION.md`), with a documented "before Step G runs" queue of 3 items: U-1 (documentation integration), U-3/FX-4 (fixture provenance via separate file), U-5/PD3 (bundle/citation validator).

| Agent | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Pragmatist | SIGN OFF W/ DISSENTS (missed FN-B) | SIGN OFF W/ DISSENTS (concedes FN-B with own 37-count verification) | **SIGN OFF** | **SIGN OFF** |
| Codex | **BLOCK** (CSS defect + prior_scan_note) | SIGN OFF W/ DISSENTS (fixes accepted) | SIGN OFF W/ DISSENTS | **SIGN OFF W/ DISSENTS** (bookkeeping nit only) |
| DeepSeek | SIGN OFF W/ DISSENTS (effectively BLOCK-for-G) | SIGN OFF W/ DISSENTS (concedes FN-C) | SIGN OFF W/ DISSENTS | **SIGN OFF** |

**Trajectory:** R1 split → R2 unanimous on FIX NOW set → R3 owner-authored fix artifacts adopted (with 2 board-driven adjustments) → R4 all three confirm applied state matches approved set.

---

## Fix set applied (commit `ce698d4`)

### FX-1 — `docs/templates-html/partials/catalog.html.j2`
Removed `| safe` on `{{ prior }}` output. Changed fallback from `'None &mdash; first scan of this repo.'` to `'None \u2014 first scan of this repo.'` (Unicode em-dash literal — the entity would re-escape through autoescape to `&amp;mdash;`). Added block comment documenting the autoescape constraint.

**Rationale:** `prior_scan_note` is Phase 4 structured LLM text. `| safe` bypassed autoescape, creating an XSS vector once Step G flows real LLM-generated content through this field.

**Origin:** Pragmatist R1 FN-1, Codex R1 FN-2, DeepSeek R1 #1. Unanimous FIX NOW across all rounds.

### FX-2 — `docs/templates-html/scan-report.html.j2`
Added `| safe` to `{{ css_content }}`. Added block comment documenting the trust boundary (css_content is loaded from `docs/scanner-design-system.css` via `_load_css()` — a static disk file, not LLM or user input). The comment also serves as D-6 (CSS autoescape path documentation).

**Rationale:** Autoescape was HTML-encoding single quotes inside the embedded `<style>` block — 37 occurrences of `&#39;` in zustand pre-fix, corrupting font-family declarations, pseudo-element content, and SVG data URIs. Browsers do NOT decode entities inside `<style>`.

**Origin:** Codex R1 FN-1, DeepSeek R1 #3. Pragmatist dismissed in R1 ("CSS doesn't generally contain characters autoescape would corrupt"); conceded in R2 with own 37-count verification.

### FX-3 — `docs/validate-scanner-report.py` Pattern 3
Added H3 finding-card parser using strip-tags-first approach (Codex R3 preferred, adopted via owner directive over DeepSeek's DOTALL+non-greedy regex and owner's initial regex). For each `<h3>...</h3>`, strips nested tags then matches F-ID prefix.

**Rationale:** Parity check was producing false-negative "MD findings missing from HTML" warnings on every zustand-shape scan (including the reference golden). The existing Pattern 2 (`F<N> — <Severity>`) never matched because renderer emits `F<N> — <Title>`. Pattern 3 closes that gap.

**Origin:** DeepSeek R1 #2 (FIX NOW), Pragmatist R1 + Codex R1 (DEFER). Owner elevated to FIX NOW in R3 to achieve Step G's "zero warnings" acceptance criterion.

### FX-3b — emergent validator bug fix (same commit)
Removed redundant `html_body = re.sub(r"/\*.*?\*/", "", html_body, flags=re.DOTALL)` from `check_parity`. CSS is already stripped via the `<style>` block regex run one line earlier. The `/\*.*?\*/` pass was over-matching body content: shell globs (`/plugins/*/hooks/*.js`) and legitimate code comments in evidence text (`/* best-effort on Windows */`) were pairing across the document, eating finding cards.

**Rationale:** Found during R3 post-apply verification. Pattern 3 found 0 H3s on caveman despite F-starting H3s clearly in the source. Root cause: `/\*.*?\*/` with DOTALL was eating everything between caveman's shell-glob evidence text. Latent bug — only surfaced on fixtures with these patterns (zustand passed by accident).

**Origin:** Emergent during R3 verification, scope-sanctioned by board in R4 (all 3 agents confirmed scope-appropriate for this commit).

---

## Unblocked items — disposition

| ID | Item | R3 Vote | R4 Confirmed | Status |
|---|---|---|---|---|
| U-1 | Update CLAUDE.md + SCANNER-OPERATOR-GUIDE.md for render-{md,html}.py | APPLY NEXT COMMIT (3-0) | Yes | Queued before Step G |
| U-2 | Parity regex (FX-3) | APPLY THIS COMMIT (3-0) | Applied | ✅ Done |
| U-3 | Fixture provenance tag | APPLY NEXT COMMIT (via separate `tests/fixtures/provenance.json`, not schema — Codex architectural position adopted over Pragmatist+DeepSeek's schema-mutation preference) | Yes | Queued before Step G |
| U-4 | CSS autoescape documentation (part of FX-2 comment) | APPLY THIS COMMIT (3-0) | Applied | ✅ Done |
| U-5 | PD3 bundle/citation validator | APPLY NEXT COMMIT (2-1 — Codex+DeepSeek NEXT, Pragmatist DEFER-with-criterion; stronger 2-1 majority wins) | Yes | Queued before Step G |
| U-6 | Template-source `\| safe` lint | DEFER post-Step-G (3-0) | Yes | Deferred |
| U-7 | `formal_review_rate` phase classification | DEFER post-Step-G (3-0) | Yes | Deferred |
| U-8 | Externalize `adjustFont` script | DEFER post-Step-G (3-0) | Yes | Deferred |
| U-9 | Duplicated prose-like fields in Phase 4 | DEFER post-Step-G (3-0) | Yes | Deferred |

**Split resolutions:**
- **FX-4 approach (U-3):** Codex's separate-file `tests/fixtures/provenance.json` adopted over Pragmatist+DeepSeek's schema mutation. Architectural rationale: `docs/scan-schema.json` describes live scan artifacts; fixture provenance is test-harness metadata; underscore-prefixed optional fields still pollute the production schema contract.
- **FX-3 approach:** Codex's strip-tags-first regex adopted over owner's initial and DeepSeek's DOTALL regex. Robustness rationale: scopes to one H3 at a time, handles arbitrary nesting, no false-positive risk from non-greedy `.*?` matching beyond an H3.
- **PD3 timing:** APPLY NEXT COMMIT (2-1) instead of Pragmatist's DEFER-with-criterion. Stronger gate: bundle validator must exist BEFORE first Step G scan runs, not "triggered by first scan."

---

## Prior-roadmap deferred items (all unanimous CONFIRM DEFER)

RD1, SD2, RD4, SD3, SD4, SD7, SD8, SD9, SD10, RD5, PD1/PD4/PD6/PD7. No automation triggers have fired. See `project_pipeline_architecture.md` for trigger definitions.

---

## Verification evidence (R4-confirmed, independently reproducible)

Re-run command:
```bash
cd /root/tinkering/stop-git-std
for f in zustand caveman archon-subset; do
  python3 docs/render-html.py tests/fixtures/$f-form.json --out /tmp/$f.html > /dev/null
  python3 docs/render-md.py tests/fixtures/$f-form.json --out /tmp/$f.md > /dev/null
  echo "--- $f ---"
  python3 docs/validate-scanner-report.py --report /tmp/$f.html | tail -1
  python3 docs/validate-scanner-report.py --parity /tmp/$f.md /tmp/$f.html | tail -3
done
python3 -m pytest tests/ -q | tail -1
```

Expected results:
- All 3 `--report` checks: `✓ is clean.`
- All 3 `--parity` checks: `✓ Parity check clean — MD and HTML are structurally consistent.`
- `pytest`: `263 passed` (no failures; pytest may report 1 environmental deprecation warning that does not affect correctness — noted by Codex R4)
- Finding ID sets matched: zustand 6/6, caveman 9/9, archon-subset 4/4

---

## Trailing dissents (carried to Step G awareness)

1. **Pytest run may report environmental deprecation warning** (Codex R4). Not a defect. CI operators should not confuse pytest warnings with test failures; focus on the "X passed" line.
2. **Validator `--parity` exits 0 on warnings, 1 on errors only** (Pragmatist R4). When Step G wires parity into CI, inspect full output for warnings, not just exit code. Documentation item, suitable for U-1 scope.

Neither blocks Step F or Step G. Both are documentation-level reminders.

---

## Process notes

- **R3 pattern worked well:** Owner authoring concrete BEFORE/AFTER snippets before the board votes is more efficient than board-drafts-from-scratch. Pragmatist R3 called this out as worth encoding in the SOP.
- **Split resolution via owner directive:** 2-1 splits on FX-3 and FX-4 approaches were resolved by owner directive with rationale, per SOP. All 3 agents accepted the resolutions in R4.
- **Emergent bug discovery:** FX-3b surfaced during R3 verification, was correctly included in the same commit per R4 unanimous confirmation (parity-working-correctly is the contract being established — shipping FX-3 alone would have left a false-clean state).
- **Pragmatist R1 miss → R2 concession:** Pragmatist initially dismissed the CSS escape concern from first principles. R2 required either defend-with-evidence or concede; Pragmatist ran the verification, found 37 occurrences, and conceded. This is the correct correction mechanism working as designed.
- **Scope expansion note carried forward:** Pragmatist R1 noted Step F expanded mid-execution (single-fixture → 3 fixtures) without board approval. R4 acknowledges this as process drift to document in the operator guide.

---

## Agent invocation commands (for future reruns)

**Pragmatist (Sonnet 4.6):**
```
Agent tool with subagent_type="general-purpose", model="sonnet", run_in_background=true
```

**Systems Thinker (Codex GPT-5 via llmuser from /tmp):**
```bash
sudo -u llmuser bash -c "cd /tmp && codex exec --dangerously-bypass-approvals-and-sandbox '<prompt>'"
```

**Skeptic (DeepSeek V4 via Qwen CLI from repo dir):**
```bash
OPENAI_API_KEY="$DEEPSEEK_API_KEY" OPENAI_BASE_URL="https://api.deepseek.com/v1" \
  qwen -y -p "<prompt>" --model deepseek-chat
```

---

## Files in this folder

- `r1-brief.md`, `r2-brief.md`, `r3-brief.md`, `r4-brief.md` — per-round briefs
- `{pragmatist,codex,deepseek}-r{1,2,3,4}.md` — 12 per-agent responses
- `CONSOLIDATION.md` — this file

---

## References

- Commit under review: `402f933` (Step F) + `ce698d4` (R3 fixes)
- Parent plan: `../041826-renderer-alignment/CONSOLIDATION.md` (7-step plan A→G)
- Step A-B verification: `../041826-renderer-impl-verify/CONSOLIDATION.md` + `./INDEX.md`
- Step C review: `../041826-fixture-enrichment/CONSOLIDATION.md`
- Step E record: `../041826-renderer-impl-verify/STEP-E-verification.md`
- Step F record: `../041826-renderer-impl-verify/STEP-F-verification.md`
- FrontierBoard SOP: `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
