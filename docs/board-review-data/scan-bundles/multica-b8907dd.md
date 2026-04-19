# multica-ai/multica Scan — Evidence Bundle

**HEAD SHA:** b8907dda8d313cc96f0927da6dce2ea121fde43e
**Scan date:** 2026-04-19
**Fetch path:** tarball at pinned SHA
**Files extracted:** 951

---

## Repo identity — facts

name: multica
description: The open-source managed agents platform. Turn coding agents into real teammates.
createdAt: 2026-01-13T17:59:46Z (3 months old)
pushedAt: 2026-04-18T15:28:13Z
stargazerCount: 16,457  forkCount: 2,038
licenseInfo: NOASSERTION (key: other)
health: 62%  coc: false  contrib: true  security_policy: false
SECURITY.md: NOT FOUND

## Owner — facts

multica-ai org created_at: 2026-01-13T17:57:46Z (same day as repo — new org)
public_repos: 3  followers: 201  type: Organization

## Contributors — facts

NevilleQingNY: 739 commits  forrestchang: 732  Bohan-J: 521  ldnvnbl: 387
devv-eve: 20  pradeep7127: 5  iFwu: 4  kagura-agent: 3  dependabot[bot]: 3
Total sample: 2444. Top contributor share: NevilleQingNY 30.2%
Four-person core: NevilleQingNY+forrestchang+Bohan-J+ldnvnbl = 97.9%

forrestchang: created 2014-06-11 (12yr), 103 repos, 2124 followers, bio "Building @multica-ai"
Bohan-J: created 2019-07-02 (7yr), 11 repos, 111 followers, bio "coFounder of @multica-ai"
ldnvnbl: created 2013-03-07 (13yr), 44 repos, 53 followers
NevilleQingNY: created 2023-09-17 (2.5yr), 15 repos, 39 followers
kagura-agent: created 2026-03-14 (6wk), 64 repos, bio "Self-evolving AI agent | 125+ open source PRs"

## Governance (C20 check) — facts

Classic branch protection on main: 404 (no classic protection)
Rulesets: 1 found — "protect-main-branch" id:11828157 enforcement: DISABLED
  rules: [deletion, non_fast_forward] — no review requirement even if enabled
  conditions: ref_name include:[], exclude:[] — no branches targeted
Rules-on-main (gh api rules/branches/main): [] empty
Org rulesets: UNKNOWN (admin:org scope missing — 404 returned)
CODEOWNERS: NOT FOUND in any of 4 standard paths
Repo ships executable code to users: YES (install.sh, CLI binaries, Electron app, Docker)
Recent releases: YES — v0.2.6 on 2026-04-18 (daily cadence)

C20 analysis: All 5 criteria met for CRITICAL:
  (1) classic protection 404 + (2) rulesets disabled/no branch targeted + (3) rules-on-main empty
  + (5) CODEOWNERS absent + ships code + daily releases in last 30 days
  [org rulesets: unknown — cannot confirm or deny additional protection]
C20 proposed severity: CRITICAL (ships executables + daily releases)

## Releases — facts

Latest: v0.2.6 (2026-04-18T06:40:07Z)
Cadence: 1-3 releases/day, averaging daily
Distribution: GoReleaser → GitHub Releases + Homebrew tap
checksums.txt published per release (confirmed in .goreleaser.yml)

## Dependabot / advisories — facts

Dependabot alerts: 403 "not authorized" (admin:repo_hook scope missing) → state: UNKNOWN
osv.dev: queried root package.json devDeps — pg package: 1 known vuln found
Security advisories: [] (zero filed)

## CI workflows — facts

Workflows: ci.yml, release.yml
pull_request_target: 0 occurrences across both workflows

ci.yml uses:
  - actions/checkout@v6 (GitHub-org, tag only) INFO
  - pnpm/action-setup@v4 (THIRD-PARTY, tag only, no secrets) WARNING
  - actions/setup-node@v6 (GitHub-org) INFO
  - actions/setup-go@v5 (GitHub-org) INFO

release.yml uses:
  - actions/checkout@v4 (GitHub-org) INFO
  - actions/setup-go@v5 (GitHub-org) INFO
  - goreleaser/goreleaser-action@v6 (THIRD-PARTY, has GITHUB_TOKEN + HOMEBREW_TAP_GITHUB_TOKEN) WARNING
  permissions: contents: write

No curl|bash in workflows. No untrusted input interpolation.

## Runtime dependencies — facts

Go: aws-sdk-go-v2, go-chi, golang-jwt/jwt/v5, gorilla/websocket, jackc/pgx/v5, cobra
Node: turbo monorepo — 9 package.json files
Inner package lifecycle scripts: NONE found (preinstall/install/postinstall/prepare)
Root package.json onlyBuiltDependencies: [esbuild, electron]

## Step A grep results — facts

eval/exec hits (TS/TSX, non-test):
  - packages/views/editor/readonly-content.tsx — lowlight hast toHtml (with rehypeSanitize)
  - packages/ui/markdown/Markdown.tsx — same pattern (with rehypeSanitize)
  - packages/ui/markdown/CodeBlock.tsx — Shiki syntax highlighter output
  - apps/desktop/src/main/daemon-manager.ts — import execFile; spawns multica CLI binary
  - apps/desktop/src/main/cli-bootstrap.ts — import execFile; CLI auto-update

dangerouslySetInnerHTML hits:
  - readonly-content.tsx, Markdown.tsx — SANITIZED via rehypeSanitize
  - CodeBlock.tsx — Shiki/lowlight output (language-specific HTML classes, not user JS)
  - chart.tsx — CSS theme tokens (developer-controlled)
  - (landing)/layout.tsx — JSON.stringify(jsonLd) in ld+json script (developer-controlled)

0.0.0.0 hits:
  - server/cmd/multica/cmd_auth.go:113 — conditional: only when MULTICA_APP_URL is a private IP (OAuth callback)
  - Dockerfile.web, docker-compose.selfhost.yml — container port bindings (expected)

CORS: No Access-Control-Allow-Origin:* pattern found. allowedOrigins() uses explicit whitelist.
TLS: No rejectUnauthorized:false or InsecureSkipVerify found.
Auth bypass: No validate_exp=false or algorithm:none found.
Hardcoded secrets: NONE found.
apps/desktop/.env.production: public URLs only (VITE_API_URL, VITE_WS_URL, VITE_APP_URL — no secrets)

Prompt injection scan (F8): 1 file matched pattern
  - server/pkg/agent/hermes.go:193: "// 3. Build the prompt content. If we have a system prompt, prepend it."
  - CLASSIFICATION: false positive — code comment about system prompt handling, not a scanner injection attempt
  - 0 actionable findings

## README install path — facts

Install methods (from README.md):
1. brew install multica-ai/tap/multica
2. curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash
3. irm https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.ps1 | iex
4. curl .../install.sh | bash -s -- --with-server (self-host)

install.sh (scripts/install.sh):
  - Fetched unpinned from /main branch (not tagged)
  - install_cli_binary(): downloads releases/latest binary
  - Binary verification: NO checksum on Linux/Mac path (install_cli_binary has no sha256 check)
  - --with-server: git clone --depth 1 main; on upgrade: git fetch origin main + git reset --hard origin/main
  - openssl rand -hex 32 generates JWT_SECRET when creating .env (good)

install.ps1:
  - Fetched unpinned from /main
  - Downloads releases/latest zip
  - SHA256 checksum verification PRESENT (downloads checksums.txt, verifies before install)
  - Gracefully warns (not fails) if checksums.txt unavailable

README paste-scan: NONE found (no "paste into system prompt" blocks)

## F12 exec inventory — facts

Agent-rule files found:
  - CLAUDE.md — Tier 1 auto-loaded (Claude Code loads at every session in repo)
  - AGENTS.md — Tier 1 auto-loaded (any AI agent platform that honors AGENTS.md)

CLAUDE.md content scan (imperative pattern check):
  - No "ignore previous instructions" / jailbreak / persona override language
  - No credential or file path requests (~/.ssh/, ~/.aws/)
  - No shell command invocations directed at scanner
  - Imperatives: standard dev instructions (run make check, use atomic commits, etc.)
  - Contains "AI Agent Verification Loop" → run make check after every change

AGENTS.md content scan:
  - Pointer to CLAUDE.md only; no actionable imperative language beyond architecture rules

Electron daemon-manager.ts:
  - execFile(bin, ["version", "--output", "json"]) — version check
  - execFile(bin, args, {timeout:20_000}) — spawns multica CLI daemon
  - bin = resolved path to multica CLI binary — not user-controlled
  - env passed: desktopSpawnEnv() — MULTICA_DESKTOP_APP flag

## PR review rate sample — facts

Total merged PRs: 739  (sample: 100 most recent)
Formal review (reviewDecision set): 1/100 = 1.0%
Any-review (reviews.length > 0): 1/100 = 1.0%

Self-merges noted in sample:
  - PR #1309 fix(auth): validate next= redirect (auth fix) — Author: Bohan-J, MergedBy: Bohan-J
    Created: 2026-04-18T05:21:04Z, Merged: 2026-04-18T05:24:01Z (3-minute self-merge)
  - PR #1307 fix(selfhost): disable dev master code — Author: kagura-agent, MergedBy: Bohan-J
    Created: 2026-04-18T05:12:08Z, Merged: 2026-04-18T06:25:24Z (73-min, security-relevant)
  - PR #1280 ci(release): restrict tag pattern — Author: ldnvnbl, MergedBy: devv-eve (cross-merge, no review)

## Recent commits sample — facts

fix(views): prevent infinite re-render loops (#1322)
docs(selfhost): clarify 888888 master code disabled by default (#1313)
fix(ui/agents): drop Codex-incompatible --model example (#1310)
fix(auth): validate next= redirect target to prevent open redirect (#1309)
fix(selfhost): disable dev master code by default in Docker (#1307)

## Open issues — facts

50+ open issues sampled. Security-related:
  - #1321: selfhost cannot create workspace: auth no token found
  - #1331: selfhost upgrade issues (Chinese user, recurring)
  - #1297: Windows Multica-spawned cursor-agent exits 1
  - #1325: Gemini CLI on Windows unusable out-of-the-box

No open CVE or security advisory tracking issues.

---

## Pattern recognition (inference)

- The org/repo same-day creation (2026-01-13) resembles a legitimately founded startup launching their project org, not a sockpuppet, given that the core maintainers (forrestchang, Bohan-J, ldnvnbl) have 7-13 year GitHub accounts with independent prior repos.

- The 1.0% review rate pattern-matches to Archon's early-stage high-velocity team operating on trust-based merges rather than formal review tooling. In both cases, it resembles a feature-shipping culture, not an intentional security evasion pattern.

- The governance posture (ruleset exists-but-disabled, no CODEOWNERS, no SECURITY.md) is consistent with a project that created the ruleset early but never completed the configuration. Not evidence of bad faith.

- The curl-pipe-from-main delivery pattern resembles caveman's installer shape: a one-liner that fetches and executes from live main. The key difference is that Multica also distributes via Homebrew (checksums) and Windows PS1 (checksums), so the risk is concentrated in the curl-pipe path specifically.

- The 888888 master code in auth.go (APP_ENV gate) plausibly indicates a developer shortcut that was never fully removed. PR #1307 addressed the Docker default but not non-Docker deployments. The fix is partial — the code remains.

- goreleaser/goreleaser-action@v6 with HOMEBREW_TAP_GITHUB_TOKEN access suggests that a goreleaser compromise could rewrite the Homebrew formula, which then auto-updates any user running brew upgrade. This is the highest-leverage CI supply-chain vector.

- kagura-agent (AI agent contributor) authoring PR #1307 (master code fix) is consistent with the platform's "coding agents as teammates" premise — multica is dogfooding its own product. The agent authored a security-sensitive fix that was then merged by a human maintainer.

---

## FINDINGS SUMMARY — synthesis

**F0 — CRITICAL · Governance** — No effective branch protection; ruleset disabled; no CODEOWNERS; no SECURITY.md
Cites: Governance section — classic 404, ruleset enforcement=disabled, rules-on-main=[], CODEOWNERS absent, security_policy=false, daily releases + executable distribution. C20 fires at CRITICAL.

**F1 — WARNING · Supply chain / Install** — curl-pipe-from-main with no binary checksum on Linux/Mac
Cites: README install path, install.sh analysis. Script fetched from /main (not pinned), binary downloaded without verification on Linux/Mac. Windows PS1 path does verify checksums. Homebrew path uses GoReleaser checksums.

**F2 — WARNING · CI/Actions** — Unpinned third-party actions; goreleaser has HOMEBREW_TAP_GITHUB_TOKEN
Cites: CI workflows section. goreleaser/goreleaser-action@v6 and pnpm/action-setup@v4 use mutable tags. Goreleaser has write access to Homebrew tap.

**F3 — WARNING · Code Review** — 1% review rate; security PRs self-merged or unreviewed
Cites: PR review section, Step 5 sample. Auth redirect fix PR #1309 self-merged in 3 min. Master code fix PR #1307 merged without review. 1/100 PRs had any review event.

**F4 — INFO · Self-host defaults** — 888888 master auth code if APP_ENV not set; JWT default "change-me"
Cites: auth.go:169, .env.example, docker-compose.selfhost.yml. Docker path now defaults to production (fixed). Non-Docker path still vulnerable if APP_ENV not explicitly set. install.sh --with-server generates a random JWT_SECRET (mitigated for that path).

**F5 — INFO · Agent-rule files** — CLAUDE.md and AGENTS.md auto-loaded; content OK; future compromise risk
Cites: F12 exec inventory, CLAUDE.md + AGENTS.md reads. Both files are developer guidelines with no manipulation language. Tier 1 auto-loaded by Claude Code and AGENTS-compatible platforms.

---

## Positive signals

- 4-person experienced team (7-13 year GitHub accounts for 3 of 4 founders)
- Daily releases with GoReleaser + checksums.txt (artifact provenance for downloads)
- No hardcoded secrets in source
- dangerouslySetInnerHTML usage is sanitized (rehypeSanitize)
- CORS is explicit whitelist (no wildcard)
- No lifecycle scripts in inner packages
- No pull_request_target usage
- 888888 backdoor partially mitigated (Docker now defaults to production)
- install.sh generates random JWT_SECRET for --with-server users
- PS1 installer verifies SHA256 checksums
- Open redirect fix (PR #1309) shipped within 24h of detection
- 0 actionable prompt injection patterns found in source

---

## Proposed verdict

**CAUTION** — Deployment axis split

**Deployment · Cloud users (multica.ai managed):** CAUTION — Install-time exposure (curl-pipe-from-main, no Linux/Mac binary checksum). Governance gaps (no review gate, no SECURITY.md) mean a supply-chain incident would likely ship before anyone noticed.

**Deployment · Self-hosted users:** CAUTION (higher risk) — All cloud-user risks, PLUS: 888888 master auth bypass if APP_ENV not explicitly set to "production", JWT default "change-me-in-production" if .env.example copied without modification.

Driving findings: F0 (CRITICAL), F1 (WARNING), F2 (WARNING), F3 (WARNING), F4 (INFO), F5 (INFO)

---

## Proposed scorecard (C10)

**Does anyone check the code?** RED — "Rare · 1% review rate"
Evidence: 1/100 PRs had any review. Formal review <30% threshold → red. Security-relevant PRs self-merged in minutes.

**Do they fix problems quickly?** AMBER — "Open fixes, not merged yet"
Evidence: PR #1307 partially fixed master code (Docker only). Self-host docs updated. Dependabot: unknown. No CVEs >14 days old. Active daily releases suggest response capability.

**Do they tell you about problems?** RED — "No advisory · No SECURITY.md"
Evidence: security_policy=false. Zero advisories filed. PR #1309 (auth redirect) and PR #1307 (master code) shipped without GHSA advisories.

**Is it safe out of the box?** AMBER — "Safer via Homebrew · Avoid curl-pipe path on prod"
Evidence: curl-pipe-from-main (F1), goreleaser action unpinned (F2). Any unverified distribution channel → amber cap.

---

## Catalog metadata

Repo: multica-ai/multica
HEAD SHA: b8907dda8d313cc96f0927da6dce2ea121fde43e (short: b8907dd)
Date: 2026-04-19
Verdict: caution
Scope axis: Deployment (self-hosted vs cloud)
Shape: Agentic platform (server + CLI + web + Electron + daemon + multi-AI)
methodology-used: path-b
rendering-pipeline: v2.4
