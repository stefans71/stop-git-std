import { getParserForFile } from "./language-map.ts";
import { classifyMatchContext, type AstClassification } from "./ast-classifier.ts";
import { readFileContent } from "../analyzers/base.ts";
import type { Finding } from "../models/finding.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { DepthMode } from "../models/enums.ts";
import { join, isAbsolute } from "path";

export interface AstRefinementSkip {
  finding_id: string;
  reason: string;
}

export interface AstRefinementSummary {
  findings_considered: number;
  findings_refined: number;
  findings_skipped: number;
  suppressed_findings: number;
  confirmed_findings: number;
  ambiguous_findings: number;
  error_count: number;
  skips: AstRefinementSkip[];
}

export async function refineFindings(
  findings: Finding[],
  workspace: LocalWorkspace,
  depthMode: DepthMode,
  hardStopPatterns: string[],
  stage2ModuleMap: Record<string, string>,
): Promise<{ findings: Finding[]; summary: AstRefinementSummary }> {
  const summary: AstRefinementSummary = {
    findings_considered: 0,
    findings_refined: 0,
    findings_skipped: 0,
    suppressed_findings: 0,
    confirmed_findings: 0,
    ambiguous_findings: 0,
    error_count: 0,
    skips: [],
  };

  if (depthMode === "quick") return { findings, summary };

  const toRefine = findings.filter((f) => {
    if (f.suppressed) return false;
    if (depthMode === "deep") return true;
    // auto mode: only hard-stop findings mapped to "ast"
    return hardStopPatterns.includes(f.id) && stage2ModuleMap[f.id] === "ast";
  });

  summary.findings_considered = toRefine.length;
  if (toRefine.length === 0) return { findings, summary };

  for (const finding of toRefine) {
    // C5: Guard missing line_numbers
    if (!finding.line_numbers || finding.line_numbers.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "missing line_numbers" });
      continue;
    }

    // C3: Iterate evidence.records instead of parallel arrays
    const records = finding.evidence.records as Array<Record<string, unknown>>;
    if (!records || records.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "no evidence records" });
      continue;
    }

    const classifications: AstClassification[] = [];

    for (const rec of records) {
      const rawPath = typeof rec.path === "string"
        ? rec.path
        : typeof rec.file === "string"
          ? rec.file
          : typeof rec.file_path === "string"
            ? rec.file_path
            : undefined;
      const lineNumber = typeof rec.line_number === "number"
        ? rec.line_number
        : typeof rec.line === "number"
          ? rec.line
          : undefined;
      if (!rawPath || !lineNumber) continue;

      const filePath = isAbsolute(rawPath) ? rawPath : join(workspace.rootPath, rawPath);

      const parser = await getParserForFile(filePath);
      if (!parser) continue; // unsupported language — skip

      const content = readFileContent(filePath);
      if (!content) continue;

      let matchText = "";
      if (typeof rec.match === "string") {
        matchText = rec.match;
      }

      try {
        const result = classifyMatchContext(parser, content, lineNumber, matchText);
        classifications.push(result.classification);
      } catch (err) {
        console.warn(`[ast-refiner] Classification failed for ${rawPath}:${lineNumber}: ${err}`);
        summary.error_count += 1;
        classifications.push("ambiguous");
      } finally {
        parser.delete();
      }
    }

    if (classifications.length === 0) {
      summary.findings_skipped += 1;
      summary.skips.push({ finding_id: finding.id, reason: "no usable evidence records" });
      continue;
    }

    summary.findings_refined += 1;

    // C1: Only all-dismiss suppresses. Confirm/ambiguous preserve original confidence.
    if (classifications.every((c) => c === "dismiss")) {
      finding.suppressed = true;
      finding.suppression_reason =
        "AST analysis: all matches are in non-executable context (string literals, comments, type names)";
      summary.suppressed_findings += 1;
    } else {
      // Preserve original confidence — do NOT mutate
      if (classifications.some((c) => c === "confirm")) summary.confirmed_findings += 1;
      if (classifications.some((c) => c === "ambiguous")) summary.ambiguous_findings += 1;
    }
  }

  console.info(
    `[ast-refiner] Summary: refined ${summary.findings_refined}/${summary.findings_considered}, ` +
      `suppressed ${summary.suppressed_findings}, confirmed ${summary.confirmed_findings}, ` +
      `ambiguous ${summary.ambiguous_findings}, skipped ${summary.findings_skipped}, ` +
      `errors ${summary.error_count}`,
  );

  return { findings, summary };
}
