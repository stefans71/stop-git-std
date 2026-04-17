import { readFileSync } from "fs";
import { parse as parseYaml } from "yaml";
import { EngineContractSchema, type EngineContract } from "./types.ts";

export function loadEngineContract(path?: string): EngineContract {
  const resolvedPath = path ?? new URL("../../docs/engine-contract.yaml", import.meta.url).pathname;
  const text = readFileSync(resolvedPath, "utf-8");
  const parsed = parseYaml(text);
  return EngineContractSchema.parse(parsed);
}
