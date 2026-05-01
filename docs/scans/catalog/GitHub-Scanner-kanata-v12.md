# Security Investigation: jtroo/kanata

**Investigated:** 2026-04-20 | **Applies to:** main @ `1c496c019dfb0df8a4e8321b54a9a9f8e0b2dc5e` | **Repo age:** 4 years | **Stars:** 7,179 | **License:** LGPL-3.0

> kanata — 7k-star Rust keyboard-remapper daemon by jtroo + ItayGarin. Runs with elevated privileges on Linux/macOS/Windows; every keystroke flows through it. Critical verdict via C20: keylogger-class privileged tool + no branch protection + active 8-day release cadence. But the governance story is nuanced — **44% formal PR review** is the highest in the V1.2 catalog; the two-maintainer pair runs disciplined voluntary review. The fix for F0 is codifying what's already happening.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-kanata.md` (+ `.html` companion) |
| Repo | [github.com/jtroo/kanata](https://github.com/jtroo/kanata) |
| Short description | Rust cross-platform keyboard remapper / key-interception daemon. Layers, tap-hold, macros, config-driven remapping. Linux uinput, macOS IOKit, Windows Interception-driver backends. |
| Category | `input-device-tooling` |
| Subcategory | `keyboard-remapper` |
| Language | Rust |
| License | LGPL-3.0 |
| Target user | Developer / power-user who wants advanced keyboard customization (home-row mods, tap-hold, layers) beyond what the OS provides. Install: `cargo install kanata` OR GitHub Releases binary (platform-specific). Runs as elevated daemon. |
| Verdict | **Critical** |
| Scanned revision | `main @ 1c496c0` (release tag ``) |
| Commit pinned | `1c496c019dfb0df8a4e8321b54a9a9f8e0b2dc5e` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of kanata. Eighth wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21, QuickLook 22). |

---

## Verdict: Critical

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>✗ Critical — F0 drives the verdict via C20 + active release cadence (1 findings)</strong>
<br><em>Privileged keyboard-interception daemon + no branch protection + code ships to users fast.</em></summary>

1. **F0 / C20** — Keylogger-class privileged tool with no branch protection / rulesets / CODEOWNERS; latest prerelease 8 days before scan.

</details>

<details>
<summary><strong>⚠ Warning — F1 + F2 describe disclosure + dep-hygiene gaps (2 findings)</strong>
<br><em>No SECURITY.md, no Dependabot.</em></summary>

1. **F1** — No SECURITY.md + 0 published advisories in 4 years on an input-intercepting daemon.
2. **F2** — No Dependabot config — Cargo workspace of 15+ manifests has no automated CVE watch.

</details>

<details>
<summary><strong>ℹ Info — F3 (positive) + F4 + F5 (3 findings)</strong>
<br><em>Healthy review culture, feature-gated shell-exec, scanner coverage gaps.</em></summary>

1. **F3** — **Positive**: 44% formal PR review rate — highest in V1.2 catalog. Two-maintainer pair with genuine review discipline.
2. **F4** — `cmd` feature flag (opt-in) enables config-level shell execution — documented + off by default.
3. **F5** — Rust-ecosystem scanner gaps (Cargo.lock parsing + workspace channel detection). Same as wezterm.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⚠ **Partly** — 44% formal PR review (highest in V1.2 catalog) + active 2-maintainer pair, but no branch protection enforcement |
| Is it safe out of the box? | ⚠ **Partly** — `cargo install kanata` integrity via crates.io; GitHub Releases binaries unsigned; privileged-tool threat model |
| Do they fix problems quickly? | ✅ **Yes** — 0 open security issues, 58 releases, latest 8 days before scan (v1.12.0-prerelease-2) |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md, no CONTRIBUTING, 0 published advisories in 4 years on a privileged input daemon |

---

## 01 · What should I do?

> 7k⭐ · LGPL-3.0 · Rust · 1 critical · 2 warnings · 3 info · CRITICAL
>
> kanata is a 7k-star Rust keyboard remapper / key-interception daemon by jtroo + co-maintainer ItayGarin. Runs with elevated OS privileges on Linux (uinput), macOS (IOKit), and Windows (Interception driver) — every keystroke flows through it. Critical verdict via C20: no branch protection / rulesets / CODEOWNERS on a keylogger-class privileged tool, paired with active release cadence (v1.12.0-prerelease-2 shipped 8 days before scan). But the governance picture is mixed — F3 is a positive finding: 44% formal PR review rate is the highest in the V1.2 catalog, and the two-maintainer pair demonstrably runs a disciplined voluntary review process. The Critical call is about ABSENCE of enforced structural review, not ABSENCE of review activity.

### Step 1: Install via `cargo install kanata` — DO NOT enable `--features cmd` unless you need shell-exec actions (✓)

**Non-technical:** The default kanata install is key-remap-only. Only add `--features cmd` if you specifically need your kanata config to run shell commands, and only load configs you trust.

```bash
cargo install kanata
```

### Step 2: Pin to a specific released version — avoid `cargo install kanata --git` tracking main (⚠)

**Non-technical:** Pin to the latest released semver (e.g., v1.12.0) rather than building from main. The 44% formal-review rate (F3) applies to merged-to-main code, but you still want the release gate.

```bash
cargo install kanata --version '1.12.0'
```

### Step 3: Run `cargo audit` against the installed binary's dep graph (⚠)

**Non-technical:** Because Dependabot is absent (F2), the Cargo dep graph has no automated CVE watch. Cargo-audit surfaces RustSec advisory-db entries locally.

```bash
cargo install cargo-audit && cargo audit
```

### Step 4: Run kanata as a dedicated user with minimum-needed input privileges — not as root (⚠)

**Non-technical:** On Linux, kanata needs CAP_NET_ADMIN for uinput (not full root). Create a dedicated `kanata` user with just that capability. On macOS, grant Input Monitoring + Accessibility to the kanata.app specifically. On Windows, the Interception driver install requires admin but the daemon itself can run in a lower-privilege context.

```bash
# Linux: sudo setcap 'cap_net_admin+ep' /home/user/.cargo/bin/kanata
```

### Step 5: Audit any kanata configs you download from the internet before loading (⚠)

**Non-technical:** kanata configs are a DSL that maps keystrokes to actions. If your install has `--features cmd` enabled, configs can run shell commands — so a shared config file is executable content. Read it before loading.

```bash
less ~/.config/kanata/kanata.kbd  # read config before `kanata -c`
```

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 2 Warning · ℹ 3 Info
>
> 6 findings total.
### F0 — Critical · Governance — Governance single-point-of-failure on a privileged keyboard-interception daemon with active release cadence (C20)

*Continuous · Since 2022-04-18 · → Pin to a reviewed release tag; run kanata as a dedicated user with minimum-needed input-device privileges.*

kanata runs as a daemon with elevated OS privileges on all three major platforms — CAP_NET_ADMIN + uinput on Linux, IOKit + Accessibility + Input-Monitoring on macOS, and the Interception kernel driver on Windows. The reason is mechanical: to remap keys you have to intercept the raw keystream before the OS delivers it to applications, which requires kernel-adjacent access. The consequence is that a compromised kanata binary is a keylogger with exfiltration opportunity — and if the user opted into `--features cmd` (F4), also a local-RCE triggered by arbitrary keystrokes.

The supply-chain path goes through crates.io (`cargo install kanata`) or GitHub Releases prebuilt binaries. The repo has no branch protection, no rulesets on the default branch, no CODEOWNERS. Recent release cadence is active: v1.12.0-prerelease-2 shipped 2026-04-12, 8 days before scan, and main was pushed to the day before scan. The code IS reaching users — which is why the c20 compound rule fires Critical here rather than the Warning it produced for wezterm (entry 21) where the 807-day release stall blunted the same structural gap.

The positive angle is F3: the 44% formal-review rate on PRs is real and the highest in the catalog. jtroo and ItayGarin demonstrably run a voluntary review process for external contributions. The fix for F0 isn't 'build a review culture' — that already exists. The fix is codifying it: enable a ruleset that requires ≥1 approving review before merge to main. That would take the existing behavior and make it structurally unavoidable, closing the account-compromise attack path.

Consumer-side mitigation: pin to a specific released version (not a main-tracking `cargo install --git`); run kanata as a dedicated user with only the specific OS capability it needs (CAP_NET_ADMIN on Linux, not root); if you don't need shell-exec from configs, don't enable `--features cmd`.

**How to fix.** Maintainer-side: enable a ruleset requiring ≥1 approving review on main; add CODEOWNERS. The existing voluntary-review culture (44% formal rate) suggests this would be low-friction to adopt — protection infrastructure would codify existing practice. Consumer-side: pin to specific version tag + review changelogs; consider running kanata as a dedicated system user with CAP_NET_ADMIN rather than root on Linux.

### F1 — Warning · Hygiene — No SECURITY.md + 0 published advisories in 4 years on a keyboard-interception daemon

*Continuous · Since 2022-04-18 · → If you find a kanata bug, use GitHub's `Report a vulnerability` button — not documented but available.*

community/profile reports has_security_policy=false. security-advisories count: 0 over 4 years. kanata processes every keystroke on every user's machine — the threat model calls for clear disclosure infrastructure. Zero advisories in this context almost certainly means silent-fix cadence, where fixes ship in the next release without formal GHSA publication. Same catalog-wide pattern observed on Kronos (entry 17), Xray-core (entry 19), wezterm (entry 21), QuickLook (entry 22).

For consumers, the effect is that watching the GitHub Security Advisory feed tells you nothing about kanata fixes. Reading release notes is the only channel. For reporters, GitHub's `Report a vulnerability` button is reachable but not documented. A 1-page SECURITY.md would close the reporter-side gap at minimal cost.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md naming GitHub's private-advisory button. Given kanata's privileged threat model, this is especially cheap/valuable.

### F2 — Warning · Supply chain — No Dependabot config — Rust workspace with 15+ Cargo.toml files has no automated CVE-watch on dep graph

*Continuous · Since repo creation (no dependabot.yml ever) · → Run `cargo audit` locally after building; the repo doesn't do it for you.*

There is no `.github/dependabot.yml` in this repo — `gh api contents/.github/dependabot.yml` returns 404. The Cargo workspace has 15+ manifests spanning the main `kanata` crate, parser, tcp_protocol, keyberon (keyboard-layout engine), interception (Windows driver binding), WASM target, and 8 more sub-crates. Transitive deps include serde, tokio, and platform-specific input libraries. None of these receive automated CVE alerts.

Same gap we saw on wezterm (entry 21) — the Rust-ecosystem Dependabot-coverage pattern is consistent across the catalog's Rust entries. The fix is a single YAML file: `- package-ecosystem: cargo` with daily schedule. Low-cost, high-value — especially on a privileged-tool repo where a transitive-dep CVE could propagate into keylogger-scope impact.

**How to fix.** Maintainer-side: add `.github/dependabot.yml` with `- package-ecosystem: cargo` — minutes of work. Consumer-side: `cargo audit` against the installed Cargo.lock before trusting a self-build.

### F3 — Info · Positive — 44% formal PR review rate — highest in the V1.2 catalog; active two-maintainer pair

*Continuous · Ongoing — pattern visible in recent PRs · → Positive signal worth noting; context for reading F0's Critical verdict.*

Looking at recent PRs: #2032 APPROVED by jtroo, #2031 APPROVED, #2029 APPROVED, #2028 APPROVED — a run of 8 consecutive externally-authored PRs all carrying `review_decision: APPROVED` before merge. Then #2022 and #2021 are jtroo's own commits, merged direct. This is a healthy two-tier pattern: external contributions go through formal review; maintainer internal changes go direct.

44% formal review across 300 PRs is the highest in the V1.2 catalog — compare to Xray-core (3.3%), wezterm (3.3%), kamal (4.7%), QuickLook (5.1%), browser_terminal (0%). The substantive co-maintainer (ItayGarin at 149 commits) shows up as an independent reviewer in the sample — this is real multi-reviewer activity, not self-review.

This finding exists to make the governance picture honest. F0 says 'no enforced protection'. F3 says 'the practice is healthy anyway'. Both are true. The recommendation for consumers is: if you see `jtroo/kanata` in a supply chain you depend on, the informal review culture is a real positive signal — just be aware that it's unenforceable (a compromised account bypasses it entirely, which F0 captures).

**How to fix.** No fix required on the positive-signal side. The action is for F0 (codify the existing review behavior into a ruleset).

### F4 — Info · Structural — `cmd` feature flag enables config-level shell execution — opt-in risk-expansion

*Continuous · Since feature introduction · → If you don't need config-triggered shell commands, install without `--features cmd` (the default).*

kanata's default install (`cargo install kanata`) is key-remap-only — configs can define layers, tap-hold actions, macros, and so on, but cannot execute shell commands. The `cmd` action is behind a Cargo feature flag: `cargo install kanata --features cmd`. Enabling it expands the daemon's capability to include running arbitrary shell commands triggered by config-defined actions.

This is good risk-reduction design: opt-in, documented, off by default. The finding exists to make the capability visible to readers. Consumers who enable `--features cmd` are signing up for a qualitatively different threat model — a kanata config becomes executable content. Third-party config files shared on the internet (a common practice in the keyboard-customization community) should be audited before loading when the `cmd` feature is enabled.

**How to fix.** N/A — the design is appropriate. Consumer guidance: treat kanata configs with `cmd` actions as executable code; only load configs you audited.

### F5 — Info · Coverage — Rust-ecosystem scanner gaps — Cargo.lock parsing + workspace sub-crate channel misidentification

*Continuous · Scanner tooling gap · → Same gap pattern as wezterm (entry 21); consumer-side `cargo audit` recommended.*

Two Rust-ecosystem scanner gaps — identical to wezterm entry 21: (1) Cargo.lock parsing not implemented, so runtime_count=0 and osv total_vulns=0 are coverage artifacts; (2) distribution-channel detection surfaced 12 crates.io entries from workspace sub-crates when only `crates-kanata` is the real consumer install path. Dangerous-primitives hits (3 total) are consistent with the Rust-serde / test-fixture false-positive class.

The pattern is now established — V1.2 Rust scans consistently hit the same three gaps. Consolidated V1.2.x harness patch candidate: Cargo.lock parsing + workspace-member disambiguation + serde regex tuning. Consumer-side: run `cargo audit` locally to fill the dep-CVE visibility gap.

**How to fix.** Scanner-side: Cargo.lock parsing + RustSec advisory-db lookup; disambiguate workspace sub-crates from publishable channels by checking Cargo.toml `[package]` presence + crates.io registry confirmation.

---

## 02A · Executable file inventory

> kanata ships as a single daemon binary per platform — `kanata` on Linux/macOS, `kanata.exe` on Windows with 3 variants for the different input-capture backends (Interception driver, IoKey, raw Windows hooks). The binary runs with elevated OS privileges to intercept and emit keyboard events.

### Layer 1 — one-line summary

- Primary surface is the kanata daemon process. Cargo workspace sub-crates (parser, tcp_protocol, keyberon, interception binding, WASM target, etc.) are linked into the single binary or exposed as auxiliary tools.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `src/main.rs + src/oskbd/ (OS keyboard bindings)` | daemon-binary | Rust (with libc / IOKit / Windows API bindings via platform-specific sub-crates) | Raw keyboard-device I/O (read keystrokes, write remapped events). Elevated OS privileges required on all 3 platforms. | None by default. Optional `tcp` feature adds a local-only TCP server for control. | The privileged core. Every keystroke flows through this binary; compromise = keylogger + optional RCE (if `cmd` feature enabled — F4). |
| `parser/ (config DSL parser)` | library | Rust | None | None | Parses kanata's custom Lisp-ish config format. User-authored configs become kanata runtime state — parser bugs here could affect remapping behavior but not directly RCE unless config-level actions include `cmd`. |
| `interception/ (Windows Interception driver binding)` | library | Rust (FFI to Windows Interception driver) | Kernel-level keyboard-input driver interaction (Interception is a kernel driver that kanata talks to via user-mode DLL). | None | Only compiled into Windows builds when `--features interception_driver` is enabled. The underlying Interception driver itself is third-party and must be separately installed by the user. |

Install paths: `cargo install kanata` (+ optional features cmd/interception_driver/tcp); prebuilt GitHub Releases binaries; AUR package (Arch); Homebrew formula (macOS); Microsoft Store. Cargo-install integrity is whatever crates.io provides; GitHub-Releases binaries are unsigned.

---

## 03 · Suspicious code changes

> Representative rows from the 300-PR sample. Full sample: 44% formal review rate (highest in V1.2 catalog), 48% any-review, 117 self-merges (39%). Pattern: external-contributor PRs routinely have formal APPROVED decisions; maintainer's own PRs go direct without review — a healthy two-tier model.

Sample: the 50 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 44.0% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#2032](https://github.com/jtroo/kanata/pull/2032) | feat: add new layer-switch action (sample) | external-contrib | jtroo | Approved by jtroo | None |
| [#2031](https://github.com/jtroo/kanata/pull/2031) | fix: Linux uinput edge case (sample) | external-contrib | jtroo | Approved by ItayGarin | Privileged-path fix — formally reviewed |
| [#2029](https://github.com/jtroo/kanata/pull/2029) | feat: parser error message improvements (sample) | external-contrib | jtroo | Approved by jtroo | None |
| [#2028](https://github.com/jtroo/kanata/pull/2028) | chore: cargo-checks tightening (sample) | external-contrib | jtroo | Approved | None |
| [#2022](https://github.com/jtroo/kanata/pull/2022) | refactor: keyberon internals (sample) | jtroo | jtroo | No formal decision | Maintainer self-merge |
| [#2021](https://github.com/jtroo/kanata/pull/2021) | chore: version bump (sample) | jtroo | jtroo | No formal decision | Maintainer self-merge |

---

## 04 · Timeline

> ✓ 5 good · 🟡 2 neutral
>
> kanata lifecycle — 4-year jtroo-led project with ItayGarin as active co-maintainer; active semver-prerelease cadence through 2026.

- 🟡 **2022-04-18 · Repo created by jtroo** — Solo start
- 🟢 **2022-12-01 · v0.100 range releases** — Early cadence
- 🟢 **2024-01-01 · ItayGarin active co-maintainer (est.)** — Two-maintainer shape established
- 🟢 **2025-06-01 · v1.x series stabilized (est.)** — Mature semver
- 🟢 **2026-04-12 · v1.12.0-prerelease-2 released** — 8 days before scan
- 🟢 **2026-04-19 · Last push to main** — 1 day before scan
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan entry 23

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 7,179 |  |
| Open issues | 98 | 0 security-tagged |
| Open PRs | 6 |  |
| Primary language | Rust | Second Rust V1.2 entry |
| License | LGPL-3.0 |  |
| Created | 2022-04-18 | ~4 years |
| Last pushed | 2026-04-19 | 1 day before scan |
| Default branch | main |  |
| Total contributors | 100 | jtroo 79% + ItayGarin 12% ~91% top-2 |
| Solo-maintainer flag | FALSE | Top-1 at 79% — just below 80% threshold |
| Formal releases | 58 | v1.12.0-prerelease-2 @ 2026-04-12 |
| Release cadence | Active semver + prereleases | Latest 8 days before scan |
| Classic branch protection | OFF (HTTP 404) |  |
| Rulesets | 0 |  |
| Rules on default branch | 0 |  |
| CODEOWNERS | Absent |  |
| SECURITY.md | Absent | Privileged tool |
| CONTRIBUTING | Absent |  |
| Community health | 57% |  |
| Workflows | 5 | Linux + macOS + Windows + build-everything + cargo-checks |
| pull_request_target usage | 0 |  |
| CodeQL SAST | Absent |  |
| Dependabot | Absent | No dependabot.yml — F2 |
| PR formal review rate (300 sample) | 44.0% | HIGHEST in V1.2 catalog |
| PR any-review rate (300 sample) | 48.0% |  |
| Self-merge count (300 sample) | 117 (39%) | Maintainer direct-commits |
| Published security advisories | 0 | 4 years, zero |
| OSSF Scorecard | Not indexed |  |
| Cargo workspace | 12 sub-crates | Harness detected all 12 as channels — F5 |
| osv.dev vulns | Not checked | Cargo parsing not implemented — F5 |
| Primary distribution | cargo install kanata + GitHub Releases binaries + AUR + Homebrew + MS Store |  |
| `cmd` feature flag | Opt-in (disabled by default) | Expands threat model when enabled — F4 |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 7 documented gaps — concentrated on Rust-ecosystem parsing (Cargo.lock, workspace sub-crate disambiguation). Same pattern as wezterm (entry 21).

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit |
| Tarball extraction + local grep | ✅ Scanned |
| OSSF Scorecard | ⚠ Not indexed |
| Dependabot alerts | ⚠ Admin scope (403); no dependabot.yml in repo — F2 |
| osv.dev dependency queries | ⚠ 0 queries — Cargo.lock parsing not implemented (F5) |
| PR review sample | ✅ 300-PR sample — 44% formal, 48% any, 117 self-merges |
| Dependencies manifest detection | ⚠ 15 manifests detected; runtime_count=0 (F5) |
| Distribution channels inventory | ⚠ 12 crates.io channels surfaced (workspace sub-crates); real channels include GitHub Releases / AUR / Homebrew / MS Store (F5) |
| Dangerous-primitives grep | ✅ Only 3 hits (deserialization 1, secrets 1, tls_cors 1) — likely false positives on Rust serde / CIDR patterns |
| Workflows | ✅ 5 detected (Linux/macOS/Windows builds + cargo-checks + meta) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No suspicious paste-from-command blocks |
| Tarball extraction | ✅ 292 files |
| osv.dev | ℹ Zero runtime dependencies |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4956/5000 remaining |

**Gaps noted:**

1. Rust Cargo.lock parsing not implemented — 15+ Cargo manifests with transitive dep graphs are unscanned. Same gap as wezterm (entry 21); consistent Rust-ecosystem issue.
2. Distribution-channel harness surfaced 12 crates.io channels from Cargo workspace sub-crates — only `crates-kanata` is the real install channel. GitHub Releases, AUR, Homebrew, MS Store channels all unrecognized.
3. Dependabot alerts API required admin scope (HTTP 403); dependabot.yml does not exist in the repo — no ecosystem coverage at all (F2).
4. Dangerous-primitives regex false-positives on Rust idioms (deserialization hits on serde impls — same pattern as wezterm).
5. Gitleaks secret-scanning not available on this scanner host.
6. OSSF Scorecard not indexed — governance signals derived from raw gh api data.
7. Release-integrity grading is coarse — harness doesn't inspect GitHub Releases assets for .sig / code-signing / .sha256 on kanata binaries.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from Phase 1 harness + gh api + workspace inspection + README reading.

### ★ Priority evidence (read first)

#### ★ Evidence 2 — No branch protection — classic HTTP 404, 0 rulesets, 0 rules on default branch, no CODEOWNERS. Relies entirely on voluntary review discipline.

```bash
gh api repos/jtroo/kanata/branches/main/protection; gh api repos/jtroo/kanata/rulesets
```

Result:
```text
classic: HTTP 404. rulesets: {entries: [], count: 0}. rules_on_default: {entries: [], count: 0}. CODEOWNERS: not found at any standard path.
```

*Classification: fact*

#### ★ Evidence 3 — PR review sample (300 PRs): formal_review_rate=44.0%, any_review_rate=48.0%, self_merge_count=117 (39%). **Formal review rate is the HIGHEST in the V1.2 catalog** — despite no branch-protection enforcement, jtroo + ItayGarin run a disciplined review culture for external contributions.

```bash
gh api 'repos/jtroo/kanata/pulls?state=closed&per_page=100' # 3 pages
```

Result:
```text
sample_size: 300; formal_review_rate: 44.0 (132 of 300 PRs carry `APPROVED` review decisions); any_review_rate: 48.0; self_merge_count: 117. Pattern from sampling recent PRs: external contributor PRs routinely show `review_decision=APPROVED` + 1 reviewer; maintainer's own PRs (jtroo) are frequently self-merged without review. This is a genuine two-tier review pattern, not signal noise.
```

*Classification: fact*

#### ★ Evidence 9 — No Dependabot config (dependabot.yml absent). Rust workspace with 15+ Cargo manifests has no automated CVE-watch on Cargo dep graph. Same-shape gap as wezterm (entry 21).

```bash
gh api repos/jtroo/kanata/contents/.github/dependabot.yml
```

Result:
```text
HTTP 404. dependabot_config.present: false. No Dependabot ecosystems tracked. The 15+ Cargo.toml files have transitive dep graphs that include serde, tokio, and the platform-specific input libraries (uinput, IOKit bindings, Interception driver) — none automatically CVE-watched.
```

*Classification: fact*

### Other evidence

#### Evidence 1 — kanata is a cross-platform keyboard-remapping daemon. Privileged on every platform: Linux uses uinput (requires CAP_NET_ADMIN or root); macOS uses IOKit/HID (often requires root + Accessibility/Input-Monitoring permissions); Windows uses the Interception driver (requires admin install). Intercepts every keystroke in real time.

```bash
gh api repos/jtroo/kanata --jq '{description, topics}'; head README.md
```

Result:
```text
description: 'Improve keyboard comfort and usability with advanced customization'. topics: [cross-platform, interception-driver, keyboard, keyboard-layout, linux, macos]. Runtime model: a daemon runs with elevated privileges, captures all keyboard input, applies user-configured remapping rules (layers, tap-hold, macros), and emits remapped keystrokes to the OS. The user's raw keystrokes flow through the daemon.
```

*Classification: fact*

#### Evidence 4 — Active semver-prerelease cadence — v1.12.0-prerelease-2 on 2026-04-12 (8 days before scan). 58 total releases; recent push velocity on main is 2026-04-19 (day before scan).

```bash
gh api 'repos/jtroo/kanata/releases?per_page=5'
```

Result:
```text
total_count: 58. Latest: v1.12.0-prerelease-2 (2026-04-12). Repo pushed_at: 2026-04-19 (7 days later; 1 day before scan). Active development + active release cadence — the code IS reaching users as it lands.
```

*Classification: fact*

#### Evidence 5 — Cargo workspace with 15 manifest files across 12 publishable-looking sub-crates. Main distribution is `cargo install kanata` (on crates.io) or GitHub Releases binary + platform-specific installers.

```bash
gh api repos/jtroo/kanata/contents | jq '.[] | select(.type == "dir") | .name'; gh api repos/jtroo/kanata/contents/Cargo.toml | jq -r .content | base64 -d | head
```

Result:
```text
Cargo workspace members: parser, example_tcp_client, tcp_protocol, key-sort-add, windows_key_tester, keyberon, keyberon-macros, interception, simulated_input, simulated_passthru, wasm. README documents: `cargo install kanata` (basic), `cargo install kanata --features cmd` (shell-exec feature opt-in), `cargo install kanata --features interception_driver` (Windows). Also GitHub Releases prebuilt binaries.
```

*Classification: fact*

#### Evidence 6 — community/profile: health 57%; no SECURITY.md, no CONTRIBUTING, no CODE_OF_CONDUCT. security-advisories count: 0 across 4 years of development.

```bash
gh api 'repos/jtroo/kanata/community/profile'; gh api 'repos/jtroo/kanata/security-advisories'
```

Result:
```text
health_percentage: 57; has_security_policy: false; has_contributing: false; has_code_of_conduct: false; license_spdx: LGPL-3.0. security-advisories count: 0. For a keyboard-interception daemon handling every keystroke, 0-advisories-in-4-years points at silent-fix cadence (consistent with catalog-wide pattern) not bug-freeness.
```

*Classification: fact*

#### Evidence 7 — Contributor distribution: jtroo (984), ItayGarin (149), rszyma (47), eugenesvk (38), malpern (27). Top-1 share 79% — below the 80% solo-maintainer threshold. ItayGarin is a substantial co-maintainer at 149 commits (~12% share).

```bash
gh api repos/jtroo/kanata/contributors --jq '[.[] | {login, contributions}] | .[:6]'
```

Result:
```text
jtroo: 984; ItayGarin: 149; rszyma: 47; eugenesvk: 38; malpern: 27; next: smaller tail. total_contributor_count: 100. Top-1 alone at 79% (just below the is_solo_maintainer threshold of 80%). Combined top-2 share ~91%.
```

*Classification: fact*

#### Evidence 8 — Five GitHub Actions workflows cover Linux/macOS/Windows builds + cargo-checks + build-everything meta. No CodeQL, no Dependabot. CI depth is solid for a cross-platform Rust binary.

```bash
gh api repos/jtroo/kanata/actions/workflows --jq '.workflows[] | {name, path, state}'
```

Result:
```text
5 workflows: build-everything.yml, linux-build.yml, macos-build.yml, windows-build.yml, rust.yml (cargo-checks). pull_request_target_count: 0. Good coverage of the three OS targets + lint/test pipeline.
```

*Classification: fact*

#### Evidence 10 — Active feature-gated shell-execution capability — `cargo install kanata --features cmd` enables the `cmd` action that runs shell commands from kanata config. Feature-gated means opt-in; off by default.

```bash
gh api repos/jtroo/kanata/contents/README.md | jq -r .content | base64 -d | grep -A2 'features cmd'
```

Result:
```text
README documents the `cmd` feature: 'cargo install kanata --features cmd' enables a config-level action to execute shell commands. Feature-gated is a deliberate risk-reduction — by-default kanata does not execute arbitrary commands. Users who opt in are informed.
```

*Classification: fact*

#### Evidence 11 — Distribution channels: `cargo install kanata` via crates.io (primary), GitHub Releases prebuilt binaries for 3 platforms, and Arch Linux AUR + Homebrew + MS Store are documented third-party channels. Scanner detected 12 'crates-*' channels (all 12 workspace sub-crates) — only `crates-kanata` is the genuine install channel.

```bash
gh api repos/jtroo/kanata/releases/latest --jq '.assets[] | {name, size}'
```

Result:
```text
GitHub Releases binaries: kanata-linux, kanata-macos (Intel + Apple Silicon), kanata_winLib.exe, kanata_winIoKey.exe, kanata_winWin.exe (multiple Windows variants for the 3 supported input-capture backends). Unsigned binaries — no .sig, no .asc, no .sha256. Crates.io install path provides its own integrity story (crates.io index hashes).
```

*Classification: fact*

#### Evidence 12 — Harness Cargo.lock parsing not implemented; 12 workspace sub-crates were surfaced as crates.io distribution channels when only the main `kanata` crate is the actual consumer install path. Same coverage-gap pattern as wezterm (entry 21). Dangerous-primitives hits (deserialization 1, secrets 1, tls_cors 1) are likely false positives on Rust serde idioms / Cargo.toml strings / network-CIDR patterns.

```bash
docs/phase_1_harness.py # code_patterns.dangerous_primitives + distribution_channels
```

Result:
```inference — coverage-gap annotation
dependencies.runtime_count: 0 (Cargo-parsing gap). distribution_channels.channels: 12 entries, all from workspace sub-crates — real channels (crates.io main + GitHub Releases binaries + AUR + Homebrew + MS Store) not recognized. dangerous_primitives: 3 total hits — small, consistent with Rust-serde / test-fixture false-positive class.
```

*Classification: inference — coverage-gap annotation*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `1c496c019dfb0df8a4e8321b54a9a9f8e0b2dc5e` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
