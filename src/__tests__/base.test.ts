import { describe, test, expect } from "bun:test";
import { classifyFile, shouldSkipInTypedAnalyzer } from "../analyzers/base.ts";

describe("classifyFile", () => {
  test("classifies .md as doc", () => {
    expect(classifyFile("README.md")).toBe("doc");
    expect(classifyFile("docs/plan.md")).toBe("doc");
  });

  test("classifies .json/.yaml as config", () => {
    expect(classifyFile("package.json")).toBe("config");
    expect(classifyFile("config.yaml")).toBe("config");
    expect(classifyFile("rules.yml")).toBe("config");
  });

  test("classifies test files as test", () => {
    expect(classifyFile("src/__tests__/policy.test.ts")).toBe("test");
    expect(classifyFile("tests/unit/foo.spec.js")).toBe("test");
  });

  test("classifies .ts/.js/.py as code", () => {
    expect(classifyFile("src/engine/policy.ts")).toBe("code");
    expect(classifyFile("lib/index.js")).toBe("code");
    expect(classifyFile("main.py")).toBe("code");
  });
});

describe("shouldSkipInTypedAnalyzer", () => {
  test("returns true for docs — they are skipped entirely", () => {
    expect(shouldSkipInTypedAnalyzer("README.md")).toBe(true);
    expect(shouldSkipInTypedAnalyzer("docs/plan.txt")).toBe(true);
  });

  test("returns true for tests — they are skipped entirely", () => {
    expect(shouldSkipInTypedAnalyzer("src/__tests__/foo.test.ts")).toBe(true);
    expect(shouldSkipInTypedAnalyzer("tests/unit/bar.spec.js")).toBe(true);
  });

  test("returns false for code files — they are scanned normally", () => {
    expect(shouldSkipInTypedAnalyzer("src/engine/policy.ts")).toBe(false);
  });

  test("returns false for config files — they are scanned with confidence downgrade", () => {
    expect(shouldSkipInTypedAnalyzer("package.json")).toBe(false);
    expect(shouldSkipInTypedAnalyzer("config.yaml")).toBe(false);
    // classifyFile still returns "config" for downstream confidence handling
    expect(classifyFile("package.json")).toBe("config");
  });
});
