# Scan Wizard — Run a GitHub Repo Security Scan

This wizard walks you through running a V2.4 deep-dive security scan on any public GitHub repo. Answer the questions below, then the scanner runs end-to-end.

---

## Step 1: What repo do you want to scan?

Provide the `owner/repo` path (e.g., `pmndrs/zustand`, `garrytan/gstack`, `NousResearch/hermes-agent`).

```
Target repo: _______________
```

## Step 2: What output do you want?

| Option | What you get | Best for | Estimated cost |
|---|---|---|---|
| **A: Both** (default) | `.md` + `.html` | Full audit trail — MD for LLM consumption, HTML for human reading | ~120k tokens |
| **B: HTML only** | `.html` (MD produced as intermediate, not committed) | Human-readable report only | ~110k tokens |
| **C: MD only** | `.md` | Cheapest — paste into your LLM and ask "should I install this?" | ~80k tokens |

```
Output mode: A / B / C (default: A)
```

## Step 3: Execution mode — run it yourself or delegate?

| Mode | Legacy name | How it works | When to use |
|---|---|---|---|
| **continuous** (default) | Path A | You (or your LLM session) run all 6 phases in one session | Smaller repos, learning the workflow |
| **delegated** | Path B | Launch a fresh agent with the handoff packet — it runs independently | Larger repos, parallel work, testing the guide |

Catalog entries 1–10 are tagged with the legacy `methodology-used: path-a` / `path-b` flag values. Going forward the concept is "execution mode" with values `continuous` or `delegated`; the rename was done in 2026-04-19 to eliminate a naming collision with the two rendering pipelines in Step 4a below.

```
Execution mode: continuous / delegated (default: continuous)
```

## Step 4: Pick a reference scan (structural pattern)

Your scan will use a prior scan as its structural template. Pick the closest shape:

| Your repo looks like... | Use this reference |
|---|---|
| A JS/TS library (npm package, no installer) | `GitHub-Scanner-zustand.html` |
| A compiled CLI with release binaries | `GitHub-Scanner-fd.html` |
| An agentic platform with server + CLI + installer | `GitHub-Scanner-Archon.html` |
| A curl-pipe-from-main installer / Claude plugin | `GitHub-Scanner-caveman.html` |
| A dense Claude Code skills/tools distribution | `GitHub-Scanner-gstack.html` |
| A tiny / new / pre-distribution tool | `GitHub-Scanner-archon-board-review.html` |
| Not sure | Use `GitHub-Scanner-fd.html` (most general) |

```
Reference scan: _______________
```

## Step 4a: Rendering pipeline — V2.4 (recommended) or V2.5-preview (Step G only)?

| Pipeline | Status | When to use |
|---|---|---|
| **Workflow V2.4** (default, recommended) | Proven on all 10 catalog scans | Anything that will enter the catalog or be shown to a user |
| **Workflow V2.5-preview** | Step G validation in progress; renderer validated against back-authored fixtures only | Only if you are the Step G operator running against `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` §"Step G" |

```
Rendering pipeline: V2.4 / V2.5-preview (default: V2.4)
```

**⚠ V2.5-preview warnings (see also §8.8 of the Operator Guide):**
- Use only for Step G acceptance runs. Do NOT use for catalog or production scans.
- Only 3 shapes validated: JS library, curl-pipe installer, agentic platform monorepo. CLI-binary, Claude-Code-skills, web-app, Python-platform shapes NOT yet exercised.
- Output not considered catalog-grade until Step G passes.
- Last reviewed: 2026-04-19.

---

## Ready? Here's what happens next.

### If you chose continuous mode (run it yourself):

Read the Operator Guide and follow it phase by phase:

```
Open: docs/SCANNER-OPERATOR-GUIDE.md
```

The 6 phases are:
1. **Prep** — create working dir, capture HEAD SHA, download tarball
2. **Gather** — run `gh api` calls per the V2.4 prompt (Steps 1-8 + A-pre/A/B/C)
3. **Bundle** — synthesize evidence into `findings-bundle.md`
4. **Render** — for Workflow V2.4: bundle → MD (Phase 4a) → HTML from MD (Phase 4b). For Workflow V2.5-preview: bundle → form.json → `render-md.py` + `render-html.py` (§8.8).
5. **Validate** — `python3 docs/validate-scanner-report.py --report <file>` until exit 0 on both; V2.5-preview additionally requires `--parity` zero errors AND zero warnings
6. **Catalog** — update `docs/scanner-catalog.md`

### If you chose delegated mode (delegate to an agent):

The handoff packet (§8.3 of the Operator Guide) consists of these files:

1. `docs/SCANNER-OPERATOR-GUIDE.md` — process document
2. `docs/repo-deep-dive-prompt.md` — what to investigate + canonical output-format spec
3. Rendering-pipeline files:
   - V2.4: `docs/GitHub-Repo-Scan-Template.html` + `docs/scanner-design-system.css`
   - V2.5-preview: `docs/scan-schema.json` + `docs/render-md.py` + `docs/render-html.py` + `docs/templates/` + `docs/templates-html/`
4. `docs/validate-scanner-report.py` — validator gate
5. Your chosen reference scan (from Step 4 above)
6. The findings-bundle slot (agent creates this during Phase 3); for V2.5-preview also the form.json slot

Use the reusable delegated-mode prompt template:

```
Open: docs/delegated-scan-template.md
```

Adapt it for your target repo:
- Replace `pmndrs/zustand` with your target
- Replace `GitHub-Scanner-fd.html` with your chosen reference scan
- Replace the "Expected verdict" section with what you know about the repo
- If using V2.5-preview, add §8.8 Operator Guide reference + the fixture shape you're mirroring
- Launch as a background agent

---

## After the scan

Your scan produces `docs/scans/catalog/GitHub-Scanner-<repo>.{html,md}`. To use it:

**As a human reader:** open the `.html` in a browser.

**As a decision artifact:** paste the `.md` into your LLM and ask:
> "Based on this security scan, should I install this repo? What risks should I know about? What should I do before installing?"

**To add to the catalog:** update `docs/scanner-catalog.md` with a new row. Include the `rendering-pipeline` column (`v2.4` or `v2.5-preview`) alongside the existing `methodology-used` flag.

---

## Reference files

| File | What it is | When you need it |
|---|---|---|
| `docs/SCANNER-OPERATOR-GUIDE.md` | End-to-end process | Always — your primary reference |
| `docs/repo-deep-dive-prompt.md` | V2.4 investigation prompt + output-format spec | Phase 2 — what to check; output-format section (lines ~1106-1490) is the canonical rendering contract |
| `docs/GitHub-Repo-Scan-Template.html` | V2.4 HTML template with placeholders | Phase 4 (V2.4 only) — structural scaffold |
| `docs/scanner-design-system.css` | 824-line CSS, copy verbatim into V2.4 HTML | Phase 4 (V2.4 only) |
| `docs/scan-schema.json` | V1.1 schema for V2.5-preview form.json | Phase 4 (V2.5-preview only) — form shape |
| `docs/render-md.py` + `docs/render-html.py` | V2.5-preview deterministic renderers | Phase 4 (V2.5-preview only) |
| `docs/validate-scanner-report.py` | Validator (`--report`, `--parity`, `--markdown`, `--template`) | Phase 5 — must exit 0 |
| `docs/scanner-catalog.md` | Live scan catalog (10 V2.4 entries) | Phase 6 + Step 4 above |
| `docs/delegated-scan-template.md` | Reusable delegated-mode prompt template | Delegated mode only |
| `docs/scans/catalog/GitHub-Scanner-*.{html,md}` | 10 completed V2.4 scans | Step 4 — structural reference |
| `tests/fixtures/{zustand,caveman,archon-subset}-form.json` | V1.1-compliant back-authored form fixtures | V2.5-preview only — authoring reference |
| `docs/External-Board-Reviews/` | Archived 3-model board review records | Context for major decisions |

---

## Current catalog (10/10 V2.4 scans — Step G is the first V2.5-preview entry)

| Scan | Verdict | Shape |
|---|---|---|
| caveman | critical | curl-pipe-from-main installer |
| Archon | critical | agentic platform with open vulns |
| zustand | caution | pure JS library, zero deps |
| fd | caution | Rust CLI, multi-platform binaries, SLSA attestations |
| gstack | caution (split) | dense agent-rule surface, install-from-main + auto-update |
| archon-board-review | caution | tiny / self-scan / pre-distribution |
| hermes-agent | — | delegated-mode validated shape |
| postiz-app | — | delegated-mode validated shape |
| agency-agents | — | — |
| open-lovable | — | — |

Step G's first live V2.5-preview scan becomes entry #11 with `rendering-pipeline: v2.5-preview` in the catalog.
