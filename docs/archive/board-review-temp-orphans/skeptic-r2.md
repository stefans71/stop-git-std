# Skeptic — Round 2 Pipeline Methodology Consolidation

## Verdict: APPROVE WITH CONDITIONS

After reviewing all three Round 1 analyses and the V2.4 prompt, I concur with the fundamental direction but with stricter classification boundaries. The 11/5/4 split is overly optimistic; reality is 7/8/5.

---

## 1. Dispute Resolution D1-D5

### D1: General vulnerability severity (not C20/F9/F15)
**Prompt rule (lines ~807-808):** "**Tier 2 — Warning unless mitigated:**" followed by list of patterns requiring mitigation assessment.

**Exact quote:** "Tier 2 — Warning unless mitigated: [...] The prompt says 'Warning unless mitigated' for Tier 2, meaning the LLM must assess whether mitigation exists."

**Vote: STRUCTURED LLM**

**Reasoning:** The prompt explicitly requires mitigation assessment ("Warning **unless mitigated**"). Determining whether a mitigation exists (e.g., "CORS `*` with credentials" but behind auth proxy) requires contextual understanding of the codebase and deployment. This is judgment, not table lookup.

### D2: Split-axis decision (F4)
**Prompt rule (line ~975):** "**F4 — Split-verdict rule (broadened in V2.3 / C8).** Emit a split verdict whenever a single headline would mean opposite things to two distinct reader groups."

**Exact quote:** "Emit a split verdict whenever a single headline would mean opposite things to two distinct reader groups."

**Vote: STRUCTURED LLM**

**Reasoning:** Determining whether a headline "would mean opposite things" requires semantic understanding of audience perspectives and risk interpretation. The axis choice (`version` vs `deployment`) is an enum, but the triggering condition is judgment-based.

### D3: Priority evidence selection
**Prompt rule (line ~949):** "**Falsification criterion (C19).** Priority evidence is strictly the evidence whose falsification would change the top-line verdict. Include 2–3 items max. Before marking an item priority, articulate this sentence to yourself: 'If this claim were false, the verdict would change from X to Y.'"

**Exact quote:** "If this claim were false, the verdict would change from X to Y."

**Vote: STRUCTURED LLM**

**Reasoning:** Counterfactual reasoning about evidence→finding→severity→verdict causal chains requires understanding dependencies. While the output is structured (`priority_evidence: [evidence_id, ...]`), the selection logic involves judgment about which evidence is most consequential.

### D4: Exhibit grouping
**Prompt rule (line ~9):** "**[S8-3] Exhibit rollup.** When a section has 7+ similar-severity items, roll into themed exhibit panels (vuln/govern/signals) using `<details>/<summary>`."

**Exact quote:** "When a section has 7+ similar-severity items, roll into themed exhibit panels (vuln/govern/signals)"

**Vote: AUTOMATABLE**

**Reasoning:** The 7+ threshold is arithmetic. "Similar-severity" means same severity level (Critical/Warning/Info). Theme assignment (vuln/govern/signals) could be automated with finding-type tags. This is deterministic counting and categorization.

### D5: Silent vs unadvertised (F5)
**Prompt rule (lines ~989-991):** "**F5 — Silent vs unadvertised language rule.** Do NOT use the word 'silent' if the release title or changelog entry references the fixed attack class. Use: [...] **'Unadvertised security fix'** — when an advisory is missing but release notes mention the fix (e.g., release title 'Hardening release: symlink-safe writes')."

**Exact quote:** "Do NOT use the word 'silent' if the release title or changelog entry references the fixed attack class."

**Vote: STRUCTURED LLM**

**Reasoning:** Determining whether release notes "reference the fixed attack class" requires semantic matching between vulnerability patterns and release note prose. This is text classification with domain knowledge, not keyword matching.

---

## 2. Deferred Items Voting

### Package Review (PD1-7):
- **PD1: V2.3 reference scans → legacy label or upgrade** — AGREE DEFER
- **PD2: MD↔HTML content parity validator** — PROMOTE TO FIX NOW (critical for report integrity)
- **PD3: Bundle/citation validator** — AGREE DEFER
- **PD4: CSS sync check in --report mode** — PROMOTE TO FIX NOW (S8 design rules depend on CSS)
- **PD5: Test suite (tests/test_validator.py)** — PROMOTE TO FIX NOW (essential for automation)
- **PD6: CI/CD integration examples** — AGREE DEFER
- **PD7: Offline font bundling** — AGREE DEFER

### Schema Review (SD1-10):
- **SD1: `components[]` for monorepo/multi-shape repos** — PROMOTE TO FIX NOW (C11 monorepo enumeration already exists)
- **SD2: Finding `kind` + `domain` orthogonal typing** — AGREE DEFER
- **SD3: Confidence scores on synthesis objects** — AGREE DEFER
- **SD4: Judgment fingerprint** — AGREE DEFER
- **SD5: Plausibility check layer (soft validator warnings)** — PROMOTE TO FIX NOW (prevents obvious errors)
- **SD6: Per-field source tags** — PROMOTE TO FIX NOW (essential for provenance)
- **SD7: Variable scorecard length (min 1, no max)** — AGREE DEFER
- **SD8: Generic `artifacts[]` model** — AGREE DEFER
- **SD9: Generic `permissions[]` abstraction** — AGREE DEFER
- **SD10: SBOM integration** — AGREE DEFER

### Pipeline Review (RD1-5):
- **RD1: V2.0 automation of structured LLM operations (Category 2)** — PROMOTE TO FIX NOW (core to pipeline design)
- **RD2: Corpus test on 20+ scans before promoting structured items to code** — PROMOTE TO FIX NOW (essential validation)
- **RD3: LLM fallback mode if automated computation fails** — PROMOTE TO FIX NOW (robustness requirement)
- **RD4: "Assumptions" field in investigation form** — AGREE DEFER
- **RD5: Management sign-off field (2-1 for including; Pragmatist dissented)** — AGREE DEFER (Pragmatist is correct: sign-off belongs outside scanner)

---

## 3. Prompt Requirements NOT in Lineage Map

**Missing from data lineage map (1140 lines):**

1. **S8-1: Utility-class rule** — "Zero `style=""` attributes on `<body>` elements. Use `.val-good`/`.val-bad`/`.val-warn`/`.val-info`, `.fw-semi`, `.stack-md`/`.stack-sm`, `.p-meta`/`.p-meta-tight`." (line 8)
   - **Impact:** CSS class enforcement for consistent rendering
   - **Should be:** DP-120 (design rule compliance)

2. **S8-8: `rem`-only font sizes** — "No `px` font-sizes in `<style>` (exception: 0px). The A+/A- controls need rem to work." (line 14)
   - **Impact:** Accessibility feature dependency
   - **Should be:** DP-121 (accessibility compliance)

3. **S8-12: Validator gate** — "`python3 validate-scanner-report.py --report <file>` + `--markdown <file>` must both exit 0 before delivery." (line 16)
   - **Impact:** Mandatory quality gate
   - **Should be:** DP-122 (validation requirement)

4. **Rate-limit budget check (W2)** — "Step 5 is the most API-heavy phase. Check remaining rate limit before proceeding." (line ~377)
   - **Impact:** Operational reliability
   - **Should be:** DP-123 (operational check)

5. **F16: Windows-specific grep patterns** — Patterns for `.ps1`/`.bat`/`.cmd` files (lines ~697-710)
   - **Impact:** Cross-platform coverage
   - **Should be:** DP-124 (platform-specific patterns)

6. **C19 design principle enforcement** — "Cyan = landmark. Amber/red/green = severity. (Design principle — enforced by CSS, not by the LLM — C19.)" (line 910)
   - **Impact:** Visual consistency rule
   - **Should be:** DP-125 (design system rule)

**Total missing: 6 design/operational requirements** (S8-1, S8-8, S8-12, W2, F16, C19)

---

## 4. Final Classification

**Revised: 7 / 8 / 5** (was 11/5/4)

### Category 1: Fully automatable (7)
1. Verdict determination (after severity resolved)
2. Scorecard cell colors (calibration table)
3. Solo-maintainer flag (>80% arithmetic)
4. Exhibit grouping (7+ threshold counting)
5. Boundary-case detection (threshold arithmetic)
6. Coverage cell status (exit code mapping)
7. Methodology boilerplate (S08 template)

### Category 2: Structured LLM (8)
1. Threat model (F13) — path enum selection
2. Action steps (S01) — type enum + command templates
3. Timeline events (S04) — factual dates with labels
4. Capability assessment (DP-115) — capability enum
5. Catalog metadata (DP-112) — category/subcategory
6. **General vulnerability severity** (D1 moved from Category 1)
7. **Split-axis decision** (D2 moved from Category 1)
8. **Priority evidence selection** (D3 moved from Category 1)
9. **Silent vs unadvertised classification** (D5 moved from Category 1)

### Category 3: LLM prose (5)
1. "What this means for you" (contextual framing)
2. "What this does NOT mean" (counterweight explanation)
3. Finding card body (narrative synthesis)
4. Editorial caption (one-sentence summary)
5. Threat model narrative (connecting paths to repo context)

---

## 5. Final Pipeline Design

**9-phase pipeline with validation gates:**

1. **Phase 1:** LLM runs tools → raw outputs captured (incremental, section-by-section)
2. **Phase 2:** Data validation gate (consistency checks: SHA match, chronological ordering, tarball integrity)
3. **Phase 3:** Python computes 7 automatable fields (verdict, scorecard colors, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate)
4. **Phase 4:** LLM fills 8 structured fields (with enum/template constraints)
5. **Phase 5:** LLM writes 5 prose fields (with structural constraints)
6. **Phase 6:** JSON assembly with provenance tags (`source_type: raw | computed | structured_llm | prose_llm`)
7. **Phase 7:** Python renderer → MD + HTML (deterministic)
8. **Phase 8:** Validator gate (form completeness, evidence linkage, S8 rule compliance)
9. **Phase 9:** Git hook spot-checks (5 commands: HEAD SHA, branch protection, rulesets, OSSF score, random evidence)

**Investigation form:** JSON (not YAML), incremental fill with `_meta.phases_completed[]` tracking.

---

## 6. Final Conditions

**APPROVE WITH 5 CONDITIONS:**

1. **Update classification tables** to reflect 7/8/5 split (not 11/5/4).
2. **Add missing 6 requirements** to data lineage map (S8-1, S8-8, S8-12, W2, F16, C19).
3. **Implement Phase 2 data validation** before computation (SHA match, contributor count, chronological ordering).
4. **Build corpus test** (20+ scans) before promoting any structured operation to code.
5. **Fix PD2, PD4, PD5, SD1, SD5, SD6, RD1, RD2, RD3** (promoted items) in V1.0.

The analysis is fundamentally sound but requires these corrections to avoid over-optimism about automation scope. The data lineage map is exceptionally thorough (1140 lines, 118 data points) and justifies the pipeline architecture.