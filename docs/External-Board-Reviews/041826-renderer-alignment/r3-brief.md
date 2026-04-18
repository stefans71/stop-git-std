# Board R3 Deliberation — C3 Only (auto_load_tier trigger)

**Round:** R3 Deliberation per FrontierBoard SOP §4-R3. Scoped to C3 only — the one item with a 3-way split in R2.

**Reviewers (positions now named, not anonymized):**
- Pragmatist (Claude) — shippability / proportionality / accuracy lens
- Systems Thinker (Codex) — architecture / data-flow / downstream effects lens
- Skeptic (DeepSeek V4) — risk / failure modes / assumptions lens

---

## 1. R2 status (all 3 agents)

**C1 (rename Step A → schema-freeze repair)** — 3-0 AGREE → settled.

**C7 (Jinja2 + structural fixture + pre-computed form)** — 3-0 AGREE → settled.

**Facilitator-resolved by 2-1 tiebreak (going to R4 confirmation):**
- **C2 (F12 fields scope):** Conditional required (required when `dangerous_calls != None` or kind is security-relevant). Dissent: Codex preferred always-required with nullable fallback for reproducibility.
- **C4 (monorepo + pr_target shape):** Sibling objects (`coverage_detail.monorepo`, `coverage_detail.pr_target_usage`) — not extending `rows[]`. Dissent: DeepSeek preferred extending rows.
- **C5 + C6 (Step G):** Step G exists as post-renderer milestone = C7 acceptance-scan matrix + dual-emit verification. Does NOT block Step B. Renderer ships on Step E. "Pipeline reliable" claim gated on Step G. Dissent (Pragmatist): prefers dropping Step G entirely and just noting a claim-boundary.

**R3 deliberation required on C3 only (genuine 3-way split).**

---

## 2. C3 — The disputed item

**Topic:** Should `auto_load_tier` (enum: Always / Conditionally / User-activated / Unknown-default-Tier-1) be a required property on finding objects in `docs/scan-schema.json`, and if so, on which findings?

**Background:** V2.3 Round 3 consolidation elevated D9 → C9 as FIX NOW: "Rewrite Step 2.5's auto-load section to classify every rule file into four tiers (Always / Conditionally / User-activated / Unknown-default-Tier-1). Tier 1 cards must include the sentence 'This file is auto-loaded for every session — content changes reach every user without opt-in' in the risk statement." `auto_load_tier` already exists as a `$def` in current schema (V1.0) but is referenced by NOTHING — so the FIX NOW never became enforceable.

### 2.1. Pragmatist (Claude) R2 position

**MODIFY → C3: AGREE (category-match only)**

> Same logic as C2. `auto_load_tier` exists as `$def` but is referenced by nothing. On trigger: **required on agent-rule-file findings only** (category match). "Always required" is the noisier option that would force a meaningless `unknown` on unrelated findings — trains LLMs to treat validator as noise.

**Pragmatist's rationale:** Scope the requirement to findings where the category string matches agent-rule-file patterns (`supply-chain/agent-rules/*`, `code/agent-rule-file`, etc.). Proportionate for V1.1 ship.

### 2.2. Systems Thinker (Codex) R2 position

**MODIFY → C3: structural subtype, not category**

> Requiring `auto_load_tier` only by category-pattern matching is too soft, because category strings are taxonomy policy and can drift. Require it on any finding or structured card representing an agent-rule/config file artifact, with category-based detection as one implementation path but not the schema boundary; if you cannot isolate that subtype cleanly yet, require it on all findings whose evidence points at agent-rule files rather than all findings globally.

**Codex's rationale:** Category strings are taxonomy policy that can drift over time. Bind the schema requirement to a structural subtype (e.g., a required `finding_kind` field or evidence-pointer shape), not a string-matching rule. If no clean subtype exists yet, use "evidence points at agent-rule files" as the trigger.

### 2.3. Skeptic (DeepSeek V4) R2 position

**MODIFY → C3: ALL findings universally required**

> `auto_load_tier` should be required on ALL findings, not just agent-rule-file patterns. This ensures consistent classification across the entire security surface. The schema already defines the enum; making it universally required prevents classification gaps and future schema drift. Safer to enforce uniformity than create pattern-based exceptions.

**DeepSeek's rationale:** Universal requirement eliminates classification gaps and exception logic. Schema is simpler; reviewer behavior is uniform; no room for drift.

---

## 3. The actual tradeoff

| Approach | Proportionality | Enforceability | Drift risk |
|---|---|---|---|
| **A. Category-match** (Pragmatist) | High — only asks for classification where it matters | Soft — depends on category string staying stable | Medium — category vocabulary may evolve |
| **B. Structural subtype** (Codex) | Medium — needs a new required field (e.g. `finding_kind: 'agent_rule_file' / 'code' / 'governance' / ...`) or evidence-pointer shape | Hard — binds to structural type that's harder to drift silently | Low — if the subtype field is well-defined, rule is stable |
| **C. Universal** (DeepSeek) | Low — forces `unknown` default on findings that have no relationship to agent-rule loading (e.g. a dependency CVE, an OSSF score) | Hard — schema enforces on all findings | Low — no exceptions to maintain |

**Secondary consideration:** The deferred roadmap in `project_pipeline_architecture.md` already lists **SD2 (finding `kind` + `domain` orthogonal typing)** as a V1.1 post-corpus item:

> SD2: Finding `kind` + `domain` orthogonal typing
> - Add `kind: risk | positive_signal | limitation | context` and `domain: governance | supply_chain | vuln | code | agent | maintainer | infrastructure` to finding schema
> - Trigger: Renderer needs to group/filter by kind (not just severity)

Note: "domain: ... | agent | ..." — there's already a planned `domain` enum where `agent` is a valid value. Codex's "structural subtype" could map to this.

---

## 4. Your task — AGREE or BLOCK

Per SOP §4-R3: **AGREE** = accept the resolution proposed. **BLOCK** = object with rationale. Positions are named now — you're responding with knowledge of who said what.

Two candidate resolutions for you to pick from (or propose your own):

### Option X — Category-match for V1.1, promote to SD2 structural binding in V1.2
- Require `auto_load_tier` on findings where `category` matches one of: `supply-chain/agent-rules/*`, `code/agent-rule-file`, `code/agent-rule-injection`.
- Add a schema `$comment` noting: "V1.2 will re-bind this to a `domain: agent` structural field per SD2 deferred roadmap."
- Result: C3 FIX NOW lands now with the pragmatic trigger; architectural concern is captured for V1.2.

### Option Y — Adopt SD2 `domain` field NOW as part of Step A, bind auto_load_tier to domain=agent
- Accelerate SD2 out of the V1.1 deferred roadmap and into the current Step A.
- Add `domain` enum (governance / supply_chain / vuln / code / agent / maintainer / infrastructure) as required on all findings.
- Require `auto_load_tier` when `domain == "agent"`.
- Result: Codex's structural binding satisfied immediately; Pragmatist's proportionality preserved (still scoped, just via structural field instead of category string); DeepSeek's "no gaps" concern partly satisfied (universal `domain` requirement).
- Cost: Step A grows — `domain` requires a matching enum in the structured-LLM prompt and affects every finding card in the zustand fixture.

### (Option Z — your own proposal)

---

## 5. Output format

Respond in this shape:

```
### C3 R3 Vote: AGREE Option [X / Y / Z] / BLOCK
Rationale: [2-4 sentences. If BLOCK, state what would unblock.]
```

End with one line:
- `VERDICT: SIGN OFF` (you accept the chosen resolution)
- `VERDICT: BLOCK` (you object; cannot proceed to R4 without resolution)

**Save output:**
- Pragmatist (subagent): inline response in final message
- Systems Thinker (Codex): `/tmp/codex-r3.md`
- Skeptic (DeepSeek V4): `.board-review-temp/renderer-alignment/deepseek-r3.md`

---

## 6. Reminder on SOP

Per §4-R3: "Skip if R2 is unanimous." Only C3 is unresolved. R4 confirmation follows R3 — agents sign off on full consolidated plan + all C-item resolutions.

---

## 7. Files to read (unchanged from R2)

- `/root/tinkering/stop-git-std/docs/scan-schema.json` — current schema V1.0
- `/root/tinkering/stop-git-std/docs/board-review-V23-consolidation.md` — C9 FIX NOW text
- `/root/tinkering/stop-git-std/docs/board-review-data/renderer-alignment-r1/` — R1 outputs
- `/root/tinkering/stop-git-std/.board-review-temp/renderer-alignment/` — R2 outputs (pragmatist-r2, codex-r2, deepseek-r2)
- `/root/tinkering/stop-git-std/.board-review-temp/renderer-alignment/r2-brief.md` — R2 consolidation brief (for context on C1-C7)

Memory: `project_pipeline_architecture.md` (for SD2 deferred roadmap context).
