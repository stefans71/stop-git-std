# Plan Modifications — Code Snippets for Board Review

Based on board plan review feedback (all 3 agents: APPROVE WITH MODIFICATIONS), here are the exact code changes for each modification.

---

## MOD 1: Threshold ABORT path also needs constraints

**File:** `src/engine/policy.ts:141-154`

```typescript
// BEFORE:
  if (
    !profileConfig.thresholds.abort.disabled &&
    meetsThreshold(scores, findings, profileConfig.thresholds.abort, runtimeFindings)
  ) {
    return {
      value: "ABORT",
      reasons: [
        `Abort threshold exceeded: exploitability=${scores.exploitability}, abuse_potential=${scores.abuse_potential}`,
      ],
      constraints: [],
      hard_stop_triggered: false,
      manual_review_required: true,
    };
  }

// AFTER:
  if (
    !profileConfig.thresholds.abort.disabled &&
    meetsThreshold(scores, findings, profileConfig.thresholds.abort, runtimeFindings)
  ) {
    const constraints = generateConstraints(active);
    constraints.push("After applying fixes, re-run stop-git-std to verify resolution.");
    return {
      value: "ABORT",
      reasons: [
        `Abort threshold exceeded: exploitability=${scores.exploitability}, abuse_potential=${scores.abuse_potential}`,
      ],
      constraints,
      hard_stop_triggered: false,
      manual_review_required: true,
    };
  }
```

---

## MOD 2: Refine non-code file filter — confidence downgrade for `.json`/`.yaml` instead of skip

**File:** `src/analyzers/base.ts` — add after line 81:

```typescript
// Non-code file classification for typed analyzers
const DOC_EXTENSIONS = new Set([".md", ".txt", ".rst", ".adoc"]);
const CONFIG_EXTENSIONS = new Set([".json", ".yaml", ".yml"]);
const TEST_PATTERNS = [/__tests__\//, /\.test\.[jt]sx?$/, /\.spec\.[jt]sx?$/, /\/tests?\//, /\/fixtures?\//];

export type FileClassification = "code" | "doc" | "config" | "test";

export function classifyFile(filePath: string): FileClassification {
  const ext = "." + (filePath.split(".").pop()?.toLowerCase() ?? "");
  if (DOC_EXTENSIONS.has(ext)) return "doc";
  if (CONFIG_EXTENSIONS.has(ext)) return "config";
  if (TEST_PATTERNS.some((p) => p.test(filePath))) return "test";
  return "code";
}

export function isNonCodeFile(filePath: string): boolean {
  return classifyFile(filePath) !== "code";
}
```

**File:** `src/analyzers/typed/ai-llm.ts` — change after line 30:

```typescript
// BEFORE:
    let allFiles: string[] = [];
    try {
      allFiles = walkFiles(workspace.rootPath);
    } catch {
      // workspace not accessible
    }

// AFTER:
    import { classifyFile } from "../base.ts";  // add to top imports

    let allFiles: string[] = [];
    try {
      allFiles = walkFiles(workspace.rootPath);
    } catch {
      // workspace not accessible
    }
    // Typed analyzers: skip docs/tests entirely, keep config files for scanning
    // but any findings from config/test files get confidence downgraded to "low"
    const codeFiles = allFiles.filter((f) => classifyFile(f) === "code" || classifyFile(f) === "config");
```

Then in each scan loop, after `emitFinding()`, add confidence downgrade:

```typescript
// After creating a finding, check if ALL matched files are non-code:
const finding = emitFinding(rule, evidence, matchedFiles, lineNumbers);
const hasCodeMatch = matchedFiles.some((f) => classifyFile(f) === "code");
if (!hasCodeMatch) {
  finding.confidence = "low";  // config/test-only match → low confidence
}
findings.push(finding);
```

**Same pattern applied to:** `agent-framework.ts`, `mcp-server.ts`, `skills-plugins.ts`

**Rationale:** Instead of skipping `.json`/`.yaml` entirely (which could miss malicious MCP configs), we keep them in the scan but downgrade confidence when a finding comes only from non-code files. Combined with MOD 1's confidence gate in policy.ts, these findings won't trigger ABORT but will still appear in the report.

---

## MOD 3: Soften PROCEED language + handle PROCEED_WITH_CONSTRAINTS

**File:** `src/reporting/terminal.ts` — new function after `decisionExplanation()`:

```typescript
function renderPlainEnglish(result: AuditResult): string[] {
  const lines: string[] = [];
  const active = result.findings.filter((f) => !f.suppressed);
  const critical = active.filter((f) => f.severity === "critical");
  const high = active.filter((f) => f.severity === "high");
  const medium = active.filter((f) => f.severity === "medium");

  lines.push(pc.bold("  What This Means"));
  lines.push(pc.dim("  ─".repeat(30)));
  lines.push("");

  switch (result.decision.value) {
    case "PROCEED":
      lines.push("  No serious issues detected in our static checks. We scanned");
      lines.push(`  ${result.coverage.files_scanned} files and found nothing that would`);
      lines.push("  prevent safe adoption.");
      break;
    case "PROCEED_WITH_CONSTRAINTS":
      lines.push("  We found some issues that need attention before you use this.");
      lines.push("  None are critically dangerous, but the mitigations listed below");
      lines.push("  should be applied first.");
      break;
    case "CAUTION":
      lines.push("  We found issues that deserve a closer look before you use this.");
      lines.push("  Review the findings below and decide whether the risks are");
      lines.push("  acceptable for your use case.");
      break;
    case "ABORT":
      lines.push("  We found serious security issues that should be fixed before");
      lines.push("  you use this. See the specific issues and remediation steps below.");
      break;
  }
  lines.push("");

  // Show critical/high findings in plain English
  const showFindings = [...critical, ...high];
  // Also show medium if few enough and no critical/high
  if (showFindings.length === 0 && medium.length > 0 && medium.length <= 3) {
    showFindings.push(...medium);
  }

  if (showFindings.length > 0) {
    lines.push(`  We found ${showFindings.length} issue(s) worth knowing about:`);
    lines.push("");
    for (const f of showFindings) {
      const explanation = RISK_EXPLANATIONS[f.id];
      if (explanation) {
        lines.push(`  ${pc.dim("•")} ${explanation.plain}`);
      }
    }
    lines.push("");
  }

  return lines;
}
```

---

## MOD 4: Merge RISK_EXPLANATIONS into `{ technical, plain }` structure

**File:** `src/reporting/terminal.ts:91-146`

```typescript
// BEFORE:
const RISK_EXPLANATIONS: Record<string, string> = {
  "GHA-EXEC-001":
    "Downloads and executes remote code in a single command. An attacker who compromises the URL can execute arbitrary code on your machine during install.",
  // ... 25 more entries
};

// AFTER:
const RISK_EXPLANATIONS: Record<string, { technical: string; plain: string }> = {
  "GHA-EXEC-001": {
    technical: "Downloads and executes remote code in a single command. An attacker who compromises the URL can execute arbitrary code on your machine during install.",
    plain: "The install downloads and runs code in one step — if the source is compromised, your machine runs the attacker's code.",
  },
  "GHA-EXEC-002": {
    technical: "Runs code automatically during package install. Malicious packages use this to execute code before you review anything.",
    plain: "Code runs automatically when you install this package — you don't get a chance to review it first.",
  },
  "GHA-EXEC-003": {
    technical: "Allows arbitrary shell commands from string input. If user data reaches this, it's remote code execution.",
    plain: "This code can run any command on your computer from text input — if that input comes from outside, it's a backdoor.",
  },
  "GHA-EXEC-004": {
    technical: "Deserializes untrusted data into executable objects. Attacker-crafted payloads can execute arbitrary code.",
    plain: "This loads external data in a way that could let an attacker slip in code that runs on your machine.",
  },
  "GHA-EXEC-005": {
    technical: "Fetches remote content then executes or loads it as code. If the remote source is compromised, your system is compromised.",
    plain: "This downloads something from the internet and then runs it — if that source gets hacked, so does your system.",
  },
  "GHA-CI-001": {
    technical: "Runs CI workflows with write access on pull requests from forks. Attackers can submit PRs that execute code with your repo's secrets.",
    plain: "Anyone can submit code changes that run with access to your project's secrets — an attacker could steal them.",
  },
  "GHA-CI-002": {
    technical: "GitHub token has broad permissions. A compromised workflow step can push code, delete branches, or access secrets.",
    plain: "The CI system has more access than it needs — if anything goes wrong, it could modify your whole project.",
  },
  "GHA-CI-003": {
    technical: "Actions pinned to tags instead of commit SHAs. If the action repo is compromised, the tag can be moved to malicious code.",
    plain: "CI tools aren't locked to exact versions — a compromised tool could swap in malicious code without you noticing.",
  },
  "GHA-CI-004": {
    technical: "Untrusted user input (PR title, issue body) injected directly into shell commands. Attackers craft input that executes arbitrary commands.",
    plain: "Pull request text gets run as a command in CI — someone could submit a PR with text that steals your project's secrets.",
  },
  "GHA-CI-005": {
    technical: "Self-hosted runners execute untrusted code from forks. The runner's host machine, network, and credentials are exposed.",
    plain: "Your build server runs code from anyone who submits a PR — they could access your server and network.",
  },
  "GHA-SECRETS-001": {
    technical: "Private key material committed to the repository. Anyone with repo access can impersonate the key owner.",
    plain: "A private key is stored in the code — anyone who can see this repo can pretend to be you.",
  },
  "GHA-SECRETS-002": {
    technical: "Environment file with probable secrets committed. Database passwords, API keys, or tokens may be exposed.",
    plain: "A config file that likely contains passwords or API keys was committed — these should never be in code.",
  },
  "GHA-SECRETS-003": {
    technical: "High-entropy string near auth keywords detected. May be a real API key or token — verify manually.",
    plain: "We found something that looks like it might be a password or API key — worth checking manually.",
  },
  "GHA-SUPPLY-001": {
    technical: "No lockfile means dependency versions aren't pinned. A compromised registry could serve malicious versions.",
    plain: "Dependencies aren't locked to specific versions — a compromised update could slip in automatically.",
  },
  "GHA-SUPPLY-002": {
    technical: "Dependencies use floating version ranges. A malicious version published within range would be installed automatically.",
    plain: "Dependencies accept a range of versions — a malicious update within that range would install without warning.",
  },
  "GHA-SUPPLY-003": {
    technical: "Dependencies sourced from raw git URLs instead of registries. No audit trail or integrity verification.",
    plain: "Some dependencies come directly from git repos instead of package registries — there's no verification they're safe.",
  },
  "GHA-SUPPLY-005": {
    technical: "Binary files without source provenance. Could contain malware that bypasses code review.",
    plain: "There are binary files with no way to verify what's in them — they could contain anything.",
  },
  "GHA-TRUST-001": {
    technical: "No security disclosure policy. Vulnerability reporters have no way to reach maintainers privately.",
    plain: "There's no SECURITY.md — if someone finds a vulnerability, there's no private way to report it.",
  },
  "GHA-TRUST-002": {
    technical: "No code ownership defined. No guarantee that changes to sensitive files are reviewed by qualified maintainers.",
    plain: "No CODEOWNERS file — there's no rule about who must review changes to important files.",
  },
  "GHA-AI-001": {
    technical: "LLM output flows directly to tool execution without validation. A prompt injection could execute arbitrary tools.",
    plain: "AI model output may control what tools run — a prompt injection attack could make the AI do things it shouldn't.",
  },
  "GHA-AI-002": {
    technical: "Secrets or sensitive data included in prompts. LLM providers may log or train on this data.",
    plain: "Sensitive data might be sent to an AI provider — they could log it or use it for training.",
  },
  "GHA-AGENT-001": {
    technical: "Agent has shell, write, and network access without human approval. A misbehaving agent can exfiltrate data or destroy files.",
    plain: "An AI agent can run commands, write files, and access the network without asking permission — if it goes wrong, it could leak or destroy data.",
  },
  "GHA-MCP-001": {
    technical: "MCP server exposes unrestricted shell execution. Any connected client can run arbitrary commands on the host.",
    plain: "This MCP server lets connected tools run any command on the computer — no restrictions.",
  },
  "GHA-MCP-003": {
    technical: "MCP server forwards auth tokens into tool calls. A malicious tool request can capture credentials.",
    plain: "Login credentials get passed to tools automatically — a malicious tool could steal them.",
  },
  "GHA-PLUGIN-002": {
    technical: "Plugin instructions attempt to override the AI's identity or safety boundaries. May be benign (defining a persona) or malicious (bypassing guardrails).",
    plain: "Plugin instructions try to change the AI's behavior — could be a normal persona definition or an attempt to bypass safety rules.",
  },
  "GHA-INFRA-001": {
    technical: "Container runs as root. A container escape gives the attacker root access to the host.",
    plain: "The container runs with full admin privileges — if an attacker breaks out, they own the whole machine.",
  },
  "GHA-INFRA-002": {
    technical: "Container uses :latest tag. Builds are not reproducible and a compromised image affects all future builds.",
    plain: "The container always pulls the latest version — a compromised image would affect everyone automatically.",
  },
};
```

**Usage update at line ~276:**

```typescript
// BEFORE:
const explanation = RISK_EXPLANATIONS[f.id];
if (explanation) {
  lines.push(`  ${pc.dim("Risk:")}  ${explanation}`);
}

// AFTER:
const explanation = RISK_EXPLANATIONS[f.id];
if (explanation) {
  lines.push(`  ${pc.dim("Risk:")}  ${explanation.technical}`);
}
```

---

## MOD 5: Stage 2 fields — optional, in all reporters

**File:** `src/models/audit-result.ts`

```typescript
// Add to AuditResult interface:
export interface Stage2Trigger {
  finding_id: string;
  reason: string;
  recommended_module: "ast" | "sandbox" | "manual_review";
}

export interface AuditResult {
  manifest: RunManifest;
  context: AuditContext;
  profile: RepoProfile;
  findings: Finding[];
  scores: Scores;
  decision: Decision;
  module_results: ModuleResult[];
  coverage: CoverageReport;
  reports: Record<string, string>;
  // Stage 2 escalation (optional — present when low-confidence hard-stops exist)
  stage2_recommended?: boolean;
  stage2_triggers?: Stage2Trigger[];
}
```

**File:** `src/reporting/markdown.ts` — add after constraints section (~line 93):

```typescript
if (result.stage2_recommended && result.stage2_triggers && result.stage2_triggers.length > 0) {
  lines.push("## Deeper Analysis Recommended");
  lines.push("");
  lines.push(`Static analysis flagged ${result.stage2_triggers.length} issue(s) with low confidence.`);
  lines.push("A deeper scan could confirm or dismiss these before you act on them.");
  lines.push("");
  for (const t of result.stage2_triggers) {
    lines.push(`- **${t.finding_id}**: ${t.reason} *(${t.recommended_module})*`);
  }
  lines.push("");
}
```

**File:** `src/reporting/sarif.ts` — add to properties (~line 118):

```typescript
properties: {
  decision: result.decision.value,
  scores: result.scores,
  run_id: result.manifest.run_id,
  stage2_recommended: result.stage2_recommended ?? false,
  stage2_triggers: result.stage2_triggers ?? [],
},
```

**JSON reporter:** No changes needed — `JSON.stringify(result)` automatically includes optional fields when present.

---

## MOD 6: `--no-stage2` flag plumbing

**File:** `src/models/audit-request.ts` — add to schema:

```typescript
no_stage2: z.boolean().default(false),
```

**File:** `src/cli.ts` — add option after line 19:

```typescript
.option("--no-stage2", "Suppress stage 2 analysis recommendations", false)
```

Add to request construction (~line 43):

```typescript
no_stage2: opts.noStage2 ?? false,
```

**File:** `src/engine/run-audit.ts` — add after Phase 10 (~line 174):

```typescript
  // Stage 2 escalation detection
  let stage2_recommended = false;
  const stage2_triggers: Stage2Trigger[] = [];

  if (!request.no_stage2) {
    const hardStopPatterns: string[] = catalog.policy_baselines.hard_stop_patterns;
    const lowConfHardStops = findings.filter(
      (f) => !f.suppressed && hardStopPatterns.includes(f.id) && f.confidence === "low"
    );

    const STAGE2_MODULE_MAP: Record<string, "ast" | "sandbox" | "manual_review"> = {
      "GHA-AI-001": "ast",
      "GHA-AGENT-001": "ast",
      "GHA-MCP-001": "ast",
      "GHA-MCP-003": "ast",
      "GHA-EXEC-004": "ast",
      "GHA-EXEC-005": "ast",
      "GHA-EXEC-001": "sandbox",
      "GHA-EXEC-002": "sandbox",
    };

    for (const f of lowConfHardStops) {
      stage2_triggers.push({
        finding_id: f.id,
        reason: `Low-confidence static match — ${STAGE2_MODULE_MAP[f.id] === "ast" ? "code flow analysis" : STAGE2_MODULE_MAP[f.id] === "sandbox" ? "sandbox execution" : "manual review"} could confirm or dismiss this finding.`,
        recommended_module: STAGE2_MODULE_MAP[f.id] ?? "manual_review",
      });
    }

    stage2_recommended = stage2_triggers.length > 0;
  }
```

Then add to result construction (~line 204):

```typescript
  const result: AuditResult = {
    manifest,
    context,
    profile,
    findings,
    scores,
    decision,
    module_results: allModuleResults,
    coverage,
    reports: {},
    ...(stage2_recommended ? { stage2_recommended, stage2_triggers } : {}),
  };
```

---

## MOD 7: `.env.example` + `.env.sample` + `.env.template`

**File:** `src/analyzers/universal/secrets.ts:156-199`

```typescript
// AFTER the envFiles filter (line 163) and AFTER matches are collected (line 180),
// add before the emitFinding call:

          if (matches.length > 0) {
            const finding = emitFinding(
              rule,
              {
                type: "env_secret_entry",
                records: matches.map((m) => ({
                  path: m.path,
                  line_number: m.lineNumber,
                  entry_key: m.entry_type,
                  detail: `Secret-like entry "${m.entry_type}" found in env file`,
                })),
              },
              affectedFiles,
              matches.map((m) => m.lineNumber),
            );

            // Downgrade example/sample/template env files
            const allExample = affectedFiles.every((f) =>
              /\.(example|sample|template)$/.test(f)
            );
            if (allExample) {
              finding.severity = "info";
              finding.confidence = "low";
            }

            findings.push(finding);
          }
```

---

## MOD 8: New test cases

**File:** `src/__tests__/policy.test.ts` — add new describe block:

```typescript
  describe("Confidence gate on hard-stop rules", () => {
    test("low-confidence hard-stop finding does NOT trigger ABORT", () => {
      const finding = makeFinding({
        id: "GHA-SECRETS-001",
        title: "Secrets exposed",
        confidence: "low",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).not.toBe("ABORT");
      expect(decision.hard_stop_triggered).toBeFalsy();
    });

    test("medium-confidence hard-stop finding DOES trigger ABORT", () => {
      const finding = makeFinding({
        id: "GHA-SECRETS-001",
        title: "Secrets exposed",
        confidence: "medium",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.hard_stop_triggered).toBe(true);
    });

    test("high-confidence hard-stop finding DOES trigger ABORT", () => {
      const finding = makeFinding({
        id: "GHA-EXEC-001",
        title: "Exec issue",
        confidence: "high",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.hard_stop_triggered).toBe(true);
    });
  });

  describe("ABORT decisions include constraints", () => {
    test("hard-stop ABORT includes non-empty constraints", () => {
      const finding = makeFinding({
        id: "GHA-EXEC-001",
        title: "Dangerous exec",
        category: "supply-chain",
        confidence: "high",
        remediation: "Pin the download URL and verify checksums.",
      });
      const decision = evaluatePolicy(
        [finding],
        makeScores(),
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.constraints.length).toBeGreaterThan(0);
    });

    test("threshold ABORT includes constraints", () => {
      const finding = makeFinding({ category: "supply-chain" });
      const scores = makeScores({ abuse_potential: 90 });
      const decision = evaluatePolicy(
        [finding],
        scores,
        baseContext,
        "balanced",
        mockContract,
        mockCatalog,
      );
      expect(decision.value).toBe("ABORT");
      expect(decision.constraints.length).toBeGreaterThan(0);
    });
  });
```

**File:** `src/__tests__/base.test.ts` (new file):

```typescript
import { describe, test, expect } from "bun:test";
import { classifyFile, isNonCodeFile } from "../analyzers/base.ts";

describe("classifyFile", () => {
  test("classifies .md as doc", () => {
    expect(classifyFile("README.md")).toBe("doc");
    expect(classifyFile("docs/plan.md")).toBe("doc");
  });

  test("classifies .json/.yaml as config", () => {
    expect(classifyFile("package.json")).toBe("config");
    expect(classifyFile("config.yaml")).toBe("config");
    expect(classifyFile("rules.yml")).toBe("config");
  });

  test("classifies test files as test", () => {
    expect(classifyFile("src/__tests__/policy.test.ts")).toBe("test");
    expect(classifyFile("tests/unit/foo.spec.js")).toBe("test");
  });

  test("classifies .ts/.js/.py as code", () => {
    expect(classifyFile("src/engine/policy.ts")).toBe("code");
    expect(classifyFile("lib/index.js")).toBe("code");
    expect(classifyFile("main.py")).toBe("code");
  });
});

describe("isNonCodeFile", () => {
  test("returns true for docs and tests", () => {
    expect(isNonCodeFile("README.md")).toBe(true);
    expect(isNonCodeFile("src/__tests__/foo.test.ts")).toBe(true);
  });

  test("returns false for code files", () => {
    expect(isNonCodeFile("src/engine/policy.ts")).toBe(false);
  });

  test("returns false for config files (they are scanned with low confidence)", () => {
    // Config files are NOT skipped — they get confidence downgrade instead
    expect(isNonCodeFile("package.json")).toBe(false);
    // But classifyFile returns "config" for downstream confidence handling
    expect(classifyFile("package.json")).toBe("config");
  });
});
```

---

## Summary of all changes

| File | Lines Affected | Change |
|------|---------------|--------|
| `src/engine/policy.ts:121` | 1 line | Add `&& f.confidence !== "low"` to hard-stop filter |
| `src/engine/policy.ts:128` | 3 lines | Change `constraints` from `[]` to `generateConstraints(active)` + per-finding remediation |
| `src/engine/policy.ts:150` | 3 lines | Add `generateConstraints(active)` + re-run instruction to threshold ABORT |
| `src/analyzers/base.ts:82+` | 15 lines | Add `classifyFile()` and `isNonCodeFile()` exports |
| `src/analyzers/typed/*.ts` (×4) | ~6 lines each | Filter to `codeFiles`, downgrade confidence for non-code matches |
| `src/analyzers/universal/secrets.ts:182-199` | 8 lines | `.env.example`/`.sample`/`.template` → severity=info, confidence=low |
| `src/reporting/terminal.ts:91-146` | 120 lines | Restructure RISK_EXPLANATIONS to `{ technical, plain }` |
| `src/reporting/terminal.ts:188+` | 40 lines | Add `renderPlainEnglish()` function + insert into report |
| `src/reporting/terminal.ts:276` | 1 line | Update to use `.technical` accessor |
| `src/reporting/terminal.ts:315+` | 15 lines | Add "Deeper Analysis Recommended" section |
| `src/models/audit-result.ts` | 10 lines | Add `Stage2Trigger` interface + optional fields |
| `src/models/audit-request.ts` | 1 line | Add `no_stage2` to schema |
| `src/cli.ts` | 2 lines | Add `--no-stage2` option + pass to request |
| `src/engine/run-audit.ts:174+` | 30 lines | Stage 2 escalation detection logic |
| `src/reporting/markdown.ts:93+` | 10 lines | Stage 2 section in markdown output |
| `src/reporting/sarif.ts:118` | 2 lines | Stage 2 fields in SARIF properties |
| `src/__tests__/policy.test.ts` | 70 lines | Confidence gate + ABORT constraints tests |
| `src/__tests__/base.test.ts` (new) | 45 lines | File classification tests |

**Total: ~370 lines across 15 files**
