import type { RepoProfile, RepoType } from "../models/repo-profile.ts";
import type { FindingCategory } from "../models/finding.ts";

const UNIVERSAL_CATEGORIES: readonly FindingCategory[] = [
  "secrets",
  "dangerous-execution",
  "ci-cd",
  "supply-chain",
  "governance-trust",
  "infrastructure",
];

const TYPE_TO_CATEGORY: ReadonlyMap<RepoType, FindingCategory> = new Map([
  ["api", "api"],
  ["ai-llm", "ai-llm"],
  ["agent-framework", "agent-framework"],
  ["mcp-server", "mcp-server"],
  ["skills-plugins", "skills-plugins"],
  ["library-package", "library-package"],
]);

export interface ActivatedModules {
  readonly universal: readonly FindingCategory[];
  readonly typed: readonly FindingCategory[];
}

export function activateModules(profile: RepoProfile): ActivatedModules {
  const typed: FindingCategory[] = [];

  for (const repoType of profile.types) {
    const category = TYPE_TO_CATEGORY.get(repoType);
    if (category && !typed.includes(category)) {
      typed.push(category);
    }
  }

  return {
    universal: UNIVERSAL_CATEGORIES,
    typed,
  };
}
