# Security Investigation: shiyu-coder/Kronos

**Investigated:** 2026-04-20 | **Applies to:** main @ `67b630e67f6a18c9e9be918d9b4337c960db1e9a` | **Repo age:** 0 years | **Stars:** 19,724 | **License:** MIT

> Kronos is a legitimate AAAI-2026 research artifact for financial candlestick forecasting, 19.7k stars, MIT, Python. The science is real; the operational posture is not. A pickle RCE on the finetune data path (issue #216) has sat unfixed 95 days with its fix PR unreviewed 7 days. The dep graph carries 48 known CVEs. Zero releases — every install tracks master — with no branch protection and 0% formal PR review. Inference-only users (HF weights via KronosPredictor) avoid the pickle path; finetune users do not — the Deployment split reflects that gap.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-Kronos.md` (+ `.html` companion) |
| Repo | [github.com/shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos) |
| Short description | Python decoder-only foundation model for financial K-line data; Flask webui; model weights on Hugging Face; ships from master (no releases). |
| Category | `ml-foundation-model` |
| Subcategory | `financial-time-series` |
| Language | Python |
| License | MIT |
| Target user | Quant researcher or finetuning user who wants to predict candlestick sequences. Install is `git clone + pip install -r requirements.txt`; models load from `NeoQuasar/Kronos-*` on HF. |
| Verdict | **Critical** (split — see below) |
| Scanned revision | `main @ 67b630e` (release tag `untagged`) |
| Commit pinned | `67b630e67f6a18c9e9be918d9b4337c960db1e9a` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of Kronos. Second wild V1.2-schema scan (after markitdown entry 15 and ghostty entry 16). |

---

## Verdict: Critical (split — Deployment axis only)

### Deployment ·  — **Critical — **

### Deployment ·  — **Critical — **

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>✗ Critical — F0 + F1 are the blocking items for anyone finetuning Kronos (2 findings)</strong>
<br><em>Unfixed RCE on finetune path + 48-CVE dependency graph.</em></summary>

1. **F0** — pickle.load on untrusted training data — disclosed 95 days, fix PR sitting 7 days.
2. **F1** — 48 CVEs in runtime deps; numpy/pandas unpinned, torch >=2.0.0.

</details>

<details>
<summary><strong>⚠ Warning — F2 + F3 + F4 describe the governance posture (3 findings)</strong>
<br><em>Solo-maintainer + no branch protection + no releases + no disclosure policy.</em></summary>

1. **F2** — 0% formal PR review, no branch protection, no CODEOWNERS.
2. **F3** — Zero releases; installs resolve to master HEAD.
3. **F4** — No SECURITY.md, 0 published advisories despite known RCE.

</details>

<details>
<summary><strong>ℹ Info — F5 is hygiene, non-blocking (1 findings)</strong>
<br><em>No dependabot, no CODEOWNERS, only a Copilot PR reviewer workflow.</em></summary>

1. **F5** — Minimal operational tooling — single-maintainer capacity signature.

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — 0% formal review, no branch protection, no CODEOWNERS |
| Is it safe out of the box? | ❌ **No** — install from master + unpinned deps + disclosed RCE on finetune path |
| Do they fix problems quickly? | ❌ **No** — 95-day-old RCE issue #216 unfixed, fix PR #249 sitting 7 days unreviewed |
| Do they tell you about problems? | ❌ **No** — no SECURITY.md, 0 advisories published despite open RCE issue #216 |

---

## 01 · What should I do?

> 19.7k⭐ · MIT · Python · 2 critical · 3 warning · 1 info · CRITICAL (split)
>
> Kronos is a 19.7k-star Python foundation model for financial candlestick forecasting, backed by AAAI-accepted research and Hugging Face weight distribution. The research artifact is legitimate; the operational posture is not. An unfixed 95-day-old pickle RCE on the finetuning path, a dependency graph with 48 CVEs, zero formal releases, no branch protection, and 0% formal PR review together make this Critical on the Deployment axis.

### Step 1: Before installing: review issue #216 and PR #249 (⚠)

**Non-technical:** Kronos has a known, unfixed code-execution risk on the finetuning path. Read the issue and proposed fix before deciding whether this affects your workflow.

```bash
gh api repos/shiyu-coder/Kronos/issues/216; gh api repos/shiyu-coder/Kronos/pulls/249
```

### Step 2: Pin to a specific reviewed commit SHA, not HEAD (⚠)

**Non-technical:** Kronos has no releases. Cloning master means installing whatever landed today. Pick a commit you're comfortable with and pin to it.

```bash
git clone https://github.com/shiyu-coder/Kronos && cd Kronos && git checkout 67b630e67f6a18c9e9be918d9b4337c960db1e9a
```

### Step 3: Install in a fresh virtualenv + audit dependency graph (⚠)

**Non-technical:** The dependency graph has 48 known CVEs. Install into an isolated venv and audit with pip-audit before importing.

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install pip-audit && pip-audit
```

### Step 4: If finetuning: apply PR #249 locally before running finetune/* code (🚨)

**Non-technical:** The pickle.load RCE is on the finetuning path. If you plan to run any finetune/*.py scripts, patch finetune/dataset.py with the restricted-unpickler change from PR #249 BEFORE invoking it on any .pkl file you did not generate yourself.

```bash
gh pr diff 249 --repo shiyu-coder/Kronos | git apply
```

### Step 5: Inference-only users: verify model downloads from HuggingFace integrity (ℹ)

**Non-technical:** If you are only running inference (loading a model from HuggingFace via KronosPredictor), the pickle RCE does not apply to you. Still — verify the HF model hashes match the NeoQuasar/* repo state before trusting them.

```bash
huggingface-cli download NeoQuasar/Kronos-base --local-dir ./Kronos-base && ls -la ./Kronos-base
```

---

## 02 · What we found

> 🚨 2 Critical · ⚠ 3 Warning · ℹ 1 Info
>
> 6 findings total.
### F0 — Critical · Vulnerability — Unsafe pickle.load on training data — disclosed RCE unfixed for 95 days

*Continuous (95 days) · Disclosed 2026-01-15; fix unmerged as of scan · → Finetune users: do NOT run finetune/* with untrusted .pkl files. Apply PR #249 patch locally or wait for merge.*

Issue #216 was opened on 2026-01-15 by an external reporter who noticed that `QlibDataset` in `finetune/dataset.py` calls `pickle.load` on `train_data.pkl` and `val_data.pkl` files that the user is expected to generate with `finetune/qlib_data_preprocess.py`. Python's `pickle` module executes arbitrary code during deserialization — this is not a subtle vulnerability, it is the textbook RCE class that Python's own docs warn against.

A fix PR (#249) was opened on 2026-04-13 proposing a `RestrictedUnpickler` that whitelists safe classes. As of the scan, PR #249 has been open for 7 days with zero reviewer engagement — unremarkable for this repo's PR queue, where 9 other security-relevant fixes from external contributors have sat 5-7 days in the same state (E8). The issue itself has been open 95 days.

For consumers: if you plan to run anything under `finetune/`, you need to treat every `.pkl` file as potentially executable. The safe paths are (a) only load `.pkl` files you generated on the same machine in this session, (b) apply PR #249 locally before running any finetune code, or (c) stick to the inference-only usage mode (loading models from Hugging Face via `KronosPredictor`), which does not traverse this code path.

This finding is what drives the Critical verdict on the finetune-deployment split. Without it, the verdict collapses to Warning on governance + dependency hygiene.

**How to fix.** Consumer-side (finetune users): apply PR #249 locally as a patch, OR only run finetune/ code on .pkl files you generated yourself on the same machine. Maintainer-side: review + merge PR #249; publish a security advisory documenting the window.

### F1 — Critical · Vulnerability — 48 known CVEs in runtime dependency graph, with loose/unpinned pinning

*Continuous · Since requirements.txt inception · → Pin deps in a project-local constraints file; re-scan dep graph with `pip-audit` at install time.*

`pip install -r requirements.txt` resolves a dependency graph that currently carries 48 published advisories on osv.dev: numpy (16), torch (12), flask (8), flask-cors (8), tqdm (3), pandas (1). The quality of that install depends on the resolver's state and when you ran it.

Two classes of pinning problem compound the CVE load. Numpy and pandas are fully unpinned in the top-level requirements.txt, leaving the resolver free to pick either a known-vulnerable older release or a post-patch release depending on environment state. Torch is pinned only at `>=2.0.0`, which spans multiple major versions with different CVE exposures. Even the exactly-pinned entries (flask==2.3.3, flask-cors==4.0.0) resolve to versions with published CVEs in their own right.

Neither a dependabot config nor a project-level lockfile gates this. The maintainer has no automated way to know which advisories apply to the current graph. Consumer mitigation is straightforward: run `pip-audit` against your `pip freeze` output in a fresh virtualenv; if it surfaces anything critical in your actual execution path, override-pin those packages in a project-local constraints file before trusting the install.

**How to fix.** Consumer-side: `pip-audit` after install; maintain a project-local constraints file that pins to known-clean versions. Maintainer-side: add dependabot config (.github/dependabot.yml), pin flask/flask-cors to patched versions, decide whether to pin or range-lock numpy/pandas/torch.

### F2 — Warning · Governance — Zero formal review + no branch protection + solo-maintainer signature

*Continuous · Since repo creation (2025-07-01) · → Treat master as 'maintainer's working branch' not 'reviewed code' — pin to a reviewed SHA before production use.*

Across the last 19 closed-and-merged PRs the formal-review rate is 0% and the any-review rate is 5.3% — PR #224 (a webui numpy-pin cleanup) is the only PR in the sample that drew even an informal comment. Every other PR was merged by the maintainer without independent review.

The repo has no classic branch protection (`gh api repos/shiyu-coder/Kronos/branches/master/protection` returns 404), no rulesets (count=0), no CODEOWNERS, and no test-gating CI workflow — the single workflow is a Copilot PR reviewer that produces advisory output, not a merge gate. Combined with a 59% commit share for the maintainer, this is a structurally single-point-of-trust repository: a leaked credential or a compromised maintainer account lands a malicious commit on master with no second-human or automated check.

None of this is evidence of current malice. It IS evidence that the repository's operational model does not include independent review, and consumers who depend on Kronos in production contexts should plan around that — minimally by pinning to a reviewed SHA rather than tracking master.

**How to fix.** Maintainer-side: enable branch protection on master (classic or ruleset) requiring at least 1 review + status checks; add CODEOWNERS naming 2 reviewers. Consumer-side: pin installs to a specific SHA that you personally reviewed.

### F3 — Warning · Structural — Zero formal releases — installs resolve to master HEAD

*Continuous · Since 2025-07-01 · → Pin to a specific commit SHA for any reproducible install.*

Kronos has never cut a release tag. `gh api repos/shiyu-coder/Kronos/releases` returns `total_count: 0`. The documented install path in the README is `pip install -r requirements.txt` against a fresh clone — meaning the installed code is literally whatever commit was on master at clone time.

The absence of releases is an amplifier for F2. In projects with versioned releases, the governance gap at HEAD matters less to consumers because they can pin to a reviewed tag. Here, HEAD is the only reachable version. Regressions and malicious commits both ship instantly to anyone who clones after they land.

The fix on the consumer side is trivial (`git checkout REVIEWED-SHA` before the pip install). The fix on the maintainer side — cutting even informal date-based tags (`2026.04`) so downstreams have a rollback target — is also trivial but has not happened in 10 months.

**How to fix.** Maintainer-side: cut even informal date-based tags (e.g., 2026.04) so downstreams have a rollback target. Consumer-side: `git clone && git checkout REVIEWED-SHA` instead of `git clone && pip install`.

### F4 — Warning · Hygiene — No SECURITY.md, no published advisories despite a known unfixed RCE

*Continuous · Ongoing · → If you discover a vuln in Kronos, expect to report it via the public issue tracker only.*

`community/profile` reports no SECURITY.md, no CONTRIBUTING, no CODE_OF_CONDUCT; health percentage 42. The security-advisories endpoint reports 0 published advisories — despite the known pickle RCE in issue #216, which arrived via the public issue tracker and has remained publicly visible and unfixed for 95 days.

The disclosure posture here is effectively 'everything is public'. A reporter with a pre-patched RCE has nowhere to go except the issue tracker, which means any future vulnerability is public before a fix exists. This is a process gap rather than a code defect — but it turns every finding into a race condition between disclosure and exploitation.

The fix is a 1-page SECURITY.md naming the 'Report a vulnerability' button under GitHub's Security tab, plus a retroactive GHSA advisory for #216 documenting the patch once #249 merges. Neither has happened.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md naming 'Report a vulnerability' button + expected response window; publish GHSA advisory retroactively for #216.

### F5 — Info · Hygiene — No dependabot config, no CODEOWNERS, no formal CI beyond Copilot review

*Continuous · Since 2025-07-01 · → Non-blocking; indicates maintenance-capacity ceiling.*

No `.github/dependabot.yml`, no CODEOWNERS, no test-gating CI workflow — the only workflow is a Copilot PR reviewer. This is operational-capacity signal rather than a specific vulnerability. Combined with F2-F4 it paints a consistent picture of a solo-maintainer research repository operating at the edge of its capacity, not a production-supported project. Non-blocking, but useful context for organizations evaluating adoption.

**How to fix.** Maintainer-side: enable dependabot (security-alerts-only minimum); add one CODEOWNERS entry; add a trivial CI workflow that runs existing regression tests.

---

## 02A · Executable file inventory

> Kronos ships Python source files executed via `pip install -r requirements.txt` + `python examples/*.py`. No curl-pipe installer, no shell-executable files classified by the harness (`executable_files: 0`).

### Layer 1 — one-line summary

- Primary install vector is pip-install-requirements; primary code-execution surface is Python modules imported by the user.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `finetune/dataset.py` | library | Python | pickle.load (line 42) — see F0 | None | QlibDataset loads train_data.pkl / val_data.pkl via pickle.load — disclosed RCE vector (issue #216). |
| `finetune/qlib_data_preprocess.py` | library | Python | pickle.dump (lines 115-119) | None | Writes train_data.pkl / val_data.pkl consumed by dataset.py. Dump-side is not directly exploitable but creates the attack surface. |
| `webui/` | web-service | Python (Flask 2.3.3 + flask-cors 4.0.0) | None | Flask listens on a local port when run | Web UI surfaces forecasts via Flask. Dep-graph carries 16 CVEs (flask=8 + flask-cors=8). |

No postinstall scripts, no curl-pipe installer, no shell-executable helpers. Risk surface is the Python code paths themselves, especially finetune/.

---

## 03 · Suspicious code changes

> Sample of 19 recent closed+merged PRs. Only PR #224 received any reviewer feedback; the other 18 merged without independent review.

Sample: the 19 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 0.0% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#243](https://github.com/shiyu-coder/Kronos/pull/243) | fix: preserve batch dim in tokenizer/predictor training | ElhamDevelopmentStudio | shiyu-coder | No formal decision | Merged without review — training-correctness fix |
| [#234](https://github.com/shiyu-coder/Kronos/pull/234) | Fix data leakage in normalization window (#227) | Nikhil1869 | shiyu-coder | No formal decision | Merged without review — data-integrity fix |
| [#232](https://github.com/shiyu-coder/Kronos/pull/232) | fix: use torch.topk instead of calling top_k as function in sample_from_logits | kuishou68 | shiyu-coder | No formal decision | Merged without review — sampling bug |
| [#224](https://github.com/shiyu-coder/Kronos/pull/224) | Fixes #223: remove incompatible numpy pin from webui requirements | randyy179 | shiyu-coder | 2 non-formal reviews | Only PR in sample with reviewer feedback |
| [#211](https://github.com/shiyu-coder/Kronos/pull/211) | Auto-detect device for easier getting started | external | shiyu-coder | No formal decision | None |
| [#174](https://github.com/shiyu-coder/Kronos/pull/174) | Improve inference throughput | external | shiyu-coder | No formal decision | None |
| [#167](https://github.com/shiyu-coder/Kronos/pull/167) | fix: define missing split_token in HierarchicalEmbedding | external | shiyu-coder | No formal decision | None |
| [#59](https://github.com/shiyu-coder/Kronos/pull/59) | fix: add torch.cuda.empty_cache() during autoregressive inference | external | shiyu-coder | No formal decision | None |
| [#54](https://github.com/shiyu-coder/Kronos/pull/54) | bugfix: add missing dependency safetensors==0.6.2 | external | shiyu-coder | No formal decision | None |
| [#25](https://github.com/shiyu-coder/Kronos/pull/25) | feat: full Kronos Web UI functionality | external | shiyu-coder | No formal decision | Full webui feature merged without review |

---

## 04 · Timeline

> ✓ 2 good · 🟡 5 neutral · 🔴 1 concerning
>
> Key beats in Kronos's public lifecycle, anchored on the 95-day pickle-RCE window.

- 🟡 **2025-07-01 · Repo created** — First commit
- 🟢 **2025-08-02 · arXiv paper published** — Kronos research artifact public
- 🟡 **2025-08-17 · Finetune scripts released** — pickle.load path introduced
- 🟢 **2025-11-10 · Accepted to AAAI 2026** — Academic validation
- 🔴 **2026-01-15 · Issue #216 opened — pickle RCE disclosed** — Start of unfixed-RCE window
- 🟡 **2026-04-13 · PR #249 opened proposing fix** — Fix proposed; unmerged at scan
- 🟡 **2026-04-13 · Last push to master** — HEAD at scan: 67b630e
- 🟡 **2026-04-20 · Scan date** — #216 now 95 days open; #249 now 7 days open

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 19,724 | High-visibility research repo |
| Forks | — | None |
| Open issues | 172 | 1 is a security issue (#216 pickle RCE) |
| Primary language | Python | None |
| License | MIT | None |
| Created | 2025-07-01 | ~10 months old at scan |
| Last pushed | 2026-04-13 | None |
| Default branch | master | None |
| Total contributors | 19 | Top-1 share 59% (shiyu-coder) |
| Formal releases | 0 | Ships from master HEAD |
| Latest release tag | — | No tags |
| Open PRs | 25 | Including security-relevant fixes sitting 5-7 days |
| Classic branch protection | OFF (HTTP 404) | None |
| Rulesets | 0 | No modern ruleset-based protection either |
| CODEOWNERS | Absent | None |
| SECURITY.md | Absent | None |
| CONTRIBUTING | Absent | None |
| Published security advisories | 0 | Despite open pickle RCE in #216 |
| Dependabot config | Absent | None |
| Workflows | 1 | Copilot PR reviewer only; no test CI |
| PR formal review rate | 0.0% | 0 of 19 closed PRs had formal review |
| PR any-review rate | 5.3% | 1 of 19 PRs (PR #224) |
| Runtime deps (osv advisories) | 48 | numpy=16, torch=12, flask=8, flask-cors=8, tqdm=3, pandas=1 |
| Model weight distribution | Hugging Face (NeoQuasar/*) | Off-GitHub integrity surface |
| OSSF Scorecard | Not indexed (HTTP 404) | Coverage gap |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 6 documented gaps (OSSF, dependabot scope, dangerous-primitives deserialization miss, distribution-channel model, gitleaks, HF-weight provenance).

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ 4992/5000 remaining at scan start |
| Tarball extraction + local grep | ✅ Scanned (92 files after extraction) |
| OSSF Scorecard | ⚠ Not indexed (HTTP 404) |
| Dependabot alerts | ⚠ HTTP 403 (admin scope required; fell back to osv.dev) |
| osv.dev dependency queries | ✅ 48 CVEs across 6 packages |
| PR review sample | ✅ 19 closed PRs analyzed |
| Dependencies manifest parse | ✅ 2 manifest files (requirements.txt + webui/requirements.txt) |
| Distribution channels inventory | ⚠ 0 channels detected — harness does not model 'git clone + pip install' from master as a channel |
| Dangerous-primitives grep (15 families) | ⚠ 0 hits reported, but pickle.load confirmed present at finetune/dataset.py:42 — coverage gap |
| Agent-rule files inventory | ✅ 0 (not an agent-tool repo) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No suspicious paste-from-command blocks |
| Install script analysis | ✅ 2 detected (pip install -r requirements.txt; pip install pyqlib) — both network, neither pinned |
| Tarball extraction | ✅ 92 files |
| osv.dev | ℹ  |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4992/5000 remaining |

**Gaps noted:**

1. OSSF Scorecard not indexed — overall_score and per-check signals unavailable; governance/review signals derived from raw gh api data instead.
2. Dependabot alerts require admin scope (HTTP 403) — osv.dev used as substitute; dependabot-configured alerting is absent from this repo regardless.
3. Dangerous-primitives deserialization family reported 0 hits but pickle.load is confirmed present at finetune/dataset.py:42 (E12). Harness regex family missed it; authoritative evidence comes from issue #216 + direct file fetch. Pattern-family gap logged.
4. Distribution-channel harness does not classify 'git clone + pip install -r requirements.txt' as a channel — the 0/0 channel count is a coverage artifact, not evidence of 'no install path'.
5. Gitleaks secret-scanning not available on this scan host — secret-in-history check deferred.
6. Hugging Face model-weight integrity (NeoQuasar/*) is outside the scanner's scope — HF access controls + HF hub integrity determine actual artifact provenance.

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from the Phase 1 harness run + direct gh api queries + osv.dev lookups.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — Open security issue #216 discloses unsafe pickle.load on QlibDataset training data — sitting 95 days unfixed; fix PR #249 sitting 7 days unreviewed.

```bash
gh api repos/shiyu-coder/Kronos/issues/216; gh api repos/shiyu-coder/Kronos/pulls/249
```

Result:
```text
Issue #216 created 2026-01-15 (state=open, 1 comment, labels=[]). PR #249 'fix: replace unsafe pickle.load with restricted unpickler' created 2026-04-13 (state=open, not merged).
```

*Classification: fact*

#### ★ Evidence 3 — osv.dev enumerates 48 known CVEs across the runtime dependency graph: numpy (16), torch (12), flask (8), flask-cors (8), tqdm (3), pandas (1).

```bash
docs/phase_1_harness.py shiyu-coder/Kronos # dependencies.osv_lookups
```

Result:
```text
numpy: 16 vulns; torch: 12; flask: 8; flask-cors: 8; tqdm: 3; pandas: 1. Total 48 advisories queryable via osv.dev for the unpinned/loose runtime dependency set.
```

*Classification: fact*

#### ★ Evidence 6 — No branch protection at any layer — classic protection returns 404, rulesets count is 0, rules_on_default is 0.

```bash
gh api repos/shiyu-coder/Kronos/branches/master/protection; gh api repos/shiyu-coder/Kronos/rulesets; gh api 'repos/shiyu-coder/Kronos/rules/branches/master'
```

Result:
```text
classic: HTTP 404; rulesets: {entries:[], count:0}; rules_on_default: {entries:[], count:0}. CODEOWNERS: not found at any standard location.
```

*Classification: fact*

### Other evidence

#### Evidence 2 — pickle.load exists at finetune/dataset.py:42 and pickle.dump calls at finetune/qlib_data_preprocess.py lines 115/117/119 — confirms the RCE vector described in #216.

```bash
gh api repos/shiyu-coder/Kronos/contents/finetune/dataset.py | jq -r .content | base64 -d | grep -n pickle
```

Result:
```text
finetune/dataset.py:1: import pickle
finetune/dataset.py:42:            self.data = pickle.load(f)
finetune/qlib_data_preprocess.py:2: import pickle
finetune/qlib_data_preprocess.py:115:            pickle.dump(train_data, f)
```

*Classification: fact*

#### Evidence 4 — requirements.txt entries are unpinned (numpy, pandas) or loosely pinned (torch >= 2.0.0) — mixed with exact pins (einops==0.8.1, safetensors==0.6.2). webui/requirements.txt similarly mixes pins.

```bash
gh api repos/shiyu-coder/Kronos/contents/requirements.txt | jq -r .content | base64 -d
```

Result:
```text
runtime dependencies (harness-parsed): numpy unpinned; pandas unpinned; torch >=2.0.0; einops ==0.8.1; huggingface_hub ==0.33.1; matplotlib ==3.9.3; safetensors ==0.6.2; flask ==2.3.3; flask-cors ==4.0.0; plotly ==5.17.0.
```

*Classification: fact*

#### Evidence 5 — Zero formal releases — the repo has never cut a version tag; installers resolve to HEAD on master.

```bash
gh api 'repos/shiyu-coder/Kronos/releases?per_page=10'
```

Result:
```text
total_count: 0; releases.entries: []. No git tags. Installation path is `git clone + pip install -r requirements.txt` against the current default-branch commit.
```

*Classification: fact*

#### Evidence 7 — PR review rate is 0.0% formal and 5.3% any-review across the last 19 closed PRs — only 1 of 19 PRs received reviewer feedback before merge.

```bash
gh api 'repos/shiyu-coder/Kronos/pulls?state=closed&per_page=19' # pr_review section
```

Result:
```text
sample_size: 19; formal_review_rate: 0.0; any_review_rate: 5.3 (1 of 19 PRs had 2 reviews — PR #224). self_merge_count: 0. Maintainer merges author-submitted PRs without independent review.
```

*Classification: fact*

#### Evidence 8 — 25 open PRs include multiple unreviewed fixes from external contributors (including security-relevant ones) sitting 5-7 days stale.

```bash
gh api 'repos/shiyu-coder/Kronos/pulls?state=open&per_page=25'
```

Result:
```text
Open (age as of scan): #249 pickle.load fix (7d), #250 flexible dep ranges (7d), #244 'resolve 8 bugs in core model' (7d), #238 '3 silent bugs in sampling' (8d), #263 fix data leakage finetune (5d), #262 fix sampling top-k/top-p (5d), #266 save_pretrained safetensors (5d), #253 tensor-dims fix (6d), #248 encoder/decoder block count (7d). Plus #83 dataloader leakage fix (224 days).
```

*Classification: fact*

#### Evidence 9 — Contributor concentration: shiyu-coder holds 36 of 61 top-contributor commits (59%); top-3 share is 52/61 (85%). Solo-maintainer author signature.

```bash
gh api repos/shiyu-coder/Kronos/contributors --jq '[.[] | {login, contributions}] | .[:6]'
```

Result:
```text
shiyu-coder: 36; Luciferbobo: 9; CharlesJ-ABu: 7; AnMakc: 6; randyy179: 2; xxsunyxx: 1. Total contributor count: 19. Maintainer profile: PhD student at Tsinghua University per GitHub bio.
```

*Classification: fact*

#### Evidence 10 — community/profile reports no SECURITY.md, no CONTRIBUTING, no CODE_OF_CONDUCT; published-advisory count is 0 despite the known pickle RCE (issue #216).

```bash
gh api 'repos/shiyu-coder/Kronos/community/profile'; gh api 'repos/shiyu-coder/Kronos/security-advisories'
```

Result:
```text
health_percentage: 42; has_security_policy: false; has_contributing: false; has_code_of_conduct: false. security-advisories count: 0. Disclosure channel is neither documented nor exercised.
```

*Classification: fact*

#### Evidence 11 — Model weights are hosted off-GitHub at Hugging Face under NeoQuasar/* — separate integrity and provenance surface from the repo.

```bash
curl -sI https://huggingface.co/NeoQuasar/Kronos-base; gh api repos/shiyu-coder/Kronos/readme | jq -r .content | base64 -d | grep -i huggingface
```

Result:
```text
README references NeoQuasar/Kronos-mini, NeoQuasar/Kronos-small, NeoQuasar/Kronos-base, NeoQuasar/Kronos-Tokenizer-2k, NeoQuasar/Kronos-Tokenizer-base. Model-weight integrity depends on HuggingFace Hub access controls, not on this repo's governance.
```

*Classification: fact*

#### Evidence 12 — Harness dangerous_primitives scan reported 0 hits in the deserialization family despite pickle.load being confirmed present at finetune/dataset.py:42 — coverage gap in the harness's regex family.

```bash
docs/phase_1_harness.py # code_patterns.dangerous_primitives.deserialization
```

Result:
```text
deserialization: 0 hits across all scanned files. Authoritative evidence for the pickle RCE comes from issue #216 + direct gh api fetch of finetune/dataset.py, not from the harness primitive scan. Coverage-gap annotation surfaced in coverage_gaps.
```

*Classification: inference — coverage-gap annotation*

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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `67b630e67f6a18c9e9be918d9b4337c960db1e9a` (untagged) · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
