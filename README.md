# stop-git-std

Detection-first Git repository safety auditor.

Decides whether a repo is safe to **adopt**, **run**, or **integrate**.

## What it checks

- Governance & trust signals
- Supply chain posture
- Secrets & credential leaks
- Dangerous execution paths
- CI/CD workflow risks
- Infrastructure/container risks
- Typed risk packs for API, AI/LLM, agent, plugin/skill, and MCP repos

## Install

```bash
bun install
```

## Usage

```bash
bun run src/cli.ts <repo-path-or-url>
```

## Build spec

See [docs/build-spec.md](docs/build-spec.md) for the full technical design.
