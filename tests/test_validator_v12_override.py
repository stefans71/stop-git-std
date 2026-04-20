"""V1.2 validator tests — gate 6.3 override-explained.

Tests docs/validate-scanner-report.py::validate_override_rationale.
Pseudocode + contract: docs/External-Board-Reviews/042026-schema-v12/CONSOLIDATION.md §5 Item A.
"""
import importlib.util
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_VALIDATOR = _HERE.parent / "docs" / "validate-scanner-report.py"
_COMPUTE = _HERE.parent / "docs" / "compute.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def validator():
    return _load("_v_scanner_report", _VALIDATOR)


@pytest.fixture(scope="module")
def compute():
    return _load("_v_compute", _COMPUTE)


class TestOverrideRationaleGate:
    """5 tests per §7.8 for validate_override_rationale coverage."""

    def test_no_override_no_enforcement(self, validator, compute):
        """When Phase 4 color == advisory color, no rationale/refs/reason required."""
        cell = {"color": "amber"}  # no rationale, refs, reason
        hint = {"color": "amber"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert errors == []

    def test_override_without_refs_fails(self, validator, compute):
        """Phase 4 amber, advisory red, override_reason + rationale but refs empty → fail."""
        cell = {
            "color": "amber",
            "rationale": "The harness threshold is too strict for this shape; manual review shows the repo handles security responsibly across multiple vectors.",
            "computed_signal_refs": [],
            "override_reason": "threshold_too_strict",
        }
        hint = {"color": "red"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert any("computed_signal_refs must be non-empty" in e for e in errors)

    def test_override_with_short_rationale_fails(self, validator, compute):
        """Rationale below 50-char floor → fail even when other fields are fine."""
        cell = {
            "color": "green",
            "rationale": "ok",  # < 50 chars
            "computed_signal_refs": ["q1_has_branch_protection"],
            "override_reason": "missing_qualitative_context",
        }
        hint = {"color": "amber"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert any("rationale must be ≥" in e for e in errors)

    def test_override_with_unknown_ref_fails(self, validator, compute):
        """Ref ID not in compute.SIGNAL_IDS → fail with explicit unknown-IDs error."""
        cell = {
            "color": "red",
            "rationale": "Branch protection is off and the repo has no CODEOWNERS, so the advisory amber color understates actual governance risk.",
            "computed_signal_refs": ["q1_not_a_real_signal_id"],
            "override_reason": "threshold_too_lenient",
        }
        hint = {"color": "amber"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert any("unknown signal IDs" in e for e in errors)

    def test_override_with_unknown_reason_fails(self, validator, compute):
        """override_reason not in OVERRIDE_REASON_ENUM → fail."""
        cell = {
            "color": "green",
            "rationale": "This repo has exemplary practices that the advisory rubric does not capture adequately for this particular shape.",
            "computed_signal_refs": ["q1_has_branch_protection"],
            "override_reason": "made_this_up",
        }
        hint = {"color": "amber"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert any("override_reason must be one of" in e for e in errors)

    def test_valid_override_passes(self, validator, compute):
        """All fields correct: refs resolve, rationale ≥ 50, reason in enum → no errors."""
        cell = {
            "color": "amber",
            "rationale": "Formal review rate sits at 8% but the repo has CONTRIBUTING.md and active non-vuln PR responsiveness; amber rather than red is the honest read.",
            "computed_signal_refs": ["q1_formal_review_rate", "q3_has_contributing_guide"],
            "override_reason": "missing_qualitative_context",
        }
        hint = {"color": "red"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert errors == []

    def test_override_missing_reason_fails(self, validator, compute):
        """override_reason=None on an override → fail with required-when-overriding message."""
        cell = {
            "color": "amber",
            "rationale": "Advisory color feels too strict given the qualitative evidence of active maintenance and documentation.",
            "computed_signal_refs": ["q1_formal_review_rate"],
            "override_reason": None,
        }
        hint = {"color": "red"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert any("override_reason required" in e for e in errors)


class TestSignalIDVocabulary:
    """2 tests per §7.8 for compute.SIGNAL_IDS frozen vocabulary."""

    def test_signal_ids_is_frozenset_of_25(self, compute):
        """V1.2.x (V13-1 signal widening) 2026-04-20 added 2 signals:
        q1_has_ruleset_protection + q2_oldest_open_security_item_age_days.
        Adding signals is V1.2.x per board Item F; removing any is V1.3.
        """
        assert isinstance(compute.SIGNAL_IDS, frozenset)
        assert len(compute.SIGNAL_IDS) == 25, (
            f"V1.2.x signal vocabulary expected at 25 entries (23 frozen + 2 V13-1 additions); got {len(compute.SIGNAL_IDS)}"
        )
        assert "q1_has_ruleset_protection" in compute.SIGNAL_IDS
        assert "q2_oldest_open_security_item_age_days" in compute.SIGNAL_IDS

    def test_signal_ids_question_scoping(self, compute):
        """Every ID must have a question-scoped prefix (q1_/q2_/q3_/q4_) or c20_ supporting prefix."""
        allowed_prefixes = ("q1_", "q2_", "q3_", "q4_", "c20_")
        for sid in compute.SIGNAL_IDS:
            assert any(sid.startswith(p) for p in allowed_prefixes), (
                f"signal ID {sid!r} violates question-scoped naming convention"
            )

    def test_override_reason_enum_is_7_values(self, compute):
        """V13-1 owner directive 2026-04-20 expanded enum from 5 to 7.

        Original 5 frozen per V1.2 board Item C; signal_vocabulary_gap +
        harness_coverage_gap added after 3/3 V1.2 wild scans showed 100%
        of observed overrides cited missing_qualitative_context — split
        needed by fix surface (compute.py vs phase_1_harness.py vs
        inherent-judgment).
        """
        assert isinstance(compute.OVERRIDE_REASON_ENUM, frozenset)
        assert compute.OVERRIDE_REASON_ENUM == frozenset({
            "threshold_too_strict",
            "threshold_too_lenient",
            "missing_qualitative_context",
            "rubric_literal_vs_intent",
            "signal_vocabulary_gap",
            "harness_coverage_gap",
            "other",
        })

    def test_signal_vocabulary_gap_override_passes(self, validator, compute):
        """V13-1: signal_vocabulary_gap is the fix-surface=compute.py label."""
        cell = {
            "color": "amber",
            "rationale": "Advisory flagged red because q1_has_branch_protection reads only classic status; the repo uses ruleset-based protection which isn't encoded as a signal yet — compute.py fix needed.",
            "computed_signal_refs": ["q1_has_branch_protection", "q1_has_codeowners"],
            "override_reason": "signal_vocabulary_gap",
        }
        hint = {"color": "red"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert errors == []

    def test_harness_coverage_gap_override_passes(self, validator, compute):
        """V13-1: harness_coverage_gap is the fix-surface=phase_1_harness.py label."""
        cell = {
            "color": "red",
            "rationale": "Advisory computed amber because q4_has_critical_on_default_path returned False; the harness's dangerous_primitives regex didn't match pickle.load — phase_1_harness.py fix needed.",
            "computed_signal_refs": ["q4_has_critical_on_default_path", "q4_all_channels_pinned"],
            "override_reason": "harness_coverage_gap",
        }
        hint = {"color": "amber"}
        errors = validator.validate_override_rationale(
            cell, hint, compute.SIGNAL_IDS, compute.OVERRIDE_REASON_ENUM
        )
        assert errors == []
