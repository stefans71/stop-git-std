# Security Investigation: WhiskeySockets/Baileys

**Investigated:** 2026-04-20 | **Applies to:** main @ `8e5093c198de5c5c0230a76e8a7224f6006ebb2e` | **Repo age:** 4 years | **Stars:** 9,034 | **License:** MIT

> Baileys — 9k-star reverse-engineered WhatsApp Web client. Critical via F0: using Baileys attaches your WhatsApp account to an unofficial client, violating WhatsApp's ToS + risking account suspension. PR #1996 vulnerability fix stale-closed 148 days, maintainer-promised replacement never shipped. 14 runtime CVEs (ws × 5). Zero governance. 150-day release stall. V13-3 trigger fires.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-Baileys.md` (+ `.html` companion) |
| Repo | [github.com/WhiskeySockets/Baileys](https://github.com/WhiskeySockets/Baileys) |
| Short description | Socket-based TypeScript library for interacting with WhatsApp Web API. Reverse-engineered from WhatsApp's official web client. Published as npm package `baileys`. Consumed by bot authors building WhatsApp automation. |
| Category | `reverse-engineered-api-library` |
| Subcategory | `whatsapp-web-client` |
| Language | JavaScript |
| License | MIT |
| Target user | Node.js/Bun/Deno developer building a WhatsApp automation, bot, or integration. Install: `npm install baileys` → import, provide auth state, connect to WhatsApp Web with consumer's phone-number-linked account. |
| Verdict | **Critical** |
| Scanned revision | `main @ 8e5093c` (release tag ``) |
| Commit pinned | `8e5093c198de5c5c0230a76e8a7224f6006ebb2e` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of Baileys. Eleventh wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21, QuickLook 22, kanata 23, freerouting 24, WLED 25). FIRES V13-3 COMPARATOR-CALIBRATION TRIGGER at 11 wild V1.2 scans. |

---

## Verdict: Critical

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>✗ Critical — F0 is the blocking item for default consumers (1 findings)</strong>
<br><em>Reverse-engineered unofficial WhatsApp client — ToS violation + account-ban risk is inherent to use.</em></summary>

1. **F0** — Library's function is to attach consumer's WhatsApp account to an unofficial client. README's own disclaimer acknowledges the exposure. WhatsApp actively detects + suspends accounts for third-party-client behavior. Not a code vulnerability — a category risk.

</details>

<details>
<summary><strong>⚠ Warning — F1–F6 describe code, supply-chain, and governance posture (6 findings)</strong>
<br><em>Latent exec pattern; unresolved community security-fix PR; 14 runtime-dep CVEs; zero governance; 150-day release stall; missing disclosure policy.</em></summary>

1. **F1** — extractVideoThumb uses child_process.exec with shell-interpolated template string. Currently callers pass tmpdir paths (safe). Latent command-injection if anyone threads external paths through.
2. **F2** — PR #1996 'Vulnerability Fixes' stale-closed after 148 days. purpshell's promised 'own version' never materialized. Library still ships deprecated `request` chain with 2 CVEs.
3. **F3** — 14 known CVEs across 6 runtime deps: `ws` × 5 (core WebSocket), protobufjs × 4, request × 2, acorn, music-metadata, @hapi/boom (EOL).
4. **F4** — Zero branch protection + 0 rulesets + no CODEOWNERS + no SECURITY.md/CONTRIBUTING/CoC + 89.5% top-2 maintainer concentration.
5. **F5** — 150-day release stall: v7.0.0-rc.9 (2025-11-21) is npm @latest; v6.7.21 stable (2025-11-06) is 165 days old; master 5 months ahead.
6. **F6** — No SECURITY.md in 4 years + 0 published GHSA + documented stale-out of vulnerability-fix PR → structural silent-fix posture.

</details>

<details>
<summary><strong>ℹ Info — F7 (1 findings)</strong>
<br><em>Scanner coverage gaps (PR sample empty, vendor_keys FP on WhatsApp dictionary, install-snippet noise).</em></summary>

1. **F7** — Harness PR sample returned 0 despite 352 merged lifetime; direct gh api queried as fallback. vendor_keys FP on `AIza...` WhatsApp protocol dictionary entry. install_script_analysis flagged stale README content.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — 0 branch protection + 0 rulesets + no CODEOWNERS + 89.5% top-2 maintainer concentration; PR sample empty (harness gap E8) |
| Is it safe out of the box? | ❌ **No** — using Baileys attaches consumer's WhatsApp account to a reverse-engineered unofficial client; ToS-violation + account-ban risk on default path (F0) |
| Do they fix problems quickly? | ❌ **No** — PR #1996 vulnerability-fix stale-closed after 148 days; 14 runtime-dep CVEs (ws × 5, protobufjs × 4); 150-day release stall on v7.0.0-rc.9 |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md + no CONTRIBUTING + 0 advisories in 4 years + documented vulnerability-fix PR stale-out (F2, F6) |

---

## 01 · What should I do?

> 9.0k⭐ · MIT · TypeScript · 1 critical · 5 warnings · 1 info · CRITICAL
>
> Baileys is a 4-year-old reverse-engineered TypeScript library for WhatsApp Web — 9k stars, 100 contributors, maintained by purpshell after original author adiwajshing went inactive. Critical verdict is category-driven: using Baileys attaches the consumer's WhatsApp account to an unofficial client, and WhatsApp's Terms of Service prohibit non-official clients + actively detect and suspend accounts showing third-party-client behavior. The README itself carries a CAUTION-flagged disclaimer acknowledging this exposure (F0). Beyond the category risk, the library has a latent command-injection pattern in ffmpeg-based video-thumbnail extraction (F1), a documented unresolved vulnerability-fix PR #1996 stale-closed after 148 days with the maintainer's promised 'own version' never delivered (F2), 14 known CVEs across 6 runtime deps including 5 on `ws` (the core WebSocket library, F3), zero branch protection + zero rulesets + no CODEOWNERS/SECURITY.md/CONTRIBUTING (F4), a 150-day release stall (F5), and a structural silent-fix disclosure posture (F6). Positive signals: 100 contributors, Copilot PR review workflow active, npm-registry-verified primary distribution channel, explicit maintainer disclaimer of ToS-endorsement.

### Step 1: Do NOT attach a primary WhatsApp account to any Baileys-based bot (🚨)

**Non-technical:** Baileys is a reverse-engineered client. WhatsApp bans accounts it detects using third-party clients. If you care about keeping your WhatsApp number, do not link it to Baileys. Use a burner number that you're prepared to lose. Do not use Baileys for mass-messaging, stalkerware, or any pattern the README explicitly discourages.

```text
# Nothing to run — this is a use-model rule
```

### Step 2: Install the stable npm package with a pinned version (⚠)

**Non-technical:** Use `npm install baileys@6.7.21` (the last non-RC stable) or `npm install baileys@7.0.0-rc.9` (current RC). Avoid `npm install baileys` without a version — the `@latest` tag resolves to the RC, which has had 150 days of accumulated bug reports against it.

```bash
npm install baileys@6.7.21 --save-exact
```

### Step 3: Override deprecated `request` dep via npm overrides (⚠)

**Non-technical:** The `request` package is deprecated since 2020 and has 2 known CVEs. PR #1996 offered to remove it; the PR stalled. You can override it in your own package.json to avoid pulling it into your install graph. (Note: `request` is only pulled via proto-extract/ — if you don't run proto-extract, you won't have it in your runtime.)

```text
# package.json: { "overrides": { "request": "npm:no-op@1.0.0" } }
```

### Step 4: Run `npm audit` and track the `ws` library specifically (⚠)

**Non-technical:** `ws` is the core WebSocket library — Baileys uses it for every connection to WhatsApp. It has 5 known CVEs at the current pin. Check upstream `ws` release notes and override to the latest patch release when you install.

```bash
npm audit && npm view ws versions --json | tail -5
```

### Step 5: Isolate your Baileys bot in a container with no other credentials (⚠)

**Non-technical:** Because Baileys holds your WhatsApp session, any vulnerability in Baileys or its deps could leak the session. Run your bot in a minimal Docker container, persist ONLY the Baileys auth state (no other secrets), and rotate the session if you suspect exposure. Don't run it on your daily-driver workstation.

```bash
docker run --rm -v ./auth_info:/app/auth_info -w /app node:20-alpine sh -c 'npm install baileys@7.0.0-rc.9 && node your-bot.js'
```

### Step 6: Evaluate the official WhatsApp Business Platform API for production use (ℹ)

**Non-technical:** If you're using Baileys for business automation, the official WhatsApp Business Platform API (https://business.whatsapp.com/) is the ToS-compliant path. It costs money and has friction that Baileys doesn't, but it doesn't risk account bans and has documented SLAs.

```text
# https://business.whatsapp.com/ for enrollment
```

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 6 Warning · ℹ 1 Info
>
> 8 findings total.
### F0 — Critical · Vulnerability — Reverse-engineered, unofficial WhatsApp client — ToS violation + account-ban risk is inherent to use; maintainers explicitly disclaim endorsement

*Continuous · Since Baileys was created 2022-01-12 · → Do NOT attach a personal WhatsApp account you rely on to a Baileys-based bot. Use a burner number; understand that account suspension is a documented outcome of third-party client use.*

The category matters here more than any specific line of code. Baileys is a reverse-engineered TypeScript library that speaks WhatsApp's Web protocol on behalf of a consuming user's own WhatsApp account. The GitHub topic list includes `reverse-engineering` — the maintainers classify the project this way themselves. The npm page for `baileys` lists purpshell as the current maintainer; the README names 'Rajeh Taher/WhiskeySockets' as the copyright holder (Rajeh is purpshell).

The README also contains a CAUTION-flagged disclaimer that would be unusual for most libraries: 'This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with WhatsApp or any of its subsidiaries or its affiliates… The maintainers of Baileys do not in any way condone the use of this application in practices that violate the Terms of Service of WhatsApp. The maintainers of this application call upon the personal responsibility of its users to use this application in a fair way, as it is intended to be used.' The disclaimer's existence is itself evidence: the authors know the category carries platform-operator risk.

WhatsApp's actual Terms of Service prohibit non-official clients — any third-party automation accessing user accounts is already out-of-ToS from WhatsApp's perspective, regardless of how 'fair' the usage is. WhatsApp has a documented history of detecting and suspending accounts that exhibit third-party-client behavior: unusual connection-fingerprints, missing official-client protocol signals, rate/timing patterns diverging from the official client, message-content patterns suggesting automation. Suspension is typically permanent and unappealable for accounts flagged this way.

The consumer impact is specific. A hobbyist running a Baileys bot on a burner number is at low-cost risk (lose the burner, get another). A business that integrates Baileys with their customer-service number faces catastrophic risk: a single detection event can suspend the number and disconnect the business from a channel their customers expect. The official alternative — the WhatsApp Business Platform API — is authorized but has friction and cost that Baileys' zero-price + direct-API-access doesn't. That trade-off is why the library has 9k stars: it works well, at the cost of standing on a platform whose owner can drop you at any time.

This is why the verdict is Critical on the default consumer path. Most users who install Baileys intend to connect their primary (or business) account — not a burner. The disclaimer is in the README but disclaimers don't change WhatsApp's detection behavior. A user who reads the README carefully, understands the risk, and sets up a burner-number pipeline is at a different severity profile (Warning) than the default consumer. The verdict tracks the default consumer, not the careful one.

**How to fix.** Maintainer-side: no fix exists — the tool's function is inherently ToS-violating. Ongoing maintainer effort (mimicking newer WhatsApp-client fingerprints, update-WhatsApp-version workflow) partially offsets detection pressure but can't resolve the underlying posture. Consumer-side: (1) use burner phone numbers, never primary accounts; (2) don't use Baileys for ToS-prohibited patterns (stalkerware, mass messaging, bulk automation — the README explicitly discourages these); (3) understand that account suspension can happen without notice; (4) if operating a business, evaluate the official WhatsApp Business Platform API as an alternative that's authorized by WhatsApp.

### F1 — Warning · Vulnerability — child_process.exec with shell string-interpolation in extractVideoThumb — latent command-injection pattern

*Continuous · Since messages-media.ts adopted this pattern (early commits 2022-ish) · → If you fork Baileys or extend it with custom media handling, DO NOT pass external file paths to the exported generateThumbnail API. Future maintainers should migrate this call to spawn(argv) form.*

The specific lines are src/Utils/messages-media.ts:125-126: `const cmd = \`ffmpeg -ss ${time} -i ${path} -y -vf scale=${size.width}:-1 -vframes 1 -f image2 ${destPath}\`` immediately followed by `exec(cmd, err => { ... })`. The `exec` import is from `child_process` at line 2 of the same file. `child_process.exec` invokes a shell (`/bin/sh` on Linux); a command string with metacharacters in any interpolated position becomes the shell's problem.

Tracing the current callers: `extractVideoThumb` is invoked from `generateThumbnail` at line 349 with `file` and `imgFilename` parameters. The `file` argument comes from `originalFilePath` (set by `encryptedStream` to `join(tmpdir(), mediaType + generateMessageIDV2() + '-original')`). `imgFilename` is `join(tmpdir(), generateMessageIDV2() + '.jpg')`. `generateMessageIDV2` is defined in src/Utils/generics.ts:182 and returns `'3EB0' + sha256-hex-substring(0, 18)` — no shell metacharacters.

So the library's own callers are safe today. The reason this is still a finding is: (a) the pattern itself is the unsafe form — `spawn('ffmpeg', [...args])` would accomplish the same task with zero shell-injection surface; (b) `generateThumbnail` is an EXPORTED API, meaning library consumers who write their own media flows may pass any string as the `file` argument; (c) any future internal refactor that threads a filename from an incoming WhatsApp message attachment (sender-controlled) into this code path would expose the entire Baileys user base to shell-injection via crafted filenames.

The mitigation is small. `spawn('ffmpeg', ['-ss', time, '-i', path, '-y', '-vf', `scale=${size.width}:-1`, '-vframes', '1', '-f', 'image2', destPath])` has identical semantics, doesn't spawn a shell, and eliminates the category entirely. A code-review checklist item for this file would close it out and prevent regression.

**How to fix.** Maintainer-side: replace `exec(cmd)` with `spawn('ffmpeg', ['-ss', time, '-i', path, '-y', '-vf', `scale=${size.width}:-1`, '-vframes', '1', '-f', 'image2', destPath])` — identical semantics, no shell, no injection surface. Code-review checklist item for future maintenance. Consumer-side: treat generateThumbnail as INTERNAL until this is fixed; don't call with external paths.

### F2 — Warning · Hygiene — Community-submitted vulnerability-fix PR #1996 closed unmerged via stale-bot after 148 days; maintainer-promised replacement never materialized; library still ships deprecated `request` dep

*Ongoing · PR #1996 opened 2025-10-30; stale-closed 2026-03-26; 'own version' not merged in 148 days since purpshell's promise · → If you maintain a downstream fork, apply the PR #1996 changes locally; if you need the deprecated `request` removed from your production chain, patch your node_modules or pin an override.*

The PR #1996 story is worth telling in full because it's the clearest data point about how vulnerability reports get handled in this project. On 2025-10-30, community contributor KaivalyaGauns filed a PR titled 'Vulnerability Fixes' that did one specific thing: replaced the deprecated-since-2020 `request` / `request-promise-core` / `request-promise-native` trio with a modern `node-fetch` + `form-data` pair. The changes were scoped to proto-extract/ (the maintainer build-tool) and were tested against the existing proto-extraction flow.

`request` and its companion packages have 2 known CVEs at Baileys' pinned version: GHSA-p8p7-x288-28g6 (SSRF via redirect) and GHSA-7xfp-9c55-5vqj (TLS certificate validation bypass). The `request` package has been marked deprecated by its own maintainers since 2020 with the recommendation to migrate to alternatives. The PR was the migration.

The whiskeysockets-bot posted its standard welcome comment within seconds: 'Thanks for opening this pull request and contributing to the project! The next step is for the maintainers to review your changes.' Then silence. The first stale-bot warning fired 2025-12-06, 37 days later. Community member vinikjkkj asked 'any updates?' on 2025-12-12. Another stale-bot warning 2025-12-27. Then, on 2026-01-08 — 70 days after the PR was filed — maintainer purpshell commented: 'We should make our own version of this PR. Opening an issue in its stead.'

That comment is the pivot point. The maintainer explicitly acknowledged the fix was needed and took ownership. But no issue was opened in a form the scanner can find; no replacement PR materialized; the original PR drifted toward stale-bot closure through two more warnings and was finally closed 2026-03-26 — 148 days after it was filed, and 77 days after purpshell's commitment.

As of scan date (2026-04-20), master's proto-extract/package.json still contains `request`, `request-promise-core`, and `request-promise-native` — confirmed by the Phase 1 harness dependency inventory. The 'own version' did not happen in 102 days since purpshell's comment.

This matters for two reasons. First, the SSRF and TLS-cert CVEs remain in the deployed dep graph; users who run proto-extract/ (typically maintainers refreshing WAProto definitions, but also anyone forking for the same purpose) pull the vulnerable code. Second, as a datapoint about how disclosure-and-fix works here, this is the kind of signal that motivates Q3's red. The stale-bot-closes-a-working-fix pattern is distinguishable from 'busy maintainer, fix in progress.' The former is the observed pattern.

**How to fix.** Maintainer-side: revive PR #1996 (cherry-pick from its diff) or author the promised 'own version'. Consumer-side: override `request` via npm overrides or use a fork that applies the fix.

### F3 — Warning · Vulnerability — 14 known CVEs across 6 direct runtime deps — `ws` (5 CVEs) is the core WebSocket library for a WebSocket-based client

*Continuous · Ongoing — dep pins in package.json at HEAD 8e5093c · → If running Baileys in production, pin dep versions with `npm audit fix` or overrides; check upstream `ws` release notes for the 5 GHSAs; consider blocking `@hapi/boom` 9.x upgrade path since that major is EOL.*

Running Baileys' package.json through osv.dev produces 14 CVE records across 6 runtime dependencies at their pinned versions. The distribution: `ws` (^8.13.0) has 5 vulns, `protobufjs` (^7.2.4) has 4, `request` (^2.88.0 via proto-extract) has 2, `acorn` (^8.15.0 via proto-extract) has 1, `music-metadata` has 1, `@hapi/boom` (^9.1.3, on EOL 9.x major) has 1.

The `ws` count matters most. `ws` is the WebSocket library Baileys uses for every connection to WhatsApp Web — it's the central transport. The 5 GHSAs on `ws` at Baileys' pin include DoS-via-header-size classes and memory-issue classes. Whether any are reachable depends on Baileys' usage patterns, but the cumulative surface is nontrivial on the single library that carries all of Baileys' traffic.

The maintainer-side signal is that there's no `.github/dependabot.yml` present. The GitHub Actions 'Dependabot Updates' workflow IS listed as active, which likely means GitHub's default security-update-only behavior — Dependabot will open PRs for security advisories affecting the current pins but won't track general dep updates. Compare to freerouting (entry 24) where an explicit dependabot.yml on `gradle` surfaced 5 open dep-bump PRs at scan time. Baileys has 0 open Dependabot-authored PRs at scan — consistent with the no-explicit-config state.

Consumer mitigation is straightforward: pin exact versions via `npm install --save-exact`, run `npm audit` regularly, use npm `overrides` to force specific `ws` and `protobufjs` versions. The structural fix is on the maintainer side: add `.github/dependabot.yml` explicitly tracking npm, bump `ws` to a version clearing the 5 GHSAs, replace `@hapi/boom` 9.x with 10.x (actively maintained), and close out F2 to drop the `request` chain.

**How to fix.** Maintainer-side: add .github/dependabot.yml scoping npm ecosystem to trigger automated dep-bump PRs; prioritize `ws` upgrade to a version clearing the 5 GHSAs; replace `@hapi/boom` 9.x with 10.x; close out F2 (PR #1996) to drop `request`. Consumer-side: npm overrides + audit fix.

### F4 — Warning · Governance — Zero branch protection + zero rulesets + no CODEOWNERS + 89.5% top-2 maintainer concentration

*Continuous · Since repo creation 2022-01-12 · → Pin to a specific released version (v7.0.0-rc.9 or v6.7.21); never install from master or github:-form without a SHA pin.*

The governance state is straightforward: nothing is configured. `gh api repos/WhiskeySockets/Baileys/branches/master/protection` returns HTTP 404 (no classic branch protection). `gh api repos/WhiskeySockets/Baileys/rulesets` returns zero entries. No CODEOWNERS file at any of the standard locations (root, .github/, docs/, .gitlab/). Community health sits at 50% because CONTRIBUTING, CODE_OF_CONDUCT, and SECURITY.md are all absent.

Contributor concentration is high: adiwajshing 71.1% + purpshell 18.4% = 89.5% of top-6 commits. adiwajshing is the original author (the repo's early commits and `inspired from whatsmeow` references in generics.ts trace back to adiwajshing's early work); they appear inactive in the recent timeline. purpshell is the named active maintainer — the README explicitly calls him the 'current maintainer,' the paid-support channel at purpshell.dev/book routes to him, and the copyright attribution names him. jlucaso1 is a distant-third contributor (45 commits) who appears in recent merge activity. Effectively, the project is single-active-maintainer with one secondary contributor occasionally in the merge pipeline.

The attack surface from this combination is: a compromised purpshell account (phishing, credential theft, session hijack) has direct push access to master with no ruleset requiring peer review, and — via the publish-release.yml workflow — can publish to npm under the `baileys` name. The time from malicious push to npm-registry-available is whatever the release workflow takes, typically minutes. Downstream consumers who installed `baileys@latest` or `baileys@^7.0.0-rc.9` would begin pulling the compromised version on their next install or rebuild.

The structural fix is a 3-line ruleset edit: add a `pull_request` rule requiring at least 1 approving reviewer, add a CODEOWNERS file naming purpshell + jlucaso1 for core paths, enable classic branch protection as backup. For context on how achievable this is: kamal (entry 18) added Copilot Reviews as a ruleset-enforced review gate; ghostty (entry 16) has a 4-rule ruleset; kanata (entry 23) has a ruleset requiring PR review. Baileys doesn't — this is a category-wide choice, not a technical limitation.

**How to fix.** Maintainer-side: add a ruleset on master requiring `pull_request` review with ≥1 approving reviewer; add CODEOWNERS naming purpshell + jlucaso1 for core; enable classic BP as backup; add SECURITY.md naming GitHub's Report-a-vulnerability UI. Consumer-side: pin `baileys` to a specific semver (not ^range), use npm lockfiles, rebuild downstream containers on known-safe dep graphs.

### F5 — Warning · Structural — 150-day release stall — v7.0.0-rc.9 from 2025-11-21 is `@latest` on npm while master is 5 months ahead

*Ongoing · Since 2025-11-21 (last tag) — 150 days · → If you want master-branch fixes, pin to a commit SHA via `yarn add github:WhiskeySockets/Baileys#SHA`; if you want semver stability, v6.7.21 is the last non-RC stable.*

The latest release on any channel is v7.0.0-rc.9 on 2025-11-21 — 150 days before the scan. npm serves this as `@latest` for `npm install baileys`. The last non-RC stable release is v6.7.21 on 2025-11-06, 165 days before scan. Master has been continuously pushed through 2026-04-19 (one day before scan), so the project is clearly active; the gap is in the release-tagging step.

v7.0.0 has been in RC for 5 months. The RC cycle moved fast initially (rc.3 → rc.9 in 2.5 months, September through November 2025) and then stopped. There's no public explanation for the stop. Meanwhile master has accumulated ~5 months of work that doesn't reach any npm consumer.

The practical impact: consumers on `baileys@latest` are using a 5-month-old snapshot. Any fixes merged to master since 2025-11-21 (including a hypothetical PR #1996 replacement, if purpshell's 'own version' ever materializes) aren't available until a new RC or stable is cut. For a library where one of the scan findings is 'community security-fix PR stale-closed' (F2), the fix-to-user latency is compounded: even if a fix DID merge to master, consumers don't see it until the release cadence resumes.

The publish-release.yml workflow appears automated — it's not a technical blocker. The decision to cut v7.0.0 (or a v7.0.0-rc.10, or a v6.7.22 backport) is a human-process bottleneck on the maintainer. Same structural pattern as wezterm (entry 21, 807-day stall on a single author) and freerouting (entry 24, 373 days with a functioning automated release workflow).

**How to fix.** Maintainer-side: cut v7.0.0 (or v6.7.22) to push accumulated main-branch work to consumers; the publish-release.yml workflow appears automated — it's a human-decision bottleneck. Consumer-side: pin to a specific master SHA via `yarn add github:WhiskeySockets/Baileys#SHA` if you need master-branch state.

### F6 — Warning · Hygiene — No SECURITY.md + 0 advisories in 4 years + documented stale-out of a vulnerability-fix PR (F2) = structural silent-fix posture

*Continuous · Since 2022-01-12 · → Researchers finding Baileys-specific vulnerabilities: use GitHub's Report-a-vulnerability UI, but don't rely on rapid response — PR #1996's pattern suggests a 4-5 month cycle to resolution if any.*

No SECURITY.md exists in any of the standard locations (root, .github/, docs/). 0 GHSA security advisories have been published against Baileys across its 4-year history. For context, 11 of 11 V1.2 wild-scan catalog entries share this silent-fix pattern — it's now the dominant community norm for this catalog's shape — but Baileys provides the clearest single data point about WHY this happens in practice.

PR #1996 (covered in F2) is the specific mechanism observable here. An external security researcher identified a real vulnerability class (deprecated-dep CVEs) and offered a tested fix. The maintainer engaged (eventually) with a plan to do it themselves. The PR stale-out-closed. The plan didn't materialize. Had this PR been merged, it would have been a natural moment to file a GHSA against the fixed-version-range of `request`. That didn't happen because the fix didn't happen.

The longer-run consequence: researchers who come to the same conclusion in the future have a specific data point about how their contribution is likely to be received. The lowest-friction action for a future researcher is to publicly disclose without filing a PR (since the PR route doesn't seem to land fixes). That's a significant upstream shift and it's the opposite of what a healthy disclosure process looks like.

The fix is cheap: a 1-page SECURITY.md naming GitHub's built-in 'Report a vulnerability' UI + expected response window + the commercial-support escalation path (purpshell.dev/book). Plus a follow-through on PR #1996 (merge it, or actually author the replacement). Both are hours of work.

**How to fix.** Maintainer-side: 1-page SECURITY.md naming the GitHub advisory UI + expected response window + the commercial-support path (purpshell.dev/book) as escalation option. Publish GHSAs when vulns are confirmed. Close out PR #1996-class threads either by merging the community PR or by publishing the 'own version' with clear attribution to the researcher.

### F7 — Info · Coverage — Scanner gaps: vendor-keys false-positive on WhatsApp protocol dictionary; harness PR sample returned empty despite 352 merged; README install-pathway detection noise

*Continuous · Scanner tooling gap · → Scanner-calibration notes for V1.2.x backlog.*

Three scanner coverage gaps documented for this scan, in order of relevance:

(1) Harness PR review sample returned 0 captures despite 352 lifetime merged PRs. The fallback was direct `gh api` queries against the pulls endpoint. The root cause is likely the sampler's filtering heuristic when the closed-PR stream is dominated by closed-without-merge (observed: ~88% of 50 most-recent closed PRs are closed without merging). The sampler presumably filters for `merged_at != null` on a fixed window; if the window is dominated by unmerged closes, the merged-PR count falls to zero.

(2) vendor_keys regex false-positive on `AIzaSyDR5yfaG7OG8sMTUj8kfQEb8T9pN8BM6Lk` at src/WABinary/constants.ts:601. The context is a WhatsApp Web protocol compression dictionary — a JavaScript array of pre-shared short tokens used by the binary format. The Google-API-key regex matches the string by coincidence. Fix: require proximity context (assignment to a variable matching `*_KEY|apiKey|GOOGLE_*`; `process.env.*` reference; URL embedding) rather than string-in-array-literal.

(3) install_script_analysis flagged `yarn add github:WhiskeySockets/Baileys` as a master-tracking install pattern; the current root README doesn't contain that snippet. The harness is likely extracting from a historical README version in tarball metadata or from a separate doc file. Fix: version-check install-snippet inputs against the current README SHA.

None of these gaps changed the verdict — Phase 4 used direct gh api fallback for PR analysis, dismissed the vendor_keys FP, and noted the install-snippet FP. All three are V1.2.x calibration items for the scanner, not Baileys defects.

**How to fix.** Scanner-side: (a) vendor_keys regex should require proximity signal (assignment context, `API_KEY` variable name, URL embedding) rather than array-literal context; (b) PR sampler needs a failure-mode handler when closed-without-merge dominates the stream; (c) install_script_analysis should version-check its inputs against the current README SHA.

---

## 02A · Executable file inventory

> Baileys ships as an npm library — no standalone executable. Consumers install via `npm install baileys` and import TypeScript/JavaScript modules. A secondary npm package `whatsapp-web-protobuf-extractor` is the build-tool used internally to extract WhatsApp Web's protobuf definitions; most library consumers don't use it directly.

### Layer 1 — one-line summary

- The library's primary attack surface is the npm supply chain (governance from F4) and the library's own internal code (F1 exec pattern). Execution context is the consumer's Node/Bun/Deno process. No native binary distribution.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `src/Utils/messages-media.ts` | library-module | Node.js / Bun / Deno | `child_process.exec(cmd)` where cmd is a shell-interpolated template string referencing filesystem paths (lines 125-126). Currently callers use tmpdir-safe paths; pattern is latent risk. — F1 | None | `extractVideoThumb` spawns ffmpeg via shell; exported `generateThumbnail` is the public API that routes to this. |
| `src/Socket/messages-recv.ts` | library-module | Node.js / Bun / Deno | `exec(node, false)` at line 1497 — note this is a LOCAL function named exec, NOT child_process.exec (grep FP). Actually processes a WhatsApp binary protocol node. | WhatsApp Web WebSocket | Core message-receive handler. The `exec` match is a false-positive on the grep; real call is internal dispatcher. |
| `src/WABinary/constants.ts` | library-module | Node.js / Bun / Deno | None actually. Contains WhatsApp protocol compression dictionary that includes an `AIza...` lookalike string — a Google-API-key regex FP — F7/E11. | None | Dictionary of pre-shared binary-protocol tokens. |
| `proto-extract/index.js` | build-tool | Node.js (dev-time) | Uses deprecated `request-promise-native` to fetch WhatsApp Web assets; PR #1996 proposed migration to node-fetch — stale-closed (F2). | HTTP to web.whatsapp.com to extract latest protobuf definitions | Build-tool used to refresh WAProto/ from WhatsApp Web's JavaScript. Only used by maintainers; consumers of the `baileys` package don't run this. |
| `.github/workflows/pr-comment.yml` | ci-workflow | GitHub Actions | `pull_request_target` trigger + no permissions block + 2 tag-pinned actions (not SHA-pinned) | Posts PR comments | Adds standard welcome/CLA comment on PRs. pull_request_target + no-permissions + tag-pinned 3rd-party combo is known-risky pattern (E9). |

Install path: `npm install baileys` (primary). Baileys pulls its own dep graph including `ws` (5 CVEs, F3) as the core WebSocket library. Consumer imports: `import makeWASocket from 'baileys'` → `makeWASocket({auth, logger})` → connects to WhatsApp Web with consumer's account state. See F0 for ToS-violation + account-ban risk inherent to this flow.

---

## 03 · Suspicious code changes

> Baileys PR review analysis: harness auto-sample returned 0 despite 352 lifetime merges (F7/E8 harness gap). Phase 4 fell back to direct gh api queries. Pattern on 50 most-recent closed PRs: ~12% merge rate, ~88% closed-without-merge — most community PRs are either closed by maintainer review or by stale-bot after 28+ days inactivity. Few PRs carry APPROVED formal-review decisions (review_decision is frequently null on even merged PRs). 6 security-keyword-flagged PRs were identified: #873 (axios), #874 (sharp), #902 (auth-utils), #1996 (Vulnerability Fixes — F2), #2153 (auth-utils memory leak), #2429 (docs auth, open-stale).

Sample: the 0 most recent merged PRs at scan time, plus flagged PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1996](https://github.com/WhiskeySockets/Baileys/pull/1996) | Vulnerability Fixes — replace deprecated `request`/`request-promise-*` with `node-fetch`+`form-data` (KaivalyaGauns) | KaivalyaGauns | [STALE-CLOSED] | purpshell comment 2026-01-08: 'We should make our own version of this PR. Opening an issue in its stead.' | Vulnerability-fix PR stale-closed after 148 days; 'own version' never merged; `request` still in master — F2 |
| [#2443](https://github.com/WhiskeySockets/Baileys/pull/2443) | fix: respect caller-provided waveform for PTT audio messages (AshishKumarD) | AshishKumarD | (auto-merge null merger) | review_decision: null | Sample merged PR — no APPROVED decision visible |
| [#2373](https://github.com/WhiskeySockets/Baileys/pull/2373) | Fix ack handling (jlucaso1) | jlucaso1 | (auto-merge null merger) | review_decision: null | Core-contributor self-merge without formal review |
| [#873](https://github.com/WhiskeySockets/Baileys/pull/873) | Fix: axios vulnerability (analyzing, don't merge) — external researcher | external-contrib | [CLOSED-UNMERGED] | Maintainer closed — 'analyzing, don't merge' | Security-flagged closed-unmerged |
| [#874](https://github.com/WhiskeySockets/Baileys/pull/874) | Fix: sharp vulnerability in libwebp dependency (analyzing, don't merge) | external-contrib | [CLOSED-UNMERGED] | Same pattern as #873 | Security-flagged closed-unmerged |
| [#2429](https://github.com/WhiskeySockets/Baileys/pull/2429) | docs(auth): document custom auth state requirements | external-contrib | [OPEN-STALE] | Stale-labeled | Security-keyword PR drifting toward stale-bot closure (auth = keyword match) |

---

## 04 · Timeline

> ✓ 1 good · 🟡 6 neutral · 🔴 4 concerning
>
> Baileys lifecycle — 4-year project with adiwajshing handoff to purpshell; recent timeline dominated by v7.0.0 RC cycle + community security-fix PRs being closed-unmerged or stale-closed.

- 🟡 **2022-01-12 · Repo created (adiwajshing)** — Original creator
- 🔴 **2024-06-14 · PR #873 (axios vuln) closed** — External sec-fix closed
- 🔴 **2024-06-14 · PR #874 (sharp vuln) closed** — External sec-fix closed
- 🟡 **2025-09-14 · v7.0.0-rc.3 released** — v7 RC cycle begins
- 🟡 **2025-10-30 · PR #1996 (Vuln Fixes) filed** — KaivalyaGauns remove `request`
- 🟡 **2025-11-06 · v6.7.21 stable released** — Last non-RC release
- 🟡 **2025-11-21 · v7.0.0-rc.9 released** — Latest; 150d before scan
- 🔴 **2026-01-08 · purpshell: 'our own version'** — Not fulfilled in 102 days
- 🔴 **2026-03-26 · PR #1996 stale-closed** — 148 days; no replacement
- 🟢 **2026-04-19 · Last push to master** — Main still active
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan entry 26

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 9,034 | None |
| Open issues | 313 | 0 security-tagged |
| Open PRs | 100+ | 1 `Stale`-labeled (#2429 docs auth); many community PRs stale out |
| Primary language | JavaScript/TypeScript | None |
| License | MIT | Code license; ToS-violation risk is separate from license |
| Created | 2022-01-12 | ~4 years |
| Last pushed | 2026-04-19 | Day before scan |
| Default branch | master | None |
| Repo size | ~231 MB | None |
| Total contributors | 100 | None |
| Top contributor | adiwajshing 71.1% | Original author, now inactive |
| Active maintainer | purpshell (18.4%) | Named in README; paid-support flow |
| Top-2 concentration | 89.5% | None |
| Solo-maintainer flag | FALSE | 71.1% < 80% threshold |
| Formal releases | 42 | Mix of stable + rc |
| Latest release | v7.0.0-rc.9 (2025-11-21) | 150 days before scan — F5 |
| Latest stable | v6.7.21 (2025-11-06) | 165 days before scan |
| Classic branch protection | OFF (HTTP 404) | None |
| Rulesets | 0 | No rulesets — F4 |
| Rules on default branch | 0 | None |
| CODEOWNERS | Absent | None |
| SECURITY.md | Absent | 4 years; F6 |
| CONTRIBUTING | Absent | None |
| CODE_OF_CONDUCT | Absent | None |
| Community health | 50% | Median V1.2 catalog |
| Workflows | 12 | Incl. Copilot code review + pr-comment.yml (pull_request_target) |
| pull_request_target usage | 1 | pr-comment.yml — E9 |
| SHA-pinned actions | 0 | Across 9 workflow files |
| Tag-pinned actions | 25 | None |
| Dependabot config (.yml) | Absent | Workflow active in default mode |
| Runtime dep CVEs | 14 (across 6 packages) | F3 (ws × 5, protobufjs × 4, request × 2) |
| PR review rate (harness sample) | N/A (sample empty) | Harness gap — E8 |
| PR merge rate (direct query, ~50 recent) | ~12% | Most closed PRs are closed-WITHOUT-merge |
| Total merged PRs lifetime | 352 | None |
| Published security advisories | 0 | 4 years; 11/11 V1.2 silent-fix pattern |
| Flagged security PRs (closed) | 6 | Incl. #1996 Vulnerability Fixes stale-closed — F2 |
| Documented disclaimer | README lines 32-38 | Explicit ToS-risk acknowledgement — F0 |
| OSSF Scorecard | Not indexed | None |
| Primary distribution | npm: `baileys` v7.0.0-rc.9 + `whatsapp-web-protobuf-extractor` v1.0.0 | Both verified on npm registry |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 7 documented gaps. Most significant: empty PR review sample despite 352 lifetime merges (F7/E8), worked around via direct gh api queries.

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit |
| Tarball extraction + local grep | ✅ Scanned |
| OSSF Scorecard | ⚠ Not indexed |
| Dependabot alerts | ⚠ Admin scope (403); no .github/dependabot.yml |
| osv.dev dependency queries | ✅ 28 queries across runtime+dev — 14 CVEs surfaced on runtime deps (F3) |
| PR review sample | ✗ **Empty sample** (0 of 352 merged lifetime captured) — harness gap (F7 / E8). Direct gh api analysis: ~12% merge rate on recent closed. |
| Dependencies manifest detection | ✅ 5 manifests (package.json x2, yarn.lock x2, package-lock.json) — includes proto-extract/ inner package |
| Distribution channels inventory | ✅ 2 channels both verified on npm registry (baileys + whatsapp-web-protobuf-extractor) |
| Dangerous-primitives grep (15 families) | ⚠ 2 exec hits (1 latent — F1 ffmpeg interpolation), 2 deserialization (libsignal safe), 14 network (self-documentation), 1 secrets (WAProto token constant — benign), 1 vendor_keys (WhatsApp dictionary entry — FP, F7/E11), 1 weak_crypto (md5 for version hash — non-crypto use) |
| Workflows | ✅ 12 detected (9 with content); 1 pull_request_target (pr-comment.yml); 0 SHA-pinned of 25 tag-pinned |
| AI-governance tooling | ✅ Copilot code review workflow active (dynamic; GitHub AI review of PRs) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No suspicious paste-from-command blocks |
| Prompt-injection scan on agent files | ⊘ N/A — no AGENTS.md or copilot-instructions.md found |
| Tarball extraction | ✅ 170 files |
| osv.dev | ℹ  |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4946/5000 remaining |

**Gaps noted:**

1. Harness PR review sample returned 0 captures despite 352 merged PRs lifetime — likely a filtering or paging issue when closed-without-merge dominates the closed-PR stream (88% of recent 50). Phase 4 fell back to direct gh api PR analysis.
2. vendor_keys regex matched `AIza...` pattern in WhatsApp protocol compression dictionary (src/WABinary/constants.ts:601) — a false positive; context is a pre-shared token array, not an active API key.
3. install_script_analysis flagged `yarn add github:WhiskeySockets/Baileys` as a master-tracking install pattern; the current root README does not contain this snippet (likely pulled from CHANGELOG or historical README content in tarball).
4. OSSF Scorecard not indexed — governance signals derived from raw gh api data.
5. Dependabot alerts API required admin scope (403); no .github/dependabot.yml present to inspect ecosystems tracked.
6. Gitleaks secret-scanning not available on this scanner host.
7. Q4 signal `q4_has_critical_on_default_path` doesn't auto-fire from reverse-engineered-API-library category signals — Phase 4 authored the override (signal_vocabulary_gap). A compute derivation watching for README disclaimers + platform-operator-API install paths would close this signal class.

---

## 07 · Evidence appendix

> ℹ 11 facts · ★ 3 priority

Command-backed evidence from Phase 1 harness + gh api + direct file fetches of messages-media.ts, constants.ts, pr-comment.yml, README, and PR #1996 comment thread.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — Baileys is explicitly a reverse-engineered, unofficial WhatsApp Web library. The GitHub topic list includes `reverse-engineering`. The README carries a CAUTION-flagged disclaimer: 'This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with WhatsApp' + 'The maintainers of Baileys do not in any way condone the use of this application in practices that violate the Terms of Service of WhatsApp.' Consumer who uses Baileys is attaching their WhatsApp account to an unofficial client.

```bash
gh api repos/WhiskeySockets/Baileys --jq '.topics'; gh api repos/WhiskeySockets/Baileys/readme | jq -r .content | base64 -d | head -40
```

Result:
```text
topics: ['bun', 'deno', 'nodejs', 'reverse-engineering', 'typescript', 'websockets', 'whatsapp-web', 'ws']. README lines 32-38 contain the disclaimer quoted above. Copyright: 'Copyright (c) 2025 Rajeh Taher/WhiskeySockets' (Rajeh = purpshell, current active maintainer). License: MIT (free to redistribute) — but MIT only governs the code itself; the WhatsApp-ToS risk is inherent to using the code, independent of license.
```

*Classification: fact*

#### ★ Evidence 3 — Security-motivated dep-modernization PR #1996 'Vulnerability Fixes' (by KaivalyaGauns, opened 2025-10-30) was closed unmerged 2026-03-26 via stale-bot after 148 days. The PR replaced the deprecated `request`/`request-promise-core`/`request-promise-native` chain (with known CVEs GHSA-p8p7-x288-28g6 SSRF + GHSA-7xfp-9c55-5vqj credential leak) with `node-fetch` + `form-data`. Maintainer purpshell commented 2026-01-08: 'We should make our own version of this PR. Opening an issue in its stead.' As of scan date, master still ships `request` as a runtime dep in proto-extract/.

```bash
gh api repos/WhiskeySockets/Baileys/pulls/1996/files; gh api repos/WhiskeySockets/Baileys/issues/1996/comments
```

Result:
```text
PR #1996 modifies: package.json (+form-data), proto-extract/index.js (switch from request-promise-native to node-fetch + form-data), proto-extract/package-lock.json + package.json (remove request + request-promise-core + request-promise-native, add node-fetch 2.7.0 + form-data 4.0.4), yarn.lock (large diff). Comments timeline: opened 2025-10-30 by KaivalyaGauns; stale bot warnings 2025-12-06 and 2025-12-27; vinikjkkj asked 'any updates?' 2025-12-12; purpshell 'We should make our own version of this PR. Opening an issue in its stead' 2026-01-08; two more stale warnings; closed 2026-03-26 by stale-bot. No replacement PR was merged — current master proto-extract/package.json still contains `request`/`request-promise-core`/`request-promise-native` (confirmed in Phase 1 harness dependency inventory).
```

*Classification: fact*

#### ★ Evidence 5 — Zero governance gates: classic branch protection HTTP 404, 0 rulesets, 0 rules on default branch, no CODEOWNERS, no SECURITY.md, no CONTRIBUTING, no CODE_OF_CONDUCT. community health_percentage=50%. Top-2 maintainer concentration: adiwajshing 1166 commits (71.1%) + purpshell 302 (18.4%) = 89.5% — concentrated but not solo. adiwajshing (original author) appears inactive in recent timeline; purpshell is the current active maintainer (README copyright 'Rajeh Taher/WhiskeySockets' = purpshell).

```bash
gh api repos/WhiskeySockets/Baileys/branches/master/protection; gh api repos/WhiskeySockets/Baileys/rulesets; gh api repos/WhiskeySockets/Baileys/community/profile; gh api repos/WhiskeySockets/Baileys/contributors?per_page=6
```

Result:
```text
classic: 404. rulesets.count: 0. rules_on_default.count: 0. CODEOWNERS: absent (checked root, .github/, docs/). community_profile: {health_percentage: 50, has_code_of_conduct: false, has_contributing: false, has_security_policy: false}. Top-6 contributors: adiwajshing (1166), purpshell (302), github-actions[bot] (52), jlucaso1 (45), canove (44), edgardmessias (30). total_contributor_count: 100. adiwajshing is listed but the original creator ('inspired from whatsmeow' comments show lineage); purpshell is the current active maintainer (README explicitly names him, has paid-support channel at purpshell.dev/book).
```

*Classification: fact*

### Other evidence

#### Evidence 2 — Command-injection pattern in extractVideoThumb: `cmd = \`ffmpeg -ss ${time} -i ${path} -y -vf scale=${size.width}:-1 -vframes 1 -f image2 ${destPath}\`` followed by `exec(cmd, err => {...})` at src/Utils/messages-media.ts lines 125-126. Current callers use tmpdir+randomID-derived paths (safe), but the pattern itself uses `child_process.exec` with string interpolation — any future caller (or consumer using the exported generateThumbnail API) that passes external path strings would expose shell-injection via filename metacharacters.

```bash
gh api repos/WhiskeySockets/Baileys/contents/src/Utils/messages-media.ts | jq -r .content | base64 -d | sed -n '115,135p'
```

Result:
```text
Line 118: `const extractVideoThumb = async (path: string, destPath: string, time: string, size: {width, height})`. Line 125: `const cmd = \`ffmpeg -ss ${time} -i ${path} -y -vf scale=${size.width}:-1 -vframes 1 -f image2 ${destPath}\``. Line 126: `exec(cmd, err => {...})`. Caller (src/Utils/messages.ts:254-259) uses `originalFilePath` from encryptedStream (which sets it to `join(tmpdir(), mediaType + generateMessageIDV2() + '-original')` — safe — and `imgFilename` from `join(tmpdir(), generateMessageIDV2() + '.jpg')` — safe). generateMessageIDV2 returns `'3EB0' + hex` — no metacharacters. Current risk is latent, not active. BUT the `extractVideoThumb`-style string-interpolation-then-exec pattern is the anti-pattern; the safer form is `spawn('ffmpeg', [...args])` which doesn't touch a shell at all.
```

*Classification: fact*

#### Evidence 4 — Runtime-dep CVE surface: 14 known CVEs across 6 direct dependencies: ws × 5 (core WebSocket library for this WhatsApp-Web client), protobufjs × 4, request × 2 (deprecated), acorn × 1 (in proto-extract), music-metadata × 1, @hapi/boom × 1 (on EOL 9.x line). No `.github/dependabot.yml` present; Dependabot Updates workflow shows active in GitHub Actions but no explicit ecosystem tracking config.

```bash
cat proto-extract/package.json package.json; for p in ws protobufjs request acorn music-metadata @hapi/boom; do curl -s https://api.osv.dev/v1/query -d "{\"package\":{\"name\":\"$p\",\"ecosystem\":\"npm\"}}"; done
```

Result:
```text
Per-package OSV counts at pinned versions: ws (^8.13.0) 5 vulns: GHSA-2mhh-w6q8-5hxw (DoS on arbitrary headers), GHSA-3h5v-q93c-6h6q, GHSA-5v72-xg48-5rpm, +2 more. protobufjs (^7.2.4): 4 vulns including GHSA-762f-c2wg-m8c8 (proto parser prototype pollution), GHSA-g954-5hwp-pp24, GHSA-h755-8qp9-cq85. request (^2.88.0 via proto-extract): 2 vulns — GHSA-p8p7-x288-28g6 (SSRF redirect to internal), GHSA-7xfp-9c55-5vqj (tls-insecure cert). acorn (^8.15.0 via proto-extract): GHSA-6chw-6frg-f759 (ReDoS). music-metadata (^11.7.0): GHSA-v6c2-xwv6-8xf7. @hapi/boom (^9.1.3): GHSA-2ggq-vfcp-gwhj (on EOL line). Relevance: `ws` is the core connection layer — 5 known CVEs on the primary WebSocket library of a WebSocket-based library is the one that most directly affects consumers.
```

*Classification: fact*

#### Evidence 6 — 150-day release stall. Latest stable: v6.7.21 (2025-11-06, 165 days before scan). Latest RC: v7.0.0-rc.9 (2025-11-21, 150 days before scan). Master last pushed 2026-04-19, one day before scan — active development on master, but no release tagging for 150 days. 42 total releases. v7.0.0 breaking changes are staged but not cut.

```bash
gh api 'repos/WhiskeySockets/Baileys/releases?per_page=10'
```

Result:
```text
total releases: 42. Recent (newest first): v7.0.0-rc.9 (2025-11-21), v7.0.0-rc.8 (2025-11-19), v7.0.0-rc.7 (2025-11-19), v6.7.21 (2025-11-06), v7.0.0-rc.6 (2025-10-19), v7.0.0-rc.5 (2025-10-02), v7.0.0-rc.4 (2025-09-26), v7.0.0-rc.3 (2025-09-14). Gap from v7.0.0-rc.9 to scan = 150 days. Main activity continues (last push 2026-04-19) — the v7.0.0 cut is staged but postponed. Consumers of the `baileys` npm package get v7.0.0-rc.9 as `@latest` (confirmed via npm registry query in harness).
```

*Classification: fact*

#### Evidence 7 — 0 published GHSA security advisories in 4 years of development. Consistent with catalog-wide silent-fix pattern (now 11/11 V1.2 scans). PR #1996 thread documents an explicit case where a security-motivated dep fix was NOT merged and NOT replaced — the 'silent fix' norm in this case appears to have been 'do not fix publicly' rather than 'fix without GHSA.'

```bash
gh api 'repos/WhiskeySockets/Baileys/security-advisories'; gh api 'repos/WhiskeySockets/Baileys/issues/1996/comments'
```

Result:
```text
security_advisories.count: 0 across 4-year history. PR #1996 comment thread: community contributor filed Vulnerability Fixes PR; maintainer purpshell committed to 'make our own version' on 2026-01-08; stale-bot closed it 2026-03-26; no replacement PR is visible in merged history (confirmed via harness dependency inventory showing `request`/`request-promise-*` still in proto-extract/package.json).
```

*Classification: fact*

#### Evidence 8 — PR-review coverage observation: harness sampled 0 PRs despite 352 lifetime merges. Direct API query shows Baileys' closed-PR stream is dominated by closed-WITHOUT-merge (external community PRs being dropped rather than merged/reviewed) — the harness sampling fell on the wrong side of this.

```bash
gh api 'repos/WhiskeySockets/Baileys/pulls?state=closed&per_page=50' --jq '[.[] | {merged: (.merged_at != null)}] | group_by(.merged) | map({merged: .[0].merged, count: length})'
```

Result:
```inference — harness-coverage-gap + methodology observation
50-most-recent closed PRs: ~6 merged (12%), ~44 closed-without-merge (88%). Pattern: most external community PRs are closed by maintainer or by stale-bot rather than merged. Most merged PRs are either (a) `github-actions[bot]` chore updates (WhatsApp Web version bumps), (b) core maintainer self-merges (purpshell, jlucaso1), or (c) a handful of external-contributor merges that received direct maintainer acceptance. Formal-review rate on the 6-merged sample: 0 APPROVED decisions visible (review_decision: null). This is consistent with a high-control maintainer workflow where formal review is bypassed in favor of merge-when-maintainer-agrees.
```

*Classification: inference — harness-coverage-gap + methodology observation*

#### Evidence 9 — Copilot code review workflow is active (dynamic/copilot-pull-request-reviewer), providing AI-assisted review commentary on PRs. 12 total workflows — Build, E2E Tests, Lint, Manual Release, PR Comment, Publish Release, Stale, Test, Update WAProto, Update WhatsApp Version, Copilot review, pages-build-deployment. 1 workflow uses pull_request_target (pr-comment.yml — comments on PRs). 0 SHA-pinned actions across 9 workflow files, 25 tag-pinned.

```bash
gh api repos/WhiskeySockets/Baileys/actions/workflows --jq '.workflows[] | {name, state}'; gh api repos/WhiskeySockets/Baileys/contents/.github/workflows/pr-comment.yml | jq -r .content | base64 -d
```

Result:
```text
12 workflows total. pr-comment.yml: 53 lines, `pull_request_target` trigger, no permissions block, 2 tag-pinned actions. The pull_request_target+no-permissions-block combo is the known-risky pattern (same class as WLED entry 25 F2 + kamal entry 18 structural pattern). Copilot code review workflow is dynamic/managed (GitHub's Copilot-PR-review AI) — different from QuickLook's Copilot SWE agent (which writes PRs).
```

*Classification: fact*

#### Evidence 10 — README install pathway: two npm packages published. (1) `baileys` (primary): `npm install baileys` → pulls v7.0.0-rc.9. (2) `whatsapp-web-protobuf-extractor` (internal build tool): `npm install whatsapp-web-protobuf-extractor` → v1.0.0. Both verified on npm registry (harness artifact_verification). Primary install path is clean npm-standard. README ALSO documents legacy `yarn add github:WhiskeySockets/Baileys` form which installs directly from master branch (no version pinning) — the harness install_script_analysis flagged this.

```bash
gh api repos/WhiskeySockets/Baileys/readme | jq -r .content | base64 -d; npm view baileys; npm view whatsapp-web-protobuf-extractor
```

Result:
```inference — install-path gap annotation
npm view baileys: name=baileys, version=7.0.0-rc.9, license=MIT, maintainer=purpshell, publishConfig.registry=https://registry.npmjs.org/. Downloads visible via the `baileys` npm listing. The legacy `yarn add github:WhiskeySockets/Baileys` snippet in the harness install_script_analysis is from archived or documentation content (not the current root README, which redirects to baileys.wiki). If a consumer follows the legacy instructions, they install HEAD of master — no version pinning, supply-chain exposure.
```

*Classification: inference — install-path gap annotation*

#### Evidence 11 — Scanner harness produced a false-positive on vendor_keys: `AIzaSyDR5yfaG7OG8sMTUj8kfQEb8T9pN8BM6Lk` at src/WABinary/constants.ts:601 matches the Google API key regex but is actually an entry in WhatsApp Web's protocol-compression dictionary (a list of pre-shared strings that the binary protocol references by index). Not an exposed secret.

```bash
gh api repos/WhiskeySockets/Baileys/contents/src/WABinary/constants.ts | jq -r .content | base64 -d | sed -n '595,615p'
```

Result:
```inference — scanner-coverage-gap annotation
Line context shows the string in a JavaScript array of short tokens: '690', '045', 'enc_iv', '75', 'failure', 'ptt_oot_playback', 'AIzaSyDR5yfaG7OG8sMTUj8kfQEb8T9pN8BM6Lk', 'w', '048', '2201', etc. This is the WhatsApp Web binary protocol's SINGLE_BYTE_TOKENS or DOUBLE_BYTE_TOKENS dictionary — a pre-shared list used for binary-format compression. The string format matches Google API key regex by coincidence (it's an arbitrary WhatsApp-chosen dictionary entry, possibly an obfuscated reference). Scanner-side mitigation: the vendor_keys regex should require the string to be in a context that suggests actual key usage (assignment to a variable named `apiKey`, `API_KEY`, `GOOGLE_API_KEY`; `process.env` reference; or URL embedding) rather than string-in-array-context.
```

*Classification: inference — scanner-coverage-gap annotation*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `8e5093c198de5c5c0230a76e8a7224f6006ebb2e` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
