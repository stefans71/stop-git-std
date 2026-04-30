# Board Review R2+R3 — Implementation Verification + DEFER Reduction

**Date:** 2026-04-17
**Review type:** Implementation verification (R2) + DEFER deliberation (R3)
**Board:** Pragmatist (Claude Opus 4.6) + Systems Thinker (Codex GPT-5.4) + Skeptic (DeepSeek V3.2)
**Input:** Git diff of commits f517667 + 7b15466 (5 files, 299 insertions, 62 deletions)
**Rounds:** R2 (blind) + R3 (deliberation with visible votes)

---

## Job 1: Implementation Verification (R2 — unanimous)

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
1. **W2 rate-limit elif ordering** (Pragmatist): The `<500` skip branch is shadowed by `<1000` reduce. Conservative behavior still fires.
2. **osv.dev covers npm only** (Skeptic): Code block shows npm with comments for other ecosystems. LLM adapts at scan time.

---

## Job 2: DEFER Reduction — Full Voting Record

### R2 votes (blind) → R3 votes (after seeing each other)

#### Items where the board AGREED (no deliberation needed)

| ID | Finding | All 3 voted | Resolution |
|----|---------|-------------|------------|
| O1 | Orchestration pivot | KEEP DEFER | **DEFER** |
| O5 | JSON-first | MERGE→O1 (2/3 in R2, held R3) | **MERGE→O1** |
| W5 | Exhibit rollup | CLOSE | **CLOSE** |
| W7 | Pre-render checklist | CLOSE | **CLOSE** |
| B6 | Step 8 prerequisites | UPGRADE | **UPGRADE** |
| Cap-5 | Unauth fallback | CLOSE (2/3) | **CLOSE** |
| Cap-10 | Fake-star detection | CLOSE (2/3) | **CLOSE** |
| Cap-11 | Reclaimed-username | CLOSE (2/3) | **CLOSE** |
| Cap-12 | Tampered timestamps | CLOSE (2/3) | **CLOSE** |
| B4 | Package incomplete | CLOSE | **CLOSE** |

#### Items that went to R3 deliberation (11 disagreements)

| ID | Finding | Pragmatist R2→R3 | Systems Thinker R2→R3 | Skeptic R2→R3 | **Final** |
|----|---------|-----------------|----------------------|---------------|-----------|
| W3 | /tmp volatile | CLOSE→**CLOSE** | CLOSE→**CLOSE** | UPGRADE→**UPGRADE** | **CLOSE** (2/3) |
| W6 | Scorecard thresholds | CLOSE→**CLOSE** | UPGRADE→**CLOSE** | CLOSE→**CLOSE** | **CLOSE** (3/3) |
| B5 | Path B stale text | UPGRADE→**UPGRADE** | UPGRADE→**UPGRADE** | CLOSE→**UPGRADE** | **UPGRADE** (3/3) |
| Cap-4 | Secrets-in-history | DEFER→**DEFER** | CLOSE→**UPGRADE** | UPGRADE→**UPGRADE** | **UPGRADE** (2/3) |
| Cap-6 | SBOM endpoint | DEFER→**DEFER** | CLOSE→**DEFER** | DEFER→**DEFER** | **DEFER** (3/3) |
| Cap-7 | Release sig verify | DEFER→**DEFER** | CLOSE→**DEFER** | UPGRADE→**UPGRADE** | **DEFER** (2/3) |
| Cap-8 | deps.dev cross-ref | CLOSE→**CLOSE** | MERGE→**UPGRADE** | UPGRADE→**CLOSE** | **DEFER** (operator override — see note) |
| Cap-9 | Fork divergence | DEFER→**DEFER** | DEFER→**DEFER** | MERGE→**DEFER** | **DEFER** (3/3) |
| Cap-13 | Binary entropy | DEFER→**CLOSE** | CLOSE→**DEFER** | CLOSE→**CLOSE** | **CLOSE** (2/3) |
| Cap-14 | Safer alternatives | UPGRADE→**CLOSE** | CLOSE→**CLOSE** | CLOSE→**CLOSE** | **CLOSE** (3/3) |
| Cap-15 | SARIF output | CLOSE→**CLOSE** | MERGE→**MERGE→O1** | UPGRADE→**CLOSE** | **MERGE→O1** (operator override — see note) |

### R3 convergence improvements

4 items reached unanimity in R3 (up from R2):
- **W6** — ST dropped UPGRADE → CLOSE (Cap-1 already addresses thresholds with real Scorecard data)
- **B5** — Skeptic dropped CLOSE → UPGRADE (convinced by operational impact: stale Path B text causes agent failures)
- **Cap-9** — Skeptic dropped MERGE → DEFER (accepted standalone tracking)
- **Cap-14** — Pragmatist dropped UPGRADE → CLOSE (accepted scope boundary: scanner assesses, doesn't recommend)

1 item flipped outcome in R3:
- **Cap-4** — ST changed CLOSE → UPGRADE ("blast radius is high enough that 'not currently exposed' is not sufficient reason to close"). Now 2/3 UPGRADE.

### Operator overrides (2 items)

**Cap-8 (deps.dev) — CLOSE → DEFER.** R3 vote was 2/3 CLOSE, but the Systems Thinker's UPGRADE argument is compelling: deps.dev is a free API (same category as Scorecard + osv.dev we just adopted), provides transitive dependency metadata we can't get from manifest parsing, and addresses the #1 blind spot identified in our own Q2 external board brief. Track for V2.5 after Cap-1 and W4 are proven in production scans. Same pattern as the other free-API integrations.

**Cap-15 (SARIF) — CLOSE → MERGE→O1.** R3 vote was 2/3 CLOSE, but the Systems Thinker's MERGE→O1 is the cleanest disposition: SARIF is a structured output format that naturally belongs with JSON-first migration. Costs nothing to note as an O1 sub-deliverable. Prevents losing the thread without adding a separate tracking item.

---

## Final tracked items (8)

### DEFER (5)

| # | ID | Item | Trigger |
|---|-----|------|---------|
| 1 | O1+O5+Cap-15 | Orchestration pivot + JSON-first + SARIF output | 10 scans or 3 rule-calibration findings |
| 2 | Cap-6 | SBOM endpoint | GitHub improves coverage/access for non-admin |
| 3 | Cap-7 | Release sig verification | `gh attestation verify` stabilizes in GA |
| 4 | Cap-8 | deps.dev cross-reference | After Cap-1 + W4 proven in production scans |
| 5 | Cap-9 | Fork divergence analysis | First suspicious fork scan |

### FIX NEXT — V2.5 (3)

| # | ID | Item | Effort |
|---|-----|------|--------|
| 1 | B5 | Path B stale text cleanup in Operator Guide | 15 min |
| 2 | B6 | Document Step 8 prerequisites (npm/pip/cargo optional) | 10 min |
| 3 | Cap-4 | Secrets-in-history detection | Scope: opportunistic gitleaks if installed, else note "secrets-in-history not scanned" in Coverage |

### CLOSED (13)

O5 (merged→O1), W3, W5, W6, W7, Cap-5, Cap-10, Cap-11, Cap-12, Cap-13, Cap-14, Cap-15 (merged→O1), B4.

**Rationale for bulk closures:**
- **W3, W5, W6, W7:** Addressed by other work (durability policy, S8 reduction, Scorecard API, validator enhancements)
- **Cap-5:** Scanner requires auth by design
- **Cap-10–14:** Speculative, niche, require tools we won't install, or outside scope
- **O5, Cap-15:** Merged into O1 (not lost, just consolidated)

---

## Disagreements resolved in R3

### D1: W3 (/tmp volatile) — Skeptic vs Pragmatist+ST
- **Skeptic (UPGRADE):** "Volatile /tmp is a genuine security risk"
- **Pragmatist+ST (CLOSE):** Durability policy already mandates bundle copy; ephemeral workspace is by design
- **Resolution:** CLOSE. Workflow addresses this, not code.

### D2: Cap-4 (secrets-in-history) — flipped R2→R3
- **R2:** 3-way split (DEFER / CLOSE / UPGRADE)
- **R3:** ST changed to UPGRADE ("blast radius high enough"), joining Skeptic. Pragmatist held DEFER (zero-install constraint).
- **Resolution:** UPGRADE to FIX NEXT. Scoped as opportunistic: use gitleaks if installed, else note coverage gap. This preserves zero-install while adding the capability for operators who have gitleaks available.

### D3: Cap-8 (deps.dev) — operator override
- **R3 vote:** 2/3 CLOSE (Pragmatist + Skeptic) vs 1/3 UPGRADE (ST)
- **Override rationale:** Free API, same pattern as Scorecard + osv.dev. Addresses our #1 identified blind spot (transitive deps). ST's architectural argument is load-bearing.
- **Resolution:** DEFER (not CLOSE). Track for after current free-API integrations are proven.

### D4: Cap-15 (SARIF) — operator override
- **R3 vote:** 2/3 CLOSE vs 1/3 MERGE→O1
- **Override rationale:** MERGE→O1 costs nothing and prevents losing the thread. Clean bookkeeping.
- **Resolution:** MERGE→O1.

---

## Board response files

All raw board member responses preserved at:
```
docs/board-review-data/axiom-triage-responses/
├── context.md                    # Shared framing document
├── r1/
│   ├── brief.md                  # R1 instructions
│   ├── pragmatist.md             # Claude Opus 4.6
│   ├── systems-thinker.md        # Codex GPT-5.4
│   └── skeptic.md                # DeepSeek V3.2
├── r2/
│   ├── brief.md
│   ├── pragmatist.md
│   ├── systems-thinker.md
│   └── skeptic.md
└── r3/
    ├── brief.md
    ├── pragmatist.md
    ├── systems-thinker.md
    └── skeptic.md
```

---

*Board review conducted 2026-04-17. R2 (blind verification) + R3 (deliberation). 2 operator overrides applied on Cap-8 and Cap-15 per Systems Thinker's architectural reasoning.*
*Pragmatist: Claude Opus 4.6 | Systems Thinker: Codex GPT-5.4 | Skeptic: DeepSeek V3.2 (deepseek-chat)*
