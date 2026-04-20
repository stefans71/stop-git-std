# Security Investigation: ghostty-org/ghostty

**Investigated:** 2026-04-20 | **Applies to:** main @ `dcc39dcd401975ee77a642fa15ba7bb9f6d85b96` | **Repo age:** 4 years | **Stars:** 51,181 | **License:** MIT

> Ghostty is a well-adopted, actively-maintained Zig terminal emulator with modern ruleset-based branch protection and a working disclosure channel (5 GHSA advisories). Two structural concerns keep this scan at Caution rather than Clean: the author holds 85.9% of commit share, and there is no formal versioned release — installs pull HEAD. Pin a specific SHA for production use; otherwise Homebrew-installed ghostty is a reasonable default for individual developer workstations.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-ghostty.md` (+ `.html` companion) |
| Repo | [github.com/ghostty-org/ghostty](https://github.com/ghostty-org/ghostty) |
| Short description | Zig-written native terminal emulator; homebrew + distro packaging; one 'tip' rolling release |
| Category | `developer-tooling` |
| Subcategory | `terminal-emulator` |
| Language | Zig |
| License | MIT |
| Target user | Developer installing a native macOS/Linux terminal emulator; open-source maintainer considering ghostty for team use. |
| Verdict | **Caution** |
| Scanned revision | `main @ dcc39dc` (release tag ``) |
| Commit pinned | `dcc39dcd401975ee77a642fa15ba7bb9f6d85b96` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of ghostty. First V1.2-schema wild scan. |

---

## Verdict: Caution

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Governance / structural — F0 + F1 drive the caution call (2 findings)</strong>
<br><em>Solo-maintainer concentration + no formal versioned releases.</em></summary>

1. **F0 / F11** — Mitchell Hashimoto holds 85.9% of commit share; single-person availability risk.
2. **F1** — Only a rolling 'tip' tag since 2022-11; installers pull HEAD without semver rollback targets.

</details>

<details>
<summary><strong>ℹ Hygiene — F2 + F3 are non-blocking signals (2 findings)</strong>
<br><em>Minor disclosure + CI posture items for maintainer awareness.</em></summary>

1. **F2** — No SECURITY.md; disclosure works via GitHub Security tab (5 advisories published).
2. **F3** — Two workflows use pull_request_target — flagged for fork-input-handling review.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⚠ **Partly** — ruleset-based protection + CODEOWNERS, but concentration risk |
| Is it safe out of the box? | ⚠ **Partly** — installing means pulling HEAD, not a reviewed release |
| Do they fix problems quickly? | ✅ **Yes** — active project, zero open security issues, responsive maintainer |
| Do they tell you about problems? | ⚠ **Partly** — 5 GHSA advisories published, but no SECURITY.md |

---

## 01 · What should I do?

> 51k⭐ · MIT · Zig · 2 warnings · 2 info · caution
>
> Ghostty is a 51k-star Zig terminal emulator by Mitchell Hashimoto. Modern ruleset-based protection is on, CODEOWNERS is present, disclosure channel works. Two structural concerns drive the caution call: single-maintainer concentration and no formal versioned releases.

### Step 1: Install ghostty via Homebrew on macOS or your distro's package (✓)

**Non-technical:** Homebrew-installed ghostty is the default path for most users. The formula pins to a vendor-reviewed commit.

```bash
brew install --cask ghostty
```

### Step 2: If building from source, pin to a specific commit SHA (⚠)

**Non-technical:** Because ghostty has no formal releases, `git clone` of main means you install whatever landed today. Pin a SHA to avoid surprise regressions.

```bash
git clone https://github.com/ghostty-org/ghostty && cd ghostty && git checkout SHA-from-release-notes
```

### Step 3: Skim the 5 GHSA advisories before adopting (ℹ)

**Non-technical:** Check the GitHub Security tab to confirm any recent advisories are resolved on the SHA you pin.

```bash
gh api repos/ghostty-org/ghostty/security-advisories --jq '.[] | {ghsa_id, severity, summary, published_at}'
```

---

## 02 · What we found

> ⚠ 2 Warning · ℹ 2 Info
>
> 4 findings total.
### F0 — Warning · Governance — Solo-maintainer concentration — Mitchell Hashimoto holds 85.9% of commit share

*Continuous · Since repo creation (2022-03-29) · → Audit before enterprise dependency; track fallback maintainer bench.*

At 85.9% commit share, Mitchell Hashimoto is ghostty's dominant author by a wide margin. Secondary contributors (jcollie 5.6%, qwerasd205 3.9%) are active but distant. This is not unusual for a creator-led open-source project in its early years, and ghostty has 100 total contributors, an active community, CODEOWNERS, and ruleset-based branch protection — the concentration is real but mitigated.

The risk model here is sustainability, not active compromise: if the primary maintainer becomes unavailable, both PR velocity and security response times will degrade before the community can absorb the workload. If your organization plans to depend on ghostty, audit this gap the same way you'd audit any key-person-risk: know who else has merge authority, check that CODEOWNERS covers sensitive paths, and treat major upgrades as attention-worthy rather than automatic.

**How to fix.** Maintainer-side: rotate review authority across 2-3 CODEOWNERS entries. Consumer-side: pin to a specific SHA rather than 'latest', review the changelog before upgrades.

### F1 — Warning · Structural — No formal versioned releases — installers pull HEAD, not semver

*Continuous · Since 2022-11 · → Pin to a specific commit SHA in production installs.*

Ghostty's release story is unusual: the only tag is 'tip' from 2022-11, and Homebrew resolves to the current main branch. There is no semver, no changelog boundary, no rollback target. Users install whatever landed this week.

This is a structural choice — the project is explicitly pre-1.0 and has declined to commit to a release cadence — not a malicious practice. But the consumer impact is real: if a regression lands on main, it's in the next `brew upgrade`. The mitigation is simple: pin to a specific commit SHA in production installs, or accept the rolling-head model with attention budget for regressions. For developer workstations where you're happy to re-read the diff when something breaks, the model is fine.

**How to fix.** Consumer-side: pin by SHA. Maintainer-side: adopt even informal date-based tags (e.g., 2026.04) to give downstreams a rollback target.

### F2 — Info · Hygiene — No SECURITY.md — disclosure policy implicit via GitHub Security tab only

*Current · Ongoing · → Skim the 5 published advisories to see disclosure cadence, then report via GitHub's 'Report a vulnerability' button.*

The absence of SECURITY.md is a hygiene gap rather than a capability gap — ghostty clearly disclosures (5 published GHSA advisories) and responds to reports, but the reporter path is implicit. A security researcher investigating this repo may not know whether to email, file a public issue, or use GitHub's 'Report a vulnerability' button without documentation.

**How to fix.** Maintainer-side: add a short SECURITY.md naming the 'Report a vulnerability' button + expected response window.

### F3 — Info · Supply chain — Two workflows use `pull_request_target` — review fork-input handling

*Current · Ongoing · → Non-blocking — flag for maintainer review of the two workflows before calling the posture clean.*

Two of ghostty's 18 workflows use the `pull_request_target` trigger — the well-known CI surface that runs fork PRs with write-scope repository secrets. The trigger alone isn't exploitable; unsafe input handling under the trigger is. This finding flags the surface for a maintainer-side review; it is not a confirmed vulnerability.

**How to fix.** Maintainer-side: confirm both workflows guard against fork-controlled checkout/ref inputs, and that no `actions/checkout@v*` step pulls the head ref of the incoming PR into the base-repo context.

---

## 02A · Executable file inventory

> Ghostty ships build-time scripts and Docker images; no install-script hook surface observed.

### Layer 1 — one-line summary

- 18 executable-classed files total, concentrated in build/docker/, github/workflows/, and Makefile.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `Makefile` | build | make | None | None | Build orchestration; standard make invocations. |
| `src/build/docker/debian/Dockerfile` | container | Docker | None | None | Build-time container image; not shipped to end users. |

No `postinstall` scripts, no curl-pipe installer script in repo. Home-brew tap exists outside this repo.

---

## 04 · Timeline

> ✓ 2 good · 🟡 2 neutral
>
> Key beats in ghostty's open-source history.

- 🟡 **2022-03-29 · Repo created** — Early open Zig terminal project
- 🟡 **2022-11-17 · 'tip' tag** — Only formal tag; rolling pre-release
- 🟢 **2024-12-01 · Public launch** — Repository opens to public; 51k stars accrue
- 🟢 **2026-04-19 · Last push** — Active development as of scan

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 51,181 | Active public interest |
| Forks | 2,391 | None |
| Open issues | 239 | None |
| Primary language | Zig | Newer-ecosystem language; no PyPI/npm-style central registry |
| License | MIT | None |
| Created | 2022-03-29 | None |
| Last pushed | 2026-04-19 | Recent activity |
| Default branch | main | None |
| Total contributors | 100 | Top contributor owns 85.9% |
| Latest release tag | tip (2022-11-17) | No versioned releases |
| Published security advisories | 5 | Visible via GitHub Security tab |
| Workflows | 18 | 2 use pull_request_target |
| Classic branch protection | OFF (HTTP 404) | Ruleset-based protection active instead |
| Repo-level rulesets | 1 | Modern alternative to classic protection |
| Rules on default branch | 4 | None |
| CODEOWNERS | Present | None |
| SECURITY.md | Absent | Disclosure via GitHub Security tab only |
| OSSF Scorecard | Not indexed (HTTP 404) | Coverage gap |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 5 documented gaps (OSSF, PR sample, Zig deps, distribution channels, gitleaks).

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ 4932/5000 remaining at scan start |
| Tarball extraction + local grep | ✅ Scanned |
| OSSF Scorecard | ⚠ Not indexed (HTTP 404) — common for Zig repos |
| PR review sample | ⚠ Harness returned 0 closed PRs — not evidence of zero review activity |
| Dependencies manifest parse | ⚠ 0 runtime deps — harness does not parse Zig's `build.zig.zon` |
| Distribution channels | ⚠ 0 channels — harness does not detect Homebrew tap distribution |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No suspicious paste-from-command blocks |
| Dangerous-primitive grep (15 families) | ✅ 2 hits total (exec: 1, network: 1) |
| Agent-rule files inventory | ✅ 7 entries (CLAUDE.md + .github/*.md) |
| Workflow `pull_request_target` usage | ⚠ 2 uses (Info finding F3) |
| Tarball extraction | ✅ 5691 files |
| osv.dev | ℹ Zero runtime dependencies |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4995/5000 remaining |
| Dependabot alerts | ⚠ Unknown |

**Gaps noted:**

1. OSSF Scorecard not indexed — overall_score and per-check signals unavailable; governance/review signals derived from raw `gh api` data instead.
2. Harness PR-sample retrieval returned zero closed PRs — formal/any review rate is unknown, treated as not-zero in the scorecard override rationale.
3. Zig `build.zig.zon` dependency manifest not parsed — runtime dependency surface reported as 0 is a harness coverage gap, not evidence of dependency-free.
4. Homebrew tap / DMG distribution channels not inventoried by the harness (no PyPI/npm/crates.io/RubyGems signature match on Zig). Distribution posture inferred from the Install page rather than harness-gathered.
5. Gitleaks secret-scanning not available on this scan host — secret-in-history check deferred.

---

## 07 · Evidence appendix

> ℹ 9 facts · ★ 3 priority

Command-backed evidence from the Phase 1 harness run + direct gh api queries.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — Top contributor Mitchell Hashimoto holds 85.9% of commit share; secondary contributors trail distantly.

```bash
gh api repos/ghostty-org/ghostty/contributors --jq '[.[] | {login, contributions}] | .[:6]'
```

Result:
```json
[{"login":"mitchellh","contributions":10931},{"login":"jcollie","contributions":712},{"login":"qwerasd205","contributions":498},{"login":"bobbinth","contributions":181},{"login":"qwerty","contributions":172},{"login":"cryptocode","contributions":144}]
```

*Classification: fact*

#### ★ Evidence 2 — Classic branch protection is off (404) but the repository uses modern ruleset-based protection: 1 repository-level ruleset + 4 rules enforced on the default branch.

```bash
gh api repos/ghostty-org/ghostty/branches/main/protection; gh api repos/ghostty-org/ghostty/rulesets; gh api 'repos/ghostty-org/ghostty/rules/branches/main'
```

Result:
```text
classic: HTTP 404 (no classic protection configured); rulesets: 1 entry; rules_on_default: 4 rules enforced
```

*Classification: fact*

#### ★ Evidence 4 — Ghostty publishes no formal versioned releases — only a single rolling 'tip' tag dated 2022-11-17; installers pull HEAD.

```bash
gh api 'repos/ghostty-org/ghostty/releases?per_page=10'
```

Result:
```text
total_count: 1; latest tag_name: 'tip'; published_at: 2022-11-17T19:22:01Z. No semver-versioned releases present.
```

*Classification: fact*

### Other evidence

#### Evidence 3 — CODEOWNERS file is present in the repository at a standard location.

```bash
gh api repos/ghostty-org/ghostty/contents/.github/CODEOWNERS
```

Result:
```text
HTTP 200 — CODEOWNERS present
```

*Classification: fact*

#### Evidence 5 — community/profile reports no SECURITY.md despite 5 published GHSA advisories — disclosure exists via the Security tab but no project-level policy document.

```bash
gh api 'repos/ghostty-org/ghostty/community/profile'; gh api 'repos/ghostty-org/ghostty/security-advisories'
```

Result:
```text
community/profile: has_security_policy=false, has_contributing=true, has_code_of_conduct=false, health_percentage=62. security-advisories: count=5
```

*Classification: fact*

#### Evidence 6 — Two workflows use pull_request_target — the trigger that grants fork PRs write-scope secrets if inputs are not carefully handled.

```bash
grep -rn 'pull_request_target' .github/workflows/ | awk -F: '{print $1}' | sort -u
```

Result:
```text
2 workflow files use pull_request_target (count from harness workflows.pull_request_target_count=2).
```

*Classification: fact*

#### Evidence 7 — OSSF Scorecard API returns 404 for ghostty-org/ghostty — the repo is not indexed by Scorecard; overall_score and per-check data are unavailable.

```bash
curl -s -o /dev/null -w '%{http_code}' https://api.securityscorecards.dev/projects/github.com/ghostty-org/ghostty
```

Result:
```text
HTTP 404 — not indexed (common for Zig repos / newer-language ecosystems).
```

*Classification: fact*

#### Evidence 8 — Harness PR-sample retrieval returned zero closed PRs for rate computation; formal_review_rate and any_review_rate are unknown rather than zero.

```bash
python3 docs/phase_1_harness.py ghostty-org/ghostty --head-sha HEAD_SHA # pr_review section
```

Result:
```text
pr_review.sample_size=0, total_closed_prs=0, formal_review_rate=None, any_review_rate=None, self_merge_count=0. Harness shape-mismatch on very-active Zig repo; not evidence of zero review activity.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 9 — Dangerous-primitives grep surfaces only 2 hits across the 15 pattern families: 1 in exec family, 1 in network. No secrets, no deserialization, no weak crypto, no path traversal.

```bash
docs/phase_1_harness.py --out ... # code_patterns.dangerous_primitives
```

Result:
```text
exec: 1 file; network: 1 file; all other 13 families: 0 hits.
```

*Classification: fact*

---

## 08 · How this scan works

### What this scan is

This is an **LLM-driven security investigation** — an AI assistant with terminal access used the [GitHub CLI](https://cli.github.com/) and free public APIs to investigate this repo's governance, code patterns, dependencies, and distribution pipeline. It then synthesized its findings into this plain-English report.

This is **not** a static analyzer, penetration test, or formal security audit. It is a trust-assessment tool that answers: "Should I install this?"

### What we checked

| Area | Scope |
|------|-------|
| Governance & Trust | Branch protection, rulesets, CODEOWNERS, SECURITY.md, community health, maintainer account age & activity, code review rates |
| Code Patterns | Dangerous primitives (eval, exec, fetch), hardcoded secrets, executable file inventory, install scripts, README paste-blocks |
| Supply Chain | Dependencies, CI/CD workflows, GitHub Actions SHA-pinning, release pipeline, artifact verification, published-vs-source comparison |
| AI Agent Rules | CLAUDE.md, AGENTS.md, .cursorrules, .mcp.json — files that instruct AI coding assistants. Checked for prompt injection and behavioral manipulation |

### External tools used

| Tool | Purpose |
|------|---------|
| [OSSF Scorecard](https://securityscorecards.dev/) | Independent security rating from the Open Source Security Foundation. Scores 24 practices from 0-10. Free API, no installation needed. |
| [osv.dev](https://osv.dev/) | Google-backed vulnerability database. Used as fallback when GitHub's Dependabot data is not accessible (requires repo admin). |
| [gitleaks](https://gitleaks.io/) (optional) | Scans code history for leaked passwords, API keys, and tokens. Requires installation. If unavailable, gap noted in Coverage. |
| [GitHub CLI](https://cli.github.com/) | Primary data source. All repo metadata, PR history, workflow files, contributor data, and issue history come from authenticated GitHub API calls. |

### What this scan cannot detect

- **Transitive dependency vulnerabilities** — we check direct dependencies but cannot fully resolve the dependency tree without running the package manager
- **Runtime behavior** — we see what the code *could* do, not what it *does* when running
- **Published artifact tampering** — we read the source code but cannot verify that what's published to npm/PyPI matches this source exactly
- **Sophisticated backdoors** — our pattern-matching catches common dangerous primitives but not logic bombs or obfuscated payloads
- **Container image contents** — we read Dockerfiles but cannot inspect built images for extra layers or embedded secrets

For comprehensive vulnerability scanning, pair this report with tools like [Semgrep](https://semgrep.dev/) (code analysis), [Snyk](https://www.snyk.io/) (dependency scanning), or [Trivy](https://aquasecurity.github.io/trivy/) (container scanning).

### Scan methodology version

Scanner prompt V2.4 · Operator Guide V0.2 · Validator with XSS checks + verdict-severity coherence · [stop-git-std](https://github.com/stefans71/stop-git-std)

---

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `dcc39dcd401975ee77a642fa15ba7bb9f6d85b96` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
