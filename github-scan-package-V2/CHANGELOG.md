# Scanner Prompt Changelog

## V2.4 (2026-04-17) — AXIOM Audit FIX NEXT Items

**Driven by:** Internal board triage of external AXIOM 5-model audit. See `docs/board-review-axiom-triage-consolidation.md`.

- **[V4]** Shell variable quoting — all `$OWNER`, `$REPO`, `$SCAN_DIR`, `$NUM` quoted; `for USER in` replaced with `while read` loop
- **[W1/O3]** Version history + D-series deferrals moved out of prompt to this file (~60 lines removed)
- **[W2]** Rate-limit budget check added before Step 5 — `gh api rate_limit` check, reduced sampling when budget low
- **[W4]** osv.dev API fallback when Dependabot returns 403 — zero install, free, parses package manifests
- **[Cap-1]** OSSF Scorecard API integration — `api.securityscorecards.dev` added to Step 1 (24 free checks)
- **[O2]** S8 design rules reduced: 5 hard rules (S8-1, S8-4, S8-5, S8-8, S8-12) + 7 recommended patterns
- **[O4]** CSS sync mechanism — template `<style>` sourced from `scanner-design-system.css` with source comment
- **[B3]** Markdown validator mode (`--markdown`) — checks required section headers + minimum content

**Also applied in V2.4 (FIX NOW from same triage):**
- **[V3]** Symlink stripping after tar extraction (`find -type l -delete`)
- **[V2]** Path traversal protection (`--no-absolute-names` on tar)
- **[V5]** Full 40-char SHA (removed `head -c 7` truncation)
- **[B1]** Template CSS synced with canonical `scanner-design-system.css`
- **[B2]** PR count logic fixed (search API `total_count`, not `per_page=1 length`)
- **[V1]** XSS security checks in validator + CSP meta tag in template

## V2.3 (2026-04-16) — Post-R3 Board Review

**Driven by:** Round 3 board review. See `docs/board-review-V23-consolidation.md`.

**Board fixes applied (C1-C6, C8-C11, C14-C15, C19, C20):**
- Validator `--report` strict-gate mode (C1)
- Auto-load tier classification in Step 2.5 (D9 elevated)
- Monorepo inner-package enumeration + required `pull_request_target` coverage line (C11)
- Step 5b path list extended to config/defaults + Step 5c batch-change keyword grep (C15 / D3 elevated)
- Binding scorecard calibration table (C10 / D10 elevated)
- F4 split-verdict broadened to Version + Deployment axes (C8)
- F13 per-finding-not-per-mention rule (C14 / D11 partial elevation)
- S8-5 / S8-7 / S8-9 tightened, S8-2 demoted to design-principle note (C19)
- C20 governance single-point-of-failure finding — standalone Warning/Critical when branch protection absent

**S8 design rules (all 12 introduced in V2.3):**
- S8-1 utility classes, S8-2 cyan landmarks, S8-3 exhibit rollup, S8-4 status chips,
  S8-5 action hints, S8-6 section status pills, S8-7 evidence grouping,
  S8-8 rem font-sizes, S8-9 timeline labels, S8-10 inventory quick-scan,
  S8-11 split-verdict banner, S8-12 validator gate

**JSON-first (D6):** Explicitly deferred to V3.0 with trigger conditions (catalog at 10 scans or 3 rule-calibration findings).

## V2.2 (2026-04-15) — Board Review Round 1

**Driven by:** Board Review round 1 on caveman report. See `docs/board-review-V21-consolidation.md`.

- **[F1]** Step 8 "Installed-artifact verification"
- **[F3]** Step 5 PR drill-in: title-OR-path gating (path hits mandatory)
- **[F4]** Split-verdict rule
- **[F5]** "Silent" vs "unadvertised" language rule
- **[F6]** Tarball fetch pins to `$HEAD_SHA`
- **[F7]** Step 2.5 expanded to static agent-rule files
- **[F8]** Coverage line for prompt-injection scan
- **[F9]** Step 2.5 hard output rule for AI-directed language
- **[F10]** Step 7.5 mandatory output schema for paste-blocks
- **[F11]** Dual review-rate metric (reviewDecision + reviews.length)
- **[F12]** Two-layer executable file inventory
- **[F13]** Threat-model explicitness rule
- **[F14]** CODEOWNERS check in Step 1
- **[F15]** SHA-pinning tiered finding for GitHub Actions
- **[F16]** Windows script patterns in Step C

## V2.1 (2026-04-14)

Fixed tarball fetch, added README paste-scan, added CI-amplified rule detection, verdict-per-file in inventory, catalog metadata header.

## Deferred Items (kept in play)

**From Round 1:** D1 binary/stego payloads, D2 dep-registry poisoning, D3 changelog-hiding (partially addressed by F3), D4 static-scanner TOCTOU, D5 governance permission graph (partially addressed by F14), D6 catalog JSON schema, D7 paste-block heuristic breadth, D8 account-takeover detection.

**From Round 2:** D9 auto-load frontmatter matching, D10 scorecard calibration table, D11 F13 cargo-cult risk, D12 version-pinning theater, D13 paste-block/CI correlation, D14 solo-maintainer bucket thresholds, D15 coverage confidence summary.
