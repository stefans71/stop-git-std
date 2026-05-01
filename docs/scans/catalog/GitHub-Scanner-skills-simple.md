# mattpocock/skills — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

mattpocock/skills — 47.9k-star Claude Code skill collection (22 SKILL.md, 1,815 lines), 3 months old, solo-maintained. Zero releases (rolling install), zero branch protection, no SECURITY.md (PR proposing one was closed without merging). Install delegates to vercel-labs/skills npm CLI. Skill content sampled is benign and consent-driven — risk is structural (solo + rolling + no second-human gate). Caution.

**Scanned:** 2026-04-30 · main @ b843cb5 · 47,917 stars · MIT · Shell

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — solo maintainer (87.3% commit share + 1 owner-test account), 0% formal review on the 1 lifetime merged PR, no branch protection, no CODEOWNERS, no rulesets
- ⚠ **Do they fix problems quickly?** Unknown — 3-month-old repo with 1 lifetime merged PR and 0 closed-merged security PRs to grade response cadence on; no overdue items either
- ✗ **Do they tell you about problems?** No — no SECURITY.md (PR #67 proposing one was closed without merging), 0 published GHSA advisories, no documented disclosure channel
- ⚠ **Is it safe out of the box?** Partly — README explains what the install does and lists the skills that will be activated, but install delegates trust to vercel-labs/skills npm package and 22 SKILL.md files are unsigned and unverifiable post-install

## Top concerns

1. **[Warning] Solo-maintainer (87.3% share, 1 active human + 1 owner-test account) with zero governance protections on a 47.9k-star skill registry** There is no structural second-human gate between mattpocock pushing to main and a user's `~/.claude/skills/` receiving that content.

2. **[Warning] Zero formal releases — install path resolves to whatever HEAD points at on main at install time** There is no release-pinned install path.

3. **[Warning] No SECURITY.md (an external PR proposing one was closed without merging) — disclosure path is informal** If you want to report a vulnerability privately, the path is unclear.

## What should I do?

**Install with these conditions.** Inspect the skill content you intend to install before linking; pin to a specific commit if you want a stable surface.

---

*stop-git-std · scanned 2026-04-30 · [mattpocock/skills](https://github.com/mattpocock/skills)*
