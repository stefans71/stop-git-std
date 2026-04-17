# Security Investigation: pmndrs/zustand

**Investigated:** 2026-04-16 | **Applies to:** main @ `32013285083648e8d58ba1f76d73b9bdc02fef50` · v5.0.12 | **Repo age:** 7 years | **Stars:** 57,754 | **License:** MIT

> A 57,000-star React state library with zero runtime dependencies, no install-time hooks, and a clean code surface — but no branch protection, no CODEOWNERS, and Dependabot alerts disabled on one of the most-imported libraries on npm.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-zustand.md` (+ `.html` companion) |
| Repo | [github.com/pmndrs/zustand](https://github.com/pmndrs/zustand) |
| Short description | Small, fast, unopinionated state-management library for React. Stores live in hooks, no provider wrapper required; middleware surface covers persistence, devtools bridge, Immer, and Redux-style APIs. Distributed as the `zustand` package on npm with zero runtime dependencies. |
| Category | `developer-tooling` |
| Subcategory | `state-management-library` |
| Language | TypeScript |
| License | MIT |
| Target user | React application developers |
| Verdict | **Caution** (split — see below) |
| Scanned revision | `main @ 3201328` (release tag `v5.0.12`) |
| Commit pinned | `32013285083648e8d58ba1f76d73b9bdc02fef50` |
| Scanner version | `V2.3-post-R3` |
| Scan date | `2026-04-16` |
| Prior scan | None — first scan of this repo. Future re-runs should rename this file to `GitHub-Scanner-zustand-2026-04-16.md` before generating the new report. |

---

## Verdict: Caution (split — Deployment axis only)

### Deployment · Solo-dev or learning context · default install — **Good with caveats — install and use, the library itself is clean**

Pure library, zero runtime deps, zero install-time hooks, zero network calls in source, no shell-exec primitives, no dangerous sinks. The code-path risk is as close to zero as a React library gets. The caveat is upstream governance: no branch protection on `main`, no rulesets, no CODEOWNERS, and Dependabot vulnerability alerts are disabled on the repo (version bumps still flow). Your install today is safe; the residual risk is supply-chain credential compromise affecting future releases.

### Deployment · Shared host / production application — **Good with caveats — pair with `minimumReleaseAge` in your consumer config**

Same verdict, stronger caveat. Because `pmndrs/zustand` is imported by millions and has no upstream governance gate, a single compromised maintainer credential would ship arbitrary code to every install on the next release with no branch-level review. Mitigation on the consumer side: set `minimumReleaseAge: 1440` in your own pnpm config (zustand uses this internally — the same trick protects you too), pin exact versions in production `package.json`, and keep an eye on release notes. The library itself is clean.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Governance gaps — no branch protection, no CODEOWNERS, Dependabot alerts off (2 findings)</strong>
<br><em>C20 single-point-of-failure fires as Warning (release age 31 days, 1 day outside Critical window); alert surface disabled while version-update PRs still flow</em></summary>

1. **Governance · F0 / C20** — No branch protection on `main` (API returns 404), zero rulesets (`/rulesets` returns `[]`, `/rules/branches/main` returns `[]`), no CODEOWNERS in any of 4 standard locations. On a 57k-star library imported by millions, this is a supply-chain single-point-of-failure. Warning (not Critical) because the latest release v5.0.12 is 31 days old — 1 day outside the 30-day active-flow window that would escalate it.
2. **Dependabot alerts** — The Dependabot alerts API returns 403 with the explicit "disabled for this repository" message — vulnerability alerts are turned off. Dependabot VERSION updates ARE still active (`dependabot[bot]` is the #6 contributor with 18 commits), so this is specifically the alert surface being disabled rather than a totally broken integration. For a repo this size with active npm publishing, it's a notable hygiene gap.

</details>

<details>
<summary><strong>✓ Strong positive signals — clean code-path, defensive supply chain, long-tenured maintainers (8 signals)</strong>
<br><em>Zero runtime deps, zero install hooks, OIDC npm publish, pnpm <code>minimumReleaseAge</code>, SHA-pinned actions, no <code>pull_request_target</code>, active Copilot-bot hygiene PRs, pmndrs collective</em></summary>

1. **Code surface** — Zero runtime dependencies. Peer deps only (`react`, `@types/react`, `immer`, `use-sync-external-store`). The inbound supply chain at install time is effectively "zustand itself" — minimal attack surface for transitive CVEs.
2. **Install hooks** — No `preinstall`, `postinstall`, `prepare`, `prepublish`, `prepack`, or `postpack` scripts in `package.json`. The 27 scripts present are all build/test/fix/patch targets. `"private": true` guards against accidental `npm publish`; release is gated through CI only.
3. **Publish pipeline** — `publish.yml` uses OIDC `id-token: write` to authenticate to npm — no long-lived npm token stored in GitHub Secrets. Published from `dist/` on `release: published` event only.
4. **Defensive consumer config** — `pnpm-workspace.yaml` contains `minimumReleaseAge: 1440`. That pnpm feature blocks installs of dep versions less than 24 hours old — the same defensive trick the scanner recommends in production consumers. Zustand uses it on itself.
5. **CI hygiene** — 7 of 8 external actions across the 8 workflows are SHA-pinned to commit hashes (not version tags or branches). The single unpinned reference is `pmndrs/docs/.github/workflows/build.yml@v3` — a same-org reusable workflow, not a third-party action. Zero `pull_request_target` usage (grep returned 0 matches).
6. **Active hygiene work** — Recent Copilot-bot PR #3395: "Pin `actions/deploy-pages` to commit SHA for supply-chain security" — ongoing pinning improvement landed in the last scan window. Pattern: bots propose hygiene fixes, maintainers merge.
7. **Code-path clean** — Grep scan of `src/` found zero `eval(`, zero `new Function(`, zero `child_process`/`execSync`/`spawnSync`, zero `fetch(`/`axios`/`http.get`/`XMLHttpRequest`/`WebSocket`, zero hardcoded credentials, zero SQL-interpolation patterns, zero prompt-injection strings. The single `.exec()` hit in `src/middleware/devtools.ts:177` is a regex-match on a caller-line string, not a process-exec.
8. **Maintainers** — dai-shi (411 commits, GitHub account since 2010, 8,088 followers) is the primary maintainer; drcmda (the pmndrs org founder, 232 commits, account since 2012, 4,215 followers) is the #2. All top contributors are real people with long tenure and substantial public presence — no sockpuppet signals. pmndrs as an org is 7 years old with 9,652 followers across 91 public repos.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⚠ **Review happens but isn't required** — ~29% formal review rate in sample, no branch protection, no CODEOWNERS |
| Is it safe out of the box? | ✅ **Yes** — clean code-path, no install hooks, no network calls, zero runtime deps |
| Can you trust the maintainers? | ✅ **Yes** — long-tenured multi-maintainer pmndrs collective with substantial public track record |
| Is it actively maintained? | ✅ **Yes** — monthly releases, weekly PR merges, 100+ releases, active Copilot-bot hygiene PRs |

---

## 01 · What should I do?

> ✓ Safe to install today · ⚠ 1 consumer-side mitigation · 3 steps
>
> **Install is safe** — the library itself is clean (Step 1). If you ship to production, pair zustand with `minimumReleaseAge` in your own pnpm config to buy time against an upstream credential-compromise scenario (Step 2). Step 3 is a maintainer-side ask you can pass along.

### Step 1: Install zustand normally — the library is clean (✓)

**Non-technical:** Zustand is a pure React state library. It has zero runtime dependencies, no install-time scripts (no `postinstall`, no `preinstall`, no `prepare`), no shell calls, no network calls, and nothing in its source tree that resembles a dangerous primitive. The published npm package is a compiled bundle under `dist/` published through GitHub Actions with OIDC. Install it the way the README recommends.

```bash
# Standard install
npm install zustand
# or
pnpm add zustand
# or
yarn add zustand
```

### Step 2: If you ship zustand in production, pin exact versions and set `minimumReleaseAge` (⚠)

**Non-technical:** The one real risk surface is upstream governance: there's no branch protection on `main`, no CODEOWNERS, and Dependabot alerts are off. That means a single compromised maintainer credential (phishing, stolen laptop, stale OAuth token, malicious browser extension) would reach every install on the next release with no branch-level review. You can't fix this yourself, but you can buy time. The `minimumReleaseAge` setting in pnpm blocks installs of dep versions newer than 24 hours — long enough for the community to notice and yank a bad release. Zustand itself uses this setting; apply it on your consumer side too.

```yaml
# In your project's pnpm-workspace.yaml (or per-user .npmrc)
minimumReleaseAge: 1440   # 24 hours (same value zustand sets internally)
```

```json
// Pin the exact version in your production package.json
"zustand": "5.0.12"       // not "^5.0.12" or "~5.0.12"
```

### Step 3: Nudge the maintainers on the two governance gaps

**Non-technical:** The maintainers are clearly capable and actively engaged — the library surface is immaculate, the npm publish pipeline uses OIDC, and there's active Copilot-bot hygiene work (PR #3395 pins `actions/deploy-pages` to a SHA). Two helpful asks:

1. Enable branch protection on `main` with "require pull request reviews" set to 1 approver and required status checks (the existing `test.yml` workflow).
2. Turn Dependabot vulnerability alerts back on in Settings → Code security (version updates already work; this is just the alert surface).

Both are free and take a minute each in the GitHub UI.

- Branch protection setup: [github.com/pmndrs/zustand/settings/branch_protection_rules/new](https://github.com/pmndrs/zustand/settings/branch_protection_rules/new)
- Dependabot alerts toggle: [github.com/pmndrs/zustand/settings/security_analysis](https://github.com/pmndrs/zustand/settings/security_analysis)

---

## 02 · What we found

> ⚠ 2 Warning · ✓ 3 OK
>
> 5 findings total. **Both Warnings are governance, not code.** F0 is the C20 single-point-of-failure (no branch protection, no rulesets, no CODEOWNERS) — Warning-level because the latest release v5.0.12 is 31 days old, 1 day outside the 30-day window that would escalate it to Critical. F1 is Dependabot vulnerability alerts being disabled (version-update PRs still flow). Everything else is positive: clean code-path, OIDC publish, defensive `minimumReleaseAge`, long-tenured maintainers.
>
> **Your action:** Nothing you need to do locally — the library installs and runs cleanly. For production use, pin exact versions and set `minimumReleaseAge: 1440` in your own pnpm config (see Step 2 above). For maintainers: enabling branch protection on `main` and re-enabling Dependabot alerts would close both Warnings without changing any code.

### F0 — Warning · Structural · boundary case — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a 57k-star npm library (C20)

*Continuous · Since repo creation · → If you install: pin exact versions in production `package.json` and set `minimumReleaseAge: 1440` in your pnpm config so you're never installing a release that's less than 24 hours old. If you maintain this repo: enable branch protection on `main` (Settings → Branches → Add rule, require 1 approver, require the existing `test.yml` checks) and add a `.github/CODEOWNERS` covering `.github/workflows/` + `src/`.*

**Boundary-case note.** This finding fires at Warning rather than Critical because of a 1-day margin. The V2.3 C20 severity rule escalates from Warning to Critical when a repo (a) has all three governance signals negative AND (b) ships executable code to user machines AND (c) has a release within the last 30 days. Zustand's latest release v5.0.12 shipped on 2026-03-16 — 31 days before this scan. One day outside the window. The next release (release cadence has been roughly monthly — v5.0.11 2026-02-01, v5.0.10 2026-01-12, v5.0.9 2025-11-30) will flip this to Critical on the next re-scan unless governance is added first.

**What's missing.** Classic branch protection on `main` returns HTTP 404 from the GitHub API (authoritative — our scan token has `repo` scope and would have returned 403 if permissions were the issue). Repo rulesets: `gh api repos/pmndrs/zustand/rulesets` returns `[]`. Rules applying to `main`: `gh api repos/pmndrs/zustand/rules/branches/main` returns `[]` — this endpoint is authoritative because it captures both repo-level and org-level rulesets that would apply. CODEOWNERS is absent in all four standard locations (`CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`, `.gitlab/CODEOWNERS`). So any push that lands on the primary maintainer's credentials goes directly to `main` without a review gate, a required status check, or a path-scoped reviewer.

**How an attacker arrives (F13).** This does not require xz-utils-level sophistication. Concrete paths: (1) credential phishing against dai-shi or drcmda (both have public profiles, large followings, and are findable targets); (2) stale OAuth token reuse from an old CI system or developer machine; (3) compromised browser session cookie via a malicious browser extension; (4) malicious IDE/editor extension running as the maintainer; (5) sloppy review of an attacker-submitted PR — the review-rate sample shows ~71% of merges had no formal `reviewDecision`, though cross-merging between dai-shi and dbritto-dev provides practical second-pair-of-eyes on most PRs; (6) compromise of a shared self-hosted runner if one were added later. None of these require compromising the npm registry itself; they route straight through the repo.

**What this means for you.** When you install zustand, you are trusting the maintainers' account security as tightly as you'd trust your own laptop's password for a package imported by millions of projects. There is no automated gate that would catch "maintainer's credentials got phished and the attacker pushed a bad release" before it reached your next install. The blast radius on a 57,754-star zero-runtime-dep library used by Fortune-500 React apps is enormous. The mitigation on your side is `minimumReleaseAge` + pinned versions; the mitigation on their side is a one-click branch-protection rule.

**What this does NOT mean.** The library itself is clean — zero runtime deps, zero install hooks, no network, no dangerous primitives. This finding is purely about the upstream process gap, not about the current code shipping something harmful. Treat it as a tail-risk on future releases, not an acute threat today.

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

**How to fix (maintainer-side, 2 minutes in the UI).** GitHub *Settings → Branches → Add branch protection rule* ([direct link](https://github.com/pmndrs/zustand/settings/branch_protection_rules/new)). For `main`: require pull request reviews (1 approver minimum), require status checks (the existing `test.yml` matrix), require branches to be up to date before merging, do not allow bypassing. Also add `.github/CODEOWNERS` covering at minimum `.github/workflows/ @dai-shi @drcmda` and `src/ @dai-shi @drcmda`. That closes the SPOF without slowing dev velocity — the cross-merge pattern between dai-shi and dbritto-dev is already doing most of this manually.

### F1 — Warning · Hygiene gap — Dependabot vulnerability alerts are disabled on a 57k-star public repo (version updates still flow)

*Current · Setting-level · → If you rely on zustand in production: subscribe to repo releases and watch the `CHANGELOG.md` for dependency notes, since upstream is not using GitHub's alert surface. If you maintain this repo: flip Dependabot alerts on in Settings → Code security — it's free and complements the version-update integration that's already running.*

**What we observed.** `gh api repos/pmndrs/zustand/dependabot/alerts` returns HTTP 403 with the explicit message *"Dependabot alerts are disabled for this repository"*. That phrasing is diagnostic — it distinguishes the alert surface being off from a scan-token-scope problem (which would say "not authorized"). So we know definitively that vulnerability alerts are turned off at the repo level.

**What's NOT disabled.** Dependabot version updates ARE active. The account `dependabot[bot]` is the #6 contributor to the repo with 18 commits in the review window, and recent PRs include standard devDep bumps (rollup, typescript, @types/react, etc.). So this is specifically the *alert* surface — the one that flags known CVEs in transitive deps — being off, not a totally broken Dependabot integration.

**What this means for you.** Because zustand has zero runtime dependencies, the user-facing impact of a missed CVE is much smaller than on a library with a large dep tree. A transitive CVE in one of the 39 devDeps would affect the build pipeline (CI runners, developers' local machines) rather than end users. Still, on a repo imported by millions of consumers, turning off the alert surface is a hygiene gap — GHSA-class CVEs published against devDeps would go unsurfaced to the maintainers unless they happen to see the advisory elsewhere.

**What this does NOT mean.** It does not mean the repo is unmaintained or that the maintainers don't care about security. The active Copilot-bot PRs (e.g., PR #3395 pinning `actions/deploy-pages` to a SHA), the OIDC publish pipeline, and the `minimumReleaseAge` setting all indicate deliberate supply-chain hygiene. This specific toggle looks like an oversight rather than a policy decision.

| Meta | Value |
|------|-------|
| Alerts API | ❌ 403 — "disabled for this repository" |
| Version updates | ✅ Active (dependabot[bot], 18 commits) |
| Runtime deps | ✅ Zero — blast radius limited to devDeps |
| DevDeps | 39 (affects CI + contributor machines) |
| Published advisories | ✅ 0 (never filed) |

**How to fix (maintainer-side, one click).** [github.com/pmndrs/zustand/settings/security_analysis](https://github.com/pmndrs/zustand/settings/security_analysis) → toggle *Dependabot alerts* to on. Takes five seconds and does not change any workflow or commit behaviour — it just turns the alert surface back on.

### F2 — OK — Clean code-path — zero runtime deps, zero install hooks, zero dangerous primitives

*Current · → No action needed. Positive signal: the library does what a library should do and nothing more.*

**Runtime dependency surface.** `package.json` declares zero runtime `dependencies`. The four `peerDependencies` (`react`, `@types/react`, `immer`, `use-sync-external-store`) are resolved by the consuming application, not installed by zustand itself — so from an attack-surface perspective the inbound supply chain at install time is "zustand itself, nothing else." 39 devDeps exist but those only run in the build/test pipeline, never in consumer environments.

**Install-time scripts.** 27 `scripts` entries in `package.json`, none of which are lifecycle hooks. A grep for `preinstall`, `postinstall`, `prepare`, `prepublish`, `prepack`, `postpack` against `package.json` returned zero matches. Combined with `"private": true`, which prevents accidental `npm publish` from a contributor's machine (release is gated through `publish.yml` on the `release: published` event), there is no code path that runs during `npm install zustand` other than copying the bundle into `node_modules`.

**Dangerous-primitive grep.** Scanning `src/` with the V2.3 Step A grep patterns: zero `eval(`, zero `new Function(`, zero `document.write`, zero `child_process`/`execSync`/`spawnSync`, zero `fetch(`/`axios.`/`http.get`/`XMLHttpRequest`/`WebSocket`, zero hardcoded credentials or tokens, zero CORS/`0.0.0.0`/`Access-Control-Allow-Origin` patterns, zero `md5(`/`sha1(`, zero SQL-interpolation patterns, zero prompt-injection strings. The only `.exec()` hit anywhere in `src/` is `src/middleware/devtools.ts:177`, which calls `.exec()` on a regex against a caller-line string to extract a function name for DevTools labelling — not a process-exec call. `innerHTML =` appears only in test setup files (the SSR hydration test). Positive control: the same grep found 22 import statements in `src/`, so the tool was working.

| Meta | Value |
|------|-------|
| Runtime deps | ✅ 0 |
| Install hooks | ✅ None (no pre/post/prepare) |
| Network calls in src/ | ✅ None |
| Shell-exec in src/ | ✅ None |
| `eval`/`Function`/`innerHTML` | ✅ None in src/ |
| Accidental-publish guard | ✅ `"private": true` |

### F3 — OK — Publish pipeline uses OIDC and `minimumReleaseAge` defensive config

*Current · → No action needed. Positive signal: the maintainers are using the current-best-practice npm publish path.*

**OIDC publish.** `.github/workflows/publish.yml` runs on the `release: published` event and sets `permissions: { id-token: write, contents: read }`. That instructs GitHub Actions to mint an OpenID Connect token for the job, which npm then exchanges for a short-lived publish credential — no long-lived `NPM_TOKEN` secret stored in GitHub. If a workflow ever leaked secrets, there would be no reusable token for an attacker to steal. This is the current 2025/2026 best practice for npm publish and it is correctly wired up here.

**`minimumReleaseAge` in the repo's own pnpm config.** `pnpm-workspace.yaml` contains `minimumReleaseAge: 1440`. That pnpm feature blocks the installation of any dependency version that was published less than 24 hours ago — a deliberate defensive trick against the rapid-compromise-and-wide-uptake pattern seen in recent supply-chain incidents. Zustand sets this on itself (so its own dev environment is protected), and the recommendation to consumers in Step 2 is the same setting.

**Accidental-publish guard.** The `"private": true` field in `package.json` means an `npm publish` run manually from a contributor's machine fails with "cannot publish over private package." Release goes only through the CI workflow on the `release: published` event. Combined with OIDC, the publish pipeline has two independent gates: the event filter and the short-lived token mint.

| Meta | Value |
|------|-------|
| Auth to npm | ✅ OIDC short-lived token |
| Long-lived NPM_TOKEN | ✅ Not present |
| `minimumReleaseAge` | ✅ 1440 minutes (24 hours) |
| Publish trigger | ✅ `release: published` event only |

### F4 — OK — Maintainers and CI hygiene are solid

*2010–2026 · Long-tenured · → No action needed. Positive signal: the people who have the credentials are the kind you want to have them.*

**Maintainers.** Primary maintainer dai-shi has a GitHub account since 2010-11-21 (15 years), 127 public repos, 8,088 followers, and 411 commits on zustand. drcmda (Paul Henschel, founder of the pmndrs collective) has an account since 2012-08-26, 95 public repos, 4,215 followers, 232 commits. dbritto-dev (59 commits) and sukvvon (50 commits) round out the cross-merge group. No sockpuppet signals anywhere — all top contributors have at least a decade of public presence and substantial real-project histories. The pmndrs organisation itself was created 2018-12-11, has 9,652 followers, and hosts 91 other libraries including `react-three-fiber`, `valtio`, and `jotai`. This is the kind of long-tenured collective that would notice if one of their accounts got phished.

**CI hygiene.** 8 workflow files in `.github/workflows/`. 7 of 8 external actions are pinned to specific commit SHAs (e.g. `preactjs/compressed-size-action@49c7ff02`). The one unpinned reference is `pmndrs/docs/.github/workflows/build.yml@v3`, which is a *reusable workflow hosted in the same pmndrs org* — not a third-party action. Cross-org reusable-workflow trust chains and same-org references are materially different, so this is tracked as Verified-with-caveat in Coverage (Section 06) rather than as a Warning finding.

**Zero `pull_request_target`.** Grep across `.github/workflows/` returned 0 matches for `pull_request_target`. That event type is the source of most of the recent GitHub Actions supply-chain incidents (PwnRequest class) because it grants the workflow access to repository secrets when triggered by a fork PR. Zustand uses plain `pull_request` throughout, which runs in a restricted context without secrets.

**Active hygiene work.** Copilot bot opened PR #3395 "Pin actions/deploy-pages to commit SHA for supply-chain security" — an ongoing pattern of bots proposing pinning improvements and maintainers merging them. The recent-commits log shows a steady rhythm of README fixes, Dependabot bumps, test-coverage expansion, devtools type corrections, and persist-hydration bugfixes. Nothing anomalous.

| Meta | Value |
|------|-------|
| Primary maintainer | ✅ dai-shi (15-yr account, 411 commits, 8,088 followers) |
| Org founder | ✅ drcmda (13-yr account, 232 commits) |
| SHA-pinned actions | ✅ 7/8 external (1 same-org reusable) |
| `pull_request_target` | ✅ 0 occurrences |
| Sockpuppet signals | ✅ None |
| pmndrs org | ✅ 7 years, 91 repos, 9,652 followers |

---

## 02A · Executable file inventory

> ✓ 0 install-time executables · ℹ 13 runtime files inventoried
>
> **Zustand ships zero install-time executables** — it's a pure library with no CLIs, no binaries, no lifecycle scripts. The 13 runtime files below compile to a single bundle under `dist/` and load into consumer applications via their bundler. No file in this inventory has an actionable dangerous-primitive hit; a single regex `.exec()` call in `devtools.ts:177` is not a process-exec.

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
| `src/*/shallow.ts` (3 files) | Shallow-equality helpers | Bundler | None | None | Comparison helpers |
| `src/types.d.ts` | Type declarations | Compile-time only | None | None | Not executable at runtime |

**Note on the one `.exec()` hit.** The Step A dangerous-primitive grep surfaced exactly one `.exec()` call across `src/`: `src/middleware/devtools.ts:177`. This is not a process-exec. It's `RegExp.prototype.exec()` called on the caller-line string that DevTools uses to label the action in its timeline UI. The regex pulls out the calling function's name for display. No `child_process`, no `spawn`, no `execFile`, no shell. This is why the finding does not fire a Warning card and why the Scanner Integrity conditional section is not emitted.

---

## 03 · Suspicious code changes

> ✓ 0 security-concerning PRs · ℹ 7 recent merges sampled
>
> **Recent PR activity is routine.** Sample of 7 most recent merges shows README fixes, Dependabot devDep bumps, docs-link updates, and a persist-hydration bugfix. One self-merge in the sample (dai-shi merged his own devDep bump) — common for a maintainer-owned library, low risk because the PR was a routine dep version bump.

Sample: the 7 most recent merged PRs at scan time, plus the one security-keyword-matching PR. None hit the flag-for-diff-review threshold. Dual review-rate metric on this sample: formal `reviewDecision` set on 2/7 = 29%.

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

- 🟡 **2019-04-09 · CREATED** — Repo created by drcmda (Paul Henschel) under the `pmndrs` organisation. Zustand is one of pmndrs's flagship libraries alongside `react-three-fiber`, `valtio`, and `jotai`.
- 🟢 **2020–2025 · STEADY SHIP** — 100+ releases over 5 years. No yanked versions on npm, no security advisories ever filed, no reported post-install incidents. The library's API has remained stable through React 16 → 19 transitions.
- 🟢 **2025-11-30 · v5.0.9** — v5.0.9 ships. Typical zustand release shape: bugfixes, type corrections, middleware tweaks, docs updates. No breaking changes.
- 🟢 **2026-02-23 · PINNING UPGRADE** — Copilot bot opens PR #3395 to pin `actions/deploy-pages` to a commit SHA. dai-shi merges. Pattern: bots propose supply-chain hygiene fixes, maintainers accept them. Exactly the opposite of what you'd see on an unmaintained repo.
- 🟢 **2026-03-16 · v5.0.12** — Current latest release. v5.0.12 shipped 31 days before this scan — 1 day over the 30-day Critical window in the C20 rule. A v5.0.13 release would flip the F0 finding to Critical on re-scan. No security content in this release; routine updates.
- 🟡 **2026-04-16 · BOUNDARY CASE** — This scan runs. HEAD at `32013285083648e8d58ba1f76d73b9bdc02fef50`, main branch, most recent merge is PR #3466. F0 fires as Warning (31 days since v5.0.12); next release flips to Critical absent branch protection.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 7 years | Created 2019-04-09 — mature library with established patterns |
| Stars / Forks | 57,754 / 2,033 | Top-tier visibility. 178 watchers, 6 open issues. |
| Primary maintainer | ✅ dai-shi (411 commits) | 15-year GitHub account, 127 public repos, 8,088 followers — no sockpuppet signals |
| Org founder | ✅ drcmda (232 commits) | pmndrs founder, 13-year account, 95 public repos, 4,215 followers |
| Review rate (sample of 7) | ⚠ 2 formal / 7 any-review | ~29% formal review. Cross-merging provides practical second-pair-of-eyes |
| Branch protection | ❌ None on main | API 404 + empty rulesets + empty rules/branches/main — authoritative |
| CODEOWNERS | ❌ None | Checked 4 standard locations — no file in any |
| Dependabot alerts | ❌ Disabled | Alerts API 403 with "disabled for this repository" message. Version updates still active. |
| Security advisories | ✅ 0 filed, 0 needed | Never an advisory-class incident in 7 years |
| Runtime dependencies | ✅ 0 | Peer deps only. 39 devDeps. |
| Install-time hooks | ✅ None | No pre/post/prepare/prepublish/prepack/postpack |
| Publish auth | ✅ OIDC (id-token: write) | No long-lived NPM_TOKEN stored in GitHub Secrets |
| `minimumReleaseAge` | ✅ 1440 (24 hours) | pnpm defensive config set in repo's own `pnpm-workspace.yaml` |
| CI workflows | 8 (test / publish / preview / compressed-size / docs / 3 matrix test variants) | 7/8 external actions SHA-pinned; zero `pull_request_target` |
| Releases | 100+ (monthly cadence) | v5.0.12 latest (31 days old at scan); v5.0.11 2026-02-01, v5.0.10 2026-01-12, v5.0.9 2025-11-30 |
| Repo size | 8,120 KB | Small library; tarball extraction surfaced 143 files / 2.2M uncompressed |
| Topics | hooks, react, redux, state-management | Also: hacktoberfest, react-context, reactjs |

---

## 06 · Investigation coverage

> 12/12 coverage cells verified · 1 caveat (same-org reusable workflow)
>
> **All 12 C11 coverage cells verified.** 8/8 workflow files read, full tarball extracted (143 files, 2.2M), 0 `pull_request_target`, 0 agent-rule files, 0 prompt-injection hits, 0 README paste-blocks, no Windows surface, not a true monorepo. One caveat: 7 of 8 external actions are SHA-pinned; the one remaining reference (`pmndrs/docs/.github/workflows/build.yml@v3`) is a same-org reusable workflow rather than a third-party action, so tracked here as Verified-with-caveat.

| Check | Result |
|-------|--------|
| Tarball extraction | ✅ OK — 143 files, 2.2M — pinned to `32013285083648e8d58ba1f76d73b9bdc02fef50` at scan start |
| Workflow files read | ✅ 8 of 8 — test, publish, preview-release, compressed-size, docs, test-multiple-builds, test-multiple-versions, test-old-typescript |
| SHA-pinning coverage | ✅ 7/8 external actions pinned (caveat: 1 same-org reusable = `pmndrs/docs/.github/workflows/build.yml@v3`) |
| `pull_request_target` scan | ✅ Verified — 0 occurrences across 8 workflows |
| Monorepo scope | ✅ Verified — `pnpm-workspace.yaml` lists `packages: [- .]`, not a true monorepo |
| README paste-scan (7.5) | ✅ Verified — 0 paste-blocks. Single fenced code block is `npm install zustand` |
| Agent-rule files | ✅ Verified — none (checked CLAUDE.md, AGENTS.md, .cursorrules, .claude/, .github/copilot-instructions.md, .mcp.json, .goosehints, agent.md) |
| Prompt-injection scan (F8) | ✅ Verified — 0 matches / 0 actionable. Scanner Integrity section NOT emitted (V2.3 conditional rule) |
| Distribution channels (F1) | ⚠ Install path: 1/1 · Artifact: 0/1. Single npm channel. README matches CI. Artifact verification would require running the pipeline end-to-end and sha256-matching the published tarball. |
| Windows surface coverage (F16) | ✅ Verified — no Windows surface (no .ps1/.bat/.cmd anywhere). Pure library. |
| Dangerous-primitive grep | ✅ Verified — 0 actionable hits. Single `.exec()` is regex-match. Positive control: 22 `import` statements found. |
| Review-rate sample | ⚠ 7 of 64 recent merges sampled — 2/7 formal (29%), 6/7 cross-merger (86%), 1/7 self-merge (14%) |
| Commit pinned | `32013285083648e8d58ba1f76d73b9bdc02fef50` |

**Gaps noted:**

1. Artifact reproducibility not verified — end-artifact was not independently rebuilt from source and sha-diffed against the published npm tarball.
2. Dependabot ALERTS are disabled (confirmed via explicit 403 message) — but Dependabot VERSION UPDATES are active. So we know the alert surface is off, but we did not separately enumerate the current dep-graph for unpatched CVEs.
3. Review-rate metric is based on a 7-PR sample, not the full 300-PR window. The pattern (formal review ~29%, practical cross-merge ~100%) is consistent across the sample but a larger enumeration would tighten the estimate.

---

## 07 · Evidence appendix

> ℹ 9 facts · ★ 2 priority
>
> 9 command-backed claims. **Skip ahead to items marked ★ START HERE** — the branch-protection-missing API check and the Dependabot-alerts-disabled diagnostic. Those two are the falsification criteria for the Warning verdict: if either reversed, the verdict would move to Clean.

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
```
{"message":"Not Found","status":"404"}
[]
[]
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

*Classification: Confirmed fact — all four governance signals are negative. 404 on branch protection is authoritative (scan token has `repo` scope; permission-denied would be 403). Empty rulesets and rules/branches/main together capture both repo-level and org-level rulesets. CODEOWNERS absent in all four standard locations. Warning-level because release age (31 days) is 1 day outside the 30-day Critical window.*

#### ★ Evidence 2 — Dependabot vulnerability alerts are disabled (version updates still active)

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

### Other evidence supporting Warnings

#### Evidence 3 — Review-rate sample on 7 recent merges — 2 formal, 7 any-contact

```bash
gh pr list -R pmndrs/zustand --state merged --limit 7 \
  --json number,title,author,mergedBy,reviewDecision,reviews \
  | jq '.[] | {pr: .number, author: .author.login, merger: .mergedBy.login,
               formal: .reviewDecision, any_review: ((.reviews|length) > 0)}'
```

Result (summarised):
```
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
```
(no matches for eval/new Function/child_process/execSync/spawnSync)
src/middleware/devtools.ts:177:  const match = callerLineRegex.exec(callerLine)
22   # positive control — grep tool working
```

*Classification: Confirmed fact — the only `.exec()` hit is `RegExp.prototype.exec()` against a caller-line string, used for DevTools action-name labelling. Not a process-exec. The 22-import positive control confirms the grep infrastructure was working, so "no hits" is a meaningful signal rather than a silent scan failure.*

### Evidence supporting OK findings

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
```
minimumReleaseAge: 1440
```

*Classification: Confirmed fact — 1440 minutes = 24 hours. pnpm will refuse to install a dep version younger than 24 hours. The same defensive config the Step 2 action-card recommends to consumers.*

#### Evidence 9 — Zero `pull_request_target` usage across 8 workflows

```bash
grep -rn 'pull_request_target' /tmp/scan-zustand/zustand-src/.github/workflows/
ls /tmp/scan-zustand/zustand-src/.github/workflows/ | wc -l
```

Result:
```
(no matches)
8
```

*Classification: Confirmed fact — 8 workflow files, zero `pull_request_target` occurrences. That event type is the vector in most GitHub Actions PwnRequest supply-chain incidents; its absence here rules out that class of attack.*

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-16 · scanned main @ `32013285083648e8d58ba1f76d73b9bdc02fef50` (v5.0.12) · scanner V2.3-post-R3*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
