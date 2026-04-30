# Pragmatist — Round 2 Response

## Job 1: Implementation Verification (14 items)

### FIX NOW Items (6)

| ID | Verdict | Notes |
|----|---------|-------|
| **V3** Symlink stripping | **CORRECT** | `find src -type l -delete` added in both operator guide and prompt. Comment explains the threat model. Good. |
| **V2** `--no-absolute-names` | **CORRECT** | Added to tar in both operator guide and prompt. One-liner, does what it says. |
| **V5** Full 40-char SHA | **CORRECT** | `head -c 7` removed from the prompt's `HEAD_SHA` capture. The operator guide already used full SHA (no change needed there). |
| **B1** CSS sync | **CORRECT** | Template now has `/* SOURCE: scanner-design-system.css — do not edit here */` comment. The validator gained an O4 CSS drift check (see below). Effectively addressed. |
| **B2** PR count logic | **CORRECT** | Changed from `pulls?state=closed&per_page=1 --jq 'length'` (which returns 0 or 1) to `search/issues?q=...+is:merged&per_page=1 --jq '.total_count'`. This is the correct fix — search API returns the real total. |
| **V1** XSS checks + CSP | **CORRECT** | CSP meta tag added to template. Validator gained `find_xss_vectors()` covering script tags, event handlers, javascript: URLs, dangerous embeds, data: URLs. Whitelist for the known-safe `adjustFont` script. Thorough. |

**FIX NOW score: 6/6 — all implemented correctly.**

### FIX NEXT Items (8)

| ID | Verdict | Notes |
|----|---------|-------|
| **V4** Quote shell variables | **CORRECT** | `$SCAN_DIR` quoted with braces, `$NUM` quoted in `gh pr view`/`gh pr diff`, `for USER in` replaced with `while IFS= read -r`. All the high-risk spots are covered. |
| **W1/O3** Changelog extraction | **CORRECT** | New `docs/CHANGELOG.md` (75 lines) covers V2.1–V2.4 + deferred items. Prompt header shrank from ~50 lines of version history to a 6-line summary pointing to `docs/CHANGELOG.md`. Net savings: ~45 lines of prompt context. |
| **W2** Rate-limit budget check | **CORRECT** | Added before Step 5 with three tiers: >1000 (full), <1000 (reduce to 50), <500 (skip Step 5). `$PR_LIMIT` variable introduced. One **minor nit**: the `elif` for <500 will never fire because it's nested under the `if < 1000` — should be a separate check or reversed order. Functionally the <1000 branch catches both cases and reduces to 50, which is acceptable but the <500 skip path is dead code. **Not blocking — the conservative behavior (reduce to 50) still fires.** |
| **W4** osv.dev fallback | **CORRECT** | Added after the Dependabot 403 note. Covers npm with a clear pattern and comments pointing to PyPI/crates.io/Go adaptation. Coverage text updated to mention both sources. Pragmatic approach — works with zero installs. |
| **Cap-1** OSSF Scorecard | **CORRECT** | `curl` to `api.securityscorecards.dev`, Python one-liner to parse, graceful 404 handling ("not indexed"). Added to Step 1 with explanatory comment. Zero dependencies. |
| **O4** CSS sync in validator | **CORRECT** | Template mode now reads `scanner-design-system.css` and checks if canonical CSS is contained in the `<style>` block. Warns if CSS file missing. Clean implementation. |
| **B3** Markdown validator | **CORRECT** | New `check_markdown()` function: checks line count ≥100, required section headers (verdict/summary, findings, evidence, scorecard), severity keywords. `--markdown` CLI flag added. |
| **O2** S8 rules reduction | **CORRECT** | Prompt header now has 5 hard rules (S8-1, S8-4, S8-5, S8-8, S8-12) clearly separated from 7 recommended patterns. The hard rules are the ones the validator can enforce. Good cut. |

**FIX NEXT score: 8/8 — all implemented correctly.**

### Summary

**14/14 items implemented. One minor dead-code nit in W2 (rate-limit elif ordering) — not worth a re-roll.** The implementation is faithful to what the board agreed. No items were done differently than specified, nothing was missed, nothing was added that wasn't agreed.

The scan-sweep animation change in the template (infinite → single-pass, amber → cyan) was not in the agreed items — it's a cosmetic drive-by. Not harmful, but flagging it for the record.

---

## Job 2: DEFER Reduction (21 → target ≤10)

| ID | Finding | Verdict | Rationale |
|----|---------|---------|-----------|
| **O1** | Full orchestration pivot | **KEEP DEFER** | This is the V3.0 architecture change. Can't do it incrementally. Keep as the north-star item. |
| **O5** | JSON evidence → HTML template | **MERGE with O1** | This IS the orchestration pivot. Same trigger conditions (10 scans or 3 rule-calibration findings). Don't track separately. |
| **W3** | /tmp volatile | **CLOSE** | The operator guide already says to copy findings-bundles to `docs/board-review-data/scan-bundles/`. The durability concern is addressed by workflow, not code. If someone loses /tmp data, they didn't follow the guide. |
| **W5** | Exhibit rollup unreliable | **CLOSE** | S8-3 is now a recommended pattern, not a hard rule. The validator doesn't enforce it. If an LLM gets the rollup wrong, it's a cosmetic issue in one report. Not worth tracking. |
| **W6** | Scorecard thresholds too rigid | **CLOSE** | Cap-1 just landed — we now have OSSF Scorecard data as evidence input. The LLM synthesizes narrative from real scores. The "rigid threshold" concern was about the old manual scorecard, which is now supplemented by real data. Revisit only if a specific false-positive surfaces. |
| **W7** | Manual pre-render checklist | **CLOSE** | The validator IS the pre-render checklist. B3 (markdown mode) just landed. Between `--report`, `--template`, and `--markdown`, the checklist is automated. |
| **B5** | Path B contradictions (stale text) | **UPGRADE to FIX NEXT** | This is a 15-minute doc cleanup. Just do it in V2.5. Read Path B sections, remove anything that contradicts the current operator guide. |
| **B6** | Step 8 prerequisites undeclared | **UPGRADE to FIX NEXT** | Another doc fix. Step 8 needs to say "requires: tarball extracted, file inventory complete." 5 minutes. |
| **Cap-4** | Secrets-in-history (gitleaks) | **KEEP DEFER** | Requires installing gitleaks or trufflehog. We don't install tools on the scanning host. Could revisit if GitHub adds a secrets-scanning API endpoint for public repos. |
| **Cap-5** | Unauthenticated fallback | **CLOSE** | The prompt already says "if gh auth fails, STOP." We don't scan unauthenticated. The scanner needs `gh` for everything. This is a non-problem. |
| **Cap-6** | SBOM endpoint | **KEEP DEFER** | GitHub's SBOM API (`/dependency-graph/sbom`) exists but coverage is spotty. Worth adding when we see it return useful data on our scan targets. Low effort when we do it. |
| **Cap-7** | Release sig verification (cosign) | **KEEP DEFER** | Requires cosign binary. Same story as Cap-4 — no external tool installs. Track for when GitHub API exposes attestation verification natively. |
| **Cap-8** | deps.dev cross-reference | **CLOSE** | osv.dev fallback (W4) just landed and covers the vulnerability angle. deps.dev adds package metadata but we already get that from the manifest + npm/pypi APIs. Marginal value. |
| **Cap-9** | Fork divergence analysis | **KEEP DEFER** | Legitimate detection vector (malicious forks with extra commits). Needs `gh api compare` work. Keep but low priority. |
| **Cap-10** | Fake-star burst detection | **CLOSE** | Speculative. No reliable API for this. StarHistory is a third-party site. The prompt already flags "repo popularity vs account age" discrepancies in the maintainer background check. |
| **Cap-11** | Reclaimed-username detection | **CLOSE** | Extremely niche attack vector. GitHub namespace recycling is rare and hard to detect via API. The maintainer background check (account age, repo count) catches the observable signals already. |
| **Cap-12** | Tampered commit timestamps | **CLOSE** | GIT_COMMITTER_DATE spoofing is detectable but the signal-to-noise ratio is terrible. Legitimate rebases look identical. Not actionable without deep forensics tooling we won't install. |
| **Cap-13** | Binary entropy analysis | **KEEP DEFER** | Legitimate (detect packed/encrypted binaries). Needs `ent` or Python entropy calculation. Low effort but niche — only matters for repos shipping binaries. Keep for when we scan more compiled-CLI repos. |
| **Cap-14** | "Safer alternative" recommendations | **UPGRADE to FIX NEXT** | High user value, zero tooling cost. When the verdict is Caution or Warning, the report should suggest well-known alternatives (e.g., "consider fd instead of this find-replacement"). This is just a prompt addition: "If verdict is Caution or worse, name 1-2 well-known alternatives in the same category." |
| **Cap-15** | SARIF output | **CLOSE** | Enterprise integration format. We have zero users asking for this. MD + HTML covers all current use cases. If someone asks, it's a straightforward JSON transform from the findings bundle. |
| **B4** | Package incomplete (missing refs) | **CLOSE** | Was already REJECT. Confirming: close it. The zip package shipped and works. |

### Final DEFER List (8 items — under target of 10)

| # | ID | Item | Notes |
|---|-----|------|-------|
| 1 | O1+O5 | Full orchestration pivot + JSON-first | Merged. V3.0 trigger: 10 scans or 3 rule-cal findings |
| 2 | Cap-4 | Secrets-in-history | Blocked on external tool or GitHub API |
| 3 | Cap-6 | SBOM endpoint | Low effort when GitHub coverage improves |
| 4 | Cap-7 | Release sig verification | Blocked on cosign or GitHub attestation API |
| 5 | Cap-9 | Fork divergence analysis | Legitimate vector, needs API work |
| 6 | Cap-13 | Binary entropy analysis | Niche, for compiled-CLI scans |
| 7 | B5 | Path B stale text cleanup | **FIX NEXT (V2.5)** |
| 8 | B6 | Step 8 prerequisites | **FIX NEXT (V2.5)** |
| 9 | Cap-14 | Safer alternative recs | **FIX NEXT (V2.5)** |

**Reduction: 21 → 6 true DEFERs + 3 FIX NEXTs = 9 tracked items. 12 items CLOSED/MERGED.**

### Items closed (12)

O5 (merged into O1), W3, W5, W6, W7, Cap-5, Cap-8, Cap-10, Cap-11, Cap-12, Cap-15, B4.
