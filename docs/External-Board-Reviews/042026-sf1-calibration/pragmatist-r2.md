# SF1 R2 — Pragmatist (Claude Sonnet 4.6)

## Verdict on hybrid

ACCEPT

## Rationale

The hybrid is my R1 Option A with two additions: a mandatory F0-type verification gate before the Q4 zustand fix, and a firm post-Step-G commitment (D-7) to the authority-boundary migration I flagged as "Option C's appeal is architecturally sound" in my INFO section. I already said C "makes sense as a Phase 2 consideration after Step G completes" — D-7 is exactly that, packaged with a concrete trigger instead of a vague gesture. The 5 patches are the Phase-1 spine, which is what I asked for. The F0 verification gate (§5.1.5) is the right call — I flagged that blind spot in R1, and the hybrid promotes it to an explicit step rather than leaving it to the implementation. D-7 does not slow down Step G, it does not require schema migration before authoring resumes, and it has a measurement trigger that could downgrade it to optional polish if the patches hold. That is not scope creep; it is scope accounting. The hybrid ships Step G on V1.1 and schedules the architectural work the Systems Thinker correctly identified — without letting the architectural work block the ship.

## Engagement with your R1 dissent audit (the items marked ❌ in §6)

The Pragmatist had no ❌ items — the §6 dissent audit shows all my R1 items as ✅. For completeness I address the two §7 sub-questions that are the closest thing to unresolved tension:

**Does D-7 feel like scope creep?**

No. My R1 said "C makes sense as a Phase 2 consideration after Step G completes." D-7 is Phase 2, post-Step-G, with a trigger. It is not in the critical path. The only risk is if D-7's existence creates implicit pressure to slow down Phase-1 work ("we should design the V1.2 schema before we finalize the patches"). That risk is mitigated by the hybrid's explicit sequencing: Phase 1 is complete and independent; D-7 does not fire until 3 live scans post-Step-G. I accept D-7 as written.

**Are any of the 5 patches fragile enough that I'd rather drop one than accept the F0-verification gate?**

No. The F0-verification gate (§5.1.5) is not a cost — it is a correctness check I should have made mandatory in R1. If F0 turns out to be install-path, then the Q4 fix would make the pipeline *less* accurate than compute.py, and I would have been advocating for the wrong fix. The gate costs one lookup and prevents one potential regression. The "drop Q4 fix if F0 is install-path" fallback path is exactly right. None of the 5 patches are fragile in the sense of being wrong-headed; the Q4 patch is the only one with an empirical precondition, and the gate handles it cleanly.

**Is there a premise in the hybrid I reject?**

One minor friction: §5.1.4 says "verify schema V1.1 `additionalProperties` setting on Phase 1 input section; adjust if needed to admit new inputs." This is correct as a step but the phrase "adjust if needed" is underdetermined. If the schema has `additionalProperties: false` on the Phase 1 input block, adding new input fields would require a schema version bump, which contradicts the "V1.1 unchanged" premise of Phase 1. My preference: before applying any patch, confirm the `additionalProperties` setting first. If it is `false`, change it to `true` for the Phase 1 input block ONLY (a non-breaking extension, not a semantic change) and note the change in the schema changelog without bumping the version number. This is a FIX NOW implementation note, not a blocker to ACCEPT.

## If ACCEPT-WITH-MODIFICATIONS

Not applicable — I am voting ACCEPT. The implementation note above is a clarification for the Phase-1 executor, not a modification to the hybrid structure.

## FIX NOW items (new or re-asserted from R1)

1. **Confirm `additionalProperties` on Phase 1 input block before applying patches.** If `false`, change to `true` for that block only; document in schema changelog without version bump. This ensures the new input fields (`has_contributing_guide`, `closed_fix_lag_days`, `has_reported_fixed_vulns`, `has_warning_on_install_path`) don't trigger V1.1 validation errors on the fixture forms.

2. **F0 type lookup for zustand-v3 is a hard gate, not an advisory step.** Hybrid §5.1.5 already says this, but emphasize: if F0 is install-path, do NOT apply the Q4 split, and instead document that compute.py is correct on Q4 zustand and the comparator LLM was wrong. Gate 6.3 should then be updated to note that Q4 zustand is an accepted LLM-overshoot case, not a compute.py bug.

All other FIX NOW items from my R1 are carried forward unchanged as part of the 5 patches.

## DEFER items (anything new or promoted)

1. **D-7 trigger specificity.** The Systems Thinker's §7 sub-question asks whether the "3 live scans" trigger is objective enough. I would add one sharpening: the delta measurement should specify what counts as a "divergence where the Phase 1 patches don't reach." Suggested wording: "a cell where the LLM's phase_4 judgment differs from compute.py's advisory output AND the Phase 1 patch for that question type doesn't explain the difference." This makes the trigger unambiguous. Low-priority to add pre-Step-G; can be written into D-7 as a rider note post-Step-G.

2. **Q2 caveman fallback.** My R1 INFO #4 flagged that the Q2 caveman mismatch is the most arguable — the rubric literally supports compute.py's green. The hybrid preserves this as a fallback option (§6 Pragmatist ✅). I defer to Phase-1 execution to determine whether `closed_fix_lag_days` is cleanly derivable from already-captured Phase 1 data. If it requires a new gh API call, accepting compute.py's literal-rubric win on Q2 is the faster path and the rubric supports it.

## INFO items

1. **The hybrid's reframing of the ❌ Codex dissent is load-bearing.** §6 correctly identifies that the hybrid "directly contradicts" Codex's "do not retune compute.py to mimic the comparator scans." The rebuttal — that the 5 patches fix rubric-ambiguity gaps, not mimic accidents — is defensible for 4 of the 5 mismatches. The Q2 caveman case is the weakest (the rubric supports compute.py's green, and the `closed_fix_lag_days` patch adds an extra-rubric signal). If Codex focuses his REJECT reasoning on Q2 caveman specifically, the owner should note that dropping Q2 caveman from the patch set is a valid option that leaves the core hybrid intact.

2. **The hybrid's D-7 trigger is bet-based, not ironclad.** Three live scans is a small sample. If the next 3 scans all happen to be JS-library shapes (similar to zustand), the trigger might report "no new drift" falsely. The D-7 design should require diversity of shape (at least 2 different shape categories among the 3 trigger scans) to make the measurement meaningful.

3. **My R1 blind-spot #1 (has_contributing_guide data availability) is partially unresolved.** The hybrid promotes blind-spot #2 and #4 to explicit gates but does not explicitly address blind-spot #1. In Phase-1 execution, if the zustand Phase 1 raw capture does not include a contributing-guide flag, the implementer needs to either: (a) add a targeted `gh api` call to check for CONTRIBUTING.md presence, or (b) check the already-captured repo metadata for a contributing_url field (GitHub API returns this on the repo object). This is low-overhead but worth flagging so Phase-1 execution doesn't stall on it.

## Blind spots

1. **I have not verified whether the hybrid's D-7 trigger timing (post-Step-G, 3 live scans) is realistic given current project velocity.** If live V2.5-preview scans don't materialize for 3-6 months post-Step-G, D-7 could sit indefinitely without firing. The trigger should have a time-based fallback: if 6 months pass post-Step-G with fewer than 3 live scans, D-7 goes forward regardless.

2. **I may be underweighting the Skeptic's "42% disobedience rate" observation.** My R1 framed it as "5 specific calibration gaps" not systemic disobedience. If the next 3 Step-G validation scans produce a different 5 mismatches on different cells, the Phase-1 patches would hold for the original 3 targets but the architecture would still need V1.2. The D-7 trigger should catch this, but I cannot verify without running the pipeline on new shapes.

3. **The `governance-floor` override for Q1 Archon (formal<10% AND no branch protection AND no CODEOWNERS → force red) is a judgment call baked into compute.py.** This is the kind of contextual override that the Systems Thinker argues belongs in Phase 4, not Phase 3. I still think it's the right call for V1.1 (it's a deterministic rule, not a semantic judgment), but the Systems Thinker's critique of this specific patch is legitimate and D-7 should include it in scope when V1.2 lands.
