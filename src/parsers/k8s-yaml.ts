import { readFile } from "node:fs/promises";
import { parse as parseYaml } from "yaml";

export interface K8sResource {
  readonly path: string;
  readonly apiVersion?: string;
  readonly kind?: string;
  readonly metadata?: { readonly name?: string; readonly namespace?: string };
  readonly raw: Record<string, unknown>;
}

export async function parseK8sYaml(filePath: string): Promise<readonly K8sResource[]> {
  try {
    const content = await readFile(filePath, "utf-8");
    // K8s files can contain multiple documents
    const docs = content.split(/^---$/m).filter((d) => d.trim());
    const resources: K8sResource[] = [];

    for (const doc of docs) {
      const parsed = parseYaml(doc) as Record<string, unknown> | null;
      if (!parsed || typeof parsed !== "object") continue;

      if (parsed.apiVersion && parsed.kind) {
        resources.push({
          path: filePath,
          apiVersion: parsed.apiVersion as string,
          kind: parsed.kind as string,
          metadata: parsed.metadata as { name?: string; namespace?: string } | undefined,
          raw: parsed,
        });
      }
    }

    return resources;
  } catch {
    return [];
  }
}
