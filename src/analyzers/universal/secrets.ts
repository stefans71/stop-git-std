import { readdirSync, statSync } from "fs";
import { join } from "path";
import { emitFinding, readFileContent, scanFileContent } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", "vendor", "__pycache__"]);

function walkFiles(dir: string, maxDepth = 5, depth = 0): string[] {
  if (depth > maxDepth) return [];
  const results: string[] = [];
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (SKIP_DIRS.has(entry.name)) continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        results.push(...walkFiles(full, maxDepth, depth + 1));
      } else {
        results.push(full);
      }
    }
  } catch {
    // ignore permission errors
  }
  return results;
}

/**
 * Compute Shannon entropy of a string.
 */
function shannonEntropy(str: string): number {
  const freq: Record<string, number> = {};
  for (const ch of str) {
    freq[ch] = (freq[ch] ?? 0) + 1;
  }
  let entropy = 0;
  const len = str.length;
  for (const count of Object.values(freq)) {
    const p = count / len;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

/**
 * Find high-entropy tokens near authentication-related keywords.
 * Returns matches with their context.
 */
function findHighEntropyNearAuth(
  content: string,
  filePath: string,
  threshold: number,
): Array<{ path: string; lineNumber: number; token: string; entropy: number; keyword: string }> {
  const results: Array<{
    path: string;
    lineNumber: number;
    token: string;
    entropy: number;
    keyword: string;
  }> = [];

  // Keywords that suggest auth secrets
  const authKeywords = /\b(api_?key|secret|token|password|passwd|auth|credential|bearer|private_?key|access_?key)\b/i;
  // Candidate high-entropy tokens: base64-like or hex strings, length 16+
  const tokenPattern = /[A-Za-z0-9+/=_\-]{16,}/g;

  const lines = content.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!;
    if (!authKeywords.test(line)) continue;

    const keyword = line.match(authKeywords)?.[0] ?? "auth";
    const tokens = line.match(tokenPattern) ?? [];
    for (const token of tokens) {
      // Skip obvious non-secrets (all same char, version strings, etc.)
      if (/^[a-z]+$/.test(token) || /^\d+$/.test(token)) continue;
      const entropy = shannonEntropy(token);
      if (entropy >= threshold) {
        results.push({
          path: filePath,
          lineNumber: i + 1,
          token: token.slice(0, 8) + "...[redacted]",
          entropy: Math.round(entropy * 100) / 100,
          keyword,
        });
      }
    }
  }
  return results;
}

export const secretsAnalyzer: AnalyzerModule = {
  name: "secrets",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];
    const root = workspace.rootPath;

    // We'll need file list for scanning rules
    let allFiles: string[] | null = null;
    const getFiles = () => {
      if (!allFiles) allFiles = walkFiles(root, 5);
      return allFiles;
    };

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-SECRETS-001": {
          // Private key blocks
          const privateKeyRegex =
            /-----BEGIN\s+(RSA|EC|OPENSSH|DSA|PGP|ENCRYPTED)\s+PRIVATE\s+KEY-----/;

          const matches: Array<{ path: string; lineNumber: number; key_type: string }> = [];
          const affectedFiles: string[] = [];

          for (const filePath of getFiles()) {
            const hits = scanFileContent(filePath, privateKeyRegex);
            for (const hit of hits) {
              const keyType = hit.match?.match(
                /BEGIN\s+(RSA|EC|OPENSSH|DSA|PGP|ENCRYPTED)\s+PRIVATE/,
              )?.[1] ?? "UNKNOWN";
              matches.push({
                path: filePath.replace(root + "/", ""),
                lineNumber: hit.lineNumber,
                key_type: keyType,
              });
              if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
            }
          }

          if (matches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "private_key_block",
                  records: matches.map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    key_type: m.key_type,
                    detail: `${m.key_type} private key block found at line ${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                matches.map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }

        case "GHA-SECRETS-002": {
          // .env files with secret-like entries
          const envFiles = getFiles().filter(
            (f) =>
              f.endsWith(".env") ||
              f.endsWith(".env.local") ||
              f.endsWith(".env.production") ||
              f.endsWith(".env.development") ||
              /\/\.env(\.[a-z]+)?$/.test(f),
          );

          const matches: Array<{ path: string; lineNumber: number; entry_type: string }> = [];
          const affectedFiles: string[] = [];

          for (const filePath of envFiles) {
            const hits = scanFileContent(filePath, /^[^#\s][A-Z0-9_]*(KEY|SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*\s*=\s*.+$/i);
            for (const hit of hits) {
              // Don't capture the actual value
              const entryType = hit.line.split("=")[0]?.trim() ?? "UNKNOWN";
              matches.push({
                path: filePath.replace(root + "/", ""),
                lineNumber: hit.lineNumber,
                entry_type: entryType,
              });
              if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
            }
          }

          if (matches.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "env_secret_entry",
                records: matches.map((m) => ({
                  path: m.path,
                  line_number: m.lineNumber,
                  entry_key: m.entry_type,
                  detail: `Secret-like entry "${m.entry_type}" found in env file`,
                })),
              },
              affectedFiles,
              matches.map((m) => m.lineNumber),
            );

            // Downgrade example/sample/template env files
            const allExample = affectedFiles.every((f) =>
              /\.(example|sample|template)$/.test(f)
            );
            if (allExample) {
              finding.severity = "info";
              finding.confidence = "low";
            }

            findings.push(finding);
          }
          break;
        }

        case "GHA-SECRETS-003": {
          // Shannon entropy scan near auth keywords
          const ENTROPY_THRESHOLD = 4.0;
          const TEXT_EXTENSIONS = new Set([
            ".ts", ".js", ".py", ".rb", ".go", ".java", ".sh", ".bash",
            ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".conf",
            ".env", ".txt", ".xml", ".properties",
          ]);

          const entropyMatches: Array<{
            path: string;
            lineNumber: number;
            token: string;
            entropy: number;
            keyword: string;
          }> = [];
          const affectedFiles: string[] = [];

          // Limit scan to text-like files
          const textFiles = getFiles().filter((f) => {
            const ext = f.slice(f.lastIndexOf(".")).toLowerCase();
            return TEXT_EXTENSIONS.has(ext);
          });

          for (const filePath of textFiles) {
            const content = readFileContent(filePath, 1048576); // 1MB limit
            if (!content) continue;
            const hits = findHighEntropyNearAuth(content, filePath, ENTROPY_THRESHOLD);
            for (const hit of hits) {
              entropyMatches.push({
                ...hit,
                path: hit.path.replace(root + "/", ""),
              });
              if (!affectedFiles.includes(filePath)) affectedFiles.push(filePath);
            }
          }

          if (entropyMatches.length > 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "high_entropy_near_auth",
                  records: entropyMatches.slice(0, 50).map((m) => ({
                    path: m.path,
                    line_number: m.lineNumber,
                    token_prefix: m.token,
                    entropy: m.entropy,
                    keyword: m.keyword,
                    detail: `High-entropy token (${m.entropy}) near auth keyword "${m.keyword}" in ${m.path}:${m.lineNumber}`,
                  })),
                },
                affectedFiles,
                entropyMatches.slice(0, 50).map((m) => m.lineNumber),
              ),
            );
          }
          break;
        }
      }
    }

    return {
      findings,
      moduleResult: {
        module_name: "secrets",
        status: "success",
        started_at: startedAt,
        completed_at: new Date().toISOString(),
        findings_emitted: findings.length,
        warnings: [],
        errors: [],
      },
    };
  },
};
