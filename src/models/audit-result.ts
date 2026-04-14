import { z } from "zod";
import type { RunManifest } from "./run-manifest.ts";
import type { AuditContext } from "./audit-context.ts";
import type { RepoProfile } from "./repo-profile.ts";
import type { Finding } from "./finding.ts";
import type { Scores } from "./scores.ts";
import type { Decision } from "./decision.ts";
import type { ModuleResult } from "./module-result.ts";

export const CoverageReportSchema = z.object({
  files_considered: z.number().int(),
  files_scanned: z.number().int(),
  files_skipped: z.number().int(),
  unsupported_languages: z.array(z.string()),
  failed_modules: z.array(z.string()),
  partial_modules: z.array(z.string()),
  successful_modules: z.array(z.string()),
  runtime_executed: z.boolean(),
});

export type CoverageReport = z.infer<typeof CoverageReportSchema>;

export interface AuditResult {
  manifest: RunManifest;
  context: AuditContext;
  profile: RepoProfile;
  findings: Finding[];
  scores: Scores;
  decision: Decision;
  module_results: ModuleResult[];
  coverage: CoverageReport;
  reports: Record<string, string>;
}
