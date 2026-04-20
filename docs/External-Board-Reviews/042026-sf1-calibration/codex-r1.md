# SF1 R1 — Systems Thinker (Codex GPT-5)

## Vote

Preferred resolution: propose-new — D (Option C as target architecture, with an explicit interim Step G bridge)

## Rationale

The current failure is not mainly a bad threshold problem; it is an authority-boundary problem. Scorecard cells compress evidence, semantics, and user-facing judgment into one output, so forcing them to be both deterministic compute output and the canonical human-readable adjudication will keep recreating drift as new repo shapes appear. Six months from now, the healthy system is one where Phase 3 owns facts and mechanical derivations, Phase 4 owns judgment with constrained rationale, and parity checks validate evidence use rather than pretending judgment is a pure function. Option A hard-codes today's comparator accidents, and Option B hard-codes today's rubric oversimplifications; both increase maintenance burden when calibration drifts again next year. The durable fix is to separate computed signals from adjudicated scorecard cells, then define a temporary bridge so Step G can resume without pretending V1.1 has a clean single authority.

## Resolution details

Proposal D has two parts.

Target architecture:
- Adopt Option C in substance. Remove scorecard cell color authority from `phase_3_computed`.
- Keep Phase 3 responsible for mechanical sub-signals only: review rates, branch protection, solo-maintainer flag, open security item counts, open CVE PR age, policy/advisory/disclosure flags, pinning/verification/default-path exposure flags, and any derived booleans already needed elsewhere.
- Add `phase_4_structured_llm.scorecard` as the sole authority for the four user-facing cells. Each cell should contain at minimum: `question`, `color`, `short_answer`, `rationale`, `evidence_refs`, and `computed_signal_refs`.
- Require the Phase 4 prompt to explain every non-obvious downgrade or upgrade against the computed signals. If the LLM says green where a computed signal looks amber/red, it must name the semantic reason, not just restate facts.

Interim Step G bridge:
- Do not retune `compute.py` to mimic the three comparator scans, and do not rewrite the 11-scan V2.4 catalog to satisfy `compute.py`.
- Freeze the current scorecard portion of `compute.py` as non-canonical for acceptance purposes and treat its output as advisory diagnostics during the bridge.
- Replace gate 6.3 for SF1-related reruns with a discrepancy-review gate: all 4 cells present, rationale cites evidence, and any diff between structured scorecard output and diagnostic compute output is explicitly explained per cell.
- Keep Step 3b byte-for-byte enforcement for the other 7 Phase 3 operations only. Scorecard cells are excluded from byte-for-byte parity until V1.2 lands.
- When V1.2 is ready, delete the scorecard-cell function from `compute.py` or demote it permanently to a non-gating lint/check tool.

Why this is cleaner than A/B/C alone:
- Versus A: it avoids encoding comparator-era judgment drift into logic that will need repeated board intervention.
- Versus B: it avoids a broad catalog rewrite that still leaves the wrong abstraction boundary in place.
- Versus plain C: it adds an operational bridge, so the project has a way to resume Step G without waiting for a perfect schema migration before any progress is possible.

## FIX NOW items

- Define temporary authority split. Update Step G acceptance text so scorecard cells are no longer required to satisfy both gate 6.3 comparator parity and Step 3b compute parity at the same time.
- Mark scorecard compute output diagnostic-only. Document that `compute.py` scorecard cells are advisory during the bridge and cannot fail a run by themselves.
- Draft V1.2 field contract. Write the minimal schema shape for `phase_4_structured_llm.scorecard` before any more pipeline work resumes, so the migration target is concrete.

## DEFER items

- Backfill comparator analysis across all 11 catalog scans. Measure how often V2.4 judgment diverges from strict thresholds beyond the 3 validation targets before deciding whether any computed lint should remain.
- Add override-pattern telemetry. Track recurring reasons the adjudicated scorecard differs from computed signals so future rubric changes are based on observed classes, not anecdotal cases.
- Revisit canonical question wording. Some drift is semantic, especially Q4; tightening the wording may reduce future ambiguity more than threshold changes will.

## INFO items

- The evidence suggests the 4 cells are not equally mechanical; Q3 and Q4 are especially semantic, but Q1 and Q2 also drift once contextual meaning matters. That argues against a per-question patchwork unless the owner is optimizing purely for short-term restart speed.
- If the project instead chooses A, it should be framed as a temporary compatibility patch with an expiry review date, not as the final architecture.
- If the project instead chooses B, it should acknowledge that this is a product decision to prefer strict comparability over user-aligned interpretation; that trade should be explicit, not disguised as bug-fixing.
- My recommendation assumes Step G's purpose is to validate a durable pipeline design, not merely to get one preview workflow over the line quickly.

## Blind spots

- I did not inspect the rest of the renderer/schema code, so I may be underestimating the migration cost from V1.1 to V1.2.
- I am inferring from 3 validation targets plus the catalog descriptions; a full 11-scan audit could reveal that drift is rarer or more patterned than this brief suggests.
- The bridge I propose reduces one hard gate into an explained-diff process, which could introduce reviewer subjectivity if not specified tightly enough.
