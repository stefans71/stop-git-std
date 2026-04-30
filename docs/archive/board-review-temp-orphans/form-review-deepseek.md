# Form Review — Skeptic
## Verdict: NEEDS FIXES
## Gaps found (prompt requirements missing from form)

### Critical Gaps (Prompt Step → Missing Form Field)

1. **Step 2.5 / F9 Agent-rule file auto-load tier classification** — No field for auto-load tier (Always auto-loaded / Conditionally auto-loaded / User-activated only / Unknown). Required for every agent-rule file finding.

2. **Step 7.5 / F10 README paste-block inventory schema** — No dedicated structure for paste-block evidence. Missing fields:
   - Block location (README.md + line number)
   - Block content (verbatim fenced code block)
   - Scope persistence (where snippet ends up)
   - Instruction verbs enumerated
   - Secret/command/file requests
   - Model-obedience changes
   - Auto-load behavior

3. **Step 8 / F1 Distribution channel verification** — `phase_1_raw_capture.distribution_channels.channels` exists but lacks:
   - Channel type classification (marketplace, npm, PyPI, curl-pipe, git clone)
   - Pinned? (boolean)
   - Verified vs source? (boolean/status)
   - Install-script pinning check results (F2)

4. **Step 5 / F3 Changelog-hiding detection** — No field to track PRs that are in `$PATH_HITS` but NOT in `$TITLE_HITS` (title-innocuous path-critical pattern).

5. **Step 2 / F15 Actions-pinning check tiers** — No structured output for tiered categorization:
   - OK (40-char SHA)
   - Info (actions/ org with major-version tag)
   - Warning (third-party action with tag/branch)
   - Critical (third-party action with @main/@master)

6. **Step 4 / F11 Dual review-rate metric** — Form has `phase_1_raw_capture.pr_review.formal_review_rate` and `any_review_rate` but no field for solo-maintainer contextualization sentence (>80% commits).

7. **Step 5 / W2 Rate-limit budget check** — No field to record API budget remaining at Step 5 and whether PR sample was reduced.

8. **Step C / F16 Windows-specific patterns** — Form has `windows_patterns` but lacks parity coverage flag: "Windows surface coverage (F16)" boolean to indicate if .ps1/.bat/.cmd files were inspected with same rigor as Linux scripts.

9. **Step A-pre / Cap-4 gitleaks availability** — Form tracks if gitleaks ran but no field for "gitleaks not available" explanatory note.

10. **Step 2 / C11 pull_request_target usage** — Form has workflow entries but no explicit `pull_request_target` count field required by prompt.

### Structural Issues

1. **Phase separation unclear for computed vs LLM fields** — Some prompt requirements blend computation and LLM judgment:
   - C20 severity formula (Python-computed) but threat model text (LLM)
   - Scorecard cells (Python-computed inputs) but short_answer (LLM)
   - Solo-maintainer detection (Python-computed) but verbatim_sentence (LLM)

2. **Evidence provenance tracking** — Form has `evidence_refs` in findings but no centralized evidence registry mapping refs to raw command outputs.

3. **Coverage section requirements** — Prompt mandates specific coverage statements (F8 prompt-injection scan, distribution channels verified, Windows surface coverage) but form's `phase_1_raw_capture` lacks structured slots for these affirmative results.

4. **Catalog metadata** — Prompt requires catalog fields (Category, Subcategory, Short description, Target user, Shape) but form's `phase_4_structured_llm.catalog_metadata` has different field names and doesn't include all required fields.

5. **Timeline events** — `phase_4_structured_llm.timeline_events` exists but no field for `.tl-severity-label` (VULN REPORTED, 5-DAY LAG, etc.) required by S8-9.

### Recommendations

1. **Add missing structured fields**:
   - `phase_1_raw_capture.agent_rule_files[]` → add `auto_load_tier` enum
   - `phase_1_raw_capture.readme_paste_blocks[]` → expand with F10 schema fields
   - `phase_1_raw_capture.distribution_channels.channels[]` → add `type`, `pinned`, `verified`, `install_script_pinning_check`
   - `phase_1_raw_capture.pr_review` → add `changelog_hiding_prs[]`, `solo_maintainer_sentence`
   - `phase_1_raw_capture.workflows` → add `pull_request_target_count`, `actions_pinning_tiers`
   - `phase_1_raw_capture.api_budget` → add `remaining_at_step_5`, `pr_sample_reduced`

2. **Clarify phase boundaries**:
   - Document which fields are Python-computed vs LLM-filled
   - Add `source_type` annotations to all fields (raw/computed/structured_llm/prose_llm)

3. **Enhance evidence tracking**:
   - Add `phase_1_raw_capture.evidence_registry` mapping refs to command+output pairs
   - Include classification (Confirmed fact / Inference) per evidence item

4. **Align with prompt coverage requirements**:
   - Add `phase_1_raw_capture.coverage_affirmations` with boolean flags for:
     - `prompt_injection_scan_completed`
     - `windows_surface_coverage_parity`
     - `distribution_channels_verified`
     - `gitleaks_available`

5. **Update catalog metadata**:
   - Align `phase_4_structured_llm.catalog_metadata` fields with prompt requirements
   - Add missing: `short_description`, `target_user`, `shape`

6. **Add timeline severity labels**:
   - Extend `phase_4_structured_llm.timeline_events.entries[]` with `severity_label` field

**Priority**: Fix critical gaps 1-3 (agent-rule tiers, paste-block schema, distribution verification) before V2.4 deployment. These are hard requirements from prompt that have no corresponding form fields.