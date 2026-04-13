import { describe, expect, test } from "bun:test";
import { activateModules } from "./router.ts";
import type { RepoProfile } from "../models/repo-profile.ts";

function makeProfile(types: RepoProfile["types"]): RepoProfile {
  return {
    path: "/test",
    name: "test",
    types,
    frameworks: [],
    inventory: { totalFiles: 0, byExtension: new Map(), files: [] },
    languages: [],
    hasLockfile: true,
    hasCiConfig: false,
    hasDockerfile: false,
    hasK8sConfig: false,
  };
}

describe("activateModules", () => {
  test("always includes universal categories", () => {
    const modules = activateModules(makeProfile(["unknown"]));
    expect(modules.universal).toHaveLength(6);
    expect(modules.universal).toContain("secrets");
    expect(modules.universal).toContain("ci-cd");
  });

  test("activates typed categories based on repo types", () => {
    const modules = activateModules(makeProfile(["api", "mcp-server"]));
    expect(modules.typed).toContain("api");
    expect(modules.typed).toContain("mcp-server");
    expect(modules.typed).not.toContain("ai-llm");
  });

  test("returns empty typed for unknown repo", () => {
    const modules = activateModules(makeProfile(["unknown"]));
    expect(modules.typed).toHaveLength(0);
  });
});
