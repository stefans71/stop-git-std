# Board Review R2 — Implementation Verification + DEFER Reduction

**Date:** 2026-04-17
**Review type:** Implementation verification + backlog cleanup
**Board:** Pragmatist (Claude Opus 4.6) + Systems Thinker (Codex GPT-5.4) + Skeptic (DeepSeek V3.2)
**Input:** Git diff of commits f517667 + 7b15466 (5 files, 299 insertions, 62 deletions)

---

## Job 1: Implementation Verification

**Result: 14/14 items implemented correctly. All 3 board members confirm.**

| ID | Item | Pragmatist | Systems Thinker | Skeptic |
|----|------|-----------|-----------------|---------|
| V3 | Symlink stripping | CORRECT | CORRECT | CORRECT |
| V2 | Path traversal protection | CORRECT | CORRECT | CORRECT |
| V5 | Full 40-char SHA | CORRECT | CORRECT | CORRECT |
| B1 | CSS sync | CORRECT | CORRECT | CORRECT |
| B2 | PR count fix | CORRECT | CORRECT | CORRECT |
| V1 | XSS validator + CSP | CORRECT | CORRECT | CORRECT |
| V4 | Shell quoting | CORRECT | CORRECT | CORRECT |
| W1/O3 | Changelog extraction | CORRECT | CORRECT | CORRECT |
| W2 | Rate-limit budget | CORRECT | CORRECT | CORRECT |
| W4 | osv.dev fallback | CORRECT | CORRECT | CORRECT |
| Cap-1 | OSSF Scorecard API | CORRECT | CORRECT | CORRECT |
| O4 | CSS sync in validator | CORRECT | CORRECT | CORRECT |
| B3 | Markdown validator | CORRECT | CORRECT | CORRECT |
| O2 | S8 rule reduction | CORRECT | CORRECT | CORRECT |

### Minor nits (non-blocking)

1. **W2 rate-limit elif ordering** (Pragmatist): The `<500` skip branch is shadowed by the `<1000` reduce branch. Conservative behavior still fires (reduces to 50). Not worth a re-roll.
2. **osv.dev only implements npm** (Skeptic): The fallback code block covers npm with comments pointing to PyPI/crates.io/Go. The LLM adapts these at scan time — this is instructions, not a script.
3. **Scan-sweep animation** (Pragmatist): Cosmetic drive-by change in template (infinite amber → single-pass cyan). Not in agreed items, not harmful.

---

## Job 2: DEFER Reduction — 21 → 7 tracked items

### Consensus matrix

| ID | Finding | Pragmatist | Systems Thinker | Skeptic | **Final** |
|----|---------|-----------|-----------------|---------|-----------|
| O1 | Full orchestration pivot | KEEP DEFER | KEEP DEFER | KEEP DEFER | **DEFER** |
| O5 | JSON-first migration | MERGE→O1 | MERGE→O1 | KEEP DEFER | **MERGE→O1** |
| W3 | /tmp volatile | CLOSE | CLOSE | UPGRADE | **CLOSE** (2/3) |
| W5 | Exhibit rollup unreliable | CLOSE | CLOSE | CLOSE | **CLOSE** (3/3) |
| W6 | Scorecard thresholds | CLOSE | UPGRADE | CLOSE | **CLOSE** (2/3) |
| W7 | Manual pre-render checklist | CLOSE | CLOSE | CLOSE | **CLOSE** (3/3) |
| B5 | Path B stale text | UPGRADE | UPGRADE | CLOSE | **UPGRADE** (2/3) |
| B6 | Step 8 prerequisites | UPGRADE | UPGRADE | UPGRADE | **UPGRADE** (3/3) |
| Cap-4 | Secrets-in-history | KEEP DEFER | CLOSE | UPGRADE | **DEFER** (no consensus, default conservative) |
| Cap-5 | Unauthenticated fallback | CLOSE | CLOSE | KEEP DEFER | **CLOSE** (2/3) |
| Cap-6 | SBOM endpoint | KEEP DEFER | CLOSE | KEEP DEFER | **DEFER** (2/3) |
| Cap-7 | Release sig verification | KEEP DEFER | CLOSE | UPGRADE | **DEFER** (Pragmatist+Skeptic both say keep/upgrade) |
| Cap-8 | deps.dev cross-reference | CLOSE | MERGE→W4 | UPGRADE | **CLOSE** (2/3 close/merge) |
| Cap-9 | Fork divergence analysis | KEEP DEFER | KEEP DEFER | MERGE | **DEFER** (2/3) |
| Cap-10 | Fake-star detection | CLOSE | CLOSE | MERGE | **CLOSE** (2/3) |
| Cap-11 | Reclaimed-username | CLOSE | CLOSE | MERGE | **CLOSE** (2/3) |
| Cap-12 | Tampered timestamps | CLOSE | CLOSE | MERGE | **CLOSE** (2/3) |
| Cap-13 | Binary entropy analysis | KEEP DEFER | CLOSE | CLOSE | **CLOSE** (2/3) |
| Cap-14 | Safer alternative recs | UPGRADE | CLOSE | CLOSE | **CLOSE** (2/3) |
| Cap-15 | SARIF output | CLOSE | MERGE→O1 | UPGRADE | **CLOSE** (2/3) |
| B4 | Package incomplete | CLOSE | CLOSE | CLOSE | **CLOSE** (3/3) |

### Final tracked items (7)

**DEFER (5):**

| # | ID | Item | Trigger |
|---|-----|------|---------|
| 1 | O1+O5 | Full orchestration pivot + JSON-first (merged) | 10 scans or 3 rule-calibration findings |
| 2 | Cap-4 | Secrets-in-history scanning | GitHub API for secrets scanning, or opportunistic gitleaks |
| 3 | Cap-6 | SBOM endpoint | GitHub improves coverage/access |
| 4 | Cap-7 | Release signature verification | GitHub attestation API or opportunistic cosign |
| 5 | Cap-9 | Fork divergence analysis | First suspicious fork scan |

**FIX NEXT — V2.5 (2):**

| # | ID | Item | Effort |
|---|-----|------|--------|
| 1 | B5 | Update Path B text in Operator Guide (stale "not yet exercised") | 15 min |
| 2 | B6 | Document Step 8 prerequisites (npm/pip/cargo optional) | 10 min |

### CLOSED (14 items — no longer tracked)

O5 (merged→O1), W3, W5, W6, W7, Cap-5, Cap-8, Cap-10, Cap-11, Cap-12, Cap-13, Cap-14, Cap-15, B4.

**Rationale for bulk closures:**
- **W3, W5, W6, W7:** Addressed by other work (validator enhancements, OSSF Scorecard, S8 reduction) or acceptable operating assumptions
- **Cap-5, Cap-8:** Scanner requires auth; deps.dev overlaps with osv.dev already added
- **Cap-10–15:** Speculative, niche, or require tools we won't install. Zero users requesting these.

---

## Disagreements resolved

### D1: W3 (/tmp volatile) — Skeptic vs Pragmatist+ST
- **Skeptic:** UPGRADE — "real security issue, use mktemp with cleanup trap"
- **Pragmatist+ST:** CLOSE — workflow already copies durable artifacts; ephemeral workspace is by design
- **Resolution:** CLOSE. The Operator Guide's §12 durability policy (head-sha.txt + bundle copy on success) is the right answer. /tmp volatility is an operating assumption, not a defect.

### D2: Cap-4 (secrets scanning) — 3-way split
- **Pragmatist:** DEFER (needs external tool)
- **ST:** CLOSE (too expensive)
- **Skeptic:** UPGRADE (critical for supply chain)
- **Resolution:** DEFER. The zero-install constraint blocks gitleaks integration today. Track for when GitHub exposes a secrets-scanning API for public repos, or when the opportunistic tool framework (Tier 2) is built.

### D3: Cap-14 (safer alternatives) — Pragmatist vs ST+Skeptic
- **Pragmatist:** UPGRADE — "high user value, just add a prompt line"
- **ST+Skeptic:** CLOSE — "out of scope, we detect risks not recommend packages"
- **Resolution:** CLOSE. The scanner assesses trustworthiness; recommending alternatives requires a package database we don't have. The LLM can already suggest alternatives in the "Should I install?" post-scan summary without a formal framework.

---

*Board review conducted 2026-04-17. Round 2 verification + backlog cleanup.*
*Pragmatist: Claude Opus 4.6 | Systems Thinker: Codex GPT-5.4 | Skeptic: DeepSeek V3.2 (deepseek-chat)*
