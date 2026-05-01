"""V1.2.x calibration v2 — regression suite against 12 V1.2 catalog bundles.

Carry-forward #4 from docs/External-Board-Reviews/050126-calibration-rebuild/
CONSOLIDATION.md §5: 'tests/test_classify_shape.py against 12 V1.2 bundles
must produce expected categories per design §3 table.' This file extends
that requirement to compute_scorecard_cells_v2() outputs — pinning the
(color, rule_id) tuple for each cell on each bundle so future regressions
are visible.

Spec: docs/calibration-design-v2.md §8 migration plan + §10 implementation
sketch.

Outcome summary (override-reduction targeting design hard floor ≤5/12):

  Pre-redesign: ~10 cell overrides across 12 V1.2 scans (~83%).
  Post-redesign with calibration v2 rules:
    - ghostty Q1: red → amber (RULE-1 governance-floor softener)
    - WLED Q1: red → amber (RULE-2 review-rate softener; 38% formal)
    - kanata Q1: red → amber (RULE-2 review-rate softener; 44% formal)
    - skills Q3: red → amber (RULE-4 sample-floor — HIGHEST-VALUE rule)
    - freerouting Q4: stays red but now rule-driven (RULE-6 auto-fire on
      deserialization + tool_loads_user_files via pcb topic)

  5 cells move from override-required to rule-driven → ~50% override
  reduction → hits design hard-floor target (≤5/12 ~42%).

  Stretch target ≤3/12 (~25%) requires RULE-7/8/9 promotion (compound
  gate: n>=2 evidence + harness signal landed). Currently INERT.

Run: python3 -m pytest tests/test_calibration_regression.py -v
"""
import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))
from compute import compute_scorecard_cells_v2

SCAN_BUNDLES = REPO_ROOT / "docs" / "scan-bundles"

# Pinned (color, rule_id) per (bundle, cell). Update DELIBERATELY when
# calibration v2 changes — each change should be reviewed against design
# intent + override-reduction metric.
EXPECTED = {
    "Baileys-8e5093c.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("red", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Note: design §8 expected Q4 red via RULE-9 if promoted; RULE-9 INERT
        # pending compound promotion gate. Current FALLBACK→amber means
        # Phase 4 LLM override is still required for Critical verdict.
    },
    "Kronos-67b630e.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("red", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Design §8 expected Q4 RULE-6 fire (deserialization + ML topic).
        # Current bundle's harness signal: deserialization.hit_count = 0
        # (the V13-3 C2 language qualifier may have suppressed pickle.load
        # detection). RULE-6 doesn't fire → harness coverage gap flagged
        # as Phase 1.5 follow-up.
    },
    "QuickLook-0cda83c.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("green", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
    },
    "WLED-01328a6.json": {
        "does_anyone_check_the_code": ("amber", "RULE-2"),
        "do_they_fix_problems_quickly": ("red", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Design §8 Q1 red→amber via RULE-2 (38% formal review). ✓
        # Design §8 Q4 red via RULE-7 if promoted (firmware no-auth + CORS).
        # RULE-7 INERT — Phase 4 LLM override still required for Critical.
    },
    "Xray-core-b465036.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("red", "FALLBACK"),
        "do_they_tell_you_about_problems": ("amber", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
    },
    "browser_terminal-9a77c4a.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("green", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Design §8 Q4 red via RULE-8 if promoted (URL typosquat).
        # RULE-8 INERT — Phase 4 LLM override still required.
    },
    "freerouting-c5ad3c7.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("green", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("red", "RULE-6"),
        # Design §8 Q4 red via RULE-6 — auto-fire on 35 ObjectInputStream hits
        # + pcb topic (tool_loads_user_files=True via _DOMAIN_TOPICS match). ✓
    },
    "ghostty-dcc39dc.json": {
        "does_anyone_check_the_code": ("amber", "RULE-1"),
        "do_they_fix_problems_quickly": ("green", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Design §8 Q1 red→amber via RULE-1 (CODEOWNERS + ruleset + 4
        # rules-on-default present). ✓ Eliminates 1 of the 10 overrides.
    },
    "kamal-6a31d14.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("green", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Design §8 expected Q1 red→amber via RULE-1, but kamal has NO
        # CODEOWNERS file — RULE-1 trigger requires CODEOWNERS. Audit's
        # projection assumed CODEOWNERS present; harness data shows
        # codeowners.found=False on kamal. RULE-3 would fire if kamal
        # were is_solo_maintained=True with has_codeql or releases>=20,
        # but kamal's contributor data shows multi-maintainer (Basecamp
        # team). Phase 4 LLM override path remains for kamal Q1.
    },
    "kanata-1c496c0.json": {
        "does_anyone_check_the_code": ("amber", "RULE-2"),
        "do_they_fix_problems_quickly": ("green", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Design §8 Q1 red→amber via RULE-2 (44% formal review). ✓
    },
    "skills-b843cb5.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("green", "FALLBACK"),
        "do_they_tell_you_about_problems": ("amber", "RULE-4"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
        # Design §8 Q3 red→amber via RULE-4 (sample-floor) — the
        # HIGHEST-VALUE rule per audit. ✓ Confirms RULE-4 firing on the
        # canonical young-repo target (90 days old + 1 lifetime PR).
    },
    "wezterm-577474d.json": {
        "does_anyone_check_the_code": ("red", "FALLBACK"),
        "do_they_fix_problems_quickly": ("red", "FALLBACK"),
        "do_they_tell_you_about_problems": ("red", "FALLBACK"),
        "is_it_safe_out_of_the_box": ("amber", "FALLBACK"),
    },
}

CELL_KEYS = [
    "does_anyone_check_the_code",
    "do_they_fix_problems_quickly",
    "do_they_tell_you_about_problems",
    "is_it_safe_out_of_the_box",
]


@pytest.fixture(scope="module")
def bundle_results():
    """Run compute_scorecard_cells_v2 against all 12 bundles once."""
    results = {}
    for fn in EXPECTED:
        form = json.loads((SCAN_BUNDLES / fn).read_text())
        results[fn] = compute_scorecard_cells_v2(form)
    return results


class TestPinnedCellOutputs:
    """Each (bundle, cell) pinned to its current (color, rule_id) tuple.
    Failures mean calibration v2 has drifted from documented behavior — verify
    the change is intentional + update the EXPECTED table with rationale."""

    @pytest.mark.parametrize("fn", list(EXPECTED.keys()))
    def test_bundle_cells_match_pinned_outputs(self, fn, bundle_results):
        result = bundle_results[fn]
        diffs = []
        for cell_key in CELL_KEYS:
            expected_color, expected_rule = EXPECTED[fn][cell_key]
            cell = result[cell_key]
            actual_color = cell["color"]
            actual_rule = cell["rule_id"]
            if (actual_color, actual_rule) != (expected_color, expected_rule):
                diffs.append(
                    f"{cell_key}: expected ({expected_color}, {expected_rule}), "
                    f"got ({actual_color}, {actual_rule})"
                )
        assert not diffs, f"{fn} drift:\n  " + "\n  ".join(diffs)


class TestRuleFiringDistribution:
    """Aggregate rule-firing counts across the 12 V1.2 catalog bundles. These
    are the override-reduction metrics from design §8 migration plan."""

    def test_rule_1_fires_on_at_least_one_scan(self, bundle_results):
        """RULE-1 governance-floor softener must fire on at least 1 scan
        in V1.2 catalog (ghostty per audit)."""
        count = sum(
            1 for r in bundle_results.values()
            if r["does_anyone_check_the_code"]["rule_id"] == "RULE-1"
        )
        assert count >= 1, "RULE-1 must fire on >=1 V1.2 catalog scan"

    def test_rule_2_fires_on_review_rate_targets(self, bundle_results):
        """RULE-2 review-rate softener must fire on WLED + kanata."""
        rule_2_scans = [
            fn for fn, r in bundle_results.items()
            if r["does_anyone_check_the_code"]["rule_id"] == "RULE-2"
        ]
        assert len(rule_2_scans) >= 2, f"RULE-2 should fire on >=2 scans, got {rule_2_scans}"

    def test_rule_4_fires_on_skills(self, bundle_results):
        """RULE-4 sample-floor (HIGHEST-VALUE rule) must fire on skills."""
        skills = bundle_results["skills-b843cb5.json"]
        q3 = skills["do_they_tell_you_about_problems"]
        assert q3["rule_id"] == "RULE-4"
        assert q3["color"] == "amber"

    def test_rule_6_fires_on_freerouting(self, bundle_results):
        """RULE-6 auto-fire (deserialization + tool_loads_user_files via pcb
        topic) must fire on freerouting per V13-3 C5 dry-run + design §8."""
        fr = bundle_results["freerouting-c5ad3c7.json"]
        q4 = fr["is_it_safe_out_of_the_box"]
        assert q4["rule_id"] == "RULE-6"
        assert q4["color"] == "red"
        assert q4["auto_fire"] is True

    def test_total_rule_driven_cells_meets_hard_floor(self, bundle_results):
        """Design §8 hard floor: >=5 cells should be rule-driven (not
        FALLBACK). This is the override-reduction target — at the §9
        ≤5/12 hard-floor acceptance threshold (post-R1 directive #1)."""
        rule_driven_count = 0
        for fn, r in bundle_results.items():
            for cell_key in CELL_KEYS:
                rid = r[cell_key]["rule_id"]
                if rid != "FALLBACK":
                    rule_driven_count += 1
        # >=5 cells rule-driven means hard floor of <=5/12 overrides remaining
        # is achievable (counting only the 12 Q1+Q3 cells where rules fire;
        # Q2 is explicitly FALLBACK-only by design).
        assert rule_driven_count >= 5, (
            f"Hard floor target unmet — only {rule_driven_count} cells rule-driven, "
            f"design §8 expects >=5"
        )

    def test_q2_is_always_fallback(self, bundle_results):
        """Per directive #16 (Q2 explicit deferral): no Q2 cell should ever
        emit a non-FALLBACK rule_id."""
        for fn, r in bundle_results.items():
            assert r["do_they_fix_problems_quickly"]["rule_id"] == "FALLBACK", (
                f"{fn} Q2 emitted non-FALLBACK rule_id — violates directive #16"
            )


class TestShapeClassificationEmbedded:
    """Every bundle's compute_scorecard_cells_v2 result must include a
    populated shape_classification block (gate v2.1 enforcement signal)."""

    @pytest.mark.parametrize("fn", list(EXPECTED.keys()))
    def test_shape_classification_present(self, fn, bundle_results):
        sc = bundle_results[fn].get("shape_classification")
        assert sc is not None
        assert sc.get("category") is not None
        assert sc["category"] != "other" or fn.startswith(("__never__",)), (
            f"{fn} classified as 'other' — should not happen on V1.2 catalog"
        )

    @pytest.mark.parametrize("fn", list(EXPECTED.keys()))
    def test_rule_id_present_on_every_cell(self, fn, bundle_results):
        """Directive #14: rule_id REQUIRED on every cell in v2 output."""
        for cell_key in CELL_KEYS:
            cell = bundle_results[fn][cell_key]
            assert "rule_id" in cell
            assert cell["rule_id"] is not None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
