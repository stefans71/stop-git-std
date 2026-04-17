1. **HOLD UPGRADE** — Volatile /tmp usage is a genuine security risk that contradicts zero-install’s reliability principle.  
2. **HOLD CLOSE** — Scorecard thresholds are out of scope; we shouldn’t add complexity for external scoring tools.  
3. **CHANGE to UPGRADE** — Stale text creates confusion; aligning with both others improves clarity without new dependencies.  
4. **HOLD UPGRADE** — Secrets in history is a real risk, and “KEEP DEFER”/“CLOSE” ignore a tangible threat.  
5. **HOLD KEEP DEFER** — SBOM endpoint depends on external tooling; deferring keeps zero-install intact for now.  
6. **HOLD UPGRADE** — Release signature verification is critical for supply chain security, even if it complicates zero-install.  
7. **CHANGE to CLOSE** — deps.dev can be covered by existing Scorecard checks; no need for separate capability.  
8. **CHANGE to KEEP DEFER** — Fork divergence is useful but not urgent; deferring aligns with the group majority.  
9. **HOLD CLOSE** — Binary entropy checks require new tool dependencies, contradicting zero-install.  
10. **HOLD CLOSE** — “Safer alternatives” is too vague and risks scope creep without concrete criteria.  
11. **CHANGE to CLOSE** — SARIF output adds complexity for niche use cases; not essential for core security scanning.  

**Final tracked items count:** 7 tracked items (5 DEFER + 2 FIX NEXT) is reasonable—it balances addressing key issues without overloading the roadmap.
