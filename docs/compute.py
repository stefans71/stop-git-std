#!/usr/bin/env python3
"""
compute.py — Phase 3 computation functions for the GitHub repo scanner.

8 fully automatable operations (board-approved classification):
1. C20 severity formula
2. Scorecard cell colors (calibration table)
3. Solo-maintainer flag (>80% threshold)
4. Exhibit grouping (7+ threshold)
5. Boundary-case detection
6. Coverage cell status
7. Methodology boilerplate
8. F5 silent vs unadvertised classification

Each function takes raw data from phase_1 and returns computed output.
All deterministic: same input → same output, no LLM needed.
"""

from datetime import datetime, timedelta, timezone


# ===========================================================================
# 1. C20 Severity Formula
# ===========================================================================

def compute_c20_severity(
    classic_protection_status: int,  # 200, 404, or 403
    rulesets: list,
    rules_on_default: list,
    has_codeowners: bool,
    latest_release_date: str | None,  # ISO date or None
    ships_executable_code: bool,
    scan_date: str | None = None,  # ISO date, defaults to today
) -> dict:
    """C20 governance SPOF severity: Critical when all governance signals
    negative AND repo ships executable code with a recent release.

    Returns dict with boolean inputs and result severity."""
    no_classic = classic_protection_status == 404
    no_rulesets = len(rulesets) == 0
    no_rules = len(rules_on_default) == 0
    no_codeowners = not has_codeowners

    has_recent_release = False
    if latest_release_date:
        scan = datetime.fromisoformat(scan_date) if scan_date else datetime.now(timezone.utc)
        if isinstance(scan, datetime) and scan.tzinfo is None:
            scan = scan.replace(tzinfo=timezone.utc)
        release = datetime.fromisoformat(latest_release_date.replace("Z", "+00:00"))
        if release.tzinfo is None:
            release = release.replace(tzinfo=timezone.utc)
        has_recent_release = (scan - release).days <= 30

    all_governance_negative = no_classic and no_rulesets and no_rules and no_codeowners

    if all_governance_negative and has_recent_release and ships_executable_code:
        result = "Critical"
    elif all_governance_negative:
        result = "Warning"
    else:
        result = None  # No C20 finding

    return {
        "no_classic_protection": no_classic,
        "no_rulesets": no_rulesets,
        "no_rules_on_default": no_rules,
        "no_codeowners": no_codeowners,
        "has_recent_release_30d": has_recent_release,
        "ships_executable_code": ships_executable_code,
        "result": result,
    }


# ===========================================================================
# 2. Scorecard Cell Colors (Calibration Table)
# ===========================================================================

def compute_scorecard_cells(
    formal_review_rate: float | None,
    any_review_rate: float | None,
    has_branch_protection: bool,
    has_codeowners: bool,
    is_solo_maintainer: bool,
    open_security_issue_count: int,
    oldest_cve_pr_age_days: int | None,
    has_security_policy: bool,
    published_advisory_count: int,
    has_silent_fixes: bool,
    all_channels_pinned: bool,
    artifact_verified: bool,
    has_critical_on_default_path: bool,
    has_warning_or_above: bool,
) -> dict:
    """Compute the 4 scorecard cells using the V2.4 calibration table.
    Returns dict with color (red/amber/green) and short_answer per cell."""

    # Q1: Does anyone check the code?
    # V2.4 calibration: Green = any>=60% AND formal>=30% AND branch protection
    # Amber = any>=50% OR formal>=20%
    # Red = any<30% OR (solo-maintainer AND any<40%)
    formal = formal_review_rate or 0
    any_rev = any_review_rate or 0
    if any_rev >= 60 and formal >= 30 and has_branch_protection:
        q1_color = "green"
        q1_answer = "Yes"
    elif any_rev < 30 or (is_solo_maintainer and any_rev < 40):
        q1_color = "red"
        q1_answer = "No"
    elif any_rev >= 50 or formal >= 20:
        q1_color = "amber"
        q1_answer = "Partly"
    else:
        q1_color = "red"
        q1_answer = "No"

    # Q2: Do they fix problems quickly?
    cve_age = oldest_cve_pr_age_days or 0
    if open_security_issue_count == 0 and cve_age <= 7:
        q2_color = "green"
        q2_answer = "Yes"
    elif open_security_issue_count <= 3 and cve_age <= 14:
        q2_color = "amber"
        q2_answer = "Partly"
    else:
        q2_color = "red"
        q2_answer = "No"

    # Q3: Do they tell you about problems?
    if has_security_policy and published_advisory_count > 0 and not has_silent_fixes:
        q3_color = "green"
        q3_answer = "Yes"
    elif has_security_policy or (published_advisory_count > 0 and not has_silent_fixes):
        q3_color = "amber"
        q3_answer = "Partly"
    else:
        q3_color = "red"
        q3_answer = "No"

    # Q4: Is it safe out of the box?
    # V2.4 calibration: Green = all pinned + verified + no Warning+
    # Red = any Critical on default install path
    # Amber = any unverified channel OR group-specific finding
    if all_channels_pinned and artifact_verified and not has_warning_or_above:
        q4_color = "green"
        q4_answer = "Yes"
    elif has_critical_on_default_path:
        q4_color = "red"
        q4_answer = "No"
    elif has_warning_or_above or not all_channels_pinned or not artifact_verified:
        q4_color = "amber"
        q4_answer = "Partly"
    else:
        q4_color = "amber"
        q4_answer = "Partly"

    return {
        "does_anyone_check_the_code": {
            "color": q1_color, "short_answer": q1_answer,
            "inputs": {"formal_review_rate": formal, "any_review_rate": any_rev,
                       "has_branch_protection": has_branch_protection, "has_codeowners": has_codeowners}
        },
        "do_they_fix_problems_quickly": {
            "color": q2_color, "short_answer": q2_answer,
            "inputs": {"open_security_issue_count": open_security_issue_count,
                       "oldest_open_cve_pr_age_days": oldest_cve_pr_age_days}
        },
        "do_they_tell_you_about_problems": {
            "color": q3_color, "short_answer": q3_answer,
            "inputs": {"has_security_policy": has_security_policy,
                       "published_advisory_count": published_advisory_count,
                       "has_silent_fixes": has_silent_fixes}
        },
        "is_it_safe_out_of_the_box": {
            "color": q4_color, "short_answer": q4_answer,
            "inputs": {"all_channels_pinned": all_channels_pinned,
                       "artifact_verified": artifact_verified,
                       "has_warning_or_above_finding": has_warning_or_above}
        },
    }


# ===========================================================================
# 3. Solo-Maintainer Flag
# ===========================================================================

def compute_solo_maintainer(contributors: list) -> dict:
    """F11: If top contributor has >80% of commits, flag as solo-maintainer.
    Returns dict with share, boolean, and verbatim sentence."""
    if not contributors:
        return {"top_contributor_share": None, "is_solo": False, "verbatim_sentence": None}

    total = sum(c.get("contributions", 0) for c in contributors)
    if total == 0:
        return {"top_contributor_share": None, "is_solo": False, "verbatim_sentence": None}

    top = max(contributors, key=lambda c: c.get("contributions", 0))
    share = top["contributions"] / total

    if share > 0.80:
        sentence = (
            f"Note: {top['login']} accounts for {share:.0%} of all commits. "
            f"This is a solo-maintainer project — all governance findings "
            f"should be read in that context."
        )
        return {"top_contributor_share": round(share, 3), "is_solo": True,
                "verbatim_sentence": sentence}

    return {"top_contributor_share": round(share, 3), "is_solo": False,
            "verbatim_sentence": None}


# ===========================================================================
# 4. Exhibit Grouping
# ===========================================================================

def compute_exhibit_grouping(findings: list) -> dict:
    """S8-3: When 7+ similar-severity items, group into themed exhibits.
    Themes: vuln (amber), govern (red), signals (green)."""
    total = len(findings)
    threshold_met = total >= 7

    if not threshold_met:
        return {"total_findings": total, "threshold_met": False, "exhibits": []}

    vuln = [f for f in findings if f.get("severity") in ("Critical", "Warning")
            and f.get("category", "").startswith(("vuln/", "supply-chain/"))]
    govern = [f for f in findings if f.get("severity") in ("Critical", "Warning")
              and f.get("category", "").startswith(("governance/", "maintainer/"))]
    signals = [f for f in findings if f.get("severity") in ("OK", "Info")]

    exhibits = []
    if vuln:
        exhibits.append({"theme": "vuln", "severity_tone": "warn",
                         "finding_ids": [f["id"] for f in vuln]})
    if govern:
        exhibits.append({"theme": "govern", "severity_tone": "critical",
                         "finding_ids": [f["id"] for f in govern]})
    if signals:
        exhibits.append({"theme": "signals", "severity_tone": "ok",
                         "finding_ids": [f["id"] for f in signals]})

    return {"total_findings": total, "threshold_met": True, "exhibits": exhibits}


# ===========================================================================
# 5. Boundary-Case Detection
# ===========================================================================

def compute_boundary_cases(
    latest_release_age_days: int | None,
    formal_review_rate: float | None,
    any_review_rate: float | None,
) -> dict:
    """Detect when values are near severity thresholds."""
    cases = []

    # C20: 30-day release window
    if latest_release_age_days is not None:
        margin = latest_release_age_days - 30
        if 0 < margin <= 5:
            cases.append({
                "threshold": "C20 release age (30 days)",
                "actual_value": latest_release_age_days,
                "margin": margin,
                "note": f"{margin} day(s) outside the Critical window",
                "would_change_to": "Critical"
            })
        elif -5 <= margin <= 0:
            cases.append({
                "threshold": "C20 release age (30 days)",
                "actual_value": latest_release_age_days,
                "margin": margin,
                "note": f"{abs(margin)} day(s) inside the Critical window",
                "would_change_to": "Warning"
            })

    # Review rate thresholds
    if formal_review_rate is not None:
        if 25 <= formal_review_rate <= 35:
            cases.append({
                "threshold": "Scorecard Q1 formal review (30%)",
                "actual_value": formal_review_rate,
                "margin": round(formal_review_rate - 30, 1),
                "note": "Near the green/amber boundary for code review scorecard",
                "would_change_to": "amber" if formal_review_rate >= 30 else "green"
            })

    return {"cases": cases}


# ===========================================================================
# 6. Coverage Cell Status
# ===========================================================================

def compute_coverage_status(raw_capture: dict) -> dict:
    """Map command outcomes to coverage status enums.
    Status values: ok, partial, blocked, not_available, not_indexed, not_queried, unknown"""
    cells = []

    # Tarball extraction
    cells.append({
        "name": "Tarball extraction",
        "status": "ok" if raw_capture.get("pre_flight", {}).get("tarball_extracted") else "blocked",
        "detail": f"{raw_capture.get('pre_flight', {}).get('tarball_file_count', 0)} files"
    })

    # OSSF Scorecard
    ossf = raw_capture.get("ossf_scorecard", {})
    if ossf.get("indexed"):
        cells.append({"name": "OSSF Scorecard", "status": "ok",
                       "detail": f"{ossf.get('overall_score')}/10"})
    elif ossf.get("queried"):
        cells.append({"name": "OSSF Scorecard", "status": "not_indexed",
                       "detail": "Repo not indexed by OSSF"})
    else:
        cells.append({"name": "OSSF Scorecard", "status": "not_queried",
                       "detail": "API not queried"})

    # osv.dev
    osv = raw_capture.get("dependencies", {}).get("osv_dev", {})
    if osv.get("queried"):
        cells.append({"name": "osv.dev", "status": "ok",
                       "detail": f"{osv.get('packages_queried', 0)} packages, {osv.get('total_vulns', 0)} vulns"})
    elif raw_capture.get("dependencies", {}).get("runtime_count", 0) == 0:
        cells.append({"name": "osv.dev", "status": "not_queried",
                       "detail": "Zero runtime dependencies"})
    else:
        cells.append({"name": "osv.dev", "status": "not_queried", "detail": ""})

    # gitleaks
    gl = raw_capture.get("gitleaks", {})
    if gl.get("ran"):
        cells.append({"name": "Secrets-in-history (gitleaks)", "status": "ok",
                       "detail": f"{gl.get('findings_count', 0)} findings"})
    elif gl.get("available"):
        cells.append({"name": "Secrets-in-history (gitleaks)", "status": "not_available",
                       "detail": "gitleaks available but not run"})
    else:
        cells.append({"name": "Secrets-in-history (gitleaks)", "status": "not_available",
                       "detail": "gitleaks not installed"})

    # API rate budget
    rate = raw_capture.get("pre_flight", {}).get("api_rate_limit", {})
    if rate.get("remaining") is not None:
        cells.append({"name": "API rate budget", "status": "ok",
                       "detail": f"{rate['remaining']}/{rate.get('limit', '?')} remaining"})

    # Dependabot
    dep = raw_capture.get("dependencies", {}).get("dependabot", {})
    dep_status = dep.get("status", "unknown")
    if dep_status == "active":
        cells.append({"name": "Dependabot alerts", "status": "ok", "detail": "Active"})
    elif dep_status == "disabled":
        cells.append({"name": "Dependabot alerts", "status": "blocked",
                       "detail": "Disabled for this repository"})
    else:
        cells.append({"name": "Dependabot alerts", "status": "unknown",
                       "detail": dep.get("error_message", "Unknown")})

    return {"cells": cells}


# ===========================================================================
# 7. Methodology Boilerplate
# ===========================================================================

def compute_methodology(scanner_version: str, prompt_version: str, guide_version: str) -> dict:
    """Section 08 — identical across all scans, only version strings vary."""
    return {
        "scanner_version": scanner_version,
        "prompt_version": prompt_version,
        "guide_version": guide_version,
    }


# ===========================================================================
# 8. F5 Silent vs Unadvertised Classification
# ===========================================================================

ATTACK_CLASS_KEYWORDS = [
    "symlink", "path traversal", "directory traversal", "rce", "remote code",
    "xss", "cross-site", "injection", "overflow", "privilege escalation",
    "denial of service", "dos", "csrf", "ssrf", "deserialization",
    "authentication bypass", "authorization", "credential", "secret",
    "hardening", "security fix", "vulnerability", "cve-",
]


def classify_f5_disclosure(release_title: str, release_notes: str, attack_class: str) -> str:
    """F5: Classify security fix disclosure as silent or unadvertised.

    'Unadvertised' = advisory missing but release notes mention the fix.
    'Silent' = release notes omit or mislabel the fix.
    'Properly disclosed' = advisory exists."""
    text = (release_title + " " + release_notes).lower()
    attack_lower = attack_class.lower()

    # Check if the specific attack class is referenced
    if attack_lower in text:
        return "unadvertised"

    # Check general security keywords
    for keyword in ATTACK_CLASS_KEYWORDS:
        if keyword in text:
            return "unadvertised"

    return "silent"


# ===========================================================================
# Verdict computation (Phase 4b — depends on finalized findings)
# ===========================================================================

def compute_verdict(findings: list) -> dict:
    """Verdict = max severity of all findings.
    Critical > Warning > Info > OK."""
    severity_order = {"Critical": 3, "Warning": 2, "Info": 1, "OK": 0}
    if not findings:
        return {"level": "Clean", "computed_from_findings": []}

    max_sev = max(findings, key=lambda f: severity_order.get(f.get("severity", "OK"), 0))
    max_level = max_sev.get("severity", "OK")

    # Map finding severity to verdict level
    verdict_map = {"Critical": "Critical", "Warning": "Caution", "Info": "Caution", "OK": "Clean"}

    return {
        "level": verdict_map.get(max_level, "Caution"),
        "computed_from_findings": [f["id"] for f in findings if f.get("severity") == max_level]
    }
