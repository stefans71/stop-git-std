# Scan Wizard — Run a GitHub Repo Security Scan

This wizard walks you through running a V2.3 deep-dive security scan on any public GitHub repo. Answer the questions below, then the scanner runs end-to-end.

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

## Step 3: Run it yourself or delegate?

| Path | How it works | When to use |
|---|---|---|
| **Path A** (default) | You (or your LLM session) run all 6 phases in one session | Smaller repos, learning the workflow |
| **Path B** (delegated) | Launch a fresh agent with the handoff packet — it runs independently | Larger repos, parallel work, testing the guide |

```
Execution path: A / B (default: A)
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

---

## Ready? Here's what happens next.

### If you chose Path A (run it yourself):

Read the Operator Guide and follow it phase by phase:

```
Open: docs/SCANNER-OPERATOR-GUIDE.md
```

The 6 phases are:
1. **Prep** — create working dir, capture HEAD SHA, download tarball
2. **Gather** — run `gh api` calls per the V2.3 prompt (Steps 1-8 + A/B/C)
3. **Bundle** — synthesize evidence into `findings-bundle.md`
4. **Render** — bundle → MD (Phase 4a) → HTML from MD (Phase 4b)
5. **Validate** — `python3 docs/validate-scanner-report.py --report <file>` until exit 0 on both
6. **Catalog** — update `docs/scanner-catalog.md`

### If you chose Path B (delegate to an agent):

The handoff packet (§8.3 of the Operator Guide) consists of these files:

1. `docs/SCANNER-OPERATOR-GUIDE.md` — process document
2. `docs/repo-deep-dive-prompt.md` — what to investigate
3. `docs/GitHub-Repo-Scan-Template.html` — template with placeholders
4. `docs/validate-scanner-report.py` — validator gate
5. Your chosen reference scan (from Step 4 above)
6. The findings-bundle slot (agent creates this during Phase 3)

Use the reusable Path B prompt template:

```
Open: docs/board-review-data/path-b-test-prompt.md
```

Adapt it for your target repo:
- Replace `pmndrs/zustand` with your target
- Replace `GitHub-Scanner-fd.html` with your chosen reference scan
- Replace the "Expected verdict" section with what you know about the repo
- Launch as a background agent

---

## After the scan

Your scan produces `docs/GitHub-Scanner-<repo>.{html,md}`. To use it:

**As a human reader:** open the `.html` in a browser.

**As a decision artifact:** paste the `.md` into your LLM and ask:
> "Based on this security scan, should I install this repo? What risks should I know about? What should I do before installing?"

**To add to the catalog:** update `docs/scanner-catalog.md` with a new row.

---

## Reference files

| File | What it is | When you need it |
|---|---|---|
| `docs/SCANNER-OPERATOR-GUIDE.md` | End-to-end process (552 lines) | Always — your primary reference |
| `docs/repo-deep-dive-prompt.md` | V2.3 investigation prompt (1078 lines) | Phase 2 — tells you what to check |
| `docs/GitHub-Repo-Scan-Template.html` | Template with placeholders (1870 lines) | Phase 4 — structural scaffold |
| `docs/validate-scanner-report.py` | Validator (288 lines) | Phase 5 — must exit 0 |
| `docs/scanner-catalog.md` | Live scan catalog (45 lines) | Phase 6 + Step 4 above |
| `docs/board-review-data/path-b-test-prompt.md` | Reusable Path B delegation prompt | Path B only |
| `docs/GitHub-Scanner-*.{html,md}` | 6 completed scans | Step 4 — structural reference |

---

## Current catalog (6/10 toward JSON-first migration)

| Scan | Verdict | Shape |
|---|---|---|
| caveman | critical | curl-pipe-from-main installer |
| Archon | critical | agentic platform with open vulns |
| zustand | caution | pure JS library, zero deps |
| fd | caution | Rust CLI, multi-platform binaries, SLSA attestations |
| gstack | caution (split) | dense agent-rule surface, install-from-main + auto-update |
| archon-board-review | caution | tiny / self-scan / pre-distribution |
