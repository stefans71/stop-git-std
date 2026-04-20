# Phase 1 Checklist — external call → `phase_1_raw_capture` field mapping

**Purpose.** Every `phase_1_raw_capture.*` field has exactly one or more external data sources (gh api, curl, tar, grep, osv.dev, OSSF Scorecard, gitleaks, package registry). This document is the mapping. A Phase 1 scan is complete when every field this checklist marks **REQUIRED** has been populated from its source, and every field marked **EVIDENCE** has been attempted (recording a not-available marker if the source is unreachable).

**Scope:** V2.5-preview wild scans. `docs/phase_1_harness.py` is the executable implementation of this checklist. `tests/test_phase_1_harness.py` verifies the mapping with mocked sources.

**Canonical source for steps:** `docs/repo-deep-dive-prompt.md` Steps 1–8 + A/B/C. This checklist is the operational cross-reference.

---

## Legend

- **REQUIRED** — schema marks this field as required; scan cannot proceed without it.
- **EVIDENCE** — field populated from external call; if source unreachable, record the not-available marker (e.g. `ossf_scorecard.indexed=false + http_status=404`), not silently omit.
- **DERIVED** — field computed from other phase_1 data; no direct external call.
- **Fallback** — alternate source when primary fails.

---

## Pre-flight (runs before any Step)

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| pf1 | `gh api repos/OWNER/REPO --jq '.full_name'` | (verify repo exists) | REQUIRED | Abort — wrong owner/repo or network outage |
| pf2 | `gh api repos/OWNER/REPO --jq '.default_branch'` | `pre_flight.default_branch` | REQUIRED | Abort |
| pf3 | `gh api repos/OWNER/REPO/commits/BRANCH --jq '.sha'` | `pre_flight.head_sha` (full 40-char) | REQUIRED | Abort |
| pf4 | `gh api repos/OWNER/REPO/tarball/HEAD_SHA | tar --no-absolute-names -xz -C SCAN_DIR --strip-components=1` | `pre_flight.tarball_extracted`, `pre_flight.tarball_file_count` | EVIDENCE | Record `tarball_extracted=false` + reason; Steps A/B/C must then skip local-grep sections and note the gap in `coverage_affirmations` |
| pf5 | `find SCAN_DIR -type l -delete` (strip symlinks) then count | `pre_flight.symlinks_stripped` | EVIDENCE | If pf4 failed, record `null` |
| pf6 | `gh api rate_limit` | `pre_flight.api_rate_limit` | EVIDENCE | Record `unknown` if query fails |

---

## Step 1 — Repo basics and maintainer background

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 1a | `gh api repos/OWNER/REPO` | `repo_metadata.{name, description, created_at, pushed_at, stargazer_count, archived, fork, license_spdx, default_branch}` | REQUIRED | Abort (repo check already run in pf1) |
| 1b | `gh api repos/OWNER/REPO/contributors?per_page=30` | `contributors.top_contributors[{login, contributions}]` (6 top by default) + `total_contributor_count` | EVIDENCE | Record `total_contributor_count=null`, `top_contributors=[]` with note |
| 1c | For each top contributor + owner: `gh api users/LOGIN --jq '{login, type, created_at, public_repos, followers, company}'` | `maintainer_accounts.accounts[]` | EVIDENCE | Per-entry partial (skip failing) |
| 1d | `curl -s https://api.securityscorecards.dev/projects/github.com/OWNER/REPO` | `ossf_scorecard.{queried=true, indexed, overall_score, checks[], raw_response}` | EVIDENCE | 404 → `indexed=false, http_status=404`. Timeout → `queried=false`. |
| 1e | `gh api repos/OWNER/REPO/community/profile` | `community_profile.{health_percentage, has_code_of_conduct, has_contributing, has_security_policy, license_spdx}` | EVIDENCE | All fields `null` on 404 |
| 1f | `gh api repos/OWNER/REPO/branches/BRANCH/protection` | `branch_protection.classic.{status, body}` | EVIDENCE | 404 is authoritative negative (no rule). 403 is authorisation failure — record distinctly. |
| 1g | `gh api repos/OWNER/REPO/rulesets` | `branch_protection.rulesets.{entries[], count}` | EVIDENCE | 404 → empty |
| 1h | `gh api repos/OWNER/REPO/rules/branches/BRANCH` | `branch_protection.rules_on_default.{entries[], count}` | EVIDENCE | 404 → empty |
| 1i | If owner type is Organization: `gh api orgs/OWNER/rulesets` | `branch_protection.org_rulesets.{entries[], status}` | EVIDENCE | 403 common (scope) — record `status=403, entries=[]` |
| 1j | `gh api repos/OWNER/REPO --jq '.owner.type'` | `branch_protection.owner_type` | DERIVED | Ensures 1i correctness |
| 1k | For each of 4 standard paths (`CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`, `.gitlab/CODEOWNERS`): `gh api repos/OWNER/REPO/contents/$PATH` | `codeowners.{found, path, content, locations_checked[]}` | EVIDENCE | All 404 → `found=false, path=null, content=null` |
| 1l | `gh api repos/OWNER/REPO/releases?per_page=100` | `releases.{entries[], total_count}` | EVIDENCE | 404 or empty → `entries=[], total_count=0` |
| 1m | `gh api repos/OWNER/REPO/security-advisories` | `security_advisories.{count, entries[]}` | EVIDENCE | 404 → `count=0, entries=[]`. Records Published GHSAs only — not open issues. |

---

## Step 2 — CI workflows

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 2a | `gh api repos/OWNER/REPO/actions/workflows` | `workflows.{entries[{name, path, state}], count}` | EVIDENCE | Empty on 404 |
| 2b | For each workflow file: `gh api repos/OWNER/REPO/contents/.github/workflows/FILE --jq '.content' | base64 -d` | `workflow_contents.entries[{path, content, sha_pinned_actions_count, tag_pinned_actions_count, has_pull_request_target, permissions_block_present}]` | EVIDENCE | Per-file retry; missing files → `content=null` |
| 2c | For each workflow content: grep `pull_request_target` | `workflows.pull_request_target_count` | DERIVED | from 2b |
| 2d | For each workflow content: grep `uses:.*@[a-f0-9]{40}` (SHA) vs `uses:.*@v[0-9]+` (tag) | workflow-level pinning stats embedded in `workflow_contents.entries[]` | DERIVED | from 2b |
| 2e | For each workflow: grep `^permissions:` top-level block | `workflow_contents.entries[].permissions_block_present` | DERIVED | from 2b |

---

## Step 2.5 — Agent-rule file detection (V2.2+)

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 2.5a | `find SCAN_DIR \( -name 'CLAUDE.md' -o -name 'AGENTS.md' -o -name 'GEMINI.md' -o -name '.cursorrules' -o -name '.mcp.json' -o -name 'copilot-instructions*' -o -path '*/.cursor/rules/*' -o -path '*/.windsurf/rules/*' -o -path '*/.clinerules/*' \) -not -path '*/node_modules/*'` | `code_patterns.agent_rule_files[{path, kind, file_sha, line_count, ci_amplified}]` | EVIDENCE | If tarball extraction failed (pf4), fall back to `gh api repos/OWNER/REPO/git/trees/HEAD?recursive=1` filter; record `source=api-tree-fallback` |
| 2.5b | `grep -rlP '\.cursor/rules/\|\.windsurf/rules/\|\.clinerules/\|copilot-instructions' SCAN_DIR/.github/workflows/` | Mark `code_patterns.agent_rule_files[].ci_amplified=true` for amplified source files | DERIVED | from 2.5a + grep |
| 2.5c | Prompt-injection text grep (see Step A row 5 below): `grep -riliP 'ignore (all )?(previous\|prior) instructions\|disregard.*instructions\|you are now\|pretend you are\|system prompt\|override.*safety\|jailbreak' SCAN_DIR` filtered to agent-rule files | `prompt_injection_scan.{scanned_files[], injection_signals[], signal_count}` | EVIDENCE | If tarball missing, mark `scanned_files=[]` + gap note |

---

## Step 3 — Dependencies and supply chain

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 3a | `gh api repos/OWNER/REPO/contents/` + recursive manifest filter | `dependencies.manifest_files[{path, ecosystem}]` (package.json, pyproject.toml, requirements*.txt, Pipfile, Gemfile, go.mod, Cargo.toml, pom.xml, build.gradle, composer.json) | EVIDENCE | Empty on 404 |
| 3b | For each manifest: fetch content, parse direct deps per ecosystem | `dependencies.{runtime[{name, ecosystem, pinning}], runtime_count, dev[...], dev_count}` | EVIDENCE | Per-manifest parse failures logged, not fatal |
| 3c | `gh api repos/OWNER/REPO/dependabot/alerts --paginate` | `dependencies.dependabot_alerts_status` (200 with data, 403 unauthorized, 404 disabled) | EVIDENCE | 403 → set fallback flag for 3d |
| 3d | **Fallback when 3c=403**: for each direct dep in 3b, `curl -s https://api.osv.dev/v1/query -d '{"package":{"name":"PKG","ecosystem":"ECOSYSTEM"}}'` per ecosystem mapping (npm→"npm", PyPI→"PyPI", crates.io→"crates.io", Go→"Go", RubyGems→"RubyGems", Maven→"Maven", Packagist→"Packagist") | `dependencies.osv_lookups[{name, ecosystem, vulns_count, vulns_summary}]` | EVIDENCE | Per-dep retry once; record `vulns_count=null` on persistent failure |
| 3e | `gh api repos/OWNER/REPO/contents/.github/dependabot.yml` | `defensive_configs.entries[]` (append dependabot config analysis: which ecosystems tracked) | EVIDENCE | 404 → `dependabot_config_present=false` |

---

## Step 4 — PR history with review rates

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 4a | `gh api "search/issues?q=repo:OWNER/REPO+is:pr+is:merged&per_page=1" --jq '.total_count'` | `pr_review.total_merged_lifetime` (headline count) | EVIDENCE | 0 or error → `null` |
| 4b | `gh pr list -R OWNER/REPO --state merged --limit 300 --json number,title,reviewDecision,reviews,author,mergedBy,mergedAt,labels` | `pr_review.{total_closed_prs, sample_size, prs[{number, title, review_decision, any_review_count, self_merge, merged_at, labels}]}` | EVIDENCE | Truncate at API limit; record actual sample_size |
| 4c | Aggregate 4b: count `reviewDecision != "" and != null` | `pr_review.formal_review_rate` | DERIVED | from 4b |
| 4d | Aggregate 4b: count `reviews | length > 0` | `pr_review.any_review_rate` | DERIVED | from 4b |
| 4e | Aggregate 4b: count `author.login == mergedBy.login` | `pr_review.self_merge_count` | DERIVED | from 4b |
| 4f | `gh pr list -R OWNER/REPO --state open --limit 300` | `open_prs.{entries[], count}` | EVIDENCE | Empty on error |
| 4g | `gh pr list -R OWNER/REPO --state closed --search 'is:unmerged' --limit 100` | `closed_not_merged_prs.{entries[], count}` | EVIDENCE | Empty on error |

---

## Step 5 — Drill into security-relevant PRs (F3)

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 5a | `gh api "search/issues?q=repo:OWNER/REPO+is:pr+in:title+security+OR+CVE+OR+vulnerability+OR+exploit+OR+RCE+OR+auth+OR+security"` | Mark `pr_review.prs[].security_flagged=true` by PR number | DERIVED | Intersection with 4b; absent PRs noted as search-only hit |
| 5b | For each security-flagged open PR (top 10): `gh pr view NUM -R OWNER/REPO --json createdAt,state,reviews,comments` | `pr_review.prs[].open_security_details` | EVIDENCE | Rate-limit aware |

---

## Step 6 — Issues (user-reported problems)

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 6a | `gh api "search/issues?q=repo:OWNER/REPO+is:open+in:title+security+OR+CVE+OR+vulnerability+OR+exploit+OR+DoS"` | `issues_and_commits.open_security_issues[{number, title, state, created_at, labels}]` | EVIDENCE | Empty on error |
| 6b | For each open security issue: `gh issue view NUM -R OWNER/REPO --json title,state,body,labels,createdAt,comments --jq '{... comment_count: (.comments | length)}'` | Enrich 6a entries with body-snippet + comment_count | EVIDENCE | Per-issue partial |
| 6c | `gh api "search/issues?q=repo:OWNER/REPO+is:closed+security"` (last 10) | `issues_and_commits.closed_issues[]` + `closed_issues_count` | EVIDENCE | Empty on error |
| 6d | `gh api "repos/OWNER/REPO/issues?state=open&per_page=1" --jq '.[0]'` header `Link` rel=last for full open count | `issues_and_commits.open_issues_count` | EVIDENCE | Fall back to naive count if Link header absent |

---

## Step 7 — Recent commits

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 7a | `gh api "repos/OWNER/REPO/commits?per_page=100&since=TIMESTAMP"` (last 90 days) | `issues_and_commits.recent_commits[{sha, author, date, message_first_line}]` | EVIDENCE | Empty on error |
| 7b | Grep 7a for security keywords (security:, fix:, CVE, vuln, auth, injection, XXE, SSRF, RCE, DoS, XSS, leak, symlink, privilege) | Flag `issues_and_commits.recent_commits[].security_keyword_match` | DERIVED | from 7a |

---

## Step 7.5 — README install-paste scan

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 7.5a | `gh api repos/OWNER/REPO/contents/README.md --jq '.content' | base64 -d` | (fetch README content for scanning) | EVIDENCE | 404 → mark `code_patterns.readme_paste_blocks.scanned=false` |
| 7.5b | Also scan `docs/README.md`, `docs/` recursively if present | | EVIDENCE | Shared with 7.5a |
| 7.5c | Grep: `grep -niE 'paste (this\|the (following\|snippet\|code\|block))\|copy (this\|these) (into\|to) (your\|the).*system prompt\|add (this\|these) to your (rules\|agent)\|include (this\|these) in (your\|the) (system prompt\|rules)\|place this in\|put this in.*(rules\|agent\|system)'` on fetched README | `code_patterns.readme_paste_blocks.{scanned=true, entries[{file, line, snippet}], entries_count}` | EVIDENCE | Returns empty list if no hits (distinct from `scanned=false`) |

---

## Step 8 — Installed-artifact verification (F1)

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| 8a | Enumerate distribution channels from repo evidence (README install sections + pyproject.toml + package.json + Dockerfile + .claude-plugin/plugin.json + Cargo.toml + marketplace manifest) | `distribution_channels.channels[{name, type, package, install_command, pinned, install_path_verified, artifact_verified, note}]` | EVIDENCE | This is a synthesis step — derived from 3a manifests + 7.5a README + Dockerfile presence |
| 8b | For each channel, per-ecosystem verification: | `artifact_verification.per_channel[{channel, method, result, note}]` | EVIDENCE | — |
| 8b.1 | **PyPI**: `curl -s https://pypi.org/pypi/PACKAGE/json | jq '{name, version, upload_time}'` | `artifact_verification.per_channel[].result={verified|not_verified}` + note (sha256 attestation published?) | EVIDENCE | 404 → `result=unavailable, note="PyPI has no such package"` |
| 8b.2 | **npm**: `curl -s https://registry.npmjs.org/PACKAGE --max-time 10 | jq '.dist-tags.latest'` | Same | EVIDENCE | 404 → same |
| 8b.3 | **crates.io**: `curl -s https://crates.io/api/v1/crates/PACKAGE | jq '.crate.newest_version'` | Same | EVIDENCE | 404 → same |
| 8b.4 | **RubyGems**: `curl -s https://rubygems.org/api/v1/gems/PACKAGE.json` | Same | EVIDENCE | 404 → same |
| 8b.5 | **Go proxy**: `curl -s https://proxy.golang.org/MODULE/@v/list` | Same | EVIDENCE | 404 → same |
| 8b.6 | **Docker Hub / GHCR**: `curl -s https://hub.docker.com/v2/repositories/PACKAGE/tags/?page_size=1` (Hub) or `gh api /users/USER/packages/container/PACKAGE/versions` (GHCR) | Same | EVIDENCE | Dual-path; GHCR requires auth scope |
| 8b.7 | **Install script**: grep `SCAN_DIR/install*.sh`, `install*.ps1`, `hooks/install*` for `curl\|wget\|Invoke-WebRequest\|DownloadString` + tag-pin-vs-SHA-pin check (`raw.githubusercontent.com/[^/]+/[^/]+/main\b` vs `@v[0-9]+` or `@[a-f0-9]{40}`) | `install_script_analysis.scripts[{file, writes, network, injection_channel, env_var_pattern, pinning_style}]` | EVIDENCE | Empty list if no install scripts |

---

## Step A-pre — Secrets-in-history scan (Cap-4)

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| Ap1 | `command -v gitleaks` | `gitleaks.available` | EVIDENCE | Boolean |
| Ap2 | If available: `gitleaks detect --source SCAN_DIR -v --redact --no-git` | `gitleaks.{ran=true, findings_count, findings[{rule_id, file, line, redacted_match}]}` | EVIDENCE | Parse stdout for "N finding(s)". If exit=1 with zero findings, record and continue. |
| Ap3 | If not available: record `gitleaks.available=false, ran=false` | and populate `coverage_affirmations.gitleaks_available=false, gitleaks_explanation` with the "install gitleaks" note | REQUIRED when Ap1=false | — |

---

## Step A — Grep for dangerous patterns (runs in extracted tarball)

Each pattern family returns `{hit_count, files[]}`. A hit opens a Step-B targeted read; the grep matches alone populate `code_patterns.dangerous_primitives`.

| # | Pattern family | Grep target | Form sub-field |
|---|---|---|---|
| A1 | Code execution | `eval\(, Function\(, vm.runIn, exec\(, execSync, spawnSync, child_process, subprocess.(call\|Popen\|run), os.system, shell=True, Runtime.getRuntime().exec` | `code_patterns.dangerous_primitives.exec[]` |
| A2 | Deserialization | `pickle.loads?, yaml.load\(, unserialize\(, ObjectInputStream, Marshal.load, marshal.loads?, joblib.load, dill.loads?` (V13-3 C2: bare `deserialize` keyword dropped — was a false-positive source on ArduinoJson `deserializeJson` / serde `deserialize` in C/C++/Rust. Unsafe-specific method names preserved.) | `code_patterns.dangerous_primitives.deserialization[]` |
| A3 | Network / fetch | `fetch\(, XMLHttpRequest, axios., got\(, http.(get\|post\|request), requests.(get\|post\|put\|delete), urllib.request, net.(connect\|Socket), http.Client, WebSocket, url.URL\(, RestTemplate` | `code_patterns.dangerous_primitives.network[]` |
| A4 | Secrets / credentials | `(api[_-]?key\|secret\|token\|password\|passwd\|pwd\|auth)\s*[:=]\s*["'][A-Za-z0-9_\-\.]{16,}` and vendor-prefix regex (sk-, ghp_, xox, AIza, AKIA) | `code_patterns.dangerous_primitives.secrets[]` |
| A5 | CORS / bind-all / TLS-disabled | `Access-Control-Allow-Origin.*\*`, `0\.0\.0\.0`, `rejectUnauthorized: false`, `verify=False`, `CURLOPT_SSL_VERIFYPEER.*false`, `InsecureSkipVerify: true` | `code_patterns.dangerous_primitives.tls_cors[]` |
| A6 | SQL injection | `query\(.*\${, execute\(f"…, .raw\(, SELECT.*\+.*\$, Statement.execute(Query\|Update)?\(.*\+, Model.(find\|where)\("#\{` | `code_patterns.dangerous_primitives.sql_injection[]` |
| A7 | Command injection | `exec\(.*\${, system\(.*\${, \`.*\${.*\}.*\`` | `code_patterns.dangerous_primitives.cmd_injection[]` |
| A8 | Auth bypass | `validate_exp=False, verify_signature=False, algorithm: 'none', disableSignUp: false`, `req.(body\|query\|params).(admin\|role\|isAdmin)`, `trust.*client.*id` | `code_patterns.dangerous_primitives.auth_bypass[]` |
| A9 | Path traversal | `readFileSync\(.*\+, path.join\(.*req., open\(.*\+.*(request\|params), os.path.join\(.*request., filepath.Join\(.*r\.URL, File\.new\(.*params\[` | `code_patterns.dangerous_primitives.path_traversal[]` |
| A10 | Archive extraction (zip slip) | `ZipFile, extractAll\(, tar.extract\(` | `code_patterns.dangerous_primitives.archive_unsafe[]` |
| A11 | SSRF / cloud metadata | `http.get\(\s*(req\|params\|request\|body), urllib.request.urlopen\(\s*request, image_from_url\(, webhook.*url`, `169\.254\.169\.254`, `metadata\.google\.internal`, `fd00:ec2` | `code_patterns.dangerous_primitives.ssrf[]` |
| A12 | DOM XSS | `innerHTML\s*=, dangerouslySetInnerHTML, document.write, .html\(.*\+, v-html=` | `code_patterns.dangerous_primitives.xss[]` |
| A13 | Weak crypto | `\bmd5\(, hashlib.md5, crypto.createHash\("md5, DigestUtils.md5, \bsha1\(, hashlib.sha1, Math.random.*(token\|secret\|session\|id), rand\(\).*(token\|secret), random.random.*token, \bDES\b, Cipher.getInstance\("DES, RC4` | `code_patterns.dangerous_primitives.weak_crypto[]` |
| A14 | Debug / dangerous-config | `DEBUG\s*=\s*(True\|true), debug:\s*true, NODE_ENV.*development, app.debug = True, dangerouslySkipPermissions.*true, ignoreSSL, skipSSLVerification` | `code_patterns.dangerous_primitives.debug_flags[]` |
| A15 | Secret files | `find` for `.env, .env.local, .env.production, *.pem, id_rsa*, credentials*` (exclude node_modules) | `code_patterns.dangerous_primitives.secret_files[]` |
| A16 | Prompt injection text | `grep -riliP 'ignore (all )?(previous\|prior) instructions\|disregard.*instructions\|you are now\|pretend you are\|system prompt\|override.*safety\|jailbreak'` | `prompt_injection_scan.injection_signals[]` |

Each sub-array: `[{file, line_snippet, match_count}]`. If SCAN_DIR unavailable (pf4 failed), populate empty with note "tarball extraction unavailable; grep deferred."

---

## Step B — Targeted read (LLM judgment, not data-gathering)

Step B is NOT a harness-executable step. When Step A surfaces hits, a quarantined LLM read produces findings that land in `phase_4_structured_llm.findings.entries[]`, not in `phase_1_raw_capture`. The harness records Step A hits and stops; Phase 4 authoring translates them.

---

## Step C — Executable file inventory + Windows patterns

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| C1 | ALWAYS-SCAN list inspection: enumerate `install.sh`, `install.ps1`, `uninstall*`, `hooks/*.js`, `hooks/*.sh`, `.github/workflows/*.yml`, `setup.py`, `Dockerfile`, `docker-entrypoint*.sh`, `Makefile` under SCAN_DIR | `code_patterns.executable_files[{path, kind, runtime}]` | EVIDENCE | Missing-file entries omitted, not nulled |
| C2 | For each executable: compute file SHA (`sha1sum` or git-blob-hash), count lines | `code_patterns.executable_files[].{file_sha, line_count}` | DERIVED | from C1 |
| C3 | Per-file grep for `dangerous_calls` (intersection with Step A patterns scoped to file) | `code_patterns.executable_files[].dangerous_calls` | DERIVED | |
| C4 | Per-file grep for network calls (curl\|wget\|fetch\|requests\|http) | `code_patterns.executable_files[].network` | DERIVED | |
| C5 | `grep -rlP 'Invoke-Expression\|iex\b\|Invoke-Command\|$ExecutionContext.InvokeCommand\|Start-Process\s+.*$(\w+)\|-ExecutionPolicy\s+Bypass\|-EncodedCommand\|-Exec\s+Bypass\|Invoke-WebRequest\|iwr\b\|DownloadString\|DownloadFile\|WebClient\|Get-Credential\|$env:USERPROFILE\|ConvertFrom-SecureString' --include='*.ps1' --include='*.bat' --include='*.cmd' SCAN_DIR` | `windows_patterns.{hits[{pattern_family, file, line_count}], hit_count}` | EVIDENCE | If no PS1/BAT/CMD files, empty with note |

---

## Monorepo detection

| # | External call | Form field | Type | Failure mode |
|---|---|---|---|---|
| M1 | `find SCAN_DIR -name 'pyproject.toml' -o -name 'package.json' -not -path '*/node_modules/*'` — if 2+ found in different sub-directories → monorepo | `monorepo.{is_monorepo, inner_packages[{path, name, kind}]}` | DERIVED | from 3a manifests; fallback to `gh api .../contents/packages` if tarball missing |
| M2 | Per inner package: search for lifecycle scripts in `package.json` (`preinstall`, `postinstall`, `prepare`, `prepublish`) | `monorepo.lifecycle_script_hits[{path, hook_name}]` | DERIVED | |

---

## Defensive configs

| # | Source | Form field |
|---|---|---|
| D1 | `.github/dependabot.yml` (3e) content + ecosystems tracked | `defensive_configs.entries[]` with `type=dependabot` |
| D2 | `.pre-commit-config.yaml` content | `defensive_configs.entries[]` with `type=pre-commit` |
| D3 | `SECURITY.md` content | `defensive_configs.entries[]` with `type=security-policy` |
| D4 | `.github/CODEOWNERS` (already captured in 1k) — surface summary only | `defensive_configs.entries[]` with `type=codeowners, present=false` |
| D5 | `.gitignore`, `.gitattributes` — scan for secret-file exclusion patterns | `defensive_configs.entries[]` with `type=gitignore` |
| D6 | Renovate config (`renovate.json`, `.github/renovate.json`, `.renovaterc`) — alternative to dependabot | `defensive_configs.entries[]` with `type=renovate` |

All DERIVED from prior fetches; no new external calls.

---

## Batch-merge detection (caveman pattern)

| # | Source | Form field |
|---|---|---|
| B1 | From `pr_review.prs[]` (4b): group by `merged_at` timestamp with resolution truncated to 5 minutes. Any group ≥5 PRs → batch-merge event. | `batch_merge_detection.{detected, pr_groups[{merged_at, pr_count, prs[numbers]}]}` |

DERIVED from 4b.

---

## Coverage affirmations

| # | Source | Form field |
|---|---|---|
| CA1 | Did Step 2.5 execute? | `coverage_affirmations.prompt_injection_scan_completed` |
| CA2 | Are there PS1 files? Step C5 result | `coverage_affirmations.windows_surface_coverage` |
| CA3 | Total channels enumerated (8a) vs. channels fully verified (8b) | `coverage_affirmations.distribution_channels_verified` (e.g. "3/5") |
| CA4 | Was gitleaks available and run? (Ap1+Ap2) | `coverage_affirmations.gitleaks_available` + `gitleaks_explanation` |

DERIVED from prior steps.

---

## Not harness-scope (deferred)

The following phase_1 sub-fields require LLM synthesis or are not directly populated by the harness:

- `code_patterns.install_hooks` — subset of `executable_files` filtered to install-context; LLM synthesis during Phase 4 authoring.
- `distribution_channels.channels[].notes` — one-line reason for classification; LLM synthesis.

Harness leaves these as empty/None; Phase 4 LLM fills them.

---

## Execution ordering

Pre-flight → Step 1 → Step 2 → Step 2.5 → Step 3 → Step 4 → Step 5 → Step 6 → Step 7 → Step 7.5 → Step 8 → Step A-pre → Step A → Step C.

Step B is a Phase 4 authoring step (not harness).

Completeness check (run at harness exit): every row in this table that wasn't marked `unavailable` should have populated its target field with at least a not-found marker. Empty with no marker = gap; harness must warn.

---

## Version

- Authored: 2026-04-20 alongside `docs/phase_1_harness.py` v0.1.0 and `tests/test_phase_1_harness.py`.
- Canonical source for V2.4 investigation steps: `docs/repo-deep-dive-prompt.md` Steps 1–8 + A/B/C.
