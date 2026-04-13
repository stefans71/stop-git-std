# stop-git-std — Build Spec

## What it is

**stop-git-std** is a detection-first Git repository safety auditor.

It decides whether a repo is safe to adopt, run, or integrate.

Broader than a secrets scanner or CVE checker — it audits the full repo surface: source trust, supply chain, dangerous execution paths, CI/CD workflow risk, infrastructure/container risk, and typed risk packs for API, AI/LLM, agent, plugin/skill, and MCP repos.

## Tech Stack

- **TypeScript / Bun (latest)** — primary engine and CLI
- **Python** — reserved for optional deep analyzers later (AST, taint/dataflow)
- Hybrid-ready architecture: Bun controls orchestration, scoring, policy, reporting

## Who Uses It

- **CLI first** (primary product)
- **GitHub Action later** (same engine underneath)
- Users: security engineers, platform engineers, devs reviewing third-party repos, AI platform teams reviewing agent/MCP/plugin repos

## Output

### MVP outputs
1. **Terminal report** — executive summary, detected repo types, top findings, final decision
2. **JSON report** — machine-readable findings, scores, decision, repo profile
3. **Markdown report** — for review, docs, PR artifacts, security workflows

### Decision values
- `PROCEED`
- `PROCEED_WITH_CONSTRAINTS`
- `CAUTION`
- `ABORT`

### Scoring axes
- `trustworthiness`
- `exploitability`
- `abuse_potential`

### Later outputs
- SARIF, GitHub Action annotations, issue/comment generation

## What It Scans For

### Universal checks (every repo)

**Governance / trust**
- Missing `SECURITY.md`, `CODEOWNERS`
- Archived/abandoned repo
- No signed tags/releases
- Suspicious contributor shifts

**Supply chain**
- Lockfile missing
- Floating dependency versions
- Direct Git or URL dependencies
- Vulnerable packages via OSV
- Opaque vendored binaries

**Secrets**
- Private keys, `.env` files, API tokens
- Connection strings
- High-entropy secret-like values

**Dangerous execution**
- `curl | bash`
- Install lifecycle hooks
- `subprocess(..., shell=True)`
- Unsafe deserialization
- Remote code/config fetched and executed

**CI/CD**
- `pull_request_target`
- Broad `GITHUB_TOKEN` permissions
- Unpinned third-party actions
- Shell injection in workflow steps
- Self-hosted runner on untrusted trigger paths

**Infrastructure**
- Docker runs as root
- `:latest` base image
- Broad Kubernetes RBAC
- Unsafe deployment defaults

### Typed checks (based on repo classification)

The tool classifies the repo first, then activates rule packs.

Categories: web app, API, AI/LLM, agent framework, skills/plugins, MCP server, library/package, CI/CD-heavy, infrastructure-heavy.

**API** — missing auth guards, permissive CORS, request-to-model binding without validation
**AI/LLM** — model output controls tool/shell execution, secrets in prompts, missing rate/budget controls
**Agent framework** — shell+write+network without approval gate, shared state without isolation
**Skills/plugins** — broad manifest permissions, instruction content overriding safety boundaries
**MCP server** — unrestricted shell tool, SSRF-capable fetch, credential forwarding into tools

### Runtime validation (post-MVP)
- Sandboxed install/build/smoke execution
- Unexpected outbound network
- Reads of SSH/cloud credential paths
- Download followed by shell execution

## Architecture

Rule-catalog-driven engine. YAML rule catalog and engine contract are source of truth.

Engine pipeline:
1. Capture audit context
2. Acquire repo
3. Inventory/classify repo
4. Activate modules
5. Run universal analyzers
6. Run typed analyzers
7. Normalize findings
8. Score findings
9. Apply policy decision
10. Emit reports

### Hybrid analyzer model

Analyzers are pluggable backends: `builtin-ts`, `python-subprocess`, `external-tool`.
All return the same normalized JSON finding contract.
MVP: pure Bun/TypeScript only. Python interface designed but not implemented.

## Repo Structure

```
stop-git-std/
  README.md
  docs/
    build-spec.md
    technical-design.md
    rule-catalog.yaml
    engine-contract.yaml
  src/
    cli.ts
    engine/
      run-audit.ts
      router.ts
      scoring.ts
      policy.ts
      normalize-findings.ts
    models/
      audit-request.ts
      repo-profile.ts
      finding.ts
      scores.ts
      decision.ts
    inventory/
      acquire-repo.ts
      enumerate-files.ts
      classify-repo.ts
      detect-frameworks.ts
    analyzers/
      universal/
        governance-trust.ts
        supply-chain.ts
        secrets.ts
        dangerous-execution.ts
        ci-cd.ts
        infrastructure.ts
      typed/
        api.ts
        ai-llm.ts
        agent-framework.ts
        skills-plugins.ts
        mcp-server.ts
        library-package.ts
    parsers/
      package-json.ts
      workflow-yaml.ts
      dockerfile.ts
      k8s-yaml.ts
      ts-ast.ts
    adapters/
      github-api.ts
      osv.ts
      scorecard.ts
    reporting/
      terminal.ts
      markdown.ts
      json.ts
    rules/
      load-rule-catalog.ts
      load-engine-contract.ts
    plugins/
      analyzer-backend.ts
      builtin-ts.ts
      python-subprocess.ts
```

## Build Plan

### Milestone 1 — Foundation
- Initialize Bun project
- CLI entrypoint
- Models (audit-request, finding, scores, decision, repo-profile)
- Load YAML rule catalog and engine contract
- Repo acquisition + inventory/classification

### Milestone 2 — Universal Analyzers
- Secrets
- Dangerous execution
- CI/CD
- Supply chain

### Milestone 3 — Typed Analyzers
- API
- AI/LLM
- Agent framework
- MCP server

### Milestone 4 — Scoring & Reporting
- Normalization
- Scoring engine
- Policy engine
- Terminal/JSON/markdown reporting

### Milestone 5 — Extensibility
- Plugin backend interface
- Stub Python subprocess analyzer contract
- GitHub Action wrapper

## Key Product Rule

This is a real repository safety auditor, not a bag of greps. Inventory first, route to right modules, normalize findings, score by axis, make a policy decision, keep evidence explicit.
