import { readdir } from "node:fs/promises";
import { join, extname } from "node:path";
import type { FileInventory } from "../models/repo-profile.ts";

const IGNORED_DIRS = new Set([
  ".git",
  "node_modules",
  ".next",
  ".nuxt",
  "dist",
  "build",
  "out",
  "__pycache__",
  ".venv",
  "venv",
  ".tox",
  "target",
  "vendor",
]);

export async function enumerateFiles(repoPath: string): Promise<FileInventory> {
  const files: string[] = [];
  const byExtension = new Map<string, number>();

  async function walk(dir: string): Promise<void> {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (IGNORED_DIRS.has(entry.name)) continue;
      const fullPath = join(dir, entry.name);
      const relativePath = fullPath.slice(repoPath.length + 1);

      if (entry.isDirectory()) {
        await walk(fullPath);
      } else if (entry.isFile()) {
        files.push(relativePath);
        const ext = extname(entry.name).toLowerCase() || "(no ext)";
        byExtension.set(ext, (byExtension.get(ext) ?? 0) + 1);
      }
    }
  }

  await walk(repoPath);

  return {
    totalFiles: files.length,
    byExtension,
    files,
  };
}
