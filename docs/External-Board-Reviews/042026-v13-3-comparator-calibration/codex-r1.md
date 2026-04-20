# V13-3 R1 — Codex

## Votes
- V3Q1 (scope): A3 — Reading A is already functionally answered by D-6, but V13-3 should explicitly close that loop and then do the broader calibration work because the telemetry is now the larger operational signal.
- V3Q2 (Priority 1 deserialization): B1
- V3Q3 (Priority 1b firmware CORS): C2
- V3Q4 (Priority 1c reverse-eng shape): D2
- V3Q5 (Q3 rubric): E3
- V3Q6 (V1.3 enum pruning): F2
- V3Q7 (V13-3 follow-up cadence): G4-prose — close this pass only after publishing a frozen V13-3 analysis, then re-trigger on whichever comes first: 25 V1.2 wild scans total or any enum-escape / multi-label ambiguity event.
- H (process): H1

## Rationale (prose)
V13-3 is both readings, but asymmetrically. Reading A is not where the risk is anymore. D-6 already covers finding-level parity for the three pinned Step G pairs, and the validator plus seven-gate process contain future drift there. The only useful systems move is to make that closure explicit in the V13-3 artifact so operators stop treating “comparator” as an unresolved pipeline-parity question. The real open loop is Reading B: the live contract between `phase_1_harness.py`, `compute.py`, Phase 4 overrides, validator gate 6.3, and the frozen V1.2 historical bundles.

The key pattern is not merely “Q4 overrides are common.” It is that Q4 overrides are common for three different integration reasons. Freerouting is a roll-up failure from harness facts to compute signal. WLED is a compound-signal failure that needs shape context. Baileys is a metadata / README classification problem with obvious false-positive risk. Those are three different blast radii. Treating them as one “Priority 1” family would couple compute changes, README parsing, and shape inference into the same V1.2.x patch stream and make regression attribution harder. That is why B1 is right, but C1 and D1 are premature.

Deserialization auto-fire is the only candidate that is both high-yield and structurally disciplined. It uses existing data paths, aligns with the V13-1 precedent that additive signals are valid V1.2.x work, and directly collapses two known overrides. The main risk is false positives from the widened deserialization family, but the telemetry already surfaced the mitigation: language qualification. That is a bounded harness-plus-compute adjustment with a clean validator story and limited renderer impact because scorecard authority already lives in Phase 4, not Phase 3.

By contrast, firmware default-no-auth plus CORS and reverse-engineered API shape classification both inject new upstream semantics into Phase 1 or compute. They rely on shape classification, README interpretation, or platform-name heuristics that are less stable than primitive-family signals. Landing those in V1.2.x would create silent coupling with scan drivers, fixture expectations, and future operator heuristics, while preserving the same validator surface. That is exactly the kind of change that looks additive in schema terms but is not additive in behavior terms. Defer both to V1.3 or at least to a later V12x patch after explicit dry-run evidence.

I do not support a Q3 rubric change now. The telemetry shows a stable amber outcome with zero overrides, which means the system is internally consistent. WLED and Baileys are not evidence that compute is missing the problem; they are evidence that the current rubric intentionally distinguishes “poor disclosure posture” from “actively hides.” If you flip those historical cases to red, you break comparability across the 11-scan bundle set and blur the line between absence of process and adversarial concealment. That is a rubric philosophy change, not calibration.

Enum pruning should also be conservative. `missing_qualitative_context` is now clearly superseded by the V13-1 split, so pruning it in V1.3 improves audit clarity. The other three unused values should stay. Eleven scans across eleven shapes is enough to retire a replaced catchall, not enough to declare future threshold or rubric exceptions dead.

The historical-bundle rule matters: preserve entries 16–26 as historical artifacts. Do not re-render them if signals change. V13-3 should be a frozen document that cites those bundles, not a living section that mutates with later V12x patches. Otherwise the board loses the ability to reason about why overrides existed at the time they were authored.

## FIX NOW items (if any)
- C-1: Define V13-3 as A3 in the written analysis and explicitly state that Reading A is closed by D-6 while Reading B remains the actionable calibration surface.
- C-2: Land Priority 1 only as a paired change: deserialization auto-fire must ship with language-qualified matching, or it will contaminate Q4 advisory hints on non-deserialization code paths.
- C-3: Freeze entries 16–26 as historical bundles; V13-3 analysis may model override collapse counterfactually, but must not re-render prior artifacts.

## DEFER items (if any)
- D-1: Priority 1b firmware default-no-auth + CORS compound signal — defer until a dry-run on the 11 bundles proves shape classification and auth-absence heuristics are not overfitting WLED.
- D-2: Priority 1c reverse-engineered-platform-API signal — defer until a wider comparator set exists; trigger lift when at least 3 scans of that shape or an equivalent dry-run corpus shows acceptable FP rate.
- D-3: Q3 rubric escalation for documented disclosure failure — defer until a broader cross-scan sample shows the amber outcome is masking materially distinct operator action.

## INFO items (if any)
- I-1: The same four Q4 `computed_signal_refs` appear on freerouting, WLED, and Baileys despite three different root causes; that is a useful symptom that the scorecard-hint vocabulary is underexpressive even when the override enum is adequate.
- I-2: Reading A and Reading B should not share a maintenance home. D-6 is executable and living; V13-3 analysis should be frozen and cited.

## Open questions the brief missed
- If Priority 1 lands, where is the canonical derivation for “tool loads user files” stored so operators do not recreate that judgment ad hoc in scan drivers?
- Should the V13-3 document require an explicit “historical vs counterfactual” section so later readers do not confuse simulated override collapse with actual bundle contents?

## Blind spots
My weakest area here is the false-positive profile of the proposed shape classifiers outside the sampled bundles. I can see the coupling risk clearly, but I have not run the broad README/topic dry-runs that would quantify it.
