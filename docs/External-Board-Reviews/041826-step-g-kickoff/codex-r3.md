### Verdict
SIGN OFF WITH DISSENTS

### Commit-by-commit confirmation
`60e0bf2` matches R2 approval. It is correctly isolated as the FX-3b/FX-3 package-validator sync, removes the unsafe global `/* ... */` strip in `check_parity`, adds the explanatory note, adds the H3 Pattern 3 matcher, and keeps scope limited to `github-scan-package-V2/validate-scanner-report.py`.

`6a3e471` matches R2 approval. It applies the approved U-1 docs integration across the expected 5 files, resolves the R1 naming collision by moving user-facing text to `continuous` / `delegated`, adds the prompt cross-reference, strengthens the Step G gating in `CLAUDE.md`, `docs/SCANNER-OPERATOR-GUIDE.md`, and `docs/Scan-Readme.md`, fixes §8.4 so the prompt remains canonical while schema/renderers are implementations, and records the deferred schema-hardening item in both §8.8.7 and the catalog changelog.

### Q1-Q8 answers
Q1: The hybrid sequence is acceptable. R2 required the FX-3b fix to land separately and DeepSeek’s additional hygiene ask was validation before U-1; the applied sequence does both. `60e0bf2` is atomic and narrowly scoped, and `6a3e471` follows after the validator-sync confirmation described in the commit message. That matches the approved direction.

Q2: The name-collision resolution is correct as applied. User-facing operator language now distinguishes the two axes cleanly: execution mode is `continuous` / `delegated`, while rendering pipeline is `V2.4` / `V2.5-preview`. Retaining legacy `path-a` / `path-b` only in historical/catalog contexts is the right compromise. I do not want a hard break on catalog flags in this commit.

Q3: §8.8 is complete against the requested checklist. I verified the triple-warning gate, status, workflow, mapping table, invariants, Step G success criterion, rollback contract, and known limitations. The mapping table includes all 8 form phases: `phase_1_raw_capture`, `phase_2_validation`, `phase_3_computed`, `phase_4_structured_llm`, `phase_4b_computed`, `phase_5_prose_llm`, `phase_6_assembly`, `scan_sign_off`. The rollback section explicitly includes package non-mutation, failed-artifact tagging, and separate schema revision. §8.8.7 explicitly carries the defer-ledger item for Scanner Integrity section 00 hit-level structure and Section 08 methodology fields.

Q4: Minimal-touch prompt cross-reference is achieved. The only prompt change is the inserted blockquote at the markdown-structure boundary. It cleanly states that both pipelines realize the same canonical output-format spec and does not rewrite the substantive prompt sections themselves.

Q5: The old `Scan-Readme.md` reference Pragmatist flagged is gone. I spot-checked for the stale `V2.3 prompt (1078 lines)` wording and it no longer exists. The file now references `docs/repo-deep-dive-prompt.md` as the V2.4 investigation prompt plus output-format spec, which is the correct replacement.

Q6: The catalog’s dual-labeling is acceptable and, in this transition window, more helpful than confusing. `methodology-used: path-a` / `path-b` remains the durable historical flag, while `(continuous)` / `(delegated)` gives the canonical current meaning inline. A footnote-only approach would be leaner, but for R3 confirmation I would keep the current dual-labeling because it reduces ambiguity during the rename.

Q7: The next-commit queue is still intact. `6a3e471` explicitly keeps U-3/FX-4, U-5/PD3, and U-10 queued before Step G runs, and nothing material from the R2 queue appears silently dropped or pulled into this commit. Scope discipline is preserved.

Q8: I do not see a new defect that would justify reopening. The only residual concern is stylistic/cleanup, not blocking: the Operator Guide still contains legacy “Path A/Path B” mentions inside explanatory prose for §8.1/§8.2, but the collision is resolved in wizard/operator-choice text, which was the actual R1 issue. `Scan-Readme.md` no longer uses Path A/B as the active choice vocabulary, and catalog flag values remain intentionally preserved.

### Trailing dissents
I am carrying one dissent into Step G awareness: the docs still mix legacy and canonical terminology in some explanatory prose, especially inside `docs/SCANNER-OPERATOR-GUIDE.md` §8.1/§8.2. That is no longer a collision bug, but it is still terminology debt. I would not block Step G on it.

I am also carrying the R2 schema concern as an active watch item, not a blocker: §8.8.7 correctly records Scanner Integrity section 00 hit-level structure and Section 08 methodology fields as deferred schema hardening, so Step G should treat that as known debt rather than settled design.
