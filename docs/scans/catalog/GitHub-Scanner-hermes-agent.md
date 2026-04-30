# Security Investigation: NousResearch/hermes-agent

**Investigated:** 2026-04-16 | **Applies to:** main @ 764536b · v0.10.0 | **Repo age:** 9 months | **Stars:** 93,679 | **License:** MIT

> A 93,000-star self-improving AI agent with strong CI defenses (SHA-pinned actions, custom supply-chain audit) but a governance gap: the ruleset on main prevents force-push but does not require reviews, and 0% of sampled PRs had any formal review. Five open security issues describe real attack surfaces in the sandbox and credential handling.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-hermes-agent.md` (+ `.html` companion) |
| Repo | [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| Short description | Self-improving AI agent with built-in learning loop, multi-model support, messaging gateway, and skill system. Ships via curl-pipe-bash installer, Docker, Nix, and PyPI. |
| Category | AI/LLM tooling |
| Subcategory | Agentic AI platform with learning loop |
| Verdict | **Caution** (split &mdash; see below) |
| Scanned revision | `main @ 764536b` (release tag `v0.10.0`, tagged v2026.4.16) |
| Prompt version | `v2.3` (post-R3) |
| Prior scan | None &mdash; first run on this repo |

---

## Verdict: Caution (split) &mdash; governance gap and open security issues

### Deployment &middot; Installing today &middot; v0.10.0 &mdash; **Install from a tagged release, not HEAD of main**

The primary install command `curl -fsSL .../main/scripts/install.sh | bash` fetches from HEAD of main. The ruleset on main prevents force-push and branch deletion but does NOT require PR reviews or status checks (F0). A compromised maintainer credential can push unreviewed code that immediately reaches new installs. Install from a tagged release instead and review the open sandbox/credential issues (F2) before running on sensitive systems.

### Version &middot; Evaluating the codebase &mdash; **Strong security awareness, real open vulnerabilities**

The codebase demonstrates above-average security consciousness: 100% SHA-pinned CI actions, a custom supply-chain-audit workflow that detects litellm-pattern attacks, CVE-aware dependency pinning, and Docker privilege dropping via gosu. However, five open security issues (#7071 sandbox escape, #8035 auth.json readable, #4427 /proc/environ bypass, #10693 OAuth PKCE leak, #11307 webhook spoofing) describe real attack surfaces. The 0% PR review rate (F4) means these gaps have no formal review gate.

### Verdict exhibits (grouped for reading speed)

**Open security vulnerabilities &mdash; 5 active issues, none fixed (3 findings: F0, F1, F2)**

1. **Governance &middot; F0** &mdash; Repo-level ruleset "protect-main" only prevents deletion and force-push. No review requirement, no status checks, no CODEOWNERS. Org-level rulesets unknown (admin:org scope gap). 0% of 15 sampled PRs had any review.
2. **Install surface &middot; F1** &mdash; curl-pipe-bash from HEAD of main (`scripts/install.sh`). Not pinned to a release tag or SHA.
3. **Runtime &middot; F2** &mdash; Five open security issues: sandbox PYTHONPATH injection leaking secrets (#7071), file_tools reading auth.json (#8035), /proc/environ env blocklist bypass (#4427), OAuth PKCE verifier leak (#10693), unauthenticated Telegram webhook spoofing (#11307).

**Strong positive signals (3 findings: F5, F6, F7)**

1. **CI &middot; F6** &mdash; 100% SHA-pinned GitHub Actions across 8 workflows. Custom supply-chain-audit.yml detects .pth files, base64+exec combos, obfuscated subprocess calls. No `pull_request_target` usage.
2. **Dependencies &middot; F7** &mdash; pyproject.toml pins ranges with explicit CVE comments. uv.lock for reproducible builds. Open issue #10695 tracks known CVEs.
3. **Agent rules &middot; F5** &mdash; AGENTS.md is a standard development guide with no AI-directed imperative language.

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | **No upstream gate** &mdash; 0% formal review rate, ruleset prevents force-push but not unreviewed merges |
| Do they fix problems quickly? | Open security issues spanning 1-22 days, none merged yet |
| Do they tell you about problems? | Partially &mdash; CVE comments in deps, public issue tracker, but no SECURITY.md for responsible disclosure |
| Is it safe out of the box? | **Caution** &mdash; install from tagged release, review sandbox/credential issues before sensitive use |

---

## 01 · What should I do?

### Step 1: Install from a tagged release, not HEAD of main

**Non-technical:** The main install command (`curl ... | bash`) grabs whatever is on the main branch right now. Since there is no review requirement on main, a bad actor who compromises the maintainer's GitHub credentials can push malicious code that you would immediately install. Instead, clone a specific tagged release.

```bash
# Instead of: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
# Do this:
git clone --depth 1 --branch v2026.4.16 https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
pip install -e ".[all]"
```

### Step 2: Review the open security issues before running on sensitive systems

**Non-technical:** The agent's code execution sandbox has a known escape path (#7071) where scripts can read your API keys. The file reading tool can access your auth tokens (#8035). If you are running this on a machine with valuable credentials, wait for these fixes or manually review the workarounds.

- Track [#7071](https://github.com/NousResearch/hermes-agent/issues/7071) (sandbox PYTHONPATH injection)
- Track [#8035](https://github.com/NousResearch/hermes-agent/issues/8035) (file_tools reads auth.json)
- Track [#4427](https://github.com/NousResearch/hermes-agent/issues/4427) (/proc/environ bypass)

### Step 3: If using Telegram webhooks, configure TELEGRAM_WEBHOOK_SECRET

**Non-technical:** Issue #11307 reports that Telegram webhook mode can accept spoofed messages if no secret is configured. Set the `TELEGRAM_WEBHOOK_SECRET` environment variable.

---

## 02 · What we found

### F0 &middot; Warning &middot; Active &mdash; Governance gap: no review gate on main

The repo-level ruleset "protect-main" (created 2026-03-20) prevents branch deletion and force-push on main. However, it does NOT require PR reviews or passing status checks before merge. No CODEOWNERS file exists. The classic branch protection API returns 404. Org-level rulesets could not be checked (admin:org scope gap &mdash; recorded as unknown, not absent).

With 93,679 stars, weekly releases shipping code to user machines, and a sole maintainer (teknium1, 82% of commits) who can merge directly, the trust chain for every install terminates at one set of credentials with no automated second-person check.

**Threat model (F13):** An attacker who phishes teknium1's GitHub credentials, compromises a stale session token, gains access via a malicious IDE extension, or exploits a GitHub OAuth vulnerability can push code directly to main. That code immediately reaches the curl-pipe-bash install path (F1) and Docker builds. The supply-chain-audit workflow would catch some patterns (.pth files, base64+exec) but not all conceivable payloads.

**Evidence:** `gh api repos/NousResearch/hermes-agent/branches/main/protection` returned 404. `gh api repos/NousResearch/hermes-agent/rulesets` returned one ruleset with only `deletion` and `non_fast_forward` rules. `gh api orgs/NousResearch/rulesets` returned 404 (scope gap). CODEOWNERS not found in 4 paths. **OSSF Scorecard is not indexed** for this repo (API returned 404), so no independent governance score is available as a cross-check.

**Action:** Enable required PR reviews on the protect-main ruleset. Add CODEOWNERS for scripts/install.sh, docker/, tools/, pyproject.toml.

### F1 &middot; Warning &middot; Active &mdash; Curl-pipe-bash install fetches from HEAD of main

The README's primary install path is:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

This fetches `scripts/install.sh` from the HEAD of the main branch. The script clones the repo at HEAD and runs `pip install`. Combined with F0 (no review gate), any push to main changes what new users install with no delay and no review.

Alternative install paths (Docker, Nix) are also tied to main branch pushes but have additional build verification (Docker smoke tests, Nix flake check).

**Evidence:** README.md lines 61-63, scripts/install.sh header.

**Action:** Pin the install URL to a tagged release SHA, or add checksum verification to the installer output.

### F2 &middot; Warning &middot; Active &mdash; Multiple open security vulnerabilities in sandbox and credential handling

Five open security issues describe real, reproducible attack surfaces:

1. **#7071** (filed 2026-04-10, open): Code execution sandbox injects the hermes-agent project root into PYTHONPATH, allowing sandboxed scripts to import `hermes_cli.config` and read LLM provider API keys.
2. **#8035** (filed 2026-04-12, open): `file_tools.read_file` path guards do not block `~/.hermes/auth.json` or `~/.hermes/mcp-tokens/`, allowing the LLM to read OAuth tokens.
3. **#4427** (filed 2026-04-01, open): Subprocess environment blocklist (`_sanitize_subprocess_env`) can be bypassed by reading `/proc/PARENT_PID/environ`, recovering stripped API keys.
4. **#10693** (filed 2026-04-16, open): Anthropic OAuth PKCE flow reuses the `code_verifier` as the `state` parameter, leaking the verifier via the authorization URL.
5. **#11307** (filed 2026-04-17, open): Telegram webhook mode accepts requests without validating `TELEGRAM_WEBHOOK_SECRET`, allowing unauthenticated update spoofing.

These issues span 1-17 days open with no merged fixes at scan time. The community is actively finding and reporting these vulnerabilities, but the triage/fix pipeline appears slow relative to the report rate.

**Evidence:** gh api search/issues for security keywords, individual issue reads.

**Action:** Triage and fix #7071 and #8035 first (credential exposure). #4427 requires a process isolation change (Docker/seccomp). #10693 and #11307 are lower blast radius but straightforward fixes.

### F3 &middot; Info &middot; Active &mdash; No security policy

The community profile shows `security_policy: false`. No SECURITY.md exists. With 93k stars and an active vulnerability disclosure community (see F2), reporters file security issues as regular public issues, making them visible to attackers before fixes ship.

**Evidence:** `gh api repos/NousResearch/hermes-agent/community/profile` &mdash; security_policy: false.

**Action:** Add SECURITY.md with private vulnerability reporting (GitHub's built-in private advisory feature or a security@nousresearch.com contact).

### F4 &middot; Info &middot; Active &mdash; Solo-maintainer commit concentration

teknium1 has 2,959 of ~3,600 commits (82%) and merged 13 of 15 sampled PRs with zero reviews. The NousResearch organization provides backing, and 29 other contributors are active, but day-to-day development bus factor is 1.

This is not inherently a security finding &mdash; many successful projects have a dominant maintainer. It becomes a concern because combined with F0 (no review gate), there is no formal check on the dominant contributor's commits.

**Evidence:** `gh api repos/NousResearch/hermes-agent/contributors?per_page=30`, PR review sample.

### F5 &middot; OK &middot; Informational &mdash; AGENTS.md is a standard development guide

AGENTS.md at the repo root contains project structure documentation and coding conventions for AI coding assistants. No imperative AI-directed language, no prompt injection attempts, no security concerns.

**Evidence:** `cat /tmp/scan-hermes-agent/src/AGENTS.md` &mdash; development guide content.

### F6 &middot; OK &middot; Informational &mdash; CI security posture is strong

All 8 CI workflows use SHA-pinned GitHub Actions (100% pinning rate). No `pull_request_target` trigger usage. The custom `supply-chain-audit.yml` workflow scans every PR diff for: .pth files (Python startup auto-execute), base64+exec combos (litellm attack pattern), obfuscated subprocess calls, outbound network calls, install hook modifications, and marshal/pickle deserialization. Tests run with API keys explicitly blanked.

This is the strongest CI security posture observed in 7 scans to date.

**Evidence:** grep of all .github/workflows/*.yml for `uses:` and `pull_request_target`.

### F7 &middot; OK &middot; Informational &mdash; Dependencies actively managed with CVE awareness

pyproject.toml pins 14 core dependencies to version ranges (e.g., `openai>=2.21.0,<3`) with inline CVE comments where applicable (`requests>=2.33.0,<3  # CVE-2026-25645`). uv.lock provides reproducible builds. Open issue #10695 tracks known CVEs in aiohttp, cryptography, and curl-cffi. No `setup.py` cmdclass overrides &mdash; standard setuptools build backend.

**Evidence:** pyproject.toml content, presence of uv.lock, issue #10695.

---

## 02A · Executable File Inventory

**Quick scan (14+ executables &mdash; includes install scripts, Docker entrypoint, skill helpers)**

| File | Verdict | Note |
|------|---------|------|
| `scripts/install.sh` | **Review** | Curl-pipe-bash target. Clones repo, sets up venv, runs pip install. F1 applies. |
| `setup-hermes.sh` | OK | Alternative setup, similar to install.sh |
| `docker/entrypoint.sh` | OK | Privilege-drops via gosu, bootstraps config, runs hermes |
| `scripts/install.ps1` | OK | Windows PowerShell installer |
| `scripts/install.cmd` | OK | Windows CMD wrapper |
| `scripts/kill_modal.sh` | OK | Modal cleanup utility |
| `scripts/release.py` | OK | Release automation (executable bit set) |
| `hermes` (root) | OK | Shell wrapper for CLI entry point |
| `skills/*/scripts/*.sh` | OK | Skill helper scripts (p5js, manim, github-auth, duckduckgo) |
| `environments/benchmarks/*/run_eval.sh` | OK | Benchmark runners |
| `hermes_cli/setup.py` | OK | CLI subpackage setup |

**Python entry points (console_scripts):**
- `hermes` &rarr; `hermes_cli.main:main` (primary CLI)
- `hermes-agent` &rarr; `run_agent:main` (agent entry)
- `hermes-acp` &rarr; `acp_adapter.entry:main` (ACP server)

**Docker:** `Dockerfile` with `ENTRYPOINT ["/opt/hermes/docker/entrypoint.sh"]`, gosu privilege dropping, smoke test in CI.

---

## 03 · Suspicious code changes

No suspicious code changes detected in the recent commit sample. All 15 sampled commits from 2026-04-16 are consistent with active development: feature additions (Gemini TTS, Gemini CLI OAuth), bug fixes (Discord RTP, approval panel clipping, checkpoint isolation), and maintenance (model catalog updates, release mapping).

The Step A grep found no `eval()` or `exec()` in source files. `subprocess` usage in cli.py is consistent with an AI agent that manages terminal backends and git operations. base64 usage is standard (JWT, PKCE, clipboard). No malicious patterns detected.

---

## 04 · Timeline

- **2025-07-22** &mdash; Repository created (START)
- **2026-03-12** &mdash; v0.2.0 first public release
- **2026-03-17** &mdash; v0.3.0
- **2026-03-20** &mdash; "protect-main" ruleset created (deletion + force-push protection)
- **2026-03-25** &mdash; Issue #3015: session file leak reported (VULN REPORTED)
- **2026-03-28** &mdash; v0.5.0
- **2026-03-30** &mdash; Issue #3971: missing token redaction patterns (VULN REPORTED)
- **2026-04-01** &mdash; Issue #4427: /proc/environ bypass (VULN REPORTED)
- **2026-04-08** &mdash; v0.8.0
- **2026-04-10** &mdash; Issue #7071: sandbox PYTHONPATH injection (VULN REPORTED)
- **2026-04-12** &mdash; Issue #8035: file_tools reads auth.json (VULN REPORTED)
- **2026-04-13** &mdash; v0.9.0
- **2026-04-16** &mdash; v0.10.0 released; Issues #10693 (OAuth PKCE) + #10695 (dep CVEs) filed; this scan (SCAN)
- **2026-04-17** &mdash; Issue #11307: Telegram webhook spoofing (VULN REPORTED)

The pattern shows vulnerability reports accelerating (7 in 23 days) while releases continue at weekly cadence. No fixes for the reported vulnerabilities have shipped in any release during this window.

---

## 05 · Repo vitals

| Metric | Value |
|--------|-------|
| Stars | 93,679 |
| Forks | 13,056 |
| Open issues | 4,986 |
| Contributors | 30+ |
| Releases | 9 (v0.2.0 to v0.10.0) |
| Release cadence | Weekly |
| Default branch | main |
| License | MIT |
| Language | Python |
| Topics | ai-agent, anthropic, claude, claude-code, clawdbot, codex, hermes, moltbot, openclaw, openai |
| Has CI | Yes (8 workflows) |
| Has tests | Yes (pytest, ~3000 tests per AGENTS.md) |
| Has Docker | Yes (multi-arch, published to Docker Hub) |
| Has Nix | Yes (flake with multi-OS matrix) |
| Commit signing | Partial (10/15 sampled commits GPG-verified) |
| Branch protection | Partial &mdash; ruleset prevents deletion/force-push, no review gate |
| CODEOWNERS | Absent |
| Security policy | Absent |
| Dependabot | Unknown (403 scope gap) |
| OSSF Scorecard | Not indexed (API returned 404) |

---

## 06 · Investigation coverage

| Check | Status | Notes |
|-------|--------|-------|
| Repo metadata (Step 1) | Complete | |
| Maintainer background (Step 1) | Complete | NousResearch org + top 3 contributors |
| Branch protection &mdash; classic (Step 1) | Complete | 404 on main |
| Branch protection &mdash; rulesets (Step 1) | Complete | 1 ruleset, deletion + non_fast_forward only |
| Org-level rulesets (C20) | **Reduced** | 404 + scope gap (needs admin:org) &mdash; recorded as unknown |
| CODEOWNERS (F14) | Complete | Not found in 4 paths |
| CI workflows (Step 2) | Complete | 8 files read |
| Agent-rule files (Step 2.5) | Complete | AGENTS.md found, no concerns |
| Dependencies (Step 3) | Complete | pyproject.toml + requirements.txt |
| Dependabot alerts | **Reduced** | 403 scope gap (needs admin:repo_hook) |
| Security advisories | Complete | Empty array |
| PR review rate (Step 4) | Complete | 15 sampled, 0% review rate |
| Security-relevant PRs (Step 5) | Partial | Sampled via issue search |
| Issues (Step 6) | Complete | 10 recent + security keyword search |
| Recent commits (Step 7) | Complete | 15 sampled |
| README install scan (Step 7.5) | Complete | curl-pipe-bash documented |
| Installed-artifact verification (Step 8) | Partial | Install script read, no SHA verification in installer |
| Dangerous-primitive grep (Step A) | Complete | Focused on root .py + agent/ + hermes_cli/ |
| Targeted read (Step B) | Complete | No actionable grep hits required deep reads |
| Executable inventory (Step C) | Complete | 14+ executables cataloged |
| OSSF Scorecard | Not indexed — API returned 404. Org-owned but not yet indexed by OSSF |
| osv.dev | Applicable — 14 core deps in pyproject.toml. CVE tracking via issue #10695 |
| Secrets-in-history | Not scanned (gitleaks not available) |
| API rate budget | 5000/5000 remaining. PR sample: 15 merged PRs |

---

## 07 · Evidence appendix

### Priority evidence

**E1: Branch protection and rulesets**

```
$ gh api repos/NousResearch/hermes-agent/branches/main/protection
{"message":"Not Found","status":"404"}

$ gh api repos/NousResearch/hermes-agent/rulesets
[{"id":14161644,"name":"protect-main","target":"branch","enforcement":"active",...}]

$ gh api repos/NousResearch/hermes-agent/rules/branches/main
[{"type":"deletion",...},{"type":"non_fast_forward",...}]

$ gh api orgs/NousResearch/rulesets
{"message":"Not Found","status":"404"}
(Token lacks admin:org scope)
```

**E2: PR review rate sample (0/15)**

```
All 15 most-recent merged PRs: reviewDecision=NONE, reviews=0
teknium1 authored 13/15, helix4u authored 2/15
```

**E3: Open security issues**

```
#7071: Sandbox PYTHONPATH injection (open since 2026-04-10)
#8035: file_tools reads auth.json (open since 2026-04-12)
#4427: /proc/environ bypass (open since 2026-04-01)
#10693: OAuth PKCE verifier leak (open since 2026-04-16)
#11307: Telegram webhook spoofing (open since 2026-04-17)
```

### Supporting evidence

**E4: CI action pinning audit**

All `uses:` directives across 8 workflow files reference SHA-pinned commits (e.g., `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5`). Zero unpinned actions found. Zero `pull_request_target` triggers.

**E5: Install script analysis**

`scripts/install.sh`: clones repo via HTTPS at HEAD of main branch, creates venv via uv, runs `pip install -e ".[all]"`. No checksum verification of downloaded content. Standard installation operations otherwise.

**E6: Dependency management**

`pyproject.toml` pins 14 core deps to ranges with CVE comments. `uv.lock` present. `requirements.txt` is unpinned convenience file (not canonical).

### Positive evidence

**E7: Supply-chain-audit workflow**

`supply-chain-audit.yml` scans every PR for: .pth files, base64+exec combos, obfuscated subprocess calls, outbound POST/PUT, setup hook modifications, marshal/pickle usage. This is a custom defense inspired by the litellm attack.

**E8: Docker security**

`docker/entrypoint.sh` drops root privileges via gosu, remaps UID/GID, creates isolated home directory for subprocesses. `docker-publish.yml` runs smoke tests before push.

**E9: AGENTS.md content**

Standard development guide with project structure, file dependency chain, coding conventions. No imperative AI-directed language.

---

## 08 · How this scan works

### What this scan is

This is an **LLM-driven security investigation** — an AI assistant with terminal access used the [GitHub CLI](https://cli.github.com/) and free public APIs to investigate this repo's governance, code patterns, dependencies, and distribution pipeline. It then synthesized its findings into this plain-English report.

This is **not** a static analyzer, penetration test, or formal security audit. It is a trust-assessment tool that answers: "Should I install this?"

### What we checked

| Area | Scope |
|------|-------|
| Governance & Trust | Branch protection, rulesets, CODEOWNERS, SECURITY.md, community health, maintainer account age & activity, code review rates |
| Code Patterns | Dangerous primitives (eval, exec, fetch), hardcoded secrets, executable file inventory, install scripts, README paste-blocks |
| Supply Chain | Dependencies, CI/CD workflows, GitHub Actions SHA-pinning, release pipeline, artifact verification |
| AI Agent Rules | CLAUDE.md, AGENTS.md, .cursorrules, .mcp.json — checked for prompt injection and behavioral manipulation |

### External tools used

| Tool | Purpose |
|------|---------|
| [OSSF Scorecard](https://securityscorecards.dev/) | Independent security rating. Scores 24 practices 0-10. Free API. |
| [osv.dev](https://osv.dev/) | Google-backed vulnerability database. Dependabot fallback. |
| [gitleaks](https://gitleaks.io/) (optional) | Scans code history for leaked secrets. Requires installation. |
| [GitHub CLI](https://cli.github.com/) | Primary data source for all repo metadata and API calls. |

### What this scan cannot detect

- **Transitive dependency vulnerabilities** — we check direct dependencies but cannot fully resolve the tree
- **Runtime behavior** — we see what the code *could* do, not what it *does* when running
- **Published artifact tampering** — we cannot verify published packages match this source
- **Sophisticated backdoors** — pattern-matching catches common primitives, not logic bombs
- **Container image contents** — we read Dockerfiles but cannot inspect built images

### Scan methodology version

Scanner prompt V2.3 (backfilled with V2.4 data) · Operator Guide V0.1 · Validator with XSS checks + verdict-severity coherence · [stop-git-std](https://github.com/stefans71/stop-git-std)
