export interface OsvVulnerability {
  id: string;
  summary?: string;
  details?: string;
  aliases?: string[];
  modified?: string;
  published?: string;
  severity?: Array<{ type: string; score: string }>;
  affected?: Array<{
    package: { name: string; ecosystem: string };
    ranges?: Array<{ type: string; events: Array<Record<string, string>> }>;
    versions?: string[];
  }>;
  references?: Array<{ type: string; url: string }>;
}

export interface OsvQueryResult {
  vulns: OsvVulnerability[];
}

/**
 * Stub: always returns an empty vulnerability list.
 * Useful when OSV querying is disabled or in dry-run mode.
 */
export async function queryOsvStub(): Promise<OsvQueryResult> {
  return { vulns: [] };
}

/**
 * Query the OSV API for vulnerabilities affecting a given package.
 *
 * @param ecosystem  e.g. "npm", "PyPI", "Go"
 * @param packageName  the package name
 * @param version  optional pinned version to narrow results
 */
export async function queryOsv(
  ecosystem: string,
  packageName: string,
  version?: string,
): Promise<OsvQueryResult> {
  const url = "https://api.osv.dev/v1/query";

  const body: Record<string, unknown> = {
    package: {
      name: packageName,
      ecosystem,
    },
  };
  if (version) {
    body.version = version;
  }

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    return { vulns: [] };
  }

  if (!response.ok) {
    return { vulns: [] };
  }

  let data: unknown;
  try {
    data = await response.json();
  } catch {
    return { vulns: [] };
  }

  const result = data as { vulns?: OsvVulnerability[] };
  return { vulns: result.vulns ?? [] };
}
