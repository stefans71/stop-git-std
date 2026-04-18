### Verdict
**BLOCK**

### Q1
Step F is mostly faithful to the pre-computed form contract: `docs/render-html.py:73-110` only reads JSON, loads templates, and reads the CSS file; there are no network calls or lazy upstream recomputations. The templates consume already-assembled phase blocks such as `phase_1_raw_capture`, `phase_4_structured_llm`, `phase_4b_computed`, and `phase_5_prose_llm` directly (`docs/templates-html/scan-report.html.j2:6-10`, `partials/section_02.html.j2:17-25`, `partials/verdict.html.j2:17-26`). I did not see HTML inventing whole findings absent from MD; the main finding loops come from `phase_4_structured_llm.findings.entries` and prose joins by `finding_id`. The architectural breach is narrower but real: the renderer mutates CSS bytes through HTML escaping and explicitly trusts one structured field as raw HTML, so the HTML emitter is not yet a pure deterministic rendering of intended content.

### Q2
The new fixtures generally honor the 8/8/4 split. In `archon-subset-form.json`, raw facts such as repo metadata and branch protection live under `phase_1_raw_capture` (`33-165`), which matches schema ownership in `scan-schema.json:571+` and the board methodology’s Phase 1 fact boundary (`board-review-pipeline-methodology.md:68-79`). Computed verdict placement is correct: `phase_4b_computed.verdict` at `archon-subset-form.json:1149-1153` matches `scan-schema.json:1320-1338`. Structured-LLM fields also sit where they should: `split_axis_decision` (`648-666`), `verdict_exhibits` (`998-1069`), `catalog_metadata` (`1139-1146`), and finding-level `meta_table` / `how_to_fix` / `duration_label` (`521-620`) all map to `scan-schema.json:1123-1315` and `455-543`. Prose is mostly contained to `phase_5_prose_llm.editorial_caption` and `per_finding_prose` (`1156-1183`, schema `1341-1367`), but the fixtures still duplicate `what_this_means` and `what_this_does_not_mean` inside `phase_4_structured_llm.findings.entries` (`548-549`, `574-575`), which is a lineage smell even if the renderer currently prefers Phase 5 prose.

### Q3
Back-authoring fixtures from goldens is acceptable for Step F because Step F is validating the renderer contract and cross-shape template coverage, not upstream acquisition fidelity. The failure mode is epistemic: a back-authored fixture can be schema-clean and render-clean while still encoding values that no real Phase 1-6 pipeline would ever produce, especially around evidence linkage, enum drift, provenance placement, and real tool-output edge cases. That risk is visible already in the stale exhibit tags caught during verification; the renderer path passed only because parity exposed the mismatch, not because the fixture origin was trustworthy by construction. I recommend adding an explicit fixture provenance marker in `_meta` stating “back-authored from golden MD, not pipeline-produced,” but that is a Step G hygiene item, not a Step F blocker.

### Q4
The parity warning is not acceptable to leave permanent if Step G is supposed to certify pipeline reliability. The root cause is in `validate-scanner-report.py:446-456`: HTML finding extraction only recognizes exhibit tags and `F<N> — Severity`, while the actual renderer emits `F<N> — Title` in `partials/section_02.html.j2:76`. For Step F’s narrow goal this was tolerable noise because the reference scans share the same pattern, but once Step G runs live scans the warning will train operators to ignore parity output. Extend the regex to match finding-card headings before Step G sign-off so parity can become a meaningful gate rather than a ritual warning.

### Q5
The HTML autoescape policy is not yet safe enough. `render-html.py:77-84` enables autoescape for `.html.j2`, and `scan-report.html.j2:16-18` inserts `{{ css_content }}` into `<style>`; rendering shows quotes and the SVG data URI escaped as entities (`&#39;`, `&#34;`), which means the stylesheet bytes are not preserved and some CSS is likely malformed. There is also one explicit trust bypass: `partials/catalog.html.j2:28,42` marks `prior_scan_note` as `| safe`, even though the schema defines it as a plain string (`scan-schema.json:1309-1312`) and the MD renderer treats it as text (`docs/templates/partials/catalog.md.j2:11,29`). The validator’s `adjustFont` allowlist is absolutely load-bearing: `validate-scanner-report.py:146-164` whitelists that inline script and `onclick`, so current CSP/XSS cleanliness depends on that exact pattern remaining small and stable.

### Q6
Step G should not wait for full automation of Phases 4-6; it should run with LLM-in-the-loop for Phases 1-6 and deterministic pipeline handling for 7-8, because the claim under test is contract survivability through the real path, not autonomy. Minimum acceptance for “pipeline reliable” should be: three live repos produce V1.1-valid JSON, both emitters pass `--report`, parity has zero errors and zero warnings, evidence refs resolve, provenance/phase placement is audited on a spot sample, and rerendering the same JSON is byte-stable. The best three shapes remain `zustand`, `Archon`, and `caveman`: they cover a library, a monorepo/agentic platform with C3 `auto_load_tier`, and a curl-pipe installer with split-by-version. If a fourth is added, use a compiled CLI shape such as `fd`, but I would not block Step G on that.

### Q7
After Step F, the renderer half of `LLM → JSON → renderer → MD+HTML` is almost complete structurally, but not operationally complete because the HTML emitter still has a style-escaping defect and a raw-HTML trust bypass. The full pipeline is still missing production Phase 1-6 orchestration, provenance validation at scale, and Step G live acceptance evidence; `board-review-pipeline-methodology.md:66-109` is clear that reliability claims depend on the whole 9-phase path, not just renderer determinism. SD2 is not newly ready just because of Step F; the current category-based C3 binding remains proportionate until real-pipeline output shows taxonomy drift. I cannot find roadmap definitions for `RD1` or `PD3` in the reviewed files, so I would not claim they are activated by this commit.

### Q8
Yes. There are two FIX NOW items before Step G: the CSS embed must stop escaping stylesheet bytes, and the `prior_scan_note` raw-HTML bypass should be removed or replaced with explicit formatting-safe text. Both are acceptance-matrix risks because they hide behind green validator/tests today: the first can degrade real report rendering without failing checks, and the second weakens the facts/inference/synthesis trust boundary just as live LLM output enters Step G. The parity-regex gap is real, but I classify it as DEFER-to-Step-G gate hardening rather than a Step F renderer blocker.

### FIX NOW items
**FN-1 — Escaped CSS corrupts HTML renderer output**  
Location: `docs/templates-html/scan-report.html.j2:16-18`, `docs/render-html.py:106-110`  
Rationale: the stylesheet is supposed to be embedded verbatim, but autoescape transforms raw CSS bytes inside `<style>`. This is a renderer defect, not a cosmetic preference.

**BEFORE**
```jinja2
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{{ css_content }}
</style>
```

**AFTER**
```jinja2
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{{ css_content | safe }}
</style>
```

**FN-2 — Structured catalog field is incorrectly trusted as HTML**  
Location: `docs/templates-html/partials/catalog.html.j2:28,42`  
Rationale: `prior_scan_note` is a string field in schema and text in MD; trusting it as HTML violates the structured/text boundary and creates needless XSS/markup-surface dependence on the validator.

**BEFORE**
```jinja2
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
```

**AFTER**
```jinja2
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None - first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
```

### DEFER items
**DEFER-1 — Extend parity regex to finding-card headings before Step G sign-off**  
Location: `docs/validate-scanner-report.py:446-456`  
Trigger: before Step G acceptance-matrix review.  
Rationale: live pipeline verification should not normalize a standing warning.

**DEFER-2 — Mark fixtures as back-authored in `_meta`**  
Location: `tests/fixtures/caveman-form.json`, `tests/fixtures/archon-subset-form.json`  
Trigger: when Step G starts consuming both live and synthetic forms in the same test corpus.  
Rationale: prevents synthetic fixtures from being mistaken for pipeline-origin evidence.

**DEFER-3 — Remove duplicated prose-like fields from Phase 4 findings**  
Location: fixture finding entries and possibly schema `scan-schema.json:499-500`  
Trigger: when upstream Phase 4/5 generation is implemented.  
Rationale: keeping “what this means / does NOT mean” in both Phase 4 and Phase 5 invites lineage confusion.

### INFO items
The renderer contract is otherwise thin and scalable: `render-html.py` is a small shim and the partial structure mirrors the MD emitter cleanly. The new fixtures materially improve shape coverage, especially `archon-subset` exercising the V1.1 C3 `auto_load_tier` rule (`archon-subset-form.json:552-559`, schema `528-540`). The current HTML tests are useful structural smoke tests but they do not assert unescaped CSS integrity, which is why the main renderer defect slipped through (`tests/test_render_html.py:72-77`).

### Anti-patterns or process drift you noticed
Parallel subagent authorship was acceptable for fixture and partial conversion work, but the review record overstates validator cleanliness because the validator is currently blind to a real CSS corruption path. The bigger process drift is allowing synthetic fixtures back-authored from goldens to sit beside pipeline-shaped artifacts without an explicit provenance marker; that is manageable in Step F, but Step G should not blur those classes. The board’s “MD canonical” rule is being respected at the content level, yet the HTML path still has hidden trust-boundary exceptions (`css_content`, `prior_scan_note`) that need to be made explicit and deterministic before the acceptance matrix.
tokens used
81,595
### Verdict
**BLOCK**

### Q1
Step F is mostly faithful to the pre-computed form contract: `docs/render-html.py:73-110` only reads JSON, loads templates, and reads the CSS file; there are no network calls or lazy upstream recomputations. The templates consume already-assembled phase blocks such as `phase_1_raw_capture`, `phase_4_structured_llm`, `phase_4b_computed`, and `phase_5_prose_llm` directly (`docs/templates-html/scan-report.html.j2:6-10`, `partials/section_02.html.j2:17-25`, `partials/verdict.html.j2:17-26`). I did not see HTML inventing whole findings absent from MD; the main finding loops come from `phase_4_structured_llm.findings.entries` and prose joins by `finding_id`. The architectural breach is narrower but real: the renderer mutates CSS bytes through HTML escaping and explicitly trusts one structured field as raw HTML, so the HTML emitter is not yet a pure deterministic rendering of intended content.

### Q2
The new fixtures generally honor the 8/8/4 split. In `archon-subset-form.json`, raw facts such as repo metadata and branch protection live under `phase_1_raw_capture` (`33-165`), which matches schema ownership in `scan-schema.json:571+` and the board methodology’s Phase 1 fact boundary (`board-review-pipeline-methodology.md:68-79`). Computed verdict placement is correct: `phase_4b_computed.verdict` at `archon-subset-form.json:1149-1153` matches `scan-schema.json:1320-1338`. Structured-LLM fields also sit where they should: `split_axis_decision` (`648-666`), `verdict_exhibits` (`998-1069`), `catalog_metadata` (`1139-1146`), and finding-level `meta_table` / `how_to_fix` / `duration_label` (`521-620`) all map to `scan-schema.json:1123-1315` and `455-543`. Prose is mostly contained to `phase_5_prose_llm.editorial_caption` and `per_finding_prose` (`1156-1183`, schema `1341-1367`), but the fixtures still duplicate `what_this_means` and `what_this_does_not_mean` inside `phase_4_structured_llm.findings.entries` (`548-549`, `574-575`), which is a lineage smell even if the renderer currently prefers Phase 5 prose.

### Q3
Back-authoring fixtures from goldens is acceptable for Step F because Step F is validating the renderer contract and cross-shape template coverage, not upstream acquisition fidelity. The failure mode is epistemic: a back-authored fixture can be schema-clean and render-clean while still encoding values that no real Phase 1-6 pipeline would ever produce, especially around evidence linkage, enum drift, provenance placement, and real tool-output edge cases. That risk is visible already in the stale exhibit tags caught during verification; the renderer path passed only because parity exposed the mismatch, not because the fixture origin was trustworthy by construction. I recommend adding an explicit fixture provenance marker in `_meta` stating “back-authored from golden MD, not pipeline-produced,” but that is a Step G hygiene item, not a Step F blocker.

### Q4
The parity warning is not acceptable to leave permanent if Step G is supposed to certify pipeline reliability. The root cause is in `validate-scanner-report.py:446-456`: HTML finding extraction only recognizes exhibit tags and `F<N> — Severity`, while the actual renderer emits `F<N> — Title` in `partials/section_02.html.j2:76`. For Step F’s narrow goal this was tolerable noise because the reference scans share the same pattern, but once Step G runs live scans the warning will train operators to ignore parity output. Extend the regex to match finding-card headings before Step G sign-off so parity can become a meaningful gate rather than a ritual warning.

### Q5
The HTML autoescape policy is not yet safe enough. `render-html.py:77-84` enables autoescape for `.html.j2`, and `scan-report.html.j2:16-18` inserts `{{ css_content }}` into `<style>`; rendering shows quotes and the SVG data URI escaped as entities (`&#39;`, `&#34;`), which means the stylesheet bytes are not preserved and some CSS is likely malformed. There is also one explicit trust bypass: `partials/catalog.html.j2:28,42` marks `prior_scan_note` as `| safe`, even though the schema defines it as a plain string (`scan-schema.json:1309-1312`) and the MD renderer treats it as text (`docs/templates/partials/catalog.md.j2:11,29`). The validator’s `adjustFont` allowlist is absolutely load-bearing: `validate-scanner-report.py:146-164` whitelists that inline script and `onclick`, so current CSP/XSS cleanliness depends on that exact pattern remaining small and stable.

### Q6
Step G should not wait for full automation of Phases 4-6; it should run with LLM-in-the-loop for Phases 1-6 and deterministic pipeline handling for 7-8, because the claim under test is contract survivability through the real path, not autonomy. Minimum acceptance for “pipeline reliable” should be: three live repos produce V1.1-valid JSON, both emitters pass `--report`, parity has zero errors and zero warnings, evidence refs resolve, provenance/phase placement is audited on a spot sample, and rerendering the same JSON is byte-stable. The best three shapes remain `zustand`, `Archon`, and `caveman`: they cover a library, a monorepo/agentic platform with C3 `auto_load_tier`, and a curl-pipe installer with split-by-version. If a fourth is added, use a compiled CLI shape such as `fd`, but I would not block Step G on that.

### Q7
After Step F, the renderer half of `LLM → JSON → renderer → MD+HTML` is almost complete structurally, but not operationally complete because the HTML emitter still has a style-escaping defect and a raw-HTML trust bypass. The full pipeline is still missing production Phase 1-6 orchestration, provenance validation at scale, and Step G live acceptance evidence; `board-review-pipeline-methodology.md:66-109` is clear that reliability claims depend on the whole 9-phase path, not just renderer determinism. SD2 is not newly ready just because of Step F; the current category-based C3 binding remains proportionate until real-pipeline output shows taxonomy drift. I cannot find roadmap definitions for `RD1` or `PD3` in the reviewed files, so I would not claim they are activated by this commit.

### Q8
Yes. There are two FIX NOW items before Step G: the CSS embed must stop escaping stylesheet bytes, and the `prior_scan_note` raw-HTML bypass should be removed or replaced with explicit formatting-safe text. Both are acceptance-matrix risks because they hide behind green validator/tests today: the first can degrade real report rendering without failing checks, and the second weakens the facts/inference/synthesis trust boundary just as live LLM output enters Step G. The parity-regex gap is real, but I classify it as DEFER-to-Step-G gate hardening rather than a Step F renderer blocker.

### FIX NOW items
**FN-1 — Escaped CSS corrupts HTML renderer output**  
Location: `docs/templates-html/scan-report.html.j2:16-18`, `docs/render-html.py:106-110`  
Rationale: the stylesheet is supposed to be embedded verbatim, but autoescape transforms raw CSS bytes inside `<style>`. This is a renderer defect, not a cosmetic preference.

**BEFORE**
```jinja2
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{{ css_content }}
</style>
```

**AFTER**
```jinja2
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{{ css_content | safe }}
</style>
```

**FN-2 — Structured catalog field is incorrectly trusted as HTML**  
Location: `docs/templates-html/partials/catalog.html.j2:28,42`  
Rationale: `prior_scan_note` is a string field in schema and text in MD; trusting it as HTML violates the structured/text boundary and creates needless XSS/markup-surface dependence on the validator.

**BEFORE**
```jinja2
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
```

**AFTER**
```jinja2
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None - first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
```

### DEFER items
**DEFER-1 — Extend parity regex to finding-card headings before Step G sign-off**  
Location: `docs/validate-scanner-report.py:446-456`  
Trigger: before Step G acceptance-matrix review.  
Rationale: live pipeline verification should not normalize a standing warning.

**DEFER-2 — Mark fixtures as back-authored in `_meta`**  
Location: `tests/fixtures/caveman-form.json`, `tests/fixtures/archon-subset-form.json`  
Trigger: when Step G starts consuming both live and synthetic forms in the same test corpus.  
Rationale: prevents synthetic fixtures from being mistaken for pipeline-origin evidence.

**DEFER-3 — Remove duplicated prose-like fields from Phase 4 findings**  
Location: fixture finding entries and possibly schema `scan-schema.json:499-500`  
Trigger: when upstream Phase 4/5 generation is implemented.  
Rationale: keeping “what this means / does NOT mean” in both Phase 4 and Phase 5 invites lineage confusion.

### INFO items
The renderer contract is otherwise thin and scalable: `render-html.py` is a small shim and the partial structure mirrors the MD emitter cleanly. The new fixtures materially improve shape coverage, especially `archon-subset` exercising the V1.1 C3 `auto_load_tier` rule (`archon-subset-form.json:552-559`, schema `528-540`). The current HTML tests are useful structural smoke tests but they do not assert unescaped CSS integrity, which is why the main renderer defect slipped through (`tests/test_render_html.py:72-77`).

### Anti-patterns or process drift you noticed
Parallel subagent authorship was acceptable for fixture and partial conversion work, but the review record overstates validator cleanliness because the validator is currently blind to a real CSS corruption path. The bigger process drift is allowing synthetic fixtures back-authored from goldens to sit beside pipeline-shaped artifacts without an explicit provenance marker; that is manageable in Step F, but Step G should not blur those classes. The board’s “MD canonical” rule is being respected at the content level, yet the HTML path still has hidden trust-boundary exceptions (`css_content`, `prior_scan_note`) that need to be made explicit and deterministic before the acceptance matrix.
