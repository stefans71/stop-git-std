# stop-git-std — Roadmap

## MVP (Done — PR #2 merged)

- CLI: `bun run src/cli.ts <repo> --format terminal`
- 11-phase pipeline (runtime validation no-op)
- 6 universal analyzers, 7 typed analyzers (regex-based, AST rules stubbed at low confidence)
- 3-axis scoring (trustworthiness, exploitability, abuse_potential) with /10 divisor
- Policy engine: strict/balanced/advisory profiles, hard-stop rules
- Output: terminal, JSON, markdown, SARIF
- Suppressions: `.stop-git-std.suppressions.yaml`

## P0 — Usability (required before real use)

### Terminal reporter improvements
- Color-coded scores (green 0-20, yellow 21-50, orange 51-75, red 76-100)
- Score range labels (Low / Moderate / Elevated / Critical)
- Findings grouped by axis in a matrix view
- Decision explanation (not just "no thresholds exceeded")
- Progress output during long scans

### Audit history / storage
- SQLite database for storing audit results
- Each run persisted: repo URL, ref, date, scores, decision, finding count
- `stop-git-std history` — list past audits
- `stop-git-std compare <run-id-1> <run-id-2>` — diff two audits of same repo
- Reports saved to `~/.stop-git-std/reports/<repo>/<date>/`

### Web UI dashboard
- Local web interface: `stop-git-std serve`
- Audit history with search/filter
- Score trends over time per repo
- Finding drill-down with evidence
- Side-by-side comparison of audits
- Export to markdown/PDF

## P1 — Detection depth

### Runtime validation (sandboxed execution)
- 3 runtime rules: credential path reads, unexpected network, download-then-exec
- Includes 2 hard-stop rules (GHA-RUNTIME-001, GHA-RUNTIME-003)
- Docker/Bun sandbox for install/build/smoke
- Network observation, filesystem observation, process observation

### AST/tree-sitter for Python + TypeScript
- Upgrades 15+ typed analyzer rules from "low confidence regex" to real detection
- Sink detection, route extraction, dataflow analysis
- Confidence upgrades from "low" to "high" for AST-backed rules

## P2 — Integration

### GitHub Action
- `action.yml` exists (stub), needs testing + marketplace publishing
- PR annotations from SARIF findings
- Check runs with pass/fail status
- Auto-comment on PRs with audit summary

### OSV API (real HTTP)
- Replace stub with real vulnerability queries
- Direct dependency scanning per ecosystem
- Advisory severity mapping to findings

### GitHub API enrichment
- Repo metadata: archived status, stars, activity, contributor count
- Release history for signed tag verification
- Rate limiting + graceful degradation without GITHUB_TOKEN

## P3 — Extensibility

### Python subprocess analyzer backend
- Plugin interface exists (stub). Enable Python-based deep analysis.
- Taint/dataflow analysis for Python repos
- Custom analyzers via Python scripts

### Multi-repo dependency graph
- Audit a repo's entire dependency tree
- Transitive risk scoring
- "This repo depends on 3 repos that would ABORT"

### Attestation and provenance verification
- SLSA/Sigstore verification for supply chain
- Build provenance checks
- Signed release verification beyond just tags
