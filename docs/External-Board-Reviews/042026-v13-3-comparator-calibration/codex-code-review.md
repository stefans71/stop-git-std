# V13-3 V1.2.x Implementation — Codex Code Review

## Overall verdict
BLOCK

## BS-1 (threshold mechanics)
The threshold mechanic inside the new helper is internally consistent: `derive_q4_critical_on_default_path_from_deserialization()` fires only when `dangerous_primitives.deserialization.hit_count >= threshold`, with default `threshold=3` (diff lines 70-110). The added tests cover the boundary at 2 vs 3 and custom-threshold override (diff lines 226-240 of the `tests/test_compute.py` hunk), so the default-N behavior is regression-tested.

The C2 regex change is also directionally correct. Dropping bare `deserialize` from `STEP_A_PATTERNS["deserialization"]` (diff lines 131-137) suppresses the documented ArduinoJson / serde-style FP class while preserving the unsafe-specific families actually relied on by C5: `pickle`, `ObjectInputStream`, `Marshal`, `yaml.load`, `unserialize`, `marshal`, `joblib`, `dill`. The new harness tests do cover both the ArduinoJson suppression and preservation of unsafe-specific matches (see `tests/test_phase_1_harness.py`, present in tree and passing locally).

Residual note: the helper docstring overstates what it verifies. It says the hits “contain at least one unsafe-specific pattern match” (diff lines 80-85), but the function itself only checks `hit_count`; it relies entirely on Phase 1 to have already language-qualified the family. That is acceptable if treated as a cross-module contract, but the contract should be stated more precisely.

## BS-3 (circular logic)
No new circular-logic defect is introduced by the helper itself. `compute_scorecard_cells()` remains advisory-only, and Q4 still prioritizes the incoming `has_critical_on_default_path` boolean over the amber path ([docs/compute.py](/root/tinkering/stop-git-std/docs/compute.py:280)). Under the V1.2 authority boundary, Phase 4 can still override the advisory either upward or downward.

The actual problem is different: the staged diff does not wire the new derivation into any advisory production path. I found no call site for `derive_q4_critical_on_default_path_from_deserialization()` outside its unit tests. So the documented C5 “auto-fire” contract is not yet live; Phase 4 cannot “override” an advisory signal that is never set. This is an implementation-completeness blocker, not a circularity blocker.

## FP coverage (regression tests)
Pass on criterion 3. `test_phase_1_harness.py` does regression-test the ArduinoJson suppression and unsafe-specific retention:

- `test_v13_3_c2_arduinojson_deserializejson_suppressed` asserts `deserializeJson` / `deserializeSegment` no longer count as deserialization hits.
- `test_v13_3_c2_unsafe_specific_still_matches` asserts the unsafe-specific patterns still match.

These tests are present in the current tree and match the stated C2 objective. I also ran `pytest -q tests/test_compute.py tests/test_phase_1_harness.py`; result: 110 passed.

## Helper quality (derive_tool_loads_user_files)
Mostly good: deterministic, pure, and testable. It reads only explicit arguments and has no hidden state. The test set covers README-positive, topic-positive, and negative cases, which is the right shape for a canonical compute helper.

Two issues:

- FIX NOW: the new `install_paths` parameter is unused (diff lines 38-42). That is not harmful today, but it creates a misleading API surface because the doc/design discussion frames install-path evidence as relevant. Either use it now or remove it until needed.
- NIT: the docstring says “returns False if either input is missing” (diff lines 56-57), but the implementation returns `True` if either README or topics match. The code is reasonable; the docstring is wrong.

## Other findings
FIX NOW: C5 is not actually integrated. The diff adds `derive_q4_critical_on_default_path_from_deserialization()` and tests it in isolation (diff lines 70-110, 194-240), but no staged change feeds its result into the scorecard advisory path or scan/form construction. `rg` found no non-test call site. Per CONSOLIDATION §9.1 / §9.3, this means the advertised “Q4 auto-fire” has not landed yet.

QUESTION: the review brief names Kronos as a would-collapse case, but the helper’s threshold default is 3 while the historical Kronos case was a single `pickle.load` site. That can still be consistent if the intended claim is “future rescan with widened regex + other hits/topic evidence reaches threshold,” but the current helper/test pair does not demonstrate that end-to-end production path.

NIT: the phase-1 checklist text still describes the old deserialization family including bare `deserialize`; that documentation drift is outside the staged diff but should be reconciled soon.

## Recommendation
apply listed FIX NOW items first
