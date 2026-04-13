import type { Finding } from "../../models/finding.ts";
import type { RepoProfile } from "../../models/repo-profile.ts";
import type { RuleCatalog } from "../../rules/load-rule-catalog.ts";
import { analyzeSecrets } from "./secrets.ts";
import { analyzeDangerousExecution } from "./dangerous-execution.ts";
import { analyzeCiCd } from "./ci-cd.ts";
import { analyzeSupplyChain } from "./supply-chain.ts";
import { analyzeGovernanceTrust } from "./governance-trust.ts";
import { analyzeInfrastructure } from "./infrastructure.ts";

export async function runUniversalAnalyzers(
  profile: RepoProfile,
  catalog: RuleCatalog,
): Promise<readonly Finding[]> {
  const results = await Promise.all([
    analyzeSecrets(profile, catalog),
    analyzeDangerousExecution(profile, catalog),
    analyzeCiCd(profile, catalog),
    analyzeSupplyChain(profile, catalog),
    analyzeGovernanceTrust(profile, catalog),
    analyzeInfrastructure(profile, catalog),
  ]);

  return results.flat();
}
