# Sprint 2: tree-sitter AST Module — Archon Implementation Plan

## Context

stop-git-std is a programmatic Git repo safety auditor (17k lines, Bun/TypeScript). Regex-only detection produces false ABORTs on 25% of tested repos (PowerShell, Google WS CLI) because pattern matching can't distinguish "this code IS an execution engine" from "this code USES execution unsafely." A 3-model board review (Review 5, unanimous) concluded: **AST analysis via tree-sitter with auto-escalation (Option D) is the immediate priority.** This is a correctness fix, not a feature.

## Board Decision (Review 5, Unanimous)

- **Architecture:** Option D — auto-escalation default + `--quick`/`--deep` CLI flags
- **Technology:** tree-sitter (multi-language, Bun-native), NOT Python subprocess
- **Integration:** AST runs automatically between suppressions and scoring when low-confidence hard-stop findings exist. User sees one set of results, not two stages.
- **Failure mode:** If tree-sitter can't parse a file, fall back to Stage 1 result
- **Trigger:** Low-confidence hard-stop findings only (existing STAGE2_MODULE_MAP)

## Execution Strategy for Archon

This plan will be consumed by `archon-board-plan-to-pr`. The codebase is 17k lines. Key guidance:

1. **Read before writing** — the pipeline is mature. Integration points are specific.
2. **Do not rewrite existing files** — modify surgically at the documented line numbers.
3. **The AST module is NEW code** — `src/analyzers/stage2/` doesn't exist yet.
4. **Test against real repos** — verify with `bun run src/cli.ts https://github.com/PowerShell/PowerShell`

---

## Milestone 1: Install tree-sitter + language grammars

### Task 1.1: Add dependencies
```bash
bun add web-tree-sitter
bun add tree-sitter-wasms
```

`web-tree-sitter` is the WASM-based tree-sitter runtime (Bun-compatible, no native bindings).
`tree-sitter-wasms` provides pre-built WASM grammar files for all major languages.

If `tree-sitter-wasms` is not available or doesn't cover C#/Rust/Go, use individual grammar packages:
- `tree-sitter-typescript`, `tree-sitter-javascript`, `tree-sitter-python`
- `tree-sitter-c-sharp`, `tree-sitter-rust`, `tree-sitter-go`

### Task 1.2: Verify tree-sitter works in Bun
Create a quick smoke test: parse a `.ts` file, walk AST, confirm it works.
```typescript
import Parser from "web-tree-sitter";
await Parser.init();
const parser = new Parser();
// load TypeScript grammar, parse a file, print root node type
```

### Acceptance: `bun test` passes with tree-sitter imported. Grammar loading works.

---

## Milestone 2: AST analyzer module

### Task 2.1: Create `src/analyzers/stage2/ast-analyzer.ts`

This is the core module. It implements `AnalyzerModule` interface from `src/plugins/analyzer-backend.ts:13-21`:

```typescript
export interface AnalyzerModule {
  name: string;
  analyze(
    workspace: LocalWorkspace,
    profile: RepoProfile,
    context: AuditContext,
    rules: RuleDefinition[],
  ): Promise<AnalyzerOutput>;
}
```

**But the AST module has a different contract than Stage 1 analyzers.** It doesn't scan all files for all rules. It receives specific findings from Stage 1 and validates them. Design:

```typescript
export interface AstAnalyzerInput {
  findings: Finding[];           // Stage 1 findings to validate
  triggers: Stage2Trigger[];     // Which findings need AST validation
  workspace: LocalWorkspace;
}

export interface AstAnalyzerOutput {
  updatedFindings: Finding[];    // Same findings with adjusted confidence
  moduleResult: ModuleResult;
}

export async function analyzeWithAst(input: AstAnalyzerInput): Promise<AstAnalyzerOutput>
```

**Core logic per finding:**
1. Get the flagged file path(s) from `finding.files`
2. Determine language from file extension → load appropriate grammar
3. Parse the file with tree-sitter
4. For each regex match location (from `finding.line_numbers`):
   - Walk AST to find the node at that line
   - Classify the node's context:
     - **String literal / comment / regex literal** → finding is false positive → set `confidence: "dismissed"` or remove
     - **Function call / method invocation / import** → finding is confirmed → keep `confidence` as-is or upgrade
     - **Variable name / type annotation / class name** → ambiguous → keep as `confidence: "low"`
5. Return updated findings

**Language → grammar mapping:**
```typescript
const GRAMMAR_MAP: Record<string, string> = {
  ".ts": "typescript", ".tsx": "tsx", ".js": "javascript", ".jsx": "javascript",
  ".py": "python",
  ".rs": "rust",
  ".go": "go",
  ".cs": "c_sharp",
  ".java": "java",
  ".rb": "ruby",
};
```

**AST node classification rules:**
- `string_literal`, `template_string`, `raw_string_literal`, `comment`, `line_comment`, `block_comment` → **dismiss** (false positive)
- `call_expression`, `method_invocation`, `function_call`, `macro_invocation` → **confirm** (real finding)
- `identifier` in a `class_declaration`, `struct_declaration`, `type_alias` → **ambiguous** (lower confidence)
- `import_declaration`, `use_declaration`, `require` → **confirm** if importing dangerous module

### Task 2.2: Grammar loader with caching

```typescript
// src/analyzers/stage2/grammar-loader.ts
const parserCache = new Map<string, Parser>();

export async function getParser(language: string): Promise<Parser | null> {
  if (parserCache.has(language)) return parserCache.get(language)!;
  try {
    await Parser.init();
    const parser = new Parser();
    // Load WASM grammar for the language
    const lang = await Parser.Language.load(grammarPath(language));
    parser.setLanguage(lang);
    parserCache.set(language, parser);
    return parser;
  } catch {
    return null; // Unsupported language — fall back to Stage 1
  }
}
```

### Acceptance: Module can parse TS, Python, Rust, Go, C# files and classify AST nodes.

---

## Milestone 3: Pipeline integration (Option D auto-escalation)

### Task 3.1: Modify `src/engine/run-audit.ts`

**Current flow (lines 155-240):**
```
Phase 8: normalize + suppress → Phase 9: score → Phase 10: policy → Stage 2 detection → build result
```

**New flow:**
```
Phase 8: normalize + suppress → Phase 8.5: AST auto-escalation → Phase 9: score → Phase 10: policy → build result
```

Insert AFTER line 161 (after suppressions applied) and BEFORE line 163 (scoring):

```typescript
// Phase 8.5: AST auto-escalation (Option D)
if (!request.skip_stage2) {
  const hardStopPatterns: string[] = catalog.policy_baselines.hard_stop_patterns;
  const astCandidates = findings.filter(
    (f) => !f.suppressed && hardStopPatterns.includes(f.id) &&
    STAGE2_MODULE_MAP[f.id] === "ast"
  );

  if (astCandidates.length > 0) {
    const astResult = await analyzeWithAst({
      findings: astCandidates,
      triggers: astCandidates.map(f => ({
        finding_id: f.id,
        reason: "Auto-escalation: verifying regex match context",
        recommended_module: "ast" as const,
      })),
      workspace,
    });

    // Replace findings with AST-validated versions
    const astFindingIds = new Set(astCandidates.map(f => `${f.id}|${(f.files ?? []).join(",")}`));
    findings = findings.map(f => {
      const key = `${f.id}|${(f.files ?? []).join(",")}`;
      if (astFindingIds.has(key)) {
        const updated = astResult.updatedFindings.find(u => 
          u.id === f.id && (u.files ?? []).join(",") === (f.files ?? []).join(",")
        );
        return updated ?? f;
      }
      return f;
    });

    // Remove dismissed findings (confidence === "dismissed")
    findings = findings.filter(f => f.confidence !== "dismissed");

    allModuleResults.push(astResult.moduleResult);
  }
}
```

**Move STAGE2_MODULE_MAP** to module scope (above `runAudit` function) since it's now used in two places.

**Remove or simplify the existing Stage 2 detection block** (lines 176-209) — it now only needs to handle sandbox triggers (non-AST), since AST runs automatically.

### Task 3.2: Add `--quick` and `--deep` CLI flags

**File:** `src/cli.ts`
- `--quick` → sets `skip_stage2: true` (skip AST, fast scan only)
- `--deep` → sets `force_stage2: true` (run AST on ALL findings, not just hard-stop)

**File:** `src/models/audit-request.ts`
- Add `force_stage2: z.boolean().default(false)`

### Task 3.3: Add "dismissed" to Confidence enum

**File:** `src/models/enums.ts`
- Add `"dismissed"` to the Confidence union type
- Dismissed findings are removed from the results before scoring

### Acceptance: Running `bun run src/cli.ts https://github.com/PowerShell/PowerShell` no longer ABORTs on false positives. The `install-powershell.sh` curl|bash finding (GHA-EXEC-001) remains because it's a real finding (sandbox module, not AST).

---

## Milestone 4: Tests

### Task 4.1: AST analyzer unit tests
- `src/__tests__/ast-analyzer.test.ts`
- Test: string literal in TS → dismissed
- Test: function call in TS → confirmed
- Test: comment in Python → dismissed
- Test: method call in Rust → confirmed
- Test: unsupported language → returns original finding unchanged

### Task 4.2: Pipeline integration tests
- Test: finding with AST candidate triggers auto-escalation
- Test: `--quick` flag skips AST
- Test: `--deep` flag analyzes all findings
- Test: AST failure falls back gracefully

### Task 4.3: Regression tests
- All 188 existing tests still pass
- Run self-audit → still PROCEED
- Run Express → still PROCEED
- Run onecli → still ABORT (real findings unchanged)

### Acceptance: All tests pass. No regressions.

---

## Milestone 5: Verification against test repos

Run the full battery:
| Repo | Expected | Verify |
|------|----------|--------|
| Express | PROCEED | No change |
| FrontierBoard | PROCEED | No change (GHA-AI-003 already fixed) |
| onecli | ABORT | Real findings preserved |
| gstack | ABORT | Real AI agent findings preserved |
| self-audit | PROCEED | Suppressions still work |
| Google WS CLI | **CAUTION** (not ABORT) | AST dismisses `model.*exec` in data model code |
| PowerShell | **CAUTION or PROCEED_WITH_CONSTRAINTS** | AST dismisses C# shell source false positives. GHA-EXEC-001 (curl|bash) preserved. |
| nanoclaw | CAUTION | No change expected |

**Target: 8/8 correct decisions.**

---

## Critical Files

| File | Action | Lines |
|------|--------|-------|
| `src/analyzers/stage2/ast-analyzer.ts` | **CREATE** | New (~300-400 lines) |
| `src/analyzers/stage2/grammar-loader.ts` | **CREATE** | New (~80 lines) |
| `src/engine/run-audit.ts` | **MODIFY** | Insert Phase 8.5 after line 161, refactor Stage 2 block |
| `src/plugins/builtin-ts.ts` | **MODIFY** | Import + register AST module (if using AnalyzerModule interface) |
| `src/models/enums.ts` | **MODIFY** | Add "dismissed" to Confidence |
| `src/models/audit-request.ts` | **MODIFY** | Add `force_stage2` field |
| `src/cli.ts` | **MODIFY** | Add `--quick` and `--deep` flags |
| `src/__tests__/ast-analyzer.test.ts` | **CREATE** | New (~200 lines) |
| `package.json` | **MODIFY** | Add tree-sitter dependencies |

## Existing code to reuse
- `classifyFile()` from `src/analyzers/base.ts:89` — determine language from extension
- `scanFileContent()` from `src/analyzers/base.ts:44` — get line numbers of matches
- `emitFinding()` from `src/analyzers/base.ts:59` — create findings
- `STAGE2_MODULE_MAP` from `src/engine/run-audit.ts:186` — rule → module mapping
- `Finding` type from `src/models/finding.ts` — finding schema
- `AnalyzerOutput` from `src/plugins/analyzer-backend.ts:8` — module output interface

## Verification

1. `bun test` — all existing + new tests pass
2. `bun run src/cli.ts .` — self-audit PROCEED
3. `bun run src/cli.ts https://github.com/PowerShell/PowerShell` — NOT ABORT
4. `bun run src/cli.ts https://github.com/anthropics/anthropic-cookbook` — sane result
5. `bun run src/cli.ts https://github.com/onecli/onecli` — still ABORT (real findings)
