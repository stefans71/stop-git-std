# Path B Delegation Prompt — Template

This is a reusable template for delegating a scan to a fresh agent. Adapt the target repo, output paths, and reference scan for each use.

---

You are an LLM operator running the GitHub Scanner for the first time. Your ONLY instructions are the Operator Guide and the handoff packet described below. You have never seen a scan run before. Follow the guide exactly.

## Your mission

Run a V2.4 scan on `OWNER/REPO` following the Operator Guide end-to-end. Produce:
- `/tmp/scan-REPO/GitHub-Scanner-REPO.md`
- `/tmp/scan-REPO/GitHub-Scanner-REPO.html`

Both must pass validation:
- `python3 validate-scanner-report.py --markdown <md-file>`
- `python3 validate-scanner-report.py --report <html-file>`

## Handoff packet (§8.3 of the Operator Guide)

Read these files in this order — all files are in the same directory as this prompt:

1. **The Operator Guide** — `SCANNER-OPERATOR-GUIDE.md`. Your primary process document. Follow it phase by phase.
2. **The V2.4 prompt** — `repo-deep-dive-prompt.md`. What to investigate (Steps 1-8 + A-pre/A/B/C) and the required MD file structure.
3. **The template** — `GitHub-Repo-Scan-Template.html`. Replace all `{{PLACEHOLDER}}` tokens and delete all `EXAMPLE-START/END` blocks.
4. **The CSS** — `scanner-design-system.css` (824 lines). Copy verbatim into HTML `<style>` block.
5. **The validator** — `validate-scanner-report.py`. Your Phase 5 gate.
6. **MD structural reference** — `reference/GitHub-Scanner-zustand.md`. Match this section skeleton (numbered sections, status lines, evidence grouping).
7. **HTML structural reference** — Pick by shape from `reference/GitHub-Scanner-*.html`. Copy STRUCTURE, not content.
8. **The findings-bundle slot** — you will CREATE this at `/tmp/scan-REPO/findings-bundle.md` during Phase 3.

## Critical process rules

- MD is canonical. Produce MD first, derive HTML from it.
- Use full 40-char SHA. After tar: `--no-absolute-names` + strip symlinks (`find -type l -delete`).
- CSS: copy ENTIRE `scanner-design-system.css` (824 lines) verbatim into HTML `<style>`.
- Scorecard questions (exact 4): "Does anyone check the code?", "Do they fix problems quickly?", "Do they tell you about problems?", "Is it safe out of the box?"
- Use OSSF Scorecard API, osv.dev fallback, rate-limit budget check, gitleaks if available.
- Section numbering: `## 01 ·` through `## 08 ·` (plus `## 02A ·`).
- Section-status summary lines under every heading.
- Evidence priority grouping: ★ Priority → Context → Positives.
- Split-verdict when risk differs by audience (F4 rule).
- Section 08 (How This Scan Works) required in every report.
- Include vital-explainer blocks with links (securityscorecards.dev, osv.dev, gitleaks.io) in HTML coverage cells.
- Validator must exit 0 on BOTH files before delivery. The markdown validator checks verdict-severity coherence (Clean + Warnings = FAIL).

## Shape-matched reference scans

| Shape | Reference |
|---|---|
| JS/TS library | `reference/GitHub-Scanner-zustand.html` |
| Compiled CLI | `reference/GitHub-Scanner-fd.html` |
| Agentic platform | `reference/GitHub-Scanner-Archon.html` |
| Curl-pipe installer | `reference/GitHub-Scanner-caveman.html` |
| Agent skills package | `reference/GitHub-Scanner-gstack.html` |

Pick the closest shape. Match its structure, not its content.
