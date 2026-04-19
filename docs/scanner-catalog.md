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
| 2 | [coleam00/Archon](https://github.com/coleam00/Archon) | `3dedc22` | 2026-04-16 | Caution (split) | Deployment · | Complex agentic platform; open vulns; split-verdict with open PR gates; sha256-verified binary distribution | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-Archon.html) · [md](GitHub-Scanner-Archon.md) |
| 3 | [coleam00/Archon](https://github.com/coleam00/Archon) (re-run) | `2732288` | 2026-04-16 | (determinism record) | -- | Re-run record confirming Archon scan's verdict held across dev SHA bump; no structural drift | `methodology-used: path-a` (continuous) | `v2.4` | [md](GitHub-Scanner-Archon-rerun-record.md) |
| 4 | [pmndrs/zustand](https://github.com/pmndrs/zustand) | `3201328` | 2026-04-16 | Caution (split) | Version · | Pure JS/TS library; zero runtime deps; C20 boundary case (31 days); single-entry package | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-zustand.html) · [md](GitHub-Scanner-zustand.md) |
| 5 | [sharkdp/fd](https://github.com/sharkdp/fd) | `a665a3b` | 2026-04-16 | Caution (split) | Deployment · | Rust CLI with multi-platform binaries + SLSA attestations; mature governance | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-fd.html) · [md](GitHub-Scanner-fd.md) |
| 6 | [grapeot/gstack](https://github.com/grapeot/gstack) | `2300067` | 2026-04-16 | Caution (split) | Version · + Deployment · | Dense agent-rule surface (F7); install-from-main amplifier; V2.4 rule-calibration sub-finding | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-gstack.html) · [md](GitHub-Scanner-gstack.md) |
| 7 | [stefans71/stop-git-std](https://github.com/stefans71/stop-git-std) / archon-board-review | `4cea18d` | 2026-04-16 | Caution | -- | Tiny self-scan; zero-blast-radius framing; scanner-coverage-gap finding; no-CI repo | `methodology-used: path-a` (continuous) | `v2.4` | [html](GitHub-Scanner-archon-board-review.html) · [md](GitHub-Scanner-archon-board-review.md) |
| 8 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | `764536b` | 2026-04-17 | Caution | -- | First org-owned repo; first Python platform; open security issues; 5 vulns via issue search | `methodology-used: path-b` (delegated) | `v2.4` | [html](GitHub-Scanner-hermes-agent.html) · [md](GitHub-Scanner-hermes-agent.md) |
| 9 | [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) | `386fc7b` | 2026-04-17 | Caution | -- | Web application; first CVE hits (8 via advisory API); first `pull_request_target` finding; Docker defaults | `methodology-used: path-b` (delegated) | `v2.4` | [html](GitHub-Scanner-postiz-app.html) · [md](GitHub-Scanner-postiz-app.md) |
| 10 | [pmndrs/zustand](https://github.com/pmndrs/zustand) (V2.4 re-scan) | `3201328` | 2026-04-17 | Clean | -- | V2.4 methodology validation re-scan; OSSF Scorecard 5.9/10; first scan with V2.4 coverage cells | `methodology-used: path-b` (delegated) | `v2.4` | [html](GitHub-Scanner-zustand-v3.html) · [md](GitHub-Scanner-zustand-v3.md) |

**Current count: 10 entries (9 full scans + 1 re-run determinism record), all `rendering-pipeline: v2.4`.** JSON-first Trigger #1 fires at 10 full scans — **TRIGGER MET**. Step G will produce the first `v2.5-preview` entry.

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
5. **Tag `rendering-pipeline`** on every entry: `v2.4` for LLM-authored MD+HTML (all current 10 entries), `v2.5-preview` for JSON-first scans rendered via `docs/render-md.py`/`render-html.py` (Step G — see Operator Guide §8.8). Do NOT use `v2.5-preview` for production scans until Step G passes acceptance.

---

## Changelog

- **2026-04-16** — Catalog created as part of V0.1 Operator Guide promotion. Initial 7 entries (6 full scans + 1 re-run record) migrated from inline §13 of the DRAFT guide. All entries use `methodology-used: path-a`.
- **2026-04-19** — Added `rendering-pipeline` column (all 10 existing entries tagged `v2.4`). Methodology column annotated with canonical `continuous`/`delegated` names alongside legacy `path-a`/`path-b` flag values. Rename done per U-1 board review (`docs/External-Board-Reviews/041826-step-g-kickoff/`) to eliminate naming collision with the V2.4/V2.5-preview rendering-pipeline axis introduced when `docs/render-md.py` and `docs/render-html.py` shipped in commits `402f933` + `ce698d4`.
