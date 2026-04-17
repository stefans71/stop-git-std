# stop-git-std

LLM-driven GitHub repo security scanner. Produces deep-dive investigation reports that tell non-engineers whether a repo is safe to install.

## How it works

An LLM (Claude, Codex, or any frontier model with `gh` CLI access) investigates a GitHub repo using a structured prompt, synthesizes findings into a bundle, and renders an HTML report + MD companion. The MD is designed to be pasted into any LLM for interactive "should I install this?" guidance.

**Not a static analyzer.** The scanner reads governance signals, PR review patterns, maintainer backgrounds, CI workflow security, install-path verification, and agent-rule file density — things that require judgment, not just pattern matching.

## Quick start

```bash
# Open this repo in Claude Code — CLAUDE.md auto-loads the project context
# Then follow the wizard:
cat docs/Scan-Readme.md
```

Or run directly:

```bash
# 1. Pick a target repo
TARGET="owner/repo"

# 2. Follow the 6-phase workflow in the Operator Guide
cat docs/SCANNER-OPERATOR-GUIDE.md

# 3. Validate your output
python3 docs/validate-scanner-report.py --report docs/GitHub-Scanner-<repo>.html
```

## What's in this repo

| Path | Purpose |
|---|---|
| `docs/Scan-Readme.md` | Interactive scan wizard — start here |
| `docs/SCANNER-OPERATOR-GUIDE.md` | V0.1 operator guide (board-reviewed) |
| `docs/repo-deep-dive-prompt.md` | V2.3 scanner prompt |
| `docs/GitHub-Repo-Scan-Template.html` | HTML template |
| `docs/validate-scanner-report.py` | Validator gate |
| `docs/scanner-catalog.md` | Live catalog of completed scans |
| `docs/GitHub-Scanner-*.{html,md}` | 6 completed scans |
| `CLAUDE.md` | Claude Code project context |

## Completed scans

| Repo | Verdict | What it tests |
|---|---|---|
| [caveman](docs/GitHub-Scanner-caveman.html) | critical | curl-pipe-from-main installer |
| [Archon](docs/GitHub-Scanner-Archon.html) | critical | agentic platform, open security PRs |
| [zustand](docs/GitHub-Scanner-zustand.html) | caution | pure JS library, zero runtime deps |
| [fd](docs/GitHub-Scanner-fd.html) | caution | Rust CLI, SLSA attestations |
| [gstack](docs/GitHub-Scanner-gstack.html) | caution | dense agent-rule surface (50 files) |
| [archon-board-review](docs/GitHub-Scanner-archon-board-review.html) | caution | tiny repo, self-scan |

## Governance

Every major change goes through a 3-model board review: Pragmatist (Claude Opus) + Systems Thinker (Codex) + Skeptic (DeepSeek V3.2). Board consolidation records are in `docs/board-review-*-consolidation.md`.

## License

MIT
