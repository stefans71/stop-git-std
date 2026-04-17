# Board Review ROUND 2 — Caveman Report + Prompt V2.2 — Consolidated Findings

**Date:** 2026-04-16
**Artifacts reviewed:** V2.2 prompt + corrected caveman report (post-V2.2 edits)
**Reviewers:** Pragmatist (Claude Opus, self-review), Systems Thinker (GPT-5 Codex), Skeptic (DeepSeek V3.2)
**Raw responses:** `/tmp/board-caveman-v22/{codex,deepseek,pragmatist}-response.md`

**Round 2 tallies:**
- Pragmatist: 11 findings (7 FIX NOW, 3 DEFER, 1 INFO)
- Systems Thinker: 6 findings (5 FIX NOW, 1 DEFER)
- Skeptic: 12 findings (7 FIX NOW, 4 DEFER, 1 INFO)
- Total raw: 29 findings

**DEFER status carried forward:** 8 items from Round 1 (D1–D8). Round 2 elevated D3, D5, D6 to FIX NOW. D1/D2/D4/D7/D8 remain deferred.

---

## TOP-LEVEL RESULT

**V2.2 partially closed Round 1's gaps.** The prompt rules (F1–F16) are all in the document. But the caveman reference report — which every future scan uses as a template — under-delivers on three of those rules:

1. **F12 two-layer inventory** — specified in V2.2 prompt, silently not executed in the caveman report (still V2.1 flat cards)
2. **F9 imperative AI language severity** — prompt table says "always X / never Y = Warning", report downgraded to Info on an undocumented "surrounding context" exception
3. **F1 installed-artifact verification** — detection landed (Finding 3b flags 0/6 channels verified), but Step 8 provides no real verification commands for Claude Code plugins; the "verification" is inferred from install-script content only

**Unanimous new blind spot:** the verdict/distribution-channel contradiction. The report says "install channels all fetch from live main" AND "installing now is fine" in the same document. All three reviewers caught this independently.

**Biggest missing conceptual piece (new in Round 2):** the report documents no-branch-protection + no-CODEOWNERS + live-main distribution + CI rule amplification + 15% review rate as **five separate ambers**, but never synthesizes them into the one coherent supply-chain-compromise attack tree. Codex #5 is the sharpest formulation of this.

---

## CONVERGENT FIX NOW (2+ reviewers — ship to V2.3 or report corrections now)

### G1. Verdict vs distribution-channel contradiction
**Raised by:** Codex #1, Skeptic #2, Pragmatist P2-5 (related)
**Gap:** Report simultaneously says "every install channel fetches from live main, no pinning" (Finding 3b) AND "if you're considering installing for the first time: installing now is fine — the hardened version is what you get" (What Should I Do?). These invert each other.
**Ship:** Rewrite new-user guidance: "The v1.6.0 source is clean, but no install path resolves to v1.6.0 specifically — every channel tracks `main`. Before installing, either (a) wait for maintainer to ship pinned release assets, or (b) clone the repo at `c2ed24b` manually and install from the clone." Scorecard "Is it safe out of the box?" must be at least `caution` (already is, but rationale should reference distribution explicitly).

### G2. F9 imperative AI language downgrade (regression against Round 1 fix)
**Raised by:** Codex #3, Pragmatist P2-3
**Gap:** V2.2 F9 table maps persistence phrases ("always X", "never Y") to Warning. Caveman's `rules/caveman-activate.md` has "ACTIVE EVERY RESPONSE" + "No revert after many turns" — both match. Report keeps it at Info via undocumented "surrounding context" escape hatch the V2.2 rule was supposed to eliminate.
**Ship (pick one):** (a) reclassify Finding 7 to Warning with explicit rationale per V2.2 table, OR (b) add a fourth row to F9 table: "Obedience persistence + self-scoped exception clause (e.g., 'drop X for security warnings') = Info with required quote of the self-scope". If (b), update the V2.2 prompt and document in V2.3.

### G3. F12 two-layer Executable File Inventory not delivered
**Raised by:** Pragmatist P2-1 (sole but definitive)
**Gap:** V2.2 prompt specifies (a) one-line summary per file at top, (b) collapsed detailed card with file SHA, line range, diff anchor. Caveman report has neither the one-liner block nor the file SHAs. It's still V2.1 7-property flat cards with a "Prompt version: v2.2" label.
**Ship:** Rewrite `## Executable File Inventory` section to match V2.2 F12. Minimum: one-liner block at top + add file SHAs + line ranges for `caveman-config.js` (lines 80–134 for safeWriteFlag/readFlag), `caveman-activate.js`, `caveman-mode-tracker.js`. Add diff anchor for the PR #70 → #71 → #72 fix chain on caveman-config.js. Why this matters: every future scan will copy the caveman report's format — if we leave V2.1 format with V2.2 label, V2.2 format propagates nowhere.

### G4. Coverage section has contradictory Windows statements
**Raised by:** Codex #4
**Gap:** Coverage says both "Windows surface coverage (F16): install.ps1, uninstall.ps1, caveman-statusline.ps1 all inspected" AND "Platforms covered: Linux hook files (.js, .sh). Did NOT inspect Windows hooks... out of scope". V1→V2.2 migration left old text alongside new. Validator would catch.
**Ship (two edits):** Remove the "Did NOT inspect Windows hooks" sentence (leftover from V2.1). Add automated validator rule to V2.3: "If a file is named in any finding as inspected, Coverage section cannot also say it was not inspected." Simple contradiction check.

### G5. F3 path-OR-title result overclaims "clean"
**Raised by:** Codex #2
**Gap:** Coverage says "zero merged PRs are in the path-hit set but not in the title-hit set." Suspicious Code Changes table includes #146 ("Respect CLAUDE_CONFIG_DIR across all hooks"), #148 ("Update Codex hook config shape"), #174 ("Isolate hooks as CommonJS") — all touch hooks, none have security keywords.
**Ship:** Recompute the set difference actually. For caveman: any PR in path-hit set but not title-hit set needs to be called out in the Suspicious Code Changes table with "path-matched, title-innocuous" as the concern. If inspection cleared them, say so explicitly (not just by omission).

### G6. Composed attack-tree finding missing (the biggest conceptual gap)
**Raised by:** Codex #5
**Gap:** The report has every ingredient separately — no branch protection (Finding 5), no CODEOWNERS (Finding 3c), live-main distribution (Finding 3b), CI amplification into 4 agent rule files (Finding 7), 15% review rate (Finding 3), 61.4% owner commit share. It never synthesizes them into: "Compromise any write-capable account → push one commit to main → workflow fans out rule changes to every user's always-on agent config on next CI run → new installs pull the payload immediately (live main) AND existing users' agent rules get rewritten AND no advisory is triggered."
**Ship:** Add a top-level "Composed Attack Path" finding (Warning severity) to the caveman report that models this single-actor takeover explicitly: preconditions, blast radius, dwell time, detection likelihood. Add a V2.3 prompt rule: "When a repo has ≥3 of {no branch protection, no CODEOWNERS, mutable distribution, CI rule amplification, low formal review rate}, generate one composed attack-path finding synthesizing them."

### G7. "Unadvertised vs silent" loophole (challenge to Round 1 fix F5)
**Raised by:** Skeptic #1
**Gap:** V2.2 F5 rule: "Unadvertised" when release notes mention the attack class, "silent" only when release notes omit. Skeptic argues: a 10-PR batch merge with the title "Hardening release: symlink-safe flag writes" is functionally silent for automated upgrade tools even though the release title names the class. The rule creates a loophole where a single keyword in a release title downgrades governance severity.
**Ship:** Tighten F5 to a conjunction: "Unadvertised" applies only when (a) release notes mention the specific attack class AND (b) the fix is prominently featured (not part of a batch merge >3 PRs that share mergedAt within 1 minute). If batch-merged, the correct label is "disclosed-but-buried" or keep "silent." Don't let a keyword-in-title create a loophole.

---

## SINGLE-REVIEWER FIX NOW (substantive — ship to V2.3 or report corrections)

### G8. Step 8 verification is aspirational for Claude Code plugins
**Raised by:** Pragmatist P2-4
**Gap:** V2.2 Step 8b table says "If possible, inspect plugin marketplace metadata" for Claude Code plugins. No diff step. For npm/PyPI the `npm pack`/`pip download` commands would produce real diffs — for plugin marketplaces there's no automation today. Caveman's "0 of 6 channels verified" line is honest about this, but the V2.2 text reads as if verification was attempted.
**Ship:** Strengthen Step 8b with concrete diff commands for every channel where possible (`npm pack`, `pip download`, `gh release download`). For channels with no diff path, say so explicitly: "No programmatic source-vs-installed diff available for Claude Code plugin marketplace today; scope the verdict accordingly." Remove the hedged "If possible" language.

### G9. First-time contributor + security-critical path gate missing (xz-utils pattern)
**Raised by:** Skeptic #3
**Gap:** V2.2 Step 1 only checks owner + top 3 contributors' account ages. A first-time contributor submitting a PR touching `hooks/`, `install*`, or workflow paths is not flagged. Caveman's `tuanaiseo` (security PR submitter) is not in top 3; the report has no finding on whether they're new to the repo.
**Ship:** Add to Step 5: for each PR in `$SEC_PRS`, check submitter's prior commit count to this repo. If <3 prior commits AND touches security-critical paths, create a Warning finding "First-time contributor touching security-critical code" with account age from Step 1. This matches the xz-utils attack pattern exactly.

### G10. No affirmative "no pull_request_target workflows detected" report line
**Raised by:** Skeptic #5
**Gap:** V2.2 Step 2 says to scan for `pull_request_target` but doesn't require affirmative reporting. Caveman has none (good), but the report doesn't say so — reader can't distinguish "checked, none found" from "forgot to check."
**Ship:** Add to Step 2 output requirement: "Explicitly state whether any workflow uses `pull_request_target`. If none, report 'No pull_request_target workflows detected (positive).' If present, analyze permissions and secret access."

### G11. `-ExecutionPolicy Bypass` deserves a finding, not a passing mention
**Raised by:** Skeptic #6
**Gap:** Finding 3d mentions that caveman's README instructs users to run `powershell -ExecutionPolicy Bypass -File hooks\install.ps1`, which disables Windows' default PowerShell execution protection. Treated as observation, not finding.
**Ship:** Upgrade to Info finding (or Warning if combined with live-main fetching): "Installation instructions disable PowerShell execution policy, lowering defense-in-depth against malicious PS1 content."

### G12. Batch merge count inconsistency: Finding 2 says "10+", Evidence 3 says "16"
**Raised by:** Pragmatist P2-8
**Gap:** Report Finding 2 enumerates 10 PRs, evidence block 3 counts 16, header hedges with "10+". Reconcile — either list all 16 or explicitly state "10 substantive code-change PRs of 16 total (remaining 6 were README/docs tweaks)."
**Ship:** Small report correction. No prompt change needed.

### G13. "What to tell the maintainer" list missing distribution-pinning recommendation
**Raised by:** Pragmatist P2-5
**Gap:** Report's maintainer ask is 4 hygiene items (advisory, SECURITY.md, Dependabot, branch protection). The single most actionable output — pinning distribution channels to release assets — is buried in Finding 3b's mitigation sub-bullet and not in the cross-reference.
**Ship:** Add items 5 and 6 to "What to tell the maintainer": (5) attach versioned release assets, (6) pin marketplace.json + install scripts to a tag. V2.3 prompt rule: "If any Distribution Channel row is Warning, 'Tell the maintainer' MUST include at least one structural pinning recommendation."

---

## DEFER ELEVATIONS (Round 2 → Round 3+ workload)

### D3 → FIX NOW — Changelog-hiding beyond chore/refactor/docs
**Raised by:** Skeptic #10, Pragmatist P2-10
**Rationale:** F3's path-OR-title gating helped but only catches PRs touching the hardcoded security-critical path list. A fix in `lib/token.js` (not in the list) with title `feat: performance improvement` evades. Also: batch merging (Finding 2) is a separate changelog-hiding technique F3 doesn't catch.
**V2.3 ship:** Tier-1 grep-pattern gating in Step 5 — any PR whose diff contains `eval`, `curl`, `execSync`, hardcoded secrets, etc. gets full inspection regardless of path or title. Plus batch-merge detection: PRs sharing `mergedAt` within 1 minute on >3 count = finding.

### D5 → FIX NOW — Governance permission graph
**Raised by:** Codex assessment, Skeptic #12
**Rationale:** F14 added CODEOWNERS check, but the full graph (collaborators with push access, tag protections, release permissions, environment protections) is still absent. For caveman the CODEOWNERS absence alone is damning, but in a multi-collaborator repo the count matters.
**V2.3 ship:** Add to Step 1: `gh api "repos/$OWNER/$REPO/collaborators?per_page=100"`. Count collaborators with push/admin access. If >3 with push and no branch protection, create a Warning finding "N users have write access to main with no required review."

### D6 → FIX NOW — Catalog JSON schema
**Raised by:** Pragmatist P2-2 (directly), Codex (implicitly in #4)
**Rationale:** V2.2 introduced split verdicts (F4), but the catalog metadata block has a single `Verdict` field. A downstream catalog consumer treating that field as atomic loses the split entirely. Round 1 D6 said "defer until the catalog is built"; Round 2 shows the split-verdict design forces it sooner.
**V2.3 ship:** Add a machine-readable block to the catalog metadata. Minimum: a `<!-- CATALOG-METADATA-JSON: {...} -->` HTML comment under the existing table with `schema_version`, `verdict_enum` (`critical|caution|clean|split`), `verdict_current`/`verdict_historical` (when split), `tarball_sha256` (for tamper detection), `scanned_revision_sha`, category, subcategory.

---

## DEFER REMAINING (kept in play, no elevation yet)

- **D1** binary/stego payloads — still defer; D1 becomes relevant only after G8 (real npm/PyPI diffing) is landed
- **D2** dep-registry poisoning — same as D1; on-ramp is G8
- **D4** static-scanner logic/TOCTOU blind spot — F6 pinned tarball fetch; no elevation needed yet. Codex wanted to elevate D4 on the basis that retroactive-edit inconsistency (G4) is a TOCTOU-like artifact problem — but the root fix there is the validator in G4, not D4 itself.
- **D7** paste-block heuristic breadth — kept
- **D8** sophisticated account-takeover — Codex wanted to elevate (composed attack tree G6 partially covers this); DeepSeek kept deferred. Resolution: G6 is the elevated form for V2.3; D8 stays deferred at the "behavioral anomaly detection" level beyond G6's scope.

---

## NEW DEFER ITEMS FROM ROUND 2 (V2.3 watch list)

- **D9** Auto-load frontmatter pattern-class matching (Pragmatist P2-9) — F7's hardcoded list of 4 formats will rot; switch to regex pattern-class detection in V2.3
- **D10** Scorecard calibration table (Pragmatist P2-7) — no quantitative thresholds for fast/slow boundaries on "Do they fix problems quickly?"; different LLMs will drift
- **D11** F13 threat-model cargo-cult risk (Skeptic #7) — guidance to enumerate attack paths "most likely given software context" rather than a fixed list
- **D12** Version-pinning theater (Skeptic #8) — detecting force-pushed / mutable tags as a second-order TOCTOU risk on pinned installs
- **D13** Paste-block ↔ CI-amplified source correlation (Skeptic #9) — when a repo has both, are they the same content? If differ, why?
- **D14** Solo-maintainer threshold graduated buckets (Skeptic #4) — replace binary 80% cutoff with >80 / 50-80 / <50 tier system
- **D15** Coverage "investigator confidence" summary line (Pragmatist P2-11) — three-part HIGH/MEDIUM/LOW rating on CODE/GOVERNANCE/DISTRIBUTION

---

## RECOMMENDED ACTION

**Ship a short V2.3 prompt update** addressing G1–G13 plus D3/D5/D6 elevations. Estimated ~10 prompt edits — smaller scope than V2.2 because most edits are tightening existing rules rather than adding new steps.

**Apply report corrections to caveman.md + caveman.html** for G1, G2, G3, G4, G5, G6, G12, G13 immediately (no prompt changes required for those).

**Biggest single-session ROI:** G3 (F12 two-layer inventory) + G6 (composed attack path finding). Those two alone move the caveman report from "good data, weak synthesis" to "defensible as an external security assessment."

**User's blind-spot question, Round 2 answer:** Still yes. Two that weren't seen in Round 1:

1. The **composed attack tree** — the report documents the ingredients of a supply-chain compromise but never cooks them into a single narrative. G6.
2. The **first-time-contributor-on-security-path** gate (xz-utils pattern) — Step 1 only vets top contributors; a new-to-the-repo submitter can slip through. G9.
