export interface ScorecardResult {
  readonly score: number;
  readonly checks: readonly ScorecardCheck[];
}

export interface ScorecardCheck {
  readonly name: string;
  readonly score: number;
  readonly reason: string;
}

/**
 * Fetch OpenSSF Scorecard results for a GitHub repository.
 * Uses the Scorecard API at api.securityscorecards.dev.
 */
export async function fetchScorecard(
  owner: string,
  repo: string,
): Promise<ScorecardResult | null> {
  try {
    const response = await fetch(
      `https://api.securityscorecards.dev/projects/github.com/${owner}/${repo}`,
      {
        headers: { Accept: "application/json" },
      },
    );

    if (!response.ok) return null;

    const data = (await response.json()) as Record<string, unknown>;
    const checks = (data.checks as Record<string, unknown>[]) ?? [];

    return {
      score: data.score as number,
      checks: checks.map((c) => ({
        name: c.name as string,
        score: c.score as number,
        reason: c.reason as string,
      })),
    };
  } catch {
    return null;
  }
}
