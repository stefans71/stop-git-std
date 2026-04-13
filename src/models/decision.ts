import type { Scores } from "./scores.ts";

/** Final decision values for a repository audit */
export type DecisionVerdict =
  | "PROCEED"
  | "PROCEED_WITH_CONSTRAINTS"
  | "CAUTION"
  | "ABORT";

/** Constraints applied when decision is PROCEED_WITH_CONSTRAINTS */
export interface Constraint {
  readonly description: string;
  readonly category: string;
  readonly severity: "required" | "recommended";
}

/** The final policy decision for a repository */
export interface Decision {
  readonly verdict: DecisionVerdict;
  readonly scores: Scores;
  readonly constraints: readonly Constraint[];
  readonly reasoning: string;
  readonly criticalFindings: number;
  readonly highFindings: number;
}
