# shiyu-coder/Kronos — Simple Report

**Verdict: ✗ Critical.** Don't install this — material risks identified.

Kronos is a legitimate AAAI-2026 research artifact for financial candlestick forecasting, 19.7k stars, MIT, Python. The science is real; the operational posture is not. A pickle RCE on the finetune data path (issue #216) has sat unfixed 95 days with its fix PR unreviewed 7 days. The dep graph carries 48 known CVEs. Zero releases — every install tracks master — with no branch protection and 0% formal PR review. Inference-only users (HF weights via KronosPredictor) avoid the pickle path; finetune users do not — the Deployment split reflects that gap.

**Scanned:** 2026-04-20 · main @ 67b630e · 19,724 stars · MIT · Python

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 0% formal review, no branch protection, no CODEOWNERS
- ✗ **Do they fix problems quickly?** No — 95-day-old RCE issue #216 unfixed, fix PR #249 sitting 7 days unreviewed
- ✗ **Do they tell you about problems?** No — no SECURITY.md, 0 advisories published despite open RCE issue #216
- ✗ **Is it safe out of the box?** No — install from master + unpinned deps + disclosed RCE on finetune path

## Top concerns

1. **[Critical] Unsafe pickle.load on training data — disclosed RCE unfixed for 95 days** If you finetune Kronos on a `.pkl` file you did not generate locally, and that file was tampered with, running the dataset loader executes attacker-controlled Python.

2. **[Critical] 48 known CVEs in runtime dependency graph, with loose/unpinned pinning** On a fresh `pip install -r requirements.txt`, the dependency resolver may pull versions with published CVEs.

3. **[Warning] Zero formal review + no branch protection + solo-maintainer signature** Commits land on master without independent review.

## What should I do?

**Don't install this.** Finetune users: do NOT run finetune/* with untrusted .pkl files. Apply PR #249 patch locally or wait for merge.

---

*stop-git-std · scanned 2026-04-20 · [shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos)*
