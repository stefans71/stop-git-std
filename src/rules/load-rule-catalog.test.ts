import { describe, expect, test } from "bun:test";
import { loadRuleCatalog, getRulesForCategory } from "./load-rule-catalog.ts";
import { resolve } from "node:path";

const CATALOG_PATH = resolve(import.meta.dirname ?? ".", "../../docs/rule-catalog.yaml");

describe("loadRuleCatalog", () => {
  test("loads the rule catalog YAML", async () => {
    const catalog = await loadRuleCatalog(CATALOG_PATH);
    expect(catalog.categories.size).toBeGreaterThan(0);
    expect(catalog.categories.has("secrets")).toBe(true);
    expect(catalog.categories.has("ci-cd")).toBe(true);
  });

  test("secrets category has rules with IDs", async () => {
    const catalog = await loadRuleCatalog(CATALOG_PATH);
    const rules = getRulesForCategory(catalog, "secrets");
    expect(rules.length).toBeGreaterThan(0);
    expect(rules[0]?.id).toMatch(/^SEC-/);
  });

  test("getRulesForCategory returns empty for unknown category", async () => {
    const catalog = await loadRuleCatalog(CATALOG_PATH);
    const rules = getRulesForCategory(catalog, "nonexistent");
    expect(rules).toHaveLength(0);
  });
});
