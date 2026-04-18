# Form Review — Pragmatist

## Verdict: NEEDS FIXES

The form covers ~90% of the prompt's investigation steps and ~95% of the 118 lineage-map data points. But there are real gaps that would cause data loss during scans.

## Gaps found (prompt requirements missing from form)

1. **Open PRs (prompt line ~356).** `gh pr list --state open` — no field in the form. Only merged PRs captured in `pr_review`.
2. **Closed-not-merged PRs (prompt line ~359).** `gh pr list --state closed` (rejected PRs) — no field. The prompt uses these to detect "rejected community security fixes."
3. **Closed issues (prompt line ~460).** `gh issue list --state closed` — no field. Only `open_security_issues` exists.
4. **Open issue count (prompt line ~459).** The form has `open_security_issues` (filtered) but no general `open_issues` array/count.
5. **Monorepo inner-package enumeration (prompt line ~237-250, C11).** No field for `monorepo.is_monorepo`, `inner_package_count`, or `lifecycle_script_hits`. The prompt makes this a mandatory Coverage entry.
6. **Workflow file contents (prompt line ~218-220, DP-020).** No field for storing actual workflow YAML content or per-workflow analysis (permissions blocks, pull_request_target, SHA-pinning). The form captures `workflows[].entries` (listing) but not content or derived analysis.
7. **SHA-pinning audit results (prompt line ~252-256, DP-021/F15).** No structured field for action pinning breakdown (sha_pinned count, version_tagged, unpinned, per-action details).
8. **Batch-merge detection (prompt Step 5c, DP-035).** No field for PRs sharing identical mergedAt timestamps.
9. **Install-script fetch targets and pinning check (prompt line ~528-553, DP-040/041).** No field for install script fetch URLs, their refs, or the pinning verdict.
10. **Release asset / artifact verification results (prompt line ~536-546, DP-043).** No field for per-channel verification method and result.
11. **Defensive configs (DP-053).** No field for things like `minimumReleaseAge` discovered during scanning.
12. **Section 00 Scanner Integrity (prompt line ~1466-1489).** Conditional section when prompt-injection hits are actionable — no field to drive this.
13. **F12 two-layer inventory format.** `executable_inventory` captures the 7-property cards but not the one-line summary layer or per-file SHA / line ranges / diff anchors (prompt line ~1009-1018).

## Coverage of 16 prior gaps

**Covered (10 of 16):**
- Pragmatist G1 (DP-026 classification): Covered — `dangerous_primitives.drill_ins` captures this via `code_patterns`
- Pragmatist G3 (scorecard consistency re-check): Covered — `phase_3_computed.scorecard_cells` has the inputs; consistency enforcement is implicit in phase_3
- Pragmatist G4 (C15 config-defaults path matching): Covered — `pr_review.security_relevant_prs` captures the union
- Pragmatist G5 (HTML-escaping): Rendering concern, not a form field — correctly out of scope
- Skeptic G4 (W2 rate-limit budget): Covered — `pre_flight.api_rate_limit`
- Skeptic G5 (F16 Windows patterns): Covered — `windows_patterns` field exists
- Skeptic G6 (C19 design principle): Rendering concern — correctly out of scope
- Skeptic G1 (S8-1 utility classes): Rendering concern — correctly out of scope
- Skeptic G2 (S8-8 rem-only fonts): Rendering concern — correctly out of scope
- Skeptic G3 (S8-12 validator gate): Covered — `phase_2_validation` + `phase_6_assembly`

**NOT covered (6 of 16):**
- Pragmatist G2 (F12 two-layer format): One-line summary layer has no field. See gap #13 above.
- Systems Thinker G1 (status chips as structured output): `finding_template` has `status` but it's a single string, not an array of chips. Prompt allows multiple chips per finding (e.g., "code resolved + disclosure gap ongoing").
- Systems Thinker G2 (per-finding action hints): `finding_template` has `action_hint` — covered. BUT the "concreteness requirement" (prompt line ~933-936) is not enforceable from the schema.
- Systems Thinker G3 (split-verdict formatting): `split_axis_decision` exists but missing the `scope_prefix` field (`Version ·` / `Deployment ·`) and no link to Section 01 audience splitting.
- Systems Thinker G4 (section-level action blocks): No field. The prompt requires `**Your action:**` blocks on every flagged section. This is a per-section output, not per-finding.
- Systems Thinker G5 (unknown-state escalation): No field to flag unknown auto-load tier with default-to-Tier-1 treatment.

## Structural issues

1. **`finding_template._example` sits inside the output JSON.** Templates/schemas should be external. Including it in every scan form wastes tokens and risks the LLM confusing the example with real data.
2. **`phase_3_computed.verdict` says "computed AFTER phase_4 findings are finalized"** — but it's in phase_3. This creates a circular dependency: phase_3 needs phase_4 output. Either move verdict to phase_4 or add a phase_3b post-pass.
3. **No `assumptions` field.** The Pragmatist R2 review noted this as useful documentation (RD4). When commands 403 or tools are unavailable, the LLM makes assumptions that should be recorded explicitly.
4. **`phase_4_structured_llm.general_vuln_severity` is underspecified.** The `assessments` array has no template showing per-assessment structure (which vulnerability, which tier, what mitigation context).

## Recommendations

1. Add fields for open PRs, closed-not-merged PRs, closed issues, and general open issue data in `phase_1_raw_capture`.
2. Add `monorepo`, `workflow_contents`, `sha_pinning_audit`, `batch_merges`, `install_script_pinning`, `artifact_verification`, and `defensive_configs` sections to `phase_1_raw_capture`.
3. Add `section_actions[]` and `status_chips` (as array, not single string) to `phase_4_structured_llm`.
4. Move `finding_template` out of the form JSON into a separate schema file.
5. Resolve the verdict phase ordering: either move it to a `phase_4b` or document the two-pass approach.
6. Add an `assumptions[]` array to `_meta` or `phase_1_raw_capture`.
