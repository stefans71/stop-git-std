import { readFileSync } from "fs";
import type { Finding, Evidence } from "../models/finding.ts";
import type { RuleDefinition } from "../rules/types.ts";
import type { FileInventory } from "../inventory/enumerate-files.ts";

export interface MatchResult {
  path: string;
  lineNumber: number;
  line: string;
  match: string;
}

export function matchFiles(inventory: FileInventory, patterns: string[]): string[] {
  return inventory.files
    .filter((f) =>
      patterns.some((p) => {
        const regexStr = p
          .replace(/\./g, "\\.")
          .replace(/\*\*/g, "___GLOBSTAR___")
          .replace(/\*/g, "[^/]*")
          .replace(/___GLOBSTAR___/g, ".*");
        return new RegExp(regexStr).test(f.relativePath);
      }),
    )
    .map((f) => f.path);
}

export function scanFileContent(filePath: string, regex: RegExp): MatchResult[] {
  const results: MatchResult[] = [];
  const content = readFileContent(filePath);
  if (!content) return results;

  const lines = content.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!;
    const m = line.match(regex);
    if (m) {
      results.push({
        path: filePath,
        lineNumber: i + 1,
        line: line.trim(),
        match: m[0],
      });
    }
  }
  return results;
}

export function readFileContent(filePath: string, maxSize: number = 5242880): string | null {
  try {
    const stat = require("fs").statSync(filePath);
    if (stat.size > maxSize) return null;
    return readFileSync(filePath, "utf-8");
  } catch {
    return null;
  }
}

export function emitFinding(
  rule: RuleDefinition,
  evidence: Evidence,
  files: string[],
  lineNumbers?: number[],
): Finding {
  return {
    id: rule.id,
    title: rule.title,
    category: rule.category,
    subcategory: rule.subcategory,
    severity: rule.default_severity,
    confidence: rule.default_confidence,
    proof_type: rule.proof_type,
    axis_impacts: { ...rule.axis_impacts },
    evidence,
    remediation: rule.remediation,
    files,
    line_numbers: lineNumbers,
    suppressed: false,
    suppression_reason: "",
  };
}
