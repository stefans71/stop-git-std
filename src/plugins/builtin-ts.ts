import type { AnalyzerModule } from "./analyzer-backend.ts";

// Import and register all built-in analyzers
import { governanceTrustAnalyzer } from "../analyzers/universal/governance-trust.ts";
import { supplyChainAnalyzer } from "../analyzers/universal/supply-chain.ts";
import { secretsAnalyzer } from "../analyzers/universal/secrets.ts";
import { dangerousExecutionAnalyzer } from "../analyzers/universal/dangerous-execution.ts";
import { ciCdAnalyzer } from "../analyzers/universal/ci-cd.ts";
import { infrastructureAnalyzer } from "../analyzers/universal/infrastructure.ts";
import { webAnalyzer } from "../analyzers/typed/web.ts";
import { apiAnalyzer } from "../analyzers/typed/api.ts";
import { aiLlmAnalyzer } from "../analyzers/typed/ai-llm.ts";
import { agentFrameworkAnalyzer } from "../analyzers/typed/agent-framework.ts";
import { skillsPluginsAnalyzer } from "../analyzers/typed/skills-plugins.ts";
import { mcpServerAnalyzer } from "../analyzers/typed/mcp-server.ts";
import { libraryPackageAnalyzer } from "../analyzers/typed/library-package.ts";

const registry = new Map<string, AnalyzerModule>();

function registerAnalyzer(analyzer: AnalyzerModule): void {
  registry.set(analyzer.name, analyzer);
}

export function getAnalyzer(name: string): AnalyzerModule | undefined {
  return registry.get(name);
}

export function getAllAnalyzers(): AnalyzerModule[] {
  return Array.from(registry.values());
}

// Register all analyzers
registerAnalyzer(governanceTrustAnalyzer);
registerAnalyzer(supplyChainAnalyzer);
registerAnalyzer(secretsAnalyzer);
registerAnalyzer(dangerousExecutionAnalyzer);
registerAnalyzer(ciCdAnalyzer);
registerAnalyzer(infrastructureAnalyzer);
registerAnalyzer(webAnalyzer);
registerAnalyzer(apiAnalyzer);
registerAnalyzer(aiLlmAnalyzer);
registerAnalyzer(agentFrameworkAnalyzer);
registerAnalyzer(skillsPluginsAnalyzer);
registerAnalyzer(mcpServerAnalyzer);
registerAnalyzer(libraryPackageAnalyzer);
