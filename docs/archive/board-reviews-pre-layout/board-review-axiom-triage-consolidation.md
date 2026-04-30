# Board Review — AXIOM External Audit Triage Consolidation

**Date:** 2026-04-17
**Review type:** External audit triage (single-round blind)
**Input:** AXIOM Council 5-model audit (scanner-AXIOM audit-report.md)
**Board:** Pragmatist (Claude Opus 4.6) + Systems Thinker (Codex GPT-5.4) + Skeptic (DeepSeek V3.2)
**Verdict:** ADOPT WITH CONDITIONS (not REWORK)

---

## Overall Assessment: "UNANIMOUS REWORK" Overruled

All 3 board members reject the AXIOM council's "UNANIMOUS REWORK" headline:

- **Pragmatist:** "This is a hardening pass, not a rework. 8 accurate scans prove the architecture works."
- **Systems Thinker:** "The product does not need a full rework. 'Conditional release block pending hardening' would be more accurate."
- **Skeptic:** (Agrees rework is appropriate but grounds this in the security findings, not architectural issues.)

**Board verdict: ADOPT WITH CONDITIONS.** The security hardening items (V1-V3, V5) are legitimate FIX NOW. The architectural pivot (O1) is directionally correct but must preserve the zero-install value proposition. The 8-scan track record demonstrates working architecture; the gaps are incremental, not foundational.

---

## O1: "Orchestrate Not Reimplant" — Nuanced Consensus

All 3 members agree on the direction but disagree on scope:

- **Pragmatist:** "Tier 1 free APIs — yes, absolutely. Hard tool dependencies — no, that kills zero-install."
- **Systems Thinker:** "Right direction, wrong absolutism. Use `gh` + public APIs by default; optional installed tools can enrich results, not define the product."
- **Skeptic:** "This is the only viable path forward" (strongest endorsement).

**Board position:** ADOPT as a V2.4 GUIDELINE, not a V3.0 architectural pivot. Specifically:
- Add free API calls now (Scorecard, osv.dev, deps.dev) — zero install, pure win
- Make installed tools (gitleaks, osv-scanner) opportunistic: use if present, fall back to current approach if not
- Keep LLM value in synthesis, cross-domain judgment, and narrative reporting
- Full architectural pivot (JSON-first + orchestration) remains deferred to V3.0 with existing triggers

---

## Consolidated Verdicts

### FIX NOW (unanimous — all 3 members agree)

| ID | Finding | Consensus | Action |
|----|---------|-----------|--------|
| **V3** | Symlink attack — host file disclosure | 3/3 ADOPT | Add `find "$SCAN_DIR" -type l -delete` after tar extraction in both prompt + Operator Guide |
| **V2** | Path traversal via tarball | 3/3 ADOPT | Add `--no-absolute-names` to tar command in prompt + Operator Guide |
| **V1** | XSS in HTML reports | 3/3 ADOPT | Add XSS checks to validator (script tags, on*= handlers, javascript: URLs, iframe/embed/object). Add CSP meta tag to template. Replace onclick in font controls. |
| **V5** | SHA truncation weakens pinning | 3/3 ADOPT | Remove `\| head -c 7` from prompt line 88. Use full SHA for tarball fetch. Display can use short form. |
| **B1** | CSS drift (template != standalone) | 3/3 ADOPT | Copy `scanner-design-system.css` content into template `<style>` block. Add source comment. |
| **B2** | PR count logic wrong | 3/3 ADOPT | Fix the `gh api pulls?per_page=1 --jq 'length'` → returns 0/1 not total. Use Link header pagination or `gh pr list --json`. |

### FIX NEXT (V2.4 cycle — strong consensus)

| ID | Finding | Consensus | Action |
|----|---------|-----------|--------|
| **V4** | Shell injection via unquoted vars | 3/3 ADOPT (downgraded from CRITICAL) | Quote all shell variables. Note: GitHub owner/repo names can't contain metacharacters; LLM constructs commands. Hygiene fix, not a vulnerability. |
| **W1/O3** | Prompt too long + changelog noise | 3/3 ADOPT | Move version history + D-series deferrals to CHANGELOG.md (~60 lines removed). Do NOT restructure core investigation steps. |
| **W2/Cap-2** | Rate-limit exhaustion + budget | 3/3 ADOPT | Add `gh api rate_limit` check before Step 5. Budget tracking. Reduced sampling when < 500 remaining. |
| **W4/Cap-3** | Dependabot 403 + dep vuln fallback | 3/3 ADOPT | Add osv.dev API fallback (free, zero install). Parse package manifests from tarball, query osv.dev per dependency. |
| **Cap-1** | OSSF Scorecard integration | 3/3 ADOPT | Add `curl -s "https://api.securityscorecards.dev/projects/github.com/$OWNER/$REPO"` to Phase 2. Parse 24 check scores as evidence. |
| **O4** | Single CSS source of truth | 3/3 ADOPT | scanner-design-system.css is authoritative. Template derives from it. Add sync mechanism. |
| **B3** | Validator doesn't validate Markdown | 3/3 ADOPT | Add `--markdown` mode checking required section headers + minimum line count. |
| **O2** | Reduce 12 S8 rules to 5 hard | 2/3 ADOPT (Pragmatist: DEFER) | Keep 5 hard rules (utility classes, no inline styles, status chips, action hints, rem fonts). Rest become "recommended patterns shown in reference scans." |

### DEFER (valid but not now)

| ID | Finding | Consensus | Trigger |
|----|---------|-----------|---------|
| **O1** | Full orchestration pivot | 3/3 DEFER to V3.0 | 10 scans, or 3 rule-calibration findings, or grep false negative that tool would catch |
| **O5** | JSON evidence → HTML template | 3/3 DEFER to V3.0 | Same as O1 (already deferred by prior board) |
| **W3** | /tmp volatile | 3/3 DEFER | First crash losing significant work |
| **W5** | Exhibit rollup unreliable | 3/3 DEFER | JSON-first migration (renderer handles deterministically) |
| **W6** | Scorecard thresholds too rigid | 3/3 DEFER | Scan where threshold produces demonstrably wrong verdict |
| **W7** | Manual pre-render checklist | 3/3 DEFER | V0.2 Operator Guide cycle |
| **B5** | Path B contradictions (stale text) | 3/3 DEFER (doc cleanup) | Next Operator Guide revision |
| **B6** | Step 8 prerequisites undeclared | 3/3 DEFER | Scan where missing tool causes false "no concerns" verdict |
| **Cap-4** | Secrets-in-history (gitleaks) | 2/3 DEFER, 1/3 FIX NEXT | Tier 2 opportunistic tool framework |
| **Cap-5** | Unauthenticated fallback | 2/3 DEFER | User request for public-only scanning |
| **Cap-6** | SBOM endpoint | 2/3 DEFER | When GitHub makes endpoint public/non-admin |
| **Cap-7** | Release sig verification (cosign) | 2/3 DEFER | Tier 3 tool framework |
| **Cap-8** | deps.dev cross-reference | 2/3 DEFER (Pragmatist: close to FIX NEXT) | After Cap-1 and Cap-3 ship |
| **Cap-9** | Fork divergence analysis | 3/3 DEFER | First suspicious fork scan |
| **Cap-10** | Fake-star burst detection | 3/3 DEFER | Free star-history API availability |
| **Cap-11-15** | Reclaimed username, tampered timestamps, binary entropy, safer alternatives, SARIF | 3/3 DEFER | Various niche triggers |

### REJECT

| ID | Finding | Consensus | Reason |
|----|---------|-----------|--------|
| **B4** | Package incomplete (missing refs) | 2/3 REJECT, 1/3 DEFER | Test zip to one person, not a public release. Files exist in repo. |
| **"UNANIMOUS REWORK"** | Overall verdict | 3/3 REJECT | Overstated. Hardening + incremental improvements, not rework. |
| **V4 at CRITICAL** | Shell injection severity | 2/3 REJECT severity | GitHub enforces safe chars in owner/repo. LLM constructs commands. Hygiene fix, not exploitable vulnerability. |

---

## Disagreements

### D1: O2 (Reduce S8 rules) — Pragmatist vs Systems Thinker + Skeptic

- **Pragmatist:** DEFER — "12 rules exist because HTML quality matters. 8 scans produced good HTML. Reducing risks regression."
- **Systems Thinker + Skeptic:** ADOPT — "LLMs reliably follow ~7-8 of 12. Later rules are inconsistently applied. Codify reality."
- **Resolution:** ADOPT for FIX NEXT. The Pragmatist's concern about regression is addressed by keeping the 5 strongest rules hard and making the rest reference-scan patterns (not deleted, just demoted).

### D2: Cap-4 (Secrets scanning) — Skeptic vs Pragmatist + Systems Thinker

- **Skeptic:** FIX NEXT — "Grepping commit messages is useless. Must integrate gitleaks."
- **Pragmatist + Systems Thinker:** DEFER — "Requires installation, violates zero-install."
- **Resolution:** DEFER with Tier 2 opportunistic note. When the opportunistic tool framework lands, gitleaks becomes the first integration.

### D3: Skeptic's overall posture

- **Skeptic:** "All development must stop until FIX NOW items are resolved. This tool is more dangerous than not running a scan."
- **Pragmatist + Systems Thinker:** The security issues are real but the tool produces accurate findings. The risk is to the operator's machine, not to the assessment quality.
- **Resolution:** FIX NOW items are genuine priorities but "stop all development" is overstated. The security hardening can be done in one session alongside continued operation.

---

## Implementation Priority (FIX NOW items ordered by effort/impact)

1. **V3 — Symlink stripping** (5 min, blocks host-file disclosure)
   - Prompt: add after tar line ~101
   - Operator Guide: add after tar line ~131
   - `find "$SCAN_DIR" -type l -delete`

2. **V2 — Path traversal protection** (1 min)
   - Add `--no-absolute-names` to all tar commands

3. **V5 — Full SHA** (15 min)
   - Prompt line 88: remove `| head -c 7`
   - Use full SHA for tarball fetch
   - Display uses `${HEAD_SHA:0:7}` for readability

4. **B1 — CSS sync** (15 min)
   - Copy scanner-design-system.css into template `<style>` block
   - Add `/* SOURCE: scanner-design-system.css — do not edit here */` comment

5. **B2 — PR count fix** (10 min)
   - Replace the broken `per_page=1 --jq 'length'` approach

6. **V1 — XSS validator + CSP** (2 hrs)
   - Add XSS content checks to validate-scanner-report.py
   - Add CSP meta tag to template
   - Replace onclick in font controls with CSP-compatible JS

---

## What AXIOM Got Right (credit where due)

1. **V1-V3 security boundary issues** — Legitimate findings. The scanner processes untrusted input and the input boundary wasn't hardened.
2. **OSSF Scorecard API** — Best single recommendation in the audit. Free, authoritative, zero-install.
3. **Competitive landscape analysis** — The 4 unique edges identified (narrative, zero-install, multi-domain, dark-theme UX) are accurate and useful for positioning.
4. **osv.dev as Dependabot fallback** — Practical, zero-install solution to a real coverage gap.
5. **CSS drift observation** — Caught a known issue and correctly identified the root cause.
6. **Prompt changelog noise** — Easy win, universally agreed.

## What AXIOM Got Wrong or Overstated

1. **"UNANIMOUS REWORK"** — Inflammatory headline for a tool that works. Should have been "Security hardening required."
2. **V4 shell injection severity** — GitHub owner/repo names can't contain metacharacters. The LLM constructs commands. Not exploitable as described.
3. **"More dangerous than not running a scan"** (DeepSeek's framing, echoed by AXIOM's Skeptic member) — The security issues affect the operator's machine, not the quality of findings. The scan findings are accurate.
4. **"LLM instruction-following degrades past ~500 lines"** — Unsupported claim for frontier models. The real issue is signal-to-noise ratio from changelog noise.
5. **B4 as a confirmed bug** — Test zip packaging choice, not a product defect.
6. **Hard tool dependencies** — Recommending gitleaks, osv-scanner, cosign as prerequisites contradicts the zero-install value proposition.

---

*Board review conducted 2026-04-17. Single-round blind review (R1 only — strong convergence, no R2 needed).*
*Pragmatist: Claude Opus 4.6 (sub-agent) | Systems Thinker: Codex GPT-5.4 | Skeptic: DeepSeek V3.2 (deepseek-chat)*
