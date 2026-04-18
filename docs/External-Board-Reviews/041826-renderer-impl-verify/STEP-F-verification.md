# Step F — HTML Renderer + Cross-Shape Fixture Coverage

**Date:** 2026-04-18
**Step:** F of the 7-step renderer plan (A→G) from `../041826-renderer-alignment/CONSOLIDATION.md`
**Scope:** **Modified** — expanded from "HTML renderer against zustand" to "HTML renderer against 3 shapes (zustand + caveman + archon-subset)" to catch cross-shape template issues before Step G. Owner directive, 2026-04-18.
**Type:** Mechanical verification + fixture authoring. No board review required per plan (Step G gates cross-shape "pipeline reliable" claim; Step F verifies the renderer itself).
**Operator:** Claude Opus 4.7 + 3 Sonnet 4.6 subagents (parallel mechanical work)
**Outcome:** PASS — all 3 fixtures render HTML clean, validator `--report` exits 0 on each, MD/HTML parity matches reference-scan baseline, 117 new HTML structural tests pass, full test suite 263/263.

---

## Hypothesis

The Phase 7 HTML renderer, built as a parallel Jinja2 shim to `render-md.py` with its own partials directory (`docs/templates-html/`), should:

1. Produce validator-clean HTML on the 3 test fixtures.
2. Pass MD/HTML parity check against each fixture's rendered MD companion.
3. Handle 3 structurally-distinct shapes without template rework:
   - **zustand** — JS/TS library, single-channel distribution, Caution verdict
   - **caveman** — curl-pipe-from-main installer, split-verdict by version, Critical verdict, 9 findings
   - **archon-subset** — agentic-platform monorepo (11 inner packages), split-verdict by deployment, Critical verdict, first fixture to exercise the C3 `auto_load_tier` constraint on `code/agent-rule-injection` category
4. Preserve the battle-tested structural patterns of `docs/GitHub-Repo-Scan-Template.html` (class names, DOM nesting, EXAMPLE-block repeaters translated to Jinja2 loops).
5. Deliver structural tests that exercise all 3 fixtures, not just zustand.

Failure modes checked:
- Template rendering errors on cross-shape data (e.g., caveman has no monorepo; archon IS monorepo)
- Phantom finding-ID references in HTML not present in MD (MD-canonical rule violation)
- Validator strict-mode failures (inline styles, placeholder tokens, EXAMPLE markers, XSS vectors)

---

## Files used

### Shipped this step
| Role | Path | SHA-256 |
|------|------|---------|
| HTML renderer shim | `docs/render-html.py` | `e142bf71a31891306a18913b63cdb2555645f6d41a0791d15e448a33cff5f97e` |
| Top-level template | `docs/templates-html/scan-report.html.j2` | (new, 48 lines) |
| Partials directory | `docs/templates-html/partials/*.html.j2` | 14 partials, ~1029 lines total (hero 53 + 13 others ~978 lines) |
| Caveman V1.1 fixture | `tests/fixtures/caveman-form.json` | `0e7f33e759ca1221026cfeb3395e222e888368c936735496cf2a6d35ef34b937` |
| Archon-subset V1.1 fixture | `tests/fixtures/archon-subset-form.json` | `bca46c04c16f1235926b803d0771bacbd1031cfd1fd1903010656f618e8a749e` |
| HTML structural tests | `tests/test_render_html.py` | 286 lines, 117 parameterized tests |

### Existing, unchanged
| Role | Path | SHA-256 |
|------|------|---------|
| Schema | `docs/scan-schema.json` (V1.1) | `2ee1324393e3d4810ae4e0efa9a4f03c238ffc9e0733777ec83545ad20b39ad0` |
| CSS (embedded verbatim) | `docs/scanner-design-system.css` | 824 lines, tracked in-repo |
| Zustand V1.1 fixture | `tests/fixtures/zustand-form.json` | unchanged from Step C |
| Validator | `docs/validate-scanner-report.py` (`--report` + `--parity` modes) | unchanged |
| Structural reference | `docs/GitHub-Repo-Scan-Template.html` | unchanged (1988-line scaffold with `{{PLACEHOLDER}}` tokens translated to Jinja2) |

### Derived artifacts (not committed)
| Role | Path | SHA-256 |
|------|------|---------|
| Rendered HTML — zustand | `/tmp/zustand-rendered.html` (2325 lines) | `f561919e94f4a2dcb4c9fa122a229a3e7b61384757452d2fc79c9e4be1b7765a` |
| Rendered HTML — caveman | `/tmp/caveman-rendered.html` (2156 lines) | `4057c5c72351557b049db93b4bc5a3ce5b32fddff641d0b9ef4e1e3341f3b67d` |
| Rendered HTML — archon-subset | `/tmp/archon-subset-rendered.html` (2070 lines) | `0bab09dd84b62ca9790a86bafc932694bfc67680ea7f8683dd991cb3e88dc622` |

---

## Commands executed

```bash
# For each fixture: render HTML, render MD, validate HTML, parity-check
for f in zustand caveman archon-subset; do
  python3 docs/render-html.py tests/fixtures/$f-form.json --out /tmp/$f-rendered.html
  python3 docs/render-md.py   tests/fixtures/$f-form.json --out /tmp/$f-rendered.md
  python3 docs/validate-scanner-report.py --report /tmp/$f-rendered.html
  python3 docs/validate-scanner-report.py --parity /tmp/$f-rendered.md /tmp/$f-rendered.html
done

# Full test suite
python3 -m pytest tests/ -q
```

---

## Expected results

1. Every `--report` validation exits 0 with all 9 strict checks passing.
2. Every `--parity` check reports "clean" (warnings acceptable if they match reference-scan behavior — see baseline check below).
3. `tests/test_render_html.py` passes 100% across 3 fixtures (skeleton, validator invariants, hero, catalog, verdict, scorecard, section headings, finding cards, methodology, shape-specific).
4. Full suite (`tests/`) passes 100%.

---

## Actual results

**Render + validator gate** — all 3 fixtures clean:
| Fixture | HTML lines | Validator `--report` |
|---------|-----------:|----------------------|
| zustand | 2325 | ✓ clean (all 9 checks pass) |
| caveman | 2156 | ✓ clean (all 9 checks pass) |
| archon-subset | 2070 | ✓ clean (all 9 checks pass) |

**MD/HTML parity check** — all 3 clean:
| Fixture | Errors | Warnings | Verdict level match | Scorecard match |
|---------|-------:|---------:|---------------------|-----------------|
| zustand | 0 | 1 (regex limitation — see note below) | ✓ Caution | ✓ 4 questions |
| caveman | 0 | 1 (same regex limitation) | ✓ Critical | ✓ 4 questions |
| archon-subset | 0 | 1 (same regex limitation) | ✓ Critical | ✓ 4 questions |

**Parity-warning note.** The warning `MD findings missing from HTML` fires because `validate-scanner-report.py --parity` matches HTML finding IDs via two regexes:
1. `exhibit-item-tag · F<N>` (verdict-exhibit tags)
2. `F<N> — <Severity>` (severity word immediately after F-ID + dash)

Our rendered HTML emits `F0 &mdash; <Title>` in finding-card `<h3>` (matching `GitHub-Scanner-zustand.html` reference exactly), not `F0 — Warning`. So the regex doesn't pick up finding IDs from `<h3>` titles in either the reference scan OR our output. Proof: running the parity check on the battle-tested reference scan `docs/GitHub-Scanner-zustand.{md,html}` produces the **identical** warning pattern. This is a known limitation of the parity check's regex, not a rendering defect. The MD-canonical rule enforcement (HTML findings ≠ MD findings produces an ERROR) works correctly — we triggered it twice during development via stale verdict-exhibit tag references, and both were fixed.

**Tests:**
```
tests/test_render_html.py: 117 passed
Full tests/ suite: 263 passed (was 146 before Step F; +117 HTML tests)
```

**Sonnet delegation record.** Three subagents ran in parallel (total ~365s wall time):
- Caveman fixture author (9 tool_uses, schema-clean on first pass, 10 scope-drift items documented)
- Archon-subset fixture author (7 tool_uses, schema-clean on first pass, monorepo data populated, C3 `auto_load_tier` constraint exercised for first time, 11 subset decisions logged)
- 13-partial HTML converter (61 tool_uses, validator clean on first pass, 4 scope-drift items documented — e.g. theme-class detection from symbol field)

---

## Issues discovered and fixed during verification

1. **Template emitted finding cards without finding IDs.** My section_02 partial wrote `<h3>{{ f.title }}</h3>`. Reference scan emits `<h3>F0 &mdash; {{ title }}</h3>`. Fix: prefix title with `{{ f.id }} &mdash; ` in the H3. After fix, all 10 of zustand's F-IDs (F0-F5, F8, F12, F16) appear in HTML.
2. **Caveman fixture had stale exhibit-tag reference.** `verdict_exhibits.groups[1].items[2].tag` was `"Distribution · F1+F2"` — but caveman has no F1 or F2 (its findings are F0, F5, F11, F14, F16, F-batch, F-advisory, F-amplify, F-deps). Fix: rename tag to `"Distribution"` without F-reference.
3. **Archon-subset fixture had 2 stale exhibit-tag references.** `"Supply chain · F2"` and `"Distribution · F8"` referenced findings dropped during subset scoping. Fix: strip `· F<N>` suffixes.

All three issues were caught by the parity check's MD-canonical-rule ERROR path. Post-fix, all 3 fixtures show clean parity.

---

## What this closes

- **Phase 7 Steps A-F complete.** MD renderer (Step B-E) and HTML renderer (Step F) both ship against V1.1 schema across 3 shape-distinct fixtures.
- **Dual-emit contract verified** — same form JSON produces structurally-consistent MD and HTML, validator-clean on each.
- **Cross-shape template robustness verified** — zustand (lib, Caution), caveman (installer, Critical with split-by-version), archon-subset (agentic platform monorepo, Critical with split-by-deployment) all render without template modifications.
- **C3 constraint tested in the wild** — archon-subset's F1 finding has `category: code/agent-rule-injection` which triggers the V1.1 C3 `auto_load_tier` requirement. Fixture validates clean.

## What this does NOT close

- **Step G** — C7 acceptance matrix using the real end-to-end JSON-first pipeline (tool-capture → compute → LLM → assembly → render). Step F's fixtures are manually authored from golden MDs, not produced by an upstream pipeline. Step G remains the gate for any "pipeline reliable" claim, and it REQUIRES board review.
- **Cross-shape coverage beyond 3 shapes.** We have 10 golden MDs in the repo but only 3 V1.1 fixtures. Remaining 7 shapes (agency-agents, archon-board-review, fd, gstack, hermes-agent, open-lovable, postiz-app) would add coverage but not structurally new cases relative to the 3 we chose.
- **Production HTML file extension conventions / output path policy** — no scanner workflow step has been updated yet to call `render-html.py`. Integration into Phase 7 of an actual scan is a later task (likely part of Step G end-to-end integration).

---

## References

- `../041826-renderer-alignment/CONSOLIDATION.md` — 7-step plan (A-G) with C1-C7 resolutions
- `./INDEX.md` — cross-reference across the 3 renderer board reviews + commit log
- `./STEP-E-verification.md` — prior mechanical-verification record for the MD renderer
- Session 5 status memory: `project_session5_status.md`
