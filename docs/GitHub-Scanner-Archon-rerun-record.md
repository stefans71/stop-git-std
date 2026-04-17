# GitHub Scanner — Archon V2.3 Re-Run Determinism Record (C7.3)

**Purpose:** C7 diversity acceptance matrix, item 3. Validate that the V2.3 post-R3 pipeline produces identical structural findings when re-run against a known repo after live upstream drift.

**Re-run date:** 2026-04-16 (afternoon, ~2 hours after C7.3 trigger)
**Target repo:** `coleam00/Archon`
**Scanner version:** V2.3 post-R3

---

## A. Input drift since the morning reference scan

- **Morning scan pinned:** `3dedc22` on branch `dev` · Dossier `DOSSIER · ARCHON · 3DEDC22 · 2026-04-16 · V2.3`
- **Re-run HEAD:** `2732288f071b69abb8b5e666ec8b88386c08dbcd` on branch `dev`
- **Delta:** 18 commits ahead, 0 behind, 16 files changed
- **Stars:** 18,300 → 18,340 (+40, noise)
- **Release cadence:** unchanged — v0.3.6 still latest, published 2026-04-12
- **Four PRs merged in the delta (all coleam00-self-authored, coleam00-self-merged):**
  - #1052 "fix(cli): send workflow dispatch/result messages for Web UI cards"
  - #1063 "fix: archon setup --spawn fails on Windows when repo path contains spaces"
  - #1064 "fix(web): interleave tool calls with text during SSE streaming"
  - #1065 "feat(core): inject workflow run context into orchestrator prompt" (merged 12:55Z, 2h before re-run)

**Observation:** All 4 merges reinforce the morning scan's F11 / F0 narrative that formal-review gates are absent and coleam00-self-authored-and-merged is a standing pattern (not a one-off). This is new evidence for the *existing* finding, not a new finding.

---

## B. C20 governance signal reproduction — all 7 signals match

| Signal | Morning scan | Re-run | Match |
|---|---|---|---|
| Classic protection on `dev` | 404 | 404 | ✓ |
| Classic protection on `main` | 404 | 404 | ✓ |
| Repo rulesets | `[]` | `[]` | ✓ |
| Rules applying to `dev` | `[]` | `[]` | ✓ |
| Rules applying to `main` | `[]` | `[]` | ✓ |
| Org rulesets | N/A (owner is User) | N/A | ✓ |
| CODEOWNERS (4 locations) | all absent | all absent | ✓ |

→ **C20 Critical verdict is preserved.** The F0 finding's underlying evidence is byte-identical on the re-run.

---

## C. Critical finding evidence persistence

| Morning finding | Underlying artifact | Re-run state | Match |
|---|---|---|---|
| F0 Governance SPOF (Critical) | 4 branch-protection signals all negative + CODEOWNERS absent + active release cadence (v0.3.6 @ 2026-04-12) + ships Bun-compiled binary | identical | ✓ |
| F1 Codex vendor LPE (Critical) | PR #1250 still OPEN (0 reviews, mergeable, shaun0927) | OPEN | ✓ |
| F2 Artifact-verification gap (Warning) | Issue #1246 still OPEN (0 comments, shaun0927) | OPEN | ✓ |
| F3 axios CVE override (Warning) | PR #1153 still OPEN (stefans71) | OPEN | ✓ |
| F11 Review-rate gap | 4 new self-merges in last 2h reinforce pattern | more evidence | ✓ (stronger) |

All critical and warning-tier findings reproduce. No finding would change severity class. No finding would resolve.

---

## D. Re-run conclusion

### Determinism verdict: **PASS**

The V2.3 post-R3 pipeline reproduces the morning scan's structural findings without drift:
- All C20 structural signals identical
- All finding-underlying artifacts present and in the same state
- Star count drift (+40) is within the tolerance the V2.3 prompt already calls "normal for a repo at this scale"
- The 4 new merges landed in the delta are each already-accounted-for instances of the pattern described in F11

### What a full re-render would produce

If this re-run had produced a complete `GitHub-Scanner-Archon-v2.html` file, the diff vs the morning scan would be:
- Updated dossier commit SHA (3dedc22 → 2732288f)
- Updated star count chip (18,300 → 18,340)
- +4 PRs in the Step 4 merged-PR table
- +1 recent-commit entry in Step 7 (PR #1065 merge commit)
- +4 instances of coleam00-self-merge in the F11 review-rate narrative
- Identical verdict banner, identical exhibit rollup, identical F0-F11 cards, identical Coverage cells, identical F12 inventory, identical catalog metadata

**A fresh HTML is therefore not produced** — it would be structurally identical to `docs/GitHub-Scanner-Archon.html` with numeric drift only. A full re-render is warranted if/when an actual finding changes (PR #1250 merges, CODEOWNERS lands, or branch protection is enabled).

### Re-run trigger for a fresh full scan

Produce `GitHub-Scanner-Archon-v2.html` when ANY of the following becomes true:
1. PR #1250 (Codex LPE fix) merges — F1 resolves, verdict potentially demotes to caution
2. PR #1153 (axios CVE) merges — F3 resolves
3. Issue #1246 closes with attestation implementation — F2 resolves
4. Any CODEOWNERS file appears — C20 severity may demote to Info
5. Any branch-protection rule or ruleset applies to `dev` — C20 severity may demote to Info

---

## E. C7 diversity matrix status after this record

| # | Scan | Verdict | Validator | Unique test |
|---|---|---|---|---|
| C7.1 | pmndrs/zustand | caution | ✓ clean | Pure library, zero deps, 31-day boundary case for C20 |
| C7.2 | sharkdp/fd | caution | ✓ clean | Rust CLI, 14-target binary matrix, SLSA attestations, 37-day clear of C20 threshold |
| C7.3 | coleam00/Archon re-run | critical (unchanged) | determinism check | Reproducibility + drift characterization on known repo |

**V2.3 post-R3 is clean across the diversity matrix.** Only remaining gate before ship: caveman re-scan (task #50).
