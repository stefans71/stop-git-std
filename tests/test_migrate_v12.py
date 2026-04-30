"""V1.2 migration script tests — round-trip, idempotence, schema validity.

Tests migrate-v1.1-to-v1.2.py (one-time script archived at
docs/archive/migrations/ post session-8 cleanup). Uses synthetic V1.1
forms to avoid mutating real fixtures.
"""
import importlib.util
import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_MIGRATION = _REPO_ROOT / "docs" / "archive" / "migrations" / "migrate-v1.1-to-v1.2.py"
_SCHEMA = _REPO_ROOT / "docs" / "scan-schema.json"


def _load_migration():
    spec = importlib.util.spec_from_file_location("_v_migration", _MIGRATION)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def migration():
    return _load_migration()


def _sample_v11_form():
    """Minimal-but-representative V1.1 shape for migration testing."""
    return {
        "schema_version": "1.1",
        "_meta": {"scan_status": "completed"},
        "target": {"owner": "o", "repo": "r", "full_name": "o/r"},
        "phase_1_raw_capture": {
            "pre_flight": {
                "head_sha": "deadbeef",
                "default_branch": "main",
                "tarball_extracted": True,
                "symlinks_stripped": False,
                "api_rate_limit": {"remaining": 100, "limit": 5000, "reset_at": "2026-04-20T06:00:00+00:00"},
            },
            "repo_metadata": {
                "name": "r",
                "is_archived": False,
                "is_fork": False,
                "default_branch_ref": "main",
                "stargazer_count": 100,
            },
            "dependencies": {
                "manifest_files": ["package.json", "requirements.txt"],
                "dependabot": {"status": "404", "alerts": []},
                "osv_dev": {"queried": True, "total_vulns": 0, "per_package": []},
            },
            "code_patterns": {
                "executable_files": {"entries": ["scripts/install.sh"]},
                "install_hooks": {"found": False, "hooks": []},
                "agent_rule_files": {"entries": [], "count": 0, "total_bytes": 0},
                "dangerous_primitives": {"hits": [
                    {"family": "exec", "file": "a.py", "line": 10, "snippet": "eval(x)"},
                    {"family": "network", "file": "b.py", "line": 5, "snippet": "urlopen(y)"},
                ], "hit_count": 2},
                "readme_paste_blocks": {"found": False, "blocks": []},
            },
        },
        "phase_2_validation": {"validation_passed": True},
        "phase_3_computed": {
            "scorecard_cells": {
                "does_anyone_check_the_code": {"color": "amber", "short_answer": "Partly"},
                "do_they_fix_problems_quickly": {"color": "green", "short_answer": "Yes"},
                "do_they_tell_you_about_problems": {"color": "green", "short_answer": "Yes"},
                "is_it_safe_out_of_the_box": {"color": "green", "short_answer": "Yes"},
            },
        },
        "phase_4_structured_llm": {},
        "phase_4b_computed": {"verdict": {"level": "caution"}},
        "phase_5_prose_llm": {},
        "phase_6_assembly": {"assembled": True},
    }


class TestMigrationRoundTrip:
    """3 round-trip tests per §7.8."""

    def test_migrated_form_validates_against_v12_schema(self, migration):
        """V1.1 → V1.2 produces schema-valid output."""
        from jsonschema import Draft202012Validator
        form = _sample_v11_form()
        new_form = migration.migrate_form(form)
        schema = json.loads(_SCHEMA.read_text())
        errors = list(Draft202012Validator(schema).iter_errors(new_form))
        assert not errors, f"V1.2 schema errors: {[(list(e.absolute_path), e.message[:80]) for e in errors[:5]]}"

    def test_migration_is_idempotent(self, migration):
        """Running migration twice produces the same output as once."""
        form = _sample_v11_form()
        once = migration.migrate_form(form)
        twice = migration.migrate_form(once)
        assert once == twice, "migrate_form is not idempotent"

    def test_no_data_loss_for_non_dropped_fields(self, migration):
        """Field renames preserve values (archived, fork, default_branch) and scorecard colors move cleanly."""
        form = _sample_v11_form()
        new_form = migration.migrate_form(form)

        # Renames preserve values
        rm = new_form["phase_1_raw_capture"]["repo_metadata"]
        assert rm["archived"] is False
        assert rm["fork"] is False
        assert rm["default_branch"] == "main"
        assert "is_archived" not in rm
        assert "is_fork" not in rm
        assert "default_branch_ref" not in rm

        # Scorecard colors migrated
        p4_cells = new_form["phase_4_structured_llm"]["scorecard_cells"]
        assert p4_cells["does_anyone_check_the_code"]["color"] == "amber"
        assert p4_cells["is_it_safe_out_of_the_box"]["color"] == "green"
        # New V1.2 fields defaulted to null/empty
        assert p4_cells["does_anyone_check_the_code"]["rationale"] is None
        assert p4_cells["does_anyone_check_the_code"]["computed_signal_refs"] == []

        # phase_3_advisory populated
        assert "phase_3_advisory" in new_form
        hints = new_form["phase_3_advisory"]["scorecard_hints"]
        assert hints["does_anyone_check_the_code"]["color"] == "amber"

        # phase_3_computed.scorecard_cells deleted
        assert "scorecard_cells" not in new_form["phase_3_computed"]

    def test_manifest_files_string_to_object(self, migration):
        """manifest_files: [str] → [{path, format}] per D1."""
        form = _sample_v11_form()
        new_form = migration.migrate_form(form)
        mf = new_form["phase_1_raw_capture"]["dependencies"]["manifest_files"]
        assert len(mf) == 2
        assert all(isinstance(e, dict) and "path" in e for e in mf)
        assert mf[0]["path"] == "package.json"

    def test_total_bytes_dropped(self, migration):
        """agent_rule_files.total_bytes dropped per Item E; bare list with no wrapper."""
        form = _sample_v11_form()
        new_form = migration.migrate_form(form)
        arf = new_form["phase_1_raw_capture"]["code_patterns"]["agent_rule_files"]
        assert isinstance(arf, list)  # not a wrapper dict

    def test_dangerous_primitives_nested_per_family(self, migration):
        """dangerous_primitives: flat hits[] → nested per-family."""
        form = _sample_v11_form()
        new_form = migration.migrate_form(form)
        dp = new_form["phase_1_raw_capture"]["code_patterns"]["dangerous_primitives"]
        assert "exec" in dp
        assert "network" in dp
        assert "hits" not in dp  # flat shape removed
        assert dp["exec"]["files"][0]["first_match"]["line"] == 10
        assert dp["network"]["files"][0]["first_match"]["snippet"] == "urlopen(y)"

    def test_reset_at_converted_to_epoch(self, migration):
        """pre_flight.api_rate_limit.reset_at ISO → reset epoch int."""
        form = _sample_v11_form()
        new_form = migration.migrate_form(form)
        arl = new_form["phase_1_raw_capture"]["pre_flight"]["api_rate_limit"]
        assert "reset_at" not in arl
        assert isinstance(arl["reset"], int)
        assert arl["reset"] > 1_700_000_000  # sanity — epoch post-2023

    def test_symlinks_stripped_bool_to_int(self, migration):
        """pre_flight.symlinks_stripped: bool → integer (False → 0)."""
        form = _sample_v11_form()
        new_form = migration.migrate_form(form)
        ss = new_form["phase_1_raw_capture"]["pre_flight"]["symlinks_stripped"]
        assert isinstance(ss, int)
        assert ss == 0
