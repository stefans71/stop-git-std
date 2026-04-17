import { z } from "zod";
import { RunManifestStatus, Environment, RuntimeMode, PolicyProfile } from "./enums.ts";

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
