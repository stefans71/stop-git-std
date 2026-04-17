export interface ParsedPackageJson {
  name?: string;
  version?: string;
  scripts: Record<string, string>;
  dependencies: Record<string, string>;
  devDependencies: Record<string, string>;
  peerDependencies: Record<string, string>;
  optionalDependencies: Record<string, string>;
  main?: string;
  module?: string;
  type?: string;
  bin?: Record<string, string> | string;
  files?: string[];
  engines?: Record<string, string>;
  raw: Record<string, unknown>;
}

/**
 * Parse the content of a package.json file.
 * Returns a typed structure with empty objects/arrays as defaults.
 */
export function parsePackageJson(content: string): ParsedPackageJson {
  let raw: Record<string, unknown>;
  try {
    raw = JSON.parse(content) as Record<string, unknown>;
  } catch {
    raw = {};
  }

  function strRecord(val: unknown): Record<string, string> {
    if (val && typeof val === "object" && !Array.isArray(val)) {
      const result: Record<string, string> = {};
      for (const [k, v] of Object.entries(val as Record<string, unknown>)) {
        if (typeof v === "string") result[k] = v;
      }
      return result;
    }
    return {};
  }

  return {
    name: typeof raw.name === "string" ? raw.name : undefined,
    version: typeof raw.version === "string" ? raw.version : undefined,
    scripts: strRecord(raw.scripts),
    dependencies: strRecord(raw.dependencies),
    devDependencies: strRecord(raw.devDependencies),
    peerDependencies: strRecord(raw.peerDependencies),
    optionalDependencies: strRecord(raw.optionalDependencies),
    main: typeof raw.main === "string" ? raw.main : undefined,
    module: typeof raw.module === "string" ? raw.module : undefined,
    type: typeof raw.type === "string" ? raw.type : undefined,
    bin: (raw.bin as ParsedPackageJson["bin"]) ?? undefined,
    files: Array.isArray(raw.files)
      ? (raw.files as unknown[]).filter((f): f is string => typeof f === "string")
      : undefined,
    engines: strRecord(raw.engines),
    raw,
  };
}
