import type { FileInventory } from "./enumerate-files.ts";

export const FRAMEWORK_MARKERS: Record<string, string> = {
  "next.config.js": "nextjs",
  "next.config.ts": "nextjs",
  "next.config.mjs": "nextjs",
  "nuxt.config.ts": "nuxt",
  "angular.json": "angular",
  "svelte.config.js": "svelte",
  "remix.config.js": "remix",
  "astro.config.mjs": "astro",
  "django-admin.py": "django",
  "manage.py": "django",
  "Cargo.toml": "rust",
  "go.mod": "go",
  "tsconfig.json": "typescript",
};

export const ECOSYSTEM_MARKERS: Record<string, string> = {
  "package.json": "npm",
  "yarn.lock": "yarn",
  "pnpm-lock.yaml": "pnpm",
  "bun.lockb": "bun",
  "requirements.txt": "pip",
  "pyproject.toml": "pip",
  "poetry.lock": "poetry",
  "Cargo.toml": "cargo",
  "go.mod": "gomod",
  "Gemfile": "bundler",
};

export function detectFrameworks(inventory: FileInventory): string[] {
  const frameworks = new Set<string>();
  const fileNames = new Set(inventory.files.map((f) => {
    const parts = f.relativePath.split("/");
    return parts[parts.length - 1]!;
  }));

  for (const [marker, framework] of Object.entries(FRAMEWORK_MARKERS)) {
    if (fileNames.has(marker)) {
      frameworks.add(framework);
    }
  }

  return [...frameworks];
}

export function detectEcosystems(inventory: FileInventory): string[] {
  const ecosystems = new Set<string>();
  const fileNames = new Set(inventory.files.map((f) => {
    const parts = f.relativePath.split("/");
    return parts[parts.length - 1]!;
  }));

  for (const [marker, ecosystem] of Object.entries(ECOSYSTEM_MARKERS)) {
    if (fileNames.has(marker)) {
      ecosystems.add(ecosystem);
    }
  }

  return [...ecosystems];
}
