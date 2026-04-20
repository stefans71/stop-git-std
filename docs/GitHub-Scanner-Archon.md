# Security Investigation: coleam00/Archon

**Investigated:** 2026-04-16 | **Applies to:** dev @ 3dedc22 · v0.3.6 | **Repo age:** 14 months | **Stars:** 18,300 | **License:** MIT

> An 18,000-star remote agentic coding platform with a serious SECURITY.md discipline, pinned-and-checksummed distribution, and three open security issues that its maintainer is actively fixing in public.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-Archon.md` (+ `.html` companion) |
| Repo | [github.com/coleam00/Archon](https://github.com/coleam00/Archon) |
| Short description | Remote agentic coding platform — a harness that lets you drive Claude Code and Codex through Slack, Telegram, GitHub, or a web UI, with its own DAG workflow engine. Ships as a Bun-compiled CLI binary plus a server + web UI. |
| Category | AI/LLM tooling |
| Subcategory | Remote agent orchestrator / workflow engine |
| Verdict | **Critical** (split — see below) |
| Scanned revision | `dev @ 3dedc22` (release tag `v0.3.6`) |
| Prompt version | `v2.3` (first Archon scan under V2.3 pipeline) |
| Prior scan | None — first run on this repo. Future re-runs should diff against `GitHub-Scanner-Archon-YYYY-MM-DD.md` snapshots. |

---

## Verdict: Critical (split) — governance gap applies to every audience

### Deployment · Installing today · v0.3.6 · default profile — **Install pinned to a tagged release, and know the trust chain terminates at the maintainer's credentials**

Install scripts sha256-verify the binary against `checksums.txt` — but both come from the same GitHub Releases URL. No branch protection on `dev`, no rulesets, no CODEOWNERS (F0 Critical). A single compromised maintainer credential ships code to every install on the next release with no gate. If you install anyway, pin to a specific tag (not `main`/`dev`) and subscribe to repo releases.

### Deployment · Shared host / multi-tenant · using Codex provider — **Do not run in production until PR #1250 merges**

Two Critical surfaces stack here: F0 (no governance gate upstream) plus F1 (Codex vendor binary resolver has no hash/signature pinning — local attacker with write access to `~/.archon/vendor/codex/` gets arbitrary-code execution under your user via [#1245](https://github.com/coleam00/Archon/issues/1245)). Also watch [PR #1153](https://github.com/coleam00/Archon/pull/1153) (axios CVE-2025-62718).

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Open security issues filed by an external researcher — actively being fixed (3 findings)</strong>
<br><em>Codex LPE + web-dist attestation gap + axios CVE override — none merged yet, all tracked publicly</em></summary>

1. **Vulnerability · F1** — Codex vendor binary resolver lacks hash/signature pinning ([#1245](https://github.com/coleam00/Archon/issues/1245)). On multi-user hosts, another user who can write to `~/.archon/vendor/codex/` gets arbitrary code execution as you on the next Codex workflow. Fix open in [PR #1250](https://github.com/coleam00/Archon/pull/1250).
2. **Supply chain · F2** — `archon serve` downloads web-dist tarball AND its sha256 checksums from the same GitHub Releases URL ([#1246](https://github.com/coleam00/Archon/issues/1246)). A release-manager token compromise defeats the verification. Reporter asks for independent attestation / sigstore.
3. **Dependency · CVE** — Axios CVE-2025-62718 (NO_PROXY bypass via hostname normalization) override pending in [PR #1153](https://github.com/coleam00/Archon/pull/1153), open since 2026-04-13 — 3 days before scan. Reaches via `@slack/bolt` and `@slack/web-api`.

</details>

<details>
<summary><strong>⚠ Governance gaps — low formal review rate, no branch protection (4 findings)</strong>
<br><em>8% formal review, no branch protection on <code>dev</code>, no CODEOWNERS, CI bot commits direct to dev</em></summary>

1. **Review rate · F11** — 13 of 160 merged PRs have formal `reviewDecision` set (8%). Any-review rate is 58% (93/160) — a second pair of eyes exists in practice (Wirasm leads dev, coleam00 is owner) but formal gates are absent.
2. **Branch protection · F14** — No branch protection rule on `dev` (the default branch) or `main`. Direct pushes possible, no required status checks at the branch level.
3. **CODEOWNERS · F14** — No CODEOWNERS file anywhere in the repo. No path-scoped review gate either — which combined with no branch protection means there is no automated requirement for a second reviewer on hooks, workflows, or install scripts.
4. **CI-bot merge** — `release.yml` runs `update-homebrew.sh` then commits the updated Homebrew formula directly to `dev` using `GITHUB_TOKEN`. Low risk (the bot only runs on tag-push) but it's a code-modification path that bypasses human review, so worth naming.

</details>

<details>
<summary><strong>✓ Strong positive signals — real disclosure, pinned distribution, established maintainers (4 findings)</strong>
<br><em>SECURITY.md with private reporting, sha256-verified installs, 7-year-old owner, active second maintainer</em></summary>

1. **Disclosure** — `SECURITY.md` at repo root with a real private reporting policy (`cole@dynamous.ai` or GitHub's private advisory). The external reporter (shaun0927, 5-year-old account, 54 followers) used it to file four well-scoped issues in public with evidence.
2. **Distribution · F1** — Install scripts verify sha256 checksums by default (`SKIP_CHECKSUM=false`). Homebrew formula pins to release tag + per-platform sha256. Docker images build via GHCR with semver tags (no live-main fetch). This is the opposite of the caveman curl-pipe-from-main pattern.
3. **Maintainer** — coleam00 (Cole Medin): 7-year GitHub account, 6,641 followers, Dynamous company listed. Wirasm (Rasmus Widing) is the de facto dev lead with 791 commits vs coleam00's 343 — owner-merges-contributor-work is healthier than solo-maintainer for review purposes.
4. **Code quality** — Recent PRs show active security work: [#1169](https://github.com/coleam00/Archon/pull/1169) blocks `.env` leaks into subprocesses, [#1217](https://github.com/coleam00/Archon/pull/1217) replaces SDK binary resolution with an explicit allowlist. `exec.ts` uses `execFile` (not shell), Docker entrypoint drops root to appuser via `gosu`.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | 🚨 **No upstream gate** — 8% formal / 58% any · no branch protection · no CODEOWNERS |
| Do they fix problems quickly? | ⚠ Open fixes, not merged yet |
| Do they tell you about problems? | ⚠ Partly — SECURITY.md with private channel but 0 published advisories (PR #1169 security fix shipped without GHSA) |
| Is it safe out of the box? | 🚨 **No** — Critical finding applies to default install path (F0 governance gap) |

---

## 01 · What should I do?

> ⚠ Action needed if you use Codex on shared hosts · 3 steps
>
> **Most urgent:** if you run Archon with the Codex provider on any machine another user can log into, wait for PR #1250 before trusting Codex runs (Step 1). For single-user laptops (Step 2) you're fine to install today via the pinned install script. Step 3 is the dependency patch to watch.

### Step 1: If you use the Codex provider on a shared host, hold off until #1250 merges (⚠)

**Non-technical:** Archon can drive either Claude Code or Codex. The Codex side downloads its binary to `~/.archon/vendor/codex/` and runs whatever's there without checking a hash or signature. On a multi-user machine, another user who has write access to that folder (the admin, a shared dev container, prior malware) can drop a rigged binary and it will run as you the next time you kick off a Codex workflow. The fix is open as PR #1250. Single-user laptops are a much lower risk because nobody else has write access to your home directory — that's the 99% case.

```bash
# Check if you have a Codex binary dropped that Archon would pick up
ls -la ~/.archon/vendor/codex/ 2>/dev/null

# If it exists AND your machine is shared, rename it so Archon refuses to load
mv ~/.archon/vendor/codex/codex ~/.archon/vendor/codex/codex.disabled

# Watch PR #1250 for merge
gh pr view 1250 -R coleam00/Archon --json state,mergedAt
```

### Step 2: If you're considering installing Archon for the first time on your own machine

**Non-technical:** Installing now is fine on a personal laptop. The install script verifies a sha256 checksum before running the binary (unlike the caveman pattern where you pipe live `main` into bash). The Codex LPE above only matters on shared hosts. If you only use the Claude Code provider, none of the open security issues affect you today.

```bash
# Recommended (verified install)
curl -fsSL https://archon.diy/install | bash

# After install, confirm version matches your expectation
archon version
```

### Step 3: Ask the maintainers to merge the axios CVE patch and enable branch protection

**Non-technical:** The maintainers are clearly doing careful work — the SECURITY.md disclosure process is real, recent PRs show security-minded refactors, and they run the private reports in public for accountability. Helpful asks:

1. Merge [PR #1153](https://github.com/coleam00/Archon/pull/1153) to get the axios CVE fix in.
2. Enable branch protection on `dev`.
3. Add a `.github/dependabot.yml` so transitive-CVE PRs get opened automatically.
4. Add CODEOWNERS so `packages/providers/` and `.github/workflows/` require a second reviewer.

These are normal for a repo at 18k stars.

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 4 Warning · ℹ 2 Info · ✓ 2 OK
>
> 9 findings total. **The Critical finding (F0) is structural:** no branch protection on `dev`, no rulesets, no CODEOWNERS — a single maintainer-credential compromise ships arbitrary code to every install on the next release. The Warnings cluster into **three open security issues being fixed in public** (Codex LPE, web-dist attestation, axios CVE) and **process gaps** (no dependabot.yml, self-merge pattern). Start with F0 (Critical) and F1 (Codex LPE) if time-pressed.
>
> **Your action:** F0 means your install path doesn't have a second-pair-of-eyes gate upstream. If you install anyway, pin to a specific release tag (not `main`/`dev`), verify the install artifact against source, and watch releases. Don't run Codex on shared hosts until PR #1250 merges (F1); watch PR #1153 for the axios patch (F3).

### F0 — Critical · Ongoing · no upstream gate — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a repo that ships executable code to every install (C20)
*Continuous · Since repo creation · → If you install Archon: pin to a specific release tag, not `main`/`dev`. Verify the binary against source if your threat model justifies it. Subscribe to repo releases so you notice unexpected tagged releases. If you maintain this repo: enable branch protection on `dev` and add CODEOWNERS covering `packages/providers/` + `.github/workflows/` + install scripts.*

**What's missing.** The `dev` branch (default) has no classic branch protection (API returns 404, authoritative); the repo has zero rulesets (newer-API `/rulesets` returns `[]`); no ruleset applies to `dev` or `main`; and there is no CODEOWNERS file in any standard location (4 checked via API + local tarball). This means: any push that lands on the maintainer's credentials goes directly to `dev` without a review gate, a required status check, or a path-scoped reviewer.

**How an attacker arrives (F13).** This does NOT require xz-utils-level sophistication. Concrete paths: (1) credential phishing against coleam00 or Wirasm (both public profiles, findable targets); (2) stale OAuth token reuse from a developer machine or old CI system; (3) compromised browser session cookie (malicious browser extension in the maintainer's session); (4) malicious IDE/editor extension running as the maintainer; (5) sloppy review of an attacker-submitted PR — 5 of 6 flagged security-adjacent PRs in this scan were Wirasm-self-submitted-and-merged, a pattern that wouldn't distinguish a real contributor PR from a credential-compromise PR; (6) compromised self-hosted runner on a release pipeline.

**What this means for you (non-technical).** When you install Archon, you are trusting the maintainer's account security as tightly as you'd trust your own laptop's password. There is no automated gate that would catch "maintainer pushed a bad change" before it reaches your next install. On an 18k-star repo that ships Bun-compiled binaries plus a server that runs on user machines, the blast radius of a single credential compromise is every current and future user.

**OSSF Scorecard note.** The repo is not yet indexed by securityscorecards.dev (API returned 404), so no independent governance score is available. If it were scored, the missing branch protection, missing CODEOWNERS, and low formal review rate would likely drag the Branch-Protection and Code-Review checks to 0-2/10 — reinforcing this finding.

**Why Critical, not Warning.** C20 escalates to Critical when the repo ships executable code to user machines AND has active code flow (≥1 release in the last 30 days). Archon meets both: CLI binaries distributed via Homebrew / `archon.diy/install` / GHCR; 8 releases in the last 30 days (v0.3.0 → v0.3.6). Combined with F2 (release-artifact integrity relies on a single GitHub Releases URL), the installed-artifact trust chain has no independent second root.

| Meta | Value |
|------|-------|
| Classic branch protection | ❌ 404 on `dev` and `main` |
| Rulesets | ❌ `[]` — zero rulesets |
| CODEOWNERS | ❌ Absent (4 locations checked) |
| Stars (blast radius) | 18,300 |
| Releases in last 30 days | ⚠ 8 |
| Active executable surface | CLI binaries + server + web UI |

**How to fix (maintainer-side).** GitHub *Settings → Branches → Add branch protection rule*. For `dev`: require pull request reviews (1 approver minimum), require status checks (the existing `Test Suite` workflow), require branches to be up to date before merging, do not allow bypassing. Also add a `.github/CODEOWNERS` file with at minimum: `packages/providers/ @coleam00`, `.github/workflows/ @coleam00`, `scripts/install* @coleam00`. This closes the single-point-of-failure without slowing dev velocity (only security-critical paths require gated review).

### F1 — Warning · Open · fix in review — Codex vendor binary resolver has no hash pinning (#1245)
*Filed 2026-04-16 · Live now · → Don't run Codex workflows on shared hosts until PR #1250 merges. Single-user laptops: low risk.*

`packages/providers/src/codex/binary-resolver.ts` resolves the Codex CLI binary from three sources — env var, config, and a dropped file under `~/.archon/vendor/codex/` — and hands it straight to the SDK's `codexPathOverride`. The only gate is `fileExists()`. No sha256, no signature, no permission check on the directory.

**How an attacker arrives (F13):** this only reaches you if another local user (or a process running as another user) can write to your `~/.archon/vendor/codex/` — which in practice means shared workstations, dev containers sharing a volume, CI images, or a Docker setup with an exposed vendor mount. Single-user laptops are low risk because nobody else has write access to your home directory. The fix open in [PR #1250](https://github.com/coleam00/Archon/pull/1250) pins the sha256 of the binary on first use and refuses to load if it changes.

| Meta | Value |
|------|-------|
| Reported by | shaun0927 — [issue #1245](https://github.com/coleam00/Archon/issues/1245) |
| Fix proposed in | [PR #1250](https://github.com/coleam00/Archon/pull/1250) (open 2026-04-16) |
| Attack surface | ⚠ Shared hosts only |
| Privilege gained | ❌ Your user, full |
| Disclosure channel | ✅ Public issue (SECURITY.md compliant) |

### F2 — Warning · Structural · no fix yet — `archon serve` web-dist integrity reduces to trusting one GitHub Releases URL (#1246)
*Filed 2026-04-16 · Live · → If you deploy Archon behind a Caddy reverse proxy in production, pin to a specific version tag and mirror the web-dist artifact yourself.*

In `packages/cli/src/commands/serve.ts` lines 82-83, the `archon serve` command downloads the web UI tarball AND its sha256 checksums file from the same `github.com/.../releases/download/vX.Y.Z/` URL. The sha256 check protects against corrupt downloads but not against a compromised release: if a release-manager token or a self-hosted runner were ever compromised, the attacker could rewrite both the tarball and the checksums simultaneously. Reporter shaun0927 asks for independent attestation — a Sigstore bundle, a separate signing key, or a `provenance` assertion generated during publish — so the integrity chain doesn't collapse into "trust GitHub Releases." This is a supply-chain hardening request rather than an exploitable bug today.

| Meta | Value |
|------|-------|
| Filed by | shaun0927 — [issue #1246](https://github.com/coleam00/Archon/issues/1246) |
| Fix | ⚠ None merged yet |
| Who's affected | Anyone running `archon serve` in production |
| Maintainer response | ✅ Issue accepted, labelled `security` |

### F3 — Warning · PR open 3 days — Axios CVE-2025-62718 (NO_PROXY bypass / SSRF) override patch pending (PR #1153)
*PR filed 2026-04-13 · 3 days open · → If you expose any Archon surface that makes outbound HTTP and honors NO_PROXY, watch PR #1153 until merged.*

Axios 1.14.x has [CVE-2025-62718](https://nvd.nist.gov/vuln/detail/CVE-2025-62718) — hostname normalization lets a crafted URL bypass `NO_PROXY` rules, so requests that the user thought would be kept off the proxy can still egress there. Archon pulls axios transitively via `@slack/bolt` and `@slack/web-api`. [PR #1153](https://github.com/coleam00/Archon/pull/1153) adds an `"axios": "^1.15.0"` override to root `package.json`, which is the idiomatic one-line fix — both Slack packages already accept `>=1.15.0` in their semver ranges, so nothing else has to change. The PR has been sitting open for 3 days at scan time. Without a Dependabot config (see F5 below), there's no automation pushing this to get merged.

| Meta | Value |
|------|-------|
| CVE | [CVE-2025-62718](https://nvd.nist.gov/vuln/detail/CVE-2025-62718) |
| Transit path | `@slack/bolt` → `@slack/web-api` → axios |
| Fix PR | [#1153](https://github.com/coleam00/Archon/pull/1153) — filed 2026-04-13 |
| Closes | [#1053](https://github.com/coleam00/Archon/issues/1053) |

### F4 — Warning · Ongoing — Governance: 8% formal review rate, no branch protection, no CODEOWNERS (F11 + F14)
*Since repo creation · → Practical reviewer density is higher than it looks (Wirasm is an active second pair of eyes), but the formal gates are all missing.*

13 of 160 merged PRs in the last 300-window have `reviewDecision` set (8% formal). The any-review rate is 58% (93/160) — meaning a human comment or approval happened on more than half of merges, just not as a formal PR-review decision. This is a much healthier picture than caveman's 15% any-review, but the formal gate is still a gap: no branch protection on `dev` (API returns 404, authoritative), no CODEOWNERS anywhere in the repo. Practically, Wirasm (Rasmus Widing, 791 commits) is the active lead — he merges almost every release — and coleam00 owns. So an owner+lead pair-of-eyes arrangement exists, it just isn't encoded in GitHub settings.

| Meta | Value |
|------|-------|
| Merged PRs (last 300) | 160 |
| Formal review rate | ❌ 8% (13/160) |
| Any-review rate | ⚠ 58% (93/160) |
| Branch protection | ❌ None (dev, main) |
| CODEOWNERS | ❌ None anywhere |
| Practical reviewer | ✅ Wirasm (lead) + coleam00 (owner) |

### F5 — Info · Process gap — No `.github/dependabot.yml` — transitive-CVE PRs aren't opened automatically
*Current · → Why it matters: PR #1153 (axios CVE) sat 3 days because no bot is tracking the dep graph. A dependabot config would have auto-opened it.*

The repo has no `.github/dependabot.yml` or `renovate.json`. The Dependabot alerts API returns 403 with the message "not authorized" (admin scope required to query), which is ambiguous — it could mean alerts are globally disabled, or it could just mean our scan token lacks admin access. Either way, there is no declarative config in the repo to describe which ecosystems and schedules to track. It's an Info finding rather than a Warning because **the maintainers are clearly watching CVEs manually** — PR #1153 is the axios fix, filed 3 days before this scan. But a bot would do this consistently.

### F6 — Info · Known attack surface — Archon executes AI-generated bash via `executeBashNode`
*By design · Ongoing · → Every workflow YAML you author or accept from a third party is effectively a shell script. Read untrusted workflows before running them.*

Archon's DAG engine supports bash script nodes (see `packages/workflows/src/dag-executor.ts` line 1035, `executeBashNode`). That is the working-as-intended feature — it's what lets Archon orchestrate builds, tests, and toolchains. But it also means anyone who hands you a workflow YAML hands you a shell script. Archon does not sandbox these beyond OS-level user isolation, and its own command-exec wrapper in `packages/git/src/exec.ts` uses `execFile` (not a shell — good, avoids interpolation-injection when Archon spawns tools). The threat is procedural, not code-level: treat third-party workflow YAMLs the same way you'd treat a bash script from the internet.

### F7 — OK — Active security work pattern — recent PRs show real engineering care
*2025-2026 · Ongoing · → No action needed. Positive signal: the team treats security PRs as first-class and merges them.*

[PR #1169](https://github.com/coleam00/Archon/pull/1169) (merged) prevents target-repo `.env` files from leaking into subprocesses by explicitly filtering the environment before spawn — the fix closes #1135 and a follow-up #1154. [PR #1217](https://github.com/coleam00/Archon/pull/1217) (merged) replaces the Claude Code SDK's auto-resolved executable path with an explicit `CLAUDE_BIN_PATH` allowlist, which was needed because Bun's `--compile` was baking build-host paths into end-user binaries — a clean fix with good install-instruction copy, CI smoke tests for both positive and negative resolver paths, and a regression test for an earlier bug. These are the marks of a team that uses security review as a development signal rather than a compliance box.

### F8 — OK — Pinned-and-checksummed distribution — opposite of curl-pipe-from-main
*Current · → No action needed. Positive signal: the install path does real verification by default.*

Both `scripts/install.sh` and `scripts/install.ps1` download from tagged GitHub releases (`.../releases/download/vX.Y.Z/archon-<os>-<arch>`), verify the sha256 against a `checksums.txt` retrieved from the same release, and only then install. `SKIP_CHECKSUM` defaults to `false`. The Homebrew formula (`homebrew/archon.rb`) pins each platform binary to a specific version + sha256. The Docker image is published by CI to GHCR with semver tags (`type=semver` / `{{version}}` pattern) — not a rolling "live main" tag. `archon.diy/install` redirects to the exact same repo-hosted script (verified byte-for-byte against `scripts/install.sh`). The one soft spot is the `:latest` rolling tag that `docker run ghcr.io/coleam00/archon:latest` will pick up — users should prefer the explicit semver tag.

---

## 02A · Executable file inventory

> ⚠ 2 Warning · ℹ 2 Info · ✓ 4 OK
>
> 8 executable surfaces cataloged (7 scripts + 1 Tier-1 auto-loaded rule file, post-R3 C5). **2 need attention** — the Codex binary resolver (F1 target) and the `release.yml` homebrew-update job that commits to `dev` without a review gate. 4 scripts + Dockerfile are fine, 2 are informational (`CLAUDE.md` Tier-1 auto-load + build pipeline).
>
> **Your action:** None needed locally on a single-user install today. The Warning items are maintainer-side: merge [PR #1250](https://github.com/coleam00/Archon/pull/1250), optionally gate the auto-commit-to-dev path in `release.yml` (put the Homebrew update behind a PR).

### Quick scan (8 executables — includes Tier 1 auto-loaded rule file, post-R3 C5)

- ⚠ `packages/providers/src/codex/binary-resolver.ts` — resolves Codex CLI path and hands it to SDK. **Warning: no sha256/signature pinning (fix open in PR #1250).**
- ⚠ `.github/workflows/release.yml` → `update-homebrew.sh` — on tag-push, downloads checksums, sed-updates `homebrew/archon.rb`, commits directly to `dev` via `GITHUB_TOKEN`. **Warning: CI bot commits to dev without review gate.**
- ✓ `scripts/install.sh` (mirrored at `archon.diy/install`) — downloads versioned binary + checksums, sha256-verifies, installs to `/usr/local/bin`. **OK — checksum verification on by default.**
- ✓ `scripts/install.ps1` (mirrored at `archon.diy/install.ps1`) — Windows PS1 parity, same checksum verification logic. **OK — F16 Windows surface covered.**
- ✓ `Dockerfile` — multi-stage, `gosu` privilege drop from root to `appuser`, no untrusted tarball fetches. **OK.**
- ✓ `docker-entrypoint.sh` — fixes volume perms, configures `GH_TOKEN` via credential helper (not `~/.gitconfig`), execs as appuser. **OK.**
- ℹ `CLAUDE.md` — Tier 1 auto-loaded agent-rule file. 813 lines of contributor conventions (TypeScript/Zod/Bun discipline). Imperative-verb grep found only project-convention statements, no prompt-injection patterns. **Info — leverage is 1:every-contributor; content benign today.**
- ℹ `scripts/build-binaries.sh` + `scripts/update-homebrew.sh` — build pipeline. Used by CI, not end users. **Info — inspected for sanity, no direct risk.**

### Inventory cards (7 properties each)

#### ⚠ `packages/providers/src/codex/binary-resolver.ts` — unpinned vendor binary

| Property | Value |
|----------|-------|
| 1. Trigger | Any Archon workflow run using the Codex provider. Called by the DAG executor when a node specifies `provider: codex`. |
| 2. Reads | `CODEX_BIN_PATH` env, `assistants.codex.codexBinaryPath` config, `~/.archon/vendor/codex/*` filesystem |
| 3. Writes | None directly; returns a path that the SDK will exec |
| 4. Network | None |
| 5. Injection channel | ⚠ Binary drop — attacker-writable `~/.archon/vendor/codex/` = arbitrary code execution on next Codex workflow |
| 6. Secret-leak path | Indirect — the dropped binary inherits full user env including API keys |
| 7. Privilege | ❌ Your user, full |

**Capability assessment:** this is the F1 surface. Worst case: on a shared host where another user can write to `~/.archon/vendor/codex/`, they drop an executable named the same as the Codex CLI. Your next Codex workflow runs it with your environment, your creds, your file access. **How an attacker arrives (F13):** dev container sharing a home mount, misconfigured Docker volume, prior malware that landed via another vector, admin user on a shared workstation. Not a remote-unauth attack — it requires the attacker to already have some local write access, then escalates via your next workflow run. PR #1250 pins the sha256 on first use.

#### ⚠ `.github/workflows/release.yml` (update-homebrew job) — CI bot commits to dev

| Property | Value |
|----------|-------|
| 1. Trigger | Push of a `v*` tag, or manual `workflow_dispatch`. Runs AFTER the release job completes. |
| 2. Reads | `checksums.txt` from the just-published release, `homebrew/archon.rb` in the repo |
| 3. Writes | `homebrew/archon.rb` in the repo, then git-pushes to `dev` using `GITHUB_TOKEN` |
| 4. Network | GitHub Releases fetch + git push to origin/dev |
| 5. Injection channel | If checksums.txt were attacker-controlled, the sed would embed attacker sha256 into the formula — but checksums.txt is built in the same pipeline run, so this is a closed loop unless the runner is compromised |
| 6. Secret-leak path | ✅ None — `GITHUB_TOKEN` scoped to the repo, not written to disk |
| 7. Privilege | Repo `contents: write`, bot commit as `github-actions[bot]` |

**Capability assessment:** every Homebrew-formula update commits straight to `dev` without a PR review — the branch has no protection rule and no CODEOWNERS gate. In isolation the job is low risk. Combined with F4 (no branch protection) it creates a code-modification path that bypasses human review. Safer pattern: open a PR with the formula update and auto-merge after a status check.

#### ✓ `scripts/install.sh` — sha256-verified by default

| Property | Value |
|----------|-------|
| 1. Trigger | User runs `curl -fsSL https://archon.diy/install \| bash` |
| 2. Reads | GitHub Releases API via curl; env vars `VERSION`, `INSTALL_DIR`, `SKIP_CHECKSUM` |
| 3. Writes | `$INSTALL_DIR/archon` (default `/usr/local/bin/archon`) after successful checksum verify |
| 4. Network | HTTPS to `github.com` / `objects.githubusercontent.com` only |
| 5. Injection channel | ✅ None observed — `set -euo pipefail`, no untrusted interpolation |
| 6. Secret-leak path | ✅ None |
| 7. Privilege | User-level unless `/usr/local/bin` write needs sudo |

**Capability assessment:** unlike caveman's `install.sh` (curl-piped from live `main`), this downloads the binary from a tagged release (`v0.3.6` by default), then downloads `checksums.txt` from the same release, then sha256-verifies the binary matches. `archon.diy/install` serves the exact same content byte-for-byte.

#### ✓ `scripts/install.ps1` — PS1 parity with F16 coverage

Same shape as `install.sh` with PowerShell idioms — `Set-StrictMode -Version Latest`, `$ErrorActionPreference = 'Stop'`, same sha256 verification logic. CI test matrix covers `windows-latest` so PS1 regressions would be caught.

#### ✓ `Dockerfile` + `docker-entrypoint.sh` — drops root to appuser

Multi-stage build (deps → web-build → runtime). Runtime image `chown`s `/.archon` to `appuser`, then `gosu` drops privileges. The git credential helper pattern is the right way to make `GH_TOKEN` available without persisting it to disk. `exec $RUNNER bun run start` ensures the server is PID 1 and receives SIGTERM for graceful shutdown.

#### ℹ `CLAUDE.md` — Tier 1 auto-loaded agent-rule file (re-run post-R3 C5)

**Auto-load tier:** **Tier 1 — Always auto-loaded.** This file is auto-loaded by Claude Code for every contributor session in the Archon repo. Content changes reach every contributor who opens Archon in Claude Code without opt-in. Single-source rule file; NOT CI-amplified into other agent rule destinations (no `.clinerules/`, no `.cursor/rules/`, no `.windsurf/rules/`, no `.github/copilot-instructions.md`).

| Property | Value |
|----------|-------|
| 1. Trigger | Claude Code auto-loads on every contributor session when editing Archon source |
| 2. Reads | N/A — static markdown |
| 3. Writes | N/A — static markdown |
| 4. Network | ✅ None |
| 5. Injection channel | ⚠ The entire file is the injection channel — auto-loads as persistent session context for every contributor |
| 6. Secret-leak path | ✅ None in current content |
| 7. Privilege | Contributor agent context |

**Imperative-verb grep result:** the 813-line file was scanned for patterns from prompt Step 2.5 (`ignore previous`, `you are now`, `from now on`, `pretend`, `act as`, `system prompt`, `jailbreak`, `execute`, `run this command`, `~/.ssh/`, `~/.aws/`). The hits found are all contributor-facing development-discipline imperatives: "All functions must have complete type annotations," "Always use `z.infer<typeof schema>`," "Never duplicate as a plain array," "All new/modified API routes must use `registerOpenApiRoute`," "Keep commits focused." These are normal project-convention statements, not prompt injection.

**Capability statement:** this file shapes how Claude Code behaves when editing Archon — it enforces Bun/TypeScript/Zod conventions, routes schema placement, and test-location rules. It does not instruct the agent to reveal secrets, exfiltrate data, execute network calls, or bypass safety rules.

**Risk statement:** this file is auto-loaded for every session — content changes reach every contributor without opt-in. A future PR that swaps the development-convention content for attacker instructions would take effect on every contributor's next Claude Code session. The existing content is benign; the leverage is permanent. Combined with the governance gaps in F4 (no branch protection on `dev`, no CODEOWNERS, 8% formal review rate), a PR modifying this file could land without a gate.

**Severity:** Info (F9 table row: "Behavioral rules only — tone, format, response style"). Card is required per F9; content is not actively hostile today but the leverage ratio is 1:every-contributor, not the earlier claim of 1:1. **Status chip: `informational` · Action hint: If you contribute to Archon, review diffs to `CLAUDE.md` with the same care as diffs to workflow YAMLs — the blast radius is every contributor's next session.**

#### ℹ `scripts/build-binaries.sh` + `scripts/update-homebrew.sh` — build-only

CI-only pipeline. `build-binaries.sh` uses a bash EXIT trap to restore `packages/paths/src/bundled-build.ts` after `bun build --compile`, so the dev tree is never left dirty even if the build fails. `update-homebrew.sh` validates that extracted sha256 values look like 64-hex-character strings before performing the sed substitution.

---

## 03 · Suspicious code changes

> ⚠ 6 PRs flagged · 0/6 formal review
>
> 6 PRs touching security-critical files (providers, installer, CI workflows), **none had a formal `reviewDecision`**. All six were merged by Wirasm (the lead contributor) landing them from other contributors, so practical review happened even without the `reviewDecision` field being set.

| PR | What it did | Submitted by | Merged by | Reviewed? | Merge time | Concern |
|----|-------------|--------------|-----------|-----------|------------|---------|
| [#1250](https://github.com/coleam00/Archon/pull/1250) | Pin Codex vendor binary sha256 on first use (fixes #1245) | (pending merge) | — | Open | — | Security fix for #1245 LPE, filed 2026-04-16 |
| [#1217](https://github.com/coleam00/Archon/pull/1217) | Replace Claude SDK embed with explicit binary-path resolver | Wirasm | Wirasm | No formal decision | 3 days | Self-submitted-and-merged; content good (CI smoke + regression tests) |
| [#1169](https://github.com/coleam00/Archon/pull/1169) | Prevent target repo .env from leaking into subprocesses (#1135) | Wirasm | Wirasm | No formal decision | 4 days | Self-merged security fix; content is good |
| [#1153](https://github.com/coleam00/Archon/pull/1153) | Override axios to ^1.15.0 for CVE-2025-62718 | (external contributor) | — | Open 3 days | — | Dep CVE fix sitting open; no dependabot auto-open |
| [#1137](https://github.com/coleam00/Archon/pull/1137) | Extract providers from @archon/core into @archon/providers | Wirasm | Wirasm | No formal decision | 2 days | Large refactor touching Dockerfile + binary paths, self-merged |
| [#1114](https://github.com/coleam00/Archon/pull/1114) | Release 0.3.6 (batch merge to dev + tag) | Wirasm | Wirasm | No formal decision | Release-batch | Standard release workflow; all prior PRs already individually merged |

---

## 04 · Timeline

> 🔴 2 bad · 🟡 2 neutral · 🟢 3 good
>
> 7 events over the last few months, plus a long run-up. **Peak concern 2026-04-13 → 2026-04-16** (axios CVE open 3 days, Codex LPE filed the scan day). The team shipped real security hardening in #1169 + #1217 during the same window, so the signal is "actively-working" not "stuck."

- 🟡 **2025-02-07 · START** — Repo created by coleam00 (Cole Medin at Dynamous). Initial architecture: Bun + TypeScript monorepo with workspace packages.
- 🟢 **2026-03 to 2026-04 · SECURITY.md** — Repo adds `SECURITY.md` at root with real private disclosure policy (email + GHSA). The difference between "caveman no-advisory culture" and "real vulnerability management."
- 🟢 **2026-04-04 · ENV LEAK FIXED** — [PR #1169](https://github.com/coleam00/Archon/pull/1169) merges — prevents target-repo `.env` files from leaking into Archon-spawned subprocesses. Real security refactor. Closes #1135.
- 🟡 **2026-04-08 to 04-12 · RELEASES** — Rapid release cadence: v0.3.0 → v0.3.6 in 4 days. All tagged. Homebrew formula auto-updated per release. Docker images published with semver tags to GHCR.
- 🟢 **2026-04-12 · RESOLVER HARDENED** — [PR #1217](https://github.com/coleam00/Archon/pull/1217) merges — explicit `CLAUDE_BIN_PATH` allowlist replaces SDK's auto-resolution. Includes positive and negative CI smoke tests.
- 🔴 **2026-04-13 · AXIOS CVE** — External contributor files [PR #1153](https://github.com/coleam00/Archon/pull/1153) for CVE-2025-62718. **Still open at scan time — 3 days with no merge.** No dependabot config to have auto-opened it.
- 🔴 **2026-04-16 · CODEX LPE** — Reporter shaun0927 files [#1245](https://github.com/coleam00/Archon/issues/1245) (Codex vendor binary LPE) and [#1246](https://github.com/coleam00/Archon/issues/1246) (web-dist attestation). Fix for #1245 proposed as [PR #1250](https://github.com/coleam00/Archon/pull/1250) the same day. Both open at scan time.
- 🟡 **2026-04-16 · SCAN** — This scan runs — same day as the security issue filings. Snapshot will diverge fast from current state; expect these open items to close within days.

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
| SECURITY.md | ✅ Yes (root) | Real private disclosure policy |
| Security advisories | ⚠ 0 published | May be used in future for open items |
| OSSF Scorecard | ⚠ Not indexed | API returned 404 — repo not yet indexed by securityscorecards.dev |
| Dependabot | ⚠ Unknown (403 without admin) | No `.github/dependabot.yml` config either way |
| Runtime dependencies (root) | ✅ 1 (claude-agent-sdk) | Transitive surface via Slack SDK, React, Vite |
| CI workflows | 4 (test, publish, release, deploy-docs) | Real matrix test (ubuntu + windows), Docker smoke test |
| Releases | 10+ (v0.2.13 → v0.3.6) | Rapid iteration, checksums.txt + multi-platform binaries + Docker published per release |
| Total PR count | ~461 closed, 20 open | Active community |

---

## 06 · Investigation coverage

> 160/300 PRs sampled · 7/7 execs inspected · 3 gaps noted
>
> **Only 160 of ~461 closed PRs reviewed** (the 300-PR API-limit window; older PRs not inspected in full). All executable files inspected. Windows PS1 surface covered.

| Check | Result |
|-------|--------|
| Merged PRs reviewed | ⚠ 160 of ~461 (sampled) — under the 300-window cap |
| Suspicious PR diffs read | 6 of the 300-keyword hits — the flagged 6 in §03 read in full |
| Dependency scan | ⚠ Metadata only — Dependabot API 403 (admin scope); full lockfile audit not performed |
| Workflow files read | ✅ 4 of 4 — deploy-docs, publish, release, test |
| Executable files inspected | ⚠ 7 of 7 (2 Warning, 4 OK, 1 Info) |
| Tarball extraction | ✅ OK (769 files) — pinned to `3dedc22` at scan start (F6 TOCTOU guard) |
| README paste-scan (7.5) | ✅ 0 paste-blocks |
| CI-amplified rule scan (2.5) | ✅ No amplifier — one `CLAUDE.md` at root, not copied into `.clinerules/` etc. by CI |
| Prompt-injection scan (F8) | ✅ 0 matches / 0 actionable |
| Distribution channels verified (F1, post-R3 C6) | ⚠ **Install path verified, installed artifact NOT verified.** 2 of 2 install paths are pinned and sha256-checked against the release's `checksums.txt` (script byte-matches `scripts/install.sh`; Homebrew formula pins per-platform sha256; Docker publish workflow uses semver GHCR tags). But the Bun-compiled binary was NOT independently rebuilt from source and diffed against the release tarball — so the trust chain terminates at GitHub Releases. This IS the gap Archon's own F2 issue (#1246) names. Treat verdict as "install path looks right; end-artifact reproducibility is not established." |
| Windows surface coverage (F16) | ✅ install.ps1 inspected; CI test matrix covers windows-latest |
| OSSF Scorecard | ⚠ Not indexed (API returned 404) — repo not yet tracked by securityscorecards.dev; no independent governance score available |
| osv.dev | ℹ Not queried — runtime deps are minimal (1 direct: claude-agent-sdk); transitive surface via Slack SDK covered by CVE watch (F3) |
| Secrets-in-history | ⚠ Not scanned (gitleaks not available) |
| API rate budget | ✅ 5000/5000 remaining. PR sample: full. |
| Tarball SHA | `3dedc22` — if your tree differs, re-run the scan |

**Gaps noted:**

1. Older PRs (pre-2026-03) not inspected — sampling window stops at 300 PRs deep.
2. Dependabot alerts API requires `admin:repo_hook` — token used here lacks it; alert state unknown beyond "no config file."
3. Monorepo has 11 inner packages with their own `package.json` — per-package dep surface not enumerated here; root + root-lock inspected as the primary surface.

---

## 07 · Evidence appendix

> ℹ 9 facts · ★ 3 priority
>
> 9 command-backed claims. **Skip ahead to items marked ★ START HERE** — the Codex LPE issue body, the install-script byte-match against archon.diy, and the review-rate dual metric.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — Codex vendor binary resolver has no sha256 pinning (F1 / issue #1245)

```bash
gh issue view 1245 -R coleam00/Archon --json title,body -q '.title'
```

Result:
```
security(providers): codex vendor binary resolver lacks hash/signature pinning — LPE via writable vendor dir
```

*Classification: Confirmed fact — issue body explains the resolver flow and the attack pre-condition (writable `~/.archon/vendor/codex/`). Fix open in PR #1250.*

#### ★ Evidence 2 — archon.diy/install serves the same content as repo scripts/install.sh

```bash
curl -fsSL https://archon.diy/install | head -5
head -5 /tmp/repo-scan-coleam00-Archon/scripts/install.sh
```

Result (identical from both commands):
```
#!/usr/bin/env bash
# scripts/install.sh
# Install Archon CLI from GitHub releases
```

*Classification: Confirmed fact — archon.diy acts as a CDN/redirect for the repo's install script, not a separately-controlled distribution endpoint.*

#### ★ Evidence 3 — Dual review-rate metric (F11) — 8% formal, 58% any-review

```bash
gh pr list -R coleam00/Archon --state merged --limit 300 --json reviewDecision,reviews \
  | jq '{ total: length,
          formal_review: [.[] | select(.reviewDecision != null and .reviewDecision != "")] | length,
          any_review:    [.[] | select(.reviews != null and (.reviews | length) > 0)]    | length }'
```

Result:
```json
{ "total": 160, "formal_review": 13, "any_review": 93 }
```

*Classification: Confirmed fact — 13/160 formal decisions = 8%; 93/160 any-review = 58%. The gap is the practical-vs-formal reviewer pattern Archon runs on.*

### Other evidence supporting Warnings

#### Evidence 4 — Axios CVE fix open 3 days (PR #1153)

```bash
gh pr view 1153 -R coleam00/Archon --json title,state,createdAt
```

Result:
```json
{"createdAt":"2026-04-13T01:31:22Z","state":"OPEN","title":"fix: override axios to ^1.15.0 for CVE-2025-62718"}
```

*Classification: Confirmed fact — PR #1153 open since 2026-04-13, scan date 2026-04-16.*

#### Evidence 5 — No branch protection on dev or main

```bash
gh api "repos/coleam00/Archon/branches/dev/protection"
gh api "repos/coleam00/Archon/branches/main/protection"
```

Result:
```
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

*Classification: Confirmed fact — 404 is authoritative, the token has `repo` scope and would return 403 if the issue were permissions.*

#### Evidence 6 — No dependabot config file in repo

```bash
find /tmp/repo-scan-coleam00-Archon -name "dependabot.yml" -o -name "dependabot.yaml" -o -name "renovate.json"
gh api "repos/coleam00/Archon/dependabot/alerts"
```

Result:
```
(find returns nothing)
{"message":"You are not authorized to perform this operation.","status":"403"}
```

*Classification: Inference — the 403 means our token lacks admin scope, not that alerts are off. But the missing config file is definitive: no declarative dependency-tracking policy exists in the repo.*

### Evidence supporting OK findings

#### Evidence 7 — SECURITY.md with real private disclosure

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

*Classification: Confirmed fact — real private channel + GHSA link, unlike caveman's missing policy.*

#### Evidence 8 — Maintainer is established (coleam00 — 7 years, 6,641 followers, Dynamous)

```bash
gh api "users/coleam00" -q '{login,created_at,public_repos,followers,company}'
```

Result:
```json
{"company":"Dynamous","created_at":"2019-02-03T02:45:51Z","followers":6641,"login":"coleam00","public_repos":51}
```

*Classification: Confirmed fact — 7-year-old account, public company affiliation, large following. Not a sockpuppet.*

#### Evidence 9 — Install script verifies sha256 checksums by default

```bash
grep -nE 'SKIP_CHECKSUM|sha256sum|verify_checksum' /tmp/repo-scan-coleam00-Archon/scripts/install.sh | head -5
```

Result:
```
#   SKIP_CHECKSUM - Set to "true" to skip checksum verification (not recommended)
# SKIP_CHECKSUM opt-in only; defaults to false
SKIP_CHECKSUM="${SKIP_CHECKSUM:-false}"
```

*Classification: Confirmed fact — checksum verification is the default install path.*

---

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

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-16 · scanned dev @ 3dedc22 (v0.3.6)*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
