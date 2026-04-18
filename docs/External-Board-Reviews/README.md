# External Board Reviews — Index

This folder archives all 3-model governance board reviews for the stop-git-std project. Each review follows FrontierBoard SOP (`/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`). Each subfolder has its own `CONSOLIDATION.md` with the canonical record.

## Review agents

| Role | Model | How to invoke | Notes |
|------|-------|---------------|-------|
| **Pragmatist** | Claude Sonnet 4.6 (when Opus wrote the artifact) OR Claude Opus 4.7 | `Agent` tool with `model: "sonnet"` or default | Use Sonnet to preserve cognitive diversity when Opus authored the work under review. Never drop to a 2-agent board. |
| **Systems Thinker** | Codex GPT-5 Codex | `sudo -u llmuser bash -c "cd /tmp && codex exec --dangerously-bypass-approvals-and-sandbox '...'"` | Must run as `llmuser` (auth tied to that user). Brief at `/tmp/...` (don't put in repo dir — CLAUDE.md pulls it off-task). Use absolute paths for repo files in the prompt. |
| **Skeptic** | DeepSeek V4 (via Qwen CLI) | `OPENAI_API_KEY="$DEEPSEEK_API_KEY" OPENAI_BASE_URL="https://api.deepseek.com/v1" qwen -y -p "..." --model deepseek-chat` | Launch from the repo directory so its workspace includes repo files. `-y` flag enables file writes (YOLO mode). Transient API errors happen — retry once. |

Per 2026-04-18 SOP compliance: minimum 3 agents per round. Never drop below 3.

## Chronological index

| Date | Folder | Topic | Rounds | Result |
|------|--------|-------|--------|--------|
| 2026-04-16 | `041626-celso/` | (pre-migration — see folder contents) | — | — |
| 2026-04-18 | `041826-renderer-alignment/` | Phase 7 renderer execution plan alignment | R1-R4 | ALL SIGN OFF (dissents noted) |
| 2026-04-18 | `041826-renderer-impl-verify/` | Steps A+B implementation verification (schema V1.1 + Jinja2 refactor) | R1 | APPROVED after owner directive (C2 BLOCK resolved) |
| 2026-04-18 | `041826-fixture-enrichment/` | Step C fix-artifact review (10 FAs for zustand-form.json) | R1 | UNANIMOUS 3-0 APPROVE, applied |
| 2026-04-18 | `041826-step-f-alignment-validation/` | Step F validation + Step G readiness — XSS, CSS escape, parity regex, deferred-items reconciliation | R1-R4 full | SIGN OFF (2) + SIGN OFF W/ DISSENTS (1, bookkeeping only). Owner fixes in `ce698d4`. |

## Current state in the renderer workstream

See `041826-renderer-impl-verify/INDEX.md` for the cross-referenced status across all 3 related reviews + commit log + remaining steps.

## Naming convention

- Folder: `MMDDYY-<topic>/`
- Files inside each folder:
  - `CONSOLIDATION.md` — the canonical record with consolidated findings, dissents, owner directives, final verdicts
  - `r1-brief.md`, `r2-brief.md`, ... — per-round briefs sent to agents
  - `{pragmatist,codex,deepseek}-r{1,2,3,4}.md` — per-agent responses
