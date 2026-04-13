import type { AuditResult } from "../models/audit-result.ts";
import type { Finding } from "../models/finding.ts";
import type { Severity } from "../models/enums.ts";

// SARIF 2.1.0 — https://docs.oasis-open.org/sarif/sarif/v2.1.0/

const SARIF_SCHEMA =
  "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json";
const SARIF_VERSION = "2.1.0";
const TOOL_NAME = "stop-git-std";

function toSarifLevel(sev: Severity): "note" | "warning" | "error" {
  switch (sev) {
    case "info":
    case "low":
      return "note";
    case "medium":
      return "warning";
    case "high":
    case "critical":
      return "error";
  }
}

interface SarifRule {
  id: string;
  name: string;
  shortDescription: { text: string };
  fullDescription?: { text: string };
  helpUri?: string;
}

interface SarifResult {
  ruleId: string;
  level: "note" | "warning" | "error";
  message: { text: string };
  locations: Array<{
    physicalLocation: {
      artifactLocation: { uri: string };
      region?: { startLine: number };
    };
  }>;
  properties?: Record<string, unknown>;
}

function buildRules(findings: Finding[]): SarifRule[] {
  const seen = new Map<string, SarifRule>();
  for (const f of findings) {
    if (!seen.has(f.id)) {
      seen.set(f.id, {
        id: f.id,
        name: f.title.replace(/\s+/g, "_"),
        shortDescription: { text: f.title },
        fullDescription: { text: f.remediation },
      });
    }
  }
  return Array.from(seen.values());
}

function buildResults(findings: Finding[]): SarifResult[] {
  const results: SarifResult[] = [];

  for (const f of findings) {
    const files = f.files ?? ["unknown"];
    const primaryFile = files[0] ?? "unknown";

    const firstLine =
      f.line_numbers && f.line_numbers.length > 0 ? f.line_numbers[0] : undefined;
    const location: SarifResult["locations"][number] = {
      physicalLocation: {
        artifactLocation: { uri: primaryFile },
        ...(firstLine !== undefined ? { region: { startLine: firstLine } } : {}),
      },
    };

    results.push({
      ruleId: f.id,
      level: toSarifLevel(f.severity),
      message: {
        text: f.suppressed
          ? `[SUPPRESSED] ${f.title}: ${f.suppression_reason}`
          : f.title,
      },
      locations: [location],
      properties: {
        category: f.category,
        confidence: f.confidence,
        suppressed: f.suppressed,
        axis_impacts: f.axis_impacts,
      },
    });
  }

  return results;
}

export function renderSarifReport(result: AuditResult): string {
  const rules = buildRules(result.findings);
  const sarifResults = buildResults(result.findings);

  const sarif = {
    $schema: SARIF_SCHEMA,
    version: SARIF_VERSION,
    runs: [
      {
        tool: {
          driver: {
            name: TOOL_NAME,
            version: result.manifest.engine_version ?? "0.0.0",
            informationUri: "https://github.com/stop-git-std/stop-git-std",
            rules,
          },
        },
        results: sarifResults,
        properties: {
          decision: result.decision.value,
          scores: result.scores,
          run_id: result.manifest.run_id,
        },
      },
    ],
  };

  return JSON.stringify(sarif, null, 2);
}
