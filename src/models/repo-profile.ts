/** Detected repo type categories */
export type RepoType =
  | "web-app"
  | "api"
  | "ai-llm"
  | "agent-framework"
  | "skills-plugins"
  | "mcp-server"
  | "library-package"
  | "ci-cd-heavy"
  | "infrastructure-heavy"
  | "unknown";

/** Detected framework information */
export interface DetectedFramework {
  readonly name: string;
  readonly version?: string;
  readonly confidence: number;
}

/** File inventory for a repository */
export interface FileInventory {
  readonly totalFiles: number;
  readonly byExtension: ReadonlyMap<string, number>;
  readonly files: readonly string[];
}

/** Profile of an analyzed repository */
export interface RepoProfile {
  readonly path: string;
  readonly name: string;
  readonly types: readonly RepoType[];
  readonly frameworks: readonly DetectedFramework[];
  readonly inventory: FileInventory;
  readonly languages: readonly string[];
  readonly hasLockfile: boolean;
  readonly hasCiConfig: boolean;
  readonly hasDockerfile: boolean;
  readonly hasK8sConfig: boolean;
}
