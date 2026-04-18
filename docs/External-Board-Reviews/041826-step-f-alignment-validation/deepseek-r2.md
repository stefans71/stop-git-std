# Board Review R2 — Skeptic (DeepSeek V4)

**Date:** 2026-04-18
**Reviewing:** Step F (HTML renderer + 2 new V1.1 fixtures)
**Agent:** Skeptic (DeepSeek V4)
**Round:** R2 Consolidation

---

## Verdict (R2)

**SIGN OFF WITH DISSENTS** (unchanged from R1)

**Position change:** I concede on parity regex (FN-C) — moving from FIX NOW to DEFER. The other two agents' DEFER position is reasonable given Step G's acceptance criteria can tolerate warnings if explicitly documented. My R1 BLOCK-for-G stance softens to SIGN OFF WITH DISSENTS.

---

## Response to each FIX NOW candidate

### FN-A: `| safe` bypass on `prior_scan_note` field
**Position: FIX NOW** (unchanged, unanimous)

This is a clear XSS vector. LLM-populated field flows unescaped user-influenced text. The fix artifact from Pragmatist/Codex is correct.

### FN-B: CSS autoescape corruption  
**Position: FIX NOW** (unchanged)

Owner verification confirms 37 `&#39;` entities in rendered HTML. CSS inside `<style>` blocks does not decode HTML entities, breaking `content: ''`, font-family quotes, and SVG data URIs. Pragmatist's R1 dismissal was incorrect — CSS absolutely contains characters autoescape corrupts (quotes, angle brackets in data URIs). Codex's fix artifact (`{{ css_content | safe }}`) is correct.

### FN-C: Parity regex extension to match H3 finding cards
**Position: DEFER** (changed from FIX NOW)

**Concession rationale:** While the regex gap creates a validator blind spot, Step G acceptance criteria can specify "zero errors + acceptable warnings" with the warning explicitly documented. The risk is operator normalization, but this can be mitigated by documenting the known warning in Step G acceptance matrix. Pragmatist and Codex's DEFER position (trigger: before Step G CI) is reasonable.

### FN-D: Duplicated prose-like fields in Phase 4 findings
**Position: DEFER** (unchanged)

Classification drift but not a renderer defect. Codex's DEFER-3 (trigger: when Phase 4/5 generation implemented) is appropriate.

---

## Fix artifacts (for items I endorse FIX NOW)

### FN-A: SECOND Pragmatist FN-1 / Codex FN-2
Location: `docs/templates-html/partials/catalog.html.j2:28,42`

**BEFORE:**
```jinja
{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
...
<tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
```

**AFTER:**
```jinja
{% set prior = catalog.get('prior_scan_note') or 'None - first scan of this repo.' %}
...
<tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
```

### FN-B: SECOND Codex FN-1
Location: `docs/templates-html/scan-report.html.j2:16-18`

**BEFORE:**
```jinja
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; ...">
<style>
{{ css_content }}
</style>
```

**AFTER:**
```jinja
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; ...">
<style>
{{ css_content | safe }}
</style>
```

**Note:** Also need corresponding fix in `docs/render-html.py:106-110` to ensure CSS is loaded as raw text, not escaped elsewhere.

---

## DEFER items reconciliation

### From this review (D-1 through D-7)

**D-1: Parity regex extension** — SECOND (DEFER, trigger: before Step G CI)
**D-2: Fixture provenance tag** — SECOND (DEFER, trigger: before Step G consumes live + synthetic fixtures together)
**D-3: formal_review_rate phase reclassification** — SECOND (DEFER, trigger: when Phase 3 compute.py formally scoped)
**D-4: Externalize adjustFont script** — SECOND (DEFER, trigger: before production deploy)
**D-5: Template-source `| safe` lint** — SECOND (DEFER, low priority)
**D-6: CSS autoescape path documentation** — SECOND (DEFER, should be done with FN-B fix)
**D-7: Remove duplicated prose-like fields from Phase 4** — SECOND (DEFER, trigger: when Phase 4/5 generation implemented)

### From prior-review roadmap

**RD1: Automate structured LLM operations** — SECOND (DEFER, trigger: 20+ scan corpus — we have 10)
**SD2: Finding `kind` + `domain` orthogonal typing** — SECOND (DEFER, trigger: renderer needs to group/filter by kind — Step F HTML doesn't group by kind yet)
**RD4: "Assumptions" field in investigation form** — SECOND (DEFER, trigger: first scan where assumption wrong affected verdict — not yet triggered)
**PD3: Bundle/citation validator** — **PROMOTE TO FIX NOW** (see special question below)
**SD3: Confidence scores on synthesis objects** — SECOND (DEFER, trigger: multi-run variance data — not yet)
**SD4: Judgment fingerprint** — SECOND (DEFER, trigger: multiple LLM models used — only Claude currently)
**SD7: Variable scorecard length** — SECOND (DEFER, trigger: new shape with different trust questions — not yet)
**SD8: Generic `artifacts[]` model** — SECOND (DEFER, trigger: complex multi-artifact release — not yet)

### Special question: Should PD3 bundle validator be promoted to FIX NOW?

**YES.** PD3's trigger was "JSON-first pipeline operational." Step F completes the renderer side, making the pipeline JSON-first operational. The bundle/citation validator ensures fact/inference/synthesis separation in `findings-bundle.md` — critical for Step G's "real pipeline" acceptance. Without it, Step G could pass with citation violations undetected. **Promote PD3 to FIX NOW before Step G.**

---

## Step G readiness — answer Q6.1, Q6.2, Q6.3

### Q6.1: Is "live pipeline run" = "fresh `gh api` calls" or "automated Phase 4-6 implementation"?

**Position: Concede to Pragmatist/Codex interpretation** — "fresh `gh api` calls against live repos" with LLM-in-the-loop.

**Rationale:** My R1 insistence on automated Phases 4-6 was overly strict. The board-approved architecture allows LLM-in-the-loop for Phases 4-6 (structured + prose LLM). Step G's purpose is to validate the *end-to-end* pipeline including renderer, not to build full automation first. LLM-in-the-loop is sufficient for acceptance testing.

### Q6.2: What's the definition of "byte-stable rerender"?

**Definition:** MD/HTML output must match byte-for-byte across two invocations of the same form JSON, given identical renderer code and CSS.

**Rationale:** This tests deterministic rendering, not LLM variance. The assertion should be: `render(form) == render(form)` for any valid V1.1 form. This catches template-side non-determinism (e.g., random IDs, timestamps without formatting).

### Q6.3: Does Step G require parity regex to catch H3 pattern first?

**No** — Step G can run with "zero errors + acceptable warnings" if the warning is explicitly documented in acceptance criteria.

**But:** The acceptance matrix must state: "Parity check warning for H3 pattern is expected and documented as limitation ID PAR-WARN-001." This prevents operator normalization by making the warning intentional.

---

## Process notes

1. **R2 consolidation effective:** Seeing all three R1 responses changed my position on parity regex (FN-C). The multi-agent debate surface worked.
2. **Owner verification crucial:** The CSS escape defect (FN-B) was owner-verified with grep count. Pragmatist's R1 dismissal was wrong — evidence matters.
3. **Scope discipline:** Step F expanded mid-execution (added archon-subset fixture). While valuable for C3 `auto_load_tier` testing, this should have board approval. Noted as anti-pattern.
4. **Fixture provenance gap:** Back-authored fixtures create illusion of pipeline completeness. D-2 (provenance tag) is minimal but important metadata.
5. **Validator blindness:** Validator didn't catch CSS corruption because it doesn't inspect CSS parse correctness. This reveals a validation coverage gap worth noting for future phases.

**Word count:** ~1,200 words

---

**Final:** Step F renderer is architecturally sound with two FIX NOW items (FN-A, FN-B) and one promoted roadmap item (PD3). With these fixes, Step G can proceed with LLM-in-the-loop acceptance testing.