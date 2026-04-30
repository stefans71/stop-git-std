# External Board Review Brief — Scanner Structural Questions

**Date:** 2026-04-17
**Prepared by:** Scanner development team (Scott + Claude Opus 4.6)
**For:** External 3-model governance board review
**Review type:** Architectural decision review (not a scan review)

---

## Background

This is a GitHub repo security scanner that uses an LLM + `gh` CLI to investigate repos and produce HTML + MD security reports. It is NOT a static analyzer — the LLM does the investigation, synthesizes findings, and renders reports.

**Current state:**
- 8 completed scans across different repo shapes (JS library, Rust CLI, agentic platform, Claude Code skills distribution, web application, etc.)
- V2.3 investigation prompt (1,078 lines) + V0.1 operator guide (552 lines) + HTML template + validator
- 3 prior board reviews on the internal team (prompt V2.3, operator guide V0.1, zustand v1-vs-v2 comparison)
- Distribution package available (209 KB zip, 13 files)

**The scanner works** — 8 repos scanned, findings are accurate, reports pass validation. The questions below are about what's MISSING from the process, not what's broken.

---

## Two questions for the board

### Q1: Should a repo-classification-to-investigation-emphasis matrix exist?

#### The problem

When an operator starts a scan, they must decide what to investigate deeply vs superficially. Currently this decision is **implicit** — the operator looks at the repo, recognizes a "shape" (library, CLI, platform, skills package), and emphasizes different investigation branches based on pattern memory.

This produces inconsistency:
- 8 scans, 8 slightly different investigation depths
- A JS library scan (zustand) emphasizes npm lifecycle hooks; a Rust CLI scan (fd) emphasizes binary attestation; a web app scan (postiz-app) emphasizes Docker defaults and CVE history — but WHICH investigation branches are mandatory for WHICH shapes is nowhere written down
- New operators (or fresh LLM agents) must guess what to emphasize

#### What a classification matrix would look like

A YAML file that maps repo characteristics → mandatory + recommended investigation items:

```yaml
classifications:
  - shape: js-library
    match:
      - file_exists: package.json
      - language: [TypeScript, JavaScript]
      - NOT file_exists: [bin/*, scripts/install*]
    emphasis:
      mandatory:
        - npm_lifecycle_hooks  # preinstall/postinstall in package.json
        - npm_registry_mapping  # does published package match this source?
        - readme_install_paste  # curl/npx invitations
      recommended:
        - transitive_dep_audit  # npm audit (if available)
      reference_scan: GitHub-Scanner-zustand.html

  - shape: compiled-cli
    match:
      - language: [Rust, Go, C, C++]
      - releases.assets_count: "> 5"
    emphasis:
      mandatory:
        - binary_attestation  # sigstore/cosign/minisign on release assets
        - cross_compile_matrix  # CI target platforms
        - registry_publish_path  # cargo publish / go install — CI-gated or manual?
      recommended:
        - binary_checksum_verify  # download + sha256sum
      reference_scan: GitHub-Scanner-fd.html

  - shape: agent-skills-distribution
    match:
      - OR:
        - file_exists: [CLAUDE.md, AGENTS.md, .cursorrules]
        - topics_include: [claude-code, ai-agent, codex]
        - file_count("SKILL.md"): "> 3"
    emphasis:
      mandatory:
        - f7_agent_rule_density  # tier 1/2/3/4 classification
        - auto_update_hooks  # SessionStart, cron, git pull from main
        - install_from_main_check  # is distribution pinned or live-main?
        - blast_radius_per_session  # what auto-loads into every session?
      recommended:
        - skill_content_audit  # read CLAUDE.md for behavioral manipulation
      reference_scan: GitHub-Scanner-gstack.html

  - shape: web-application
    match:
      - file_exists: [docker-compose.yml, Dockerfile]
      - OR:
        - file_exists: [.env.example, config/database.yml]
        - topics_include: [self-hosted, saas]
    emphasis:
      mandatory:
        - default_credentials  # JWT secrets, DB passwords in compose/env
        - pull_request_target  # CI write-all permissions
        - cve_history  # published security advisories
        - docker_image_provenance  # mutable tags, base image pinning
      recommended:
        - container_scan  # Trivy/Grype on built image (if available)
      reference_scan: GitHub-Scanner-postiz-app.html

  - shape: agentic-platform
    match:
      - has_install_script: true
      - OR:
        - file_exists: [packages/providers/*, src/commands/*]
        - description_matches: [agent, orchestrat, workflow]
    emphasis:
      mandatory:
        - install_script_audit  # what does the installer download/execute?
        - artifact_verification  # checksums, signatures, attestation
        - vendor_binary_trust  # does it download third-party binaries?
        - ci_release_pipeline  # what triggers a release? manual or automated?
      recommended:
        - homebrew_formula_audit  # if distributed via brew
        - self_merge_pattern  # F11 review rate on security-adjacent PRs
      reference_scan: GitHub-Scanner-Archon.html

  # --- Applied to ALL shapes (cross-cutting) ---
  universal:
    mandatory:
      - c20_governance_check  # branch protection + rulesets + CODEOWNERS
      - f7_agent_rule_scan  # CLAUDE.md, AGENTS.md, .cursorrules, .mcp.json
      - step_a_dangerous_primitives  # eval, exec, fetch, network, crypto
      - f11_review_rate_sample  # merged-PR author vs merger + review count
      - f12_executable_inventory  # 2-layer per V2.3 prompt
      - readme_install_path  # how do users install?
      - maintainer_background  # account age, followers, sockpuppet signals
    recommended:
      - dependabot_alerts_check
      - security_advisory_check
      - recent_commit_sample
      - open_issue_sample
```

#### Board questions on Q1

1. **Should this classification matrix exist as a formal YAML file in the scanner package?** Or should it remain implicit operator judgment?
2. **Is the shape list complete?** Missing shapes from the 8-scan catalog: tiny/pre-distribution repos (archon-board-review), Python packages (hermes-agent). Others the board can think of?
3. **Is the mandatory/recommended split the right granularity?** Or should everything be mandatory with a "skip if N/A" rule?
4. **Should the matrix be BINDING (like the C10 scorecard calibration) or ADVISORY?** Binding = the validator or a pre-scan check enforces it. Advisory = the operator should follow it but won't be blocked.
5. **Does this matrix belong in the prompt, the operator guide, or a separate file?**

#### Evidence to review

- `repo-deep-dive-prompt.md` — the current investigation spec (Steps 1-8 + A/B/C). Note that Step 2.5 (agent-rule detection) and Step 8 (artifact verification) already have shape-specific branches, but they're prose, not structured.
- `scanner-catalog.md` — the 8 completed scans. Each entry names its "shape" and could be tagged with which emphasis items were actually investigated.
- Any 2-3 `.md` scan files — to see how findings differ across shapes.

---

### Q2: What common vulnerabilities is the scanner blind to?

#### The problem

The scanner uses `gh` CLI + local grep (on a downloaded tarball) as its primary toolchain. This is powerful for governance, trust signals, and surface-level code patterns. But it has known blind spots.

#### Gap analysis (ranked by severity)

| # | Blind spot | What we miss | Tool that would close it | Current impact |
|---|---|---|---|---|
| **1** | **Transitive dependency vulnerabilities** | We check direct deps (package.json, Cargo.toml) but don't resolve the full tree. A safe direct dep can pull in a compromised transitive dep. | `npm audit` / `pip audit` / `cargo audit` / `bundler-audit` | **HIGH** — most real supply-chain attacks are transitive (event-stream, ua-parser-js, colors.js) |
| **2** | **Published artifact ≠ source** | We read the source tarball but can't verify that what's published to npm/PyPI/crates.io matches. An attacker could publish a different version. | `npm pack --dry-run` + diff against source; `cargo package --list`; PyPI download + diff | **HIGH** — this is literally the scanner's stated purpose ("is it safe to install?") and we can't fully answer it |
| **3** | **Secrets in git history** | We grep current files for hardcoded secrets but don't scan historical commits where secrets were committed then "deleted" (still in git objects). | truffleHog, gitleaks, detect-secrets | **MEDIUM** — common finding in security audits; `gh` can't traverse git history efficiently |
| **4** | **Context-dependent code vulnerabilities (SAST)** | Our Step A grep finds `eval(` and `innerHTML=` but misses: SQL injection via ORM query builders, SSRF via redirect chains, auth bypass via logic errors, race conditions | Semgrep, CodeQL, Bandit (Python), cargo-audit (Rust) | **MEDIUM** — grep catches ~30-40% of what SAST catches |
| **5** | **Container image contents** | We read Dockerfiles but can't inspect built images for extra layers, embedded secrets, or outdated base images | Trivy, Grype, `docker inspect` | **MEDIUM** — relevant for self-hosted web apps (like postiz-app) |
| **6** | **Runtime / dynamic behavior** | We see `fetch(url)` in source but can't observe what URL is actually called at runtime, or what data is exfiltrated | Dynamic analysis, network sandboxing | **LOW** for pre-install assessment (the scanner's use case is "should I install?" not "is this running safely?") |
| **7** | **Binary reverse engineering** | For repos shipping pre-built binaries, we trust the CI build pipeline but can't inspect the binary itself | Disassembly, binary diffing | **LOW** — sigstore attestation is the practical mitigation (fd has it) |

#### The current prompt's position

The V2.3 prompt says (paraphrased):
- "Use `gh` CLI for all API calls" — **mandatory**
- "Download the tarball and grep locally" — **mandatory**
- "Check npm/PyPI for published artifact mapping" — **recommended, not mandatory**
- No mention of `npm audit`, truffleHog, Semgrep, Trivy, or any external security tool

The prompt is effectively a **governance + surface-level-code scanner**, not a SAST/SCA tool. This is a design choice, not a bug — but it's an undocumented design choice.

#### Board questions on Q2

1. **Should the scanner add mandatory tool calls?** Specifically:
   - `npm audit` / `pip audit` / `cargo audit` — one command per ecosystem, closes the #1 gap (transitive deps). ~10 seconds per scan.
   - `gh api repos/OWNER/REPO/dependency-graph/sbom` — GitHub's own SBOM endpoint, free, no extra tool needed. Surfaces transitive deps via the GitHub dependency graph.
   
2. **Should we add OPTIONAL tool calls with graceful degradation?** Example: "if `semgrep` is installed, run `semgrep --config auto` on the tarball. If not installed, note 'SAST not performed — install semgrep for deeper code analysis' in Coverage."

3. **Or should we explicitly document the blind spots as OUT OF SCOPE?** The scanner's value proposition is governance + trust + install-safety assessment, not comprehensive SAST/SCA. Maybe the right answer is: "This scanner tells you whether to trust the maintainers and the distribution pipeline. For code-level vulnerability scanning, use [Semgrep/CodeQL/Snyk] separately." Add a "Limitations" section to every report.

4. **The SBOM endpoint is the lowest-hanging fruit.** `gh api repos/OWNER/REPO/dependency-graph/sbom` returns the full dependency tree as SPDX JSON — no extra tool needed, works with the existing `gh` CLI toolchain. Should this be mandatory in the prompt's Step 3 (dependency and supply chain)?

5. **Should the scanner output include a "Coverage completeness" indicator?** Something like: "This scan covers governance (✓), surface code patterns (✓), transitive dependencies (✗ — run `npm audit` separately), secrets in history (✗ — run `truffleHog` separately), container image (✗ — run `trivy` separately)." This makes the blind spots visible per-scan rather than in a general disclaimer.

#### Evidence to review

- `repo-deep-dive-prompt.md` Steps 3, A, B, C — the current dependency + code analysis spec
- `GitHub-Scanner-postiz-app.md` — the scan that found 8 CVEs (all via the advisory API, not via code analysis — demonstrates what we CAN catch vs what we'd need SAST for)
- `GitHub-Scanner-hermes-agent.md` — found 5 open security issues via issue search, not via code scanning
- `GitHub-Scanner-fd.md` — the one scan with sigstore attestation as a compensating control for the binary-trust gap

---

## Deliverables requested from the board

For each question:

1. **Verdict:** YES (build it) / NO (accept the gap) / DEFER (with trigger)
2. **If YES:** priority items (which gaps to close first, which shapes to classify first)
3. **If DEFER:** what trigger re-opens the question (scan count? specific finding? user feedback?)
4. **Numbered findings** with severity, evidence, impact, proposed fix — same format as prior board reviews

## Reference files (included in the scanner package)

| File | Lines | Purpose |
|---|---|---|
| `repo-deep-dive-prompt.md` | 1,078 | Current investigation spec — what the LLM checks |
| `SCANNER-OPERATOR-GUIDE.md` | 552 | Current process guide — how the scan runs end-to-end |
| `scanner-catalog.md` | 45 | 8-scan catalog with shapes and verdicts |
| `GitHub-Scanner-zustand.md` | 534 | Example: JS library scan (clean, governance-only findings) |
| `GitHub-Scanner-postiz-app.md` | 364 | Example: web app scan (CVEs, Docker defaults, pull_request_target) |
| `GitHub-Scanner-gstack.md` | 600 | Example: agent-skills scan (50 agent-rule files, install-from-main) |
| `GitHub-Scanner-fd.md` | 594 | Example: Rust CLI scan (SLSA attestations, multi-platform binaries) |
| `GitHub-Scanner-hermes-agent.md` | 347 | Example: Python platform scan (org-owned, open vulns) |

The board should read at least 3 of the scan `.md` files to understand how findings are currently derived and where the gaps show.

---

## Process notes for the facilitator

- This is a single-round review (not the 4-round SOP used for internal reviews). The questions are well-defined enough for each board member to take a position independently.
- If the board wants to go deeper on either question, a follow-up 4-round review on the specific deliverable (classification YAML schema or tool-integration spec) is appropriate.
- The scanner development team will apply FIX NOW items from this review in the next working session.
