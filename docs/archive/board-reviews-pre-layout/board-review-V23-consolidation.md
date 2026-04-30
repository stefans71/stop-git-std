# Round 3 Board Review — V2.3 Consolidation

**Generated:** 2026-04-16
**Review type:** V2.3 prompt + V2.3 template + Archon acceptance scan + JSON-first architecture proposal
**Rounds completed:** 1 (blind parallel)
**Board composition:** 3 models

## Agents

| Agent | Model | Role | Finding count | Verdict |
|-------|-------|------|---------------|---------|
| Pragmatist | Claude Opus 4.6 (self-review) | Shippability, proportionality, accuracy | 12 (5 FIX NOW · 3 ELEVATE-DEFER · 3 DEFER · 1 INFO) | SIGN OFF AFTER FIXES |
| Systems Thinker | GPT-5.2-codex (via `codex exec` as `llmuser`) | Architecture, process logic, attack trees | 7 (4 FIX NOW · 2 ELEVATE-DEFER · 1 DEFER triage) | **BLOCK** |
| Skeptic | DeepSeek V3.2 (direct API) | Blind spots, overconfidence, unstated assumptions | 10 (5 FIX NOW · 3 ELEVATE-DEFER · 2 INFO) | SIGN OFF AFTER FIXES |

**Raw responses:**
- Pragmatist: `/tmp/board-caveman-v23/pragmatist/response.md`
- Systems Thinker: `/tmp/board-caveman-v23/systems-thinker/response.md`
- Skeptic: `/tmp/board-caveman-v23/skeptic/response.md`

## Context carried forward

- **Round 1 (V2.1)**: 16 FIX NOW, 8 DEFER (D1–D8) — all FIX NOW applied.
- **Round 2 (V2.2)**: 20+ findings, 3 DEFER→FIX NOW elevations (D3/D5/D6), 7 new DEFER (D9–D15) — FIX NOWs applied.
- **Sprint 8** between Round 2 and Round 3 — aesthetic + UX refactor codified as 12 S8-N rules in V2.3 prompt. Not previously board-reviewed.
- **Acceptance scan**: `coleam00/Archon` on dev@3dedc22 / v0.3.6.

---

## Consolidated findings (deduplicated, severity-ordered)

Convergence is encoded in the `Sources` column — a finding raised by multiple reviewers has higher board confidence than one raised by a single reviewer.

### FIX NOW — must land before V2.3 ships

#### C1. Validator `--report` mode missing; current validator exits 0 on a template with 253 unfilled placeholders

- **Sources:** Systems Thinker Finding 1; confirmed by running the validator against the template in-session. Pragmatist Finding 10 flagged the same gap as DEFER; Systems Thinker is right to elevate.
- **Evidence:** `python3 docs/validate-scanner-report.py docs/GitHub-Repo-Scan-Template.html` → `✓ ... is clean.` (exit 0) while reporting 253 `{{PLACEHOLDER}}` tokens and 39 EXAMPLE-START/END pairs. Prompt V2.3 rule S8-12 (`repo-deep-dive-prompt.md:29-31`) says validator failure is a hard stop; the prompt's Writing rules at `repo-deep-dive-prompt.md:702-703` say the final file must contain zero EXAMPLE markers; validator at `docs/validate-scanner-report.py:117-125` treats placeholders as informational only.
- **Impact:** The validator is load-bearing *in name only*. A rendered report with unfilled placeholders or unstripped EXAMPLE blocks will ship and pass "validation."
- **Proposed fix:** Add CLI flags `--template` and `--report`. In `--report` mode fail non-zero if `placeholders > 0` OR `EXAMPLE-START + EXAMPLE-END > 0`. Update prompt rule S8-12 to invoke `python3 docs/validate-scanner-report.py --report <output.html>`. Default mode (no flag) remains the current "template or report" permissive behaviour for backwards compatibility. **Estimated effort: ~20 lines in `validate-scanner-report.py` + 1 line in prompt.**
- **Dependencies:** Blocks C2, C3, C4 (none of those contracts are enforceable until the gate actually rejects missing structure).

#### C2. Template does not implement the Coverage + Scanner Integrity output schema the prompt requires

- **Sources:** Systems Thinker Finding 2.
- **Evidence:** Prompt `repo-deep-dive-prompt.md:820-835` requires Coverage to include ~10 specific fields (merged-PR sampling, suspicious-PR diff count, tarball extraction, executable-file verdict breakdown, README paste scan, CI-amplified/static rule counts, prompt-injection counts, distribution-channel verification, Windows coverage, limitations). `repo-deep-dive-prompt.md:832` also requires a top-level "Scanner Integrity" section ABOVE Section 01 when actionable prompt-injection hits exist. Template Coverage at `GitHub-Repo-Scan-Template.html:1579-1624` has only 3 fixed cells + generic gap cards. Template has no Scanner Integrity section at all. Archon scan's Coverage table has 12 cells because the LLM filled gaps from prose; the template didn't provide the scaffolding.
- **Impact:** Prompt demands output the template has no canonical place for; LLM can omit load-bearing coverage details and still produce a structurally valid report.
- **Proposed fix:** Add explicit template rows/cards for every Coverage field listed in the prompt. Add a `<section id="scanner-integrity">` block (or a conditional top-level `<details class="collapsible-section">`) above Section 01, with required count fields and finding-card examples for actionable hits. When no hits, template instruction tells the LLM to delete the whole block — not emit empty shells.
- **Dependencies:** Depends on C1 for enforcement. Supersedes any "V2.3 is self-consistent" claim.

#### C3. Template inventory cards lack F12 fields (File SHA, line ranges, diff anchor); Archon scan confirms the drift

- **Sources:** Systems Thinker Finding 3.
- **Evidence:** Prompt F12 at `repo-deep-dive-prompt.md:799-808` requires every security-critical inventory card to include File SHA, line range(s), and diff anchor, and says to drop routine privilege lines unless privilege is non-default. Template inventory at `GitHub-Repo-Scan-Template.html:1334-1418` has only the 7 properties + capability assessment — no SHA, no line ranges, no diff anchor placeholders. Archon inventory at `GitHub-Scanner-Archon.md:231-287` shows the drift: 7 properties + capability, no SHA, no lines, no diff anchor, and routine `| 7. Privilege | User-level ... |` rows still present.
- **Impact:** The highest-value audit trail (rebuild instructions for technical readers) is missing from both the schema and the live artifact. Most security-sensitive section is not reproducible.
- **Proposed fix:** Extend template inventory card with three mandatory fields (`File SHA at scanned revision`, `Relevant lines`, `Diff anchor`). Add rule that privilege is omitted unless non-default. Add C1-enforceable validator checks that warning inventory cards contain all three markers.
- **Dependencies:** Depends on C1. Interacts with C12 (these belong in JSON, not hand-authored HTML).

#### C4. No HTML-escape validator check; untrusted repo content can flow into rendered HTML

- **Sources:** Systems Thinker Finding 4.
- **Evidence:** Prompt `repo-deep-dive-prompt.md:56-70` says repo content is UNTRUSTED and may contain prompt injection. `repo-deep-dive-prompt.md:810` explicitly requires HTML-escaping all inserted text (PR titles, issue titles, commit messages) — `&`→`&amp;`, `<`→`&lt;`, etc. Validator (`validate-scanner-report.py:11-18`) checks tag balance, EXAMPLE balance, placeholder count, inline styles, px font-sizes — no escape check anywhere.
- **Impact:** A malicious repo can attack the scanner's output path, not just the model. Raw HTML/JS could reach a rendered report through unescaped titles or bodies.
- **Proposed fix:** Short-term: add a validator heuristic check — detect unescaped `<` characters outside `<code>`/`<pre>` blocks and outside the known-safe CSS/JS/comment regions. Flag as a warning (since false positives are possible). Better long-term fix: C12 (JSON-first) moves repo text into a JSON field and renders with deterministic escaping in code, eliminating the class.
- **Dependencies:** Depends on C1. C12 supersedes this.

#### C5. Archon CLAUDE.md inventory card skipped the mandatory F9 / Step 2.5 scan

- **Sources:** Pragmatist Finding 1. (Skeptic Finding 4 flags a related correlation gap in D13.)
- **Evidence:** `GitHub-Scanner-Archon.md:281-283` — the whole CLAUDE.md card is a 3-line prose summary ("not a propagation vector") with no imperative-verb grep, no auto-load frontmatter check, no capability statement, no risk statement, no severity chip, no action-hint. Prompt Step 2.5 at `repo-deep-dive-prompt.md:201-228` requires every rule file to get a full card; F9 at line 219 makes it a hard output rule. The Pragmatist authored this card and acknowledges the rule-miss.
- **Impact:** The acceptance scan violates the prompt's own hard output rule on exactly the surface V2.3 was meant to enforce. Directly undermines the Pragmatist's own "direct-HTML-fill is reliable" claim.
- **Proposed fix (two-part):**
  1. **Immediate:** re-run the CLAUDE.md inventory card on Archon with: imperative-verb list extracted from the file, explicit auto-load statement, capability + risk statements, severity chip, action-hint.
  2. **Prompt hardening:** add an explicit per-rule-file checklist to Step 2.5 (6 mandatory items per card — verb list, auto-load behaviour, capability, risk, severity, chip+hint). Paired with C9 (auto-load tier classification).
- **Dependencies:** Blocks C7 (acceptance-scan completeness). Partially addresses D9 (elevated as C9 below).

#### C6. "Distribution channels verified 2 of 2" on Archon conflates install-path verification with installed-artifact verification

- **Sources:** Pragmatist Finding 2; Systems Thinker Finding 5 (D1 elevation) reached the same conclusion via a different path.
- **Evidence:** `GitHub-Scanner-Archon.md:363` says `Distribution channels verified (F1) | ✅ 2 of 2 — archon.diy/install byte-matched scripts/install.sh; Homebrew formula inspected; Docker publish workflow read`. What was actually verified: the install script is pinned and checksums match `checksums.txt`. What was NOT verified: that the Bun-compiled binary in the release tarball matches source at `3dedc22`. The scan never ran `bun build --compile` locally and diffed output. Archon itself ships Bun-compiled binaries (`GitHub-Scanner-Archon.md:15`). Issue #1246 (the scan's own F2) is EXACTLY this gap — the scan names it as open but claims verification anyway. Self-contradictory.
- **Impact:** The single most load-bearing claim in Coverage for a trust decision is false-green. Verdict's "installing today is safe" framing is weaker than it reads.
- **Proposed fix:**
  1. **Immediate on Archon report:** replace the `✅ 2 of 2` line with `⚠ Install path verified (script pinned, sha256 checked); installed artifact NOT verified (Bun-compiled binary not rebuilt locally and diffed)`. Mirror in HTML.
  2. **Prompt fix (Step 8):** distinguish two tiers — **Path verified** (install mechanism pinned + checksummed) vs **Artifact verified** (binary independently rebuilt from source or diffed). Tier-1-only cannot claim `✅ Verified`; must be `⚠ Path only`. This is the concrete version of D1 (binary/stego payloads) and D4 (static-scanner TOCTOU blind spot).
- **Dependencies:** Triggers D1 elevation (see C10). Also addresses D4 partially.

#### C7. n=1 acceptance scan is insufficient evidence that direct-HTML-fill is reliable; two rule-misses (C5 + C6) on the one test weaken it further

- **Sources:** Pragmatist Finding 7; Skeptic Finding 2.
- **Evidence:** Archon shares key shape with caveman (AI/LLM tooling, Bun, developer-facing CLI, AGENTS/CLAUDE rule files, install+Homebrew+Docker triad). Untested shapes: a React library with 0 executable files, a Python ML tool with no binary release, a Go systems daemon, a repo with 50 agent rule files, a repo with zero findings. Exhibit rollup threshold (S8-3 fires at 7+) was barely exercised (Archon had 8 findings across 3 exhibits). Beyond the shape gap: the Archon scan itself produced two rule-misses (C5 + C6), so the pipeline did not cleanly execute V2.3 even on a near-neighbour.
- **Impact:** Claiming "pipeline reliable" from n=1 with two misses is over-confident. Real drift risk ships with V2.3 if additional shapes aren't tested.
- **Proposed fix:** Run at least TWO more acceptance scans before V2.3 is locked:
  1. **Archon re-run** after C5 + C6 applied — establish the fixes work.
  2. **A clean Python tool** — Skeptic suggests `tiangolo/fastapi`; Pragmatist suggests `scikit-learn` or `pola-rs/polars`.
  3. **A React library with no install script** — `pmndrs/zustand` or `TanStack/query`.
  4. (Optional stretch: a zero-findings repo to exercise the clean-verdict template branches.)
  Validate each against V2.3 (prompt + template + C1-gated validator). Only after all three produce valid V2.3-shape reports do we claim pipeline reliability.
- **Dependencies:** Blocks a clean "SIGN OFF" from this round. Also serves as the empirical test feeding the JSON-first decision in C12.

#### C8. F4 / S8-11 split-verdict under-specified; Archon used it for a deployment-axis split not a version-axis split

- **Sources:** Pragmatist Finding 4.
- **Evidence:** `GitHub-Scanner-Archon.html:886-894` uses split verdict with both entries scoped to the same version (v0.3.6), split on single-user vs shared host. F4 at `repo-deep-dive-prompt.md:774-779` and S8-11 at line 16 both specify split-verdict for version-time splits only. The deployment-axis split in Archon is a good UX choice but is a rule violation.
- **Impact:** Readers who know V2.3 semantics will misread the scope. The rule needs to authorise deployment-axis splits or Archon needs a different structure.
- **Proposed fix:** Broaden F4 (and mirror in S8-11) to name two valid axes: (a) Version axis (current clean vs historical vulnerable) and (b) Deployment axis (safe in one profile, risky in another — shared host, CI runner, multi-tenant). Require scope labels to prefix with `Version · ...` or `Deployment · ...` so the axis is explicit. Apply to Archon HTML labels.
- **Dependencies:** None.

#### C9. ELEVATE D9 → FIX NOW: auto-load tier classification is required; Archon CLAUDE.md miss is proof

- **Sources:** Pragmatist Finding 3.
- **Evidence:** Prompt at `repo-deep-dive-prompt.md:210` lists auto-load frontmatter checks for Cursor (`alwaysApply: true`), Windsurf (`trigger: always_on`), copilot-instructions.md, AGENTS.md, GEMINI.md — but lumps CLAUDE.md into the same prose without a tier label. C5 shows the detection didn't fire on Archon's CLAUDE.md.
- **Impact:** Reports continue to under-scan CLAUDE.md / AGENTS.md / GEMINI.md files unless classification is explicit. Same failure mode will appear on every repo with these files.
- **Proposed fix:** Rewrite Step 2.5's auto-load section to classify every rule file into four tiers (Always / Conditionally / User-activated / Unknown-default-Tier-1). Tier 1 cards must include the sentence "This file is auto-loaded for every session — content changes reach every user without opt-in" in the risk statement.
- **Dependencies:** Paired with C5. Supersedes D9.

#### C10. ELEVATE D10 → FIX NOW: scorecard calibration table needed; Archon's amber cell is un-grounded under current F11

- **Sources:** Skeptic Finding 1; Pragmatist Finding 9 (both independently proposed nearly identical calibration tables).
- **Evidence:** Archon "Does anyone check the code?" cell = `⚠ Informal (8% formal, 58% any-review)`. F11 at `repo-deep-dive-prompt.md:266-270` says "for multi-maintainer repos use formal review rate as the primary signal" — which would score red at 8%. But the cell is amber. The 58%-any-review + dual-maintainer (Wirasm+coleam00) argument is reasonable, but it contradicts F11 as written and isn't grounded in a binding rule. Different LLM runs could plausibly produce red on the same data.
- **Impact:** Reproducibility at risk. Scorecards can't be compared across scans or scanners.
- **Proposed fix:** Add a binding calibration table to the prompt (before `### Scorecard consistency rule`, around line 572). Both reviewers proposed table shapes; Pragmatist's is more concrete and uses the F11 dual metric. Recommended landing: Pragmatist's table verbatim, with one small tightening from Skeptic (explicit "Informal"/"Rare"/"Good" labels mapping to amber/red/green so the report's wording is grounded too).
- **Dependencies:** Supersedes D10. None blocking.

#### C11. Monorepo inner packages + `pull_request_target` workflow check not performed; Archon report is missing coverage

- **Sources:** Skeptic Finding 6.
- **Evidence:** Archon scan Coverage (`GitHub-Scanner-Archon.md:371`): "Monorepo has 11 inner packages with their own `package.json` — per-package dep surface not enumerated here." Workflow files inspection says "4 of 4" but does not mention checking for `pull_request_target` (a critical pattern explicitly called out in prompt Step 2).
- **Impact:** Scanner may miss supply-chain risks in inner packages (postinstall lifecycle scripts in `packages/*/package.json`) and CI privilege-escalation vectors.
- **Proposed fix:** In prompt Step 2, add: "For monorepos, enumerate all `package.json` via `find . -name package.json -not -path '*/node_modules/*'` and report the count. Sample 1-2 inner packages for lifecycle scripts (preinstall, postinstall, prepare, prepublishOnly)." In the Step 2 CI check, require explicit "`pull_request_target` usage: N found" line in Coverage even when N=0.
- **Dependencies:** None.

### ELEVATE-DEFER (promote from D1–D15 to next-round work)

#### C12. D6 (JSON-first) — Systems Thinker says promote now; Pragmatist says defer with triggers; Skeptic says defer pending cross-LLM test. **Board consensus: DEFER with explicit triggers.**

- **Sources:** Systems Thinker Finding 6 (ELEVATE), Pragmatist Finding 8 (DEFER with triggers), Skeptic Finding 9 (INFO — premature without cross-LLM evidence).
- **Synthesis:** Systems Thinker's concern is architectural: prompt says MD is canonical but Archon is generated HTML-first, caveman.md is still at v2.2 while HTML is Sprint-8 — the source-of-truth story is already incoherent at n=2 catalog entries. Pragmatist agrees JSON-first is the right V3.0 target but argues it shouldn't ship simultaneously with V2.3 rule tightening (doubles moving parts). Skeptic wants cross-LLM evidence before committing.
- **Board decision:** **DEFER** with explicit re-evaluation triggers (any one triggers V3.0 work):
  1. Catalog corpus reaches 10 scans.
  2. A subsequent board review surfaces 3+ rule-skip findings similar to C5 / C6.
  3. A manual re-run diff between two scans of the same repo becomes impractical.
  4. A cross-LLM compatibility test (Skeptic's proposal — see C16 INFO) fails on GPT-4o or Gemini.
- **If adopted:** Systems Thinker's 4-step migration path is the recommended plan (freeze schema → LLM emits JSON+legacy-MD for 2 releases → deterministic renderer → schema-first validator).
- **Why not promote now:** the C1–C11 FIX NOWs are prompt/template edits that can ship in days. JSON-first is a multi-week workstream that would benefit from the additional acceptance data from C7. Sequence: land C1–C11 → run C7 matrix → reconvene on JSON-first.

#### C13. D1 (binary/stego payloads) — elevated as C6 already captures it

- **Sources:** Systems Thinker Finding 5.
- **Status:** Folded into C6 (distribution/artifact verification). D1 in future rounds = the broader "verify binary against source" workstream (reproducible builds, provenance attestations); C6 is the narrow Step 8 prompt wording fix.

#### C14. D11 (F13 threat-model cargo-cult) — Archon F1 shows double-encoding; one-liner prompt fix lands now

- **Sources:** Pragmatist Finding 6.
- **Evidence:** Archon F1 card contains two "How an attacker arrives (F13)" passages, slightly rephrased (`GitHub-Scanner-Archon.md:141` and `:243`). Same content restated.
- **Proposed fix:** Edit `repo-deep-dive-prompt.md:796-797` (F13 block) to add: "F13 statements are per-finding, not per-mention. If the same threat model appears in both a finding card and an inventory card, write the 'how attacker arrives' sentence once in the finding card and reference it from the inventory card with 'See F<N> threat model above'; do not restate in varied phrasing." Also: edit Archon HTML + MD to collapse the duplicate.
- **Dependencies:** None. Small prompt/doc edit.

#### C15. D3 (changelog-hiding variants) — expand path gate to cover config/defaults files

- **Sources:** Skeptic Finding 7.
- **Evidence:** F3 path-OR-title gating catches PRs touching hook files, install scripts, workflow YAMLs — but not PRs that change security-relevant defaults in non-critical-path files (e.g., `config/defaults.json`, `**/defaults.*`, `**/settings.yaml`). A PR changing an insecure default with an innocuous title slips through.
- **Proposed fix:** Extend Step 5b path list: add `**/defaults.*`, `**/config/*.json`, `**/settings.yaml`. Also: add a grep for security-keywords in the diff of any PR that touches >3 files (batch changes).
- **Dependencies:** None. Prompt update.

### DEFER (kept in play; re-evaluate next round)

| ID | Status | Notes |
|----|--------|-------|
| D2 dep-registry poisoning | **Kept** | No Archon trigger; still relevant for registry-published repos |
| D4 static-scanner TOCTOU | **Partial** | F6 pinned tarball to SHA; deeper checks still open. C6 addresses the artifact side. |
| D5 governance permission graph | **Partial, kept** | Archon's CI-bot-commits-to-dev is a permission-graph signal (`GitHub-Scanner-Archon.md:54-55, 245-257`). Systems Thinker flagged but did not promote. Carry with acceptance criterion: "model who actually has write/admin rights on protected or flagged repos." |
| D7 paste-block heuristic breadth | **Kept** | Archon has no paste-blocks so no new evidence |
| D8 sophisticated account-takeover | **Kept** | Pragmatist Finding 12 notes Archon's governance surface is compounded (no branch protection + no CODEOWNERS + CI-bot commits) — raises the blast radius of a takeover but not a new detection angle. |
| D9 auto-load frontmatter classification | **ELEVATED** — see C9 |
| D10 scorecard calibration | **ELEVATED** — see C10 |
| D11 F13 cargo-cult | **ELEVATED (partial)** — see C14. Full audit deferred. |
| D12 version-pinning theater | **Kept** | Prompt at `repo-deep-dive-prompt.md:180-184` still treats `@v4` action tags as low-risk Info. Systems Thinker Finding 7 flagged. Carry with concrete criterion: "mutable action tags (`@v4`, `@main`) must be `Info · Mutable tag` not pinned-equivalent." |
| D13 paste-block ↔ CI-amplified correlation | **Kept/partial** | Skeptic Finding 4 raised; Archon had no paste-blocks so trigger wasn't hit. Prompt edit proposed: "if a paste-block references or copies content from a static agent-rule file, note the correlation in both cards." Carry forward. |
| D14 solo-maintainer bucket thresholds | **Kept** | F11's hardcoded >80% threshold still exists; Archon under threshold so no trigger. |
| D15 coverage investigator-confidence line | **Kept** | Systems Thinker flagged. Carry with acceptance criterion: "Coverage section ends with a one-line investigator-confidence summary (High / Moderate / Low) with justification." |

### INFO (not blocking; useful next-round context)

#### C16. Cross-LLM compatibility test for V2.3 pipeline

- **Sources:** Skeptic Finding 9.
- **Claim:** The Archon acceptance scan was produced by Claude Opus — the same LLM family that wrote the V2.3 prompt and template. The "pipeline reliable" claim is LLM-specific until tested on GPT-4o / Gemini / a smaller open model.
- **Disposition:** Useful data point for the JSON-first trigger (C12.4). Not a V2.3 blocker (the pipeline is being shipped under stop-git-std, which can specify "use Claude Code" in the prompt preamble — a reasonable restriction).
- **Suggested follow-up:** run the V2.3 prompt on Archon (or one of the C7 diversity-matrix repos) using GPT-4o and Gemini Pro. Validate HTML with C1-enforced `--report` mode. If both pass: direct-HTML-fill is cross-LLM robust; JSON-first remains deferred. If either fails: C12 trigger fires.

#### C17. Archon verdict framing — "actively fixing in public" underweights the self-merge pattern

- **Sources:** Pragmatist Finding 12.
- **Evidence:** Archon §03 Suspicious Code Changes table (`GitHub-Scanner-Archon.md:272-281`): 5 of 6 flagged PRs are Wirasm→Wirasm self-merges. The scan notes it but softens with "content is good." Per prompt's Red Flags section (`repo-deep-dive-prompt.md:588`), self-merge on security-sensitive PRs is an explicit flag.
- **Impact:** Editorial calibration only — verdict ("caution") is right. But the table rows should say "Self-merged by lead maintainer without formal review — content quality is good, but the pattern is F11-flagged" rather than softening with "content is good" alone.
- **Proposed fix:** Edit Archon MD+HTML §03 rows for #1217 and #1169.

#### C18. Verdict taxonomy — add `caution-historical` vs `caution-active` modifiers

- **Sources:** Skeptic Finding 8.
- **Claim:** Same `caution` verdict label does different work for caveman (historical fixed vulns) vs Archon (live open issues). Users may conflate.
- **Disposition:** Good idea for V2.4. Not a V2.3 blocker — the split-verdict structure already allows a detail line that names the distinction (Archon says "Wait for PR #1250" in the `bad` entry which is stronger than caveman's "upgrade required"). Skeptic's proposed modifier would make the distinction banner-level rather than detail-level. Carry as DEFER; re-evaluate when a 3rd "caution" scan lands.

#### C19. S8 rule proportionality — demote S8-2, tighten S8-5/S8-7/S8-9

- **Sources:** Pragmatist Finding 5.
- **Details:**
  - **S8-2 (Cyan landmark)** — design principle, not LLM-violable. Demote from numbered rule to intro note. Renumber S8-3→S8-12 down by one.
  - **S8-7 (Priority evidence)** — add explicit criterion: "priority = evidence whose falsification would flip the verdict; if you can't articulate that, don't flag as priority."
  - **S8-9 (Timeline severity labels)** — forbid restatement-of-date labels (`SCAN`, `START`, `TODAY`). Require beat-naming labels (`5-DAY LAG`, `FIX SHIPS`).
  - **S8-5 on `.informational` findings** — require action-hint be instructive or dropped entirely; a hint that repeats "no action" noise.
- **Disposition:** FIX NOW on Pragmatist's read (Finding 5), but the board consensus is this is a proportionality tightening, not a blocker. Bundle with C8 as prompt-edit work that can ship alongside C1–C7. **Promoting to FIX NOW** in the board consolidation — small, concrete, ships with C1–C11.

---

## Architecture verdict: JSON-first vs direct-HTML-fill

**Decision:** DEFER JSON-first to V3.0. Explicit re-evaluation triggers are in C12.

**Rationale (synthesis of all three reviewers):**

- Systems Thinker made the strongest structural case: the current architecture has no single enforceable source of truth across prompt / MD / HTML / validator. Caveman.md is at v2.2 while caveman.html is Sprint-8 refactored — at n=2 catalog entries the coherence is already breaking down.
- Pragmatist agreed JSON-first is the right V3.0 target but flagged the proposal timing: shipping V2.3 rule-tightening AND a new architecture simultaneously doubles the moving parts under review. Better to sequence.
- Skeptic raised cross-LLM compatibility as an unmeasured variable. One of C12's triggers should be a cross-LLM test failure.

**Migration path (when triggered):** use Systems Thinker's 4-step plan — schema freeze → dual emit (JSON + legacy MD) for 2 releases → deterministic renderer → schema-first validator.

---

## DEFER item status table (post Round 3)

| ID | Status after Round 3 | Notes |
|----|---------------------|-------|
| D1 binary/stego payloads | **ELEVATED → C6** | Path-verified vs artifact-verified distinction added to prompt Step 8 |
| D2 dep-registry poisoning | Kept in play | No Archon trigger |
| D3 batch-merge variant | **ELEVATED → C15** | Path gate extended to config/defaults files + diff-keyword grep |
| D4 static-scanner TOCTOU | Partially addressed by C6 | Deeper checks still deferred |
| D5 governance permission graph | Partially addressed | Archon CI-bot case surfaced in C11 and INFO; full graph model still deferred |
| D6 catalog JSON schema | **DEFERRED with triggers → C12** | Explicit re-eval triggers set |
| D7 paste-block heuristic breadth | Kept in play | No Archon paste-blocks |
| D8 sophisticated account-takeover | Kept in play | C17 notes Archon's compounding governance surface but no new detection angle |
| D9 auto-load frontmatter classification | **ELEVATED → C9** | Tier classification rule in Step 2.5 |
| D10 scorecard calibration | **ELEVATED → C10** | Binding calibration table in prompt |
| D11 F13 cargo-cult | **PARTIALLY ELEVATED → C14** | One-liner rule added; full audit deferred |
| D12 version-pinning theater | Kept, criterion added | "mutable action tags must be flagged Info · Mutable tag" |
| D13 paste ↔ CI-amplified correlation | Kept, criterion added | Skeptic's cross-reference rule if trigger hits |
| D14 solo-maintainer bucket thresholds | Kept in play | Archon below F11's 80% threshold |
| D15 coverage investigator-confidence line | Kept, criterion added | Coverage ends with one-line confidence + justification |

---

## Overall board verdict

**Three-way reading:**
- Pragmatist: SIGN OFF AFTER FIXES (5 FIX NOW)
- Systems Thinker: **BLOCK** (4 FIX NOW architecturally blocking)
- Skeptic: SIGN OFF AFTER FIXES (5 FIX NOW)

**Board consensus:** **SIGN OFF AFTER FIXES** — but with the Systems Thinker's caveat that C1 through C4 are structurally blocking. The validator-gate fix (C1), template-prompt coverage alignment (C2), inventory-card F12 fields (C3), and HTML-escape check (C4) are enforcement gaps. Without them, the "V2.3 ships" claim is architecturally hollow. Once those four land, the block resolves.

**Ship checklist (ordered by dependency):**

1. **C1** — add `--report` mode to validator. Gate for everything else.
2. **C2, C3, C4** — template + validator alignment. Template-layer fixes.
3. **C5, C6** — re-run Archon CLAUDE.md card; correct Archon "2 of 2" claim. Concrete acceptance-scan fixes (10 minutes each).
4. **C8, C9, C10, C11, C14, C15, C19** — prompt edits (F4/S8-11 broadening; auto-load tier classification; scorecard calibration table; monorepo coverage; F13 single-statement rule; D3 path extension; S8 proportionality tightening). All additive, non-breaking.
5. **C7** — run the acceptance-scan matrix (Archon re-run + React library + Python tool). Empirical validation of the pipeline on non-Bun-AI-tooling shapes. **This is the real gate before claiming "pipeline reliable."**
6. **C17, C18** — editorial calibration on Archon + verdict-taxonomy for V2.4.

After C1–C7 land, V2.3 is the production scanner. C12 (JSON-first) and C13–C18 are next-round work.

**Estimated effort:** C1 + C2 + C3 + C4 in ~200 lines of changes. C5 + C6 in ~50 lines. C7 matrix in 3 scans × ~30 min each. Total critical-path work: roughly one working session, not a multi-week refactor.

---

## Process notes

**Timing:**
- Brief writing: ~10 min
- Three parallel reviews: ~5 min (Skeptic first, Systems Thinker second, Pragmatist third)
- Consolidation: ~30 min

**Tooling observations:**
- DeepSeek handled 117KB payload (V2.3 prompt + Archon.md + briefs) cleanly; 30,720 prompt tokens / 3,131 completion tokens.
- Codex (GPT-5.2-codex) via `codex exec --dangerously-bypass-approvals-and-sandbox` ran isolated from `/tmp`. Used 128,133 tokens — reads the full prompt (56KB) + both Archon artifacts + validator.
- Pragmatist (Agent tool, general-purpose subagent) completed in ~5.6 min, 107,961 tokens. Produced the longest and most self-critical review.

**Lessons for Round 4 / trigger:**
- The validator-not-a-gate bug (C1) should have been caught before Round 3 — the Pragmatist ran the validator on both caveman and Archon and saw "is clean" without noticing it was also "is clean" on the unfilled template. Process note: validator-gate claims need a **negative test** (a file that SHOULD fail) before trusting positive results.
- Systems Thinker's BLOCK-severity calls are reliably load-bearing — every one of its FIX NOWs was factually verifiable and had a concrete line-level fix. This is the pattern to trust going forward.
- The 3-model board continues to find things the self-review misses. In Round 3, the self-review self-caught C5 and C6, but missed C1 (the validator gap), C2 (template-prompt coverage misalignment), C3 (F12 fields missing from template), C4 (no escape check). Systems Thinker caught all four. Do not skip the board.
- Next round (V2.3+ or V3.0): re-evaluate JSON-first against the C12 triggers. Expect the triggers to fire within ~2-3 scans.
