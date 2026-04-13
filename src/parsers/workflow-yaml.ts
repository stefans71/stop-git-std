import { readFile } from "node:fs/promises";
import { parse as parseYaml } from "yaml";

export interface WorkflowTrigger {
  readonly event: string;
  readonly config?: unknown;
}

export interface WorkflowStep {
  readonly name?: string;
  readonly uses?: string;
  readonly run?: string;
  readonly with?: Readonly<Record<string, unknown>>;
  readonly env?: Readonly<Record<string, string>>;
}

export interface WorkflowJob {
  readonly name?: string;
  readonly runsOn?: string;
  readonly permissions?: unknown;
  readonly steps: readonly WorkflowStep[];
}

export interface WorkflowFile {
  readonly path: string;
  readonly name?: string;
  readonly triggers: readonly WorkflowTrigger[];
  readonly permissions?: unknown;
  readonly jobs: ReadonlyMap<string, WorkflowJob>;
}

export async function parseWorkflowYaml(filePath: string): Promise<WorkflowFile | null> {
  try {
    const content = await readFile(filePath, "utf-8");
    const parsed = parseYaml(content) as Record<string, unknown>;

    const triggers: WorkflowTrigger[] = [];
    const on = parsed.on ?? parsed.true; // YAML parses `on:` as `true:` sometimes
    if (on && typeof on === "object") {
      for (const [event, config] of Object.entries(on as Record<string, unknown>)) {
        triggers.push({ event, config });
      }
    } else if (typeof on === "string") {
      triggers.push({ event: on });
    }

    const jobs = new Map<string, WorkflowJob>();
    const rawJobs = parsed.jobs as Record<string, Record<string, unknown>> | undefined;
    if (rawJobs) {
      for (const [jobId, jobDef] of Object.entries(rawJobs)) {
        const steps = ((jobDef.steps as Record<string, unknown>[]) ?? []).map((s) => ({
          name: s.name as string | undefined,
          uses: s.uses as string | undefined,
          run: s.run as string | undefined,
          with: s.with as Record<string, unknown> | undefined,
          env: s.env as Record<string, string> | undefined,
        }));
        jobs.set(jobId, {
          name: jobDef.name as string | undefined,
          runsOn: (jobDef["runs-on"] as string) ?? undefined,
          permissions: jobDef.permissions,
          steps,
        });
      }
    }

    return {
      path: filePath,
      name: parsed.name as string | undefined,
      triggers,
      permissions: parsed.permissions,
      jobs,
    };
  } catch {
    return null;
  }
}
