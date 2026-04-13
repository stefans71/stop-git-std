import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

export async function analyzeMcpServer(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "mcp-server");
  const findings: Finding[] = [];

  const sourceFiles = profile.inventory.files.filter(
    (f) => f.endsWith(".ts") || f.endsWith(".js") || f.endsWith(".py"),
  );

  for (const file of sourceFiles) {
    const fullPath = join(profile.path, file);
    let content: string;
    try {
      content = await readFile(fullPath, "utf-8");
    } catch {
      continue;
    }

    const lines = content.split("\n");

    // MCP-001: Unrestricted shell tool
    const shellRule = rules.find((r) => r.id === "MCP-001");
    if (shellRule) {
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        // Detect tool definitions that expose shell execution
        if (
          /tool.*shell|shell.*tool|exec.*tool|command.*tool/i.test(line) ||
          (/name.*["'](shell|exec|run|command)["']/i.test(line) &&
            content.includes("exec") || content.includes("spawn"))
        ) {
          const context = lines.slice(Math.max(0, i - 2), Math.min(lines.length, i + 5)).join("\n");
          const hasRestriction = /allowlist|whitelist|allowed|restrict|validate|sanitize/i.test(context);
          if (!hasRestriction) {
            findings.push(
              createFinding(shellRule, [
                { file, line: i + 1, snippet: line.trim().slice(0, 200) },
              ]),
            );
          }
        }
      }
    }

    // MCP-002: SSRF-capable fetch
    const ssrfRule = rules.find((r) => r.id === "MCP-002");
    if (ssrfRule) {
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        if (/tool.*fetch|fetch.*tool|name.*["']fetch["']/i.test(line)) {
          const context = lines.slice(Math.max(0, i - 2), Math.min(lines.length, i + 10)).join("\n");
          const hasValidation = /validate.*url|url.*validate|allowlist|whitelist|restrict|internal|private/i.test(context);
          if (!hasValidation) {
            findings.push(
              createFinding(ssrfRule, [
                { file, line: i + 1, snippet: line.trim().slice(0, 200) },
              ]),
            );
          }
        }
      }
    }

    // MCP-003: Credential forwarding
    const credRule = rules.find((r) => r.id === "MCP-003");
    if (credRule) {
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        if (
          /process\.env.*tool|tool.*process\.env|credential.*forward|forward.*credential/i.test(line) ||
          (/process\.env/i.test(line) && /token|secret|key|password|credential/i.test(line) &&
            /tool|handler|execute/i.test(content.slice(Math.max(0, content.indexOf(line) - 500), content.indexOf(line) + 500)))
        ) {
          findings.push(
            createFinding(credRule, [
              { file, line: i + 1, snippet: line.trim().slice(0, 200) },
            ]),
          );
        }
      }
    }
  }

  return findings;
}

function createFinding(rule: RuleDefinition, evidence: Evidence[]): Finding {
  return {
    id: `${rule.id}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    ruleId: rule.id,
    category: "mcp-server",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.75,
    tags: ["typed", "mcp-server"],
  };
}
