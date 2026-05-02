# pbakaus/impeccable — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

pbakaus/impeccable — 24.3k-star design-anti-pattern detection toolkit shipped as 36 skill files fanned out to 13 different AI coding harnesses (.claude, .cursor, .gemini, .agents, etc.) plus a Node CLI plus a Chrome extension. Created 5.5 months ago, single-author (96.9% share), no branch protection, 38.8% self-merge rate. 4 security issues have been triaged (2 closed in ~7-10 days, 2 open with fix-PRs sitting). Open #92 is a build-time RCE in 3 build scripts via `new Function()`; affects contributors only, not consumers of the published CLI. Install topology is 3-hop for skills (`npx impeccable skills install` → vercel-labs/skills → GitHub) with no signature verification on the alternative CDN bundle path; CLI-only `npx impeccable detect [paths]` is single-hop and safe. 0 published GHSA + no SECURITY.md = consumers won't get Dependabot alerts when fixes ship. The skill-content surface (468 files) amplifies single-key compromise blast radius but trusts only one source-of-truth directory (`source/skills/impeccable/`, 36 files).

**Scanned:** 2026-05-02 · main @ 444e4ac · 24,298 stars · Apache-2.0 · JavaScript

**Scan coverage gaps:** OSSF not indexed · Dependabot unavailable · gitleaks unavailable · Skill-file enumeration scope-restricted · Distribution-channel verification scope-restricted

---

## Trust scorecard

- ⚠ **Does anyone check the code?** Partly — 53% any-review on n=49, but solo maintainer with no branch protection and 39% self-merge rate; Tessl + Copilot CI provides automated review only
- ⚠ **Do they fix problems quickly?** Partly — 22-day-old open #92 build-time RCE has an authored fix-PR sitting; 2 prior security issues closed within ~7-10 days in late April
- ✗ **Do they tell you about problems?** No — 0 published GHSA, no SECURITY.md, no dependabot.yml; security fixes ship silently from the consumer's POV (no Dependabot alert, no npm advisory)
- ⚠ **Is it safe out of the box?** Partly — install-path multi-hop (npx impeccable skills install → vercel-labs/skills npm CLI → GitHub) with no signature verification on the bundle path; CLI-only path (`npx impeccable detect`) is single-hop and safe to run

## Top concerns

1. **[Warning] Solo maintainer (96.9% commit share, CODEOWNERS = `* @pbakaus`) with zero branch protection on a 24k-star, 5.5-month-old project** There is no structural second-human gate between pbakaus pushing to `main` and 13 different AI harnesses across the install base receiving updated skill content.

2. **[Warning] `new Function()` build-time RCE in 3 build scripts (issue #92 OPEN 22 days; fix-PR authored, not merged)** If a malicious or honest-mistake commit lands in `main` modifying the regex-matched ANTIPATTERNS region, every contributor who runs `bun run build` or `bun run dev` afterward executes attacker-controlled JavaScript in their dev environment with their full file-system access.

3. **[Warning] Three-hop install supply chain (impeccable npm → vercel-labs/skills npm → GitHub or impeccable.style CDN) with no signature verification** Two of the three skill-install paths route through trust intermediaries beyond pbakaus: vercel-labs/skills (an upstream npm CLI bug per CLAUDE.md L529) and the impeccable.style CDN bundle.

## What should I do?

**Install with these conditions.** Pin to a specific commit SHA (not `@latest`) when installing skills; review the generated .claude/skills/ tree against the upstream source before running them in a sensitive repo.

---

*stop-git-std · scanned 2026-05-02 · [pbakaus/impeccable](https://github.com/pbakaus/impeccable)*
