# Path B Test Prompt — First Exercise (2026-04-16)

This is the exact prompt given to a fresh Claude Opus 4.6 sub-agent to validate the Operator Guide V0.1 as self-sufficient. The agent had no memory of prior scans. Result: PASS — structural parity with v1 scan, validator-clean on first attempt.

---

You are an LLM operator running the GitHub Scanner for the first time. Your ONLY instructions are the Operator Guide and the handoff packet described below. You have never seen a scan run before. Follow the guide exactly.

## Your mission

Run a V2.3 post-R3 scan on `pmndrs/zustand` following the Operator Guide end-to-end. Produce:
- `/root/tinkering/stop-git-std/docs/GitHub-Scanner-zustand-v2.html`
- `/root/tinkering/stop-git-std/docs/GitHub-Scanner-zustand-v2.md`

Both must pass `python3 docs/validate-scanner-report.py --report <file>` with exit 0.

Use `-v2` suffix so you don't overwrite existing scan artifacts.

## Handoff packet (§8.3 of the Operator Guide)

Read these files in this order — this is the complete artifact set per the guide's §8.3 "portable handoff packet":

1. **The Operator Guide** — `/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md` (552 lines). This is your primary process document. Follow it phase by phase.
2. **The V2.3 prompt** — `/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md` (1078 lines). This tells you WHAT to investigate and what output rules to follow.
3. **The template** — `/root/tinkering/stop-git-std/docs/GitHub-Repo-Scan-Template.html` (1870 lines). Replace all `{{PLACEHOLDER}}` tokens and delete all `EXAMPLE-START/END` blocks.
4. **The validator** — `/root/tinkering/stop-git-std/docs/validate-scanner-report.py` (288 lines). Your Phase 5 gate.
5. **One reference scan (shape match)** — `/root/tinkering/stop-git-std/docs/GitHub-Scanner-fd.html` — use this as your structural reference. fd is another `caution`-verdict scan with Warning + Info findings. Copy fd's STRUCTURE, not its CONTENT. Write fresh prose for zustand.
6. **The findings-bundle slot** — you will CREATE this at `/tmp/scan-zustand-v2/findings-bundle.md` during Phase 3.

## Critical process rules from the guide (so you don't have to re-derive them)

- **Phase 1**: mkdir `/tmp/scan-zustand-v2/`, capture HEAD SHA into `head-sha.txt` FIRST, download tarball at pinned SHA, extract.
- **Phase 2**: follow §6.1's ordering (mirrors V2.3 prompt Steps 1-8 + A/B/C). Each gh api call produces FACTS. Tag everything as fact.
- **Phase 3**: write findings-bundle.md with structurally-separated sections: evidence (facts only) → pattern recognition (inference, tagged) → findings summary + proposed verdict + scorecard (synthesis, citing evidence refs).
- **Phase 4a**: bundle → canonical MD (creative rendering step). MD is the canonical output.
- **Phase 4b**: MD → HTML (structurally derived — HTML may NOT add or alter findings/verdicts/evidence absent from MD).
- **Phase 5**: `python3 docs/validate-scanner-report.py --report <file>` on BOTH files. Iterate until both exit 0.
- **Phase 6a**: you don't need to update the catalog (I'll handle that). Just produce the two output files.

## What you're testing

This is the first-ever Path B (delegated) scan. You are a fresh agent with no memory of prior scans. If the guide is self-sufficient, you should be able to produce a validator-clean scan pair that structurally matches our existing zustand scan. If the guide is confusing or incomplete, note where you got stuck — that feedback is as valuable as the output.

## Scan target

- Repo: `pmndrs/zustand`
- Default branch: `main`
- Language: TypeScript
- Description: React state-management library
- Expected verdict: `caution` (C20 governance SPOF fires as Warning — no branch protection, no rulesets, no CODEOWNERS; release age ~31+ days puts it outside the 30-day Critical window)

## Context-budget note

You have limited context. Be efficient:
- Don't read every line of every reference file — skim structure, read details only where needed.
- For Phase 2, batch parallel gh api calls where possible.
- The zustand codebase is small (143 files, 2.2 MB) — manageable.
- For Phase 4, use fd.html as structural reference but write SHORTER than fd (zustand has fewer findings).

## Reporting back

After you finish (or if you get stuck), report:
1. Files produced and their line counts
2. Validator exit status on both
3. Where the Operator Guide was clear vs confusing
4. Where you had to make a judgment call the guide didn't cover
5. Total gh api calls made
6. Whether you wrote a findings-bundle.md and where

Begin by reading the Operator Guide, then execute Phase 1.
