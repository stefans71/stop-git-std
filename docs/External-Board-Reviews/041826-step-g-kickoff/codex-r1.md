**Verdict**

**SIGN OFF WITH DISSENTS.** Additive is the right near-term governance move, but the proposed doc framing has one architectural flaw that should be fixed before applying: it overloads `Path A` / `Path B` to mean a different axis than the Operator Guide already uses (`continuous` vs `delegated` in [SCANNER-OPERATOR-GUIDE.md](/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md:297), [SCANNER-OPERATOR-GUIDE.md](/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md:311), [CLAUDE.md](/root/tinkering/stop-git-std/CLAUDE.md:23)). That will create operator confusion.

**Q1**

Additive is the right call. Step G exists precisely because JSON-first is not yet live-validated; the brief states it has only passed back-authored fixtures, not live scans. Making V2.5-preview primary before Step G would invert the acceptance gate. Architecturally, though, do not present this as two permanent “paths.” Present it as:

- Execution mode: continuous vs delegated
- Rendering pipeline: V2.4 direct-authoring vs V2.5-preview JSON-first

That preserves current Guide semantics in §8 and avoids a second `Path A/B` taxonomy.

**Q2**

Minimal prompt update is warranted, not zero and not rewrite. The output-format half is a contract, not just “investigation.” The prompt explicitly specifies the report structure at [repo-deep-dive-prompt.md](/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md:1106), [repo-deep-dive-prompt.md](/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md:1170), [repo-deep-dive-prompt.md](/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md:1200), [repo-deep-dive-prompt.md](/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md:1353). A short note at the top of the output-format section saying this contract is realized either directly by the LLM or via `scan-schema.json` + renderers is the cleanest unification layer.

**Q3**

Leave the 10 catalog scans alone. They are valid V2.4 artifacts. Retrofitting them would create churn without increasing trust. But the catalog should gain an explicit methodology/version marker so the repo is honest about mixed-era outputs. The brief’s suggestion is right.

**Q4**

Q4.1: Accept repo/package drift, but mark it explicitly as a version boundary. The package is a V2.4 distributable snapshot; the repo is becoming V2.5-preview. Keeping package docs unchanged is defensible only if repo docs clearly say preview and package docs remain self-consistent.

Q4.2: The package validator drift should not be folded into U-1, but it should be scheduled urgently. The Step F consolidation already records `FX-3b` as a real latent bug, not renderer-only ([CONSOLIDATION.md](/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md:47), [CONSOLIDATION.md](/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md:49), [CONSOLIDATION.md](/root/tinkering/stop-git-std/docs/External-Board-Reviews/041826-step-f-alignment-validation/CONSOLIDATION.md:74)). Leaving it indefinitely in the package is architecturally inconsistent.

Q4.3: Full package refresh is separate post-Step-G work. Agreed.

**Q5**

Current wording is not strong enough by itself. I would not require an env var, but I would require stronger doc gating:

- “Use only for Step G acceptance runs”
- “Do not use for catalog scans or user-facing production scans”
- “Preview pipeline; output not yet considered catalog-grade until Step G passes”

That warning should appear in `CLAUDE.md`, the Operator Guide, and `Scan-Readme.md`.

**Q6**

Rollback should be stronger than “revise schema later.” Recommended rollback model:

- Path A remains the only production/default path throughout
- If Step G fails, revert docs to remove V2.5-preview operator instructions from entry-point docs, or quarantine them into a Step G appendix
- Do not mutate package
- Treat failed Step G forms/fixtures as test artifacts, not operator exemplars

That is cleaner than keeping a known-bad preview path in the main operator flow.

**Q7**

Main blind spots:

- The proposal collides with existing `Path A` / `Path B` terminology. This is the biggest issue.
- §8.4 already says the rendered output contract lives in the prompt ([SCANNER-OPERATOR-GUIDE.md](/root/tinkering/stop-git-std/docs/SCANNER-OPERATOR-GUIDE.md:347)). If U-1 adds schema/renderer docs without updating that sentence, the Guide becomes self-contradictory.
- The proposed §8.8 does not explain how an operator authors `form.json` from the bundle. “Reference zustand-form.json for shape” is not enough. There is no operator-facing authoring workflow yet.
- `CLAUDE.md` currently says “Path B” means delegation, not JSON-first ([CLAUDE.md](/root/tinkering/stop-git-std/CLAUDE.md:49)). Reusing that label will break the wizard.

On schema alignment: V1.1 mostly mirrors the variable parts of the prompt contract. It has structures for verdict exhibits, scorecard cells, action steps, findings, executable inventory, PR sample, repo vitals, coverage, and evidence ([scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1054), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1158), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1185), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1210), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1233), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1268), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1272), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:1284)). But it is not a complete mirror of the prompt spec:

- Scanner Integrity section 00 in the prompt requires hit-level file/line/raw-content structure; `scanner_integrity` does not model that explicitly enough ([repo-deep-dive-prompt.md](/root/tinkering/stop-git-std/docs/repo-deep-dive-prompt.md:1466), [scan-schema.json](/root/tinkering/stop-git-std/docs/scan-schema.json:176)).
- Section 08’s variable “methodology version” is modeled, but the rest of Section 08 is largely implicit/static, not formalized.

So: schema is adequate as renderer input, but not yet the single canonical formalization of the full prompt output spec.

**Additional blind spot**

`Scan-Readme.md` is stale on core versioning (`V2.3`, 6/10 catalog, old Path A/B semantics) ([Scan-Readme.md](/root/tinkering/stop-git-std/docs/Scan-Readme.md:1), [Scan-Readme.md](/root/tinkering/stop-git-std/docs/Scan-Readme.md:120)). If you touch docs, this file cannot remain a minor afterthought.

**FIX NOW**

- Do not reuse `Path A` / `Path B` for pipeline variants.
- Update the prompt with a one-line output-contract cross-reference.
- Clarify that preview is Step-G-only and non-production.
- Fix §8.4 wording so prompt/schema/renderers are not in conflict.

**DEFER**

- Full package refresh to V2.5 after Step G.
- Schema hardening for explicit Scanner Integrity hit structure.

**INFO**

- Repo/package guide parity can be intentionally broken, but only as an explicit V2.4 package vs V2.5-preview repo boundary.
