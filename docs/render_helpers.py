"""render_helpers.py — Phase 4 derivation helpers for renderers.

Shared by docs/render-md.py + docs/render-html.py via env.globals injection.
Produces mechanical table-row content that the LLM previously re-authored
into phase_4_structured_llm. Templates fall back to derived content when
the LLM-authored override is empty.

Per back-to-basics-plan.md §Phase 4: 3 helpers — derive_repo_vitals,
derive_coverage_detail, derive_pr_sample. (4th helper derive_evidence_facts
was dropped after disk verification — section 07 is 100% LLM synthesis.
See plan §Phase 4 "Why no derive_evidence_facts" note.)

All helpers take phase_1_raw_capture as input. None return shape-specific
commentary (the `note` column on vitals stays None — LLM adds insight via
the override path when applicable).
"""

from datetime import datetime, timezone


def _safe_dict(x):
    return x if isinstance(x, dict) else {}


def _safe_list(x):
    return x if isinstance(x, list) else []


def _fmt_int(n):
    return f"{n:,}" if isinstance(n, int) else (str(n) if n is not None else "")


def _fmt_date(iso):
    return iso[:10] if isinstance(iso, str) and len(iso) >= 10 else ""


def _row(metric, value, note=None):
    return {"metric": metric, "value": value, "note": note}


def derive_repo_vitals(p1: dict) -> list:
    """Produce mechanical {metric, value, note} rows from phase_1_raw_capture.

    `note` is None for derived rows. The LLM adds notes via override when
    a row deserves shape-specific commentary (e.g. "Massively popular for
    a 3-month-old repo" on stars).

    Covers ~20 mechanical metrics: identity (stars/forks/license/created/
    pushed/default branch), governance (codeowners/SECURITY.md/branch
    protection/rulesets/community health %), supply-chain surface
    (workflows/pr_target/dependabot/CodeQL), distribution (releases),
    review hygiene (formal/any review rate, self-merge), and posture
    (advisories, OSSF Scorecard score).
    """
    p1 = _safe_dict(p1)
    rm = _safe_dict(p1.get("repo_metadata"))
    contrib = _safe_dict(p1.get("contributors"))
    releases = _safe_dict(p1.get("releases"))
    bp = _safe_dict(p1.get("branch_protection"))
    codeowners = _safe_dict(p1.get("codeowners"))
    community = _safe_dict(p1.get("community_profile"))
    advisories = _safe_dict(p1.get("security_advisories"))
    workflows = _safe_dict(p1.get("workflows"))
    deps = _safe_dict(p1.get("dependencies"))
    ossf = _safe_dict(p1.get("ossf_scorecard"))
    pr_review = _safe_dict(p1.get("pr_review"))

    rows = []

    # Identity
    rows.append(_row("Stars", _fmt_int(rm.get("stargazer_count"))))
    rows.append(_row("Forks", _fmt_int(rm.get("fork_count"))))
    rows.append(_row("Open issues", _fmt_int(rm.get("open_issues_count"))))
    rows.append(_row("Primary language", rm.get("primary_language") or ""))
    rows.append(_row("License", rm.get("license_spdx") or ""))
    rows.append(_row("Created", _fmt_date(rm.get("created_at"))))
    rows.append(_row("Last pushed", _fmt_date(rm.get("pushed_at"))))
    rows.append(_row("Default branch", rm.get("default_branch") or ""))

    # Contributors
    top = _safe_list(contrib.get("top_contributors"))
    total = contrib.get("total_contributor_count")
    rows.append(_row("Total contributors", _fmt_int(total)))
    if top and isinstance(top[0], dict):
        first = top[0]
        login = first.get("login", "")
        commits = first.get("contributions") or first.get("commits")
        if login and commits and isinstance(total, int) and total > 0:
            sum_commits = sum((c.get("contributions") or c.get("commits") or 0) for c in top if isinstance(c, dict))
            if sum_commits > 0:
                pct = round(100 * commits / sum_commits, 1)
                rows.append(_row("Top contributor", f"{login} ({pct}%)"))

    # Distribution
    rows.append(_row("Formal releases", _fmt_int(releases.get("total_count"))))
    rel_entries = _safe_list(releases.get("entries"))
    if rel_entries and isinstance(rel_entries[0], dict):
        latest = rel_entries[0]
        tag = latest.get("tag_name") or latest.get("name") or ""
        published = _fmt_date(latest.get("published_at"))
        if tag:
            rows.append(_row("Latest release", f"{tag} ({published})" if published else tag))

    # Governance — branch protection
    classic = _safe_dict(bp.get("classic"))
    classic_status = classic.get("status") or classic.get("http_status")
    rows.append(_row("Classic branch protection", "configured" if classic_status == 200 else "none (HTTP 404)"))

    # rulesets / rules_on_default are dicts {count, entries} in V1.2 bundles;
    # the legacy `compute_scorecard_cells()` path used direct lists. Handle both.
    rulesets_obj = bp.get("rulesets")
    if isinstance(rulesets_obj, dict):
        rulesets_count = rulesets_obj.get("count", len(_safe_list(rulesets_obj.get("entries"))))
    else:
        rulesets_count = len(_safe_list(rulesets_obj))
    rows.append(_row("Repository rulesets", _fmt_int(rulesets_count)))

    rules_obj = bp.get("rules_on_default")
    if isinstance(rules_obj, dict):
        rules_count = rules_obj.get("count", len(_safe_list(rules_obj.get("entries"))))
    else:
        rules_count = len(_safe_list(rules_obj))
    rows.append(_row("Rules on default branch", _fmt_int(rules_count)))

    rows.append(_row("CODEOWNERS", "present" if codeowners.get("found") else "absent"))
    rows.append(_row("SECURITY.md", "present" if community.get("has_security_policy") else "absent"))
    rows.append(_row("CONTRIBUTING", "present" if community.get("has_contributing") else "absent"))
    health = community.get("health_percentage")
    if health is not None:
        rows.append(_row("Community health", f"{health}%"))

    # Supply-chain surface
    rows.append(_row("Workflows", _fmt_int(workflows.get("count"))))
    pr_target = workflows.get("pull_request_target_count")
    if pr_target is not None:
        rows.append(_row("`pull_request_target` usage", _fmt_int(pr_target)))

    dependabot = _safe_dict(deps.get("dependabot_config"))
    rows.append(_row("Dependabot config", "present" if dependabot.get("found") else "absent"))

    # Review hygiene
    formal_rate = pr_review.get("formal_review_rate")
    any_rate = pr_review.get("any_review_rate")
    sample = pr_review.get("sample_size")
    if sample is not None:
        rows.append(_row("PR sample size", _fmt_int(sample)))
    if formal_rate is not None:
        rows.append(_row("Formal review rate", f"{formal_rate}%"))
    if any_rate is not None:
        rows.append(_row("Any-review rate", f"{any_rate}%"))

    # Posture
    rows.append(_row("Published GHSA advisories", _fmt_int(advisories.get("count"))))

    if ossf.get("indexed"):
        score = ossf.get("overall_score")
        if score is not None:
            rows.append(_row("OSSF Scorecard", f"{score}/10"))
    elif ossf.get("queried"):
        rows.append(_row("OSSF Scorecard", "not indexed"))

    return rows


_COVERAGE_ICON = {
    "ok": "✅",
    "partial": "⚠",
    "blocked": "❌",
    "not_available": "⚠",
    "not_indexed": "ℹ",
    "not_queried": "ℹ",
    "unknown": "⚠",
}


def derive_coverage_detail(p1: dict) -> list:
    """Produce mechanical {check, result} rows from phase_1 harness flags.

    Each row reflects a coverage decision the harness made: did it run, was
    it gated by missing access, was the data source unavailable, etc.
    Maps phase_1 affirmations + counts into a flat human-readable table.
    """
    p1 = _safe_dict(p1)
    coverage = _safe_dict(p1.get("coverage_affirmations"))
    pre_flight = _safe_dict(p1.get("pre_flight"))
    ossf = _safe_dict(p1.get("ossf_scorecard"))
    deps = _safe_dict(p1.get("dependencies"))
    gitleaks = _safe_dict(p1.get("gitleaks"))
    workflows = _safe_dict(p1.get("workflows"))
    pr_review = _safe_dict(p1.get("pr_review"))
    pi_scan = _safe_dict(p1.get("prompt_injection_scan"))

    rows = []

    # Tarball + grep — only emit if harness ran (pre_flight present)
    if pre_flight:
        file_count = pre_flight.get("tarball_file_count")
        if pre_flight.get("tarball_extracted"):
            rows.append({"check": "Tarball extraction + local grep", "result": f"✅ Scanned ({file_count} files)" if file_count else "✅ Scanned"})
        else:
            rows.append({"check": "Tarball extraction + local grep", "result": "❌ Not extracted"})

    # API rate budget
    rate = _safe_dict(pre_flight.get("api_rate_limit"))
    remaining = rate.get("remaining")
    if remaining is not None:
        rows.append({"check": "`gh api` rate limit", "result": f"✅ {remaining}/5000 remaining"})

    # OSSF Scorecard
    if ossf.get("indexed"):
        score = ossf.get("overall_score")
        rows.append({"check": "OSSF Scorecard", "result": f"✅ Indexed ({score}/10)" if score is not None else "✅ Indexed"})
    elif ossf.get("queried"):
        status = ossf.get("http_status")
        rows.append({"check": "OSSF Scorecard", "result": f"⚠ Not indexed (HTTP {status})" if status else "⚠ Not indexed"})

    # osv.dev / dependabot
    osv = _safe_list(deps.get("osv_lookups"))
    if osv:
        rows.append({"check": "osv.dev dependency queries", "result": f"✅ {len(osv)} package(s) queried"})

    dependabot_alerts = _safe_dict(deps.get("dependabot_alerts"))
    if dependabot_alerts.get("queried"):
        if dependabot_alerts.get("accessible"):
            count = dependabot_alerts.get("count")
            rows.append({"check": "Dependabot alerts", "result": f"✅ Accessible ({count} alerts)" if count is not None else "✅ Accessible"})
        else:
            rows.append({"check": "Dependabot alerts", "result": "⚠ Admin scope (403)"})

    # Gitleaks
    if gitleaks.get("ran"):
        count = gitleaks.get("findings_count", 0)
        rows.append({"check": "Gitleaks", "result": f"✅ Scanned ({count} findings)"})
    elif gitleaks.get("available") is False:
        rows.append({"check": "Gitleaks", "result": "⊗ Not available on this scanner host"})

    # Workflows
    wf_count = workflows.get("count")
    if wf_count is not None:
        rows.append({"check": "Workflows", "result": f"✅ {wf_count} detected" if wf_count else "✅ None present"})

    # PR sample
    if pr_review:
        sample = pr_review.get("sample_size")
        if sample is not None:
            rows.append({"check": "PR review sample", "result": f"✅ Sample size N={sample}" if sample > 0 else "⊗ N=0 lifetime merged PRs"})

    # Prompt-injection scan
    if pi_scan.get("scan_method"):
        scanned = _safe_list(pi_scan.get("scanned_files"))
        signals = pi_scan.get("signal_count", 0)
        rows.append({"check": "Prompt-injection scan", "result": f"✅ {len(scanned)} file(s); {signals} signal(s)"})

    # Distribution channels
    if coverage.get("distribution_channels_verified") is not None:
        rows.append({"check": "Distribution channels inventory", "result": "✅ Verified" if coverage.get("distribution_channels_verified") else "⚠ Not verified"})

    return rows


def derive_pr_sample(p1: dict) -> list:
    """Produce mechanical PR sample rows from phase_1.pr_review.prs.

    Returns: [{number, title, author, merger, formal_review, any_review,
               self_merge, security_flagged, merged_at}, ...]

    Schema-tolerant — handles two row shapes:
      - V1.1 fixture rows: number, author, merger, formal_review (str|None),
        any_review (bool), self_merge.
      - V1.2 harness rows: number, title, review_decision, any_review_count
        (int), self_merge, merged_at, labels, security_flagged.

    Phase 1.5 follow-up: V1.2 harness `pr_review.prs` does NOT populate
    author or merger fields; on real bundles those columns render as ''.
    Harness should populate them so the derived simple table matches the
    LLM enriched table structurally. Tracked alongside kamal CODEOWNERS
    gap + Kronos pickle.load gap in docs/calibration-impl-notes.md §4-§5.
    """
    p1 = _safe_dict(p1)
    pr_review = _safe_dict(p1.get("pr_review"))
    prs = _safe_list(pr_review.get("prs"))

    rows = []
    for p in prs:
        if not isinstance(p, dict):
            continue
        # any_review may be a bool (V1.1 fixture) or derived from any_review_count int (V1.2 harness)
        if "any_review" in p:
            any_review = bool(p.get("any_review"))
        else:
            any_review = bool(p.get("any_review_count", 0))
        # formal_review may be already-stringified (V1.1 fixture) or live in review_decision (V1.2 harness)
        formal_review = p.get("formal_review")
        if formal_review is None:
            formal_review = p.get("review_decision") or ""
        rows.append({
            "number": p.get("number"),
            "title": p.get("title", ""),
            "author": p.get("author", ""),
            "merger": p.get("merger", ""),
            "formal_review": formal_review,
            "any_review": any_review,
            "self_merge": bool(p.get("self_merge", False)),
            "security_flagged": bool(p.get("security_flagged", False)),
            "merged_at": _fmt_date(p.get("merged_at")),
        })
    return rows
