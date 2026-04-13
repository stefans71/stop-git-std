import type { AuditRequest } from "../models/audit-request.ts";
import type { Finding } from "../models/finding.ts";
import type { RepoProfile } from "../models/repo-profile.ts";
import type { Decision } from "../models/decision.ts";
import type { ScoringResult } from "../models/scores.ts";
import type { RuleCatalog } from "../rules/load-rule-catalog.ts";
import { acquireRepo } from "../inventory/acquire-repo.ts";
import { enumerateFiles } from "../inventory/enumerate-files.ts";
import { classifyRepo } from "../inventory/classify-repo.ts";
import { detectFrameworks } from "../inventory/detect-frameworks.ts";
import { activateModules } from "./router.ts";
import { runUniversalAnalyzers } from "../analyzers/universal/index.ts";
import { runTypedAnalyzers } from "../analyzers/typed/index.ts";
import { normalizeFindings } from "./normalize-findings.ts";
import { scoreFindings } from "./scoring.ts";
import { applyPolicy } from "./policy.ts";
import { basename } from "node:path";

export interface AuditResult {
  readonly profile: RepoProfile;
  readonly findings: readonly Finding[];
  readonly scores: ScoringResult;
  readonly decision: Decision;
}

export async function runAudit(
  request: AuditRequest,
  catalog: RuleCatalog,
): Promise<AuditResult> {
  // 1. Acquire repo
  const { repoPath } = await acquireRepo(request.repoPath);

  // 2. Inventory files
  const inventory = await enumerateFiles(repoPath);

  // 3. Detect frameworks
  const frameworks = await detectFrameworks(repoPath, inventory.files);

  // 4. Classify repo
  const types = classifyRepo(inventory, frameworks);

  // Detect languages from file extensions
  const languages = detectLanguages(inventory.byExtension);

  const profile: RepoProfile = {
    path: repoPath,
    name: basename(repoPath),
    types,
    frameworks,
    inventory,
    languages,
    hasLockfile: inventory.files.some(
      (f) =>
        f === "package-lock.json" ||
        f === "bun.lockb" ||
        f === "bun.lock" ||
        f === "pnpm-lock.yaml" ||
        f === "yarn.lock" ||
        f === "Gemfile.lock" ||
        f === "poetry.lock" ||
        f === "Pipfile.lock",
    ),
    hasCiConfig: inventory.files.some(
      (f) => f.startsWith(".github/workflows/") || f.startsWith(".circleci/") || f === ".gitlab-ci.yml",
    ),
    hasDockerfile: inventory.files.some((f) => f === "Dockerfile" || f.startsWith("Dockerfile.")),
    hasK8sConfig: inventory.files.some(
      (f) => f.includes("k8s/") || f.includes("kubernetes/") || f.includes("helm/"),
    ),
  };

  // 5. Activate modules
  const modules = activateModules(profile);

  // 6. Run universal analyzers
  const universalFindings = await runUniversalAnalyzers(profile, catalog);

  // 7. Run typed analyzers
  const typedFindings = await runTypedAnalyzers(profile, catalog, modules.typed);

  // 8. Normalize findings
  const allFindings = normalizeFindings([...universalFindings, ...typedFindings]);

  // 9. Score
  const scores = scoreFindings(allFindings);

  // 10. Decide
  const decision = applyPolicy(scores, allFindings);

  return { profile, findings: allFindings, scores, decision };
}

function detectLanguages(byExtension: ReadonlyMap<string, number>): readonly string[] {
  const extToLang: Record<string, string> = {
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".py": "Python",
    ".rb": "Ruby",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".swift": "Swift",
    ".php": "PHP",
  };

  const langs = new Set<string>();
  for (const [ext] of byExtension) {
    const lang = extToLang[ext];
    if (lang) langs.add(lang);
  }
  return Array.from(langs);
}
