# Scanner Catalog — Prior Scans

The live catalog of all completed scans using the V2.3/V2.4/V2.5-preview scanner pipeline. Each entry records the repo, commit, verdict, shape, execution mode, and rendering pipeline so future scans can:

1. **Find a shape-matched reference scan** for structural guidance (see `SCANNER-OPERATOR-GUIDE.md` §8.3 handoff-packet rule — pick the shape-closest prior scan).
2. **Track rule-calibration observations** that accumulate toward board-review triggers.
3. **Count toward JSON-first migration triggers** (Trigger #1 fires at 10 scans — MET).
4. **Distinguish V2.4 outputs from V2.5-preview outputs** so operators don't conflate the two pipelines (V2.5-preview is Step G validation only; see Operator Guide §8.8).

---

## Catalog entries

Column notes:
- **Methodology** — legacy `methodology-used: path-a` / `path-b` flag values. Canonical current name is "execution mode" with values `continuous` / `delegated` (renamed 2026-04-19 to eliminate naming collision with rendering-pipeline axis). Old flag values preserved for historical traceability.
- **Rendering pipeline** — `v2.4` for LLM-authored MD+HTML (all 10 entries currently). `v2.5-preview` will appear when Step G produces the first live JSON-first scan.

| # | Repo | HEAD SHA | Date | Verdict | Scope axis | Shape / structural pattern | Methodology | Rendering pipeline | Artifacts |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | `c2ed24b` | 2026-04-16 | Critical (split) | Version · + Deployment · | Curl-pipe-from-main installer; solo maintainer; 12-day-old repo with 32k stars | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-caveman.html) · [md](GitHub-Scanner-caveman.md) |
| 2 | [coleam00/Archon](https://github.com/coleam00/Archon) | `3dedc22` | 2026-04-16 | Critical (split) | Deployment · | Complex agentic platform; open vulns; split-verdict with open PR gates; sha256-verified binary distribution | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-Archon.html) · [md](GitHub-Scanner-Archon.md) |
| 3 | [coleam00/Archon](https://github.com/coleam00/Archon) (re-run) | `2732288` | 2026-04-16 | (determinism record) | -- | Re-run record confirming Archon scan's verdict held across dev SHA bump; no structural drift | `methodology-used: path-a` (continuous) | `v2.4` | [md](GitHub-Scanner-Archon-rerun-record.md) |
| 4 | [pmndrs/zustand](https://github.com/pmndrs/zustand) | `3201328` | 2026-04-16 | Caution (split) | Version · | Pure JS/TS library; zero runtime deps; C20 boundary case (31 days); single-entry package | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-zustand.html) · [md](GitHub-Scanner-zustand.md) |
| 5 | [sharkdp/fd](https://github.com/sharkdp/fd) | `a665a3b` | 2026-04-16 | Caution (split) | Deployment · | Rust CLI with multi-platform binaries + SLSA attestations; mature governance | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-fd.html) · [md](GitHub-Scanner-fd.md) |
| 6 | [grapeot/gstack](https://github.com/grapeot/gstack) | `2300067` | 2026-04-16 | Caution (split) | Version · + Deployment · | Dense agent-rule surface (F7); install-from-main amplifier; V2.4 rule-calibration sub-finding | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-gstack.html) · [md](GitHub-Scanner-gstack.md) |
| 7 | [stefans71/stop-git-std](https://github.com/stefans71/stop-git-std) / archon-board-review | `4cea18d` | 2026-04-16 | Caution | -- | Tiny self-scan; zero-blast-radius framing; scanner-coverage-gap finding; no-CI repo | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-archon-board-review.html) · [md](GitHub-Scanner-archon-board-review.md) |
| 8 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | `764536b` | 2026-04-17 | Caution | -- | First org-owned repo; first Python platform; open security issues; 5 vulns via issue search | `methodology-used: path-b` (delegated) | `v2.4` | [html](GitHub-Scanner-hermes-agent.html) · [md](GitHub-Scanner-hermes-agent.md) |
| 9 | [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) | `386fc7b` | 2026-04-17 | Caution | -- | Web application; first CVE hits (8 via advisory API); first `pull_request_target` finding; Docker defaults | `methodology-used: path-b` (delegated) | `v2.4` | [html](GitHub-Scanner-postiz-app.html) · [md](GitHub-Scanner-postiz-app.md) |
| 10 | [pmndrs/zustand](https://github.com/pmndrs/zustand) (V2.4 re-scan) | `3201328` | 2026-04-17 | Clean | -- | V2.4 methodology validation re-scan; OSSF Scorecard 5.9/10; first scan with V2.4 coverage cells | `methodology-used: path-b` (delegated) | `v2.4` | [html](GitHub-Scanner-zustand-v3.html) · [md](GitHub-Scanner-zustand-v3.md) |
| 11 | [multica-ai/multica](https://github.com/multica-ai/multica) | `b8907dd` | 2026-04-19 | Caution (split) | Deployment · | Agentic task management platform (Go CLI + Electron + Next.js + Docker self-host); curl-pipe-from-main with no binary checksum on Linux/Mac; 888888 dev auth bypass; no branch protection; 1% review rate; GoReleaser checksums on release assets | `methodology-used: path-b` (delegated) | `v2.4` | [html](GitHub-Scanner-multica.html) · [md](GitHub-Scanner-multica.md) |
| 12 | [pmndrs/zustand](https://github.com/pmndrs/zustand) (Step G pilot) | `3201328` | 2026-04-20 | Caution | -- | **Step G acceptance run, target 1 of 3.** V2.5-preview JSON-first pipeline validation at pinned V2.4 SHA. Cell-by-cell structural parity vs V2.4 comparator (entry #10) cleared. 4 findings (F0-F3), Q1 amber / Q2 green / Q3 amber / Q4 green. Commit `2c13324`. | `methodology-used: continuous` | `v2.5-preview` | [html](GitHub-Scanner-zustand-v3-v25preview.html) · [md](GitHub-Scanner-zustand-v3-v25preview.md) |
| 13 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (Step G) | `c2ed24b` | 2026-04-20 | Critical (split) | Version · | **Step G acceptance run, target 2 of 3.** Fresh form authoring from newly-created bundle at `docs/board-review-data/scan-bundles/caveman-c2ed24b.md`; first redo after initial attempt reverted (`e24e695` → `8a23ee8`) for fixture content reuse. 5 findings (F0/F5/F11/F14/F16), Q1 red via governance-floor override / Q2 amber via closed_fix_lag_days=5 / Q3 red / Q4 red. Commit `ed68fae`. | `methodology-used: continuous` | `v2.5-preview` | [html](GitHub-Scanner-caveman-v25preview.html) · [md](GitHub-Scanner-caveman-v25preview.md) |
| 14 | [coleam00/Archon](https://github.com/coleam00/Archon) (Step G) | `3dedc22` | 2026-04-20 | Critical (split) | Deployment · | **Step G acceptance run, target 3 of 3.** Fresh form authoring from newly-created bundle at `docs/board-review-data/scan-bundles/Archon-3dedc22.md`. 9 findings (F0-F8), Q1 red / Q2 amber / Q3 amber (post-U-11 catalog correction) / Q4 red. Split on Deployment: default installers vs shared-host Codex users. Commit `be56935`. | `methodology-used: continuous` | `v2.5-preview` | [html](GitHub-Scanner-Archon-v25preview.html) · [md](GitHub-Scanner-Archon-v25preview.md) |

**Current count: 14 entries — 11 `rendering-pipeline: v2.4` (10 full scans + 1 re-run determinism record) + 3 `rendering-pipeline: v2.5-preview` (Step G acceptance runs at pinned V2.4 SHAs, entries 12–14).** Step G acceptance matrix **PASSED 3/3** (all 7 gates clear on every target). V2.5-preview remains preview-status until the first unfixtured production scan proves the pipeline beyond the 3 known shapes.

---

## Rule-calibration observations (toward Trigger #2 — need 3+, have 2)

1. **gstack (scan #6):** C20 "release in 30 days" has semantic mismatch for install-from-main repos that don't cut releases.
2. **archon-board-review (scan #7):** V2.3 F7 misses Archon-ecosystem `commands/*.md` YAML-frontmatter files.

---

## How to use this catalog

1. **Pick the shape-closest prior scan** as a structural reference for your new scan. Shape match is about the repo's distribution model and finding surface, not its language or star count.
2. **Include 1–2 reference scans** in the portable handoff packet (§8.3 of the Operator Guide). Use the structure (verdict layout, scorecard shape, exhibit grouping) — **never copy content**.
3. **After completing a scan**, add a new row to this table (Phase 6a of the Operator Guide).
4. **Tag `methodology-used`** on every entry: `path-a` for continuous single-session scans (execution mode: continuous), `path-b` for delegated scans (execution mode: delegated) — see Operator Guide §8.1/§8.2.
5. **Tag `rendering-pipeline`** on every entry: `v2.4` for LLM-authored MD+HTML, `v2.5-preview` for JSON-first scans rendered via `docs/render-md.py`/`render-html.py` (Step G acceptance runs at pinned V2.4 SHAs — see Operator Guide §8.8). Step G acceptance matrix cleared on 3 shapes (entries 12–14). **V2.5-preview is NOT yet production-cleared** — continue using V2.4 for catalog and user-facing production scans until the first unfixtured wild scan on a shape outside {zustand, caveman, Archon} passes all 7 gates. That wild-scan trigger promotes V2.5-preview from "Step-G-validated" to "production-cleared."

---

## Changelog

- **2026-04-16** — Catalog created as part of V0.1 Operator Guide promotion. Initial 7 entries (6 full scans + 1 re-run record) migrated from inline §13 of the DRAFT guide. All entries use `methodology-used: path-a`.
- **2026-04-19** — Added `rendering-pipeline` column (all 10 existing entries tagged `v2.4`). Methodology column annotated with canonical `continuous`/`delegated` names alongside legacy `path-a`/`path-b` flag values. Rename done per U-1 board review (`docs/External-Board-Reviews/041826-step-g-kickoff/`) to eliminate naming collision with the V2.4/V2.5-preview rendering-pipeline axis introduced when `docs/render-md.py` and `docs/render-html.py` shipped in commits `402f933` + `ce698d4`. Added entry #11: multica-ai/multica (path-b delegated, v2.4).
- **2026-04-20** — Step G acceptance matrix passed 3/3. Added entries #12 (zustand Step G pilot, commit `2c13324`), #13 (caveman Step G, commit `ed68fae` — re-authored after `e24e695` reverted as `8a23ee8`), #14 (Archon Step G, commit `be56935`). First three `v2.5-preview` entries. V2.5-preview remains preview-status until first unfixtured wild scan passes all 7 gates. SF1 scorecard-calibration board (`042026-sf1-calibration/`) resolved the compute.py↔V2.4-comparator drift that surfaced pre-pilot; 4 temporary-compatibility patches + U-11 single-cell Archon Q3 catalog correction (green → amber) applied en route to gate-6.3 clear.
