import { readFileSync } from "fs";
import { parse as parseYaml } from "yaml";
import { RuleCatalogSchema, type RuleCatalog } from "./types.ts";

export function loadRuleCatalog(path?: string): RuleCatalog {
  const resolvedPath = path ?? new URL("../../docs/rule-catalog.yaml", import.meta.url).pathname;
  const text = readFileSync(resolvedPath, "utf-8");
  const parsed = parseYaml(text);
  return RuleCatalogSchema.parse(parsed);
}
