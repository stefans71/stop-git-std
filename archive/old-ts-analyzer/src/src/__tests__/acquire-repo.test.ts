import { test, expect, describe } from "bun:test";
import { classifyTarget, collectGitMetadata } from "../inventory/acquire-repo.ts";

describe("classifyTarget", () => {
  describe("local paths", () => {
    test("returns local for absolute path", () => {
      expect(classifyTarget("/home/user/myrepo")).toBe("local");
    });

    test("returns local for relative path", () => {
      expect(classifyTarget("./myrepo")).toBe("local");
    });

    test("returns local for bare directory name", () => {
      expect(classifyTarget("myrepo")).toBe("local");
    });

    test("returns local for /tmp path", () => {
      expect(classifyTarget("/tmp/some-repo")).toBe("local");
    });
  });

  describe("GitHub URLs", () => {
    test("returns github for https://github.com URL", () => {
      expect(classifyTarget("https://github.com/owner/repo")).toBe("github");
    });

    test("returns github for https://github.com URL with .git suffix", () => {
      expect(classifyTarget("https://github.com/owner/repo.git")).toBe("github");
    });

    test("returns github for git@github.com SSH URL", () => {
      expect(classifyTarget("git@github.com:owner/repo.git")).toBe("github");
    });

    test("returns github for git@github.com without .git suffix", () => {
      expect(classifyTarget("git@github.com:owner/repo")).toBe("github");
    });
  });

  describe("generic git URLs", () => {
    test("returns git for non-GitHub https URL", () => {
      expect(classifyTarget("https://gitlab.com/owner/repo.git")).toBe("git");
    });

    test("returns git for git:// protocol", () => {
      expect(classifyTarget("git://bitbucket.org/owner/repo.git")).toBe("git");
    });

    test("returns git for non-GitHub SSH URL", () => {
      expect(classifyTarget("git@bitbucket.org:owner/repo.git")).toBe("git");
    });

    test("returns git for self-hosted https URL", () => {
      expect(classifyTarget("https://mygitserver.internal/org/repo")).toBe("git");
    });
  });
});

describe("collectGitMetadata", () => {
  const repoPath = process.cwd();

  test("returns an object with lastCommitDate, contributors, and tags", async () => {
    const meta = await collectGitMetadata(repoPath);
    expect(meta).toBeDefined();
    expect(meta).toHaveProperty("lastCommitDate");
    expect(meta).toHaveProperty("contributors");
    expect(meta).toHaveProperty("tags");
    expect(meta).toHaveProperty("signedTags");
  });

  test("lastCommitDate is a string or null", async () => {
    const meta = await collectGitMetadata(repoPath);
    expect(meta.lastCommitDate === null || typeof meta.lastCommitDate === "string").toBe(true);
  });

  test("lastCommitDate is a non-empty string for a git repo", async () => {
    const meta = await collectGitMetadata(repoPath);
    // The current working directory is a git repo, so we expect a date
    expect(typeof meta.lastCommitDate).toBe("string");
    expect((meta.lastCommitDate as string).length).toBeGreaterThan(0);
  });

  test("contributors is an array of strings", async () => {
    const meta = await collectGitMetadata(repoPath);
    expect(Array.isArray(meta.contributors)).toBe(true);
    for (const c of meta.contributors) {
      expect(typeof c).toBe("string");
    }
  });

  test("contributors contains at least one entry for a repo with commits", async () => {
    const meta = await collectGitMetadata(repoPath);
    expect(meta.contributors.length).toBeGreaterThan(0);
  });

  test("tags is an array", async () => {
    const meta = await collectGitMetadata(repoPath);
    expect(Array.isArray(meta.tags)).toBe(true);
  });

  test("signedTags is an array", async () => {
    const meta = await collectGitMetadata(repoPath);
    expect(Array.isArray(meta.signedTags)).toBe(true);
  });

  test("contributors are deduplicated (no duplicates)", async () => {
    const meta = await collectGitMetadata(repoPath);
    const unique = new Set(meta.contributors);
    expect(unique.size).toBe(meta.contributors.length);
  });
});
