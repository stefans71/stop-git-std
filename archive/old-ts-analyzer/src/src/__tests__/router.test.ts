import { test, expect, describe } from "bun:test";
import { routeModules } from "../engine/router.ts";
import type { RepoProfile } from "../models/repo-profile.ts";

const mockContract = {
  module_routing: {
    universal_modules: ["governance_trust", "supply_chain", "secrets", "dangerous_execution", "ci_cd", "infrastructure"],
    category_routes: {
      web_app: ["web"],
      api: ["api"],
      ai_llm: ["ai_llm"],
      mcp_server: ["mcp_server"],
      library_package: ["library_package"],
    },
  },
} as any;

const makeProfile = (detected_categories: string[]): RepoProfile => ({
  languages: ["TypeScript"],
  frameworks: [],
  ecosystems: [],
  detected_categories: detected_categories as any,
  artifacts: { manifests: [], workflows: [], containers: [], infra: [], binaries: [] },
  high_risk_files: [],
  signed_tags_count: 0,
  pinned_actions_ratio: 0,
});

describe("routeModules", () => {
  test("always includes all universal modules", () => {
    const profile = makeProfile(["library_package"]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.universal).toContain("governance_trust");
    expect(result.universal).toContain("supply_chain");
    expect(result.universal).toContain("secrets");
    expect(result.universal).toContain("dangerous_execution");
    expect(result.universal).toContain("ci_cd");
    expect(result.universal).toContain("infrastructure");
  });

  test("includes typed module for web_app category", () => {
    const profile = makeProfile(["web_app"]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.typed).toContain("web");
  });

  test("includes typed module for api category", () => {
    const profile = makeProfile(["api"]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.typed).toContain("api");
  });

  test("includes typed module for ai_llm category", () => {
    const profile = makeProfile(["ai_llm"]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.typed).toContain("ai_llm");
  });

  test("includes typed module for mcp_server category", () => {
    const profile = makeProfile(["mcp_server"]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.typed).toContain("mcp_server");
  });

  test("includes typed module for library_package category", () => {
    const profile = makeProfile(["library_package"]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.typed).toContain("library_package");
  });

  test("combines modules from multiple categories", () => {
    const profile = makeProfile(["web_app", "api"]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.typed).toContain("web");
    expect(result.typed).toContain("api");
  });

  test("all array contains both universal and typed modules", () => {
    const profile = makeProfile(["web_app"]);
    const result = routeModules(profile, mockContract, [], []);
    for (const mod of result.universal) {
      expect(result.all).toContain(mod);
    }
    for (const mod of result.typed) {
      expect(result.all).toContain(mod);
    }
    expect(result.all.length).toBe(result.universal.length + result.typed.length);
  });

  test("enabled override adds extra module to typed", () => {
    const profile = makeProfile(["library_package"]);
    const result = routeModules(profile, mockContract, ["extra_module"], []);
    expect(result.typed).toContain("extra_module");
    expect(result.all).toContain("extra_module");
  });

  test("enabled override does not duplicate universal module", () => {
    const profile = makeProfile(["library_package"]);
    const result = routeModules(profile, mockContract, ["governance_trust"], []);
    // governance_trust is already universal, should not appear in typed
    expect(result.universal).toContain("governance_trust");
    expect(result.typed).not.toContain("governance_trust");
    // Should appear exactly once in all
    const occurrences = result.all.filter((m) => m === "governance_trust").length;
    expect(occurrences).toBe(1);
  });

  test("disabled override removes module from universal", () => {
    const profile = makeProfile(["library_package"]);
    const result = routeModules(profile, mockContract, [], ["infrastructure"]);
    expect(result.universal).not.toContain("infrastructure");
    expect(result.all).not.toContain("infrastructure");
  });

  test("disabled override removes module from typed", () => {
    const profile = makeProfile(["web_app"]);
    const result = routeModules(profile, mockContract, [], ["web"]);
    expect(result.typed).not.toContain("web");
    expect(result.all).not.toContain("web");
  });

  test("disabled override can remove multiple modules", () => {
    const profile = makeProfile(["web_app", "api"]);
    const result = routeModules(profile, mockContract, [], ["web", "secrets"]);
    expect(result.all).not.toContain("web");
    expect(result.all).not.toContain("secrets");
    // Other universal modules still present
    expect(result.all).toContain("governance_trust");
  });

  test("unknown category in profile produces no typed modules from that category", () => {
    const profile = makeProfile(["unknown_category" as any]);
    const result = routeModules(profile, mockContract, [], []);
    // Universal modules still present; no typed from unknown category
    expect(result.universal.length).toBe(6);
    expect(result.typed.length).toBe(0);
  });

  test("returns empty typed array when no categories and no overrides", () => {
    const profile = makeProfile([]);
    const result = routeModules(profile, mockContract, [], []);
    expect(result.typed).toEqual([]);
    expect(result.universal.length).toBe(6);
  });
});
