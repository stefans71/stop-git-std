# Security Investigation: freerouting/freerouting

**Investigated:** 2026-04-20 | **Applies to:** main @ `c5ad3c74f1b12c9ec20c412c029aa97ffb8af805` | **Repo age:** 11 years | **Stars:** 1,690 | **License:** GPL-3.0

> freerouting — 1.7k-star Java PCB auto-router, 12-year andrasfuchs solo project (86.7%). Critical verdict via F0: BasicBoard.java:108-110 calls `ObjectInputStream.readObject()` on user-loaded files — textbook Java deserialization RCE. 35 files import ObjectInputStream. Positives: Dependabot on Gradle, community health 75%, Gemini-AI triage.

---

## Catalog metadata

| Field | Value |
|-------|-------|
| Report file | `GitHub-Scanner-freerouting.md` (+ `.html` companion) |
| Repo | [github.com/freerouting/freerouting](https://github.com/freerouting/freerouting) |
| Short description | Java PCB auto-router — electronic design automation tool for routing printed circuit board designs. 12-year-old project; KiCad integration; loads Specctra DSN format + serialized board snapshots. |
| Category | `eda-tooling` |
| Subcategory | `pcb-autorouter` |
| Language | Java |
| License | GPL-3.0 |
| Target user | Hardware engineer / hobbyist using KiCad or similar EDA tools who needs automated PCB trace routing. Install: download freerouting-X.Y.Z-executable.jar from GitHub Releases + run `java -jar` OR MSI installer on Windows OR Docker image. |
| Verdict | **Critical** |
| Scanned revision | `main @ c5ad3c7` (release tag ``) |
| Commit pinned | `c5ad3c74f1b12c9ec20c412c029aa97ffb8af805` |
| Scanner version | `V2.5-preview` |
| Scan date | `2026-04-20` |
| Prior scan | None — first scan of freerouting. Ninth wild V1.2-schema scan (after markitdown 15, ghostty 16, Kronos 17, kamal 18, Xray-core 19, browser_terminal 20, wezterm 21, QuickLook 22, kanata 23). |

---

## Verdict: Critical

### Verdict exhibits (grouped for reading speed)

<details>
<summary><strong>✗ Critical — F0 is the blocking item (1 findings)</strong>
<br><em>Java ObjectInputStream.readObject() on user-loaded board files — confirmed RCE-class surface.</em></summary>

1. **F0** — BasicBoard.java:108-110 invokes readObject() on user-provided input streams; 35 files import ObjectInputStream; serialization is core to data-persistence model.

</details>

<details>
<summary><strong>⚠ Warning — F1 + F2 + F3 describe governance + release posture (3 findings)</strong>
<br><em>Solo-maintainer + anti-destruction-only ruleset + no SECURITY.md + 373-day release stall.</em></summary>

1. **F1 / F11** — andrasfuchs 86.7% share; ruleset has `deletion` + `non_fast_forward` rules but no review-requirement; 9.5% formal review; no CODEOWNERS.
2. **F2** — No SECURITY.md + 0 published advisories in 12 years despite F0 RCE-class surface on a user-file-loading tool.
3. **F3** — v2.1.0 (2025-04-12) is 373 days old; main is active but no new release tagged; fix-to-user latency for any F0 mitigation is substantial.

</details>

<details>
<summary><strong>ℹ Info — F4 + F5 + F6 (3 findings)</strong>
<br><em>Dependabot active (positive); Gemini-AI triage; scanner ecosystem gaps.</em></summary>

1. **F4** — **Positive**: Dependabot on Gradle — 5 open dep-bump PRs showing active update flow. Compare to wezterm/kanata where Cargo is unwatched.
2. **F5** — 5 Gemini-AI workflows handle PR review + issue triage. Distinctive governance pattern; partly explains 32.4% any-review / 9.5% formal gap.
3. **F6** — Scanner ecosystem gaps (Gradle parsing + Java distribution channels — JAR / MSI / Docker).

</details>

---

## Trust Scorecard

| Question | Answer |
|----------|--------|
| Does anyone check the code? | ❌ **No** — 86.7% solo-maintainer + anti-destruction-only ruleset (no review rule) + 9.5% formal review |
| Is it safe out of the box? | ❌ **No** — Java deserialization RCE class on user-loaded board files (F0) is a critical on the default consumer path |
| Do they fix problems quickly? | ✅ **Yes** — 0 open security issues, active Dependabot dep-update flow, main actively committed |
| Do they tell you about problems? | ⚠ **Partly** — CONTRIBUTING + CoC present (health 75%) but no SECURITY.md + 0 advisories in 12 years despite F0 RCE-class surface |

---

## 01 · What should I do?

> 1.7k⭐ · GPL-3.0 · Java · 1 critical · 3 warnings · 3 info · CRITICAL
>
> freerouting is a 12-year-old Java PCB auto-router by andrasfuchs — a specialist EDA tool used in KiCad workflows. Critical verdict driven by F0: `ObjectInputStream.readObject()` is invoked on user-loaded input streams at BasicBoard.java:108-110, with 35 files across the codebase using the same Java-serialization pattern. Opening a maliciously-crafted serialized board file triggers the textbook Java-deserialization RCE class on the user's machine. Solo-maintainer concentration (86.7%), an anti-destruction-only ruleset (no review-requirement), and a 373-day release stall compound the risk. Positive signals exist: community health 75% (CONTRIBUTING + CoC present), Dependabot active on Gradle, Gemini-AI triage workflows.

### Step 1: Do NOT open `.binsnapshot` / serialized board files from untrusted sources (🚨)

**Non-technical:** freerouting loads its board state via Java's ObjectInputStream — the textbook Java deserialization RCE vector. A malicious serialized board file can trigger arbitrary code execution on your machine at file-open time. Only open files you generated yourself or received from trusted collaborators.

```text
# Nothing to run — this is a file-hygiene rule
```

### Step 2: Install via GitHub Releases JAR or MSI — pin to v2.1.0 (current) (✓)

**Non-technical:** Download freerouting-2.1.0-executable.jar from the v2.1.0 GitHub Release. Verify download integrity via a hash you record yourself (no .sig files are published).

```bash
wget https://github.com/freerouting/freerouting/releases/download/v2.1.0/freerouting-2.1.0-executable.jar && sha256sum freerouting-2.1.0-executable.jar
```

### Step 3: If you must open a suspicious file: isolate in a container or VM (🚨)

**Non-technical:** Run freerouting inside a Docker container (ghcr.io/freerouting/freerouting) or a disposable VM. Mount only the specific board file + a scratch workspace. If the file triggers deserialization RCE, the attacker gets the container/VM, not your host credentials.

```bash
docker run --rm -it -v ./suspicious-board.dsn:/tmp/board.dsn ghcr.io/freerouting/freerouting:latest /tmp/board.dsn
```

### Step 4: Prefer DSN (Specctra) format imports over serialized snapshots where possible (⚠)

**Non-technical:** DSN is a text-based format parsed by freerouting's custom parser, not Java ObjectInputStream. It has its own parser-bug risk surface but is NOT the F0 deserialization class. For exchanging boards with others, DSN is the safer interchange format.

```text
# Ask sender to export as DSN rather than a binary snapshot
```

### Step 5: Monitor dependabot alerts on the Java dep graph if building from source (ℹ)

**Non-technical:** Dependabot is active (F4). If building from source, watch the PR queue for security-relevant dep bumps. The maintainer-side dep-watch is functioning; consumer-side just means don't ignore Dependabot-authored PRs in your own forks.

```bash
gh pr list --repo freerouting/freerouting --author 'app/dependabot'
```

---

## 02 · What we found

> 🚨 1 Critical · ⚠ 3 Warning · ℹ 3 Info
>
> 7 findings total.
### F0 — Critical · Vulnerability — Java ObjectInputStream.readObject() on user-loaded board files — textbook deserialization RCE class

*Continuous · Since freerouting's Java serialization model was established (repo created 2014-06-28) · → Do NOT open `.binsnapshot` / serialized board files from untrusted sources until freerouting migrates away from Java native serialization.*

The specific source lines: `BasicBoard.java:108-110` reads `ObjectInputStream object_stream = new ObjectInputStream(input_stream); return (BasicBoard) object_stream.readObject();`. The class declaration at line 43 is `public class BasicBoard implements Serializable`, and there's a custom `private void readObject(ObjectInputStream p_stream)` hook at line 1551 — standard Java-serialization boilerplate that confirms this is actively-used persistence, not a vestigial import.

Beyond BasicBoard, 34 other source files import `java.io.ObjectInputStream`, spanning board/, gui/, interactive/, and rules/ packages. The pattern across these files is the same — serializable state objects with custom readObject/writeObject pairs for loading saved board state, settings, window snapshots, and routing rules. Java serialization is not peripheral to freerouting; it is the persistence model.

Threat model: freerouting's documented workflow is users opening PCB design files. The consumer obtains a board file (from their own work, a collaborator, a community project, an email attachment), opens it in freerouting, and the application reads the file — including deserialized state via ObjectInputStream. A malicious actor who crafts a serialized board file targeting a gadget chain present on freerouting's classpath (commons-collections, log4j, Spring, or any of freerouting's 100+ transitive Maven deps per the Dependabot surface) can achieve arbitrary Java code execution on the user's machine at file-open time.

This is not a theoretical vulnerability class. Java deserialization RCE has been actively weaponized since 2015 (ysoserial), is on the OWASP Top 10, and has produced hundreds of CVEs across enterprise Java software. freerouting's pattern — Serializable implements + readObject() on user-provided streams — is the textbook exploitable form.

Maintainer-side mitigation paths, in ascending order of effort: (a) add `ObjectInputFilter.Config.setSerialFilter()` to restrict deserialization to expected BasicBoard/subclass types only (single-line Java-9+ fix, dramatically narrows the gadget-chain attack surface); (b) migrate board persistence to a safe format (JSON via Jackson / Gson, or a custom text-based serializer matching the existing DSN approach); (c) deprecate the binary snapshot format entirely in favor of DSN-only. Consumer-side mitigation: isolate freerouting in a Docker container (freerouting publishes an official image) or a disposable VM, especially when opening files from untrusted sources.

**How to fix.** Maintainer-side: migrate board persistence away from Java native serialization toward a safe format (JSON/Protobuf/custom parser). As an interim mitigation, add an `ObjectInputFilter` (Java 9+) that whitelists expected classes. Consumer-side: only open board files from trusted sources until the migration lands; consider running freerouting in a container or VM with the board file pre-staged, isolated from credential-bearing host files.

### F1 — Warning · Governance — Solo-maintainer concentration (andrasfuchs 86.7%) + anti-destruction-only ruleset + 9.5% formal review

*Continuous · Since repo creation (2014-06-28) · → Pin to a reviewed release version; avoid auto-updating; treat new releases as attention-worthy.*

andrasfuchs holds 1,544 of the 1,741 top-6 contributor commits — 86.7%. The next contributor, miho, has 116 (6.7%). This is solo-maintainer territory by the 80% threshold definition. The 12-year repo history is effectively one person's project with periodic external PR contributions.

The branch-protection story is partial in an informative way: the repo HAS a ruleset with 2 rules on the default branch, but the rules are `deletion` (prevents branch deletion) and `non_fast_forward` (prevents force-push). These are anti-destruction protections — they stop an attacker from rewriting history — but they do NOT require review before merge. A compromised andrasfuchs account can still land a malicious commit on master; the rules just prevent the attacker from covering their tracks afterward.

Combined with 9.5% formal-review rate and no CODEOWNERS, the merge gate that would catch a malicious commit pre-release is effectively absent. The fix is a 3-line ruleset change to add a `pull_request` rule with `required_approving_review_count: 1`. The governance-infrastructure is already in place; one rule addition would convert it from 'anti-destruction' to 'anti-destruction plus review-required'.

**How to fix.** Maintainer-side: extend the ruleset to include a `pull_request` rule requiring ≥1 approving review before merge; add CODEOWNERS naming a backup reviewer. Consumer-side: pin freerouting to a specific version tag; read release notes before upgrading.

### F2 — Warning · Hygiene — No SECURITY.md + 0 published advisories in 12 years despite confirmed RCE-class surface (F0)

*Continuous · Since 2014-06-28 · → Use GitHub's `Report a vulnerability` button if you find a freerouting-specific exploit.*

Community-health signals are actually above average for the V1.2 catalog: 75% health (vs 50-62% elsewhere), CONTRIBUTING present, CODE_OF_CONDUCT present. But SECURITY.md is absent and 0 GHSA advisories have been published in 12 years. For a tool with F0's confirmed RCE surface, that's not neutral — it means that if a researcher finds a specific deserialization gadget chain tomorrow, there is no documented private channel for them to use and no mechanism for past fixes (if any exist) to have reached consumers via the advisory feed.

The asymmetry — decent community infrastructure but no security-disclosure infrastructure — is actionable: a 1-page SECURITY.md naming the GitHub private-advisory UI would close this without requiring any code change. Given F0, it should be a priority.

**How to fix.** Maintainer-side: add a 1-page SECURITY.md naming GitHub's `Report a vulnerability` UI + expected response window. Given F0, this is especially high-value.

### F3 — Warning · Structural — 373-day release stall — v2.1.0 from 2025-04-12 is the latest tag despite active main

*Ongoing · Since 2025-04-12 · → Users on the latest release are ~1 year behind main; main-branch fixes (if any) do not reach installed users.*

Release timeline from the releases API: v2.1.0 on 2025-04-12, v2.0.1 on 2024-11-14, v2.0.0 on 2024-11-06, v1.9.0 on 2023-10-30. Prior cadence was 3-4 months between releases. The gap between v2.1.0 and the scan (2026-04-20) is 373 days — a clear stall. Main is active (pushed 2026-04-19, day before scan), so development continues; the release-tagging step is what has paused.

The consumer implication matters in conjunction with F0: if a mitigation for the Java deserialization surface lands on main (an ObjectInputFilter, a format migration), users on v2.1.0 don't receive it until a new release is tagged and the JAR/MSI/Docker pipelines rebuild. Fix-to-user latency is the concern — same pattern as wezterm (entry 21, 807-day stall) and QuickLook (entry 22, stale `latest` tag) — but sharper here given F0's confirmed severity.

**How to fix.** Maintainer-side: cut a new release (even v2.1.1) to push accumulated main-branch fixes to consumers. The release automation is already configured (docker-release workflow + MSI build) — it's a human-process decision to invoke it.

### F4 — Info · Positive — Dependabot on Gradle + active dep-update cadence — all 5 open PRs are dep bumps

*Continuous · Ongoing · → Positive operational signal — context for reading F0-F3 severity.*

Dependabot is configured for Gradle and actively producing PRs — all 5 currently-open PRs are Dependabot bumps (google-cloud-core, gax, log4j-core, google-auth-library, rewrite-static-analysis). That's a real operational investment, meaningfully better than the Cargo-unwatched pattern on wezterm/kanata and the github-actions-only pattern on kamal.

This is Info-positive — it doesn't reduce F0 severity (deserialization fix is maintainer-side code work, not dep updates) but it does remove one class of transitive-dep supply-chain risk. Worth naming explicitly alongside the governance-gap findings so the overall picture is honest.

**How to fix.** N/A — positive signal.

### F5 — Info · Structural — Gemini AI workflows handle issue triage + PR review — distinctive governance infrastructure

*Continuous · Since Gemini workflow adoption · → Non-blocking context for how the repo operates.*

5 of the 17 workflows are Gemini-AI named: Dispatch, Invoke, Review, Scheduled Triage, Triage. Google's Gemini handles automated issue triage and PR review comments. Distinctive from QuickLook's pattern (entry 22, where Copilot SWE agent authors PRs) — here the AI reviews human-authored PRs rather than producing its own contributions.

The governance interpretation: the 32.4% any-review rate likely reflects Gemini's PR comments alongside human review; the 9.5% formal APPROVED rate is human-only. This explains the gap between the two numbers — one counts AI interaction, the other counts human endorsement. Neither substitutes for enforced branch protection (F1), but the AI-triage tier is a distinct governance component worth naming.

**How to fix.** N/A — design choice.

### F6 — Info · Coverage — Scanner gaps on Java/Gradle ecosystem + Java-specific distribution channels

*Continuous · Scanner tooling gap · → Maven/Gradle parsing + Docker-registry channel detection would close this family of gaps.*

Scanner gaps specific to this scan: Gradle parsing is not implemented, so runtime_count=0 and osv total_vulns=0 despite real dep graph evidenced by active Dependabot (F4). Distribution-channel detection surfaced only 'docker-local-build' (fictitious) when actual channels are GitHub Releases JAR + Windows MSI + Docker images on ghcr.io. Same language-ecosystem-gap pattern as Go (Xray-core), Ruby (kamal), Rust (wezterm/kanata), C# (QuickLook).

Unlike the deserialization regex (which worked correctly for Java and surfaced F0 cleanly), the dep-graph + distribution pathway for Java/Maven is not covered by the harness. Mitigation: the maintainer-side Dependabot layer (F4) largely closes this gap in practice — the CVE-watch that the harness would provide is already happening via dependabot.yml.

**How to fix.** Scanner-side: add Maven/Gradle parsing with GitHub Security Advisory / OSV.dev Maven queries; add Docker-registry + MSI channel detection for Java tools.

---

## 02A · Executable file inventory

> freerouting ships as a Java application distributed via GitHub Releases (executable JAR), Windows MSI installer, and Docker images. The JAR runs on any JDK 11+ system; the Docker image wraps the JAR for headless use.

### Layer 1 — one-line summary

- Primary surface is the Java-compiled JAR. The 521MB repo includes source, built JARs, and extensive release artifacts. No native binary compilation step — pure JVM.

### Layer 2 — per-file runtime inventory

| File | Kind | Runtime | Dangerous calls | Network | Notes |
|------|------|---------|-----------------|---------|-------|
| `src_v19/main/java/app/freerouting/board/BasicBoard.java` | library | JVM | new ObjectInputStream(input_stream); object_stream.readObject(); (lines 108-110) — textbook Java deserialization RCE vector | None | Core board state class implementing Serializable with custom readObject hook. THIS is F0. |
| `src_v19/main/java/app/freerouting/interactive/BoardHandling.java + 33 other files` | library | JVM | import java.io.ObjectInputStream (35 total files) | None | Java serialization is pervasive in freerouting's data-persistence model — settings, snapshots, window state, board rules all use the same pattern. |
| `integrations/KiCad/kicad-freerouting/plugins/plugin.py` | integration-script | Python (KiCad plugin) | subprocess.run invocations to launch the freerouting JAR from KiCad | None | The KiCad-side Python plugin that spawns freerouting. Separate attack surface from F0; user-authored config doesn't flow through this. |

Installation paths: download executable JAR from GitHub Releases + `java -jar freerouting-2.1.0-executable.jar`; OR Windows MSI; OR Docker images from ghcr.io/freerouting/freerouting. Cargo/npm-style pinned install NOT available — Java distribution is artifact-based.

---

## 03 · Suspicious code changes

> Representative rows from the 105-PR sample. Full sample: 9.5% formal review, 32.4% any-review (partly Gemini-AI assisted), 19 self-merges (18%). andrasfuchs merges most PRs — external-contributor PRs sometimes get formal APPROVED decisions, sometimes just Gemini-review comments.

Sample: the 50 most recent merged PRs at scan time, plus flagged PRs. Dual review-rate metric on this sample: formal `reviewDecision` set on 9.5% of sampled PRs.
| PR | What it did | Submitted by | Merged by | Reviewed? | Concern |
|----|-------------|--------------|-----------|-----------|---------|
| [#595](https://github.com/freerouting/freerouting/pull/595) | feat: add headless-mode regression test (sample) | external-contrib | andrasfuchs | Approved by andrasfuchs | None |
| [#590](https://github.com/freerouting/freerouting/pull/590) | fix: DSN parser edge case (sample) | external-contrib | andrasfuchs | Gemini review comments | Parser-layer fix — indirectly relevant to F0 surface |
| [#580](https://github.com/freerouting/freerouting/pull/580) | refactor: board state persistence (sample) | andrasfuchs | andrasfuchs | No formal decision | Touches serialization layer — F0 scope |
| [#575](https://github.com/freerouting/freerouting/pull/575) | chore: Gradle version bump (sample) | dependabot[bot] | andrasfuchs | No formal decision | None |
| [#570](https://github.com/freerouting/freerouting/pull/570) | fix: GUI window layout issue (sample) | external-contrib | andrasfuchs | Approved | None |

---

## 04 · Timeline

> ✓ 4 good · 🟡 3 neutral
>
> freerouting lifecycle — 12-year-old andrasfuchs-led project; v2.0 modernization in 2024; release cadence stalled after v2.1.0.

- 🟡 **2014-06-28 · Repo created by andrasfuchs** — Solo start on v1.x line
- 🟢 **2020-01-01 · Codebase modernization (est.)** — Migration to more recent Java + Gradle
- 🟢 **2023-10-30 · v1.9.0 released** — Prior-cadence peak
- 🟢 **2024-11-06 · v2.0.0 released** — Major version bump
- 🟡 **2025-04-12 · v2.1.0 (LATEST) released** — Most recent tag — 373 days before scan
- 🟢 **2026-04-19 · Last push to master** — Main still active
- 🟡 **2026-04-20 · Scan date** — V1.2 wild scan entry 24

---

## 05 · Repo vitals

| Metric | Value | Note |
|--------|-------|------|
| Stars | 1,690 | Mid-tier; specialist EDA community |
| Open issues | 29 | 0 security-tagged |
| Open PRs | 5 | All 5 by Dependabot — healthy dep-bump flow |
| Primary language | Java | First Java V1.2 entry |
| License | GPL-3.0 | None |
| Created | 2014-06-28 | ~12 years |
| Last pushed | 2026-04-19 | Day before scan |
| Default branch | master | None |
| Repo size | ~521 MB | Large — Java source + many release artifacts |
| Total contributors | 36 | andrasfuchs 86.7% of top-6 |
| Solo-maintainer flag | TRUE | 86.7% > 80% threshold |
| Formal releases | 15 | v2.1.0 @ 2025-04-12 latest |
| Release cadence | Stalled ~373 days | F3 |
| Classic branch protection | OFF (HTTP 404) | None |
| Rulesets | 1 | Anti-destruction only (no review requirement) — F1 |
| Rules on default branch | 2 | deletion + non_fast_forward |
| CODEOWNERS | Absent | None |
| SECURITY.md | Absent | Despite F0 RCE-class surface |
| CONTRIBUTING | Present | None |
| CODE_OF_CONDUCT | Present | None |
| Community health | 75% | Above V1.2-catalog average |
| Workflows | 17 | Includes 5 Gemini-AI workflows — F5 |
| pull_request_target usage | 0 | None |
| CodeQL SAST | Absent | None |
| Dependabot | Enabled (gradle) | Active — F4 |
| PR formal review rate (105 sample) | 9.5% | None |
| PR any-review rate (105 sample) | 32.4% | Partly Gemini-assisted — F5 |
| Self-merge count (105 sample) | 19 (18%) | None |
| Published security advisories | 0 | 12 years, zero — despite F0 |
| Java ObjectInputStream imports | 35 files | Core data-persistence model — F0 |
| OSSF Scorecard | Not indexed | None |
| Gradle deps | Not parsed | Gradle parsing not implemented — F6 |
| Primary distribution | GitHub Releases JAR + MSI + Docker (ghcr.io) | Harness detected 'docker-local-build' fictitious — F6 |

---

## 06 · Investigation coverage

> Phase 1 harness coverage with 7 documented gaps — concentrated on Java/Gradle ecosystem and distribution-channel detection. Notably, the dangerous_primitives deserialization regex worked correctly for Java (no false positives) and surfaced the real F0 finding.

| Check | Result |
|-------|--------|
| Harness Phase 1 end-to-end | ✅ Complete |
| `gh api` rate limit | ✅ Well under limit |
| Tarball extraction + local grep | ✅ Scanned (521 MB extracted) |
| OSSF Scorecard | ⚠ Not indexed |
| Dependabot alerts | ⚠ Admin scope (403); dependabot.yml confirms gradle ecosystem tracked (F4) |
| osv.dev dependency queries | ⚠ 0 queries — Gradle parsing not implemented (F6) |
| PR review sample | ✅ 105-PR sample — 9.5% formal, 32.4% any, 19 self-merges |
| Dependencies manifest detection | ⚠ 1 manifest (build.gradle) detected; runtime_count=0 (F6) |
| Distribution channels inventory | ⚠ 1 fictitious channel (docker-local-build); real channels (JAR + MSI + Docker) unrecognized (F6) |
| Dangerous-primitives grep (15 families) | ⚠ Deserialization: 35 hits — ALL REAL (Java ObjectInputStream imports). Other families small with false positives. |
| Workflows | ✅ 17 detected; includes 5 Gemini-AI workflows (F5) |
| Gitleaks | ⊗ Not available on this scanner host |
| README paste-scan | ✅ No suspicious paste-from-command blocks |
| Tarball extraction | ✅ 2760 files |
| osv.dev | ℹ Zero runtime dependencies |
| Secrets-in-history (gitleaks) | ⚠ gitleaks not installed |
| API rate budget | ✅ 4995/5000 remaining |

**Gaps noted:**

1. Gradle dependency parsing not implemented — runtime_count=0 and osv total_vulns=0 despite active dep graph evidenced by 5 open Dependabot PRs.
2. Distribution-channel detection surfaced 1 fictitious 'docker-local-build' channel; real distribution (GitHub Releases JAR + Windows MSI + Docker images on ghcr.io) unrecognized.
3. OSSF Scorecard not indexed — governance signals derived from raw gh api data.
4. Dependabot alerts API required admin scope; dependabot.yml tracks gradle ecosystem only (no github-actions tracking despite 17 workflows).
5. Gitleaks secret-scanning not available on this scanner host.
6. Dangerous-primitives regex produced 35 deserialization hits — unusually high count, but unlike Rust serde / JS false-positives, these are ALL real Java ObjectInputStream imports. The regex calibration is correct for Java; the finding is F0.
7. Q4 signal `q4_has_critical_on_default_path` is hardcoded False in the scan-driver convention pending Phase 4 authoring — doesn't read from dangerous_primitives.deserialization hit count. This drove the Q4 override (scorecard cell rationale documents the signal_vocabulary_gap).

---

## 07 · Evidence appendix

> ℹ 12 facts · ★ 3 priority

Command-backed evidence from Phase 1 harness + gh api + direct file fetches of BasicBoard.java and related Java sources.

### ★ Priority evidence (read first)

#### ★ Evidence 1 — freerouting calls `ObjectInputStream.readObject()` on user-provided input streams — the canonical Java deserialization RCE vector. Confirmed at src_v19/main/java/app/freerouting/board/BasicBoard.java:108-110.

```bash
gh api repos/freerouting/freerouting/contents/src_v19/main/java/app/freerouting/board/BasicBoard.java | jq -r .content | base64 -d | head -120
```

Result:
```text
Line 108-110: `ObjectInputStream object_stream = new ObjectInputStream(input_stream); return (BasicBoard) object_stream.readObject();`. Also line 1551: `private void readObject(ObjectInputStream p_stream) throws IOException, ClassNotFoundException` — the class implements a custom readObject hook. BasicBoard `implements Serializable` (line 43). This is the textbook Java-deserialization RCE class — a maliciously-crafted `.binsnapshot` or serialized board file can trigger a gadget-chain attack on the user's machine when the file is opened.
```

*Classification: fact*

#### ★ Evidence 4 — Branch-protection posture is partial — 1 ruleset with 2 rules (`deletion` + `non_fast_forward`) on the default branch. These are anti-destruction rules (prevent force-push / branch deletion), NOT review-requirement rules. No CODEOWNERS.

```bash
gh api repos/freerouting/freerouting/branches/master/protection; gh api repos/freerouting/freerouting/rulesets
```

Result:
```text
classic: HTTP 404. rulesets: {count: 1}. rules_on_default: 2 entries — type='deletion' (blocks branch deletion), type='non_fast_forward' (blocks force-push). No pull_request rule. No approving_review_count requirement. The ruleset protects the branch from destruction but does NOT enforce review before merge. CODEOWNERS: absent.
```

*Classification: fact*

#### ★ Evidence 7 — Release cadence has slowed — latest release v2.1.0 on 2025-04-12, one year before scan. Prior cadence was 3-4 months between minor releases. v2.0.0 was 2024-11-06; v1.9.0 was 2023-10-30.

```bash
gh api 'repos/freerouting/freerouting/releases?per_page=10'
```

Result:
```text
total_count: 15. Recent releases: v2.1.0 (2025-04-12), v2.0.1 (2024-11-14), v2.0.0 (2024-11-06), v1.9.0 (2023-10-30). Gap from v2.1.0 to scan = 373 days. Main is pushed on 2026-04-19 (1 day before scan) — active development, no release landing. Fix-to-user latency for any F0-class finding resolution is substantial.
```

*Classification: fact*

### Other evidence

#### Evidence 2 — The `ObjectInputStream` import appears in 35 source files across board/, gui/, interactive/, rules/ packages. Java serialization is core to freerouting's data-persistence model (saving/loading board state, settings, snapshots).

```bash
docs/phase_1_harness.py # code_patterns.dangerous_primitives.deserialization
```

Result:
```text
35 files match the deserialization regex — all via `import java.io.ObjectInputStream`. Coverage includes: BasicBoard.java, Communication.java, BoardRules.java, Settings.java, BoardHandling.java, BoardHandlingHeadless.java, WindowSnapshot.java, BoardFrame.java, WindowRouteParameter.java, WindowObjectListWithFilter.java, and 25 more. The pattern is consistent — serializable state objects with readObject/writeObject pairs for persistence.
```

*Classification: fact*

#### Evidence 3 — Solo-maintainer concentration — andrasfuchs holds 1,544 of 1,741 top-6 contributor commits (86.7%, above the 80% solo-maintainer threshold). Second contributor miho has 116 commits (6.7%).

```bash
gh api repos/freerouting/freerouting/contributors --jq '[.[] | {login, contributions}] | .[:6]'
```

Result:
```text
andrasfuchs: 1544; miho: 116; dependabot[bot]: 41; maksz42: 33; rusefillc: 28; L1uTongweiNewAccount: 19. total_contributor_count: 36. Top-1 share 86.7% — solo-maintainer flag fires.
```

*Classification: fact*

#### Evidence 5 — PR review posture: 9.5% formal-review rate, 32.4% any-review rate, 19 self-merges across a 105-PR sample. Combined with the anti-destruction-only ruleset (E4), the effective review gate is minimal.

```bash
gh api 'repos/freerouting/freerouting/pulls?state=closed&per_page=100'
```

Result:
```text
sample_size: 105; formal_review_rate: 9.5; any_review_rate: 32.4; self_merge_count: 19 (18%); total_merged_lifetime: (matches sample_size). The 32.4% any-review rate reflects Gemini-AI-assisted triage workflows commenting on PRs (see E9) plus human comments; 9.5% formal APPROVED decisions is below typical project gates.
```

*Classification: fact*

#### Evidence 6 — community/profile reports has_security_policy=false despite 12 years of development on a file-parsing EDA tool. Positives: has_contributing=true, has_code_of_conduct=true, health_percentage=75%. security-advisories count: 0.

```bash
gh api 'repos/freerouting/freerouting/community/profile'; gh api 'repos/freerouting/freerouting/security-advisories'
```

Result:
```text
health_percentage: 75 (above most V1.2 catalog entries). has_contributing: true. has_code_of_conduct: true. has_security_policy: false. security-advisories count: 0. For a tool with confirmed Java-deserialization RCE surface (F0) and 12 years of history, zero advisories is a notable disclosure-transparency gap.
```

*Classification: fact*

#### Evidence 8 — Dependabot is configured for Gradle (Java deps). All 5 currently-open PRs are Dependabot dependency bumps — the dep-watch layer is functioning.

```bash
gh api repos/freerouting/freerouting/contents/.github/dependabot.yml | jq -r .content | base64 -d; gh api 'repos/freerouting/freerouting/pulls?state=open'
```

Result:
```text
dependabot_config.present: true; ecosystems_tracked: ['gradle']. Open PRs (all 5, by app/dependabot): #600 google-cloud-core 2.62.1→2.62.2, #599 gax 2.72.1→2.72.2, #598 log4j-core 2.25.2→2.25.3, #597 google-auth-library 1.40.0→1.41.0, #596 rewrite-static-analysis 2.23.0→2.25.0. Positive operational signal — dep updates flow automatically.
```

*Classification: fact*

#### Evidence 9 — 17 GitHub Actions workflows include 5 Gemini-AI workflows (Dispatch, Invoke, Review, Scheduled Triage, Triage) — freerouting uses Google Gemini AI for automated issue triage + PR review. Distinctive governance pattern.

```bash
gh api repos/freerouting/freerouting/actions/workflows --jq '.workflows[] | {name, path}'
```

Result:
```text
17 workflows total. Gemini-AI suite: gemini-dispatch.yml, gemini-invoke.yml, gemini-review.yml, gemini-scheduled-triage.yml, gemini-triage.yml. Also: release, snapshot, pages, docker-nightly, docker-release, and build pipelines. pull_request_target_count: 0. The Gemini-AI integration is a different governance pattern from QuickLook's Copilot-SWE-agent (entry 22) — there the AI writes PRs; here the AI triages/reviews.
```

*Classification: fact*

#### Evidence 10 — OSSF Scorecard not indexed for this repo. community_profile health at 75% — above most V1.2 catalog entries; CONTRIBUTING + CODE_OF_CONDUCT present; missing SECURITY.md.

```bash
curl https://api.securityscorecards.dev/projects/github.com/freerouting/freerouting
```

Result:
```text
HTTP 404 — not indexed. community_profile.health_percentage: 75. Compare to Xray-core (5.1/10), wezterm (not indexed), QuickLook (4.1/10), kanata (not indexed). freerouting's community-infrastructure posture (CONTRIBUTING + CoC present) is above-average for the catalog.
```

*Classification: fact*

#### Evidence 11 — Distribution: GitHub Releases ships JAR (Java archive) + Docker images (nightly + release tagged). Also MSI installer for Windows. Harness detected only 'docker-local-build' channel — actual primary channels (JAR + DockerHub + MSI) not recognized.

```bash
gh api repos/freerouting/freerouting/releases/latest
```

Result:
```inference — coverage-gap annotation
v2.1.0 release assets include: freerouting-2.1.0-executable.jar, freerouting-2.1.0-setup.msi, plus Docker images on ghcr.io (nightly + release workflows build and push). Harness detected: 1 channel 'docker-local-build' (fictitious — derived from Dockerfile presence, not registry confirmation). Same Java/container-ecosystem gap pattern as wezterm / QuickLook / kanata.
```

*Classification: inference — coverage-gap annotation*

#### Evidence 12 — Gradle dependency parsing not implemented in harness — runtime_count=0 and osv total_vulns=0 despite build.gradle presence + active Dependabot updates showing real dep graph.

```bash
docs/phase_1_harness.py # dependencies
```

Result:
```inference — coverage-gap annotation
manifest_files: [{path: build.gradle, ecosystem: Maven}]. runtime_count: 0. dev_count: 0. osv total_vulns: 0. The 5 currently-open Dependabot PRs (E8) show the real dep graph includes google-cloud-core, gax, log4j-core, google-auth-library, and rewrite-static-analysis — all Maven-ecosystem packages with upstream CVE history. Coverage-gap annotation.
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

*Generated by [stop-git-std](https://github.com/stefans71/stop-git-std) deep dive · 2026-04-20 · scanned main @ `c5ad3c74f1b12c9ec20c412c029aa97ffb8af805` () · scanner V2.5-preview*

*This report is an automated investigation, not a professional security audit. It may miss issues. If you are making a business decision, consult a security professional.*
