import { z } from "zod";
import { DecisionValue } from "./enums.ts";

export const DecisionSchema = z.object({
  value: DecisionValue,
  reasons: z.array(z.string()),
  constraints: z.array(z.string()),
  hard_stop_triggered: z.boolean().optional(),
  triggered_by_rules: z.array(z.string()).optional(),
  manual_review_required: z.boolean().optional(),
});

export type Decision = z.infer<typeof DecisionSchema>;
