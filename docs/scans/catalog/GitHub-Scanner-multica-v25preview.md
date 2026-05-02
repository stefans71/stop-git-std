# Security Investigation: multica-ai/multica

**Investigated:** 2026-05-02 | **Applies to:** main @ `3df95c84b8af6f26b6d4fe8ccfcaca74ee977cf1` | **Repo age:** 0 years | **Stars:** 23,547 | **License:** NOASSERTION

> multica-ai/multica — 23.5k-star open-source agentic platform (TS+Go monorepo, Electron desktop, GHCR self-host), 4 months old, 84 contributors. The 888888 dev-verification-code Critical from the 2026-04-19 prior scan is now Warning (APP_ENV=production gate landed ~2026-04-18). Active responsiveness — 5 security issues closed in past 8 days. Open concerns: branch-protection ruleset declared but enforcement disabled (5.7% review rate, 73% self-merge), curl|bash installer skips SHA256 verification on macOS/Linux (Windows DOES verify), and #1114 LD_PRELOAD privesc on agent custom_env still open at 16 days. Caution.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-multica.md` (+ `.html` companion) |
| Repo | [github.com/multica-ai/multica](https://github.com/multica-ai/multica) |
| Short description | Open-source managed agents platform — assign coding tasks to AI agents (Claude Code, Codex, Hermes, etc.) via web/desktop dashboard. TS monorepo + Go server + Electron desktop, distributed via Homebrew + curl|bash + GHCR Docker images. By multica-ai (organization, 84 contributors). |
| Category | `developer-tooling` |
| Subcategory | `agentic-platform` |
| Language | TypeScript |
| License | NOASSERTION |
| Target user | Developer or small AI-native team adopting agent-managed task workflows. Cloud users hit `brew install multica-ai/tap/multica` then `multica setup`. Self-host operators run `curl ... install.sh | bash -s -- --with-server` then `multica setup self-host`. |
| Verdict | **Caution** (split — see below) |
| Scanned revision | `main @ 3df95c8` (release tag ``) |
| Commit pinned | `3df95c84b8af6f26b6d4fe8ccfcaca74ee977cf1` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-05-02` |
| Prior scan | Re-scan of multica-ai/multica. Catalog entry 11 was scanned 2026-04-19 at HEAD b8907dd (V2.4 / delegated, Caution split). Current scan: V2.5-preview at HEAD 3df95c8 (16 days later, +4 commits visible in PR cadence). Verdict still Caution; the 888888 dev-code Critical concern from prior scan is now Warning because APP_ENV gate landed (closed issue #1304, ~2026-04-18). Open #1114 LD_PRELOAD privesc is new vs prior scan. |

---

## Verdict: Caution (split — Deployment axis only)

### Deployment · Cloud CLI consumer (default `multica setup`) — **Caution — Use Homebrew; review CLI updates' release notes; the cloud-side has no exposure to the self-host bypass paths.**

### Deployment · Self-host operator (`--with-server`) — **Caution — Do NOT change APP_ENV from production. Pin to a release tag once releases ship. Watch issue #1114 before exposing custom_env to untrusted workspace operators.**

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Caution — 5 Warning findings cluster around process gaps + install-path asymmetry (5 findings)</strong>
<br><em>23.5k-star agentic-platform monorepo, 4 months old, 84 contributors but 5.7% review rate and 73% self-merge. Governance ruleset exists but enforcement is off. Curl-pipe installer skips checksums on Unix.</em></summary>

1. **F0** — Self-host 888888 dev-code path is APP_ENV=production-gated by default (improved from prior scan); operator-error scenarios re-open it.
2. **F1** — install.sh on macOS/Linux skips SHA256 verification; install.ps1 on Windows does verify.
3. **F2** — Branch-protection ruleset exists but `enforcement: disabled`. No CODEOWNERS, no SECURITY.md.
4. **F3** — 5.7% formal review rate; 220 of 300 sample PRs self-merged. The operational shape of F2.
5. **F4** — 4 open security issues (#1114 16-day LD_PRELOAD privesc); 5 fixed in past 8 days — responsive but not shrinking.

</details>

<details>
<summary><strong>ℹ Info — F5 + F6 are upstream-tracking + scanner coverage notes (2 findings)</strong>
<br><em>1 known low-severity transitive XSS; OSSF/gitleaks/npm-registry coverage gaps logged.</em></summary>

1. **F5** — @tiptap/extension-link GHSA-vhrc-hgrq-x75r — single low-severity transitive vuln. No Dependabot config.
2. **F6** — Scanner did not run gitleaks; OSSF Scorecard not indexed; 10/10 npm packages registry-status `unavailable`.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — 5.7% review rate, 73% self-merge, branch-protection ruleset declared but enforcement disabled, no CODEOWNERS |
| Is it safe out of the box? | ⚠ **Partly** — Homebrew path is safe; curl|bash path on macOS/Linux skips checksum verification (Windows installer does verify); APP_ENV=production gate defends the 888888 path by default |
| Do they fix problems quickly? | ⚠ **Mixed** — 5 security issues closed in past 8 days (responsive), but 4 still open with oldest 16 days (privesc unaddressed) |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md, no published advisories, no Dependabot config; reporters use generic issues |

---

## 01 · What should I do?

> 23.5k⭐ · NOASSERTION · TS+Go monorepo · 5 warnings · 1 info · caution
>
> multica-ai/multica is a 4-month-old open-source agentic platform — assign coding tasks to AI agents the way you'd assign to a teammate. The repo is a pnpm + Turborepo TypeScript monorepo (apps/web Next.js, apps/desktop Electron, packages/{core,ui,views,eslint-config,tsconfig}) plus a Go server (server/) and a CLI binary built via GoReleaser. 84 contributors with the top contributor at 29.7% commit share — actively multi-maintainer. The verdict is Caution rather than Critical because (a) the previously-flagged 888888 self-host bypass has been APP_ENV-gated since ~2026-04-18 (closing the 2026-04-19 prior scan's Critical concern); (b) 5 security issues have been closed in the past 8 days, indicating active triage; (c) 0 pull_request_target workflows means no PR-target attack surface. The Caution applies primarily to install-path discipline (curl|bash on Unix without checksums), the visible-but-disabled branch-protection ruleset, and the 16-day-old open privesc report (#1114).

### Step 1: If using cloud (multica.ai), install via Homebrew (✓)

**Non-technical:** The cloud path is the simplest and lowest-risk install: Homebrew tap with formula-pinning + checksum verification. After install, `multica setup` connects you to the cloud workspace.

```bash
brew install multica-ai/tap/multica && multica setup
```

### Step 2: If using curl|bash on Unix, download and read install.sh first (ℹ)

**Non-technical:** The README's curl|bash path on macOS/Linux skips SHA256 verification on the downloaded binary. Mitigation: download the script, read it, then bash it — or just use Homebrew (step 1) where possible.

```bash
curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh -o /tmp/multica-install.sh && less /tmp/multica-install.sh && bash /tmp/multica-install.sh
```

### Step 3: If self-hosting, verify APP_ENV=production before exposing the instance (⚠)

**Non-technical:** The 888888 dev-verification-code path is disabled when APP_ENV=production. Docker self-host pins APP_ENV=production by default, but if you've inherited a non-default .env (e.g., from a guide that suggested setting APP_ENV=staging for dev), the bypass re-opens. Confirm before publishing the URL.

```bash
cd ~/.multica/server && docker compose -f docker-compose.selfhost.yml config | grep APP_ENV
```

### Step 4: If wiring custom_env into agent runtimes, read open issue #1114 (⚠)

**Non-technical:** Issue #1114 reports that the env-var allowlist for agent custom_env permits LD_PRELOAD/NODE_OPTIONS/HTTP_PROXY — which can let a workspace operator inject loader hooks into spawned agent CLIs. If your trust boundary includes 'workspace operators are not 100% trusted,' don't expose custom_env until #1114 lands.

```bash
gh issue view 1114 --repo multica-ai/multica
```

---

## 02 · What we found

> ⚠ 5 Warning · ℹ 2 Info
>
> 7 findings total.
### F0 — Warning · Deployment — Self-hosted hardening relies on operator preserving APP_ENV=production gate that disables the 888888 dev verification code

*Continuous · Since hardening landed (~2026-04-18, per closed issue #1304) · → If self-hosting, do NOT change APP_ENV from `production`. Verify your `docker compose ... config` shows `APP_ENV=production` before going live; treat any non-production APP_ENV as a public-instance disqualifier until MULTICA_DEV_VERIFICATION_CODE is also empty.*

The 2026-04-19 prior scan flagged this as Critical: any operator running self-host with the dev verification code populated could log in as anyone via the literal `888888`. Since that scan, multica has added an APP_ENV=production gate in two places: server/cmd/server/main.go:128 logs a warning and skips activation when production; auth.go:97-108 isDevVerificationCode() short-circuits to false in production. Closed issue #1304 documents the fix.

docker-compose.selfhost.yml pins `APP_ENV: ${APP_ENV:-production}` by default, so the out-of-the-box self-host posture is hardened. The remaining Warning-level risk is operator error: an admin who deliberately sets APP_ENV to non-production (commonly done when running a private test instance) AND populates MULTICA_DEV_VERIFICATION_CODE re-opens the bypass.

The mitigation is config discipline rather than code change. The defense is one config flip away from being absent — which is why this is Warning rather than OK. A maintainer-side hardening would gate the dev-code variable at build-time, so the production binary cannot enable it under any runtime configuration.

**How to fix.** Operator-side: keep `APP_ENV=production` in your environment / .env. Leave `MULTICA_DEV_VERIFICATION_CODE` empty in production. If you need a test instance accessible from the internet, use a proper provider OAuth path (Google) instead of email codes and unset the dev code variable entirely. Maintainer-side: consider gating MULTICA_DEV_VERIFICATION_CODE on build-time (only compiled into dev builds) so the production binary cannot enable it under any runtime configuration.

### F1 — Warning · Distribution — curl-pipe-from-main installer with no checksum verification on macOS/Linux (Windows installer DOES verify)

*Continuous · Since installer scripts landed · → Prefer the Homebrew install path (`brew install multica-ai/tap/multica`) — formula-pinned and checksum-verified. If you must use the curl|bash path, download the script first and read it before piping to bash.*

Two install paths in the README run shell from the network. `curl -fsSL .../main/scripts/install.sh | bash` on macOS/Linux. `irm .../main/scripts/install.ps1 | iex` on Windows. Both fetch from the `main` branch (no SHA pin, no tag pin). install.sh's binary-download step (lines 83-130) scrapes the redirect on `releases/latest` to learn the tag, downloads the binary, and `mv`s it to /usr/local/bin without integrity check.

install.ps1 by contrast (lines 195-213) downloads `checksums.txt` from the release tag and validates SHA256 of the downloaded zip. Windows users get checksum verification; Linux/macOS users do not. The asymmetry reads as a feature gap (Windows installer was hardened later) rather than malicious — but it leaves the largest install audience (Unix) unverified.

The Homebrew install path (`brew install multica-ai/tap/multica`) sidesteps both. Homebrew formulae are tap-pinned and pull from a separate distribution channel with its own integrity checks. Whenever Homebrew is available, prefer it.

**How to fix.** Maintainer-side: add `checksums.txt` download + sha256sum verification to install.sh on the Unix path (mirror the install.ps1 pattern at lines 195-213). Optionally pin the install script to a release tag in the README curl command (`raw.githubusercontent.com/multica-ai/multica/v0.2.X/scripts/install.sh`) so install.sh updates are gated on tagged releases rather than every push to main. Consumer-side: prefer Homebrew where available; otherwise download install.sh first (`curl -O https://...`), read it, then `bash install.sh`.

### F2 — Warning · Governance — Branch-protection ruleset present-but-disabled, no CODEOWNERS, no enforced rules-on-default — visible-but-toothless governance posture

*Continuous · Since repo created (2026-01-13); ruleset added 2026-01-15 disabled · → Read open security issues (4 as of scan) before pulling; treat any cherry-picked direct-to-main commit as ungated until the `protect-main-branch` ruleset enforcement flips on.*

All four canonical governance signals are negative. Classic protection HTTP 404. Ruleset count 1 — but `enforcement: disabled` on the only ruleset (`protect-main-branch`, id 11828157, created 2026-01-15 and never enabled). Rules-on-default 0. CODEOWNERS not present at any of 4 standard paths. Org rulesets unknown (token scope).

The presence of a disabled ruleset is the most informative signal — the maintainers KNOW they should have branch protection (they created the rule) but have not flipped enforcement on. Whether this is intentional (perhaps to avoid friction during the 4-month bootstrap) or oversight, the operational result is identical: every push to main reaches consumers with no second-human gate.

84 contributors with the top contributor at 29.7% commit share — multica is NOT solo-maintained, so the bus-factor angle is weaker than the prior scan's framing. The risk is procedural (no enforced gate), not single-person SPOF. The C20 governance computer fires Warning rather than Critical because there are no formal releases yet (the recent-release amplifier that promotes governance-SPOF to Critical is N/A; multica ships via GHCR images and an as-yet-unpublished Homebrew tap).

**How to fix.** Maintainer-side: flip the existing `protect-main-branch` ruleset enforcement from `disabled` to `active` and require ≥1 review on PRs to main. Add a CODEOWNERS file (even self-listed) so reviewers are auto-requested. Add SECURITY.md to declare a disclosure channel. Consumer-side: pin to a release tag in install paths (`MULTICA_SELFHOST_REF=v0.2.X` env var) once releases ship, rather than tracking main.

### F3 — Warning · Process — 5.7% formal/any review rate over 300 closed PRs; 220 of 300 (73%) self-merged

*Continuous · Across 300-PR sample (recent ~2 weeks) · → Don't assume the next merged commit was reviewed by a second person — most aren't. Inspect security-relevant PR diffs directly when triaging an upgrade.*

300-PR sample yields 5.7% formal review rate, 5.7% any-review rate, and 220 of 300 PRs (73%) self-merged. Lifetime merged: 1,026 PRs. The `formal === any` equality is interesting — when reviews happen, they are formal approvals; the issue is they rarely happen.

30 of the 300 PRs in the sample carried security keywords (title or path). Combined with F2's missing enforcement, the operational shape is: most code reaching main has had no second-human read, including security-relevant changes. This is the lived consequence of F2 — a finding in its own right because the gap is observable in PR data independent of governance signals.

The fix is the same as F2: enabling the existing `protect-main-branch` ruleset with required-review-on-PR closes both findings. The maintainers have the scaffold; flipping enforcement on is a one-action change.

**How to fix.** Maintainer-side: enabling the `protect-main-branch` ruleset (see F2 fix) closes both findings — required-review-on-PR forces formal review, blocks self-merge. Consumer-side: when picking an install pin, choose a tagged release rather than `main`-tracking once releases exist.

### F4 — Warning · Vulnerabilities — 4 open security issues (oldest 16 days) including a privilege-escalation report on agent custom_env handling

*Recent (past 16 days) · Open: 2026-04-16 to 2026-04-25; Closed: 2026-04-16 to 2026-04-24 · → Before deploying multica with externally-controlled agent runtimes, read issue #1114 and decide whether the LD_PRELOAD bypass affects your trust model.*

Four security issues open at scan. The notable one is #1114 (16 days old): `isBlockedEnvKey allows LD_PRELOAD/NODE_OPTIONS/HTTP_PROXY override via custom_env`. The reporter walks through the agent-execution code path where workspace operators can pass loader-overriding env vars to spawned agent CLIs, escalating from workspace-operator privilege to whatever the agent CLI runs with. Unresolved past two weeks. The other three open items (#1382 vague report, #1663 brute-force protection, #1667 Origin/CSRF) are 7-12 days old.

Counter-signal: the team CLOSED FIVE security issues in the prior 8 days (2026-04-16 to 2026-04-24) — the 888888 self-host issue (#1304), shell.openExternal IPC URL-scheme bypass (#1115), Hermes filterCustomArgs bypass (#1113), /health/realtime metrics exposure (#1606), and open-redirect via ?next= (#1116). The fix rate roughly matches the open-arrival rate.

Pattern: responsive (5 closed in 8 days), but the queue is not shrinking. This is the operational shape of an active small-team project under active security-research scrutiny — the scrutiny is real (probably from the prior scan + community attention to agentic platforms), and the team is keeping up. The scorecard's Q2 advisory says red on the open-side count alone; the override to amber reflects the close-side counter-signal.

**How to fix.** Maintainer-side: prioritize #1114 (the LD_PRELOAD/NODE_OPTIONS bypass is a real privesc on the agent-execution path). Add SECURITY.md so reporters know the disclosure channel and labeled issues. Consumer-side: if you're running multica in any context where workspace operators are not 100% trusted, watch #1114 before wiring in custom_env.

### F5 — Info · Supply-chain — 1 known transitive vulnerability: @tiptap/extension-link (GHSA-vhrc-hgrq-x75r); no Dependabot config; alerts API behind admin scope

*Continuous · Until tiptap upstream patches · → Watch for tiptap upstream patch; consider enabling Dependabot in your fork if you self-host.*

osv.dev batch lookup over 30 declared deps yielded one advisory: @tiptap/extension-link GHSA-vhrc-hgrq-x75r (DOM XSS in tiptap link extension). Single low-severity transitive vuln in a UI library — not a deployment blocker, just a fix-and-bump waiting on upstream tiptap.

Defensibility gap: no `.github/dependabot.yml` is present. Even at the alert-only tier, Dependabot is not configured. The native Dependabot alerts API returned HTTP 403 (admin scope required) so the true alert state inside the maintainer view is unknown — but the absence of a config file means there's no automated bump-PR pipeline.

**How to fix.** Maintainer-side: add `.github/dependabot.yml` enabling at minimum the npm ecosystem on the root + monorepo packages. Consumer-side: noop for now — single low-sev XSS in a UI library is not a deployment blocker.

### F6 — Info · Coverage — Scanner coverage gaps: OSSF Scorecard not indexed; gitleaks not installed; npm registry probe unavailable for 10/10 declared packages

*Scan-time · 2026-05-02 scan · → Re-run with admin-scoped GitHub token + gitleaks installed for full coverage; check npm registry directly to confirm @multica/* packages are not yet published.*

Five coverage limitations independent of the repo: OSSF Scorecard returned HTTP 404 (repo not yet indexed; will appear once Scorecard's discovery threshold is crossed). gitleaks not installed in the scan environment, so secrets-in-history were not scanned. Dependabot alerts API 403 (admin scope). Org rulesets API errored (admin:org scope). npm registry presence probe `unavailable` for all 10 declared @multica/* packages — likely they haven't been published to npm yet, but the harness can't disambiguate that from registry-probe-failed.

Re-running with admin-scoped GitHub token + gitleaks installed + manual `npm view multica` would close all five gaps. None of these are findings about multica — they're scanner-side limits that consumers should know about so they can request a wider re-scan if needed.

**How to fix.** Re-run with: (a) `gh auth refresh -s admin:org` to enable org rulesets + Dependabot alerts; (b) `brew install gitleaks` (or equivalent) to enable secrets-in-history scan; (c) `npm view multica` to confirm npm registry status.

---

## 02A · Executable file inventory

> multica is a TypeScript monorepo + Go server + Electron desktop. The execution surface fans across 3 runtimes: (1) Go binary `multica` CLI (~500 LOC of cmd/ + handler/ + daemon/ in server/); (2) Node.js apps/web (Next.js App Router); (3) Electron apps/desktop. Plus 2 install scripts (install.sh 462 lines, install.ps1 483 lines) that the README pipes through bash/iex.

### Layer 1 — one-line summary

- Primary surface: Go server (server/ — cmd/server/main.go entrypoint + internal/handler + internal/daemon). Secondary surface: Next.js web app (apps/web). Tertiary surface: Electron desktop (apps/desktop). Distribution surface: scripts/install.sh (Unix), scripts/install.ps1 (Windows), Dockerfile + Dockerfile.web, docker-compose.selfhost.yml, .goreleaser.yml.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `scripts/install.sh` | installer | bash | curl-pipe-from-main; binary download via redirect-scrape; mv to /usr/local/bin without checksum (lines 83-130). git clone + git checkout in --with-server mode (lines 271-339). | Yes — fetches binary tarballs from GitHub release CDN; clones repo for self-host mode. | set -euo pipefail (defensive). Detects OS/arch. Falls back to ~/.local/bin if /usr/local/bin not writable. NO checksum verification on binary download — the asymmetry vs install.ps1 is F1. |
| `scripts/install.ps1` | installer | PowerShell | Invoke-Expression (`iex`) entry point per README. Invoke-WebRequest for binary + checksums. Expand-Archive to %LOCALAPPDATA%. | Yes — fetches binary zip + checksums.txt from GitHub release CDN. | Verifies SHA256 against checksums.txt (lines 195-213). The Unix install.sh does not have this — F1 asymmetry. |
| `server/cmd/server/main.go` | go-binary-entrypoint | Go runtime (compiled binary) | Configures HTTP server, JWT auth, agent runtime daemons. The 888888 dev-code env-var consumption is gated at line 128 by APP_ENV=production check. | Yes — listens on :8080 by default; outbound to Resend (email), Google OAuth, optional S3. | The APP_ENV=production gate at line 128 is the F0 defense. JWT_SECRET defaults to `change-me-in-production` if unset (warning logged). Generates JWT signing key per build. |
| `server/internal/handler/auth.go` | auth-handler | Go runtime | isDevVerificationCode() at line 97 — the 888888 path. Short-circuits to false in production (isProductionEnv check). Constant-time comparison at line 107. | Email-code send via Resend; verify-code endpoint accepts user-submitted codes. | Open issue #1663 reports lack of brute-force protection on /auth/verify-code (no lockout/backoff). Open issue #1667 reports Origin-header CSRF defense gap. |
| `docker-compose.selfhost.yml` | compose | Docker | JWT_SECRET defaults to insecure literal if unset (line 44). APP_ENV pinned to 'production' by default (line 58 — F0 defense). | Pulls ghcr.io/multica-ai/multica-{backend,web} images; tag default `latest` per .env.example. | install.sh setup_server() generates a random JWT_SECRET via `openssl rand -hex 32` on first install (line 304), patching the insecure default at install time. |

Two install-path entrypoints (install.sh / install.ps1) plus the Go server binary handle the consumer-facing risk. The TypeScript monorepo (apps/web + packages/*) is large but its risk profile is dominated by upstream npm deps (E11) rather than novel surface.

---

## 03 · Suspicious code changes

> ✓ 1 security-flagged PRs · ℹ 50 recent merges sampled

Sample: the 50 most recent merged PRs at scan time. Dual review-rate metric on this sample: formal `reviewDecision` set on 5.7% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1980](https://github.com/multica-ai/multica/pull/1980) | fix(daemon): add safe.directory=* to gitEnv to fix CI dubious ownership errors | ? | ? | no | Self-merge |
| [#1971](https://github.com/multica-ai/multica/pull/1971) | fix(views): preserve kanban display settings when dragging issues | ? | ? | no | Self-merge |
| [#1970](https://github.com/multica-ai/multica/pull/1970) | feat(inbox): remove redundant mark-as-done hover button, add archive button for done tasks | ? | ? | no | Self-merge |
| [#1969](https://github.com/multica-ai/multica/pull/1969) | fix(daemon): optimize quick-create prompt for high-fidelity descriptions | ? | ? | no | Self-merge |
| [#1961](https://github.com/multica-ai/multica/pull/1961) | fix(views): responsive Autopilot list for mobile viewports | ? | ? | no | Self-merge |
| [#1959](https://github.com/multica-ai/multica/pull/1959) | fix(skill): sanitize null bytes to prevent PostgreSQL UTF8 encoding error | ? | ? | APPROVED | — |
| [#1949](https://github.com/multica-ai/multica/pull/1949) | fix(runtimes): correct install script URL in connect remote dialog | ? | ? | no | — |
| [#1938](https://github.com/multica-ai/multica/pull/1938) | Increase empty claim cache TTL | ? | ? | APPROVED | — |
| [#1937](https://github.com/multica-ai/multica/pull/1937) | docs(changelog): publish v0.2.21 release notes | ? | ? | no | Self-merge |
| [#1936](https://github.com/multica-ai/multica/pull/1936) | fix(onboarding): decouple from workspace state and route invitees correctly | ? | ? | no | Self-merge |
| [#1934](https://github.com/multica-ai/multica/pull/1934) | fix(views): only show "Mark as Done" button on Inbox page | ? | ? | no | Self-merge |
| [#1933](https://github.com/multica-ai/multica/pull/1933) | docs: add Multica name origin section to README | ? | ? | no | Self-merge |
| [#1931](https://github.com/multica-ai/multica/pull/1931) | fix(daemon): reclaim disk on long-open issues + correct cancelled-status check | ? | ? | no | — |
| [#1930](https://github.com/multica-ai/multica/pull/1930) | refactor(repos): drop unused description + tighten create-project layout | ? | ? | no | Self-merge |
| [#1929](https://github.com/multica-ai/multica/pull/1929) | feat(projects): project github_repo resources override workspace repos | ? | ? | no | Self-merge |
| [#1928](https://github.com/multica-ai/multica/pull/1928) | fix(task): rerun starts a fresh session, skip poisoned resume | ? | ? | no | Self-merge |
| [#1927](https://github.com/multica-ai/multica/pull/1927) | feat(markdown): add fullscreen lightbox for mermaid diagrams | ? | ? | APPROVED | Self-merge |
| [#1926](https://github.com/multica-ai/multica/pull/1926) | feat(projects): typed project resources + agent runtime injection | ? | ? | no | Self-merge |
| [#1924](https://github.com/multica-ai/multica/pull/1924) | fix(quick-create): subscribe requester to issues created via quick-create | ? | ? | no | Self-merge |
| [#1921](https://github.com/multica-ai/multica/pull/1921) | fix(issues): wrap Details/Token usage in grid for PropRow subgrid | ? | ? | no | Self-merge |
| [#1919](https://github.com/multica-ai/multica/pull/1919) | feat(chat): no-agent disabled state with onboarding fix and editor cleanup | ? | ? | no | Self-merge |
| [#1915](https://github.com/multica-ai/multica/pull/1915) | feat: permission-aware UI across agent/comment/runtime/skill surfaces | ? | ? | no | Self-merge |
| [#1914](https://github.com/multica-ai/multica/pull/1914) | refactor(chat): simplify task-status-pill | ? | ? | no | Self-merge |
| [#1912](https://github.com/multica-ai/multica/pull/1912) | fix: stabilize mobile issue detail layout | ? | ? | no | — |
| [#1909](https://github.com/multica-ai/multica/pull/1909) | fix: prevent mobile input focus zoom | ? | ? | no | Self-merge |
| [#1907](https://github.com/multica-ai/multica/pull/1907) | feat(daemon): add Co-authored-by trailer for Multica Agent to git commits | ? | ? | no | Self-merge |
| [#1906](https://github.com/multica-ai/multica/pull/1906) | feat(inbox): notification preferences to control inbox noise by event type | ? | ? | no | Self-merge |
| [#1903](https://github.com/multica-ai/multica/pull/1903) | fix(daemon): prevent Quick Create from inventing requirements beyond user input | ? | ? | no | Self-merge |
| [#1901](https://github.com/multica-ai/multica/pull/1901) | feat(autopilots): show execution log for run-only autopilot runs | ? | ? | no | Self-merge |
| [#1897](https://github.com/multica-ai/multica/pull/1897) | fix(agents): navigate to detail page before invalidating list query | ? | ? | no | Self-merge |
| [#1896](https://github.com/multica-ai/multica/pull/1896) | fix(desktop): prevent Cmd+R / Ctrl+R / F5 from reloading the page | ? | ? | no | Self-merge |
| [#1894](https://github.com/multica-ai/multica/pull/1894) | feat(modals): persist drafts for create-project and feedback modals | ? | ? | no | Self-merge |
| [#1893](https://github.com/multica-ai/multica/pull/1893) | fix(inbox): auto-archive inbox item when marking done from issue detail | ? | ? | no | Self-merge |
| [#1892](https://github.com/multica-ai/multica/pull/1892) | feat(quick-create): enrich issue title and description with URL context | ? | ? | no | Self-merge |
| [#1889](https://github.com/multica-ai/multica/pull/1889) | feat(daemon): expose concurrent task slot env | ? | ? | no | — |
| [#1888](https://github.com/multica-ai/multica/pull/1888) | feat(markdown): render mermaid diagrams | ? | ? | CHANGES_REQUESTED | — |
| [#1887](https://github.com/multica-ai/multica/pull/1887) | fix(inbox): jump instantly to targeted comments | ? | ? | no | — |
| [#1886](https://github.com/multica-ai/multica/pull/1886) | feat(views): add remote machine / AWS EC2 connection wizard to Runtimes page | ? | ? | no | Self-merge |
| [#1885](https://github.com/multica-ai/multica/pull/1885) | feat(inbox): add one-click Done button to inbox items | ? | ? | no | Self-merge |
| [#1883](https://github.com/multica-ai/multica/pull/1883) | Improve quick create inbox previews | ? | ? | no | Self-merge |
| [#1881](https://github.com/multica-ai/multica/pull/1881) | fix: make workspace table columns resizable | ? | ? | no | — |
| [#1879](https://github.com/multica-ai/multica/pull/1879) | Refine Quick Create agent modal | ? | ? | no | — |
| [#1878](https://github.com/multica-ai/multica/pull/1878) | fix(ci): restore frontend checks | ? | ? | no | — |
| [#1875](https://github.com/multica-ai/multica/pull/1875) | fix(views): stop showing hardcoded model name in default model display | ? | ? | no | Self-merge |
| [#1873](https://github.com/multica-ai/multica/pull/1873) | fix(inbox): improve quick-create notification to show issue title prominently | ? | ? | no | Self-merge |
| [#1872](https://github.com/multica-ai/multica/pull/1872) | fix(views): remove redundant issue ID from breadcrumb | ? | ? | no | Self-merge |
| [#1868](https://github.com/multica-ai/multica/pull/1868) | fix(auth): route invitees to their workspace instead of forcing /onboarding | ? | ? | APPROVED | Security-flagged |
| [#1867](https://github.com/multica-ai/multica/pull/1867) | fix(desktop): show git-described version in dev instead of stale 0.1.0 | ? | ? | no | Self-merge |
| [#1866](https://github.com/multica-ai/multica/pull/1866) | feat(quick-create): add file upload button to Quick Capture dialog | ? | ? | no | Self-merge |
| [#1864](https://github.com/multica-ai/multica/pull/1864) | fix(quick-create): block submit while image uploads are in progress | ? | ? | no | Self-merge |

---

## 04 · Timeline

> ✓ 4 good · 🟡 4 neutral · 🔴 3 concerning

- 🟡 **2026-01-13 · Repo created** — Initial commit by multica-ai org
- 🔴 **2026-01-15 · Ruleset added — disabled** — ruleset id 11828157 `protect-main-branch` created with `enforcement: disabled`. Never enabled in 4 months.
- 🟢 **2026-04-16 · Hermes filterCustomArgs bypass closed** — Issue #1113 closed — security fix landed on agent-arg sanitization.
- 🔴 **2026-04-16 · LD_PRELOAD privesc reported (open)** — Issue #1114 — isBlockedEnvKey allows LD_PRELOAD/NODE_OPTIONS/HTTP_PROXY override via custom_env. Still open at scan.
- 🟢 **2026-04-17 · shell.openExternal fix** — Issue #1115 closed — desktop IPC accepted any URL scheme; restricted.
- 🟢 **2026-04-18 · 888888 + open-redirect fixes** — Issues #1304 (888888 / APP_ENV gate) + #1116 (open-redirect ?next=) closed. The APP_ENV gate closes the 2026-04-19 prior scan's Critical concern.
- 🟡 **2026-04-19 · Prior scan (V2.4 / delegated)** — Catalog entry 11 at HEAD b8907dd. Verdict: Caution split. Critical concern: 888888 dev auth bypass on self-host (Critical at the time, now mitigated).
- 🟢 **2026-04-24 · /health/realtime restricted** — Issue #1606 closed — restricted to loopback unless REALTIME_METRICS_TOKEN set.
- 🔴 **2026-04-25 · Brute-force + CSRF reports** — Issues #1663 + #1667 — both still open at scan.
- 🟡 **2026-05-01 · Latest push to main** — Last activity before scan.
- 🟡 **2026-05-02 · Scan date** — Re-scan of catalog entry 11. V2.5-preview at HEAD 3df95c8.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 23,547 |  |
| Forks | 2,890 |  |
| Open issues | 411 |  |
| Primary language | TypeScript |  |
| License | NOASSERTION |  |
| Created | 2026-01-13 |  |
| Last pushed | 2026-05-01 |  |
| Default branch | main |  |
| Total contributors | 84 |  |
| Top contributor | NevilleQingNY (29.7%) |  |
| Formal releases | 59 |  |
| Latest release | v0.2.23 (2026-05-01) |  |
| Classic branch protection | none (HTTP 404) |  |
| Repository rulesets | 1 |  |
| Rules on default branch | 0 |  |
| CODEOWNERS | absent |  |
| SECURITY.md | absent |  |
| CONTRIBUTING | present |  |
| Community health | 62% |  |
| Workflows | 4 |  |
| `pull_request_target` usage | 0 |  |
| Dependabot config | absent |  |
| PR sample size | 300 |  |
| Formal review rate | 5.7% |  |
| Any-review rate | 5.7% |  |
| Published GHSA advisories | 0 |  |
| OSSF Scorecard | not indexed |  |

---

## 06 · Investigation coverage

| Check | Result |
|-------|--------|
| Tarball extraction + local grep | ✅ Scanned (2763 files) |
| `gh api` rate limit | ✅ 4993/5000 remaining |
| OSSF Scorecard | ⚠ Not indexed (HTTP 404) |
| osv.dev dependency queries | ✅ 30 package(s) queried |
| Gitleaks | ⊗ Not available on this scanner host |
| Workflows | ✅ 4 detected |
| PR review sample | ✅ Sample size N=300 |
| Prompt-injection scan | ✅ 4 file(s); 0 signal(s) |
| Distribution channels inventory | ✅ Verified |

**Gaps noted:**

1. OSSF Scorecard — not_indexed: Repo not yet indexed by OSSF (4 months old). Will appear once the project crosses scorecard's discovery threshold.
2. Secrets-in-history (gitleaks) — not_available: gitleaks not installed in scan environment; install + re-run for git-history secret coverage.
3. Dependabot alert count — unknown: API returned HTTP 403 (admin scope required). Re-run with `gh auth refresh -s admin:org`.
4. Org rulesets — unknown: API errored (admin:org scope required). Re-run with elevated token to confirm whether an org-level ruleset enforces protection that the repo-level one does not.
5. npm registry status (10 packages) — unavailable: Harness reported `unavailable` for all 10 declared @multica/* packages. Likely not yet published — confirm with `npm view multica` and `npm view @multica/core`.

---

## 07 · Evidence appendix

> ℹ 14 facts · ★ 3 priority

### ★ Priority evidence (read first)

#### ★ Evidence 2 — Branch protection: classic protection HTTP 404. One ruleset declared (`protect-main-branch`, id=11828157) but `enforcement: disabled` — visible-but-toothless. Zero rules-on-default. CODEOWNERS not present at any of 4 standard locations.

```bash
gh api repos/multica-ai/multica/branches/main/protection ; gh api repos/multica-ai/multica/rulesets
```

Result:
```text
classic.status=404. rulesets.entries=[{name:'protect-main-branch', enforcement:'disabled'}], rulesets.count=1. rules_on_default.count=0. codeowners.found=False (checked CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS).
```

*Classification: fact*

#### ★ Evidence 5 — Closed security issues in past 16 days (responsive remediation): #1606 /health/realtime metrics exposure (closed 2026-04-24); #1304 'self-host 888888 master verification code may be enabled' (closed 2026-04-18); #1116 open redirect via ?next= (closed 2026-04-18); #1115 shell.openExternal IPC accepts any URL scheme in desktop app (closed 2026-04-17); #1113 Hermes backend bypasses filterCustomArgs (closed 2026-04-16).

```bash
gh issue list --state closed --search 'security' --limit 20
```

Result:
```text
5 security issues closed in 8 calendar days (2026-04-16 to 2026-04-24).
```

*Classification: fact*

#### ★ Evidence 7 — Checksum verification asymmetry: install.ps1 (Windows, line 195-213) downloads `checksums.txt` from the release and verifies SHA256 of the downloaded zip. install.sh (macOS/Linux, lines 83-130) downloads the binary tarball via redirect-scrape, runs `tar -xzf`, then `mv` to /usr/local/bin — NO checksum or signature verification.

```bash
grep -n 'checksum\|sha256\|verify' src/scripts/install.sh src/scripts/install.ps1
```

Result:
```text
install.ps1 has $checksumUrl + Invoke-WebRequest + SHA256 verify path. install.sh: zero checksum-related lines. Windows users get checksums; Unix users do not.
```

*Classification: fact*

### Other evidence

#### Evidence 1 — 23,547 stars, 84 contributors, top contributor NevilleQingNY at 787 commits (29.7% share). Created 2026-01-13, pushed 2026-05-01 — 4-month-old repo with active multi-contributor cadence.

```bash
gh api repos/multica-ai/multica + gh api repos/multica-ai/multica/contributors --jq '[.[]|{login,contributions}]'
```

Result:
```text
stargazer_count=23547, fork_count=2890, total_contributor_count=84. Top-1 share 29.7% — NOT solo (well below 80% threshold).
```

*Classification: fact*

#### Evidence 3 — PR review rate over 300-PR sample: 5.7% formal review, 5.7% any review. 220 of 300 sample PRs self-merged (73%). Lifetime merged total 1,026.

```bash
gh pr list --state closed --limit 300 + gh api repos/.../pulls?state=closed
```

Result:
```text
formal_review_rate=5.7, any_review_rate=5.7, self_merge_count=220, total_merged_lifetime=1026. 30 of 300 PRs flagged with security keywords.
```

*Classification: fact*

#### Evidence 4 — Open security issues — 4 total, oldest 16 days. #1114 (16d): isBlockedEnvKey allows LD_PRELOAD/NODE_OPTIONS/HTTP_PROXY override via custom_env (agent-execution privilege escalation). #1382 (12d): vague 'security vulnerability report' with question label. #1663 (7d): /auth/verify-code lacks brute-force protection. #1667 (7d): Origin header not validated on state-changing requests (CSRF defense gap).

```bash
gh issue list --state open --search 'security' --limit 50
```

Result:
```text
open_security_issues=4. Created dates: 1114=2026-04-16, 1382=2026-04-20, 1663+1667=2026-04-25. oldest_open_security_item_age_days=16.
```

*Classification: fact*

#### Evidence 6 — Install paths declared in README: (1) `brew install multica-ai/tap/multica` (Homebrew tap); (2) `curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash` (curl-pipe-from-main); (3) `irm https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.ps1 | iex` (Windows IEX-pipe-from-main); (4) `--with-server` flag on (2) clones repo and runs Docker self-host. install.sh tracks main, no SHA pin, no tag pin. install.ps1 same.

```bash
grep -n 'curl\|brew install\|irm\|iex' src/README.md
```

Result:
```text
Confirmed in README.md lines 65-100. install_script_analysis: scripts/install.sh tracks_main_branch=true sha_pinned=false tag_pinned=false (462 lines). scripts/install.ps1 same (483 lines). README pastes: 5 install commands all network-bound, all main-tracking.
```

*Classification: fact*

#### Evidence 8 — MULTICA_DEV_VERIFICATION_CODE behavior: empty by default in .env.example. server/cmd/server/main.go:128 logs warning + ignores when APP_ENV=production. server/internal/handler/auth.go:97-108 isDevVerificationCode() returns false unconditionally if isProductionEnv(). docker-compose.selfhost.yml line 58 pins APP_ENV default to 'production'.

```bash
grep -rn 'MULTICA_DEV_VERIFICATION_CODE\|isDevVerificationCode\|isProductionEnv' src/server src/docker-compose*.yml
```

Result:
```text
Verification: APP_ENV gate enforced in 2 places (main.go warning + auth.go check). docker-compose.selfhost.yml: `APP_ENV: ${APP_ENV:-production}`. Bypass requires operator explicitly setting APP_ENV != production AND setting the dev code.
```

*Classification: fact*

#### Evidence 9 — Workflows: 4 active. release.yml (380 lines, permissions block present, 0 SHA-pinned actions, 29 tag-pinned), ci.yml (84 lines, no permissions block, 5 tag-pinned), desktop-smoke.yml (59 lines, permissions block, 5 tag-pinned). Zero `pull_request_target` triggers across all workflows. release.yml validates tag format (semver regex) before publishing.

```bash
gh api repos/.../actions/workflows + read .github/workflows/*.yml
```

Result:
```text
0 SHA-pinned actions across all workflows; all action references are tag-pinned (e.g. actions/checkout@v4, goreleaser-action@v6). 0 pull_request_target. release.yml requires `if: github.repository_owner == 'multica-ai'` for the publish job.
```

*Classification: fact*

#### Evidence 10 — 10 npm package channels declared in package.json + workspace manifests (multica + 9 @multica/*: core, ui, desktop, views, eslint-config, tsconfig, docs). Harness reports `unavailable` for npm registry presence on all 10 — likely not yet published. Plus Homebrew tap (`multica-ai/tap/multica`) and a Go server binary built via GoReleaser.

```bash
registry probe via npm view + ls packages/*/package.json
```

Result:
```text
10 npm channels declared, 0 verified on registry. 1 Homebrew tap declared, registry probe unavailable. Distribution channels verified ratio: 0/10.
```

*Classification: fact*

#### Evidence 11 — Dependencies: 322 runtime + 122 dev. osv.dev lookup over 30 deps yielded 1 advisory: `@tiptap/extension-link` GHSA-vhrc-hgrq-x75r (low-severity DOM XSS in tiptap link extension). Dependabot config (.github/dependabot.yml) NOT present. Dependabot alerts API returned HTTP 403 (admin scope required — true alert state unknown).

```bash
osv.dev batch query + cat .github/dependabot.yml
```

Result:
```text
1 known transitive vuln. dependabot_config.present=False. dependabot_alerts.status=403. SECURITY.md not present.
```

*Classification: fact*

#### Evidence 12 — Agent-rule files: AGENTS.md (47 lines) and CLAUDE.md (358 lines) at repo root. Prompt-injection scan over both files: 0 signals detected. Content is standard architectural guidance (monorepo layout, state-management rules, CI commands), not instruction-injection vectors.

```bash
phase_1_harness.py prompt_injection_scan + manual review of CLAUDE.md head
```

Result:
```text
scanned_files=4 (2 unique + 2 src/ duplicates), injection_signals=0, scan_method=tarball.
```

*Classification: fact*

#### Evidence 13 — Coverage gaps: OSSF Scorecard returns HTTP 404 (repo not indexed — only 4 months old). gitleaks not installed in scan environment (cannot scan secrets-in-history). Dependabot alerts unknown (admin scope). Org rulesets unknown (admin:org scope).

```bash
OSSF API + gitleaks --version + gh api dependabot
```

Result:
```text
OSSF http_status=404. gitleaks.available=False. dependabot_alerts.status=403. org_rulesets.status=error.
```

*Classification: fact*

#### Evidence 14 — Releases: 0 published GitHub Releases at scan time. install.sh fallback: when no release tag is found, defaults to `main` branch. Self-hosted Docker images (`ghcr.io/multica-ai/multica-backend`) tag default `latest` per .env.example.

```bash
gh api repos/.../releases
```

Result:
```text
releases.total_count=0. install.sh get_selfhost_ref() returns 'main' if get_latest_version() is empty. .env.example: MULTICA_IMAGE_TAG=latest.
```

*Classification: fact*

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

Scanner prompt V2.4 · Operator Guide 2026-05-01 · Validator with XSS checks + verdict-severity coherence · [stop-git-std](https://github.com/stefans71/stop-git-std)

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-05-02 · scanned main @ `3df95c84b8af6f26b6d4fe8ccfcaca74ee977cf1` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
