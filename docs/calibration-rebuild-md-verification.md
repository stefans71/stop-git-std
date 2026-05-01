# Calibration rebuild — Phase 6: MD calibration verification (LLM consumer test)

**Phase:** 6 of `docs/back-to-basics-plan.md`
**Date:** 2026-05-01
**Branch:** `chore/calibration-md-verification` from `main` at `5d4ed3b` (Phase 5 close).
**Method:** for each of 5 selected catalog scans, hand the rendered MD to a cold fork (general-purpose agent, fresh context, no project knowledge) and ask the plan §Phase 6 prompt verbatim:

> *"You're an LLM consumer. The user pasted this MD report and asked 'should I install this?' Give your answer. Don't reference any other knowledge — just react to the report."*

Forks were instructed to respond in a fixed shape (VERDICT + ONE-LINE + WHY + WHAT-WOULD-CHANGE-YOUR-MIND) so answers are comparable. Verdict enum: `YES` / `YES-WITH-CAVEATS` / `IT-DEPENDS` / `NO`.

**Pass bar:** cold fork answer matches calibrated reading on ≥4 of 5.

**Result: 5 of 5 match. Pass bar cleared.**

---

## Verdict-mapping convention

The cold fork was free to pick any of YES / YES-WITH-CAVEATS / IT-DEPENDS / NO. The mapping to the calibrated `verdict_level` enum used for match/miss classification:

| Calibrated `verdict_level` | Fork verdicts that count as MATCH |
|---|---|
| `Healthy` | YES |
| `Caution` | YES-WITH-CAVEATS, IT-DEPENDS |
| `Critical` | NO |

A fork answering `YES` (clean) on a `Caution` scan = miss (under-cautious). A fork answering `YES-WITH-CAVEATS` on a `Critical` scan = miss (under-cautious). A fork answering `NO` on a `Caution` scan would be over-cautious — also a miss (this is the failure mode session 8 flagged).

---

## Summary

| Entry | Repo | Calibrated | Fork verdict | Match |
|---:|---|---|---|:---:|
| 16 | ghostty-org/ghostty | Caution | YES-WITH-CAVEATS | ✓ |
| 26 | WhiskeySockets/Baileys | Critical | NO | ✓ |
| 27 | mattpocock/skills | Caution | YES-WITH-CAVEATS | ✓ |
| 20 | BatteredBunny/browser_terminal | Critical | NO | ✓ |
| 24 | freerouting/freerouting | Critical | NO | ✓ |

**Match count: 5 / 5.**

---

## Per-scan detail

### Entry 16 — ghostty-org/ghostty (Caution)

- **Calibrated cells:** Q1 amber (override), Q2 green, Q3 amber, Q4 amber. Verdict: `Caution`.
- **MD path:** `docs/scans/catalog/GitHub-Scanner-ghostty-v12.md`

**Fork verdict:** **YES-WITH-CAVEATS** — match.

```
ONE-LINE: Install via Homebrew for personal use, but pin a specific commit SHA if
you're putting it anywhere production-adjacent.

WHY:
- 51k stars, MIT, active maintenance, zero open security issues, and 5 GHSA
  advisories already responsibly disclosed — the project clearly takes security
  seriously.
- Modern ruleset-based branch protection + CODEOWNERS are in place, so code review
  controls exist even if not classic-style.
- Two real but manageable concerns: Mitchell Hashimoto authors 85.9% of commits
  (bus-factor risk) and there are no versioned releases — `brew upgrade` pulls
  whatever landed today.
- Only Info-level hygiene gaps (missing SECURITY.md, two `pull_request_target`
  workflows flagged for review but no confirmed vuln).
- Code-pattern grep was clean: only 2 hits across 15 dangerous-primitive families,
  no secrets, no install-script hooks.

WHAT-WOULD-CHANGE-YOUR-MIND: A confirmed exploit in the `pull_request_target`
workflows or evidence the maintainer-concentration is producing stalled security
responses would flip me to NO; conversely, formal versioned releases would push
this to a clean YES.
```

**Analysis:** Fork picked up the same signals the calibrated cells were built from — solo-maintainer concentration (Q1 override), zero open security issues + responsiveness (Q2 green), GHSA advisories without SECURITY.md (Q3 amber), no versioned releases (Q4 amber). The `pull_request_target` Info finding made it into the fork's reasoning without being treated as a blocker, which is the calibrated intent.

### Entry 26 — WhiskeySockets/Baileys (Critical)

- **Calibrated cells:** Q1 red, Q2 red, Q3 red, Q4 red (override). Verdict: `Critical`.
- **MD path:** `docs/scans/catalog/GitHub-Scanner-Baileys.md`

**Fork verdict:** **NO** — match.

```
ONE-LINE: Don't install this unless you're knowingly attaching a burner WhatsApp
number to a hobby bot — the report flags inherent ToS-violation/account-ban risk
plus a stack of governance and CVE problems.

WHY:
- F0 Critical: Baileys is a reverse-engineered unofficial WhatsApp client; using
  it can get your WhatsApp account permanently suspended, and the README itself
  disclaims endorsement.
- 14 known CVEs across 6 runtime deps, including 5 on `ws` — the core WebSocket
  library every Baileys connection rides on.
- A community vulnerability-fix PR (#1996) was stale-closed after 148 days; the
  maintainer's promised replacement never shipped, so deprecated `request` deps
  with SSRF + TLS-bypass CVEs are still in master.
- Zero governance: no branch protection, no rulesets, no CODEOWNERS, no
  SECURITY.md in 4 years, 0 published advisories, 89.5% top-2 maintainer
  concentration — a compromised maintainer account ships straight to npm.
- 150-day release stall on `@latest` (v7.0.0-rc.9), so even if fixes did land
  they wouldn't reach consumers; all four Trust Scorecard questions are "No."

WHAT-WOULD-CHANGE-YOUR-MIND: If this were strictly a hobby/burner-number use
case AND PR #1996 (or its replacement) had landed with `ws` bumped, branch
protection enabled, and a SECURITY.md in place, I'd downgrade to YES-WITH-CAVEATS.
```

**Analysis:** Strongest match in the set. Fork independently named all four red cells (governance, fix-velocity via PR #1996, disclosure, supply-chain via ws CVEs) plus the F0 reverse-engineering ToS finding. Carve-out for hobby use mirrors the calibrated dossier's adoption-path framing.

### Entry 27 — mattpocock/skills (Caution)

- **Calibrated cells:** Q1 red, Q2 amber (override), Q3 red, Q4 amber. Verdict: `Caution`.
- **MD path:** `docs/scans/catalog/GitHub-Scanner-skills.md`
- **Note:** entry 27 was the first catalog entry with a `missing_qualitative_context` override at any n value (V13-3 §2 inference reopened — see `project_session8_status.md`). The verdict downgrade from `Critical` to `Caution` is precisely the case this fork test was meant to validate.

**Fork verdict:** **YES-WITH-CAVEATS** — match.

```
ONE-LINE: It's safe to install today if you read the SKILL.md files and pick the
clone+link path, but treat any future re-install as a code-review event.

WHY:
- Content sampled is benign and consent-driven, and several skills (e.g.
  /git-guardrails-claude-code) are explicitly defensive — no malicious code or
  dangerous primitives found across 15 grep families.
- Maintainer is a known, reputable figure (Matt Pocock, Total TypeScript) and
  the repo has 47.9k stars, which is a meaningful (if soft) trust signal.
- Structural risk is real but manageable: solo maintainer (87.3% commit share +
  a test account), zero branch protection, zero releases (rolling install), no
  SECURITY.md (PR proposing one was closed), and a two-stage supply chain through
  vercel-labs/skills npm CLI.
- 22 SKILL.md files (1,815 lines) become instructions Claude executes against
  your repo — and only 1 of 23 was actually scanned for prompt injection, so
  your own read-through is doing real work.
- Verdict is "Caution," not Critical; no published advisories, no overdue items,
  no detected secrets or dangerous patterns.

WHAT-WOULD-CHANGE-YOUR-MIND: Evidence of any actually-malicious or
data-exfiltrating SKILL.md, a recent unexplained force-push to main, or a
compromise signal on the vercel-labs/skills CLI would flip me to NO; conversely,
branch protection + a SECURITY.md + pinned release tags would flip me to YES.
```

**Analysis:** Critical validation — this is precisely the verdict shape the V13-3 `missing_qualitative_context` override was authored to produce. A previously over-cautious read would have returned `NO` ("solo maintainer + zero governance + n=23 instruction files = Critical"). The fork instead engaged with the qualitative content (benign skills, defensive intent, reputable maintainer) and returned a graduated YES-WITH-CAVEATS that names the structural risks without treating them as blockers. The override survived a cold consumer test.

### Entry 20 — BatteredBunny/browser_terminal (Critical)

- **Calibrated cells:** Q1 red, Q2 green, Q3 red, Q4 red (override). Verdict: `Critical`.
- **MD path:** `docs/scans/catalog/GitHub-Scanner-browser_terminal-v12.md`

**Fork verdict:** **NO** — match.

```
ONE-LINE: Don't follow the README's Chrome install link — and honestly, given
everything else stacked on top, I'd skip this tool unless you really need a
browser-tab shell.

WHY:
- The README's Chrome Web Store link points to chrome.google.cm (Cameroon TLD)
  instead of chrome.google.com — a live typosquat that could serve a fake store
  page if the domain is attacker-controlled (F0 Critical).
- The Go native host is shipped from GitHub Releases with zero checksums or
  signatures, and install instructions tell you to `sudo mv` it without any
  verification step (F1).
- By design, the native host gives any extension context a live `/bin/sh` with
  your user privileges — no auth, no allowlist, no prompt (F4).
- Single maintainer, 0% PR review rate across 12 lifetime PRs, no branch
  protection, no CODEOWNERS, no SECURITY.md — one account compromise reaches
  every user (F3).
- 10-month release stall means even fixes on main don't reach store-distributed
  users until a new tag is cut (F2).

WHAT-WOULD-CHANGE-YOUR-MIND: If the maintainer fixed the .cm typo, started
signing releases (Sigstore or .sha256), and added at least a shared-secret
between the extension and the native host, this drops to YES-WITH-CAVEATS for
users who actually want a browser-tab terminal.
```

**Analysis:** Fork led with the live typosquat (F0) — the highest-impact finding in the report — and stacked the supply-chain + privilege findings (F1, F4) consistent with the Q4 red override. The Q2 green cell (no published CVEs and active maintenance) is correctly NOT used as a counter-signal; the fork named the 10-month release stall as F2 instead. Calibrated reading and consumer reading converge on the same blocker set.

### Entry 24 — freerouting/freerouting (Critical)

- **Calibrated cells:** Q1 red, Q2 green, Q3 amber, Q4 red (override). Verdict: `Critical`.
- **MD path:** `docs/scans/catalog/GitHub-Scanner-freerouting-v12.md`
- **Phase 6 priority work item watch:** this is one of the 5 entries the Phase 5 calibration v2 rerender flagged as a Q3 FALLBACK regression (advisory shifted amber→red, LLM cell stayed amber, no override_reason). Phase 6 specifically asked whether the Q3 drift would skew the cold fork.

**Fork verdict:** **NO** — match.

```
ONE-LINE: Don't install this for opening untrusted board files — it has a
textbook Java deserialization RCE on the default file-open path, and the project
lacks the governance to fix it quickly.

WHY:
- F0 critical: BasicBoard.java:108-110 calls ObjectInputStream.readObject()
  directly on user-loaded files, with the same pattern across 35 files — a
  malicious .binsnapshot opens as code execution on your machine.
- Solo maintainer (andrasfuchs 86.7%) with an anti-destruction-only ruleset (no
  review requirement) and only 9.5% formal review — a compromised account or bad
  PR can land unchecked.
- 373-day release stall since v2.1.0 means even if a fix lands on main,
  fix-to-user latency is huge.
- No SECURITY.md and zero published advisories in 12 years despite a confirmed
  RCE-class surface — no clear disclosure channel.
- Positives exist (Dependabot active on Gradle, 75% community health, Gemini-AI
  triage) but none of them mitigate the deserialization vector.

WHAT-WOULD-CHANGE-YOUR-MIND: If freerouting shipped a release that replaced
ObjectInputStream with a safe format (or at least an ObjectInputFilter
whitelist) and only opened files I generated myself, I'd downgrade to
YES-WITH-CAVEATS — or I'd run it today inside a throwaway Docker container with
only DSN files from trusted sources.
```

**Analysis:** Fork independently led with the F0 deserialization RCE (the Q4 override-reason driver) and stacked governance (Q1) + release stall + missing SECURITY.md (Q3 amber). The fork's mention of "no SECURITY.md and zero published advisories in 12 years" treats the Q3 amber/red distinction as moot — the absence of a disclosure channel is the consumer-relevant fact, regardless of whether calibrated advisory said amber or red. **This is a Q3-attribution datapoint:** the cold fork did NOT pivot on the calibrated Q3 color; it engaged with the underlying signals. See §"Q3 FALLBACK regression — did it actually matter?" below.

---

## Q3 FALLBACK regression — did it actually matter for this test?

**Answer: no.** The Phase 5 calibration v2 rerender mutated `phase_3_advisory.scorecard_hints` and exposed Q3 advisory drift on 5 entries (ghostty, kamal, wezterm, freerouting, WLED — see `docs/calibration-rebuild-rerender-comparison.md` §"Phase 6 input — gate 6.3 backlog"). The §Current state warning was that "the Q3 advisory drift propagates through the rendered MD."

In practice, **it does not.** Rendered MD is sourced from `phase_4_structured_llm.scorecard_cells` (the LLM-authored cell colors), not from `phase_3_advisory.scorecard_hints`. The LLM cells were authored before Phase 5 and were not re-authored. Spot check on the rendered MD for ghostty Q3 confirms `⚠ **Partly**` (amber) renders, not red.

**Implication for this test:** the cold-fork run did NOT actually stress-test calibration v2's Q3 rule changes. It validated that the Phase 4-era LLM cells (unchanged across Phase 5) still lead consumers to the calibrated verdict.

**Implication for Phase 6 priority work item:** the gate 6.3 backlog (7 cells across 6 entries) is now a `phase_3` ↔ `phase_4` divergence the validator's `--form` mode will eventually demand resolution on, but it is NOT propagating into consumer-facing MD today. Phase 7 work can decide whether to:
- **(a)** re-author Phase 4 cells to align with calibration v2 advisory (and accept that consumer-facing reports will shift on those 5 entries),
- **(b)** add `override_reason` to existing Phase 4 cells to keep current MD semantics with rule-driven advisory,
- **(c)** soften calibration v2 Q3 rules (introduce a RULE-5-style softener for repos with partial disclosure signals so advisory naturally lands amber, matching legacy + matching the LLM cells already in place).

The cold-fork test does not pick between these — it just confirms the current rendered MD reads correctly to a consumer.

---

## Failure-mode coverage

The test was designed to detect three failure modes flagged in earlier sessions:

| Failure mode | Detected here? | Why / why not |
|---|---|---|
| **Over-cautious skill collections** (session 8 — V13-3 §2 inference: solo + zero governance + many instruction files → false-Critical) | No | Entry 27 (skills) returned YES-WITH-CAVEATS — the V13-3 `missing_qualitative_context` override survived the cold read. |
| **Under-cautious genuine criticals** (Baileys / browser_terminal / freerouting) | No | All three returned NO with reasoning that named the calibrated blockers. |
| **Q3 advisory drift skewing consumer reading** (Phase 5 priority work item) | Not exercised | Rendered MD reflects Phase 4 LLM cells, which are unchanged. The Q3 drift lives in `phase_3_advisory` only. |

---

## Owner sign-off

- [ ] Match count = 5 of 5 (pass bar ≥4) — confirmed.
- [ ] Q3 attribution analysis above accurate (rendered MD = phase_4 LLM cells, drift is phase_3-only).
- [ ] Recommend proceeding to Phase 7 (Simple Report HTML on top of calibrated MD).
- [ ] Approve merge of `chore/calibration-md-verification` to `main`.

Phase 6 is read-only relative to MD content (no MD or HTML files were modified). The only delta on this branch is this verification doc + a §Current state update.
