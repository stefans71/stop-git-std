import { readFile } from "node:fs/promises";

export interface DockerInstruction {
  readonly instruction: string;
  readonly args: string;
  readonly line: number;
}

export interface DockerfileData {
  readonly path: string;
  readonly instructions: readonly DockerInstruction[];
  readonly baseImages: readonly string[];
  readonly hasUserDirective: boolean;
  readonly exposedPorts: readonly string[];
}

export async function parseDockerfile(filePath: string): Promise<DockerfileData | null> {
  try {
    const content = await readFile(filePath, "utf-8");
    const lines = content.split("\n");
    const instructions: DockerInstruction[] = [];
    const baseImages: string[] = [];
    let hasUserDirective = false;
    const exposedPorts: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]!.trim();
      if (!line || line.startsWith("#")) continue;

      const match = line.match(/^(\w+)\s+(.*)/);
      if (!match) continue;

      const instruction = match[1]!.toUpperCase();
      const args = match[2]!;
      instructions.push({ instruction, args, line: i + 1 });

      if (instruction === "FROM") {
        baseImages.push(args.split(/\s+/)[0]!);
      } else if (instruction === "USER") {
        hasUserDirective = true;
      } else if (instruction === "EXPOSE") {
        exposedPorts.push(args);
      }
    }

    return { path: filePath, instructions, baseImages, hasUserDirective, exposedPorts };
  } catch {
    return null;
  }
}
