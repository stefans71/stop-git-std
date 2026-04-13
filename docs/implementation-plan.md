# stop-git-std — Finalized Implementation Plan

## Confirmed Decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | CLI framework | `commander` |
| 2 | YAML loading | Runtime file load from `docs/` |
| 3 | Git operations | `Bun.spawn` + git CLI |
| 4 | Clone temp dir | `/tmp/stop-git-std/<run-id>` |
| 5 | AST scanning MVP | Regex/heuristic fallback with confidence downgrade |
| 6 | OSV in M2 | Stub in M2, full HTTP in M5 |
| 7 | Scoring divisor | `/20` (overridden from spec's `/10` for MVP calibration) |
| 8 | Trust signal source | `repo_profile` inspection in scorer |
| 9 | Suppression file | `.stop-git-std.suppressions.yaml` |
| 10 | Typed analyzer depth | Regex/heuristic with lower confidence, never skip rules |
| 11 | Web module in M3 | Yes, include |
| 12 | Python subprocess contract | stdin/stdout JSON |
| 13 | GitHub Action packaging | Source + Bun |

## Resolved Contradictions

- **Engine contract Python filenames**: Stale notes. Treat as behavior spec only; implement in Bun/TS.
- **Phase count**: MVP keeps `runtime_validation` as a structural no-op (11 phases, phase 7 is skip-unless-enabled).
- **Missing `web.ts`**: Added to typed analyzers.
- **Routing canonical source**: Engine contract wins. Rule catalog routing is informational.
- **Scoring divisor**: Changed from `/10` to `/20` for MVP.
- **`library_package` route**: Added to canonical routes.
- **Trust signals**: Derived from `repo_profile`, not positive findings.
- **M3 scope**: All 7 typed analyzers included.

## Canonical Docs

| Purpose | Path |
|---------|------|
| Architecture & build spec | `docs/technical-design.md` |
| Engine execution contract | `docs/engine-contract.yaml` |
| Rule catalog | `docs/rule-catalog.yaml` |

Old `gh_audit_*` naming is transitional and will be removed.

## Tech Stack

- **Bun + TypeScript** — primary engine, orchestration, scoring, policy, reporting
- **Python** — optional later via plugin/subprocess interface only
- **CLI-first** — terminal + JSON + markdown outputs

## External Dependencies

| Package | Purpose |
|---------|---------|
| `zod` | Schema validation for all models |
| `yaml` (js-yaml) | Parse YAML rule catalog and engine contract |
| `commander` | CLI argument parsing |
| `picocolors` | Terminal coloring |
| `nanoid` | Generate `run_id` values |

---

## Milestone 1 — Foundation

**Goal**: Project scaffolding, all type definitions, YAML loading, CLI entrypoint, repo acquisition, inventory, classification, module routing.

### Task 1.1: Create directory structure

```
src/
  cli.ts
  engine/
    run-audit.ts
    router.ts
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
    typed/
  parsers/
  adapters/
  reporting/
  rules/
    types.ts
    load-rule-catalog.ts
    load-engine-contract.ts
  plugins/
    analyzer-backend.ts
    builtin-ts.ts
```

### Task 1.2: Define core model types (Zod schemas + TypeScript types)

**`src/models/enums.ts`**
- `Severity` = `"info" | "low" | "medium" | "high" | "critical"`
- `Confidence` = `"low" | "medium" | "high"`
- `ProofType` = `"static" | "heuristic" | "runtime"`
- `DecisionValue` = `"PROCEED" | "PROCEED_WITH_CONSTRAINTS" | "CAUTION" | "ABORT"`
- `ModuleStatus` = `"pending" | "running" | "success" | "partial" | "failed" | "skipped"`
- `Environment` = `"developer_laptop" | "ci_runner" | "container_isolated" | "offline_analysis" | "production_service"`
- `RuntimeMode` = `"off" | "install_only" | "build" | "smoke"`
- `AdoptionMode` = `"third_party" | "internal" | "fork_review" | "pre_merge"`
- `PolicyProfile` = `"strict" | "balanced" | "advisory"`

**`src/models/audit-request.ts`** — Zod schema matching `inputs.audit_request` from engine contract.

**`src/models/audit-context.ts`** — Zod schema matching `artifacts.audit_context`.

**`src/models/repo-profile.ts`** — Languages, frameworks, ecosystems, detected_categories, artifacts (manifests/workflows/containers/infra/binaries), counts, high_risk_files, capability_summary. Type `RepoCategory` = union of all category strings.

**`src/models/finding.ts`** — Full finding schema with axis_impacts, evidence (type + records), remediation, mapped_standards, suppression fields.

**`src/models/scores.ts`** — Three axes (0-100), confidence, component_breakdown, environment_multiplier_applied.

**`src/models/decision.ts`** — Value, reasons, constraints, hard_stop_triggered, triggered_by_rules, manual_review_required.

**`src/models/module-result.ts`** — Module name, status, timing, findings_emitted, warnings, errors, coverage.

**`src/models/run-manifest.ts`** — run_id, engine_version, rule_catalog_version, timing, repo_target, ref, status.

**`src/models/local-workspace.ts`** — rootPath, gitMetadata (lastCommitDate, contributors, tags, signedTags), isLocal.

**`src/models/index.ts`** — Barrel export.

**Blocks**: Everything else depends on this.

### Task 1.3: YAML rule catalog and engine contract loaders

**`src/rules/types.ts`** — Types for RuleDefinition, RuleCatalog, EngineContract, PolicyProfileConfig, ScoringDefaults, DetectionSpec.

**`src/rules/load-rule-catalog.ts`**
- `loadRuleCatalog(path?: string): RuleCatalog`
- Default path: `docs/rule-catalog.yaml` relative to package root
- Parse YAML, validate with Zod, return typed catalog

**`src/rules/load-engine-contract.ts`**
- `loadEngineContract(path?: string): EngineContract`
- Default path: `docs/engine-contract.yaml`

**Depends on**: Task 1.2 (enum types), `yaml` + `zod` packages.

### Task 1.4: Repo acquisition

**`src/inventory/acquire-repo.ts`**
- `acquireRepo(context: AuditContext): Promise<LocalWorkspace>`
- Detect local path vs GitHub URL vs generic git URL
- Remote: shallow clone (depth=1) via `Bun.spawn("git", ["clone", "--depth", "1", ...])`
- Local: validate path exists and is a git repo
- Checkout specified ref
- Apply include/exclude path filters
- Collect git metadata (last commit, contributors, tags, signed tags)
- Clone to `/tmp/stop-git-std/<run-id>/`

**Depends on**: Task 1.2, Task 1.3.

### Task 1.5: File inventory and repo classification

**`src/inventory/enumerate-files.ts`**
- `enumerateFiles(workspace, excludePatterns): Promise<FileInventory>`
- Walk directory tree, respect exclude patterns + `max_files_default` (50000) + `max_file_size_bytes` (5MB)
- Return file list with extensions, sizes, paths, counts

**`src/inventory/classify-repo.ts`**
- `classifyRepo(inventory, workspace): RepoProfile`
- Language detection by file extension distribution
- Framework detection by marker files
- Category detection heuristics (web_app, api, ai_llm, agent_framework, skills_plugins, mcp_server, library_package, infrastructure, ci_cd)
- Build capability_summary

**`src/inventory/detect-frameworks.ts`**
- Framework detection helpers: marker file -> framework name map
- Ecosystem detection: npm, pip, cargo, gomod, etc.

**Depends on**: Task 1.4.

### Task 1.6: CLI entrypoint and engine stub

**`src/cli.ts`**
- Parse CLI args via commander: `<repo-path-or-url>`, `--ref`, `--env`, `--policy`, `--format`, `--output-dir`, `--include`, `--exclude`, `--enable-module`, `--disable-module`, `--runtime-mode`, `--adoption-mode`
- Construct AuditRequest, call `runAudit(request)`
- Exit codes: 0=PROCEED, 1=ABORT, 2=CAUTION

**`src/engine/run-audit.ts`** (M1 stub)
- `runAudit(request: AuditRequest): Promise<AuditResult>`
- Implements phases 1-4: context_capture, repository_acquisition, inventory_classification, module_routing
- Stubs phases 5-11

**`src/engine/router.ts`**
- `routeModules(profile, context, catalog): ActiveModules`
- Start with universal modules, expand by detected categories using engine contract routes
- Apply enabled/disabled overrides, deduplicate

**Depends on**: All above.

### Task 1.7: M1 tests

- `src/__tests__/models.test.ts` — Zod schema acceptance/rejection
- `src/__tests__/load-rule-catalog.test.ts` — Load actual YAML
- `src/__tests__/load-engine-contract.test.ts` — Load actual YAML
- `src/__tests__/classify-repo.test.ts` — Mock inventories -> correct categories
- `src/__tests__/router.test.ts` — Mock profiles -> correct module activation
- `src/__tests__/acquire-repo.test.ts` — Local path acquisition

Add to `package.json`:
```json
"scripts": { "test": "bun test", "dev": "bun run src/cli.ts" }
```

---

## Milestone 2 — Universal Analyzers

**Goal**: All 6 universal analysis modules + parsers. Each loads rules from catalog and emits normalized findings.

### Analyzer contract

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

interface AnalyzerOutput {
  findings: Finding[];
  moduleResult: ModuleResult;
}
```

### Task 2.1: Analyzer base infrastructure

**`src/plugins/analyzer-backend.ts`** — AnalyzerModule interface, AnalyzerOutput type.

**`src/plugins/builtin-ts.ts`** — Registry of all built-in TS analyzers.

**`src/analyzers/base.ts`** — Shared helpers:
- `matchFiles(inventory, patterns): string[]`
- `scanFileContent(path, regex): MatchResult[]`
- `readFileContent(path, maxSize): string | null`
- `emitFinding(rule, evidence, files, lineNumbers?): Finding`

### Task 2.2: Governance & Trust (GHA-TRUST-001–005)

**`src/analyzers/universal/governance-trust.ts`**
- path_check: SECURITY.md, CODEOWNERS
- github_api_lookup: archived/abandoned (git metadata fallback)
- tag_signature_verification: signed tags via git
- git_metadata_analysis: contributor shift detection

### Task 2.3: Supply Chain (GHA-SUPPLY-001–005)

**`src/analyzers/universal/supply-chain.ts`**
- manifest_parse: lockfile presence, floating versions, git/URL deps
- osv_lookup: **stub** (returns empty + warning)
- file_signature_scan: binary detection

**`src/adapters/osv.ts`** — Stub interface.

### Task 2.4: Secrets (GHA-SECRETS-001–003)

**`src/analyzers/universal/secrets.ts`**
- regex_scan: PEM private key blocks
- path_risk_scan: `.env` files with secret-like entries
- entropy_scan: Shannon entropy near auth keywords
- Must redact evidence snippets

### Task 2.5: Dangerous Execution (GHA-EXEC-001–005)

**`src/analyzers/universal/dangerous-execution.ts`**
- regex_scan: curl|bash patterns
- manifest_parse: install lifecycle hooks
- regex fallback for AST rules (subprocess shell=True, unsafe deser, remote code load) with confidence downgrade

**`src/parsers/package-json.ts`** — Parse scripts, deps, detect hooks + git/URL deps.

### Task 2.6: CI/CD (GHA-CI-001–005)

**`src/analyzers/universal/ci-cd.ts`**
- yaml_parse: pull_request_target triggers, broad permissions, unpinned actions
- workflow_semantics: shell injection via `${{ github.event.* }}` in run steps
- self-hosted runner + untrusted trigger detection

**`src/parsers/workflow-yaml.ts`** — Parse GH Actions YAML: triggers, jobs, steps, permissions, uses, run.

### Task 2.7: Infrastructure (GHA-INFRA-001–003)

**`src/analyzers/universal/infrastructure.ts`**
- dockerfile_parse: USER directive, FROM :latest
- yaml_parse: K8s RBAC wildcard detection

**`src/parsers/dockerfile.ts`** — Line-based parser: FROM, USER, RUN.

**`src/parsers/k8s-yaml.ts`** — Role/ClusterRole broad permission detection.

### Task 2.8: Wire universal analyzers into engine

**`src/engine/run-audit.ts`** (update) — Implement phase 5 (universal_analysis):
- Iterate active universal modules, call each analyzer
- Respect timeout_seconds_per_phase (300s)
- continue_on_module_error behavior
- Collect findings + module results

### Task 2.9: M2 tests

One test file per analyzer + per parser. Create temp directories with specific file contents, run analyzer, assert expected findings with correct severity/confidence/axis_impacts.

---

## Milestone 3 — Typed Analyzers

**Goal**: All 7 category-specific modules activated by repo classification.

### Task 3.1: Web (GHA-WEB-001–002)
**`src/analyzers/typed/web.ts`** — Debug mode config detection, unescaped template output (regex heuristic).

### Task 3.2: API (GHA-API-001–003)
**`src/analyzers/typed/api.ts`** — Auth guard detection on sensitive routes, CORS config, request-to-model binding.

### Task 3.3: AI/LLM (GHA-AI-001–003)
**`src/analyzers/typed/ai-llm.ts`** — Model output -> exec/tool dispatch, secrets in prompts, missing rate/budget controls.

### Task 3.4: Agent Framework (GHA-AGENT-001–002)
**`src/analyzers/typed/agent-framework.ts`** — Shell+write+network without approval gate, shared state without isolation.

### Task 3.5: Skills/Plugins (GHA-PLUGIN-001–002)
**`src/analyzers/typed/skills-plugins.ts`** — Broad manifest permissions, instruction identity/guardrail override patterns.

### Task 3.6: MCP Server (GHA-MCP-001–003)
**`src/analyzers/typed/mcp-server.ts`** — Unrestricted shell tool, SSRF-capable fetch, credential forwarding.

### Task 3.7: Library/Package (GHA-PKG-001)
**`src/analyzers/typed/library-package.ts`** — Import/init-time network or process side effects.

### Task 3.8: Wire typed analyzers into engine
**`src/engine/run-audit.ts`** (update) — Implement phase 6 (typed_analysis), same pattern as universal.

### Task 3.9: M3 tests
One test file per typed analyzer.

---

## Milestone 4 — Scoring, Policy & Reporting

**Goal**: Finding normalization, 3-axis scoring, policy decisions, all 3 report formats.

### Task 4.1: Finding normalization

**`src/engine/normalize-findings.ts`**
- Merge universal + typed + runtime findings
- Deduplicate by `(id, files, evidence.type)`, merge strategy: combine_evidence_records
- Attach module names, default standard mappings (stub)
- Apply suppressions from `.stop-git-std.suppressions.yaml`
- Suppressed findings remain with `suppressed: true`

### Task 4.2: Scoring engine

**`src/engine/scoring.ts`**
- `computeScores(findings, profile, context, moduleResults, contract): Scores`
- Formula: `weighted_axis_value = axis_impact * severity_weight * confidence_multiplier / 20`
- Environment multiplier on abuse_potential only
- Subtract trust credits from repo_profile (signed_tags: 8, security_md: 3, codeowners: 2, pinned_actions_ratio_high: 4)
- Clamp 0-100
- Confidence model: high/medium/low based on failed_modules_ratio, AST support, runtime mode

### Task 4.3: Policy engine

**`src/engine/policy.ts`**
- `evaluatePolicy(findings, scores, context, contract): Decision`
- Precedence: hard_stop -> ABORT threshold -> CAUTION threshold -> PROCEED_WITH_CONSTRAINTS threshold -> PROCEED
- Hard-stop rules from `policy_baselines.hard_stop_patterns`
- Three profiles: strict, balanced, advisory
- Generate constraints + reasons

### Task 4.4: Terminal reporter

**`src/reporting/terminal.ts`** — Color-coded decision, executive summary, top findings, score breakdown, module coverage, constraints.

### Task 4.5: JSON reporter

**`src/reporting/json.ts`** — Full structured output matching engine contract artifact schemas.

### Task 4.6: Markdown reporter

**`src/reporting/markdown.ts`** — Structured markdown for PRs and review artifacts.

### Task 4.7: Finalize engine pipeline

**`src/engine/run-audit.ts`** (finalize) — Wire phases 7-11:
- `runtime_validation`: no-op unless explicitly enabled
- `finding_normalization`: call normalizeFindings
- `scoring`: call computeScores
- `policy_decision`: call evaluatePolicy
- `reporting`: call reporters per output_formats
- Build RunManifest with timing and status

**`src/models/audit-result.ts`** — Type containing all artifacts.

### Task 4.8: M4 tests

- normalize-findings.test.ts — dedup, suppression
- scoring.test.ts — known findings -> expected scores, clamping, env multiplier
- policy.test.ts — all three profiles, hard-stop triggers
- reporters/*.test.ts — output validation

---

## Milestone 5 — Extensibility

**Goal**: Plugin backend, Python subprocess stub, GitHub Action, full adapters.

### Task 5.1: Plugin backend interface

**`src/plugins/analyzer-backend.ts`** (finalize)
- `AnalyzerBackend` interface: `type`, `canHandle()`, `execute()`
- Backend registry + dispatcher

### Task 5.2: Python subprocess backend stub

**`src/plugins/python-subprocess.ts`**
- stdin/stdout JSON protocol
- MVP: logs "not yet available", returns empty

### Task 5.3: GitHub Action wrapper

**`action.yml`** — Action metadata, inputs, runs src/cli.ts via Bun.

**`.github/workflows/self-test.yml`** — Dogfood: run on self.

### Task 5.4: GitHub API adapter

**`src/adapters/github-api.ts`** — getRepoMetadata, checkArchived, getLatestRelease. Optional enrichment, graceful degradation without GITHUB_TOKEN.

### Task 5.5: Scorecard adapter stub

**`src/adapters/scorecard.ts`** — OpenSSF Scorecard API interface, stub.

### Task 5.6: OSV adapter (full)

**`src/adapters/osv.ts`** (upgrade) — Real HTTP to OSV.dev API.

### Task 5.7: M5 tests

- backend-dispatch.test.ts
- github-api.test.ts (mocked)
- osv.test.ts (mocked)

---

## Dependency Graph

```
M1.2 (models) ──┬── M1.3 (YAML loaders) ──┬── M1.4 (acquire repo)
                 │                          ├── M1.5 (classify repo)
                 │                          └── M1.6 (CLI + router + engine stub)
                 │
                 └── M2.1 (analyzer base) ──┬── M2.2-M2.7 (universal analyzers)
                                            └── M3.1-M3.7 (typed analyzers)
                                                     │
                                                     └── M4.1 (normalization) ── M4.2 (scoring) ── M4.3 (policy)
                                                                                                        │
                                                                                                        └── M4.4-M4.6 (reporters)
                                                                                                               │
                                                                                                               └── M5 (extensibility)
```

## Full File Manifest (54 files)

### Milestone 1 (21 files)
1. `src/models/enums.ts`
2. `src/models/audit-request.ts`
3. `src/models/audit-context.ts`
4. `src/models/finding.ts`
5. `src/models/scores.ts`
6. `src/models/decision.ts`
7. `src/models/module-result.ts`
8. `src/models/run-manifest.ts`
9. `src/models/repo-profile.ts`
10. `src/models/local-workspace.ts`
11. `src/models/index.ts`
12. `src/rules/types.ts`
13. `src/rules/load-rule-catalog.ts`
14. `src/rules/load-engine-contract.ts`
15. `src/inventory/acquire-repo.ts`
16. `src/inventory/enumerate-files.ts`
17. `src/inventory/classify-repo.ts`
18. `src/inventory/detect-frameworks.ts`
19. `src/engine/router.ts`
20. `src/engine/run-audit.ts`
21. `src/cli.ts`

### Milestone 2 (14 files)
22. `src/plugins/analyzer-backend.ts`
23. `src/plugins/builtin-ts.ts`
24. `src/analyzers/base.ts`
25. `src/parsers/package-json.ts`
26. `src/parsers/workflow-yaml.ts`
27. `src/parsers/dockerfile.ts`
28. `src/parsers/k8s-yaml.ts`
29. `src/analyzers/universal/governance-trust.ts`
30. `src/analyzers/universal/secrets.ts`
31. `src/analyzers/universal/dangerous-execution.ts`
32. `src/analyzers/universal/supply-chain.ts`
33. `src/analyzers/universal/ci-cd.ts`
34. `src/analyzers/universal/infrastructure.ts`
35. `src/adapters/osv.ts` (stub)

### Milestone 3 (7 files)
36. `src/analyzers/typed/web.ts`
37. `src/analyzers/typed/api.ts`
38. `src/analyzers/typed/ai-llm.ts`
39. `src/analyzers/typed/agent-framework.ts`
40. `src/analyzers/typed/skills-plugins.ts`
41. `src/analyzers/typed/mcp-server.ts`
42. `src/analyzers/typed/library-package.ts`

### Milestone 4 (7 files)
43. `src/engine/normalize-findings.ts`
44. `src/engine/scoring.ts`
45. `src/engine/policy.ts`
46. `src/models/audit-result.ts`
47. `src/reporting/terminal.ts`
48. `src/reporting/json.ts`
49. `src/reporting/markdown.ts`

### Milestone 5 (5 files)
50. `src/plugins/python-subprocess.ts`
51. `src/adapters/github-api.ts`
52. `src/adapters/scorecard.ts`
53. `src/adapters/osv.ts` (full)
54. `action.yml`
