# Internal Board Review — Triage of External AXIOM Council Audit

**Date:** 2026-04-17
**Review type:** External audit triage
**Input:** AXIOM Council 5-model audit of scanner v2.3 (scanner-AXIOM audit-report.md)
**Decision framework:** ADOPT / REJECT / DEFER per finding

---

## What happened

Scott's friend ran a 5-model council (Claude Opus 4.6, Codex GPT-5.3, ChatGPT 5.4, Gemini 3.1 Pro, DeepSeek V3.2) against our scanner v2.3 zip package (13 files, 209KB). Their verdict: UNANIMOUS REWORK. The audit has 9 sections covering security vulnerabilities, bugs, weaknesses, missing capabilities, competitive landscape, and simplification recommendations.

## Our board's job

Assess each finding for applicability to our system. For each:

1. **ADOPT** — finding is valid and actionable now. Specify what to change.
2. **REJECT** — finding is wrong, misunderstands the system, or is based on incorrect assumptions. Explain why.
3. **DEFER** — finding is valid but not actionable now. Specify the trigger that re-opens it.

## Critical context the external board may not have had

1. **The scanner is LLM-operated, not script-operated.** The prompt is instructions FOR an LLM, not a bash script. Shell commands in the prompt are examples the LLM follows, not literal scripts users execute. The LLM adapts them. This affects how V4 (shell injection) and V5 (SHA truncation) should be assessed.

2. **The CSS drift (B1) is known.** We extracted CSS to a standalone file AFTER the template was written. The template needs updating — we know this. The question is whether it's a FIX NOW or a scheduled cleanup.

3. **Path B WAS exercised.** We ran zustand-v2 via Path B (fresh Opus agent, handoff packet). The guide text saying "proposed — not yet exercised" is stale. The catalog does show Path A for all entries because the zustand-v2 was a validation test, not a catalog entry.

4. **The zip was built for ONE recipient** (Scott's friend) as a v2.3 distribution test. It was not intended as a public release. Missing reference artifacts were a packaging oversight, not a design gap.

5. **JSON-first migration is already planned.** Our internal board reviewed this (V2.3 R3) and deferred to V3.0 with explicit triggers: catalog reaches 10 scans OR 3+ rule-calibration findings.

6. **We already identified Q1 (classification matrix) and Q2 (vulnerability coverage gaps)** in our external board brief. The AXIOM audit's Section 4 (Missing Capabilities) substantially overlaps our Q2.

7. **The "UNANIMOUS REWORK" verdict** should be assessed for appropriateness. The scanner has produced 8 accurate scans across 6 repo shapes. The security vulnerabilities (V1-V5) are real but affect the scanner's own security posture, not the accuracy of its findings.

## Files for reference

- `/root/tinkering/stop-git-std/docs/External-Board-Reviews/041626-celso/scanner-AXIOM audit-report.md` — the full AXIOM audit
- `/root/tinkering/stop-git-std/docs/validate-scanner-report.py` — current validator (289 lines)
- `/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md` — V2.3 prompt (1078 lines)
- `/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md` — V0.1.1 operator guide (552 lines)
- `/root/tinkering/stop-git-std/docs/scanner-design-system.css` — canonical CSS (816 lines)
- `/root/tinkering/stop-git-std/docs/GitHub-Repo-Scan-Template.html` — HTML template
- `/root/tinkering/stop-git-std/docs/board-review-data/external-board-brief-v1.md` — our own Q1+Q2 brief

## Findings to triage

### Section 1: Critical Vulnerabilities (V1-V5)

**V1. XSS in HTML Reports** — Validator doesn't block `<script>`, `on*=`, `javascript:` URLs, `<iframe>`. C4 heuristic only checks bare `<`.
**V2. Path Traversal via Tarball** — No `--no-absolute-names` on tar.
**V3. Symlink Attack** — `grep -r` follows symlinks outside scan dir.
**V4. Shell Injection via Unquoted Variables** — Prompt shows unquoted `$OWNER`, `$REPO`.
**V5. SHA Truncation** — Prompt line 88 uses `head -c 7`. Tarball fetch uses short SHA.

### Section 2: Confirmed Bugs (B1-B6)

**B1. CSS Drift** — Template body::after ≠ standalone CSS body::after.
**B2. PR Count Logic** — `pulls?state=closed&per_page=1 --jq 'length'` returns 0 or 1, not total.
**B3. Validator Doesn't Validate Markdown** — MD files pass trivially. False assurance.
**B4. Package Incomplete** — caveman.html not in reference/, .md companions missing.
**B5. Path B Contradictions** — Guide says "not yet exercised" but it was.
**B6. Step 8 Prerequisites** — Needs npm/pip/cargo not listed in prerequisites.

### Section 3: Weaknesses (W1-W7)

**W1. 1078-Line Prompt** — Exceeds reliable LLM compliance window.
**W2. N×2 API Calls in Step 5b** — Up to 1200 calls, no budget.
**W3. /tmp Volatile** — Crash mid-Phase-2 loses evidence.
**W4. Dependabot 403** — No fallback for non-admin users.
**W5. Exhibit Rollup Unreliable** — LLMs poor at counting + conditional restructure.
**W6. Scorecard Thresholds Too Rigid** — 59% vs 60% on imprecise data.
**W7. Manual Pre-Render Checklist** — LLM operators skip it.

### Section 4: Missing Capabilities (15 items, priority-ranked)

HIGH: OSSF Scorecard API, rate-limit budget, dep vuln fallback, secrets-in-history, unauthenticated fallback.
MEDIUM: SBOM endpoint, release sig verification, deps.dev, fork divergence, fake-star detection.
LOW: Reclaimed-username, tampered timestamps, binary entropy, safer alternatives, SARIF output.

### Section 5: Competitive Landscape

Claims scanner reimplements ~60% of OSSF Scorecard. Identifies 4 unique edges (plain-English narrative, zero-install, multi-domain analysis, dark-theme reports). Proposes 3-tier integration strategy.

### Section 6: Overengineering/Simplification (O1-O5)

**O1.** LLM should orchestrate tools, not reimplant them.
**O2.** Reduce 12 S8 rules to 5 hard rules.
**O3.** Move changelog out of prompt.
**O4.** Single CSS source of truth.
**O5.** JSON evidence → HTML template (= our JSON-first plan).

### Section 7: Must-Have Fix List (12 items)

Prioritized list combining V1-V5 fixes + B2 + OSSF integration + rate-limit check.

### Section 8: Nice-to-Have List (10 items)

Quick scan mode, embedded fonts, gitleaks/osv-scanner, automated checklist, checkpointing, etc.
