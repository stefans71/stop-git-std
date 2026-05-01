# Security Investigation: mattpocock/skills

**Investigated:** 2026-04-30 | **Applies to:** main @ `b843cb5ea74b1fe5e58a0fc23cddef9e66076fb8` | **Repo age:** 0 years | **Stars:** 47,917 | **License:** MIT

> mattpocock/skills — 47.9k-star Claude Code skill collection (22 SKILL.md, 1,815 lines), 3 months old, solo-maintained. Zero releases (rolling install), zero branch protection, no SECURITY.md (PR proposing one was closed without merging). Install delegates to vercel-labs/skills npm CLI. Skill content sampled is benign and consent-driven — risk is structural (solo + rolling + no second-human gate). Caution.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-skills.md` (+ `.html` companion) |
| Repo | [github.com/mattpocock/skills](https://github.com/mattpocock/skills) |
| Short description | Curated collection of 22 agent skills (slash commands) for Claude Code, written in Markdown. Consumed via Claude Code plugin marketplace or `npx skills@latest add mattpocock/skills`. By Matt Pocock (Total TypeScript). |
| Category | `developer-tooling` |
| Subcategory | `claude-code-skills` |
| Language | Shell |
| License | MIT |
| Target user | Developer using Claude Code who wants a curated skill set. Install via npx (delegates to vercel-labs/skills npm CLI), Claude Code plugin marketplace, or `git clone` + `scripts/link-skills.sh`. Skills become slash commands post-install. |
| Verdict | **Caution** |
| Scanned revision | `main @ b843cb5` (release tag `untagged`) |
| Commit pinned | `b843cb5ea74b1fe5e58a0fc23cddef9e66076fb8` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-30` |
| Prior scan | First scan of mattpocock/skills. 12th wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21, QuickLook 22, kanata 23, freerouting 24, WLED 25, Baileys 26). |

---

## Verdict: Caution

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Caution — F0..F4 cluster around the same root: solo-maintainer-no-protections + rolling supply chain (5 findings)</strong>
<br><em>47.9k stars + 3 months old + zero governance protections + rolling install path through a third-party npm CLI = trust-the-maintainer-and-the-CLI posture.</em></summary>

1. **F0 / F11** — mattpocock holds 87.3% commit share + 1 owner-test account = effective bus-factor 1; all 7 governance signals negative.
2. **F1** — Zero releases — install resolves to whatever HEAD points at on main at install time. Rolling distribution.
3. **F2** — No SECURITY.md (PR #67 closed without merging); no documented disclosure channel.
4. **F3** — Two-stage supply chain — `npx skills@latest add` extends trust to vercel-labs/skills npm CLI.
5. **F4** — 22 SKILL.md files (1,815 lines) form the post-install prompt surface; instructions Claude executes with user's repo permissions.

</details>

<details>
<summary><strong>ℹ Info — F5 is scanner coverage, not a property of the repo (1 findings)</strong>
<br><em>Harness scanned 1/23 markdown rule files for prompt injection.</em></summary>

1. **F5** — agent_rule_files heuristic missed the 22 SKILL.md files; only top-level CLAUDE.md scanned. V1.2.x patch candidate.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — solo maintainer (87.3% commit share + 1 owner-test account), 0% formal review on the 1 lifetime merged PR, no branch protection, no CODEOWNERS, no rulesets |
| Is it safe out of the box? | ⚠ **Partly** — README explains what the install does and lists the skills that will be activated, but install delegates trust to vercel-labs/skills npm package and 22 SKILL.md files are unsigned and unverifiable post-install |
| Do they fix problems quickly? | ⚠ **Unknown** — 3-month-old repo with 1 lifetime merged PR and 0 closed-merged security PRs to grade response cadence on; no overdue items either |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md (PR #67 proposing one was closed without merging), 0 published GHSA advisories, no documented disclosure channel |

---

## 01 · What should I do?

> 47.9k⭐ · MIT · Markdown-canonical · 5 warnings · 1 info · caution
>
> mattpocock/skills is a 3-month-old, 47.9k-star curated collection of 22 Claude Code skills, distributed as a plugin (`.claude-plugin/plugin.json`) and via `npx skills@latest add mattpocock/skills` (which routes through the vercel-labs/skills npm CLI). The repo is solo-maintained (mattpocock 87.3% commit share + a maintainer-owned test account; total contributor count: 2). Governance posture is minimal: no branch protection, no CODEOWNERS, no SECURITY.md (a PR proposing one was closed without merging), no published advisories, no Dependabot config, 1 GitHub Actions workflow (Copilot review bot). The verdict is Caution rather than Critical because (a) the underlying content is markdown — fully auditable; (b) several skills are explicitly defensive (e.g., `/git-guardrails-claude-code` blocks dangerous git commands); (c) mattpocock's public reputation (Total TypeScript, 11.9k followers, 218 public repos) is itself a meaningful trust signal. The Caution applies to the install path and post-install update model, not to the current skill content.

### Step 1: Install via the documented quickstart, OR clone and link locally for tighter trust scope (✓)

**Non-technical:** Two equivalent paths. (1) `npx skills@latest add mattpocock/skills` — fastest, but trusts both mattpocock and vercel-labs/skills (the npm CLI that drives the install). (2) `git clone` + `bash scripts/link-skills.sh` — same end result, but stays within mattpocock's trust scope only. Pick whichever matches your trust model.

```bash
npx skills@latest add mattpocock/skills  # OR: git clone https://github.com/mattpocock/skills && cd skills && bash scripts/link-skills.sh
```

### Step 2: Read the SKILL.md before invoking the skill (ℹ)

**Non-technical:** Each skill is a markdown file under skills/<bucket>/<name>/SKILL.md. When you run a slash command, Claude reads that file as instructions. Treat skill content like code — read it once, decide if you trust it, then invoke.

```bash
ls ~/.claude/skills/  # see installed skills; cat ~/.claude/skills/tdd/SKILL.md  # read one before /tdd
```

### Step 3: Run /setup-matt-pocock-skills before first use of the engineering skills (ℹ)

**Non-technical:** The README directs users to run /setup-matt-pocock-skills as the first step. It will ask you about your issue tracker, label vocabulary, and where docs/CONTEXT.md live, then write a config block to AGENTS.md/CLAUDE.md and per-section files under docs/agents/. Read what it proposes before confirming.

```bash
# In Claude Code
/setup-matt-pocock-skills
```

### Step 4: Pin to a specific commit if you want a stable surface (rolling install otherwise) (⚠)

**Non-technical:** There are no release tags. `npx skills@latest add mattpocock/skills` resolves to whatever HEAD points at on `main` at install time. If you want the same skill set tomorrow that you have today, install once and don't re-run with @latest. Or fork the repo and pin your fork.

```bash
git clone --depth 1 https://github.com/mattpocock/skills.git && cd skills && git rev-parse HEAD  # record the SHA you trust
```

### Step 5: Disclose vulnerabilities privately via GitHub's 'Report a vulnerability' UI (ℹ)

**Non-technical:** There is no SECURITY.md and no documented disclosure channel. If you find a security issue, use GitHub's built-in private vulnerability reporting at github.com/mattpocock/skills/security/advisories/new (untested but standard). Don't post publicly.

```bash
open https://github.com/mattpocock/skills/security/advisories/new
```

---

## 02 · What we found

> ⚠ 5 Warning · ℹ 1 Info
>
> 6 findings total.
### F0 — Warning · Governance — Solo-maintainer (87.3% share, 1 active human + 1 owner-test account) with zero governance protections on a 47.9k-star skill registry

*Continuous · Since repo creation (2026-02-03) · → Inspect the skill content you intend to install before linking; pin to a specific commit if you want a stable surface.*

mattpocock holds 87.3% of top-contributor commit share (55 commits to TESTPERSONAL's 8). The TESTPERSONAL account is almost certainly maintainer-owned: created 2014, no bio, no company, 9 followers, 0 public repos — the profile of a personal test/dev account, not an independent reviewer. Effective bus-factor is 1.

All 7 C20 governance signals are negative: classic branch protection HTTP 404, 0 rulesets, 0 rules-on-default-branch, no CODEOWNERS at any standard location, owner is a User account (not an Org → org rulesets n/a), and OSSF Scorecard has not indexed the repo. There is no structural second-human gate between mattpocock pushing to `main` and a user's `~/.claude/skills/` receiving that content via `npx skills@latest add` or the plugin marketplace.

Why Warning, not Critical: the C20 rule reserves Critical for solo-maintainer + no-protection + recent-release on a privileged tool, and there are no formal release tags here at all. The blast radius is real (47.9k stars, rolling distribution) but the canonical mitigation — pin to a release tag — doesn't apply because tags don't exist. Mattpocock's public reputation (Total TypeScript founder, 11.9k followers, 218 public repos, ex-Vercel) is itself a meaningful trust signal. The finding is structural, not a judgment about the maintainer.

**How to fix.** Maintainer-side: enable a branch protection ruleset on `main` requiring ≥1 approving review; add a CODEOWNERS file (even self-listed); publish a SECURITY.md naming a disclosure channel. Consumer-side: `git clone` and inspect `skills/<bucket>/<name>/SKILL.md` before linking; or pin to a specific commit SHA via the install command rather than `@latest`.

### F1 — Warning · Supply-Chain — Zero formal releases — install path resolves to whatever HEAD points at on main at install time

*Continuous · Since repo creation (2026-02-03) · → If you want a stable skill set, install once and don't re-run with `@latest`; or fork and pin.*

The repo has zero GitHub Releases and zero semantic version tags. Both documented install paths consume the latest commit on `main` at install time: `npx skills@latest add mattpocock/skills` resolves through the vercel-labs/skills CLI to whatever HEAD points at, and the Claude Code plugin marketplace (via `.claude-plugin/plugin.json`) reads the manifest from `main` at activation time.

This is the rolling-distribution pattern. Whatever you install today differs from whatever you install tomorrow if main has moved. A malicious commit to `main` reaches users at the next install boundary (or the next plugin auto-update, if that exists in the marketplace). Many Claude Code skill sets follow this pattern — it isn't unique to mattpocock/skills — but it's worth being explicit about.

Consumer-side mitigation: install once, then don't blindly re-run with `@latest`. If you need a stable surface, fork the repo and pin your fork to a SHA you've reviewed. Maintainer-side mitigation is more interesting: cutting a `v0.1.0` tag and documenting `@v0.1.0` install would let trust-conscious users opt into a pinned surface without restructuring the rolling default.

**How to fix.** Maintainer-side: cut versioned release tags (e.g. `v0.1.0`) and document `npx skills@latest add mattpocock/skills@v0.1.0` (if the upstream `skills` CLI supports SHA/tag pinning). Consumer-side: install once, then don't blindly re-run install commands; or fork and maintain your own pinned copy.

### F2 — Warning · Governance — No SECURITY.md (an external PR proposing one was closed without merging) — disclosure path is informal

*Continuous · Since repo creation (2026-02-03) · → If you find a security issue, message mattpocock directly via X/Twitter or the Total TypeScript team, since there is no documented private channel.*

PR #67 (`Create SECURITY.md for security policy`) was opened by an external contributor on 2026-04-26 and closed without merging two days later. The body was a one-line description; the PR added 21 lines and 0 deletions across 1 file. It was closed as part of a maintainer-curated batch on 2026-04-28 affecting 6+ unrelated PRs (a SECURITY policy, a typo fix, a lockfile fix, several feature additions). The pattern reads as 'tidy up the PR queue', not as 'reject this disclosure mechanism deliberately'.

But the operational effect is the same either way: there is no SECURITY.md and no documented private disclosure channel. community/profile.has_security_policy is false; published GHSA advisories: 0. A reporter who finds a security-relevant issue has no signposted path. GitHub's built-in `Report a vulnerability` UI may still work as an implicit fallback (untested), but it isn't advertised.

The closest analogue is the `.out-of-scope/` directory, which documents non-security scope decisions in prose form (e.g. why mainstream-only issue trackers, why question-limits on grilling) — a positive transparency signal, but not a security-disclosure surface. Adding a 1-page SECURITY.md (PR #67 was already drafted) closes this in minutes.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md naming a private disclosure channel (email, GitHub private advisory, or a Total TypeScript team alias) and a response-time expectation. Reviewing PR #67 as a starting point would close this in minutes. Consumer-side: if you find something, use GitHub's private-advisory UI or DM the maintainer; do not post publicly.

### F3 — Warning · Supply-Chain — Two-stage supply chain — install via `npx skills@latest` extends trust to vercel-labs/skills (a separate npm-published CLI)

*Continuous · Since README quickstart adopted · → When you run the documented install command, you are also implicitly trusting whoever publishes the npm `skills` package.*

The README's documented quickstart is `npx skills@latest add mattpocock/skills`. That command pulls the npm package `skills@1.5.3`, published by vercel-labs/skills — a separate GitHub repository, separate maintainer surface, separate npm trust scope. The vercel-labs CLI then fetches mattpocock/skills content and writes it into `~/.claude/skills/`. The trust chain is: npm registry → vercel-labs/skills publishers → vercel-labs/skills CLI logic → mattpocock/skills content.

A compromise at any layer of that chain could redirect, modify, or exfiltrate during install. Vercel is a well-known platform vendor with reasonable supply-chain hygiene, but the framing matters: a single-line install command quietly extends trust to two maintainer groups, not one. The Claude Code plugin marketplace path (via `.claude-plugin/plugin.json`) is an alternative with its own (Anthropic-mediated) trust assumptions.

The simplest mitigation stays within mattpocock's trust scope: clone the repo and run `bash scripts/link-skills.sh` (which symlinks SKILL.md files into `~/.claude/skills/`). No npm registry, no vercel-labs CLI, no plugin marketplace — just git + ln. Maintainer-side: documenting this clone+link path alongside the npx path lets users self-select their trust boundary.

**How to fix.** Consumer-side: skip the npx step. Clone mattpocock/skills directly, run `scripts/link-skills.sh` (which symlinks SKILL.md files into `~/.claude/skills/`), and you stay within mattpocock's trust scope. Maintainer-side: optionally document the clone+link path alongside the npx path so users can pick their trust boundary.

### F4 — Warning · Supply-Chain — 22 SKILL.md files (1,815 lines) form the post-install prompt surface — instructions Claude executes with full repo permissions

*Continuous · Since the first SKILL.md was added (2026-02-03) · → Read each SKILL.md before invoking the skill; treat installed skills as code, not as documentation.*

Once installed, the 22 skills become slash-commands invokable from Claude Code. When invoked, each skill loads its SKILL.md as Claude instructions and Claude executes them against the user's working repo with normal Claude Code permissions. Several skills explicitly modify environment: `/setup-pre-commit` writes to `package.json`, `.husky/`, and installs npm devDependencies; `/git-guardrails-claude-code` writes to `~/.claude/settings.json` to install hook scripts; `/setup-matt-pocock-skills` writes config blocks to `AGENTS.md`/`CLAUDE.md` plus per-section files under `docs/agents/`.

The risk is not 'malicious now' — the SKILL.md content sampled (setup-pre-commit, git-guardrails-claude-code, setup-matt-pocock-skills, tdd) is consent-driven and consistent with stated purpose. Several skills are explicitly defensive: `/git-guardrails-claude-code` blocks `git push`, `git reset --hard`, `git clean -f`, etc. before they execute. The risk is 'a future malicious commit reaches users on the next install / auto-update'.

Consumer-side mitigation is straightforward but requires intent: before linking, `cat skills/<bucket>/<name>/SKILL.md` for each skill you intend to use. Treat skill-update events as code-review events, not as silent updates. Every SKILL.md is plain markdown — fully auditable, not obfuscated. Maintainer-side: a CHANGELOG.md at the skill level (or commit messages with `[skill: ...]` prefixes) would help downstream auditability without adding tooling.

**How to fix.** Consumer-side: before linking, `cat skills/<bucket>/<name>/SKILL.md` for each skill you intend to use; install only the ones you've read. Treat skill-update events as code-review events, not silent updates. Maintainer-side: a `CHANGELOG.md` at the skill level (or commit messages with `[skill: ...]` prefixes) would help downstream auditability.

### F5 — Info · Coverage — Scanner coverage gap on plugin-shape repos — only 1 of 23 markdown rule files was scanned for prompt injection

*Continuous · Scanner harness gap · → Non-blocking. Re-running with a SKILL.md-aware scanner would close this gap.*

The harness's `code_patterns.agent_rule_files` heuristic captured the 13-line top-level `CLAUDE.md` and stopped there. The 22 SKILL.md files (1,815 lines) under `skills/<bucket>/<name>/SKILL.md` were not enumerated. As a result `prompt_injection_scan.scanned_files` is `['CLAUDE.md']` and `signal_count: 0` — but the 0-signal result reflects 1/23 file coverage, not a clean read on the full prompt surface.

The third-party Skillsmith scanner (issue #105, closed 2026-04-30) scanned the SKILL.md content with a different ruleset and surfaced one false positive — a regex match on the phrase '...the system:' at end-of-line in `skills/engineering/tdd/SKILL.md` line 64, where 'system' refers to the system under test in TDD prose. Skillsmith concluded false positive on their side, tracked auto-quarantine + pattern-tuning, and filed it informationally.

This is a property of the harness, not of mattpocock/skills. V1.2.x patch candidate: extend `code_patterns.agent_rule_files` to recursively find SKILL.md files under any `skills/` subdirectory, and feed all of them into `prompt_injection_scan.scanned_files`. Same class of fix as V13-3 C2 (deserialization language-qualifier regex) — narrow, shape-specific harness tuning.

**How to fix.** Scanner-side: extend `code_patterns.agent_rule_files` to recursively find SKILL.md files under any `skills/` subdirectory, and feed all of them into `prompt_injection_scan.scanned_files`. This is a V1.2.x-class harness patch (similar in spirit to V13-3 C2 language qualifier). Consumer-side: read the SKILL.md files yourself, or run a SKILL.md-aware tool.

---

## 02A · Executable file inventory

> mattpocock/skills ships markdown-canonical skill content (22 SKILL.md files, 1,815 lines) plus 2 small shell scripts under `scripts/`. There are no compiled binaries, no native dependencies, no package manifests. The 'execution' surface is what Claude does when a skill is invoked: skills load their SKILL.md as instructions and Claude follows them with the user's repo permissions.

### Layer 1 — one-line summary

- Primary surface: 22 SKILL.md files under `skills/<bucket>/<name>/`. Secondary surface: 2 install/utility scripts under `scripts/`. Tertiary surface: 1 plugin manifest (`.claude-plugin/plugin.json`) listing 12 promoted skills.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `skills/engineering/setup-matt-pocock-skills/SKILL.md` | agent-rule | Claude Code (Markdown → instructions) | Writes to AGENTS.md/CLAUDE.md at repo root; writes docs/agents/{issue-tracker,triage-labels,domain}.md. Asks user permission first. Reads .git/config and `git remote -v`. | None directly; instructs Claude to use `gh` or `glab` CLI for issue-tracker setup if user picks that path. | Required setup skill — the README quickstart says to run `/setup-matt-pocock-skills` after install. Modifies the user's repo config files. Consent-driven; explicit confirmation step before writing. |
| `skills/misc/git-guardrails-claude-code/SKILL.md` | agent-rule | Claude Code (Markdown → instructions) | Writes to ~/.claude/settings.json (PreToolUse hooks); installs an executable hook script under .claude/hooks/. Acts as a defensive measure — blocks `git push`, `git reset --hard`, `git clean -f`, etc. | None. | This skill is itself a defensive measure — it adds hooks that block destructive git commands. Net-positive security signal; the install action modifies the user's Claude Code settings. |
| `skills/misc/setup-pre-commit/SKILL.md` | agent-rule | Claude Code (Markdown → instructions) | Installs Husky + lint-staged + Prettier as devDependencies (npm/pnpm/yarn/bun); writes .husky/pre-commit; modifies package.json scripts. | Installs npm packages — outbound to npm registry. | Standard developer-tooling setup. Modifies user's package.json + adds devDeps + creates pre-commit hook. |
| `scripts/link-skills.sh` | shell-script | bash | Symlinks every SKILL.md from this repo into ~/.claude/skills/. Uses `mkdir -p` + `ln -sfn`. Has a guard against accidentally pointing back at this repo (would otherwise pollute the working copy). | None. | Maintainer-side install script. Used by users who clone the repo directly and want to symlink skills locally. Defensive coding — checks for circular symlinks before writing. |
| `skills/engineering/tdd/SKILL.md` | agent-rule | Claude Code (Markdown → instructions) | Instructs Claude to write tests + run them; uses red-green-refactor loop. Doesn't modify environment outside the user's chosen test directory. | None directly. Contains a `fetch()` example in mocking.md (line 44, false-positive on harness `network` family grep). | The skill flagged by the third-party Skillsmith scanner (issue #105) for a regex false-positive on the phrase '...the system:' at end-of-line. Skillsmith concluded false positive on their side. Content is benign TDD prose. |

The full set of 22 SKILL.md files is auditable via `find skills -name SKILL.md`. Treat each as code: read it before invoking the skill. Several skills (setup-matt-pocock-skills, setup-pre-commit, git-guardrails-claude-code) modify user-side files; the consent points are inside each SKILL.md.

---

## 03 · Suspicious code changes

> ✓ 2 security-concerning PRs · ℹ 5 recent merges sampled

Sample: the 1 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 0.0% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#90](https://github.com/mattpocock/skills/pull/90) | Add setup-matt-pocock-skills; rename github-triage; migrate skills to vague prose | mattpocock | mattpocock | No formal decision; 0 reviews | Self-merge |
| [#67](https://github.com/mattpocock/skills/pull/67) | Create SECURITY.md for security policy (CLOSED, not merged) | external-contrib | — | Closed without comment | Disclosure-policy PR rejected |
| [#28](https://github.com/mattpocock/skills/pull/28) | [Security] Add security lens, priority ordering, and challenge behavior to grill-me skill (CLOSED, not merged) | external-contrib | — | Closed without comment | Security-tagged PR rejected |
| [#75](https://github.com/mattpocock/skills/pull/75) | fix typo in readme (CLOSED, not merged) | external-contrib | — | Closed without comment | Trivial fix rejected |
| [#74](https://github.com/mattpocock/skills/pull/74) | Fix npx command paths in README (CLOSED, not merged) | external-contrib | — | Closed without comment | Documentation fix rejected |

---

## 04 · Timeline

> 🟡 4 neutral · 🔴 1 concerning

- 🟡 **2026-02-03 · Repo created** — Initial commit by mattpocock; first SKILL.md added
- 🟡 **2026-04-26 · SECURITY.md PR opened** — PR #67 by external contributor proposing a security policy document
- 🔴 **2026-04-28 · Batch close + first merge** — PR #67 + 5 other contributor PRs closed without merge; PR #90 (only ever-merged) self-merged by mattpocock — maintainer-curated cleanup day
- 🟡 **2026-04-30 · Skillsmith heads-up** — Issue #105 — third-party scanner reports regex FP on TDD prose; closed same day without comment
- 🟡 **2026-04-30 · Scan date** — 12th wild V1.2 scan; HEAD b843cb5e

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 47,917 | Massively popular for a 3-month-old repo |
| Forks | 3,900 |  |
| Open issues | 5 | Low; quickly triaged |
| Open PRs | 0 | Maintainer-driven curation |
| Primary language | Shell (per GitHub) — actually Markdown-canonical | GitHub heuristic misclassifies the 2 install scripts as primary |
| License | MIT |  |
| Created | 2026-02-03 | ~3 months old |
| Last pushed | 2026-04-30 | Active (scan day) |
| Default branch | main |  |
| Total contributors | 2 | Top-1 share 87.3% (mattpocock); 2nd is `TESTPERSONAL` test account |
| Solo-maintainer flag | TRUE | 87.3% > 80% threshold |
| Formal releases | 0 | Rolling-distribution model |
| Latest release | — | No releases — F1 |
| Classic branch protection | OFF (HTTP 404) |  |
| Rulesets | 0 |  |
| Rules on default branch | 0 |  |
| CODEOWNERS | Absent |  |
| SECURITY.md | Absent | PR #67 proposing one closed without merge — F2 |
| CONTRIBUTING | Absent |  |
| Code of conduct | Absent |  |
| Community health | 42% |  |
| Workflows | 1 (Copilot reviewer bot) | No CI tests, no SAST, no Dependabot |
| pull_request_target usage | 0 |  |
| CodeQL SAST | Absent |  |
| Dependabot config | Absent (.github/dependabot.yml missing) | No package manifests to scan anyway — markdown-only repo |
| PR formal review rate (lifetime sample) | 0% (1/1 self-merged) |  |
| PR any-review rate (lifetime sample) | 0% |  |
| Self-merge count | 1 of 1 (100%) | Sample size N=1 — weak signal alone |
| Total merged PRs (lifetime) | 1 | PR #90 'Add setup-matt-pocock-skills' |
| Closed-without-merge PRs (sample) | 10+ (incl. #67 SECURITY.md, #28 [Security], #75 typo) | Maintainer-curated |
| Published security advisories | 0 |  |
| Open security issues | 0 |  |
| OSSF Scorecard | Not indexed | 404 |
| SKILL.md files | 22 (1,815 lines total) | 12 promoted via plugin.json; 10 in personal/+deprecated/ |
| CLAUDE.md size | 13 lines | Top-level repo conventions only |
| Prompt-injection signals (CLAUDE.md only) | 0 | 22 SKILL.md not scanned — F5 |
| Dangerous-pattern grep families | 15 of 15 scanned, 1 hit (TDD fetch FP) | 0 hits in deserialization/exec/secrets/cmd_injection/auth_bypass/path_traversal/etc. |
| Distribution channels | 0 detected by harness | Install via npx skills@latest (vercel-labs/skills) + Claude Code plugin marketplace + clone+link |
| Documented install paths | 3 | npx, plugin marketplace, clone+link script |

---

## 06 · Investigation coverage

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete (28 fields populated) |
| `gh api` rate limit | ✅ Well under limit |
| Tarball extraction + local grep | ✅ Scanned (small repo, 87 KB) |
| OSSF Scorecard | ⚠ Not indexed (HTTP 404) |
| Dependabot alerts | ⚠ Admin scope (403); .github/dependabot.yml absent — but no package manifests to scan in any case |
| osv.dev dependency queries | ⊗ N/A — no manifest files (markdown-only repo) |
| PR review sample | ⚠ Sample size N=1 lifetime merged PR; review-rate signals are degenerate |
| Dependencies manifest detection | ⊗ N/A — markdown-only repo, no package manifests |
| Distribution channels inventory | ⚠ 0 channels detected by harness; real install paths (npx via vercel-labs/skills, plugin marketplace, clone+link) require shape-specific detection |
| Dangerous-primitives grep (15 families) | ✅ All clean except 1 FP (TDD fetch() example in mocking.md) |
| Workflows | ✅ 1 detected (Copilot review bot) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No paste-from-command blocks |
| Prompt-injection scan | ⚠ Only CLAUDE.md (1/23 markdown rule files) scanned — F5 |
| agent_rule_files enumeration | ⚠ Only top-level CLAUDE.md captured; 22 SKILL.md files missed — F5 |
| Tarball extraction | ✅ 57 files |
| osv.dev | ℹ Zero runtime dependencies |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4988/5000 remaining |

**Gaps noted:**

1. Harness `code_patterns.agent_rule_files` does not recursively enumerate SKILL.md files under `skills/<bucket>/<name>/`. Only the 13-line top-level CLAUDE.md was captured. The actual prompt-injection surface (22 files, 1,815 lines) was not scanned. F5 documents this; V1.2.x patch candidate.
2. Distribution-channel detection found 0 channels. The actual install paths are: (1) `npx skills@latest add mattpocock/skills` via the vercel-labs/skills npm CLI; (2) Claude Code plugin marketplace via `.claude-plugin/plugin.json`; (3) `git clone` + `scripts/link-skills.sh` for local symlinks. None of these matches the harness's npm/PyPI/crates.io/RubyGems/NuGet pattern set.
3. OSSF Scorecard not indexed (HTTP 404) — repo too new or not picked up by OSSF's discovery. Governance signals derived from raw `gh api` data.
4. Dependabot-alerts API required admin scope (403). Repo has no package manifests so this is moot.
5. Gitleaks secret-scanning not available on this scanner host. The 0-secrets harness result reflects only the regex-based grep pass over file content, not a full git-history scan.
6. PR review-rate signals are degenerate at N=1 lifetime merged PR. Q2 advisory color (green) reflects 'no overdue items' rather than 'demonstrated fix cadence'; Phase 4 overrides Q2 to amber on this basis (see scorecard rationale).

---

## 07 · Evidence appendix

> ℹ 10 facts · ★ 3 priority

### ★ Priority evidence (read first)

#### ★ Evidence 2 — All 7 C20 governance signals are negative: classic branch protection HTTP 404, 0 rulesets, 0 rules-on-default-branch, no CODEOWNERS at any of 4 standard locations, owner is User (not Org → org rulesets n/a), OSSF Scorecard not indexed (404).

```bash
gh api repos/mattpocock/skills/branches/main/protection; gh api repos/mattpocock/skills/rulesets
```

Result:
```text
branch_protection.classic.status: 404. rulesets.count: 0. rules_on_default.count: 0. CODEOWNERS: not found at CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS. owner_type: User. OSSF Scorecard http_status: 404 (repo not indexed by OSSF).
```

*Classification: fact*

#### ★ Evidence 5 — Documented install path is `npx skills@latest add mattpocock/skills`. The `skills` npm package (npm version 1.5.3) is published by vercel-labs/skills — a separate trust boundary from mattpocock/skills itself. Install is therefore two-stage: trust vercel-labs's npm CLI to install Matt's skills correctly.

```bash
head -40 README.md  # quickstart section; curl -s https://registry.npmjs.org/skills/latest
```

Result:
```text
README quickstart line: `npx skills@latest add mattpocock/skills`. npm package `skills@1.5.3`, repo: git+https://github.com/vercel-labs/skills.git, homepage: https://github.com/vercel-labs/skills#readme. There is also a `.claude-plugin/plugin.json` manifest at the repo root listing 12 skills, which can be consumed via Claude Code's plugin marketplace as an alternative install path.
```

*Classification: fact*

#### ★ Evidence 10 — Harness coverage gap on plugin-shape repos. The harness's `code_patterns.agent_rule_files` heuristic captured only the top-level `CLAUDE.md` (13 lines) as an agent rule file, missing the 22 SKILL.md files (1,815 lines) which form the actual prompt surface for users post-install. The `prompt_injection_scan` consequently scanned 1 file out of 23.

```bash
python3 -c 'import json; f=json.load(open("phase-1-raw.json")); print(f["phase_1_raw_capture"]["code_patterns"]["agent_rule_files"]); print(f["phase_1_raw_capture"]["prompt_injection_scan"])'
```

Result:
```text
agent_rule_files: [{path: 'CLAUDE.md', kind: 'claude', line_count: 13, ci_amplified: false}]. prompt_injection_scan: {scanned_files: ['CLAUDE.md'], injection_signals: [], signal_count: 0, scan_method: 'tarball'}. The 22 SKILL.md files under skills/ are not enumerated as agent_rule_files. This is a scanner-coverage limitation specific to the Claude Code plugin/skills shape.
```

*Classification: fact*

### Other evidence

#### Evidence 1 — mattpocock holds 87.3% top-contributor commit share (55 commits) on a 47.9k-star, 3-month-old repo. The only other contributor is `TESTPERSONAL` (8 commits, 0 public repos, 9 followers, no bio) — almost certainly a maintainer-owned test/dev account, not an independent reviewer.

```bash
gh api repos/mattpocock/skills/contributors --jq '[.[] | {login, contributions}]'
```

Result:
```text
[{login: 'mattpocock', contributions: 55}, {login: 'TESTPERSONAL', contributions: 8}]. total_contributor_count: 2. Top-1 share: 87.3% (above 80% solo-maintainer threshold). TESTPERSONAL profile: created 2014-02-12, no bio, no company, 9 followers, 0 public repos.
```

*Classification: fact*

#### Evidence 3 — Zero formal releases. The repo has no GitHub Releases, no semantic version tags. Users installing via the documented quickstart receive the latest commit on `main` at install time — no release-pinning is exposed by the install path.

```bash
gh api repos/mattpocock/skills/releases
```

Result:
```text
releases.total_count: 0. entries: []. The install model is rolling: each invocation of the install command resolves to whatever HEAD points at on `main` at that moment. There is no equivalent of pinning a release tag.
```

*Classification: fact*

#### Evidence 4 — PR #67 ('Create SECURITY.md for security policy'), opened by an external contributor, was closed 2026-04-28 without merging. community/profile reports has_security_policy=false. There are zero published GHSA security advisories in 3 months of repo lifetime.

```bash
gh api repos/mattpocock/skills/pulls/67; gh api repos/mattpocock/skills/community/profile
```

Result:
```text
PR #67 'Create SECURITY.md for security policy' — body: 'Added a security policy document outlining supported versions and vulnerability reporting.' state: closed, merged: false, additions: 21, deletions: 0, files_count: 1. closed_at: 2026-04-28T09:22:13Z. community_profile.has_security_policy: false; has_contributing: false; has_code_of_conduct: false; health_percentage: 42. security_advisories.count: 0.
```

*Classification: fact*

#### Evidence 6 — The `skills/` tree contains 22 SKILL.md files totaling 1,815 lines. Each contains markdown instructions Claude executes when the skill is invoked (e.g., `/grill-me`, `/tdd`, `/diagnose`). 12 of the 22 are listed in `.claude-plugin/plugin.json`; 10 (in `personal/` + `deprecated/`) are not promoted but still present in the repo.

```bash
find skills -name SKILL.md -exec wc -l {} +; cat .claude-plugin/plugin.json
```

Result:
```text
22 SKILL.md files. Sizes: 7-130 lines each. Total: 1,815 lines. plugin.json lists 12 paths under `engineering/` + `productivity/`. Buckets: engineering/ (10), productivity/ (3), personal/ (2), misc/ (5), deprecated/ (4). Skills perform actions like setup-pre-commit (modifies package.json + .husky/), git-guardrails-claude-code (writes ~/.claude/settings.json hooks), setup-matt-pocock-skills (writes AGENTS.md/CLAUDE.md + docs/agents/*).
```

*Classification: fact*

#### Evidence 7 — PR review posture on lifetime sample: 1 PR ever merged (#90, self-merged by mattpocock 2026-04-28, 0 reviews). Multiple recent contributor PRs were closed without merging, including PR #67 (SECURITY.md) and PR #28 ([Security] Add security lens to grill-me skill).

```bash
gh api 'repos/mattpocock/skills/pulls?state=closed&per_page=100'
```

Result:
```text
total_merged_lifetime: 1. sample of merged: PR #90 'Add setup-matt-pocock-skills; rename github-triage; migrate skills to vague prose' — merged 2026-04-28, self_merge: true, any_review_count: 0. Closed-without-merge sample includes #28 (Security label), #61, #62, #64, #65, #66, #67 (SECURITY.md), #69, #74, #75, #81 — many closed in a single batch on 2026-04-28. Pattern is maintainer-driven curation rather than collaborative review.
```

*Classification: fact*

#### Evidence 8 — Issue #105 (closed 2026-04-30) was a heads-up from a third-party scanner (Skillsmith, skillsmith.app) reporting a regex false-positive on `skills/engineering/tdd/SKILL.md` line 64 — the phrase '...the system:' at end-of-line matched their chat-role-injection pattern despite the meaning being plainly programming-domain ('the system under test'). Matt closed the issue without comment. No prompt-injection signals in the harness scan of `CLAUDE.md`.

```bash
gh api repos/mattpocock/skills/issues/105
```

Result:
```text
Issue #105 title: 'Heads-up: Skillsmith security scanner flags TDD SKILL.md (false positive — role-injection regex)'. Author: wrsmith108. State: closed. Body explains the Skillsmith regex `/(?:^|\s)(?:system|assistant|user)\s*:\s*(?:\n|$)/i` matched 'system:' at end-of-line in TDD prose; concluded false positive on their side; tracked auto-quarantine + pattern-tuning. comments: 0 (Matt closed without commenting). harness prompt_injection_scan: scanned_files=['CLAUDE.md'] (13 lines), signal_count: 0. The 22 SKILL.md files were NOT scanned by this harness (coverage gap).
```

*Classification: fact*

#### Evidence 9 — Workflow surface: 1 GitHub Actions workflow (Copilot pull-request reviewer bot, dynamic). No CI tests, no static-analysis, no Dependabot config (.github/dependabot.yml absent), no SECURITY.md, no SAST. dangerous-pattern grep found 0 hits in the deserialization/exec/secrets/cmd_injection/auth_bypass/path_traversal/etc. families. 1 hit in the `network` family — a `fetch()` example in `skills/engineering/tdd/mocking.md` documenting test mocks (false positive).

```bash
gh api repos/mattpocock/skills/actions/workflows; ls .github/
```

Result:
```text
workflows.count: 1 ('Copilot code review' — dynamic, GitHub-managed). workflow_contents.entries: [] (the Copilot bot has no checked-in YAML — it's installed via the GitHub Copilot integration). pull_request_target_count: 0. defensive_configs: dependabot.yml not present; SECURITY.md not present. dangerous_primitives.deserialization.hit_count: 0. .exec.hit_count: 0. .network.hit_count: 1 (skills/engineering/tdd/mocking.md line 44, 'getUser: (id) => fetch(`/users/${id}`)' — TDD mocking example).
```

*Classification: fact*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-30 · scanned main @ `b843cb5ea74b1fe5e58a0fc23cddef9e66076fb8` (untagged) · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
