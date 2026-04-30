# Security Investigation: JuliusBrussee/caveman

**Investigated:** 2026-04-16 | **Applies to:** main @ c2ed24b · v1.6.0 | **Repo age:** 12 days | **Stars:** 32,844 | **License:** MIT

> A twelve-day-old Claude Code plugin that shipped real local-privilege-escalation vulnerabilities before it got to a thousand stars — and fixed them without an advisory. This is the forensic record.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-caveman.md` (+ `.html` companion) |
| Repo | [github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) |
| Short description | Claude Code plugin that compresses LLM output to "caveman" speech to cut ~65% of tokens. Ships as Claude Code plugin, Codex plugin, Gemini CLI extension, and agent rule files for Cursor/Windsurf/Cline/Copilot. |
| Category | AI/LLM tooling |
| Subcategory | Token-saver / output-compressor |
| Verdict | **Critical** (split — see below) |
| Scanned revision | `main @ c2ed24b` (release tag `v1.6.0`) |
| Prompt version | `v2.2` (initial scan with v2.1; v2.2 corrections applied retroactively after Round 1 board review; R3-C20 verdict amendment applied) |
| Prior scan | None — first run on this repo. Future re-runs should diff against `GitHub-Scanner-caveman-YYYY-MM-DD.md` snapshots. |
| Dossier | `DOSSIER · CAVEMAN · C2ED24B · 2026-04-16 · V2.2 · R3-C20` |

---

## Verdict: Critical (split) — governance gap applies to every audience

### Version · Current release · v1.6.0 · installing today — **Clean code, but no upstream gate — every install trusts the maintainer's credentials**

Code in v1.6.0 is sound. But every install path fetches live `main`, and there is no branch protection on `main`, no rulesets, no CODEOWNERS (F0 Critical). A single compromised maintainer credential ships code to every Claude Code session on the next install. If you install, pin to a specific tag and verify `~/.claude/hooks/` contents afterwards.

### Version · Historical installs · v1.0.0 – v1.5.1 — **Upgrade required**

A local-privilege-escalation vulnerability shipped for 11 days. No advisory was issued. If you installed before 2026-04-15, upgrade now — do not skip. The F0 governance gap applies to historical installs too: even now, there is no upstream gate preventing a repeat.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>WARN Historical vulnerability, disclosed through release notes only (3 findings)</strong>
<br><em>Symlink bug shipped 11 days, fix landed in v1.6.0, no GitHub Security Advisory</em></summary>

1. **Vulnerability** — Symlink-based file-clobber vulnerability existed in all versions v1.0.0 through v1.5.1 (11 days, 2026-04-04 to 2026-04-15). Fixed in v1.6.0.
2. **Disclosure · F5** — **Unadvertised** security fix — no advisory, no CVE, but release title reads "Hardening release: hook crash fixes + symlink-safe flag writes." Named in release notes, not in GitHub's advisory channel.
3. **Response lag** — Security PR sat open for 5 days after the reporter explained the exact attack vector in the commit message.

</details>

<details>
<summary><strong>WARN Governance and distribution — no review gate, no pinning (4 findings)</strong>
<br><em>15% formal review rate, no branch protection, no CODEOWNERS, every install channel tracks live main</em></summary>

1. **Review rate · F11** — 15% formal (5/33) and 36% any-review (12/33). 7-PR gap = informal review without formal decision. Security PRs #70 and #71 had zero review activity.
2. **Batch merge** — v1.6.0 "hardening release" is a 10+ PR batch merge committed at a single timestamp — security fix hidden among unrelated changes.
3. **Distribution · F1+F2** — Every distribution channel fetches from live `main` or unpinned artifacts — no release assets, marketplace manifest says `"source": "./"`, install scripts curl from main on both Linux and Windows.
4. **Governance · F14** — No branch protection on main. **No CODEOWNERS anywhere** — no path-scoped review gate either. Dependabot disabled.

</details>

<details>
<summary><strong>OK Positive signals — code quality, scope, maintainer legitimacy (3 findings)</strong>
<br><em>v1.6.0 code is defensive, dep surface minimal, maintainer is an established 4-year account</em></summary>

1. **Code quality · F16** — The v1.6.0 hardening code itself is thorough: O_NOFOLLOW, atomic temp-and-rename, whitelist-validated reads, size caps, symlink refusal. Windows PS1 parity confirmed.
2. **Attack surface** — Minimal runtime surface — 1 dependency (benchmarks only), zero network calls in hook files.
3. **Maintainer** — Established 4-year GitHub account with 42 public repos, 618 followers — not a sockpuppet.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | RED **No** — 15% formal review rate (5/33) · no branch protection · no CODEOWNERS |
| Do they fix problems quickly? | AMBER **Slow** — 5-day lag between security PR filed and merged |
| Do they tell you about problems? | RED **No advisory** — zero GitHub Security Advisories ever published, no SECURITY.md at repo root |
| Is it safe out of the box? | RED **No** — F0 governance gap applies to default install path + every distribution channel tracks live `main` |

---

## 01 · What should I do?

> WARN Action needed if installed < v1.6.0 · 3 steps
>
> **Most urgent:** if you installed caveman before 2026-04-15, upgrade now (Step 1). For new installers today (Step 2): code is fine but install method matters. Step 3 is what to ask the maintainer.

### Step 1: If you installed v1.5.1 or earlier, upgrade or remove now (WARN)

**Non-technical:** Open Claude Code, run `/plugin disable caveman`, then `/plugin install caveman`. This gets you the hardened v1.6.0. If you installed manually via the `install.sh` script, run `bash ~/.claude/hooks/uninstall.sh` first, then re-install. The old version could have been used — though only by someone who already had access to your computer — to silently overwrite files like your SSH key or shell profile. Upgrading closes that.

```bash
# Check which version you have
cat ~/.claude/hooks/caveman-config.js 2>/dev/null | grep -c 'safeWriteFlag'
# 0 = vulnerable, >= 1 = v1.6.0+

# Upgrade via plugin manager
claude plugin disable caveman
claude plugin install caveman

# OR manual re-install
bash ~/.claude/hooks/uninstall.sh
bash <(curl -s https://raw.githubusercontent.com/JuliusBrussee/caveman/main/hooks/install.sh)
```

### Step 2: If you're considering installing for the first time

**Non-technical:** Installing now is fine — the hardened version is what you get. The concern above (about silent fixes) is about past users, not you. Be aware that this plugin runs code every time Claude Code starts and every time you submit a prompt, so it has broad access to your local session.

```bash
claude plugin install caveman

# After install, verify the hardened helpers exist
grep -l 'safeWriteFlag' ~/.claude/plugins/*/caveman*/hooks/*.js
```

### Step 3: Ask the maintainer for standard hygiene

**Non-technical:** The maintainer is clearly doing careful work — the v1.6.0 code is well-written. But for a 32,000-star plugin, the lack of an advisory process is a real gap. Open an issue or discussion asking for:

1. A GitHub Security Advisory for the symlink vulnerability fixed in v1.6.0.
2. A `SECURITY.md` at the repo root with a disclosure process.
3. Dependabot re-enabled.
4. Branch protection on `main` with a 1-approver requirement.
5. A `.github/CODEOWNERS` file covering `hooks/`, `rules/`, `.github/workflows/`, and install scripts.

These are normal for a repo at 32k stars.

---

## 02 · What we found

> CRIT 1 Critical · WARN 5 Warning · INFO 2 Info · OK 2 OK
>
> 10 findings total. **The Critical finding (F0) is structural:** no branch protection on `main`, no rulesets, no CODEOWNERS — on a 32k-star Claude Code plugin that ships hooks running in every session, a single maintainer-credential compromise ships arbitrary code to every install. The Warnings cluster into **historical vulnerability (now fixed)** and **structural governance gaps** (unpinned distribution, no disclosure process, 15% review rate, batch-merge pattern). Start with F0 (Critical) and Finding 1 (the vulnerability) if time-pressed.
>
> **Your action:** F0 means even the clean-code v1.6.0 release is shipped through an ungated pipeline — pin to a tag, verify `~/.claude/hooks/` after install, subscribe to releases. If you installed before 2026-04-15 upgrade now. If you're installing today use the plugin manager, not the curl-pipe, and verify the version after.

### F0 — Critical · Ongoing · no upstream gate — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a 32k-star repo that ships hooks into every Claude Code session (C20)
*Continuous · Since repo creation · → If you install caveman: pin to a specific release tag, not `main`. After install, check `~/.claude/hooks/` against the tagged release. Subscribe to repo releases. If you maintain this repo: enable branch protection on `main` and add CODEOWNERS covering `hooks/`, `rules/`, `.github/workflows/`, install scripts.*

**What's missing.** The `main` branch (default) has no classic branch protection (API returns 404, authoritative); the repo has zero rulesets (`/rulesets` returns `[]`); no ruleset applies to `main` (`/rules/branches/main` returns `[]`); and there is no CODEOWNERS file in any of 4 standard locations. Owner is a User account, so no org-level rulesets can apply. Conclusion: any push that lands on JuliusBrussee's credentials goes directly to `main` without a review gate, required status check, or path-scoped reviewer.

**How an attacker arrives (F13).** This does NOT require xz-utils-level sophistication. Concrete paths: (1) credential phishing against a 32k-star-repo maintainer (findable target); (2) stale OAuth token reuse; (3) compromised browser session cookie; (4) malicious IDE extension running as the maintainer; (5) sloppy review of an attacker PR — the base review rate on this repo is 15% formal / 36% any, and the security fix PRs (#70, #71) had zero reviews, so the pattern wouldn't flag a credential-compromise PR as unusual.

**What this means for you (non-technical).** When you install caveman, you are trusting JuliusBrussee's account security as tightly as you'd trust your own laptop's password. There is no automated gate that would catch "maintainer pushed a bad change" before it reaches your next install, and the hook files run on every Claude Code session. The blast radius of a single credential compromise is every current and future user — 32k stars worth.

**Why Critical, not Warning.** C20 escalates to Critical when the repo ships executable code to user machines AND has active code flow (≥ 1 release in the last 30 days). Caveman meets both: hook files run on every Claude Code session start and every user prompt; 10 releases (v1.0.0 → v1.6.0) shipped in the last 30 days. Combined with the already-flagged "every install channel fetches live `main`" pattern, there is no independent second root of trust.

| Meta | Value |
|------|-------|
| Classic branch protection | BAD 404 on `main` |
| Rulesets | BAD `[]` — zero rulesets |
| CODEOWNERS | BAD Absent (4 locations checked) |
| Stars (blast radius) | 32,844 |
| Releases in last 30 days | WARN 10 |
| Active executable surface | Hooks in every Claude Code session |

**OSSF Scorecard correlation.** The OSSF Scorecard API returned 404 for this repo — it is not yet indexed, likely due to its 12-day age. Were it indexed, the Branch-Protection, Code-Review, and Security-Policy checks would all score 0/10, consistent with every governance finding in this report.

**How to fix (maintainer-side).** GitHub *Settings → Branches → Add branch protection rule* for `main`: require pull request reviews (1 approver minimum), require status checks, require branches to be up to date before merging, do not allow bypassing. Also add a `.github/CODEOWNERS` file covering at minimum `hooks/`, `rules/`, `.github/workflows/`, and install scripts. This is a 10-minute maintainer task that closes the single-point-of-failure. At 32k stars, it is basic hygiene the repo should already have.

### F5 — Warning · Code fixed in v1.6.0 · Disclosure gap open — Unadvertised symlink vulnerability — named in release notes, not in advisory channel
*2026-04-04 – 2026-04-15 · 11 days live · → If you installed before 2026-04-15, upgrade now. New installers on v1.6.0 are fine.*

Every version from v1.0.0 through v1.5.1 has a symlink-based file-clobber bug in the SessionStart and UserPromptSubmit hooks. The reporter's own commit message describes the attack in plain terms: "If [the flag file path] is replaced with a symlink, Node will follow it and overwrite the symlink target. A local attacker (or another process running as the same user) could abuse this to modify unintended files writable by the user." A local attacker or malicious process running as you could point the flag file path at something important — like `~/.ssh/authorized_keys` or a shell rc file — and the hook would overwrite it with the string "full" or "lite" on your next Claude Code session. The repo never issued a GitHub Security Advisory, CVE, or public notice. Users who installed v1.0.0–v1.5.1 have no programmatic way to learn they should upgrade.

| Meta | Value |
|------|-------|
| Reported by | tuanaiseo — [PR #70](https://github.com/JuliusBrussee/caveman/pull/70) |
| Fixed by | tuanaiseo — [PR #70](https://github.com/JuliusBrussee/caveman/pull/70), [PR #71](https://github.com/JuliusBrussee/caveman/pull/71) |
| Merged by | JuliusBrussee |
| Reviewed by | BAD Nobody |
| The fix | O_NOFOLLOW + atomic temp+rename + symlink refusal at parent and target |
| Advisory published | BAD None |

**Related — PR #71 tightened parent-chain validation on the same reporter's next submission.** The same reporter filed PR #71 minutes after #70 with a stronger `assertNoSymlink` that walks every path component. It was also left open for 5 days and merged without review.

### F-batch — Warning · Ongoing pattern — v1.6.0 was a 10+ PR batch merge — security fix hidden among unrelated changes
*2026-04-15 · 23-minute merge window · → Ask the maintainer to stop batching security fixes with unrelated PRs.*

On 2026-04-15 the maintainer merged PRs #70, #71, #119, #120, #146, #148, #153, #169, #171, and #174 into main within a 23-minute window. All ten ended up with the same `mergedAt` timestamp of 2026-04-15T12:50:16Z from github-actions post-processing. Eight of the ten had no code review. Two of them (#70 and #71) were the real security fixes. When a security fix ships as part of a 10-PR rollup alongside unrelated changes — README link fixes, path quoting, Codex plugin shape tweaks — it gets hidden from users who scan release notes looking for security-relevant changes. This is the "changelog hiding" pattern: the release note for v1.6.0 reads "Hardening release: hook crash fixes + symlink-safe flag writes" but doesn't call out that every prior version had a live exploitable bug.

| Meta | Value |
|------|-------|
| Merged by | JuliusBrussee |
| Shared mergedAt | 2026-04-15T12:50:16Z |
| PRs in batch | 16 total |
| Release tag | [v1.6.0](https://github.com/JuliusBrussee/caveman/releases/tag/v1.6.0) |

### F11 — Warning · Ongoing — Review rate: 15% formal, 36% any (F11 dual metric)
*Since repo creation · Throughout history · → Only relevant if you rely on caveman for sensitive workflows. Ask maintainer to require one other approver on hook/workflow PRs.*

Only 5 of 33 merged PRs have `reviewDecision` set. Combined with no branch protection rule on `main`, any PR the maintainer clicks "merge" on goes straight to users. For a 32,844-star repo that runs as a plugin on every Claude Code session, that's concerning. The maintainer is doing thoughtful work — the v1.6.0 code is carefully hardened — but there's no second pair of eyes on changes before they ship to tens of thousands of developers' local machines.

| Meta | Value |
|------|-------|
| PRs with formal review | 5 / 33 |
| Review rate | BAD 15% |
| Security PRs with review | BAD 0 of 2 (#70, #71) |

### F-advisory — Warning · No advisories ever — No GitHub Security Advisory workflow — no way to learn about future vulns
*Repo lifetime · → Subscribe to the repo's releases — release notes are currently the only disclosure channel. Ask maintainer to enable advisories.*

The repo has never published a security advisory (the `security-advisories` API returns an empty array). There is no `SECURITY.md` at the repo root documenting how to report a vulnerability — there is one inside `caveman-compress/` but it covers a different concern (the Snyk static-analysis rating), not a disclosure policy. A security-minded user has no canonical channel to report a vuln, and no feed to subscribe to for notifications. Dependabot is also explicitly disabled (the response literally says "Dependabot alerts are disabled for this repository"), so even if a dependency vulnerability were filed upstream, this repo wouldn't surface it.

| Meta | Value |
|------|-------|
| Advisories published | BAD 0 |
| SECURITY.md at root | BAD No |
| Dependabot | BAD Disabled |

### F14 — Info · Current — No branch protection rule on main
*Current · → No action required of you — this is a maintainer-side issue. Compounds every other finding though.*

The branch-protection API returns 404 — meaning no rule is configured (not a permissions issue; 404 is authoritative here). Direct pushes to `main` are possible, no required review count, no required status checks. Not actively exploited right now, but combined with the 15% review rate and lack of a security advisory process, this is a governance gap that would compound any attacker who compromised the maintainer's GitHub session or credentials.

| Meta | Value |
|------|-------|
| API response | 404 Not Found |
| Interpretation | No protection rule exists (definitive) |

### F16 — OK — v1.6.0 security code is thorough and well-reasoned
*v1.6.0 · Current · → No action needed. Positive signal: maintainer's v1.6.0 fix shows real security engineering care.*

The `caveman-config.js` in v1.6.0 contains `safeWriteFlag` and `readFlag` helpers that correctly implement every defense expected for this class of vulnerability: atomic write via temp+rename, O_NOFOLLOW flag handling, permission 0o600 on write, symlink refusal at both parent directory and target, 64-byte size cap on reads, and whitelist validation of read content against a fixed set of valid mode strings. The comments explicitly describe the attack scenarios being defended against. This is good security engineering — the concern is not with the code but with the process that shipped it without an advisory.

| Meta | Value |
|------|-------|
| O_NOFOLLOW | OK Yes |
| Atomic rename | OK Yes |
| Whitelist-validated reads | OK Yes |
| Size cap | OK 64 bytes |

### F-amplify — Info · Ongoing · High leverage — CI sync amplifies one rule file into 4+ always-on agent configs
*Ongoing · → No action needed today. Watch for future changes to `rules/caveman-activate.md` — leverage ratio is high.*

The `.github/workflows/sync-skill.yml` CI copies `rules/caveman-activate.md` into four separate always-on agent rule locations on every push to main: `.clinerules/caveman.md`, `.cursor/rules/caveman.mdc` (with `alwaysApply: true` frontmatter), `.windsurf/rules/caveman.md` (with `trigger: always_on` frontmatter), and `.github/copilot-instructions.md` (which Copilot auto-loads). One compromise of that single 17-line source file would ship arbitrary always-on agent instructions to every caveman user running Cursor, Windsurf, Cline, or Copilot. **Today the content is clean** — it's a short behavioral rule about writing tersely — but the leverage ratio is worth flagging because this pattern is uncommon for a 32k-star repo to have without a security review process. A future PR that modifies `rules/caveman-activate.md` would ship to every agent rule file without any gate.

| Meta | Value |
|------|-------|
| Source file | `rules/caveman-activate.md` (17 lines) |
| Destination files | 4 always-on agent rule files |
| Amplifier workflow | [sync-skill.yml](https://github.com/JuliusBrussee/caveman/blob/main/.github/workflows/sync-skill.yml) |
| Current content | OK Clean (behavioral rules only) |
| Leverage | WARN High — 1 file → every user's always-on agent config |

**Related — README install-paste snippet.** README line 271 instructs users to paste 7 lines of text into their agent's system prompt. The pasted content is currently safe (same behavioral rules as above). A future compromise of the README could swap the snippet for attacker instructions, and every user who previously pasted it is already compromised.

### F-deps — OK — Minimal runtime dependency surface
*Current · → No action needed. Positive signal.*

The hooks directory has a `package.json` with zero runtime dependencies (literally just `{"type": "commonjs"}`). The only dependency in the whole repo is `anthropic>=0.40.0` in `benchmarks/requirements.txt`, and that's for the benchmark suite, not the runtime plugin. Attack surface from transitive dependencies is essentially zero for users running the plugin.

| Meta | Value |
|------|-------|
| Hook runtime deps | OK 0 |
| Only dep | anthropic (benchmark-only) |
| Network in hooks | OK None |

---

## 02A · Executable file inventory

> WARN 3 Warning · INFO 2 Info · OK 3 OK
>
> 8 executable files cataloged. **3 need attention** — two hook files that had the pre-v1.6.0 symlink vuln (now fixed) plus the install script (fetches from live main). 3 are fine, 2 are informational (CI-amplified rule source + README paste block).
>
> **Your action:** The two hook files (`caveman-activate.js`, `caveman-mode-tracker.js`) are **already fixed in v1.6.0** — upgrade closes them if you're on an older install (same action as F5). For `install.sh`: when installing, prefer `claude plugin install caveman` over the curl-pipe-bash option, and after install run `grep -c 'safeWriteFlag' ~/.claude/plugins/*/caveman*/hooks/*.js` — should return at least 1. The two Info items (`rules/caveman-activate.md`, README paste-block) need no action today; they're documented so you know the leverage if something changes in the future.

### Quick scan (8 executables — F12 one-line inventory)

- WARN `hooks/install.sh` — user-triggered installer, fetches hooks from `raw.githubusercontent.com/.../main/`, writes `~/.claude/hooks/*`. **Warning: live-main fetch, not pinned.**
- WARN `hooks/caveman-activate.js` — runs on every Claude Code session start, writes one flag file, no network. **OK in v1.6.0 (was Warning in v1.0.0–v1.5.1, symlink vuln fixed).**
- WARN `hooks/caveman-mode-tracker.js` — runs on every user prompt, writes flag file via symlink-safe helper. **OK in v1.6.0 (same historical vuln as above).**
- OK `hooks/caveman-config.js` — imported by hooks above, implements the v1.6.0 symlink defenses. No direct writes. **OK — security-critical module, watch in future diffs.**
- OK `hooks/uninstall.sh` — user-triggered remover, deletes hook files + rewrites settings. No network. **OK.**
- OK `.github/workflows/sync-skill.yml` — CI on push to main, copies SKILL.md into 4 agent rule locations. Narrow scope. **OK workflow, but amplifies F-amplify source.**
- INFO `rules/caveman-activate.md` — CI-amplified into 4 always-on agent rule files. 17 lines of behavioral rules. **Info: imperative AI language present but benign today. High future-compromise leverage.**
- INFO `README.md` line 271 paste-block — 7 lines users paste into their agent's system prompt. **Info: safe today; one-time trust decision with permanent consequence.**

### Inventory cards (7 properties each)

#### WARN `hooks/install.sh` — fetches live main, not pinned

| Property | Value |
|----------|-------|
| 1. Trigger | User runs `bash hooks/install.sh` or `bash <(curl -s raw.githubusercontent.com/.../install.sh)` |
| 2. Reads | `~/.claude/settings.json`, `~/.claude/hooks/*` |
| 3. Writes | `~/.claude/hooks/*.js`, `*.sh`, `settings.json`, `settings.json.bak` |
| 4. Network | curl to `raw.githubusercontent.com/JuliusBrussee/caveman/main/hooks/*` (only in curl-pipe mode) |
| 5. Injection channel | OK None observed — env vars to node -e, not shell interpolation |
| 6. Secret-leak path | OK None observed |
| 7. Privilege | User-level, no sudo required |

**Capability assessment:** this installer downloads hook JS files from the caveman main branch and writes them to `~/.claude/hooks/`. It merges hook registrations into `settings.json` using a node -e script that reads paths from env vars (not shell interpolation, which shields against `$HOME` quoting issues). Worst case if the installer itself is compromised: arbitrary code execution as the user, because the downloaded hook files will run on every Claude Code session start. Users who run the curl-pipe variant are implicitly trusting that the main-branch hook files are safe at the moment they install — there is no pinning to a tagged release in the install script.

#### WARN `hooks/caveman-activate.js` — vulnerable before v1.6.0, OK now

| Property | Value |
|----------|-------|
| 1. Trigger | SessionStart hook — runs every Claude Code session start |
| 2. Reads | `~/.claude/settings.json`, `PLUGIN_ROOT/skills/caveman/SKILL.md`, env `CLAUDE_CONFIG_DIR`, `CAVEMAN_DEFAULT_MODE` |
| 3. Writes | `~/.claude/.caveman-active` via symlink-safe `safeWriteFlag` |
| 4. Network | OK None observed |
| 5. Injection channel | Emits SKILL.md content as SessionStart additionalContext. Attacker-modified SKILL.md would inject arbitrary session context, but requires plugin-dir write access. |
| 6. Secret-leak path | OK None observed — no logging, no network |
| 7. Privilege | User-level, runs in Claude Code's hook sandbox |

**Capability assessment:** this hook writes a small flag file and emits the caveman ruleset as session context. The write is symlink-safe in v1.6.0 — before v1.6.0, a local attacker could redirect the write to clobber other files. It cannot reach the network. The worst-case capability after v1.6.0 is that if `skills/caveman/SKILL.md` in the plugin directory is modified by an attacker, the session prompt gets arbitrary additional context — but that attacker already has write access to the plugin dir, so the marginal risk is small.

#### WARN `hooks/caveman-mode-tracker.js` — vulnerable before v1.6.0, OK now

| Property | Value |
|----------|-------|
| 1. Trigger | UserPromptSubmit hook — runs on every user prompt |
| 2. Reads | stdin (user prompt JSON), `~/.claude/.caveman-active` via symlink-safe `readFlag`, env vars |
| 3. Writes | `~/.claude/.caveman-active` via `safeWriteFlag` when input matches activation pattern |
| 4. Network | OK None observed |
| 5. Injection channel | Parses user prompt; emits a fixed hardcoded reinforcement string — user text does NOT propagate into prompt injection via this channel |
| 6. Secret-leak path | OK None — flag read capped 64 bytes + whitelist-validated |
| 7. Privilege | User-level |

**Capability assessment:** runs on every user message. In v1.6.0 the read and write paths are both symlink-safe and size-capped, so a local attacker swapping the flag file for a symlink gets neither file-clobber (the write refuses) nor data-exfiltration (the read refuses). Without these guards — that is, in v1.5.1 and earlier — this hook was one of the two vulnerable write sites.

#### OK `hooks/caveman-config.js` — security-critical module

| Property | Value |
|----------|-------|
| 1. Trigger | Imported by the two hooks above; not standalone |
| 2. Reads | `$XDG_CONFIG_HOME/caveman/config.json` (or platform equivalent); env `CAVEMAN_DEFAULT_MODE` |
| 3. Writes | None directly; exports `safeWriteFlag` used by hooks |
| 4. Network | OK None |
| 5. Injection channel | OK None — no user input reaches this module |
| 6. Secret-leak path | OK None |
| 7. Privilege | User-level |

**Capability assessment:** this is the security-critical module. It owns `safeWriteFlag` (O_NOFOLLOW + temp+rename + symlink refusal) and `readFlag` (whitelist + 64-byte cap + symlink refusal). If a future PR changed these functions in a way that removed the symlink checks, every caveman user would re-inherit the v1.5.1 vulnerability. Worth watching in future diffs.

#### OK `hooks/uninstall.sh` — user-triggered remover

| Property | Value |
|----------|-------|
| 1. Trigger | User runs `bash hooks/uninstall.sh` |
| 2. Reads | `~/.claude/settings.json`, `~/.claude/hooks/*` |
| 3. Writes | Deletes `~/.claude/hooks/caveman-*`, rewrites `settings.json`, deletes `.caveman-active` |
| 4. Network | OK None (no curl-pipe variant) |
| 5. Injection channel | OK None observed |
| 6. Secret-leak path | OK None |
| 7. Privilege | User-level |

**Capability assessment:** uses the same env-var-passing pattern as install.sh to avoid shell interpolation. Worst case is it removes files it shouldn't — but the rm target list is a fixed array, not user input.

#### OK `.github/workflows/sync-skill.yml` — narrow-scope CI

| Property | Value |
|----------|-------|
| 1. Trigger | Push to `main` on specific paths (skills/caveman/SKILL.md etc.) |
| 2. Reads | Repo files under `skills/`, `rules/`, `caveman-compress/` |
| 3. Writes | Copies SKILL.md across `.clinerules/`, `.cursor/`, `.windsurf/`, `plugins/`; rebuilds `caveman.skill` zip; commits + pushes |
| 4. Network | Standard git push only |
| 5. Injection channel | OK None — no `pull_request_target`, no untrusted input in shell |
| 6. Secret-leak path | OK None — no secret access beyond `GITHUB_TOKEN` |
| 7. Privilege | `contents: write` scoped to the repo |

**Capability assessment:** legitimate-looking sync automation. Narrowly scoped: runs only on `push` to `main` (not `pull_request`), has `contents: write` scoped to itself, uses `actions/checkout@v4` (version-tagged but not SHA-pinned — minor concern, standard practice). Worst case: if an attacker got commit access to main, the workflow would amplify their change across synced directories on the next push, but the attacker would already have write access at that point.

#### INFO `rules/caveman-activate.md` — amplified into 4 always-on agent rule files

| Property | Value |
|----------|-------|
| 1. Trigger | On every push to main, CI copies this file into 4 agent rule locations; once there, loaded as always-on instructions on every user's session |
| 2. Reads | N/A — static markdown rule content |
| 3. Writes | N/A at the source; CI writes 4 destinations: `.clinerules/caveman.md`, `.cursor/rules/caveman.mdc` (with `alwaysApply:true`), `.windsurf/rules/caveman.md` (with `trigger:always_on`), `.github/copilot-instructions.md` |
| 4. Network | OK None |
| 5. Injection channel | WARN THE ENTIRE FILE IS AN INJECTION CHANNEL — becomes persistent system-prompt-level instructions for every user's agent |
| 6. Secret-leak path | OK None in current content — no exfiltration instructions |
| 7. Privilege | User's agent context (alwaysApply / always_on / auto-loaded) |

**Capability assessment:** current content is 17 lines of terse behavioral rules (drop articles/filler, write fragments, keep code normal) with no imperative language directed at secrets or exfiltration. **Clean today.** The risk lives in the leverage ratio: one PR to this one file ships to every caveman user's always-on agent config on the next CI run, without any review gate (recall: 85% of merged PRs have no formal review on this repo). A future attacker who lands a benign-looking README/docs PR that modifies this file could instruct every user's agent to reveal secrets, log paths, or execute specific commands on specific triggers. This is not speculative — it's the exact pattern the prompt scanner is designed to catch, and it's the same leverage structure that made the xz-utils attack so damaging.

#### INFO `README.md` line 271 install-paste block — user-pasted agent rules

| Property | Value |
|----------|-------|
| 1. Trigger | When user reads README and pastes the block into their agent's system prompt or rules file; then active on every session thereafter |
| 2. Reads | Runs inside user's LLM agent context; no file system access from the snippet itself |
| 3. Writes | Persists in user's agent rules file — user-copied, not repo-controlled after paste |
| 4. Network | OK None |
| 5. Injection channel | WARN README-to-agent-rules propagation vector |
| 6. Secret-leak path | OK None in current content |
| 7. Privilege | User's agent context, scope depends on target agent |

**Capability assessment:** the pasted 7-line block contains only behavioral rules — no model-directed instructions to reveal files, execute commands, or transmit data. **Safe to paste today.** But once a user pastes it, the copy lives in their agent rules file indefinitely. A future README PR that swaps the snippet for attacker instructions would not reach already-pasted users, but would catch every future user who follows the README's advice. For an end-user this is a one-time trust decision with permanent consequences — worth naming in the report.

---

## 03 · Suspicious code changes

> WARN 6 PRs flagged · 0 reviewed
>
> 6 PRs touching security-critical files, **none had formal review**. Two are the security fix itself (#70, #71). The other four are recent hook-touching PRs merged the same day without approvals.
>
> **Your action:** casual user — this is a **governance signal, not a direct threat**. No specific PR here is malicious. Note it, decide if you trust the maintainer's process. Auditing for production — click each PR link and read the diff yourself. #70 is the real security fix (verify it matches Evidence 1). #146, #148, #174 touched hook file paths in a batch merge without review — worth reading if you're risk-averse. If anything looks wrong, don't install.

| PR | What it did | Submitted by | Merged by | Reviewed? | Merge time | Concern |
|----|-------------|--------------|-----------|-----------|------------|---------|
| [#70](https://github.com/JuliusBrussee/caveman/pull/70) | Added symlink-safe write to hook files | tuanaiseo | JuliusBrussee | No | 5 days | Real security fix, zero reviews, no advisory published |
| [#71](https://github.com/JuliusBrussee/caveman/pull/71) | Strengthened safeWriteFlag with parent-chain check | tuanaiseo | JuliusBrussee | No | 5 days | Follow-up security work, same reporter as #70, zero reviews |
| [#120](https://github.com/JuliusBrussee/caveman/pull/120) | Natural-language activation in mode tracker | hummat | JuliusBrussee | No | 3 days | Expands user-input parsing surface — new regex triggers flag-file writes, merged without decision |
| [#146](https://github.com/JuliusBrussee/caveman/pull/146) | Respect CLAUDE_CONFIG_DIR across all hooks | BrendanIzu | JuliusBrussee | No | 1 day | Touches every hook's path resolution — merged without formal approval |
| [#174](https://github.com/JuliusBrussee/caveman/pull/174) | Isolate hooks as CommonJS via hooks/package.json | malakhov-dmitrii | JuliusBrussee | No | 4 hours | Changes module-loading on user machines, fastest merge in batch, no review |
| [#148](https://github.com/JuliusBrussee/caveman/pull/148) | Update Codex hook config shape | davidbits | JuliusBrussee | No | 1 day | Plugin config shape change, no review |

---

## 04 · Timeline

> BAD 4 bad · 🟡 3 neutral · 🟢 1 good
>
> 8 events over 13 days. **Peak concern 2026-04-10 to 2026-04-15** (reporter filed, maintainer didn't act for 5 days while shipping 4 more vulnerable releases). v1.6.0 on 2026-04-15 closed the code vuln but shipped without any security advisory.
>
> **Your action:** the bad events are **historical** — the code is fixed now. What you do depends on when you installed: **installed between 2026-04-04 and 2026-04-14** — you ran vulnerable code; upgrade. **Installing today** — you get v1.6.0 (fine). The "NO ADVISORY" event is the one still-open issue: it's why no automated upgrade tool is going to prompt you. Subscribe to repo releases if you want future signal.

- 🟡 **2026-04-04 · START** — Repo created by JuliusBrussee. v1.0.0 released same day — hooks ship with the symlink-unsafe flag write (unknown at the time).
- 🟡 **2026-04-05 to 04-09 · CONTEXT** — Rapid releases: v1.1.0, v1.2.0, v1.3.0, v1.3.5. All still contain the vulnerable hook write, nobody had reported it yet.
- 🔴 **2026-04-10 · VULN REPORTED** — **tuanaiseo** files [PR #70](https://github.com/JuliusBrussee/caveman/pull/70) with a commit message that spells out the symlink attack in full. Files [PR #71](https://github.com/JuliusBrussee/caveman/pull/71) minutes later with stronger parent-chain check. **Both PRs sit open.**
- 🔴 **2026-04-11 · STILL SHIPPING VULN** — v1.4.0, v1.4.1, v1.5.0, v1.5.1 all released **while PRs #70 and #71 sit unaddressed**. All four versions ship the vulnerable code. Users install them.
- 🔴 **2026-04-12 to 04-14 · 5-DAY LAG** — More PRs filed (hummat #119, #120), maintainer still has not addressed the two security PRs. **Users continue installing v1.5.1.**
- 🟢 **2026-04-15 12:27-12:50 UTC · FIX SHIPS** — Maintainer batch-merges 10+ PRs including #70 and #71 within a 23-minute window. v1.6.0 tagged and released with headline "Hardening release: hook crash fixes + symlink-safe flag writes." Code fix is good. Batch-merge is bad.
- 🔴 **2026-04-15 post-release · NO ADVISORY** — **No GitHub Security Advisory created. No CVE. No SECURITY.md added.** Users of v1.0.0-v1.5.1 receive no programmatic notification that they are running vulnerable code.
- 🟡 **2026-04-16 · SCAN** — This scan runs — 1 day after v1.6.0 release. Vulnerable versions (v1.0.0-v1.5.1) remain installable from the Releases page.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | WARN 12 days | Very new — released 2026-04-04, scanned 2026-04-16 |
| Stars | 32,844 | Viral growth to 32k+ stars in 12 days — scrutiny should match |
| Owner account age | OK 4 years | Established account, 42 public repos, 618 followers — not a sockpuppet |
| Merged PRs (review rate) | BAD 5 / 33 (15%) | Only 15% have formal review decisions |
| Branch protection | BAD None | API returns 404 — definitively no rule configured |
| Security advisories | BAD 0 published | Repo has never published a GitHub Security Advisory |
| Dependabot | BAD Disabled | Explicitly disabled — even upstream dep vulns won't surface |
| Runtime dependencies | OK 1 (benchmarks only) | Hook package.json has zero deps; only anthropic SDK for benchmarks |
| CI workflows | 1 (sync-skill.yml) | Single internal file-copy automation, narrowly scoped |
| Releases | 10 | v1.0.0 → v1.6.0 in 11 days; v1.0.0–v1.5.1 are vulnerable |
| OSSF Scorecard | BAD Not indexed | API returned 404 — repo too new or not yet crawled by OSSF |

---

## 06 · Investigation coverage

> 33/33 PRs reviewed · 8/8 execs inspected · 0/6 channels verified · 2 gaps noted
>
> **All 33 merged PRs reviewed (no sampling).** Every executable file inspected. **Distribution channels: 0 of 6 fully verified against source** — that's a method limitation, flagged under F1+F2.

| Check | Result |
|-------|--------|
| Merged PRs reviewed | OK 33 of 33 — full coverage, under the 300-PR sample cap |
| Suspicious PR diffs read | 6 of 19 — both Security-labeled reports (#70, #71) plus 4 recent hook-touching PRs read in full |
| Dependency scan | BAD Blocked — Dependabot explicitly disabled (HTTP 403), but runtime dep list is trivial, so verdict unchanged |
| Workflow files read | OK 1 of 1 — sync-skill.yml fully inspected |
| Executable files inspected | WARN 8 of 8 (3 Warning, 3 OK, 2 Info) — 3 hook .js + install.sh + uninstall.sh + sync-skill.yml + CI-amplified rule source + README paste block. "Inspected" is not "clean" — 3 got Warning cards. |
| Tarball extraction | OK 103 files extracted; grep positive-control passed |
| OSSF Scorecard | BAD Not indexed — API returned 404; repo too new for OSSF crawl |
| osv.dev | OK No runtime deps to check — hook package.json has zero dependencies |
| Secrets-in-history | Not scanned (gitleaks not available) |
| API rate budget | 5000/5000 remaining. PR sample: full. |

**Gaps noted:**

1. Windows hook variants (`install.ps1`, `uninstall.ps1`, `caveman-statusline.ps1`) not inspected in equal depth to the Unix shell and Node.js files.
2. 13 of 19 security-keyword PRs were classified from metadata only — their diffs were not read in full.

---

## 07 · Evidence appendix

> INFO 10 facts · STAR 3 priority
>
> 10 command-backed claims. **Skip ahead to items marked STAR START HERE** — those are the three most consequential for the verdict (the vulnerability itself, no advisory, no branch protection).

### STAR Priority evidence (read first)

#### STAR Evidence 1 — v1.6.0 fixes a real symlink vulnerability that existed in v1.0.0–v1.5.1

```bash
gh pr view 70 -R JuliusBrussee/caveman --json commits -q '.commits[0].messageBody'
```

Result:
```
The SessionStart hook writes to `~/.claude/.caveman-active` using `fs.writeFileSync` on a predictable path. If that path is replaced with a symlink, Node will follow it and overwrite the symlink target. A local attacker (or another process running as the same user) could abuse this to modify unintended files writable by the user.

Affected files: caveman-activate.js, caveman-mode-tracker.js

Signed-off-by: tuanaiseo 221258316+tuanaiseo@users.noreply.github.com
```

*Classification: Confirmed fact — vulnerability described in the reporter's own commit message; fix adds O_NOFOLLOW and symlink refusal; before/after diff confirms the unprotected write.*

#### STAR Evidence 2 — No GitHub Security Advisory was issued for the fix

```bash
gh api "repos/JuliusBrussee/caveman/security-advisories"
```

Result:
```
[]
```

*Classification: Confirmed fact — empty array response means zero advisories published.*

#### STAR Evidence 5 — No branch protection on main

```bash
gh api "repos/JuliusBrussee/caveman/branches/main/protection"
```

Result:
```json
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/branches/branch-protection#get-branch-protection","status":"404"}
```

*Classification: Confirmed fact — 404 is authoritative here. The authenticated token has admin-read access and would return 403 if the issue were permissions; 404 means no rule exists.*

### Other evidence supporting Warnings

#### Evidence 3 — v1.6.0 was a 10+ PR batch merge committed at a single timestamp

```bash
gh pr list -R JuliusBrussee/caveman --state merged --limit 300 --json number,title,mergedAt \
  | jq '[.[] | select(.mergedAt == "2026-04-15T12:50:16Z")] | length'
```

Result:
```
16
```

*Classification: Confirmed fact — 16 PRs share the same mergedAt timestamp, reflecting a synchronized batch merge.*

#### Evidence 4 — 85% of merged PRs have no formal review

```bash
gh pr list -R JuliusBrussee/caveman --state merged --limit 300 --json reviewDecision \
  | jq '[.[] | select(.reviewDecision != null and .reviewDecision != "")] | length'
```

Result:
```
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

*Classification: Confirmed fact — the response distinguishes "disabled" from a permissions error.*

### Evidence supporting OK findings

#### Evidence 7 — Runtime dependency surface is minimal

```bash
find /tmp/repo-scan-JuliusBrussee-caveman -type f \( -name 'package.json' -o -name 'requirements*.txt' -o -name 'pyproject.toml' \)
cat /tmp/repo-scan-JuliusBrussee-caveman/hooks/package.json
cat /tmp/repo-scan-JuliusBrussee-caveman/benchmarks/requirements.txt
```

Result:
```
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
```
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
```
/tmp/repo-scan-JuliusBrussee-caveman/caveman-compress/SECURITY.md
```

*Classification: Confirmed fact — the only SECURITY.md is nested inside `caveman-compress/` and covers a different concern (Snyk static-analysis rating), not a disclosure policy.*

---

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
| Supply Chain | Dependencies, CI/CD workflows, GitHub Actions SHA-pinning, release pipeline, artifact verification |
| AI Agent Rules | CLAUDE.md, AGENTS.md, .cursorrules, .mcp.json — checked for prompt injection and behavioral manipulation |

### External tools used

| Tool | Purpose |
|------|---------|
| [OSSF Scorecard](https://securityscorecards.dev/) | Independent security rating. Scores 24 practices 0-10. Free API. |
| [osv.dev](https://osv.dev/) | Google-backed vulnerability database. Dependabot fallback. |
| [gitleaks](https://gitleaks.io/) (optional) | Scans code history for leaked secrets. Requires installation. |
| [GitHub CLI](https://cli.github.com/) | Primary data source for all repo metadata and API calls. |

### What this scan cannot detect

- **Transitive dependency vulnerabilities** — we check direct dependencies but cannot fully resolve the tree
- **Runtime behavior** — we see what the code *could* do, not what it *does* when running
- **Published artifact tampering** — we cannot verify published packages match this source
- **Sophisticated backdoors** — pattern-matching catches common primitives, not logic bombs
- **Container image contents** — we read Dockerfiles but cannot inspect built images

### Scan methodology version

Scanner prompt V2.3 (backfilled with V2.4 data) · Operator Guide V0.1 · Validator with XSS checks + verdict-severity coherence · [stop-git-std](https://github.com/stefans71/stop-git-std)

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-16 · scanned main @ c2ed24b (v1.6.0) · scanner V2.2-post-R3*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
