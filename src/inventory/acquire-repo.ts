import { stat } from "node:fs/promises";
import { resolve } from "node:path";

export interface AcquireResult {
  readonly repoPath: string;
  readonly isLocal: boolean;
}

export async function acquireRepo(target: string): Promise<AcquireResult> {
  // For MVP, only support local paths
  const repoPath = resolve(target);

  const stats = await stat(repoPath).catch(() => null);
  if (!stats?.isDirectory()) {
    throw new Error(`Target is not a directory: ${repoPath}`);
  }

  // Verify it looks like a git repo
  const gitDir = await stat(resolve(repoPath, ".git")).catch(() => null);
  if (!gitDir) {
    throw new Error(`Target does not appear to be a git repository: ${repoPath}`);
  }

  return { repoPath, isLocal: true };
}
