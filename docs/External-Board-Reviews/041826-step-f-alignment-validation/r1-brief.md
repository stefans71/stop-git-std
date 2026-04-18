# Board Review R1 (Blind) — Step F Alignment + Step G Readiness

**Date:** 2026-04-18
**Reviewing:** Commit `402f933` (Step F: HTML renderer + 2 new V1.1 fixtures) plus Step G readiness for the 7-step renderer plan (A→G)
**Round:** R1 Blind (each agent drafts independently; no cross-pollination)
**Rounds planned:** Blind → Consolidation → Deliberation (if needed) → Confirmation [→ Fix Artifacts if FIX NOW]
**Minimum agents per round:** 3 (per FrontierBoard SOP §4)

You are one of three reviewers. Draft your review alone. Do not reference other agents' output. Your job is not to be nice; it is to surface real risks before Step G commits us to end-to-end pipeline work.

---

## 1. Project background (self-contained — do NOT skip)

**stop-git-std** is an LLM-driven GitHub repo security auditor. Humans feed the tool a repo URL; an LLM walks a 9-phase pipeline that produces a MD + HTML security report. This is a "deep-dive investigation tool," not a static analyzer. 10 completed golden scans exist at `docs/GitHub-Scanner-*.md` / `.html` backing the corpus.

### Board-approved architecture (Session 3 & 4 reviews, canonical record: `docs/board-review-pipeline-methodology.md`)

**8/8/4 data-point classification** (118 data points across 10 golden scans, board-approved):
- **8 Automatable** (Python decision trees, V1.0): verdict level, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised
- **8 Structured LLM** (enums + templates, V1.0): general vuln severity, split-axis, priority evidence, threat model, action steps, timeline, capability assessment, catalog metadata
- **4 Prose LLM** (structural constraints only): "what this means", "what this does NOT mean", finding body, editorial caption

**9-phase pipeline:**
1. Tool execution → raw capture (FACT)
2. Data validation gate
3. Python computes 8 automatable fields (FACT-derived)
4. LLM fills 8 structured fields (enum/template constrained)
5. LLM writes 4 prose fields (structural constrained)
6. JSON assembly with provenance tags
7. Python renderer → MD + HTML
8. Validator gate
9. Git hook spot-checks

**Core invariants (board-enforced):**
- **MD is canonical.** HTML derives from same JSON, may NOT add findings absent from MD.
- **Facts / inference / synthesis are separate.** Raw capture = FACTS. Phase 3 = FACT-derived. Phase 4/5 = INFERENCE/SYNTHESIS with provenance tags.
- **Pre-computed form contract.** Renderer consumes post-Phase-6 snapshot. No lazy compute inside renderer.
- **Prose stays sparse.** Fixtures must not invent prose; existing golden-MD prose density is preserved.
- **Validator is the gate.** `validate-scanner-report.py --report` must exit 0 on both emitters.

### Completed work to date

**Phase 7 renderer plan (A→G), board-approved in `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`:**
| Step | Status | Commit |
|---|---|---|
| A — Schema freeze V1.1 (renderer-driven $defs, C2/C3 conditionals) | ✅ Done | `2b576bf` + `c6531bb` |
| B — render-md.py → Jinja2 (thin shim + 14 partials) | ✅ Done | `75db969` |
| C — Fixture enrichment (zustand, 10 FAs approved) | ✅ Done | `59224ac` |
| D — Flip tests to structural assertions (+39 tests) | ✅ Done | `aac2b3b` |
| E — Validator `--report` gate on rendered MD | ✅ Done | `cf8c576` |
| **F — HTML renderer + cross-shape fixture coverage** | ✅ Done | **`402f933`** (this review) |
| G — C7 acceptance matrix via end-to-end JSON-first pipeline | ⏳ Next, **board required** | — |

**Prior reviews archived:**
- `docs/External-Board-Reviews/041826-renderer-alignment/` — R1-R4 on the 7-step plan
- `docs/External-Board-Reviews/041826-renderer-impl-verify/` — R1 on Steps A+B implementation verification
- `docs/External-Board-Reviews/041826-fixture-enrichment/` — R1 on Step C fix artifacts (unanimous 3-0 approve)

---

## 2. What Step F shipped

Full verification record: `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-impl-verify/STEP-F-verification.md` (READ THIS — it has hypothesis, files + SHA-256, expected vs actual).

Summary:
- **`docs/render-html.py`** — 117-line Jinja2 shim, parallel to `render-md.py`. Loads post-Phase-6 form, embeds `scanner-design-system.css` verbatim via `{{ css_content }}`, renders with `autoescape=select_autoescape(['html','htm','j2'])`, `trim_blocks=True`, `lstrip_blocks=True`, `keep_trailing_newline=True`.
- **`docs/templates-html/scan-report.html.j2`** (top-level, 68 lines) + 14 partials at `docs/templates-html/partials/*.html.j2` (~1029 lines total). Translated from the 1988-line battle-tested `docs/GitHub-Repo-Scan-Template.html` scaffold.
- **Two new V1.1-compliant fixtures:**
  - `tests/fixtures/caveman-form.json` (1305 lines, 9 findings, split-verdict by version, Critical) — curl-pipe-from-main installer shape
  - `tests/fixtures/archon-subset-form.json` (1199 lines, 4 findings subset-scoped from 11-finding golden, monorepo with 11 inner packages, split-verdict by deployment, Critical) — agentic platform. **First fixture to exercise the V1.1 C3 `auto_load_tier` constraint** via `category: code/agent-rule-injection`.
- **117 new HTML structural tests** at `tests/test_render_html.py`, parameterized over all 3 fixtures.
- **Tests:** 263/263 passing (was 146; +117 HTML tests).

**Process note.** Fixtures and partials were authored by three Sonnet 4.6 subagents running in parallel (scope-drift + synthesis logs captured). Opus retained judgment and synthesis.

**Two bugs caught during verification and fixed:**
1. Template: `section_02.html.j2` emitted `<h3>{{ title }}</h3>` without finding ID prefix. Fixed to `<h3>{{ f.id }} &mdash; {{ title }}</h3>` matching reference scan. This flipped zustand HTML parity from "findings missing" to "all F-IDs present."
2. Fixture data: caveman and archon-subset verdict_exhibits had stale F-ID references (`Distribution · F1+F2`, `Supply chain · F2`, `Distribution · F8`) pointing to findings that existed in the original golden but were dropped during subset scoping. Fixed by stripping `· F<N>` suffixes. Parity check's MD-canonical-rule ERROR path correctly caught these — proof the gate works.

**MD/HTML parity check result** (for each of 3 fixtures): `✓ Parity check clean (with 1 warning(s))`. The warning is `MD findings missing from HTML` and is a **known regex limitation** — the parity check looks for `F<N> — <Severity>` but our HTML (and the reference scans') emits `F<N> — <Title>`. Running `--parity` on the battle-tested reference scan `docs/GitHub-Scanner-zustand.{md,html}` produces the identical warning pattern (verified). So our output matches reference behavior exactly.

---

## 3. What you need to EVALUATE (8 questions)

Agents may identify issues OUTSIDE these questions — welcome them. But every review must answer each:

### Q1: Is Step F faithful to the architecture?

Read `docs/render-html.py` and `docs/templates-html/scan-report.html.j2` and at least 2 partials (suggest `partials/section_02.html.j2` and `partials/verdict.html.j2`). Answer:
- Does the renderer violate the pre-computed form contract? (any lazy compute, any network calls, any file IO beyond CSS read and template load)
- Does it synthesize new data, or strictly render what the form provides?
- Does HTML introduce any field/finding not present in MD?

### Q2: Do the new fixtures honor the 8/8/4 classification?

Read `tests/fixtures/caveman-form.json` (or `archon-subset-form.json`) and cross-reference against `docs/scan-schema.json` (V1.1). For at least 5 fields, answer: does the field live in the right phase block?
- Phase 1 raw_capture = FACTS from `gh api` / OSSF / osv.dev / gitleaks
- Phase 3 computed = deterministic Python output (8 automatables)
- Phase 4 structured_llm = enum/template-constrained (8 structured)
- Phase 5 prose_llm = structural-constrained prose (4 prose)
- Is there any drift (prose expansion, synthesized facts in raw_capture, etc.)?

### Q3: Manual back-authoring of fixtures — is it epistemologically sound?

Sonnet subagents back-authored caveman + archon-subset fixtures from existing golden MDs (not from running a real pipeline). This is explicit; the STEP-F-verification.md calls it out. Your job:
- Is this a valid substrate for Step F's renderer testing, given Step G will run the real pipeline?
- What's the specific failure mode risk — where might a back-authored fixture look valid but hide a real pipeline issue?
- Should we add a provenance tag to the fixtures marking them as "back-authored, not pipeline-produced"?

### Q4: Is the parity-check regex limitation a real gap or acceptable?

The `--parity` mode's regex catches finding IDs only via (a) `exhibit-item-tag · F<N>` and (b) `F<N> — <Severity>`. Our H3s emit `F<N> — <Title>`, matching reference scans. This produces a warning every run. Your judgment:
- Is this an acceptable validator limitation (tolerable noise)?
- Or should the parity regex be extended to match H3 finding-card patterns?
- If we leave it as-is, what's the downside when Step G produces real pipeline output?

### Q5: Is the HTML renderer's autoescape policy safe?

The shim uses `autoescape=select_autoescape(['html','htm','j2'])`. CSS content is passed via `{{ css_content }}` (which gets escaped). Finding titles, evidence commands, repo names — all user-influenced text — go through variable interpolation.
- Does `{{ css_content }}` escape HTML inside CSS (e.g., quoting `content: ''` may break)? Verify or flag.
- Are there any `| safe` bypasses in the 14 partials that could be XSS vectors? (Sonnet's synthesis log mentioned one in `catalog.html.j2` for a `prior` field.)
- Does the CSP `script-src 'unsafe-inline'` + font-scale `<script>` pass the validator's XSS heuristics? (The validator has an explicit allowlist for `adjustFont` — is this load-bearing?)

### Q6: Step G scope — which shapes should run, and what are the acceptance criteria?

The renderer-alignment CONSOLIDATION.md says Step G = "C7 acceptance matrix + dual-emit verification: Archon re-run + one other shape + zustand, each producing V1.1-compliant JSON + valid MD+HTML."

But Step G requires the full upstream pipeline (Phases 1-6). Phases 4-6 (structured LLM, prose LLM, assembly) are NOT built yet — only Phase 7 (renderer) is.

Your recommendation:
- Do we build minimal Phase 4-6 automation before Step G?
- Or does Step G initially run with LLM-in-the-loop (human operator walks Phases 1-6, pipeline handles 7-8)?
- What are the minimum acceptance criteria for "pipeline reliable" that Step G must satisfy?
- Which 3 shapes (or alternative count) give the best cross-shape signal?

### Q7: Where are we vs where we said we'd be?

The canonical goal (per `project_pipeline_architecture.md`) is "LLM→JSON→renderer→HTML+MD" with structured separation of facts/inference/synthesis.
- After Step F, is the renderer side of "LLM→JSON→renderer" done?
- What's the remaining work to call the FULL pipeline operational?
- Are any deferred items (RD1, SD2, PD3 from the roadmap) now ready to activate based on Step F's output?
- Are we building technical debt we'll regret in Step G?

### Q8: Any FIX NOW items for Step F?

List items (if any) that MUST be addressed before Step G starts. For each FIX NOW, author a fix artifact with anchored context (BEFORE/AFTER) per FrontierBoard SOP §6. Distinguish from DEFER (can wait until after Step G) and INFO (noted for the record).

---

## 4. Files to READ (absolute paths — agents, you CAN read these with your bypass-approvals flag)

**Verification record & plan (READ FIRST):**
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-impl-verify/STEP-F-verification.md`
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`

**Code shipped:**
- `/root/tinkering/stop-git-std/docs/render-html.py`
- `/root/tinkering/stop-git-std/docs/templates-html/scan-report.html.j2`
- `/root/tinkering/stop-git-std/docs/templates-html/partials/hero.html.j2` (smallest, for pattern)
- `/root/tinkering/stop-git-std/docs/templates-html/partials/section_02.html.j2` (most complex)
- `/root/tinkering/stop-git-std/docs/templates-html/partials/verdict.html.j2` (split-verdict + exhibits)
- `/root/tinkering/stop-git-std/docs/templates-html/partials/catalog.html.j2` (has the `| safe` noted)

**Fixtures shipped:**
- `/root/tinkering/stop-git-std/tests/fixtures/caveman-form.json`
- `/root/tinkering/stop-git-std/tests/fixtures/archon-subset-form.json`
- `/root/tinkering/stop-git-std/tests/fixtures/zustand-form.json` (for comparison — earlier step)

**Tests:**
- `/root/tinkering/stop-git-std/tests/test_render_html.py`

**Schema + validator (the enforcement layer):**
- `/root/tinkering/stop-git-std/docs/scan-schema.json` (V1.1, 1412 lines)
- `/root/tinkering/stop-git-std/docs/validate-scanner-report.py`

**Architectural goals (reference):**
- `/root/tinkering/stop-git-std/docs/board-review-pipeline-methodology.md` (board-approved architecture)
- `/root/tinkering/stop-git-std/CLAUDE.md` (project operating rules)

**Reference golden outputs (for cross-shape comparison):**
- `/root/tinkering/stop-git-std/docs/GitHub-Scanner-caveman.md` — golden that caveman fixture is back-authored from
- `/root/tinkering/stop-git-std/docs/GitHub-Scanner-Archon.md` — golden that archon-subset fixture is back-authored from

---

## 5. Output format (required)

Produce a response with exactly these sections, in this order:

### Verdict
One of: **SIGN OFF** · **SIGN OFF WITH DISSENTS** · **BLOCK**

- SIGN OFF = Step F is done, Step G may proceed as planned
- SIGN OFF WITH DISSENTS = Step F acceptable, but with noted concerns to address later
- BLOCK = Step F has a flaw that must be fixed before Step G runs

### Q1-Q8 answers
One section per question, 2-6 sentences each. Cite specific file paths + line numbers where possible.

### FIX NOW items (if any)
For each: ID, title, location, rationale. If the item touches concrete code/schema/fixture, author a fix artifact in BEFORE/AFTER format with 3+ lines of anchored context per the SOP.

### DEFER items
Same format but flagged as DEFER with a trigger condition for when they become actionable.

### INFO items
Observations worth noting but not actionable this round.

### Anti-patterns or process drift you noticed
Any concern about HOW the work was done (subagent delegation, fixture authoring from goldens, skipping prior board reviews, etc.) goes here.

---

## 6. Ground rules

- You are one of **three** independent reviewers. Do not speculate about the other two.
- Be direct. If Step F looks fine, say so in one sentence and move on. If it has issues, name them with line numbers.
- Your lens is your lens — Pragmatist, Systems Thinker, or Skeptic — not a generic code review.
- Under 2500 words. Quality over volume.
- If you cannot open a file, say so and work from the brief. Do not fabricate line numbers.
