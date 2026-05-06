# onecli/onecli — Simple Report

**Verdict: ⚠ Caution.** Install with these conditions in mind.

onecli/onecli — a 2-month-old, 2,093-star credential vault for AI agents. The architecture is a Rust gateway (`apps/gateway`) that does HTTPS MITM interception via a generated CA cert, paired with a Next.js dashboard (`apps/web`) and a Postgres store. Encryption is AES-256-GCM via the audited `ring` crate. Solo-maintained (guyb1 85%), 0.0% formal review rate across 208 merged PRs, no CODEOWNERS, no SECURITY.md, no published GHSAs. Distribution: `curl -fsSL https://onecli.sh/install | sh` pulls a `latest`-tagged Docker image and a compose file from `main` — three mutable trust anchors. The MITM design means installing OneCLI's CA on an agent host puts the gateway on the trust path of every HTTPS call the agent makes, not just the calls you've configured for credential injection. Past security feedback (#131 0.0.0.0 binding) was handled responsively (closed in days). Issue queue is currently clean (0 open security-tagged); PR #234 (SBOM crypto audit) is sitting open for 5 days. Verdict: Caution — encryption is solid, governance is solo + unstructured, install path is unpinned, MITM design expands trust surface significantly. Safe to evaluate in isolation; pin the version, isolate the host, and treat OneCLI as a single-purpose secrets-handling appliance — not a casual install on a developer machine.

**Scanned:** 2026-05-06 · main @ fa6468e · 2,093 stars · Apache-2.0 · TypeScript

**Scan coverage gaps:** OSSF not indexed · Dependabot unavailable · gitleaks unavailable · MITM-design threat-surface coverage gap

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 0.0% formal review rate over 208 PRs; active ruleset on main but no required-reviewer rule; no CODEOWNERS; recent self-merges include credential-resolution + cloud-apps PRs
- ✓ **Do they fix problems quickly?** Yes — closed issue #131 (0.0.0.0 binding) was fixed within days; 0 open security-tagged issues at scan time
- ✗ **Do they tell you about problems?** No — no SECURITY.md, no published GHSAs, no .github/dependabot.yml; consumers won't get Dependabot alerts when a fix ships
- ⚠ **Is it safe out of the box?** Partly — encryption is solid (AES-256-GCM via ring), but the documented install path (`curl|sh` + `latest` Docker tag + main-tracking compose URL) is unpinned, and the gateway's MITM design expands trust surface significantly

## Top concerns

1. **[Warning] Solo maintainer (85.0% commit share) on a 2-month-old credential vault with no CODEOWNERS and 15 total contributors** The structural human-review gate between maintainer code changes and the published Docker image is essentially the maintainer's own discipline.

2. **[Warning] Active branch ruleset on `main` does not enforce required-reviewer count — 0.0% formal review rate across 208 merged PRs, observed self-merge pattern in recent sample** Self-merge is the primary merge mode.

3. **[Warning] `curl|sh` installer downloads `docker-compose.yml` from `main` (mutable) and pins the Docker image to `latest` (mutable) — no SHA / tag pin / signature verification** If you take the documented happy path (`curl|sh` → pull `latest`), you are trusting the maintainer to control three mutable surfaces (DNS, main branch, latest tag) for the lifetime of your install.

## What should I do?

**Install with these conditions.** If you self-host, pin the Docker image to a specific tag (`ONECLI_VERSION=1.21.0`) rather than `latest`, review the source for the version you're running, and treat OneCLI as a single-trust-anchor service — compromise of one maintainer credential reaches every secret you've stored.

---

*stop-git-std · scanned 2026-05-06 · [onecli/onecli](https://github.com/onecli/onecli)*
