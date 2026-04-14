import pc from "picocolors";
import type { AuditResult } from "../models/audit-result.ts";
import type { Finding } from "../models/finding.ts";
import type { Severity } from "../models/enums.ts";

// ── Colour helpers ────────────────────────────────────────────────────────────

function colorDecision(value: string): string {
  switch (value) {
    case "PROCEED":
      return pc.green(pc.bold("✓ PROCEED"));
    case "PROCEED_WITH_CONSTRAINTS":
      return pc.cyan(pc.bold("⚠ PROCEED WITH CONSTRAINTS"));
    case "CAUTION":
      return pc.yellow(pc.bold("⚠ CAUTION"));
    case "ABORT":
      return pc.red(pc.bold("✗ ABORT"));
    default:
      return value;
  }
}

function colorSeverity(sev: Severity): string {
  switch (sev) {
    case "critical":
      return pc.red(pc.bold("CRITICAL"));
    case "high":
      return pc.red("HIGH");
    case "medium":
      return pc.yellow("MEDIUM");
    case "low":
      return pc.cyan("LOW");
    case "info":
      return pc.gray("INFO");
  }
}

function scoreColor(score: number): string {
  if (score <= 20) return pc.green(String(score));
  if (score <= 50) return pc.yellow(String(score));
  if (score <= 75) return pc.red(String(score));
  return pc.red(pc.bold(String(score)));
}

function scoreLabel(score: number): string {
  if (score <= 20) return pc.green("Low");
  if (score <= 50) return pc.yellow("Moderate");
  if (score <= 75) return pc.red("Elevated");
  return pc.red(pc.bold("Critical"));
}

function scoreBar(score: number, width: number = 20): string {
  const filled = Math.round((score / 100) * width);
  const empty = width - filled;
  const bar = "█".repeat(filled) + "░".repeat(empty);
  if (score <= 20) return pc.green(bar);
  if (score <= 50) return pc.yellow(bar);
  if (score <= 75) return pc.red(bar);
  return pc.red(pc.bold(bar));
}

// ── Decision explanations ────────────────────────────────────────────────────

function decisionExplanation(result: AuditResult): string[] {
  const lines: string[] = [];
  switch (result.decision.value) {
    case "PROCEED":
      lines.push(pc.green("  This repo passed all safety checks. No critical or high-severity"));
      lines.push(pc.green("  issues found. Safe to adopt, run, or integrate."));
      break;
    case "PROCEED_WITH_CONSTRAINTS":
      lines.push(pc.cyan("  This repo has issues that need mitigation before use."));
      lines.push(pc.cyan("  Review the constraints below and apply them before adoption."));
      break;
    case "CAUTION":
      lines.push(pc.yellow("  This repo has elevated risk. Manual review recommended before"));
      lines.push(pc.yellow("  adoption. Review all findings and assess whether the risks"));
      lines.push(pc.yellow("  are acceptable for your use case."));
      break;
    case "ABORT":
      lines.push(pc.red("  This repo triggered one or more hard-stop rules. These indicate"));
      lines.push(pc.red("  dangerous patterns that make the repo unsafe to adopt without"));
      lines.push(pc.red("  significant remediation. Do NOT adopt until issues are resolved."));
      break;
  }
  return lines;
}

// ── Finding risk explanations ────────────────────────────────────────────────

const RISK_EXPLANATIONS: Record<string, string> = {
  "GHA-EXEC-001":
    "Downloads and executes remote code in a single command. An attacker who compromises the URL can execute arbitrary code on your machine during install.",
  "GHA-EXEC-002":
    "Runs code automatically during package install. Malicious packages use this to execute code before you review anything.",
  "GHA-EXEC-003":
    "Allows arbitrary shell commands from string input. If user data reaches this, it's remote code execution.",
  "GHA-EXEC-004":
    "Deserializes untrusted data into executable objects. Attacker-crafted payloads can execute arbitrary code.",
  "GHA-EXEC-005":
    "Fetches remote content then executes or loads it as code. If the remote source is compromised, your system is compromised.",
  "GHA-CI-001":
    "Runs CI workflows with write access on pull requests from forks. Attackers can submit PRs that execute code with your repo's secrets.",
  "GHA-CI-002":
    "GitHub token has broad permissions. A compromised workflow step can push code, delete branches, or access secrets.",
  "GHA-CI-003":
    "Actions pinned to tags instead of commit SHAs. If the action repo is compromised, the tag can be moved to malicious code.",
  "GHA-CI-004":
    "Untrusted user input (PR title, issue body) injected directly into shell commands. Attackers craft input that executes arbitrary commands.",
  "GHA-CI-005":
    "Self-hosted runners execute untrusted code from forks. The runner's host machine, network, and credentials are exposed.",
  "GHA-SECRETS-001":
    "Private key material committed to the repository. Anyone with repo access can impersonate the key owner.",
  "GHA-SECRETS-002":
    "Environment file with probable secrets committed. Database passwords, API keys, or tokens may be exposed.",
  "GHA-SECRETS-003":
    "High-entropy string near auth keywords detected. May be a real API key or token — verify manually.",
  "GHA-SUPPLY-001":
    "No lockfile means dependency versions aren't pinned. A compromised registry could serve malicious versions.",
  "GHA-SUPPLY-002":
    "Dependencies use floating version ranges. A malicious version published within range would be installed automatically.",
  "GHA-SUPPLY-003":
    "Dependencies sourced from raw git URLs instead of registries. No audit trail or integrity verification.",
  "GHA-SUPPLY-005":
    "Binary files without source provenance. Could contain malware that bypasses code review.",
  "GHA-TRUST-001":
    "No security disclosure policy. Vulnerability reporters have no way to reach maintainers privately.",
  "GHA-TRUST-002":
    "No code ownership defined. No guarantee that changes to sensitive files are reviewed by qualified maintainers.",
  "GHA-AI-001":
    "LLM output flows directly to tool execution without validation. A prompt injection could execute arbitrary tools.",
  "GHA-AI-002":
    "Secrets or sensitive data included in prompts. LLM providers may log or train on this data.",
  "GHA-AGENT-001":
    "Agent has shell, write, and network access without human approval. A misbehaving agent can exfiltrate data or destroy files.",
  "GHA-MCP-001":
    "MCP server exposes unrestricted shell execution. Any connected client can run arbitrary commands on the host.",
  "GHA-MCP-003":
    "MCP server forwards auth tokens into tool calls. A malicious tool request can capture credentials.",
  "GHA-PLUGIN-002":
    "Plugin instructions attempt to override the AI's identity or safety boundaries. May be benign (defining a persona) or malicious (bypassing guardrails).",
  "GHA-INFRA-001":
    "Container runs as root. A container escape gives the attacker root access to the host.",
  "GHA-INFRA-002":
    "Container uses :latest tag. Builds are not reproducible and a compromised image affects all future builds.",
};

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
  const hr = pc.dim("─".repeat(68));
  const hrBold = "═".repeat(68);

  lines.push("");
  lines.push(pc.bold(hrBold));
  lines.push(pc.bold("  stop-git-std — Repository Safety Audit"));
  lines.push(pc.bold(hrBold));
  lines.push("");

  // ── Decision ──
  lines.push(`  ${colorDecision(result.decision.value)}`);
  lines.push("");
  lines.push(...decisionExplanation(result));
  lines.push("");

  if (result.decision.reasons.length > 0) {
    for (const r of result.decision.reasons) {
      lines.push(`  ${pc.dim("•")} ${r}`);
    }
    lines.push("");
  }

  lines.push(hr);

  // ── Scores with bars ──
  lines.push("");
  lines.push(pc.bold("  Risk Scores") + pc.dim("  (0 = safe, 100 = critical risk)"));
  lines.push("");

  const tw = result.scores.trustworthiness;
  const ex = result.scores.exploitability;
  const ap = result.scores.abuse_potential;

  lines.push(
    `  Trustworthiness  ${scoreBar(tw)}  ${scoreColor(tw).padStart(12)} / 100  ${scoreLabel(tw)}`,
  );
  lines.push(
    pc.dim("                   How well-governed and maintained is the source?"),
  );
  lines.push(
    `  Exploitability   ${scoreBar(ex)}  ${scoreColor(ex).padStart(12)} / 100  ${scoreLabel(ex)}`,
  );
  lines.push(
    pc.dim("                   How exposed is the attack surface?"),
  );
  lines.push(
    `  Abuse Potential  ${scoreBar(ap)}  ${scoreColor(ap).padStart(12)} / 100  ${scoreLabel(ap)}`,
  );
  lines.push(
    pc.dim("                   How easily could this be misused in your environment?"),
  );
  lines.push("");
  lines.push(
    `  Confidence: ${pc.bold(result.scores.confidence)}` +
      (result.scores.environment_multiplier_applied !== undefined
        ? pc.dim(
            `  |  Env: ${result.scores.environment_multiplier_applied}x on abuse_potential`,
          )
        : ""),
  );

  lines.push("");
  lines.push(hr);

  // ── Findings detail ──
  const counts = countBySeverity(result.findings);
  const active = result.findings.filter((f) => !f.suppressed);
  const suppressed = result.findings.filter((f) => f.suppressed);

  lines.push("");
  lines.push(
    pc.bold(`  Findings`) +
      `  ${active.length} active` +
      (suppressed.length > 0 ? pc.dim(`, ${suppressed.length} suppressed`) : ""),
  );
  lines.push("");

  // Severity summary bar
  const sevLine = (["critical", "high", "medium", "low", "info"] as Severity[])
    .filter((s) => counts[s] > 0)
    .map((s) => `${colorSeverity(s)} ${counts[s]}`)
    .join("  ");
  if (sevLine) lines.push(`  ${sevLine}`);
  lines.push("");

  // Detailed findings — ALL of them, grouped by severity
  const sorted = active.sort((a, b) => {
    const order: Severity[] = ["critical", "high", "medium", "low", "info"];
    return order.indexOf(a.severity) - order.indexOf(b.severity);
  });

  for (const f of sorted) {
    lines.push(`  ${colorSeverity(f.severity)}  ${f.id}`);
    lines.push(`  ${pc.bold(f.title)}`);

    if (f.files && f.files.length > 0) {
      const shortFiles = f.files
        .slice(0, 3)
        .map((p) => {
          const parts = p.split("/");
          return parts.length > 3
            ? ".../" + parts.slice(-2).join("/")
            : p;
        });
      lines.push(`  ${pc.dim("Files:")} ${shortFiles.join(", ")}`);
    }

    // Risk explanation
    const explanation = RISK_EXPLANATIONS[f.id];
    if (explanation) {
      lines.push(`  ${pc.dim("Risk:")}  ${explanation}`);
    }

    // Remediation from the finding
    if (f.remediation) {
      lines.push(`  ${pc.dim("Fix:")}   ${f.remediation}`);
    }

    lines.push("");
  }

  // Suppressed findings summary
  if (suppressed.length > 0) {
    lines.push(
      pc.dim(`  ${suppressed.length} finding(s) suppressed by .stop-git-std.suppressions.yaml`),
    );
    for (const f of suppressed) {
      lines.push(
        pc.dim(`    [${f.severity}] ${f.id} — ${f.title} (${f.suppression_reason || "suppressed"})`),
      );
    }
    lines.push("");
  }

  // Constraints
  if (result.decision.constraints.length > 0) {
    lines.push(hr);
    lines.push("");
    lines.push(pc.bold("  Required Mitigations"));
    lines.push(
      pc.dim("  Apply these before adopting this repo:"),
    );
    lines.push("");
    for (const c of result.decision.constraints) {
      lines.push(`  ${pc.cyan("→")} ${c}`);
    }
    lines.push("");
  }

  // Coverage
  lines.push(hr);
  lines.push("");
  lines.push(pc.bold("  Coverage"));
  lines.push(
    `  Files: ${result.coverage.files_scanned} scanned / ${result.coverage.files_considered} total` +
      (result.coverage.files_skipped > 0
        ? pc.dim(` (${result.coverage.files_skipped} skipped — too large or excluded)`)
        : ""),
  );
  lines.push(
    `  Runtime: ${result.coverage.runtime_executed ? pc.green("yes") : pc.dim("no (static analysis only)")}`,
  );

  if (result.coverage.successful_modules.length > 0) {
    lines.push(
      `  Modules: ${pc.green(String(result.coverage.successful_modules.length) + " ok")}` +
        (result.coverage.partial_modules.length > 0
          ? `, ${pc.yellow(String(result.coverage.partial_modules.length) + " partial")}`
          : "") +
        (result.coverage.failed_modules.length > 0
          ? `, ${pc.red(String(result.coverage.failed_modules.length) + " failed")}`
          : ""),
    );
    lines.push(
      pc.dim(`  ${result.coverage.successful_modules.join(", ")}`),
    );
  }

  if (result.coverage.failed_modules.length > 0) {
    lines.push(
      pc.red(
        `  ⚠ Failed modules: ${result.coverage.failed_modules.join(", ")}`,
      ),
    );
    lines.push(
      pc.red("    Results may be incomplete — re-run or investigate module failures."),
    );
  }

  lines.push("");
  lines.push(hr);
  lines.push("");

  return lines.join("\n");
}
