# Step E — Validator `--report` Gate on Rendered Output

**Date:** 2026-04-18
**Step:** E of the 7-step renderer plan (A→G) from `../041826-renderer-alignment/CONSOLIDATION.md`
**Type:** Mechanical verification (no board review required per plan)
**Operator:** Claude Opus 4.7 (`claude-opus-4-7[1m]`) in session 5
**Outcome:** PASS — validator exit 0, zero flagged issues, no fix applied

---

## Hypothesis

After Steps A (schema freeze V1.1), B (render-md.py → Jinja2), C (fixture enrichment), and D (structural-assertion tests), the deterministic MD renderer should produce output that passes `validate-scanner-report.py --report` (strict rendered-report mode) without any further template changes.

A passing result closes Step E and ships the MD renderer. A failure would surface specific template issues to fix before proceeding.

**Gate:** `validate-scanner-report.py --report <rendered.md>` must exit 0 on output produced by `render-md.py` from the canonical fixture.

---

## Files used

| Role | Path | SHA-256 |
|------|------|---------|
| Renderer (shim) | `docs/render-md.py` | `c9e94abdf19fcc23f4d40af290f85b249ef947f03b7d586cffea1d3b07aebf97` |
| Renderer templates | `docs/templates/scan-report.md.j2` + `docs/templates/partials/*.md.j2` | (14 partials, 508 lines total) |
| Schema | `docs/scan-schema.json` (V1.1) | `2ee1324393e3d4810ae4e0efa9a4f03c238ffc9e0733777ec83545ad20b39ad0` |
| Canonical fixture | `tests/fixtures/zustand-form.json` (1015 lines) | `7f3f96fb3cfd9f3cfdd6a7d2aaa7080b2b88957f016234e7ae65a632c327e880` |
| Validator | `docs/validate-scanner-report.py` (`--report` mode) | tracked in-repo |
| Rendered artifact (derived, not committed) | `/tmp/rendered.md` (541 lines) | `071b3fbf274fa25f4be266fce3ecbe005e40e08b63d3aef67f589c3b75a0f38f` |

Head commit at verification: `2f71c5a` (pre-Step-E). All 146 tests passing.

---

## Commands executed

```bash
# 1. Render MD from the canonical fixture
python3 docs/render-md.py tests/fixtures/zustand-form.json --out /tmp/rendered.md

# 2. Run validator in strict rendered-report mode
python3 docs/validate-scanner-report.py --report /tmp/rendered.md
```

---

## Expected results

1. Renderer exits 0 and writes a non-empty `rendered.md` covering all 13 section headers.
2. Validator exits 0 with all strict-mode checks passing:
   - Tag balance (0 unclosed)
   - No mismatched close tags
   - EXAMPLE markers balanced (0/0)
   - Zero inline `style=''` attributes
   - No `px` font-sizes in `<style>` (rem only)
   - Zero `{{PLACEHOLDER}}` tokens (rendered-report strict check)
   - Zero EXAMPLE-START/END markers (rendered-report strict check)
   - No XSS vectors (script tags, event handlers, `javascript:`, dangerous embeds)
   - No suspicious unescaped `<` outside code/pre/script/style/comments

---

## Actual results

**Renderer:** exit 0, produced 540-line MD (541 w/ trailing newline).

**Validator output (verbatim):**
```
=== Validating rendered.md (541 lines, mode: rendered-report (strict)) ===
  ✓ All tags balanced (0 unclosed)
  ✓ No mismatched close tags
  ✓ EXAMPLE markers balanced (0 start / 0 end)
  ✓ Zero inline style='' attributes on rendered elements
  ✓ No px font-sizes in <style> block (rem only)
  ✓ Zero {{PLACEHOLDER}} tokens remaining (rendered-report check)
  ✓ Zero EXAMPLE-START/END markers remaining (rendered-report check)
  ✓ No XSS vectors detected (script tags, event handlers, javascript: URLs, dangerous embeds)
  ✓ No suspicious unescaped '<' outside code/pre/script/style/comments

✓ rendered.md is clean.
```

Exit code: 0.

No template edits, schema edits, or fixture edits were required. Hypothesis confirmed on first run.

---

## Conclusion

**Step E: PASS.** The MD renderer (Jinja2 architecture from Step B, driven by V1.1 schema from Step A, with the enriched fixture from Step C, verified by structural assertions from Step D) produces validator-clean output. Phase 7 Steps A-E are complete.

**What this closes:**
- Renderer MD pipeline is production-ready against the V1.1 schema + canonical fixture.
- The "renderer ships on Step E" commitment from the renderer-alignment consolidation (C5+C6 resolution) is satisfied.

**What this does NOT close:**
- **Step F** (render-html.py) — deferred to a later session per the 7-step plan. MD/HTML parity gate (PD2 validator mode) already exists but needs the HTML renderer to exercise.
- **Step G** (C7 acceptance matrix — Archon re-run + one other shape + zustand via end-to-end JSON-first pipeline) — gates any "pipeline reliable" claim. Board review REQUIRED before that claim is made.
- This verification runs against a **single fixture** (zustand). It does not prove the renderer works across all 9 shapes; Step G exists for that cross-shape validation.

**What to do next:** Ask the owner whether to sequence Step F (HTML renderer) or Step G (acceptance matrix — board review) next. Neither blocks the other.

---

## References

- `../041826-renderer-alignment/CONSOLIDATION.md` — 7-step plan (A-G) with C1-C7 resolutions
- `./INDEX.md` — cross-reference across the 3 renderer board reviews + commit log
- `./CONSOLIDATION.md` — Step A+B implementation verification record (included C2 owner directive)
- `../041826-fixture-enrichment/CONSOLIDATION.md` — Step C fixture enrichment review (10 FAs, 3-0 APPROVE)
- Session 5 status memory: `project_session5_status.md`
