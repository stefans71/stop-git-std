# Simple Report — concept brief

**Phase:** 7 of `docs/back-to-basics-plan.md` (calibration rebuild).
**Status:** concept draft authored 2026-05-01 from owner-supplied design intent.
**Branch:** `feat/simple-report` from `main` at `56430c0`.

---

## 1. Product positioning

The Simple Report is **the primary user-facing HTML output going forward.** The long-form HTML (`docs/GitHub-Repo-Scan-Template.html`) is being retired from the consumer-facing role and stays as the auditor view. Going forward, a scan produces two artifacts:

- **`GitHub-Scanner-<repo>.md`** — paste-ready Markdown for any LLM consumer ("should I install this?" prompt). Already validated by Phase 6 (5/5 cold-fork match).
- **`GitHub-Scanner-<repo>-simple.html`** — single-page polished visual overview. Product face. This brief.

The full HTML stays available for auditors who need full evidence + provenance, but is no longer the default output.

### Why a Simple Report

The full HTML carries 9 sections, ~30 finding cards, evidence appendices, PR tables, timelines, vitals grids — designed for forensic review. The two failure modes that drove session-8/9 work both came from over-stuffed presentation:

- **Consumer paralysis** — too much to read; users skim, miss the verdict, install anyway.
- **Over-cautious reading** — when every cell shows a color and every finding gets a card, "amber + amber + amber + amber + 6 warnings" reads as "scary," even when the calibrated verdict is Caution-not-Critical.

The Simple Report fixes both by delivering: **verdict + why + 4 plain-English answers + 3 top concerns + what-to-do** on one page.

---

## 2. Visual design — carry forward, drop, new

The existing scanner has a strong visual identity in `docs/scanner-design-system.css` (824 lines, dark forensic-console theme). The Simple Report must **read as the same product** — same typography, same palette, same feel — but use a tighter subset of the components.

### Carry forward (verbatim from design system)

| Element | Class / token | Rationale |
|---|---|---|
| Color palette | `--bg-void / --bg-surface / --bg-elevated / --border / --text-primary` + `--red-glow / --amber-glow / --green-glow / --cyan-glow` (with `-dim` and `-bg` variants) | Product identity — every Simple Report must read as a stop-git-std artifact. |
| Typography | `--font-display: 'Unbounded'` (headlines) + `--font-sans: 'Inter'` (body) + `--font-mono: 'JetBrains Mono'` (chrome/labels) | Same as full report. |
| Body chrome | `body::before` (noise + scanlines) + `body::after` (single-pass cyan scan-sweep animation) | Iconic project chrome; signals "this is a security scan." Keep. |
| Page wrapper | `.page` (max-width 960px, centered) | Consistent column width with full report. |
| Hero | `.hero` (slimmed) + `.hero-badge` (status dot) + `h1` slash-separated repo name + `.hero-caption` | Direct carry-forward. The repo-name `<span class="{verdict_color_class}">` keeps the color-coded identity gesture from the full report. |
| Verdict banner | `.verdict-banner.critical / .caution / .clean` + `.verdict-label` chip | Direct carry-forward. **Drop:** `data-dossier` vertical scan-ID bar (too verbose), `.verdict-split` two-audience layout (overkill for simple), `.verdict-exhibits` rolled panels (overkill). The banner becomes single-headline + 1-2 sentence editorial summary. |
| Action card | `.action-card.stop / .wait / .ok-action / .info-action` | Direct carry-forward. Used for "What should I do?" block. |
| Footer | `.footer` (border-top + small muted text) | Direct carry-forward. |

### Drop entirely (no equivalent in Simple Report)

- `.scorecard-grid` (4-column color cells) — replaced by sentence rows; user explicitly said "not cell colors"
- All `.collapsible-section` mechanics — Simple is single-page, nothing to collapse
- `.section-status`, `.section-subtitle`, `.section-action` — no auditor sections
- `.finding-card` collapsible details — replaced by simpler 3-card summary stack
- PR table, `.timeline`, `.vitals-grid` — no detail sections
- `.evidence-priority`, `.evidence-row`, `.evidence-pre`, `.evidence-classification`, `.evidence-group-label` — no evidence
- `.sub-finding`, `.inventory-summary`, `.inv-verdict` — no sub-findings or inventory
- `.scan-strip` (top dossier ribbon) — too dense for simple
- `.catalog-meta` (key-value table between hero and verdict) — replaced by inline meta-line in hero
- `.font-controls` floating widget — single-page report, doesn't need a/A/A toggle

### New patterns (Simple Report only)

| Pattern | Purpose | Implementation |
|---|---|---|
| **Scorecard sentence row** | Replaces 4-cell color grid with one row per question. Plain-English answer reads as a sentence. | 4 stacked rows: `<div class="sc-row sc-row--{color}"><span class="sc-glyph">{✓/⚠/✗}</span><div><div class="sc-question">Does anyone check the code?</div><div class="sc-answer">Partly — ruleset-based branch protection + CODEOWNERS, but Mitchell Hashimoto holds 85.9% of commits.</div></div></div>`. Glyph color comes from the cell color (red/amber/green). |
| **Top-3 findings stack** | Replaces full finding-card grid with 3 stripped-down cards. | Severity tag chip + title + 1-2 sentence what-this-means. No collapsible body, no evidence refs, no chips. Border-left accent in cell color (reuses existing `.finding-card.critical / .warning / .info / .ok` border-left convention). |
| **Verdict summary line** | The 1-2 sentence editorial under the verdict label. | Reuses `.verdict-banner` body — replaces the `<h2>` + `.verdict-split` with a slim `<h2>` (verdict word) + `<p>` (editorial caption). |

---

## 3. Page structure (single page, top to bottom)

```
┌─────────────────────────────────────────────────────────┐
│ HERO (slim)                                             │
│   ◉ stop-git-std · simple report                        │
│   ghostty-org/<span class="amber">ghostty</span>        │
│   Investigated 2026-04-20 · main @ dcc39dc · 51,181 ★   │
│   · MIT · Zig                                            │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ VERDICT BANNER                                          │
│   ● CAUTION                                             │
│   Install for personal use, pin SHA for production.     │
│   Ghostty is well-adopted, actively-maintained, with    │
│   modern branch protection. Two structural concerns     │
│   keep this scan at Caution: 85.9% commit concentration │
│   and no formal versioned releases.                     │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ SCORECARD                                               │
│   ⚠  Does anyone check the code?                        │
│      Partly — ruleset-based branch protection +         │
│      CODEOWNERS, but concentration risk.                │
│   ✓  Do they fix problems quickly?                      │
│      Yes — active project, zero open security issues,   │
│      responsive maintainer.                              │
│   ⚠  Do they tell you about problems?                   │
│      Partly — 5 GHSA advisories published, but no       │
│      SECURITY.md.                                        │
│   ⚠  Is it safe out of the box?                         │
│      Mostly — clean code-pattern grep, but no signed    │
│      releases.                                           │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ TOP CONCERNS                                            │
│   [WARNING] Solo-maintainer concentration               │
│     Mitchell Hashimoto holds 85.9% of commit share.     │
│     If they become unavailable, PR throughput and       │
│     security response time both degrade.                │
│   [WARNING] No formal versioned releases                │
│     Installers pull HEAD, not semver. Homebrew          │
│     resolves to the current default-branch commit.      │
│   [INFO]    No SECURITY.md                              │
│     Disclosure has happened (5 advisories), but the     │
│     reporting path is implicit — reporters must find    │
│     the GitHub Security tab.                            │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ WHAT SHOULD I DO?                                       │
│   ▸ Install with these conditions:                      │
│     Pin a specific commit SHA before deploying          │
│     anywhere production-adjacent. For personal use      │
│     via Homebrew, the rolling install is reasonable.    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ FOOTER                                                  │
│   stop-git-std · scanned 2026-04-20 ·                   │
│   github.com/ghostty-org/ghostty                        │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Data contract — what's mechanical vs LLM-synthesized

The Simple Report renders from the **same `form.json`** that produces the long-form HTML. No separate data pipeline. No re-authoring required for existing bundles.

| Display element | Source | Mechanical or LLM? |
|---|---|---|
| Repo owner / name / URL | `target.owner / .repo / .url` | mechanical |
| Short SHA | `phase_1_raw_capture.pre_flight.head_sha[:7]` | mechanical |
| Scan date | `_meta.scan_completed_at` (formatted `YYYY-MM-DD`) | mechanical |
| Stars / license / language | `phase_1_raw_capture.repo_metadata.stargazer_count / .license_spdx / .primary_language` | mechanical |
| Verdict level (Critical / Caution / Healthy) | `phase_4b_computed.verdict.level` | mechanical (already rule-driven by Phase 3) |
| Verdict 1-2 sentence why | `phase_5_prose_llm.editorial_caption.text` | **LLM (already in bundle)** |
| Q1–Q4 cell color (severity glyph) | `phase_4_structured_llm.scorecard_cells.<q>.color` | mechanical |
| Q1–Q4 plain-English answer | `phase_4_structured_llm.scorecard_cells.<q>.short_answer` | **LLM (already in bundle)** |
| Top 3 findings (selection) | `phase_4_structured_llm.findings.entries[]` sorted by severity (Critical > Warning > Info) then input order; take first 3 | mechanical |
| Finding title | `findings.entries[i].title` | **LLM (already in bundle)** |
| Finding 1-sent summary | `findings.entries[i].what_this_means` (truncated to first sentence if > 200 chars) | **LLM (already in bundle)** |
| "What should I do?" headline | derived from verdict level via static lookup table (Critical → "Don't install." / Caution → "Install with these conditions." / Healthy → "Safe to install.") | mechanical |
| "What should I do?" body | first 1-2 sentences of `phase_5_prose_llm.per_finding_prose.entries[0].body_paragraphs[0]` (the highest-severity finding's lead paragraph), trimmed | **LLM (existing field; mechanically selected)** |

**Key insight from data contract:** every LLM-synthesized field already exists in the bundles produced by the V2.4 / V2.5-preview pipeline. Phase 7 does not require any schema additions or bundle re-authoring — render-simple.py reads existing fields. This is consistent with the V2.5-preview pattern (deterministic rendering from authored bundle).

### What if a field is missing?

The renderer must be defensive on missing fields (some V1.1-era bundles in `.board-review-temp/step-g-execution/` lack `phase_5_prose_llm`). Fallback policy:

| Missing field | Fallback |
|---|---|
| `editorial_caption.text` | Synthesize from verdict + top finding title: `"<Repo> is at <Caution/Critical>. <Top finding title>."` |
| `scorecard_cells.<q>.short_answer` | Use `<q>.headline` if present; else `"<Color>"` (Yes/Partly/No mapped from green/amber/red) |
| `findings.entries[i].what_this_means` | Use first 200 chars of `findings.entries[i].body` if present; else just title |
| `per_finding_prose.entries[0].body_paragraphs[0]` | Use static template based on verdict level only |

Fallback paths are tested in `tests/test_render_simple.py` against a synthetic minimal bundle.

---

## 5. Top-3 selection rule (mechanical)

```python
SEVERITY_ORDER = {"Critical": 0, "Warning": 1, "Info": 2, "OK": 3}

def pick_top_3(findings):
    entries = findings.get("entries", [])
    sorted_ = sorted(entries, key=lambda f: (SEVERITY_ORDER.get(f.get("severity"), 99),
                                             entries.index(f)))
    return sorted_[:3]
```

**Tie-break:** input order (which the LLM authored as F0, F1, F2... = author's intended priority).

**Edge case:** if a scan has fewer than 3 findings (e.g., a Clean repo), the section renders only the findings present; if zero findings, the section is omitted entirely and the action block becomes a clean "Safe to install" green card.

---

## 6. MD variant

The Simple Report MD output is a tighter version of the existing scanner MD, structured to match the HTML layout exactly so they read in parallel:

```markdown
# ghostty-org/ghostty — Simple Report

**Verdict: ⚠ Caution.** Install for personal use, pin SHA for production.

Ghostty is a well-adopted, actively-maintained Zig terminal emulator with
modern ruleset-based branch protection and a working disclosure channel
(5 GHSA advisories). Two structural concerns keep this scan at Caution:
85.9% commit concentration and no formal versioned releases.

**Scanned:** 2026-04-20 · main @ dcc39dc · 51,181 stars · MIT · Zig

---

## Trust scorecard

- ⚠ **Does anyone check the code?** Partly — ruleset-based branch protection + CODEOWNERS, but concentration risk.
- ✓ **Do they fix problems quickly?** Yes — active project, zero open security issues, responsive maintainer.
- ⚠ **Do they tell you about problems?** Partly — 5 GHSA advisories published, but no SECURITY.md.
- ⚠ **Is it safe out of the box?** Mostly — clean code-pattern grep, but no signed releases.

## Top concerns

1. **[Warning] Solo-maintainer concentration.** Mitchell Hashimoto holds 85.9% of commit share. If they become unavailable, PR throughput and security response time both degrade.
2. **[Warning] No formal versioned releases.** Installers pull HEAD, not semver. Homebrew resolves to the current default-branch commit.
3. **[Info] No SECURITY.md.** Disclosure has happened (5 advisories), but the reporting path is implicit — reporters must find the GitHub Security tab.

## What should I do?

**Install with these conditions:** pin a specific commit SHA before deploying anywhere production-adjacent. For personal use via Homebrew, the rolling install is reasonable.

---

*stop-git-std · scanned 2026-04-20 · [github.com/ghostty-org/ghostty](https://github.com/ghostty-org/ghostty)*
```

The Simple MD is **separate from** the long-form MD that V2.4/V2.5-preview already produces. Both will be available; the long-form MD remains the LLM-consumer paste target (already validated by Phase 6), the Simple MD is for human-readable terminal/email contexts.

---

## 7. Visual & inline-CSS strategy

**Self-contained HTML — except for typography CDN.** The Simple Report ships with all CSS inlined in a `<style>` block. No external stylesheet, no JS, no external image references. Typography (Unbounded/Inter/JetBrains Mono) loads from Google Fonts CDN — same pattern as `docs/GitHub-Repo-Scan-Template.html` (lines 33-36, with CSP meta restricting font-src to `fonts.gstatic.com`). System fallbacks (`'Inter'` → system sans) keep the report readable if fonts fail to load. **Open question for owner:** if strict "no external deps" is required, the alternative is base64-embedded font subsets (~150-400KB inline per render); ship-with-CDN is the recommended default unless the owner specifies otherwise.

**CSS budget target:** ≤ 250 lines (vs 824 lines in the full design system). Achieved by:
- Dropping all auditor-only patterns (collapsibles, evidence, vitals, timeline, PR table, etc).
- Single severity-color pattern reused for hero badge dot + scorecard glyph + finding card border + action card.
- No animations except the iconic `body::after` cyan scan-sweep (single-pass, 3s, then disappears) and verdict-banner pulse — both define product identity.
- Inline `<style>` block in the template, not an external file. Renderer copies the canonical CSS subset directly into the rendered HTML.

The CSS subset lives at `docs/templates-simple/simple-report.css` (source of truth) and is read + inlined by `render-simple.py` at build time. This way the source CSS stays editable / lintable / diffable while the output is self-contained.

---

## 8. Renderer + template files

```
docs/render-simple.py                      # CLI: read form.json → write .html + .md
docs/templates-simple/
  simple-report.html.j2                    # Jinja2 template for HTML
  simple-report.md.j2                      # Jinja2 template for MD
  simple-report.css                        # Canonical CSS subset (inlined at build)
tests/test_render_simple.py                # 3 representative-bundle tests + minimal-bundle fallback test
```

### CLI

```bash
python3 docs/render-simple.py form.json --out-html GitHub-Scanner-<repo>-simple.html --out-md GitHub-Scanner-<repo>-simple.md
```

Flags:
- `--out-html PATH` (required) — path to write rendered HTML.
- `--out-md PATH` (optional; default: derive `.md` sibling of `--out-html`) — path to write rendered MD.
- `--no-md` — skip MD output if HTML-only is wanted.

### Wizard integration (applied 2026-05-01 in Phase 7 close)

CLAUDE.md changes landed alongside the renderer per owner directive 2026-05-01:

- **Q1 output mode** — A: long-form MD + Simple Report HTML (default, user-facing); B: + long-form HTML (auditor view); C: MD only.
- **Q3a rendering pipeline** — V2.5-preview is now the **default + recommended** pipeline (was V2.4). V2.4 marked as **legacy — does not produce Simple Report**. V2.4 cannot drive `render-simple.py` (no `form.json` produced).
- **Post-scan options** (CLAUDE.md "After the scan completes") — option 1 "View the report" now opens the **Simple Report HTML**. Option 2 reframed as "detailed walkthrough" — read the long-form MD and walk the user through findings + safe-install conditions.

The Operator Guide §4 + §8 Phase 4 contract was updated in lockstep:
- Phase 4a: render-md.py → long-form MD (canonical, REQUIRED).
- Phase 4b: render-simple.py → Simple Report HTML + MD (primary user-facing, REQUIRED).
- Phase 4c: render-html.py → long-form HTML (auditor view, OPTIONAL).
- Phase 4d: re-run determinism record (lightweight MD-only, OPTIONAL).
- Validator gates Phase 4a + 4b; Phase 4c gates `--report` only if produced.

---

## 9. Test strategy

`tests/test_render_simple.py` covers:

| Test | Coverage |
|---|---|
| `test_renders_clean_against_ghostty_bundle` | Caution verdict path; LLM fields all present; should produce HTML + MD with all 4 scorecard sentences and 3 top findings. |
| `test_renders_clean_against_baileys_bundle` | Critical verdict path; 8 findings (top 3 must include F0 Critical first); action card must be `.stop` red. |
| `test_renders_clean_against_skills_bundle` | Caution verdict with V13-3 `missing_qualitative_context` override (entry 27); validates that the Simple Report does not "shout Critical" on a calibrated-Caution scan. |
| `test_minimal_bundle_fallbacks` | Synthetic bundle missing `phase_5_prose_llm` and `findings.entries[i].what_this_means` — fallback policy should keep all 5 sections rendering with synthesized content. |
| `test_html_is_self_contained` | Parse HTML + assert no external `<link>`, `<script>`, or `<img src="http*">`. CSS is inline. |
| `test_md_renders_in_parallel` | HTML + MD share the same scorecard sentences + finding titles + action block content (parity-style check). |

No `--report` validator gate yet — Simple Report is a new artifact type and the existing validator targets the long-form. Phase 7 ships its own minimal validator if needed; otherwise relies on the test suite for correctness.

---

## 10. What this brief deliberately defers (post-Phase-7 follow-up backlog)

The following are out of scope for Phase 7 (intentionally — to keep the phase landable). They become the post-Phase-7 follow-up backlog:

- **V2.4-bundle → form.json adapter.** V2.4 (legacy) does not produce a `form.json` and therefore cannot drive `render-simple.py`. Adding an adapter would let legacy V2.4 scans (catalog entries 1-11) generate Simple Reports retroactively. Trade-off: adapter logic must invent or hand-author the LLM-synthesized fields (editorial_caption, scorecard short_answers, finding what_this_means, action_hint) that V2.5-preview emits natively but V2.4 prose-renders elsewhere. Not Phase 7 scope; queued.
- **Gate 6.3 backlog resolution** (7 cells × 6 V1.2 entries) — `phase_3` ↔ `phase_4` divergences from Phase 5 calibration v2 rerender. Resolution choice: (b) add `override_reason` to existing Phase 4 cells, or (c) soften calibration v2 Q3 rules. Not (a) — that would shift consumer-facing semantics that Phase 6 + 7 just validated as correct.
- **Q3 FALLBACK regression** on 5 entries (ghostty, kamal, wezterm, freerouting, WLED) — `phase_3` advisory only; rendered MD + Simple HTML unaffected (Phase 6 finding). Address alongside gate 6.3 backlog.
- **Full-sentence scorecard short_answers.** Current bundles produce fragmentary forms ("Partly — concentration risk"). The question-above + answer-below layout makes them readable as pairs; rewrite to full sentences ("Code reviews happen, but most commits come from one person") would be a 12-bundle re-author and is cosmetic polish, not blocking.
- **Inline customization** (custom branding for org-internal scans) — would need separate config layer.
- **Theme switcher (light mode)** — the dark forensic-console look is the product identity; a light theme would be an explicit alt-product decision.
- **Print stylesheet** — readers print rarely; defer until requested.
- **Embed-in-README badge** — would need separate backend.

---

## 11. Acceptance criteria

Phase 7 is complete when:

- [ ] `docs/render-simple.py` + `docs/templates-simple/{simple-report.html.j2, simple-report.md.j2, simple-report.css}` all exist.
- [ ] `tests/test_render_simple.py` passes (6 tests as listed in §9).
- [ ] Renders cleanly against ghostty (Caution), Baileys (Critical), skills (Caution-with-override) bundles — outputs go to `docs/scans/catalog/` alongside long-form.
- [ ] Self-contained HTML — no external fetches, opens correctly with `file://` protocol.
- [ ] Visual review by owner — "this looks like the product."
- [ ] Wizard Q1 amended in CLAUDE.md to include option D Simple Report.
- [ ] Owner sign-off on merge.

---

## 12. Cross-references

- Source design system: `docs/scanner-design-system.css`
- Template DOM contract: `docs/GitHub-Repo-Scan-Template.html` (the auditor view, retained)
- Phase 6 verification: `docs/calibration-rebuild-md-verification.md` (validates that calibrated MD reads correctly to consumers — Simple Report inherits that calibration)
- Plan: `docs/back-to-basics-plan.md` §Phase 7
