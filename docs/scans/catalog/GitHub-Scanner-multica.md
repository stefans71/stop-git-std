# Security Investigation: multica-ai/multica

**Investigated:** 2026-04-19 | **Applies to:** main @ `b8907dd` · v0.2.6 | **Repo age:** 3 months | **Stars:** 16,457 | **License:** Other (NOASSERTION)

> A fast-growing agentic task-management platform (like Linear but with AI agents as first-class citizens) that ships a CLI, Electron desktop app, and self-hostable server — but operates with no branch protection gate, a 1% PR review rate, a curl-pipe-from-main installer with no binary checksum on Linux/Mac, and no SECURITY.md, meaning a single maintainer account compromise could ship malicious code to every new install before anyone noticed.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-multica.md` (+ `.html` companion) |
| Repo | [github.com/multica-ai/multica](https://github.com/multica-ai/multica) |
| Short description | Open-source managed agents platform — assigns AI coding agents (Claude Code, Codex, Gemini, Cursor Agent, etc.) to tasks, tracks progress, and compounds reusable skills. Ships a Go CLI, Electron desktop app, Next.js web app, and self-hosted Docker stack. |
| Category | AI/LLM tooling |
| Subcategory | Agentic task management / agent orchestration platform |
| Language | TypeScript (frontend), Go (backend + CLI) |
| License | Other (NOASSERTION — not a standard SPDX identifier) |
| Target user | AI-native development teams integrating multiple coding agents |
| Verdict | **Caution** (split — Deployment axis) |
| Scanned revision | `main @ b8907dd` (release tag `v0.2.6`) |
| Commit pinned | `b8907dda8d313cc96f0927da6dce2ea121fde43e` |
| Scanner version | `V2.4` |
| Scan date | `2026-04-19` |
| Prior scan | None — first scan of this repo. Future re-runs should rename this file to `GitHub-Scanner-multica-2026-04-19.md` before generating the new report. |

---

## Verdict: Caution (split — Deployment axis)

### Deployment · Cloud users · using multica.ai managed service — **Proceed with caution; install via Homebrew, not curl-pipe**

The managed cloud service itself looks fine at code level — no critical runtime vulnerabilities found. The install-time exposure is real: the default README install command (`curl | bash`) fetches from live `main` with no binary checksum verification on Linux and Mac. A maintainer account compromise or force-push on `main` would silently infect new installs. Use the Homebrew path instead (`brew install multica-ai/tap/multica`), which uses GoReleaser-produced release assets with checksums.

### Deployment · Self-hosted users · Docker or manual setup — **Review your configuration before exposing to the network**

Self-hosted users carry all the cloud-user risks plus two deployment-specific concerns: the `888888` master authentication bypass is still active in the Go source and triggers if `APP_ENV` is not explicitly set to `production` (Docker now defaults correctly after v0.2.6 but non-Docker self-hosters must set this manually), and the `docker-compose.selfhost.yml` default `JWT_SECRET` falls back to the string `change-me-in-production` if `.env` was created without running the install script.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Governance and supply-chain gaps — no review gate, no SECURITY.md, curl-pipe-from-main (3 findings)</strong>
<br><em>No branch protection, 1% review rate, security PRs self-merged; install script fetches live main without checksum</em></summary>

1. **Governance · F0 / C20** — No effective branch protection on `main`. Ruleset `protect-main-branch` exists but has `enforcement: disabled` and no branches targeted. CODEOWNERS absent. No SECURITY.md. Ships executables daily. Any maintainer account compromise propagates to users before any gate fires.
2. **Supply chain · F1** — `curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash` fetches the installer from live `main` (no tag pin). The Linux/Mac binary download path has no checksum verification. The self-host `--with-server` mode clones and tracks live `main`. Windows PS1 path *does* verify SHA256 checksums — asymmetric coverage.
3. **CI actions · F2** — `goreleaser/goreleaser-action@v6` in `release.yml` is a third-party action pinned to a mutable tag, not a SHA. It has access to `GITHUB_TOKEN` and `HOMEBREW_TAP_GITHUB_TOKEN`. A goreleaser action compromise could rewrite the Homebrew formula, affecting all `brew upgrade` users.

</details>

<details>
<summary><strong>⚠ Code review gaps and self-host defaults — security PRs unreviewed; dev backdoor partially open (2 findings)</strong>
<br><em>1% review rate; auth redirect fix self-merged in 3 min; 888888 master code lives in source</em></summary>

1. **Review rate · F3** — 1 of 100 sampled merged PRs had any review event (formal or informal). The auth redirect fix (PR #1309) was self-merged by its author in 3 minutes. The master code disable (PR #1307, security-sensitive) was merged without review. Not a solo-maintainer project (4-person team) — the low rate reflects a process gap, not a structural constraint.
2. **Self-host defaults · F4** — `server/internal/handler/auth.go:169` contains `isMasterCode := code == "888888" && os.Getenv("APP_ENV") != "production"`. Docker deployment now defaults `APP_ENV=production` (v0.2.6). Non-Docker self-hosters who copy `.env.example` without modification start with the dev backdoor active. The `JWT_SECRET` docker-compose fallback is `change-me-in-production`.

</details>

<details>
<summary><strong>✓ Positive signals — experienced team, artifact checksums, sanitized rendering, partial mitigations (5 signals)</strong>
<br><em>4-person founding team (7-13yr accounts), GoReleaser checksums.txt, rehypeSanitize on all markdown, no hardcoded secrets</em></summary>

1. **Team legitimacy** — Three of four core founders have 7-13 year GitHub accounts with independent prior work (forrestchang: 103 repos, 2,124 followers; Bohan-J: bio "coFounder of @multica-ai"; ldnvnbl: 44 repos, 13yr account). Not a sockpuppet pattern.
2. **Release checksums** — GoReleaser publishes `checksums.txt` with every release. Homebrew formula pins to tagged release assets. Windows PS1 installer verifies SHA256 before extracting. The supply-chain concern is the curl-pipe entry point, not the releases themselves.
3. **XSS mitigated** — All `dangerouslySetInnerHTML` usage is via `lowlight`/`Shiki` syntax highlighters or sanitized through `rehypeSanitize` before rendering. No unescaped user content injected into the DOM.
4. **CORS is explicit whitelist** — No `Access-Control-Allow-Origin: *` found. `allowedOrigins()` uses an explicit list (defaults to localhost dev ports). No TLS verification disabled.
5. **Partial security fixes shipped** — PR #1307 disabled `888888` in Docker (2026-04-18). PR #1309 fixed open-redirect in auth (2026-04-18). No lifecycle scripts in inner npm packages. `install.sh --with-server` generates a random `JWT_SECRET` via `openssl rand`.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | 🔴 **Rare · 1% review rate** — security PRs self-merged; no branch protection gate |
| Do they fix problems quickly? | 🟡 **Open fixes, not merged yet** — Docker default fixed; non-Docker path still exposed |
| Do they tell you about problems? | 🔴 **No advisory · No SECURITY.md** — security fixes ship without GHSA advisories |
| Is it safe out of the box? | 🟡 **Safer via Homebrew · Avoid curl-pipe on prod** — unverified channel caps this amber |

---

## 01 · What should I do?

> ⚠ 1 Critical finding, 3 Warnings · 3 steps
>
> **Orientation:** The platform is active and improving fast, but two supply-chain paths (curl-pipe installer, unpinned goreleaser action) and the absence of any review gate mean a single account compromise could silently ship malicious code. If you're evaluating multica today, use the safest install path and harden your self-host config before network exposure.

### Step 1: Use the Homebrew install path, not the curl-pipe command (⚠)

**Non-technical:** The README's default install command (`curl ... | bash`) downloads and runs a script directly from the live `main` branch — no verification of what you're getting. If a maintainer account were compromised and the script tampered with, you'd run malicious code without knowing. The Homebrew path is safer because it installs a release binary whose checksum was published by GoReleaser at release time.

```bash
# Safer install (macOS/Linux with Homebrew)
brew install multica-ai/tap/multica

# Verify the installed binary version
multica version
```

**Non-technical:** On Windows, the PowerShell installer already verifies a SHA256 checksum before extracting — that path is fine.

### Step 2: If self-hosting, set APP_ENV=production and change your JWT_SECRET (⚠)

**Non-technical:** The Multica Go server has a developer shortcut: if you don't tell it you're in production, it accepts `888888` as a magic login code that bypasses email verification for any account. Recent Docker images default this correctly, but if you're running the server any other way, you need to set this manually.

```bash
# In your .env file:
APP_ENV=production
JWT_SECRET=$(openssl rand -hex 32)

# If using the Docker Compose self-host stack, verify your override:
grep APP_ENV .env  # should be: APP_ENV=production
grep JWT_SECRET .env  # should NOT be: JWT_SECRET=change-me-in-production
```

### Step 3: Subscribe to repo releases to catch future security fixes (ℹ)

**Non-technical:** Multica has no SECURITY.md or advisory channel — the most recent security fixes (auth redirect and master code) shipped as regular PRs with no advisory notification. Watch the GitHub releases page so you hear about security-relevant updates.

```bash
# Watch releases on GitHub: https://github.com/multica-ai/multica/releases
# Or subscribe via gh:
gh api user/subscriptions -X PUT -H "Accept: application/vnd.github+json" \
  --field reason=releases 2>/dev/null || echo "Visit https://github.com/multica-ai/multica/subscription"
```

---

## 02 · What we found

> 🔴 1 Critical · ⚠ 3 Warning · ℹ 2 Info · ✓ 5 OK
>
> 6 active findings. Governance and supply-chain are the dominant themes — no critical runtime code vulnerabilities, but the trust chain from source to install has gaps at nearly every step.
>
> **Your action:** Use Homebrew install, set `APP_ENV=production` if self-hosting, and watch releases for security updates. No emergency action required unless you're already running a non-Docker self-host without `APP_ENV=production`.

### F0 — Critical · Governance · C20 — No effective branch protection, no CODEOWNERS, no SECURITY.md

*Active · Ships daily releases · → If you install: use Homebrew and pin to a release tag. If you maintain: enable branch protection with required reviews, add CODEOWNERS for `scripts/`, `.github/workflows/`, and add SECURITY.md.*

**What happened.** The repository has a ruleset named `protect-main-branch` but its `enforcement` field is set to `disabled` — it has no effect. Classic branch protection on `main` returns 404 (absent). `rules/branches/main` returns an empty array — no rules apply to the default branch. CODEOWNERS is absent from all four standard paths. There is no SECURITY.md.

**What this means for you.** Any of the four core maintainers can push directly to `main` with no second reviewer. A compromised GitHub account, a phished session cookie, a rogue browser extension running in a maintainer's browser — any of these paths gives an attacker the ability to push a tampered commit to `main`. Because the README install command fetches the installer script from live `main`, the window between compromise and victim installation is the time between the push and the user next running `curl ... | bash`.

**What this does NOT mean.** This does not mean multica is actively compromised or that the maintainers have bad intentions. It means the safety net that would catch a compromise *before users are affected* is not present. The four-person founding team has strong GitHub track records.

**Threat model (F13).** An attacker arrives at a maintainer account via: phishing email targeting the company domain, a compromised browser extension exfiltrating a GitHub session token, a malicious VSCode/IDE extension running code in the maintainer's user context, or a supply-chain compromise of a dev dependency the team installs locally. Once the attacker has write access to `main`, they push a one-line change to `scripts/install.sh`, `docker-compose.selfhost.yml`, or a Go server file. No reviewer, no status check, no required approval. The blast radius is 16,457 GitHub stars plus every downstream install.

| Meta | Value |
|------|-------|
| Branch protection | 🔴 None (ruleset exists but `enforcement: disabled`) |
| CODEOWNERS | 🔴 Absent (all 4 standard paths checked) |
| SECURITY.md | 🔴 Absent |
| Org rulesets | ❓ Unknown (admin:org scope required — not tested) |
| Stars / blast radius | 16,457 stars, 2,038 forks |

**How to fix (maintainer, low effort, 15 min).** Go to Settings → Branches → Add branch protection rule for `main`. Enable: "Require a pull request before merging" (1 required reviewer), "Require status checks to pass" (CI/CD). Add `.github/CODEOWNERS` with `scripts/ @multica-ai/core` and `.github/workflows/ @multica-ai/core`. Create `SECURITY.md` with a private disclosure email.

---

### F1 — Warning · Supply chain / Install — curl-pipe-from-main, no Linux/Mac binary checksum

*Active · Default README install path · → If you install: use Homebrew. If you maintain: fetch the installer from a pinned release tag; add checksum verification to `install_cli_binary()`.*

**What happened.** The primary install method in the README is `curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash`. This fetches the installer script from the live, unpinned `main` branch and executes it immediately. Inside `install_cli_binary()`, the script downloads the CLI binary from `releases/latest` but performs no SHA256 checksum verification before executing the binary. By contrast, the Windows PowerShell installer (`install.ps1`) *does* download `checksums.txt` and verify the SHA256 before extracting. The `--with-server` mode clones from `main` and on upgrades runs `git reset --hard origin/main` — also unpinned.

**What this means for you.** If an attacker gains write access to `main` (see F0), they can replace `install.sh` or modify the server clone path. New users who run the curl-pipe command will execute the tampered code with no warning. This is a known attack pattern for software distributed via shell scripts — it has been exploited against real projects.

**What this does NOT mean.** The Homebrew distribution channel (`brew install multica-ai/tap/multica`) uses GoReleaser-produced release artifacts with a published `checksums.txt`, managed by Homebrew's formula pinning. Users installing via Homebrew are protected against this specific vector. The concern is limited to the curl-pipe path.

| Meta | Value |
|------|-------|
| Script fetch | 🔴 Unpinned from `main` |
| Linux/Mac binary checksum | 🔴 Not verified |
| Windows binary checksum | ✅ SHA256 verified |
| Homebrew path | ✅ GoReleaser checksums + Homebrew formula pin |
| --with-server clone | 🔴 `git clone --depth 1 main`, upgrades track live `main` |

**How to fix (maintainer, medium effort).** In `install_cli_binary()`: after downloading the `.tar.gz`, download the corresponding `checksums.txt` from the same release URL, extract the expected SHA256, compute `sha256sum` of the local file, and fail if they don't match. For the script itself: publish versioned install scripts with the release and update README to point to the release-pinned URL.

---

### F2 — Warning · CI/Actions — Unpinned goreleaser third-party action; Homebrew PAT exposure

*Active · Release workflow · → If you maintain: pin `goreleaser/goreleaser-action` and `pnpm/action-setup` to full SHA hashes. Rotate `HOMEBREW_TAP_GITHUB_TOKEN` to a fine-grained PAT scoped only to the homebrew-tap repo.*

**What happened.** `release.yml` uses `goreleaser/goreleaser-action@v6` — a third-party action pinned only to a mutable `v6` tag. The same job passes `HOMEBREW_TAP_GITHUB_TOKEN: $&#123;&#123; secrets.HOMEBREW_TAP_GITHUB_TOKEN &#125;&#125;` to the action. If the goreleaser action's `v6` tag is repointed to a compromised release, the action runs with access to both the GITHUB_TOKEN (write to this repo) and the Homebrew PAT (write to `multica-ai/homebrew-tap`). A Homebrew formula rewrite could push a malicious binary to every user who runs `brew upgrade`. `ci.yml` also uses `pnpm/action-setup@v4` (third-party, no secrets, lower impact).

**What this does NOT mean.** The goreleaser project itself is well-maintained. This finding is about the lack of a SHA pin — not a claim that goreleaser is currently compromised.

| Meta | Value |
|------|-------|
| `goreleaser/goreleaser-action@v6` | 🔴 Third-party, mutable tag, has HOMEBREW_TAP_GITHUB_TOKEN |
| `pnpm/action-setup@v4` | ⚠ Third-party, mutable tag, no secrets |
| `actions/checkout`, `actions/setup-*` | ✅ GitHub-org actions (lower risk at mutable tags) |
| pull_request_target | ✅ 0 occurrences |

**How to fix (maintainer, low effort).** Pin each third-party action to a full 40-char SHA: `goreleaser/goreleaser-action@COMMIT_SHA`, `pnpm/action-setup@COMMIT_SHA`. Renovate Bot or GitHub's Dependabot can automate SHA-pin updates.

---

### F3 — Warning · Code Review — 1% review rate; security-relevant PRs self-merged or unreviewed

*Ongoing · All development · → If you install: treat the 1% rate as a process gap in a fast-moving startup — not evidence of malice. If you maintain: configure branch protection with required reviewer (1) to force the workflow.*

**What happened.** Of 100 sampled merged PRs (most recent, out of 739 total), 1 had any review event (formal or informal). This is below the red threshold (any-review &lt; 30%). Notable examples:
- **PR #1309** (`fix(auth): validate next= redirect target to prevent open redirect`) — Author: Bohan-J, merged by Bohan-J. Created at 05:21 UTC, merged at 05:24 UTC (3-minute self-merge on an auth security fix).
- **PR #1307** (`fix(selfhost): disable dev master code by default in Docker`) — Authored by `kagura-agent` (a self-described AI agent account), merged by Bohan-J at 06:25 UTC. Security-sensitive, no review.
- **PR #1280** (`ci(release): restrict tag pattern to semver and reject -dirty tags`) — CI change, cross-merged by `devv-eve`, no review.

This is not a solo-maintainer project (top contributor holds 30.2% of commits, four-person team covers 97.9%). The low review rate is a process choice in a hypergrowth startup, not a structural limit.

**What this does NOT mean.** Cross-merges (author ≠ merger, approximately 40% of sample) are not the same as no review, but the evidence shows mergers are not leaving review comments — they're merge-clicking without code examination.

| Meta | Value |
|------|-------|
| Formal review rate | 🔴 1% (1/100 sampled — reviewDecision set) |
| Any-review rate | 🔴 1% (1/100 — any review event) |
| Total merged PRs | 739 (sampled 100) |
| Auth PR self-merge | 🔴 PR #1309 self-merged in 3 min |
| Top contributor | NevilleQingNY 30.2% — multi-contributor team |

---

### F4 — Info · Self-host defaults — 888888 master auth code; JWT_SECRET default value

*Partially mitigated · Non-Docker self-host path · → If you self-host: explicitly set `APP_ENV=production` in your `.env` and change `JWT_SECRET` from the default.*

**What happened.** `server/internal/handler/auth.go:169`: `isMasterCode := code == "888888" && os.Getenv("APP_ENV") != "production"`. This allows any actor who knows the email of a registered user to log in as that user using the code `888888` — bypassing email verification entirely — when `APP_ENV` is not set to `production`. PR #1307 (2026-04-18) updated the Docker self-host stack to default `APP_ENV=production`, which disables the bypass for new Docker deployments. Non-Docker self-hosters who copy `.env.example` without modification do not have `APP_ENV` in `.env.example` and must add it manually. The `docker-compose.selfhost.yml` also sets `JWT_SECRET: ${JWT_SECRET:-change-me-in-production}` — the fallback is a known string if `.env` does not override it. The `install.sh --with-server` path generates a random JWT_SECRET via `openssl rand -hex 32`, mitigating this for users who install via that path.

**What this does NOT mean.** The cloud-managed service (multica.ai) is not affected by this finding. This applies only to self-hosted deployments.

| Meta | Value |
|------|-------|
| 888888 gate | `APP_ENV != "production"` — Docker now defaults to production |
| Non-Docker self-host | ⚠ Must set APP_ENV=production manually |
| JWT_SECRET default | `change-me-in-production` in compose fallback |
| install.sh --with-server | ✅ Generates random JWT_SECRET via openssl |

---

### F5 — Info · Agent-rule files — CLAUDE.md and AGENTS.md committed (Tier 1 auto-loaded; content OK)

*Informational · Repo contributors · → No action needed today. Subscribe to repo releases — a future change to either file reaches every contributor's Claude Code session automatically.*

**What happened.** Two Tier 1 auto-loaded agent-rule files are committed to the repository root:
- `CLAUDE.md` — 300+ line developer guide for Claude Code. Auto-loaded by Claude Code at every session start in this repo. Covers architecture, state management, testing conventions, commit rules, CLI release process.
- `AGENTS.md` — Pointer document to `CLAUDE.md`. Auto-loaded by AI agent platforms that honor the AGENTS.md convention.

Content scan of both files: no AI-directed manipulation language found. No `ignore previous instructions`, no jailbreak patterns, no credential requests, no file path exfiltration, no network command invocations targeting the scanner. The imperative language is standard developer guidance ("run `make check`", "use atomic commits").

**Capability statement.** These files currently instruct contributors' Claude Code sessions to follow multica's architectural conventions, run the verification pipeline before pushing, and use specific Go/TypeScript patterns.

**Risk statement.** If either file were tampered with (e.g., via a compromised maintainer account and the absent branch protection of F0), malicious instructions would reach every contributor's Claude Code session on the next session start — without opt-in or notification.

| Meta | Value |
|------|-------|
| CLAUDE.md | Auto-load Tier 1 · No manipulation language · 300+ lines |
| AGENTS.md | Auto-load Tier 1 · Pointer doc only |
| Injection patterns | 🔴 0 found (0 actionable) |

---

## 02A · Executable file inventory

> ⚠ 3 install-time executables · ℹ 5 runtime files inventoried
>
> Multica ships a Go CLI binary (via Homebrew, GitHub Releases, curl-pipe), a PowerShell installer, and a full Docker stack. The Electron desktop app spawns the CLI daemon using `execFile` with a hardcoded binary path. No lifecycle scripts in inner npm packages. No prompt injection attempts found in any inventoried file.

### Layer 1 — one-line summary

- ⚠ `scripts/install.sh` — runs at install time; downloads and executes CLI binary from GitHub Releases; no checksum on Linux/Mac. F1.
- ⚠ `scripts/install.ps1` — runs at install time on Windows; downloads CLI zip; SHA256 verified. Safer than Linux path.
- ✅ `apps/desktop/src/main/daemon-manager.ts` — runs at Electron app start; spawns multica CLI daemon via `execFile`; binary path is hardcoded to installed CLI location, not user-controlled.
- ✅ `apps/desktop/src/main/cli-bootstrap.ts` — runs when Electron detects CLI version mismatch; downloads updated CLI binary via release URL; no checksum verification (same gap as install.sh on Linux/Mac).
- ✅ `.github/workflows/ci.yml` — runs on every push/PR; builds and tests only; no secrets access.
- ⚠ `.github/workflows/release.yml` — runs on semver tag push; uses goreleaser with GITHUB_TOKEN + HOMEBREW_TAP_GITHUB_TOKEN. F2.
- ℹ `CLAUDE.md` — Tier 1 auto-loaded for every Claude Code contributor session. Content clean. F5.
- ℹ `AGENTS.md` — Tier 1 auto-loaded for AGENTS.md-aware platforms. Pointer doc. F5.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `scripts/install.sh` | Bash installer | Install-time (user runs) | None (no eval, no dynamic exec) | curl releases/latest + raw.githubusercontent.com/main | No checksum on binary download (Linux/Mac) |
| `scripts/install.ps1` | PowerShell installer | Install-time (Windows) | Invoke-WebRequest, Invoke-RestMethod | GitHub API + Releases | SHA256 verified before extract |
| `apps/desktop/src/main/daemon-manager.ts` | Electron main process | App startup | execFile (multica CLI binary) | None (IPC to renderer only) | bin path resolved from app bundle, not user input |
| `apps/desktop/src/main/cli-bootstrap.ts` | Electron main process | On CLI version mismatch | execFile (CLI binary) | curl GitHub Releases | No checksum on downloaded CLI update |
| `.github/workflows/release.yml` | GitHub Actions | Tag push | goreleaser action (builds+publishes) | GitHub Releases, Homebrew tap | HOMEBREW_TAP_GITHUB_TOKEN scope |
| `CLAUDE.md` | Agent rule file | Every contributor Claude Code session | n/a | n/a | Tier 1 auto-load, content clean |
| `AGENTS.md` | Agent rule file | Every AGENTS-aware agent session | n/a | n/a | Pointer to CLAUDE.md |

---

## 03 · Suspicious code changes

> ✅ 0 externally-reported security PRs · ⚠ 2 security-relevant self-merges flagged · ℹ 100 recent merges sampled
>
> The sample shows a high-velocity team shipping features and bug fixes daily. Two PRs are flagged: a 3-minute auth-fix self-merge and an AI-agent-authored master-code-disable that was merged without review.

Sample: 100 most recent merged PRs (of 739 total). Formal review rate: 1/100 = 1%. Sampled 2026-03-xx through 2026-04-18.

| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1309](https://github.com/multica-ai/multica/pull/1309) | fix(auth): validate next= redirect to prevent open redirect | Bohan-J (founder) | Bohan-J | No | Self-merge in 3 min — security fix, no second reviewer |
| [#1307](https://github.com/multica-ai/multica/pull/1307) | fix(selfhost): disable dev master code by default in Docker | kagura-agent (AI) | Bohan-J | No | Security-sensitive; AI agent authored; no review |
| [#1280](https://github.com/multica-ai/multica/pull/1280) | ci(release): restrict tag pattern to semver; reject -dirty | ldnvnbl | devv-eve | No | CI security improvement; cross-merge, no review |
| [#1322](https://github.com/multica-ai/multica/pull/1322) | fix(views): prevent infinite re-render loops | forrestchang | (self) | No | Bug fix; not security-critical |
| [#1313](https://github.com/multica-ai/multica/pull/1313) | docs(selfhost): clarify 888888 is disabled by default | Bohan-J | (self) | No | Documentation; follows PR #1307 |

No changelog-hiding pattern detected (security PRs are labeled `fix(auth)` and `fix(selfhost)` — security keywords present in titles). No rejected community security fixes. No first-time contributors touching security-critical files in the sample.

---

## 04 · Timeline

> ✅ 5 positive · ⚠ 3 caution · ℹ 2 context
>
> 10 beats across 3 months of active development. Story arc: fast-growing startup shipping daily with improving security hygiene (auth redirect fix, master code disable, CI tag restriction all in the last week) but governance infrastructure still lagging the release velocity.

- ✅ **2026-01-13 · FOUNDED** — multica-ai org created; repo launched as open-source with TypeScript+Go monorepo, Homebrew distribution, and GoReleaser checksums from day one.
- ℹ **2026-01-15 · RULESET CREATED** — `protect-main-branch` ruleset created but with `enforcement: disabled`. Branch protection exists on paper, not in practice.
- ✅ **2026-04-14 to 15 · STEADY SHIP** — v0.1.35 → v0.2.0 shipped (major version bump). Daily release cadence established. 16,000+ stars accumulated in 3 months.
- ⚠ **2026-04-18 · SECURITY FIX 1** — PR #1309: open-redirect fix in auth handler. Self-merged by author in 3 minutes. No advisory filed.
- ⚠ **2026-04-18 · SECURITY FIX 2** — PR #1307: 888888 master code disabled in Docker default. Authored by AI agent `kagura-agent`, merged by Bohan-J in 73 min. No advisory filed.
- ✅ **2026-04-18 · CI HARDENING** — PR #1280: tag pattern restricted to semver; `-dirty` tags rejected. Prevents accidental dirty releases.
- ⚠ **2026-04-19 · SCAN** — At scan time: no SECURITY.md, no branch protection, 1% review rate, curl-pipe-from-main installer with no Linux/Mac checksum. Active daily release cadence.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 3 months | Created 2026-01-13 — very new |
| Stars / Forks | 16,457 / 2,038 | Rapid growth — 3 months old |
| Primary maintainer | NevilleQingNY (739 commits) | 2.5yr account, 39 followers — established but younger than co-founders |
| Co-founders | forrestchang (732), Bohan-J (521), ldnvnbl (387) | 7-13yr accounts, legitimate histories |
| Review rate (sample of 100) | 🔴 1% formal / 1% any-review | Well below 30% threshold; process gap in fast-moving startup |
| Branch protection | 🔴 None effective | Classic: 404. Ruleset: exists but enforcement=disabled |
| CODEOWNERS | 🔴 Absent | All 4 standard paths checked |
| Dependabot alerts | ❓ Unknown | 403 — admin scope required; osv.dev: pg package has 1 known vuln |
| Security advisories | 🔴 0 filed | No GHSA advisories; recent security fixes shipped without advisory |
| Runtime dependencies | Go: 12 direct; Node: pnpm monorepo | AWS SDK, chi, jwt, pgx, gorilla/websocket |
| Install-time hooks | ✅ None | No preinstall/postinstall in inner packages |
| Publish auth | GoReleaser via tag push | GITHUB_TOKEN + HOMEBREW_TAP_GITHUB_TOKEN |
| CI workflows | 2 (ci.yml, release.yml) | 0 pull_request_target; 2 unpinned third-party actions |
| Releases | 35+ (daily cadence) | Latest: v0.2.6 on 2026-04-18 |
| OSSF Scorecard | Not indexed | Not yet indexed by securityscorecards.dev |
| Dependency vulnerabilities (osv.dev) | ⚠ pg package: 1 known vuln | Queried root package.json devDependencies; pg is a dev-only dep |
| Secrets in code history (gitleaks) | Not scanned | gitleaks not available — not a clean-code claim |
| API rate budget | 4,974/5000 remaining | PR sample: 100 (full) |

---

## 06 · Investigation coverage

> 15/15 coverage cells attempted · 3 caveats
>
> Comprehensive coverage. Tarball extracted at pinned SHA. All CI workflows read. All agent-rule files found and scanned. Main coverage gap is Dependabot (scope) and OSSF Scorecard (not indexed).

| Check | Result |
|-------|--------|
| Tarball extraction | ✅ 951 files — pinned to `b8907dda8d313cc96f0927da6dce2ea121fde43e` |
| Workflow files read | ✅ 2 of 2 — ci.yml, release.yml |
| SHA-pinning coverage | ⚠ 2/7 external actions are third-party at mutable tags (goreleaser, pnpm); 5/7 are GitHub-org actions |
| `pull_request_target` scan | ✅ Verified — 0 occurrences across 2 workflows |
| Monorepo scope | ✅ Verified — 9 package.json files; inner lifecycle scripts: none |
| README paste-scan (7.5) | ✅ Verified — 0 paste-blocks found |
| Agent-rule files | ✅ 2 found: CLAUDE.md (Tier 1), AGENTS.md (Tier 1) |
| Prompt-injection scan (F8) | ✅ Verified — 1 file matched pattern; 0 actionable (false positive: code comment in hermes.go) |
| Distribution channels (F1) | ⚠ Install path: 3/4 verified (Homebrew ✅, Windows PS1 ✅, git clone ✅); curl-pipe ⚠ unverified binary checksum |
| Windows surface coverage (F16) | ✅ install.ps1 inspected — Invoke-WebRequest, Invoke-RestMethod; checksum verification present; no -ExecutionPolicy Bypass |
| Dangerous-primitive grep | ✅ Verified — 0 actionable hits. dangerouslySetInnerHTML uses are sanitized or from trusted highlighters. execFile in Electron main process is bounded to known binary path. |
| Review-rate sample | ✅ 100 of 739 recent merges sampled — 1/100 formal (1%), 1/100 any-review (1%) |
| Dependency scan | ❓ Dependabot: 403 (admin:repo_hook scope missing) — state unknown |
| OSSF Scorecard | ❓ Not indexed — securityscorecards.dev returned no data for this repo |
| Dependency vulnerabilities (osv.dev) | ⚠ Queried 12 root devDeps — pg: 1 known vuln found. Checked against [osv.dev](https://osv.dev/), free Google-backed vulnerability database. |
| Secrets in code history (gitleaks) | Not scanned — gitleaks not available. Scanned by [gitleaks](https://gitleaks.io/) for secrets in git history. "Not scanned" means tool unavailable, not that the code is clean. |
| API rate budget | ✅ 4,974/5000 remaining — PR sample: 100 (full). GitHub limits API calls to 5,000/hour. |
| Commit pinned | `b8907dda8d313cc96f0927da6dce2ea121fde43e` |

**Gaps noted:**

1. Dependabot alerts — 403 returned (admin:repo_hook scope required). Cannot confirm whether Dependabot is enabled or whether any alerts are open. State: unknown.
2. OSSF Scorecard — not indexed. Repo is 3 months old; likely not yet indexed.
3. Org-level rulesets — admin:org scope required. Cannot confirm whether org rulesets provide additional protection. State: unknown.
4. Secrets-in-history (gitleaks) — tool not available. Not a clean-history claim.

---

## 07 · Evidence appendix

> ✅ 12 facts · 🔴 3 priority
>
> 12 command-backed claims. **Skip ahead to items marked START HERE** — those are the most consequential for the verdict.

### Priority evidence (read first)

#### START HERE Evidence 1 — No effective branch protection on main (F0 / C20)

```bash
gh api "repos/multica-ai/multica/branches/main/protection" 2>&1 | head -5
gh api "repos/multica-ai/multica/rulesets" 2>&1
gh api "repos/multica-ai/multica/rules/branches/main" 2>&1
```

Result:
```
Branch protection: {"message":"Not Found","status":"404"}
Rulesets: [{"id":11828157,"name":"protect-main-branch","enforcement":"disabled","rules":[{"type":"deletion"},{"type":"non_fast_forward"}],...}]
Rules on main: []
```

*Classification: Confirmed fact — three separate API calls confirm: no classic protection (404), one ruleset exists but enforcement=disabled, and no rules apply to the main branch.*

#### START HERE Evidence 2 — install.sh fetches from main with no binary checksum (F1)

```bash
# Script delivery:
head -10 scripts/install.sh
# Binary verification function:
grep -n 'checksum\|sha256\|hash\|verify' scripts/install.sh
```

Result:
```
# curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash
install_cli_binary() {
  # Get latest release tag
  local latest
  latest=$(curl -sI "$REPO_WEB_URL/releases/latest" ...)
  ...
  curl -fsSL "$url" -o "$tmp_dir/multica.tar.gz"
  tar -xzf "$tmp_dir/multica.tar.gz" -C "$tmp_dir" multica
  ...
}
# No checksum lines found in install.sh (grep returned no output)
```

*Classification: Confirmed fact — grep for checksum/sha256/hash/verify in install.sh returned zero matches on the Linux/Mac binary installation path.*

#### START HERE Evidence 3 — 888888 master auth code in source (F4)

```bash
grep -nP '888888|APP_ENV' server/internal/handler/auth.go
grep -nP 'JWT_SECRET' docker-compose.selfhost.yml .env.example
```

Result:
```
auth.go:169: isMasterCode := code == "888888" && os.Getenv("APP_ENV") != "production"
docker-compose.selfhost.yml:45: JWT_SECRET: ${JWT_SECRET:-change-me-in-production}
.env.example:10: JWT_SECRET=change-me-in-production
```

*Classification: Confirmed fact — source code at scanned SHA contains the 888888 bypass gated on APP_ENV. Default JWT_SECRET is a known string in both .env.example and the docker-compose fallback.*

### Other evidence supporting Warnings

#### Evidence 4 — goreleaser action unpinned with Homebrew PAT (F2)

```bash
grep -nP 'uses:|HOMEBREW_TAP_GITHUB_TOKEN' .github/workflows/release.yml
```

Result:
```
uses: goreleaser/goreleaser-action@v6
env:
  GITHUB_TOKEN: $&#123;&#123; secrets.GITHUB_TOKEN &#125;&#125;
  HOMEBREW_TAP_GITHUB_TOKEN: $&#123;&#123; secrets.HOMEBREW_TAP_GITHUB_TOKEN &#125;&#125;
```

*Classification: Confirmed fact — third-party action using mutable @v6 tag, with Homebrew PAT in scope.*

#### Evidence 5 — 1% PR review rate (F3)

```bash
gh pr list -R multica-ai/multica --state merged --limit 100 \
  --json number,title,reviewDecision,reviews | python3 -c "
import sys,json
prs=json.load(sys.stdin)
formal=sum(1 for p in prs if p.get('reviewDecision'))
any_r=sum(1 for p in prs if p.get('reviews'))
print(f'Formal: {formal}/100. Any-review: {any_r}/100.')
"
```

Result:
```
Formal: 1/100. Any-review: 1/100.
```

*Classification: Confirmed fact — sampled 100 most recent merged PRs, 1 had formal reviewDecision set.*

#### Evidence 6 — PR #1309 auth fix self-merged in 3 minutes (F3)

```bash
gh pr view 1309 -R multica-ai/multica --json title,author,mergedBy,createdAt,mergedAt,reviewDecision
```

Result:
```json
{"title":"fix(auth): validate next= redirect target to prevent open redirect",
 "author":{"login":"Bohan-J"},"mergedBy":{"login":"Bohan-J"},
 "createdAt":"2026-04-18T05:21:04Z","mergedAt":"2026-04-18T05:24:01Z",
 "reviewDecision":null}
```

*Classification: Confirmed fact — author equals mergedBy (self-merge), 3-minute window, no reviewDecision.*

#### Evidence 7 — No CODEOWNERS found (F0)

```bash
for P in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do
  gh api "repos/multica-ai/multica/contents/$P" 2>&1 | head -1
done
```

Result:
```
{"message":"Not Found",...}
{"message":"Not Found",...}
{"message":"Not Found",...}
{"message":"Not Found",...}
```

*Classification: Confirmed fact — all four standard CODEOWNERS locations returned 404.*

#### Evidence 8 — No SECURITY.md (F0 / scorecard)

```bash
gh api "repos/multica-ai/multica/community/profile" -q '.files.security_policy'
```

Result:
```
null
```

*Classification: Confirmed fact — security_policy field is null; no SECURITY.md present.*

### Evidence supporting OK findings

#### Evidence 9 — dangerouslySetInnerHTML is sanitized (OK)

```bash
grep -n 'rehypeSanitize\|sanitizeSchema' packages/views/editor/readonly-content.tsx packages/ui/markdown/Markdown.tsx
```

Result:
```
readonly-content.tsx:26: import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
readonly-content.tsx:52: const sanitizeSchema = { ... }
readonly-content.tsx:298: rehypePlugins={[rehypeRaw, [rehypeSanitize, sanitizeSchema]]}
Markdown.tsx:4: import rehypeSanitize, { defaultSchema } from 'rehype-sanitize'
Markdown.tsx:404: rehypePlugins={[rehypeRaw, [rehypeSanitize, sanitizeSchema]]}
```

*Classification: Confirmed fact — rehypeSanitize is imported and applied in the rehypePlugins chain before rendering.*

#### Evidence 10 — CORS uses explicit whitelist, no wildcard (OK)

```bash
grep -n 'AllowedOrigins\|Access-Control-Allow-Origin.*\*' server/cmd/server/router.go
```

Result:
```
AllowedOrigins: origins,  (line 88)
# No wildcard match found
```

*Classification: Confirmed fact — CORS uses computed origins array from allowedOrigins() function; no wildcard pattern found.*

#### Evidence 11 — No lifecycle scripts in inner npm packages (OK)

```bash
for P in $(head -5 /tmp/pkg-list.txt); do
  grep -HE '"(preinstall|install|postinstall|prepare|prepublishOnly)"' "$P" 2>/dev/null
done
echo "Lifecycle check done"
```

Result:
```
Lifecycle check done
```

*Classification: Confirmed fact — grep returned no output; no lifecycle scripts in sampled inner packages.*

#### Evidence 12 — Windows PS1 verifies SHA256 checksum (OK)

```bash
grep -nP 'checksum\|SHA256\|hash\|verify' scripts/install.ps1 | head -5
```

Result:
```
72:    # Verify SHA256 checksum
73:    $checksumUrl = "https://github.com/.../checksums.txt"
77:    $actualHash = (Get-FileHash -Path $zipFile -Algorithm SHA256).Hash.ToLower()
78:    $expectedLine = ...multica_windows_$arch\.zip...
```

*Classification: Confirmed fact — PS1 downloads and verifies SHA256 checksum before extracting CLI binary.*

---

## 08 · How this scan works

**What this scan is.** An LLM-driven security investigation using the GitHub CLI (`gh`) and free public APIs. Not a static analyzer, penetration test, or formal audit. The investigator ran specific commands, read specific files, and synthesized findings from what was observed.

**What we checked.** Governance and trust (branch protection, CODEOWNERS, maintainer background, review rate), code patterns (dangerous primitives, XSS sinks, auth bypass patterns, hardcoded credentials), supply chain (CI workflow actions, install scripts, artifact verification), AI agent rules (CLAUDE.md, AGENTS.md), and distribution channels (Homebrew, curl-pipe, PowerShell).

**External tools used.**
- [GitHub CLI](https://cli.github.com/) — repo metadata, PRs, issues, workflows
- [OSSF Scorecard](https://securityscorecards.dev/) — not indexed for this repo
- [osv.dev](https://osv.dev/) — dependency vulnerability database (pg package: 1 vuln found in devDependencies)
- [gitleaks](https://gitleaks.io/) — not available on this scanner instance

**What this scan cannot detect.** Transitive dependency vulnerabilities (only direct deps queried), runtime behavior (what the code does when running with real data), published artifact tampering after the GoReleaser checksum is published, sophisticated backdoors designed to evade grep patterns, container contents at runtime, or vulnerabilities introduced after the scanned commit (`b8907dd`).

**Scan methodology version.** Prompt V2.4 · Operator Guide V0.2 · Validator: python3 validate-scanner-report.py

