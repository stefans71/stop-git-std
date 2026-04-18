# Systems Thinker — Pipeline & Methodology Review
## Verdict: APPROVE WITH CONDITIONS

## 1. Agreement with 11/5/4 classification (verify each automatable item)
I agree with the direction, but not the exact 11/5/4 boundary as written. The prompt supports a strong facts/computed/structured/prose split, but Category 1 currently includes several operations that are constrained rather than fully deterministic.

Automatable as written by prompt rules:
- `Scorecard cell colors/status` — yes. The calibration table is binding and threshold-based.
- `Solo-maintainer flag` — yes. `>80%` is explicit and the required sentence is verbatim.
- `Boundary-case detection` — yes. This is threshold arithmetic plus a note.
- `Coverage cell status / coverage reporting primitives` — yes. Command outcome and tool availability are factual.
- `Methodology boilerplate` — yes. This should be rendered from a template.
- `Verdict determination` — yes, but only after severity and split-axis are already resolved upstream.

Not fully automatable from prompt rules alone:
- `Severity assignment` — no, not globally. C20, F9, and parts of F15 are deterministic, but general vuln severity still includes context-dependent mitigation judgment.
- `Split-axis classification` — not fully. F4 says split when one headline would mean opposite things to distinct audiences and to choose the most consequential axis. That is structured judgment, not a pure decision tree.
- `Priority evidence selection` — not fully. The falsification test is clear, but mapping evidence to “would change verdict from X to Y” still requires reasoning over the dependency chain.
- `Exhibit grouping` — partially. The `7+` threshold is deterministic, but assigning findings into `vuln/govern/signals` is still taxonomy judgment unless you add explicit finding-type tags upstream.
- `Silent vs unadvertised` — partially. The F5 rule is clear, but deciding whether release notes “reference the fixed attack class” is semantic classification, not simple text match.

My corrected classification is:
- `6 fully automatable now`
- `10 LLM-required but structureable`
- `4 prose/editorial`

If you insist on keeping the current three-bucket framing, the most defensible adjusted split is `8/8/4`, by moving `severity`, `split-axis`, `priority evidence`, `silent vs unadvertised`, and `exhibit theming` out of “fully automatable,” while keeping `verdict` automatable only as a downstream derivation.

## 2. Automate in V1.0 or V2.0?
Automate in V1.0:
- scorecard color/state computation
- solo-maintainer flag
- boundary-case detection
- coverage status generation
- methodology rendering
- final verdict derivation once upstream structured fields are fixed

Automate in V2.0:
- severity engines for specific rule families: C20, F9, F15, fixed threshold findings
- split-verdict triggering
- priority evidence ranking
- F5 silent/unadvertised classifier
- exhibit grouping/theme assignment

Reason: V1 should only automate what is visibly table-driven in the prompt. The rest should first be converted into explicit intermediate fields and audited on a corpus before you trust code to replace scanner judgment.

## 3. Structured operation enums/templates
Use closed enums where the prompt already implies a closed set, and extensible enums where repo-specific variation is expected.

Recommended enums:
- `finding.severity`: `ok | info | warning | critical`
- `finding.status_chip`: `resolved | active | ongoing | mitigated | informational`
- `scorecard.cell_color`: `green | amber | red`
- `coverage.status`: `ok | partial | blocked | not_available | not_indexed | unknown`
- `split.axis`: `none | version | deployment`
- `disclosure_type`: `properly_disclosed | unadvertised | silent | unknown`
- `capability`: `arbitrary_code_exec | file_read | file_write | network_access | credential_access | prompt_injection_channel | persistence | none`
- `action_type`: `install_normally | pin_version | pin_commit | avoid_default_install | set_config | verify_artifact | wait_for_fix | maintainer_governance_fix | maintainer_release_fix | do_not_install`

Threat model should be hybrid:
- closed base enum for common arrival paths: `phishing`, `stale_token`, `session_compromise`, `malicious_extension`, `sloppy_pr_merge`, `runner_compromise`
- optional `other_text` field for repo-specific paths

Timeline events should be structured as:
- `date`
- `event_type`
- `severity_class`
- `label`
- `description`

Catalog metadata should use controlled vocabulary for `category` and `subcategory`, not free text.

## 4. Prose field templates
Use soft templates, not hard sentence shells.

Good approach:
- require intent and evidence slots per prose field
- provide optional starter patterns
- enforce max length and citation linkage

Do not force a single sentence mold like `When you install {repo}...` for every repo. That will flatten useful distinctions and create formulaic prose. The right control is:
- mandatory factual anchors
- mandatory audience
- mandatory counterweight for “does NOT mean”
- short length budget

## 5. 9-phase pipeline assessment
The 9-phase pipeline is correct in spirit and better than the current “LLM does everything” flow. I would keep it, with two adjustments.

Required adjustments:
- Split Phase 3 into `3a deterministic computation` and `3b rule-family classifiers under review`. Do not label all of Phase 3 “computed” until the non-deterministic items above are removed.
- Add a provenance freeze before rendering: every report field should carry `source_type = raw | computed | structured_llm | prose_llm` plus evidence references where applicable.

Recommended final order:
1. Tool execution and raw capture
2. Normalization into investigation form
3. Deterministic computations
4. Structured LLM classification
5. Prose generation
6. JSON assembly with provenance tags
7. Deterministic renderers
8. Validation and completeness checks
9. Spot-check / re-run verification

## 6. Git hook spot-checks
Re-run commands that are high-impact, cheap, and likely to catch stale or fabricated capture:

- `HEAD SHA` capture
- classic branch protection API call
- rulesets applying to default branch
- OSSF Scorecard overall plus one cited per-check score
- one randomly selected evidence command from the appendix

Best concrete set:
1. `gh api "repos/$OWNER/$REPO/commits/HEAD" -q '.sha'`
2. `gh api "repos/$OWNER/$REPO/branches/$DEFAULT_BRANCH/protection" 2>&1 | head -5`
3. `gh api "repos/$OWNER/$REPO/rules/branches/$DEFAULT_BRANCH" 2>&1 | head -20`
4. `curl -s "https://api.securityscorecards.dev/projects/github.com/$OWNER/$REPO" | ...`
5. one deterministic appendix command chosen by stored command hash

Do not use star count as a primary hook check. It is volatile and low-value for integrity verification.

## 7. Investigation form design
Use JSON, filled incrementally, with explicit scan-state transitions.

JSON over YAML because:
- easier schema validation
- easier deterministic rendering
- safer escaping for quoted evidence
- less ambiguity around multiline content and scalar typing

Fill incrementally, one phase at a time:
- raw tool outputs and normalized facts first
- computed fields second
- structured LLM fields third
- prose last

Add sign-off fields:
- `scan_status`: `in_progress | ready_for_validation | validated | manager_approved`
- `manager_signoff`: nullable object set outside the scanner path

The scanner should never set management approval itself.

## Corrections to the analysis
- The analysis overstates “fully automatable” for severity assignment. Prompt V2.4 contains both hard tables and open-ended severity judgment.
- `verdict = max(severity)` is incomplete without the F4 split-verdict decision already having been made.
- Split-axis choice is not binary classification from facts alone; “opposite meaning to two reader groups” is a semantic test.
- Priority evidence selection needs an explicit field-level dependency graph if you want deterministic automation.
- Exhibit grouping is only partly deterministic until findings carry machine-readable themes.
- F5 classification is clearer than typical prose, but still semantic enough that it belongs in structured classification first.
- Catalog metadata is mostly factual, but category/subcategory and short description should stay controlled-LLM, not pure code, unless you maintain a taxonomy classifier.

## Final conditions
- Narrow V1 automation to the clearly table-driven items.
- Reclassify the disputed five operations as structured judgment, not deterministic computation.
- Add provenance tags per field before renderer work begins.
- Use JSON with schema validation and incremental writes.
- Make hook verification compare current outputs to stored raw captures, not just re-run commands in isolation.
- Do a corpus test on at least 20 prior scans before promoting any structured judgment item into deterministic code.
