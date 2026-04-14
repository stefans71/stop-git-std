# stop-git-std — Roadmap

## MVP (Done — PR #2)

- CLI: `bun run src/cli.ts <repo> --format terminal`
- 11-phase pipeline (runtime validation no-op)
- 6 universal analyzers, 7 typed analyzers (regex-based, AST rules stubbed at low confidence)
- 3-axis scoring (trustworthiness, exploitability, abuse_potential) with /10 divisor
- Policy engine: strict/balanced/advisory profiles, hard-stop rules
- Output: terminal, JSON, markdown, SARIF
- Suppressions: `.stop-git-std.suppressions.yaml`
- Terminal reporter: color-coded score bars, risk explanations, remediation per finding
- Tested on 6 real repos (Express, FrontierBoard, onecli, gstack, Google WS CLI, self-audit)

## Board Review Results (2026-04-14)

3-model board review (Claude Opus 4.6, Codex GPT-5.2, DeepSeek V3.2) — unanimous findings:
- Detection accuracy: **2/5** — universal analyzers work, typed analyzers produce 37% false positives
- Scoring calibration: **3/5** — math correct, false positives corrupt inputs
- Actionability: **1/5** — 4/6 repos get ABORT with zero remediation guidance
- Tool got **2/6 decisions right** (Express, onecli). 4/6 too aggressive.
- Full report: `board-review-data/BOARD-FINAL-RECOMMENDATION.md`

## P0 — Detection Accuracy Fixes (next — board-mandated)

### DR1: Hard-stop confidence gating
- Hard-stop rules must check confidence >= medium before triggering ABORT
- Low-confidence regex stubs downgraded to HIGH findings with constraints
- Fixes: Google WS CLI (ABORT→CAUTION), self-audit (ABORT→PROCEED), gstack partial

### DR2: ABORT remediation paths
- Generate constraints for ALL decisions including ABORT
- Per-finding remediation steps + "re-run after fixing" instruction
- Every ABORT becomes actionable, not a dead end

### DR3: Typed analyzer false positive reduction
- Skip non-code files (.md, .yaml, .json, test files) in typed analyzers
- Eliminates ~80% of typed analyzer false positives
- Fixes: FrontierBoard (CAUTION→PROCEED), self-audit FP count drops from 11 to ~2

### DR4: .env.example distinction
- Files ending in `.example` get severity=info, confidence=low

### Plain-English output
- New "What This Means" section in terminal report
- Translates every finding into lay-person language: "here's what could actually happen"
- Sits between decision and technical scores

### Staged scanning architecture (Stage 1 → Stage 2)
- Stage 1 (current): fast static regex scan with confidence levels
- When low-confidence findings would trigger hard-stop: recommend deeper analysis
- Stage 2 modules (designed, built later): AST (tree-sitter), sandbox execution
- Terminal output shows what deeper analysis would verify
- CLI: `--no-stage2` to suppress recommendations

Expected outcome: decision accuracy **2/6 → 5/6** after DR1-DR3.

## P1 — Detection Depth (Stage 2 modules)

### AST/tree-sitter analysis
- Verifies whether flagged patterns are in executable code vs docs/comments/strings
- Upgrades typed analyzer confidence from "low" to "high" when confirmed
- Dismisses findings when pattern is in documentation or string literals
- Priority: GHA-AI-001, GHA-AGENT-001, GHA-MCP-001

### Sandbox execution (runtime validation)
- Runs install/build in isolated container
- Captures: network connections, file writes, process spawns, env access
- Confirms or dismisses GHA-EXEC-001 (curl|bash), GHA-EXEC-002 (install hooks)
- Docker/Bun sandbox, no network after initial download

### OSV dependency vulnerability scanning
- Replace stub with real OSV.dev API queries
- Biggest detection gap identified by board — no dependency CVE detection currently
- Direct dependency scanning per ecosystem

## P2 — Usability & Storage

### Audit history / SQLite storage
- Each run persisted: repo URL, ref, date, scores, decision, finding count
- `stop-git-std history` — list past audits
- `stop-git-std compare <run-id-1> <run-id-2>` — diff two audits of same repo

### Web UI dashboard
- Local web interface: `stop-git-std serve`
- Score trends over time, finding drill-down, side-by-side comparison

## P3 — Integration

### GitHub Action
- PR annotations from SARIF findings
- Check runs with pass/fail status
- Auto-comment on PRs with audit summary

### GitHub API enrichment
- Repo metadata: archived status, stars, activity, contributor count
- Release history for signed tag verification

## P4 — Extensibility

### Python subprocess analyzer backend
- Enable Python-based deep analysis via plugin interface
- Taint/dataflow analysis for Python repos

### Multi-repo dependency graph
- Audit entire dependency trees
- Transitive risk scoring

### Attestation and provenance verification
- SLSA/Sigstore verification for supply chain
