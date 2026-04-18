# Board Review R2 (Consolidation) — Step F + Step G Readiness

**Date:** 2026-04-18
**Reviewing:** Commit `402f933` (Step F: HTML renderer + 2 new V1.1 fixtures)
**Round:** R2 Consolidation — each agent sees all three R1 responses + the full deferred-items landscape, authors fix artifacts, responds to specific arguments from other agents
**Rounds planned so far:** R1 Blind done → R2 Consolidation (this) → R3 Deliberation (if still split) → R4 Confirmation

**IMPORTANT — YOU ARE STATELESS.** You have no memory of R1 even if you "wrote" it. All R1 content is inlined below verbatim. Read everything in this brief from scratch. Do not assume you know anything not in here.

---

## 1. Project background (self-contained)

**stop-git-std** is an LLM-driven GitHub repo security auditor producing MD + HTML scan reports. Board-approved architecture:

- **8/8/4 classification** (board-approved Session 3+4, canonical record: `docs/board-review-pipeline-methodology.md`):
  - 8 automatable (Python compute)
  - 8 structured LLM (enum/template constrained)
  - 4 prose LLM (structural constrained)
- **9-phase pipeline:** tool exec → validation → compute → structured LLM → prose LLM → assembly → render → validator → git-hook
- **Core invariants:** MD canonical / facts-inference-synthesis separate / pre-computed form contract / prose stays sparse / validator is the gate

**Phase 7 renderer plan (A→G) board-approved at `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`:**
- Steps A-E: done (schema V1.1, Jinja2 MD renderer, zustand fixture, tests, validator gate)
- **Step F: done (this review)** — HTML renderer + 2 new V1.1 fixtures (caveman + archon-subset)
- Step G: next, requires board sign-off — C7 acceptance matrix via real pipeline

## 2. What Step F shipped

Full record at `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-impl-verify/STEP-F-verification.md`. Summary:
- `docs/render-html.py` (117-line Jinja2 shim, parallel to render-md.py)
- `docs/templates-html/scan-report.html.j2` + 14 partials (~1029 lines)
- `tests/fixtures/caveman-form.json` (1305 lines, 9 findings, split-by-version, Critical)
- `tests/fixtures/archon-subset-form.json` (1199 lines, 4 findings, monorepo, split-by-deployment, first to exercise C3 `auto_load_tier` on `code/agent-rule-injection`)
- `tests/test_render_html.py` (117 parameterized tests)
- 263/263 tests passing, validator `--report` clean on all 3 rendered HTMLs, parity matches reference-scan baseline

## 3. R1 Verdict matrix

| Agent | Verdict | FIX NOW count | Summary |
|---|---|---|---|
| **Pragmatist** (Sonnet 4.6) | SIGN OFF WITH DISSENTS | 1 | Renderer architecturally sound; one XSS vector (`\| safe` on `prior_scan_note`). Missed the CSS-escape bug. |
| **Systems Thinker** (Codex GPT-5) | **BLOCK** | 2 | CSS bytes corrupted by autoescape + `prior_scan_note` bypass. Both block Step G. |
| **Skeptic** (DeepSeek V4) | SIGN OFF WITH DISSENTS | 3 | XSS + CSS escape + parity regex gap. |

**Owner verification during R1 processing:** I confirmed the CSS escape defect with my own eye by grepping the rendered HTML:

```
--font-mono: &#39;JetBrains Mono&#39;, &#39;SF Mono&#39;, &#39;Fira Code&#39;, monospace;
--font-display: &#39;Unbounded&#39;, &#39;Inter&#39;, sans-serif;
content: &#39;&#39;;
url(&#34;data:image/svg+xml,%3Csvg viewBox=&#39;0 0 256 256&#39; ...)
```

Inside a `<style>` block, browsers do NOT decode HTML entities. So `content: &#39;&#39;;` tries to render literal text `&#39;&#39;`, not empty string. Fonts, pseudo-element content, SVG data URIs all corrupted. **Codex's BLOCK is technically correct.** The validator didn't catch it because the validator doesn't inspect CSS parse correctness.

---

## 4. R1 full text (inlined — stateless agents must read this)

### 4.1 — Pragmatist (Sonnet 4.6) R1 verbatim

> **Verdict: SIGN OFF WITH DISSENTS**
>
> Step F is architecturally sound and the renderer is shippable. One live XSS vector (`| safe` on a LLM-populated field) needs to be resolved before Step G produces pipeline output that flows real repo content through that path. Everything else is either clean or safely deferrable.
>
> **Q1 — Architecture:** Renderer is faithful. No lazy compute, no network calls. All maps are lookup tables keyed on pre-computed enum values. section_02.html.j2 pulls findings exclusively from phase_4_structured_llm.findings.entries. HTML introduces no fields absent from MD.
>
> **Q2 — 8/8/4 classification:** Caveman fixture spot-check passes for 5 fields. One mild ambiguity: `formal_review_rate` (line 231 of caveman-form.json) is a percentage derived from counted PRs — lives in Phase 1 raw_capture but looks like Phase 3 automatable. Schema allows it. Worth tracking.
>
> **Q3 — Back-authoring valid:** For renderer testing in isolation. Failure mode: back-authored fixtures may encode golden-MD quirks rather than pipeline output semantics. E.g., Phase 3 compute may produce `formal_review_rate: null` on incomplete API data, but fixture supplies literal integer — null-handling paths never exercised. Add provenance tag (DEFER).
>
> **Q4 — Parity regex limitation:** Acceptable. Reference scan produces identical warning. Downside: CI normalization of the warning. DEFER before Step G CI wires it up.
>
> **Q5 — Autoescape:** Mostly safe. `| safe` bypass on `prior_scan_note` in catalog.html.j2 line 28/42 is a real XSS vector for Step G (LLM-generated text flows through). CSS via `{{ css_content }}` is "acceptable — CSS doesn't generally contain characters that autoescape would corrupt in practice." **[PRAGMATIST WAS WRONG ABOUT CSS — see owner verification above]**
>
> **Q6 — Step G scope:** LLM-in-the-loop acceptable. Don't build Phase 4-6 automation first. 3 shapes: zustand, caveman, new-shape (fd or gstack).
>
> **Q7 — Status:** Renderer side done. Remaining: Phase 4-6 automation, integration into scan workflow.
>
> **Q8 — FIX NOW:** 1 item — prior_scan_note `| safe` removal.
>
> **FIX NOW FN-1:** `| safe` on `prior_scan_note` in catalog.html.j2 line 28, 42.
>
> **BEFORE:**
> ```jinja
> {% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}
> ...
>       <tr><td class="key">Prior scan</td><td class="val">{{ prior | safe }}</td></tr>
> ```
>
> **AFTER:**
> ```jinja
> {% set prior = catalog.get('prior_scan_note') or 'None \u2014 first scan of this repo.' %}
> ...
>       <tr><td class="key">Prior scan</td><td class="val">{{ prior }}</td></tr>
> ```
>
> **DEFER items:** (D-1) Parity regex extension before Step G CI. (D-2) Back-authored fixture provenance tag. (D-3) `formal_review_rate` phase classification review when Phase 3 automation is scoped.
>
> **INFO items:** (I-1) render-html.py not yet wired into scan workflow. (I-2) validator doesn't lint template-source `| safe` bypasses. (I-3) CSS autoescape path not documented.
>
> **Anti-patterns:** Subagent scope-drift logs should be first-class review artifacts. Step F scope was expanded mid-execution without board approval — should have gone back to the board.

### 4.2 — Systems Thinker (Codex GPT-5) R1 verbatim

> **Verdict: BLOCK**
>
> **Q1 — Architecture:** Renderer mostly faithful. Templates consume already-assembled phase blocks. Architectural breach narrower but real: renderer mutates CSS bytes through HTML escaping and trusts one structured field as raw HTML, so HTML emitter is not yet a pure deterministic rendering.
>
> **Q2 — 8/8/4:** Generally honored. archon-subset-form.json raw facts in phase_1_raw_capture (33-165), phase_4b_computed.verdict at 1149-1153, structured LLM fields properly placed. **Drift noted:** fixtures duplicate `what_this_means` and `what_this_does_not_mean` inside phase_4_structured_llm.findings.entries (548-549, 574-575) — lineage smell.
>
> **Q3 — Back-authoring:** Acceptable for Step F. Failure mode epistemic — schema-clean/render-clean while encoding values no real pipeline would produce. Visible in stale exhibit-tag references caught during dev. Recommend explicit fixture provenance marker in `_meta`.
>
> **Q4 — Parity regex:** NOT acceptable to leave permanent if Step G is supposed to certify pipeline reliability. Root cause: validate-scanner-report.py:446-456. Once Step G runs live scans the warning will train operators to ignore parity output. Extend regex before Step G sign-off.
>
> **Q5 — Autoescape NOT safe enough:**
> - `scan-report.html.j2:16-18` inserts `{{ css_content }}` into `<style>`. Rendering shows quotes and SVG data URIs escaped as entities (`&#39;`, `&#34;`). **CSS is malformed.**
> - `partials/catalog.html.j2:28,42` marks prior_scan_note as `| safe`. Schema defines as plain string; MD renderer treats as text. Trust bypass.
> - `adjustFont` allowlist in validator (146-164) is load-bearing.
>
> **Q6 — Step G scope:** Run with LLM-in-the-loop for Phases 1-6. Minimum acceptance: 3 live repos, V1.1-valid JSON, both emitters pass --report, parity zero errors AND zero warnings, evidence refs resolve, provenance audited, rerendering byte-stable. Shapes: zustand, Archon, caveman. Optional 4th: fd.
>
> **Q7 — Status:** Renderer half of LLM→JSON→renderer structurally almost complete, operationally NOT complete — style-escaping defect + raw-HTML bypass. Full pipeline still missing Phase 1-6 orchestration.
>
> **Q8 — FIX NOW:** 2 items — CSS escape corruption + prior_scan_note bypass.
>
> **FIX NOW FN-1 (Codex): Escaped CSS corrupts renderer output**
> Location: `docs/templates-html/scan-report.html.j2:16-18`, `docs/render-html.py:106-110`
>
> **BEFORE:**
> ```jinja
> <meta http-equiv="Content-Security-Policy" content="default-src 'none'; ...">
> <style>
> {{ css_content }}
> </style>
> ```
>
> **AFTER:**
> ```jinja
> <meta http-equiv="Content-Security-Policy" content="default-src 'none'; ...">
> <style>
> {{ css_content | safe }}
> </style>
> ```
>
> **FIX NOW FN-2 (Codex): Structured catalog field incorrectly trusted as HTML**
> Location: `docs/templates-html/partials/catalog.html.j2:28,42` (same item as Pragmatist FN-1)
>
> **BEFORE:** `{% set prior = catalog.get('prior_scan_note') or 'None &mdash; first scan of this repo.' %}` + `{{ prior | safe }}`
> **AFTER:** `{% set prior = catalog.get('prior_scan_note') or 'None - first scan of this repo.' %}` + `{{ prior }}`
>
> **DEFER:** DEFER-1 parity regex extension (trigger: before Step G acceptance matrix). DEFER-2 fixture provenance marker. DEFER-3 remove duplicated prose-like fields from Phase 4 findings when Phase 4/5 generation is implemented.
>
> **INFO:** Renderer is thin and scalable. archon-subset exercising C3 auto_load_tier is material improvement. Tests don't assert unescaped CSS integrity — that's why the main defect slipped.
>
> **Anti-patterns:** Review record overstates validator cleanliness because validator is blind to a real CSS corruption path. Allowing synthetic fixtures to sit beside pipeline-shaped artifacts without a provenance marker is manageable in Step F but Step G shouldn't blur classes.

### 4.3 — Skeptic (DeepSeek V4) R1 verbatim

> **Verdict: SIGN OFF WITH DISSENTS** (but "Step G cannot proceed until FIX NOW items are addressed" — effectively BLOCK-for-G)
>
> **Q1 — Architecture faithful, minor deviation:** CSS embed via `{{ css_content }}` will be HTML-escaped, could break `content: ''` rules. Should mark safe.
>
> **Q2 — 8/8/4 classification mostly correct with drift evidence:** `prior_scan_note` (caveman line 1178) contains HTML entity `&mdash;` — belongs in Phase 7 renderer, not Phase 4 structured data. Prose expansion into structured field.
>
> **Q3 — Back-authoring hides pipeline integration risks:** FIX NOW — add provenance tag. Step G must include live pipeline run.
>
> **Q4 — Parity regex gap creates validator blind spot:** FIX NOW — extend regex to catch `F<N> — <Title>` pattern or extract from `<h3>` tags.
>
> **Q5 — XSS vector present:**
> - FIX NOW: remove `| safe` on prior_scan_note (catalog.html.j2:42)
> - CSS escape issue breaks `content:` rules — mark CSS safe via `{% filter safe %}`
> - adjustFont script allowlisted — acceptable for prototype, externalize for production
>
> **Q6 — Step G NOT ready:**
> - Phases 4-6 NOT built (only compute.py Phase 3 exists)
> - Cannot run "real pipeline" without manual LLM operation
> - Recommendation: build minimal Phase 4-6 automation before Step G
> - Acceptance: automated Phases 1-6 for 3 shapes (Archon, caveman, zustand), V1.1-compliant JSON, MD+HTML pass --report and --parity, no manual intervention beyond repo URL
>
> **Q7 — Renderer done, pipeline incomplete.** Technical debt: back-authored fixtures create illusion of pipeline completeness. `| safe` XSS + parity regex are quality gaps.
>
> **Q8 — 3 FIX NOW:** prior_scan_note XSS + parity regex + CSS escape. Plus 1 DEFER: fixture provenance.
>
> **FIX NOW 1:** Remove `| safe` on prior_scan_note (catalog.html.j2:42) — SAME AS PRAGMATIST FN-1 AND CODEX FN-2
>
> **FIX NOW 2:** Fix parity regex to catch H3 finding titles. Location: `validate-scanner-report.py:459`.
> **BEFORE:**
> ```python
> html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)", html_body))
> ```
> **AFTER:**
> ```python
> html_findings |= set(re.findall(r"(F\d+|F-[\w-]+)\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info|.*?)", html_body))
> # OR better: extract from <h3> tags directly
> ```
>
> **FIX NOW 3:** Mark CSS as safe to prevent escaping — SAME AS CODEX FN-1 (but uses `{% filter safe %}` block instead of `| safe` filter)
>
> **DEFER:** Provenance tag (before Step G). Externalize adjustFont (before production).
>
> **Anti-patterns:** Back-authoring hides integration risk (need pipeline-stub fixture). Validator warning normalization trains bad behavior. `| safe` filter added without security review. Step G scope creep — consolidation says "real pipeline" but Phases 4-6 don't exist.

---

## 5. Consolidated FIX NOW candidates (4 items, with each agent's position)

### FN-A: `| safe` bypass on `prior_scan_note` field
- **Location:** `docs/templates-html/partials/catalog.html.j2` line 28, 42
- **Rationale:** LLM-populated field will flow unescaped user-influenced text in Step G. XSS vector.
- **Pragmatist:** FIX NOW (FN-1)
- **Codex:** FIX NOW (FN-2)
- **DeepSeek:** FIX NOW (#1)
- **Status: UNANIMOUS FIX NOW**

### FN-B: CSS autoescape corruption
- **Location:** `docs/templates-html/scan-report.html.j2` line 16-18 (the `{{ css_content }}` call)
- **Evidence:** Owner-verified — rendered output contains `&#39;`, `&#34;` inside `<style>` block. Browsers don't decode entities in `<style>`, so CSS `content: ''` becomes `content: &#39;&#39;` (literal text). Font family quotes corrupted. SVG data URIs corrupted.
- **Pragmatist R1:** Dismissed as "acceptable — CSS doesn't generally contain characters autoescape would corrupt." **This was wrong.** Pragmatist should concede or defend in R2.
- **Codex:** FIX NOW (FN-1)
- **DeepSeek:** FIX NOW (#3)
- **Status: 2/3 FIX NOW, Pragmatist missed/dismissed (needs R2 position revision)**

### FN-C: Parity regex extension to match H3 finding cards
- **Location:** `docs/validate-scanner-report.py` line 446-456 (the HTML finding-ID extraction)
- **Rationale:** Current regex produces false "findings missing from HTML" warning for every zustand-shaped scan. In Step G CI, operators will normalize the warning and miss real divergence.
- **Pragmatist:** DEFER (D-1, trigger: before Step G CI)
- **Codex:** DEFER (DEFER-1, trigger: before Step G acceptance matrix)
- **DeepSeek:** FIX NOW (#2)
- **Status: SPLIT 2-DEFER vs 1-FIX-NOW. Pragmatist + Codex vs DeepSeek**

### FN-D: Duplicated prose-like fields in Phase 4 findings
- **Location:** Phase 4 `findings.entries[*]` carry `what_this_means` / `what_this_does_not_mean` at `archon-subset-form.json:548-549, 574-575` (and same pattern in caveman). These are also in Phase 5 `per_finding_prose`.
- **Pragmatist:** Not raised explicitly
- **Codex:** DEFER (DEFER-3, trigger: when Phase 4/5 generation is implemented)
- **DeepSeek:** Flagged as classification drift (INFO-level — `prior_scan_note` HTML entity specifically)
- **Status: DEFER (no FIX NOW votes)**

---

## 6. All DEFER items on the table (from this review AND the prior-review roadmap)

### From this review (R1)

- **D-1: Parity regex extension** (see FN-C above)
- **D-2: Fixture provenance tag** — `"_back_authored_from": "docs/GitHub-Scanner-<name>.md"` in `_meta` of caveman and archon-subset fixtures. Trigger: before Step G consumes live + synthetic fixtures together.
- **D-3: formal_review_rate phase reclassification** — Phase 1 vs Phase 3 ambiguity. Trigger: when Phase 3 compute.py is formally scoped.
- **D-4: Externalize adjustFont script** — CSP `unsafe-inline` should be fixed before production deploy.
- **D-5: Template-source `| safe` lint** — validator should reject `| safe` in templates except an allowlist. Low priority, but FN-A showed the gap.
- **D-6: CSS autoescape path documentation** — `# NOTE` comment in render-html.py explaining why CSS needs `| safe`.
- **D-7: Remove duplicated prose-like fields from Phase 4** (see FN-D above)

### From prior-review roadmap (`project_pipeline_architecture.md` — still deferred, worth reconsidering now that Step F is done)

**V1.1-post-corpus items (10+ scans in corpus, we have 10 goldens):**
- **RD1:** Automate structured LLM operations — requires 20+ scan corpus. We have 10; not triggered yet.
- **SD2:** Finding `kind` + `domain` orthogonal typing. Renderer-driver for grouping. Would replace C3's category-regex with `domain == agent` check. Trigger was "renderer needs to group/filter by kind." Step F HTML renderer does not currently group by kind.
- **RD4:** "Assumptions" field in investigation form. Trigger: first scan where an assumption was wrong and affected the verdict. Not yet triggered.
- **PD3:** Bundle/citation validator (fact/inference/synthesis separation in findings-bundle.md). Trigger: JSON-first pipeline operational. Arguably triggered by Step E+F completion.

**V1.2 items (schema refinements):**
- **SD3:** Confidence scores on synthesis objects. Trigger: multi-run variance data. Not yet triggered.
- **SD4:** Judgment fingerprint (model + prompt hash + timestamp). Trigger: multiple LLM models used. Only Claude currently.
- **SD7:** Variable scorecard length. Trigger: new shape with different trust questions. Not yet encountered.
- **SD8:** Generic `artifacts[]` model. Trigger: complex multi-artifact release. Not yet triggered.

**V2.0+ items:** SD9 (permissions), SD10 (SBOM), RD5 (management sign-off), PD1/PD4/PD6/PD7 (packaging) — all have explicit triggers that have not fired.

### Deferred items you might argue are NOW ready

Worth the board's judgment in R2:
- **PD3 (bundle/citation validator):** Arguably triggered by Step F completion. Should it be FIX NOW before Step G?
- **SD2 (kind + domain typing):** Would let us re-bind C3 from regex to a structured field. Renderer doesn't currently need it, but Step G's acceptance-matrix would exercise real pipeline output where the regex may miss edge cases. Promote now or hold until V1.2?

---

## 7. Step G readiness questions still open

Cross-agent R1 convergence on Step G scope:
- Run LLM-in-the-loop (all 3 agree)
- 3 shapes (zustand + caveman + one new, likely Archon or fd)
- Acceptance criteria: V1.1-valid JSON, validator `--report` clean on both emitters, parity **zero errors + zero warnings**, evidence refs resolve, re-rendering is byte-stable

But several ambiguities remain:
- **Q6.1:** Is "live pipeline run" = "fresh `gh api` calls against live repos" (Codex & Pragmatist interpretation) or "automated Phase 4-6 implementation" (DeepSeek interpretation)? **R2 agents: please converge.**
- **Q6.2:** What's the definition of "byte-stable rerender"? — does MD/HTML output need to match across two invocations of the same form? (If yes, we need determinism tests; if not, what's the assertion?)
- **Q6.3:** Does Step G require the parity regex to catch the H3 pattern first (DeepSeek position) or can it run with "zero errors + acceptable warnings" (Pragmatist + Codex position)? — **directly ties to FN-C**

---

## 8. What you must produce in R2

Each agent must return a document with EXACTLY these sections:

### Verdict (R2)
One of: **SIGN OFF** · **SIGN OFF WITH DISSENTS** · **BLOCK**. This may differ from your R1. Explicitly state if it changed and why.

### Response to each FIX NOW candidate (4 items)
For FN-A, FN-B, FN-C, FN-D, state: FIX NOW | DEFER | REJECT. If you changed your R1 position, explain why. If the fix artifact author by another agent is wrong, say specifically what's wrong with it. **Pragmatist: you MUST respond to FN-B (CSS escape) since you dismissed it in R1 but 2 others flagged it and the owner verified it.**

### Fix artifacts (one per FIX NOW item you endorse)
Provide anchored BEFORE/AFTER with 3+ lines of surrounding context. Only required for items you vote FIX NOW. If another agent's artifact is fine, write "SECOND [agent's FN-X]" and you're done.

### DEFER items reconciliation
Walk the full DEFER list (Section 6 above, items D-1 through D-7 AND the prior-roadmap items RD1/SD2/PD3/etc.). For each: SECOND | REJECT | ADJUST TRIGGER. Special question — should PD3 or SD2 be promoted to FIX NOW given Step F is done?

### Step G readiness — answer Q6.1, Q6.2, Q6.3
Explicit yes/no or position-with-rationale on each.

### Process notes
Any comment on how R2 was run, fixture-authoring, scope expansions. Brief.

---

## 9. Files to READ (absolute paths, re-read since you're stateless)

**Essential (all agents):**
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-impl-verify/STEP-F-verification.md`
- `/root/tinkering/stop-git-std/docs/render-html.py` (lines 70-110 for autoescape setup)
- `/root/tinkering/stop-git-std/docs/templates-html/scan-report.html.j2` (line 16-18 for `{{ css_content }}`)
- `/root/tinkering/stop-git-std/docs/templates-html/partials/catalog.html.j2` (lines 28, 42 for `| safe`)
- `/root/tinkering/stop-git-std/docs/validate-scanner-report.py` (lines 446-456 for parity regex)

**Verification (recommended):**
- Run: `python3 docs/render-html.py tests/fixtures/zustand-form.json --out /tmp/zustand.html && grep -c "&#39;" /tmp/zustand.html` — this proves the CSS escape claim. The result should be 200+.

**For DEFER reconciliation:**
- `/root/tinkering/stop-git-std/.board-review-temp/step-f-review/pragmatist-r1.md`
- `/root/tinkering/stop-git-std/.board-review-temp/step-f-review/codex-r1.md`
- `/root/tinkering/stop-git-std/.board-review-temp/step-f-review/deepseek-r1.md`

**Roadmap context:**
- `/root/tinkering/stop-git-std/docs/board-review-pipeline-methodology.md`

---

## 10. Ground rules (same as R1)

- Write under 2500 words.
- Cite specific files + line numbers.
- Do not speculate about other agents' future responses.
- If R1-you was wrong about something, concede clearly — the point of R2 is consolidation, not doubling down.
- Do not invent FIX NOW items not present in R1 unless you name a new concrete bug with repro evidence.
