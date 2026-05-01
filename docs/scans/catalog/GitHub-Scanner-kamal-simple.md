# basecamp/kamal — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

Kamal is Basecamp's deploy tool — 14k-star Ruby gem that SSHes into operator-configured servers and runs docker commands for zero-downtime rollouts. 71 semver releases, CodeQL + Copilot-review ruleset, active triage — but 4.7% formal review, 51% self-merge, no CODEOWNERS, no SECURITY.md. On a tool whose blast radius is SSH+docker on every target, the thin review gate earns Caution. Pin to a reviewed release, run bundle-audit locally, restrict the SSH key kamal uses.

**Scanned:** 2026-04-20 · main @ 6a31d14 · 14,101 stars · MIT · Ruby

---

## Trust scorecard

- ⚠ **Does anyone check the code?** Partly — Copilot ruleset + CodeQL + 71 semver releases, but 4.7% formal review + 51% self-merge + no CODEOWNERS
- ✓ **Do they fix problems quickly?** Yes — 0 open security issues, 71 releases (latest 33 days old), active triage
- ⚠ **Do they tell you about problems?** Partly — CONTRIBUTING exists, but no SECURITY.md and 0 published advisories on a privileged tool
- ⚠ **Is it safe out of the box?** Partly — semver-release discipline is real, but RubyGems publisher + deploy credentials are not verified out-of-band

## Top concerns

1. **[Warning] Two-maintainer concentration + 4.7% formal review on a privileged remote-execution tool** Most changes on main have landed without independent human review.

2. **[Warning] No SECURITY.md on a privileged deployment tool** Vulnerability reporters with a pre-patched finding default to the public issue tracker because there's no documented alternative.

3. **[Info] Dependabot config watches only github-actions — RubyGems deps unwatched** The runtime dependency graph — the piece that ACTUALLY runs on every kamal invocation — has no automated advisory watch configured.

## What should I do?

**Install with these conditions.** Pin to a reviewed release tag; verify publisher account security before major upgrades.

---

*stop-git-std · scanned 2026-04-20 · [basecamp/kamal](https://github.com/basecamp/kamal)*
