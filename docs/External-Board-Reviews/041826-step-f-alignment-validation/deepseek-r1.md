# Board Review R1 — Skeptic Lens on Step F

**Date:** 2026-04-18  
**Reviewer:** Skeptic (DeepSeek)  
**Commit:** `402f933` (Step F: HTML renderer + 2 new V1.1 fixtures)  
**Lens:** What breaks, what is hidden, what claims are not evidenced, test coverage gaps, Step G readiness

## Verdict
**SIGN OFF WITH DISSENTS**

Step F delivers a functional HTML renderer that passes validation and parity checks. However, there are material safety gaps (XSS vector in `| safe` bypass), validator blind spots (parity regex misses H3 titles), and epistemological concerns (back-authored fixtures hide pipeline integration risks). Step G cannot proceed until FIX NOW items are addressed.

## Q1-Q8 Answers

### Q1: Is Step F faithful to the architecture?

**Yes, with one minor deviation.** `/root/tinkering/stop-git-std/docs/render-html.py` respects the pre-computed form contract: no lazy compute, no network calls, no file IO beyond CSS read and template load. It synthesizes no new data — strictly renders what the form provides. HTML introduces no field/finding not present in MD (MD-canonical rule enforced by validator parity check).

**Deviation:** The renderer embeds CSS via `{{ css_content }}` (line 15 of scan-report.html.j2) which Jinja2 autoescape will HTML-escape. This could break CSS `content: ''` rules containing quotes. CSS should be marked safe or injected via `{% filter safe %}`.

### Q2: Do the new fixtures honor the 8/8/4 classification?

**Mostly, but with classification drift evidence.** Examining `/root/tinkering/stop-git-std/tests/fixtures/caveman-form.json`:

- **Phase 1 raw_capture** (lines 418-507): Contains FACTS from `gh api`/OSSF/gitleaks — correct.
- **Phase 3 computed** (lines 508-1261): Contains 8 automatable fields (C20 severity, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 classification) — correct.
- **Phase 4 structured_llm** (lines 1262-1305): Contains 8 structured fields (general vuln severity, split-axis, priority evidence, threat model, action steps, timeline, capability assessment, catalog metadata) — correct.
- **Phase 5 prose_llm**: Contains 4 prose fields — correct.

**Drift:** The `prior_scan_note` field (line 1178) contains HTML entity `&mdash;` which belongs in Phase 7 renderer, not Phase 4 structured data. This is prose expansion into structured field.

### Q3: Manual back-authoring of fixtures — is it epistemologically sound?

**No — this hides pipeline integration risks.** Back-authoring fixtures from golden MDs (`docs/GitHub-Scanner-caveman.md`) is valid for testing the renderer in isolation, but creates false confidence for Step G. The failure mode: Phase 4-6 (structured LLM, prose LLM, assembly) are NOT built. A back-authored fixture can be schema-valid while the real pipeline produces malformed JSON that fails validation or renders incorrectly.

**FIX NOW:** Add provenance tag `"_back_authored_from": "docs/GitHub-Scanner-caveman.md"` to fixture metadata. Step G must include at least one live pipeline run to validate integration.

### Q4: Is the parity-check regex limitation a real gap or acceptable?

**Real gap that creates validator blind spot.** `/root/tinkering/stop-git-std/docs/validate-scanner-report.py` lines 454-459 show the regex only matches:
1. `exhibit-item-tag · F<N>`
2. `F<N> — <Severity>`

Our HTML emits `F<N> — <Title>` in H3s (line 42 of section_02.html.j2). The validator warns "MD findings missing from HTML" for every finding. While this matches reference scan behavior, it's a **false negative** that trains us to ignore validator warnings.

**FIX NOW:** Extend regex pattern 2 to `F<N>\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info|.*?)` to catch titles. Or better: extract finding IDs from `<h3>` tags directly.

### Q5: Is the HTML renderer's autoescape policy safe?

**No — XSS vector present.** `/root/tinkering/stop-git-std/docs/templates-html/partials/catalog.html.j2` line 42: `{{ prior | safe }}` bypasses autoescape. The `prior_scan_note` field contains user-influenced text (could be repo name, scan dates). If the pipeline ever populates this from untrusted source (e.g., prior scan filename), this is XSS.

**CSS escaping issue:** `{{ css_content }}` gets HTML-escaped (line 15 of scan-report.html.j2). CSS `content: '<script>'` would become `content: '&lt;script&gt;'`, breaking styling.

**CSP `script-src 'unsafe-inline'`:** The `adjustFont` script (lines 22-31 of scan-report.html.j2) is allowlisted in validator heuristics — acceptable for prototype but should be externalized for production.

**FIX NOW:** Remove `| safe` filter; HTML-escape `prior` field. Mark CSS as safe via `{% filter safe %}`.

### Q6: Step G scope — which shapes should run, and what are the acceptance criteria?

**Step G is not ready.** The consolidation plan says Step G = "C7 acceptance matrix + dual-emit verification: Archon re-run + one other shape + zustand." But:

1. **Phases 4-6 are NOT built** — only `compute.py` (Phase 3) exists. No structured LLM, prose LLM, or assembly implementation.
2. **We cannot run "real pipeline"** without human operator walking Phases 1-6 manually.

**Recommendation:** Build minimal Phase 4-6 automation before Step G. At minimum:
- Phase 4: Template-based LLM calls for 8 structured fields
- Phase 5: Constrained prose generation for 4 prose fields  
- Phase 6: JSON assembly with provenance tags

**Acceptance criteria for Step G:**
1. Automated pipeline runs Phases 1-6 end-to-end for 3 shapes (Archon, caveman, zustand)
2. Produces V1.1-compliant JSON that validates against schema
3. Renders to MD+HTML that pass `--report` and `--parity` checks
4. No manual intervention beyond initial repo URL input

### Q7: Where are we vs where we said we'd be?

**Renderer side complete, pipeline side incomplete.** The "LLM→JSON→renderer" vision has `→renderer` done (Steps A-F). But `LLM→JSON` is not automated — Phases 4-5 require human LLM operation.

**Technical debt:** Back-authored fixtures create illusion of pipeline completeness. The `| safe` XSS vector and parity regex blind spot are quality gaps.

**Deferred items:** SD2 (finding `kind` + `domain` orthogonal typing) remains V1.2. C3 `auto_load_tier` constraint tested in archon-subset fixture — good.

### Q8: Any FIX NOW items for Step F?

**Yes — 3 FIX NOW items:**

1. **XSS vector in `| safe` filter** (catalog.html.j2:42)
2. **Parity regex blind spot** (validate-scanner-report.py:459)  
3. **CSS escaping breaks `content:` rules** (scan-report.html.j2:15)

Plus 1 DEFER: Back-authored fixture provenance tags.

## FIX NOW Items

### FIX NOW 1: Remove XSS vector `| safe` filter
**Location:** `/root/tinkering/stop-git-std/docs/templates-html/partials/catalog.html.j2:42`
**Rationale:** `prior_scan_note` contains user-influenced text; `| safe` bypasses autoescape, creating XSS if field contains `<script>`.
**Fix artifact:**
```jinja2
BEFORE:
<tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>

AFTER:
<tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
```

### FIX NOW 2: Fix parity regex to catch H3 finding titles
**Location:** `/root/tinkering/stop-git-std/docs/validate-scanner-report.py:459`
**Rationale:** Current regex `F<N> — <Severity>` misses `F<N> — <Title>` pattern, causing false "MD findings missing from HTML" warnings.
**Fix artifact:**
```python
BEFORE:
html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))

AFTER:
html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info|.*?)", html_body))
# OR better: extract from <h3> tags directly
```

### FIX NOW 3: Mark CSS as safe to prevent escaping
**Location:** `/root/tinkering/stop-git-std/docs/templates-html/scan-report.html.j2:15-17`
**Rationale:** `{{ css_content }}` gets HTML-escaped, breaking CSS `content: ''` rules.
**Fix artifact:**
```jinja2
BEFORE:
<style>
{{ css_content }}
</style>

AFTER:
<style>
{% filter safe %}
{{ css_content }}
{% endfilter %}
</style>
```

## DEFER Items

### DEFER 1: Add provenance tag to back-authored fixtures
**Location:** Fixture metadata in `tests/fixtures/caveman-form.json` and `archon-subset-form.json`
**Rationale:** Documents that fixtures are manually authored from golden MDs, not pipeline-produced.
**Trigger:** Before Step G execution.

### DEFER 2: Externalize `adjustFont` script from CSP unsafe-inline
**Location:** `/root/tinkering/stop-git-std/docs/templates-html/scan-report.html.j2:22-31`
**Rationale:** CSP `script-src 'unsafe-inline'` is acceptable for prototype but should be fixed for production.
**Trigger:** Before production deployment.

## INFO Items

1. **Fixture classification drift:** `prior_scan_note` contains HTML entity `&mdash;` — renderer concern, not structured data.
2. **Test coverage:** 117 new HTML tests good, but no tests for XSS vectors or CSS escaping.
3. **Process:** Sonnet subagent delegation worked (3 parallel agents, ~365s wall time).

## Anti-patterns or Process Drift

1. **Back-authoring hides integration risk:** Creating fixtures from golden outputs tests renderer in isolation but gives false confidence for end-to-end pipeline. Should have at least one fixture produced by minimal pipeline stub.

2. **Validator warning normalization:** Parity regex limitation produces consistent warning that teams learn to ignore. This trains bad behavior — ignoring validator output.

3. **Safety review gap:** `| safe` filter added without security review. Sonnet synthesis log mentioned it but no human flagged the XSS risk.

4. **Step G scope creep:** Consolidation.md says Step G requires "real pipeline" but Phases 4-6 don't exist. This sets up Step G for failure or scope reduction.

**Root cause:** Velocity prioritized over completeness. Renderer ships with known gaps (parity warning, CSS escape) because "reference scan does same." This is technical debt that will compound in Step G.

---

**Final:** Step F is mechanically sound but has safety and completeness gaps that must be fixed before Step G. The renderer works; the pipeline story is incomplete.