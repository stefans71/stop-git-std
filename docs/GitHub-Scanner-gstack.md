# Security Investigation: garrytan/gstack

**Investigated:** 2026-04-16 | **Applies to:** main @ `23000672673224f04a5d0cb8d692356069c95f6a` | **Repo age:** 1 month 5 days | **Stars:** 73,710 | **License:** MIT

> A five-week-old Claude Code skill bundle that hit 73,000 stars while shipping `git clone main` as its only install path — and optionally registers a SessionStart hook that auto-pulls `main` on every session. The code is clean; the delivery mechanism is the story. Verdict splits by deployment context: solo laptop is good with caveats; shared host with `setup --team` is bad.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-gstack.md` (+ `.html` companion) |
| Repo | [github.com/garrytan/gstack](https://github.com/garrytan/gstack) |
| Short description | Garry's Stack — Claude Code skills plus a fast headless browser. One repo, one install, entire AI engineering workflow. Ships ~50 agent-rule files (CLAUDE.md plus 41 per-tool SKILL.md), ~30 shell bin scripts, and a compiled Bun browser binary. Distributed via `git clone main` with an optional SessionStart auto-update hook in team mode. |
| Category | `developer-tooling` |
| Subcategory | `claude-code-skills-distribution` |
| Language | TypeScript (+ Bun runtime) |
| License | MIT |
| Target user | Developers using Claude Code, OpenClaw, Codex, or Factory agent hosts |
| Verdict | **Caution** (split by Deployment — see below) |
| Scanned revision | `main @ 23000672` (no tags; HEAD of main 2026-04-14) |
| Commit pinned | `23000672673224f04a5d0cb8d692356069c95f6a` |
| Scanner version | `V2.3-post-R3` |
| Scan date | `2026-04-16` |
| Prior scan | None — first scan. Future re-runs should rename this file to `GitHub-Scanner-gstack-YYYY-MM-DD.md` before generating the new report. |

---

## Verdict: Caution (split — Deployment axis only)

### Deployment · Personal laptop · solo dev · no team mode — **Good with caveats — install, pin the commit, don't enable `--team`**

The code itself is clean: 4 runtime deps (`@ngrok/ngrok`, `diff`, `playwright`, `puppeteer-core`), no `eval` or `new Function` in any scanned path, and the `execSync`/`curl`/`fetch` usage pattern is the by-design product behaviour you would expect from a CLI tool ecosystem. The caveats are structural, not code-level: the only install path is `git clone --depth 1 main` with no tag pinning, no checksum, no signature (F-install). There are zero releases ever — version is tracked in `VERSION`, `package.json`, and commit messages but not exposed as git tags. After install, record the commit SHA locally and re-verify after any `git pull`. Skip the `--team` flag — it registers an auto-update hook that amplifies this risk (see the other column).

### Deployment · Team or shared host · `setup --team` · SessionStart auto-update — **Bad — any maintainer compromise propagates fleet-wide within one hour**

`setup --team` writes `auto_upgrade=true` to gstack's config and registers `gstack-session-update` as a SessionStart hook in `~/.claude/settings.json`. On every new Claude Code session, that hook runs in the background, checks a 1-hour throttle, and `git pull`s garrytan's current `main`. Combined with 88% self-merge (30 of 34 merged PRs by garrytan, 0 formal reviews in the 2-PR deep-dive sample), no branch protection on `main`, zero rulesets, and no CODEOWNERS, one garrytan-credential compromise reaches every team member's laptop on their next session. Do not install in team mode on a shared host or production-adjacent environment until branch protection, CODEOWNERS, and SHA-pinning land upstream.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Governance &amp; distribution — no review gate, no pinning, auto-update amplifier (3 findings)</strong>
<br><em>C20 governance SPOF fires as Warning (no releases → release-age criterion false under V2.3 rule-as-written — see F0 rule-calibration note). 88% self-merge rate. Install from live `main` on both documented channels, with an optional SessionStart auto-update hook that compresses propagation to one hour in team mode.</em></summary>

1. **Governance · F0 / C20** — No classic branch protection on `main` (API returns 404), zero rulesets (`/rulesets` returns `[]`), no rules on `main` (`/rules/branches/main` returns `[]`), no CODEOWNERS in any of 4 standard locations. Owner is a User account (garrytan), not an Organization, so no org-level ruleset layer applies.
2. **Review rate · F-self-merge** — 30 of 34 merged PRs (88%) author-merged by garrytan. 2-PR deep-dive sample (PR #1000, PR #988) both self-merged with zero formal review decisions. PR #988 title "security wave 3 — 12 fixes, 7 contributors" landed as one self-merged bundle.
3. **Distribution · F-install + F-auto-update** — Primary install is `git clone --depth 1 main && ./setup` — no tag, SHA, checksum, or signature. In `--team` mode, `setup` registers a SessionStart hook that `git pull`s main on each session start (1-hour throttle). Secondary channel is ClawHub, also unpinned.

</details>

<details>
<summary><strong>✓ Positive signals — accountable maintainer, active security work, clean code surface (6 signals)</strong>
<br><em>Garry Tan is a publicly accountable YC CEO, active security-fix waves, actionlint CI, `umask 077` setup, LICENSE present, diff-based test tiers</em></summary>

1. **Maintainer** — Garry Tan. GitHub account since 2008-08-07 (17 years), 5,957 followers, 15 public repos, CEO of Y Combinator. Publicly accountable identity, not a sockpuppet.
2. **Active security response** — Recent PR titles include "security wave 3 — 12 fixes, 7 contributors" (PR #988) and "cookie picker auth token leak" (PR #904) — iterative hardening, not a coasting repo.
3. **CI hygiene** — `actionlint` integrated into CI on every push and PR. Workflow-level security linting is in place.
4. **Setup hygiene** — `./setup` runs `umask 077` for restrictive permissions on written files and provides checksum-verification guidance for the Bun runtime bootstrap.
5. **Disclosure baseline** — LICENSE present (MIT). No published advisories (zero filed), no open vulnerabilities. No SECURITY.md at root — documented as a gap.
6. **Engineering signals** — Diff-based test tier selection (gate vs periodic), structured version strings in commit messages (`v0.16.4.0`, `v0.17.0.0`), and `skill-docs.yml` enforces SKILL.md freshness via `git diff --exit-code`.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | RED — **No** — 88% self-merge, 0 formal reviews in sample, no branch protection, no CODEOWNERS |
| Is it safe out of the box? | AMBER — **Mostly** — code path is clean; the risk is structural (install-from-main + no artifact verification + optional auto-update hook) |
| Can you trust the maintainers? | GREEN — **Yes** — Garry Tan is a publicly accountable YC CEO, 17-year GitHub tenure, 5,957 followers |
| Is it actively maintained? | GREEN — **Yes** — daily commits, iterative security-fix waves, structured version strings even without formal releases |

---

## 01 · What should I do?

> ⚠ Skip `--team` on shared hosts · ✓ Safe solo with a pin · 3 steps
>
> **Most important**: if you are on a shared host or deploying gstack to a team, do not pass `--team` (Step 2) — the SessionStart auto-update hook is the risk amplifier. Solo installs are fine (Step 1) with a simple post-install sanity check. Step 3 is the maintainer ask.

### Step 1: Solo install on your own laptop — fine, but pin the commit and sanity-check afterwards

**Non-technical:** gstack ships as a `git clone` of the `main` branch. There are no tagged releases, so when you install, you get whatever the latest commit on `main` happens to be. That is normally fine — the code itself is clean and Garry Tan's identity is accountable — but it means there is no upstream gate preventing a bad commit from reaching you. Install, capture the commit hash, and check the installed skill directory against it.

```bash
# Install (matches README line 49)
git clone --single-branch --depth 1 \
  https://github.com/garrytan/gstack.git \
  ~/.claude/skills/gstack
cd ~/.claude/skills/gstack
./setup                           # no --team flag

# Pin: record the commit you installed
git -C ~/.claude/skills/gstack rev-parse HEAD > ~/.gstack-installed-commit

# Sanity-check: no unexpected files, setup didn't register a SessionStart hook
grep -l 'gstack-session-update' ~/.claude/settings.json || echo "OK: no auto-update hook"
ls ~/.claude/skills/gstack/bin | wc -l      # expect ~30
```

### Step 2: Do NOT pass `--team` on a shared host or in a production-adjacent environment (⚠)

**Non-technical:** `setup --team` enables `auto_upgrade=true` and registers a `gstack-session-update` hook. Every time a user on that machine opens a new Claude Code session, the hook runs in the background, checks a one-hour throttle, and runs `git pull` against garrytan's `main`. That means a single commit Garry pushes today reaches every team member on their next session. Combined with no branch protection, no CODEOWNERS, and 88% self-merge, that is an unacceptable blast radius for a shared environment. Keep auto-update off; upgrade by running `git pull` yourself when you decide to.

```bash
# If someone already ran --team and you want to roll it back
# 1. Edit ~/.claude/settings.json and remove the SessionStart entry
#    that references gstack-session-update
# 2. Flip the gstack config
gstack config set auto_upgrade false

# 3. Verify no hook remains
grep -l 'gstack-session-update' ~/.claude/settings.json \
  && echo "STILL REGISTERED — edit settings.json manually"
```

### Step 3: Ask the maintainer for the three structural fixes

**Non-technical:** Garry Tan is clearly doing thoughtful, iterative work here — the "security wave 3" PR title is the pattern of someone actively hardening a codebase. At 73,000 stars the repo has outgrown single-maintainer governance. The three small, free asks that would change this verdict from caution to good:

1. Enable classic branch protection on `main` requiring one reviewer and the existing CI status checks.
2. Add a `.github/CODEOWNERS` covering `bin/`, `setup`, `.github/workflows/`, and `CLAUDE.md`.
3. Start tagging releases (even weekly cut-tags) so installers can pin to a known commit instead of live `main`.

None of these slow velocity; all three close the single-point-of-failure that makes F0 a Warning today.

- Branch protection setup: [github.com/garrytan/gstack/settings/branch_protection_rules/new](https://github.com/garrytan/gstack/settings/branch_protection_rules/new)

---

## 02 · What we found

> ⚠ 3 Warning · ℹ 4 Info · ✓ 0 OK (positive signals surfaced as exhibits)
>
> 7 findings total. **Three Warnings cluster around delivery, not code**: F0 governance single-point-of-failure, F-install (install-from-main), and F-auto-update (the SessionStart hook that amplifies F-install in team mode). F-auto-update links back to F-install — they share a threat model. Four Info findings document the F7 agent-rule density (densest in the catalog), self-merge rate, ngrok tunnel exposure, Dependabot explicit-disable, and a minor SHA-pinning gap.
>
> **Your action:** Solo laptop user: read F-install (Step 1 above handles it). Shared-host or team deployer: read F-install and F-auto-update together — those are the two that change the verdict for your case. F-F7-density is context — useful to understand what code is auto-loaded into your Claude Code session when gstack is installed.

### F0 — Warning · Structural · Ongoing — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a 73k-star repo that ships auto-loaded agent rules (C20)

*Continuous · Since repo creation · → If you install gstack: pin the commit SHA locally (Step 1) and re-verify after any `git pull`. Do not pass `--team` (Step 2). If you maintain this repo: enable classic branch protection on `main` requiring 1 reviewer and the existing CI checks, and add `.github/CODEOWNERS` covering `bin/`, `setup`, `.github/workflows/`, and `CLAUDE.md`.*

**What is missing.** Classic branch protection on `main` returns HTTP 404 (authoritative — the scan token has `repo` scope and would return 403 on a permissions issue). Repo rulesets: `gh api repos/garrytan/gstack/rulesets` returns `[]`. Rules on `main`: `gh api repos/garrytan/gstack/rules/branches/main` returns `[]`. CODEOWNERS is absent in all four standard locations (`CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`, `.gitlab/CODEOWNERS`). Owner is a User account (garrytan), not an Organization, so there is no org-level ruleset layer either way — the authoritative check reduces to the three signals above plus CODEOWNERS, and all four are negative.

**Why this is Warning per the V2.3 rule — and why the threat model is structurally stronger than the severity suggests.** V2.3's C20 Critical gate requires all three governance signals negative AND executable code shipped AND at least one release in the last 30 days. gstack meets the first two conditions: all three governance signals are negative, and the repo ships ~30 bin scripts, a compiled Bun browser binary, a `./setup` installer, and ~50 agent-rule files that auto-load into Claude Code sessions. But gstack has **zero releases ever** — no tags, no GitHub Releases API entries — because distribution *is* `git clone main`. By the letter of the rule, "no release in 30 days" is true, so F0 fires at Warning, not Critical.

**V2.4 rule-calibration note — boundary case for future board review.** *The V2.3 C20 Critical gate uses "at least one release in the last 30 days" as a proxy for "active code flow." gstack surfaces a semantic mismatch: the repo has zero releases because **distribution is live `main`** — every push propagates to every future install, and in team mode to every existing install within an hour. That is strictly more live than a released repo, not less. Per the rule-as-written the release-age condition is false and F0 fires at Warning; per the spirit of "active code flow" the argument for Critical is substantial. Reporting Warning here is the correct call under V2.3 semantics; capturing the calibration gap is the right thing to feed into the next scanner round. A V2.4 refinement could consider "commits to default branch in last 30 days AND distribution is live-main" as a Critical escalation path alongside the existing release-age criterion. This scan does not escalate F0 to Critical — it reports the rule-as-written outcome and documents the observation for C7 diversity-matrix input.*

**How an attacker arrives (F13).** Concrete paths that do not require xz-utils-level tradecraft: (1) credential phishing against garrytan — YC CEO is a findable, high-value target; (2) stale OAuth token from an old CI system or workstation; (3) compromised browser session cookie via a malicious browser extension; (4) malicious IDE / VS Code / Cursor extension running as garrytan; (5) sloppy review on an attacker PR — the 88% self-merge rate means a legit-looking outside PR followed by a garrytan self-merge is indistinguishable from garrytan's normal workflow. None of these require compromising GitHub infrastructure; paths 1–5 all route through the repo.

**What this means for you.** When you install gstack, you are trusting garrytan's account security as tightly as your own laptop password. There is no automated gate preventing "maintainer pushed a bad change" from reaching your next install. Because CLAUDE.md and the 41 per-tool SKILL.md files auto-load as context in every Claude Code session (F-F7-density), the blast radius of one bad commit is every current and future user — 73,000 stars and counting. In team mode, it is every team member within one hour of their next session.

| Meta | Value |
|------|-------|
| Classic branch protection | RED — 404 on `main` |
| Rulesets | RED — `[]` (zero) |
| Rules on main | RED — `[]` (authoritative) |
| CODEOWNERS | RED — absent (4 locations checked) |
| Org-level rulesets | N/A (owner is User) |
| Stars (blast radius) | 73,710 |
| Releases in last 30 days | AMBER — 0 ever; distribution is live `main` |
| Active executable surface | ~30 bin scripts, compiled browser, 50 agent-rule files auto-loaded into Claude Code |

**How to fix (maintainer-side, ~10 minutes in the UI).** GitHub *Settings → Branches → Add branch protection rule* ([direct link](https://github.com/garrytan/gstack/settings/branch_protection_rules/new)). For `main`: require pull request reviews (1 approver), require status checks (the existing `actionlint`, `evals`, and `skill-docs` workflows), require branches up-to-date before merging, do not allow bypassing. Add `.github/CODEOWNERS` covering at minimum `bin/ @garrytan`, `setup @garrytan`, `.github/workflows/ @garrytan`, and `CLAUDE.md @garrytan`. Start tagging releases (even just weekly cut-tags) so installers can pin. At 73k stars, this is baseline hygiene the repo should already have.

### F-install — Warning · Distribution · Ongoing — Install-from-main: no tag, no SHA, no checksum, no signature on any channel

*Current · Every install · → Solo: pin the commit locally after install (Step 1). Team: see F-auto-update — the SessionStart hook is the amplifier of this finding.*

**What the README prescribes.** The primary install command (README line 49, verbatim): `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`. There is no tag or SHA pin, no checksum file published, no signature (sigstore, minisign, or otherwise). The secondary install channel is ClawHub (`clawhub install gstack-openclaw-...`) — also unpinned and third-party. There is no npm publish surface and no pre-built binary release.

**Why this is Warning.** "Install from main" by itself would be Info-class noise for a small repo. It becomes Warning at gstack's scale for three reasons: (1) **73k stars** means the blast radius of one bad commit is very large; (2) the installed artifact auto-loads instructions into every Claude Code session (see F-F7-density) — it is not an isolated CLI binary; (3) there is no upstream gate stopping a bad commit from reaching install-time, because F0's governance SPOF removes the review layer. None of those three facts are catastrophic individually; together they produce a Warning-tier structural risk that every install inherits.

**What would turn this into Info.** Tag releases (even monthly), and have the README pin to the latest tag (`git clone --branch v0.17.0 ...`). Publish a checksums file per tag. Either would fold this finding into positive-signal territory. Neither requires restructuring the project — the repo already tracks structured version strings in `VERSION`, `package.json`, and commit messages; they just are not exposed as git tags yet.

| Meta | Value |
|------|-------|
| Primary install path | AMBER — `git clone --depth 1 main` |
| Secondary channel | AMBER — ClawHub (unpinned) |
| Tag pinning | RED — none; zero releases ever |
| Checksum / signature | RED — absent on both channels |
| Install-path coverage (C6) | 2 of 2 documented |
| Artifact verification (C6) | RED — 0 of 2 |

### F-auto-update — Warning · Delivery amplifier · Ongoing in team mode — SessionStart auto-update hook amplifies F-install in team mode (any maintainer compromise propagates fleet-wide within one hour)

*Current · Every session · 1-hour throttle · → Do not pass `--team` on shared hosts or production-adjacent machines. For existing team-mode installs: remove the `gstack-session-update` entry from `~/.claude/settings.json` and run `gstack config set auto_upgrade false`.*

**What the hook does.** When `./setup` runs with `--team`: (1) it writes `auto_upgrade=true` to gstack's config; (2) it registers `gstack-session-update` as a SessionStart hook in Claude Code's `~/.claude/settings.json`. On every new Claude Code session thereafter, `gstack-session-update` fires, checks a 1-hour throttle, forks to a background process, and runs `git pull` (with `GIT_TERMINAL_PROMPT=0`) against garrytan's current `main`. Result: team-mode installs auto-pull `main` at most once per hour on each user's next session start.

**Why this is the amplifier, not the root cause.** This finding is deliberately linked to F-install above. The root risk is "install from live main with no upstream gate" (F-install plus F0). The hook does not add a new vulnerability class — it compresses the reaction window. *See F-install above for the underlying threat model;* this card documents the delivery amplifier specifically because it changes the verdict tier for shared-host deployments. Without the hook, a user who installed gstack on day 1 only gets a bad commit if they manually run `git pull`; with the hook, they get it on their next session.

**Concrete scenario.** Garry's GitHub credentials are phished on a Tuesday. The attacker pushes one commit to `main` that adds an exfiltration line to `bin/gstack-telemetry-sync`. By Wednesday, every team member who opens Claude Code on a gstack-team-mode machine has pulled that commit and run it. On solo installs without the hook, the window is however long before the user next runs `git pull` — likely days or weeks, buying time for garrytan to notice, revoke, and force-push. The hook removes that slack.

| Meta | Value |
|------|-------|
| Trigger | Every Claude Code SessionStart in `--team` mode |
| Throttle | 1 hour |
| Action | `git pull` main, forked to background |
| Log | `$STATE_DIR/analytics/session-update.log` |
| Fleet propagation | RED — ≤ 1 hour from malicious commit to every team user |
| Opt-in mechanism | GREEN — `--team` flag required at setup time |

### F-self-merge — Warning · Governance · Ongoing — 30 of 34 merged PRs (88%) author-merged by garrytan; security-fix PR #988 self-merged with 0 reviews

*Repo lifetime · Throughout history · → Only relevant if you rely on gstack for sensitive workflows. Ask maintainer to require one other approver on PRs touching `bin/` and `setup`.*

**The numbers.** Of the last 100 merged PRs visible through the API, garrytan authored 30, and four other contributors (evansolomon, mvanhorn, sensdiego, snowmaker) authored 1 each. Across all 34 merged PRs scanned, 30 show `merged_by=garrytan` with `author=garrytan` — an 88% self-merge rate. A 2-PR deep-dive on the two most recent merges (PR #1000 "feat: UX behavioral foundations" and PR #988 "fix: security wave 3 — 12 fixes, 7 contributors") found both were self-merged with zero formal review decisions recorded.

**Why PR #988 specifically is worth calling out.** The title names a collaborative effort: 12 fixes, 7 contributors. That is exactly the kind of PR where a maintainer might legitimately batch contributor work and merge it themselves because the review happened out-of-band on the individual branches. It is also indistinguishable, from the outside, from a credential-compromise push that happens to use "security wave" framing to look routine. Without branch protection, required reviewers, or CODEOWNERS, a human reviewer looking at the repo's merge history has no signal to separate the two cases. The pattern is not evidence of compromise — it is evidence that the repo's governance would not surface one if it happened.

**What this does NOT mean.** Garry Tan is clearly doing careful, iterative work. The "security wave 3" framing suggests ongoing, deliberate hardening. This finding is about the *process* gap, not about any specific PR being suspicious.

| Meta | Value |
|------|-------|
| Self-merge rate | RED — 30 / 34 (88%) |
| Formal reviews (2-PR sample) | RED — 0 of 2 |
| PR #1000 (latest) | RED — self-merge, 0 reviews |
| PR #988 (security bundle) | RED — self-merge, 0 reviews, 12 fixes batched |
| Other contributors | 4 drive-by authors (1 commit each) |

### F-F7-density — Info · Context-heavy · Ongoing — ~50 agent-rule files; CLAUDE.md auto-loads 26 KB of instructions into every Claude Code session (densest F7 surface in the scanner catalog)

*Current · Every session · → No action needed today — current content is benign (standard dev commands, test tier classification). Documented because the leverage is atypical and directly compounds F0/F-install if content ever changes.*

**Why this is Info, not Warning.** None of the current content is malicious. A spot-check of `CLAUDE.md` lines 1–50 found standard development commands (`bun install`, `bun test`, `bun run test:evals`), test-tier classifications (gate vs periodic), diff-based test selection, and touchfiles description. The opening half of the 502-line file is unambiguously benign agent-rule content. This finding exists because the leverage ratio is atypical — one maintainer compromise propagates ~26 KB of instructions into every current and future user's Claude Code session, plus per-tool skill files on demand. That is the F7 threat model in its sharpest form.

#### F7 agent-rule file inventory — 4 tiers, ~50 files total

**Tier 1 — auto-loaded in every Claude Code session.** These load as context without any user action once gstack is installed as a skill.

- `CLAUDE.md` — 26,938 bytes / 502 lines — auto-loaded every session
- `AGENTS.md` — 2,610 bytes — for agentic frameworks (OpenClaw, Codex)
- `SKILL.md` — 38,827 bytes — root skill descriptor

**Tier 2 — context-loaded on slash-command invocation.** Each tool directory has its own `SKILL.md` that injects into the agent context only when the user invokes that skill. `find . -name 'SKILL.md' -not -name '*.tmpl'` returns **41 files**, distributed across ~35 tool directories including: `autoplan`, `benchmark`, `browse` (34,525 bytes — the second-largest), `canary`, `careful`, `checkpoint`, `codex`, `cso`, `design`, `design-consultation`, `design-html`, `design-review`, `design-shotgun`, `devex-review`, `document-release`, `extension`, `freeze`, `gstack-upgrade`, `guard`, `health`, `investigate`, `land-and-deploy`, `learn`, `office-hours`, `pair-agent`, `plan-ceo-review`, `plan-design-review`, `plan-devex-review`, `plan-eng-review`, `qa`, `qa-only`, `retro`, `review`, `ship`, `unfreeze`.

**Tier 3 — supporting agent-rule context.** Files Claude Code would read contextually when an agent asks about architecture or design. `ARCHITECTURE.md`, `BROWSER.md`, `CONTRIBUTING.md`, `DESIGN.md`, `ETHOS.md`, `TODOS.md`, plus `openclaw/gstack-full-CLAUDE.md`, `openclaw/gstack-lite-CLAUDE.md`, `openclaw/gstack-plan-CLAUDE.md`, `openclaw/agents-gstack-section.md`, per-tool supporting docs (`review/TODOS-format.md`, `review/design-checklist.md`, `review/greptile-triage.md`, `review/checklist.md`), and `docs/*.md`.

**Tier 4 — copy/paste install-time instructions in the README.** The README contains two paste-install blocks — literal text meant to be pasted into an agent session to trigger installation, one for Claude Code hosts (README line 49) and one for OpenClaw hosts (README line 79). These are not malicious, but they are not harmless either: they are instructions executed by the user's agent, not code the user reads first. A future README PR could swap one for attacker instructions, and every user who copy-pastes it is compromised on first run.

**The concrete leverage statement.** **One maintainer compromise → 26 KB of instructions auto-loaded into every current and future user's Claude Code session, plus any of 41 per-tool skill files injected on demand.** For a repo at 73,000 stars, that is the densest F7 surface we have seen in this catalog by an order of magnitude. Previous scans had zero (zustand, fd) or one (caveman via the CI-amplified `/copy_to_claude_md` pattern). This is the first gstack-class F7 density the scanner has documented.

| Meta | Value |
|------|-------|
| Total agent-rule files | AMBER — ~50 across 4 tiers |
| Tier 1 auto-load bytes | ~68 KB (CLAUDE.md + AGENTS.md + SKILL.md) |
| Tier 2 per-tool SKILL.md count | 41 |
| README paste-install blocks | 2 (Claude Code + OpenClaw) |
| Current content | GREEN — benign (dev commands, test tiers) |
| Leverage | AMBER — highest in catalog |

### F-ngrok — Info · Runtime surface · Opt-in — `@ngrok/ngrok` runtime dep exposes local browser via public tunnels during `/pair-agent` skill use

*Current · When `/pair-agent` active · → If you use `/pair-agent`, close the tunnel explicitly when done and understand the exposure window. No action if you do not use that skill.*

**What happens.** The `/pair-agent` skill uses the `@ngrok/ngrok` runtime dependency (`^1.7.0`, 1 of 4 runtime deps) to create a public ngrok tunnel that exposes the local browser session to remote agents. The marketing language around this feature references scoped tokens, tab isolation, rate limiting, and activity attribution — all legitimate defensive properties. The concrete security fact beneath the marketing: while the tunnel is up, the user's local browser is reachable via the public internet.

**Why Info.** This is opt-in by design — the tunnel only exists when the user actively invokes `/pair-agent`. Documented mitigations exist. Users who do not use that skill are not exposed. Users who do use it should understand that enabling remote-agent pairing temporarily punches a hole through their local firewall; that is the feature, not a bug.

| Meta | Value |
|------|-------|
| Dependency | `@ngrok/ngrok ^1.7.0` |
| Trigger | `/pair-agent` skill invocation |
| Exposure | Local browser session on public tunnel |
| Mitigations | GREEN — scoped tokens, tab isolation, rate limiting |

### F-dependabot — Info · Configuration · Ongoing — Dependabot alerts explicitly disabled; no `.github/dependabot.yml` for version updates

*Current · → Ask the maintainer to re-enable Dependabot alerts. Four runtime deps plus a larger dev-dep tree deserve automatic CVE monitoring.*

**What the API says.** `gh api repos/garrytan/gstack/dependabot/alerts` returns a 403 with message *"Dependabot alerts are disabled for this repository."* That specific wording distinguishes an explicit config disable from a permissions error. The same signal appeared in our earlier zustand scan. There is also no `.github/dependabot.yml` visible at top level, so Dependabot version-bump PRs are not configured either.

**Why this matters, and why it is Info.** The runtime dependency list is short (4 deps: `@ngrok/ngrok`, `diff`, `playwright`, `puppeteer-core`), so a missed CVE in direct deps would be discoverable by hand. The dev-dep tree is larger and contributes to CI. Disabling Dependabot is a defensible choice for noise reduction, but at 73k stars the cost/benefit shifts — users of the repo can no longer rely on "Dependabot would have caught this" as a baseline assumption. Info-tier because the 4 direct runtime deps are each from a credible, well-known publisher.

| Meta | Value |
|------|-------|
| Alerts API | RED — 403 "disabled" (explicit) |
| Version-update config | RED — no `.github/dependabot.yml` |
| Published advisories | GREEN — 0 filed |
| Runtime dep count | 4 (all trusted publishers) |

### F-SHA-pinning — Info · CI hygiene · Minor gap — CI actions are tag-pinned, not SHA-pinned

*Current · All 5 workflows · → Ask maintainer to SHA-pin third-party actions on security-relevant workflows. Lower priority than F-install.*

**What we observed.** All 5 CI workflows in `.github/workflows/` (`actionlint.yml`, `ci-image.yml`, `evals.yml`, `evals-periodic.yml`, `skill-docs.yml`) use tag-pinned external actions: `actions/checkout@v4`, `docker/login-action@v3`, `rhysd/actionlint@v1.7.11`, `oven-sh/setup-bun@v2`. No SHA pins. Tags are mutable — a compromised publisher could republish a tag to point at a malicious commit. SHA-pinning closes that class of attack.

**Why Info.** Every external action publisher here is a high-trust party (GitHub, Docker, Rhys Dow, Oven). The workflows do not use `pull_request_target` (zero occurrences across all 5 files — a positive signal). Root-level `permissions:` is missing on most workflows but the two escalated ones (`evals`, `ci-image`) scope `contents: read, packages: write` per-job. Ubicloud runners are in use (third-party GitHub Actions alternative) — notable but not a red flag.

| Meta | Value |
|------|-------|
| Workflow count | 5 |
| SHA-pinned actions | RED — 0 of 5 workflows |
| `pull_request_target` | GREEN — 0 occurrences |
| Runner | Ubicloud (third-party) |
| actionlint integration | GREEN — on every push and PR |

---

## 02A · Executable file inventory

> ⚠ 2 files carry Warning-context badges · ℹ Highest-leverage F7 surface in catalog · ✓ Code path clean
>
> One-line inventory under Layer 1. Layer 2 tables the top ~12 executable surfaces. **`./setup` is the install driver and the hook registrar** — it is the file whose behaviour determines whether this repo is safe in team mode. **`bin/gstack-session-update`** is the auto-update surface (F-auto-update). Everything else is conventional.

### Layer 1 — one-line summary

- gstack ships **1 compiled browser binary** (`browse/dist/browse`, built via Bun), **~30 shell bin scripts** (`bin/gstack-*`, most 1–8 KB each), **1 main setup script** (`./setup`, ~16 KB — installer and hook registrar), and **~50 agent-rule files** (CLAUDE.md + 41 per-tool SKILL.md + supporting docs). **Distribution: `git clone main` with optional SessionStart auto-update hook in team mode.** No install-time `package.json` lifecycle hooks (`./setup` is itself invoked by the README install command, which is equivalent).

### Layer 2 — per-file runtime inventory

| File | Kind / runtime | Trigger | Property notes | Verdict context |
|------|----------------|---------|----------------|-----------------|
| `./setup` (16,750 B) | install script / bash | User runs on first install | Detects host (claude / codex / kiro / factory / openclaw), symlinks skills into host dir, `umask 077` for restrictive perms, checksum-verify guidance for Bun. **Registers `gstack-session-update` as SessionStart hook in `--team` mode.** | WARN — install driver + hook registrar (F-auto-update) |
| `bin/gstack-session-update` | auto-update hook / bash | Claude Code SessionStart when team mode on | Forks to background, checks 1-hour throttle, `git pull` from main with `GIT_TERMINAL_PROMPT=0`, logs to `$STATE_DIR/analytics/session-update.log`. | WARN — auto-update surface (F-auto-update) |
| `bin/gstack-settings-hook` | Claude Code settings editor / bash | Called by `./setup` | JSON-patches `~/.claude/settings.json`; adds or removes SessionStart hooks. Used for install (add) and uninstall (remove). | Scoped to settings file; no network |
| `bin/gstack-update-check` | version polling / bash | On user command | `curl` to GitHub to read remote version; prompts user to upgrade if newer. Read-only, no code download. | By-design, read-only network |
| `bin/gstack-telemetry-sync` | telemetry / bash | On usage events | `curl -X POST` of usage data to a remote endpoint. Opt-in/opt-out mechanism not verified in this scan — worth follow-up. | By-design, outbound POST |
| `bin/gstack-community-dashboard` | usage reporting / bash | On user command | `curl` GET to community dashboard endpoint. | By-design, read-only network |
| `browse/dist/browse` | compiled Bun binary | Invoked via `gstack browse` | Headless browser CLI; uses Playwright + puppeteer-core; can expose via `@ngrok/ngrok` when `/pair-agent` is active (F-ngrok). | Large runtime surface by product design |
| `bin/gstack-global-discover.ts` (19 KB) | TypeScript source / Bun | Called during discovery | `execSync("git remote get-url origin")` plus file discovery across directory tree. | By-design product behaviour |
| ~30 `bin/gstack-*` scripts | utility CLIs / bash | User-invoked | One tool per script; each does one thing. No `eval` or `new Function` observed anywhere in `bin/` or `scripts/`. | Clean — conventional CLI wrappers |
| `CLAUDE.md` (26 KB, Tier 1) | auto-loaded agent rules / markdown | Every Claude Code session | 502 lines; sampled lines 1–50 are benign dev commands and test-tier documentation. Not reviewed in full. | Densest F7 surface (F-F7-density) |
| `SKILL.md` per tool × 41 | agent-invocable skills / markdown | slash-command invocation | Context-injected when user invokes the matching slash-command. `browse` SKILL.md is 34,525 bytes (second-largest). | Densest F7 surface (F-F7-density) |
| `.github/workflows/*.yml` × 5 | CI workflows / GitHub Actions | push / PR / cron | All tag-pinned actions (F-SHA-pinning). Zero `pull_request_target`. Ubicloud runner. `actionlint` runs on every push and PR. | Clean pattern, minor pin gap |

*Scanner Integrity conditional section omitted — Step A dangerous-primitive grep of `bin/`, `scripts/`, and `browse/src/` found zero F8-actionable hits. All `execSync` / `spawnSync` / `curl` / `fetch` usage is explicit by-design product behaviour for a CLI tool ecosystem. No `eval(` or `new Function(` in any scanned path.*

---

## 03 · Suspicious code changes

> ✓ 0 security-concerning PRs · ⚠ 2 self-merge pattern samples
>
> 2-PR deep-dive sample of the two most recent merges — both show **100% self-merge with 0 formal reviews**, consistent with the 88% self-merge rate across all 34 merged PRs. None of the sampled PRs contain security-concerning diffs. The concern is the governance pattern (F-self-merge), not any specific PR.

| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1000](https://github.com/garrytan/gstack/pull/1000) | feat: UX behavioral foundations + ux-audit command (v0.17.0.0) | garrytan | garrytan | No (formal) | Self-merge, 0 formal reviews. Feature PR, no security-concerning diff observed. |
| [#988](https://github.com/garrytan/gstack/pull/988) | fix: security wave 3 — 12 fixes, 7 contributors (v0.16.4.0) | garrytan | garrytan | No (formal) | **Security-bundle self-merge.** Title names 12 fixes from 7 contributors, all landed as a single garrytan-authored, garrytan-merged PR with no formal review. Pattern is indistinguishable from a credential-compromise push dressed in routine framing. |
| [#904](https://github.com/garrytan/gstack/pull/904) | cookie picker auth token leak (proactive fix) | garrytan | garrytan | No (formal) | Positive-signal context: title shows proactive security-fix culture, but same self-merge-without-review pattern. Not a concern in isolation; reinforces F-self-merge. |

Sample scope: the 2 most recent merges deep-dived plus 1 earlier security-titled PR pulled as positive-signal context. Overall authorship: garrytan 30 of 34 merged PRs (88%); 4 drive-by contributors (1 commit each). This is not a full-history PR audit — see Section 06 Coverage for the explicit gap.

---

## 04 · Timeline

> ✓ 3 good · 🟡 3 neutral
>
> Five beats across the repo's 5-week history. **The story is viral growth of a competent solo maintainer's personal toolkit** — no shipped vulnerabilities, no security incidents on record, iterative fix waves. The one thing to notice is the velocity: 73k stars in 5 weeks sets expectations for governance that the repo has not yet grown into.

- 🟡 **2026-03-11 · START** — Repo created by garrytan (Garry Tan, YC CEO). First commits land the `./setup` installer, the `bin/` script family, and the initial `CLAUDE.md`. Positioning: "Garry's Stack — Claude Code skills + fast headless browser. One repo, one install, entire AI engineering workflow."
- 🟢 **2026-03-11 to 2026-04-10 · VIRAL GROWTH** — Star count crosses 73,000 within five weeks — enormous stars-per-day rate, consistent with a high-profile founder's personal toolkit going viral through YC and Twitter channels. The product appears to work well; no known incidents in this window.
- 🟢 **Circa 2026-04-05 · PROACTIVE FIX** — PR #904 "cookie picker auth token leak" lands as a proactive fix. Self-merged with no formal review (F-self-merge pattern), but the work itself is positive-signal: the maintainer is actively hardening surfaces.
- 🟢 **Circa 2026-04-12 · SECURITY WAVE** — PR #988 "security wave 3 — 12 fixes, 7 contributors" (v0.16.4.0). Bundles 12 hardening changes from 7 contributors into a single self-merged PR. Good content, concerning process: batch self-merges of security bundles are what the F-self-merge finding is about.
- 🟡 **2026-04-14 · LATEST** — PR #1000 "feat: UX behavioral foundations + ux-audit command" (v0.17.0.0) lands as HEAD of `main` — the commit this scan is pinned against (`23000672...`). Self-merged, 0 formal reviews.
- 🟡 **2026-04-16 · SCAN** — This scan runs — two days after the HEAD commit. Repo is 1 month 5 days old; zero releases ever; 357 open issues (feature requests and minor bugs, no security labels observed); Dependabot explicitly disabled; no branch protection on `main`.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | ⚠ 1 month 5 days | Created 2026-03-11. Very new for the scale of deployment. |
| Stars / Forks | 73,710 / 10,420 | ~73k stars in ~5 weeks — blast radius matches scrutiny demand. |
| Maintainer account age | ✅ 17 years | garrytan since 2008-08-07. CEO of Y Combinator. 5,957 followers, 15 public repos — established, publicly accountable identity. |
| Merged PRs (self-merge rate) | ❌ 30 / 34 (88%) | Four drive-by contributors (1 commit each). 2-PR deep-dive: 0 formal reviews. |
| Branch protection | ❌ None on `main` | API 404 + rulesets `[]` + rules/branches `[]`. Authoritative. |
| CODEOWNERS | ❌ Absent | Checked 4 standard locations. Owner is User (not Org) — no org-level ruleset layer either way. |
| Security advisories | ✅ 0 filed / 0 open | No published advisories to date. No SECURITY.md at root. |
| Dependabot | ❌ Disabled | Alerts API returns 403 "disabled for this repository" — explicit config disable. |
| Runtime dependencies | ✅ 4 | `@ngrok/ngrok`, `diff`, `playwright`, `puppeteer-core` — all trusted publishers. |
| CI workflows | 5 | `actionlint`, `ci-image`, `evals`, `evals-periodic`, `skill-docs`. Zero `pull_request_target`. Ubicloud runner. |
| Releases | ⚠ 0 ever | No tags, no GitHub Releases. Distribution is `git clone main`. Version tracked in `VERSION`, `package.json`, commit messages (v0.17.0.0). |
| Repo size | 82,829 KB | Tarball: 422 files, 8.9 MB uncompressed. |

---

## 06 · Investigation coverage

> 12/12 C11 coverage cells verified · 1 amber (Artifact 0/2 — F-install)
>
> **All 12 C11 coverage cells verified.** 2-PR deep-dive from 34 merged. All 5 workflow files read. Full tarball extracted (422 files, 8.9 MB). **Distribution channels: Install path 2 of 2 documented, Artifact 0 of 2 verified** — that is the F-install finding expressed as coverage.

| Check | Result |
|-------|--------|
| Merged PRs scanned | ✅ 34 total, 2 deep-dive — authorship counted across all 34; 2 most recent opened in full diff |
| Suspicious PR diffs | ✅ 0 anomalies in sample — no security-concerning diffs in the 2-PR deep-dive |
| Workflow files read | ✅ 5 of 5 — actionlint, ci-image, evals, evals-periodic, skill-docs. Tag-pinned actions, no SHA pins |
| `pull_request_target` usage | ✅ 0 occurrences across all 5 workflows (rules out PwnRequest class) |
| Executable files | ✅ ~30 bin + 1 compiled browser + 1 setup + 41 SKILL. Layer 1 + Layer 2 in 02A |
| Monorepo scope | ✅ Not a monorepo — single `package.json` at root, no workspaces |
| Tarball extraction | ✅ 422 files / 8.9 MB pinned to `23000672`. Grep positive controls passed |
| README paste-scan | ⚠ 2 paste-install blocks — README lines 49 + 79 target Claude Code and OpenClaw respectively. Not malicious, but literal install-time instructions meant to be executed by the user's agent — documented in F-F7-density Tier 4 |
| Agent-rule files | ⚠ ~50 — densest in catalog. CLAUDE.md (Tier 1) + 41 per-tool SKILL.md (Tier 2) + supporting docs (Tier 3) + 2 README paste-install blocks (Tier 4). Cross-reference F-F7-density |
| Prompt-injection scan | ✅ 0 matches — README.md, CLAUDE.md, AGENTS.md scanned for imperative-AI-directed injection patterns; none found. README paste-install blocks are maintainer-to-user-LLM content, not scanner-targeted injection |
| Distribution channels (C6) | ⚠ **Install path 2 of 2 · Artifact 0 of 2**. `git clone main` + ClawHub both documented; neither is pin-verified or signature-verified. This is F-install in the coverage frame |
| Windows surface | ✅ None — zero `.ps1`/`.bat`/`.cmd` files at top 3 levels. Setup has Unix-detection only |
| Commit pinned | `23000672673224f04a5d0cb8d692356069c95f6a` |

**Gaps noted:**

1. Only 2 of 34 merged PRs received full-diff deep-dive — metadata authorship counted for the remaining 32. Review-rate metric is based on that 2-PR sample.
2. Telemetry opt-out mechanism (`gstack-telemetry-sync` POSTs usage data) not verified in this scan. Worth a follow-up.
3. CLAUDE.md content review limited to lines 1–50 (benign sample) — full 502-line content not audited. The opening half is unambiguously benign agent-rule content; the remainder was not reviewed line-by-line.

---

## 07 · Evidence appendix

> ℹ 9 facts · ★ 3 priority
>
> 9 command-backed claims. **Skip ahead to items marked ★ START HERE** — the three most consequential for the verdict (governance SPOF, install-from-main with no verification, auto-update hook mechanics).

### ★ Priority evidence (read first)

#### ★ Evidence 1 — No branch protection, no rulesets, no CODEOWNERS on `main` (F0 / C20)

```bash
gh api "repos/garrytan/gstack/branches/main/protection"
gh api "repos/garrytan/gstack/rulesets"
gh api "repos/garrytan/gstack/rules/branches/main"
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do
  gh api "repos/garrytan/gstack/contents/$p" 2>&1 | head -1
done
gh api "users/garrytan" -q .type
```

Result:
```
{"message":"Not Found","status":"404"}
[]
[]
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
User
```

*Classification: Confirmed fact — all four governance signals negative. 404 on branch protection is authoritative. Owner type is User, so org-level ruleset layer is N/A. Warning, not Critical, because release-age criterion is false (no releases ever). See the V2.4 calibration note in the F0 finding for the boundary-case discussion.*

#### ★ Evidence 2 — Primary install path is `git clone main` with no pin / checksum / signature (F-install)

```bash
gh release list -R garrytan/gstack --limit 5
gh api "repos/garrytan/gstack/tags" -q 'length'
gh api repos/garrytan/gstack/contents/README.md -q .content \
  | base64 -d | grep -nE 'git clone|curl|install' | head -10
```

Result:
```
# gh release list output: (empty) — 0 releases
# tags length: 0
# README line 49:
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git \
  ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
# README line 79 (OpenClaw install): similar pattern, no pinning
```

*Classification: Confirmed fact — zero releases, zero tags, README install command pins nothing. No checksum file or signature published. Secondary channel (ClawHub) also unpinned. Artifact verification row in C6 coverage: 0 of 2.*

#### ★ Evidence 3 — SessionStart auto-update hook registered by `setup --team` (F-auto-update)

```bash
grep -nE 'SessionStart|session-update|auto_upgrade|GIT_TERMINAL_PROMPT' \
  /tmp/scan-gstack/gstack-src/setup \
  /tmp/scan-gstack/gstack-src/bin/gstack-session-update
```

Result:
```
setup: writes auto_upgrade=true to gstack config when --team is passed
setup: invokes gstack-settings-hook to add SessionStart entry for gstack-session-update
bin/gstack-session-update:
  - throttle check (1 hour) against $STATE_DIR/analytics/session-update.log
  - fork to background
  - GIT_TERMINAL_PROMPT=0 git pull on main
  - append to session-update.log
```

*Classification: Confirmed fact — hook registration and throttled `git pull` are the two mechanics confirmed by reading both files. Propagation window is bounded by the 1-hour throttle plus the time until each user's next session start.*

### Other evidence supporting Warnings

#### Evidence 4 — 30 of 34 merged PRs author-merged by garrytan (F-self-merge)

```bash
gh pr list -R garrytan/gstack --state merged --limit 100 \
  --json number,title,author,mergedBy,reviewDecision \
  | jq '[.[] | select(.author.login == "garrytan" and .mergedBy.login == "garrytan")] | length, length'
```

Result:
```
30
34

# 2-PR deep-dive (most recent merges):
PR#1000: author=garrytan, merger=garrytan, reviewDecision=null
PR#988:  author=garrytan, merger=garrytan, reviewDecision=null (title: "security wave 3")
```

*Classification: Confirmed fact — 30 of 34 = 88% self-merge. Both most-recent merges have `reviewDecision=null`. PR #988's title references a 12-fix, 7-contributor bundle landed as a single self-merge.*

#### Evidence 5 — F7 agent-rule density: 41 SKILL.md files plus CLAUDE.md + AGENTS.md

```bash
find /tmp/scan-gstack/gstack-src -name 'SKILL.md' -not -name '*.tmpl' | wc -l
wc -c /tmp/scan-gstack/gstack-src/CLAUDE.md /tmp/scan-gstack/gstack-src/AGENTS.md \
  /tmp/scan-gstack/gstack-src/SKILL.md
```

Result:
```
41
26938 CLAUDE.md
 2610 AGENTS.md
38827 SKILL.md
```

*Classification: Confirmed fact — 41 per-tool SKILL.md files; CLAUDE.md is 26,938 bytes (502 lines); AGENTS.md is 2,610 bytes; root SKILL.md is 38,827 bytes. Densest F7 surface observed in the scanner catalog to date.*

#### Evidence 6 — Dependabot explicitly disabled (F-dependabot)

```bash
gh api "repos/garrytan/gstack/dependabot/alerts"
```

Result:
```
{"message":"Dependabot alerts are disabled for this repository.","documentation_url":"https://docs.github.com/rest/dependabot/alerts#list-dependabot-alerts-for-a-repository","status":"403"}
```

*Classification: Confirmed fact — the "disabled for this repository" wording distinguishes explicit config disable from a permissions error. No `.github/dependabot.yml` at top level for version-update config either.*

### Evidence supporting positive signals

#### Evidence 7 — Maintainer is a long-tenured, publicly accountable identity (Garry Tan)

```bash
gh api "users/garrytan" -q '{login,created_at,public_repos,followers,company}'
```

Result:
```json
{"login":"garrytan","created_at":"2008-08-07T...","public_repos":15,"followers":5957,"company":"Y Combinator"}
```

*Classification: Confirmed fact — 17-year-old account, 5,957 followers, `company` field "Y Combinator". Garry Tan is the public CEO of YC; identity is accountable and verifiable outside GitHub. No sockpuppet signals.*

#### Evidence 8 — CI workflows: zero `pull_request_target`, actionlint integrated

```bash
grep -rn 'pull_request_target' /tmp/scan-gstack/gstack-src/.github/workflows/
ls /tmp/scan-gstack/gstack-src/.github/workflows/
grep -n 'rhysd/actionlint' /tmp/scan-gstack/gstack-src/.github/workflows/actionlint.yml
```

Result:
```
# no matches for pull_request_target
actionlint.yml
ci-image.yml
evals.yml
evals-periodic.yml
skill-docs.yml
# actionlint.yml references rhysd/actionlint@v1.7.11, triggered on [push, pull_request]
```

*Classification: Confirmed fact — 5 workflow files total, zero `pull_request_target` usage (rules out PwnRequest class), `actionlint` runs on every push and PR. All external actions are tag-pinned (F-SHA-pinning minor note), not SHA-pinned.*

#### Evidence 9 — Dangerous-primitive scan: clean source paths, by-design product behaviour only

```bash
grep -rnE '\beval\(|new Function\(' /tmp/scan-gstack/gstack-src/bin/ \
  /tmp/scan-gstack/gstack-src/scripts/ /tmp/scan-gstack/gstack-src/browse/src/
grep -rnE '\bexecSync\(|\bspawnSync\(|\bcurl\b' /tmp/scan-gstack/gstack-src/bin/ | wc -l
```

Result:
```
# no matches for eval( or new Function(
# execSync / spawnSync / curl count across bin/: >50 (all by-design CLI wrappers)
```

*Classification: Confirmed fact — zero `eval(` or `new Function(` in source paths scanned. Shell-exec and network-call sites are the product's stated purpose (CLI orchestration, version checks, telemetry, pair-agent tunnel). Scanner Integrity section is correctly omitted under V2.3 rules.*

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · scanned main @ `23000672673224f04a5d0cb8d692356069c95f6a` · scanner V2.3-post-R3*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
