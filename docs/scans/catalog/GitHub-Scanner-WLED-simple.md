# wled/WLED — Simple Report

**Verdict: ✗ Critical.** Don't install this — material risks identified.

WLED — 17.8k-star ESP32 LED firmware, wled-org-owned, 100 contributors. Critical via F0: unresolved private GHSA-2xwq-cxqw-wfv8, 74 days silent after researcher's public complaint on issue #5340; 0.15.x backport unverified. F1 Warning: default-install has no auth, CORS wildcard, unauthenticated /reset — any same-LAN page can control the device. Positives: 38%/86% review rate, CodeQL + Copilot active.

**Scanned:** 2026-04-20 · main @ 01328a6 · 17,837 stars · EUPL-1.2 · C++

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — anti-destruction-only ruleset (no review rule) + no CODEOWNERS, despite strong 38% formal / 86% any-review culture
- ✗ **Do they fix problems quickly?** No — unresolved GHSA-2xwq-cxqw-wfv8 with 74-day maintainer silence after public complaint (issue #5340); backport status unknown
- ⚠ **Do they tell you about problems?** Partly — CONTRIBUTING + CoC present (health 75%); no SECURITY.md; private-advisory permissions misconfigured per #5340 thread; 0 advisories in 9 years
- ✗ **Is it safe out of the box?** No — default-install has no authentication; CORS wildcard on all origins/methods/headers; unauthenticated /reset (F1)

## Top concerns

1. **[Critical] Unresolved private GHSA-2xwq-cxqw-wfv8 — researcher publicly reports maintainer non-response; 74 days silent since last comment; backport to 0.15.x publicly unconfirmed** A researcher documented both (a) substantive findings (at least one 'critical' per netmindz's own words) and (b) a disclosure-handling failure.

2. **[Warning] Default-install WLED has NO authentication — CORS wildcard on all endpoints + unauthenticated `/reset` + optional-PIN OTA make any same-LAN webpage a control surface** A WLED device on your home WiFi, running factory defaults, can be controlled (read config, change settings, rebooted, potentially reflashed) by any webpage that anyone on the same LAN visits.

3. **[Warning] Nightly deployment uses `andelf/nightly-release@main` (mutable ref); 0 SHA-pinned actions across 8 workflows; PR #5386 proposes fix but unmerged 60 days** The nightly firmware distribution channel (install.wled.me/nightly) is structurally dependent on the personal GitHub account of `andelf`.

## What should I do?

**Don't install this.** Pin to a specific WLED version only after reviewing the GHSA-2xwq-cxqw-wfv8 resolution in WLED's public changelog; do not expose an unupdated WLED device to untrusted networks.

---

*stop-git-std · scanned 2026-04-20 · [wled/WLED](https://github.com/wled/WLED)*
