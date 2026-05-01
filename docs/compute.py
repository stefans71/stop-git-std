#!/usr/bin/env python3
"""
compute.py — Phase 3 computation functions for the GitHub repo scanner.

V1.2 scope (post-2026-04-20 board review, docs/External-Board-Reviews/042026-schema-v12/):
  - 7 byte-for-byte deterministic operations remain in phase_3_computed.
  - compute_scorecard_cells() is DEMOTED TO ADVISORY — output feeds
    phase_3_advisory.scorecard_hints (non-authoritative). Phase 4 LLM
    is the scorecard cell authority and may override with rationale +
    computed_signal_refs citing the 23 frozen SIGNAL_IDs below.
  - SIGNAL_IDS exported as a frozenset — validator resolves Phase 4's
    computed_signal_refs against this set (gate 6.3 override-explained).

Fully automatable operations (board-approved 8/8/4 classification):
1. C20 severity formula
2. Scorecard cell ADVISORY hints (was authoritative pre-V1.2)
3. Solo-maintainer flag (>80% threshold)
4. Exhibit grouping (7+ threshold)
5. Boundary-case detection
6. Coverage cell status
7. Methodology boilerplate
8. F5 silent vs unadvertised classification

Each function takes raw data from phase_1 and returns computed output.
All deterministic: same input → same output, no LLM needed.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import NamedTuple


# ===========================================================================
# V1.2 Signal ID vocabulary (frozen per 2026-04-20 board review Item F)
# ===========================================================================
#
# Phase 4 LLM cites these IDs in scorecard_cells[key].computed_signal_refs
# when overriding phase_3_advisory.scorecard_hints[key].color. Validator
# (docs/validate-scanner-report.py) resolves every ref against this set.
#
# Naming convention (frozen V1.2):
#   q1_ / q2_ / q3_ / q4_  — scorecard-input signals (scoped to the 4 cells)
#   c20_                   — supporting signals for C20 governance SPOF
#
# V1.2.x patches may ADD signals without a schema bump; removing any signal
# requires a V1.3 bump. Post-V1.2 telemetry (override-pattern log) drives
# the "add more" decision — see CONSOLIDATION §8 V12x-3, V12x-4 triggers.

SIGNAL_IDS: frozenset[str] = frozenset({
    # Q1 — Does anyone check the code?
    "q1_formal_review_rate",
    "q1_any_review_rate",
    "q1_has_branch_protection",
    "q1_has_ruleset_protection",  # V1.2.x (V13-1): ruleset-based protection signal
    "q1_has_codeowners",
    "q1_is_solo_maintainer",
    "q1_governance_floor_override",
    # Q2 — Do they fix problems quickly?
    "q2_open_security_issue_count",
    "q2_oldest_open_cve_pr_age_days",
    "q2_oldest_open_security_item_age_days",  # V1.2.x (V13-1): widened evidence — issues + security-PRs
    "q2_closed_fix_lag_days",
    # Q3 — Do they tell you about problems?
    "q3_has_security_policy",
    "q3_has_contributing_guide",
    "q3_published_advisory_count",
    "q3_has_silent_fixes",
    "q3_has_reported_fixed_vulns",
    # Q4 — Is it safe out of the box?
    "q4_all_channels_pinned",
    "q4_artifact_verified",
    "q4_has_critical_on_default_path",
    "q4_has_warning_on_install_path",
    # C20 supporting signals
    "c20_has_classic_protection",
    "c20_has_rulesets",
    "c20_has_rules_on_default",
    "c20_has_recent_release_30d",
    "c20_ships_executable_code",
})


OVERRIDE_REASON_ENUM: frozenset[str] = frozenset({
    "threshold_too_strict",
    "threshold_too_lenient",
    "missing_qualitative_context",
    "rubric_literal_vs_intent",
    "signal_vocabulary_gap",
    "harness_coverage_gap",
    "other",
})


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
#
# SF1 board review (2026-04-20, docs/External-Board-Reviews/042026-sf1-calibration/):
# The 4 Q1-Q2-Q3-Q4 calibration functions below carry TEMPORARY COMPATIBILITY
# PATCHES for V1.1 Step G acceptance. These align compute output with the V2.4
# comparator-MD judgments for zustand-v3, caveman, and Archon. They are NOT the
# endorsed steady-state design. Scorecard-cell authority migrates to
# phase_4_structured_llm in V1.2 per deferred item D-7 (Operator Guide §8.8.7).
#
# Patch inventory applied here:
#   Q1: governance-floor override — formal<10% AND no branch_protection AND
#       no codeowners forces red regardless of any-review threshold.
#   Q2: closed_fix_lag_days input — merged security fix >3 days drops green
#       to amber (visible friction signal).
#   Q3: has_contributing_guide input — amber floor includes contributing
#       guide as a disclosure gesture.
#   Q4: has_warning_on_install_path input (replacing has_warning_or_above)
#       — governance warnings outside install-path no longer block green.

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
    has_warning_on_install_path: bool,
    has_contributing_guide: bool = False,
    closed_fix_lag_days: int | None = None,
    has_ruleset_protection: bool = False,
    oldest_open_security_item_age_days: int | None = None,
    phase_1_raw_capture: dict | None = None,
) -> dict:
    """Compute the 4 scorecard cells using the V2.4 calibration table.
    Returns dict with color (red/amber/green) and short_answer per cell.

    SF1 patches (temporary V1.1 compatibility; migrates to V1.2 D-7):
      - has_contributing_guide: Q3 amber floor signal (disclosure gesture
        without formal SECURITY.md).
      - has_warning_on_install_path: Q4 install-scope warning (governance
        warnings elsewhere don't block green).
      - closed_fix_lag_days: Q2 merged security PR age (>3 days → amber).
      - Q1 governance-floor override baked into the branches below.

    V1.2.x signal widening (V13-1 owner directive 2026-04-20):
      - has_ruleset_protection: True when branch_protection.rulesets.count >= 1
        AND branch_protection.rules_on_default.count >= 1. Folds into the Q1
        governance-floor check as `has_any_branch_protection =
        has_branch_protection OR has_ruleset_protection`. Addresses ghostty
        entry 16 + kamal entry 18 Q1 overrides where classic-only check
        missed ruleset-based protection.
      - oldest_open_security_item_age_days: widens Q2 age evidence beyond
        CVE-labeled PRs to include open issues with security keywords and
        security-labeled PRs. Q2 now considers max(oldest_cve_pr_age_days,
        oldest_open_security_item_age_days). Addresses Kronos entry 17 Q2
        override where a 95-day-old open issue was invisible to the
        PR-scoped signal.

    V1.2.x (V13-3 C5 integration, owner directive OD-4 + Codex code-review
    gate 2026-04-20):
      - phase_1_raw_capture: optional. When provided, compute_q4_autofires_from_phase_1
        is invoked and its `has_critical_on_default_path` result is OR-merged
        with the explicit kwarg. This is the live integration point for the
        C5 deserialization auto-fire: scan drivers pass phase_1_raw_capture
        and the Q4 advisory upgrades automatically when unsafe-deserialization
        + tool-loads-user-files conditions are met. Phase 4 retains override
        authority per D-7 scorecard-authority boundary (may still author a
        different color in phase_4_structured_llm.scorecard_cells).
    """

    # V13-3 C5: Q4 auto-fire from Phase 1 raw capture (when provided).
    # OR-merge with the explicit kwarg — never downgrades an explicit True.
    if phase_1_raw_capture is not None:
        autofires = compute_q4_autofires_from_phase_1(phase_1_raw_capture)
        if autofires.get("has_critical_on_default_path"):
            has_critical_on_default_path = True

    # Q1: Does anyone check the code?
    # V2.4 calibration: Green = any>=60% AND formal>=30% AND branch protection
    # Amber = any>=50% OR formal>=20%
    # Red = any<30% OR (solo-maintainer AND any<40%)
    # SF1 patch: Q1 governance-floor override — formal<10% AND no branch
    # protection AND no codeowners forces red (Archon-shape: high any-review
    # masking functionally-absent review process).
    # V1.2.x (V13-1): has_any_branch_protection = classic OR ruleset-based.
    formal = formal_review_rate or 0
    any_rev = any_review_rate or 0
    has_any_branch_protection = has_branch_protection or has_ruleset_protection
    if (formal < 10 and not has_any_branch_protection and not has_codeowners):
        q1_color = "red"
        q1_answer = "No"
    elif any_rev >= 60 and formal >= 30 and has_any_branch_protection:
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
    # SF1 patch: closed_fix_lag_days — a repo with merged security PR taking
    # >3 days is amber even if no open issues (caveman-shape friction signal).
    # V1.2.x (V13-1): cve_age = max(oldest_cve_pr_age_days,
    # oldest_open_security_item_age_days) — widens evidence beyond PRs to
    # include open security issues + security-labeled PRs.
    cve_age = max(oldest_cve_pr_age_days or 0, oldest_open_security_item_age_days or 0)
    if open_security_issue_count == 0 and cve_age <= 7:
        if closed_fix_lag_days is not None and closed_fix_lag_days > 3:
            q2_color = "amber"
            q2_answer = "Partly"
        else:
            q2_color = "green"
            q2_answer = "Yes"
    elif open_security_issue_count <= 3 and cve_age <= 14:
        q2_color = "amber"
        q2_answer = "Partly"
    else:
        q2_color = "red"
        q2_answer = "No"

    # Q3: Do they tell you about problems?
    # SF1 patch: has_contributing_guide — a repo with a contributing guide
    # offers a disclosure gesture (place to report) even without SECURITY.md,
    # so it reaches the amber floor rather than red (zustand-shape).
    if has_security_policy and published_advisory_count > 0 and not has_silent_fixes:
        q3_color = "green"
        q3_answer = "Yes"
    elif (has_security_policy or has_contributing_guide
          or (published_advisory_count > 0 and not has_silent_fixes)):
        q3_color = "amber"
        q3_answer = "Partly"
    else:
        q3_color = "red"
        q3_answer = "No"

    # Q4: Is it safe out of the box?
    # V2.4 calibration: Red = any Critical on default install path (highest priority)
    # Green = all pinned + verified + no Warning+ on install path + no Critical on default
    # Amber = any unverified channel OR install-path Warning OR group-specific finding
    # SF1 patch: has_warning_on_install_path replaces has_warning_or_above —
    # governance/upstream warnings outside the install path (zustand F0:
    # no branch protection) no longer drop Q4 below green.
    # V13-3 (2026-04-20 Codex code-review r2): has_critical_on_default_path check
    # moved FIRST so a Critical-on-default-path (including C5 auto-fire) always
    # forces red even when channels are pinned. Prior ordering let green win
    # first, making Critical-but-pinned scans incorrectly report green.
    if has_critical_on_default_path:
        q4_color = "red"
        q4_answer = "No"
    elif all_channels_pinned and artifact_verified and not has_warning_on_install_path:
        q4_color = "green"
        q4_answer = "Yes"
    elif has_warning_on_install_path or not all_channels_pinned or not artifact_verified:
        q4_color = "amber"
        q4_answer = "Partly"
    else:
        q4_color = "amber"
        q4_answer = "Partly"

    # V1.2: emit advisory shape with signals list (IDs from SIGNAL_IDS
    # frozenset). Feeds phase_3_advisory.scorecard_hints in the form.
    # V1.2.x (V13-1): governance floor now reads has_any_branch_protection.
    governance_floor_triggered = (
        formal < 10 and not has_any_branch_protection and not has_codeowners
    )
    return {
        "does_anyone_check_the_code": {
            "color": q1_color, "short_answer": q1_answer,
            "signals": [
                {"id": "q1_formal_review_rate", "value": formal},
                {"id": "q1_any_review_rate", "value": any_rev},
                {"id": "q1_has_branch_protection", "value": has_branch_protection},
                {"id": "q1_has_ruleset_protection", "value": has_ruleset_protection},
                {"id": "q1_has_codeowners", "value": has_codeowners},
                {"id": "q1_is_solo_maintainer", "value": is_solo_maintainer},
                {"id": "q1_governance_floor_override", "value": governance_floor_triggered},
            ],
        },
        "do_they_fix_problems_quickly": {
            "color": q2_color, "short_answer": q2_answer,
            "signals": [
                {"id": "q2_open_security_issue_count", "value": open_security_issue_count},
                {"id": "q2_oldest_open_cve_pr_age_days", "value": oldest_cve_pr_age_days},
                {"id": "q2_oldest_open_security_item_age_days", "value": oldest_open_security_item_age_days},
                {"id": "q2_closed_fix_lag_days", "value": closed_fix_lag_days},
            ],
        },
        "do_they_tell_you_about_problems": {
            "color": q3_color, "short_answer": q3_answer,
            "signals": [
                {"id": "q3_has_security_policy", "value": has_security_policy},
                {"id": "q3_has_contributing_guide", "value": has_contributing_guide},
                {"id": "q3_published_advisory_count", "value": published_advisory_count},
                {"id": "q3_has_silent_fixes", "value": has_silent_fixes},
            ],
        },
        "is_it_safe_out_of_the_box": {
            "color": q4_color, "short_answer": q4_answer,
            "signals": [
                {"id": "q4_all_channels_pinned", "value": all_channels_pinned},
                {"id": "q4_artifact_verified", "value": artifact_verified},
                {"id": "q4_has_critical_on_default_path", "value": has_critical_on_default_path},
                {"id": "q4_has_warning_on_install_path", "value": has_warning_on_install_path},
            ],
        },
    }


# ===========================================================================
# 3. Solo-Maintainer Flag
# ===========================================================================

def derive_q1_has_ruleset_protection(branch_protection: dict | None) -> bool:
    """V1.2.x (V13-1): True when ruleset-based branch protection is active.

    Reads phase_1_raw_capture.branch_protection. Fires when both:
      - rulesets.count >= 1 (at least one ruleset scoped to default branch)
      - rules_on_default.count >= 1 (at least one enforced rule)

    This captures GitHub's modern ruleset-based protection which is invisible
    to the classic-protection API (branches/<ref>/protection returns 404).
    Fix for ghostty entry 16 + kamal entry 18 Q1 overrides.
    """
    if not branch_protection:
        return False
    rulesets = (branch_protection.get("rulesets") or {}).get("count") or 0
    rules_on_default = (branch_protection.get("rules_on_default") or {}).get("count") or 0
    return rulesets >= 1 and rules_on_default >= 1


_SECURITY_KEYWORDS = re.compile(
    r"\b(security|vuln|vulnerab|cve|ghsa|rce|xxe|xss|csrf|sqli|injection|"
    r"deserialization|pickle|traversal|ssrf|advisory|exploit|exposure|leak)\b",
    re.IGNORECASE,
)


def derive_q2_oldest_open_security_item_age_days(
    issues_and_commits: dict | None,
    open_prs: dict | None,
    scan_date_iso: str | None = None,
) -> int | None:
    """V1.2.x (V13-1): max age-in-days of any open security item.

    Reads from phase_1_raw_capture:
      - issues_and_commits.open_security_issues[*].created_at
      - open_prs.entries[*] filtered by title keyword match (security, vuln,
        cve, rce, ...) — labels are rarely applied on non-CVE repos.

    Returns None if nothing matches, else int days since max(created_at).

    Addresses Kronos entry 17 Q2 override where a 95-day-old open issue
    (#216, pickle deserialization RCE) was invisible to the PR-scoped
    q2_oldest_open_cve_pr_age_days signal.
    """
    from datetime import date, datetime, timezone

    if scan_date_iso:
        scan_date = date.fromisoformat(scan_date_iso)
    else:
        scan_date = datetime.now(timezone.utc).date()

    ages: list[int] = []

    if issues_and_commits:
        for issue in (issues_and_commits.get("open_security_issues") or []):
            created = issue.get("created_at")
            if not created:
                continue
            try:
                created_date = datetime.fromisoformat(created.replace("Z", "+00:00")).date()
                ages.append((scan_date - created_date).days)
            except (ValueError, AttributeError):
                continue

    if open_prs:
        for pr in (open_prs.get("entries") or []):
            title = pr.get("title") or ""
            if not _SECURITY_KEYWORDS.search(title):
                continue
            created = pr.get("created_at")
            if not created:
                continue
            try:
                created_date = datetime.fromisoformat(created.replace("Z", "+00:00")).date()
                ages.append((scan_date - created_date).days)
            except (ValueError, AttributeError):
                continue

    return max(ages) if ages else None


# V1.2.x (V13-3 C18, owner directive 2026-04-20): derivation helper for the
# "tool loads user files" judgment. Canonical storage of this heuristic lives
# in compute.py per V13-1 precedent (derive_q1_has_ruleset_protection,
# derive_q2_oldest_open_security_item_age_days). Scan drivers MUST NOT
# reimplement this logic ad hoc.
# Verb-then-noun-within-few-words pattern. Captures phrases like
# "opens a board file", "parses a document", "loads a pretrained model",
# "reads a binsnapshot" — i.e. the tool consuming user-provided input as a
# default operation, typed in either plural-verb (opens/parses/loads/reads)
# or singular-verb (open/parse/load/read) form.
_FILE_LOADING_README_PATTERNS = re.compile(
    r"\b(opens?|parses?|loads?|reads?|imports?)\b"
    r"(?:\s+\w+){0,4}\s+"
    r"\b(files?|documents?|designs?|boards?|models?|presets?|configs?|"
    r"datasets?|checkpoints?|pdfs?|docx|epub|binsnapshots?|snapshots?|"
    r"binaries?|archives?)\b",
    re.IGNORECASE,
)

_FILE_LOADING_TOPICS = frozenset({
    # Tools that inherently consume user files / designs / datasets
    "document-conversion", "document-parser", "pdf", "docx",
    "eda", "cad", "pcb", "routing",
    "ml", "machine-learning", "deep-learning", "foundation-model",
    "dataset", "checkpoint", "pretrained",
    "file-parser", "format-converter",
})


def derive_tool_loads_user_files(
    readme_text: str | None,
    repo_metadata: dict | None,
) -> bool:
    """V1.2.x (V13-3 C18): True when repo README or topic list indicates the
    tool consumes user-provided files as a default operation.

    Logic is OR over two independent evidence sources:
      - README text (phase_1_raw_capture source) matches verb-then-noun phrases
        like "opens a board file", "parses a document", "loads a pretrained
        model" — see _FILE_LOADING_README_PATTERNS.
      - repo_metadata.topics[] contains a file-consuming category from
        _FILE_LOADING_TOPICS (document-conversion, eda, pcb, ml, dataset, etc.)

    Returns True if EITHER source matches; False only when both are absent or
    neither yields a match.

    Used as a precondition for V13-3 Q4 auto-fire from deserialization hits:
    if a repo both exposes unsafe deserialization AND is documented as loading
    user files, the default-path critical condition is true.

    Not a regex on code — this is a README/metadata-level judgment helper.
    """
    if readme_text and _FILE_LOADING_README_PATTERNS.search(readme_text):
        return True

    if repo_metadata:
        topics = repo_metadata.get("topics") or []
        if any(t in _FILE_LOADING_TOPICS for t in topics):
            return True

    return False


def derive_q4_critical_on_default_path_from_deserialization(
    dangerous_primitives: dict | None,
    readme_text: str | None = None,
    repo_metadata: dict | None = None,
    threshold: int = 3,
) -> bool:
    """V1.2.x (V13-3 C5, owner directive 2026-04-20): auto-fire Q4
    has_critical_on_default_path when a repo exposes unsafe deserialization
    primitives AND is documented as loading user files.

    Condition (all must be true):
      - `dangerous_primitives.deserialization.hit_count >= threshold` (default 3)
      - `derive_tool_loads_user_files()` returns True

    Cross-module contract: this function reads only the aggregate `hit_count`,
    not individual hit snippets. It relies on Phase 1 (`phase_1_harness.py`
    STEP_A_PATTERNS) having already language-qualified the deserialization
    family — specifically, the V13-3 C2 change dropped the bare `deserialize`
    keyword so that ArduinoJson-class `deserializeJson(...)` and serde-style
    `deserialize()` no longer count toward hit_count. If that harness-side
    qualification is weakened in future, this helper's precision degrades
    correspondingly.

    Would have auto-resolved freerouting entry 24 Q4 (30 ObjectInputStream
    hits in BasicBoard.java + pcb topic → True) per dry-run at
    `docs/v13-3-fp-dry-run.md`. Does NOT fire on WLED entry 25 because
    post-C2 ArduinoJson hit_count = 0. Kronos entry 17 (single pickle.load
    site) is below the default threshold and would not fire from
    deserialization alone — collapse of that override depends on the broader
    V1.2.x pickle.loads? regex widening landed earlier, not on this helper.

    Returns False if deserialization field missing, hit_count below threshold,
    or tool-loads-user-files false.
    """
    if not dangerous_primitives:
        return False
    deser = dangerous_primitives.get("deserialization") or {}
    hit_count = deser.get("hit_count") or 0
    if hit_count < threshold:
        return False

    loads_user_files = derive_tool_loads_user_files(
        readme_text=readme_text,
        repo_metadata=repo_metadata,
    )
    return loads_user_files


def compute_q4_autofires_from_phase_1(phase_1_raw_capture: dict | None) -> dict:
    """V1.2.x (V13-3 C5 integration, owner directive OD-4 + Codex code-review
    gate 2026-04-20): derive Q4 auto-fire signals from Phase 1 raw capture.

    Call sites: this wrapper is invoked INTERNALLY by `compute_scorecard_cells()`
    when the caller passes `phase_1_raw_capture=<p1>`. Scan drivers do NOT need
    to call this directly — passing phase_1_raw_capture to compute_scorecard_cells
    triggers the auto-fire automatically. The wrapper is exposed here for unit
    testing and for rare callers who need the auto-fire result without
    invoking the full scorecard computation.

    Returns a dict with the auto-fire signals derivable from phase_1_raw_capture:
      - has_critical_on_default_path (bool): True when V13-3 C5 fires
      - reasons (list[str]): which derivation paths contributed to the True
        verdict (e.g., ["deserialization_c5"])

    Reads from phase_1_raw_capture:
      - code_patterns.dangerous_primitives (C5 input)
      - repo_metadata (C18 topic signal)
      - README is NOT currently stored in phase_1_raw_capture; the C18
        README-text signal is therefore not exercised by this wrapper.
        Callers that have README text in hand may call
        `derive_q4_critical_on_default_path_from_deserialization` directly.

    Conservative by design: if phase_1_raw_capture is missing/empty, returns
    {has_critical_on_default_path: False, reasons: []}.
    """
    result = {"has_critical_on_default_path": False, "reasons": []}
    if not phase_1_raw_capture:
        return result

    code_patterns = phase_1_raw_capture.get("code_patterns") or {}
    dangerous_primitives = code_patterns.get("dangerous_primitives") or {}
    repo_metadata = phase_1_raw_capture.get("repo_metadata") or {}

    if derive_q4_critical_on_default_path_from_deserialization(
        dangerous_primitives=dangerous_primitives,
        readme_text=None,  # not currently stored in phase_1_raw_capture
        repo_metadata=repo_metadata,
    ):
        result["has_critical_on_default_path"] = True
        result["reasons"].append("deserialization_c5")

    return result


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


# ===========================================================================
# Calibration v2 — shape classifier + rule-table cell evaluators
# ===========================================================================
#
# Phase 3 of `docs/back-to-basics-plan.md`. Spec is `docs/calibration-design-v2.md`
# (3-of-3 R3 SIGN OFF, archive at `docs/External-Board-Reviews/050126-calibration-rebuild/`).
#
# Architecture: shape-as-modifier. One unified rule table with shape-conditional
# branches where rules need shape awareness. Rule evaluation order per design §2:
#   1. Auto-fire trips (short-circuit on first match)
#   2. Shape modifiers
#   3. Sample-floor / context modifiers
#   4. Base rule table (signal-driven; current calibration baseline)
#   5. Fallback (existing compute_scorecard_cells advisory)
# First-match-wins. No combining. rule_id REQUIRED on every CellEvaluation.
#
# `compute_scorecard_cells_v2()` is the new orchestrator. The legacy
# `compute_scorecard_cells()` is retained as-is for backwards compatibility with
# existing scan drivers; v2 is opt-in via the new entry point.

# 9 closed-enum shape categories per design §3.
SHAPE_CATEGORIES = frozenset({
    "library-package",
    "cli-binary",
    "agent-skills-collection",
    "agentic-platform",
    "web-application",
    "desktop-application",
    "embedded-firmware",
    "install-script-fetcher",
    "specialized-domain-tool",
    "other",
})

# Provisional categories (n=1 representation in V1.2 catalog as of 2026-05-01).
# Promote to stable at n>=2 V1.2 scans classifying cleanly per design §3 +
# directive #11 in CONSOLIDATION §3. Phase 3 chooses tracking mechanism — for
# now, this is a static frozenset; future implementation can derive from the
# catalog or maintain a separate counter.
PROVISIONAL_CATEGORIES = frozenset({
    "embedded-firmware",         # WLED only
    "install-script-fetcher",    # caveman (V2.4-era; not in V1.2 catalog)
    # Note: agent-skills-collection has skills (V1.2) + gstack (V2.4-era);
    # specialized-domain-tool has freerouting + Kronos (n=2). Both stable.
})

# Topics that strongly indicate a desktop-application shape.
# Excludes vpn/proxy/tunnel/anticensorship — those are CLI-server tools per the
# Xray-core classification (network proxies run as daemons, not GUIs).
_DESKTOP_TOPICS = frozenset({
    "terminal", "terminal-emulator", "terminal-emulators",
    "chrome-extension", "firefox-extension", "browser-extension",
    "quicklook", "explorer-extension", "shell-extension",
    "gui", "gnome", "kde", "macos-app", "windows-app",
})

# Workflow basenames that indicate desktop GUI packaging (used as a secondary
# signal when topics are absent — e.g. ghostty's empty topic list but presence
# of flatpak.yml + snap.yml in .github/workflows/). Exact basename match — not
# substring — to avoid false matches like "create-snapshot.yml" containing
# "snap" or "macos-build.yml" being treated as GUI when it's just cross-
# platform CLI build (kanata-shape).
_DESKTOP_WORKFLOW_BASENAMES = frozenset({
    "flatpak.yml", "flatpak.yaml",
    "snap.yml", "snap.yaml",
    "appimage.yml", "appimage.yaml",
    "dmg.yml", "dmg.yaml",
    "msix.yml", "msix.yaml",
    "winget.yml", "winget.yaml",
})

# Languages where the canonical published artifact is a CLI binary (Cargo bin,
# Go binary, Ruby gem with bin entry, native compiled). Used by Step 6 cli-
# binary heuristic to gate the trigger — JS/TS published packages are
# library-package by default since release-asset distribution is rare in npm.
_CLI_DEFAULT_LANGUAGES = frozenset({
    "go", "rust", "ruby", "zig", "haskell", "ocaml", "elixir", "crystal",
    "c", "c++",  # uncommon for CLIs at scale, but native binaries are CLI-shape
})

# Topics indicating embedded firmware / IoT.
_FIRMWARE_TOPICS = frozenset({
    "esp32", "esp8266", "arduino", "platformio",
    "firmware", "embedded", "iot", "microcontroller",
})

# Topics indicating specialized-domain tools (EDA, ML, document parsing, etc.).
_DOMAIN_TOPICS = frozenset({
    # EDA / CAD
    "pcb", "pcb-design", "eda", "cad", "autorouter", "autorouting",
    "router", "routing", "dsn", "specctra",
    # ML / data science
    "ml", "machine-learning", "deep-learning",
    "foundation-model", "pretrained", "huggingface", "transformers",
    "dataset", "checkpoint", "pytorch", "tensorflow",
    # Document / format conversion
    "document-conversion", "document-parser", "format-converter",
    "pdf", "docx", "epub", "markdown-converter",
    # Bioinformatics / scientific
    "bioinformatics", "scientific-computing", "computational-biology",
})

# Topics indicating reverse-engineered platform integrations.
_REVERSE_ENGINEERED_TOPICS = frozenset({
    "reverse-engineering", "reverse-engineered", "unofficial-api",
    "whatsapp-web",  # Baileys-shape — RE'd platform clients
})

# README phrases indicating reverse-engineered scope (case-insensitive substring).
_REVERSE_ENGINEERED_README_PHRASES = (
    "unofficial",
    "reverse-engineered",
    "reverse engineered",
    "tos may apply",
    "terms of service may apply",
    "this client is not affiliated",
    "not affiliated with",
)

# Topics indicating elevated-permissions tooling (kernel, system, hardware,
# input devices, terminal, browser-extension permissions, network sockets).
_PRIVILEGED_TOOL_TOPICS = frozenset({
    "kernel", "kernel-module", "driver", "system",
    "interception-driver", "kernel-adjacent",
    "firmware", "esp32", "esp8266", "iot", "embedded", "arduino",
    "keyboard", "mouse", "input", "keyboard-layout", "keyboard-remapping",
    "terminal", "terminal-emulator", "terminal-emulators", "shell",
    "chrome-extension", "firefox-extension", "browser-extension",
    "shell-extension", "explorer-extension", "quicklook",
    "vpn", "proxy", "tunnel", "anticensorship",
    "ssh", "ssh-client", "ssh-server",
})


class ShapeClassification(NamedTuple):
    """Output of classify_shape() per design §3 + §4.

    `category` is one of SHAPE_CATEGORIES (9 closed-enum values + 'other').
    `confidence` is debug-only — no rule reads it (directive #13).
      Tracked in form.json for audit (correlation between low-confidence
      classifications and override spikes).
    `matched_rule` is a short string explaining which heuristic branch fired
      (e.g. "C++ + esp32 topic"). Useful for audit + debugging.
    """
    category: str
    is_reverse_engineered: bool
    is_privileged_tool: bool
    is_solo_maintained: bool
    confidence: str
    matched_rule: str


def _safe_dict(obj) -> dict:
    """Return obj if it's a dict, else {}. Avoids None-attribute errors when
    walking phase_1_raw_capture nested fields."""
    return obj if isinstance(obj, dict) else {}


def _safe_list(obj) -> list:
    return obj if isinstance(obj, list) else []


def _topic_set(repo_metadata: dict) -> frozenset[str]:
    return frozenset(_safe_list(repo_metadata.get("topics")))


def _detect_reverse_engineered(form: dict) -> bool:
    """True when README disclaimer phrases or topics indicate reverse-engineered
    platform-API library shape (per design §3 cross-shape modifier).

    Reads phase_1_raw_capture only. Currently uses topics as the primary signal
    since README text isn't stored in phase_1_raw_capture (the harness extracts
    code patterns + structured metadata, not full README). README-text matching
    is left available for callers that have README in hand."""
    p1 = _safe_dict(form.get("phase_1_raw_capture"))
    repo_meta = _safe_dict(p1.get("repo_metadata"))
    topics = _topic_set(repo_meta)
    if topics & _REVERSE_ENGINEERED_TOPICS:
        return True
    return False


def _detect_privileged_tool(form: dict) -> bool:
    """True when the tool runs with elevated permissions: kernel/driver,
    firmware, input device, terminal emulator, browser extension, network
    proxy/VPN, shell extender (per design §3 cross-shape modifier).

    Topic-based detection from phase_1_raw_capture.repo_metadata.topics.
    Repos with empty topics (e.g. ghostty) may miss this detector; the override
    mechanism is the safety net for those cases.

    PHASE 3 IMPLEMENTATION DRIFT (vs design §3 expected table):
      Design §3 listed 6 expected privileged_tool=True scans on V1.2 catalog:
        ghostty, wezterm, kanata, QuickLook, WLED, browser_terminal.
      This implementation produces 6 TRUE on the same catalog but with set
      difference:
        + Xray-core fires TRUE (vpn/proxy/tunnel topics — privileged daemon)
        - ghostty fires FALSE (empty topics; can't detect terminal-emulator
          shape from phase_1 alone)
      Both calls are defensible: Xray-core IS privileged (network proxy
      daemon, often runs as root for low-port binding); ghostty IS privileged
      (terminal emulator handles SSH keys + shell history). The design table
      was illustrative — topic-based detection inherently can't see
      empty-topics repos. Phase 4 LLM override handles ghostty's case.
      Tracked here so the deviation doesn't read as a bug six months from now."""
    p1 = _safe_dict(form.get("phase_1_raw_capture"))
    repo_meta = _safe_dict(p1.get("repo_metadata"))
    topics = _topic_set(repo_meta)
    if topics & _PRIVILEGED_TOOL_TOPICS:
        return True
    return False


def _has_desktop_packaging_workflows(executable_files: list) -> bool:
    """Detect desktop-distribution CI workflows by exact basename match
    (flatpak.yml, snap.yml, appimage.yml, dmg.yml, msix.yml, winget.yml).

    Used as a secondary signal for desktop-application when topics are absent
    (e.g. ghostty's empty topic list + presence of flatpak.yml + snap.yml).
    Exact-basename match deliberate — substring `snap` would false-match
    `create-snapshot.yml`, and `macos` would false-match `macos-build.yml`
    (a normal cross-platform CLI build workflow, not a GUI packaging step)."""
    for entry in _safe_list(executable_files):
        if not isinstance(entry, dict):
            continue
        path = (entry.get("path") or "").lower()
        basename = path.rsplit("/", 1)[-1]
        if basename in _DESKTOP_WORKFLOW_BASENAMES:
            return True
    return False


def _is_publishable_package_manifest(manifest_files: list) -> bool:
    """True when a package-publish manifest is present (npm package.json,
    Rust Cargo.toml, Ruby gemspec, Python pyproject.toml, Go module). False
    when only dependency-tracking manifests are present (requirements.txt,
    Pipfile, package-lock.json alone)."""
    PUBLISHABLE_FILENAMES = {
        "package.json", "pyproject.toml", "setup.py",
        "cargo.toml", "gemfile", "*.gemspec",
        "go.mod",
    }
    for entry in _safe_list(manifest_files):
        if not isinstance(entry, dict):
            continue
        path = (entry.get("path") or "").lower()
        # Match top-level publish manifests (not lockfiles, not nested deps)
        basename = path.rsplit("/", 1)[-1]
        if basename in {"package.json", "pyproject.toml", "setup.py",
                        "cargo.toml", "gemfile", "go.mod"}:
            return True
        if basename.endswith(".gemspec"):
            return True
    return False


def classify_shape(form: dict) -> ShapeClassification:
    """Classify a scan form into a shape category + cross-shape modifiers.

    Reads from form.phase_1_raw_capture ONLY (per Codex FIX-NOW directive #2).
    Does NOT consult phase_4_structured_llm.catalog_metadata.shape — phase
    boundary preserved.

    Returns ShapeClassification with deterministic output: same form always
    produces same classification. When no clean match, returns
    category='other' with confidence='low'; the override mechanism handles
    that case via Phase 4 LLM-authored cell colors with override_reason.
    """
    p1 = _safe_dict(form.get("phase_1_raw_capture"))
    repo_meta = _safe_dict(p1.get("repo_metadata"))
    code_patterns = _safe_dict(p1.get("code_patterns"))
    deps = _safe_dict(p1.get("dependencies"))
    install_script = _safe_dict(p1.get("install_script_analysis"))
    releases = _safe_dict(p1.get("releases"))
    # V1.2 bundle shape: contributors = {top_contributors: [...], total_contributor_count: N}
    # Older shape was a bare list. Accept both for backward compatibility.
    contributors_raw = p1.get("contributors")
    if isinstance(contributors_raw, dict):
        contributors = _safe_list(contributors_raw.get("top_contributors"))
    else:
        contributors = _safe_list(contributors_raw)

    primary_lang = (repo_meta.get("primary_language") or "").lower()
    topics = _topic_set(repo_meta)
    agent_rule_files = _safe_list(code_patterns.get("agent_rule_files"))
    executable_files = _safe_list(code_patterns.get("executable_files"))
    manifest_files = _safe_list(deps.get("manifest_files"))
    install_scripts = _safe_list(install_script.get("scripts"))
    releases_count = (
        releases.get("count")
        if isinstance(releases.get("count"), int)
        else len(_safe_list(releases.get("entries")))
    )

    # Cross-shape modifiers (computed once, returned regardless of category)
    is_re = _detect_reverse_engineered(form)
    is_priv = _detect_privileged_tool(form)
    solo_meta = compute_solo_maintainer(contributors)
    is_solo = bool(solo_meta.get("is_solo"))

    def _result(category: str, confidence: str, matched_rule: str) -> ShapeClassification:
        return ShapeClassification(
            category=category,
            is_reverse_engineered=is_re,
            is_privileged_tool=is_priv,
            is_solo_maintained=is_solo,
            confidence=confidence,
            matched_rule=matched_rule,
        )

    # ---------------------------------------------------------------------
    # Step 1 — embedded-firmware (clearest topic signal: ESP/Arduino + C/C++)
    # ---------------------------------------------------------------------
    if (topics & _FIRMWARE_TOPICS) and primary_lang in {"c", "c++"}:
        return _result(
            "embedded-firmware",
            confidence="high",
            matched_rule="C/C++ primary + firmware/iot/esp topic",
        )

    # ---------------------------------------------------------------------
    # Step 2 — agent-skills-collection (no-tool-fingerprint signature)
    #
    # The skills-collection shape has a distinctive negative footprint: no
    # release artifacts, no package manifest, no compiled executables — but
    # at least one agent-rule file (CLAUDE.md / AGENTS.md / SKILL.md). This
    # disambiguates skills (no fingerprint, primary=Shell or Markdown) from
    # tools that happen to ship AGENTS.md sub-directory contributor guides
    # (ghostty: 7 AGENTS.md but Zig + 18 exec files + release → NOT skills).
    # ---------------------------------------------------------------------
    if (
        len(agent_rule_files) >= 1
        and len(executable_files) == 0
        and len(manifest_files) == 0
        and releases_count == 0
        and primary_lang in {"shell", "markdown", ""}
    ):
        return _result(
            "agent-skills-collection",
            confidence="high",
            matched_rule="rule-files present + no exec/manifest/release fingerprint",
        )
    # Markdown-canonical skills (gstack-shape; not in V1.2 catalog but covered)
    if primary_lang == "markdown" and len(agent_rule_files) >= 3:
        return _result(
            "agent-skills-collection",
            confidence="high",
            matched_rule="Markdown primary + >=3 agent-rule files",
        )

    # ---------------------------------------------------------------------
    # Step 3 — desktop-application via TOPIC (high-confidence, narrow)
    # Only fires on explicit GUI/extension/shell-extension topics. Workflow-
    # based fallback (Step 5) handles cases with empty topic lists.
    # ---------------------------------------------------------------------
    if topics & _DESKTOP_TOPICS:
        return _result(
            "desktop-application",
            confidence="high",
            matched_rule="desktop topic (terminal/extension/quicklook/etc.)",
        )
    # GUI-canonical languages — Swift / Objective-C indicate native desktop
    # apps. C# is ambiguous (could be desktop GUI or server) — gated below
    # on releases + no-domain-topic condition handled by Step 5b.
    if primary_lang in {"swift", "objective-c"} and releases_count >= 5:
        return _result(
            "desktop-application",
            confidence="medium",
            matched_rule=f"{primary_lang} + release artifacts present",
        )

    # ---------------------------------------------------------------------
    # Step 4 — specialized-domain-tool via TOPIC (must fire BEFORE workflow-
    # fallback in Step 5; domain topics like 'pcb' are a stronger signal
    # than 'release-tag.yml exists' for shape inference).
    # ---------------------------------------------------------------------
    if topics & _DOMAIN_TOPICS:
        return _result(
            "specialized-domain-tool",
            confidence="high",
            matched_rule="domain topic (EDA/ML/document-conversion/etc.)",
        )

    # ---------------------------------------------------------------------
    # Step 4b — Python-no-fingerprint specialized-domain-tool catch
    #
    # Python repos with only requirements.txt (dependency-tracking, NOT
    # publishable), no executables, no releases — most commonly research /
    # ML / domain-specific tooling (Kronos-shape: Python ML library, Hugging
    # Face-hosted weights, README-driven install instructions).
    # Discriminates from library-package because pyproject.toml/setup.py
    # would mark it as publishable; pure requirements.txt + install-script
    # presence is a domain-tool footprint, not a library footprint.
    # ---------------------------------------------------------------------
    if (
        primary_lang == "python"
        and len(executable_files) == 0
        and releases_count == 0
        and not _is_publishable_package_manifest(manifest_files)
    ):
        return _result(
            "specialized-domain-tool",
            confidence="medium",
            matched_rule="Python + no exec/release/publish-manifest (research/ML shape)",
        )

    # ---------------------------------------------------------------------
    # Step 5 — desktop-application via WORKFLOW fallback
    # Empty-topics repos like ghostty (Zig terminal emulator) detected via
    # presence of GUI-distribution workflow basenames (flatpak.yml,
    # snap.yml, etc.). Tightened to exact-basename match to avoid false
    # positives from `create-snapshot.yml` / `macos-build.yml`.
    # ---------------------------------------------------------------------
    if _has_desktop_packaging_workflows(executable_files):
        return _result(
            "desktop-application",
            confidence="medium",
            matched_rule="desktop-packaging workflows (flatpak/snap/AppImage/dmg)",
        )
    # C# + many releases — typically desktop apps (QuickLook-class). Fires
    # only if Step 3/4 didn't catch it via topic — defensive fallback.
    if primary_lang == "c#" and releases_count >= 5:
        return _result(
            "desktop-application",
            confidence="medium",
            matched_rule="C# + release artifacts present",
        )

    # ---------------------------------------------------------------------
    # Step 6 — install-script-fetcher (curl-pipe-from-main pattern)
    # ---------------------------------------------------------------------
    if (
        len(install_scripts) >= 1
        and releases_count == 0
        and len(executable_files) == 0
        and len(manifest_files) == 0
    ):
        return _result(
            "install-script-fetcher",
            confidence="medium",
            matched_rule="install scripts + no releases/exec/manifest",
        )

    # ---------------------------------------------------------------------
    # Step 7 — cli-binary (language-canonical: Go/Rust/Ruby/Zig/Haskell/etc.)
    #
    # Released-asset count is unreliable as a discriminator — npm/Cargo/
    # Ruby release entries often have asset_count=0 because the binary lives
    # at the package registry, not on GitHub release pages. The reliable
    # signal is the language: Go/Rust/Ruby/etc. published packages with
    # >=5 releases + Gemfile/go.mod/Cargo.toml are typically CLI binaries.
    # JS/TS is excluded — npm publishing is library-default (Baileys-shape).
    # ---------------------------------------------------------------------
    if (
        releases_count >= 5
        and _is_publishable_package_manifest(manifest_files)
        and primary_lang in _CLI_DEFAULT_LANGUAGES
    ):
        return _result(
            "cli-binary",
            confidence="high",
            matched_rule=f"{primary_lang} + >=5 releases + publishable manifest",
        )

    # ---------------------------------------------------------------------
    # Step 8 — library-package (publishable manifest, no CLI/desktop fingerprint)
    #
    # Languages where package-manager-distributed library is the default
    # shape — npm/TypeScript packages especially. Catches Baileys (JS +
    # package.json + 42 releases but no platform binaries → library).
    # ---------------------------------------------------------------------
    if _is_publishable_package_manifest(manifest_files):
        return _result(
            "library-package",
            confidence="medium",
            matched_rule="publishable manifest, library-canonical shape",
        )

    # ---------------------------------------------------------------------
    # Step 8 — agentic-platform / Step 9 — web-application
    #
    # No V1.2 catalog scans match these cleanly (postiz-app + Archon are
    # V2.4-era and have .md bundles, not V1.2 .json). Heuristics deferred
    # to first hit — fall through to other for now.
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # Step 10 — Fallback: 'other' with low confidence
    #
    # Per design §4: when classify_shape cannot decide cleanly, returns
    # ('other', confidence='low'). Phase 4 LLM author override-explained
    # mechanism handles cell colors via the existing override path. This
    # preserves phase boundary (no fallback to phase_4_structured_llm).
    # ---------------------------------------------------------------------
    return _result(
        "other",
        confidence="low",
        matched_rule="catch-all (no heuristic branch matched)",
    )


# ===========================================================================
# Cell evaluators (RULE-1 through RULE-9; Q2 explicit-deferral per directive #16)
# ===========================================================================
#
# Each evaluator returns a CellEvaluation with rule_id REQUIRED. The 4 evaluators
# implement first-match-wins precedence per design §2:
#   1. Auto-fire trips (short-circuit on first match)
#   2. Shape modifiers
#   3. Sample-floor / context modifiers
#   4. Base rule table (current calibration baseline)
#   5. Fallback (rule_id='FALLBACK')


class CellEvaluation(NamedTuple):
    """Output of evaluate_q1/q2/q3/q4 per design §10.

    `rule_id` is REQUIRED — values are RULE-1 through RULE-10 or 'FALLBACK'.
    Validator enforces presence (directive #14).
    `auto_fire` distinguishes immediate trips (RULE-6 + RULE-7/8/9) from
    base-table evaluation.
    `template_vars` carry signal values for the short_answer template renderer."""
    color: str
    short_answer_template_key: str
    template_vars: dict
    rule_id: str
    auto_fire: bool


def evaluate_q1(signals: dict, shape: ShapeClassification) -> CellEvaluation:
    """Q1 — 'Does anyone check the code?'

    Order: RULE-1 (governance-floor softener) → RULE-2 (review-rate softener)
    → RULE-3 (narrow tie-breaker for non-privileged solo OSS with positive
    signals) → base-table fallback.
    """
    has_codeowners = bool(signals.get("has_codeowners"))
    has_ruleset_protection = bool(signals.get("has_ruleset_protection"))
    has_branch_protection = bool(signals.get("has_branch_protection"))
    rules_on_default_count = int(signals.get("rules_on_default_count") or 0)
    formal = float(signals.get("formal_review_rate") or 0)
    any_rev = float(signals.get("any_review_rate") or 0)
    has_codeql = bool(signals.get("has_codeql"))
    releases_count = int(signals.get("releases_count") or 0)
    pr_sample_size = int(signals.get("pr_sample_size") or 0)

    has_any_branch_protection = has_branch_protection or has_ruleset_protection

    # RULE-1 — governance-floor softener (FIRM)
    # CODEOWNERS + ruleset + rules-on-default present → amber, not red.
    if has_codeowners and has_ruleset_protection and rules_on_default_count > 0:
        concentration_qualifier = (
            "concentration risk remains" if shape.is_solo_maintained
            else "review-rate signal alone is below threshold"
        )
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q1.amber.governance_present",
            template_vars={
                "concentration_qualifier": concentration_qualifier,
                "is_solo_maintained": shape.is_solo_maintained,
            },
            rule_id="RULE-1",
            auto_fire=False,
        )

    # RULE-2 — review-rate softener (FIRM)
    # Voluntary review rate above OSS-median → amber, not red.
    if formal >= 30 or any_rev >= 60:
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q1.amber.review_rate_present",
            template_vars={
                "formal_review_rate": formal,
                "any_review_rate": any_rev,
                "pr_sample_size": pr_sample_size,
            },
            rule_id="RULE-2",
            auto_fire=False,
        )

    # RULE-3 — narrow tie-breaker for non-privileged solo OSS with positive
    # signals. Captures the kamal pattern (solo + non-privileged + compound
    # positive evidence).
    if (
        shape.is_solo_maintained
        and not shape.is_privileged_tool
        and (has_codeql or releases_count >= 20)
    ):
        positive_signal = "CodeQL on" if has_codeql else f"{releases_count} releases"
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q1.amber.solo_with_positive_signals",
            template_vars={
                "positive_signal": positive_signal,
                "releases_count": releases_count,
                "has_codeql": has_codeql,
            },
            rule_id="RULE-3",
            auto_fire=False,
        )

    # FALLBACK — base-table behavior matches legacy compute_scorecard_cells
    # for the cases none of RULE-1/2/3 fired. Solo + low any-review = red;
    # otherwise amber/red per legacy thresholds.
    is_solo_maintainer = shape.is_solo_maintained
    if (formal < 10 and not has_any_branch_protection and not has_codeowners):
        return CellEvaluation(
            color="red",
            short_answer_template_key="q1.red.no_governance",
            template_vars={"formal": formal},
            rule_id="FALLBACK",
            auto_fire=False,
        )
    if any_rev < 30 or (is_solo_maintainer and any_rev < 40):
        return CellEvaluation(
            color="red",
            short_answer_template_key="q1.red.no_governance",
            template_vars={"any_review_rate": any_rev},
            rule_id="FALLBACK",
            auto_fire=False,
        )
    if any_rev >= 50 or formal >= 20:
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q1.amber.review_rate_present",
            template_vars={
                "formal_review_rate": formal,
                "any_review_rate": any_rev,
                "pr_sample_size": pr_sample_size,
            },
            rule_id="FALLBACK",
            auto_fire=False,
        )
    return CellEvaluation(
        color="red",
        short_answer_template_key="q1.red.no_governance",
        template_vars={"formal": formal, "any_review_rate": any_rev},
        rule_id="FALLBACK",
        auto_fire=False,
    )


def evaluate_q2(signals: dict, shape: ShapeClassification) -> CellEvaluation:
    """Q2 — 'Do they fix problems quickly?'

    Per directive #16 (R3 pre-archive doc fix): NO RULE CHANGES. Q2 is
    explicitly deferred — audit found Q2 well-calibrated, only 2 of 10 V1.2
    overrides were Q2 (both addressed by V1.2.x signal widening). Phase 1.5
    re-entry trigger: >=3 Q2 overrides in next 5 wild scans, OR Phase 1
    re-render audit miscalls.

    This function reproduces the legacy Q2 logic from compute_scorecard_cells
    and emits rule_id='FALLBACK' since no Q2 rule fires by design.
    """
    open_security_issue_count = int(signals.get("open_security_issue_count") or 0)
    oldest_cve_pr_age_days = signals.get("oldest_cve_pr_age_days")
    oldest_open_security_item_age_days = signals.get("oldest_open_security_item_age_days")
    closed_fix_lag_days = signals.get("closed_fix_lag_days")

    cve_age = max(oldest_cve_pr_age_days or 0, oldest_open_security_item_age_days or 0)

    if open_security_issue_count == 0 and cve_age <= 7:
        if closed_fix_lag_days is not None and closed_fix_lag_days > 3:
            return CellEvaluation(
                color="amber",
                short_answer_template_key="q2.amber.closed_fix_lag",
                template_vars={"closed_fix_lag_days": closed_fix_lag_days},
                rule_id="FALLBACK",
                auto_fire=False,
            )
        return CellEvaluation(
            color="green",
            short_answer_template_key="q2.green.no_open",
            template_vars={},
            rule_id="FALLBACK",
            auto_fire=False,
        )
    if open_security_issue_count <= 3 and cve_age <= 14:
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q2.amber.few_open",
            template_vars={
                "open_security_issue_count": open_security_issue_count,
                "cve_age": cve_age,
            },
            rule_id="FALLBACK",
            auto_fire=False,
        )
    return CellEvaluation(
        color="red",
        short_answer_template_key="q2.red.many_open_or_old",
        template_vars={
            "open_security_issue_count": open_security_issue_count,
            "cve_age": cve_age,
        },
        rule_id="FALLBACK",
        auto_fire=False,
    )


def evaluate_q3(signals: dict, shape: ShapeClassification) -> CellEvaluation:
    """Q3 — 'Do they tell you about problems?'

    Order: RULE-4 (sample-floor; HIGHEST-VALUE — fixes skills-class) →
    RULE-5 (ruleset-as-disclosure floor; hygiene) → base-table fallback.
    """
    repo_age_days = int(signals.get("repo_age_days") or 0)
    total_merged_lifetime = int(signals.get("total_merged_lifetime") or 0)
    has_security_policy = bool(signals.get("has_security_policy"))
    has_contributing_guide = bool(signals.get("has_contributing_guide"))
    has_ruleset_protection = bool(signals.get("has_ruleset_protection"))
    published_advisory_count = int(signals.get("published_advisory_count") or 0)
    has_silent_fixes = bool(signals.get("has_silent_fixes"))

    # RULE-4 — sample-floor (HIGHEST-VALUE — addresses skills-class)
    # repo_age_days < 180 AND total_merged_lifetime < 5 → too young to grade.
    if repo_age_days > 0 and repo_age_days < 180 and total_merged_lifetime < 5:
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q3.amber.sample_floor",
            template_vars={
                "repo_age_days": repo_age_days,
                "total_merged_lifetime": total_merged_lifetime,
            },
            rule_id="RULE-4",
            auto_fire=False,
        )

    # RULE-5 — ruleset-as-disclosure floor (HYGIENE)
    # ruleset protection + published advisories → amber (already amber via
    # base table; this codifies why).
    if has_ruleset_protection and published_advisory_count > 0:
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q3.amber.ruleset_disclosed",
            template_vars={"published_advisory_count": published_advisory_count},
            rule_id="RULE-5",
            auto_fire=False,
        )

    # FALLBACK — base-table from legacy compute_scorecard_cells
    if has_security_policy and published_advisory_count > 0 and not has_silent_fixes:
        return CellEvaluation(
            color="green",
            short_answer_template_key="q3.green.full_disclosure",
            template_vars={"published_advisory_count": published_advisory_count},
            rule_id="FALLBACK",
            auto_fire=False,
        )
    if (
        has_security_policy
        or has_contributing_guide
        or (published_advisory_count > 0 and not has_silent_fixes)
    ):
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q3.amber.partial_disclosure",
            template_vars={
                "has_security_policy": has_security_policy,
                "has_contributing_guide": has_contributing_guide,
                "published_advisory_count": published_advisory_count,
            },
            rule_id="FALLBACK",
            auto_fire=False,
        )
    return CellEvaluation(
        color="red",
        short_answer_template_key="q3.red.no_disclosure",
        template_vars={},
        rule_id="FALLBACK",
        auto_fire=False,
    )


def evaluate_q4(signals: dict, shape: ShapeClassification) -> CellEvaluation:
    """Q4 — 'Is it safe out of the box?'

    Order: RULE-6 (Q4 auto-fire extension; FIRM) → RULE-7/8/9 (n=1 candidates,
    promotion-gated; do NOT fire until both n>=2 confirming scans AND harness
    signal landed) → base-table fallback.

    RULE-7/8/9 are intentionally inert in the current implementation: the
    promotion-gate semantics require BOTH evidence + harness work before they
    activate. Phase 1.5 wild-scan progression triggers the promotion.
    """
    deser_hits = int(signals.get("deserialization_hit_count") or 0)
    cmd_inj_hits = int(signals.get("cmd_injection_hit_count") or 0)
    exec_hits = int(signals.get("exec_hit_count") or 0)
    tool_loads_user_files = bool(signals.get("tool_loads_user_files"))
    has_unverified_install_path = bool(signals.get("has_unverified_install_path"))
    all_channels_pinned = bool(signals.get("all_channels_pinned"))
    artifact_verified = bool(signals.get("artifact_verified"))
    has_warning_on_install_path = bool(signals.get("has_warning_on_install_path"))
    has_critical_on_default_path_kw = bool(signals.get("has_critical_on_default_path"))

    # RULE-6 — Q4 auto-fire extension (FIRM; extends V13-3 C5)
    # Three sub-conditions, any of which fires red:
    #   - deserialization >= 3 + tool_loads_user_files (existing V13-3 C5)
    #   - cmd_injection >= 1 + tool_loads_user_files (NEW)
    #   - exec >= 1 + has_unverified_install_path (NEW)
    rule_6_fires = False
    rule_6_pattern = None
    rule_6_top_file = None
    rule_6_hit_count = 0
    if deser_hits >= 3 and tool_loads_user_files:
        rule_6_fires = True
        rule_6_pattern = "unsafe deserialization"
        rule_6_hit_count = deser_hits
        rule_6_top_file = signals.get("deserialization_top_file") or ""
    elif cmd_inj_hits >= 1 and tool_loads_user_files:
        rule_6_fires = True
        rule_6_pattern = "command injection"
        rule_6_hit_count = cmd_inj_hits
        rule_6_top_file = signals.get("cmd_injection_top_file") or ""
    elif exec_hits >= 1 and has_unverified_install_path:
        rule_6_fires = True
        rule_6_pattern = "exec on unverified install path"
        rule_6_hit_count = exec_hits
        rule_6_top_file = signals.get("exec_top_file") or ""

    if rule_6_fires:
        return CellEvaluation(
            color="red",
            short_answer_template_key="q4.red.exec_pattern",
            template_vars={
                "primary_pattern": rule_6_pattern,
                "hit_count": rule_6_hit_count,
                "top_file": rule_6_top_file,
            },
            rule_id="RULE-6",
            auto_fire=True,
        )

    # RULE-7/8/9 — n=1 candidates with promotion gates. Currently INERT:
    # design §5 promotion-gate semantics require BOTH (a) n>=2 confirming
    # scans AND (b) the harness-side detection signal is implemented and
    # tested. Until both land, the rules don't activate — they fall through
    # to the base table or to Phase 4 LLM-authored override.
    #   RULE-7: shape == embedded-firmware AND no_auth_default OR cors_wildcard
    #   RULE-8: install-doc URL TLD-deviation (typosquat)
    #   RULE-9: shape == library-package AND is_reverse_engineered AND ToS
    # No-op until promotion. See Phase 1.5 wild-scan trigger.

    # Caller-supplied has_critical_on_default_path (Phase 4 LLM override or
    # legacy explicit kwarg). Treated as auto-fire for compatibility.
    if has_critical_on_default_path_kw:
        return CellEvaluation(
            color="red",
            short_answer_template_key="q4.red.exec_pattern",
            template_vars={
                "primary_pattern": "Critical finding on default path",
                "hit_count": 0,
                "top_file": "",
            },
            rule_id="FALLBACK",
            auto_fire=True,
        )

    # FALLBACK — base-table from legacy compute_scorecard_cells
    if all_channels_pinned and artifact_verified and not has_warning_on_install_path:
        return CellEvaluation(
            color="green",
            short_answer_template_key="q4.green.verified",
            template_vars={},
            rule_id="FALLBACK",
            auto_fire=False,
        )
    if (
        has_warning_on_install_path
        or not all_channels_pinned
        or not artifact_verified
    ):
        return CellEvaluation(
            color="amber",
            short_answer_template_key="q4.amber.install_warns",
            template_vars={"trust_qualifier": "install path has friction signals"},
            rule_id="FALLBACK",
            auto_fire=False,
        )
    return CellEvaluation(
        color="amber",
        short_answer_template_key="q4.amber.install_warns",
        template_vars={},
        rule_id="FALLBACK",
        auto_fire=False,
    )


def compute_scorecard_cells_v2(form: dict, signals: dict | None = None) -> dict:
    """Compute the 4 scorecard cells using the calibration v2 rule table.

    Args:
        form: full scan form (read for shape classification).
        signals: derived signal dict that the rule evaluators consume. If None,
            constructed from `form` heuristically (best-effort defaults).

    Returns dict mirroring compute_scorecard_cells's V1.2 advisory shape, with:
      - color: red/amber/green
      - short_answer: one of 'No' / 'Partly' / 'Yes' (template_key→short_answer
                      derivation deferred to renderer; this function emits the
                      legacy short_answer for backwards compat)
      - signals: V1.2 SIGNAL_IDS list
      - rule_id: REQUIRED — RULE-1..RULE-10 or FALLBACK (directive #14)
      - shape_classification: full ShapeClassification namedtuple as dict
    """
    shape = classify_shape(form)
    sigs = signals or _derive_signals_from_form(form)

    q1 = evaluate_q1(sigs, shape)
    q2 = evaluate_q2(sigs, shape)
    q3 = evaluate_q3(sigs, shape)
    q4 = evaluate_q4(sigs, shape)

    color_to_answer = {"red": "No", "amber": "Partly", "green": "Yes"}

    def _cell(eval_: CellEvaluation, sig_list: list) -> dict:
        return {
            "color": eval_.color,
            "short_answer": color_to_answer.get(eval_.color, "Partly"),
            "rule_id": eval_.rule_id,
            "auto_fire": eval_.auto_fire,
            "short_answer_template_key": eval_.short_answer_template_key,
            "template_vars": eval_.template_vars,
            "signals": sig_list,
        }

    return {
        "shape_classification": {
            "category": shape.category,
            "is_reverse_engineered": shape.is_reverse_engineered,
            "is_privileged_tool": shape.is_privileged_tool,
            "is_solo_maintained": shape.is_solo_maintained,
            "confidence": shape.confidence,
            "matched_rule": shape.matched_rule,
        },
        "does_anyone_check_the_code": _cell(q1, [
            {"id": "q1_formal_review_rate", "value": sigs.get("formal_review_rate")},
            {"id": "q1_any_review_rate", "value": sigs.get("any_review_rate")},
            {"id": "q1_has_branch_protection", "value": sigs.get("has_branch_protection")},
            {"id": "q1_has_ruleset_protection", "value": sigs.get("has_ruleset_protection")},
            {"id": "q1_has_codeowners", "value": sigs.get("has_codeowners")},
            {"id": "q1_is_solo_maintainer", "value": shape.is_solo_maintained},
        ]),
        "do_they_fix_problems_quickly": _cell(q2, [
            {"id": "q2_open_security_issue_count", "value": sigs.get("open_security_issue_count")},
            {"id": "q2_oldest_open_cve_pr_age_days", "value": sigs.get("oldest_cve_pr_age_days")},
            {"id": "q2_oldest_open_security_item_age_days", "value": sigs.get("oldest_open_security_item_age_days")},
            {"id": "q2_closed_fix_lag_days", "value": sigs.get("closed_fix_lag_days")},
        ]),
        "do_they_tell_you_about_problems": _cell(q3, [
            {"id": "q3_has_security_policy", "value": sigs.get("has_security_policy")},
            {"id": "q3_has_contributing_guide", "value": sigs.get("has_contributing_guide")},
            {"id": "q3_published_advisory_count", "value": sigs.get("published_advisory_count")},
            {"id": "q3_has_silent_fixes", "value": sigs.get("has_silent_fixes")},
        ]),
        "is_it_safe_out_of_the_box": _cell(q4, [
            {"id": "q4_all_channels_pinned", "value": sigs.get("all_channels_pinned")},
            {"id": "q4_artifact_verified", "value": sigs.get("artifact_verified")},
            {"id": "q4_has_critical_on_default_path", "value": sigs.get("has_critical_on_default_path")},
            {"id": "q4_has_warning_on_install_path", "value": sigs.get("has_warning_on_install_path")},
        ]),
    }


def _derive_signals_from_form(form: dict) -> dict:
    """Best-effort signal derivation from a form's phase_1_raw_capture +
    phase_3_computed inputs.

    Used by compute_scorecard_cells_v2 when caller doesn't supply explicit
    signals (e.g. regression tests against catalog bundles). Real scan
    drivers should construct the signal dict explicitly using harness
    output + derive_* helpers."""
    p1 = _safe_dict(form.get("phase_1_raw_capture"))
    p3 = _safe_dict(form.get("phase_3_computed"))

    pr_review = _safe_dict(p1.get("pr_review"))
    branch_protection = _safe_dict(p1.get("branch_protection"))
    codeowners = _safe_dict(p1.get("codeowners"))
    code_patterns = _safe_dict(p1.get("code_patterns"))
    dangerous = _safe_dict(code_patterns.get("dangerous_primitives"))
    issues_and_commits = _safe_dict(p1.get("issues_and_commits"))
    advisories = _safe_dict(p1.get("security_advisories"))
    community = _safe_dict(p1.get("community_profile"))
    repo_meta = _safe_dict(p1.get("repo_metadata"))
    artifact_verification = _safe_dict(p1.get("artifact_verification"))
    contributors_raw = p1.get("contributors")
    if isinstance(contributors_raw, dict):
        contributors = _safe_list(contributors_raw.get("top_contributors"))
    else:
        contributors = _safe_list(contributors_raw)

    rules_on_default = _safe_dict(branch_protection.get("rules_on_default"))
    classic = _safe_dict(branch_protection.get("classic"))

    has_branch_protection_classic = (classic.get("status") == 200)
    has_ruleset_protection = derive_q1_has_ruleset_protection(branch_protection)

    deser = _safe_dict(dangerous.get("deserialization"))
    cmd_inj = _safe_dict(dangerous.get("cmd_injection"))
    exec_p = _safe_dict(dangerous.get("exec"))

    solo_meta = compute_solo_maintainer(contributors)

    # Phase 1 doesn't currently expose readme text; tool_loads_user_files
    # detection from phase_1_raw_capture relies on topics.
    tool_loads_user_files = derive_tool_loads_user_files(
        readme_text=None, repo_metadata=repo_meta,
    )

    # repo_age_days from created_at if present
    repo_age_days = 0
    created_at = repo_meta.get("created_at")
    if created_at:
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            repo_age_days = (now - created).days
        except (ValueError, AttributeError):
            pass

    # total_merged_lifetime from pr_review or repo_metadata
    total_merged_lifetime = (
        pr_review.get("total_merged_lifetime")
        or pr_review.get("merged_total")
        or repo_meta.get("merged_pr_count_lifetime")
        or 0
    )

    return {
        "formal_review_rate": pr_review.get("formal_review_rate"),
        "any_review_rate": pr_review.get("any_review_rate"),
        "pr_sample_size": pr_review.get("sample_size"),
        "has_branch_protection": has_branch_protection_classic,
        "has_ruleset_protection": has_ruleset_protection,
        "rules_on_default_count": int(rules_on_default.get("count") or 0),
        "has_codeowners": bool(codeowners.get("present") or codeowners.get("file_present")),
        "has_codeql": bool(_safe_dict(p1.get("defensive_configs")).get("has_codeql")),
        "releases_count": int(_safe_dict(p1.get("releases")).get("count") or 0),
        # Q2 signals
        "open_security_issue_count": len(_safe_list(issues_and_commits.get("open_security_issues"))),
        "oldest_cve_pr_age_days": pr_review.get("oldest_open_cve_pr_age_days"),
        "oldest_open_security_item_age_days": derive_q2_oldest_open_security_item_age_days(
            issues_and_commits, _safe_dict(p1.get("open_prs")),
        ),
        "closed_fix_lag_days": pr_review.get("closed_fix_lag_days"),
        # Q3 signals
        "repo_age_days": repo_age_days,
        "total_merged_lifetime": total_merged_lifetime,
        "has_security_policy": bool(community.get("has_security_policy")),
        "has_contributing_guide": bool(community.get("has_contributing_guide")),
        "published_advisory_count": int(advisories.get("published_count") or 0),
        "has_silent_fixes": bool(advisories.get("has_silent_fixes")),
        # Q4 signals
        "deserialization_hit_count": int(deser.get("hit_count") or 0),
        "cmd_injection_hit_count": int(cmd_inj.get("hit_count") or 0),
        "exec_hit_count": int(exec_p.get("hit_count") or 0),
        "tool_loads_user_files": tool_loads_user_files,
        "has_unverified_install_path": not bool(artifact_verification.get("verified")),
        "all_channels_pinned": bool(artifact_verification.get("all_channels_pinned")),
        "artifact_verified": bool(artifact_verification.get("verified")),
        "has_warning_on_install_path": bool(_safe_dict(p3.get("scorecard_cells")).get("has_warning_on_install_path")),
        "has_critical_on_default_path": bool(_safe_dict(p3.get("scorecard_cells")).get("has_critical_on_default_path")),
    }
