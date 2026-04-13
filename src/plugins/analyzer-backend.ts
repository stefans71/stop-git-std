import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { Finding } from "../models/finding.ts";
import type { ModuleResult } from "../models/module-result.ts";
import type { RuleDefinition } from "../rules/types.ts";

export interface AnalyzerOutput {
  findings: Finding[];
  moduleResult: ModuleResult;
}

export interface AnalyzerModule {
  name: string;
  analyze(
    workspace: LocalWorkspace,
    profile: RepoProfile,
    context: AuditContext,
    rules: RuleDefinition[],
  ): Promise<AnalyzerOutput>;
}

export interface AnalyzerBackend {
  type: "builtin-ts" | "python-subprocess" | "external";
  canHandle(moduleName: string): boolean;
  execute(
    moduleName: string,
    workspace: LocalWorkspace,
    profile: RepoProfile,
    context: AuditContext,
    rules: RuleDefinition[],
  ): Promise<AnalyzerOutput>;
}

const backends: AnalyzerBackend[] = [];

export function registerBackend(backend: AnalyzerBackend): void {
  backends.push(backend);
}

export async function dispatchAnalysis(
  moduleName: string,
  workspace: LocalWorkspace,
  profile: RepoProfile,
  context: AuditContext,
  rules: RuleDefinition[],
): Promise<AnalyzerOutput> {
  const backend = backends.find((b) => b.canHandle(moduleName));
  if (!backend) {
    throw new Error(`No backend can handle module: ${moduleName}`);
  }
  return backend.execute(moduleName, workspace, profile, context, rules);
}
