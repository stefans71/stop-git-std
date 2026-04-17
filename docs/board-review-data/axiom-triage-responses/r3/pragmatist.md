# Pragmatist — Round 3 Deliberation

## Disagreement Items (11)

### W3 — /tmp volatile
**HOLD: CLOSE.**
Skeptic wants UPGRADE. The argument presumably is that `/tmp` cleanup races are a real security issue and `mktemp -d` with a trap would fix it. I disagree — the operator guide already mandates copying findings-bundles to `docs/board-review-data/scan-bundles/` before session end. The durability guarantee comes from the workflow, not from changing the temp directory strategy. If someone loses `/tmp` data, they skipped the copy step. Adding `mktemp` + trap is a nice defensive coding practice, but it solves a problem we already solve procedurally. Not worth tracking.

### W6 — Scorecard thresholds rigid
**HOLD: CLOSE.**
Systems Thinker wants UPGRADE, arguing that with OSSF Scorecard API now live, threshold interpretation matters. Fair point in principle, but here is why I still close it: the scanner prompt already tells the LLM to synthesize narrative from scorecard data, not apply rigid cutoffs. The LLM interprets the raw scores contextually. If a specific false-positive surfaces from bad threshold interpretation, we reopen then. Tracking a theoretical problem that Cap-1's design already mitigates is backlog noise.

### B5 — Path B stale text
**HOLD: UPGRADE to FIX NEXT.**
Skeptic voted CLOSE, presumably arguing it is just docs. But contradictory operator text in Path B will cause real agent failures — Path B is the delegation path, and if the handoff packet contains stale instructions, the background agent does the wrong thing. This is a 15-minute cleanup with direct operational impact. Cheap fix, real consequence if skipped. UPGRADE stands.

### Cap-4 — Secrets-in-history (gitleaks)
**HOLD: KEEP DEFER.**
Systems Thinker wants CLOSE (too expensive, requires extra tooling). Skeptic wants UPGRADE. I split the middle deliberately. The detection is genuinely valuable for supply-chain assessment — leaked secrets in history are one of the clearest "this repo has poor security hygiene" signals. But it requires gitleaks/trufflehog installation, which violates our zero-install constraint. DEFER is correct: we track it for when GitHub exposes secret-scanning results via API for public repos. Not closeable because the signal matters. Not upgradeable because we cannot implement it today.

### Cap-6 — SBOM endpoint
**HOLD: KEEP DEFER.**
Systems Thinker wants CLOSE. GitHub's `/dependency-graph/sbom` endpoint exists and returns SPDX data. Coverage is spotty today but improving. When it works, it gives us a machine-readable dependency inventory for free. This is a "check back in 6 months" item, which is exactly what DEFER means.

### Cap-7 — Release sig verification
**HOLD: KEEP DEFER.**
GitHub is building attestation verification into `gh` CLI — `gh attestation verify` already exists in beta. When that stabilizes, this becomes a one-liner. DEFER is the right holding pattern.

### Cap-8 — deps.dev cross-reference
**HOLD: CLOSE.**
W4 (osv.dev fallback) already landed. deps.dev adds marginal metadata value. Clean CLOSE.

### Cap-9 — Fork divergence
**HOLD: KEEP DEFER.**
Fork divergence is a distinct detection vector. Keep as standalone DEFER.

### Cap-13 — Binary entropy analysis
**CHANGE: CLOSE.**
Both others voted CLOSE. Existing executable inventory already flags unexpected binaries. Marginal signal doesn't justify tracking.

### Cap-14 — Safer alternative recommendations
**CHANGE: CLOSE.**
Both others voted CLOSE. Scanner assesses trustworthiness, not recommends alternatives. Valid scope boundary.

### Cap-15 — SARIF output
**HOLD: CLOSE.**
Zero users asking. If JSON-first lands, SARIF is a trivial transform. Not a separate tracked item.

## Final count: 7 tracked items (5 DEFER + 2 FIX NEXT). Correct number.
