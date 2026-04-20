# V13-3 R1 — Pragmatist

## Votes

- V3Q1 (scope): **A3** — Confirm D-6 closes the narrow pipeline-comparator reading; the broad cross-scan calibration is the real deliverable V13-3 owes.
- V3Q2 (Priority 1 deserialization): **B1** — Additive signal, CONSOLIDATION Board Item F permits it; language-qualifier prerequisite (V12x-9) must land first in the same commit.
- V3Q3 (Priority 1b firmware CORS): **C2** — New shape-classification input required; that's bigger than additive signal work; defer to V1.3 where shape taxonomy is owned.
- V3Q4 (Priority 1c reverse-eng shape): **D2** — FP risk on authorized third-party clients is real and unquantifiable from 1 observation; need ≥3 confirmed fires before codifying.
- V3Q5 (Q3 rubric): **E2** — Don't change the rubric; add `community_norms_differ` as a V1.3 candidate (DeepSeek's preserved dissent now has telemetric backing at 11/11); rubric change is a bigger cross-scan comparability event than it looks.
- V3Q6 (V1.3 enum pruning): **F2** — Prune only `missing_qualitative_context` (superseded by V13-1 split); keep the other 3 as headroom; 11 scans isn't a balanced sample (Lua/PHP/Swift absent).
- V3Q7 (V13-3 follow-up cadence): **G3** — Condition-triggered is smarter than count-triggered; `signal_vocabulary_gap` at >80%, OR ≥2 new enum values fire in one scan, OR a case fits none are the right tripwires.
- H (process): **H2** — Owner directive after this R1; the scope is multi-axis but the directional answers are clear enough; R2/R3 only if dissent from Systems Thinker or Skeptic is substantive.

---

## Rationale

**On V3Q1 (scope):** The narrow reading (D-6 covers pipeline-level parity, V13-3 closes with a confirmation note) is correct but insufficient. D-6 already passes on all 3 Step G pairs — that question is closed. The interesting V13-3 work is the broad reading: the 11-scan cross-analysis has never been formally written up as a frozen document. The `docs/v12-wild-scan-telemetry.md` is a living doc, not a decision artifact. V13-3's mandate is to produce a citable analysis document (`docs/v13-3-analysis.md`) that closes the deferred-ledger item with evidence rather than just a note.

**On V3Q2 (deserialization Priority 1):** This is the right call, but the sequencing constraint is hard. V12x-9 (language qualifier on the deserialization regex) is a prerequisite — without it, the Priority 1 compute derivation fires on WLED's 19 ArduinoJson FP hits and produces a Critical finding on what is safe JSON parsing. The two must ship atomically: V12x-9 narrows the regex, then Priority 1 auto-fires from the narrowed output. The brief treats V12x-9 as "promoted from Low to Medium" — the operator needs to treat it as mandatory blocker for Priority 1, not just a parallel work item.

**On V3Q3 (firmware CORS, Priority 1b):** This is not an additive signal — it requires a new shape-classification input (firmware vs non-firmware). The shape taxonomy doesn't exist in compute.py today; building it requires a new harness layer reading README keywords + install-path signals. That's not V1.2.x additive; it's infrastructure. Defer to V1.3 where shape-aware compute can be designed cleanly.

**On V3Q4 (reverse-eng shape, Priority 1c):** 1 observation (Baileys). The FP scenario (authorized third-party clients) is real; libraries like the official Discord SDK, Matrix clients, or vendor-blessed bots would match the disclaimer regex. The cost of a false Critical on a legitimate library is high — it destroys trust in the scanner. Defer to V1.3 and collect ≥3 confirmed fires (whatsmeow, discord.py-self, instagrapi are all live candidates) before codifying.

**On V3Q5 (Q3 rubric):** The brief frames this as E1 (escalate to red on documented failure) vs E3 (keep as-is). E1 is the wrong move for comparability reasons: 9 of 11 prior V1.2 scans would remain amber under Q3 while 2 become red — this creates a retroactive comparability break. The 11/11 silent-fix pattern is strong enough that it argues for naming the community norm explicitly in the rubric language, not for moving the threshold. E2 is the right frame: preserve the amber reading as accurate for the current rubric's purpose ("do they have the infrastructure"), and advance `community_norms_differ` as the V1.3 enum value that lets Phase 4 call out the WLED/Baileys pattern without changing the rubric color decision. DeepSeek's R3 Item C dissent (CONSOLIDATION §5 Item C) explicitly preserved this trigger — the data at n=11 makes it fire.

**On V3Q6 (enum pruning):** 11 scans is enough to drop `missing_qualitative_context` (the V13-1 split was designed to absorb it; it hasn't fired since), but not enough to prune `threshold_too_lenient`, `rubric_literal_vs_intent`, or `other`. The sample is heavily skewed: Zig, Rust, C#, Java, Python ML are all represented, but Lua/PHP/Ruby/Swift/Kotlin aren't. A PHP WordPress plugin or a Ruby-on-Rails server gem might produce `rubric_literal_vs_intent` overrides on Q2 or Q3 where "4 security items open" doesn't actually mean "slow fixes." Hold F3-equivalent headroom for those shapes.

**On V3Q7 (follow-up cadence):** Count-based triggers (G2 at 20 or 25) are dumb timers. The right trigger is: something surprising happens in the data. G3's three conditions are precise enough to fire when the taxonomy is strained without firing every 10 scans on routine operation.

**On H (process):** H2. This review covers 7 connected questions. R1 gives the board a round of input; if the three agents converge on the same key votes (particularly B1/B2 on deserialization, C2/C3 on firmware, E2/E3 on Q3 rubric), the owner has enough to act without a full R2/R3 cycle. Full three-round review adds 30-45 minutes of orchestration overhead for decisions that the data makes clear. Escalate only if the Systems Thinker or Skeptic surfaces something this brief missed.

---

## FIX NOW items

- **FN-1:** V12x-9 (language-qualifier regex on deserialization family) MUST be treated as a hard prerequisite for V3Q2/Priority 1 auto-fire — not as a parallel-and-maybe item. The brief lists it as "promoted from Low to Medium"; it should be elevated to blocker. If Priority 1 ships without V12x-9, the WLED ArduinoJson FPs will trigger spurious Critical findings.

---

## DEFER items

- **V3Q3 (C2):** Priority 1b firmware compound signal — defer to V1.3 pending shape-classification infrastructure.
- **V3Q4 (D2):** Priority 1c reverse-engineered-API shape signal — defer to V1.3 pending ≥3 confirmed fire observations.
- **V3Q6-remainder:** `threshold_too_lenient`, `rubric_literal_vs_intent`, `other` — hold at V1.3 pending balanced shape-sample (Lua/PHP/Swift/Kotlin shapes uncovered).

---

## INFO items

- **INF-1:** The 82% scan-level override rate (9 of 11 scans have ≥1 override) is higher than the brief frames it. The 33% cell-level override rate from V13-1 was alarming enough to drive enum expansion. At scan level 82% suggests the harness+compute advisory layer is rarely producing Phase 4-concordant results across an entire scan — worth naming explicitly in the V13-3 analysis document.
- **INF-2:** §8.3's question about V2.4-era back-labeling: recommend V1.2-only scope for V13-3. Back-labeling V2.4 prose to machine-readable override categories is manual and error-prone. The V13-3 analysis document should note this as an explicit scope exclusion, not leave it ambiguous.
- **INF-3:** The `docs/v13-3-analysis.md` document format should mirror `docs/v13-1-override-telemetry-analysis.md` structurally — that's the established template for this class of analysis and it worked well.

---

## Open questions the brief missed

- **OQ-1:** V12x-6 (multi-ecosystem manifest parsing) is Priority 2 in the backlog but isn't a V3Qx vote option — it affects 7 of 11 scans and produces `runtime_count=0 / osv_total_vulns=0` for Maven/Gradle/Cargo/Gomod/Bundler/.NET. Is this on or off the V13-3 scope? The brief treats it as a backlog item without a landing-window decision. V1.2.x or V1.3?
- **OQ-2:** If V3Q2 B1 lands (deserialization auto-fire), entries 17 (Kronos) and 24 (freerouting) would no longer have Q4 overrides if re-processed. But CONSOLIDATION §9 says "existing override records preserved as historical." Does the V13-3 document explicitly codify this non-retroactivity rule, or does it leave it implicit?

---

## Blind spots

My perspective is weakest on the compute.py derivation specifics for Priority 1 — I've read the logic but haven't traced the signal chain from `dangerous_primitives.deserialization.hit_count` through to `q4_has_critical_on_default_path` to verify the threshold mechanics are as described. The "≥3 hits plus README keyword match" threshold N is asserted but not tested. I'm also weakest on whether V12x-9's language-qualifier regex change is truly low-risk or whether suppressing `\bdeserialize\b` in C/C++/Rust creates a coverage blind spot on genuine unsafe deserialization in those languages.
