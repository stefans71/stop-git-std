### Verdict (R3)
**SIGN OFF WITH DISSENTS**. Unchanged from R2.

### Vote on each owner-authored fix artifact
**FX-1: ADJUST.** Core fix is right, but I would not use `\u2014` inside the Jinja literal; use the actual character so template behavior is unambiguous.

**BEFORE** (`docs/templates-html/partials/catalog.html.j2:26-42`)
```jinja
{% set prompt_ver = form.get('_meta', {}).get('prompt_version', 'V2.3-post-R3') %}
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
```

**AFTER**
```jinja
{% set prompt_ver = form.get('_meta', {}).get('prompt_version', 'V2.3-post-R3') %}
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None — first scan of this repo.' %}
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
```

**FX-2: SECOND.** This is the correct trust boundary: repo-local static CSS is safe at insertion, and current output reproduces 37 `&#39;` corruptions without it.

**FX-3: ADJUST.** Owner’s Pattern 3 is fine for today’s emitted `<h3>F0 &mdash; ...</h3>` contract, but it does **not** actually handle nested-span wrapping around the ID because closing tags between `F0` and the dash break the regex. If the goal is nested-tag resilience, strip tags from `<h3>` first.

**BEFORE** (`docs/validate-scanner-report.py:445-456`)
```python
    html_findings = set(re.findall(r'exhibit-item-tag[^<]*?(?:·|&middot;)\s*(F\d+|F-[\w-]+)', html_body))
    html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))
```

**AFTER**
```python
    html_findings = set(re.findall(r'exhibit-item-tag[^<]*?(?:·|&middot;)\s*(F\d+|F-[\w-]+)', html_body))
    html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))

    for h3_html in re.findall(r"<h3[^>]*>(.*?)</h3>", html_body, flags=re.DOTALL | re.IGNORECASE):
        h3_text = re.sub(r"<[^>]+>", "", h3_html)
        m = re.match(r"\s*(F\d+|F-[\w-]+)\s*(?:&mdash;|—|–|-)", h3_text)
        if m:
            html_findings.add(m.group(1))
```

**FX-4: ADJUST.** I do not support adding `_fixture_*` fields to `_meta` in `docs/scan-schema.json`. That mixes test-corpus provenance into the live scan artifact contract. Keep provenance in test-only metadata.

**BEFORE**
No machine-readable fixture provenance file exists.

**AFTER** (`tests/fixtures/provenance.json`)
```json
{
  "caveman-form.json": {
    "provenance": "back-authored-from-golden-md",
    "source": "docs/GitHub-Scanner-caveman.md",
    "authored_by": "Claude Sonnet 4.6 subagent, commit 402f933 (Step F)"
  },
  "archon-subset-form.json": {
    "provenance": "back-authored-from-golden-md",
    "source": "docs/GitHub-Scanner-Archon.md",
    "subset_scope": "4 findings kept of 11 in golden — F0/F1/F4/F7"
  },
  "zustand-form.json": {
    "provenance": "authored-from-scan-data",
    "authored_for": "Step C fixture enrichment (commit 59224ac)"
  }
}
```

### Vote on unblocked items U-1 through U-9
**U-1: APPLY IN NEXT COMMIT (before Step G).** Step G needs an executable documented Phase 7, but this is workflow integration, not part of the renderer defect-fix batch.

**U-2: APPLY IN THIS COMMIT.** Parity zero-warning is part of the stated Step G bar, and this validator fix is self-contained.

**U-3: APPLY IN NEXT COMMIT (before Step G).** Provenance is required before mixed live+synthetic evaluation, but it should land as test-side metadata, not a production schema mutation.

**U-4: APPLY IN THIS COMMIT.** The FX-2 comment is the right place to document the trust boundary and prevent regression.

**U-5: APPLY IN NEXT COMMIT (before Step G).** This resolves the R2 split: PD3 is not triggered by Step F alone, but Step G should not be the first live bundle run without it.

**U-6: DEFER (post-Step-G).** Useful hardening, not load-bearing once FX-1 is fixed.

**U-7: DEFER (post-Step-G).** Still a Phase 3 ownership/classification issue, not a renderer/pipeline gate.

**U-8: DEFER (post-Step-G).** Inline `adjustFont` remains acceptable under current CSP and validator contract.

**U-9: DEFER (post-Step-G).** This belongs with Phase 4/5 generator cleanup at the source of duplication.

### Prior-roadmap deferred items
**RD1 — CONFIRM DEFER.**  
**SD2 — CONFIRM DEFER.**  
**RD4 — CONFIRM DEFER.**  
**SD3 — CONFIRM DEFER.**  
**SD4 — CONFIRM DEFER.**  
**SD7 — CONFIRM DEFER.**  
**SD8 — CONFIRM DEFER.**  
**SD9 — CONFIRM DEFER.**  
**SD10 — CONFIRM DEFER.**  
**RD5 — CONFIRM DEFER.**  
**PD1/PD4/PD6/PD7 — CONFIRM DEFER.**

### Post-apply verification plan
**ADJUST.** The 8-step plan is close, but I want three changes:

1. Keep steps 1-4 as written.  
2. Step 5 must assert **warnings == 0 explicitly**, not just exit 0, because `--parity` returns success on warnings.  
3. Add/update validator tests for both plain `<h3>F0 &mdash; ...</h3>` and nested-tag `<h3><span>F0</span> &mdash; ...</h3>` cases if FX-3 is taken in adjusted form.  
4. Replace step 7 with provenance verification if FX-4 follows my adjustment: validate `tests/fixtures/provenance.json` covers all three fixtures and is referenced by the review notes; do **not** mutate `docs/scan-schema.json` for fixture-only metadata.  
5. Step 6 should require the full suite to pass at the current repo count, not hardcode `263/263`.

### Process notes
The main architectural line here is simple: renderer/runtime schema should describe live scan artifacts, not test-harness history. That is why I support FX-1/FX-2, support FX-3 with a more robust extraction path, and reject schema pollution for fixture provenance. PD3 should be treated the same way: not a Step F fix, but a hard precondition before Step G claims pipeline integrity.
