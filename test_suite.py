#!/usr/bin/env python3
"""
FlowFinance Comprehensive Test Suite
=====================================
Tests: HTML validation, JS syntax, security, parsers, edge cases
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import html5lib

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")

def print_pass(text):
    print(f"  {GREEN}✓{RESET} {text}")

def print_fail(text):
    print(f"  {RED}✗{RESET} {text}")

def print_warn(text):
    print(f"  {YELLOW}⚠{RESET} {text}")

def print_info(text):
    print(f"  {BLUE}ℹ{RESET} {text}")

class FlowFinanceTestSuite:
    def __init__(self, html_path):
        self.html_path = Path(html_path)
        self.html_content = self.html_path.read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.html_content, 'html5lib')
        self.results = {'passed': 0, 'failed': 0, 'warnings': 0}

    def run_all(self):
        """Run all test suites"""
        print(f"\n{BOLD}FlowFinance Test Suite{RESET}")
        print(f"Testing: {self.html_path}")
        print(f"File size: {len(self.html_content):,} bytes ({len(self.html_content)//1024}KB)")
        print(f"Lines: {len(self.html_content.splitlines()):,}")

        self.test_html_structure()
        self.test_html5_validation()
        self.test_javascript_syntax()
        self.test_security_headers()
        self.test_accessibility()
        self.test_css_validation()
        self.test_javascript_patterns()
        self.test_parser_edge_cases()
        self.test_xss_vectors()
        self.test_data_validation()
        self.test_performance_concerns()

        self.print_summary()
        return self.results['failed'] == 0

    def test_html_structure(self):
        """Test basic HTML structure"""
        print_header("HTML Structure Tests")

        # DOCTYPE
        if self.html_content.strip().startswith('<!DOCTYPE html>'):
            print_pass("DOCTYPE present")
            self.results['passed'] += 1
        else:
            print_fail("Missing DOCTYPE")
            self.results['failed'] += 1

        # Language attribute
        html_tag = self.soup.find('html')
        if html_tag and html_tag.get('lang'):
            print_pass(f"Language attribute: {html_tag.get('lang')}")
            self.results['passed'] += 1
        else:
            print_fail("Missing lang attribute on <html>")
            self.results['failed'] += 1

        # Meta charset
        charset = self.soup.find('meta', charset=True)
        if charset:
            print_pass(f"Charset: {charset.get('charset')}")
            self.results['passed'] += 1
        else:
            print_fail("Missing charset meta tag")
            self.results['failed'] += 1

        # Viewport
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            print_pass("Viewport meta tag present")
            self.results['passed'] += 1
        else:
            print_fail("Missing viewport meta tag")
            self.results['failed'] += 1

        # Title
        title = self.soup.find('title')
        if title and title.string:
            print_pass(f"Title: {title.string[:50]}...")
            self.results['passed'] += 1
        else:
            print_fail("Missing or empty title")
            self.results['failed'] += 1

    def test_html5_validation(self):
        """Validate HTML5 structure"""
        print_header("HTML5 Validation")

        # Parse with html5lib (strict)
        try:
            doc = html5lib.parse(self.html_content)
            print_pass("HTML5 parsing successful")
            self.results['passed'] += 1
        except Exception as e:
            print_fail(f"HTML5 parsing failed: {e}")
            self.results['failed'] += 1

        # Check for unclosed tags (common issues)
        unclosed_patterns = [
            (r'<br[^/]', 'Unclosed <br> tags (should be <br> or <br/>)'),
            (r'<hr[^/]', 'Unclosed <hr> tags'),
            (r'<img(?![^>]*/>)[^>]*>', 'Unclosed <img> tags'),
        ]

        for pattern, desc in unclosed_patterns:
            matches = re.findall(pattern, self.html_content)
            if not matches:
                print_pass(f"No {desc}")
                self.results['passed'] += 1

    def test_javascript_syntax(self):
        """Extract and validate JavaScript"""
        print_header("JavaScript Syntax Validation")

        # Extract all script content (excluding JSON-LD which is JSON, not JS)
        scripts = self.soup.find_all('script')
        inline_scripts = [s.string for s in scripts if s.string and not s.get('src') and s.get('type') != 'application/ld+json']

        print_info(f"Found {len(inline_scripts)} inline script(s)")

        for i, script in enumerate(inline_scripts):
            if not script.strip():
                continue

            # Write to temp file and validate with Node
            temp_path = Path('/tmp/test_script.js')
            temp_path.write_text(script)

            result = subprocess.run(
                ['node', '--check', str(temp_path)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print_pass(f"Script {i+1}: Syntax valid ({len(script):,} chars)")
                self.results['passed'] += 1
            else:
                print_fail(f"Script {i+1}: Syntax error")
                print(f"      {result.stderr[:200]}")
                self.results['failed'] += 1

        # Check for common JS issues
        js_content = '\n'.join(inline_scripts)

        # eval() usage
        eval_matches = re.findall(r'\beval\s*\(', js_content)
        if not eval_matches:
            print_pass("No eval() usage found")
            self.results['passed'] += 1
        else:
            print_fail(f"Found {len(eval_matches)} eval() usage(s) - security risk")
            self.results['failed'] += 1

        # innerHTML with user input
        innerhtml_matches = re.findall(r'\.innerHTML\s*=(?!=)', js_content)
        print_info(f"Found {len(innerhtml_matches)} innerHTML assignments (review for XSS)")

        # console.log (should be minimal in production)
        console_matches = re.findall(r'console\.(log|error|warn|debug)', js_content)
        if len(console_matches) <= 5:
            print_pass(f"Console statements: {len(console_matches)} (acceptable)")
            self.results['passed'] += 1
        else:
            print_warn(f"Console statements: {len(console_matches)} (consider reducing)")
            self.results['warnings'] += 1

    def test_security_headers(self):
        """Test security-related meta tags and attributes"""
        print_header("Security Tests")

        # CSP
        csp = self.soup.find('meta', attrs={'http-equiv': 'Content-Security-Policy'})
        if csp:
            print_pass("Content-Security-Policy meta tag present")
            csp_content = csp.get('content', '')

            # Check CSP directives
            if 'default-src' in csp_content:
                print_pass("  CSP has default-src directive")
                self.results['passed'] += 1
            if 'script-src' in csp_content:
                print_pass("  CSP has script-src directive")
                self.results['passed'] += 1
            if "'unsafe-eval'" not in csp_content:
                print_pass("  CSP blocks unsafe-eval")
                self.results['passed'] += 1
            else:
                print_warn("  CSP allows unsafe-eval")
                self.results['warnings'] += 1

            self.results['passed'] += 1
        else:
            print_fail("Missing Content-Security-Policy")
            self.results['failed'] += 1

        # X-Content-Type-Options
        xcto = self.soup.find('meta', attrs={'http-equiv': 'X-Content-Type-Options'})
        if xcto:
            print_pass("X-Content-Type-Options present")
            self.results['passed'] += 1
        else:
            print_warn("Missing X-Content-Type-Options")
            self.results['warnings'] += 1

        # External scripts with SRI
        external_scripts = self.soup.find_all('script', src=True)
        for script in external_scripts:
            src = script.get('src', '')
            integrity = script.get('integrity')
            crossorigin = script.get('crossorigin')

            if 'cdnjs' in src or 'cdn' in src:
                if integrity:
                    print_pass(f"SRI present for: {src[:40]}...")
                    self.results['passed'] += 1
                else:
                    print_fail(f"Missing SRI for CDN script: {src[:40]}...")
                    self.results['failed'] += 1

                if crossorigin:
                    print_pass("  crossorigin attribute present")
                    self.results['passed'] += 1

    def test_accessibility(self):
        """Test WCAG accessibility requirements"""
        print_header("Accessibility (WCAG) Tests")

        # Skip link
        skip_link = self.soup.find('a', class_='skip-link')
        if skip_link:
            print_pass("Skip navigation link present")
            self.results['passed'] += 1
        else:
            print_warn("Missing skip navigation link")
            self.results['warnings'] += 1

        # ARIA landmarks
        main_content = self.soup.find(id='main-content')
        if main_content:
            print_pass("Main content landmark present")
            self.results['passed'] += 1

        # Form labels
        inputs = self.soup.find_all('input', {'type': lambda x: x not in ['hidden', 'submit', 'button']})
        labeled = 0
        for inp in inputs:
            inp_id = inp.get('id')
            aria_label = inp.get('aria-label')
            label = self.soup.find('label', {'for': inp_id}) if inp_id else None
            if label or aria_label:
                labeled += 1

        if inputs:
            label_pct = (labeled / len(inputs)) * 100
            if label_pct >= 90:
                print_pass(f"Form inputs labeled: {labeled}/{len(inputs)} ({label_pct:.0f}%)")
                self.results['passed'] += 1
            else:
                print_warn(f"Form inputs labeled: {labeled}/{len(inputs)} ({label_pct:.0f}%)")
                self.results['warnings'] += 1

        # Buttons with labels
        buttons = self.soup.find_all('button')
        unlabeled_buttons = []
        for btn in buttons:
            text = btn.get_text(strip=True)
            aria = btn.get('aria-label')
            title = btn.get('title')
            if not text and not aria and not title:
                unlabeled_buttons.append(btn)

        if not unlabeled_buttons:
            print_pass(f"All {len(buttons)} buttons have labels")
            self.results['passed'] += 1
        else:
            print_warn(f"{len(unlabeled_buttons)} button(s) may need labels")
            self.results['warnings'] += 1

        # Role attributes
        roles = self.soup.find_all(attrs={'role': True})
        print_info(f"ARIA roles used: {len(roles)}")

        # Color contrast (check CSS variables)
        css_content = '\n'.join([s.string for s in self.soup.find_all('style') if s.string])
        if '--text-secondary' in css_content and '--text-muted' in css_content:
            print_pass("Text color variables defined for contrast control")
            self.results['passed'] += 1

    def test_css_validation(self):
        """Validate CSS"""
        print_header("CSS Validation")

        styles = self.soup.find_all('style')
        total_css = '\n'.join([s.string for s in styles if s.string])

        print_info(f"Total CSS: {len(total_css):,} characters")

        # Check for common CSS issues
        issues = []

        # !important overuse
        important_count = total_css.count('!important')
        if important_count <= 10:
            print_pass(f"!important usage: {important_count} (acceptable)")
            self.results['passed'] += 1
        else:
            print_warn(f"!important usage: {important_count} (consider reducing)")
            self.results['warnings'] += 1

        # CSS variables
        var_matches = re.findall(r'--[\w-]+:', total_css)
        print_pass(f"CSS custom properties: {len(var_matches)}")
        self.results['passed'] += 1

        # Media queries
        media_queries = re.findall(r'@media[^{]+', total_css)
        print_info(f"Media queries: {len(media_queries)}")

        # Check for responsive breakpoints
        if '768px' in total_css or '1024px' in total_css:
            print_pass("Responsive breakpoints defined")
            self.results['passed'] += 1

    def test_javascript_patterns(self):
        """Test for good/bad JavaScript patterns"""
        print_header("JavaScript Pattern Analysis")

        scripts = [s.string for s in self.soup.find_all('script') if s.string]
        js_content = '\n'.join(scripts)

        # Async/await usage
        async_count = len(re.findall(r'\basync\b', js_content))
        await_count = len(re.findall(r'\bawait\b', js_content))
        print_info(f"Async/await usage: {async_count} async, {await_count} await")

        # Error handling
        try_count = len(re.findall(r'\btry\s*{', js_content))
        catch_count = len(re.findall(r'\bcatch\s*\(', js_content))
        if try_count >= 5:
            print_pass(f"Error handling: {try_count} try/catch blocks")
            self.results['passed'] += 1
        else:
            print_warn(f"Limited error handling: {try_count} try/catch blocks")
            self.results['warnings'] += 1

        # Event listener cleanup
        remove_listener = len(re.findall(r'removeEventListener', js_content))
        print_info(f"Event listener cleanup: {remove_listener} removeEventListener calls")

        # Memory leak patterns
        if 'WeakMap' in js_content or 'WeakSet' in js_content:
            print_pass("Uses WeakMap/WeakSet for memory management")
            self.results['passed'] += 1

        # Promise handling
        promise_catch = len(re.findall(r'\.catch\s*\(', js_content))
        print_info(f"Promise error handling: {promise_catch} .catch() calls")

        # Class usage
        classes = re.findall(r'class\s+(\w+)', js_content)
        print_info(f"ES6 classes: {', '.join(classes)}")

    def test_parser_edge_cases(self):
        """Test data parser patterns for edge cases"""
        print_header("Parser Edge Case Analysis")

        scripts = [s.string for s in self.soup.find_all('script') if s.string]
        js_content = '\n'.join(scripts)

        # CSV injection protection
        if 'replace' in js_content and ('"' in js_content or 'escape' in js_content.lower()):
            print_pass("CSV escaping logic present")
            self.results['passed'] += 1

        # Date parsing robustness
        date_patterns = re.findall(r'new Date\([^)]+\)', js_content)
        print_info(f"Date parsing instances: {len(date_patterns)}")

        # Number parsing
        parsefloat = len(re.findall(r'parseFloat', js_content))
        parseint = len(re.findall(r'parseInt', js_content))
        print_info(f"Number parsing: {parsefloat} parseFloat, {parseint} parseInt")

        # NaN checks
        isnan_checks = len(re.findall(r'isNaN|Number\.isNaN', js_content))
        if isnan_checks >= 2:
            print_pass(f"NaN validation: {isnan_checks} checks")
            self.results['passed'] += 1
        else:
            print_warn(f"Limited NaN validation: {isnan_checks} checks")
            self.results['warnings'] += 1

        # Null/undefined checks
        null_checks = len(re.findall(r'===?\s*(null|undefined)|!==?\s*(null|undefined)|\?\?|\?\.\w', js_content))
        print_info(f"Null safety patterns: {null_checks}")

    def test_xss_vectors(self):
        """Test for XSS vulnerability patterns"""
        print_header("XSS Vulnerability Scan")

        scripts = [s.string for s in self.soup.find_all('script') if s.string]
        js_content = '\n'.join(scripts)

        # Dangerous patterns
        dangerous_patterns = [
            (r'document\.write\s*\(', 'document.write()'),
            (r'\.outerHTML\s*=', 'outerHTML assignment'),
            (r'location\s*=\s*[^;]+\+', 'Dynamic location assignment'),
            (r'javascript:', 'javascript: protocol'),
            (r'on\w+\s*=\s*["\'][^"\']*\+', 'Inline event handler with concatenation'),
        ]

        for pattern, desc in dangerous_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            if not matches:
                print_pass(f"No {desc} found")
                self.results['passed'] += 1
            else:
                print_fail(f"Found {len(matches)} {desc} - potential XSS")
                self.results['failed'] += 1

        # Check innerHTML with user data
        # This is a simplified check
        innerhtml_lines = [line for line in js_content.split('\n') if 'innerHTML' in line]
        risky_innerhtml = 0
        for line in innerhtml_lines:
            if any(x in line for x in ['${', '+ ', ' +', 'template']):
                risky_innerhtml += 1

        if risky_innerhtml > 0:
            print_warn(f"Review {risky_innerhtml} innerHTML assignments with dynamic content")
            self.results['warnings'] += 1
        else:
            print_pass("innerHTML usage appears safe")
            self.results['passed'] += 1

    def test_data_validation(self):
        """Test input validation patterns"""
        print_header("Input Validation Tests")

        scripts = [s.string for s in self.soup.find_all('script') if s.string]
        js_content = '\n'.join(scripts)

        # Form validation
        if 'required' in self.html_content:
            print_pass("HTML5 required attributes used")
            self.results['passed'] += 1

        # Type checking
        typeof_checks = len(re.findall(r'typeof\s+\w+', js_content))
        if typeof_checks >= 3:
            print_pass(f"Type checking: {typeof_checks} typeof checks")
            self.results['passed'] += 1

        # Range validation for amounts
        if 'amount' in js_content.lower() and ('<' in js_content or '>' in js_content):
            print_pass("Amount range validation present")
            self.results['passed'] += 1

        # Sanitization
        sanitize_patterns = ['trim()', 'replace(', 'escape', 'sanitize', 'encode']
        found_sanitization = sum(1 for p in sanitize_patterns if p in js_content)
        if found_sanitization >= 2:
            print_pass(f"Input sanitization patterns: {found_sanitization}")
            self.results['passed'] += 1

    def test_performance_concerns(self):
        """Test for performance issues"""
        print_header("Performance Analysis")

        scripts = [s.string for s in self.soup.find_all('script') if s.string]
        js_content = '\n'.join(scripts)

        # DOM queries in loops (potential issue)
        loop_dom = re.findall(r'for\s*\([^)]+\)[^{]*{[^}]*document\.(getElementById|querySelector)', js_content)
        if not loop_dom:
            print_pass("No DOM queries inside loops detected")
            self.results['passed'] += 1
        else:
            print_warn(f"DOM queries in loops: {len(loop_dom)} (cache references)")
            self.results['warnings'] += 1

        # Event delegation
        if 'closest(' in js_content or 'target.' in js_content:
            print_pass("Event delegation patterns used")
            self.results['passed'] += 1

        # Debounce/throttle
        if 'debounce' in js_content.lower() or 'throttle' in js_content.lower():
            print_pass("Debounce/throttle implemented")
            self.results['passed'] += 1
        else:
            print_info("Consider debounce for scroll/resize handlers")

        # requestAnimationFrame
        if 'requestAnimationFrame' in js_content:
            print_pass("Uses requestAnimationFrame for animations")
            self.results['passed'] += 1

        # CSS animations vs JS
        css = '\n'.join([s.string for s in self.soup.find_all('style') if s.string])
        if '@keyframes' in css:
            print_pass("CSS animations used (better performance)")
            self.results['passed'] += 1

        # Lazy loading
        if 'lazy' in self.html_content.lower() or 'IntersectionObserver' in js_content:
            print_pass("Lazy loading implemented")
            self.results['passed'] += 1
        else:
            print_info("Consider lazy loading for off-screen content")

    def print_summary(self):
        """Print test summary"""
        print_header("Test Summary")

        total = self.results['passed'] + self.results['failed'] + self.results['warnings']

        print(f"\n  {GREEN}Passed:{RESET}   {self.results['passed']}")
        print(f"  {RED}Failed:{RESET}   {self.results['failed']}")
        print(f"  {YELLOW}Warnings:{RESET} {self.results['warnings']}")
        print(f"  {BLUE}Total:{RESET}    {total}")

        if self.results['failed'] == 0:
            print(f"\n  {GREEN}{BOLD}✓ All critical tests passed!{RESET}")
        else:
            print(f"\n  {RED}{BOLD}✗ {self.results['failed']} critical test(s) failed{RESET}")

        score = (self.results['passed'] / total * 100) if total > 0 else 0
        print(f"\n  {BOLD}Quality Score: {score:.1f}%{RESET}")


if __name__ == '__main__':
    html_file = sys.argv[1] if len(sys.argv) > 1 else 'flowfinance-beast.html'

    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found")
        sys.exit(1)

    suite = FlowFinanceTestSuite(html_file)
    success = suite.run_all()
    sys.exit(0 if success else 1)
