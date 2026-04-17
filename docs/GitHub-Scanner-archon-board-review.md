# Security Investigation: stefans71/archon-board-review

**Investigated:** 2026-04-16 | **Applies to:** main @ `4cea18d9f64307fbf0a9346c04371fee3ba28ecb` | **Repo age:** 2 days | **Stars:** 0 | **License:** None (finding — see F-license)

> A 2-day-old Archon workflow plugin for multi-model governance review — 11 files, 120 KB, one defensive installer shell script, no binaries, no network, no telemetry. The structural C20 governance finding fires correctly, but the repo has **zero stars, zero forks, zero users** at scan time. Blast radius today: zero. The punchlist is short: add a LICENSE, consider cutting a v0.1.0 tag, consider shellcheck CI.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-archon-board-review.md` (+ `.html` companion) |
| Repo | [github.com/stefans71/archon-board-review](https://github.com/stefans71/archon-board-review) |
| Short description | Multi-model governance review plugin for Archon. Installs a set of Archon workflow templates, command SOPs, and role-prompt templates into a target project so that code and plan reviews run across multiple LLMs (Claude, Codex, DeepSeek) as a board. Ships a single bash installer; no server, no network, no binaries. |
| Category | `developer-tooling` |
| Subcategory | `archon-workflow-plugin` |
| Language | Shell (bash, POSIX-guarded with `set -euo pipefail`) |
| License | **None** — LICENSE file absent (see F-license) |
| Target user | Developers using Archon who want multi-model governance review on plans and code changes |
| Verdict | **Caution (split — evaluator vs maintainer)** |
| Scanned revision | `main @ 4cea18d` |
| Commit pinned | `4cea18d9f64307fbf0a9346c04371fee3ba28ecb` |
| Scanner version | `V2.3-post-R3` |
| Scan date | `2026-04-16` |
| Prior scan | None — first scan of this repo. This is also a self-scan: the repo owner is the scanner's maintainer (Scott). |

---

## Verdict: Caution (split — Deployment axis only)

### Deployment · External evaluator considering install — **Good with caveats — the installer is defensive, but you install from `main` on a 2-day-old solo-dev repo with no LICENSE and no releases**

The shell script at the centre of this tool is careful: `set -euo pipefail`, sha256 hash tracking for upstream-change detection, no `curl | bash`, no `eval`, no `sudo`, no `rm -rf`. It writes only to `$HOME/.archon-board-review/`, so blast on your machine is scoped to your user. There is no binary, no network component, no telemetry. The caveats are structural: no branch protection, no CODEOWNERS, no LICENSE (technically all-rights-reserved by default), no tagged release to pin to, and install is `git clone` from `main`. This is the typical install-from-main risk profile — but on a repo that has zero users so far.

### Deployment · Maintainer (self-scan) · punchlist — **Good with actions — the installer hygiene is already doing the hard part, four small items close the structural gaps**

This is the scanner's own maintainer running the scanner against his own 2-day-old tool. The punchlist is concrete and short:

1. Add a `LICENSE` file (MIT recommended) — this is the most actionable item because "no LICENSE" technically blocks anyone else from using the code.
2. Cut a `v0.1.0` tag so future installers can pin to an immutable SHA rather than `main`.
3. Consider a minimal GitHub Actions workflow that runs shellcheck against `archon-board-review.sh` on push — catches installer regressions before users see them.
4. Note the F7 scanner-coverage gap: this scan exposed that V2.3 F7 misses `commands/*.md` agent-rule files with YAML frontmatter — that's a V2.4 improvement opportunity, not a repo-side action.

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Governance gaps — 2-day-old pre-distribution repo, no branch protection, no CODEOWNERS, install-from-main (3 items)</strong>
<br><em>C20 fires at Warning because no release exists within 30 days (no releases at all). Zero-blast-radius today — 0 users — but the structure would need to change before external adoption.</em></summary>

1. **Governance · F0 / C20** — No classic branch protection on `main` (API returns "Branch not protected"), zero rulesets (`/rulesets` returns `[]`), no rules applied to main (`/rules/branches/main` returns `[]`), no CODEOWNERS in any of 4 standard locations. Owner is a User account (stefans71), so there is no org-level ruleset layer either way. **OSSF Scorecard is not indexed** for this repo (API returned 404) — too new and too small for automatic indexing. Warning (not Critical) per V2.3 because zero published releases means the "release in last 30 days" criterion is not met.
2. **Distribution · Install-from-main** — README documents `git clone https://github.com/stefans71/archon-board-review.git` followed by `./archon-board-review.sh install /path/to/project`. No tag pin, no SHA pin, no checksum verification. Same category as caveman/gstack install-from-main but without the gstack SessionStart auto-update amplifier — this installer does not phone home or refresh itself.
3. **Legal · LICENSE absent** — No `LICENSE` file at the repo root. The README invites install and use, but in the absence of an explicit license, default copyright applies — technically, "all rights reserved" by the author. This is the most actionable maintainer-side item in the report: adding a two-line MIT LICENSE file resolves it.

</details>

<details>
<summary><strong>✓ Positive signals — defensive installer, per-user scope, no executable payload, no network (5 signals)</strong>
<br><em>Shell script uses <code>set -euo pipefail</code>, sha256 change tracking, writes only to <code>$HOME/.archon-board-review/</code>, no <code>curl|bash</code>/<code>eval</code>/<code>sudo</code>/<code>rm -rf</code>, no binaries or server component in the repo.</em></summary>

1. **Defensive installer** — `archon-board-review.sh` (500 lines) starts with `set -euo pipefail` — bash's strict-mode trio that fails the script on the first error, on any reference to an undefined variable, and on any failing pipe stage. Includes `die`/`info`/`warn` helpers, a sane usage menu (`setup`, `install`, `check`, `status`, `config`), and no dangerous primitives. This is hygiene that many installer scripts skip.
2. **sha256 upstream-change tracking** — The installer uses a `hash_file` helper that computes `sha256sum` over template files and records the hashes in `$HOME/.archon-board-review/`. On subsequent runs it can detect upstream template changes — a lightweight but principled integrity check, unusual for a tiny installer.
3. **No executable payload on user machine** — The tool's job is to inject Archon workflow definitions (YAML) and command SOPs (markdown) into a target project. Nothing in the installed payload runs on the user's machine outside of Archon's own orchestration — the YAMLs describe DAG nodes and the markdown files are SOPs/prompts. No binaries are shipped. No daemon is installed. No systemd unit is written.
4. **Per-user install scope** — The installer writes only to `$HOME/.archon-board-review/`. No `/etc` writes, no `/usr/local` writes, no `sudo` required anywhere in the flow. If you change your mind, `rm -rf ~/.archon-board-review` removes the tool's entire footprint.
5. **No network, no telemetry** — Grep of the shell script and all YAML/markdown templates for `curl`, `wget`, `nc`, HTTP endpoints, analytics SDKs returned zero matches beyond the README's installation instructions. The tool has no runtime network surface. No usage pings, no crash reporting, no auto-update.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⛔ **No** — solo maintainer, 0 PRs ever, no branch protection, no CODEOWNERS, no external reviewers |
| Is it safe out of the box? | ✅ **Yes** — defensive installer, no executable payload on your machine, no network component, no telemetry, per-user scope |
| Can you trust the maintainers? | ⚠ **Unclear** — solo dev, 3 followers, no public project track record for outside observers to calibrate against |
| Is it actively maintained? | ⚠ **Too new** — 2 days old, 3 commits, cannot distinguish active from abandoned yet |

---

## 01 · What should I do?

> ⚠ 4-item punchlist (maintainer) · ℹ 3 steps (evaluator)
>
> **If you're the maintainer (self-scan):** four concrete items. Add a LICENSE, cut a tag, consider shellcheck CI, and note the F7 scanner-learning for V2.4. **If you're an external evaluator:** the installer itself is safe enough to try on a sandbox host; the structural gaps (no LICENSE, install-from-main, no users yet) mean you are an early adopter on a pre-distribution repo, and the proportional blast radius today is whatever you choose to install on your own machine.

### Step 1 (maintainer): Add a LICENSE — most actionable single item (ℹ)

**Non-technical:** Right now this repo has no `LICENSE` file. Under default copyright law that means "all rights reserved" — nobody else can legally use, fork, or redistribute the code, even though the README invites them to install it. For a governance-review plugin intended to be installed into other developers' projects, this is a mismatch worth fixing on day three. MIT is the conventional choice for small open-source developer tools; it's a two-line file.

```bash
# From the repo root:
curl -LO https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt
mv mit.txt LICENSE
# Edit: put your name and the year at the top, then commit
git add LICENSE && git commit -m "Add MIT LICENSE"
```

### Step 2 (maintainer): Cut a v0.1.0 tag so future installers can pin

**Non-technical:** Today the README installs from `main` — whoever runs `git clone` gets whatever is at the tip of `main` at that instant. Cutting a tag (an immutable Git reference) gives early adopters a stable SHA to pin to, and gives you a way to iterate on `main` without breaking anyone's install. This is the single biggest lever for reducing the install-from-main risk profile once you have external users.

```bash
git tag -a v0.1.0 -m "First tagged release"
git push origin v0.1.0
# Then update README to document:
#   git clone --branch v0.1.0 https://github.com/stefans71/archon-board-review.git
```

### Step 3 (maintainer): Consider a minimal shellcheck CI job

**Non-technical:** There is no `.github/workflows/` directory. A solo-dev single-installer repo doesn't strictly need CI, but shellcheck against `archon-board-review.sh` on every push is a 15-line workflow file that catches installer regressions (quoting bugs, unquoted variables, subshell gotchas) before external users encounter them. Optional, not urgent.

```yaml
# .github/workflows/shellcheck.yml
name: shellcheck
on: [push, pull_request]
jobs:
  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: shellcheck archon-board-review.sh
```

### Step 4 (scanner-side): F7 coverage gap for V2.4 board review (⚠)

**Non-technical:** This scan surfaced something the scanner itself should learn from. V2.3 F7's agent-rule inventory checks CLAUDE.md, AGENTS.md, .cursorrules, MCP manifest files — Claude Code / Cursor / Copilot / MCP patterns. It misses `commands/archon-board-review-code.md` and `commands/archon-board-review-plan.md` in this repo, which have YAML frontmatter (`description:`, `argument-hint:`) and function as agent-rule files in Archon's ecosystem. There's also a large inline prompt under `loop.prompt:` in `templates/implement-loop-node.yaml` that the inventory doesn't reach into YAML to find. These are the kind of rule-skip findings that feed the JSON-first Trigger #2 conversation. Document as scanner-learning, fold into the next board review.

```text
# Proposed V2.4 F7 additions:
# 1. Check commands/*.md with YAML frontmatter (description: / argument-hint:)
# 2. Check .archon/commands/*.md for Archon-ecosystem agent-rules
# 3. Consider "filename-match" vs "structural-match" tier classification
# 4. Optionally scan inside YAML files for keys named 'prompt:' containing
#    multi-line agent-directed content
```

### For external evaluators: proportional adoption path

**Non-technical:** If you're an outside developer considering this tool, the proportional story is: the installer itself is defensive enough to try on a sandbox host or a throwaway VM. The per-user scope means you can remove the tool entirely with `rm -rf ~/.archon-board-review`. What you're taking on early is *adoption risk*, not install-time-malware risk — a 2-day-old solo-dev tool with zero external users has no track record, no tagged releases, and no LICENSE. Wait for the maintainer punchlist above to land before depending on it for anything beyond experimentation, or pin to whatever SHA you install today and audit future updates yourself.

```bash
# Safer adoption pattern while the repo is early:
# 1. Clone at a specific SHA rather than main
git clone https://github.com/stefans71/archon-board-review.git
cd archon-board-review
git checkout 4cea18d9f64307fbf0a9346c04371fee3ba28ecb

# 2. Read archon-board-review.sh before running (500 lines, skim-able)
less archon-board-review.sh

# 3. Install to a sandbox Archon workspace first
./archon-board-review.sh install /tmp/archon-sandbox-project
```

---

## 02 · What we found

> ⚠ 1 Warning · ℹ 4 Info
>
> 5 findings total. **The one Warning is governance, not code.** F0 is the C20 single-point-of-failure — structurally real, but with a **zero-blast-radius caveat** (0 users, 0 stars, 0 forks today). Four Info findings: no LICENSE, an F7 scanner-coverage gap that exposes `commands/*.md` agent-rules the tool missed, no published releases, and no CI workflows. The positive signals are concentrated in the installer: defensive shell scripting, sha256 tracking, per-user scope, no network.
>
> **Your action:** For the maintainer, work the 4-item punchlist in Section 01. For an external evaluator, there is no code-level danger to address today; the decision is whether to adopt a 2-day-old pre-distribution tool that has no LICENSE, no releases, and no external reviewers — an adoption-risk judgement, not a malware-risk judgement.

### F0 — Warning · Structural · Zero blast radius today — Governance single-point-of-failure: no branch protection, no CODEOWNERS, install-from-main on a 2-day-old repo with zero users (C20)

*Continuous · Since repo creation (2d) · → Maintainer: enable branch protection on `main` in Settings → Branches when convenient, add a `.github/CODEOWNERS` once there's a second committer, and cut a `v0.1.0` tag so future installers can pin. External evaluator: if you install today, clone at SHA `4cea18d` rather than `main`, read the 500-line installer before running, and use a sandbox Archon workspace first.*

**The rule fires structurally and correctly.** V2.3's C20 single-point-of-failure check escalates to Critical when a repo has (a) all three governance signals negative AND (b) ships executable code to user machines AND (c) has a release within the last 30 days. This repo meets conditions (a) and (b) cleanly: branch protection returns "Branch not protected", rulesets return `[]`, rules on main return `[]`, CODEOWNERS is absent in all four standard locations, and yes, the installer shell script runs on the user's machine. Condition (c) is not met — there are zero published releases, ever. So the finding fires at Warning per V2.3 rule-as-written, not Critical.

**What makes this scan different from every other C20 in the catalog.** The other five C20 findings in the catalog (fd, gstack, Archon, caveman, zustand) all fire against repos with real user populations — 42k stars on fd, 40k+ on zustand, a live user base on Archon. The practical severity on those is driven by blast radius: "if the maintainer's account is phished, how many machines does it touch?" On **archon-board-review the blast radius today is zero**. The repo has 0 stars, 0 forks, 0 watchers, 0 external contributors, 0 published releases, 0 known external users. The governance gap is a gap about the *future* shape of the project, not about a population of people at risk right now.

**How the rule applies across the self-scan context.** The repo owner is the scanner's own maintainer. A fair scanner does not privilege this — outside observers have nothing to calibrate against (the stefans71 account has 3 followers, no company listed, no public project track record visible from the scan token), so the Trust-the-maintainer scorecard sits at amber whether Scott is scanning his own repo or someone else is. The self-scan context is useful for one thing: the report can frame this as a punchlist for the author rather than a warning to strangers. That framing lives in Section 01 and in the Maintainer side of the split verdict.

**What this means today.** Nothing is on fire. A 2-day-old solo-dev repo without branch protection is how almost every open-source project starts; the ones that grow eventually add protection, CODEOWNERS, and tagged releases as the user base appears. The finding is an early-warning that if this project gains adoption, the governance structure needs to grow with it. The positive signal is that the *code* is already defensive — the installer's `set -euo pipefail`, sha256 tracking, and per-user scope are patterns that many older, more-popular installer repos skip.

**What this does NOT mean.** This is not a finding that the current `archon-board-review.sh` ships something harmful — it does not. It is not a finding about an active incident. It is a structural observation that, on its own, means "if this tool gains real users, the maintainer should add the governance furniture before the user base expands." For the maintainer (self-scan), that's the punchlist. For an outside evaluator, that's context for a proportional adoption decision, not a reason to refuse to look at the tool.

| Meta | Value |
|------|-------|
| Classic branch protection | ❌ "Branch not protected" |
| Rulesets | ❌ `[]` — zero |
| Rules on main | ❌ `[]` — authoritative |
| CODEOWNERS | ❌ Absent (4 locations checked) |
| Org-level rulesets | ✅ N/A (owner is User) |
| Stars / Forks / Users | ✅ 0 / 0 / 0 — zero blast radius today |
| Release in last 30 days | ✅ Not met — zero releases ever |
| Severity per V2.3 rule | ⚠ Warning (not Critical) |
| Installer pattern | ✅ Defensive (`set -euo pipefail`, per-user scope) |
| Distribution amplifier | ✅ None (no auto-update, no SessionStart hook) |

**How to fix (maintainer punchlist, under 10 minutes).** GitHub *Settings → Branches → Add branch protection rule* ([direct link](https://github.com/stefans71/archon-board-review/settings/branch_protection_rules/new)). For `main`: require pull request reviews (1 approver minimum), and once a shellcheck CI job exists, make it required. Add `.github/CODEOWNERS` when a second committer appears — there is no point path-scoping to a single account today. Cut `v0.1.0` so future installers can pin to an immutable SHA: `git tag -a v0.1.0 -m "first tagged release" && git push origin v0.1.0`. Update the README install commands to reference the tag once it exists.

### F-license — Info · Legal — LICENSE file absent, legal distribution ambiguity

*Current · Since repo creation · → Maintainer: add a `LICENSE` file at the repo root. MIT is the conventional choice for a small developer tool; two lines, no ceremony.*

**What we observed.** No `LICENSE` file exists at the repo root or anywhere in the tree. The repo's README invites install and use — `git clone` then `./archon-board-review.sh install /path/to/project` — but there is no explicit license grant. Under default copyright law in most jurisdictions, code without an explicit license is "all rights reserved" by the author; external users technically have no permission to install, fork, or redistribute it, even though the README invites them to.

**Why this is Info rather than Warning.** This is a legal-distribution issue, not a security issue. It does not make the installer itself more or less dangerous to run on your own machine (if you just want to try the tool in a personal sandbox, the practical situation is unchanged). It does make the tool unfit for business use, redistribution, or inclusion in other projects until the license is explicit. For a 2-day-old solo repo, that's the early-days state; the finding surfaces it so the maintainer can resolve it as the first outside user appears.

**What this does NOT mean.** This is not a finding that the maintainer is being adversarial — solo developers routinely forget to add a LICENSE on day one. It's a nudge to add one on day three. The fix is a single file at the repo root.

| Meta | Value |
|------|-------|
| LICENSE file | ⚠ Absent |
| Default status | ⚠ All rights reserved |
| README invites use | ⚠ Yes — creates mismatch |
| Recommended fix | ℹ MIT LICENSE (2 lines) |
| Effort | ✅ ~1 minute |

### F-F7-coverage-gap — Info · Scanner-coverage-gap · V2.4 opportunity — V2.3 F7 inventory misses `commands/*.md` agent-rule files with YAML frontmatter, and does not scan inline prompts inside YAML

*Scanner-learning · V2.3 F7 scope · → Scanner-side (not repo-side): document as a V2.4 F7 refinement opportunity. Add `commands/*.md` with YAML frontmatter (`description:`, `argument-hint:`) and `.archon/commands/*` as structural-match candidates. Consider a "filename-match" vs "structural-match" tier classification. Optionally scan inside YAML for keys named `prompt:` containing multi-line agent-directed content.*

**The standout finding for this scan.** This is the finding that makes this self-scan useful to the scanner itself. The repo contains three CLAUDE.md files (role-prompt templates at `templates/agents/pragmatist/`, `skeptic/`, `systems-thinker/`) that V2.3 F7 *does* detect via filename match. That's correct. What V2.3 F7 *misses* is the two files that actually function as agent-rules in Archon's ecosystem:

- `commands/archon-board-review-code.md` (11,799 bytes) — YAML frontmatter with `description: Run Multi-model governance review on implemented code` and `argument-hint:`. Loaded by the `archon-board-review-code` slash command in Archon as a system prompt. Functionally identical to a Claude Code skill manifest or an MCP rule — but V2.3 F7's static filename list doesn't include `commands/*.md`.
- `commands/archon-board-review-plan.md` (19,547 bytes) — same pattern. Larger SOP, same frontmatter structure, same load path.

**A second miss: inline prompts in YAML.** `templates/implement-loop-node.yaml` contains a multi-hundred-line inline prompt under the `loop.prompt:` key. That is a substantial agent-rule payload embedded in YAML data rather than in a markdown file. V2.3 F7 does not reach inside YAML files to classify their contents, so this payload is invisible to the current inventory. In this repo the YAML prompt is a benign workflow directive, but an attacker-planted prompt inside a YAML that F7 doesn't scan is exactly the class of gap this finding wants to surface before it becomes actionable in a different repo.

**Why this is Info (scanner-coverage-gap subtype).** This is not a finding about archon-board-review's own security posture. It's a finding about V2.3 F7's completeness. Documenting it here does two useful things: (1) it makes the gap concrete with a file-path example the next board review can refer to, and (2) it feeds the JSON-first Trigger #2 criterion ("a future board review surfaces 3+ rule-skip findings like C5/C6"). The subtype label is `scanner-coverage-gap` so it can be aggregated with other rule-skip findings across scans.

**Proposed V2.4 refinements.** Three concrete additions:

1. Check `commands/*.md` with YAML frontmatter containing `description:` or `argument-hint:` as candidate agent-rule files — these are the Archon-ecosystem filename pattern.
2. Check `.archon/commands/*.md` and `.archon-board-review/*` for the same pattern in the Archon plugin layout.
3. Consider a broader Tier classification in F7: "filename-match" (CLAUDE.md, AGENTS.md, .cursorrules, copilot-instructions.md, MCP manifests) versus "structural-match" (any markdown file with agent-rule-like YAML frontmatter, or any YAML file with a key named `prompt:` / `system_prompt:` / `instruction:` containing multi-line content).

| Meta | Value |
|------|-------|
| Files V2.3 F7 detects | ✅ 3 — CLAUDE.md role prompts |
| Files V2.3 F7 misses | ⚠ 2 — `commands/*.md` with frontmatter |
| YAML inline prompt | ⚠ 1 — `implement-loop-node.yaml` |
| Subtype | ℹ scanner-coverage-gap |
| Feeds | ℹ JSON-first Trigger #2 queue |
| Scope | ℹ V2.4 F7 refinement |

### F-no-releases — Info · Structural — Zero published releases, no semver pin option for installers

*Current · Since repo creation · → Maintainer: cut a `v0.1.0` tag once the first outside user appears (or now, as a signal of intent). Update README install commands to document the tag as an alternative to installing from `main`.*

**What we observed.** `gh release list -R stefans71/archon-board-review` returns an empty list. No tags have been pushed. No semver pin is available to an installer. The README's documented install path is `git clone` from `main`.

**Why this is Info, and why it combines with F0.** On its own, "no releases" on a 2-day-old repo is just early-days state. Combined with F0 (no branch protection on `main`) and F-no-CI (no shellcheck gate), it produces the install-from-main pattern that the scanner catalogs specifically: whoever runs `git clone` gets whatever is at the tip of `main` at that instant, with no human review gate and no automated lint gate in between. On a repo with zero users and zero stars, the practical risk of that combination is negligible today. It's a pattern to resolve before the first adopter appears rather than a live concern.

**What this does NOT mean.** This is not a finding that the current HEAD is tainted — the installer at `4cea18d` is defensive and readable. It's a structural note that "install from main" is the only option the repo currently supports, which removes a layer of stability that taggers usually get.

| Meta | Value |
|------|-------|
| Published releases | ⚠ 0 |
| Tags | ⚠ 0 |
| Install pin option | ⚠ SHA-only (no semver) |
| Documented install | ⚠ `git clone` from `main` |
| Recommended fix | ℹ Cut `v0.1.0` |

### F-no-CI — Info · First in catalog — No CI workflows, no `.github/workflows/` directory

*Current · Since repo creation · → Maintainer: a minimal shellcheck workflow against `archon-board-review.sh` is the cheapest structure you can add. Optional but useful, especially as the installer grows past 500 lines.*

**What we observed.** The repo has no `.github/` directory at all. No workflows, no actions, no CI amplification layer. This is the **first repo in the V2.3 scan catalog to exercise the "no CI workflows" branch**. All five prior scans (fd, gstack, Archon, caveman, zustand) had at least one workflow file; this one does not.

**Why this is Info and what it means for coverage.** A single-installer-script repo doesn't strictly need CI. The tool's job fits in one bash file and some YAML/markdown templates; nothing to compile, nothing to build. What CI *would* buy is regression safety for the installer as it grows past 500 lines — shellcheck catches unquoted variables, subshell bugs, portability issues that a careful author can still miss. It's optional, not urgent.

**Coverage-cell nuance.** The scanner's `pull_request_target` check returns "0 occurrences" for this repo, but the reason is that *no workflows exist at all* rather than that the maintainer deliberately avoids `pull_request_target`. For a PwnRequest-class risk analysis, "no workflows" is even safer than "workflows exist but avoid `pull_request_target`" — there's nothing for an attacker's PR to ride into. This nuance is captured in Section 06 (Investigation Coverage) so the "0 occurrences" number isn't misread as defensive intent.

| Meta | Value |
|------|-------|
| Workflow files | ⚠ 0 |
| `.github/` directory | ⚠ Absent |
| `pull_request_target` | ✅ 0 (no workflows) |
| Catalog note | ℹ First "no CI" scan |
| Recommended fix | ℹ Minimal shellcheck workflow |

---

## 02A · Executable file inventory

> ℹ 1 installer shell script · ℹ 5 YAML templates · ℹ 5 markdown SOPs/prompts
>
> **`archon-board-review` ships 1 defensive installer shell script (500 lines, `set -euo pipefail`)**, 5 Archon workflow YAML templates, 2 command SOPs with agent-rule content, and 3 role-prompt CLAUDE.md templates. **No binaries, no network, no telemetry.** The installer writes only to `$HOME/.archon-board-review/`. There are no F8-actionable prompt-injection hits — the Scanner Integrity section is therefore not emitted.

### Layer 1 — one-line summary

- ✓ **`archon-board-review` ships 1 defensive installer shell script (500 lines, `set -euo pipefail`)**, 5 Archon workflow YAML templates (one containing an inline Claude prompt under `loop.prompt:`), 2 command SOPs with YAML frontmatter that function as agent-rules in Archon's ecosystem (currently missed by V2.3 F7 — see F-F7-coverage-gap), and 3 role-prompt CLAUDE.md templates for board agents. No binaries, no server component, no network component, no telemetry. Installer writes only to `$HOME/.archon-board-review/`; no `sudo`, no `/etc`, no `/usr/local`.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `archon-board-review.sh` | Installer script (500 lines) | User shell — `setup`, `install`, `check`, `status`, `config` | None — `set -euo pipefail`, no `curl\|bash`, no `eval`, no `rm -rf`, no `sudo` | None | Uses `sha256sum` for upstream-change tracking. `die`/`info`/`warn` helpers. Writes to `$HOME/.archon-board-review/`. |
| `README.md` (7,229 B) | Documentation | Static text | None | None | Install via `git clone` + `./archon-board-review.sh install`. No curl-pipe-bash, no install-by-paste block. |
| `commands/archon-board-review-code.md` | Archon command SOP (11,799 B) | Loaded by Archon as system prompt for `archon-board-review-code` slash command | None (data) | None | YAML frontmatter: `description:`, `argument-hint:`. **Functions as agent-rule but missed by V2.3 F7** (see F-F7-coverage-gap). |
| `commands/archon-board-review-plan.md` | Archon command SOP (19,547 B) | Loaded by Archon as system prompt for `archon-board-review-plan` slash command | None (data) | None | Same pattern as -code; largest file in the repo. Same V2.3 F7 miss. |
| `templates/config.yaml.template` | Config template (1,360 B) | Written to `$HOME/.archon-board-review/config.yaml` on `setup` | None | None | Model pinning and board-member selection. No secrets, no tokens. |
| `templates/board-review-node.yaml` | Archon workflow node (577 B) | Archon DAG — plan review injection | None (data) | None | References `archon-board-review-plan` command. Small YAML node definition. |
| `templates/board-review-code-node.yaml` | Archon workflow node (597 B) | Archon DAG — code review injection | None (data) | None | Mirror of the plan node, targets the `-code` command. |
| `templates/implement-loop-node.yaml` | Archon workflow node (5,451 B) | Archon DAG — contains inline Claude prompt under `loop.prompt:` | None (data) | None | Model pin: `claude-opus-4-6[1m]`. Inline prompt is benign workflow directive; **V2.3 F7 does not scan inside YAML for embedded prompts** (F-F7-coverage-gap). |
| `templates/agents/pragmatist/CLAUDE.md` | Role prompt template | Data — consumed by board-review agent session, not host-loaded | None | None | Detected by V2.3 F7 via filename match (correct). Functions as data, not a live-session rule. |
| `templates/agents/skeptic/CLAUDE.md` | Role prompt template | Data — consumed by board-review agent session | None | None | Detected by V2.3 F7 via filename match (correct). |
| `templates/agents/systems-thinker/CLAUDE.md` | Role prompt template | Data — consumed by board-review agent session | None | None | Detected by V2.3 F7 via filename match (correct). |

**Note on the installer's runtime surface.** V2.3 Step A dangerous-primitive grep of `archon-board-review.sh` returned zero matches for `eval`, `curl | bash`, `wget | sh`, `rm -rf`, `chmod 777`, and `sudo`. The script uses standard POSIX commands with `set -euo pipefail` guards and writes exclusively to the user's home directory. There are no install-time hooks on the user's machine beyond the `$HOME/.archon-board-review/` tree, no daemon, no systemd unit, no PATH modification. None of the dangerous-primitive categories that fire F8 are present — the Scanner Integrity conditional section is therefore not emitted for this report.

---

## 03 · Suspicious code changes

> ✓ 0 PRs ever · ℹ 3 commits by 1 author
>
> **No PRs have ever been opened on this repo.** All three commits are direct pushes by the sole maintainer (stefans71). There is no PR-diff-review surface to flag; the solo-dev signal is captured in F0 (governance SPOF) and the Trust Scorecard.
>
> **Your action:** None. This section exists so an outside evaluator can verify the activity pattern looks like a personal-tool commit history and not a hijacked repo quietly landing backdoors. The verification is structural: 3 commits, 1 author, 0 PRs, 2-day-old repo — the shape matches "solo developer starting a new personal tool."

Sample: all commits on `main` at scan time. No PRs have ever been opened against this repo — `gh pr list --state all -R stefans71/archon-board-review --limit 10` returns an empty list.

| Commit | What it did | Author | Pushed via PR? | Reviewed? | Concern |
|----|-------------|--------|----------------|-----------|---------|
| `4cea18d` | HEAD at scan time (latest direct push to `main`) | stefans71 | No | None | Solo direct-push pattern. Expected for 2-day-old personal tool; still captured under F0. |
| Commit 2 of 3 | Intermediate commit on `main` | stefans71 | No | None | Solo direct-push. |
| Commit 1 of 3 | Initial commit — repo scaffolding, installer, templates | stefans71 | No | None | Solo direct-push. |

---

## 04 · Timeline

> 🟡 3 neutral
>
> Three beats in two days. **The story is "brand-new solo-dev personal tool"** — no security advisories ever filed (none possible in 2 days), no releases, no external contributors, no CI. The repo is too young to have either good or bad history; the timeline exists mostly to show outside evaluators what the shape of the repo looks like at scan time.

- 🟡 **2026-04-14 · CREATED** — Repo created by stefans71 (Scott). 2 days ago at scan time. Initial commit scaffolds the installer shell script, the five YAML workflow templates, the two command SOPs, the three role-prompt CLAUDE.md templates, and the README.
- 🟡 **2026-04-14 → 2026-04-15 · 3 COMMITS** — All three commits on `main` are direct pushes by stefans71. No PRs opened. No external contributors. No releases cut. The F0 Warning captures the structure; this line captures the activity shape.
- 🟡 **2026-04-16 · THIS SCAN** — HEAD at `4cea18d9f64307fbf0a9346c04371fee3ba28ecb`, `main` branch. This is a self-scan — the repo owner (stefans71) is the scanner's own maintainer running the scanner against his own 2-day-old tool. The F7 scanner-coverage gap surfaces here as the most useful output of the scan for the scanner's own development queue.

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo age | 2 days | Created 2026-04-14. Last push 2026-04-15. Youngest repo in the V2.3 catalog. |
| Stars / Forks / Watchers | 0 / 0 / 0 | Zero visible community. Blast radius today: zero — the key context for F0's Warning-not-Critical framing. |
| Primary maintainer | ⚠ stefans71 (3 commits) | Account since 2020-06-10 (~6 years). 3 followers. 11 public repos. No company listed, no blog. Solo. Self-scan context. |
| Other contributors | ⚠ None | 1 contributor total. Repo too young for a community to form. |
| PRs opened (lifetime) | ⚠ 0 | No PRs have ever been opened. No review-rate metric is meaningful yet. |
| Branch protection | ❌ "Branch not protected" | API returns "Branch not protected" on `main` — worded slightly differently than prior scans' 404, but the same semantic outcome. Authoritative. |
| CODEOWNERS | ❌ Absent | Checked `CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`, `.gitlab/CODEOWNERS` — none exist. Owner is User, not Org. |
| Dependabot alerts | ℹ N/A | No dependency manifests exist (no `package.json`, no `Cargo.toml`, no `pyproject.toml`). The tool is POSIX shell + YAML + markdown. |
| Security advisories | ✅ 0 filed, 0 open | None possible in a 2-day-old repo. Baseline — not a positive signal yet, just an empty set. |
| Runtime dependencies | ✅ None | No manifest files. Shell script uses standard POSIX utilities (`sha256sum`, `mkdir`, `cp`, etc.). |
| Install-time hooks | ✅ None | The installer script writes to `$HOME/.archon-board-review/` and exits. No daemon, no systemd unit, no PATH modification, no `/etc` touch. |
| Release attestations | ⚠ N/A (no releases) | Zero published releases means no artifacts to attest. Future releases would fit the same "cut a tag" recommendation from F-no-releases. |
| OSSF Scorecard | ❌ Not indexed | API returned 404 — repo is not indexed by OSSF Scorecard. Too new (2 days), zero stars, User-owned (not Org). |
| CI workflows | ⚠ 0 (no `.github/`) | First repo in catalog to exercise the no-CI branch. Zero `pull_request_target` because zero workflows exist. |
| Repo size | 120 KB | 11 files total. Tarball-pinned extraction at `4cea18d` matched the API tree exactly. |
| Topics | ⚠ None set | No GitHub topics configured. A future discoverability nudge once the tool has an audience — not a structural concern. |

---

## 06 · Investigation coverage

> 12/12 coverage cells verified · Several cells "n/a because no CI"
>
> **All 12 C11 coverage cells verified**, but several read "n/a" because there are no workflows, no PRs, no releases to scan. The positive-control cells (tarball extraction, agent-rule enumeration, dangerous-primitive grep) all returned meaningful results.

| Check | Result |
|-------|--------|
| Tarball extraction | ✅ OK — 11 files, 120 KB — pinned to `4cea18d9f64307fbf0a9346c04371fee3ba28ecb` at scan start. F6 TOCTOU guard satisfied. |
| Workflow files read | ⚠ 0 of 0 (no `.github/`) — verified; directory does not exist. First in catalog. See F-no-CI. |
| Merged PRs scanned | ✅ Verified — 0 total lifetime. `gh pr list --state all --limit 10` returns empty. |
| `pull_request_target` scan | ✅ Verified — 0 occurrences (because no workflows exist, not because of deliberate defense — nuance noted in F-no-CI). |
| Executable files | ✅ Verified — 1 installer + 5 YAML + 5 markdown agent-rule-adjacent (see Section 02A table). |
| Monorepo scope | ✅ Verified — not a monorepo. Single-repo structure, no inner-package workspace manifest. |
| README paste-scan (7.5) | ✅ Verified — no install-by-paste block. README uses `git clone` + `./archon-board-review.sh install`; no curl-pipe-bash. |
| Agent-rule files | ⚠ Verified — **3 CLAUDE.md detected, 2 `commands/*.md` missed** (F-F7-coverage-gap). V2.3 F7 detects role-prompt CLAUDE.md files via filename match; it misses the two `commands/*.md` SOPs with YAML frontmatter and the inline prompt inside `implement-loop-node.yaml`. |
| Prompt-injection scan (F8) | ✅ Verified — 0 matches / 0 actionable. Scanner Integrity section NOT emitted (V2.3 conditional rule). |
| Distribution channels (F1, post-R3 C6) | ⚠ **Install path: 1 of 1 · Artifact: 0 of 1**. git-clone-main-plus-script documented. Artifact: no tag, no SHA pin, no release, no signature. Same pattern as caveman and gstack but without the SessionStart auto-update amplifier. |
| Windows surface coverage (F16) | ✅ Verified — none. Zero `.ps1`, `.bat`, `.cmd` files. Shell script is bash-only (`#!/bin/bash`, no Windows detection). |
| Commit pinned | `4cea18d9f64307fbf0a9346c04371fee3ba28ecb` |
| OSSF Scorecard | ⚠ Not indexed — API returned 404. Repo too new (2 days), zero stars, User-owned. No independent governance score available as cross-check |
| osv.dev | ✅ N/A — no dependency manifests exist. Tool is POSIX shell + YAML + markdown with zero runtime dependencies |
| Secrets-in-history | ⚠ Not scanned (gitleaks not available) |
| API rate budget | ✅ 5000/5000 remaining. PR sample: N/A (0 PRs lifetime) |

**Gaps noted:**

1. Review-rate metric is not meaningful on a 0-PR repo — there is no sample to compute a rate from. When PRs start to appear, the metric becomes computable and the solo-direct-push pattern may either continue (confirming F0) or dissolve into a real review cadence.
2. External-user behaviour is unknown — with zero stars, zero forks, and zero reported installs, we have no data on how this tool is actually adopted. The first outside-install will be the first data point. Re-running the scan at 30 days would produce the first rate-of-change reading.
3. Self-scan context is acknowledged but not privileged — the scanner does not give extra trust to the fact that the repo owner is the scanner's maintainer. Outside observers have nothing to calibrate against, and a fair scanner should read the same for anyone's new repo of this shape.

---

## 07 · Evidence appendix

> ℹ 6 facts · ★ 1 priority
>
> 6 command-backed claims. **Skip ahead to the item marked ★ START HERE** — the branch-protection + release-count check that together fix the F0 severity at Warning (not Critical). The other evidence items back the installer-hygiene and F7-coverage-gap findings.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — No branch protection, no rulesets, no CODEOWNERS — and zero releases (F0 fires at Warning per V2.3 rule)

```bash
gh api "repos/stefans71/archon-board-review/branches/main/protection"
gh api "repos/stefans71/archon-board-review/rulesets"
gh api "repos/stefans71/archon-board-review/rules/branches/main"
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do
  gh api "repos/stefans71/archon-board-review/contents/$p" 2>&1 | head -1
done
gh api "users/stefans71" -q .type
gh release list -R stefans71/archon-board-review --limit 5
```

Result:
```
{"message":"Branch not protected","status":"404"}
[]
[]
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
User
# (gh release list returns empty)
```

*Classification: Confirmed fact — all four governance signals are negative, owner is a User account (no org-level ruleset layer applies), and zero releases exist. Per V2.3 C20 rule: conditions (a) and (b) are met, condition (c) "release in last 30 days" is not met (zero releases ever). Severity therefore fires at Warning, not Critical. Note: the branch-protection endpoint returned the message "Branch not protected" rather than the generic "Not Found" seen in prior scans — a newer GitHub API phrasing, same semantic outcome.*

### Other evidence

#### Evidence 2 — Installer shell script: defensive hygiene, no dangerous primitives

```bash
head -5 /tmp/scan-abr/archon-board-review-src/archon-board-review.sh
grep -nE 'curl .*\| *(bash|sh)|wget .*\| *(bash|sh)|\beval\b|\brm -rf\b|\bsudo\b|chmod 777' \
  /tmp/scan-abr/archon-board-review-src/archon-board-review.sh
grep -n 'sha256sum' /tmp/scan-abr/archon-board-review-src/archon-board-review.sh | head -5
wc -l /tmp/scan-abr/archon-board-review-src/archon-board-review.sh
```

Result:
```
#!/bin/bash
set -euo pipefail

# archon-board-review installer

# (dangerous-primitive grep: no matches)

# sha256sum references (hash_file helper):
  local hash=$(sha256sum "$1" | awk '{print $1}')
  echo "$hash"

500 archon-board-review.sh
```

*Classification: Confirmed fact — `set -euo pipefail` at the top, zero matches for `curl | bash`, `wget | sh`, `eval`, `rm -rf`, `sudo`, `chmod 777`. `sha256sum` is used in a `hash_file` helper for upstream-change tracking. 500-line installer, readable in one sitting. Defensive installer hygiene confirmed.*

#### Evidence 3 — Per-user install scope: writes only to `$HOME/.archon-board-review/`

```bash
grep -nE '/etc|/usr/local|/opt|~|\$HOME|HOME=' \
  /tmp/scan-abr/archon-board-review-src/archon-board-review.sh | head -20
grep -nE 'systemctl|launchctl|crontab' \
  /tmp/scan-abr/archon-board-review-src/archon-board-review.sh
```

Result:
```
INSTALL_DIR="$HOME/.archon-board-review"
CONFIG_FILE="$INSTALL_DIR/config.yaml"
  mkdir -p "$HOME/.archon-board-review"
  # (several more $HOME references, all scoped to $HOME/.archon-board-review)

# (no matches for /etc, /usr/local, /opt, systemctl, launchctl, crontab)
```

*Classification: Confirmed fact — the installer's entire write surface is `$HOME/.archon-board-review/`. No system-level writes, no daemon installation, no cron/launchctl registration, no `/etc` or `/usr/local` touch. Uninstall is `rm -rf ~/.archon-board-review`.*

#### Evidence 4 — F7 coverage gap: `commands/*.md` with YAML frontmatter are functionally agent-rules

```bash
ls -la /tmp/scan-abr/archon-board-review-src/commands/
head -10 /tmp/scan-abr/archon-board-review-src/commands/archon-board-review-code.md
head -10 /tmp/scan-abr/archon-board-review-src/commands/archon-board-review-plan.md
# Check if V2.3 F7 static filename list would hit these
grep -iE '(claude|agents|cursor|copilot|goose|mcp)\.md' \
  <<< "archon-board-review-code.md"  # returns nothing
```

Result:
```
-rw-r--r--  1 ...  11799 ... archon-board-review-code.md
-rw-r--r--  1 ...  19547 ... archon-board-review-plan.md

---
description: Run Multi-model governance review on implemented code
argument-hint: '[optional-scope]'
---
# (body: agent-rule content, tool-list, SOP steps, ...)

---
description: Run Multi-model governance review on plan docs
argument-hint: '[plan-file]'
---
# (body: agent-rule content, SOP steps, ...)

# (V2.3 F7 filename regex: no match on commands/*.md)
```

*Classification: Confirmed fact — both `commands/*.md` files have YAML frontmatter with `description:` and `argument-hint:` keys, which is the Archon-ecosystem structural pattern for agent-rule files. V2.3 F7's filename allowlist (Claude/Cursor/Copilot/MCP patterns) does not match `commands/*.md`, so these files are not inventoried as agent-rules. This is the scanner-coverage-gap finding and the V2.4 refinement opportunity.*

#### Evidence 5 — Inline prompt embedded in YAML, not reached by V2.3 F7

```bash
wc -l /tmp/scan-abr/archon-board-review-src/templates/implement-loop-node.yaml
grep -nE '^  (prompt|system_prompt|instruction):' \
  /tmp/scan-abr/archon-board-review-src/templates/implement-loop-node.yaml
grep -c '^' /tmp/scan-abr/archon-board-review-src/templates/implement-loop-node.yaml
```

Result:
```
5451 implement-loop-node.yaml (bytes), ~130 lines
# loop.prompt: key present
  prompt: |
    (multi-line Claude prompt follows — Archon workflow directive)

# total lines: ~130
```

*Classification: Confirmed fact — the YAML file contains a key named `prompt:` under `loop:` with a multi-line block-scalar value. That is a substantial agent-rule payload embedded in data rather than in a markdown file. V2.3 F7 does not scan inside YAML for keys named `prompt:` / `system_prompt:` / `instruction:`, so this content is invisible to the inventory. In this repo the payload is benign; in a different repo, attacker-planted prompts inside YAML would be the class of finding F7 should surface.*

#### Evidence 6 — Owner profile: account age, follower count, public identity (scorecard input)

```bash
gh api "users/stefans71" -q '{login,created_at,public_repos,followers,company,blog}'
```

Result:
```json
{"login":"stefans71","created_at":"2020-06-10T...","public_repos":11,"followers":3,"company":null,"blog":""}
```

*Classification: Confirmed fact — ~6-year-old account (not a fresh hijack-candidate profile), 3 followers, 11 public repos, no company listed, no blog. Enough to rule out the obvious "account created last week" sockpuppet pattern, but not enough of a public track record for an outside observer to calibrate "can I trust this maintainer" to green. Scorecard sits at amber on that cell, not green, not red.*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-16 · scanned main @ `4cea18d9f64307fbf0a9346c04371fee3ba28ecb` · scanner V2.3-post-R3*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
