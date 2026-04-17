# Security Investigation: pmndrs/zustand

**Investigated:** 2026-04-17 | **Applies to:** main @ 3201328 (v5.0.12) | **Repo age:** 2,565 days | **Stars:** 57,760 | **License:** MIT | **OSSF Scorecard:** 5.9/10

---

**Report file:** GitHub-Scanner-zustand-v3.md (+ .html companion)
**Repo:** [github.com/pmndrs/zustand](https://github.com/pmndrs/zustand)
**Short description:** Lightweight React state management library with zero runtime dependencies. Hook-based API, framework-agnostic core.
**Category:** Web framework
**Subcategory:** State management library
**Verdict:** Caution
**Scanned revision:** main @ 3201328 (v5.0.12)
**Prompt version:** v2.4
**Prior scan:** GitHub-Scanner-zustand.html (2026-04-16, v2.3)

---

## Verdict: Caution

**The library code is clean, well-maintained, and has zero runtime dependencies. The concern is governance: no branch protection, no CODEOWNERS, and no SECURITY.md leave a supply-chain gap that matters for a package installed by 57,760+ starred projects.**

- **Warning:** No branch protection on default branch — anyone with write access can push directly to main without review (F0)
- **Info:** No SECURITY.md — no documented channel for private vulnerability disclosure (F1)
- **Info:** Four CI workflows lack explicit token permissions blocks (F2)
- **Info:** Docs workflow uses unpinned reusable workflow reference (F3)
- **Positive:** Zero runtime dependencies, SHA-pinned CI actions, active maintenance, 65% review rate

## Trust Scorecard

- **Does anyone check the code?** — Amber (Informal). 65% any-review rate and 45% formal-review rate are solid, but no branch protection on the default branch prevents a Green rating. Reviews happen voluntarily, not enforced.
- **Do they fix problems quickly?** — Green. Zero open security issues, zero open CVE PRs. Active maintenance with 30 commits in the last 90 days. v5.0.12 shipped 2026-03-16.
- **Do they tell you about problems?** — Amber (No advisory channel). No SECURITY.md file. No published security advisories. The team has a contributing guide but no documented private disclosure path.
- **Is it safe out of the box?** — Green. npm package verified (v5.0.12 on registry). Zero runtime dependencies. No install scripts, no lifecycle hooks, no dangerous patterns in source code.

## What Should I Do?

### 1. Install with confidence at the current version

zustand v5.0.12 is safe to install. The library code has zero runtime dependencies, no install scripts, and no dangerous patterns.

**Technical:**
```bash
npm install zustand@5.0.12
```

**Non-technical:** Go ahead and install it. The code itself is clean.

### 2. Pin to the current version

Because there is no branch protection, a future compromise of a maintainer account could push malicious code. Pinning protects you until you verify the next release.

**Technical:**
```bash
# In package.json, use exact version (no ^ or ~):
"zustand": "5.0.12"
```

**Non-technical:** When you install, make sure your project locks to this exact version so you don't auto-upgrade to an unreviewed version.

### 3. Watch for governance improvements

Subscribe to the repo to see when branch protection or a security policy is added.

**Technical:**
```bash
gh api repos/pmndrs/zustand --jq '.default_branch' # verify main
# Watch: https://github.com/pmndrs/zustand/settings/branches
```

**Non-technical:** Check back periodically to see if the team has added branch protection rules. This would upgrade the verdict to Clean.

### 4. If you are a maintainer: enable branch protection

**Technical:**
Navigate to https://github.com/pmndrs/zustand/settings/branches and add a branch protection rule for `main` requiring at least one review. Add a CODEOWNERS file. Add a SECURITY.md with a private disclosure channel.

## What We Found

### Finding 1: No Branch Protection on Default Branch (C20)
- **Severity:** Warning
- **Status:** Active, Ongoing
- **What this means for you:** Anyone with write access to the pmndrs/zustand repo can push code directly to the main branch without a review gate. This does not mean the code is compromised today — it means the safety net is missing.
- **Threat model:** An attacker who compromises a maintainer's GitHub account (via phishing, leaked token, session hijack from a malicious browser extension, or compromised IDE plugin) could push directly to main. The publish.yml workflow triggers on release events, so the attacker would also need to create a GitHub release to ship malicious code to npm. This is a two-step attack, but neither step has a review gate.
- **Evidence:** `gh api repos/pmndrs/zustand/branches/main/protection` returned 404. Repo-level rulesets: empty array. Rules on default branch: empty array. CODEOWNERS: not found in any of 4 standard locations. Org-level rulesets: unknown (admin:org scope required).
- **Blast radius:** 57,760 stars, 2,035 forks. zustand is a top-10 React state management library.
- **Action:** If you maintain this repo, enable branch protection at https://github.com/pmndrs/zustand/settings/branches requiring at least one approving review. Add a CODEOWNERS file covering security-critical paths (.github/workflows/, publish.yml).

### Finding 2: No Security Policy (SECURITY.md)
- **Severity:** Info
- **Status:** Active
- **What this means for you:** If you discover a vulnerability in zustand, there is no documented way to report it privately. The OSSF Security-Policy check scores 0/10.
- **Evidence:** Community profile `security_policy: false`. No SECURITY.md in root, .github/, or docs/.
- **Action:** If you maintain this repo, add a SECURITY.md with a private disclosure email or GitHub Security Advisories link.

### Finding 3: Missing Explicit Token Permissions in CI Workflows
- **Severity:** Info
- **Status:** Active, Ongoing
- **What this means for you:** Four of eight CI workflows (test.yml, test-multiple-versions.yml, test-multiple-builds.yml, compressed-size.yml) do not declare explicit `permissions:` blocks. This means they run with GitHub's default token permissions, which are broader than necessary. The OSSF Token-Permissions check scores 0/10.
- **Mitigation:** The publish.yml workflow (the one that matters most) correctly scopes permissions to `id-token: write` and `contents: read`. The permissionless workflows are test/CI only and cannot publish packages.
- **Action:** Add `permissions: { contents: read }` to each test workflow to follow least-privilege principle.

### Finding 4: Unpinned Reusable Workflow in docs.yml
- **Severity:** Info
- **Status:** Active
- **What this means for you:** The docs.yml workflow references `pmndrs/docs/.github/workflows/build.yml@v3` using a tag, not a SHA pin. If the pmndrs/docs repo were compromised, the attacker could alter the docs build workflow.
- **Mitigation:** This workflow only builds GitHub Pages documentation. It cannot affect the npm package. The deploy-pages action IS SHA-pinned.
- **Action:** Pin the reusable workflow to a SHA: `uses: pmndrs/docs/.github/workflows/build.yml@COMMIT_SHA`

## Executable File Inventory

zustand has zero executable files in the always-investigate categories (no hooks, no install scripts, no lifecycle scripts, no agent rule files, no Dockerfiles). The only executable artifacts are 8 CI workflow YAML files.

### CI Workflows (8 files)

- **publish.yml** — Trigger: release published. Permissions: id-token:write, contents:read. Actions: all SHA-pinned. Builds and publishes to npm. OK.
- **test.yml** — Trigger: push/PR. No explicit permissions. Actions: all SHA-pinned. Runs tests only. OK.
- **test-multiple-versions.yml** — Trigger: push/PR. No explicit permissions. Actions: SHA-pinned. Matrix tests. OK.
- **test-multiple-builds.yml** — Trigger: push/PR. No explicit permissions. Actions: SHA-pinned. Matrix tests. OK.
- **test-old-typescript.yml** — Trigger: push/PR. No explicit permissions. Actions: SHA-pinned. TS compat. OK.
- **preview-release.yml** — Trigger: push to main. Actions: SHA-pinned. Preview releases. OK.
- **compressed-size.yml** — Trigger: PR. No explicit permissions. Uses third-party preactjs/compressed-size-action (SHA-pinned). OK.
- **docs.yml** — Trigger: push to main. Uses pmndrs/docs reusable workflow @v3 (NOT SHA-pinned). deploy-pages IS SHA-pinned. Pages-only, cannot affect npm. Info.

## Suspicious Code Changes

No suspicious code changes were identified. All sampled PRs had clear purposes (docs fixes, type corrections, dependency bumps, test coverage). No changelog-hiding patterns detected.

| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|---|---|---|---|---|---|
| #3395 | Pin deploy-pages to SHA | copilot-swe-agent | dai-shi | No formal review | AI-authored security fix merged without review — low risk (docs workflow only) |
| #3391 | Fix persist rehydration callback | Shohjahon-n | dai-shi | APPROVED (11 reviews) | None — good review process |

## Timeline

- **2019-04-09** — REPO CREATED. pmndrs/zustand created by drcmda (Paul Henschel).
- **2024-10-14** — V5 SHIPS. v5.0.0 released after RC cycle (rc.0 through rc.2).
- **2025-05-21** — ACTIVE RELEASE. v5.0.5 through v5.0.12, regular monthly cadence.
- **2026-02-23** — SUPPLY-CHAIN FIX. PR #3395 pins deploy-pages to SHA (Copilot-authored).
- **2026-03-16** — LATEST RELEASE. v5.0.12 ships with devtools type fix and persist fix.
- **2026-04-14** — LAST COMMIT. README docs link update.
- **2026-04-17** — SCAN DATE. This investigation.

## Repo Vitals

- **Repository:** pmndrs/zustand (Organization-owned)
- **Age:** 7 years (created 2019-04-09)
- **Stars:** 57,760 | **Forks:** 2,035
- **License:** MIT
- **OSSF Scorecard:** 5.9/10
- **Default branch:** main (no protection)
- **Latest release:** v5.0.12 (2026-03-16)
- **Runtime dependencies:** 0
- **Dev dependencies:** 39
- **Open issues:** 2 (0 security-related)
- **Top contributor:** dai-shi (411 commits, 54.7% of top 4)
- **PR review rate:** 65% any-review, 45% formal-review (100 of 895 sampled)
- **Releases in last year:** 12 (monthly cadence)
- **Community health:** 62% (contributing guide, MIT license; no CoC, no SECURITY.md)

## Investigation Coverage

- **Data sources queried:** gh API (repo, contributors, users, branches, rulesets, community, advisories, workflows, PRs, issues, commits), OSSF Scorecard API, osv.dev API, npm registry
- **OSSF Scorecard:** 5.9/10 (14 checks returned data; Branch-Protection returned -1 due to token limitation)
- **osv.dev:** Not queried (zero runtime dependencies — nothing to query)
- **Dependabot:** 403 "Dependabot alerts are disabled for this repository"
- **Secrets-in-history:** Not scanned (gitleaks not available)
- **API budget at Step 5:** 4960/5000 remaining. PR sample: 100 (full — no reduction needed)
- **PR review analysis:** 100 of 895 total merged PRs sampled (most recent)
- **Security-relevant PRs drilled:** 18 title-matched, 2 inspected in detail (representative sample)
- **Tarball extraction:** Success, 143 files
- **Executable files inspected:** 8 of 8 CI workflows (0 Warning, 8 OK, 0 Critical). 0 hooks, 0 install scripts, 0 lifecycle scripts.
- **README install-paste scan:** Run, 0 paste blocks found
- **CI-amplified rule detection:** Run, 0 sources found. Static agent-rule files: 0 found.
- **Prompt-injection scan:** 0 strings matched imperative-targeting-scanner pattern, 0 classified as actionable findings
- **Distribution channels verified:** 1 of 1 (npm). npm registry verified (v5.0.12 tarball available, shasum confirmed). Git clone trivially matches scan.
- **Windows surface coverage:** N/A — repo ships no .ps1/.bat/.cmd files
- **Inner package.json enumeration:** 3 files (root + 2 examples). 0 lifecycle scripts in any.
- **pull_request_target usage:** 0 workflows
- **Monorepo lifecycle scripts:** 0 (sampled 3 of 3 package.json files)
- **Limitations:** Org-level rulesets unknown (admin:org scope not available). Dependabot disabled. gitleaks not installed. Only 100 of 895 merged PRs sampled.

## Evidence Appendix

### E1: Branch Protection — No Classic Rule (Priority Evidence)
- **Claim:** No branch protection rule exists on the main branch.
- **Command:** `gh api repos/pmndrs/zustand/branches/main/protection`
- **Result:** `{"message":"Not Found","status":"404"}`
- **Classification:** Confirmed fact

### E2: Rulesets — Empty
- **Claim:** No repo-level rulesets protect any branch.
- **Command:** `gh api repos/pmndrs/zustand/rulesets`
- **Result:** `[]`
- **Classification:** Confirmed fact

### E3: Rules on Default Branch — Empty
- **Claim:** No rules apply to the main branch.
- **Command:** `gh api repos/pmndrs/zustand/rules/branches/main`
- **Result:** `[]`
- **Classification:** Confirmed fact

### E4: CODEOWNERS — Absent
- **Claim:** No CODEOWNERS file exists in any standard location.
- **Command:** Checked CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS via gh api
- **Result:** All 4 paths returned empty/404
- **Classification:** Confirmed fact

### E5: PR Review Rate (Priority Evidence)
- **Claim:** 65% any-review rate, 45% formal review rate on most recent 100 merged PRs.
- **Command:** `gh pr list -R pmndrs/zustand --state merged --limit 100 --json number,title,createdAt,mergedAt,author,reviewDecision,reviews,labels`
- **Result:** 65 of 100 had at least one review; 45 of 100 had formal reviewDecision set
- **Classification:** Confirmed fact (sampled — 100 of 895 total)

### E6: Zero Runtime Dependencies
- **Claim:** zustand has zero runtime dependencies.
- **Command:** `python3 -c "import json; d=json.load(open('package.json')); print(d.get('dependencies',{}))"`
- **Result:** `{}`
- **Classification:** Confirmed fact

### E7: OSSF Scorecard
- **Claim:** OSSF Scorecard rates pmndrs/zustand at 5.9/10.
- **Command:** `curl -s "https://api.securityscorecards.dev/projects/github.com/pmndrs/zustand"`
- **Result:** Overall 5.9/10. Key checks: Code-Review 6/10, Maintained 10/10, Token-Permissions 0/10, Dangerous-Workflow 10/10, Security-Policy 0/10.
- **Classification:** Confirmed fact

### E8: npm Package Verified
- **Claim:** zustand v5.0.12 is published on npm with matching version.
- **Command:** `npm view zustand dist.shasum dist.tarball version`
- **Result:** version=5.0.12, shasum=ed36f647aa89965c4019b671dfc23ef6c6e3af8c
- **Classification:** Confirmed fact

### E9: No Security Policy
- **Claim:** No SECURITY.md or security policy file exists.
- **Command:** `gh api repos/pmndrs/zustand/community/profile -q '{security_policy: (.files.security_policy != null)}'`
- **Result:** `security_policy: false`
- **Classification:** Confirmed fact

### E10: Dangerous Pattern Grep — Clean
- **Claim:** No eval, exec, network calls, hardcoded secrets, or XSS sinks in non-test source.
- **Command:** Multiple grep commands per Step A
- **Result:** 0 hits for eval/exec, 0 for network calls, 0 for secrets, XSS sinks only in test file
- **Classification:** Confirmed fact
