# Security Investigation: wled/WLED

**Investigated:** 2026-04-20 | **Applies to:** main @ `01328a65c17c5a74aa53938f36efac27168267a1` | **Repo age:** 9 years | **Stars:** 17,837 | **License:** EUPL-1.2

> WLED — 17.8k-star ESP32 LED firmware, wled-org-owned, 100 contributors. Critical via F0: unresolved private GHSA-2xwq-cxqw-wfv8, 74 days silent after researcher's public complaint on issue #5340; 0.15.x backport unverified. F1 Warning: default-install has no auth, CORS wildcard, unauthenticated /reset — any same-LAN page can control the device. Positives: 38%/86% review rate, CodeQL + Copilot active.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-WLED.md` (+ `.html` companion) |
| Repo | [github.com/wled/WLED](https://github.com/wled/WLED) |
| Short description | ESP32/ESP8266 firmware for WS2812B and other WiFi-controlled digital LED strips. On-device webserver + JSON API + MQTT + Art-Net + E1.31 + UDP realtime. 9-year project with 100 contributors. |
| Category | `embedded-iot-firmware` |
| Subcategory | `esp32-led-controller` |
| Language | C++ |
| License | EUPL-1.2 |
| Target user | Hobbyist / maker / IoT integrator who wants WiFi-controllable LED lighting. Install: flash a .bin firmware to an ESP32/ESP8266 via install.wled.me (WebSerial browser flasher) or via `esptool.py` + downloaded .bin from GitHub Releases. Configure via captive-portal AP on first boot, then via web UI on LAN. |
| Verdict | **Critical** |
| Scanned revision | `main @ 01328a6` (release tag ``) |
| Commit pinned | `01328a65c17c5a74aa53938f36efac27168267a1` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of WLED. Tenth wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21, QuickLook 22, kanata 23, freerouting 24). |

---

## Verdict: Critical

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>✗ Critical — F0 is the blocking item (1 findings)</strong>
<br><em>Unresolved private GHSA-2xwq-cxqw-wfv8; 74-day maintainer silence after public complaint; backport status unknown.</em></summary>

1. **F0** — Issue #5340 remains open 74 days after last maintainer comment. Researcher escalated publicly because private channel didn't get ack in 10+ days. netmindz acknowledged 'critical' was fixed before but 0.15.x backport unverified publicly.

</details>

<details>
<summary><strong>⚠ Warning — F1–F4 describe default-posture and governance (4 findings)</strong>
<br><em>Default-no-auth webserver + CORS wildcard + /reset unauthenticated, anti-destruction-only ruleset, missing SECURITY.md, nightly-release@main mutable supply-chain ref.</em></summary>

1. **F1** — Factory-default WLED: empty PIN → correctPIN=true (wled_server.cpp:848); CORS wildcard on all endpoints (line 342); /reset unauthenticated (line 396). Any same-LAN webpage can control the device.
2. **F2** — nightly.yml uses `andelf/nightly-release@main` (mutable branch ref). Triggers WLED-WebInstaller via PAT_PUBLIC. PR #5386 proposes fix, unmerged 60 days. 0 SHA-pinned actions across 8 workflows.
3. **F3** — Ruleset has `deletion` + `non_fast_forward` only — no review-requirement rule. No CODEOWNERS. Despite strong social review (38% formal / 86% any), no structural enforcement.
4. **F4** — No SECURITY.md in 9 years. Private-advisory permissions misconfigured per issue #5340 thread (softhack007 got 404 on own project's advisory). 0 published advisories.

</details>

<details>
<summary><strong>ℹ Info — F5 + F6 (2 findings)</strong>
<br><em>Build-time Python CVE surface (not runtime); scanner coverage gaps.</em></summary>

1. **F5** — Python build deps: urllib3 (28 vulns), requests (13), starlette (7), bottle (8), certifi (6), uvicorn (4) = 73 CVE records. Build-time only; firmware ships pure C++. No .github/dependabot.yml.
2. **F6** — Scanner gaps: deserialization regex FP on ArduinoJson (19 hits); ghostly npm-wled channel; q2 security-keyword FP on PR #4942.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — anti-destruction-only ruleset (no review rule) + no CODEOWNERS, despite strong 38% formal / 86% any-review culture |
| Is it safe out of the box? | ❌ **No** — default-install has no authentication; CORS wildcard on all origins/methods/headers; unauthenticated /reset (F1) |
| Do they fix problems quickly? | ❌ **No** — unresolved GHSA-2xwq-cxqw-wfv8 with 74-day maintainer silence after public complaint (issue #5340); backport status unknown |
| Do they tell you about problems? | ⚠ **Partly** — CONTRIBUTING + CoC present (health 75%); no SECURITY.md; private-advisory permissions misconfigured per #5340 thread; 0 advisories in 9 years |

---

## 01 · What should I do?

> 17.8k⭐ · EUPL-1.2 · C++ · 1 critical · 4 warnings · 2 info · CRITICAL
>
> WLED is a 9-year-old ESP32/ESP8266 firmware for controlling addressable LED strips over WiFi — 17.8k stars, 100 contributors, wled-org-owned since Jan 2025. Critical verdict driven by F0: an unresolved private GHSA-2xwq-cxqw-wfv8 where researcher breakingsystems publicly complained on 2026-02-02 about maintainer non-response after 10+ days; last maintainer comment 2026-02-06 (74 days before scan) said the 'critical had been fixed' but 0.15.x backport status is publicly unconfirmed. On top of that, the factory-default firmware has no authentication, a CORS wildcard on all endpoints, and an unauthenticated /reset — making a default-install WLED on a LAN controllable by any same-network webpage (F1). Governance: an anti-destruction-only ruleset (no review requirement), missing SECURITY.md despite 9 years of history, and a mutable `andelf/nightly-release@main` supply-chain reference. Positive signals exist: unusually strong review culture (38% formal / 86% any, second-highest in the V1.2 catalog), CodeQL + Copilot AI-governance workflows active, Dependabot running, 100-contributor community.

### Step 1: Do NOT expose WLED devices to the internet or to untrusted networks (🚨)

**Non-technical:** Default WLED has no authentication. Never port-forward WLED to the internet. Never attach WLED to a network you don't control. If you want remote access, use a VPN into your home network, not direct exposure.

```text
# Check your router config — no port-forward rules for port 80 to your WLED device's IP
```

### Step 2: Set a PIN on first boot (Settings > Security & Update > PIN) (🚨)

**Non-technical:** After flashing WLED and connecting it to WiFi, open the web UI, go to Settings > Security & Update, set a PIN. This locks the settings/OTA endpoints against casual LAN-peer access. Empty PIN = no authentication (the factory default).

```text
# Via web UI: http://wled.local/settings → Security & Update → enter PIN → Save
```

### Step 3: Enable `otaSameSubnet` + use a dedicated IoT VLAN (⚠)

**Non-technical:** Even with a PIN, treat WLED as an untrusted device on your network. Put it on a separate VLAN (most consumer routers call this a 'Guest' or 'IoT' network). Enable otaSameSubnet so OTA uploads only accept from the same subnet.

```text
# Router-specific — consult your router's VLAN or guest-network setup docs
```

### Step 4: Install the STABLE channel, not nightly — pin to v0.15.4 for now (⚠)

**Non-technical:** install.wled.me has a channel selector — choose 'Stable' (currently v0.15.4), not 'Nightly'. The stable channel doesn't ride the @main-pinned nightly-release supply chain (F2). Watch for v0.15.5 or later before assuming GHSA-2xwq-cxqw-wfv8 (F0) is resolved.

```text
# Visit https://install.wled.me and select the Stable channel
```

### Step 5: Check release notes for GHSA-2xwq-cxqw-wfv8 resolution before assuming fixed (🚨)

**Non-technical:** Follow WLED release notes (github.com/wled/WLED/releases) and watch issue #5340 for resolution status. If you're on v0.15.x, the researcher noted the 'critical' was previously fixed but backport status is publicly unconfirmed. Err on the side of assuming not-yet-fixed until WLED publishes confirmation.

```bash
gh api repos/wled/WLED/issues/5340 --jq '.state'
```

### Step 6: If building from source: use an isolated build VM + pin Python deps (ℹ)

**Non-technical:** If you don't use pre-built .bin from install.wled.me or GitHub Releases and instead run `pip install platformio && platformio run`, the Python build environment pulls 29 packages with 73 known CVEs (F5). Use a disposable VM or Docker container for the build, not your daily workstation. Binary-install users can ignore this.

```bash
docker run --rm -v $(pwd):/w -w /w python:3.11-slim bash -c 'pip install -r requirements.txt && platformio run'
```

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 4 Warning · ℹ 2 Info
>
> 7 findings total.
### F0 — Critical · Vulnerability — Unresolved private GHSA-2xwq-cxqw-wfv8 — researcher publicly reports maintainer non-response; 74 days silent since last comment; backport to 0.15.x publicly unconfirmed

*Ongoing · Since 2026-02-02 (public issue opened); 74 days silent since 2026-02-06 · → Pin to a specific WLED version only after reviewing the GHSA-2xwq-cxqw-wfv8 resolution in WLED's public changelog; do not expose an unupdated WLED device to untrusted networks.*

The timeline, reconstructed from public issue #5340 comments: researcher breakingsystems filed a private GitHub Security Advisory (GHSA-2xwq-cxqw-wfv8) on wled/WLED circa 2026-01-23 via the standard 'Report a vulnerability' UI. After 10+ days with no maintainer acknowledgement on the private thread, they opened public issue #5340 on 2026-02-02 — explicitly calling out the unresponsiveness and asking a maintainer to 'please have a look … and leave a comment there.'

Maintainer softhack007 (the #3 contributor at 9.5% of commits) replied within two hours. But his response was revealing: 'I get a 404 page not found on your URL.' breakingsystems confirmed the expected collaborator scoping should grant softhack007 access, pointing to a permissions gap inside wled-org's advisory-team configuration. softhack007 then pinged netmindz (the project's self-described release manager). netmindz replied 2026-02-04: 'I have given an initial response, more details to follow. TLDR: the critical has already been reported once before and had been fixed. I just need to double check that it did get back ported to 0.15.x. Other issues reported are very fairly basic rather than significant discoveries.'

That was the last substantive maintainer comment. Scan date is 2026-04-20, putting the silence at 74 days. Issue #5340 remains open. v0.15.4 shipped 2026-03-14 (36 days before scan, 37 days after netmindz's 'fixing backport' comment) — but no public release notes mention GHSA-2xwq-cxqw-wfv8. A user running v0.15.4 cannot tell, from public information, whether they're running the fixed version.

The severity framing matters here. The vulnerability itself is private — this finding doesn't reconstruct the specific attack class. What the finding DOES document is a disclosure-handling failure on a 'critical'-tier vulnerability by the maintainers' own characterization, on a project with 17.8k stars and widespread IoT deployment. Combined with the catalog-wide silent-fix pattern (10 of 10 V1.2 scans with 0 published GHSA), the practical consumer consequence is: you can't rely on GHSA syndication to know when to update. You have to watch the issue tracker and release notes, and even then, WLED release notes rarely call out security fixes explicitly.

Related context: the same researcher filed issue #3233 in 2023 ('WiFi Scanning vulnerable to XSS') with a clear PoC demonstrating stored-XSS via SSID name. That issue was closed within 5 days without publishing a GHSA. netmindz's reference to 'the critical has been reported before' is consistent with GHSA-2xwq-cxqw-wfv8 being a new instance of the same XSS class or a related one — but again, publicly unconfirmed.

**How to fix.** Maintainer-side: close issue #5340 with a public summary of which WLED versions fix GHSA-2xwq-cxqw-wfv8 and which other issues were resolved. Publish GHSA-2xwq-cxqw-wfv8 once resolution is confirmed — syndicates to the GHSA feed and lets users running older versions know they need to update. Consumer-side: watch for v0.15.5 or later release notes before assuming the current 0.15.x install is up-to-date.

### F1 — Warning · Vulnerability — Default-install WLED has NO authentication — CORS wildcard on all endpoints + unauthenticated `/reset` + optional-PIN OTA make any same-LAN webpage a control surface

*Continuous · Since WLED's webserver-with-optional-auth design was established · → Set a PIN in the Security & Update page immediately after first boot. Do NOT expose WLED devices to untrusted networks or to the internet. Consider isolating WLED on a separate IoT VLAN.*

The specific source lines in wled00/wled_server.cpp tell the story. Line 342 initializes CORS: `DefaultHeaders::Instance().addHeader(F("Access-Control-Allow-Origin"), "*");` followed immediately by Access-Control-Allow-Methods: * and Access-Control-Allow-Headers: * on lines 343-344. There is no user-configurable option for tighter CORS. Any origin may issue cross-origin requests and read responses.

Line 848 establishes the authentication model: `correctPIN = !strlen(settingsPIN);`. This is the first thing initServer does on the PIN state — if the PIN is empty (the factory default), correctPIN is immediately set to true, marking the device as already-authenticated. A user who doesn't know to set a PIN effectively opts out of all subsequent auth checks for the session.

The /reset endpoint at line 396-399 bypasses even the PIN system: `server.on(F("/reset"), HTTP_GET, [](AsyncWebServerRequest *request){ serveMessage(request, 200, ...); doReboot = true; });`. No auth. Any GET /reset reboots the device. This is a denial-of-service primitive — a malicious webpage on the same LAN can reboot the WLED device indefinitely.

The OTA flash endpoint (`/update`, lines 507-548) does check auth. The logic is: `if (((otaSameSubnet && !inSameSubnet(client)) && !strlen(settingsPIN)) || (!otaSameSubnet && !inLocalSubnet(client))) { reject }` followed by `if (!correctPIN) { reject }`. Both otaSameSubnet and the PIN are OPTIONAL user settings. Default install: otaSameSubnet is off; PIN is empty → `inLocalSubnet(client)` (client IP must match 10/8, 192.168/16, or 172.16/12) is the only gate. Any LAN peer who can reach WLED can upload firmware.

The design rationale is clear enough from WLED's documentation: the project assumes the LAN is a trusted zone. That's a defensible stance for a hobbyist LED controller. The finding documents what happens in the cases where that assumption fails: ISP-provided routers with no client isolation, guest networks bridged to main, IoT VLANs misconfigured, a family member's phone running a compromised app. In those cases, a default-config WLED is a control-plane of the home network.

A specific mitigation is already present in the codebase but must be user-activated: setting a PIN closes the unauthenticated-settings surface, enabling otaSameSubnet closes the remote-OTA surface, and putting WLED on a separate VLAN closes the LAN-peer surface entirely. The finding's severity reflects that most users don't do any of these. Firmware maintainers could change that by making PIN setup mandatory in the first-boot captive portal — a ~20-line change to the AP-mode setup flow.

**How to fix.** Maintainer-side: make PIN setting part of the first-boot AP-mode configuration flow (currently optional); add a warning banner to the web UI when no PIN is set; tighten CORS defaults (restrict to same-origin by default with user-opt-in for web-app-integration use cases); add basic auth check on `/reset`. Consumer-side: set a PIN in Settings > Security & Update on first boot; enable `otaSameSubnet`; ideally isolate WLED on an IoT VLAN with no routing to main LAN devices.

### F2 — Warning · Structural — Nightly deployment uses `andelf/nightly-release@main` (mutable ref); 0 SHA-pinned actions across 8 workflows; PR #5386 proposes fix but unmerged 60 days

*Continuous · Since the nightly workflow adopted andelf/nightly-release; PR #5386 unmerged since 2026-02-20 · → If building firmware from WLED source or consuming nightly builds from install.wled.me/nightly, note the upstream supply-chain exposure. Production use should pin to a tagged stable release (v0.15.4) rather than nightly.*

The specific line in .github/workflows/nightly.yml: step 'Update Nightly Release' at line 25 reads `uses: andelf/nightly-release@main`. That @main ref is a pointer to the live main branch of an individual developer's GitHub action. Tag-pinning would constrain the ref to a specific released version; SHA-pinning would constrain to a specific commit. @main pins to whatever andelf pushes next.

The blast radius is specific. The nightly workflow builds .bin firmware variants (using the wled_build reusable workflow) and then, via andelf/nightly-release@main, creates a GitHub Release tagged 'nightly' with the .bin files as assets. A subsequent step (peter-evans/repository-dispatch@v3 — tag-pinned, safer) uses `secrets.PAT_PUBLIC` to dispatch a release-nightly event to wled/WLED-WebInstaller. That downstream repo publishes the new nightly to install.wled.me/nightly — the WebSerial flasher consumed by end users.

If andelf/nightly-release's main branch is altered — account takeover, developer social-engineered, or andelf themselves turning malicious — the next nightly WLED build consumes the modified action with GITHUB_TOKEN in scope. Malicious action code could embed payloads in the .bin before it's published, or redirect artifacts, or exfiltrate the PAT. The compromise window is 'from andelf's next push to the next nightly build' — which runs at 2 AM UTC daily per the cron schedule.

Open PR #5386 ('Pin andelf/nightly-release to version tag instead of @main branch') was filed on 2026-02-20. It proposes the one-line fix: `uses: andelf/nightly-release@v1.0.0` (or whatever stable tag exists). The PR has been open 60 days, unmerged. This is the kind of fix that's faster to merge than to document reasons not to merge.

Broader hygiene: across the 8 WLED workflow files, 0 actions are SHA-pinned and 25 are tag-pinned. Tag-pinning is the industry-common pattern but still vulnerable to tag-hijacking (action owner force-pushes a tag to point at malicious code). SHA-pinning is the stricter form that pins to an immutable commit. A consolidated hardening pass would swap all 25 tag-pins to SHAs; Dependabot has a setting to manage SHA-pinned action updates automatically.

**How to fix.** Maintainer-side: merge PR #5386 (pin to a tag); further harden by pinning all 25 tag-pinned actions to commit SHAs (the standard Dependabot-manageable pattern); add a permissions block to pr-merge.yaml. Consumer-side: for production deployments, use tagged releases (v0.15.4) not nightly; if using install.wled.me, prefer the 'Stable' channel over 'Nightly'.

### F3 — Warning · Governance — Ruleset has `deletion` + `non_fast_forward` only — no required-review rule; no CODEOWNERS; despite 38% formal review + 86% any-review culture

*Continuous · Since ruleset creation 2025-02-09 (anti-destruction from day 1) · → Pin to reviewed release tags; treat unreleased (nightly / main-tip) code as unreviewed-by-gate even though 86% of PRs receive SOME review.*

The ruleset was created 2025-02-09 — shortly after the ownership transfer from Aircoookie to the wled org on 2025-01-31. It has exactly 2 rules on the default branch: `deletion` (blocks branch deletion) and `non_fast_forward` (blocks force-push). Both are anti-destruction rules — they prevent an attacker from rewriting history after a malicious merge, but they do not prevent the merge itself.

No `pull_request` rule. No `required_approving_review_count`. No `required_status_checks`. No CODEOWNERS. No classic branch protection (HTTP 404 on that API). A compromised maintainer account with write access can push directly to main (history-preserving, so fast-forward-safe) and the commit lands. The anti-destruction rules would prevent covering tracks afterward but not the initial merge.

The unusual aspect of WLED's posture is the review culture coexisting with absent enforcement. 38% of the 50-PR closed-merged sample had formal APPROVED review decisions — second-highest in the V1.2 catalog after kanata's 44%. 86% had at least one review interaction (comments, requested changes, or approvals) — the HIGHEST any-review rate we've seen across V1.2 scans. Self-merges were 64%, but the 86% any-review rate implies these are typically post-review author-merges, not unreviewed ones.

The gap is structural: a well-meaning community of 100 contributors, 6-person top-contributor tier (blazoncek 46%, Aircoookie 24.6%, softhack007 9.5%, netmindz 8.7%, DedeHai 5.8%, willmmiles 5.3%), with strong review hygiene, but no ruleset forcing it. The fix is a 3-line ruleset addition — add a `pull_request` rule requiring ≥1 approving review. That would convert the structural review from 'social norm' to 'cannot merge without it.'

**How to fix.** Maintainer-side: extend the 'Main' ruleset to include a `pull_request` rule with `required_approving_review_count: 1` (or 2); add CODEOWNERS naming primary reviewers per subsystem (Aircoookie + netmindz for core; blazoncek for FX; softhack007 for audio). Consumer-side: pin to tagged release (v0.15.4), not main.

### F4 — Warning · Hygiene — No SECURITY.md in 9 years; private-advisory permissions misconfigured (per issue #5340 comment thread)

*Continuous · Since 2016-12-20 · → Researchers finding WLED vulns should use the GitHub 'Report a vulnerability' button AND simultaneously mention the report in the public discussions/Discord to route around the maintainer-side permissions gap documented in issue #5340.*

The documented permissions gap from issue #5340 is specific. softhack007's first comment on the public issue was 'I get a 404 page not found on your URL' — the URL being https://github.com/wled/WLED/security/advisories/GHSA-2xwq-cxqw-wfv8. breakingsystems responded with screenshot evidence that the advisory's collaborator list included '@wled wled owners' as a team with access. softhack007, as a member of wled-owners, should have seen the advisory. He didn't.

That points to a GitHub permissions misconfiguration inside wled-org — either the wled-owners team's advisory-read scope didn't propagate, or the advisory's team-level collaborator field wasn't set up correctly. Either way, the effect is that the private disclosure channel has a documented failure mode. A researcher filing a private advisory cannot assume all maintainers see it; they have to publicly ping individual accounts to route around the gap.

Beyond that specific incident, the disclosure-policy absence is catalog-wide: no SECURITY.md at root, .github/, or docs/ despite 9 years of project history. Community health is 75% (CONTRIBUTING and CODE_OF_CONDUCT present — above the V1.2 catalog median) but the security-disclosure piece specifically is missing. 0 GHSA advisories have been published over 9 years. The earlier 2023 XSS disclosure (issue #3233) was closed within 5 days but not syndicated as an advisory.

The practical fix is cheap: a 1-page SECURITY.md naming GitHub's 'Report a vulnerability' UI, Discord as backup, and an expected response SLA. Plus an audit of the wled-owners team advisory-permissions to make sure the private channel actually works. Both are hours of work, not days.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md naming GitHub's 'Report a vulnerability' UI + Discord as backup + expected response SLA. Audit the wled-owners team scope against the private advisory UI (fix the permissions issue that surfaced in #5340 comment thread). Publish GHSA-2xwq-cxqw-wfv8 once resolved to close the feedback loop.

### F5 — Info · Hygiene — Build-time Python deps (platformio + transitives) carry 73+ CVEs across 9 packages — attack surface for build-from-source users only; firmware itself ships pure C++

*Continuous · Since platformio toolchain adopted · → If you `git clone` WLED and build from source, pin your Python environment with `pip install -r requirements.txt --require-hashes` or use a reproducible build VM. Binary-install users (install.wled.me or downloaded .bin) are not directly affected.*

The Python requirements.txt pins 23 packages at specific versions. osv.dev lookups across those pins reveal the CVE surface: urllib3 (28 records), requests (13), starlette (7), bottle (8), certifi (6), uvicorn (4), marshmallow (3), idna (2), h11 (1). That's 72 Python records plus 1 npm record (clean-css). Most are historical — the pinned versions are reasonably current (urllib3==2.5.0, requests==2.33.0, starlette==0.45.3) and many OSV records apply to older versions. But the pinned-version-has-some-CVE-record shape is real.

The scope is crucial for severity framing. These are PLATFORMIO BUILD-TIME dependencies. The firmware itself is pure C++ compiled for ESP32 — there is no Python runtime, no Node runtime, no FastAPI server on the device. The Python environment exists only for the build pipeline: platformio reads platformio.ini, resolves board configurations, invokes the C++ toolchain, and produces the .bin files. starlette/uvicorn/bottle are part of platformio's own web UI for package management — WLED's build process doesn't actually use them, but pip pulls them anyway as platformio transitives.

The consumer impact breakdown: (a) install.wled.me user or downloaded-.bin user — zero exposure (you never run any Python); (b) `git clone && platformio run` user — the build environment is exposed; (c) build server integrator — the attack surface is the pip install step. For category (b) and (c), a malicious PyPI package hijack (typosquat, account takeover) during build could inject code into the pio-scripts/ layer and thus into the .bin metadata. The scenario requires a specific PyPI-side compromise window; it's not a today-risk but a lurking-risk.

The maintainer-side fix is to add .github/dependabot.yml explicitly tracking pip and npm (currently only the github-actions ecosystem gets the default Dependabot coverage). That would route the 73 OSV records into automated PR updates and close most of them by version bumps. The consumer-side fix for build-from-source users is `pip install -r requirements.txt --require-hashes` in a disposable VM.

**How to fix.** Maintainer-side: add a `.github/dependabot.yml` explicitly tracking pip + npm (and github-actions while we're at it); consider bumping requirements.txt to current versions of urllib3 / requests (latest patches close most of the OSV records). Consumer-side (build-from-source only): use a disposable build VM; pin with `--require-hashes`; don't copy the build environment into production.

### F6 — Info · Coverage — Scanner coverage gaps: false-positive deserialization regex (ArduinoJson), ghost npm-wled channel, q2 security-keyword FP on PR #4942

*Continuous · Scanner tooling gap · → Calibration note — three scanner gaps documented for V1.2.x backlog.*

Three specific scanner coverage gaps documented for this scan, in order of surprise:

(1) The V1.2.x-widened deserialization regex (`pickle\.loads?|yaml\.load\s*\(|ObjectInputStream|deserialize|Marshal\.load|\bmarshal\.loads?|\bjoblib\.load|\bdill\.loads?`) matched 19 hits in WLED's C++ codebase. Every one is a call to ArduinoJson's `deserializeJson(*pDoc, STREAM)` — safe JSON parsing, not an RCE-class primitive. The regex has no language qualifier, so it collides with any C/C++/Rust/Go project using JSON libraries that happen to expose function names containing 'deserialize'. Contrasts sharply with freerouting (entry 24) where every deserialization hit was a real Java ObjectInputStream call. The calibration fix is a language-qualifier: restrict pickle-family patterns to Python files, Java-family to .java, and gate ArduinoJson-style deserializeJson via a known-safe-function allowlist.

(2) Distribution-channel detection surfaced exactly one channel: 'npm-wled' (verified present on npm registry at version 1.1.0). But WLED doesn't ship firmware via npm. The package.json `name: "wled"` is for build-tooling use (HTML minification pipeline). The real distribution channels are install.wled.me (a WebSerial browser flasher that downloads .bin and pushes to an ESP32 over USB), GitHub Releases (12 .bin variants per target board: ESP32-WROOM.bin, ESP32-WROVER.bin, ESP8266_debug.bin, ESP32-S3.bin, etc.), and the WLED iOS/Android apps for on-LAN discovery + control. The harness's channel-detection heuristic needs (a) an exclusion for package.json entries that aren't actually published as the primary artifact, (b) recognition of ESP firmware release-asset patterns (.bin/.bin.gz), and (c) a WebSerial-flasher-site detection pattern.

(3) The q2_oldest_open_security_item_age_days signal returned 214 days, driving Q2 red. The 214-day match is PR #4942 'Add internal user backup functionality to Security & Update page' — a feature PR that extends the settings page named 'Security & Update.' The security-keyword regex matches on the substring 'Security' in the title. The real security item is issue #5340 at 76 days. Phase 4's Q2 red is still correct (the 74-day silence on an unresolved GHSA is a genuine red condition), but for a different substantive reason than the signal driver. A filter that checks PR labels and body text alongside title would disambiguate feature-page PRs from actual vulnerability-handling PRs.

None of these gaps changed the verdict; Phase 4 authored around each and documented the calibration issues for V1.2.x backlog consideration.

**How to fix.** Scanner-side: (a) add language-qualifier to deserialization regex so C/C++ `deserializeJson` / `deserialize` matches don't escalate; (b) add ESP32/.bin release-asset detection for GitHub Releases; (c) add q2 PR-title false-positive filter (exclude titles with 'feature', 'add', 'improve', 'update' plus Security-substring — check body + labels for actual vulnerability topic).

---

## 02A · Executable file inventory

> WLED ships as ESP32/ESP8266 firmware. Primary on-device binary is ~1.5MB of compiled C++ (built via platformio). Distribution channel: .bin files per target board on GitHub Releases + install.wled.me WebSerial flasher. No native desktop binary.

### Layer 1 — one-line summary

- Firmware compilation pipeline: platformio reads platformio.ini, builds 12+ target-board variants (ESP32-WROOM, ESP32-WROVER, ESP8266_debug, ESP32-S3, ESP32-C3, ESP32-C6, etc.), each producing a .bin. Release workflow (release.yml) + nightly workflow (nightly.yml) invoke the build and publish artifacts to GitHub Releases + trigger WLED-WebInstaller publication.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `wled00/wled_server.cpp` | firmware-webserver | ESP32 (C++) | `DefaultHeaders::Instance().addHeader("Access-Control-Allow-Origin", "*")` (line 342); `/reset` handler with no auth (line 396-399); `correctPIN = !strlen(settingsPIN)` (line 848) — F1 core surface | HTTP server on port 80 (default); WebSocket handler; OTA endpoint | THIS is F1. The webserver initializes CORS wildcard, exposes /reset unauthenticated, and gates OTA behind optional-PIN + optional-same-subnet checks. |
| `.github/workflows/nightly.yml` | ci-workflow | GitHub Actions | `uses: andelf/nightly-release@main` (line 25, mutable ref) — F2 | Uses PAT_PUBLIC to dispatch to wled/WLED-WebInstaller | Ships firmware to install.wled.me/nightly. PR #5386 proposes pinning fix. |
| `.github/workflows/pr-merge.yaml` | ci-workflow | GitHub Actions | `pull_request_target` on closed events + `actions-cool/check-user-permission@v2` (tag-pinned, third-party); no permissions block | Discord webhook notification | Safer form of pull_request_target (closed/merged only, permission-gated) but tag-pinned third-party action + no permissions block weakens the gate. |
| `platformio.ini + pio-scripts/` | build-pipeline | Python (platformio) | 4 subprocess calls in pio-scripts/ for git metadata + module validation; tools/cdata-test.js uses child_process | None | Build-time Python environment — 73 CVEs across 9 pinned packages (F5). Firmware runtime is unaffected. |

Install paths: (1) `install.wled.me` — visit in Chrome/Edge, click Install, browser-side WebSerial pushes the .bin directly to a USB-connected ESP32. (2) Download .bin from GitHub Releases + `esptool.py --port /dev/ttyUSB0 write_flash 0x0 WLED.bin`. (3) For existing WLED devices: upload new .bin via Settings > Security & Update (requires PIN if set; same-subnet check if enabled).

---

## 03 · Suspicious code changes

> Representative rows from the 50-PR closed-merged sample plus 2 currently-open security-relevant PRs. Full sample: 38% formal APPROVED, 86% any-review (HIGHEST in V1.2 catalog), 64% self-merge (mostly post-review author-merges). 2 open PRs are specifically security-relevant: #5482 prevents /upload overwriting wsec.json (secrets file — implies current releases have this issue), #5386 pins nightly-release@main to a tag (F2 fix, unmerged 60 days).

Sample: the 50 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 41.0% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#5516](https://github.com/wled/WLED/pull/5516) | Add identifier string for DMX realtime mode | external-contrib | DedeHai | Approved by DedeHai | None |
| [#5515](https://github.com/wled/WLED/pull/5515) | better packet queuing & pacing for custom palette live preview | blazoncek | blazoncek | 2 any-reviews, self-merged | Self-merge by top contributor; review culture present but not enforced |
| [#5482](https://github.com/wled/WLED/pull/5482) | prevent /upload from overwriting wsec.json | external-contrib | [OPEN] | N/A — open | SECURITY-RELEVANT: currently-open PR implies /upload CAN overwrite wsec.json (secrets file) in current releases |
| [#5386](https://github.com/wled/WLED/pull/5386) | Pin andelf/nightly-release to version tag instead of @main branch | external-contrib | [OPEN] | N/A — open 60 days | SECURITY-RELEVANT: fixes F2 supply-chain; unmerged |
| [#5497](https://github.com/wled/WLED/pull/5497) | 0.16 - Backport dynarray fixes from V5 WIP | willmmiles | willmmiles | APPROVED + self-merged | None |
| [#5493](https://github.com/wled/WLED/pull/5493) | Refactor wled-tools discover_devices for deduplication and clarity | external-contrib | netmindz | Approved by netmindz | None |

---

## 04 · Timeline

> ✓ 1 good · 🟡 8 neutral · 🔴 2 concerning
>
> WLED lifecycle — 9-year Aircoookie-originated project; ownership transferred to wled org Jan 2025; two disclosure events from breakingsystems (2023 XSS #3233 closed silently; 2026 GHSA-2xwq-cxqw-wfv8 unresolved).

- 🟡 **2016-12-20 · Repo created (Aircoookie)** — Original Aircoookie/WLED
- 🔴 **2023-06-06 · Issue #3233 (XSS) filed** — Closed in 5 days — no GHSA
- 🟢 **2025-01-31 · wled org created** — Ownership transfer from Aircoookie
- 🟡 **2025-02-09 · Ruleset 'Main' created** — Anti-destruction only
- 🟡 **2026-01-23 · Private GHSA-2xwq filed** — Inferred from public issue
- 🔴 **2026-02-02 · Public issue #5340 opens** — After ~10 days silence
- 🟡 **2026-02-04 · netmindz partial response** — Last substantive comment
- 🟡 **2026-02-20 · PR #5386 opens (F2 fix)** — Unmerged 60 days
- 🟡 **2026-03-14 · v0.15.4 released** — No GHSA acknowledgement
- 🟡 **2026-04-11 · v16.0.0-beta released** — Next major track
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan entry 25

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 17,837 | Largest in V1.2 catalog |
| Open issues | 350 | 1 security-tagged (#5340) — F0 |
| Open PRs | 113 | 5 security-keyword-matching; 1 real security PR (#5482) |
| Primary language | C++ | ESP32 firmware |
| License | EUPL-1.2 | European Union Public Licence |
| Created | 2016-12-20 | ~9 years |
| Last pushed | 2026-04-20 | Day of scan |
| Default branch | main |  |
| Repo size | ~70 MB |  |
| Total contributors | 100 |  |
| Top contributor | blazoncek 46.0% | Not solo; dispersed |
| Org owner | wled (org) | Transferred from Aircoookie 2025-01-31 |
| Solo-maintainer flag | FALSE | 46.0% < 80% threshold |
| Formal releases | 68 | Stable v0.15.4 + v16.0.0-beta + nightly |
| Latest stable release | v0.15.4 (2026-03-14) | 36 days before scan |
| Latest prerelease | v16.0.0-beta (2026-04-11) | 9 days before scan |
| Classic branch protection | OFF (HTTP 404) |  |
| Rulesets | 1 | Anti-destruction only — F3 |
| Rules on default branch | 2 | deletion + non_fast_forward |
| CODEOWNERS | Absent |  |
| SECURITY.md | Absent | 9 years; F4 |
| CONTRIBUTING | Present |  |
| CODE_OF_CONDUCT | Present |  |
| Community health | 75% |  |
| Workflows | 12 | Includes CodeQL + Copilot SWE agent + Copilot review + Dependabot |
| pull_request_target usage | 1 | pr-merge.yaml (on closed events) — F2 |
| SHA-pinned actions | 0 | All 8 workflows tag-pinned only |
| Tag-pinned actions | 25 |  |
| Dependabot config (.yml) | Absent | But Dependabot workflow active (default behavior) |
| PR formal review rate (50 sample) | 38% | Second-highest in V1.2 catalog (after kanata 44%) |
| PR any-review rate (50 sample) | 86% | HIGHEST in V1.2 catalog |
| Self-merge count (50 sample) | 32 (64%) | Mostly post-review author-merges |
| Published security advisories | 0 | 9 years; 10/10 V1.2 silent-fix pattern |
| Open security issues | 1 | #5340 — 76 days old (F0) |
| Open private GHSA | GHSA-2xwq-cxqw-wfv8 (referenced in #5340) | Status unknown — F0 |
| Python build-time deps | 29 | 73 OSV vulns across 9 packages — F5 |
| OSSF Scorecard | Not indexed |  |
| Primary distribution | install.wled.me (WebSerial) + GitHub Releases .bin + WLED iOS/Android apps | Harness detected ghostly 'npm-wled' — F6 |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 8 documented gaps — concentrated on (a) deserialization regex false-positives in C/C++ with JSON libraries, (b) embedded-firmware distribution channels (install.wled.me WebSerial + GitHub Releases .bin), and (c) q2 PR-title security-keyword FPs on feature-page PRs.

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit (4994/5000 remaining) |
| Tarball extraction + local grep | ✅ Scanned (580 files) |
| OSSF Scorecard | ⚠ Not indexed |
| Dependabot alerts | ⚠ Admin scope (403); no .github/dependabot.yml; Dependabot workflow shows active (default behavior) |
| osv.dev dependency queries | ✅ 29 Python/npm queries — 73 vulns surfaced across 9 packages (F5) |
| PR review sample | ✅ 50-PR sample — 38% formal, 86% any, 64% self-merge |
| Dependencies manifest detection | ✅ 4 manifests (requirements.txt x2, package.json, package-lock.json) — ALL build-time |
| Distribution channels inventory | ⚠ 1 ghostly channel (npm-wled); real channels (install.wled.me + GitHub Releases .bin + WLED apps) unrecognized — F6 |
| Dangerous-primitives grep (15 families) | ⚠ 19 deserialization hits (ALL false-positive — ArduinoJson's safe deserializeJson); 7 tls_cors hits (real: Access-Control-Allow-Origin: * — F1); 7 xss (innerHTML in minified UI); 4 exec (build-tooling); 2 weak_crypto (sha1 in util.cpp) |
| Workflows | ✅ 12 detected (8 with content); pull_request_target in pr-merge.yaml (on closed) — F2 |
| CodeQL SAST | ✅ Active workflow |
| AI-governance tooling | ✅ Copilot SWE agent + Copilot PR review workflows active (same pattern as QuickLook entry 22) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No suspicious paste-from-command blocks |
| Prompt-injection scan on agent files | ✅ 0 signals on AGENTS.md + .github/copilot-instructions.md |
| Tarball extraction | ✅ 580 files |
| osv.dev | ℹ  |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4994/5000 remaining |

**Gaps noted:**

1. Dangerous-primitives deserialization regex produces false-positives on C/C++ codebases using JSON libraries — 19 ArduinoJson `deserializeJson` matches here are SAFE JSON parsing, not pickle/ObjectInputStream RCE class. Regex needs language qualifier.
2. Distribution-channel detection surfaced ghostly 'npm-wled' (build-tooling package name) — real channels are install.wled.me (WebSerial browser flasher) + GitHub Releases .bin (12 target boards per release) + iOS/Android apps for discovery.
3. q2_oldest_open_security_item_age_days FP: PR #4942 title contains 'Security & Update page' (feature PR) → 214-day signal driving Q2 red. Real security item is issue #5340 at 76 days. Cell color still correct but for a different reason.
4. OSSF Scorecard not indexed — governance signals derived from raw gh api data.
5. Dependabot alerts API required admin scope; no .github/dependabot.yml present to inspect ecosystems tracked.
6. Gitleaks secret-scanning not available on this scanner host.
7. Q4 signal `q4_has_critical_on_default_path` doesn't auto-fire from tls_cors + default-no-auth combo — Phase 4 authored the override (scorecard cell rationale documents the signal_vocabulary_gap).
8. Prior XSS disclosure (#3233 from 2023) was closed without publishing a GHSA — confirms silent-fix pattern. Scanner has no way to count 'issues with security keywords that were closed without GHSA' across the issue archive as a signal.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from Phase 1 harness + gh api + direct file fetches of wled_server.cpp, nightly.yml, pr-merge.yaml, and issue #5340 comment thread.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — Unresolved private GHSA-2xwq-cxqw-wfv8 — researcher breakingsystems reported multiple vulnerabilities via GitHub's private advisory UI circa 2026-01-23; received no maintainer acknowledgement for ~10 days; opened public issue #5340 on 2026-02-02.

```bash
gh api repos/wled/WLED/issues/5340
```

Result:
```text
Issue #5340 body: 'I reported a number of vulnerabilities privately via the Github Report a vulnerability feature. It has been over one week now without a response/acknowledgement. Could one of the WLED maintainers please have a look at GHSA-2xwq-cxqw-wfv8 and leave a comment there?' Comments: softhack007 (maintainer #3, 9.5% commits) replied same day saying he gets 404 on the advisory URL — permissions issue with wled-owners group. breakingsystems confirmed softhack007 should have access. softhack007 then tagged netmindz (release manager). netmindz replied 2026-02-04: 'I have given an initial response, more details to follow. TLDR: the critical has already been reported once before and had been fixed. I just need to double check that it did get back ported to 0.15.x. Other issues reported are very fairly basic rather than significant discoveries.' Last update: 2026-02-06. Scan date: 2026-04-20. 74 days silent. Issue STILL OPEN. Status of 0.15.x backport PUBLICLY UNCONFIRMED.
```

*Classification: fact*

#### ★ Evidence 2 — Default-install WLED webserver exposes all endpoints without authentication when PIN is unset. `correctPIN = !strlen(settingsPIN)` at wled00/wled_server.cpp:848 — empty PIN marks the device unlocked. CORS wildcard on all origins/methods/headers makes cross-origin requests from any webpage possible.

```bash
gh api repos/wled/WLED/contents/wled00/wled_server.cpp | jq -r .content | base64 -d | grep -nE '(correctPIN|Access-Control-Allow)'
```

Result:
```text
wled_server.cpp:342: `DefaultHeaders::Instance().addHeader(F("Access-Control-Allow-Origin"), "*");` followed by `Methods: *` and `Headers: *` (lines 343-344). wled_server.cpp:848: `correctPIN = !strlen(settingsPIN);` — when PIN is empty (DEFAULT OUT-OF-BOX STATE), correctPIN=true and subpage gates pass. wled_server.cpp:396-399: `server.on(F("/reset"), HTTP_GET, [](AsyncWebServerRequest *request){ serveMessage(...); doReboot = true; });` — ZERO authentication check on reboot endpoint. For OTA (`/update`, lines 507-548), the auth chain checks `otaSameSubnet` + `correctPIN` + `otaLock` — all three are OPTIONAL user-settings; defaults leave OTA open within the LAN.
```

*Classification: fact*

#### ★ Evidence 3 — Nightly deployment workflow uses `andelf/nightly-release@main` — a mutable branch reference to a third-party action. Open PR #5386 proposes pinning to a version tag; unmerged after 60 days. The workflow carries PAT_PUBLIC to trigger wled/WLED-WebInstaller release events.

```bash
gh api repos/wled/WLED/contents/.github/workflows/nightly.yml | jq -r .content | base64 -d
```

Result:
```text
nightly.yml line 25: `uses: andelf/nightly-release@main` — references the `main` branch (mutable) rather than a tagged version. The step carries GITHUB_TOKEN. Line 35: separate step uses `peter-evans/repository-dispatch@v3` (tag-pinned) with `secrets.PAT_PUBLIC` to dispatch release-nightly events to wled/WLED-WebInstaller (which publishes to install.wled.me/nightly). PR #5386 'Pin andelf/nightly-release to version tag instead of @main branch' opened 2026-02-20, unmerged 60 days later. Across all 8 workflows: 0 SHA-pinned actions, 25 tag-pinned actions.
```

*Classification: fact*

### Other evidence

#### Evidence 4 — Branch-protection posture — 1 ruleset with 2 rules (`deletion` + `non_fast_forward`) on default branch. No CODEOWNERS. No classic branch protection. Anti-destruction only; no review-requirement.

```bash
gh api repos/wled/WLED/rulesets; gh api repos/wled/WLED/rules/branches/main
```

Result:
```text
classic: HTTP 404. rulesets.count: 1 (ruleset 'Main', id 3622502, created 2025-02-09 — right after org transfer from Aircoookie to wled-org). rules_on_default.count: 2, types: ['deletion', 'non_fast_forward']. No `pull_request` rule. No `required_approving_review_count`. CODEOWNERS: absent (checked root, .github/, docs/, .gitlab/).
```

*Classification: fact*

#### Evidence 5 — Strong review culture despite missing enforcement: 38% formal APPROVED review rate (second-highest in V1.2 catalog after kanata 44%), 86% any-review rate, 64% self-merge across 50-PR closed-merged sample. `pr-merge.yaml` uses `pull_request_target` but on closed/merged events with a third-party tag-pinned `actions-cool/check-user-permission@v2` gate.

```bash
gh api 'repos/wled/WLED/pulls?state=closed&per_page=100'
```

Result:
```text
sample_size: 50 closed-merged PRs. formal (APPROVED): 19 (38%). any_review_count>0: 43 (86%). self_merge: 32 (64%). 0 security_flagged. Self-merges are typically authors merging their own PRs AFTER receiving a review from someone else (not unreviewed self-merges — the 86% any-review rate confirms this). Context: 113 open PRs, 1167 merged lifetime. pull_request_target_count across 8 workflows: 1 (pr-merge.yaml, on closed events, calls actions-cool/check-user-permission@v2 with GITHUB_TOKEN — tag-pinned third-party action).
```

*Classification: fact*

#### Evidence 6 — community/profile reports has_security_policy=false. No SECURITY.md at root, .github/, or docs/. health_percentage: 75% (CONTRIBUTING + CODE_OF_CONDUCT present).

```bash
gh api 'repos/wled/WLED/community/profile'; gh api repos/wled/WLED/contents/SECURITY.md
```

Result:
```text
health_percentage: 75. has_contributing: true. has_code_of_conduct: true. has_security_policy: false. SECURITY.md: 404 at all checked paths. Published GHSA advisories count: 0 across 9 years (repo created 2016-12-20). Earlier public XSS disclosure: issue #3233 (breakingsystems, 2023-06-06, title: 'WiFi Scanning (and other features) vulnerable to Cross-Site Scripting (XSS)') — closed within 5 days without a published advisory. That earlier pattern (silent-fix rather than GHSA publication) matches the catalog-wide pattern (10/10 V1.2 scans now with 0 GHSA).
```

*Classification: fact*

#### Evidence 7 — Contributor concentration — blazoncek 46.0% + Aircoookie 24.6% of top-6 contributions. Top-1 share 46% is BELOW 80% solo-maintainer threshold. 100 total contributors. wled org owns repo (transferred from Aircoookie Feb 2025).

```bash
gh api repos/wled/WLED/contributors?per_page=6
```

Result:
```text
top_contributors: blazoncek (2314, 46.0%); Aircoookie (1236, 24.6%); softhack007 (479, 9.5%); netmindz (439, 8.7%); DedeHai (292, 5.8%); willmmiles (268, 5.3%). total_top6: 5028. total_contributor_count: 100. Dispersed pattern — no single contributor above 50%. wled org created 2025-01-31, now owns the repo; Aircoookie remains the 'WLED creator' account. netmindz explicitly self-describes as 'Release manager for @wled'. This is a small-org governance pattern, not solo-maintainer.
```

*Classification: fact*

#### Evidence 8 — Distribution channel: firmware is NOT shipped via npm (harness misidentified npm-wled as primary). Actual channels are GitHub Releases .bin/.bin.gz files + install.wled.me web-flasher (wled/WLED-WebInstaller downstream repo) + WLED iOS/Android apps for discovery.

```bash
gh api repos/wled/WLED/releases/latest --jq '.assets[].name'; gh api repos/wled/WLED-WebInstaller
```

Result:
```inference — coverage-gap annotation
v0.15.4 assets: ESP32-WROOM.bin, ESP32-WROVER.bin, ESP8266_debug.bin, etc. (12 .bin/.bin.gz firmware variants per target board). Distribution is via download-bin → flash-over-USB or download-bin → OTA-upload to existing WLED. install.wled.me is a WebSerial-based flasher that downloads the .bin and uses WebUSB/WebSerial to flash the ESP32 directly from the browser. The npm-wled package (package.json name='wled') is BUILD TOOLING for the web UI (Python + npm consume it for HTML minification) — it doesn't distribute firmware. Harness-detected channel 'npm-wled' is a ghostly channel; real channels are artifact-based.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 9 — Release cadence — stable v0.15.4 on 2026-03-14 (36 days before scan), v0.15.3 on 2025-12-04, v0.15.2 on 2025-11-29. v16.0.0-beta on 2026-04-11 (9 days before scan). Nightlies daily.

```bash
gh api 'repos/wled/WLED/releases?per_page=10'
```

Result:
```text
68 total releases. Latest stable: v0.15.4 (2026-03-14). Beta for next major: v16.0.0-beta (2026-04-11). Prereleases: nightly (daily), v16.0.0-beta (9d), v0.15.2-beta1 (6m old). Active cadence — 2 releases in last 30 days. Stable lag: 36 days from v0.15.4 to scan. The GHSA-2xwq-cxqw-wfv8 critical (E1) — if netmindz's 'already fixed' assessment is correct — may be fixed in v0.15.4 (released 6 weeks after the public issue opened) or may still be pending backport. Publicly UNCONFIRMED.
```

*Classification: fact*

#### Evidence 10 — Python build-tooling deps (via platformio) carry 73+ CVEs across 9 packages: urllib3 (28 vulns), requests (13), starlette (7), bottle (8), certifi (6), uvicorn (4), marshmallow (3), idna (2), h11 (1). These are BUILD-TIME deps, not firmware runtime deps — firmware ships pure C++ for ESP32. No .github/dependabot.yml present despite Dependabot Updates workflow showing active.

```bash
cat requirements.txt; for pkg in $(cat requirements.txt | awk -F'==' '{print $1}'); do curl -s https://api.osv.dev/v1/query -d '{"package":{"name":"'$pkg'","ecosystem":"PyPI"}}'; done
```

Result:
```inference — threat-scope annotation
runtime_count: 29 PyPI deps (platformio + transitives). osv.dev totals: urllib3 28, requests 13, starlette 7, bottle 8, certifi 6, uvicorn 4, marshmallow 3, idna 2, h11 1, clean-css (npm) 1 = 73 CVE records. Relevance: these are build-time deps consumed by platformio during .bin firmware compilation. The firmware itself ships as C++ compiled for ESP32 — no Python or Node runtime on device. Attack surface: only during build-from-source workflow, and only if PyPI is compromised OR a developer pulls a malicious transitive dep. Not a direct consumer risk for binary-install users.
```

*Classification: inference — threat-scope annotation*

#### Evidence 11 — Dangerous-primitive grep produced 19 hits for deserialization family — ALL are `deserializeJson` / `deserializeSegment` / `deserializeState` calls on the ArduinoJson library, which is SAFE JSON deserialization (not Java-ObjectInputStream-style RCE class). The V1.2.x pickle.load-widening regex introduced in session 6 produces a false-positive here.

```bash
docs/phase_1_harness.py # code_patterns.dangerous_primitives.deserialization
```

Result:
```inference — scanner-coverage-gap annotation
19 hits across: wled00/json.cpp, wled_server.cpp, wled_serial.cpp, FX_fcn.cpp, udp.cpp, ws.cpp, set.cpp, wled.cpp, remote.cpp, presets.cpp, etc. All are `deserializeJson(*pDoc, STREAM)` or `deserializeMap()` / `deserializeState()` / `deserializeSegment()` — the ArduinoJson library's safe JSON parsing API, NOT Java ObjectInputStream or Python pickle. Regex false-positive on the widened deserialization pattern. Contrasts with freerouting (entry 24) where every deserialization hit was a real ObjectInputStream call. Calibration note: the widened regex captures both safe (deserializeJson) and unsafe (pickle, ObjectInputStream) deserialization families; Phase 4 or compute-side disambiguation by language+library is needed to prevent FP escalation.
```

*Classification: inference — scanner-coverage-gap annotation*

#### Evidence 12 — Q2 signal `q2_oldest_open_security_item_age_days` fires 214 days but the 214-day match is a FALSE POSITIVE — PR #4942 'Add internal user backup functionality to Security & Update page' matches on the word 'Security' in the title but is a feature addition, not a vulnerability fix.

```bash
gh api 'repos/wled/WLED/pulls?state=open' --jq '.[] | select(.title | test("Security|vuln|cve|xss|csrf|rce|injection|auth|deserializ|disclosure|advisory"; "i")) | {number, title, created_at}'
```

Result:
```inference — scanner-coverage-gap annotation
PR #4942 'Add internal user backup functionality to Security & Update page' — 213 days old (created 2025-09-19), a feature PR that extends the settings > Security & Update page (nothing to do with vulnerability remediation). PR #5340 (issue) is the actual security item at 76 days. Phase 4 accepts the Q2 signal firing red because the real driver (unresolved GHSA + 74-day silent public issue) IS red-worthy — the compute signal happens to fire red for a different reason, but the cell color is correct. Scanner-side note: the security-keyword regex over PR titles produces FPs on 'Security & Update page' substring matches; disambiguation could check PR labels + body for actual security-topic vs feature-page-topic.
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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `01328a65c17c5a74aa53938f36efac27168267a1` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
