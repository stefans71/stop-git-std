import { readdirSync } from "fs";
import { join } from "path";
import { emitFinding, scanFileContent, shouldSkipInTypedAnalyzer, classifyFile } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

function walkFiles(dir: string): string[] {
  const results: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "node_modules" || entry.name === ".git") continue;
      results.push(...walkFiles(full));
    } else {
      results.push(full);
    }
  }
  return results;
}

export const mcpServerAnalyzer: AnalyzerModule = {
  name: "mcp_server",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];

    let allFiles: string[] = [];
    try {
      allFiles = walkFiles(workspace.rootPath);
    } catch {
      // workspace not accessible
    }
    const scanFiles = allFiles.filter((f) => !shouldSkipInTypedAnalyzer(f));

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-MCP-001": {
          const regex = /mcp.*server|server.*mcp|McpServer|createServer.*mcp/i;
          const authRegex = /auth|token|bearer|apiKey|api_key/i;
          const matchedFiles: string[] = [];

          const filesWithMcp = new Set<string>();
          const filesWithAuth = new Set<string>();

          for (const f of scanFiles) {
            if (scanFileContent(f, regex).length > 0) filesWithMcp.add(f);
            if (scanFileContent(f, authRegex).length > 0) filesWithAuth.add(f);
          }

          const unprotected = [...filesWithMcp].filter((f) => !filesWithAuth.has(f));
          for (const f of unprotected) {
            matchedFiles.push(f);
          }

          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "heuristic",
                records: matchedFiles.map((f) => ({
                  file: f,
                  pattern: "MCP server without visible auth",
                })),
              },
              matchedFiles,
            );
            const hasCodeMatch = matchedFiles.some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
          break;
        }

        case "GHA-MCP-002": {
          const regex = /tools?\s*:\s*\[\s*['"`]\*['"`]|allowAllTools|all_tools\s*:\s*true/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of scanFiles) {
            const matches = scanFileContent(f, regex);
            for (const m of matches) {
              matchedFiles.push(m.path);
              lineNumbers.push(m.lineNumber);
            }
          }

          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "regex_match",
                records: matchedFiles.map((f, i) => ({
                  file: f,
                  line: lineNumbers[i],
                  pattern: "broad tool permission in MCP server",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            const hasCodeMatch = [...new Set(matchedFiles)].some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
          break;
        }

        case "GHA-MCP-003": {
          const regex = /ignore previous|override.*instruction|you are now|disregard.*system/i;
          const matchedFiles: string[] = [];
          const lineNumbers: number[] = [];

          for (const f of scanFiles) {
            const matches = scanFileContent(f, regex);
            for (const m of matches) {
              matchedFiles.push(m.path);
              lineNumbers.push(m.lineNumber);
            }
          }

          if (matchedFiles.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "regex_match",
                records: matchedFiles.map((f, i) => ({
                  file: f,
                  line: lineNumbers[i],
                  pattern: "prompt injection in MCP tool descriptor",
                })),
              },
              [...new Set(matchedFiles)],
              lineNumbers,
            );
            const hasCodeMatch = [...new Set(matchedFiles)].some((f) => classifyFile(f) === "code");
            finding.confidence = hasCodeMatch ? rule.default_confidence : "low";
            findings.push(finding);
          }
          break;
        }

        default:
          break;
      }
    }

    return {
      findings,
      moduleResult: {
        module_name: "mcp_server",
        status: "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
        warnings: [],
        errors: [],
        coverage: {
          files_scanned: scanFiles.length,
        },
      },
    };
  },
};
