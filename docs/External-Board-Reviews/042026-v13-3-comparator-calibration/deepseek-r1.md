# V13-3 R1 — Skeptic

## Votes
- V3Q1 (scope): **A2** — Broad cross-scan pattern calibration. The narrow comparator is already covered by D-6; the real value is in the 11-scan pattern analysis.
- V3Q2 (Priority 1 deserialization): **B2** — Defer to V1.3. Language qualifier is a bigger change than "additive signal"; it's a semantic rewrite of the deserialization family.
- V3Q3 (Priority 1b firmware CORS): **C2** — Defer to V1.3. Requires shape classification input — a new schema field, not just signal addition.
- V3Q4 (Priority 1c reverse-eng shape): **D3** — Reject. ToS-violation categories are librarian judgment, not automatable. The false-positive risk on vendor-authorized clients is unacceptably high.
- V3Q5 (Q3 rubric adjustment): **E3** — Keep Q3 rubric as-is. Amber correctly captures "partly" across all 11 scans; documented failures are already captured.
- V3Q6 (V1.3 enum pruning): **F3** — Prune none. 11 scans is insufficient evidence; 4 unused values are sleeping, not dead.
- V3Q7 (V13-3 follow-up cadence): **G2** — Trigger at 25 V1.2 wild scans. 11 is too small for stable patterns.
- H (process): **H1** — Full board. Multi-axis scope with schema implications warrants board review.

## Rationale (prose)

The fundamental assumption wrong in this brief is that 11 scans constitute a statistically meaningful sample for calibration decisions. They don't. The 11-scan roster shows heavy bias: Python/Rust over-represented (3 each), while entire ecosystems (PHP, Swift, Kotlin, Lua) are absent. The "4 unused enum values are dead" conclusion is premature — we haven't seen the shapes that would trigger them.

What breaks under adversarial reading? The "Q4 is the override hotspot" pattern (6 of 9 overrides). This isn't a structural flaw — it's sample bias. Q4's `q4_has_critical_on_default_path` is a Phase-4-authored boolean by design. The brief treats this as a problem to fix with harness patches, but that misunderstands the contract: Phase 4 is the judgment layer. Automating Q4 judgments via regex risks false positives that Phase 4 would override anyway, creating circular logic.

The Priority 1-3 harness patches are textbook overfitting. Each patch solves exactly one observed override:
- Priority 1 solves freerouting's Java deserialization (but creates false positives on safe JSON parsing)
- Priority 1b solves WLED's firmware CORS (but requires new shape classification input)
- Priority 1c solves Baileys' ToS-violation (but fails on vendor-authorized clients)

This is the "last bug" fallacy — fixing what we just saw, not building robust signals. The language-qualifier requirement for deserialization (Priority 1) reveals the deeper problem: the deserialization primitive family is conceptually broken. It conflates safe JSON parsing with unsafe pickle/ObjectInputStream. Fixing this requires rethinking the primitive taxonomy, not adding language qualifiers.

The silent-fix pattern (11/11 scans with 0 GHSA advisories) is being misinterpreted. The brief suggests Q3 rubric adjustment, but the data shows Phase 4 correctly renders amber for all 11 scans, including WLED and Baileys with documented disclosure failures. The rubric already works — amber means "partly tells you about problems." The two documented failures don't change the community norm; they confirm it. Changing the rubric to red for documented failures would create inconsistency: why red for WLED/Baileys but amber for the other 9 with identical 0-advisory patterns?

The comparator calibration's original purpose — detecting semantic drift between V2.4 and V2.5-preview — is already satisfied by D-6. The expanded "pattern calibration" scope risks mission creep: we're now debating schema changes (shape classification), primitive family redesigns, and rubric adjustments based on 11 biased samples.

My prior R1 framing about `override_category` for semantic drift detection remains unaddressed. The current 7-value enum doesn't distinguish between "threshold calibration" (fixable via signal tuning) and "judgment call" (inherent to Phase 4's role). Without this distinction, the 11-scan analysis conflates fixable gaps with irreducible judgment.

## FIX NOW items (if any)
- **C-1:** Document the sample bias explicitly in the V13-3 analysis. State clearly: "11 scans, Python/Rust heavy, missing major ecosystems."
- **C-2:** Reject the "dead enum" narrative. Keep all 7 values through V1.3; revisit at 25+ scans.

## DEFER items (if any)
- **D-1:** All Priority 1-3 harness patches → V1.3. They require schema changes (shape classification) or primitive family redesigns.
- **D-2:** Q3 rubric adjustment → Never. The rubric correctly captures the community norm.

## INFO items (if any)
- **I-1:** The zero-override streak (wezterm→QuickLook→kanata) shows the signal vocabulary works for some shapes. This is positive calibration data.
- **I-2:** `signal_vocabulary_gap` at 67% modal suggests compute.py needs expansion, but the expansion should be principled (new signal families), not one-off patches.

## Open questions the brief missed
- What's the **false-positive rate** of the proposed harness patches? Test them against the 11 existing scans.
- How does **Phase 4 judgment change** if we auto-fire Q4 from deserialization hits? Would Phase 4 override the auto-fire?
- What **new shapes** would trigger the 4 unused enum values? Design hypothetical test cases.

## Blind spots
My perspective is weakest on the **implementation complexity** of the language qualifier for deserialization. I'm advocating deferral but haven't examined the regex code to see if language detection is feasible within the current harness architecture.

Also, I'm skeptical of sample size but haven't calculated **confidence intervals** for the 67% `signal_vocabulary_gap` modal rate. At n=9 overrides, the 95% CI is wide (~35-90%). The "strongly modal" claim is statistically weak.