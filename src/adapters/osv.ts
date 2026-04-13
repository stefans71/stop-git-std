export interface OsvVulnerability {
  readonly id: string;
  readonly summary: string;
  readonly severity?: string;
  readonly aliases?: readonly string[];
  readonly affected: readonly {
    readonly package: { readonly name: string; readonly ecosystem: string };
    readonly ranges?: readonly { readonly events: readonly Record<string, string>[] }[];
  }[];
}

/**
 * Query the OSV.dev API for known vulnerabilities in a package.
 */
export async function queryOsv(
  packageName: string,
  ecosystem: string,
  version?: string,
): Promise<readonly OsvVulnerability[]> {
  try {
    const body: Record<string, unknown> = {
      package: { name: packageName, ecosystem },
    };
    if (version) {
      body.version = version;
    }

    const response = await fetch("https://api.osv.dev/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) return [];

    const data = (await response.json()) as { vulns?: OsvVulnerability[] };
    return data.vulns ?? [];
  } catch {
    return [];
  }
}

/**
 * Batch query for multiple packages.
 */
export async function batchQueryOsv(
  packages: readonly { name: string; ecosystem: string; version?: string }[],
): Promise<ReadonlyMap<string, readonly OsvVulnerability[]>> {
  const results = new Map<string, readonly OsvVulnerability[]>();

  // Query in parallel with concurrency limit
  const concurrency = 5;
  for (let i = 0; i < packages.length; i += concurrency) {
    const batch = packages.slice(i, i + concurrency);
    const promises = batch.map(async (pkg) => {
      const vulns = await queryOsv(pkg.name, pkg.ecosystem, pkg.version);
      return { name: pkg.name, vulns };
    });

    const batchResults = await Promise.all(promises);
    for (const { name, vulns } of batchResults) {
      if (vulns.length > 0) {
        results.set(name, vulns);
      }
    }
  }

  return results;
}
