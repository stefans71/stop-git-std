# WhiskeySockets/Baileys — Simple Report

**Verdict: ✗ Critical.** Don't install this — material risks identified.

Baileys — 9k-star reverse-engineered WhatsApp Web client. Critical via F0: using Baileys attaches your WhatsApp account to an unofficial client, violating WhatsApp's ToS + risking account suspension. PR #1996 vulnerability fix stale-closed 148 days, maintainer-promised replacement never shipped. 14 runtime CVEs (ws × 5). Zero governance. 150-day release stall. V13-3 trigger fires.

**Scanned:** 2026-04-20 · main @ 8e5093c · 9,034 stars · MIT · JavaScript

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 0 branch protection + 0 rulesets + no CODEOWNERS + 89.5% top-2 maintainer concentration; PR sample empty (harness gap E8)
- ✗ **Do they fix problems quickly?** No — PR #1996 vulnerability-fix stale-closed after 148 days; 14 runtime-dep CVEs (ws × 5, protobufjs × 4); 150-day release stall on v7.0.0-rc.9
- ✗ **Do they tell you about problems?** No — no SECURITY.md + no CONTRIBUTING + 0 advisories in 4 years + documented vulnerability-fix PR stale-out (F2, F6)
- ✗ **Is it safe out of the box?** No — using Baileys attaches consumer's WhatsApp account to a reverse-engineered unofficial client; ToS-violation + account-ban risk on default path (F0)

## Top concerns

1. **[Critical] Reverse-engineered, unofficial WhatsApp client — ToS violation + account-ban risk is inherent to use; maintainers explicitly disclaim endorsement** Any user who connects their WhatsApp account to a Baileys bot risks WhatsApp-side account suspension at any time.

2. **[Warning] child_process.exec with shell string-interpolation in extractVideoThumb — latent command-injection pattern** For direct consumers of baileys: if you pass only library-generated (tmpdir/random) paths, you're not currently exposed.

3. **[Warning] Community-submitted vulnerability-fix PR #1996 closed unmerged via stale-bot after 148 days; maintainer-promised replacement never materialized; library still ships deprecated `request` dep** The dep-modernization that an external contributor offered for free (working tested PR) is not available to users of the library.

## What should I do?

**Don't install this.** Do NOT attach a personal WhatsApp account you rely on to a Baileys-based bot. Use a burner number; understand that account suspension is a documented outcome of third-party client use.

---

*stop-git-std · scanned 2026-04-20 · [WhiskeySockets/Baileys](https://github.com/WhiskeySockets/Baileys)*
