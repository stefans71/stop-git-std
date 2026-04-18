# Round 2 — Pipeline Methodology Consolidation

You reviewed a data pipeline and methodology analysis in Round 1 (blind). Now read ALL THREE Round 1 reviews and converge on the final classification, pipeline design, and implementation plan.

## Context (read these files for full background)

1. `.board-review-temp/pipeline-methodology-brief.md` — original brief explaining the process, findings, proposed 9-phase architecture, and 7 questions
2. `.board-review-temp/data-lineage-map.md` — 1140-line data lineage map tracing 118 data points from tool to report
3. `github-scan-package-V2/repo-deep-dive-prompt.md` — the V2.4 investigation prompt (~1500 lines). **Cross-reference this against the lineage map and classification disputes below.**

## All 3 Round 1 Reviews

4. `.board-review-temp/pragmatist-r1.md` — Pragmatist review (APPROVE WITH CONDITIONS, reclassifies to 8/7/4)
5. `.board-review-temp/systems-thinker-r1.md` — Systems Thinker review (APPROVE WITH CONDITIONS, reclassifies to 6/10/4 or 8/8/4)
6. `.board-review-temp/skeptic-r1.md` — Skeptic review (APPROVE WITH CONDITIONS, reclassifies to 9/7/4)

## Classification dispute — the 5 contested operations

The original analysis claimed 11 operations are fully automatable. All 3 reviewers reclassified some. Here are the 5 disputed items:

| # | Operation | Original | Pragmatist | Sys. Thinker | Skeptic |
|---|-----------|----------|------------|--------------|---------|
| D1 | General vuln severity (not C20/F9/F15) | Auto | **Structured LLM** | **Structured LLM** | Auto |
| D2 | Split-axis decision (F4) | Auto | **Structured LLM** | **Structured LLM** | Auto |
| D3 | Priority evidence selection | Auto | **Structured LLM** | **Structured LLM** | **Structured LLM** |
| D4 | Exhibit grouping | Auto | Auto | **Partial** | **Structured LLM** |
| D5 | Silent vs unadvertised (F5) | Auto | Auto w/ caveat | **Partial** | Auto |

**YOUR TASK: For each of D1-D5, read the EXACT prompt rule governing it, and vote AUTOMATABLE or STRUCTURED LLM with a quote from the prompt.**

## Deferred items from ALL prior review rounds

These items were deferred across the full board review process (package review, schema review, fact-vs-synthesis review, pipeline review). Vote AGREE DEFER or PROMOTE TO FIX NOW.

### From package review (Rounds 1-2):
- PD1: V2.3 reference scans → legacy label or upgrade
- PD2: MD↔HTML content parity validator
- PD3: Bundle/citation validator
- PD4: CSS sync check in --report mode
- PD5: Test suite (tests/test_validator.py)
- PD6: CI/CD integration examples
- PD7: Offline font bundling

### From schema review (Rounds 1-4):
- SD1: `components[]` for monorepo/multi-shape repos
- SD2: Finding `kind` + `domain` orthogonal typing
- SD3: Confidence scores on synthesis objects
- SD4: Judgment fingerprint
- SD5: Plausibility check layer (soft validator warnings)
- SD6: Per-field source tags
- SD7: Variable scorecard length (min 1, no max)
- SD8: Generic `artifacts[]` model
- SD9: Generic `permissions[]` abstraction
- SD10: SBOM integration

### From pipeline review (Round 1):
- RD1: V2.0 automation of structured LLM operations (Category 2)
- RD2: Corpus test on 20+ scans before promoting structured items to code
- RD3: LLM fallback mode if automated computation fails
- RD4: "Assumptions" field in investigation form
- RD5: Management sign-off field (2-1 for including; Pragmatist dissented)

## Your task for Round 2

1. **Vote on D1-D5** with exact prompt rule quotes
2. **Vote AGREE DEFER / PROMOTE on all deferred items** (PD1-7, SD1-10, RD1-5)
3. **Flag any prompt requirements NOT captured** in the data lineage map
4. **State your final classification** (X automatable / Y structured LLM / Z prose)
5. **State your final pipeline design** (phase ordering, gates, form format)
6. **Final verdict and conditions**

Write your response to your outbox file.
