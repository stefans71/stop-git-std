# Security Investigation: pmndrs/zustand

**Investigated:** 2026-04-17 | **Applies to:** main @ 3201328 (v5.0.12) | **Repo age:** 2,565 days | **Stars:** 57,760 | **License:** MIT

| Field | Value |
|-------|-------|
| Report file | GitHub-Scanner-zustand-v3.md (+ .html companion) |
| Repo | https://github.com/pmndrs/zustand |
| Short description | Lightweight React state management library (1.4K LOC, zero runtime deps) used by 57K+ stargazers |
| Category | Web framework |
| Subcategory | React state management |
| Verdict | clean |
| Scanned revision | main @ 3201328 (v5.0.12) |
| Prompt version | V2.4 |
| Prior scan | GitHub-Scanner-zustand.html (2026-04-16, V2.3) |
| OSSF Scorecard | 5.9 / 10 (14 checks) |
| Methodology | path-a |

## Verdict: clean

**Safe to install.** zustand v5.0.12 ships zero runtime dependencies, zero install hooks, and zero executable files. The source is 1,447 lines of TypeScript with no dangerous code patterns.

- **Zero runtime dependencies** — nothing executes on install except npm placing the module files
- **Zero hooks, zero install scripts** — no preinstall/postinstall/prepare lifecycle scripts
- **No agent-rule files** — no CLAUDE.md, AGENTS.md, .cursor/rules, or similar
- **Excellent CI** — 8 workflows with SHA-pinned actions, matrix testing across React 18/19 and TypeScript 4.5–5.9
- **Active multi-maintainer project** — 67% review rate, 30 commits in last 90 days, OSSF Maintained 10/10
- **Governance gaps exist but do not affect your install** — no SECURITY.md and no confirmed branch protection on main (see findings below)

## Trust Scorecard

- **Does anyone check the code?** — Green (Regular). Any-review rate 67%, formal review 54.3%. Multi-maintainer repo (top contributor 38.2% of commits). OSSF Code-Review: 6/10.
- **Do they fix problems quickly?** — Green. Zero open security issues, zero open CVE PRs. 30 commits and 1 issue activity in last 90 days. OSSF Maintained: 10/10.
- **Do they tell you about problems?** — Amber (No advisory channel). No SECURITY.md, no published advisories. Zero historical CVEs — nothing to disclose yet, but no channel exists if one is found.
- **Is it safe out of the box?** — Green. npm channel verified (versioned, shasum ed36f647), zero runtime dependencies, zero Warning+ findings on the default install path.

## What Should I Do?

### If you are installing zustand today

1. **Install normally.** `npm install zustand` is safe. The package has zero runtime dependencies and zero install hooks.
   - *Plain English:* Just install it. Nothing runs behind the scenes.
2. **Pin your version** in package.json to avoid surprise updates: use `"zustand": "5.0.12"` instead of `"^5.0.12"`.
   - *Plain English:* Lock the version number so you only get updates when you choose to.
3. **Subscribe to releases** at https://github.com/pmndrs/zustand/releases to watch for security-relevant changes.
   - *Plain English:* Click "Watch" on the GitHub page so you hear about updates.

### If you maintain a zustand fork or downstream dependency

1. **Consider adding a SECURITY.md** with a private reporting channel if your fork handles sensitive data.
2. **Enable branch protection** on your fork's main branch.
3. **Monitor the governance gap** (Finding F1) — if pmndrs adds branch protection or CODEOWNERS in the future, that strengthens the upstream supply chain.

## What We Found

### Finding F0: No vulnerability disclosure channel
- **Severity:** Warning
- **Status:** Active
- **What happened:** zustand has no SECURITY.md file and no published security advisories. The OSSF Security-Policy check scores 0/10.
- **What this means for you:** If someone discovers a vulnerability in zustand, there is no documented private channel to report it. Vulnerabilities may be reported as public issues, which exposes all users before a fix is available.
- **Action:** If you maintain a fork, add a SECURITY.md. As a user, subscribe to zustand releases to catch any security-relevant updates.

### Finding F1: No confirmed branch protection on main
- **Severity:** Warning
- **Status:** Active
- **What happened:** Classic branch protection returned 404. Repo-level rulesets returned empty array. Rules on default branch returned empty array. CODEOWNERS not found. Org-level rulesets could not be checked (admin:org scope not available — state is UNKNOWN, not confirmed absent).
- **Threat model:** An attacker who compromises a maintainer's GitHub session (via phishing, stolen token, malicious browser extension, or compromised IDE plugin) could push directly to main and trigger the publish workflow, shipping malicious code to npm. The blast radius is 57,760+ stars and all downstream npm consumers.
- **What this means for you:** This is a governance process gap. It does not mean the code is unsafe today — it means there is one fewer guardrail preventing a future compromise.
- **Mitigating factors:** The repo has multiple active maintainers with 10+ year old accounts. The review rate (67% any-review) indicates a culture of review even without enforcement. All CI actions are SHA-pinned. The Copilot SWE agent's supply-chain pinning PR (#3395) shows awareness of these issues.
- **Action:** Pin your zustand version and review changelogs before upgrading.

### Finding F2: CI workflow token permissions too broad
- **Severity:** Info
- **Status:** Active
- **What happened:** OSSF Token-Permissions scored 0/10. The publish.yml and docs.yml workflows explicitly scope their permissions, but other workflows (test.yml, test-multiple-*.yml, compressed-size.yml, preview-release.yml) use default GITHUB_TOKEN permissions which are broader than needed.
- **What this means for you:** This affects the CI environment, not your local install. A compromised CI step in a test workflow could theoretically escalate its permissions.
- **Action:** No user action needed. Maintainers could add `permissions: {}` at the workflow level and grant only what each job needs.

### Finding F3: One CI action uses version tag instead of SHA pin
- **Severity:** Info
- **Status:** Active
- **What happened:** `pmndrs/docs/.github/workflows/build.yml@v3` in docs.yml uses a version tag. All other 23 uses directives are SHA-pinned.
- **What this means for you:** This is an internal pmndrs org reusable workflow used only for docs deployment — not for code publishing. The risk is limited to docs page compromise.
- **Action:** No user action needed.

### Finding F4: Dependabot alerts disabled
- **Severity:** Info
- **Status:** Active
- **What happened:** Dependabot alerts API returned 403: "Dependabot alerts are disabled for this repository."
- **What this means for you:** With zero runtime dependencies, Dependabot's absence has minimal impact on end users. It would mainly catch vulnerabilities in devDependencies used during development.
- **Action:** No user action needed.

## Executable File Inventory

zustand has no executable files in the always-investigate list. There are no hook files, install scripts, lifecycle scripts, agent-rule files, Dockerfiles, or README paste-blocks.

**CI workflows (8 files):** All inspected. No dangerous patterns found. No pull_request_target usage. No curl|bash patterns. No secret exfiltration. 23/24 actions SHA-pinned. The publish workflow (publish.yml) uses npm provenance (`id-token: write`) which is a positive signal.

## Suspicious Code Changes

No suspicious code changes identified. The sampled PRs show routine maintenance: documentation updates, CI improvements, TypeScript compatibility fixes, and dependency updates.

| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|-------------|-----------|-----------|---------|
| #3395 | Pin actions/deploy-pages to SHA | Copilot agent | dai-shi | No | Self-merge of bot PR in 7 min — low risk (benign change) |

## Timeline

- **2019-04-09** — REPO CREATED — zustand created under pmndrs org
- **2024-10-14** — MAJOR RELEASE — v5.0.0 published
- **2026-02-10** — CI HARDENING — PR #3381 pins all GitHub Actions to commit SHAs
- **2026-02-23** — CI HARDENING — PR #3395 pins actions/deploy-pages to SHA (Copilot-authored)
- **2026-03-16** — LATEST RELEASE — v5.0.12 published
- **2026-04-14** — LAST COMMIT — README link update (#3466)
- **2026-04-17** — THIS SCAN — investigating main @ 3201328

## Repo Vitals

| Metric | Value | Interpretation |
|--------|-------|---------------|
| Stars | 57,760 | Extremely popular — one of the most-starred React libraries |
| Forks | 2,035 | High fork count, active ecosystem |
| Age | 2,565 days (7 years) | Mature, established project |
| License | MIT | Permissive, no compliance issues |
| Runtime deps | 0 | Minimal attack surface |
| Source lines | 1,447 (16 TS files) | Small, auditable codebase |
| Contributors | 30+ | Healthy contributor base |
| Top contributor share | 38.2% (dai-shi) | Multi-maintainer, not solo |
| Formal review rate | 54.3% (300 PR sample) | Above green threshold |
| Any-review rate | 67.0% (300 PR sample) | Healthy review culture |
| Open issues | 2 | Very few open issues |
| OSSF Scorecard | 5.9/10 | Above average |
| Last release | v5.0.12 (2026-03-16) | Active releases |
| Last commit | 2026-04-14 | Active development |
| Dependabot | Disabled | Gap in automated vulnerability scanning |
| SECURITY.md | Absent | No disclosure channel |
| Branch protection | Not confirmed | Governance gap |

## Investigation Coverage

| Check | Result |
|-------|--------|
| Repo metadata | Queried successfully |
| Maintainer background | Top 4 checked — all established (10+ year accounts) |
| OSSF Scorecard | 5.9/10 (14 checks indexed) |
| osv.dev fallback | Not queried (zero runtime dependencies) |
| Dependabot alerts | Disabled for this repo (403) |
| gitleaks (secrets-in-history) | Not scanned (gitleaks not available) |
| API budget at Step 5 | 4,971/5,000 remaining. PR sample: 300 (full) |
| Branch protection | Classic 404 + rulesets [] + org unknown (scope gap) |
| CODEOWNERS | Not found (4 locations checked) |
| Merged PR sample | 300 of 895 total (33.5% sampled) |
| Security-relevant PRs inspected | 4 title hits reviewed, 1 detailed diff (#3395) |
| Tarball extraction | 143 files extracted |
| Step A grep (dangerous patterns) | All categories scanned — 0 concerning hits |
| Step B targeted reads | 1 file (devtools.ts) — RegExp.exec(), not eval() |
| Executable files inspected | 0 of 0 (none exist) — 8 CI workflows inspected separately |
| README install-paste scan | Run — 0 paste blocks found |
| Agent-rule files (Step 2.5) | CI-amplified: 0. Static: 0 |
| Prompt-injection scan | 0 strings matched imperative-targeting-scanner pattern, 0 findings |
| Distribution channels | 1 of 1 resolved (npm verified, git clone trivial) |
| Windows surface | N/A — no .ps1/.bat/.cmd files in repo |
| pull_request_target usage | 0 workflows |
| Inner package.json lifecycle | 3 files found, 0 lifecycle scripts |
| Monorepo enumeration | 3 package.json files (root + 2 examples), 0 lifecycle scripts |

## Evidence Appendix

### E1: Branch protection — no classic rule on main
- **Claim:** No classic branch protection rule configured on main
- **Command:** `gh api repos/pmndrs/zustand/branches/main/protection`
- **Result:** `{"message":"Not Found","status":"404"}`
- **Classification:** Confirmed fact

### E2: No rulesets on main
- **Claim:** No repo-level rulesets and no rules apply to main
- **Command:** `gh api repos/pmndrs/zustand/rulesets` and `gh api repos/pmndrs/zustand/rules/branches/main`
- **Result:** Both returned `[]`
- **Classification:** Confirmed fact

### E3: Org rulesets unknown
- **Claim:** Org-level rulesets could not be checked
- **Command:** `gh api orgs/pmndrs/rulesets`
- **Result:** 404 + "This API operation needs the admin:org scope"
- **Classification:** Confirmed fact — state is unknown (scope gap), not absent

### E4: OSSF Scorecard
- **Claim:** Overall score 5.9/10
- **Command:** `curl -s https://api.securityscorecards.dev/projects/github.com/pmndrs/zustand`
- **Result:** Score 5.9/10 with per-check breakdown (see OSSF Scorecard detail section)
- **Classification:** Confirmed fact

### E5: PR review rate
- **Claim:** Formal review 54.3%, any-review 67.0%
- **Command:** `gh pr list -R pmndrs/zustand --state merged --limit 300 --json reviewDecision,reviews`
- **Result:** 163/300 formal, 201/300 any-review
- **Classification:** Confirmed fact (300/895 sample)

### E6: Zero runtime dependencies
- **Claim:** zustand has no runtime dependencies
- **Command:** `python3 -c "import json; print(json.load(open('package.json')).get('dependencies',{}))"` in scan dir
- **Result:** `{}` (empty dict)
- **Classification:** Confirmed fact

### E7: No SECURITY.md
- **Claim:** No security policy file exists
- **Command:** `gh api repos/pmndrs/zustand/community/profile -q '.files.security_policy'`
- **Result:** `null` (false)
- **Classification:** Confirmed fact

### E8: SHA-pinned actions
- **Claim:** 23/24 uses directives are SHA-pinned
- **Command:** grep of all workflow files for `uses:` directives
- **Result:** Only `pmndrs/docs/.github/workflows/build.yml@v3` uses a version tag
- **Classification:** Confirmed fact

### E9: No dangerous code patterns
- **Claim:** Zero eval, network, secrets, XSS, CORS patterns in source
- **Command:** Step A grep battery on extracted source
- **Result:** Only hit was RegExp.exec() in devtools.ts — false positive
- **Classification:** Confirmed fact

### E10: Dependabot disabled
- **Claim:** Dependabot alerts are disabled
- **Command:** `gh api repos/pmndrs/zustand/dependabot/alerts`
- **Result:** HTTP 403: "Dependabot alerts are disabled for this repository"
- **Classification:** Confirmed fact

### E11: Token-Permissions gap
- **Claim:** OSSF Token-Permissions scored 0/10
- **Command:** OSSF Scorecard API
- **Result:** Token-Permissions: 0/10 — "detected GitHub workflow tokens with excessive permissions"
- **Classification:** Confirmed fact
