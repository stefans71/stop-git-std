import { test, expect, describe } from "bun:test";
import { loadRuleCatalog } from "../rules/load-rule-catalog.ts";

describe("loadRuleCatalog", () => {
  test("loads the real docs/rule-catalog.yaml successfully", () => {
    const catalog = loadRuleCatalog();
    expect(catalog).toBeDefined();
  });

  test("returns object with required top-level keys", () => {
    const catalog = loadRuleCatalog();
    expect(catalog).toHaveProperty("version");
    expect(catalog).toHaveProperty("name");
    expect(catalog).toHaveProperty("modules");
    expect(catalog).toHaveProperty("scoring_defaults");
    expect(catalog).toHaveProperty("policy_baselines");
  });

  test("has expected version and name values", () => {
    const catalog = loadRuleCatalog();
    expect(typeof catalog.version).toBe("number");
    expect(typeof catalog.name).toBe("string");
    expect(catalog.name.length).toBeGreaterThan(0);
  });

  test("modules contains governance_trust key", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.modules).toHaveProperty("governance_trust");
  });

  test("modules contains supply_chain key", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.modules).toHaveProperty("supply_chain");
  });

  test("modules contains secrets key", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.modules).toHaveProperty("secrets");
  });

  test("modules contains dangerous_execution key", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.modules).toHaveProperty("dangerous_execution");
  });

  test("modules contains ci_cd key", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.modules).toHaveProperty("ci_cd");
  });

  test("modules contains infrastructure key", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.modules).toHaveProperty("infrastructure");
  });

  test("each module has a description and rules array", () => {
    const catalog = loadRuleCatalog();
    for (const [name, mod] of Object.entries(catalog.modules)) {
      expect(mod, `module ${name} missing description`).toHaveProperty("description");
      expect(Array.isArray(mod.rules), `module ${name} rules should be array`).toBe(true);
    }
  });

  test("scoring_defaults has severity_weights", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.scoring_defaults).toHaveProperty("severity_weights");
  });

  test("policy_baselines has hard_stop_patterns", () => {
    const catalog = loadRuleCatalog();
    expect(catalog.policy_baselines).toHaveProperty("hard_stop_patterns");
    expect(Array.isArray(catalog.policy_baselines.hard_stop_patterns)).toBe(true);
  });

  test("throws on invalid path", () => {
    expect(() => loadRuleCatalog("/nonexistent/path/rule-catalog.yaml")).toThrow();
  });
});
