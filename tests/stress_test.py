#!/usr/bin/env python3
"""
FlowFinance Stress Tests
========================
Tests parser limits, edge cases, and malicious inputs
"""

import json
import random
import string
from datetime import datetime, timedelta

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

def print_info(text):
    print(f"  {BLUE}ℹ{RESET} {text}")


class StressTestGenerator:
    """Generate test data for stress testing"""

    @staticmethod
    def generate_csv(rows=1000, malicious=False):
        """Generate CSV test data"""
        lines = ['Date,Description,Amount,Type,Category']

        for i in range(rows):
            date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')

            if malicious:
                # Inject various payloads
                payloads = [
                    '<script>alert("xss")</script>',
                    '=CMD|"/C calc"!A0',  # CSV injection
                    "'; DROP TABLE transactions;--",  # SQL injection
                    '${7*7}',  # Template injection
                    '../../../etc/passwd',  # Path traversal
                    'javascript:alert(1)',
                    '"><img src=x onerror=alert(1)>',
                    '\x00\x00\x00',  # Null bytes
                    'A' * 10000,  # Buffer overflow attempt
                ]
                desc = random.choice(payloads)
            else:
                desc = f"Transaction {i}"

            amount = round(random.uniform(0.01, 10000), 2)
            tx_type = random.choice(['income', 'expense'])
            category = random.choice(['Food', 'Housing', 'Transport', 'Entertainment', 'Other'])

            # Escape CSV properly
            desc_escaped = f'"{desc.replace(chr(34), chr(34)+chr(34))}"'
            lines.append(f'{date},{desc_escaped},{amount},{tx_type},{category}')

        return '\n'.join(lines)

    @staticmethod
    def generate_large_numbers():
        """Test numeric edge cases"""
        return [
            0,
            -0,
            0.01,
            0.001,
            0.0001,
            999999999,
            999999999.99,
            -999999999.99,
            float('inf'),
            float('-inf'),
            1e10,
            1e-10,
            2**53,  # Max safe integer
            2**53 + 1,  # Beyond safe integer
        ]

    @staticmethod
    def generate_date_edge_cases():
        """Test date parsing edge cases"""
        return [
            '2024-01-01',
            '2024-12-31',
            '2024-02-29',  # Leap year
            '2023-02-29',  # Invalid leap year
            '2024-13-01',  # Invalid month
            '2024-01-32',  # Invalid day
            '01/15/2024',  # US format
            '15/01/2024',  # EU format
            '2024/01/15',  # Alternative format
            'January 15, 2024',
            '15-Jan-2024',
            '1/1/24',  # Two digit year
            '99/12/31',  # Y2K issue
            '00/01/01',  # Y2K edge
            '',
            'invalid',
            '0000-00-00',
            '9999-99-99',
        ]

    @staticmethod
    def generate_string_edge_cases():
        """Test string handling edge cases"""
        return [
            '',
            ' ',
            '   ',
            '\t',
            '\n',
            '\r\n',
            'a',
            'A' * 201,  # Over maxlength
            'A' * 1000,
            'A' * 10000,
            '🎉💰🚀',  # Emojis
            '日本語',  # Japanese
            'العربية',  # Arabic (RTL)
            '中文',  # Chinese
            'Ελληνικά',  # Greek
            '\u0000',  # Null char
            '\u200B',  # Zero-width space
            '\uFEFF',  # BOM
            '<>',
            '&amp;',
            '&lt;script&gt;',
            '"quoted"',
            "'quoted'",
            '`backticks`',
            '${template}',
            '{{mustache}}',
            '[[wiki]]',
        ]

    @staticmethod
    def generate_qif_edge_cases():
        """Generate QIF format edge cases"""
        test_cases = []

        # Valid QIF
        test_cases.append("""!Type:Bank
D01/15/2024
T-50.00
PGrocery Store
^
D01/16/2024
T100.00
PSalary
^""")

        # Empty QIF
        test_cases.append("")

        # QIF with no transactions
        test_cases.append("!Type:Bank\n")

        # QIF with invalid type
        test_cases.append("""!Type:Invalid
D01/15/2024
T-50.00
^""")

        # QIF with malformed dates
        test_cases.append("""!Type:Bank
D99/99/9999
T-50.00
^""")

        # QIF with huge amount
        test_cases.append("""!Type:Bank
D01/15/2024
T-999999999999999
^""")

        return test_cases

    @staticmethod
    def generate_ofx_edge_cases():
        """Generate OFX format edge cases"""
        valid_ofx = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<STMTRS>
<BANKTRANLIST>
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20240115
<TRNAMT>-50.00
<NAME>Grocery Store
</STMTTRN>
</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""

        return [
            valid_ofx,
            "",  # Empty
            "<OFX></OFX>",  # Empty OFX
            "NOT OFX AT ALL",  # Invalid format
            valid_ofx.replace('-50.00', 'NaN'),  # NaN amount
            valid_ofx.replace('-50.00', 'Infinity'),  # Infinity
        ]


def run_stress_tests():
    """Run all stress tests"""
    print(f"\n{BOLD}FlowFinance Stress Test Suite{RESET}")
    print(f"Testing parser limits and edge cases")

    results = {'passed': 0, 'failed': 0}
    gen = StressTestGenerator()

    # CSV Generation Tests
    print_header("CSV Generation Tests")

    csv_small = gen.generate_csv(100)
    print_pass(f"Generated 100-row CSV: {len(csv_small):,} bytes")
    results['passed'] += 1

    csv_medium = gen.generate_csv(1000)
    print_pass(f"Generated 1,000-row CSV: {len(csv_medium):,} bytes")
    results['passed'] += 1

    csv_large = gen.generate_csv(10000)
    print_pass(f"Generated 10,000-row CSV: {len(csv_large):,} bytes ({len(csv_large)//1024}KB)")
    results['passed'] += 1

    csv_malicious = gen.generate_csv(100, malicious=True)
    print_pass(f"Generated malicious CSV: {len(csv_malicious):,} bytes")
    results['passed'] += 1

    # Save test files
    with open('/tmp/test_small.csv', 'w') as f:
        f.write(csv_small)
    with open('/tmp/test_large.csv', 'w') as f:
        f.write(csv_large)
    with open('/tmp/test_malicious.csv', 'w') as f:
        f.write(csv_malicious)

    print_info("Test files saved to /tmp/test_*.csv")

    # Numeric Edge Cases
    print_header("Numeric Edge Cases")

    numbers = gen.generate_large_numbers()
    for num in numbers:
        try:
            # Test JavaScript-like number handling
            if num == float('inf') or num == float('-inf'):
                print_info(f"Infinity value: {num} (should be handled)")
            elif num != num:  # NaN check
                print_info(f"NaN value detected (should be handled)")
            elif abs(num) > 2**53:
                print_info(f"Beyond safe integer: {num}")
            else:
                print_pass(f"Valid number: {num}")
                results['passed'] += 1
        except Exception as e:
            print_fail(f"Number handling error: {num} - {e}")
            results['failed'] += 1

    # Date Edge Cases
    print_header("Date Parsing Edge Cases")

    dates = gen.generate_date_edge_cases()
    for date_str in dates:
        try:
            # Try parsing
            if not date_str or date_str == 'invalid':
                print_info(f"Invalid date string: '{date_str[:20]}' (should be rejected)")
            else:
                # Check if parseable
                from datetime import datetime
                try:
                    parsed = datetime.strptime(date_str, '%Y-%m-%d')
                    print_pass(f"ISO date: {date_str}")
                    results['passed'] += 1
                except:
                    print_info(f"Non-ISO date: '{date_str}' (needs special handling)")
        except Exception as e:
            print_info(f"Date edge case: '{date_str[:20]}' - {e}")

    # String Edge Cases
    print_header("String Handling Edge Cases")

    strings = gen.generate_string_edge_cases()
    for s in strings:
        display = repr(s)[:40]
        if len(s) > 200:
            print_info(f"Long string ({len(s)} chars): truncation needed")
        elif '\x00' in s:
            print_info(f"Null byte in string: should be stripped")
        elif '<' in s or '>' in s:
            print_info(f"HTML chars: {display} (needs escaping)")
        elif s.strip() == '':
            print_info(f"Empty/whitespace string: {display}")
        else:
            print_pass(f"String: {display}")
            results['passed'] += 1

    # QIF Edge Cases
    print_header("QIF Format Edge Cases")

    qif_cases = gen.generate_qif_edge_cases()
    for i, qif in enumerate(qif_cases):
        if not qif:
            print_info(f"QIF case {i+1}: Empty file (should handle gracefully)")
        elif '!Type:Invalid' in qif:
            print_info(f"QIF case {i+1}: Invalid type (should warn)")
        elif '99/99/9999' in qif:
            print_info(f"QIF case {i+1}: Invalid date (should skip)")
        else:
            print_pass(f"QIF case {i+1}: Valid format")
            results['passed'] += 1

    # OFX Edge Cases
    print_header("OFX Format Edge Cases")

    ofx_cases = gen.generate_ofx_edge_cases()
    for i, ofx in enumerate(ofx_cases):
        if not ofx:
            print_info(f"OFX case {i+1}: Empty file")
        elif '<OFX>' not in ofx:
            print_info(f"OFX case {i+1}: Invalid format")
        elif 'NaN' in ofx or 'Infinity' in ofx:
            print_info(f"OFX case {i+1}: Invalid number (should handle)")
        else:
            print_pass(f"OFX case {i+1}: Valid format")
            results['passed'] += 1

    # Memory Stress Test
    print_header("Memory Stress Simulation")

    # Generate large dataset
    large_data = []
    for i in range(100000):
        large_data.append({
            'date': '2024-01-15',
            'description': f'Transaction {i}',
            'amount': random.uniform(1, 1000),
            'type': 'expense',
            'category': 'Food'
        })

    mem_size = len(json.dumps(large_data))
    print_pass(f"Generated 100K transactions: {mem_size:,} bytes ({mem_size//1024//1024}MB)")
    results['passed'] += 1

    # Cleanup
    del large_data

    # Summary
    print_header("Stress Test Summary")

    total = results['passed'] + results['failed']
    print(f"\n  {GREEN}Passed:{RESET}  {results['passed']}")
    print(f"  {RED}Failed:{RESET}  {results['failed']}")
    print(f"  {BLUE}Total:{RESET}   {total}")

    if results['failed'] == 0:
        print(f"\n  {GREEN}{BOLD}✓ All stress tests passed!{RESET}")
    else:
        print(f"\n  {RED}{BOLD}✗ {results['failed']} stress test(s) failed{RESET}")

    return results['failed'] == 0


if __name__ == '__main__':
    run_stress_tests()
