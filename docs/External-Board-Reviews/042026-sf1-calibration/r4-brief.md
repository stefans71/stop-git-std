# SF1 Board Review — R4 Brief (Stateless, Narrow Tension-1 Only)

**Review type:** Single-tension tiebreaker.
**Round:** 4 (Tension 1 only).
**Scope:** NARROW — resolve the Archon Q3 "published advisories for fixed vulns" interpretation only. R3 locked the rest of the synthesized hybrid with 3/3 CONFIRM + 3/3 UNION-ACCEPT on Tension 2 + clean dissent audit. **Gate C stays in the Phase 1 plan regardless of this vote.** R4 decides the DEFAULT entering the Gate C audit (and whether G-C-ACCEPT means "no pre-declared default").

Agents are stateless — everything needed is inline.

---

## 1. The narrow question

**Is the V2.4 rubric's "published advisories for fixed vulns" requirement (Q3 green condition) a STRICT PRECONDITION or an INTENT-READING?**

- If **strict precondition** → compute.py's current amber on Archon Q3 is correct; V2.4 LLM's green was disobedience; skip the `has_reported_fixed_vulns` patch; **default vote D-CANONICAL**.
- If **intent-reading** → rubric's intent is to reward active disclosure processes; repos with SECURITY.md + nothing yet to disclose reach green via `has_reported_fixed_vulns = false`; apply the patch; **default vote A-CANONICAL**.
- If **evidence-dependent** → cannot be decided without Phase-1 audit of Archon's specific vuln history; Gate C runs with no pre-declared default; **vote G-C-ACCEPT**.

Your vote:
- **A-CANONICAL** (Pragmatist R3 position)
- **D-CANONICAL** (Skeptic R3 position)
- **G-C-ACCEPT** (Codex R3 position)
- **OTHER** (propose a different resolution)

---

## 2. The rubric text — VERBATIM (from `docs/repo-deep-dive-prompt.md` lines 753–756)

> **"Do they tell you about problems?"**
> - **Green** — `SECURITY.md` with private channel AND published advisories for fixed vulns.
> - **Amber** — `SECURITY.md` with private channel BUT no published advisories; OR unadvertised-but-release-noted fixes (F5 class). Use the label "Disclosed in release notes, no advisory" when fixes ship without GHSA.
> - **Red** — No `SECURITY.md` OR silent fixes (F5 class). Use the label "No advisory".

Key phrases to weigh:
- Green requires both AND-clauses (SECURITY.md + private channel AND published advisories for fixed vulns).
- Amber explicitly covers "SECURITY.md with private channel BUT no published advisories." This is the exact Archon state.
- There is no "nothing to disclose yet" exemption in the rubric text.

---

## 3. Archon evidence — VERIFIED LIVE

Run from `/root/tinkering/stop-git-std/` just now:

```
$ gh api repos/coleam00/Archon/security-advisories --jq '. | length'
0
```

**Archon has 0 published GitHub Security Advisories.** (Verified live against GitHub API.)

Archon DOES have SECURITY.md with real private reporting channel (from the V2.4 comparator MD):
- `cole@dynamous.ai` email
- GitHub's private advisory reporting link
- Recently added (2026-03 to 2026-04)

Archon's 3 currently-open security-related items at scan time (F1/F2/F3 in the comparator MD):
- **F1 Codex vendor binary LPE** — issue #1245, PR #1250 open
- **F2 Web-dist attestation gap** — tracked
- **F3 Axios CVE-2025-62718** — PR #1153 open 3 days

Archon's history of security-related PRs merged (from comparator MD's activity-timeline):
- **PR #1169 + PR #1217** — described as "security-minded refactors" shipped during the scan window. **Were any of these fixes for undisclosed vulnerabilities that should have gotten GHSAs?** The comparator MD does not say.

The comparator MD's own Disclosure section (line 380):
```
| Security advisories | ⚠ 0 published | May be used in future for open items |
```

Notice the comparator ACKNOWLEDGES 0 published advisories and uses the "⚠" warning indicator — yet the Trust Scorecard at line 77 says:
```
| Do they tell you about problems? | ✅ Yes — SECURITY.md + public issues |
```

**The comparator MD is INTERNALLY inconsistent on Archon Q3.** The Trust Scorecard row (green) contradicts the Disclosure section (⚠ 0 published). This is a V2.4 LLM output, not human-reviewed ground truth.

---

## 4. R3 votes on Tension 1 — VERBATIM

### 4.1 Pragmatist R3 — A-CANONICAL

```
Vote: A-CANONICAL

Rationale: Gate C defers a decision that can be made now without additional Phase 1 data. The evidence is already in the brief: Archon has a SECURITY.md and 0 published advisories because it has not had a public security vulnerability to disclose — not because it is hiding disclosures. DeepSeek's "LLM disobedience" framing depends on reading the rubric's "published advisories for fixed vulns" requirement as a strict precondition that penalizes projects with clean records, which is an unreasonable reading of the rubric's intent. A security-mature project with a SECURITY.md, a private reporting channel, and nothing to disclose yet is not amber — it is green with `has_reported_fixed_vulns = false`. Deciding A-CANONICAL now removes an unnecessary runtime branch from Phase 1 execution, eliminates the risk that the operator picks D-CANONICAL in the moment for the wrong reasons, and keeps the patch list clean. If Gate C auditing the Archon repo during Phase 1 execution surfaces evidence that Archon DID have vulns it did not disclose, the operator can flip to D-CANONICAL at that point — but the default should be the `has_reported_fixed_vulns` patch, not a coin flip.

[From INFO section of the same response:]

A-CANONICAL has a load-bearing assumption: The `has_reported_fixed_vulns` patch for Archon Q3 requires that Phase 1 data collection can reliably determine whether the repo has had prior security vulnerabilities. The hybrid's data-availability note says "check already-captured GitHub Security Advisories count = 0 AND the historical CVE issue list = 0." This is a reasonable proxy but not perfect — a repo could have handled vulnerabilities privately without creating GitHub advisories or public CVE issues. For the purposes of Step G validation on the 3 pinned targets, this is fine. For V1.2 design, the `has_reported_fixed_vulns` input field should carry a docstring noting it is a best-effort proxy from public sources. This is not a reason to reject A-CANONICAL; it is implementation hygiene.

[From Blind spots:]

I cannot evaluate Tension 1 with new Archon data. My A-CANONICAL vote is based on the rubric-intent argument, not a fresh read of Archon's actual SECURITY.md and advisory history. If the Archon repo turns out to have had disclosed vulnerabilities that the V2.4 LLM missed when giving green, DeepSeek's disobedience framing would be correct and A-CANONICAL would bake in the wrong fix. The Phase 1 operator should confirm `has_reported_fixed_vulns = false` is actually true for Archon before applying the patch — this is what Gate C was designed for, and even though I voted A-CANONICAL (default to the patch), the gate's audit step should still execute as a verification, not be skipped.
```

### 4.2 Systems Thinker R3 — G-C-ACCEPT

```
Vote: G-C-ACCEPT

Rationale: For this round, Gate C is the right disposition because it prevents the archive from hard-coding a semantic claim that the brief itself still treats as contested. From a systems perspective, the important boundary is that whichever branch is taken is documented as a temporary V1.1 calibration decision, not as proof that Q3 judgment belongs permanently in deterministic compute.
```

### 4.3 Skeptic R3 — D-CANONICAL

```
Vote: D-CANONICAL

Rationale: The rubric explicitly requires "published advisories for fixed vulns" for green. Archon has zero published advisories. This is not rubric ambiguity—it's LLM disobedience. Accepting compute.py's amber as correct maintains rubric integrity and avoids creating a special-case patch that rewards ignoring clear requirements. The LLM's leniency, while user-friendly, violates the scoring framework it was instructed to follow.
```

---

## 5. The three competing readings

### Reading 1: Strict precondition (DeepSeek D-CANONICAL)

- Rubric text is explicit: green requires BOTH (`SECURITY.md` + private channel) AND (`published advisories for fixed vulns`).
- Amber is explicitly defined to cover "SECURITY.md with private channel BUT no published advisories." That phrase exactly describes Archon.
- The rubric author could have written "green = SECURITY.md with private channel (published advisories not required if no vulns)" and chose not to. The literal text is binding.
- 0 published advisories → amber. Not a bug, not disobedience to reality — a correct amber reading per the rubric.
- **What V2.4 did wrong:** the LLM gave green. That's disobedience.
- **Consequence:** compute.py's amber stays. V2.4 Archon comparator scorecard Q3 gets corrected from green → amber during U-11 (a one-cell catalog fix, not a full harmonization). Step G gate 6.3 then passes on this cell without patching compute.

### Reading 2: Intent-reading with "nothing to disclose" exemption (Pragmatist A-CANONICAL)

- Rubric's purpose is to reward active disclosure processes, not to punish repos with clean records.
- A brand-new SECURITY.md with zero vulns-to-date should reach green — otherwise no repo can ever be green in its first year.
- `published advisories for fixed vulns` presupposes there are fixed vulns to report. If there are zero, the clause is vacuously satisfied.
- The patch (`has_reported_fixed_vulns` flag) encodes this intent: green when SECURITY.md present AND (published advisories > 0 OR no vulns to report).
- **What V2.4 did right:** the LLM read the rubric's intent correctly. compute.py's literal reading was the rigid one.
- **Consequence:** Apply the patch. Archon Q3 goes green via `has_reported_fixed_vulns = false`. Gate 6.3 passes on this cell.

### Reading 3: Evidence-dependent — cannot pre-decide (Codex G-C-ACCEPT)

- Both strict and intent readings are defensible in the abstract.
- The right answer depends on whether Archon has had UNDISCLOSED fixed vulns (PRs #1169 / #1217 were "security-minded refactors" — were any of them for vulns that should have been advisory'd?).
- If yes → strict reading applies; Archon Q3 should be amber (even on intent-reading, because they HAD vulns to disclose and didn't).
- If no → intent reading applies; Archon Q3 can be green (no fixed vulns to require advisories for).
- The brief cannot resolve this from documentation alone — requires Phase 1 operator to read the diff/commit messages of #1169 and #1217.
- **Consequence:** Gate C runs without default. Operator decides A vs D based on Archon's actual code/history.

---

## 6. Additional evidence that matters for your vote

**The comparator MD is internally inconsistent on Archon Q3:**
- Trust Scorecard (line 77): `✅ Yes — SECURITY.md + public issues` → green.
- Disclosure section (line 380): `⚠ 0 published | May be used in future for open items` → warning indicator.

The V2.4 LLM flagged "0 published" with a warning symbol in one section, then reported green in the Trust Scorecard. This is not confident rubric-intent reading — this is the LLM seeing the conflict and deciding to flag-but-accept. Weight this however you choose:
- Pro-strict: the LLM itself acknowledged the gap; the warning ⚠ was the honest read; green in the scorecard was the leniency.
- Pro-intent: the LLM saw active process + open tracking + recent SECURITY.md and judged "the process is working, advisories would be premature"; warning was just accurate reporting of the numeric count.

**Archon has ACTIVE security work in public:**
- 3 open security issues being tracked and worked
- 2 recent PRs merged that are described as "security-minded refactors"
- External reporter using the SECURITY.md private channel

This is **not** a dormant repo claiming security maturity. It's actively receiving reports and shipping fixes. If the rubric's purpose is to distinguish "team that handles security" from "team that doesn't," Archon is clearly the former.

**Archon's SECURITY.md is recent (2026-03 to 2026-04):**
- At ~1 month old at scan time
- No advisories published because no vulns have been resolved through the advisory process yet
- The 3 open items may become the first advisories

---

## 7. What A-CANONICAL and D-CANONICAL actually output

**If A-CANONICAL (apply patch) with `has_reported_fixed_vulns = FALSE` for Archon:**
- Q3 Archon → **green** (SECURITY.md + nothing to disclose yet)
- Matches V2.4 comparator (green) ✓
- Gate 6.3 passes on Archon Q3 ✓

**If A-CANONICAL (apply patch) with `has_reported_fixed_vulns = TRUE` for Archon** (operator judges that #1169/#1217 or similar fixes did constitute reported vulns):
- Q3 Archon → **amber** (has fixed vulns but no advisories)
- Does NOT match V2.4 comparator (green) ✗
- Gate 6.3 fails on Archon Q3 — requires rewriting V2.4 Archon Q3 from green to amber

**If D-CANONICAL (skip patch):**
- Q3 Archon → **amber** (compute.py literal)
- Does NOT match V2.4 comparator (green) ✗
- Gate 6.3 fails on Archon Q3 — requires rewriting V2.4 Archon Q3 from green to amber (the single-cell catalog correction)

**Critical observation:** D-CANONICAL and "A-CANONICAL with honest data" produce IDENTICAL outputs if Archon has ever shipped a security fix that could have been advisory'd. The two camps differ only on:
1. Whether the rubric's intent ever allows "nothing to disclose yet" (philosophical).
2. Whether Archon specifically qualifies for that exemption (empirical).

G-C-ACCEPT is the one position that doesn't require us to decide #1 without evidence on #2.

---

## 8. Required output format

```
# SF1 R4 — [Your agent name]

## Vote

A-CANONICAL / D-CANONICAL / G-C-ACCEPT / OTHER

## Rationale (3–6 sentences)

[Which reading of the rubric survives the additional evidence in §6 + §7? What, if anything, changed from your R3 position?]

## Specific reply to the opposing position

[If A or D: engage with the strongest argument from the other camp. If G-C-ACCEPT: explain why the empirical uncertainty outweighs the philosophical clarity of either A or D.]

## Secondary consequences of your vote

[If A-CANONICAL: what happens if Gate C finds Archon DID have disclosable vulns?
If D-CANONICAL: acknowledge that V2.4 Archon Q3 will need a one-cell catalog correction (green → amber).
If G-C-ACCEPT: what criteria should the Phase 1 operator use to pick?]

## Blind spots

[Things you might be missing in this R4 analysis.]
```

---

## 9. What this vote decides (and does not)

- **Decides:** the DEFAULT bias entering Gate C. A-CANONICAL = default apply patch. D-CANONICAL = default skip patch. G-C-ACCEPT = no default; operator decides purely on evidence.
- **Does NOT decide:** whether Gate C runs (it runs regardless).
- **Does NOT decide:** anything else in the synthesized hybrid (all locked by R3 3/3 CONFIRM).
- **If all 3 agents vote the same way** → decision is unanimous and archived.
- **If 2-1 split** → majority wins; minority dissent is recorded in the consolidation doc.
- **If 3 different votes** → owner decides.

Your vote is your last say on this point before archival.
