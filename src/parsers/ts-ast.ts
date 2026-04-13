import { readFile } from "node:fs/promises";

export interface SimpleMatch {
  readonly file: string;
  readonly line: number;
  readonly snippet: string;
}

/**
 * Simple pattern-based search in TypeScript/JavaScript files.
 * Not a full AST parser — uses regex matching for MVP.
 * A proper AST parser (e.g., ts-morph) can be added later.
 */
export async function searchFileContent(
  filePath: string,
  pattern: RegExp,
): Promise<readonly SimpleMatch[]> {
  try {
    const content = await readFile(filePath, "utf-8");
    const lines = content.split("\n");
    const matches: SimpleMatch[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]!;
      if (pattern.test(line)) {
        matches.push({
          file: filePath,
          line: i + 1,
          snippet: line.trim(),
        });
      }
    }

    return matches;
  } catch {
    return [];
  }
}

export async function fileContainsPattern(filePath: string, pattern: RegExp): Promise<boolean> {
  try {
    const content = await readFile(filePath, "utf-8");
    return pattern.test(content);
  } catch {
    return false;
  }
}
