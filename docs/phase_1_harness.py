#!/usr/bin/env python3
"""
phase_1_harness.py — executable implementation of docs/phase-1-checklist.md

Runs every external call prescribed by the V2.4 scanner prompt
(docs/repo-deep-dive-prompt.md Steps 1-8 + A/B/C + pre-flight), writes
results into a schema-valid phase_1_raw_capture JSON structure per
docs/scan-schema.json.

Usage:
    python3 phase_1_harness.py <owner/repo> [--head-sha <sha>] [--scan-dir DIR]
                               [--out FORM_JSON] [--skip-tarball]
                               [--skip-gitleaks]

Output: a JSON file containing top-level `{target, _meta, pre_flight-only}`
with `phase_1_raw_capture` fully populated from external calls. The LLM
operator then layers Phase 4 findings + prose on top.

External dependencies: gh (GitHub CLI), curl, tar, find, grep (plus optional
gitleaks). All other logic is pure Python 3.10+.

Design: every prompt step is a function. Each function returns a dict that
maps directly to a phase_1_raw_capture sub-field. main() composes them.
Failure modes captured per checklist (not silently omitted).
"""

from __future__ import annotations
import argparse
import base64
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str] | str, timeout: int = 60, shell: bool = False,
         input_data: str | None = None) -> tuple[int, str, str]:
    """Run a subprocess, return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True,
            timeout=timeout, input=input_data,
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return -2, "", f"command not found: {e}"


def _gh_api(path: str, jq: str | None = None, paginate: bool = False,
            timeout: int = 45) -> tuple[int, Any]:
    """Run `gh api` and return (returncode, parsed-json-or-text)."""
    cmd = ["gh", "api", path]
    if paginate:
        cmd.append("--paginate")
    if jq:
        cmd.extend(["--jq", jq])
    rc, out, err = _run(cmd, timeout=timeout)
    if rc != 0:
        return rc, {"error": err.strip() or out.strip(), "path": path}
    if jq:
        # jq output: already coerced; try JSON parse, fall back to raw
        out_stripped = out.strip()
        try:
            return rc, json.loads(out_stripped)
        except (json.JSONDecodeError, ValueError):
            return rc, out_stripped
    try:
        return rc, json.loads(out)
    except json.JSONDecodeError:
        return rc, out


def _curl_json(url: str, timeout: int = 15) -> tuple[int, Any]:
    """Fetch a JSON URL via curl; return (status_code_equivalent, parsed)."""
    rc, out, err = _run(
        ["curl", "-fsSL", "--max-time", str(timeout), url],
        timeout=timeout + 2,
    )
    if rc != 0:
        return rc, {"error": err.strip() or out.strip(), "url": url}
    try:
        return rc, json.loads(out)
    except json.JSONDecodeError:
        return rc, out


def _b64_decode_contents(contents_response: dict) -> str | None:
    """Decode `content` field from a `gh api contents/PATH` response."""
    if not isinstance(contents_response, dict):
        return None
    content = contents_response.get("content")
    if not content:
        return None
    try:
        return base64.b64decode(content).decode("utf-8", errors="replace")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------


def pre_flight(owner_repo: str, head_sha_override: str | None = None,
               scan_dir: Path | None = None,
               skip_tarball: bool = False) -> tuple[dict, Path | None]:
    """Run pre-flight steps pf1-pf6. Returns (pre_flight_dict, scan_dir).

    scan_dir is the Path to extracted tarball (or None if skipped/failed).
    """
    out: dict[str, Any] = {"head_sha": None, "default_branch": None}

    # pf1: verify repo exists
    rc, data = _gh_api(f"repos/{owner_repo}", jq=".full_name")
    if rc != 0:
        raise SystemExit(f"pf1 failure: repo {owner_repo} not found ({data})")
    if data != owner_repo:
        raise SystemExit(f"pf1 mismatch: {data} != {owner_repo}")

    # pf2: default branch
    rc, data = _gh_api(f"repos/{owner_repo}", jq=".default_branch")
    if rc != 0:
        raise SystemExit(f"pf2 failure: default_branch")
    out["default_branch"] = data

    # pf3: head_sha
    if head_sha_override:
        out["head_sha"] = head_sha_override
    else:
        rc, data = _gh_api(
            f"repos/{owner_repo}/commits/{out['default_branch']}",
            jq=".sha",
        )
        if rc != 0:
            raise SystemExit(f"pf3 failure: head_sha")
        out["head_sha"] = data

    # pf4 + pf5: tarball extract
    out["tarball_extracted"] = False
    out["tarball_file_count"] = None
    out["symlinks_stripped"] = None
    if not skip_tarball:
        scan_dir = scan_dir or Path(
            tempfile.mkdtemp(prefix=f"scan-{owner_repo.replace('/', '-')}-")
        )
        scan_dir.mkdir(parents=True, exist_ok=True)
        # Fetch tarball via gh api (follows redirects) and pipe to tar.
        # Default GNU tar behavior strips leading / from paths — no extra flag
        # needed (V2.4 prompt's --no-absolute-names is bsdtar-only; GNU tar 1.34
        # rejects it). strip-components=1 removes the owner-repo-sha/ wrapper dir.
        tar_cmd = (
            f"gh api repos/{owner_repo}/tarball/{out['head_sha']} 2>/dev/null "
            f"| tar -xz -C {scan_dir} --strip-components=1"
        )
        rc, out_tar, err_tar = _run(tar_cmd, shell=True, timeout=180)
        if rc == 0 and any(scan_dir.iterdir()):
            out["tarball_extracted"] = True
            # Count files before strip
            file_count = sum(1 for _ in scan_dir.rglob("*") if _.is_file())
            out["tarball_file_count"] = file_count
            # Strip symlinks (pf5)
            symlink_count = 0
            for p in scan_dir.rglob("*"):
                if p.is_symlink():
                    p.unlink()
                    symlink_count += 1
            out["symlinks_stripped"] = symlink_count
        else:
            out["tarball_error"] = (err_tar or out_tar)[:200]
            scan_dir = None

    # pf6: rate limit
    rc, data = _gh_api("rate_limit", jq=".resources.core")
    out["api_rate_limit"] = data if rc == 0 else {"error": "query failed"}

    return out, scan_dir


# ---------------------------------------------------------------------------
# Step 1: repo basics + maintainer background
# ---------------------------------------------------------------------------


def step_1_repo_metadata(owner_repo: str) -> dict:
    rc, data = _gh_api(f"repos/{owner_repo}")
    if rc != 0:
        return {"$comment": f"repo_metadata fetch failed: {data}"}
    return {
        "name": data.get("name"),
        "description": data.get("description"),
        "created_at": data.get("created_at"),
        "pushed_at": data.get("pushed_at"),
        "stargazer_count": data.get("stargazers_count"),
        "fork_count": data.get("forks_count"),
        "archived": data.get("archived"),
        "fork": data.get("fork"),
        "has_issues_enabled": data.get("has_issues"),
        "primary_language": data.get("language"),
        "topics": data.get("topics") or [],
        "license_spdx": (data.get("license") or {}).get("spdx_id"),
        "default_branch": data.get("default_branch"),
        "open_issues_count": data.get("open_issues_count"),
        "size_kb": data.get("size"),
    }


def step_1_contributors(owner_repo: str, top_n: int = 6) -> dict:
    rc, data = _gh_api(
        f"repos/{owner_repo}/contributors?per_page=30",
        jq=f"[.[] | {{login, contributions}}]",
    )
    if rc != 0 or not isinstance(data, list):
        return {"top_contributors": [], "total_contributor_count": None,
                "$comment": "contributors fetch failed"}
    # Also get total count if paginate
    rc_all, all_data = _gh_api(
        f"repos/{owner_repo}/contributors?per_page=100&anon=true",
        jq="length",
    )
    total = all_data if (rc_all == 0 and isinstance(all_data, int)) else None
    return {
        "top_contributors": data[:top_n],
        "total_contributor_count": total,
    }


def step_1_maintainer_accounts(owner_repo: str, contributors: list) -> dict:
    """Fetch user metadata for owner + top contributors."""
    owner = owner_repo.split("/")[0]
    accounts = []
    rc, owner_data = _gh_api(
        f"users/{owner}",
        jq="{login, type, created_at, public_repos, followers, company, bio}",
    )
    if rc == 0 and isinstance(owner_data, dict):
        owner_data["role"] = "owner"
        accounts.append(owner_data)
    for c in (contributors or [])[:5]:
        login = c.get("login")
        if not login or login == owner:
            continue
        rc, u = _gh_api(
            f"users/{login}",
            jq="{login, type, created_at, public_repos, followers, company, bio}",
        )
        if rc == 0 and isinstance(u, dict):
            u["role"] = "contributor"
            u["contributions"] = c.get("contributions")
            accounts.append(u)
    return {"accounts": accounts}


def step_1_ossf_scorecard(owner_repo: str) -> dict:
    url = f"https://api.securityscorecards.dev/projects/github.com/{owner_repo}"
    rc, data = _curl_json(url, timeout=15)
    if rc != 0:
        # Distinguish 404 (not indexed) from other errors
        err_str = str(data.get("error", "")).lower() if isinstance(data, dict) else ""
        if "404" in err_str or "not found" in err_str:
            return {"queried": True, "indexed": False, "http_status": 404,
                    "overall_score": None, "checks": [], "raw_response": None}
        return {"queried": False, "indexed": None, "http_status": None,
                "overall_score": None, "checks": [],
                "raw_response": {"error": data.get("error") if isinstance(data, dict) else str(data)}}
    if isinstance(data, dict):
        return {
            "queried": True, "indexed": True, "http_status": 200,
            "overall_score": data.get("score"),
            "checks": [{"name": c.get("name"), "score": c.get("score")}
                       for c in data.get("checks", [])],
            "raw_response": {"date": data.get("date"),
                             "commit": (data.get("repo") or {}).get("commit")},
        }
    return {"queried": True, "indexed": False, "http_status": None,
            "overall_score": None, "checks": [],
            "raw_response": {"error": "unexpected response shape"}}


def step_1_community_profile(owner_repo: str) -> dict:
    rc, data = _gh_api(f"repos/{owner_repo}/community/profile")
    if rc != 0:
        return {"$comment": "community/profile fetch failed",
                "health_percentage": None,
                "has_code_of_conduct": None,
                "has_contributing": None,
                "has_security_policy": None,
                "license_spdx": None}
    files = data.get("files") or {}
    # community/profile has API quirks — can miss SECURITY.md at root even when
    # present (observed on microsoft/markitdown). Fall back to direct contents
    # check for all three policy files. This is a V2.4 prompt silent gap.
    has_security_policy = bool(files.get("security_policy"))
    if not has_security_policy:
        for path in ["SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md"]:
            rc2, _ = _gh_api(f"repos/{owner_repo}/contents/{path}")
            if rc2 == 0:
                has_security_policy = True
                break
    has_contributing = bool(files.get("contributing"))
    if not has_contributing:
        for path in ["CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"]:
            rc2, _ = _gh_api(f"repos/{owner_repo}/contents/{path}")
            if rc2 == 0:
                has_contributing = True
                break
    has_code_of_conduct = bool(files.get("code_of_conduct"))
    if not has_code_of_conduct:
        for path in ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"]:
            rc2, _ = _gh_api(f"repos/{owner_repo}/contents/{path}")
            if rc2 == 0:
                has_code_of_conduct = True
                break
    return {
        "health_percentage": data.get("health_percentage"),
        "has_code_of_conduct": has_code_of_conduct,
        "has_contributing": has_contributing,
        "has_security_policy": has_security_policy,
        "license_spdx": (files.get("license") or {}).get("spdx_id")
        if isinstance(files.get("license"), dict) else None,
    }


def step_1_branch_protection(owner_repo: str, default_branch: str) -> dict:
    result: dict[str, Any] = {}
    # 1f: classic
    rc, data = _gh_api(f"repos/{owner_repo}/branches/{default_branch}/protection")
    if rc != 0 and isinstance(data, dict) and "404" in str(data.get("error", "")):
        result["classic"] = {"status": 404}
    elif rc != 0:
        result["classic"] = {"status": "error", "error": str(data)[:200]}
    else:
        result["classic"] = {"status": 200, "body": data}
    # 1g: rulesets
    rc, data = _gh_api(f"repos/{owner_repo}/rulesets")
    if rc == 0 and isinstance(data, list):
        result["rulesets"] = {"entries": data, "count": len(data)}
    else:
        result["rulesets"] = {"entries": [], "count": 0}
    # 1h: rules on default branch
    rc, data = _gh_api(f"repos/{owner_repo}/rules/branches/{default_branch}")
    if rc == 0 and isinstance(data, list):
        result["rules_on_default"] = {"entries": data, "count": len(data)}
    else:
        result["rules_on_default"] = {"entries": [], "count": 0}
    # 1j: owner type
    rc, owner_type = _gh_api(f"repos/{owner_repo}", jq=".owner.type")
    if rc == 0:
        result["owner_type"] = owner_type
    else:
        result["owner_type"] = "unknown"
    # 1i: org rulesets (if owner is org)
    if result["owner_type"] == "Organization":
        owner = owner_repo.split("/")[0]
        rc, data = _gh_api(f"orgs/{owner}/rulesets")
        if rc == 0 and isinstance(data, list):
            result["org_rulesets"] = {"status": 200, "entries": data}
        elif rc != 0 and isinstance(data, dict) and "403" in str(data.get("error", "")):
            result["org_rulesets"] = {"status": 403, "entries": [],
                                      "note": "admin:org scope required"}
        else:
            result["org_rulesets"] = {"status": "error", "entries": []}
    else:
        result["org_rulesets"] = {"status": "n/a", "entries": [],
                                  "note": "owner is not an Organization"}
    return result


def step_1_codeowners(owner_repo: str) -> dict:
    locations = ["CODEOWNERS", ".github/CODEOWNERS",
                 "docs/CODEOWNERS", ".gitlab/CODEOWNERS"]
    for path in locations:
        rc, data = _gh_api(f"repos/{owner_repo}/contents/{path}")
        if rc == 0 and isinstance(data, dict) and data.get("content"):
            content = _b64_decode_contents(data)
            return {
                "found": True,
                "path": path,
                "content": content,
                "locations_checked": locations,
            }
    return {
        "found": False,
        "path": None,
        "content": None,
        "locations_checked": locations,
    }


def step_1_releases(owner_repo: str) -> dict:
    rc, data = _gh_api(f"repos/{owner_repo}/releases?per_page=100", paginate=False)
    if rc != 0 or not isinstance(data, list):
        return {"entries": [], "total_count": 0,
                "$comment": "releases fetch failed"}
    entries = [
        {"tag_name": r.get("tag_name"),
         "published_at": r.get("published_at"),
         "prerelease": r.get("prerelease"),
         "draft": r.get("draft"),
         "author": (r.get("author") or {}).get("login")}
        for r in data
    ]
    return {"entries": entries, "total_count": len(entries)}


def step_1_security_advisories(owner_repo: str) -> dict:
    rc, data = _gh_api(f"repos/{owner_repo}/security-advisories")
    if rc != 0 or not isinstance(data, list):
        return {"count": 0, "entries": []}
    return {
        "count": len(data),
        "entries": [
            {"ghsa_id": a.get("ghsa_id"),
             "severity": a.get("severity"),
             "cve_id": a.get("cve_id"),
             "published_at": a.get("published_at"),
             "summary": a.get("summary")}
            for a in data
        ],
    }


# ---------------------------------------------------------------------------
# Step 2: CI workflows
# ---------------------------------------------------------------------------


def step_2_workflows(owner_repo: str) -> tuple[dict, dict]:
    """Returns (workflows_field, workflow_contents_field)."""
    rc, data = _gh_api(f"repos/{owner_repo}/actions/workflows")
    wf_list = []
    if rc == 0 and isinstance(data, dict):
        wf_list = [
            {"name": w.get("name"), "path": w.get("path"),
             "state": w.get("state")}
            for w in data.get("workflows", [])
        ]

    contents_entries = []
    pull_request_target_count = 0

    # Also try contents listing for non-actions-registered workflows
    rc2, wf_contents = _gh_api(f"repos/{owner_repo}/contents/.github/workflows")
    paths: list[str] = []
    if rc2 == 0 and isinstance(wf_contents, list):
        paths = [f".github/workflows/{item.get('name')}" for item in wf_contents
                 if item.get("type") == "file"]
    # Union with wf_list paths
    paths = list({w["path"] for w in wf_list} | set(paths))

    sha_re = re.compile(r"uses:\s*\S+@[a-f0-9]{40}")
    tag_re = re.compile(r"uses:\s*\S+@v?\d+(?:\.\d+)*(?:-\S+)?\s*$", re.M)
    perms_re = re.compile(r"^permissions:", re.M)
    prt_re = re.compile(r"pull_request_target")

    for path in paths:
        rc, contents = _gh_api(f"repos/{owner_repo}/contents/{path}")
        if rc != 0 or not isinstance(contents, dict):
            continue
        text = _b64_decode_contents(contents) or ""
        entry = {
            "path": path,
            "content_lines": len(text.splitlines()),
            "sha_pinned_actions_count": len(sha_re.findall(text)),
            "tag_pinned_actions_count": len(tag_re.findall(text)),
            "has_pull_request_target": bool(prt_re.search(text)),
            "permissions_block_present": bool(perms_re.search(text)),
        }
        if entry["has_pull_request_target"]:
            pull_request_target_count += 1
        contents_entries.append(entry)

    workflows_field = {
        "entries": wf_list,
        "count": len(wf_list) if wf_list else len(paths),
        "pull_request_target_count": pull_request_target_count,
    }
    return workflows_field, {"entries": contents_entries}


# ---------------------------------------------------------------------------
# Step 2.5: agent-rule files
# ---------------------------------------------------------------------------


AGENT_RULE_PATTERNS = [
    # filename-based
    (r"(^|/)CLAUDE\.md$",       "claude"),
    (r"(^|/)AGENTS\.md$",       "agents"),
    (r"(^|/)GEMINI\.md$",       "gemini"),
    (r"(^|/)\.cursorrules$",    "cursor-legacy"),
    (r"(^|/)\.mcp\.json$",      "mcp"),
    (r"(^|/)\.cursor/rules/.*\.(md|mdc)$",  "cursor"),
    (r"(^|/)\.windsurf/rules/.*\.md$",      "windsurf"),
    (r"(^|/)\.clinerules/.*\.md$",          "cline"),
    (r"(^|/)\.github/copilot-instructions(\.md)?$", "copilot"),
]


def step_2_5_agent_rule_files(scan_dir: Path | None,
                              owner_repo: str) -> tuple[dict, dict]:
    """Returns (code_patterns.agent_rule_files, prompt_injection_scan)."""
    rule_files: list[dict] = []
    if scan_dir and scan_dir.exists():
        for p in scan_dir.rglob("*"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(scan_dir))
            if any(p.match("**/node_modules/**") for _ in ["x"]) or "/node_modules/" in rel:
                continue
            for pat, kind in AGENT_RULE_PATTERNS:
                if re.search(pat, rel):
                    try:
                        content = p.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        content = ""
                    rule_files.append({
                        "path": rel,
                        "kind": kind,
                        "line_count": len(content.splitlines()),
                        "ci_amplified": False,  # marked in step_2_5_ci_amplified
                    })
                    break
    else:
        # Fallback: fetch git tree via API
        rc, tree = _gh_api(f"repos/{owner_repo}/git/trees/HEAD?recursive=1")
        if rc == 0 and isinstance(tree, dict):
            for item in tree.get("tree", []):
                path = item.get("path", "")
                for pat, kind in AGENT_RULE_PATTERNS:
                    if re.search(pat, path):
                        rule_files.append({
                            "path": path, "kind": kind,
                            "line_count": None, "ci_amplified": False,
                            "source": "api-tree-fallback",
                        })
                        break

    # Mark CI-amplified
    if scan_dir and scan_dir.exists():
        wf_dir = scan_dir / ".github" / "workflows"
        if wf_dir.exists():
            amplifier_regex = re.compile(
                r"\.cursor/rules/|\.windsurf/rules/|\.clinerules/|copilot-instructions"
            )
            for yml in wf_dir.glob("*.yml"):
                try:
                    text = yml.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                if amplifier_regex.search(text):
                    # Mark all currently found rule files as ci_amplified
                    # (conservative — any amplifier workflow implies at least one CI-copied file)
                    for rf in rule_files:
                        rf["ci_amplified"] = True

    # Prompt-injection text grep restricted to the rule files
    injection_re = re.compile(
        r"ignore (all )?(previous|prior) instructions|disregard.*instructions|"
        r"you are now|pretend you are|system prompt|override.*safety|jailbreak",
        re.IGNORECASE,
    )
    injection_signals: list[dict] = []
    scanned_files: list[str] = []
    if scan_dir and scan_dir.exists():
        for rf in rule_files:
            p = scan_dir / rf["path"]
            if not p.is_file():
                continue
            scanned_files.append(rf["path"])
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if injection_re.search(line):
                    injection_signals.append({
                        "file": rf["path"],
                        "line": lineno,
                        "match_snippet": line[:160],
                    })

    return (
        {"agent_rule_files": rule_files},
        {"scanned_files": scanned_files,
         "injection_signals": injection_signals,
         "signal_count": len(injection_signals),
         "scan_method": "tarball" if (scan_dir and scan_dir.exists()) else "api-tree"},
    )


# ---------------------------------------------------------------------------
# Step 3: dependencies
# ---------------------------------------------------------------------------


MANIFEST_NAMES = {
    "package.json": "npm",
    "package-lock.json": "npm",
    "yarn.lock": "npm",
    "pnpm-lock.yaml": "npm",
    "requirements.txt": "PyPI",
    "requirements-dev.txt": "PyPI",
    "pyproject.toml": "PyPI",
    "Pipfile": "PyPI",
    "Pipfile.lock": "PyPI",
    "Gemfile": "RubyGems",
    "Gemfile.lock": "RubyGems",
    "go.mod": "Go",
    "go.sum": "Go",
    "Cargo.toml": "crates.io",
    "Cargo.lock": "crates.io",
    "pom.xml": "Maven",
    "build.gradle": "Maven",
    "composer.json": "Packagist",
    "composer.lock": "Packagist",
}


def _parse_pyproject_toml(text: str) -> tuple[list[dict], list[dict]]:
    """Return (runtime_deps, dev_deps) from a pyproject.toml string."""
    runtime, dev = [], []
    # Simple regex — tolerates modest TOML without a TOML parser. Handles
    # [project] dependencies = [...] + [project.optional-dependencies] blocks.
    in_proj = False
    in_deps = False
    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("[project]"):
            in_proj = True
            in_deps = False
            continue
        if line.startswith("[") and not line.startswith("[project"):
            in_proj = False
            in_deps = False
            continue
        if in_proj and re.match(r"^\s*dependencies\s*=\s*\[", line):
            in_deps = True
            continue
        if in_deps:
            if "]" in line:
                in_deps = False
                continue
            m = re.match(r'\s*["\']([^"\',\[\]]+?)["\'],?\s*$', line)
            if m:
                spec = m.group(1).strip()
                name = re.split(r"[<>=!~\[]", spec)[0].strip()
                pin = "unpinned" if spec == name else spec[len(name):].strip()
                runtime.append({"name": name, "ecosystem": "PyPI", "pinning": pin or "unpinned"})
    return runtime, dev


def _parse_package_json(text: str) -> tuple[list[dict], list[dict]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [], []
    def _to_list(obj: dict | None) -> list[dict]:
        if not isinstance(obj, dict):
            return []
        return [{"name": k, "ecosystem": "npm",
                 "pinning": v if re.match(r"^(\^|~|\d)", v) else "range/other"}
                for k, v in obj.items()]
    return _to_list(data.get("dependencies")), _to_list(data.get("devDependencies"))


def _parse_requirements_txt(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[<>=!~\[]", line)[0].strip()
        if name:
            pin = "unpinned" if line == name else line[len(name):].strip()
            out.append({"name": name, "ecosystem": "PyPI", "pinning": pin or "unpinned"})
    return out


def step_3_dependencies(owner_repo: str, scan_dir: Path | None) -> tuple[dict, dict]:
    """Returns (dependencies_field, dependabot_alerts_status)."""
    manifest_files: list[dict] = []
    runtime_all: list[dict] = []
    dev_all: list[dict] = []

    # 3a: enumerate manifests
    if scan_dir and scan_dir.exists():
        for p in scan_dir.rglob("*"):
            if not p.is_file():
                continue
            if "/node_modules/" in str(p):
                continue
            if p.name in MANIFEST_NAMES:
                rel = str(p.relative_to(scan_dir))
                manifest_files.append({
                    "path": rel, "ecosystem": MANIFEST_NAMES[p.name]
                })
    else:
        # Fallback: use git tree
        rc, tree = _gh_api(f"repos/{owner_repo}/git/trees/HEAD?recursive=1")
        if rc == 0 and isinstance(tree, dict):
            for item in tree.get("tree", []):
                name = Path(item.get("path", "")).name
                if name in MANIFEST_NAMES and "node_modules/" not in item.get("path", ""):
                    manifest_files.append({
                        "path": item["path"], "ecosystem": MANIFEST_NAMES[name]
                    })

    # 3b: parse each manifest
    for mf in manifest_files:
        if scan_dir and scan_dir.exists():
            p = scan_dir / mf["path"]
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
        else:
            rc, contents = _gh_api(f"repos/{owner_repo}/contents/{mf['path']}")
            if rc != 0 or not isinstance(contents, dict):
                continue
            text = _b64_decode_contents(contents) or ""

        if mf["path"].endswith("pyproject.toml"):
            r, d = _parse_pyproject_toml(text)
        elif mf["path"].endswith("package.json"):
            r, d = _parse_package_json(text)
        elif mf["path"].endswith(("requirements.txt", "requirements-dev.txt")):
            r = _parse_requirements_txt(text)
            d = []
        else:
            r, d = [], []
        runtime_all.extend(r)
        dev_all.extend(d)

    # 3c: Dependabot alerts
    rc, data = _gh_api(f"repos/{owner_repo}/dependabot/alerts", paginate=True)
    if rc == 0 and isinstance(data, list):
        dependabot = {"status": 200, "alerts_count": len(data),
                      "alerts": [{"summary": (a.get("security_advisory") or {}).get("summary"),
                                  "severity": (a.get("security_advisory") or {}).get("severity"),
                                  "state": a.get("state")}
                                 for a in data[:20]]}
    elif isinstance(data, dict):
        err = str(data.get("error", ""))
        if "403" in err:
            dependabot = {"status": 403, "alerts_count": None,
                          "note": "admin scope required; falling back to osv.dev"}
        elif "404" in err:
            dependabot = {"status": 404, "alerts_count": None,
                          "note": "Dependabot not enabled on this repo"}
        else:
            dependabot = {"status": "error", "note": err[:200]}
    else:
        dependabot = {"status": "unknown"}

    # 3d: osv.dev fallback — only run if Dependabot non-OK
    osv_lookups: list[dict] = []
    if dependabot.get("status") != 200:
        # Limit to top 15 direct deps per ecosystem to bound runtime
        seen = set()
        for dep in runtime_all[:30]:
            key = (dep["name"], dep["ecosystem"])
            if key in seen:
                continue
            seen.add(key)
            osv_pkg = {"name": dep["name"], "ecosystem": dep["ecosystem"]}
            payload = json.dumps({"package": osv_pkg})
            rc, out, err = _run(
                ["curl", "-fsSL", "--max-time", "10",
                 "https://api.osv.dev/v1/query",
                 "-d", payload],
                timeout=12,
            )
            if rc != 0:
                osv_lookups.append({**osv_pkg, "vulns_count": None,
                                    "error": (err or "request failed")[:120]})
                continue
            try:
                resp = json.loads(out)
                vulns = resp.get("vulns", []) or []
                osv_lookups.append({
                    **osv_pkg,
                    "vulns_count": len(vulns),
                    "vulns_summary": [v.get("id") for v in vulns[:5]],
                })
            except json.JSONDecodeError:
                osv_lookups.append({**osv_pkg, "vulns_count": None,
                                    "error": "json decode"})

    # 3e: dependabot.yml config
    rc, contents = _gh_api(f"repos/{owner_repo}/contents/.github/dependabot.yml")
    dependabot_config_present = rc == 0 and isinstance(contents, dict) and contents.get("content")
    dependabot_config_text = _b64_decode_contents(contents) if dependabot_config_present else None
    ecosystems_tracked = []
    if dependabot_config_text:
        for m in re.finditer(r'package-ecosystem:\s*"?([a-z-]+)"?', dependabot_config_text):
            ecosystems_tracked.append(m.group(1))

    deps_field = {
        "manifest_files": manifest_files,
        "runtime": runtime_all,
        "runtime_count": len(runtime_all),
        "dev": dev_all,
        "dev_count": len(dev_all),
        "dependabot_alerts": dependabot,
        "osv_lookups": osv_lookups,
        "dependabot_config": {
            "present": bool(dependabot_config_present),
            "ecosystems_tracked": ecosystems_tracked,
            "raw_snippet": dependabot_config_text[:500] if dependabot_config_text else None,
        },
    }
    return deps_field, dependabot


# ---------------------------------------------------------------------------
# Step 4: PR history + review rates
# ---------------------------------------------------------------------------


def step_4_pr_review(owner_repo: str, limit: int = 300) -> tuple[dict, dict, dict]:
    """Returns (pr_review, open_prs, closed_not_merged_prs)."""
    # 4a: total merged lifetime via search
    rc, total = _gh_api(
        f"search/issues?q=repo:{owner_repo}+is:pr+is:merged&per_page=1",
        jq=".total_count",
    )
    total_lifetime = total if (rc == 0 and isinstance(total, int)) else None

    # 4b: fetch merged PRs with review decision + reviews
    rc, out, err = _run(
        ["gh", "pr", "list", "-R", owner_repo, "--state", "merged",
         "--limit", str(limit),
         "--json", "number,title,reviewDecision,reviews,author,mergeCommit,"
                   "mergedAt,labels,mergedBy"],
        timeout=90,
    )
    merged_prs: list[dict] = []
    if rc == 0:
        try:
            merged_prs = json.loads(out)
        except json.JSONDecodeError:
            merged_prs = []

    formal = 0
    any_rev = 0
    self_merge = 0
    prs_summary: list[dict] = []
    for pr in merged_prs:
        decision = pr.get("reviewDecision") or ""
        reviews = pr.get("reviews") or []
        author = (pr.get("author") or {}).get("login")
        merger = (pr.get("mergedBy") or {}).get("login")
        is_formal = bool(decision) and decision != ""
        is_any = bool(reviews) and len(reviews) > 0
        is_self = bool(author and merger and author == merger)
        if is_formal:
            formal += 1
        if is_any:
            any_rev += 1
        if is_self:
            self_merge += 1
        prs_summary.append({
            "number": pr.get("number"),
            "title": pr.get("title", "")[:160],
            "review_decision": decision,
            "any_review_count": len(reviews),
            "self_merge": is_self,
            "merged_at": pr.get("mergedAt"),
            "labels": [(l.get("name") if isinstance(l, dict) else l)
                       for l in (pr.get("labels") or [])],
        })

    total = len(merged_prs) if merged_prs else 0
    pr_review = {
        "total_closed_prs": total,
        "sample_size": total,
        "total_merged_lifetime": total_lifetime,
        "prs": prs_summary[:50],
        "formal_review_rate": round(100 * formal / total, 1) if total else None,
        "any_review_rate": round(100 * any_rev / total, 1) if total else None,
        "self_merge_count": self_merge,
    }

    # 4f: open PRs
    rc, out, err = _run(
        ["gh", "pr", "list", "-R", owner_repo, "--state", "open",
         "--limit", "300", "--json", "number,title,author,createdAt"],
        timeout=45,
    )
    if rc == 0:
        try:
            open_list = json.loads(out)
        except json.JSONDecodeError:
            open_list = []
    else:
        open_list = []
    open_prs = {"entries": [{"number": p.get("number"),
                             "title": p.get("title", "")[:160],
                             "author": (p.get("author") or {}).get("login"),
                             "created_at": p.get("createdAt")}
                            for p in open_list],
                "count": len(open_list)}

    # 4g: closed-not-merged PRs
    rc, out, err = _run(
        ["gh", "pr", "list", "-R", owner_repo, "--state", "closed",
         "--search", "is:unmerged", "--limit", "100",
         "--json", "number,title,closedAt"],
        timeout=45,
    )
    if rc == 0:
        try:
            closed_list = json.loads(out)
        except json.JSONDecodeError:
            closed_list = []
    else:
        closed_list = []
    closed_prs = {
        "entries": [{"number": p.get("number"),
                     "title": p.get("title", "")[:160],
                     "closed_at": p.get("closedAt")} for p in closed_list],
        "count": len(closed_list),
    }

    return pr_review, open_prs, closed_prs


# ---------------------------------------------------------------------------
# Step 5: security-flagged PRs (derived from Step 4 data + search)
# ---------------------------------------------------------------------------


def step_5_flag_security_prs(owner_repo: str, pr_review: dict) -> dict:
    rc, data = _gh_api(
        f"search/issues?q=repo:{owner_repo}+is:pr+in:title+security+OR+CVE+OR+"
        f"vulnerability+OR+exploit+OR+RCE+OR+auth",
        jq=".items | map(.number)",
    )
    sec_numbers = set()
    if rc == 0 and isinstance(data, list):
        sec_numbers = set(data)
    # Flag the prs_summary entries
    for pr in pr_review.get("prs", []):
        pr["security_flagged"] = pr.get("number") in sec_numbers
    pr_review["security_flagged_count"] = sum(
        1 for pr in pr_review.get("prs", []) if pr.get("security_flagged")
    )
    pr_review["security_flagged_numbers"] = sorted(sec_numbers)
    return pr_review


# ---------------------------------------------------------------------------
# Step 6: issues
# ---------------------------------------------------------------------------


def step_6_issues(owner_repo: str) -> dict:
    rc, data = _gh_api(
        f"search/issues?q=repo:{owner_repo}+is:issue+is:open+in:title+"
        f"security+OR+CVE+OR+vulnerability+OR+exploit+OR+DoS",
        jq=".items | map({number, title, state, created_at, "
           "labels: [.labels[].name], "
           "author: .user.login, "
           "body_snippet: (.body[0:300] // \"\")})",
    )
    open_sec = data if (rc == 0 and isinstance(data, list)) else []
    # Open issue count (full, naive)
    rc, total = _gh_api(
        f"search/issues?q=repo:{owner_repo}+is:issue+is:open&per_page=1",
        jq=".total_count",
    )
    open_total = total if (rc == 0 and isinstance(total, int)) else None
    # Closed security issues (last 10)
    rc, data = _gh_api(
        f"search/issues?q=repo:{owner_repo}+is:issue+is:closed+security&sort=updated&per_page=10",
        jq=".items | map({number, title, closed_at, author: .user.login})",
    )
    closed_sec = data if (rc == 0 and isinstance(data, list)) else []
    return {
        "open_security_issues": open_sec,
        "open_issues_count": open_total,
        "closed_issues": closed_sec,
        "closed_issues_count": len(closed_sec),
        "recent_commits": [],  # filled by step_7
    }


# ---------------------------------------------------------------------------
# Step 7: recent commits
# ---------------------------------------------------------------------------


SECURITY_KEYWORDS = re.compile(
    r"\b(security|fix|CVE|vuln|auth|injection|XXE|SSRF|RCE|DoS|XSS|leak|"
    r"symlink|privilege|sanitiz|escape|redos)\b",
    re.IGNORECASE,
)


def step_7_recent_commits(owner_repo: str) -> list[dict]:
    since = (dt.datetime.now(dt.timezone.utc)
             - dt.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rc, data = _gh_api(
        f"repos/{owner_repo}/commits?per_page=100&since={since}",
        jq="[.[] | {sha: .sha[0:7], author: (.author.login // .commit.author.name), "
           "date: .commit.author.date, message_first_line: (.commit.message | split(\"\\n\")[0])}]",
    )
    commits = data if (rc == 0 and isinstance(data, list)) else []
    for c in commits:
        c["security_keyword_match"] = bool(
            SECURITY_KEYWORDS.search(c.get("message_first_line", "") or "")
        )
    return commits


# ---------------------------------------------------------------------------
# Step 7.5: README install-paste scan
# ---------------------------------------------------------------------------


README_PASTE_RE = re.compile(
    r"paste (this|the (following|snippet|code|block))|"
    r"copy (this|these) (into|to) (your|the).*system prompt|"
    r"add (this|these) to your (rules|agent)|"
    r"include (this|these) in (your|the) (system prompt|rules)|"
    r"place this in|put this in.*(rules|agent|system)",
    re.IGNORECASE,
)


def step_7_5_readme_paste(owner_repo: str, scan_dir: Path | None) -> dict:
    entries: list[dict] = []
    scanned_any = False
    if scan_dir and scan_dir.exists():
        for p in [scan_dir / "README.md", scan_dir / "readme.md",
                  scan_dir / "README.rst", scan_dir / "docs" / "README.md"]:
            if p.is_file():
                scanned_any = True
                try:
                    text = p.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    if README_PASTE_RE.search(line):
                        entries.append({
                            "file": str(p.relative_to(scan_dir)),
                            "line": lineno,
                            "snippet": line[:200],
                        })
    if not scanned_any:
        # Fallback: fetch README via API
        rc, contents = _gh_api(f"repos/{owner_repo}/contents/README.md")
        if rc == 0 and isinstance(contents, dict):
            text = _b64_decode_contents(contents) or ""
            scanned_any = True
            for lineno, line in enumerate(text.splitlines(), 1):
                if README_PASTE_RE.search(line):
                    entries.append({"file": "README.md", "line": lineno,
                                    "snippet": line[:200], "source": "api-fallback"})
    return {
        "scanned": scanned_any,
        "entries": entries,
        "entries_count": len(entries),
    }


# ---------------------------------------------------------------------------
# Step 8: installed-artifact verification
# ---------------------------------------------------------------------------


def _verify_pypi(pkg: str) -> dict:
    rc, data = _curl_json(f"https://pypi.org/pypi/{pkg}/json", timeout=10)
    if rc != 0 or not isinstance(data, dict):
        return {"method": "pypi-registry-presence", "result": "unavailable",
                "note": f"PyPI lookup failed: {rc}"}
    info = data.get("info") or {}
    return {
        "method": "pypi-registry-presence",
        "result": "verified" if info.get("name") else "not_verified",
        "latest_version": info.get("version"),
        "upload_time": ((data.get("releases") or {})
                        .get(info.get("version") or "", [{}])[0]).get("upload_time"),
    }


def _verify_npm(pkg: str) -> dict:
    rc, data = _curl_json(f"https://registry.npmjs.org/{pkg}", timeout=10)
    if rc != 0 or not isinstance(data, dict):
        return {"method": "npm-registry-presence", "result": "unavailable"}
    return {
        "method": "npm-registry-presence",
        "result": "verified" if data.get("name") else "not_verified",
        "latest_version": (data.get("dist-tags") or {}).get("latest"),
    }


def _verify_crates(pkg: str) -> dict:
    rc, data = _curl_json(f"https://crates.io/api/v1/crates/{pkg}", timeout=10)
    if rc != 0 or not isinstance(data, dict):
        return {"method": "crates-io-presence", "result": "unavailable"}
    return {
        "method": "crates-io-presence",
        "result": "verified" if (data.get("crate") or {}).get("name") else "not_verified",
        "latest_version": (data.get("crate") or {}).get("newest_version"),
    }


def _verify_rubygems(pkg: str) -> dict:
    rc, data = _curl_json(f"https://rubygems.org/api/v1/gems/{pkg}.json", timeout=10)
    if rc != 0 or not isinstance(data, dict):
        return {"method": "rubygems-presence", "result": "unavailable"}
    return {"method": "rubygems-presence",
            "result": "verified" if data.get("name") else "not_verified",
            "latest_version": data.get("version")}


VERIFIERS = {
    "PyPI": _verify_pypi,
    "npm": _verify_npm,
    "crates.io": _verify_crates,
    "RubyGems": _verify_rubygems,
}


def step_8_distribution(owner_repo: str, scan_dir: Path | None,
                        manifests: list[dict],
                        readme_text: str) -> tuple[dict, dict, dict]:
    """Derive distribution_channels + artifact_verification + install_script_analysis."""
    channels: list[dict] = []
    verifications: list[dict] = []

    # From manifests: each top-level manifest suggests a registry-based channel
    seen_channels: set[tuple[str, str]] = set()
    for mf in manifests:
        eco = mf["ecosystem"]
        path = mf["path"]
        if eco in VERIFIERS:
            # Try to extract package name from manifest
            pkg_name = None
            full = scan_dir / path if (scan_dir and scan_dir.exists()) else None
            text: str | None = None
            if full and full.is_file():
                text = full.read_text(encoding="utf-8", errors="replace")
            if text is None:
                rc, contents = _gh_api(f"repos/{owner_repo}/contents/{path}")
                if rc == 0 and isinstance(contents, dict):
                    text = _b64_decode_contents(contents)
            if text:
                if path.endswith("pyproject.toml"):
                    m = re.search(r'^\s*name\s*=\s*["\']([^"\']+)["\']',
                                  text, re.M)
                    if m:
                        pkg_name = m.group(1)
                elif path.endswith("package.json"):
                    try:
                        pkg_name = json.loads(text).get("name")
                    except json.JSONDecodeError:
                        pass
                elif path.endswith("Cargo.toml"):
                    m = re.search(r'^\s*name\s*=\s*["\']([^"\']+)["\']',
                                  text, re.M)
                    if m:
                        pkg_name = m.group(1)

            if pkg_name and (pkg_name, eco) not in seen_channels:
                seen_channels.add((pkg_name, eco))
                eco_map = {"PyPI": ("pip install", "pypi"),
                           "npm": ("npm install", "npm"),
                           "crates.io": ("cargo install", "crates"),
                           "RubyGems": ("gem install", "rubygems")}
                cmd_prefix, channel_prefix = eco_map[eco]
                ch_name = f"{channel_prefix}-{pkg_name}"
                channels.append({
                    "name": ch_name,
                    "type": "package_manager",
                    "package": pkg_name,
                    "install_command": f"{cmd_prefix} {pkg_name}",
                    "pinned": False,
                    "install_path_verified": True,
                    "artifact_verified": False,
                    "ecosystem": eco,
                    "note": f"Registered in {path}",
                })
                # Verify
                ver = VERIFIERS[eco](pkg_name)
                verifications.append({"channel": ch_name, **ver})

    # Dockerfile detection
    dockerfile_present = False
    if scan_dir and scan_dir.exists():
        dockerfile_present = (scan_dir / "Dockerfile").is_file()
    else:
        rc, _ = _gh_api(f"repos/{owner_repo}/contents/Dockerfile")
        dockerfile_present = rc == 0
    if dockerfile_present:
        ch_name = "docker-local-build"
        channels.append({
            "name": ch_name,
            "type": "container",
            "package": f"{owner_repo} (Dockerfile in repo)",
            "install_command": "docker build",
            "pinned": False,
            "install_path_verified": False,
            "artifact_verified": False,
            "ecosystem": "Docker",
            "note": "No prebuilt image check attempted; user builds locally",
        })
        verifications.append({
            "channel": ch_name, "method": "dockerfile-in-repo",
            "result": "not_verified",
            "note": "Docker local-build path; no registry digest checked"
        })

    # Install scripts detection
    install_scripts: list[dict] = []
    curl_pattern = re.compile(
        r"curl|wget|Invoke-WebRequest|DownloadString|DownloadFile|"
        r"iwr\b|Invoke-RestMethod", re.IGNORECASE)
    pinning_pattern_sha = re.compile(r"@[a-f0-9]{7,40}")
    pinning_pattern_tag = re.compile(r"@v?\d+\.\d+(?:\.\d+)?")
    main_branch_pattern = re.compile(
        r"raw\.githubusercontent\.com/[^/]+/[^/]+/(main|master)\b", re.IGNORECASE)
    if scan_dir and scan_dir.exists():
        for name in ["install.sh", "install.ps1", "setup.sh", "setup.ps1"]:
            # Search a few typical locations
            for p in list(scan_dir.glob(name)) + list((scan_dir / "hooks").glob(name)) \
                     + list((scan_dir / "scripts").glob(name)):
                if not p.is_file():
                    continue
                try:
                    text = p.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                rel = str(p.relative_to(scan_dir))
                install_scripts.append({
                    "file": rel,
                    "network": bool(curl_pattern.search(text)),
                    "tracks_main_branch": bool(main_branch_pattern.search(text)),
                    "sha_pinned": bool(pinning_pattern_sha.search(text)),
                    "tag_pinned": bool(pinning_pattern_tag.search(text)),
                    "injection_channel": False,  # conservative; Phase 4 review if sh + curl-pipe
                    "line_count": len(text.splitlines()),
                })

    # README install-path snippets (grep for install commands)
    if readme_text:
        for m in re.finditer(
            r"\b(curl|wget|pip install|npm install|yarn add|gem install|"
            r"cargo install|go install|brew install|docker run|docker pull|"
            r"pipx install)\b[^\n]{0,120}", readme_text, re.IGNORECASE):
            install_scripts.append({
                "file": "README.md",
                "snippet": m.group(0)[:150],
                "network": True,
                "tracks_main_branch": bool(
                    main_branch_pattern.search(m.group(0))),
                "sha_pinned": bool(pinning_pattern_sha.search(m.group(0))),
                "tag_pinned": bool(pinning_pattern_tag.search(m.group(0))),
            })

    return (
        {"channels": channels},
        {"per_channel": verifications},
        {"scripts": install_scripts},
    )


# ---------------------------------------------------------------------------
# Step A-pre: gitleaks
# ---------------------------------------------------------------------------


def step_a_pre_gitleaks(scan_dir: Path | None) -> dict:
    if shutil.which("gitleaks") is None:
        return {"available": False, "ran": False,
                "findings_count": None,
                "findings": [],
                "note": "gitleaks not installed; install to cover secrets-in-history"}
    if not scan_dir or not scan_dir.exists():
        return {"available": True, "ran": False, "findings_count": None,
                "findings": [],
                "note": "tarball not extracted — gitleaks scan skipped"}
    rc, out, err = _run(
        ["gitleaks", "detect", "--source", str(scan_dir),
         "--redact", "--no-git", "--report-format", "json",
         "--report-path", "/dev/stdout"],
        timeout=120,
    )
    findings: list[dict] = []
    if rc in (0, 1):  # 0 = clean, 1 = findings
        try:
            # gitleaks may print banner to stderr; filter lines
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("[") or line.startswith("{"):
                    parsed = json.loads(line)
                    if isinstance(parsed, list):
                        findings.extend(parsed)
                    else:
                        findings.append(parsed)
        except json.JSONDecodeError:
            pass
    return {
        "available": True,
        "ran": True,
        "findings_count": len(findings),
        "findings": [{"rule_id": f.get("RuleID"),
                      "file": f.get("File"),
                      "line": f.get("StartLine"),
                      "redacted_match": (f.get("Secret") or "")[:32]}
                     for f in findings[:25]],
    }


# ---------------------------------------------------------------------------
# Step A: dangerous-pattern grep
# ---------------------------------------------------------------------------


STEP_A_PATTERNS = [
    ("exec", re.compile(r"\beval\s*\(|new\s+Function\s*\(|vm\.runIn|\bexec\s*\(|execSync|spawnSync\s*\(|child_process|subprocess\.(call|Popen|run)|os\.system|shell\s*=\s*True|Runtime\.getRuntime\(\)\.exec")),
    # V1.2.x (V13-1 owner directive 2026-04-20): widened per Kronos entry 17 Q4
    # override. Prior regex matched `pickle.loads` but not `pickle.load`
    # (singular) — missed the 95-day-old RCE at finetune/dataset.py:42.
    # Added: pickle.load/loads, marshal.load/loads, joblib.load, dill.load/loads.
    ("deserialization", re.compile(r"pickle\.loads?|yaml\.load\s*\(|unserialize\(|ObjectInputStream|deserialize|Marshal\.load|\bmarshal\.loads?|\bjoblib\.load|\bdill\.loads?")),
    ("network", re.compile(r"\bfetch\s*\(|XMLHttpRequest|axios\.|got\(|http\.(get|post|request)|requests\.(get|post|put|delete)|urllib\.request|net\.(connect|Socket)|http\.Client|WebSocket|url\.URL\(|RestTemplate")),
    ("secrets", re.compile(r"(api[_-]?key|secret|token|password|passwd|pwd|auth)\s*[:=]\s*[\"'][A-Za-z0-9_\-\.]{16,}", re.IGNORECASE)),
    ("vendor_keys", re.compile(r"sk-[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{36}|xox[abpr]-[A-Za-z0-9-]+|AIza[0-9A-Za-z_-]{35}|AKIA[0-9A-Z]{16}")),
    ("tls_cors", re.compile(r"Access-Control-Allow-Origin.*\*|rejectUnauthorized\s*:\s*false|verify\s*=\s*False|CURLOPT_SSL_VERIFYPEER.*false|InsecureSkipVerify\s*:\s*true|0\.0\.0\.0")),
    ("sql_injection", re.compile(r"query\s*\(\s*[\"'`].*\$\{|execute\s*\(\s*f[\"']|\.raw\(")),
    ("cmd_injection", re.compile(r"exec\(.*\$\{|system\(.*\$\{")),
    ("auth_bypass", re.compile(r"validate_exp\s*=\s*(False|false)|verify_signature\s*=\s*False|algorithm\s*:\s*[\"']none")),
    ("path_traversal", re.compile(r"readFileSync\s*\(\s*[^)]*\+|path\.join\(.*req\.|os\.path\.join\(.*request\.|filepath\.Join\(.*r\.URL")),
    ("archive_unsafe", re.compile(r"\bZipFile|extractAll\(|tar\.extract\(")),
    ("ssrf", re.compile(r"http\.get\(\s*(req|params|request|body)|urllib\.request\.urlopen\(\s*request|169\.254\.169\.254|metadata\.google\.internal|fd00:ec2")),
    ("xss", re.compile(r"innerHTML\s*=|dangerouslySetInnerHTML|document\.write|\.html\(.*\+|v-html=")),
    ("weak_crypto", re.compile(r"\bmd5\s*\(|hashlib\.md5|createHash\s*\(\s*[\"']md5|\bsha1\s*\(|hashlib\.sha1|\bDES\b|RC4|Math\.random\s*\(\s*\)\s*.*(token|secret|session)")),
    ("debug_flags", re.compile(r"DEBUG\s*=\s*(True|true)|debug:\s*true|NODE_ENV.*development|app\.debug\s*=\s*True|ignoreSSL|skipSSLVerification")),
]


def step_a_dangerous_patterns(scan_dir: Path | None) -> dict:
    """Grep dangerous patterns. Returns code_patterns.dangerous_primitives shape."""
    if not scan_dir or not scan_dir.exists():
        return {
            "scanned": False,
            "note": "tarball extraction unavailable; grep deferred",
            **{name: {"hit_count": 0, "files": []} for name, _ in STEP_A_PATTERNS},
        }
    results: dict[str, dict] = {}
    # Walk all source files (skip node_modules, .git, vendor, dist, build)
    SKIP_DIRS = {"node_modules", ".git", "vendor", "dist", "build", "__pycache__",
                 ".venv", "venv", ".tox", ".next", ".nuxt"}
    for name, pattern in STEP_A_PATTERNS:
        hits: list[dict] = []
        for p in scan_dir.rglob("*"):
            if not p.is_file():
                continue
            if any(skip in p.parts for skip in SKIP_DIRS):
                continue
            if p.suffix not in {".py", ".js", ".ts", ".tsx", ".jsx", ".mjs",
                                ".rb", ".go", ".rs", ".java", ".php", ".c",
                                ".cpp", ".sh", ".ps1", ".yml", ".yaml", ".toml",
                                ".json", ".env", ".md"}:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if pattern.search(text):
                # Count matches + capture first line
                first_match = None
                lines = text.splitlines()
                for lineno, line in enumerate(lines, 1):
                    if pattern.search(line):
                        first_match = {"line": lineno, "snippet": line[:120]}
                        break
                hits.append({
                    "file": str(p.relative_to(scan_dir)),
                    "first_match": first_match,
                })
        results[name] = {
            "hit_count": len(hits),
            "files": hits[:20],  # cap
        }
    return {"scanned": True, **results}


# ---------------------------------------------------------------------------
# Step C: executable file inventory + Windows patterns
# ---------------------------------------------------------------------------


EXECUTABLE_PATTERNS = [
    ("install.sh", "shell-installer", "bash"),
    ("install.ps1", "shell-installer", "powershell"),
    ("uninstall.sh", "shell-uninstaller", "bash"),
    ("uninstall.ps1", "shell-uninstaller", "powershell"),
    ("setup.py", "python-setup", "python"),
    ("Dockerfile", "container-build", "docker"),
    ("docker-entrypoint.sh", "container-entrypoint", "bash"),
    ("Makefile", "build-driver", "make"),
]


def step_c_executable_inventory(scan_dir: Path | None) -> tuple[dict, dict]:
    """Returns (executable_files_field, windows_patterns_field)."""
    files: list[dict] = []
    if not scan_dir or not scan_dir.exists():
        return {"executable_files": []}, {"hits": [], "hit_count": 0}

    # Explicit patterns
    for name, kind, runtime in EXECUTABLE_PATTERNS:
        for p in scan_dir.rglob(name):
            if not p.is_file():
                continue
            rel = str(p.relative_to(scan_dir))
            if "/node_modules/" in rel:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            # Compute simple SHA
            import hashlib
            sha = hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:12]
            files.append({
                "path": rel,
                "kind": kind,
                "runtime": runtime,
                "line_count": len(text.splitlines()),
                "file_sha": sha,
                "has_network_call": bool(re.search(
                    r"curl|wget|fetch|Invoke-WebRequest|DownloadString|DownloadFile",
                    text, re.IGNORECASE)),
                "has_env_var_pattern": bool(re.search(
                    r"\$\{?[A-Z_]+\}?|os\.environ|Environment::get|"
                    r"\$env:[A-Z_]+", text)),
            })

    # Also CI workflow files
    wf_dir = scan_dir / ".github" / "workflows"
    if wf_dir.is_dir():
        for yml in wf_dir.glob("*.yml"):
            try:
                text = yml.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            import hashlib
            sha = hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:12]
            files.append({
                "path": str(yml.relative_to(scan_dir)),
                "kind": "ci-workflow",
                "runtime": "github-actions",
                "line_count": len(text.splitlines()),
                "file_sha": sha,
                "has_network_call": False,
                "has_env_var_pattern": bool(re.search(r"\$\{\{[^}]+\}\}", text)),
            })

    # Windows patterns (PS1 + BAT + CMD)
    win_patterns = [
        ("invoke_expression", re.compile(r"Invoke-Expression|\biex\b|Invoke-Command", re.IGNORECASE)),
        ("execution_context_invoke", re.compile(r"\$ExecutionContext\.InvokeCommand|Start-Process\s+.*\$")),
        ("exec_policy_bypass", re.compile(r"-ExecutionPolicy\s+Bypass|-EncodedCommand|-Exec\s+Bypass", re.IGNORECASE)),
        ("ps_web_download", re.compile(r"Invoke-WebRequest|iwr\b|Invoke-RestMethod|DownloadString|DownloadFile|WebClient", re.IGNORECASE)),
        ("ps_credentials", re.compile(r"Get-Credential|\$env:USERPROFILE|\$env:APPDATA|ConvertFrom-SecureString")),
        ("batch_redirects", re.compile(r"\^[<>&|]|call\s+:|goto\s+:")),
    ]
    win_hits: list[dict] = []
    for p in scan_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".ps1", ".bat", ".cmd"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for fam, pat in win_patterns:
            if pat.search(text):
                win_hits.append({
                    "file": str(p.relative_to(scan_dir)),
                    "pattern_family": fam,
                })

    return (
        {"executable_files": files},
        {"hits": win_hits, "hit_count": len(win_hits)},
    )


# ---------------------------------------------------------------------------
# Monorepo detection
# ---------------------------------------------------------------------------


def detect_monorepo(manifests: list[dict]) -> dict:
    parents_with_manifests: dict[str, list[str]] = {}
    for mf in manifests:
        path = mf["path"]
        parts = path.split("/")
        if len(parts) > 1:
            parent = "/".join(parts[:-1])
            parents_with_manifests.setdefault(parent, []).append(mf["path"])

    is_mono = len(parents_with_manifests) >= 2
    inner: list[dict] = []
    if is_mono:
        for parent, paths in parents_with_manifests.items():
            first = paths[0]
            ecosystem = MANIFEST_NAMES.get(Path(first).name, "unknown")
            inner.append({
                "path": parent,
                "name": Path(parent).name,
                "ecosystem": ecosystem,
                "manifest_count": len(paths),
            })
    return {
        "is_monorepo": is_mono,
        "inner_packages": inner,
        "lifecycle_script_hits": [],  # populated separately if npm/package.json has hooks
    }


# ---------------------------------------------------------------------------
# Defensive configs derivation
# ---------------------------------------------------------------------------


def derive_defensive_configs(owner_repo: str,
                             dependabot_config: dict,
                             has_security_policy: bool,
                             scan_dir: Path | None) -> dict:
    entries: list[dict] = []
    if dependabot_config.get("present"):
        entries.append({
            "file": ".github/dependabot.yml",
            "type": "dependabot",
            "present": True,
            "detail": f"ecosystems tracked: {dependabot_config.get('ecosystems_tracked')}",
        })
    else:
        entries.append({"file": ".github/dependabot.yml", "type": "dependabot",
                        "present": False})

    # Pre-commit
    if scan_dir and scan_dir.exists():
        pc = scan_dir / ".pre-commit-config.yaml"
        if pc.is_file():
            try:
                text = pc.read_text(encoding="utf-8", errors="replace")
                entries.append({
                    "file": ".pre-commit-config.yaml",
                    "type": "pre-commit",
                    "present": True,
                    "detail": f"{len(text.splitlines())} lines",
                })
            except Exception:
                pass

    entries.append({
        "file": "SECURITY.md",
        "type": "security-policy",
        "present": bool(has_security_policy),
    })

    # Renovate alternatives
    if scan_dir and scan_dir.exists():
        for name in ["renovate.json", ".github/renovate.json", ".renovaterc",
                     ".renovaterc.json"]:
            if (scan_dir / name).exists():
                entries.append({
                    "file": name, "type": "renovate", "present": True,
                })

    return {"entries": entries}


# ---------------------------------------------------------------------------
# Batch-merge detection
# ---------------------------------------------------------------------------


def detect_batch_merges(pr_review: dict, threshold: int = 5) -> dict:
    prs = pr_review.get("prs", [])
    if not prs:
        return {"detected": False, "pr_groups": []}
    # Group by merged_at truncated to 5-minute buckets
    from collections import defaultdict
    buckets: dict[str, list[dict]] = defaultdict(list)
    for pr in prs:
        ts = pr.get("merged_at")
        if not ts:
            continue
        # Normalize to 5-minute bucket
        try:
            d = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            bucket = d.strftime("%Y-%m-%dT%H:%M:00Z")
            # Round down to 5-minute
            d_bucket = d.replace(second=0, microsecond=0)
            d_bucket = d_bucket.replace(minute=(d_bucket.minute // 5) * 5)
            bucket_key = d_bucket.strftime("%Y-%m-%dT%H:%M:00Z")
        except Exception:
            continue
        buckets[bucket_key].append(pr)
    pr_groups = []
    for bucket, group in buckets.items():
        if len(group) >= threshold:
            pr_groups.append({
                "merged_at_bucket": bucket,
                "pr_count": len(group),
                "prs": [p["number"] for p in group],
            })
    return {"detected": bool(pr_groups), "pr_groups": pr_groups}


# ---------------------------------------------------------------------------
# Coverage affirmations
# ---------------------------------------------------------------------------


def build_coverage_affirmations(p1: dict) -> dict:
    inj = p1.get("prompt_injection_scan") or {}
    win = p1.get("windows_patterns") or {}
    channels = (p1.get("distribution_channels") or {}).get("channels") or []
    verifications = (p1.get("artifact_verification") or {}).get("per_channel") or []
    verified_count = sum(1 for v in verifications if v.get("result") == "verified")
    gl = p1.get("gitleaks") or {}
    return {
        "prompt_injection_scan_completed": bool(inj.get("scanned_files") or inj.get("signal_count") == 0),
        "windows_surface_coverage": (
            "scanned" if win.get("hits") is not None else "not scanned"
        ),
        "distribution_channels_verified": f"{verified_count}/{len(channels)}",
        "gitleaks_available": bool(gl.get("available")),
        "gitleaks_explanation": gl.get("note"),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_phase_1(owner_repo: str, head_sha: str | None, scan_dir_opt: Path | None,
                  skip_tarball: bool) -> dict:
    # Pre-flight
    print(f"[pf] pre-flight for {owner_repo}", file=sys.stderr)
    pf, scan_dir = pre_flight(owner_repo, head_sha, scan_dir_opt, skip_tarball)
    default_branch = pf["default_branch"]
    print(f"[pf] head_sha={pf['head_sha'][:12]}, default_branch={default_branch}, "
          f"tarball={'yes' if pf['tarball_extracted'] else 'no'}", file=sys.stderr)

    p1: dict = {"pre_flight": pf}

    print("[1a] repo_metadata", file=sys.stderr)
    p1["repo_metadata"] = step_1_repo_metadata(owner_repo)

    print("[1b] contributors", file=sys.stderr)
    contrib = step_1_contributors(owner_repo)
    p1["contributors"] = contrib

    print("[1c] maintainer_accounts", file=sys.stderr)
    p1["maintainer_accounts"] = step_1_maintainer_accounts(
        owner_repo, contrib.get("top_contributors", []))

    print("[1d] ossf_scorecard", file=sys.stderr)
    p1["ossf_scorecard"] = step_1_ossf_scorecard(owner_repo)

    print("[1e] community_profile", file=sys.stderr)
    p1["community_profile"] = step_1_community_profile(owner_repo)

    print("[1f-j] branch_protection", file=sys.stderr)
    p1["branch_protection"] = step_1_branch_protection(owner_repo, default_branch)

    print("[1k] codeowners", file=sys.stderr)
    p1["codeowners"] = step_1_codeowners(owner_repo)

    print("[1l] releases", file=sys.stderr)
    p1["releases"] = step_1_releases(owner_repo)

    print("[1m] security_advisories", file=sys.stderr)
    p1["security_advisories"] = step_1_security_advisories(owner_repo)

    print("[2] workflows + contents", file=sys.stderr)
    wf, wfc = step_2_workflows(owner_repo)
    p1["workflows"] = wf
    p1["workflow_contents"] = wfc

    print("[2.5] agent_rule_files + prompt_injection_scan", file=sys.stderr)
    cp_agent, inj = step_2_5_agent_rule_files(scan_dir, owner_repo)
    p1["code_patterns"] = {"agent_rule_files": cp_agent["agent_rule_files"]}
    p1["prompt_injection_scan"] = inj

    print("[3] dependencies + dependabot + osv.dev", file=sys.stderr)
    deps, _ = step_3_dependencies(owner_repo, scan_dir)
    p1["dependencies"] = deps

    print("[4] pr_review + open + closed", file=sys.stderr)
    pr_review, open_prs, closed_prs = step_4_pr_review(owner_repo)
    p1["pr_review"] = pr_review
    p1["open_prs"] = open_prs
    p1["closed_not_merged_prs"] = closed_prs

    print("[5] flag security PRs", file=sys.stderr)
    p1["pr_review"] = step_5_flag_security_prs(owner_repo, p1["pr_review"])

    print("[6] issues", file=sys.stderr)
    p1["issues_and_commits"] = step_6_issues(owner_repo)

    print("[7] recent commits", file=sys.stderr)
    p1["issues_and_commits"]["recent_commits"] = step_7_recent_commits(owner_repo)

    print("[7.5] README paste-scan", file=sys.stderr)
    # Fetch README for scan + later install extraction
    readme_text = ""
    if scan_dir and scan_dir.exists() and (scan_dir / "README.md").is_file():
        readme_text = (scan_dir / "README.md").read_text(encoding="utf-8", errors="replace")
    else:
        rc, contents = _gh_api(f"repos/{owner_repo}/contents/README.md")
        if rc == 0 and isinstance(contents, dict):
            readme_text = _b64_decode_contents(contents) or ""
    paste = step_7_5_readme_paste(owner_repo, scan_dir)
    p1["code_patterns"]["readme_paste_blocks"] = paste

    print("[8] distribution + artifact verification + install scripts", file=sys.stderr)
    dc, av, isa = step_8_distribution(
        owner_repo, scan_dir, deps.get("manifest_files", []), readme_text)
    p1["distribution_channels"] = dc
    p1["artifact_verification"] = av
    p1["install_script_analysis"] = isa

    print("[A-pre] gitleaks", file=sys.stderr)
    p1["gitleaks"] = step_a_pre_gitleaks(scan_dir)

    print("[A] dangerous-pattern grep", file=sys.stderr)
    p1["code_patterns"]["dangerous_primitives"] = step_a_dangerous_patterns(scan_dir)

    print("[C] executable inventory + Windows patterns", file=sys.stderr)
    exec_inv, win = step_c_executable_inventory(scan_dir)
    p1["code_patterns"]["executable_files"] = exec_inv["executable_files"]
    # install_hooks is an LLM-synthesis subset; leave empty
    p1["code_patterns"]["install_hooks"] = []
    p1["windows_patterns"] = win

    print("[monorepo] detection", file=sys.stderr)
    p1["monorepo"] = detect_monorepo(deps.get("manifest_files", []))

    print("[defensive_configs] derivation", file=sys.stderr)
    p1["defensive_configs"] = derive_defensive_configs(
        owner_repo, deps.get("dependabot_config", {}),
        p1["community_profile"].get("has_security_policy"), scan_dir)

    print("[batch_merge] detection", file=sys.stderr)
    p1["batch_merge_detection"] = detect_batch_merges(p1["pr_review"])

    print("[coverage_affirmations] build", file=sys.stderr)
    p1["coverage_affirmations"] = build_coverage_affirmations(p1)

    return p1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("owner_repo", help="e.g. microsoft/markitdown")
    ap.add_argument("--head-sha", default=None,
                    help="Pin to this SHA (default: latest on default branch)")
    ap.add_argument("--scan-dir", default=None,
                    help="Directory for tarball extraction (default: tempdir)")
    ap.add_argument("--out", default=None,
                    help="Output form.json path (default: ./phase-1-<repo>.json)")
    ap.add_argument("--skip-tarball", action="store_true",
                    help="Skip tarball extraction; use API-tree fallback for Steps 2.5/A/C")
    args = ap.parse_args()

    scan_dir = Path(args.scan_dir) if args.scan_dir else None

    phase_1 = build_phase_1(args.owner_repo, args.head_sha, scan_dir, args.skip_tarball)

    out_path = Path(args.out) if args.out else Path(
        f"phase-1-{args.owner_repo.replace('/', '-')}.json")
    form = {
        "_meta": {
            "scanner_version": "V2.5-preview-wild",
            "prompt_version": "V2.4",
            "harness_version": "phase_1_harness.py v0.1.0",
            "scan_started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        "target": {
            "owner": args.owner_repo.split("/")[0],
            "repo": args.owner_repo.split("/")[1],
            "full_name": args.owner_repo,
            "url": f"https://github.com/{args.owner_repo}",
        },
        "phase_1_raw_capture": phase_1,
    }
    out_path.write_text(json.dumps(form, indent=2, default=str))
    print(f"\n✓ wrote {out_path}", file=sys.stderr)
    print(f"  phase_1_raw_capture fields populated: {len(phase_1)}", file=sys.stderr)


if __name__ == "__main__":
    main()
