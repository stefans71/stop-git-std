# Board Verification Consolidation — Steps A+B Implementation

**Date:** 2026-04-18
**Topic:** Implementation verification of commits `2b576bf` (schema V1.1) and `75db969` (Jinja2 refactor) against the 2026-04-18 approved renderer plan (see `../041826-renderer-alignment/CONSOLIDATION.md`).
**Rounds:** R1 only (single-pass verification).
**Scope:** Does the implementation match the approved plan? V1-V11 checks + drift audit.

## Agents

| Role | Model | How invoked |
|------|-------|-------------|
| Systems Thinker | Codex (GPT-5 Codex) | `sudo -u llmuser codex exec --dangerously-bypass-approvals-and-sandbox` from /tmp |
| Skeptic | DeepSeek V4 (deepseek-chat) | `qwen -y -p "..." --model deepseek-chat` from repo dir |

Pragmatist/Claude skipped — Claude authored both the plan and the implementation (same-model blind spot).

## R1 verdicts

| Agent | Verdict |
|-------|---------|
| Codex | **BLOCK** — C2 `kind` trigger missing + unapproved Step A extras |
| DeepSeek | **APPROVE** — no blocking drift, extras are additive/non-breaking |

Split 1-1 on verdict. Owner directive applied (see below).

## Key findings

### V2 C2 execution — BLOCK (Codex) vs AGREE (DeepSeek)

Codex: the board's C2 rule was `dangerous_calls != None OR kind in sensitive set`. Commit `2b576bf` only implemented the `dangerous_calls` half. The `kind in sensitive set` half was silently dropped — underspecified trigger means "sensitive set" was never defined by the board, so the implementer had no clear rule to encode. Codex called this a direct miss against the approved rule.

DeepSeek: read the implementation as satisfying the "security-relevant" intent via the `dangerous_calls` trigger; considered `kind` a minor axis.

### Unapproved Step A extras — FLAG (Codex) vs minor drift (DeepSeek)

Both reviewers noted additions beyond the explicit plan: `finding.rule_id`, `finding.boundary_note`, `evidence.command_lang`/`result_lang`, `codeowners.locations_checked`, `action_step_type` enum broadened (install/mitigate/nudge/...), `branch_protection.classic.status` widened to accept integer HTTP status.

Codex: unapproved additions — drift from the plan.
DeepSeek: "additive, non-breaking, aligned with project quality goals — all drift is additive, non-breaking."

**Facilitator resolution:** Each of these additions was needed to make the existing zustand fixture validate against V1.1. They fall within the "schema-freeze repair" scope explicitly authorized by C1 (approved 3-0 in the 041826-renderer-alignment review). DeepSeek's reading is accurate; Codex's flag is fair but non-blocking. Recorded here for audit trail, not adjusted.

### V9 render/golden drift — FLAG (Codex)

Codex noted rendered output differs materially from `docs/GitHub-Scanner-zustand.md` despite 26/26 render tests passing. This is expected by design — the tests are structural/fact-level (not full diff-match) precisely because Step C fixture enrichment hasn't landed yet. The plan explicitly calls for tests to flip to fuller structural assertions in Step D *after* Step C.

**Facilitator note:** not actionable pre-Step-C; documented for context.

## Owner directive (2026-04-18)

Adopt Codex's original R2 dissent position on C2 — simplify `executable_file_inventory_entry` to require `file_sha` + `line_ranges` + `diff_anchor` **structurally** on every entry, with `null` allowed when a scan cannot resolve them. This resolves the BLOCK cleanly by eliminating the "sensitive set" underspecification entirely. Rationale:

1. Codex's R2 dissent already preferred always-required-with-null-fallback.
2. DeepSeek's APPROVE is preserved (move is additive, not a regression).
3. The `kind`-based trigger half was underspecified by the board; fixing by defining "sensitive set" now would be a new design decision, not an implementation fix.
4. Documentary enforcement (required key, value may be null) matches the pattern used elsewhere in the schema.

Applied in commit (see below). Removes the conditional `allOf` block; the three fields move to `required`; their `type` stays `["string", "null"]`.

## Final status

- **APPROVED after owner directive.**
- Fixture still validates clean against the updated schema (0 errors).
- All 107 tests still pass.

## Round artifacts

- `r1-brief.md` — implementation verification brief with V1-V11 checks
- `codex-r1.md` — Codex BLOCK verdict with full drift audit
- `deepseek-r1.md` — DeepSeek APPROVE verdict

## Next action

Proceed to Step C (fixture enrichment with structural-LLM fields).
