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
| A JS/TS library (npm package, no installer) | `reference/GitHub-Scanner-zustand.html` |
| A compiled CLI with release binaries | `reference/GitHub-Scanner-fd.html` |
| An agentic platform with server + CLI + installer | `reference/GitHub-Scanner-Archon.html` |
| A curl-pipe-from-main installer / Claude plugin | `reference/GitHub-Scanner-caveman.html` |
| A dense Claude Code skills/tools distribution | `reference/GitHub-Scanner-gstack.html` |
| Not sure | Use `reference/GitHub-Scanner-fd.html` (most general) |

```
Reference scan: _______________
```

---

## Ready? Here's what happens next.

### If you chose Path A (run it yourself):

Read the Operator Guide and follow it phase by phase:

```
Open: SCANNER-OPERATOR-GUIDE.md
```

The 6 phases are:
1. **Prep** — create working dir, capture HEAD SHA (full 40-char), download tarball with `--no-absolute-names`, strip symlinks
2. **Gather** — run `gh api` calls + OSSF Scorecard + osv.dev per the V2.4 prompt (Steps 1-8 + A-pre/A/B/C)
3. **Bundle** — synthesize evidence into `findings-bundle.md`
4. **Render** — bundle → MD (Phase 4a) → HTML from MD (Phase 4b)
5. **Validate** — `python3 validate-scanner-report.py --report <file>` on HTML + `python3 validate-scanner-report.py --markdown <file>` on MD — both must exit 0
6. **Catalog** — update `scanner-catalog.md`

### If you chose Path B (delegate to an agent):

The handoff packet (§8.3 of the Operator Guide) consists of these files:

1. `SCANNER-OPERATOR-GUIDE.md` — process document
2. `repo-deep-dive-prompt.md` — what to investigate
3. `GitHub-Repo-Scan-Template.html` — template with placeholders
4. `validate-scanner-report.py` — validator gate
5. Your chosen reference scan (from Step 4 above)
6. The findings-bundle slot (agent creates this during Phase 3)

Use the reusable Path B prompt template:

```
Open: reference/path-b-test-prompt.md
```

Adapt it for your target repo, launch as a background agent.

---

## After the scan

Your scan produces `GitHub-Scanner-<repo>.{html,md}`. To use it:

**As a human reader:** open the `.html` in a browser.

**As a decision artifact:** paste the `.md` into your LLM and ask:
> "Based on this security scan, should I install this repo? What risks should I know about? What should I do before installing?"

**To add to the catalog:** update `scanner-catalog.md` with a new row.

---

## Reference files

| File | What it is | When you need it |
|---|---|---|
| `SCANNER-OPERATOR-GUIDE.md` | V0.2 end-to-end process | Always — your primary reference |
| `repo-deep-dive-prompt.md` | V2.4 investigation prompt | Phase 2 — tells you what to check |
| `GitHub-Repo-Scan-Template.html` | Template with placeholders + CSP | Phase 4 — structural scaffold |
| `scanner-design-system.css` | Mandatory CSS (824 lines) | Phase 4b — copy verbatim into HTML |
| `validate-scanner-report.py` | Validator (--report, --markdown, --template) | Phase 5 — must exit 0 |
| `scanner-catalog.md` | Live scan catalog | Phase 6 + reference |
| `CHANGELOG.md` | Version history V2.1→V2.4 | Reference |
| `reference/path-b-test-prompt.md` | Reusable Path B delegation prompt | Path B only |
| `reference/GitHub-Scanner-*.html` | 5 reference scans (different shapes) | Phase 4 — structural reference |

---

## Current catalog (10/10 — JSON-first Trigger #1 MET)

| Scan | Verdict | Shape |
|---|---|---|
| caveman | critical (split) | curl-pipe-from-main installer |
| Archon | caution (split) | agentic platform with open vulns |
| zustand | caution (split) | pure JS library, zero deps |
| fd | caution (split) | Rust CLI, multi-platform binaries, SLSA attestations |
| gstack | caution (split) | dense agent-rule surface, install-from-main + auto-update |
| archon-board-review | caution | tiny / self-scan / pre-distribution |
| hermes-agent | caution | Python platform, org-owned, open vulns |
| postiz-app | caution | web application, CVEs, Docker defaults |
| zustand (V2.4 re-scan) | clean | V2.4 methodology validation re-scan |
| Archon (re-run) | (determinism record) | re-run confirming verdict held across SHA bump |
