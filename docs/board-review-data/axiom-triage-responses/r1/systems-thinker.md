codex
**Fix Now**

- `V1 XSS in HTML reports` — **ADOPT**. This is the clearest structural trust failure. The scanner renders adversarial repo content into HTML; validator-only structure checks are not a security boundary.
- `V2 Path traversal via tar extraction` — **ADOPT**. Even if GitHub tarballs are usually safe, the boundary is still untrusted input. One-person distribution lowers exposure, not severity.
- `V3 Symlink attack / host-file disclosure` — **ADOPT**. This is a system-boundary issue, not a cosmetic bug. Any tool that reads attacker-controlled repos must normalize or strip links.
- `V5 SHA truncation` — **ADOPT**. This weakens the stated immutability model. If you claim commit pinning, use the full SHA.
- `O1 LLM should orchestrate, not reimplant` — **ADOPT, with modification**. Right direction, wrong absolutism. For a zero-install tool, the core should remain usable with `gh` + public APIs; optional installed tools can enrich results, not define the product.
- `O4 Single CSS source of truth` — **ADOPT**. Known drift proves the current architecture already split canonical design state.

**Fix Next**

- `V4 Shell injection via unquoted variables` — **ADOPT**. The audit overstates exploitability because variables are LLM-constructed, not direct user input. Still worth fixing: quote everything for robustness and prompt-failure containment.
- `B1 CSS drift` — **ADOPT**. Real bug, but not an architectural blocker given the file split was already known.
- `B2 PR count logic wrong` — **ADOPT**. This affects credibility and sampling disclosure.
- `B3 Markdown validator claim is false` — **ADOPT**. Documentation/assurance bug; fix wording or add an actual MD validator.
- `B4 Missing referenced artifacts` — **ADOPT**. Packaging integrity issue.
- `B5 Path B contradictions` — **REJECT as stated / ADOPT doc cleanup**. The stale-guide claim is valid, but the finding is obsolete because Path B was exercised. Treat as documentation debt, not current product contradiction.
- `B6 Step 8 prerequisites undeclared` — **ADOPT**. Important because environment mismatch causes silent failure modes.
- `W1 1078-line prompt too long` — **ADOPT**. This is the main systems reliability issue after boundary hardening.
- `W2 Rate-limit exhaustion` — **ADOPT**. Needs budgeting/sampling controls before scanning larger repos becomes dependable.
- `W4 Dependabot alerts require admin scope` — **ADOPT**. Coverage collapse on common permission models is a real capability gap.
- `W6 Scorecard thresholds too rigid` — **ADOPT**. Precision is higher than the data quality justifies.
- `W7 Manual pre-render checklist` — **ADOPT**. Manual gates are weak operationally in LLM-run flows.
- `O2 Reduce 12 design rules to 5 hard rules` — **ADOPT**. Good reliability trade.
- `O3 Move changelog out of prompt` — **ADOPT**. Cheap prompt-quality win.

**Defer**

- `W3 /tmp is volatile` — **DEFER**. Real, but acceptable for a one-operator test tool until checkpointing matters operationally.
- `W5 Exhibit rollup trigger unreliable` — **DEFER**. Presentation fragility, not core scanner correctness.
- `O5 JSON-first evidence -> template` — **DEFER**. Already correctly deferred to `v3.0`; no reason to reopen that board decision now.

**Reject**

- No major item should be fully discarded, but some audit framing is too strong:
- `UNANIMOUS REWORK` — **REJECT as the headline**. The product does not need a full rework. It needs boundary hardening now and architectural tightening next. “Conditional release block pending hardening” would be more accurate.
- `V4 as critical shell injection` — **REJECT at critical severity**. Keep the fix, drop the threat inflation.
- `B5 as a live product contradiction` — **REJECT**. It is stale documentation, not evidence Path B is unproven.

**Capability Items**

**Fix Next**
- `1 OSSF Scorecard integration` — **ADOPT**. Best immediate leverage.
- `2 Rate-limit awareness + budget` — **ADOPT**. Core operational control.
- `3 Dependency vuln fallback` — **ADOPT**. Needed when Dependabot is unavailable.
- `4 Secrets-in-history scanning` — **ADOPT**. High-value complementary signal.
- `5 Unauthenticated fallback mode` — **ADOPT**. Good resilience for zero-install positioning.
- `6 SBOM generation` — **ADOPT**. Useful, low-friction expansion.
- `7 Release signature verification` — **ADOPT**. Valuable, but after boundary fixes.

**Defer**
- `8 deps.dev cross-reference` — **DEFER**. Nice enrichment, not foundational.
- `9 Fork divergence analysis` — **DEFER**. Useful for maturity/governance, not scanner viability.
- `10 Fake-star burst detection` — **DEFER**. Differentiator, not core trust.
- `11 Reclaimed-username detection` — **DEFER**.
- `12 Tampered commit timestamps` — **DEFER**.
- `13 Binary entropy analysis` — **DEFER**.
- `14 Safer alternative recommendations` — **DEFER**.
- `15 SARIF output` — **DEFER**. Valuable for integration, but not for the current non-technical narrative-first use case.

**Direct Answers**

`UNANIMOUS REWORK` is not the right governance label. The concept is architecturally sound. The current state is better described as: release-blocking hardening required, then incremental architecture cleanup.

`O1` is directionally right, but only if interpreted correctly. For a zero-install tool, “orchestrate not reimplant” should mean:
- use built-in `gh` and free/public APIs by default,
- optionally consume installed tools when present,
- keep LLM value in synthesis, cross-domain judgment, and narrative reporting.

If O1 is read as “make this dependent on installed specialist tools,” then it conflicts with the zero-install value proposition. If read as “stop using the LLM to manually emulate everything tools or APIs already expose,” then it is the right architectural move.
tokens used
