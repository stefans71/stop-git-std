#!/usr/bin/env python3
"""
validate-scanner-report.py — HTML structural + template-alignment validator
for GitHub Scanner reports, the scan template, and markdown scan reports.

Usage:
  python3 validate-scanner-report.py [--report | --template | --markdown] <path>
  python3 validate-scanner-report.py --parity <md_path> <html_path>
  python3 validate-scanner-report.py --bundle <findings-bundle.md>

Modes:
  (default)    Permissive mode — checks structure, reports placeholder count as
               info only. Suitable for linting either a template or a rendered
               report.
  --report     Strict mode for rendered HTML reports. Fails non-zero if any
               {{PLACEHOLDER}} tokens remain or any <!-- EXAMPLE-START/END -->
               markers remain. Also runs XSS vector detection (V1 fix) and
               the repo-untrusted-text escape check (C4) heuristic.
  --template   Verification mode for the canonical template. Requires >0
               placeholders and >0 EXAMPLE markers (a template with zero is
               either empty or already a rendered report in disguise). Also
               checks CSS sync against scanner-design-system.css (O4 fix).
  --markdown   Validation mode for .md scan reports. Checks required section
               headers (Verdict, Findings, Evidence, Scorecard), minimum 100
               lines, and severity keyword presence (B3 fix).
  --parity     MD↔HTML structural parity check. Enforces MD-canonical rule:
               HTML may not add findings absent from MD. Verifies scorecard
               question set + verdict level agree (PD2).
  --bundle     U-5/PD3 citation-discipline audit of a findings-bundle.md.
               Checks: evidence sections contain no interpretive verbs;
               Pattern recognition bullets each use an interpretive verb;
               FINDINGS SUMMARY present; Proposed verdict cites F-IDs or
               severity; no orphan F-IDs referenced outside FINDINGS SUMMARY.

What this checks in all modes:
  1. HTML tag balance (every opener has a closer, order preserved).
  2. EXAMPLE-START / EXAMPLE-END marker balance (paired count).
  3. {{PLACEHOLDER}} token count.
  4. Inline style="" attribute count on body elements (V2.3 S8-1 rule: zero).
  5. px font-size declarations (V2.3 S8-8 rule: rem only).

--report mode additionally checks:
  6. Zero placeholders remaining.
  7. Zero EXAMPLE-START/END markers remaining.
  8. Heuristic scan for unescaped '<' or untemplated ampersands in repo-
     quoted text regions (C4 — prompt rule repo-deep-dive-prompt.md:810
     says PR titles, issue titles, commit messages must be HTML-escaped).

Exit codes:
  0  clean
  1  validation issue(s) found
  2  usage error (no file, bad args)

History: first written during Sprint 8 to validate GitHub-Scanner-caveman.html.
Extended post Round-3 board review to close the validator-not-a-gate bug
(board finding C1) and add the untrusted-text escape check (board finding C4).
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID_TAGS = {"br", "img", "meta", "link", "hr", "input", "col", "area", "base",
             "embed", "source", "track", "wbr"}


# ===========================================================================
# V1.2 form-mode validation helpers
# ===========================================================================

OVERRIDE_RATIONALE_MIN_CHARS = 50  # per V1.2 board review Item A

_SCORECARD_QUESTION_KEYS = (
    "does_anyone_check_the_code",
    "do_they_fix_problems_quickly",
    "do_they_tell_you_about_problems",
    "is_it_safe_out_of_the_box",
)


def _load_compute_constants():
    """Import SIGNAL_IDS + OVERRIDE_REASON_ENUM from docs/compute.py.

    Defers the import so --report / --parity / etc. callers don't pay the
    compute.py import cost unless they're in --form mode.
    """
    import importlib.util
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("_scanner_compute", here / "compute.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SIGNAL_IDS, mod.OVERRIDE_REASON_ENUM


def validate_override_rationale(cell: dict, advisory_hint: dict,
                                signal_ids: frozenset, override_enum: frozenset) -> list:
    """V1.2 gate 6.3 override-explained check.

    Returns list of error strings. Empty list = cell passes.
    Called per scorecard cell. Only enforces when the Phase 4 color differs
    from the paired Phase 3 advisory color — matching colors need no
    rationale.
    """
    errors = []
    phase4_color = (cell or {}).get("color")
    advisory_color = (advisory_hint or {}).get("color")

    # No override → no enforcement (cell-by-cell match is the trivial pass).
    if phase4_color == advisory_color:
        return errors

    # Override detected. Enforce override-explained contract.
    rationale = (cell.get("rationale") or "") if cell else ""
    refs = cell.get("computed_signal_refs") or [] if cell else []
    reason = cell.get("override_reason") if cell else None

    if reason is None:
        errors.append("override_reason required when Phase 4 color differs from advisory")
    elif reason not in override_enum:
        errors.append(f"override_reason must be one of {sorted(override_enum)}; got {reason!r}")

    if len(rationale) < OVERRIDE_RATIONALE_MIN_CHARS:
        errors.append(f"rationale must be ≥{OVERRIDE_RATIONALE_MIN_CHARS} chars when overriding advisory; got {len(rationale)}")

    if not refs:
        errors.append("computed_signal_refs must be non-empty when overriding advisory")
    else:
        unknown = [r for r in refs if r not in signal_ids]
        if unknown:
            errors.append(f"computed_signal_refs contains unknown signal IDs: {unknown}")

    return errors


def check_form(path: Path) -> tuple:
    """V1.2 form.json validator.

    Runs:
      1. jsonschema validation against docs/scan-schema.json
      2. Override-rationale gate (gate 6.3) on each scorecard cell pair

    Returns (errors, warnings). 0 errors = form is V1.2-clean.
    """
    errors = 0
    warnings = 0
    try:
        form = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"  ✗ form.json parse error: {e}")
        return (1, 0)

    # 1. jsonschema
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  ⚠ jsonschema not installed; skipping schema validation")
        warnings += 1
        schema_errors = []
    else:
        schema_path = Path(__file__).resolve().parent / "scan-schema.json"
        schema = json.loads(schema_path.read_text())
        validator = Draft202012Validator(schema)
        schema_errors = list(validator.iter_errors(form))

    if schema_errors:
        errors += len(schema_errors)
        print(f"  ✗ jsonschema: {len(schema_errors)} error(s)")
        for e in schema_errors[:8]:
            loc = "/".join(str(p) for p in e.absolute_path)
            print(f"    - {loc or '<root>'}: {e.message[:160]}")
        if len(schema_errors) > 8:
            print(f"    ... (+{len(schema_errors) - 8} more)")
    else:
        print(f"  ✓ jsonschema: CLEAN")

    # 2. Gate 6.3 override-explained
    signal_ids, override_enum = _load_compute_constants()
    cells = (((form.get("phase_4_structured_llm") or {}).get("scorecard_cells") or {}))
    hints = (((form.get("phase_3_advisory") or {}).get("scorecard_hints") or {}))
    gate_errors = 0
    gate_overrides = 0
    for key in _SCORECARD_QUESTION_KEYS:
        cell = cells.get(key) or {}
        hint = hints.get(key) or {}
        cell_errors = validate_override_rationale(cell, hint, signal_ids, override_enum)
        if cell_errors:
            gate_errors += len(cell_errors)
            phase4_c = cell.get("color")
            advisory_c = hint.get("color")
            print(f"  ✗ gate 6.3 — {key} ({advisory_c} → {phase4_c}):")
            for msg in cell_errors:
                print(f"      - {msg}")
        elif cell.get("color") != hint.get("color") and cell.get("color") is not None:
            gate_overrides += 1
    if gate_errors:
        errors += gate_errors
    else:
        if gate_overrides:
            print(f"  ✓ gate 6.3: CLEAN — {gate_overrides} override(s) all explained")
        else:
            print(f"  ✓ gate 6.3: CLEAN — no overrides")

    return (errors, warnings)


class TagBalanceChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        # Self-closing tags — do nothing
        pass

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            top = self.stack[-1] if self.stack else None
            self.errors.append((self.getpos(), tag, top))


def strip_comments_and_inline_content(html: str) -> str:
    """Remove <!-- ... -->, <style>...</style>, <script>...</script>
       so the tag-balance check doesn't false-positive on tag names
       that appear inside CSS rules or JS strings."""
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def strip_safe_regions(html: str) -> str:
    """For the C4 untrusted-text escape heuristic: strip regions where raw
       '<' is intentional and not a security concern — <code>, <pre>,
       <script>, <style>, HTML comments. What's left is text that should
       have been HTML-escaped if it came from the repo."""
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<code[^>]*>.*?</code>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<pre[^>]*>.*?</pre>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return html


# Regex for valid HTML tag/entity starts. Anything that looks like a tag
# opener '<X' where X is not one of these is suspicious — it could be
# unescaped user input mistaken for a tag, or it could be literal content
# the author meant to show. We flag with a line snippet for human review.
VALID_TAG_START = re.compile(
    r"<\s*/?\s*("
    r"[a-zA-Z][a-zA-Z0-9-]*"   # normal tag name
    r"|!DOCTYPE"
    r")",
    re.IGNORECASE,
)


def find_suspicious_lt(html_stripped: str, raw_html: str):
    """Return list of (line_num, snippet) for '<' characters that don't
       begin a valid HTML tag and aren't inside a stripped safe region.
       Heuristic — can false-positive on legitimate prose like 'N<3' but
       useful as a warning layer."""
    findings = []
    for m in re.finditer(r"<", html_stripped):
        pos = m.start()
        # Check if this '<' starts a valid tag — if so, skip.
        if VALID_TAG_START.match(html_stripped, pos):
            continue
        # Find line number in the stripped text
        line_num = html_stripped.count("\n", 0, pos) + 1
        # Snippet: ±30 chars around
        snippet_start = max(0, pos - 30)
        snippet_end = min(len(html_stripped), pos + 30)
        snippet = html_stripped[snippet_start:snippet_end].replace("\n", "\\n")
        findings.append((line_num, snippet))
    return findings


def find_xss_vectors(html: str):
    """Scan for XSS vectors in the rendered HTML body (outside <style> blocks).
    Returns list of (line_num, description, snippet) tuples.
    Added post-AXIOM audit (V1 fix)."""
    # Strip style blocks — event handlers inside CSS are not XSS
    body_html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)

    findings = []

    # 1. <script> tags in body (outside style blocks — already stripped above)
    #    Allow the known-safe font-size adjustFont script block.
    for m in re.finditer(r"<script[^>]*>(.*?)</script>", body_html, re.DOTALL | re.IGNORECASE):
        script_body = m.group(1)
        # Whitelist: font-size control script (adjustFont only)
        if "adjustFont" in script_body and len(script_body.strip().splitlines()) < 10:
            continue
        line = body_html.count("\n", 0, m.start()) + 1
        findings.append((line, "<script> tag in body", m.group()[:60]))

    # 2. Event handler attributes (on*=)
    for m in re.finditer(r'\bon[a-z]+\s*=\s*["\']', body_html, re.IGNORECASE):
        # Allow onclick in font-controls (known safe pattern)
        ctx_start = max(0, m.start() - 80)
        context = body_html[ctx_start:m.start()]
        if "adjustFont" in body_html[m.start():m.start() + 50]:
            continue
        line = body_html.count("\n", 0, m.start()) + 1
        findings.append((line, f"event handler attribute: {m.group().strip()}", m.group()))

    # 3. javascript: URLs
    for m in re.finditer(r'(?:href|src|action)\s*=\s*["\']?\s*javascript:', body_html, re.IGNORECASE):
        line = body_html.count("\n", 0, m.start()) + 1
        findings.append((line, "javascript: URL", m.group()))

    # 4. Dangerous embed tags
    for m in re.finditer(r"<(iframe|embed|object|applet|form)[\s>]", body_html, re.IGNORECASE):
        line = body_html.count("\n", 0, m.start()) + 1
        findings.append((line, f"dangerous <{m.group(1)}> tag", m.group()))

    # 5. data: URLs in src attributes (can execute JS)
    for m in re.finditer(r'src\s*=\s*["\']?\s*data:', body_html, re.IGNORECASE):
        line = body_html.count("\n", 0, m.start()) + 1
        findings.append((line, "data: URL in src attribute", m.group()))

    return findings


def check(path: Path, mode: str = "default") -> int:
    raw = path.read_text(encoding="utf-8")
    clean = strip_comments_and_inline_content(raw)

    # 1. Tag balance
    checker = TagBalanceChecker()
    checker.feed(clean)

    # 2. EXAMPLE markers
    starts = raw.count("<!-- EXAMPLE-START:")
    ends = raw.count("<!-- EXAMPLE-END:")

    # 3. Placeholder tokens
    placeholders = raw.count("{{")

    # 4. Inline style= attributes on rendered elements
    inline_styles = len(re.findall(r'\bstyle\s*=\s*"', clean))

    # 5. px font-sizes in the <style> block (stay rem-only per S8-8)
    styleblock = ""
    m = re.search(r"<style[^>]*>(.*?)</style>", raw, flags=re.DOTALL | re.IGNORECASE)
    if m:
        styleblock = m.group(1)
    px_fontsizes = re.findall(r"font-size\s*:\s*\d+(?:\.\d+)?px", styleblock)

    total_errors = 0
    warnings = 0

    mode_label = {"default": "permissive", "report": "rendered-report (strict)", "template": "template"}[mode]
    print(f"=== Validating {path.name} ({raw.count(chr(10))+1} lines, mode: {mode_label}) ===")

    # --- Always-on checks ---

    # Tag balance
    if checker.stack:
        print(f"  ✗ {len(checker.stack)} unclosed tags remaining")
        for tag, (line, col) in checker.stack[-5:]:
            print(f"      <{tag}> opened at line {line}")
        total_errors += 1
    else:
        print(f"  ✓ All tags balanced (0 unclosed)")

    if checker.errors:
        print(f"  ✗ {len(checker.errors)} mismatched close tags")
        for (line, col), tag, top in checker.errors[:5]:
            top_str = f"{top[0]} (line {top[1][0]})" if top else "empty stack"
            print(f"      line {line}: </{tag}> but stack top is {top_str}")
        total_errors += 1
    else:
        print(f"  ✓ No mismatched close tags")

    # EXAMPLE marker balance (always checked)
    if starts == ends:
        print(f"  ✓ EXAMPLE markers balanced ({starts} start / {ends} end)")
    else:
        print(f"  ✗ EXAMPLE markers unbalanced ({starts} start / {ends} end)")
        total_errors += 1

    # Inline styles (V2.3 S8-1)
    if inline_styles == 0:
        print(f"  ✓ Zero inline style='' attributes on rendered elements")
    else:
        print(f"  ✗ {inline_styles} inline style='' attribute(s) found — use utility classes instead")
        total_errors += 1

    # px font-sizes (V2.3 S8-8)
    if not px_fontsizes:
        print(f"  ✓ No px font-sizes in <style> block (rem only)")
    else:
        print(f"  ✗ {len(px_fontsizes)} px font-size(s) in <style> — should be rem for A+/A- scaling")
        for decl in px_fontsizes[:5]:
            print(f"      {decl}")
        total_errors += 1

    # --- Mode-specific checks ---

    if mode == "report":
        # Strict: rendered reports must have zero placeholders & zero markers
        if placeholders == 0:
            print(f"  ✓ Zero {{{{PLACEHOLDER}}}} tokens remaining (rendered-report check)")
        else:
            print(f"  ✗ {placeholders} {{{{PLACEHOLDER}}}} token(s) remaining — report is not fully rendered")
            total_errors += 1

        if starts == 0 and ends == 0:
            print(f"  ✓ Zero EXAMPLE-START/END markers remaining (rendered-report check)")
        else:
            print(f"  ✗ {starts + ends} EXAMPLE marker(s) remaining — template scaffolding not stripped")
            total_errors += 1

        # XSS security check (V1 fix — AXIOM audit)
        xss_findings = find_xss_vectors(raw)
        if not xss_findings:
            print(f"  ✓ No XSS vectors detected (script tags, event handlers, javascript: URLs, dangerous embeds)")
        else:
            print(f"  ✗ {len(xss_findings)} XSS vector(s) detected — report contains potentially dangerous content")
            for line, desc, snippet in xss_findings[:10]:
                print(f"      line ~{line}: {desc}")
            total_errors += 1

        # C4: repo-text escape heuristic
        safe_stripped = strip_safe_regions(raw)
        suspicious = find_suspicious_lt(safe_stripped, raw)
        if not suspicious:
            print(f"  ✓ No suspicious unescaped '<' outside code/pre/script/style/comments")
        else:
            print(f"  ⚠ {len(suspicious)} possibly-unescaped '<' character(s) outside safe regions (heuristic — may be false positives)")
            for line, snippet in suspicious[:5]:
                print(f"      ~line {line}: ...{snippet}...")
            print(f"      If these come from repo content (PR titles, issue titles, commit messages), HTML-escape them per prompt line 810.")
            warnings += 1

    elif mode == "template":
        # Template must have placeholders and markers (else it's not a template)
        if placeholders > 0:
            print(f"  ✓ Placeholders present: {placeholders} (template check)")
        else:
            print(f"  ✗ Zero {{{{PLACEHOLDER}}}} tokens — this is not a template (rendered-report in template path?)")
            total_errors += 1

        if starts > 0 and ends > 0:
            print(f"  ✓ EXAMPLE markers present: {starts} start / {ends} end (template check)")
        else:
            print(f"  ✗ No EXAMPLE markers — this is not a template")
            total_errors += 1

        # O4: CSS sync check — verify template <style> contains the canonical CSS
        css_file = path.parent / "scanner-design-system.css"
        if css_file.exists():
            canonical_css = css_file.read_text(encoding="utf-8").strip()
            if canonical_css in styleblock:
                print(f"  ✓ Template CSS matches scanner-design-system.css ({len(canonical_css.splitlines())} lines)")
            else:
                print(f"  ✗ Template CSS has DRIFTED from scanner-design-system.css — re-sync required")
                total_errors += 1
        else:
            print(f"  ⚠ scanner-design-system.css not found alongside template — cannot verify CSS sync")
            warnings += 1

    else:
        # Permissive default — just inform
        print(f"  ℹ {{{{PLACEHOLDER}}}} token count: {placeholders} (info; use --report or --template for strict check)")

    return total_errors, warnings


def check_markdown(path: Path) -> int:
    """B3: Validate a Markdown scan report has required sections and minimum content."""
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    total_errors = 0
    warnings = 0

    print(f"=== Validating {path.name} ({len(lines)} lines, mode: markdown) ===")

    # Minimum line count — a real scan report is at least 100 lines
    if len(lines) >= 100:
        print(f"  ✓ Line count: {len(lines)} (minimum 100)")
    else:
        print(f"  ✗ Only {len(lines)} lines — expected at least 100 for a scan report")
        total_errors += 1

    # Required section headers — must match the numbered section pattern from the prompt
    required_sections = [
        ("Verdict or Executive Summary", r"(?i)#+ .*(verdict|executive\s+summary)"),
        ("Scorecard", r"(?i)#+ .*scorecard"),
        ("What should I do (Section 01)", r"(?i)#+ .*(what should i do|what to do|01)"),
        ("What we found (Section 02)", r"(?i)#+ .*(what we found|finding|02 )"),
        ("Executable file inventory (02A)", r"(?i)#+ .*(executable|inventory|02a)"),
        ("Timeline (Section 04)", r"(?i)#+ .*(timeline|04)"),
        ("Repo vitals (Section 05)", r"(?i)#+ .*(repo vital|vital|05)"),
        ("Investigation coverage (Section 06)", r"(?i)#+ .*(coverage|06)"),
        ("Evidence (Section 07)", r"(?i)#+ .*(evidence|07)"),
        ("How this scan works (Section 08)", r"(?i)#+ .*(how this scan works|methodology|08)"),
    ]
    for name, pattern in required_sections:
        if re.search(pattern, raw):
            print(f"  ✓ Required section found: {name}")
        else:
            print(f"  ✗ Missing required section: {name}")
            total_errors += 1

    # Section numbering check — sections should use "## 0N ·" pattern
    numbered_sections = re.findall(r"^## 0[0-9A-Za-z]+ ·", raw, re.MULTILINE)
    if len(numbered_sections) >= 7:
        print(f"  ✓ Section numbering: {len(numbered_sections)} numbered sections (## 0N · pattern)")
    elif len(numbered_sections) >= 1:
        print(f"  ⚠ Only {len(numbered_sections)} numbered sections found (expected 7+). Some sections may be missing numbers.")
        warnings += 1
    else:
        print(f"  ✗ No numbered sections (## 0N · pattern) found — report structure does not match template")
        total_errors += 1

    # Evidence structure check — priority grouping
    has_priority_evidence = bool(re.search(r"(?i)(priority evidence|START HERE|★)", raw))
    if has_priority_evidence:
        print(f"  ✓ Evidence priority grouping present (★ / START HERE / Priority evidence)")
    else:
        print(f"  ⚠ No evidence priority grouping found — evidence appendix should use ★ Priority / Context / Positives groups")
        warnings += 1

    # Must have at least one verdict keyword
    if re.search(r"(?i)(critical|caution|warning|clean|informational)", raw):
        print(f"  ✓ Verdict/severity keywords present")
    else:
        print(f"  ✗ No verdict or severity keywords found")
        total_errors += 1

    # Verdict-severity coherence check: "Clean" verdict with Warning/Critical findings is invalid.
    # A report cannot say the repo is clean while also flagging warnings.
    has_clean_verdict = bool(re.search(r"(?i)verdict[:\s]*clean", raw))
    has_warning_findings = bool(re.search(r"(?i)\bwarning\b", raw))
    has_critical_findings = bool(re.search(r"(?i)\bcritical\b", raw))
    if has_clean_verdict and (has_warning_findings or has_critical_findings):
        severity = "Critical" if has_critical_findings else "Warning"
        print(f"  ✗ Verdict says 'Clean' but report contains {severity} findings — verdict must be Caution or higher when warnings exist")
        total_errors += 1
    elif has_clean_verdict:
        print(f"  ✓ Clean verdict with no Warning/Critical findings (coherent)")
    else:
        print(f"  ✓ Verdict-severity coherence OK")

    # V2.4 scorecard question contract check — the 4 canonical questions
    canonical_questions = [
        "Does anyone check the code?",
        "Do they fix problems quickly?",
        "Do they tell you about problems?",
        "Is it safe out of the box?",
    ]
    found_questions = []
    for q in canonical_questions:
        if q.lower() in raw.lower():
            found_questions.append(q)
    if len(found_questions) == 4:
        print(f"  ✓ All 4 canonical scorecard questions present")
    elif len(found_questions) > 0:
        missing = [q for q in canonical_questions if q not in found_questions]
        print(f"  ✗ Scorecard contract break: missing {len(missing)} canonical question(s): {missing}")
        total_errors += 1
    else:
        print(f"  ⚠ No canonical scorecard questions found (may be a non-standard report)")
        warnings += 1

    if total_errors == 0:
        print(f"\n✓ {path.name} is clean.")
    else:
        print(f"\n✗ {path.name} has {total_errors} validation issue(s).")

    return total_errors, warnings


def check_parity(md_path: Path, html_path: Path) -> tuple:
    """PD2: Check that MD and HTML reports contain the same structural content.
    The MD is canonical — HTML may not add findings absent from MD.

    Diagnostic categories:
      ERROR — real MD-canonical break: HTML adds a finding not in MD, verdict mismatch,
              canonical scorecard question missing. Exit 1.
      WARNING — structural ambiguity: could not extract verdict. Exit 0.
      INFO — authoring/rendering variation (asymmetric parity where MD has F-IDs not in HTML
             but HTML adds nothing; compact-bundle style; section-name rendering differences).
             Not a contamination signal; MD-canonical is one-way (HTML cannot add; MD may have
             extras). Emitted as `ℹ Note:` so FN-5 grep on WARNING: does not STOP on them.
    """
    md_raw = md_path.read_text(encoding="utf-8")
    html_raw = html_path.read_text(encoding="utf-8")
    total_errors = 0
    warnings = 0
    infos = 0

    print(f"=== Parity check: {md_path.name} ↔ {html_path.name} ===")

    # 1. Finding IDs — extract from both, MD is canonical.
    # F-ID pattern allows digits, hyphenated words, OR dots (e.g. F-crates.io).
    # MD h3 separator allows em/en/hyphen OR &middot;/· (hermes-agent style).
    fid_pat = r"F\d+|F-[\w.-]+"
    md_findings = set(
        re.findall(
            rf"###\s+({fid_pat})\s*(?:[—–-]|&middot;|·)",
            md_raw,
        )
    )
    # HTML findings: look for finding IDs adjacent to severity/status markers in body text.
    # Strip CSS/style/script/comments first to avoid false positives from rule references.
    html_body = re.sub(r"<style[^>]*>.*?</style>", "", html_raw, flags=re.DOTALL | re.IGNORECASE)
    html_body = re.sub(r"<!--.*?-->", "", html_body, flags=re.DOTALL)
    # NOTE: do NOT strip /* */ here — CSS comments are already removed with the <style>
    # block above. A global /\*.*?\*/ strip matches shell globs (e.g. /plugins/*/hooks/*.js)
    # and legitimate code comments in evidence text, eating finding cards. Found during
    # Step F parity work against caveman fixture.

    # HTML extraction uses two buckets:
    #   finding_card_ids — from h3 inside finding-card context (prefix or tail-parens).
    #     These are the CANONICAL HTML finding set; must be subset of MD.
    #   reference_ids — from exhibit-tags and severity-adjacent text in synthesis layers.
    #     These are allowed to reference rule-IDs or compound finding groups (e.g.
    #     "Distribution · F1+F2" summarizes a cluster without implying an F1 finding card).
    #     Used only to warn on MD findings missing from HTML.
    finding_card_ids = set()
    reference_ids = set()

    # Pattern 1 (reference): exhibit-item-tag content like "Dependabot alerts · F1" or "· F0"
    reference_ids |= set(re.findall(
        rf'exhibit-item-tag[^<]*?(?:·|&middot;)\s*({fid_pat})',
        html_body,
    ))
    # Pattern 2 (reference): finding IDs with severity marker in heading-like context
    reference_ids |= set(re.findall(
        rf"({fid_pat})\s*(?:—|&mdash;|–)\s*(?:Warning|Critical|OK|Info)",
        html_body,
    ))
    # Pattern 3 + 4 (finding-card): h3 inside finding-cards. Prefix "F0 — Title" OR
    # tail "(F0 / C20)" / "(F11 + F14)". Match LAST parens at end to avoid mid-prose.
    # V2.4 HTMLs share the `finding-card` CSS class between Finding cards and Evidence
    # cards. Skip Evidence cards so their h3s don't get treated as finding-card IDs —
    # detect by looking for the nearest preceding `<span class="tag…-tag">Evidence N</span>`.
    tag_re = re.compile(r'<span\s+class="tag[^"]*-tag[^"]*"[^>]*>([^<]+)</span>',
                        re.IGNORECASE)
    for h3_match in re.finditer(r"<h3[^>]*>(.*?)</h3>", html_body,
                                flags=re.DOTALL | re.IGNORECASE):
        preceding = html_body[max(0, h3_match.start() - 1000):h3_match.start()]
        preceding_tags = tag_re.findall(preceding)
        if preceding_tags and re.match(r'Evidence\s+\d+', preceding_tags[-1].strip()):
            continue
        h3_text = re.sub(r"<[^>]+>", "", h3_match.group(1)).strip()
        m = re.match(rf"({fid_pat})\s*(?:&mdash;|—|–|-)", h3_text)
        if m:
            finding_card_ids.add(m.group(1))
        tail_paren = re.search(r"\(([^()]*)\)\s*$", h3_text)
        if tail_paren:
            tail_inner = tail_paren.group(1).strip()
            # Only treat tail parens as a finding-card ID when the parens contain
            # an ID expression ONLY — "F-ID" or "F-ID / rule-ID", no prose. Reject:
            #   "(F11 dual metric)" — prose word "dual metric"
            #   "(F11 + F14)"       — rule-ID cluster reference (NOT finding-card ID).
            #                         Archon h3 "Governance: ... (F11 + F14)" references
            #                         catalog rules F11/F14, not finding cards. False-
            #                         positive compound extraction attempted 2026-04-20
            #                         was reverted after it flagged MD-canonical violations.
            #   "(densest F7 surface in catalog)" — prose mentioning F-ID
            tail_id_only = re.fullmatch(
                rf"({fid_pat})(?:\s*/\s*[A-Z]\d+)?", tail_inner
            )
            if tail_id_only:
                finding_card_ids.add(tail_id_only.group(1))

    html_findings = finding_card_ids | reference_ids

    if md_findings:
        card_only = finding_card_ids - md_findings
        md_missing_from_html = md_findings - html_findings
        if not card_only and not md_missing_from_html:
            print(f"  ✓ Finding IDs match: {sorted(md_findings)}")
        else:
            if card_only:
                print(f"  ✗ HTML finding-card IDs NOT in MD (violates MD-canonical rule): {sorted(card_only)}")
                total_errors += 1
            if md_missing_from_html:
                # MD-canonical is asymmetric: HTML cannot add findings, but MD may have F-IDs
                # that are not explicitly encoded in HTML h3 tags (authoring choice — HTML
                # finding cards use prose titles, or compound tail parens like "(F11 + F14)"
                # that the regex rejects). Not a contamination signal when no HTML extras
                # exist (card_only is empty). Emit as informational note.
                print(f"  ℹ Note: MD findings not extractable from HTML: {sorted(md_missing_from_html)} (authoring variation; MD-canonical not violated since no HTML extras)")
                infos += 1
    else:
        # Compact-bundle style (zero F-IDs in MD FINDINGS SUMMARY, e.g. zustand-v3 style,
        # U-10 approved). Not a contamination signal.
        print(f"  ℹ Note: Could not extract finding IDs from MD (compact-bundle style or prose-only summary)")
        infos += 1

    # 2. Scorecard questions — both MD and HTML must contain the canonical 4-question
    # set defined in docs/repo-deep-dive-prompt.md §"Trust Scorecard" (~line 743).
    # Non-canonical wording (e.g. "Can you trust the maintainers?") is authorial drift
    # and must be flagged as a content bug, not accepted as a valid alternate.
    canonical_qs = {
        "Does anyone check the code?",
        "Do they fix problems quickly?",
        "Do they tell you about problems?",
        "Is it safe out of the box?",
    }
    md_qs = {q for q in canonical_qs if q.lower() in md_raw.lower()}
    html_qs = {q for q in canonical_qs if q.lower() in html_raw.lower()}
    if len(md_qs) == 4 and len(html_qs) == 4:
        print(f"  ✓ Scorecard questions match (4 canonical questions in both)")
    else:
        if len(md_qs) < 4:
            missing_md = canonical_qs - md_qs
            print(f"  ✗ MD scorecard missing canonical question(s): {sorted(missing_md)}")
            total_errors += 1
        if len(html_qs) < 4:
            missing_html = canonical_qs - html_qs
            print(f"  ✗ HTML scorecard missing canonical question(s): {sorted(missing_html)}")
            total_errors += 1

    # 3. Verdict level — both must agree
    # MD verdict: look for "Verdict: X" or "Verdict | **X**" in header area
    md_primary = re.search(r"(?i)verdict[:\s|*]+(clean|caution|critical)", md_raw[:1500])
    # HTML verdict: look for verdict-banner class with verdict level. Search html_body
    # (CSS stripped) so CSS rules like `.verdict-banner.critical { ... }` can't shadow
    # the actual rendered `<div class="verdict-banner caution">`.
    html_primary = re.search(r'verdict-banner\s+(clean|caution|critical)', html_body, re.IGNORECASE)
    if not html_primary:
        html_primary = re.search(r"(?i)class=\"[^\"]*\b(clean|caution|critical)\b", html_body[:5000])
    if md_primary and html_primary:
        if md_primary.group(1).lower() == html_primary.group(1).lower():
            print(f"  ✓ Verdict level matches: {md_primary.group(1)}")
        else:
            print(f"  ✗ Verdict mismatch — MD: {md_primary.group(1)}, HTML: {html_primary.group(1)}")
            total_errors += 1
    elif md_primary:
        print(f"  ⚠ WARNING: Could not extract verdict from HTML for comparison")
        warnings += 1
    else:
        print(f"  ⚠ WARNING: Could not extract verdict from MD for comparison")
        warnings += 1

    # 4. Section presence — key sections should be in both.
    # Section-name rendering variations (e.g., MD "## How this scan works" vs HTML
    # "<section class='methodology'>") are authoring/template choices, not content
    # breaks. Classify as info, not warning, so FN-5 pre-flight gate does not STOP
    # on template evolution.
    key_sections = ["what should i do", "what we found", "evidence", "coverage",
                    "timeline", "repo vital", "how this scan works"]
    for section in key_sections:
        in_md = section in md_raw.lower()
        in_html = section in html_raw.lower()
        if in_md and not in_html:
            print(f"  ℹ Note: Section '{section}' in MD but not found in HTML (rendering variation)")
            infos += 1

    if total_errors == 0 and warnings == 0 and infos == 0:
        print(f"\n✓ Parity check clean — MD and HTML are structurally consistent.")
    elif total_errors == 0:
        parts = []
        if warnings:
            parts.append(f"{warnings} warning(s)")
        if infos:
            parts.append(f"{infos} info note(s)")
        print(f"\n✓ Parity check clean (with {', '.join(parts)}).")
    else:
        print(f"\n✗ Parity check found {total_errors} error(s).")

    return total_errors, warnings


# ---------------------------------------------------------------------------
# U-5/PD3: Bundle/citation validator
#
# Audits a `findings-bundle.md` against the Operator Guide's citation-discipline
# rule (§11.1) and the pre-render checklist (§9.2.1). Queued to build before the
# first live Step G scan (per docs/External-Board-Reviews/041826-step-g-kickoff/
# CONSOLIDATION.md — DeepSeek R3 compromise: Step G acceptance criterion).
# ---------------------------------------------------------------------------

# Interpretive verbs per §7.2 Pattern recognition rule. Evidence sections MUST
# NOT contain these; Pattern recognition bullets MUST contain at least one.
INTERPRETIVE_VERBS = [
    "resembles", "resemble",
    "suggests", "suggest",
    "consistent with",
    "pattern-matches to", "pattern matches to",
    "reminiscent of",
    "plausibly indicates", "plausibly indicate",
    "looks like", "look like",
    "behaves similarly to", "behave similarly to",
]

# Synthesis-region heading keywords (case-insensitive substring match). Anything
# else that isn't "Pattern recognition" falls into evidence.
SYNTHESIS_KEYWORDS = [
    "findings summary", "key findings",
    "positive signals",
    "proposed verdict", "verdict",
    "proposed scorecard", "scorecard",
    "catalog metadata",
]

FID_PAT = r"F\d+|F-[\w.-]+"


def _interpretive_verb_hits(text: str) -> list:
    """Return the interpretive verbs found in text (preserving duplicates unique)."""
    hits = []
    for verb in INTERPRETIVE_VERBS:
        # Word-boundary on single words; literal-phrase match for multi-word verbs.
        pat = rf"\b{re.escape(verb)}\b" if " " not in verb else re.escape(verb)
        if re.search(pat, text, re.IGNORECASE):
            hits.append(verb)
    return hits


def parse_bundle_regions(bundle_text: str) -> dict:
    """Split a findings-bundle.md into {evidence, pattern, synthesis} regions.

    Classification:
      - heading starts with "Pattern recognition" → pattern
      - heading matches a SYNTHESIS_KEYWORDS substring → synthesis
      - everything else under ## → evidence
    """
    regions: dict = {"evidence": {}, "pattern": "", "synthesis": {}}
    sections = re.split(r"^## ", bundle_text, flags=re.MULTILINE)
    for section in sections[1:]:  # skip preamble
        head_and_body = section.split("\n", 1)
        heading = head_and_body[0].strip()
        body = head_and_body[1] if len(head_and_body) > 1 else ""
        heading_lower = heading.lower()
        if heading_lower.startswith("pattern recognition"):
            regions["pattern"] = body
        elif (heading_lower == "findings"
              or any(kw in heading_lower for kw in SYNTHESIS_KEYWORDS)):
            # "## Findings" alone is compact-bundle synthesis (zustand-v3 style);
            # keyword substring match covers "FINDINGS SUMMARY", "Proposed verdict", etc.
            regions["synthesis"][heading] = body
        else:
            regions["evidence"][heading] = body
    return regions


def check_bundle(path) -> tuple:
    """U-5/PD3: Audit findings-bundle.md for citation discipline.

    Checks:
      1. Evidence sections contain no interpretive verbs (facts-only rule).
      2. Pattern recognition bullets (if present) each contain an interpretive
         verb (inference-is-tagged rule).
      3. FINDINGS SUMMARY section exists and is non-empty.
      4. Proposed verdict cites at least one F-ID or names a severity level.
      5. F-IDs referenced in synthesis outside FINDINGS SUMMARY also appear in
         FINDINGS SUMMARY (no orphan finding references).

    Returns: (errors, warnings).
    """
    text = path.read_text(encoding="utf-8")
    regions = parse_bundle_regions(text)
    errors = 0
    warnings = 0

    print(f"=== Bundle check: {path.name} ===")

    # 1. Evidence discipline
    evidence_verb_leaks = []
    for section_name, body in regions["evidence"].items():
        hits = _interpretive_verb_hits(body)
        if hits:
            evidence_verb_leaks.append((section_name, hits))
    if evidence_verb_leaks:
        for name, hits in evidence_verb_leaks:
            print(f"  ✗ Evidence section '{name}' uses interpretive verb(s): {sorted(set(hits))}")
        errors += len(evidence_verb_leaks)
    else:
        print(f"  ✓ Evidence sections ({len(regions['evidence'])}): facts-only, no interpretive verbs")

    # 2. Pattern recognition discipline
    if regions["pattern"].strip():
        # Match bullet markers followed by whitespace, so horizontal rules
        # (`---`) and emphasis syntax (`**text**`) don't count as bullets.
        bullets = [ln.strip() for ln in regions["pattern"].split("\n")
                   if re.match(r"^[-*]\s+\S", ln.strip())]
        no_verb = [b for b in bullets if not _interpretive_verb_hits(b)]
        if no_verb:
            print(f"  ✗ Pattern recognition: {len(no_verb)} of {len(bullets)} bullet(s) missing interpretive verb")
            for b in no_verb[:3]:
                snippet = b[:90] + "…" if len(b) > 90 else b
                print(f"      → {snippet}")
            errors += 1
        else:
            print(f"  ✓ Pattern recognition: all {len(bullets)} bullet(s) tagged with interpretive verb")
    else:
        print(f"  ℹ No Pattern recognition section (inference segregation not exercised)")

    # 3. FINDINGS SUMMARY exists + F-ID extraction
    findings_heading = None
    findings_body = ""
    for k, v in regions["synthesis"].items():
        kl = k.lower()
        if "findings summary" in kl or kl.startswith("key findings") or kl == "findings":
            findings_heading = k
            findings_body = v
            break
    if not findings_heading or not findings_body.strip():
        print(f"  ✗ FINDINGS SUMMARY section missing or empty")
        errors += 1
    else:
        summary_fids = set(re.findall(FID_PAT, findings_heading + "\n" + findings_body))
        print(f"  ✓ FINDINGS SUMMARY present: {sorted(summary_fids) if summary_fids else '(no F-IDs parsed)'}")

    findings_fids = set(re.findall(FID_PAT, (findings_heading or "") + "\n" + findings_body))

    # 4. Proposed verdict cites F-IDs or severity
    verdict_heading = None
    verdict_body = ""
    for k, v in regions["synthesis"].items():
        if "verdict" in k.lower():
            verdict_heading = k
            verdict_body = v
            break
    if not verdict_heading:
        print(f"  ✗ Proposed verdict section missing")
        errors += 1
    else:
        combined = verdict_heading + "\n" + verdict_body
        verdict_fids = set(re.findall(FID_PAT, combined))
        has_severity = bool(re.search(
            r"(?i)\b(clean|caution|critical|warning|info|ok|amber|green|red)\b",
            combined,
        ))
        if verdict_fids:
            print(f"  ✓ Proposed verdict cites F-IDs: {sorted(verdict_fids)}")
        elif has_severity:
            # Compact-bundle style: if FINDINGS SUMMARY also has zero F-IDs, the
            # entire bundle is prose-synthesis (zustand-v3 pattern, U-10 approved).
            # Verdict without F-IDs is consistent with the shape, not a discipline
            # break. Classify as info. Otherwise (FINDINGS SUMMARY has F-IDs but
            # verdict doesn't), the asymmetry is a citation gap worth flagging.
            if not findings_fids:
                print(f"  ℹ Note: Proposed verdict names severity without F-IDs (compact-bundle style; consistent with F-ID-free FINDINGS SUMMARY)")
            else:
                print(f"  ⚠ WARNING: Proposed verdict names severity but no specific F-IDs")
                warnings += 1
        else:
            print(f"  ✗ Proposed verdict does not cite F-IDs or severity levels")
            errors += 1

    # 5. Orphan F-IDs (referenced in synthesis but not in FINDINGS SUMMARY)
    orphan_fids = set()
    for k, v in regions["synthesis"].items():
        if k == findings_heading:
            continue
        orphan_fids |= set(re.findall(FID_PAT, k + "\n" + v))
    orphan_fids -= findings_fids
    if orphan_fids:
        print(f"  ✗ F-IDs referenced in synthesis but not in FINDINGS SUMMARY: {sorted(orphan_fids)}")
        errors += 1

    # Summary line
    if errors == 0 and warnings == 0:
        print(f"\n✓ Bundle check clean — {path.name} passes citation discipline.")
    elif errors == 0:
        print(f"\n✓ Bundle check clean (with {warnings} warning(s)).")
    else:
        print(f"\n✗ Bundle check found {errors} error(s).")

    return errors, warnings


def main():
    argv = sys.argv[1:]
    mode = "default"
    if argv and argv[0] == "--report":
        mode = "report"
        argv = argv[1:]
    elif argv and argv[0] == "--template":
        mode = "template"
        argv = argv[1:]
    elif argv and argv[0] == "--markdown":
        mode = "markdown"
        argv = argv[1:]
    elif argv and argv[0] == "--parity":
        mode = "parity"
        argv = argv[1:]
    elif argv and argv[0] == "--bundle":
        mode = "bundle"
        argv = argv[1:]
    elif argv and argv[0] == "--form":
        mode = "form"
        argv = argv[1:]

    if mode == "parity":
        if len(argv) != 2:
            print("Usage: python3 validate-scanner-report.py --parity <md_file> <html_file>")
            return 2
        md_path = Path(argv[0])
        html_path = Path(argv[1])
        if not md_path.exists():
            print(f"ERROR: MD file not found — {md_path}")
            return 2
        if not html_path.exists():
            print(f"ERROR: HTML file not found — {html_path}")
            return 2
        errors, warnings = check_parity(md_path, html_path)
        if errors == 0:
            return 0
        return 1

    if mode == "bundle":
        if len(argv) != 1:
            print("Usage: python3 validate-scanner-report.py --bundle <findings-bundle.md>")
            return 2
        bundle_path = Path(argv[0])
        if not bundle_path.exists():
            print(f"ERROR: bundle file not found — {bundle_path}")
            return 2
        errors, warnings = check_bundle(bundle_path)
        if errors == 0:
            return 0
        return 1

    if mode == "form":
        if len(argv) != 1:
            print("Usage: python3 validate-scanner-report.py --form <form.json>")
            return 2
        form_path = Path(argv[0])
        if not form_path.exists():
            print(f"ERROR: form file not found — {form_path}")
            return 2
        print(f"Validating {form_path.name} against V1.2 schema + gate 6.3 override-explained...")
        errors, warnings = check_form(form_path)
        if errors == 0:
            print(f"\n✓ {form_path.name} is V1.2-clean"
                  + (f" ({warnings} warning(s))" if warnings else "."))
            return 0
        print(f"\n✗ {form_path.name}: {errors} error(s)"
              + (f", {warnings} warning(s)" if warnings else ""))
        return 1

    if len(argv) != 1:
        print(__doc__)
        return 2

    path = Path(argv[0])
    if not path.exists():
        print(f"ERROR: file not found — {path}")
        return 2

    if mode == "markdown":
        errors, warnings = check_markdown(path)
    else:
        errors, warnings = check(path, mode)

    if errors == 0:
        if warnings > 0:
            print(f"\n✓ {path.name} is clean (with {warnings} warning(s) — review above).")
        else:
            print(f"\n✓ {path.name} is clean.")
        return 0
    else:
        print(f"\n✗ {path.name} has {errors} validation issue(s).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
