/** Severity levels for findings */
export type Severity = "critical" | "high" | "medium" | "low" | "info";

/** Categories of security findings */
export type FindingCategory =
  | "secrets"
  | "dangerous-execution"
  | "ci-cd"
  | "supply-chain"
  | "governance-trust"
  | "infrastructure"
  | "api"
  | "ai-llm"
  | "agent-framework"
  | "mcp-server"
  | "skills-plugins"
  | "library-package";

/** Evidence supporting a finding */
export interface Evidence {
  readonly file: string;
  readonly line?: number;
  readonly snippet?: string;
  readonly context?: string;
}

/** A single security finding from an analyzer */
export interface Finding {
  readonly id: string;
  readonly ruleId: string;
  readonly category: FindingCategory;
  readonly severity: Severity;
  readonly title: string;
  readonly description: string;
  readonly evidence: readonly Evidence[];
  readonly remediation?: string;
  readonly confidence: number; // 0.0 - 1.0
  readonly tags: readonly string[];
}
