import { existsSync, mkdirSync } from "fs";
import type { AuditContext } from "../models/audit-context.ts";
import type { LocalWorkspace, GitMetadata } from "../models/local-workspace.ts";

export function classifyTarget(repoTarget: string): "local" | "github" | "git" {
  if (repoTarget.startsWith("https://github.com") || repoTarget.startsWith("git@github.com")) {
    return "github";
  }
  if (repoTarget.startsWith("https://") || repoTarget.startsWith("git://") || repoTarget.startsWith("git@")) {
    return "git";
  }
  return "local";
}

export async function cloneRepo(
  url: string,
  ref: string,
  destDir: string,
  depth?: number,
): Promise<void> {
  mkdirSync(destDir, { recursive: true });
  const args = ["clone", "--depth", String(depth ?? 1)];
  if (ref !== "default_branch") {
    args.push("--branch", ref);
  }
  args.push(url, destDir);
  const proc = Bun.spawn(["git", ...args], { stdout: "pipe", stderr: "pipe" });
  const exitCode = await proc.exited;
  if (exitCode !== 0) {
    const stderr = await new Response(proc.stderr).text();
    throw new Error(`git clone failed (exit ${exitCode}): ${stderr}`);
  }
}

export async function collectGitMetadata(repoPath: string): Promise<GitMetadata> {
  const run = async (args: string[]): Promise<string> => {
    const proc = Bun.spawn(["git", ...args], { cwd: repoPath, stdout: "pipe", stderr: "pipe" });
    await proc.exited;
    return new Response(proc.stdout).text();
  };

  const lastCommitRaw = (await run(["log", "-1", "--format=%aI"])).trim();
  const lastCommitDate = lastCommitRaw || null;

  const contributorsRaw = await run(["log", "--format=%ae"]);
  const contributors = [...new Set(contributorsRaw.trim().split("\n").filter(Boolean))];

  const tagsRaw = await run(["tag", "-l"]);
  const tags = tagsRaw.trim().split("\n").filter(Boolean);

  const signedTags: string[] = [];
  for (const tag of tags) {
    const verifyProc = Bun.spawn(["git", "tag", "-v", tag], {
      cwd: repoPath,
      stdout: "pipe",
      stderr: "pipe",
    });
    const code = await verifyProc.exited;
    if (code === 0) signedTags.push(tag);
  }

  return { lastCommitDate, contributors, tags, signedTags };
}

export async function acquireRepo(
  context: AuditContext,
  runId: string,
): Promise<LocalWorkspace> {
  const targetType = classifyTarget(context.repo_target);

  let rootPath: string;
  let isLocal: boolean;

  if (targetType === "local") {
    rootPath = context.repo_target;
    isLocal = true;
    if (!existsSync(rootPath)) {
      throw new Error(`Local path does not exist: ${rootPath}`);
    }
  } else {
    rootPath = `/tmp/stop-git-std/${runId}`;
    isLocal = false;
    await cloneRepo(context.repo_target, context.ref, rootPath);
  }

  const gitMetadata = await collectGitMetadata(rootPath);

  return { rootPath, gitMetadata, isLocal };
}
