# ghostty-org/ghostty — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

Ghostty is a well-adopted, actively-maintained Zig terminal emulator with modern ruleset-based branch protection and a working disclosure channel (5 GHSA advisories). Two structural concerns keep this scan at Caution rather than Clean: the author holds 85.9% of commit share, and there is no formal versioned release — installs pull HEAD. Pin a specific SHA for production use; otherwise Homebrew-installed ghostty is a reasonable default for individual developer workstations.

**Scanned:** 2026-04-20 · main @ dcc39dc · 51,181 stars · MIT · Zig

---

## Trust scorecard

- ⚠ **Does anyone check the code?** Partly — ruleset-based protection + CODEOWNERS, but concentration risk
- ✓ **Do they fix problems quickly?** Yes — active project, zero open security issues, responsive maintainer
- ⚠ **Do they tell you about problems?** Partly — 5 GHSA advisories published, but no SECURITY.md
- ⚠ **Is it safe out of the box?** Partly — installing means pulling HEAD, not a reviewed release

## Top concerns

1. **[Warning] Solo-maintainer concentration — Mitchell Hashimoto holds 85.9% of commit share** A single developer approves or writes the vast majority of ghostty commits.

2. **[Warning] No formal versioned releases — installers pull HEAD, not semver** The only tagged release (as of HEAD) is 'tip' from 2022-11.

3. **[Info] No SECURITY.md — disclosure policy implicit via GitHub Security tab only** No SECURITY.md file documents the vulnerability reporting channel.

## What should I do?

**Install with these conditions.** Audit before enterprise dependency; track fallback maintainer bench.

---

*stop-git-std · scanned 2026-04-20 · [ghostty-org/ghostty](https://github.com/ghostty-org/ghostty)*
