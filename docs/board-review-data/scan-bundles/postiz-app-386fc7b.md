# postiz-app Scan — Evidence Bundle

Scan date: 2026-04-16
HEAD SHA: 386fc7b049737d5047bc83c6c19dd291e22eb28c (short: 386fc7b)
Fetch path: tarball at pinned SHA
File count: 881

## Repo identity

- **Repo:** gitroomhq/postiz-app
- **Owner type:** Organization
- **Default branch:** main
- **Created:** 2023-07-08
- **Last push:** 2026-04-17
- **Stars:** 28,822 / Forks: 5,141
- **License:** AGPL-3.0
- **Description:** The ultimate social media scheduling tool, with AI
- **Archived:** No
- **Issues enabled:** Yes

## Owner

- gitroomhq — Organization, created 2023-03-20, 17 public repos, 371 followers
- nevo-david (top contributor, 1352 commits / 69.0% share) — User, created 2022-02-21, 46 public repos, 1961 followers
- egelhaus (2nd, 344 commits / 17.6%) — User, created 2024-01-17, 11 public repos, 36 followers
- jamesread (3rd, 159 commits / 8.1%) — User, created 2012-07-23, 133 public repos, 229 followers

## Contributors

Top contributor nevo-david has 69.0% of commits. egelhaus 17.6%. 30 contributors visible in top-30 API.

## Governance (C20 check)

Classic protection: 404 (absent). Repo ruleset: "Copilot review for default branch" with deletion/non_fast_forward/copilot_code_review rules — NO required reviews, NO required status checks. Org rulesets: unknown (scope gap). CODEOWNERS: absent in all 4 paths. Community profile: health 100%, no SECURITY.md.

## Releases

20+ releases, most recent v2.21.6 (2026-04-12). Weekly cadence. v2.21.3 titled "Security Fixes."

## Dependabot / advisories

Dependabot: 403 scope gap (unknown). 8 published advisories: 7 SSRF + 1 stored XSS.

## CI workflows

10 workflows. pull_request_target: 2 (pr-docker-build.yml with write-all, pr-quality.yml with scoped permissions). No curl|bash. No SHA-pinned actions. peakoss/anti-slop@v0 mutable tag.

## Runtime dependencies

Monorepo, 7 package.json files. Root postinstall: prisma-generate (safe). No inner-package lifecycle scripts. Published SDK @postiz/node on npm.

## Step A grep results

eval: 1 file (Facebook SDK, third-party). Network: 63 files. Hardcoded secrets: none. CORS wildcard: 1 file (MCP OAuth metadata). 0.0.0.0: in SSRF blocklist (positive). TLS skip: none. SQL injection: none. XSS sinks: 16 dangerouslySetInnerHTML. Weak crypto: none. Prompt injection: 1 false positive in translation.json.

## README install path

Docker-based. ghcr.io/gitroomhq/postiz-app:latest (mutable tag). No curl|bash install.

## F12 exec inventory

CLAUDE.md, .github/copilot-instructions.md, Dockerfile.dev, docker-compose.yaml, docker-compose.dev.yaml, package.json postinstall, pr-docker-build.yml, publish-extension.yml, f.js (FB SDK).

## PR review rate sample

50 merged PRs. Formal: 14.0%. Any-review: 52.0%. nevo-david: 69.0% commits.

## Recent commits sample

386fc7b nevo-david 2026-04-15 feat: fix generation. Active daily.

## Open issues

240 total. 10 OAuth/auth bugs. No unpatched security vulns reported.

---

## Pattern recognition (inference)

- SSRF cluster resembles iterative fix-and-bypass pattern
- webhook.url.validator.ts suggests structurally sound SSRF mitigation
- pull_request_target + write-all resembles known CI attack vector
- 16 dangerouslySetInnerHTML instances look like ongoing XSS surface
- Docker-compose defaults resemble convenience-over-safety pattern
- No SECURITY.md despite 8 CVEs is consistent with reactive-only disclosure

---

## FINDINGS SUMMARY

F1: SSRF Advisory Cluster (Warning, resolved) — 7 SSRF CVEs in 12 months, all fixed in v2.21.3+
F2: Stored XSS via File Upload CVE-2026-40487 (Warning, resolved) — fixed in v2.21.6
F3: No SECURITY.md (Warning, active) — no private disclosure channel despite 8 CVEs
F4: Docker Compose Default Credentials (Warning, active) — placeholder JWT secret, default DB password
F5: CI pull_request_target with write-all (Warning, active) — fork PRs can access secrets
F6: Third-Party Actions Not SHA-Pinned (Info, ongoing) — 8 actions on tags, peakoss/anti-slop@v0
F7: No Required Reviews on Default Branch (Warning, active) — partial C20, no CODEOWNERS
F8: Agent Rule Files (Info, informational) — CLAUDE.md + copilot-instructions.md, behavioral only

## Positive signals

Active development, published advisories (8 CVEs), SSRF mitigations, CodeQL, PR quality gate, community health 100%, no committed secrets, legitimate maintainers, AGPL-3.0, force-push prevention.

## Proposed verdict

caution — Active maintenance and transparent vulnerability handling, but governance gaps (no required reviews, no SECURITY.md) and deployment concerns (default credentials) warrant caution.

## Proposed scorecard (C10)

1. "Does anyone check the code?" — Amber (Informal). any-review 52%, formal 14%.
2. "Is it safe out of the box?" — Amber (Self-hosted: change defaults). Mutable Docker tag, default creds.
3. "Can you trust the maintainers?" — Amber (Published advisories, no SECURITY.md).
4. "Is it actively maintained?" — Green (Weekly releases, daily commits).

## Catalog metadata

Report: GitHub-Scanner-postiz-app.md/.html | Repo: gitroomhq/postiz-app | Category: Web application | Subcategory: Social media management | Verdict: caution | Revision: main @ 386fc7b (v2.21.6) | Prompt: v2.3 | Prior scan: None | methodology-used: path-a
