import type { AuditResult } from "../engine/run-audit.ts";

export function renderMarkdown(result: AuditResult): string {
  const lines: string[] = [];

  lines.push("# Repository Safety Audit Report");
  lines.push("");
  lines.push(`**Tool**: stop-git-std`);
  lines.push(`**Date**: ${new Date().toISOString().split("T")[0]}`);
  lines.push(`**Repository**: ${result.profile.name}`);
  lines.push(`**Path**: \`${result.profile.path}\``);
  lines.push(`**Types**: ${result.profile.types.join(", ")}`);
  lines.push(`**Languages**: ${result.profile.languages.join(", ") || "N/A"}`);
  lines.push("");

  // Decision
  const verdictEmoji: Record<string, string> = {
    PROCEED: "✅",
    PROCEED_WITH_CONSTRAINTS: "⚠️",
    CAUTION: "🟠",
    ABORT: "🛑",
  };

  lines.push("## Decision");
  lines.push("");
  lines.push(
    `**${verdictEmoji[result.decision.verdict] ?? ""} ${result.decision.verdict}**`,
  );
  lines.push("");
  lines.push(result.decision.reasoning);
  lines.push("");

  // Scores
  lines.push("## Scores");
  lines.push("");
  lines.push("| Axis | Score |");
  lines.push("|------|-------|");
  lines.push(`| Trustworthiness | ${result.scores.overall.trustworthiness}/100 |`);
  lines.push(`| Exploitability | ${result.scores.overall.exploitability}/100 |`);
  lines.push(`| Abuse Potential | ${result.scores.overall.abuse_potential}/100 |`);
  lines.push("");

  // Findings
  if (result.findings.length > 0) {
    lines.push("## Findings");
    lines.push("");
    lines.push(`**Total**: ${result.findings.length} findings`);
    lines.push("");

    lines.push("| Severity | Rule | Title | File | Remediation |");
    lines.push("|----------|------|-------|------|-------------|");

    for (const f of result.findings) {
      const file = f.evidence[0]?.file ?? "";
      const line = f.evidence[0]?.line ? `:${f.evidence[0].line}` : "";
      lines.push(
        `| ${f.severity} | ${f.ruleId} | ${f.title} | \`${file}${line}\` | ${f.remediation ?? "—"} |`,
      );
    }
    lines.push("");
  } else {
    lines.push("## Findings");
    lines.push("");
    lines.push("No findings detected.");
    lines.push("");
  }

  // Constraints
  if (result.decision.constraints.length > 0) {
    lines.push("## Constraints");
    lines.push("");
    for (const c of result.decision.constraints) {
      lines.push(`- **[${c.severity}]** ${c.description}`);
    }
    lines.push("");
  }

  // Summary
  lines.push("## Summary");
  lines.push("");
  lines.push("| Metric | Count |");
  lines.push("|--------|-------|");
  lines.push(`| Critical | ${result.decision.criticalFindings} |`);
  lines.push(`| High | ${result.decision.highFindings} |`);
  lines.push(`| Medium | ${result.findings.filter((f) => f.severity === "medium").length} |`);
  lines.push(`| Low | ${result.findings.filter((f) => f.severity === "low").length} |`);
  lines.push(`| Info | ${result.findings.filter((f) => f.severity === "info").length} |`);
  lines.push(`| **Total** | **${result.findings.length}** |`);
  lines.push("");

  return lines.join("\n");
}
