# Implementation Plan Review

**Reviewed**: `docs/implementation-plan.md` (enhanced with TypeScript code snippets)
**Against**: `docs/engine-contract.yaml` (v2), `docs/rule-catalog.yaml` (v2)
**Date**: 2026-04-13

## Pass/Fail Summary

| Check | Status | Notes |
|-------|--------|-------|
| Enum schemas | PASS | All enum values match YAML specs exactly |
| AuditRequest schema | PASS | All fields, types, defaults match engine contract |
| AuditContext schema | PASS | Required fields match; optional fields correct |
| RepoProfile schema | PASS | All nested objects match artifact definition |
| Finding schema | PASS | All required/optional fields match |
| Scores schema | PASS | Axes, confidence, component_breakdown match |
| Decision schema | PASS | All fields present and typed correctly |
| ModuleResult schema | PASS | Coverage sub-object matches |
| RunManifest schema | PASS | All fields present |
| RuleDefinition schema | PASS | Matches catalog rule structure |
| Scoring divisor (/20) | PASS | Confirmed in code and Confirmed Decisions table |
| Severity weights | PASS | info=1, low=3, medium=8, high=15, critical=25 |
| Confidence multipliers | PASS | low=0.6, medium=0.85, high=1.0 |
| Environment multipliers | PASS | All 5 values match contract and catalog |
| Trust credits | PASS | Values match contract: 8, 3, 2, 4 |
| Hard-stop rule IDs | PASS | All 10 IDs match `policy_baselines.hard_stop_patterns` |
| Module routing config | PASS | `library_package` included; router reads contract dynamically |
| All 7 typed analyzers | PASS | web, api, ai-llm, agent-framework, skills-plugins, mcp-server, library-package |
| Suppression file name | PASS | `.stop-git-std.suppressions.yaml` |
| Runtime validation no-op | PASS | Structural no-op in MVP |
| Commander for CLI | PASS | Confirmed in code |
| Trust signals from repo_profile | PASS | deriveTrustCredits uses absence-of-findings pattern |
| Policy profile thresholds | **FAIL** | Code doesn't read thresholds from contract at runtime; see Finding 1 |
| AuditContext missing policy_profile | **FAIL** | Policy code uses `(context as any).policy_profile`; see Finding 2 |
| Confidence model completeness | **FAIL** | Missing `ast_supported_for_major_languages` condition; see Finding 3 |
| Type consistency (Finding <-> RuleDefinition) | PASS | Both use same Severity/Confidence/ProofType enums |
| Deduplication key fields | PASS | Matches contract: `(id, files, evidence.type)` |
| Phase order | PASS | 11 phases, runtime_validation as structural no-op |

## Detailed Findings

### Finding 1: Policy evaluatePolicy() incorrectly hardcodes adoption_mode logic (MEDIUM)

**Location**: `src/engine/policy.ts`, plan lines 1546-1548

**Problem**: The code forces `"balanced"` profile for all `third_party` adoption modes, ignoring the user's explicitly chosen `policy_profile`:

```typescript
const profileName = context.adoption_mode === "third_party"
    ? "balanced"
    : (context as any).policy_profile ?? "balanced";
```

The engine contract has no such constraint. The user should be able to run `--policy strict` even when auditing a third-party repo.

**Fix**: Replace with direct policy_profile access (see Finding 2 for making it available).

### Finding 2: AuditContext is missing `policy_profile` field (MEDIUM)

**Location**: `src/models/audit-context.ts`, plan lines 220-234

**Problem**: The engine contract's `audit_context` artifact does NOT include `policy_profile` (it's only on `audit_request` and `run_manifest`). The policy code works around this with `(context as any).policy_profile`, which is a type-unsafe hack that will always be `undefined`.

**Fix**: Either:
- (a) Add `policy_profile` to `AuditContext` as an optional field (deviation from contract, but practical), OR
- (b) Pass `policy_profile` as a separate parameter to `evaluatePolicy()` from the `AuditRequest`

Option (b) is cleaner since it doesn't deviate from the contract schema:

```typescript
export function evaluatePolicy(
  findings: Finding[],
  scores: Scores,
  policyProfile: PolicyProfile,  // <-- add this parameter
  contract: EngineContract,
  catalog: RuleCatalog
): Decision {
  const profileConfig = contract.policy_profiles[policyProfile];
  // ...
}
```

### Finding 3: Confidence model missing AST condition (LOW)

**Location**: `src/engine/scoring.ts`, plan lines 1484-1505

**Problem**: The engine contract's `confidence_model.rules` (lines 784-798) specifies three conditions for `high` confidence:
1. `ast_supported_for_major_languages == true`
2. `failed_modules_ratio <= 0.10`
3. `runtime_mode in [build, smoke] or critical_static_findings_count >= 1`

The plan's `deriveConfidence()` implements conditions 2 and 3 but omits condition 1. Since MVP uses regex/heuristic fallback (no real AST), this means high confidence could be returned even though AST isn't actually supported.

**Fix**: Add AST support check. For MVP, this can always return false (since AST is stubbed), which would mean high confidence is harder to achieve:

```typescript
// Check if AST is supported for major languages in this repo
// MVP: always false since we use regex fallback
const astSupported = false; // TODO: implement when real AST parsing is added

if (astSupported && failedRatio <= 0.10 && (runtimeActive || hasCriticalStatic)) {
  return "high";
}
```

### Finding 4: Trust credits subtracted from all axes (INFORMATIONAL)

**Location**: `src/engine/scoring.ts`, plan lines 1441-1445

**Observation**: The plan subtracts trust credits from all three axes (trustworthiness, exploitability, abuse_potential). The engine contract's formula says `min(100, max(0, round(sum(weighted_axis_values) - trust_credits)))` per axis, which could be read either way. This is consistent with the plan's approach. However, trust signals like "signed_tags_present" arguably only affect trustworthiness, not exploitability.

**Status**: Acceptable for MVP. Consider axis-specific trust credits in a future iteration.

### Finding 5: Engine contract scoring formula discrepancy is documented (INFORMATIONAL)

**Location**: Plan line 13, engine contract line 830

**Observation**: The engine contract still contains `/ 10` in the formula at line 830:
```
weighted_axis_value = axis_impact * severity_weight * confidence_multiplier / 10
```

The plan correctly uses `/20` per Confirmed Decision #7. The discrepancy is documented in the "Resolved Contradictions" section. The engine contract YAML should be updated to `/20` to stay in sync, but this is outside the scope of the plan review.

### Finding 6: Missing SARIF reporter (LOW)

**Location**: Plan Milestone 4, file manifest

**Problem**: The engine contract lists SARIF as a supported output format (line 22) and defines `sarif_mapping` (lines 966-977). The plan mentions `sarif` in the `OutputFormat` enum but does not include a `src/reporting/sarif.ts` file in the file manifest or Milestone 4 tasks. The plan lists only terminal, JSON, and markdown reporters.

**Fix**: Either add a `src/reporting/sarif.ts` file to M4 or M5, or document it as a future addition.

### Finding 7: `audit-result.ts` not in models barrel export (INFORMATIONAL)

**Location**: Plan line 457 (index.ts)

**Observation**: The barrel export at `src/models/index.ts` (line 457) includes `export * from "./audit-result"`, so this is actually correct. No fix needed.

### Finding 8: RuleCatalog schema expects `policy_baselines` at top level (LOW)

**Location**: `src/rules/types.ts`, plan lines 560-564

**Problem**: The `RuleCatalogSchema` expects `policy_baselines` as a top-level key in the rule catalog YAML. Checking the actual YAML structure, `policy_baselines` IS at the top level (line 1560). This validates correctly.

**Status**: PASS - no issue.

## Missing Pieces

1. **SARIF reporter**: Not in file manifest (see Finding 6).
2. **Suppression loader**: The plan defines `SuppressionEntry` type and `applySuppressions()` function stub but does not include a file loader for `.stop-git-std.suppressions.yaml`. Should be added to the normalization module or as a utility in `src/engine/`.
3. **Error handling cases**: The engine contract defines specific error handling behaviors (lines 941-953: rule_parse_error, parser_not_supported, github_api_unavailable, osv_lookup_failed, runtime_sandbox_failed). The plan's `continueOnError` pattern covers the spirit of this but doesn't implement the specific downgrade/warning behaviors for each case.
4. **Coverage contract**: The engine contract (lines 955-965) requires reporting on `files_considered`, `files_scanned`, `files_skipped`, `unsupported_languages`, `failed_modules`, `partial_modules`, `runtime_executed`. The plan collects most of this via `ModuleResult.coverage` and `FileInventory` but doesn't assemble a coverage report artifact. This could be derived from existing data in the reporter.

## Overall Assessment: **NEEDS FIXES**

Three items need correction before the plan is ready for code generation:

1. **[MUST FIX]** Finding 2 + Finding 1: Pass `policy_profile` to `evaluatePolicy()` correctly instead of using `(context as any).policy_profile`. Remove the incorrect adoption_mode-based override logic.
2. **[SHOULD FIX]** Finding 3: Add the AST support condition to `deriveConfidence()`, defaulting to `false` for MVP.
3. **[SHOULD FIX]** Finding 6: Add SARIF reporter to the file manifest, even as a stub.

All other checks pass. The Zod schemas are accurate, scoring constants are correct, hard-stop rules match, module routing is properly configured, and the type system is internally consistent.
