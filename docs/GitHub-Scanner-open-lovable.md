# Security Investigation: firecrawl/open-lovable

**Investigated:** 2026-04-17 | **Applies to:** main @ 69bd93b | **Repo age:** 619 days | **Stars:** 25,491 | **License:** MIT

| Field | Value |
|-------|-------|
| Report file | GitHub-Scanner-open-lovable.md (+ .html companion) |
| Repo | [github.com/firecrawl/open-lovable](https://github.com/firecrawl/open-lovable) |
| Short description | AI-powered tool that clones any website and recreates it as a modern React app using multiple LLM providers (Anthropic, OpenAI, Google, Groq) with sandboxed code execution via Vercel Sandbox or E2B. |
| Category | AI/LLM tooling |
| Subcategory | AI code generation platform |
| Verdict | caution |
| Scanned revision | main @ 69bd93b |
| Prompt version | v2.4 |
| Prior scan | None — first run |

## Verdict: Caution

**Unauthenticated API routes can execute arbitrary commands in sandboxed environments — safe for local dev, risky if deployed publicly.**

- **Warning:** API routes `/api/run-command` and `/api/run-command-v2` accept arbitrary shell commands via unauthenticated POST requests. Commands execute inside Vercel/E2B sandboxes, not on the host, but no auth gate prevents abuse if the app is deployed to a public URL.
- **Warning:** Zero formal code review across all 12 merged PRs. The V2 rewrite (PR #122, 100+ files) was self-merged with no reviews.
- **Warning:** No branch protection, no rulesets, no CODEOWNERS, no SECURITY.md — governance single-point-of-failure (C20). Anyone with write access can push directly to main.
- **Info:** CORS `Access-Control-Allow-Origin: *` on AI streaming and web scraping routes. Standard for local dev but dangerous on public deployments.
- **Positive:** Sandbox execution model isolates generated code from the host machine. All maintainer accounts are established (2+ years). No hardcoded secrets, no malicious lifecycle scripts, no prompt injection patterns detected.

## Trust Scorecard

- **Does anyone check the code?** — Red (Rare). Formal review rate: 0.0%. Any-review rate: 8.3% (1 of 12 merged PRs). No branch protection on main. Top contributor has 63.8% of commits but this is a multi-contributor repo, not a solo project — the low review rate is a process gap, not a structural limitation.
- **Do they fix problems quickly?** — Amber (Open fixes, not merged yet). No open CVEs, no security advisories. PR #176 ("fix: update dependencies to patch security vulnerabilities") is open but not yet merged. No evidence of ignored security reports.
- **Do they tell you about problems?** — Red (No advisory). No SECURITY.md, no published security advisories, no release notes (no releases exist at all). There is no channel for responsible disclosure and no mechanism to notify users of security fixes.
- **Is it safe out of the box?** — Amber (Local dev: yes. Public deployment: add auth first). For local development where the user supplies their own API keys: reasonably safe — sandbox isolates code execution. For public/shared deployment: the unauthenticated command execution endpoints and CORS wildcard mean anyone on the internet can use your sandbox. Distribution: git clone from main only, no pinned releases.

## What Should I Do?

### If you are using this for local development (most users)

1. **Clone and run locally — this is the intended use case.** The sandbox execution model (Vercel Sandbox / E2B) means generated code runs in an ephemeral remote container, not on your machine.
   - *Technical:* `git clone https://github.com/firecrawl/open-lovable.git && cd open-lovable && pnpm install && cp .env.example .env.local` — fill in your API keys.
   - *Plain English:* Download the code, install it, and add your own API keys. The app runs on your computer and sends AI requests to cloud services.

2. **Pin to a specific commit rather than tracking main.** There are no releases, so `main` is a moving target.
   - *Technical:* `git checkout 69bd93bae7a9c97ef989eb70aabe6797fb3dac89`
   - *Plain English:* Lock your copy to the version we just reviewed, so future changes do not affect you until you choose to update.

3. **Review your .env.local before running.** The app uses multiple API keys (Firecrawl, AI providers, Vercel/E2B). Each key has billing implications.
   - *Plain English:* Make sure you understand which services you are paying for before starting the app.

### If you are deploying this publicly

4. **Add authentication middleware before deploying.** The API routes at `/api/run-command`, `/api/run-command-v2`, `/api/install-packages`, `/api/install-packages-v2`, and `/api/kill-sandbox` have zero authentication. On a public URL, anyone can execute commands in your sandbox and rack up your cloud bill.
   - *Technical:* Add a Next.js middleware.ts that validates session/JWT/API key on all `/api/*` routes before the handler runs.
   - *Plain English:* Without a login system, anyone who finds your URL can use your AI credits and sandbox resources.

5. **Remove or restrict CORS wildcard headers.** The `Access-Control-Allow-Origin: *` on AI streaming and scraping routes means any website can make requests to your deployment.
   - *Technical:* Replace `'*'` with your specific frontend domain in `app/api/generate-ai-code-stream/route.ts` and `app/api/scrape-website/route.ts`.

## What We Found

### Finding 1: Unauthenticated Command Execution API Routes
- **Severity:** Warning
- **Status:** Active
- **What this means for you:** The app has API endpoints that run shell commands and install npm packages. These commands run inside a sandboxed container (Vercel Sandbox or E2B), not on your machine. However, there is no login or API key check — if you deploy this to a public URL, anyone who discovers it can run commands in your sandbox, install packages, and consume your cloud resources.
- **Threat model (F13):** An attacker who discovers the public URL can POST arbitrary commands to `/api/run-command`. The sandbox isolation limits damage to the ephemeral container — they cannot access the host filesystem or network. The primary risk is resource abuse (sandbox compute time, API credits) and potential data exfiltration from the sandbox environment.
- **Action:** Add authentication middleware to all API routes before any public deployment. For local-only use, this is low risk because only localhost can reach the endpoints.

### Finding 2: Zero Code Review Process
- **Severity:** Warning
- **Status:** Active
- **What this means for you:** None of the 12 merged pull requests received a formal code review. The V2 rewrite (PR #122, touching 100+ files across all API routes, sandbox providers, and the frontend) was merged by its author with zero reviews. This means security-relevant changes ship without a second pair of eyes.
- **Action:** If you rely on this project, watch the commit log for changes to API routes and sandbox provider code. Consider reviewing diffs yourself before pulling updates.

### Finding 3: Governance Single-Point-of-Failure (C20)
- **Severity:** Warning
- **Status:** Active
- **What this means for you:** There is no branch protection on the main branch. No rulesets. No CODEOWNERS file. No SECURITY.md. Anyone with write access to the repo can push directly to main without any automated gate. Combined with 25K+ stars and 4.9K forks, this means a compromised maintainer account could push malicious code that reaches thousands of users.
- **Threat model (F13):** Attacker paths include: phishing the maintainer's GitHub credentials, compromising a browser extension in the maintainer's session, or gaining access via a stale personal access token. Once write access is obtained, the attacker pushes to main — no review gate, no CI gate, no CODEOWNERS approval required.
- **Action (if you install):** Pin to a reviewed commit SHA. Monitor the repo's commit feed for unexpected pushes. **(If you maintain):** Enable branch protection on main at Settings > Branches > Add rule. Require at least 1 review before merge. Add a CODEOWNERS file covering `app/api/` and `lib/sandbox/`.

### Finding 4: CORS Wildcard on AI and Scraping Routes
- **Severity:** Info
- **Status:** Active / Informational
- **What this means for you:** Two API routes (`generate-ai-code-stream` and `scrape-website`) set `Access-Control-Allow-Origin: *`, which means any website can make cross-origin requests to these endpoints. For local development this is standard. For public deployments, it means a malicious website visited by the user could trigger AI code generation or website scraping using the deployment's API keys.
- **Action:** If deploying publicly, restrict the CORS origin to your frontend domain.

### Finding 5: Dependency Vulnerability
- **Severity:** Info
- **Status:** Active
- **What this means for you:** The `@anthropic-ai/sdk` dependency has 1 known vulnerability according to osv.dev. Dependabot data was not accessible (403 — admin scope required), so the full vulnerability picture is incomplete.
- **Action:** Run `npm audit` locally after installation to see the full advisory. Update `@anthropic-ai/sdk` to the latest version.

### Finding 6: Agent Rule File (Cursor)
- **Severity:** OK
- **Status:** Informational
- **What this means for you:** The file `components/app/.cursor/rules/home-page-components.md` is a Cursor IDE rule file that documents home page component structure for the migration. It contains no AI-directed imperative language, no secrets, no commands, and no model-obedience changes.
- **Imperative-verb list:** None found
- **Auto-load tier:** Tier 2 (conditionally auto-loaded — Cursor with path-specific glob matching)
- **Capability statement:** This file tells Cursor IDE about the expected directory structure for home page components during migration.
- **Risk statement:** If this file were compromised, a future attacker could inject instructions that affect every Cursor user working in the `components/app/(home)` path — but the current content is benign documentation.

## Executable File Inventory

### Quick Scan
- `/api/run-command/route.ts` — runs on POST request, executes arbitrary commands in sandbox, no auth. **Warning.**
- `/api/run-command-v2/route.ts` — runs on POST request, executes arbitrary commands in sandbox via provider, no auth. **Warning.**
- `/api/install-packages/route.ts` — runs on POST request, installs npm packages in sandbox, no auth. **Warning.**
- `/api/install-packages-v2/route.ts` — runs on POST request, installs npm packages in sandbox via provider, no auth. **Warning.**
- `/api/kill-sandbox/route.ts` — runs on POST request, kills active sandbox, no auth. **Warning.**
- `packages/create-open-lovable/lib/installer.js` — CLI scaffolding tool, runs execSync('npm install') with controlled input. **OK.**
- `components/app/.cursor/rules/home-page-components.md` — Cursor IDE rule file, documentation only. **OK.**

### File: app/api/run-command/route.ts
- **Trigger:** POST request to /api/run-command
- **Reads:** request.json() for `command` field; global.activeSandbox
- **Writes:** Executes arbitrary command in sandbox via `global.activeSandbox.runCommand()`
- **Network:** Communicates with sandbox runtime (Vercel/E2B cloud)
- **Injection channel:** User-supplied `command` string is passed directly to sandbox execution. No sanitization.
- **Secret-leak path:** None — sandbox is isolated from host secrets
- **Capability assessment:** Could execute any shell command the sandbox runtime allows. In worst case, if sandbox isolation fails, this becomes an RCE. In the normal case, damage is limited to the ephemeral container.

### File: app/api/run-command-v2/route.ts
- **Trigger:** POST request to /api/run-command-v2
- **Reads:** request.json() for `command` field; sandboxManager.getActiveProvider() or global.activeSandboxProvider
- **Writes:** Executes arbitrary command via provider.runCommand()
- **Network:** Communicates with sandbox runtime
- **Injection channel:** Same as run-command — user-supplied command passed to sandbox
- **Secret-leak path:** None
- **Capability assessment:** Same as run-command but routes through the sandbox manager abstraction layer.

### File: app/api/install-packages/route.ts
- **Trigger:** POST request to /api/install-packages
- **Reads:** request.json() for `packages` array; global.activeSandboxProvider
- **Writes:** Installs npm packages in sandbox. Has validation (dedup, filter empty strings).
- **Network:** Sandbox runtime + npm registry
- **Injection channel:** Package names come from request body. Some validation exists (dedup, type check) but no allowlist or regex filter on package name format.
- **Secret-leak path:** None
- **Capability assessment:** Could install any npm package in the sandbox. A malicious package name with postinstall hooks would execute in the sandbox container.

### File: packages/create-open-lovable/lib/installer.js
- **Trigger:** User runs `npx create-open-lovable`
- **Reads:** User input via inquirer prompts; .env template files
- **Writes:** Creates project directory, copies template files, runs `npm install` via execSync
- **Network:** npm registry (via npm install)
- **Injection channel:** None — command is hardcoded `npm install`, user input goes to file paths only
- **Secret-leak path:** None
- **Capability assessment:** Standard CLI scaffolding tool. execSync runs controlled npm install with cwd set to the new project directory.

### File: components/app/.cursor/rules/home-page-components.md
- **Trigger:** Auto-loaded by Cursor IDE when working in matching paths (Tier 2)
- **Reads:** None
- **Writes:** None
- **Network:** None
- **Injection channel:** If modified, could inject instructions into Cursor sessions
- **Secret-leak path:** None
- **Capability assessment:** Currently benign documentation. A future compromise could inject arbitrary Cursor instructions for anyone working on home page components.

## Suspicious Code Changes

| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|-------------|-----------|-----------|---------|
| [#122](https://github.com/firecrawl/open-lovable/pull/122) | V2 rewrite — 100+ files, all API routes, sandbox providers, new features | developersdigest | developersdigest | No (0 reviews) | Self-merged massive change with zero review. Added run-command-v2, install-packages-v2, scrape-website routes — all without auth. |
| [#109](https://github.com/firecrawl/open-lovable/pull/109) | Vercel sandbox support — rewrote sandbox infrastructure | MFCo | developersdigest | No (0 reviews) | Security-critical sandbox architecture change with zero review. |

## Timeline

- **2025-08-08** — REPO CREATED. firecrawl/open-lovable created with E2B sandbox integration.
- **2025-08-26** — SANDBOX MIGRATION. PR #109 migrates from E2B to Vercel Sandbox. Merged with 0 reviews.
- **2025-09-02** — SANDBOX REVERTED then merged. PR #109 merged, then immediately reverted (PR #110), suggesting instability.
- **2025-09-02 to 2025-09-10** — V2 DEVELOPMENT. developersdigest pushes V2 rewrite directly and via PR #122 (self-merged, 0 reviews). Adds all v2 API routes, sandbox providers, and complete frontend redesign.
- **2025-09-27** — LAST COMMUNITY PR. PR #136 (README update for Morph API key) is the last merged community contribution.
- **2025-11-19** — V3 PUSH. Direct push to main "v3" by developersdigest. No PR, no review. Last commit on the repo.
- **2025-11-19 to 2026-04-17** — ACTIVITY GAP. 5 months with no commits. 38 open PRs, 131 open issues accumulating.

## Repo Vitals

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Age | 619 days | Relatively young |
| Stars | 25,491 | Very popular — high blast radius |
| Forks | 4,898 | Heavily forked |
| Open issues | 131 | Many unaddressed, includes spam |
| Open PRs | 38 | Community contributions not being merged |
| Last commit | 2025-11-19 (5 months ago) | Possibly stale/unmaintained |
| Contributors | 11 | Small team, dominated by 1 person |
| Top contributor share | developersdigest: 63.8% | Near-solo maintenance |
| Releases | 0 | No versioned releases, install from main only |
| License | MIT | Permissive |
| Branch protection | None | No gates on main |
| SECURITY.md | None | No disclosure policy |
| OSSF Scorecard | Not indexed | Not available for this repo |
| Dependencies | 67 direct, 12 dev | Large dependency tree |

## Investigation Coverage

| Coverage item | Status |
|---------------|--------|
| Repo metadata (Step 1) | Complete |
| Maintainer background | Complete — owner + top 3 contributors checked |
| OSSF Scorecard | Not indexed (API returned no data) |
| Dependabot alerts | 403 (admin scope required) — status unknown |
| osv.dev fallback | Queried 20 of 67 direct deps, 1 vulnerability found |
| Secrets-in-history | Not scanned (gitleaks not available) |
| API budget at Step 5 | 4982/5000 remaining. PR sample: 12 (full — only 12 exist) |
| Merged PRs reviewed | 12 of 12 (complete) |
| Security-relevant PR diffs read | 3 of 5 title-hit PRs |
| Step A tarball extraction | Succeeded, 336 files |
| Executable files inspected | 7 of 7 inspected (5 Warning, 2 OK, 0 Critical) |
| README install-paste scan (Step 7.5) | Run — 0 paste blocks found |
| CI-amplified rule detection (Step 2.5) | Run — 0 CI-amplified files. 1 static agent rule file found. |
| Prompt-injection scan | Run — 0 strings matched imperative-targeting-scanner pattern |
| Distribution channels | 1 of 1 (git clone from main). No releases to verify against. |
| pull_request_target usage | 0 workflows |
| Windows surface | No .ps1/.bat/.cmd files in repo — N/A |
| Monorepo inner-package scan | 2 package.json files found. Root: no lifecycle scripts. create-open-lovable: no lifecycle scripts. |

## Evidence Appendix

### E1: No authentication on command execution routes (Priority evidence)
- **Claim:** API routes run-command and run-command-v2 accept arbitrary commands without authentication.
- **Command:** `grep -nP 'auth|session|cookie|jwt|bearer|middleware|verify|login' app/api/run-command/route.ts app/api/run-command-v2/route.ts`
- **Result:** No matches. Files contain no authentication logic. POST handler directly reads `command` from request body and passes to sandbox execution.
- **Classification:** Confirmed fact

### E2: Zero formal code review rate (Priority evidence)
- **Claim:** 0% of merged PRs received formal review approval.
- **Command:** `gh pr list -R firecrawl/open-lovable --state merged --limit 300 --json number,reviewDecision,reviews`
- **Result:** 12 merged PRs. reviewDecision is empty string on all 12. reviews.length > 0 on exactly 1 (PR #33).
- **Classification:** Confirmed fact

### E3: No branch protection on main (Priority evidence)
- **Claim:** No branch protection rules exist on the default branch.
- **Command:** `gh api repos/firecrawl/open-lovable/branches/main/protection` returned 404. `gh api repos/firecrawl/open-lovable/rulesets` returned []. `gh api repos/firecrawl/open-lovable/rules/branches/main` returned [].
- **Result:** All three checks confirm no protection.
- **Classification:** Confirmed fact (org rulesets are unknown due to scope gap — 403 on admin:org)

### E4: CORS wildcard on AI streaming route
- **Claim:** generate-ai-code-stream route sets Access-Control-Allow-Origin: *
- **Command:** `grep -nP 'Access-Control-Allow-Origin' app/api/generate-ai-code-stream/route.ts`
- **Result:** Line 1883: `'Access-Control-Allow-Origin': '*'`
- **Classification:** Confirmed fact

### E5: Dependency vulnerability
- **Claim:** @anthropic-ai/sdk has 1 known vulnerability.
- **Command:** `curl -s "https://api.osv.dev/v1/query" -d '{"package":{"name":"@anthropic-ai/sdk","ecosystem":"npm"}}'`
- **Result:** 1 vulnerability returned
- **Classification:** Confirmed fact (osv.dev data)

### E6: No releases
- **Claim:** The repo has zero releases.
- **Command:** `gh release list -R firecrawl/open-lovable --limit 20`
- **Result:** No output (empty)
- **Classification:** Confirmed fact

### E7: 5-month activity gap
- **Claim:** Last commit was 2025-11-19, 5 months before this scan.
- **Command:** `gh api repos/firecrawl/open-lovable/commits?per_page=1 -q '.[0].commit.author.date'`
- **Result:** 2025-11-19T15:15:21Z
- **Classification:** Confirmed fact

### E8: Community health 37%
- **Claim:** No SECURITY.md, no Code of Conduct, no CONTRIBUTING file.
- **Command:** `gh api repos/firecrawl/open-lovable/community/profile`
- **Result:** health: 37, security_policy: false, coc: false, contrib: false
- **Classification:** Confirmed fact
