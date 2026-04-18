# Board Review: Progress Check — Are We On Track?

## What we've built this session (in order)

| # | Artifact | File | Tests | Board reviewed? |
|---|----------|------|-------|-----------------|
| 1 | Package V2 fixes (scorecard, paths, catalog) | 8 files modified | - | Yes (R1-R2) |
| 2 | Data lineage map (118 data points) | `.board-review-temp/data-lineage-map.md` | - | Yes (pipeline R1-R2) |
| 3 | Pipeline architecture (8/8/4 classification) | `docs/board-review-pipeline-methodology.md` | - | Yes (10 rounds total) |
| 4 | Validator test suite | `tests/test_validator.py` | 37 tests | Caught real bug (4 scans had wrong scorecard questions) |
| 5 | MD/HTML parity check | Added to `docs/validate-scanner-report.py` | 5 tests | - |
| 6 | Investigation form V1.1 | `docs/GitHub-Repo-Scan-Form.json` | - | Yes (3-model review, 23 gaps fixed) |
| 7 | JSON Schema V1.0 | `docs/scan-schema.json` | Schema validates blank form | - |
| 8 | 8 computation functions | `docs/compute.py` | 30 tests | - |
| **Total** | | | **67 tests, all passing** | |

## Current architecture (board-approved)

```
Phase 1:  LLM runs tools → fills GitHub-Repo-Scan-Form.json (incremental)
Phase 2:  Python validates raw data consistency
Phase 3:  compute.py computes 8 automatable fields (C20, scorecard, etc.)
Phase 4:  LLM fills 8 structured fields (enums/templates constrained)
Phase 4b: compute.py derives verdict from finalized findings
Phase 5:  LLM writes 4 prose fields (structural constraints)
Phase 6:  Assembler builds complete JSON with provenance tags
Phase 7:  render-md.py + render-html.py → deterministic output     ← NEXT
Phase 8:  validate-scanner-report.py gates the output
Phase 9:  Git hook spot-checks (5 commands re-run)
```

## What the board has NOT reviewed yet

1. **`docs/scan-schema.json`** — JSON Schema draft 2020-12, 30 $defs. Validates the investigation form. Enforces severity/status/provenance enums, evidence_refs required on non-OK findings.
2. **`docs/compute.py`** — The 8 automatable computation functions. Each is a deterministic decision tree from the V2.4 prompt calibration rules.

## What's next (renderers)

`render-md.py` and `render-html.py` — mechanical Python scripts that take a completed investigation form JSON and produce the final MD and HTML reports. These are deterministic: same JSON → same MD → same HTML.

## Questions for the board

1. **Are we on track?** Does the build order make sense? Is anything missing before we build renderers?

2. **Review compute.py** — Read `docs/compute.py`. Do the 8 functions correctly implement the V2.4 prompt calibration rules? Any edge cases missed?

3. **Review scan-schema.json** — Read `docs/scan-schema.json`. Does the schema correctly validate what the investigation form should contain? Any gaps?

4. **Review the investigation form** — Read `docs/GitHub-Repo-Scan-Form.json`. With the 23 fixes applied, is it complete enough for the renderer to produce zustand-quality output?

5. **Renderer design question:** The renderer needs to map JSON fields to the exact HTML template structure (section ordering, CSS classes, finding card layout). Should we:
   - A: Build the renderer from scratch using the template as a guide
   - B: Parse the existing zustand.html gold standard and reverse-engineer the renderer from it
   - C: Use the HTML template (`GitHub-Repo-Scan-Template.html`) as a literal template with placeholder substitution

6. **Should we test the pipeline end-to-end on zustand BEFORE building renderers?** i.e., manually fill the investigation form with zustand data, run compute.py, verify the computed outputs match what's in zustand.md?

## Files to read

1. `docs/compute.py` — 8 computation functions (~280 lines)
2. `docs/scan-schema.json` — JSON Schema (~400+ lines)
3. `docs/GitHub-Repo-Scan-Form.json` — Investigation form V1.1 (~480 lines)
4. `docs/validate-scanner-report.py` — Validator with parity check (~530 lines)
5. `github-scan-package-V2/repo-deep-dive-prompt.md` — V2.4 prompt (for cross-reference)

## Verdict options

- **ON TRACK** — proceed to renderers
- **ON TRACK WITH CONDITIONS** — fix specific items first
- **COURSE CORRECT** — we're heading in the wrong direction on something
