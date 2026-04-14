import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { refineFindings } from "../stage2/ast-refiner.ts";
import type { Finding } from "../models/finding.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import { writeFileSync, mkdirSync, rmSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";

function makeFinding(overrides: Partial<Finding> = {}): Finding {
  return {
    id: "GHA-AI-001",
    title: "Test finding",
    category: "supply-chain",
    severity: "high",
    confidence: "medium",
    proof_type: "static",
    axis_impacts: { trustworthiness: 0, exploitability: 0, abuse_potential: 0 },
    evidence: { type: "file_match", records: [] },
    remediation: "Fix it",
    suppressed: false,
    suppression_reason: "",
    ...overrides,
  };
}

const HARD_STOP_PATTERNS = ["GHA-AI-001", "GHA-AGENT-001", "GHA-MCP-001", "GHA-MCP-003", "GHA-EXEC-004", "GHA-EXEC-005"];
const STAGE2_MODULE_MAP: Record<string, string> = {
  "GHA-AI-001": "ast",
  "GHA-AGENT-001": "ast",
  "GHA-MCP-001": "ast",
  "GHA-MCP-003": "ast",
  "GHA-EXEC-004": "ast",
  "GHA-EXEC-005": "ast",
};

let tmpDir: string;
let workspace: LocalWorkspace;

beforeAll(() => {
  tmpDir = join(tmpdir(), `ast-refiner-test-${Date.now()}`);
  mkdirSync(tmpDir, { recursive: true });
  workspace = { rootPath: tmpDir } as LocalWorkspace;
});

afterAll(() => {
  rmSync(tmpDir, { recursive: true, force: true });
});

describe("refineFindings", () => {
  test("suppresses finding when all evidence is in string literals", async () => {
    const filePath = join(tmpDir, "test-string.js");
    writeFileSync(filePath, `const msg = "model execution handler";\n`);

    const finding = makeFinding({
      files: [filePath],
      line_numbers: [1],
      evidence: { type: "file_match", records: [{ match: "model execution" }] },
    });

    const result = await refineFindings([finding], workspace, "auto", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    expect(result[0]!.suppressed).toBe(true);
    expect(result[0]!.suppression_reason).toContain("AST analysis");
  });

  test("preserves finding when evidence is in function call", async () => {
    const filePath = join(tmpDir, "test-call.js");
    writeFileSync(filePath, `const result = model.exec(userInput);\n`);

    const finding = makeFinding({
      files: [filePath],
      line_numbers: [1],
      evidence: { type: "file_match", records: [{ match: "exec" }] },
    });

    const result = await refineFindings([finding], workspace, "auto", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    expect(result[0]!.suppressed).toBe(false);
    expect(result[0]!.confidence).toBe("high");
  });

  test("returns findings unchanged when depth_mode is 'quick'", async () => {
    const finding = makeFinding({
      files: [join(tmpDir, "any.js")],
      line_numbers: [1],
    });

    const result = await refineFindings([finding], workspace, "quick", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    expect(result[0]!.confidence).toBe("medium"); // unchanged
    expect(result[0]!.suppressed).toBe(false);
  });

  test("analyzes all findings in 'deep' mode regardless of hard-stop status", async () => {
    const filePath = join(tmpDir, "test-deep.js");
    writeFileSync(filePath, `const x = "some credential string";\n`);

    const finding = makeFinding({
      id: "NON-HARDSTOP-001",
      files: [filePath],
      line_numbers: [1],
      evidence: { type: "file_match", records: [{ match: "credential" }] },
    });

    const result = await refineFindings([finding], workspace, "deep", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    expect(result[0]!.suppressed).toBe(true); // string literal → dismissed even for non-hard-stop
  });

  test("skips files with unsupported extensions", async () => {
    const filePath = join(tmpDir, "test.java");
    writeFileSync(filePath, `public class Exec {}\n`);

    const finding = makeFinding({
      files: [filePath],
      line_numbers: [1],
    });

    const result = await refineFindings([finding], workspace, "auto", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    expect(result[0]!.confidence).toBe("medium"); // unchanged
    expect(result[0]!.suppressed).toBe(false);
  });

  test("handles findings with missing files gracefully", async () => {
    const finding = makeFinding({ files: undefined, line_numbers: undefined });

    const result = await refineFindings([finding], workspace, "auto", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    expect(result[0]!.confidence).toBe("medium"); // unchanged
  });

  test("PowerShell pattern: C# class definition → ambiguous/dismiss", async () => {
    const filePath = join(tmpDir, "CommandModel.cs");
    writeFileSync(filePath, `using System;\n\npublic class CommandModel {\n    /// <summary>Execute the pipeline</summary>\n    public void Execute() { }\n}\n`);

    const finding = makeFinding({
      id: "GHA-EXEC-004",
      files: [filePath],
      line_numbers: [4], // points to comment line
      evidence: { type: "file_match", records: [{ match: "Execute" }] },
    });

    const result = await refineFindings([finding], workspace, "auto", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    // Comment line → dismissed
    expect(result[0]!.suppressed).toBe(true);
  });

  test("Google WS CLI pattern: Rust format string → dismiss", async () => {
    const filePath = join(tmpDir, "mod.rs");
    writeFileSync(filePath, `fn main() {\n    let query = format!("model_exec_query_{}", id);\n}\n`);

    const finding = makeFinding({
      id: "GHA-AI-001",
      files: [filePath],
      line_numbers: [2],
      evidence: { type: "file_match", records: [{ match: "model_exec" }] },
    });

    const result = await refineFindings([finding], workspace, "auto", HARD_STOP_PATTERNS, STAGE2_MODULE_MAP);
    expect(result[0]!.suppressed).toBe(true);
  });
});
