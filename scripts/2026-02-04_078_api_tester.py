#!/usr/bin/env python3
"""
HTTP API Testing Tool - API测试工具
A powerful command-line tool for testing REST APIs

Features:
- GET/POST/PUT/PATCH/DELETE methods
- Headers and authentication support
- JSON/YAML response formatting
- Response validation and assertions
- Test case management
- Colorful output
- CSV/HTML report generation
"""

import argparse
import json
import sys
import time
import csv
import base64
import re
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlencode
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import html
from io import StringIO


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ResultStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIP = "SKIP"


@dataclass
class TestResult:
    """Test case execution result"""
    test_name: str
    status: ResultStatus
    method: str
    url: str
    response_code: int
    response_time: float
    expected_code: int
    message: str = ""
    response_body: str = ""
    errors: List[str] = field(default_factory=list)


@dataclass
class TestCase:
    """API test case definition"""
    name: str
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    expected_code: int = 200
    expected_body_contains: Optional[str] = None
    expected_body_not_contains: Optional[str] = None
    expected_headers: Dict[str, str] = field(default_factory=dict)
    validators: List[Callable] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None


class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        return f"{color}{text}{cls.RESET}"
    
    @classmethod
    def success(cls, text: str) -> str:
        return cls.colorize(text, cls.GREEN)
    
    @classmethod
    def error(cls, text: str) -> str:
        return cls.colorize(text, cls.RED)
    
    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colorize(text, cls.YELLOW)
    
    @classmethod
    def info(cls, text: str) -> str:
        return cls.colorize(text, cls.CYAN)
    
    @classmethod
    def dim(cls, text: str) -> str:
        return cls.colorize(text, cls.DIM)


class APIValidator:
    """Collection of built-in validators for API responses"""
    
    @staticmethod
    def status_code(expected: int) -> Callable[[int, int, str, float, str], List[str]]:
        """Validate response status code"""
        def validator(actual: int, code: int, url: str, time: float, body: str) -> List[str]:
            errors = []
            if actual != expected:
                errors.append(f"Expected status {expected}, got {actual}")
            return errors
        return validator
    
    @staticmethod
    def response_time_max(max_ms: int) -> Callable[[int, int, str, float, str], List[str]]:
        """Validate response time is below threshold"""
        def validator(actual: int, code: int, url: str, time_ms: float, body: str) -> List[str]:
            errors = []
            if time_ms * 1000 > max_ms:
                errors.append(f"Response time {time_ms*1000:.2f}ms exceeds {max_ms}ms")
            return errors
        return validator
    
    @staticmethod
    def body_contains(text: str) -> Callable[[int, int, str, float, str], List[str]]:
        """Validate response body contains expected text"""
        def validator(actual: int, code: int, url: str, time_ms: float, body: str) -> List[str]:
            errors = []
            if text not in body:
                errors.append(f"Response body does not contain '{text}'")
            return errors
        return validator
    
    @staticmethod
    def body_json() -> Callable[[int, int, str, float, str], List[str]]:
        """Validate response is valid JSON"""
        def validator(actual: int, code: int, url: str, time_ms: float, body: str) -> List[str]:
            errors = []
            try:
                json.loads(body)
            except json.JSONDecodeError:
                errors.append("Response is not valid JSON")
            return errors
        return validator
    
    @staticmethod
    def header_exists(name: str) -> Callable[[int, int, str, float, str, Dict[str, str]], List[str]]:
        """Validate response contains expected header"""
        def validator(actual: int, code: int, url: str, time_ms: float, body: str, headers: Dict[str, str] = None) -> List[str]:
            errors = []
            headers = headers or {}
            if name.lower() not in {k.lower() for k in headers.keys()}:
                errors.append(f"Expected header '{name}' not found")
            return errors
        return validator


class APITester:
    """Main API Testing Tool class"""
    
    def __init__(self, base_url: str = "", timeout: int = 30, verbose: bool = False):
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.timeout = timeout
        self.verbose = verbose
        self.test_results: List[TestResult] = []
        self.total_requests = 0
        self.total_time = 0
        
    def _make_request(self, method: str, url: str, headers: Dict[str, str] = None, 
                     body: str = None, auth: tuple = None) -> tuple:
        """Execute HTTP request and return (status_code, response_body, response_headers, time_ms)"""
        full_url = urljoin(self.base_url + '/', url) if self.base_url else url
        headers = headers or {}
        body_bytes = body.encode('utf-8') if body else None
        
        req = urllib.request.Request(full_url, data=body_bytes, method=method)
        for key, value in headers.items():
            req.add_header(key, value)
        
        if auth:
            credentials = f"{auth[0]}:{auth[1]}"
            encoded = base64.b64encode(credentials.encode()).decode()
            req.add_header('Authorization', f'Basic {encoded}')
        
        start_time = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                end_time = time.perf_counter()
                response_body = response.read().decode('utf-8')
                response_headers = dict(response.headers)
                return response.status, response_body, response_headers, (end_time - start_time) * 1000
        except urllib.error.HTTPError as e:
            end_time = time.perf_counter()
            error_body = e.read().decode('utf-8') if e.fp else ""
            return e.code, error_body, dict(e.headers), (end_time - start_time) * 1000
        except urllib.error.URLError as e:
            end_time = time.perf_counter()
            return 0, str(e.reason), {}, (end_time - start_time) * 1000
        except Exception as e:
            end_time = time.perf_counter()
            return 0, str(e), {}, (end_time - start_time) * 1000
    
    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        result = TestResult(
            test_name=test_case.name,
            status=ResultStatus.ERROR,
            method=test_case.method,
            url=test_case.url,
            response_code=0,
            response_time=0,
            expected_code=test_case.expected_code,
            message="Test initialization failed"
        )
        
        try:
            if test_case.setup:
                test_case.setup()
                
            status_code, body, headers, time_ms = self._make_request(
                test_case.method,
                test_case.url,
                test_case.headers,
                test_case.body
            )
            
            result.response_code = status_code
            result.response_time = time_ms
            result.response_body = body[:1000] if body else ""
            
            # Run validators
            errors = []
            for validator in test_case.validators:
                errors.extend(validator(status_code, test_case.expected_code, 
                                       test_case.url, time_ms, body, headers))
            
            # Built-in validations
            if status_code != test_case.expected_code:
                errors.append(f"Expected status {test_case.expected_code}, got {status_code}")
            
            if test_case.expected_body_contains and test_case.expected_body_contains not in body:
                errors.append(f"Body should contain '{test_case.expected_body_contains}'")
            
            if test_case.expected_body_not_contains and test_case.expected_body_not_contains in body:
                errors.append(f"Body should NOT contain '{test_case.expected_body_not_contains}'")
            
            for h_name, h_value in test_case.expected_headers.items():
                if h_name.lower() not in {k.lower() for k in headers.keys()}:
                    errors.append(f"Expected header '{h_name}' not found")
                elif headers.get(h_name, "").lower() != h_value.lower():
                    errors.append(f"Header '{h_name}' expected '{h_value}', got '{headers.get(h_name)}'")
            
            result.errors = errors
            
            if not errors:
                result.status = ResultStatus.PASS
                result.message = "Test passed successfully"
            else:
                result.status = ResultStatus.FAIL
                result.message = "; ".join(errors)
                
            if test_case.teardown:
                test_case.teardown()
                
        except Exception as e:
            result.errors = [str(e)]
            result.message = f"Test error: {str(e)}"
            
        self.test_results.append(result)
        self.total_requests += 1
        self.total_time += result.response_time
        
        return result
    
    def run_test_suite(self, test_cases: List[TestCase], parallel: bool = False) -> List[TestResult]:
        """Execute multiple test cases"""
        if parallel:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(self.run_test_case, tc): tc for tc in test_cases}
                for future in as_completed(futures):
                    pass
        else:
            for tc in test_cases:
                self.run_test_case(tc)
        
        return self.test_results
    
    def print_result(self, result: TestResult):
        """Print test result with formatting"""
        status_icon = {
            ResultStatus.PASS: "✓",
            ResultStatus.FAIL: "✗",
            ResultStatus.ERROR: "!",
            ResultStatus.SKIP: "○"
        }[result.status]
        
        status_color = {
            ResultStatus.PASS: Colors.success,
            ResultStatus.FAIL: Colors.error,
            ResultStatus.ERROR: Colors.warning,
            ResultStatus.SKIP: Colors.dim
        }[result.status]
        
        print(f"{status_color(status_icon)} {Colors.bold(result.test_name)}")
        print(f"  {Colors.info(result.method)} {result.url}")
        print(f"  Status: {result.expected_code} | Response: {result.response_code} | Time: {result.response_time:.2f}ms")
        
        if self.verbose and result.response_body:
            body_preview = result.response_body[:200]
            print(f"  Response: {Colors.dim(body_preview)}")
        
        if result.errors:
            for err in result.errors[:3]:
                print(f"  {Colors.error('Error:')} {err}")
        else:
            print(f"  {Colors.success(result.message)}")
        print()
    
    def print_summary(self):
        """Print test execution summary"""
        passed = sum(1 for r in self.test_results if r.status == ResultStatus.PASS)
        failed = sum(1 for r in self.test_results if r.status == ResultStatus.FAIL)
        errors = sum(1 for r in self.test_results if r.status == ResultStatus.ERROR)
        
        print(Colors.BOLD + "=" * 60)
        print("TEST SUMMARY")
        print("=" * Colors.RESET)
        print(f"Total Tests:   {self.total_requests}")
        print(f"{Colors.success(f'Passed:')}       {passed}")
        print(f"{Colors.error(f'Failed:')}       {failed}")
        print(f"{Colors.warning(f'Errors:')}       {errors}")
        print(f"Total Time:    {self.total_time:.2f}ms")
        print(f"Avg Time:      {self.total_time/self.total_requests:.2f}ms" if self.total_requests > 0 else "")
        print(Colors.BOLD + "=" * Colors.RESET)
        
        return passed, failed, errors
    
    def export_csv(self, filename: str):
        """Export results to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Test Name', 'Method', 'URL', 'Status', 'Expected Code', 
                           'Actual Code', 'Response Time (ms)', 'Message'])
            for r in self.test_results:
                writer.writerow([r.test_name, r.method, r.url, r.status.value, 
                               r.expected_code, r.response_code, 
                               f"{r.response_time:.2f}", r.message])
        print(f"{Colors.success('✓')} Results exported to {filename}")
    
    def export_html(self, filename: str):
        """Export results to HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>API Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .error {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .test-case {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; }}
        .status {{ font-weight: bold; }}
    </style>
</head>
<body>
    <h1>API Test Report</h1>
    <div class="summary">
        <h3>Summary</h3>
        <p>Total Tests: {self.total_requests}</p>
        <p class="pass">Passed: {sum(1 for r in self.test_results if r.status == ResultStatus.PASS)}</p>
        <p class="fail">Failed: {sum(1 for r in self.test_results if r.status == ResultStatus.FAIL)}</p>
        <p class="error">Errors: {sum(1 for r in self.test_results if r.status == ResultStatus.ERROR)}</p>
        <p>Total Time: {self.total_time:.2f}ms</p>
    </div>
    <h2>Test Results</h2>
"""
        for r in self.test_results:
            status_class = r.status.value.lower()
            html_content += f"""
    <div class="test-case">
        <h4 class="status {status_class}">{r.status.value} - {r.test_name}</h4>
        <p><strong>Method:</strong> {r.method} | <strong>URL:</strong> {r.url}</p>
        <p><strong>Expected:</strong> {r.expected_code} | <strong>Actual:</strong> {r.response_code} | <strong>Time:</strong> {r.response_time:.2f}ms</p>
        <p><strong>Message:</strong> {html.escape(r.message)}</p>
    </div>
"""
        html_content += "</body></html>"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"{Colors.success('✓')} HTML report exported to {filename}")


def parse_headers(header_str: str) -> Dict[str, str]:
    """Parse headers from string format 'Key: Value'"""
    headers = {}
    for line in header_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers


def main():
    parser = argparse.ArgumentParser(
        description="HTTP API Testing Tool - Powerful command-line API testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single request
  %(prog)s -m GET https://api.example.com/users
  
  # POST with JSON body
  %(prog)s -m POST https://api.example.com/users -b '{"name":"John"}' -h "Content-Type:application/json"
  
  # Run test suite
  %(prog)s --suite tests.json --base-url https://api.example.com
  
  # With authentication
  %(prog)s -m GET https://api.example.com/secure -a user:pass
  
  # Export results
  %(prog)s -m GET https://api.example.com -o results.csv
        """
    )
    
    parser.add_argument('-m', '--method', default='GET', 
                       choices=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'],
                       help='HTTP method (default: GET)')
    parser.add_argument('url', nargs='?', help='URL to test')
    parser.add_argument('-b', '--body', help='Request body')
    parser.add_argument('-H', '--header', action='append', help='Add request header (can be used multiple times)')
    parser.add_argument('-a', '--auth', help='Basic authentication (username:password)')
    parser.add_argument('-o', '--output', choices=['json', 'csv', 'html'], 
                        help='Output format for results')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--base-url', help='Base URL for relative paths')
    parser.add_argument('--suite', help='Test suite file (JSON/YAML)')
    parser.add_argument('--validate', action='store_true', help='Validate response is JSON')
    parser.add_argument('--expect-code', type=int, default=200, help='Expected status code')
    parser.add_argument('--csv', help='Export results to CSV file')
    parser.add_argument('--html', help='Export results to HTML file')
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = APITester(base_url=args.base_url or "", timeout=args.timeout, verbose=args.verbose)
    
    # Build headers
    headers = {}
    if args.header:
        for h in args.header:
            if ':' in h:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()
    
    # Parse auth
    auth = None
    if args.auth and ':' in args.auth:
        auth = tuple(args.auth.split(':', 1))
    
    # Run single test or suite
    if args.suite:
        # Load and run test suite
        try:
            with open(args.suite, 'r') as f:
                if args.suite.endswith('.yaml') or args.suite.endswith('.yml'):
                    import yaml
                    suite_data = yaml.safe_load(f)
                else:
                    suite_data = json.load(f)
            
            test_cases = []
            for tc_data in suite_data.get('tests', []):
                tc = TestCase(
                    name=tc_data['name'],
                    method=tc_data['method'],
                    url=tc_data['url'],
                    headers=tc_data.get('headers', {}),
                    body=tc_data.get('body'),
                    expected_code=tc_data.get('expected_code', 200),
                )
                test_cases.append(tc)
            
            results = tester.run_test_suite(test_cases)
            for r in results:
                tester.print_result(r)
            tester.print_summary()
            
        except Exception as e:
            print(f"{Colors.error('Error loading test suite:')} {e}")
            sys.exit(1)
    else:
        # Single request
        if not args.url:
            parser.print_help()
            sys.exit(1)
        
        # Create test case
        tc = TestCase(
            name=f"API Test - {args.method} {args.url}",
            method=args.method,
            url=args.url,
            headers=headers,
            body=args.body,
            expected_code=args.expect_code,
        )
        
        if args.validate:
            tc.validators.append(APIValidator.body_json())
        
        result = tester.run_test_case(tc)
        tester.print_result(result)
    
    # Export results
    if args.csv:
        tester.export_csv(args.csv)
    if args.html:
        tester.export_html(args.html)
    if args.output == 'csv':
        tester.export_csv('results.csv')
    elif args.output == 'html':
        tester.export_html('results.html')
    elif args.output == 'json':
        print(json.dumps([{
            'name': r.test_name,
            'status': r.status.value,
            'code': r.response_code,
            'time': r.response_time
        } for r in tester.test_results], indent=2))


if __name__ == "__main__":
    main()
