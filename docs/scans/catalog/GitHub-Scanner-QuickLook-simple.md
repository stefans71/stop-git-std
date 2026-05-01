# QL-Win/QuickLook — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

QuickLook — 23k-star C# Windows Explorer extender that brings macOS Quick-Look semantics to Windows. Press spacebar on any file; 1 of 21 plugins parses it and shows a preview. Parser surface IS the risk model: archives, PE binaries, Office, PDF, images all run through parsers. Two-maintainer repo (xupefei + emako, 94% combined), no branch protection, 0 advisories in 9 years, `latest` tag stale since Dec 2024 (semver 4.5.0 is current). Zero scorecard overrides.

**Scanned:** 2026-04-20 · main @ 0cda83c · 23,083 stars · GPL-3.0 · C#

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 5.1% formal review + no branch protection + 94% two-maintainer share on a privileged shell-integration tool
- ✓ **Do they fix problems quickly?** Yes — 0 open security issues, active semver releases (4.5.0 6 days before scan, 4.4.0 ~100 days before)
- ✗ **Do they tell you about problems?** No — no SECURITY.md, no CONTRIBUTING, 0 published advisories in 9 years on a parser-heavy tool
- ⚠ **Is it safe out of the box?** Partly — MSI installer with no documented checksums; 21 parsers run on any hovered file; bundled vendored libraries uncertain-version

## Top concerns

1. **[Warning] 21-plugin untrusted-file-parsing surface — archives, PE, Office, PDF, images, mail on every Explorer hover** Running QuickLook on a Windows workstation means every file you hover-preview is fed through a parser.

2. **[Warning] Vendored minified JS libraries in MarkdownViewer/ImageViewer — no upstream-version tracking or automated update** Installed QuickLook users receive the bundled-library version from whenever a maintainer last refreshed it — which may be months or years stale relative to upstream fixes.

3. **[Warning] No SECURITY.md and zero published GHSA advisories in 9 years on a parser-heavy tool** Advisory syndication does not happen.

## What should I do?

**Install with these conditions.** If you download a file from an untrusted source, do NOT hover-preview it in Explorer until you have scanned it with AV; pressing spacebar is effectively running a parser on the content.

---

*stop-git-std · scanned 2026-04-20 · [QL-Win/QuickLook](https://github.com/QL-Win/QuickLook)*
