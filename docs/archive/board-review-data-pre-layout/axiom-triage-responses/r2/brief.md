# Round 2 Brief — Implementation Verification + DEFER Reduction

You are reviewing the actual code changes made to implement the AXIOM audit triage findings. Two jobs:

## Job 1: Verify implementation matches agreed verdicts

The board agreed on 6 FIX NOW + 8 FIX NEXT items. The diff below shows what was actually changed across 5 files. For each agreed item, verify:
- Was it implemented correctly?
- Does the implementation match what the board specified?
- Are there any gaps or mistakes?

**Agreed FIX NOW items:**
1. V3 — Strip symlinks after tar extraction (`find -type l -delete`)
2. V2 — Add `--no-absolute-names` to tar
3. V5 — Use full 40-char SHA (remove `head -c 7`)
4. B1 — Sync template CSS with standalone file
5. B2 — Fix PR count logic
6. V1 — XSS checks in validator + CSP meta tag

**Agreed FIX NEXT items:**
1. V4 — Quote all shell variables
2. W1/O3 — Move changelog out of prompt (~60 lines to CHANGELOG.md)
3. W2 — Rate-limit budget check before Step 5
4. W4 — osv.dev fallback for Dependabot 403
5. Cap-1 — OSSF Scorecard API call
6. O4 — CSS sync mechanism in validator
7. B3 — Markdown validator mode
8. O2 — Reduce S8 rules from 12 to 5 hard

## Job 2: Reduce the 21 DEFER items

21 deferred items is too many. Some of these should be ADOPT NOW or at least ADOPT NEXT. Review each and re-classify:

| ID | Finding | Current status |
|----|---------|---------------|
| O1 | Full orchestration pivot | DEFER to V3.0 |
| O5 | JSON evidence → HTML template | DEFER to V3.0 |
| W3 | /tmp volatile | DEFER |
| W5 | Exhibit rollup unreliable | DEFER |
| W6 | Scorecard thresholds too rigid | DEFER |
| W7 | Manual pre-render checklist | DEFER |
| B5 | Path B contradictions (stale text) | DEFER (doc cleanup) |
| B6 | Step 8 prerequisites undeclared | DEFER |
| Cap-4 | Secrets-in-history (gitleaks) | DEFER |
| Cap-5 | Unauthenticated fallback | DEFER |
| Cap-6 | SBOM endpoint | DEFER |
| Cap-7 | Release sig verification (cosign) | DEFER |
| Cap-8 | deps.dev cross-reference | DEFER |
| Cap-9 | Fork divergence analysis | DEFER |
| Cap-10 | Fake-star burst detection | DEFER |
| Cap-11 | Reclaimed-username detection | DEFER |
| Cap-12 | Tampered commit timestamps | DEFER |
| Cap-13 | Binary entropy analysis | DEFER |
| Cap-14 | "Safer alternative" recommendations | DEFER |
| Cap-15 | SARIF output | DEFER |
| B4 | Package incomplete (missing refs) | REJECT |

For each, say:
- **KEEP DEFER** — still not actionable, explain why
- **UPGRADE to FIX NEXT** — should be done in V2.5 cycle, explain what specifically
- **CLOSE** — not worth tracking, explain why
- **MERGE** — combine with another item

Target: reduce 21 DEFERs to ≤10. Be aggressive about closing items that are speculative, niche, or require tools we won't install.

## The implementation diff follows below

