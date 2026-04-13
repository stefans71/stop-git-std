import type { RepoType, DetectedFramework, FileInventory } from "../models/repo-profile.ts";

interface ClassificationSignal {
  readonly type: RepoType;
  readonly weight: number;
}

export function classifyRepo(
  inventory: FileInventory,
  frameworks: readonly DetectedFramework[],
): readonly RepoType[] {
  const signals: ClassificationSignal[] = [];
  const fileSet = new Set(inventory.files);
  const frameworkNames = new Set(frameworks.map((f) => f.name));

  // API detection
  if (
    frameworkNames.has("express") ||
    frameworkNames.has("fastify") ||
    frameworkNames.has("fastapi") ||
    frameworkNames.has("flask")
  ) {
    signals.push({ type: "api", weight: 0.8 });
  }
  if (inventory.files.some((f) => f.includes("routes/") || f.includes("api/"))) {
    signals.push({ type: "api", weight: 0.5 });
  }

  // Web app detection
  if (frameworkNames.has("next.js") || frameworkNames.has("react") || frameworkNames.has("vue")) {
    signals.push({ type: "web-app", weight: 0.8 });
  }

  // AI/LLM detection
  if (frameworkNames.has("langchain") || frameworkNames.has("openai") || frameworkNames.has("anthropic")) {
    signals.push({ type: "ai-llm", weight: 0.9 });
  }
  if (inventory.files.some((f) => f.includes("prompt") || f.includes("llm") || f.includes("model"))) {
    signals.push({ type: "ai-llm", weight: 0.3 });
  }

  // Agent framework detection
  if (
    frameworkNames.has("openai") &&
    inventory.files.some((f) => f.includes("agent") || f.includes("tool"))
  ) {
    signals.push({ type: "agent-framework", weight: 0.7 });
  }
  if (inventory.files.some((f) => f.match(/agents?\//i) && inventory.files.some((g) => g.match(/tools?\//i)))) {
    signals.push({ type: "agent-framework", weight: 0.5 });
  }

  // MCP server detection
  if (frameworkNames.has("mcp-sdk")) {
    signals.push({ type: "mcp-server", weight: 0.95 });
  }
  if (inventory.files.some((f) => f.includes("mcp") || f.match(/server\.(ts|js)$/))) {
    signals.push({ type: "mcp-server", weight: 0.3 });
  }

  // Skills/plugins detection
  if (
    inventory.files.some((f) => f.includes("manifest.json") || f.includes("plugin.json")) ||
    inventory.files.some((f) => f.match(/skills?\//i) || f.match(/plugins?\//i))
  ) {
    signals.push({ type: "skills-plugins", weight: 0.6 });
  }

  // Library/package detection
  if (fileSet.has("package.json")) {
    // Check for typical library indicators
    if (
      inventory.files.some(
        (f) => f === "index.ts" || f === "index.js" || f === "src/index.ts" || f === "src/index.js",
      )
    ) {
      signals.push({ type: "library-package", weight: 0.4 });
    }
  }

  // CI/CD heavy detection
  const ciFiles = inventory.files.filter(
    (f) => f.startsWith(".github/workflows/") || f.startsWith(".circleci/") || f.startsWith(".gitlab-ci"),
  );
  if (ciFiles.length >= 3) {
    signals.push({ type: "ci-cd-heavy", weight: 0.6 });
  }

  // Infrastructure heavy detection
  if (frameworkNames.has("terraform") || frameworkNames.has("kubernetes")) {
    signals.push({ type: "infrastructure-heavy", weight: 0.8 });
  }
  if (frameworkNames.has("docker")) {
    signals.push({ type: "infrastructure-heavy", weight: 0.3 });
  }

  // Aggregate signals by type, take the max weight
  const typeWeights = new Map<RepoType, number>();
  for (const signal of signals) {
    const existing = typeWeights.get(signal.type) ?? 0;
    typeWeights.set(signal.type, Math.max(existing, signal.weight));
  }

  // Return types with weight >= 0.4, sorted by weight descending
  const types = Array.from(typeWeights.entries())
    .filter(([, weight]) => weight >= 0.4)
    .sort((a, b) => b[1] - a[1])
    .map(([type]) => type);

  return types.length > 0 ? types : ["unknown"];
}
