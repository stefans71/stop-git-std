# Archive

Historical artifacts kept for reference but not load-bearing for current work. If you're tracking down "where did this go" after the session-8 cleanup, here's the map:

| Subdir | What's in it |
|---|---|
| `prompts/` | Older scanner-prompt versions (V2, V2.1, V2.2). Current is `docs/repo-deep-dive-prompt.md` (V2.4). |
| `board-reviews-pre-layout/` | Pre-`External-Board-Reviews/` board consolidations (V2.1/V2.2/V2.3 prompt reviews, AXIOM triage, V0.1 operator-guide review, V2.4 package review). The canonical board-review archive is `docs/External-Board-Reviews/`. |
| `board-review-temp-orphans/` | 14 R1/R2 brief + agent-response files committed to `.board-review-temp/` before that dir was added to `.gitignore`. See subdir's own README. |
| `board-review-data-pre-layout/` | Older artifacts from `docs/board-review-data/` that pre-date the `External-Board-Reviews/<MMDDYY>-<topic>/` archive layout (axiom-triage-responses, V1 external board brief, V2 package audit report + review brief, corrected-MD-structure analysis). |
| `migrations/` | One-time migration scripts that have already executed. Currently: `migrate-v1.1-to-v1.2.py` (ran 2026-04-20 against 3 active fixtures; idempotent). |
| `scans-superseded/` | Scan outputs that were never promoted to the catalog OR were superseded by a newer version. Currently: agency-agents (V2.x; never promoted), open-lovable (V2.x; never promoted), zustand-v2 (intermediate state; superseded by zustand-v3 at catalog entry 10). |

Nothing in here should be referenced by `CLAUDE.md`, `REPO_MAP.md`, the Operator Guide, or any of the production code/scripts. If you find a reference into `docs/archive/`, that's a bug — file it.
