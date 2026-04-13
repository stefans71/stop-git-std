import type { Finding, FindingCategory } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import type { RuleCatalog } from "../../rules/load-rule-catalog.ts";
import { analyzeApi } from "./api.ts";
import { analyzeAiLlm } from "./ai-llm.ts";
import { analyzeAgentFramework } from "./agent-framework.ts";
import { analyzeMcpServer } from "./mcp-server.ts";
import { analyzeSkillsPlugins } from "./skills-plugins.ts";
import { analyzeLibraryPackage } from "./library-package.ts";

type TypedAnalyzer = (
  profile: RepoProfile,
  catalog: RuleCatalog,
) => Promise<readonly Finding[]>;

const TYPED_ANALYZERS: ReadonlyMap<FindingCategory, TypedAnalyzer> = new Map([
  ["api", analyzeApi],
  ["ai-llm", analyzeAiLlm],
  ["agent-framework", analyzeAgentFramework],
  ["mcp-server", analyzeMcpServer],
  ["skills-plugins", analyzeSkillsPlugins],
  ["library-package", analyzeLibraryPackage],
]);

export async function runTypedAnalyzers(
  profile: RepoProfile,
  catalog: RuleCatalog,
  activeCategories: readonly FindingCategory[],
): Promise<readonly Finding[]> {
  const promises: Promise<readonly Finding[]>[] = [];

  for (const category of activeCategories) {
    const analyzer = TYPED_ANALYZERS.get(category);
    if (analyzer) {
      promises.push(analyzer(profile, catalog));
    }
  }

  const results = await Promise.all(promises);
  return results.flat();
}
