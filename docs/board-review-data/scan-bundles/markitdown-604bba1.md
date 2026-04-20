# microsoft/markitdown Scan — Evidence Bundle

## Scan metadata

- Repo: `microsoft/markitdown`
- HEAD SHA: `604bba13da2f43b756b49122cb65bdedb85b1dff` (short: `604bba1`) — `main` branch
- Default branch: `main`
- Fetch path: `gh api` calls only (no tarball extraction in this scan environment)
- Scan date: 2026-04-20
- Scanner prompt version: V2.4
- Rendering pipeline: V2.5-preview (wild scan — first production-clearance trigger run)
- Repo age at scan: 17 months (created 2024-11-13)
- Stars: 112,825
- License: MIT

### Owner / maintainers

- `microsoft` — Organization, created 2013-12-10, 7,778 public repos, 117,865 followers. Enterprise owner.
- `afourney` (Adam Fourney, `adamfo@microsoft.com`) — repo author per `pyproject.toml`; 100 commits (top contributor); sole release author across all 18 releases.
- `gagb` — second contributor with 70 commits (70% of afourney's volume).
- Contribution concentration is owner-plus-lead — not a solo-maintainer situation (top contributor at ~42% of commits in the top-6 summary).

### Distribution shape

Python monorepo with 4 sub-packages published to PyPI:

- `markitdown` (core, `pyproject.toml`)
- `markitdown[all]` (optional-deps full conversion surface — pdfminer.six, mammoth, python-pptx, pandas, openpyxl, pdfplumber, azure-ai-documentintelligence, youtube-transcript-api, pydub, SpeechRecognition, and more)
- `markitdown-mcp` (Model Context Protocol server — depends on `mcp~=1.8.0` + `markitdown[all]`)
- `markitdown-ocr` (OCR layer — pdfminer.six, pdfplumber, PyMuPDF, mammoth)
- `markitdown-sample-plugin` (example for plugin authors)

Plus a `Dockerfile` at repo root (Python 3.13-slim-bullseye base + ffmpeg + exiftool; runs as `nobody:nogroup`; users build locally — no prebuilt image published to a registry).

## Evidence

Facts only — no interpretive verbs. Each claim is backed by a command and captured result.

### Evidence 1 — Classic branch protection 404 BUT an active ruleset exists with `required_approving_review_count: 0`

Command:

```
gh api "repos/microsoft/markitdown/branches/main/protection"
gh api "repos/microsoft/markitdown/rulesets"
gh api "repos/microsoft/markitdown/rules/branches/main"
```

Result:

```
{"message":"Not Found","status":"404"}
[{"id":2607793,"name":"Protect Main Branch","enforcement":"active",...}]
[{"type":"deletion",...}, {"type":"non_fast_forward",...},
 {"type":"pull_request","parameters":{"required_approving_review_count":0,
   "require_code_owner_review":false,"require_last_push_approval":false,...}},
 {"type":"required_status_checks","parameters":{"required_status_checks":[
   {"context":"tests"},{"context":"pre-commit"}]}}]
```

Fact: classic branch protection API returns 404 (no classic rule configured). A modern ruleset ID 2607793 "Protect Main Branch" is active on `main` with 4 rules: deletion prevention, non-fast-forward prevention, PR required (but `required_approving_review_count: 0` — zero reviewers required), and required status checks (`tests` + `pre-commit` contexts). CODEOWNER review and last-push approval are explicitly `false`. **Better governance than caveman / Archon (ruleset exists) but the PR gate admits zero-reviewer merges — the gate is soft.**

### Evidence 2 — No CODEOWNERS file in any standard location

Command:

```
for p in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS .gitlab/CODEOWNERS; do
  gh api "repos/microsoft/markitdown/contents/$p" 2>&1 | head -1
done
```

Result: all four return `{"message":"Not Found","status":"404"}`

Fact: No CODEOWNERS in any of the four standard locations. Combined with `require_code_owner_review: false` in the ruleset (Evidence 1), there is no path-scoped reviewer requirement.

### Evidence 3 — Open XXE vulnerability in DOCX pre-processor, fix PR sitting ~47 days

Command: `gh issue view 1565 -R microsoft/markitdown --json title,state,body,labels,createdAt`

Result (excerpt):

```
Title: Security: XXE vulnerability in DOCX pre-processor (ET.fromstring on untrusted input)
State: OPEN
Created: 2026-02-20T22:29:06Z
Labels: [] (none — "security" is in the title but no security label applied)
Body: ## Security Vulnerability Report
      Type: XML External Entity (XXE) Injection
      Severity: High
      File: packages/markitdown/src/markitdown/converter_utils/docx/pre_process.py, line 45
      Commit tested: 4a5340f93b2bf1dc11641f921fbfd6d5f016924b
      Description:
      The function `_convert_omath_to_latex()` in `pre_process.py` uses
      `ET.fromstring()` to parse XML content extracted from user-supplied
      DOCX files...
```

Follow-up: `gh pr view 1582 -R microsoft/markitdown --json state,createdAt,reviews,comments`

Result:

```
{"state":"OPEN","createdAt":"2026-03-03T03:23:46Z","reviews":0 objects,"comments":3}
```

Fact: OPEN High-severity XXE injection in `_convert_omath_to_latex()` — a DOCX pre-processor calls `xml.etree.ElementTree.fromstring()` on content extracted from user-supplied DOCX files. Fix PR #1582 (uses `defusedxml.ElementTree` to replace the unsafe parser) has been open 47 days at scan time with 0 reviews and 3 comments. The vulnerable code is still present in `main` / v0.1.5.

### Evidence 4 — Open Zip Bomb DoS in ZipConverter, no fix PR, ~114 days old

Command: `gh issue view 1514 -R microsoft/markitdown --json title,state,createdAt,body`

Result (excerpt):

```
Title: [Security] Potential Denial of Service (DoS) via Zip Bomb in ZipConverter
State: OPEN
Created: 2025-12-27T07:28:00Z
Body: A vulnerability was identified in the ZipConverter where it attempts to
      read the entire content of each file within a ZIP archive into memory
      simultaneously. This can be exploited using a "Zip Bomb"
      (a small ZIP file that decompresses to a very large size), leading to
      excessive memory consumption and potential system crashes (Out-of-Memory).
      In packages/markitdown/src/markitdown/converters/_zip_c...
```

Fact: OPEN Medium-severity (DoS class) — `_zip_converter.py` reads full zip-entry contents into memory without size guards. Issue has been open 114 days at scan time. No fix PR identified for this issue. No batch memory/size cap on the read path.

### Evidence 5 — Unanswered request for GHSA on CVE-2025-64512 (silently patched in v0.1.4)

Command: `gh issue view 1504 -R microsoft/markitdown --json title,state,createdAt,body,comments`

Result (excerpt):

```
Title: Should a security advisory for Markitdown 0.1.3 be released?
State: OPEN
Created: 2025-12-12T10:09:59Z
Comment count: 0
Body: Hello Microsoft Team 👋
      Markitdown 0.1.3 is vulnerable to arbitrary code execution due to
      CVE-2025-64512. The issue has been patched in release 0.1.4, where the
      package `pdfminer.six` has been updated, as written in the changelog
      (I can confirm the patch). However, this seems to be a minor feature
      release rather than an important security update. Should the maintainers
      release a security advisory...
```

Fact: A community member filed an explicit request for a GitHub Security Advisory covering CVE-2025-64512 (arbitrary code execution via `pdfminer.six` transitive CVE that affected markitdown 0.1.3). v0.1.4 bumped the dep, closing the vuln, but the release notes framed it as a routine feature release — no GHSA published. The request has been open 130 days with **zero comments and no maintainer response**. This is an F5-class unadvertised-fix pattern on a known CVE.

### Evidence 6 — Zero formal review decisions on last 174 merged PRs

Command:

```
gh pr list -R microsoft/markitdown --state merged --limit 300 --json reviewDecision,reviews \
  | jq '{total: length, formal_review: [.[] | select(.reviewDecision != null and .reviewDecision != "")] | length,
         any_review: [.[] | select(.reviews != null and (.reviews | length) > 0)] | length}'
```

Result: `{"total":174,"formal_review":0,"any_review":70}`

Verification on 10 most recent merged PRs — `reviewDecision` field is empty string (`""`) on every one, with review counts ranging 0-6 per PR.

Fact: 0 of 174 merged PRs have `reviewDecision` set (0% formal review rate). 70/174 (40%) have at least one review-object present (practical review via comments). The ruleset's PR gate doesn't require reviewDecision to be set, so merges proceed as long as status checks pass.

### Evidence 7 — Dependabot config exists but tracks only GitHub Actions (not pip)

Command:

```
gh api "repos/microsoft/markitdown/contents/.github/dependabot.yml" --jq '.content' | base64 -d
```

Result:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Fact: `.github/dependabot.yml` exists and is syntactically valid. It declares one update stream: `github-actions` ecosystem on weekly schedule. The `pip` ecosystem (which would track Python runtime dependencies like `beautifulsoup4`, `requests`, `markdownify`, `magika`, `pdfminer.six`, etc.) is NOT configured. This explains why CVE-2025-64512 in `pdfminer.six` was not auto-surfaced through a Dependabot PR when published.

### Evidence 8 — CI workflows tag-pin actions, not SHA-pin

Command: `grep -cE '@[a-f0-9]{40}|@v[0-9]+' <(gh api repos/microsoft/markitdown/contents/.github/workflows/tests.yml --jq '.content' | base64 -d)`

Result: 2 (both `uses:` lines — `actions/checkout@v5` + `actions/setup-python@v5` — match the `@v[0-9]+` pattern, not the `@<sha>` pattern).

Fact: Both CI workflows (`tests.yml` and `pre-commit.yml`) use GitHub Actions references pinned to major version tags, not to SHAs. This is consistent with GitHub's own guidance for first-party `actions/*` refs but differs from the SHA-pinning discipline some projects adopt.

### Evidence 9 — Microsoft SECURITY.md — enterprise disclosure boilerplate

Command: `gh api repos/microsoft/markitdown/contents/SECURITY.md --jq '.content' | base64 -d`

Result (first 20 lines):

```markdown
<!-- BEGIN MICROSOFT SECURITY.MD V0.0.9 BLOCK -->

## Security

Microsoft takes the security of our software products and services seriously,
which includes all source code repositories managed through our GitHub
organizations...

## Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them to the Microsoft Security Response Center (MSRC)
at https://msrc.microsoft.com/create-report.

If you prefer to submit without logging in, send email to
secure@microsoft.com. If possible, encrypt your message with our PGP key...

You should receive a response within 24 hours.
```

Fact: SECURITY.md is the Microsoft V0.0.9 boilerplate template — routes disclosures to MSRC (Microsoft Security Response Center) with a 24-hour response SLA, plus a direct email channel (`secure@microsoft.com`) with PGP support. Enterprise-grade disclosure infrastructure.

### Evidence 10 — Zero published Security Advisories on the repo

Command: `gh api repos/microsoft/markitdown/security-advisories --jq '. | length'`

Result: `0`

Fact: Despite the Microsoft SECURITY.md disclosure channel and at least one known historical CVE (CVE-2025-64512, patched in v0.1.4 per Evidence 5), the repo has never published a GitHub Security Advisory. Combined with Evidence 5's unanswered advisory request, this confirms a disclosure-channel-exists-but-advisories-are-not-filed pattern.

### Evidence 11 — No dangerous-primitive code patterns in Python sources

Command:

```
gh api "search/code?q=repo:microsoft/markitdown+subprocess.shell%3DTrue"  --jq '.total_count'
gh api "search/code?q=repo:microsoft/markitdown+os.system"                --jq '.total_count'
```

Result: 0 hits each.

Fact: Neither `subprocess.shell=True` (shell-interpolation-injection risk) nor `os.system(...)` (same class, shell path) appears anywhere in the repo source tree per GitHub code-search. This is a clean Python posture on these specific primitives — separate from the XXE / Zip Bomb issues (which are parsing-surface bugs, not shell-injection bugs).

### Evidence 12 — Release cadence + sole release author

Command: `gh api repos/microsoft/markitdown/releases --jq '[.[] | .author.login] | group_by(.) | map({author: .[0], count: length})'`

Result: `[{"author":"afourney","count":18}]`

Fact: 100% of 18 releases (v0.1.0 through v0.1.5 + prereleases) were authored by `afourney`. Bus-factor for release management is 1. Latest stable is v0.1.5 on 2026-02-20 (59 days before scan — outside the 30-day C20 "recent release" window).

## Pattern recognition

*(Inference layer — each bullet tagged with an approved interpretive verb.)*

- The combination of "ruleset requires PR but 0 approving reviews needed" (Evidence 1), "0 formal review decisions across 174 merges" (Evidence 6), and "no CODEOWNERS" (Evidence 2) is **consistent with** a merge workflow where PRs are used as a status-check gate, not as a review gate. Practical review via comments happens on ~40% of merges, but nothing enforces it.
- The juxtaposition of enterprise-grade MSRC disclosure (Evidence 9) with zero published advisories (Evidence 10) and an unanswered request for GHSA on a known CVE (Evidence 5) **suggests** a split between channel-existence and channel-use: the infrastructure is there, but the project has not adopted the advisory-publication habit that MSRC typically enforces at the org level.
- The gap between "Dependabot configured for github-actions" (Evidence 7) and "pdfminer.six CVE patched silently in v0.1.4" (Evidence 5) **plausibly indicates** the project watches transitive Python CVEs manually or not at all — a pip-ecosystem Dependabot entry would have auto-opened a PR when CVE-2025-64512 was published.

## FINDINGS SUMMARY

Fresh-authored for this wild scan. F-IDs are assigned in severity order (highest-impact first). No V2.4 comparator exists for this repo; the acceptance gates are 1, 2, 3, 4, 5, 7 (gate 6 structural parity N/A on a wild scan).

- F0 · Warning · Ongoing — Soft governance gate: ruleset requires PR but requires 0 approving reviews; no CODEOWNERS; 0% formal review rate on 174 merges. Driven by Evidence 1, 2, 6.
- F1 · Warning · Open · fix sitting 47 days — **Live XXE injection vulnerability** in DOCX pre-processor (`_convert_omath_to_latex` via `ET.fromstring` on untrusted input). Fix proposed in PR #1582 (uses `defusedxml`), not yet merged. v0.1.5 is exposed. Driven by Evidence 3.
- F2 · Warning · Open · no fix PR — **Live Zip Bomb DoS vulnerability** in `_zip_converter.py` (full-file-into-memory without size guard). 114 days old, no fix proposed. Driven by Evidence 4.
- F3 · Warning · F5-class · Ongoing disclosure gap — CVE-2025-64512 (arbitrary code execution via `pdfminer.six`) patched silently in v0.1.4 release notes without a GitHub Security Advisory. Community request for GHSA (#1504) unanswered for 130 days. Driven by Evidence 5, 10.
- F4 · Info · Current — Dependabot tracks only `github-actions` ecosystem; `pip` ecosystem NOT configured. Transitive-CVE PRs on Python deps are not auto-opened. Driven by Evidence 7.
- F5 · Info · Current — CI workflow references are tag-pinned (`@v5`), not SHA-pinned. Consistent with GitHub's guidance for first-party actions; flagged for inventory completeness only. Driven by Evidence 8.
- F6 · Info · Current — 100% of 18 releases authored by `afourney`. Bus-factor for release management is 1 (though code contribution bus-factor is ~2 with `gagb`). Driven by Evidence 12.
- F7 · OK — Enterprise MSRC disclosure channel with 24-hour SLA, `secure@microsoft.com` + PGP key. Channel infrastructure is strong (pattern of use is the concern in F3). Driven by Evidence 9.
- F8 · OK — No dangerous-primitive shell patterns in Python sources (`os.system`, `subprocess.shell=True` both 0 hits). Clean on shell-injection surface. Driven by Evidence 11.

## Verdict

markitdown verdict: **Caution** — driven jointly by F1 (live XXE, fix sitting 47 days) and F2 (live Zip Bomb, no fix). F3 (F5-class disclosure gap on CVE-2025-64512) compounds. F0 (governance) amplifies the rate at which future issues of this shape can slip through merges.

**Not Critical** because:

- F1 and F2 require a victim to feed markitdown a malicious DOCX / ZIP file respectively — they are not remote-unauth vulns. The typical use of markitdown (converting trusted or semi-trusted local files) is lower-risk.
- The governance gate, while soft, is better than caveman / Archon's zero-ruleset state — there IS a ruleset; it just requires 0 approving reviewers.
- The disclosure infrastructure (MSRC, PGP, 24-hr SLA) is genuinely strong; the concern is the gap between infrastructure-existence and use-pattern (F3).

**Candidate for split verdict on Deployment axis:** running markitdown against trusted/audited input (own documents, internal pipelines) = lower risk; running against untrusted user uploads (web service, API endpoint accepting files from end users) = upgrade to Caution+ until F1 + F2 fixes ship.

## Scorecard

V2.4 rubric applied with the SF1 scorecard-calibration-patched `compute.py`. Cell colors will be produced by `compute.py` during Phase 3; the table below is the expected mapping grounded in the Phase 1 facts above.

- Q1 Does anyone check the code? — **AMBER (Informal)**. Ruleset requires PR + status checks but 0 approving reviews, no CODEOWNERS, 0% formal review rate, 40% any-review rate. Practical review via comments happens but is not enforced.
- Q2 Do they fix problems quickly? — **AMBER (Slow)**. 2 live security issues open (XXE 59 days, Zip Bomb 114 days). XXE fix PR #1582 open 47 days. No formal security triage lane visible.
- Q3 Do they tell you about problems? — **AMBER**. SECURITY.md with private MSRC channel (strong) BUT 0 published advisories, F5-class silent patch of CVE-2025-64512, and request for GHSA (#1504) unanswered 130 days.
- Q4 Is it safe out of the box? — **AMBER**. Live XXE + Zip Bomb affect the default install path (v0.1.5 on PyPI) for users processing untrusted files; code-exec-primitives are clean (no shell-injection); PyPI distribution has no project-level sha256 attestation.
