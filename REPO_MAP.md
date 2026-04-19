# Repository Map — stop-git-std

**Last audited:** 2026-04-19 03:47 UTC
**HEAD at audit:** `3c09afb` (U-3/FX-4: fixture provenance landed)
**Regeneration:** this file is hand-maintained. Run `git log -1 --format='%ai' -- <path>` to verify any listed timestamp.

This is the "where does everything live AND what ships" doc. If you're Claude starting a fresh session, read `CLAUDE.md` first for operating instructions, then come here for the index.

Three sections:
- **§1 Work done** — historical + existing artifacts
- **§2 Current plan + continue-building context** — where we are, next steps, how to run the board
- **§3 File/folder index + release status** — the categorized directory

---

## 1. Work done

### 1.1 Phase 7 renderer plan (A→G)

Canonical plan: `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md`

| Step | Status | Key commit(s) |
|---|---|---|
| A — Schema freeze V1.1 (renderer-driven $defs, C2/C3 conditionals) | ✅ Done | `2b576bf` + `c6531bb` |
| B — render-md.py → Jinja2 thin shim + 14 partials | ✅ Done | `75db969` |
| C — Zustand fixture enrichment (10 FAs) | ✅ Done | `59224ac` |
| D — Flip render tests to structural assertions | ✅ Done | `aac2b3b` |
| E — Validator `--report` gate on rendered MD | ✅ Done | `cf8c576` |
| F — HTML renderer + cross-shape fixtures + R3 XSS/CSS/parity fixes | ✅ Done | `402f933` + `ce698d4` |
| — U-1 (Step G doc integration) | ✅ Done | `6a3e471` |
| — FX-3b parallel (package validator sync) | ✅ Done | `60e0bf2` |
| — U-3/FX-4 (fixture provenance) | ✅ Done | `3c09afb` |
| **G — C7 acceptance matrix (live JSON-first pipeline on 3 shapes)** | ⏳ Next, board required | — |

### 1.2 Board reviews archive (`docs/External-Board-Reviews/`, 63 files across 6 folders)

Index master: `docs/External-Board-Reviews/README.md`

| Folder | Scope | Verdict | Rounds |
|---|---|---|---|
| `041626-celso/` | V2.3 pre-migration review | — | — |
| `041826-renderer-alignment/` | Phase 7 renderer plan A-G approval | ALL SIGN OFF | R1-R4 |
| `041826-renderer-impl-verify/` | Steps A+B implementation verification + STEP-E/STEP-F verification records + INDEX cross-ref | APPROVED post-owner-directive | R1 |
| `041826-fixture-enrichment/` | Step C 10-FA review | UNANIMOUS 3-0 APPROVE | R1 |
| `041826-step-f-alignment-validation/` | Step F validation + XSS/CSS/parity fixes | SIGN OFF 2 + W/DISSENTS 1 (bookkeeping) | R1-R4 |
| `041826-step-g-kickoff/` | U-1 doc integration, V2.5-preview pipeline | SIGN OFF 1 + W/DISSENTS 2 (non-blocking) | R1-R3 |

Older flat-file board records (pre-`External-Board-Reviews/` layout, kept for historical reference):
- `docs/board-review-V21-consolidation.md` · `V22` · `V23` — V2.1/V2.2/V2.3 scanner prompt reviews
- `docs/board-review-axiom-triage-consolidation.md` · `axiom-triage-R2-consolidation.md` — AXIOM findings triage
- `docs/board-review-operator-guide-consolidation.md` — V0.1 operator guide review
- `docs/board-review-package-v2-consolidation.md` — V2.4 package review
- `docs/board-review-pipeline-methodology.md` — JSON-first pipeline architecture decision (8/8/4, 9-phase) — canonical pipeline-architecture record

### 1.3 Completed scans (V2.4 catalog, 10 entries)

`docs/scanner-catalog.md` lists entries 1–10 (all `rendering-pipeline: v2.4`). Artifacts at `docs/GitHub-Scanner-<repo>.{html,md}`. Shape coverage: curl-pipe installer (caveman), agentic platform (Archon), JS library (zustand), Rust CLI (fd), Claude-Code skills (gstack), pre-distribution (archon-board-review), Python platform (hermes-agent), web app (postiz-app), plus zustand-v2/v3 revisions + Archon rerun record.

### 1.4 Historical / backfilled artifacts

- `docs/repo-deep-dive-prompt-V2.md` · `V2.1.md` · `V2.2.md` — prompt version archives (current is V2.4 at `docs/repo-deep-dive-prompt.md`)
- `docs/CHANGELOG.md` — prompt version history (V2.1→V2.4)
- `docs/GitHub-Repo-Scan-Form.json` — (check purpose; may be a backfilled artifact)
- `archive/` — old TypeScript static analyzer (101 files, historical; see §3.5)

---

## 2. Current plan + continue-building context

### 2.1 Architecture

**8/8/4 classification** (board-approved, canonical record `docs/board-review-pipeline-methodology.md`):
- 8 Automatable (Python compute) — verdict, scorecard cells, solo-maintainer, exhibit grouping, boundary-case, coverage status, methodology boilerplate, F5 silent/unadvertised
- 8 Structured LLM (enum/template constrained) — general vuln severity, split-axis, priority evidence, threat model, action steps, timeline, capability assessment, catalog metadata
- 4 Prose LLM (structural constrained) — what_this_means, what_this_does_NOT_mean, finding body, editorial caption

**9-phase pipeline:** tool-exec → validation → compute → structured-LLM → prose-LLM → assembly → render → validator → git-hook

**Invariants:** MD canonical / facts-inference-synthesis separate / pre-computed form contract / prose stays sparse / validator is the gate

### 2.2 Current state

- **HEAD:** `3c09afb` (2026-04-19 03:47 UTC) — U-3/FX-4 landed
- **Tests:** 263/263 passing (`python3 -m pytest tests/ -q`)
- **Validator on all 3 V1.1 fixtures:** `--report` clean, `--parity` zero errors + zero warnings
- **Repo↔package validator:** byte-identical (0 diff lines, synced in `60e0bf2`)
- **CSS:** 824 lines
- **Catalog:** 10 V2.4 scans (all `rendering-pipeline: v2.4`); Step G will produce the first V2.5-preview entry
- **Commits ahead of origin:** 53

### 2.3 Board runbook — how to run the 3-model governance board

**SOP:** `/root/.frontierboard/FrontierBoard/docs/REVIEW-SOP.md`

**Composition** (per SOP §4, minimum 3 agents):
- **Pragmatist** — Claude Sonnet 4.6 when Opus wrote the artifact (same-model blind spot rule); Opus otherwise. Via `Agent` tool.
- **Systems Thinker** — Codex GPT-5. Via `sudo -u llmuser` from `/tmp/`.
- **Skeptic** — DeepSeek V4. Via Qwen CLI from repo directory.

**Rounds:** minimum 3 (Blind → Consolidation → Confirmation). Add R3 Deliberation → R4 Confirmation (4-round) if R2 produces a split verdict.

**Invocation — Pragmatist (Sonnet 4.6):**
```
Agent tool
  subagent_type="general-purpose"
  model="sonnet"   (when Opus wrote the artifact)
  run_in_background=true
  prompt: "You are the Pragmatist on a 3-model FrontierBoard review. Read /tmp/<topic>-<round>-brief.md end-to-end. ... <role specifics>"
```

**Invocation — Systems Thinker (Codex GPT-5):**
```bash
sudo -u llmuser bash -c "cd /tmp && codex exec \
  --dangerously-bypass-approvals-and-sandbox '<prompt>'" \
  > /tmp/<topic>-codex-<round>.log 2>&1
```
Must be `llmuser` (auth tied to that user; running as root → 401 token expired). Must run from `/tmp` (repo-dir CLAUDE.md pulls Codex off-task). Brief file at `/tmp/<topic>-<round>-brief.md`.

**Invocation — Skeptic (DeepSeek V4):**
```bash
OPENAI_API_KEY="$DEEPSEEK_API_KEY" \
OPENAI_BASE_URL="https://api.deepseek.com/v1" \
  qwen -y -p "<prompt>" --model deepseek-chat \
  > .board-review-temp/<topic>/deepseek-<round>-raw.log 2>&1
```
Launch from repo directory (workspace scope includes repo files). `-y` = YOLO mode, required for file writes.

**Failure modes:**
- Codex 401 "token expired" → you're running as root; switch to `llmuser`
- DeepSeek `API Error: Connection error` / `terminated` → transient, retry once (succeeds ~90% of the time)
- Qwen "cannot access file" → launched from wrong directory

**File staging pattern** (during review):
```
.board-review-temp/<topic>/
  r1-brief.md · r2-brief.md · r3-brief.md · r4-brief.md
  pragmatist-r1.md · codex-r1.md · deepseek-r1.md
  pragmatist-r2.md · codex-r2.md · deepseek-r2.md
  (etc.)
  deepseek-r<N>-raw.log    (qwen stdout capture)
```

**Archive pattern** (on sign-off):
```
docs/External-Board-Reviews/<MMDDYY>-<topic>/
  CONSOLIDATION.md       (final record — verdicts, resolutions, dissents, owner directives, agent-invocation snapshot)
  r{1..4}-brief.md
  {pragmatist,codex,deepseek}-r{1..4}.md
```
Then update `docs/External-Board-Reviews/README.md` master index.

**Brief essentials** (agents are STATELESS — re-read file even if you "wrote" it):
1. Full project context from scratch
2. All prior-round outputs inlined verbatim (R2+)
3. Absolute paths for files to READ
4. Required output format (§ structure, word cap)

**Recent examples to model after:**
- 4-round with split verdict: `docs/External-Board-Reviews/041826-step-f-alignment-validation/`
- 3-round with 2-1 owner-directive resolutions: `docs/External-Board-Reviews/041826-step-g-kickoff/`
- Fix-artifact-first governance: R3 brief has owner-authored BEFORE/AFTER, board votes SECOND/ADJUST/REJECT

### 2.4 Step G prerequisites queue

Per `docs/External-Board-Reviews/041826-step-g-kickoff/CONSOLIDATION.md`. Status as of HEAD `3c09afb`:

| Item | Scope | Status |
|---|---|---|
| U-1 | V2.5-preview doc integration | ✅ Done (`6a3e471`) |
| U-3/FX-4 | `tests/fixtures/provenance.json` — separate-file approach | ✅ Done (`3c09afb`) |
| U-5/PD3 | Bundle/citation validator — validate fact/inference/synthesis separation in findings-bundle.md | ⏳ Before first live Step G scan |
| U-10 | Re-validate all 10 catalog scans with fixed validator (check for shell-glob evidence corruption) | ⏳ Before first V2.5-preview promoted to catalog |

**Step G itself:** run full Phase 1-6 pipeline against 3 shapes (likely zustand + caveman + Archon), produce form.json → render-md.py + render-html.py → validator clean + parity zero warnings + structural-parity vs V2.4 scan of same repo. See `docs/SCANNER-OPERATOR-GUIDE.md` §8.8 for the operator-facing spec.

### 2.5 Deferred ledger

Non-active items tracked for future trigger:

- **Schema hardening** (Codex R2 defer-ledger) — `scan-schema.json` V1.1 doesn't fully formalize the prompt output spec. Gaps: Scanner Integrity section 00 hit-level structure; Section 08 methodology fields beyond version marker. Trigger: after Step G surfaces concrete schema pain.
- **`github-scan-package-V2/` V2.5 refresh** — full docs + renderer sync to package. Trigger: after Step G passes acceptance.
- **V1.1+ roadmap items** (from `docs/board-review-pipeline-methodology.md`): RD1 (automate structured LLM), SD2 (kind+domain typing), RD4 (assumptions field), PD3 (bundle validator — tied to U-5 above), SD3/SD4/SD7/SD8 (V1.2 schema items), SD9/SD10/RD5/PD1/PD4/PD6/PD7 (V2.0+). All triggers documented in the methodology record; none yet fired.
- **Terminology cleanup** (Codex R3 trailing dissent) — Operator Guide §8.1/§8.2 body prose still contains legacy "Path A/B" in explanatory text. Collision bug already fixed in wizard; lingering prose is cleanup, not urgent.
- **Catalog dual-label cosmetic** (Pragmatist R3 noted) — `methodology-used: path-a (continuous)` dual-label is transitional. Footnote-only variant possible later.

---

## 3. File/folder index + release status

Release status key:
- `release-ready` — ships with the open-source release
- `staged-v2.4` — ships as V2.4 distributable; post-Step-G refresh will bump to V2.5
- `corpus` — example scans / test fixtures; ships as demonstration material
- `governance` — board review archives; ships as transparent-dev evidence
- `dev-only` — useful in-repo but NOT in open-source release
- `historical` — older state, kept for reference but not a product concern
- `excluded` — runtime / scratch; should be gitignored

### 3.1 Product core (release-ready)

| Path | Purpose | Status | Last touched |
|---|---|---|---|
| `CLAUDE.md` | Repo operator instructions (cap 250 lines) | release-ready | 2026-04-19 |
| `REPO_MAP.md` | This file — navigation + release status + board runbook | release-ready | 2026-04-19 |
| `AUDIT_TRAIL.md` | Checkpoint log + revert recipes | release-ready | 2026-04-19 |
| `README.md` | Top-level repo intro | release-ready | 2026-04-17 |
| `.gitignore` | Git hygiene | release-ready | 2026-04-13 |
| `docs/SCANNER-OPERATOR-GUIDE.md` | V0.2 end-to-end operator process | release-ready | 2026-04-19 |
| `docs/Scan-Readme.md` | V2.4 human-readable wizard | release-ready | 2026-04-19 |
| `docs/repo-deep-dive-prompt.md` | V2.4 scanner prompt (investigation + output-format spec) | release-ready | 2026-04-19 |
| `docs/GitHub-Repo-Scan-Template.html` | V2.4 HTML template with placeholders | release-ready | 2026-04-17 |
| `docs/scanner-design-system.css` | 824-line mandatory V2.4 CSS | release-ready | 2026-04-17 |
| `docs/validate-scanner-report.py` | Validator (`--report`, `--parity`, `--markdown`, `--template`) | release-ready | 2026-04-18 |
| `docs/compute.py` | Python compute for Phase 3 automatable fields | release-ready | 2026-04-18 |
| `docs/render-md.py` | V2.5-preview MD renderer (117-line Jinja2 shim) | release-ready | 2026-04-18 |
| `docs/render-html.py` | V2.5-preview HTML renderer (135-line Jinja2 shim) | release-ready | 2026-04-18 |
| `docs/scan-schema.json` | V1.1 investigation form schema | release-ready | 2026-04-18 |
| `docs/templates/` | V2.5-preview MD Jinja2 partials (14 files) | release-ready | 2026-04-18 |
| `docs/templates-html/` | V2.5-preview HTML Jinja2 partials (14 files) | release-ready | 2026-04-18 |
| `tests/test_compute.py` | Phase 3 compute tests | release-ready | 2026-04-18 |
| `tests/test_validator.py` | Validator unit tests | release-ready | 2026-04-18 |
| `tests/test_render_md.py` | MD renderer structural tests | release-ready | 2026-04-18 |
| `tests/test_render_html.py` | HTML renderer structural tests | release-ready | 2026-04-18 |
| `tests/test_end_to_end.py` | End-to-end integration tests | release-ready | 2026-04-18 |
| `tests/fixtures/zustand-form.json` | V1.1 fixture — JS library shape | release-ready | 2026-04-18 |
| `tests/fixtures/caveman-form.json` | V1.1 fixture — curl-pipe installer shape | release-ready | 2026-04-18 |
| `tests/fixtures/archon-subset-form.json` | V1.1 fixture — agentic monorepo + C3 auto_load_tier path | release-ready | 2026-04-18 |
| `tests/fixtures/provenance.json` | Fixture provenance ledger (keyed by filename) | release-ready | 2026-04-19 |

### 3.2 Package V2.4 distributable (staged)

`github-scan-package-V2/` — 16 tracked files, self-contained V2.4 release snapshot.

| Path | Status | Notes |
|---|---|---|
| `github-scan-package-V2/CLAUDE.md` | staged-v2.4 | 119 lines, V2.4 Package header. Intentionally drifted from repo `CLAUDE.md` post-U-1. |
| `github-scan-package-V2/SCANNER-OPERATOR-GUIDE.md` | staged-v2.4 | Byte-identical to `docs/SCANNER-OPERATOR-GUIDE.md` BEFORE U-1. Now drifted (no §8.8). |
| `github-scan-package-V2/validate-scanner-report.py` | staged-v2.4 | ✅ Synced to repo in `60e0bf2` (FX-3 + FX-3b bug fixes; not V2.5 features) |
| `github-scan-package-V2/GitHub-Repo-Scan-Template.html` | staged-v2.4 | 10-line drift vs repo |
| `github-scan-package-V2/scanner-design-system.css` | staged-v2.4 | Byte-identical to repo |
| `github-scan-package-V2/repo-deep-dive-prompt.md` | staged-v2.4 | 24-line drift vs repo (repo has V2.5-preview blockquote) |
| `github-scan-package-V2/Scan-Readme.md` | staged-v2.4 | 102-line drift (old V2.3 / Path A/B terminology) |
| `github-scan-package-V2/scanner-catalog.md` | staged-v2.4 | 6 entries (repo has 10). Drift is intentional snapshot. |
| `github-scan-package-V2/CHANGELOG.md` | staged-v2.4 | Prompt version history |
| `github-scan-package-V2/reference/*` | staged-v2.4 | Reference scans bundled with package |

**Post-Step-G**: a dedicated "V2.5 package refresh" commit cycle will sync the package to current repo state (docs + renderer files + fixtures + schema) and bump to `github-scan-package-V2.5/` or similar.

### 3.3 Corpus (release-ready as demonstration)

| Path | Purpose | Status |
|---|---|---|
| `docs/GitHub-Scanner-<repo>.{md,html}` (10 scans × 2 formats) | Completed V2.4 catalog scans | corpus |
| `docs/GitHub-Scanner-Archon-rerun-record.md` | Determinism record for Archon dev-SHA bump | corpus |
| `docs/scanner-catalog.md` | Live catalog (10 entries, rendering-pipeline column) | release-ready (mutates each scan) |

### 3.4 Governance / transparent dev (release-ready)

| Path | Purpose | Status |
|---|---|---|
| `docs/External-Board-Reviews/README.md` | Master index of all board reviews | governance |
| `docs/External-Board-Reviews/041626-celso/` | V2.3 pre-migration review | governance |
| `docs/External-Board-Reviews/041826-renderer-alignment/` | Phase 7 plan A-G | governance |
| `docs/External-Board-Reviews/041826-renderer-impl-verify/` | Step A+B + STEP-E/STEP-F verification records + INDEX | governance |
| `docs/External-Board-Reviews/041826-fixture-enrichment/` | Step C 10-FA review | governance |
| `docs/External-Board-Reviews/041826-step-f-alignment-validation/` | Step F R3 fixes review | governance |
| `docs/External-Board-Reviews/041826-step-g-kickoff/` | U-1 doc integration | governance |
| `docs/board-review-pipeline-methodology.md` | Canonical 8/8/4 + 9-phase architecture record | release-ready (referenced everywhere) |

### 3.5 Historical / pre-current-layout (keep in repo, release-optional)

| Path | Purpose | Status |
|---|---|---|
| `docs/board-review-V21-consolidation.md` / `V22` / `V23` | Older board reviews, pre-`External-Board-Reviews/` layout | historical |
| `docs/board-review-axiom-triage-consolidation.md` + R2 | AXIOM findings triage (V2.3 era) | historical |
| `docs/board-review-operator-guide-consolidation.md` | V0.1 operator guide review | historical |
| `docs/board-review-package-v2-consolidation.md` | V2.4 package review | historical |
| `docs/repo-deep-dive-prompt-V2.md` / `V2.1.md` / `V2.2.md` | Prompt version archives | historical |
| `docs/CHANGELOG.md` | Prompt version changelog | release-ready (references archives) |
| `archive/` | Old TypeScript static analyzer (101 files, pre-pivot) | historical — release-optional as "previous iteration" evidence; can also be excluded |
| `docs/board-review-data/` | Older bundles + path-b-test-prompt.md (23 files) | dev-only (pre-`External-Board-Reviews/` staging area) |
| `docs/GitHub-Repo-Scan-Form.json` | Unclear purpose — pre-schema artifact | dev-only (investigate before release) |

### 3.6 Scratch / runtime (excluded)

| Path | Why excluded |
|---|---|
| `.board-review-temp/` | Session scratch for active board reviews. Should add to `.gitignore`. Currently untracked but visible. |
| `docs/__pycache__/` · `tests/__pycache__/` | Python bytecode cache. Should add to `.gitignore`. |
| `.claude/scheduled_tasks.lock` | Runtime lock. Should add to `.gitignore`. |
| `github-repo-scanner-v2.3.tar.gz` · `.zip` | Release artifacts. Should add to `.gitignore`. |
| `.archon/` | Archon integration data (7 files). Release-status depends on whether Archon is a shipping dependency — flag for review. |

**Recommended `.gitignore` additions:**
```
.board-review-temp/
**/__pycache__/
.claude/scheduled_tasks.lock
*.tar.gz
*.zip
```

---

## Maintenance

- **When to update this file:** on any commit that adds/removes a tracked file from the product-core list, or changes a directory's release status. Run `git log -1 --format='%ai' -- <path>` on each listed file to refresh timestamps.
- **When to audit the release plan:** before each release (V2.4, V2.5, etc.). Confirm every `release-ready` entry is current; every `excluded` is gitignored.
- **Cross-references:** `CLAUDE.md` Navigation block · `AUDIT_TRAIL.md` for checkpoint history · `docs/External-Board-Reviews/README.md` for board-review master index.
