export interface RepoMetadata {
  owner: string;
  repo: string;
  description?: string;
  defaultBranch?: string;
  isArchived: boolean;
  isFork: boolean;
  isPrivate: boolean;
  stargazersCount: number;
  forksCount: number;
  pushedAt?: string;
  createdAt?: string;
  topics?: string[];
  license?: string;
  hasSecurityPolicy: boolean;
  hasIssues: boolean;
}

export interface GitHubRelease {
  tagName: string;
  name?: string;
  publishedAt?: string;
  isDraft: boolean;
  isPrerelease: boolean;
  url: string;
}

const BASE = "https://api.github.com";

function authHeaders(): Record<string, string> {
  const token = process.env.GITHUB_TOKEN;
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

async function githubGet(path: string): Promise<unknown | null> {
  const token = process.env.GITHUB_TOKEN;
  if (!token) return null;

  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: {
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        ...authHeaders(),
      },
    });
  } catch (err) {
    console.warn(`[github-api] Request to ${path} failed: ${err}`);
    return null;
  }

  if (!res.ok) {
    console.warn(`[github-api] ${path} returned HTTP ${res.status}`);
    return null;
  }

  try {
    return await res.json();
  } catch (err) {
    console.warn(`[github-api] Failed to parse response from ${path}: ${err}`);
    return null;
  }
}

/**
 * Fetch repository metadata from the GitHub API.
 * Returns null if GITHUB_TOKEN is not set or the request fails.
 */
export async function getRepoMetadata(
  owner: string,
  repo: string,
): Promise<RepoMetadata | null> {
  const data = await githubGet(`/repos/${owner}/${repo}`) as Record<string, unknown> | null;
  if (!data) return null;

  return {
    owner,
    repo,
    description: typeof data.description === "string" ? data.description : undefined,
    defaultBranch: typeof data.default_branch === "string" ? data.default_branch : undefined,
    isArchived: Boolean(data.archived),
    isFork: Boolean(data.fork),
    isPrivate: Boolean(data.private),
    stargazersCount: typeof data.stargazers_count === "number" ? data.stargazers_count : 0,
    forksCount: typeof data.forks_count === "number" ? data.forks_count : 0,
    pushedAt: typeof data.pushed_at === "string" ? data.pushed_at : undefined,
    createdAt: typeof data.created_at === "string" ? data.created_at : undefined,
    topics: Array.isArray(data.topics)
      ? (data.topics as string[])
      : undefined,
    license:
      data.license && typeof (data.license as Record<string, unknown>).spdx_id === "string"
        ? (data.license as Record<string, unknown>).spdx_id as string
        : undefined,
    hasSecurityPolicy: Boolean(data.security_and_analysis),
    hasIssues: Boolean(data.has_issues),
  };
}

/**
 * Check whether a repository is archived.
 * Returns null if GITHUB_TOKEN is not set or the request fails.
 */
export async function checkArchived(
  owner: string,
  repo: string,
): Promise<boolean | null> {
  const data = await githubGet(`/repos/${owner}/${repo}`) as Record<string, unknown> | null;
  if (data === null) return null;
  return Boolean(data.archived);
}

/**
 * Fetch the latest release for a repository.
 * Returns null if GITHUB_TOKEN is not set or the request fails.
 */
export async function getLatestRelease(
  owner: string,
  repo: string,
): Promise<GitHubRelease | null> {
  const data = await githubGet(`/repos/${owner}/${repo}/releases/latest`) as Record<string, unknown> | null;
  if (!data) return null;

  return {
    tagName: typeof data.tag_name === "string" ? data.tag_name : "",
    name: typeof data.name === "string" ? data.name : undefined,
    publishedAt: typeof data.published_at === "string" ? data.published_at : undefined,
    isDraft: Boolean(data.draft),
    isPrerelease: Boolean(data.prerelease),
    url: typeof data.html_url === "string" ? data.html_url : "",
  };
}
