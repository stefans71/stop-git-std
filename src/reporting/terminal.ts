import type { AuditResult } from "../engine/run-audit.ts";
import type { Finding } from "../models/finding.ts";

const VERDICT_COLORS: Record<string, string> = {
  PROCEED: "\x1b[32m",            // green
  PROCEED_WITH_CONSTRAINTS: "\x1b[33m", // yellow
  CAUTION: "\x1b[38;5;208m",      // orange
  ABORT: "\x1b[31m",              // red
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: "\x1b[31m",
  high: "\x1b[38;5;208m",
  medium: "\x1b[33m",
  low: "\x1b[36m",
  info: "\x1b[37m",
};

const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const DIM = "\x1b[2m";

export function renderTerminal(result: AuditResult): string {
  const lines: string[] = [];

  // Header
  lines.push("");
  lines.push(`${BOLD}stop-git-std — Repository Safety Audit${RESET}`);
  lines.push(`${"─".repeat(50)}`);
  lines.push(`${DIM}Repository:${RESET} ${result.profile.name}`);
  lines.push(`${DIM}Path:${RESET}       ${result.profile.path}`);
  lines.push(`${DIM}Types:${RESET}      ${result.profile.types.join(", ")}`);
  lines.push(`${DIM}Languages:${RESET}  ${result.profile.languages.join(", ") || "N/A"}`);
  lines.push("");

  // Decision
  const color = VERDICT_COLORS[result.decision.verdict] ?? "";
  lines.push(`${BOLD}Decision: ${color}${result.decision.verdict}${RESET}`);
  lines.push(`${DIM}${result.decision.reasoning}${RESET}`);
  lines.push("");

  // Scores
  lines.push(`${BOLD}Scores${RESET}`);
  lines.push(`  Trustworthiness: ${scoreBar(result.scores.overall.trustworthiness, true)}`);
  lines.push(`  Exploitability:  ${scoreBar(result.scores.overall.exploitability, false)}`);
  lines.push(`  Abuse Potential: ${scoreBar(result.scores.overall.abuse_potential, false)}`);
  lines.push("");

  // Findings summary
  if (result.findings.length === 0) {
    lines.push(`${BOLD}No findings.${RESET}`);
  } else {
    lines.push(`${BOLD}Findings (${result.findings.length})${RESET}`);
    lines.push("");

    // Group by severity
    const bySeverity = new Map<string, Finding[]>();
    for (const f of result.findings) {
      const list = bySeverity.get(f.severity) ?? [];
      list.push(f);
      bySeverity.set(f.severity, list);
    }

    for (const severity of ["critical", "high", "medium", "low", "info"]) {
      const group = bySeverity.get(severity);
      if (!group || group.length === 0) continue;

      const sevColor = SEVERITY_COLORS[severity] ?? "";
      lines.push(`  ${sevColor}${BOLD}${severity.toUpperCase()}${RESET} (${group.length})`);

      for (const finding of group) {
        const file = finding.evidence[0]?.file ?? "";
        const line = finding.evidence[0]?.line ? `:${finding.evidence[0].line}` : "";
        lines.push(`    ${sevColor}●${RESET} ${finding.title}`);
        lines.push(`      ${DIM}${file}${line}${RESET}`);
        if (finding.remediation) {
          lines.push(`      ${DIM}→ ${finding.remediation}${RESET}`);
        }
      }
      lines.push("");
    }
  }

  // Constraints
  if (result.decision.constraints.length > 0) {
    lines.push(`${BOLD}Constraints${RESET}`);
    for (const c of result.decision.constraints) {
      const icon = c.severity === "required" ? "⚠" : "→";
      lines.push(`  ${icon} ${c.description}`);
    }
    lines.push("");
  }

  lines.push(`${"─".repeat(50)}`);
  return lines.join("\n");
}

function scoreBar(value: number, invertColor: boolean): string {
  const filled = Math.round(value / 5);
  const empty = 20 - filled;
  const isGood = invertColor ? value >= 60 : value <= 30;
  const isBad = invertColor ? value <= 30 : value >= 60;
  const color = isGood ? "\x1b[32m" : isBad ? "\x1b[31m" : "\x1b[33m";
  return `${color}${"█".repeat(filled)}${DIM}${"░".repeat(empty)}${RESET} ${value}`;
}
