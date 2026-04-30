# Board Review: Scanner Data Pipeline & Methodology

## What you are reviewing

A data lineage analysis of the GitHub repo security scanner, mapping every data point from its source through to the final report. This analysis changes the proposed JSON-first architecture significantly.

## How we arrived at this analysis

### Step 1: Board reviewed package-V2 (Rounds 1-2)
- 3-model board reviewed the 17-file distribution package
- Verdict: SHIP WITH CONDITIONS (2-1, 6 FIX NOW items implemented)
- Board found: scorecard question mismatch in gold standard, stale references, path leaks

### Step 2: Board reviewed JSON schema design (Rounds 1-2)
- Structural analysis of all 9 completed scans extracted universal vs shape-specific fields
- Board converged on 14 FIX NOW items for the schema structure
- Board reviewed raw MD data (zustand + caveman) alongside the proposed schema

### Step 3: Critical insight surfaced — facts vs LLM synthesis
- We identified that the data populating the schema comes from two fundamentally different sources:
  - **Deterministic tool output** (gh API calls, OSSF API, grep, gitleaks) — same input, same output
  - **LLM synthesis** (severity, verdict, scorecard answers, threat models, prose) — varies across runs
- Board reviewed this in Round 3 (Deliberation) and Round 4 (Consolidation)
- Unanimous agreement: schema must distinguish facts from synthesis
- Converged on: `provenance` enum on findings, `evidence_refs` required, `result_truncated` flag

### Step 4: Data lineage mapping (THIS REVIEW)
- We asked: for EVERY data point in the scanner, what is its source, how does the LLM process it, and what constraints apply?
- An agent read the full V2.4 prompt (~1500 lines), the Operator Guide, and two completed scans (zustand + caveman)
- The agent traced 118 data points across 11 phases
- We then analyzed the agent's output and classified each synthesis operation by automation potential

## The raw analysis

**Read this file — it is the primary artifact for this review:**

`/tmp/board-package-v2/data-lineage-map.md` (1140 lines)

It contains:
- **54 raw data points** (DP-001 through DP-054) — every `gh api` call, `grep`, `curl`, and `find` command the scanner runs, with exact commands, output formats, examples from real scans, and where each appears in the report
- **19 synthesis data points** (DP-100 through DP-118) — every LLM judgment, with the exact prompt rules that constrain it, how much synthesis freedom the LLM has, repeatability assessment, and whether it could be automated
- **Cross-cutting summary tables** — data flow from sources to report sections
- **JSON schema design implications** — which operations are automatable vs require LLM

## Our synthesis of the findings

After reviewing the 118 data points, we classified each LLM synthesis operation:

### Category 1: Fully automatable WITHOUT an LLM (11 operations)

These are currently done by the LLM following prompt rules, but the rules are deterministic enough that Python code could compute the same result:

| Operation | Current method | Why it's automatable |
|-----------|---------------|---------------------|
| Severity assignment (C20) | LLM reads calibration table | Boolean formula: `(no_protection AND no_codeowners AND recent_release AND ships_executable) → Critical` |
| Verdict determination | LLM picks max severity | `verdict = max(finding_severities)` |
| Scorecard cell colors | LLM reads threshold table | Decision tree: `formal_review >= 30% AND any_review >= 60% AND branch_protection → green` |
| Solo-maintainer flag | LLM checks commit share | `top_contributor_commits / total_commits > 0.80 → true` |
| Split-axis classification | LLM reads F4 criteria | Binary classification: version-axis vs deployment-axis based on documented criteria |
| Priority evidence selection | LLM applies falsification test | Select evidence whose falsification would change the verdict |
| Exhibit grouping | LLM applies S8-3 threshold | `if section_findings >= 7: group_into_exhibits(by_severity_theme)` |
| Silent vs unadvertised (F5) | LLM reads release notes | Text match: release notes mention fix → "unadvertised"; omit → "silent" |
| Boundary-case detection | LLM compares values | Arithmetic: `actual_value - threshold < margin → flag` |
| Coverage cell status | LLM reports command outcomes | Map command exit codes: 200→ok, 404→not_found, 403→blocked |
| Methodology boilerplate (S08) | LLM copies template text | Identical across all 9 scans — pure template |

### Category 2: LLM required but could be more structured (5 operations)

These need LLM judgment but could be constrained with enums, templates, and controlled vocabularies:

| Operation | Current method | How to structure it |
|-----------|---------------|-------------------|
| Threat model (F13) | LLM enumerates attack paths | Provide path enum (phishing, stale_token, session_compromise, malicious_extension, sloppy_review, runner_compromise). LLM selects applicable paths + adds one contextual sentence per path |
| Action steps (S01) | LLM writes commands + prose | Action type enum (install_normally, pin_version, set_config, nudge_maintainer, upgrade_required, do_not_install) + command templates. LLM fills in repo-specific values + prose wrapper |
| Timeline events (S04) | LLM selects events + labels | Events are factual (dates from API). Labels from controlled vocabulary (VULN_REPORTED, FIX_SHIPS, etc.). LLM selects which events to include |
| Capability assessment | LLM assesses worst-case | Capability enum (arbitrary_code_exec, file_exfil, network_access, credential_access, prompt_injection_channel, none). LLM selects + adds contextual sentence |
| Catalog metadata | LLM picks category | Category/subcategory from controlled list. Short description is LLM prose but constrained to 2-3 sentences |

### Category 3: Genuinely requires LLM creative prose (4 operations)

These resist structuring because their value IS the contextual framing:

| Operation | Why it needs LLM |
|-----------|-----------------|
| "What this means for you" | Contextual risk framing for a non-technical reader. Must address the specific user's situation based on the repo's shape, blast radius, and governance signals |
| "What this does NOT mean" | Editorial guardrails preventing over-reaction. Must reference specific positive signals that counterbalance the finding |
| Finding card body paragraphs | Narrative synthesis connecting evidence to conclusions with citations. Structure is templated but prose is editorial |
| One-line editorial caption | H1 hero summary. Creative synthesis of the entire scan into one sentence |

## Proposed architectural change

Based on these findings, the pipeline should change from:

```
CURRENT:
  LLM runs tools → LLM synthesizes everything → LLM writes MD → LLM writes HTML
  (fragile: LLM can skip steps, misapply rules, drift from calibration)

PROPOSED:
  Phase 1-2: LLM runs tools → raw outputs captured VERBATIM into investigation form
  Phase 3:   Python computes 11 automatable fields (severity, verdict, scorecard, etc.)
  Phase 4:   LLM fills 5 structured fields (threat model from enum, action steps from template, etc.)
  Phase 5:   LLM writes 4 prose fields ("what this means", "what this does NOT mean", body, caption)
  Phase 6:   Complete JSON assembled (facts + computed + structured + prose)
  Phase 7:   Python renderer → MD + HTML (mechanical, deterministic)
  Phase 8:   Validator checks: form completeness, evidence linkage, provenance tagging
  Phase 9:   Git hook spot-checks: re-runs 3-5 tool commands, verifies outputs match
```

### What this means for repeatability:

| Layer | Same repo, same SHA → | What varies |
|-------|----------------------|-------------|
| Raw tool output | IDENTICAL | Nothing (deterministic) |
| Computed fields (11 ops) | IDENTICAL | Nothing (deterministic) |
| Structured LLM fields (5 ops) | CONVERGES | Specific phrasing within templates |
| Prose LLM fields (4 ops) | VARIES | Creative framing (content is grounded) |
| Rendered MD + HTML | IDENTICAL from same JSON | Nothing (deterministic renderer) |

### What this means for the JSON schema:

The schema is NOT just a "container for LLM opinions." It is:
- **~54 fields** of verifiable tool output (FACTS)
- **~11 fields** of mechanically computed values (DETERMINISTIC)
- **~5 fields** of LLM-constrained structured data (CONVERGES)
- **~4 fields** of LLM prose (VARIES)

The vast majority of the schema is deterministic or verifiable. Only 4 fields genuinely vary across runs.

## Questions for the board

1. **Do you agree with the 11/5/4 classification?** Are there operations we classified as automatable that actually require LLM judgment? Vice versa?

2. **Should we automate the 11 mechanical operations in V1.0?** Or keep LLM-in-the-loop for V1.0 and automate in V2.0? (Automating means writing Python decision trees that replace prompt rules.)

3. **For the 5 structured operations, are the proposed enums/templates sufficient?** Should threat model paths be a closed enum or extensible? Should action steps use a fixed template set or allow LLM variation?

4. **For the 4 prose operations, should the schema provide sentence templates?** e.g., "When you install {repo}, you are trusting {trust_surface} because {governance_gap}." Or leave it fully LLM-authored?

5. **Does the proposed 9-phase pipeline make sense?** Are there phases missing? Is the ordering correct?

6. **Git hook spot-checks:** Which 3-5 commands should the hook re-run to verify? Suggestions: HEAD SHA check, branch protection API call, OSSF Scorecard score, star count, one random evidence item.

7. **Investigation form design:** Should it be JSON or YAML? Should the LLM fill it incrementally (one section at a time) or all at once? Should there be a "scan sign-off" field that only management can set?

## Files to read

1. **This brief** — process, synthesis, proposed architecture
2. `/tmp/board-package-v2/data-lineage-map.md` — the raw 1140-line data lineage map (118 data points)
3. `/root/tinkering/stop-git-std/github-scan-package-V2/repo-deep-dive-prompt.md` — the V2.4 prompt (what the LLM currently follows)

## Verdict options

- **APPROVE** — the 11/5/4 classification is correct, proceed with proposed pipeline
- **APPROVE WITH CONDITIONS** — classification needs adjustments (specify which)
- **REWORK** — fundamental issues with the analysis or proposed architecture
