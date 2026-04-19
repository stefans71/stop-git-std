"""Tests for U-5/PD3 bundle/citation validator (docs/validate-scanner-report.py
--bundle mode). Covers the Operator Guide §11.1 citation-discipline rule and
the §9.2.1 pre-render checklist automation.
"""

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "validate_scanner_report", REPO_ROOT / "docs" / "validate-scanner-report.py"
)
vsr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vsr)

check_bundle = vsr.check_bundle
parse_bundle_regions = vsr.parse_bundle_regions

BUNDLES_DIR = REPO_ROOT / "docs" / "board-review-data" / "scan-bundles"


def _tmp(content: str, suffix: str = ".md") -> Path:
    fd = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    fd.write(content)
    fd.close()
    return Path(fd.name)


class TestBundleParser:
    """Region classification correctness."""

    def test_evidence_sections_collected(self):
        bundle = (
            "# repo Scan Bundle\n"
            "## Repo identity\nfacts\n\n"
            "## Governance (C20 check)\nmore facts\n\n"
            "## Step A grep results\ngrep output\n\n"
            "## FINDINGS SUMMARY\nF0: test\n"
        )
        regions = parse_bundle_regions(bundle)
        assert "Repo identity" in regions["evidence"]
        assert "Governance (C20 check)" in regions["evidence"]
        assert "Step A grep results" in regions["evidence"]
        assert len(regions["evidence"]) == 3

    def test_pattern_recognition_captured(self):
        bundle = "## Pattern recognition (inference)\n- X resembles Y\n"
        regions = parse_bundle_regions(bundle)
        assert "resembles" in regions["pattern"]

    def test_synthesis_sections_classified(self):
        bundle = (
            "## FINDINGS SUMMARY\nF0\n\n"
            "## Proposed verdict\ntext\n\n"
            "## Proposed scorecard\ncell\n\n"
            "## Catalog metadata\nmeta\n"
        )
        regions = parse_bundle_regions(bundle)
        assert len(regions["synthesis"]) == 4

    def test_compact_findings_heading_is_synthesis(self):
        # zustand-v3-style compact bundle uses "## Findings" alone
        bundle = "## Findings\n- F0: test\n"
        regions = parse_bundle_regions(bundle)
        assert "Findings" in regions["synthesis"]
        assert "Findings" not in regions["evidence"]

    def test_custom_evidence_section_defaults_correctly(self):
        # Any ## heading not matching pattern/synthesis keywords goes to evidence
        bundle = "## npm registry\n- 57k weekly downloads\n"
        regions = parse_bundle_regions(bundle)
        assert "npm registry" in regions["evidence"]


class TestBundleCorpus:
    """All existing V2.4 findings-bundle.md files must pass the validator."""

    def test_hermes_agent_bundle_passes(self):
        errors, _ = check_bundle(BUNDLES_DIR / "hermes-agent-764536b.md")
        assert errors == 0

    def test_open_lovable_bundle_passes(self):
        errors, _ = check_bundle(BUNDLES_DIR / "open-lovable-69bd93b.md")
        assert errors == 0

    def test_postiz_app_bundle_passes(self):
        errors, _ = check_bundle(BUNDLES_DIR / "postiz-app-386fc7b.md")
        assert errors == 0

    def test_zustand_bundle_passes(self):
        errors, _ = check_bundle(BUNDLES_DIR / "zustand-3201328.md")
        assert errors == 0

    def test_zustand_v3_bundle_passes(self):
        errors, _ = check_bundle(BUNDLES_DIR / "zustand-v3-3201328.md")
        assert errors == 0


class TestBundleFailCases:
    """Synthetic bundles that must fail specific contract checks."""

    def test_interpretive_verb_in_evidence_fails(self):
        bundle = (
            "## Governance\nRepo has no branch protection. This resembles fd's gap pattern.\n\n"
            "## FINDINGS SUMMARY\n### F0 — Test\nFact.\n\n"
            "## Proposed verdict\nF0 caution.\n"
        )
        p = _tmp(bundle)
        errors, _ = check_bundle(p)
        p.unlink()
        assert errors >= 1, "Interpretive verb in evidence section must fail"

    def test_pattern_bullet_without_interpretive_verb_fails(self):
        bundle = (
            "## Repo identity\nfacts\n\n"
            "## Pattern recognition (inference)\n"
            "- X resembles Y\n"
            "- Bare statement with no interpretive verb at all\n\n"
            "## FINDINGS SUMMARY\n### F0 — Test\nFact.\n\n"
            "## Proposed verdict\nF0 caution.\n"
        )
        p = _tmp(bundle)
        errors, _ = check_bundle(p)
        p.unlink()
        assert errors >= 1, "Pattern recognition bullet without interpretive verb must fail"

    def test_missing_findings_summary_fails(self):
        bundle = (
            "## Repo identity\nfacts\n\n"
            "## Proposed verdict\ncaution — no F-ID cited\n"
        )
        p = _tmp(bundle)
        errors, _ = check_bundle(p)
        p.unlink()
        assert errors >= 1, "Missing FINDINGS SUMMARY must fail"

    def test_verdict_without_fid_or_severity_fails(self):
        bundle = (
            "## Repo identity\nfacts\n\n"
            "## FINDINGS SUMMARY\n### F0 — Test\nFact.\n\n"
            "## Proposed verdict\nSome hand-wavy text with no severity word and no F-ID reference.\n"
        )
        p = _tmp(bundle)
        errors, _ = check_bundle(p)
        p.unlink()
        assert errors >= 1, "Verdict without F-ID or severity must fail"

    def test_orphan_fid_in_scorecard_fails(self):
        bundle = (
            "## Repo identity\nfacts\n\n"
            "## FINDINGS SUMMARY\n### F0 — Test\nFact.\n\n"
            "## Proposed verdict\nF0 caution.\n\n"
            "## Proposed scorecard\n"
            "1. Check: amber — driven by F99 (not in summary!)\n"
        )
        p = _tmp(bundle)
        errors, _ = check_bundle(p)
        p.unlink()
        assert errors >= 1, "F-ID referenced outside FINDINGS SUMMARY must fail as orphan"


class TestBundleHappyPath:
    """A minimal synthetic bundle that exercises every contract cleanly."""

    def test_minimal_fully_compliant_bundle(self):
        bundle = (
            "# Synthetic Scan — Evidence Bundle\n\n"
            "## Repo identity\nowner/repo @ 0000000 facts only\n\n"
            "## Governance (C20 check)\nclassic 404, rulesets [], no CODEOWNERS\n\n"
            "## Pattern recognition (inference)\n"
            "- Profile resembles prior scans with similar governance gap\n"
            "- Release cadence suggests active maintenance\n\n"
            "## FINDINGS SUMMARY\n"
            "### F0 — Governance SPOF (C20) — Warning\n"
            "No branch protection, no rulesets, no CODEOWNERS.\n\n"
            "## Proposed verdict\n"
            "caution — driven by F0 Warning\n\n"
            "## Proposed scorecard\n"
            "1. Code review: amber — governance gap per F0\n\n"
            "## Catalog metadata\n"
            "Category: test | Verdict: caution\n"
        )
        p = _tmp(bundle)
        errors, warnings = check_bundle(p)
        p.unlink()
        assert errors == 0, f"Minimal compliant bundle should pass; got {errors} errors"
