# Board Review — Step C Fixture Enrichment Fix Artifacts

**Task:** Review the planned fixture enrichment for `tests/fixtures/zustand-form.json`. Each fix artifact (FA-1..FA-10) is an ADD to a specific JSON path — no deletes, no prose changes. Verify the structures match the V1.1 schema and together enable §02A, §05, §06, §07 rendering plus enrich §Verdict/§01/§03/§04/findings.

**Reviewers:** Codex (Systems Thinker) + DeepSeek (Skeptic). Pragmatist/Claude skipped — Claude drafted the artifacts.

**Round:** R1 only. APPROVE/FLAG/BLOCK per fix artifact + overall verdict.

**What you are reviewing:** shape correctness against the V1.1 schema, plus completeness vs the renderer contract. You are NOT reviewing the semantic accuracy of the test data (is PR #3466 really a README fix?) — that's test fixture fidelity, not board concern.

---

## 0. Context

- **Approved plan:** `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` — Step C = "Enrich zustand-form.json against V1.1 schema. Structural-LLM fields only. Prose stays sparse."
- **Implementation verification closure:** `docs/External-Board-Reviews/041826-renderer-impl-verify/CONSOLIDATION.md` — approved Step A + Step B with C2 resolution (file_sha/line_ranges/diff_anchor now required-always-nullable on `executable_file_inventory_entry`).
- **V1.1 schema:** `docs/scan-schema.json` (1412 lines). Defines every structure these artifacts target.
- **Golden reference for factual content:** `docs/GitHub-Scanner-zustand.md` (602 lines) — one known-good rendering.
- **Current fixture:** `tests/fixtures/zustand-form.json` (705 lines) — validates clean against V1.1 but drives only 10 of 13 sections.
- **Rule: prose stays sparse.** No multi-paragraph `body_paragraphs[]`. No new "what this means" prose. Existing sparse prose for F0/F1/F5 stays as-is; F2/F3/F4 prose stays absent.

---

## 1. Summary — what each FA adds

| FA | Path | Target section | Size | New top-level key? |
|---|---|---|---|---|
| **FA-1** | `phase_4_structured_llm.section_leads.section_01` | §01 intro blockquote | ~4 lines | yes |
| **FA-2** | `phase_4_structured_llm.verdict_exhibits.groups[]` | §Verdict exhibits | ~30 lines | yes |
| **FA-3** | `phase_4_structured_llm.executable_file_inventory` | §02A | ~70 lines | yes |
| **FA-4** | `phase_4_structured_llm.pr_sample_review` | §03 richer table | ~30 lines | yes |
| **FA-5** | `phase_4_structured_llm.timeline_intro` + enrich `timeline_events` notes | §04 intro | ~1 line (intro) + existing entries unchanged | no (field add) |
| **FA-6** | `phase_4_structured_llm.repo_vitals.rows[]` | §05 | ~55 lines | yes |
| **FA-7** | `phase_4_structured_llm.coverage_detail` (rows, monorepo, pr_target_usage) + `coverage_intro` + `coverage_gaps` | §06 | ~80 lines | yes |
| **FA-8** | `phase_4_structured_llm.evidence.entries[]` + `evidence_intro` | §07 | ~120 lines | yes |
| **FA-9** | Per-finding enrichment on `phase_4_structured_llm.findings.entries[*]`: `meta_table[]`, `how_to_fix`, `duration_label`, `date_label` | §02 finding cards | ~80 lines | no (field adds) |
| **FA-10** | `phase_3_computed.coverage_status.cells` — fix empty-array to populate from `compute_coverage_status()` | §06 (coverage status cells, different from coverage_detail) | ~25 lines | no (populate existing) |

**Total estimated additions:** ~490 lines of JSON. Prose content stays bounded by existing sparse prose.

---

## 2. Each fix artifact — structure + sample

### FA-1: section_leads.section_01

**Location:** `phase_4_structured_llm.section_leads.section_01`
**Current:** absent
**Addition:**

```json
"section_leads": {
  "section_01": {
    "pill_row": "✓ Safe to install today · ⚠ 1 consumer-side mitigation · 3 steps",
    "summary": "**Install is safe** — the library itself is clean (Step 1). If you ship to production, pair zustand with `minimumReleaseAge` in your own pnpm config to buy time against an upstream credential-compromise scenario (Step 2). Step 3 is a maintainer-side ask you can pass along."
  }
}
```

**Schema ref:** `#/$defs/section_lead` via `phase_4_structured_llm.section_leads.section_01`.

### FA-2: verdict_exhibits.groups

**Location:** `phase_4_structured_llm.verdict_exhibits`
**Current:** absent
**Addition:**

```json
"verdict_exhibits": {
  "groups": [
    {
      "symbol": "⚠",
      "headline": "Governance gaps — no branch protection, no CODEOWNERS, Dependabot alerts off",
      "one_line_summary": "C20 single-point-of-failure fires as Warning (release age 31 days, 1 day outside Critical window); alert surface disabled while version-update PRs still flow",
      "items": [
        {
          "tag": "Governance · F0 / C20",
          "claim": "No branch protection on `main` (API returns 404), zero rulesets, no CODEOWNERS in any of 4 standard locations. On a 57k-star library imported by millions, this is a supply-chain single-point-of-failure. Warning (not Critical) because the latest release v5.0.12 is 31 days old — 1 day outside the 30-day active-flow window."
        },
        {
          "tag": "Dependabot alerts · F1",
          "claim": "The Dependabot alerts API returns 403 with the explicit 'disabled for this repository' message — vulnerability alerts are turned off. Dependabot VERSION updates ARE still active; this is specifically the alert surface."
        }
      ]
    },
    {
      "symbol": "✓",
      "headline": "Strong positive signals — clean code-path, defensive supply chain, long-tenured maintainers",
      "one_line_summary": "Zero runtime deps, zero install hooks, OIDC npm publish, pnpm minimumReleaseAge, SHA-pinned actions, no pull_request_target, active Copilot-bot hygiene PRs, pmndrs collective",
      "items": [
        { "tag": "Code surface", "claim": "Zero runtime dependencies. Peer deps only. The inbound supply chain at install time is effectively 'zustand itself' — minimal attack surface for transitive CVEs." },
        { "tag": "Install hooks", "claim": "No preinstall/postinstall/prepare/prepublish/prepack/postpack scripts. `\"private\": true` guards against accidental `npm publish`." },
        { "tag": "Publish pipeline", "claim": "`publish.yml` uses OIDC `id-token: write` — no long-lived npm token stored. Published from `dist/` on `release: published` event only." },
        { "tag": "Defensive consumer config", "claim": "`pnpm-workspace.yaml` contains `minimumReleaseAge: 1440` — blocks installs of dep versions <24 hours old." },
        { "tag": "CI hygiene", "claim": "7 of 8 external actions SHA-pinned. Zero `pull_request_target`." },
        { "tag": "Active hygiene work", "claim": "Copilot bot PR #3395 pinned `actions/deploy-pages` to SHA; dai-shi merged. Pattern: bots propose hygiene, maintainers merge." },
        { "tag": "Code-path clean", "claim": "Zero eval/new Function/child_process/execSync/spawnSync/fetch/axios. Single `.exec()` in `src/middleware/devtools.ts:177` is a regex match, not a process-exec." },
        { "tag": "Maintainers", "claim": "dai-shi (15-year GitHub account, 8,088 followers, 411 commits), drcmda (pmndrs founder, 13-year account, 4,215 followers, 232 commits). No sockpuppet signals." }
      ]
    }
  ]
}
```

**Schema ref:** `#/$defs/verdict_exhibit_group` → `#/$defs/verdict_exhibit_item`.

### FA-3: executable_file_inventory

**Location:** `phase_4_structured_llm.executable_file_inventory`
**Current:** absent
**Addition (abbreviated — 13 layer2 entries, one sample shown):**

```json
"executable_file_inventory": {
  "lead": "✓ 0 install-time executables · ℹ 13 runtime files inventoried. Zustand ships zero install-time executables — it's a pure library with no CLIs, no binaries, no lifecycle scripts. No file in this inventory has an actionable dangerous-primitive hit.",
  "layer1_summary": "✓ **Zustand ships 0 install-time executables — pure library.** No CLIs, no binaries, no `pre/post/prepare` hooks. Runtime code is 16 TypeScript source files (7 top-level modules + 7 middleware + shallow helpers + types) compiled to `dist/` and published as the `zustand` npm package.",
  "layer2_entries": [
    {
      "path": "src/index.ts",
      "kind": "Barrel re-export",
      "runtime": "Bundler",
      "dangerous_calls": "None",
      "network": "None",
      "notes": "Entrypoint (`main` in `package.json`)",
      "file_sha": "32013285083648e8d58ba1f76d73b9bdc02fef50",
      "line_ranges": null,
      "diff_anchor": null
    },
    {
      "path": "src/middleware/devtools.ts",
      "kind": "Redux DevTools bridge",
      "runtime": "Bundler",
      "dangerous_calls": "1 `.exec()` — **regex match, not process exec**",
      "network": "None",
      "notes": "Posts messages to `window.__REDUX_DEVTOOLS_EXTENSION__`. The `.exec()` at line 177 is `RegExp.prototype.exec`",
      "file_sha": "32013285083648e8d58ba1f76d73b9bdc02fef50",
      "line_ranges": "177",
      "diff_anchor": "src/middleware/devtools.ts#L177"
    }
    // ... 11 more entries following same shape (vanilla.ts, react.ts, traditional.ts,
    // persist.ts, immer.ts, redux.ts, combine.ts, subscribeWithSelector.ts, ssrSafe.ts,
    // shallow.ts (3 files), types.d.ts). Benign entries get file_sha = HEAD_SHA,
    // line_ranges = null, diff_anchor = null. devtools.ts is the only security-note row.
  ],
  "closing_note": "**Note on the one `.exec()` hit.** The Step A dangerous-primitive grep surfaced exactly one `.exec()` call across `src/`: `src/middleware/devtools.ts:177`. This is not a process-exec. It's `RegExp.prototype.exec()` called on the caller-line string that DevTools uses to label the action in its timeline UI."
}
```

**Schema ref:** `#/$defs/executable_file_inventory` + `executable_file_inventory_entry` (file_sha/line_ranges/diff_anchor now required-always-nullable per 2026-04-18 implementation-verify resolution).

**Note on C2 enforcement:** every layer2 entry emits the three keys; null is used when the field genuinely doesn't apply (benign regex-only files use HEAD SHA but null line_ranges/diff_anchor).

### FA-4: pr_sample_review

**Location:** `phase_4_structured_llm.pr_sample_review`
**Current:** absent
**Addition (8 rows):**

```json
"pr_sample_review": {
  "intro": "**Recent PR activity is routine.** Sample of 7 most recent merges shows README fixes, Dependabot devDep bumps, docs-link updates, and a persist-hydration bugfix. One self-merge in the sample (dai-shi merged his own devDep bump) — common for a maintainer-owned library, low risk because the PR was a routine dep version bump.",
  "rows": [
    { "number": 3466, "what": "Update TypeScript guide links in README", "author": "FelixEckl (CONTRIBUTOR)", "merger": "dai-shi", "reviewed": "No formal decision", "concern": "Docs only. Different author/merger — practical pair-of-eyes.", "flagged": false },
    { "number": 3447, "what": "DevDep bump via dependabot", "author": "dependabot[bot]", "merger": "dbritto-dev", "reviewed": "No formal decision", "concern": "Routine bot bump. Different merger.", "flagged": false },
    { "number": 3443, "what": "Test coverage expansion", "author": "mahmoodhamdi", "merger": "dbritto-dev", "reviewed": "No formal decision", "concern": "Tests only.", "flagged": false },
    { "number": 3442, "what": "Test coverage expansion (follow-up)", "author": "mahmoodhamdi", "merger": "dbritto-dev", "reviewed": "No formal decision", "concern": "Tests only.", "flagged": false },
    { "number": 3427, "what": "DevDep bump (rollup/typescript)", "author": "dai-shi (MEMBER)", "merger": "dai-shi", "reviewed": "No formal decision", "concern": "**Self-merge** — routine devDep bump. Low risk.", "flagged": false },
    { "number": 3423, "what": "Devtools type correction", "author": "pavan-sh", "merger": "dai-shi", "reviewed": "Formal review", "concern": "Type-level fix.", "flagged": false },
    { "number": 3414, "what": "Persist-middleware hydration bugfix", "author": "grigoriy-reshetniak", "merger": "dai-shi", "reviewed": "Formal review", "concern": "Reviewed + merged by different people.", "flagged": false },
    { "number": 3395, "what": "**[Security-keyword hit]** Pin `actions/deploy-pages` to commit SHA", "author": "Copilot (bot)", "merger": "dai-shi", "reviewed": "No formal decision", "concern": "**Positive signal** — bot proposed pinning, maintainer merged.", "flagged": true }
  ]
}
```

**Schema ref:** `#/$defs/pr_sample_review` → `pr_sample_review_row`.

### FA-5: timeline_intro

**Location:** `phase_4_structured_llm.timeline_intro`
**Current:** absent
**Addition:** one string (existing `timeline_events.entries` array stays unchanged).

```json
"timeline_intro": "Six beats across the library's history. **The story is steady ship-and-fix** — 100+ releases over 7 years, monthly cadence in recent months, ongoing hygiene work, no security incidents, no yanked versions. One process note: the latest release shipped 31 days ago, which puts the C20 governance finding on the Warning side of the boundary but would flip it to Critical on the next scan unless governance is added first."
```

**Schema ref:** `phase_4_structured_llm.timeline_intro` (type `["string", "null"]`).

### FA-6: repo_vitals.rows

**Location:** `phase_4_structured_llm.repo_vitals.rows`
**Current:** absent
**Addition (18 rows — abbreviated):**

```json
"repo_vitals": {
  "rows": [
    { "metric": "Repo age", "value": "7 years", "note": "Created 2019-04-09 — mature library with established patterns" },
    { "metric": "Stars / Forks", "value": "57,754 / 2,033", "note": "Top-tier visibility. 178 watchers, 6 open issues." },
    { "metric": "Primary maintainer", "value": "✅ dai-shi (411 commits)", "note": "15-year GitHub account, 127 public repos, 8,088 followers — no sockpuppet signals" },
    // ... 15 more rows mirroring golden §05 lines 337-352
    { "metric": "OSSF Scorecard", "value": "5.9/10 (14 checks returned)", "note": "Independent security rating from the [Open Source Security Foundation](https://securityscorecards.dev/). Scores 24 practices 0-10; most repos 3-5, above 6 is strong." }
  ]
}
```

**Schema ref:** `#/$defs/repo_vitals_row`.

### FA-7: coverage_detail + coverage_intro + coverage_gaps

**Location:** `phase_4_structured_llm.coverage_detail`, `.coverage_intro`, `.coverage_gaps`
**Current:** absent
**Addition:**

```json
"coverage_intro": "**All 12 C11 coverage cells verified.** 8/8 workflow files read, full tarball extracted (143 files, 2.2M), 0 `pull_request_target`, 0 agent-rule files, 0 prompt-injection hits, 0 README paste-blocks, no Windows surface, not a true monorepo. One caveat: 7 of 8 external actions are SHA-pinned; the one remaining reference is a same-org reusable workflow rather than a third-party action.",
"coverage_detail": {
  "rows": [
    { "check": "Tarball extraction", "result": "✅ OK — 143 files, 2.2M — pinned to `32013285083648e8d58ba1f76d73b9bdc02fef50` at scan start" },
    { "check": "Workflow files read", "result": "✅ 8 of 8 — test, publish, preview-release, compressed-size, docs, test-multiple-builds, test-multiple-versions, test-old-typescript" },
    // ... 14 more rows from golden §06 lines 364-380
    { "check": "API rate budget", "result": "✅ 5000/5000 remaining. PR sample: full. — GitHub limits API calls to 5,000/hour. Full budget available." }
  ],
  "monorepo": {
    "is_monorepo": false,
    "inner_package_count": 0,
    "sampled_inner_packages": [],
    "lifecycle_script_hits": 0
  },
  "pr_target_usage": {
    "usage_count": 0,
    "workflows_checked": 8,
    "note": "Zero `pull_request_target` usage across 8 workflows — rules out that class of attack"
  }
},
"coverage_gaps": {
  "entries": [
    "Artifact reproducibility not verified — end-artifact was not independently rebuilt from source and sha-diffed against the published npm tarball.",
    "Dependabot ALERTS are disabled (confirmed via explicit 403 message) — but Dependabot VERSION UPDATES are active. So we know the alert surface is off, but we did not separately enumerate the current dep-graph for unpatched CVEs.",
    "Review-rate metric is based on a 7-PR sample, not the full 300-PR window."
  ]
}
```

**Schema ref:** `#/$defs/coverage_detail` (rows + monorepo + pr_target_usage). Plus `coverage_intro` + `coverage_gaps`.

### FA-8: evidence.entries + evidence_intro

**Location:** `phase_4_structured_llm.evidence`, `.evidence_intro`
**Current:** absent
**Addition (9 evidence entries — abbreviated):**

```json
"evidence_intro": "9 command-backed claims. **Skip ahead to items marked ★ START HERE** — the branch-protection-missing API check and the Dependabot-alerts-disabled diagnostic. Those two are the falsification criteria for the Warning verdict: if either reversed, the verdict would move to Clean.",
"evidence": {
  "entries": [
    {
      "id": "E1",
      "claim": "No branch protection, no rulesets, no CODEOWNERS on `main` (F0 / C20)",
      "command": "gh api \"repos/pmndrs/zustand/branches/main/protection\"\ngh api \"repos/pmndrs/zustand/rulesets\"\ngh api \"repos/pmndrs/zustand/rules/branches/main\"\nfor p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do\n  gh api \"repos/pmndrs/zustand/contents/$p\" 2>&1 | head -1\ndone",
      "command_lang": "bash",
      "result": "{\"message\":\"Not Found\",\"status\":\"404\"}\n[]\n[]\n{\"message\":\"Not Found\",\"status\":\"404\"}\n{\"message\":\"Not Found\",\"status\":\"404\"}\n{\"message\":\"Not Found\",\"status\":\"404\"}\n{\"message\":\"Not Found\",\"status\":\"404\"}",
      "result_lang": null,
      "result_truncated": false,
      "classification": "Confirmed fact — all four governance signals are negative. 404 on branch protection is authoritative; scan token has `repo` scope."
    }
    // ... E2 Dependabot alerts disabled (diagnostic 403 + version-updates-active contributor check)
    // ... E3 Review-rate sample on 7 recent merges
    // ... E4 Zero install-time hooks in package.json
    // ... E5 OIDC token used for npm publish
    // ... E6 Dangerous-primitive grep (positive control)
    // ... E7 Maintainer long-tenure (dai-shi + drcmda user APIs)
    // ... E8 minimumReleaseAge defensive config
    // ... E9 Zero pull_request_target usage
  ]
}
```

**Schema ref:** `#/$defs/evidence` (id, claim, command, command_lang, result, result_lang, result_truncated, classification). Note `priority_evidence.selections` already in fixture references E1 + E3 (via `evidence_id`); FA-8's evidence.entries provides the referents.

### FA-9: per-finding enrichment

**Location:** `phase_4_structured_llm.findings.entries[*]`
**Current:** each finding has id/severity/category/title/action_hint/etc but NO meta_table, how_to_fix, duration_label, date_label.
**Addition (applied to each finding F0-F5, abbreviated to F0 sample):**

```json
{
  "id": "F0",
  "severity": "Warning",
  // ... existing fields preserved ...
  "duration_label": "Continuous",
  "date_label": "Since repo creation",
  "how_to_fix": "GitHub *Settings → Branches → Add branch protection rule* ([direct link](https://github.com/pmndrs/zustand/settings/branch_protection_rules/new)). For `main`: require pull request reviews (1 approver minimum), require status checks (the existing `test.yml` matrix), require branches to be up to date before merging, do not allow bypassing. Also add `.github/CODEOWNERS` covering at minimum `.github/workflows/ @dai-shi @drcmda` and `src/ @dai-shi @drcmda`.",
  "meta_table": [
    { "label": "Classic branch protection", "value": "❌ 404 on `main`" },
    { "label": "Rulesets", "value": "❌ `[]` — zero rulesets" },
    { "label": "Rules on main", "value": "❌ `[]` — authoritative" },
    { "label": "CODEOWNERS", "value": "❌ Absent (4 locations checked)" },
    { "label": "Stars (blast radius)", "value": "57,754" },
    { "label": "Forks (blast radius)", "value": "2,033" },
    { "label": "Latest release age", "value": "⚠ 31 days (boundary; 1 day from Critical)" },
    { "label": "Executable surface", "value": "✅ Pure library (no install hooks)" }
  ]
}
```

**Schema ref:** `#/$defs/finding` — all four added fields are optional in schema; they render additional detail when present.

**Applied to:** F0 (8 meta rows + how_to_fix), F1 (5 meta rows + how_to_fix), F2 (6 meta rows, no how_to_fix — OK finding), F3 (4 meta rows), F4 (6 meta rows), F5 (4 meta rows + how_to_fix).

### FA-10: phase_3_computed.coverage_status.cells — populate

**Location:** `phase_3_computed.coverage_status.cells`
**Current:** `[]` (empty array — compute_coverage_status() was never run on this fixture).
**Addition:** run `compute_coverage_status(phase_1_raw_capture)` and populate. Fixture already has the raw capture; this is just executing the existing Python function and baking the result into the fixture.

```json
"coverage_status": {
  "cells": [
    { "name": "Tarball extraction", "status": "ok", "detail": "143 files" },
    { "name": "OSSF Scorecard", "status": "ok", "detail": "5.9/10" },
    { "name": "osv.dev", "status": "not_queried", "detail": "Zero runtime dependencies" },
    { "name": "Secrets-in-history (gitleaks)", "status": "not_available", "detail": "gitleaks not installed" },
    { "name": "API rate budget", "status": "ok", "detail": "5000/5000 remaining" },
    { "name": "Dependabot alerts", "status": "blocked", "detail": "Disabled for this repository" }
  ]
}
```

**Schema ref:** `#/$defs/coverage_cell`. Renderer uses `coverage_status.cells` as fallback when `coverage_detail.rows[]` is absent; with FA-7 landing, `coverage_detail.rows[]` takes precedence (the renderer already handles this — see `section_06.md.j2` lines dedup on `check`/`name`).

---

## 3. What I need you to check (V1-V6)

**V1 — Shape correctness.** For each FA-1 through FA-10, does the proposed JSON match the corresponding V1.1 schema `$def`? Focus on required fields, type coercion, enum conformance.

**V2 — Coverage completeness.** After all 10 FAs apply, does the fixture populate every renderer-consumed field listed in the plan's §1 table (brief.md from 041826-renderer-alignment, §1 table of missing fields)? Flag any gaps.

**V3 — Prose discipline.** Per the board resolution, prose stays sparse. Confirm no FA adds multi-paragraph `body_paragraphs[]`, new "what this means" / "what this does NOT mean" prose, or other prose-LLM fields on findings beyond what's already present for F0/F1/F5.

**V4 — C2 compliance on FA-3.** Every `layer2_entries[]` entry in FA-3 carries the 3 required fields (file_sha/line_ranges/diff_anchor), with null used only when genuinely unresolvable. Confirm the sample matches; flag if benign entries should have any of them populated vs null.

**V5 — References resolve.** FA-8 adds evidence entries E1-E9; existing `priority_evidence.selections` references E1, E3. Confirm all referenced IDs will exist after FA-8 applies.

**V6 — Unintended drift.** Any FA introducing new fields not in the V1.1 schema? Any FA deleting or modifying existing fixture content?

**Overall verdict per reviewer:** `APPROVE` (apply all FAs) / `REFINE` (list specific FAs needing adjustment) / `BLOCK` (specific structural errors — list them).

---

## 4. Output format

```
## Fix Artifact Review — <Role>

### V1 — Shape correctness: APPROVE / REFINE / BLOCK
[per-FA notes if any]

### V2 — Coverage completeness: APPROVE / REFINE / BLOCK
### V3 — Prose discipline: APPROVE / REFINE / BLOCK
### V4 — C2 compliance on FA-3: APPROVE / REFINE / BLOCK
### V5 — References resolve: APPROVE / REFINE / BLOCK
### V6 — Unintended drift: APPROVE / REFINE / BLOCK

### Per-FA verdict summary
FA-1: APPROVE / REFINE / BLOCK — [1 sentence]
FA-2: ...
FA-3: ...
...

VERDICT: APPROVE all FAs / REFINE (list FAs needing fixes) / BLOCK (list structural blockers)
```

**Save output:**
- Codex: `/tmp/codex-fa-review.md`
- DeepSeek: `.board-review-temp/fixture-enrichment/deepseek-fa-review.md`

---

## 5. Files to read

All in `/root/tinkering/stop-git-std/`:
- `docs/scan-schema.json` — V1.1 schema (verify FA shapes against it)
- `tests/fixtures/zustand-form.json` — current fixture (ADDs go here)
- `docs/GitHub-Scanner-zustand.md` — golden MD (factual content source)
- `docs/templates/partials/*.md.j2` — what the renderer consumes (confirms what fields are actually read)
- `docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md` — original plan
- `docs/External-Board-Reviews/041826-renderer-impl-verify/CONSOLIDATION.md` — C2 resolution context
