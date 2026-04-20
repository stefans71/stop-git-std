# V13-3 R2 — Skeptic

## Per-C-item votes

### C1 — Write `docs/v13-3-analysis.md` as a frozen A3-scoped document
**Vote:** AGREE
**Rationale:** The frozen analysis document is necessary to close the deferred ledger item with evidence. Mirroring the v13-1 template provides consistency and establishes a pattern for future calibration analyses.

### C2 — V12x-9 language qualifier regex on deserialization family is HARD PREREQUISITE for Priority 1 auto-fire
**Vote:** AGREE
**Rationale:** If Priority 1 lands, language qualification is essential to avoid false positives on safe JSON parsing. The WLED ArduinoJson case demonstrates this risk concretely. Sequencing them atomically is correct.

### C3 — Freeze entries 16-26 as historical bundles; V13-3 analysis models override collapse counterfactually, NOT by re-rendering
**Vote:** AGREE
**Rationale:** Historical preservation is critical for auditability and comparability. Counterfactual modeling allows analysis without retroactively changing records, maintaining the integrity of the 11-scan dataset.

### C4 — Document sample bias explicitly in V13-3 analysis
**Vote:** AGREE
**Rationale:** The Python/Rust heavy sample (3 each) with missing ecosystems (PHP, Swift, Kotlin, Lua) must be explicitly stated to constrain over-reading. This is low-cost, high-value context framing.

### C5 — V3Q2: Priority 1 deserialization auto-fire
**Vote:** DISAGREE (B2 defer)
**Rationale:** The language qualifier requirement reveals a deeper problem: the deserialization primitive family is conceptually broken, conflating safe JSON parsing with unsafe pickle/ObjectInputStream. This isn't additive signal work—it's a semantic rewrite of the primitive taxonomy. Deferring to V1.3 allows principled redesign rather than patching the current broken taxonomy.

### C6 — V3Q3: Priority 1b firmware CORS compound signal
**Vote:** AGREE
**Rationale:** Deferring to V1.3 is correct. This requires shape-classification infrastructure (firmware vs non-firmware), which is a new schema field, not just signal addition. The sample has only 1 observation (WLED).

### C7 — V3Q4: Priority 1c reverse-engineered-API shape signal
**Vote:** DISAGREE-REJECT (D3 close permanently)
**Rationale:** ToS-violation categories are librarian judgment, not automatable. The false-positive risk on vendor-authorized clients (official Discord SDK, Matrix clients) is unacceptably high and would destroy scanner trust. This should be rejected, not deferred.

### C8 — V3Q5: Q3 rubric adjustment
**Vote:** AGREE
**Rationale:** Keeping Q3 rubric as-is is correct. The 11/11 silent-fix pattern shows Phase 4 correctly renders amber for all scans, including WLED/Baileys with documented disclosure failures. Amber means "partly tells you about problems"—changing to red would create inconsistency across identical 0-advisory patterns.

### C9 — V3Q6: V1.3 enum pruning
**Vote:** DISAGREE
**Rationale:** 11 biased samples are insufficient to prune any enum values. The 4 unused values are sleeping, not dead—we haven't seen the shapes that would trigger them. Pruning `missing_qualitative_context` assumes the V13-1 split is complete, but at n=11 we can't know if future shapes will need this catchall.

### C10 — V3Q7: V13-3 follow-up cadence
**Vote:** MODIFY
**Rationale:** G4 (Systems) is too permissive—it allows event-based triggers that could fire prematurely. G2 (Skeptic) at N=25 provides statistical stability. Modify to: "Trigger at 25 V1.2 wild scans OR when 3 consecutive scans produce override patterns not explainable by current enum."

### C11 — 82% scan-level override rate is worth naming
**Vote:** AGREE (INFO item)
**Rationale:** The high override rate (9/11 scans) indicates the harness+compute advisory layer rarely produces Phase 4-concordant results across entire scans. This should be explicitly named in the analysis.

### C12 — Same 4 Q4 `computed_signal_refs` appear on freerouting + WLED + Baileys despite 3 different root causes
**Vote:** AGREE (INFO item)
**Rationale:** This symptom shows the scorecard-hint vocabulary is underexpressive even when the override enum is adequate. Worth documenting as a signal vocabulary limitation.

### C13 — Zero-override streak (wezterm → QuickLook → kanata) is positive calibration data
**Vote:** AGREE (INFO item)
**Rationale:** The streak shows the signal vocabulary works for some shapes (terminal emulators, shell extenders, keyboard daemons). This positive evidence should be cited alongside the override patterns.

### C14 — `signal_vocabulary_gap` 67% suggests compute needs PRINCIPLED expansion, not one-off patches
**Vote:** AGREE (INFO item)
**Rationale:** The modal override reason indicates systemic gaps in compute.py's signal families. Expansion should be principled (new signal families) rather than one-off patches for observed overrides.

### C15 — Reading A and Reading B should not share maintenance home
**Vote:** AGREE (INFO item)
**Rationale:** D-6 (executable, living) and V13-3 analysis (frozen, citable) serve different purposes. Keeping them separate maintains clarity of purpose.

### C16 — V1.2-only scope for V13-3; no V2.4-era back-labeling
**Vote:** AGREE (INFO item)
**Rationale:** Back-labeling V2.4 prose to machine-readable categories is manual and error-prone. Explicit scope exclusion prevents mission creep.

### C17 — V12x-6 (multi-ecosystem manifest parsing) scope landing decision
**Vote:** AGREE
**Rationale:** Defer to V1.3. This requires multi-ecosystem parser work (Java/Ruby/Rust/Go/.NET), substantially larger than Priority 1. Aligns with principled expansion (C14) rather than one-off patches.

### C18 — Canonical storage of "tool loads user files" derivation
**Vote:** AGREE
**Rationale:** If Priority 1 lands (which I oppose), the derivation must be in `docs/compute.py` as a helper function, not ad hoc in scan drivers. This follows the V13-1 precedent.

### C19 — V13-3 analysis document should include "historical vs counterfactual" section
**Vote:** AGREE
**Rationale:** Essential to prevent confusion between simulated override collapse and actual bundle contents. This section clarifies the analysis methodology.

### C20 — Dry-run FP rate test for harness patches before V1.3 promotion
**Vote:** AGREE
**Rationale:** Dry-run testing is essential for any harness changes. For Priority 1 (which I oppose), it would reveal the false-positive rate. For deferred items, it becomes part of V1.3 promotion gate.

## Meta-positions

- **Did R1 change your mind on anything after reading the other two agents' rationales inlined below?** Yes. The Pragmatist's FN-1 (V12x-9 as hard prerequisite) and Systems' C-2 (language-qualified matching requirement) strengthened my position that Priority 1 is not additive—it requires semantic rewrite of the deserialization family. Their recognition of the coupling risk validates my "principled vs one-off" framing.

- **Does the C5 + C6/C7 + C14 package resolve the "principled vs one-off" tension?** No. The package attempts to split the difference but fails. C5 (land Priority 1) remains one-off patching of the broken deserialization taxonomy. C6/C7 deferrals acknowledge shape-classification complexity but don't address the core issue: Priority 1 itself is overfitting to freerouting's Java deserialization. The principled solution is to defer ALL Priority items to V1.3 for coordinated primitive taxonomy redesign.

## New items raised at R2

- **N1:** The deserialization primitive family needs taxonomy redesign, not language qualification. Safe JSON parsing (ArduinoJson) and unsafe deserialization (pickle, ObjectInputStream) are conceptually distinct primitives. This redesign belongs in V1.3, not V1.2.x patches.

- **N2:** Statistical confidence intervals should be calculated for the 67% `signal_vocabulary_gap` modal rate. At n=9 overrides, the 95% CI is ~35-90%. The "strongly modal" claim is statistically weak and should be qualified in the analysis.

## Explicit non-escalations

- **C8 (Q3 rubric):** I accept the majority E3 position despite my R1 dissent on `community_norms_differ`. The 11/11 silent-fix pattern shows the current rubric works.

- **C10 (follow-up cadence):** I'll accept a modified G4 that includes count-based stability (N=25) as primary trigger with event-based secondary triggers.

## Blind spots (updated)

- **Implementation complexity of language qualifier:** Still unexamined. If Priority 1 lands despite my dissent, the regex code needs review to ensure language detection is feasible within current harness architecture.

- **Confidence intervals:** Added as N2—need to calculate statistical bounds on the 67% modal rate claim.

- **Phase 4 judgment change:** Unaddressed—if Priority 1 auto-fires Q4 from deserialization hits, would Phase 4 override it? This creates circular logic: Phase 4 overrides compute, compute auto-fires from Phase 4's judgment patterns.