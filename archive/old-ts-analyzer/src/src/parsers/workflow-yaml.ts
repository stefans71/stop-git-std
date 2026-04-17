import { parse as parseYaml } from "yaml";

export interface WorkflowTrigger {
  event: string;
  config: unknown;
}

export interface WorkflowPermissions {
  [scope: string]: string;
}

export interface WorkflowStep {
  id?: string;
  name?: string;
  uses?: string;
  run?: string;
  with?: Record<string, unknown>;
  env?: Record<string, string>;
  if?: string;
}

export interface WorkflowJob {
  id: string;
  name?: string;
  runsOn?: string | string[];
  permissions?: WorkflowPermissions;
  steps: WorkflowStep[];
  needs?: string | string[];
  environment?: string | { name: string; url?: string };
}

export interface ParsedWorkflow {
  name?: string;
  triggers: WorkflowTrigger[];
  jobs: WorkflowJob[];
  permissions?: WorkflowPermissions;
  env?: Record<string, string>;
  raw: Record<string, unknown>;
}

function toStringRecord(val: unknown): Record<string, string> {
  if (!val || typeof val !== "object" || Array.isArray(val)) return {};
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(val as Record<string, unknown>)) {
    out[k] = String(v);
  }
  return out;
}

function parseStep(raw: unknown): WorkflowStep {
  if (!raw || typeof raw !== "object") return {};
  const r = raw as Record<string, unknown>;
  return {
    id: typeof r.id === "string" ? r.id : undefined,
    name: typeof r.name === "string" ? r.name : undefined,
    uses: typeof r.uses === "string" ? r.uses : undefined,
    run: typeof r.run === "string" ? r.run : undefined,
    with:
      r.with && typeof r.with === "object"
        ? (r.with as Record<string, unknown>)
        : undefined,
    env: toStringRecord(r.env),
    if: typeof r.if === "string" ? r.if : undefined,
  };
}

/**
 * Parse a GitHub Actions workflow YAML file.
 */
export function parseWorkflowYaml(content: string): ParsedWorkflow {
  let raw: Record<string, unknown>;
  try {
    raw = parseYaml(content) as Record<string, unknown>;
  } catch {
    raw = {};
  }

  // ── Triggers (on:) ──────────────────────────────────────────────────────────
  const triggers: WorkflowTrigger[] = [];
  const onBlock = raw.on ?? raw.true; // YAML may parse `on` as `true` in some parsers
  if (onBlock) {
    if (typeof onBlock === "string") {
      triggers.push({ event: onBlock, config: null });
    } else if (Array.isArray(onBlock)) {
      for (const ev of onBlock) {
        triggers.push({ event: String(ev), config: null });
      }
    } else if (typeof onBlock === "object") {
      for (const [event, config] of Object.entries(onBlock as Record<string, unknown>)) {
        triggers.push({ event, config });
      }
    }
  }

  // ── Jobs ────────────────────────────────────────────────────────────────────
  const jobs: WorkflowJob[] = [];
  const jobsBlock = raw.jobs;
  if (jobsBlock && typeof jobsBlock === "object" && !Array.isArray(jobsBlock)) {
    for (const [jobId, jobDef] of Object.entries(jobsBlock as Record<string, unknown>)) {
      if (!jobDef || typeof jobDef !== "object") continue;
      const j = jobDef as Record<string, unknown>;
      const steps = Array.isArray(j.steps) ? j.steps.map(parseStep) : [];
      jobs.push({
        id: jobId,
        name: typeof j.name === "string" ? j.name : undefined,
        runsOn: (j["runs-on"] as string | string[] | undefined) ?? undefined,
        permissions: j.permissions
          ? toStringRecord(j.permissions)
          : undefined,
        steps,
        needs: (j.needs as string | string[] | undefined) ?? undefined,
        environment: (j.environment as WorkflowJob["environment"]) ?? undefined,
      });
    }
  }

  return {
    name: typeof raw.name === "string" ? raw.name : undefined,
    triggers,
    jobs,
    permissions: raw.permissions ? toStringRecord(raw.permissions) : undefined,
    env: raw.env ? toStringRecord(raw.env) : undefined,
    raw,
  };
}
