#!/usr/bin/env python3
"""
validate-scanner-report.py — HTML structural + template-alignment validator
for GitHub Scanner reports, the scan template, and markdown scan reports.

Usage:
  python3 validate-scanner-report.py [--report | --template | --markdown] <path>

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

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID_TAGS = {"br", "img", "meta", "link", "hr", "input", "col", "area", "base",
             "embed", "source", "track", "wbr"}


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

    # Required section headers (case-insensitive search in first 2 heading levels)
    required_sections = [
        ("Verdict or Executive Summary", r"(?i)#+ .*(verdict|executive\s+summary)"),
        ("Findings", r"(?i)#+ .*finding"),
        ("Evidence", r"(?i)#+ .*evidence"),
        ("Scorecard", r"(?i)#+ .*scorecard"),
    ]
    for name, pattern in required_sections:
        if re.search(pattern, raw):
            print(f"  ✓ Required section found: {name}")
        else:
            print(f"  ✗ Missing required section: {name}")
            total_errors += 1

    # Must have at least one verdict keyword
    if re.search(r"(?i)(critical|caution|warning|clean|informational)", raw):
        print(f"  ✓ Verdict/severity keywords present")
    else:
        print(f"  ✗ No verdict or severity keywords found")
        total_errors += 1

    if total_errors == 0:
        print(f"\n✓ {path.name} is clean.")
    else:
        print(f"\n✗ {path.name} has {total_errors} validation issue(s).")

    return total_errors, warnings


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
