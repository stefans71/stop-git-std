# Pragmatist R1 — Step F Alignment + Step G Readiness

**Agent:** Claude Sonnet 4.6 (Pragmatist lens — Opus wrote Step F, Sonnet reviews per same-model rule)
**Round:** R1 Blind
**Date:** 2026-04-18

---

### Verdict

**SIGN OFF WITH DISSENTS**

Step F is architecturally sound and the renderer is shippable. One live XSS vector (`| safe` on a LLM-populated field) needs to be resolved before Step G produces pipeline output that flows real repo content through that path. Everything else is either clean or safely deferrable.

---

### Q1 — Is Step F faithful to the architecture?

The renderer is faithful. `render-html.py` has no lazy compute, no network calls, and no file IO beyond the CSS read (line 74: `CSS_PATH.read_text`) and template loading via `FileSystemLoader`. All maps (`SEV_UTIL_CLASS`, `VERDICT_BANNER_CLASS`, etc.) are Python-level lookup tables keyed on pre-computed enum values — they translate, they do not decide. `section_02.html.j2` (lines 17-23) pulls findings exclusively from `phase_4_structured_llm.findings.entries` and prose from `phase_5_prose_llm.per_finding_prose.entries`. No synthesis, no derived field creation. The pre-computed form contract holds.

HTML does not introduce findings absent from MD. The `section_02` partial loops the same `findings` array the MD renderer consumes. The parity-check gate (which already proved its worth catching two stale F-ID references during development) confirms this per fixture.

---

### Q2 — Do the new fixtures honor the 8/8/4 classification?

Spot-check of five fields in `caveman-form.json`:

1. `phase_1_raw_capture.pre_flight.head_sha` — raw fact from `gh api`. Correct phase.
2. `phase_1_raw_capture.pr_review.formal_review_rate` (line 231: `15`) — computed from PR data, lives in Phase 1 raw_capture. This is a mild classification ambiguity: `formal_review_rate` is a percentage derived from counted PRs, which looks like a Phase 3 automatable output, not a raw captured fact. In practice the schema allows it in Phase 1 and the board approved this classification, so not a blocker — but worth tracking.
3. `phase_3_computed.solo_maintainer` — deterministic boolean from contributor count. Correct phase, correct semantics.
4. `phase_4_structured_llm.findings.entries[*].severity` — enum-constrained LLM output. Correct phase.
5. `phase_5_prose_llm.per_finding_prose.entries[*].what_this_does_not_mean` — prose LLM field. Correct phase.

No drift detected. Prose fields contain no synthesized raw facts; raw_capture fields contain no LLM text. The `archon-subset` fixture similarly validates: C3 `auto_load_tier` is correctly placed in `phase_4_structured_llm.findings.entries` entries with `category: code/agent-rule-injection`. Classification discipline is intact.

---

### Q3 — Manual back-authoring of fixtures — is it epistemologically sound?

It is valid for the stated purpose: testing the renderer in isolation. The fixtures test that the Jinja2 templates correctly consume V1.1-shaped JSON and produce validator-clean HTML. They do not test that the upstream pipeline (Phases 1-6) produces correct JSON. The STEP-F-verification.md correctly calls this out under "What this does NOT close."

The specific failure mode risk: back-authored fixtures may encode the golden MD's quirks rather than the pipeline's output semantics. For example, if the real Phase 3 compute produces `formal_review_rate: null` when the API returns incomplete data, but the back-authored fixture supplies a literal integer, the renderer will never exercise the null-handling paths. Similarly, Phase 4/5 LLM fields might produce prose edge cases (very long strings, markdown inside JSON strings, Unicode sequences) that the golden MDs don't contain, and those won't stress-test the autoescape behavior.

A provenance tag should be added. This is a DEFER item (see below) — it's useful metadata but not urgent while Step G hasn't produced pipeline JSON yet. Once Step G runs, the contrast between pipeline-produced and back-authored fixtures is the diagnostic signal; the tag makes that contrast machine-readable.

---

### Q4 — Is the parity-check regex limitation a real gap or acceptable?

Acceptable, with one caveat. The brief's own evidence is conclusive: running `--parity` against the battle-tested reference scan `docs/GitHub-Scanner-zustand.{md,html}` produces the identical warning. The limitation predates Step F and represents the baseline. Our HTML output matches reference-scan behavior exactly.

The downside for Step G: the parity check will continue to emit a warning for every run, which creates noise. If Step G adds CI integration, a future engineer might suppress the warning or treat it as expected boilerplate, masking a genuine MD/HTML finding-count divergence. That's a real long-term risk but not a Step G blocker.

Pragmatist take: fix the parity regex in a discrete commit before Step G CI wires it up, so the warning doesn't become load-bearing noise. This is a DEFER with a concrete trigger: before parity check runs in CI.

---

### Q5 — Is the HTML renderer's autoescape policy safe?

Mostly yes, with one real issue.

**CSS content via `{{ css_content }}`**: The CSS is a static file committed to the repo (`docs/scanner-design-system.css`). Jinja2 autoescape will HTML-encode characters like `<`, `>`, `&`, `"` in it. CSS does not generally contain these characters in ways that would break rendering — the validator's CSS sync check (used in `--template` mode) confirms the CSS matches what's in the design system. The real-world risk here is low: if the CSS had a `content: '<'` declaration, autoescape would render it as `content: '&lt;'`, which is valid CSS for that property. No `<style>` content in our design system uses raw HTML entities in value positions. Acceptable.

**`| safe` in `catalog.html.j2` line 42**: This is the one real issue. The `prior_scan_note` field is populated by Phase 4 structured LLM (`catalog_metadata.prior_scan_note`). The fallback in the template is `'None &mdash; first scan of this repo.'`, which contains a literal HTML entity — hence the `| safe` bypass. But this also means any LLM-generated content in that field bypasses autoescape entirely. In current fixtures this field is either null/absent or a static string. In Step G pipeline output, it will contain LLM-generated prose referencing prior scans. If a scanned repo's name, URL, or prior-report filename contains `<script>` or other HTML, an injected Phase 4 LLM response could deliver it unescaped into the rendered HTML.

The correct fix is narrow: don't mark the field `| safe`. Instead, store the raw text in the fixture (e.g., `"None — first scan of this repo."` with a real em-dash or plain ASCII), let autoescape handle it, and emit the `&mdash;` entity only in the fallback inside the template logic. This is a FIX NOW because Step G will produce real pipeline JSON flowing LLM text through this path.

**CSP `script-src 'unsafe-inline'`**: The validator explicitly allowlists the `adjustFont` script block (lines 148-152 of `validate-scanner-report.py`). The allowlist check verifies both that "adjustFont" is in the script body and that the script is under 10 lines. The font-scale script in `scan-report.html.j2` (lines 28-34) is 7 lines. This is load-bearing but correctly scoped — the validator would catch any additional `<script>` blocks added to the template.

---

### Q6 — Step G scope — shapes and acceptance criteria

The key constraint the brief surfaces: Phases 4-6 (structured LLM, prose LLM, assembly) are not automated yet. Step G as originally defined requires full pipeline output.

Pragmatist recommendation: **do not build full Phase 4-6 automation before Step G**. Instead, scope Step G as "LLM-in-the-loop operator run" — human operator walks Phases 1-5 following the existing investigation prompt, produces a V1.1-compliant JSON, and the automated pipeline handles Phases 7-8 (render + validate). This is exactly how scans currently work (the operator IS the LLM). Step G's value is proving the JSON→renderer path is correct for real pipeline output, not that Phases 4-6 are automated.

Minimum acceptance criteria for Step G:
1. Operator produces a V1.1-compliant JSON via real `gh api` calls (not back-authored from a golden MD).
2. `render-md.py` and `render-html.py` both produce validator-clean output.
3. Parity check passes with zero errors (warnings acceptable per Q4 baseline).
4. At least one finding in the real JSON differs from the corresponding golden MD finding (proving this is genuinely a new pipeline run, not a copy).

Shapes for Step G: zustand (known-clean baseline, low complexity), caveman (curl-pipe installer, split verdict, highest user risk relevance), and one new shape not in the current 3 fixtures (fd or gstack would add CLI-with-binaries or Claude Code skills coverage). Three shapes is the right count — adding more delays without proportional signal.

---

### Q7 — Where are we vs where we said we'd be?

The renderer side of "LLM→JSON→renderer" is done. Both emitters (MD and HTML) are Jinja2-based, parameterized over a shared V1.1 form, produce validator-clean output across 3 structurally distinct shapes, and have 263 passing tests. That is the entirety of Phase 7.

Remaining work to call the full pipeline operational:
- Phases 1-3: these are partially done — `gh api` tooling exists, `compute.py` handles Phase 3 automatable fields. The operator guide already documents the human-in-the-loop walkthrough.
- Phases 4-5 automation: not built. Currently LLM-in-the-loop (operator).
- Phase 6 assembly: not explicitly built as a standalone step; fixtures suggest it's the operator's JSON-construction step.
- Integration: `render-html.py` is not yet wired into the scan workflow (CLAUDE.md still says "render HTML via template").

Deferred items from the roadmap: RD1 (schema version field in rendered outputs for forward-compat) is not yet actionable — the renderer already passes `prompt_version` through from the form, so this is handled. SD2 (C3 trigger re-bind to `domain==agent`) is still deferred and correctly so — no pipeline currently produces that domain field. PD3 is not visible in files I've read; cannot assess.

Technical debt risk for Step G: none that I'd call regrettable. The `| safe` bypass (Q5) is the one item that would compound if left alone into Step G.

---

### Q8 — FIX NOW items for Step F

One FIX NOW.

---

### FIX NOW items

**FN-1: `| safe` bypass on LLM-populated `prior_scan_note` field**

- **Location:** `docs/templates-html/partials/catalog.html.j2`, line 28 and line 42
- **Rationale:** The `| safe` filter disables Jinja2 autoescape for the `prior` variable, which is set from `catalog_metadata.prior_scan_note` (a Phase 4 LLM output) with a fallback HTML-entity string. In Step G, real pipeline runs will flow LLM-generated text through this path. If the LLM includes a repo name, URL, or prior-report reference that contains `<`, `>`, or `&` characters (e.g., `<script>alert(1)</script>` injected via a compromised repo description that made it into a prior scan note), it would render unescaped. The fix has two parts: (a) change the fallback to use a plain-text em-dash or ASCII, and (b) remove `| safe`.

**BEFORE** (lines 28 and 42 of `catalog.html.j2`):
```jinja
{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
```

**AFTER:**
```jinja
{% set prior = catalog.get('prior_scan_note') or 'None \u2014 first scan of this repo.' %}
...
      <tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
```

The em-dash Unicode literal (`\u2014`) or the ASCII fallback `"None -- first scan of this repo."` both render correctly without `| safe`. Autoescape then handles any LLM-produced content in the field. The validator's `--report` mode should independently flag `| safe` bypasses; if it does not, that's a separate gap (see INFO items).

---

### DEFER items

**D-1: Parity-check regex should match H3 finding-card patterns**
- Trigger: before parity check is wired into CI for Step G.
- The current regex misses finding IDs in `<h3>F<N> &mdash; <Title></h3>`. Fix the regex to also match `F\d+ &mdash;` or `F\d+ —` patterns. Until CI integration, the warning is tolerable noise per Q4 analysis.

**D-2: Provenance tag on back-authored fixtures**
- Trigger: when Step G produces the first pipeline-generated JSON.
- Add a `"fixture_provenance": "back-authored"` field to the fixture `$comment` or `_meta` block so machine comparisons can distinguish back-authored from pipeline-produced fixtures. Also worth adding a short note in the test file's docstring.

**D-3: `formal_review_rate` phase classification ambiguity**
- Trigger: when Phase 3 compute.py is formally scoped for full automation.
- `formal_review_rate` is a derived computation (percentage of PRs with formal review) but lives in `phase_1_raw_capture`. If Phase 3 automation is built to produce all automatable fields, this field may need migration to `phase_3_computed` for classification hygiene. Not urgent while Phase 3 is human-assisted.

---

### INFO items

**I-1: `render-html.py` not yet wired into the scan workflow.** CLAUDE.md and the operator guide still reference the old HTML template directly. This is correct per STEP-F-verification.md ("What this does NOT close") but should be the first integration task in Step G.

**I-2: Validator does not explicitly flag `| safe` bypasses in template source.** The validator runs against rendered HTML, not template source. A malicious or mistaken `| safe` in a template would only be caught if the resulting HTML triggered the XSS vector heuristic (which requires an actual `<script>` or event-handler output, not just escaped-content bypass). Consider adding a template-source lint that greps for `| safe` in `--template` mode. Low priority, but FN-1 is evidence this gap is real.

**I-3: CSS autoescape.** The CSS contains no characters that autoescape would corrupt in practice. But the `{{ css_content }}` path is not documented as "intentionally escaped." Adding a `# NOTE: CSS is HTML-escaped by Jinja2 autoescape; this is safe because...` comment in `render-html.py` near line 109 would prevent a future dev from adding `| safe` thinking it's needed.

---

### Anti-patterns or process drift

**Subagent delegation for fixture authoring is appropriate but scope-drift logs should be reviewed.** The STEP-F-verification.md records scope-drift items for all three subagents (caveman: 10, archon-subset: 11 planned subset decisions, partial HTML converter: 4). These were documented, which is good. But the brief doesn't record whether the scope-drift items were reviewed and explicitly approved by Opus before commit. The two fixture bugs that were caught (stale F-ID references) originated in subagent-authored content. This is the expected failure mode of back-authoring: subagents extract from golden MDs faithfully but miss structural context (e.g., which findings were subset-dropped). The process worked — the parity gate caught the issues — but the drift logs should be a first-class review artifact for future delegations, not just a log note.

**Step F's scope was expanded mid-execution without board approval.** The original plan had Step F as "HTML renderer against zustand only." It was expanded by owner directive to cover 3 shapes. The expansion produced real value (caught the H3 bug on caveman/archon-subset before Step G). But this is the second time scope has been expanded within a step without going back to the board — the board approved the 7-step plan, not an expanded Step F. For Step G (which has explicit board approval requirement), any scope changes should be treated as requiring board sign-off rather than owner directive alone.
