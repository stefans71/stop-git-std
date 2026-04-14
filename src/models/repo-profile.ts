import { z } from "zod";
import { RepoCategory } from "./enums.ts";

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
  signed_tags_count: z.number().default(0),
  pinned_actions_ratio: z.number().min(0).max(1).default(0),
});

export type RepoProfile = z.infer<typeof RepoProfileSchema>;
