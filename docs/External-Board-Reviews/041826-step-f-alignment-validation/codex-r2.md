### Verdict (R2)
**SIGN OFF WITH DISSENTS**

Position changed from **BLOCK** in R1. My R1 blockers were FN-A and FN-B. The proposed artifacts for both are technically correct and sufficient to clear that block if applied. I am not carrying FN-C forward as a Step F blocker, but I do tighten its trigger: it becomes a **Step G pre-gate fix** because the acceptance matrix now expects parity zero warnings.

### Response to each FIX NOW candidate (4 items)
**FN-A: `prior_scan_note` `| safe` bypass**  
**FIX NOW.** No change from R1. The field is structured text, not trusted HTML. The proposed fix is correct: remove `| safe` and replace the fallback string with plain text, not `&mdash;`.

**FN-B: CSS autoescape corruption**  
**FIX NOW.** No change from R1. Owner repro is sufficient; I also re-rendered and still observed escaped entities in the current output. The proposed fix is correct: mark the CSS payload safe at the insertion site because the payload is repo-local static CSS, not user content.

**FN-C: parity regex extension**  
**DEFER.** No change in core disposition, but I am adjusting the trigger. This is not a Step F renderer blocker because it does not corrupt emitted content. It is, however, a **required pre-gate for Step G acceptance** if Step G keeps the stated “zero warnings” criterion. DeepSeek is right about the operational risk; I disagree only on phase placement.

**FN-D: duplicated prose-like fields in Phase 4 findings**  
**DEFER.** No change from R1. This is lineage drift, not a renderer defect. Fix when Phase 4/5 generation is implemented so ownership boundaries can be corrected at the source.

### Fix artifacts (one per FIX NOW item you endorse)
**FN-A**  
**SECOND Pragmatist FN-1 / Codex FN-2**

**BEFORE** (`docs/templates-html/partials/catalog.html.j2:26-42`)
```jinja
{% set prompt_ver = form.get('_meta', {}).get('prompt_version', 'V2.3-post-R3') %}
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
```

**AFTER**
```jinja
{% set prompt_ver = form.get('_meta', {}).get('prompt_version', 'V2.3-post-R3') %}
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None - first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
```

**FN-B**  
**SECOND Codex FN-1**

**BEFORE** (`docs/templates-html/scan-report.html.j2:13-18`)
```jinja
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Unbounded:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{{ css_content }}
</style>
```

**AFTER**
```jinja
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Unbounded:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{{ css_content | safe }}
</style>
```

### DEFER items reconciliation
**D-1 parity regex extension**  
**SECOND, ADJUST TRIGGER.** Trigger is no longer vague “before Step G sign-off”; it is **before any Step G acceptance run that requires parity zero warnings**.

**D-2 fixture provenance tag**  
**SECOND.** Needed before Step G mixes live-pipeline and back-authored forms in the same evidence set.

**D-3 `formal_review_rate` phase reclassification**  
**SECOND.** Keep for Phase 3 scoping.

**D-4 externalize `adjustFont` script**  
**SECOND.** Production-hardening item, not Step G.

**D-5 template-source `| safe` lint**  
**SECOND.** Useful validator hardening after FN-A, but not a gate.

**D-6 CSS autoescape path documentation**  
**SECOND.** Add a code comment near the safe insertion so this defect does not regress.

**D-7 remove duplicated prose-like Phase 4 fields**  
**SECOND.** Do it with Phase 4/5 generator implementation, not in renderer review.

**RD1 automate structured LLM operations**  
**SECOND.** Not triggered; corpus threshold still not met.

**SD2 `kind` + `domain` orthogonal typing**  
**REJECT promotion now.** Not worth doing before Step G re-binds C3. Step G can run with the current schema if C3 behavior is explicitly audited in the chosen repos. Promote in V1.2 when a renderer or validator actually needs structured grouping/filtering.

**RD4 assumptions field**  
**SECOND.** Trigger has not fired.

**PD3 bundle/citation validator**  
**ADJUST TRIGGER, not FIX NOW.** Step F does **not** make the JSON-first pipeline operational; it proves the renderer against synthetic forms. PD3 should trigger **before the first Step G claim that a live JSON-first pipeline is operational**, not merely because Step F completed.

**SD3 confidence scores**  
**SECOND.** Not triggered.

**SD4 judgment fingerprint**  
**SECOND.** Not triggered with single-model usage.

**SD7 variable scorecard length**  
**SECOND.** Not triggered.

**SD8 generic `artifacts[]` model**  
**SECOND.** Not triggered.

**SD9 permissions**  
**SECOND.** V2.0+, not triggered.

**SD10 SBOM**  
**SECOND.** V2.0+, not triggered.

**RD5 management sign-off**  
**SECOND.** V2.0+, not triggered.

**PD1 packaging**  
**SECOND.** V2.0+, not triggered.

**PD4 packaging**  
**SECOND.** V2.0+, not triggered.

**PD6 packaging**  
**SECOND.** V2.0+, not triggered.

**PD7 packaging**  
**SECOND.** V2.0+, not triggered.

Special question answers:
- **PD3 promoted to FIX NOW? No.** Step F is still synthetic-fixture verification.
- **SD2 promoted to FIX NOW? No.** Premature before Step G; not a prerequisite to re-bind C3.

### Step G readiness — answer Q6.1, Q6.2, Q6.3
**Q6.1**  
“Live pipeline run” means **fresh Phase 1 capture against live repos plus manual/LLM-assisted Phases 4-6**, not full automation of Phases 4-6. DeepSeek’s automation requirement is a later roadmap item, not the correct Step G gate.

**Q6.2**  
“Byte-stable rerender” means: given the **same form JSON bytes**, MD and HTML rerenders must be byte-identical across invocations. It does not mean two fresh live scans must match each other.

**Q6.3**  
Step G should **not** accept “zero errors + acceptable warnings.” If the acceptance matrix says zero warnings, then FN-C must be fixed first. So my position is: **parity regex is not a Step F blocker, but it is a Step G pre-gate fix.**

### Process notes
R2 consolidation usefully separated “renderer emits bad bytes” from “validator has an observational blind spot.” That distinction is why my verdict changes: FN-A/FN-B were real ship blockers and are cleanly fixable; FN-C remains important but belongs at the Step G gate, not as a reason to keep Step F blocked.
