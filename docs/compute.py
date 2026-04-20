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
