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

// ── Plain English summary ────────────────────────────────────────────────────

function renderPlainEnglish(result: AuditResult): string[] {
  const lines: string[] = [];
  const active = result.findings.filter((f) => !f.suppressed);
  const critical = active.filter((f) => f.severity === "critical");
  const high = active.filter((f) => f.severity === "high");
  const medium = active.filter((f) => f.severity === "medium");

  lines.push(pc.bold("  What This Means"));
  lines.push(pc.dim("  " + "\u2500".repeat(30)));
  lines.push("");

  switch (result.decision.value) {
    case "PROCEED":
      lines.push("  No serious issues detected in our static checks. We scanned");
      lines.push(`  ${result.coverage.files_scanned} files and found nothing that would`);
      lines.push("  prevent safe adoption.");
      break;
    case "PROCEED_WITH_CONSTRAINTS":
      lines.push("  We found some issues that need attention before you use this.");
      lines.push("  None are critically dangerous, but the mitigations listed below");
      lines.push("  should be applied first.");
      break;
    case "CAUTION":
      lines.push("  We found issues that deserve a closer look before you use this.");
      lines.push("  Review the findings below and decide whether the risks are");
      lines.push("  acceptable for your use case.");
      break;
    case "ABORT":
      lines.push("  We found serious security issues that should be fixed before");
      lines.push("  you use this. See the specific issues and remediation steps below.");
      break;
  }
  lines.push("");

  // Show critical/high findings in plain English; show medium if few and no critical/high
  const showFindings = [...critical, ...high];
  if (showFindings.length === 0 && medium.length > 0 && medium.length <= 3) {
    showFindings.push(...medium);
  }

  if (showFindings.length > 0) {
    const explained = showFindings.filter((f) => RISK_EXPLANATIONS[f.id]);
    if (explained.length > 0) {
      lines.push(`  We found ${explained.length} issue(s) worth knowing about:`);
      lines.push("");
      for (const f of explained) {
        lines.push(`  ${pc.dim("\u2022")} ${RISK_EXPLANATIONS[f.id]!.plain}`);
      }
      const unexplained = showFindings.length - explained.length;
      if (unexplained > 0) {
        lines.push(`  ${pc.dim("\u2022")} Plus ${unexplained} additional finding(s) — see details below.`);
      }
      lines.push("");
    }
  }

  return lines;
}

// ── Finding risk explanations ────────────────────────────────────────────────

const RISK_EXPLANATIONS: Record<string, { technical: string; plain: string }> = {
  "GHA-EXEC-001": {
    technical: "Downloads and executes remote code in a single command. An attacker who compromises the URL can execute arbitrary code on your machine during install.",
    plain: "The install downloads and runs code in one step — if the source is compromised, your machine runs the attacker's code.",
  },
  "GHA-EXEC-002": {
    technical: "Runs code automatically during package install. Malicious packages use this to execute code before you review anything.",
    plain: "Code runs automatically when you install this package — you don't get a chance to review it first.",
  },
  "GHA-EXEC-003": {
    technical: "Allows arbitrary shell commands from string input. If user data reaches this, it's remote code execution.",
    plain: "This code can run any command on your computer from text input — if that input comes from outside, it's a backdoor.",
  },
  "GHA-EXEC-004": {
    technical: "Deserializes untrusted data into executable objects. Attacker-crafted payloads can execute arbitrary code.",
    plain: "This loads external data in a way that could let an attacker slip in code that runs on your machine.",
  },
  "GHA-EXEC-005": {
    technical: "Fetches remote content then executes or loads it as code. If the remote source is compromised, your system is compromised.",
    plain: "This downloads something from the internet and then runs it — if that source gets hacked, so does your system.",
  },
  "GHA-CI-001": {
    technical: "Runs CI workflows with write access on pull requests from forks. Attackers can submit PRs that execute code with your repo's secrets.",
    plain: "Anyone can submit code changes that run with access to your project's secrets — an attacker could steal them.",
  },
  "GHA-CI-002": {
    technical: "GitHub token has broad permissions. A compromised workflow step can push code, delete branches, or access secrets.",
    plain: "The CI system has more access than it needs — if anything goes wrong, it could modify your whole project.",
  },
  "GHA-CI-003": {
    technical: "Actions pinned to tags instead of commit SHAs. If the action repo is compromised, the tag can be moved to malicious code.",
    plain: "CI tools aren't locked to exact versions — a compromised tool could swap in malicious code without you noticing.",
  },
  "GHA-CI-004": {
    technical: "Untrusted user input (PR title, issue body) injected directly into shell commands. Attackers craft input that executes arbitrary commands.",
    plain: "Pull request text gets run as a command in CI — someone could submit a PR with text that steals your project's secrets.",
  },
  "GHA-CI-005": {
    technical: "Self-hosted runners execute untrusted code from forks. The runner's host machine, network, and credentials are exposed.",
    plain: "Your build server runs code from anyone who submits a PR — they could access your server and network.",
  },
  "GHA-SECRETS-001": {
    technical: "Private key material committed to the repository. Anyone with repo access can impersonate the key owner.",
    plain: "A private key is stored in the code — anyone who can see this repo can pretend to be you.",
  },
  "GHA-SECRETS-002": {
    technical: "Environment file with probable secrets committed. Database passwords, API keys, or tokens may be exposed.",
    plain: "A config file that likely contains passwords or API keys was committed — these should never be in code.",
  },
  "GHA-SECRETS-003": {
    technical: "High-entropy string near auth keywords detected. May be a real API key or token — verify manually.",
    plain: "We found a high-entropy string that may be a password or API key. Have a security engineer or AI assistant review the files below to confirm whether it's a real secret or test data.",
  },
  "GHA-SUPPLY-001": {
    technical: "No lockfile means dependency versions aren't pinned. A compromised registry could serve malicious versions.",
    plain: "Dependencies aren't locked to specific versions — a compromised update could slip in automatically.",
  },
  "GHA-SUPPLY-002": {
    technical: "Dependencies use floating version ranges. A malicious version published within range would be installed automatically.",
    plain: "Dependencies accept a range of versions — a malicious update within that range would install without warning.",
  },
  "GHA-SUPPLY-003": {
    technical: "Dependencies sourced from raw git URLs instead of registries. No audit trail or integrity verification.",
    plain: "Some dependencies come directly from git repos instead of package registries — there's no verification they're safe.",
  },
  "GHA-SUPPLY-005": {
    technical: "Binary files without source provenance. Could contain malware that bypasses code review.",
    plain: "There are binary files with no way to verify what's in them — they could contain anything.",
  },
  "GHA-TRUST-001": {
    technical: "No security disclosure policy. Vulnerability reporters have no way to reach maintainers privately.",
    plain: "There's no SECURITY.md — if someone finds a vulnerability, there's no private way to report it.",
  },
  "GHA-TRUST-002": {
    technical: "No code ownership defined. No guarantee that changes to sensitive files are reviewed by qualified maintainers.",
    plain: "No CODEOWNERS file — there's no rule about who must review changes to important files.",
  },
  "GHA-AI-001": {
    technical: "LLM output flows directly to tool execution without validation. A prompt injection could execute arbitrary tools.",
    plain: "AI model output may control what tools run — a prompt injection attack could make the AI do things it shouldn't.",
  },
  "GHA-AI-002": {
    technical: "Secrets or sensitive data included in prompts. LLM providers may log or train on this data.",
    plain: "Sensitive data might be sent to an AI provider — they could log it or use it for training.",
  },
  "GHA-AGENT-001": {
    technical: "Agent has shell, write, and network access without human approval. A misbehaving agent can exfiltrate data or destroy files.",
    plain: "An AI agent can run commands, write files, and access the network without asking permission — if it goes wrong, it could leak or destroy data.",
  },
  "GHA-MCP-001": {
    technical: "MCP server exposes unrestricted shell execution. Any connected client can run arbitrary commands on the host.",
    plain: "This MCP server lets connected tools run any command on the computer — no restrictions.",
  },
  "GHA-MCP-003": {
    technical: "MCP server forwards auth tokens into tool calls. A malicious tool request can capture credentials.",
    plain: "Login credentials get passed to tools automatically — a malicious tool could steal them.",
  },
  "GHA-PLUGIN-002": {
    technical: "Plugin instructions attempt to override the AI's identity or safety boundaries. May be benign (defining a persona) or malicious (bypassing guardrails).",
    plain: "Plugin instructions try to change the AI's behavior — could be a normal persona definition or an attempt to bypass safety rules.",
  },
  "GHA-INFRA-001": {
    technical: "Container runs as root. A container escape gives the attacker root access to the host.",
    plain: "The container runs with full admin privileges — if an attacker breaks out, they own the whole machine.",
  },
  "GHA-INFRA-002": {
    technical: "Container uses :latest tag. Builds are not reproducible and a compromised image affects all future builds.",
    plain: "The container always pulls the latest version — a compromised image would affect everyone automatically.",
  },
  "GHA-INFRA-003": {
    technical: "Kubernetes manifest grants broad RBAC permissions. A compromised pod can access or modify cluster-wide resources.",
    plain: "This gives the app broad access across the entire cluster — if it's compromised, the attacker gets that access too.",
  },
  "GHA-TRUST-003": {
    technical: "Repository appears archived or abandoned. No active maintainer to address security issues.",
    plain: "This project looks abandoned — if a security problem is found, nobody is around to fix it.",
  },
  "GHA-TRUST-004": {
    technical: "No signed tags or releases. Difficult to verify that published artifacts match the source code.",
    plain: "Releases aren't signed — there's no way to prove the code you download is what the author actually published.",
  },
  "GHA-TRUST-005": {
    technical: "Unusual recent change in commit authors. Could indicate a maintainer account takeover.",
    plain: "New contributors appeared recently — this may be normal growth, but sudden maintainer changes can indicate account compromise. Check the project's contributor history.",
  },
  "GHA-SUPPLY-004": {
    technical: "A direct dependency has a known security vulnerability. The vulnerability may be exploitable in your usage.",
    plain: "One of the packages this depends on has a known security hole — it might affect you too.",
  },
  "GHA-WEB-001": {
    technical: "Debug mode enabled in production-like configuration. Exposes stack traces, internal state, and diagnostic endpoints.",
    plain: "Debug mode is on — this shows detailed error messages and internal info that attackers can use.",
  },
  "GHA-WEB-002": {
    technical: "User-controlled content rendered without escaping. Attackers can inject scripts that run in other users' browsers.",
    plain: "User input gets displayed without cleaning it first — an attacker could inject code that runs in your browser.",
  },
  "GHA-API-001": {
    technical: "Sensitive API route has no visible authentication check. Unauthenticated users may access protected resources.",
    plain: "An important API endpoint doesn't check who's calling it — anyone could access data they shouldn't.",
  },
  "GHA-API-002": {
    technical: "CORS allows all origins or credentials with wildcards. Any website can make authenticated requests to this API.",
    plain: "Any website can talk to this API as if it were you — your login cookies get sent along automatically.",
  },
  "GHA-API-003": {
    technical: "Request body bound directly to internal model without validation. Attackers can set fields they shouldn't have access to.",
    plain: "Data from users goes straight into the system without checking — someone could set admin-only fields.",
  },
  "GHA-AI-003": {
    technical: "No rate limiting or budget controls on AI model calls. Runaway usage can generate large unexpected costs.",
    plain: "These files make AI/LLM API calls without visible rate limiting or budget controls. Review the files below to add request limits before production use.",
  },
  "GHA-AGENT-002": {
    technical: "Agent tasks share memory or state without isolation. One task can read or corrupt another task's data.",
    plain: "Different AI tasks share the same memory — one task could accidentally (or intentionally) mess with another's data.",
  },
  "GHA-PLUGIN-001": {
    technical: "Plugin manifest requests broad permissions (e.g., wildcard access). A malicious plugin gets far more access than it needs.",
    plain: "This plugin asks for access to everything — if it turns out to be malicious, it can do a lot of damage.",
  },
  "GHA-MCP-002": {
    technical: "MCP fetch tool can request arbitrary URLs including internal services. Server-side request forgery (SSRF) risk.",
    plain: "This tool can fetch any URL, including internal ones — an attacker could use it to reach systems that should be private.",
  },
  "GHA-PKG-001": {
    technical: "Package runs network requests or spawns processes at import time. Side effects execute before you can inspect behavior.",
    plain: "Just loading this package triggers network calls or runs commands — you don't get a chance to opt in first.",
  },
  "GHA-RUNTIME-001": {
    technical: "Install or build process accesses SSH keys or cloud credential files. Could exfiltrate credentials during routine operations.",
    plain: "During install, this reads your SSH keys or cloud credentials — it could be stealing them.",
  },
  "GHA-RUNTIME-002": {
    technical: "Unexpected outbound network connection to unknown domain during install. May be phoning home or exfiltrating data.",
    plain: "During install, this connects to an unknown server — it might be sending your data somewhere.",
  },
  "GHA-RUNTIME-003": {
    technical: "Runtime observed downloading content then executing it as code. Classic dropper behavior.",
    plain: "This downloads something and then runs it — that's exactly how malware installers work.",
  },
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

  // ── Plain English summary ──
  lines.push(...renderPlainEnglish(result));

  lines.push(hr);

  // ── Scores with bars ──
  lines.push("");
  lines.push(pc.bold("  Risk Scores") + pc.dim("  (0% = safe, 100% = dangerous)"));
  lines.push("");

  const tw = result.scores.trustworthiness;
  const ex = result.scores.exploitability;
  const ap = result.scores.abuse_potential;

  lines.push(
    `  Trustworthiness Risk  ${scoreBar(tw)}  ${scoreColor(tw).padStart(5)}%  ${scoreLabel(tw)}`,
  );
  lines.push(
    pc.dim("                        How well-governed and maintained is the source?"),
  );
  lines.push(
    `  Exploitability Risk   ${scoreBar(ex)}  ${scoreColor(ex).padStart(5)}%  ${scoreLabel(ex)}`,
  );
  lines.push(
    pc.dim("                        How exposed is the attack surface?"),
  );
  lines.push(
    `  Abuse Potential Risk  ${scoreBar(ap)}  ${scoreColor(ap).padStart(5)}%  ${scoreLabel(ap)}`,
  );
  lines.push(
    pc.dim("                        How easily could this be misused in your environment?"),
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

    // Risk explanation — technical + plain English
    const explanation = RISK_EXPLANATIONS[f.id];
    if (explanation) {
      lines.push(`  ${pc.dim("Risk:")}  ${explanation.technical}`);
      lines.push(`  ${pc.dim("    →")}  ${explanation.plain}`);
    }

    // Remediation from the finding
    if (f.remediation) {
      lines.push(`  ${pc.dim("Fix:")}   ${f.remediation}`);
    }

    // Actionable next steps with full file paths
    if (f.files && f.files.length > 0) {
      const label = f.files.length === 1 ? "Review this file" : "Review these files";
      lines.push(`  ${pc.dim("Next:")}  ${label}:`);
      for (const file of f.files.slice(0, 5)) {
        lines.push(`  ${pc.dim("       ")} ${file}`);
      }
      if (f.files.length > 5) {
        lines.push(`  ${pc.dim("       ")} ... and ${f.files.length - 5} more`);
      }
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

  // ── Stage 2 recommendations ──
  if (result.stage2_recommended && result.stage2_triggers && result.stage2_triggers.length > 0) {
    lines.push(hr);
    lines.push("");
    lines.push(pc.bold("  Deeper Analysis Recommended"));
    lines.push(pc.dim("  Static analysis flagged issue(s) with low confidence."));
    lines.push(pc.dim("  A deeper scan could confirm or dismiss these."));
    lines.push("");
    for (const t of result.stage2_triggers) {
      const moduleLabel = t.recommended_module === "ast" ? "Code flow analysis"
        : t.recommended_module === "sandbox" ? "Sandbox execution"
        : "Manual review";
      lines.push(`  ${pc.yellow("\u2192")} ${pc.bold(t.finding_id)}: ${t.reason}`);
      lines.push(`    ${pc.dim("Recommended:")} ${moduleLabel}`);
    }
    lines.push("");
    lines.push(pc.dim("  Future: stop-git-std --deep <repo>"));
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
