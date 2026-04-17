# Security Investigation: gitroomhq/postiz-app

**Investigated:** 2026-04-16 | **Applies to:** main @ 386fc7b (v2.21.6) | **Repo age:** 33 months | **Stars:** 28,822 | **License:** AGPL-3.0

> A 28,800-star open-source social media scheduling platform with 8 published CVEs (7 SSRF, 1 XSS) — all patched in the current release — but no required review gates on the default branch, no SECURITY.md, and Docker Compose defaults that ship with placeholder credentials.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-postiz-app.md` (+ `.html` companion) |
| Repo | [github.com/gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) |
| Short description | Open-source social media scheduling tool with AI. NestJS backend, Vite React frontend, Temporal orchestrator. Monorepo with 6 apps, Docker-based deployment, Chrome extension, and published SDK (`@postiz/node`). |
| Category | Web application |
| Subcategory | Social media management / SaaS platform |
| Verdict | **Caution** |
| Scanned revision | `main @ 386fc7b` (release tag `v2.21.6`) |
| Prompt version | `v2.3` |
| Prior scan | None — first run |

---

## Verdict: Caution — governance gaps and deployment defaults warrant review

Postiz is actively maintained with transparent vulnerability handling (8 published CVEs with GHSA entries), but structural governance gaps and deployment concerns require attention before trusting it in production.

- **8 published CVEs** (7 SSRF + 1 stored XSS) — all fixed in v2.21.6, but the SSRF cluster indicates historically weak input validation
- **No required reviews on default branch** — ruleset prevents force-push but does not require review or status checks; no CODEOWNERS
- **No SECURITY.md** — 8 CVEs published but no private disclosure channel documented
- **Docker Compose ships default credentials** — placeholder JWT secret and hardcoded DB password
- **CI workflow uses pull_request_target with write-all permissions** — fork PRs can access secrets (mitigated by environment gate)
- **Positive:** weekly releases, daily commits, CodeQL scanning, PR quality gate, comprehensive SSRF mitigations now in place, legitimate multi-year maintainer accounts

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | **Amber** — Informal: 52% any-review / 14% formal. No required reviews on main. No CODEOWNERS. |
| Is it safe out of the box? | **Amber** — Self-hosted: change defaults before deploying. Docker Compose ships placeholder JWT secret and default DB password. Docker image uses mutable `:latest` tag. |
| Can you trust the maintainers? | **Amber** — Published advisories (8 CVEs with GHSA entries), but no SECURITY.md for private disclosure. |
| Is it actively maintained? | **Green** — Weekly releases. v2.21.6 shipped 2026-04-12. Daily commits from primary maintainer. |

---

## 01 · What should I do?

### Step 1: If you are deploying self-hosted via Docker Compose, change all default credentials immediately

**Non-technical:** The default Docker Compose file ships with a placeholder JWT secret and a hardcoded database password. Anyone who knows these defaults can forge login sessions and access your database. Before going live, generate real random secrets.

```bash
# Generate a proper JWT secret
openssl rand -base64 64

# Replace in docker-compose.yaml:
# JWT_SECRET: 'YOUR_GENERATED_SECRET_HERE'
# DATABASE_URL: 'postgresql://postiz-user:YOUR_STRONG_PASSWORD@postiz-postgres:5432/postiz-db-local'
# Also consider setting DISABLE_REGISTRATION: 'true' after creating your account
```

### Step 2: Ensure you are running v2.21.6 or later

**Non-technical:** Seven SSRF vulnerabilities and one stored XSS vulnerability were fixed between v2.21.1 and v2.21.6. If you are running any earlier version, upgrade immediately.

```bash
# Check your current version
# Check your running container version
docker ps --filter name=postiz

# Pull the latest release
docker pull ghcr.io/gitroomhq/postiz-app:v2.21.6

# Pin to a specific version tag rather than :latest
# In docker-compose.yaml, change:
#   image: ghcr.io/gitroomhq/postiz-app:latest
# to:
#   image: ghcr.io/gitroomhq/postiz-app:v2.21.6
```

### Step 3: If you are evaluating Postiz for a team or organization

**Non-technical:** The code review rate is 52% informal / 14% formal, and there is no branch protection requiring reviews. This means code changes can land on main without a second pair of eyes. For a production deployment, consider:

1. Subscribe to [GitHub releases](https://github.com/gitroomhq/postiz-app/releases) to catch security fixes
2. Pin your Docker image to a specific version tag (not `:latest`)
3. Run behind a reverse proxy with rate limiting
4. If contributing: ask the maintainers to add a SECURITY.md and enable required reviews

---

## 02 · What we found

> 0 Critical - 5 Warning - 2 Info - 1 OK
>
> 8 findings total. The Warnings cluster into three themes: historical vulnerability pattern (SSRF + XSS), governance gaps (no required reviews, no SECURITY.md), and deployment defaults (Docker Compose credentials, CI permissions). Start with F1 (SSRF cluster) and F7 (governance) if time-pressed.
>
> **Your action:** Upgrade to v2.21.6 if not already current. Change all default credentials in docker-compose.yaml before deploying. Pin Docker images to a specific version tag.

### F1 — Warning - Resolved - SSRF Advisory Cluster: 7 High-Severity SSRF CVEs in 12 Months

**Date range:** 2025-07 to 2026-04 | **Duration:** ~9 months

Seven separate SSRF vulnerabilities were discovered and patched across multiple endpoints: `/api/public/stream`, webhook creation, upload-from-url, and header mutation in middleware. The pattern indicates the codebase originally lacked SSRF defenses and retrofitted them iteratively. Current code includes `webhook.url.validator.ts` with comprehensive IPv4/IPv6 blocklist and DNS resolution checks.

- **CVE-2025-53641** (High) — Header mutation SSRF (2025-07)
- **CVE-2024-34351** (High) — High-severity SSRF (2026-03-25)
- **GHSA-89v5-38xr-9m4j** (High) — Multiple SSRF vectors (2026-03-25)
- **CVE-2026-34577** (High) — Unauthenticated full-read SSRF via /public/stream (2026-03-29)
- **CVE-2026-34576** (High) — SSRF in upload-from-url, cloud metadata access (2026-03-29)
- **CVE-2026-34590** (Medium) — SSRF via webhook creation (2026-03-29)
- **CVE-2026-40168** (High) — SSRF via redirect bypass (2026-04-09)

**What this means for you:** If you are on v2.21.3 or later, the known SSRF vectors are mitigated. If on an earlier version, your instance is exposed to multiple SSRF attacks including cloud metadata access (169.254.169.254). The cluster pattern means future SSRF bypasses are plausible — monitor advisories.

### F2 — Warning - Resolved - Stored XSS via File Upload (CVE-2026-40487)

**Published:** 2026-04-12 | **Fixed in:** v2.21.6

MIME type spoofing bypasses upload validation. An authenticated user could upload HTML/SVG files with a spoofed `Content-Type: image/png` header. The files were served with their original extension's Content-Type, enabling stored XSS. The frontend has 16 `dangerouslySetInnerHTML` instances across preview components that render user content.

**What this means for you:** Fixed in the current release. The 16 dangerouslySetInnerHTML instances suggest ongoing XSS attack surface that may yield future findings. Ensure your instance is on v2.21.6+.

### F3 — Warning - Active - No SECURITY.md: No Private Disclosure Channel

Despite 8 published CVEs, the repo has no SECURITY.md file. The community profile confirms `security_policy: false`. Security researchers have no documented private reporting channel. The advisories show reports were handled, but the path to report is unclear.

**What this means for you:** If you discover a vulnerability in Postiz, there is no clear private channel to report it. Reports may go to public issues, potentially exposing vulnerabilities before fixes are ready.

### F4 — Warning - Active - Docker Compose Ships Default Credentials

`docker-compose.yaml` contains:
- `JWT_SECRET: 'random string that is unique to every install - just type random characters here!'` — a placeholder, not a generated secret
- `DATABASE_URL` with password `postiz-password`
- `DISABLE_REGISTRATION: 'false'` — open registration by default

**What this means for you:** Any self-hosted deployment using the default docker-compose.yaml without changing these values has a predictable JWT secret (enabling session forgery), a known database password, and open user registration. This is a deployment-axis concern that primarily affects users who follow the quickstart without reading documentation.

### F5 — Warning - Active - CI Workflow: pull_request_target with write-all Permissions

`pr-docker-build.yml` uses `pull_request_target` with `permissions: write-all`. It checks out fork PR code at `github.event.pull_request.head.sha`, builds a Docker image, and pushes to GHCR. An `environment: build-pr` gate provides partial mitigation by requiring approval.

**Threat model (F13):** A malicious actor forks the repo, crafts a PR with injected code in the Dockerfile or build scripts, and submits it. If a maintainer approves the environment deployment without inspecting the PR code, the malicious code runs with write-all permissions and access to repository secrets. The environment gate reduces this from automatic to approval-gated, but the approval UI does not show the code diff.

**What this means for you:** This primarily affects the maintainers and the GHCR image supply chain. If you pull Docker images from `ghcr.io/gitroomhq/postiz-app-pr:*`, those images are built from unreviewed fork code.

### F6 — Info - Ongoing - Third-Party Actions Not SHA-Pinned

Eight third-party GitHub Actions use tag-only pinning. Notable:
- `peakoss/anti-slop@v0` — mutable v0 tag in a `pull_request_target` workflow with PR write access
- `mnao305/chrome-extension-upload@v5.0.0` — controls Chrome extension publishing with access to Chrome store secrets
- `docker/login-action@v3`, `docker/setup-buildx-action@v3` — Docker build pipeline

**What this means for you:** If any upstream action is compromised, workflows automatically pull the malicious version. The extension-publishing action is the highest-value target (access to Chrome store credentials). Risk is low probability but high impact.

### F7 — Warning - Active - No Required Reviews on Default Branch (Governance Gap)

Classic branch protection returned 404 on `main`. The repo-level ruleset ("Copilot review for default branch") prevents branch deletion and force-push but does NOT require reviews or status checks. No CODEOWNERS file exists. Org-level rulesets are unknown (scope gap requiring `admin:org`). **OSSF Scorecard is not indexed** for this repo (API returned 404), so no independent governance score is available as a cross-check.

**Threat model (F13):** An attacker who compromises nevo-david's GitHub account (phishing, stale OAuth token, session cookie theft via malicious browser extension, compromised IDE plugin) can push directly to main without any review gate. Given 28,822 stars and 3M+ Docker pulls, blast radius is significant. The force-push prevention in the ruleset limits history rewriting but does not prevent malicious commit insertion.

**What this means for you:** Code changes can land on main without a second pair of eyes. On a repo with 28k+ stars that ships Docker images to production deployments, this is a meaningful governance gap. The partial ruleset (force-push prevention) is better than nothing but does not substitute for required reviews.

### F8 — Info - Informational - Agent Rule Files: CLAUDE.md and copilot-instructions.md

Two Tier 1 auto-loaded agent rule files found:
- `CLAUDE.md` — auto-loaded by Claude Code for every contributor session. Contains project architecture description, coding conventions (NestJS 3-layer pattern, SWR hooks, pnpm-only), and UI guidelines.
- `.github/copilot-instructions.md` — auto-loaded by GitHub Copilot. Contains project architecture, developer workflows, coding conventions, integration points, and Sentry logging patterns.

Both files contain behavioral rules only. No imperative AI-directed language, no secrets, no command execution, no file path references, no obedience changes. Content is consistent with standard developer documentation.

**Imperative verb list:** CLAUDE.md uses "don't use", "never install", "focus on writing", "always use", "must comply". copilot-instructions.md uses "use", "ensure", "make sure". All are standard coding-convention directives, not scanner-targeting injection.

**Capability:** These files configure contributor AI assistants to follow Postiz coding conventions.
**Risk:** A future compromise of either file injects instructions into every contributor's AI assistant session — CLAUDE.md for Claude Code users, copilot-instructions.md for Copilot users. Subscribe to changes on these files if contributing.

---

## 02A · Executable File Inventory

### Quick scan (F12 one-liner per file)

- `CLAUDE.md` — auto-loaded every Claude Code session, behavioral rules only, no commands. **OK**
- `.github/copilot-instructions.md` — auto-loaded every Copilot session, behavioral rules only. **OK**
- `Dockerfile.dev` — builds production image from node:22.20-bookworm-slim, installs pnpm/pm2/nginx. **OK**
- `docker-compose.yaml` — orchestrates postiz + postgres + redis + temporal, ships default credentials. **Warning (F4)**
- `package.json` postinstall — runs `pnpm run prisma-generate` (Prisma codegen). **OK**
- `.github/workflows/pr-docker-build.yml` — pull_request_target with write-all, builds fork PR Docker images. **Warning (F5)**
- `.github/workflows/publish-extension.yml` — publishes Chrome extension, uses Chrome store secrets. **OK**
- `apps/frontend/public/f.js` — Facebook SDK (third-party, 15,897 lines, minified). **OK (third-party)**

### Detailed cards

#### CLAUDE.md
- **Trigger:** Auto-loaded by Claude Code on every session in this repo (Tier 1)
- **Reads:** N/A (instruction file, not executable code)
- **Writes:** N/A
- **Network:** None
- **Injection channel:** This file IS the injection channel — content becomes part of every Claude Code contributor's context
- **Secret-leak path:** None
- **Auto-load tier:** Tier 1 — always auto-loaded. This file is auto-loaded for every session — content changes reach every user without opt-in.
- **Capability assessment:** Configures Claude Code to follow Postiz coding conventions (NestJS patterns, pnpm-only, component guidelines). Currently benign.

#### .github/copilot-instructions.md
- **Trigger:** Auto-loaded by GitHub Copilot for every contributor (Tier 1)
- **Reads:** N/A
- **Writes:** N/A
- **Network:** None
- **Injection channel:** This file IS the injection channel — content becomes Copilot system instructions
- **Secret-leak path:** None
- **Auto-load tier:** Tier 1 — always auto-loaded. This file is auto-loaded for every session — content changes reach every user without opt-in.
- **Capability assessment:** Configures Copilot with project architecture and Sentry logging patterns. Currently benign.

#### docker-compose.yaml
- **Trigger:** User-initiated (`docker compose up`)
- **Reads:** Environment variables from the compose file
- **Writes:** PostgreSQL data volume, Redis data, upload directory
- **Network:** Exposes port 4007 (frontend), 5432 (postgres), 6379 (redis)
- **Secret-leak path:** JWT_SECRET placeholder is predictable; DB password is hardcoded
- **Capability assessment:** Deploys the full Postiz stack. Default credentials mean any instance deployed without customization has a known JWT secret and DB password.

#### .github/workflows/pr-docker-build.yml
- **Trigger:** pull_request_target (opened, synchronize) — fires on fork PRs
- **Reads:** Fork PR source code at PR head SHA
- **Writes:** Builds and pushes Docker image to GHCR (ghcr.io/gitroomhq/postiz-app-pr)
- **Network:** GHCR push
- **Secret-leak path:** `permissions: write-all` grants access to all repository secrets; `github.token` used for GHCR login
- **Capability assessment:** Fork PR code runs in a Docker build context with write-all permissions. Environment gate `build-pr` requires approval but does not show code diff in the approval UI. See F5 threat model.

---

## 03 · Suspicious Code Changes

No PRs were flagged as suspicious in the sampled set. Security fixes were committed by the primary maintainer (nevo-david) with commit messages like "feat: security fixes" and "feat: fix advisory" — the use of `feat:` prefix for security fixes is a minor changelog-hygiene concern (conventional commits would use `fix:` or `security:`) but the content is legitimate.

---

## 04 · Timeline

| Date | Event | Severity |
|------|-------|----------|
| 2023-07-08 | Repository created | CONTEXT |
| 2025-07-11 | CVE-2025-53641 published — header mutation SSRF | VULN REPORTED |
| 2026-03-25 | CVE-2024-34351 + GHSA-89v5-38xr-9m4j published — multiple SSRF vectors | SSRF CLUSTER |
| 2026-03-29 | v2.21.3 "Security Fixes" release — CVE-2026-34576, CVE-2026-34577, CVE-2026-34590 fixed | FIX SHIPS |
| 2026-04-09 | v2.21.5 — CVE-2026-40168 SSRF redirect bypass fixed | FIX SHIPS |
| 2026-04-12 | v2.21.6 — CVE-2026-40487 stored XSS fixed | FIX SHIPS |
| 2026-04-16 | This scan | SCAN |

---

## 05 · Repo Vitals

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Stars | 28,822 | Very popular — high blast radius for any compromise |
| Forks | 5,141 | Active community forking |
| Open issues | 240 | Moderate backlog — mostly OAuth/integration bugs |
| Contributors (top 30) | 30 | nevo-david dominates (69%), egelhaus active (17.6%) |
| License | AGPL-3.0 | Strong copyleft, source availability guaranteed |
| Releases (last 30 days) | 3 | Active release cadence |
| PR formal review rate | 14.0% (7/50) | Low formal review — most PRs merged without formal approval |
| PR any-review rate | 52.0% (26/50) | Moderate informal review — someone looks at about half |
| Branch protection | Partial — force-push prevention only | No required reviews or status checks |
| CODEOWNERS | Absent | No path-scoped review requirements |
| SECURITY.md | Absent | No documented private disclosure channel |
| CodeQL | Enabled | Automated code scanning active |
| Dependabot alerts | Unknown (scope gap) | 403 — requires admin:repo_hook |
| Docker pulls | 3M+ (per README) | Wide deployment base |
| OSSF Scorecard | Not indexed | API returned 404 — repo is not indexed by OSSF Scorecard |

---

## 06 · Investigation Coverage

- **Repo metadata:** gh api repos/gitroomhq/postiz-app — success
- **Contributors:** top 30 — success
- **Maintainer background:** gitroomhq (Org), nevo-david, egelhaus, jamesread — success
- **Releases:** 20 most recent — success
- **Branch protection (classic):** 404 — no classic protection (confirmed absent)
- **Rulesets (repo):** 1 found — confirmed no required reviews
- **Rulesets (org):** 404 — scope gap (requires admin:org), state unknown
- **CODEOWNERS:** checked 4 standard paths — confirmed absent
- **Security advisories:** 8 published — success
- **Dependabot alerts:** 403 — scope gap (requires admin:repo_hook), state unknown
- **CI workflows:** 10 workflows read — success
- **pull_request_target usage:** 2 workflows (pr-docker-build.yml, pr-quality.yml)
- **Monorepo inner packages:** 7 package.json files enumerated, 6 sampled for lifecycle scripts — 0 inner lifecycle scripts found
- **Merged PRs:** 50 sampled (formal: 14%, any-review: 52%)
- **Open issues:** 20 sampled of 240 total; 10 security-keyword matches (all OAuth/auth bugs)
- **Recent commits:** 20 sampled — success
- **Step 7.5 paste-block scan:** run, 0 paste blocks found
- **Step 2.5 agent-rule detection:** 0 CI-amplified, 2 static (CLAUDE.md, .github/copilot-instructions.md)
- **Step A tarball extraction:** success, 881 files
- **Prompt-injection scan:** 1 string matched, 0 classified as actionable (false positive in translation.json)
- **Distribution channels:** 1 verified (Docker via GHCR), 1 partially verified (npm SDK @postiz/node), Chrome extension not verified against source
- **Windows surface:** no .ps1/.bat/.cmd files — not applicable
- **Executable files inspected:** 8 of 8 (2 Warning, 4 OK, 0 Critical, 2 Info)
- **OSSF Scorecard:** Not indexed — API returned 404. No independent governance score available as cross-check
- **osv.dev:** Applicable — NestJS monorepo with multiple package.json dependency manifests. 8 published CVEs tracked via GHSA
- **Secrets-in-history:** Not scanned (gitleaks not available)
- **API rate budget:** 5000/5000 remaining. PR sample: 50 merged PRs

---

## 07 · Evidence Appendix

### Priority evidence (read first)

#### E1: No required reviews on default branch
- **Claim:** The default branch `main` has no required review gate
- **Command:** `gh api repos/gitroomhq/postiz-app/branches/main/protection` and `gh api repos/gitroomhq/postiz-app/rulesets` and `gh api repos/gitroomhq/postiz-app/rules/branches/main`
- **Result:** Classic protection: 404. Ruleset: 1 found with rules deletion, non_fast_forward, copilot_code_review (review_on_push: false). No required_reviews or required_status_checks rules.
- **Classification:** Confirmed fact

#### E2: 8 published security advisories (7 SSRF + 1 XSS)
- **Claim:** 8 CVEs published, all with GHSA entries
- **Command:** `gh api repos/gitroomhq/postiz-app/security-advisories`
- **Result:** 8 advisories returned, all state: published. CVE-2026-40487 (XSS), CVE-2026-40168 (SSRF), CVE-2026-34590 (SSRF), CVE-2026-34576 (SSRF), CVE-2026-34577 (SSRF), CVE-2024-34351 (SSRF), GHSA-89v5-38xr-9m4j (SSRF), CVE-2025-53641 (SSRF).
- **Classification:** Confirmed fact

#### E3: Docker Compose default credentials
- **Claim:** docker-compose.yaml ships with predictable JWT secret and hardcoded DB password
- **Command:** `grep -nP 'JWT_SECRET|postiz-password' docker-compose.yaml`
- **Result:** Line 11: `JWT_SECRET: 'random string that is unique to every install - just type random characters here!'` / Line 12: `DATABASE_URL: 'postgresql://postiz-user:postiz-password@...'`
- **Classification:** Confirmed fact

### Supporting evidence

#### E4: PR review rate
- **Claim:** 14% formal review rate, 52% any-review rate
- **Command:** `gh pr list -R gitroomhq/postiz-app --state merged --limit 50 --json number,title,createdAt,mergedAt,author,reviewDecision,reviews`
- **Result:** 50 sampled. 7 with reviewDecision set (14%). 26 with reviews.length > 0 (52%).
- **Classification:** Confirmed fact (sampled — 50 most recent of total merged)

#### E5: No SECURITY.md
- **Claim:** No security policy documented
- **Command:** `gh api repos/gitroomhq/postiz-app/community/profile`
- **Result:** `security_policy: false`
- **Classification:** Confirmed fact

#### E6: pull_request_target with write-all
- **Claim:** pr-docker-build.yml uses pull_request_target with write-all permissions
- **Command:** `cat .github/workflows/pr-docker-build.yml`
- **Result:** `on: pull_request_target`, `permissions: write-all`, `environment: name: build-pr`
- **Classification:** Confirmed fact

#### E7: SSRF mitigations in current code
- **Claim:** webhook.url.validator.ts implements comprehensive IP blocklist
- **Command:** `cat libraries/nestjs-libraries/src/dtos/webhooks/webhook.url.validator.ts`
- **Result:** IPv4 blocklist covering 0.0.0.0/8, 10.0.0.0/8, 127.0.0.0/8, 169.254.0.0/16, 172.16-31.0.0/12, 192.168.0.0/16, 100.64.0.0/10, 198.18.0.0/15, 224+. IPv6 blocklist covering ::1, ::, fe80:, fc/fd, ff. DNS resolution check.
- **Classification:** Confirmed fact

### Positive evidence

#### E8: Active release cadence
- **Claim:** Weekly releases with security fixes shipping promptly
- **Command:** `gh release list -R gitroomhq/postiz-app --limit 20`
- **Result:** v2.21.6 (2026-04-12), v2.21.5 (2026-04-09), v2.21.4 (2026-03-29), v2.21.3 "Security Fixes" (2026-03-29). 3 releases in last 30 days.
- **Classification:** Confirmed fact

#### E9: No committed secrets in source
- **Claim:** No hardcoded API keys or credentials in source code
- **Command:** `grep -rlP '(api[_-]?key|secret|token|password)\s*[:=]\s*["..."][A-Za-z0-9_\-\.]{16,}' . --include='*.ts' --include='*.js'`
- **Result:** 0 matches
- **Classification:** Confirmed fact

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
