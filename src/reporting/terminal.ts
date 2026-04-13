import pc from "picocolors";
import type { AuditResult } from "../models/audit-result.ts";
import type { Finding } from "../models/finding.ts";
import type { Severity } from "../models/enums.ts";

// ── Colour helpers ────────────────────────────────────────────────────────────

function colorDecision(value: string): string {
  switch (value) {
    case "PROCEED":
      return pc.green(value);
    case "PROCEED_WITH_CONSTRAINTS":
      return pc.cyan(value);
    case "CAUTION":
      return pc.yellow(value);
    case "ABORT":
      return pc.red(pc.bold(value));
    default:
      return value;
  }
}

function colorSeverity(sev: Severity): string {
  switch (sev) {
    case "critical":
      return pc.red(pc.bold(sev));
    case "high":
      return pc.red(sev);
    case "medium":
      return pc.yellow(sev);
    case "low":
      return pc.cyan(sev);
    case "info":
      return pc.gray(sev);
  }
}

// ── Severity counts ───────────────────────────────────────────────────────────

function countBySeverity(findings: Finding[]): Record<Severity, number> {
  const counts: Record<Severity, number> = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    info: 0,
  };
  for (const f of findings) {
    if (!f.suppressed) counts[f.severity]++;
  }
  return counts;
}

// ── Main renderer ─────────────────────────────────────────────────────────────

export function renderTerminalReport(result: AuditResult): string {
  const lines: string[] = [];
  const hr = pc.dim("─".repeat(60));

  lines.push("");
  lines.push(pc.bold("╔══ stop-git-std Audit Report ══╗"));
  lines.push(hr);

  // Decision
  lines.push(`  Decision: ${colorDecision(result.decision.value)}`);
  if (result.decision.hard_stop_triggered) {
    lines.push(`  ${pc.red("⚠  Hard-stop rule triggered — adoption blocked")}`);
  }
  if (result.decision.manual_review_required) {
    lines.push(`  ${pc.yellow("Manual review required before proceeding")}`);
  }
  if (result.decision.reasons.length > 0) {
    lines.push(`  Reasons:`);
    for (const r of result.decision.reasons) {
      lines.push(`    • ${r}`);
    }
  }

  lines.push(hr);

  // Scores
  lines.push(pc.bold("  Scores"));
  lines.push(`    Trustworthiness : ${pc.bold(String(result.scores.trustworthiness))}`);
  lines.push(`    Exploitability  : ${pc.bold(String(result.scores.exploitability))}`);
  lines.push(`    Abuse Potential : ${pc.bold(String(result.scores.abuse_potential))}`);
  lines.push(`    Confidence      : ${result.scores.confidence}`);
  if (result.scores.environment_multiplier_applied !== undefined) {
    lines.push(
      `    Env multiplier  : ${result.scores.environment_multiplier_applied}x (abuse_potential)`,
    );
  }

  lines.push(hr);

  // Findings summary
  const counts = countBySeverity(result.findings);
  const total = result.findings.filter((f) => !f.suppressed).length;
  const suppressed = result.findings.filter((f) => f.suppressed).length;
  lines.push(pc.bold(`  Findings  (${total} active, ${suppressed} suppressed)`));
  for (const sev of ["critical", "high", "medium", "low", "info"] as Severity[]) {
    if (counts[sev] > 0) {
      lines.push(`    ${colorSeverity(sev).padEnd(20)} ${counts[sev]}`);
    }
  }

  // Top findings
  const topFindings = result.findings
    .filter((f) => !f.suppressed)
    .sort((a, b) => {
      const order: Severity[] = ["critical", "high", "medium", "low", "info"];
      return order.indexOf(a.severity) - order.indexOf(b.severity);
    })
    .slice(0, 5);

  if (topFindings.length > 0) {
    lines.push("");
    lines.push(pc.bold("  Top Findings"));
    for (const f of topFindings) {
      lines.push(
        `    [${colorSeverity(f.severity)}] ${f.id} — ${f.title}`,
      );
      if (f.files && f.files.length > 0) {
        lines.push(`      ${pc.dim("Files: " + f.files.slice(0, 3).join(", "))}`);
      }
    }
  }

  // Constraints
  if (result.decision.constraints.length > 0) {
    lines.push(hr);
    lines.push(pc.bold("  Constraints"));
    for (const c of result.decision.constraints) {
      lines.push(`    • ${c}`);
    }
  }

  // Coverage
  lines.push(hr);
  lines.push(pc.bold("  Module Coverage"));
  lines.push(`    Files considered  : ${result.coverage.files_considered}`);
  lines.push(`    Files scanned     : ${result.coverage.files_scanned}`);
  lines.push(`    Files skipped     : ${result.coverage.files_skipped}`);
  lines.push(`    Runtime executed  : ${result.coverage.runtime_executed}`);
  if (result.coverage.successful_modules.length > 0) {
    lines.push(
      `    ${pc.green("Success")} (${result.coverage.successful_modules.length}): ${result.coverage.successful_modules.join(", ")}`,
    );
  }
  if (result.coverage.partial_modules.length > 0) {
    lines.push(
      `    ${pc.yellow("Partial")} (${result.coverage.partial_modules.length}): ${result.coverage.partial_modules.join(", ")}`,
    );
  }
  if (result.coverage.failed_modules.length > 0) {
    lines.push(
      `    ${pc.red("Failed")} (${result.coverage.failed_modules.length}): ${result.coverage.failed_modules.join(", ")}`,
    );
  }

  lines.push(hr);
  lines.push("");

  return lines.join("\n");
}
