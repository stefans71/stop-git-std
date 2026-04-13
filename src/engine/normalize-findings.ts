import type { Finding } from "../models/finding.ts";

export function normalizeFindings(findings: readonly Finding[]): readonly Finding[] {
  // Deduplicate by ruleId + file + line
  const seen = new Set<string>();
  const deduplicated: Finding[] = [];

  for (const finding of findings) {
    const key = dedupeKey(finding);
    if (!seen.has(key)) {
      seen.add(key);
      deduplicated.push(finding);
    }
  }

  // Sort by severity (critical first), then by category
  const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  deduplicated.sort((a, b) => {
    const sevDiff = severityOrder[a.severity] - severityOrder[b.severity];
    if (sevDiff !== 0) return sevDiff;
    return a.category.localeCompare(b.category);
  });

  return deduplicated;
}

function dedupeKey(finding: Finding): string {
  const evidence = finding.evidence[0];
  const location = evidence
    ? `${evidence.file}:${evidence.line ?? ""}:${evidence.snippet?.slice(0, 50) ?? ""}`
    : "";
  return `${finding.ruleId}::${location}`;
}
