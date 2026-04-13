import type { AnalyzerBackend } from "./analyzer-backend.ts";
import type { AnalyzerOutput } from "./analyzer-backend.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { RuleDefinition } from "../rules/types.ts";

/**
 * Python subprocess backend stub.
 *
 * This backend is a placeholder for future integration with Python-based
 * analyzers (e.g., Bandit, Semgrep Python rules).  It intentionally does
 * nothing so that the router can safely fall through to another backend.
 */
export const pythonSubprocessBackend: AnalyzerBackend = {
  type: "python-subprocess",

  canHandle(_moduleName: string): boolean {
    // Not yet implemented — never claims ownership of any module.
    return false;
  },

  async execute(
    moduleName: string,
    _workspace: LocalWorkspace,
    _profile: RepoProfile,
    _context: AuditContext,
    _rules: RuleDefinition[],
  ): Promise<AnalyzerOutput> {
    const started_at = new Date().toISOString();
    return {
      findings: [],
      moduleResult: {
        module_name: moduleName,
        status: "skipped",
        started_at,
        completed_at: new Date().toISOString(),
        findings_emitted: 0,
        warnings: ["python-subprocess backend is not yet implemented"],
        errors: [],
      },
    };
  },
};
