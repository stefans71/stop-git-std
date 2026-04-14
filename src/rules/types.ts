import { z } from "zod";
import { Severity, Confidence, ProofType } from "../models/enums.ts";

export const DetectionSpecSchema = z.object({
  primary_method: z.string(),
  secondary_methods: z.array(z.string()).optional(),
  logic: z.string(),
  params: z.record(z.string(), z.unknown()).optional(),
  file_patterns: z.array(z.string()).optional(),
  regex: z.string().optional(),
});

export type DetectionSpec = z.infer<typeof DetectionSpecSchema>;

export const EvidenceShapeSchema = z.object({
  type: z.string(),
  fields: z.array(z.string()),
});

export type EvidenceShape = z.infer<typeof EvidenceShapeSchema>;

export const RuleAxisImpactsSchema = z.object({
  trustworthiness: z.number(),
  exploitability: z.number(),
  abuse_potential: z.number(),
});

export const PolicyHintsSchema = z.object({
  hard_stop: z.boolean(),
  constrain_if_present: z.boolean(),
});

export const RuleDefinitionSchema = z.object({
  id: z.string(),
  title: z.string(),
  category: z.string(),
  subcategory: z.string().optional(),
  default_severity: Severity,
  default_confidence: Confidence,
  proof_type: ProofType,
  rationale: z.string().optional(),
  applies_to: z.record(z.string(), z.unknown()).optional(),
  detection: DetectionSpecSchema,
  evidence_shape: EvidenceShapeSchema,
  axis_impacts: RuleAxisImpactsSchema,
  remediation: z.string(),
  policy_hints: PolicyHintsSchema,
});

export type RuleDefinition = z.infer<typeof RuleDefinitionSchema>;

export const ModuleDefinitionSchema = z.object({
  description: z.string(),
  recommended_methods: z.array(z.string()).optional(),
  rules: z.array(RuleDefinitionSchema),
});

export type ModuleDefinition = z.infer<typeof ModuleDefinitionSchema>;

export const ScoringDefaultsSchema = z.object({
  severity_weights: z.record(Severity, z.number()),
  confidence_multipliers: z.record(Confidence, z.number()),
  environment_abuse_multipliers: z.record(z.string(), z.number()),
});

export type ScoringDefaults = z.infer<typeof ScoringDefaultsSchema>;

export const RuleCatalogSchema = z.object({
  version: z.number(),
  name: z.string(),
  status: z.string(),
  purpose: z.string(),
  meta: z.record(z.string(), z.unknown()),
  scoring_defaults: ScoringDefaultsSchema,
  modules: z.record(z.string(), ModuleDefinitionSchema),
  runtime_rules: ModuleDefinitionSchema.optional(),
  policy_baselines: z.object({
    hard_stop_patterns: z.array(z.string()),
    proceed_with_constraints_examples: z.array(z.string()).optional(),
  }),
});

export type RuleCatalog = z.infer<typeof RuleCatalogSchema>;

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

export const EngineContractSchema = z.object({
  version: z.number(),
  name: z.string(),
  status: z.string().optional(),
  purpose: z.string().optional(),
  references: z.record(z.string(), z.string()).optional(),
  meta: z.record(z.string(), z.unknown()).optional(),
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
  enums: z.record(z.string(), z.array(z.string())).optional(),
  inputs: z.record(z.string(), z.unknown()).optional(),
  artifacts: z.record(z.string(), z.unknown()).optional(),
  phase_order: z.array(z.string()),
  phases: z.record(z.string(), z.unknown()).optional(),
  module_routing: z.object({
    universal_modules: z.array(z.string()),
    category_routes: z.record(z.string(), z.array(z.string())),
  }),
  rule_evaluation_contract: z.record(z.string(), z.unknown()).optional(),
  confidence_model: z.object({
    description: z.string().optional(),
    inputs: z.array(z.string()).optional(),
    rules: z.array(z.object({
      name: z.string(),
      when: z.record(z.string(), z.unknown()).optional(),
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
  suppressions: z.record(z.string(), z.unknown()).optional(),
  error_handling: z.record(z.string(), z.unknown()).optional(),
  coverage_contract: z.record(z.string(), z.unknown()).optional(),
  sarif_mapping: z.record(z.string(), z.unknown()).optional(),
  decision_generation: z.record(z.string(), z.unknown()).optional(),
  example_run: z.record(z.string(), z.unknown()).optional(),
  implementation_notes: z.record(z.string(), z.unknown()).optional(),
  next_expansion_candidates: z.array(z.string()).optional(),
});

export type EngineContract = z.infer<typeof EngineContractSchema>;
