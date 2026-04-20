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
| 2026-04-18 → 2026-04-19 | `041826-step-g-kickoff/` | Step G kickoff / U-1 doc integration — V2.5-preview pipeline documented as Step-G-experimental across 5 docs, FX-3b synced to package | R1-R3 | SIGN OFF (1) + SIGN OFF W/ DISSENTS (2, non-blocking carried awareness). Owner commits `60e0bf2` (FX-3b parallel) + `6a3e471` (U-1). |
| 2026-04-19 | `041926-step-g-execution/` | Step G execution approach — first live V2.5-preview pipeline run on 3 shape-matched repos (zustand/caveman/Archon). 9 fix artifacts + 15 carry-forward dispositions + graduated failure rubric + pilot-and-checkpoint ordering. | R1-R3 | **UNANIMOUS CLEAN SIGN OFF.** 41-item dissent audit, zero silent drops. First review to use SOP §4 pre-archive dissent audit gate. |
| 2026-04-20 | `042026-sf1-calibration/` | Step G Finding SF1 — scorecard cell calibration drift between `docs/compute.py` and V2.4 comparator MDs across all 3 targets (5 cell mismatches). Design decision on authority boundary. Hybrid "A-now + C-for-V1.2 + edge_case": 5 temporary-compatibility compute.py patches + D-7 committed architecture migration with 4-trigger disjunctive union. | R1-R4 | **3/3 CONFIRM on frozen hybrid · 3/3 UNION-ACCEPT on D-7 trigger · 2-1 G-C-ACCEPT on Archon Q3 (Tension 1) with DeepSeek D-CANONICAL dissent preserved.** Dissent audit clean. |
| 2026-04-20 | `042026-schema-v12/` | Schema V1.2 design — co-scheduled D-7 (scorecard cell authority migration `phase_3_computed` → `phase_4_structured_llm`; `phase_3_advisory` new top-level) + D-8 (schema accepts harness output natively; transformer deleted). 6 substantive items (A-F) resolved: rationale refs-only floor, active-fixtures-only migration with `step-g-failed-artifact` exclusion rule, 5-value `override_reason` enum, no `dangerous_primitives` renderer edits (empirically no consumer), `total_bytes` dropped, 23-row question-scoped signal ID vocabulary frozen. | R1-R3 + owner directives | **3/3 SIGN OFF with owner directives on Q3, OQ-2/3, and 6 R3 items.** 31-item dissent audit · 9 live preserved dissents + 3 moot-preserved · zero silent drops. |
| 2026-04-20 | `042026-v13-3-comparator-calibration/` | V13-3 — 11-scan comparator calibration analysis. Triggered at catalog entry 26 (Baileys, 11th V1.2 wild scan). 4 V13-3 scope items (C5 Priority 1 deserialization auto-fire LAND V1.2.x, C7 Priority 1c reverse-eng DEFER V1.3 with triggered-promotion-or-REJECT gate, C9 prune `missing_qualitative_context` V1.3 with historical-hold, C10 G4-broadened follow-up cadence). 20 total C-items + N1/N2 (new V1.3 items: deserialization taxonomy redesign, 67% modal confidence intervals). | R1-R3 + owner directive | **2/3 R3 AGREE convergence + owner directive close (OD-4)** — Codex unavailable in R3 window due to OpenAI backend capacity; Codex R2 positions consistent with all R3 resolutions; Codex assigned code-review gate on staged V1.2.x implementation diff. 33-item dissent audit · zero silent drops. |

## Current state in the renderer workstream

See `041826-renderer-impl-verify/INDEX.md` for the cross-referenced status across all 3 related reviews + commit log + remaining steps.

## Naming convention

- Folder: `MMDDYY-<topic>/`
- Files inside each folder:
  - `CONSOLIDATION.md` — the canonical record with consolidated findings, dissents, owner directives, final verdicts
  - `r1-brief.md`, `r2-brief.md`, ... — per-round briefs sent to agents
  - `{pragmatist,codex,deepseek}-r{1,2,3,4}.md` — per-agent responses
