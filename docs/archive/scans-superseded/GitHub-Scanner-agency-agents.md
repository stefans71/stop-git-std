# Security Investigation: msitarzewski/agency-agents

- Scan date: 2026-04-17
- Commit pin: 783f6a72bfd7f3135700ac273c619d92821b419a
- Default branch: main
- Repo shape: prompt and agent distribution repository with shell-based install and conversion scripts

## Verdict

Verdict: Caution

The scanned shell scripts were not overtly malicious, and no install-time remote fetch pattern was found in them. The bigger trust issue is that this repo ships 184 prompt files into agent and rules locations across many tools, while the public sample of recent merged PRs showed zero review events and the documented install path is an unpinned local checkout rather than a tagged or signed artifact.

If you use it, pin a specific commit and review the exact agents and integrations you plan to install. Do not treat current main as a stable trust anchor.

## Findings

### F-review — Recent merged PR sample shows no independent review before install-affecting changes ship (Warning)

- Severity: Warning
- Status: Ongoing
- Summary: The 20 most recent merged PRs visible through the public API all returned zero review events, including install-path and security-policy changes.
- Risk: This matters because the repository distributes prompt content into agent and rules directories. A bad change can ship with little upstream friction if review remains this thin.
- Action: If you install: pin the exact commit you trust and inspect install-related diffs before updating. If you maintain: require one reviewer for scripts, workflows, SECURITY.md, and integration outputs.
- Evidence:
  - GitHub search reported 119 merged PRs total.
  - Sampled the 20 most recent merged PRs from the public pulls API; all 20 had zero review events via the pull reviews endpoint.
  - PR 437 was authored and merged by the owner and had zero review events.
  - PR 323 and PR 410 were merged by the owner and also had zero review events.

### F-distribution — The documented install path relies on a local checkout rather than a tagged or signed artifact (Warning)

- Severity: Warning
- Status: Active
- Summary: README guidance tells users to run convert.sh and install.sh from a checkout. The repository had zero tags and zero releases at scan time.
- Risk: The next user who clones or pulls current main gets the newest prompt payload. That risk is amplified because the payload is agent content that several tools auto-load or surface prominently.
- Action: If you install: use a specific commit SHA and keep a trusted local snapshot. If you maintain: publish tagged releases or signed bundles and document a pinned install path.
- Evidence:
  - README Quick Start uses local scripts from the checkout and does not pin a release or tag.
  - GitHub releases endpoint returned an empty list.
  - Git tags list was empty.
  - Installer destinations include user-wide and project-scoped agent or rules paths such as ~/.claude/agents, ~/.copilot/agents, .cursor/rules, CONVENTIONS.md, .windsurfrules, ~/.config/kimi/agents, and ~/.openclaw/agency-agents.

### F-surface — The repository has low classic code-execution surface but high prompt-distribution surface (Informational)

- Severity: Informational
- Status: Informational
- Summary: Static checks did not show install-time network fetches or committed secret files in the shipped shell scripts. The main payload is 184 Markdown prompt files copied into tool-specific locations.
- Risk: This reduces traditional malware-style risk, but it shifts trust to prompt quality, tool auto-load behavior, and maintainer controls.
- Action: Review only the specific agents and integrations you plan to install, with extra care for always-on or user-wide destinations.
- Evidence:
  - No root dependency manifests were found for npm, PyPI, Cargo, Go, Ruby, Maven, or Composer.
  - No .env, PEM, SSH key, or credentials filenames were found.
  - The only workflow is lint-agents.yml; it uses pull_request, not pull_request_target.
  - Grep hits for fetch and subprocess patterns appeared mainly inside Markdown prompt examples, not inside repository-executed shell code.

## Executable File Inventory

### scripts/install.sh (Warning)

- Trigger: Manual user execution after cloning the repo
- Data it reads: HOME, PWD, category directories, integrations outputs, optional openclaw CLI output
- Data it writes: Writes into agent and rules directories for Claude Code, Copilot, Gemini-related tools, OpenCode, Cursor, Aider, Windsurf, Qwen, Kimi, and OpenClaw
- Network: No direct network fetch found
- Prompt-injection channel: High: copies prompt content into agent or rules locations that may be auto-loaded
- Secret-leak path: No direct secret exfiltration path found
- Privilege: Current user, user-home and project config paths
- Capability assessment: Can populate many agentic tools with repo prompt content in one run
- Risk statement: If a future malicious prompt lands upstream, rerunning the installer could spread it across multiple local agent surfaces.

### scripts/convert.sh (Informational)

- Trigger: Manual user execution before installing non-native integrations
- Data it reads: All agent Markdown files plus frontmatter fields
- Data it writes: Writes tool-specific prompt artifacts including Cursor mdc, Windsurf rules, Aider conventions, OpenClaw workspaces, Qwen agents, and Kimi agent files
- Network: No network activity found
- Prompt-injection channel: High: repackages prompt content into tool-native formats
- Secret-leak path: No direct secret handling found
- Privilege: Current user inside the repo checkout
- Capability assessment: Can transform the source prompts into downstream rule and system-prompt formats
- Risk statement: A compromised source prompt would be propagated into multiple integration formats without a separate artifact verification step.

### .github/workflows/lint-agents.yml (OK)

- Trigger: Runs on pull_request for agent-directory changes
- Data it reads: Changed file paths from git diff
- Data it writes: Writes only GITHUB_OUTPUT
- Network: No network fetch or curl pipe found
- Prompt-injection channel: Low: validates structure only
- Secret-leak path: No obvious secret use beyond standard Actions environment
- Privilege: GitHub Actions runner
- Capability assessment: Can lint changed agent files before merge
- Risk statement: Its main future risk is governance: if changed without review, it could weaken validation of content that later ships to users.

### integrations/mcp-memory/setup.sh (Informational)

- Trigger: Manual user execution for the optional MCP memory integration
- Data it reads: Looks for common MCP config paths in the user home and current directory
- Data it writes: Does not modify config files; prints example config to stdout
- Network: No network activity found; only placeholder package-manager guidance is printed
- Prompt-injection channel: Medium: guides users toward adding an external memory server to their toolchain
- Secret-leak path: No direct secret access beyond config-file existence checks
- Privilege: Current user
- Capability assessment: Can steer users toward wiring a persistent memory server into supported tools
- Risk statement: Because it does not pin a specific memory server, a careless user could connect an unsafe third-party MCP server.

## Suspicious Code Changes

| PR | Files | Why it was inspected | Result |
|---|---|---|---|
| 437 | scripts/install.sh, scripts/convert.sh, scripts/lint-agents.sh, .github/workflows/lint-agents.yml, README.md, CONTRIBUTING.md | Install and workflow surface | Self-merged by owner; zero review events; diff adds finance paths without hidden fetch logic. |
| 323 | scripts/install.sh | Install-path correction | Merged by owner; zero review events; diff fixes OpenCode and Copilot destination handling. |
| 410 | SECURITY.md | Security-policy addition | Merged by owner; zero review events; resulting file contains trailing EOFcat SECURITY.md artifact. |

## Repo Vitals

| Metric | Value |
|---|---|
| Stars | 81,436 |
| Forks | 13,038 |
| Created | 2025-10-13T12:12:29Z |
| Last push | 2026-04-12T04:25:59Z |
| License | MIT |
| Releases | 0 |
| Tags | 0 |
| OSSF Scorecard | not indexed, public API returned 404 |
| Merged PRs | 119 |
| Review sample | 0 of 20 recent merged PRs had review events |
| Agent prompt files copied by installer | 184 |

## Trust Scorecard

### Does anyone check the code?

- Rating: Red
- Rationale: Sampled 0 of 20 recent merged PRs with review events. The sample included install-path and security-policy changes.

### Do they fix problems quickly?

- Rating: Green
- Rationale: The repo is active and the sampled open issues did not show obvious security or CVE titles.

### Do they tell you about problems?

- Rating: Amber
- Rationale: SECURITY.md exists and points reporters to private advisories, but there are no published advisories and no release history.

### Is it safe out of the box?

- Rating: Amber
- Rationale: The default path is a local checkout plus scripts, not a tagged or signed artifact, and several integrations install auto-loaded prompt files.

## Investigation Coverage

| Coverage cell | Status | Notes |
|---|---|---|
| OSSF Scorecard | Partial | Public Scorecard API returned HTTP 404 for this repository. |
| osv.dev and deps | Not applicable | Dependabot alerts required authentication and no direct dependency manifests were present. |
| Secrets in history | Not scanned | gitleaks was not installed in this environment. |
| API budget | Measured | GitHub unauthenticated core budget was 60 per hour; 47 remained after evidence collection. |
| pull_request_target usage | Checked | 0 workflows. The only workflow uses pull_request. |
| Tar hardening | Fallback used | Host tar lacked the required --no-absolute-names flag, so checkout fallback was used after pinning the full SHA. |
| Branch protection | Unknown | Classic branch-protection endpoint returned 401 Requires authentication; rulesets and branch rules endpoints returned empty arrays. |
| CODEOWNERS | Checked | No CODEOWNERS file found in standard locations. |

## Evidence

### Repo identity and maintainers

- Public repo metadata on 2026-04-17: 81,436 stars, 13,038 forks, created 2025-10-13T12:12:29Z, pushed 2026-04-12T04:25:59Z.
- Owner account msitarzewski was created on 2012-07-13, has 22 public repos, and 2734 followers.
- Contributor jnMetaCode was created on 2015-04-24, has 104 public repos, and 260 followers.
- Contributor epowelljr was created on 2014-04-19, has 21 public repos.

### Governance evidence

- community profile health was 85 percent with CONTRIBUTING and PR template present.
- No CODEOWNERS file was found in standard locations.
- Classic branch protection was not confirmable because the endpoint returned 401 Requires authentication.
- Repo rulesets endpoint returned an empty array.
- Branch rules endpoint for main returned an empty array.

### CI and workflow evidence

- The only workflow file is .github/workflows/lint-agents.yml.
- Trigger is pull_request only.
- pull_request_target usage: 0 workflows.
- Action pinning: actions/checkout@v4 only, which is a first-party major-tag pin rather than a full SHA pin.

### Dependency and supply-chain evidence

- No root dependency manifest was present for npm, PyPI, Cargo, Go, Ruby, Maven, or Composer.
- Dependabot alerts endpoint returned 401 Requires authentication.
- Security advisories endpoint returned an empty list.
- OSSF Scorecard public API returned HTTP 404 for this repository.

### Install and distribution evidence

- README quick start instructs users to run install.sh and convert.sh from a local checkout.
- The repo had zero GitHub releases and zero Git tags at scan time.
- install.sh writes into user and project agent or rules locations for Claude Code, Copilot, Gemini-related tools, OpenCode, Cursor, Aider, Windsurf, Qwen, Kimi, and OpenClaw.
- convert.sh sets Cursor alwaysApply to false by default, but the docs show how a user can flip a rule to alwaysApply true manually.
- No README or integration docs matched the scanner pattern for paste this into your system prompt or rules file invitations.

### PR and issue evidence

- GitHub search reported 119 merged PRs total.
- Review sample: 0 of 20 recent merged PRs had review events.
- PR 437 changed install, convert, lint, workflow, README, and CONTRIBUTING coverage and was self-merged by the owner with zero review events.
- PR 323 corrected install paths and was merged by the owner with zero review events.
- PR 410 added SECURITY.md and was merged by the owner with zero review events; the resulting file contains a trailing EOFcat SECURITY.md artifact.
- The sampled open issues did not show obvious security or CVE titles.

### Recent commits sample

- 783f6a72bfd7f3135700ac273c619d92821b419a — 2026-04-12T04:25:59Z — Shiven Garia — signature status E — Fix opencode global install docs to use install.sh --path (#249)
- cef210520701d2c57fce139eb4832ee56a01f929 — 2026-04-12T04:25:56Z — Ryanba — signature status E — docs: add Qwen integration guide (#232)
- 2af37738667ea3387227b198fe89a614e0192743 — 2026-04-12T04:25:53Z — Ryanba — signature status E — docs: align displayed OpenClaw install path (#231)
- 3d574c9aacb99d3f974e641701020f74814aa7aa — 2026-04-12T04:25:50Z — Ryanba — signature status E — docs: align agent linting with OpenClaw section split (#230)
- a4ec4a0d135b808cfecc18f678374ac25dc702d7 — 2026-04-12T04:25:48Z — Kiên Bùi — signature status E — fix: add post-install hint for Copilot agent path verification (#224)

## Section 08 — How This Scan Works

- Phase 1: prep and commit pinning.
- Phase 2: evidence gathering from local source, public GitHub REST, Scorecard lookup, issue and PR sampling, and install-path inspection.
- Phase 3: findings bundle with facts, inference, and synthesis separated.
- Phase 4: canonical Markdown first, then derived HTML.
- Phase 5: validator loop until both outputs pass.
- Phase 6: deliver results with explicit coverage gaps instead of guessing.

The scanner treats repository content as untrusted input. It prefers local grep, minimal-context reads, and explicit coverage accounting over narrative trust or guessed results.

## Limitations

- gh CLI was not authenticated in this environment, so authenticated GitHub endpoints and GraphQL-only fields were unavailable.
- Classic branch protection could not be confirmed because the public endpoint returned 401 Requires authentication.
- The review conclusion is sample-based on the most recent 20 merged PRs, not the full 119-PR history.
- gitleaks was not installed, so secrets in history were not scanned.
- Scorecard data was unavailable because the public Scorecard API returned 404 for this repository.

