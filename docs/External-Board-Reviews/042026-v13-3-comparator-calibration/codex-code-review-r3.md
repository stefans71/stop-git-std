# V13-3 V1.2.x Implementation — Codex Code Review

## Overall verdict
SIGN OFF W/ NOTES

## BS-1 (threshold mechanics)
The threshold mechanic remains internally consistent. `derive_q4_critical_on_default_path_from_deserialization()` still gates on `dangerous_primitives.deserialization.hit_count >= threshold`, and `compute_scorecard_cells()` now OR-merges the Phase-1-derived auto-fire into the explicit `has_critical_on_default_path` input before Q4 rubric evaluation ([docs/compute.py](/root/tinkering/stop-git-std/docs/compute.py:224), [docs/compute.py](/root/tinkering/stop-git-std/docs/compute.py:562)).

This resolves the prior blocker in the advisory compute path itself. The integration is no longer a helper sitting unused beside production logic: the advisory scorer now consumes `phase_1_raw_capture` directly via its new optional kwarg ([docs/compute.py](/root/tinkering/stop-git-std/docs/compute.py:185)). The new `TestV13_3_C5LiveIntegrationInScorecardCells` cases exercise the actual entrypoint and cover positive, negative, backward-compat, and explicit-true non-downgrade behavior ([tests/test_compute.py](/root/tinkering/stop-git-std/tests/test_compute.py:711)).

## BS-3 (rubric ordering / safety)
The Q4 reorder is safe and fixes a real precedence bug. Under the stated rubric, “Critical on default path” is stricter than the green pinned-and-verified condition, so moving `has_critical_on_default_path` ahead of the green branch is the correct ordering ([docs/compute.py](/root/tinkering/stop-git-std/docs/compute.py:294)). For non-critical cases, the green and amber branches are unchanged in substance, so existing non-critical scorecards keep prior behavior.

I do not see a new regression introduced by the signature change. `phase_1_raw_capture` is optional and defaults to `None`, so existing callers that do not know about the new kwarg continue to get the old behavior; the dedicated compatibility test covers that explicitly ([tests/test_compute.py](/root/tinkering/stop-git-std/tests/test_compute.py:764)). The OR-merge also preserves explicit `has_critical_on_default_path=True`, so the auto-fire only upgrades and never masks a stronger caller-supplied judgment ([tests/test_compute.py](/root/tinkering/stop-git-std/tests/test_compute.py:770)).

## FP coverage (backward compatibility / live integration)
Pass on criteria 1-3.

- Criterion 1: yes, C5 is now integrated into the advisory production function rather than requiring a separate precompute wrapper call.
- Criterion 2: yes, the Q4 reorder is safe and aligns the implementation with the rubric’s intended precedence.
- Criterion 3: yes, the no-`phase_1_raw_capture` path is tested directly and is adequate as backward-compat coverage at the function boundary.

The four new live-integration tests are the right shape for this fix. They specifically prove the previously missing behavior: freerouting-shaped Phase 1 input upgrades a baseline green Q4 to red, while WLED-shaped post-C2 input does not.

## Other findings
NOTE: `compute_q4_autofires_from_phase_1()`’s docstring still describes the previous integration model: scan drivers invoking the wrapper before `compute_scorecard_cells()` and forwarding the result ([docs/compute.py](/root/tinkering/stop-git-std/docs/compute.py:567)). That is now stale relative to the implemented design, where `compute_scorecard_cells()` performs the wrapper call internally when `phase_1_raw_capture` is supplied. This is documentation drift, not a functional issue.

NOTE: the wrapper-focused test class docstring still repeats the old “suitable for forwarding into compute_scorecard_cells kwargs” framing ([tests/test_compute.py](/root/tinkering/stop-git-std/tests/test_compute.py:784)). Again, not a correctness problem, but it should be cleaned up to avoid reintroducing the obsolete call pattern in future edits.

## Recommendation
ship; optionally clean up the stale wrapper-call documentation in a follow-up
