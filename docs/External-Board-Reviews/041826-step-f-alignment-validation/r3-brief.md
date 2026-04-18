# Board Review R3 (Deliberation) — Step F Fix Artifacts + Unblocked Items

**Date:** 2026-04-18
**Reviewing:** Commit `402f933` (Step F) + owner-authored fix snippets (this brief) + unblocked roadmap items
**Round:** R3 Deliberation — owner (facilitator) has authored concrete code snippets for each item proposed for application; board evaluates the snippets, proposes alternatives where disagreeing, and votes on each
**Rounds so far:** R1 Blind done → R2 Consolidation done (verdicts SIGN OFF WITH DISSENTS × 3, 2/3 FIX NOW unanimous on FN-A/FN-B) → R3 Deliberation (this) → R4 Confirmation

**STATELESS.** Read everything fresh. Do not assume you remember R1 or R2 even if you "wrote" them. All R2 convergence is inlined below.

---

## 1. Project background (self-contained)

**stop-git-std** — LLM-driven GitHub repo security auditor. Board-approved 9-phase pipeline (tool exec → validation → compute → structured LLM → prose LLM → assembly → render → validator → git-hook). 8/8/4 classification: 8 automatable / 8 structured LLM / 4 prose LLM. MD canonical, HTML derived.

Phase 7 renderer plan A→G. Steps A-F done. Step G next (requires board sign-off). Step F commit `402f933` is under review.

Full R1/R2 records at `/root/tinkering/stop-git-std/.board-review-temp/step-f-review/` (`pragmatist-r1.md`, `codex-r1.md`, `deepseek-r1.md`, `pragmatist-r2.md`, `codex-r2.md`, `deepseek-r2.md`). R1 brief at `/tmp/step-f-r1-brief.md`, R2 brief at `/tmp/step-f-r2-brief.md`.

## 2. R2 convergence summary

**Verdicts (R2):**
- Pragmatist: SIGN OFF WITH DISSENTS (conceded FN-B with 37-count verification)
- Codex: SIGN OFF WITH DISSENTS (moved from R1 BLOCK after fix artifacts accepted)
- DeepSeek: SIGN OFF WITH DISSENTS (conceded FN-C to DEFER)

**FIX NOW unanimous:**
- **FN-A:** Remove `| safe` on `prior_scan_note` in `docs/templates-html/partials/catalog.html.j2`
- **FN-B:** Add `| safe` on `css_content` in `docs/templates-html/scan-report.html.j2`

**DEFER unanimous:**
- **FN-C / D-1:** Parity regex extension to match H3 finding cards — DEFER, apply before Step G CI
- **FN-D / D-7:** Duplicated prose-like fields in Phase 4 findings — DEFER to Phase 4/5 generator
- **D-2:** Fixture provenance tag — DEFER, apply before Step G mixes live+synthetic
- **D-3:** `formal_review_rate` phase reclassification — DEFER to Phase 3 compute.py scoping
- **D-4:** Externalize `adjustFont` — DEFER to production deploy
- **D-5:** Template-source `| safe` lint — DEFER, low priority
- **D-6:** CSS autoescape path documentation — DEFER BUT should bundle with FN-B commit (Pragmatist + Codex position)

**Step G criteria converged:**
- Q6.1 LLM-in-the-loop for Phases 1-6 (unanimous)
- Q6.2 byte-stable = same form JSON → identical render twice (unanimous)
- Q6.3 zero errors + zero warnings — 2/3 want D-1 fix first; DeepSeek OK with documented `PAR-WARN-001`

**Remaining 2-1 split:**
- **PD3 (bundle/citation validator):** DeepSeek wants promotion to FIX NOW (Step F triggers it); Pragmatist + Codex say DEFER (Step G triggers it, not Step F). This is the main R3 deliberation question.

**NEW item surfaced by owner (unblocked by Step F completion):**
- **Integration of `render-html.py` into scan workflow.** STEP-F-verification.md line 143 notes: *"no scanner workflow step has been updated yet to call render-html.py. Integration into Phase 7 of an actual scan is a later task (likely part of Step G end-to-end integration)."* CLAUDE.md and operator guide still reference the old HTML template directly. R3 question: Is this integration a Step G pre-requisite or part of Step G itself?

---

## 3. Owner-authored fix snippets for R3 review

These are the **concrete snippets the facilitator intends to apply** pending board sign-off. Each item includes BEFORE/AFTER with anchored context. Board: either SECOND, author a better alternative with your own BEFORE/AFTER, or REJECT.

### FX-1 (from FN-A): remove `| safe` on `prior_scan_note`

**File:** `docs/templates-html/partials/catalog.html.j2`

**BEFORE** (lines 26-45, 20 lines of anchored context):
```jinja
{% set prompt_ver = form.get('_meta', {}).get('prompt_version', 'V2.3-post-R3') %}
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
    <div class="catalog-label">Catalog metadata</div>
    <table>
      <tr><td class="key">Report file</td><td class="val"><code>GitHub-Scanner-{{ target.repo }}.html</code> (+ <code>.md</code> companion)</td></tr>
      <tr><td class="key">Repo</td><td class="val"><a href="{{ target.url }}">github.com/{{ target.owner }}/{{ target.repo }}</a></td></tr>
      <tr><td class="key">Short description</td><td class="val">{{ short_desc }}</td></tr>
      <tr><td class="key">Category</td><td class="val">{{ catalog.get('category', '') }}</td></tr>
      <tr><td class="key">Subcategory</td><td class="val">{{ catalog.get('subcategory', '') }}</td></tr>
      <tr><td class="key">Verdict</td><td class="val {{ verdict_util }} fw-semi">{{ verdict_level }}{% if should_split %} (split){% endif %}</td></tr>
      <tr><td class="key">Scanned revision</td><td class="val">main @ {{ short_sha(head_sha) }} ({{ latest_tag }})</td></tr>
      <tr><td class="key">Prompt version</td><td class="val">{{ prompt_ver }}</td></tr>
      <tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
    </table>
  </div>
```

**AFTER:**
```jinja
{% set prompt_ver = form.get('_meta', {}).get('prompt_version', 'V2.3-post-R3') %}
{% set scanner_ver = form.get('_meta', {}).get('scanner_version', 'unknown') %}
{# prior_scan_note is Phase 4 structured LLM text, treat as plain text (autoescape). Fallback uses Unicode em-dash — NOT &mdash; entity, because the string is re-rendered through autoescape which would double-escape the & to &amp;. #}
{% set prior = catalog.get('prior_scan_note') or 'None \u2014 first scan of this repo.' %}
{% set short_desc = catalog.get('short_description') or repo_meta.get('description', '') %}
{% set verdict_util = VERDICT_UTIL_CLASS.get(verdict_level, 'val-warn') %}
  <div class="catalog-meta">
    <div class="catalog-label">Catalog metadata</div>
    <table>
      <tr><td class="key">Report file</td><td class="val"><code>GitHub-Scanner-{{ target.repo }}.html</code> (+ <code>.md</code> companion)</td></tr>
      <tr><td class="key">Repo</td><td class="val"><a href="{{ target.url }}">github.com/{{ target.owner }}/{{ target.repo }}</a></td></tr>
      <tr><td class="key">Short description</td><td class="val">{{ short_desc }}</td></tr>
      <tr><td class="key">Category</td><td class="val">{{ catalog.get('category', '') }}</td></tr>
      <tr><td class="key">Subcategory</td><td class="val">{{ catalog.get('subcategory', '') }}</td></tr>
      <tr><td class="key">Verdict</td><td class="val {{ verdict_util }} fw-semi">{{ verdict_level }}{% if should_split %} (split){% endif %}</td></tr>
      <tr><td class="key">Scanned revision</td><td class="val">main @ {{ short_sha(head_sha) }} ({{ latest_tag }})</td></tr>
      <tr><td class="key">Prompt version</td><td class="val">{{ prompt_ver }}</td></tr>
      <tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
    </table>
  </div>
```

**Changes:**
1. Line 28 fallback string: `'None &mdash; first scan of this repo.'` → `'None \u2014 first scan of this repo.'` (Unicode em-dash literal; avoids the `&` → `&amp;` double-escape bug Pragmatist R2 flagged)
2. Added `{#` comment explaining the choice
3. Line 42 table cell: `{{ prior | safe }}` → `{{ prior }}` (autoescape handles user content)

---

### FX-2 (from FN-B): mark `css_content` as safe

**File:** `docs/templates-html/scan-report.html.j2`

**BEFORE** (lines 11-22, 12 lines of anchored context):
```jinja
<title>Security Investigation: {{ target.owner }}/{{ target.repo }}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Unbounded:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{{ css_content }}
</style>
</head>
<body>

<div class="font-controls">
```

**AFTER:**
```jinja
<title>Security Investigation: {{ target.owner }}/{{ target.repo }}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Unbounded:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'unsafe-inline';">
<style>
{# css_content is loaded from docs/scanner-design-system.css via render-html.py _load_css(). It is a static disk file, not LLM or user input. Marking | safe is required because autoescape would HTML-encode single quotes in font-family declarations, pseudo-element content, and SVG data URIs — corrupting the stylesheet (browsers do not decode entities inside <style>). #}
{{ css_content | safe }}
</style>
</head>
<body>

<div class="font-controls">
```

**Changes:**
1. Line 17: `{{ css_content }}` → `{{ css_content | safe }}`
2. Added `{#` block comment explaining why `| safe` is correct here (satisfies D-6 "CSS autoescape path documentation")

---

### FX-3 (from D-1, proposed to bundle with FN-A/FN-B per Pragmatist + Codex position): parity regex extension

**File:** `docs/validate-scanner-report.py`

**BEFORE** (lines 445-456, 12 lines of anchored context):
```python
    # 1. Finding IDs — extract from both, MD is canonical
    md_findings = set(re.findall(r"###\s+(F\d+|F-[\w-]+)\s*[—–-]", md_raw))
    # HTML findings: look for finding IDs adjacent to severity/status markers in body text
    # Strip CSS/style/script/comments first to avoid false positives from rule references
    html_body = re.sub(r"<style[^>]*>.*?</style>", "", html_raw, flags=re.DOTALL | re.IGNORECASE)
    html_body = re.sub(r"<!--.*?-->", "", html_body, flags=re.DOTALL)
    html_body = re.sub(r"/\*.*?\*/", "", html_body, flags=re.DOTALL)
    # Match finding IDs in exhibit tags (most reliable HTML pattern)
    # Pattern 1: exhibit-item-tag content like "Dependabot alerts · F1" or "· F0"
    html_findings = set(re.findall(r'exhibit-item-tag[^<]*?(?:·|&middot;)\s*(F\d+|F-[\w-]+)', html_body))
    # Pattern 2: finding IDs with severity in heading-like context
    html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))
```

**AFTER:**
```python
    # 1. Finding IDs — extract from both, MD is canonical
    md_findings = set(re.findall(r"###\s+(F\d+|F-[\w-]+)\s*[—–-]", md_raw))
    # HTML findings: look for finding IDs adjacent to severity/status markers in body text
    # Strip CSS/style/script/comments first to avoid false positives from rule references
    html_body = re.sub(r"<style[^>]*>.*?</style>", "", html_raw, flags=re.DOTALL | re.IGNORECASE)
    html_body = re.sub(r"<!--.*?-->", "", html_body, flags=re.DOTALL)
    html_body = re.sub(r"/\*.*?\*/", "", html_body, flags=re.DOTALL)
    # Match finding IDs in exhibit tags (most reliable HTML pattern)
    # Pattern 1: exhibit-item-tag content like "Dependabot alerts · F1" or "· F0"
    html_findings = set(re.findall(r'exhibit-item-tag[^<]*?(?:·|&middot;)\s*(F\d+|F-[\w-]+)', html_body))
    # Pattern 2: finding IDs with severity in heading-like context
    html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))
    # Pattern 3: finding IDs inside <h3> finding-card headings (Step F renderer emits F<N> &mdash; <Title>)
    # Match the ID as the first token of an H3 after any nested spans/tags are stripped
    html_findings |= set(re.findall(
        r'<h3[^>]*>\s*(?:<[^>]+>\s*)*(F\d+|F-[\w-]+)\s*(?:&mdash;|—|–|-)',
        html_body,
    ))
```

**Changes:**
- Added Pattern 3 — matches the Step F H3 card format `<h3>F0 &mdash; Title</h3>` (and variants with nested `<span>` tags for status chips that precede the ID). Uses non-capturing `(?:<[^>]+>\s*)*` to step through any nested opening tags.
- Pragmatist R2 explicitly flagged DeepSeek's R1-proposed `.*?` wildcard as wrong (too permissive — matches prose text). My pattern anchors on `<h3>` + first F-ID token, which is tight.

**Rationale for bundling with FN-A/FN-B:** Pragmatist and Codex both said "D-1 should be applied before Step G." The clean way is one commit: FX-1 + FX-2 + FX-3 + D-2 fixture provenance (FX-4 below), all under the banner "Apply R2 unanimous FIX NOW + required pre-Step-G items."

---

### FX-4 (from D-2, proposed to bundle): fixture provenance tag

**File 1:** `tests/fixtures/caveman-form.json`
**File 2:** `tests/fixtures/archon-subset-form.json`

**BEFORE** (top of each file, `_meta` block):
```json
{
  "$comment": "... existing comment ...",
  "schema_version": "V1.1",
  "_meta": {
    "phases_completed": [...],
    "scan_status": "...",
    "scanner_version": "...",
    ...
  },
  ...
}
```

**AFTER:**
```json
{
  "$comment": "... existing comment ...",
  "schema_version": "V1.1",
  "_meta": {
    "phases_completed": [...],
    "scan_status": "...",
    "scanner_version": "...",
    "_fixture_provenance": "back-authored-from-golden-md",
    "_fixture_back_authored_from": "docs/GitHub-Scanner-caveman.md",
    "_fixture_authored_by": "Claude Sonnet 4.6 subagent, commit 402f933 (Step F)",
    ...
  },
  ...
}
```

**For archon-subset:** same pattern, `_fixture_back_authored_from` → `docs/GitHub-Scanner-Archon.md` with additional field `_fixture_subset_scope`: `"4 findings kept of 11 in golden — F0/F1/F4/F7; dropped F2/F3/F5/F6/F8/F9/F10 because they're variations of the same theme"`.

**For zustand-form.json:** NOT back-authored (authored as part of Step C fixture-enrichment fresh from the real scan data). Add instead:
```json
    "_fixture_provenance": "authored-from-scan-data",
    "_fixture_authored_for": "Step C fixture enrichment (commit 59224ac)",
```

**Schema impact:** `_meta` currently has `additionalProperties: false` at schema line 1066. The fix also needs to either (a) add these fields to the schema or (b) relax `additionalProperties` for the underscore-prefixed fields. Cleanest: add `_fixture_provenance`, `_fixture_back_authored_from`, `_fixture_authored_by`, `_fixture_subset_scope` as optional fields in the `_meta` properties block of the schema.

---

## 4. Unblocked items on the table

Step F completion unblocks these items. R3 should vote on each: **APPLY IN THIS COMMIT** | **APPLY IN NEXT COMMIT (before Step G)** | **DEFER (post-Step-G)**.

### U-1: Integration of `render-html.py` into scan workflow
**Context:** STEP-F-verification.md line 143 says `render-html.py` is not yet called from the actual scan workflow. CLAUDE.md (`/root/tinkering/stop-git-std/CLAUDE.md`) references the old HTML template approach (copy CSS verbatim into template). Operator guide (`docs/SCANNER-OPERATOR-GUIDE.md`) has the 6-phase workflow ending in "render HTML via template."
**Owner proposal:** APPLY IN NEXT COMMIT (before Step G). Update CLAUDE.md and SCANNER-OPERATOR-GUIDE.md to document: operator produces `form.json`, then runs `python3 docs/render-md.py form.json --out <name>.md` and `python3 docs/render-html.py form.json --out <name>.html` as the new Phase 7. Without this, Step G cannot run "live pipeline" because there's no documented pipeline to run.
**Board: vote.**

### U-2: D-1 parity regex extension (FX-3 above)
**Context:** See FX-3. Bundle with this commit.
**Owner proposal:** APPLY IN THIS COMMIT (part of the same batch as FN-A/FN-B since Pragmatist + Codex both said "before Step G").
**Board: vote on bundling (this commit vs separate commit).**

### U-3: D-2 fixture provenance tag (FX-4 above)
**Context:** See FX-4. Bundle with this commit.
**Owner proposal:** APPLY IN THIS COMMIT — low effort, prevents epistemic drift in Step G corpus.
**Board: vote on bundling.**

### U-4: D-6 CSS autoescape documentation (part of FX-2)
**Context:** Bundled into FX-2 as the block `{#` comment.
**Owner proposal:** APPLY IN THIS COMMIT (FX-2 already includes it).
**Board: approve comment wording or propose alternative.**

### U-5: PD3 bundle/citation validator
**Context:** DeepSeek R2 argued PD3 triggered by Step F (renderer complete). Pragmatist + Codex R2 said PD3 triggers after Step G (pipeline operational end-to-end). 2-1 split unresolved.
**Owner proposal:** DEFER until Step G proves pipeline operational. Rationale: PD3 validates fact/inference/synthesis separation in `findings-bundle.md`. That file is produced in Phase 3 of the scan workflow (pre-JSON-assembly). Step F shipped the renderer (Phase 7). No new `findings-bundle.md` has been produced through a real pipeline since Step F. Therefore the PD3 trigger ("JSON-first pipeline operational") is not met by Step F alone. But I concede DeepSeek's concern: Step G risks "pass with citation violations undetected." Compromise: list PD3 as a Step G acceptance criterion — the first Step G scan that produces a real `findings-bundle.md` MUST also trigger PD3 validator build.
**Board: vote on this compromise vs DeepSeek's FIX NOW vs Pragmatist/Codex pure DEFER.**

### U-6: D-5 template-source `| safe` lint
**Context:** FN-A exposed the gap — validator doesn't flag `| safe` in template source. If FX-1 is applied, the only `| safe` remaining will be FX-2's `css_content` (intentional). A simple grep-based lint would catch future unintentional bypasses.
**Owner proposal:** DEFER (Pragmatist + Codex R2 position). Small effort but not load-bearing once FX-1 applies.
**Board: confirm DEFER or promote.**

### U-7: D-3 `formal_review_rate` phase classification
**Context:** Lives in `phase_1_raw_capture` but is a derived percentage. Classification ambiguity.
**Owner proposal:** DEFER to Phase 3 compute.py formal scoping.
**Board: confirm.**

### U-8: D-4 externalize `adjustFont` script
**Context:** CSP `unsafe-inline` allows inline `<script>` for font-scale. Validator allowlists the `adjustFont` pattern explicitly.
**Owner proposal:** DEFER to production deploy.
**Board: confirm.**

### U-9: D-7 / FN-D remove duplicated prose-like fields from Phase 4
**Context:** `what_this_means` / `what_this_does_not_mean` exist in both Phase 4 and Phase 5 schema paths.
**Owner proposal:** DEFER to Phase 4/5 generator implementation.
**Board: confirm.**

---

## 5. Prior-roadmap deferred items (still-deferred, for completeness)

Board: for each, confirm DEFER or promote to FIX NOW. R2 reviewed these; R3 should not re-litigate unless NEW evidence has surfaced since R2.

| Item | R2 position | Owner R3 proposal | Board vote |
|---|---|---|---|
| RD1 — automate structured LLM | DEFER (20+ corpus) | DEFER | ? |
| SD2 — kind + domain typing | DEFER | DEFER | ? |
| RD4 — assumptions field | DEFER | DEFER | ? |
| SD3 — confidence scores | DEFER | DEFER | ? |
| SD4 — judgment fingerprint | DEFER (single-model) | DEFER | ? |
| SD7 — variable scorecard length | DEFER | DEFER | ? |
| SD8 — generic `artifacts[]` | DEFER | DEFER | ? |
| SD9 — permissions | DEFER (V2.0+) | DEFER | ? |
| SD10 — SBOM | DEFER (V2.0+) | DEFER | ? |
| RD5 — management sign-off | DEFER (V2.0+) | DEFER | ? |
| PD1/PD4/PD6/PD7 — packaging | DEFER (V2.0+) | DEFER | ? |

---

## 6. Post-apply verification plan

If FX-1 through FX-4 are approved in R3, the owner will:
1. Apply all 4 fix artifacts
2. Re-render zustand, caveman, archon-subset → HTML
3. Verify `grep -c "&#39;" /tmp/*-rendered.html` drops from 37 to **0 or near-zero** (only legitimate `&#39;` inside code blocks, not inside `<style>`)
4. Run `python3 docs/validate-scanner-report.py --report` on all 3 HTMLs — must exit 0
5. Run `python3 docs/validate-scanner-report.py --parity` on each MD/HTML pair — must produce **zero warnings** (FX-3 regex fix should catch the H3 finding IDs)
6. Run full test suite `python3 -m pytest tests/` — must pass 263/263 (or add/update tests if FX-3 changes parity behavior)
7. Update schema if FX-4 adds `_fixture_*` fields to `_meta.properties`
8. Present the applied diff + verification log to R4

---

## 7. What R3 must produce

Each agent returns a document with EXACTLY these sections:

### Verdict (R3)
SIGN OFF | SIGN OFF WITH DISSENTS | BLOCK. State if changed from R2.

### Vote on each owner-authored fix artifact
For FX-1, FX-2, FX-3, FX-4: **SECOND** | **ADJUST (with your own BEFORE/AFTER)** | **REJECT**. If ADJUST, provide anchored BEFORE/AFTER for your alternative. If your own fix is better than owner's, say so and give it.

### Vote on unblocked items U-1 through U-9
For each: **APPLY IN THIS COMMIT** | **APPLY IN NEXT COMMIT (before Step G)** | **DEFER (post-Step-G)** | **NOT APPLICABLE**. One sentence rationale per vote. Pay specific attention to U-1 (scan workflow integration) and U-5 (PD3 promotion).

### Prior-roadmap deferred items
One line per item: **CONFIRM DEFER** | **PROMOTE TO FIX NOW** (with rationale).

### Post-apply verification plan
SECOND the 8-step plan in Section 6, or propose additions/changes.

### Process notes
Brief. Any anti-pattern observation or R3-process improvement.

---

## 8. Ground rules

- Under 2500 words.
- Cite file paths + line numbers when proposing alternatives.
- If your R2 position was wrong, concede.
- Do not invent new FIX NOW items unless you surface a concrete new bug with repro evidence (not something already discussed in R1/R2).
- The split on PD3 (2-1 DeepSeek vs Pragmatist+Codex) MUST be resolved in R3 — R3 is the deliberation round where split items converge.

---

## 9. Files to READ (absolute paths, stateless)

**Essential:**
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-impl-verify/STEP-F-verification.md` (background, especially line 143)
- `/root/tinkering/stop-git-std/docs/templates-html/partials/catalog.html.j2` (26-45, FX-1 target)
- `/root/tinkering/stop-git-std/docs/templates-html/scan-report.html.j2` (11-22, FX-2 target)
- `/root/tinkering/stop-git-std/docs/validate-scanner-report.py` (445-456, FX-3 target)
- `/root/tinkering/stop-git-std/tests/fixtures/caveman-form.json` (`_meta` block, FX-4 target)
- `/root/tinkering/stop-git-std/docs/scan-schema.json` (lines ~1050-1110 for `_meta` definition with `additionalProperties: false`)

**R2 records (for R3 deliberation context):**
- `/root/tinkering/stop-git-std/.board-review-temp/step-f-review/pragmatist-r2.md`
- `/root/tinkering/stop-git-std/.board-review-temp/step-f-review/codex-r2.md`
- `/root/tinkering/stop-git-std/.board-review-temp/step-f-review/deepseek-r2.md`

**Verification command** (agents can run to confirm owner artifacts work):
```bash
cd /root/tinkering/stop-git-std && \
  python3 docs/render-html.py tests/fixtures/zustand-form.json --out /tmp/z-before.html && \
  echo "Before FX-2: $(grep -c '&#39;' /tmp/z-before.html) occurrences of &#39;"
```
