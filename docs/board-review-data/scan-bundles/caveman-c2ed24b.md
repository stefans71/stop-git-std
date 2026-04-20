# JuliusBrussee/caveman Scan — Evidence Bundle

## Scan metadata

- Repo: `JuliusBrussee/caveman`
- HEAD SHA: `c2ed24b` (tag `v1.6.0`)
- Default branch: `main`
- Fetch path: tarball via `gh api`
- Extraction: 103 files (hooks/, rules/, .github/workflows/, caveman-compress/, benchmarks/)
- Scan date: 2026-04-16
- Scanner prompt version: V2.4 (comparator MD: `docs/GitHub-Scanner-caveman.md`, rendered by V2.4 authoring round + V2.3 initial with R3-C20 amendment)
- Repo age at scan: 12 days (repo created 2026-04-04)
- Stars: 32,844
- License: MIT

### Owner / maintainer

- `JuliusBrussee` — User account (not Org), created 2022-04-21 (~4 years tenure at scan), 42 public repos, 618 followers. Not a sockpuppet. Supported by Evidence 8.

### Distribution shape

- Claude Code plugin (marketplace manifest with `"source": "./"` — live `main`, no pinning)
- curl-pipe install script: `bash <(curl -s raw.githubusercontent.com/.../install.sh)`
- Windows PS1 mirror: `install.ps1`
- CI-synced agent rule targets: `.clinerules/caveman.md`, `.cursor/rules/caveman.mdc`, `.windsurf/rules/caveman.md`, `.github/copilot-instructions.md`
- None of the 6 distribution channels use pinned hashes or artifact verification.

## Evidence

Facts only — no interpretive verbs. Each claim is backed by a command + captured result.

### Evidence 1 (STAR) — v1.6.0 fixes a real symlink vulnerability present in v1.0.0–v1.5.1

Command: `gh pr view 70 -R JuliusBrussee/caveman --json commits -q '.commits[0].messageBody'`

Result:

> The SessionStart hook writes to `~/.claude/.caveman-active` using `fs.writeFileSync` on a predictable path. If that path is replaced with a symlink, Node will follow it and overwrite the symlink target. A local attacker (or another process running as the same user) could abuse this to modify unintended files writable by the user.
>
> Affected files: `caveman-activate.js`, `caveman-mode-tracker.js`
>
> Signed-off-by: tuanaiseo 221258316+tuanaiseo@users.noreply.github.com

Fact: vulnerability described in the reporter's own commit message; fix in v1.6.0 adds O_NOFOLLOW + symlink refusal; before/after diff confirms the unprotected write in v1.5.1 and earlier. **Backs F5.**

### Evidence 2 (STAR) — Zero GitHub Security Advisories published

Command: `gh api "repos/JuliusBrussee/caveman/security-advisories"`

Result: `[]`

Fact: empty array response means zero advisories published over repo lifetime. **Backs F5 (disclosure gap component) + the F-advisory adjunct.**

### Evidence 3 — v1.6.0 was a 10+ PR batch merge committed at a single timestamp

Command: `gh pr list -R JuliusBrussee/caveman --state merged --limit 300 --json number,title,mergedAt | jq '[.[] | select(.mergedAt == "2026-04-15T12:50:16Z")] | length'`

Result: `16`

Fact: 16 PRs share mergedAt `2026-04-15T12:50:16Z` — a synchronized batch merge by github-actions post-processing. The two security fix PRs (#70, #71) are among those 16. **Backs the batch-merge component of F5.**

### Evidence 4 — 85% of merged PRs have no formal review

Command: `gh pr list -R JuliusBrussee/caveman --state merged --limit 300 --json reviewDecision | jq '[.[] | select(.reviewDecision != null and .reviewDecision != "")] | length'`

Result: `5`

Fact: 5 of 33 merged PRs have `reviewDecision` set = 15% formal review rate. Security PRs #70 and #71 had zero review activity (both merged without any formal review decision). **Backs F11.**

### Evidence 5 (STAR) — No branch protection on main

Command: `gh api "repos/JuliusBrussee/caveman/branches/main/protection"`

Result: `{"message":"Not Found","documentation_url":"https://docs.github.com/rest/branches/branch-protection#get-branch-protection","status":"404"}`

Fact: 404 is authoritative here — the authenticated token has admin-read access; a permissions issue would return 403. 404 = no rule exists. **Backs F0 + F14.**

### Evidence 5b — Zero rulesets, zero rules on default branch, no CODEOWNERS

Command:

```
gh api "repos/JuliusBrussee/caveman/rulesets"
gh api "repos/JuliusBrussee/caveman/rules/branches/main"
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do
  gh api "repos/JuliusBrussee/caveman/contents/$p" 2>&1 | head -1
done
```

Result:

```
[]
[]
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
{"message":"Not Found","status":"404"}
```

Fact: no repo-level rulesets, no rules on `main`, CODEOWNERS absent in all four standard locations. Owner is a User account so no org-level rulesets apply. **Backs F0 (C20 all four governance signals negative).**

### Evidence 6 — Dependabot is disabled

Command: `gh api "repos/JuliusBrussee/caveman/dependabot/alerts"`

Result: `{"message":"Dependabot alerts are disabled for this repository.","documentation_url":"https://docs.github.com/rest/dependabot/alerts#list-dependabot-alerts-for-a-repository","status":"403"}`

Fact: 403 response distinguishes "disabled" from a permissions error. Dependabot is explicitly off. **Backs the no-upstream-signal component of F14.**

### Evidence 7 — Runtime dependency surface is minimal

Command:

```
find /tmp/repo-scan-JuliusBrussee-caveman -type f \( -name 'package.json' -o -name 'requirements*.txt' -o -name 'pyproject.toml' \)
cat /tmp/repo-scan-JuliusBrussee-caveman/hooks/package.json
cat /tmp/repo-scan-JuliusBrussee-caveman/benchmarks/requirements.txt
```

Result:

```
/tmp/repo-scan-JuliusBrussee-caveman/hooks/package.json
/tmp/repo-scan-JuliusBrussee-caveman/benchmarks/requirements.txt

{ "type": "commonjs" }

anthropic>=0.40.0
```

Fact: `hooks/package.json` declares no dependencies; the only Python dep (`anthropic`) is benchmark-only. Runtime attack surface from transitive deps is essentially zero.

### Evidence 8 — Maintainer is an established 4-year-old account

Command: `gh api "users/JuliusBrussee" -q '{login,created_at,public_repos,followers}'`

Result: `{"login":"JuliusBrussee","created_at":"2022-04-21T20:06:45Z","followers":618,"public_repos":42}`

Fact: account created 2022-04-21 (4 years old at scan), 42 public repos, 618 followers. Not a sockpuppet. Normal for a maintainer of a viral plugin.

### Evidence 9 — v1.6.0 hooks implement defense-in-depth against symlink attacks

Command: `grep -nE 'O_NOFOLLOW|lstatSync|isSymbolicLink|renameSync|fchmodSync' /tmp/repo-scan-JuliusBrussee-caveman/hooks/caveman-config.js`

Result:

```
80:      if (fs.lstatSync(flagDir).isSymbolicLink()) return;
87:      if (fs.lstatSync(flagPath).isSymbolicLink()) return;
93:    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
94:    const flags = fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | O_NOFOLLOW;
99:      try { fs.fchmodSync(fd, 0o600); } catch (e) { /* best-effort on Windows */ }
103:    fs.renameSync(tempPath, flagPath);
126:    st = fs.lstatSync(flagPath);
130:    if (st.isSymbolicLink() || !st.isFile()) return null;
131:    if (st.size > MAX_FLAG_BYTES) return null;
133:    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
134:    const flags = fs.constants.O_RDONLY | O_NOFOLLOW;
```

Fact: v1.6.0 code uses every defense expected for this class of vulnerability: atomic temp+rename, O_NOFOLLOW flag, mode 0o600, symlink refusal at parent directory and target, 64-byte size cap on reads, whitelist validation of read content. **Backs F16.**

### Evidence 10 — No SECURITY.md at repo root

Command: `find /tmp/repo-scan-JuliusBrussee-caveman -maxdepth 2 -iname 'SECURITY.md'`

Result: `/tmp/repo-scan-JuliusBrussee-caveman/caveman-compress/SECURITY.md`

Fact: the only SECURITY.md is nested inside `caveman-compress/` and covers a different concern (Snyk static-analysis rating), not a disclosure policy. No SECURITY.md exists at the repo root. **Backs F5 (disclosure gap) + the F-advisory adjunct.**

### Evidence 11 — PR review-lag on the security fix

Context derived from §03 and §04 timeline in the V2.4 comparator:

- Reporter (tuanaiseo) filed PR #70 on 2026-04-10 with a complete description of the symlink attack in the commit message.
- PR #70 and companion PR #71 sat open until 2026-04-15 (5 days).
- 4 vulnerable releases (v1.4.0, v1.4.1, v1.5.0, v1.5.1) shipped during those 5 days while the fix was pending.
- Both PRs merged 2026-04-15 12:50:16Z as part of the v1.6.0 batch with zero formal review.

Fact: closed-security-PR lag = 5 days. `closed_fix_lag_days = 5` for scorecard-calibration Q2 compute patch. **Backs F5 and F11 jointly.**

## Pattern recognition

*(Inference layer — each bullet tagged with an interpretive verb.)*

- The combination of no published advisories and the 16-PR batch merge **suggests** the maintainer treats security fixes as part of the regular release cadence rather than as separately-signaled events — users who skim release notes for security-relevant changes do not find a clear signal.
- The 15% formal review rate combined with zero reviews on the two security PRs (#70 and #71) is **consistent with** a governance gap that applies uniformly rather than being specific to security work; a credential-compromise PR would not stand out against this baseline.
- The simultaneous "v1.6.0 code is thorough" (F16) and "no advisory was issued" (F5 disclosure component) **plausibly indicates** the concern is process, not capability — the maintainer is technically competent but does not operate a formal disclosure pipeline.

## FINDINGS SUMMARY

The canonical V2.4 finding cards are five H3 entries in the comparator MD. Narrative bullets inside grouped warning summaries do not count as canonical cards.

- F0 · Critical · Ongoing — Governance single-point-of-failure: no branch protection, no rulesets, no CODEOWNERS on a 32k-star repo that ships hooks into every Claude Code session. C20 escalates Warning → Critical because the repo ships executable code AND has active code flow (10 releases in last 30 days). Driven by Evidence 5, 5b.
- F5 · Warning · Code fixed in v1.6.0 · Disclosure gap open — Unadvertised symlink vulnerability; named in release notes, not in GitHub's advisory channel. v1.0.0 through v1.5.1 shipped the vulnerability for 11 days. Driven by Evidence 1, 2, 10, 11.
- F11 · Warning · Ongoing — Review rate 15% formal (5/33), 36% any-review (12/33). Security PRs #70 and #71 had zero review activity. Driven by Evidence 4.
- F14 · Info · Current — No branch protection rule on main; stand-alone branch-protection-API-404 fact. F0 is the C20 Critical combining all governance signals; F14 is the narrower single-fact item. Driven by Evidence 5.
- F16 · OK — v1.6.0 security code is thorough and well-reasoned: O_NOFOLLOW, atomic temp+rename, whitelist-validated reads, size caps, symlink refusal at both parent and target. Driven by Evidence 9.

## Verdict

Caveman verdict: **Critical (split)** on Version axis — driven by F0 (Critical, governance single-point-of-failure).

- Split axis: **Version**. Current release (v1.6.0) is clean code but sits behind an ungated pipeline (F0 applies). Historical releases (v1.0.0 – v1.5.1) shipped a live exploitable symlink vulnerability (F5) for 11 days. Both audiences share the same F0 governance exposure going forward.
- F11 (Warning) and F14 (Info) are continuous governance gaps — not audience-specific.
- F16 (OK) is a positive signal about the v1.6.0 fix quality.

## Scorecard

V2.4 comparator scorecard, which the scorecard-calibration patched `compute.py` now reproduces cell-by-cell:

- **Q1 Does anyone check the code?** — RED. 15% formal review (5/33), no branch protection on `main`, no CODEOWNERS. `compute.py` Q1 governance-floor override fires (scorecard-calibration patch): `formal<10% AND not branch_protection AND not codeowners` forces red regardless of any-review threshold.
- **Q2 Do they fix problems quickly?** — AMBER. Security PR #70 filed 2026-04-10, merged 2026-04-15 (5-day lag). No open security issues at scan time. `compute.py` Q2 `closed_fix_lag_days > 3` patch (scorecard-calibration) drops green to amber.
- **Q3 Do they tell you about problems?** — RED. No `SECURITY.md` at root, no contributing guide (scorecard-calibration Q3 amber-floor input is False), zero GitHub Security Advisories ever published, Dependabot disabled.
- **Q4 Is it safe out of the box?** — RED. F0 Critical finding on default install path (`has_critical_on_default_path = True`). Every distribution channel fetches from live `main` or unpinned artifacts.
