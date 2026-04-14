import { test, expect, describe } from "bun:test";
import { getGrammarName, getParserForFile } from "../stage2/language-map.ts";

describe("getGrammarName", () => {
  test("maps TypeScript extensions", () => {
    expect(getGrammarName("foo.ts")).toBe("typescript");
    expect(getGrammarName("bar.tsx")).toBe("typescript");
  });

  test("maps JavaScript extensions", () => {
    expect(getGrammarName("foo.js")).toBe("javascript");
    expect(getGrammarName("bar.jsx")).toBe("javascript");
    expect(getGrammarName("baz.mjs")).toBe("javascript");
    expect(getGrammarName("qux.cjs")).toBe("javascript");
  });

  test("maps Python extension", () => {
    expect(getGrammarName("script.py")).toBe("python");
  });

  test("maps Rust extension", () => {
    expect(getGrammarName("lib.rs")).toBe("rust");
  });

  test("maps Go extension", () => {
    expect(getGrammarName("main.go")).toBe("go");
  });

  test("maps C# extension", () => {
    expect(getGrammarName("Program.cs")).toBe("c_sharp");
  });

  test("returns null for unsupported extensions", () => {
    expect(getGrammarName("file.java")).toBeNull();
    expect(getGrammarName("file.rb")).toBeNull();
    expect(getGrammarName("file.cpp")).toBeNull();
  });

  test("returns null for files with no extension", () => {
    expect(getGrammarName("Makefile")).toBeNull();
  });

  test("handles uppercase extensions via toLowerCase", () => {
    expect(getGrammarName("file.TS")).toBe("typescript");
    expect(getGrammarName("file.PY")).toBe("python");
  });

  test("handles double extensions (uses last segment)", () => {
    expect(getGrammarName("file.test.ts")).toBe("typescript");
    expect(getGrammarName("file.spec.js")).toBe("javascript");
  });
});

describe("getParserForFile", () => {
  test("returns a parser for supported file types", async () => {
    const parser = await getParserForFile("test.ts");
    expect(parser).not.toBeNull();
    parser!.delete();
  });

  test("returns null for unsupported file types", async () => {
    const parser = await getParserForFile("test.java");
    expect(parser).toBeNull();
  });
});
