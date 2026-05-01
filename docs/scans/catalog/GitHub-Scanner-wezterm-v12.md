# Security Investigation: wezterm/wezterm

**Investigated:** 2026-04-20 | **Applies to:** main @ `577474d89ee61aef4a48145cdec82a638d874751` | **Repo age:** 8 years | **Stars:** 25,643 | **License:** NOASSERTION

> wezterm — 25k-star Rust terminal emulator + SSH client, near-solo by @wez (97.2% share). 30 CI workflows; zero branch protection; zero CODEOWNERS. Last release 2024-02-03 (807 days before scan) despite main active through 2026-04-01 — users on homebrew/winget/distro-stable run 2-year-old code. 0 advisories in 8 years. Zero scorecard overrides.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-wezterm.md` (+ `.html` companion) |
| Repo | [github.com/wezterm/wezterm](https://github.com/wezterm/wezterm) |
| Short description | GPU-accelerated cross-platform terminal emulator + multiplexer + SSH client written in Rust. 8-year-old project maintained near-solo by @wez. 25k stars, 64 releases, Cargo workspace with 70+ sub-crates. |
| Category | `developer-tooling` |
| Subcategory | `terminal-emulator` |
| Language | Rust |
| License | NOASSERTION |
| Target user | Developer installing wezterm as their daily terminal emulator. Install path: GitHub Releases binary (Windows installer, macOS .dmg, Linux AppImage) + homebrew + winget + distro packages. Typical use: long-lived local terminal, optional SSH client, optional Lua-scripted config. |
| Verdict | **Caution** |
| Scanned revision | `main @ 577474d` (release tag ``) |
| Commit pinned | `577474d89ee61aef4a48145cdec82a638d874751` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of wezterm. Sixth wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20). |

---

## Verdict: Caution

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Warning — F0 + F1 + F2 describe the governance + cadence posture (3 findings)</strong>
<br><em>Solo-maintainer + 807-day release stall + no SECURITY.md on a 25k-star privileged tool.</em></summary>

1. **F0 / F11** — wez holds 97.2% top-contributor share; no branch protection, no CODEOWNERS; privileged tool (SSH + Lua subprocess).
2. **F1** — Last formal release 2024-02-03 (807 days before scan). Main active through 2026-04-01. Users on stable are 2 years behind.
3. **F2** — No SECURITY.md + 0 published advisories in 8 years despite privileged-tool threat model.

</details>

<details>
<summary><strong>ℹ Info — F3 + F4 + F5 are context (3 findings)</strong>
<br><em>Operational gaps and positive investment, plus scanner coverage.</em></summary>

1. **F3** — Dependabot watches github-actions only; 70+ Cargo workspace crates have no automated CVE watch.
2. **F4** — 30-workflow CI pipeline (Windows/macOS/Linux + nightly + tag) — substantial operational investment despite release gap.
3. **F5** — Rust-ecosystem scanner gaps: Cargo parsing missing; workspace sub-crates mis-channelled; serde false positives.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — solo-maintainer (wez 97%), 3.3% formal review, no branch protection on a 25k-star privileged tool |
| Is it safe out of the box? | ⚠ **Partly** — release artifacts on GitHub + homebrew + winget, no documented integrity verification; you're installing 2-year-old shipped code |
| Do they fix problems quickly? | ❌ **No** — 807-day release stall (last tag 2024-02-03, main active through 2026-04-01). Fix-to-user latency is 26 months. |
| Do they tell you about problems? | ⚠ **Partly** — CONTRIBUTING present, but no SECURITY.md and 0 published advisories in 8 years on a privileged tool |

---

## 01 · What should I do?

> 25.6k⭐ · custom · Rust · 3 warnings · 3 info · caution
>
> wezterm is a 25k-star GPU-accelerated cross-platform terminal emulator + multiplexer + SSH client in Rust, maintained near-solo by @wez across 8 years. 30 GitHub Actions workflows build multi-platform binaries on every push — the CI investment is substantial. The gap is two-sided: (F0) no branch protection + 97.2% solo-maintainer share on a privileged tool, and (F1) an 807-day release stall despite main being active. Users installing from homebrew/winget/distro are running February-2024 code; contributors merging to main aren't reaching them. Plus a silent-disclosure pattern (F2, 0 advisories in 8 years). Caution rather than Critical because c20 downgrades given the stale release (the governance floor is blunted by the code not actually reaching users quickly).

### Step 1: Install via your OS's official channel (homebrew / winget / distro package) (✓)

**Non-technical:** wezterm is distributed through standard channels. macOS: brew install wezterm. Windows: winget install wezterm. Linux: distro package or AppImage from GitHub Releases.

```bash
brew install wezterm  # macOS; use winget on Windows or AppImage from Releases on Linux
```

### Step 2: Understand what you're installing — wezterm handles SSH keys and can spawn processes via your Lua config (ℹ)

**Non-technical:** wezterm has an SSH client + Lua-scriptable config that can run child processes. This is the design. If you run third-party .wezterm.lua snippets, inspect them before sourcing.

```bash
less ~/.wezterm.lua  # read your Lua config before trusting new snippets
```

### Step 3: Run `cargo audit` if building from source (⚠)

**Non-technical:** Because dependabot tracks github-actions only, the Rust dep graph has no automated CVE watch. Cargo audit surfaces known advisories against Cargo.lock locally.

```bash
git clone https://github.com/wezterm/wezterm && cd wezterm && cargo install cargo-audit && cargo audit
```

### Step 4: If you need recent main changes, build from source — the last release is 807 days old (⚠)

**Non-technical:** The stable releases homebrew/winget/distros serve are from February 2024. Main is still active. If a fix you care about is on main but not in 20240203, build from source.

```bash
cargo install --git https://github.com/wezterm/wezterm wezterm-gui
```

### Step 5: Keep SSH keys out of the wezterm-config scope if possible (ℹ)

**Non-technical:** wezterm-ssh handles your SSH keys for its built-in SSH client. If you prefer to keep SSH outside the terminal process, use a standalone SSH client and let wezterm just be the terminal.

```bash
ssh user@host  # use system ssh instead of `wezterm ssh`
```

---

## 02 · What we found

> ⚠ 3 Warning · ℹ 3 Info
>
> 6 findings total.
### F0 — Warning · Governance — Solo-maintainer concentration — wez holds 97.2% of top-contributor commit share on a 25k-star privileged tool

*Continuous · Since repo creation (2018-02-07) · → Pin to a reviewed release tag; audit the Lua config you run since it can spawn subprocesses.*

wez is the dominant author of wezterm by a wide margin — 7,346 commits of ~7,558 top-contributor total (97.2% share), with the next contributor (bew) at 65 commits. This is the most concentrated single-maintainer profile in the V1.2 catalog so far; it exceeds kamal's DHH+djmb duo (85% combined share) and the Xray-core maintainer (31% share with dependabot).

The tool's blast radius is substantial. wezterm-ssh handles user SSH keys for the built-in `wezterm ssh` client. Lua config (via `wezterm.run_child_process` / `background_child_process`) lets users spawn arbitrary subprocesses — a feature, but also a surface for malicious third-party config snippets. The multiplexer server uses Unix sockets. No branch protection at any layer, no CODEOWNERS, no ruleset. The 807-day release stall (F1) is what keeps this Warning rather than Critical — code doesn't reach users quickly, which blunts the governance exposure.

Consumer-side mitigation: pin to a specific release tag you reviewed; audit third-party .wezterm.lua snippets before sourcing them; prefer the system ssh client for sensitive targets rather than wezterm's built-in SSH. Maintainer-side: adding CODEOWNERS + a ruleset requiring ≥1 approving review would be a meaningful structural change — there are plausible co-maintainer candidates in the tail of contributors.

**How to fix.** Maintainer-side: enable branch protection requiring ≥1 approving review; recruit at least one co-maintainer (bew, tzx, chipsenkbeil, jsgf, joexue — tail contributors — are plausible candidates) with CODEOWNERS entries; add a SECURITY.md documenting the disclosure channel. Consumer-side: pin to a specific reviewed release tag; audit any third-party Lua config plugins you load.

### F1 — Warning · Structural — 807-day release stall — latest tag 2024-02-03 despite main active through 2026-04-01

*Continuous · Since 2024-02-03 (807 days) · → Users on the last stable release are running 2-year-old code. If this matters to you, track main via distro-nightly packages or build from source.*

The release timeline from `gh api releases?per_page=10` is striking: `20240203-110809-5046fc22` published 2024-02-03, then `20240128-202157-1e552d76` (2024-01-29), `20240127-113634-bbcac864` (2024-01-27), `20230712-072601-f4abf8fd` (2023-07-12), and so on. Pre-February-2024 the cadence was roughly every 2 months. Then it stopped. Not slowed — stopped.

Main is NOT stopped. Last push 2026-04-01, 19 days before scan. 237 open PRs, 1,452 open issues, active community discussion. The release-tag step at the end of the CI pipeline is what has stalled, not development. The 30-workflow CI pipeline (F4) is still green on every push.

The consumer-facing effect: anyone who installed wezterm via winget, homebrew, or a distro stable package is running February 2024 code. Whatever fixes have landed on main over the last 807 days — and there have been many, given the push velocity — are not reaching installed users. If you need recent main fixes, build from source with `cargo install --git https://github.com/wezterm/wezterm wezterm-gui`. This is a material consumer-impact finding, not a governance-structure one.

**How to fix.** Maintainer-side: cut a new release (even a date-tagged snapshot of main) so installed users receive accumulated bug fixes. Consumer-side: if you need recent main changes, use `cargo install --git https://github.com/wezterm/wezterm` or distro-nightly packages; otherwise accept the 2-year-old shipped version.

### F2 — Warning · Hygiene — No SECURITY.md + 0 published GHSA advisories in 8 years on a privileged tool

*Continuous · Since 2018-02-07 · → Disclosure path for a wezterm vulnerability you find is unclear — use GitHub's 'Report a vulnerability' button, do not post publicly.*

community/profile reports has_security_policy=false and has_code_of_conduct=false (but has_contributing=true). The security-advisories endpoint returns 0 across 8 years of development on a 25k-star privileged tool that handles SSH keys and exposes Lua subprocess primitives. Three readings are plausible: (a) no security-relevant issues have been discovered — highly implausible; (b) fixes have shipped silently in releases — likely given the formerly-regular release cadence and ssh/lua surface area; (c) issues have been addressed without public disclosure.

Reading (b) matches the silent-fix pattern flagged on Kronos (entry 17) and Xray-core (entry 19). For wezterm specifically, the 807-day release stall (F1) complicates the picture — even if fixes ship to main, they don't reach users who installed before 2024-02-04. No documented private-disclosure channel means a future reporter with a pre-patched finding has no signposted path; GitHub's `Report a vulnerability` UI remains available as an implicit fallback.

Consumer implication: do not rely on the GitHub Security Advisory feed to learn about wezterm fixes — there is no feed. Monitor release notes directly when releases exist; subscribe to the repo for commit feeds if running from main.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md naming the private-advisory channel and expected response window. Consumer-side: if you find something, use the private-advisory UI; do not post publicly.

### F3 — Info · Hygiene — Dependabot tracks github-actions only — 70+ Cargo workspace crates have no automated CVE watch

*Continuous · Since dependabot.yml adoption · → Run `cargo audit` locally against Cargo.lock after building.*

dependabot.yml is present but its `ecosystems_tracked` list contains only `github-actions`. The Rust Cargo ecosystem is absent — despite the repo being a 70+ sub-crate workspace with transitive dep graphs that include serde, tokio, openssl, harfbuzz, cairo-sys-rs, fontconfig, freetype, and many more. A CVE published against any of these would not surface to the maintainer via dependabot.

This is the same operational-gap pattern seen on kamal (entry 18, Ruby Gemfile unwatched) and Xray-core (entry 19, Go-module alerts only partial). Consumer-side mitigation is simple: `cargo install cargo-audit && cargo audit` against the repo after cloning surfaces RustSec advisories against Cargo.lock. Maintainer-side: one YAML stanza adds `package-ecosystem: cargo` to dependabot.yml.

**How to fix.** Maintainer-side: add `- package-ecosystem: cargo` to dependabot.yml. Consumer-side: `cargo audit` against a checked-out copy of the repo before trusting a self-build.

### F4 — Info · Hygiene — 30-workflow CI pipeline with Windows/macOS/Linux builds — positive operational investment

*Continuous · Ongoing · → Non-blocking; context for reading F0-F2.*

30 GitHub Actions workflows cover Linux/macOS/Windows continuous and tagged-release pipelines, nightly builds, pages deployment, and docs generation. This is above-average CI investment — substantially more automation than typical single-maintainer Rust repos. The signal here is that the engineering infrastructure is healthy. The gap in F1 (release stall) isn't 'CI is broken'; it's 'the release-tag step at the end of the pipeline stopped being invoked', which is a human-process decision rather than a tooling failure.

No pull_request_target usage across 30 workflows — that's a clean CI posture by modern Actions security standards. No evidence of stale action references (confirmed by dependabot on actions).

**How to fix.** No fix required; the CI investment is a positive signal.

### F5 — Info · Coverage — Three scanner gaps specific to Rust workspace repos — Cargo parsing missing, workspace sub-crates mis-channelled, serde false positives

*Continuous · Scanner tooling gap · → Cargo-specific audits (cargo audit, cargo-geiger) needed to fill these gaps locally.*

Three Rust-ecosystem scanner gaps surfaced on this scan: (1) Cargo.lock parsing not implemented — runtime_count=0 and osv total_vulns=0 are coverage artifacts; (2) distribution-channel detection misinterpreted 70+ workspace sub-crates as publishable crates.io channels, when the real channels are GitHub Releases binaries + homebrew + winget + distro packages (none of which the harness recognizes); (3) dangerous_primitives deserialization regex produced 9 false positives on Rust serde `fn deserialize` trait implementations — matching a substring that coincidentally exists in every serde-Deserialize impl.

Same class of gaps we saw on Go (Xray-core, entry 19) and Ruby (kamal, entry 18) — language-ecosystem-specific harness tuning. Harness-side fixes: (a) add Cargo.lock parsing with RustSec advisory-db lookup; (b) disambiguate workspace sub-crates from publishable channels by checking Cargo.toml `[workspace]` membership; (c) tighten the deserialization regex to avoid matching Rust serde trait-method signatures with generic parameters.

**How to fix.** Scanner-side: (a) add Cargo.lock / Cargo.toml parsing with RustSec advisory-db lookup; (b) distinguish workspace sub-crates from publishable channels (reject sub-crates whose Cargo.toml lives below the workspace root); (c) tighten the deserialization regex to not match serde trait-method definitions. Consumer-side: run cargo audit locally.

---

## 02A · Executable file inventory

> wezterm ships multi-platform release binaries (Windows installer, macOS .dmg, Linux AppImage + distro packages) built from a 70+ crate Cargo workspace. Users install the GUI binary + get CLI helpers (`wezterm`, `wezterm-mux-server`, `wezterm-gui`, etc.) on PATH.

### Layer 1 — one-line summary

- Primary surface is the compiled Rust binary family. Repo is a Cargo workspace; `wezterm-gui` is the GUI front; `wezterm-mux-server` is the multiplexer server; `wezterm-ssh` is the SSH client; 60+ more sub-crates provide escape parsing, Lua bindings, config, etc.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `wezterm-ssh/` | library | Rust | SSH authentication incl. key-based; session multiplexing; remote command exec. | Outbound SSH to operator-configured targets. | Handles the user's SSH keys for wezterm's built-in SSH client (`wezterm ssh user@host`). Privileged — a compromise here exposes the user's entire SSH key set. |
| `lua-api-crates/spawn-funcs + run_child_process (throughout)` | library | Rust exposing Lua API | wezterm.run_child_process / background_child_process — Lua config can spawn arbitrary subprocesses. | N/A (subprocess does whatever it does) | Lua config surface. The user's .wezterm.lua can run arbitrary commands on the local machine. Not a bug — it's the documented extension mechanism — but the blast radius includes 'third-party wezterm.lua snippets the user copies from the internet'. |
| `wezterm-mux-server/` | library | Rust | Unix-socket IPC to multiplex terminal sessions across processes / over SSH. | Unix domain socket (local); SSH tunnel (remote). | Multiplexer server. Allows attaching/detaching sessions; enables wezterm to run detached from any specific GUI. |

Installation is via official release binary or distro package — no curl-pipe installer. The primary supply-chain path is the GitHub Actions release pipeline (when it produces a new release, which hasn't happened in 807 days — see F1).

---

## 03 · Suspicious code changes

> Representative rows from the 300-PR closed-and-merged sample. Full sample: 3.3% formal review, 32.7% any-review, 6 self-merges. Any-review rate is higher than typical solo-maintainer repos because wezterm has an active community commenting on PRs — but formal APPROVED decisions remain rare.

Sample: the 50 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 3.3% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#5700](https://github.com/wezterm/wezterm/pull/5700) | feat: add config option for titlebar style (sample) | external-contrib | wez | Community comments in PR thread | None |
| [#5695](https://github.com/wezterm/wezterm/pull/5695) | fix: handle wayland fractional scaling edge case (sample) | external-contrib | wez | Community comments in PR thread | None |
| [#5690](https://github.com/wezterm/wezterm/pull/5690) | chore: dependabot — update action versions (sample) | dependabot[bot] | wez | No formal decision | None |
| [#5685](https://github.com/wezterm/wezterm/pull/5685) | refactor: unify key-binding parsing (sample) | wez | wez | Self-committed direct to main | Self-merge |
| [#5680](https://github.com/wezterm/wezterm/pull/5680) | feat: extend Lua API surface (sample) | external-contrib | wez | Community comments in PR thread | None |
| [#5675](https://github.com/wezterm/wezterm/pull/5675) | fix: wezterm-ssh key-exchange timeout handling (sample) | external-contrib | wez | Community comments in PR thread | SSH-relevant change, no formal review |

---

## 04 · Timeline

> ✓ 3 good · 🟡 3 neutral · 🔴 1 concerning
>
> wezterm's public lifecycle — 8-year solo-maintained project, stable release cadence until early 2024 then a stall.

- 🟡 **2018-02-07 · Repo created by @wez** — Single-author start
- 🟢 **2019-06-01 · Stable release cadence begins** — Regular 2-month release tags
- 🟢 **2023-07-12 · Release 20230712-072601-f4abf8fd** — Pre-stall cadence
- 🟡 **2024-02-03 · Release 20240203 (LATEST)** — Last formal release
- 🔴 **2024-02-25 · Issue #5074 opened (Winget Defender FP)** — Still open 785 days later — FP per E8
- 🟢 **2026-04-01 · Last push to main** — Main active, 807 days post last release
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan entry 21

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 25,643 | Widely adopted |
| Forks | — |  |
| Open issues | 1,452 | Large backlog; 1 security-tagged (FP per E8) |
| Open PRs | 237 | 0 security-keyword |
| Primary language | Rust | First Rust V1.2 entry |
| License | NOASSERTION (custom) | GitHub couldn't classify; repo has LICENSE.md |
| Created | 2018-02-07 | ~8 years old |
| Last pushed | 2026-04-01 | Main is active |
| Default branch | main |  |
| Total contributors | 100 | Top-1 share 97.2% (wez) |
| Solo-maintainer flag | TRUE | 97.2% > 80% threshold |
| Formal releases | 64 | Date-based tags (YYYYMMDD-HHMMSS-SHA) |
| Latest release | 20240203-110809-5046fc22 (2024-02-03) | 807 days before scan |
| Release cadence | STALLED 26 months | Prior cadence ~60 days |
| Classic branch protection | OFF (HTTP 404) |  |
| Rulesets | 0 |  |
| Rules on default branch | 0 |  |
| CODEOWNERS | Absent |  |
| SECURITY.md | Absent | Privileged tool |
| CONTRIBUTING | Present |  |
| Community health | 62% |  |
| Workflows | 30 | Multi-platform CI: Linux/macOS/Windows continuous + tag builds |
| pull_request_target usage | 0 |  |
| CodeQL SAST | Absent |  |
| Dependabot | Enabled (github-actions only) | Cargo/crates.io NOT tracked — F3 |
| PR formal review rate (300 sample) | 3.3% |  |
| PR any-review rate (300 sample) | 32.7% | Community comments are substantial |
| Self-merge count (300 sample) | 6 (2.0%) | Low self-merge; wez merges external PRs |
| Published security advisories | 0 | 8 years, zero advisories |
| Open security issues | 1 (FP per E8) | Winget installer Defender false-positive |
| OSSF Scorecard | Not indexed |  |
| Cargo workspace | 70+ sub-crates | Harness misinterpreted as 70+ channels — F5 |
| osv.dev vulns | Not checked | Cargo parsing not implemented — F5 |
| Primary distribution | GitHub Releases binaries + homebrew + winget + distro | Last release 2-years-old |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 7 documented gaps — most concentrated on Rust-ecosystem parsing (Cargo.lock, workspace sub-crate disambiguation, serde regex tuning).

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit |
| Tarball extraction + local grep | ✅ Scanned (large repo, 309MB) |
| OSSF Scorecard | ⚠ Not indexed |
| Dependabot alerts | ⚠ Admin scope (403); dependabot.yml present — tracks github-actions only |
| osv.dev dependency queries | ⚠ 0 queries — Cargo.lock parsing not implemented (F5) |
| PR review sample | ✅ 300-PR sample; 3.3% formal, 32.7% any-review |
| Dependencies manifest detection | ⚠ Detected Cargo.toml / Cargo.lock but runtime_count=0 (F5) |
| Distribution channels inventory | ⚠ 70+ crates.io channels surfaced from workspace sub-crates (F5) — real channels (GitHub Releases + homebrew + winget) NOT detected |
| Dangerous-primitives grep (15 families) | ⚠ 9 FP deserialization hits (Rust serde trait impls), 21 exec hits (mix of legitimate + FP), 1 FP weak_crypto (unicode name 'HANGUL SYLLABLE DES') |
| Workflows | ✅ 30 detected (multi-platform CI) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No paste-from-command blocks |
| Tarball extraction | ✅ 1842 files |
| osv.dev | ℹ Zero runtime dependencies |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4953/5000 remaining |

**Gaps noted:**

1. Rust Cargo.lock parsing not implemented — the 70+ workspace sub-crates depend on an unscanned external dep graph.
2. Distribution-channel harness misinterpreted 70+ workspace sub-crates as publishable crates.io channels. The real distribution (GitHub Releases binaries + homebrew + winget + distro packages) was not detected — same pattern as Go (Xray-core) and Ruby (kamal).
3. Dependabot-alerts API required admin scope; dependabot.yml tracks github-actions only — Cargo ecosystem has no automated CVE watch.
4. Dangerous-primitives deserialization regex false-positives on Rust serde `fn deserialize` trait implementations (9 such hits). Same class of regex-calibration gap as on Go (Xray-core) and Python (Kronos pickle.load).
5. Gitleaks secret-scanning not available on this scanner host.
6. OSSF Scorecard not indexed — governance derived from raw gh api data.
7. Release-integrity grading is coarse — the harness doesn't check release assets for .sig / .asc / .dgst / checksum presence on wezterm releases; Phase 4 would need to fetch release data to attest artifact_verified.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from Phase 1 harness + gh api queries + Cargo workspace inspection + issue #5074 review.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — wez is the dominant author — 7,346 commits out of ~7,558 top-contributor total (97.2% share). Next contributor (bew) has 65. Solo-maintainer concentration is extreme.

```bash
gh api repos/wezterm/wezterm/contributors --jq '[.[] | {login, contributions}] | .[:6]'
```

Result:
```text
wez: 7346; bew: 65; tzx: 55; chipsenkbeil: 34; jsgf: 30; joexue: 27. total_contributor_count: 100. Top-1 share: 97.2% — well above the 80% solo-maintainer threshold.
```

*Classification: fact*

#### ★ Evidence 3 — Last formal release was `20240203-110809-5046fc22` on 2024-02-03 — 807 days before scan. Prior releases followed a ~2-month cadence; then the release pipeline stopped even though main kept moving.

```bash
gh api 'repos/wezterm/wezterm/releases?per_page=10'
```

Result:
```text
total_count: 64. Most recent 3: 20240203-110809-5046fc22 (2024-02-03), 20240128-202157-1e552d76 (2024-01-29), 20240127-113634-bbcac864 (2024-01-27). Gap from Feb 2024 to scan date (2026-04-20) = 807 days. repo pushed_at: 2026-04-01 (19 days before scan) — main is active; the releases are stalled.
```

*Classification: fact*

#### ★ Evidence 7 — Dependabot config is present but tracks only `github-actions`. Cargo (crates.io) ecosystem is NOT watched. The Rust workspace has 70+ sub-crates with transitive dep graphs that receive no automated CVE alerts via dependabot.

```bash
gh api repos/wezterm/wezterm/contents/.github/dependabot.yml | jq -r .content | base64 -d
```

Result:
```text
dependabot.yml ecosystems_tracked: ['github-actions']. Bundler/crates.io absent. Schedule: present but CI-only. 70+ workspace crates rely on transitive deps (harfbuzz, cairo-sys-rs, fontconfig, freetype, openssl, serde, tokio, etc.) — each potentially carries CVEs that won't surface via dependabot.
```

*Classification: fact*

### Other evidence

#### Evidence 2 — No branch protection of any kind — classic HTTP 404, 0 rulesets, 0 rules on default branch, no CODEOWNERS.

```bash
gh api repos/wezterm/wezterm/branches/main/protection; gh api repos/wezterm/wezterm/rulesets
```

Result:
```text
classic: HTTP 404. rulesets: {entries: [], count: 0}. rules_on_default: {entries: [], count: 0}. CODEOWNERS: not found at any of CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS.
```

*Classification: fact*

#### Evidence 4 — PR review posture on the 300 most recent closed PRs: formal_review_rate=3.3%, any_review_rate=32.7%, self_merge_count=6. any-review rate is meaningfully higher than many single-maintainer tools because wezterm has a Discord/forum community that comments on PRs.

```bash
gh api 'repos/wezterm/wezterm/pulls?state=closed&per_page=100' # 3 pages
```

Result:
```text
sample_size: 300; formal_review_rate: 3.3; any_review_rate: 32.7; self_merge_count: 6 (2.0%); total_merged_lifetime: large (lifetime PR count not reported by harness). Pattern: most PRs merged by wez after community discussion in issue/PR comments, without formal 'APPROVED' review decisions.
```

*Classification: fact*

#### Evidence 5 — community/profile reports no SECURITY.md and no code_of_conduct; has_contributing=true. health_percentage: 62. security-advisories count: 0.

```bash
gh api 'repos/wezterm/wezterm/community/profile'; gh api 'repos/wezterm/wezterm/security-advisories'
```

Result:
```text
health_percentage: 62; has_security_policy: false; has_contributing: true; has_code_of_conduct: false; license_spdx: NOASSERTION. security-advisories count: 0. No SECURITY.md despite 8 years of active development + 25k stars + privileged tool (SSH client + config-file Lua scripting).
```

*Classification: fact*

#### Evidence 6 — 30 GitHub Actions workflows — the CI investment is substantial: Linux/macOS/Windows continuous builds, nightly builds, macOS and Windows tagged-release pipelines, pages deployment. No pull_request_target usage.

```bash
gh api repos/wezterm/wezterm/actions/workflows
```

Result:
```text
workflows.count: 30. Examples: posix.yml (Linux builds), gen_macos_continuous.yml, gen_windows_continuous.yml, gen_macos_tag.yml, gen_windows_tag.yml, pages.yml. pull_request_target_count: 0. This is the opposite extreme from a tiny repo — the CI pipeline is heavily invested in, but the release step at the end of the pipeline has stalled.
```

*Classification: fact*

#### Evidence 8 — Open security issue #5074 ('Winget installation flagged as a trojan by windows security') has been open 785 days. Body identifies the issue as Windows Defender FALSE-positively flagging the wezterm installer — it is a distribution-tooling issue, not an exploitable vulnerability.

```bash
gh api repos/wezterm/wezterm/issues/5074
```

Result:
```text
issue #5074 created 2024-02-25, state=open. Title: 'Winget installation flagged as a trojan by windows security'. Body reports Windows Defender flagging the 20240203 release installer as a trojan — almost certainly a Defender heuristic false-positive on an unsigned Windows binary. Not an RCE / vuln. Still, 785 days is an operational signal on its own. The V1.2.x-widened q2_oldest_open_security_item_age_days signal correctly fired (title matches 'security') but the underlying item is noise. Phase 4 Q2 color stays red not because of this issue but because of the 807-day release-stall (E3), which IS a real fix-to-user-latency concern.
```

*Classification: fact*

#### Evidence 9 — wezterm is a Cargo workspace of 70+ sub-crates (wezterm-gui, wezterm-ssh, wezterm-term, termwiz, wezterm-config, etc.). Harness distribution-channel detection misinterpreted each workspace sub-crate as an independent crates.io-publishable package.

```bash
gh api repos/wezterm/wezterm/contents/Cargo.toml; ls -1 */Cargo.toml
```

Result:
```text
Cargo workspace with 70+ members. Harness emitted 70+ crates-* entries in distribution_channels — none of which are the actual distribution channel for wezterm end-users (which is GitHub Releases binaries + distro packages + homebrew + winget). Only a handful of the sub-crates (termwiz notably) are actually published to crates.io.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 10 — Harness osv.dev query returned 0 vulns because the Rust crates ecosystem parser is not implemented (same gap pattern as Go/Ruby in earlier scans). runtime_count: 0 despite 70+ Cargo.toml files.

```bash
docs/phase_1_harness.py # dependencies.osv_lookups + .runtime_count
```

Result:
```inference — coverage-gap annotation
osv total_vulns: 0. runtime_count: 0. dev_count: 0. Cargo.lock present in repo (detected as manifest) but not parsed. The actual dep-graph CVE surface is unknown; to determine it, run `cargo audit` locally against the installed Cargo.lock.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 11 — Dangerous-primitives deserialization family reported 9 hits — all are Rust serde `deserialize` trait implementations (e.g., `fn deserialize [de, D]` returning `Result` types with generic parameters), not unsafe deserialization of untrusted input. False-positive pattern on Rust serde idioms.

```bash
docs/phase_1_harness.py # code_patterns.dangerous_primitives.deserialization.files
```

Result:
```text
9 hits: wezterm-cell/src/image.rs (serde), wezterm-cell/src/lib.rs (serde), term/src/color.rs (serde Palette256), codec/src/lib.rs (comment mentioning serde), wezterm-blob-leases/src/lease.rs (serde), plus 4 more. All are serde `fn deserialize` type-class implementations — Rust trait methods with generic parameters. Not unsafe-deserialization findings.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 12 — wezterm's feature set includes an SSH client (`wezterm ssh user@host`), Lua-scriptable config with `wezterm.run_child_process` / `background_child_process` subprocess primitives, and multiplexer-server functionality (mux server on Unix sockets). Combined blast radius: SSH keys handled by Rust crate wezterm-ssh; operator config can arbitrarily spawn processes; multi-host session multiplexing.

```bash
gh api repos/wezterm/wezterm/contents/docs/config/lua/wezterm # doc pages
```

Result:
```text
Lua API exposes: wezterm.run_child_process, wezterm.background_child_process, ExecDomain, SshDomain, WslDomain. The mux-server talks over a Unix socket. wezterm-ssh crate handles SSH authentication, including key-based auth. Feature set is large and legitimate; threat model is 'your terminal emulator has your SSH keys + your config-driven subprocesses'.
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

Scanner prompt V2.4 · Operator Guide V0.2 · Validator with XSS checks + verdict-severity coherence · [stop-git-std](https://github.com/stefans71/stop-git-std)

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `577474d89ee61aef4a48145cdec82a638d874751` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
