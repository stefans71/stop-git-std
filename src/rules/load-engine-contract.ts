import { readFile } from "node:fs/promises";
import { parse as parseYaml } from "yaml";

export interface PipelineStage {
  readonly name: string;
  readonly description: string;
  readonly input: string | readonly string[];
  readonly output: string | readonly string[];
}

export interface BackendDefinition {
  readonly name: string;
  readonly description: string;
  readonly status: string;
}

export interface EngineContract {
  readonly pipeline: { readonly stages: readonly PipelineStage[] };
  readonly analyzer: {
    readonly backends: readonly BackendDefinition[];
  };
  readonly categories: {
    readonly universal: readonly string[];
    readonly typed: readonly string[];
  };
}

export async function loadEngineContract(path: string): Promise<EngineContract> {
  const content = await readFile(path, "utf-8");
  const parsed = parseYaml(content) as EngineContract;
  return parsed;
}
