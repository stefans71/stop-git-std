# stop-git-std v3 — Technical Design

## Overview

**stop-git-std** is a detection-first Git repository safety auditor built with Bun/TypeScript. It decides whether a repo is safe to adopt, run, or integrate by auditing the full repo surface: source trust, supply chain, dangerous execution paths, CI/CD workflow risk, infrastructure/container risk, and typed risk packs for API, AI/LLM, agent, plugin/skill, and MCP repos.

## Tech Stack

- **Bun + TypeScript** — primary engine, orchestration, scoring, policy, reporting
- **Python** — optional later, via plugin/subprocess interface only. Bun owns all orchestration.
- **CLI-first** — primary product surface

## Canonical Documents

| Document | Path | Purpose |
|----------|------|---------|
| Technical Design | `docs/technical-design.md` | Architecture, pipeline, decisions |
| Engine Contract | `docs/engine-contract.yaml` | Execution contract: phases, artifacts, scoring, policy |
| Rule Catalog | `docs/rule-catalog.yaml` | All rules by module, detection methods, axis impacts |
| Implementation Plan | `docs/implementation-plan.md` | Milestone-by-milestone build plan with confirmed decisions |

## Architecture

### Rule-Catalog-Driven Engine

The engine is data-driven. Rules are defined in YAML (`docs/rule-catalog.yaml`), not hardcoded. The engine contract (`docs/engine-contract.yaml`) defines execution semantics: phase ordering, artifact schemas, scoring formulas, and policy profiles.

Analyzers load their rules from the catalog at runtime and emit normalized findings matching the finding contract.

### 11-Phase Pipeline

The engine executes a fixed sequence of 11 phases (defined in `engine-contract.yaml`):

1. **context_capture** — Normalize audit request into audit context
2. **repository_acquisition** — Clone/fetch repo or open local path
3. **inventory_classification** — Build repo profile: languages, frameworks, categories, capabilities
4. **module_routing** — Activate modules based on detected categories + user overrides
5. **universal_analysis** — Run 6 universal rule modules (every repo)
6. **typed_analysis** — Run category-specific rule modules (activated by classification)
7. **runtime_validation** — Optional sandboxed execution (no-op in MVP)
8. **finding_normalization** — Merge, dedupe, normalize all findings
9. **scoring** — Compute 3-axis risk scores + confidence
10. **policy_decision** — Convert scores + findings into final decision
11. **reporting** — Emit requested report formats

### Module System

**Universal modules** (run on every repo):
- `governance_trust` — Source attribution, maintainer hygiene, provenance
- `supply_chain` — Dependency posture, reproducibility, vulnerability
- `secrets` — Committed secrets and sensitive material
- `dangerous_execution` — Install/run-path behaviors that can cause harm
- `ci_cd` — GitHub Actions and pipeline trust-boundary risks
- `infrastructure` — Container and deployment safety

**Typed modules** (activated by repo classification):
- `web` — Web application security signals
- `api` — API auth, validation, exposure
- `ai_llm` — LLM integration safety
- `agent_framework` — Agentic system permissions and controls
- `skills_plugins` — Extension manifest and instruction safety
- `mcp_server` — MCP tool exposure and scope risks
- `library_package` — Reusable package import-time side effects

**Routing**: Engine contract is canonical for module routing. Classification detects repo categories, router expands to universal + typed modules per category routes.

### Analyzer Contract

Every analyzer implements:

```typescript
interface AnalyzerModule {
  name: string;
  analyze(
    workspace: LocalWorkspace,
    profile: RepoProfile,
    context: AuditContext,
    rules: RuleDefinition[]
  ): Promise<AnalyzerOutput>;
}
```

Returns normalized findings matching the Finding schema from the engine contract.

### Pluggable Backend Interface

Analyzers are pluggable backends: `builtin-ts`, `python-subprocess`, `external-tool`. MVP is pure Bun/TypeScript. Python interface designed but not implemented until M5.

## Scoring Model

Three risk axes scored 0-100 (higher is worse):

- **trustworthiness** — Source trust, governance, provenance signals
- **exploitability** — Attack surface, vulnerability exposure
- **abuse_potential** — Potential for misuse in target environment

### Formula (MVP)

```
weighted_axis_value = axis_impact * severity_weight * confidence_multiplier / 10
```

**Severity weights**: info=1, low=3, medium=8, high=15, critical=25

**Confidence multipliers**: low=0.6, medium=0.85, high=1.0

**Environment multiplier** (applied to abuse_potential only):
- developer_laptop: 1.25
- ci_runner: 1.30
- container_isolated: 0.80
- offline_analysis: 0.20
- production_service: 1.40

**Trust signal subtraction** (derived from repo_profile, only when corresponding module completed with status "success" or "partial"):
- signed_tags_present: -8
- security_md_present: -3
- codeowners_present: -2
- pinned_actions_ratio_high: -4

Each axis clamped to [0, 100].

**Note**: The divisor is `/10` as specified in the engine contract.

### Confidence Model (MVP — version "mvp-1")

- **high**: failed_modules_ratio <= 0.10 AND (critical_static_findings >= 1 OR all universal modules completed successfully)
- **medium**: failed_modules_ratio <= 0.30
- **low**: fallback

> MVP confidence model — AST requirement added when parser support ships.

## Policy Decision

### Decision Values

- `PROCEED` — Safe to adopt
- `PROCEED_WITH_CONSTRAINTS` — Adopt with specific mitigations
- `CAUTION` — Significant risk, manual review recommended
- `ABORT` — Do not adopt

### Policy Profiles

Three profiles with different thresholds: **strict**, **balanced** (default), **advisory**.

### Hard-Stop Rules

These rules trigger immediate ABORT (strict/balanced) or CAUTION (advisory):
- GHA-SECRETS-001, GHA-EXEC-001, GHA-EXEC-005, GHA-CI-004
- GHA-AI-001, GHA-AGENT-001, GHA-MCP-001, GHA-MCP-003
- GHA-RUNTIME-001, GHA-RUNTIME-003

### Default Constraints

Automatically attached based on finding categories:
- High abuse_potential: run in disposable container, restrict network, scoped tokens
- Supply chain findings: pin to reviewed commit SHA, vendor dependencies
- CI/CD findings: disable self-hosted runners, minimize token permissions
- Runtime findings: block adoption until manual review

## Output Formats

### MVP
1. **Terminal report** — Executive summary, top findings, scores, decision (color-coded)
2. **JSON report** — Full machine-readable output matching engine contract artifact schemas
3. **Markdown report** — For PRs, review artifacts, security workflows

### Later
- SARIF
- GitHub Action annotations
- Issue/comment generation

## CLI Interface

```bash
bun run src/cli.ts <repo-path-or-url> [options]
```

Options: `--ref`, `--env`, `--policy`, `--format`, `--output-dir`, `--include`, `--exclude`, `--enable-module`, `--disable-module`, `--runtime-mode`, `--adoption-mode`

Exit codes: 0=PROCEED, 1=ABORT, 2=CAUTION

## Suppressions

File: `.stop-git-std.suppressions.yaml`

```yaml
suppressions:
  - rule_id: GHA-SECRETS-003
    path_globs: ["test/fixtures/**"]
    justification: "Test fixtures with fake tokens"
    approved_by: "security-team"
    expires_at: "2026-12-31"
```

- Hard-stop rules cannot be suppressed by default
- Expired suppressions are ignored
- Suppressed findings remain in output with `suppressed: true`

## Error Handling

Philosophy: best-effort with transparency.

- Rule parse error: mark module partial, continue
- Parser not supported: downgrade coverage confidence
- GitHub API unavailable: continue without metadata enrichment
- OSV lookup failed: emit warning, continue
- Runtime sandbox failed: mark failed, continue unless hard-stop already triggered

## Repo Structure

```
stop-git-std/
  docs/
    technical-design.md
    engine-contract.yaml
    rule-catalog.yaml
    implementation-plan.md
  src/
    cli.ts
    engine/
      run-audit.ts
      router.ts
      normalize-findings.ts
      scoring.ts
      policy.ts
    models/
      enums.ts
      audit-request.ts
      audit-context.ts
      repo-profile.ts
      finding.ts
      scores.ts
      decision.ts
      module-result.ts
      run-manifest.ts
      local-workspace.ts
      audit-result.ts
      index.ts
    inventory/
      acquire-repo.ts
      enumerate-files.ts
      classify-repo.ts
      detect-frameworks.ts
    analyzers/
      base.ts
      universal/
        governance-trust.ts
        supply-chain.ts
        secrets.ts
        dangerous-execution.ts
        ci-cd.ts
        infrastructure.ts
      typed/
        web.ts
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
    adapters/
      github-api.ts
      osv.ts
      scorecard.ts
    reporting/
      terminal.ts
      markdown.ts
      json.ts
    rules/
      types.ts
      load-rule-catalog.ts
      load-engine-contract.ts
    plugins/
      analyzer-backend.ts
      builtin-ts.ts
      python-subprocess.ts
```
