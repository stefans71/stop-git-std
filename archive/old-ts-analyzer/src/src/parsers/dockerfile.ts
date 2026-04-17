export interface DockerfileFrom {
  image: string;
  tag?: string;
  digest?: string;
  alias?: string;
}

export interface DockerfileRun {
  command: string;
  lineNumber: number;
}

export interface DockerfileUser {
  user: string;
  lineNumber: number;
}

export interface ParsedDockerfile {
  froms: DockerfileFrom[];
  users: DockerfileUser[];
  runs: DockerfileRun[];
  /** Exposes declared ports */
  exposes: string[];
  /** ENV declarations as key=value pairs */
  envVars: Record<string, string>;
  /** ADD/COPY directives (source) */
  copies: string[];
  /** Raw lines */
  lines: string[];
}

/**
 * Parse a Dockerfile line-by-line, extracting FROM, USER, RUN, EXPOSE, ENV,
 * COPY/ADD directives.
 */
export function parseDockerfile(content: string): ParsedDockerfile {
  const lines = content.split(/\r?\n/);
  const result: ParsedDockerfile = {
    froms: [],
    users: [],
    runs: [],
    exposes: [],
    envVars: {},
    copies: [],
    lines,
  };

  let i = 0;
  while (i < lines.length) {
    // Handle line continuations
    const rawLine = lines[i];
    if (rawLine === undefined) { i++; continue; }
    let line = rawLine.trim();
    while (line.endsWith("\\") && i + 1 < lines.length) {
      i++;
      const nextLine = lines[i];
      line = line.slice(0, -1).trim() + " " + (nextLine ?? "").trim();
    }

    // Skip comments and empty lines
    if (!line || line.startsWith("#")) {
      i++;
      continue;
    }

    const upper = line.toUpperCase();
    const lineNumber = i + 1;

    if (upper.startsWith("FROM ")) {
      const rest = line.slice(5).trim();
      // Handle: image:tag[@digest] [AS alias]
      const asMatch = rest.match(/^(.+?)\s+AS\s+(\S+)$/i);
      const imageStr = asMatch ? (asMatch[1] ?? rest).trim() : rest;
      const alias = asMatch ? asMatch[2] : undefined;

      const digestIdx = imageStr.indexOf("@");
      if (digestIdx !== -1) {
        const image = imageStr.slice(0, digestIdx);
        const digest = imageStr.slice(digestIdx + 1);
        result.froms.push({ image, digest, alias });
      } else {
        const colonIdx = imageStr.lastIndexOf(":");
        if (colonIdx !== -1) {
          const image = imageStr.slice(0, colonIdx);
          const tag = imageStr.slice(colonIdx + 1);
          result.froms.push({ image, tag, alias });
        } else {
          result.froms.push({ image: imageStr, alias });
        }
      }
    } else if (upper.startsWith("USER ")) {
      result.users.push({ user: line.slice(5).trim(), lineNumber });
    } else if (upper.startsWith("RUN ")) {
      result.runs.push({ command: line.slice(4).trim(), lineNumber });
    } else if (upper.startsWith("EXPOSE ")) {
      const ports = line.slice(7).trim().split(/\s+/);
      result.exposes.push(...ports);
    } else if (upper.startsWith("ENV ")) {
      const rest = line.slice(4).trim();
      // Two forms: ENV KEY=VALUE ... and ENV KEY VALUE
      const eqIdx = rest.indexOf("=");
      if (eqIdx !== -1) {
        // Could be multiple KEY=VALUE pairs
        const pairs = rest.match(/(\w+)=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\S+)/g) ?? [];
        for (const pair of pairs) {
          const idx = pair.indexOf("=");
          const key = pair.slice(0, idx);
          const val = pair.slice(idx + 1).replace(/^["']|["']$/g, "");
          result.envVars[key] = val;
        }
      } else {
        const spaceIdx = rest.indexOf(" ");
        if (spaceIdx !== -1) {
          const key = rest.slice(0, spaceIdx);
          const val = rest.slice(spaceIdx + 1).trim();
          result.envVars[key] = val;
        }
      }
    } else if (upper.startsWith("COPY ") || upper.startsWith("ADD ")) {
      const rest = line.slice(upper.startsWith("ADD") ? 4 : 5).trim();
      // First token is source (skip --chown= or --from= flags)
      const tokens = rest.split(/\s+/).filter((t) => !t.startsWith("--"));
      const firstToken = tokens[0];
      if (tokens.length >= 2 && firstToken !== undefined) {
        result.copies.push(firstToken);
      }
    }

    i++;
  }

  return result;
}
