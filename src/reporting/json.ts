import type { AuditResult } from "../engine/run-audit.ts";

export function renderJson(result: AuditResult): string {
  const output = {
    meta: {
      tool: "stop-git-std",
      version: "0.1.0",
      timestamp: new Date().toISOString(),
    },
    repository: {
      name: result.profile.name,
      path: result.profile.path,
      types: result.profile.types,
      languages: result.profile.languages,
      frameworks: result.profile.frameworks.map((f) => ({
        name: f.name,
        version: f.version,
        confidence: f.confidence,
      })),
      stats: {
        totalFiles: result.profile.inventory.totalFiles,
        hasLockfile: result.profile.hasLockfile,
        hasCiConfig: result.profile.hasCiConfig,
        hasDockerfile: result.profile.hasDockerfile,
        hasK8sConfig: result.profile.hasK8sConfig,
      },
    },
    decision: {
      verdict: result.decision.verdict,
      reasoning: result.decision.reasoning,
      constraints: result.decision.constraints,
    },
    scores: {
      overall: result.scores.overall,
      categories: result.scores.categories,
    },
    findings: result.findings.map((f) => ({
      id: f.id,
      ruleId: f.ruleId,
      category: f.category,
      severity: f.severity,
      title: f.title,
      description: f.description,
      evidence: f.evidence,
      remediation: f.remediation,
      confidence: f.confidence,
      tags: f.tags,
    })),
    summary: {
      totalFindings: result.findings.length,
      critical: result.decision.criticalFindings,
      high: result.decision.highFindings,
      medium: result.findings.filter((f) => f.severity === "medium").length,
      low: result.findings.filter((f) => f.severity === "low").length,
      info: result.findings.filter((f) => f.severity === "info").length,
    },
  };

  return JSON.stringify(output, null, 2);
}
