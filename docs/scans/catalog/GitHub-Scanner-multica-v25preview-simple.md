# multica-ai/multica — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

multica-ai/multica — 23.5k-star open-source agentic platform (TS+Go monorepo, Electron desktop, GHCR self-host), 4 months old, 84 contributors. The 888888 dev-verification-code Critical from the 2026-04-19 prior scan is now Warning (APP_ENV=production gate landed ~2026-04-18). Active responsiveness — 5 security issues closed in past 8 days. Open concerns: branch-protection ruleset declared but enforcement disabled (5.7% review rate, 73% self-merge), curl|bash installer skips SHA256 verification on macOS/Linux (Windows DOES verify), and #1114 LD_PRELOAD privesc on agent custom_env still open at 16 days. Caution.

**Scanned:** 2026-05-02 · main @ 3df95c8 · 23,547 stars · NOASSERTION · TypeScript

**Scan coverage gaps:** OSSF not indexed · gitleaks unavailable · Dependabot unknown · org rulesets unknown · npm registry status unavailable

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 5.7% review rate, 73% self-merge, branch-protection ruleset declared but enforcement disabled, no CODEOWNERS
- ⚠ **Do they fix problems quickly?** Mixed — 5 security issues closed in past 8 days (responsive), but 4 still open with oldest 16 days (privesc unaddressed)
- ✗ **Do they tell you about problems?** No — no SECURITY.md, no published advisories, no Dependabot config; reporters use generic issues
- ⚠ **Is it safe out of the box?** Partly — Homebrew path is safe; curl|bash path on macOS/Linux skips checksum verification (Windows installer does verify); APP_ENV=production gate defends the 888888 path by default

## Top concerns

1. **[Warning] Self-hosted hardening relies on operator preserving APP_ENV=production gate that disables the 888888 dev verification code** Out-of-the-box Docker self-host is hardened.

2. **[Warning] curl-pipe-from-main installer with no checksum verification on macOS/Linux (Windows installer DOES verify)** On macOS/Linux, the installer trusts whatever binary lives at the release URL.

3. **[Warning] Branch-protection ruleset present-but-disabled, no CODEOWNERS, no enforced rules-on-default — visible-but-toothless governance posture** Multica has the governance scaffold (a ruleset entry exists) but enforcement is off.

## What should I do?

**Install with these conditions.** If self-hosting, do NOT change APP_ENV from `production`. Verify your `docker compose ... config` shows `APP_ENV=production` before going live; treat any non-production APP_ENV as a public-instance disqualifier until MULTICA_DEV_VERIFICATION_CODE is also empty.

---

*stop-git-std · scanned 2026-05-02 · [multica-ai/multica](https://github.com/multica-ai/multica)*
