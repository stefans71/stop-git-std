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

export const OutputFormat = z.enum(["json", "yaml", "markdown", "sarif", "terminal"]);
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
