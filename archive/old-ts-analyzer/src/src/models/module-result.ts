import { z } from "zod";
import { ModuleStatus } from "./enums.ts";

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
