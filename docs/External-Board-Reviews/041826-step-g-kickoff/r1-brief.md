# Board Review R1 (Blind) — Step G Kickoff / U-1 Documentation Integration

**Date:** 2026-04-18
**Reviewing:** Proposed approach (NO code yet) for integrating `render-md.py` + `render-html.py` into the operator-facing scan workflow
**Round:** R1 Blind — each agent drafts independently
**Rounds planned:** Blind → Consolidation → Confirmation (3-round SOP; narrower scope than Step F)
**Context:** Step F ships the renderer. Step G is the C7 acceptance matrix. Before Step G runs, the operator workflow needs documented integration so operators (and LLMs walking the guide) know how to invoke the renderer.

**STATELESS.** Read fresh. This is a fix-artifact-first governance review: owner proposes approach + draft snippets BEFORE applying. Board assesses approach, blind spots, and scope.

---

## 1. Project background (self-contained)

**stop-git-std** is an LLM-driven GitHub repo security auditor. Board-approved architecture:
- 8/8/4 classification (automatable / structured LLM / prose LLM)
- 9-phase pipeline
- MD canonical, HTML derived, validator as gate
- Facts/inference/synthesis separation

Phase 7 renderer plan A→G: **Steps A-F done** (schema V1.1, Jinja2 renderers for both MD and HTML, 3 V1.1 fixtures, 263 tests passing, validator clean). **Step G is next** — C7 acceptance matrix running live scans through the JSON-first pipeline.

Just-completed Step F board review: `docs/External-Board-Reviews/041826-step-f-alignment-validation/` (4-round, SIGN OFF). Key outputs to U-1: "next-commit queue before Step G runs" containing **U-1 doc integration, U-3/FX-4 fixture provenance, U-5/PD3 bundle validator**.

This review covers U-1 only. U-3/FX-4 and U-5/PD3 will be separate reviews.

---

## 2. Current state of the operator-facing docs

Two parallel sets of docs exist:

### 2.1 Repo-level (canonical, in-repo)

- **`/root/tinkering/stop-git-std/CLAUDE.md`** (103 lines) — repo operator instructions. Currently says "Phase 4a produces MD first. Phase 4b derives HTML from it" and points operators at `docs/GitHub-Repo-Scan-Template.html` + `docs/scanner-design-system.css` (copy verbatim). NO mention of `render-md.py` or `render-html.py`.
- **`/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md`** (569 lines) — V0.1 operator guide. §8.5 describes Phase 4a as "LLM reads the bundle, reads 1-2 shape-matched reference scans, and produces the canonical MD report." §8.6 describes Phase 4b as "structural derivation from the MD" with CSS copy-verbatim. NO mention of the renderer.
- **`/root/tinkering/stop-git-std/docs/Scan-Readme.md`** (137 lines) — human-readable wizard. Same old workflow.
- **`/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md`** (1508 lines) — the V2.4 scanner prompt. Describes what the LLM investigates (Steps 1-8 + A/B/C). NOT about rendering.

### 2.2 Package-level (distributable, github-scan-package-V2/)

A V2.4 release snapshot dated ~2026-04-17 (predates Step F). **Precise drift audit (repo vs package, 2026-04-18):**

| File | Drift (diff lines) | Status |
|---|---:|---|
| `CLAUDE.md` | not compared line-by-line, but diverges in emphasis (package version says "V2.4 Package", is shipped to users) | Divergent by design |
| `SCANNER-OPERATOR-GUIDE.md` | **0** | **Currently identical** — any repo edit creates drift |
| `Scan-Readme.md` | 102 | Drifted |
| `validate-scanner-report.py` | 16 | **Drifted — missing FX-3 Pattern 3 + FX-3b comment-strip removal from Step F R3 commit `ce698d4`** |
| `GitHub-Repo-Scan-Template.html` | 10 | Minor drift |
| `scanner-design-system.css` | 0 | Identical |
| `repo-deep-dive-prompt.md` | 24 | Minor drift |
| `scanner-catalog.md` | (different — package has only 6 entries, repo has 10) | Drifted |
| No renderer files in package | — | Package is V2.4 — pre-Phase-7 |

**Key observation:** `SCANNER-OPERATOR-GUIDE.md` is currently byte-identical between repo and package. Any U-1 edit to the repo version immediately creates a drift. This means U-1's scope decision for Q4 has a hidden sub-question: **do we update both in lockstep (maintaining parity), or accept the drift as the point where V2.4 package diverges from V2.5-preview repo?**

### 2.3 What this means

**Two eras coexist in the repo:**
- **V2.4 workflow (existing, proven on 10 catalog scans):** LLM captures data → LLM writes `findings-bundle.md` → LLM authors `GitHub-Scanner-<repo>.md` + `.html` directly from template → validator gates.
- **JSON-first workflow (Step F shipped, Step G unvalidated):** LLM captures data → LLM produces `form.json` (V1.1 schema) → `render-md.py` + `render-html.py` produce MD + HTML → validator gates.

The JSON-first workflow has been validated only against **back-authored fixtures** (zustand, caveman, archon-subset from golden MDs). **No live scan has run through it end-to-end.** That's literally what Step G is for.

---

## 3. Owner proposal for U-1 scope

### 3.1 Scope decision — what U-1 DOES

Update **repo-level docs only** in this commit:
- `CLAUDE.md`
- `docs/SCANNER-OPERATOR-GUIDE.md`
- `docs/Scan-Readme.md`

To do the following:

1. **Keep V2.4 (Path A) as the primary documented workflow.** Rationale: 10 completed scans prove it works; Step G hasn't yet validated Path B end-to-end.
2. **Document JSON-first (Path B) as experimental, for operators doing Step G.** Include the renderer commands, the V1.1 schema location, fixture examples, and a "pre-Step-G" disclaimer.
3. **Add a "which path" decision section** so operators don't accidentally mix paths.
4. **Preserve all invariants** (MD canonical, facts/inference/synthesis, validator gate).

### 3.2 Scope decision — what U-1 does NOT do

- **Do NOT update the V2.4 prompt** (`docs/repo-deep-dive-prompt.md`, 1508 lines). It describes what to investigate, not how to render. Rendering changes don't affect investigation.
- **Do NOT update `github-scan-package-V2/`.** It's a V2.4 distributable snapshot. After Step G validates Path B, a separate future commit creates a V2.5 package with JSON-first as primary. Also: the package validator is out of sync with the repo validator (missing FX-3 + FX-3b from Step F) — sync is a separate concern for post-Step-G V2.5 package work.
- **Do NOT flip Path B to primary yet.** The board's "pipeline reliable" claim is gated on Step G. Documenting Path B as primary before Step G validates it would be premature.
- **Do NOT add new features to the renderer.** U-1 is documentation only. No code changes to render-md.py / render-html.py / templates/.

### 3.3 Proposed draft — CLAUDE.md changes

**BEFORE** (CLAUDE.md line 39-47, current Path A execution block):
```markdown
Then **execute the scan** following `docs/SCANNER-OPERATOR-GUIDE.md` (6-phase workflow).

### Path A execution
Follow phases 1-6 yourself. Read the Operator Guide for details on each phase. Key files:
- `docs/SCANNER-OPERATOR-GUIDE.md` — your process document
- `docs/repo-deep-dive-prompt.md` — what to investigate (Steps 1-8 + A/B/C)
- `docs/GitHub-Repo-Scan-Template.html` — HTML template with placeholders
- `docs/scanner-design-system.css` — **MANDATORY** CSS (816 lines, copy verbatim into HTML `<style>` block — do NOT truncate or rewrite)
- `docs/validate-scanner-report.py` — validator gate (`--report` mode, must exit 0)
```

**AFTER:**
```markdown
Then **execute the scan**. There are two documented paths:

#### Path V2.4 (recommended, proven on 10 scans)
LLM-authored MD and HTML directly from the findings bundle. Follow `docs/SCANNER-OPERATOR-GUIDE.md` 6-phase workflow. Key files:
- `docs/SCANNER-OPERATOR-GUIDE.md` — process document
- `docs/repo-deep-dive-prompt.md` — what to investigate (Steps 1-8 + A/B/C)
- `docs/GitHub-Repo-Scan-Template.html` — HTML template with placeholders
- `docs/scanner-design-system.css` — **MANDATORY** CSS (824 lines, copy verbatim into HTML `<style>` block — do NOT truncate or rewrite)
- `docs/validate-scanner-report.py --report` — validator gate (exit 0 required)

#### Path V2.5-preview (JSON-first pipeline, experimental — Step G validation in progress)
LLM authors `form.json` (V1.1 schema) → deterministic renderer produces MD + HTML. This is the future-direction pipeline but has only been validated on back-authored fixtures; live scans remain a Step G open item.

Only use this path if you are explicitly running Step G of the renderer plan. Otherwise use Path V2.4.

Key files:
- `docs/scan-schema.json` — V1.1 schema (investigation form structure)
- `tests/fixtures/{zustand,caveman,archon-subset}-form.json` — example form.jsons to mirror
- `docs/render-md.py` — MD renderer: `python3 docs/render-md.py form.json --out GitHub-Scanner-<repo>.md`
- `docs/render-html.py` — HTML renderer: `python3 docs/render-html.py form.json --out GitHub-Scanner-<repo>.html`
- `docs/validate-scanner-report.py --report` — validator gate (exit 0 required on both MD + HTML)
- `docs/validate-scanner-report.py --parity` — MD/HTML parity (zero errors + zero warnings required for Step G)
```

**BEFORE** (CLAUDE.md Key rules, line 68):
```markdown
- **MD is canonical.** Phase 4a produces MD first. Phase 4b derives HTML from it. HTML may not add findings absent from MD.
```

**AFTER:**
```markdown
- **MD is canonical.** In Path V2.4, Phase 4a produces MD, Phase 4b derives HTML. In Path V2.5-preview, both are rendered from the same `form.json` (MD-canonical enforced by the shared form contract). In either path, HTML may not add findings absent from MD.
```

### 3.4 Proposed draft — SCANNER-OPERATOR-GUIDE.md changes

Add a new §8.8 at end of Phase 4 section:
```markdown
### 8.8 Phase 4 — Path V2.5-preview (JSON-first, experimental)

**Status:** The deterministic renderer shipped in commit `402f933` + `ce698d4`. Validated against back-authored fixtures (zustand, caveman, archon-subset). **End-to-end validation on a live scan is open as Step G of the renderer plan (see `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`).** Use this path only if you are Step G's operator.

**Workflow:**
1. Phase 1-3 unchanged (prep, gather, bundle).
2. Phase 4 (new): author `form.json` conforming to `docs/scan-schema.json` V1.1. Reference `tests/fixtures/zustand-form.json` for shape. The form represents the same data that in V2.4 goes into the bundle + MD, but in machine-readable structured form.
3. Render:
   ```bash
   python3 docs/render-md.py form.json --out docs/GitHub-Scanner-<repo>.md
   python3 docs/render-html.py form.json --out docs/GitHub-Scanner-<repo>.html
   ```
4. Phase 5 validate: `--report` on each, `--parity` on the pair.

**Fixture provenance (planned next commit):** V2.5-preview fixtures will be tagged in `tests/fixtures/provenance.json` to distinguish back-authored from live-pipeline-produced forms. Step G scans are the first live-pipeline forms.

**Constraints preserved from V2.4:**
- MD-canonical rule (HTML may not add findings absent from MD) — enforced by shared form.
- Facts/inference/synthesis separation — enforced by schema phase boundaries.
- Validator is the gate.
- `head-sha.txt` written as first durable artifact — same as V2.4.

**Known limitations pre-Step-G:**
- Only 3 shapes have V1.1 fixtures (JS library, curl-pipe installer, agentic platform monorepo). Other shapes (CLI binary, Claude Code skills) have not been exercised.
- The JSON-first pipeline has not produced a scan from live `gh api` data — only back-authored reconstructions of goldens.
- Phases 4-6 automation (structured LLM, prose LLM, assembly) is not built; Step G uses LLM-in-the-loop for those phases.

### 3.5 Proposed draft — Scan-Readme.md

Minor: add one line in the files table pointing to the V2.5-preview renderers and a "which path" sentence. Full snippet deferred to post-board approval so the board can direct the format.

---

## 4. Blind spots the board should address

### Q1: Is "additive" the right strategy, or should we commit to Path B before Step G proves it?

Owner proposal: additive (Path A primary, Path B experimental). Alternative: unify on Path B now to force Step G to happen quickly.

### Q2: Does the V2.4 prompt (`repo-deep-dive-prompt.md`) need updating?

**Revised framing** (owner correction after reviewing prompt structure):

The prompt has TWO parts:
- **Lines 1-1090: Investigation instructions** — what `gh api` calls to run, what to grep for, how to interpret results. This is what the LLM/operator executes.
- **Lines 1106-1490: Output format specification** — the exact MD file structure (`## 01 · What should I do?`, `## 02 · What we found`, finding card format, verdict format, evidence appendix structure, etc.).

**The second half IS the output contract.** The renderer's templates at `docs/templates/partials/*.md.j2` are a mechanical implementation of this specification. Both Path A (LLM authors MD directly) and Path B (render from form.json) must produce prompt-compliant output.

This reframes the question: the investigation half doesn't need changes (it's about what to check, not how to render). The output-format half should note that "this specification is also realized via docs/scan-schema.json V1.1 + render-md.py/render-html.py for the JSON-first pipeline" — a single cross-reference, not a rewrite.

Board: confirm owner proposal of minimal prompt update (one cross-reference at the top of the output-format section, no rewrite), OR argue for zero prompt change (the prompt is investigation-only and the rendering contract lives entirely in the schema + templates).

### Q3: How do we handle the 10 existing catalog scans?

Owner proposal: leave them alone — they're completed V2.4 artifacts. The catalog (`docs/scanner-catalog.md`) should document that catalog entries 1-10 are V2.4 outputs; Step G adds the first V2.5-preview entries.

### Q4: Package (github-scan-package-V2/) drift

Three sub-questions:

- **Q4.1 — Operator guide parity:** `docs/SCANNER-OPERATOR-GUIDE.md` and `github-scan-package-V2/SCANNER-OPERATOR-GUIDE.md` are byte-identical today. Owner proposal updates only the repo version, creating drift. Alternative: update both in lockstep. Board: confirm accept-drift as V2.4-to-V2.5 boundary marker, OR require lockstep.
- **Q4.2 — Validator sync:** Package validator missing FX-3 + FX-3b. Users of the V2.4 package running its validator against V2.4-shape HTML won't hit the bugs (they're V2.5 renderer-specific). But the package's validator still has the comment-strip bug (FX-3b) that eats shell-glob-containing evidence — this is a latent bug in V2.4 too, whether or not U-1 ships. Owner proposal: leave as-is for U-1; fix in a separate "package maintenance" commit. Board: is this the right call, or should FX-3b at least sync to package ASAP since it's a real bug in V2.4-shape scans (e.g., caveman)?
- **Q4.3 — Full package refresh:** Post-Step G, the package likely gets a full V2.5 refresh with renderer + fixtures + schema. Board: confirm this is a future separate work item, not conflated with U-1.

### Q5: Is there a safety concern with Path B being documented pre-validation?

Operators who read the guide might run Path B prematurely. Owner proposal relies on the "experimental — Step G validation in progress" wording. Board: is that strong enough, or should Path B require a specific flag/env var to enable?

### Q6: What's the rollback plan if Step G fails?

Owner proposal: if Step G reveals schema or renderer defects, the V1.1 schema gets revised and fixtures re-authored. Path B docs update to reflect V1.2 or whatever. Path A continues unchanged throughout. Board: confirm or propose stronger rollback.

### Q7: Any blind spots in the proposed draft?

This is the open-ended catch-all. Specifically: does the proposed CLAUDE.md change obscure the key rules? Does the operator guide §8.8 have enough detail for an operator to actually produce form.json from scratch (spoiler: it doesn't — the prompt doesn't describe form.json authoring). What's missing?

---

## 5. What R1 must produce

### Verdict
SIGN OFF | SIGN OFF WITH DISSENTS | BLOCK (on the approach, not on code — no code has been applied yet).

### Response to Q1-Q7
Direct answers. Cite files/lines where relevant.

### Additional blind spots
Things the brief didn't surface but you see. Especially welcome from the Skeptic.

### FIX NOW / DEFER / INFO items
Applied to the proposed approach, not applied code. FIX NOW on approach = "don't take this approach without addressing X first."

Under 2000 words. Narrower scope than Step F.

---

## 6. Files to READ

- `/root/tinkering/stop-git-std/CLAUDE.md` (full — 103 lines)
- `/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md` (§8 in particular, lines 310-420)
- `/root/tinkering/stop-git-std/docs/Scan-Readme.md` (full — 137 lines, quick read)
- `/root/tinkering/stop-git-std/docs/scan-schema.json` (lines 1-100 for V1.1 intro)
- `/root/tinkering/stop-git-std/tests/fixtures/zustand-form.json` (for reference on what form.json looks like)
- `/root/tinkering/stop-git-std/docs/render-md.py` (117 lines, shim)
- `/root/tinkering/stop-git-std/docs/render-html.py` (135 lines, shim)
- `/root/tinkering/stop-git-std/github-scan-package-V2/CLAUDE.md` (for Q4 — compare to repo CLAUDE.md)
- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md` (for the "next-commit queue" that puts U-1 before Step G)

---

## 7. Ground rules

- Under 2000 words.
- Cite file paths + line numbers.
- This is approach review, NOT code review — no fix artifacts for committed code needed. Fix artifacts apply to the PROPOSED draft snippets (Section 3.3/3.4).
- If you disagree with owner's scope decision (Q4 package, Q2 prompt update), say so with rationale.
- Pragmatist: your risk is hand-waving Path B's incompleteness. Be precise about what's validated and what isn't.
- Systems Thinker: the coexistence of two paths is architecturally ugly. Say whether "additive" is the right call or unification is better.
- Skeptic: the failure mode is "operator runs Path B on a repo that hasn't been fixtured, hits a schema edge case, produces invalid JSON, can't tell." Find more failure modes.
