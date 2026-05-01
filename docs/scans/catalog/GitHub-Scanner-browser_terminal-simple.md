# BatteredBunny/browser_terminal — Simple Report

**Verdict: ✗ Critical.** Don't install this — material risks identified.

BatteredBunny/browser_terminal — 10-star Chrome+Firefox extension exposing browser-tab shell access via a Go native-messaging host. installation.md directs Chrome users to chrome.google.cm (Cameroon TLD) instead of .com — a live typosquat URL (F0 Critical). Firefox install path is correct. Unsigned Go binary + 10-month release stall + single-maintainer governance floor complete the picture.

**Scanned:** 2026-04-20 · main @ 9a77c4a · 10 stars · GPL-3.0 · Go

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 0% formal / 0% any-review across 12 lifetime PRs, single human maintainer, no branch protection
- ✓ **Do they fix problems quickly?** Yes (structurally) — 0 open security issues; dependabot active; small dep-graph surface
- ✗ **Do they tell you about problems?** No — no SECURITY.md, no CONTRIBUTING, no disclosure channel documented; 0 published advisories
- ✗ **Is it safe out of the box?** No — install doc directs Chrome users to a typosquat TLD; binary install has no integrity verification

## Top concerns

1. **[Critical] installation.md points Chrome users to `chrome.google.cm` — Cameroon-TLD typosquat of chrome.google.com** Any user who installs via the README's Chrome link lands on a Cameroon-TLD URL, not the real Chrome Web Store.

2. **[Warning] Unsigned Go binary + `sudo mv` install with no documented integrity verification** You are trusting the GitHub-Releases pipeline end-to-end, including whatever GitHub Actions workflow produced the binary, without a cross-check.

3. **[Warning] Release cadence stalled 10 months — v1.4.7 from June 2025; main has unshipped changes** Users are on 10-month-old code even though the repo looks active.

## What should I do?

**Don't install this.** Do NOT follow the Chrome install URL as written. Go to chrome.google.com/webstore directly and search for 'browser_terminal'.

---

*stop-git-std · scanned 2026-04-20 · [BatteredBunny/browser_terminal](https://github.com/BatteredBunny/browser_terminal)*
