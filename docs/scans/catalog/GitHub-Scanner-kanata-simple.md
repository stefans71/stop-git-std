# jtroo/kanata — Simple Report

**Verdict: ✗ Critical.** Don't install this — material risks identified.

kanata — 7k-star Rust keyboard-remapper daemon by jtroo + ItayGarin. Runs with elevated privileges on Linux/macOS/Windows; every keystroke flows through it. Critical verdict via C20: keylogger-class privileged tool + no branch protection + active 8-day release cadence. But the governance story is nuanced — **44% formal PR review** is the highest in the V1.2 catalog; the two-maintainer pair runs disciplined voluntary review. The fix for F0 is codifying what's already happening.

**Scanned:** 2026-04-20 · main @ 1c496c0 · 7,179 stars · LGPL-3.0 · Rust

---

## Trust scorecard

- ⚠ **Does anyone check the code?** Partly — 44% formal PR review (highest in V1.2 catalog) + active 2-maintainer pair, but no branch protection enforcement
- ✓ **Do they fix problems quickly?** Yes — 0 open security issues, 58 releases, latest 8 days before scan (v1.12.0-prerelease-2)
- ✗ **Do they tell you about problems?** No — no SECURITY.md, no CONTRIBUTING, 0 published advisories in 4 years on a privileged input daemon
- ⚠ **Is it safe out of the box?** Partly — `cargo install kanata` integrity via crates.io; GitHub Releases binaries unsigned; privileged-tool threat model

## Top concerns

1. **[Critical] Governance single-point-of-failure on a privileged keyboard-interception daemon with active release cadence (C20)** A compromise of jtroo's GitHub or crates.io publisher account reaches every user's keyboard-input stream on the next prerelease.

2. **[Warning] No SECURITY.md + 0 published advisories in 4 years on a keyboard-interception daemon** GHSA syndication does not flow from kanata.

3. **[Warning] No Dependabot config — Rust workspace with 15+ Cargo.toml files has no automated CVE-watch on dep graph** A CVE against a core Rust dep in kanata's graph (e.g., a serialize-parser bug in serde's JSON layer used by the tcp_protocol crate) would not surface automatically.

## What should I do?

**Don't install this.** Pin to a reviewed release tag; run kanata as a dedicated user with minimum-needed input-device privileges.

---

*stop-git-std · scanned 2026-04-20 · [jtroo/kanata](https://github.com/jtroo/kanata)*
