import type { Finding, FindingCategory } from "../models/finding.ts";
import type { Scores, CategoryScore, ScoringResult } from "../models/scores.ts";

const SEVERITY_WEIGHTS = { critical: 10, high: 5, medium: 2, low: 1, info: 0 };

const CATEGORY_AXIS_WEIGHTS: Record<string, { trust: number; exploit: number; abuse: number }> = {
  "secrets": { trust: 0.3, exploit: 0.8, abuse: 0.5 },
  "dangerous-execution": { trust: 0.4, exploit: 0.9, abuse: 0.7 },
  "ci-cd": { trust: 0.5, exploit: 0.7, abuse: 0.6 },
  "supply-chain": { trust: 0.7, exploit: 0.5, abuse: 0.4 },
  "governance-trust": { trust: 0.9, exploit: 0.1, abuse: 0.2 },
  "infrastructure": { trust: 0.3, exploit: 0.6, abuse: 0.4 },
  "api": { trust: 0.3, exploit: 0.7, abuse: 0.5 },
  "ai-llm": { trust: 0.4, exploit: 0.6, abuse: 0.8 },
  "agent-framework": { trust: 0.4, exploit: 0.8, abuse: 0.9 },
  "mcp-server": { trust: 0.4, exploit: 0.8, abuse: 0.9 },
  "skills-plugins": { trust: 0.3, exploit: 0.6, abuse: 0.7 },
  "library-package": { trust: 0.5, exploit: 0.4, abuse: 0.3 },
};

export function scoreFindings(findings: readonly Finding[]): ScoringResult {
  // Group by category
  const byCategory = new Map<FindingCategory, Finding[]>();
  for (const f of findings) {
    const list = byCategory.get(f.category) ?? [];
    list.push(f);
    byCategory.set(f.category, list);
  }

  // Calculate per-category scores
  const categories: CategoryScore[] = [];
  let totalTrust = 0;
  let totalExploit = 0;
  let totalAbuse = 0;
  let totalWeight = 0;

  for (const [category, categoryFindings] of byCategory) {
    const rawScore = categoryFindings.reduce(
      (sum, f) => sum + SEVERITY_WEIGHTS[f.severity] * f.confidence,
      0,
    );

    // Normalize to 0-100 (cap at 100)
    const normalizedScore = Math.min(100, rawScore * 5);
    const weight = categoryFindings.length;

    categories.push({
      category,
      score: Math.round(normalizedScore),
      weight,
      findingCount: categoryFindings.length,
    });

    const axisWeights = CATEGORY_AXIS_WEIGHTS[category] ?? { trust: 0.5, exploit: 0.5, abuse: 0.5 };
    totalTrust += normalizedScore * axisWeights.trust * weight;
    totalExploit += normalizedScore * axisWeights.exploit * weight;
    totalAbuse += normalizedScore * axisWeights.abuse * weight;
    totalWeight += weight;
  }

  // Calculate overall scores
  const divisor = totalWeight || 1;
  const overall: Scores = {
    // Trustworthiness is inverted: high findings = low trust
    trustworthiness: Math.max(0, Math.round(100 - totalTrust / divisor)),
    exploitability: Math.min(100, Math.round(totalExploit / divisor)),
    abuse_potential: Math.min(100, Math.round(totalAbuse / divisor)),
  };

  return { overall, categories };
}
