# V13-3 V1.2.x Implementation — Codex Code Review

## Overall verdict
BLOCK

## BS-1 (threshold mechanics)
The threshold mechanic remains internally consistent. `derive_q4_critical_on_default_path_from_deserialization()` still gates on `dangerous_primitives.deserialization.hit_count >= threshold`, default `threshold=3`, and the new wrapper `compute_q4_autofires_from_phase_1()` preserves that behavior rather than altering it. The added tests cover freerouting-shaped positive, WLED-shaped negative, null/missing inputs, and no-file-loading negative cases; targeted compute tests pass locally (`pytest -q tests/test_compute.py`: 80 passed).

The prior docstring precision concern is resolved. The helper docstring no longer claims it verifies unsafe-specific pattern matches itself; it now states the actual cross-module contract: this helper consumes only aggregate `hit_count` and relies on Phase 1 language qualification.

Residual note only: the wrapper currently exercises only the `repo_metadata.topics` branch because README text is not stored in `phase_1_raw_capture`. That is accurately documented in the wrapper docstring, so this is not a correctness defect in the staged diff.

## BS-3 (circular logic)
No circular-logic defect was introduced. Q4 still depends on the explicit `has_critical_on_default_path` input to `compute_scorecard_cells()`, and the new wrapper is structurally the right place to derive that advisory signal from Phase 1 raw capture before scorecard computation.

However, the original implementation-completeness blocker is still present: I still found no non-test call site for `compute_q4_autofires_from_phase_1()` or the lower-level derivation helper anywhere in the repository. `rg` finds definitions and tests, but no scan driver / `build_form.py` / advisory production path invoking the wrapper. The wrapper docstring says future callers should invoke it before `compute_scorecard_cells()`, but that is still a prospective integration note, not a landed integration.

So the advertised C5 “auto-fire live in advisory production” contract is still not satisfied by this diff. The new wrapper is necessary, but not sufficient.

## FP coverage (regression tests)
Pass on the regression-test criterion. The staged tests are materially stronger than in the first pass:

- `TestV13_3_Q4AutoFireFromDeserialization` covers freerouting-shaped, Kronos-shaped, WLED-shaped, below-threshold, missing-input, and custom-threshold behavior.
- `TestV13_3_ComputeQ4AutofiresFromPhase1` covers the new Phase-1-shaped wrapper on positive and negative cases.

These tests demonstrate the helper and wrapper behavior in isolation. They do not change the integration finding above.

## Helper quality (derive_tool_loads_user_files)
Resolved.

- The unused `install_paths` parameter has been removed from the function signature.
- The docstring now correctly describes OR logic and no longer contradicts the implementation.

The helper remains deterministic, pure, and testable.

## Other findings
Resolved from first pass:

- The Kronos threshold question is now clarified in the `derive_q4_critical_on_default_path_from_deserialization()` docstring: a single `pickle.load` site is below the default threshold, and any broader collapse claim depends on earlier regex widening rather than this helper alone.
- `docs/phase-1-checklist.md` A2 row has been updated to remove the stale bare-`deserialize` reference and document the V13-3 C2 language qualifier.

Still FIX NOW:

- C5 is still not integrated into any non-test advisory production path. Adding `compute_q4_autofires_from_phase_1()` does not by itself make the auto-fire live; a real caller must invoke it and forward `has_critical_on_default_path` into `compute_scorecard_cells()`.

## Recommendation
apply listed FIX NOW item first
