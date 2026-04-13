#!/usr/bin/env bun
import { parseArgs } from "node:util";
import { resolve, join } from "node:path";
import type { AuditRequest, OutputFormat } from "./models/audit-request.ts";
import { loadRuleCatalog } from "./rules/load-rule-catalog.ts";
import { runAudit } from "./engine/run-audit.ts";
import { renderTerminal } from "./reporting/terminal.ts";
import { renderMarkdown } from "./reporting/markdown.ts";
import { renderJson } from "./reporting/json.ts";

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    format: { type: "string", short: "f", default: "terminal" },
    output: { type: "string", short: "o" },
    verbose: { type: "boolean", short: "v", default: false },
    "rule-catalog": { type: "string" },
    categories: { type: "string", short: "c" },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
  strict: true,
});

if (values.help || positionals.length === 0) {
  console.log(`
stop-git-std — Git repository safety auditor

Usage:
  stop-git-std <repo-path> [options]

Options:
  -f, --format <format>       Output format: terminal, json, markdown (default: terminal)
  -o, --output <dir>          Output directory for reports
  -v, --verbose               Verbose output
  --rule-catalog <path>       Path to custom rule catalog YAML
  -c, --categories <list>     Comma-separated categories to check
  -h, --help                  Show this help
`);
  process.exit(values.help ? 0 : 1);
}

const target = positionals[0]!;
const formats = (values.format ?? "terminal").split(",") as OutputFormat[];
const catalogPath = values["rule-catalog"] ?? join(import.meta.dirname ?? ".", "../docs/rule-catalog.yaml");
const categories = values.categories?.split(",");

const request: AuditRequest = {
  target,
  repoPath: resolve(target),
  outputFormats: formats,
  outputDir: values.output,
  verbose: values.verbose ?? false,
  ruleCatalogPath: catalogPath,
  categories,
};

try {
  const catalog = await loadRuleCatalog(catalogPath);
  const result = await runAudit(request, catalog);

  for (const format of formats) {
    switch (format) {
      case "terminal":
        console.log(renderTerminal(result));
        break;
      case "json":
        console.log(renderJson(result));
        break;
      case "markdown":
        console.log(renderMarkdown(result));
        break;
    }
  }

  // Exit with non-zero if ABORT
  if (result.decision.verdict === "ABORT") {
    process.exit(2);
  } else if (result.decision.verdict === "CAUTION") {
    process.exit(1);
  }
} catch (error) {
  console.error("Error:", error instanceof Error ? error.message : error);
  process.exit(3);
}
