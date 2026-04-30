# Package Audit Report: github-scan-package-V2

**Date:** 2026-04-17
**Auditor:** Claude Opus 4.6 (structural comparison against known-good V2.3 zustand.md)
**Known-good reference:** `/root/tinkering/stop-git-std/docs/GitHub-Scanner-zustand.md` (534 lines, V2.3-post-R3)

---

## Executive summary

The package contains all the CSS classes, template HTML, and design-system rules needed to produce V2.3-quality scans. The problem is that **no file in the package explicitly tells the scan agent to reproduce the structural patterns visible in the reference scans**. The structural richness lives in three places: the HTML template (which agents see but don't always mirror in MD), the S8 design rules in the prompt header (7 of 12 were demoted to "recommended"), and the reference scans (which are included but never described structurally). The prompt's "Markdown file structure" section is a skeleton that actively contradicts the known-good output, and the validator enforces almost none of the structural richness.

**Root cause:** The V2.4 prompt change [O2] demoted 7 S8 rules from "hard" to "recommended" and removed all binding language about section numbering, exhibit structure, evidence grouping, and split-verdict rendering from the MD format specification. Agents treat "recommended" as "optional" and the skeletal MD structure as the authoritative format.

---

## File-by-file analysis

### 1. CLAUDE.md (lines 1-106)

**What it says about report structure:** Almost nothing. It tells agents to:
- Follow the 6-phase workflow in SCANNER-OPERATOR-GUIDE.md (line 20)
- Use reference scans for "structural patterns" (line 82) -- but only says "5 reference scans (different shapes)"
- Copy CSS verbatim (line 49)
- Pick a reference scan by shape (lines 86-94)

**What's missing:**
- No instruction to "match the section numbering pattern (01 · 02 · etc.) from the reference scan"
- No instruction to "use collapsible-section with section-number for every major section"
- No mention of split-verdict exhibits, evidence priority grouping, or exhibit rollup
- No mention of section-status pills, section-subtitle, or section-action blocks
- No mention of vitals-grid (Coverage is rendered as vitals-grid in good scans, not as tables)
- No instruction to use the reference scan's **MD** structure -- only the HTML reference is included
- The phrase "structural patterns" on line 82 is too vague to be actionable

**Recommended fixes:**
- Add after line 82: "When rendering, match the section numbering (`01 ·`, `02 ·`, etc.), collapsible-section wrapping, section-status pill rows, evidence priority grouping, and exhibit rollup patterns from the reference scan. The reference HTML is the structural truth -- your MD and HTML output must reproduce this structure, not the skeletal Markdown file structure in the prompt."

### 2. SCANNER-OPERATOR-GUIDE.md (lines 1-569)

**What it says about report structure:** Very little. Key section:
- **Section 8.4** (line 348-349): "The rendered output's required structural elements are specified by the V2.4 prompt... This guide does not duplicate that specification." -- This is a **delegation to the prompt**, which is where the problem lies.
- **Section 8.5** (line 351-356): Phase 4a says "reads 1-2 shape-matched reference scans" but does not say "reproduce their structural patterns"
- **Section 8.6** (line 358-366): Phase 4b says "HTML-only additions are limited to structural/presentational elements (status chips, verdict-exhibits rollup, timeline dot colour, utility classes)" -- this implies these are HTML-only, which tells agents NOT to put them in MD

**What's missing:**
- No mention of section numbering anywhere in the guide
- No mention of collapsible sections as a structural requirement
- No mention of evidence priority grouping (`★ Priority evidence`)
- No mention of exhibit rollup pattern
- No mention of inventory-summary quick-scan block
- No mention of vitals-grid vs table for coverage/vitals sections
- Section 8.6 line 361 actively damages MD quality by framing structural elements as "HTML-only additions"

**Recommended fixes:**
- **Line 349:** Replace the delegation sentence with an explicit structural checklist:
  ```
  The rendered output must include:
  - Section numbering: `01 ·` through `08 ·` (plus `02A ·` for inventory)
  - Every section wrapped in a collapsible-section with section-number, section-status pills, section-subtitle, and section-action
  - Split-verdict exhibits when F4 fires (grouped by theme: govern/vuln/signals)
  - Evidence Appendix with priority grouping: ★ Priority evidence first, then context, then positives
  - Inventory quick-scan summary block above detailed cards when 3+ exec files exist
  - Coverage as vitals-grid cells, not as a flat table
  ```
- **Line 361:** Reword to clarify that status chips, section-status pills, and exhibits appear in MD too (as markdown equivalents like `> ⚠ 5 Warning · ℹ 2 Info · ✓ 2 OK`)

### 3. repo-deep-dive-prompt.md (lines 1-1166)

This is the most consequential file. It has the most structural instructions but they are undermined by three problems.

#### Problem A: S8 demotion (lines 7-17)

**Hard rules (5):** S8-1 (utility classes), S8-4 (status chips), S8-5 (action hints), S8-8 (rem font-sizes), S8-12 (validator gate)

**Recommended (7):** S8-2 (cyan landmarks), **S8-3 (exhibit rollup)**, **S8-6 (section status pills)**, **S8-7 (priority evidence grouping)**, **S8-9 (timeline severity labels)**, **S8-10 (inventory quick-scan)**, **S8-11 (split-verdict banner)**

**Which recommended rules cause the structural thinness?**

| Rule | Impact on structural richness | Should re-promote? |
|------|-------------------------------|-------------------|
| **S8-3** exhibit rollup | **HIGH** -- Without this, findings are flat bullet lists instead of themed, expandable exhibit blocks | **YES** |
| **S8-6** section status pills | **HIGH** -- Without this, sections have no summary counts (`⚠ 5 Warning · ℹ 2 Info`), forcing the reader to open every section | **YES** |
| **S8-7** priority evidence grouping | **HIGH** -- Without this, evidence appendix is an undifferentiated list with no `★ Priority` grouping, losing the falsification-criterion structure | **YES** |
| **S8-11** split-verdict banner | **HIGH** -- Without this, split verdicts collapse into single-line verdicts, losing audience-specific reads | **YES** |
| S8-9 timeline severity labels | MEDIUM -- Labels like `VULN REPORTED`, `5-DAY LAG` add story but aren't structurally load-bearing | Keep recommended |
| S8-10 inventory quick-scan | MEDIUM -- Quick-scan block is useful but absence doesn't lose data, just the 10-second-read layer | Keep recommended |
| S8-2 cyan landmarks | LOW -- Enforced by CSS, not by LLM (prompt line 907 already says this) | Keep recommended |

**Recommendation:** Re-promote S8-3, S8-6, S8-7, S8-11 from "recommended" to "hard". These four are structurally load-bearing -- their absence is what makes scans look "thin."

#### Problem B: Markdown file structure section (lines 1093-1164)

This is the **single biggest cause** of structural thinness in MD output. Compare:

**What the prompt says (line 1093-1164):**
```markdown
## What Should I Do?
## What We Found
## Executable File Inventory
## Suspicious Code Changes
## Timeline
## Repo Vitals
## Investigation Coverage
## Evidence Appendix
```

**What the known-good zustand.md actually uses:**
```markdown
## 01 · What should I do?
## 02 · What we found
## 02A · Executable file inventory
## 03 · Suspicious code changes
## 04 · Timeline
## 05 · Repo vitals
## 06 · Investigation coverage
## 07 · Evidence appendix
```

**Differences:**
1. No section numbering (`01 ·`, `02 ·`, etc.) in the prompt's MD structure
2. No section-status summary lines (the `> ⚠ 5 Warning · ℹ 2 Info · ✓ 2 OK` blockquotes under each heading)
3. No section-action blocks (the `> **Your action:**` blockquotes)
4. No verdict exhibits (the `<details><summary>` blocks under Verdict)
5. No evidence priority grouping (`### ★ Priority evidence (read first)`)
6. No "How This Scan Works" section (Section 08) -- mentioned at line 1079-1089 but not in the MD structure
7. The finding format shows flat metadata fields but not the rich narrative structure zustand.md uses (threat model paragraphs, meta tables, "what this does NOT mean" blocks, "how to fix" sections)
8. No "Catalog metadata" section -- mentioned elsewhere but absent from the MD structure
9. No Verdict Exhibits section under Verdict

**Recommended fix:** Replace lines 1093-1164 with a structure that matches zustand.md. Add numbering, section-status lines, section-action blocks, evidence grouping, and the full finding card structure.

#### Problem C: The "How This Scan Works" section (lines 1079-1089)

Line 1089 says: "In the MD file, include this as a `## How This Scan Works` section after the Evidence Appendix."

But the Markdown file structure at line 1093 does NOT include this section. Agents read the structure and skip Section 08.

**Fix:** Add `## 08 · How this scan works` to the MD structure.

### 4. GitHub-Repo-Scan-Template.html (2000+ lines)

**Good news:** The template has all the right structural patterns:
- 10 collapsible-sections with section-numbers (00 through 08, plus 02A)
- section-status pills on every summary row
- section-subtitle and section-action blocks
- exhibit rollup pattern (vuln/govern/signals)
- verdict-split two-column layout
- evidence-group-label with priority/context/positives
- inventory-summary quick-scan block
- vitals-grid for coverage and vitals sections

**Bad news:** No agent reads the template and says "I need to reproduce this structure in my MD." The template is used for Phase 4b (HTML from MD), but the agent writing Phase 4a (MD) reads the prompt's "Markdown file structure" section, which is skeletal.

**Recommended fix:** Add a comment block at the top of the template (after the existing HOW TO USE block) that explicitly maps the HTML sections to their MD equivalents:

```
HTML Section 01 (collapsible-section, section-number "01")
  → MD: ## 01 · What should I do?
  → Must include: section-status summary, section-action block, numbered steps
  
HTML Section 02 (section-number "02")
  → MD: ## 02 · What we found
  → Must include: section-status counts, finding cards with status chips + action hints
  
...etc for all sections
```

### 5. scanner-design-system.css (816 lines)

**Status: Complete.** The CSS defines every class the template uses: `.collapsible-section`, `.section-number`, `.section-status`, `.section-action`, `.section-subtitle`, `.exhibit`, `.verdict-split`, `.evidence-group-label`, `.evidence-priority`, `.priority-flag`, `.inventory-summary`, `.vitals-grid`, `.vital-cell`, etc.

**No fixes needed.** The CSS is not the problem -- it's the instructions that fail to require agents to use the patterns the CSS enables.

### 6. validate-scanner-report.py (429 lines)

**HTML mode (`--report`) checks:**
- Tag balance
- EXAMPLE marker balance
- Placeholder count (must be 0)
- Inline style="" count (must be 0) -- S8-1
- px font-sizes (must be 0) -- S8-8
- XSS vectors
- Unescaped `<` heuristic

**Markdown mode (`--markdown`) checks:**
- Minimum 100 lines
- 4 required section headers: Verdict/Executive Summary, Findings, Evidence, Scorecard
- Verdict keyword presence
- Verdict-severity coherence

**What the validator does NOT check (for either mode):**

| Missing check | Impact |
|---------------|--------|
| Section numbering (`01 ·`, `02 ·`, etc.) | Agents produce unnumbered sections |
| Section order | Sections can appear in any order |
| Required section count (8 sections + 02A) | Agents skip sections entirely (especially 08) |
| Collapsible-section wrapping (HTML) | Agents may use flat `<h2>` instead of `<details>` |
| Section-status pills presence | Agents skip summary counts |
| Section-action blocks | Agents skip "YOUR ACTION" blocks |
| Evidence priority grouping | Evidence appendix is flat |
| Exhibit rollup pattern | Findings are flat bullet lists |
| Split-verdict structure | Split verdicts collapse to single lines |
| Inventory summary block | Missing quick-scan layer |
| Coverage vitals-grid usage | Coverage rendered as tables |
| "What Should I Do?" section existence | Can be missing |
| "Investigation Coverage" section existence | Can be missing |
| "Timeline" section existence | Can be missing |
| "How This Scan Works" section existence | Almost always missing |
| Evidence claim/command/result structure | Evidence entries lack structure |
| Finding card metadata fields | Findings are thin prose |

**Recommended fixes (in priority order):**

1. **MD validator: Add required sections.** Expand `required_sections` list to include:
   - What Should I Do / What should I do (mapped to `01 ·`)
   - What We Found / What we found
   - Executable File Inventory / Executable file inventory
   - Investigation Coverage / Investigation coverage
   - Evidence Appendix / Evidence appendix
   - Timeline
   - Repo Vitals / Repo vitals

2. **MD validator: Check section numbering.** Add a check that sections use the `## 0N ·` pattern. Warning if absent.

3. **MD validator: Check evidence structure.** For each `### ` under the Evidence section, verify it contains `Claim:` or `Command:` or `Result:` or the `bash` fenced code block pattern.

4. **MD validator: Check Section 08 existence.** Require `How This Scan Works` or `How this scan works` header.

5. **HTML validator: Check section-number presence.** Verify 8+ `<span class="section-number">` elements exist.

6. **HTML validator: Check collapsible-section count.** Verify 8+ `<details class="collapsible-section">` elements.

### 7. Scan-Readme.md (121 lines)

**What it says about structure:** Nothing beyond "your scan will use a prior scan as its structural template" (line 41). Does not define what "structural template" means.

**Fix:** Add a "Structural requirements" section explaining the numbered-section pattern, section-status lines, and evidence grouping that the reference scans demonstrate.

### 8. reference/GitHub-Scanner-zustand.html

**Status: Good.** This IS a V2.3 scan with full structural richness:
- Section numbers 01-07 (no 08 -- zustand predates the Section 08 requirement)
- Collapsible sections throughout
- Verdict-split with two-column layout
- Exhibit rollup (govern + signals)
- Evidence priority grouping (★ Priority evidence, context, positives)
- Section-status pills on every section
- Section-action blocks
- Vitals-grid for coverage
- Priority-flag markers on evidence cards

**All 5 reference scans** in `reference/` are V2.3 scans with the rich structure. The reference material is there -- agents just aren't told to reproduce it.

---

## Specific answers to the 6 questions

### Q1: Which "recommended" S8 rules are responsible for structural richness?

**S8-3** (exhibit rollup), **S8-6** (section status pills), **S8-7** (priority evidence grouping), and **S8-11** (split-verdict banner) are the four that produce the structural richness. Re-promote all four to "hard."

S8-9 (timeline labels) and S8-10 (inventory quick-scan) are enrichment, not structure. S8-2 (cyan landmarks) is enforced by CSS anyway.

### Q2: Does the prompt's "Markdown file structure" define section order 01-08?

**No.** The Markdown file structure section (prompt lines 1093-1164) uses plain `## What Should I Do?` headers with no numbering. It does not include Section 08 (How This Scan Works). It does not include section-status lines, section-action blocks, verdict exhibits, or evidence priority grouping. It actively contradicts the known-good zustand.md output.

### Q3: Does CLAUDE.md tell agents to "match the reference scan structure"?

**No.** CLAUDE.md line 82 says reference scans show "structural patterns" but never says "match this structure" or "reproduce the section numbering." It only says to pick a reference by shape. The word "structure" appears exactly once in CLAUDE.md and is too vague to be actionable.

### Q4: Does Operator Guide Section 8 tell agents about section numbering, collapsible sections, evidence grouping?

**No.** Section 8.4 explicitly delegates to the prompt: "This guide does not duplicate that specification." Section 8.6 frames structural elements (status chips, exhibits, timeline dots) as "HTML-only additions," which actively tells agents these are not needed in MD. The Operator Guide has zero mentions of "section number," "collapsible," "evidence group," or "exhibit."

### Q5: Are reference scans in reference/ V2.3 scans with rich structure?

**Yes.** All 5 reference HTML scans (zustand, fd, caveman, gstack, Archon) are V2.3 scans with full structural richness -- section numbers, collapsible sections, exhibits, evidence grouping, split-verdict banners, inventory summaries, section-status pills. The reference material is correct; the instructions to use it are absent.

### Q6: Is there any instruction anywhere that says "every section MUST be a collapsible-section with a section-number"?

**No.** The HTML template uses this pattern for all 10 sections, and the CSS defines the classes, but no prose instruction in any file says sections must use this pattern. The closest is the template's comment block (lines 6-30) which says "Every flagged section MUST carry a section-status pill row + section-action" but does not say "must be a collapsible-section with a section-number."

---

## Priority fix list (ordered by impact)

### Fix 1 (CRITICAL): Rewrite prompt's Markdown file structure

**File:** `repo-deep-dive-prompt.md` lines 1093-1164
**Action:** Replace the skeletal structure with one matching zustand.md's actual pattern. Include:
- Section numbering: `## 01 · What should I do?` through `## 08 · How this scan works`
- Section-status summary lines as blockquotes under each heading
- Section-action blocks ("**Your action:**")
- Verdict exhibits structure (`<details>` blocks or `>` blockquotes)
- Evidence priority grouping (`### ★ Priority evidence (read first)`)
- Finding card full structure (threat model, meta table, "what this does NOT mean", "how to fix")
- `## 08 · How this scan works` section

### Fix 2 (CRITICAL): Re-promote 4 S8 rules to hard

**File:** `repo-deep-dive-prompt.md` lines 7-17
**Action:** Move S8-3, S8-6, S8-7, S8-11 from "Recommended" to "Hard design rules":
- **S8-3** exhibit rollup (7+ items)
- **S8-6** section status pills
- **S8-7** priority evidence grouping
- **S8-11** split-verdict banner

This changes the hard rule count from 5 to 9.

### Fix 3 (HIGH): Add structural requirements to CLAUDE.md

**File:** `CLAUDE.md` after line 82
**Action:** Add explicit instruction:
```
**Structural fidelity rule:** Your output must reproduce the section numbering
(01 · through 08 ·), section-status summary lines, section-action blocks,
exhibit rollup, evidence priority grouping, and split-verdict structure visible
in the reference scans. The reference HTML is the structural truth. Read one
reference scan before starting Phase 4a and match its section skeleton.
```

### Fix 4 (HIGH): Expand MD validator checks

**File:** `validate-scanner-report.py` function `check_markdown()`
**Action:** Add checks for:
- 8 required sections (not just 4): add What Should I Do, Executable File Inventory, Investigation Coverage, Timeline, Repo Vitals
- Section numbering pattern (`## 0N ·`) -- warn if absent
- Section 08 existence
- Evidence claim/command/result structure (at least one `bash` code block in Evidence section)
- Minimum finding count (at least 1 `### F` or `### Finding` header)

### Fix 5 (MEDIUM): Fix Operator Guide Section 8.6 framing

**File:** `SCANNER-OPERATOR-GUIDE.md` line 361
**Action:** Reword from "HTML-only additions are limited to structural/presentational elements (status chips, verdict-exhibits rollup...)" to "The MD must include markdown equivalents of key structural elements: section-status summary lines (as blockquotes), section-action blocks, exhibit grouping (as `<details>` blocks or nested headings), and evidence priority grouping (as `### ★ Priority evidence` headers). The HTML adds only CSS-level presentational polish (colours, animations, grid layouts) -- not structural content."

### Fix 6 (MEDIUM): Add MD reference to the package

**Current gap:** The package includes 5 reference HTML scans but zero reference MD scans. Agents producing Phase 4a (MD) have no MD exemplar to follow.
**Action:** Include `reference/GitHub-Scanner-zustand.md` in the package (copy from `/root/tinkering/stop-git-std/docs/GitHub-Scanner-zustand.md`). Update CLAUDE.md to mention it: "For MD structure, see `reference/GitHub-Scanner-zustand.md`."

### Fix 7 (LOW): Add Scan-Readme.md structural requirements section

**File:** `Scan-Readme.md`
**Action:** Add a brief section after "Ready? Here's what happens next" listing the structural requirements: numbered sections, status summaries, evidence grouping, exhibit rollup.

---

## Summary of gaps by structural feature

| Feature | Where it's defined | Where it's required | Why agents miss it |
|---------|-------------------|--------------------|--------------------|
| Section numbering (01 · 02 ·) | HTML template, reference scans | Nowhere in prose | Prompt MD structure uses unnumbered headers |
| Section-status pills | S8-6 (recommended), CSS, template | Not in any hard rule | Demoted from hard to recommended in V2.4 |
| Section-action blocks | S8-6 (recommended), template | Not in any hard rule | Part of the same demotion |
| Exhibit rollup | S8-3 (recommended), CSS, template | Not in any hard rule | Demoted from hard to recommended in V2.4 |
| Split-verdict banner | S8-11 (recommended), CSS, template | Not in any hard rule | Demoted from hard to recommended in V2.4 |
| Evidence priority grouping | S8-7 (recommended), CSS, template | Not in any hard rule | Demoted from hard to recommended in V2.4 |
| Vitals-grid for coverage | Template, reference scans | Nowhere | Not mentioned in prompt at all |
| Section 08 (methodology) | Prompt lines 1079-1089 | Yes (line 1081) | Absent from prompt's MD structure (line 1093) |
| Evidence claim/command/result | Prompt lines 1062-1077 | Yes | Not in MD structure or validator |
| Finding threat model | F13, prompt lines 992-1003 | Yes (per finding) | Not reflected in MD structure finding template |
