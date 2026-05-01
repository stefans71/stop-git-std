# freerouting/freerouting — Simple Report

**Verdict: ✗ Critical.** Don't install this — material risks identified.

freerouting — 1.7k-star Java PCB auto-router, 12-year andrasfuchs solo project (86.7%). Critical verdict via F0: BasicBoard.java:108-110 calls `ObjectInputStream.readObject()` on user-loaded files — textbook Java deserialization RCE. 35 files import ObjectInputStream. Positives: Dependabot on Gradle, community health 75%, Gemini-AI triage.

**Scanned:** 2026-04-20 · main @ c5ad3c7 · 1,690 stars · GPL-3.0 · Java

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 86.7% solo-maintainer + anti-destruction-only ruleset (no review rule) + 9.5% formal review
- ✓ **Do they fix problems quickly?** Yes — 0 open security issues, active Dependabot dep-update flow, main actively committed
- ⚠ **Do they tell you about problems?** Partly — CONTRIBUTING + CoC present (health 75%) but no SECURITY.md + 0 advisories in 12 years despite F0 RCE-class surface
- ✗ **Is it safe out of the box?** No — Java deserialization RCE class on user-loaded board files (F0) is a critical on the default consumer path

## Top concerns

1. **[Critical] Java ObjectInputStream.readObject() on user-loaded board files — textbook deserialization RCE class** If a user opens a malicious .binsnapshot (or any serialized board file) obtained from an untrusted source — a shared community project, an email attachment, a file from a compromised sharing site — the file-open action can trigger arbitrary code execution via Java deserialization gadget chains.

2. **[Warning] Solo-maintainer concentration (andrasfuchs 86.7%) + anti-destruction-only ruleset + 9.5% formal review** The governance gate that could catch a compromised-account scenario exists minimally (anti-destruction rules) but does not include a review-requirement step.

3. **[Warning] No SECURITY.md + 0 published advisories in 12 years despite confirmed RCE-class surface (F0)** No documented disclosure channel; no GHSA syndication.

## What should I do?

**Don't install this.** Do NOT open `.binsnapshot` / serialized board files from untrusted sources until freerouting migrates away from Java native serialization.

---

*stop-git-std · scanned 2026-04-20 · [freerouting/freerouting](https://github.com/freerouting/freerouting)*
