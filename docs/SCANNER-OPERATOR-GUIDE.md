# GitHub Scanner Operator Guide

**Status:** V0.2 · V2.4 companion · 2026-04-17 (AXIOM audit fixes applied, board reviewed)
**Audience:** Human operators + LLM orchestrators running the scanner end-to-end

> **Standalone package note:** When running from the standalone `github-scan-package-V2/` folder, all files are in the same directory. File paths in this guide that begin with `docs/` should be read without the `docs/` prefix (e.g., `docs/validate-scanner-report.py` → `validate-scanner-report.py`). The `CLAUDE.md` entry point already uses flat paths.

---

## 1. Purpose

The V2.4 prompt (`repo-deep-dive-prompt.md`), template (`GitHub-Repo-Scan-Template.html`), and validator (`validate-scanner-report.py`) describe **what** a scan should contain and how its output should look. This guide captures **how to run one end-to-end** — the workflow that's been emergent in practice but is not written down anywhere else.

Without this guide, an operator who has the prompt + template + validator can reproduce *something* V2.4-shaped, but will miss:
- The two-phase evidence/render split
- The `/tmp/scan-<repo>/` working directory convention
- The `findings-bundle.md` intermediate artifact
- The validator iteration loop and its common false-positives
- The fact-vs-inference-vs-synthesis hygiene that keeps scans honest
- How to use prior scans as structural references without plagiarising their content
- The portable handoff packet — the runtime-agnostic artifact set that lets any frontier LLM execute the scan

These all affect **accuracy and reproducibility**, not just ergonomics.

---

## 2. When to use this guide

- You are running a V2.4 scan against a GitHub repo.
- You are writing automation (shell script, CI job, or YAML workflow) that wraps the scanner.
- You are an LLM orchestrator (any runtime) and want the end-to-end workflow, not just the prompt.

---

## 3. Prerequisites

| Tool / condition | Why | Portable? |
|---|---|---|
| `gh` CLI, authenticated | All repo metadata + API calls | yes |
| `gh` scopes | Minimum `repo` read; `admin:org` + `admin:repo_hook` recommended for full governance / Dependabot coverage — absence is reduced coverage, not a broken scan | yes |
| Host | Guide assumes `github.com`. `GH_HOST=<enterprise-host>` works for most Phase 2 gh calls; rulesets API availability and organization audit endpoints may differ — verify manually on GHE. First non-github.com scan should feed back into this guide. | yes (with caveats) |
| `tar` + standard POSIX | Extract repo tarball locally | yes |
| `python3` 3.8+ | Run the validator | yes |
| `jq` | Parse gh api JSON (recommended) | yes |
| `npm` / `pip` / `cargo` (optional) | Step 8 installed-artifact verification — needed only when the scanned repo distributes via npm/PyPI/crates.io. If absent, note "artifact verification: skipped (tool not available)" in Coverage. Not required for core scan. | yes |
| `gitleaks` (optional) | Secrets-in-history scanning (Cap-4). If installed, run `gitleaks detect --source "$SCAN_DIR" -v --redact`. If absent, note "secrets-in-history: not scanned" in Coverage. | yes |
| `curl` | OSSF Scorecard API + osv.dev fallback (added V2.4). Usually pre-installed. | yes |
| A markdown-capable editor | Write `findings-bundle.md` | yes |
| `/tmp` writable with ≥500 MB free | Working directory for tarball + bundle | yes |
| An LLM runtime with a context window large enough to hold the handoff packet (see §8.3) | Phase 2–4 synthesis | yes (any frontier model) |
| `methodology-used` catalog flag | Every scan entry records `path-a` or `path-b` (see §8.1/§8.2) | yes |

The scanner is **LLM-driven**. It is not a static analyzer. All synthesis happens in the LLM's context; all shell commands are helpers that populate that context.

---

## 4. Six-phase workflow

```
┌────────────────────────────────────────────────────────────────────┐
│  PHASE 1   prep            mkdir, capture HEAD SHA (first durable  │
│                            artifact), download tarball, extract    │
├────────────────────────────────────────────────────────────────────┤
│  PHASE 2   gather          gh api + local grep per V2.4 Steps      │
│                            1–8 + A/B/C                              │
├────────────────────────────────────────────────────────────────────┤
│  PHASE 3   bundle          synthesise evidence into                │
│                            /tmp/scan-<repo>/findings-bundle.md     │
├────────────────────────────────────────────────────────────────────┤
│  PHASE 4a  MD render       bundle → canonical MD report            │
│  PHASE 4b  HTML render     MD → HTML (structurally derived only)   │
│  PHASE 4c  re-run record   optional lightweight MD-only output     │
│                            documenting a re-scan with minor drift  │
├────────────────────────────────────────────────────────────────────┤
│  PHASE 5   validate        --report mode loop until exit 0 on      │
│                            BOTH MD and HTML                         │
├────────────────────────────────────────────────────────────────────┤
│  PHASE 6a  catalog         required: update docs/scanner-catalog.md│
│  PHASE 6b  memory          optional: operator-local memory update  │
└────────────────────────────────────────────────────────────────────┘
```

Each phase is described below with concrete commands, decision points, and failure modes.

### 4.1 Pre-flight checks

Run these **before Phase 1**. Any failure aborts the scan with a concrete message; don't proceed with partial setup.

```bash
# 1. gh is authenticated (exit 0 + shows a user)
gh auth status || { echo "STOP: gh CLI is not authenticated. Run 'gh auth login'."; exit 1; }

# 2. gh token has the required scopes
#    Minimum: repo (read)
#    Recommended: admin:org + admin:repo_hook for full governance + Dependabot coverage
#    Absence of the recommended scopes is "reduced coverage," not "scan broken."
gh auth status 2>&1 | grep -E "Token scopes" || echo "NOTE: scope line not found; verify manually."

# 3. /tmp is writable with at least 500 MB free
df -P /tmp | awk 'NR==2 { if ($4 < 512000) { print "STOP: /tmp has <500 MB free."; exit 1 } }'
test -w /tmp || { echo "STOP: /tmp not writable."; exit 1; }

# 4. python3 >= 3.8
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' \
  || { echo "STOP: python3 3.8+ required."; exit 1; }

# 5. Target repo exists and this token can see it
gh api "repos/<owner>/<repo>" --silent \
  || { echo "STOP: cannot reach repos/<owner>/<repo> with current token."; exit 1; }
```

Record any scope gap as part of Phase 2's capture-plan — it downgrades specific findings to "unknown" rather than "absent." See §6.3.

---

## 5. Phase 1 — Prep

**Goal:** working directory exists, HEAD SHA is captured as the first durable artifact, tarball is extracted.

```bash
# Working directory convention — /tmp is intentional, not a bug
mkdir -p /tmp/scan-<repo-short-name>
cd /tmp/scan-<repo-short-name>

# Capture HEAD on the repo's default branch. Record the result;
# the dossier's commit-pin comes from here.
# head-sha.txt is the FIRST DURABLE ARTIFACT — write it before any other gh api call.
# If the scan is interrupted, this single file is what the re-run reads to resume
# on the same commit.
HEAD_SHA=$(gh api repos/<owner>/<repo>/commits/<default-branch> --jq '.sha')
echo "$HEAD_SHA" > head-sha.txt

# Download at the pinned SHA so a force-push between now and the end of
# the scan can't silently change what we're analysing.
gh api "repos/<owner>/<repo>/tarball/${HEAD_SHA}" > tarball.gz
mkdir -p src && tar --no-absolute-names -xzf tarball.gz -C src --strip-components=1

# Strip symlinks — prevents malicious repos from reading host files via
# symlinks pointing outside the scan directory (e.g., README.md -> /etc/shadow).
find src -type l -delete

# Sanity check. If this returns 0, abort — the scan is broken and should
# be reported as "blocked."
find src -type f | wc -l
```

**Why `/tmp`:** the tarball and intermediate evidence are not durable artifacts by default. The scan's durable outputs are the committed `docs/GitHub-Scanner-<repo>.{html,md}` pair plus `head-sha.txt` (immediately) and the bundle copy (on Phase 4 success — see §12).

**Fragility acknowledgement:** a session crash between Phase 2 and Phase 4 loses the bundle because `/tmp` is volatile. The minimum durability policy in §12 addresses the SHA + final-bundle cases; mid-scan auto-resume is deferred to post-Phase-2-YAML.

---

## 6. Phase 2 — Gather

**Goal:** populate the LLM's context with every piece of evidence the V2.4 prompt's finding rules depend on.

The prompt's Step 1–Step 8 + Step A/B/C describe exactly which `gh api` calls and local greps are required. This guide does not repeat them — **follow the prompt**. What this guide captures is the **ordering discipline, what counts as evidence, and the common failure modes**.

### 6.1 Ordering discipline (1:1 with the V2.4 prompt)

Run these in this order, numbered exactly as the V2.4 prompt numbers them. Later steps use earlier results.

1. **Step 1 — Repo basics, maintainer background, and governance.** Repo metadata, owner profile, contributors, CODEOWNERS × 4 paths, branch protection × 2 branches + rulesets + rules-on-default + org rulesets if Org. The C20 governance single-point-of-failure check is fully performed here as the prompt specifies.
2. **Step 2 — Read the actual CI workflow files.** `pull_request_target` surfaces, SHA-pinning audit, third-party-action tier classification.
3. **Step 2.5 — Detect agent-rule files (CI-amplified AND static, F7).** First-class numbered step, not an afterthought. Covers `.github/copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.windsurf/*`, `.cline/*`, and Archon-ecosystem `commands/*.md` YAML-frontmatter files.
4. **Step 3 — Dependency and supply chain.** Package manifests (package.json / Cargo.toml / pyproject.toml / go.mod / etc.), Dependabot alerts, published security advisories.
5. **Step 4 — PR history with self-merge detection + dual review-rate metric (F11).** Both `reviewDecision` set AND `reviews.length > 0`. Solo-maintainer context mandatory when owner has >80% of commits.
6. **Step 5 — Drill into security-relevant PRs (title OR path gating, F3).**
   - 5a: title-keyword drill-in
   - 5b: path-keyword drill-in (config/defaults paths per C15)
   - 5c: batch-change keyword grep (C15)
7. **Step 6 — Issues (user-reported problems).**
8. **Step 7 — Recent commits.**
9. **Step 7.5 — README install-paste scan.** Mandatory output schema for paste-blocks (F10).
10. **Step 8 — Installed-artifact verification (F1).** For every declared distribution channel, resolve what users actually install and diff against source.
11. **Step A — Dangerous-primitive grep on `src/` (cross-cutting).** Pattern-only, no full reads.
12. **Step B — Targeted read with quarantine.** Only when a grep hits.
13. **Step C — Executable file inventory (F12, two-layer).**

**Release cadence** is captured during Step 1's governance block (it feeds the C20 severity gate) and cross-referenced again when writing the bundle.

### 6.2 What counts as evidence

| Kind | Example | Treat as |
|---|---|---|
| **Fact** | `gh api repos/OWNER/NAME/branches/main/protection` returns 404 | Directly quotable in the report. Confirmed. |
| **Fact** | `grep -rn 'eval(' src/` returns 0 matches | Directly quotable. Confirmed clean. |
| **Inference** | "This install pattern resembles caveman's curl-pipe-from-main shape" | Synthesis step. Note in the bundle's *Pattern recognition* section, never in an evidence section. |
| **Assumption** | "Garry Tan's account is secure because he's YC CEO" | Not evidence. Don't include. |

Tag each bullet in your gathering notes with its kind. The findings-bundle segregates these structurally (§7).

### 6.3 Common failure modes

- **403 on Dependabot alerts:** two possible meanings. "Not authorized" = scope gap (your token can't see; state is **unknown**). "Disabled for this repository" = actively disabled (factual finding). Record the exact error message.
- **404 on branch protection:** usually means "no classic protection rule." But rulesets or org-rulesets may still protect the branch. The `rules/branches/<branch>` endpoint is the authoritative check for "what rules apply to this branch."
- **Org rulesets require `admin:org` scope.** If your token lacks it, the finding is "unknown," not "absent." Record which.
- **Tarball URL follows redirects** — use `gh api` (which follows them) rather than raw `curl`.
- **`gh api tarball/<SHA>` exceeds GitHub's response-size limit or times out.** Fall back to:
  ```bash
  git clone --depth 1 --single-branch --branch <default-branch> \
    https://github.com/<owner>/<repo>.git src
  cd src && git checkout "$HEAD_SHA" && cd ..
  ```
  Record which path (tarball vs shallow-clone) was used in the bundle's "Repo identity" evidence block.

---

## 7. Phase 3 — Bundle

**Goal:** write `/tmp/scan-<repo>/findings-bundle.md` — a single document that is the input to Phase 4.

### 7.1 Why the bundle exists

- It separates **what was found** (evidence) from **how it will be rendered** (report).
- It makes Phase 4 reproducible: a different LLM (or a human) given the bundle can render the same report.
- It is the **single source of truth for a given scan**. If Phase 4 drifts from the bundle, Phase 4 is wrong; the bundle should not be edited to match.
- **JSON-readiness (narrow).** The bundle's structure is amenable to JSON formalisation when the JSON-first migration fires, but the current prose form has gaps a schema would need to close (classification enums, citation pointers, capture-plan state). See §14.1 for what's in scope for near-term YAML-ification vs deferred to the JSON migration.

### 7.2 Required sections of the bundle

The bundle has three structurally-separated regions: **evidence (facts only)**, **pattern recognition (inference)**, and **synthesis (proposed findings / verdict / scorecard)**. Do not mix.

#### Evidence sections — facts only

```markdown
# <repo> Scan — Evidence Bundle

## Repo identity            — facts from gh api (include fetch path: tarball vs clone)
## Owner                    — facts from gh api
## Contributors             — facts only (commit counts, timestamps, login handles)
## Governance (C20 check)   — facts (all 7 signals: classic protection × 2, rulesets, rules-on-default, org rulesets, CODEOWNERS × 4 paths)
## Releases                 — facts (cadence, latest tag, release notes keywords)
## Dependabot / advisories  — facts, clearly labelled unknown vs disabled vs active
## CI workflows             — facts per workflow (file, triggers, action pins, permissions)
## Runtime dependencies     — facts (manifests quoted verbatim)
## Step A grep results      — facts (command + match count + first-5 matches with line refs)
## README install path      — facts + verbatim-quoted install commands
## F12 exec inventory       — facts (2-layer per V2.4 prompt)
## PR review rate sample    — facts only (dual metric — reviewDecision set AND reviews.length > 0)
## Recent commits sample    — facts (SHA, author, date, title, signed? flag)
## Open issues              — facts (count, severity keywords, ages)
```

Evidence sections may never contain interpretive verbs. Evidence is what a reviewer can rerun and reproduce.

#### Pattern recognition (inference) — tagged, segregated

```markdown
## Pattern recognition (inference)
- Statements connecting this scan's facts to prior-scan shapes, authorial heuristics,
  or plausible threat models. Each bullet MUST use an interpretive verb from the
  allowed list so a reader cannot mistake it for a fact:
    resembles, suggests, consistent with, pattern-matches to, reminiscent of,
    plausibly indicates, looks like, behaves similarly to
- Every bullet cites the evidence section line refs it derives from.
- A reviewer can disagree with any bullet here without disputing facts.
```

#### Synthesis sections — derived from facts + inferences, with citations

```markdown
## FINDINGS SUMMARY                       — synthesis
### F0, F1, ...                           — each with severity + title + evidence citations
## Positive signals                       — synthesis (for exhibits + scorecard)
## Proposed verdict                       — synthesis (cites finding severities that drive it)
## Proposed scorecard (C10)               — synthesis (each cell cites evidence)
## Catalog metadata                       — facts for header (category / SHA / date / methodology-used / etc.)
```

Every claim in the synthesis region **must cite the evidence line refs or evidence IDs it derives from** (§11.1).

### 7.3 Fact / inference / synthesis — quick reference

This is a pointer section only. The authoritative treatment is §11.

- Evidence sections: **facts only**. Verbatim quotes where possible.
- Pattern recognition section: **inference**, tagged with an interpretive verb, always cited to evidence.
- Synthesis sections: **derived** from facts + inference, every claim cited.

If you catch yourself writing an interpretive verb in an evidence section, cut it and move the bullet to Pattern recognition.

### 7.4 Proposed verdict lives in the bundle, not in the head

- The bundle proposes the verdict (`critical` / `caution` / `clean`), scope axis (`Version ·` or `Deployment ·`), both audience-entry severities, all 4 scorecard cells with red/amber/green, and all finding severities.
- Phase 4 transcribes these into the MD report and the HTML view — it does not re-derive them.
- If Phase 4 disagrees with the bundle, that's a Phase 3 error to fix in the bundle, not a Phase 4 decision to improvise.

---

## 8. Phase 4 — Render

**Goal:** produce the committed `docs/GitHub-Scanner-<repo>.md` and `.html` pair.

**Phase 4 is split into 4a (MD-first) → 4b (HTML-from-MD).** A lightweight Phase 4c exists for re-run determinism records.

### 8.1 Execution mode: continuous (legacy alias: Path A — the only mode exercised today in V2.4)

- The same LLM runtime that completed Phases 2 and 3 continues directly into Phase 4.
- Load the findings-bundle, the V2.4 template, and 1–2 prior scans as structural references (chosen by shape match — see §8.3).
- Produce the MD (4a) and then the HTML (4b) in the same session.
- **7 of 9** scans in `docs/scanner-catalog.md` used Path A; 2 used Path B (hermes-agent, postiz-app). Both methodologies are validated.
- Tag the catalog entry with `methodology-used: path-a`.

**Path-selection criterion (context-budget, not file-count).** Path A is viable when the operator's remaining context can hold:

`context.md + brief + DRAFT-or-reference + bundle + template-or-prior-scan + the edit loop`

If the context budget is exhausted or fragmented — if any of the six ingredients has already been squeezed out or is about to be — consider Path B.

### 8.2 Execution mode: delegated (legacy alias: Path B — exercised and validated)

> **Validated:** zustand-v2 scan (2026-04-16) — fresh Opus agent ran end-to-end from handoff packet alone. Structural parity with Path A confirmed. hermes-agent and postiz-app scans also used Path B successfully.

- Phase 2–3 operator writes the bundle (or the delegated agent runs all 6 phases from scratch with the handoff packet).
- A fresh sub-agent or delegated runtime is launched with the portable handoff packet (§8.3): read the guide, read the prompt, use 1–2 prior scans as structural references, produce the MD + HTML pair, validate, iterate.
- The parent operator is free to work on other tasks while the delegated runtime runs.
- Intended for cases where the context budget cannot hold the edit loop alongside prior Phase 2–3 context, or when running multiple scans in parallel.
- Tag the catalog entry with `methodology-used: path-b`.

### 8.3 The portable handoff packet

The guide previously described Path A (continuous) and Path B (delegated) in terms of operator runtime. In practice, what matters is the **handoff packet** — the exact artifact set the operator's LLM runtime receives. The rules below are runtime-agnostic.

**Required artifacts in every handoff packet:**

1. This guide (`SCANNER-OPERATOR-GUIDE.md`)
2. The V2.4 prompt (`repo-deep-dive-prompt.md`)
3. The findings bundle (`/tmp/scan-<repo>/findings-bundle.md`) for the Phase 4 render step
4. The template (`GitHub-Repo-Scan-Template.html`)
5. The validator (`validate-scanner-report.py`)
6. 1–2 prior reference scans from `docs/scanner-catalog.md` — selected by shape match

**Load order** (first to last into the runtime's context):

`context.md → brief (role-specific for Path B; operator's self-direction for Path A) → DRAFT/guide → V2.4 prompt → findings-bundle → template + reference scans`

**Render order.** MD-first (Phase 4a) → HTML-from-MD (Phase 4b). Never render HTML first.

**Validation order.** MD validator pass → HTML validator pass. Iterate until both exit 0.

**Context-fallback rule.** If the operator's runtime context is smaller than the combined inputs:
1. Elide the reference scan with the weakest shape match first.
2. Trim the validator docs to command-examples only.
3. As last resort, split the render into two calls — Phase 4a in call 1, Phase 4b in call 2 — passing the MD between them.

### 8.4 What the rendered output must contain

The rendered output's required structural elements are specified by the V2.4 prompt (`repo-deep-dive-prompt.md` output-format section, lines ~1106–1490 — §"What Should I Do?", §"What We Found", §"Executable File Inventory", etc.). That spec is the **canonical output contract**.

This contract can be realized via two rendering pipelines (see §8.1 / §8.8):
- **Workflow V2.4 (the path exercised by all 10 catalog entries):** the LLM authors the MD + HTML directly from the findings-bundle, following the prompt's output-format section as a template.
- **Workflow V2.5-preview (experimental, Step G validation in progress):** the LLM authors a `form.json` conforming to `docs/scan-schema.json` V1.1; the deterministic renderers `docs/render-md.py` + `docs/render-html.py` (with Jinja2 partials at `docs/templates/` + `docs/templates-html/`) produce the MD + HTML from the form.

Both pipelines must produce output conforming to the prompt's output-format spec. The schema + renderers are an implementation of that spec, not a second competing spec. This guide does not duplicate the spec itself.

### 8.5 Phase 4a — bundle → canonical MD

- Phase 4a is the creative/rendering step. The LLM reads the bundle, reads 1–2 shape-matched reference scans, and produces the canonical MD report.
- All proposed verdicts, finding severities, scorecard cells, and audience-severity calls must transcribe from the bundle, not be re-derived.
- Every claim carries an evidence citation, per §11.1.

### 8.6 Phase 4b — MD → HTML (structurally derived)

- Phase 4b is a structural derivation from the MD.
- **HTML may not add or alter findings, verdicts, evidence text, or scorecard calls that are absent from or different in the MD.** The V2.4 prompt's §8.4 MD-canonical rule applies: if the HTML says something the MD does not, the HTML is wrong.
- The MD must include markdown equivalents of key structural elements: section-status summary lines (as blockquotes), section-action blocks, exhibit grouping (as `<details>` blocks), evidence priority grouping (as `### ★ Priority evidence` headers), and split-verdict per-audience entries (as H3 sub-headings). The HTML adds CSS-level presentational polish (colours, animations, grid layouts) — not structural content absent from the MD.

**NON-NEGOTIABLE: the CSS design system.** Before writing ANY HTML body content, copy the entire contents of `docs/scanner-design-system.css` (824 lines) into the HTML's `<style>` block verbatim. Do not modify, truncate, abbreviate, or rewrite ANY part of the CSS. This file is the canonical design system — it defines the verdict banner, scorecard grid, finding cards, exhibit rollup, timeline, and all visual conventions. HTML scans that do not use this exact CSS will drift from the catalog and must be re-rendered.

The CSS includes the single-pass scan-line animation (a thin cyan line that sweeps once from top to bottom on page load, then disappears).

### 8.7 Phase 4c — re-run determinism record (optional, lightweight)

- Used when a scan has already been produced and a re-run on a new SHA or in a new session yields **identical structural findings** — only cosmetic drift (dossier SHA, dates, counts).
- Output is an MD-only note (e.g., `GitHub-Scanner-<repo>-rerun-record.md`) listing: prior scan's SHA, new SHA, what changed, explicit "no structural drift" statement.
- Does not require Phase 4b.
- Example in the current catalog: `GitHub-Scanner-Archon-rerun-record.md` (2026-04-16 re-run confirming the Archon scan's verdict held across a dev→dev SHA bump).

### 8.8 Phase 4 — Workflow V2.5-preview (JSON-first, production-cleared 2026-04-20)

> **V2.5-preview — production-cleared 2026-04-20. Current schema: V1.2 (landed 2026-04-20).**
> - **Schema V1.2 shipped 2026-04-20** per board review `docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md` (3 rounds + owner directives; 3/3 SIGN OFF; 31-item dissent audit with zero silent drops). Closes D-7 (scorecard cell authority migration) + D-8 (schema harness-canonical). Key deltas: transformer deleted (schema adopts harness names + shapes); `phase_3_advisory.scorecard_hints` new top-level; `phase_4_structured_llm.scorecard_cells` authoritative with `{rationale, edge_case, suggested_threshold_adjustment, computed_signal_refs, override_reason}`; 23-row signal ID vocabulary (`compute.SIGNAL_IDS`) with question-scoped prefix (`q1_` / `q2_` / `q3_` / `q4_` / `c20_`); 5-value `override_reason` enum; `agent_rule_files.total_bytes` dropped.
> - **Gate 6.3 is now "override-explained."** When Phase 4's scorecard color differs from the paired `phase_3_advisory` advisory color, validator (docs/validate-scanner-report.py `--form` mode) requires: `rationale ≥50 chars`, `computed_signal_refs` non-empty with all IDs resolving against `compute.SIGNAL_IDS`, and `override_reason` in the 5-value enum. Schema validation + override-gate are both run by `python3 docs/validate-scanner-report.py --form <form.json>`.
> - **V1.1 support:** V1.1 forms continue to validate against V1.1 schema for archived-artifact tests (`step-g-failed-artifact` fixtures stay V1.1; tests referencing them pin via `# schema: V1.1` annotation). New scans target V1.2. One-time migration: `python3 migrate-v1.1-to-v1.2.py` (active fixtures only; idempotent).
> - Step G acceptance matrix: 3/3 targets cleared all 7 gates on pinned V2.4 SHAs (zustand-v3, caveman, Archon — catalog entries 12-14, commits `2c13324`, `ed68fae`, `be56935`).
> - Production-clearance trigger fired 2026-04-20 via first wild scan on Python monorepo shape (microsoft/markitdown, 112k stars — outside the 3 Step G validation shapes); cleared all 7 applicable gates using harness-gathered Phase 1 data.
> - **Phase 1 is harness-driven.** `docs/phase_1_harness.py` (shipped commit `4ad4cf6`) implements V2.4 prompt Steps 1-8 + A/B/C end-to-end: gh api + OSSF Scorecard + osv.dev + gitleaks + package registries (PyPI/npm/crates.io/RubyGems) + tarball extraction + local grep + README paste-scan. Run: `python3 docs/phase_1_harness.py <owner/repo> --out FORM.json`. V1.2 schema accepts the harness output directly (transformer eliminated). See `docs/phase-1-checklist.md` for the canonical step→field mapping.
> - V2.4 (§8.5-8.6) remains a valid pipeline; V2.5-preview is the right choice when structural parity vs V2.4 comparators (Step G targets) or deterministic reproducibility matters, OR when you want Phase 1 automated rather than LLM-authored.
> - Validated shapes: JS library (zustand-v3), curl-pipe installer (caveman), Bun/TS agentic platform monorepo (Archon), **Python monorepo + PyPI + Dockerfile (markitdown)**. CLI-binary (fd), Claude-Code-skills (gstack), web-app (postiz-app) shapes remain un-wild-scanned — each new shape is a soft opportunity to widen the validation surface.
> - **Last reviewed: 2026-04-20 (V1.2 schema landing).** Most recent board decision: `docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md`.

#### 8.8.1 Status

The deterministic renderer shipped in commits `402f933` (Step F HTML renderer + 2 fixtures) + `ce698d4` (Step F R3 XSS/CSS/parity fixes). The Jinja2 architecture validates clean against back-authored fixtures (zustand, caveman, archon-subset) with 279/279 tests passing and validator `--report` + `--parity` clean. All 4 Step G pre-reqs cleared (U-1, U-3/FX-4, U-5/PD3, U-10). Step G execution approach approved by board review `041926-step-g-execution` with 9 fix artifacts + 15 carry-forward dispositions + graduated failure rubric. **End-to-end validation on a live scan (fresh `gh api` capture → pipeline → MD+HTML) remains the open execution step.**

#### 8.8.2 Workflow

1. Phases 1–3 unchanged from V2.4 (prep, gather, bundle). Same `head-sha.txt` first-durable-artifact rule. Same `findings-bundle.md` produced in Phase 3.
2. **Phase 4 (V2.5-preview)** — LLM authors `form.json` conforming to `docs/scan-schema.json` V1.1. Reference `tests/fixtures/zustand-form.json` for shape. The form represents the same data that in V2.4 goes into the bundle + MD, but in machine-readable structured form.
3. **Phase 4 render** — deterministic:
   ```bash
   python3 docs/render-md.py   form.json --out docs/GitHub-Scanner-<repo>.md
   python3 docs/render-html.py form.json --out docs/GitHub-Scanner-<repo>.html
   ```
4. **Phase 5** — validator gate. `--parity` and `--bundle` modes return exit 0 even when warnings exist, so the operator MUST inspect warning count explicitly, not rely on exit code alone. The validator emits three diagnostic levels: ERROR (exit 1), WARNING (structural ambiguity, exit 0 but gate-blocking), INFO (authoring/rendering variation, exit 0 non-blocking). Warning lines are prefixed `⚠ WARNING:`; info lines are prefixed `ℹ Note:`. FN-5 grep pattern matches `WARNING:` substring (not `^WARNING:`), since warnings are indent-prefixed `  ⚠ WARNING:` in validator output:
   - `python3 docs/validate-scanner-report.py --report <.html>` exits 0 on HTML
   - `python3 docs/validate-scanner-report.py --markdown <.md>` exits 0 on MD
   - `python3 docs/validate-scanner-report.py --parity <.md> <.html> 2>&1 | tee parity-output.txt` — exit 0 required AND `grep -c 'WARNING:' parity-output.txt` must equal `0`
   - `python3 docs/validate-scanner-report.py --bundle <findings-bundle.md> 2>&1 | tee bundle-output.txt` — exit 0 required AND `grep -c 'WARNING:' bundle-output.txt` must equal `0`
   - INFO-level notes (`ℹ Note:`) do NOT gate-block Step G acceptance. They are authoring/rendering variations (asymmetric parity where MD has F-IDs not in HTML but HTML adds nothing, compact-bundle summary style, template section-name differences). MD-canonical is asymmetric: HTML cannot add findings; MD may have extras.

**Execution ordering — pilot-and-checkpoint.** Run the first target (zustand) end-to-end through all pre-flight, authoring, render, and gate checks. **Hard checkpoint before continuing.** Checkpoint criteria:

- Zustand passes all 7 gates cleanly → continue to caveman, then Archon sequentially in the same session.
- Zustand fails on pipeline-correctness gates (1–3 or 5) → STOP; do not spend caveman + Archon on a broken pipeline; trigger rollback per §8.8.6.
- Zustand fails on authoring-only gates (4 or 6) → one retry permitted on zustand. If retry passes, continue to caveman + Archon. If retry fails on gate 6, assess shape-specific vs rubric-level per §8.8.6.

Rationale: parallel runs would confound the diagnosis space; continuous-uninterrupted could waste caveman + Archon targets if zustand reveals a systemic defect.

#### 8.8.3 Phase-to-prompt mapping + operator checklist

The prompt (`repo-deep-dive-prompt.md`) has two halves: investigation instructions (lines 1–1090) and output-format spec (lines ~1106–1490). The table below shows which form.json phase block each half feeds, and which prompt section drives it.

| Form phase | Source | Prompt reference | Schema `$def` |
|---|---|---|---|
| `phase_1_raw_capture` | `gh api` calls + OSSF Scorecard API + osv.dev + `gitleaks` if present | Pre-flight + Steps 1–4 | `phase_1_raw_capture` in `scan-schema.json` |
| `phase_2_validation` | Sanity checks on Phase 1 outputs (SHA consistent, dates chronological, tarball nonempty) | Download + extraction + symlink-strip + SANITY CHECK | `phase_2_validation` |
| `phase_3_computed` | Python compute functions (`docs/compute.py`) on Phase 1 data | Deterministic — no prompt section; the 8 automatable operations (verdict, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised) | `phase_3_computed` |
| `phase_4_structured_llm` | LLM produces enum/template-constrained fields: findings entries, general vuln severity, split-axis decision, priority evidence, threat models, action steps, timeline events, capability assessments, catalog metadata, section leads, verdict exhibits | Prompt Steps A/B/C + scorecard calibration + output-format spec §§01/02/04/07/Verdict/Trust Scorecard | `phase_4_structured_llm` |
| `phase_4b_computed` | Python derives verdict level from findings (`docs/compute.py::compute_verdict`) | Deterministic — no prompt section | `phase_4b_computed` |
| `phase_5_prose_llm` | LLM writes 4 prose fields: `what_this_means`, `what_this_does_not_mean`, finding body paragraphs, editorial caption | Output-format spec §02 finding-card body + §Hero caption | `phase_5_prose_llm` |
| `phase_6_assembly` | Final JSON merge, provenance tags | N/A (assembly step — Python) | `phase_6_assembly` |
| `scan_sign_off` | Human or operator-agent approval marker | Operator decision | `scan_sign_off` |

**Operator checklist** (converting a V2.4 findings-bundle.md into a V2.5-preview form.json). Three phases: pre-flight, authoring, post-render. Pre-flight and post-render steps are NOT optional for Step G.

**Pre-flight** (before any live bundle or form authoring begins):

- **Step -2: Provenance entry.** Per `tests/fixtures/provenance.json` `ordering_constraints`: create the provenance entry for the live Step G form BEFORE authoring begins, not retroactively. Tag as `step-g-live-pipeline`, distinct from `back-authored` or `authored-from-scan-data` template fixtures.
- **Step -1: V2.4 comparator cleanliness.** Run `validate-scanner-report.py --parity <V2.4.md> <V2.4.html>` on each of the 3 V2.4 catalog comparator pairs (zustand-v3, caveman, Archon). Each must report exit 0 AND zero `WARNING:` lines per §8.8.2 step 4 inspection (grep substring `WARNING:`, not `^WARNING:`). INFO notes (`ℹ Note:`) are not gate-blocking — they represent authoring/rendering variation (asymmetric parity, compact-bundle style, template section-name differences) and do not indicate structural-parity contamination. If any comparator reports `WARNING:` lines, STOP — the structural-parity anchor is contaminated; re-scan the comparator or document as "comparator-tainted, Step G-deferred for this shape" before proceeding.
- **Step 0: Adversarial bundle validator smoke test.** Before authoring any live bundle, author 4 synthetic bundles (each mutates a clean corpus bundle) and verify `--bundle` behavior:
  1. Inject a synthesis verb ("suggests", "indicates", "plausibly") into an evidence block under `## Evidence`. Expected: **exit 1** + flags interpretive-verb-in-evidence.
  2. Inject an orphan F-ID (`F99`) into `## Pattern recognition` that is never declared in `## FINDINGS SUMMARY`. Expected: **exit 1** + flags orphan-F-ID.
  3. Delete the `## FINDINGS SUMMARY` section entirely. Expected: **exit 1** + flags missing-required-section.
  4. **Compact-bundle baseline:** `## FINDINGS SUMMARY` contains ZERO F-IDs but valid prose (the zustand-v3 compact style). Expected: **exit 0** with informational note, NOT a failure. Confirms validator distinguishes empty-but-valid from missing.

  Each failure-case must hard-fail with nonzero exit AND a specific message. Compact-bundle case must pass. If any test behaves unexpectedly, STOP — bundle validator is not acceptance-ready.

**Authoring** (per target):

1. Start with `tests/fixtures/zustand-form.json` as a template (copy + blank out repo-specific fields). **Note:** `zustand-form.json` is tagged `authored-from-scan-data` in `provenance.json`; it is a template-for-shape, NOT evidence of pipeline correctness.
2. Populate `target.{owner,repo,full_name,url}` + `_meta.{prompt_version,scan_started_at,scanner_version}` + `phase_1_raw_capture.pre_flight.head_sha` (full 40-char).
3. Fill `phase_1_raw_capture.*` from the `gh api` call outputs your V2.4 scan already captured.
4. **Step 3b — Phase 3 computed fields MUST invoke `python3 docs/compute.py` directly.** "Mirror the logic manually" is **disallowed** for Step G. Required invocations per the 8 automatable operations (verdict, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised). Capture emitted values as artifacts at `.board-review-temp/step-g-execution/compute-output-<target>.json` for audit. `phase_3_computed.*` and `phase_4b_computed.verdict.level` in the live `form.json` MUST equal these emitted values byte-for-byte.
   - **Note (SF1 board 2026-04-20):** The scorecard-cell computation within `compute.py` carries 5 temporary compatibility patches for V1.1 Step G acceptance — these align compute output with the V2.4 comparator-MD judgments that gate 6.3 checks against. The patches are annotated in `docs/compute.py` and are NOT the steady-state design. Scorecard-cell authority migrates to `phase_4_structured_llm` in V1.2 per deferred item D-7 (§8.8.7). The byte-for-byte rule remains in force for Step G; after D-7 lands, gate 6.3 changes from "cell-by-cell match" to "override-explained" and the byte-for-byte requirement drops for scorecard cells only.
5. **Step 3c — Bundle-complete gate.** Before beginning `form.json` authoring, confirm ALL of:
   1. `findings-bundle.md` contains all 6 required sections (`## Scan metadata`, `## Evidence`, `## Pattern recognition`, `## FINDINGS SUMMARY`, `## Verdict`, `## Scorecard`).
   2. `validate-scanner-report.py --bundle <findings-bundle.md>` returns exit 0 + zero `WARNING:` lines (per §8.8.2 step 4 inspection).
   3. Bundle file saved + committed to `docs/board-review-data/scan-bundles/<repo>-<sha>.md` per §12 durability rule.

   Only after 5.1–5.3 succeed may `form.json` authoring begin. No mid-bundle drafting of `form.json`.
6. Translate the findings-bundle's evidence + synthesis sections into `phase_4_structured_llm.findings.entries[]` + `phase_4_structured_llm.verdict_exhibits.groups[]` + supporting structured fields. One finding in the bundle = one entry in the schema. Phase 3 computed values from Step 3b are authoritative — do NOT re-derive them.
7. Author the 4 prose fields (`phase_5_prose_llm.*`) using the bundle's finding summary prose.
8. Validate the form against the schema: `python3 -c "import json; from jsonschema import Draft202012Validator; schema=json.load(open('docs/scan-schema.json')); form=json.load(open('form.json')); errors=list(Draft202012Validator(schema).iter_errors(form)); print('✓' if not errors else f'✗ {len(errors)} errors: {[e.message[:100] for e in errors[:5]]}')"`
9. Render via §8.8.2 step 3 command.

**Post-render** (per target):

- **Step 10 — Phase-boundary contamination check, all 3 targets, semantic criteria, STOP on contamination.** For each `form.json`: confirm `phase_4_structured_llm.findings.entries[].*` structured fields (severity, evidence_refs, action_steps) contain only structured content appropriate to the field type; **no narrative sentences or synthesis claims in Phase 4 structured fields.** Prose must live in `phase_5_prose_llm.*`. This check runs on EVERY target, not first-only — boundary contamination is shape-sensitive. If contamination is found in ANY target, **STOP execution** and fix the authoring rubric/prompt before proceeding. Contamination indicates a systemic LLM prompt issue; proceeding would waste subsequent targets on the same defect.
- **Step 11 — Gate acceptance.** Run §8.8.5 gates 1–7. All gates must pass per the §8.8.6 disposition rules.
- **Note on authoring determinism:** Step G does NOT require that the same bundle produce byte-identical `form.json` across re-authoring attempts by the same or different LLM. This is deferred property D-3 on the post-Step-G ledger. Gate 5 tests render-determinism given a fixed `form.json`, not authoring-determinism.

Automation note: Step 3b's compute.py invocation is manual for Step G — the pipeline harness calling compute.py from a filled Phase 1 is deferred item D-2 on the post-Step-G ledger.

#### 8.8.4 Invariants preserved from V2.4

- **MD-canonical rule** — HTML may not add findings absent from MD. Enforced by the shared form.json contract and the `--parity` validator gate.
- **Facts / inference / synthesis separation** — enforced by schema phase boundaries (Phase 1 = facts, Phase 3 = compute-derived, Phase 4 = structured LLM inference/synthesis, Phase 5 = prose LLM synthesis). Phase-boundary contamination check (§8.8.3 Step 10) catches leaks into Phase 4 structured fields.
- **`head-sha.txt` first durable artifact.** Same as V2.4.
- **Validator is the gate.** Same as V2.4, plus the `--parity` zero-errors-zero-warnings requirement for Step G acceptance. Operator parses warning count explicitly (§8.8.2 step 4); exit code alone is insufficient.

#### 8.8.5 Step G success criterion

**Validator-clean is necessary but NOT sufficient.** A V2.5-preview scan passes Step G for a target only if ALL 7 gates pass:

1. `form.json` validates clean against V1.1 schema (zero errors).
2. Both rendered outputs pass `validate-scanner-report.py --report` (exit 0).
3. `--parity <md> <html>` reports zero errors **AND** zero `WARNING:` lines (operator must inspect stdout per §8.8.2 step 4; exit code alone is insufficient). INFO notes (`ℹ Note:`) are non-gating.
4. Evidence refs resolve (no dead `E*` or `EB-*` references in findings).
5. Re-rendering the same `form.json` produces byte-identical MD + HTML (determinism test: `diff <(render) <(render)` = empty).
6. **Structural parity against V2.4 comparator — explicit zero-tolerance checklist.** For each target, compare V2.5-preview rendered MD against the V2.4 catalog comparator MD at the same SHA. ALL of the following must be exact match; any mismatch = gate-6 failure:
   - **6.1 Finding inventory** — every F-ID in V2.4 comparator maps to exactly one entry in `phase_4_structured_llm.findings.entries[]`. No extras. No missing.
   - **6.2 Severity per F-ID** — each F-ID's `severity` matches V2.4 comparator's severity for the same F-ID. Zero inversions, zero downgrades, zero upgrades. **Execution-record requirement:** document the mapping in `.board-review-temp/step-g-execution/severity-mapping-<target>.md` as a table with one row per finding: `<F-ID> | <V2.4 severity> | <V2.5-preview severity> | match?`. Operator attests match explicitly; auditable trail preserves the comparison.
   - **6.3 Scorecard cells** — all 4 canonical questions present + all 4 cell colors match V2.4 comparator cell-by-cell (red/amber/green).
   - **6.4 Verdict level** — `phase_4b_computed.verdict.level` (Critical / Caution / Clean) matches V2.4 comparator's verdict level.
   - **6.5 Split-axis** — if comparator is a split verdict, `phase_4_structured_llm.verdict_split.axis` must match (`deployment` vs `version`, etc.). If comparator is not split, V2.5-preview must not be split.
   - **6.6 Evidence linkage** — every non-OK finding has non-empty `evidence_refs`; every ref resolves to a declared entry in `phase_4_structured_llm.evidence.entries[]`.
   - **Archon-specific comparator clarification:** The comparator for Archon is `docs/GitHub-Scanner-Archon.md` (full 11 findings), NOT `tests/fixtures/archon-subset-form.json` (4 findings, renderer-validation scope only).
   - **Evidence-card count** is informational only, not a gate. V2.4 catalog scans use varying depth (zustand-v3 bullets, caveman + Archon tables) — this is rendering variation, not drift.
7. **Phase-boundary contamination check** (§8.8.3 Step 10) passes for every target — no narrative sentences or synthesis claims in Phase 4 structured fields. STOP condition applies if contamination is found on any target.

#### 8.8.6 Failure disposition — graduated rubric

**Not all failures are equal.** Pipeline-correctness failures require full rollback; authoring-quality failures are graded and retryable. The verdict stays strict: **Step G is NOT "passed" until all 3 targets clear all 7 gates** (including gate 6 after permitted retries).

| Failure pattern | Disposition |
|---|---|
| Validator gates 1–3 fail on ANY target | **Full rollback** — §8.8 quarantined, failed forms tagged `step-g-failed-artifact`, V2.4 remains only production path. Pipeline-correctness failure. |
| Determinism gate 5 fails on ANY target | **Full rollback** — indicates renderer bug in `render-md.py`/`render-html.py`. Pipeline-correctness failure. |
| Evidence refs gate 4 fails on 1 target | **Target-local authoring error.** One retry for that target (re-author affected findings). If retry fails → target fails Step G; proceed to other targets; graduate per gate-6 rules. |
| Gate 6 (structural parity) fails on 1 target, others clean, **after one retry** | **Overall Step G = FAIL**, treated as **isolated target failure, not full rollback.** Failing shape tagged `step-g-failed-artifact` in `provenance.json`; retain passing targets as diagnostic evidence; V2.5-preview **NOT promoted as Step-G-passed until all 3 shapes pass**. NO full quarantine unless repeated or systemic. |
| Gate 6 fails on 2+ of 3 targets (including retries) | **Full rollback** — authoring-quality failure at scale indicates schema or rubric-level defect. |
| Gate 7 (phase-boundary contamination) triggers on ANY target | **STOP immediately.** Fix authoring rubric/prompt before proceeding. Contamination indicates systemic LLM prompt issue. |
| ANY gate fails ambiguously mid-run (rubric interpretation dispute) | **HALT immediately.** Do not claim pass/fail. Escalate to board mini-review before continuing. |
| Schema-validation failure (form.json invalid against V1.1) | **Target-local authoring error** — one retry; behaves like gate 4. |

**Key principles:**

- Gates 1–3, 5 = **pipeline correctness** → full rollback on any failure.
- Gate 4 + schema validation = **authoring error, target-local, retryable**.
- Gate 6 = **authoring quality, graded** — isolated miss after retry = Step G fails overall but isolated disposition (no quarantine); scaled miss = systemic, full rollback.
- Gate 7 = **systemic prompt health** → STOP on any target's contamination.
- Ambiguity = halt, not pass.

**Rollback operational consequences** (when full rollback is triggered):

1. Workflow V2.4 (§8.5–8.6) continues as the ONLY production/default path. Existing catalog scans are unaffected.
2. The V2.5-preview subsection (this §8.8) is either **reverted out of the main Operator Guide flow** (removed from §8) or **quarantined into an appendix** at the end of this guide. Operator-entry points (CLAUDE.md wizard Q3a, §8 TOC) remove the V2.5-preview option until schema/renderer fixes validate in a fresh board review.
3. Failed Step G `form.json` files are tagged in `tests/fixtures/provenance.json` as `step-g-failed-artifact` and kept as test artifacts, NOT as operator exemplars.
4. `github-scan-package-V2/` is NOT mutated during rollback. The package is a V2.4 distributable; V2.5 inclusion is a separate post-Step-G release cycle.
5. Schema revision (to V1.2 or later) happens in a separate work cycle; this §8.8 is held DEPRECATED during that cycle.

#### 8.8.7 Known limitations + post-Step-G commitments

**Limitations pre-Step-G:**

- Only 3 shapes have V1.1 fixtures (JS library, curl-pipe installer, agentic platform monorepo). CLI binary, Claude Code skills, web app, and Python platform shapes are NOT exercised. Shape-specific schema gaps for fd/gstack/postiz/hermes-agent cannot be detected by this Step G; tracked as D-5 on the post-Step-G ledger.
- The JSON-first pipeline has NOT produced a scan from live `gh api` data — only back-authored reconstructions of goldens. Step G is the first live run.
- Phases 4–6 automation (structured LLM, prose LLM, assembly) is not built. Step G uses LLM-in-the-loop for those phases. Full automation is deferred item D-2.
- **Schema hardening — explicit watchpoint, not merely deferred.** `docs/scan-schema.json` V1.1 does not fully formalize the prompt output-format spec. Notable gaps: Scanner Integrity section 00 hit-level file/line/raw-content structure; Section 08 methodology fields beyond version marker. **Any need to invent ad hoc fields, overload existing fields, or carry semantics outside schema-defined locations upgrades this from DEFER to FIX NOW and HALTS execution.** Schema revision requires a separate board review cycle.
- Fresh-HEAD live scan validation is a production-promotion pre-req, not a Step G acceptance pre-req (D-1). Step G runs at pinned V2.4 catalog SHAs for apples-to-apples structural-parity comparison.
- LLM non-determinism on form.json re-authoring (same bundle, different LLM or session → potentially different schema-valid form.json) is deferred property D-3. Gate 5 tests render-determinism given a fixed `form.json`, not authoring-determinism.
- Fixture provenance tagging (U-3/FX-4 per board) landed in commit `3c09afb` at `tests/fixtures/provenance.json`. Live Step G forms must be tagged there BEFORE authoring begins (see §8.8.3 Step -2).
- PD3 bundle/citation validator shipped 2026-04-19 as `--bundle` mode in `docs/validate-scanner-report.py` (U-5 per board, commit `885bdcf`). Required gate before first live Step G scan; see §9.2.1 for invocation.

**Post-Step-G commitments (not deferred indefinitely):**

- **D-6 Automated severity distribution comparison script — SHIPPED 2026-04-20.** Lives at `docs/compare-severity-distribution.py`. Reads either a rendered `.md` report or a `form.json` bundle from each side; emits the severity-mapping table and exits 1 on any mismatch. Invocation:
  ```bash
  python3 docs/compare-severity-distribution.py \
    --v24 docs/GitHub-Scanner-<target>.md \
    --v25 docs/GitHub-Scanner-<target>-v25preview.md \
    --target <target> \
    [--out .board-review-temp/step-g-execution/severity-mapping-<target>.md]
  ```
  Tests at `tests/test_compare_severity_distribution.py` (23 tests; exit-code contract + 3 integrated Step G pairs pass). Use this tool instead of the manual gate-6.2 check from §8.8 going forward.

- **D-7 Scorecard cell authority migration (V1.1 → V1.2) — COMMITTED, not conditional.** Added by SF1 board review 2026-04-20 (`docs/External-Board-Reviews/042026-sf1-calibration/CONSOLIDATION.md`). Move scorecard cell colors out of `phase_3_computed.scorecard_cells` into `phase_4_structured_llm.scorecard_cells` with structured-constraint fields: `question`, `color` (red|amber|green enum), `short_answer`, `rationale` (must cite E-IDs), `edge_case` (bool), `suggested_threshold_adjustment` (optional — feedback loop), `computed_signal_refs` (list). Demote `compute_scorecard_cells()` to advisory — output surfaces as `phase_3_advisory.scorecard_hints` for Phase 4 LLM to consult. Gate 6.3 changes from "cell-by-cell match" to "cells present + rationale cites evidence + LLM override of advisory hint explained with `edge_case=true`." Step 3b byte-for-byte requirement RETAINED for the other 7 Phase 3 operations.
  - **Trigger** (disjunctive; whichever fires first): (1) first V2.5-preview scan on a repo shape NOT in the current 7 catalog shapes; (2) 3 live V2.5-preview scans post-Step-G with ≥2 different shape categories; (3) 6 months post-Step-G, regardless of scan volume; (4) any cell diverges from V2.4-equivalent-judgment for semantic (not threshold-calibration) reasons — such divergence accelerates urgency.
  - **Rider items in scope at V1.2 implementation:** 11-scan catalog comparator analysis; override-pattern telemetry; canonical question wording review; rubric literal-vs-intent documentation for Q3 (DeepSeek R4 disobedience concern preserved); Q1 Archon governance-floor revisit (whether the override belongs in Phase 4 LLM or stays as a deterministic rule).
  - **Companion reading:** SF1 Phase 1 patches in `docs/compute.py` (Q1-Q4 calibration fixes) are annotated "temporary compatibility calibration for V1.1 Step G acceptance" — do NOT interpret them as the endorsed steady-state design. V1.2 is the durable fix.

- **D-8 Schema V1.2 hardening — accept harness output natively.** Added by first wild V2.5-preview scan 2026-04-20 (microsoft/markitdown, catalog entry #15). The Phase 1 harness (`docs/phase_1_harness.py`, commit `4ad4cf6`) produces legitimately richer data than V1.1 schema accepts — e.g. `dependencies.dependabot_alerts` + `dependencies.osv_lookups` + `dependencies.dependabot_config` (schema has only `dependencies.dependabot` + `dependencies.osv_dev` with slightly different shapes); `code_patterns.dangerous_primitives.{exec, archive_unsafe, network, ...}` per-family hit tables (schema flattens to `{hits[], hit_count}`); `pr_review.{self_merge_count, total_merged_lifetime, security_flagged_count}` (schema has only `self_merge_rate` as a computed rate); `ossf_scorecard.http_status`; `_meta.harness_version`; plus type/shape mismatches on `code_patterns.agent_rule_files` (list vs object wrapper), `pre_flight.symlinks_stripped` (int count vs bool).
  - **Current bridge (D-8 workaround):** The transformer at `.board-review-temp/markitdown-scan/transform_harness.py` converts harness output to a V1.1-compliant `form.json` while preserving the full richness in a sidecar `phase-1-raw-full.json` for provenance/audit. This is the minimum-viable path that kept the markitdown wild scan moving without a multi-day board-review pause per §8.8.7.
  - **D-8 scope when triggered:** (a) update `docs/scan-schema.json` to V1.2 with expanded field surface matching harness output (the sidecar IS the spec — it shows what V1.2 needs to accept); (b) move transformer logic into the harness itself (emit schema-valid form directly); (c) regenerate fixture forms for zustand/caveman/Archon/archon-subset with the richer surface; (d) update renderer template partials to surface the new data where useful (e.g. `self_merge_count` in §03 PR review table).
  - **Trigger:** POST-STEP-G IMMEDIATE. No external dependency; schedule alongside D-7 review cycle.
  - **Rider items:** clarify `community/profile` API quirk (markitdown hit — API didn't report files.security_policy despite SECURITY.md at root; harness now does direct-path fallback). Document as a known GitHub API gotcha in V1.2 changelog.

---

## 9. Phase 5 — Validate

**Goal:** Validator exits 0 on both the MD and the HTML. Use the correct mode flag for each format.

```bash
python3 docs/validate-scanner-report.py --markdown docs/GitHub-Scanner-<repo>.md
python3 docs/validate-scanner-report.py --report docs/GitHub-Scanner-<repo>.html
```

- `--markdown` checks: required section headers (Verdict, Findings, Evidence, Scorecard), minimum 100 lines, severity keywords.
- `--report` checks: tag balance, inline styles, px font-sizes, placeholders, EXAMPLE markers, XSS vectors, untrusted-text escaping.

All checks must pass.

### 9.1 Common false-positives (heuristic warnings that are NOT blockers)

- `bash <(curl ...)` inside a fenced code block — the `<` looks like an unclosed tag. Validator warns, returns exit 0 anyway. At least one prior scan demonstrates this pattern (see `docs/scanner-catalog.md`).
- `<<<` bash here-string inside a fenced code block — same issue, same resolution.
- Inline code containing `<placeholder-name>` style literals in the MD — these DO fail. Replace with uppercase literals (`PLACEHOLDER_NAME`) or backtick-escape per the V2.4 prompt's `docs/validate-scanner-report.py` guidance.

### 9.2 Real failures (validator returns non-zero)

- `{{PLACEHOLDER}}` tokens remaining in the rendered output → replace or delete.
- `EXAMPLE-START` / `EXAMPLE-END` markers remaining → replace or delete the block.
- Inline `style=''` attributes → move to the template's existing utility classes.
- Unescaped `<` in body text (not in code/pre/script/style/comments) → HTML-entity-escape (`&lt;`).
- Unclosed or mismatched tags → structural fix.

### 9.2.1 Pre-render checklist (walk before Phase 4a)

Walk this checklist against the Phase 3 bundle **before** starting Phase 4a. Failures are Phase 3 errors to fix in the bundle.

- [ ] Every finding-summary item in the bundle has an evidence citation (line ref or evidence ID).
- [ ] Proposed verdict cites the specific finding severities that drive it.
- [ ] Each scorecard cell cites the evidence that drives its red / amber / green call.
- [ ] All audience severities in the split-verdict cite their distinguishing criterion.
- [ ] No claim in the bundle's "Pattern recognition" section uses fact framing (no interpretive verb → cut the bullet or move to synthesis).

An automated pass is available as `python3 docs/validate-scanner-report.py --bundle /tmp/scan-<repo>/findings-bundle.md` (built 2026-04-19 per U-5/PD3 board queue). The validator audits the same 5 checklist items plus the Pattern recognition interpretive-verb rule (§7.2). Exit 0 clean, 1 on contract violation. Run before starting Phase 4a.

### 9.3 Iteration budget

Expect 1–3 iterations on HTML, 1–2 on MD. If you're past 4 iterations on either, stop and diagnose — something structural is wrong (usually a bad copy-paste from a reference scan, or a 4b step adding content not in the 4a MD).

---

## 10. Phase 6 — Catalog

**Goal:** the new scan is discoverable and the catalog is updated. Memory updates are optional and operator-specific.

### 10.1 Phase 6a — required, repo-native catalog update

Update `docs/scanner-catalog.md` with the new scan's entry. This is the **public contract** — everything Phase 6 requires must go here. One row per scan with these fields:

- Repo (`owner/name` + short description)
- HEAD SHA (short)
- Scan date (UTC ISO date)
- Verdict banner (`critical` / `caution` / `clean` + split-axis if present)
- Scope axis (`Version ·` / `Deployment ·` / both)
- Shape / structural pattern (for future shape-match lookups)
- `methodology-used: path-a` | `path-b`
- Links to the `.html` + `.md` artifacts

If `docs/scanner-catalog.md` does not exist, create it using the scaffold (the current repo ships one as part of the V0.1 promotion).

### 10.2 Phase 6b — optional, operator-local memory update

If the operator's runtime has a memory system (e.g., Claude memory files, Codex session store), update it with a pointer to the new scan. **Optional and operator-specific.**

This guide deliberately does **not** reference specific runtime memory paths. The required public contract lives in Phase 6a.

### 10.3 Surfaced rule observations

If this scan surfaced a rule-calibration observation, a rule-skip finding, or a new shape the catalog doesn't cover, capture it for the next board review. Two triggers that fire a review:
- 3+ accumulated rule-skip findings
- Severity-semantic changes
- Coverage-obligation changes

See §14.5 for the full cadence policy.

---

## 11. Fact vs inference vs synthesis — why it matters

An LLM running this scanner has pattern memory across prior scans. That's an asset (recognising structure quickly) and a liability (colouring new evidence with old patterns). Concretely, the risks:

- **Risk 1 (plausible):** Pattern-match in Phase 2 makes the operator skip an API call because "I know what this kind of repo looks like." → Scan has evidence gaps.
- **Risk 2 (plausible):** Inference written as fact in the bundle. → Report presents an interpretation as a verified finding.
- **Risk 3 (plausible):** Synthesis imported from a prior scan. → Report is self-plagiarising, not saying something honest about the target repo.

These risks are plausible and have informed guide design; pattern-memory colouring is observed anecdotally but is not measured across the 9-scan catalog.

### 11.0 The hygiene practice

- **Evidence sections** in the bundle contain only facts. Verbatim quotes where possible. If you can't write the source command that produced it, it's not a fact.
- **Inference is segregated** into its own "Pattern recognition" section (§7.2), with an interpretive verb on every bullet and an evidence citation. Reviewers can disagree with inference without disputing facts.
- **Synthesis sections** (proposed findings, verdict, scorecard) are derived from facts + inferences and **every claim carries a citation** (§11.1). The bundle structure enforces this by putting synthesis at the end.
- **The report's Section 07 (Evidence appendix)** should be direct quotes of facts + the commands that produced them. If a reader can't reproduce the evidence, the scan is not auditable.

### 11.1 Citation-discipline rule

> Every synthesized claim in the bundle — each proposed finding, each verdict entry, each scorecard cell, each audience severity — **must cite the evidence section line refs or evidence IDs it derives from**. Unlabeled synthesis is a Phase 3 error to fix in the bundle, not a Phase 4 rendering decision.

In practice this means:
- Every bullet in `## FINDINGS SUMMARY` names at least one source in the evidence region.
- The `## Proposed verdict` block lists the finding severities (F0, F4, …) that drive its call.
- Every `## Proposed scorecard` cell names the evidence section(s) that push it red / amber / green.
- Every split-verdict audience severity names the criterion that distinguishes it from the other audience.

The pre-render checklist (§9.2.1) walks these items one-by-one. Run `python3 docs/validate-scanner-report.py --bundle <findings-bundle.md>` to automate the walk (U-5/PD3, built 2026-04-19), or step through manually before starting Phase 4a.

### 11.2 Does Phase 3 synthesis bias Phase 4 render?

Yes, almost by definition. Phase 4a renders what Phase 3 proposes. The question is whether Phase 3 synthesis was derived from this scan's facts or from pattern memory of prior scans. Mitigations currently in practice:

1. Phase 3 bundle is written in full before Phase 4a begins, so the operator's synthesis is explicit.
2. Phase 4 Path B delegates to a fresh runtime, which has no pattern memory of prior scans beyond what's in the bundle + the 1–2 reference scans explicitly loaded.
3. The citation-discipline rule (§11.1) + the pre-render checklist (§9.2.1) surface uncited synthesis before it ships.
4. The validator enforces structural consistency but does not catch content drift.

---

## 12. Recovery — minimum durability policy

**Current policy (minimum durability):**

1. **`head-sha.txt` is the first durable artifact.** Write it in Phase 1 before any other gh api call. If the scan is interrupted, this is the one thing the re-run uses to resume on the same commit.
2. **On Phase 4 success**, copy `/tmp/scan-<repo>/findings-bundle.md` to `docs/board-review-data/scan-bundles/<repo>-<SHA>.md` (create the directory if absent). The bundle then lives alongside the committed HTML + MD pair for auditability.
3. **Full auto-resume on crash mid-Phase-2** remains deferred to post-Phase-2-YAML.

```bash
# At the tail of a successful Phase 4 + Phase 5:
mkdir -p docs/board-review-data/scan-bundles
cp /tmp/scan-<repo>/findings-bundle.md \
   "docs/board-review-data/scan-bundles/<repo>-${HEAD_SHA:0:7}.md"
```

**What requires new tooling** (candidates for later YAML automation):
- Resumable data-gathering: if Phase 2 has 14 sub-steps, checkpointing per-step lets a crash resume rather than restart.
- A `--checkpoint` flag on the gathering harness so partial results survive.

---

## 13. Prior-scan references

The live catalog of prior scans usable as structural references is maintained separately:

> **See `docs/scanner-catalog.md` for the live catalog of prior scans usable as structural references.**

Shape match selection and handoff-packet inclusion rules live in §8.3.

---

## 14. Open questions and final positions

Consolidated from the 3-model board review (2026-04-16). `docs/board-review-operator-guide-consolidation.md` is the review record.

### 14.1 YAML scope today

**Final position:**
- **Phase 1: full YAML.** Mechanical prep steps with variable substitution.
- **Phase 2: capture-plan + classification enums (explicitly not a truth object).** The YAML enumerates required gh api calls, jq filters, and classification enums (e.g., 403-scope-gap vs 403-disabled, 404-no-classic-protection vs 404-also-no-ruleset) so the operator records state deterministically.
- **Phase 5: orchestration metadata only.** The validator is already CLI-first; YAML adds step sequencing, not logic.
- **Phases 3 and 4 stay prose until the JSON-first migration fires.** Schema-readiness is not claimed. See consolidation doc for trigger conditions.

### 14.2 CLAUDE.md-equivalent for non-Claude operators

**Final position:** no bespoke file. The **portable handoff packet** (§8.3) supersedes the question. Any runtime receives the same packet; nothing in the guide is Claude-specific.

### 14.3 Synthesis-bias mitigation

**Final position:**
- **V0.1:** the citation-discipline rule (§11.1) + the manual pre-render checklist (§9.2.1).
- **V0.2:** `--bundle` automation in `docs/validate-scanner-report.py` — shipped 2026-04-19 per U-5/PD3 board queue. Passes on all 5 existing V2.4 bundles; 16 tests cover parser + corpus + synthetic failure cases. See §9.2.1 for invocation.

### 14.4 Recovery checkpointing pre-JSON-first

**Final position:** yes — the minimum durability policy (§12) now. `head-sha.txt` at start, bundle-on-success copy at end. Full mid-scan resume deferred to post-Phase-2-YAML.

### 14.5 Catalog growth — per-scan board re-review?

**Final position:** no. **Aggregated-delta review only** — triggers on 3+ rule-skip findings, severity-semantic changes, or coverage-obligation changes. **Interim spot-check at scans 7 and 9** (re-audit one prior scan's bundle-to-report coherence). **Full board re-review at scan 10** covers full methodology.

### 14.6 Non-github.com adaptation

The 9-scan catalog is 100% github.com. The first GHE / Gitea / self-hosted scan will surface API availability deltas that need to be captured back into the guide. Specifically: rulesets API availability, organization audit endpoints, Dependabot alerts endpoint parity. Until then, `GH_HOST=<enterprise-host>` is believed to work for Phase 2 gh calls, with manual verification required.

---

## 15. Changelog

- **2026-04-17 · V0.2** — AXIOM audit triage fixes: B5 Path B text updated (exercised + validated on zustand-v2, hermes-agent, postiz-app); B6 prerequisites table expanded (npm/pip/cargo optional for Step 8, gitleaks optional for Cap-4, curl for V2.4 APIs). Companion prompt bumped to V2.4.
- **2026-04-16 · V0.1 promotion** — Unanimous SIGN OFF AFTER FIXES from 3-model board (Pragmatist/Claude Opus 4.6, Systems Thinker/Codex GPT-5.4, Skeptic/DeepSeek V3.2). 10 FIX NOW items applied: A1 fact/inference discipline rewrite (§7.2/§7.3/§11); A2 Path A practiced / Path B proposed (§8.1/§8.2); A3 pre-flight + minimum durability policy (§4.1 new, §6.3, §12); A4 citation-discipline rule + pre-render checklist (§11.1 new, §9.2.1 new); Phase 4 MD-first split (§8, §8.4 deleted, Phase 4c added for re-run records); Phase 6 public-catalog-vs-optional-memory split (§10, §13 → docs/scanner-catalog.md); §6.1 1:1 ordering with V2.4 prompt Steps 1–8 + A/B/C, Step 2.5 restored; JSON-readiness narrowing (§7.1/§14.1); GitHub Enterprise GH_HOST note (§3, new §14.6); portable handoff packet (§8.3 new). Consolidation record: `docs/board-review-operator-guide-consolidation.md`. Author acknowledged same-model-blindspot: R2-F14 (Phase 4 conflict) and R2-F15 (Phase 6 coupling) were caught by Systems Thinker in R1, not by self-review.
- **2026-04-16** — DRAFT created from the 9-scan catalog (caveman, Archon, zustand, fd, gstack, archon-board-review). Pre-board-review. No version tag yet; will be tagged V0.1 after first board review.
