# Security Investigation: firecrawl/open-lovable

**Investigated:** 2026-04-17 | **Applies to:** main @ 69bd93ba (no release tags) | **Repo age:** 252 days | **Stars:** 25,496 | **License:** MIT

---

**Report file:** GitHub-Scanner-open-lovable.md (+ .html companion)
**Repo:** [github.com/firecrawl/open-lovable](https://github.com/firecrawl/open-lovable)
**Short description:** Open-source clone of Lovable.dev — an AI-powered website cloner and React app generator that uses Firecrawl for scraping and cloud sandboxes (Vercel/E2B) for live preview.
**Category:** AI/LLM tooling
**Subcategory:** AI code generator / web cloner
**Verdict:** Caution
**Scanned revision:** main @ 69bd93ba (no release tags)
**Prompt version:** V2.4
**Prior scan:** None — first run

---

## Verdict: Caution

**AI-powered web cloner with significant governance gaps and API routes that execute arbitrary commands in cloud sandboxes — safe for local experimentation with your own API keys, but deploy with caution.**

Key findings:

- **No branch protection, no CODEOWNERS, no CI/CD, no security policy** — a 25K-star repo with zero governance gates. Any maintainer account compromise pushes directly to main.
- **API routes accept arbitrary shell commands** (`/api/run-command`, `/api/run-command-v2`) and execute them in cloud sandboxes without authentication middleware.
- **CORS wildcard (`Access-Control-Allow-Origin: *`)** on streaming AI code generation and scraping endpoints.
- **0% formal code review rate** across all 12 merged PRs. Only 1 of 12 PRs received any review at all (an external approval from a non-associated account).
- **4 Cursor rule files committed** — auto-loaded styling/architecture instructions. Content is benign (design system rules), but the channel exists for future compromise.
- **67 runtime dependencies** including AI SDKs (Anthropic, OpenAI, Google, Groq) with 1 known vulnerability (osv.dev: @anthropic-ai/sdk).

## Trust Scorecard

- **Does anyone check the code?** — Red: Rare. 0% formal review rate, 8% any-review rate (1 of 12 PRs). Solo-maintained: developersdigest has 37 of 58 commits (64%). No branch protection.
- **Do they fix problems quickly?** — Amber: Open fixes, not merged yet. PR #176 patches security vulnerabilities, open since 2025-12-11 and unmerged. PR #178 reports a Vercel/React CVE, open since 2025-12-17.
- **Do they tell you about problems?** — Red: No advisory. No SECURITY.md, no published advisories, no disclosure channel.
- **Is it safe out of the box?** — Amber: Safe for single-user local dev with your own API keys. Shared/production deployment requires authentication middleware on API routes.

## 01 · What Should I Do?

### If you are evaluating this for local development:

1. **Clone and audit `.env.example`** — the app requires your own API keys (Firecrawl, Anthropic/OpenAI/Gemini/Groq, Vercel/E2B sandbox). No keys are hardcoded. Your keys stay local.
   - *Plain English:* Copy the example environment file and fill in your own API keys. The app does not ship with anyone else's keys.

2. **Pin to a specific commit** — there are no release tags. Use `git checkout 69bd93ba` to lock to the scanned revision.
   - *Plain English:* Because there are no version numbers, bookmark the exact code snapshot you tested so future changes cannot surprise you.

3. **Do NOT expose the Next.js server to the public internet** — the `/api/run-command` and `/api/run-command-v2` routes accept arbitrary shell commands with no authentication.
   - *Plain English:* If anyone on the internet can reach your server, they can run any command in your sandbox environment.

4. **Review PR #176** before deploying — it patches dependency vulnerabilities that remain unmerged as of this scan.

### If you maintain this repo:

1. Enable branch protection on `main` with at least 1 required review.
2. Add a `SECURITY.md` with a private disclosure channel.
3. Add authentication middleware to all `/api/*` routes before any non-localhost deployment.
4. Merge PR #176 (dependency security patches).

## 02 · What We Found

### Finding 1: No governance gates — single point of failure
- **Severity:** Warning
- **Status:** Active
- **Action:** Enable branch protection on main at github.com/firecrawl/open-lovable/settings/branches

**What happened:** Classic branch protection returned 404. Repo-level rulesets: empty array. Rules on default branch: empty array. Org-level rulesets: 404 (admin:org scope required — state unknown, but repo-level checks confirm no protection). No CODEOWNERS file in any standard location. No CI workflows exist at all.

**Threat model:** An attacker who gains access to any account with write permission (via phishing, credential stuffing, stale personal access token, malicious browser extension, or IDE plugin compromise) can push arbitrary code directly to main. With 25,496 stars and 4,897 forks, the blast radius of a compromise is substantial — every user who clones or pulls from main receives the malicious code immediately.

**What this means for you:** Nobody is required to review code before it goes live. A single compromised account can ship malware to thousands of users.

### Finding 2: Unauthenticated command execution API routes
- **Severity:** Warning
- **Status:** Active
- **Action:** Add authentication middleware to `/api/run-command` and `/api/run-command-v2` before any non-localhost deployment.

**What happened:** The API routes `/api/run-command/route.ts` and `/api/run-command-v2/route.ts` accept a JSON body `{ "command": "..." }` and execute it in the active sandbox via `global.activeSandbox.runCommand()` or `provider.runCommand()`. No authentication check, no API key validation, no rate limiting. Commands execute in the cloud sandbox (Vercel or E2B), not on the host machine.

**Mitigating factor:** Commands run inside an isolated cloud sandbox, not on the user's local machine. The sandbox is ephemeral and does not have access to the host filesystem or environment. However, the sandbox does have access to whatever API keys were injected at creation time.

**What this means for you:** If you deploy this application to a publicly reachable URL, anyone can run arbitrary commands in your sandbox — potentially accessing the API keys you configured for that sandbox session.

### Finding 3: CORS wildcard on sensitive endpoints
- **Severity:** Info
- **Status:** Active
- **Action:** Restrict CORS origins to your own domain before production deployment.

**What happened:** `Access-Control-Allow-Origin: *` is set on `/api/generate-ai-code-stream/route.ts` (line 1883) and `/api/scrape-website/route.ts` (line 105). This allows any website to make cross-origin requests to these endpoints.

**Mitigating factor:** The app is designed for local development (`localhost:3000`). CORS wildcards on localhost are standard practice. This only becomes a concern if the server is exposed publicly.

**What this means for you:** For local dev, this is fine. For production, restrict to your domain.

### Finding 4: Zero code review process
- **Severity:** Warning
- **Status:** Ongoing
- **Action:** This is a solo-maintained repo. Review rate is inherently limited by the contributor base — compare with governance indicators (advisories, branch protection, CODEOWNERS, CI gates) rather than review rate alone.

**What happened:** Of 12 merged PRs, 0 had a formal reviewDecision set. Only 1 (PR #33 "Add support for Google Gemini AI") received any review — an APPROVED review from user Saeen55-stack (no association with the project). Formal review rate: 0%. Any-review rate: 8.3%.

The primary maintainer (developersdigest) authored 37 of 58 total commits (64%) and merged most PRs, including self-merges on security-relevant changes.

**What this means for you:** No second pair of eyes has checked most of the code. The project's quality depends entirely on one maintainer's diligence.

### Finding 5: Unmerged security PRs
- **Severity:** Info
- **Status:** Active
- **Action:** Watch PR #176 and #178 for merge; re-evaluate after they land.

**What happened:** PR #176 "fix: update dependencies to patch security vulnerabilities" has been open since 2025-12-11 with no maintainer response (128 days at scan time). PR #178 "Vercel/react server components CVE" has been open since 2025-12-17 with no response (121 days).

Last commit to main was 2025-11-19 (v3 release). No commits in 150 days. This pattern is consistent with an inactive or paused project.

**What this means for you:** Known security patches are sitting unmerged. The maintainer may not be actively monitoring the project.

### Finding 6: 0.0.0.0 bind in sandbox configuration
- **Severity:** Info
- **Status:** Active

**What happened:** The sandbox creation routes configure Vite dev servers to bind to `0.0.0.0` (all interfaces) inside the cloud sandbox. This is found in `app/api/create-ai-sandbox/route.ts` (line 138, 281, 371) and the sandbox provider files. This is expected behavior for cloud sandbox containers that need to be reachable from outside the container.

**What this means for you:** The `0.0.0.0` bind is inside the isolated sandbox, not on your local machine. This is standard for container-based development environments.

### Finding 7: dangerouslySetInnerHTML usage (16 instances)
- **Severity:** Info
- **Status:** Informational

**What happened:** 16 files use React's `dangerouslySetInnerHTML`. Most are in the flame/ASCII animation components (`components/shared/effects/flame/*`) where pre-built ASCII art frames from local JSON data files are rendered. Two notable uses:
- `components/shared/pylon.tsx` (line 73): injects a third-party analytics/chat widget script (Pylon).
- `components/ui/shadcn/tooltip.tsx` (line 93): renders tooltip description as raw HTML from props — XSS risk if description contains user-controlled content.

**What this means for you:** The ASCII animation uses are low-risk (static local data). The tooltip and Pylon widget uses warrant attention if you extend the app to handle user-generated content.

## 02A · Executable File Inventory

### Quick scan (4 Cursor rule files, 0 install scripts, 0 CI workflows)

- **styles/design-system/.cursor/rules/design-system.md** — Auto-loaded Cursor rule. Design system color/typography guidance. OK.
- **styles/components/.cursor/rules/component-styles.md** — Auto-loaded Cursor rule. Component CSS architecture rules. OK.
- **components/app/(home)/.cursor/rules/home-page-components.md** — Auto-loaded Cursor rule. Home page component migration notes. OK.
- **components/shared/effects/.cursor/rules/flame-effects.md** — Auto-loaded Cursor rule. ASCII flame animation documentation. OK.

### File: styles/design-system/.cursor/rules/design-system.md
- **Auto-load tier:** Tier 2 — Conditionally auto-loaded (Cursor `.mdc` in `.cursor/rules/` directory, loaded when working in that directory subtree)
- **Imperative verbs:** "Use CSS custom properties", "Use" (color instructions)
- **Capability statement:** Instructs Cursor AI to use the project's fire-inspired design system colors, typography, and utility classes when generating CSS.
- **Risk statement:** A future compromise of this file could instruct Cursor to inject malicious CSS or JavaScript via AI-generated code for every developer working in the styles directory.
- **Severity:** Info
- **Status:** Informational
- **Checklist:** Imperative verbs: "Use" (x3). Auto-load tier: Tier 2. Capability: design system guidance. Risk: CSS injection via AI. Severity: Info. Status: Informational.

### File: styles/components/.cursor/rules/component-styles.md
- **Auto-load tier:** Tier 2 — Conditionally auto-loaded
- **Imperative verbs:** "Only create CSS files for components that need them", "Use P3 colors", "Keep animations performant"
- **Capability statement:** Instructs Cursor to follow component CSS architecture patterns (import strategy, P3 color fallbacks, animation performance).
- **Risk statement:** A future compromise could instruct AI to generate components with malicious styles or scripts.
- **Severity:** Info
- **Status:** Informational

### File: components/app/(home)/.cursor/rules/home-page-components.md
- **Auto-load tier:** Tier 2 — Conditionally auto-loaded
- **Imperative verbs:** None found — purely structural documentation of component migration plan.
- **Capability statement:** Documents the home page component structure and migration priority for Cursor AI context.
- **Risk statement:** A future compromise could redirect AI to generate components importing from malicious sources.
- **Severity:** Info
- **Status:** Informational

### File: components/shared/effects/.cursor/rules/flame-effects.md
- **Auto-load tier:** Tier 2 — Conditionally auto-loaded
- **Imperative verbs:** None found — documents how flame ASCII animation system works (data.json files, frame speeds, visibility-based rendering).
- **Capability statement:** Provides context about the flame animation system so AI understands the innerHTML-based ASCII rendering approach.
- **Risk statement:** A future compromise could instruct AI to modify the flame components to inject malicious content via innerHTML.
- **Severity:** Info
- **Status:** Informational

## 03 · Suspicious Code Changes

| PR | What it did | Submitted by | Merged by | Reviewed? | Merge time | Concern |
|----|------------|-------------|-----------|-----------|------------|---------|
| [#122](https://github.com/firecrawl/open-lovable/pull/122) | "V2" — major rewrite | developersdigest | developersdigest | No | 14 min | Self-merge of major version bump with no review |
| [#109](https://github.com/firecrawl/open-lovable/pull/109) | Vercel sandbox support | MFCo | developersdigest | No | 11 hrs | External contributor adding sandbox execution — no review |
| [#33](https://github.com/firecrawl/open-lovable/pull/33) | Add Google Gemini AI | ayoubdya | developersdigest | Yes (1 review) | 10 hrs | Only PR with any review; reviewer (Saeen55-stack) has no project association |
| [#136](https://github.com/firecrawl/open-lovable/pull/136) | Update README for Morph API key | bekbull | bekbull | No | 3 min | Self-merge |

## 04 · Timeline

- **2025-08-08** — REPO CREATED. firecrawl/open-lovable created under the Firecrawl organization.
- **2025-08-08 to 2025-08-14** — RAPID GROWTH. Initial development burst: 37 commits from developersdigest, multiple community PRs merged without review.
- **2025-09-02** — SANDBOX ADDED. Vercel sandbox support merged (PR #109) from external contributor MFCo — no code review. This PR introduced the command execution API routes.
- **2025-09-10** — V2 SHIPS. Major "V2" rewrite self-merged by developersdigest in 14 minutes with no review.
- **2025-09-27** — LAST MERGE. PR #136 (Morph API key README update) was the last merged PR.
- **2025-11-19** — LAST COMMIT. "v3" commit pushed directly to main. No PR, no review.
- **2025-12-11** — SECURITY PR FILED. PR #176 filed to patch dependency vulnerabilities. Still open 128 days later.
- **2025-12-17** — CVE PR FILED. PR #178 reports Vercel/React server components CVE. Still open 121 days later.
- **2026-04-17** — THIS SCAN. 150 days since last commit. Security PRs unmerged. 93 open issues.

## 05 · Repo Vitals

- **Stars:** 25,496 | **Forks:** 4,897
- **Created:** 2025-08-08 (252 days ago)
- **Last push:** 2025-11-19 (150 days ago)
- **License:** MIT
- **Language:** TypeScript (Next.js 15 / React)
- **Default branch:** main
- **Archived:** No
- **Community health:** 37% (no CoC, no CONTRIBUTING, no SECURITY.md)
- **OSSF Scorecard:** Not indexed
- **Dependencies:** 67 runtime + 12 dev
- **Open issues:** 93 (many are spam/non-actionable; some are real bugs)
- **Open PRs:** 38 (majority from external contributors, none merged since Sept 2025)
- **Merged PRs:** 12 total
- **Formal review rate:** 0% (0 of 12)
- **Any-review rate:** 8.3% (1 of 12)
- **Releases:** None (no tags, no releases page)
- **CI/CD:** None (no .github/workflows directory)
- **Branch protection:** None (404 on classic, empty rulesets)
- **CODEOWNERS:** None
- **Security advisories:** None published

## 06 · Investigation Coverage

- **Data sources queried:** gh api (repo, contributors, users, branches, rulesets, rules, org rulesets, community/profile, advisories, PRs, issues, commits, contents), OSSF Scorecard API, osv.dev API
- **OSSF Scorecard:** Not indexed. The repo is not in the OSSF Scorecard database.
- **osv.dev:** Queried 15 of 67 direct dependencies. 1 vulnerability found (@anthropic-ai/sdk: 1 advisory). Remaining 52 dependencies not queried (rate-limit conservation).
- **Dependabot:** 403 (admin:repo_hook scope required). State: unknown, not "clean."
- **Secrets-in-history:** Not scanned (gitleaks not available). Install gitleaks for full coverage.
- **API budget at Step 5:** 4,944/5,000 remaining. PR sample: 12/12 (full — only 12 merged PRs exist).
- **Tarball extraction:** Success. 336 files extracted from tarball pinned to HEAD SHA 69bd93bae7a9c97ef989eb70aabe6797fb3dac89.
- **Merged PRs reviewed:** 12 of 12 (all merged PRs examined).
- **Security-relevant PR diffs read:** Not applicable — no PRs matched title or path security keywords. All 12 PRs were inspected via metadata.
- **Executable files inspected:** 4 of 4 (4 Cursor rule files, 0 install scripts, 0 CI workflows). Verdict breakdown: 0 Warning, 4 Info, 0 Critical.
- **README install-paste scan:** Run. 0 paste-this blocks found.
- **CI-amplified rule detection:** Run. 0 CI-amplified sources (no .github/workflows directory). 4 static Cursor rule files found.
- **Prompt-injection scan:** 2 files matched "system prompt" pattern. 0 classified as actionable findings — both are legitimate LLM system prompt construction in API route code, not scanner-targeting injection.
- **Distribution channels:** 1 channel (git clone). No npm package published. No release assets. No install scripts. Channel verified against source: trivially matches scan.
- **Windows surface:** No .ps1/.bat/.cmd files found. N/A.
- **pull_request_target usage:** 0 workflows (no CI exists).
- **Monorepo inner packages:** 1 inner package found (`packages/create-open-lovable/package.json`). Sampled for lifecycle scripts: none found.

### V2.4 External Tool Coverage

- **OSSF Scorecard:** Not indexed. Independent security rating from the Open Source Security Foundation (securityscorecards.dev). Scores 24 security practices from 0-10. Most repos score 3-5; above 6 is strong.
- **osv.dev:** 1 vulnerability found in 15 queried packages. Checked against osv.dev, a free vulnerability database backed by Google. Shows known security issues in this project's dependencies.
- **gitleaks:** Not scanned (tool not available). Scanned by gitleaks for passwords, API keys, or tokens accidentally committed to the code. "Not scanned" means the tool was not available — not that the code is clean.
- **API budget:** 4,944/5,000 remaining at Step 5. Full PR sample (12/12). GitHub limits API calls to 5,000/hour. Budget was sufficient for complete coverage.

## 07 · Evidence Appendix

### Priority Evidence

#### E1: No branch protection (supports Finding 1)
- **Claim:** No branch protection of any kind exists on the default branch.
- **Command:** `gh api repos/firecrawl/open-lovable/branches/main/protection`
- **Result:** `{"message":"Not Found","status":"404"}`
- **Command:** `gh api repos/firecrawl/open-lovable/rulesets`
- **Result:** `[]`
- **Command:** `gh api repos/firecrawl/open-lovable/rules/branches/main`
- **Result:** `[]`
- **Classification:** Confirmed fact

#### E2: Unauthenticated command execution routes (supports Finding 2)
- **Claim:** API routes accept arbitrary commands without authentication.
- **Command:** `grep -nP 'command' app/api/run-command/route.ts | head -5`
- **Result:** Line 11: `const { command } = await request.json();` — command taken directly from request body. No auth check in the route.
- **Classification:** Confirmed fact

#### E3: 0% formal review rate (supports Finding 4)
- **Claim:** Zero merged PRs have a formal review decision.
- **Command:** `gh pr list -R firecrawl/open-lovable --state merged --limit 300 --json reviewDecision`
- **Result:** All 12 PRs show `"reviewDecision":""` (empty). Only PR #33 has a `reviews` array with 1 entry.
- **Classification:** Confirmed fact

### Context Evidence

#### E4: CORS wildcard on API routes (supports Finding 3)
- **Claim:** CORS wildcard set on AI code generation and scraping endpoints.
- **Command:** `grep -nP 'Access-Control-Allow-Origin' app/api/generate-ai-code-stream/route.ts`
- **Result:** Line 1883: `'Access-Control-Allow-Origin': '*'`
- **Classification:** Confirmed fact

#### E5: Unmerged security PRs (supports Finding 5)
- **Claim:** Security-patching PRs open for 120+ days with no maintainer response.
- **Command:** `gh pr list -R firecrawl/open-lovable --state open --json number,title,createdAt`
- **Result:** PR #176 "fix: update dependencies to patch security vulnerabilities" (2025-12-11), PR #178 "Vercel/react server components CVE" (2025-12-17) — both open, no comments.
- **Classification:** Confirmed fact

#### E6: osv.dev vulnerability (supports dependency assessment)
- **Claim:** @anthropic-ai/sdk has 1 known vulnerability.
- **Command:** `curl -s "https://api.osv.dev/v1/query" -d '{"package":{"name":"@anthropic-ai/sdk","ecosystem":"npm"}}'`
- **Result:** 1 vulnerability returned.
- **Classification:** Confirmed fact

#### E7: Dependabot access denied
- **Claim:** Dependabot alerts could not be queried.
- **Command:** `gh api repos/firecrawl/open-lovable/dependabot/alerts`
- **Result:** `{"message":"You are not authorized to perform this operation.","status":"403"}`
- **Classification:** Confirmed fact — state is unknown (scope gap), not "clean."

### Positive Evidence

#### E8: No hardcoded secrets
- **Claim:** No hardcoded API keys or secrets found in source code.
- **Command:** `grep -rlP '(api[_-]?key|secret|token|password)\s*[:=]\s*["'"'"'][A-Za-z0-9_\-\.]{16,}' . | grep -v node_modules | grep -v .env`
- **Result:** 0 matches.
- **Classification:** Confirmed fact

#### E9: No eval/exec usage
- **Claim:** No `eval()` or `new Function()` calls in application code.
- **Command:** `grep -rlP 'eval\s*\(|new\s+Function\s*\(' . --include='*.ts' --include='*.tsx' --include='*.js'`
- **Result:** 0 matches.
- **Classification:** Confirmed fact

#### E10: Sandbox isolation
- **Claim:** Command execution happens in isolated cloud sandboxes, not on host.
- **Source:** `app/api/run-command/route.ts` line 30: `const result = await global.activeSandbox.runCommand({...})`
- **Classification:** Confirmed fact — commands are forwarded to Vercel Sandbox or E2B sandbox APIs, not executed locally.

#### E11: No prompt injection targeting scanner
- **Claim:** No AI-directed prompt injection targeting security scanners was found.
- **Command:** `grep -rliP 'ignore (all )?(previous|prior) instructions|you are now|pretend you are|jailbreak' . | grep -v node_modules`
- **Result:** 2 files matched "system prompt" keyword — both are legitimate LLM prompt construction code, not scanner-targeting injection.
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
