import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Finding, Evidence } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import { getRulesForCategory, type RuleCatalog, type RuleDefinition } from "../../rules/load-rule-catalog.ts";

function shannonEntropy(s: string): number {
  const freq = new Map<string, number>();
  for (const ch of s) {
    freq.set(ch, (freq.get(ch) ?? 0) + 1);
  }
  let entropy = 0;
  for (const count of freq.values()) {
    const p = count / s.length;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

export async function analyzeSecrets(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const rules = getRulesForCategory(catalog, "secrets");
  const findings: Finding[] = [];

  for (const file of profile.inventory.files) {
    // Check file-pattern rules (like .env files)
    for (const rule of rules) {
      if (rule.filePattern && rule.pattern) {
        const regex = new RegExp(rule.pattern);
        if (regex.test(file)) {
          findings.push(createFinding(rule, [{ file, snippet: file }]));
        }
      }
    }

    // Check content-pattern rules
    if (shouldScanFile(file)) {
      const fullPath = join(profile.path, file);
      let content: string;
      try {
        content = await readFile(fullPath, "utf-8");
      } catch {
        continue;
      }

      const lines = content.split("\n");
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]!;
        for (const rule of rules) {
          if (rule.filePattern || !rule.pattern) continue;

          const regex = new RegExp(rule.pattern, "i");
          const match = regex.exec(line);
          if (!match) continue;

          // Entropy check for high-entropy rule
          if (rule.entropyCheck && rule.minEntropy) {
            const entropy = shannonEntropy(match[0]);
            if (entropy < rule.minEntropy) continue;
          }

          findings.push(
            createFinding(rule, [
              { file, line: i + 1, snippet: line.trim().slice(0, 200) },
            ]),
          );
        }
      }
    }
  }

  return findings;
}

function shouldScanFile(file: string): boolean {
  const skipExtensions = new Set([
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".br",
    ".exe", ".dll", ".so", ".dylib",
    ".lock", ".lockb",
  ]);
  const ext = file.slice(file.lastIndexOf(".")).toLowerCase();
  return !skipExtensions.has(ext);
}

function createFinding(rule: RuleDefinition, evidence: Evidence[]): Finding {
  return {
    id: `${rule.id}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    ruleId: rule.id,
    category: "secrets",
    severity: rule.severity,
    title: rule.title,
    description: rule.description,
    evidence,
    remediation: rule.remediation,
    confidence: 0.8,
    tags: ["universal", "secrets"],
  };
}
