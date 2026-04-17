---
description: Run FrontierBoard 3-model governance review on the implementation plan
argument-hint: (no arguments - reads from workflow artifacts)
---

# Board Review Plan

**Workflow ID**: $WORKFLOW_ID

---

## Your Mission

Run a FrontierBoard multi-model board review on the implementation plan before code is written.
Three agents (Claude Opus 4.6, GPT-5.2 Codex, DeepSeek V3.2) review the plan following the
4-round SOP: Blind Review → Consolidation → Deliberation (if needed) → Confirmation.

FIX NOW items are applied to the plan. The reviewed plan becomes the implementation source.

**This step does NOT implement anything** — it reviews and improves the plan.

---

## Phase 1: LOAD — Read Plan Artifacts

### 1.1 Load Plan Context

```bash
cat $ARTIFACTS_DIR/plan-context.md
```

Extract: plan title, files to change, scope limits, validation commands, acceptance criteria.

### 1.2 Load Plan Confirmation

```bash
cat $ARTIFACTS_DIR/plan-confirmation.md
```

Verify status is CONFIRMED or PROCEED WITH CAUTION. If BLOCKED, stop:

```
Board review cannot proceed — plan confirmation is BLOCKED.
Fix blockers and re-run the workflow.
```

### 1.3 Load Original Plan

The plan source path is in `plan-context.md`. Read the full plan:

```bash
cat {plan-source-path}
```

### 1.4 Set Board Paths

```bash
BOARD=/root/.frontierboard/FrontierBoard/.board
BOARD_DIR=$BOARD/board
BOARD_USER=llmuser
```

**PHASE_1_CHECKPOINT:**

- [ ] Plan context loaded
- [ ] Confirmation status verified (not BLOCKED)
- [ ] Original plan loaded
- [ ] Board paths set

---

## Phase 2: PRE-FLIGHT — Verify Board Environment

### 2.1 Check Board User

```bash
id $BOARD_USER
```

If it fails: stop with "Board user 'llmuser' does not exist. Run FrontierBoard /setup first."

### 2.2 Check Agent Directories

For each agent (pragmatist, systems-thinker, skeptic), verify:

```bash
for AGENT in pragmatist systems-thinker skeptic; do
  test -d "$BOARD_DIR/$AGENT/inbox" || echo "MISSING: $AGENT/inbox"
  test -d "$BOARD_DIR/$AGENT/outbox" || echo "MISSING: $AGENT/outbox"
  test -f "$BOARD_DIR/$AGENT/CLAUDE.md" || echo "MISSING: $AGENT/CLAUDE.md"
done
```

### 2.3 Check CLIs

```bash
sudo -u $BOARD_USER bash -c 'which claude' || echo "claude CLI not found for $BOARD_USER"
sudo -u $BOARD_USER bash -c 'which codex' || echo "codex CLI not found for $BOARD_USER"
```

### 2.4 Check Credentials

```bash
test -f /home/$BOARD_USER/.claude/.credentials.json || echo "No Claude credentials"
test -f /home/$BOARD_USER/.codex/auth.json || echo "No Codex credentials"
```

### 2.5 Review Lock

```bash
LOCKFILE=$BOARD/.review-lock
if [ -f "$LOCKFILE" ]; then
  LOCK_PID=$(cut -d'|' -f2 "$LOCKFILE")
  if kill -0 "$LOCK_PID" 2>/dev/null; then
    echo "Review in progress (PID $LOCK_PID). Wait or kill it."
    exit 1
  else
    rm -f "$LOCKFILE"
  fi
fi
echo "$$|$(date -Iseconds)" > "$LOCKFILE"
```

If any pre-flight check fails, stop immediately. Do NOT proceed to agent runs.

**PHASE_2_CHECKPOINT:**

- [ ] Board user exists
- [ ] All agent directories complete
- [ ] CLIs available
- [ ] Credentials exist
- [ ] Lock acquired

---

## Phase 3: BRIEF — Write Agent Briefs

### 3.1 Compose the Brief

Write a brief containing:

1. **Review type**: Implementation plan review (NOT code review)
2. **Context**: What the project does, what this plan adds
3. **Full plan inline** — the entire plan text, not a summary
4. **Scope limits** — the "NOT Building" section from plan-context.md
5. **Plan confirmation status** — any warnings from confirm-plan
6. **Evaluation criteria**:
   - Completeness: does the plan cover all acceptance criteria?
   - Feasibility: can each task be implemented as described?
   - Risk: what could go wrong during implementation?
   - Dependencies: are task ordering and file dependencies correct?
   - Missing pieces: what does the plan assume but not state?
7. **Output format**: Numbered findings with severity (FIX NOW / DEFER / INFO)
8. **Deferred items**: Check `$BOARD_DIR/../tasks.json` for items with `status: "deferred"`.
   Include them as: "Evaluate whether your review triggers any of these deferred items."

### 3.2 Write Context File

Write the project context to each agent's inbox:

```bash
CONTEXT="Project: $(basename $(pwd))
Project path: $(pwd)
Review type: Implementation plan
Date: $(date -Iseconds)"

for AGENT in pragmatist systems-thinker skeptic; do
  echo "$CONTEXT" > "$BOARD_DIR/$AGENT/inbox/context.md"
done
```

### 3.3 Write Brief to Inboxes

```bash
for AGENT in pragmatist systems-thinker skeptic; do
  echo "$BRIEF" > "$BOARD_DIR/$AGENT/inbox/brief.md"
done
```

**PHASE_3_CHECKPOINT:**

- [ ] Brief composed with full plan inline
- [ ] Context written to all 3 agent inboxes
- [ ] Brief written to all 3 agent inboxes
- [ ] Deferred items included

---

## Phase 4: ROUND 1 — Blind Review

### 4.1 Record Start Time

```bash
REVIEW_START=$(date +%s)
RUN_ID="run-$REVIEW_START"
for AGENT in pragmatist systems-thinker skeptic; do
  echo "$RUN_ID" > "$BOARD_DIR/$AGENT/outbox/.run-id"
done
```

### 4.2 Launch All Agents in Parallel

```bash
# Pragmatist (Claude Opus 4.6)
timeout 900 sudo -u $BOARD_USER bash -c "unset CLAUDECODE && cd $BOARD_DIR/pragmatist && claude --dangerously-skip-permissions -p 'read CLAUDE.md then read inbox/context.md and inbox/brief.md and write your report to outbox/report.md'" &
PID_PRAGMATIST=$!

# Systems Thinker (Codex GPT-5.2)
timeout 900 sudo -u $BOARD_USER bash -c "cd $BOARD_DIR/systems-thinker && codex exec -m 'gpt-5.2-codex' --dangerously-bypass-approvals-and-sandbox 'read CLAUDE.md then read inbox/context.md and inbox/brief.md and write your report to outbox/report.md'" &
PID_SYSTEMS=$!

# Skeptic (DeepSeek R3.2 via Qwen CLI — OpenAI-compatible API)
timeout 900 sudo -u $BOARD_USER bash -c "export OPENAI_API_KEY='$DEEPSEEK_API_KEY' OPENAI_BASE_URL='https://api.deepseek.com' && cd $BOARD_DIR/skeptic && qwen --yolo -m deepseek-reasoner -p 'read CLAUDE.md then read inbox/context.md and inbox/brief.md and write your report to outbox/report.md'" &
PID_SKEPTIC=$!

wait $PID_PRAGMATIST $PID_SYSTEMS $PID_SKEPTIC
ROUND1_END=$(date +%s)
echo "Round 1 complete in $((ROUND1_END - REVIEW_START))s"
```

### 4.3 Verify Reports

For each agent, check:

1. Exit code was 0 (non-zero or 124 = timeout → failure)
2. `outbox/report.md` exists and was modified after `$REVIEW_START`
3. For Codex: report does NOT start with `OpenAI Codex v` or contain `ERROR:` (CLI error, not findings)

```bash
for AGENT in pragmatist systems-thinker skeptic; do
  REPORT="$BOARD_DIR/$AGENT/outbox/report.md"
  if [ ! -f "$REPORT" ]; then
    echo "FAILED: $AGENT — no report produced"
  elif [ "$(stat -c %Y "$REPORT")" -lt "$REVIEW_START" ]; then
    echo "STALE: $AGENT — report older than run start"
  else
    echo "OK: $AGENT — $(wc -l < "$REPORT") lines"
  fi
done
```

**Failed agents must be retried once.** If retry also fails, note which agent failed and
continue only if at least 2 agents produced valid reports. With fewer than 2, stop the review.

### 4.4 Read Reports

Read all successful reports. Do NOT share them between agents.

```bash
cat $BOARD_DIR/pragmatist/outbox/report.md
cat $BOARD_DIR/systems-thinker/outbox/report.md
cat $BOARD_DIR/skeptic/outbox/report.md
```

**PHASE_4_CHECKPOINT:**

- [ ] All 3 agents launched in parallel
- [ ] Reports collected (at least 2 valid)
- [ ] Failed agents retried
- [ ] Timing recorded

---

## Phase 5: ROUND 2 — Consolidation

**Done by you (orchestrator), not agents.**

### 5.1 Group Findings

1. Read all Round 1 reports
2. Group findings by theme
3. Assign consolidated IDs: C1, C2, C3...
4. Note which agents raised each item and whether they agree

### 5.2 Classify Each Item

| Severity | When to use |
|----------|-------------|
| **FIX NOW** | Plan error, missing dependency, incorrect task ordering, wrong file path |
| **DEFER** | Valid concern but not blocking implementation. Must have trigger condition |
| **INFO** | Observation, suggestion, nice-to-have |
| **REJECT** | Agent raised something already covered by scope limits |

### 5.3 Apply Tiebreaking Rules

When agents assign different severities:
1. 2 of 3 agree → use majority, note dissent
2. All 3 disagree → use highest severity, flag for Round 3
3. FIX NOW vs DEFER disagreement → classify as FIX NOW, let deliberation resolve

### 5.4 Write Consolidation

Write to each agent's inbox as `consolidation.md` and `round2-brief.md`:

- Full original brief (agents are ephemeral, no memory)
- Consolidated findings with IDs
- Proposed classifications
- Instructions: respond with AGREE / DISAGREE (with rationale) / MODIFY per item

### 5.5 Run Round 2 Agents

Launch all agents again (same parallel pattern as Round 1) with Round 2 inboxes.
Collect Round 2 reports.

**PHASE_5_CHECKPOINT:**

- [ ] Findings grouped and classified
- [ ] Consolidation written to inboxes
- [ ] Round 2 agents completed
- [ ] Agreement/disagreement recorded

---

## Phase 6: ROUND 3 — Deliberation (if needed)

If Round 2 is unanimous:

> Round 2 unanimous — skipping deliberation, proceeding to confirmation.

Skip to Phase 7.

If disagreements exist:
1. Extract disputed items
2. Show each agent's position with names visible
3. Write `round3-brief.md` to inboxes (include ALL prior context)
4. Agents state AGREE or BLOCK per item
5. Run agents, collect reports

**PHASE_6_CHECKPOINT:**

- [ ] Disputes identified (or unanimous → skip)
- [ ] Round 3 completed (if needed)

---

## Phase 7: ROUND 4 — Confirmation

### 7.1 Write Final Brief

Write `round4-brief.md` to all inboxes containing:
- All items with final classifications
- Implementation notes for FIX NOW items
- Dispute resolutions (if any)
- Instructions: state SIGN OFF or BLOCK per item

### 7.2 Run Confirmation Round

Launch all agents. Collect reports.

### 7.3 Handle Blocks

If all agents sign off → proceed.

If any agent blocks:
- Document the block and rationale
- Apply owner authority override with documented rationale (autonomous mode)
- Note the override in the review artifact

**PHASE_7_CHECKPOINT:**

- [ ] Confirmation round completed
- [ ] All agents signed off (or blocks overridden)

---

## Phase 8: APPLY — Fix the Plan

### 8.1 Collect FIX NOW Items

From the final consolidated findings, extract all items classified as FIX NOW.

### 8.2 Apply Fixes to Plan

For each FIX NOW item, modify the plan:
- Wrong task ordering → reorder tasks
- Missing dependency → add dependency note
- Incorrect file path → fix the path
- Missing task → add the task
- Ambiguous instruction → clarify it

**Do NOT rewrite the plan from scratch.** Make targeted edits that address each finding.

### 8.3 Write Amended Plan

If any FIX NOW items were applied, write the amended plan to `$ARTIFACTS_DIR/plan-amended.md`.
Update `plan-context.md` to reference the amended plan.

If no FIX NOW items, the original plan stands unchanged.

**PHASE_8_CHECKPOINT:**

- [ ] FIX NOW items extracted
- [ ] Plan amendments applied (if any)
- [ ] Amended plan written (if applicable)

---

## Phase 9: ARTIFACT — Write Board Review

### 9.1 Write Review Artifact

Write to `$ARTIFACTS_DIR/board-review.md`:

```markdown
# Board Review

**Generated**: {YYYY-MM-DD HH:MM}
**Workflow ID**: $WORKFLOW_ID
**Review mode**: Standard (3 agents, 4-round SOP)
**Rounds completed**: {N}

---

## Agents

| Agent | Model | Status |
|-------|-------|--------|
| Pragmatist | Claude Opus 4.6 | {OK/FAILED} |
| Systems Thinker | GPT-5.2 Codex | {OK/FAILED} |
| Skeptic | DeepSeek V3.2 | {OK/FAILED} |

---

## FIX NOW Items

| ID | Finding | Agent(s) | Applied |
|----|---------|----------|---------|
| C1 | {description} | Pragmatist, Skeptic | Yes — {what changed} |
| C3 | {description} | All | Yes — {what changed} |

{If none: "No FIX NOW items. Plan passed review unchanged."}

---

## DEFER Items

| ID | Finding | Trigger Condition |
|----|---------|-------------------|
| C2 | {description} | {when this becomes relevant} |

{If none: "No deferred items."}

---

## INFO Items

| ID | Finding |
|----|---------|
| C4 | {observation} |

---

## Plan Amendments

{If amendments made:}
Amended plan written to: `$ARTIFACTS_DIR/plan-amended.md`

Changes:
- C1: {what was changed in the plan}
- C3: {what was changed in the plan}

{If no amendments:}
No amendments. Original plan stands.

---

## Sign-Off

| Agent | Verdict |
|-------|---------|
| Pragmatist | SIGN OFF |
| Systems Thinker | SIGN OFF |
| Skeptic | {SIGN OFF / BLOCK (overridden)} |

---

## Timing

**Total**: {N}s
**Round 1**: {N}s (Pragmatist: {N}s, Systems Thinker: {N}s, Skeptic: {N}s)
**Rounds 2-4**: {N}s each
```

### 9.2 Append to Review Log

Append a summary to `$BOARD_DIR/REVIEW-LOG.md`.

### 9.3 Remove Lock

```bash
rm -f $BOARD/.review-lock
```

**PHASE_9_CHECKPOINT:**

- [ ] Board review artifact written
- [ ] Review log updated
- [ ] Lock removed

---

## Phase 10: OUTPUT — Report Results

```markdown
## Board Review Complete

**Workflow ID**: `$WORKFLOW_ID`
**Status**: {APPROVED / APPROVED WITH AMENDMENTS}

### Review Summary

| Metric | Count |
|--------|-------|
| FIX NOW items | {N} (all applied) |
| DEFER items | {M} |
| INFO items | {K} |
| Rounds completed | {R} |

### Agents

| Agent | Model | Verdict |
|-------|-------|---------|
| Pragmatist | Opus 4.6 | SIGN OFF |
| Systems Thinker | GPT-5.2 Codex | SIGN OFF |
| Skeptic | DeepSeek V3.2 | SIGN OFF |

{If amendments:}
### Plan Amendments

{N} FIX NOW items applied to plan. Amended plan: `$ARTIFACTS_DIR/plan-amended.md`

### Artifact

Review written to: `$ARTIFACTS_DIR/board-review.md`

### Next Step

Proceed to milestone implementation loop.
```

---

## Error Handling

### Agent Fails After Retry

Continue with remaining agents if at least 2 produced valid reports.
Document the failure in the review artifact. If fewer than 2 agents
produced reports, stop the review and report:

```
Board review cannot complete — fewer than 2 agents produced valid reports.
Check agent credentials and CLIs, then re-run.
```

### Lock Held by Active Process

Do not break the lock. Report the PID and suggest waiting or killing.

### Plan Confirmation BLOCKED

Cannot review a blocked plan. Stop immediately.

---

## Success Criteria

- **AGENTS_RAN**: At least 2 of 3 agents produced valid reports
- **SOP_FOLLOWED**: 4-round process completed (3 if unanimous after R2)
- **FIX_NOW_APPLIED**: All FIX NOW items applied to plan
- **ARTIFACT_WRITTEN**: `board-review.md` contains full review record
- **LOCK_RELEASED**: Review lock removed
