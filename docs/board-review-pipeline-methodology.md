# Board Review: Pipeline Methodology & Data Lineage

**Date:** 2026-04-17 to 2026-04-18
**Subject:** Scanner data pipeline architecture — facts vs synthesis classification, investigation form design
**Rounds completed:** 4 (Package R1-R2) + 4 (Schema R1-R4) + 2 (Pipeline R1-R2)
**Total board sessions:** 10 rounds across 3 review topics

---

## Board Composition

| Agent | Model | Role |
|-------|-------|------|
| Pragmatist | Claude Opus 4.6 (sub-agent) | Operational focus, prompt cross-reference |
| Systems Thinker | GPT-5.4 (Codex via llmuser) | Architectural integrity, coverage gaps |
| Skeptic | DeepSeek V3.2 (via Qwen CLI) | Adversarial review, classification challenges |

---

## Final Verdicts: UNANIMOUS APPROVE WITH CONDITIONS

## Key Outcome: Data Lineage Map

118 data points traced across the scanner pipeline:
- **54 raw data points** (DP-001 through DP-054) — tool commands with deterministic output
- **19 synthesis operations** (DP-100 through DP-118) — LLM judgment with varying repeatability
- Full map at: `.board-review-temp/data-lineage-map.md` (1140 lines)

## Board-Approved Classification: 8 / 8 / 4

### Category 1: Fully Automatable (8 operations — implement as Python in V1.0)

| # | Operation | Prompt rule | Input | Output |
|---|-----------|-------------|-------|--------|
| 1 | Verdict determination | `verdict = max(finding_severities)` | All finding severities | `verdict.level` enum |
| 2 | Scorecard cell colors | Calibration table (lines ~739-768) | PR rates, branch protection, OSSF | 4 cells with red/amber/green |
| 3 | Solo-maintainer flag | F11: `>80% commits` → verbatim sentence | Contributor list | Boolean + sentence |
| 4 | Exhibit grouping | S8-3: `7+ similar-severity items` → themed panels | Finding count + severities | Exhibit array |
| 5 | Boundary-case detection | Threshold proximity arithmetic | Actual values vs thresholds | Boundary notes |
| 6 | Coverage cell status | Command exit code mapping | Command results | Status enum |
| 7 | Methodology boilerplate | S08 template (identical across all 9 scans) | Version strings | Section 08 content |
| 8 | F5 silent vs unadvertised | Keyword matching against attack class | Release notes text | Classification enum |

### Category 2: Structured LLM (8 operations — constrained by enums/templates)

| # | Operation | Constraint | Freedom level |
|---|-----------|-----------|---------------|
| 1 | General vuln severity | Tier 1/2/3 table + "unless mitigated" | LOW-MEDIUM |
| 2 | Split-axis decision | F4: "opposite things to two groups" | LOW |
| 3 | Priority evidence selection | Falsification criterion, max 3 items | LOW |
| 4 | Threat model (F13) | Path enum + contextual framing | MEDIUM |
| 5 | Action steps (S01) | Action type enum + command templates | MEDIUM |
| 6 | Timeline events (S04) | Factual dates + label vocabulary | MEDIUM |
| 7 | Capability assessment | Capability enum + contextual sentence | MEDIUM |
| 8 | Catalog metadata | Category/subcategory controlled vocab | LOW |

### Category 3: LLM Prose (4 operations — structural constraints only)

| # | Operation | Constraint |
|---|-----------|-----------|
| 1 | "What this means for you" | Must contain trust relationship, governance gap, blast radius. Max 3 sentences. |
| 2 | "What this does NOT mean" | Must contain positive counterbalance, explicit non-implication. Max 3 sentences. |
| 3 | Finding card body paragraphs | Evidence citations required, causal chain, IS vs COULD distinction |
| 4 | One-line editorial caption | Max 25 words, synthesize full scan |

## Board-Approved Pipeline: 9 Phases

```
Phase 1:  LLM runs tools → raw outputs captured into investigation form (JSON)
          (incremental, section by section, following prompt step ordering)

Phase 2:  Data validation gate
          - SHA consistency (tarball vs captured HEAD SHA)
          - Required field completeness
          - Chronological ordering
          - No null required fields

Phase 3:  Python computes 8 automatable fields
          - provenance tag: "computed"
          - Unit tests required

Phase 4:  LLM fills 8 structured fields
          - Constrained by enums, templates, controlled vocabularies
          - provenance tag: "structured_llm"
          - evidence_refs required on non-OK findings

Phase 5:  LLM writes 4 prose fields
          - Structural constraints (anchors, max length, citations)
          - provenance tag: "prose_llm"

Phase 6:  JSON assembly
          - All fields carry provenance: raw | computed | structured_llm | prose_llm
          - Evidence references validated
          - Completeness check

Phase 7:  Python renderer → MD + HTML
          - Deterministic: same JSON = same output
          - HTML-escaping of repo-sourced text

Phase 8:  Validator gate
          - Form completeness, evidence linkage, provenance tagging
          - MD/HTML content parity (PD2)
          - S8 structural checks

Phase 9:  Git hook spot-checks
          - 5 commands: HEAD SHA, branch protection, rulesets, OSSF score,
            one random priority evidence item
          - Non-zero exit blocks delivery
```

## Promoted from Deferred to FIX NOW (V1.0)

| Item | Source | Votes | Notes |
|------|--------|-------|-------|
| PD2: MD/HTML content parity validator | Package review | 3-0 | One-function addition to validator |
| PD5: Test suite (`test_validator.py`) | Package review | 3-0 | Foundation for Phase 3 automation |
| RD2: Start capturing structured corpus | Pipeline review | 3-0 | Every scan captures investigation form JSON |
| SD1: `components[]` for monorepo | Schema review | 2-1 | Pragmatist dissented (no monorepo scans yet) |
| SD5: Plausibility warning layer | Schema review | 2-1 | Pragmatist dissented (V1.1 scope) |
| SD6: Per-field source tags | Schema review | 2-1 | Pragmatist dissented (provenance enum sufficient) |
| RD3: LLM fallback mode | Pipeline review | 2-1 | Pragmatist dissented (implement after V1.0 stable) |

## Prompt Coverage Gaps Found

Combined from all 3 reviewers — requirements in V2.4 prompt NOT captured in data lineage map:

1. Status chips not modeled as structured output (Codex)
2. Per-finding action hints under-specified (Codex)
3. Split-verdict formatting obligations partial (Codex)
4. Section-level action blocks missing (Codex)
5. Unknown-state escalation rule (Codex)
6. DP-026 grep hit classification missing (Pragmatist)
7. F12 two-layer inventory format (Pragmatist)
8. Scorecard consistency re-check as separate step (Pragmatist)
9. C15 config-defaults PR path matching (Pragmatist)
10. HTML-escaping of repo content (Pragmatist)
11. S8-1 utility-class rule (DeepSeek)
12. S8-8 rem-only font sizes (DeepSeek)
13. S8-12 validator gate requirement (DeepSeek)
14. W2 rate-limit budget check (DeepSeek)
15. F16 Windows-specific grep patterns (DeepSeek)
16. C19 color design principle (DeepSeek)

## Raw Reviews

All stored at `/root/tinkering/stop-git-std/.board-review-temp/`:
- `pipeline-methodology-brief.md` — original brief
- `data-lineage-map.md` — 1140-line lineage map
- `pipeline-r2-brief.md` — R2 consolidation brief
- `pragmatist-r1.md`, `pragmatist-r2.md`
- `systems-thinker-r1.md`, `systems-thinker-r2.md`
- `skeptic-r1.md`, `skeptic-r2.md`
