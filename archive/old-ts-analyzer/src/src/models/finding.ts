import { z } from "zod";
import { Severity, Confidence, ProofType } from "./enums.ts";

export const AxisImpactsSchema = z.object({
  trustworthiness: z.number(),
  exploitability: z.number(),
  abuse_potential: z.number(),
});

export type AxisImpacts = z.infer<typeof AxisImpactsSchema>;

export const EvidenceSchema = z.object({
  type: z.string(),
  records: z.array(z.record(z.string(), z.unknown())),
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
