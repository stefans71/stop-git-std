**Verdict**

**SIGN OFF WITH DISSENTS.** The overall Step G shape is right: keep scope to the 3 fixtured shapes, use pinned-SHA replays for parity, and do not parallelize the first live JSON-first run. But do **not** execute as currently written without two execution-time additions: a pre-render semantic gate on `form.json`, and a graduated failure rubric. The present contract proves renderer determinism and MD/HTML parity; it does **not** yet adequately prove bundle→`form.json` semantic fidelity. The schema is permissive inside Phases 3–5, and the guide currently allows operators to “mirror” compute logic manually, which reintroduces authorial drift into an allegedly deterministic phase ([SCANNER-OPERATOR-GUIDE.md:427-433](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md), [scan-schema.json:1031-1121](file:///root/tinkering/stop-git-std/docs/scan-schema.json), [scan-schema.json:1123-1368](file:///root/tinkering/stop-git-std/docs/scan-schema.json)).

**Q1**

3 total targets is the correct acceptance-set size, but the execution shape should be **1 + 2 sequential**, not “all 3 in one uninterrupted continuous sweep.” Only 3 shapes are fixtured for V1.1, and Step G is explicitly limited to those shapes ([SCANNER-OPERATOR-GUIDE.md:382-387](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md), [REPO_MAP.md:165-179](file:///root/tinkering/stop-git-std/REPO_MAP.md)). Expanding to 5 would mix fixture authoring with acceptance. Contracting to 1 loses cross-shape signal. Recommendation: run `zustand` first as a pilot, hold a stop/go review, then run `caveman` and `Archon`.

**Q2**

Use the V2.4 catalog SHAs, not fresh HEAD. Step G’s success criterion is structural parity against the existing scan of the same repo, so same-SHA replay is the clean isolation boundary ([SCANNER-OPERATOR-GUIDE.md:444-450](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md)). Live-data handling has already been partially de-risked by the Archon rerun record: SHA drift changed counts and tables, but not the structural finding set or verdict shape ([GitHub-Scanner-Archon-rerun-record.md:62-78](file:///root/tinkering/stop-git-std/docs/GitHub-Scanner-Archon-rerun-record.md)).

**Q3**

The current plan does **not** yet close the multica-class drift risk; it only relocates it from DOM to schema semantics. `form.json` can be schema-valid while omitting or mis-stating key semantics because most internals of `phase_3_computed`, `phase_4_structured_llm`, and `phase_5_prose_llm` are optional ([scan-schema.json:1031-1121](file:///root/tinkering/stop-git-std/docs/scan-schema.json), [scan-schema.json:1123-1368](file:///root/tinkering/stop-git-std/docs/scan-schema.json)). Add a **pre-render semantic checklist** per target:

- Finding inventory exact-match: every F-ID in bundle summary maps to exactly one `findings.entries[]`, no extras.
- Severity exact-match: each mapped finding’s severity must match the V2.4 comparator.
- Scorecard exact-match: all 4 canonical cells and colors match comparator.
- Verdict exact-match: `phase_4b_computed.verdict.level` matches comparator and is derivable from the finding set.
- Split-axis exact-match: if comparator is split, axis must match (`deployment` vs `version`).
- Evidence linkage exact-match: every non-OK finding has `evidence_refs`, and every ref resolves to a declared evidence entry ([scan-schema.json:515-541](file:///root/tinkering/stop-git-std/docs/scan-schema.json), [SCANNER-OPERATOR-GUIDE.md:444-450](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md)).

**Q4**

Run one adversarial smoke test on `--bundle` before Step G. The validator checks the right classes of mistakes, but the evidence provided so far is “16 tests + 5 clean corpus bundles,” and the implementation still lets warning-only outcomes pass with exit 0 ([AUDIT_TRAIL.md:75-89](file:///root/tinkering/stop-git-std/AUDIT_TRAIL.md), [validate-scanner-report.py:682-798](file:///root/tinkering/stop-git-std/docs/validate-scanner-report.py), [validate-scanner-report.py:837-848](file:///root/tinkering/stop-git-std/docs/validate-scanner-report.py)). Inject one synthesis verb into an evidence block and one orphan F-ID into synthesis; confirm both hard-fail.

**Q5**

Do **not** parallelize across the 3 targets. The new failure surface is bundle→`form.json`, and sequential execution gives you information reuse without contaminating the diagnosis space. Parallel runs would tell you “three operators drafted three different forms” but not whether the prompt, the schema, the manual compute step, or the semantic checklist is the actual problem. This is especially true because Step G still keeps Phases 4–6 LLM-in-the-loop ([SCANNER-OPERATOR-GUIDE.md:464-466](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md)). Recommendation: sequential, same operator, with a hard checkpoint after target 1.

**Q6**

17/18 is **not** a Step G pass. Step G is the acceptance gate for the “pipeline reliable” claim, and the guide currently defines pass as all gates on all targets ([SCANNER-OPERATOR-GUIDE.md:444-450](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md), [041826-renderer-alignment/CONSOLIDATION.md:48-56](file:///root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-renderer-alignment/CONSOLIDATION.md)). But failure disposition should be graduated:

- Isolated target failure: overall Step G = fail, failed artifact tagged `step-g-failed-artifact`, other targets retained as evidence, no full quarantine yet.
- Repeated target failure on same gate or any defect in compute/schema/validator contract: Step G = fail and §8.8 quarantined per rollback.
- Comparator ambiguity or rubric ambiguity discovered mid-run: halt immediately; no pass/fail claim until rubric is fixed.

Full quarantine should be reserved for **systemic** defects, not a single localized miss.

**Q7**

The 3 V2.4 comparators are trustworthy enough. U-10 explicitly revalidated the catalog against the fixed validator and re-canonicalized scorecards/verdicts ([REPO_MAP.md:167-176](file:///root/tinkering/stop-git-std/REPO_MAP.md), [AUDIT_TRAIL.md:105-124](file:///root/tinkering/stop-git-std/AUDIT_TRAIL.md)). The three comparator MD/HTML pairs all show the canonical four scorecard questions and aligned verdict banners/headers ([GitHub-Scanner-zustand-v3.md:19-34](file:///root/tinkering/stop-git-std/docs/GitHub-Scanner-zustand-v3.md), [GitHub-Scanner-zustand-v3.html:891-1025](file:///root/tinkering/stop-git-std/docs/GitHub-Scanner-zustand-v3.html), [GitHub-Scanner-caveman.md:26-78](file:///root/tinkering/stop-git-std/docs/GitHub-Scanner-caveman.md), [GitHub-Scanner-caveman.html:889-1043](file:///root/tinkering/stop-git-std/docs/GitHub-Scanner-caveman.html), [GitHub-Scanner-Archon.md:25-78](file:///root/tinkering/stop-git-std/docs/GitHub-Scanner-Archon.md), [GitHub-Scanner-Archon.html:882-1036](file:///root/tinkering/stop-git-std/docs/GitHub-Scanner-Archon.html)).

**Q8**

Biggest remaining blind spot: the guide still permits operators to “invoke `docs/compute.py` functions on Phase 1 data (or mirror their logic)” ([SCANNER-OPERATOR-GUIDE.md:427-433](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md)). For Step G, “mirror their logic” should be disallowed. A deterministic phase cannot be hand-reimplemented during acceptance. Require direct compute execution and preserve the emitted values as artifacts.

Second blind spot: the source packet is state-inconsistent. The brief says review-start HEAD `30da757`, while `REPO_MAP.md` and the top `AUDIT_TRAIL.md` checkpoint still point to earlier audit heads ([r1-brief.md:7](file:///root/tinkering/stop-git-std/.board-review-temp/step-g-execution/r1-brief.md), [REPO_MAP.md:3-4](file:///root/tinkering/stop-git-std/REPO_MAP.md), [REPO_MAP.md:83](file:///root/tinkering/stop-git-std/REPO_MAP.md), [AUDIT_TRAIL.md:20-23](file:///root/tinkering/stop-git-std/AUDIT_TRAIL.md)). Not a blocker, but the Step G packet should include the actual git HEAD in the artifact manifest.

**FIX NOW / DEFER / INFO**

- `FN-1` | High | Remove “or mirror their logic” from Step G execution. Manual reimplementation of Phase 3 undermines the compute/render separation. | Require direct `docs/compute.py` execution and artifact capture.
- `FN-2` | High | Add a pre-render semantic gate for bundle→`form.json`; schema-valid is too weak because Phase 3–5 internals are largely optional. | Use the six-point exact-match checklist from Q3 before rendering.
- `FN-3` | High | Predeclare failure rubric before the first run. Current binary rollback is too coarse for 18 sub-gates. | Use the isolated-vs-systemic rubric from Q6.
- `FN-4` | Medium | Adversarial `--bundle` smoke test missing. Current evidence is corpus-clean, not operator-mistake resistant. | Inject one failing evidence block and one orphan F-ID before live Step G.
- `D-1` | Medium | Schema hardening remains real, especially Scanner Integrity and methodology gaps already logged. | Keep deferred until Step G surfaces concrete pain ([SCANNER-OPERATOR-GUIDE.md:463-468](file:///root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md), [REPO_MAP.md:184-186](file:///root/tinkering/stop-git-std/REPO_MAP.md)).
- `I-1` | Low | Provenance discipline is already correctly separated from production schema. | Keep tagging live Step G forms in `tests/fixtures/provenance.json` before any promotion ([provenance.json:45-47](file:///root/tinkering/stop-git-std/tests/fixtures/provenance.json)).

**Additional blind spots**

- `--parity` and `--bundle` both return 0 when warnings exist, so execution must inspect warning count explicitly, not just exit code ([validate-scanner-report.py:832-848](file:///root/tinkering/stop-git-std/docs/validate-scanner-report.py), [validate-scanner-report.py:864-870](file:///root/tinkering/stop-git-std/docs/validate-scanner-report.py)).
- `zustand-form.json` is itself tagged `authored-from-scan-data`, not `pipeline-produced`, so using it as a template is fine, but using similarity to it as evidence of pipeline correctness is not ([provenance.json:12-21](file:///root/tinkering/stop-git-std/tests/fixtures/provenance.json)).

**Architectural recommendation**

The architecture wants **3-target sequential, but checkpointed**, not “3-target sequential continuous” as a single uninterrupted flow and not parallel. Run target 1, execute the semantic checklist, decide whether failures are operator-local or systemic, then continue. If target 1 passes cleanly, targets 2 and 3 can stay in the same session. If target 1 fails semantically, stop and fix the contract before spending the other two targets.
