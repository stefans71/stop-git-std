export interface ScorecardCheckResult {
  name: string;
  score: number;
  reason?: string;
  details?: string[];
}

export interface ScorecardResult {
  repo: string;
  ref?: string;
  score: number;
  checks: ScorecardCheckResult[];
  date?: string;
}

/**
 * Fetch OpenSSF Scorecard results for a repository.
 *
 * This is currently a stub — returns null.
 * A full implementation would call the Scorecard API at
 * https://api.securityscorecards.dev/projects/github.com/<owner>/<repo>
 */
export async function fetchScorecard(
  _owner: string,
  _repo: string,
): Promise<ScorecardResult | null> {
  return null;
}
