import { readFile } from "node:fs/promises";
import { parse as parseYaml } from "yaml";
import type { Severity } from "../models/finding.ts";

export interface RuleDefinition {
  readonly id: string;
  readonly title: string;
  readonly severity: Severity;
  readonly pattern?: string;
  readonly filePattern?: boolean;
  readonly fileGlob?: string;
  readonly entropyCheck?: boolean;
  readonly minEntropy?: number;
  readonly description: string;
  readonly remediation?: string;
}

export interface RuleCategory {
  readonly name: string;
  readonly description: string;
  readonly rules: readonly RuleDefinition[];
}

export interface RuleCatalog {
  readonly categories: ReadonlyMap<string, RuleCategory>;
}

export async function loadRuleCatalog(path: string): Promise<RuleCatalog> {
  const content = await readFile(path, "utf-8");
  const parsed = parseYaml(content) as {
    categories: Record<string, { name: string; description: string; rules: RuleDefinition[] }>;
  };

  const categories = new Map<string, RuleCategory>();
  for (const [key, value] of Object.entries(parsed.categories)) {
    categories.set(key, {
      name: value.name,
      description: value.description,
      rules: value.rules ?? [],
    });
  }

  return { categories };
}

export function getRulesForCategory(catalog: RuleCatalog, category: string): readonly RuleDefinition[] {
  return catalog.categories.get(category)?.rules ?? [];
}
