import { test, expect, describe } from "bun:test";
import { loadEngineContract } from "../rules/load-engine-contract.ts";

describe("loadEngineContract", () => {
  test("loads the real docs/engine-contract.yaml successfully", () => {
    const contract = loadEngineContract();
    expect(contract).toBeDefined();
  });

  test("returns object with required top-level keys", () => {
    const contract = loadEngineContract();
    expect(contract).toHaveProperty("version");
    expect(contract).toHaveProperty("name");
    expect(contract).toHaveProperty("phase_order");
    expect(contract).toHaveProperty("module_routing");
    expect(contract).toHaveProperty("policy_profiles");
  });

  test("has expected version and name types", () => {
    const contract = loadEngineContract();
    expect(typeof contract.version).toBe("number");
    expect(typeof contract.name).toBe("string");
    expect(contract.name.length).toBeGreaterThan(0);
  });

  test("phase_order is a non-empty array of strings", () => {
    const contract = loadEngineContract();
    expect(Array.isArray(contract.phase_order)).toBe(true);
    expect(contract.phase_order.length).toBeGreaterThan(0);
    for (const phase of contract.phase_order) {
      expect(typeof phase).toBe("string");
    }
  });

  test("module_routing has universal_modules", () => {
    const contract = loadEngineContract();
    expect(contract.module_routing).toHaveProperty("universal_modules");
    expect(Array.isArray(contract.module_routing.universal_modules)).toBe(true);
    expect(contract.module_routing.universal_modules.length).toBeGreaterThan(0);
  });

  test("module_routing has category_routes", () => {
    const contract = loadEngineContract();
    expect(contract.module_routing).toHaveProperty("category_routes");
    expect(typeof contract.module_routing.category_routes).toBe("object");
  });

  test("policy_profiles has strict profile", () => {
    const contract = loadEngineContract();
    expect(contract.policy_profiles).toHaveProperty("strict");
  });

  test("policy_profiles has balanced profile", () => {
    const contract = loadEngineContract();
    expect(contract.policy_profiles).toHaveProperty("balanced");
  });

  test("policy_profiles has advisory profile", () => {
    const contract = loadEngineContract();
    expect(contract.policy_profiles).toHaveProperty("advisory");
  });

  test("each policy profile has hard_stop_behavior and thresholds", () => {
    const contract = loadEngineContract();
    for (const [name, profile] of Object.entries(contract.policy_profiles)) {
      expect(profile, `profile ${name} missing hard_stop_behavior`).toHaveProperty("hard_stop_behavior");
      expect(profile, `profile ${name} missing thresholds`).toHaveProperty("thresholds");
      expect(profile.thresholds, `profile ${name} missing abort threshold`).toHaveProperty("abort");
      expect(profile.thresholds, `profile ${name} missing caution threshold`).toHaveProperty("caution");
    }
  });

  test("universal_modules includes core governance modules", () => {
    const contract = loadEngineContract();
    const universals = contract.module_routing.universal_modules;
    expect(universals).toContain("governance_trust");
    expect(universals).toContain("supply_chain");
    expect(universals).toContain("secrets");
  });

  test("throws on invalid path", () => {
    expect(() => loadEngineContract("/nonexistent/path/engine-contract.yaml")).toThrow();
  });
});
