# Board Review Plan — Detection Accuracy & Scoring Calibration

## What the Board Reviews

stop-git-std has been run against 6 repos. The board evaluates whether the tool's findings, scores, and decisions are correct.

## Repos Audited

| Repo | Decision | Findings | Type |
|------|----------|----------|------|
| stop-git-std (self) | ABORT | 13 | Self-audit (false positives expected — tool detects its own rule descriptions) |
| expressjs/express | PROCEED | 5 | Well-known framework, should be clean |
| stefans71/FrontierBoard | CAUTION | 6 | AI governance tool with skills/personas, some false positives expected |
| onecli/onecli | ABORT | 13 | Known risky — curl\|bash, CI injection, committed .env |
| garrytan/gstack | ABORT | 15 | YC internal AI tool — agent/skill patterns without approval gates |
| googleworkspace/cli | ABORT | 6 | Google's workspace CLI — LLM controls tool execution |

## Audit Data

All results saved in `/root/tinkering/stop-git-std/board-review-data/`:
- `*.json` — full structured output (findings, scores, decisions, module results)
- `*.txt` — terminal reports (human-readable)

## Board Agents

| Agent | Model | CLI |
|-------|-------|-----|
| Pragmatist | Claude Opus 4.6 | claude |
| Systems Thinker | Codex GPT-5.2 | codex |
| Skeptic | DeepSeek V3.2 | run-deepseek.sh wrapper |

Board location: `/root/.frontierboard/FrontierBoard/.board/`

## Evaluation Questions for Each Repo

### 1. Finding Accuracy
For each finding in each repo:
- **True positive**: The finding is real and correctly identified
- **False positive**: The finding is incorrect — the code doesn't actually have this problem
- **Severity correct?**: Is the severity appropriate or over/under-rated?

### 2. Missed Detections (False Negatives)
For each repo, are there security issues the tool SHOULD have found but didn't? Agents should:
- Read the actual repo source code (clone or read from /tmp/stop-git-std/ if still cached)
- Compare what was found vs what exists
- Flag any gaps

### 3. Scoring Calibration
For each repo:
- Do the scores (0-100 per axis) feel right given the findings?
- Is the decision (PROCEED/CAUTION/ABORT) appropriate?
- Would a human security reviewer agree with this outcome?

### 4. Cross-Repo Consistency
- Does Express (PROCEED, 5 findings) feel right compared to onecli (ABORT, 13 findings)?
- Is the self-audit ABORT reasonable (false positives on own rules) or should the tool handle this?
- Are the AI/agent-related ABORT decisions too aggressive? All 3 AI/agent repos got ABORT.

### 5. Actionability of ABORT Decisions
4 of 6 repos got ABORT. The tool says "don't install" but provides no path forward. Evaluate:
- Should ABORT include "to make this safe, fix these N things" guidance?
- Should hard-stop rules generate constraints (like PROCEED_WITH_CONSTRAINTS does) even when the decision is ABORT?
- For repos you'd actually want to use (e.g., Google Workspace CLI), what would a "safe adoption path" look like?
- Is the current hard-stop behavior too binary? Should there be a "ABORT unless you apply these mitigations" tier?

### 6. Detection Depth — Is Static Analysis Enough?
The tool currently does regex-only static analysis. For ABORT repos:
- Would AST/dataflow analysis change any decisions? (e.g., the "model output controls execution" finding — is the flow actually exploitable or is there validation between model output and execution?)
- Would sandbox execution reveal additional risks not visible statically? (e.g., does onecli's install script actually phone home?)
- For each ABORT repo, what would a sandbox test plan look like?
- Should the tool recommend "run deeper analysis" when static-only confidence is low?

### 7. Progressive Assessment (Critical Product Feedback)
The tool currently short-circuits on hard-stop rules — it flags ABORT and stops reasoning. This is wrong. The board should evaluate and propose:

**Current behavior**: `curl | bash` found → ABORT → "don't install"
**Expected behavior**: `curl | bash` found → continue scanning → analyze the CONTEXT of the pattern → assess concrete threat level → provide adoption path

For each ABORT finding across all repos:
- What is the **concrete threat scenario**? Not "this pattern is dangerous" but "an attacker could do X because Y, resulting in Z"
- What **additional context** would change the threat level? (e.g., the curl target is a pinned URL with checksum verification → lower risk)
- What is the **safe adoption path**? (e.g., "run install in a container with no network egress after the download")
- Should this finding be ABORT, or should it be "HIGH with constraints"?

The tool should never just say "don't install." It should say "here's what's dangerous, here's the concrete risk, and here's how to use it safely if you choose to."

### 8. Specific Questions
- **Self-audit false positives**: The tool flags itself for MCP/agent/AI patterns because its source code discusses those threats. Is this a tool problem or expected behavior?
- **FrontierBoard CAUTION**: Is this correct given the false positives? With suppressions, would PROCEED be right?
- **Google Workspace CLI ABORT**: Is flagging "model output controls tool execution" correct for a tool that's designed to let LLMs control Google APIs?

## How to Run the Review

### Write briefs
Each agent gets:
1. `inbox/context.md` — this plan document
2. `inbox/brief.md` — instructions to read all 6 terminal reports from `board-review-data/*.txt`, then read the JSON files for detailed findings, then answer the evaluation questions

### Launch agents
Per `/root/.frontierboard/FrontierBoard/.board/board/BOARD.md`:
- Pragmatist + Skeptic (Claude): use `claude --model opus --dangerously-skip-permissions`
- Systems Thinker: use `codex exec -m gpt-5.2-codex --dangerously-bypass-approvals-and-sandbox`
- Skeptic (DeepSeek): use `run-deepseek.sh` wrapper — inline the terminal reports (they fit in context)

### Make data accessible
```bash
chmod -R o+rX /root/tinkering/stop-git-std/board-review-data/
```

### Round structure
- Round 1: Blind review — each agent evaluates all 6 audits independently
- Round 2: Consolidation — group findings, classify
- Round 3+: If disagreements, deliberate. Otherwise confirm.

### Output
Each agent writes to `outbox/detection-review-report.md` with:
- Per-repo assessment (TP/FP per finding, missed detections, scoring opinion)
- Cross-repo consistency assessment
- Answers to specific questions
- Overall accuracy rating (1-5) with justification
