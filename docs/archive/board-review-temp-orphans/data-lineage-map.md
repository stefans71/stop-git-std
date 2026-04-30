# Data Lineage Map — GitHub Repo Security Scanner V2.4

**Purpose:** Traces every data point from source through capture to final report placement. Ground truth for the JSON schema design.

**Source files analyzed:**
- `github-scan-package-V2/repo-deep-dive-prompt.md` (V2.4, ~1500 lines)
- `github-scan-package-V2/SCANNER-OPERATOR-GUIDE.md` (V0.2)
- `docs/GitHub-Scanner-zustand.md` (completed scan — JS/TS library shape)
- `docs/GitHub-Scanner-caveman.md` (completed scan — curl-pipe-from-main shape)

---

## Phase 1: Repository Metadata

### DP-001: HEAD SHA (commit pin)

**Prompt step:** Pre-flight check (line ~65 in prompt)
**Prompt instruction:** "Capture the exact commit SHA you're investigating — record this in the report's version scope"
**Tool/command:** `gh api "repos/$OWNER/$REPO/commits/HEAD" -q '.sha'`
**Raw output format:** 40-character hex string
**Example raw output:** `32013285083648e8d58ba1f76d73b9bdc02fef50` (zustand)
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: H1 hero line, Catalog metadata ("Commit pinned"), Coverage ("Commit pinned"), footer
  - Field name: `head_sha`
**Verifiable by re-running:** YES (at the time of scan; SHA changes with new commits)

### DP-002: Default branch name

**Prompt step:** Pre-flight check (line ~66)
**Prompt instruction:** `DEFAULT_BRANCH=$(gh repo view "$OWNER/$REPO" --json defaultBranchRef -q '.defaultBranchRef.name')`
**Tool/command:** `gh repo view "$OWNER/$REPO" --json defaultBranchRef -q '.defaultBranchRef.name'`
**Raw output format:** String (e.g., "main", "master")
**Example raw output:** `main`
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: H1 hero line ("main @ SHA"), Catalog metadata ("Scanned revision")
  - Field name: `default_branch`
**Verifiable by re-running:** YES

### DP-003: Repo overview metadata

**Prompt step:** Step 1 (line ~100)
**Prompt instruction:** "Repo overview"
**Tool/command:** `gh repo view "$OWNER/$REPO" --json name,description,createdAt,pushedAt,stargazerCount,forkCount,licenseInfo,defaultBranchRef,isArchived,hasIssuesEnabled,isFork,parent`
**Raw output format:** JSON object with multiple fields
**Example raw output:** (zustand) name=zustand, stars=57754, forks=2033, license=MIT, createdAt=2019-04-09, isArchived=false
**Capture method:** VERBATIM (individual fields extracted)
**Where it appears in report:**
  - Section: H1 hero line (stars, license, repo age), Section 05 Repo Vitals (all fields), Catalog metadata (description, language, license)
  - Field names: `repo_name`, `description`, `created_at`, `pushed_at`, `stargazer_count`, `fork_count`, `license`, `is_archived`, `has_issues`, `is_fork`
**Verifiable by re-running:** YES (counts change over time)

### DP-004: Top contributors list

**Prompt step:** Step 1 (line ~103)
**Prompt instruction:** "Top contributors"
**Tool/command:** `gh api "repos/$OWNER/$REPO/contributors?per_page=30" -q '.[] | "\(.login): \(.contributions) commits"'`
**Raw output format:** Newline-separated strings "login: N commits"
**Example raw output:** (zustand) dai-shi: 411, drcmda: 232, dbritto-dev: 59, sukvvon: 50, dependabot[bot]: 18
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 05 Repo Vitals ("Primary maintainer"), Section 02 findings (F0 threat model — contributor context)
  - Field name: `contributors[]` with `.login`, `.contributions`
**Verifiable by re-running:** YES

### DP-005: Maintainer account metadata (per user)

**Prompt step:** Step 1 (line ~106-109)
**Prompt instruction:** "MAINTAINER BACKGROUND CHECK — For the repo owner AND top 3 contributors, pull account metadata"
**Tool/command:** `gh api "users/$USER" -q '{login: .login, created_at: .created_at, public_repos: .public_repos, followers: .followers, bio: .bio}'`
**Raw output format:** JSON object per user
**Example raw output:** (zustand) `{"login":"dai-shi","created_at":"2010-11-21T12:52:33Z","public_repos":127,"followers":8088}`
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 05 Repo Vitals, Section 02 findings (F4/maintainer card), Evidence Appendix (Evidence 7 in zustand)
  - Field name: `maintainers[].login`, `.created_at`, `.public_repos`, `.followers`, `.bio`
**Verifiable by re-running:** YES

### DP-006: Release list

**Prompt step:** Step 1 (line ~113)
**Prompt instruction:** "Releases"
**Tool/command:** `gh release list -R "$OWNER/$REPO" --limit 20`
**Raw output format:** Tab-separated rows: tag, title, date, prerelease flag
**Example raw output:** (zustand) v5.0.12, v5.0.11, v5.0.10, v5.0.9 ... 100+ total
**Capture method:** VERBATIM (list), then SYNTHESIZE (cadence, age of latest)
**If SYNTHESIZE:**
  - Synthesis rule: C20 severity gate uses "release within last 30 days" threshold
  - Synthesis freedom: LOW (30-day window is a hard rule)
  - Repeatability: DETERMINISTIC (date arithmetic)
**Where it appears in report:**
  - Section: Section 05 Repo Vitals ("Releases"), Section 04 Timeline, Section 02 F0 card (release age for C20 severity)
  - Field name: `releases[]` with `.tag`, `.title`, `.date`, `.prerelease`; derived: `latest_release_age_days`, `release_cadence`
**Verifiable by re-running:** YES

### DP-007: Community profile / governance health

**Prompt step:** Step 1 (line ~131)
**Prompt instruction:** "Governance"
**Tool/command:** `gh api "repos/$OWNER/$REPO/community/profile" -q '{health: .health_percentage, coc: (.files.code_of_conduct != null), contrib: (.files.contributing != null), security_policy: (.files.security_policy != null), license: .files.license.spdx_id}'`
**Raw output format:** JSON object with booleans and percentage
**Example raw output:** health=80, coc=false, contrib=true, security_policy=false, license="MIT"
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 05 Repo Vitals ("Security advisories" note about SECURITY.md), Scorecard ("Do they tell you about problems?")
  - Field name: `community_health_pct`, `has_coc`, `has_contributing`, `has_security_policy`, `license_spdx`
**Verifiable by re-running:** YES

### DP-008: Published security advisories

**Prompt step:** Step 1 (line ~202)
**Prompt instruction:** "Published advisories"
**Tool/command:** `gh api "repos/$OWNER/$REPO/security-advisories"`
**Raw output format:** JSON array (empty if none)
**Example raw output:** (zustand) `[]` — 0 advisories; (caveman) `[]` — 0 advisories
**Capture method:** VERBATIM (count + contents if non-empty)
**Where it appears in report:**
  - Section: Section 05 Repo Vitals ("Security advisories"), Section 02 findings (F-advisory in caveman), Scorecard ("Do they tell you about problems?"), Evidence Appendix
  - Field name: `security_advisories[]`, `security_advisory_count`
**Verifiable by re-running:** YES

### DP-009: CI workflow listing

**Prompt step:** Step 1 (line ~206)
**Prompt instruction:** "CI workflow filenames"
**Tool/command:** `gh api "repos/$OWNER/$REPO/actions/workflows" -q '.workflows[] | "\(.name) — \(.path)"'`
**Raw output format:** Newline-separated strings "name -- path"
**Example raw output:** (zustand) 8 workflows: test, publish, preview-release, compressed-size, docs, etc.
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 05 Repo Vitals ("CI workflows"), Section 06 Coverage ("Workflow files read")
  - Field name: `workflows[]` with `.name`, `.path`
**Verifiable by re-running:** YES

---

## Phase 2: Governance & Trust Signals

### DP-010: Branch protection — classic API

**Prompt step:** Step 1 (line ~134)
**Prompt instruction:** "Branch protection — classic API"
**Tool/command:** `gh api "repos/$OWNER/$REPO/branches/$DEFAULT_BRANCH/protection"`
**Raw output format:** JSON object (200) or error JSON (404/403)
**Example raw output:** (zustand) `{"message":"Not Found","status":"404"}` — no classic protection
**Capture method:** VERBATIM (HTTP status code + response body)
**If the response requires interpretation:**
  - 404 = no classic branch protection rule (confirmed absent)
  - 403 = insufficient permissions (unknown, not absent)
  - 200 = protection exists (extract required_pull_request_reviews, required_status_checks, etc.)
**Where it appears in report:**
  - Section: Section 05 Repo Vitals ("Branch protection"), Section 02 findings (F0/C20 card), Section 07 Evidence (priority evidence), Scorecard ("Does anyone check the code?")
  - Field name: `branch_protection.classic.status` (404|403|200), `branch_protection.classic.details` (if 200)
**Verifiable by re-running:** YES

### DP-011: Branch protection — repo rulesets

**Prompt step:** Step 1 (line ~141)
**Prompt instruction:** "Branch protection — rulesets"
**Tool/command:** `gh api "repos/$OWNER/$REPO/rulesets"`
**Raw output format:** JSON array (empty if none)
**Example raw output:** (zustand) `[]`; (caveman) `[]`
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 F0/C20 card, Section 07 Evidence, Section 05 Repo Vitals
  - Field name: `branch_protection.rulesets` (array)
**Verifiable by re-running:** YES

### DP-012: Branch protection — rules on default branch

**Prompt step:** Step 1 (line ~142)
**Prompt instruction:** "rules that apply to the default branch"
**Tool/command:** `gh api "repos/$OWNER/$REPO/rules/branches/$DEFAULT_BRANCH"`
**Raw output format:** JSON array (empty if none)
**Example raw output:** (zustand) `[]` — authoritative (captures repo+org rulesets)
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 F0/C20 card (the authoritative "are rules applied?" check), Section 07 Evidence
  - Field name: `branch_protection.rules_on_default` (array)
**Verifiable by re-running:** YES

### DP-013: Owner type (User vs Organization)

**Prompt step:** Step 1 (line ~144)
**Prompt instruction:** "Also check org-level rulesets when the owner is an org"
**Tool/command:** `gh api "users/$OWNER" -q '.type'`
**Raw output format:** String: "User" or "Organization"
**Example raw output:** (zustand) "Organization" (pmndrs); (caveman) "User"
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Drives whether org rulesets are checked; appears indirectly in F0 card ("Owner is a User account, so no org-level rulesets can apply" in caveman)
  - Field name: `owner_type`
**Verifiable by re-running:** YES

### DP-014: Org-level rulesets (conditional)

**Prompt step:** Step 1 (line ~146)
**Prompt instruction:** "if [ "$OWNER_TYPE" = "Organization" ]; then gh api "orgs/$OWNER/rulesets""
**Tool/command:** `gh api "orgs/$OWNER/rulesets"` (only if org)
**Raw output format:** JSON array
**Example raw output:** (zustand/pmndrs) — would return org rulesets if any exist
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 F0/C20 card (completeness of governance check)
  - Field name: `branch_protection.org_rulesets` (array, nullable if User-owned)
**Verifiable by re-running:** YES

### DP-015: CODEOWNERS file (4-location check)

**Prompt step:** Step 1 (line ~151-158)
**Prompt instruction:** "Check standard locations in order"
**Tool/command:** `gh api "repos/$OWNER/$REPO/contents/$CODEOWNERS_PATH"` for CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS
**Raw output format:** Base64-encoded file content (200) or 404
**Example raw output:** (zustand) 404 on all 4 paths; (caveman) 404 on all 4 paths
**Capture method:** VERBATIM (presence + content if found)
**Where it appears in report:**
  - Section: Section 02 F0/C20 card, Section 05 Repo Vitals, Section 07 Evidence, Scorecard
  - Field name: `codeowners.found` (boolean), `codeowners.path` (string|null), `codeowners.content` (string|null), `codeowners.covers_critical_paths` (boolean)
**Verifiable by re-running:** YES

---

## Phase 3: Dependencies & Vulnerabilities

### DP-016: Dependency manifest filenames

**Prompt step:** Step 3 (line ~317-319)
**Prompt instruction:** "Dependency files at root"
**Tool/command:** `gh api "repos/$OWNER/$REPO/contents/" -q '.[] | select(.name | test("package.json|...")) | .name'`
**Raw output format:** Newline-separated filenames
**Example raw output:** (zustand) package.json, pnpm-lock.yaml, pnpm-workspace.yaml
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Bundle "Runtime dependencies" evidence section, Section 05 Repo Vitals
  - Field name: `dependency_manifests[]`
**Verifiable by re-running:** YES

### DP-017: Dependabot alerts

**Prompt step:** Step 3 (line ~321)
**Prompt instruction:** "Dependabot alerts (requires admin — may 403, record result)"
**Tool/command:** `gh api "repos/$OWNER/$REPO/dependabot/alerts" --paginate -q '.[].security_advisory.summary'`
**Raw output format:** JSON array of advisory summaries, or 403 error JSON
**Example raw output:** (zustand) `{"message":"Dependabot alerts are disabled for this repository.","status":"403"}`; distinguishes disabled vs scope-gap
**Capture method:** VERBATIM (status code + message text is diagnostic)
**If 403, the exact message text matters:**
  - "disabled for this repository" = factual finding (alerts OFF)
  - "not authorized" = scope gap (unknown state)
**Where it appears in report:**
  - Section: Section 02 findings (F1 in zustand), Section 05 Repo Vitals, Section 06 Coverage, Section 07 Evidence
  - Field name: `dependabot.status` (enum: active|disabled|unknown), `dependabot.alerts[]`, `dependabot.error_message`
**Verifiable by re-running:** YES

### DP-018: osv.dev vulnerability query (Dependabot fallback)

**Prompt step:** Step 3 (line ~326-338)
**Prompt instruction:** "fall back to osv.dev (free, zero-auth, zero-install)"
**Tool/command:** `curl -s "https://api.osv.dev/v1/query" -d '{"package":{"name":"$PKG","ecosystem":"npm"}}'`
**Raw output format:** JSON with `vulns` array per package
**Example raw output:** (zustand) Not queried — zero runtime dependencies
**Capture method:** VERBATIM (count per package)
**Where it appears in report:**
  - Section: Section 06 Coverage ("osv.dev: N deps queried, N vulns"), Section 05 Repo Vitals
  - Field name: `osv_dev.queried` (boolean), `osv_dev.packages_queried` (int), `osv_dev.total_vulns` (int), `osv_dev.per_package[]`
**Verifiable by re-running:** YES

### DP-019: Dependency manifest contents (local grep)

**Prompt step:** Step 8a (line ~530-534)
**Prompt instruction:** "Published package declarations"
**Tool/command:** `head -20 "$SCAN_DIR/$F"` for package.json, pyproject.toml, etc. Also `jq '.dependencies' "$SCAN_DIR/package.json"` and similar
**Raw output format:** File content (first 20 lines or extracted dependency section)
**Example raw output:** (zustand) dependencies={} (zero runtime deps), peerDependencies={react, @types/react, immer, use-sync-external-store}, devDependencies=39 entries
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 findings (F2 in zustand — "zero runtime deps"), Section 02A Executable File Inventory, Section 05 Repo Vitals
  - Field name: `dependencies.runtime[]`, `dependencies.dev[]`, `dependencies.peer[]`, `dependencies.runtime_count`, `dependencies.dev_count`
**Verifiable by re-running:** YES

---

## Phase 4: CI/CD & Supply Chain

### DP-020: Workflow file contents (per workflow)

**Prompt step:** Step 2 (line ~218-220)
**Prompt instruction:** "Read each one into the scan dir for later grep"
**Tool/command:** `gh api "repos/$OWNER/$REPO/contents/.github/workflows/$WF" -q '.content' | base64 -d`
**Raw output format:** Full YAML file content per workflow
**Example raw output:** (zustand) 8 workflow files: test.yml, publish.yml, preview-release.yml, etc.
**Capture method:** VERBATIM (stored locally), then SYNTHESIZE (dangerous pattern scan)
**If SYNTHESIZE:**
  - Synthesis rule: Check for `pull_request_target`, `curl | bash`, secret access, shell interpolation of untrusted input
  - Synthesis freedom: LOW (pattern matching)
  - Repeatability: DETERMINISTIC (grep-based)
**Where it appears in report:**
  - Section: Section 02 findings (F4 CI hygiene in zustand, F5 OSSF Token-Permissions), Section 06 Coverage, Section 07 Evidence
  - Field name: `workflows[].content`, `workflows[].has_pull_request_target`, `workflows[].permissions`, `workflows[].uses_oidc`
**Verifiable by re-running:** YES

### DP-021: SHA-pinning audit (per action reference)

**Prompt step:** Step 2 (line ~252-256 — F15 tiered check)
**Prompt instruction:** "Extract every `uses:` directive. Categorize and produce a finding card per tier"
**Tool/command:** `grep -nE 'uses:' "$SCAN_DIR/.github/workflows/"*.yml` (then classify each)
**Raw output format:** List of action references with their pinning status
**Example raw output:** (zustand) 7/8 SHA-pinned, 1 same-org reusable workflow at @v3
**Capture method:** VERBATIM (list of references), then SYNTHESIZE (tier classification)
**If SYNTHESIZE:**
  - Synthesis rule: F15 tier table — OK (40-char SHA), Info (actions/ org @vN), Warning (3rd-party tag), Critical (3rd-party @main/@master)
  - Synthesis freedom: LOW (hard tier table)
  - Repeatability: DETERMINISTIC
**Where it appears in report:**
  - Section: Section 02 findings (F4 in zustand), Section 05 Repo Vitals, Section 06 Coverage ("SHA-pinning coverage")
  - Field name: `actions_pinning.total`, `actions_pinning.sha_pinned`, `actions_pinning.version_tagged`, `actions_pinning.unpinned`, `actions_pinning.details[]`
**Verifiable by re-running:** YES

### DP-022: `pull_request_target` usage

**Prompt step:** Step 2 (line ~229-235 — C11 mandatory)
**Prompt instruction:** "every scan must report `pull_request_target` usage explicitly in Coverage, even when zero hits"
**Tool/command:** `grep -rn 'pull_request_target' "$SCAN_DIR/.github/workflows/"`
**Raw output format:** Match lines or empty
**Example raw output:** (zustand) 0 matches across 8 workflows; (caveman) 0 matches
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage (mandatory — "0 occurrences"), Section 02 findings (F4), Section 07 Evidence (Evidence 9 in zustand)
  - Field name: `pull_request_target_count`, `pull_request_target_workflows[]`
**Verifiable by re-running:** YES

### DP-023: Workflow permissions blocks

**Prompt step:** Step 2 (implicit from F15/OSSF check)
**Prompt instruction:** Derived from workflow file content; OSSF Token-Permissions check correlates
**Tool/command:** `grep -nE 'permissions:|id-token' "$SCAN_DIR/.github/workflows/"*.yml`
**Raw output format:** Match lines
**Example raw output:** (zustand) publish.yml has `permissions: { id-token: write, contents: read }`; 4 of 8 lack explicit permissions
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 findings (F5 in zustand — OSSF Token-Permissions 0/10), Section 07 Evidence (Evidence 5)
  - Field name: `workflows[].has_explicit_permissions`, `workflows[].permissions_block`
**Verifiable by re-running:** YES

---

## Phase 5: Code Patterns

### DP-024: Tarball file count (extraction sanity check)

**Prompt step:** Download section (line ~84-89)
**Prompt instruction:** "SANITY CHECK — verify extraction worked"
**Tool/command:** `find "$SCAN_DIR" -type f | wc -l`
**Raw output format:** Integer
**Example raw output:** (zustand) 143 files; (caveman) 103 files
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage ("Tarball extraction"), Section 05 Repo Vitals ("Repo size")
  - Field name: `tarball_file_count`
**Verifiable by re-running:** YES

### DP-025: Dangerous primitive grep results (Step A — all patterns)

**Prompt step:** Step A (line ~594-665)
**Prompt instruction:** "Grep for dangerous patterns (pattern-only, no full reads)"
**Tool/command:** Multiple `grep -rlP` commands covering eval, exec, child_process, fetch, hardcoded secrets, CORS, SQL injection, auth bypass, path traversal, SSRF, XSS sinks, weak crypto, debug defaults, committed secrets, install hooks, prompt injection
**Raw output format:** Lists of filenames per pattern (or empty)
**Example raw output:** (zustand) All clean except 1 `.exec()` hit in src/middleware/devtools.ts:177 (regex match, not process-exec). Positive control: 22 import statements found.
**Capture method:** VERBATIM (file lists + match counts)
**Where it appears in report:**
  - Section: Section 02 findings (F2 in zustand — clean code-path), Section 02A (note on false positive .exec()), Section 06 Coverage ("Dangerous-primitive grep"), Section 07 Evidence (Evidence 6)
  - Field name: `dangerous_primitives.categories[].pattern`, `.matches[]`, `.match_count`; `dangerous_primitives.positive_control_count`
**Verifiable by re-running:** YES

### DP-026: Targeted read of grep hits (Step B)

**Prompt step:** Step B (line ~669-680)
**Prompt instruction:** "For files that hit dangerous patterns, read ONLY 5 lines of context around each match"
**Tool/command:** `grep -nP 'PATTERN' FILEPATH -A 5 -B 2`
**Raw output format:** Contextual code snippet (matched line + surrounding)
**Example raw output:** (zustand) `src/middleware/devtools.ts:177: const match = callerLineRegex.exec(callerLine)` — confirmed regex match
**Capture method:** VERBATIM (code snippet), then SYNTHESIZE (is this a true positive?)
**If SYNTHESIZE:**
  - Synthesis rule: None explicit — LLM determines if pattern is a true dangerous call vs false positive
  - Synthesis freedom: MEDIUM (guided by pattern context)
  - Repeatability: SHOULD-CONVERGE (most false positives are obvious)
**Where it appears in report:**
  - Section: Section 02A (notes on specific hits), Section 07 Evidence
  - Field name: `dangerous_primitives.drill_ins[].file`, `.line`, `.context`, `.classification` (true_positive|false_positive)
**Verifiable by re-running:** YES

### DP-027: Install-time hooks (package.json lifecycle scripts)

**Prompt step:** Step A (line ~659-661) and Step C
**Prompt instruction:** "Install/lifecycle hooks (package.json)"
**Tool/command:** `grep -P '"(preinstall|install|postinstall|prepare|prepublish|postpublish)"\s*:' package.json`
**Raw output format:** Match lines or empty
**Example raw output:** (zustand) `[]` — zero lifecycle hooks; (caveman) `{ "type": "commonjs" }` — zero deps
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 findings (F2 in zustand — "no install hooks"), Section 02A Layer 1, Section 05 Repo Vitals, Section 07 Evidence (Evidence 4)
  - Field name: `install_hooks[]`, `has_install_hooks` (boolean)
**Verifiable by re-running:** YES

### DP-028: Prompt injection scan results

**Prompt step:** Step A (line ~664) and Step 2.5 content scan
**Prompt instruction:** "Prompt injection targeting AI scanners"
**Tool/command:** `grep -rliP 'ignore (all )?(previous|prior) instructions|disregard.*instructions|you are now|pretend you are|...' .`
**Raw output format:** List of filenames (or empty)
**Example raw output:** (zustand) 0 matches; (caveman) 0 actionable
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage ("Prompt-injection scan: N strings matched, M actionable"), Conditional Section 00 (Scanner Integrity) if M > 0
  - Field name: `prompt_injection.total_matches`, `prompt_injection.actionable_count`, `prompt_injection.hits[]`
**Verifiable by re-running:** YES

### DP-029: README install-paste blocks (Step 7.5)

**Prompt step:** Step 7.5 (line ~473-514)
**Prompt instruction:** "Find install-by-paste invitations in README and related docs"
**Tool/command:** `grep -niE 'paste (this|the (following|snippet|code|block))|copy (this|these) (into|to) (your|the).*system prompt|...' README.md docs/`
**Raw output format:** Match lines or empty
**Example raw output:** (zustand) 0 paste-blocks (single fenced code block is `npm install zustand`); (caveman) 1 paste-block at README line 271 (7 lines of behavioral rules)
**Capture method:** VERBATIM (location + content of paste block)
**Where it appears in report:**
  - Section: Section 02A Executable File Inventory (dedicated card per paste-block), Section 06 Coverage ("README paste-scan")
  - Field name: `paste_blocks[].file`, `.line`, `.invitation_text`, `.block_content`, `.scope_persistence`, `.instruction_verbs[]`, `.secret_requests`, `.obedience_changes`, `.auto_load_behavior`
**Verifiable by re-running:** YES

### DP-030: Executable file inventory (Step C — 7 properties per file)

**Prompt step:** Step C (line ~682-737)
**Prompt instruction:** "For every file in the ALWAYS-SCAN list, document the 7 properties based on grep results"
**Tool/command:** Multiple greps per file: `readFile|read_text|open(`, `writeFile|write_text|open.*w`, network greps, prompt-injection channel analysis, secrets grep, privilege assessment
**Raw output format:** Per-file structured data (7 properties + capability assessment)
**Example raw output:** (caveman) 8 files: install.sh (Warning — live-main fetch), caveman-activate.js (Warning — historical vuln), caveman-mode-tracker.js (Warning), caveman-config.js (OK), uninstall.sh (OK), sync-skill.yml (OK), rules/caveman-activate.md (Info), README paste-block (Info)
**Capture method:** VERBATIM (grep results per property), then SYNTHESIZE (capability assessment paragraph)
**If SYNTHESIZE:**
  - Synthesis rule: "what COULD this code do in the worst case?" — distinct from what it DOES
  - Synthesis freedom: MEDIUM (bounded by grep evidence)
  - Repeatability: SHOULD-CONVERGE
**Where it appears in report:**
  - Section: Section 02A (Layer 1 quick-scan + Layer 2 per-file cards)
  - Field name: `executable_inventory[].path`, `.trigger`, `.reads[]`, `.writes[]`, `.network`, `.injection_channel`, `.secret_leak_path`, `.privilege`, `.capability_assessment`, `.severity` (OK|Info|Warning|Critical)
**Verifiable by re-running:** PARTIAL (greps yes; capability assessment is synthesis)

---

## Phase 6: PR Review Patterns

### DP-031: Total merged PR count

**Prompt step:** Step 4 (line ~348-350)
**Prompt instruction:** "Total merged PR count — use search API for accurate total"
**Tool/command:** `gh api "search/issues?q=repo:$OWNER/$REPO+is:pr+is:merged&per_page=1" --jq '.total_count'`
**Raw output format:** Integer
**Example raw output:** (zustand) ~64 (inferred from sample context); (caveman) 33
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage ("N of N recent merges sampled"), Section 03
  - Field name: `pr_total_merged`
**Verifiable by re-running:** YES

### DP-032: Merged PR list with review data (F11 dual metric)

**Prompt step:** Step 4 (line ~352-353)
**Prompt instruction:** "All merged PRs — include `reviews` array so we can compute the broader review metric"
**Tool/command:** `gh pr list -R "$OWNER/$REPO" --state merged --limit 300 --json number,title,createdAt,mergedAt,author,reviewDecision,reviews,labels`
**Raw output format:** JSON array of PR objects
**Example raw output:** (zustand) 7-PR sample: 2/7 formal review (29%), 6/7 cross-merger (86%), 1/7 self-merge; (caveman) 33 PRs: 5/33 formal (15%), 12/33 any-review (36%)
**Capture method:** VERBATIM (full JSON), then SYNTHESIZE (rate calculations)
**If SYNTHESIZE:**
  - Synthesis rule: F11 dual metric — formal rate = PRs with reviewDecision set; any-review rate = PRs with reviews.length > 0
  - Synthesis freedom: LOW (arithmetic)
  - Repeatability: DETERMINISTIC
**Where it appears in report:**
  - Section: Section 03 (PR table), Section 05 Repo Vitals ("Review rate"), Section 07 Evidence (Evidence 3 in zustand), Scorecard ("Does anyone check the code?")
  - Field name: `pr_review.formal_rate`, `pr_review.any_review_rate`, `pr_review.sample_size`, `pr_review.self_merge_count`, `pr_review.cross_merger_count`, `pr_review.prs[]`
**Verifiable by re-running:** YES (sample contents change as new PRs merge)

### DP-033: Security-relevant PR identification (Step 5 — triple filter)

**Prompt step:** Step 5 (line ~400-439)
**Prompt instruction:** "Gate on title OR path — either signal triggers full inspection" (5a title, 5b path, 5c batch-change)
**Tool/command:**
  - 5a: `gh pr list ... -q '[.[] | select(.title | test("auth|token|secret|..."))]'`
  - 5b: Per-PR `gh pr view $NUM --json files` then grep for critical paths
  - 5c: Per-PR file count check + diff keyword grep for >3-file PRs
**Raw output format:** Union of PR numbers matching any filter
**Example raw output:** (zustand) PR #3395 (security-keyword title hit — "Pin actions/deploy-pages to commit SHA"); (caveman) PRs #70, #71 (security fix), #120, #146, #148, #174
**Capture method:** VERBATIM (PR numbers + filter that matched)
**Where it appears in report:**
  - Section: Section 03 (PR table with "Concern" column), Section 06 Coverage ("suspicious PRs had their diffs actually read")
  - Field name: `security_prs[].number`, `.filter_matched` (title|path|batch), `.title`, `.author`, `.merged_by`, `.reviewed`, `.diff_read` (boolean)
**Verifiable by re-running:** YES

### DP-034: Security PR diff content

**Prompt step:** Step 5 (line ~443-448)
**Prompt instruction:** "For EVERY PR in $SEC_PRS, you MUST pull full details and read the diff"
**Tool/command:** `gh pr view "$NUM" -R "$OWNER/$REPO" --json mergedBy,reviews,commits,files,mergeCommit,createdAt,mergedAt,author,title,reviewDecision` + `gh pr diff "$NUM"`
**Raw output format:** JSON metadata + unified diff text
**Example raw output:** (caveman) PR #70 diff shows O_NOFOLLOW + atomic rename + symlink refusal additions
**Capture method:** VERBATIM (diff content), then SYNTHESIZE (changelog-hiding check, self-merge flag)
**If SYNTHESIZE:**
  - Synthesis rule: "Compare the title-hit set vs the path-hit set. If any PR is in $PATH_HITS but NOT in $TITLE_HITS, its title avoids security keywords despite touching security-critical paths"
  - Synthesis freedom: LOW (set comparison)
  - Repeatability: DETERMINISTIC
**Where it appears in report:**
  - Section: Section 03 (PR table), Section 02 findings (vulnerability-specific cards)
  - Field name: `security_prs[].diff_summary`, `.is_self_merge`, `.is_changelog_hiding`, `.merge_lag_days`
**Verifiable by re-running:** YES

### DP-035: Batch-merge detection

**Prompt step:** Step 5c and implicit from PR mergedAt timestamps
**Prompt instruction:** "Any PR that touches >3 files is potentially a changelog-hiding batch merge"
**Tool/command:** `gh pr list ... --json number,mergedAt` then group by identical mergedAt timestamps
**Raw output format:** Count of PRs sharing identical mergedAt
**Example raw output:** (caveman) 16 PRs with mergedAt = 2026-04-15T12:50:16Z
**Capture method:** VERBATIM (count + PR numbers), then SYNTHESIZE (is this a batch merge?)
**If SYNTHESIZE:**
  - Synthesis rule: Multiple PRs sharing identical mergedAt timestamp = batch merge pattern
  - Synthesis freedom: LOW (timestamp grouping)
  - Repeatability: DETERMINISTIC
**Where it appears in report:**
  - Section: Section 02 findings (F-batch in caveman), Section 04 Timeline, Section 07 Evidence
  - Field name: `batch_merges[].timestamp`, `.pr_count`, `.pr_numbers[]`
**Verifiable by re-running:** YES

---

## Phase 7: Agent Rules

### DP-036: CI-amplified agent rule detection

**Prompt step:** Step 2.5 (line ~263-266)
**Prompt instruction:** "CI-amplified sources — find workflows that copy into agent rule paths"
**Tool/command:**
  - `grep -rlP '\.cursor/rules/|\.windsurf/rules/|\.clinerules/|copilot-instructions|AGENTS\.md|GEMINI\.md' "$SCAN_DIR/.github/workflows/"`
  - `grep -nP '(cp|cat|printf|sed)\s.*(\.cursor/rules/|...)' "$SCAN_DIR/.github/workflows/"*.yml`
**Raw output format:** Match lines or empty
**Example raw output:** (zustand) No matches (no agent-rule CI amplification); (caveman) sync-skill.yml copies rules/caveman-activate.md into 4 agent rule locations
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 findings (F-amplify in caveman), Section 02A (inventory card for amplified rule), Section 06 Coverage
  - Field name: `agent_rules.ci_amplified[].workflow`, `.source_file`, `.destination_files[]`
**Verifiable by re-running:** YES

### DP-037: Static agent-rule files (F7)

**Prompt step:** Step 2.5 (line ~268-277)
**Prompt instruction:** "F7 — Static agent-rule files committed directly"
**Tool/command:** `find "$SCAN_DIR" -path '*/.cursor/rules/*' -o -path '*/.windsurf/rules/*' -o ... -o -name 'CLAUDE.md' -o -name 'AGENTS.md' -o -name 'GEMINI.md'`
**Raw output format:** List of file paths
**Example raw output:** (zustand) None — no agent rule files; (caveman) .cursor/rules/caveman.mdc, .windsurf/rules/caveman.md, .clinerules/caveman.md, .github/copilot-instructions.md
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02A (inventory card per file), Section 06 Coverage ("Agent-rule files"), Section 02 findings (F9 cards)
  - Field name: `agent_rules.static[].path`, `.auto_load_tier` (always|conditional|user_activated|unknown), `.content_scan_results`
**Verifiable by re-running:** YES

### DP-038: Agent-rule file content scan (F9 severity determination)

**Prompt step:** Step 2.5 (line ~296-312)
**Prompt instruction:** "Content scan: read the file with Step B methodology. Search for AI-directed imperative patterns"
**Tool/command:** `grep -nP 'ignore (all )?previous|you are now|system prompt|execute|run (this|the) command|~/.ssh/|~/.aws/' "$SCAN_DIR/path/to/agent-rule-file"`
**Raw output format:** Match lines or empty
**Example raw output:** (caveman) rules/caveman-activate.md — 17 lines of behavioral rules ("Drop articles/filler, write fragments, keep code normal"), no imperative AI-directed language targeting secrets/commands
**Capture method:** VERBATIM (matches), then SYNTHESIZE (F9 severity table classification)
**If SYNTHESIZE:**
  - Synthesis rule: F9 severity table — No imperative=OK, Behavioral only=Info, Persona/obedience change=Warning, Secrets/commands/network=Critical
  - Synthesis freedom: LOW (hard table)
  - Repeatability: SHOULD-CONVERGE
**Where it appears in report:**
  - Section: Section 02A (per-card severity + checklist), Section 02 findings
  - Field name: `agent_rules.files[].severity`, `.imperative_verbs[]`, `.auto_load_tier`, `.capability_statement`, `.risk_statement`
**Verifiable by re-running:** YES

---

## Phase 8: Distribution & Artifacts

### DP-039: README install invitations

**Prompt step:** Step 8a (line ~524-527)
**Prompt instruction:** "README install invitations"
**Tool/command:** `grep -niE 'install|plugin install|npm install|pip install|...' README.md`
**Raw output format:** Match lines with line numbers
**Example raw output:** (zustand) `npm install zustand`, `pnpm add zustand`, `yarn add zustand`; (caveman) `claude plugin install caveman`, `bash <(curl ... install.sh)`
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 findings (distribution channel table — F1/F2), Section 01 (install commands in action steps)
  - Field name: `distribution_channels[].channel_name`, `.install_command`, `.resolves_to`
**Verifiable by re-running:** YES

### DP-040: Install script fetch targets

**Prompt step:** Step 8a (line ~528-529)
**Prompt instruction:** "Install scripts and their fetch targets"
**Tool/command:** `grep -rniP 'curl|wget|Invoke-WebRequest|git clone|gh repo clone' "$SCAN_DIR"/install*.sh "$SCAN_DIR"/hooks/install*.sh`
**Raw output format:** Match lines showing URLs/refs fetched
**Example raw output:** (caveman) `curl -s raw.githubusercontent.com/JuliusBrussee/caveman/main/hooks/*` — fetches from live main
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 findings (F2 — install-script pinning check), Section 02A (install.sh card)
  - Field name: `install_scripts[].fetch_targets[]`, `.pinned` (boolean), `.ref_used` (main|tag|sha)
**Verifiable by re-running:** YES

### DP-041: Install-script pinning check (F2)

**Prompt step:** Step 8c (line ~548-553)
**Prompt instruction:** "For every install.sh / install.ps1 / lifecycle script, inspect the ref used in fetches"
**Tool/command:** `grep -nP 'raw\.githubusercontent\.com|/archive/|/releases/download|github\.com/.*\.git' "$SCAN_DIR"/**/install* | grep -vE '@[a-f0-9]{7,40}|/v[0-9]+\.[0-9]+|/refs/tags/'`
**Raw output format:** Match lines (hits = unpinned fetches)
**Example raw output:** (caveman) hits — fetches from live `main`, not pinned to tag/sha
**Capture method:** VERBATIM (any hit is a Warning finding)
**Where it appears in report:**
  - Section: Section 02 findings (F1+F2 in caveman), distribution channel table
  - Field name: `install_scripts[].pinning_check.unpinned_refs[]`, `.finding_severity` (Warning if unpinned)
**Verifiable by re-running:** YES

### DP-042: Distribution channel verification table

**Prompt step:** Step 8d (line ~555-563)
**Prompt instruction:** "For each channel, record one row in a new Distribution Channel table"
**Tool/command:** Composite of 8a/8b/8c results
**Raw output format:** Per-channel: channel name, resolves to, pinned?, verified vs source?
**Example raw output:** (caveman) claude plugin install → marketplace manifest → main HEAD (No), bash curl → main (No, Warning), git clone → user-pinned (N/A)
**Capture method:** VERBATIM (channel + resolution), then SYNTHESIZE (pinning assessment)
**If SYNTHESIZE:**
  - Synthesis rule: "If any channel is 'Not performed' or 'Not pinned,' the 'Is it safe out of the box?' scorecard cell cannot exceed amber"
  - Synthesis freedom: LOW (hard constraint)
  - Repeatability: DETERMINISTIC
**Where it appears in report:**
  - Section: Section 02 findings (F1+F2), Section 06 Coverage ("Distribution channels"), Scorecard ("Is it safe out of the box?")
  - Field name: `distribution_channels[].verified` (boolean), `.pinned` (boolean), `.channel_type`
**Verifiable by re-running:** PARTIAL (channel resolution is deterministic; marketplace metadata may change)

### DP-043: Release assets / artifact verification

**Prompt step:** Step 8b (line ~536-546)
**Prompt instruction:** "Resolve what users actually install. For each channel..."
**Tool/command:** Various: `npm view PACKAGE dist.shasum`, `gh release download TAG`, plugin manifest inspection
**Raw output format:** Checksums, file lists, manifest contents
**Example raw output:** (zustand) OIDC publish from dist/ on release:published event; (caveman) "marketplace API not accessible"
**Capture method:** VERBATIM (where performed), otherwise "Not performed" with reason
**Where it appears in report:**
  - Section: Section 06 Coverage ("Distribution channels verified: N/M"), Section 02 findings
  - Field name: `artifact_verification[].channel`, `.verified`, `.method`, `.result`
**Verifiable by re-running:** YES (when performed)

---

## Phase 9: External Data Sources

### DP-044: OSSF Scorecard API

**Prompt step:** Step 1 (line ~120-128)
**Prompt instruction:** "OSSF Scorecard (Cap-1) — free API, no auth, 24 pre-computed security checks"
**Tool/command:** `curl -s "https://api.securityscorecards.dev/projects/github.com/$OWNER/$REPO" | python3 -c "..."`
**Raw output format:** JSON with overall score + per-check scores (24 checks, each 0-10)
**Example raw output:** (zustand) overall 5.9/10, 14 checks returned: Branch-Protection -1/10, Code-Review 6/10, Token-Permissions 0/10, ...; (caveman) 404 — not indexed
**Capture method:** VERBATIM (score values)
**Where it appears in report:**
  - Section: Section 05 Repo Vitals ("OSSF Scorecard"), Section 02 findings (corroborating evidence — e.g., F0 "OSSF Branch-Protection: -1/10"), Section 06 Coverage, Section 07 Evidence
  - Field name: `ossf_scorecard.overall_score`, `ossf_scorecard.indexed` (boolean), `ossf_scorecard.checks[]` with `.name`, `.score`, `.reason`
**Verifiable by re-running:** YES (OSSF re-indexes periodically)

### DP-045: osv.dev vulnerability API

**Prompt step:** Step 3 fallback (line ~326-338)
**Prompt instruction:** "fall back to osv.dev"
**Tool/command:** `curl -s "https://api.osv.dev/v1/query" -d '{"package":{"name":"$PKG","ecosystem":"npm"}}'`
**Raw output format:** JSON per package with vulns array
**Example raw output:** (zustand) Not queried (zero runtime deps); (caveman) Not queried (zero runtime deps in hooks)
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage, Section 05 Repo Vitals
  - Field name: `osv_dev` (see DP-018)
**Verifiable by re-running:** YES

### DP-046: gitleaks scan (optional)

**Prompt step:** Step A-pre (line ~566-583)
**Prompt instruction:** "If gitleaks is installed, run it on the extracted source"
**Tool/command:** `gitleaks detect --source "$SCAN_DIR" -v --redact --no-git`
**Raw output format:** Finding lines (redacted) or "no secrets detected"
**Example raw output:** (zustand) "gitleaks: not installed"; (caveman) "gitleaks: not installed"
**Capture method:** VERBATIM (findings or "not available" gap note)
**Where it appears in report:**
  - Section: Section 06 Coverage ("Secrets-in-history"), Section 05 Repo Vitals, Section 02 findings (if secrets found)
  - Field name: `gitleaks.available` (boolean), `gitleaks.findings_count`, `gitleaks.findings[]` (redacted)
**Verifiable by re-running:** YES (when available)

### DP-047: GitHub API rate limit

**Prompt step:** Step 5 rate-limit check (line ~382-396)
**Prompt instruction:** "Rate-limit budget check — GitHub allows 5,000 authenticated requests/hour"
**Tool/command:** `gh api rate_limit --jq '.resources.core.remaining'`
**Raw output format:** Integer
**Example raw output:** (zustand) 5000/5000 remaining; (caveman) 5000/5000 remaining
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage ("API rate budget"), Section 05 Repo Vitals
  - Field name: `api_rate_limit.remaining`, `api_rate_limit.total`, `pr_sample_size` (full|reduced)
**Verifiable by re-running:** YES

---

## Phase 10: Issues and Commits (raw data)

### DP-048: Open issues

**Prompt step:** Step 6 (line ~459)
**Prompt instruction:** "Issues (user-reported problems)"
**Tool/command:** `gh issue list -R "$OWNER/$REPO" --state open --limit 200 --json number,title,createdAt,author,labels,comments`
**Raw output format:** JSON array of issue objects
**Example raw output:** (zustand) 6 open issues
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 05 Repo Vitals (issue count), Scorecard ("Do they fix problems quickly?")
  - Field name: `issues.open_count`, `issues.open[]`, `issues.security_labeled_count`
**Verifiable by re-running:** YES

### DP-049: Closed issues

**Prompt step:** Step 6 (line ~460)
**Prompt instruction:** (continuation of issues step)
**Tool/command:** `gh issue list -R "$OWNER/$REPO" --state closed --limit 200 --json number,title,createdAt,closedAt,author,labels`
**Raw output format:** JSON array
**Example raw output:** Various
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 05 Repo Vitals, Scorecard
  - Field name: `issues.closed_count`, `issues.closed[]`
**Verifiable by re-running:** YES

### DP-050: Recent commit messages

**Prompt step:** Step 7 (line ~468)
**Prompt instruction:** "Recent commits"
**Tool/command:** `gh api "repos/$OWNER/$REPO/commits?per_page=100" -q '.[].commit.message'`
**Raw output format:** Newline-separated commit messages (first 200 lines)
**Example raw output:** Various
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 04 Timeline (selected commits), Section 03 (commit context for PRs)
  - Field name: `recent_commits[].message`, `.sha`, `.author`, `.date`
**Verifiable by re-running:** YES

### DP-051: Monorepo inner-package enumeration (C11)

**Prompt step:** Step 2 (line ~237-250)
**Prompt instruction:** "A monorepo with per-package package.json files has a hidden supply-chain surface"
**Tool/command:** `find "$SCAN_DIR" -name "package.json" -not -path "*/node_modules/*"` + lifecycle script sampling
**Raw output format:** File list + grep results for lifecycle scripts in sampled packages
**Example raw output:** (zustand) pnpm-workspace.yaml lists `packages: [- .]` — not a true monorepo
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage ("Monorepo scope")
  - Field name: `monorepo.is_monorepo` (boolean), `monorepo.inner_package_count`, `monorepo.lifecycle_script_hits[]`
**Verifiable by re-running:** YES

### DP-052: Windows executable files

**Prompt step:** Step C / F16 (line ~697-717)
**Prompt instruction:** "F16 — Windows-specific grep patterns (run when .ps1/.bat/.cmd files exist)"
**Tool/command:** Multiple `grep -rlP` for Invoke-Expression, iex, Invoke-Command, -ExecutionPolicy Bypass, etc.
**Raw output format:** Match lists or empty
**Example raw output:** (zustand) No .ps1/.bat/.cmd files — "no Windows surface"; (caveman) install.ps1, uninstall.ps1 present but not inspected in equal depth
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 06 Coverage ("Windows surface coverage"), Section 02A
  - Field name: `windows_surface.files[]`, `.inspected` (boolean), `.grep_results[]`
**Verifiable by re-running:** YES

### DP-053: `minimumReleaseAge` and other defensive configs

**Prompt step:** Implicit from Step A / local grep during Step 8
**Prompt instruction:** Not a specific step — discovered through Step A or dependency manifest inspection
**Tool/command:** `grep -n 'minimumReleaseAge' "$SCAN_DIR/pnpm-workspace.yaml"` (example)
**Raw output format:** Match line with value
**Example raw output:** (zustand) `minimumReleaseAge: 1440` — 24-hour defensive delay
**Capture method:** VERBATIM
**Where it appears in report:**
  - Section: Section 02 findings (F3 in zustand — positive signal), Section 05 Repo Vitals, Section 07 Evidence (Evidence 8), Section 01 (recommended action)
  - Field name: `defensive_configs[].name`, `.value`, `.file`, `.line`
**Verifiable by re-running:** YES

### DP-054: Vulnerability-specific PR data (Step 5 drill-in)

**Prompt step:** Step 5 (line ~443-448)
**Prompt instruction:** "For EVERY PR in $SEC_PRS, pull full details and read the diff"
**Tool/command:** `gh pr view "$NUM" -R "$OWNER/$REPO" --json mergedBy,reviews,commits,files,mergeCommit,createdAt,mergedAt,author,title,reviewDecision` + `gh pr diff "$NUM"`
**Raw output format:** JSON + unified diff
**Example raw output:** (caveman) PR #70: author=tuanaiseo, mergedBy=JuliusBrussee, reviewDecision=null, reviews=[], commit message describes symlink attack vector
**Capture method:** VERBATIM (metadata + diff excerpt)
**Where it appears in report:**
  - Section: Section 02 findings (vulnerability cards), Section 03 (PR table), Section 04 Timeline, Section 07 Evidence
  - Field name: `vulnerability_prs[].number`, `.author`, `.merged_by`, `.reviewed`, `.review_lag_days`, `.commit_message`, `.fix_description`
**Verifiable by re-running:** YES

---

## Phase 11: LLM Synthesis Data Points

These are NOT tool outputs. They are generated by the LLM from raw data, constrained by prompt rules.

### DP-100: Severity assignment per finding

**Based on raw data:** All evidence from Phases 1-9 relevant to the finding
**Prompt rules constraining it:**
  - C20 severity gate: "Critical when repo ships executable code + has release in last 30 days + all governance signals negative. Warning otherwise."
  - F9 severity table for agent-rule files: "No imperative=OK, Behavioral=Info, Persona/obedience=Warning, Secrets/commands=Critical"
  - F15 tier table for action pinning: OK/Info/Warning/Critical based on action source and ref type
  - General tiered vulnerability table (Tier 1 always critical, Tier 2 warning unless mitigated, Tier 3 info unless compounding)
  - Scorecard consistency re-check: "If any finding is critical, no scorecard cell may be green"
**Synthesis freedom:** LOW for C20/F9/F15 (hard tables). MEDIUM for general vulnerability tiers (context-dependent mitigation).
**Repeatability:** SHOULD-CONVERGE (hard rules make most severity calls deterministic; edge cases near thresholds may vary — e.g., zustand's 31-day-vs-30-day boundary)
**Structured form possibility:** YES — severity is an enum {OK, Info, Warning, Critical} driven by a decision tree of factual inputs. The C20 gate is already a boolean formula: `(classic_404 AND rulesets_empty AND rules_on_default_empty AND no_codeowners) AND (has_recent_release AND ships_executable) => Critical`. This could be fully automated.
**Where it appears:** Every finding card in Section 02, Scorecard cells, Verdict banner

### DP-101: Verdict determination

**Based on raw data:** All finding severities (DP-100), distribution channel verification (DP-042), scorecard consistency check
**Prompt rules constraining it:**
  - Verdict enum: `critical`, `caution`, `clean`
  - Split-verdict rule (F4): "Emit a split verdict whenever a single headline would mean opposite things to two distinct reader groups"
  - Two axes: Version (current vs historical) or Deployment (profile A vs profile B)
  - Scorecard consistency: "If any finding is critical, no scorecard cell may be green"
  - Bundle proposes verdict; Phase 4 transcribes — does not re-derive
**Synthesis freedom:** LOW (verdict is the maximum severity of all findings, constrained by split-axis rules)
**Repeatability:** SHOULD-CONVERGE (determined by finding severities, which are themselves mostly deterministic)
**Structured form possibility:** YES — `verdict = max(finding_severities)`. Split axis is a classification decision with documented criteria. Could be automated with a decision tree.
**Where it appears:** Verdict banner (Section before 01), Catalog metadata, H1 hero

### DP-102: Scorecard cell answers (4 cells)

**Based on raw data:**
  - "Does anyone check the code?" — `pr_review.formal_rate`, `pr_review.any_review_rate`, `branch_protection` status, `codeowners` status
  - "Do they fix problems quickly?" — open security issues, open CVE PR age, commit recency
  - "Do they tell you about problems?" — `has_security_policy`, `security_advisory_count`, F5 status
  - "Is it safe out of the box?" — distribution channel pinning, artifact verification, finding severities
**Prompt rules constraining it (exact calibration table, line ~739-768):**
  - "Does anyone check the code?" — Green: any-review >= 60% AND formal >= 30% AND branch protection. Amber: any-review >= 50% OR formal >= 20%. Red: any-review < 30% OR (solo + any-review < 40%).
  - "Do they fix problems quickly?" — Green: no open security issues AND no CVE PRs >7d. Amber: 1-3 open or CVE PR 3-14d. Red: 4+ open or CVE PR >14d or abandoned.
  - "Do they tell you about problems?" — Green: SECURITY.md + published advisories. Amber: SECURITY.md but no advisories OR unadvertised fixes. Red: no SECURITY.md OR silent fixes.
  - "Is it safe out of the box?" — Green: all channels pinned + artifact verified + no Warning+ findings. Amber: any channel unverified OR group-specific finding. Red: any Critical on default install.
  - Consistency re-check: "If any finding is critical, no scorecard cell may be green"
**Synthesis freedom:** LOW (calibration table is binding — "Calibration wins over editorial judgement for colour")
**Repeatability:** SHOULD-CONVERGE (threshold-based; edge cases near boundaries may produce different labels but same color)
**Structured form possibility:** YES — each cell is a decision tree of factual inputs with enum outputs (red/amber/green + label). Fully automatable.
**Where it appears:** Trust Scorecard section, Verdict banner context

### DP-103: Threat model enumeration (F13)

**Based on raw data:** Finding type, governance signals, distribution channels
**Prompt rules constraining it:**
  - F13: "Any finding involving a 'local attacker' MUST enumerate how the attacker arrives in one sentence"
  - C20 finding card MUST include: "Threat model (F13) enumerating 4+ attacker paths"
  - Required paths to consider: "phishing, stale token, session compromise, malicious IDE/browser extension, sloppy PR merge, etc."
**Synthesis freedom:** MEDIUM (paths are enumerated in prompt but LLM selects which are relevant + adds context)
**Repeatability:** SHOULD-CONVERGE (the path enumeration is template-like; specific framing will vary)
**Structured form possibility:** PARTIAL — the attacker paths are an enum (phishing, stale_token, session_compromise, malicious_extension, sloppy_review, runner_compromise). But the contextual framing ("review-rate sample shows ~71% of merges had no formal reviewDecision") requires LLM.
**Where it appears:** Section 02 finding cards (F0/C20), Section 02A (inventory capability assessments)

### DP-104: "What this means for you" prose

**Based on raw data:** Finding severity, blast radius (stars/forks), distribution method, user context
**Prompt rules constraining it:**
  - Must be present on every Warning+ finding
  - Must be "non-technical" / "as if advising a friend"
  - Must address "the person deciding whether to install"
**Synthesis freedom:** HIGH (prose framing is creative, though content is grounded in facts)
**Repeatability:** WILL-VARY (different LLMs will phrase differently; factual content should converge)
**Structured form possibility:** PARTIAL — could provide a template like "When you install {repo}, you are trusting {trust_surface} because {governance_gap}. The blast radius is {stars} stars." But full prose needs LLM.
**Where it appears:** Section 02 finding cards

### DP-105: "What this does NOT mean" prose

**Based on raw data:** Finding context, positive signals that counterbalance the finding
**Prompt rules constraining it:**
  - Required on every Warning+ finding (V2.4)
  - C20 framing: "Cole's email: 404 does not equal world-writable"
  - Must prevent over-reaction
**Synthesis freedom:** HIGH (editorial framing)
**Repeatability:** WILL-VARY
**Structured form possibility:** LOW — this is inherently editorial prose. Could provide sentence templates but the value is in the specific framing.
**Where it appears:** Section 02 finding cards

### DP-106: Action steps (Section 01)

**Based on raw data:** Findings, governance gaps, distribution channels, user context
**Prompt rules constraining it:**
  - "Action steps must include both a command-line version AND a plain-English version for non-technical users"
  - Must address both "if you install" and "if you maintain" audiences
  - Must be "concretely-instructive" (S8-5 tightening)
**Synthesis freedom:** MEDIUM (command suggestions are constrained by the platform; framing has freedom)
**Repeatability:** SHOULD-CONVERGE (commands are deterministic; framing varies)
**Structured form possibility:** PARTIAL — action type enum (install_normally, pin_version, set_config, nudge_maintainer, upgrade_required, do_not_install) + associated command templates could be structured. Prose needs LLM.
**Where it appears:** Section 01 ("What should I do?")

### DP-107: Split-axis decision

**Based on raw data:** Finding severities, audience differentiation signals
**Prompt rules constraining it:**
  - F4: "Emit a split verdict whenever a single headline would mean opposite things to two distinct reader groups"
  - Two valid axes: Version (current vs historical) or Deployment (profile A vs B)
  - "If both axes apply, pick the axis whose decision is most consequential"
**Synthesis freedom:** LOW (decision criteria are documented; axis selection is constrained)
**Repeatability:** SHOULD-CONVERGE
**Structured form possibility:** YES — `split_axis: null | "version" | "deployment"`, `split_entries: [{scope, audience, verdict, headline, detail}]`
**Where it appears:** Verdict banner, Catalog metadata

### DP-108: Priority evidence selection

**Based on raw data:** All evidence items + their relationship to the verdict
**Prompt rules constraining it:**
  - "Priority evidence is strictly the evidence whose falsification would change the top-line verdict"
  - "Include 2-3 items max"
  - Falsification criterion: "If this claim were false, the verdict would change from X to Y"
**Synthesis freedom:** LOW (falsification criterion is a hard test)
**Repeatability:** SHOULD-CONVERGE (the evidence most likely to change the verdict is usually obvious)
**Structured form possibility:** YES — `priority_evidence: [evidence_id, ...]` where selection criterion is `verdict_would_change_if_false`
**Where it appears:** Section 07 Evidence Appendix (priority group)

### DP-109: Timeline narrative

**Based on raw data:** Release dates, PR dates, issue dates, scan date, vulnerability disclosure dates
**Prompt rules constraining it:**
  - S8-9: Timeline severity labels — 1-3 words naming "the beat of the story"
  - Forbidden labels: SCAN, START, TODAY, NOW, generic CONTEXT
  - Good labels: VULN REPORTED, 5-DAY LAG, FIX SHIPS, NO ADVISORY
  - Colors follow item class (bad/good/neutral)
**Synthesis freedom:** MEDIUM (event selection is constrained; label phrasing has bounded freedom)
**Repeatability:** SHOULD-CONVERGE (key events are factual; label phrasing may vary)
**Structured form possibility:** PARTIAL — `timeline_events[].date`, `.label`, `.severity_class`, `.description`. Label is a short string, constrained by vocabulary.
**Where it appears:** Section 04 Timeline

### DP-110: Exhibit grouping

**Based on raw data:** Finding count, severity distribution
**Prompt rules constraining it:**
  - S8-3: "When a section has 7+ similar-severity items, roll into themed exhibit panels"
  - 3 exhibit themes: vuln (amber), govern (red), signals (green)
  - "Fewer than 3 exhibits is OK. More than 3 means your cut is too fine."
**Synthesis freedom:** LOW (7+ threshold is hard; theme assignment follows severity)
**Repeatability:** SHOULD-CONVERGE
**Structured form possibility:** YES — `exhibits[].theme` (vuln|govern|signals), `.findings[]`
**Where it appears:** Verdict exhibits, Section 02

### DP-111: Finding card prose (body paragraphs)

**Based on raw data:** Evidence for the specific finding
**Prompt rules constraining it:**
  - Must include: severity tag, status (active/resolved/ongoing/mitigated), action hint, threat model, meta table
  - "What this means for you" + "What this does NOT mean" on Warning+
  - "How to fix" with audience-side effort estimate
  - Evidence citations (per S11.1 citation-discipline rule)
**Synthesis freedom:** HIGH (prose composition is creative; constrained by required structural elements)
**Repeatability:** WILL-VARY (structure converges; phrasing varies)
**Structured form possibility:** PARTIAL — structural elements (severity, status, action_hint, meta_table) are fully structured. Prose paragraphs need LLM.
**Where it appears:** Section 02 finding cards

### DP-112: Catalog metadata fields

**Based on raw data:** Repo overview (DP-003), verdict (DP-101), scan date, prompt version
**Prompt rules constraining it:**
  - Required fields: report_file, repo, short_description, category, subcategory, language, license, target_user, verdict, scanned_revision, commit_pinned, scanner_version, scan_date, prior_scan
  - Category: "High-level bucket" from specified list
  - Subcategory: "More specific role within the category"
**Synthesis freedom:** LOW for most fields (factual), MEDIUM for category/subcategory/short_description
**Repeatability:** SHOULD-CONVERGE
**Structured form possibility:** YES — all fields are structured. Category/subcategory are enum-like.
**Where it appears:** Catalog metadata table

### DP-113: Coverage gap enumeration

**Based on raw data:** Which commands succeeded/failed, which tools were available
**Prompt rules constraining it:**
  - Must state which data sources were queried
  - Must state which commands failed and why
  - Must not claim "complete coverage" when sampling occurred
  - Specific mandatory cells: OSSF Scorecard, osv.dev, gitleaks, API budget, etc.
**Synthesis freedom:** LOW (factual reporting of what was/wasn't done)
**Repeatability:** DETERMINISTIC (same inputs => same gaps noted)
**Structured form possibility:** YES — `coverage_cells[].name`, `.status` (ok|blocked|not_available|partial), `.detail`
**Where it appears:** Section 06 Coverage

### DP-114: Solo-maintainer contextualization

**Based on raw data:** Top contributor commit share from DP-004
**Prompt rules constraining it:**
  - F11: "If the repo owner has >80% of commits, include this sentence verbatim..."
  - Exact verbatim sentence provided in prompt for >80% case
**Synthesis freedom:** NONE when >80% (verbatim sentence required). LOW otherwise.
**Repeatability:** DETERMINISTIC (arithmetic threshold + verbatim text)
**Structured form possibility:** YES — `is_solo_maintainer: boolean` (top_contributor_share > 0.80)
**Where it appears:** Scorecard "Does anyone check the code?" cell

### DP-115: Capability assessment per executable file

**Based on raw data:** The 7 properties of each executable file (DP-030)
**Prompt rules constraining it:**
  - "given the grep hits above, what COULD this code do in the worst case?"
  - "Distinct from what it DOES (which requires running it)"
**Synthesis freedom:** MEDIUM (bounded by grep evidence; worst-case framing requires judgment)
**Repeatability:** SHOULD-CONVERGE
**Structured form possibility:** PARTIAL — capabilities could be an enum list (arbitrary_code_exec, file_exfil, network_access, credential_access, prompt_injection_channel, none). But the contextual framing needs LLM.
**Where it appears:** Section 02A per-file cards

### DP-116: F5 silent vs unadvertised classification

**Based on raw data:** Release title/notes text, advisory existence
**Prompt rules constraining it:**
  - F5: "Do NOT use 'silent' if the release title or changelog entry references the fixed attack class"
  - "Unadvertised" = advisory missing but release notes mention the fix
  - "Silent" = release notes omit or mislabel the fix
**Synthesis freedom:** LOW (binary classification based on release note content)
**Repeatability:** SHOULD-CONVERGE
**Structured form possibility:** YES — `disclosure_type: "unadvertised" | "silent" | "properly_disclosed"`
**Where it appears:** Section 02 finding cards (F5 type)

### DP-117: Boundary-case notes

**Based on raw data:** Thresholds and actual values (e.g., 31 days vs 30-day window)
**Prompt rules constraining it:**
  - Must explain when a finding is near a severity threshold
  - "1 day outside the Critical window" (zustand example)
**Synthesis freedom:** LOW (arithmetic comparison + explanation)
**Repeatability:** DETERMINISTIC
**Structured form possibility:** YES — `boundary_cases[].threshold`, `.actual_value`, `.margin`, `.would_change_to`
**Where it appears:** Section 02 finding cards

### DP-118: Section 08 methodology boilerplate

**Based on raw data:** Prompt version, guide version, validator capabilities
**Prompt rules constraining it:**
  - Required subsections: What this scan is, What we checked, External tools used, What this scan cannot detect, Scan methodology version
  - Content is largely templated/boilerplate
**Synthesis freedom:** NONE (boilerplate — exact subsection structure and content specified in prompt)
**Repeatability:** DETERMINISTIC
**Structured form possibility:** YES — fully templated, only variable is version strings
**Where it appears:** Section 08

---

## Cross-cutting: Data Flow Summary

### Raw Data Sources (all VERBATIM capture)

| Source | Data Points | API/Tool |
|--------|------------|----------|
| GitHub REST API (via gh) | DP-001 through DP-015, DP-017, DP-020, DP-031-035, DP-048-050 | `gh api`, `gh repo view`, `gh pr list`, `gh release list`, `gh issue list` |
| Local tarball grep | DP-024-030, DP-036-038, DP-051-053 | `grep -rlP`, `find`, `cat` |
| OSSF Scorecard API | DP-044 | `curl https://api.securityscorecards.dev/...` |
| osv.dev API | DP-018/DP-045 | `curl https://api.osv.dev/v1/query` |
| gitleaks (optional) | DP-046 | `gitleaks detect` |
| GitHub rate limit API | DP-047 | `gh api rate_limit` |

### LLM Synthesis Points (all require LLM)

| Synthesis | Freedom | Automatable? | Data Points |
|-----------|---------|-------------|-------------|
| Severity assignment | LOW | YES (decision tree) | DP-100 |
| Verdict determination | LOW | YES (max severity) | DP-101 |
| Scorecard cells | LOW | YES (calibration table) | DP-102 |
| Threat model | MEDIUM | PARTIAL (path enum + context) | DP-103 |
| "What this means" prose | HIGH | NO (LLM required) | DP-104 |
| "What this does NOT mean" | HIGH | NO (LLM required) | DP-105 |
| Action steps | MEDIUM | PARTIAL (command templates + prose) | DP-106 |
| Split-axis decision | LOW | YES (classification) | DP-107 |
| Priority evidence selection | LOW | YES (falsification test) | DP-108 |
| Timeline narrative | MEDIUM | PARTIAL (events factual, labels creative) | DP-109 |
| Exhibit grouping | LOW | YES (threshold + theme) | DP-110 |
| Finding card prose | HIGH | NO (LLM required) | DP-111 |
| Catalog metadata | LOW | MOSTLY (category/subcategory need LLM) | DP-112 |
| Coverage gaps | LOW | YES (factual) | DP-113 |
| Solo-maintainer flag | NONE | YES (arithmetic) | DP-114 |
| Capability assessment | MEDIUM | PARTIAL (enum + context) | DP-115 |
| Silent vs unadvertised | LOW | YES (binary classification) | DP-116 |
| Boundary-case notes | LOW | YES (arithmetic) | DP-117 |
| Methodology boilerplate | NONE | YES (template) | DP-118 |

### Report Section to Data Point Mapping

| Report Section | Primary Data Points | Synthesis Data Points |
|----------------|--------------------|-----------------------|
| H1 Hero | DP-001, DP-002, DP-003 (stars, license, age) | — |
| Catalog Metadata | DP-001, DP-002, DP-003 | DP-112 (category, subcategory, description) |
| Verdict Banner | — | DP-101 (verdict), DP-107 (split axis), DP-110 (exhibits) |
| Trust Scorecard | DP-010-015, DP-032, DP-007, DP-042 | DP-102 (cell answers) |
| 01 What Should I Do | — | DP-106 (action steps) |
| 02 What We Found | DP-010-015, DP-017-019, DP-021-023, DP-025-028, DP-032-035, DP-036-038, DP-039-043, DP-054 | DP-100 (severity), DP-103 (threat model), DP-104/105 (prose), DP-111 (card body), DP-116 (F5 class), DP-117 (boundary) |
| 02A Executable Inventory | DP-025-027, DP-029-030, DP-036-038 | DP-115 (capability assessment) |
| 03 Suspicious Code Changes | DP-032-035, DP-054 | — (table is factual) |
| 04 Timeline | DP-003 (createdAt), DP-006, DP-054 | DP-109 (narrative + labels) |
| 05 Repo Vitals | DP-003-009, DP-010-015, DP-017-019, DP-032, DP-044, DP-046, DP-047, DP-053 | DP-114 (solo maintainer) |
| 06 Coverage | DP-024, DP-022, DP-028-029, DP-032, DP-042, DP-044-047, DP-051-052 | DP-113 (gap enumeration) |
| 07 Evidence Appendix | All factual DPs cited by findings | DP-108 (priority selection) |
| 08 How This Scan Works | — | DP-118 (boilerplate) |

---

## JSON Schema Design Implications

### Fully Automatable (could be computed from raw data without LLM)

1. **Severity assignment** for C20 (boolean formula), F9 (content pattern table), F15 (tier table)
2. **Verdict** (max severity)
3. **Scorecard cells** (calibration thresholds)
4. **Solo-maintainer flag** (commit share > 80%)
5. **Split-axis classification** (version vs deployment criteria)
6. **Priority evidence selection** (falsification criterion)
7. **Exhibit grouping** (count threshold + severity theme)
8. **Silent vs unadvertised** (release note content check)
9. **Boundary-case detection** (threshold proximity)
10. **Coverage cell status** (command success/failure)
11. **Methodology section** (template)

### Require LLM but could be more structured

1. **Threat model** — path enum with contextual framing
2. **Action steps** — action type enum + command templates + prose wrapper
3. **Timeline** — event selection factual, label/framing creative
4. **Capability assessment** — capability enum + contextual sentence
5. **Catalog metadata** — category/subcategory from controlled vocabulary

### Require LLM, resist structuring

1. **"What this means for you"** — editorial prose grounded in facts
2. **"What this does NOT mean"** — editorial prose preventing over-reaction
3. **Finding card body paragraphs** — narrative synthesis with citations
4. **One-sentence editorial caption** (H1 hero) — creative summary

---

*Generated 2026-04-17. Source: V2.4 prompt + V0.2 Operator Guide + zustand + caveman completed scans.*
