import { describe, expect, test } from "bun:test";
import { classifyRepo } from "./classify-repo.ts";
import type { FileInventory, DetectedFramework } from "../models/repo-profile.ts";

function makeInventory(files: string[]): FileInventory {
  return { totalFiles: files.length, byExtension: new Map(), files };
}

describe("classifyRepo", () => {
  test("detects API type from express framework", () => {
    const frameworks: DetectedFramework[] = [{ name: "express", confidence: 0.9 }];
    const types = classifyRepo(makeInventory(["src/index.ts"]), frameworks);
    expect(types).toContain("api");
  });

  test("detects MCP server type from mcp-sdk", () => {
    const frameworks: DetectedFramework[] = [{ name: "mcp-sdk", confidence: 0.95 }];
    const types = classifyRepo(makeInventory(["src/server.ts"]), frameworks);
    expect(types).toContain("mcp-server");
  });

  test("detects AI/LLM type from openai", () => {
    const frameworks: DetectedFramework[] = [{ name: "openai", confidence: 0.9 }];
    const types = classifyRepo(makeInventory(["src/chat.ts"]), frameworks);
    expect(types).toContain("ai-llm");
  });

  test("returns unknown for empty repo", () => {
    const types = classifyRepo(makeInventory([]), []);
    expect(types).toEqual(["unknown"]);
  });

  test("detects infrastructure from terraform", () => {
    const frameworks: DetectedFramework[] = [{ name: "terraform", confidence: 0.7 }];
    const types = classifyRepo(makeInventory(["main.tf"]), frameworks);
    expect(types).toContain("infrastructure-heavy");
  });
});
