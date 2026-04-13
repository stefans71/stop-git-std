import type { Finding } from "../models/finding.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { RuleDefinition } from "../rules/load-rule-catalog.ts";

export interface AnalyzerInput {
  readonly profile: RepoProfile;
  readonly rules: readonly RuleDefinition[];
  readonly files: readonly string[];
}

export interface AnalyzerBackend {
  readonly name: string;
  readonly type: "builtin-ts" | "python-subprocess" | "external-tool";
  analyze(input: AnalyzerInput): Promise<readonly Finding[]>;
}

export interface AnalyzerRegistry {
  register(backend: AnalyzerBackend): void;
  get(name: string): AnalyzerBackend | undefined;
  list(): readonly AnalyzerBackend[];
}

export function createAnalyzerRegistry(): AnalyzerRegistry {
  const backends = new Map<string, AnalyzerBackend>();

  return {
    register(backend: AnalyzerBackend): void {
      backends.set(backend.name, backend);
    },
    get(name: string): AnalyzerBackend | undefined {
      return backends.get(name);
    },
    list(): readonly AnalyzerBackend[] {
      return Array.from(backends.values());
    },
  };
}
