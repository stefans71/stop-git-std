# Pragmatist (Sonnet 4.6) — R2 Consolidation

**Date:** 2026-04-18
**Reviewing:** Commit `402f933` — Step F HTML renderer
**Round:** R2 Consolidation (self-verified CSS defect — 37 `&#39;` occurrences in rendered output)

---

## Verdict (R2)

**SIGN OFF WITH DISSENTS** — unchanged label, but the scope of what blocks Step G has changed.

R1 verdict was SIGN OFF WITH DISSENTS on the strength of one FIX NOW (FN-A). That was wrong. FN-B (CSS escape corruption) is a confirmed defect, not an acceptable tradeoff, and should have been FIX NOW in R1. Codex's BLOCK was technically correct. I am not adopting BLOCK as my own verdict because both fixes are narrow one-liner changes and I expect they will be applied before Step G is authorized — at which point the file is clean. But Step G cannot be authorized until both FN-A and FN-B are applied and re-validated. Codex's BLOCK stands for this commit as-is.

---

## Response to each FIX NOW candidate

### FN-A: `| safe` on `prior_scan_note` — FIX NOW (unchanged)

Unanimous. The artifact I authored in R1 is correct except for one detail: Codex's artifact replaces the `&mdash;` fallback with a plain ASCII dash. My R1 used a Unicode em-dash literal (`\u2014`). Both are functionally equivalent — the `&mdash;` in the original is a Jinja template string, not HTML output, but since Jinja autoescape is on, any `&` in the Python string would be re-escaped to `&amp;mdash;` on render, which is wrong. The Unicode literal is the correct fix. SECOND my own R1 FN-1 artifact with the `\u2014` fallback.

### FN-B: CSS autoescape corruption — CONCEDE. FIX NOW.

R1 position: "CSS doesn't generally contain characters that autoescape would corrupt in practice." That was wrong.

Verification run:
```
python3 docs/render-html.py tests/fixtures/zustand-form.json --out /tmp/zustand.html && grep -c "&#39;" /tmp/zustand.html
```
Result: **37 occurrences**. The rendered output contains `&#39;` inside the `<style>` block where a browser will interpret it as literal text, not as `'`. This corrupts:
- Font-family stacks
- Pseudo-element content
- SVG data URIs embedded in the CSS

The root cause is `autoescape=select_autoescape(["html", "htm", "j2"])` in `render-html.py:83`. The fix is `| safe` on `{{ css_content }}` since the CSS content is a static file read from disk, not LLM-generated or user-supplied. XSS risk of marking it safe is zero.

SECOND Codex FN-1 artifact exactly — `{{ css_content | safe }}` at scan-report.html.j2:17. Plus adding a one-line comment in `render-html.py:render()` ("css_content is a static disk file — safe to mark | safe") should be part of the FN-B fix commit.

### FN-C: Parity regex extension — DEFER (position unchanged, clarified rationale)

DeepSeek votes FIX NOW. Codex and I both vote DEFER with trigger "before Step G acceptance matrix."

**DeepSeek's proposed fix (`.*?` wildcard after the severity token) is wrong as written** — it would match any string after the dash, including false positives from prose text that happens to contain an `F\d+` pattern. DeepSeek's secondary suggestion (parse `<h3>` tags directly) is better but was not fully specified as a code artifact.

The correct fix would parse H3 content with something like:
```python
html_findings |= set(re.findall(r'<h3[^>]*>\s*(?:<[^>]+>)*\s*(F\d+|F-[\w-]+)', html_body))
```

But I am not proposing this as FIX NOW because: (1) the warning is already present in reference scans — it's a known baseline; (2) the validator still catches ID mismatches at the error level via Pattern 1 (exhibit tags); (3) the right fix requires reading the actual H3 template structure carefully before authoring the regex. Rushing a wrong regex is worse than a deferred correct one. DEFER with trigger: before Step G CI is wired up, the regex fix must be authored against the actual H3 template output and tested.

### FN-D: Duplicated prose-like fields in Phase 4 findings — DEFER (position unchanged)

No FIX NOW votes from any agent. Fixture-authoring artifact for a schema field that Phase 4/5 generation hasn't been implemented for. When Phase 4/5 generation is built, the duplication question resolves naturally. SECOND Codex DEFER-3.

---

## Fix artifacts

- **FN-A:** SECOND my own R1 artifact (catalog.html.j2, replace `| safe` + fix fallback string to Unicode em-dash `\u2014`).
- **FN-B:** SECOND Codex FN-1 artifact exactly — `{{ css_content | safe }}` at scan-report.html.j2:17.

No new artifacts introduced.

---

## DEFER items reconciliation

**D-1: Parity regex extension** — SECOND Codex DEFER-1. Trigger: before Step G acceptance matrix is run.

**D-2: Fixture provenance tag** — SECOND. Add `"_back_authored_from": "docs/GitHub-Scanner-<name>.md"` to `_meta` in caveman and archon-subset fixtures.

**D-3: formal_review_rate phase classification** — SECOND. Trigger: when Phase 3 compute.py is formally scoped.

**D-4: Externalize adjustFont script** — SECOND. Trigger: before production deploy.

**D-5: Template-source `| safe` lint** — SECOND. Low effort. Trigger: after FN-A is applied.

**D-6: CSS autoescape path documentation** — SECOND, upgrade the trigger. A one-line comment should be part of the FN-B fix commit, not deferred separately.

**D-7: Remove duplicated prose-like fields from Phase 4** — SECOND Codex DEFER-3.

**Prior-roadmap items:**

**RD1 (automate structured LLM):** SECOND DEFER. Trigger not met.

**SD2 (kind + domain orthogonal typing):** SECOND as DEFER. Not promoting to FIX NOW. The H3 card renderer doesn't group by `kind` — it groups by severity.

**PD3 (bundle/citation validator):** SECOND as DEFER. Steps A–F completing the renderer does not fully trigger PD3 — the pipeline still needs Phase 1–6 orchestration. Step G will produce the first real pipeline output; PD3 is appropriately triggered AFTER Step G confirms the pipeline is operational end-to-end.

**RD4, SD3, SD4, SD7, SD8, V2.0+ items:** All SECOND as deferred. None of their triggers have fired.

---

## Step G readiness — Q6.1, Q6.2, Q6.3

**Q6.1: "Live pipeline run" definition**

Converge on the Pragmatist + Codex interpretation: "live pipeline run" means fresh `gh api` calls against live repos, with the LLM-in-the-loop for Phases 4–6, producing real V1.1-valid JSON. It does NOT require automated Phase 4–6 orchestration before Step G.

**Q6.2: "Byte-stable rerender" definition**

Given the same `form.json` input, two invocations produce bitwise-identical output. Already guaranteed by deterministic Jinja2 path. Simple assertion: render twice, `diff` the outputs, expect empty.

**Q6.3: Parity regex and Step G acceptance**

FN-C is DEFER, but the Step G acceptance criterion must be "zero errors AND zero warnings." DeepSeek is right that normalizing warnings trains bad behavior. **The resolution: apply the D-1 parity regex fix before Step G runs, so the criterion is clean.** D-1 should be applied in the same batch as FN-A and FN-B.

Proposed Step G acceptance matrix (converged):
- 3 live repo shapes: zustand, caveman, third shape TBD (fd or Archon)
- V1.1-valid JSON confirmed by schema validator
- `--report` exits 0 on both `.html` and `.md`
- Parity check: zero errors AND zero warnings (requires D-1 fix applied first)
- Evidence refs resolve
- Rerender byte-stable

---

## Process notes

R1 missed FN-B because I did not run the verification command. That was a failure of method, not just a wrong conclusion. The R2 requirement to either concede or defend with evidence was the correct correction mechanism.

Scope note: Step F was expanded mid-execution to include two new fixtures (caveman, archon-subset) without a board approval checkpoint. The fixtures are valuable, but the scope expansion pattern should be documented as requiring a board check-in.
