"""V1.2.x calibration v2 — validator gate v2.1 (rule_id REQUIRED).

Tests docs/validate-scanner-report.py --form mode enforcement of rule_id
presence on every scorecard_hint when phase_3_advisory.shape_classification
is present (signal that the bundle was authored via compute_scorecard_cells_v2).

Carry-forward #5 from docs/External-Board-Reviews/050126-calibration-rebuild/
CONSOLIDATION.md §5.

Spec: docs/calibration-design-v2.md §10 directive #14.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "docs" / "validate-scanner-report.py"


_TEMPLATE_BUNDLE = REPO_ROOT / "docs" / "scan-bundles" / "ghostty-dcc39dc.json"


def _minimal_v12_form() -> dict:
    """Load a real V1.2 bundle as a baseline + return as new dict for mutation.
    Using a real bundle ensures we get all V1.2-required top-level fields
    (schema_version, _meta, target, phase_2_validation, phase_6_assembly, etc.)
    without re-implementing the full schema in test fixtures.

    Phase 5 (back-to-basics-plan) promoted scan-bundles to v2 (added
    shape_classification + per-cell rule_id; advisory colors recomputed by
    compute_scorecard_cells_v2 may differ from phase_4 LLM colors).
    This function normalizes the loaded bundle back to a pre-v2 minimal
    state so test scaffolding is independent of bundle migrations:
      1. Strip shape_classification + per-cell rule_id/auto_fire/template_*
      2. Force advisory colors to match phase_4 LLM colors (no override
         needed → gate 6.3 passes by construction)."""
    form = json.loads(_TEMPLATE_BUNDLE.read_text())
    p3a = form.get("phase_3_advisory", {})
    p3a.pop("shape_classification", None)
    p4_cells = form.get("phase_4_structured_llm", {}).get("scorecard_cells", {})
    for key, hint in p3a.get("scorecard_hints", {}).items():
        hint.pop("rule_id", None)
        hint.pop("auto_fire", None)
        hint.pop("short_answer_template_key", None)
        hint.pop("template_vars", None)
        if key in p4_cells:
            hint["color"] = p4_cells[key].get("color", hint.get("color"))
    return form


def _v2_shape_classification() -> dict:
    return {
        "category": "cli-binary",
        "is_reverse_engineered": False,
        "is_privileged_tool": False,
        "is_solo_maintained": False,
        "confidence": "high",
        "matched_rule": "test fixture",
    }


def _run_validator(tmp_path, form: dict) -> tuple[int, str]:
    """Write form to tmp file + run --form mode. Returns (exit_code, stdout)."""
    p = tmp_path / "form.json"
    p.write_text(json.dumps(form, indent=2))
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--form", str(p)],
        capture_output=True, text=True, timeout=30,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestRuleIdEnforcement:
    """Gate v2.1: rule_id REQUIRED on every scorecard_hint when v2 was used."""

    def test_legacy_v12_form_without_shape_classification_passes(self, tmp_path):
        """No shape_classification → legacy V1.2 bundle. Gate v2.1 NOT enforced."""
        form = _minimal_v12_form()
        # No shape_classification anywhere — pre-v2 scoring
        rc, out = _run_validator(tmp_path, form)
        assert rc == 0, f"Legacy V1.2 form should validate clean. Output:\n{out}"

    def test_v2_form_with_all_rule_ids_passes(self, tmp_path):
        """shape_classification present + every cell has rule_id → gate clean."""
        form = _minimal_v12_form()
        form["phase_3_advisory"]["shape_classification"] = _v2_shape_classification()
        for k in form["phase_3_advisory"]["scorecard_hints"]:
            form["phase_3_advisory"]["scorecard_hints"][k]["rule_id"] = "FALLBACK"
        rc, out = _run_validator(tmp_path, form)
        assert rc == 0, f"V2 form with rule_ids should validate clean. Output:\n{out}"
        assert "gate v2.1: CLEAN" in out

    def test_v2_form_missing_rule_id_on_one_cell_fails(self, tmp_path):
        """shape_classification present + one cell missing rule_id → gate fails."""
        form = _minimal_v12_form()
        form["phase_3_advisory"]["shape_classification"] = _v2_shape_classification()
        # Add rule_id to 3 cells but leave Q3 missing
        for k in [
            "does_anyone_check_the_code",
            "do_they_fix_problems_quickly",
            "is_it_safe_out_of_the_box",
        ]:
            form["phase_3_advisory"]["scorecard_hints"][k]["rule_id"] = "RULE-1"
        # do_they_tell_you_about_problems intentionally missing rule_id
        rc, out = _run_validator(tmp_path, form)
        assert rc != 0, f"V2 form missing rule_id should fail validation. Output:\n{out}"
        assert "gate v2.1" in out
        assert "do_they_tell_you_about_problems" in out
        assert "rule_id MISSING" in out

    def test_v2_form_with_invalid_rule_id_fails(self, tmp_path):
        """rule_id outside RULE-1..RULE-10 + FALLBACK → fail."""
        form = _minimal_v12_form()
        form["phase_3_advisory"]["shape_classification"] = _v2_shape_classification()
        for k in form["phase_3_advisory"]["scorecard_hints"]:
            form["phase_3_advisory"]["scorecard_hints"][k]["rule_id"] = "FALLBACK"
        # Inject invalid rule_id on Q1
        form["phase_3_advisory"]["scorecard_hints"]["does_anyone_check_the_code"]["rule_id"] = "RULE-99"
        rc, out = _run_validator(tmp_path, form)
        assert rc != 0
        assert "gate v2.1" in out
        assert "RULE-99" in out

    def test_v2_form_with_all_rule_id_values_in_valid_set(self, tmp_path):
        """RULE-1 through RULE-10 + FALLBACK all accepted."""
        form = _minimal_v12_form()
        form["phase_3_advisory"]["shape_classification"] = _v2_shape_classification()
        rule_ids = ["RULE-1", "RULE-4", "RULE-6", "FALLBACK"]
        for k, rid in zip(form["phase_3_advisory"]["scorecard_hints"], rule_ids):
            form["phase_3_advisory"]["scorecard_hints"][k]["rule_id"] = rid
        rc, out = _run_validator(tmp_path, form)
        assert rc == 0, f"All-valid rule_ids should pass. Output:\n{out}"


class TestSchemaAcceptsV2Fields:
    """Schema must accept new optional fields without breaking existing bundles."""

    def test_legacy_v12_bundle_still_validates(self, tmp_path):
        """Smoke-test: a legacy form without any v2 fields validates clean."""
        form = _minimal_v12_form()
        rc, out = _run_validator(tmp_path, form)
        assert rc == 0, f"Legacy form should validate. Output:\n{out}"

    def test_v2_fields_pass_schema(self, tmp_path):
        """v2 form with shape_classification + rule_id + auto_fire +
        short_answer_template_key + template_vars must pass schema validation."""
        form = _minimal_v12_form()
        form["phase_3_advisory"]["shape_classification"] = _v2_shape_classification()
        form["phase_4_structured_llm"]["shape_classification"] = _v2_shape_classification()
        for k in form["phase_3_advisory"]["scorecard_hints"]:
            form["phase_3_advisory"]["scorecard_hints"][k].update({
                "rule_id": "RULE-1",
                "auto_fire": False,
                "short_answer_template_key": "q1.amber.governance_present",
                "template_vars": {"concentration_qualifier": "concentration risk remains"},
            })
        rc, out = _run_validator(tmp_path, form)
        assert rc == 0, f"V2 form should pass schema. Output:\n{out}"
        # Check no schema errors emitted
        assert "jsonschema: 0 error" in out or "jsonschema: CLEAN" in out

    def test_invalid_shape_category_rejected(self, tmp_path):
        """category outside the 9-enum + 'other' must fail schema validation."""
        form = _minimal_v12_form()
        form["phase_3_advisory"]["shape_classification"] = {
            "category": "definitely-not-valid-category",
            "is_reverse_engineered": False,
            "is_privileged_tool": False,
            "is_solo_maintained": False,
            "confidence": "high",
            "matched_rule": "test",
        }
        for k in form["phase_3_advisory"]["scorecard_hints"]:
            form["phase_3_advisory"]["scorecard_hints"][k]["rule_id"] = "FALLBACK"
        rc, out = _run_validator(tmp_path, form)
        assert rc != 0, "Invalid category should fail schema validation"

    def test_invalid_confidence_rejected(self, tmp_path):
        """confidence outside high/medium/low fails schema."""
        form = _minimal_v12_form()
        form["phase_3_advisory"]["shape_classification"] = {
            "category": "cli-binary",
            "is_reverse_engineered": False,
            "is_privileged_tool": False,
            "is_solo_maintained": False,
            "confidence": "extremely-low",
            "matched_rule": "test",
        }
        for k in form["phase_3_advisory"]["scorecard_hints"]:
            form["phase_3_advisory"]["scorecard_hints"][k]["rule_id"] = "FALLBACK"
        rc, out = _run_validator(tmp_path, form)
        assert rc != 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
