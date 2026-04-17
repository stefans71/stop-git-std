import { readdirSync, statSync } from "fs";
import { join, relative, extname } from "path";
import type { LocalWorkspace } from "../models/local-workspace.ts";

export interface FileEntry {
  path: string;
  relativePath: string;
  extension: string;
  sizeBytes: number;
}

export interface FileInventory {
  files: FileEntry[];
  totalFiles: number;
  scannedFiles: number;
  skippedFiles: number;
  extensionCounts: Record<string, number>;
}

function matchesGlob(relativePath: string, pattern: string): boolean {
  const regexStr = pattern
    .replace(/\*\*/g, "___GLOBSTAR___")
    .replace(/\*/g, "[^/]*")
    .replace(/___GLOBSTAR___/g, ".*")
    .replace(/\?/g, ".");
  return new RegExp(`^${regexStr}$`).test(relativePath);
}

export async function enumerateFiles(
  workspace: LocalWorkspace,
  excludePatterns: string[],
  maxFiles: number = 50000,
  maxFileSizeBytes: number = 5242880,
): Promise<FileInventory> {
  const files: FileEntry[] = [];
  let skippedFiles = 0;
  let totalFiles = 0;

  function walk(dir: string): void {
    if (files.length >= maxFiles) return;

    let entries: string[];
    try {
      entries = readdirSync(dir);
    } catch {
      return;
    }

    for (const entry of entries) {
      if (files.length >= maxFiles) return;

      const fullPath = join(dir, entry);
      const rel = relative(workspace.rootPath, fullPath);

      if (excludePatterns.some((p) => matchesGlob(rel, p))) {
        skippedFiles++;
        continue;
      }

      let stat;
      try {
        stat = statSync(fullPath);
      } catch {
        skippedFiles++;
        continue;
      }

      if (stat.isDirectory()) {
        walk(fullPath);
      } else if (stat.isFile()) {
        totalFiles++;
        if (stat.size > maxFileSizeBytes) {
          skippedFiles++;
          continue;
        }
        files.push({
          path: fullPath,
          relativePath: rel,
          extension: extname(entry),
          sizeBytes: stat.size,
        });
      }
    }
  }

  walk(workspace.rootPath);

  const extensionCounts: Record<string, number> = {};
  for (const f of files) {
    const ext = f.extension || "(none)";
    extensionCounts[ext] = (extensionCounts[ext] ?? 0) + 1;
  }

  return {
    files,
    totalFiles,
    scannedFiles: files.length,
    skippedFiles,
    extensionCounts,
  };
}
