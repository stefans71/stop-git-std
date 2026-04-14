import { Command, Option } from "commander";
import { AuditRequestSchema } from "./models/audit-request.ts";
import { runAudit } from "./engine/run-audit.ts";

const program = new Command()
  .name("stop-git-std")
  .description("Git repository safety auditor")
  .argument("<repo>", "Repository path or URL")
  .option("--ref <ref>", "Git ref to audit", "default_branch")
  .option("--env <environment>", "Target environment", "offline_analysis")
  .option("--policy <profile>", "Policy profile", "balanced")
  .option("--format <formats...>", "Output formats", ["json", "markdown"])
  .option("--output-dir <dir>", "Output directory")
  .option("--include <paths...>", "Include path patterns")
  .option("--exclude <paths...>", "Exclude path patterns")
  .option("--enable-module <modules...>", "Force-enable modules")
  .option("--disable-module <modules...>", "Force-disable modules")
  .option("--runtime-mode <mode>", "Runtime validation mode", "off")
  .option("--adoption-mode <mode>", "Adoption context", "third_party")
  .addOption(
    new Option("--skip-stage2", "Suppress stage 2 analysis recommendations"),
  )
  .addOption(
    new Option("--quick", "Skip AST analysis (regex-only)").conflicts(["deep"]),
  )
  .addOption(
    new Option("--deep", "Force AST analysis on all findings").conflicts(["quick"]),
  );

export async function main(): Promise<number> {
  program.parse();
  const opts = program.opts();
  const [repoTarget] = program.args;

  if (!repoTarget) {
    program.help();
    return 1;
  }

  const request = AuditRequestSchema.parse({
    repo_target: repoTarget,
    ref: opts.ref,
    target_environment: opts.env,
    policy_profile: opts.policy,
    output_formats: opts.format,
    include_paths: opts.include ?? [],
    exclude_paths: opts.exclude,
    enabled_modules: opts.enableModule ?? [],
    disabled_modules: opts.disableModule ?? [],
    runtime_mode: opts.runtimeMode,
    adoption_mode: opts.adoptionMode,
    skip_stage2: opts.skipStage2 || opts.quick || false,
    depth_mode: opts.deep ? "deep" : opts.quick ? "quick" : "auto",
  });

  const result = await runAudit(request);

  const exitCodeMap = { PROCEED: 0, PROCEED_WITH_CONSTRAINTS: 0, ABORT: 1, CAUTION: 2 } as const;
  return exitCodeMap[result.decision.value];
}

main()
  .then((code) => process.exit(code))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
