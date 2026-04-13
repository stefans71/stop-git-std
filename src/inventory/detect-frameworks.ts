import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { DetectedFramework } from "../models/repo-profile.ts";

interface FrameworkSignature {
  readonly name: string;
  readonly packageNames: readonly string[];
  readonly fileIndicators?: readonly string[];
}

const FRAMEWORK_SIGNATURES: readonly FrameworkSignature[] = [
  { name: "express", packageNames: ["express"], fileIndicators: [] },
  { name: "fastify", packageNames: ["fastify"] },
  { name: "next.js", packageNames: ["next"], fileIndicators: ["next.config.js", "next.config.ts", "next.config.mjs"] },
  { name: "react", packageNames: ["react"] },
  { name: "vue", packageNames: ["vue"] },
  { name: "django", packageNames: ["django"], fileIndicators: ["manage.py"] },
  { name: "flask", packageNames: ["flask"] },
  { name: "fastapi", packageNames: ["fastapi"] },
  { name: "langchain", packageNames: ["langchain", "@langchain/core"] },
  { name: "openai", packageNames: ["openai", "@openai/agents"] },
  { name: "anthropic", packageNames: ["@anthropic-ai/sdk"] },
  { name: "mcp-sdk", packageNames: ["@modelcontextprotocol/sdk"] },
  { name: "terraform", packageNames: [], fileIndicators: ["main.tf", "terraform.tf"] },
  { name: "kubernetes", packageNames: [], fileIndicators: ["k8s/", "kubernetes/"] },
  { name: "docker", packageNames: [], fileIndicators: ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"] },
];

export async function detectFrameworks(
  repoPath: string,
  files: readonly string[],
): Promise<readonly DetectedFramework[]> {
  const detected: DetectedFramework[] = [];
  const fileSet = new Set(files);

  // Check package.json dependencies
  let pkgDeps: Record<string, string> = {};
  try {
    const pkgContent = await readFile(join(repoPath, "package.json"), "utf-8");
    const pkg = JSON.parse(pkgContent) as {
      dependencies?: Record<string, string>;
      devDependencies?: Record<string, string>;
    };
    pkgDeps = { ...pkg.dependencies, ...pkg.devDependencies };
  } catch {
    // No package.json or invalid
  }

  for (const sig of FRAMEWORK_SIGNATURES) {
    // Check package dependencies
    for (const pkgName of sig.packageNames) {
      if (pkgDeps[pkgName]) {
        detected.push({
          name: sig.name,
          version: pkgDeps[pkgName],
          confidence: 0.9,
        });
        break;
      }
    }

    // Check file indicators
    if (sig.fileIndicators) {
      for (const indicator of sig.fileIndicators) {
        if (fileSet.has(indicator) || files.some((f) => f.startsWith(indicator))) {
          if (!detected.some((d) => d.name === sig.name)) {
            detected.push({ name: sig.name, confidence: 0.7 });
          }
          break;
        }
      }
    }
  }

  return detected;
}
