import { existsSync } from "fs";
import { emitFinding, readFileContent } from "../base.ts";
import type { AnalyzerModule, AnalyzerOutput } from "../../plugins/analyzer-backend.ts";
import type { Finding } from "../../models/finding.ts";

export const governanceTrustAnalyzer: AnalyzerModule = {
  name: "governance_trust",

  async analyze(workspace, _profile, _context, rules): Promise<AnalyzerOutput> {
    const startedAt = new Date().toISOString();
    const findings: Finding[] = [];
    const root = workspace.rootPath;

    for (const rule of rules) {
      switch (rule.id) {
        case "GHA-TRUST-001": {
          // Check SECURITY.md or .github/SECURITY.md exists
          const paths = [
            `${root}/SECURITY.md`,
            `${root}/.github/SECURITY.md`,
          ];
          const found = paths.some((p) => existsSync(p));
          if (!found) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "file_absence",
                  records: [
                    {
                      checked_paths: paths.map((p) => p.replace(root + "/", "")),
                      detail: "No SECURITY.md found in root or .github/",
                    },
                  ],
                },
                [],
              ),
            );
          }
          break;
        }

        case "GHA-TRUST-002": {
          // Check CODEOWNERS or .github/CODEOWNERS exists
          const paths = [
            `${root}/CODEOWNERS`,
            `${root}/.github/CODEOWNERS`,
            `${root}/docs/CODEOWNERS`,
          ];
          const found = paths.some((p) => existsSync(p));
          if (!found) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "file_absence",
                  records: [
                    {
                      checked_paths: paths.map((p) => p.replace(root + "/", "")),
                      detail: "No CODEOWNERS found in root, .github/, or docs/",
                    },
                  ],
                },
                [],
              ),
            );
          }
          break;
        }

        case "GHA-TRUST-003": {
          // Check last commit date — stale if > 18 months ago
          const lastCommit = workspace.gitMetadata.lastCommitDate;
          if (lastCommit) {
            const lastCommitMs = new Date(lastCommit).getTime();
            const eighteenMonthsMs = 18 * 30 * 24 * 60 * 60 * 1000;
            const ageMs = Date.now() - lastCommitMs;
            if (ageMs > eighteenMonthsMs) {
              const ageDays = Math.floor(ageMs / (24 * 60 * 60 * 1000));
              findings.push(
                emitFinding(
                  rule,
                  {
                    type: "git_metadata",
                    records: [
                      {
                        last_commit_date: lastCommit,
                        age_days: ageDays,
                        threshold_days: 18 * 30,
                        detail: `Repository last committed ${ageDays} days ago (> 18 months)`,
                      },
                    ],
                  },
                  [],
                ),
              );
            }
          }
          break;
        }

        case "GHA-TRUST-004": {
          // Check signed tags: total tags > 0 but signed = 0
          const totalTags = workspace.gitMetadata.tags.length;
          const signedTags = workspace.gitMetadata.signedTags.length;
          if (totalTags > 0 && signedTags === 0) {
            findings.push(
              emitFinding(
                rule,
                {
                  type: "git_metadata",
                  records: [
                    {
                      total_tags: totalTags,
                      signed_tags: signedTags,
                      tags_sample: workspace.gitMetadata.tags.slice(0, 5),
                      detail: `${totalTags} tags found but none are signed`,
                    },
                  ],
                },
                [],
              ),
            );
          }
          break;
        }

        case "GHA-TRUST-005": {
          // Analyze git log for contributor shift in sensitive paths last 30 days
          const sensitivePaths = [
            "package.json",
            ".github/workflows",
            "Dockerfile",
            "docker-compose",
            ".env",
            "requirements.txt",
            "pyproject.toml",
            "Makefile",
            "scripts/",
          ];

          try {
            const since = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
              .toISOString()
              .split("T")[0]!;

            const result = Bun.spawnSync(
              [
                "git",
                "log",
                `--since=${since}`,
                "--pretty=format:%ae",
                "--name-only",
                "--",
                ...sensitivePaths,
              ],
              { cwd: root, stderr: "pipe" },
            );

            if (result.exitCode === 0) {
              const output = new TextDecoder().decode(result.stdout);
              const lines = output.split("\n").filter((l) => l.trim() !== "");

              // Parse: email lines followed by file lines (blank-separated commits)
              const emailRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
              const commitsByAuthor: Record<string, number> = {};
              let currentAuthor = "";
              let totalCommits = 0;

              for (const line of lines) {
                if (emailRegex.test(line.trim())) {
                  currentAuthor = line.trim().toLowerCase();
                  commitsByAuthor[currentAuthor] =
                    (commitsByAuthor[currentAuthor] ?? 0) + 1;
                  totalCommits++;
                }
              }

              if (totalCommits > 3) {
                for (const [author, count] of Object.entries(commitsByAuthor)) {
                  const ratio = count / totalCommits;
                  if (ratio > 0.6 && totalCommits > 3) {
                    findings.push(
                      emitFinding(
                        rule,
                        {
                          type: "contributor_shift",
                          records: [
                            {
                              author,
                              commit_count: count,
                              total_sensitive_commits: totalCommits,
                              ratio: Math.round(ratio * 100) / 100,
                              window_days: 30,
                              detail: `Author ${author} accounts for ${Math.round(ratio * 100)}% of sensitive-path commits in last 30 days`,
                            },
                          ],
                        },
                        [],
                      ),
                    );
                    break; // emit once per rule trigger
                  }
                }
              }
            }
          } catch {
            // git not available or not a git repo — skip silently
          }
          break;
        }
      }
    }

    return {
      findings,
      moduleResult: {
        module_name: "governance_trust",
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
