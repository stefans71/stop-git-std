#!/usr/bin/env python3
"""
Tests for compute.classify_shape() — Phase 3 calibration v2 shape classifier.

Spec: docs/calibration-design-v2.md §3 + §4
Carry-forward: 050126-calibration-rebuild/CONSOLIDATION.md §5 item #4
  ("tests/test_classify_shape.py against 12 V1.2 bundles must produce expected
   categories per design §3 table.")

Coverage:
  - Per-step heuristic unit tests (synthetic fixtures)
  - 12-bundle V1.2 catalog gate (must produce expected categories per §3 table)
  - Cross-shape modifier helpers (_detect_reverse_engineered, _detect_privileged_tool)
  - Edge cases: empty form, missing fields, contributors shape variants

Run: python3 -m pytest tests/test_classify_shape.py -v
"""

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "docs"))
from compute import (
    classify_shape, ShapeClassification, SHAPE_CATEGORIES,
    _detect_reverse_engineered, _detect_privileged_tool,
    _has_desktop_packaging_workflows,
    _is_publishable_package_manifest,
)


SCAN_BUNDLES = REPO_ROOT / "docs" / "scan-bundles"


def _make_form(**phase_1_overrides) -> dict:
    """Build a minimal valid form for classify_shape input. Pass overrides
    as keyword args (repo_metadata=..., code_patterns=..., etc.)."""
    p1 = {
        "repo_metadata": {"primary_language": None, "topics": []},
        "code_patterns": {
            "agent_rule_files": [],
            "executable_files": [],
            "dangerous_primitives": {},
        },
        "dependencies": {"manifest_files": []},
        "install_script_analysis": {"scripts": []},
        "releases": {"count": 0, "entries": []},
        "contributors": {"top_contributors": [], "total_contributor_count": 0},
    }
    p1.update(phase_1_overrides)
    return {"phase_1_raw_capture": p1}


# ===========================================================================
# Step 1 — embedded-firmware
# ===========================================================================

class TestStep1EmbeddedFirmware:

    def test_cpp_with_esp32_topic(self):
        form = _make_form(repo_metadata={"primary_language": "C++", "topics": ["esp32", "led"]})
        sc = classify_shape(form)
        assert sc.category == "embedded-firmware"
        assert sc.confidence == "high"

    def test_c_with_arduino_topic(self):
        form = _make_form(repo_metadata={"primary_language": "C", "topics": ["arduino", "iot"]})
        sc = classify_shape(form)
        assert sc.category == "embedded-firmware"

    def test_python_with_iot_topic_does_not_fire(self):
        """Topic alone insufficient — also requires C/C++ primary."""
        form = _make_form(repo_metadata={"primary_language": "Python", "topics": ["iot"]})
        sc = classify_shape(form)
        assert sc.category != "embedded-firmware"


# ===========================================================================
# Step 2 — agent-skills-collection
# ===========================================================================

class TestStep2AgentSkillsCollection:

    def test_skills_no_fingerprint_signature(self):
        """skills-shape: 1+ rule file, NO exec, NO manifest, NO release."""
        form = _make_form(
            repo_metadata={"primary_language": "Shell", "topics": []},
            code_patterns={
                "agent_rule_files": [{"path": "CLAUDE.md", "kind": "claude"}],
                "executable_files": [],
                "dangerous_primitives": {},
            },
        )
        sc = classify_shape(form)
        assert sc.category == "agent-skills-collection"

    def test_ghostty_anti_pattern_does_not_fire(self):
        """ghostty-shape: 7 AGENTS.md but Zig + many exec + release → NOT skills."""
        form = _make_form(
            repo_metadata={"primary_language": "Zig", "topics": []},
            code_patterns={
                "agent_rule_files": [{"path": f"AGENTS.md.{i}"} for i in range(7)],
                "executable_files": [{"path": "Makefile"}],  # any exec disqualifies
                "dangerous_primitives": {},
            },
        )
        sc = classify_shape(form)
        assert sc.category != "agent-skills-collection"

    def test_markdown_canonical_skills_collection(self):
        """gstack-shape: Markdown primary + 3+ rule files."""
        form = _make_form(
            repo_metadata={"primary_language": "Markdown", "topics": []},
            code_patterns={
                "agent_rule_files": [
                    {"path": "skills/a/SKILL.md"},
                    {"path": "skills/b/SKILL.md"},
                    {"path": "skills/c/SKILL.md"},
                ],
                "executable_files": [],
                "dangerous_primitives": {},
            },
        )
        sc = classify_shape(form)
        assert sc.category == "agent-skills-collection"


# ===========================================================================
# Step 3 — desktop-application via TOPIC
# ===========================================================================

class TestStep3DesktopByTopic:

    def test_terminal_emulator_topic(self):
        form = _make_form(repo_metadata={"primary_language": "Rust", "topics": ["terminal-emulator"]})
        sc = classify_shape(form)
        assert sc.category == "desktop-application"
        assert sc.confidence == "high"

    def test_chrome_extension_topic(self):
        form = _make_form(repo_metadata={"primary_language": "Go", "topics": ["chrome-extension"]})
        sc = classify_shape(form)
        assert sc.category == "desktop-application"

    def test_quicklook_topic(self):
        form = _make_form(repo_metadata={"primary_language": "C#", "topics": ["quicklook"]})
        sc = classify_shape(form)
        assert sc.category == "desktop-application"


# ===========================================================================
# Step 4 — specialized-domain-tool via TOPIC (must fire BEFORE Step 5)
# ===========================================================================

class TestStep4DomainByTopic:

    def test_pcb_topic_fires_before_workflow_fallback(self):
        """freerouting-class: pcb topic + maybe Docker workflow. Domain topic
        must short-circuit before workflow-based desktop fallback."""
        form = _make_form(
            repo_metadata={"primary_language": "Java", "topics": ["pcb", "autorouter"]},
            code_patterns={
                "agent_rule_files": [],
                "executable_files": [{"path": ".github/workflows/docker-release.yml"}],
                "dangerous_primitives": {},
            },
        )
        sc = classify_shape(form)
        assert sc.category == "specialized-domain-tool"
        assert "domain topic" in sc.matched_rule

    def test_ml_topic(self):
        form = _make_form(repo_metadata={"primary_language": "Python", "topics": ["machine-learning", "pytorch"]})
        sc = classify_shape(form)
        assert sc.category == "specialized-domain-tool"


# ===========================================================================
# Step 4b — Python-no-fingerprint specialized-domain (Kronos catch)
# ===========================================================================

class TestStep4bPythonNoFingerprint:

    def test_kronos_python_only_requirements(self):
        """Kronos-shape: Python + requirements.txt only + 0 exec + 0 release."""
        form = _make_form(
            repo_metadata={"primary_language": "Python", "topics": []},
            code_patterns={"agent_rule_files": [], "executable_files": [], "dangerous_primitives": {}},
            dependencies={"manifest_files": [{"path": "requirements.txt", "ecosystem": "PyPI"}]},
            install_script_analysis={"scripts": [{"file": "README.md", "snippet": "pip install -r requirements.txt"}]},
        )
        sc = classify_shape(form)
        assert sc.category == "specialized-domain-tool"

    def test_python_with_pyproject_does_not_fire_here(self):
        """Python with publishable manifest (pyproject.toml) → library-package, not
        Step 4b. Step 4b is for the no-fingerprint case only."""
        form = _make_form(
            repo_metadata={"primary_language": "Python", "topics": []},
            dependencies={"manifest_files": [{"path": "pyproject.toml"}]},
        )
        sc = classify_shape(form)
        assert sc.category == "library-package"


# ===========================================================================
# Step 5 — desktop-application via WORKFLOW fallback (ghostty catch)
# ===========================================================================

class TestStep5DesktopByWorkflow:

    def test_ghostty_flatpak_snap_workflows(self):
        """ghostty-shape: empty topics but flatpak.yml + snap.yml workflows."""
        form = _make_form(
            repo_metadata={"primary_language": "Zig", "topics": []},
            code_patterns={
                "agent_rule_files": [],
                "executable_files": [
                    {"path": ".github/workflows/flatpak.yml"},
                    {"path": ".github/workflows/snap.yml"},
                ],
                "dangerous_primitives": {},
            },
        )
        sc = classify_shape(form)
        assert sc.category == "desktop-application"
        assert "desktop-packaging workflows" in sc.matched_rule

    def test_kanata_macos_build_does_not_false_match(self):
        """kanata-class: macos-build.yml is cross-platform CLI build, NOT GUI.
        Substring `macos` must NOT match `macos-build.yml`."""
        form = _make_form(
            repo_metadata={"primary_language": "Rust", "topics": []},
            code_patterns={
                "agent_rule_files": [],
                "executable_files": [{"path": ".github/workflows/macos-build.yml"}],
                "dangerous_primitives": {},
            },
            dependencies={"manifest_files": [{"path": "Cargo.toml"}]},
            releases={"count": 50, "entries": []},
        )
        sc = classify_shape(form)
        # With Rust + Cargo + 50 releases, this routes to cli-binary
        assert sc.category == "cli-binary"

    def test_freerouting_create_snapshot_does_not_false_match(self):
        """freerouting-class: create-snapshot.yml workflow contains `snap`
        substring. Exact-basename match must NOT trigger desktop fallback."""
        form = _make_form(
            repo_metadata={"primary_language": "Java", "topics": []},
            code_patterns={
                "agent_rule_files": [],
                "executable_files": [{"path": ".github/workflows/create-snapshot.yml"}],
                "dangerous_primitives": {},
            },
        )
        # Without domain topic + without true desktop workflow, falls to other
        sc = classify_shape(form)
        assert sc.category != "desktop-application"


# ===========================================================================
# Step 7 — cli-binary (language-canonical: Go/Rust/Ruby/etc.)
# ===========================================================================

class TestStep7CliBinary:

    def test_rust_cargo_with_releases(self):
        form = _make_form(
            repo_metadata={"primary_language": "Rust", "topics": []},
            dependencies={"manifest_files": [{"path": "Cargo.toml"}]},
            releases={"count": 30, "entries": []},
        )
        sc = classify_shape(form)
        assert sc.category == "cli-binary"

    def test_go_module_with_releases(self):
        form = _make_form(
            repo_metadata={"primary_language": "Go", "topics": []},
            dependencies={"manifest_files": [{"path": "go.mod"}]},
            releases={"count": 100, "entries": []},
        )
        sc = classify_shape(form)
        assert sc.category == "cli-binary"

    def test_ruby_gemfile_with_releases(self):
        form = _make_form(
            repo_metadata={"primary_language": "Ruby", "topics": []},
            dependencies={"manifest_files": [{"path": "Gemfile"}]},
            releases={"count": 70, "entries": []},
        )
        sc = classify_shape(form)
        assert sc.category == "cli-binary"

    def test_javascript_with_package_json_falls_to_library(self):
        """Baileys-shape: JS + package.json + many releases → library, NOT cli-binary."""
        form = _make_form(
            repo_metadata={"primary_language": "JavaScript", "topics": []},
            dependencies={"manifest_files": [{"path": "package.json"}]},
            releases={"count": 42, "entries": []},
        )
        sc = classify_shape(form)
        assert sc.category == "library-package"

    def test_typescript_with_package_json_falls_to_library(self):
        form = _make_form(
            repo_metadata={"primary_language": "TypeScript", "topics": []},
            dependencies={"manifest_files": [{"path": "package.json"}]},
            releases={"count": 30, "entries": []},
        )
        sc = classify_shape(form)
        assert sc.category == "library-package"


# ===========================================================================
# Step 9 — Fallback to 'other'
# ===========================================================================

class TestStep9Fallback:

    def test_empty_form(self):
        form = _make_form()
        sc = classify_shape(form)
        assert sc.category == "other"
        assert sc.confidence == "low"

    def test_missing_phase_1(self):
        sc = classify_shape({})
        assert sc.category == "other"
        assert sc.confidence == "low"

    def test_unrecognized_combination(self):
        form = _make_form(
            repo_metadata={"primary_language": "Haskell", "topics": []},
            # Haskell with no manifests, no exec, no releases — falls to other
        )
        sc = classify_shape(form)
        assert sc.category == "other"


# ===========================================================================
# Cross-shape modifier helpers
# ===========================================================================

class TestDetectReverseEngineered:

    def test_whatsapp_web_topic_fires(self):
        form = _make_form(repo_metadata={"primary_language": "JavaScript", "topics": ["whatsapp-web", "ws"]})
        assert _detect_reverse_engineered(form) is True

    def test_reverse_engineering_topic_fires(self):
        form = _make_form(repo_metadata={"topics": ["reverse-engineering"]})
        assert _detect_reverse_engineered(form) is True

    def test_no_topics_returns_false(self):
        form = _make_form()
        assert _detect_reverse_engineered(form) is False


class TestDetectPrivilegedTool:

    def test_terminal_emulator_topic_fires(self):
        form = _make_form(repo_metadata={"topics": ["terminal-emulator"]})
        assert _detect_privileged_tool(form) is True

    def test_keyboard_topic_fires(self):
        form = _make_form(repo_metadata={"topics": ["keyboard", "interception-driver"]})
        assert _detect_privileged_tool(form) is True

    def test_chrome_extension_topic_fires(self):
        form = _make_form(repo_metadata={"topics": ["chrome-extension"]})
        assert _detect_privileged_tool(form) is True

    def test_vpn_topic_fires(self):
        form = _make_form(repo_metadata={"topics": ["vpn", "proxy"]})
        assert _detect_privileged_tool(form) is True

    def test_no_topics_returns_false(self):
        form = _make_form()
        assert _detect_privileged_tool(form) is False


class TestHasDesktopPackagingWorkflows:

    def test_flatpak_yml_basename_matches(self):
        files = [{"path": ".github/workflows/flatpak.yml"}]
        assert _has_desktop_packaging_workflows(files) is True

    def test_snap_yml_basename_matches(self):
        files = [{"path": ".github/workflows/snap.yml"}]
        assert _has_desktop_packaging_workflows(files) is True

    def test_create_snapshot_does_NOT_match(self):
        """Substring trap: 'snap' is in 'snapshot' — must use exact basename."""
        files = [{"path": ".github/workflows/create-snapshot.yml"}]
        assert _has_desktop_packaging_workflows(files) is False

    def test_macos_build_does_NOT_match(self):
        """Substring trap: 'macos' in 'macos-build.yml' must not fire."""
        files = [{"path": ".github/workflows/macos-build.yml"}]
        assert _has_desktop_packaging_workflows(files) is False


class TestIsPublishablePackageManifest:

    def test_package_json_is_publishable(self):
        assert _is_publishable_package_manifest([{"path": "package.json"}]) is True

    def test_cargo_toml_is_publishable(self):
        assert _is_publishable_package_manifest([{"path": "Cargo.toml"}]) is True

    def test_gemspec_is_publishable(self):
        assert _is_publishable_package_manifest([{"path": "myproject.gemspec"}]) is True

    def test_requirements_txt_is_NOT_publishable(self):
        """Pure dependency-tracking, not package-publishing."""
        assert _is_publishable_package_manifest([{"path": "requirements.txt"}]) is False

    def test_package_lock_alone_is_NOT_publishable(self):
        """Lockfiles aren't publish manifests."""
        assert _is_publishable_package_manifest([{"path": "package-lock.json"}]) is False


# ===========================================================================
# 12-bundle V1.2 catalog gate (CONSOLIDATION §5 carry-forward #4)
# ===========================================================================

class TestV12CatalogGate:
    """The §4 validation requirement: classify_shape() must produce the
    expected category for each of the 12 V1.2 catalog scan bundles per the
    design §3 table. This is a Phase 3 BLOCKER — must hit 12/12."""

    EXPECTED_CATEGORIES = {
        'ghostty-dcc39dc.json':           'desktop-application',
        'Kronos-67b630e.json':            'specialized-domain-tool',
        'kamal-6a31d14.json':             'cli-binary',
        'Xray-core-b465036.json':         'cli-binary',
        'browser_terminal-9a77c4a.json':  'desktop-application',
        'wezterm-577474d.json':           'desktop-application',
        'QuickLook-0cda83c.json':         'desktop-application',
        'kanata-1c496c0.json':            'cli-binary',
        'freerouting-c5ad3c7.json':       'specialized-domain-tool',
        'WLED-01328a6.json':              'embedded-firmware',
        'Baileys-8e5093c.json':           'library-package',
        'skills-b843cb5.json':            'agent-skills-collection',
    }

    @classmethod
    def _load_form(cls, fn: str) -> dict:
        return json.loads((SCAN_BUNDLES / fn).read_text())

    def test_each_bundle_classifies_correctly(self):
        misses = []
        for fn, expected in self.EXPECTED_CATEGORIES.items():
            form = self._load_form(fn)
            sc = classify_shape(form)
            if sc.category != expected:
                misses.append(f"{fn}: expected {expected}, got {sc.category} ({sc.matched_rule})")
        assert not misses, "Per-bundle classification misses:\n  " + "\n  ".join(misses)

    def test_all_12_bundles_classify_to_known_category(self):
        for fn in self.EXPECTED_CATEGORIES:
            form = self._load_form(fn)
            sc = classify_shape(form)
            assert sc.category in SHAPE_CATEGORIES, (
                f"{fn} produced unknown category: {sc.category}"
            )

    def test_baileys_is_reverse_engineered(self):
        form = self._load_form("Baileys-8e5093c.json")
        sc = classify_shape(form)
        assert sc.is_reverse_engineered is True

    def test_skills_is_solo_maintained(self):
        """Audit data: mattpocock 87.3% commit share."""
        form = self._load_form("skills-b843cb5.json")
        sc = classify_shape(form)
        assert sc.is_solo_maintained is True

    def test_privileged_tool_distribution_reasonable(self):
        """Audit expects ~6 of 12 V1.2 scans to flag is_privileged_tool.
        The detector uses topics; some misses (ghostty no topics) and false
        positives (Xray-core proxy/vpn topics fire) are acceptable."""
        count = 0
        for fn in self.EXPECTED_CATEGORIES:
            form = self._load_form(fn)
            sc = classify_shape(form)
            if sc.is_privileged_tool:
                count += 1
        # Expect 4-7 inclusive — substantively close to the audit's ~6.
        assert 4 <= count <= 7, f"is_privileged_tool count {count} outside expected band [4,7]"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
