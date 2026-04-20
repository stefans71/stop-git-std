# Schema V1.2 R1 — Skeptic

## Votes (one per question)
- Q1: **coordinated** — D-7 and D-8 are intrinsically coupled; splitting creates two migration pains and risks schema drift between them.
- Q2: **D7-A1** — compute.py must remain visible as advisory with signal refs; otherwise "override-explained" is just "say something and move on" theater.
- Q3: **D8-B3** — Neither harness nor V1.1 naming is optimal; adopt clean third shape that drops `is_` prefix but keeps `_ref` suffix for clarity.
- Q4: **migration-script** — Clean cut with one-time migration script preserves forward simplicity while enabling V1.1 fixture regeneration.
- Q5: **D7-G4** — Automated gate requiring non-empty rationale ≥ N chars + computed_signal_refs non-empty; free-text alone invites LLM word salad.
- Q6: **no (deferred to V1.3+)** — V1.2 scope should be schema + harness integration only; renderer enhancements are separate complexity.
- Q7: **explicit OUT-of-scope list (agree)** — SD2, PD3, Package V2.5 refresh, Scanner-Integrity section 00, Schema-hardening watchpoint must stay out.

## Rationale (prose)

The fundamental assumption wrong in this brief is that "override-explained" with D7-G1 (free-text rationale) provides meaningful accountability. It doesn't. Without D7-G2+ structural constraints, Phase 4 LLM can write plausible-sounding nonsense that cites nothing, and gate 6.3 becomes a rubber stamp. The zustand Q4 example in the brief shows the danger: V2.4 LLM softened red → amber because of CONTRIBUTING.md and non-vuln PR responsiveness. If compute.py can't observe those signals, how can Phase 4 LLM cite them? It can't—it will invent post-hoc justifications unless forced to reference concrete computed_signal_refs.

The 11-scan comparator analysis needs something V1.2 as designed cannot extract: **semantic drift detection**. V1.2 focuses on threshold calibration (formal<10% → red) but misses when LLM overrides for qualitative reasons outside the rubric (e.g., "this repo has a vibrant community despite low formal review"). The comparator needs a field like `override_category: "threshold" | "qualitative_context" | "rubric_interpretation"` to distinguish calibration fixes from judgment calls.

What scan shape would embarrass V1.2? A **monorepo with mixed governance models**—some subdirectories have branch protection, others don't; some have CODEOWNERS, others don't. The harness flattens these to repo-level booleans, losing the nuance. Phase 4 LLM reading the raw data might spot the pattern, but V1.2's `has_branch_protection: bool` can't capture it, and the LLM has no structured way to express "partial branch protection in critical subpaths."

The dangerous_primitives flattening (per-family → flat hits[]) is a **data loss we'll regret**. The sidecar preserves `exec.files[].first_match.snippet` but the schema discards it. When a security analyst wants to know "what kind of exec calls?" (subprocess.run vs os.system vs eval), they need the family context. The flattening also loses hit distribution across families—3 exec hits vs 1 exec + 1 network + 1 deserialization tells different stories about codebase risk profile.

D-8's field naming debate misses the deeper issue: **type coercion losses**. `symlinks_stripped: int → bool` loses count data that matters for tarball integrity assessment. `distribution_channels_verified: "4/5" → bool` loses granularity—which channel failed? These aren't just naming differences; they're semantic compression that future analyses will need to reverse-engineer from sidecars.

## FIX NOW items (if any)
- **C-1:** Dangerous_primitives flattening must preserve family context in V1.2 schema. Keep per-family structure with hit_count + files[].
- **C-2:** Add `override_category` enum to scorecard_cell schema to enable semantic drift analysis in 11-scan comparator.
- **C-3:** Type coercion fields (symlinks_stripped, distribution_channels_verified) must preserve original granularity or add companion fields.

## DEFER items (if any)
- **D-1:** Renderer partial updates for new fields (e.g., self_merge_count display) — defer to V1.3 to keep V1.2 focused on schema/harness integration.
- **D-2:** Full Scanner-Integrity section 00 hit-level structure — has its own scope trigger (Codex R2 defer-ledger).

## INFO items (if any)
- **I-1:** The transformer's `agent_rule_files.total_bytes` heuristic (line_count × 50) is fragile; V1.2 schema should accept raw line_count and let renderer compute bytes if needed.
- **I-2:** `ossf_scorecard.http_status` dropped by transformer but useful for diagnosing API failures; V1.2 should preserve it.
- **I-3:** `dependencies.dependabot_config` contains schedule/open-pr-limit data valuable for automation assessment; dropping it loses insight.

## Open questions the brief missed
- How does V1.2 handle **partial Phase 1 failures**? If gitleaks times out but OSSF succeeds, does schema validation fail or accept null/partial structures?
- What's the **migration story for catalog entries 1-11** (V2.4 scans without forms)? Will they stay V2.4-only or get back-authored V1.2 forms?
- Does **Phase 4 LLM get access to the sidecar** (phase-1-raw-full.json) for richer context, or only the schema-valid subset?

## Blind spots
My perspective is weakest on the **renderer template complexity** of adopting per-family dangerous_primitives. I'm advocating for richer schema but haven't examined the 14 Jinja2 partials to see if they can gracefully handle nested structures. The pragmatic trade-off might favor flattening for renderer simplicity, but that's data loss we should acknowledge upfront.

Also, I'm skeptical of "advisory" compute.py (D7-A1) but haven't considered the **prompt engineering burden** of teaching Phase 4 LLM to reference computed_signal_refs. If the LLM consistently ignores them, the structure is decorative. We need evidence from Step G Phase 4 runs on whether LLMs naturally cite evidence IDs when available.