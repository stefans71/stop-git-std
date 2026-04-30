# firecrawl/open-lovable Scan — Evidence Bundle

## Repo identity
- Repo: firecrawl/open-lovable
- Description: Clone and recreate any website as a modern React app in seconds
- Created: 2025-08-08, Last push: 2025-11-19
- Default branch: main
- HEAD SHA: 69bd93bae7a9c97ef989eb70aabe6797fb3dac89
- Stars: 25,491 | Forks: 4,898 | License: MIT
- Fetch path: tarball | Files: 336

## Owner
- firecrawl — Org, created 2023-05-30, 89 repos, 2,250 followers

## Contributors
- developersdigest: 37 (63.8%), bekbull: 6, MFCo: 5, ericciarla: 3, 7 others: 1-2 each

## Governance (C20)
- Classic branch protection: 404, Rulesets: [], Rules on main: [], Org rulesets: unknown (403)
- CODEOWNERS: not found, SECURITY.md: none, Community health: 37%
- C20 FIRES

## Releases: NONE

## Dependencies
- Dependabot: 403 (admin required)
- osv.dev: 20 of 67 deps checked, 1 vuln (@anthropic-ai/sdk)
- Advisories: none published
- No lifecycle scripts

## CI: Only Copilot code review (dynamic). No custom workflows. pull_request_target: 0.

## PR review rate
- 12 merged PRs total, 0% formal review, 8.3% any-review
- PR #122 (V2, 100+ files) self-merged with 0 reviews

## Key findings:
- F1: No auth on run-command, install-packages, kill-sandbox API routes (Warning)
- F2: Zero code review (Warning)
- F3: Governance SPOF - C20 (Warning)
- F4: CORS wildcard on AI stream/scrape routes (Info)
- F5: 1 dep vulnerability (Info)
- F6: Agent rule file OK

## Verdict: caution (Deployment axis split)
