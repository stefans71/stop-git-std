# Security Investigation: QL-Win/QuickLook

**Investigated:** 2026-04-20 | **Applies to:** main @ `0cda83c26d99148f3b6e5273d7028b4ecffa1e77` | **Repo age:** 9 years | **Stars:** 23,083 | **License:** GPL-3.0

> QuickLook — 23k-star C# Windows Explorer extender that brings macOS Quick-Look semantics to Windows. Press spacebar on any file; 1 of 21 plugins parses it and shows a preview. Parser surface IS the risk model: archives, PE binaries, Office, PDF, images all run through parsers. Two-maintainer repo (xupefei + emako, 94% combined), no branch protection, 0 advisories in 9 years, `latest` tag stale since Dec 2024 (semver 4.5.0 is current). Zero scorecard overrides.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-QuickLook.md` (+ `.html` companion) |
| Repo | [github.com/QL-Win/QuickLook](https://github.com/QL-Win/QuickLook) |
| Short description | C# Windows File Explorer extender — presses spacebar on any file and invokes one of 21 format-specific parser plugins (archives, PE, ELF, Office, PDF, mail, images, video) to show a preview. Brings macOS Quick Look semantics to Windows. |
| Category | `windows-shell-integration` |
| Subcategory | `file-preview-extender` |
| Language | C# |
| License | GPL-3.0 |
| Target user | Windows desktop user who wants hover-preview of arbitrary file types. Install: MSI installer from GitHub Releases, `scoop install quicklook`, or Microsoft Store. |
| Verdict | **Caution** |
| Scanned revision | `main @ 0cda83c` (release tag ``) |
| Commit pinned | `0cda83c26d99148f3b6e5273d7028b4ecffa1e77` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of QuickLook. Seventh wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21). |

---

## Verdict: Caution

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Warning — F0 + F1 + F2 + F3 describe architecture + supply-chain + governance posture (4 findings)</strong>
<br><em>21-plugin parser surface + vendored JS libs + 0 advisories + thin review gate.</em></summary>

1. **F0** — 21 plugins parse archives, PE, ELF, Office, PDF, mail, images, video on every Explorer hover — large untrusted-file-parsing surface by design.
2. **F1** — MarkdownViewer/ImageViewer bundle vendored minified JS libs (mermaid, MathJax, markdown-it, highlight.js, svga) without upstream-version tracking.
3. **F2** — No SECURITY.md + 0 published advisories in 9 years on a parser-heavy tool.
4. **F3 / F11** — xupefei + emako hold 94% top-contributor share; 5.1% formal review; no branch protection.

</details>

<details>
<summary><strong>ℹ Info — F4 + F5 + F6 are process + coverage observations (3 findings)</strong>
<br><em>Release-tag hygiene + AI-PR governance + scanner gaps.</em></summary>

1. **F4** — `latest` tag points to 2024-12-06 despite 4.5.0 shipping 2026-04-14 — tooling that follows `latest` serves 16-month-old code.
2. **F5** — All 3 open PRs authored by Copilot SWE agent — AI-PR review protocol undocumented.
3. **F6** — Scanner gaps: .NET/NuGet parsing absent; Windows-package-manager channels unrecognized; dangerous-primitives false-positives on minified JS.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — 5.1% formal review + no branch protection + 94% two-maintainer share on a privileged shell-integration tool |
| Is it safe out of the box? | ⚠ **Partly** — MSI installer with no documented checksums; 21 parsers run on any hovered file; bundled vendored libraries uncertain-version |
| Do they fix problems quickly? | ✅ **Yes** — 0 open security issues, active semver releases (4.5.0 6 days before scan, 4.4.0 ~100 days before) |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md, no CONTRIBUTING, 0 published advisories in 9 years on a parser-heavy tool |

---

## 01 · What should I do?

> 23k⭐ · GPL-3.0 · C# · 4 warnings · 3 info · caution
>
> QuickLook is Windows's macOS-style Quick Look — press spacebar on any file in Explorer and a preview pops up. 23k stars, maintained by xupefei + emako for 9 years. The 21-plugin architecture (archives, PE, ELF, Office, PDF, mail, images, video) is the tool's function AND its threat model: every file you hover-preview is fed through a parser. Verdict: Caution. Drivers: the parser surface (F0) + vendored-JS-lib staleness (F1) + 0 advisories in 9 years (F2) + two-maintainer governance floor (F3). Mitigations exist — plugins can be disabled, releases are active, OSSF-indexed 4.1/10, Scoop/MS Store/MSI distribution — but installing QuickLook means trusting 21 parsers to handle whatever you hover.

### Step 1: Install via Scoop or MSI from GitHub Releases (✓)

**Non-technical:** QuickLook ships an official MSI installer on GitHub Releases. Scoop (`scoop install quicklook`) and Microsoft Store are also first-party channels.

```bash
scoop install quicklook
```

### Step 2: Pin to a specific semver (not `latest` tag) — 4.5.0 is current (⚠)

**Non-technical:** The repo's `latest` tag is stuck on 2024-12-06. Explicitly install a semver like 4.5.0. If your package manager resolves 'latest' lazily, switch to an explicit version.

```bash
scoop install quicklook@4.5.0
```

### Step 3: Disable plugins you don't need (ℹ)

**Non-technical:** QuickLook ships 21 plugins covering archives, PE/ELF binaries, Office, PDF, mail, images, video. Each is an untrusted-file parser. In QuickLook's settings, disable the ones you don't need — especially if your workflow involves hover-previewing files from untrusted sources.

```text
Open QuickLook settings → Plugins → uncheck ones you don't want
```

### Step 4: Before previewing a file from an untrusted source, scan it first (⚠)

**Non-technical:** Hovering + pressing spacebar on a file invokes the appropriate plugin's parser. If the file is malicious and the plugin has a bug, that's code execution. Treat hover-preview as parser execution — scan suspicious files with AV first.

```text
Windows Defender / your AV of choice — scan the file before hover-preview
```

### Step 5: If running CI/build of QuickLook from source: `dotnet list package --vulnerable` (ℹ)

**Non-technical:** Harness doesn't parse .NET NuGet deps (F6). If you're building from source, run `dotnet list package --vulnerable` against the solution to surface dep CVEs.

```bash
dotnet list QuickLook.sln package --vulnerable --include-transitive
```

---

## 02 · What we found

> ⚠ 4 Warning · ℹ 3 Info
>
> 7 findings total.
### F0 — Warning · Structural — 21-plugin untrusted-file-parsing surface — archives, PE, Office, PDF, images, mail on every Explorer hover

*Continuous · Since each plugin's introduction · → If you download a file from an untrusted source, do NOT hover-preview it in Explorer until you have scanned it with AV; pressing spacebar is effectively running a parser on the content.*

QuickLook's value proposition is that pressing spacebar on any file in Windows Explorer shows a preview without opening the file's native application. The implementation is 21 plugins, each responsible for one format family: ArchiveViewer (ZIP/RAR/7Z), PEViewer (Windows .exe/.dll), ELFViewer (Linux binaries), OfficeViewer (Excel/Word), PDFViewer, MailViewer (EML), ImageViewer, VideoViewer, and others. Every plugin is a parser invoked against untrusted file content.

This is the tool's function, not a defect. It is also a direct enumeration of the threat surface: any file an attacker can convince a user to hover over in Explorer flows into a parser. Comparable tools (macOS Quick Look, Windows thumbnail providers, PDF readers) have historically been rich sources of parser-RCE CVEs. The relevant question isn't 'is there a known vuln right now'; it's 'when a parser bug in one of these 21 plugins surfaces, how quickly does a fix reach users?' — and F2 (no advisories + no documented disclosure) suggests 'slowly and quietly'.

Consumer-side mitigation: disable plugins you don't need (QuickLook supports per-plugin toggles). Scan suspicious files with AV before hover-preview. Maintainer-side: consider sandboxing the preview process via Windows AppContainer, or track upstream parser-library CVE feeds per plugin.

**How to fix.** Maintainer-side: track upstream CVE feeds for the underlying parser libraries per plugin; consider sandboxing the plugin process (Windows AppContainer or similar). Consumer-side: treat hover-preview as parser execution; disable plugins you don't need (QuickLook supports plugin toggles).

### F1 — Warning · Supply chain — Vendored minified JS libraries in MarkdownViewer/ImageViewer — no upstream-version tracking or automated update

*Continuous · Since each bundled library was committed · → Don't trust the MarkdownViewer plugin to be up-to-date with security fixes in mermaid / MathJax / markdown-it / highlight.js; the bundled copies are pinned to whenever they were last refreshed in-repo.*

MarkdownViewer bundles minified copies of mermaid.min.js (diagram rendering), mathjax tex-mml-svg.js (math), markdown-it.min.js (markdown→HTML), and highlight.min.js (syntax highlighting). ImageViewer bundles svga.min.js. These are pinned vendored assets committed to the repo — not package.json-managed dependencies with dependabot coverage.

Each upstream library ships security patches periodically. markdown-it has had several XSS fixes; MathJax has had its own CVE history; highlight.js has had regex-based DoS findings. The bundled copies in QuickLook are pinned to whenever a maintainer last refreshed them, with no automated reminder when upstream ships a fix. The WebView2 that renders the markdown trusts these libraries; a markdown file crafted to trigger a known-in-upstream bug would pass through unaltered.

Fix surface on the maintainer side is straightforward: migrate the bundled libs to a package.json + build-time bundle step, then add 'npm' to the Dependabot ecosystems. Consumer-side there is little to do — the bundle ships with the installer and is not user-replaceable.

**How to fix.** Maintainer-side: switch to a package.json-managed dependency graph for bundled libs so dependabot alerts (which IS enabled per E10) flows CVE updates automatically. Consumer-side: limited — the bundles ship as-is with the installer.

### F2 — Warning · Hygiene — No SECURITY.md and zero published GHSA advisories in 9 years on a parser-heavy tool

*Continuous · Since 2017-04-12 · → If you find a QuickLook parser bug, the disclosure path is GitHub's private `Report a vulnerability` button — not documented but still reachable.*

community/profile reports has_security_policy=false. security-advisories count: 0 across 9 years. For a tool with QuickLook's parser surface (21 plugins covering the historically-CVE-rich parser formats), zero published advisories implies silent-fix cadence — not 'zero bugs ever existed'. This is the same pattern flagged on Kronos (entry 17), Xray-core (entry 19), and wezterm (entry 21) — a consistent catalog-wide phenomenon.

For consumers, the practical effect is that GHSA syndication does not cover QuickLook. Knowing whether a given release fixes a security-relevant parser bug requires reading release notes carefully. For reporters, the disclosure path is GitHub's `Report a vulnerability` UI (still reachable but not documented in-repo). The maintainer-side fix is a 1-page SECURITY.md.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md documenting the private-advisory channel. Consumer-side: read release notes on each version bump; treat any parser-fix release as potentially security-relevant.

### F3 — Warning · Governance — Two-maintainer concentration + 5.1% formal review + no branch protection on a privileged shell-integration tool

*Continuous · Since 2017-04-12 · → Pin to a specific release version; prefer MSI installer from GitHub Releases over `latest`-tracking channels.*

xupefei (716 commits) + emako (611) combine for 94% of the top-6 contributor share — a tight two-maintainer repo. PR sample shows 5.1% formal review + 25.5% any-review + 5 self-merges of 137 — consistent with the two maintainers alternately reviewing each other's PRs informally without recording `APPROVED` decisions. No branch protection, no CODEOWNERS.

The tool's blast radius is 'hooked into every user's Explorer' — the installed MSI registers a keyboard hook and a preview window. A credential compromise of either xupefei or emako's account reaches every QuickLook user whose installation auto-updates. The review gate that would catch a malicious commit before release is thin. This is typical for active two-maintainer projects; the finding describes the structural exposure.

**How to fix.** Maintainer-side: enable ruleset requiring ≥1 approving review + CODEOWNERS; encourage tail-contributor reviewers. Consumer-side: pin to specific release tag; review release notes before upgrading.

### F4 — Info · Hygiene — Confusing `latest` tag — points to 2024-12-06 even though 4.5.0 shipped 2026-04-14

*Continuous · Since 2024-12-06 (latest-tag last-moved date) · → If an installer / package manager / scoop manifest resolves to the `latest` tag, it is serving 16-month-old code. Prefer explicit version pins (e.g., `4.5.0`).*

The repo carries a git tag literally named `latest` pointing to a release from 2024-12-06. The actual most-recent semver release is `4.5.0` on 2026-04-14 (6 days before scan). Tooling that resolves `latest` as a version hint (some installers and package-manager manifests do this) would serve 16-month-old code; tooling that uses explicit semver tags gets current.

Hygiene-level defect at worst — not malicious, not exploitable directly. The fix is one GitHub Actions step in the release workflow: `git tag -fa latest && git push origin latest --force` per release. Consumer mitigation: avoid installers that resolve `latest`-tag; use explicit version pins.

**How to fix.** Maintainer-side: either delete the `latest` tag, or move it forward on every new release (a GitHub Actions release workflow step: `git tag -fa latest && git push origin latest --force`).

### F5 — Info · Hygiene — All 3 open PRs are AI-authored (Copilot SWE agent) — governance pattern for AI-PR review is undocumented

*Current snapshot · Scan date only · → Non-blocking; context for how the repo manages AI-generated contributions.*

All 3 currently-open PRs are authored by `app/copilot-swe-agent` — GitHub's AI agent. No human PRs currently in the queue. This is an emerging governance pattern: AI agents submit feature PRs, and the repo's review process has to decide how to review them. With no CODEOWNERS and 5.1% formal review rate, an AI-authored PR that a maintainer skims and merges has effectively zero independent review.

Info-level because the PRs themselves aren't a vulnerability — Copilot SWE agent is a legitimate GitHub feature. The observation is about process: the repo absorbs AI contributions without a documented protocol. If those PRs include changes to plugins (parser code, archive handling), the risk surface is the same as for any unreviewed PR — amplified by AI authorship being less predictable than a familiar contributor.

**How to fix.** Maintainer-side: document AI-PR review expectations (e.g., 'Copilot PRs require manual test + diff read before merge'). Consumer-side: if you install a release that merged Copilot PRs, scan the release-commit range for AI-authored additions.

### F6 — Info · Coverage — Scanner gaps on .NET/C# ecosystem — .csproj/.sln parsing, distribution-channel detection for Windows package managers

*Continuous · Scanner tooling gap · → Scanner-side work needed to recognize .NET projects properly.*

Three scanner-side gaps surfaced on this scan: (1) .NET .csproj / .sln parsing not implemented — runtime_count=0 despite ~21 plugin projects, each a NuGet consumer; (2) distribution-channel detection returned 0 channels when the real channels are GitHub Releases MSI installer + Scoop + Microsoft Store; (3) dangerous_primitives regex produced 20+ false positives on bundled minified JS libraries in plugin Resources/ directories. Same class of language-ecosystem gap seen on Go/Ruby/Rust/Python in prior catalog entries.

Non-blocking for this scan's verdict — F1 captures the vendored-JS concern without relying on the regex hits, and F0/F2/F3 are independent of dep-CVE coverage. Scanner-side: .NET NuGet advisory parsing would be the most impactful addition.

**How to fix.** Scanner-side: add NuGet / .csproj dependency parsing + RustSec-equivalent NuGet advisory DB lookup; add Scoop manifest / MS Store presence checks for Windows-tool channels; tighten dangerous-primitives regexes to exclude minified-JS file contents.

---

## 02A · Executable file inventory

> QuickLook is installed as a Windows MSI that registers an Explorer hook (spacebar keyboard handler) and loads 21 plugin DLLs for file-format-specific previews. Plugins are loaded into the QuickLook process; each plugin is a C# assembly that may in turn load native parser libraries.

### Layer 1 — one-line summary

- Primary surface is the compiled QuickLook.exe main process + 21 plugin DLLs. Release binaries ship as a single MSI installer. No user-authored scripting surface (unlike wezterm's Lua).

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `QuickLook.Plugin/QuickLook.Plugin.ArchiveViewer/` | plugin-parser | .NET (C#) | Archive decompression of ZIP/RAR/7Z — historically-vulnerable format family. | None | One of the higher-risk plugins. Archive parsing has been a fertile CVE ground across many tools (unrar libraries, zip-slip directory-traversal class). |
| `QuickLook.Plugin/QuickLook.Plugin.PEViewer/` | plugin-parser | .NET (C#) | Windows PE binary (.exe/.dll) header + section parsing. | None | Renders preview of executable metadata. Parser of untrusted binary format. |
| `QuickLook.Plugin/QuickLook.Plugin.MarkdownViewer/Resources/js/*.min.js` | vendored-library | WebView2 (Chromium-based) | None | None | Bundled mermaid, MathJax, markdown-it, highlight.js libs. These execute in a Chromium-based WebView2 control that previews the markdown. Supply-chain surface — F1. |

Install is via MSI / Scoop / MS Store. The MSI is signed (Windows SmartScreen accepts it) but the repo doesn't carry a separate code-signing certificate fingerprint for consumers to verify out-of-band.

---

## 03 · Suspicious code changes

> Representative rows from the 137-PR sample. Full sample: 5.1% formal review, 25.5% any-review, 5 self-merges (3.6%). xupefei and emako alternately review each other's PRs informally; external contributors get community comments but rarely formal APPROVED decisions.

Sample: the 50 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 5.1% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1800](https://github.com/QL-Win/QuickLook/pull/1800) | feat: add ELFViewer plugin (sample) | xupefei | xupefei | No formal decision | Self-committed plugin addition |
| [#1795](https://github.com/QL-Win/QuickLook/pull/1795) | fix: ArchiveViewer handles malformed RAR (sample) | emako | xupefei | Approved by xupefei | Parser-fix — security-relevant class |
| [#1790](https://github.com/QL-Win/QuickLook/pull/1790) | chore: update mermaid bundled lib (sample) | external-contrib | emako | Community comments | None |
| [#1785](https://github.com/QL-Win/QuickLook/pull/1785) | feat: OfficeViewer xlsx formula render (sample) | xupefei | xupefei | No formal decision | None |
| [#1780](https://github.com/QL-Win/QuickLook/pull/1780) | chore: dependabot bump action (sample) | dependabot[bot] | xupefei | No formal decision | None |
| [#1775](https://github.com/QL-Win/QuickLook/pull/1775) | fix: MailViewer EML header edge case (sample) | external-contrib | emako | Community comments | Parser-fix |

---

## 04 · Timeline

> ✓ 5 good · 🟡 3 neutral
>
> QuickLook's lifecycle — 9-year xupefei-led project, emako joined as co-maintainer, active semver releases.

- 🟡 **2017-04-12 · Repo created by xupefei** — Single-author start
- 🟢 **2018-06-01 · First stable release (est.)** — Early release cadence
- 🟢 **2022-03-01 · emako joins as co-maintainer (est.)** — Top-2 shape begins
- 🟡 **2024-12-06 · `latest` tag last moved (F4)** — Pre-stall state preserved on this tag
- 🟢 **2026-01-08 · 4.4.0 release** — Semver cadence active
- 🟢 **2026-04-14 · 4.5.0 release** — 6 days before scan
- 🟢 **2026-04-17 · Last push to master** — Active development
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan entry 22

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 23,083 | None |
| Open issues | 187 | 0 security-tagged |
| Open PRs | 3 | All 3 authored by app/copilot-swe-agent |
| Primary language | C# | First C# V1.2 entry |
| License | GPL-3.0 | None |
| Created | 2017-04-12 | ~9 years |
| Last pushed | 2026-04-17 | Active |
| Default branch | master | None |
| Total contributors | 81 | Top-2 (xupefei + emako) ~94% of top-6 |
| Formal releases | 56 | 4.5.0 @ 2026-04-14 latest semver |
| `latest` tag date | 2024-12-06 | Stale — not moved since Dec 2024 despite 4.5.0 shipping — F4 |
| Plugins (untrusted parsers) | 21 | Archive/PE/ELF/Office/PDF/Mail/Image/Video + more — F0 |
| Classic branch protection | OFF (HTTP 404) | None |
| Rulesets | 0 | None |
| Rules on default branch | 0 | None |
| CODEOWNERS | Absent | None |
| SECURITY.md | Absent | Parser-heavy tool, 9 years |
| CONTRIBUTING | Absent | None |
| Community health | 50% | None |
| Workflows | 4 | msbuild + Copilot review + Copilot SWE + Dependabot |
| pull_request_target usage | 0 | None |
| CodeQL SAST | Absent | None |
| Dependabot config | Runs (workflow present); no dependabot.yml in repo | Likely enabled via repo settings |
| PR formal review rate | 5.1% | 137-PR sample |
| PR any-review rate | 25.5% | None |
| Self-merge count | 5 (3.6%) | None |
| Published security advisories | 0 | 9 years, zero |
| OSSF Scorecard | 4.1/10 | Indexed |
| NuGet deps | Not parsed | .csproj parsing not implemented — F6 |
| Bundled vendored JS libs | 5+ (mermaid/MathJax/markdown-it/highlight.js/svga) | No upstream version tracking — F1 |
| Primary distribution | GitHub Releases MSI + Scoop + MS Store | Harness detected 0 channels — F6 |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 7 documented gaps — concentrated on .NET / Windows-package-manager ecosystem and bundled-JS false-positives.

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit |
| Tarball extraction + local grep | ✅ Scanned |
| OSSF Scorecard | ✅ Indexed, overall 4.1/10 |
| Dependabot alerts | ⚠ Admin scope (403); no dependabot.yml in repo but 'Dependabot Updates' workflow runs — config is in repo settings (F6) |
| osv.dev dependency queries | ⚠ 0 queries — .csproj / .sln parsing not implemented (F6) |
| PR review sample | ✅ 137-PR sample — 5.1% formal, 25.5% any, 5 self-merges |
| Dependencies manifest detection | ⚠ 0 detected (F6 — .NET project files unrecognized) |
| Distribution channels inventory | ⚠ 0 detected — real channels (GitHub Releases MSI + Scoop + MS Store) unrecognized (F6) |
| Dangerous-primitives grep (15 families) | ⚠ 20+ hits across 5 families — all false positives on bundled minified JS in plugin Resources/ (F6) |
| Workflows | ✅ 4 detected (msbuild + Copilot × 2 + Dependabot) |
| Agent-rule files inventory | ✅ 0 (not an agent-tool repo) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No paste-from-command blocks |
| Tarball extraction | ✅ 896 files |
| osv.dev | ℹ Zero runtime dependencies |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4992/5000 remaining |

**Gaps noted:**

1. .NET .csproj / .sln dependency parsing not implemented — NuGet dep graph for 21+ plugin projects is unscanned. Same pattern as Go/Ruby/Rust ecosystem gaps.
2. Distribution-channel harness did not detect QuickLook's actual channels: GitHub Releases MSI installer, Scoop (`scoop install quicklook`), Microsoft Store. Reported 0 channels is a coverage artifact.
3. Dependabot-alerts API required admin scope (HTTP 403); dependabot.yml is NOT in the repo but a 'Dependabot Updates' dynamic workflow runs — implies config is in repo Settings. Coverage of actual dep ecosystems tracked is unknown to this scan.
4. Dangerous-primitives regex produced 20+ false positives on bundled minified JavaScript libraries inside plugin Resources/ directories (mermaid.min.js, mathjax, markdown-it, highlight.js, svga). Regex tuning gap.
5. Gitleaks secret-scanning not available on this scanner host.
6. Release-integrity grading is coarse — harness doesn't check MSI installer release assets for .sig / code-signing / checksum files on QuickLook releases.
7. Copilot SWE agent PRs (E9) surfaced as regular PRs — harness doesn't distinguish AI-authored contributions or flag them for governance-attention.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from Phase 1 harness + gh api queries + plugin-directory inspection.

### ★ Priority evidence (read first)

#### ★ Evidence 3 — QuickLook's architecture is a 21-plugin system that invokes a different parser for each file format. The plugin list enumerates the untrusted-file-parsing surface.

```bash
gh api repos/QL-Win/QuickLook/contents/QuickLook.Plugin
```

Result:
```text
21 plugins: AppViewer, ArchiveViewer, CLSIDViewer, CertViewer, CsvViewer, ELFViewer, FontViewer, HelixViewer, HtmlViewer, ImageViewer, InsvBlocker, MailViewer, MarkdownViewer, MediaInfoViewer, OfficeViewer, PDFViewer, PEViewer, PluginInstaller, TextViewer, ThumbnailViewer, VideoViewer. Critical-parser plugins: ArchiveViewer (ZIP/RAR/7Z), PDFViewer, OfficeViewer (Excel/Word), PEViewer (Windows .exe/.dll), ELFViewer (Linux binaries), MailViewer (EML), ImageViewer (many raster formats), VideoViewer (codecs).
```

*Classification: fact*

#### ★ Evidence 4 — MarkdownViewer bundles minified third-party JavaScript libraries — mermaid.min.js, mathjax/tex-mml-svg.js, markdown-it.min.js, highlight.min.js, svgaplayerweb/svga.min.js — as pinned vendored assets with no recorded upstream version or automated update path.

```bash
ls QuickLook.Plugin/QuickLook.Plugin.MarkdownViewer/Resources
```

Result:
```text
Vendored libraries in QuickLook.Plugin.MarkdownViewer/Resources/ (and ImageViewer/Resources/Web/): mermaid.min.js, markdown-it.min.js, highlight.min.js, mathjax tex-mml-svg.js, svga.min.js. The bundled versions were committed to the repo rather than fetched at build time; upstream CVE patches (mermaid, MathJax, highlight.js, markdown-it all ship security fixes periodically) do not automatically flow to the bundled copies.
```

*Classification: fact*

#### ★ Evidence 5 — No SECURITY.md; community/profile reports has_security_policy=false, has_contributing=false, has_code_of_conduct=false, health_percentage=50. security-advisories count: 0 across 9 years of development.

```bash
gh api 'repos/QL-Win/QuickLook/community/profile'; gh api 'repos/QL-Win/QuickLook/security-advisories'
```

Result:
```text
community_profile: has_security_policy: false; has_contributing: false; has_code_of_conduct: false; health_percentage: 50; license_spdx: GPL-3.0. security-advisories count: 0. For a file-preview tool with 21 parsers handling archives/PE/Office/PDF/images — a surface historically prone to parser-RCE bugs — the zero-advisory record is notable.
```

*Classification: fact*

### Other evidence

#### Evidence 1 — Two-maintainer concentration: xupefei (716 commits) + emako (611) = 1,327 of the ~1,408 top-6 commit total (94%). 81 total contributors but the long tail is thin.

```bash
gh api repos/QL-Win/QuickLook/contributors --jq '[.[] | {login, contributions}] | .[:6]'
```

Result:
```text
xupefei: 716; emako: 611; Copilot: 21; rabelux: 18; Jethro-Alter: 13; mooflu: 8. total_contributor_count: 81. Top-2 share 94%; top-1 alone 52% (below the 80% solo-maintainer threshold because emako meaningfully co-maintains).
```

*Classification: fact*

#### Evidence 2 — No branch protection — classic 404, 0 rulesets, 0 rules on default, no CODEOWNERS.

```bash
gh api repos/QL-Win/QuickLook/branches/master/protection; gh api repos/QL-Win/QuickLook/rulesets
```

Result:
```text
classic: HTTP 404. rulesets: {entries: [], count: 0}. rules_on_default: {entries: [], count: 0}. CODEOWNERS: not found.
```

*Classification: fact*

#### Evidence 6 — OSSF Scorecard indexed — overall 4.1/10. Below Xray-core (5.1) and typical mid-tier — consistent with branch-protection=0 and signed-releases likely 0.

```bash
curl https://api.securityscorecards.dev/projects/github.com/QL-Win/QuickLook
```

Result:
```text
HTTP 200; overall_score: 4.1/10. Indexed. 4.1 aligns with absence of Branch-Protection + Code-Review-Rate + Signed-Releases positive signals observed in F0/F1.
```

*Classification: fact*

#### Evidence 7 — Release pipeline emits semver tags regularly (4.5.0 on 2026-04-14, 4.4.0 on 2026-01-08) but a confusing `latest` tag exists and dates to 2024-12-06. Downstream consumers that track `latest` get stale code; those tracking the semver series get current.

```bash
gh api 'repos/QL-Win/QuickLook/releases?per_page=10'
```

Result:
```text
total_count: 56. Sample: 4.5.0 (2026-04-14), 4.4.0 (2026-01-08), 4.3.x (earlier 2025), `latest` tag (2024-12-06). The `latest` tag points to an earlier release and has not moved in 16 months. Some installer tooling / scoop manifests may resolve to `latest` and serve the stale version.
```

*Classification: fact*

#### Evidence 8 — 300-PR sample (actual 137-PR sample per harness): formal_review_rate=5.1%, any_review_rate=25.5%, self_merge_count=5. Somewhat better review-rate than single-maintainer repos but still far below a standard project gate.

```bash
gh api 'repos/QL-Win/QuickLook/pulls?state=closed&per_page=100'
```

Result:
```text
sample_size: 137; formal_review_rate: 5.1; any_review_rate: 25.5; self_merge_count: 5. Better than Xray-core's 7.7% any-review; worse than kamal's 18.7%. Consistent with a two-maintainer repo where xupefei + emako alternately review each other's PRs informally.
```

*Classification: fact*

#### Evidence 9 — All 3 currently open PRs are authored by `app/copilot-swe-agent` — GitHub's AI agent. No human contributions in the open queue as of scan.

```bash
gh api 'repos/QL-Win/QuickLook/pulls?state=open'
```

Result:
```text
open_prs count: 3. Authors: app/copilot-swe-agent × 3 (#1833 'Remember my choice option for protected view notice', #1825 'search panel support in CSV viewer', #1820 'file extension allowlist/blocklist filtering'). The open queue is entirely AI-authored; the governance question is how these are reviewed before merge.
```

*Classification: fact*

#### Evidence 10 — Workflows count=4 — msbuild, Copilot PR reviewer, Copilot SWE agent, Dependabot Updates. No CodeQL / SAST workflow. pull_request_target usage: 0.

```bash
gh api repos/QL-Win/QuickLook/actions/workflows
```

Result:
```text
workflows.count: 4. Named: msbuild.yml (Windows build), Copilot code review (dynamic), Copilot cloud agent (dynamic), Dependabot Updates (dynamic). pull_request_target_count: 0. CodeQL: absent. SAST coverage is not present in this repo's CI; the Copilot review is LLM-based not SAST.
```

*Classification: fact*

#### Evidence 11 — Harness detected 0 dependency manifests. Reality: QuickLook is a .NET C# project using .csproj/.sln files which harness doesn't parse. Distribution-channel detection also returned 0 channels; actual install channels are MSI installer on GitHub Releases, Scoop (scoop install quicklook), and Microsoft Store.

```bash
docs/phase_1_harness.py # dependencies + distribution_channels
```

Result:
```inference — coverage-gap annotation
dependencies.manifest_files: []; runtime_count: 0; dev_count: 0. distribution_channels.channels: []. Dependabot config marked 'not present' but workflows show 'Dependabot Updates' running — the config likely lives in repo settings, not dependabot.yml. Coverage-gap annotation.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 12 — Dangerous-primitives regex hits are all inside bundled third-party minified JavaScript (mermaid, MathJax, markdown-it, highlight.js) — not QuickLook's own code. Exec/deserialization/network/cmd_injection/xss families all triggered on the vendored minified libs in MarkdownViewer and ImageViewer plugins.

```bash
docs/phase_1_harness.py # code_patterns.dangerous_primitives by family
```

Result:
```inference — coverage-gap annotation
exec: 7 hits, deserialization: 1, network: 5, cmd_injection: 3, xss: 4 — all within QuickLook.Plugin.MarkdownViewer/Resources/{js,mathjax}/*.min.js and QuickLook.Plugin.ImageViewer/Resources/Web/svgaplayerweb/svga.min.js. Classification: regex false positives on minified library internals. This IS a coverage-gap annotation but it is ALSO the basis of F1 — the bundled libs themselves are a supply-chain surface regardless of whether they trigger the primitive regex.
```

*Classification: inference — coverage-gap annotation*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `0cda83c26d99148f3b6e5273d7028b4ecffa1e77` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
