# Scan-authoring template — V1.2 wild-scan workflow

This directory holds canonical templates for the per-scan authoring scripts that produce a V1.2 wild-scan `form.json`. The templates are starting points for `.scan-workspaces/<repo>/` — see the workflow below.

## When to use this

Whenever you start a new V1.2 wild scan. Per `CLAUDE.md` scan instructions:

1. Wizard collects target + output mode + execution mode + shape + pipeline.
2. Pipeline V2.5-preview runs `python3 docs/phase_1_harness.py <owner/repo>` to produce `phase-1-raw.json`.
3. **Phase 4/5/6 authoring is not automated** — it's LLM-in-the-loop work that produces `form.json` from the harness output. The 3 scripts here drive that authoring deterministically once the data is filled in.

## Files

| Template | Purpose | What changes per scan |
|---|---|---|
| `build_form.py.template` | Reads `phase-1-raw.json` → runs Phase 3 compute → writes skeleton `form.json` (phases 1-3 + advisory; phases 4/5/6 empty). | Only the docstring + `$comment` field — the compute logic is fully generic. |
| `author_phase_4.py.template` | Fills `phase_4_structured_llm.*` (findings, evidence, scorecard cells, verdict exhibits, split axis, repo vitals, coverage detail, action steps, timeline events, executable file inventory, etc.). Also computes the Phase 4b verdict from finding severities. | Everything substantive — this is where the scan's actual judgment lives. |
| `author_phase_5_6.py.template` | Fills `phase_5_prose_llm.editorial_caption` + per-finding 2-3-paragraph prose; finalises Phase 6 assembly metadata. | Editorial caption + per-finding prose. |

## Workflow

```bash
# 1. Set up scan workspace
mkdir -p .scan-workspaces/<repo>
cd .scan-workspaces/<repo>

# 2. Capture HEAD SHA + run harness (head SHA is the first durable artifact)
gh api repos/<owner>/<repo>/commits/main --jq '.sha' > head-sha.txt
python3 ../../docs/phase_1_harness.py <owner>/<repo> \
  --head-sha "$(cat head-sha.txt)" \
  --scan-dir extract \
  --out phase-1-raw.json

# 3. Copy templates
cp ../../docs/scan-authoring-template/build_form.py.template build_form.py
cp ../../docs/scan-authoring-template/author_phase_4.py.template author_phase_4.py
cp ../../docs/scan-authoring-template/author_phase_5_6.py.template author_phase_5_6.py

# 4. Fill in build_form.py (just docstring + $comment) and run
python3 build_form.py
# → form.json with phases 1-3 + advisory populated, phases 4/5/6 empty, schema-clean

# 5. Author author_phase_4.py — this is the substantive work.
#    Use a recent .scan-workspaces/<other-repo>/author_phase_4.py as a content reference.
#    Run it: python3 author_phase_4.py
# → form.json with phase_4 + phase_4b populated, schema-clean

# 6. Author author_phase_5_6.py — editorial caption + per-finding prose
#    python3 author_phase_5_6.py
# → form.json with phase_5 + phase_6 complete, schema-clean

# 7. Render
cd ../..
python3 docs/render-md.py   .scan-workspaces/<repo>/form.json --out docs/scans/catalog/GitHub-Scanner-<repo>.md
python3 docs/render-html.py .scan-workspaces/<repo>/form.json --out docs/scans/catalog/GitHub-Scanner-<repo>.html

# 8. Validate (must all exit 0; --parity must be zero warnings)
python3 docs/validate-scanner-report.py --markdown docs/scans/catalog/GitHub-Scanner-<repo>.md
python3 docs/validate-scanner-report.py --report   docs/scans/catalog/GitHub-Scanner-<repo>.html
python3 docs/validate-scanner-report.py --parity   docs/scans/catalog/GitHub-Scanner-<repo>.md docs/scans/catalog/GitHub-Scanner-<repo>.html

# 9. Persist the form bundle (durability rule)
cp .scan-workspaces/<repo>/form.json docs/scan-bundles/<repo>-<short-sha>.json

# 10. Update catalog + telemetry, commit (see WILD-SCAN-PROCESS.md for the full post-render sequence)
```

## Common pitfalls

- **Editorial caption too long.** The validator's `--parity` mode searches the first 1,500 bytes of the rendered MD for a verdict marker. If the editorial caption + catalog metadata table push the `| Verdict | **Caution** |` row past byte 1,500, parity check emits "Could not extract verdict from MD for comparison" as a warning. Keep editorial caption under ~400 chars and `catalog_metadata.short_description` + `target_user` each under ~250 chars.
- **`threat_model_paths` enum.** Allowed values: `phishing`, `stale_token`, `session_compromise`, `malicious_extension`, `sloppy_review`, `runner_compromise`, `other`. NOT a free-text field.
- **`override_reason` enum (V13-1, 7 values).** `signal_vocabulary_gap`, `harness_coverage_gap`, `threshold_too_strict`, `threshold_too_lenient`, `missing_qualitative_context`, `rubric_literal_vs_intent`, `other`. Required when scorecard color differs from Phase 3 advisory; rationale must be ≥50 chars; `computed_signal_refs` must be non-empty and resolve against `compute.SIGNAL_IDS`.
- **Timeline labels max 40 chars.** Use `note` for longer detail.
- **`edge_case` is a string, not a bool.** Empty/no-edge-case → `None`.

## Reference scans (live exemplars)

The `.scan-workspaces/` directory holds the actual authoring scripts from completed wild scans. They're gitignored (per-scan scratch) but persist locally and serve as the richest reference. As of session 8: ghostty, kanata, wezterm, QuickLook, kamal, Xray-core, browser_terminal, Kronos, freerouting, WLED, Baileys, markitdown, skills.

For a quick visual sense of "what does the rendered output look like," see `docs/scans/catalog/_exemplar` (designated `GitHub-Scanner-ghostty-v12`, the first V1.2 wild scan + first override-explained scan).
