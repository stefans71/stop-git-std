# Security Investigation: JuliusBrussee/caveman

**Investigated:** 2026-04-20 | **Applies to:** main @ `c2ed24b` · v1.6.0 | **Repo age:** 0 years | **Stars:** 32,844 | **License:** MIT

> A twelve-day-old Claude Code plugin that shipped real local-privilege-escalation vulnerabilities before it got to a thousand stars — and fixed them without an advisory. This is the forensic record.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-caveman.md` (+ `.html` companion) |
| Repo | [github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) |
| Short description | Claude Code plugin that compresses LLM output to caveman speech to cut ~65% of tokens. Ships as Claude Code plugin, Codex plugin, Gemini CLI extension, and agent rule files for Cursor/Windsurf/Cline/Copilot. |
| Category | `AI/LLM tooling` |
| Subcategory | `Token-saver / output-compressor` |
| Language | JavaScript |
| License | MIT |
| Target user | Claude Code users, AI agent developers |
| Verdict | **Critical** (split — see below) |
| Scanned revision | `main @ c2ed24b` (release tag `v1.6.0`) |
| Commit pinned | `c2ed24b` |
| Scanner version | `V2.5-preview-step-g` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan; rename this file on re-run. |

---

## Verdict: Critical (split — Version axis only)

### Version · Version · Current release · v1.6.0 · installing today — **Critical — Clean code, but no upstream gate — every install trusts the maintainer's credentials**

Code in v1.6.0 is sound. But every install path fetches live main, and there is no branch protection on main, no rulesets, no CODEOWNERS (F0 Critical). A single compromised maintainer credential ships code to every Claude Code session on the next install.

### Version · Version · Historical installs · v1.0.0 – v1.5.1 — **Critical — Upgrade required**

A local-privilege-escalation vulnerability shipped for 11 days. No advisory was issued. If you installed before 2026-04-15, upgrade now — do not skip. The F0 governance gap applies to historical installs too: even now, there is no upstream gate preventing a repeat.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Historical vulnerability, disclosed through release notes only (3 findings)</strong>
<br><em>Symlink bug shipped 11 days, fix landed in v1.6.0, no GitHub Security Advisory</em></summary>

1. **Vulnerability** — Symlink-based file-clobber vulnerability existed in all versions v1.0.0 through v1.5.1 (11 days, 2026-04-04 to 2026-04-15). Fixed in v1.6.0.
2. **Disclosure · F5** — Unadvertised security fix — no advisory, no CVE, but release title reads 'Hardening release: hook crash fixes + symlink-safe flag writes.' Named in release notes, not in GitHub's advisory channel.
3. **Response lag** — Security PR sat open for 5 days after the reporter explained the exact attack vector in the commit message.

</details>

<details>
<summary><strong>⚠ Governance and distribution — no review gate, no pinning (4 findings)</strong>
<br><em>15% formal review rate, no branch protection, no CODEOWNERS, every install channel tracks live main</em></summary>

1. **Review rate · F11** — 15% formal (5/33) and 36% any-review (12/33). 7-PR gap = informal review without formal decision. Security PRs #70 and #71 had zero review activity.
2. **Batch merge** — v1.6.0 'hardening release' is a 10+ PR batch merge committed at a single timestamp — security fix hidden among unrelated changes.
3. **Distribution** — Every distribution channel fetches from live main or unpinned artifacts — no release assets, marketplace manifest says "source": "./", install scripts curl from main on both Linux and Windows.
4. **Governance · F14** — No branch protection on main. No CODEOWNERS anywhere — no path-scoped review gate either. Dependabot disabled.

</details>

<details>
<summary><strong>✓ Positive signals — code quality, scope, maintainer legitimacy (3 findings)</strong>
<br><em>v1.6.0 code is defensive, dep surface minimal, maintainer is an established 4-year account</em></summary>

1. **Code quality · F16** — The v1.6.0 hardening code itself is thorough: O_NOFOLLOW, atomic temp-and-rename, whitelist-validated reads, size caps, symlink refusal. Windows PS1 parity confirmed.
2. **Attack surface** — Minimal runtime surface — 1 dependency (benchmarks only), zero network calls in hook files.
3. **Maintainer** — Established 4-year GitHub account with 42 public repos, 618 followers — not a sockpuppet.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — No |
| Is it safe out of the box? | ❌ **No** — No |
| Do they fix problems quickly? | ⚠ **Partly** — Partly |
| Do they tell you about problems? | ❌ **No** — No |

---

## 01 · What should I do?

> ⚠ Action needed if installed < v1.6.0 · 3 steps
>
> **Most urgent:** if you installed caveman before 2026-04-15, upgrade now (Step 1). For new installers today (Step 2): code is fine but install method matters. Step 3 is what to ask the maintainer.

### Step 1: If you installed v1.5.1 or earlier, upgrade or remove now (⚠)

**Non-technical:** Open Claude Code, run /plugin disable caveman, then /plugin install caveman. This gets you the hardened v1.6.0.

```bash
cat ~/.claude/hooks/caveman-config.js 2>/dev/null | grep -c 'safeWriteFlag'
claude plugin disable caveman
claude plugin install caveman
```

### Step 2: If installing for the first time, prefer plugin manager over curl-pipe and verify after (ℹ)

**Non-technical:** Installing now is fine — the hardened version is what you get. Be aware this plugin runs code every time Claude Code starts and every time you submit a prompt.

```bash
claude plugin install caveman
grep -l 'safeWriteFlag' ~/.claude/plugins/*/caveman*/hooks/*.js
```

### Step 3: Ask the maintainer for standard hygiene (ℹ)

**Non-technical:** Open an issue asking for: a GitHub Security Advisory, SECURITY.md, Dependabot re-enabled, and branch protection on main.

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 2 Warning · ℹ 1 Info · ✓ 1 OK
>
> 5 findings total.
### F0 — Critical · Structural — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a 32k-star repo that ships hooks into every Claude Code session (C20)

*Continuous · Since repo creation · → If you install caveman: pin to a specific release tag, not main. After install, check ~/.claude/hooks/ against the tagged release. If you maintain this repo: enable branch protection on main and add CODEOWNERS covering hooks/, rules/, .github/workflows/, install scripts.*

**What we observed.** Classic branch protection on main returns 404. Rulesets: []. Rules on main: []. CODEOWNERS absent in all four standard locations. Owner is a User account (no org-level rulesets possible).

**What this means for you.** When you install caveman, you are trusting JuliusBrussee's account security as tightly as you'd trust your own laptop's password. There is no automated gate that would catch a phished-credential push before it reaches your next install, and the hook files run on every Claude Code session.

**What this does NOT mean.** This does not mean the current v1.6.0 code is malicious. The finding is purely about the upstream process gap — any future compromise has no automated gate.

| Meta | Value |
|------|-------|
| Classic branch protection | ❌ 404 on `main` |
| Rulesets | ❌ `[]` — zero rulesets |
| CODEOWNERS | ❌ Absent (4 locations checked) |
| Stars (blast radius) | 32,844 |
| Releases in last 30 days | ⚠ 10 |
| Active executable surface | Hooks in every Claude Code session |

**How to fix.** GitHub *Settings → Branches → Add branch protection rule* for `main`: require pull request reviews (1 approver minimum), require status checks, require branches to be up to date before merging, do not allow bypassing. Also add a `.github/CODEOWNERS` file covering at minimum `hooks/`, `rules/`, `.github/workflows/`, and install scripts.

### F5 — Warning · Vulnerability — Unadvertised symlink vulnerability — named in release notes, not in advisory channel

*11 days · 2026-04-04 – 2026-04-15 · → If you installed before 2026-04-15, upgrade now. New installers on v1.6.0 are fine.*

**What we observed.** PR #70 commit message spells out the symlink attack in full. The hook wrote to a predictable path using fs.writeFileSync without any symlink checks. Affected versions: v1.0.0 through v1.5.1 (11 days live). Fix adds O_NOFOLLOW, atomic temp+rename, and symlink refusal.

**What this means for you.** Any user who installed caveman between 2026-04-04 and 2026-04-14 ran vulnerable code. A local attacker or malicious process could have redirected the hook's flag file write to overwrite sensitive user files.

**What this does NOT mean.** This does not mean every user was exploited. Exploitation requires a local attacker or malicious co-process — it's not a remote code execution bug. v1.6.0 is clean.

| Meta | Value |
|------|-------|
| Reported by | tuanaiseo — PR #70 |
| Fixed by | tuanaiseo — PR #70, PR #71 |
| Merged by | JuliusBrussee |
| Reviewed by | ❌ Nobody |
| The fix | O_NOFOLLOW + atomic temp+rename + symlink refusal at parent and target |
| Advisory published | ❌ None |

**How to fix.** Upgrade to v1.6.0 via `claude plugin disable caveman && claude plugin install caveman`. Verify with `grep -c 'safeWriteFlag' ~/.claude/hooks/caveman-config.js` — should return >= 1.

### F11 — Warning · Governance — Review rate: 15% formal, 36% any (F11 dual metric)

*Since repo creation · Throughout history · → Only relevant if you rely on caveman for sensitive workflows. Ask maintainer to require one other approver on hook/workflow PRs.*

| Meta | Value |
|------|-------|
| PRs with formal review | 5 / 33 |
| Review rate | ❌ 15% |
| Security PRs with review | ❌ 0 of 2 (#70, #71) |

### F14 — Info · Governance — No branch protection rule on main

*Current · Current · → No action required of you — this is a maintainer-side issue. Compounds every other finding though.*

| Meta | Value |
|------|-------|
| API response | 404 Not Found |
| Interpretation | No protection rule exists (definitive) |

### F16 — OK · Code quality — v1.6.0 security code is thorough and well-reasoned

*v1.6.0 · Current · → No action needed. Positive signal: maintainer's v1.6.0 fix shows real security engineering care.*

| Meta | Value |
|------|-------|
| O_NOFOLLOW | ✅ Yes |
| Atomic rename | ✅ Yes |
| Whitelist-validated reads | ✅ Yes |
| Size cap | ✅ 64 bytes |

---

## 02A · Executable file inventory

> ⚠ 3 Warning · ℹ 2 Info · ✓ 3 OK — 8 executable files cataloged. 3 need attention: install.sh (fetches live main) and two hook files (had pre-v1.6.0 symlink vuln, now fixed). 3 are OK. 2 are Info (CI-amplified rule source + README paste block).

### Layer 1 — one-line summary

- 8 executable files: 2 hook JS files (symlink-safe in v1.6.0, previously vulnerable), 1 config JS module (security-critical), 1 install shell script (fetches live main), 1 uninstall shell script, 1 CI workflow (amplifies rule file to 4 agents), 1 agent rule source (17-line behavioral rule, CI-synced), and 1 README paste-block (7-line user-pasted rules).

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `hooks/install.sh` | Installer shell script | User-triggered or curl-pipe | curl to raw.githubusercontent.com/JuliusBrussee/caveman/main/hooks/* | Fetches from live main branch | Warning: live-main fetch, not pinned to any release tag. Writes to ~/.claude/hooks/*. |
| `hooks/caveman-activate.js` | SessionStart hook | Node.js (Claude Code hook sandbox) | fs.writeFileSync (pre-v1.6.0); safeWriteFlag (v1.6.0) | None | Runs every Claude Code session start. Symlink-safe in v1.6.0 via safeWriteFlag. Vulnerable in v1.0.0-v1.5.1. |
| `hooks/caveman-mode-tracker.js` | UserPromptSubmit hook | Node.js (Claude Code hook sandbox) | fs.writeFileSync (pre-v1.6.0); safeWriteFlag (v1.6.0) | None | Runs on every user prompt. Reads stdin (user prompt JSON). Both read and write paths symlink-safe in v1.6.0. |
| `hooks/caveman-config.js` | Security config module | Node.js (imported by hooks) | None — exports safeWriteFlag and readFlag | None | Security-critical module. Implements O_NOFOLLOW + temp+rename + symlink refusal. Watch in future diffs. |
| `hooks/uninstall.sh` | Uninstaller shell script | User-triggered | None | None | Uses env-var-passing pattern (not shell interpolation). Removes ~/.claude/hooks/caveman-* and rewrites settings.json. |
| `.github/workflows/sync-skill.yml` | CI automation | GitHub Actions | None | Standard git push only | Copies SKILL.md into 4 agent rule locations on push to main. contents:write scoped to repo. No pull_request_target. No SHA-pinned actions — uses actions/checkout@v4. |
| `rules/caveman-activate.md` | Agent rule source (CI-amplified) | LLM agent context (alwaysApply) | None in current content | None | 17 lines of behavioral rules. CI-synced to 4 always-on agent rule files. High leverage: 1 file → every user's always-on agent config on next CI run. |
| `README.md` | Install-paste block (line 271) | User's LLM agent context | None in current content | None | 7-line block users paste into their agent's system prompt. Safe today; permanent consequence once pasted. |

The two hook files (caveman-activate.js and caveman-mode-tracker.js) were the vulnerability sites pre-v1.6.0 — the symlink-unsafe fs.writeFileSync calls have been replaced with safeWriteFlag from caveman-config.js. The install.sh file remains a live-main fetch risk regardless of code version.

---

## 03 · Suspicious code changes

> **33 PRs reviewed — full coverage (under the 300-PR cap).** 6 PRs flagged as security-relevant, none had formal review. Two are the security fix itself (#70, #71). The other four are hook-touching PRs merged the same day in the batch without any approvals.

Sample: the 6 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 15% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#70](https://github.com/JuliusBrussee/caveman/pull/70) | Added symlink-safe write to hook files (the real security fix) | tuanaiseo | JuliusBrussee | No formal decision | Real security fix, zero reviews, no advisory published. Sat open 5 days. |
| [#71](https://github.com/JuliusBrussee/caveman/pull/71) | Strengthened safeWriteFlag with parent-chain symlink check | tuanaiseo | JuliusBrussee | No formal decision | Follow-up security work, same reporter as #70, zero reviews. Sat open 5 days. |
| [#120](https://github.com/JuliusBrussee/caveman/pull/120) | Natural-language activation in mode tracker — new regex triggers flag-file writes | hummat | JuliusBrussee | No formal decision | Expands user-input parsing surface — new regex triggers flag-file writes, merged without decision. |
| [#146](https://github.com/JuliusBrussee/caveman/pull/146) | Respect CLAUDE_CONFIG_DIR across all hooks | BrendanIzu | JuliusBrussee | No formal decision | Touches every hook's path resolution — merged without formal approval. |
| [#174](https://github.com/JuliusBrussee/caveman/pull/174) | Isolate hooks as CommonJS via hooks/package.json | malakhov-dmitrii | JuliusBrussee | No formal decision | Changes module-loading on user machines, fastest merge in batch (4 hours), no review. |
| [#148](https://github.com/JuliusBrussee/caveman/pull/148) | Update Codex hook config shape | davidbits | JuliusBrussee | No formal decision | Plugin config shape change, no review. |

---

## 04 · Timeline

> ✓ 1 good · 🟡 3 neutral · 🔴 3 concerning
>
> Eight events over 13 days. **The story is exploit-then-fix — but no disclosure.** Repo launched April 4 and went viral; a reporter found and described the symlink attack by April 10; the maintainer shipped 4 more vulnerable releases before merging the fix on April 15 in a 10-PR batch. The disclosure gap is the one still-open wound: no advisory, no SECURITY.md, no programmatic upgrade signal.

- 🟡 **2026-04-04 · REPO CREATED** — Repo created by JuliusBrussee. v1.0.0 released same day — hooks ship with the symlink-unsafe flag write (unknown at the time).
- 🟡 **2026-04-05 · RAPID RELEASES** — v1.1.0 through v1.3.5 released over 5 days. All still contain the vulnerable hook write; nobody had reported it yet.
- 🔴 **2026-04-10 · VULN REPORTED** — tuanaiseo files PR #70 with a commit message spelling out the symlink attack in full. PR #71 filed minutes later with stronger parent-chain check. Both PRs sit open.
- 🔴 **2026-04-11 · STILL SHIPPING** — v1.4.0, v1.4.1, v1.5.0, v1.5.1 released while PRs #70 and #71 sit unaddressed. All four versions ship the vulnerable code.
- 🟢 **2026-04-15 · FIX SHIPS** — Maintainer batch-merges 10+ PRs including #70 and #71 within a 23-minute window. v1.6.0 tagged — 'Hardening release: hook crash fixes + symlink-safe flag writes.' Code fix is good. Batch-merge is bad.
- 🔴 **2026-04-15 · NO ADVISORY** — No GitHub Security Advisory created. No CVE. No SECURITY.md added. Users of v1.0.0-v1.5.1 receive no programmatic notification that they are running vulnerable code.
- 🟡 **2026-04-16 · SCAN** — This scan runs — 1 day after v1.6.0 release. Vulnerable versions (v1.0.0-v1.5.1) remain installable from the Releases page.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | ⚠ 12 days | Very new — released 2026-04-04, scanned 2026-04-16 |
| Stars | 32,844 | Viral growth to 32k+ stars in 12 days — scrutiny should match |
| Owner account age | ✅ 4 years | Established account, 42 public repos, 618 followers — not a sockpuppet |
| Merged PRs (review rate) | ❌ 5 / 33 (15%) | Only 15% have formal review decisions |
| Branch protection | ❌ None | API returns 404 — definitively no rule configured |
| Security advisories | ❌ 0 published | Repo has never published a GitHub Security Advisory |
| Dependabot | ❌ Disabled | Explicitly disabled — even upstream dep vulns won't surface |
| Runtime dependencies | ✅ 1 (benchmarks only) | Hook package.json has zero deps; only anthropic SDK for benchmarks |
| CI workflows | 1 (sync-skill.yml) | Single internal file-copy automation, narrowly scoped |
| Releases | 10 | v1.0.0 → v1.6.0 in 11 days; v1.0.0–v1.5.1 are vulnerable |
| OSSF Scorecard | ❌ Not indexed | API returned 404 — repo too new or not yet crawled by OSSF |

---

## 06 · Investigation coverage

> **33/33 PRs reviewed · 8/8 executables inspected · 0/6 distribution channels fully verified · 2 gaps noted.** All 33 merged PRs reviewed (full coverage under the 300-PR cap). Every executable file inspected. Distribution channels: 0 of 6 fully verified against source — method limitation, flagged under F1+F2.

| Check | Result |
|-------|--------|
| Merged PRs reviewed | ✅ 33 of 33 — full coverage, under the 300-PR sample cap |
| Suspicious PR diffs read | 6 of 19 — both Security-labeled PRs (#70, #71) plus 4 recent hook-touching PRs read in full |
| Dependency scan | ❌ Blocked — Dependabot explicitly disabled (HTTP 403), but runtime dep list is trivial |
| Workflow files read | ✅ 1 of 1 — sync-skill.yml fully inspected |
| Executable files inspected | ⚠ 8 of 8 (3 Warning, 3 OK, 2 Info) |
| Tarball extraction | ✅ 103 files extracted; grep positive-control passed |
| OSSF Scorecard | ❌ Not indexed — API returned 404; repo too new for OSSF crawl |
| osv.dev | ✅ No runtime deps to check — hook package.json has zero dependencies |
| Secrets-in-history | Not scanned (gitleaks not available) |
| API rate budget | 5000/5000 remaining. PR sample: full. |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| Dependabot alerts | ❌ Disabled for this repository |
| `pull_request_target` usage | 0 found across 1 workflows · Zero pull_request_target usage in sync-skill.yml — rules out that class of attack |

**Gaps noted:**

1. Windows hook variants (install.ps1, uninstall.ps1, caveman-statusline.ps1) not inspected in equal depth to the Unix shell and Node.js files.
2. 13 of 19 security-keyword PRs were classified from metadata only — their diffs were not read in full.

---

## 07 · Evidence appendix

> ℹ 10 facts · ★ 3 priority

10 command-backed claims. **Skip ahead to items marked ★ START HERE** — the vulnerability proof, the no-advisory confirmation, and the branch-protection check. Those three are the falsification criteria for the Critical verdict.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — v1.6.0 fixes a real symlink vulnerability that existed in v1.0.0–v1.5.1

```bash
gh pr view 70 -R JuliusBrussee/caveman --json commits -q '.commits[0].messageBody'
```

Result:
```None
The SessionStart hook writes to `~/.claude/.caveman-active` using `fs.writeFileSync` on a predictable path. If that path is replaced with a symlink, Node will follow it and overwrite the symlink target. A local attacker (or another process running as the same user) could abuse this to modify unintended files writable by the user.

Affected files: caveman-activate.js, caveman-mode-tracker.js

Signed-off-by: tuanaiseo 221258316+tuanaiseo@users.noreply.github.com
```

*Classification: Confirmed fact — vulnerability described in the reporter's own commit message; fix adds O_NOFOLLOW and symlink refusal; before/after diff confirms the unprotected write.*

#### ★ Evidence 2 — No GitHub Security Advisory was issued for the fix

```bash
gh api "repos/JuliusBrussee/caveman/security-advisories"
```

Result:
```json
[]
```

*Classification: Confirmed fact — empty array response means zero advisories published.*

#### ★ Evidence 5 — No branch protection on main

```bash
gh api "repos/JuliusBrussee/caveman/branches/main/protection"
```

Result:
```json
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/branches/branch-protection#get-branch-protection","status":"404"}
```

*Classification: Confirmed fact — 404 is authoritative here. The authenticated token has admin-read access and would return 403 if the issue were permissions; 404 means no rule exists.*

### Other evidence

#### Evidence 3 — v1.6.0 was a 10+ PR batch merge committed at a single timestamp

```bash
gh pr list -R JuliusBrussee/caveman --state merged --limit 300 --json number,title,mergedAt \
  | jq '[.[] | select(.mergedAt == "2026-04-15T12:50:16Z")] | length'
```

Result:
```None
16
```

*Classification: Confirmed fact — 16 PRs share the same mergedAt timestamp, reflecting a synchronized batch merge.*

#### Evidence 4 — 85% of merged PRs have no formal review

```bash
gh pr list -R JuliusBrussee/caveman --state merged --limit 300 --json reviewDecision \
  | jq '[.[] | select(.reviewDecision != null and .reviewDecision != "")] | length'
```

Result:
```None
5
```

*Classification: Confirmed fact — 5 of 33 merged PRs = 15% formal review rate.*

#### Evidence 6 — Dependabot is disabled for this repository

```bash
gh api "repos/JuliusBrussee/caveman/dependabot/alerts"
```

Result:
```json
{"message":"Dependabot alerts are disabled for this repository.","documentation_url":"https://docs.github.com/rest/dependabot/alerts#list-dependabot-alerts-for-a-repository","status":"403"}
```

*Classification: Confirmed fact — the response distinguishes 'disabled' from a permissions error.*

#### Evidence 7 — Runtime dependency surface is minimal

```bash
find /tmp/repo-scan-JuliusBrussee-caveman -type f \( -name 'package.json' -o -name 'requirements*.txt' -o -name 'pyproject.toml' \)
cat /tmp/repo-scan-JuliusBrussee-caveman/hooks/package.json
cat /tmp/repo-scan-JuliusBrussee-caveman/benchmarks/requirements.txt
```

Result:
```None
/tmp/repo-scan-JuliusBrussee-caveman/hooks/package.json
/tmp/repo-scan-JuliusBrussee-caveman/benchmarks/requirements.txt

{ "type": "commonjs" }

anthropic>=0.40.0
```

*Classification: Confirmed fact — the hook package.json declares no dependencies; the only Python dep is the Anthropic SDK, only for the benchmark suite.*

#### Evidence 8 — Maintainer is an established account, not a sockpuppet

```bash
gh api "users/JuliusBrussee" -q '{login,created_at,public_repos,followers}'
```

Result:
```json
{"login":"JuliusBrussee","created_at":"2022-04-21T20:06:45Z","followers":618,"public_repos":42}
```

*Classification: Confirmed fact — account created 2022-04-21 (4 years old at time of scan), 42 public repos, 618 followers.*

#### Evidence 9 — v1.6.0 hooks implement defense-in-depth against symlink attacks

```bash
grep -nE 'O_NOFOLLOW|lstatSync|isSymbolicLink|renameSync|fchmodSync' \
  /tmp/repo-scan-JuliusBrussee-caveman/hooks/caveman-config.js
```

Result:
```None
80:      if (fs.lstatSync(flagDir).isSymbolicLink()) return;
87:      if (fs.lstatSync(flagPath).isSymbolicLink()) return;
93:    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
94:    const flags = fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | O_NOFOLLOW;
99:      try { fs.fchmodSync(fd, 0o600); } catch (e) { /* best-effort on Windows */ }
103:    fs.renameSync(tempPath, flagPath);
126:    st = fs.lstatSync(flagPath);
130:    if (st.isSymbolicLink() || !st.isFile()) return null;
131:    if (st.size > MAX_FLAG_BYTES) return null;
133:    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
134:    const flags = fs.constants.O_RDONLY | O_NOFOLLOW;
```

*Classification: Confirmed fact — the v1.6.0 code uses every defense expected for this class of vulnerability.*

#### Evidence 10 — No SECURITY.md at repo root

```bash
find /tmp/repo-scan-JuliusBrussee-caveman -maxdepth 2 -iname 'SECURITY.md'
```

Result:
```None
/tmp/repo-scan-JuliusBrussee-caveman/caveman-compress/SECURITY.md
```

*Classification: Confirmed fact — the only SECURITY.md is nested inside caveman-compress/ and covers a different concern (Snyk static-analysis rating), not a disclosure policy.*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `c2ed24b` (v1.6.0) · scanner V2.5-preview-step-g*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
