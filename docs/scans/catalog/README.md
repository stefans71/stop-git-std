# Scan catalog (rendered outputs)

All 27 catalog-referenced V2.4 + V2.5-preview scans live here as `GitHub-Scanner-<repo>.{md,html}` pairs (Archon has a `.md`-only re-run record). The live catalog table — verdict, shape, methodology, rendering pipeline — is `docs/scanner-catalog.md`.

## Reference exemplar

**`GitHub-Scanner-ghostty-v12.{md,html}`** is the gold-standard exemplar for V1.2-schema wild scans. It was the first V1.2 scan + first override-explained scan; it is structurally clean, recent, and demonstrates a typical Caution-verdict shape without unusual edge cases.

When showing someone "what does a finished V1.2 scan look like" or referencing report shape in design discussions, use ghostty-v12.

For the **structural** anchors (form.json shape, DOM template, CSS, schema), see:

- Form structure: `tests/fixtures/{zustand,caveman,archon-subset}-form.json`
- DOM template: `docs/GitHub-Repo-Scan-Template.html`
- Visual contract: `docs/scanner-design-system.css`
- Schema: `docs/scan-schema.json`
- Per-scan authoring template: `docs/scan-authoring-template/`

## Superseded variants

Scans that are no longer current versions of their repo's catalog entry live in `docs/archive/scans-superseded/`. As of the session-8 cleanup that includes:

- `GitHub-Scanner-agency-agents.{md,html}` — early V2.x scan, never promoted to catalog
- `GitHub-Scanner-open-lovable.{md,html}` — early V2.x scan, never promoted to catalog
- `GitHub-Scanner-zustand-v2.{md,html}` — intermediate V2.x state superseded by `zustand-v3` (catalog entry 10)
