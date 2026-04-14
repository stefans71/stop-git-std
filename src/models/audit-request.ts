import { z } from "zod";
import {
  Environment,
  RuntimeMode,
  AdoptionMode,
  OutputFormat,
  PolicyProfile,
} from "./enums.ts";

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
