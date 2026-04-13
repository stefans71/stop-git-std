export interface GitMetadata {
  lastCommitDate: string | null;
  contributors: string[];
  tags: string[];
  signedTags: string[];
}

export interface LocalWorkspace {
  rootPath: string;
  gitMetadata: GitMetadata;
  isLocal: boolean;
}
