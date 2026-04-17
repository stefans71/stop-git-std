import { z } from "zod";
import { Confidence } from "./enums.ts";

export const ScoresSchema = z.object({
  trustworthiness: z.number().int().min(0).max(100),
  exploitability: z.number().int().min(0).max(100),
  abuse_potential: z.number().int().min(0).max(100),
  confidence: Confidence,
  component_breakdown: z.record(z.string(), z.unknown()).optional(),
  environment_multiplier_applied: z.number().optional(),
});

export type Scores = z.infer<typeof ScoresSchema>;
