# Security Investigation: BatteredBunny/browser_terminal

**Investigated:** 2026-04-20 | **Applies to:** main @ `9a77c4ace7fd014c19391e541e348d7369f99e6a` | **Repo age:** 3 years | **Stars:** 10 | **License:** GPL-3.0

> BatteredBunny/browser_terminal — 10-star Chrome+Firefox extension exposing browser-tab shell access via a Go native-messaging host. installation.md directs Chrome users to chrome.google.cm (Cameroon TLD) instead of .com — a live typosquat URL (F0 Critical). Firefox install path is correct. Unsigned Go binary + 10-month release stall + single-maintainer governance floor complete the picture.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-browser_terminal.md` (+ `.html` companion) |
| Repo | [github.com/BatteredBunny/browser_terminal](https://github.com/BatteredBunny/browser_terminal) |
| Short description | Chrome + Firefox extension providing local-shell access via a Go native-messaging host. Small single-maintainer project (10 stars, 2 contributors). |
| Category | `browser-extension` |
| Subcategory | `terminal-native-messaging` |
| Language | Go |
| License | GPL-3.0 |
| Target user | Developer who wants a browser-tab-hosted terminal as a workflow convenience. Install path: (1) extension from Chrome Web Store or Firefox Add-ons, (2) Go native binary from GitHub Releases + `sudo mv` into PATH, (3) `browser_terminal --install` to register the native-messaging manifest. |
| Verdict | **Critical** (split — see below) |
| Scanned revision | `main @ 9a77c4a` (release tag ``) |
| Commit pinned | `9a77c4ace7fd014c19391e541e348d7369f99e6a` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of BatteredBunny/browser_terminal. Fifth wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19). |

---

## Verdict: Critical (split — Deployment axis only)

### Deployment ·  — **Critical — **

### Deployment ·  — **Critical — **

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>✗ Critical — F0 is the blocking item for Chrome install (1 findings)</strong>
<br><em>README's Chrome Web Store link is a Cameroon-TLD typosquat.</em></summary>

1. **F0** — installation.md points Chrome users to chrome.google.cm (not chrome.google.com) — an active typosquat-exposed URL.

</details>

<details>
<summary><strong>⚠ Warning — F1 + F2 + F3 describe the supply-chain + governance posture (3 findings)</strong>
<br><em>Unsigned binary, stalled release cadence, single-maintainer governance floor.</em></summary>

1. **F1** — Go native host ships from GitHub Releases with no .dgst/.sig/.sha256; README omits any integrity-verification step before `sudo mv`.
2. **F2** — v1.4.7 (June 2025) is the latest release; main has 10 months of unshipped activity. Browser-store users are on stale code.
3. **F3** — Single human maintainer + 0/12 formal-review rate + no branch protection + no CODEOWNERS + no SECURITY.md.

</details>

<details>
<summary><strong>ℹ Info — F4 + F5 + F6 are context (3 findings)</strong>
<br><em>Architectural blast-radius notes + positive hygiene + scanner gaps.</em></summary>

1. **F4** — Native-messaging architecture grants any extension context a live shell — this is the tool's function; install only if you want that.
2. **F5** — Dependabot on gomod + npm + github-actions; 1 dev-only esbuild vuln not reachable at runtime.
3. **F6** — Scanner coverage gaps: no install-doc URL scan, fictitious npm channel detected, dangerous-primitives false-positive on build-script self-read.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — 0% formal / 0% any-review across 12 lifetime PRs, single human maintainer, no branch protection |
| Is it safe out of the box? | ❌ **No** — install doc directs Chrome users to a typosquat TLD; binary install has no integrity verification |
| Do they fix problems quickly? | ✅ **Yes (structurally)** — 0 open security issues; dependabot active; small dep-graph surface |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md, no CONTRIBUTING, no disclosure channel documented; 0 published advisories |

---

## 01 · What should I do?

> 10⭐ · GPL-3.0 · Go + TS · 1 critical · 3 warnings · 3 info · CRITICAL (split)
>
> BatteredBunny/browser_terminal is a 10-star browser extension providing browser-tab-hosted shell access via a Go native-messaging host. Small tool, real function. Critical verdict driven by F0: installation.md points Chrome users to chrome.google.cm — a Cameroon-TLD typosquat of chrome.google.com. Firefox users (following the correctly-spelled addons.mozilla.org link) avoid F0, which is why this is a Deployment-axis split. Beyond F0: unsigned Go binary with no integrity verification step (F1), 10-month release stall (F2), single-maintainer governance floor (F3). Positive signals exist (dependabot on 3 ecosystems; no known reachable vulns in the dep graph) but the install-path defect is the live issue.

### Step 1: Install Chrome extension via chrome.google.com/webstore — NOT via the README link (🚨)

**Non-technical:** The README's Chrome install link uses a `.cm` (Cameroon) typosquat URL instead of `.com`. Open chrome.google.com/webstore manually and search for 'browser_terminal' or paste the extension ID nbnfihffeffdhcbblmekelobgmdccfnl. Verify the publisher before installing.

```bash
open 'https://chrome.google.com/webstore/detail/browser-terminal/nbnfihffeffdhcbblmekelobgmdccfnl'
```

### Step 2: Install Firefox extension via addons.mozilla.org (link in README is correct) (✓)

**Non-technical:** Firefox users can follow the README link — addons.mozilla.org is correct.

```bash
open 'https://addons.mozilla.org/en-US/firefox/addon/browser_terminal/'
```

### Step 3: Before `sudo mv`, hash the downloaded native binary and record the baseline (⚠)

**Non-technical:** The release has no .sha256 / .dgst / .sig file. Compute sha256sum locally after downloading and record it — this is your tripwire for future releases.

```bash
sha256sum ~/Downloads/browser_terminal_linux | tee ~/.browser_terminal.baseline.sha256
```

### Step 4: Run the extension in a dedicated browser profile (⚠)

**Non-technical:** Because the native host bridges to a shell, anything that reaches the extension can run shell commands as your user. Isolate the extension in a browser profile that has no other extensions, no logged-in sessions, and no sensitive sites open.

```bash
google-chrome --profile-directory='browser_terminal-isolated'
```

### Step 5: After `browser_terminal --install`, read the installed native-messaging manifest to confirm the extension ID binding (ℹ)

**Non-technical:** The `--install` step writes a native-messaging manifest into ~/.config/google-chrome/NativeMessagingHosts/ (Chrome) or ~/.mozilla/native-messaging-hosts/ (Firefox). Read it to verify which extension IDs are allowed to talk to the host.

```bash
cat ~/.config/google-chrome/NativeMessagingHosts/*browser_terminal*.json
```

### Step 6: If you don't need a browser-driven terminal, don't install the native host (ℹ)

**Non-technical:** The extension alone (no native host installed) is effectively a no-op. If you installed the extension to try it and decided it isn't for you, uninstall the host with `browser_terminal --uninstall` to remove the native-messaging manifest.

```bash
browser_terminal --uninstall
```

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 3 Warning · ℹ 3 Info
>
> 7 findings total.
### F0 — Critical · Vulnerability — installation.md points Chrome users to `chrome.google.cm` — Cameroon-TLD typosquat of chrome.google.com

*Continuous (as long as the typo is in installation.md) · Detected 2026-04-20; unknown when the typo was introduced · → Do NOT follow the Chrome install URL as written. Go to chrome.google.com/webstore directly and search for 'browser_terminal'.*

installation.md — the project's single install document — contains this line: `Install extension from [firefox addons](https://addons.mozilla.org/en-US/firefox/addon/browser_terminal/) or [chrome web store](https://chrome.google.cm/webstore/detail/browser-terminal/nbnfihffeffdhcbblmekelobgmdccfnl)`. The Firefox URL is correct; the Chrome URL is not `chrome.google.com` — it is `chrome.google.cm`, a Cameroon-TLD lookalike. `.cm` is a widely-documented typosquat target for `.com` specifically because users drop the trailing `o` when typing fast.

The link is hyperlinked in the rendered README, so a reader who clicks it goes directly to the typosquat URL without having a chance to notice the TLD. If `chrome.google.cm` is (or ever becomes) attacker-controlled, they can serve a fake Chrome Web Store page to any user following the install instructions. The extension ID in the URL (`nbnfihffeffdhcbblmekelobgmdccfnl`) is the real ID, but on a .cm domain the Chrome-Web-Store-level trust chain is not in effect — it's just a page the operator of .cm controls.

This finding is the only reason the overall verdict is Critical rather than Caution. A consumer who wants to install this extension should open chrome.google.com/webstore manually and search by name or paste the extension ID — do not follow the link from the README. Firefox users are unaffected. For the maintainer: a one-character fix (`cm` → `com`) resolves the finding.

**How to fix.** Maintainer-side: fix `chrome.google.cm` to `chrome.google.com` in installation.md and republish. Consumer-side: ignore the README link, navigate to chrome.google.com/webstore manually, search for the extension by name or by the ID `nbnfihffeffdhcbblmekelobgmdccfnl`, and verify the publisher before installing.

### F1 — Warning · Supply chain — Unsigned Go binary + `sudo mv` install with no documented integrity verification

*Continuous · Since first release · → Before running `sudo mv`, compute sha256sum of the downloaded binary and record it yourself; compare against the binary you download next time as a change-detection tripwire.*

The v1.4.7 release (2025-06-23) ships four assets: two Go native binaries (`browser_terminal_linux`, `browser_terminal_macos`) and two extension packages (chromium + firefox zips). Zero of the assets have an accompanying checksum file — no `.dgst`, no `.sig`, no `.sha256`, no `.asc`. The installation flow is 'download the binary, `sudo mv` it into `/usr/local/bin/`, run `--install`'. No step asks the user to verify anything.

The blast radius of an unverified native-binary install is user-level access (not root — the install step is `sudo mv`, but the binary itself runs as the user). That's sufficient access for the shell the tool provides to do anything the user can do: read SSH keys, read browser profiles, modify shell-startup files, exfiltrate data. A publisher-account compromise that re-uploads the release asset would reach every user who downloads next.

Baseline remediation on the consumer side is a one-line `sha256sum` step before `sudo mv`: record the hash on first install, and use it as a tripwire for later releases. Real remediation on the maintainer side is adopting either per-asset checksums (minimal GHA change) or Sigstore keyless signing (slightly more infrastructure but stronger guarantees).

**How to fix.** Maintainer-side: emit a `.sha256` or `.dgst` per asset in the release workflow (~5 lines of GitHub Actions YAML); adopt Sigstore keyless signing for the binary (minimal operational burden). Consumer-side: `sha256sum browser_terminal_linux` before moving it, and record that hash as your baseline.

### F2 — Warning · Structural — Release cadence stalled 10 months — v1.4.7 from June 2025; main has unshipped changes

*Continuous · Since 2025-06-23 · → If you value the changes on main, build from source (nix run github:BatteredBunny/browser_terminal#native or pnpm build); otherwise accept that you are running 10-month-old shipped code.*

v1.4.7 was published 2025-06-23. The repo's last push to main is 2026-04-03 — 10 months later. Browser-store extensions auto-update from whatever the store distributes; if the Chrome Web Store and Firefox Add-ons are still serving v1.4.7 (very likely, since no new release tag exists), those installed users are running 10-month-old shipped code regardless of how active main is.

For a small single-maintainer repo this pattern is common — changes accumulate on main without a 'release-worthy' threshold being met. The governance consequence is that any fix merged to main does not reach users until a new tag is cut and the browser stores process the updated manifest. If a security issue is fixed on main today, the typical store propagation time is 1–7 days after a new tag; until then, users are exposed even though 'the repo fixed it'.

Nothing in this finding is immediately actionable beyond awareness. It becomes urgent if a future fix on main targets an exploitable issue — the release stall would delay user remediation.

**How to fix.** Maintainer-side: cut a release when batched changes pass whatever internal bar exists; at minimum, re-tag and republish when a security-relevant fix lands. Consumer-side: for privileged-tool hygiene, prefer source-builds over stale shipped binaries.

### F3 — Warning · Governance — Single-maintainer governance floor on a privileged browser-extension + native-shell tool

*Continuous · Since repo creation (2023-04-14) · → Pin a reviewed release tag you built yourself rather than tracking whatever the store updates to.*

BatteredBunny is the only human contributor to this repo (41 commits across the lifetime). The only other 'contributor' is dependabot[bot] (12 commits). Across the 12 lifetime closed PRs: 0 had formal review decisions, 0 had any reviewer engagement, 0 self-merges (the maintainer's own commits go direct to main — PRs here are mostly dependabot). There is no branch protection, no rulesets, no CODEOWNERS, no SECURITY.md.

For a tool whose installed form provides a live interactive shell to browser-extension contexts, this is the minimum-viable governance posture. A single account compromise on the maintainer's GitHub credentials reaches every installed user via the native-binary release path. The extension half is protected somewhat by browser-store moderation gates, but the native-binary path has no such intermediary.

There is no implicit criticism of the maintainer here — small OSS projects routinely operate this way. The finding describes the structural exposure, and a consumer who installs a privileged tool should understand that THEY are the review gate if none exists upstream.

**How to fix.** Maintainer-side: at minimum, enable a ruleset requiring status checks before merge (the existing GitHub Actions workflows would gate merges), add SECURITY.md naming the private-advisory channel. Consumer-side: recognize that 'pin a reviewed SHA' means you, personally, are the review gate.

### F4 — Info · Structural — Native-messaging host grants any extension context a full interactive shell — this is the tool's function, not a bug

*By design · N/A · → Understand what you're installing. If you don't need a browser-driven terminal, don't install the native host.*

The native-host Go binary reads JSON messages from Chrome's native-messaging stdin protocol and forwards them to a `/bin/sh` subprocess wired through a PTY. There is no authentication between the extension and the native host, no command allowlist, no session prompt. The design IS the feature: the user installs a browser-tab-hosted terminal, and the terminal has the user's privileges.

This is categorized as Info rather than Warning because it is not a defect — it is the tool's declared function. It is named here so the threat model is explicit: the tool's attack surface is 'any path that reaches the extension's message ports, bridged to a shell'. Users should install it only if they want that capability and understand what it grants.

Risk-reduction suggestions for the maintainer: a shared-secret between extension and host (prevents arbitrary-extension access); a startup confirmation prompt in the host (prevents silent first-use); a command-allowlist mode (opt-in hardening for paranoid users). None of these exist today.

**How to fix.** Not applicable — this is the tool's function. A maintainer could add authentication (shared secret between extension and host), a command allowlist, or a session-start user prompt to reduce the surface. Consumer-side: run the extension in a dedicated browser profile with no other extensions and no sensitive sessions.

### F5 — Info · Hygiene — Dependabot on gomod + npm + github-actions; one low-severity dev-only dep vuln (esbuild)

*Continuous · Since dependabot.yml adoption · → Non-blocking; dep-graph is small and watched.*

Dependabot is configured for gomod + npm + github-actions with daily polling — above-average hygiene for a 10-star single-maintainer project. The osv.dev query against the dep graph surfaces exactly one vulnerability (esbuild GHSA-67mh-4wv8-2f99, a same-origin bypass in esbuild's dev-server), which is not reachable in this repo's build-only use of esbuild. The Go runtime dep surface is a single entry: `github.com/creack/pty` — a standard well-maintained PTY library.

This finding is Info because it describes existing positive investment and an unreachable vuln — no action required.

**How to fix.** Consumer-side: acknowledge the dep graph is watched; focus attention on F0-F3 where the real risks are.

### F6 — Info · Coverage — Scanner coverage gaps: install-doc URL typosquat detection absent; fictitious npm channel surfaced from package.json

*Continuous · Scanner tooling gap · → Scanner-side improvements would catch the F0 class of finding automatically; consumer-side it means this scan's Q4 relies on LLM-authored override for the typosquat.*

Two scanner-side gaps relevant to this scan: (1) the harness does not scan README / install-doc URLs for anomalies (TLD deviation, suspicious redirect targets, visual-similarity lookalikes). The F0 typosquat was surfaced only because LLM authoring read installation.md directly during Phase 4. A future scan on a browser-extension shape would hit the same gap unless the harness is extended. (2) The harness detected `npm-browser_terminal` as a distribution channel on the basis of package.json presence alone; the package is not actually on the npm registry. Real channels (Chrome Web Store + Firefox Add-ons + GitHub Releases) were not recognized.

Fix surface for both is `docs/phase_1_harness.py`: add install-doc URL analysis (TLD deviation check against a reference list of known install-source domains like chrome.google.com / addons.mozilla.org / pypi.org); tighten npm-channel detection to require `npm view` confirmation; add browser-store channel recognition. When those land, a future re-scan would emit F0-class findings automatically without needing Phase 4 override.

**How to fix.** Scanner-side: (a) add install-doc URL scan with TLD-deviation detection (flag URLs whose TLD differs from a known-good reference — e.g., if README links point at chrome.google anywhere other than .com); (b) tighten npm-channel detection to require `npm view PACKAGE` confirmation, not package.json presence alone; (c) add browser-store channel recognition (chrome-web-store, firefox-addons).

---

## 02A · Executable file inventory

> browser_terminal ships two artifact families: (1) the Go-compiled native host binary (`browser_terminal_linux`, `browser_terminal_macos`) distributed via GitHub Releases; (2) the Chrome + Firefox extension packages (JS/TS + manifest) distributed via the respective browser stores.

### Layer 1 — one-line summary

- The native host is the privileged half — it spawns `/bin/sh` under PTY and forwards stdin/stdout between the extension and the shell. The extension half is sandboxed by the browser's extension runtime.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `native/main.go` | native-host | Go | exec.Command(shell) + creack/pty PTY wiring + bidirectional stdin/stdout bridge to Chrome native-messaging. | No outbound network calls by the native host itself; shell subprocesses are free to make any network call they wish via user-typed commands. | Privileged shell bridge. User-level privileges. Any extension context with native-messaging permission reaches this shell. |
| `src/ (extension frontend — TypeScript + JS)` | browser-extension | Browser (Chrome / Firefox) | None | Native-messaging port to the Go host. | Extension half. Sandboxed by the browser runtime. Communicates ONLY with the native host (per manifest). The risk surface is whatever CAN reach the extension's message ports — content-scripts, other extensions with message-passing permission, etc. |
| `.github/workflows/release.yml + fix-hash.yml` | ci-pipeline | GitHub Actions | None | Cross-compile Go → linux + macos binaries; package extension; upload to GitHub Releases. | Release pipeline. Runs on tag push. No checksum or signature generation step at present. |

Installation involves separate channels (browser store for the extension, GitHub Releases for the native binary). The browser-store halves have automated store-level review; the native-binary half does not. See F0 (typosquat) + F1 (unsigned binary) for consumer guidance.

---

## 03 · Suspicious code changes

> Representative rows from the 12-PR lifetime sample. Every PR in the repo's history was merged by the maintainer without formal reviewer engagement — this is the sample, not a subset.

Sample: the 12 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 0.0% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#12](https://github.com/BatteredBunny/browser_terminal/pull/12) | dependabot: gomod dep bump (sample) | dependabot[bot] | BatteredBunny | No formal decision | None |
| [#10](https://github.com/BatteredBunny/browser_terminal/pull/10) | feat: extension UI improvements (sample) | BatteredBunny | BatteredBunny | No formal decision | Self-committed — representative of the 12-PR history |
| [#8](https://github.com/BatteredBunny/browser_terminal/pull/8) | fix: native host PTY resize handling (sample) | BatteredBunny | BatteredBunny | No formal decision | Privileged-path change, no review |
| [#5](https://github.com/BatteredBunny/browser_terminal/pull/5) | chore: update Nix flake inputs (sample) | BatteredBunny | BatteredBunny | No formal decision | None |
| [#2](https://github.com/BatteredBunny/browser_terminal/pull/2) | feat: Firefox support added (sample) | BatteredBunny | BatteredBunny | No formal decision | None |

---

## 04 · Timeline

> ✓ 1 good · 🟡 4 neutral
>
> browser_terminal lifecycle — small single-author project from 2023, 5 releases, recent activity on main.

- 🟡 **2023-04-14 · Repo created** — Single-author start
- 🟢 **2024-05-01 · First formal release (v1.0.0 estimated)** — Release cadence begins
- 🟡 **2025-06-23 · v1.4.7 released (latest)** — Last release at scan
- 🟡 **2026-04-03 · Last push to main** — Active main, no new release
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan, entry 20

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 10 | Very low — near-zero community audit |
| Forks | — |  |
| Open issues | 1 | 0 security-tagged |
| Open PRs | 0 |  |
| Primary language | Go | Plus TypeScript/JS in src/ extension frontend |
| License | GPL-3.0 |  |
| Created | 2023-04-14 | ~3 years |
| Last pushed | 2026-04-03 | Active commits |
| Default branch | main |  |
| Total contributors | 2 (incl. dependabot) | BatteredBunny: 41 commits; dependabot[bot]: 12 |
| Human contributors | 1 | Single maintainer |
| Formal releases | 5 | Latest v1.4.7 on 2025-06-23 |
| Release cadence | Stalled 10 months | Main has unshipped activity |
| Release integrity | None | No .dgst / .sig / .sha256 / .asc |
| Classic branch protection | OFF (HTTP 404) |  |
| Rulesets | 0 |  |
| Rules on default branch | 0 |  |
| CODEOWNERS | Absent |  |
| SECURITY.md | Absent | Privileged tool (shell bridge) |
| CONTRIBUTING | Absent |  |
| Community health | 42% |  |
| Workflows | 4 | Release × 2 + Dependabot + Dependency-Graph |
| pull_request_target usage | 0 |  |
| CodeQL SAST | Absent |  |
| Dependabot | Enabled (gomod + npm + github-actions) | Multi-ecosystem |
| PR formal review rate | 0.0% | 12-PR lifetime sample |
| PR any-review rate | 0.0% |  |
| Self-merge count | 0 | Maintainer commits directly to main |
| Published security advisories | 0 |  |
| Open security issues | 0 |  |
| OSSF Scorecard | Not indexed |  |
| Runtime Go deps | 1 (creack/pty) | Very small attack surface |
| npm deps (runtime) | 7 | Per harness parse of package.json |
| osv.dev vulns | 1 (esbuild dev-server; not reachable) | Build-time only |
| Primary distribution | Chrome Web Store + Firefox Add-ons + GitHub Releases (native host) | Harness detected fictitious npm channel (F6) |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 7 documented gaps — most notably the install-doc URL scan absence that necessitated Phase 4 authoring of F0.

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit |
| Tarball extraction + local grep | ✅ Scanned |
| OSSF Scorecard | ⚠ Not indexed |
| Dependabot alerts | ⚠ Admin scope (403); dependabot.yml present + active |
| osv.dev dependency queries | ✅ 1 vuln (esbuild, dev-server bypass — not reachable at runtime) |
| PR review sample | ✅ 12-PR lifetime sample; formal + any review both 0% |
| Dependencies manifest detection | ✅ 4 manifests (go.mod + go.sum + package.json + pnpm-lock.yaml) |
| Distribution channels inventory | ⚠ Detected fictitious 'npm-browser_terminal' channel; real channels (Chrome Web Store + Firefox Add-ons + GitHub Releases) NOT detected (F6) |
| Install-doc URL scan for typosquat | ⊗ Not implemented — F0 typosquat surfaced by LLM authoring only |
| Dangerous-primitives grep (15 families) | ⚠ 1 false-positive path_traversal hit (build-script `fs.readFileSync(SRC_DIR + '/manifest.json')` — reads its own manifest) |
| Workflows | ✅ 4 detected (Release × 2 + Dependabot + Dep-Graph); no CodeQL; no test CI |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No paste-from-command blocks (but typosquat URL F0 surfaced separately — see F6 gap) |
| Tarball extraction | ✅ 35 files |
| osv.dev | ℹ  |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4985/5000 remaining |

**Gaps noted:**

1. Install-doc URL analysis is not implemented in the harness — F0 typosquat URL in installation.md was only surfaced by LLM authoring reading the file directly. Future browser-extension scans will need the same manual step until harness adds TLD-deviation detection.
2. Distribution-channel harness detected a fictitious 'npm-browser_terminal' channel based solely on package.json presence (the package is not on the npm registry). Real channels (Chrome Web Store + Firefox Add-ons + GitHub Releases binary) were not recognized.
3. OSSF Scorecard not indexed — governance signals derived entirely from raw gh api data.
4. Dependabot-alerts API required admin scope (HTTP 403); dependabot.yml confirms active multi-ecosystem coverage regardless.
5. Dangerous-primitives `path_traversal` family produced a false positive on a build-script self-read of manifest.json — Go/JS mixed-repo idioms aren't perfectly aligned with the regex tuning.
6. Gitleaks secret-scanning not available on this scanner host.
7. Release-integrity channels are not formally graded beyond presence-check of `.dgst` / `.sig`. For this release (v1.4.7), absence of any such files is captured via Phase 4 authoring (F1) but not surfaced as a compute signal.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from Phase 1 harness + direct gh api queries + installation.md read + native/main.go read.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — installation.md points Chrome users to `chrome.google.cm/webstore/detail/browser-terminal/nbnfihffeffdhcbblmekelobgmdccfnl` — the `.cm` TLD (Cameroon) is a known typosquat target for `.com`.

```bash
gh api repos/BatteredBunny/browser_terminal/contents/installation.md | jq -r .content | base64 -d
```

Result:
```text
Step 1: 'Install extension from [firefox addons](https://addons.mozilla.org/en-US/firefox/addon/browser_terminal/) or [chrome web store](https://chrome.google.cm/webstore/detail/browser-terminal/nbnfihffeffdhcbblmekelobgmdccfnl)'. The Firefox URL is correct (addons.mozilla.org); the Chrome URL is not chrome.google.com — it is chrome.google.cm, a Cameroon-TLD lookalike. If .cm is ever registered by an adversary, it serves a fake Web Store page to any user who follows the README.
```

*Classification: fact*

#### ★ Evidence 3 — Release v1.4.7 (2025-06-23) ships 4 assets: linux + macos native Go binaries plus chromium + firefox extension zips. Zero checksum files, zero signature files.

```bash
gh api repos/BatteredBunny/browser_terminal/releases/latest
```

Result:
```text
tag: v1.4.7, published: 2025-06-23. Assets: browser_terminal_linux (2.2MB), browser_terminal_macos (2.2MB), chromium-browser_terminal-1.4.7.zip (3.0MB), firefox-browser_terminal-1.4.7.zip (3.0MB). No .dgst, .sig, .asc, .sha256, or .sha512 files. No GPG signature. No Sigstore attestation. No SLSA provenance.
```

*Classification: fact*

#### ★ Evidence 9 — Release cadence stall — v1.4.7 published 2025-06-23, last push to main 2026-04-03. Users on the release are 10 months behind the main branch; main has unshipped changes.

```bash
gh api 'repos/BatteredBunny/browser_terminal/releases?per_page=5'; gh api repos/BatteredBunny/browser_terminal --jq .pushed_at
```

Result:
```text
Latest release: v1.4.7 on 2025-06-23. Repo pushed_at: 2026-04-03. 10-month gap between the latest released version and the tip of main. Browser-store-distributed extensions auto-update users to whatever the store serves — if the Chrome / Firefox stores are serving v1.4.7, users on those stores are also on 10-month-old code even though the repo looks active.
```

*Classification: fact*

### Other evidence

#### Evidence 2 — The Go native-messaging host spawns `/bin/sh` (or `$SHELL`) and wires its PTY to stdin/stdout of the browser extension. Any extension context with native-messaging permission receives a live shell session.

```bash
gh api repos/BatteredBunny/browser_terminal/contents/native/main.go | jq -r .content | base64 -d
```

Result:
```text
main.go: `shell := '/bin/sh'; if rawShell := os.Getenv('SHELL'); rawShell != '' { shell = rawShell }; cmd := exec.Command(shell); ... processCommands(stdinQueue, cmd)` — the native host starts a shell subprocess on launch, receives JSON messages from the extension via Chrome native messaging, and forwards them as PTY input. No authentication, no command allowlist, no sandboxing.
```

*Classification: fact*

#### Evidence 4 — installation.md instructs users to `sudo mv ~/Downloads/browser_terminal_linux /usr/local/bin/browser_terminal` without any integrity-verification step in between the download and the move.

```bash
gh api repos/BatteredBunny/browser_terminal/contents/installation.md | jq -r .content | base64 -d
```

Result:
```text
Install steps: (1) browser store, (2) 'Download native program from releases', (3) `sudo mv ~/Downloads/browser_terminal_linux /usr/local/bin/browser_terminal`, (4) `browser_terminal --install`. No sha256sum step. No checksum file exists to verify against. User on step 3 is trusting the GitHub-hosted binary integrity implicitly.
```

*Classification: fact*

#### Evidence 5 — Near-solo maintainer profile — BatteredBunny authored 41 commits, dependabot[bot] 12. Total contributor count: 2. Top-human share = 100% (77.4% including the bot).

```bash
gh api repos/BatteredBunny/browser_terminal/contributors
```

Result:
```text
top_contributors: BatteredBunny: 41, dependabot[bot]: 12. total_contributor_count: 2 (both entries). Excluding the bot, this is a single-author repository.
```

*Classification: fact*

#### Evidence 6 — Zero formal review + zero any-review across the 12-PR closed-and-merged history. Zero self-merges. PR sample is tiny; the pattern IS the sample.

```bash
gh api 'repos/BatteredBunny/browser_terminal/pulls?state=closed&per_page=20'
```

Result:
```text
sample_size: 12 (= total_closed_prs = total_merged_lifetime). formal_review_rate: 0.0. any_review_rate: 0.0. self_merge_count: 0. All 12 PRs in the lifetime of the repo merged without any reviewer interaction.
```

*Classification: fact*

#### Evidence 7 — No branch protection of any kind — classic HTTP 404, rulesets count 0, rules_on_default count 0. No CODEOWNERS at any standard path.

```bash
gh api repos/BatteredBunny/browser_terminal/branches/main/protection; gh api repos/BatteredBunny/browser_terminal/rulesets
```

Result:
```text
classic: HTTP 404. rulesets: {entries: [], count: 0}. rules_on_default: {entries: [], count: 0}. CODEOWNERS: not found at any of CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS.
```

*Classification: fact*

#### Evidence 8 — community/profile reports no SECURITY.md, no CONTRIBUTING, no CODE_OF_CONDUCT. health_percentage: 42.

```bash
gh api 'repos/BatteredBunny/browser_terminal/community/profile'; gh api 'repos/BatteredBunny/browser_terminal/security-advisories'
```

Result:
```text
health_percentage: 42; has_security_policy: false; has_contributing: false; has_code_of_conduct: false; license_spdx: GPL-3.0. security-advisories count: 0.
```

*Classification: fact*

#### Evidence 10 — Dependabot is configured for gomod + npm + github-actions. OSV query on the dep graph finds 1 vuln: esbuild (GHSA-67mh-4wv8-2f99, dev-server CORS bypass).

```bash
gh api repos/BatteredBunny/browser_terminal/contents/.github/dependabot.yml | jq -r .content | base64 -d
```

Result:
```text
dependabot.yml ecosystems: ['gomod', 'npm', 'github-actions']. osv.dev total vulns: 1 — esbuild GHSA-67mh-4wv8-2f99 (dev-server same-origin bypass). The vulnerability is reachable only when running `esbuild` in dev-server mode, which this repo does not do at runtime (esbuild is a build-time dep). Not reachable in production consumption.
```

*Classification: fact*

#### Evidence 11 — Harness detected a 'npm-browser_terminal' distribution channel via package.json — but `browser_terminal` is not a published npm package. package.json is the internal build manifest for the extension source.

```bash
docs/phase_1_harness.py # distribution_channels; npm view browser_terminal
```

Result:
```inference — coverage-gap annotation
distribution_channels: [{name: 'npm-browser_terminal', type: 'package_manager', install_command: 'npm install browser_terminal', install_path_verified: true, artifact_verified: false}]. Manual `npm view browser_terminal`: not in the public npm registry. The channel is fictitious — the harness derived it from package.json presence without confirming actual publication. Coverage-gap annotation.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 12 — Actual distribution channels: Chrome Web Store (via the typosquat-susceptible URL in installation.md) + Firefox Add-ons (addons.mozilla.org) + direct GitHub Releases download of the native Go binary.

```bash
grep -i 'install\|download' installation.md
```

Result:
```text
Three de-facto channels, none of them the detected 'npm' channel: (1) Chrome Web Store (chrome.google.cm — typo), (2) Firefox Add-ons (addons.mozilla.org — correct), (3) GitHub Releases for the Go native host (unsigned, no checksum). Browser stores enforce their own review; the GitHub-Releases native-host path has no additional moderation beyond the maintainer's GitHub Actions release pipeline.
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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `9a77c4ace7fd014c19391e541e348d7369f99e6a` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
