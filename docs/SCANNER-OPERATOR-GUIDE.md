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

### 8.1 Path A — continuous (the only path exercised today)

- The same LLM runtime that completed Phases 2 and 3 continues directly into Phase 4.
- Load the findings-bundle, the V2.4 template, and 1–2 prior scans as structural references (chosen by shape match — see §8.3).
- Produce the MD (4a) and then the HTML (4b) in the same session.
- **7 of 9** scans in `docs/scanner-catalog.md` used Path A; 2 used Path B (hermes-agent, postiz-app). Both methodologies are validated.
- Tag the catalog entry with `methodology-used: path-a`.

**Path-selection criterion (context-budget, not file-count).** Path A is viable when the operator's remaining context can hold:

`context.md + brief + DRAFT-or-reference + bundle + template-or-prior-scan + the edit loop`

If the context budget is exhausted or fragmented — if any of the six ingredients has already been squeezed out or is about to be — consider Path B.

### 8.2 Path B (delegated — exercised and validated)

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

The rendered output's required structural elements are specified by the V2.4 prompt (see `repo-deep-dive-prompt.md` §"What Should I Do?", §"What We Found", §"Executable File Inventory", etc.). This guide does not duplicate that specification.

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

An automated `--bundle-check` pass is explicitly **deferred to V0.2** (see DEFER list in `docs/board-review-operator-guide-consolidation.md`).

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

The pre-render checklist (§9.2.1) walks these items one-by-one. Until `--bundle-check` is built (deferred to V0.2), the operator walks the checklist manually before starting Phase 4a.

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
- **V0.2:** `--bundle-check` automation that audits the checklist programmatically. Deferred until one operator has hand-executed the manual checklist on ≥2 scans.

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
