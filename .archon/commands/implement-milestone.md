---
description: Implement a milestone from the build spec
argument-hint: <milestone number and description>
---

# Implement Milestone

You are building **stop-git-std**, a detection-first Git repository safety auditor built with Bun/TypeScript.

## Your task

Implement: $ARGUMENTS

## Instructions

1. Read `docs/build-spec.md` for the full architecture and requirements
2. Follow the repo structure defined in the build spec exactly
3. Write production-quality TypeScript — proper types, error handling, no `any`
4. Add tests for each module you implement
5. Keep the engine pipeline design: acquire → inventory → classify → analyze → normalize → score → decide → report
6. All analyzers must return normalized findings matching the finding model
7. Use Zod for schema validation where appropriate
8. Write a brief summary of what you implemented to $ARTIFACTS_DIR/summary.md

## Key constraints

- Bun/TypeScript only (no Python for MVP)
- Rule catalog is YAML-driven — analyzers load rules, not hardcode them
- Pluggable analyzer backend interface (but only `builtin-ts` for now)
- CLI is the primary interface
