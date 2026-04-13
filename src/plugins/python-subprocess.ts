import type { Finding } from "../models/finding.ts";
import type { AnalyzerBackend, AnalyzerInput } from "./analyzer-backend.ts";

/**
 * Python subprocess analyzer backend — STUB for MVP.
 *
 * This backend is designed but not implemented in the MVP.
 * It defines the interface for running Python-based analyzers
 * via subprocess, receiving JSON findings back.
 *
 * Future implementation will:
 * 1. Spawn a Python subprocess
 * 2. Pass AnalyzerInput as JSON via stdin
 * 3. Receive Finding[] as JSON via stdout
 * 4. Handle timeouts and errors
 */
export function createPythonSubprocessBackend(): AnalyzerBackend {
  return {
    name: "python-subprocess",
    type: "python-subprocess",

    async analyze(_input: AnalyzerInput): Promise<readonly Finding[]> {
      // Stub: Python subprocess analyzers are not implemented in MVP
      // When implemented, this will:
      // 1. Serialize input to JSON
      // 2. Spawn python3 with the analyzer script
      // 3. Parse JSON output as Finding[]
      return [];
    },
  };
}
