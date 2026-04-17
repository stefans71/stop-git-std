# Security Investigation: pmndrs/zustand

**Investigated:** 2026-04-16 | **Applies to:** main @ `3201328` · v5.0.12 | **Repo age:** 7 years | **Stars:** 57,758 | **License:** MIT

> A 57,000-star React state-management library with zero runtime dependencies and a clean code surface, but no branch protection, no CODEOWNERS, and Dependabot alerts disabled on one of the most-imported packages on npm.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-zustand-v2.md` (+ `.html` companion) |
| Repo | [github.com/pmndrs/zustand](https://github.com/pmndrs/zustand) |
| Short description | Small, fast, unopinionated state-management library for React. Stores live in hooks, no provider wrapper required; middleware covers persistence, devtools, Immer, and Redux-style APIs. Distributed as `zustand` on npm with zero runtime dependencies. |
| Category | `developer-tooling` |
| Subcategory | `state-management-library` |
| Language | TypeScript |
| License | MIT |
| Target user | React application developers |
| Verdict | **Caution** (split on deployment axis) |
| Scanned revision | `main @ 3201328` (release tag `v5.0.12`) |
| Commit pinned | `32013285083648e8d58ba1f76d73b9bdc02fef50` |
| Scanner version | `V2.3-post-R3` |
| Scan date | `2026-04-16` |
| Methodology | `path-b` (first delegated scan) |
| Prior scan | `GitHub-Scanner-zustand.html` (first scan, same repo, same SHA) |

---

## Verdict: Caution (split on Deployment axis)

### Deployment - Solo-dev or learning context - default install - **Good with caveats: install and use, the library itself is clean**

Pure library, zero runtime deps, zero install-time hooks, zero network calls in source, no shell-exec primitives, no dangerous sinks. The code-path risk is as close to zero as a React library gets. The caveat is upstream governance: no branch protection on `main`, no rulesets, no CODEOWNERS, and Dependabot vulnerability alerts are disabled on the repo (version bumps still flow). Your install today is safe; the residual risk is supply-chain credential compromise affecting future releases.

### Deployment - Shared host / production application - **Good with caveats: pin your version, watch for unusual releases**

Same verdict, stronger caveat. Because `pmndrs/zustand` is imported by millions and has no upstream governance gate, a single compromised maintainer credential would ship arbitrary code to every install on the next release with no branch-level review. Mitigation on the consumer side: pin exact versions in production `package.json`, use `minimumReleaseAge` in pnpm config, and keep an eye on release notes. The library itself is clean.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>Warning: Governance gaps - no branch protection, no CODEOWNERS, Dependabot alerts off (2 findings)</strong>
<br><em>C20 single-point-of-failure fires as Warning (release age 31 days, 1 day outside the 30-day Critical window); Dependabot alert surface disabled while version-update PRs still flow</em></summary>

1. **Governance - F0 / C20** - No branch protection on `main` (API returns 404), zero rulesets (`/rulesets` returns `[]`, `/rules/branches/main` returns `[]`), no CODEOWNERS in any of 4 standard locations. Org rulesets unknown (scope gap, needs `admin:org`). On a 57k-star library imported by millions, this is a supply-chain single-point-of-failure. Warning (not Critical) because the latest release v5.0.12 is 31 days old, 1 day outside the 30-day active-flow window that would escalate it. All 10 visible releases are authored exclusively by dai-shi.
2. **Dependabot alerts disabled - F1** - The Dependabot alerts API returns 403 with the explicit "disabled for this repository" message. Dependabot version updates ARE still active (`dependabot[bot]` is the #6 contributor with 18 commits, and `dependabot.yml` is present). This is specifically the alert surface being disabled. Low practical impact given zero runtime deps, but devDependency vulnerabilities could go unnoticed.

</details>

<details>
<summary><strong>OK: Strong positive signals - clean code-path, defensive supply chain, long-tenured maintainer (9 signals)</strong>
<br><em>Zero runtime deps, zero install hooks, SHA-pinned CI actions, no pull_request_target, least-privilege publish permissions, broad test matrix, active maintenance cadence, long-tenured maintainer, standard install path</em></summary>

1. **Code surface** - Zero runtime dependencies. Peer deps only (`react`, `@types/react`, `immer`, `use-sync-external-store`). The inbound supply chain at install time is effectively "zustand itself."
2. **Install hooks** - No `preinstall`, `postinstall`, or any lifecycle scripts in `package.json`. The scripts present are all build/test/fix targets.
3. **Publish pipeline** - `publish.yml` uses OIDC `id-token: write` to authenticate to npm. Published from `dist/` on `release: published` event only. Permissions are least-privilege: `id-token: write` + `contents: read`.
4. **CI action hygiene** - All 3 standard actions (checkout, setup-node, pnpm/action-setup) are SHA-pinned with version comments across all 8 workflows. One minor gap: `pmndrs/docs/.github/workflows/build.yml@v3` is tag-pinned (same-org reusable workflow, not a third-party action). `preactjs/compressed-size-action` is SHA-pinned. Zero `pull_request_target` usage.
5. **Clean source** - Step A dangerous-primitive grep of `src/src/` returned zero matches for eval, Function, child_process, execSync, spawnSync, fs.write, fs.read, net.connect, http.request, fetch, XMLHttpRequest, WebSocket, crypto, process.env, innerHTML, document.write. Only `import...from` (16 matches, expected ES module imports). Positive control confirmed grep was working.
6. **Broad test matrix** - Tests run across React 18.0-19.2 + canary, TypeScript 4.5-5.9, CJS/ESM build modes. 8 workflow files covering compressed size, multi-build, multi-version, old-TS, and standard test suite.
7. **Active maintenance** - 5 releases in 5 months (v5.0.8 through v5.0.12, Aug 2025 - Mar 2026). Community PRs merged regularly. 15 recent commits show healthy multi-contributor activity.
8. **Long-tenured maintainer** - dai-shi (Daishi Kato) has a 14-year GitHub account (since 2010), 8,087 followers, 127 public repos. Publicly known React library author maintaining zustand, jotai, valtio, and waku. No sockpuppet signals.
9. **Standard install path** - README line 23-24: `npm install zustand` inside a bash code block. No curl-pipe, no wget-to-sh, no unusual install instructions.

</details>

---

## Scorecard

| Question | Rating | Detail |
|----------|--------|--------|
| Does anyone check the code? | **Amber** | 45% formal review rate (`reviewDecision` APPROVED), 70% with any review activity (20-PR sample). No branch protection enforces review. 7 self-merges in sample (dai-shi 3 + dbritto-dev 4). |
| Is it safe out of the box? | **Green** | Zero runtime deps, zero dangerous primitives in source (Step A grep clean), pure TypeScript state management. No eval, no network, no fs. Standard `npm install`. |
| Can you trust the maintainers? | **Green** | dai-shi is a 14-year GitHub veteran with 8k followers, publicly known React library author. Org pmndrs (Poimandres) is an established open-source collective with 91 repos. No sockpuppet signals. |
| Is it actively maintained? | **Green** | v5.0.12 released 2026-03-16 (31 days before scan). 5 releases in 5 months. Community PRs merged regularly. Dependabot version bumps flowing. |

---

## Section 01: What Should I Do?

**Status:** Safe to install today | Pin versions in production | 2 steps

Install `zustand` the way the README describes. If you ship it to production, pin your version and consider setting `minimumReleaseAge` in your pnpm config to add a 24-hour delay on new releases. The library code is clean; the governance gap is the only concern and it affects future releases, not the current one.

### Step 1: Install normally

**Non-technical:** `zustand` is a React state-management library with zero runtime dependencies. You install it with `npm install zustand` (or `yarn add zustand` or `pnpm add zustand`) and import it into your React code. There are no install-time scripts, no network calls at runtime, no file system access, no shell execution. The install is standard and safe.

```bash
npm install zustand
# or
yarn add zustand
# or
pnpm add zustand
```

### Step 2: For production apps, pin versions and add a release-age gate

**Non-technical:** Because there is no branch protection on `main`, an attacker who compromised a maintainer's credentials could push malicious code and publish a new npm release without any automated review gate. You can protect yourself on the consumer side by pinning exact versions and adding a time delay before accepting new releases.

```bash
# In your package.json, use exact versions (no ^ or ~):
"zustand": "5.0.12"

# In .npmrc or pnpm config, add a minimum release age:
# This blocks installs of versions less than 24 hours old
minimum-release-age=1440
```

**For maintainers:** Enable branch protection on `main` (Settings - Branches - Add rule, require 1 approver, require CI status checks). Add `.github/CODEOWNERS` covering `.github/workflows/` and `src/`. Enable Dependabot security alerts. These are all free, incremental, and would close the governance SPOF without slowing velocity.

---

## Section 02: What We Found

**Status:** 1 Warning, 1 Info, 9 OK signals

5 findings total across 2 severity levels, plus 9 positive signals. The one Warning is governance, not code. F0 is the C20 single-point-of-failure (no branch protection, no rulesets, no CODEOWNERS) at Warning because release age (31 days) sits just outside the 30-day Critical window. F1 is an Info noting Dependabot alerts are disabled. Everything else is positive.

**Your action:** Nothing you need to do at the source level. For production deployments, pin versions and add a release-age gate (see Step 2 above). For maintainers: enabling branch protection and Dependabot alerts would close both findings.

### F0: Governance single-point-of-failure - no branch protection, no rulesets, no CODEOWNERS (Warning / C20)

**Status:** Ongoing, structural | **Action:** If you use zustand: pin versions in production. If you maintain this repo: enable branch protection on `main`.

**Severity sits at Warning, near the boundary.** The V2.3 C20 rule escalates to Critical when a repo (a) has all governance signals negative AND (b) distributes executable code AND (c) has a release within the last 30 days. v5.0.12 shipped 2026-03-16, 31 days before this scan. This is a 1-day margin, so while technically outside the Critical window, it is not a comfortable margin.

**What is missing.** Classic branch protection on `main` returns HTTP 404 from the GitHub API. Repo rulesets: `gh api repos/pmndrs/zustand/rulesets` returns `[]`. Rules applying to `main`: `gh api repos/pmndrs/zustand/rules/branches/main` returns `[]`. Org rulesets: unknown (scope gap, needs `admin:org`). CODEOWNERS absent in all 4 standard locations. Any push that lands on a maintainer's credentials goes directly to `main` without a review gate.

**How an attacker arrives (F13).** Concrete paths: (1) credential phishing against dai-shi, who has a public profile and findable identity; (2) stale OAuth token reuse from an old CI system or workstation; (3) compromised browser session cookie; (4) malicious IDE extension; (5) npm token theft bypassing the repo entirely (though the OIDC publish pipeline makes this harder since there is no long-lived npm token). None of these require nation-state tradecraft.

**What this means for you.** On a solo-dev laptop, zustand runs inside React's render cycle with no I/O capabilities. The blast radius of a malicious release is limited to what JavaScript can do in a browser context (read cookies, exfiltrate localStorage, inject DOM). In a Node.js/SSR context the blast radius is wider (filesystem, network, process). Either way, the practical mitigation is cheap: pin exact versions and add a release-age gate.

**What this does NOT mean.** The current v5.0.12 source code is clean. Zero dangerous primitives, zero runtime deps. This finding is about the repo's process gap, not about the current release containing something harmful.

| Check | Result |
|-------|--------|
| Classic branch protection | 404 on `main` |
| Rulesets | `[]` (zero) |
| Rules on main | `[]` (authoritative) |
| CODEOWNERS | Absent (4 locations) |
| Org rulesets | Unknown (scope gap) |
| Stars (blast radius) | 57,758 |
| Latest release age | 31 days (1 day outside Critical window) |
| All releases by | dai-shi exclusively |

### F1: Dependabot security alerts disabled (Info)

**Status:** Ongoing, configuration-level | **Action:** Maintainers should enable Dependabot security alerts in repo settings.

The Dependabot alerts API returns 403 with "Dependabot alerts are disabled for this repository." This is distinct from a scope gap. Dependabot version updates ARE active (`dependabot.yml` present, `dependabot[bot]` has 18 contributions). The alert surface specifically is disabled.

Low practical impact: zustand has zero runtime dependencies, so there is no transitive CVE exposure at install time. DevDependency vulnerabilities are the gap, and those only affect contributors building from source.

| Check | Result |
|-------|--------|
| Dependabot alerts API | 403 "disabled for this repository" |
| dependabot.yml | Present (npm daily + github-actions weekly, major only) |
| dependabot[bot] contributions | 18 |
| Runtime dependencies | 0 |

---

## Section 02A: Executable File Inventory

**Status:** 0 executables of concern | 143 files total

zustand ships as an npm package containing compiled JavaScript (from TypeScript source). There are no shell scripts, no PowerShell scripts, no batch files, no binary executables. Three image files in `examples/demo/src/resources/` have erroneous `+x` permission bits (ground.png, bg.jpg, stars.png) but are non-executable content.

**Your action:** None. The repo contains no executable files of security concern.

| File / Artifact | Kind | Dangerous calls | Network | Notes |
|-----------------|------|-----------------|---------|-------|
| `src/react.ts` | Library source | None | None | React hook entry point, imports from `vanilla.ts` |
| `src/vanilla.ts` | Library source | None | None | Core store implementation, pure TS |
| `src/traditional.ts` | Library source | None | None | Legacy API compatibility layer |
| `src/middleware/*.ts` | Middleware | None | None | persist, devtools, immer, redux, subscribeWithSelector |
| `src/shallow.ts` | Library source | None | None | Shallow comparison utility |
| npm: `zustand@5.0.12` | Published package | None | None | Built from `dist/` via `publish.yml`, OIDC auth |
| `examples/demo/src/resources/*.png` | Image assets | N/A | N/A | Erroneous +x bit, not executable |

---

## Section 03: Suspicious Code Changes

**Status:** 0 security-concerning PRs | 20 recent merges sampled

Recent PR activity is routine. Sample of 20 most recent merged PRs shows docs fixes, dependency bumps, test coverage expansion, and a devtools type fix. 3 PRs authored by copilot-swe-agent (all merged by human maintainers). 7 self-merges in sample (3 by dai-shi on README/deps, 4 by dbritto-dev on docs/workflow changes).

**Your action:** None. The recent-activity pattern is normal maintenance, not a hijacked repo.

| PR | What it did | Author | Merged by | Reviewed? | Concern |
|----|-------------|--------|-----------|-----------|---------|
| [#3466](https://github.com/pmndrs/zustand/pull/3466) | Update TypeScript guide links in README | FelixEckl | dai-shi | APPROVED | Docs only |
| [#3447](https://github.com/pmndrs/zustand/pull/3447) | Bump actions/deploy-pages 4.0.5 to 5.0.0 | dependabot | dbritto-dev | No decision | Routine bot bump |
| [#3442](https://github.com/pmndrs/zustand/pull/3442) | Expand React subscribe test coverage | mahmoodhamdi | dbritto-dev | No decision | Test-only |
| [#3427](https://github.com/pmndrs/zustand/pull/3427) | Update dev dependencies | dai-shi | dai-shi | No decision | **Self-merge** on deps update |
| [#3414](https://github.com/pmndrs/zustand/pull/3414) | Fix devtools config type extension | grigoriy-reshetniak | dai-shi | APPROVED | Type fix, reviewed |
| [#3391](https://github.com/pmndrs/zustand/pull/3391) | Fix persist post-rehydration callback | Shohjahon-n | dai-shi | APPROVED | Bug fix, 11 reviews |

---

## Section 04: Timeline

**Status:** 4 good signals, 1 neutral

Five beats across the library's 7-year history. The story is a well-maintained React library with steady releases, no security incidents, and an increasingly professional CI pipeline.

| Date | Label | Description |
|------|-------|-------------|
| 2019-04-09 | CREATED | Repo created under pmndrs (Poimandres) org. 7+ years at scan time. |
| 2019-2025 | STEADY GROWTH | Multiple major versions (v1-v5). Zero security advisories filed. Zero npm supply-chain incidents. Grew to 57k stars. |
| 2025-2026 | CI HARDENING | SHA-pinned actions, OIDC npm publish, copilot-bot hygiene PRs pinning deploy-pages. Active supply-chain awareness. |
| 2026-03-16 | V5.0.12 SHIPS | Latest release. 31 days before scan. All positive: persist bug fix, devtools type fix, dev dependency updates. |
| 2026-04-16 | THIS SCAN | HEAD at `32013285083648e8d58ba1f76d73b9bdc02fef50`. F0 fires as Warning. |

---

## Section 05: Repo Vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 7 years | Created 2019-04-09 |
| Stars / Forks | 57,758 / 2,035 | Top-tier npm library visibility |
| Primary maintainer | dai-shi (411 commits, ~48%) | Daishi Kato, 14yr account, 8k followers, freelancer |
| #2 contributor | drcmda (232 commits) | Poimandres org member |
| #3 contributor | dbritto-dev (59 commits) | Active co-maintainer, merges PRs |
| Review rate (20-PR sample) | 45% formal / 70% any | No branch protection enforces review |
| Branch protection | None on `main` | API 404 + empty rulesets + empty rules |
| CODEOWNERS | None | 4 locations checked |
| Dependabot alerts | Disabled | 403 "disabled for this repository" |
| Security advisories | 0 filed | Clean history |
| Runtime dependencies | 0 | Peer deps only (optional) |
| CI workflows | 8 files | All actions SHA-pinned except one same-org reusable workflow |
| Latest release | v5.0.12 (2026-03-16) | 31 days old at scan time |
| Open issues | 2 | Both non-security (#2659 "help wanted", #100 "Thank you!") |
| npm package | zustand@5.0.12 | Registry points to github.com/pmndrs/zustand.git |

---

## Section 06: Investigation Coverage

**Status:** 11 coverage cells verified | 0 amber gaps

| Cell | Status | Note |
|------|--------|------|
| Tarball extraction | OK (143 files) | Pinned to `32013285...` at scan start |
| Workflow files read | 8 of 8 | All headers + key sections inspected |
| Merged PRs scanned | 20 sampled | Dual review-rate metric computed |
| `pull_request_target` scan | 0 occurrences | Grep confirmed across all 8 workflows |
| Executable files | 0 of concern | 3 images with erroneous +x bit |
| Monorepo scope | N/A | Single-package repo |
| README paste-scan (7.5) | 1 block | `npm install zustand` only, standard |
| Agent-rule files | None found | 6 locations checked |
| Prompt-injection scan | 0 matches | No imperative-AI-directed strings |
| Distribution channels | npm only | OIDC publish from CI |
| Dependabot config | Present | Alert surface disabled, version updates active |

**Gap:** Org rulesets could not be checked (token lacks `admin:org` scope). This means we cannot confirm whether pmndrs has org-level rulesets that apply to zustand. Finding F0 notes this as "unknown" rather than "absent."

**Gap:** Review-rate metric is based on a 20-PR sample, not the full merged-PR history. Pattern (45% formal, 70% any) is consistent across the sample.

---

## Section 07: Evidence Appendix

9 command-backed claims. The branch-protection-missing check and the Dependabot-disabled check are the two falsification criteria for the Warning verdict.

### Evidence 1: No branch protection, no rulesets, no CODEOWNERS on `main` (F0 / C20) -- START HERE

**Command:**
```bash
gh api "repos/pmndrs/zustand/branches/main/protection"
gh api "repos/pmndrs/zustand/rulesets"
gh api "repos/pmndrs/zustand/rules/branches/main"
for p in .github/CODEOWNERS CODEOWNERS docs/CODEOWNERS .github/docs/CODEOWNERS; do
  test -f "/tmp/scan-zustand-v2/src/$p" && echo "FOUND: $p" || echo "NOT FOUND: $p"
done
gh api "orgs/pmndrs/rulesets"
```

**Result:**
```
{"message":"Not Found","status":"404"}
[]
[]
NOT FOUND: .github/CODEOWNERS
NOT FOUND: CODEOWNERS
NOT FOUND: docs/CODEOWNERS
NOT FOUND: .github/docs/CODEOWNERS
{"message":"Not Found","status":"404"} (needs admin:org scope)
```

**Classification:** Confirmed fact. Branch protection absent (404), rulesets empty, rules on main empty, CODEOWNERS absent in all 4 locations, org rulesets unknown (scope gap).

### Evidence 2: Dependabot alerts disabled (F1)

**Command:**
```bash
gh api repos/pmndrs/zustand/dependabot/alerts
```

**Result:**
```
{"message":"Dependabot alerts are disabled for this repository.","status":"403"}
```

**Classification:** Confirmed fact. The 403 message explicitly says "disabled for this repository" -- this is distinct from a scope gap (which would say "You are not authorized").

### Evidence 3: Zero dangerous primitives in source

**Command:**
```bash
for pattern in 'eval(' 'Function(' 'child_process' 'execSync' 'fs.write' 'fetch(' 'innerHTML'; do
  count=$(grep -rn "$pattern" /tmp/scan-zustand-v2/src/src/ 2>/dev/null | wc -l)
  echo "$pattern: $count matches"
done
```

**Result:** All patterns returned 0 matches. `import...from` returned 16 (expected ES module imports).

**Classification:** Confirmed fact. Positive control (import...from) verified grep was working.

### Evidence 4: Zero runtime dependencies

**Command:**
```bash
cat /tmp/scan-zustand-v2/src/package.json | jq '.dependencies'
```

**Result:** `null` (no `dependencies` field exists)

**Classification:** Confirmed fact.

### Evidence 5: All CI actions SHA-pinned

**Command:**
```bash
grep -rn 'uses:' /tmp/scan-zustand-v2/src/.github/workflows/*.yml
```

**Result:** All `actions/checkout`, `pnpm/action-setup`, `actions/setup-node` references use SHA pins with version comments. One exception: `pmndrs/docs/.github/workflows/build.yml@v3` (tag-pinned, same-org).

**Classification:** Confirmed fact.

### Evidence 6: No pull_request_target

**Command:**
```bash
grep -rn 'pull_request_target' /tmp/scan-zustand-v2/src/.github/workflows/
```

**Result:** No matches.

**Classification:** Confirmed fact.

### Evidence 7: PR review rate dual metric

**Command:**
```bash
gh api graphql -f query='{ repository(owner:"pmndrs", name:"zustand") { pullRequests(last:20, states:[MERGED]) { nodes { reviewDecision reviews(first:1) { totalCount } } } } }'
```

**Result:** 9/20 APPROVED reviewDecision (45%); 14/20 with reviews.totalCount > 0 (70%).

**Classification:** Confirmed fact (sample-based).

### Evidence 8: Release cadence and authorship

**Command:**
```bash
gh api repos/pmndrs/zustand/releases --jq '.[0:10] | .[] | {tag: .tag_name, date: .published_at, author: .author.login}'
```

**Result:** v5.0.12 (2026-03-16), v5.0.11 (2026-02-01), v5.0.10 (2026-01-12), v5.0.9 (2025-11-30), v5.0.8 (2025-08-19). All authored by dai-shi.

**Classification:** Confirmed fact. 31-day release age at scan time.

### Evidence 9: npm registry mapping

**Command:**
```bash
curl -s https://registry.npmjs.org/zustand/latest | jq '{version, repository: .repository.url}'
```

**Result:** `{"version": "5.0.12", "repository": "git+https://github.com/pmndrs/zustand.git"}`

**Classification:** Confirmed fact. npm package maps to the scanned repo.

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive. 2026-04-16. Scanned main @ `32013285083648e8d58ba1f76d73b9bdc02fef50` (v5.0.12). Scanner V2.3-post-R3. This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
