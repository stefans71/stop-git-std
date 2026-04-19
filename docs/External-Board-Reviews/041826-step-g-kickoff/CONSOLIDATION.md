# CONSOLIDATION — Step G Kickoff / U-1 Documentation Integration

**Dates:** 2026-04-18 (R1) → 2026-04-19 (R2, R3 applied + confirmation)
**Reviewed:** U-1 approach + commits `60e0bf2` (FX-3b parallel — package validator sync) + `6a3e471` (U-1 — V2.5-preview docs integration)
**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
**Rounds:** R1 Blind → R2 Consolidation → R3 Confirmation (3-round SOP; narrower scope than Step F's 4-round, no deliberation needed since R2 converged)
**Board:** Pragmatist (Claude Sonnet 4.6), Systems Thinker (Codex GPT-5 as llmuser from /tmp), Skeptic (DeepSeek V4 via qwen -y --model deepseek-chat from repo dir)

---

## Final verdict

**SIGN OFF.** U-1 shipped. Step G may proceed once the remaining pre-Step-G queue (U-3/FX-4, U-5/PD3, U-10) is addressed.

| Agent | R1 | R2 | R3 |
|---|---|---|---|
| Pragmatist | SIGN OFF W/ DISSENTS (4 FIX NOW) | SIGN OFF (upgrade — all 4 resolved) | **SIGN OFF** |
| Codex | SIGN OFF W/ DISSENTS (4 FIX NOW + defer-ledger ask) | SIGN OFF W/ DISSENTS (all 11 SECOND + schema hardening added to ledger) | **SIGN OFF W/ DISSENTS** (non-blocking: terminology debt + schema watch) |
| DeepSeek | SIGN OFF W/ DISSENTS (3 splits) | SIGN OFF W/ DISSENTS (2-1 losses on env var + FX-3b timing) | **SIGN OFF W/ DISSENTS** (non-blocking: env-var preference + U-10 ordering) |

---

## What shipped (commits `60e0bf2` + `6a3e471`)

### Commit 1: FX-3b parallel (`60e0bf2`, 1 file)
Sync of `FX-3` + `FX-3b` validator fixes from repo to `github-scan-package-V2/validate-scanner-report.py`. Closes a real V2.4 bug where the package validator's `/\*.*?\*/` global comment-strip mangled shell globs and code comments in evidence text, eating finding cards (demonstrated on caveman shape). Package validator now byte-identical to repo validator.

**Validation evidence (DeepSeek R2-directed):**
- Repo-vs-package diff: 0 lines
- Package `--report` + `--parity` on V2.4 reference zustand: clean, 6 finding IDs matched
- Package `--report` + `--parity` on V2.5-preview zustand render: clean, 6 finding IDs matched
- Package `--parity` on caveman shell-glob case: clean, 9 finding IDs matched
- Zero errors, zero warnings all three cases

### Commit 2: U-1 documentation integration (`6a3e471`, 5 files, 237/73 insertions/deletions)

**CLAUDE.md** — Q2 wizard renamed `Path A/B` → `Execution mode: continuous / delegated`. Q3a added for rendering pipeline `V2.4` vs `V2.5-preview (Step G only)`. CSS line count 816 → 824. MD-canonical rule extended to both pipelines. Repo structure + current state sections updated. Board reviews pointer modernized.

**docs/SCANNER-OPERATOR-GUIDE.md** — §8.1/§8.2 section headers renamed. §8.4 self-contradiction resolved (Codex R1 catch). §8.8 new subsection authored with 7 parts:
- Triple-warning gate (Codex R1 FIX NOW) at the top
- 8.8.1 status / 8.8.2 workflow
- 8.8.3 phase-to-prompt mapping TABLE + 8-step operator checklist (Pragmatist R1 FIX NOW)
- 8.8.4 invariants preserved
- 8.8.5 Step G success criterion including structural-parity vs V2.4 scan (Pragmatist R1 FIX NOW)
- 8.8.6 rollback contract: V2.4 continues, V2.5-preview quarantined, failed fixtures tagged, package untouched, schema revision separate cycle
- 8.8.7 known limitations including schema-hardening defer-ledger (Codex R2 explicit ask)

**docs/Scan-Readme.md** — V2.3 → V2.4 top-line. Step 3 renamed to Execution mode. Step 4a added for rendering pipeline. Legacy "V2.3 prompt (1078 lines)" references revised. Files + catalog blocks expanded for V2.5-preview.

**docs/repo-deep-dive-prompt.md** — Single blockquote at §"Markdown file structure" framing both pipelines as implementations of the same output-format spec. Minimal touch per unanimous R1 vote.

**docs/scanner-catalog.md** — New `rendering-pipeline` column (all 10 entries `v2.4`). Methodology column annotated with canonical continuous/delegated. Changelog entry for 2026-04-19.

---

## Split resolutions

### 5.1 — FX-3b timing
- Pragmatist + Codex: parallel commit before U-1 (**won 2-1**)
- DeepSeek: blocks U-1, sequential-with-test
- **Resolution:** Parallel commit (`60e0bf2` first), with validation step executed between commits per DeepSeek's hygiene ask. Both commits land before any Step G scan.

### 5.2 — Gating mechanism
- Pragmatist + Codex: three warnings + shape-coverage + "Last reviewed" date, no env var (**won 2-1**)
- DeepSeek: environment variable `STOP_GIT_STD_EXPERIMENTAL=1`
- **Resolution:** Triple-warning gate adopted. DeepSeek's env var rejected as overkill for the project's operator profile (LLMs + technically fluent humans). DeepSeek carried concern as trailing dissent, non-blocking.

### 5.3 — Scan-Readme.md scope
- All three: include Scan-Readme.md in U-1 scope with snippet authored now (**unanimous**)

---

## Unblocked items disposition

| ID | Item | R2 Vote | R3 Confirmed | Status |
|---|---|---|---|---|
| U-1 | V2.5-preview doc integration | APPLY THIS REVIEW (3-0) | Yes | ✅ Applied `6a3e471` |
| U-2 | Parity regex extension | APPLIED IN STEP F (prior) | — | Completed in `ce698d4` |
| U-3/FX-4 | Fixture provenance (separate file) | APPLY NEXT COMMIT (3-0) | Yes, queued | Before Step G runs / before Step G fixtures authored |
| U-4 | CSS autoescape doc comment | APPLIED IN STEP F (prior) | — | Completed in `ce698d4` |
| U-5/PD3 | Bundle/citation validator | APPLY NEXT COMMIT (2-1 NEXT over DEFER-with-criterion) | Yes, queued | Before first live Step G `findings-bundle.md` |
| U-6 | Template-source `\| safe` lint | DEFER post-Step-G (3-0) | Yes | Deferred |
| U-7 | `formal_review_rate` phase reclassification | DEFER post-Step-G (3-0) | Yes | Deferred |
| U-8 | Externalize `adjustFont` script | DEFER post-Step-G (3-0) | Yes | Deferred |
| U-9 | Duplicated prose fields in Phase 4 | DEFER post-Step-G (3-0) | Yes | Deferred |
| U-10 | Re-validate all 10 catalog scans | ADJUST per R3 Codex — before first V2.5-preview promoted to catalog (tightens DeepSeek's R2 "before Step G runs") | Yes, queued | Before first V2.5-preview catalog entry |
| FX-3b | Package validator sync | APPLY PARALLEL (2-1 over blocks-U-1) | Yes | ✅ Applied `60e0bf2` |

---

## Prior-roadmap deferred items

All 11 items (RD1, SD2, RD4, SD3, SD4, SD7, SD8, SD9, SD10, RD5, PD1/4/6/7) unanimously CONFIRM DEFER across R2 + R3. No automation triggers have fired.

**Codex R2 added to defer ledger:**
- **Schema hardening** — `docs/scan-schema.json` V1.1 does not yet fully formalize the prompt contract. Specific gaps: Scanner Integrity section 00 hit-level file/line/raw-content structure; Section 08 methodology fields beyond the currently modeled version marker. Recorded in §8.8.7 of the Operator Guide. Not a U-1 blocker; active watch item for Step G.

---

## Verification evidence (R3-confirmed, independently reproducible)

Re-run command:
```bash
cd /root/tinkering/stop-git-std
python3 -m pytest tests/ -q | tail -2
for f in zustand caveman archon-subset; do
  python3 docs/render-html.py tests/fixtures/$f-form.json --out /tmp/$f.html > /dev/null
  python3 docs/render-md.py tests/fixtures/$f-form.json --out /tmp/$f.md > /dev/null
  echo "--- $f ---"
  python3 docs/validate-scanner-report.py --report /tmp/$f.html | tail -1
  python3 docs/validate-scanner-report.py --parity /tmp/$f.md /tmp/$f.html | tail -1
done
diff docs/validate-scanner-report.py github-scan-package-V2/validate-scanner-report.py | wc -l
wc -l docs/scanner-design-system.css
```

Observed at commit time:
- pytest: **263 passed in 40.33s**
- All 3 `--report`: `✓ is clean.`
- All 3 `--parity`: `✓ Parity check clean — MD and HTML are structurally consistent.`
- Repo-vs-package validator diff: **0 lines**
- CSS line count: **824**

---

## Trailing dissents (carried into Step G awareness, not blockers)

### From Pragmatist R3
1. **Provenance.json ordering discipline** — U-3/FX-4 should land before any Step G form.json is authored, not merely before Step G "runs." If fixture authoring starts without provenance.json in place, the first live form.json is machine-untaggable retroactively.
2. **Catalog dual-labeling cosmetic** — `methodology-used: path-a (continuous)` could read ambiguously; column note resolves if read but column notes get skipped. Noted, not carried.

### From Codex R3
1. **Terminology debt** — Operator Guide §8.1/§8.2 body prose still contains legacy "Path A/Path B" mentions in explanatory text. The collision is resolved in wizard/operator-choice text (the actual R1 issue); lingering prose is cleanup, not bug.
2. **Schema hardening watch** — Per §8.8.7, Scanner Integrity §00 + §08 methodology gaps are active watch items during Step G.

### From DeepSeek R3
1. **Env-var gating preference** — Still believes env var would be stronger than triple-warning. Accepts adequacy given experimental nature.
2. **U-10 timing** — Must execute before any V2.5-preview scan enters catalog (already queued; timing discipline noted).
3. **Shape coverage limitation** — Properly documented in §8.8.0.

All three dissent sets are documentation-level Step G awareness items, not blockers.

---

## Process notes

- **3-round SOP sufficient** (no R4 needed) because R2 converged on direction unanimously; R3 was narrow confirmation of applied state.
- **Fix-artifact-first pattern** (owner authors snippets, board votes SECOND/ADJUST/REJECT) worked again, as in Step F. Pragmatist R3 called this out in Step F; the R2 brief's §4 owner-revised-items block formalizes it further.
- **Parallel commit with validation step** resolved the FX-3b 2-1 split elegantly: satisfies P+C's "parallel" preference while absorbing DeepSeek's "validation step" requirement. Worth encoding as a split-resolution pattern in SOP.
- **DeepSeek API transient "Connection error"** on R1 first attempt; retry succeeded (per memory: known pattern, retry once). Non-blocking.
- **Package drift audit** surfaced meaningful drift that would not have been noticed without this review (operator guide byte-identical, validator 16-line drift, Scan-Readme 102-line drift). Pattern worth institutionalizing before future package releases.

---

## Agent invocation reference (for future reruns)

**Pragmatist (Sonnet 4.6):**
```
Agent tool with subagent_type="general-purpose", model="sonnet", run_in_background=true
```

**Systems Thinker (Codex GPT-5 via llmuser from /tmp):**
```bash
sudo -u llmuser bash -c "cd /tmp && codex exec --dangerously-bypass-approvals-and-sandbox '<prompt>'"
```

**Skeptic (DeepSeek V4 via Qwen CLI from repo dir):**
```bash
OPENAI_API_KEY="$DEEPSEEK_API_KEY" OPENAI_BASE_URL="https://api.deepseek.com/v1" \
  qwen -y -p "<prompt>" --model deepseek-chat
```

---

## Files in this folder

- `r1-brief.md`, `r2-brief.md`, `r3-brief.md` — per-round briefs
- `{pragmatist,codex,deepseek}-r{1,2,3}.md` — 9 per-agent responses
- `CONSOLIDATION.md` — this file

---

## References

- Commits under review: `60e0bf2` (FX-3b parallel) + `6a3e471` (U-1)
- Parent: `../041826-renderer-alignment/CONSOLIDATION.md` (7-step plan A→G)
- Step F: `../041826-step-f-alignment-validation/CONSOLIDATION.md` (Step F + Step G readiness review that queued U-1)
- Step F record: `../041826-renderer-impl-verify/STEP-F-verification.md`
- FrontierBoard SOP: `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`
