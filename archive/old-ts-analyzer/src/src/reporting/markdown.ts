import type { AuditResult } from "../models/audit-result.ts";
import type { Severity } from "../models/enums.ts";

const SEVERITY_ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];

function escMd(s: string): string {
  return s.replace(/[|`*_[\]]/g, "\\$&");
}

export function renderMarkdownReport(result: AuditResult): string {
  const lines: string[] = [];

  // ── Header ──────────────────────────────────────────────────────────────────
  lines.push("# stop-git-std Audit Report");
  lines.push("");
  lines.push(`**Repository:** ${escMd(result.context.repo_target)}`);
  lines.push(`**Ref:** ${escMd(result.context.ref)}`);
  lines.push(`**Run ID:** ${escMd(result.manifest.run_id)}`);
  lines.push(`**Generated:** ${result.manifest.completed_at ?? result.manifest.started_at}`);
  lines.push("");

  // ── Decision ────────────────────────────────────────────────────────────────
  lines.push("## Decision");
  lines.push("");
  lines.push(`**${result.decision.value}**`);
  if (result.decision.hard_stop_triggered) {
    lines.push("");
    lines.push("> ⚠️ Hard-stop rule triggered — adoption is blocked until resolved.");
  }
  if (result.decision.manual_review_required) {
    lines.push("");
    lines.push("> Manual review required before proceeding.");
  }
  if (result.decision.reasons.length > 0) {
    lines.push("");
    lines.push("### Reasons");
    for (const r of result.decision.reasons) {
      lines.push(`- ${r}`);
    }
  }
  lines.push("");

  // ── Scores ──────────────────────────────────────────────────────────────────
  lines.push("## Scores");
  lines.push("");
  lines.push("| Axis | Score | Confidence |");
  lines.push("|------|------:|-----------|");
  lines.push(`| Trustworthiness | ${result.scores.trustworthiness} | ${result.scores.confidence} |`);
  lines.push(`| Exploitability | ${result.scores.exploitability} | ${result.scores.confidence} |`);
  lines.push(`| Abuse Potential | ${result.scores.abuse_potential} | ${result.scores.confidence} |`);
  if (result.scores.environment_multiplier_applied !== undefined) {
    lines.push("");
    lines.push(
      `> Environment multiplier (${result.context.target_environment}): **${result.scores.environment_multiplier_applied}×** applied to abuse_potential`,
    );
  }
  lines.push("");

  // ── Findings ────────────────────────────────────────────────────────────────
  const activeFindings = result.findings.filter((f) => !f.suppressed);
  const suppressedFindings = result.findings.filter((f) => f.suppressed);

  lines.push("## Findings");
  lines.push("");
  lines.push(`**${activeFindings.length}** active finding(s), **${suppressedFindings.length}** suppressed.`);
  lines.push("");

  if (activeFindings.length > 0) {
    lines.push("| ID | Title | Severity | Confidence | Category | Files |");
    lines.push("|----|-------|----------|------------|----------|-------|");

    const sorted = [...activeFindings].sort(
      (a, b) =>
        SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity),
    );
    for (const f of sorted) {
      const files = (f.files ?? []).slice(0, 2).map(escMd).join(", ");
      lines.push(
        `| \`${f.id}\` | ${escMd(f.title)} | ${f.severity} | ${f.confidence} | ${f.category} | ${files} |`,
      );
    }
    lines.push("");
  }

  // ── Constraints ─────────────────────────────────────────────────────────────
  if (result.decision.constraints.length > 0) {
    lines.push("## Constraints");
    lines.push("");
    for (const c of result.decision.constraints) {
      lines.push(`- ${c}`);
    }
    lines.push("");
  }

  // ── Stage 2 ────────────────────────────────────────────────────────────────
  if (result.stage2_recommended && result.stage2_triggers && result.stage2_triggers.length > 0) {
    lines.push("## Deeper Analysis Recommended");
    lines.push("");
    lines.push(`Static analysis flagged ${result.stage2_triggers.length} issue(s) with low confidence.`);
    lines.push("A deeper scan could confirm or dismiss these before you act on them.");
    lines.push("");
    for (const t of result.stage2_triggers) {
      lines.push(`- **${t.finding_id}**: ${t.reason} *(${t.recommended_module})*`);
    }
    lines.push("");
  }

  // ── Coverage ────────────────────────────────────────────────────────────────
  lines.push("## Coverage");
  lines.push("");
  lines.push("| Metric | Value |");
  lines.push("|--------|------:|");
  lines.push(`| Files considered | ${result.coverage.files_considered} |`);
  lines.push(`| Files scanned | ${result.coverage.files_scanned} |`);
  lines.push(`| Files skipped | ${result.coverage.files_skipped} |`);
  lines.push(`| Runtime executed | ${result.coverage.runtime_executed} |`);
  lines.push(`| Successful modules | ${result.coverage.successful_modules.length} |`);
  lines.push(`| Partial modules | ${result.coverage.partial_modules.length} |`);
  lines.push(`| Failed modules | ${result.coverage.failed_modules.length} |`);
  lines.push("");

  if (result.coverage.failed_modules.length > 0) {
    lines.push("### Failed Modules");
    for (const m of result.coverage.failed_modules) {
      lines.push(`- \`${m}\``);
    }
    lines.push("");
  }

  return lines.join("\n");
}
