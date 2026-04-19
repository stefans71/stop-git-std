### Verdict (R2)
SIGN OFF WITH DISSENTS. Unchanged from R1.

Owner addressed the core R1 architectural issues correctly. The additive strategy is still the right call, and the revised proposal is now internally coherent.

### Response to Owner-Revised Items (§4.1–4.11)

**4.1 Renaming**  
SECOND. This confirms the adopted two-axis terminology I asked for in R1. It cleanly resolves the Path A/B collision in both `CLAUDE.md` and `SCANNER-OPERATOR-GUIDE.md`.

**4.2 §8.4 wording fix**  
SECOND. This confirms the 8.4 contradiction fix from R1. The revised wording correctly makes the prompt canonical while allowing schema + renderers to be an implementation of the same contract.

**4.3 form.json authoring bridge**  
SECOND. This closes a real operator gap. The phase-to-prompt table plus checklist is the right minimum bridge.

**4.4 Path B gating**  
SECOND. This confirms the stronger gating I asked for in R1. The three-warning model in `CLAUDE.md`, Operator Guide, and `Scan-Readme.md` is sufficient for this operator profile. The added shape-coverage and “last reviewed” lines improve it further. No env var needed.

**4.5 Rollback plan in §8.8**  
SECOND. This confirms the quarantine-to-appendix rollback I asked for in R1. Keeping failed Step G artifacts out of the main operator flow is the correct containment model.

**4.6 Prompt cross-reference**  
SECOND. This confirms the prompt cross-reference fix from R1. Minimal, correct, and at the right abstraction layer.

**4.7 Catalog methodology column**  
SECOND. Necessary metadata, low risk, good separation of V2.4 vs V2.5-preview provenance.

**4.8 Structural-parity criterion**  
SECOND. This is the right addition. Validator-clean alone is not an acceptance gate for Step G.

**4.9 CSS line count fix**  
SECOND. Good hygiene. Not architectural, but worth correcting since the docs use exact counts operationally.

**4.10 FX-3b package validator sync**  
SECOND, with reason. I support the owner’s sequencing: separate parallel commit, but both commits land before any Step G scan runs. That preserves clean history without weakening operational safety.

**4.11 U-10 catalog re-validation**  
ADJUST. I support the item, but I would tighten the purpose and timing:
- Re-validate all 10 catalog artifacts with the fixed validator.
- Record which scans change status or emit materially different warnings.
- Treat this as a deferred integrity sweep, not a U-1 blocker.
- Preferred timing: after U-1 lands, before any V2.5-preview scan is promoted into the catalog as a first-class entry.

Reason: the DeepSeek concern is valid enough to queue, but not strong enough to block Step G acceptance work. This is catalog integrity follow-up, not a prerequisite for documenting the preview path.

### Resolution of Splits (§5.1–5.3)

**5.1 FX-3b timing**  
Confirm owner proposal. Separate commit, but it must land before any Step G run is treated as operationally valid. This is functionally aligned with my R1 position and absorbs DeepSeek’s sequencing concern without over-coupling the work.

**5.2 Gating mechanism**  
Confirm owner proposal. Three explicit warnings in all three docs, plus shape-coverage warning and review date, is enough. I do not support an env var. The risk here is misframing and misuse in docs, not unauthorized command execution.

**5.3 Scan-Readme.md handling**  
Confirm owner proposal. Include `docs/Scan-Readme.md` in U-1 now, with drafted snippet now. This directly addresses my R1 staleness concern. It should not be left as a post-board cleanup.

### New FIX NOW Items

None.

One non-blocking process adjustment should be recorded before R3: explicitly carry forward the schema-hardening gap as a DEFER item. My R1 concern still stands that `scan-schema.json` V1.1 does not yet fully formalize the prompt contract, especially:
- Scanner Integrity section 00 hit-level structure
- Section 08 methodology fields beyond the currently modeled version marker

That is not a U-1 blocker, but it should be named in the defer ledger so the repo does not accidentally treat V1.1 as the complete canonical schema.

### Approval for Owner to Proceed to R3

Yes.

Proceed to R3 after applying the agreed changes, with one expectation: the defer list should explicitly include schema hardening, and U-10 should be queued as a catalog integrity follow-up rather than left implicit.
