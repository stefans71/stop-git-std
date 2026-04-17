import { test, expect, describe } from "bun:test";
import { detectLanguages, detectCategories, classifyRepo } from "../inventory/classify-repo.ts";
import type { FileInventory } from "../inventory/enumerate-files.ts";

const makeInventory = (files: Array<{ relativePath: string; extension: string }>, extensionCounts?: Record<string, number>): FileInventory => {
  const fileEntries = files.map((f) => ({
    path: `/tmp/test/${f.relativePath}`,
    relativePath: f.relativePath,
    extension: f.extension,
    sizeBytes: 100,
  }));
  const counts: Record<string, number> = extensionCounts ?? {};
  if (!extensionCounts) {
    for (const f of fileEntries) {
      const ext = f.extension || "(none)";
      counts[ext] = (counts[ext] ?? 0) + 1;
    }
  }
  return {
    files: fileEntries,
    totalFiles: fileEntries.length,
    scannedFiles: fileEntries.length,
    skippedFiles: 0,
    extensionCounts: counts,
  };
};

describe("detectLanguages", () => {
  test("maps TypeScript extensions to TypeScript language", () => {
    const langs = detectLanguages({ ".ts": 10, ".tsx": 3 });
    expect(langs).toContain("TypeScript");
  });

  test("maps Python extensions to Python language", () => {
    const langs = detectLanguages({ ".py": 5 });
    expect(langs).toContain("Python");
  });

  test("returns languages sorted by descending file count", () => {
    const langs = detectLanguages({ ".py": 20, ".ts": 5, ".go": 1 });
    expect(langs[0]).toBe("Python");
    expect(langs[1]).toBe("TypeScript");
    expect(langs[2]).toBe("Go");
  });

  test("merges .ts and .tsx into single TypeScript entry", () => {
    const langs = detectLanguages({ ".ts": 5, ".tsx": 5, ".py": 3 });
    // TypeScript has combined count of 10, Python has 3 — TypeScript should be first
    expect(langs[0]).toBe("TypeScript");
    // TypeScript should appear only once
    expect(langs.filter((l) => l === "TypeScript").length).toBe(1);
  });

  test("ignores unknown extensions", () => {
    const langs = detectLanguages({ ".xyz": 100, ".ts": 1 });
    expect(langs).not.toContain(undefined);
    expect(langs.length).toBe(1);
    expect(langs[0]).toBe("TypeScript");
  });

  test("returns empty array for empty extension counts", () => {
    const langs = detectLanguages({});
    expect(langs).toEqual([]);
  });
});

describe("detectCategories", () => {
  test("classifies web_app from nextjs framework", () => {
    const inventory = makeInventory([
      { relativePath: "package.json", extension: ".json" },
    ]);
    const cats = detectCategories(inventory, ["nextjs"], ["TypeScript"]);
    expect(cats).toContain("web_app");
  });

  test("classifies api from routes/ directory", () => {
    const inventory = makeInventory([
      { relativePath: "routes/users.ts", extension: ".ts" },
      { relativePath: "package.json", extension: ".json" },
    ]);
    const cats = detectCategories(inventory, [], ["TypeScript"]);
    expect(cats).toContain("api");
  });

  test("classifies api from controllers/ directory", () => {
    const inventory = makeInventory([
      { relativePath: "controllers/auth.ts", extension: ".ts" },
    ]);
    const cats = detectCategories(inventory, [], ["TypeScript"]);
    expect(cats).toContain("api");
  });

  test("classifies api from express framework", () => {
    const inventory = makeInventory([
      { relativePath: "index.ts", extension: ".ts" },
    ]);
    const cats = detectCategories(inventory, ["express"], ["TypeScript"]);
    expect(cats).toContain("api");
  });

  test("classifies library_package from package.json", () => {
    const inventory = makeInventory([
      { relativePath: "package.json", extension: ".json" },
      { relativePath: "src/index.ts", extension: ".ts" },
    ]);
    const cats = detectCategories(inventory, [], ["TypeScript"]);
    expect(cats).toContain("library_package");
  });

  test("classifies library_package from Cargo.toml", () => {
    const inventory = makeInventory([
      { relativePath: "Cargo.toml", extension: ".toml" },
      { relativePath: "src/lib.rs", extension: ".rs" },
    ]);
    const cats = detectCategories(inventory, [], ["Rust"]);
    expect(cats).toContain("library_package");
  });

  test("classifies library_package from pyproject.toml", () => {
    const inventory = makeInventory([
      { relativePath: "pyproject.toml", extension: ".toml" },
      { relativePath: "src/main.py", extension: ".py" },
    ]);
    const cats = detectCategories(inventory, [], ["Python"]);
    expect(cats).toContain("library_package");
  });

  test("classifies infrastructure from Dockerfile", () => {
    const inventory = makeInventory([
      { relativePath: "Dockerfile", extension: "" },
    ]);
    const cats = detectCategories(inventory, [], []);
    expect(cats).toContain("infrastructure");
  });

  test("classifies infrastructure from terraform files", () => {
    const inventory = makeInventory([
      { relativePath: "infra/main.terraform", extension: ".terraform" },
    ]);
    const cats = detectCategories(inventory, [], []);
    expect(cats).toContain("infrastructure");
  });

  test("classifies ci_cd from .github/workflows/ files", () => {
    const inventory = makeInventory([
      { relativePath: ".github/workflows/ci.yml", extension: ".yml" },
    ]);
    const cats = detectCategories(inventory, [], []);
    expect(cats).toContain("ci_cd");
  });

  test("classifies mcp_server from matching files", () => {
    const inventory = makeInventory([
      { relativePath: "mcp-server/index.ts", extension: ".ts" },
      { relativePath: "server/config.ts", extension: ".ts" },
    ]);
    const cats = detectCategories(inventory, [], ["TypeScript"]);
    expect(cats).toContain("mcp_server");
  });

  test("defaults to library_package when no category detected", () => {
    const inventory = makeInventory([
      { relativePath: "README.md", extension: ".md" },
    ]);
    const cats = detectCategories(inventory, [], []);
    expect(cats).toContain("library_package");
  });

  test("can classify multiple categories at once", () => {
    const inventory = makeInventory([
      { relativePath: "package.json", extension: ".json" },
      { relativePath: ".github/workflows/ci.yml", extension: ".yml" },
      { relativePath: "Dockerfile", extension: "" },
    ]);
    const cats = detectCategories(inventory, ["nextjs"], ["TypeScript"]);
    expect(cats).toContain("web_app");
    expect(cats).toContain("library_package");
    expect(cats).toContain("ci_cd");
    expect(cats).toContain("infrastructure");
  });
});

describe("classifyRepo", () => {
  const mockInventory: FileInventory = {
    files: [
      { path: "/tmp/test/package.json", relativePath: "package.json", extension: ".json", sizeBytes: 100 },
      { path: "/tmp/test/src/index.ts", relativePath: "src/index.ts", extension: ".ts", sizeBytes: 200 },
    ],
    totalFiles: 2,
    scannedFiles: 2,
    skippedFiles: 0,
    extensionCounts: { ".json": 1, ".ts": 1 },
  };

  const mockWorkspace = {
    rootPath: "/tmp/test",
    isLocal: true,
    gitMetadata: {
      lastCommitDate: "2024-01-01T00:00:00Z",
      contributors: ["dev@example.com"],
      tags: [],
      signedTags: [],
    },
  };

  test("returns a RepoProfile object", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(profile).toBeDefined();
    expect(typeof profile).toBe("object");
  });

  test("includes languages array", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(Array.isArray(profile.languages)).toBe(true);
    expect(profile.languages).toContain("TypeScript");
  });

  test("includes detected_categories array with library_package", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(Array.isArray(profile.detected_categories)).toBe(true);
    expect(profile.detected_categories).toContain("library_package");
  });

  test("includes frameworks array", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(Array.isArray(profile.frameworks)).toBe(true);
  });

  test("includes artifacts with correct shape", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(profile.artifacts).toHaveProperty("manifests");
    expect(profile.artifacts).toHaveProperty("workflows");
    expect(profile.artifacts).toHaveProperty("containers");
    expect(profile.artifacts).toHaveProperty("infra");
    expect(profile.artifacts).toHaveProperty("binaries");
  });

  test("detects package.json as a manifest", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(profile.artifacts.manifests).toContain("package.json");
  });

  test("has signed_tags_count of 0 when no signed tags", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(profile.signed_tags_count).toBe(0);
  });

  test("has pinned_actions_ratio of 0 when no workflows", () => {
    const profile = classifyRepo(mockInventory, mockWorkspace);
    expect(profile.pinned_actions_ratio).toBe(0);
  });
});
