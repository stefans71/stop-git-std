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
| 7 | Scoring divisor | `/10` (per engine contract spec) |
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
- **Scoring divisor**: `/10` as specified in engine contract.
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

```typescript
// src/models/enums.ts
import { z } from "zod";

export const Severity = z.enum(["info", "low", "medium", "high", "critical"]);
export type Severity = z.infer<typeof Severity>;

export const Confidence = z.enum(["low", "medium", "high"]);
export type Confidence = z.infer<typeof Confidence>;

export const ProofType = z.enum(["static", "heuristic", "runtime"]);
export type ProofType = z.infer<typeof ProofType>;

export const DecisionValue = z.enum(["PROCEED", "PROCEED_WITH_CONSTRAINTS", "CAUTION", "ABORT"]);
export type DecisionValue = z.infer<typeof DecisionValue>;

export const ModuleStatus = z.enum(["pending", "running", "success", "partial", "failed", "skipped"]);
export type ModuleStatus = z.infer<typeof ModuleStatus>;

export const Environment = z.enum([
  "developer_laptop",
  "ci_runner",
  "container_isolated",
  "offline_analysis",
  "production_service",
]);
export type Environment = z.infer<typeof Environment>;

export const RuntimeMode = z.enum(["off", "install_only", "build", "smoke"]);
export type RuntimeMode = z.infer<typeof RuntimeMode>;

export const AdoptionMode = z.enum(["third_party", "internal", "fork_review", "pre_merge"]);
export type AdoptionMode = z.infer<typeof AdoptionMode>;

export const PolicyProfile = z.enum(["strict", "balanced", "advisory"]);
export type PolicyProfile = z.infer<typeof PolicyProfile>;

export const OutputFormat = z.enum(["json", "yaml", "markdown", "sarif"]);
export type OutputFormat = z.infer<typeof OutputFormat>;

export const RunManifestStatus = z.enum(["success", "partial", "failed"]);
export type RunManifestStatus = z.infer<typeof RunManifestStatus>;

export const RepoCategory = z.enum([
  "web_app",
  "api",
  "ai_llm",
  "agent_framework",
  "skills_plugins",
  "mcp_server",
  "library_package",
  "infrastructure",
  "ci_cd",
]);
export type RepoCategory = z.infer<typeof RepoCategory>;
```

**`src/models/audit-request.ts`** — Zod schema matching `inputs.audit_request` from engine contract.

```typescript
// src/models/audit-request.ts
import { z } from "zod";
import {
  Environment,
  RuntimeMode,
  AdoptionMode,
  OutputFormat,
  PolicyProfile,
} from "./enums";

export const AuditRequestSchema = z.object({
  repo_target: z.string().min(1),
  ref: z.string().default("default_branch"),
  target_environment: Environment.default("offline_analysis"),
  expected_permissions: z.array(z.string()).default([]),
  runtime_mode: RuntimeMode.default("off"),
  adoption_mode: AdoptionMode.default("third_party"),
  output_formats: z.array(OutputFormat).default(["json", "markdown"]),
  enabled_modules: z.array(z.string()).default([]),
  disabled_modules: z.array(z.string()).default([]),
  include_paths: z.array(z.string()).default([]),
  exclude_paths: z.array(z.string()).default([
    ".git/**",
    "node_modules/**",
    "vendor/**",
    "dist/**",
    "build/**",
    "target/**",
  ]),
  allow_network_during_runtime: z.boolean().default(false),
  policy_profile: PolicyProfile.default("balanced"),
  notes: z.string().default(""),
});

export type AuditRequest = z.infer<typeof AuditRequestSchema>;
```

**`src/models/audit-context.ts`** — Zod schema matching `artifacts.audit_context`.

```typescript
// src/models/audit-context.ts
import { z } from "zod";
import { Environment, RuntimeMode, AdoptionMode } from "./enums";

export const AuditContextSchema = z.object({
  repo_target: z.string(),
  ref: z.string(),
  target_environment: Environment,
  expected_permissions: z.array(z.string()),
  runtime_validation_enabled: z.boolean(),
  runtime_mode: RuntimeMode.optional(),
  adoption_mode: AdoptionMode.optional(),
  notes: z.string().optional(),
});

export type AuditContext = z.infer<typeof AuditContextSchema>;
```

**`src/models/repo-profile.ts`** — Languages, frameworks, ecosystems, detected_categories, artifacts (manifests/workflows/containers/infra/binaries), counts, high_risk_files, capability_summary. Type `RepoCategory` = union of all category strings.

```typescript
// src/models/repo-profile.ts
import { z } from "zod";
import { RepoCategory } from "./enums";

export const CapabilitySummarySchema = z.object({
  shell_exec: z.boolean().default(false),
  filesystem_read: z.boolean().default(false),
  filesystem_write: z.boolean().default(false),
  network_access: z.boolean().default(false),
  credential_access_signals: z.boolean().default(false),
  ci_privileged_signals: z.boolean().default(false),
});

export type CapabilitySummary = z.infer<typeof CapabilitySummarySchema>;

export const RepoArtifactsSchema = z.object({
  manifests: z.array(z.string()).default([]),
  workflows: z.array(z.string()).default([]),
  containers: z.array(z.string()).default([]),
  infra: z.array(z.string()).default([]),
  binaries: z.array(z.string()).default([]),
});

export type RepoArtifacts = z.infer<typeof RepoArtifactsSchema>;

export const RepoCountsSchema = z.object({
  total_files: z.number().int().default(0),
  scanned_files: z.number().int().default(0),
  skipped_files: z.number().int().default(0),
});

export type RepoCounts = z.infer<typeof RepoCountsSchema>;

export const RepoProfileSchema = z.object({
  languages: z.array(z.string()),
  frameworks: z.array(z.string()),
  ecosystems: z.array(z.string()).default([]),
  detected_categories: z.array(RepoCategory),
  artifacts: RepoArtifactsSchema,
  counts: RepoCountsSchema.optional(),
  high_risk_files: z.array(z.string()),
  capability_summary: CapabilitySummarySchema.optional(),
  // Trust signal fields — populated during inventory/classification
  signed_tags_count: z.number().default(0),
  pinned_actions_ratio: z.number().min(0).max(1).default(0),
});

export type RepoProfile = z.infer<typeof RepoProfileSchema>;
```

**`src/models/finding.ts`** — Full finding schema with axis_impacts, evidence (type + records), remediation, mapped_standards, suppression fields.

```typescript
// src/models/finding.ts
import { z } from "zod";
import { Severity, Confidence, ProofType } from "./enums";

export const AxisImpactsSchema = z.object({
  trustworthiness: z.number(),
  exploitability: z.number(),
  abuse_potential: z.number(),
});

export type AxisImpacts = z.infer<typeof AxisImpactsSchema>;

export const EvidenceSchema = z.object({
  type: z.string(),
  records: z.array(z.record(z.unknown())),
});

export type Evidence = z.infer<typeof EvidenceSchema>;

export const FindingSchema = z.object({
  id: z.string(),
  title: z.string(),
  category: z.string(),
  subcategory: z.string().optional(),
  severity: Severity,
  confidence: Confidence,
  proof_type: ProofType,
  module_name: z.string().optional(),
  files: z.array(z.string()).optional(),
  line_numbers: z.array(z.number().int()).optional(),
  axis_impacts: AxisImpactsSchema,
  evidence: EvidenceSchema,
  remediation: z.string(),
  mapped_standards: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
  suppressed: z.boolean().default(false),
  suppression_reason: z.string().default(""),
});

export type Finding = z.infer<typeof FindingSchema>;
```

**`src/models/scores.ts`** — Three axes (0-100), confidence, component_breakdown, environment_multiplier_applied.

```typescript
// src/models/scores.ts
import { z } from "zod";
import { Confidence } from "./enums";

export const ScoresSchema = z.object({
  trustworthiness: z.number().int().min(0).max(100),
  exploitability: z.number().int().min(0).max(100),
  abuse_potential: z.number().int().min(0).max(100),
  confidence: Confidence,
  component_breakdown: z.record(z.unknown()).optional(),
  environment_multiplier_applied: z.number().optional(),
});

export type Scores = z.infer<typeof ScoresSchema>;
```

**`src/models/decision.ts`** — Value, reasons, constraints, hard_stop_triggered, triggered_by_rules, manual_review_required.

```typescript
// src/models/decision.ts
import { z } from "zod";
import { DecisionValue } from "./enums";

export const DecisionSchema = z.object({
  value: DecisionValue,
  reasons: z.array(z.string()),
  constraints: z.array(z.string()),
  hard_stop_triggered: z.boolean().optional(),
  triggered_by_rules: z.array(z.string()).optional(),
  manual_review_required: z.boolean().optional(),
});

export type Decision = z.infer<typeof DecisionSchema>;
```

**`src/models/module-result.ts`** — Module name, status, timing, findings_emitted, warnings, errors, coverage.

```typescript
// src/models/module-result.ts
import { z } from "zod";
import { ModuleStatus } from "./enums";

export const ModuleCoverageSchema = z.object({
  files_considered: z.number().int().optional(),
  files_scanned: z.number().int().optional(),
  parser_supported: z.boolean().optional(),
  confidence_modifier: z.number().optional(),
});

export type ModuleCoverage = z.infer<typeof ModuleCoverageSchema>;

export const ModuleResultSchema = z.object({
  module_name: z.string(),
  status: ModuleStatus,
  started_at: z.string(),
  completed_at: z.string().optional(),
  findings_emitted: z.number().int(),
  warnings: z.array(z.string()).default([]),
  errors: z.array(z.string()).default([]),
  coverage: ModuleCoverageSchema.optional(),
});

export type ModuleResult = z.infer<typeof ModuleResultSchema>;
```

**`src/models/run-manifest.ts`** — run_id, engine_version, rule_catalog_version, timing, repo_target, ref, status.

```typescript
// src/models/run-manifest.ts
import { z } from "zod";
import { RunManifestStatus, Environment, RuntimeMode, PolicyProfile } from "./enums";

export const RunManifestSchema = z.object({
  run_id: z.string(),
  engine_version: z.string(),
  rule_catalog_version: z.number().int(),
  started_at: z.string(),
  completed_at: z.string().optional(),
  repo_target: z.string(),
  ref: z.string(),
  target_environment: Environment.optional(),
  runtime_mode: RuntimeMode.optional(),
  policy_profile: PolicyProfile.optional(),
  status: RunManifestStatus.optional(),
});

export type RunManifest = z.infer<typeof RunManifestSchema>;
```

**`src/models/local-workspace.ts`** — rootPath, gitMetadata (lastCommitDate, contributors, tags, signedTags), isLocal.

```typescript
// src/models/local-workspace.ts

export interface GitMetadata {
  lastCommitDate: string | null;
  contributors: string[];
  tags: string[];
  signedTags: string[];
}

export interface LocalWorkspace {
  rootPath: string;
  gitMetadata: GitMetadata;
  isLocal: boolean;
}
```

**`src/models/index.ts`** — Barrel export.

```typescript
// src/models/index.ts
export * from "./enums";
export * from "./audit-request";
export * from "./audit-context";
export * from "./repo-profile";
export * from "./finding";
export * from "./scores";
export * from "./decision";
export * from "./module-result";
export * from "./run-manifest";
export * from "./local-workspace";
export * from "./audit-result";
```

**Blocks**: Everything else depends on this.

### Task 1.3: YAML rule catalog and engine contract loaders

**`src/rules/types.ts`** — Types for RuleDefinition, RuleCatalog, EngineContract, PolicyProfileConfig, ScoringDefaults, DetectionSpec.

```typescript
// src/rules/types.ts
import { z } from "zod";
import { Severity, Confidence, ProofType } from "../models/enums";

// --- Detection spec matching rule catalog structure ---

export const DetectionSpecSchema = z.object({
  primary_method: z.string(),
  secondary_methods: z.array(z.string()).optional(),
  logic: z.string(),
  params: z.record(z.unknown()).optional(),
  file_patterns: z.array(z.string()).optional(),
  regex: z.string().optional(),
});

export type DetectionSpec = z.infer<typeof DetectionSpecSchema>;

// --- Evidence shape ---

export const EvidenceShapeSchema = z.object({
  type: z.string(),
  fields: z.array(z.string()),
});

export type EvidenceShape = z.infer<typeof EvidenceShapeSchema>;

// --- Axis impacts (integer from catalog) ---

export const RuleAxisImpactsSchema = z.object({
  trustworthiness: z.number(),
  exploitability: z.number(),
  abuse_potential: z.number(),
});

// --- Policy hints per rule ---

export const PolicyHintsSchema = z.object({
  hard_stop: z.boolean(),
  constrain_if_present: z.boolean(),
});

// --- Single rule definition ---

export const RuleDefinitionSchema = z.object({
  id: z.string(),
  title: z.string(),
  category: z.string(),
  subcategory: z.string().optional(),
  default_severity: Severity,
  default_confidence: Confidence,
  proof_type: ProofType,
  rationale: z.string().optional(),
  applies_to: z.record(z.unknown()).optional(),
  detection: DetectionSpecSchema,
  evidence_shape: EvidenceShapeSchema,
  axis_impacts: RuleAxisImpactsSchema,
  remediation: z.string(),
  policy_hints: PolicyHintsSchema,
});

export type RuleDefinition = z.infer<typeof RuleDefinitionSchema>;

// --- Module definition in catalog ---

export const ModuleDefinitionSchema = z.object({
  description: z.string(),
  recommended_methods: z.array(z.string()).optional(),
  rules: z.array(RuleDefinitionSchema),
});

export type ModuleDefinition = z.infer<typeof ModuleDefinitionSchema>;

// --- Scoring defaults from catalog ---

export const ScoringDefaultsSchema = z.object({
  severity_weights: z.record(Severity, z.number()),
  confidence_multipliers: z.record(Confidence, z.number()),
  environment_abuse_multipliers: z.record(z.string(), z.number()),
});

export type ScoringDefaults = z.infer<typeof ScoringDefaultsSchema>;

// --- Top-level rule catalog ---

export const RuleCatalogSchema = z.object({
  version: z.number(),
  name: z.string(),
  status: z.string(),
  purpose: z.string(),
  meta: z.record(z.unknown()),
  scoring_defaults: ScoringDefaultsSchema,
  modules: z.record(z.string(), ModuleDefinitionSchema),
  runtime_rules: ModuleDefinitionSchema.optional(),
  policy_baselines: z.object({
    hard_stop_patterns: z.array(z.string()),
    proceed_with_constraints_examples: z.array(z.string()).optional(),
  }),
});

export type RuleCatalog = z.infer<typeof RuleCatalogSchema>;

// --- Policy profile threshold config (from engine contract) ---

export const ThresholdConfigSchema = z.object({
  abuse_potential_gte: z.number().optional(),
  or_critical_findings_gte: z.number().optional(),
  exploitability_gte: z.number().optional(),
  or_high_findings_gte: z.number().optional(),
  or_any_runtime_findings: z.boolean().optional(),
  disabled: z.boolean().optional(),
});

export type ThresholdConfig = z.infer<typeof ThresholdConfigSchema>;

export const PolicyProfileConfigSchema = z.object({
  hard_stop_behavior: z.enum(["abort", "caution"]),
  thresholds: z.object({
    abort: ThresholdConfigSchema,
    caution: ThresholdConfigSchema,
    proceed_with_constraints: ThresholdConfigSchema,
  }),
});

export type PolicyProfileConfig = z.infer<typeof PolicyProfileConfigSchema>;

// --- Engine contract Zod schema (C2: replaces bare interface with validated schema) ---

export const EngineContractSchema = z.object({
  version: z.number(),
  name: z.string(),
  status: z.string().optional(),
  purpose: z.string().optional(),
  references: z.record(z.string()).optional(),
  meta: z.record(z.unknown()).optional(),
  execution_defaults: z.object({
    clone: z.object({
      strategy: z.string(),
      depth: z.number(),
      recurse_submodules: z.boolean(),
    }),
    performance: z.object({
      max_file_size_bytes: z.number(),
      max_files_default: z.number(),
      max_ast_files_per_language: z.number(),
      timeout_seconds_per_phase: z.record(z.string(), z.number()),
    }),
    behavior: z.object({
      continue_on_module_error: z.boolean(),
      emit_partial_results_on_failure: z.boolean(),
      fail_closed_on_runtime_hard_stop: z.boolean(),
    }),
  }),
  enums: z.record(z.array(z.string())).optional(),
  inputs: z.record(z.unknown()).optional(),
  artifacts: z.record(z.unknown()).optional(),
  phase_order: z.array(z.string()),
  phases: z.record(z.unknown()).optional(),
  module_routing: z.object({
    universal_modules: z.array(z.string()),
    category_routes: z.record(z.string(), z.array(z.string())),
  }),
  rule_evaluation_contract: z.record(z.unknown()).optional(),
  confidence_model: z.object({
    description: z.string().optional(),
    inputs: z.array(z.string()).optional(),
    rules: z.array(z.object({
      name: z.string(),
      when: z.record(z.unknown()).optional(),
      output: z.string(),
    })),
  }),
  confidence_model_version: z.string().default("mvp-1"),
  scoring_model: z.object({
    description: z.string().optional(),
    steps: z.array(z.unknown()),
    formulas: z.record(z.string(), z.string()),
  }),
  policy_profiles: z.record(z.string(), PolicyProfileConfigSchema),
  hard_stop_logic: z.object({
    source: z.object({
      from_rule_catalog_policy_baselines: z.boolean(),
    }),
    behavior: z.record(z.string(), z.string()),
    exceptions: z.object({
      allowed_only_with_manual_override: z.boolean().optional(),
      override_requires: z.array(z.string()).optional(),
    }).optional(),
  }),
  suppressions: z.record(z.unknown()).optional(),
  error_handling: z.record(z.unknown()).optional(),
  coverage_contract: z.record(z.unknown()).optional(),
  sarif_mapping: z.record(z.unknown()).optional(),
  decision_generation: z.record(z.unknown()).optional(),
  example_run: z.record(z.unknown()).optional(),
  implementation_notes: z.record(z.unknown()).optional(),
  next_expansion_candidates: z.array(z.string()).optional(),
});

export type EngineContract = z.infer<typeof EngineContractSchema>;

// --- Legacy interface kept for reference (replaced by Zod schema above) ---
// export interface EngineContract {
//   version: number;
//   name: string;
//   execution_defaults: { ... };
//   ...
// }

export interface EngineContractLegacy {
  version: number;
  name: string;
  execution_defaults: {
    clone: { strategy: string; depth: number; recurse_submodules: boolean };
    performance: {
      max_file_size_bytes: number;
      max_files_default: number;
      max_ast_files_per_language: number;
      timeout_seconds_per_phase: Record<string, number>;
    };
    behavior: {
      continue_on_module_error: boolean;
      emit_partial_results_on_failure: boolean;
      fail_closed_on_runtime_hard_stop: boolean;
    };
  };
  phase_order: string[];
  module_routing: {
    universal_modules: string[];
    category_routes: Record<string, string[]>;
  };
  scoring_model: {
    steps: unknown[];
    formulas: Record<string, string>;
  };
  policy_profiles: Record<string, PolicyProfileConfig>;
  hard_stop_logic: {
    source: { from_rule_catalog_policy_baselines: boolean };
    behavior: Record<string, string>;
  };
}
```

**`src/rules/load-rule-catalog.ts`**
- `loadRuleCatalog(path?: string): RuleCatalog`
- Default path: `docs/rule-catalog.yaml` relative to package root
- Parse YAML, validate with Zod, return typed catalog

```typescript
// src/rules/load-rule-catalog.ts
import { parse as parseYaml } from "yaml";
import { RuleCatalogSchema, type RuleCatalog } from "./types";

export function loadRuleCatalog(path?: string): RuleCatalog {
  const resolvedPath = path ?? new URL("../../docs/rule-catalog.yaml", import.meta.url).pathname;
  const raw = Bun.file(resolvedPath);
  // Bun.file().text() is async; use readFileSync for sync loading
  const text = require("fs").readFileSync(resolvedPath, "utf-8");
  const parsed = parseYaml(text);
  return RuleCatalogSchema.parse(parsed);
}
```

**`src/rules/load-engine-contract.ts`**
- `loadEngineContract(path?: string): EngineContract`
- Default path: `docs/engine-contract.yaml`

```typescript
// src/rules/load-engine-contract.ts
import { parse as parseYaml } from "yaml";
import { EngineContractSchema, type EngineContract } from "./types";

export function loadEngineContract(path?: string): EngineContract {
  const resolvedPath = path ?? new URL("../../docs/engine-contract.yaml", import.meta.url).pathname;
  const text = require("fs").readFileSync(resolvedPath, "utf-8");
  const parsed = parseYaml(text);
  // C2: Full Zod validation — replaces bare `parsed as EngineContract` cast
  return EngineContractSchema.parse(parsed);
}
```

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

```typescript
// src/inventory/acquire-repo.ts
import type { AuditContext } from "../models/audit-context";
import type { LocalWorkspace, GitMetadata } from "../models/local-workspace";

export async function acquireRepo(
  context: AuditContext,
  runId: string
): Promise<LocalWorkspace> {
  // Implementation: detect local vs remote, clone or open, collect metadata
  // ...
}

/** Determine if target is a local path, GitHub URL, or generic git URL */
export function classifyTarget(
  repoTarget: string
): "local" | "github" | "git" {
  // ...
}

/** Shallow clone a remote repo into /tmp/stop-git-std/<runId>/ */
export async function cloneRepo(
  url: string,
  ref: string,
  destDir: string,
  depth?: number
): Promise<void> {
  // Bun.spawn("git", ["clone", "--depth", String(depth ?? 1), url, destDir])
  // ...
}

/** Collect git metadata from a local repo path */
export async function collectGitMetadata(
  repoPath: string
): Promise<GitMetadata> {
  // ...
}
```

**Depends on**: Task 1.2, Task 1.3.

### Task 1.5: File inventory and repo classification

**`src/inventory/enumerate-files.ts`**
- `enumerateFiles(workspace, excludePatterns): Promise<FileInventory>`
- Walk directory tree, respect exclude patterns + `max_files_default` (50000) + `max_file_size_bytes` (5MB)
- Return file list with extensions, sizes, paths, counts

```typescript
// src/inventory/enumerate-files.ts
import type { LocalWorkspace } from "../models/local-workspace";

export interface FileEntry {
  path: string;
  relativePath: string;
  extension: string;
  sizeBytes: number;
}

export interface FileInventory {
  files: FileEntry[];
  totalFiles: number;
  scannedFiles: number;
  skippedFiles: number;
  extensionCounts: Record<string, number>;
}

export async function enumerateFiles(
  workspace: LocalWorkspace,
  excludePatterns: string[],
  maxFiles?: number,
  maxFileSizeBytes?: number
): Promise<FileInventory> {
  // Walk workspace.rootPath, apply exclude globs, enforce limits
  // maxFiles defaults to 50000, maxFileSizeBytes defaults to 5242880
  // ...
}
```

**`src/inventory/classify-repo.ts`**
- `classifyRepo(inventory, workspace): RepoProfile`
- Language detection by file extension distribution
- Framework detection by marker files
- Category detection heuristics (web_app, api, ai_llm, agent_framework, skills_plugins, mcp_server, library_package, infrastructure, ci_cd)
- Build capability_summary

```typescript
// src/inventory/classify-repo.ts
import type { FileInventory } from "./enumerate-files";
import type { LocalWorkspace } from "../models/local-workspace";
import type { RepoProfile } from "../models/repo-profile";

export function classifyRepo(
  inventory: FileInventory,
  workspace: LocalWorkspace
): RepoProfile {
  // ...
}

export function detectLanguages(
  extensionCounts: Record<string, number>
): string[] {
  // Map extensions to language names, return sorted by frequency
  // ...
}

export function detectCategories(
  inventory: FileInventory,
  frameworks: string[],
  languages: string[]
): string[] {
  // Heuristic classification into RepoCategory values
  // ...
}
```

**`src/inventory/detect-frameworks.ts`**
- Framework detection helpers: marker file -> framework name map
- Ecosystem detection: npm, pip, cargo, gomod, etc.

```typescript
// src/inventory/detect-frameworks.ts
import type { FileInventory } from "./enumerate-files";

/** Marker file -> framework name map */
export const FRAMEWORK_MARKERS: Record<string, string> = {
  "next.config.js": "nextjs",
  "next.config.ts": "nextjs",
  "nuxt.config.ts": "nuxt",
  "angular.json": "angular",
  "svelte.config.js": "svelte",
  "remix.config.js": "remix",
  "astro.config.mjs": "astro",
  "django-admin.py": "django",
  "manage.py": "django",
  "Cargo.toml": "rust",
  "go.mod": "go",
  "tsconfig.json": "typescript",
};

/** Manifest file -> ecosystem map */
export const ECOSYSTEM_MARKERS: Record<string, string> = {
  "package.json": "npm",
  "yarn.lock": "yarn",
  "pnpm-lock.yaml": "pnpm",
  "requirements.txt": "pip",
  "pyproject.toml": "pip",
  "poetry.lock": "poetry",
  "Cargo.toml": "cargo",
  "go.mod": "gomod",
  "Gemfile": "bundler",
};

export function detectFrameworks(inventory: FileInventory): string[] {
  // ...
}

export function detectEcosystems(inventory: FileInventory): string[] {
  // ...
}
```

**Depends on**: Task 1.4.

### Task 1.6: CLI entrypoint and engine stub

**`src/cli.ts`**
- Parse CLI args via commander: `<repo-path-or-url>`, `--ref`, `--env`, `--policy`, `--format`, `--output-dir`, `--include`, `--exclude`, `--enable-module`, `--disable-module`, `--runtime-mode`, `--adoption-mode`
- Construct AuditRequest, call `runAudit(request)`
- Exit codes: 0=PROCEED, 1=ABORT, 2=CAUTION

```typescript
// src/cli.ts
import { Command } from "commander";
import { AuditRequestSchema, type AuditRequest } from "./models/audit-request";
import { runAudit } from "./engine/run-audit";

const program = new Command()
  .name("stop-git-std")
  .description("Git repository safety auditor")
  .argument("<repo>", "Repository path or URL")
  .option("--ref <ref>", "Git ref to audit", "default_branch")
  .option("--env <environment>", "Target environment", "offline_analysis")
  .option("--policy <profile>", "Policy profile", "balanced")
  .option("--format <formats...>", "Output formats", ["json", "markdown"])
  .option("--output-dir <dir>", "Output directory")
  .option("--include <paths...>", "Include path patterns")
  .option("--exclude <paths...>", "Exclude path patterns")
  .option("--enable-module <modules...>", "Force-enable modules")
  .option("--disable-module <modules...>", "Force-disable modules")
  .option("--runtime-mode <mode>", "Runtime validation mode", "off")
  .option("--adoption-mode <mode>", "Adoption context", "third_party");

export async function main(): Promise<number> {
  program.parse();
  const opts = program.opts();
  const [repoTarget] = program.args;

  const request = AuditRequestSchema.parse({
    repo_target: repoTarget,
    ref: opts.ref,
    target_environment: opts.env,
    policy_profile: opts.policy,
    output_formats: opts.format,
    include_paths: opts.include ?? [],
    exclude_paths: opts.exclude,
    enabled_modules: opts.enableModule ?? [],
    disabled_modules: opts.disableModule ?? [],
    runtime_mode: opts.runtimeMode,
    adoption_mode: opts.adoptionMode,
  });

  const result = await runAudit(request);

  // Exit codes: 0=PROCEED, 1=ABORT, 2=CAUTION
  const exitCodeMap = { PROCEED: 0, PROCEED_WITH_CONSTRAINTS: 0, ABORT: 1, CAUTION: 2 } as const;
  return exitCodeMap[result.decision.value];
}
```

**`src/engine/run-audit.ts`** (M1 stub)
- `runAudit(request: AuditRequest): Promise<AuditResult>`
- Implements phases 1-4: context_capture, repository_acquisition, inventory_classification, module_routing
- Stubs phases 5-11

```typescript
// src/engine/run-audit.ts
import type { AuditRequest } from "../models/audit-request";
import type { AuditResult } from "../models/audit-result";
import type { AuditContext } from "../models/audit-context";
import type { RunManifest } from "../models/run-manifest";
import type { RuleCatalog, EngineContract } from "../rules/types";

export async function runAudit(request: AuditRequest): Promise<AuditResult> {
  // Phase 1: context_capture — normalize request into AuditContext
  // Phase 2: repository_acquisition — clone or open local path
  // Phase 3: inventory_classification — enumerate files, classify repo
  // Phase 4: module_routing — determine active modules
  // Phases 5-11: stubs in M1, wired in M2-M4
  // ...
}

/** Phase 1: Normalize AuditRequest into AuditContext */
export function captureContext(request: AuditRequest): AuditContext {
  return {
    repo_target: request.repo_target,
    ref: request.ref,
    target_environment: request.target_environment,
    expected_permissions: request.expected_permissions,
    runtime_validation_enabled: request.runtime_mode !== "off",
    runtime_mode: request.runtime_mode,
    adoption_mode: request.adoption_mode,
    notes: request.notes,
  };
}
```

**`src/engine/router.ts`**
- `routeModules(profile, context, catalog): ActiveModules`
- Start with universal modules, expand by detected categories using engine contract routes
- Apply enabled/disabled overrides, deduplicate

```typescript
// src/engine/router.ts
import type { RepoProfile } from "../models/repo-profile";
import type { AuditContext } from "../models/audit-context";
import type { EngineContract } from "../rules/types";

export interface ActiveModules {
  universal: string[];
  typed: string[];
  all: string[];
}

export function routeModules(
  profile: RepoProfile,
  context: AuditContext,
  contract: EngineContract,
  enabledOverrides: string[],
  disabledOverrides: string[]
): ActiveModules {
  // 1. Start with universal_modules from contract.module_routing
  // 2. For each detected_category, add typed modules from category_routes
  // 3. Merge enabledOverrides
  // 4. Remove disabledOverrides
  // 5. Deduplicate
  // ...
}
```

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

```typescript
// src/plugins/analyzer-backend.ts
import type { LocalWorkspace } from "../models/local-workspace";
import type { RepoProfile } from "../models/repo-profile";
import type { AuditContext } from "../models/audit-context";
import type { Finding } from "../models/finding";
import type { ModuleResult } from "../models/module-result";
import type { RuleDefinition } from "../rules/types";

export interface AnalyzerOutput {
  findings: Finding[];
  moduleResult: ModuleResult;
}

export interface AnalyzerModule {
  name: string;
  analyze(
    workspace: LocalWorkspace,
    profile: RepoProfile,
    context: AuditContext,
    rules: RuleDefinition[]
  ): Promise<AnalyzerOutput>;
}

export interface AnalyzerBackend {
  type: "builtin-ts" | "python-subprocess" | "external";
  canHandle(moduleName: string): boolean;
  execute(
    moduleName: string,
    workspace: LocalWorkspace,
    profile: RepoProfile,
    context: AuditContext,
    rules: RuleDefinition[]
  ): Promise<AnalyzerOutput>;
}
```

**`src/plugins/builtin-ts.ts`** — Registry of all built-in TS analyzers.

```typescript
// src/plugins/builtin-ts.ts
import type { AnalyzerModule } from "./analyzer-backend";

const registry = new Map<string, AnalyzerModule>();

export function registerAnalyzer(analyzer: AnalyzerModule): void {
  registry.set(analyzer.name, analyzer);
}

export function getAnalyzer(name: string): AnalyzerModule | undefined {
  return registry.get(name);
}

export function getAllAnalyzers(): AnalyzerModule[] {
  return Array.from(registry.values());
}
```

**`src/analyzers/base.ts`** — Shared helpers:
- `matchFiles(inventory, patterns): string[]`
- `scanFileContent(path, regex): MatchResult[]`
- `readFileContent(path, maxSize): string | null`
- `emitFinding(rule, evidence, files, lineNumbers?): Finding`

```typescript
// src/analyzers/base.ts
import type { Finding, Evidence } from "../models/finding";
import type { RuleDefinition } from "../rules/types";
import type { FileInventory } from "../inventory/enumerate-files";

export interface MatchResult {
  path: string;
  lineNumber: number;
  line: string;
  match: string;
}

export function matchFiles(
  inventory: FileInventory,
  patterns: string[]
): string[] {
  // Filter inventory.files by glob patterns, return matching paths
  // ...
}

export function scanFileContent(
  filePath: string,
  regex: RegExp
): MatchResult[] {
  // Read file, match regex per line, return results
  // ...
}

export function readFileContent(
  filePath: string,
  maxSize?: number
): string | null {
  // Read up to maxSize bytes (default 5MB), return null if too large or unreadable
  // ...
}

/** Build a Finding from a rule definition, evidence, and file locations */
export function emitFinding(
  rule: RuleDefinition,
  evidence: Evidence,
  files: string[],
  lineNumbers?: number[]
): Finding {
  return {
    id: rule.id,
    title: rule.title,
    category: rule.category,
    subcategory: rule.subcategory,
    severity: rule.default_severity,
    confidence: rule.default_confidence,
    proof_type: rule.proof_type,
    axis_impacts: { ...rule.axis_impacts },
    evidence,
    remediation: rule.remediation,
    files,
    line_numbers: lineNumbers,
    suppressed: false,
    suppression_reason: "",
  };
}
```

### Task 2.2: Governance & Trust (GHA-TRUST-001–005)

**`src/analyzers/universal/governance-trust.ts`**
- path_check: SECURITY.md, CODEOWNERS
- github_api_lookup: archived/abandoned (git metadata fallback)
- tag_signature_verification: signed tags via git
- git_metadata_analysis: contributor shift detection

```typescript
// src/analyzers/universal/governance-trust.ts — C8 detection code

import { emitFinding, scanFileContent, matchFiles, readFileContent } from "../base";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend";
import type { LocalWorkspace } from "../../models/local-workspace";
import type { RepoProfile } from "../../models/repo-profile";
import type { AuditContext } from "../../models/audit-context";
import type { RuleDefinition } from "../../rules/types";
import type { Finding } from "../../models/finding";

export const governanceTrustAnalyzer: AnalyzerModule = {
  name: "governance_trust",

  async analyze(workspace, profile, context, rules): Promise<AnalyzerOutput> {
    const findings: Finding[] = [];
    const startedAt = new Date().toISOString();

    for (const rule of rules) {
      switch (rule.id) {
        // GHA-TRUST-001: Check if SECURITY.md or .github/SECURITY.md exists
        case "GHA-TRUST-001": {
          const securityPaths = ["SECURITY.md", ".github/SECURITY.md"];
          const found = securityPaths.some((p) =>
            require("fs").existsSync(`${workspace.rootPath}/${p}`)
          );
          if (!found) {
            findings.push(
              emitFinding(rule, {
                type: "missing_file",
                records: [{ expected_paths: securityPaths }],
              }, [])
            );
          }
          break;
        }

        // GHA-TRUST-002: Check if CODEOWNERS or .github/CODEOWNERS exists
        case "GHA-TRUST-002": {
          const codeownersPaths = ["CODEOWNERS", ".github/CODEOWNERS"];
          const found = codeownersPaths.some((p) =>
            require("fs").existsSync(`${workspace.rootPath}/${p}`)
          );
          if (!found) {
            findings.push(
              emitFinding(rule, {
                type: "missing_file",
                records: [{ expected_paths: codeownersPaths }],
              }, [])
            );
          }
          break;
        }

        // GHA-TRUST-003: Check git metadata for archived flag or last commit > 18 months ago
        case "GHA-TRUST-003": {
          const lastCommitDate = workspace.gitMetadata.lastCommitDate;
          if (lastCommitDate) {
            const lastCommit = new Date(lastCommitDate);
            const monthsAgo = (Date.now() - lastCommit.getTime()) / (1000 * 60 * 60 * 24 * 30);
            if (monthsAgo > 18) {
              findings.push(
                emitFinding(rule, {
                  type: "stale_repo",
                  records: [{ last_commit: lastCommitDate, months_inactive: Math.round(monthsAgo) }],
                }, [])
              );
            }
          }
          break;
        }

        // GHA-TRUST-004: Check `git tag -v` output or count signed tags
        case "GHA-TRUST-004": {
          const signedTags = workspace.gitMetadata.signedTags;
          const totalTags = workspace.gitMetadata.tags;
          if (totalTags.length > 0 && signedTags.length === 0) {
            findings.push(
              emitFinding(rule, {
                type: "unsigned_tags",
                records: [{ total_tags: totalTags.length, signed_tags: 0 }],
              }, [])
            );
          }
          break;
        }

        // GHA-TRUST-005: Analyze git log for new contributor dominating sensitive paths in last 30 days
        case "GHA-TRUST-005": {
          // Parse git log for last 30 days, identify contributors to sensitive paths
          // (e.g., .github/workflows/*, package.json, Dockerfile)
          // Flag if a single new contributor dominates commits to these paths
          const proc = Bun.spawnSync(["git", "log", "--since=30.days",
            "--format=%ae|%H", "--", ".github/workflows/", "package.json",
            "Dockerfile", "*.lock"], { cwd: workspace.rootPath });
          const output = proc.stdout.toString();
          const lines = output.trim().split("\n").filter(Boolean);
          const contributorCommits = new Map<string, number>();
          for (const line of lines) {
            const [email] = line.split("|");
            contributorCommits.set(email, (contributorCommits.get(email) ?? 0) + 1);
          }
          // Flag if any contributor with < 10% historical presence has > 60% recent sensitive commits
          if (lines.length > 3) {
            const totalRecent = lines.length;
            for (const [email, count] of contributorCommits) {
              if (count / totalRecent > 0.6) {
                findings.push(
                  emitFinding(rule, {
                    type: "contributor_shift",
                    records: [{ contributor: email, sensitive_commits_30d: count, total_30d: totalRecent }],
                  }, [])
                );
              }
            }
          }
          break;
        }
      }
    }

    return {
      findings,
      moduleResult: {
        module_name: "governance_trust",
        status: findings.length >= 0 ? "success" : "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
      },
    };
  },
};
```

### Task 2.3: Supply Chain (GHA-SUPPLY-001–005)

**`src/analyzers/universal/supply-chain.ts`**
- manifest_parse: lockfile presence, floating versions, git/URL deps
- osv_lookup: **stub** (returns empty + warning)
- file_signature_scan: binary detection

```typescript
// src/analyzers/universal/supply-chain.ts — C8 detection code

// GHA-SUPPLY-001: Manifest exists but lockfile missing
// Check per-ecosystem mappings:
const LOCKFILE_MAP: Record<string, string[]> = {
  "package.json": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb"],
  "Gemfile": ["Gemfile.lock"],
  "requirements.txt": ["requirements.txt"], // self-locking
  "pyproject.toml": ["poetry.lock", "pdm.lock"],
  "Cargo.toml": ["Cargo.lock"],
  "go.mod": ["go.sum"],
};
// For each manifest found in inventory, check if any corresponding lockfile exists

// GHA-SUPPLY-002: Parse package.json deps for floating version specs
// Regex: /[\^~*]|latest/ against each version value in dependencies/devDependencies
const FLOATING_VERSION_RE = /^[\^~*]|^latest$/;
// Flag each dep with a floating spec

// GHA-SUPPLY-003: Parse deps for git+ or URL sources
// Match: /^(git\+|https?:\/\/)/ in dependency version fields
const URL_DEP_RE = /^(git\+|https?:\/\/)/;

// GHA-SUPPLY-004: OSV lookup stub
// Call queryOsvStub() — returns empty array + emits warning
// "OSV lookup not yet available — returning empty results"

// GHA-SUPPLY-005: Scan for binary files by extension
const BINARY_EXTENSIONS = [".exe", ".dll", ".so", ".dylib", ".bin"];
// Filter inventory.files by these extensions, emit finding for each match
```

**`src/adapters/osv.ts`** — Stub interface.

### Task 2.4: Secrets (GHA-SECRETS-001–003)

**`src/analyzers/universal/secrets.ts`**
- regex_scan: PEM private key blocks
- path_risk_scan: `.env` files with secret-like entries
- entropy_scan: Shannon entropy near auth keywords
- Must redact evidence snippets

```typescript
// src/analyzers/universal/secrets.ts — C8 detection code

// GHA-SECRETS-001: Regex for private key blocks across all files
const PRIVATE_KEY_RE = /-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----/;
// scanFileContent(filePath, PRIVATE_KEY_RE) across all inventory files
// Emit finding with redacted evidence (show file + line number, not key content)

// GHA-SECRETS-002: Check for .env, .env.* files containing secret-like lines
// Match files: /^\.env($|\.)/ in inventory
// For each .env file, scan lines matching:
const ENV_SECRET_RE = /^[A-Z_]*(KEY|SECRET|TOKEN|PASSWORD)\s*=/i;
// Emit finding per file with count of matching lines

// GHA-SECRETS-003: Shannon entropy scan near auth keywords
// For lines containing: token, secret, api_key, password (case-insensitive)
// Compute Shannon entropy of the value portion (after = or : delimiter)
function shannonEntropy(s: string): number {
  const freq = new Map<string, number>();
  for (const c of s) freq.set(c, (freq.get(c) ?? 0) + 1);
  let entropy = 0;
  for (const count of freq.values()) {
    const p = count / s.length;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}
// Flag if entropy >= 4.0 — indicates likely hardcoded secret
const AUTH_KEYWORD_RE = /(?:token|secret|api_key|password)\s*[=:]\s*["']?(\S+)/i;
```

### Task 2.5: Dangerous Execution (GHA-EXEC-001–005)

**`src/analyzers/universal/dangerous-execution.ts`**
- regex_scan: curl|bash patterns
- manifest_parse: install lifecycle hooks
- regex fallback for AST rules (subprocess shell=True, unsafe deser, remote code load) with confidence downgrade

```typescript
// src/analyzers/universal/dangerous-execution.ts — C8 detection code

// GHA-EXEC-001: curl|bash piping in scripts
// File patterns: .sh, .bash, Dockerfile, package.json
const CURL_PIPE_RE = /curl\s+[^\n|]+\|\s*(bash|sh)/;
// scanFileContent for each matching file

// GHA-EXEC-002: Parse package.json for lifecycle hooks
// Check scripts object for: preinstall, install, postinstall
// Emit finding if any of these hooks exist (they run on npm install)
// Use: JSON.parse(readFileContent("package.json"))?.scripts
const LIFECYCLE_HOOKS = ["preinstall", "install", "postinstall"];

// GHA-EXEC-003: Python subprocess with shell=True
// File patterns: *.py
const SUBPROCESS_SHELL_RE = /subprocess\.(run|call|Popen)\(.*shell\s*=\s*True/;

// GHA-EXEC-004: Unsafe deserialization patterns
// File patterns: *.py, *.js
const UNSAFE_DESER_RE = /pickle\.loads|yaml\.load\(|serialize.*eval/;

// GHA-EXEC-005: Remote code execution heuristic
// Detect fetch/download followed by eval/exec/require in same file
// Two-pass scan:
//   Pass 1: check for fetch(), download(), http.get(), axios.get(), urllib
//   Pass 2: check for eval(), exec(), require(), import(), Function()
// If both present in same file, emit finding with confidence "medium"
const FETCH_RE = /\b(fetch|download|http\.get|axios\.get|urllib|requests\.get)\b/;
const EXEC_RE = /\b(eval|exec|require|import|Function)\s*\(/;
```

**`src/parsers/package-json.ts`** — Parse scripts, deps, detect hooks + git/URL deps.

### Task 2.6: CI/CD (GHA-CI-001–005)

**`src/analyzers/universal/ci-cd.ts`**
- yaml_parse: pull_request_target triggers, broad permissions, unpinned actions
- workflow_semantics: shell injection via `${{ github.event.* }}` in run steps
- self-hosted runner + untrusted trigger detection

```typescript
// src/analyzers/universal/ci-cd.ts — C8 detection code

// GHA-CI-001: Parse workflow YAML for pull_request_target trigger
// For each .github/workflows/*.yml file:
//   Parse YAML, check `on:` or `true:` keys for `pull_request_target`
// Emit if found — this trigger runs with base repo permissions on forked PR code

// GHA-CI-002: Broad permissions in workflow
// Check for `permissions: write-all` at workflow or job level
// Also flag individual broad scopes like `contents: write` + `actions: write`
const BROAD_PERMISSIONS_RE = /permissions:\s*write-all/;

// GHA-CI-003: Unpinned action references
// Parse `uses:` values in steps, flag any not pinned to SHA (40-char hex)
const SHA_PIN_RE = /^[^@]+@[0-9a-f]{40}$/;
// For each `uses:` ref that doesn't match SHA_PIN_RE, emit finding
// Skip actions like `actions/checkout@v4` — these should be `actions/checkout@<sha>`

// GHA-CI-004: Shell injection via expression interpolation in run steps
// Regex for dangerous patterns in `run:` blocks:
const SHELL_INJECTION_RE = /\$\{\{\s*github\.event\.(pull_request\.title|issue\.title|head_ref)/;
// These expressions can be attacker-controlled and inject shell commands

// GHA-CI-005: Self-hosted runner with untrusted triggers
// Check if workflow has `runs-on: self-hosted` AND trigger is pull_request_target,
// pull_request (from fork), or issue_comment
// Combination is dangerous — attacker code runs on org infrastructure
```

**`src/parsers/workflow-yaml.ts`** — Parse GH Actions YAML: triggers, jobs, steps, permissions, uses, run.

### Task 2.7: Infrastructure (GHA-INFRA-001–003)

**`src/analyzers/universal/infrastructure.ts`**
- dockerfile_parse: USER directive, FROM :latest
- yaml_parse: K8s RBAC wildcard detection

```typescript
// src/analyzers/universal/infrastructure.ts — C8 detection code

// GHA-INFRA-001: Dockerfile missing USER directive
// Parse Dockerfile line by line, check if any USER directive exists
// If no USER directive found, container runs as root by default
// Scan: Dockerfile, *.dockerfile, Dockerfile.*
const USER_DIRECTIVE_RE = /^USER\s+/m;

// GHA-INFRA-002: FROM with :latest tag
// Parse FROM lines in Dockerfiles
const FROM_LATEST_RE = /^FROM\s+\S+:latest/m;
// Also flag FROM lines with no tag at all (implicit :latest):
const FROM_NO_TAG_RE = /^FROM\s+([^\s:@]+)\s*$/m;

// GHA-INFRA-003: Kubernetes RBAC wildcard permissions
// Parse K8s YAML files (kind: Role or ClusterRole)
// Check rules[].verbs and rules[].resources for "*"
// File patterns: *.yaml, *.yml in k8s/, kubernetes/, manifests/, deploy/ dirs
// Parse YAML, check:
//   kind === "Role" || kind === "ClusterRole"
//   rules[].verbs includes "*" OR rules[].resources includes "*"
```

**`src/parsers/dockerfile.ts`** — Line-based parser: FROM, USER, RUN.

**`src/parsers/k8s-yaml.ts`** — Role/ClusterRole broad permission detection.

### Task 2.8: Wire universal analyzers into engine

**`src/engine/run-audit.ts`** (update) — Implement phase 5 (universal_analysis):
- Iterate active universal modules, call each analyzer
- Respect timeout_seconds_per_phase (300s)
- continue_on_module_error behavior
- Collect findings + module results

```typescript
// Phase 5 implementation sketch inside run-audit.ts
import type { Finding } from "../models/finding";
import type { ModuleResult } from "../models/module-result";
import { getAnalyzer } from "../plugins/builtin-ts";

async function runAnalysisPhase(
  moduleNames: string[],
  workspace: LocalWorkspace,
  profile: RepoProfile,
  context: AuditContext,
  rulesByModule: Map<string, RuleDefinition[]>,
  timeoutMs: number,
  continueOnError: boolean
): Promise<{ findings: Finding[]; moduleResults: ModuleResult[] }> {
  const findings: Finding[] = [];
  const moduleResults: ModuleResult[] = [];

  for (const moduleName of moduleNames) {
    const analyzer = getAnalyzer(moduleName);
    if (!analyzer) {
      moduleResults.push({
        module_name: moduleName,
        status: "skipped",
        started_at: new Date().toISOString(),
        findings_emitted: 0,
        warnings: [`No analyzer registered for module: ${moduleName}`],
      });
      continue;
    }

    try {
      const rules = rulesByModule.get(moduleName) ?? [];
      const output = await analyzer.analyze(workspace, profile, context, rules);
      findings.push(...output.findings);
      moduleResults.push(output.moduleResult);
    } catch (err) {
      if (!continueOnError) throw err;
      moduleResults.push({
        module_name: moduleName,
        status: "failed",
        started_at: new Date().toISOString(),
        findings_emitted: 0,
        errors: [String(err)],
      });
    }
  }

  return { findings, moduleResults };
}
```

### Task 2.9: M2 tests

One test file per analyzer + per parser. Create temp directories with specific file contents, run analyzer, assert expected findings with correct severity/confidence/axis_impacts.

---

## Milestone 3 — Typed Analyzers

**Goal**: All 7 category-specific modules activated by repo classification.

### Task 3.1: Web (GHA-WEB-001–002)
**`src/analyzers/typed/web.ts`** — Debug mode config detection, unescaped template output (regex heuristic).
- **GHA-WEB-001**: Regex-feasible (MVP). Scan for `DEBUG\s*=\s*True`, `debug:\s*true`, `NODE_ENV.*development` in config files. Confidence: medium.
- **GHA-WEB-002**: Stub with confidence "low". Template injection requires AST/framework awareness.

### Task 3.2: API (GHA-API-001–003)
**`src/analyzers/typed/api.ts`** — Auth guard detection on sensitive routes, CORS config, request-to-model binding.
- **GHA-API-001**: Stub with confidence "low". Auth guard detection requires AST control flow analysis.
- **GHA-API-002**: Regex-feasible (MVP). Scan for `Access-Control-Allow-Origin: *` or `cors({ origin: "*" })` patterns.
- **GHA-API-003**: Stub with confidence "low". Request-to-model binding analysis requires framework-specific AST.

### Task 3.3: AI/LLM (GHA-AI-001–003)
**`src/analyzers/typed/ai-llm.ts`** — Model output -> exec/tool dispatch, secrets in prompts, missing rate/budget controls.
- **GHA-AI-001**: Stub with confidence "low". Detecting model output flowing to exec/tool dispatch requires dataflow analysis.
- **GHA-AI-002**: Stub with confidence "low". Secrets-in-prompts detection requires understanding prompt construction.
- **GHA-AI-003**: Stub with confidence "low". Rate/budget control detection is framework-specific.

### Task 3.4: Agent Framework (GHA-AGENT-001–002)
**`src/analyzers/typed/agent-framework.ts`** — Shell+write+network without approval gate, shared state without isolation.
- **GHA-AGENT-001**: Stub with confidence "low". Requires understanding agent tool registration and approval gate patterns.
- **GHA-AGENT-002**: Stub with confidence "low". Shared state isolation detection requires framework-specific analysis.

### Task 3.5: Skills/Plugins (GHA-PLUGIN-001–002)
**`src/analyzers/typed/skills-plugins.ts`** — Broad manifest permissions, instruction identity/guardrail override patterns.
- **GHA-PLUGIN-001**: Regex-feasible (MVP). Scan manifest files (plugin.json, manifest.json) for overly broad permission declarations.
- **GHA-PLUGIN-002**: Regex-feasible (MVP). Scan for prompt injection/identity override patterns like `ignore previous instructions`, `you are now`, `system:` in string literals.

### Task 3.6: MCP Server (GHA-MCP-001–003)
**`src/analyzers/typed/mcp-server.ts`** — Unrestricted shell tool, SSRF-capable fetch, credential forwarding.
- **GHA-MCP-001**: Stub with confidence "low". Detecting unrestricted shell execution tool requires understanding MCP tool registration patterns.
- **GHA-MCP-002**: Stub with confidence "low". SSRF-capable fetch detection needs dataflow from user input to fetch URL.
- **GHA-MCP-003**: Stub with confidence "low". Credential forwarding detection requires understanding token/key propagation.

### Task 3.7: Library/Package (GHA-PKG-001)
**`src/analyzers/typed/library-package.ts`** — Import/init-time network or process side effects.
- **GHA-PKG-001**: Regex-feasible (MVP). Scan top-level module files for `fetch(`, `http.get(`, `net.connect(`, `child_process`, `subprocess` at module scope (not inside functions).

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

```typescript
// src/engine/normalize-findings.ts
import type { Finding } from "../models/finding";

// C3: SuppressionEntry schema with hard-stop override fields
export const SuppressionEntrySchema = z.object({
  rule_id: z.string(),
  path_globs: z.array(z.string()).optional(),
  expires_at: z.string().optional(),
  justification: z.string(),
  approved_by: z.string().optional(),
  // C3: Required for suppressing hard-stop rules
  override_reason: z.string().optional(),
  reviewer_identity: z.string().optional(),
  reviewed_commit_sha: z.string().optional(),
});

export type SuppressionEntry = z.infer<typeof SuppressionEntrySchema>;

export const SuppressionsFileSchema = z.object({
  suppressions: z.array(SuppressionEntrySchema),
});

export function normalizeFindings(
  universalFindings: Finding[],
  typedFindings: Finding[],
  runtimeFindings?: Finding[]
): Finding[] {
  const merged = [
    ...universalFindings,
    ...typedFindings,
    ...(runtimeFindings ?? []),
  ];
  return deduplicateFindings(merged);
}

/** Deduplicate by (id, files, evidence.type), combine_evidence_records */
export function deduplicateFindings(findings: Finding[]): Finding[] {
  const keyMap = new Map<string, Finding>();
  for (const f of findings) {
    const key = `${f.id}|${(f.files ?? []).sort().join(",")}|${f.evidence.type}`;
    const existing = keyMap.get(key);
    if (existing) {
      // Merge evidence records
      existing.evidence.records.push(...f.evidence.records);
    } else {
      keyMap.set(key, { ...f });
    }
  }
  return Array.from(keyMap.values());
}

/** Apply suppressions from .stop-git-std.suppressions.yaml
 *  C3: Hard-stop rules cannot be suppressed unless the suppression includes
 *  override_reason, reviewer_identity, AND reviewed_commit_sha.
 */
export function applySuppressions(
  findings: Finding[],
  suppressions: SuppressionEntry[],
  hardStopPatterns: string[]
): Finding[] {
  for (const finding of findings) {
    const matchingSuppression = suppressions.find((s) => {
      if (s.rule_id !== finding.id) return false;
      // Check path glob match if specified
      if (s.path_globs && s.path_globs.length > 0 && finding.files) {
        const matchesPath = finding.files.some((file) =>
          s.path_globs!.some((glob) => minimatch(file, glob))
        );
        if (!matchesPath) return false;
      }
      return true;
    });

    if (!matchingSuppression) continue;

    // C3: Reject suppression of hard-stop rules unless all override fields present
    if (hardStopPatterns.includes(finding.id)) {
      const hasValidOverride =
        matchingSuppression.override_reason &&
        matchingSuppression.reviewer_identity &&
        matchingSuppression.reviewed_commit_sha;
      if (!hasValidOverride) {
        console.warn(
          `Suppression for hard-stop rule ${finding.id} rejected: ` +
          `requires override_reason, reviewer_identity, and reviewed_commit_sha`
        );
        continue;
      }
    }

    finding.suppressed = true;
    finding.suppression_reason = matchingSuppression.justification;
  }
  return findings;
}

// C4: Suppression file loader
import { parse as parseYaml } from "yaml";

/** Load suppressions from .stop-git-std.suppressions.yaml in the workspace root.
 *  - File not found: return empty array
 *  - Parse errors: warn and return empty array
 *  - Expired suppressions: filtered out
 */
export function loadSuppressions(workspacePath: string): SuppressionEntry[] {
  const suppressionPath = `${workspacePath}/.stop-git-std.suppressions.yaml`;
  const fs = require("fs");

  if (!fs.existsSync(suppressionPath)) {
    return [];
  }

  try {
    const text = fs.readFileSync(suppressionPath, "utf-8");
    const parsed = parseYaml(text);
    const validated = SuppressionsFileSchema.parse(parsed);

    // Filter out expired suppressions
    const now = new Date();
    return validated.suppressions.filter((s) => {
      if (!s.expires_at) return true;
      const expiresAt = new Date(s.expires_at);
      return expiresAt > now;
    });
  } catch (err) {
    console.warn(
      `Failed to parse suppressions file at ${suppressionPath}: ${err}`
    );
    return [];
  }
}
```

### Task 4.2: Scoring engine

**`src/engine/scoring.ts`**
- `computeScores(findings, profile, context, moduleResults, contract): Scores`
- Formula: `weighted_axis_value = axis_impact * severity_weight * confidence_multiplier / 10`
- Environment multiplier on abuse_potential only
- Subtract trust credits from repo_profile (signed_tags: 8, security_md: 3, codeowners: 2, pinned_actions_ratio_high: 4)
- Clamp 0-100
- Confidence model (MVP "mvp-1"): high if failed_modules_ratio <= 0.10 AND (critical_static_findings >= 1 OR all universal modules completed); medium if failed_modules_ratio <= 0.30; low fallback

```typescript
// src/engine/scoring.ts
import type { Finding } from "../models/finding";
import type { Scores } from "../models/scores";
import type { RepoProfile } from "../models/repo-profile";
import type { AuditContext } from "../models/audit-context";
import type { ModuleResult } from "../models/module-result";
import type { EngineContract } from "../rules/types";
import type { Severity, Confidence, Environment } from "../models/enums";

// --- Lookup tables (as const for type safety) ---

export const SEVERITY_WEIGHTS = {
  info: 1,
  low: 3,
  medium: 8,
  high: 15,
  critical: 25,
} as const satisfies Record<Severity, number>;

export const CONFIDENCE_MULTIPLIERS = {
  low: 0.60,
  medium: 0.85,
  high: 1.00,
} as const satisfies Record<Confidence, number>;

export const ENVIRONMENT_ABUSE_MULTIPLIERS = {
  developer_laptop: 1.25,
  ci_runner: 1.30,
  container_isolated: 0.80,
  offline_analysis: 0.20,
  production_service: 1.40,
} as const satisfies Record<Environment, number>;

export const TRUST_CREDITS = {
  signed_tags_present: 8,
  security_md_present: 3,
  codeowners_present: 2,
  pinned_actions_ratio_high: 4,
} as const;

// --- Core scoring function ---

export function computeScores(
  findings: Finding[],
  profile: RepoProfile,
  context: AuditContext,
  moduleResults: ModuleResult[],
  contract: EngineContract
): Scores {
  // 1. Initialize axes to zero
  let trustworthiness = 0;
  let exploitability = 0;
  let abuse_potential = 0;

  // 2. For each unsuppressed finding, compute weighted contribution per axis
  for (const f of findings) {
    if (f.suppressed) continue;

    const severityW = SEVERITY_WEIGHTS[f.severity];
    const confidenceM = CONFIDENCE_MULTIPLIERS[f.confidence];

    // weighted_axis_value = axis_impact * severity_weight * confidence_multiplier / 10
    trustworthiness += (f.axis_impacts.trustworthiness * severityW * confidenceM) / 10;
    exploitability += (f.axis_impacts.exploitability * severityW * confidenceM) / 10;
    abuse_potential += (f.axis_impacts.abuse_potential * severityW * confidenceM) / 10;
  }

  // 3. Apply environment multiplier to abuse_potential only
  const envMultiplier = ENVIRONMENT_ABUSE_MULTIPLIERS[context.target_environment];
  abuse_potential *= envMultiplier;

  // 4. Subtract trust credits (trustworthiness axis ONLY — see C1/C10)
  const credits = deriveTrustCredits(profile, moduleResults);
  trustworthiness -= credits;

  // 5. Clamp 0-100
  const clamp = (v: number) => Math.min(100, Math.max(0, Math.round(v)));

  // 6. Derive confidence
  const confidence = deriveConfidence(moduleResults, findings, context);

  return {
    trustworthiness: clamp(trustworthiness),
    exploitability: clamp(exploitability),
    abuse_potential: clamp(abuse_potential),
    confidence,
    environment_multiplier_applied: envMultiplier,
  };
}

/**
 * Derive trust credits from repo_profile fields directly.
 * Only award credits when the corresponding module completed with status "success" or "partial".
 * Trust credits apply to trustworthiness axis ONLY — they must NOT reduce exploitability or abuse_potential.
 */
function deriveTrustCredits(
  profile: RepoProfile,
  moduleResults: ModuleResult[]
): number {
  let credits = 0;

  // Helper: check if a module completed successfully
  const moduleCompleted = (name: string): boolean =>
    moduleResults.some(
      (m) => m.module_name === name && (m.status === "success" || m.status === "partial")
    );

  // SECURITY.md presence — check repo_profile.artifacts.manifests or high_risk_files
  if (moduleCompleted("governance_trust")) {
    const allArtifacts = [
      ...profile.artifacts.manifests,
      ...profile.high_risk_files,
    ];
    if (
      allArtifacts.some(
        (f) => f.endsWith("SECURITY.md") || f.endsWith(".github/SECURITY.md")
      )
    ) {
      credits += TRUST_CREDITS.security_md_present;
    }
  }

  // CODEOWNERS presence
  if (moduleCompleted("governance_trust")) {
    const allArtifacts = [
      ...profile.artifacts.manifests,
      ...profile.high_risk_files,
    ];
    if (
      allArtifacts.some(
        (f) => f.endsWith("CODEOWNERS") || f.endsWith(".github/CODEOWNERS")
      )
    ) {
      credits += TRUST_CREDITS.codeowners_present;
    }
  }

  // Signed tags — derived from repo_profile (populated during inventory phase)
  // repo_profile.signed_tags_count is set by classify-repo.ts from git tag -v output
  if (moduleCompleted("governance_trust")) {
    if (profile.signed_tags_count > 0) {
      credits += TRUST_CREDITS.signed_tags_present;
    }
  }

  // Pinned actions ratio — derived from repo_profile (populated during inventory phase)
  // repo_profile.pinned_actions_ratio is set by classify-repo.ts from workflow YAML parsing
  // This is a repo_profile signal, NOT derived from finding absence
  if (moduleCompleted("ci_cd")) {
    const workflows = profile.artifacts?.workflows ?? [];
    if (workflows.length > 0 && profile.pinned_actions_ratio >= 0.9) {
      credits += TRUST_CREDITS.pinned_actions_ratio_high;
    }
  }

  return credits;
}

// MVP confidence model — AST requirement added when parser support ships
function deriveConfidence(
  moduleResults: ModuleResult[],
  findings: Finding[],
  _context: AuditContext
): "high" | "medium" | "low" {
  const totalModules = moduleResults.length;
  const failedModules = moduleResults.filter((m) => m.status === "failed").length;
  const failedRatio = totalModules > 0 ? failedModules / totalModules : 1;
  const hasCriticalStatic = findings.some(
    (f) => f.severity === "critical" && f.proof_type === "static"
  );

  // C6: MVP confidence model (version "mvp-1")
  // high: failed_modules_ratio <= 0.10 AND (critical_static_findings >= 1
  //        OR all universal modules completed successfully)
  const universalModuleNames = [
    "governance_trust", "supply_chain", "secrets",
    "dangerous_execution", "ci_cd", "infrastructure",
  ];
  const allUniversalSuccess = universalModuleNames.every((name) =>
    moduleResults.some(
      (m) => m.module_name === name && (m.status === "success" || m.status === "partial")
    )
  );

  if (failedRatio <= 0.10 && (hasCriticalStatic || allUniversalSuccess)) {
    return "high";
  }
  if (failedRatio <= 0.30) {
    return "medium";
  }
  return "low";
}
```

### Task 4.3: Policy engine

**`src/engine/policy.ts`**
- `evaluatePolicy(findings, scores, context, contract): Decision`
- Precedence: hard_stop -> ABORT threshold -> CAUTION threshold -> PROCEED_WITH_CONSTRAINTS threshold -> PROCEED
- Hard-stop rules from `policy_baselines.hard_stop_patterns`
- Three profiles: strict, balanced, advisory
- Generate constraints + reasons

```typescript
// src/engine/policy.ts
import type { Finding } from "../models/finding";
import type { Scores } from "../models/scores";
import type { Decision } from "../models/decision";
import type { AuditContext } from "../models/audit-context";
import type { PolicyProfile } from "../models/enums";
import type { EngineContract, PolicyProfileConfig, RuleCatalog } from "../rules/types";

/** Hard-stop rule IDs from policy_baselines.hard_stop_patterns */
export const HARD_STOP_RULE_IDS = [
  "GHA-SECRETS-001",
  "GHA-EXEC-001",
  "GHA-EXEC-005",
  "GHA-CI-004",
  "GHA-AI-001",
  "GHA-AGENT-001",
  "GHA-MCP-001",
  "GHA-MCP-003",
  "GHA-RUNTIME-001",
  "GHA-RUNTIME-003",
] as const;

export function evaluatePolicy(
  findings: Finding[],
  scores: Scores,
  context: AuditContext,
  policyProfile: PolicyProfile,
  contract: EngineContract,
  catalog: RuleCatalog
): Decision {
  const profileConfig: PolicyProfileConfig =
    contract.policy_profiles[policyProfile];

  const reasons: string[] = [];
  const constraints: string[] = [];
  const triggeredRules: string[] = [];

  // 1. Check hard-stop rules
  const hardStopIds = catalog.policy_baselines.hard_stop_patterns;
  const activeFindings = findings.filter((f) => !f.suppressed);
  const hardStopFindings = activeFindings.filter((f) =>
    hardStopIds.includes(f.id)
  );

  if (hardStopFindings.length > 0) {
    for (const f of hardStopFindings) {
      triggeredRules.push(f.id);
      reasons.push(`Triggered by rule ${f.id}: ${f.title}`);
    }
    const hardStopValue =
      profileConfig.hard_stop_behavior === "abort" ? "ABORT" : "CAUTION";
    return {
      value: hardStopValue as any,
      reasons,
      constraints,
      hard_stop_triggered: true,
      triggered_by_rules: triggeredRules,
      manual_review_required: true,
    };
  }

  // 2. Check ABORT thresholds
  const abortT = profileConfig.thresholds.abort;
  if (!abortT.disabled) {
    const criticalCount = activeFindings.filter(
      (f) => f.severity === "critical"
    ).length;
    if (
      (abortT.abuse_potential_gte && scores.abuse_potential >= abortT.abuse_potential_gte) ||
      (abortT.or_critical_findings_gte && criticalCount >= abortT.or_critical_findings_gte)
    ) {
      reasons.push(
        `Abuse potential score ${scores.abuse_potential} or critical finding count ${criticalCount} met abort threshold`
      );
      return {
        value: "ABORT",
        reasons,
        constraints,
        hard_stop_triggered: false,
        triggered_by_rules: triggeredRules,
        manual_review_required: true,
      };
    }
  }

  // 3. Check CAUTION thresholds
  const cautionT = profileConfig.thresholds.caution;
  const highCount = activeFindings.filter((f) => f.severity === "high").length;
  if (
    (cautionT.exploitability_gte && scores.exploitability >= cautionT.exploitability_gte) ||
    (cautionT.or_high_findings_gte && highCount >= cautionT.or_high_findings_gte)
  ) {
    reasons.push(
      `Exploitability ${scores.exploitability} or high finding count ${highCount} met caution threshold`
    );
    return {
      value: "CAUTION",
      reasons,
      constraints: generateConstraints(activeFindings, scores),
      hard_stop_triggered: false,
      triggered_by_rules: triggeredRules,
      manual_review_required: false,
    };
  }

  // 4. Check PROCEED_WITH_CONSTRAINTS thresholds
  const pwcT = profileConfig.thresholds.proceed_with_constraints;
  const hasRuntimeFindings = activeFindings.some(
    (f) => f.proof_type === "runtime"
  );
  if (
    (pwcT.abuse_potential_gte && scores.abuse_potential >= pwcT.abuse_potential_gte) ||
    (pwcT.or_any_runtime_findings && hasRuntimeFindings)
  ) {
    return {
      value: "PROCEED_WITH_CONSTRAINTS",
      reasons: ["Threshold met for constrained adoption"],
      constraints: generateConstraints(activeFindings, scores),
      hard_stop_triggered: false,
      triggered_by_rules: triggeredRules,
      manual_review_required: false,
    };
  }

  // 5. Default PROCEED
  return {
    value: "PROCEED",
    reasons: ["All thresholds passed"],
    constraints: [],
    hard_stop_triggered: false,
    triggered_by_rules: [],
    manual_review_required: false,
  };
}

function generateConstraints(findings: Finding[], scores: Scores): string[] {
  const constraints: string[] = [];
  if (scores.abuse_potential >= 20) {
    constraints.push("run_in_disposable_container");
    constraints.push("restrict_network_egress");
    constraints.push("use_scoped_throwaway_tokens");
  }
  if (findings.some((f) => f.category === "supply_chain")) {
    constraints.push("pin_to_reviewed_commit_sha");
    constraints.push("vendor_or_pin_dependencies");
  }
  if (findings.some((f) => f.category === "ci_cd")) {
    constraints.push("disable_self_hosted_runner_paths");
    constraints.push("minimize_github_token_permissions");
  }
  if (findings.some((f) => f.proof_type === "runtime")) {
    constraints.push("block_adoption_until_manual_review");
  }
  return constraints;
}
```

### Task 4.4: Terminal reporter

**`src/reporting/terminal.ts`** — Color-coded decision, executive summary, top findings, score breakdown, module coverage, constraints.

```typescript
// src/reporting/terminal.ts
import type { AuditResult } from "../models/audit-result";

export function renderTerminalReport(result: AuditResult): string {
  // Render color-coded decision, executive summary, top findings,
  // score breakdown, module coverage, constraints
  // ...
}
```

### Task 4.5: JSON reporter

**`src/reporting/json.ts`** — Full structured output matching engine contract artifact schemas.

```typescript
// src/reporting/json.ts
import type { AuditResult } from "../models/audit-result";

export function renderJsonReport(result: AuditResult): string {
  return JSON.stringify(result, null, 2);
}
```

### Task 4.6: Markdown reporter

**`src/reporting/markdown.ts`** — Structured markdown for PRs and review artifacts.

```typescript
// src/reporting/markdown.ts
import type { AuditResult } from "../models/audit-result";

export function renderMarkdownReport(result: AuditResult): string {
  // Generate structured markdown with decision, scores, findings table, constraints
  // ...
}
```

### Task 4.6b: SARIF reporter

**`src/reporting/sarif.ts`** — SARIF 2.1.0 export per engine contract `sarif_mapping` (info/low -> note, medium -> warning, high/critical -> error).

```typescript
// src/reporting/sarif.ts
import type { AuditResult } from "../models/audit-result";

const SEVERITY_TO_SARIF_LEVEL: Record<string, string> = {
  info: "note",
  low: "note",
  medium: "warning",
  high: "error",
  critical: "error",
};

export function renderSarifReport(result: AuditResult): string {
  const sarifLog = {
    $schema: "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
    version: "2.1.0",
    runs: [
      {
        tool: {
          driver: {
            name: "stop-git-std",
            version: result.manifest.engine_version,
            rules: result.findings.map((f) => ({
              id: f.id,
              shortDescription: { text: f.title },
            })),
          },
        },
        results: result.findings.map((f) => ({
          ruleId: f.id,
          level: SEVERITY_TO_SARIF_LEVEL[f.severity] ?? "note",
          message: { text: f.title },
          locations: (f.files ?? []).map((file) => ({
            physicalLocation: { artifactLocation: { uri: file } },
          })),
        })),
      },
    ],
  };
  return JSON.stringify(sarifLog, null, 2);
}
```

### Task 4.7: Finalize engine pipeline

**`src/engine/run-audit.ts`** (finalize) — Wire phases 7-11:
- `runtime_validation`: no-op unless explicitly enabled
- `finding_normalization`: call normalizeFindings, then load suppressions via `loadSuppressions(workspace.rootPath)` (C4) and apply via `applySuppressions(findings, suppressions, catalog.policy_baselines.hard_stop_patterns)` (C3)
- `scoring`: call computeScores
- `policy_decision`: call evaluatePolicy
- `reporting`: call reporters per output_formats (include `coverage` in all formats — C7)
- Build RunManifest with timing and status

**`src/models/audit-result.ts`** — Type containing all artifacts.

```typescript
// src/models/audit-result.ts
import { z } from "zod";
import type { RunManifest } from "./run-manifest";
import type { AuditContext } from "./audit-context";
import type { RepoProfile } from "./repo-profile";
import type { Finding } from "./finding";
import type { Scores } from "./scores";
import type { Decision } from "./decision";
import type { ModuleResult } from "./module-result";

// C7: Coverage report artifact
export const CoverageReportSchema = z.object({
  files_considered: z.number().int(),
  files_scanned: z.number().int(),
  files_skipped: z.number().int(),
  unsupported_languages: z.array(z.string()),
  failed_modules: z.array(z.string()),
  partial_modules: z.array(z.string()),
  successful_modules: z.array(z.string()),
  runtime_executed: z.boolean(),
});

export type CoverageReport = z.infer<typeof CoverageReportSchema>;

export interface AuditResult {
  manifest: RunManifest;
  context: AuditContext;
  profile: RepoProfile;
  findings: Finding[];
  scores: Scores;
  decision: Decision;
  module_results: ModuleResult[];
  coverage: CoverageReport; // C7
  reports: Record<string, string>;
}
```

**C7: `buildCoverageReport` function** — added to engine:

```typescript
// src/engine/coverage.ts
import type { CoverageReport } from "../models/audit-result";
import type { FileInventory } from "../inventory/enumerate-files";
import type { ModuleResult } from "../models/module-result";

/** Build a coverage report from inventory and module results */
export function buildCoverageReport(
  inventory: FileInventory,
  moduleResults: ModuleResult[],
  runtimeExecuted: boolean
): CoverageReport {
  return {
    files_considered: inventory.totalFiles,
    files_scanned: inventory.scannedFiles,
    files_skipped: inventory.skippedFiles,
    unsupported_languages: [], // Populated from inventory analysis
    failed_modules: moduleResults
      .filter((m) => m.status === "failed")
      .map((m) => m.module_name),
    partial_modules: moduleResults
      .filter((m) => m.status === "partial")
      .map((m) => m.module_name),
    successful_modules: moduleResults
      .filter((m) => m.status === "success")
      .map((m) => m.module_name),
    runtime_executed: runtimeExecuted,
  };
}
```

**C7: Reporter updates** — All reporters must include coverage data:

- **Terminal reporter** (`src/reporting/terminal.ts`): Add "Module Coverage" section showing which modules ran (success/partial/failed/skipped), file counts (considered/scanned/skipped), and unsupported languages if any.
- **JSON reporter** (`src/reporting/json.ts`): Include `coverage` field in the top-level output object (already present via `AuditResult.coverage`).
- **Markdown reporter** (`src/reporting/markdown.ts`): Add a "## Coverage" section with a table of module statuses and file scan statistics.

### Task 4.8: M4 tests

- normalize-findings.test.ts — dedup, suppression, hard-stop suppression rejection (C3)
- scoring.test.ts — known findings -> expected scores, clamping, env multiplier, trust credits from repo_profile (C1)
- policy.test.ts — all three profiles, hard-stop triggers
- reporters/*.test.ts — output validation, coverage section presence (C7)

### Calibration Fixtures (C5)

Five fixture definitions for scoring calibration tests. Each fixture defines a synthetic repo scenario with expected axis scores and decision outcomes.

**Fixture 1: Clean repo**
- Has: SECURITY.md, CODEOWNERS, signed tags, all actions pinned to SHA, no issues found
- Modules: all universal modules return status "success" with 0 findings
- Expected: all axes near 0, trust credits fully applied to trustworthiness, confidence "high", decision **PROCEED**

```typescript
// test/fixtures/clean-repo.ts
export const cleanRepoFixture = {
  name: "clean-repo",
  profile: {
    artifacts: { manifests: ["SECURITY.md", "CODEOWNERS", "package.json"], workflows: [".github/workflows/ci.yml"] },
    high_risk_files: [],
  },
  findings: [], // No findings
  moduleResults: universalModulesAllSuccess(),
  expectedScores: { trustworthiness: 0, exploitability: 0, abuse_potential: 0 },
  expectedDecision: "PROCEED",
};
```

**Fixture 2: Secrets repo**
- Has: committed RSA private key (triggers GHA-SECRETS-001, severity critical)
- Expected: hard-stop triggers immediately, decision **ABORT**

```typescript
// test/fixtures/secrets-repo.ts
export const secretsRepoFixture = {
  name: "secrets-repo",
  findings: [
    { id: "GHA-SECRETS-001", severity: "critical", confidence: "high",
      axis_impacts: { trustworthiness: 10, exploitability: 10, abuse_potential: 10 } },
  ],
  expectedDecision: "ABORT",
  expectedHardStop: true,
};
```

**Fixture 3: Dangerous execution repo**
- Has: curl|bash in install script (GHA-EXEC-001), unpinned GitHub Actions (GHA-CI-003)
- Expected: high exploitability + abuse_potential, decision **CAUTION** or **ABORT** depending on profile

```typescript
// test/fixtures/dangerous-exec-repo.ts
export const dangerousExecFixture = {
  name: "dangerous-exec-repo",
  findings: [
    { id: "GHA-EXEC-001", severity: "critical", confidence: "high",
      axis_impacts: { trustworthiness: 2, exploitability: 10, abuse_potential: 10 } },
    { id: "GHA-CI-003", severity: "medium", confidence: "high",
      axis_impacts: { trustworthiness: 3, exploitability: 5, abuse_potential: 3 } },
  ],
  expectedDecision: "ABORT", // GHA-EXEC-001 is a hard-stop rule
  expectedHardStop: true,
};
```

**Fixture 4: MCP server with shell tool**
- Has: unrestricted shell execution tool (GHA-MCP-001, severity critical)
- Expected: hard-stop triggers, decision **ABORT**

```typescript
// test/fixtures/mcp-shell-repo.ts
export const mcpShellFixture = {
  name: "mcp-shell-repo",
  findings: [
    { id: "GHA-MCP-001", severity: "critical", confidence: "low",
      axis_impacts: { trustworthiness: 3, exploitability: 10, abuse_potential: 10 } },
  ],
  expectedDecision: "ABORT",
  expectedHardStop: true,
};
```

**Fixture 5: Well-governed but risky**
- Has: SECURITY.md, CODEOWNERS, signed tags (all governance signals present)
- Also has: floating deps (GHA-SUPPLY-002), debug mode enabled (GHA-WEB-001)
- Expected: trust credits reduce **trustworthiness** axis, but exploitability stays elevated
- Decision: **PROCEED_WITH_CONSTRAINTS**
- **C10 validation**: This fixture MUST verify that trust credits do NOT reduce exploitability or abuse_potential axes. If trust credits mask exploitability findings, C10 should be promoted to FIX NOW.

```typescript
// test/fixtures/well-governed-risky.ts
export const wellGovernedRiskyFixture = {
  name: "well-governed-but-risky",
  profile: {
    artifacts: { manifests: ["SECURITY.md", "CODEOWNERS", "package.json"], workflows: [] },
    high_risk_files: [],
  },
  findings: [
    { id: "GHA-SUPPLY-002", severity: "medium", confidence: "high",
      axis_impacts: { trustworthiness: 2, exploitability: 5, abuse_potential: 2 } },
    { id: "GHA-WEB-001", severity: "medium", confidence: "medium",
      axis_impacts: { trustworthiness: 1, exploitability: 4, abuse_potential: 3 } },
  ],
  moduleResults: universalModulesAllSuccess(),
  // Trust credits: security_md(3) + codeowners(2) = 5 subtracted from trustworthiness ONLY
  // Exploitability and abuse_potential remain elevated (NOT reduced by trust credits)
  expectedScores: {
    trustworthiness: "near_zero_after_credits", // raw ~2.4 - 5 credits = clamped to 0
    exploitability: "elevated",                  // ~7.4 — NOT reduced by trust credits
    abuse_potential: "elevated",                 // ~3.8 — NOT reduced by trust credits
  },
  expectedDecision: "PROCEED_WITH_CONSTRAINTS",
  // C10 TEST: assert exploitability > 0 even though trust credits are applied
  // If this assertion fails, trust credits are incorrectly reducing exploitability
  c10Assertion: "exploitability must NOT be reduced by trust credits",
};
```

---

## Milestone 5 — Extensibility

**Goal**: Plugin backend, Python subprocess stub, GitHub Action, full adapters.

### Task 5.1: Plugin backend interface

**`src/plugins/analyzer-backend.ts`** (finalize)
- `AnalyzerBackend` interface: `type`, `canHandle()`, `execute()`
- Backend registry + dispatcher

```typescript
// Finalized AnalyzerBackend dispatch (added to analyzer-backend.ts)

const backends: AnalyzerBackend[] = [];

export function registerBackend(backend: AnalyzerBackend): void {
  backends.push(backend);
}

export async function dispatchAnalysis(
  moduleName: string,
  workspace: LocalWorkspace,
  profile: RepoProfile,
  context: AuditContext,
  rules: RuleDefinition[]
): Promise<AnalyzerOutput> {
  const backend = backends.find((b) => b.canHandle(moduleName));
  if (!backend) {
    throw new Error(`No backend can handle module: ${moduleName}`);
  }
  return backend.execute(moduleName, workspace, profile, context, rules);
}
```

### Task 5.2: Python subprocess backend stub

**`src/plugins/python-subprocess.ts`**
- stdin/stdout JSON protocol
- MVP: logs "not yet available", returns empty

```typescript
// src/plugins/python-subprocess.ts
import type { AnalyzerBackend, AnalyzerOutput } from "./analyzer-backend";
import type { LocalWorkspace } from "../models/local-workspace";
import type { RepoProfile } from "../models/repo-profile";
import type { AuditContext } from "../models/audit-context";
import type { RuleDefinition } from "../rules/types";

export const pythonSubprocessBackend: AnalyzerBackend = {
  type: "python-subprocess",

  canHandle(_moduleName: string): boolean {
    return false; // Not yet available
  },

  async execute(
    moduleName: string,
    _workspace: LocalWorkspace,
    _profile: RepoProfile,
    _context: AuditContext,
    _rules: RuleDefinition[]
  ): Promise<AnalyzerOutput> {
    console.warn(`Python subprocess backend not yet available for: ${moduleName}`);
    return {
      findings: [],
      moduleResult: {
        module_name: moduleName,
        status: "skipped",
        started_at: new Date().toISOString(),
        findings_emitted: 0,
        warnings: ["Python subprocess backend not yet implemented"],
      },
    };
  },
};
```

### Task 5.3: GitHub Action wrapper

**`action.yml`** — Action metadata, inputs, runs src/cli.ts via Bun.

**`.github/workflows/self-test.yml`** — Dogfood: run on self.

### Task 5.4: GitHub API adapter

**`src/adapters/github-api.ts`** — getRepoMetadata, checkArchived, getLatestRelease. Optional enrichment, graceful degradation without GITHUB_TOKEN.

```typescript
// src/adapters/github-api.ts

export interface RepoMetadata {
  archived: boolean;
  default_branch: string;
  stargazers_count: number;
  pushed_at: string;
  license: string | null;
}

export async function getRepoMetadata(
  owner: string,
  repo: string
): Promise<RepoMetadata | null> {
  // Graceful degradation: return null if GITHUB_TOKEN not set
  // ...
}

export async function checkArchived(
  owner: string,
  repo: string
): Promise<boolean | null> {
  // ...
}

export async function getLatestRelease(
  owner: string,
  repo: string
): Promise<{ tag_name: string; published_at: string } | null> {
  // ...
}
```

### Task 5.5: Scorecard adapter stub

**`src/adapters/scorecard.ts`** — OpenSSF Scorecard API interface, stub.

```typescript
// src/adapters/scorecard.ts

export interface ScorecardResult {
  score: number;
  checks: { name: string; score: number }[];
}

export async function fetchScorecard(
  owner: string,
  repo: string
): Promise<ScorecardResult | null> {
  // Stub: returns null, to be implemented later
  return null;
}
```

### Task 5.6: OSV adapter (full)

**`src/adapters/osv.ts`** (upgrade) — Real HTTP to OSV.dev API.

```typescript
// src/adapters/osv.ts

export interface OsvVulnerability {
  id: string;
  summary: string;
  severity: string;
  affected_versions: string[];
  fixed_version: string | null;
}

/** Stub version (M2) — returns empty */
export async function queryOsvStub(
  _ecosystem: string,
  _packageName: string,
  _version: string
): Promise<OsvVulnerability[]> {
  return [];
}

/** Full version (M5) — real HTTP to OSV.dev */
export async function queryOsv(
  ecosystem: string,
  packageName: string,
  version: string
): Promise<OsvVulnerability[]> {
  const resp = await fetch("https://api.osv.dev/v1/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      package: { name: packageName, ecosystem },
      version,
    }),
  });
  if (!resp.ok) return [];
  const data = (await resp.json()) as { vulns?: any[] };
  return (data.vulns ?? []).map((v: any) => ({
    id: v.id,
    summary: v.summary ?? "",
    severity: v.database_specific?.severity ?? "unknown",
    affected_versions: (v.affected ?? []).flatMap((a: any) =>
      (a.ranges ?? []).flatMap((r: any) =>
        (r.events ?? []).map((e: any) => e.introduced ?? "")
      )
    ),
    fixed_version: null,
  }));
}
```

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

## Full File Manifest (56 files)

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

### Milestone 4 (9 files)
43. `src/engine/normalize-findings.ts`
44. `src/engine/scoring.ts`
45. `src/engine/policy.ts`
46. `src/engine/coverage.ts` (C7)
47. `src/models/audit-result.ts`
48. `src/reporting/terminal.ts`
49. `src/reporting/json.ts`
50. `src/reporting/markdown.ts`
51. `src/reporting/sarif.ts`

### Milestone 5 (5 files)
52. `src/plugins/python-subprocess.ts`
53. `src/adapters/github-api.ts`
54. `src/adapters/scorecard.ts`
55. `src/adapters/osv.ts` (full)
56. `action.yml`
