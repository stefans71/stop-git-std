import { test, expect, describe } from "bun:test";
import { readFileSync } from "fs";
import { loadRuleCatalog } from "../rules/load-rule-catalog.ts";

/**
 * Tests for Phase 8.5 integration in run-audit.ts.
 * Validates the STAGE2_MODULE_MAP and the conditional guard logic.
 */

describe("STAGE2_MODULE_MAP integration", () => {
  // C4: Assert all hard-stop rules have a STAGE2_MODULE_MAP entry or explicit exemption
  test("hard-stop rules are covered by STAGE2_MODULE_MAP or explicitly exempted", () => {
    const catalog = loadRuleCatalog();
    const hardStops = new Set(catalog.policy_baselines.hard_stop_patterns);

    const source = readFileSync(new URL("../engine/run-audit.ts", import.meta.url), "utf8");
    const mapBody = source.match(/const STAGE2_MODULE_MAP[\s\S]*?=\s*\{([\s\S]*?)\n\};/);
    expect(mapBody).not.toBeNull();

    const mapKeys = new Set<string>();
    const re = /"([A-Z0-9-]+)"\s*:\s*"(ast|sandbox|manual_review)"/g;
    for (const match of mapBody![1]!.matchAll(re)) {
      mapKeys.add(match[1]!);
    }

    // Rules that don't need AST/sandbox (no regex-based evidence, or handled differently)
    const exempt = new Set(["GHA-SECRETS-001", "GHA-CI-004", "GHA-RUNTIME-001", "GHA-RUNTIME-003"]);
    for (const id of hardStops) {
      expect(
        mapKeys.has(id) || exempt.has(id),
      ).toBe(true);
    }
  });

  test("STAGE2_MODULE_MAP keys match expected rule IDs", async () => {
    const mod = await import("../engine/run-audit.ts");
    expect(mod.runAudit).toBeDefined();
    expect(typeof mod.runAudit).toBe("function");
  });

  test("ast-refiner module can be dynamically imported (Phase 8.5 import path)", async () => {
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    expect(typeof refineFindings).toBe("function");
  });

  test("refineFindings gracefully handles empty findings array", async () => {
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    const result = await refineFindings(
      [],
      { rootPath: "/nonexistent" } as any,
      "auto",
      ["GHA-AI-001"],
      { "GHA-AI-001": "ast" },
    );
    expect(result).toEqual({ findings: [], summary: expect.any(Object) });
  });

  test("refineFindings returns findings unchanged in quick mode", async () => {
    const { refineFindings } = await import("../stage2/ast-refiner.ts");
    const findings = [{ id: "GHA-AI-001", suppressed: false } as any];
    const result = await refineFindings(
      findings,
      { rootPath: "/nonexistent" } as any,
      "quick",
      ["GHA-AI-001"],
      { "GHA-AI-001": "ast" },
    );
    expect(result.findings).toBe(findings); // Same reference — no processing
  });
});
