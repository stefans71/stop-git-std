import type { Finding } from "../models/finding.ts";
import type { AnalyzerBackend, AnalyzerInput } from "./analyzer-backend.ts";
import { searchFileContent } from "../parsers/ts-ast.ts";
import { join } from "node:path";

export function createBuiltinTsBackend(): AnalyzerBackend {
  return {
    name: "builtin-ts",
    type: "builtin-ts",

    async analyze(input: AnalyzerInput): Promise<readonly Finding[]> {
      const findings: Finding[] = [];

      for (const rule of input.rules) {
        if (!rule.pattern) continue;

        const regex = new RegExp(rule.pattern, "i");
        const targetFiles = rule.fileGlob
          ? input.files.filter((f) => f.endsWith(rule.fileGlob!.replace("*", "")))
          : input.files;

        for (const file of targetFiles) {
          const fullPath = join(input.profile.path, file);
          const matches = await searchFileContent(fullPath, regex);

          for (const match of matches) {
            findings.push({
              id: `${rule.id}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
              ruleId: rule.id,
              category: "secrets", // Will be overridden by the caller
              severity: rule.severity,
              title: rule.title,
              description: rule.description,
              evidence: [
                {
                  file,
                  line: match.line,
                  snippet: match.snippet.slice(0, 200),
                },
              ],
              remediation: rule.remediation,
              confidence: 0.8,
              tags: ["builtin-ts"],
            });
          }
        }
      }

      return findings;
    },
  };
}
