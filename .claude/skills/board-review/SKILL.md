---
name: board-review
description: Trigger a FrontierBoard governance review of this project. Run when the user types /board-review or asks for a board review.
---

# Board Review

Launch a FrontierBoard review from this project session.

## Board Location
`/root/.frontierboard/FrontierBoard`

## Board Members

| Agent | Model | Angle |
|-------|-------|-------|
| Pragmatist | Claude Opus 4.6 | Operational reality |
| Systems Thinker | Codex GPT-5.2 | Architecture |
| Skeptic | DeepSeek V3.2 | Gaps and correctness |

## How to Run

### Option 1: From a separate terminal
```bash
cd /root/.frontierboard/FrontierBoard/.board && claude
```
Then describe what you want reviewed, or use `/brief` then `/run`.

### Option 2: Launch from this session
```bash
nohup bash -c 'unset CLAUDECODE && cd /root/.frontierboard/FrontierBoard/.board && claude --dangerously-skip-permissions -p "review the project at /root/tinkering/stop-git-std — focus on [SCOPE]. Run /brief then /run."' > /tmp/fb-review.log 2>&1 &
```

## Review Modes

| Mode | Agents | Rounds | Time |
|------|--------|--------|------|
| Quick | 1 agent | 1 round | ~3 min |
| Standard | 3 agents | 3-4 rounds (full SOP) | ~10-20 min |

## Checking Results

After the review completes, read:
- `/root/.frontierboard/FrontierBoard/.board/board/REVIEW-LOG.md` — synthesis
- Individual reports in each agent's `outbox/report.md`
