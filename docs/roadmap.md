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

Stage 2 is triggered automatically when Stage 1 flags low-confidence findings that would trigger hard-stop rules. The P0 work builds the escalation framework and recommendation output; P1 builds the actual analysis modules.

### AST/tree-sitter analysis module
- **Purpose:** Verify whether flagged patterns are in executable code paths vs docs/comments/string literals
- **How it works:** Uses tree-sitter to parse flagged files. Walks the AST to determine if the regex match is inside a function call, string literal, comment, or markdown text. If the match is in a non-executable context (string literal in an analyzer, markdown description, test fixture), the finding is dismissed or confidence downgraded.
- **Findings it resolves:**
  - GHA-AI-001 (model→exec): Checks if `model.*exec` match is an actual function call chain or a documentation string
  - GHA-AGENT-001 (unrestricted agent): Checks if `register.*tool` is a real tool registration call or a regex pattern in analyzer code
  - GHA-MCP-001 (shell exposure): Checks if `mcp.*server` is an MCP server instantiation or a test/doc reference
  - GHA-MCP-003 (credential forwarding): Checks if credential-passing pattern is in executable code
  - GHA-EXEC-004 (unsafe deserialization): Checks if `pickle.loads`/`yaml.load` is a real call or a regex string
  - GHA-EXEC-005 (remote code fetch): Checks if `fetch()` + `eval()` co-location is in actual code flow
- **Output:** Upgrades confidence to "high" (confirmed) or dismisses finding (false positive in docs/comments)
- **Impact:** Eliminates self-audit false positives entirely. Resolves AI/agent/MCP false positives for repos like FrontierBoard and Google WS CLI.
- **Tech:** tree-sitter with TypeScript, Python, Rust, Go grammars. ~500-800 lines.

### Sandbox execution module
- **Purpose:** Verify runtime behavior of install scripts and lifecycle hooks
- **How it works:** Runs `npm install` / `pip install` / shell scripts inside a Docker container with:
  - Network monitoring (what URLs does it contact?)
  - Filesystem monitoring (what files does it write outside the project?)
  - Process monitoring (what child processes does it spawn?)
  - Environment monitoring (does it read SSH keys, AWS credentials, etc.?)
- **Findings it resolves:**
  - GHA-EXEC-001 (curl|bash): Verifies what the install script actually downloads and whether the source is trusted
  - GHA-EXEC-002 (install hooks): Captures what lifecycle hooks actually do at install time
  - GHA-RUNTIME-001 (credential path reads): Detects if the package reads `~/.ssh/`, `~/.aws/`, etc.
  - GHA-RUNTIME-003 (download-then-exec at runtime): Captures post-install download behavior
- **Output:** New findings with `proof_type: "runtime"` and high confidence behavioral evidence
- **Impact:** Turns "this script *could* be malicious" into "this script *does* contact attacker.com and writes to ~/.ssh/"
- **Tech:** Docker API + eBPF or strace for syscall capture. ~1000-1500 lines. Requires Docker on the host.
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
