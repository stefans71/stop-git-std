# wezterm/wezterm — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

wezterm — 25k-star Rust terminal emulator + SSH client, near-solo by @wez (97.2% share). 30 CI workflows; zero branch protection; zero CODEOWNERS. Last release 2024-02-03 (807 days before scan) despite main active through 2026-04-01 — users on homebrew/winget/distro-stable run 2-year-old code. 0 advisories in 8 years. Zero scorecard overrides.

**Scanned:** 2026-04-20 · main @ 577474d · 25,643 stars · NOASSERTION · Rust

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — solo-maintainer (wez 97%), 3.3% formal review, no branch protection on a 25k-star privileged tool
- ✗ **Do they fix problems quickly?** No — 807-day release stall (last tag 2024-02-03, main active through 2026-04-01). Fix-to-user latency is 26 months.
- ⚠ **Do they tell you about problems?** Partly — CONTRIBUTING present, but no SECURITY.md and 0 published advisories in 8 years on a privileged tool
- ⚠ **Is it safe out of the box?** Partly — release artifacts on GitHub + homebrew + winget, no documented integrity verification; you're installing 2-year-old shipped code

## Top concerns

1. **[Warning] Solo-maintainer concentration — wez holds 97.2% of top-contributor commit share on a 25k-star privileged tool** The supply-chain blast radius for wezterm is substantial.

2. **[Warning] 807-day release stall — latest tag 2024-02-03 despite main active through 2026-04-01** If you installed wezterm via winget, homebrew (stable), or a distro stable package, you are running February 2024 code.

3. **[Warning] No SECURITY.md + 0 published GHSA advisories in 8 years on a privileged tool** No documented private channel for a vulnerability reporter to use.

## What should I do?

**Install with these conditions.** Pin to a reviewed release tag; audit the Lua config you run since it can spawn subprocesses.

---

*stop-git-std · scanned 2026-04-20 · [wezterm/wezterm](https://github.com/wezterm/wezterm)*
