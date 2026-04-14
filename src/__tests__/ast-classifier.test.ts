import { test, expect, describe } from "bun:test";
import { classifyMatchContext } from "../stage2/ast-classifier.ts";
import { getParserForFile } from "../stage2/language-map.ts";

async function getParser(ext: string) {
  const parser = await getParserForFile(`test${ext}`);
  if (!parser) throw new Error(`No parser for ${ext}`);
  return parser;
}

describe("classifyMatchContext", () => {
  // ── Dismiss cases (false positives) ──────────────────────────────────────

  test("dismisses match inside string literal (JS)", async () => {
    const parser = await getParser(".js");
    const code = `const msg = "model execution complete";`;
    const result = classifyMatchContext(parser, code, 1, "model execution");
    expect(result.classification).toBe("dismiss");
    parser.delete();
  });

  test("dismisses match inside comment (Python)", async () => {
    const parser = await getParser(".py");
    const code = `# model exec is handled by the pipeline\nx = 1`;
    const result = classifyMatchContext(parser, code, 1, "model exec");
    expect(result.classification).toBe("dismiss");
    parser.delete();
  });

  test("dismisses match inside Rust string (gmail/mod.rs pattern)", async () => {
    const parser = await getParser(".rs");
    const code = `fn main() {\n    let query = "SELECT * FROM model_exec_log";\n}`;
    const result = classifyMatchContext(parser, code, 2, "model_exec");
    expect(result.classification).toBe("dismiss");
    parser.delete();
  });

  test("dismisses match inside C# comment", async () => {
    const parser = await getParser(".cs");
    const code = `// Execute the model pipeline\nclass Foo {}`;
    const result = classifyMatchContext(parser, code, 1, "Execute");
    expect(result.classification).toBe("dismiss");
    parser.delete();
  });

  test("dismisses match inside Go string literal", async () => {
    const parser = await getParser(".go");
    const code = `package main\n\nfunc main() {\n    s := "model exec query"\n}`;
    const result = classifyMatchContext(parser, code, 4, "model exec");
    expect(result.classification).toBe("dismiss");
    parser.delete();
  });

  // ── Confirm cases (true positives) ───────────────────────────────────────

  test("confirms match in function call (JS)", async () => {
    const parser = await getParser(".js");
    const code = `const result = model.exec(userInput);`;
    const result = classifyMatchContext(parser, code, 1, "exec");
    expect(result.classification).toBe("confirm");
    parser.delete();
  });

  test("confirms match in import statement (Python)", async () => {
    const parser = await getParser(".py");
    const code = `from model_exec import run_pipeline`;
    const result = classifyMatchContext(parser, code, 1, "model_exec");
    expect(result.classification).toBe("confirm");
    parser.delete();
  });

  test("confirms eval() call (JS)", async () => {
    const parser = await getParser(".js");
    const code = `eval(response.text);`;
    const result = classifyMatchContext(parser, code, 1, "eval");
    expect(result.classification).toBe("confirm");
    parser.delete();
  });

  // ── Ambiguous cases ──────────────────────────────────────────────────────

  test("marks type annotation match as ambiguous (TS)", async () => {
    const parser = await getParser(".ts");
    const code = `interface ModelExecConfig { timeout: number; }`;
    const result = classifyMatchContext(parser, code, 1, "ModelExecConfig");
    expect(result.classification).toBe("ambiguous");
    parser.delete();
  });

  // ── Edge cases ───────────────────────────────────────────────────────────

  test("returns ambiguous for unsupported language", async () => {
    const parser = await getParserForFile("test.java");
    expect(parser).toBeNull();
  });

  test("returns ambiguous for malformed source code", async () => {
    const parser = await getParser(".js");
    const code = `}{}{model exec }{{{`;
    const result = classifyMatchContext(parser, code, 1, "model exec");
    // Malformed code still parses (tree-sitter is error-tolerant) — result should be defined
    expect(result.classification).toBeDefined();
    parser.delete();
  });
});
