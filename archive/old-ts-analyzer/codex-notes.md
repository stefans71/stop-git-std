
This document is the implementation-aligned technical design baseline for stop-git-std v3 — Technical Design.md


NOTES: Here’s the clean way to think about them.

[What each document is
1. stop-git-std v3 — Technical Design (stop-git-std v3 — Technical Design.md)

This is the human-readable architecture/design doc.

Use it for:

product definition
architecture
phases
module concepts
implementation strategy
repo structure
milestone plan
Bun/TypeScript + optional Python backend direction

This should now be your main design doc.

2. Gh-audit-engine-contract-v2

This is the machine-readable execution contract.

It defines:

inputs
outputs
phases
routing
scoring behavior
policy thresholds
suppression behavior
reporting contract

In other words:

the technical design says what the system is
the engine contract says how the engine behaves

This is a very important file.

But it is still in the old gh-audit naming and still contains some Python-era assumptions in places, especially under references and implementation_notes.

3. gh_audit_rule_catalog_v_2.yaml

This is the rule inventory.

It defines:

rule IDs
categories
severities
confidence
methods
evidence shapes
policy hints
routing matrix
tool/method matrix

This file answers:
“What exactly do we check for?”

Also very important.

4. gh_audit_engine_contract_v_2.yaml

This appears to be a duplicate / alternate copy of the engine contract concept.

If this is separate from Gh-audit-engine-contract-v2, then you likely have:

one canvas/doc version
one exported/copied filename version

That is probably where the confusion is coming from.

What you should keep conceptually

You really only need 3 canonical documents:

A. Technical design

Human-readable system/build spec

Recommended name:
docs/technical-design.md

B. Rule catalog

Machine-readable rules

Recommended name:
docs/rule-catalog.yaml

C. Engine contract

Machine-readable execution contract

Recommended name:
docs/engine-contract.yaml

That’s the clean set.

What I think happened

You created docs in stages:

first under gh-audit
then later renamed the product to stop-git-std
then created some canvas docs and some filename-style docs

So now you have:

old product-name docs
updated product-name doc
possibly duplicate contract docs in different naming styles
What I recommend doing now
Keep
stop-git-std v3 — Technical Design as the replacement for the old .md
the rule catalog YAML
the engine contract YAML
Deprecate / rename
anything still named gh-audit-*
especially duplicate contract files
Clean canonical mapping

Use this mapping in the repo:

docs/
  technical-design.md      <- from stop-git-std v3 — Technical Design
  rule-catalog.yaml        <- from gh_audit_rule_catalog_v_2.yaml
  engine-contract.yaml     <- from Gh-audit-engine-contract-v2 / gh_audit_engine_contract_v_2.yaml
Important note about Gh-audit-engine-contract-v2

It is still useful, but it should be updated and renamed.

At minimum these parts should change:

name: gh-audit-engine-contract → stop-git-std-engine-contract
references to gh-audit-rule-catalog-v2.yaml
references to gh-audit-technical-design-v2.md
implementation_notes currently still point to Python files like:
config.py
models.py
engine.py
those should become Bun/TypeScript-oriented

So the answer is:

It is not a random extra file.
It is the execution contract spec, and you should keep that concept — but rename and align it with stop-git-std.]


5. Inputs and Outputs
5.1 CLI inputs
stop-git-std \
  --repo https://github.com/org/repo \
  --ref main \
  --env developer_laptop \
  --perm network,filesystem_read,github_token \
  --runtime-mode off \
  --format md,json
Required inputs
--repo or local path
Optional inputs
--ref
--env
--perm
--runtime-mode
--policy
--output-dir
--fail-on
--max-depth
5.2 Core machine-readable outputs
audit_context.json
repo_profile.json
findings.json
scores.json
decision.json
report.md
6. Context Model

The system must not score a repo in a vacuum.

6.1 Context schema
{
  "repo_target": "https://github.com/org/repo",
  "ref": "main",
  "target_environment": "developer_laptop",
  "expected_permissions": [
    "filesystem_read",
    "network",
    "github_token"
  ],
  "runtime_validation_enabled": false,
  "adoption_mode": "third_party",
  "notes": "Will be evaluated before local execution"
}
6.2 Supported environments
Environment	Description	Risk multiplier
developer_laptop	interactive machine with user secrets likely present	high
ci_runner	automated runner with repository and secrets access	high
container_isolated	isolated container with minimal secrets	medium
production_service	deployed service affecting users/data	critical
offline_analysis	no execution, static review only	low

Environment affects scoring and policy outcomes.

7. Repository Inventory and Classification

Phase 1 establishes what exists in the repo.

7.1 Responsibilities
shallow clone/fetch
enumerate file tree
identify languages
detect frameworks
identify workflows and manifests
detect high-risk artifacts
classify component categories
compute inventory metadata
7.2 Data model
{
  "languages": ["TypeScript", "Python"],
  "frameworks": ["Express", "React"],
  "components": {
    "web_app": true,
    "api": true,
    "ai_llm": true,
    "agent_framework": false,
    "skills_plugins": false,
    "mcp_server": false,
    "ci_cd": true,
    "infrastructure": true,
    "library_package": false
  },
  "artifacts": {
    "manifests": ["package.json", "bun.lock"],
    "workflows": [".github/workflows/release.yml"],
    "containers": ["Dockerfile"],
    "infra": ["docker-compose.yml", "k8s/deploy.yaml"]
  },
  "high_risk_files": [
    "scripts/install.sh",
    ".github/workflows/release.yml"
  ]
}
7.3 Classification matrix
Category	Detection signals	Primary parser/method	Secondary method	Output flag
Web app	routes, templates, controllers, SSR frameworks	manifest parser + AST route detector	path heuristics	web_app
API	endpoint definitions, OpenAPI, router setup	AST router detector	keyword/path heuristics	api
AI/LLM	SDK imports, provider endpoints, prompt/tool code	AST import scan + manifest parser	grep heuristics	ai_llm
Agent framework	agent loops, tool registries, planner/executor patterns	AST rule pack	keyword heuristics	agent_framework
Skills/plugins	SKILL.md, manifests, extension descriptors	file pattern detector	manifest schema checks	skills_plugins
MCP server	MCP package imports, tool definitions, server config	manifest + AST detector	config search	mcp_server
CI/CD	workflow files, Jenkinsfile, pipeline configs	YAML parser	path heuristics	ci_cd
Infrastructure	Dockerfile, Compose, Terraform, Helm, K8s	config parser	file name heuristics	infrastructure
Library/package	publish metadata, importable package layout	manifest parser	packaging heuristics	library_package
7.4 Example detector snippets
TypeScript framework detection
import { readFileSync } from "node:fs";
import { join } from "node:path";

const TS_FRAMEWORK_PATTERNS: Record<string, RegExp> = {
  Express: /from\\s+["']express["']|require\\(["']express["']\\)/,
  Fastify: /from\\s+["']fastify["']|require\\(["']fastify["']\\)/,
  Next: /from\\s+["']next["']|next\\(/,
};

export function detectTsFrameworks(files: string[], root: string): string[] {
  const found = new Set<string>();
  for (const rel of files.filter(f => f.endsWith(".ts") || f.endsWith(".js"))) {
    const text = readFileSync(join(root, rel), "utf8");
    for (const [name, pattern] of Object.entries(TS_FRAMEWORK_PATTERNS)) {
      if (pattern.test(text)) found.add(name);
    }
  }
  return [...found];
}
MCP detection heuristic
const MCP_PATTERNS = [
  /modelcontextprotocol/,
  /mcp-server/,
  /@modelcontextprotocol\/sdk/,
  /registerTool\(/,
];

export function detectMcp(files: Array<{ path: string; content: string }>): boolean {
  return files.some(file =>
    file.path.toLowerCase().includes("mcp") ||
    MCP_PATTERNS.some(pattern => pattern.test(file.content))
  );
}
8. Analysis Strategy by Depth

The engine should use a layered approach.

Tier	Method	Speed	Precision	Use cases
1	path/file/keyword heuristics	very fast	low-medium	initial inventory
2	manifest/config parsing	fast	medium-high	dependencies, workflows, infra
3	AST rule analysis	medium	high	code sinks, routers, auth patterns
4	lightweight dataflow	slower	higher	taint to dangerous sinks
5	sandbox runtime observation	slowest	highest for behavior	ambiguous/high-risk repos
Design rule
Always do Tiers 1–2.
Run Tier 3 where language support exists.
Run Tier 4 only on selected sink families.
Run Tier 5 when requested or triggered by policy.
9. Universal Check Modules

These run regardless of repo category.

9.1 Governance and Trust Module
Goal

Assess whether the source is responsibly maintained and attributable.

Checks
Check	Signal source	Method
SECURITY.md present	repo tree	path check
CODEOWNERS present	repo tree	path check
branch protection evidence	GitHub API / metadata	API lookup
signed tags/releases	git metadata / GitHub API	CLI or API
maintainer concentration	git log	commit analysis
suspicious contributor shift	git history	time-series heuristic
release cadence	tags/releases	metadata analysis
archived/abandoned	GitHub metadata	API lookup
dependency update hygiene	lockfile and PR signals	manifest + metadata
Tooling
git CLI
GitHub API adapter
metadata scorer
9.2 Supply Chain Module
Goal

Assess dependency hygiene and provenance.

Checks
Check	Method	Example artifacts
lockfile present	manifest parsing	package-lock.json, bun.lock, poetry.lock
floating versions	manifest parser	^, ~, *, unpinned git refs
direct Git dependencies	manifest parser	git+https://...
arbitrary download URLs	config/code scan	curl/wget/tarball install
vulnerable packages	OSV query adapter	npm/pip/cargo deps
opaque vendored binaries	file scan	.so, .dll, bundled executables
typosquatting suspicion	name heuristics	package distance scoring
scorecard posture	Scorecard adapter	branch protection, workflows
Tooling
ecosystem-specific manifest parsers
OSV client
OpenSSF Scorecard adapter
file signature scanner
9.3 Secrets Module
Goal

Detect committed secrets or sensitive material.

Checks
hardcoded API tokens
private keys
cloud creds
committed .env
connection strings
auth tokens in tests/examples
Methods
regex detectors
entropy heuristics
filename/path risk scoring
optional integration with secret scanners
9.4 Dangerous Execution Module
Goal

Detect code and scripts that can cause immediate harm when installed or run.

Checks
Pattern family	Examples
download-and-execute	`curl URL
install hooks	postinstall, preinstall, setup hooks
dynamic eval	eval, exec, new Function
unsafe deserialization	pickle.loads, unsafe YAML loaders
shell execution	child_process.exec, shell-based subprocesses
remote plugin loading	fetching code/config at runtime
disabled security controls	cert verify off, auth bypass flags
9.5 CI/CD Module
Goal

Treat workflows and runner trust boundaries as first-class audit targets.

Checks
Check	Method	Risk
pull_request_target use	YAML parse	high
unpinned third-party actions	YAML parse	medium-high
broad token permissions	YAML parse	high
secrets available on risky triggers	workflow semantics	high
self-hosted runners	YAML parse	medium-high
shell injection via inputs	AST/regex in workflows	high
artifact poisoning paths	workflow graph heuristics	medium
9.6 Infra and Container Module
Goal

Detect unsafe deployment and containerization defaults.

Checks
root container user
privileged container
dangerous bind mounts
wildcard ingress/service exposure
weak base image
missing resource constraints
broad K8s RBAC
hardcoded secrets in manifests
9.7 License Module
Goal

Evaluate legal adoption compatibility.

Checks
missing license
ambiguous custom terms
viral/incompatible license for intended use
bundled third-party code lacking attribution

This module should not block execution safety analysis, but it can block adoption decisions.

10. Type-Specific Modules

Each repo category maps to one or more module packs.

10.1 Category-to-module routing matrix
Detected category	Module pack	Standards family	MVP depth
web_app	web	OWASP ASVS subset, CWE	static + config
api	api	OWASP API Top 10	static + config
ai_llm	ai_llm	OWASP LLM Top 10	static
agent_framework	agent	agentic risk patterns	static
skills_plugins	plugin	plugin/skill rule pack	static
mcp_server	mcp	MCP risk pack	static
library_package	package	package safety	static
infrastructure	infra	CIS/K8s/container checks	config
ci_cd	ci	workflow risk pack	config
10.2 Web module
Categories
auth/session patterns
access control assumptions
input validation
output encoding
crypto misuse
SSRF/XSS/SQLi heuristics where detectable
Methods
AST route extraction
middleware detection
config inspection
sink scanning
10.3 API module
Categories
missing auth on sensitive routes
CORS misconfiguration
mass assignment
object-level authorization gaps
schema validation absence
sensitive error leakage
10.4 AI/LLM module
Categories
prompt injection exposure
unvalidated model output controlling tools
prompt leakage of secrets/context
unbounded retrieval/action loops
no rate/consumption boundaries
raw provider key exposure
10.5 Agent module
Categories
excessive agency
unrestricted tool sets
missing human gates for destructive actions
shared memory contamination
recursive self-modification
autonomous network/shell execution
10.6 Skills/plugins module
Categories
manifest permission scope
dangerous hidden actions
shell/network actions hidden in install or runtime path
tampering with identity or configuration files
untrusted update/fetch behavior
10.7 MCP module
Categories
unrestricted filesystem or process tools
SSRF-capable fetch tools
credential passthrough
prompt-to-tool escalation without policy boundary
unauthenticated local or remote tool exposure
10.8 Package/library module
Categories
import-time side effects
install-time execution
unsafe defaults
dependency sprawl
opaque binaries / vendored payloads
public API requiring dangerous permissions without justification
11. Finding Model

All modules must emit findings using a common schema.

11.1 Finding schema
{
  "id": "GHA-CI-003",
  "title": "Workflow uses pull_request_target with broad token permissions",
  "category": "ci_cd",
  "subcategory": "workflow_trust_boundary",
  "severity": "high",
  "confidence": "high",
  "axis_impacts": {
    "trustworthiness": -5,
    "exploitability": 12,
    "abuse_potential": 18
  },
  "files": [".github/workflows/build.yml"],
  "evidence": [
    "on: pull_request_target",
    "permissions: write-all"
  ],
  "mapped_standards": ["GITHUB-ACTIONS-HARDENING", "CWE-829"],
  "proof_type": "static",
  "remediation": "Use pull_request instead of pull_request_target where possible and minimize GITHUB_TOKEN permissions.",
  "tags": ["github-actions", "token-scope", "pr-trust-boundary"]
}
11.2 Severity scale
info
low
medium
high
critical
11.3 Confidence scale
low
medium
high
12. Scoring Engine

A single number is not sufficient.

12.1 Axis definitions
Axis	Meaning
Trustworthiness	source quality, governance, provenance, maintenance
Exploitability	insecurity of implementation/configuration
Abuse Potential	capability to harm the environment if run
12.2 Range

Each axis is 0..100, where higher is worse.

12.3 Score construction
base = 0
+ weighted normalized findings
+ environment multipliers
+ confidence modifiers
- positive trust signals
clamped to 0..100
12.4 Example weighting matrix
Finding type	Trustworthiness	Exploitability	Abuse potential
missing SECURITY.md	+6	+0	+0
unpinned dependency	+4	+6	+1
critical OSV vuln	+2	+20	+4
committed private key	+8	+8	+15
pull_request_target + write-all	+5	+12	+18
curl pipe shell	+2	+10	+20
unrestricted shell tool in MCP	+0	+8	+25
signed releases present	-8	-1	-1
sandbox runtime showed unexpected exfil domain	+6	+8	+30
12.5 Environment multiplier examples
Environment	Abuse multiplier
developer_laptop	1.25
ci_runner	1.3
container_isolated	0.8
offline_analysis	0.2
production_service	1.4
13. Policy Engine

Policy converts findings and scores into decisions.

13.1 Decision matrix
Condition	Decision
clear malicious/exfil or critical unsafe execution pattern in core path	ABORT
severe abuse potential with weak provenance	ABORT
high risk but controllable with isolation and pinning	PROCEED_WITH_CONSTRAINTS
moderate unresolved risks	CAUTION
no major findings and acceptable posture	PROCEED
13.2 Hard-stop rules

Emit ABORT if any of the following are present unless explicitly overridden:

credential theft indicators
download-and-execute in default install/run path from untrusted remote source
runtime-observed exfiltration of env/home credentials
unaudited shell execution tool exposed through agent or MCP interface
critical GitHub Actions trust-boundary violation with write permissions and untrusted input execution
intentionally hidden or obfuscated high-risk code in adoption path
13.3 Constraint templates

PROCEED_WITH_CONSTRAINTS should include concrete controls such as:

run only in disposable container
block outbound network except allowlist
provide read-only mount only
use throwaway token with least privilege
pin to reviewed commit SHA
disable install scripts
remove self-hosted runner execution
14. Runtime Validation Design

Optional but important for ambiguous or high-risk repos.

14.1 Runtime modes
Mode	Description
off	no runtime execution
install_only	observe install behavior
build	observe install + build
smoke	install + build + basic startup/CLI invocation
14.2 Runtime environment requirements
disposable container or VM
no personal SSH keys
no browser cookies
no prod secrets
controlled HOME directory
outbound network logging
filesystem activity logging
14.3 Observations captured
{
  "network": [
    {"host": "example.com", "port": 443, "process": "bun", "phase": "install"}
  ],
  "file_reads": ["/tmp/home/.ssh/config"],
  "file_writes": ["/workspace/.cache/foo"],
  "processes": ["bash", "curl", "bun"],
  "alerts": [
    "Attempted read of home-directory SSH-related file during install"
  ]
}
15. Tooling and Methods Matrix

This is the implementation matrix the build needs.

Problem area	Primary method	Supporting tools	MVP?	Notes
repo clone/inventory	git + filesystem walk	git, Bun fs APIs	yes	shallow clone preferred
language detection	extensions + manifest parse	custom detector	yes	start simple
dependency parse	ecosystem parsers	npm/bun/pip/cargo/go parsers	yes	direct deps first
vuln lookup	OSV client	OSV API	yes	cache results
scorecard posture	Scorecard adapter	OpenSSF Scorecard	yes	optional offline fallback
secrets detection	regex + entropy	gitleaks optional	yes	support suppression
workflow analysis	YAML parser	yaml package	yes	first-class module
AST rules	language-specific parsers	TypeScript compiler API, tree-sitter later	yes	start with TS/JS support
dataflow	selective taint rules	later plugin or external engine	partial	selected sinks only
runtime observation	isolated runner	container sandbox + tracing	later	smoke mode first
report generation	templates	markdown/json/sarif emitter	yes	deterministic output
16. Code Organization

Suggested project structure:

stop-git-std/
  README.md
  docs/
    technical-design.md
    rule-catalog.yaml
    engine-contract.yaml
  src/
    cli.ts
    engine/
      run-audit.ts
      router.ts
      scoring.ts
      policy.ts
      normalize-findings.ts
    models/
      audit-request.ts
      repo-profile.ts
      finding.ts
      scores.ts
      decision.ts
    inventory/
      acquire-repo.ts
      enumerate-files.ts
      classify-repo.ts
      detect-frameworks.ts
    analyzers/
      universal/
        governance-trust.ts
        supply-chain.ts
        secrets.ts
        dangerous-execution.ts
        ci-cd.ts
        infrastructure.ts
      typed/
        web.ts
        api.ts
        ai-llm.ts
        agent-framework.ts
        skills-plugins.ts
        mcp-server.ts
        library-package.ts
    parsers/
      package-json.ts
      workflow-yaml.ts
      dockerfile.ts
      k8s-yaml.ts
      ts-ast.ts
    adapters/
      github-api.ts
      osv.ts
      scorecard.ts
    reporting/
      terminal.ts
      markdown.ts
      json.ts
      sarif.ts
    rules/
      load-rule-catalog.ts
      load-engine-contract.ts
    plugins/
      analyzer-backend.ts
      builtin-ts.ts
      python-subprocess.ts
17. Execution Flow
import type { AuditContext, Finding } from "./models";
import { buildRepoProfile } from "./inventory/classify-repo";
import { runUniversalChecks } from "./analyzers/universal";
import { runTypedChecks } from "./analyzers/typed";
import { scoreFindings } from "./engine/scoring";
import { decide } from "./engine/policy";

export async function runAudit(context: AuditContext) {
  const profile = await buildRepoProfile(context);
  const findings: Finding[] = [];

  findings.push(...await runUniversalChecks(context, profile));
  findings.push(...await runTypedChecks(context, profile));

  // runtime optional in later phase
  const scores = scoreFindings(context, profile, findings);
  const decision = decide(context, profile, findings, scores);

  return { profile, findings, scores, decision };
}
18. Example Rule Specs

Rules should be data-driven where possible.

18.1 Regex rule format
id: GHA-EXEC-001
title: curl pipe shell in script
category: dangerous_execution
severity: high
confidence: high
file_patterns:
  - "*.sh"
  - "*.bash"
  - "Dockerfile"
regex: "curl\\s+[^\\n|]+\\|\\s*(bash|sh)"
message: "Repository pipes remotely fetched data into a shell."
remediation: "Download artifacts explicitly, verify checksum/signature, and avoid pipe-to-shell execution."
axis_impacts:
  trustworthiness: 2
  exploitability: 10
  abuse_potential: 20
18.2 Semantic rule format
id: GHA-CI-002
title: pull_request_target with write token
category: ci_cd
severity: high
confidence: high
engine: workflow_yaml
conditions:
  on_contains: pull_request_target
  permissions_contains: write-all
message: "Workflow combines pull_request_target with broad token permissions."
remediation: "Minimize permissions and avoid untrusted code execution in trusted workflow contexts."
19. Reporting Format
19.1 Markdown report outline
# stop-git-std report

## Executive Summary
## Audit Context
## Repository Profile
## Decision
## Score Breakdown
## Critical Findings
## Findings by Category
## Recommended Controls
## Appendix: Detected Components
19.2 Example executive summary

The repository appears to contain a TypeScript API service, GitHub Actions workflows, Docker deployment artifacts, and OpenAI integration code. The highest-risk findings are an unsafe pull_request_target workflow with broad token permissions and a shell-based install script that downloads remote code. Trustworthiness is moderate, exploitability is high, and abuse potential is high for a developer laptop environment. Recommendation: ABORT until workflow and install-path risks are removed.

20. Calibration and Test Corpus

The system needs benchmark repos to tune precision and severity.

20.1 Corpus categories
known-good mature repos
abandoned but benign repos
repos with vulnerable dependency posture
repos with dangerous GitHub Actions patterns
unsafe AI/agent repos
plugin/skill repos with hidden execution patterns
MCP servers with broad tool access
repos with intentionally committed secrets
20.2 Test goals
measure false positive rate by category
measure detection coverage of high-severity rules
tune score thresholds
validate policy decisions against expert judgment
21. MVP Build Plan
Milestone 1: Bun project bootstrap and inventory

Deliverables:

Bun project initialization
CLI skeleton
YAML rule catalog loader
YAML engine contract loader
repo acquisition / local loading
inventory scanner
classification engine
profile JSON output
Milestone 2: Universal modules

Deliverables:

secrets module
dangerous execution module
dependency parsing
OSV lookup adapter
CI/CD workflow analysis
license/basic governance checks
Milestone 3: Typed modules

Deliverables:

API module
AI/LLM module
agent module
plugins module
MCP module
library/package module
Milestone 4: scoring and policy

Deliverables:

normalized finding schema
score engine
policy engine
terminal + JSON + markdown report output
Milestone 5: plugin backend interface

Deliverables:

analyzer backend contract
builtin TypeScript backend
stub Python subprocess backend contract
optional GitHub Action wrapper planning
Milestone 6: runtime mode

Deliverables:

isolated runner design
observation collector
runtime findings bridge
22. Immediate Build Decisions

These should be locked early.

22.1 Primary runtime and language

Recommended:

Bun (latest)
TypeScript

Reason:

strong CLI ergonomics
fast filesystem scanning
clean YAML/JSON/TOML handling
excellent fit for rule-catalog-driven orchestration
natural path to a later GitHub Action wrapper
22.2 Deep analysis stance

Recommended:

do not implement Python analyzers in MVP
design a plugin/subprocess analyzer interface now
allow optional Python deep analyzers later for advanced AST, taint, and semantic analysis

Rule:

Bun/TypeScript remains the source of truth for engine behavior, scoring, policy, and reporting
all analyzer backends must emit the same normalized finding contract
22.3 External dependencies

Recommended adapters:

OSV
OpenSSF Scorecard
GitHub API

Keep adapters optional so the CLI can still run offline with partial capabilities.

22.4 Report truth model

Rule:

findings are facts or bounded inferences
decisions are policy outputs
reports must never claim runtime behavior unless actually observed
23. Summary

The v3 build should be implemented as a layered, evidence-driven repository auditor with:

Bun/TypeScript as the primary engine
context-aware scoring
inventory-first categorization
universal plus typed rule packs
first-class workflow and abuse-potential analysis
optional Python deep analyzers later through a plugin/subprocess interface
optional runtime validation in a later phase
deterministic policy decisions

This document is the implementation-aligned technical design baseline for stop-git-std.