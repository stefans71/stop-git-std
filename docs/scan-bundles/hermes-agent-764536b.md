# NousResearch/hermes-agent Scan — Evidence Bundle

## Repo identity
- **Repo:** NousResearch/hermes-agent
- **Description:** "The agent that grows with you"
- **HEAD SHA:** 764536b684b081eead7f4394911b4399a66e7f9c (7-char: 764536b)
- **Default branch:** main
- **Created:** 2025-07-22
- **Last push:** 2026-04-17T00:39:52Z (day of scan)
- **Stars:** 93,679 | Forks: 13,056
- **License:** MIT
- **Archived:** false | Issues enabled: true | Is fork: false
- **Language:** Python
- **Fetch path:** tarball at pinned SHA; 1,739 files extracted
- **Install mechanism:** pyproject.toml with setuptools backend

## Owner
- **NousResearch** — Organization, created 2023-05-20, 71 public repos, 2,969 followers
- Owner type confirmed: Organization (triggers C20 org-ruleset check)

## Contributors
- teknium1: 2,959 commits (~82% of total)
- 0xbyt4: 185 commits
- kshitijk4poor: 71 commits
- 29 other contributors with 8-61 commits each
- Solo-maintainer signal: teknium1 has ~82% of commits

## Governance (C20 check)
1. Classic branch protection on main: 404 (no classic protection rule)
2. Repo-level rulesets: 1 active ruleset "protect-main" — deletion + non_fast_forward only
3. Rules on default branch: deletion + non_fast_forward (no review requirement)
4. Org-level rulesets: unknown (403 scope gap — needs admin:org)
5. CODEOWNERS: not found in any standard path
6. Community profile: health 75%, no security policy
7. No SECURITY.md

## Releases
- 9 releases, v0.2.0 (2026-03-12) to v0.10.0 (2026-04-16)
- Weekly cadence, very active

## Dependabot / advisories
- Dependabot alerts: 403 scope gap (unknown)
- Security advisories: empty array (none published)
- pyproject.toml has CVE comments on pinned deps

## CI workflows
- 8 workflows, ALL actions SHA-pinned (100%)
- No pull_request_target usage
- supply-chain-audit.yml: custom litellm-pattern defense
- tests.yml: API keys blanked in env

## PR review rate (F11)
- 15 sampled: 0% review rate (both metrics)
- teknium1 authored 13/15, helix4u 2/15

## Open security issues
- #10693: OAuth PKCE verifier leak
- #7071: Sandbox PYTHONPATH injection
- #3971: Missing token redaction patterns
- #8035: file_tools reads auth.json
- #4427: /proc/environ bypass
- #11307: Telegram webhook spoofing

## FINDINGS SUMMARY

### F0: Governance gap — no review gate on main (Warning, Active)
### F1: Curl-pipe-bash install fetches from HEAD of main (Warning, Active)
### F2: Multiple open security vulnerabilities (Warning, Active)
### F3: No security policy (Info, Active)
### F4: Solo-maintainer commit concentration (Info, Active)
### F5: AGENTS.md — standard development guide (OK, Informational)
### F6: CI security posture — SHA-pinned, supply-chain audit (OK, Informational)
### F7: Dependencies managed with CVE awareness (OK, Informational)

## Proposed verdict: CAUTION (split on Deployment axis)
Drivers: F0 + F1 + F2

## Proposed scorecard
- Supply chain: Amber (F0, F1)
- Code & runtime: Amber (F2)
- Maintenance & governance: Amber (F0, F4)
- Transparency & response: Green (F3 minor)
