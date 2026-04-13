/** Score axes for a repository audit */
export interface Scores {
  /** How trustworthy is the repo's provenance and governance? 0-100 */
  readonly trustworthiness: number;
  /** How exploitable are the detected issues? 0-100 (higher = more exploitable) */
  readonly exploitability: number;
  /** How likely is the repo to be used for abuse? 0-100 (higher = more abusable) */
  readonly abuse_potential: number;
}

/** Per-category score breakdown */
export interface CategoryScore {
  readonly category: string;
  readonly score: number;
  readonly weight: number;
  readonly findingCount: number;
}

/** Full scoring result */
export interface ScoringResult {
  readonly overall: Scores;
  readonly categories: readonly CategoryScore[];
}
