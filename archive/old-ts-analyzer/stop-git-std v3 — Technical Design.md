# stop-git-std v3 — Technical Design

## Status
Draft build specification for implementation.

## 1. Purpose

`stop-git-std` is a detection-first repository safety auditor for evaluating whether a Git repository is safe to **adopt**, **run**, and **integrate**.

It is designed to answer four separate questions:

1. **Is the source trustworthy enough to consider?**
2. **Is the code/configuration insecure or operationally risky?**
3. **Could the repo abuse its execution environment if run?**
4. **What controls or constraints are required before adoption?**

This tool audits the full repository surface, not just one artifact class. A single repository may contain application code, workflows, infra, containers, agent logic, skills/plugins, MCP servers, and dependency manifests at the same time.

---

## 2. Non-Goals

Version 3 does not aim to:

- prove absence of vulnerabilities
- replace full manual application pentesting
- fully implement all OWASP ASVS requirements
- perform deep symbolic execution
- support perfect interprocedural taint tracking across all languages in MVP
- certify provenance across every build ecosystem

The goal is **high-signal pre-adoption safety review**, not formal verification.

---

## 3. Product Definition

### 3.1 Primary output

A structured report with:

- repository profile
- detected component categories
- findings with severity, confidence, evidence, and remediation
- axis scores:
  - trustworthiness
  - exploitability
  - abuse potential
- final decision:
  - `PROCEED`
  - `PROCEED_WITH_CONSTRAINTS`
  - `CAUTION`
  - `ABORT`

### 3.2 Primary users

- security engineers evaluating third-party repos
- platform engineers deciding whether to adopt internal/external tooling
- AI platform teams evaluating agent, MCP, or plugin ecosystems
- developers doing local due diligence before running unknown code

### 3.3 Deployment targets

Primary target:
- standalone CLI

Secondary later target:
- GitHub Action wrapper around the same engine

### 3.4 Implementation stance

Primary implementation:
- Bun (latest)
- TypeScript

Optional later extension:
- Python deep analyzers invoked through a plugin/subprocess interface for advanced AST, taint, or semantic analysis where Bun/TypeScript is not the best fit

The Bun/TypeScript engine remains the source of truth for:

- CLI behavior
- repo acquisition
- inventory/classification
- analyzer routing
- finding normalization
- scoring
- policy decisions
- reporting

---

## 4. System Architecture

```text
User Input
  └── repo URL / local path / ref / target environment / permissions

Phase 0: Context Capture
  └── audit_context.json

Phase 1: Inventory & Classification
  └── repo_profile.json

Phase 2: Universal Static Analysis
  ├── governance/trust module
  ├── supply-chain module
  ├── secrets module
  ├── dangerous execution module
  ├── CI/CD module
  ├── infra/container module
  └── license module

Phase 3: Type-Specific Modules
  ├── web
  ├── api
  ├── ai_llm
  ├── agent_framework
  ├── skills_plugins
  ├── mcp_server
  └── library_package

Phase 4: Optional Behavioral Validation
  └── runtime_observations.json

Phase 5: Finding Normalization
  └── findings.json

Phase 6: Scoring Engine
  └── scores.json

Phase 7: Policy Engine
  └── final_decision.json

Report Generation
  ├── markdown report
  ├── json bundle
  └── SARIF (optional)