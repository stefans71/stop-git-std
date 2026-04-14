import { z } from "zod";
import { parse as parseYaml } from "yaml";
import { readFileSync } from "fs";
import { join } from "path";
import type { Finding } from "../models/finding.ts";

// ── Suppression schemas ───────────────────────────────────────────────────────

export const SuppressionEntrySchema = z.object({
  rule_id: z.string(),
  path_globs: z.array(z.string()).optional(),
  expires_at: z.string().optional(),
  justification: z.string(),
  approved_by: z.string().optional(),
  override_reason: z.string().optional(),
  reviewer_identity: z.string().optional(),
  reviewed_commit_sha: z.string().optional(),
});

export type SuppressionEntry = z.infer<typeof SuppressionEntrySchema>;

export const SuppressionsFileSchema = z.object({
  suppressions: z.array(SuppressionEntrySchema),
});

export type SuppressionsFile = z.infer<typeof SuppressionsFileSchema>;

// ── Glob helper ───────────────────────────────────────────────────────────────

function globToRegex(pattern: string): RegExp {
  const regexStr = pattern
    .replace(/\./g, "\\.")
    .replace(/\*\*/g, "___GLOBSTAR___")
    .replace(/\*/g, "[^/]*")
    .replace(/___GLOBSTAR___/g, ".*")
    .replace(/\?/g, ".");
  return new RegExp(`^${regexStr}$`);
}

function matchesAnyGlob(filePath: string, globs: string[]): boolean {
  return globs.some((g) => globToRegex(g).test(filePath));
}

// ── Core functions ────────────────────────────────────────────────────────────

/**
 * Merge universal, typed, and optional runtime findings into a single list,
 * then deduplicate.
 */
export function normalizeFindings(
  universalFindings: Finding[],
  typedFindings: Finding[],
  runtimeFindings: Finding[] = [],
): Finding[] {
  const merged = [...universalFindings, ...typedFindings, ...runtimeFindings];
  return deduplicateFindings(merged);
}

/**
 * Deduplicate findings by a composite key of id | sorted files | evidence type.
 * When duplicates are found, evidence records are combined into the first occurrence.
 */
export function deduplicateFindings(findings: Finding[]): Finding[] {
  const seen = new Map<string, Finding>();
  for (const f of findings) {
    const key = `${f.id}|${(f.files ?? []).slice().sort().join(",")}|${f.evidence.type}`;
    if (!seen.has(key)) {
      seen.set(key, { ...f, evidence: { ...f.evidence, records: [...f.evidence.records] } });
    } else {
      // Merge evidence records into the existing entry
      const existing = seen.get(key)!;
      existing.evidence.records.push(...f.evidence.records);
    }
  }
  return Array.from(seen.values());
}

/**
 * Apply suppressions to findings.
 *
 * C3 constraint: hard-stop rule IDs require `override_reason`, `reviewer_identity`,
 * and `reviewed_commit_sha` on the suppression entry before they can be suppressed.
 */
export function applySuppressions(
  findings: Finding[],
  suppressions: SuppressionEntry[],
  hardStopPatterns: string[],
): Finding[] {
  return findings.map((finding) => {
    const matchingSuppression = suppressions.find((s) => {
      if (s.rule_id !== finding.id) return false;

      // If path_globs are specified, at least one file must match
      if (s.path_globs && s.path_globs.length > 0) {
        const files = finding.files ?? [];
        if (files.length === 0) return false;
        if (!files.some((file) => matchesAnyGlob(file, s.path_globs!))) return false;
      }

      return true;
    });

    if (!matchingSuppression) return finding;

    // C3: hard-stop rules need override_reason + reviewer_identity + reviewed_commit_sha
    const isHardStop = hardStopPatterns.includes(finding.id);
    if (isHardStop) {
      const hasOverride =
        matchingSuppression.override_reason &&
        matchingSuppression.reviewer_identity &&
        matchingSuppression.reviewed_commit_sha;
      if (!hasOverride) {
        // Cannot suppress without required override fields
        return finding;
      }
    }

    return {
      ...finding,
      suppressed: true,
      suppression_reason: matchingSuppression.justification,
    };
  });
}

/**
 * Load suppressions from `.stop-git-std.suppressions.yaml` in the workspace root.
 * Filters out entries that have expired (expires_at < today).
 */
export function loadSuppressions(workspacePath: string): SuppressionEntry[] {
  const filePath = join(workspacePath, ".stop-git-std.suppressions.yaml");

  let raw: string;
  try {
    raw = readFileSync(filePath, "utf-8");
  } catch {
    // File not present — no suppressions
    return [];
  }

  let parsed: unknown;
  try {
    parsed = parseYaml(raw);
  } catch (err) {
    console.warn(`[suppressions] Failed to parse ${filePath}: ${err}`);
    return [];
  }

  const result = SuppressionsFileSchema.safeParse(parsed);
  if (!result.success) {
    console.warn(`[suppressions] Schema validation failed for ${filePath}: ${result.error.message}`);
    return [];
  }

  const now = new Date();
  return result.data.suppressions.filter((s) => {
    if (!s.expires_at) return true;
    return new Date(s.expires_at) >= now;
  });
}
