# Board Review Consolidation — Operator Guide DRAFT

**Review date:** 2026-04-16
**Target:** `docs/SCANNER-OPERATOR-GUIDE.md` DRAFT (417 lines)
**Board:** Pragmatist (Claude Opus 4.6, author) · Systems Thinker (Codex GPT-5.4) · Skeptic (DeepSeek V3.2)
**Rounds completed:** 4 (R1 Blind → R2 Consolidation → R3/R4 Combined Deliberation + Final Verdict; R3+R4 expedited per SOP given unanimous R2 verdict)

---

## Unanimous final verdict

**SIGN OFF AFTER FIXES** — all three board members. Zero BLOCK positions. All three confirm DRAFT is shippable as V0.1 after the 10 FIX NOW items below land.

Per-round verdicts:

| Round | Pragmatist | Systems Thinker | Skeptic |
|---|---|---|---|
| R1 | PROVISIONAL SIGN OFF AFTER FIXES · 8 FIX NOW · 1 DEFER · 4 INFO | PROVISIONAL SIGN OFF AFTER FIXES · 8 findings | PROVISIONAL SIGN OFF AFTER FIXES · 10 findings |
| R2 | PROVISIONAL SIGN OFF AFTER FIXES · 13 HELD + 4 NEW · 2 disagreements with Skeptic | PROVISIONAL SIGN OFF AFTER FIXES · all 8 carry + 1 new | PROVISIONAL SIGN OFF AFTER FIXES · 10 held + 3 new + 2 rescinded |
| R3/R4 | SIGN OFF AFTER FIXES · 9 FIX NOW | SIGN OFF AFTER FIXES · 10 FIX NOW | SIGN OFF AFTER FIXES · 10 FIX NOW |

---

## Live disagreements — resolved

### D1 — §14.1 YAML scope today

- **Pragmatist R2**: YAML Phases 1 + 5 only.
- **Skeptic R2**: YAML Phase 1 AND Phase 2 NOW.
- **Systems Thinker R2**: offered schema sketch for Phase 1 + 2; supports both near-term.
- **R3/R4 resolution**: **Phase 1 full YAML. Phase 2 as capture-plan + classification (explicitly not a truth object). Phase 5 orchestration metadata only.** All three aligned on ST's R2 sketch. Skeptic's "wait entirely" position rejected because ST's rule-based classification enums handle the 403-vs-404 judgment Skeptic raised.

### D2 — §14.2 bespoke instructions file naming

- **Pragmatist R2**: AGENTS.md framework-agnostic + stub CLAUDE.md for Claude operators.
- **Skeptic R2**: NEVER — cross-runtime instructions belong in the main guide.
- **Systems Thinker R2-F5**: reframed the question — "portability is a handoff-packet problem, not a Claude-vs-others split."
- **R3/R4 resolution**: **Accept ST's reframe. No new bespoke file in V0.1.** A new "Portable handoff packet" subsection in the main guide supersedes both Pragmatist's and Skeptic's R2 positions. Both prior positions were answers to the wrong question.

### D3 — Skeptic's 2 rescinded findings
- R2-F14 and R2-F15 were Skeptic's own rescinds of R1 items (one misattributed, one was ST's not Skeptic's). No action needed.

---

## Consolidated FIX NOW list for V0.1 promotion (10 items)

All three board members converged on these. Numbers are canonical for the V0.1 edit pass.

| # | Item | Sections affected | Source |
|---|---|---|---|
| **1** | **A1 · Fact/inference discipline rewrite** — §7.2 bundle-structure table must segregate facts from inference structurally, not rhetorically. §11 must state the citation-discipline rule unambiguously. §7.3 and §11 duplication resolved. | §7.2, §7.3, §11 | P, ST, Sk |
| **2** | **A2 · Path A practised / Path B proposed** — §8.1 describes Path A as the only path used in 6 of 6 scans. §8.2 demotes Path B to "Proposed — not yet exercised" with a warning banner. Path-selection criterion switches from file-count to context-budget. Add a `methodology-used: path-a \| path-b` flag to the catalog. | §8.1, §8.2, §3 (prereqs), catalog schema | P, ST, Sk |
| **3** | **A3 · Pre-flight + minimum durability policy** — New §4.1 pre-flight checks (gh auth, scope, /tmp writable, disk space, tarball fetch feasibility). New §12 minimum durability rule: `head-sha.txt` is the first durable artifact; on successful scan, copy `findings-bundle.md` to `docs/board-review-data/scan-bundles/<repo>-<SHA>.md`. §6.3 extended with tarball-fallback guidance when `gh api tarball` exceeds GitHub's response size limit. | §3, §4.1 (new), §6.3, §12 | P, ST, Sk |
| **4** | **A4 · Citation-discipline rule + pre-render manual checklist** — §11.1 defines: every synthesized finding, verdict, and scorecard cell in the bundle must cite evidence line refs or evidence IDs. Add a pre-render manual checklist (in §11 or §9) that the operator walks through before running Phase 4. `--bundle-check` automation deferred to V0.2. | §11.1, §9 (checklist addendum) | P, ST, Sk |
| **5** | **Phase 4 split — MD-first** — §8 rewritten. Phase 4a: bundle → canonical MD. Phase 4b: MD → HTML (structurally derived, no new findings). Phase 5 validates BOTH. §8.4 redundant bullet list deleted; defers to V2.3 prompt. MD is canonical per V2.3 locked design; HTML may not add or alter findings/verdicts/evidence absent from MD. | §8, §8.4, §5 (phase diagram) | P, ST, Sk |
| **6** | **Phase 6 split — public catalog vs optional memory** — §10 rewritten into 6a (required repo-native catalog update at a named path, e.g. `docs/scanner-catalog.md` with per-scan entries) and 6b (optional operator-local memory update). §13 prior-scan reference library moved out of the guide into the catalog artifact to stop coupling guide text to memory contents. | §10, §13, new `docs/scanner-catalog.md` (scaffold) | P, ST, Sk |
| **7** | **§6.1 ordering mirrors V2.3 prompt** — §6.1 restructured 1:1 with V2.3 prompt Steps 1-8 + A/B/C. Step 2.5 (agent-rule detection) restored as a dedicated first-class item, not demoted to last position. C20 governance check reflected in Step 1 as the prompt specifies. | §6.1 | P, ST, Sk |
| **8** | **JSON-readiness narrowing** — §7.1 and §14.1 wording change. Remove "already a JSON payload in prose form." Replace with: "The bundle's structure is amenable to JSON formalisation when the migration fires, but the current prose form has gaps a schema would need to close — see §14.1 for what's in scope." | §7.1, §14.1 | ST, Sk |
| **9** | **GitHub Enterprise / GH_HOST prerequisite note** — §3 prerequisite table gains a "Host" row noting the guide assumes `github.com`. For `GH_HOST=<enterprise-host>`, most Phase 2 gh calls work unchanged; edge cases (rulesets API availability, organization audit endpoints) are uncovered and should be verified manually. Add §14.6 open question. | §3, §14 | P, ST (R2), Sk |
| **10** | **Portable handoff packet** — New §8.3 or §8.5 subsection (replaces D2's bespoke-file decision). Describes the exact artifact set an operator hands to their LLM runtime (context.md equivalent, findings-bundle template, validator path, reference-scan pointers, load order, MD-first render order, validation order, context-fallback rule when the runtime's context is smaller than the combined inputs). Runtime-agnostic — no mention of Claude, Codex, or DeepSeek. | §8.3 or §8.5 (new) | P, Sk (D2), ST (R2-F5) |

### Items folded into the above (not separate FIX NOWs)

- **Unsupported claims** (Skeptic R2-F11/F12): §9.1 "multiple prior scans show this pattern" → "at least one prior scan"; §11 "Risk 1, 2, 3 have happened" → "Risk 1, 2, 3 are plausible; pattern-memory coloring is observed anecdotally but not measured." Folded into #1 (A1) + #4 (A4) edit passes.
- **Calibration cadence between scans 6–10** (Pragmatist + Skeptic): interim spot-check schedule — at scan 7 and scan 9, re-audit one prior scan's bundle-to-report coherence manually. Documented in §14.5 as the final position, not a separate FIX NOW.
- **Archon rerun record = 7th output class**: marked INFO (documented, not blocking). Add Phase 4c "re-run determinism record" as a lightweight alternative to full render when drift is minor.

---

## DEFER list (V0.2 and later)

| Item | Trigger |
|---|---|
| ~~Automated `--bundle-check` tool auditing citation discipline~~ — **shipped 2026-04-19** as `--bundle` mode in `docs/validate-scanner-report.py` per U-5/PD3 board queue. 16 tests; passes on all 5 V2.4 bundles. | ~~After V0.1 stabilises + ≥2 manual-checklist runs~~ — trigger met via catalog growth; built ahead of first Step G run |
| Full Phase 2 YAML schema (beyond capture-plan) | After JSON-first migration fires (catalog at 10 scans, or Trigger #2 hits 3 rule-skip findings) |
| Auto-resume on crash mid-Phase-2 | After Phase 2 is YAML-wrapped |
| Non-github.com adaptation guide (GitHub Enterprise, Gitea, self-hosted) | First operator attempts a non-github.com scan |
| V2.4 C20 rule-calibration (install-from-main repos without releases) | Captured in V2.3 catalog (gstack scan) — scheduled for next scanner-rule board review |

---

## INFO / non-blocking observations

- Validator heuristic false-positives on bash here-strings (`<<<`) and `bash <(curl ...)` in code fences are tolerable. Multiple scans pass with these warnings. Document in §9.1 as expected.
- Current catalog: 6 scans. JSON-first Trigger #1 fires at 10.
- Rule-calibration observations toward Trigger #2 (need 3+, have 2):
  1. gstack: C20 "release in 30 days" has semantic mismatch for install-from-main repos
  2. archon-board-review: V2.3 F7 misses Archon-ecosystem `commands/*.md` YAML-frontmatter files
- Pragmatist explicitly acknowledged same-model-blindspot in R2 and R3/R4: R2-F14 (Phase 4 conflict) and R2-F15 (Phase 6 coupling) were both caught by Systems Thinker, not by self-review. These are now FIX NOW items #5 and #6.

---

## §14 final positions (consolidated)

| # | Question | Final answer |
|---|---|---|
| 14.1 | What can be YAML'd today? | **Phase 1 full YAML. Phase 2 as capture-plan + classification enums. Phase 5 orchestration metadata.** Phase 3/4 stay prose until JSON-first migration. |
| 14.2 | CLAUDE.md-equivalent for non-Claude operators? | **No bespoke file.** A "Portable handoff packet" subsection in the main guide describes the runtime-agnostic artifact set. |
| 14.3 | Synthesis-bias mitigation tool? | **V0.1: manual pre-render checklist.** V0.2: `--bundle-check` automation, once the citation-discipline rule is normalised. |
| 14.4 | Recovery checkpointing pre-JSON-first? | **Yes — minimum durability policy now.** `head-sha.txt` + bundle-on-success copy. Full resume deferred to post-Phase-2-YAML. |
| 14.5 | Catalog growth — per-scan board re-review? | **No.** Aggregated-delta review only: triggers on 3+ rule-skip findings, severity-semantic changes, or coverage-obligation changes. Interim spot-check at scans 7 and 9. Full board re-review at scan 10. |

---

## Promotion condition — DRAFT → V0.1

Complete all 10 FIX NOW items. Verification: at least one board member re-audits the edited DRAFT against each FIX NOW item and confirms it landed.

Expected edit effort: ~250-400 lines of changes across the 417-line DRAFT (significant but not a rewrite). Three new sections (§4.1 pre-flight, §8.3 portable handoff packet, Phase 4c re-run determinism) plus restructurings of §6.1, §7.2, §7.3, §8, §10, §11.

After V0.1 lands, the scanner tool package is: prompt V2.3 + template V2.3 + validator + operator guide V0.1.

---

## Process notes

- R1 → R2 → R3/R4 expedited combined. ~25 minutes total wall-clock. Three parallel executions per round.
- All three board members responded in every round.
- Pragmatist (Claude Opus 4.6) self-review via sub-agent delegation.
- Systems Thinker (Codex) fell back to ChatGPT's default model when `gpt-5.2-codex` was unavailable (same pattern as Round 3 scanner review).
- Skeptic (DeepSeek V3.2) via direct API. Max_tokens capped at 8000 per API limit.
- Infrastructure at `/tmp/board-operator-guide/` — all round responses, briefs, and packets retained.

---

## Artifact inventory

- `/tmp/board-operator-guide/context.md` — review setup
- `/tmp/board-operator-guide/{pragmatist,systems-thinker,skeptic}/brief.md` — R1 role briefs
- `/tmp/board-operator-guide/{pragmatist,systems-thinker,skeptic}/response-round{1,2,34}.md` — all responses
- `/tmp/board-operator-guide/round2-shared-context.md` + `/round2-packet.md` — R2 setup
- `/tmp/board-operator-guide/round34-shared-context.md` + `/round34-packet.md` — R3/R4 setup
- `/tmp/board-operator-guide/{systems-thinker,skeptic}/run*.sh` — reusable execution harnesses
- `docs/SCANNER-OPERATOR-GUIDE.md` — the DRAFT under review (unchanged during the review)
- `docs/board-review-operator-guide-consolidation.md` — **this file**
