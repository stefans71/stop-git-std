import type { AuditResult } from "../models/audit-result.ts";

/**
 * Serialize the full AuditResult as pretty-printed JSON.
 */
export function renderJsonReport(result: AuditResult): string {
  return JSON.stringify(result, null, 2);
}
