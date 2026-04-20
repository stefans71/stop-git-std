# V13-3 R2 — Codex

## Per-C-item votes

### C1 — Write `docs/v13-3-analysis.md` as a frozen A3-scoped document
**Vote:** AGREE
**Rationale:** This is the correct deliverable shape. It closes Reading A explicitly, preserves Reading B as the operative calibration surface, and keeps the analysis in a citable frozen artifact rather than mutating the living telemetry doc.

### C2 — V12x-9 language qualifier regex on deserialization family is HARD PREREQUISITE for Priority 1 auto-fire
**Vote:** AGREE
**Rationale:** Priority 1 is only safe as an atomic harness-plus-compute change. Without language qualification, WLED-style safe JSON parsing contaminates Q4 and breaks trust in the advisory path.

### C3 — Freeze entries 16-26 as historical bundles; V13-3 analysis models override collapse counterfactually, NOT by re-rendering
**Vote:** AGREE
**Rationale:** Historical bundles are evidence, not a mutable benchmark. Counterfactual modeling belongs in the analysis document, not in rewritten artifacts.

### C4 — Document sample bias explicitly in V13-3 analysis
**Vote:** AGREE
**Rationale:** The sample is broad enough to justify calibration discussion, but still biased enough that any pruning or promotion claim needs that caveat stated plainly. This is low-cost guardrail text.

### C5 — V3Q2: Priority 1 deserialization auto-fire
**Vote:** AGREE
**Rationale:** This is still the only V1.2.x candidate that materially collapses known overrides while staying within an existing data path. I agree only in the paired form with C2, C18, and C20.

### C6 — V3Q3: Priority 1b firmware CORS compound signal
**Vote:** AGREE
**Rationale:** Defer. This crosses into shape classification and auth-absence inference, which is a larger behavioral change than an additive signal patch.

### C7 — V3Q4: Priority 1c reverse-engineered-API shape signal
**Vote:** AGREE
**Rationale:** Defer. README/topic heuristics and authorized-client false positives make this unsuitable for V1.2.x promotion without a wider corpus and explicit dry-run evidence.

### C8 — V3Q5: Q3 rubric adjustment
**Vote:** AGREE
**Rationale:** Keep the rubric as-is. The current system is internally consistent on Q3, and changing it now would be a philosophy change disguised as calibration.

### C9 — V3Q6: V1.3 enum pruning
**Vote:** AGREE
**Rationale:** `missing_qualitative_context` now reads as a superseded catchall after V13-1. The other three unused values should remain as headroom because the sample is still shape-skewed.

### C10 — V3Q7: V13-3 follow-up cadence
**Vote:** MODIFY
**Rationale:** I agree with the hybrid cadence, but the trigger should be framed as `N=25 OR any taxonomy-strain event`, where taxonomy strain includes enum-escape, genuine multi-label ambiguity, or a materially new override class. That keeps the count floor while not forcing another routine review before the data changes in kind.
**Alternative:** Adopt G4 with the event trigger broadened from only enum-escape / multi-label to any clearly new override class that does not map cleanly to the current taxonomy.

### C11 — 82% scan-level override rate is worth naming
**Vote:** AGREE
**Rationale:** The document should name this directly because it describes operator burden and calibration quality at scan granularity, not only cell granularity.

### C12 — Same 4 Q4 `computed_signal_refs` appear on freerouting + WLED + Baileys despite 3 different root causes
**Vote:** AGREE
**Rationale:** This is useful integration evidence. It shows the advisory vocabulary is underexpressive even when the override enum itself is adequate.

### C13 — Zero-override streak is positive calibration data
**Vote:** AGREE
**Rationale:** The analysis should not read as one-way failure accounting. The zero-override streak is evidence that the present contract works on some shapes.

### C14 — `signal_vocabulary_gap` 67% suggests compute needs PRINCIPLED expansion, not one-off patches
**Vote:** MODIFY
**Rationale:** I agree with the principle but not as an absolute bar on bounded fixes. The right rule is principled expansion as the default, with narrowly scoped V1.2.x exceptions only when the data path already exists and the FP surface is explicitly tested.
**Alternative:** Record C14 as governing guidance for V1.3 planning while allowing C5 as a bounded exception because it is existing-data-path work, not a new classifier family.

### C15 — Reading A and Reading B should not share maintenance home
**Vote:** AGREE
**Rationale:** D-6 stays living and executable; V13-3 stays frozen and analytical. Mixing them would blur operational drift checks with historical calibration reasoning.

### C16 — V1.2-only scope for V13-3; no V2.4-era back-labeling
**Vote:** AGREE
**Rationale:** Back-labeling old prose into new machine categories would create invented precision. The exclusion should be explicit.

### C17 — V12x-6 (multi-ecosystem manifest parsing) scope landing decision
**Vote:** AGREE
**Rationale:** This is V1.3 work. It is cross-ecosystem parser expansion, not a narrow calibration patch, and it belongs with the broader principled compute/harness expansion package.

### C18 — Canonical storage of "tool loads user files" derivation
**Vote:** AGREE
**Rationale:** If Priority 1 lands, this derivation must live in `docs/compute.py` as a named helper. Storing that judgment in drivers would create silent divergence across scans.

### C19 — V13-3 analysis document should include "historical vs counterfactual" section
**Vote:** AGREE
**Rationale:** This is required to keep future readers from misreading simulated override collapse as historical bundle state. It is a documentation control for OD-3.

### C20 — Dry-run FP rate test for harness patches before V1.3 promotion
**Vote:** AGREE
**Rationale:** For C5 it should be part of the V1.2.x landing gate, and for C6/C7 it should remain a V1.3 promotion gate. This is the missing evidence layer between observed overrides and safe automation.

## Meta-positions
- Did R1 change your mind on anything after reading the other two agents' rationales inlined below? Yes. Pragmatist's framing strengthened the need to treat V12x-9 as a hard blocker rather than merely a companion patch, and Skeptic's sample-bias point is strong enough that C4 should be explicit in the analysis. My core votes did not change.
- Does the C5 + C6/C7 + C14 package resolve the "principled vs one-off" tension? Yes, if C5 is treated as a bounded exception rather than a precedent. The package works because C6/C7 hold the line against new classifier families in V1.2.x while C14 remains the rule for broader V1.3 expansion.

## New items raised at R2 (if any)
- N1: V13-3 should explicitly distinguish "underexpressive advisory vocabulary" from "underpowered override enum" so later readers do not infer that Q4 override clustering implies another enum expansion.

## Explicit non-escalations (if any)
- I am not pressing Q3 rubric re-open beyond the deferred note in C8; the current amber behavior is stable and comparable across the 11-scan set.
- I am not pressing reverse-engineered-API rejection beyond defer; the corpus is too small to justify permanent closure.

## Blind spots (updated if anything changed)
I still have limited quantified evidence on FP rates outside the sampled bundles, especially for future shape classifiers. My confidence is highest on the integration boundaries and lowest on how broad a dry-run corpus would be needed to safely promote C6 or C7.
