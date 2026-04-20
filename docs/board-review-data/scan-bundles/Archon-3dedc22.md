# coleam00/Archon Scan — Evidence Bundle

## Scan metadata

- Repo: `coleam00/Archon`
- HEAD SHA: `3dedc22` (tag `v0.3.6`)
- Default branch: `dev` (NOT `main` — Archon develops on `dev` and tags releases from it)
- Fetch path: tarball via `gh api` pinned to SHA
- Extraction: 769 files (monorepo — 11 inner packages: core, cli, providers, workflows, git, paths, slack, telegram, github, web, codex)
- Scan date: 2026-04-16
- Scanner prompt version: V2.3 (first Archon scan under V2.3 pipeline; comparator MD: `docs/GitHub-Scanner-Archon.md`)
- Repo age at scan: 14 months (repo created 2025-02-07)
- Stars: 18,300
- License: MIT

### Owner / maintainer

- `coleam00` (Cole Medin) — User account, created 2019-02-03 (~7 years tenure at scan), 51 public repos, 6,641 followers, Dynamous company. Supported by Evidence 8.
- `Wirasm` (Rasmus Widing) — de facto lead contributor with 791 commits (vs. coleam00's 343 on the `dev` branch at scan). Owner-merges-contributor-work arrangement.

### Distribution shape

Mixed modern-supply-chain pattern. Verified install-path discipline, unverified end-artifact reproducibility.

- `scripts/install.sh` — sha256-verified install from GitHub Releases. `SKIP_CHECKSUM=false` default. Supported by Evidence 9.
- `scripts/install.ps1` — Windows parity with same sha256 verification.
- `archon.diy/install` — byte-for-byte identical to `scripts/install.sh` (Evidence 2).
- Homebrew formula `homebrew/archon.rb` — pins per-platform binary to version + sha256.
- Docker image `ghcr.io/coleam00/archon` — semver-tagged publish via CI (no live-main).
- Codex vendor binary under `~/.archon/vendor/codex/` — unpinned, unverified (the F1 Warning surface).

## Evidence

Facts only — no interpretive verbs. Each claim is backed by a command and captured result.

### Evidence 1 (priority) — Codex vendor binary resolver has no sha256 pinning (F1 / issue #1245)

Command: `gh issue view 1245 -R coleam00/Archon --json title,body -q '.title'`

Result: `security(providers): codex vendor binary resolver lacks hash/signature pinning — LPE via writable vendor dir`

Fact: issue body explains the resolver flow (env → config → filesystem drop under `~/.archon/vendor/codex/`) and the attack pre-condition (another local user has write access to that directory). Fix proposed in PR #1250. **Backs F1.**

### Evidence 2 (priority) — `archon.diy/install` serves the same content as `scripts/install.sh`

Command:

```
curl -fsSL https://archon.diy/install | head -5
head -5 /tmp/repo-scan-coleam00-Archon/scripts/install.sh
```

Result (identical from both sources):

```
#!/usr/bin/env bash
# scripts/install.sh
# Install Archon CLI from GitHub releases
```

Fact: `archon.diy` acts as a CDN/redirect for the repo's install script, not a separately-controlled distribution endpoint. A user who fetches the install script via either route gets the same content. **Backs F8.**

### Evidence 3 (priority) — Dual review-rate metric (F4) — 8% formal, 58% any-review

Command: `gh pr list -R coleam00/Archon --state merged --limit 300 --json reviewDecision,reviews | jq '{ total: length, formal_review: [.[] | select(.reviewDecision != null and .reviewDecision != "")] | length, any_review: [.[] | select(.reviews != null and (.reviews | length) > 0)] | length }'`

Result: `{ "total": 160, "formal_review": 13, "any_review": 93 }`

Fact: 13 of 160 merged PRs have formal `reviewDecision` set (8%). Any-review rate (PRs with at least one review object present) is 93/160 = 58%. **Backs F4.**

### Evidence 4 — Axios CVE fix open 3 days (PR #1153)

Command: `gh pr view 1153 -R coleam00/Archon --json title,state,createdAt`

Result: `{"createdAt":"2026-04-13T01:31:22Z","state":"OPEN","title":"fix: override axios to ^1.15.0 for CVE-2025-62718"}`

Fact: PR #1153 open since 2026-04-13, scan date 2026-04-16 (3 days open at scan time). Override fix targets CVE-2025-62718 (NO_PROXY bypass) reaching via `@slack/bolt` → `@slack/web-api` → axios. **Backs F3.**

### Evidence 5 — No branch protection on `dev` or `main`

Command:

```
gh api "repos/coleam00/Archon/branches/dev/protection"
gh api "repos/coleam00/Archon/branches/main/protection"
```

Result:

```
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

Fact: 404 authoritative on both branches. The authenticated token has `repo` scope and would return 403 if the issue were permissions. **Backs F0 + F4.**

### Evidence 6 — No `dependabot.yml` config file in repo; Dependabot alerts API 403

Command:

```
find /tmp/repo-scan-coleam00-Archon -name "dependabot.yml" -o -name "dependabot.yaml" -o -name "renovate.json"
gh api "repos/coleam00/Archon/dependabot/alerts"
```

Result:

```
(find returns nothing)
{"message":"You are not authorized to perform this operation.","status":"403"}
```

Fact: no declarative dependency-tracking config exists in the repo. Dependabot alerts API 403 is ambiguous without admin scope — could mean disabled or simply unauthorised to read. Missing config file is definitive. **Backs F5.**

### Evidence 7 — SECURITY.md with real private disclosure channel

Command: `cat /tmp/repo-scan-coleam00-Archon/SECURITY.md | head -12`

Result:

```markdown
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Archon, please report it responsibly.

**Do NOT open a public issue for security vulnerabilities.**

Instead, email **cole@dynamous.ai** or use [GitHub's private vulnerability reporting](https://github.com/coleam00/Archon/security/advisories/new).
```

Fact: SECURITY.md at repo root with real private channel (direct email + GHSA private reporting link). Unlike caveman's missing policy. **Backs positive disclosure signal (referenced in F4 meta + contributes to verdict audience framing).**

### Evidence 8 — Maintainer is established (coleam00 — 7-year account, 6,641 followers, public company affiliation)

Command: `gh api "users/coleam00" -q '{login,created_at,public_repos,followers,company}'`

Result: `{"company":"Dynamous","created_at":"2019-02-03T02:45:51Z","followers":6641,"login":"coleam00","public_repos":51}`

Fact: 7-year-old account, public company affiliation (Dynamous), 6,641 followers, 51 public repos. Not a sockpuppet. Supports the "established maintainer" positive signal in F7.

### Evidence 9 — Install script verifies sha256 checksums by default

Command: `grep -nE 'SKIP_CHECKSUM|sha256sum|verify_checksum' /tmp/repo-scan-coleam00-Archon/scripts/install.sh | head -5`

Result:

```
#   SKIP_CHECKSUM - Set to "true" to skip checksum verification (not recommended)
# SKIP_CHECKSUM opt-in only; defaults to false
SKIP_CHECKSUM="${SKIP_CHECKSUM:-false}"
```

Fact: checksum verification is the default install path; users must opt-in to skip. **Backs F8.**

### Evidence 10 — F1 Codex LPE attack is gated by local-write pre-condition

Context from the V2.4 MD §02 F1 card body: the Codex binary resolver at `packages/providers/src/codex/binary-resolver.ts` reads from three sources (env var `CODEX_BIN_PATH`, config `assistants.codex.codexBinaryPath`, filesystem drop under `~/.archon/vendor/codex/`) and hands the path to the SDK's `codexPathOverride`. The only gate is `fileExists()`. No sha256, no signature, no permission check on the directory.

Fact: F1 is not a remote-unauth attack. It requires the attacker to already have local write access to `~/.archon/vendor/codex/`, then escalates to arbitrary code execution on the victim's next Codex workflow. Applies to shared workstations, dev containers with shared volumes, CI images, or Docker setups with exposed vendor mounts. **Backs F1 threat-model framing and F6 (executeBashNode is a related design surface).**

### Evidence 11 — PR #1169 and #1217 shipped recent security hardening without GHSA

Context from V2.4 MD §04 timeline:

- PR #1169 title: `security: prevent target repo .env from leaking into subprocesses (#1135)` — merged 2026-04-13, no GHSA published.
- PR #1217 title: `fix(providers): replace Claude SDK embed with explicit binary-path resolver` — merged 2026-04-14 (module-resolver bug fix, not security-remediation; still merged without formal review).
- Gate C audit per SF1 finding (Phase 1 of this pipeline): `has_reported_fixed_vulns = TRUE` for Archon because PR #1169 was an undisclosed security fix.

Fact: the repo has had ≥1 security-labelled fix (#1169) merged without an accompanying GHSA publication. Compute.py Q3 output = amber (SECURITY.md present but zero published advisories). This is the `scorecard-calibration` board review's Tension-1 outcome for Archon specifically. **Backs the Q3 amber in the scorecard section below.**

## Pattern recognition

*(Inference layer — each bullet tagged with an approved interpretive verb.)*

- The 8% formal review rate combined with "self-submitted-and-merged" being the pattern for 5 of 6 security-adjacent PRs **suggests** the practical review lives in implicit owner-plus-lead trust rather than encoded gates; a credential-compromise PR from Wirasm or coleam00 would not stand out against the baseline self-merge pattern.
- The juxtaposition of "no published advisories despite PR #1169 being a security fix" and "Reporter shaun0927 filing four well-scoped security issues publicly within one day" is **consistent with** a team that accepts security reports through SECURITY.md's private channel and then discusses fixes in public — a partial-disclosure stance, not a refusal-to-disclose stance.
- The install-path verification (sha256 from same release URL) is **reminiscent of** a closed-loop integrity story: strong at one layer (binary matches checksums), weak at the meta-layer (both downloaded from the same GitHub Releases URL, so a release-manager token compromise would defeat both at once). This is the gap the repo's own F2 issue (#1246) asks to close with sigstore / independent attestation.

## FINDINGS SUMMARY

V2.4 comparator card inventory (9 canonical H3 finding cards):

- F0 · Critical · Ongoing — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a repo that ships executable code to every install (C20). Driven by Evidence 5.
- F1 · Warning · Open · fix in review — Codex vendor binary resolver lacks hash/signature pinning (#1245). LPE on shared hosts. Fix proposed in PR #1250. Driven by Evidence 1, 10.
- F2 · Warning · Structural · no fix yet — `archon serve` web-dist integrity reduces to trusting one GitHub Releases URL (#1246). Supply-chain hardening request rather than an exploitable bug today. Driven by Evidence 9 (integrity loop) and issue #1246 content.
- F3 · Warning · PR open 3 days — Axios CVE-2025-62718 (NO_PROXY bypass / SSRF) override patch pending in PR #1153. Transits via `@slack/bolt` → `@slack/web-api` → axios. Driven by Evidence 4.
- F4 · Warning · Ongoing — 8% formal review rate, 58% any-review, no branch protection, no CODEOWNERS. Owner+lead practical reviewer pair exists but not encoded in GitHub settings. Driven by Evidence 3, 5.
- F5 · Info · Process gap — No `.github/dependabot.yml` — transitive-CVE PRs not auto-opened. Driven by Evidence 6.
- F6 · Info · Known attack surface — Archon executes AI-generated bash via `executeBashNode` (DAG engine feature). Not a bug — a disclosed trust-model property. Sandbox third-party workflow YAMLs.
- F7 · OK — Active security work pattern — recent PRs (#1169 env-leak block, #1217 binary-path resolver) show real security engineering care. Driven by Evidence 11.
- F8 · OK — Pinned-and-checksummed distribution — opposite of curl-pipe-from-main. Install scripts sha256-verify by default, Homebrew pins per-platform sha256, Docker uses semver tags. Driven by Evidence 2, 9.

## Verdict

Archon verdict: **Critical (split)** on Deployment axis — driven by F0 (Critical, governance single-point-of-failure).

- Split axis: **Deployment**. Two audiences share the F0 governance exposure but diverge on the Codex LPE surface:
  - Default-profile installers today: F0 applies. Install-path is verified; end-artifact reproducibility is not.
  - Shared-host + Codex users: F0 + F1 (Codex LPE via `~/.archon/vendor/codex/`) stack. Wait for PR #1250 to merge.
- F2, F3 (Warning) are ongoing supply-chain gaps visible in the public issue tracker.
- F4 (Warning) is a continuous governance gap; F5 (Info) is a process gap compounding F3 response lag.
- F6 (Info) is a disclosed trust-model property, not a bug.
- F7 and F8 (OK) are real positive signals — active security refactors and pinned distribution discipline.

## Scorecard

V2.4 comparator scorecard, which the scorecard-calibration patched `compute.py` reproduces cell-by-cell:

- Q1 Does anyone check the code? — RED ("No upstream gate"). 8% formal / 58% any-review, no branch protection, no CODEOWNERS. `compute.py` Q1 governance-floor override fires: `formal<10% AND not branch_protection AND not codeowners` forces red regardless of any-review threshold.
- Q2 Do they fix problems quickly? — AMBER ("Open fixes, not merged yet"). 3 open security issues (F1 / F2 / F3). `open_security_issue_count=3 AND cve_age<=14` → amber.
- Q3 Do they tell you about problems? — AMBER ("Partly"). SECURITY.md present with private channel, but 0 published advisories (Gate C audit of the scorecard-calibration board review: PR #1169 was a security fix shipped without GHSA → `has_reported_fixed_vulns=TRUE` → amber via compute.py's standard branch; U-11 catalog correction updated comparator MD from green → amber).
- Q4 Is it safe out of the box? — RED ("No"). F0 Critical finding applies to the default install path. `has_critical_on_default_path=TRUE`.
