# Security Investigation: coleam00/Archon

**Investigated:** 2026-04-20 | **Applies to:** main @ `3dedc22537f7b06d2011193f3f4ff4a36a353dfe` · v0.3.6 | **Repo age:** 1 year | **Stars:** 18,300 | **License:** MIT

> An 18,000-star remote agentic coding platform with a serious SECURITY.md discipline, pinned-and-checksummed distribution, and three open security issues that its maintainer is actively fixing in public.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-Archon.md` (+ `.html` companion) |
| Repo | [github.com/coleam00/Archon](https://github.com/coleam00/Archon) |
| Short description | Remote agentic coding platform — a harness that lets you drive Claude Code and Codex through Slack, Telegram, GitHub, or a web UI, with its own DAG workflow engine. Ships as a Bun-compiled CLI binary plus a server + web UI. |
| Category | `AI/LLM tooling` |
| Subcategory | `Remote agent orchestrator / workflow engine` |
| Language | TypeScript |
| License | MIT |
| Target user | Developers who want to run Claude Code or Codex remotely from Slack/Telegram/GitHub/web |
| Verdict | **Critical** (split — see below) |
| Scanned revision | `main @ 3dedc22` (release tag `v0.3.6`) |
| Commit pinned | `3dedc22537f7b06d2011193f3f4ff4a36a353dfe` |
| Scanner version | `V2.5-preview-step-g` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan; rename this file on re-run with date suffix. |

---

## Verdict: Critical (split — Deployment axis only)

### Deployment · Deployment · Installing today · v0.3.6 · default profile — **Critical — Install pinned to a tagged release, and know the trust chain terminates at the maintainer's credentials**

Install scripts sha256-verify the binary against checksums.txt — but both come from the same GitHub Releases URL. No branch protection on dev, no rulesets, no CODEOWNERS (F0 Critical). A single compromised maintainer credential ships code to every install on the next release with no gate. If you install anyway, pin to a specific tag and subscribe to releases.

### Deployment · Deployment · Shared host / multi-tenant · using Codex provider — **Critical — Do not run in production until PR #1250 merges**

Two Critical surfaces stack: F0 (no governance gate upstream) plus F1 (Codex vendor binary resolver has no hash/signature pinning — local attacker with write access to ~/.archon/vendor/codex/ gets arbitrary-code execution under your user via #1245). Also watch PR #1153 (axios CVE).

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Open security issues filed by an external researcher — actively being fixed (3 findings)</strong>
<br><em>Codex LPE + web-dist attestation gap + axios CVE override — none merged yet, all tracked publicly</em></summary>

1. **Vulnerability · F1** — Codex vendor binary resolver lacks hash/signature pinning (#1245). Local attacker with write access to ~/.archon/vendor/codex/ gets arbitrary code execution as invoking user. Fix in PR #1250.
2. **Supply chain · F2** — `archon serve` downloads web-dist tarball AND its sha256 checksums from the same GitHub Releases URL (#1246). Release-manager token compromise defeats the verification. Reporter asks for sigstore / independent attestation.
3. **Dependency · F3** — Axios CVE-2025-62718 (NO_PROXY bypass / SSRF) override pending in PR #1153. Open since 2026-04-13 — 3 days before scan. Reaches via @slack/bolt and @slack/web-api.

</details>

<details>
<summary><strong>⚠ Governance gaps — low formal review rate, no branch protection (4 findings)</strong>
<br><em>8% formal review, no branch protection on `dev`, no CODEOWNERS, CI bot commits direct to dev</em></summary>

1. **Review rate · F4** — 13 of 160 merged PRs have formal reviewDecision set (8%). Any-review rate is 58% (93/160) — owner+lead pair exists in practice but formal gates are absent.
2. **Branch protection · F4** — No branch protection rule on `dev` (the default branch) or `main`. Direct pushes possible, no required status checks at the branch level.
3. **CODEOWNERS · F4** — No CODEOWNERS file anywhere in the repo. No path-scoped review gate either.
4. **CI-bot merge** — `release.yml` runs `update-homebrew.sh` then commits the updated Homebrew formula directly to `dev` using GITHUB_TOKEN. Low risk (tag-push only) but bypasses human review.

</details>

<details>
<summary><strong>✅ Strong positive signals — real disclosure, pinned distribution, established maintainers (4 findings)</strong>
<br><em>SECURITY.md with private reporting, sha256-verified installs, 7-year-old owner, active second maintainer</em></summary>

1. **Disclosure** — SECURITY.md at repo root with real private reporting policy (cole@dynamous.ai or GitHub private advisory). External reporter (shaun0927) used it.
2. **Distribution · F8** — Install scripts verify sha256 checksums by default (SKIP_CHECKSUM=false). Homebrew formula pins per-platform sha256. Docker via GHCR semver tags (no live-main).
3. **Maintainer** — coleam00 (Cole Medin): 7-year account, 6,641 followers, Dynamous company. Wirasm (Rasmus Widing) is de facto dev lead (791 commits vs coleam00's 343).
4. **Code quality · F7** — Recent PRs show active security work: #1169 blocks .env leaks into subprocesses; #1217 replaces SDK binary resolution with explicit allowlist. exec.ts uses execFile (not shell). Docker drops root via gosu.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — No |
| Is it safe out of the box? | ❌ **No** — No |
| Do they fix problems quickly? | ⚠ **Partly** — Partly |
| Do they tell you about problems? | ⚠ **Partly** — Partly |

---

## 01 · What should I do?

> 🚨 Hold if using Codex on shared hosts · ⚠ 1 consumer mitigation · 3 steps
>
> **Most urgent:** if you run Archon with the Codex provider on any machine another user can log into, wait for PR #1250 before trusting Codex runs (Step 1). For single-user laptops (Step 2) you're fine to install today via the pinned install script. Step 3 is the dependency patch to watch.

### Step 1: If you use the Codex provider on a shared host, hold off until #1250 merges (⚠)

**Non-technical:** Archon downloads a Codex CLI binary to ~/.archon/vendor/codex/ without checking its hash. On a multi-user machine, another user who can write to that folder can drop a rigged binary that runs as you. The fix is open as PR #1250. Single-user laptops are low risk.

```bash
ls -la ~/.archon/vendor/codex/ 2>/dev/null
gh pr view 1250 -R coleam00/Archon --json state,mergedAt
```

### Step 2: Install Archon on your own machine — the install script verifies checksums (✓)

**Non-technical:** Installing now is fine on a personal laptop. The install script sha256-verifies the binary before running it.

```bash
curl -fsSL https://archon.diy/install | bash
archon version
```

### Step 3: Ask maintainers to merge the axios CVE patch and enable branch protection (ℹ)

**Non-technical:** Merge PR #1153 (axios CVE fix), enable branch protection on dev, add dependabot.yml, add CODEOWNERS.

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 4 Warning · ℹ 2 Info · ✓ 2 OK
>
> 9 findings total.
### F0 — Critical · Structural — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a repo that ships executable code to every install (C20)

*Continuous · Since repo creation · → Maintainer-side: enable branch protection on `dev`, add CODEOWNERS covering `packages/providers/` + `.github/workflows/` + install scripts. User-side: pin installs to a tagged release, verify the binary against source if your threat model justifies it, subscribe to releases.*

**What we observed.** The `dev` branch (default) has no classic branch protection (API returns 404, authoritative); zero rulesets; no CODEOWNERS file in any standard location; owner is a User account so no org-level rulesets apply.

**What this means for you.** When you install Archon, you are trusting the maintainer's account security as tightly as you'd trust your own laptop's password. There is no automated gate that would catch 'maintainer pushed a bad change' before it reaches your next install. On an 18k-star repo that ships Bun-compiled binaries plus a server, the blast radius of a single credential compromise is every current and future user.

**What this does NOT mean.** It does not mean the maintainer is careless — the practical owner+lead review pattern is strong (see F4). It means the gate is social rather than technical. A credential-compromise PR would bypass the social gate.

| Meta | Value |
|------|-------|
| Classic branch protection | ❌ 404 on `dev` and `main` |
| Rulesets | ❌ `[]` — zero rulesets |
| CODEOWNERS | ❌ Absent (4 locations checked) |
| Stars (blast radius) | 18,300 |
| Releases in last 30 days | ⚠ 8 |
| Active executable surface | CLI binaries + server + web UI |

**How to fix.** GitHub *Settings → Branches → Add branch protection rule*. For `dev`: require pull request reviews (1 approver minimum), require status checks (existing Test Suite workflow), require branches up-to-date before merging, do not allow bypassing. Add `.github/CODEOWNERS` with at minimum: `packages/providers/ @coleam00`, `.github/workflows/ @coleam00`, `scripts/install* @coleam00`.

### F1 — Warning · Vulnerability — Codex vendor binary resolver has no hash/signature pinning — local privilege escalation on shared hosts (#1245)

*Live · Filed 2026-04-16 (scan day) · → Don't run Codex workflows on shared hosts until PR #1250 merges. Single-user laptops: low risk.*

**What we observed.** `packages/providers/src/codex/binary-resolver.ts` resolves the Codex CLI from three sources (env var, config, `~/.archon/vendor/codex/` filesystem drop) and hands the path to `codexPathOverride`. Only gate is `fileExists()` — no sha256, no signature, no directory permission check.

**What this means for you.** On a shared host where another user can write to `~/.archon/vendor/codex/`, they drop an executable named the same as the Codex CLI. Your next Codex workflow runs it with your environment, your creds, your file access. This is LPE via binary swap, not a remote-unauth attack.

**What this does NOT mean.** It does not affect single-user laptops where only you have write access to `~/` — that's the 99% case. PR #1250 adds sha256 pinning on first use.

| Meta | Value |
|------|-------|
| Reported by | shaun0927 — [issue #1245](https://github.com/coleam00/Archon/issues/1245) |
| Fix proposed | [PR #1250](https://github.com/coleam00/Archon/pull/1250) (open 2026-04-16) |
| Attack surface | ⚠ Shared hosts only |
| Privilege gained | ❌ Invoking user, full |
| Disclosure channel | ✅ Public issue (SECURITY.md compliant) |

**How to fix.** Wait for PR #1250 (pins sha256 of Codex binary on first use, refuses to load on mismatch). Until then, if Archon is installed on a shared host, rename any existing `~/.archon/vendor/codex/codex` to disable it.

### F2 — Warning · Supply chain — `archon serve` web-dist integrity reduces to trusting one GitHub Releases URL (#1246)

*Live · Filed 2026-04-16 · → If you deploy Archon behind a Caddy reverse proxy in production, pin to a specific version tag and mirror the web-dist artifact yourself.*

**What we observed.** In `packages/cli/src/commands/serve.ts` lines 82-83, `archon serve` downloads both the web UI tarball and its sha256 checksums from the same `github.com/.../releases/download/vX.Y.Z/` URL.

**What this means for you.** The sha256 check protects against corrupt downloads but not against a compromised release: if a release-manager token or self-hosted runner were compromised, the attacker could rewrite tarball and checksums simultaneously. Reporter asks for independent attestation (Sigstore / separate signing key).

**What this does NOT mean.** It's not an exploitable bug today — it's a supply-chain hardening request. The integrity chain works against corruption and against most common attacks; it collapses under release-manager-token compromise.

| Meta | Value |
|------|-------|
| Filed by | shaun0927 — [issue #1246](https://github.com/coleam00/Archon/issues/1246) |
| Fix | ⚠ None merged yet |
| Who's affected | Anyone running `archon serve` in production |
| Maintainer response | ✅ Issue accepted, labelled `security` |

**How to fix.** Track issue #1246 for the structural fix (Sigstore / separate signing key / provenance assertion during publish). Until then, mirror the web-dist artifact yourself out-of-band and verify against a known-good hash independent of GitHub Releases.

### F3 — Warning · CVE — Axios CVE-2025-62718 (NO_PROXY bypass / SSRF) override patch pending (PR #1153)

*Live · PR open 2026-04-13 (3 days at scan) · → If you expose any Archon surface that makes outbound HTTP and honors NO_PROXY, watch PR #1153 until merged.*

**What we observed.** Axios 1.14.x has CVE-2025-62718 (hostname normalization bypass of NO_PROXY). Archon pulls axios transitively via @slack/bolt → @slack/web-api. PR #1153 adds an axios ^1.15.0 override; open 3 days at scan time.

**What this means for you.** If you expose an Archon surface that makes outbound HTTP and honors NO_PROXY, a crafted URL can still egress to the proxy you thought would be bypassed. Practical impact is scenario-specific.

**What this does NOT mean.** Doesn't mean Archon is currently exploiting the bug — it means the fix is ready and just needs to be merged. A dependabot config would have auto-opened this when the CVE was published.

| Meta | Value |
|------|-------|
| CVE | [CVE-2025-62718](https://nvd.nist.gov/vuln/detail/CVE-2025-62718) |
| Transit path | `@slack/bolt` → `@slack/web-api` → axios |
| Fix PR | [#1153](https://github.com/coleam00/Archon/pull/1153) — filed 2026-04-13 |
| Closes | [#1053](https://github.com/coleam00/Archon/issues/1053) |

**How to fix.** Merge PR #1153 (1-line package.json override: `"axios": "^1.15.0"`). Both Slack packages already accept `>=1.15.0` in their semver ranges, so nothing else has to change. Add `.github/dependabot.yml` (see F5) so future transitive CVEs get auto-opened.

### F4 — Warning · Structural — 8% formal review rate, no branch protection, no CODEOWNERS — governance gap (F11 + F14)

*Continuous · Since repo creation · → Practical reviewer density is higher than it looks (Wirasm is an active second pair of eyes), but the formal gates are all missing.*

**What we observed.** 13/160 formal reviewDecision set = 8% formal. 93/160 any-review = 58%. No branch protection on dev or main. No CODEOWNERS in any standard location. Wirasm (791 commits) is the active dev lead; coleam00 (343 commits) owns.

**What this means for you.** Practically, the review density is much higher than caveman — there's a real second pair of eyes (Wirasm leads; coleam00 owns). But the formal gate is missing. If a credential-compromise PR came through Wirasm's account, the pattern looks identical to a legitimate Wirasm-self-merge.

**What this does NOT mean.** Doesn't mean review is superficial — the recent security PRs (#1169, #1217) are carefully authored. It means the institutional structure doesn't encode the review pattern that's happening in practice.

| Meta | Value |
|------|-------|
| Merged PRs (last 300) | 160 |
| Formal review rate | ❌ 8% (13/160) |
| Any-review rate | ⚠ 58% (93/160) |
| Branch protection | ❌ None (dev, main) |
| CODEOWNERS | ❌ None anywhere |
| Practical reviewer | ✅ Wirasm (lead, 791 commits) + coleam00 (owner, 343 commits) |

**How to fix.** Same maintainer-side fix as F0: enable branch protection on `dev` with 1-approver requirement + add CODEOWNERS. The practical owner+lead review pattern (Wirasm lead, coleam00 owner) would then be encoded in GitHub settings rather than being implicit.

### F5 — Info · Hygiene gap — No `.github/dependabot.yml` — transitive-CVE PRs aren't opened automatically

*Current · Process-level · → Add `.github/dependabot.yml` with weekly schedule on `npm` + `pip` ecosystems. Would have auto-opened PR #1153 when CVE-2025-62718 was published.*

**What we observed.** No `.github/dependabot.yml` or `renovate.json` in the repo. Dependabot alerts API returns 403 (token lacks admin scope — ambiguous; could mean disabled or unauthorised).

**What this means for you.** Transitive CVEs are not auto-surfaced. PR #1153 (axios CVE) is the proof: filed manually by an external contributor, sat 3 days before any action. A bot would have opened it when the CVE published.

**What this does NOT mean.** Doesn't mean the maintainers don't care — they clearly watch CVEs manually. It means they don't have a consistent automation floor.

| Meta | Value |
|------|-------|
| `.github/dependabot.yml` | ❌ Absent |
| Dependabot API alerts | ⚠ 403 (token lacks admin scope — ambiguous) |
| Practical impact | ℹ PR #1153 sat 3 days before human-opened |
| Effort to fix | ✅ 15-line YAML file |

**How to fix.** Create `.github/dependabot.yml` at repo root with npm + pip ecosystem entries on weekly schedule. The maintainers clearly watch CVEs manually (PR #1153 proves this) but a bot does it consistently and closes the CVE-to-PR lag.

### F6 — Info · Design property — Archon executes AI-generated bash via `executeBashNode` — known attack surface, disclosed feature

*Ongoing · By design · → Every workflow YAML you author or accept from a third party is effectively a shell script. Read untrusted workflows before running them.*

**What we observed.** Archon's DAG engine supports bash script nodes (`executeBashNode` at `packages/workflows/src/dag-executor.ts`). Own command-exec wrapper uses `execFile` (not shell).

**What this means for you.** Every workflow YAML you author or accept from a third party is effectively a shell script. Read untrusted workflows before running them.

**What this does NOT mean.** Doesn't mean Archon is poorly designed — it's a core feature of an agentic platform. The trust model is explicit: AI-generated commands run with invoking-user privileges. Sandbox if executing untrusted.

| Meta | Value |
|------|-------|
| Function | `executeBashNode` in DAG workflow engine (`packages/workflows/src/dag-executor.ts`) |
| Trust model | AI output runs with invoking user's privileges |
| Mitigation (operator side) | Sandbox (container / VM / non-privileged user) for untrusted workflows |
| Known, documented | ✅ Not hidden — core feature |

**How to fix.** This is an inherent property of agentic coding platforms, not a bug to fix. The project's disclosure posture (SECURITY.md + public issue triage) handles it appropriately. Users should run Archon in a sandbox (container, VM, or non-privileged user) if executing untrusted AI-generated workflows.

### F7 — OK · Positive — Active security work pattern — recent PRs (#1169, #1217) show real engineering care

*Ongoing · 2025-2026 · → No action needed. Positive signal: the team treats security PRs as first-class and merges them.*

**What we observed.** PR #1169 prevents target-repo .env leaks into subprocesses (merged). PR #1217 replaces Claude SDK embed with explicit binary-path resolver (merged). exec.ts uses execFile, Docker entrypoint drops root to appuser via gosu.

**What this means for you.** The team treats security PRs as first-class. Recent security refactors include positive and negative CI smoke tests and regression tests. This is a good-signal pattern.

| Meta | Value |
|------|-------|
| [PR #1169](https://github.com/coleam00/Archon/pull/1169) | ✅ merged — prevents target-repo .env leak into subprocesses (closes #1135) |
| [PR #1217](https://github.com/coleam00/Archon/pull/1217) | ✅ merged — replaces Claude SDK embed with explicit binary-path resolver |
| Shell exec wrapper | ✅ `execFile` in `packages/git/src/exec.ts` (not shell — avoids interpolation injection) |
| Docker privilege drop | ✅ root → appuser via `gosu` |

### F8 — OK · Positive — Pinned-and-checksummed distribution — opposite of curl-pipe-from-main

*Current · Ongoing · → No action needed. Positive signal: install path does real verification by default.*

**What we observed.** Install scripts download from tagged GitHub releases and sha256-verify against checksums.txt from the same release; SKIP_CHECKSUM=false default. Homebrew formula pins per-platform sha256. Docker images published to GHCR with semver tags.

**What this means for you.** The install path does real verification by default. `archon.diy/install` redirects to the exact same repo-hosted script (byte-identical).

**What this does NOT mean.** Doesn't mean artifact integrity is perfect — the F2 issue names the residual gap (tarball + checksums from same URL). The install-path is strong; the end-artifact reproducibility is not independently established.

| Meta | Value |
|------|-------|
| Install scripts | ✅ sha256-verify binary against `checksums.txt` from same release (SKIP_CHECKSUM=false default) |
| Homebrew formula | ✅ Pins each platform binary to version + sha256 |
| Docker | ⚠ `:latest` rolling tag available — prefer explicit semver tag |
| `archon.diy/install` | ✅ byte-identical to `scripts/install.sh` — not a separate endpoint |
| Contrast | caveman: curl-pipe from live main, no checksum. Archon: opposite. |

---

## 02A · Executable file inventory

> ⚠ 2 Warning · ℹ 2 Info · ✓ 4 OK — 8 executable surfaces cataloged (7 scripts + 1 Tier-1 auto-loaded rule file). 2 need attention: the Codex binary resolver (F1 target) and the release.yml homebrew-update job that commits to dev without a review gate.

### Layer 1 — one-line summary

- **8 executable surfaces inventoried.** The 2 Warning items are maintainer-side: merge PR #1250 (Codex binary pinning) and optionally gate the Homebrew auto-commit path in release.yml. The 4 OK items (install.sh, install.ps1, Dockerfile, docker-entrypoint.sh) are clean and sha256-verified where applicable. CLAUDE.md is a Tier-1 auto-loaded agent rule file — content benign today, leverage is every contributor session.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `packages/providers/src/codex/binary-resolver.ts` | Vendor binary resolver | Node/Bun | fileExists() — no sha256 or signature check on resolved binary path | None directly | Warning: resolves Codex CLI from env/config/~/.archon/vendor/codex/ and passes to SDK codexPathOverride without hash pinning. Fix open in PR #1250. |
| `.github/workflows/release.yml` | CI release workflow | GitHub Actions | git push via GITHUB_TOKEN direct to dev on tag-push | GitHub Releases fetch + git push to origin/dev | Warning: update-homebrew job commits homebrew/archon.rb directly to dev without review gate. Low risk in isolation; compound risk with F0 (no branch protection). |
| `scripts/install.sh` | Install script | shell | None — set -euo pipefail, sha256sum verification | HTTPS to github.com / objects.githubusercontent.com only | OK — downloads versioned binary from tagged release, sha256-verifies before install. SKIP_CHECKSUM defaults to false. |
| `scripts/install.ps1` | Install script (Windows) | PowerShell | None — Set-StrictMode -Version Latest, same sha256 verification logic | HTTPS to github.com only | OK — PS1 parity with install.sh. F16 Windows surface covered. |
| `Dockerfile` | Container definition | Docker | None — multi-stage, gosu privilege drop | None at runtime (build-time only) | OK — multi-stage build, drops root to appuser via gosu, no untrusted tarball fetches. |
| `docker-entrypoint.sh` | Container entrypoint | shell | None — exec $RUNNER bun run start | None | OK — fixes volume perms, configures GH_TOKEN via credential helper (not ~/.gitconfig), execs as appuser. |
| `CLAUDE.md` | Agent rule file (Tier 1 auto-loaded) | Claude Code agent context | None — static markdown, development conventions only | None | Info — auto-loaded for every contributor session in this repo. 813 lines of TypeScript/Zod/Bun contributor conventions. Imperative-verb grep found no prompt injection patterns. Leverage: 1:every contributor. Content benign today. |
| `scripts/build-binaries.sh` | Build pipeline script | shell | None — EXIT trap pattern for safe rollback | None | Info — CI-only build pipeline. Uses bash EXIT trap to restore bundled-build.ts after bun build --compile. Not end-user facing. |

**Note on CLAUDE.md auto-load leverage.** A future PR swapping the benign development-convention content for attacker instructions would take effect on every contributor's next Claude Code session. Combined with the governance gaps in F0/F4 (no branch protection on dev, no CODEOWNERS, 8% formal review rate), a PR modifying CLAUDE.md could land without a gate. Current content is benign; the structural risk is the leverage ratio.

---

## 03 · Suspicious code changes

> **6 security-adjacent PRs reviewed.** All 6 touch security-critical files (providers, installer, CI workflows). None had a formal `reviewDecision`. All were merged by Wirasm (the lead contributor), so practical review happened without the `reviewDecision` field being set.

Sample: the 5 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 8% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1250](https://github.com/coleam00/Archon/pull/1250) | Pin Codex vendor binary sha256 on first use (fixes #1245 LPE) | shaun0927 (EXTERNAL REPORTER) | — (open) | No formal decision | Security fix for #1245 LPE, filed 2026-04-16. Still open at scan time. |
| [#1217](https://github.com/coleam00/Archon/pull/1217) | Replace Claude SDK embed with explicit binary-path resolver | Wirasm (LEAD) | Wirasm | No formal decision | Self-submitted-and-merged; content good (CI smoke + regression tests). |
| [#1169](https://github.com/coleam00/Archon/pull/1169) | Prevent target repo .env from leaking into subprocesses (#1135) | Wirasm (LEAD) | Wirasm | No formal decision | Self-merged security fix; content is good. |
| [#1153](https://github.com/coleam00/Archon/pull/1153) | Override axios to ^1.15.0 for CVE-2025-62718 | external_contributor (EXTERNAL) | — (open) | No formal decision | Dep CVE fix sitting open 3 days; no dependabot auto-open. |
| [#1137](https://github.com/coleam00/Archon/pull/1137) | Extract providers from @archon/core into @archon/providers | Wirasm (LEAD) | Wirasm | No formal decision | Large refactor touching Dockerfile + binary paths, self-merged. |

---

## 04 · Timeline

> ✓ 3 good · 🟡 3 neutral · 🔴 2 concerning
>
> 7 events from repo creation to scan day. **Peak concern 2026-04-13 → 2026-04-16** (axios CVE open 3 days, Codex LPE filed the scan day). The team shipped real security hardening in #1169 + #1217 during the same window, so the signal is actively-working not stuck.

- 🟡 **2025-02-07 · START** — Repo created by coleam00 (Cole Medin at Dynamous). Initial architecture: Bun + TypeScript monorepo with workspace packages.
- 🟢 **2026-03-15 · SECURITY.md** — Repo adds SECURITY.md at root with real private disclosure policy (email + GHSA). The difference between no-advisory culture and real vulnerability management.
- 🟢 **2026-04-04 · ENV LEAK FIXED** — PR #1169 merges — prevents target-repo .env files from leaking into Archon-spawned subprocesses. Real security refactor. Closes #1135.
- 🟡 **2026-04-08 · RELEASES** — Rapid release cadence: v0.3.0 → v0.3.6 in 4 days. All tagged. Homebrew formula auto-updated. Docker images published with semver tags.
- 🟢 **2026-04-12 · RESOLVER HARDENED** — PR #1217 merges — explicit CLAUDE_BIN_PATH allowlist replaces SDK auto-resolution. Includes positive + negative CI smoke tests.
- 🔴 **2026-04-13 · AXIOS CVE** — External contributor files PR #1153 for CVE-2025-62718. Still open at scan time — 3 days with no merge. No dependabot config.
- 🔴 **2026-04-16 · CODEX LPE** — Reporter shaun0927 files #1245 (Codex vendor binary LPE) and #1246 (web-dist attestation). PR #1250 proposed same day. Both open at scan time.
- 🟡 **2026-04-16 · SCAN** — This scan runs — same day as the security issue filings. Snapshot will diverge fast; expect open items to close within days.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 14 months | Created 2025-02-07, scanned 2026-04-16 |
| Stars | 18,300 | Very high visibility — scrutiny should match scale |
| Owner account age | ✅ 7 years | coleam00 created 2019-02-03, 51 public repos, 6,641 followers, Dynamous company |
| Lead contributor | ✅ Wirasm (791 commits) | More than owner's 343 — a second active maintainer |
| Merged PRs (review rate) | ⚠ 13 formal / 93 any / 160 total | 8% formal, 58% any-review |
| Branch protection | ❌ None (dev, main) | API returns 404 on both — definitive |
| CODEOWNERS | ❌ None | No file in any standard location |
| SECURITY.md | ✅ Yes (root) | Real private disclosure policy — cole@dynamous.ai or GitHub private advisory |
| Security advisories | ⚠ 0 published | 3 open issues being tracked publicly |
| OSSF Scorecard | ⚠ Not indexed | API returned 404 — repo not yet indexed by securityscorecards.dev |
| Dependabot | ⚠ Unknown (403 without admin) | No .github/dependabot.yml config either way |
| Runtime dependencies (root) | ✅ 1 (claude-agent-sdk) | Transitive surface via Slack SDK, React, Vite |
| CI workflows | 4 (test, publish, release, deploy-docs) | Real matrix test (ubuntu + windows), Docker smoke test |
| Releases | 10+ (v0.2.13 → v0.3.6) | Rapid iteration, checksums.txt + multi-platform binaries + Docker published per release |
| Total PR count | ~461 closed, 20 open | Active community |

---

## 06 · Investigation coverage

> **160/300 PRs sampled, 7/7 execs inspected, 3 gaps noted.** Only 160 of ~461 closed PRs reviewed (300-PR API-limit window; older PRs not inspected). All executable files inspected. Windows PS1 surface covered. Monorepo has 11 inner packages — only root + root-lock inspected as the primary surface.

| Check | Result |
|-------|--------|
| Tarball extraction | ✅ OK — 769 files — pinned to `3dedc22` at scan start |
| Workflow files read | ✅ 4 of 4 — deploy-docs, publish, release, test |
| Merged PRs reviewed | ⚠ 160 of ~461 (sampled) — under the 300-window cap |
| Suspicious PR diffs read | 6 of the 300-keyword hits — the flagged 6 in §03 read in full |
| Dependency scan | ⚠ Metadata only — Dependabot API 403 (admin scope); full lockfile audit not performed |
| Executable files inspected | ⚠ 7 of 7 (2 Warning, 4 OK, 1 Info) |
| `pull_request_target` scan | ✅ Verified — 0 occurrences across 4 workflows |
| README paste-scan | ✅ 0 paste-blocks |
| Agent-rule files | ✅ 1 found — CLAUDE.md at root (Tier 1 auto-loaded). Not CI-amplified. |
| Prompt-injection scan | ✅ 0 matches / 0 actionable |
| Distribution channels verified | ⚠ Install path verified, installed artifact NOT verified — trust chain terminates at GitHub Releases (see F2 issue #1246) |
| Windows surface coverage | ✅ install.ps1 inspected; CI test matrix covers windows-latest |
| OSSF Scorecard | ⚠ Not indexed (API 404) |
| osv.dev | ℹ Not queried — transitive surface covered by CVE watch (F3) |
| Secrets-in-history | ⚠ Not scanned (gitleaks not available) |
| API rate budget | ✅ 5000/5000 remaining |
| Tarball SHA | `3dedc22` — if your tree differs, re-run the scan |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| Dependabot alerts | ⚠ 403 — token lacks admin scope; alert state unknown. No .github/dependabot.yml config file found. |
| Monorepo coverage | 11 inner packages (11 sampled: packages/cli, packages/core, packages/providers, packages/workflows, packages/git, packages/paths, packages/web, packages/slack, packages/telegram, packages/github, packages/config) · lifecycle hits: 0 |
| `pull_request_target` usage | 0 found across 4 workflows · Zero `pull_request_target` usage across 4 workflows — rules out that class of attack |

**Gaps noted:**

1. Older PRs (pre-2026-03) not inspected — sampling window stops at 300 PRs deep; ~300 older PRs remain un-reviewed.
2. Dependabot alerts API requires admin:repo_hook scope; scan token lacks it so alert state beyond 'no config file' is unknown.
3. Monorepo has 11 inner packages with their own package.json — per-package dep surface not enumerated. Root + root-lock inspected as primary surface.

---

## 07 · Evidence appendix

> ℹ 11 facts · ★ 3 priority

6 command-backed claims. **Skip ahead to items marked ★ START HERE** — the Codex LPE issue body, the install-script byte-match against archon.diy, and the review-rate dual metric. Those three are the falsification criteria for the split verdict.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — Codex vendor binary resolver has no sha256 pinning (F1 / issue #1245)

```bash
gh issue view 1245 -R coleam00/Archon --json title,body -q '.title'
```

Result:
```None
security(providers): codex vendor binary resolver lacks hash/signature pinning — LPE via writable vendor dir
```

*Classification: Confirmed fact — issue title + body describe the three-source resolver (env var CODEX_BIN_PATH, config, filesystem drop under ~/.archon/vendor/codex/) and the attack pre-condition (writable vendor dir). Fix open in PR #1250.*

#### ★ Evidence 2 — archon.diy/install serves the same content as scripts/install.sh (byte-identical)

```bash
curl -fsSL https://archon.diy/install | head -5
head -5 /tmp/repo-scan-coleam00-Archon/scripts/install.sh
```

Result:
```None
#!/usr/bin/env bash
# scripts/install.sh
# Install Archon CLI from GitHub releases
```

*Classification: Confirmed fact — both sources return byte-identical output. archon.diy is a CDN/redirect for the repo's install script, not a separately-controlled distribution endpoint.*

#### ★ Evidence 3 — Dual review-rate metric (F4): 8% formal, 58% any-review over last 160 merged PRs

```bash
gh pr list -R coleam00/Archon --state merged --limit 300 --json reviewDecision,reviews | jq '{ total: length, formal_review: [.[] | select(.reviewDecision != null and .reviewDecision != "")] | length, any_review: [.[] | select(.reviews != null and (.reviews | length) > 0)] | length }'
```

Result:
```json
{ "total": 160, "formal_review": 13, "any_review": 93 }
```

*Classification: Confirmed fact — 13/160 formal decisions = 8%; 93/160 any-review = 58%. Gap reflects practical-vs-formal reviewer pattern.*

### Other evidence

#### Evidence 4 — Axios CVE-2025-62718 override patch PR #1153 open 3 days at scan time

```bash
gh pr view 1153 -R coleam00/Archon --json title,state,createdAt
```

Result:
```json
{"createdAt":"2026-04-13T01:31:22Z","state":"OPEN","title":"fix: override axios to ^1.15.0 for CVE-2025-62718"}
```

*Classification: Confirmed fact — PR #1153 open since 2026-04-13, scan date 2026-04-16. Targets CVE via @slack/bolt → @slack/web-api → axios transit.*

#### Evidence 5 — No branch protection on `dev` or `main` — 404 authoritative on both

```bash
gh api "repos/coleam00/Archon/branches/dev/protection"
gh api "repos/coleam00/Archon/branches/main/protection"
```

Result:
```None
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

*Classification: Confirmed fact — 404 authoritative (token has repo scope; permissions issue would return 403). No rule configured on either branch.*

#### Evidence 6 — No .github/dependabot.yml; Dependabot alerts API returns 403 (token lacks admin scope)

```bash
find /tmp/repo-scan-coleam00-Archon -name "dependabot.yml" -o -name "dependabot.yaml" -o -name "renovate.json"
gh api "repos/coleam00/Archon/dependabot/alerts"
```

Result:
```None
(find returns nothing)
{"message":"You are not authorized to perform this operation.","status":"403"}
```

*Classification: Inference — 403 alerts API is ambiguous without admin scope. Missing config file is definitive: no declarative dependency-tracking policy exists.*

#### Evidence 7 — SECURITY.md at root with real private disclosure channel

```bash
cat /tmp/repo-scan-coleam00-Archon/SECURITY.md | head -12
```

Result:
```markdown
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Archon, please report it responsibly.

**Do NOT open a public issue for security vulnerabilities.**

Instead, email **cole@dynamous.ai** or use [GitHub's private vulnerability reporting](https://github.com/coleam00/Archon/security/advisories/new).
```

*Classification: Confirmed fact — real private channel (email + GHSA link) at repo root.*

#### Evidence 8 — Maintainer is an established 7-year account with public company affiliation

```bash
gh api "users/coleam00" -q '{login,created_at,public_repos,followers,company}'
```

Result:
```json
{"company":"Dynamous","created_at":"2019-02-03T02:45:51Z","followers":6641,"login":"coleam00","public_repos":51}
```

*Classification: Confirmed fact — 7-year account, public Dynamous affiliation, 6,641 followers, 51 public repos. Not a sockpuppet.*

#### Evidence 9 — Install script verifies sha256 checksums by default (SKIP_CHECKSUM=false)

```bash
grep -nE 'SKIP_CHECKSUM|sha256sum|verify_checksum' /tmp/repo-scan-coleam00-Archon/scripts/install.sh | head -5
```

Result:
```bash
#   SKIP_CHECKSUM - Set to "true" to skip checksum verification (not recommended)
# SKIP_CHECKSUM opt-in only; defaults to false
SKIP_CHECKSUM="${SKIP_CHECKSUM:-false}"
```

*Classification: Confirmed fact — default install path does sha256 verification. Users must opt-in to skip.*

#### Evidence 10 — PR #1169 was a security fix merged without GHSA publication (Gate C audit outcome)

```bash
gh api repos/coleam00/Archon/pulls/1169 --jq '{title, merged, merged_at}'
```

Result:
```json
{"title":"security: prevent target repo .env from leaking into subprocesses (#1135)","merged":true,"merged_at":"2026-04-13T10:46:24Z"}
```

*Classification: Confirmed fact — PR #1169 merged 2026-04-13 with title prefix 'security:' and body describing undisclosed secret-leak vulnerability. No GHSA published. Per Gate C audit of the scorecard-calibration board review (docs/External-Board-Reviews/042026-sf1-calibration/), has_reported_fixed_vulns = TRUE for Archon.*

#### Evidence 11 — Archon's DAG engine supports bash script nodes via `executeBashNode`

```bash
grep -n 'executeBashNode' /tmp/repo-scan-coleam00-Archon/packages/workflows/src/dag-executor.ts
```

Result:
```None
1035:      case 'bash': return await executeBashNode(node, ctx);
```

*Classification: Confirmed fact — the DAG engine dispatches bash-type nodes to `executeBashNode`. This is the design property behind F6: workflow YAMLs are effectively shell scripts at execution time. Archon does not sandbox beyond OS user-level isolation.*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `3dedc22537f7b06d2011193f3f4ff4a36a353dfe` (v0.3.6) · scanner V2.5-preview-step-g*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
