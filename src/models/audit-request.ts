/** Supported output formats */
export type OutputFormat = "terminal" | "json" | "markdown";

/** Configuration for an audit run */
export interface AuditRequest {
  /** Path or URL to the repository to audit */
  readonly target: string;
  /** Resolved local path to the repository */
  readonly repoPath: string;
  /** Output format(s) to generate */
  readonly outputFormats: readonly OutputFormat[];
  /** Output directory for reports (defaults to stdout for terminal) */
  readonly outputDir?: string;
  /** Whether to run in verbose mode */
  readonly verbose: boolean;
  /** Path to custom rule catalog override */
  readonly ruleCatalogPath?: string;
  /** Specific categories to check (empty = all) */
  readonly categories?: readonly string[];
}
