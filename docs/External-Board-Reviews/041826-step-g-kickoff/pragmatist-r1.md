# Pragmatist (Sonnet 4.6) — R1 Step G Kickoff / U-1

**Date:** 2026-04-18
**Verdict:** SIGN OFF WITH DISSENTS

---

## Verdict rationale

The owner's additive approach is the correct call. Flipping Path B to primary before a single live scan has cleared the JSON-first pipeline would be a documentation bet against an unvalidated system. Proposed draft changes are directionally sound. Three dissents follow, two of which are FIX NOW.

---

## Q1: Is "additive" the right strategy?

Yes. Unifying on Path B before Step G completes would create exactly the wrong pressure: it would make Step G a documentation rollback exercise rather than a validation exercise. Additive preserves the proven V2.4 path for production scans while putting Path B in a clearly fenced lane.

One practical sharpening: CLAUDE.md already uses "Path A" and "Path B" for two entirely different concepts (run-yourself vs. delegate). Introducing "Path V2.4" and "Path V2.5-preview" alongside "Path A/Path B" creates a name collision that will confuse both human operators and LLMs reading CLAUDE.md. Suggest "Rendering Mode V2.4" / "Rendering Mode V2.5-preview" or "Workflow V2.4" / "Workflow V2.5-preview" so "Path" stays for delegation.

---

## Q2: Prompt update scope

Confirm owner's minimal-touch proposal: one cross-reference sentence at the top of the output-format section (lines ~1106), nothing else. Zero-change is defensible but slightly worse — the prompt's output-format section is the contract that both paths implement. One sentence pointing to `docs/scan-schema.json` and `render-md.py` costs nothing and makes the contract visible. Do not rewrite the output-format section.

---

## Q3: Existing catalog scans

Confirm owner proposal. Leave the 10 completed scans alone. Add a metadata column or footnote to `docs/scanner-catalog.md` distinguishing "V2.4-pipeline" from "V2.5-preview-pipeline" entries. Step G's first live scan becomes immediately distinguishable in the catalog without touching anything else.

---

## Q4: Package drift

**Q4.1 — Operator guide parity:** Accept drift as the V2.4-to-V2.5 boundary marker.

**Q4.2 — Validator sync (FX-3b): DISSENT — FIX NOW, NOT in U-1 but in a parallel commit before the U-1 commit lands.** FX-3b is a latent bug in V2.4 that eats shell-glob-containing evidence. Caveman-shape scans specifically use curl-pipe-from-main patterns that FX-3b would corrupt. This isn't theoretical — it's demonstrated. Leaving the package validator with this bug is fine if it goes into the commit queue NOW, not indefinitely deferred.

**Q4.3 — Full package refresh:** Confirm as future work post-Step G. Not U-1 scope.

---

## Q5: Safety concern — Path B documented pre-validation

Disclaimer wording is sufficient for this project's operator profile (LLMs and technically fluent humans). A flag/env-var would add friction to Step G itself — the one workflow you want to run.

One improvement: §8.8 says "Use this path only if you are Step G's operator." Rewrite as: "Use this path only when explicitly running Step G of the renderer validation plan." Clearer, applies equally to delegated agents.

---

## Q6: Rollback plan if Step G fails

Confirm owner proposal. Path A continues working throughout any Step G failure. Schema revision to V1.2 + fixture re-authoring + §8.8 doc update are the mechanical steps.

One addition: if Step G produces validator-clean output that's structurally worse than a V2.4 scan on the same repo, the rollback criterion needs explicit statement. "Validator clean" is necessary but not sufficient. Add to §8.8: **Step G success requires rendered output reviewed against V2.4 scan of same repo for structural parity, not just validator cleanliness.**

---

## Q7: Blind spots in the proposed draft

**FIX NOW — operator can't produce form.json from scratch.** The proposed §8.8 says "author form.json conforming to docs/scan-schema.json V1.1" and points at fixture examples. But the investigation prompt describes what to check, not how to populate the 9-phase form structure. An operator running Step G faces a blank form.json with a 1508-line prompt and no bridge between them.

Minimum viable bridge: a mapping table in §8.8 that says:
- Phase 1 raw capture fields come from gh api calls per prompt Steps 1-4
- Phase 2 validation fields come from Steps 5-6
- Phase 3 computed fields are derived from Phases 1-2
- Phases 4-5 are LLM-authored structured/prose output

Not a rewrite of the prompt. One-table addition to §8.8. **FIX NOW before doc lands.**

**INFO — CSS line count mismatch.** CLAUDE.md currently says 816 lines; proposed draft says 824 (correct). Confirm 824 before committing.

**INFO — Path A/B name collision.** Flagged in Q1. Cheap fix: rename delegation question to "Mode A / Mode B" or "Option A / Option B" so "Path" is reserved for rendering.

**INFO — Scan-Readme.md line count drift.** Line 119 references SCANNER-OPERATOR-GUIDE.md as "552 lines"; after §8.8 addition it's wrong. Either drop the line count or update it.

---

## FIX NOW / DEFER / INFO summary

| Item | Priority | Action |
|---|---|---|
| Path A/B name collision with rendering names | **FIX NOW** | Rename delegation options in CLAUDE.md |
| form.json authoring bridge missing from §8.8 | **FIX NOW** | Add phase-to-prompt mapping table before committing |
| FX-3b package validator sync | **FIX NOW (parallel commit, not U-1)** | Add to post-U-1 queue; track explicitly |
| Step G success = structural parity, not just validator clean | **FIX NOW** | Add explicit note to §8.8 |
| CSS line count 816→824 in CLAUDE.md | INFO | Tidy fix during commit |
| Scan-Readme.md line-count annotation | INFO | Update when snippet authored |
| Full package refresh | DEFER | Post-Step G |
| Validator sync full pass (non-FX-3b) | DEFER | V2.5 package work |

---

**Bottom line:** Approach sound. Ship additive. Fix form.json authoring gap and Path A/B name collision before commit lands. Track FX-3b package sync as immediate follow-on, not indefinitely deferred.
