# SF1 R1 — Skeptic (DeepSeek V4)

## Vote

Preferred resolution: **C — Schema split V1.1 → V1.2**

## Rationale

All three options are fundamentally flawed because they're solving the wrong problem. The core issue isn't calibration drift—it's that we're trying to automate something that's inherently judgmental. Option A makes compute.py a rubber stamp for past LLM whims, Option B rewrites history to fit a flawed algorithm, and Option C at least acknowledges the truth: scorecard cells are qualitative judgments, not deterministic computations. But even Option C doesn't go far enough—it just moves the problem to a different phase without fixing the underlying design flaw.

## Resolution details

**Option C with a critical modification:** Don't just move scorecard cells to phase_4_structured_llm—eliminate the pretense of deterministic scoring entirely. Replace the 4-cell scorecard with a structured judgment system where the LLM must:
1. For each question, select a color (red/amber/green)
2. Provide a 1-2 sentence rationale citing specific evidence
3. Flag any "edge case" where the evidence conflicts with simple thresholds
4. Optionally suggest threshold adjustments for future calibration

The schema change should look like:
```json
"phase_4_structured_llm": {
  "scorecard_judgments": [
    {
      "question": "Does anyone check the code?",
      "color": "amber",
      "rationale": "65% any-review but no branch protection",
      "edge_case": true,
      "suggested_threshold_adjustment": "Consider lowering formal-review requirement when any-review > 60%"
    }
  ]
}
```

Compute.py should still calculate its "suggested" colors based on current thresholds, but these become advisory inputs to the LLM, not binding outputs.

## FIX NOW items

1. **Schema versioning trap** — Moving to V1.2 creates immediate incompatibility with all existing fixtures. Need a migration path that doesn't break Step G entirely.
2. **LLM judgment consistency** — Without deterministic thresholds, we lose comparability across scans. Need to define what "structured constraints" actually means.
3. **Render pipeline dependency** — Both render-md.py and render-html.py assume phase_3_computed.scorecard_cells exists. This is a breaking change.

## DEFER items

1. **Threshold refinement** — The actual calibration improvements (like distinguishing install-surface from governance) should happen regardless of where authority lives.
2. **Catalog harmonization** — If we keep V2.4 as canonical for now, we need a plan for eventual reconciliation.
3. **Validation gate redesign** — Gate 6.3 needs rethinking if cells become LLM judgments.

## INFO items

**What nobody is saying:** The real problem is that we have 11 "canonical" scans that were authored by an LLM following a prompt that the same LLM apparently ignored in 5 out of 12 cells across 3 targets. That's a 42% disobedience rate on the very rubric we're trying to codify. This suggests either:
1. The rubric is fundamentally flawed/unworkable
2. The LLM is incapable of following it consistently
3. The "canonical" scans aren't actually canonical

**Premise that might be wrong:** That V2.4 scans represent "ground truth." They're LLM outputs, not human-reviewed gold standards. Treating them as canonical creates a circular reference problem.

**Hidden assumption:** That scorecard cells need to be comparable across repos. If they're qualitative judgments, maybe they shouldn't be—maybe each repo gets a bespoke assessment.

## Blind spots

1. **I might be over-indexing on the "judgment vs computation" dichotomy.** Maybe with better thresholds, compute.py could capture the nuance.
2. **I'm assuming schema changes are acceptable.** The project owner might have strong constraints against breaking changes.
3. **I haven't considered the operational cost** of making every scan dependent on LLM judgment quality—this could make the tool less reliable, not more.
4. **The "skeptic" lens might be making me too cynical** about the possibility of finding a workable technical solution.
5. **I'm not accounting for the possibility** that the mismatches are actually bugs in compute.py's implementation of the rubric, not philosophical differences.