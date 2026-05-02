# Security Investigation: pbakaus/impeccable

**Investigated:** 2026-05-02 | **Applies to:** main @ `444e4acad38a00ec4b837ce57e9b4ef561297450` | **Repo age:** 0 years | **Stars:** 24,298 | **License:** Apache-2.0

> pbakaus/impeccable — 24.3k-star design-anti-pattern detection toolkit shipped as 36 skill files fanned out to 13 different AI coding harnesses (.claude, .cursor, .gemini, .agents, etc.) plus a Node CLI plus a Chrome extension. Created 5.5 months ago, single-author (96.9% share), no branch protection, 38.8% self-merge rate. 4 security issues have been triaged (2 closed in ~7-10 days, 2 open with fix-PRs sitting). Open #92 is a build-time RCE in 3 build scripts via `new Function()`; affects contributors only, not consumers of the published CLI. Install topology is 3-hop for skills (`npx impeccable skills install` → vercel-labs/skills → GitHub) with no signature verification on the alternative CDN bundle path; CLI-only `npx impeccable detect [paths]` is single-hop and safe. 0 published GHSA + no SECURITY.md = consumers won't get Dependabot alerts when fixes ship. The skill-content surface (468 files) amplifies single-key compromise blast radius but trusts only one source-of-truth directory (`source/skills/impeccable/`, 36 files).

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-impeccable.md` (+ `.html` companion) |
| Repo | [github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| Short description | Curated collection of 36 design-and-anti-pattern skills (slash commands) shipped to 13 different AI coding harnesses (.claude, .cursor, .gemini, .agents, .github, .kiro, .opencode, .pi, .qoder, .rovodev, .trae, .trae-cn, plus a `plugin/` Claude Code plugin marketplace bundle) plus a Node CLI (`impeccable detect`) for headless anti-pattern scanning, plus a Chrome devtools extension. By Paul Bakaus. |
| Category | `developer-tooling` |
| Subcategory | `agent-skills-multi-harness` |
| Language | JavaScript |
| License | Apache-2.0 |
| Target user | Frontend designer or developer using an AI coding agent who wants to catch AI-generated design slop (italic-serif hero typography, hero metric stacks, gradient text, glassmorphism, generic card grids) and apply consistent design heuristics. Three install paths: (1) `npx impeccable skills install` — delegates to vercel-labs/skills npm CLI which fetches from GitHub; (2) Claude Code plugin marketplace via `.claude-plugin/plugin.json`; (3) `npx impeccable detect <files-or-dir>` for one-shot CLI scans without persistent skill installation. |
| Verdict | **Caution** |
| Scanned revision | `main @ 444e4ac` (release tag ``) |
| Commit pinned | `444e4acad38a00ec4b837ce57e9b4ef561297450` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-05-02` |
| Prior scan | First scan of pbakaus/impeccable. 14th wild V1.2-schema scan after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21, QuickLook 22, kanata 23, freerouting 24, WLED 25, Baileys 26, skills 27, multica 28. |

---

## Verdict: Caution

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Caution — F0..F3 cluster around solo-maintainer + multi-hop install + silent disclosure on a fast-growing skills+CLI surface (5 findings)</strong>
<br><em>24k stars + 5.5 months old + zero branch protection + 3-hop install path + no GHSA channel + open build-time RCE with authored fix sitting = trust-the-maintainer-and-the-CLI posture; safe to use the CLI directly, take the slower install path for the skills.</em></summary>

1. **F0** — pbakaus 96.9% commit share + zero branch protection + 39% self-merge rate. Single-key compromise reaches 13 harnesses across the install base.
2. **F1** — Open #92: 3 sites of `new Function()` build-time RCE in scripts/. Affects contributors (`bun run build`/`dev`), not consumers. Fix-PR authored, sitting 22 days.
3. **F2** — `npx impeccable skills install` → `npx skills add` → vercel-labs/skills → GitHub. `skills update` fetches `impeccable.style/api/download/bundle/universal` over HTTPS with no signature verification.
4. **F3** — 0 GHSA published, no SECURITY.md, no dependabot.yml. 4 security issues handled internally (2 closed in ~7d, 2 open). Consumers don't get Dependabot alerts.
5. **F4** — 468 skill files × 13 harnesses regenerated from one source `source/skills/impeccable/` (36 files). Trust surface = 36 source files; ×13 fanout amplifies single-key compromise blast radius.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⚠ **Partly** — 53% any-review on n=49, but solo maintainer with no branch protection and 39% self-merge rate; Tessl + Copilot CI provides automated review only |
| Is it safe out of the box? | ⚠ **Partly** — install-path multi-hop (npx impeccable skills install → vercel-labs/skills npm CLI → GitHub) with no signature verification on the bundle path; CLI-only path (`npx impeccable detect`) is single-hop and safe to run |
| Do they fix problems quickly? | ⚠ **Partly** — 22-day-old open #92 build-time RCE has an authored fix-PR sitting; 2 prior security issues closed within ~7-10 days in late April |
| Do they tell you about problems? | ❌ **No** — 0 published GHSA, no SECURITY.md, no dependabot.yml; security fixes ship silently from the consumer's POV (no Dependabot alert, no npm advisory) |

---

## 01 · What should I do?

> Caution • Solo maintainer • 0 GHSA • Multi-hop install
>
> A multi-harness AI-coding-skills collection (36 skill files × 13 harness directories) plus a Node CLI for design anti-pattern detection plus a Chrome extension. 24.3k stars on a 5.5-month-old repo; solo-maintained by Paul Bakaus. Three install paths with varying trust topologies. Open build-time RCE (issue #92) sitting with an authored fix-PR for 22 days.

### Step 1: If you only need anti-pattern detection, use the CLI directly — no skills install required (✓)

**Non-technical:** Run `npx impeccable detect <files-or-dir>` to scan HTML/JSX/TSX/Vue/Svelte for design slop and anti-patterns without installing skills into your repo. This is single-hop (npm registry → consumer) and avoids the 3-hop skills-install supply chain.

```bash
npx impeccable detect ./src
```

### Step 2: If you want the skills, prefer the manual git-clone path over `npx impeccable skills install` (✓)

**Non-technical:** The `npx impeccable skills install` path chains through vercel-labs/skills (a 3rd-party intermediary). To stay within pbakaus's trust scope only, clone the repo and copy the harness directory yourself. This lets you inspect `source/skills/impeccable/` (36 files) before linking, and pins to the commit you cloned rather than `@latest`.

```bash
git clone https://github.com/pbakaus/impeccable && cd impeccable && git checkout 444e4acad38a00ec4b837ce57e9b4ef561297450 && less source/skills/impeccable/SKILL.md && cp -r .claude/skills/impeccable ~/your-project/.claude/skills/
```

### Step 3: Watch for #92 to merge (build-time RCE fix) before contributing source-code changes (✓)

**Non-technical:** If you plan to contribute (run `bun run build` or `bun run dev`), wait for PR resolving issue #92 to merge — that closes the `new Function()` build-time RCE. Tracking via `gh issue view 92 -R pbakaus/impeccable`. Consumers running only the published CLI are unaffected.

```bash
gh issue view 92 -R pbakaus/impeccable
```

### Step 4: Subscribe to the repo's commit feed to catch security fixes (no Dependabot alerts will fire) (✓)

**Non-technical:** Because there are 0 published GHSA and no SECURITY.md, Dependabot will not notify you when a fix ships. Subscribe to releases (`gh repo set-notifications --watch pbakaus/impeccable`) or grep recent commits for `security:` prefix periodically.

```bash
gh api repos/pbakaus/impeccable/commits --jq '.[] | select(.commit.message | test("security:"; "i")) | {sha, message: (.commit.message | split("\n")[0])}' | head
```

### Step 5: If you're sensitive to skill-content prompt-injection, audit `source/skills/impeccable/` directly (✓)

**Non-technical:** The 468-file fanout you see in `.claude/skills/`, `.cursor/skills/`, etc. is regenerated from 36 source files in `source/skills/impeccable/reference/`. Those 36 files are the real trust surface for the skill instructions; the fanout copies are mechanical regenerations of the same content.

```bash
git clone https://github.com/pbakaus/impeccable && find impeccable/source/skills/impeccable -name '*.md' -exec wc -l {} +
```

---

## 02 · What we found

> ⚠ 4 Warning · ℹ 2 Info
>
> 6 findings total.
### F0 — Warning · Governance — Solo maintainer (96.9% commit share, CODEOWNERS = `* @pbakaus`) with zero branch protection on a 24k-star, 5.5-month-old project

*Continuous since repo creation (2025-11-16) · Since 2025-11-16 · → Pin to a specific commit SHA (not `@latest`) when installing skills; review the generated .claude/skills/ tree against the upstream source before running them in a sensitive repo.*

pbakaus is the only contributor with maintainer access to a 24.3k-star, 5.5-month-old project. The remaining ~3% of contributions come from external community PR authors but no other account has merge rights. CODEOWNERS at `.github/CODEOWNERS` reads `* @pbakaus` for global ownership plus specific rules for `scripts/` and `source/` (also `@pbakaus`). 19 of 49 closed PRs (38.8%) were self-merged.

All 7 governance signals are negative. Classic branch protection returns HTTP 404 (no rule). 0 rulesets configured; 0 rules-on-default-branch. The owner is a User account, not an Org, so `org_rulesets` is N/A. The repo is not indexed by OSSF Scorecard. The Tessl Skill Review and Copilot code review CI workflows do run on every PR (visible in `.github/workflows/`) but neither is a required-review gate — pbakaus can self-merge any PR and frequently does.

If pbakaus's GitHub credentials are compromised — stolen token, hijacked session, OAuth-app abuse — an attacker can push directly to `main` with no second-human gate. The malicious commit propagates to 13 harness directories on the next `bun run build` and reaches consumers via three install paths: `npx impeccable skills install`, `npx impeccable skills update` (CDN bundle), and the Claude Code plugin marketplace. 24.3k stars indicates a non-trivial install base. Mitigation is consumer-side: pin to a specific commit SHA when installing, audit `source/skills/impeccable/` before linking, or use only the CLI (`npx impeccable detect`) which doesn't pull skill content.

**How to fix.** Maintainer-side: enable a branch protection ruleset on `main` requiring ≥1 approving review (Tessl + Copilot are CI-side, not gating); promote the existing CODEOWNERS to a required-review rule; consider transferring ownership to a GitHub Org so `org_rulesets` becomes available. Consumer-side: pin the install command to a specific commit SHA (e.g. `npx skills add pbakaus/impeccable#444e4ac`) rather than `@latest`; or `git clone` + inspect skill `.md` files before linking them into a sensitive repo.

### F1 — Warning · Build-time RCE — `new Function()` build-time RCE in 3 build scripts (issue #92 OPEN 22 days; fix-PR authored, not merged)

*OPEN 22 days as of scan date · Since #92 filed 2026-04-10 · → Affects contributors who run `bun run build` or `bun run dev` against a malicious commit. Does NOT affect consumers running `npx impeccable detect` or `npm install impeccable`. Wait for #92 to merge before contributing code changes; safe to install + use the published CLI.*

Issue #92 'security: replace new Function() eval with direct ESM import' was filed 22 days ago and is still open. The PR is authored — the fix replaces 3 instances of `new Function()` code evaluation with direct ESM imports of the already-exported `ANTIPATTERNS` array — but has not been merged. The companion meta-tracking issue #94 'Security and consistency audit findings' (also 22 days open) classifies this as 'High' severity.

The three sites are `scripts/build.js:122` (validateAntipatternRules — runs during `bun run build`), `scripts/build-extension.js:63` (antipatterns.json extraction — runs during extension build), and `scripts/lib/sub-pages-data.js:107` (readAntipatternRules — runs at dev-server boot AND during build). All three extract a regex-matched region of `src/detect-antipatterns.mjs` and evaluate it with `new Function()`. Any commit that mutates the matched region grants arbitrary code execution in the build environment when `bun run build` or `bun run dev` runs.

The impact is bounded to repository contributors and CI. The published `impeccable` npm package ships only `bin/`, `src/`, and `LICENSE` (per `package.json` `files`); the `scripts/` directory is not in the package. Consumers running `npx impeccable detect` or `npx impeccable live` do not invoke the build scripts. So this is a developer-local RCE, not a published-package supply-chain RCE. The fix landing would close it; until then, contributors should be aware that `bun run build` + `bun run dev` execute trusted code only — review PRs touching `src/detect-antipatterns.mjs` carefully before pulling them.

**How to fix.** Maintainer-side: merge PR #92, which replaces the 3 `new Function()` calls with direct ESM imports of the already-exported `ANTIPATTERNS` array. Add a CI lint that fails on any new `new Function(` or `eval(` call in `scripts/`. Consumer-side: no action required; the published CLI is unaffected.

### F2 — Warning · Supply chain — Three-hop install supply chain (impeccable npm → vercel-labs/skills npm → GitHub or impeccable.style CDN) with no signature verification

*Continuous (install-path design) · Continuous · → If you only need the CLI scanner, run `npx impeccable detect <files>` directly — no skills install required, no third-party intermediary. If you do want skills, prefer the `git clone` + manual link path over `npx impeccable skills install`.*

The skills install path is documented as `npx impeccable skills install`. Reading `bin/commands/skills.mjs` line 339 reveals this is implemented as `execSync('npx skills add pbakaus/impeccable')` — i.e. the `impeccable` CLI delegates to a third-party npm CLI (`vercel-labs/skills`) which then fetches from GitHub. Compromise of `vercel-labs/skills` allows injection of malicious skill content for every consumer who triggers an install.

The alternative path is `npx impeccable skills update`, which calls `downloadAndExtractBundle()` to fetch `https://impeccable.style/api/download/bundle/universal` over HTTPS, then unpacks with `execSync('unzip -qo "${tmpZip}" -d "${tmpDir}"')`. There is no signature verification: no SHA hash, no GPG, no Sigstore — just TLS to the impeccable.style Cloudflare Pages origin. Compromise of the Cloudflare account or DNS hijack of impeccable.style allows skill substitution for every consumer who runs `skills update`.

Install path 3 (Claude Code plugin marketplace via `.claude-plugin/marketplace.json`) follows Anthropic's plugin-marketplace trust model — single-source from this GitHub repo. The CLI-only path `npx impeccable detect <files>` does NOT pull skill content and is single-hop (npm registry → consumer); it is the safest install option if you only need the anti-pattern detector and don't want skills.

**How to fix.** Maintainer-side: ship signed bundles (Sigstore or detached PGP signatures) and document signature verification as a step in `npx impeccable skills install`; consider removing the npx-skills-add path in favor of a single first-party install verb. Consumer-side: prefer `git clone https://github.com/pbakaus/impeccable && cd impeccable && bun run build` followed by manually copying the relevant `.<harness>/skills/` dir into your repo — this stays within pbakaus's trust scope without involving vercel-labs/skills or the CDN bundle path.

### F3 — Warning · Disclosure — No published GHSA, no SECURITY.md, no dependabot.yml — security-fixes ship silently from the consumer's perspective

*Continuous since repo creation · Continuous · → Don't rely on Dependabot to alert you when a security fix ships. Watch the repo's commits or `security:`-prefixed issue closes if you've installed the skill bundle or the CLI.*

0 GitHub Security Advisories have been published despite 4 visible security-tagged issues being actively triaged. Two security issues were closed within ~7-10 days in late April 2026: #100 addressed shell injection in `npx impeccable [target]`, port-squatting in `npx impeccable live`, and added prompt-injection warnings to the critique skill; #93 hardened `extension/devtools/panel.js:503-511` against selector-injection by switching from manual escaping to `JSON.stringify`. Both fixes landed via maintainer self-merge.

Two security issues remain open as of scan date (both 22 days old): #92 (build-time RCE — see F1) has an authored fix-PR sitting, and #94 (audit tracking issue) lists multiple medium-severity items. No SECURITY.md exists at the repo root, so there's no public channel for coordinated disclosure (the maintainer uses GitHub Issues with explicit `security:` title prefix as an ad-hoc channel). No `.github/dependabot.yml` exists either — dependency security patches arrive via manual PR rather than automated bot.

From a downstream consumer's perspective: when a security fix ships in a new `impeccable@x.y.z` release, npm advisory database doesn't know about it (no GHSA), Dependabot doesn't notify (no advisory feed), and the npm-package release-notes channel isn't picked up by typical security-monitoring tools. You learn about security fixes by reading the repo's commit log or the impeccable.style changelog manually. The fixes themselves ARE transparent (issues + PRs are public) — the gap is in the notification channel, not the disclosure of facts.

**How to fix.** Maintainer-side: add a `SECURITY.md` with a disclosure-channel email or HackerOne handle; add `.github/dependabot.yml` for npm + GitHub Actions; for fix #100 and #93 (already closed), file retroactive GHSAs via `gh api -X POST repos/pbakaus/impeccable/security-advisories` so the npm advisory database picks them up. Consumer-side: subscribe to the repo's commit feed or releases page to catch security fixes; pin the npm package to a specific version and check release notes before bumping.

### F4 — Info · Prompt injection — 468 skill files × 13 harness directories form the post-install instruction surface — single source of trust, but large amplification factor

*Continuous · Continuous · → Audit `source/skills/impeccable/` (the single source of truth) before installing — not the per-harness fanout, which is regenerated mechanically. The total instruction surface is 36 skill files × ~lines-each, not 468 × ~lines.*

Each `.md` file under any of the 13 `<harness>/skills/<command>/` subtrees becomes part of an LLM's instruction context when its harness loads the skill. 36 unique skills × 13 harness fanouts = 468 skill files in the working tree. CLAUDE.md L96 documents that the harness output directories are intentionally committed and auto-regenerated by `bun run build` from `source/skills/impeccable/`.

The effective trust surface is the 36 source files in `source/skills/impeccable/reference/`, not the 468 fanout copies. The build pipeline does provider-specific placeholder replacement (`{{model}}`, `{{config_file}}`, `{{ask_instruction}}`, `{{command_prefix}}`, `{{available_commands}}`, `{{scripts_path}}` per CLAUDE.md L86-93) but otherwise the skill text is identical across harnesses. Reading the 36 source files is sufficient to audit the post-install instruction surface.

The 1 prompt-injection scan signal in CLAUDE.md L288 ('The harness inlines `SKILL.md` into the system prompt for "skill-on"...') is meta-documentation about the consumer-side instruction-loading mechanism — not an injection payload. Tessl Skill Review CI runs an external skill-quality reviewer on PRs touching skill content, providing an automated review layer (but not a blocking gate; see F0). Closed issue #100 (4 days ago) explicitly added prompt-injection warnings to the `critique` skill — the maintainer is aware of the threat model and is hardening it iteratively.

**How to fix.** Maintainer-side: continue Tessl Skill Review CI; consider sandboxing harness CI to enforce that `<harness>/skills/` content is byte-identical to `source/skills/impeccable/` after build (closes the regeneration drift gap). Consumer-side: read the 36 source files in `source/skills/impeccable/reference/` before installing; ignore the per-harness fanout copies.

### F5 — Info · Scanner coverage — Scanner coverage gap on multi-harness skill collections — only AGENTS.md + CLAUDE.md (2 root files) were enumerated; 468 skill files under `<harness>/skills/` were not

*Open scanner gap · Continuous · → Read this scan in conjunction with a manual audit of `source/skills/impeccable/` if you're sensitive to skill-content prompt-injection vectors. Same gap was documented for mattpocock/skills (catalog entry 27).*

The Phase 1 harness (`docs/phase_1_harness.py::step_2_5_agent_rule_files()`) enumerates known root-level rule files (AGENTS.md, CLAUDE.md, etc.) but does not recursively traverse harness subdirectories. For impeccable, this means only the 2 root files (AGENTS.md L69 + CLAUDE.md L288) were captured; the 468 skill `.md` files under all 13 `<harness>/skills/<command>/` subtrees were not enumerated.

Same gap previously documented for catalog entry 27 (mattpocock/skills): 22 SKILL.md files not enumerated. The fix is a V1.2.x patch candidate: extend `step_2_5_agent_rule_files()` to recursively enumerate `<harness>/skills/**/*.md` for known harness-name patterns (.claude, .agents, .cursor, .gemini, .kiro, .opencode, .pi, .qoder, .rovodev, .trae, .trae-cn, .github, plugin) and run prompt-injection regex over each, with a deduplication pass that detects when N fanout copies share the same source content.

The F4 finding's prompt-injection surface analysis is informed by the build-pipeline structure (single source-of-truth, regenerated mechanically) per CLAUDE.md L94-102, not by a per-file scan of the 468 skill files. A targeted scanner would surface more granular information.

**How to fix.** Scanner-side (V1.2.x patch candidate): extend `step_2_5_agent_rule_files()` to recursively enumerate `<harness>/skills/**/*.md` for known harness-name patterns (.claude, .agents, .cursor, etc.) and run prompt-injection regex over each, with a deduplication pass to detect when 13 fanout copies share the same source. Same fix would close the gap for mattpocock/skills (entry 27).

---

## 02A · Executable file inventory

> Two CI workflow files were classified as 'executable' by the Phase 1 harness (.github/workflows/ci.yml, .github/workflows/skill-review.yml). The harness's executable-file detector did not classify the package's JS executables (no shebangs on the imported `.mjs` modules), so the security-relevant binaries below come from manual inspection of `bin/`, `src/`, and `scripts/`. The published npm package ships only `bin/`, `src/`, and `LICENSE` per `package.json` `files` declaration.

### Layer 1 — one-line summary

- 5 executable files of consequence: `bin/cli.js` (Node CLI entrypoint, ~57 lines), `bin/commands/skills.mjs` (skills install/update — uses `execSync` for `npx skills add` + `unzip` + `git status`; ~649 lines), `src/detect-antipatterns.mjs` (detector engine — 3,600 lines, loaded by build scripts via `new Function()` per F1), `src/detect-antipatterns-browser.js` (generated browser variant), and `scripts/build.js` (Bun build orchestrator — uses `new Function()` per F1; not in published npm package). Plus 2 GitHub Actions workflows (`ci.yml`, `skill-review.yml`).

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `bin/cli.js` | Node CLI entrypoint | Node >=18 ESM | None (dispatches to detect-antipatterns.mjs and skills.mjs) | None directly | Routes `detect` / `skills help|install|update|check` / `--version` / `--help`. ~57 lines. |
| `bin/commands/skills.mjs` | Node module — skills install/update CLI | Node >=18 ESM | execSync (3 sites: `npx skills add`, `unzip`, `git status --porcelain`) | GET https://impeccable.style/api/commands ; GET https://impeccable.style/api/download/bundle/universal ; transitively `npx skills add` fetches from GitHub | F2 supply-chain finding source. Closed #100 added shell-quoting hardening for argument paths in late April 2026. ~649 lines. |
| `src/detect-antipatterns.mjs` | Detector engine library | Node >=18 ESM (also runs under jsdom in tests) | None at runtime; ANTIPATTERNS array is read by build scripts via `new Function()` (F1 build-time RCE) | None | Primary library export of the `impeccable` npm package. Re-exported via `src/detect-antipatterns-browser.js` for the Chrome extension. ~3,600 lines. |
| `scripts/build.js` | Bun build orchestrator (NOT in published npm package) | Bun runtime (CI + local dev) | `new Function()` at line 122 (F1 — see #92 OPEN) | None | Runs at `bun run build`. Excluded from the published package by package.json `files` whitelist. Build-time RCE bounded to contributors. |
| `.github/workflows/skill-review.yml` | GitHub Actions workflow — Tessl Skill Review | GitHub-hosted runner | Tessl-provided action; runs on PRs touching SKILL.md files | Outbound to Tessl review API | Adds an automated skill-quality review surface but is NOT a required-review gate (per F0 governance). |
| `.github/workflows/ci.yml` | GitHub Actions workflow — CI | GitHub-hosted runner | Standard test/build run; pinned action versions not yet audited | Standard CI (npm install, etc.) | General CI workflow; runs on every PR. |

The published npm package (`impeccable@2.1.8`) ships only `bin/`, `src/`, and `LICENSE` per the `files` whitelist in `package.json`. The `scripts/` directory containing the F1 `new Function()` build-time RCE is NOT shipped to consumers — it lives only in the GitHub repo and runs only when contributors execute `bun run build` or `bun run dev`.

---

## 03 · Suspicious code changes

> Sample = population: 49 closed PRs in lifetime (46 merged, 3 closed without merge). Formal-review rate (GitHub reviewDecision set) = 36.7% (18/49). Any-review rate (reviewDecision set OR a review event posted) = 53.1% (26/49). Self-merge count = 19 of 49 (38.8%). Security-flagged (title contains a security keyword) = 1 (open). Tessl Skill Review (CI on PRs touching skills) and GitHub Copilot code review (CI on PRs generally) both run on every PR but neither is a required-review gate. A representative sample of recent PRs:

Sample: the 49 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 36.7% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#129](https://github.com/pbakaus/impeccable/pull/129) | Detector: add italic-serif display headline + hero eyebrow chip rules (closes #127) | vinaypokharkar | pbakaus | Approved (1 reviewer + Tessl + Copilot CI) | External community contribution; merged after CI review |
| [#130](https://github.com/pbakaus/impeccable/pull/130) | Migrate site from Bun to Astro (build-system change) | pbakaus | pbakaus | No formal decision | Self-merge; build-system change touches dev pipeline |
| [#124](https://github.com/pbakaus/impeccable/pull/124) | fix(live): switch live-poll to execFileSync, validate ids strictly (security hardening) | pbakaus | pbakaus | No formal decision | Self-merge on security-relevant fix; should have had a reviewer |
| [#123](https://github.com/pbakaus/impeccable/pull/123) | feat(load-context): support context dir outside repo root (closes #119) | 0x963D | pbakaus | Approved | External contribution; touches path resolution |
| [#100](https://github.com/pbakaus/impeccable/pull/100) | Fix security vulnerabilities in critique skill (shell injection, port-squatting, prompt-injection warnings) | pbakaus | pbakaus | No formal decision | Self-merge on security fix; closed within ~7 days of report |
| [#93](https://github.com/pbakaus/impeccable/pull/93) | security: use JSON.stringify for selector escaping in devtools panel | pbakaus | pbakaus | No formal decision | Self-merge on security fix; closed within ~7 days |
| [#74](https://github.com/pbakaus/impeccable/pull/74) | ci: Tessl skill review for SKILL.md pull requests (CI workflow addition) | rohan-tessl | pbakaus | Approved | External contribution from Tessl team; adds CI review surface |

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo | pbakaus/impeccable |  |
| Stars / Forks | 24,298 / 1,259 |  |
| Created | 2025-11-16 (5.5 months old at scan time) |  |
| License | Apache-2.0 |  |
| Primary language | JavaScript (ESM, Bun + Node) |  |
| HEAD SHA | 444e4acad38a00ec4b837ce57e9b4ef561297450 |  |
| Latest published version | impeccable@2.1.8 (npm) |  |
| Default branch | main |  |
| Top contributor share | 96.9% (pbakaus) |  |
| Total contributors | 18 |  |
| Closed PRs sampled | 49 (all closed in lifetime) |  |
| PR formal review rate | 36.7% |  |
| PR any-review rate | 53.1% |  |
| Self-merge count / rate | 19 / 38.8% |  |
| Branch protection | None (classic 404, 0 rulesets, 0 rules-on-default) |  |
| CODEOWNERS | .github/CODEOWNERS — `* @pbakaus` |  |
| Published GHSA / SECURITY.md / dependabot.yml | 0 / absent / absent |  |
| OSSF Scorecard | Not indexed (HTTP 404) |  |
| Skill files (per harness × N harnesses) | 36 × 13 = 468 (single source `source/skills/impeccable/`) |  |
| Distribution channels | 1 real (npm `impeccable`); 23 test fixtures detected |  |
| Open security-tagged issues | 2 (#92 build-time RCE 22d open with fix-PR; #94 audit tracking 22d open) |  |
| Recently closed security issues | 2 (#100 + #93 closed 2026-04-29, ~7-10 days from open) |  |

---

## 06 · Investigation coverage

| Check | Result |
|-------|--------|
| Phase 1 harness | phase_1_harness.py V0.2 (gh api + OSSF + osv.dev + tarball extraction; gitleaks unavailable; Dependabot alerts gated by admin scope) |
| Phase 1 raw fields populated | 28 of 28 |
| Tarball file count | 1,314 files (31MB extract); 0 symlinks stripped |
| Phase 3 compute | compute.py V2 calibration (classify_shape() + compute_scorecard_cells_v2() + compute_c20_severity + compute_solo_maintainer) |
| Phase 3 shape classification | library-package (medium confidence) per RULE-publishable-manifest. Real shape is multi-harness agent-skills-collection — not yet captured by classifier (signal_vocabulary_gap on harness-fanout-skills heuristic). Phase 4 LLM authored shape into catalog_metadata directly. |
| Phase 3 advisory→Phase 4 overrides | 2 cells (Q2 RED→AMBER missing_qualitative_context; Q4 AMBER→AMBER with edge_case explained — channel count denominator misleading) |
| OSSF Scorecard | Not indexed (HTTP 404) |
| Dependabot alerts | Unavailable (HTTP 403 admin scope); osv.dev fallback ran 9 lookups, 0 advisories |
| gitleaks (secrets-in-history) | Unavailable (gitleaks not installed on scanner host) |
| Skill-content prompt-injection scan | scope-restricted — only AGENTS.md + CLAUDE.md (2 root files) scanned; 468 skill files not enumerated. 1 signal in CLAUDE.md is meta-documentation, not a payload |
| Distribution channels detected | 24 (1 real + 23 test fixtures); 1/24 install paths verified; 0/24 artifact-verified; 0/24 pinned |
| Tarball extraction | ✅ 1314 files |
| osv.dev | ℹ  |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4995/5000 remaining |

**Gaps noted:**

1. OSSF Scorecard — not indexed: Scorecard API returned HTTP 404 (repo too new or not picked up by OSSF's discovery). Governance signals derived from raw `gh api` data and CODEOWNERS read.
2. Dependabot alert count — unavailable: GitHub API returned HTTP 403 (admin scope required). Fell back to osv.dev — queried 9 manifests, returned 0 known vulnerabilities. Open security issues #92 + #94 documented via repo issue triage.
3. Secrets-in-history (gitleaks) — unavailable: gitleaks not installed on the scanner host. The 0-secrets harness result reflects only regex-grep over working-tree file content, not full git-history scan.
4. Skill-file enumeration — scope-restricted: harness `code_patterns.agent_rule_files` enumerated only the 2 root-level rule files (AGENTS.md + CLAUDE.md). The 468 skill `.md` files under `.claude/skills/`, .cursor/skills/, ... 13 harness directories) were not enumerated. F5 documents this as a V1.2.x patch candidate.
5. Distribution-channel verification — scope-restricted: harness emitted 24 npm channels but 23 are test fixtures (`tests/framework-fixtures/vite8-react-*`) used as antipattern-detection test inputs, not real distributable packages. Only `impeccable@2.1.8` is a real distribution channel; its install path was verified, but its artifact provenance was not.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 0 priority

### Other evidence

#### Evidence 1 — pbakaus is the sole privileged contributor on a 24,298-star, 5.5-month-old repo (created 2025-11-16). The remaining 3.1% of contributions are spread across community PR authors. CODEOWNERS = `* @pbakaus`.

```bash
gh api repos/pbakaus/impeccable/contributors --jq 'sort_by(-.contributions) | [.[0:5][] | {login, contributions}]'
```

Result:
```text
Top contributor: pbakaus 96.9% (computed via solo-maintainer rule). Total contributors: 18. CODEOWNERS at `.github/CODEOWNERS`: `# Global ownership — auto-request review from Paul on every PR\n* @pbakaus\n# Build system\nscripts/ @pbakaus\n# Source content (skills & commands)\nsource/ @pbakaus`.
```

*Classification: fact*

#### Evidence 2 — Branch protection is entirely absent. Classic protection HTTP 404 (no rule), 0 rulesets, 0 rules-on-default. Owner is a User account (not Org → no org rulesets possible). 49 closed PRs include 19 self-merges (38.8%).

```bash
gh api repos/pbakaus/impeccable/branches/main/protection ; gh api repos/pbakaus/impeccable/rulesets ; gh api repos/pbakaus/impeccable/branches/main/rules
```

Result:
```text
branch_protection.classic.status = 404 (no protection); rulesets.entries = []; rules_on_default.entries = []; owner_type = User; org_rulesets.note = `owner is not an Organization`. pr_review.{total_closed_prs: 49, total_merged_lifetime: 46, formal_review_rate: 36.7, any_review_rate: 53.1, self_merge_count: 19, security_flagged_count: 1}.
```

*Classification: fact*

#### Evidence 3 — Issue #92 'security: replace new Function() eval with direct ESM import' is OPEN 22 days. Fix-PR is authored but unmerged. Author of issue documents 3 sites of `new Function()` build-time RCE: `scripts/build.js:122` (runs during `bun run build`), `scripts/build-extension.js:63` (runs during extension build), `scripts/lib/sub-pages-data.js:107` (runs at dev-server startup AND during build). Mutating the regex-matched ANTIPATTERNS source region grants arbitrary code execution at build time.

```bash
gh api repos/pbakaus/impeccable/issues/92 --jq '{title, state, age_days: (((now - (.created_at|fromdateiso8601))/86400)|round), comments}'
```

Result:
```text
{title: 'security: replace new Function() eval with direct ESM import', state: 'open', age_days: 22, comments: 1}. Cross-referenced by tracking issue #94 'Security and consistency audit findings' (also OPEN 22 days) which lists this as a 'High' severity finding.
```

*Classification: fact*

#### Evidence 4 — Two security issues were closed within ~7-10 days in late April 2026: #100 'Fix security vulnerabilities in critique skill' (closed 2026-04-29) addressing shell injection in `npx impeccable [target]`, port-squatting in `npx impeccable live`, and prompt-injection warnings; and #93 'security: use JSON.stringify for selector escaping in devtools panel' (closed 2026-04-29) hardening `extension/devtools/panel.js:503-511` against selector-injection.

```bash
gh api 'repos/pbakaus/impeccable/issues?state=closed&per_page=100' --jq '.[] | select(.title|test("security|vuln|injection|exploit|XSS|RCE"; "i")) | {n: .number, t: .title, closed: .closed_at}'
```

Result:
```text
Closed: #100 'Fix security vulnerabilities in critique skill' (2026-04-29T01:05:10Z); #93 'security: use JSON.stringify for selector escaping in devtools panel' (2026-04-29T01:09:55Z). Both fixes landed via maintainer self-merge.
```

*Classification: fact*

#### Evidence 5 — Zero published GitHub Security Advisories (GHSA), no SECURITY.md at the repo root, no `.github/dependabot.yml`. Dependabot alerts API returned HTTP 403 (admin scope required); osv.dev fallback returned 0 advisories across 9 dependency lookups. Despite this, security-tagged issues are triaged with explicit `security:` title prefix.

```bash
gh api repos/pbakaus/impeccable/security-advisories ; gh api repos/pbakaus/impeccable/contents/SECURITY.md ; gh api repos/pbakaus/impeccable/contents/.github/dependabot.yml
```

Result:
```text
security-advisories: 0 published. SECURITY.md: 404. .github/dependabot.yml: 404. defensive_configs.entries: [{file: '.github/dependabot.yml', present: false}, {file: 'SECURITY.md', present: false}]. dependencies.dependabot_alerts: {status: 403, note: 'admin scope required; falling back to osv.dev'}. osv_lookups: 9 manifests checked, 0 advisories returned.
```

*Classification: fact*

#### Evidence 6 — Install path 1 — `npx impeccable skills install` — chains a 3-hop supply trust: (a) npm registry serves the `impeccable` CLI; (b) the CLI then `execSync('npx skills add pbakaus/impeccable')` which fetches from vercel-labs/skills npm CLI; (c) vercel-labs/skills resolves and downloads from GitHub. Install path 2 — `npx impeccable skills update` — fetches `https://impeccable.style/api/download/bundle/universal` over HTTPS with no signature verification and unzips with `execSync('unzip -qo "${tmpZip}" -d "${tmpDir}"')`.

```bash
rg -n 'execSync|API_BASE|downloadAndExtractBundle' bin/commands/skills.mjs
```

Result:
```text
bin/commands/skills.mjs:20: const API_BASE = 'https://impeccable.style';
bin/commands/skills.mjs:102: execSync(`unzip -qo "${tmpZip}" -d "${tmpDir}"`, { encoding: 'utf8' });
bin/commands/skills.mjs:339: execSync(`npx skills add pbakaus/impeccable${yes ? ' -y' : ''}`, { stdio: 'inherit' });
bin/commands/skills.mjs:472: const status = execSync('git status --porcelain', { cwd: root, encoding: 'utf8' });
downloadFile() uses node:https get() over HTTPS with no integrity check.
```

*Classification: fact*

#### Evidence 7 — Skill content is regenerated from a single source of truth (`source/skills/impeccable/`) and emitted to 13 harness directories on every `bun run build`. 36 skill `.md` files per harness × 13 harnesses = 468 skill files in the working tree. Each one becomes part of an LLM's instruction context when its harness loads it.

```bash
for d in .claude .agents .cursor .gemini .kiro .opencode .pi .qoder .rovodev .trae .trae-cn .github plugin; do   echo "$d: $(find $d/skills -type f -name '*.md' 2>/dev/null | wc -l)"; done
```

Result:
```text
.claude/skills/*.md: 36; .agents/skills/*.md: 36; .cursor/skills/*.md: 36; .gemini/skills/*.md: 36; .kiro/skills/*.md: 36; .opencode/skills/*.md: 36; .pi/skills/*.md: 36; .qoder/skills/*.md: 36; .rovodev/skills/*.md: 36; .trae/skills/*.md: 36; .trae-cn/skills/*.md: 36; .github/skills/*.md: 36; plugin/skills/*.md: 36. Total skill files: 468 (552 .md files under any */skills/* path including READMEs and reference subdocs). Single source `source/skills/impeccable/`. CLAUDE.md L96 explicitly documents the build-time fanout.
```

*Classification: fact*

#### Evidence 8 — Repo CI workflows include automated review surfaces: `.github/workflows/ci.yml`, `.github/workflows/tessl.yml` (Tessl Skill Review — runs Tessl's external skill-quality reviewer on PRs touching skills), and `.github/workflows/copilot-review.yml` (GitHub Copilot code review). HEAD commit `444e4ac` was an external community PR (#127/#129) by vinaypokharkar adding two new detection rules — first/recent visible external code-contribution merge.

```bash
gh api repos/pbakaus/impeccable/actions/workflows --jq '.workflows[] | {name, state}' ; gh api repos/pbakaus/impeccable/commits/main --jq '{author: .commit.author.name, files_changed: (.files|length)}'
```

Result:
```text
Workflows: CI (active), Tessl Skill Review (active), Copilot code review (active). HEAD commit author: Vinay Pokharkar (external — github.com/vinaypokharkar). Files changed: 22 (rule code + skill copy across all 13 harness dirs + tests + fixtures). Commit verified-signature: valid (GitHub web UI).
```

*Classification: fact*

#### Evidence 9 — Distribution-channel detection found 24 npm channels but 23 of them are TEST FIXTURES under `tests/framework-fixtures/` (vite8-react-* variants, nextjs-app-router, sveltekit, nuxt, astro) plus `demos/landing-demo`. Only `npm-impeccable` (the root `impeccable@2.1.8` package) is a real distribution channel. Harness verified install path for `npm install impeccable` (install_path_verified=true) but did not verify artifact provenance (artifact_verified=false) and the package is not pinned (no integrity hash in install command).

```bash
rg -n '"name":' package.json tests/framework-fixtures/*/files/package.json demos/*/package.json | head -25
```

Result:
```text
Real package: impeccable@2.1.8 (license Apache-2.0, bin: impeccable: bin/cli.js, files: ['bin/', 'src/', 'LICENSE']). 23 test fixtures named *-fixture exist under tests/framework-fixtures/ with their own package.json but are not published. distribution_channels.channels: 24 entries; coverage_affirmations.distribution_channels_verified: '1/24'.
```

*Classification: fact*

#### Evidence 10 — OSSF Scorecard returned HTTP 404 (repo not enrolled in OSSF Scorecard's automated weekly scan). osv.dev queried 9 manifests and returned 0 known vulnerabilities. gitleaks not available on the scanner host; the 0-secrets harness result reflects only regex-grep over file content, not full git-history secret scan.

```bash
curl -sI https://api.securityscorecards.dev/projects/github.com/pbakaus/impeccable
```

Result:
```text
OSSF Scorecard HTTP 404 (not indexed). osv_lookups: 9 manifest queries, 0 advisories. coverage_affirmations.gitleaks_available: false; coverage_affirmations.gitleaks_explanation: 'gitleaks not installed; install to cover secrets-in-history'. coverage_affirmations.distribution_channels_verified: '1/24'. coverage_affirmations.windows_surface_coverage: 'scanned'. coverage_affirmations.prompt_injection_scan_completed: true.
```

*Classification: fact*

#### Evidence 11 — Prompt-injection scan over root agent-rule files (AGENTS.md + CLAUDE.md) returned 1 signal — a meta-discussion line in CLAUDE.md describing how the harness inlines `SKILL.md` into the system prompt. Not a payload; a documentation note about the consumer-side instruction-loading mechanism. The harness did NOT recurse into the 468 skill files under `*/skills/<command>/` — that is a documented coverage gap (F5).

```bash
python3 docs/phase_1_harness.py pbakaus/impeccable --head-sha 444e4ac --skip-tarball  # inspects code_patterns.prompt_injection_scan
```

Result:
```text
scanned_files: ['AGENTS.md', 'CLAUDE.md']. signal_count: 1. signal location: CLAUDE.md L288 — 'The harness inlines `SKILL.md` into the system prompt for "skill-on", stripping sections irrelevant to an API-driven craft run...' (meta-documentation, not an injection payload). scan_method: tarball. Skill content under .claude/skills/, .cursor/skills/, etc. — 468 files — was NOT enumerated.
```

*Classification: fact*

#### Evidence 12 — Repo growth velocity: 24,298 stars + 1,259 forks acquired in 5.5 months since creation 2025-11-16. The current published npm version is `impeccable@2.1.8`, the Claude Code plugin manifest declares `.claude-plugin/plugin.json` `version`, and the Chrome extension has its own `extension/manifest.json` version — three independently versioned components per CLAUDE.md L155-176.

```bash
gh api repos/pbakaus/impeccable --jq '{stars: .stargazers_count, forks: .forks_count, created: .created_at}'
```

Result:
```text
stargazers_count: 24298, forks_count: 1259, created_at: 2025-11-16T01:52:04Z. Default branch: main; pushed_at: 2026-05-02T19:01:43Z (HEAD captured at scan time). License: Apache-2.0. Tarball size: 1314 files.
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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-05-02 · scanned main @ `444e4acad38a00ec4b837ce57e9b4ef561297450` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
