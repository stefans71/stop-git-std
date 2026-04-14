import type { FileInventory } from "../inventory/enumerate-files.ts";
import type { ModuleResult } from "../models/module-result.ts";
import type { CoverageReport } from "../models/audit-result.ts";

/**
 * Build a CoverageReport from the file inventory, module results, and
 * a flag indicating whether runtime execution was attempted.
 */
export function buildCoverageReport(
  inventory: FileInventory,
  moduleResults: ModuleResult[],
  runtimeExecuted: boolean,
): CoverageReport {
  const failed_modules: string[] = [];
  const partial_modules: string[] = [];
  const successful_modules: string[] = [];

  for (const m of moduleResults) {
    switch (m.status) {
      case "failed":
        failed_modules.push(m.module_name);
        break;
      case "partial":
        partial_modules.push(m.module_name);
        break;
      case "success":
        successful_modules.push(m.module_name);
        break;
      // pending / running / skipped are not categorised in the report
    }
  }

  // Derive unsupported languages from skipped modules' warnings if possible;
  // for now, surface the set of extensions with no matching analyzer as unknown
  const unsupported_languages: string[] = [];

  return {
    files_considered: inventory.totalFiles,
    files_scanned: inventory.scannedFiles,
    files_skipped: inventory.skippedFiles,
    unsupported_languages,
    failed_modules,
    partial_modules,
    successful_modules,
    runtime_executed: runtimeExecuted,
  };
}
