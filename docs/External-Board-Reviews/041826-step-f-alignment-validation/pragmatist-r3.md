# Pragmatist (Sonnet 4.6) — R3 Deliberation

**Date:** 2026-04-18
**Reviewing:** Owner-authored FX-1..FX-4 + U-1..U-9 unblocked items

---

## Verdict (R3)

**SIGN OFF** — upgrading from R2 "SIGN OFF WITH DISSENTS." All three dissents are resolved by the owner's fix artifacts. No blocking issues remain.

---

## Vote on Each Fix Artifact

**FX-1 — SECOND.** The two changes are right. The `'None &mdash; ...'` → `'None \u2014 ...'` swap avoids the double-escape bug Pragmatist flagged in R2 (autoescape would turn the `&` into `&amp;`). The `{{ prior | safe }}` → `{{ prior }}` removes the XSS gate bypass. The `{#` comment explains the invariant for the next maintainer. No adjustments.

**FX-2 — SECOND.** Pre-fix verification: 37 occurrences of `&#39;` in the rendered `<style>` block. The fix (`{{ css_content | safe }}`) is the only correct solution — you cannot serve CSS through an autoescaped Jinja block. The `{#` block comment resolves D-6 (CSS autoescape path documentation) in the same change. No adjustments.

**FX-3 — SECOND** (with one observation, not a blocker).

Ran the regex against the actual rendered zustand HTML:
- Pattern 3 returns `['F0', 'F1', 'F2', 'F3', 'F4', 'F5']` — all 6 finding cards
- Pattern 2 returns `[]` — Step F H3 format uses `&mdash;` between ID and title, not ID and severity; Pattern 2 was never matching
- Pattern 1 returns `['F0', 'F1']` — exhibit tags
- Union = all 6 findings

The owner's regex anchors on `<h3` + optional leading tags + first F-ID token + `(?:&mdash;|—|–|-)`. Does not false-positive on non-finding H3s (e.g. `<h3>Step 1: Install...</h3>`, `<h3><code>src/index.ts</code></h3>`) because none start with `F\d+`. Tight and correct.

One observation: exhibit-heading `No branch protection, no rulesets, no CODEOWNERS on main (F0 / C20)` has ID at end, not start. Pattern 3 does not match. Correct behavior — Pattern 1 covers exhibit-tag association.

No adjustments needed.

**FX-4 — SECOND** (with one schema note, already flagged by owner).

The four fields (`_fixture_provenance`, `_fixture_back_authored_from`, `_fixture_authored_by`, `_fixture_subset_scope`) are right. Confirmed `_meta` has `additionalProperties: false` at `docs/scan-schema.json` line 161. Schema update is load-bearing — if omitted, schema validation rejects the tagged fixtures. Must be same commit as fixture JSON changes.

No adjustments needed.

---

## Vote on Unblocked Items U-1 through U-9

**U-1 — APPLY IN NEXT COMMIT (before Step G).** Without documented pipeline steps calling `render-md.py` and `render-html.py`, Step G cannot run "live pipeline" end-to-end. Next commit should update CLAUDE.md and `docs/SCANNER-OPERATOR-GUIDE.md` to replace the old "copy CSS verbatim into template" instruction with the two render commands. Documentation only, low risk.

**U-2 — APPLY IN THIS COMMIT.** FX-3 verified correct. Bundling with FX-1/FX-2 is cleaner than a separate commit — one cohesive unit.

**U-3 — APPLY IN THIS COMMIT.** Fixture provenance is low effort and prevents corpus epistemic drift. Schema update required.

**U-4 — APPLY IN THIS COMMIT (already included in FX-2).** Comment wording approved.

**U-5 — DEFER, with Step G acceptance criterion.** Accepting owner's compromise framing. Reasoning against DeepSeek's FIX NOW position: PD3 validates `findings-bundle.md` citation discipline. No real `findings-bundle.md` has been produced through the JSON-first pipeline since Step F. Building a validator for an artifact that doesn't yet exist in the new pipeline is premature. The right trigger is when Step G produces a real bundle from a live scan. The compromise — list PD3 as a Step G acceptance criterion — satisfies DeepSeek's underlying concern without building on ungrounded assumptions now. **R3 resolves the 2-1 split: DEFER with mandated Step G gate.**

**U-6 — DEFER.** Once FX-1 applies, the only remaining `| safe` is FX-2's intentional `css_content`, documented by comment. Not load-bearing.

**U-7 — DEFER.** No new evidence since R2.

**U-8 — DEFER.** `unsafe-inline` for `adjustFont` acceptable tradeoff.

**U-9 — DEFER.** Phase 4/5 generator architecture decision.

---

## Prior-Roadmap Deferred Items

All 11 items: **CONFIRM DEFER.** No new evidence. Automation triggers (20+ corpus for RD1, V2.0+ for SD9/SD10/RD5/PD-cluster) not met.

---

## Post-Apply Verification Plan

**SECOND** the 8-step plan, with one addition:

After step 7 (schema update for FX-4), add:

> **7b.** Run `python3 docs/validate-scanner-report.py --schema tests/fixtures/caveman-form.json`, `--schema tests/fixtures/archon-subset-form.json`, and `--schema tests/fixtures/zustand-form.json` to confirm all three fixtures pass schema validation with the new `_fixture_*` fields. Catches the case where the schema update was forgotten or incomplete.

---

## Process Notes

The R3 pattern of "owner authors concrete BEFORE/AFTER, board seconds/adjusts/rejects" is more efficient than "board proposes and negotiates." Worth encoding in the SOP.

The PD3 split resolution mechanism — converting a FIX NOW disagreement into a Step G acceptance criterion — is a useful governance pattern. When two rounds can't resolve a split, the answer is often "defer but bind it to an observable trigger." The board should have this in its toolkit explicitly.
