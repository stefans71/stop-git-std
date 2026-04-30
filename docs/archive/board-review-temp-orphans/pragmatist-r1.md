# Pragmatist -- Pipeline & Methodology Review

## Verdict: APPROVE WITH CONDITIONS

The 11/5/4 classification is largely sound but has 3 misplacements that need correction before implementation. The proposed 9-phase pipeline is architecturally correct and should proceed. Conditions are itemized below.

---

## 1. Agreement with 11/5/4 classification

I verified each of the 11 "fully automatable" operations against the V2.4 prompt. Here is my assessment:

### Correctly classified as automatable (8 of 11)

1. **Verdict determination** -- Correct. `verdict = max(finding_severities)` plus the split-axis selection. Fully mechanical.

2. **Scorecard cell colors** -- Correct. The calibration table at prompt lines ~739-768 is a hard decision tree with explicit thresholds (e.g., `any-review >= 60% AND formal >= 30% AND branch protection => green`). The prompt itself says "Calibration wins over editorial judgement for colour." Automatable.

3. **Solo-maintainer flag** -- Correct. Pure arithmetic: `top_contributor_commits / total_commits > 0.80`. The verbatim sentence is specified in the prompt. Fully deterministic.

4. **Exhibit grouping** -- Correct. The threshold (7+ items) and theme vocabulary (vuln/govern/signals) are hard rules. Automatable.

5. **Boundary-case detection** -- Correct. Arithmetic comparison of actual value vs threshold with margin flagging. Automatable.

6. **Coverage cell status** -- Correct. Maps command exit codes to enum values. Deterministic.

7. **Methodology boilerplate (S08)** -- Correct. The prompt specifies 5 exact subsections with templated content. Only variable is version strings. Fully automatable.

8. **Silent vs unadvertised (F5)** -- Mostly correct, but see caveat below. The binary classification rule ("release notes mention fix => unadvertised; omit => silent") is clear. However, DETERMINING whether release notes "mention the fix" requires reading release note prose and matching it to the fixed attack class. This is a text-matching task that is straightforward for keyword hits (release title says "symlink-safe writes" and the fix is a symlink attack) but could be ambiguous for vague release notes. I'll keep this as automatable with a caveat: the Python implementation should use keyword matching against the attack class vocabulary, with an LLM fallback for ambiguous cases.

### MISCLASSIFIED -- these require LLM judgment (3 of 11)

9. **Severity assignment (C20)** -- PARTIALLY MISCLASSIFIED. The C20 governance-gap severity IS a boolean formula and is automatable. But the brief claims severity assignment OVERALL is automatable, and the prompt has MULTIPLE severity systems:
   - C20 governance gap: boolean formula -- YES automatable
   - F9 agent-rule content: pattern table -- YES automatable
   - F15 action pinning tiers: tier table -- YES automatable
   - General vulnerability tiers (Tier 1/2/3): "adjust based on context" -- NO, requires LLM judgment. The prompt says "Warning unless mitigated" for Tier 2, meaning the LLM must assess whether mitigation exists.
   - Per-finding severity when multiple rules interact -- the prompt has no explicit precedence rule for when a finding triggers multiple severity tables simultaneously.

   **Correction:** Split this into two items. C20/F9/F15 severity formulas are automatable (keep in Category 1). General vulnerability severity with mitigation assessment stays with the LLM (move to Category 2).

10. **Split-axis classification** -- MISCLASSIFIED. The prompt's F4 rule says "Emit a split verdict whenever a single headline would mean opposite things to two distinct reader groups." Determining whether a headline "would mean opposite things" is a judgment call, not a boolean formula. The prompt gives two valid axes (version, deployment) but the DECISION of whether to split at all, and which axis to pick when "both axes apply," requires understanding the semantic content of findings and their audience impact. This is LLM judgment.

    **Correction:** Move to Category 2 (structured LLM). The axis is an enum (`null | "version" | "deployment"`), but selecting it requires LLM reasoning about audience impact.

11. **Priority evidence selection** -- MISCLASSIFIED. The falsification criterion ("if this claim were false, the verdict would change") sounds mechanical but is not. To evaluate whether falsifying a piece of evidence would change the verdict, you must reason about the CAUSAL CHAIN from evidence to finding to severity to verdict. This is counterfactual reasoning -- a core LLM capability, not a decision tree. Consider: "If branch protection actually existed, would the verdict change?" requires knowing whether the C20 finding is the sole Critical, whether other findings independently sustain the verdict, etc. A simple `max()` reversal could approximate this, but the prompt explicitly limits priority evidence to "2-3 items max," meaning you must RANK counterfactual impact -- that ranking is judgment.

    **Correction:** Move to Category 2 (structured LLM). The output format is structured (`priority_evidence: [evidence_id, ...]`), but the selection logic requires LLM reasoning.

### Revised classification: 8 / 7 / 4

After corrections:
- **Fully automatable:** 8 operations (verdict, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised)
- **LLM + structure:** 7 operations (threat model, action steps, timeline, capability assessment, catalog metadata, split-axis decision, priority evidence selection) plus the general vulnerability severity sub-component of severity assignment
- **LLM prose:** 4 operations (unchanged -- "what this means," "what this does NOT mean," finding card body, editorial caption)

---

## 2. Automate in V1.0 or V2.0?

**Automate the 8 confirmed-mechanical operations in V1.0.** Reasons:

1. These are the operations most likely to DRIFT across scanner runs. A Python decision tree for C20 severity will never accidentally apply a 29-day window instead of 30-day. The LLM will.

2. They are also the cheapest to implement -- each is a small function with well-defined inputs and outputs. The calibration table and C20 formula are already pseudocode in the prompt.

3. Automating them reduces the LLM's cognitive load during the scan, making the remaining LLM operations (prose, judgment calls) higher quality.

**Implementation order for V1.0:**
1. Coverage cell status (simplest -- exit code mapping)
2. Solo-maintainer flag (one arithmetic check)
3. Boundary-case detection (threshold arithmetic)
4. Exhibit grouping (count + theme assignment)
5. Scorecard cell colors (calibration table -- most impact on report consistency)
6. Verdict determination (depends on scorecard + findings)
7. Methodology boilerplate (template substitution)
8. F5 silent/unadvertised (keyword matching with fallback)

**For V2.0:** Automate the structured LLM operations (Category 2) by providing the enums and templates, then constraining LLM output to fill slots. This is a bigger architectural change because it requires the investigation form to have structured fields the LLM populates.

---

## 3. Structured operation enums/templates

For the 7 structured operations (revised Category 2):

### Threat model (F13)
The path enum should be **extensible with a closed core.** The 6 paths in the brief (phishing, stale_token, session_compromise, malicious_extension, sloppy_review, runner_compromise) cover the common cases well. Add an `other` variant with a required `description` field. The LLM selects from the core enum and adds `other` only when a genuinely novel path exists. This prevents enum sprawl while allowing edge cases.

### Action steps (S01)
The action type enum is good. I would add one more: `audit_before_use` for repos that are caution-level but not do-not-install. The command templates should be parameterized by package manager (`npm install X@Y`, `pip install X==Y`, `cargo install X --version Y`). The prose wrapper is LLM-authored but should follow a template: "{Non-technical explanation of why}. {Command block}. {What this achieves}."

### Timeline events (S04)
Events are factual (dates from API) -- agreed. The label vocabulary should be a **recommended list, not a closed enum.** The prompt already has good/forbidden examples. Enforce: max 3 words, no date restatements, severity class required. Let the LLM compose labels within those constraints.

### Capability assessment (DP-115)
The capability enum (arbitrary_code_exec, file_exfil, network_access, credential_access, prompt_injection_channel, none) is good. Add `filesystem_write` as distinct from `file_exfil` -- writing to arbitrary paths is a different risk than reading. The contextual sentence should reference specific grep evidence: "Based on {grep_pattern} at {file}:{line}, this file could {capability}."

### Catalog metadata (DP-112)
Category and subcategory should be a **closed list maintained in the schema file.** The current prompt examples are good starting vocabulary. New categories require a schema update (not LLM invention). This prevents category drift across scans.

### Split-axis decision (moved from Category 1)
Output: `split_axis: null | "version" | "deployment"`. When non-null, require `split_entries[]` with `{scope, audience, verdict, headline, detail}`. The LLM decides IF a split is needed and WHICH axis, but the output structure is fully constrained.

### Priority evidence selection (moved from Category 1)
Output: `priority_evidence: [evidence_id, ...]` (max 3). Require a `falsification_statement` per item: "If {claim} were false, verdict would change from {X} to {Y}." This forces the LLM to articulate its reasoning, making it auditable.

---

## 4. Prose field templates

For the 4 irreducible prose operations:

**Do NOT provide rigid sentence templates.** The value of these fields IS the contextual framing. A template like "When you install {repo}, you are trusting {trust_surface} because {governance_gap}" would produce formulaic, cargo-cult prose across scans. The caveman and zustand scans read differently because they SHOULD -- the risks are fundamentally different shapes.

**Instead, provide structural constraints:**

1. **"What this means for you"** -- Must contain: (a) the trust relationship being established, (b) the specific governance gap, (c) the blast radius in concrete terms. Max 3 sentences. Must be readable by someone who does not know what "branch protection" means.

2. **"What this does NOT mean"** -- Must contain: (a) at least one specific positive signal that counterbalances, (b) an explicit statement of what the finding does NOT imply. Must reference Cole's email framing: "404 does not equal world-writable." Max 3 sentences.

3. **Finding card body** -- Must contain: evidence citations (by ID), the causal chain from evidence to conclusion, and the distinction between what IS happening vs what COULD happen. Structure is templated (severity tag, status chip, action hint, meta table) but narrative paragraphs are free prose.

4. **Editorial caption** -- One sentence, max 25 words. Must synthesize the entire scan, not just the worst finding. Should be useful as a standalone summary (e.g., in a scan catalog).

These constraints are enforceable by the validator without killing editorial quality.

---

## 5. 9-phase pipeline assessment

The proposed 9-phase pipeline is **architecturally sound** with two adjustments:

### Current proposal (from brief):
1. LLM runs tools -> raw outputs captured
2. (continuation of Phase 1)
3. Python computes 8 automatable fields
4. LLM fills 7 structured fields
5. LLM writes 4 prose fields
6. Complete JSON assembled
7. Python renderer -> MD + HTML
8. Validator checks
9. Git hook spot-checks

### Adjustments needed:

**Phase 1-2 should be split more precisely.** The prompt has a natural ordering: metadata first (Step 1), then governance (Step 1 continued), then CI/CD (Step 2), then dependencies (Step 3), then PRs (Steps 4-5), then issues/commits (Steps 6-7), then code patterns (Steps A-C), then distribution (Step 8). The investigation form should mirror this ordering with sections that can be filled incrementally.

**Phase 3 depends on Phase 1-2 completeness.** The Python computation step cannot run until ALL raw data is captured. This means Phase 2 needs a completeness check: "Are all required API calls recorded? Are any blocked/failed?" This is already partially covered by the coverage cell, but it should be an explicit gate.

**Add Phase 2.5: Data validation.** Between raw capture and computation, validate that raw data is internally consistent (e.g., the HEAD SHA in the tarball matches the captured SHA, the contributor count matches the contributor list length, release dates are chronologically ordered). This catches data corruption before it propagates into computed fields.

### Revised pipeline:
1. LLM runs tools, captures raw outputs into investigation form (incremental, section by section)
2. Data validation gate (consistency checks on raw data)
3. Python computes 8 automatable fields from validated raw data
4. LLM fills 7 structured fields (with enums/templates constraining output)
5. LLM writes 4 prose fields (with structural constraints)
6. JSON assembly (facts + computed + structured + prose)
7. Python renderer -> MD + HTML (deterministic)
8. Validator gate (form completeness, evidence linkage, provenance tagging, structural checks)
9. Git hook spot-checks (re-run 3-5 tool commands, verify outputs match)

This is a 9-phase pipeline with a cleaner Phase 2.

---

## 6. Git hook spot-checks

The hook should re-run **5 commands** chosen to cover different data sources and catch different failure modes:

1. **HEAD SHA verification** -- `gh api "repos/$OWNER/$REPO/commits/HEAD" -q '.sha'`. Compare to `head_sha` in the JSON. Catches: stale scan, force-push between scan and delivery. Cheapest check, highest signal.

2. **Branch protection classic API** -- `gh api "repos/$OWNER/$REPO/branches/$DEFAULT_BRANCH/protection"`. Compare HTTP status code to `branch_protection.classic.status`. Catches: protection added/removed between scan and delivery, incorrect 404-vs-403 recording.

3. **OSSF Scorecard overall score** -- `curl -s "https://api.securityscorecards.dev/projects/github.com/$OWNER/$REPO" | jq '.score'`. Compare to `ossf_scorecard.overall_score`. Catches: OSSF re-indexing that materially changes the score, API errors silently recorded as data.

4. **Star count** -- `gh repo view "$OWNER/$REPO" --json stargazerCount -q '.stargazerCount'`. Compare with 10% tolerance to `stargazer_count`. Catches: data recording errors, star manipulation between scan and delivery.

5. **One random evidence item from priority evidence** -- Select one `evidence_id` from `priority_evidence[]`, re-run the exact command recorded in the evidence entry, compare output. Catches: fabricated evidence, command transcription errors. This is the most valuable check because it validates the evidence chain, not just metadata.

**Implementation notes:**
- The hook should exit non-zero if ANY check fails, with a clear error message identifying which check and what the discrepancy is.
- Allow a `--skip-external` flag for offline environments (skips OSSF check).
- The random evidence check should be seeded by the scan SHA so it is reproducible but not predictable by the LLM.

---

## 7. Investigation form design

### JSON, not YAML.

Reasons:
1. The downstream pipeline is Python. `json.load()` is stdlib; YAML requires `pyyaml` (extra dependency).
2. JSON has no ambiguity around types -- `"404"` vs `404` is explicit. YAML's type inference (`yes` -> boolean) has caused bugs in every project I've seen use it for structured data.
3. The form will be programmatically read by the Python computation layer and the renderer. JSON round-trips cleanly.
4. LLMs produce valid JSON more reliably than valid YAML (indentation sensitivity is an LLM weakness).

### Incremental fill, not all-at-once.

The LLM should fill the form section by section as it completes each investigation phase. Reasons:
1. A 118-field form filled in one shot will have more errors than one filled incrementally with validation between sections.
2. Incremental filling allows early termination if a blocking error occurs (e.g., tarball extraction fails at Phase 1 -- no point continuing).
3. It maps naturally to the prompt's step-by-step structure.

**Implementation:** The form starts as a skeleton with all fields present but null-valued. Each investigation step populates its section. A `_meta.phases_completed[]` array tracks which phases have run. The Phase 3 computation step checks `_meta.phases_completed` before running.

### No "scan sign-off" field.

A management sign-off field in the investigation form conflates two concerns: data quality (is the scan correct?) and risk acceptance (do we trust this repo?). The scan produces facts and analysis. Risk acceptance is a business decision that happens AFTER reading the report, not inside the scanning tool. If management review is needed, it belongs in a wrapper process (e.g., a PR review on the scan output), not in the scan schema itself.

---

## Corrections to the analysis (if any)

1. **DP-026 (targeted read of grep hits) is missing from the synthesis classification.** The brief classifies it as raw data with a synthesis component ("is this a true positive?"), but does not assign it to any of the three categories. This is a Category 2 operation -- the LLM reads 5 lines of context and classifies a grep hit as true positive or false positive. It could be partially automated with AST parsing for some languages but requires LLM for cross-language coverage. Add it to Category 2.

2. **DP-042 (distribution channel verification table) has a synthesis component not fully captured.** The scorecard constraint ("if any channel unverified, safe-out-of-box cannot exceed amber") is automatable (Category 1). But the per-channel "resolves to" determination (e.g., "marketplace manifest -> main HEAD") requires understanding the distribution mechanism, which is LLM judgment. The brief correctly notes this in the DP-042 entry but does not account for it in the summary tables.

3. **The brief counts 54 raw data points and 19 synthesis points = 73 total, but claims 118.** The 118 figure appears to count sub-fields within data points (e.g., DP-003 has ~10 sub-fields). The brief should clarify: 54 data point GROUPS, 118 individual fields, 19 synthesis operations. This distinction matters for the JSON schema (118 fields, not 54).

4. **DP-112 (catalog metadata) is classified as "MOSTLY" automatable in the summary table but listed as Category 2 in the schema implications section.** These are consistent in spirit but the brief should pick one label. I agree with Category 2 -- the category/subcategory selection needs LLM, even if most other fields are factual.

---

## Final conditions

The analysis should proceed to implementation with these 4 conditions:

1. **Reclassify the 3 misplaced operations** (general vulnerability severity, split-axis decision, priority evidence selection) from Category 1 to Category 2. The revised count is 8/7/4. Update all summary tables to match.

2. **Add Phase 2.5 (data validation gate)** to the pipeline between raw capture and computation. Define at least 5 consistency checks (SHA match, contributor count, chronological ordering, tarball file count > 0, no null required fields).

3. **Use JSON for the investigation form**, with incremental fill and phase tracking. No management sign-off field in the schema.

4. **Implement the 8 automatable operations in V1.0** as Python functions with unit tests. Each function takes the relevant raw data fields as input and returns the computed field. Test against the zustand and caveman scan data as ground truth.

No rework needed. The analysis is thorough, the data lineage map is the most valuable artifact produced in this project to date, and the proposed architecture is correct in its fundamental insight: most of what the scanner produces is deterministic, and only 4 fields genuinely vary. That insight alone justifies the effort.
