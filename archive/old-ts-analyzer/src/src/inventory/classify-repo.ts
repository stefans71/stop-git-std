import type { FileInventory } from "./enumerate-files.ts";
import type { LocalWorkspace } from "../models/local-workspace.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { RepoCategory } from "../models/enums.ts";
import { detectFrameworks, detectEcosystems } from "./detect-frameworks.ts";

const EXTENSION_TO_LANGUAGE: Record<string, string> = {
  ".ts": "TypeScript",
  ".tsx": "TypeScript",
  ".js": "JavaScript",
  ".jsx": "JavaScript",
  ".py": "Python",
  ".go": "Go",
  ".rs": "Rust",
  ".java": "Java",
  ".rb": "Ruby",
  ".php": "PHP",
  ".cs": "C#",
  ".cpp": "C++",
  ".c": "C",
  ".swift": "Swift",
  ".kt": "Kotlin",
};

export function detectLanguages(extensionCounts: Record<string, number>): string[] {
  const langCounts = new Map<string, number>();
  for (const [ext, count] of Object.entries(extensionCounts)) {
    const lang = EXTENSION_TO_LANGUAGE[ext];
    if (lang) {
      langCounts.set(lang, (langCounts.get(lang) ?? 0) + count);
    }
  }
  return [...langCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([lang]) => lang);
}

export function detectCategories(
  inventory: FileInventory,
  frameworks: string[],
  languages: string[],
  rootPath?: string,
): RepoCategory[] {
  const categories = new Set<RepoCategory>();
  const fileNames = new Set(inventory.files.map((f) => f.relativePath));
  const hasFile = (name: string) => fileNames.has(name);
  const hasFileMatching = (pattern: RegExp) =>
    inventory.files.some((f) => pattern.test(f.relativePath));

  // Web app detection
  if (frameworks.some((f) => ["nextjs", "nuxt", "angular", "svelte", "remix", "astro"].includes(f))) {
    categories.add("web_app");
  }

  // API detection
  if (hasFileMatching(/routes?\//i) || hasFileMatching(/controllers?\//i) ||
      hasFileMatching(/api\//i) || frameworks.some((f) => ["express", "fastify", "hono"].includes(f))) {
    categories.add("api");
  }

  // AI/LLM detection
  if (hasFileMatching(/\b(llm|openai|anthropic|langchain|transformers)\b/i) ||
      inventory.files.some((f) => f.relativePath.includes("model") && f.extension === ".py")) {
    categories.add("ai_llm");
  }

  // Agent framework detection
  if (hasFileMatching(/\b(agent|tool_use|toolcall|autogen|crewai)\b/i)) {
    categories.add("agent_framework");
  }

  // Skills/plugins detection
  if (hasFile("plugin.json") || hasFile("manifest.json") || hasFileMatching(/skills?\//i)) {
    categories.add("skills_plugins");
  }

  // MCP server detection — check filenames, package name, and dependencies
  const isMcp =
    (hasFileMatching(/mcp/i) && hasFileMatching(/server/i)) ||
    inventory.files.some((f) => {
      if (f.relativePath !== "package.json") return false;
      try {
        if (!rootPath) return false;
        const pkg = JSON.parse(
          require("fs").readFileSync(
            require("path").join(rootPath, f.relativePath),
            "utf8",
          ),
        );
        const name = (pkg.name ?? "").toLowerCase();
        const allDeps = {
          ...pkg.dependencies,
          ...pkg.devDependencies,
        };
        const desc = (pkg.description ?? "").toLowerCase();
        return (
          name.includes("mcp") ||
          desc.includes("mcp") ||
          "@modelcontextprotocol/sdk" in allDeps ||
          Object.keys(allDeps).some((d) => d.includes("mcp-server"))
        );
      } catch {
        return false;
      }
    });
  if (isMcp) {
    categories.add("mcp_server");
  }

  // Library/package detection
  if (hasFile("package.json") || hasFile("Cargo.toml") || hasFile("setup.py") || hasFile("pyproject.toml")) {
    categories.add("library_package");
  }

  // Infrastructure detection
  if (hasFileMatching(/Dockerfile/i) || hasFileMatching(/docker-compose/i) ||
      hasFileMatching(/terraform/i) || hasFileMatching(/k8s|kubernetes/i)) {
    categories.add("infrastructure");
  }

  // CI/CD detection
  if (hasFileMatching(/\.github\/workflows\//)) {
    categories.add("ci_cd");
  }

  if (categories.size === 0) {
    categories.add("library_package");
  }

  return [...categories];
}

export function classifyRepo(
  inventory: FileInventory,
  workspace: LocalWorkspace,
): RepoProfile {
  const languages = detectLanguages(inventory.extensionCounts);
  const frameworks = detectFrameworks(inventory);
  const ecosystems = detectEcosystems(inventory);
  const detected_categories = detectCategories(inventory, frameworks, languages, workspace.rootPath);

  const manifests: string[] = [];
  const workflows: string[] = [];
  const containers: string[] = [];
  const infra: string[] = [];
  const binaries: string[] = [];
  const high_risk_files: string[] = [];

  const BINARY_EXTENSIONS = new Set([".exe", ".dll", ".so", ".dylib", ".bin"]);
  const MANIFEST_FILES = new Set(["package.json", "Cargo.toml", "go.mod", "pyproject.toml",
    "requirements.txt", "Gemfile", "SECURITY.md", "CODEOWNERS"]);

  for (const f of inventory.files) {
    const fileName = f.relativePath.split("/").pop()!;

    if (MANIFEST_FILES.has(fileName) || f.relativePath.endsWith("SECURITY.md") ||
        f.relativePath.endsWith("CODEOWNERS")) {
      manifests.push(f.relativePath);
    }
    if (f.relativePath.startsWith(".github/workflows/")) {
      workflows.push(f.relativePath);
    }
    if (fileName.startsWith("Dockerfile") || fileName === "docker-compose.yml" ||
        fileName === "docker-compose.yaml") {
      containers.push(f.relativePath);
    }
    if (f.relativePath.match(/terraform|k8s|kubernetes|helm/i)) {
      infra.push(f.relativePath);
    }
    if (BINARY_EXTENSIONS.has(f.extension)) {
      binaries.push(f.relativePath);
    }
    if (fileName.startsWith(".env") || fileName.endsWith(".pem") ||
        fileName.endsWith(".key")) {
      high_risk_files.push(f.relativePath);
    }
  }

  // Compute pinned_actions_ratio from workflow files
  let pinnedActions = 0;
  let totalActions = 0;
  const SHA_PIN_RE = /^[^@]+@[0-9a-f]{40}$/;
  for (const wf of workflows) {
    try {
      const content = require("fs").readFileSync(
        `${workspace.rootPath}/${wf}`, "utf-8"
      );
      const usesMatches = content.match(/uses:\s*(.+)/g) ?? [];
      for (const m of usesMatches) {
        const ref = m.replace(/uses:\s*/, "").trim();
        totalActions++;
        if (SHA_PIN_RE.test(ref)) pinnedActions++;
      }
    } catch { /* skip unreadable */ }
  }

  return {
    languages,
    frameworks,
    ecosystems,
    detected_categories,
    artifacts: { manifests, workflows, containers, infra, binaries },
    counts: {
      total_files: inventory.totalFiles,
      scanned_files: inventory.scannedFiles,
      skipped_files: inventory.skippedFiles,
    },
    high_risk_files,
    signed_tags_count: workspace.gitMetadata.signedTags.length,
    pinned_actions_ratio: totalActions > 0 ? pinnedActions / totalActions : 0,
  };
}
