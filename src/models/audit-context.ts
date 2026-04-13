import { z } from "zod";
import { Environment, RuntimeMode, AdoptionMode } from "./enums.ts";

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
