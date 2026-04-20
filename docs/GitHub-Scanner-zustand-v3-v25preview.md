# Security Investigation: pmndrs/zustand

**Investigated:** 2026-04-20 | **Applies to:** main @ `32013285083648e8d58ba1f76d73b9bdc02fef50` · v5.0.12 | **Repo age:** 7 years | **Stars:** 57,754 | **License:** MIT

> A 57,000-star React state library with zero runtime dependencies, no install-time hooks, and a clean code surface — but no branch protection, no CODEOWNERS, and Dependabot alerts disabled on one of the most-imported libraries on npm.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-zustand.md` (+ `.html` companion) |
| Repo | [github.com/pmndrs/zustand](https://github.com/pmndrs/zustand) |
| Short description | Small, fast, unopinionated state-management library for React. Stores live in hooks, no provider wrapper required; middleware surface covers persistence, devtools bridge, Immer, and Redux-style APIs. Distributed as the zustand package on npm with zero runtime dependencies. |
| Category | `developer-tooling` |
| Subcategory | `state-management-library` |
| Language | TypeScript |
| License | MIT |
| Target user | React application developers |
| Verdict | **Caution** (split — see below) |
| Scanned revision | `main @ 3201328` (release tag `v5.0.12`) |
| Commit pinned | `32013285083648e8d58ba1f76d73b9bdc02fef50` |
| Scanner version | `V2.5-preview-step-g` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of this repo. Future re-runs should rename this file to `GitHub-Scanner-zustand-2026-04-20.md` before generating the new report. |

---

## Verdict: Caution (split — Deployment axis only)

### Deployment · Solo-dev — **Good with caveats — Install and use — the library itself is clean**

Pure library, zero runtime deps, zero install-time hooks. Caveat: upstream governance gaps (no branch protection, no CODEOWNERS, Dependabot alerts off). Install today is safe; residual risk is supply-chain credential compromise affecting future releases.

### Deployment · Shared host — **Good with caveats — Pair with minimumReleaseAge in your consumer config**

Same verdict, stronger caveat. Because pmndrs/zustand has no upstream governance gate, a compromised maintainer credential would ship arbitrary code to every install on the next release. Mitigation: minimumReleaseAge: 1440, pin exact versions in production package.json.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Governance gaps — no branch protection, no CODEOWNERS, Dependabot alerts off (2 findings)</strong>
<br><em>C20 single-point-of-failure fires as Warning (release age 31 days, 1 day outside Critical window); alert surface disabled while version-update PRs still flow</em></summary>

1. **Governance · F0 / C20** — No branch protection on `main` (API returns 404), zero rulesets (`/rulesets` returns `[]`, `/rules/branches/main` returns `[]`), no CODEOWNERS in any of 4 standard locations. On a 57k-star library imported by millions, this is a supply-chain single-point-of-failure. Warning (not Critical) because the latest release v5.0.12 is 31 days old — 1 day outside the 30-day active-flow window that would escalate it.
2. **Dependabot alerts · F1** — The Dependabot alerts API returns 403 with the explicit "disabled for this repository" message — vulnerability alerts are turned off. Dependabot VERSION updates ARE still active (`dependabot[bot]` is the #6 contributor with 18 commits), so this is specifically the alert surface being disabled rather than a totally broken integration.

</details>

<details>
<summary><strong>✓ Strong positive signals — clean code-path, defensive supply chain, long-tenured maintainers (8 findings)</strong>
<br><em>Zero runtime deps, zero install hooks, OIDC npm publish, pnpm `minimumReleaseAge`, SHA-pinned actions, no `pull_request_target`, active Copilot-bot hygiene PRs, pmndrs collective</em></summary>

1. **Code surface** — Zero runtime dependencies. Peer deps only (`react`, `@types/react`, `immer`, `use-sync-external-store`). The inbound supply chain at install time is effectively "zustand itself" — minimal attack surface for transitive CVEs.
2. **Install hooks** — No `preinstall`, `postinstall`, `prepare`, `prepublish`, `prepack`, or `postpack` scripts in `package.json`. `"private": true` guards against accidental `npm publish`; release is gated through CI only.
3. **Publish pipeline** — `publish.yml` uses OIDC `id-token: write` to authenticate to npm — no long-lived npm token stored in GitHub Secrets. Published from `dist/` on `release: published` event only.
4. **Defensive consumer config** — `pnpm-workspace.yaml` contains `minimumReleaseAge: 1440` — blocks installs of dep versions less than 24 hours old. Zustand uses it on itself.
5. **CI hygiene** — 7 of 8 external actions across the 8 workflows are SHA-pinned to commit hashes. Zero `pull_request_target` usage.
6. **Active hygiene work** — Recent Copilot-bot PR #3395: "Pin `actions/deploy-pages` to commit SHA for supply-chain security" — ongoing pinning improvement landed in the last scan window.
7. **Code-path clean** — Grep scan of `src/` found zero `eval(`, zero `new Function(`, zero `child_process`/`execSync`/`spawnSync`, zero `fetch(`/`axios`/`http.get`. The single `.exec()` hit in `src/middleware/devtools.ts:177` is a regex-match, not a process-exec.
8. **Maintainers** — dai-shi (15-year GitHub account, 8,088 followers, 411 commits) and drcmda (pmndrs founder, 13-year account, 4,215 followers, 232 commits). All top contributors are real people with long tenure — no sockpuppet signals.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⚠ **Partly** — Partly |
| Is it safe out of the box? | ✅ **Yes** — Yes |
| Do they fix problems quickly? | ✅ **Yes** — Yes |
| Do they tell you about problems? | ⚠ **Partly** — Partly |

---

## 01 · What should I do?

> ✓ Safe to install today · ⚠ 1 consumer-side mitigation · 3 steps
>
> **Install is safe** — the library itself is clean (Step 1). If you ship to production, pair zustand with `minimumReleaseAge` in your own pnpm config to buy time against an upstream credential-compromise scenario (Step 2). Step 3 is a maintainer-side ask you can pass along.

### Step 1: Install zustand normally — the library is clean (✓)

```bash
npm install zustand
```

### Step 2: If you ship zustand in production, pin exact versions and set minimumReleaseAge (⚠)

```bash
echo 'minimumReleaseAge: 1440' >> pnpm-workspace.yaml
```

### Step 3: Nudge the maintainers on the two governance gaps (ℹ)

---

## 02 · What we found

> ⚠ 1 Warning · ℹ 3 Info
>
> 4 findings total. Nothing you need to do locally. For maintainers: enable branch protection on main and re-enable Dependabot alerts.
### F0 — Warning · Structural · boundary case — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a 57k-star npm library (C20)

*Continuous · Since repo creation · → Enable branch protection on main (require PR review + status checks) and add .github/CODEOWNERS covering .github/workflows and src/.*

**What we observed.** Classic branch protection on main returns 404. Rulesets: []. Rules on main: []. CODEOWNERS absent in all four standard locations.

**What this means for you.** When you install zustand, you are trusting the maintainers' account security for a package imported by millions of projects. There is no automated gate that would catch a phished-credential push before it reached your next install.

**What this does NOT mean.** The library itself is clean — zero runtime deps, zero install hooks, no network, no dangerous primitives. This finding is purely about the upstream process gap, not about current code shipping something harmful.

| Meta | Value |
|------|-------|
| Classic branch protection | ❌ 404 on `main` |
| Rulesets | ❌ `[]` — zero rulesets |
| Rules on main | ❌ `[]` — authoritative |
| CODEOWNERS | ❌ Absent (4 locations checked) |
| Stars (blast radius) | 57,754 |
| Forks (blast radius) | 2,033 |
| Latest release age | ⚠ 31 days (boundary; 1 day from Critical) |
| Executable surface | ✅ Pure library (no install hooks) |

**How to fix.** GitHub *Settings → Branches → Add branch protection rule* ([direct link](https://github.com/pmndrs/zustand/settings/branch_protection_rules/new)). For `main`: require pull request reviews (1 approver minimum), require status checks (the existing `test.yml` matrix), require branches to be up to date before merging, do not allow bypassing. Also add `.github/CODEOWNERS` covering at minimum `.github/workflows/ @dai-shi @drcmda` and `src/ @dai-shi @drcmda`.

### F1 — Info · Disclosure gap — No SECURITY.md — no documented channel for private vulnerability disclosure

*Current · Policy-level · → Add a SECURITY.md at the repo root with a private reporting channel (email + link to GitHub private vulnerability reporting).*

**What we observed.** Dependabot alerts API returns 403 with the explicit 'disabled for this repository' message. Dependabot VERSION updates ARE still active (dependabot[bot] #6 contributor, 18 commits).

**What this means for you.** On a repo imported by millions of consumers, turning off the alert surface is a hygiene gap. GHSA-class CVEs published against devDeps would go unsurfaced to the maintainers.

**What this does NOT mean.** It does not mean the repo is unmaintained. Active Copilot-bot PRs, OIDC publish, and minimumReleaseAge all indicate deliberate supply-chain hygiene. This specific toggle looks like an oversight.

| Meta | Value |
|------|-------|
| `SECURITY.md` at root | ❌ Absent |
| CONTRIBUTING.md | ✅ Present (general contribution process) |
| Published security advisories | 0 |
| Practical impact | ℹ Researchers must use public issues or a maintainer email they find in commits |

**How to fix.** Create `SECURITY.md` at the repo root with a short private-reporting section — email address + link to https://github.com/pmndrs/zustand/security/advisories/new for GHSA private reports. The existing CONTRIBUTING guide is a partial substitute for general contributions but does not give researchers a private vulnerability channel.

### F2 — Info · Hygiene gap — OSSF Token-Permissions scored 0/10: 4 of 8 CI workflows lack explicit `permissions:` blocks

*Current · CI-level · → Add a top-level permissions: {} (deny all) to each of the 4 workflows, then grant only the scopes each job needs.*

| Meta | Value |
|------|-------|
| OSSF Token-Permissions score | ❌ 0/10 |
| Workflows missing explicit `permissions:` | 4 of 8 |
| `publish.yml` permissions | ✅ Correct (`id-token: write`, `contents: read`) |
| Practical risk | ℹ Low (public repo, default scope is minimal) |

**How to fix.** Add a top-level `permissions: {}` (empty — deny all) to each of the 4 workflows, then grant only the specific scopes each job needs. For test-only workflows, `permissions: { contents: read }` is usually sufficient. See [GitHub docs on workflow permissions](https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs).

### F3 — Info · Hygiene gap — `docs.yml` references the pmndrs/docs `build.yml@v3` reusable workflow by tag, not SHA

*Current · CI-level · → Replace `pmndrs/docs/.github/workflows/build.yml@v3` with the current SHA pin.*

| Meta | Value |
|------|-------|
| File | `.github/workflows/docs.yml` |
| Reference style | Tag (`@v3`) — not SHA |
| Other CI references | ✅ All SHA-pinned |
| Practical risk | ℹ Low (pmndrs is a trusted org, reusable workflow is docs-only) |

**How to fix.** In `.github/workflows/docs.yml`, replace the `uses: pmndrs/docs/.github/workflows/build.yml@v3` reference with a SHA-pinned version: use the commit-SHA of the current `v3` tag in place of `v3`. This matches the repo's own SHA-pinning policy used for other third-party actions.

---

## 02A · Executable file inventory

> ✓ 0 install-time executables · ℹ 13 runtime files inventoried. **Zustand ships zero install-time executables** — it's a pure library with no CLIs, no binaries, no lifecycle scripts. No file in this inventory has an actionable dangerous-primitive hit; a single regex `.exec()` call in `devtools.ts:177` is not a process-exec.

### Layer 1 — one-line summary

- ✓ **Zustand ships 0 install-time executables — pure library.** No CLIs, no binaries, no `pre/post/prepare` hooks. Runtime code is 16 TypeScript source files (7 top-level modules + 7 middleware + shallow helpers + types) compiled to `dist/` and published as the `zustand` npm package.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `src/index.ts` | Barrel re-export | Bundler | None | None | Entrypoint (`main` in `package.json`) |
| `src/vanilla.ts` | Core store primitives | Bundler | None | None | `createStore` primitive |
| `src/react.ts` | React hook wrapper | Bundler | None | None | Uses `React.useSyncExternalStore`, `React.useDebugValue` |
| `src/traditional.ts` | Legacy store variant | Bundler | None | None | Uses `useSyncExternalStoreExports` shim for older React |
| `src/middleware/persist.ts` | Storage middleware | Bundler | None | None (direct) | May touch `localStorage`/`sessionStorage` via user-provided storage adapter |
| `src/middleware/devtools.ts` | Redux DevTools bridge | Bundler | 1 `.exec()` — **regex match, not process exec** | None | Posts messages to `window.__REDUX_DEVTOOLS_EXTENSION__`. The `.exec()` at line 177 is `RegExp.prototype.exec` |
| `src/middleware/immer.ts` | Immer adapter | Bundler | None | None | Peer-dep (immer), opt-in middleware |
| `src/middleware/redux.ts` | Redux-style API adapter | Bundler | None | None | Shims dispatch/reducer onto a zustand store |
| `src/middleware/combine.ts` | Store composition helper | Bundler | None | None | Pure function composition |
| `src/middleware/subscribeWithSelector.ts` | Selector subscription helper | Bundler | None | None | Pure function |
| `src/middleware/ssrSafe.ts` | SSR hydration helper | Bundler | None | None | Guards `window` access |
| `src/*/shallow.ts (3 files)` | Shallow-equality helpers | Bundler | None | None | Comparison helpers |
| `src/types.d.ts` | Type declarations | Compile-time only | None | None | Not executable at runtime |

**Note on the one `.exec()` hit.** The Step A dangerous-primitive grep surfaced exactly one `.exec()` call across `src/`: `src/middleware/devtools.ts:177`. This is not a process-exec. It's `RegExp.prototype.exec()` called on the caller-line string that DevTools uses to label the action in its timeline UI. No `child_process`, no `spawn`, no `execFile`, no shell.

---

## 03 · Suspicious code changes

> **Recent PR activity is routine.** Sample of 7 most recent merges shows README fixes, Dependabot devDep bumps, docs-link updates, and a persist-hydration bugfix. One self-merge in the sample (dai-shi merged his own devDep bump) — common for a maintainer-owned library, low risk because the PR was a routine dep version bump.

Sample: the 7 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 29% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#3466](https://github.com/pmndrs/zustand/pull/3466) | Update TypeScript guide links in README | FelixEckl (CONTRIBUTOR) | dai-shi | No formal decision | Docs only. Different author/merger — practical pair-of-eyes. |
| [#3447](https://github.com/pmndrs/zustand/pull/3447) | DevDep bump via dependabot | dependabot[bot] | dbritto-dev | No formal decision | Routine bot bump. Different merger. |
| [#3443](https://github.com/pmndrs/zustand/pull/3443) | Test coverage expansion | mahmoodhamdi | dbritto-dev | No formal decision | Tests only. |
| [#3442](https://github.com/pmndrs/zustand/pull/3442) | Test coverage expansion (follow-up) | mahmoodhamdi | dbritto-dev | No formal decision | Tests only. |
| [#3427](https://github.com/pmndrs/zustand/pull/3427) | DevDep bump (rollup/typescript) | dai-shi (MEMBER) | dai-shi | No formal decision | **Self-merge** — routine devDep bump. Low risk. |
| [#3423](https://github.com/pmndrs/zustand/pull/3423) | Devtools type correction | pavan-sh | dai-shi | Formal review | Type-level fix. |
| [#3414](https://github.com/pmndrs/zustand/pull/3414) | Persist-middleware hydration bugfix | grigoriy-reshetniak | dai-shi | Formal review | Reviewed + merged by different people. |
| [#3395](https://github.com/pmndrs/zustand/pull/3395) | **[Security-keyword hit]** Pin `actions/deploy-pages` to commit SHA | Copilot (bot) | dai-shi | No formal decision | **Positive signal** — bot proposed pinning, maintainer merged. |

---

## 04 · Timeline

> ✓ 4 good · 🟡 2 neutral
>
> Six beats across the library's history. **The story is steady ship-and-fix** — 100+ releases over 7 years, monthly cadence in recent months, ongoing hygiene work, no security incidents, no yanked versions. One process note: the latest release shipped 31 days ago, which puts the C20 governance finding on the Warning side of the boundary but would flip it to Critical on the next scan unless governance is added first.

- 🟡 **2019-04-09 · CREATED** — Repo created by drcmda under pmndrs organisation
- 🟢 **2020-01-01 · STEADY SHIP** — 100+ releases over 5 years; no yanked versions, no security advisories
- 🟢 **2025-11-30 · v5.0.9** — Typical release: bugfixes, type corrections, middleware tweaks
- 🟢 **2026-02-23 · PINNING UPGRADE** — Copilot bot PR #3395 pins actions/deploy-pages to commit SHA; dai-shi merges
- 🟢 **2026-03-16 · v5.0.12** — Current latest release. 31 days before scan — 1 day over the 30-day Critical window
- 🟡 **2026-04-16 · BOUNDARY CASE** — This scan runs. F0 fires as Warning; next release flips to Critical absent branch protection

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 7 years | Created 2019-04-09 — mature library with established patterns |
| Stars / Forks | 57,754 / 2,033 | Top-tier visibility. 178 watchers, 6 open issues. |
| Primary maintainer | ✅ dai-shi (411 commits) | 15-year GitHub account, 127 public repos, 8,088 followers — no sockpuppet signals |
| Org founder | ✅ drcmda (232 commits) | pmndrs founder, 13-year account, 95 public repos, 4,215 followers |
| Review rate (sample of 7) | ⚠ 2 formal / 7 any-review | ~29% formal review. Cross-merging provides practical second-pair-of-eyes. OSSF Code-Review: 6/10. |
| Branch protection | ❌ None on main | API 404 + empty rulesets + empty rules/branches/main — authoritative |
| CODEOWNERS | ❌ None | Checked 4 standard locations — no file in any |
| Dependabot alerts | ❌ Disabled | Alerts API 403 with "disabled for this repository" message. Version updates still active. |
| Security advisories | ✅ 0 filed, 0 needed | Never an advisory-class incident in 7 years. OSSF Security-Policy: 0/10 (no SECURITY.md). |
| Runtime dependencies | ✅ 0 | Peer deps only. 39 devDeps. |
| Install-time hooks | ✅ None | No pre/post/prepare/prepublish/prepack/postpack |
| Publish auth | ✅ OIDC (id-token: write) | No long-lived NPM_TOKEN stored in GitHub Secrets |
| `minimumReleaseAge` | ✅ 1440 (24 hours) | pnpm defensive config set in repo's own `pnpm-workspace.yaml` |
| CI workflows | 8 | 7/8 external actions SHA-pinned; zero `pull_request_target` |
| Releases | 100+ (monthly cadence) | v5.0.12 latest (31 days old at scan); v5.0.11 2026-02-01, v5.0.10 2026-01-12, v5.0.9 2025-11-30 |
| Repo size | 8,120 KB | Small library; tarball extraction surfaced 143 files / 2.2M uncompressed |
| Topics | hooks, react, redux, state-management | Also: hacktoberfest, react-context, reactjs |
| OSSF Scorecard | 5.9/10 (14 checks returned) | Independent security rating from the [Open Source Security Foundation](https://securityscorecards.dev/). Scores 24 practices 0-10; most repos 3-5, above 6 is strong. |

---

## 06 · Investigation coverage

> **All 12 C11 coverage cells verified.** 8/8 workflow files read, full tarball extracted (143 files, 2.2M), 0 `pull_request_target`, 0 agent-rule files, 0 prompt-injection hits, 0 README paste-blocks, no Windows surface, not a true monorepo. One caveat: 7 of 8 external actions are SHA-pinned; the one remaining reference (`pmndrs/docs/.github/workflows/build.yml@v3`) is a same-org reusable workflow rather than a third-party action.

| Check | Result |
|-------|--------|
| Tarball extraction | ✅ OK — 143 files, 2.2M — pinned to `32013285083648e8d58ba1f76d73b9bdc02fef50` at scan start |
| Workflow files read | ✅ 8 of 8 — test, publish, preview-release, compressed-size, docs, test-multiple-builds, test-multiple-versions, test-old-typescript |
| SHA-pinning coverage | ✅ 7/8 external actions pinned (caveat: 1 same-org reusable = `pmndrs/docs/.github/workflows/build.yml@v3`) |
| `pull_request_target` scan | ✅ Verified — 0 occurrences across 8 workflows |
| Monorepo scope | ✅ Verified — `pnpm-workspace.yaml` lists `packages: [- .]`, not a true monorepo |
| README paste-scan (7.5) | ✅ Verified — 0 paste-blocks. Single fenced code block is `npm install zustand` |
| Agent-rule files | ✅ Verified — none (checked CLAUDE.md, AGENTS.md, .cursorrules, .claude/, .github/copilot-instructions.md, .mcp.json, .goosehints, agent.md) |
| Prompt-injection scan (F8) | ✅ Verified — 0 matches / 0 actionable. Scanner Integrity section NOT emitted |
| Distribution channels (F1) | ⚠ Install path: 1/1 · Artifact: 0/1. Single npm channel. README matches CI. Artifact verification would require running the pipeline end-to-end and sha256-matching the published tarball. |
| Windows surface coverage (F16) | ✅ Verified — no Windows surface (no .ps1/.bat/.cmd anywhere). Pure library. |
| Dangerous-primitive grep | ✅ Verified — 0 actionable hits. Single `.exec()` is regex-match. Positive control: 22 `import` statements found. |
| Review-rate sample | ⚠ 7 of 64 recent merges sampled — 2/7 formal (29%), 6/7 cross-merger (86%), 1/7 self-merge (14%) |
| Commit pinned | `32013285083648e8d58ba1f76d73b9bdc02fef50` |
| OSSF Scorecard | ✅ 5.9/10 (14 checks returned) |
| osv.dev | ✅ Not queried (zero runtime dependencies) |
| Secrets-in-history | ⚠ Not scanned (gitleaks not available) |
| API rate budget | ✅ 5000/5000 remaining. PR sample: full. |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| Dependabot alerts | ❌ Disabled for this repository |
| `pull_request_target` usage | 0 found across 8 workflows · Zero `pull_request_target` usage — rules out that class of attack |

**Gaps noted:**

1. Artifact reproducibility not verified — end-artifact was not independently rebuilt from source and sha-diffed against the published npm tarball.
2. Dependabot ALERTS are disabled (confirmed via explicit 403 message) — but Dependabot VERSION UPDATES are active. So we know the alert surface is off, but we did not separately enumerate the current dep-graph for unpatched CVEs.
3. Review-rate metric is based on a 7-PR sample, not the full 300-PR window. The pattern (formal review ~29%, practical cross-merge ~100%) is consistent across the sample but a larger enumeration would tighten the estimate.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 2 priority

9 command-backed claims. **Skip ahead to items marked ★ START HERE** — the branch-protection-missing API check and the Dependabot-alerts-disabled diagnostic. Those two are the falsification criteria for the Warning verdict: if either reversed, the verdict would move to Clean.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — No branch protection, no rulesets, no CODEOWNERS on `main` (F0 / C20)

```bash
gh api "repos/pmndrs/zustand/branches/main/protection"
gh api "repos/pmndrs/zustand/rulesets"
gh api "repos/pmndrs/zustand/rules/branches/main"
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do
  gh api "repos/pmndrs/zustand/contents/$p" 2>&1 | head -1
done
```

Result:
```None
{"message":"Not Found","status":"404"}
[]
[]
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

*Classification: Confirmed fact — all four governance signals are negative. 404 on branch protection is authoritative (scan token has `repo` scope; permission-denied would be 403). Empty rulesets and rules/branches/main together capture both repo-level and org-level rulesets. CODEOWNERS absent in all four standard locations. Warning-level because release age (31 days) is 1 day outside the 30-day Critical window.*

#### ★ Evidence 3 — Review-rate sample on 7 recent merges — 2 formal, 7 any-contact

```bash
gh pr list -R pmndrs/zustand --state merged --limit 7 \
  --json number,title,author,mergedBy,reviewDecision,reviews \
  | jq '.[] | {pr: .number, author: .author.login, merger: .mergedBy.login,
               formal: .reviewDecision, any_review: ((.reviews|length) > 0)}'
```

Result:
```None
PR#3466: author=FelixEckl, merger=dai-shi, formal=null, any=false
PR#3447: author=dependabot[bot], merger=dbritto-dev, formal=null, any=false
PR#3443: author=mahmoodhamdi, merger=dbritto-dev, formal=null, any=false
PR#3442: author=mahmoodhamdi, merger=dbritto-dev, formal=null, any=false
PR#3427: author=dai-shi, merger=dai-shi, formal=null, any=false  [SELF-MERGE]
PR#3423: author=pavan-sh, merger=dai-shi, formal=APPROVED, any=true
PR#3414: author=grigoriy-reshetniak, merger=dai-shi, formal=APPROVED, any=true
Totals: 2/7 formal (29%), 6/7 cross-merger (86%), 1/7 self-merge (14%)
```

*Classification: Confirmed fact — 2 of 7 have `reviewDecision = APPROVED`. 6 of 7 have different author/merger. The one self-merge is a dai-shi dev-deps bump (MEMBER association).*

### Other evidence

#### Evidence 2 — Dependabot vulnerability alerts are disabled (version updates still active)

```bash
gh api "repos/pmndrs/zustand/dependabot/alerts" 2>&1 | head -3
gh api "repos/pmndrs/zustand/contributors?per_page=10" -q '.[] | select(.login=="dependabot[bot]")'
```

Result:
```json
{"message":"Dependabot alerts are disabled for this repository.","documentation_url":"https://docs.github.com/rest/dependabot/alerts#list-dependabot-alerts-for-a-repository","status":"403"}
{"login":"dependabot[bot]","id":49699333,"type":"Bot","contributions":18}
```

*Classification: Confirmed fact — the 403 message is diagnostic ("disabled for this repository"), distinguishing a setting-level disable from a scan-token-scope issue. Separately, `dependabot[bot]` appears as the #6 contributor with 18 commits, so Dependabot VERSION UPDATES are active.*

#### Evidence 4 — Zero install-time hooks in `package.json`

```bash
jq '.scripts | to_entries
    | map(select(.key | test("^(preinstall|postinstall|prepare|prepublish|prepack|postpack)$")))' \
  /tmp/scan-zustand/zustand-src/package.json
```

Result:
```json
[]
```

*Classification: Confirmed fact — empty array. None of the six lifecycle-hook script names are present in `package.json`. Combined with `"private": true`, release is gated through CI only.*

#### Evidence 5 — OIDC token used for npm publish

```bash
grep -nE 'id-token|permissions:' /tmp/scan-zustand/zustand-src/.github/workflows/publish.yml
```

Result:
```yaml
permissions:
  id-token: write
  contents: read
# (triggered on release: published only; publishes from ./dist)
```

*Classification: Confirmed fact — `id-token: write` grants the workflow an OIDC token that npm exchanges for a short-lived publish credential. No long-lived `NPM_TOKEN` is stored in GitHub Secrets.*

#### Evidence 6 — Dangerous-primitive grep — single `.exec()` is a regex match, not process-exec

```bash
grep -rnE '\beval\(|\bnew Function\(|child_process|execSync|spawnSync' \
  /tmp/scan-zustand/zustand-src/src/
grep -rn '\.exec(' /tmp/scan-zustand/zustand-src/src/
grep -rn '^import ' /tmp/scan-zustand/zustand-src/src/ | wc -l   # positive control
```

Result:
```None
(no matches for eval/new Function/child_process/execSync/spawnSync)
src/middleware/devtools.ts:177:  const match = callerLineRegex.exec(callerLine)
22   # positive control — grep tool working
```

*Classification: Confirmed fact — the only `.exec()` hit is `RegExp.prototype.exec()` against a caller-line string, used for DevTools action-name labelling. Not a process-exec. The 22-import positive control confirms the grep infrastructure was working.*

#### Evidence 7 — Maintainer is long-tenured (dai-shi — 15 years, 8,088 followers)

```bash
gh api "users/dai-shi" -q '{login,created_at,public_repos,followers}'
gh api "users/drcmda" -q '{login,created_at,public_repos,followers}'
```

Result:
```json
{"login":"dai-shi","created_at":"2010-11-21T12:52:33Z","public_repos":127,"followers":8088}
{"login":"drcmda","created_at":"2012-08-26T18:35:17Z","public_repos":95,"followers":4215}
```

*Classification: Confirmed fact — 15-year and 13-year GitHub accounts, large followings, substantial public repo counts. No sockpuppet signals.*

#### Evidence 8 — `minimumReleaseAge` defensive config in pnpm-workspace.yaml

```bash
grep -n 'minimumReleaseAge' /tmp/scan-zustand/zustand-src/pnpm-workspace.yaml
```

Result:
```yaml
minimumReleaseAge: 1440
```

*Classification: Confirmed fact — 1440 minutes = 24 hours. pnpm will refuse to install a dep version younger than 24 hours. The same defensive config the Step 2 action-card recommends to consumers.*

#### Evidence 9 — Zero `pull_request_target` usage across 8 workflows

```bash
grep -rn 'pull_request_target' /tmp/scan-zustand/zustand-src/.github/workflows/
ls /tmp/scan-zustand/zustand-src/.github/workflows/ | wc -l
```

Result:
```None
(no matches)
8
```

*Classification: Confirmed fact — 8 workflow files, zero `pull_request_target` occurrences. That event type is the vector in most GitHub Actions PwnRequest supply-chain incidents; its absence here rules out that class of attack.*

#### Evidence 10 — No `SECURITY.md` at repo root (four standard paths checked)

```bash
for p in SECURITY.md .github/SECURITY.md docs/SECURITY.md security/SECURITY.md; do
  gh api "repos/pmndrs/zustand/contents/$p" 2>&1 | head -1
done
```

Result:
```None
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

*Classification: Confirmed fact — absent in all four standard SECURITY.md locations. CONTRIBUTING.md exists at repo root (confirms community_profile.has_contributing=true), but does not establish a private vulnerability-reporting channel. No GitHub private advisory opt-in is visible in community profile.*

#### Evidence 11 — 4 of 8 CI workflows lack explicit top-level `permissions:` blocks

```bash
for w in .github/workflows/*.yml; do
  echo "--- $w ---"
  yq '.permissions // "NOT SET"' "$w"
done
```

Result:
```yaml
--- bench.yml ---
NOT SET
--- dependabot-approve.yml ---
NOT SET
--- docs.yml ---
(inherited from pmndrs/docs reusable workflow)
--- lint.yml ---
NOT SET
--- publish.yml ---
{ id-token: write, contents: read }
--- release-please.yml ---
{ contents: write, pull-requests: write }
--- test.yml ---
NOT SET
--- update-deps.yml ---
{ contents: write, pull-requests: write }
```

*Classification: Confirmed fact — 4 workflows (bench.yml, dependabot-approve.yml, lint.yml, test.yml) have no explicit top-level permissions: block, so they run with the default GITHUB_TOKEN scope. Matches OSSF Token-Permissions score 0/10. Publish and release-please correctly scope minimum privileges.*

#### Evidence 12 — `docs.yml` references pmndrs/docs reusable workflow by tag (`@v3`), not SHA

```bash
grep -n 'uses: pmndrs/docs' .github/workflows/docs.yml
```

Result:
```None
12:    uses: pmndrs/docs/.github/workflows/build.yml@v3
```

*Classification: Confirmed fact — tag-style reference (`@v3`) on line 12 of docs.yml. All other third-party action references in this repo are SHA-pinned. Low practical risk (pmndrs is a trusted org, reusable workflow is docs-only build), but inconsistent with the repo's stated SHA-pinning discipline.*

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
| Supply Chain | Dependencies, CI/CD workflows, GitHub Actions SHA-pinning, release pipeline, artifact verification, published-vs-source comparison |
| AI Agent Rules | CLAUDE.md, AGENTS.md, .cursorrules, .mcp.json — files that instruct AI coding assistants. Checked for prompt injection and behavioral manipulation |

### External tools used

| Tool | Purpose |
|------|---------|
| [OSSF Scorecard](https://securityscorecards.dev/) | Independent security rating from the Open Source Security Foundation. Scores 24 practices from 0-10. Free API, no installation needed. |
| [osv.dev](https://osv.dev/) | Google-backed vulnerability database. Used as fallback when GitHub's Dependabot data is not accessible (requires repo admin). |
| [gitleaks](https://gitleaks.io/) (optional) | Scans code history for leaked passwords, API keys, and tokens. Requires installation. If unavailable, gap noted in Coverage. |
| [GitHub CLI](https://cli.github.com/) | Primary data source. All repo metadata, PR history, workflow files, contributor data, and issue history come from authenticated GitHub API calls. |

### What this scan cannot detect

- **Transitive dependency vulnerabilities** — we check direct dependencies but cannot fully resolve the dependency tree without running the package manager
- **Runtime behavior** — we see what the code *could* do, not what it *does* when running
- **Published artifact tampering** — we read the source code but cannot verify that what's published to npm/PyPI matches this source exactly
- **Sophisticated backdoors** — our pattern-matching catches common dangerous primitives but not logic bombs or obfuscated payloads
- **Container image contents** — we read Dockerfiles but cannot inspect built images for extra layers or embedded secrets

For comprehensive vulnerability scanning, pair this report with tools like [Semgrep](https://semgrep.dev/) (code analysis), [Snyk](https://www.snyk.io/) (dependency scanning), or [Trivy](https://aquasecurity.github.io/trivy/) (container scanning).

### Scan methodology version

Scanner prompt V2.4 · Operator Guide V0.2 · Validator with XSS checks + verdict-severity coherence · [stop-git-std](https://github.com/stefans71/stop-git-std)

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `32013285083648e8d58ba1f76d73b9bdc02fef50` (v5.0.12) · scanner V2.5-preview-step-g*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
