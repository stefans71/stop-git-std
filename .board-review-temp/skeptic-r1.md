# Skeptic — Pipeline & Methodology Review
## Verdict: APPROVE WITH CONDITIONS

## 1. Agreement with 11/5/4 classification
**Mostly correct, but three misclassifications require correction:**

**Category 1 (Fully automatable) should be 9 operations, not 11:**
- **Remove:** "Priority evidence selection" (DP-108) - The falsification test ("evidence whose falsification would change the verdict") requires understanding causal relationships between evidence and verdict that is not purely algorithmic. This is judgment.
- **Remove:** "Exhibit grouping" (DP-110) - While the 7+ threshold is mechanical, "similar-severity items" and "themed exhibit panels" require semantic grouping judgment. Theme assignment ("vuln", "govern", "signals") is not purely severity-based.

**Category 2 (LLM required but structured) should be 7 operations, not 5:**
- **Add:** Priority evidence selection (moved from Category 1)
- **Add:** Exhibit grouping (moved from Category 1)

**Category 3 (LLM creative prose) remains 4 operations.**

**Corrected classification: 9/7/4**

## 2. Automate in V1.0 or V2.0?
**Automate the 9 mechanical operations in V1.0.** The analysis shows these are deterministic decision trees already encoded in prompt rules. Implementing them in Python:
- Eliminates LLM drift on threshold calculations (e.g., 31 vs 30 days)
- Guarantees identical outputs for identical inputs
- Reduces prompt complexity and token usage
- Provides clear validation points

**Exception:** Keep "Methodology boilerplate" (DP-118) as LLM-generated in V1.0 since it's trivial and low-risk, but template it for V2.0.

## 3. Structured operation enums/templates
**For the 7 structured operations:**

**Threat model (DP-103):** Closed enum of attacker paths with LLM contextualization. The prompt already enumerates paths; formalize as: `["phishing", "stale_token", "session_compromise", "malicious_extension", "sloppy_review", "runner_compromise", "supply_chain_compromise", "insider_threat"]`. LLM selects applicable + adds one contextual sentence per selected path.

**Action steps (DP-106):** Fixed template set with parameterization. Templates for: `install_normally`, `pin_version`, `set_config_flag`, `nudge_maintainer`, `upgrade_required`, `do_not_install`. LLM fills repo-specific values into template commands.

**Timeline (DP-109):** Controlled vocabulary for labels: `["VULN_REPORTED", "FIX_COMMITTED", "FIX_SHIPS", "NO_ADVISORY", "SILENT_FIX", "RELEASE_CUT", "SECURITY_POLICY_ADDED", "CODEOWNERS_ADDED", "BRANCH_PROTECTION_ENABLED", "ABANDONED_PR"]`. LLM selects which factual events to include and assigns labels.

**Capability assessment (DP-115):** Capability enum: `["arbitrary_code_execution", "file_exfiltration", "network_access", "credential_access", "prompt_injection_channel", "persistence", "privilege_escalation", "none"]`. LLM selects applicable + contextual sentence.

**Catalog metadata (DP-112):** Controlled lists for category/subcategory based on existing scans. Category: `["infrastructure", "developer_tool", "library", "framework", "cli_tool", "github_action", "documentation"]`. Subcategory per category.

**Priority evidence selection (DP-108):** Structure as `priority_evidence: [{evidence_id, falsification_would_change_verdict_to, reasoning}]`. LLM provides reasoning for selection.

**Exhibit grouping (DP-110):** Structure as `exhibits: [{theme: "vuln"|"govern"|"signals", title: string, finding_ids: []}]`. LLM groups findings thematically.

## 4. Prose field templates
**Provide lightweight sentence templates for the 4 prose operations:**

**"What this means for you" (DP-104):** Template: "When you install {repo}, you are trusting {trust_surface} because {governance_gap}. The blast radius is {stars} stars and {forks} forks." LLM fills variables and expands.

**"What this does NOT mean" (DP-105):** Template: "This does NOT mean {overreaction_to_avoid} because {positive_counterbalancing_signal}." LLM specifies both parts.

**Finding card body paragraphs (DP-111):** Structural template with placeholders: "[Severity context] [Evidence synthesis with citations] [Action hint] [Threat model reference]". LLM writes prose within this structure.

**One-line editorial caption:** No template - this is genuinely creative synthesis.

**These templates guide without constraining editorial value.**

## 5. 9-phase pipeline assessment
**The pipeline is sound but needs two adjustments:**

**Add Phase 0: Pre-flight validation** - Before any tool runs, validate: repo exists, scanner has required permissions, API rate limit check, tool dependencies installed.

**Reorder Phase 8 & 9:** Validation (Phase 8) should occur *before* rendering (Phase 7). Current order renders potentially invalid JSON. Correct order:
1. Phase 1-2: LLM runs tools → raw outputs captured
2. Phase 3: Python computes 9 automatable fields
3. Phase 4: LLM fills 7 structured fields
4. Phase 5: LLM writes 4 prose fields
5. Phase 6: Complete JSON assembled
6. **Phase 7: Validator checks** (completeness, evidence linkage, provenance)
7. **Phase 8: Git hook spot-checks** (re-run key commands)
8. Phase 9: Python renderer → MD + HTML

## 6. Git hook spot-checks
**Hook should re-run 4 commands that are:**
1. **Most critical to verdict** - Branch protection status (DP-010)
2. **Most likely to change** - HEAD SHA (DP-001) to detect new commits
3. **External API with potential drift** - OSSF Scorecard score (DP-044)
4. **One random evidence item** - Select randomly from evidence list to verify consistency

**Plus verification that:** All required provenance fields are populated, evidence_refs are valid IDs, result_truncated flag is accurate.

## 7. Investigation form design
**JSON (not YAML)** - More explicit typing, better tooling support, aligns with existing schema work.

**LLM fills incrementally by section** - One investigation form per major phase (tool outputs, computed fields, structured fields, prose). This allows validation between phases and reduces context window pressure.

**Include "scan sign-off" field** - Boolean `approved_for_release: false` default, requiring manual override by authorized user. This creates a governance checkpoint.

**Add "assumptions" section** - LLM documents any assumptions made during synthesis (e.g., "assumed npm installs are from npm registry", "assumed GitHub Actions run in GitHub-hosted runners").

## Corrections to the analysis
1. **DP-108 (Priority evidence)** is not fully automatable - requires causal reasoning about evidence-verdict relationships.
2. **DP-110 (Exhibit grouping)** requires thematic judgment beyond mechanical thresholds.
3. **DP-114 (Solo-maintainer)** analysis misses that the >80% threshold applies verbatim text, but <80% still requires LLM judgment about maintainer concentration.
4. **The pipeline diagram** shows LLM writing MD then HTML - but current implementation writes MD only. HTML rendering is separate.
5. **Missing data point:** LLM's decision to sample vs exhaustive checking (e.g., checking 5 vs 50 PRs) - this affects coverage reporting.

## Final conditions
1. **Correct the classification** to 9/7/4 as specified above.
2. **Implement Phase 0 (pre-flight)** and **reorder validation before rendering**.
3. **Add "assumptions" field** to investigation form.
4. **Before implementing automation**, create test suite that runs both Python decision trees and LLM prompt rules on 10+ diverse repos to verify identical outputs.
5. **Document edge cases** for each automatable operation with explicit handling rules (e.g., tie-breaking for split-axis when both axes apply).
6. **Retain LLM fallback mode** - If automated computation fails or produces invalid result, fall back to LLM with logging of the failure.

**The analysis is fundamentally sound and the proposed architecture significantly improves repeatability while preserving necessary LLM judgment.**