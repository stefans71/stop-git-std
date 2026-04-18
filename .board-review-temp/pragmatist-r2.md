# Pragmatist — Pipeline R2 (Consolidation)

## Disputed operations (with prompt quotes)

| # | Operation | Vote | Prompt rule (quoted) | Reasoning |
|---|-----------|------|---------------------|-----------|
| D1 | General vuln severity (not C20/F9/F15) | **STRUCTURED LLM** | Line 807: `"**Tier 2 — Warning unless mitigated:**"` followed by 10 vuln types. Line 798-822: Tier 1 says "Always critical," Tier 3 says "Info unless compounding." The word "mitigated" and "unless compounding" are judgment calls — the prompt provides NO decision tree for determining whether mitigation exists or whether compounding applies. Contrast with C20 (line 163-187), which IS a boolean formula. | I maintain my R1 position. C20/F9/F15 have hard tables; general vuln severity does not. The Skeptic's "Auto" vote ignores that "unless mitigated" requires the LLM to assess context. 2-1 across the board confirms STRUCTURED LLM. |
| D2 | Split-axis decision (F4) | **STRUCTURED LLM** | Line 975-976: `"Emit a split verdict whenever a single headline would mean opposite things to two distinct reader groups."` Line 985: `"If both axes apply (rare), pick the axis whose decision is most consequential for the reader."` | "Would mean opposite things" is a semantic judgment, not a boolean test. "Most consequential" is explicitly comparative reasoning. The output is a simple enum (`null | version | deployment`), but the DECISION requires LLM interpretation of findings in context. The Skeptic's "Auto" vote conflates structured output format with deterministic selection logic. 2-1 confirms STRUCTURED LLM. |
| D3 | Priority evidence selection | **STRUCTURED LLM** | Line 949: `"Priority evidence is strictly the evidence whose falsification would change the top-line verdict. Include 2–3 items max. Before marking an item priority, articulate this sentence to yourself: 'If this claim were false, the verdict would change from X to Y.' If you can't fill in X and Y concretely, the item does not belong at the top of the appendix."` | All 3 reviewers now agree this is STRUCTURED LLM (3-0 in R1). The falsification test is a clear criterion, but APPLYING it requires counterfactual reasoning over the evidence-to-finding-to-severity-to-verdict causal chain. A Python function would need a full dependency graph of the scan's logic — that is the LLM's job. Unanimous. |
| D4 | Exhibit grouping | **AUTOMATABLE** | Line 9 (S8-3): `"When a section has 7+ similar-severity items, roll into themed exhibit panels (vuln/govern/signals) using <details>/<summary>."` Line 919: `"Fewer than 3 exhibits is OK. More than 3 means your cut is too fine."` | I maintain my R1 position. The threshold (7+) is hard. The themes (vuln/govern/signals) are a closed 3-item enum. The Skeptic says "similar-severity items" and theme assignment need judgment, but the prompt already maps severity to theme: amber=vuln, red=govern, green=signals (line 915-917). The Systems Thinker's "Partial" is fair — theme assignment is mechanical IF findings carry severity tags, which they do by this pipeline phase. Automatable with the caveat that findings must be tagged before this step runs. |
| D5 | Silent vs unadvertised (F5) | **AUTOMATABLE** with caveat | Line 989-993: `"F5 — Silent vs unadvertised language rule. Do NOT use the word 'silent' if the release title or changelog entry references the fixed attack class. Use: 'Unadvertised security fix' — when an advisory is missing but release notes mention the fix (e.g., release title 'Hardening release: symlink-safe writes'). 'Silent security fix' — only when release notes omit or mislabel the fix (e.g., a fix committed under chore: with release notes saying 'minor improvements')."` | The rule is binary: does the release text reference the attack class or not? This is keyword matching against a known vocabulary (the attack class identified by the finding). The Systems Thinker's "Partial" concern about semantic classification is valid at the margins (vague release notes), but the prompt gives concrete examples that establish a keyword-matching standard. Automatable with LLM fallback for ambiguous cases. |

**Summary of D1-D5 votes:** D1=Structured LLM, D2=Structured LLM, D3=Structured LLM (unanimous), D4=Automatable, D5=Automatable with caveat.

---

## Deferred items votes

| # | Vote | Reason |
|---|------|--------|
| PD1 | AGREE DEFER | V2.3 reference scans work as structural templates. Labeling them "legacy" is cosmetic — do it when V3 ships, not before. |
| PD2 | **PROMOTE TO FIX NOW** | MD/HTML content parity is a CLAUDE.md hard rule ("HTML may not add findings absent from MD"). A validator check for this costs one afternoon and catches a real failure mode. The V2.4 prompt says "Generate the MD first... then render it into the HTML template" but nothing enforces parity post-render. |
| PD3 | AGREE DEFER | Bundle/citation validation is valuable but depends on the JSON-first architecture existing. Premature until the investigation form is implemented. |
| PD4 | AGREE DEFER | CSS sync is a packaging concern, not a pipeline concern. Address when the design system is versioned separately. |
| PD5 | **PROMOTE TO FIX NOW** | Zero tests exist. The pipeline architecture adds Python computation functions (Phase 3) that MUST have unit tests from day one. `test_validator.py` is the foundation. Without it, the V1.0 automation of the 8 mechanical operations is untestable and therefore unshippable. |
| PD6 | AGREE DEFER | CI/CD examples are nice-to-have documentation. Not blocking. |
| PD7 | AGREE DEFER | Offline font bundling is a deployment concern, not a correctness concern. |
| SD1 | AGREE DEFER | `components[]` for monorepo is a schema extension. Current prompt handles monorepos via C11 enumeration. Schema can add this when a monorepo scan surfaces the need. |
| SD2 | AGREE DEFER | Finding `kind` + `domain` typing is a schema refinement. Current severity + status enums are sufficient for V1.0. |
| SD3 | AGREE DEFER | Confidence scores on synthesis are interesting but add complexity without clear consumer. Defer until renderers need them. |
| SD4 | AGREE DEFER | Judgment fingerprint (which LLM, which prompt version produced each synthesis field) is useful for auditing but not blocking for pipeline V1.0. |
| SD5 | AGREE DEFER | Plausibility check layer is a V2.0 quality gate. V1.0 validator is sufficient. |
| SD6 | AGREE DEFER | Per-field source tags overlap with the provenance enum (`raw | computed | structured_llm | prose_llm`). The provenance enum is simpler and sufficient for V1.0. |
| SD7 | AGREE DEFER | Variable scorecard length is a schema flexibility question. Current 4-cell scorecard is locked by the prompt. Revisit if scorecard questions ever change. |
| SD8 | AGREE DEFER | Generic `artifacts[]` model is over-abstraction at this stage. Current per-channel fields are clearer. |
| SD9 | AGREE DEFER | Generic `permissions[]` abstraction is premature. Current branch-protection and CODEOWNERS fields are domain-specific and correct. |
| SD10 | AGREE DEFER | SBOM integration is a feature, not a pipeline concern. Defer to post-V1.0. |
| RD1 | AGREE DEFER | V2.0 automation of structured LLM ops (Category 2) requires corpus validation first. Correct to defer. |
| RD2 | **PROMOTE TO FIX NOW** | Corpus test on 20+ scans before promoting structured items to code is a prerequisite for RD1. But the corpus itself must be built NOW — every new scan should be captured in the investigation form format to build the training/validation set. Start capturing structured data immediately, even if automation is deferred. |
| RD3 | AGREE DEFER | LLM fallback mode is a resilience feature. Design it into the architecture but implement after V1.0 Python functions are proven stable. |
| RD4 | AGREE DEFER | "Assumptions" field is useful documentation but not blocking. The LLM already records coverage gaps. An explicit assumptions field can be added to the investigation form without architectural impact. |
| RD5 | AGREE DEFER | Management sign-off field. I dissented in R1 and I maintain: risk acceptance is a business process, not a scan schema concern. A wrapper process (PR review on scan output) is the right place for this. The 2-1 vote to include it should not override the principle of separation of concerns. I accept the deferral as a compromise. |

**Promoted items: PD2, PD5, RD2** (3 of 22 deferred items).

---

## Prompt coverage gaps (requirements NOT in lineage map)

After cross-referencing the V2.4 prompt against the data lineage map's 118 data points:

1. **DP-026 classification missing.** The lineage map documents DP-026 (targeted read of grep hits) as raw data with a synthesis component ("is this a true positive?") but never assigns it to Category 1, 2, or 3. This is Category 2 — true-positive/false-positive classification of grep hits requires LLM judgment with AST-level understanding.

2. **F12 two-layer inventory format not traced.** The prompt (line 1009-1018) requires a two-layer format for every executable file: a one-line summary AND a collapsed detailed card. The lineage map captures DP-030 (7 properties per file) but does not trace the one-line summary layer separately. This matters because the one-line summary is a synthesis operation (condensing 7 properties into one sentence) that belongs in Category 2.

3. **Scorecard consistency re-check not traced as a separate operation.** The prompt (line 763-768) specifies a post-calibration consistency check: "If any finding is critical, no scorecard cell may be green." The lineage map mentions this within DP-102 but does not trace it as a distinct computational step. It should be: a separate Category 1 (automatable) operation that runs AFTER scorecard cell computation and AFTER severity assignment, enforcing cross-field constraints.

4. **C15 config-defaults PR path matching not traced.** The prompt (line 407-422) extends security-relevant PR detection to include defaults/config files. The lineage map captures DP-033 (security-relevant PR identification) but does not separately trace the C15 path extension. This matters because the path list is a hard-coded pattern that is fully automatable — it should be explicit in the lineage map.

5. **HTML-escaping of repo content (line 1019-1020) not traced.** The prompt requires HTML-escaping of all inserted text from the repo. This is a Category 1 (fully automatable) operation that is absent from the lineage map. It matters because un-escaped repo content in HTML is an XSS vector.

---

## Final classification: 8 / 8 / 4

After resolving disputes:

**Category 1 — Fully automatable (8 operations):**
1. Verdict determination (`max(finding_severities)`)
2. Scorecard cell colors (calibration table)
3. Solo-maintainer flag (>80% threshold + verbatim sentence)
4. Exhibit grouping (7+ threshold + 3-theme enum)
5. Boundary-case detection (threshold arithmetic)
6. Coverage cell status (command exit code mapping)
7. Methodology boilerplate (template)
8. F5 silent vs unadvertised (keyword matching with LLM fallback)

Plus 3 sub-operations that are automatable components of larger operations:
- C20 severity formula (within severity assignment)
- F9 severity table (within severity assignment)
- F15 tier table (within severity assignment)
- Scorecard consistency re-check (post-computation constraint enforcement)
- HTML-escaping (rendering step)

**Category 2 — Structured LLM (8 operations):**
1. General vulnerability severity (Tier 1/2/3 with "unless mitigated/compounding" judgment)
2. Split-axis decision (F4 — "opposite things to two reader groups")
3. Priority evidence selection (falsification counterfactual)
4. Threat model (F13 — path enum + contextual framing)
5. Action steps (S01 — action type enum + command templates + prose)
6. Timeline events (S04 — event selection + label composition)
7. Capability assessment (capability enum + contextual sentence)
8. Catalog metadata (category/subcategory from controlled vocabulary + short description)

**Category 3 — LLM prose (4 operations):**
1. "What this means for you" (editorial risk framing)
2. "What this does NOT mean" (editorial guardrails)
3. Finding card body paragraphs (narrative synthesis with citations)
4. One-line editorial caption (creative summary)

---

## Final pipeline design

9 phases, revised from R1 with board convergence:

```
Phase 1:  LLM runs tools, captures raw outputs into investigation form
          (incremental, section by section, following prompt step ordering)

Phase 2:  Data validation gate
          - SHA consistency (tarball vs captured HEAD SHA)
          - Required field completeness check
          - Chronological ordering of dates
          - Tarball file count > 0
          - No null required fields after all steps complete

Phase 3:  Python computes 8 automatable fields
          - Input: validated raw data from Phase 1
          - Output: computed fields with provenance tag "computed"
          - Unit tests required (PD5 promoted)

Phase 4:  LLM fills 8 structured fields
          - Constrained by enums, templates, controlled vocabularies
          - Output tagged with provenance "structured_llm"
          - Each field has a required evidence_ref linking to raw data

Phase 5:  LLM writes 4 prose fields
          - Structural constraints (mandatory anchors, max length, citation requirements)
          - Output tagged with provenance "prose_llm"

Phase 6:  JSON assembly
          - All fields carry provenance: raw | computed | structured_llm | prose_llm
          - Evidence references validated (every ref points to existing raw data)
          - Completeness check: all required fields populated

Phase 7:  Python renderer -> MD + HTML
          - Deterministic: same JSON = same output
          - HTML-escaping of all repo-sourced text (gap #5 above)
          - CSS copied verbatim from design system

Phase 8:  Validator gate
          - Form completeness
          - Evidence linkage (every finding has evidence)
          - Provenance tagging (every field has source_type)
          - MD/HTML content parity (PD2 promoted)
          - Structural checks (tag balance, no placeholders, rem-only fonts)

Phase 9:  Spot-check verification
          - Re-run 5 commands: HEAD SHA, branch protection, OSSF score,
            rules-on-default-branch, one random priority evidence item
          - Compare outputs to stored raw captures
          - Non-zero exit blocks delivery
```

**Form format:** JSON, incremental fill, phase tracking via `_meta.phases_completed[]`. No management sign-off field.

**Provenance tags:** Every field carries `source_type: raw | computed | structured_llm | prose_llm`. This is the convergence point — all 3 R1 reviewers agreed on provenance tagging.

---

## Final verdict and conditions

**APPROVE WITH CONDITIONS**

The analysis is sound. The data lineage map is the most valuable artifact in this project. The 8/8/4 classification is the correct boundary — it is the most defensible split given the actual prompt rules.

**Conditions (3 FIX NOW, 2 architectural):**

1. **FIX NOW — PD5: Create `test_validator.py` before implementing any Phase 3 automation.** The 8 automatable functions need unit tests from day one. Test against zustand and caveman scan data as ground truth.

2. **FIX NOW — PD2: Add MD/HTML content parity check to the validator.** This is a one-function addition that catches a real failure mode already documented in the rules.

3. **FIX NOW — RD2: Start capturing structured investigation data immediately.** Every new scan should produce a findings-bundle in the investigation form JSON format, even before the automated pipeline exists. This builds the corpus needed for future automation validation.

4. **Architectural — Provenance tags are non-negotiable.** Every field in the JSON schema must carry `source_type`. Do not ship the schema without this. All 3 reviewers agree.

5. **Architectural — Do not automate Category 2 items until the corpus has 20+ scans.** The 8 structured LLM operations require corpus validation before any code replaces LLM judgment. This is RD1 + RD2 combined: capture data now, automate later.

No rework required. Proceed to implementation.
