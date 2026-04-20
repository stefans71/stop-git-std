# SF1 R2 — Systems Thinker (Codex GPT-5)

## Verdict on hybrid

ACCEPT-WITH-MODIFICATIONS

## Rationale (3–6 sentences)

The hybrid is acceptable only if Phase 1 is treated as a temporary compatibility patch rather than evidence that scorecard-cell authority belongs in `compute.py`. I can accept a short-term retune to unblock Step G, but I do not accept D-7 being downgraded to optional polish based only on whether the next 3 live scans happen to fit the patched thresholds. That would re-encode the original problem: a judgment-bearing output remains mechanically authoritative unless drift is observed again. The right synthesis is "A now, but C is already committed," with live-scan results determining priority and exact scope, not whether the authority-boundary fix exists at all. An objective trigger tied to new repo-shape coverage is also stronger than measured drift alone because it tests the composition boundary directly, not just whether a small sample happened to stay quiet.

## Engagement with your R1 dissent audit (the items marked ❌ in §6)

On the reframed FIX NOW #1: I accept the operational unblock, but not the architectural implication. Patching `compute.py` until both current gates pass is fine for Step G only if the record explicitly says this is a temporary compatibility measure and does not resolve the authority split.

On "do not retune compute.py to mimic the 3 comparator scans": this dissent is not fully withdrawn, but it is no longer load-bearing if the retune is boxed in. I can accept the 5 patches as a bounded bridge because the hybrid also carries the Phase-4 authority model forward; I do not accept any framing that these patches have now "solved" scorecard computation in principle.

On "compute output should become advisory during the bridge": this remains the main unresolved issue. The hybrid postpones advisory-only treatment until V1.2, which is tolerable only if D-7 is mandatory and scheduled by an objective trigger or review point, not contingent on drift being rediscovered.

## If ACCEPT-WITH-MODIFICATIONS

1. Change D-7 from conditional to committed: the post-Step-G deferred ledger should say the scorecard authority-boundary migration to V1.2 will be reviewed and dispositioned after the first expansion beyond the current validation set, not downgraded to optional polish if drift is low.
2. Replace the current trigger with a two-part trigger: start V1.2 design when either `a)` the first scan on a repo shape not represented in the current 7 catalog shapes lands, or `b)` after 3 live scans beyond Step G, whichever comes first. Measured drift should prioritize urgency, not determine whether the migration exists.
3. Add an expiry note to Phase 1: the 5 scorecard patches are a temporary compatibility layer for V1.1 Step G acceptance, and any future scorecard-threshold change after Step G should be presumed to route through D-7 review rather than ad hoc `compute.py` edits.

## FIX NOW items (new or re-asserted from R1)

- Record in the deferred ledger that D-7 is a committed architecture item, not optional polish.
- Add the two-part trigger or an equivalent objective trigger based on new repo-shape coverage, not drift alone.
- Annotate the Phase 1 scorecard patches as temporary compatibility calibration for Step G.

## DEFER items (anything new or promoted)

- Define the exact review checkpoint for D-7 disposition: owner review after first new repo shape or after 3 live scans, whichever comes first.
- Add override telemetry once V1.2 exists so recurring scorecard/computed-signal disagreements are categorized instead of handled as one-off threshold patches.

## INFO items

- The premise I reject is: "if the next 3 live scans do not drift, the authority-boundary problem was not real." Low observed drift on a tiny sample does not mean the abstraction is correct; it may just mean the sample stayed inside the patched envelope.
- The early-warning sign that should pull D-7 forward is not only numeric divergence. A single new repo shape that requires another bespoke scorecard parameter or override in `compute.py` is enough evidence that the boundary is wrong.
- I am comfortable with the hybrid rejecting Option B. Rewriting the catalog to fit current thresholds would lock in the wrong lesson.

## Blind spots

- I still have not inspected the actual schema/renderer coupling, so I may be underestimating the practical cost of making V1.2 mandatory rather than optional.
- I am assuming the owner can tolerate carrying an explicitly temporary architecture note in the deferred ledger without it being ignored later.
- I am inferring from the stated repo-shape distribution; if the current validation set already exercises the shapes that matter most operationally, the trigger may be conservative.
