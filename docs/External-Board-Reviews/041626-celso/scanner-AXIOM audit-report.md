# Full Council Audit — GitHub Repo Scanner v2.3
## Conducted 2026-04-17 by AXIOM Council (5 members) + Competitive Research

**Council:** Claude Opus 4.6, Codex GPT-5.3, ChatGPT 5.4, Gemini 3.1 Pro, DeepSeek V3.2
**Verdict:** UNANIMOUS REWORK (5/5)
**Repo:** stefans71/stop-git-std (github-repo-scanner-v2.3.zip, 13 files, 209KB)

---

## EXECUTIVE SUMMARY

This is an **impressively ambitious** project — a 13-file package that turns any LLM with terminal access into a GitHub repo security scanner producing beautiful dark-themed HTML reports for non-technical users. It has gone through 3 board reviews with 50+ fixes applied (F1-F16, C1-C20, S8-1 through S8-12). The investigation prompt covers areas that no single existing tool addresses: combined governance + code review + contributor + supply chain + behavior analysis, all synthesized into plain-English narrative.

**However, the scanner has critical security vulnerabilities in its own operation**, the prompt is beyond reliable LLM compliance at 1078 lines, and it manually reimplements checks that established tools (OSSF Scorecard, osv-scanner, gitleaks) already do better and for free.

**Bottom line:** The concept is strong. The execution needs a security hardening pass and an architectural pivot from "LLM does everything with grep" to "LLM orchestrates specialized tools and synthesizes their output."

---

## SECTION 1: CRITICAL VULNERABILITIES (Security of the Scanner Itself)

These must be fixed before ANY sharing. A security tool with security holes destroys user trust.

### V1. XSS in HTML Reports — Validator Is Not a Security Gate (5/5 consensus)

The `validate-scanner-report.py` checks structural HTML (tag balance, placeholders, inline styles, px font-sizes) but **does not block XSS vectors**:
- No check for `<script>` tags in body content
- No check for `javascript:` URLs in href/src attributes
- No check for event handler attributes (`onclick`, `onerror`, etc.)
- No check for `<iframe>`, `<embed>`, `<object>` tags
- The C4 heuristic only looks for bare `<` characters — properly-formed malicious tags pass cleanly

**Verified by Codex + ChatGPT 5.4:** A file containing `<img onerror="alert(1)">` and `<a href="javascript:alert(1)">` passes `--report` mode with exit 0.

**Impact:** The scanner takes untrusted data from repos (PR titles, issue titles, commit messages, file contents) and renders it into HTML. An attacker can craft a repo whose PR title contains XSS that executes in the browser of anyone viewing the report.

**Fix (MUST-HAVE):**
- Add XSS content checks to the validator: reject `on*=` attributes, `javascript:` URLs, `<script>` outside `<style>`, `<iframe>`, `<embed>`, `<object>`
- Add Content Security Policy (CSP) to the HTML template
- Remove inline event handlers from template (the `onclick` in font controls)

### V2. Path Traversal via Tarball Extraction (5/5 consensus)

The scanner extracts untrusted tarballs with `tar -xz -C "$SCAN_DIR" --strip-components=1` — no path traversal protection.

**Attack:** A malicious tarball containing `../../.ssh/authorized_keys` would write files outside the scan directory.

**Mitigation note:** GitHub's tar generation is unlikely to include traversal paths, BUT the Operator Guide explicitly supports GitHub Enterprise (GHE, §14.6), where a compromised instance could serve malicious tarballs.

**Fix (MUST-HAVE):**
- Add `--no-absolute-names` to tar command
- Validate all extracted paths are within `$SCAN_DIR` before any scanning
- Check tar exit status (currently only checks file count)

### V3. Symlink Attack — Host File Disclosure (4/5 consensus)

The scanner runs `grep -r` and `find` on extracted files. If the repo contains symlinks pointing outside the extraction directory (e.g., `README.md -> /etc/shadow`), grep follows them and reads host files.

**Verified by Codex:** `grep -r` follows symlinked files/directories when passed as arguments.

**Impact:** Sensitive host files get read into the LLM context and may appear in the final report.

**Fix (MUST-HAVE):**
- After extraction, strip all symlinks: `find "$SCAN_DIR" -type l -delete`
- Or use `find -type f -not -type l` to build file lists for grep
- Or extract with `--no-same-owner --no-same-permissions` + validate realpath

### V4. Shell Injection via Unquoted Variables (Claude, Codex)

Several commands use unquoted `$OWNER` and `$REPO`. The `for USER in $OWNER $(...)` loop (prompt line 126) is particularly fragile — repo/owner names with spaces or shell metacharacters would cause command injection.

**Fix (MUST-HAVE):** Quote all shell variables. Replace `for USER in $OWNER $(...)` with a `while read` loop.

### V5. SHA Truncation Weakens Commit Pinning (Codex, ChatGPT 5.4)

The prompt captures HEAD SHA then truncates to 7 chars (`head -c 7`) and uses the short SHA for tarball fetch. This undermines the F6 TOCTOU protection — short SHAs have collision risk.

**Fix (MUST-HAVE):** Use full 40-char SHA everywhere. Store full SHA in `head-sha.txt`, use full SHA for tarball fetch.

---

## SECTION 2: CONFIRMED BUGS

### B1. CSS Has Already Drifted — Template != Standalone File (5/5 consensus)

The template (`GitHub-Repo-Scan-Template.html:95-101`) has a `body::after` as "slow sweeping scan bar" (120px amber, 14s infinite loop). The standalone `scanner-design-system.css:59-66` has a "single-pass scan line" (2px cyan, 3s single animation). **These are completely different animations.** The "copy CSS verbatim" instruction is already violated in the canonical template itself. No sync mechanism exists.

### B2. PR Count Logic Is Wrong (Codex, ChatGPT 5.4)

The prompt's total-merged-PR detection uses `gh api "repos/OWNER/REPO/pulls?state=closed&per_page=1" --jq 'length'` — this returns 0 or 1, not the total count. The scanner cannot correctly report "sampled 300 of N total."

### B3. Validator Doesn't Actually Validate Markdown (ChatGPT 5.4)

The guide, CLAUDE.md, wizard, and Path B prompt all say "both MD and HTML must pass validation." But the validator is an HTML structural checker — a trivial Markdown file exits 0 under `--report`. This is false assurance.

### B4. Package Is Incomplete — Missing Referenced Artifacts (ChatGPT 5.4)

The prompt names `GitHub-Scanner-caveman.html` as the reference implementation. The wizard references caveman and archon-board-review. The catalog links `.md` companions. None of these are shipped in the v2.3 zip's `reference/` directory.

### B5. Path B Contradictions (ChatGPT 5.4)

The Operator Guide says Path B is "proposed — not yet exercised" (§8.2). But `path-b-test-prompt.md` claims PASS. The catalog shows all 7 entries used Path A. No Path B artifacts exist.

### B6. Step 8 Prerequisites Not Declared (ChatGPT 5.4)

The prerequisites list `gh`, `tar`, `python3`, `jq`. But Step 8 requires `npm view`, `pip download`, and release-download workflows that need `npm`/`pip`/`cargo` installed. These are aspirational on most LLM environments.

---

## SECTION 3: WEAKNESSES (Fragility & Failure Modes)

### W1. 1078-Line Prompt Exceeds Reliable LLM Compliance (5/5)

Research shows LLM instruction-following degrades past ~500 lines. The prompt has:
- 44 lines of changelog/version history (noise)
- 12 S8 design sub-rules
- 16 F-series fixes
- 20 C-series adjustments
- 15 D-series deferrals

Steps at the END of the prompt (Step C, scorecard calibration, evidence appendix) are most likely to be partially followed.

### W2. N x 2 API Calls in Step 5b Will Exhaust Rate Limit (5/5)

For each of up to 300 PRs, Step 5b calls `gh pr view` + `gh pr diff` = 600 API calls. Plus Step 5c diffs. Total: ~1200 API calls just for Step 5. GitHub limit: 5000/hour. No budget mechanism, no early exit, no sampling fallback.

### W3. /tmp Is Volatile (5/5)

A crash mid-Phase-2 (the longest phase, potentially hours) loses all gathered evidence. Only `head-sha.txt` and post-success bundle copy survive.

### W4. Dependabot Alerts Require Admin Scope (5/5)

Frequently returns 403. No fallback to `npm audit`, `pip-audit`, `osv-scanner`. Dependency vulnerability coverage is ZERO for non-admin users.

### W5. Exhibit Rollup Trigger Unreliable (Claude, DeepSeek)

The 7+ items → 3 themed panels requires the LLM to count items, determine severity similarity, then restructure into exhibit panels. LLMs are poor at counting and conditional restructuring.

### W6. Scorecard Thresholds Too Rigid (4/5)

59% any-review = amber, 60% = green is arbitrary precision on imprecise data computed from a 300-PR sample. Creates false confidence.

### W7. Manual Pre-Render Checklist (Claude, Codex, ChatGPT 5.4)

§9.2.1 is a manual checkbox list. `--bundle-check` automation deferred to V0.2. In practice, LLM operators skip this.

---

## SECTION 4: MISSING CAPABILITIES (Priority-Ranked)

### HIGH PRIORITY

| # | Capability | Consensus | Best-in-Class Competitor |
|---|-----------|-----------|-------------------------|
| 1 | **OSSF Scorecard integration** | 5/5 | ossf/scorecard — 24 checks, 0-10 scoring, free API at `api.securityscorecards.dev` |
| 2 | **Rate-limit awareness + budget** | 5/5 | (No competitor — unique gap) |
| 3 | **Dependency vuln fallback** (osv-scanner / npm audit / pip-audit) | 5/5 | Socket.dev behavioral analysis, Snyk dependency paths |
| 4 | **Secrets-in-history scanning** (gitleaks/trufflehog) | 5/5 | gitxray (Kali Linux included) |
| 5 | **Unauthenticated fallback mode** | 4/5 | (60 req/hour public API) |

### MEDIUM PRIORITY

| # | Capability | Consensus | Best-in-Class Competitor |
|---|-----------|-----------|-------------------------|
| 6 | **SBOM generation** (`dependency-graph/sbom` endpoint) | 4/5 | GitHub native |
| 7 | **Release signature verification** (actual `cosign`/`gpg` verify) | 4/5 | Stacklok Trusty — sigstore provenance |
| 8 | **deps.dev cross-reference** | 3/5 | deps.dev API (free) |
| 9 | **Fork divergence analysis** | 3/5 | (No good competitor) |
| 10 | **Fake-star burst detection** | 2/5 | StarGuard — sliding-window MAD algorithm |

### LOW PRIORITY (but would differentiate)

| # | Capability | Source |
|---|-----------|--------|
| 11 | **Reclaimed-username detection** | Gitxray — detects deleted accounts re-registered by attackers |
| 12 | **Tampered commit timestamps** | Gitxray — detects repos faking their age |
| 13 | **Binary entropy analysis** | (No good OSS tool) |
| 14 | **"Safer alternative" recommendations** | Stacklok Trusty — suggests less-risky packages |
| 15 | **SARIF output** for GitHub Security tab integration | Allstar |

---

## SECTION 5: COMPETITIVE LANDSCAPE

### The Scanner's Unique Edge (No Competitor Has This)

1. **Plain-English narrative report** — Every existing tool outputs tables/JSON/badges. NONE produce a narrative a non-developer can read.
2. **Zero-install LLM approach** — Every other tool requires installation. The prompt-to-`gh`-CLI approach is frictionless.
3. **Combined multi-domain analysis** — StarGuard does stars, Gitxray does contributors, Scorecard does practices, Socket does behavior. Nobody combines all four.
4. **Beautiful dark-theme reports** — The HTML output is genuinely impressive. No security tool comes close to this UX.

### Where Competitors Are Better

| Area | Competitor | Gap |
|------|-----------|-----|
| Governance scoring | **OSSF Scorecard** (24 checks, 0-10 per-check) | Scanner manually reimplements ~60% of what Scorecard computes for free |
| Dependency vulns | **Snyk/Socket.dev** (deep dep-tree analysis) | Scanner has zero coverage when Dependabot 403s |
| Secrets detection | **Gitleaks** (regex + entropy on full history) | Scanner only greps commit messages |
| Install behavior | **Socket.dev** (static analysis of what code DOES) | Scanner greps patterns but doesn't model data flows |
| Star fraud | **StarGuard** (MAD algorithm + account profiling) | Scanner mentions star count but doesn't analyze curve |
| Identity forensics | **Gitxray** (SSH key fingerprinting, username reclamation) | Scanner checks account age only |
| Release integrity | **Stacklok Trusty** (sigstore verification) | Scanner checks if .sig files exist, doesn't verify |

### Recommended Integration Strategy

**Tier 1 — Free API calls, add immediately:**
```bash
# OSSF Scorecard (auth-free, computes 24 checks)
curl -s "https://api.securityscorecards.dev/projects/github.com/OWNER/REPO"

# deps.dev (auth-free, dependency analysis)
curl -s "https://api.deps.dev/v3/projects/github.com%2FOWNER%2FREPO"

# OSV.dev (auth-free, vulnerability lookup)
curl -s "https://api.osv.dev/v1/query" -d '{"package":{"name":"PKG","ecosystem":"npm"}}'
```

**Tier 2 — Require tool installation, recommend in prerequisites:**
```bash
# gitleaks (secrets-in-history)
gitleaks git --source "$SCAN_DIR" --redact --report-format json

# osv-scanner (dependency vulns when Dependabot 403s)
osv-scanner scan --lockfile "$SCAN_DIR/package-lock.json"
```

**Tier 3 — Nice-to-have, add when capacity allows:**
- StarGuard-style star-velocity analysis
- Gitxray-style contributor identity checks
- Trusty-style "safer alternative" suggestions

---

## SECTION 6: OVERENGINEERING / SIMPLIFICATION

### O1. LLM Should Orchestrate, Not Reimplant (Gemini, DeepSeek — strongest recommendation)

**The architectural pivot:** Stop using the LLM to grep for security patterns. Instead:
1. Run OSSF Scorecard, osv-scanner, gitleaks as data sources
2. Use the LLM to synthesize their outputs into plain-English narrative
3. LLM adds the governance/contributor/behavioral analysis that tools can't do

This cuts token cost ~40%, improves accuracy, and removes the "grep-based security" fragility.

### O2. 12 S8 Design Rules → 5 Hard Rules (5/5)

Currently: 12 sub-rules each requiring specific CSS classes. LLMs reliably follow ~7-8 of these. The later rules (S8-9 timeline labels, S8-10 inventory quick-scan, S8-11 split-verdict) are inconsistently applied.

**Recommendation:** Keep 5 hard rules (utility classes, no inline styles, status chips, action hints, rem font-sizes). Make the rest "recommended patterns shown in reference scans."

### O3. Move 44 Lines of Changelog Out of Prompt (5/5)

The version history (V2.1/V2.2/V2.3 changes, deferred items D1-D15, board review references) consumes prompt context the LLM reads but cannot act on. Move to `CHANGELOG.md`.

### O4. Single CSS Source of Truth (5/5)

Pick ONE: template's `<style>` block OR `scanner-design-system.css`. Delete the other. Add a CI/build step to prevent drift.

### O5. Consider JSON Evidence → HTML Template (Gemini, ChatGPT 5.4)

Instead of having the LLM generate complex HTML directly:
1. LLM produces structured JSON evidence bundle
2. A Jinja2/Handlebars template renders the HTML from JSON
3. This eliminates most design-compliance issues and makes the validator meaningful

This is the V3.0 architectural direction the prompt already hints at (JSON-first migration).

---

## SECTION 7: MUST-HAVE FIX LIST (Ordered by Priority)

| # | Fix | Effort | Impact |
|---|-----|--------|--------|
| 1 | **Strip symlinks after extraction** (`find -type l -delete`) | 5 min | Blocks host-file disclosure |
| 2 | **Add `--no-absolute-names` to tar** | 1 min | Blocks path traversal |
| 3 | **Add XSS checks to validator** (event handlers, javascript: URLs, script tags) | 2 hrs | Blocks stored XSS in reports |
| 4 | **Add CSP to HTML template** | 30 min | Defense-in-depth for XSS |
| 5 | **Fix CSS drift** — pick one source, delete the other | 15 min | Eliminates live bug |
| 6 | **Use full 40-char SHA** everywhere | 15 min | Fixes commit pinning |
| 7 | **Quote all shell variables** | 30 min | Blocks shell injection |
| 8 | **Move changelog out of prompt** | 15 min | Improves LLM compliance |
| 9 | **Add OSSF Scorecard API call** | 1 hr | Adds 24 free security checks |
| 10 | **Add rate-limit check before Step 5** | 30 min | Prevents quota exhaustion |
| 11 | **Fix PR count logic** (use `gh pr list --json number --jq 'length'`) | 10 min | Fixes sampling disclosure |
| 12 | **Ship missing reference artifacts** (caveman, .md companions) | varies | Fixes incomplete package |

---

## SECTION 8: NICE-TO-HAVE LIST

| # | Improvement | Effort | Impact |
|---|-------------|--------|--------|
| 1 | Add `--quick` scan mode (skip Steps 5b/5c/8/A) | 2 hrs | ~30% cost reduction |
| 2 | Embed fonts or use system-only fallback (offline rendering) | 1 hr | Removes CDN dependency |
| 3 | Add gitleaks + osv-scanner as recommended prereqs | 30 min | Secrets + dep vuln coverage |
| 4 | Automate pre-render checklist | 2 hrs | Replaces manual step |
| 5 | Add checkpointing in Phase 2 | 4 hrs | Crash recovery |
| 6 | Exercise Path B with real catalog entry | 2 hrs | Validates delegation |
| 7 | Add fake-star detection (StarGuard algorithm) | 4 hrs | Unique differentiator |
| 8 | Add "safer alternative" suggestions (Trusty-style) | 4 hrs | UX win for non-technical users |
| 9 | Build Markdown-specific validator | 2 hrs | Fixes false MD assurance |
| 10 | Add Docker containerization option | 4 hrs | Sandbox all security concerns |

---

## SECTION 9: OVERALL ASSESSMENT

### What's Great
- **Concept is genuinely novel.** No existing tool produces a plain-English narrative security report for non-technical users. The scanner fills a real gap.
- **Beautiful output.** The dark-theme forensic-console HTML with collapsible sections, split verdicts, and exhibit rollups is best-in-class UX for security findings.
- **Thorough investigation scope.** The prompt covers governance, code review, supply chain, CI/CD, contributor identity, install behavior, agent-rule files, and README paste-injection — a breadth no single tool matches.
- **Evidence discipline.** The fact/inference/synthesis separation, evidence appendix, and citation rules are excellent architectural choices.
- **Three rounds of board review.** The 50+ fixes show genuine iteration and quality improvement.

### What Needs Work
- **The scanner itself is vulnerable.** XSS, path traversal, symlink attacks, and shell injection in a security tool is a credibility-killer. These are the #1 priority.
- **Too much LLM, not enough tooling.** The scanner manually greps for security patterns that OSSF Scorecard, gitleaks, and osv-scanner already detect better. The LLM should orchestrate and synthesize, not reimplant.
- **Prompt is too long.** 1078 lines with embedded changelogs, deferred items, and 12 design sub-rules degrades compliance. The later rules are followed inconsistently.
- **No rate-limit awareness.** Will break on any popular repo.

### The Single Most Important Improvement

**Harden the scanner's own input boundary.** Fix symlink stripping, path traversal protection, XSS validation, and shell quoting. A security tool that can be exploited by the very repos it scans is fundamentally broken. Everything else — OSSF integration, rate limiting, prompt refactoring — is secondary to making the scanner itself secure.

### Would We Recommend It?

**Not yet for non-technical users.** After the security hardening pass (Section 7, items 1-7), it would be safe. After the OSSF Scorecard integration and prompt refactoring (items 8-10), it would be genuinely useful. The concept, design, and execution quality are strong — the gaps are fixable, not architectural.

---

*Council members: Claude Opus 4.6, Codex GPT-5.3, ChatGPT 5.4, Gemini 3.1 Pro, DeepSeek V3.2*
*Competitive research: 10 tools analyzed (OSSF Scorecard, StarGuard, Gitxray, Snyk, Socket.dev, Stacklok Trusty, GitHub Security Lab Taskflow Agent, Allstar, SAP Fosstars, GitHub Native Security Features)*
*Audit date: 2026-04-17*

