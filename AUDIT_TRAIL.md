# Audit Trail — Known-Good Checkpoints

Canonical log of milestone commits with the verification state captured at commit time. Purpose: if something breaks, grep this file to find the last known-good state and revert cleanly.

**Conventions:**
- One checkpoint per significant milestone (not per commit).
- Timestamps are canonical commit timestamps from `git log -1 --format='%ai'`.
- Verification state reflects what was tested AT THAT COMMIT, not retroactively.
- Board approval links point to the `CONSOLIDATION.md` authorizing the milestone.
- "Revert to this state" command is `git reset --hard <sha>` — **destructive**; confirm before running.

**Recovery workflow:**
1. Identify the symptom. Recent regression? Check the most recent checkpoint first.
2. Find the last checkpoint where verification was green.
3. Compare `git diff <checkpoint-sha>..HEAD` to see what changed.
4. Revert or cherry-pick as needed.

---

## Checkpoint — 2026-04-19 — U-5/PD3 bundle/citation validator shipped

**HEAD:** `885bdcf`
**Added:** `docs/validate-scanner-report.py` +178 lines (check_bundle + parse_bundle_regions), `--bundle` CLI mode, package mirror; `tests/test_bundle_validator.py` (341 lines, 16 tests). 6 files, 633 ins / 7 del.
**State:** Last pre-Step-G board item cleared. Step G prerequisites now fully done: U-1 (`6a3e471`), U-3/FX-4 (`3c09afb`), U-5/PD3 (`885bdcf`), U-10 (`6481533`).

**Verification at commit time:**
- pytest: `279 passed in 43.56s` (up from 263; +16 new bundle-validator tests)
- Repo ↔ package validator diff: **0 lines**
- `--bundle` smoke test on all 5 V2.4 corpus bundles: clean (2 warnings for V2.4 bundles that name severity without citing F-IDs — lenient heuristic, Step G bundles should cite F-IDs directly)

**Contract (per Operator Guide §9.2.1 + §11.1):**
1. Evidence sections must not contain interpretive verbs (facts-only)
2. Pattern recognition bullets must each use an allowed interpretive verb
3. FINDINGS SUMMARY section exists and non-empty (accepts "Findings" / "Key findings" compact heading variants)
4. Proposed verdict cites at least one F-ID or names a severity level
5. F-IDs referenced in synthesis outside FINDINGS SUMMARY must appear in it (no orphan finding references)

**Design decisions recorded:**
- Lenient citation heuristic for MVP — line-ref (`L45`) / evidence-ID (`evidence.Governance`) formats not required. §11.1 aspirational for V2.5-preview bundles; V2.4 corpus uses informal citation style. Step-G-specific tightening can layer on post-hoc.
- Interpretive-verb leak in evidence = hard error (facts/inference separation is load-bearing).
- Untagged pattern bullet = hard error (inference must be self-identifying).
- Horizontal rules (`---`) and emphasis (`**x**`) correctly excluded from bullet detection via `^[-*]\s+\S` match.
- Compact bundle style (`## Findings` alone) accepted as synthesis — zustand-v3 corpus precedent.

**Documentation updates (in same commit):**
- Operator Guide §9.2.1, §11.1, §14.3, §8.8.7 updated — "deferred" language replaced with `--bundle` invocation.
- `docs/board-review-operator-guide-consolidation.md` DEFER-list entry marked shipped.
- `REPO_MAP.md` §2.4 U-5/PD3 + U-10 both marked done.

**Board approval:** Not required for this commit — board queued the item (`docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §U-5 "APPLY NEXT COMMIT 2-1"), owner-built per spec. Board review will happen at Step G kickoff when this validator gates the first live scan bundle.

**Revert:** `git reset --hard 885bdcf` to stay at bundle-validator-live state. `git reset --hard 3434ce5` to return to pre-U-5 state (loses --bundle mode + 16 tests).

---

## Checkpoint — 2026-04-19 — U-10 complete: canonical scorecard + verdict clean sweep

**HEAD:** `6481533`
**Changed:** 5 HTML scans (scorecard de-drift), 1 MD scan (zustand-v2 scorecard drift on both sides), `docs/GitHub-Scanner-Archon.{md,html}` (verdict metadata), `docs/scanner-catalog.md` (entry 2 verdict), `docs/validate-scanner-report.py` + package mirror (detect_scorecard narrowed to canonical-only). 11 files, 56 ins / 110 del.
**State:** Every catalog scan + zustand-v2 passes `--parity` clean. Canonical 4-question Trust Scorecard is the only accepted set. Archon verdict internally consistent across MD metadata + section heading + HTML banner + catalog row (all Critical).

**Verification at commit time:**
- pytest: `263 passed in 44.80s`
- Repo ↔ package validator diff: **0 lines**
- `--parity` clean on 12 MD+HTML pairs: caveman, Archon, zustand, fd, gstack, archon-board-review, hermes-agent, postiz-app, zustand-v3, zustand-v2, agency-agents, open-lovable

**Source of canonical set:** `docs/repo-deep-dive-prompt.md:743-758` (V2.4 prompt, Trust Scorecard section). Questions:
1. Does anyone check the code?
2. Do they fix problems quickly?
3. Do they tell you about problems?
4. Is it safe out of the box?

**Drift origin:** 5 scans were authored with non-canonical "Can you trust the maintainers?" + "Is it actively maintained?" wording. No prompt version ever defined those — pure authorial drift. Commit `cf6afcd` (2026-04-18) had reverted 4 MDs back to canonical without touching their HTMLs, creating MD↔HTML divergence that `--parity` caught once the regex gaps were closed in `3845406`.

**Board approval:** Not required — fixes align the catalog to the prompt's documented canonical set (no new semantic decisions). Owner-directed clean sweep.

**Revert:** `git reset --hard 6481533` to stay at clean-swept state. `git reset --hard 3845406` returns to validator-narrow-pending state (5 content bugs re-exposed).

---

## Checkpoint — 2026-04-19 — U-10 partial: validator regex extensions for V2.4 catalog

**HEAD:** `3845406`
**Changed:** `docs/validate-scanner-report.py` + package mirror (158 ins/40 del each) + `tests/test_validator.py` (5 ins/4 del). 244 ins / 81 del across 3 files.
**State:** `--parity` now correctly discriminates V2.4 authorial variants. 4 of 9 MD+HTML catalog pairs clean (caveman, zustand, hermes-agent, zustand-v3). 5 remain with real content bugs isolated for separate decision (Archon split-verdict, + 4 scorecard V2.3/V2.4 mismatches).

**Verification at commit time:**
- pytest: `263 passed in 44.84s`
- Repo ↔ package validator diff: **0 lines**
- Package validator `--parity` on zustand V2.4 reference: clean
- U-10 run log in `/tmp/u10-revalidation/` (4 runs showing progressive triage)

**Validator delta vs `ce698d4` Step F R3 state:**
- F-ID pattern extended to accept `.` (F-crates.io)
- MD h3 separator accepts `&middot;`/`·` (hermes-agent style)
- HTML h3 split: finding-card (MD-canonical strict) vs reference-tag (warning)
- Pattern 4 tail-paren ID: only single-F-ID ID-only tails; rejects composites and prose
- Evidence cards filtered by preceding `Evidence N` tag (shared `finding-card` CSS class)
- Scorecard detector accepts V2.3 or V2.4 question set, singular "maintainer" accepted
- Verdict regex reads CSS-stripped body (no CSS rule shadowing)

**Remaining content-bug ledger (deferred, NOT blocking):**
- Archon: MD title "Verdict: Caution (split)" vs HTML verdict-banner class "critical" — authorial inconsistency on which deployment axis drives the primary banner color
- fd, gstack, archon-board-review, postiz-app: MD scorecard reverted to V2.3 in `cf6afcd` (2026-04-18), HTMLs left on V2.4 — needs scorecard-version canonical decision

**Board approval:** Not required (regex tuning only, no semantic behavior change on passing scans; owner-authored). Content-bug resolution (above) may warrant board review before bulk edits — pending owner direction.

**Revert:** `git reset --hard 3845406` to stay at this validator state; `git reset --hard 886eef1` to return to pre-U-10 state (loses validator improvements, re-exposes regex gaps masking real catalog bugs).

---

## Checkpoint — 2026-04-19 03:47 UTC — U-3/FX-4 fixture provenance ledger

**HEAD:** `3c09afb`
**Added:** `tests/fixtures/provenance.json` (54 lines) — Codex separate-file approach for fixture provenance
**State:** Phase 7 renderer Steps A-F complete, U-1 + U-3/FX-4 applied. Step G cleared (pending U-5/PD3 + U-10).

**Verification at commit time:**
- pytest: `263 passed in 42.11s`
- provenance.json validates as JSON; 3 fixtures tagged (zustand: authored-from-scan-data; caveman + archon-subset: back-authored-from-golden-md)
- No regression — same 263 tests as prior checkpoint

**Board approval:** schema-untouched approach approved in `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §5.1 (Codex R3 ADJUST adopted by owner directive 2-1 over Pragmatist+DeepSeek schema-mutation)

**Revert:** `git reset --hard 3c09afb`

---

## Checkpoint — 2026-04-19 00:16 UTC — Step G kickoff board review archived

**HEAD:** `7e285f1`
**Archived:** `docs/External-Board-Reviews/041826-step-g-kickoff/` (R1-R3 full record, 14 files)
**State:** U-1 shipped and confirmed. Step G cleared by 3-0 sign-off.

**Verification at commit time:**
- pytest: 263/263
- Validator `--report` + `--parity` clean on zustand/caveman/archon-subset
- Board: Pragmatist SIGN OFF (R3 upgrade), Codex SIGN OFF WITH DISSENTS (non-blocking terminology debt), DeepSeek SIGN OFF WITH DISSENTS (non-blocking env-var preference)

**Board approval:** `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md`

**Revert:** `git reset --hard 7e285f1` — preserves U-1 doc changes

---

## Checkpoint — 2026-04-19 00:09 UTC — U-1 V2.5-preview docs integrated

**HEAD:** `6a3e471`
**Changed:** 5 docs updated (CLAUDE.md, SCANNER-OPERATOR-GUIDE.md §8.4 + new §8.8, Scan-Readme.md V2.4 refresh, repo-deep-dive-prompt.md one-line cross-ref, scanner-catalog.md rendering-pipeline column). 237 insertions / 73 deletions.
**State:** V2.5-preview pipeline documented as Step-G-experimental across operator-facing docs. Path A/B renamed to continuous/delegated (legacy aliases preserved for catalog flag values). Triple-warning gate in §8.8. Structural-parity criterion for Step G success. Rollback contract.

**Verification at commit time:**
- pytest: `263 passed in 40.33s`
- All 3 fixtures render + validator clean + parity zero errors + zero warnings
- CSS line count: 824 (verified via `wc -l docs/scanner-design-system.css`)

**Board approval:** R2 unanimous direction, R2 split resolutions 2-1 in owner's favor on FX-3b timing + gating mechanism, unanimous on Scan-Readme scope. See `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §5.1/5.2/5.3.

**Revert:** `git reset --hard 6a3e471` — reverts to state before board archive (R3 responses still in `.board-review-temp/step-g-kickoff/`)

---

## Checkpoint — 2026-04-19 00:01 UTC — FX-3b package validator sync

**HEAD:** `60e0bf2`
**Changed:** `github-scan-package-V2/validate-scanner-report.py` (1 file, 12 insertions / 1 deletion). Package validator now byte-identical to repo validator.
**State:** V2.4 package validator bug fixed. Real bug affecting V2.4 scans with shell-glob evidence (demonstrated against caveman shape). Not a V2.5 feature — V2.4 correctness fix.

**Verification at commit time (DeepSeek R2-directed validation step):**
- Repo ↔ package validator diff: **0 lines**
- Package `--report` on V2.4 reference `docs/GitHub-Scanner-zustand.html`: clean
- Package `--parity` on V2.4 reference: all 6 finding IDs matched
- Package `--report` + `--parity` on V2.5-preview zustand render: clean, all 6 finding IDs matched
- Package `--parity` on caveman shell-glob case: **all 9 finding IDs matched, zero errors, zero warnings** (this was the reproducible failure mode FX-3b resolves)

**Board approval:** parallel-commit-before-U-1 approved 2-1 in R2 (`docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md` §5.1)

**Revert:** `git reset --hard 60e0bf2` — reverts U-1 but keeps package validator fix; OR `git reset --hard 638472d` to also revert the package validator (exposes V2.4 bug again — NOT recommended)

---

## Checkpoint — 2026-04-18 23:25 UTC — Step F R3 fixes (XSS + CSS + parity + comment-strip)

**HEAD:** `ce698d4`
**Changed:** 3 files, 23 insertions / 4 deletions. FX-1 `prior_scan_note` XSS fix. FX-2 CSS autoescape corruption fix (33 `&#39;` occurrences eliminated inside `<style>` blocks). FX-3 parity regex H3 Pattern 3 with strip-tags-first. FX-3b validator comment-strip bug removal (emergent — shell globs in evidence text were eating finding cards).
**State:** V2.5-preview renderer pipeline considered production-ready at the renderer layer. All 3 fixtures produce clean output. Parity check has **zero errors AND zero warnings** (previously 1 warning-level false-negative baseline).

**Verification at commit time:**
- pytest: 263/263 passing
- `&#39;` count inside `<style>` block: **0 across all 3 fixtures** (was 37 on zustand pre-fix)
- Validator `--report` clean on all 3 rendered HTMLs
- Parity: all finding IDs matched — zustand 6/6, caveman 9/9, archon-subset 4/4

**Board approval:** 3-model R3 deliberation adopted Codex's strip-tags-first regex (ADJUST over owner's initial + DeepSeek's DOTALL regex). R4 confirmation SIGN OFF (2) + SIGN OFF WITH DISSENTS (1, bookkeeping pytest-warning nit). See `docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md`.

**Revert:** `git reset --hard ce698d4`

---

## Checkpoint — 2026-04-18 22:35 UTC — Step F HTML renderer + cross-shape fixtures

**HEAD:** `402f933`
**Changed:** 21 files, 4235 insertions. `docs/render-html.py` (117-line shim) + `docs/templates-html/scan-report.html.j2` + 14 partials (~1029 lines) + `tests/fixtures/caveman-form.json` (1305 lines, 9 findings) + `tests/fixtures/archon-subset-form.json` (1199 lines, 4 findings, first V1.1 C3 auto_load_tier exercise) + `tests/test_render_html.py` (117 parameterized tests).
**State:** HTML renderer shipped against 3 cross-shape fixtures. 263 tests passing (up from 146). Known defects at this commit: `prior_scan_note` XSS + CSS escape + parity regex H3 gap + validator comment-strip bug — all resolved in next checkpoint (`ce698d4`).

**Verification at commit time:**
- pytest: 263 passed
- All 3 fixtures render + validator `--report` clean
- `--parity` clean with 1 warning per fixture (baseline false-negative matching reference scan behavior — resolved in R3 fixes)

**Board approval:** Step F alignment review R1-R4 at `docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md` authorized R3 fixes; Step F commit itself is the implementation under review.

**Revert:** `git reset --hard 402f933` — reverts to state before XSS/CSS fixes (known defects)

---

## Checkpoint — 2026-04-18 21:50 UTC — Step E validator gate clean

**HEAD:** `cf8c576`
**Changed:** Verification record only (`docs/External-Board-Reviews/041826-renderer-impl-verify/STEP-E-verification.md`) + INDEX update. No code delta — validator `--report` on zustand-rendered.md exits 0 on first try.
**State:** MD renderer verified clean against V1.1 schema + enriched zustand fixture. Phase 7 Steps A-E complete. Step F (HTML renderer) next.

**Verification at commit time:**
- pytest: 146/146 passing
- `python3 docs/validate-scanner-report.py --report /tmp/rendered.md` → exit 0

**Board approval:** mechanical verification, no board review required per plan

**Revert:** `git reset --hard cf8c576` — state before Step F (HTML renderer doesn't exist at this checkpoint)

---

## Checkpoint — 2026-04-18 14:32 UTC — Step D structural assertion tests

**HEAD:** `aac2b3b`
**Changed:** `tests/test_render_md.py` flipped from exact-match to structural assertions. +39 tests in 9 new classes.
**State:** MD renderer covered by 65 structural tests across 12 classes. 146/146 tests passing (up from 107).

**Verification at commit time:**
- pytest: 146 passed

**Revert:** `git reset --hard aac2b3b`

---

## Checkpoint — 2026-04-18 14:22 UTC — Step C zustand fixture enrichment

**HEAD:** `59224ac`
**Changed:** `tests/fixtures/zustand-form.json` 705 → 1015 lines. 10 fix-artifacts approved by 3-model board (`docs/External-Board-Reviews/041826-fixture-enrichment/` R1 UNANIMOUS 3-0).
**State:** Zustand fixture has all structural-LLM fields populated (executable_file_inventory, PR sample, verdict_exhibits, repo_vitals, coverage_detail, evidence entries, per-finding enrichment). First V1.1-compliant fixture.

**Verification at commit time:**
- pytest: 107 passed
- Fixture validates clean against schema V1.1
- Render output 540 lines (vs golden 602; 62-line gap is prose density — intentional "prose stays sparse" rule)

**Board approval:** `docs/External-Board-Reviews/041826-fixture-enrichment/CONSOLIDATION.md`

**Revert:** `git reset --hard 59224ac`

---

## Checkpoint — 2026-04-18 13:59 UTC — Step A C2 BLOCK resolution

**HEAD:** `c6531bb`
**Changed:** `docs/scan-schema.json` — `file_sha`, `line_ranges`, `diff_anchor` now required-always-nullable on every `executable_file_inventory_entry`.
**State:** V1.1 schema freeze completion. Resolves Codex R2 BLOCK in renderer-impl-verify R1 via owner directive adopting Codex's R2 dissent position.

**Verification at commit time:**
- Fixture (zustand) re-validates clean against updated schema

**Board approval:** `docs/External-Board-Reviews/041826-renderer-impl-verify/` R1 Codex BLOCK resolved by owner directive; final position captured in CONSOLIDATION.

**Revert:** `git reset --hard c6531bb` — state before Step C enrichment

---

## Checkpoint — 2026-04-18 13:47 UTC — Step B render-md.py Jinja2 refactor

**HEAD:** `75db969`
**Changed:** `docs/render-md.py` rewritten 782 → 117 lines as a Jinja2 shim + 15 template files at `docs/templates/` (scan-report.md.j2 top-level + 14 partials, 508 lines total). Thin Python + templates architecture per Option C (board-approved Step F alignment R4).
**State:** MD renderer is template-driven. Formatting logic lives in .j2 files. Shim exposes helpers + renders via FileSystemLoader.

**Verification at commit time:**
- pytest: 107 passed
- `render-md.py tests/fixtures/zustand-form.json` produces a clean MD

**Board approval:** Option C (Jinja2) approved unanimously in `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` R4

**Revert:** `git reset --hard 75db969`

---

## Checkpoint — 2026-04-18 13:33 UTC — Step A schema freeze V1.1

**HEAD:** `2b576bf`
**Changed:** `docs/scan-schema.json` 1054 → 1412 lines. V1.0 → V1.1. Added renderer-driven `$defs` (verdict_exhibit_group/item, executable_file_inventory, pr_sample_review, coverage_detail, repo_vitals_row, section_lead, per_finding_prose_entry, timeline_tone). Reconciled stale shapes. C2 conditional (file_sha/line_ranges/diff_anchor on executable_file_inventory_entry). C3 conditional (auto_load_tier on agent-rule-injection category).
**State:** V1.1 schema is the canonical form contract for the V2.5-preview pipeline. Subsequent fixes (`c6531bb`) refined C2 to required-always-nullable.

**Verification at commit time:**
- Schema is valid JSON; structure reviewed by R4 board

**Board approval:** Step F alignment review R1-R4 at `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`

**Revert:** `git reset --hard 2b576bf` — V1.0 schema state, renderers don't exist yet

---

## Pre-Step-F baseline (2026-04-18 prior)

Tests at 107 (pre-Step-D additions). MD renderer exists post-Step-B. V1.1 schema landed in Step A. Older commits (Step C, D, E, F) not individually checkpointed here — see `git log --oneline` for raw history and `docs/External-Board-Reviews/` for decision context.

**Broad pre-Step-F baseline:** `2b576bf..402f933` is the Steps A-F arc. `ce698d4` is the cleanup-complete point. Everything after `402f933` has ≥263 tests.

---

## Maintenance

- **When to add a checkpoint:** after any commit that represents a named milestone (Step X, U-N, board review archived, significant bug fix landed). Do not add one per mechanical commit.
- **Rebuild instructions:** if you need to regenerate this file from scratch, walk `git log --oneline` looking for "Step", "U-", "FX-", "Archive" prefixes; run `git show <sha>` for each to extract verification state from commit messages.
- **Cross-references:** `REPO_MAP.md` for what currently exists · `docs/External-Board-Reviews/README.md` for board review master index · `CLAUDE.md` for operator entry point.
