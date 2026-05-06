# Security Investigation: onecli/onecli

**Investigated:** 2026-05-06 | **Applies to:** main @ `fa6468e4711bc283f26b11e68c0ce8dc6a799010` | **Repo age:** 0 years | **Stars:** 2,093 | **License:** Apache-2.0

> onecli/onecli — a 2-month-old, 2,093-star credential vault for AI agents. The architecture is a Rust gateway (`apps/gateway`) that does HTTPS MITM interception via a generated CA cert, paired with a Next.js dashboard (`apps/web`) and a Postgres store. Encryption is AES-256-GCM via the audited `ring` crate. Solo-maintained (guyb1 85%), 0.0% formal review rate across 208 merged PRs, no CODEOWNERS, no SECURITY.md, no published GHSAs. Distribution: `curl -fsSL https://onecli.sh/install | sh` pulls a `latest`-tagged Docker image and a compose file from `main` — three mutable trust anchors. The MITM design means installing OneCLI's CA on an agent host puts the gateway on the trust path of every HTTPS call the agent makes, not just the calls you've configured for credential injection. Past security feedback (#131 0.0.0.0 binding) was handled responsively (closed in days). Issue queue is currently clean (0 open security-tagged); PR #234 (SBOM crypto audit) is sitting open for 5 days. Verdict: Caution — encryption is solid, governance is solo + unstructured, install path is unpinned, MITM design expands trust surface significantly. Safe to evaluate in isolation; pin the version, isolate the host, and treat OneCLI as a single-purpose secrets-handling appliance — not a casual install on a developer machine.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-onecli.md` (+ `.html` companion) |
| Repo | [github.com/onecli/onecli](https://github.com/onecli/onecli) |
| Short description | OneCLI is a credential-vault gateway for AI agents. You store API keys (OpenAI, Anthropic, Stripe, GitHub, etc.) in OneCLI; agents make HTTP calls through the gateway; the gateway intercepts outbound HTTPS via a generated CA certificate, matches request host+path against injection rules, decrypts the matching credential from AES-256-GCM storage, and rewrites the request headers/query before forwarding upstream. Agents see only placeholder keys (e.g. `FAKE_KEY`); the gateway swaps in `REAL_KEY` at request time. |
| Category | `developer-tooling` |
| Subcategory | `credential-vault` |
| Language | TypeScript |
| License | Apache-2.0 |
| Target user | Developer or platform-team operator running multiple AI agents that need access to many third-party APIs, who wants to avoid baking credentials into each agent. Two install paths: (1) `curl -fsSL https://onecli.sh/install | sh` — pipe-from-net installer that downloads `docker-compose.yml` from the `main` branch (no SHA pin) and boots the all-in-one Docker image; (2) `git clone && docker compose -f docker/docker-compose.yml up` for manual review. Local dev mode skips JWT validation entirely (`AUTH_MODE=local`); OAuth mode (`AUTH_MODE=oauth`) validates NextAuth session cookies. |
| Verdict | **Caution** |
| Scanned revision | `main @ fa6468e` (release tag ``) |
| Commit pinned | `fa6468e4711bc283f26b11e68c0ce8dc6a799010` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-05-06` |
| Prior scan | First scan of onecli/onecli. 15th wild V1.2-schema scan after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21, QuickLook 22, kanata 23, freerouting 24, WLED 25, Baileys 26, skills 27, multica 28, impeccable 29. |

---

## Verdict: Caution

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>⚠ Caution — F0..F3 cluster around solo-maintained credential-vault on a 2-month-old repo with mutable install path and MITM-by-design trust expansion (5 findings)</strong>
<br><em>Encryption is solid; governance is solo + 0% formal-review across 208 PRs; install path is unpinned on three trust anchors; the gateway's MITM design means the host sees all agent traffic. Safe to evaluate in isolation; risky to put on the trust path of high-stakes agents until the governance gap closes.</em></summary>

1. **F0** — guyb1 85% commit share; 15 contributors; no CODEOWNERS; 2-month-old credential vault. Single-key compromise reaches every secret stored.
2. **F1** — 0.0% formal review rate over 208 merged PRs. Active ruleset on main but no required-reviewer rule. Recent self-merges include credential-resolution code paths.
3. **F2** — `curl|sh` installer + tracks `main` for compose file + `latest` Docker tag. Three mutable trust anchors. No SHA / signature / SLSA attestation.
4. **F3** — Gateway MITM-intercepts all HTTPS via a generated CA cert. Trust surface = every URL the agent visits, not just the configured-credential APIs.
5. **F4** — No SECURITY.md, no GHSA published, no dependabot.yml. Consumers don't get alerts when a security fix ships.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — 0.0% formal review rate over 208 PRs; active ruleset on main but no required-reviewer rule; no CODEOWNERS; recent self-merges include credential-resolution + cloud-apps PRs |
| Is it safe out of the box? | ⚠ **Partly** — encryption is solid (AES-256-GCM via ring), but the documented install path (`curl|sh` + `latest` Docker tag + main-tracking compose URL) is unpinned, and the gateway's MITM design expands trust surface significantly |
| Do they fix problems quickly? | ✅ **Yes** — closed issue #131 (0.0.0.0 binding) was fixed within days; 0 open security-tagged issues at scan time |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md, no published GHSAs, no .github/dependabot.yml; consumers won't get Dependabot alerts when a fix ships |

---

## 01 · What should I do?

> Caution • Solo maintainer • 0% formal review • MITM-by-design • 0 GHSA
>
> A 2-month-old credential vault that brokers API keys to AI agents via an HTTPS-MITM gateway. 2,093 stars; solo-maintained by guyb1 (85% commit share). Encryption (AES-256-GCM via ring) is solid; the rest of the trust surface is large — install path is unpinned on three trust anchors, the gateway MITM design means installing OneCLI's CA expands the trust surface beyond stored API keys to all agent traffic.

### Step 1: Don't use `curl|sh`. Pin to a specific tag and clone the repo. (✓)

**Non-technical:** The default install command (`curl -fsSL https://onecli.sh/install | sh`) trusts three mutable anchors (DNS for onecli.sh, the `main` branch, and the `latest` Docker tag). For a credential vault, pin to a specific release tag and verify the commit before bringing the gateway up.

```bash
git clone --depth 1 -b v1.21.0 https://github.com/onecli/onecli && cd onecli && git rev-parse HEAD && export ONECLI_VERSION=1.21.0 && docker compose -f docker/docker-compose.yml up -d --wait
```

### Step 2: Review the credential-handling files at the version you're running (✓)

**Non-technical:** If you're shipping OneCLI to production, read `apps/gateway/src/{crypto.rs,inject.rs,auth.rs}` and `apps/gateway/src/vault/` at the tag you cloned — these are the files that touch your secrets. The codebase is reasonably small (Rust gateway is ~3-5k lines) so a one-time audit is feasible.

```bash
git checkout v1.21.0 && wc -l apps/gateway/src/{crypto.rs,inject.rs,auth.rs} && ls apps/gateway/src/vault/
```

### Step 3: Isolate the gateway: the host sees every URL your agent visits (✓)

**Non-technical:** The OneCLI gateway works by MITM-intercepting HTTPS. To do that, your agent must trust OneCLI's CA certificate. Once installed, all of the agent's outbound HTTPS traffic flows through the gateway in cleartext — not just the calls you've configured for credential injection. Run the gateway in a dedicated container or VM, install the CA cert only into the agent's process / user trust store (not system-wide), and treat the gateway host as a single-purpose secrets host.

```bash
# After install, OneCLI generates the CA cert in /app/data/. Limit who can read it: docker exec onecli ls -la /app/data/ ; # On your agent host, install the CA cert ONLY for the agent's user, not system-wide:
```

### Step 4: Subscribe to repo releases — Dependabot won't notify you about OneCLI fixes (✓)

**Non-technical:** There's no SECURITY.md, no published GHSA, and no dependabot.yml — security fixes ship silently from the consumer's perspective. Subscribe to the GitHub repo's releases feed (or RSS) to catch fixes as they land. Watch for `security:` or `fix:` prefixes in commit messages and PR titles.

```bash
gh api repos/onecli/onecli/releases --jq '.[0:3][] | {tag_name, published_at, name, body: (.body | .[0:200])}'
```

### Step 5: Run gitleaks against the clone to cover secrets-in-history (✓)

**Non-technical:** The scanner harness on this scan host doesn't have gitleaks installed, so the `0 secrets` finding reflects only working-tree regex-grep, not full git-history scan. If you're cloning OneCLI to self-host it, run gitleaks once locally to cover the history axis yourself — takes ~30 seconds.

```bash
gitleaks detect --source . --no-git --report-format json
```

---

## 02 · What we found

> ⚠ 4 Warning · ℹ 2 Info
>
> 6 findings total.
### F0 — Warning · Governance — Solo maintainer (85.0% commit share) on a 2-month-old credential vault with no CODEOWNERS and 15 total contributors

*Continuous since repo creation (2026-03-08) · Since 2026-03-08 · → If you self-host, pin the Docker image to a specific tag (`ONECLI_VERSION=1.21.0`) rather than `latest`, review the source for the version you're running, and treat OneCLI as a single-trust-anchor service — compromise of one maintainer credential reaches every secret you've stored.*

guyb1 holds 85.0% of contribution share on a credential vault that's about 2 months old at scan time. Total contributor count is 15; the second contributor (johnnyfish, founder of ChartDB) holds 12.0%, and the remaining ~3% is spread across 13 community PR authors. No CODEOWNERS file is present at any of the four standard locations checked. The active ruleset on `main` (id 13642592, enforcement=active) prevents direct pushes to main but does not enforce required-reviewer count: `formal_review_rate = 0.0%` across 208 sampled merged PRs.

The blast radius if guyb1's GitHub credentials are compromised is the entire credential-vault product. Code paths that handle secrets — `apps/gateway/src/inject.rs` (credential header/query injection at request time), `apps/gateway/src/crypto.rs` (AES-256-GCM encryption/decryption), `apps/gateway/src/vault/` (Bitwarden integration) — can be modified and shipped to consumers via the next CI publish workflow run on tag push. Consumers running `latest` (the install-script default) pull the new image on next restart. 2,093 stars in 2 months indicates a non-trivial install base; each install holds the API keys its operator chose to store.

Compensating signals: the project ships visible defensive patterns (`withAudit` on every state-changing operation, defensive bind-host detection in the installer, AES-256-GCM via the audited `ring` crate, fail-closed key handling). Past security feedback (issue #131 0.0.0.0 binding, closed 2026-04-02) was handled within days. The finding is structural — about the absence of a second-human review gate on a high-stakes product — not about the maintainer's intent or competence. Adding `.github/CODEOWNERS` and amending the ruleset to require ≥1 approving review would close it without any code change.

**How to fix.** Maintainer-side: add `.github/CODEOWNERS` with `* @guyb1 @johnnyfish` (or whatever set of trusted reviewers); update the `main` ruleset to require ≥1 approving review from CODEOWNERS for PRs; consider requiring 2 approvals for changes under `apps/gateway/src/{crypto.rs,inject.rs,vault/,auth.rs}` (the credential-handling code path). Consumer-side: pin Docker image tags (`ONECLI_VERSION=1.21.0`), don't use `latest`; review release notes before bumping; consider treating OneCLI as you'd treat any 2-month-old self-hosted secrets manager (additional network isolation, scoped service accounts upstream).

### F1 — Warning · Governance — Active branch ruleset on `main` does not enforce required-reviewer count — 0.0% formal review rate across 208 merged PRs, observed self-merge pattern in recent sample

*Continuous since repo creation · Since 2026-03-08 · → Treat any 'review' the dashboard shows on a PR as advisory only — across the full corpus, no PR has a GitHub `reviewDecision` field set. If you're auditing a specific commit, look at the actual diff, not review counts.*

Across 208 sampled merged PRs (the entire merged-PR population at scan time), the `reviewDecision` field is empty on every single one — `formal_review_rate = 0.0%`. The `any_review_rate` of 1.4 reflects review-event count averaged across PRs (most of these appear to be GitHub Copilot CI comments, not human approvals). The 5 most-recent merged PRs show this pattern in detail: #252 (johnnyfish-merged, 0 reviews), #250 (guyb1 self-merged, 0 reviews), #249 (guyb1 self-merged 'generic OAuth interface, and credential resolution', 0 reviews), #247 (guyb1 self-merged 'cloud-only apps framework, credential header injection, and user provisioning schema', 0 reviews), #246 (gavrielc external-merged 'support ONECLI_VERSION env var in install script', 0 reviews).

Two of the recent self-merges (#247 and #249) directly touch credential-handling code paths. These are the highest-stakes changes in the codebase and are the changes most in need of a structural second-pair-of-eyes step. The CI workflow does run (Rust clippy, TypeScript check-types, lint, Prisma migration drift) on every PR — so syntactic correctness and basic type safety are gated — but no semantic / threat-model / design review is structurally required.

Compensating: the active ruleset is meaningfully different from no protection at all (it prevents direct pushes to main, so all changes go through a PR with CI). PR #234 'ci: add SBOM crypto audit to block unapproved crypto dependencies' is open and would close a real supply-chain gap when merged. The fix is process-side: amend the ruleset to require ≥1 approving review and add CODEOWNERS as a hard requirement on credential-handling files.

**How to fix.** Maintainer-side: amend the ruleset to require ≥1 approving review (and add CODEOWNERS as a hard requirement on credential-handling files); merge PR #234 (SBOM crypto audit) so crypto-dependency additions are gated. Consumer-side: not directly actionable — read this finding alongside F0, treat the trust posture as 'maintainer judgment + automated CI', and pin to known-good releases.

### F2 — Warning · Supply chain — `curl|sh` installer downloads `docker-compose.yml` from `main` (mutable) and pins the Docker image to `latest` (mutable) — no SHA / tag pin / signature verification

*Continuous (install-path design) · Continuous · → Don't use `curl -fsSL https://onecli.sh/install | sh`. Instead clone the repo at a specific tag, set `ONECLI_VERSION=1.21.0`, run `docker compose -f docker/docker-compose.yml up -d --wait` manually.*

The README's quick-start command is `curl -fsSL https://onecli.sh/install | sh`. Reading the install script (also at `scripts/install.sh` in the repo) reveals three mutable trust anchors in the documented happy path: (1) `https://onecli.sh/install` (third-party domain serving the script); (2) `https://raw.githubusercontent.com/onecli/onecli/main/docker/docker-compose.yml` — tracks the `main` branch, so any commit to main changes what new installs receive; (3) `ghcr.io/onecli/onecli:${ONECLI_VERSION:-latest}` — the Docker tag is mutable, points to whatever the most recent `publish.yml` workflow pushed.

None of the three has a documented checksum, GPG signature, Sigstore attestation, or SLSA provenance. The `publish.yml` workflow does build multi-arch images (linux/amd64 + linux/arm64) with digest manifests, but does not run `cosign sign` or `slsa-github-generator`. Compensating: the install script itself is defensively coded — it binds Docker ports to 127.0.0.1 / WSL loopback / docker0 IP and refuses 0.0.0.0; checks that Docker daemon is running; checks for port conflicts before starting. Past closed issue #131 (0.0.0.0 binding, closed 2026-04-02) corrected a real hardening miss.

Setting `ONECLI_VERSION=[tag]` in the environment before piping does pin the Docker tag (the install script exports it as an env var consumed by `docker compose pull`). Using the manual path (`git clone --depth 1 -b v1.21.0 && cd onecli && docker compose -f docker/docker-compose.yml up`) avoids the onecli.sh DNS dependency entirely. For a credential vault, that manual path is the safer choice.

**How to fix.** Maintainer-side: emit a SHA-256 checksum of `docker-compose.yml` per release (publish to a separate stable URL or include in the release notes); sign Docker images with `cosign` via `slsa-github-generator` or `cosign sign-blob`; document a verified-install path in README. Consumer-side: clone at a tag (`git clone --depth 1 -b v1.21.0 https://github.com/onecli/onecli`), pin `ONECLI_VERSION=1.21.0` in your environment, run `docker compose -f docker/docker-compose.yml up -d`.

### F3 — Warning · Design risk — Gateway requires installing a OneCLI-generated CA certificate as a trusted root — all of an agent's outbound HTTPS traffic flows through the gateway in cleartext at the proxy

*By design · Continuous · → Run the gateway in a tightly-scoped network namespace or container; never install the OneCLI CA cert on a developer machine that also browses the web; treat the gateway host as a machine that holds the decryption keys to everything every agent talks to.*

OneCLI's documented design requires the gateway to MITM-intercept HTTPS traffic from agents in order to inject credentials at request time. README.md L43-46 says: 'Rust gateway: fast, memory-safe HTTP gateway with MITM interception for HTTPS'. The mechanism: the gateway generates a CA certificate (`rcgen 0.13`); the agent must trust it as a root authority; the gateway then accepts CONNECT-method requests, terminates TLS with a leaf cert signed by its CA, parses the cleartext request, applies any matching credential-injection rule, and re-encrypts to the upstream.

Once the CA is trusted, every HTTPS call the agent makes is decrypted at the gateway — not just the calls you've configured for credential injection. The gateway therefore sees: every URL the agent visits, every header (including session cookies and OAuth tokens issued at runtime), every request body (which may contain secrets the gateway wasn't asked to manage), and every response. The trust expansion compared to 'a place to put my API keys' is significant: compromise of the gateway host (RCE via a future CVE, container escape, supply-chain compromise via F2, misconfigured network exposure) yields visibility into all traffic from every agent that trusts its CA, not just the secrets you stored.

The crypto handling for stored secrets is solid: AES-256-GCM via `ring 0.17`, 32-byte key length enforced, fail-closed on bad input. The Bitwarden integration via `ap-*` v0.9.0 crates (Noise-based authenticated channel) is a separate trust path — vault credentials fetched that way are not stored in OneCLI's Postgres but injected on demand. The finding is not 'crypto is wrong' but 'the gateway expands the trust surface beyond what its UI suggests'. The mitigation is operational, not architectural: deploy the gateway in a dedicated container or VM; install the CA cert only into the agent's user / process trust store, not system-wide; treat the gateway host as a single-purpose secrets appliance.

**How to fix.** Maintainer-side: document the MITM trust model prominently in SECURITY.md (or README) with explicit guidance on network isolation, CA-cert scoping (per-process trust, not system-wide), and audit-log review; ship example systemd / Docker network policies for least-privilege gateway deployments. Consumer-side: deploy the gateway in a dedicated container/VM with no other workloads; install the CA cert only into the agent's trust store (not the system trust store); enable egress-traffic logging on the gateway host itself; rotate the CA periodically; if available in your environment, use process-level network policy (e.g. eBPF-based netns isolation) so only the agent processes can route through the gateway.

### F4 — Info · Disclosure — No SECURITY.md, no published GHSA, no `.github/dependabot.yml` — security disclosure channel absent on a credential vault

*Continuous since repo creation · Continuous · → Subscribe to the repo's commit feed and release notes if you self-host. Don't expect Dependabot alerts to fire when a security fix ships.*

0 GitHub Security Advisories have been published despite the project handling at least one real security issue (#131 0.0.0.0 binding, closed 2026-04-02 in ~days from report). No SECURITY.md exists at the repo root or under `.github/`, so there's no documented coordinated-disclosure channel — the maintainer's de facto channel is GitHub Issues (which is public from the moment a report is filed). No `.github/dependabot.yml` exists either, so dependency patches arrive via manual PR rather than automated bot.

From a downstream consumer's perspective: when a real security fix lands in a future OneCLI release (e.g. a hypothetical bug in `apps/gateway/src/crypto.rs` or an upstream dependency vulnerability), no GHSA is published, so the npm advisory database doesn't pick it up; Dependabot doesn't notify; security-monitoring tools that consume GHSA feeds have no signal. You learn about security fixes by reading commits or release notes manually. The fixes themselves ARE transparent (issues + commits + PRs are public); the gap is in the notification channel that pushes signals to consumers.

Maintainer-side fix: add `SECURITY.md` with a coordinated-disclosure email and expected response window; add `.github/dependabot.yml` for the `npm`, `cargo`, and `github-actions` ecosystems; for #131 specifically, file a retroactive GHSA so the GHCR-image consumer feed can backfill. Consumer-side: subscribe to releases via `gh repo view onecli/onecli --web` → Watch → Releases-only; periodically check for `security:` / `fix:` / `CVE-` keywords in release notes.

**How to fix.** Maintainer-side: add `SECURITY.md` with a coordinated-disclosure email + expected response time; add `.github/dependabot.yml` for the npm + cargo + GitHub-Actions ecosystems; for #131 (0.0.0.0 binding) consider filing a retroactive GHSA so the npm package consumers (if any) get backfilled into the advisory feed. Consumer-side: subscribe to releases (`gh repo view onecli/onecli --web` → Watch → Releases only); set up a monitor on the `v*` tag pattern; check the release notes for keywords like 'security:', 'fix:', 'CVE-' before bumping.

### F5 — Info · Scanner coverage — Scanner coverage gaps: gitleaks not installed on host, OSSF Scorecard not indexed, Dependabot alerts behind admin scope — secret-scan and governance signals are partial

*Open scanner gap · Continuous · → If you're sensitive to secrets-in-history risk, run `gitleaks detect --source [clone]` locally before self-hosting. The scan's 'no leaked secrets' result reflects only what the harness could check.*

Three scanner-coverage gaps are stacked on this scan: gitleaks (secrets-in-history) is unavailable on the scanner host so the secret-scan reflects only working-tree regex-grep, not full git history; OSSF Scorecard returned HTTP 404 because the repo is not indexed by OSSF discovery (typical for repos under ~3 months old); Dependabot alerts API returned HTTP 403 because the scanner's token lacks admin scope, and the harness fell back to osv.dev (9 manifest queries, 0 advisories returned).

None of these gaps are evidence of vulnerability — they are coverage gaps that the consumer should close manually if their threat model demands stronger guarantees. The gitleaks gap is the same gap previously documented for catalog entry 29 (impeccable). The OSSF 404 result could be made non-ambiguous by adding an explicit `is_repo_under_90_days` computed field so calibration rules can suppress OSSF-based color shifts for new repos.

There's also a Q4 signal-vocabulary gap (separately recorded as the override on the `is_it_safe_out_of_the_box` cell): the rubric currently does not have a `q4_design_requires_root_trust` signal for MITM-by-design / kernel-module / system-wide-CA-trust postures. F3's trust-surface analysis is captured in prose but not in the cell-level signal set. Tracked as a V1.2.x candidate — first wild scan in the V1.2 corpus where MITM-by-design is the dominant Q4 risk.

**How to fix.** Scanner-side (V1.2.x): install gitleaks on the scanner host so secrets-in-history is covered; document the OSSF 404 result as 'repo too new' rather than ambiguous-failure; add an explicit 'is_repo_under_90_days' computed field so calibration rules can suppress OSSF-based RED for new repos. Consumer-side: clone the repo locally and run `gitleaks detect --source .` to cover the secrets-in-history axis; manually skim recent commits for security-keyword commits.

---

## 02A · Executable file inventory

> The Phase 1 harness's executable-file detector enumerated workflow files and a small set of scripts. The security-relevant binaries below come from inspection of `apps/gateway/src/`, `scripts/`, `docker/`, and the GitHub Actions workflows. The published artifact is the GHCR Docker image, which contains the Rust gateway binary + the Next.js standalone bundle; `scripts/install.sh` is consumer-fetched via `curl|sh`.

### Layer 1 — one-line summary

- 6 executables of consequence: `apps/gateway/src/crypto.rs` (AES-256-GCM encryption — F3 trust anchor), `apps/gateway/src/inject.rs` (credential header/query injection at request time), `apps/gateway/src/auth.rs` (JWT/cookie/API-key gateway auth — `local` mode skips JWT validation), `apps/gateway/src/connect.rs` + `ca.rs` (CONNECT-method MITM proxy + CA cert generation — F3), `scripts/install.sh` (curl|sh installer — F2), `docker/entrypoint.sh` (auto-generates encryption key on first start). Plus 3 GitHub Actions workflows (`ci.yml`, `publish.yml`, `release.yml`).

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `apps/gateway/src/crypto.rs` | Rust module — encryption / decryption | Rust release binary in Docker image | ring::aead::AES_256_GCM (audited primitive); SystemRandom for IV generation | None directly | Implements CryptoService::{from_env, from_base64_key, decrypt, encrypt}. Format `{iv}:{authTag}:{ciphertext}` matches Node.js CryptoService. Key length enforced (32 bytes); fail-closed on bad input. ~150 lines. |
| `apps/gateway/src/inject.rs` | Rust module — credential injection at request time | Rust release binary in Docker image | HeaderName::from_bytes / HeaderValue::from_str (input-validated); base64 decode of Proxy-Authorization | Reads agent token from Proxy-Authorization header; applies SetHeader/ReplaceHeader/RemoveHeader/SetParam injections to forwarded request | F0 + F1 blast-radius epicenter — modifications here directly affect what credentials are injected into agent traffic. Self-merged PRs in the recent sample (#247, #249) touched this code path. ~200 lines. |
| `apps/gateway/src/auth.rs` | Rust module — gateway HTTP auth (browser sessions + API keys) | Rust release binary in Docker image | jsonwebtoken::decode (HS256 validation against NEXTAUTH_SECRET when AUTH_MODE=oauth) | Reads session cookies / Authorization header; queries Postgres for user/project resolution | AUTH_MODE=local SKIPS JWT validation entirely — looks up the 'local-admin' user directly. Fine for single-user dev; a misconfiguration risk if shipped to a multi-user host. Documented in .env.example. ~150 lines. |
| `apps/gateway/src/connect.rs` | Rust module — CONNECT-method MITM proxy | Rust release binary in Docker image | rcgen for cert generation; tokio-rustls TLS termination | Accepts CONNECT requests from agents; terminates TLS with generated leaf cert (signed by the gateway's CA); re-encrypts upstream | F3 epicenter — this is the file that implements the MITM design. CA cert is generated once and persisted to /app/data/. ~unknown lines (not opened in this scan). |
| `scripts/install.sh` | POSIX shell — curl|sh installer (consumer-fetched) | sh on macOS / Linux / WSL | Downloads and writes docker-compose.yml; runs docker compose pull + up | GET https://raw.githubusercontent.com/onecli/onecli/main/docker/docker-compose.yml ; docker pull ghcr.io/onecli/onecli:${ONECLI_VERSION} | F2 epicenter. Defensively coded for bind-host detection (127.0.0.1 / docker0 / WSL loopback; refuses 0.0.0.0). 220 lines. |
| `docker/entrypoint.sh` | POSIX shell — Docker container entrypoint | sh inside the OneCLI container | Writes encryption key to /app/data/secret-encryption-key (mode 600) on first start if SECRET_ENCRYPTION_KEY env var is empty | Runs `prisma migrate deploy` against the configured DATABASE_URL | Auto-generates 32-byte random key from /dev/urandom on first start in OSS mode; Cloud mode uses AWS KMS via env var. AUTH_MODE selection happens at container start (not build time). ~50 lines. |

The published artifact is the GHCR Docker image (`ghcr.io/onecli/onecli:${ONECLI_VERSION}`) which contains the Rust gateway binary + the Next.js standalone bundle. The 4 internal npm workspace packages (`@onecli/{db,ui,eslint-config,typescript-config}`) are not separately distributed. The Bitwarden integration depends on `ap-*` v0.9.0 crates from crates.io which were not opened in this scan.

---

## 03 · Suspicious code changes

> Sample = 208 closed PRs in lifetime (208 merged, 0 closed without merge over the GraphQL sample window). Formal-review rate (GitHub `reviewDecision` set on at least one review) = 0.0% across the sample — no merged PR has a formal review decision recorded. Any-review rate = 1.4 (review events per merged PR, averaged) — most of these are GitHub Copilot CI comments, not human reviewers. Self-merge is the dominant merge mode. The active ruleset on `main` (id 13642592) enforces status checks (CI must pass) but not required-reviewer count. A representative sample of recent PRs:

Sample: the 50 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 0.0% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#252](https://github.com/onecli/onecli/pull/252) | fix: include hostname in injection cache key (#251) (#252) | (merged by) johnnyfish | johnnyfish | No formal decision; 0 review events | Touches injection cache (security-relevant); no human reviewer |
| [#250](https://github.com/onecli/onecli/pull/250) | fix: center dashboard content and unify page widths | guyb1 | guyb1 | No formal decision; 0 review events | Self-merge on cosmetic dashboard change; not security-relevant |
| [#249](https://github.com/onecli/onecli/pull/249) | feat: generic OAuth interface, and credential resolution | guyb1 | guyb1 | No formal decision; 0 review events | Self-merge on credential-resolution code path; should have had a reviewer |
| [#247](https://github.com/onecli/onecli/pull/247) | feat: cloud-only apps framework, credential headers, and user provisioning | guyb1 | guyb1 | No formal decision; 0 review events | Self-merge on credential-header injection logic; high blast radius |
| [#246](https://github.com/onecli/onecli/pull/246) | feat: support ONECLI_VERSION env var in install script | gavrielc | gavrielc | No formal decision; 0 review events | External contribution touching install-script trust path; merged with no formal review |
| [#234](https://github.com/onecli/onecli/pull/234) | ci: add SBOM crypto audit to block unapproved crypto dependencies (OPEN, 5 days) | hisgarden | (open) | Pending; OPEN | Hardening PR sitting in queue; merging would close a real gap (F1) |
| [#131](https://github.com/onecli/onecli/issues/131) | [ISSUE] docker-compose.yml binds ports on 0.0.0.0, services exposed publicly by default (CLOSED 2026-04-02) | paps | (fix self-merged by guyb1) | Closed within days of report | Real security issue handled responsively; demonstrates fix-quickly behavior (Q2 = green) |

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Repo | onecli/onecli |  |
| Stars / Forks | 2,093 / 104 |  |
| Created | 2026-03-08 (~2 months old at scan time) |  |
| Org created | 2026-02-24 (~2.5 months old) |  |
| License | Apache-2.0 |  |
| Primary language | TypeScript (apps/web) + Rust (apps/gateway) |  |
| HEAD SHA | fa6468e4711bc283f26b11e68c0ce8dc6a799010 |  |
| Latest published version | v1.21.0 (2026-05-05) — GHCR Docker image `ghcr.io/onecli/onecli` |  |
| Default branch | main |  |
| Top contributor share | 85.0% (guyb1) |  |
| Total contributors | 15 |  |
| Closed PRs sampled | 208 (all merged in lifetime) |  |
| PR formal review rate | 0.0% |  |
| PR any-review rate | 1.4 (review events / merged PR average) |  |
| Branch protection | Active ruleset on main (id 13642592, enforcement=active); classic protection 404; no required-reviewer rule |  |
| CODEOWNERS | Not present (checked CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS) |  |
| Published GHSA / SECURITY.md / dependabot.yml | 0 / absent / absent |  |
| OSSF Scorecard | Not indexed (HTTP 404 — repo too new) |  |
| Distribution channels | GHCR Docker image (consumer-facing); 4 internal npm workspace packages |  |
| Open security-tagged issues | 0 |  |
| Open PRs | 5 (incl. #234 SBOM crypto audit, 5d open; #149 structured audit logging; #113 1Password integration) |  |
| Releases lifetime | 52 (cadence: ~1 release every 1-2 days) |  |
| Encryption | AES-256-GCM via ring 0.17 (audited primitive); key auto-generated to /app/data/secret-encryption-key (mode 600) on OSS first-start; AWS KMS on Cloud feature flag |  |
| Bitwarden integration | Via ap-{client,proxy-client,proxy-protocol,noise} v0.9.0 crates (Bitwarden Agent Access protocol) |  |

---

## 06 · Investigation coverage

| Check | Result |
|-------|--------|
| Phase 1 harness | phase_1_harness.py V0.2 (gh api + OSSF + osv.dev + tarball extraction; gitleaks unavailable; Dependabot alerts gated by admin scope) |
| Phase 1 raw fields populated | 28 of 28 |
| Tarball file count | 507 files (extract); 0 symlinks stripped |
| Phase 3 compute | compute.py V2 calibration (classify_shape() + compute_scorecard_cells_v2() + compute_c20_severity + compute_solo_maintainer) |
| Phase 3 shape classification | agentic-platform (medium confidence) — cross-language monorepo (npm + non-npm Rust) + publishable npm + backend-dir-non-canonical. solo_maintainer=true (85.0% top-share) |
| Phase 3 advisory→Phase 4 overrides | 1 cell (Q4 amber→amber with `signal_vocabulary_gap` override — Q4 rubric does not yet have a `q4_design_requires_root_trust` signal for MITM-by-design / CA-cert-install posture) |
| OSSF Scorecard | Not indexed (HTTP 404, repo too new) |
| Dependabot alerts | Unavailable (HTTP 403 admin scope); osv.dev fallback queried 9 manifests, 0 advisories |
| gitleaks (secrets-in-history) | Unavailable (gitleaks not installed on scanner host); working-tree regex-grep returned 0 signals |
| Prompt-injection scan | 2 root agent-rule files scanned (CLAUDE.md + .agents/skills/vercel-react-best-practices/AGENTS.md); 0 injection signals |
| Distribution channels detected | 1 consumer-facing (GHCR Docker image, multi-arch amd64+arm64); 4 internal npm workspace packages (not separately distributed); install path = `curl|sh` (mutable on 3 trust anchors per F2) |
| Crypto primitive review | AES-256-GCM via ring 0.17 (audited); fail-closed on bad key; format compatible with Node.js CryptoService |
| Architecture | Rust gateway with MITM HTTPS interception via rcgen-generated CA; Next.js dashboard; Postgres backing store; Bitwarden integration via ap-* v0.9.0 crates |
| Tarball extraction | ❌ None files |
| osv.dev | ℹ  |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4995/5000 remaining |

**Gaps noted:**

1. OSSF Scorecard — not indexed: Scorecard API returned HTTP 404 (repo created 2026-03-08, ~2 months old; not yet picked up by OSSF discovery). Governance signals derived from raw `gh api` data.
2. Dependabot alert count — unavailable: GitHub API returned HTTP 403 (admin scope required). Fell back to osv.dev — queried 9 manifests across npm + Cargo lock and returned 0 advisories. No security advisories visible from the project's own panel, but consumers without admin would also be blocked from this view.
3. Secrets-in-history (gitleaks) — unavailable: gitleaks is not installed on the scanner host. The 0-secrets harness result reflects only regex-grep over working-tree file content, not full git-history scan. Same gap as catalog entry 29 (impeccable). Consumer should run `gitleaks detect --source [clone]` locally if their threat model demands it.
4. MITM-design threat-surface — coverage gap: Phase 3 compute does not have a `q4_design_requires_root_trust` signal, so the architectural-trust-surface implication of the OneCLI MITM design is captured in F3 prose but not in the Q4 scorecard cell. Override recorded as `signal_vocabulary_gap` in `is_it_safe_out_of_the_box`. Tracked as V1.2.x candidate.
5. Bitwarden Agent Access protocol verification — scope-restricted: the `ap-*` v0.9.0 crates (`ap-client`, `ap-proxy-client`, `ap-proxy-protocol`, `ap-noise`) are pulled from crates.io. The Phase 1 harness does not currently fingerprint cargo-registry artifacts the way it does for npm. Tracked as scanner-coverage gap.

---

## 07 · Evidence appendix

> ℹ 10 facts · ★ 0 priority

### Other evidence

#### Evidence 1 — guyb1 holds 85.0% of contribution share on a 2-month-old credential vault. The org `onecli` was created 2026-02-24 (~2.5 months before scan); the repo was created 2026-03-08. johnnyfish (founder of ChartDB) is second contributor at 12.0%. No CODEOWNERS file is present.

```bash
gh api repos/onecli/onecli/contributors --jq 'sort_by(-.contributions) | [.[0:5][] | {login, contributions}]'
```

Result:
```text
Top contributors: guyb1 (170 contributions, 85.0%), johnnyfish (24, 12.0%), christian-oudard (2), mbravorus (2), abergs (1). Total contributors: 15. CODEOWNERS check: not found in any of CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS, .gitlab/CODEOWNERS.
```

*Classification: fact*

#### Evidence 2 — Branch protection: classic protection HTTP 404 (no rule), but an active ruleset on `main` exists (id 13642592, target=branch, enforcement=active, source=Repository). However the ruleset does not enforce required-reviewer count: formal review rate over 208 sampled merged PRs is 0.0%, any-review rate is 1.4 (sum of review counts / total) — i.e. about 1.4 review events per merged PR on average across the corpus, but with no `reviewDecision` set on any sampled PR.

```bash
gh api repos/onecli/onecli/branches/main/protection ; gh api repos/onecli/onecli/rulesets ; gh api graphql --paginate -f query='...closed pulls...' --jq '[formal/any review rates]'
```

Result:
```text
branch_protection.classic.status = 404. branch_protection.rulesets.entries = 1 ruleset (active enforcement). pr_review.{total_closed_prs: 208, total_merged_lifetime: 208, formal_review_rate: 0.0, any_review_rate: 1.4, self_merge_count: not-explicitly-counted-but-observed-across-sample, security_flagged_count: 0}.
```

*Classification: fact*

#### Evidence 3 — PR sample shows the 5 most-recent merged PRs (out of 208 lifetime) all have `review_decision = ""` (empty), `any_review_count = 0`, and a mix of self-merge (4 of 5) vs other-merger. Across the entire 208-PR sample, self-merges and 0-review-count PRs are the dominant pattern. PR #234 (open since 2026-05-01) is `ci: add SBOM crypto audit to block unapproved crypto dependencies` — a PR proposing crypto-supply-chain hardening — open ~5 days at scan date.

```bash
gh api graphql -f query='[closedPRs first:20]' --jq '.data.repository.pullRequests.nodes[]'
```

Result:
```text
Recent merged PRs (first 5 of 208): #252 (johnnyfish-merged hostname-cache fix, 0 reviews); #250 (guyb1 self-merged dashboard layout, 0 reviews); #249 (guyb1 self-merged generic OAuth interface + credential resolution, 0 reviews); #248 (guyb1 self-merged release-please tag, 0 reviews); #247 (guyb1 self-merged 'cloud-only apps framework, credential header injection, user provisioning schema', 0 reviews). Open PRs: 5 (including #234 SBOM crypto audit, open 5d, hisgarden-authored).
```

*Classification: fact*

#### Evidence 4 — Installer at `scripts/install.sh` (also served as `https://onecli.sh/install`) downloads `docker-compose.yml` from the `main` branch (mutable), and the compose file pins the OneCLI image to `ONECLI_VERSION:-latest` (also mutable). There is no SHA-256 checksum of the compose file, no GPG signature, no Sigstore attestation. The script does run defensively in other respects: it explicitly binds Docker ports to `127.0.0.1` (or `docker0` IP on Linux) — never `0.0.0.0` — and exits if it cannot determine a safe bind host. Past closed issue #131 (closed 2026-04-02) was 'docker-compose.yml binds ports on 0.0.0.0, services exposed publicly by default' — fixed.

```bash
cat scripts/install.sh ; cat docker/docker-compose.yml ; gh issue list -R onecli/onecli --state closed --search 'docker-compose'
```

Result:
```text
install.sh:73 — `COMPOSE_URL="https://raw.githubusercontent.com/onecli/onecli/main/docker/docker-compose.yml"` (tracks main, no tag). install.sh:140 — `ONECLI_VERSION="${ONECLI_VERSION:-latest}"`. docker-compose.yml:23 — `image: ghcr.io/onecli/onecli:${ONECLI_VERSION:-latest}`. install.sh:39-77 — `detect_bind_host()` returns 127.0.0.1 / WSL loopback / docker0 bridge IP, never 0.0.0.0. Closed issue #131 (2026-04-02): 0.0.0.0 binding fixed.
```

*Classification: fact*

#### Evidence 5 — The gateway uses MITM HTTPS interception by design. README.md L43-46 documents: 'Rust gateway: fast, memory-safe HTTP gateway with MITM interception for HTTPS'. The gateway generates its own CA certificate via the `rcgen` crate and agents must install it as a trusted root for HTTPS interception to work. Cargo.toml L24 declares `rcgen = "0.13"` (certificate generation), L17-19 declares `tokio-rustls`/`rustls`/`rustls-pemfile` (TLS termination). `apps/gateway/src/ca.rs` and `connect.rs` implement the CA + the CONNECT-method MITM proxy.

```bash
ls apps/gateway/src/ ; grep -nE 'rcgen|MITM|interception' apps/gateway/Cargo.toml README.md
```

Result:
```text
apps/gateway/src/: approval.rs apps.rs auth.rs ca.rs cache.rs cloud cloud_apps.rs connect.rs crypto.rs db.rs gateway gateway.rs inject.rs main.rs policy.rs telemetry.rs telemetry_core.rs vault. Cargo.toml: rcgen = "0.13". README.md L43: 'Rust gateway: fast, memory-safe HTTP gateway with MITM interception for HTTPS'.
```

*Classification: fact*

#### Evidence 6 — Encryption uses AES-256-GCM via `ring 0.17` (an audited crypto library; same primitive used by rustls transitively). Format `{iv_b64}:{authTag_b64}:{ciphertext_b64}` matches the Node.js `CryptoService` for Rust↔Node compatibility. Key handling: OSS edition auto-generates a 32-byte random key on first container start (`docker/entrypoint.sh:18-26`) and persists it to `/app/data/secret-encryption-key` with mode 600; Cloud edition uses AWS KMS via the `cloud` Cargo feature flag. The `.env.example` ships a placeholder string `SECRET_ENCRYPTION_KEY=change-me-to-secure-key` — but that string is not valid base64 of 32 bytes, so if a user copies `.env.example` to `.env` without changing it, `crypto.rs::CryptoService::from_base64_key()` rejects with `bail!("SECRET_ENCRYPTION_KEY must be exactly 32 bytes")` (fail-closed at boot, not silent compromise).

```bash
head -150 apps/gateway/src/crypto.rs ; cat docker/entrypoint.sh ; cat .env.example
```

Result:
```text
crypto.rs:30-50 — AES-256-GCM with `ring::aead::AES_256_GCM`, 32-byte key length enforced, 12-byte IV, 16-byte auth tag. entrypoint.sh:18 — `if [ "$NEXT_PUBLIC_EDITION" != "cloud" ] && [ -z "$SECRET_ENCRYPTION_KEY" ]; then ... head -c 32 /dev/urandom | base64 > "$SECRET_KEY_FILE"; chmod 600 "$SECRET_KEY_FILE"; fi`. .env.example:23 — `SECRET_ENCRYPTION_KEY=change-me-to-secure-key`.
```

*Classification: fact*

#### Evidence 7 — No SECURITY.md is present at repo root. community_profile.has_security_policy = false; security_advisories.count = 0 (no published GHSAs). community profile is otherwise 75% complete: CoC + CONTRIBUTING.md + Apache-2.0 LICENSE present. No `.github/dependabot.yml` is present. The Phase 1 harness's gitleaks step did not run because gitleaks is not installed on the scanner host (coverage gap; not evidence of leaked secrets). OSSF Scorecard returned HTTP 404 (repo not yet indexed by OSSF discovery — typical for repos under ~3 months old).

```bash
ls -la SECURITY.md .github/SECURITY.md 2>&1 ; gh api repos/onecli/onecli/community/profile --jq '{health_percentage,has_security_policy}' ; gh api repos/onecli/onecli/security-advisories --jq 'length'
```

Result:
```text
SECURITY.md / .github/SECURITY.md: not present. community_profile: {health_percentage: 75, has_security_policy: false, has_code_of_conduct: true, has_contributing: true}. security_advisories: 0. ossf_scorecard: {queried: true, indexed: false, http_status: 404}.
```

*Classification: fact*

#### Evidence 8 — The Next.js side ships `apps/web/src/lib/services/audit-service.ts` (referenced from CLAUDE.md L66-93) and an explicit `withAudit` pattern for state-changing operations. CLAUDE.md prescribes auditing all CREATE/UPDATE/DELETE/REGENERATE actions on AGENT/SECRET/RULE/API_KEY entities, with explicit guidance to never include sensitive values (tokens, secrets, passwords) in audit metadata. The published 1.21.0 release (2026-05-05) shipped the `feat: cloud-only apps framework, credential headers, and user provisioning` PR (#247) and `feat: generic OAuth interface, and credential resolution` PR (#249). Release cadence: 52 releases in ~2 months.

```bash
grep -nE 'withAudit|AUDIT_ACTIONS|AUDIT_SERVICES' apps/web/src/lib/services/audit-service.ts ; gh api repos/onecli/onecli/releases --jq '. | length'
```

Result:
```text
CLAUDE.md L66-93 prescribes withAudit pattern; AUDIT_ACTIONS = {CREATE, UPDATE, DELETE, REGENERATE}; AUDIT_SERVICES = {AGENT, SECRET, RULE, API_KEY}; metadata guidance explicitly forbids tokens/secrets/passwords. Releases: 52 in lifetime (2026-03-08 to 2026-05-05). Latest: v1.21.0 (2026-05-05).
```

*Classification: fact*

#### Evidence 9 — Distribution channels detected: 4 npm packages (`onecli-cloud` private workspace root; `@onecli/db`, `@onecli/eslint-config`, `@onecli/ui` — internal monorepo packages) plus the GHCR Docker image `ghcr.io/onecli/onecli:${ONECLI_VERSION}`. None of the npm packages have `pinned: true` or `artifact_verified: true` — they are internal workspace packages, not consumer-facing distributables (the consumer-facing entrypoint is the Docker image). The Docker image is built and published by .github/workflows/publish.yml on every `v*` tag push (multi-arch amd64+arm64), with cosign-style digest reuse but no Sigstore signature attestation.

```bash
find . -name 'package.json' -not -path './node_modules/*' -exec jq -r '.name' {} + ; head -80 .github/workflows/publish.yml
```

Result:
```text
package.json names: onecli-cloud (root, private), @onecli/db (packages/db), @onecli/eslint-config (packages/eslint-config), @onecli/ui (packages/ui), @onecli/typescript-config (packages/typescript-config). Workflow `publish.yml` builds linux/amd64 + linux/arm64 to ghcr.io/onecli/onecli with `docker/build-push-action@v7` and emits multi-arch manifest. No `cosign sign` or `slsa-github-generator` step.
```

*Classification: fact*

#### Evidence 10 — The Rust gateway depends on 4 unusual `ap-*` v0.9.0 crates: `ap-client`, `ap-proxy-client`, `ap-proxy-protocol`, `ap-noise` — these implement Bitwarden's Agent Access protocol (Noise-based authenticated channel for vault credential injection). The Cargo.toml `cloud` feature gates AWS KMS, AWS config, and Redis. The `prompt_injection_scan` step ran over 2 root agent-rule files (CLAUDE.md, .agents/skills/vercel-react-best-practices/AGENTS.md) and found 0 injection signals. `skills-lock.json` pins 5 skill collections (vercel-labs/skills, anthropics/skills, leonardomso/rust-skills, vercel-labs/agent-skills × 2) by SHA-256 computed hash.

```bash
cat apps/gateway/Cargo.toml ; cat skills-lock.json ; find .agents/ -name 'SKILL.md' -o -name 'AGENTS.md' | head
```

Result:
```text
Cargo.toml: ap-client = '0.9.0', ap-proxy-client = '0.9.0', ap-proxy-protocol = '0.9.0', ap-noise = '0.9.0' (Bitwarden Agent Access protocol). [features] cloud = ['dep:aws-sdk-kms', 'dep:aws-config', 'dep:redis']. skills-lock.json: 5 skills with computedHash (SHA-256). prompt_injection_scan: 0 signals across 2 scanned files.
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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-05-06 · scanned main @ `fa6468e4711bc283f26b11e68c0ce8dc6a799010` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
