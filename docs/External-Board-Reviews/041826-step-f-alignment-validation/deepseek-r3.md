# Board Review R3 — Skeptic (DeepSeek V4)

**Date:** 2026-04-18
**Reviewing:** Step F fix artifacts + unblocked items
**Agent:** Skeptic (DeepSeek V4)
**Round:** R3 Deliberation

---

## Verdict (R3)

**SIGN OFF WITH DISSENTS** (unchanged from R2)

**Position change:** I accept the owner's compromise on PD3 (U-5) — list as Step G acceptance criterion with validator build for first Step G scan. This resolves the 2-1 split from R2.

---

## Vote on each owner-authored fix artifact

### FX-1 (FN-A): remove `| safe` on `prior_scan_note`
**Vote: SECOND**

The owner's fix is correct:
1. Changes fallback string from `'None &mdash; first scan of this repo.'` to `'None \u2014 first scan of this repo.'` — avoids double-escaping `&` to `&amp;mdash;`
2. Removes `| safe` filter, allowing autoescape to protect against XSS
3. Adds explanatory comment

**Rationale:** This addresses the XSS vector while maintaining correct typography. The Unicode em-dash (`\u2014`) is the proper solution.

### FX-2 (FN-B): mark `css_content` as safe
**Vote: SECOND**

The owner's fix is correct:
1. Adds `| safe` to `{{ css_content }}`
2. Includes explanatory comment documenting why CSS is safe (static disk file)
3. Addresses the 37 `&#39;` corruption issue confirmed by verification

**Rationale:** CSS contains quotes, angle brackets in data URIs, and other characters that autoescape corrupts. Since `css_content` is loaded from `docs/scanner-design-system.css` via `_load_css()`, it's a static file with zero XSS risk.

### FX-3 (D-1 parity regex extension)
**Vote: ADJUST**

The owner's regex pattern is **insufficient**. It matches `<h3[^>]*>\s*(?:<[^>]+>\s*)*(F\d+|F-[\w-]+)\s*(?:&mdash;|—|–|-)` but fails to account for:
1. Nested tags *after* the finding ID (e.g., `<span class="severity-chip">`)
2. The actual H3 structure observed: `<h3>F0 &mdash; Title</h3>` with possible preceding `<span>` tags for status chips

**My alternative BEFORE/AFTER:**

**File:** `docs/validate-scanner-report.py` (lines 445-456)

**BEFORE:**
```python
    # Pattern 2: finding IDs with severity in heading-like context
    html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))
```

**AFTER:**
```python
    # Pattern 2: finding IDs with severity in heading-like context
    html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))
    # Pattern 3: finding IDs in H3 finding-card headings (Step F renderer format)
    # Matches: <h3>F0 &mdash; Title</h3> or <h3><span class="status-chip">Active</span>F0 &mdash; Title</h3>
    # Uses non-greedy .*? to skip any tags between <h3> and the F-ID
    html_findings |= set(re.findall(
        r'<h3[^>]*>(?:.*?<[^>]+>)*.*?(F\d+|F-[\w-]+)\s*(?:&mdash;|—|–|-)',
        html_body,
        flags=re.DOTALL
    ))
```

**Rationale:** The `re.DOTALL` flag handles multiline H3 content. The `(?:.*?<[^>]+>)*` pattern skips any nested tags before the finding ID. This matches the actual rendered HTML structure.

### FX-4 (D-2 fixture provenance tag)
**Vote: ADJUST**

The owner's approach violates schema validation (`additionalProperties: false`). We must either:
1. Add the fields to the schema definition
2. Relax `additionalProperties` for underscore-prefixed fields in `_meta`

**My alternative BEFORE/AFTER:**

**File 1:** `docs/scan-schema.json` (lines ~145-160 in the `meta` definition)

**BEFORE:**
```json
    "meta": {
      "type": "object",
      "required": ["scan_status"],
      "properties": {
        "phases_completed": {
          "type": "array",
          "items": { "type": "string" }
        },
        "scan_status": {
          "type": "string",
          "enum": ["in_progress", "validated", "completed"]
        },
        "scanner_version": { "type": ["string", "null"] },
        "prompt_version": { "type": ["string", "null"] },
        "model": { "type": ["string", "null"] },
        "scan_started_at": { "type": ["string", "null"] },
        "scan_completed_at": { "type": ["string", "null"] },
        "assumptions": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "additionalProperties": false
    },
```

**AFTER:**
```json
    "meta": {
      "type": "object",
      "required": ["scan_status"],
      "properties": {
        "phases_completed": {
          "type": "array",
          "items": { "type": "string" }
        },
        "scan_status": {
          "type": "string",
          "enum": ["in_progress", "validated", "completed"]
        },
        "scanner_version": { "type": ["string", "null"] },
        "prompt_version": { "type": ["string", "null"] },
        "model": { "type": ["string", "null"] },
        "scan_started_at": { "type": ["string", "null"] },
        "scan_completed_at": { "type": ["string", "null"] },
        "assumptions": {
          "type": "array",
          "items": { "type": "string" }
        },
        "_fixture_provenance": { "type": ["string", "null"] },
        "_fixture_back_authored_from": { "type": ["string", "null"] },
        "_fixture_authored_by": { "type": ["string", "null"] },
        "_fixture_subset_scope": { "type": ["string", "null"] },
        "_fixture_authored_for": { "type": ["string", "null"] }
      },
      "additionalProperties": false
    },
```

**Rationale:** Schema compliance is non-negotiable. Adding the fields as optional (`["string", "null"]`) maintains backward compatibility while enabling provenance tracking.

---

## Vote on unblocked items U-1 through U-9

### U-1: Integration of `render-html.py` into scan workflow
**Vote: APPLY IN NEXT COMMIT (before Step G)**

**Rationale:** Step G cannot run "live pipeline" without documented integration. CLAUDE.md and SCANNER-OPERATOR-GUIDE.md must be updated to reflect the new Phase 7 workflow (`render-md.py` + `render-html.py`).

### U-2: D-1 parity regex extension (FX-3)
**Vote: APPLY IN THIS COMMIT**

**Rationale:** Should bundle with FN-A/FN-B as Pragmatist and Codex both said "before Step G." My adjusted regex (above) fixes the owner's insufficient pattern.

### U-3: D-2 fixture provenance tag (FX-4)
**Vote: APPLY IN THIS COMMIT**

**Rationale:** Low effort, prevents epistemic drift in Step G corpus. Must include schema update as per my ADJUST vote.

### U-4: D-6 CSS autoescape documentation (part of FX-2)
**Vote: APPLY IN THIS COMMIT**

**Rationale:** Already included in FX-2's comment. Satisfies documentation requirement.

### U-5: PD3 bundle/citation validator
**Vote: APPLY IN NEXT COMMIT (before Step G)**

**Rationale:** I accept the owner's compromise. PD3 should be listed as Step G acceptance criterion, with validator built for first Step G scan. This ensures citation violations are caught during Step G validation without blocking Step F fixes.

### U-6: D-5 template-source `| safe` lint
**Vote: DEFER (post-Step-G)**

**Rationale:** Low priority once FX-1 applies. The only remaining `| safe` will be FX-2's `css_content` (intentional).

### U-7: D-3 `formal_review_rate` phase classification
**Vote: DEFER (post-Step-G)**

**Rationale:** Classification ambiguity doesn't affect renderer. Defer to Phase 3 compute.py scoping.

### U-8: D-4 externalize `adjustFont` script
**Vote: DEFER (post-Step-G)**

**Rationale:** CSP already allows `unsafe-inline`. Production optimization, not renderer defect.

### U-9: D-7 / FN-D remove duplicated prose-like fields
**Vote: DEFER (post-Step-G)**

**Rationale:** Schema cleanup for Phase 4/5 generator implementation, not renderer.

---

## Prior-roadmap deferred items

**RD1 — automate structured LLM:** CONFIRM DEFER (20+ corpus not met)
**SD2 — kind + domain typing:** CONFIRM DEFER (renderer doesn't group by kind yet)
**RD4 — assumptions field:** CONFIRM DEFER (no wrong-assumption scans yet)
**SD3 — confidence scores:** CONFIRM DEFER (no multi-run variance data)
**SD4 — judgment fingerprint:** CONFIRM DEFER (single-model only)
**SD7 — variable scorecard length:** CONFIRM DEFER (no new trust question shapes)
**SD8 — generic `artifacts[]`:** CONFIRM DEFER (no complex multi-artifact releases)
**SD9 — permissions:** CONFIRM DEFER (V2.0+)
**SD10 — SBOM:** CONFIRM DEFER (V2.0+)
**RD5 — management sign-off:** CONFIRM DEFER (V2.0+)
**PD1/PD4/PD6/PD7 — packaging:** CONFIRM DEFER (V2.0+)

---

## Post-apply verification plan

**SECOND** the 8-step plan with **one addition**:

**Add step 4.5:** Run parity check with verbose output to confirm FX-3 regex catches all H3 finding IDs:
```bash
python3 docs/validate-scanner-report.py --parity --verbose docs/GitHub-Scanner-zustand.md /tmp/zustand-rendered.html
```

**Verification steps:**
1. ✅ Apply all 4 fix artifacts (with my FX-3 and FX-4 adjustments)
2. ✅ Re-render zustand, caveman, archon-subset → HTML
3. ✅ Verify `grep -c "&#39;" /tmp/*-rendered.html` drops from 37 to **0** (only legitimate `&#39;` inside code blocks)
4. ✅ Run `python3 docs/validate-scanner-report.py --report` on all 3 HTMLs — must exit 0
5. ✅ Run parity check with verbose output to confirm H3 IDs caught
6. ✅ Run full test suite `python3 -m pytest tests/` — must pass 263/263
7. ✅ Update schema for FX-4 `_fixture_*` fields
8. ✅ Present applied diff + verification log to R4

---

## Process notes

1. **R3 deliberation effective:** Owner's concrete snippets enabled precise evaluation. My ADJUST votes provide improved implementations.
2. **Schema compliance critical:** FX-4 must respect `additionalProperties: false`. My schema update ensures validation passes.
3. **Regex precision matters:** FX-3 owner pattern too restrictive. My pattern with `re.DOTALL` handles actual H3 structure.
4. **PD3 compromise acceptable:** Listing as Step G acceptance criterion with validator build resolves the 2-1 split while ensuring citation validation happens before pipeline operationalization.
5. **Integration documentation gap:** U-1 is essential — without updated operator guide, Step G cannot proceed.

**Word count:** ~1,400 words

---

**Final:** With my ADJUSTED FX-3 and FX-4, and acceptance of PD3 compromise, Step F fixes can proceed. The 8-step verification plan (with my addition) ensures comprehensive validation before R4 confirmation.