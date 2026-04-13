import { readFile } from "node:fs/promises";
import { join } from "node:path";

export interface PackageJsonData {
  readonly name?: string;
  readonly version?: string;
  readonly scripts?: Readonly<Record<string, string>>;
  readonly dependencies?: Readonly<Record<string, string>>;
  readonly devDependencies?: Readonly<Record<string, string>>;
  readonly peerDependencies?: Readonly<Record<string, string>>;
  readonly private?: boolean;
}

export async function parsePackageJson(repoPath: string): Promise<PackageJsonData | null> {
  try {
    const content = await readFile(join(repoPath, "package.json"), "utf-8");
    return JSON.parse(content) as PackageJsonData;
  } catch {
    return null;
  }
}

export function getAllDependencies(pkg: PackageJsonData): ReadonlyMap<string, string> {
  const deps = new Map<string, string>();
  for (const [name, version] of Object.entries(pkg.dependencies ?? {})) {
    deps.set(name, version);
  }
  for (const [name, version] of Object.entries(pkg.devDependencies ?? {})) {
    deps.set(name, version);
  }
  for (const [name, version] of Object.entries(pkg.peerDependencies ?? {})) {
    deps.set(name, version);
  }
  return deps;
}
