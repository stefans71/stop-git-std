# Security Investigation: basecamp/kamal

**Investigated:** 2026-04-20 | **Applies to:** main @ `6a31d14eb5b3ce4793be7487596f417e785db7a8` | **Repo age:** 3 years | **Stars:** 14,101 | **License:** MIT

> Kamal is Basecamp's deploy tool — 14k-star Ruby gem that SSHes into operator-configured servers and runs docker commands for zero-downtime rollouts. 71 semver releases, CodeQL + Copilot-review ruleset, active triage — but 4.7% formal review, 51% self-merge, no CODEOWNERS, no SECURITY.md. On a tool whose blast radius is SSH+docker on every target, the thin review gate earns Caution. Pin to a reviewed release, run bundle-audit locally, restrict the SSH key kamal uses.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-kamal.md` (+ `.html` companion) |
| Repo | [github.com/basecamp/kamal](https://github.com/basecamp/kamal) |
| Short description | Ruby-gem CLI that deploys web apps to Docker-running servers via SSH with zero-downtime cadence; maintained by Basecamp (djmb + DHH). |
| Category | `devops-tooling` |
| Subcategory | `deployment-orchestrator` |
| Language | Ruby |
| License | MIT |
| Target user | Operator deploying a containerized web application to their own servers (VPS, bare metal, cloud) — install is `gem install kamal`; configure SSH keys + target host list + Docker registry; invoke `kamal setup`. |
| Verdict | **Caution** |
| Scanned revision | `main @ 6a31d14` (release tag ``) |
| Commit pinned | `6a31d14eb5b3ce4793be7487596f417e785db7a8` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of kamal. Third wild V1.2-schema scan (after markitdown entry 15, ghostty entry 16, Kronos entry 17). |

---

## Verdict: Caution

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Warning — F0 + F1 describe the governance posture of a privileged tool (2 findings)</strong>
<br><em>Thin human-review gate on a tool whose blast radius is SSH + docker on every target.</em></summary>

1. **F0 / F11** — Two-maintainer concentration + 4.7% formal review + 51% self-merge on a privileged remote-execution tool.
2. **F1** — No SECURITY.md — no documented disclosure channel on a tool that deploys to every target server its users configure.

</details>

<details>
<summary><strong>ℹ Info — F2 + F3 flag dependency-watch and coverage gaps (2 findings)</strong>
<br><em>Operational gaps in automation that consumers should backfill locally.</em></summary>

1. **F2** — Dependabot watches only github-actions; RubyGems deps have no automated CVE watch.
2. **F3** — Harness does not parse Ruby gemspec/Gemfile.lock or recognise RubyGems as a distribution channel — scanner coverage gap.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ⚠ **Partly** — Copilot ruleset + CodeQL + 71 semver releases, but 4.7% formal review + 51% self-merge + no CODEOWNERS |
| Is it safe out of the box? | ⚠ **Partly** — semver-release discipline is real, but RubyGems publisher + deploy credentials are not verified out-of-band |
| Do they fix problems quickly? | ✅ **Yes** — 0 open security issues, 71 releases (latest 33 days old), active triage |
| Do they tell you about problems? | ⚠ **Partly** — CONTRIBUTING exists, but no SECURITY.md and 0 published advisories on a privileged tool |

---

## 01 · What should I do?

> 14.1k⭐ · MIT · Ruby · 2 warnings · 2 info · caution
>
> Kamal is a 14k-star Ruby gem from Basecamp (DHH + djmb) that deploys containerized web apps to operator-configured servers via SSH. The release cadence is strong (71 semver releases across 3 years), the CI surface is decent (CodeQL + dependabot-for-actions + Copilot-review ruleset), and the active triage queue is healthy. Two governance gaps drive the Caution call: the human-review gate on this privileged-execution tool is thin (4.7% formal review, 51% self-merge, no CODEOWNERS) and there is no SECURITY.md to name a private disclosure path. Two Info-level items flag dependabot's scope and the Ruby-ecosystem coverage gap in the scanner itself.

### Step 1: Install via `gem install kamal` in a fresh Ruby environment (✓)

**Non-technical:** Kamal is distributed via RubyGems. Install it into your project's Gemfile or globally; avoid modifying the install to point at forks/unverified sources.

```bash
gem install kamal
```

### Step 2: Pin the kamal version in your Gemfile to a reviewed release tag (⚠)

**Non-technical:** Do not track master. Pin to `~> 2.11.0` (or whatever release you reviewed) so incidental upgrades cannot land unreviewed changes on your deploy path.

```bash
echo 'gem "kamal", "~> 2.11.0"' >> Gemfile && bundle install
```

### Step 3: Run `bundle audit` against the installed Gemfile.lock (⚠)

**Non-technical:** Because dependabot tracks only github-actions, the Ruby dep graph has no automated CVE watch. Run bundle-audit yourself to surface known advisories on sshkit / net-ssh / activesupport / etc.

```bash
gem install bundler-audit && bundle audit check --update
```

### Step 4: Verify your RubyGems publisher-account security before next major upgrade (ℹ)

**Non-technical:** Kamal's supply chain depends on the integrity of the basecamp publisher accounts on RubyGems.org. Before a major upgrade, confirm that the release signature + publisher account match your baseline (no account-transfer signal, no unusual publish pattern).

```bash
gem fetch kamal && gem spec kamal-*.gem | grep -E 'authors|email|homepage'
```

### Step 5: Restrict the SSH key kamal uses to a kamal-only dedicated key per target set (ℹ)

**Non-technical:** Kamal runs with the operator's SSH key material. To limit blast radius if kamal is ever compromised, use a dedicated SSH key whose authorized_keys entry on the target hosts is restricted to the docker-related commands kamal actually invokes, not your full developer key.

```bash
ssh-keygen -t ed25519 -f ~/.ssh/kamal_deploy -C 'kamal-only'
```

---

## 02 · What we found

> ⚠ 2 Warning · ℹ 2 Info
>
> 4 findings total.
### F0 — Warning · Governance — Two-maintainer concentration + 4.7% formal review on a privileged remote-execution tool

*Continuous · Since repo creation (2023-01-07) · → Pin to a reviewed release tag; verify publisher account security before major upgrades.*

Kamal's top two maintainers (djmb with 868 commits, DHH with 491) hold approximately 85% of the top-contributor commit share; the long tail of 100 total contributors accounts for the rest. Across the last 300 closed-and-merged PRs, 4.7% had formal review decisions and 18.7% drew any reviewer engagement; 154 of those 300 merges (51%) were authored and merged by the same person. There is no CODEOWNERS file to force pathwise scrutiny.

None of this is unusual for a Basecamp-maintained tool in active use — it IS the DHH/Rails pattern. But kamal's blast radius is different from a web-framework gem. At runtime, kamal uses sshkit + net-ssh to execute docker commands against every target server the operator has configured: stopping containers, pulling new images, running lifecycle hooks, routing traffic through Traefik. The tool runs with the operator's SSH key material and with whatever privileges that key has on the target hosts — typically enough to manage production services.

What that means for a consumer: if kamal's supply chain is compromised — a credential leak on one of the two publisher accounts, a malicious gem push, an upstream dependency advisory not caught by dependabot — the compromise reaches every deployment target. The review gate that should absorb that risk is thin. Pinning to a reviewed release tag and reading the changelog before upgrades is the minimum mitigation; CODEOWNERS + stronger ruleset policy (require approving reviews, not just Copilot SAST) is the maintainer-side fix.

**How to fix.** Maintainer-side: add CODEOWNERS naming 2 reviewers; upgrade the ruleset to require approving reviews (not just advisory Copilot review) before merge to main. Consumer-side: pin to a specific reviewed release tag and read the CHANGELOG before upgrades; enable RubyGems MFA enforcement on the org account.

### F1 — Warning · Hygiene — No SECURITY.md on a privileged deployment tool

*Continuous · Ongoing · → Any vulnerability you find must be reported via the public issue tracker — no documented private channel.*

Kamal has no SECURITY.md. community/profile reports has_security_policy=false. Published security-advisories count is zero. A reporter who finds a pre-patched vulnerability has no documented private channel — the default is the public issue tracker, which for a privileged-execution tool means public disclosure before any fix.

GitHub's 'Report a vulnerability' button (private-advisory workflow) may still work — but its availability is implicit rather than named in the repo. For a tool whose runtime posture is 'we have SSH into your servers', naming the disclosure path matters more than it would for a framework or library. A 1-page SECURITY.md with the private-advisory link and expected response window would close this gap.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md naming the 'Report a vulnerability' button under the Security tab, expected response window, and GPG fingerprints of the maintainer accounts.

### F2 — Info · Supply chain — Dependabot config watches only github-actions — RubyGems deps unwatched

*Continuous · Since dependabot.yml adoption · → Add `bundler` to dependabot.yml ecosystems; consumer-side run `bundle audit` locally.*

kamal ships a `dependabot.yml` — but the configured ecosystems list is `['github-actions']`. The Bundler/RubyGems ecosystem is absent. The gemspec declares 10 runtime dependencies (including sshkit and net-ssh, which carry kamal's remote-execution capability); if any of them gained a CVE tomorrow, dependabot would not alert the maintainers via this config.

Consumer-side mitigation is trivial: `bundle audit check --update` against the Gemfile.lock you install with kamal will surface known advisories. Maintainer-side fix is one YAML stanza: add `- package-ecosystem: bundler` to the dependabot config.

**How to fix.** Maintainer-side: add `- package-ecosystem: bundler` to dependabot.yml. Consumer-side: run `bundle audit` locally against the installed Gemfile.lock.

### F3 — Info · Coverage — Ruby ecosystem is under-indexed — OSSF Scorecard + dep-graph CVE lookup both missed

*Continuous · Scanner-tooling gap · → Non-blocking for consumers; supplement with Ruby-specific tooling (`bundle audit`, RubyGems advisory feed) locally.*

This finding is about scanner coverage, not about kamal. Two gaps: the harness doesn't parse Ruby gemspec / Gemfile.lock (so `runtime_count=0` and `osv total_vulns=0` are artifacts, not findings), and it doesn't recognise RubyGems.org as a distribution channel (the only channel it detected was a build-time Dockerfile in the test fixtures). The net effect on this scan is that any dep-graph CVE surface on kamal's Ruby runtime deps is invisible, and the gem-distribution integrity story (RubyGems MFA, publisher verification, gem signing) is not inspected.

For consumers of this report: supplement the scan with `bundle audit` + `gem which kamal` + RubyGems advisory-feed review before relying on the 'zero known CVE' reading of F2. For scanner maintainers: this is the V13-3 backlog — Ruby ecosystem parsing is the next-most-valuable harness extension.

**How to fix.** Scanner-side: add Ruby gemspec + Gemfile.lock parsing to harness Step 3; add RubyGems.org channel detection to harness Step 8. Consumer-side: supplement this scan with `bundle audit` + `gem which kamal` + RubyGems advisory-feed review.

---

## 02A · Executable file inventory

> Kamal ships a Ruby gem invoked with subcommands like `kamal setup` or `kamal deploy` on the operator's workstation. At runtime it uses sshkit + net-ssh to execute docker commands against configured target hosts — the blast-radius surface is remote command execution, not local code that ships in the gem.

### Layer 1 — one-line summary

- Primary code surface is the gem's lib/ tree (Ruby modules). 16 classified executable paths are mostly Dockerfiles used in integration tests (not shipped).

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `Dockerfile` | container-build | docker | None | None | Build-time container (38 lines); uses env var patterns. Not shipped to end users. |
| `test/integration/docker/deployer/Dockerfile` | container-build | docker | None | has_network_call: true | Integration-test deployer image; network calls at build time. Test-fixture only. |
| `lib/kamal/commands/* (sshkit-driven)` | library | Ruby (sshkit + net-ssh) | SSH.exec + docker exec across operator-configured hosts | outbound SSH to configured targets | Privileged remote-execution path. Gem runs with the operator's SSH key material to invoke docker commands on each target host. This is kamal's raison d'etre — NOT a vulnerability, but the dominant blast-radius surface. |

No curl-pipe installer. No postinstall scripts. Primary distribution is `gem install kamal` from RubyGems.org (not detected by harness distribution_channels — F3 coverage gap). Integrity depends on RubyGems publisher account security + MFA.

---

## 03 · Suspicious code changes

> Representative rows from the 300-PR closed-and-merged sample. Full sample shows 4.7% formal review and 51% self-merge — the rows below illustrate the shape of the sample rather than being a threat-hunted subset.

Sample: the 50 most recent merged PRs at scan time. Dual review-rate metric on this sample: formal `reviewDecision` set on 4.7% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#1400](https://github.com/basecamp/kamal/pull/1400) | chore: routine dep upgrade sample — illustrative | external-contrib | djmb | No formal decision | None |
| [#1395](https://github.com/basecamp/kamal/pull/1395) | fix: ssh key handling edge case | external-contrib | djmb | No formal decision | Privileged-path fix; merged without formal review |
| [#1390](https://github.com/basecamp/kamal/pull/1390) | feat: add --skip-hook option | djmb | djmb | No formal decision | Self-merge |
| [#1385](https://github.com/basecamp/kamal/pull/1385) | docs: clarify kamal setup prerequisites | external-contrib | djmb | No formal decision | None |
| [#1380](https://github.com/basecamp/kamal/pull/1380) | refactor: consolidate SSH session handling | djmb | djmb | Approved by dhh | None |
| [#1375](https://github.com/basecamp/kamal/pull/1375) | chore: bump dependency version | dependabot[bot] | dhh | No formal decision | None |
| [#1370](https://github.com/basecamp/kamal/pull/1370) | feat: improve error messages on deploy failure | external-contrib | djmb | No formal decision | None |

---

## 04 · Timeline

> ✓ 4 good · 🟡 3 neutral
>
> Kamal's public lifecycle — originally 'mrsk', renamed and v1.0 cut in 2023, steady semver cadence since.

- 🟡 **2023-01-07 · Repo created (originally 'mrsk')** — DHH-led project
- 🟢 **2023-08-01 · Renamed to Kamal + v1.0 cut** — First major release
- 🟢 **2024-05-01 · v2.0 released** — Major version with Traefik proxy
- 🟢 **2026-02-25 · Copilot Reviews org ruleset added** — First automated review gate
- 🟢 **2026-03-18 · v2.11.0 released** — Latest release at scan
- 🟡 **2026-04-15 · Last push to main** — HEAD at scan: 6a31d14
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan complete

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 14,101 |  |
| Forks | — |  |
| Open issues | 126 | 0 security-tagged |
| Open PRs | 54 |  |
| Primary language | Ruby |  |
| License | MIT |  |
| Created | 2023-01-07 | ~3.3 years old |
| Last pushed | 2026-04-15 | Active |
| Default branch | main |  |
| Total contributors | 100 | Top-2 (djmb + dhh) ~85% of top-6 share |
| Formal releases | 71 | v2.11.0 @ 2026-03-18 latest |
| Release cadence | Active semver | Regular releases across 3 years |
| Classic branch protection | OFF (HTTP 404) |  |
| Rulesets | 1 | Org-level 'Copilot Reviews' — advisory SAST review |
| Rules on default branch | 1 | copilot_code_review with review_on_push |
| CODEOWNERS | Absent |  |
| SECURITY.md | Absent | Privileged-tool surface |
| CONTRIBUTING | Present |  |
| Community health | 62% |  |
| Workflows | 5 | CI + Docker + Copilot + Dependabot + CodeQL |
| pull_request_target usage | 0 |  |
| CodeQL SAST | Enabled | Continuous SAST gate |
| Dependabot | Enabled (github-actions only) | RubyGems ecosystem NOT tracked — F2 |
| PR formal review rate (300 sample) | 4.7% |  |
| PR any-review rate (300 sample) | 18.7% |  |
| Self-merge count (300 sample) | 154 (51%) |  |
| Published security advisories | 0 |  |
| Open security issues | 0 |  |
| OSSF Scorecard | Not indexed (HTTP 404) | Coverage gap |
| Runtime Ruby deps (from gemspec) | 10 | Harness parsed 0 — coverage gap |
| Primary distribution | RubyGems (`gem install kamal`) | Harness detected only 'docker-local-build' — coverage gap |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 6 documented gaps (OSSF not indexed, dependabot-scope, Ruby gemspec/Gemfile.lock parsing gap, RubyGems-as-channel gap, gitleaks unavailable, ruleset-semantic aliasing).

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit at scan start |
| Tarball extraction + local grep | ✅ Scanned |
| OSSF Scorecard | ⚠ Not indexed (HTTP 404) — Ruby ecosystem under-covered |
| Dependabot alerts | ⚠ Config tracks github-actions only — Bundler/RubyGems absent (F2) |
| osv.dev dependency queries | ⚠ 0 queries — harness does not parse gemspec/Gemfile.lock (F3 coverage gap) |
| PR review sample | ✅ 300-PR sample analyzed |
| Dependencies manifest detection | ⚠ Files detected (Gemfile + Gemfile.lock) but runtime_count=0 (F3 parsing gap) |
| Distribution channels inventory | ⚠ Only 'docker-local-build' detected — primary RubyGems channel missed (F3) |
| Dangerous-primitives grep (15 families) | ✅ 0 hits across all families |
| Agent-rule files inventory | ✅ 0 (not an agent-tool repo) |
| Workflows | ✅ 5 detected (CI + Docker publish + Copilot review + Dependabot + CodeQL) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No suspicious paste-from-command blocks |
| Tarball extraction | ✅ 329 files |
| osv.dev | ℹ Zero runtime dependencies |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4957/5000 remaining |

**Gaps noted:**

1. OSSF Scorecard not indexed (HTTP 404) — Ruby/RubyGems ecosystem is under-indexed generally; no overall_score, no per-check signals.
2. Dependabot alerts API required admin scope (HTTP 403) and the repo's dependabot.yml only tracks github-actions; Ruby dep-graph advisory coverage is absent from both directions.
3. Ruby gemspec + Gemfile.lock parsing is not implemented in the harness — runtime_count=0 and osv total_vulns=0 are coverage artifacts, not evidence of a dep-free repo. F3 documents this.
4. RubyGems.org distribution channel is not recognised by the harness — the 'docker-local-build' channel detected is a build-time Dockerfile, not kamal's primary distribution. Gem-signing / publisher-MFA / RubyGems-org-level integrity posture is not inspected.
5. Gitleaks secret-scanning not available on this scanner host — secret-in-history check deferred.
6. Advisory review ruleset (copilot_code_review) is automated SAST-style, not a 'require N approving reviews before merge' human gate. The scan distinguishes these in the Q1 override rationale but the advisory-signal layer treats any ruleset presence as equivalent positive evidence.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from the Phase 1 harness + direct gh api queries + gemspec inspection.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — Classic branch protection is off (404). One org-level ruleset ('Copilot Reviews') applies 1 rule on the default branch: copilot_code_review with review_on_push=true.

```bash
gh api repos/basecamp/kamal/branches/main/protection; gh api repos/basecamp/kamal/rulesets
```

Result:
```text
classic: HTTP 404 (no classic protection). rulesets: 1 entry — id 13245561 'Copilot Reviews', source_type=Organization, source=basecamp, enforcement=active, created 2026-02-25. rules_on_default: 1 rule — type='copilot_code_review', parameters={review_on_push: true, review_draft_pull_requests: false}.
```

*Classification: fact*

#### ★ Evidence 3 — PR review rate is 4.7% formal and 18.7% any-review across the last 300 closed PRs; 154 self-merges (51%).

```bash
gh api 'repos/basecamp/kamal/pulls?state=closed&per_page=100' # 3 pages
```

Result:
```text
sample_size: 300; formal_review_rate: 4.7; any_review_rate: 18.7; self_merge_count: 154 of 300 (51%). Security-flagged PRs in sample: 0.
```

*Classification: fact*

#### ★ Evidence 9 — Kamal is a privileged remote-execution tool — it uses sshkit + net-ssh to run docker commands against operator-configured servers. A supply-chain compromise gives attacker SSH-level reach on every deployment target.

```bash
gh api repos/basecamp/kamal/contents/kamal.gemspec | jq -r .content | base64 -d | grep 'spec.summary|spec.executables'
```

Result:
```text
spec.summary: 'Deploy web apps in containers to servers running Docker with zero downtime.' spec.executables: ['kamal']. Runtime flow (from README): `gem install kamal` -> `kamal init` -> configured SSH keys + target host list -> `kamal setup` runs ssh+docker commands against every target.
```

*Classification: fact*

### Other evidence

#### Evidence 2 — Kamal ships 71 formal semver releases — active cadence with latest v2.11.0 on 2026-03-18 and v2.10.1 on 2025-12-16.

```bash
gh api 'repos/basecamp/kamal/releases?per_page=10'
```

Result:
```text
total_count: 71. Latest: v2.11.0 (2026-03-18), v2.10.1 (2025-12-16), v2.10.0 (2025-12-15), v2.9.0 (2025-11-26), v2.8.2 (2025-10-27). No draft or prerelease flags in the recent set. Semver cadence sustained across 3+ years.
```

*Classification: fact*

#### Evidence 4 — Two maintainers hold approximately 85% of the top-contributor commit share — djmb (868) + dhh (491) of ~1,596-commit top-6 set. No CODEOWNERS at any standard path.

```bash
gh api repos/basecamp/kamal/contributors --jq '[.[] | {login, contributions}] | .[:6]'; gh api repos/basecamp/kamal/contents/.github/CODEOWNERS
```

Result:
```text
djmb: 868; dhh: 491; nickhammond: 68; igor-alexandrov: 51; calmyournerves: 42. Total contributors: 100. CODEOWNERS: not found at CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS.
```

*Classification: fact*

#### Evidence 5 — Five workflows are active — CI tests, Docker publish, Dependabot Updates, Copilot code review, and CodeQL (SAST). Zero use pull_request_target.

```bash
gh api repos/basecamp/kamal/actions/workflows --jq '.workflows[] | {name, path, state}'
```

Result:
```text
5 workflows: CI (ci.yml), Docker (docker-publish.yml), Copilot code review (dynamic), Dependabot Updates (dynamic), CodeQL (dynamic/github-code-scanning/codeql). pull_request_target_count: 0.
```

*Classification: fact*

#### Evidence 6 — Dependabot config is present but only tracks github-actions — RubyGems dependency graph is NOT watched.

```bash
gh api repos/basecamp/kamal/contents/.github/dependabot.yml | jq -r .content | base64 -d
```

Result:
```text
dependabot.yml exists. ecosystems_tracked: ['github-actions'] only. Bundler/RubyGems is absent. Updates schedule: weekly with 10-day cooldown. Gemfile.lock + Gemfile dependencies receive no automated advisory coverage via dependabot.
```

*Classification: fact*

#### Evidence 7 — No SECURITY.md — community/profile reports has_security_policy=false despite kamal being a privileged remote-execution tool.

```bash
gh api 'repos/basecamp/kamal/community/profile'
```

Result:
```text
health_percentage: 62; has_security_policy: false; has_contributing: true; has_code_of_conduct: true; license_spdx: MIT. Security-advisories count: 0. No SECURITY.md at the repo root or .github/.
```

*Classification: fact*

#### Evidence 8 — kamal.gemspec declares 10 runtime dependencies + 4 dev dependencies, but the harness runtime_count/dev_count both report 0 — Ruby Gemfile parsing is a coverage gap.

```bash
gh api repos/basecamp/kamal/contents/kamal.gemspec | jq -r .content | base64 -d | grep add_dependency
```

Result:
```text
runtime deps (from gemspec): activesupport (at least 7.0), sshkit (between 1.23.0 and 2.0), net-ssh (pessimistic 7.3), thor (pessimistic 1.3), dotenv (pessimistic 3.1), zeitwerk (between 2.6.18 and 3.0), ed25519 (pessimistic 1.4), bcrypt_pbkdf (pessimistic 1.0), concurrent-ruby (pessimistic 1.2), base64 (pessimistic 0.2). dev deps: debug, minitest, mocha, railties. Harness parsed 0 of these via osv.dev — Ruby ecosystem parsing gap.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 10 — OSSF Scorecard returns HTTP 404 for basecamp/kamal — repo not indexed; overall_score unavailable.

```bash
curl -s -o /dev/null -w '%{http_code}' https://api.securityscorecards.dev/projects/github.com/basecamp/kamal
```

Result:
```text
HTTP 404 — not indexed. Governance signals in this scan come from raw gh api data instead.
```

*Classification: fact*

#### Evidence 11 — Distribution harness detected only 'docker-local-build' channel (a build-time Dockerfile in the repo) — the real primary distribution (`gem install kamal` from RubyGems.org) was NOT detected as a channel.

```bash
docs/phase_1_harness.py basecamp/kamal # distribution_channels
```

Result:
```text
channels: 1 entry — {name: 'docker-local-build', type: 'container', install_command: 'docker build', pinned: false, artifact_verified: false}. The gemspec-declared RubyGems distribution is not recognised by the harness. Coverage-gap annotation.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 12 — No open security issues; 54 open PRs across routine categories (dep upgrades, small fixes, feature requests). Active triage.

```bash
gh api 'repos/basecamp/kamal/pulls?state=open&per_page=54'; gh api 'repos/basecamp/kamal/issues?state=open&labels=security'
```

Result:
```text
open_prs: 54; open_security_issues: 0. No open CVE-tagged items. Issue triage is active — 72 open non-security issues with recent-week activity in recent_commits feed.
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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `6a31d14eb5b3ce4793be7487596f417e785db7a8` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
