export interface GitHubRepoInfo {
  readonly owner: string;
  readonly repo: string;
  readonly archived: boolean;
  readonly stargazersCount: number;
  readonly forksCount: number;
  readonly openIssuesCount: number;
  readonly license?: string;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly pushedAt: string;
  readonly defaultBranch: string;
}

export interface GitHubContributor {
  readonly login: string;
  readonly contributions: number;
}

/**
 * Fetch repository metadata from the GitHub API.
 * Requires GITHUB_TOKEN env var for authenticated requests.
 */
export async function fetchRepoInfo(
  owner: string,
  repo: string,
): Promise<GitHubRepoInfo | null> {
  const token = process.env.GITHUB_TOKEN;
  const headers: Record<string, string> = {
    Accept: "application/vnd.github.v3+json",
    "User-Agent": "stop-git-std",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}`,
      { headers },
    );
    if (!response.ok) return null;

    const data = (await response.json()) as Record<string, unknown>;
    return {
      owner,
      repo,
      archived: data.archived as boolean,
      stargazersCount: data.stargazers_count as number,
      forksCount: data.forks_count as number,
      openIssuesCount: data.open_issues_count as number,
      license: (data.license as Record<string, string> | null)?.spdx_id,
      createdAt: data.created_at as string,
      updatedAt: data.updated_at as string,
      pushedAt: data.pushed_at as string,
      defaultBranch: data.default_branch as string,
    };
  } catch {
    return null;
  }
}

export async function fetchContributors(
  owner: string,
  repo: string,
): Promise<readonly GitHubContributor[]> {
  const token = process.env.GITHUB_TOKEN;
  const headers: Record<string, string> = {
    Accept: "application/vnd.github.v3+json",
    "User-Agent": "stop-git-std",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/contributors?per_page=10`,
      { headers },
    );
    if (!response.ok) return [];

    const data = (await response.json()) as Record<string, unknown>[];
    return data.map((c) => ({
      login: c.login as string,
      contributions: c.contributions as number,
    }));
  } catch {
    return [];
  }
}
