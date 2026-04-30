codex
1. `W3 /tmp volatile` — `HOLD (CLOSE)`: the issue is environment-specific and `/tmp` volatility is expected behavior, so I don’t see a product-level action.  
2. `W6 Scorecard thresholds` — `CHANGE to CLOSE`: threshold tuning without evidence of a concrete decision error feels like methodology churn, not a tracked finding.  
3. `B5 Path B stale text` — `HOLD (UPGRADE)`: stale user-facing text on an alternate path is still a correctness issue because it can mislead operators even if the path is secondary.  
4. `Cap-4 Secrets-in-history` — `CHANGE to UPGRADE`: if secrets may exist in git history, the blast radius is high enough that “not currently exposed” is not a sufficient reason to close.  
5. `Cap-6 SBOM endpoint` — `CHANGE to KEEP DEFER`: this is useful capability work, but without a clear compliance or customer requirement it should stay deferred rather than closed or upgraded.  
6. `Cap-7 Release sig verify` — `CHANGE to KEEP DEFER`: release-signature verification is meaningful supply-chain hardening, but it still reads as roadmap work unless there is evidence of active distribution risk.  
7. `Cap-8 deps.dev` — `CHANGE to UPGRADE`: independent dependency reputation/supply-chain checking adds defense-in-depth and should not be dismissed just because `W4` may cover adjacent ground.  
8. `Cap-9 Fork divergence` — `HOLD (KEEP DEFER)`: fork divergence matters, but it is a governance/maintenance signal rather than a direct defect unless it is already causing missed fixes.  
9. `Cap-13 Binary entropy` — `CHANGE to KEEP DEFER`: it is a weak standalone signal, but as a lightweight detection capability it is more “defer” than “close.”  
10. `Cap-14 Safer alternatives` — `HOLD (CLOSE)`: suggesting safer alternatives is good advisory material, but by itself it is not a discrete issue to track.  
11. `Cap-15 SARIF output` — `HOLD (MERGE→O1)`: SARIF is an output-format enhancement and belongs under the broader reporting/output workstream rather than as a separate tracked item.

`7 tracked items` seems right if the goal is a tight final set with only clearly actionable work; I would keep `5 DEFER + 2 FIX NEXT` unless your process requires breaking out capability items more explicitly.
