import { nanoid } from "nanoid";
import type { AuditRequest } from "../models/audit-request.ts";
import type { AuditResult, Stage2Trigger, AstRefinementSummary } from "../models/audit-result.ts";
import type { AuditContext } from "../models/audit-context.ts";
import type { Finding } from "../models/finding.ts";
import type { ModuleResult } from "../models/module-result.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { RuleDefinition } from "../rules/types.ts";
import { loadRuleCatalog } from "../rules/load-rule-catalog.ts";
import { loadEngineContract } from "../rules/load-engine-contract.ts";
import { acquireRepo } from "../inventory/acquire-repo.ts";
import { enumerateFiles } from "../inventory/enumerate-files.ts";
import { classifyRepo } from "../inventory/classify-repo.ts";
import { routeModules } from "./router.ts";
import { getAnalyzer } from "../plugins/builtin-ts.ts";
import { normalizeFindings, loadSuppressions, applySuppressions } from "./normalize-findings.ts";
import { computeScores } from "./scoring.ts";
import { evaluatePolicy } from "./policy.ts";
import { buildCoverageReport } from "./coverage.ts";
import { renderTerminalReport } from "../reporting/terminal.ts";
import { renderJsonReport } from "../reporting/json.ts";
import { renderMarkdownReport } from "../reporting/markdown.ts";
import { renderSarifReport } from "../reporting/sarif.ts";

const ENGINE_VERSION = "0.1.0";

const STAGE2_MODULE_MAP: Record<string, "ast" | "sandbox" | "manual_review"> = {
  "GHA-AI-001": "ast",
  "GHA-AGENT-001": "ast",
  "GHA-MCP-001": "ast",
  "GHA-MCP-003": "ast",
  "GHA-EXEC-004": "ast",
  "GHA-EXEC-005": "ast",
  "GHA-EXEC-001": "sandbox",
  "GHA-EXEC-002": "sandbox",
};

export function captureContext(request: AuditRequest): AuditContext {
  return {
    repo_target: request.repo_target,
    ref: request.ref,
    target_environment: request.target_environment,
    expected_permissions: request.expected_permissions,
    runtime_validation_enabled: request.runtime_mode !== "off",
    runtime_mode: request.runtime_mode,
    adoption_mode: request.adoption_mode,
    notes: request.notes,
  };
}

async function runAnalysisPhase(
  moduleNames: string[],
  workspace: LocalWorkspace,
  profile: RepoProfile,
  context: AuditContext,
  rulesByModule: Map<string, RuleDefinition[]>,
  continueOnError: boolean,
): Promise<{ findings: Finding[]; moduleResults: ModuleResult[] }> {
  const findings: Finding[] = [];
  const moduleResults: ModuleResult[] = [];

  for (const moduleName of moduleNames) {
    const analyzer = getAnalyzer(moduleName);
    if (!analyzer) {
      moduleResults.push({
        module_name: moduleName,
        status: "skipped",
        started_at: new Date().toISOString(),
        findings_emitted: 0,
        warnings: [`No analyzer registered for module: ${moduleName}`],
        errors: [],
      });
      continue;
    }

    try {
      const rules = rulesByModule.get(moduleName) ?? [];
      const output = await analyzer.analyze(workspace, profile, context, rules);
      findings.push(...output.findings);
      moduleResults.push(output.moduleResult);
    } catch (err) {
      if (!continueOnError) throw err;
      moduleResults.push({
        module_name: moduleName,
        status: "failed",
        started_at: new Date().toISOString(),
        findings_emitted: 0,
        warnings: [],
        errors: [String(err)],
      });
    }
  }

  return { findings, moduleResults };
}

export async function runAudit(request: AuditRequest): Promise<AuditResult> {
  const startedAt = new Date().toISOString();
  const runId = nanoid();

  // Phase 1: context_capture
  const context = captureContext(request);

  // Load rule catalog and engine contract
  const catalog = loadRuleCatalog();
  const contract = loadEngineContract();

  // Phase 2: repository_acquisition
  const workspace = await acquireRepo(context, runId);

  // Phase 3: inventory_classification
  const inventory = await enumerateFiles(workspace, request.exclude_paths);
  const profile = classifyRepo(inventory, workspace);

  // Phase 4: module_routing
  const activeModules = routeModules(
    profile,
    contract,
    request.enabled_modules,
    request.disabled_modules,
  );

  // Build rules by module map from catalog
  const rulesByModule = new Map<string, RuleDefinition[]>();
  for (const [moduleName, moduleDef] of Object.entries(catalog.modules)) {
    rulesByModule.set(moduleName, moduleDef.rules);
  }
  if (catalog.runtime_rules) {
    rulesByModule.set("runtime_validation", catalog.runtime_rules.rules);
  }

  const continueOnError = contract.execution_defaults.behavior.continue_on_module_error;

  // Phase 5: universal_analysis
  const universalResult = await runAnalysisPhase(
    activeModules.universal,
    workspace,
    profile,
    context,
    rulesByModule,
    continueOnError,
  );

  // Phase 6: typed_analysis
  const typedResult = await runAnalysisPhase(
    activeModules.typed,
    workspace,
    profile,
    context,
    rulesByModule,
    continueOnError,
  );

  // Phase 7: runtime_validation (no-op unless enabled)
  const runtimeFindings: Finding[] = [];

  // Phase 8: finding_normalization
  const allModuleResults = [...universalResult.moduleResults, ...typedResult.moduleResults];
  let findings = normalizeFindings(
    universalResult.findings,
    typedResult.findings,
    runtimeFindings,
  );

  // Load and apply suppressions (C3/C4)
  const suppressions = loadSuppressions(workspace.rootPath);
  findings = applySuppressions(
    findings,
    suppressions,
    catalog.policy_baselines.hard_stop_patterns,
  );

  // Phase 8.5: AST refinement (auto-escalation)
  let ast_refinement_summary: AstRefinementSummary | undefined;

  if (request.depth_mode !== "quick") {
    try {
      const { refineFindings } = await import("../stage2/ast-refiner.ts");
      const refinement = await refineFindings(
        findings,
        workspace,
        request.depth_mode,
        catalog.policy_baselines.hard_stop_patterns,
        STAGE2_MODULE_MAP,
      );
      findings = refinement.findings;
      ast_refinement_summary = refinement.summary;
    } catch (err) {
      console.warn(`[ast-refiner] AST refinement failed, continuing with original findings: ${err}`);
    }
  }

  // Phase 9: scoring
  const scores = computeScores(findings, profile, context, allModuleResults, contract);

  // Phase 10: policy_decision
  const decision = evaluatePolicy(
    findings,
    scores,
    context,
    request.policy_profile,
    contract,
    catalog,
  );

  // ── Stage 2 escalation detection ───────────────────────────────────────────
  let stage2_recommended = false;
  const stage2_triggers: Stage2Trigger[] = [];

  if (!request.skip_stage2 && request.depth_mode !== "deep") {
    const hardStopPatterns: string[] = catalog.policy_baselines.hard_stop_patterns;
    const lowConfHardStops = findings.filter(
      (f) => !f.suppressed && hardStopPatterns.includes(f.id) && f.confidence === "low"
    );

    for (const f of lowConfHardStops) {
      const mod = STAGE2_MODULE_MAP[f.id] ?? "manual_review";
      const label = mod === "ast" ? "code flow analysis"
        : mod === "sandbox" ? "sandbox execution" : "manual review";
      stage2_triggers.push({
        finding_id: f.id,
        reason: `Low-confidence static match \u2014 ${label} could confirm or dismiss this.`,
        recommended_module: mod,
      });
    }

    stage2_recommended = stage2_triggers.length > 0;
  }

  // Build coverage report (C7)
  const coverage = buildCoverageReport(inventory, allModuleResults, false);

  // Build manifest
  const manifest = {
    run_id: runId,
    engine_version: ENGINE_VERSION,
    rule_catalog_version: catalog.version,
    started_at: startedAt,
    completed_at: new Date().toISOString(),
    repo_target: request.repo_target,
    ref: request.ref,
    target_environment: request.target_environment,
    runtime_mode: request.runtime_mode,
    policy_profile: request.policy_profile,
    status: allModuleResults.some((m) => m.status === "failed") ? "partial" as const : "success" as const,
  };

  const result: AuditResult = {
    manifest,
    context,
    profile,
    findings,
    scores,
    decision,
    module_results: allModuleResults,
    coverage,
    reports: {},
    ...(ast_refinement_summary ? { ast_refinement_summary } : {}),
    ...(stage2_recommended ? { stage2_recommended, stage2_triggers } : {}),
  };

  // Phase 11: reporting
  const reporters: Record<string, (r: AuditResult) => string> = {
    json: renderJsonReport,
    markdown: renderMarkdownReport,
    sarif: renderSarifReport,
  };

  for (const format of request.output_formats) {
    const renderer = reporters[format];
    if (renderer) {
      result.reports[format] = renderer(result);
    }
  }

  // Terminal output always
  const terminalOutput = renderTerminalReport(result);
  console.log(terminalOutput);

  return result;
}
