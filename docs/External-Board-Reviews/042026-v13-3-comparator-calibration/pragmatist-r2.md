# V13-3 R2 — Pragmatist

## Per-C-item votes

### C1 — Write `docs/v13-3-analysis.md` as a frozen A3-scoped document
**Vote:** AGREE
**Rationale:** OD-2 codifies the deliverable; v13-1-override-telemetry-analysis.md is the right structural template. No modification needed — owner has committed to authoring it.

### C2 — V12x-9 language-qualifier regex is HARD PREREQUISITE for Priority 1 auto-fire
**Vote:** AGREE
**Rationale:** R1 Pragmatist FN-1 was unambiguous on this; Systems C-2 independently concurred. Shipping Priority 1 without V12x-9 produces spurious Critical findings on WLED's ArduinoJson pattern. The sequencing constraint must be enforced at commit level (single atomic PR), not as a soft convention.

### C3 — Freeze entries 16-26 as historical bundles; counterfactual analysis only
**Vote:** AGREE
**Rationale:** Already codified as OD-3. All three R1 positions implicitly assumed this; the explicit vote is pro-forma confirmation.

### C4 — Document sample bias explicitly in V13-3 analysis
**Vote:** AGREE
**Rationale:** Skeptic's framing is correct and the cost is one paragraph. PHP/Swift/Kotlin/Lua absence must be named so the 67% modal rate is read as a lower-bound estimate, not a converged calibration.

### C5 — V3Q2: Priority 1 deserialization auto-fire (land as V1.2.x)
**Vote:** AGREE (B1)
**Rationale:** Paired with C2 as atomic prerequisite, Priority 1 is structurally disciplined — uses existing data paths, collapses two known overrides (freerouting, Kronos), aligns with the V1.2.x additive-signal contract. Skeptic's "semantic rewrite" concern is addressed by the language qualifier; at that point it is additive, not a primitive-taxonomy redesign.

### C6 — V3Q3: Priority 1b firmware CORS compound signal — defer to V1.3
**Vote:** AGREE
**Rationale:** Unanimous R1. Shape-classification infrastructure does not exist; defer trigger is clear (≥2 firmware/IoT scans in catalog).

### C7 — V3Q4: Priority 1c reverse-engineered-API shape — defer to V1.3
**Vote:** AGREE (D2 defer)
**Rationale:** 1 observation (Baileys). FP risk on vendor-authorized clients is real and unquantifiable. ≥3 confirmed fires + dry-run FP check is the right gate before codifying; I'm not pressing D3 (reject outright) because the shape is real and may recur.

### C8 — V3Q5: Keep Q3 rubric as-is; V13-4 deferred enum addition
**Vote:** AGREE (E3 + deferred V13-4)
**Rationale:** My R1 E2 position was for adding `community_norms_differ` as a V1.3 candidate, which is absorbed by the "deferred V13-4" clause. The rubric itself stays stable for comparability; the enum addition waits for N=15 or first Q3 override fire — I can live with that framing.

### C9 — V3Q6: Prune `missing_qualitative_context` only in V1.3
**Vote:** AGREE
**Rationale:** V13-1 split was designed to supersede it; it hasn't fired in 11 scans post-expansion. Prune the replaced catchall; preserve the 3 headroom values for unsampled shapes.

### C10 — V3Q7: Follow-up cadence — G4 (Systems superset)
**Vote:** AGREE
**Rationale:** G4 is a genuine superset satisfying both my G3 (event-triggered) and Skeptic's G2 (count-triggered). The dual-trigger structure is more robust than either alone: count fires if nothing interesting happens, events fire if something structurally new appears before N=25.

### C11 — 82% scan-level override rate worth naming (INFO)
**Vote:** AGREE — preserve in V13-3 analysis document as noted.

### C12 — Same Q4 signal refs on 3 different root-cause patterns (INFO)
**Vote:** AGREE — Systems' diagnosis is correct; scorecard-hint vocabulary is underexpressive.

### C13 — Zero-override streak (wezterm→QuickLook→kanata) as positive calibration data (INFO)
**Vote:** AGREE — must be cited alongside the 82% rate to give a balanced picture.

### C14 — `signal_vocabulary_gap` 67% suggests principled expansion, not one-off patches (INFO)
**Vote:** AGREE — the C5+C6/C7 package already embodies this: land the one structurally disciplined patch (Priority 1), defer the shape-inference patches.

### C15 — Reading A and Reading B should not share maintenance home (INFO)
**Vote:** AGREE — D-6 stays executable and living; v13-3-analysis.md is frozen and cited. OD-2 already encodes this.

### C16 — V1.2-only scope for V13-3; no V2.4-era back-labeling (INFO)
**Vote:** AGREE — my R1 INF-2 position. Back-labeling is manual and error-prone; scope exclusion should be stated explicitly in the document.

### C17 — V12x-6 multi-ecosystem manifest parsing — defer to V1.3
**Vote:** AGREE (V1.3)
**Rationale:** V12x-6 requires parsers for 5+ ecosystems; it is substantially larger than Priority 1's additive-regex-plus-compute-derivation. Bundling it with V1.3 compute expansion (C14 "principled") is the right framing.

### C18 — Canonical storage of "tool loads user files" derivation in compute.py (conditional on B1)
**Vote:** AGREE
**Rationale:** The V13-1 precedent (`derive_q1_has_ruleset_protection`, `derive_q2_oldest_open_security_item_age_days`) is the right model. A `derive_tool_loads_user_files()` helper in compute.py keeps the judgment out of scan drivers and makes it testable.

### C19 — V13-3 analysis document should include "historical vs counterfactual" section
**Vote:** AGREE
**Rationale:** Without this section, later readers will conflate simulated override collapse with actual bundle contents. Low-cost, high-clarity; confirmed by my R1 OQ-2.

### C20 — Dry-run FP rate test for harness patches before V1.3 promotion
**Vote:** AGREE
**Rationale:** FIX NOW for C5 (Priority 1 landing gate); DEFER for C6/C7 (V1.3 promotion gate). This is exactly the empirical check Skeptic's BS-3 flagged as missing.

---

## Meta-positions

**Did R1 change your mind on anything?**
Yes, on two items. (1) C10 (follow-up cadence): my G3 event-only position was too brittle — Systems' G4 superset satisfying both G2 and G3 is genuinely better. I'm moving to G4. (2) C8 (Q3 rubric): Systems' framing that "amber correctly captures the current rubric's purpose" clarified why E2 was the wrong move — the rubric change and the enum addition are separate concerns; deferring the enum addition to V13-4 preserves my intent without breaking comparability.

**Does the C5+C6/C7+C14 package resolve the "principled vs one-off" tension?**
Partially yes. C5 (Priority 1) is disciplined: additive signal, existing data path, language-qualified, atomic with V12x-9. Deferring C6/C7 correctly keeps the shape-inference patches (which are one-off) out of V1.2.x. However, Skeptic's "principled expansion not one-off patches" concern isn't fully resolved until a V1.3 compute expansion is scoped as a coherent new signal family — C5 alone is a point fix, not a proof of principled architecture. The tension is managed, not closed.

---

## New items raised at R2

None. The C1-C20 frame is complete.

---

## Explicit non-escalations

- **V3Q3 (C6) / V3Q4 (C7):** Not pressing for landing these in V1.2.x. The deferred triggers (shape-classification infrastructure; ≥3 confirmed fires) are the right gates and I'm satisfied with the framing.
- **C8 E2 (Q3 rubric enum addition):** Not pressing for V1.2.x landing. The V13-4 deferred trigger is acceptable.
- **H (process):** Not re-raising H2 (owner-directive shortcut). OD-1 resolved this; the full R2-R3 cycle is appropriate given the scope.

---

## Blind spots (updated)

BS-1 remains: I haven't traced the exact `dangerous_primitives.deserialization.hit_count` → `q4_has_critical_on_default_path` threshold mechanics in compute.py to verify the C5 auto-fire claim. The "≥3 hits plus README keyword" assertion is unverified end-to-end. This is the main open risk on C5 — if the threshold is wrong, C20's dry-run gate will catch it, but the dry-run must actually run before the commit merges.
