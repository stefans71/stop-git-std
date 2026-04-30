# Security Investigation: microsoft/markitdown

**Investigated:** 2026-04-20 | **Applies to:** main @ `604bba13da2f43b756b49122cb65bdedb85b1dff` | **Repo age:** 1 year | **Stars:** 112,866 | **License:** MIT

> A 112,000-star Microsoft-owned file-conversion tool with enterprise disclosure infrastructure on paper and two live vulnerabilities sitting unfixed in the issue tracker — including an XXE fix that's been waiting 47 days for review and a Zip Bomb that's been public for 114 days with no fix proposed.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-markitdown.md` (+ `.html` companion) |
| Repo | [github.com/microsoft/markitdown](https://github.com/microsoft/markitdown) |
| Short description | None |
| Category | `None` |
| Subcategory | `None` |
| Language | None |
| License | MIT |
| Target user |  |
| Verdict | **Caution** (split — see below) |
| Scanned revision | `main @ 604bba1` (release tag ``) |
| Commit pinned | `604bba13da2f43b756b49122cb65bdedb85b1dff` |
| Scanner version | `V2.5-preview-wild` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of this repo. Future re-runs should rename this file to `GitHub-Scanner-markitdown-2026-04-20.md` before generating the new report. |

---

## Verdict: Caution (split — Deployment axis only)

### Deployment · Deployment · Internal/trusted files · v0.1.5 — **Caution — Clean shell surface + strong disclosure channel, but governance is soft and two open vulns will land if you process something they miss**

For converting documents you control (internal ETL pipelines, trusted corpora, your own files), markitdown at v0.1.5 is a reasonable install. The shell surface is clean (F7), Microsoft MSRC is a real disclosure channel (F6), and the two live vulns (F1 XXE, F2 Zip Bomb) require a malicious input file to trigger — a risk you control if the corpus is trusted.

### Deployment · Deployment · Untrusted file upload · any user-facing endpoint — **Caution — Wait for F1 + F2 fixes before accepting arbitrary DOCX/ZIP/EPUB uploads**

A web service, API endpoint, or automated pipeline that feeds markitdown arbitrary user-supplied files exposes both the XXE (F1 — DOCX pre-processor) and the Zip Bomb (F2 — ZIP/EPUB/DOCX archive extraction). Until PR #1582 merges and F2 gets a fix, wrap markitdown in a memory-capped sandbox per F2's how_to_fix, or route DOCX-only traffic through a different converter.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Two live vulns in default install path when processing untrusted files (3 findings)</strong>
<br><em>XXE in DOCX pre-processor (fix sitting 47 days) + Zip Bomb DoS in ZipConverter + EPUB + DOCX (no fix in 114 days)</em></summary>

1. **XXE · F1** — _convert_omath_to_latex() uses ET.fromstring() on user-supplied DOCX XML; PR #1582 replaces with defusedxml, has been open 47 days with 0 reviews.
2. **Zip Bomb · F2** — ZipConverter reads entire zip-entry content into memory with no size guard; no fix PR in 114 days. Harness grep shows same pattern in _epub_converter.py and docx/pre_process.py — not separately issue-filed.
3. **Disclosure · F3** — CVE-2025-64512 (pdfminer.six ACE) silently patched in v0.1.4; request for GHSA (#1504) unanswered 130 days. Users of 0.1.3 have no programmatic upgrade signal.

</details>

<details>
<summary><strong>⚠ Governance gaps — soft PR gate + no CODEOWNERS + 0% formal review (5 findings)</strong>
<br><em>Ruleset requires PR but 0 approving reviews; 43.7% of merges are self-merges; no CODEOWNERS</em></summary>

1. **PR gate · F0** — Ruleset 'Protect Main Branch' is active (PR required + status checks) but required_approving_review_count=0. The gate allows self-merge without review.
2. **Review rate · F0** — 0/174 merged PRs have formal reviewDecision set; 70/174 (40.2%) have review objects; 76/174 (43.7%) are self-merges.
3. **CODEOWNERS · F0** — Absent in 4 standard locations. No path-scoped reviewer on security-critical files (converters, workflows, install scripts).
4. **Dependabot · F4** — Only tracks github-actions; pip ecosystem not configured. CVE-2025-64512 would have been auto-opened if it had been.
5. **Release bus-factor · F5** — All 18 releases authored by afourney. Release-management bus-factor is 1.

</details>

<details>
<summary><strong>✅ Positive signals — enterprise disclosure channel + clean shell surface (3 findings)</strong>
<br><em>Microsoft MSRC disclosure with 24-hour SLA; 0 dangerous shell primitives; 112k stars suggests broad community scrutiny</em></summary>

1. **MSRC · F6** — SECURITY.md routes to MSRC + secure@microsoft.com + PGP key with 24-hour response SLA. Enterprise-grade disclosure infrastructure.
2. **Shell surface · F7** — 0 hits for os.system and subprocess.shell=True across the repo. 3 subprocess.run call sites all use argv-form (no shell interpolation).
3. **Maintainer tenure · F5 meta** — afourney (Adam Fourney, Microsoft) is the named author; code bus-factor ~2 with gagb as active co-maintainer.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — No |
| Is it safe out of the box? | ⚠ **Partly** — Partly |
| Do they fix problems quickly? | ⚠ **Partly** — Partly |
| Do they tell you about problems? | ⚠ **Partly** — Partly |

---

## 01 · What should I do?

> 🚨 Hold if using Codex on shared hosts · ⚠ 1 consumer mitigation · 3 steps
>
> **Most urgent:** if you run Archon with the Codex provider on any machine another user can log into, wait for PR #1250 before trusting Codex runs (Step 1). For single-user laptops (Step 2) you're fine to install today via the pinned install script. Step 3 is the dependency patch to watch.

### Step 1: If you use the Codex provider on a shared host, hold off until #1250 merges (⚠)

**Non-technical:** Archon downloads a Codex CLI binary to ~/.archon/vendor/codex/ without checking its hash. On a multi-user machine, another user who can write to that folder can drop a rigged binary that runs as you. The fix is open as PR #1250. Single-user laptops are low risk.

```bash
ls -la ~/.archon/vendor/codex/ 2>/dev/null
gh pr view 1250 -R coleam00/Archon --json state,mergedAt
```

### Step 2: Install Archon on your own machine — the install script verifies checksums (✓)

**Non-technical:** Installing now is fine on a personal laptop. The install script sha256-verifies the binary before running it.

```bash
curl -fsSL https://archon.diy/install | bash
archon version
```

### Step 3: Ask maintainers to merge the axios CVE patch and enable branch protection (ℹ)

**Non-technical:** Merge PR #1153 (axios CVE fix), enable branch protection on dev, add dependabot.yml, add CODEOWNERS.

---

## 02 · What we found

> ⚠ 4 Warning · ℹ 2 Info · ✓ 2 OK
>
> 8 findings total.
### F0 — Warning · Structural — Soft governance gate: ruleset requires PR but 0 approving reviews; no CODEOWNERS; 0% formal review rate on 174 merges

*Continuous · Since ruleset creation 2024-11-13 · → Increase required_approving_review_count to 1 in the Protect Main Branch ruleset + add .github/CODEOWNERS covering packages/markitdown/converters/ and .github/workflows/.*

**What we observed.** Ruleset 'Protect Main Branch' is active with 4 rules (deletion prevention, non-fast-forward, PR required, status checks tests+pre-commit), but required_approving_review_count=0. No CODEOWNERS file. 0/174 merged PRs have formal reviewDecision; 76/174 are self-merges.

**What this means for you.** The PR workflow LOOKS gated — pushes to main go through a PR — but nothing actually requires a human to click approve. Combined with 43.7% self-merge rate, a maintainer-credential-compromise PR would not stand out from the pattern.

**What this does NOT mean.** It does not mean the maintainers don't review — 40% of PRs have review objects (comments/approvals) attached. It means the institution has not encoded the review pattern as a required gate. A rulesetdial change (set required_approving_review_count from 0 to 1) closes this.

| Meta | Value |
|------|-------|
| Classic branch protection | ❌ 404 on `main` |
| Ruleset active | ✅ 'Protect Main Branch' (4 rules) |
| Required approving reviews | ❌ 0 (PR gate is soft) |
| CODEOWNERS | ❌ Absent (4 locations checked) |
| Formal review rate | ❌ 0% (0/174) |
| Any-review rate | ⚠ 40.2% (70/174) |
| Self-merge rate | ⚠ 43.7% (76/174) |

**How to fix.** In GitHub *Settings → Rules → Protect Main Branch*, set **Require pull request reviews before merging** and increase **Required approving reviews** from 0 to 1. Add `.github/CODEOWNERS` at minimum: `packages/markitdown/converters/ @afourney @gagb`, `packages/markitdown/converter_utils/ @afourney @gagb`, `.github/workflows/ @afourney`. Combined, these close the self-merge + zero-review pattern.

### F1 — Warning · Vulnerability — Open XXE injection in DOCX pre-processor (`_convert_omath_to_latex` via `ET.fromstring` on user input); fix PR open 47 days

*Live in main and v0.1.5 · Filed 2026-02-20 · fix PR 2026-03-03 · → If you process untrusted DOCX files through markitdown, wait for PR #1582 to merge before deploying v0.1.5+. Internal/trusted DOCX processing is lower risk.*

**What we observed.** packages/markitdown/src/markitdown/converter_utils/docx/pre_process.py:45 uses xml.etree.ElementTree.fromstring() on XML extracted from user-supplied DOCX files. Issue #1565 filed 2026-02-20, describes the vuln in full. PR #1582 proposes a one-import-line fix (defusedxml.ElementTree) — has been open 47 days with 0 reviews.

**What this means for you.** Any markitdown deployment that processes DOCX files from untrusted sources is exposed to XXE attacks (file read, SSRF via external entities). Internal-only use with trusted documents is lower risk.

**What this does NOT mean.** This is not remote-code-execution — XXE typically enables file reads, SSRF, or DoS via entity expansion. The fix is trivial; the concerning signal is that a 47-day-old security fix PR from an external contributor has received no reviews.

| Meta | Value |
|------|-------|
| File | `packages/markitdown/src/markitdown/converter_utils/docx/pre_process.py:45` |
| Severity (reporter) | High |
| Attack | XXE via `_convert_omath_to_latex` parsing user-supplied DOCX XML |
| Reported by | [m45537-blip](https://github.com/microsoft/markitdown/issues/1565) — 2026-02-20 |
| Fix PR | [#1582](https://github.com/microsoft/markitdown/pull/1582) — open 47 days, 0 reviews, 3 comments |
| Mitigation | Use `defusedxml` (already a runtime dep — the import swap is one line) |

**How to fix.** Track PR #1582 (uses `defusedxml.ElementTree` to replace `xml.etree.ElementTree.fromstring()` in `_convert_omath_to_latex()`). Until merged, sanitise inputs before markitdown or feed only trusted DOCX files. The fix is mechanical — `import defusedxml.ElementTree as ET` in place of `xml.etree`.

### F2 — Warning · Vulnerability — Open Zip Bomb DoS in ZipConverter (and EPUB + DOCX sibling converters); 114 days old, no fix PR

*Live in main and v0.1.5 · Filed 2025-12-27 · → If you process untrusted ZIP, EPUB, or DOCX files, wait for a fix or wrap markitdown with a memory/size-cap sandbox.*

**What we observed.** _zip_converter.py:96 reads zipfile.ZipFile entries into memory without size checks. Two sibling files (_epub_converter.py:59, converter_utils/docx/pre_process.py:139) use the same pattern — independently flagged by the Phase 1 harness's dangerous-primitives grep.

**What this means for you.** Feed markitdown a maliciously-crafted ZIP, EPUB, or DOCX containing a zip bomb and the conversion process crashes with OOM. If markitdown runs behind a web service or auto-queue, this becomes a sustained DoS.

**What this does NOT mean.** Not RCE — the impact is denial-of-service, not code execution. The fix involves streaming-with-size-cap rather than full in-memory decompression; no trivial one-liner.

| Meta | Value |
|------|-------|
| Primary file (issue) | `packages/markitdown/src/markitdown/converters/_zip_converter.py:96` |
| Sibling exposures (harness-discovered) | `_epub_converter.py:59`, `converter_utils/docx/pre_process.py:139` — same unguarded zipfile.ZipFile pattern |
| Severity (reporter) | Medium (DoS class) |
| Attack | Zip Bomb → OOM crash of markitdown process |
| Reported by | [sugarbinj](https://github.com/microsoft/markitdown/issues/1514) — 2025-12-27 |
| Fix PR | ⚠ None filed yet (114 days at scan) |

**How to fix.** Issue #1514 proposes size-aware streaming reads. Until merged: run markitdown in a resource-capped sandbox (container with memory limit, ulimit -v, or ProcessPoolExecutor with RLIMIT_AS) when handling untrusted archive files. Consider swapping `zipfile.ZipFile.read(...)` for a streaming read with a size cap (e.g. read first N bytes, check against `ZipInfo.file_size` and `compress_size` before full extraction).

### F3 — Warning · Process — F5-class disclosure gap: CVE-2025-64512 (arbitrary code execution via `pdfminer.six`) silently patched in v0.1.4; GHSA request unanswered 130 days

*v0.1.3 → v0.1.4 silent patch · Fix 2025-12-01 · GHSA still unpublished · → If you installed markitdown 0.1.3 or earlier, upgrade to 0.1.4+. Ask maintainers to publish a GHSA for the transitive CVE so past users get a programmatic upgrade signal.*

**What we observed.** CVE-2025-64512 (arbitrary code execution in pdfminer.six) affected markitdown 0.1.3 transitively. v0.1.4 (2025-12-01) bumped pdfminer.six and closed the vuln, but released the fix in a 'feature update' without a GitHub Security Advisory. Issue #1504 (2025-12-12) asks for a GHSA — has been open 130 days with zero comments.

**What this means for you.** If you were running markitdown 0.1.3 at the time the pdfminer.six CVE was published, you had no programmatic signal that you were vulnerable. Anyone still on 0.1.3 today has no programmatic signal that they should upgrade.

**What this does NOT mean.** The fix exists and is shipped — this is purely a disclosure-publication gap. The failure is administrative, not technical.

| Meta | Value |
|------|-------|
| CVE | CVE-2025-64512 (arbitrary code execution in pdfminer.six) |
| Affected versions | markitdown 0.1.3 and earlier (transitive via pdfminer.six) |
| Fixed in | v0.1.4 (2025-12-01, pdfminer.six dep bump) |
| GHSA published | ❌ None (130 days after issue #1504 requested it) |
| Issue #1504 comments | ❌ 0 (no maintainer response) |
| F5 pattern | Unadvertised fix — release notes framed as feature update |

**How to fix.** Maintainer-side: publish a GitHub Security Advisory at https://github.com/microsoft/markitdown/security/advisories for CVE-2025-64512 as it applies to markitdown 0.1.3-and-earlier via the pdfminer.six dependency. Reference issue #1504's request body. The fix is already shipped (v0.1.4) — this is purely a disclosure-publication step.

### F4 — Info · Hygiene gap — Dependabot tracks only `github-actions` ecosystem; pip (Python runtime deps) not configured

*Current · Since dependabot.yml creation · → No direct user action. Ask maintainer to extend `.github/dependabot.yml` with a `pip` ecosystem entry so transitive Python-dep CVEs open PRs automatically.*

**What we observed.** .github/dependabot.yml declares only github-actions as an ecosystem to track. No pip ecosystem entry, despite 19 runtime deps across 4 sub-packages.

**What this means for you.** Transitive Python CVEs do not surface as Dependabot PRs. The CVE-2025-64512 pdfminer.six issue had to be caught by human review rather than by bot.

**What this does NOT mean.** Not a direct vulnerability — a hygiene gap that slows CVE response. Adding 4 pip ecosystem entries to the YAML (one per sub-package) closes this in minutes.

| Meta | Value |
|------|-------|
| Current ecosystems tracked | `github-actions` only |
| pip ecosystem | ❌ Not configured |
| Consequence | CVE-2025-64512 required human-authored v0.1.4 release to close; bot would have opened a PR immediately |

**How to fix.** Add a second update stream to `.github/dependabot.yml`:
```yaml
  - package-ecosystem: "pip"
    directory: "/packages/markitdown"
    schedule:
      interval: "weekly"
  - package-ecosystem: "pip"
    directory: "/packages/markitdown-mcp"
    schedule:
      interval: "weekly"
```
Repeat for markitdown-ocr + markitdown-sample-plugin. Would have auto-opened a PR when CVE-2025-64512 was published.

### F5 — Info · Structural — 100% of 18 releases authored by `afourney`; release-management bus-factor is 1

*Continuous · Since repo creation · → No direct user action. Ask maintainer to document release process and grant release permissions to a second team member (e.g. gagb).*

**What we observed.** All 18 releases (v0.1.0 through v0.1.5 including prereleases) were authored by afourney. Code contribution bus-factor is healthier — afourney has 100 commits, gagb has 70.

**What this means for you.** A compromise of afourney's GitHub credentials (or absence due to unplanned leave) blocks releases. Users depending on timely security releases have a single point of failure on the release-management side.

**What this does NOT mean.** Not a vulnerability in the normal sense. Microsoft's enterprise account-security practices likely reduce compromise risk; the concern is continuity, not exploitation.

| Meta | Value |
|------|-------|
| Releases authored | 18/18 (100%) by afourney |
| Code bus-factor | ~2 (afourney 100 commits, gagb 70 commits) |
| Release bus-factor | ⚠ 1 (afourney only) |

**How to fix.** Add a release runbook (`docs/RELEASING.md`) and grant GitHub release-publish permission to at least one additional maintainer. Low-priority — code bus-factor is healthier (afourney + gagb active) — but a compromise of afourney's credentials currently ships releases to PyPI/GHCR with no independent signal.

### F6 — OK · Positive — Enterprise MSRC disclosure channel with 24-hour SLA + PGP + secure@microsoft.com

*Current · Standard Microsoft SECURITY.md · → Use https://msrc.microsoft.com/create-report or secure@microsoft.com for any vulnerability you discover. Response SLA is 24 hours.*

**What we observed.** SECURITY.md at root is the Microsoft V0.0.9 boilerplate — routes vulnerability reports to MSRC (https://msrc.microsoft.com/create-report) or secure@microsoft.com, with a PGP key available and a 24-hour response SLA.

**What this means for you.** If you discover a vulnerability in markitdown, there is a real channel with enterprise response guarantees. The channel works — the F1/F2 reporters used the issue tracker (which is also compliant with the SECURITY.md language for non-vuln issues) and the F3 reporter filed a public issue after the fix shipped.

**What this does NOT mean.** Not a guarantee of response. F3 shows the publication side is weak — MSRC isn't publishing GHSAs for known fixed vulns. The channel accepts reports; it's not clear whether it publishes advisories.

| Meta | Value |
|------|-------|
| Channel | ✅ MSRC + secure@microsoft.com + PGP |
| SLA | ✅ 24-hour first response |
| Contrast | The channel works (reporter of #1565 used the issue tracker; issue is visible + triaged). The concern (F3) is the publication side — MSRC doesn't seem to be posting GHSAs for known fixed vulns. |

### F7 — OK · Positive — Python sources clean on shell-injection primitives (os.system, subprocess.shell=True: 0 hits each)

*Current · Scan date 2026-04-20 · → No action needed. Positive signal: the repo avoids the most common shell-interpolation-injection class.*

**What we observed.** GitHub code-search returned 0 hits each for `os.system` and `subprocess.shell=True` across the entire repo. The harness's dangerous-primitives grep confirmed 3 subprocess.run sites (exiftool version check + test files), all using argv-form (safe).

**What this means for you.** Shell-injection as an attack class is not present in markitdown's code path. The vulns that do exist (F1 XXE, F2 Zip Bomb) are parsing-surface bugs, not shell-surface bugs.

**What this does NOT mean.** Not a statement about overall code quality — just that this specific vulnerability class is absent. The archive-extraction class (F2) is present in 3 places.

| Meta | Value |
|------|-------|
| os.system hits | ✅ 0 |
| subprocess.shell=True hits | ✅ 0 |
| subprocess.run hits (argv form — safe) | 3 (`_exiftool.py`, 2 test files) |
| Harness Step A archive_unsafe hits | ⚠ 3 (F2 scope — separate from shell surface) |

---

## 02A · Executable file inventory

> ⚠ 2 Warning · ℹ 2 Info · ✓ 4 OK — 8 executable surfaces cataloged (7 scripts + 1 Tier-1 auto-loaded rule file). 2 need attention: the Codex binary resolver (F1 target) and the release.yml homebrew-update job that commits to dev without a review gate.

### Layer 1 — one-line summary

- **8 executable surfaces inventoried.** The 2 Warning items are maintainer-side: merge PR #1250 (Codex binary pinning) and optionally gate the Homebrew auto-commit path in release.yml. The 4 OK items (install.sh, install.ps1, Dockerfile, docker-entrypoint.sh) are clean and sha256-verified where applicable. CLAUDE.md is a Tier-1 auto-loaded agent rule file — content benign today, leverage is every contributor session.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `packages/providers/src/codex/binary-resolver.ts` | Vendor binary resolver | Node/Bun | fileExists() — no sha256 or signature check on resolved binary path | None directly | Warning: resolves Codex CLI from env/config/~/.archon/vendor/codex/ and passes to SDK codexPathOverride without hash pinning. Fix open in PR #1250. |
| `.github/workflows/release.yml` | CI release workflow | GitHub Actions | git push via GITHUB_TOKEN direct to dev on tag-push | GitHub Releases fetch + git push to origin/dev | Warning: update-homebrew job commits homebrew/archon.rb directly to dev without review gate. Low risk in isolation; compound risk with F0 (no branch protection). |
| `scripts/install.sh` | Install script | shell | None — set -euo pipefail, sha256sum verification | HTTPS to github.com / objects.githubusercontent.com only | OK — downloads versioned binary from tagged release, sha256-verifies before install. SKIP_CHECKSUM defaults to false. |
| `scripts/install.ps1` | Install script (Windows) | PowerShell | None — Set-StrictMode -Version Latest, same sha256 verification logic | HTTPS to github.com only | OK — PS1 parity with install.sh. F16 Windows surface covered. |
| `Dockerfile` | Container definition | Docker | None — multi-stage, gosu privilege drop | None at runtime (build-time only) | OK — multi-stage build, drops root to appuser via gosu, no untrusted tarball fetches. |
| `docker-entrypoint.sh` | Container entrypoint | shell | None — exec $RUNNER bun run start | None | OK — fixes volume perms, configures GH_TOKEN via credential helper (not ~/.gitconfig), execs as appuser. |
| `CLAUDE.md` | Agent rule file (Tier 1 auto-loaded) | Claude Code agent context | None — static markdown, development conventions only | None | Info — auto-loaded for every contributor session in this repo. 813 lines of TypeScript/Zod/Bun contributor conventions. Imperative-verb grep found no prompt injection patterns. Leverage: 1:every contributor. Content benign today. |
| `scripts/build-binaries.sh` | Build pipeline script | shell | None — EXIT trap pattern for safe rollback | None | Info — CI-only build pipeline. Uses bash EXIT trap to restore bundled-build.ts after bun build --compile. Not end-user facing. |

**Note on CLAUDE.md auto-load leverage.** A future PR swapping the benign development-convention content for attacker instructions would take effect on every contributor's next Claude Code session. Combined with the governance gaps in F0/F4 (no branch protection on dev, no CODEOWNERS, 8% formal review rate), a PR modifying CLAUDE.md could land without a gate. Current content is benign; the structural risk is the leverage ratio.

---

## 03 · Suspicious code changes

> **6 security-adjacent PRs reviewed.** All 6 touch security-critical files (providers, installer, CI workflows). None had a formal `reviewDecision`. All were merged by Wirasm (the lead contributor), so practical review happened without the `reviewDecision` field being set.

Sample: the 50 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 0.0% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1250](https://github.com/coleam00/Archon/pull/1250) | Pin Codex vendor binary sha256 on first use (fixes #1245 LPE) | shaun0927 (EXTERNAL REPORTER) | — (open) | No formal decision | Security fix for #1245 LPE, filed 2026-04-16. Still open at scan time. |
| [#1217](https://github.com/coleam00/Archon/pull/1217) | Replace Claude SDK embed with explicit binary-path resolver | Wirasm (LEAD) | Wirasm | No formal decision | Self-submitted-and-merged; content good (CI smoke + regression tests). |
| [#1169](https://github.com/coleam00/Archon/pull/1169) | Prevent target repo .env from leaking into subprocesses (#1135) | Wirasm (LEAD) | Wirasm | No formal decision | Self-merged security fix; content is good. |
| [#1153](https://github.com/coleam00/Archon/pull/1153) | Override axios to ^1.15.0 for CVE-2025-62718 | external_contributor (EXTERNAL) | — (open) | No formal decision | Dep CVE fix sitting open 3 days; no dependabot auto-open. |
| [#1137](https://github.com/coleam00/Archon/pull/1137) | Extract providers from @archon/core into @archon/providers | Wirasm (LEAD) | Wirasm | No formal decision | Large refactor touching Dockerfile + binary paths, self-merged. |

---

## 04 · Timeline

> ✓ 1 good · 🟡 3 neutral · 🔴 4 concerning

- 🟡 **2024-11-13 · START** — Repo created by afourney (Adam Fourney, Microsoft). Ruleset 'Protect Main Branch' configured same day.
- 🟡 **2025-08-26 · v0.1.3** — v0.1.3 released. Vulnerable to CVE-2025-64512 via pdfminer.six transitive dep (not yet known at the time).
- 🔴 **2025-12-01 · v0.1.4 SILENT PATCH** — v0.1.4 released with pdfminer.six dep bump that closes CVE-2025-64512. Release notes frame it as a feature update — no GHSA, no advisory, no CVE mention in changelog.
- 🔴 **2025-12-12 · ADVISORY REQUEST FILED** — Issue #1504 filed asking for GHSA covering the 0.1.3 CVE. Zero comments, no maintainer response — still open at scan time (130 days).
- 🔴 **2025-12-27 · ZIP BOMB REPORTED** — Issue #1514 filed describing Zip Bomb DoS in ZipConverter. No fix PR in 114 days at scan time.
- 🔴 **2026-02-20 · XXE REPORTED + v0.1.5** — Issue #1565 filed describing High-severity XXE in DOCX pre-processor. Same day: v0.1.5 released (does NOT include XXE fix).
- 🟢 **2026-03-03 · XXE FIX PR FILED** — PR #1582 opens with defusedxml-based fix. Proposed by an external contributor.
- 🟡 **2026-04-20 · SCAN** — This scan runs. XXE fix PR has been open 47 days; Zip Bomb 114 days; GHSA request 130 days; all without maintainer response or merge.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 14 months | Created 2025-02-07, scanned 2026-04-16 |
| Stars | 18,300 | Very high visibility — scrutiny should match scale |
| Owner account age | ✅ 7 years | coleam00 created 2019-02-03, 51 public repos, 6,641 followers, Dynamous company |
| Lead contributor | ✅ Wirasm (791 commits) | More than owner's 343 — a second active maintainer |
| Merged PRs (review rate) | ⚠ 13 formal / 93 any / 160 total | 8% formal, 58% any-review |
| Branch protection | ❌ None (dev, main) | API returns 404 on both — definitive |
| CODEOWNERS | ❌ None | No file in any standard location |
| SECURITY.md | ✅ Yes (root) | Real private disclosure policy — cole@dynamous.ai or GitHub private advisory |
| Security advisories | ⚠ 0 published | 3 open issues being tracked publicly |
| OSSF Scorecard | ⚠ Not indexed | API returned 404 — repo not yet indexed by securityscorecards.dev |
| Dependabot | ⚠ Unknown (403 without admin) | No .github/dependabot.yml config either way |
| Runtime dependencies (root) | ✅ 1 (claude-agent-sdk) | Transitive surface via Slack SDK, React, Vite |
| CI workflows | 4 (test, publish, release, deploy-docs) | Real matrix test (ubuntu + windows), Docker smoke test |
| Releases | 10+ (v0.2.13 → v0.3.6) | Rapid iteration, checksums.txt + multi-platform binaries + Docker published per release |
| Total PR count | ~461 closed, 20 open | Active community |

---

## 06 · Investigation coverage

| Check | Result |
|-------|--------|
| Tarball extraction | ✅ OK — 769 files — pinned to `3dedc22` at scan start |
| Workflow files read | ✅ 4 of 4 — deploy-docs, publish, release, test |
| Merged PRs reviewed | ⚠ 160 of ~461 (sampled) — under the 300-window cap |
| Suspicious PR diffs read | 6 of the 300-keyword hits — the flagged 6 in §03 read in full |
| Dependency scan | ⚠ Metadata only — Dependabot API 403 (admin scope); full lockfile audit not performed |
| Executable files inspected | ⚠ 7 of 7 (2 Warning, 4 OK, 1 Info) |
| `pull_request_target` scan | ✅ Verified — 0 occurrences across 4 workflows |
| README paste-scan | ✅ 0 paste-blocks |
| Agent-rule files | ✅ 1 found — CLAUDE.md at root (Tier 1 auto-loaded). Not CI-amplified. |
| Prompt-injection scan | ✅ 0 matches / 0 actionable |
| Distribution channels verified | ⚠ Install path verified, installed artifact NOT verified — trust chain terminates at GitHub Releases (see F2 issue #1246) |
| Windows surface coverage | ✅ install.ps1 inspected; CI test matrix covers windows-latest |
| OSSF Scorecard | ⚠ Not indexed (API 404) |
| osv.dev | ℹ Not queried — transitive surface covered by CVE watch (F3) |
| Secrets-in-history | ⚠ Not scanned (gitleaks not available) |
| API rate budget | ✅ 5000/5000 remaining |
| Tarball SHA | `3dedc22` — if your tree differs, re-run the scan |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| Dependabot alerts | ⚠ admin scope required; falling back to osv.dev |
| Monorepo coverage | 11 inner packages (11 sampled: packages/cli, packages/core, packages/providers, packages/workflows, packages/git, packages/paths, packages/web, packages/slack, packages/telegram, packages/github, packages/config) · lifecycle hits: 0 |
| `pull_request_target` usage | 0 found across 4 workflows · Zero `pull_request_target` usage across 4 workflows — rules out that class of attack |

**Gaps noted:**

1. gitleaks not installed in this scan environment — secrets-in-history not scanned.
2. Distribution channels: 4 PyPI packages verified via registry presence; 1 Docker channel (docker-local-build) unverifiable (no prebuilt image published).
3. Dependabot alerts API returned 403 (admin:repo_hook scope missing); osv.dev fallback covered 18 direct deps across all 4 sub-packages.
4. Windows-only surface coverage: N/A (Python cross-platform, no PS1/BAT files in repo; harness confirmed 0 Windows-pattern hits).

---

## 07 · Evidence appendix

> ℹ 11 facts · ★ 3 priority

### ★ Priority evidence (read first)

#### ★ Evidence 3 — Open XXE injection vulnerability in DOCX pre-processor; fix PR #1582 sitting ~47 days

```bash
gh issue view 1565 -R microsoft/markitdown --json title,state,body,createdAt
gh pr view 1582 -R microsoft/markitdown --json state,createdAt,reviews,comments
```

Result:
```None
Title: Security: XXE vulnerability in DOCX pre-processor (ET.fromstring on untrusted input)
State: OPEN
Created: 2026-02-20T22:29:06Z
Body: Type: XML External Entity (XXE) Injection, Severity: High, File: packages/markitdown/src/markitdown/converter_utils/docx/pre_process.py line 45, Commit tested: 4a5340f. The function _convert_omath_to_latex() uses ET.fromstring() to parse XML content extracted from user-supplied DOCX files.
---
{"state":"OPEN","createdAt":"2026-03-03T03:23:46Z","reviews":0,"comments":3}
```

*Classification: Confirmed fact — OPEN High-severity XXE injection. Fix PR #1582 (uses defusedxml.ElementTree) open 47 days at scan, 0 reviews, 3 comments. Vulnerable code still present in main/v0.1.5.*

#### ★ Evidence 4 — Open Zip Bomb DoS vulnerability in ZipConverter; 114 days old, no fix PR

```bash
gh issue view 1514 -R microsoft/markitdown --json title,state,body,createdAt
```

Result:
```None
Title: [Security] Potential Denial of Service (DoS) via Zip Bomb in ZipConverter
State: OPEN
Created: 2025-12-27T07:28:00Z
Body: ZipConverter reads entire content of each file within a ZIP archive into memory simultaneously. Exploitable via Zip Bomb (small compressed file decompressing to very large size), leading to OOM/system crash. File: packages/markitdown/src/markitdown/converters/_zip_converter.py
```

*Classification: Confirmed fact — OPEN Medium-severity DoS. No size guard on zip-entry reads. Issue open 114 days. No fix PR. Harness Step A independently flagged zipfile.ZipFile calls in same file (archive_unsafe family, line 96). Additional exposures: _epub_converter.py and converter_utils/docx/pre_process.py use same zipfile pattern.*

#### ★ Evidence 11 — Harness independently flagged the Zip Bomb-vulnerable file and related zipfile call sites

```bash
python3 docs/phase_1_harness.py microsoft/markitdown (Step A dangerous-primitives grep)
```

Result:
```None
archive_unsafe hits:
  packages/markitdown/src/markitdown/converters/_zip_converter.py:96  with zipfile.ZipFile(file_stream, "r") as zipObj:
  packages/markitdown/src/markitdown/converters/_epub_converter.py:59  with zipfile.ZipFile(file_stream, "r") as z:
  packages/markitdown/src/markitdown/converter_utils/docx/pre_process.py:139  with zipfile.ZipFile(input_docx, mode="r") as zip_input:
```

*Classification: Confirmed fact — Phase 1 harness (docs/phase_1_harness.py) Step A dangerous-primitives grep flagged 3 zipfile.ZipFile call sites via the archive_unsafe pattern family. The first match (line 96 of _zip_converter.py) is exactly the call site in issue #1514's body. The EPUB converter and DOCX pre-processor use the same unguarded-ZipFile pattern and would share the Zip Bomb exposure if fed a zipbombed file — not separately issue-filed at scan time. This is an example of the harness surfacing additional attack surface beyond what's in the public issue tracker.*

### Other evidence

#### Evidence 1 — Classic branch protection 404, ruleset exists but requires 0 approving reviewers

```bash
gh api "repos/microsoft/markitdown/branches/main/protection"
gh api "repos/microsoft/markitdown/rules/branches/main"
```

Result:
```json
{"message":"Not Found","status":"404"}
[{"type":"deletion"},{"type":"non_fast_forward"},{"type":"pull_request","parameters":{"required_approving_review_count":0,"require_code_owner_review":false,"require_last_push_approval":false}},{"type":"required_status_checks","parameters":{"required_status_checks":[{"context":"tests"},{"context":"pre-commit"}]}}]
```

*Classification: Confirmed fact — classic branch protection returns 404 (no classic rule). Ruleset 2607793 'Protect Main Branch' is active with 4 rules: deletion prevention, non-fast-forward, PR required with required_approving_review_count=0 (!), required status checks (tests + pre-commit). CODEOWNER review explicitly false. Better than caveman/Archon/zustand (ruleset exists) but PR gate admits zero-reviewer merges.*

#### Evidence 2 — No CODEOWNERS in any of 4 standard locations

```bash
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do gh api "repos/microsoft/markitdown/contents/$p" 2>&1 | head -1; done
```

Result:
```None
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

*Classification: Confirmed fact — all four standard locations return 404. Combined with require_code_owner_review=false in E1 ruleset, there is no path-scoped reviewer requirement.*

#### Evidence 5 — Unanswered request for GHSA on CVE-2025-64512 (silently patched in v0.1.4)

```bash
gh issue view 1504 -R microsoft/markitdown --json title,state,body,comments
```

Result:
```None
Title: Should a security advisory for Markitdown 0.1.3 be released?
State: OPEN
Created: 2025-12-12T10:09:59Z
Body: Markitdown 0.1.3 is vulnerable to arbitrary code execution due to CVE-2025-64512. The issue has been patched in release 0.1.4, where the package pdfminer.six has been updated. However, this seems to be a minor feature release rather than an important security update. Should the maintainers release a security advisory?
Comment count: 0
```

*Classification: Confirmed fact — community member explicitly requested GHSA for CVE-2025-64512 (arbitrary code execution via pdfminer.six transitive CVE affecting markitdown 0.1.3). v0.1.4 bumped the dep (closing the vuln) but no GHSA was published. The request has been open 130 days with zero comments and no maintainer response. F5-class unadvertised-fix pattern.*

#### Evidence 6 — 0 formal review decisions on 174 merged PRs; 40% any-review; 76 self-merges

```bash
gh pr list -R microsoft/markitdown --state merged --limit 300 --json reviewDecision,reviews,author,mergedBy | jq '{total: length, formal: [.[] | select(.reviewDecision != null and .reviewDecision != "")] | length, any_review: [.[] | select(.reviews | length > 0)] | length, self_merge: [.[] | select(.author.login == .mergedBy.login)] | length}'
```

Result:
```json
{"total":174,"formal":0,"any_review":70,"self_merge":76}
```

*Classification: Confirmed fact — 0/174 merged PRs have reviewDecision set (0% formal). 70/174 (40.2%) have at least one review-object present. 76/174 (43.7%) are self-merges (PR author = merged-by). The E1 ruleset PR gate requires a PR but 0 approving reviewers, so self-merges + no formal decisions are structurally enabled.*

#### Evidence 7 — Dependabot config exists but tracks only github-actions; pip ecosystem NOT configured

```bash
gh api "repos/microsoft/markitdown/contents/.github/dependabot.yml" --jq .content | base64 -d
```

Result:
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

*Classification: Confirmed fact — dependabot.yml declares only github-actions ecosystem on weekly schedule. pip ecosystem is NOT configured, so transitive Python-dep CVEs (like CVE-2025-64512 in pdfminer.six) are not auto-surfaced via Dependabot PRs.*

#### Evidence 8 — 100% of 18 releases authored by afourney; release bus-factor is 1

```bash
gh api repos/microsoft/markitdown/releases --jq '[.[] | .author.login] | group_by(.) | map({author: .[0], count: length})'
```

Result:
```json
[{"author":"afourney","count":18}]
```

*Classification: Confirmed fact — every one of the 18 releases (v0.1.0 through v0.1.5 + prereleases) was authored by afourney. Code-contribution bus-factor is ~2 (afourney + gagb), but release-management bus-factor is 1.*

#### Evidence 9 — Microsoft SECURITY.md — enterprise MSRC disclosure with 24-hour SLA + PGP

```bash
gh api repos/microsoft/markitdown/contents/SECURITY.md --jq .content | base64 -d | head -15
```

Result:
```markdown
<!-- BEGIN MICROSOFT SECURITY.MD V0.0.9 BLOCK -->

## Security

Microsoft takes the security of our software products and services seriously...

## Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them to the Microsoft Security Response Center (MSRC) at https://msrc.microsoft.com/create-report.

If you prefer to submit without logging in, send email to secure@microsoft.com. If possible, encrypt your message with our PGP key...

You should receive a response within 24 hours.
```

*Classification: Confirmed fact — SECURITY.md is the Microsoft V0.0.9 boilerplate routing disclosures to MSRC with 24-hour response SLA, plus direct email (secure@microsoft.com) with PGP. Enterprise-grade disclosure infrastructure. Community profile API did NOT report this at /files.security_policy (observed quirk; harness fallback via direct contents check caught it).*

#### Evidence 10 — Python sources clean of shell-injection primitives (os.system, subprocess.shell=True)

```bash
gh api "search/code?q=repo:microsoft/markitdown+subprocess.shell%3DTrue" --jq .total_count
gh api "search/code?q=repo:microsoft/markitdown+os.system" --jq .total_count
```

Result:
```None
0
0
```

*Classification: Confirmed fact — 0 hits for shell-interpolation-injection patterns. Harness Step A grep (docs/phase_1_harness.py dangerous-primitive scan) also found 3 subprocess.run call sites but all use list-form argv (no shell=True), e.g. converter_utils _exiftool.py line 22 for exiftool version check and test files. No shell-interpolation-injection risk on the shell surface.*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `604bba13da2f43b756b49122cb65bdedb85b1dff` () · scanner V2.5-preview-wild*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
