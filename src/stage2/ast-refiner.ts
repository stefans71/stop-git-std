import { getParserForFile } from "./language-map.ts";
import { classifyMatchContext, type AstClassification } from "./ast-classifier.ts";
import { readFileContent } from "../analyzers/base.ts";
import type { Finding } from "../models/finding.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { DepthMode } from "../models/enums.ts";
import { join, isAbsolute } from "path";

export async function refineFindings(
  findings: Finding[],
  workspace: LocalWorkspace,
  depthMode: DepthMode,
  hardStopPatterns: string[],
  stage2ModuleMap: Record<string, string>,
): Promise<Finding[]> {
  if (depthMode === "quick") return findings;

  const toRefine = findings.filter((f) => {
    if (f.suppressed) return false;
    if (depthMode === "deep") return true;
    // auto mode: only hard-stop findings mapped to "ast"
    return hardStopPatterns.includes(f.id) && stage2ModuleMap[f.id] === "ast";
  });

  if (toRefine.length === 0) return findings;

  for (const finding of toRefine) {
    const files = finding.files;
    const lineNumbers = finding.line_numbers;

    if (!files || files.length === 0) continue;

    const classifications: AstClassification[] = [];

    for (let i = 0; i < files.length; i++) {
      const rawPath = files[i]!;
      const filePath = isAbsolute(rawPath) ? rawPath : join(workspace.rootPath, rawPath);
      const lineNumber = lineNumbers?.[i];
      if (!lineNumber) continue;

      const parser = await getParserForFile(filePath);
      if (!parser) continue; // unsupported language — skip

      const content = readFileContent(filePath);
      if (!content) continue;

      // Extract match text from the corresponding evidence record for this file
      let matchText = "";
      const rec = finding.evidence.records[i] as Record<string, unknown> | undefined;
      if (rec && typeof rec.match === "string") {
        matchText = rec.match;
      }

      try {
        const result = classifyMatchContext(parser, content, lineNumber, matchText);
        classifications.push(result.classification);
      } catch (err) {
        console.warn(`[ast-refiner] Classification failed for ${rawPath}:${lineNumber}: ${err}`);
        classifications.push("ambiguous");
      } finally {
        parser.delete();
      }
    }

    if (classifications.length === 0) continue;

    if (classifications.every((c) => c === "dismiss")) {
      finding.suppressed = true;
      finding.suppression_reason =
        "AST analysis: all matches are in non-executable context (string literals, comments, type names)";
    } else if (classifications.some((c) => c === "confirm")) {
      finding.confidence = "high";
    } else {
      // All ambiguous or mix of dismiss+ambiguous
      finding.confidence = "low";
    }
  }

  return findings;
}
