# Systems Thinker — Pipeline R2 (Consolidation)

## Disputed operations (with prompt quotes): table D1-D5

| ID | Operation | Exact prompt rule | Vote | Reason |
|---|---|---|---|---|
| D1 | General vuln severity (not C20/F9/F15) | "Tiered by default severity (adjust based on context):" and `Tier 2 — Warning unless mitigated:` and `Tier 3 — Info unless compounding:` | STRUCTURED LLM | The prompt explicitly leaves room for contextual mitigation and compounding judgment. That is not a closed decision tree as written. |
| D2 | Split-axis decision (F4) | `Emit a split verdict whenever a single headline would mean opposite things to two distinct reader groups.` and `If both axes apply (rare), pick the axis whose decision is most consequential for the reader` | STRUCTURED LLM | "Opposite things" and "most consequential" are semantic audience-judgment tests. The output can be structured, but the trigger and axis choice are not fully mechanical in the prompt. |
| D3 | Priority evidence selection | `Priority evidence is strictly the evidence whose falsification would change the top-line verdict.` and `Before marking an item priority, articulate this sentence to yourself: "If this claim were false, the verdict would change from X to Y."` | STRUCTURED LLM | This is explicit counterfactual reasoning over the evidence-to-verdict chain. It is auditable and constrainable, but not deterministic code from the prompt alone. |
| D4 | Exhibit grouping | `When a section has 7+ similar-severity items, roll into themed exhibit panels (vuln/govern/signals)` and `More than 3 means your cut is too fine.` | STRUCTURED LLM | The `7+` threshold is mechanical, but `similar-severity` and assignment into `vuln/govern/signals` still require semantic grouping rules the prompt does not formalize. |
| D5 | Silent vs unadvertised (F5) | `Do NOT use the word "silent" if the release title or changelog entry references the fixed attack class.` and `"Silent security fix" — only when release notes omit or mislabel the fix` | STRUCTURED LLM | The output label is binary, but `references the fixed attack class` and `mislabel` require semantic text interpretation. That can be tightly structured, but the prompt does not reduce it to keyword logic. |

## Deferred items votes: table PD1-7, SD1-10, RD1-5

| ID | Vote | Rationale |
|---|---|---|
| PD1 | PROMOTE TO FIX NOW | Reference-scan version drift contaminates the methodology baseline and weakens board-review repeatability. |
| PD2 | PROMOTE TO FIX NOW | Once rendering is deterministic, MD and HTML parity becomes a core integrity check, not a nice-to-have. |
| PD3 | PROMOTE TO FIX NOW | Citation and bundle integrity are part of the scanner's trust model. This is foundational. |
| PD4 | AGREE DEFER | Useful, but lower leverage once validator and deterministic rendering are in place. |
| PD5 | PROMOTE TO FIX NOW | The proposed Python decision layers need tests before promotion into the pipeline. |
| PD6 | AGREE DEFER | Documentation/examples do not block architecture hardening. |
| PD7 | AGREE DEFER | Packaging quality issue, not a pipeline correctness blocker. |
| SD1 | PROMOTE TO FIX NOW | Monorepo/multi-shape repos are already in scope; without `components[]`, lineage and verdict scope will stay lossy. |
| SD2 | PROMOTE TO FIX NOW | `kind` and `domain` are structural coordinates needed for deterministic grouping, filtering, and future automation. |
| SD3 | AGREE DEFER | Confidence is useful, but provenance and evidence linkage are higher priority than score inflation metadata. |
| SD4 | AGREE DEFER | Judgment fingerprinting is governance garnish until the synthesis model stabilizes. |
| SD5 | PROMOTE TO FIX NOW | A plausibility-warning layer is the right place to catch near-misses without turning them into hard failures. |
| SD6 | PROMOTE TO FIX NOW | Per-field source tags are the schema-level equivalent of evidence traceability. They should not wait. |
| SD7 | AGREE DEFER | The prompt is still calibrated around a fixed scorecard shape; schema flexibility can follow later. |
| SD8 | AGREE DEFER | Generic artifact abstraction is useful, but current pipeline can ship with explicit artifact types first. |
| SD9 | AGREE DEFER | Generic permissions abstraction is premature until more repo shapes force it. |
| SD10 | AGREE DEFER | SBOM integration is valuable but not required to stabilize the current prompt-governed pipeline. |
| RD1 | AGREE DEFER | V2.0 automation of structured-LLM operations should wait until V1.0 facts/computation layers are proven. |
| RD2 | PROMOTE TO FIX NOW | Promotion from prompt logic to code should be gated by a multi-repo corpus, not two exemplars. |
| RD3 | PROMOTE TO FIX NOW | Add fallback only with explicit logging and provenance; otherwise deterministic-phase failures become hard stops. |
| RD4 | PROMOTE TO FIX NOW | An `assumptions` field materially improves auditability for the structured-LLM layer. |
| RD5 | AGREE DEFER | Management sign-off is workflow governance, not scanner data model. Keep it outside the scan artifact for now. |

## Prompt coverage gaps

1. **Status chips are not modeled as a first-class structured output.** The prompt requires: `.status-chip.resolved` / `.active` / `.ongoing` / `.mitigated` / `.informational`, but the lineage map only embeds status inside finding-card prose structure.

2. **Per-finding action hints are under-specified in the lineage map.** The prompt makes S8-5 mandatory and concretely instructive, but the pipeline summary only models Section 01 action steps, not finding-level action hints.

3. **Split-verdict formatting obligations are only partially captured.** The lineage map captures `split_axis`, but not the required scope prefix (`Version ·` / `Deployment ·`) or the rule that Section 01 must split by audience when F4 fires.

4. **Section-level action blocks are missing.** The prompt requires `.section-action` on every collapsible section except purely informational ones; the lineage map does not model this output obligation.

5. **Unknown-state escalation is not surfaced strongly enough.** The prompt states `Unknown — call out explicitly; default treatment = Tier 1 until proven otherwise.` That defaulting rule is materially important and should be explicit in the schema/pipeline rules, not left implicit in prose.

## Final classification: 6 / 10 / 4

- **Automatable (6):** verdict determination; scorecard cells; solo-maintainer flag; boundary-case detection; coverage cell status; methodology boilerplate.
- **Structured LLM (10):** general severity outside hard tables; threat model; action steps; timeline; capability assessment; catalog metadata; split-axis decision; priority evidence selection; exhibit grouping; silent-vs-unadvertised classification.
- **Prose (4):** what this means for you; what this does NOT mean; finding card body prose; one-line editorial caption.

## Final pipeline design

1. **Phase 0 — Pre-flight gate.** Validate repo access, tool availability, rate-limit headroom, output skeleton, and prompt/schema version pairing.
2. **Phase 1 — Raw capture.** Run commands in prompt order and record verbatim outputs plus failures/unknowns into an investigation JSON.
3. **Phase 2 — Raw-data validation.** Sanity-check internal consistency, required fields, command/result coverage, and source tagging.
4. **Phase 3 — Deterministic compute.** Compute the 6 fully automatable outputs only.
5. **Phase 4 — Structured LLM fill.** Populate the 10 constrained judgment fields using enums, templates, and required rationale slots.
6. **Phase 5 — Prose LLM fill.** Generate the 4 editorial fields after structured outputs are frozen.
7. **Phase 6 — Assembly gate.** Build the complete JSON artifact with facts, computed values, structured judgments, prose, provenance, assumptions, and evidence refs.
8. **Phase 7 — Validation gate.** Run schema validation, citation/bundle validation, MD↔HTML parity checks, and prompt-specific structural checks.
9. **Phase 8 — Spot-check gate.** Re-run a small set of high-signal commands, including one priority-evidence claim.
10. **Phase 9 — Deterministic rendering.** Render MD and HTML from the validated JSON only.

**Form format:** JSON, section-by-section fill, with `_meta.phases_completed`, per-field source tags, explicit `unknown` states, and an `assumptions[]` field. No management sign-off field inside the scan artifact.

## Final verdict and conditions

**Verdict: APPROVE WITH CONDITIONS**

The core architectural move is correct: separate verbatim facts, deterministic computation, structured judgment, and editorial prose. But the original `11/5/4` overstates what the prompt has actually formalized. On the literal V2.4 rules, the right consolidation is **6/10/4**, not `11/5/4`.

**Conditions before implementation:**

1. Reclassify D1-D5 as above and update all summary tables to match `6/10/4`.
2. Promote the validator/test/citation items marked FIX NOW, especially PD2, PD3, PD5, SD1, SD2, SD5, SD6, RD2, and RD4.
3. Add structured fields for status chips, finding-level action hints, split-verdict audience metadata, explicit unknown states, and assumptions.
4. Treat RD3 fallback as auditable degraded mode only: if deterministic computation fails, log the failure, tag the field as fallback-generated, and block silent substitution.
5. Do not promote any structured-LLM field into deterministic code until corpus testing shows stable agreement across materially different repo shapes.
