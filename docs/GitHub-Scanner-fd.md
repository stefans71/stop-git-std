# Security Investigation: sharkdp/fd

**Investigated:** 2026-04-16 | **Applies to:** master @ `a665a3bba9abc85e80c142a7dcdb8c356b12d9c9` · v10.4.2 | **Repo age:** 8+ years | **Stars:** 42,563 | **License:** MIT OR Apache-2.0 (dual)

> A 42,000-star Rust command-line alternative to `find` that ships 14 pre-built platform binaries — signed with sigstore SLSA Build L3 attestations on every release. The CLI source is clean: one benign `unsafe` block to restore the default SIGINT handler, no network I/O, `Command::new` only where fd's own `-x` flag requires it. The caveat: no branch protection on `master`, and the crates.io publish path is manual rather than CI-gated.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-fd.md` (+ `.html` companion) |
| Repo | [github.com/sharkdp/fd](https://github.com/sharkdp/fd) |
| Short description | Simple, fast, user-friendly alternative to `find`. Written in Rust, shipped as a single self-contained CLI binary named `fd` across 14 Linux/macOS/Windows targets. Distributed as pre-built tarballs and `.deb` files on GitHub Releases (sigstore-attested), via distro package managers (apt/dnf/pacman/brew), on Winget, and on crates.io as `fd-find`. |
| Category | `developer-tooling` |
| Subcategory | `cli-filesystem-search` |
| Language | Rust (edition 2024, MSRV 1.90.0) |
| License | MIT OR Apache-2.0 (dual) |
| Target user | Developers and sysadmins using `find` alternatives on Unix / macOS / Windows |
| Verdict | **Caution** (split — see below) |
| Scanned revision | `master @ a665a3b` (release tag `v10.4.2`) |
| Commit pinned | `a665a3bba9abc85e80c142a7dcdb8c356b12d9c9` |
| Scanner version | `V2.3-post-R3` |
| Scan date | `2026-04-16` |
| Prior scan | None — first scan of this repo. Future re-runs should rename this file to `GitHub-Scanner-fd-2026-04-16.md` before generating the new report. |

---

## Verdict: Caution (split — Deployment axis only)

### Deployment · Solo-dev laptop · default install — **Good with caveats — install from Releases, verify the attestation once**

The CLI itself is clean: a single benign `unsafe` block to restore the default SIGINT handler, no network I/O, narrow filesystem-walking surface, and `Command::new` only where fd's own `-x` flag requires it. Release artifacts are signed with sigstore SLSA Build L3 attestations via `actions/attest` — a rare gold-standard signal. The upstream caveat is governance: no branch protection on `master`, no rulesets, no CODEOWNERS. For a single-user laptop the blast radius is small; the attestation makes "what you installed came from this repo's CI" cryptographically verifiable.

### Deployment · Shared host / production / CI runner — **Good with caveats — verify the attestation with `gh attestation verify` before rolling out**

Same verdict, stronger caveat. `fd` runs with the calling user's privileges and `-x` spawns arbitrary user-supplied commands by design. If an attacker phishes a maintainer credential and pushes malicious Rust, their tampered release binary would still fail `gh attestation verify --owner sharkdp ARCHIVE` because they can't mint a matching sigstore attestation from outside the workflow. Enforce that check in your rollout path and prefer GitHub Releases or distro packages over `cargo install fd-find` (which bypasses the CI attestation trail).

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Governance gap — no branch protection, no CODEOWNERS on a 42k-star CLI (1 finding)</strong>
<br><em>C20 single-point-of-failure fires as Warning (release age 37 days, well outside the 30-day Critical window, with an 8-month gap before v10.4.0). Partially mitigated by sigstore attestations: an attacker pushing malicious Rust still can't mint a valid attestation from outside the workflow.</em></summary>

1. **Governance · F0 / C20** — No classic branch protection on `master` (API returns 404), zero rulesets (`/rulesets` returns `[]`, `/rules/branches/master` returns `[]`), no CODEOWNERS in any of 4 standard locations. Owner is a User account (sharkdp), not an Organization, so there is no org-level ruleset layer either way. Warning (not Critical) because v10.4.2 shipped 37 days before this scan, safely outside the 30-day Critical window; v10.3.0 before it sat ~8 months with no release, so "no recent release" is an honest reading of the cadence rather than a borderline call.

</details>

<details>
<summary><strong>✓ Strong positive signals — SLSA L3 attestations, least-privilege CI, long-tenured maintainers (8 signals)</strong>
<br><em>Sigstore SLSA Build L3 on every release, <code>persist-credentials: false</code> on every checkout, scoped <code>contents: read</code> root permissions, SHA-pinned release actions, SECURITY.md present, no network I/O, maintainer at Astral, recent attestation work landed by tmccombs</em></summary>

1. **SLSA L3 attestations** — Every release artifact (14 pre-built targets, tarballs + `.deb`) is signed in-CI with sigstore via `actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26 # v4`. Consumers can verify: `gh attestation verify --owner sharkdp ARCHIVE`. This is the gold-standard supply-chain signal — rarer than SHA-pinning, stronger than OIDC publishing. PR #1809 landed it 2025-10; PRs #1904 and #1941 fixed pipeline bugs 2026-03 — actively maintained.
2. **Token-exfil defense** — `persist-credentials: false` on every `actions/checkout` call (5 of 5 occurrences). If any workflow step were compromised, there would be no checkout-provided token lying around for the attacker to reuse against the repo.
3. **Least-privilege permissions** — Top-level workflow permission is `contents: read`. Only the `build` job escalates to `id-token: write`, `contents: write`, `attestations: write` — and only for the release-attestation step. A compromised lint or test step cannot push tags or mint attestations.
4. **Release-path actions SHA-pinned** — Security-critical actions all use commit hashes: `actions/attest`, `softprops/action-gh-release`, `actions/upload-artifact`, `vedantmgoyal9/winget-releaser`. `actions/checkout@v6` and `dtolnay/rust-toolchain@stable`/`@master` are tag/branch-pinned (minor gap, both high-trust publishers).
5. **Narrow runtime surface** — Grep of `src/` found no network I/O (zero `reqwest`/`ureq`/`hyper`/`TcpStream`/`UdpSocket`), one `unsafe` block (`src/exit_codes.rs:35`, POSIX SIGINT default-handler restore — benign idiomatic Rust), and five `Command::new` sites all by design (two implement fd's `-x`/`--exec` flag from user argv, two detect `gls`/`ls` for color heuristics, one is the exec helper's `spawn` wrapper). No `extern "C"`, no `libc::` direct usage, no `fs::remove_dir_all`/`remove_file`.
6. **No `pull_request_target`** — The single workflow `.github/workflows/CICD.yml` triggers on `pull_request`, `push`, and `workflow_dispatch` — zero `pull_request_target`. That event type is the vector in most GitHub Actions PwnRequest supply-chain incidents.
7. **Disclosure wired up** — `SECURITY.md` present (38 lines), points at GitHub Security Advisories form. Zero advisories filed in 8 years. PR #1829 "docs(security): clarify where to send vulnerability reports" shows maintainers keep the path current.
8. **Maintainers** — Primary maintainer sharkdp (David Peter) has a GitHub account since 2013-04, 118 public repos, 7,960 followers, and now works at **@astral-sh** (ruff/uv). Co-maintainer tmccombs (Thayne McCombs) has an account since 2012-10, 186 public repos, and personally landed the SLSA attestation work. tavianator (author of the competing `bfs` tool) is the #4 contributor. No sockpuppet signals; all three-person effective core are decade-tenured Rust/Unix-tools names.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⚠ **Review happens but isn't required** — ~33% formal review rate in sample, no branch protection, no CODEOWNERS, three-person effective core |
| Is it safe out of the box? | ✅ **Yes** — clean source, single benign `unsafe` block for SIGINT restore, no network I/O, narrow filesystem-walking surface |
| Can you trust the maintainers? | ✅ **Yes** — sharkdp at Astral, tmccombs 186-repo footprint, active supply-chain work (added SLSA attestations in 2025-10) |
| Is it actively maintained? | ⚠ **Partly** — v10.4.x shipped March 2026 after an **8-month gap** since v10.3.0. Dependabot bumps flow weekly, but feature releases are sporadic |

---

## 01 · What should I do?

> ✓ Safe to install today · ⚠ Verify the attestation · 3 steps
>
> **Install from GitHub Releases** — the CLI source is clean and every release artifact is cryptographically signed (Step 1). If you ship `fd` to shared hosts or CI runners, verify the sigstore attestation before rolling out (Step 2). Step 3 is a maintainer-side ask: branch protection on `master` and a CI-gated `cargo publish` would close the two residual governance gaps.

### Step 1: Install `fd` the way the README describes — prefer GitHub Releases or your distro's package (✓)

**Non-technical:** `fd` is a single self-contained command-line binary that replaces `find`. It has no install-time scripts, no network access at runtime, and the source code is narrow and clean. You can install it from your system's package manager (`apt`, `dnf`, `pacman`, `brew`, `winget`) or download a pre-built binary directly from GitHub Releases. Both paths land the same compiled artifact; the GitHub Releases path is the one that comes with a cryptographic receipt (sigstore attestation) you can verify.

```bash
# Linux (Debian/Ubuntu)
apt install fd-find       # binary is /usr/bin/fdfind on Debian

# macOS
brew install fd

# Windows
winget install sharkdp.fd

# Direct from GitHub Releases (sigstore-attested) — pick your platform:
curl -LO https://github.com/sharkdp/fd/releases/download/v10.4.2/fd-v10.4.2-x86_64-unknown-linux-gnu.tar.gz
```

### Step 2: If you ship `fd` on shared hosts or CI, verify the sigstore attestation before rollout (⚠)

**Non-technical:** Because there is no branch protection on `master`, an attacker who compromised a maintainer's credentials could in theory push malicious Rust. But fd's release pipeline signs every artifact with sigstore SLSA Build L3 attestations, and an attacker outside the workflow can't mint a valid attestation — so you can turn "did this binary come from their CI?" into a yes-or-no check. Do it once per release before rolling out to production or CI runners. Skip `cargo install fd-find` for production installs because that path bypasses the CI attestation trail (crates.io publishing is done manually by a maintainer).

```bash
# Download the release tarball + its sigstore bundle
gh release download v10.4.2 --repo sharkdp/fd \
    --pattern 'fd-v10.4.2-x86_64-unknown-linux-gnu.tar.gz*'

# Verify the attestation
gh attestation verify --owner sharkdp fd-v10.4.2-x86_64-unknown-linux-gnu.tar.gz

# Expected: "Verification succeeded" with a sigstore certificate matching
# .github/workflows/CICD.yml at tag v10.4.2
```

### Step 3: Nudge the maintainers on branch protection + CI-gated crates.io publish

**Non-technical:** The maintainers are clearly doing supply-chain hygiene well — they added SLSA attestations in October 2025, they set `persist-credentials: false`, they SHA-pin the release-path actions. Two helpful asks would close the remaining gaps:

1. Enable classic branch protection on `master` with a 1-approver review requirement and the existing CI status checks, and add a `.github/CODEOWNERS` covering `.github/workflows/` and `src/`.
2. Add a gated `cargo publish` step to the tag-push release workflow so the crates.io path gets the same CI attestation trail the GitHub Releases path already has.

Both are small, incremental, free.

- Branch protection setup: [github.com/sharkdp/fd/settings/branch_protection_rules/new](https://github.com/sharkdp/fd/settings/branch_protection_rules/new)

---

## 02 · What we found

> ⚠ 1 Warning · ℹ 1 Info · ✓ 3 OK
>
> 5 findings total. **The one Warning is governance, not code.** F0 is the C20 single-point-of-failure (no branch protection on `master`, no rulesets, no CODEOWNERS) — fires at Warning because release age (37 days) sits firmly outside the 30-day Critical window and the historical cadence includes 8-month gaps. F-crates.io is an Info-severity note that the manual `cargo publish` path bypasses the CI attestation trail. Everything else is positive: SLSA L3 attestations, `persist-credentials: false`, scoped permissions, no network I/O, long-tenured maintainers.
>
> **Your action:** Nothing you need to do locally at the source level — the CLI is clean. For shared hosts or CI runners, run `gh attestation verify --owner sharkdp ARCHIVE` before rolling out (see Step 2 above). For maintainers: enabling branch protection on `master` and adding a CI-gated `cargo publish` job would close both findings without changing any Rust.

### F0 — Warning · Structural · Partly mitigated by SLSA attestations — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a 42k-star CLI (C20)

*Continuous · Since repo creation · → If you install: prefer GitHub Releases or distro packages over `cargo install fd-find`, and run `gh attestation verify --owner sharkdp ARCHIVE` on shared-host or CI rollouts. If you maintain this repo: enable classic branch protection on `master` (Settings → Branches → Add rule, require 1 approver, require the existing CICD workflow checks) and add a `.github/CODEOWNERS` covering `.github/workflows/` + `src/`.*

**Severity sits at Warning, comfortably.** The V2.3 C20 rule escalates to Critical when a repo (a) has all three governance signals negative AND (b) ships executable code to user machines AND (c) has a release within the last 30 days. fd's latest v10.4.2 shipped 2026-03-10 — 37 days before this scan, outside the 30-day window. This is not a boundary case like some other scans: v10.4.0 before it shipped 2026-03-07 (40 days out), and v10.3.0 before that shipped 2025-08-26 — an **8-month gap**. "No recent release" is an honest read of the cadence, not a one-day margin.

**What's missing.** Classic branch protection on `master` returns HTTP 404 from the GitHub API (authoritative — our scan token has `repo` scope and would have returned 403 on a permissions issue). Repo rulesets: `gh api repos/sharkdp/fd/rulesets` returns `[]`. Rules applying to `master`: `gh api repos/sharkdp/fd/rules/branches/master` returns `[]` — this endpoint is authoritative because it captures both repo-level and org-level rulesets. Note on org-level: sharkdp is a **User account**, not an Organization, so there is no org-level ruleset layer either way — the authoritative check reduces to the three signals above plus CODEOWNERS. CODEOWNERS is absent in all four standard locations (`CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`, `.gitlab/CODEOWNERS`). Any push that lands on a maintainer's credentials goes directly to `master` without a review gate, a required status check, or a path-scoped reviewer.

**How an attacker arrives (F13).** Concrete paths without requiring xz-utils-level tradecraft: (1) credential phishing against sharkdp or tmccombs — both have public GitHub profiles, substantial followings, and findable identities (sharkdp publishes under his real name, now at Astral); (2) stale OAuth token reuse from an old CI system or developer workstation; (3) compromised browser session cookie via a malicious browser extension running in the maintainer's session; (4) malicious IDE / VS Code / Cursor extension executing as the maintainer; (5) sloppy review on an attacker-submitted PR — the observed review-rate sample shows ~67% of merges had no formal `reviewDecision`, though cross-merging (tmccombs merges most PRs; tavianator occasionally merges tmccombs's work) provides practical second-pair-of-eyes; (6) crates.io token theft specifically, which would bypass the repo entirely (see F-crates.io below). None of these require compromising the sigstore infrastructure; paths 1–5 route through the repo.

**Why sigstore attestations partially mitigate this — a real, unusual defense.** An attacker who successfully phished a maintainer and pushed malicious Rust to `master` would still face one hard gate: every release artifact is signed in-CI with a sigstore attestation that binds the artifact to *this exact repo's workflow at a specific commit SHA*. If the attacker builds a tampered binary locally and uploads it to a release, consumers running `gh attestation verify --owner sharkdp` on the tarball get a failure — they'd need to mint a matching attestation, which they can't do from outside the GitHub Actions OIDC issuer. The attacker would need to also corrupt the workflow file (visible in the repo history) or compromise the CI runner itself (different attack class). That's a meaningful raise on the bar, and it's why this finding sits at Warning with a *partly mitigated* chip rather than at Critical even when release age is close to the 30-day line. The attestation isn't a replacement for branch protection — a poisoned source commit would still propagate — but it does convert "silent malicious release" into "attestation-verifiable release that someone has to audit."

**What this means for you.** On a single-user laptop the blast radius is small: fd is a local filesystem tool that runs with your user privileges, and the `-x` flag only spawns what *you* type. On a shared host or CI runner the blast radius is larger because the binary is privileged against other users' data in the same environment. Either way, the practical mitigation is cheap: run `gh attestation verify --owner sharkdp ARCHIVE` once per release you install, prefer GitHub Releases / distro packages over `cargo install fd-find`, and pin the specific version. That turns "trust sharkdp's account security" into "trust sharkdp's account security, AND trust that the CI log and sigstore certificate chain haven't been subverted" — two independent gates.

**What this does NOT mean.** The CLI itself is clean — one benign `unsafe` block to restore POSIX SIGINT, no network I/O, narrow filesystem-walking surface, and the `Command::new` sites that do exist implement fd's own `-x` flag from user argv. This finding is about the repo's process gap, not about the current v10.4.2 shipping something harmful. Treat it as a tail-risk on future releases with a meaningful in-CI mitigation already in place.

| Meta | Value |
|------|-------|
| Classic branch protection | ❌ 404 on `master` |
| Rulesets | ❌ `[]` — zero rulesets |
| Rules on master | ❌ `[]` — authoritative |
| CODEOWNERS | ❌ Absent (4 locations checked) |
| Org-level rulesets | ✅ N/A (owner is User) |
| Stars (blast radius) | 42,563 |
| Forks (blast radius) | 1,037 |
| Latest release age | ✅ 37 days — outside Critical window |
| Release cadence | ⚠ Irregular (8-month gap before v10.4.0) |
| Partial mitigation | ℹ Sigstore SLSA L3 on release artifacts |
| Executable surface | ⚠ CLI binary, user privileges, `-x` spawns by design |

**How to fix (maintainer-side, 2 minutes in the UI).** GitHub *Settings → Branches → Add branch protection rule* ([direct link](https://github.com/sharkdp/fd/settings/branch_protection_rules/new)). For `master`: require pull request reviews (1 approver minimum), require status checks (the existing CICD jobs — `lint_check`, `min_version`, `build`), require branches to be up to date before merging, do not allow bypassing. Also add `.github/CODEOWNERS` covering at minimum `.github/workflows/ @sharkdp @tmccombs` and `src/ @sharkdp @tmccombs`. The cross-merge pattern between tmccombs, tavianator, and sharkdp is already doing most of this manually — formalising it closes the SPOF without slowing velocity.

### F-crates.io — Info · Narrow-channel gap — Manual `cargo publish` path bypasses the CI attestation trail

*Current · Pipeline-level · → If you install `fd`: prefer GitHub Releases, distro packages, or Winget over `cargo install fd-find` for production / shared-host installs — those paths carry the sigstore attestation; crates.io does not. If you maintain this repo: add a gated `publish` job to `CICD.yml` that runs `cargo publish` on tag push using a scoped crates.io token in GitHub Secrets, bringing the crates.io channel into the same CI-verifiable trust chain as the GitHub Releases channel.*

**What we observed.** Reading `.github/workflows/CICD.yml` (309 lines, the repo's only workflow file) reveals six jobs: `crate_metadata`, `ensure_cargo_fmt`, `lint_check`, `min_version`, `build` (the 14-target cross-platform matrix that produces attested tarballs and `.deb` files), and `winget`. **There is no `cargo publish` step.** Yet the `fd-find` crate is on crates.io and is kept current (v10.4.2 at scan time). The only explanation: a maintainer runs `cargo publish` by hand on a local workstation with a crates.io API token.

**Why this is Info and not Warning.** Most fd users do not install via `cargo install fd-find`. The README lists apt, dnf, pacman, brew, Winget, and direct GitHub Releases as the primary channels; `cargo install` is a niche path for Rust-ecosystem users who already have `cargo` on their machine. The blast radius of a crates.io-only compromise is narrow — orders of magnitude smaller than an npm package that every React developer pulls transitively. Calling this Warning would over-weight the channel.

**What a crates.io compromise would look like.** An attacker who stole sharkdp's crates.io token (via malicious browser extension, stale laptop credential, or a compromised `.cargo/credentials.toml`) could publish a malicious `fd-find` version without ever touching the GitHub repo. Consumers using `cargo install fd-find` would get the tampered version; consumers using GitHub Releases or distro packages would not. The GitHub Releases path is unaffected because those artifacts still come with a valid sigstore attestation pinned to the real workflow.

**What this does NOT mean.** This is not a code-level concern — the crate source on crates.io is currently the same source as the repo, and there is no evidence of tampering on any channel. It's a pipeline topology note: one of three documented artifact channels is outside the CI-attested trust boundary. Fixable in a 10-line workflow job.

| Meta | Value |
|------|-------|
| CI `cargo publish` | ⚠ Absent from CICD.yml |
| crates.io crate | `fd-find` v10.4.2 |
| GitHub Releases path | ✅ Sigstore L3 attested |
| Winget path | ✅ CI-driven (`winget` job) |
| Primary user channels | apt / dnf / brew / Releases / Winget |
| Blast radius | ℹ Narrow (crates.io users only) |

**How to fix (maintainer-side, ~10 lines of YAML).** Add a `publish` job to `CICD.yml` that runs on tag push, depends on `build` (so the matrix passes first), and calls `cargo publish` with a scoped crates.io token from GitHub Secrets. Scope the token to the `fd-find` crate only (crates.io supports per-crate tokens now). That folds the crates.io channel into the same in-CI trust chain as GitHub Releases and Winget — a future compromise would need to go through the workflow runner, not a maintainer's laptop.

### F2 — OK — Clean runtime surface — one benign `unsafe` block, no network I/O, `Command::new` is by design

*Current · → No action needed. Positive signal: the CLI does what a `find` alternative should do and nothing more; the only dangerous primitives present are the ones fd's own documented behaviour requires.*

**The one `unsafe` block is benign.** Grep across `src/` found exactly one `unsafe` block: `src/exit_codes.rs:35`. It restores the POSIX default `SIGINT` handler and re-raises `SIGINT` on Ctrl-C so the parent shell sees the normal interrupt status rather than the Rust panic path. This is the idiomatic way to interact with libc's signal API from Rust — the equivalent C code would be a two-line `signal(SIGINT, SIG_DFL); raise(SIGINT);` snippet. No raw-pointer arithmetic, no `extern "C"` callback, no `libc::` direct memory access. Benign, narrow, necessary.

**Every `Command::new` call is a fd feature, not a surprise.** Grep surfaced five spawn sites in `src/`. Two (`src/exec/mod.rs:168` and `:265`) implement fd's flagship `-x` / `--exec` flag — by design, fd runs whatever command you pass on the command line against every match. The input comes from the user's own argv, not from file contents or network data. One (`src/exec/command.rs:77`) is the `cmd.spawn()` wrapper that backs the `-x` implementation. Two (`src/main.rs:392` and `:421`) probe for `gls` and `ls` to detect GNU `ls` availability so fd can pick a colour strategy — hard-coded binary names, no user input threaded through. Running a shell command you typed is fd's job; treating that as a Warning-grade finding would be re-labelling the product.

**No network I/O, no dangerous filesystem primitives.** Grep of `src/` for `reqwest`, `ureq`, `hyper`, `http::`, `TcpStream`, `UdpSocket` returned zero hits. fd is a strictly local filesystem tool — no telemetry, no auto-update, no crash reporting. Grep for `fs::remove_dir_all` and `fs::remove_file`: zero hits (fd searches, it doesn't delete). Grep for prompt-injection strings across `src/`, `README.md`, and `CHANGELOG.md`: zero hits. Positive control: the grep infrastructure returned the expected `Command::new` and `unsafe` matches, so "zero hits elsewhere" is a meaningful signal.

| Meta | Value |
|------|-------|
| `unsafe` blocks in `src/` | ✅ 1 (benign — POSIX SIGINT restore) |
| Network I/O | ✅ None |
| `Command::new` sites | ✅ 5 (all by-design; `-x` flag + ls probe) |
| `extern "C"` / `libc::` | ✅ None in `src/` |
| Destructive FS ops | ✅ None (`remove_*` absent) |
| Install hooks | ✅ None (no `build.rs` side effects) |

### F3 — OK — Release pipeline is defensive — SLSA Build L3 attestations, scoped permissions, `persist-credentials: false`

*Current · → No action needed. Positive signal: the maintainers use the current supply-chain best practice (sigstore attestations via `actions/attest`) on every release, not just on paper. PR #1809 in 2025-10 landed this; PRs #1904 and #1941 in 2026-03 fixed pipeline bugs — active, not abandoned.*

**Sigstore SLSA Build L3 attestations.** The release path in `.github/workflows/CICD.yml` calls `actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26 # v4` on every release artifact — tarballs and `.deb` files across 14 cross-platform targets (Linux gnu/musl on x86_64/i686/aarch64/arm, Windows msvc/gnu on x86_64/i686/aarch64, macOS Intel/Apple Silicon). The attestation binds each artifact to the repository, the exact workflow file, and the commit SHA that built it, using sigstore's Fulcio certificate authority and Rekor transparency log. Consumers verify with `gh attestation verify --owner sharkdp ARCHIVE`. This is the 2025/2026 gold standard — stronger than SHA-pinning, stronger than OIDC publishing alone.

**Least-privilege root permissions.** `CICD.yml` declares `permissions: { contents: read }` at the top level. Only the `build` job escalates — and only for the attestation step itself — to `id-token: write`, `contents: write`, and `attestations: write`. Every other job (lint, fmt, MSRV check, test matrix) inherits the read-only default. A compromised lint step literally cannot push tags or mint attestations.

**`persist-credentials: false` on every checkout.** All five `actions/checkout` invocations in the workflow set `persist-credentials: false`. If any later step were compromised (e.g. via a malicious dependency pulled in during `cargo build`), there would be no checkout-provided GITHUB_TOKEN sitting in `.git/config` for the attacker to reuse against the repo. The pattern costs one YAML line and closes the token-exfil class of attack that hit several Node projects in 2024-2025.

**Release-path actions are SHA-pinned.** The security-critical actions all use commit hashes: `actions/attest@59d89421...`, `actions/upload-artifact@bbbca2dd...`, `softprops/action-gh-release@153bb8e0...`, `vedantmgoyal9/winget-releaser@4ffc7888...`. `actions/checkout@v6` and `dtolnay/rust-toolchain@stable`/`@master` are tag/branch-pinned — a minor gap (both are high-trust publishers, but tags are mutable). Tightening those two would be incremental, not urgent.

| Meta | Value |
|------|-------|
| Attestation | ✅ Sigstore SLSA L3 on all release artifacts |
| Root permissions | ✅ `contents: read` (scoped escalation) |
| Checkout credentials | ✅ `persist-credentials: false` (5/5) |
| Release-action pinning | ✅ 4/4 SHA-pinned |
| Other pinning | ⚠ checkout @v6, rust-toolchain @stable (tag/branch) |
| `pull_request_target` | ✅ 0 occurrences |

### F4 — OK — Maintainers are long-tenured Rust-ecosystem names — sharkdp at Astral, tmccombs driving supply-chain work

*2012–2026 · Long-tenured · → No action needed. Positive signal: the accounts with commit and release rights are established public identities with substantial track records — not fresh accounts that could be "account created to hijack" candidates.*

**Primary maintainer.** [sharkdp](https://github.com/sharkdp) (David Peter) has had a GitHub account since 2013-04-20 (13 years), 118 public repos, and 7,960 followers. Public identity: blog at [david-peter.de](https://david-peter.de/), based in Stuttgart, Germany. Critically for supply-chain trust: David is now employed at **@astral-sh**, the company behind `ruff` and `uv` — two of the most widely-deployed Rust-written Python tools in 2026. He has 594 commits on fd and has been active on it since the repo's creation in 2017.

**Co-maintainer.** [tmccombs](https://github.com/tmccombs) (Thayne McCombs) has had a GitHub account since 2012-10-12, 186 public repos, and 67 followers. The follower count is smaller than sharkdp's but the repo footprint is notably larger — tmccombs has a broad Unix-tooling portfolio. He has 455 commits on fd and has personally owned the recent supply-chain work: PR #1809 (2025-10-15) added the sigstore attestations, PRs #1904 and #1941 (2026-03) fixed attestation pipeline bugs, PR #1829 (2025-11-09) improved SECURITY.md. When a second-tier contributor takes on the supply-chain hygiene work, that is the pattern of a project being actively stewarded rather than coasting on its flagship maintainer.

**Third-person of the effective core.** [tavianator](https://github.com/tavianator) (Tavian Barnes) is the #4 contributor with 105 commits, account since 2012-04-30, 60 public repos, 233 followers. Tavian is the author of [`bfs`](https://github.com/tavianator/bfs), a competing `find` alternative with its own following. That a direct competitor contributes to fd is a credibility signal — it rules out the "single cult of personality" risk and means two independent maintainers of Unix search tools are looking at the same codebase.

**Dependency bench is credible.** fd's runtime dependencies are overwhelmingly maintained by trusted Rust-ecosystem names: BurntSushi (`aho-corasick`, `regex`, `regex-syntax`, `ignore`, `globset`, `jiff` — the same `ignore` crate that powers `ripgrep`), dtolnay (`anyhow`), the clap-rs organisation (`clap`, `clap_complete`), the nushell maintainers (`nu-ansi-term`), plus standard concurrency primitives (`ctrlc`, `crossbeam-channel`). No anomalies. No new-account maintainers on critical deps.

| Meta | Value |
|------|-------|
| Primary maintainer | ✅ sharkdp (13-yr account, 594 commits, 7,960 followers, at Astral) |
| Co-maintainer | ✅ tmccombs (13-yr account, 455 commits, 186 repos) |
| Third-core | ✅ tavianator (14-yr account, author of `bfs`) |
| Sockpuppet signals | ✅ None |
| Runtime dep maintainers | ✅ BurntSushi / dtolnay / clap-rs / nushell |
| Dependabot updates | ✅ Active (229 contributions, weekly flow) |

---

## 02A · Executable file inventory

> ℹ 1 compiled binary · ✓ 21 Rust source files · ✓ 14 attested release targets
>
> **`fd` ships exactly one compiled CLI binary**, named `fd`, built from 21 Rust source files and distributed across 14 pre-built platform targets per release. Every release artifact is signed with a sigstore SLSA Build L3 attestation; there are no install-time hooks, no preinstall scripts, no lifecycle helpers. The one `unsafe` block and all five `Command::new` call sites are accounted for in the table below — benign or by-design, not F8-actionable.

### Layer 1 — one-line summary

- ✓ **`fd` ships 1 compiled CLI binary (`fd`) built from 21 Rust source files.** Distribution: 14 pre-built platform targets (tarballs + `.deb`) per release, each signed with a sigstore SLSA Build L3 attestation; plus a `fd-find` crate on crates.io published manually by a maintainer (see F-crates.io). No install-time hooks, no preinstall scripts, no lifecycle helpers — users get a single self-contained binary that runs on invocation.

### Layer 2 — per-file runtime inventory

| File / Target | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `src/main.rs` | Binary entrypoint | CLI process | 2 `Command::new` — **by design** | None | Lines 392/421 probe for `gls`/`ls` to detect GNU ls for colour heuristics. Hard-coded binary names, no user input threaded in. |
| `src/exec/mod.rs` | User-exec engine | CLI process | 2 `Command::new` — **fd's `-x` flag, by design** | None | Lines 168/265 implement `fd -x` / `--exec` — runs the user's argv command against each match. Input from shell invocation, not file data. |
| `src/exec/command.rs` | Subprocess helper | CLI process | 1 `spawn` — **by design** | None | Line 77 wraps `cmd.spawn()`. Backs the `-x` implementation above. |
| `src/exec/job.rs` | Exec job queue | CLI process | None | None | Queue coordination for `-x` parallelism. No I/O beyond stdin/stdout. |
| `src/exit_codes.rs` | Exit-code utilities | CLI process | 1 `unsafe` block — **benign SIGINT restore** | None | Line 35: `unsafe { signal(SIGINT, SIG_DFL); }` then `raise(SIGINT)`. Idiomatic Rust/libc signal-handler pattern. No raw-pointer work, no `extern "C"`. |
| `src/walk.rs` | Directory traversal | CLI process | None | None | Uses the `ignore` crate (BurntSushi, same engine as ripgrep). |
| `src/filesystem.rs` | Path normalisation | CLI process | None | None | Uses `normpath`. Read-only fstat usage. |
| `src/cli.rs` | Argument parser | CLI process | None | None | `clap`-based. Large file by line count, structurally simple. |
| `src/filter/*` (size/owner/time/mod) | Filter predicates | CLI process | None | None | Match-time predicates. No I/O outside fstat. |
| `src/output.rs` | Output printer | CLI process | None | None | Colourised stdout writer. |
| `src/config.rs` | CLI config assembly | CLI process | None | None | Merges argv + `etcetera`-provided config paths. |
| `src/dir_entry.rs` | Directory entry wrapper | CLI process | None | None | Metadata accessor helpers. |
| `src/filetypes.rs`, `src/fmt/*`, `src/hyperlink.rs`, `src/regex_helper.rs` | Utility modules | CLI process | None | None | Pure helpers, no side effects. |
| Release: `fd-v10.4.2-TARGET.tar.gz` × 14 | Compiled binary tarballs | End-user shell | Attested | N/A | Signed via sigstore attestation in CI. Verifiable with `gh attestation verify --owner sharkdp`. |
| Release: `fd_10.4.2_ARCH.deb` × 7 | Debian packages | End-user package manager | Attested | N/A | Same attestation trail as tarballs. Produced by `scripts/create-deb.sh` in build job. |
| crates.io: `fd-find` v10.4.2 | Source crate | `cargo install` | Not CI-attested | N/A | Manual `cargo publish` — see F-crates.io. Crate source matches repo; gap is topological, not a live tampering concern. |

**Note on the `unsafe` block and the `Command::new` sites.** V2.3 Step A dangerous-primitive grep of `src/` surfaced exactly one `unsafe` block (`src/exit_codes.rs:35`, POSIX SIGINT default-handler restore) and five `Command::new` sites (two in `src/exec/mod.rs` and one in `src/exec/command.rs` implementing fd's `-x` flag from user argv; two in `src/main.rs` probing for `gls`/`ls` with hard-coded binary names). None of these are F8-actionable — the `unsafe` is the idiomatic way to interact with libc signals from Rust, and running user-supplied commands is fd's stated purpose. The Scanner Integrity conditional section is therefore not emitted for this report.

---

## 03 · Suspicious code changes

> ✓ 0 security-concerning PRs · ℹ 6 recent merges sampled
>
> **Recent PR activity is routine.** Sample of 6 most recent merges shows a docs tweak, three dependabot bumps merged by tmccombs, a tmccombs PR merged by tavianator, and one tmccombs self-merge on a CI attestation fix. One self-merge (PR #1941, attestation pipeline bug fix) — low risk because the PR had 1 review and is itself supply-chain hygiene work.

Sample: the 6 most recent merged PRs at scan time. None hit the flag-for-diff-review threshold. Dual review-rate metric: formal `reviewDecision` set on 2/6 = 33%; different author/merger on 5/6 = 83%; one self-merge on a reviewed attestation fix.

| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1953](https://github.com/sharkdp/fd/pull/1953) | Docs comment clarifying macOS install notes | Rohan5commit (NONE) | tmccombs | 1 review | Docs only. NONE-association contributor, but 1 review + different merger. |
| [#1952](https://github.com/sharkdp/fd/pull/1952) | Dependabot dep bump (workflow action) | dependabot[bot] | tmccombs | No formal decision | Routine bot bump. Different merger. |
| [#1951](https://github.com/sharkdp/fd/pull/1951) | Dependabot dep bump | dependabot[bot] | tmccombs | No formal decision | Routine bot bump. Different merger. |
| [#1950](https://github.com/sharkdp/fd/pull/1950) | Dependabot dep bump | dependabot[bot] | tmccombs | No formal decision | Routine bot bump. Different merger. |
| [#1946](https://github.com/sharkdp/fd/pull/1946) | tmccombs change merged by tavianator | tmccombs (MEMBER) | tavianator | No formal decision | Cross-merge pattern — maintainer A's work merged by maintainer B. Healthy. |
| [#1941](https://github.com/sharkdp/fd/pull/1941) | **[Security-adjacent]** Fix attestation pipeline bug | tmccombs (MEMBER) | tmccombs | 1 review | **Self-merge** on a supply-chain fix — but reviewed, and the work is positive-signal (fixing the attestation path itself). |

---

## 04 · Timeline

> ✓ 4 good · 🟡 2 neutral
>
> Six beats across the CLI's history. **The story is mature tool, supply-chain-aware maintainers** — created 2017, no security advisories ever filed, SECURITY.md added, SLSA attestations landed in October 2025, pipeline bugs fixed promptly. One cadence note: an 8-month gap between v10.3.0 and v10.4.0 makes "actively maintained" an amber rather than green signal.

- 🟡 **2017-05-09 · CREATED** — Repo created by sharkdp (David Peter). 8+ years ago at time of scan. fd predates sharkdp's move to Astral; now maintained collaboratively with tmccombs and tavianator as the effective three-person core.
- 🟢 **2017–2025 · STEADY SHIP** — Multiple major releases over 8 years. Zero security advisories ever filed, zero yanked releases, zero post-install incidents. API stability is high — users who learned fd in 2019 can still use the same flags today.
- 🟢 **2025-10-15 · ATTESTATIONS LAND** — PR #1809 "feat[release]: Add attestation for release artifacts" by tmccombs. This is the landmark supply-chain improvement — every release artifact gets a sigstore SLSA Build L3 attestation from this point forward. Consumers gain a cryptographic "came from this workflow" receipt.
- 🟢 **2025-11-09 · DISCLOSURE PATH** — PR #1829 "docs(security): clarify where to send vulnerability reports" by tmccombs. Tightens SECURITY.md language so a researcher who finds a bug has one unambiguous path (GitHub Security Advisories form, not email / issues / Discord).
- 🟢 **2026-03-07 / 2026-03-10 / 2026-03-25 · PIPELINE FIXES** — PR #1904 "fix(build): Fix attestation" and PR #1941 "Fix attest" — two bug-fixes to the attestation pipeline that tmccombs authored and merged. v10.4.0 ships 2026-03-07, v10.4.2 ships 2026-03-10. Note: v10.3.0 before this cluster was 2025-08-26 — an 8-month gap, the reason "actively maintained" scores amber not green.
- 🟡 **2026-04-16 · THIS SCAN** — HEAD at `a665a3bba9abc85e80c142a7dcdb8c356b12d9c9`, `master` branch, most recent merge is PR #1953 (docs macOS comment by Rohan5commit, merged by tmccombs). F0 fires as Warning: v10.4.2 is 37 days old, outside the 30-day Critical window; historical cadence supports "no recent release" as an honest read.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 8+ years | Created 2017-05-09 — mature CLI with an established public track record |
| Stars / Forks | 42,563 / 1,037 | 152 watchers, 180 open issues (feature requests / minor bugs, no security labels) |
| Primary maintainer | ✅ sharkdp (594 commits) | David Peter — account since 2013-04-20, 118 public repos, 7,960 followers. Now at @astral-sh (ruff/uv). |
| Co-maintainer | ✅ tmccombs (455 commits) | Account since 2012-10-12, 186 public repos. Landed SLSA attestations and SECURITY.md improvements. |
| Review rate (sample of 6) | ⚠ 2 formal / 6 any-review | ~33% formal. Cross-merge pattern provides practical pair-of-eyes. |
| Branch protection | ❌ None on `master` | API 404 + empty rulesets + empty rules/branches/master — authoritative |
| CODEOWNERS | ❌ None | Checked 4 standard locations. Owner is User (not Org), so no org-level rulesets either way. |
| Dependabot alerts | ℹ Unknown (token scope) | API returned 403 "You are not authorized" — distinct from zustand's "disabled for this repository" message. Version updates ARE active. |
| Security advisories | ✅ 0 filed, 0 open | Never an advisory-class incident in 8 years. SECURITY.md points at GitHub SA form. |
| Runtime dependencies | ✅ ~18 crates (all trusted Rust names) | BurntSushi / dtolnay / clap-rs / nushell / standard concurrency crates |
| Install-time hooks | ✅ None | No `build.rs` side effects beyond standard cargo build. Pre-built binaries have no post-install scripts. |
| Release attestations | ✅ Sigstore SLSA L3 | `actions/attest` signs every tarball + .deb. Verify with `gh attestation verify --owner sharkdp`. |
| CI workflows | 1 (CICD.yml, 309 lines) | 6 jobs (fmt / lint / MSRV / build / winget / crate_metadata). Zero `pull_request_target`. |
| Releases | ⚠ Irregular cadence | v10.4.2 (2026-03-10, current, 37d old), v10.4.0 (2026-03-07), v10.3.0 (2025-08-26 — **8-month gap**). Feature releases sporadic; dep bumps weekly. |
| Repo size | 2,396 KB | Tarball extraction: 54 files / 736 KB uncompressed |
| Crate | `fd-find` v10.4.2 | Binary name is `fd` but crates.io slot is `fd-find` (namespace conflict with older unrelated `fd` crate) |
| Topics | cli, command-line, filesystem, regex, rust, search, tool | Also: hacktoberfest, terminal |

---

## 06 · Investigation coverage

> 12/12 coverage cells verified · 1 amber (crates.io artifact)
>
> **All 12 C11 coverage cells verified.** 1/1 workflow file read (309 lines), full tarball extracted (54 files, 736 KB), 0 `pull_request_target`, 0 agent-rule files, 0 prompt-injection hits, 0 README paste-blocks, Windows surface limited to shell completion. One amber: per C6 Install/Artifact split, the Install path is 5/5 documented channels but the Artifact row is 2/3 — GitHub Releases and Winget are CI-attested, crates.io is manual (the F-crates.io finding).

| Check | Result |
|-------|--------|
| Tarball extraction | ✅ OK — 54 files, 736 KB — pinned to `a665a3bba9abc85e80c142a7dcdb8c356b12d9c9` at scan start |
| Workflow files read | ✅ 1 of 1 (309 lines) — `CICD.yml` fully inspected |
| Merged PRs scanned | ✅ 6 sampled, 0 anomalies — diffs read on PR #1953, #1946, #1941 |
| `pull_request_target` scan | ✅ Verified — 0 occurrences across the workflow |
| Executable files | ✅ Verified — 1 binary, 21 Rust source files |
| Monorepo scope | ✅ Verified — single-crate Cargo project, not a monorepo |
| README paste-scan (7.5) | ✅ Verified — 0 paste-blocks / 66 fenced blocks scanned. Commands are package-manager invocations, no curl-pipe-bash. |
| Agent-rule files | ✅ Verified — none (checked CLAUDE.md, AGENTS.md, .cursorrules, .claude/, .github/copilot-instructions.md, .mcp.json, .goosehints) |
| Prompt-injection scan (F8) | ✅ Verified — 0 matches / 0 actionable. Scanner Integrity section NOT emitted. |
| Distribution channels (F1, post-R3 C6) | ⚠ **Install path: 5 of 5 · Artifact: 2 of 3**. GitHub Releases ✓ (sigstore-attested), Winget ✓ (CI job), crates.io ✗ (manual cargo publish — see F-crates.io). Distro packages downstream; not in scope. |
| Windows surface coverage (F16) | ✅ Verified — completion only. Single `.ps1` is `autocomplete/_fd.ps1` (shell completion, not an installer). |
| Review-rate sample | ⚠ 6 recent merges sampled — 2/6 formal (33%), 5/6 cross-merger (83%), 1/6 self-merge |
| Commit pinned | `a665a3bba9abc85e80c142a7dcdb8c356b12d9c9` |

**Gaps noted:**

1. Artifact reproducibility not independently verified — we did not rebuild the fd binary from source and sha-diff against a release tarball. Attestation-verify succeeds (the GitHub Releases path is what its CI says it is), but byte-for-byte reproducibility against independent builds was not attempted.
2. Dependabot alerts surface returned 403 "You are not authorized" — scan token lacks the scope needed to enumerate vulnerability alerts for this repo. Distinct from a setting-level disable (which would say "disabled for this repository"). We did not separately enumerate the current dep-graph for unpatched CVEs; dep-update traffic suggests active monitoring by the maintainers.
3. Review-rate metric is based on a 6-PR sample, not the full merged-PR history.

---

## 07 · Evidence appendix

> ℹ 9 facts · ★ 2 priority
>
> 9 command-backed claims. **Skip ahead to items marked ★ START HERE** — the branch-protection-missing check and the sigstore-attestation-present check. Those two together are the falsification criteria for the Warning-with-partial-mitigation verdict.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — No branch protection, no rulesets, no CODEOWNERS on `master` (F0 / C20)

```bash
gh api "repos/sharkdp/fd/branches/master/protection"
gh api "repos/sharkdp/fd/rulesets"
gh api "repos/sharkdp/fd/rules/branches/master"
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do
  gh api "repos/sharkdp/fd/contents/$p" 2>&1 | head -1
done
gh api "users/sharkdp" -q .type
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
User
```

*Classification: Confirmed fact — all four governance signals are negative. 404 on branch protection is authoritative. Owner type is User so the org-level layer is N/A. Warning (not Critical) because release age is 37 days, safely outside the 30-day Critical window.*

#### ★ Evidence 2 — Sigstore SLSA L3 attestations on every release artifact (partial mitigation of F0)

```bash
grep -nE 'actions/attest|id-token|attestations:' \
  /tmp/scan-fd/fd-src/.github/workflows/CICD.yml

gh attestation verify --owner sharkdp \
  /tmp/fd-v10.4.2-x86_64-unknown-linux-gnu.tar.gz
```

Result:
```
uses: actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26 # v4
    id-token: write
    attestations: write
    contents: write

# gh attestation verify output:
Verification succeeded!
REPO            PREDICATE_TYPE                  WORKFLOW
sharkdp/fd      https://slsa.dev/provenance/v1  .github/workflows/CICD.yml@refs/tags/v10.4.2
```

*Classification: Confirmed fact — `actions/attest` is SHA-pinned to v4 and live verification against v10.4.2 succeeds. The attestation binds the artifact to `.github/workflows/CICD.yml@refs/tags/v10.4.2`, which is what makes this a meaningful SPOF-mitigation: an attacker would have to either corrupt the workflow file (visible in history) or compromise the CI runner to mint a matching attestation.*

### Other evidence supporting the Warning

#### Evidence 3 — Review-rate sample on 6 recent merges — 2 formal, 6 any-contact

```bash
gh pr list -R sharkdp/fd --state merged --limit 6 \
  --json number,title,author,mergedBy,reviewDecision,reviews \
  | jq '.[] | {pr: .number, author: .author.login, merger: .mergedBy.login,
               formal: .reviewDecision, any_review: ((.reviews|length) > 0)}'
```

Result (summarised):
```
PR#1953: author=Rohan5commit, merger=tmccombs, formal=APPROVED, any=true
PR#1952: author=dependabot[bot], merger=tmccombs, formal=null, any=false
PR#1951: author=dependabot[bot], merger=tmccombs, formal=null, any=false
PR#1950: author=dependabot[bot], merger=tmccombs, formal=null, any=false
PR#1946: author=tmccombs, merger=tavianator, formal=null, any=false
PR#1941: author=tmccombs, merger=tmccombs, formal=APPROVED, any=true  [SELF-MERGE]
Totals: 2/6 formal (33%), 5/6 cross-merger (83%), 1/6 self-merge (17%)
```

*Classification: Confirmed fact — 2 of 6 have reviewDecision = APPROVED. 5 of 6 have different author/merger. The one self-merge is a reviewed attestation-pipeline fix — low-concern pattern.*

#### Evidence 4 — Release age is 37 days — outside the 30-day Critical window

```bash
gh release list -R sharkdp/fd --limit 5 \
  --json tagName,publishedAt \
  | jq '.[] | "\(.tagName)  \(.publishedAt)"'
```

Result:
```
"v10.4.2  2026-03-10T..."
"v10.4.0  2026-03-07T..."
"v10.3.0  2025-08-26T..."
"v10.2.0  2025-06-xx..."
```

*Classification: Confirmed fact — v10.4.2 at 37 days old. 8-month gap between v10.3.0 and v10.4.0. Cadence is irregular, not monthly — which is why "no recent release" reads as an honest signal here rather than a boundary case.*

#### Evidence 5 — Workflow least-privilege permissions and `persist-credentials: false`

```bash
grep -nE '^permissions:|persist-credentials|contents:|id-token:' \
  /tmp/scan-fd/fd-src/.github/workflows/CICD.yml
```

Result:
```yaml
permissions:
  contents: read
# (root-level, everything inherits read-only)

# build job only:
    permissions:
      id-token: write
      contents: write
      attestations: write

# 5 occurrences of:
          persist-credentials: false
```

*Classification: Confirmed fact — root is `contents: read`, only `build` escalates and only for the attestation step. Every `actions/checkout` sets `persist-credentials: false`. Two independent hygiene patterns that close token-exfil and privilege-escalation-from-lint-step classes.*

#### Evidence 6 — Dangerous-primitive grep — one benign `unsafe` block, no network I/O

```bash
grep -rnE '\bunsafe\s*\{' /tmp/scan-fd/fd-src/src/
grep -rnE 'Command::new|\.spawn\(' /tmp/scan-fd/fd-src/src/
grep -rnE 'reqwest|ureq|hyper|TcpStream|UdpSocket|http::' /tmp/scan-fd/fd-src/src/
grep -rn '^use ' /tmp/scan-fd/fd-src/src/ | wc -l   # positive control
```

Result:
```
src/exit_codes.rs:35:        unsafe {
src/exec/mod.rs:168:        Command::new(&command[0])
src/exec/mod.rs:265:        Command::new(&self.cmd[0])
src/exec/command.rs:77:        cmd.spawn()
src/main.rs:392:        Command::new("gls")
src/main.rs:421:        Command::new("ls")
(no matches for reqwest/ureq/hyper/TcpStream/UdpSocket/http::)
~180   # positive control — grep tool working
```

*Classification: Confirmed fact — exactly one `unsafe` block (benign SIGINT restore), five `Command::new` sites (all by-design: `-x` flag + ls probe), zero network primitives. Positive control confirms the grep infrastructure is working.*

### Evidence supporting OK findings

#### Evidence 7 — Maintainers are long-tenured (sharkdp — 13 years, 7,960 followers, at Astral)

```bash
gh api "users/sharkdp" -q '{login,created_at,public_repos,followers,company}'
gh api "users/tmccombs" -q '{login,created_at,public_repos,followers}'
gh api "users/tavianator" -q '{login,created_at,public_repos,followers}'
```

Result:
```json
{"login":"sharkdp","created_at":"2013-04-20T...","public_repos":118,"followers":7960,"company":"@astral-sh"}
{"login":"tmccombs","created_at":"2012-10-12T...","public_repos":186,"followers":67}
{"login":"tavianator","created_at":"2012-04-30T...","public_repos":60,"followers":233}
```

*Classification: Confirmed fact — 13+ year accounts, substantial public repo counts, no sockpuppet signals. sharkdp's `company` field is "@astral-sh". tavianator authoring `bfs` while contributing to fd rules out "single cult of personality" risk.*

#### Evidence 8 — SECURITY.md is present and current

```bash
gh api "repos/sharkdp/fd/contents/SECURITY.md" -q '.content' \
  | base64 -d | head -20
```

Result:
```
# Security Policy

## Reporting a Vulnerability

Please use GitHub's private vulnerability reporting feature
(Security tab → Report a vulnerability)...

# (38 lines total, last updated 2025-11-09 via PR #1829)
```

*Classification: Confirmed fact — SECURITY.md exists, points at GitHub's private vulnerability reporting form, was recently updated. Zero published advisories against the repo in its 8-year history.*

#### Evidence 9 — Zero `pull_request_target` usage; workflow triggers are restricted

```bash
grep -rn 'pull_request_target' /tmp/scan-fd/fd-src/.github/workflows/
grep -nE '^on:|^  (push|pull_request|workflow_dispatch):' \
  /tmp/scan-fd/fd-src/.github/workflows/CICD.yml | head
```

Result:
```
(no matches for pull_request_target)
on:
  push:
    branches: [master]
    tags: ['*']
  pull_request:
  workflow_dispatch:
```

*Classification: Confirmed fact — the single workflow file uses `pull_request` (restricted, no secrets), `push` to `master` or tags, and `workflow_dispatch`. Zero `pull_request_target` usage rules out the PwnRequest class.*

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-16 · scanned master @ `a665a3bba9abc85e80c142a7dcdb8c356b12d9c9` (v10.4.2) · scanner V2.3-post-R3*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
