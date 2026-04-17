# Pragmatist — Round 1 Response

**Role:** Pragmatist (implementation-focused, low-effort/high-impact bias)
**Input:** AXIOM 5-model council audit of GitHub Repo Scanner v2.3
**Date:** 2026-04-17

---

## Meta-Assessment: Is "UNANIMOUS REWORK" Appropriate?

**No.** "UNANIMOUS REWORK" is overstated for a tool that has produced 8 accurate scans with 50+ board fixes already applied. The audit itself says "the concept is strong," "the gaps are fixable, not architectural," and "execution quality is strong." That is not a rework — that is a hardening pass plus incremental improvements.

The AXIOM council appears to have evaluated the scanner as if it were a shipped product for non-technical end users. It is not. It is an LLM-operated investigation tool used by its author. The zip was sent to one person. The threat model for "attacker crafts a repo whose PR title contains XSS" is real but the blast radius is currently one person running the scan in a terminal, not a web application serving reports to the public.

**My framing:** This is a "SECURITY HARDENING + INCREMENTAL" verdict, not a rework.

---

## Meta-Assessment: Is O1 (Orchestrate Not Reimplant) Right for Zero-Install?

**Partially.** The AXIOM council is correct that OSSF Scorecard's free API should be called instead of reimplementing its checks. That is a pure win — zero install, one curl call, 24 checks.

But the broader "orchestrate gitleaks/osv-scanner/etc." recommendation contradicts the tool's core value proposition: zero-install, works anywhere an LLM has `gh` CLI access. Adding `gitleaks`, `osv-scanner`, `cosign` as hard dependencies turns this into yet another tool-installation-required scanner. The right architecture is:

1. **Tier 1 (adopt now):** Free API calls that need zero install (Scorecard, deps.dev, osv.dev)
2. **Tier 2 (opportunistic):** If gitleaks/osv-scanner are available, use them; if not, fall back to current grep-based approach
3. **Tier 3 (defer):** Don't add hard dependencies on tools that need installation

This preserves the zero-install value while getting 80% of the benefit.

---

## FIX NOW

### V3: Symlink Attack — Host File Disclosure
**Verdict:** ADOPT
**Reasoning:** This is the highest-impact, lowest-effort fix in the entire audit. One line (`find "$SCAN_DIR" -type l -delete`) after tar extraction blocks symlink-based host file disclosure. The attack is real: a malicious repo with `README.md -> /etc/shadow` would leak host files into the LLM context.
**What to change:** Add `find "$SCAN_DIR" -type l -delete` immediately after the tar extraction sanity check in both the prompt (line ~101) and the Operator Guide (line ~131).

### V2: Path Traversal via Tarball Extraction
**Verdict:** ADOPT
**Reasoning:** Another one-liner. Add `--no-absolute-names` to the tar command. The AXIOM note about GitHub Enterprise is valid — a compromised GHE instance could serve malicious tarballs.
**What to change:** Change tar commands in prompt and Operator Guide to include `--no-absolute-names`. The Operator Guide already pipes to `tar -xzf` so add the flag there too.

### V5: SHA Truncation Weakens Commit Pinning
**Verdict:** ADOPT
**Reasoning:** The prompt uses `head -c 7` to truncate the SHA, then uses the short SHA for the tarball fetch. The Operator Guide already uses the full SHA (line 125). This is a prompt-only fix — align the prompt with the Operator Guide. Short SHA collision risk is theoretical for now but the fix is trivial.
**What to change:** Remove `| head -c 7` from prompt line 88. Use full SHA for tarball fetch. Display can still use short form (`${HEAD_SHA:0:7}`) for human readability.

### V1: XSS in HTML Reports — Validator Is Not a Security Gate
**Verdict:** ADOPT (scoped)
**Reasoning:** The audit is correct that the validator does not check for `<script>`, `onclick`, `javascript:` URLs, etc. However, the threat model needs scoping: the LLM generates the HTML, and the LLM is the one inserting repo-sourced text. The C4 heuristic already catches bare `<` but misses well-formed malicious tags. Adding targeted checks is low-effort.
**What to change:**
1. Add to validator: reject `<script>` in body (outside `<style>`), `on\w+=` event handler attributes, `javascript:` URLs, `<iframe>`, `<embed>`, `<object>` tags.
2. Add a CSP meta tag to the HTML template: `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:;">`.
3. The existing `onclick` in the font-size controls needs replacing with a CSP-compatible approach.

### B2: PR Count Logic Is Wrong
**Verdict:** ADOPT
**Reasoning:** `gh api pulls?state=closed&per_page=1 --jq 'length'` returns 0 or 1, not total count. This is a factual bug that makes the "sampled N of M" disclosure inaccurate. Fix is one line.
**What to change:** Replace with `gh api "repos/$OWNER/$REPO/pulls?state=closed&per_page=1" -i 2>&1 | grep -i 'Link:' | grep -oP 'page=\K\d+(?=>; rel="last")'` or use `gh pr list --repo $OWNER/$REPO --state merged --json number --jq 'length'` (but this caps at 1000). Better: use the `Link` header pagination or the REST total_count approach.

### B1: CSS Has Already Drifted — Template != Standalone File
**Verdict:** ADOPT
**Reasoning:** Known issue (noted in brief context item 6). The standalone `scanner-design-system.css` is the authoritative source per our own design. The template's `<style>` block needs to be replaced with the standalone CSS content, or the template should `<link>` to it. Since reports are standalone HTML files, the template's `<style>` block should contain the exact content of `scanner-design-system.css`.
**What to change:** Copy `scanner-design-system.css` content into template's `<style>` block, replacing whatever is there. Add a comment: `/* SOURCE: scanner-design-system.css — do not edit here, edit the .css file */`.

---

## FIX NEXT (V2.4 cycle)

### V4: Shell Injection via Unquoted Variables
**Verdict:** ADOPT (FIX NEXT)
**Reasoning:** The AXIOM council flags unquoted `$OWNER` and `$REPO`. However — and this is critical context the council missed — these are not user-input variables. The LLM constructs these commands. GitHub owner/repo names cannot contain spaces or shell metacharacters (GitHub enforces `[a-zA-Z0-9._-]`). The `for USER in $OWNER $(...)` pattern is fine for GitHub usernames. That said, defensive quoting is good hygiene and the fix is mechanical.
**What to change:** Quote `"$OWNER"`, `"$REPO"`, `"$SCAN_DIR"` throughout prompt. Low priority because the attack vector doesn't exist for GitHub-sourced values.

### W2: N x 2 API Calls in Step 5b Will Exhaust Rate Limit
**Verdict:** ADOPT (FIX NEXT)
**Reasoning:** 600+ API calls for PR analysis is a real problem for popular repos. The scanner has hit this in practice (it's why we sample 300 PRs, not all). Adding a rate-limit check and early exit is practical.
**What to change:** Add `gh api rate_limit --jq '.resources.core.remaining'` check before Step 5. If remaining < 500, switch to reduced sampling (50 PRs). Add budget tracking: count API calls, warn at 80% of remaining budget.

### W1: 1078-Line Prompt Exceeds Reliable LLM Compliance
**Verdict:** ADOPT (FIX NEXT, scoped)
**Reasoning:** The audit is right that the changelog/version history (44 lines) is dead weight. The 15 D-series deferrals are also noise the LLM reads but cannot act on. However, the claim that "LLM instruction-following degrades past ~500 lines" is unsupported — frontier models (Opus 4.6, Codex GPT-5.x) handle 1000+ line system prompts routinely. The real issue is signal-to-noise, not absolute length.
**What to change:** Move version history and D-series deferrals to `CHANGELOG.md`. This removes ~60 lines of noise. Do NOT restructure the core investigation steps — they work.

### O3: Move 44 Lines of Changelog Out of Prompt
**Verdict:** ADOPT (FIX NEXT) — same as W1 scoped above.
**What to change:** Already covered under W1.

### O4: Single CSS Source of Truth
**Verdict:** ADOPT (FIX NEXT)
**Reasoning:** Already covered under B1 for the immediate drift fix. The longer-term fix is a build/copy step.
**What to change:** Add a one-liner script or Makefile target that copies `scanner-design-system.css` into the template's `<style>` block. Run it as part of the scan prep.

### B3: Validator Doesn't Actually Validate Markdown
**Verdict:** ADOPT (FIX NEXT)
**Reasoning:** True — the validator is an HTML checker. A trivial `.md` file exits 0. Since MD is the canonical format (our own rule), the validator should at minimum check that MD files contain expected sections.
**What to change:** Add a `--markdown` mode that checks for required section headers (Executive Summary, Findings, Evidence Appendix, etc.) and minimum line count. Low effort, high assurance.

### W4: Dependabot Alerts Require Admin Scope
**Verdict:** ADOPT (FIX NEXT)
**Reasoning:** Dependabot 403 is common and means zero dependency vulnerability coverage. The Tier 1 free API approach works here: `curl -s "https://api.osv.dev/v1/query"` needs zero auth and zero install.
**What to change:** Add osv.dev API fallback when Dependabot returns 403. Parse `package.json`/`requirements.txt`/`Cargo.toml` from the extracted source, query osv.dev for each dependency.

### Cap-1: OSSF Scorecard Integration
**Verdict:** ADOPT (FIX NEXT)
**Reasoning:** This is the single highest-value capability addition. One `curl` call to `api.securityscorecards.dev` returns 24 pre-computed checks for free, no auth, no install. The LLM currently reimplements ~60% of these checks with grep. This replaces fragile grep-based detection with authoritative data.
**What to change:** Add to Phase 2: `curl -s "https://api.securityscorecards.dev/projects/github.com/$OWNER/$REPO"`. Parse the JSON. Use individual check scores as evidence inputs. LLM still writes the narrative — Scorecard provides the data.

### Cap-2: Rate-Limit Awareness + Budget
**Verdict:** ADOPT (FIX NEXT) — same as W2 above.

### Cap-3: Dependency Vuln Fallback
**Verdict:** ADOPT (FIX NEXT) — same as W4 above, via osv.dev API (zero install).

---

## DEFER

### O1: LLM Should Orchestrate, Not Reimplant
**Verdict:** DEFER
**Reasoning:** The full architectural pivot to "LLM orchestrates tools" is the V3.0 JSON-first migration direction our own board already deferred (triggers: 10 scans or 3 rule-calibration findings, currently at 8 scans and 2 calibration findings). The Tier 1 API calls (Scorecard, osv.dev, deps.dev) can be adopted incrementally without an architectural pivot. The full pivot adds complexity and hard tool dependencies that contradict zero-install.
**Trigger to re-open:** 10 completed scans, or 3 rule-calibration findings, or a scan where grep-based detection produces a false negative that Scorecard/gitleaks would have caught.

### O2: 12 S8 Design Rules -> 5 Hard Rules
**Verdict:** DEFER
**Reasoning:** The 12 S8 rules exist because the HTML output quality matters (the audit itself praises it). Reducing to 5 hard rules risks regression in report quality. The real fix is O5/JSON-first, where the template handles design compliance and the LLM just provides data. Until then, the current 12 rules work well enough — 8 scans have produced good HTML.
**Trigger to re-open:** If a scan produces HTML that fails 4+ S8 rules, or when JSON-first lands.

### O5: JSON Evidence -> HTML Template
**Verdict:** DEFER
**Reasoning:** This IS V3.0. Our board already deferred it with triggers. The AXIOM council is restating our own roadmap item.
**Trigger to re-open:** Same as O1 — 10 scans or 3 rule-calibration findings.

### W3: /tmp Is Volatile
**Verdict:** DEFER
**Reasoning:** True but low-impact. Phase 2 can be long, but the head-sha.txt + findings-bundle copy pattern means re-running from the same SHA is straightforward. Adding checkpointing is 4+ hours of work for a failure mode that has not occurred in 8 scans.
**Trigger to re-open:** First crash that loses significant work, or when scan count reaches 15+.

### W5: Exhibit Rollup Trigger Unreliable
**Verdict:** DEFER
**Reasoning:** The 7+ items rollup is a nice-to-have UX feature. If the LLM doesn't trigger it, the report still works — it just has more items in a flat list. This is a cosmetic concern.
**Trigger to re-open:** JSON-first migration (where the renderer handles rollup deterministically).

### W6: Scorecard Thresholds Too Rigid
**Verdict:** DEFER
**Reasoning:** The 59%/60% threshold concern is valid in theory but the thresholds produce reasonable results in practice across 8 scans. Adjusting thresholds without data showing they cause wrong verdicts is premature optimization.
**Trigger to re-open:** A scan where the threshold produces a demonstrably wrong verdict.

### W7: Manual Pre-Render Checklist
**Verdict:** DEFER
**Reasoning:** `--bundle-check` automation was already deferred to V0.2 by our board. The manual checklist works — LLM operators follow it when it's in the Operator Guide flow.
**Trigger to re-open:** V0.2 Operator Guide cycle.

### B5: Path B Contradictions
**Verdict:** DEFER
**Reasoning:** The brief context says Path B was exercised (zustand-v2). The Operator Guide text is stale. This is a documentation update, not a functional bug. Low priority.
**What to change (when addressed):** Update Operator Guide to reflect that Path B has been exercised. Add zustand-v2 Path B artifacts to catalog.
**Trigger to re-open:** Next Operator Guide revision.

### B6: Step 8 Prerequisites Not Declared
**Verdict:** DEFER
**Reasoning:** Step 8 (install behavior analysis) is aspirational for repos with npm/pip/cargo packages. In practice, the LLM checks if the tools are available and skips if not. The prerequisites list is for the core scan; Step 8 tools are optional enhancements.
**Trigger to re-open:** When a scan produces a false "no install concerns" verdict because npm/pip wasn't available.

### Cap-4: Secrets-in-History Scanning (gitleaks/trufflehog)
**Verdict:** DEFER
**Reasoning:** Requires tool installation. Violates zero-install. The scanner already checks commit messages for secrets patterns — it's not as thorough as gitleaks but it's something. Add as Tier 2 opportunistic: if gitleaks is available, use it; if not, continue with current approach.
**Trigger to re-open:** When we add the Tier 2 opportunistic tool framework.

### Cap-5: Unauthenticated Fallback Mode
**Verdict:** DEFER
**Reasoning:** 60 req/hour is barely enough for Phase 1. The scanner requires `gh auth status` — if you don't have auth, you can't scan meaningfully. Not worth the engineering for a degraded experience.
**Trigger to re-open:** User request for public-only scanning.

### Cap-6: SBOM Generation
**Verdict:** DEFER
**Reasoning:** GitHub's `dependency-graph/sbom` endpoint requires repo admin or the dependency graph to be enabled. Same 403 problem as Dependabot. The osv.dev fallback (Cap-3) is more practical.
**Trigger to re-open:** When GitHub makes SBOM endpoint public.

### Cap-7: Release Signature Verification
**Verdict:** DEFER
**Reasoning:** Requires cosign/gpg installation. The scanner already checks whether .sig/.asc files exist in releases, which is the right level for a triage tool. Actual verification is a Tier 3 concern.
**Trigger to re-open:** Tier 3 tool framework.

### Cap-8: deps.dev Cross-Reference
**Verdict:** DEFER (but close to FIX NEXT)
**Reasoning:** Free API, zero install, useful data. But lower priority than Scorecard (Cap-1) and osv.dev (Cap-3). Add it after those two are integrated.
**Trigger to re-open:** After Cap-1 and Cap-3 are shipped.

### Cap-9: Fork Divergence Analysis
**Verdict:** DEFER
**Reasoning:** Niche. Most scans target original repos, not forks. When we do scan a fork, the LLM can manually check divergence with `gh api repos/OWNER/REPO --jq '.parent.full_name'`.
**Trigger to re-open:** First scan of a suspicious fork.

### Cap-10: Fake-Star Burst Detection
**Verdict:** DEFER
**Reasoning:** Interesting but complex. StarGuard's MAD algorithm requires historical star data that GitHub's API doesn't expose (only current stargazers, paginated). Not practical without a third-party data source.
**Trigger to re-open:** When a free star-history API becomes available.

### Cap-11: Reclaimed-Username Detection
**Verdict:** DEFER
**Reasoning:** Requires comparing historical contributor data with current account metadata. Gitxray does this but requires installation. The scanner already checks account age, which catches the most obvious cases.
**Trigger to re-open:** Tier 3 tool framework.

### Cap-12: Tampered Commit Timestamps
**Verdict:** DEFER
**Reasoning:** Interesting forensic check but extremely niche. Would require cloning the repo (not just tarball) to inspect git objects. Low priority.
**Trigger to re-open:** Evidence of timestamp manipulation in a scanned repo.

### Cap-13: Binary Entropy Analysis
**Verdict:** DEFER
**Reasoning:** No good tooling exists (the audit says so itself). The scanner already flags binary files in the repo. Entropy analysis is research-grade, not production-ready.
**Trigger to re-open:** When a reliable tool emerges.

### Cap-14: "Safer Alternative" Recommendations
**Verdict:** DEFER
**Reasoning:** Nice UX idea but requires a package recommendation database. Trusty has this for npm; nothing exists for pip/cargo/go. The scanner's job is assessment, not recommendation — "should I install this?" already includes alternatives when obvious.
**Trigger to re-open:** When deps.dev or similar provides alternative package data via API.

### Cap-15: SARIF Output
**Verdict:** DEFER
**Reasoning:** SARIF is for CI/CD integration into GitHub's Security tab. The scanner's value is the human-readable narrative, not machine-readable output. SARIF would be a parallel output format for a different audience. Not aligned with current users.
**Trigger to re-open:** When a user requests CI/CD integration.

---

## REJECT

### B4: Package Is Incomplete — Missing Referenced Artifacts
**Verdict:** REJECT
**Reasoning:** The zip was sent to ONE person as a test distribution, not a public release. The missing reference artifacts (caveman.html, .md companions) are in the repo — they just weren't included in the test zip. This is not a bug in the scanner; it's a packaging choice for a one-off test. When we do a real distribution, we'll include the right files.

---

## Summary Table

| Priority | IDs | Count |
|----------|-----|-------|
| FIX NOW | V1, V2, V3, V5, B1, B2 | 6 |
| FIX NEXT | V4, W1, W2, W4, O3, O4, B3, Cap-1, Cap-2, Cap-3 | 10 |
| DEFER | O1, O2, O5, W3, W5, W6, W7, B5, B6, Cap-4 through Cap-15 | 21 |
| REJECT | B4 | 1 |

## Key Disagreements with AXIOM Council

1. **"UNANIMOUS REWORK" is wrong.** This is a hardening pass, not a rework. 8 accurate scans prove the architecture works.
2. **V4 (shell injection) is overstated.** GitHub owner/repo names cannot contain shell metacharacters. The LLM constructs commands, not users. Still worth quoting for hygiene, but not MUST-HAVE.
3. **B4 (incomplete package) is a non-issue.** Test zip to one person != public release.
4. **The "orchestrate not reimplant" framing is partially wrong.** Tier 1 free APIs — yes, absolutely. Hard tool dependencies — no, that kills the zero-install value proposition.
5. **W1 (prompt length) impact is overstated.** "Research shows LLM instruction-following degrades past ~500 lines" is not supported by evidence for frontier models. The real issue is the changelog noise, which is a 15-minute fix.

## Capability Prioritization

Of the 15 capability items, only 3 would improve scan accuracy without adding tool dependencies:
1. **Cap-1 (OSSF Scorecard)** — free API, 24 checks, massive accuracy boost
2. **Cap-3 (osv.dev fallback)** — free API, fills the Dependabot 403 gap
3. **Cap-8 (deps.dev)** — free API, dependency metadata

Everything else either requires tool installation (violating zero-install) or addresses edge cases that haven't occurred in 8 scans.
