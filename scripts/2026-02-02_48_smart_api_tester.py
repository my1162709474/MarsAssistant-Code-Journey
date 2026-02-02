#!/usr/bin/env python3
"""
智能API测试工具
Smart API Testing Tool

功能特性:
- 支持多种HTTP方法 (GET/POST/PUT/DELETE/PATCH)
- 请求头和请求体配置
- 响应验证和断言
- 环境变量管理
- 测试用例组织和批量执行
- 彩色终端输出
- 历史记录管理
"""

import json
import requests
import argparse
import sys
import os
import time
from datetime import datetime
from typing import Any, Optional, Dict, List
from enum import Enum
import base64
import re

# ANSI颜色代码
class Colors:
    """终端颜色配置"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

class HttpMethod(Enum):
    """HTTP请求方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class StatusCode(Enum):
    """HTTP状态码分类"""
    SUCCESS = (200, 299)
    REDIRECTION = (300, 399)
    CLIENT_ERROR = (400, 499)
    SERVER_ERROR = (500, 599)

class APIResponse:
    """API响应封装"""
    
    def __init__(self, response: requests.Response, duration: float):
        self.status_code = response.status_code
        self.headers = dict(response.headers)
        self.text = response.text
        self.json_data = None
        self.duration = duration
        self.url = response.url
        
        try:
            self.json_data = response.json()
        except json.JSONDecodeError:
            pass
    
    def is_success(self) -> bool:
        """检查是否成功 (2xx)"""
        return 200 <= self.status_code < 300
    
    def is_client_error(self) -> bool:
        """检查是否客户端错误 (4xx)"""
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """检查是否服务器错误 (5xx)"""
        return 500 <= self.status_code < 600
    
    def get_status_category(self) -> str:
        """获取状态类别"""
        if self.is_success():
            return "SUCCESS"
        elif self.is_client_error():
            return "CLIENT_ERROR"
        elif self.is_server_error():
            return "SERVER_ERROR"
        else:
            return "REDIRECTION"

class AssertionResult:
    """断言结果"""
    
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
    
    def __str__(self):
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if self.passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        return f"{status} [{self.name}] {self.message}"

class APIValidator:
    """API响应验证器"""
    
    @staticmethod
    def assert_status_code(response: APIResponse, expected: int) -> AssertionResult:
        """断言状态码"""
        actual = response.status_code
        passed = actual == expected
        message = f"Expected {expected}, got {actual}" if not passed else ""
        return AssertionResult(f"Status Code = {expected}", passed, message)
    
    def assert_status_in(self, response: APIResponse, expected_codes: List[int]) -> AssertionResult:
        """断言状态码在列表中"""
        actual = response.status_code
        passed = actual in expected_codes
        message = f"Expected one of {expected_codes}, got {actual}" if not passed else ""
        return AssertionResult(f"Status Code in {expected_codes}", passed, message)
    
    @staticmethod
    def assert_json_path(response: APIResponse, path: str, expected_value: Any) -> AssertionResult:
        """断言JSON路径值"""
        try:
            data = response.json_data
            keys = path.split('.')
            for key in keys:
                if isinstance(data, dict):
                    data = data.get(key, None)
                elif isinstance(data, list):
                    data = data[int(key)] if key.isdigit() else None
                else:
                    data = None
            
            passed = data == expected_value
            message = f"Path '{path}': expected {expected_value}, got {data}" if not passed else ""
            return AssertionResult(f"JSON Path '{path}' = {expected_value}", passed, message)
        except Exception as e:
            return AssertionResult(f"JSON Path '{path}'", False, str(e))
    
    @staticmethod
    def assert_json_has_key(response: APIResponse, key: str) -> AssertionResult:
        """断言JSON包含指定键"""
        if response.json_data is None:
            return AssertionResult(f"JSON has key '{key}'", False, "Response is not valid JSON")
        
        passed = key in response.json_data or any(key in item for item in response.json_data if isinstance(response.json_data, list))
        message = f"Key '{key}' not found" if not passed else ""
        return AssertionResult(f"JSON has key '{key}'", passed, message)
    
    @staticmethod
    def assert_response_time(response: APIResponse, max_ms: int) -> AssertionResult:
        """断言响应时间"""
        duration_ms = response.duration * 1000
        passed = duration_ms <= max_ms
        message = f"Response time {duration_ms:.2f}ms exceeded {max_ms}ms" if not passed else ""
        return AssertionResult(f"Response Time ≤ {max_ms}ms", passed, message)
    
    @staticmethod
    def assert_response_contains(response: APIResponse, text: str) -> AssertionResult:
        """断言响应包含文本"""
        passed = text in response.text
        message = f"Text '{text}' not found in response" if not passed else ""
        return AssertionResult(f"Response contains '{text}'", passed, message)
    
    @staticmethod
    def assert_response_size(response: APIResponse, max_kb: int) -> AssertionResult:
        """断言响应大小"""
        size_kb = len(response.text.encode('utf-8')) / 1024
        passed = size_kb <= max_kb
        message = f"Response size {size_kb:.2f}KB exceeded {max_kb}KB" if not passed else ""
        return AssertionResult(f"Response Size ≤ {max_kb}KB", passed, message)


class TestCase:
    """API测试用例"""
    
    def __init__(self, name: str, method: str, url: str, 
                 headers: Optional[Dict] = None, 
                 body: Optional[Any] = None,
                 assertions: Optional[List[Dict]] = None):
        self.name = name
        self.method = HttpMethod(method.upper())
        self.url = url
        self.headers = headers or {}
        self.body = body
        self.assertions = assertions or []
        self.id = f"test_{int(time.time() * 1000)}"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "method": self.method.value,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "assertions": self.assertions
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TestCase':
        """从字典创建"""
        return cls(
            name=data["name"],
            method=data["method"],
            url=data["url"],
            headers=data.get("headers", {}),
            body=data.get("body"),
            assertions=data.get("assertions", [])
        )


class TestSuite:
    """测试套件"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.test_cases: List[TestCase] = []
        self.variables: Dict[str, str] = {}
        self.created_at = datetime.now().isoformat()
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def set_variable(self, key: str, value: str):
        """设置环境变量"""
        self.variables[key] = value
    
    def get_variable(self, key: str) -> Optional[str]:
        """获取环境变量"""
        return self.variables.get(key)
    
    def resolve_variables(self, text: str) -> str:
        """解析变量"""
        for key, value in self.variables.items():
            text = text.replace(f"${{{key}}}", value)
        return text
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "variables": self.variables,
            "tests": [tc.to_dict() for tc in self.test_cases],
            "created_at": self.created_at
        }
    
    def save_to_file(self, filepath: str):
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'TestSuite':
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        suite = cls(name=data["name"], description=data.get("description", ""))
        suite.variables = data.get("variables", {})
        
        for test_data in data.get("tests", []):
            suite.add_test_case(TestCase.from_dict(test_data))
        
        return suite


class APITester:
    """API测试器主类"""
    
    def __init__(self, timeout: int = 30, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        self.validator = APIValidator()
        self.history: List[Dict] = []
    
    def execute_request(self, test_case: TestCase, variables: Dict[str, str] = None) -> APIResponse:
        """执行HTTP请求"""
        # 解析URL中的变量
        url = test_case.url
        if variables:
            for key, value in variables.items():
                url = url.replace(f"${{{key}}}", value)
        
        # 准备请求头
        headers = test_case.headers.copy()
        # 解析请求头中的变量
        for key in headers:
            if isinstance(headers[key], str) and variables:
                for var_key, var_value in variables.items():
                    headers[key] = headers[key].replace(f"${{{var_key}}}", var_value)
        
        # 准备请求体
        body = test_case.body
        if isinstance(body, str) and variables:
            for var_key, var_value in variables.items():
                body = body.replace(f"${{{var_key}}}", var_value)
        
        # 发送请求
        start_time = time.time()
        
        try:
            if test_case.method == HttpMethod.GET:
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif test_case.method == HttpMethod.POST:
                if isinstance(body, dict):
                    response = requests.post(url, json=body, headers=headers, timeout=self.timeout)
                else:
                    response = requests.post(url, data=body, headers=headers, timeout=self.timeout)
            elif test_case.method == HttpMethod.PUT:
                if isinstance(body, dict):
                    response = requests.put(url, json=body, headers=headers, timeout=self.timeout)
                else:
                    response = requests.put(url, data=body, headers=headers, timeout=self.timeout)
            elif test_case.method == HttpMethod.DELETE:
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            elif test_case.method == HttpMethod.PATCH:
                if isinstance(body, dict):
                    response = requests.patch(url, json=body, headers=headers, timeout=self.timeout)
                else:
                    response = requests.patch(url, data=body, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {test_case.method}")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error to {url}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
        
        duration = time.time() - start_time
        return APIResponse(response, duration)
    
    def run_assertions(self, response: APIResponse, assertions: List[Dict]) -> List[AssertionResult]:
        """执行断言"""
        results = []
        
        for assertion in assertions:
            assertion_type = assertion.get("type", "")
            
            if assertion_type == "status_code":
                results.append(self.validator.assert_status_code(response, assertion["expected"]))
            elif assertion_type == "status_in":
                results.append(self.validator.assert_status_in(response, assertion["expected"]))
            elif assertion_type == "json_path":
                results.append(self.validator.assert_json_path(response, assertion["path"], assertion["expected"]))
            elif assertion_type == "json_has_key":
                results.append(self.validator.assert_json_has_key(response, assertion["key"]))
            elif assertion_type == "response_time":
                results.append(self.validator.assert_response_time(response, assertion["max_ms"]))
            elif assertion_type == "response_contains":
                results.append(self.validator.assert_response_contains(response, assertion["text"]))
            elif assertion_type == "response_size":
                results.append(self.validator.assert_response_size(response, assertion["max_kb"]))
        
        return results
    
    def run_test(self, test_case: TestCase, variables: Dict[str, str] = None) -> Dict:
        """运行单个测试"""
        result = {
            "test_name": test_case.name,
            "method": test_case.method.value,
            "url": test_case.url,
            "passed": False,
            "response": None,
            "assertions": [],
            "error": None
        }
        
        try:
            response = self.execute_request(test_case, variables)
            result["response"] = {
                "status_code": response.status_code,
                "status_category": response.get_status_category(),
                "duration_ms": round(response.duration * 1000, 2),
                "size_bytes": len(response.text.encode('utf-8')),
                "json": response.json_data
            }
            
            # 执行断言
            assertions = self.run_assertions(response, test_case.assertions)
            result["assertions"] = [
                {
                    "name": a.name,
                    "passed": a.passed,
                    "message": a.message
                }
                for a in assertions
            ]
            
            # 判断测试是否通过
            result["passed"] = response.is_success() and all(a.passed for a in assertions)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def run_suite(self, suite: TestSuite) -> Dict:
        """运行测试套件"""
        suite_result = {
            "suite_name": suite.name,
            "total": len(suite.test_cases),
            "passed": 0,
            "failed": 0,
            "tests": [],
            "duration_ms": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        for test_case in suite.test_cases:
            test_result = self.run_test(test_case, suite.variables)
            suite_result["tests"].append(test_result)
            
            if test_result["passed"]:
                suite_result["passed"] += 1
            else:
                suite_result["failed"] += 1
        
        suite_result["duration_ms"] = round((time.time() - start_time) * 1000, 2)
        
        # 保存到历史记录
        self.history.append(suite_result)
        
        return suite_result


class OutputFormatter:
    """输出格式化器"""
    
    @staticmethod
    def print_header(text: str, width: int = 80):
        """打印标题"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(width)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}\n")
    
    @staticmethod
    def print_test_result(result: Dict, index: int = 1):
        """打印测试结果"""
        passed = result["passed"]
        status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
        status_text = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        
        print(f"{status_icon} Test #{index}: {result['test_name']}")
        print(f"  {Colors.DIM}Method:{Colors.RESET} {result['method']}")
        print(f"  {Colors.DIM}URL:{Colors.RESET} {result['url']}")
        
        if result['response']:
            response = result['response']
            status_color = Colors.GREEN if response['status_category'] == 'SUCCESS' else Colors.RED
            print(f"  {Colors.DIM}Status:{Colors.RESET} {response['status_code']} ({status_color}{response['status_category']}{Colors.RESET})")
            print(f"  {Colors.DIM}Time:{Colors.RESET} {response['duration_ms']}ms")
            
            if result['assertions']:
                print(f"  {Colors.DIM}Assertions:{Colors.RESET}")
                for assertion in result['assertions']:
                    icon = f"{Colors.GREEN}✓{Colors.RESET}" if assertion['passed'] else f"{Colors.RED}✗{Colors.RESET}"
                    print(f"    {icon} {assertion['name']}")
        
        if result['error']:
            print(f"  {Colors.RED}Error:{Colors.RESET} {result['error']}")
        
        print()
    
    @staticmethod
    def print_suite_summary(result: Dict):
        """打印套件总结"""
        total = result['total']
        passed = result['passed']
        failed = result['failed']
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        pass_color = Colors.GREEN if pass_rate >= 80 else Colors.YELLOW if pass_rate >= 50 else Colors.RED
        
        print(f"{Colors.BOLD}{'─' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}Suite: {result['suite_name']}{Colors.RESET}")
        print(f"{Colors.BOLD}Total: {total} | Passed: {Colors.GREEN}{passed}{Colors.RESET} | Failed: {Colors.RED}{failed}{Colors.RESET}")
        print(f"{Colors.BOLD}Pass Rate: {pass_color}{pass_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.BOLD}Duration: {result['duration_ms']}ms{Colors.RESET}")
        print(f"{Colors.BOLD}{'─' * 60}{Colors.RESET}\n")
    
    @staticmethod
    def print_json_response(response: Dict, max_depth: int = 3, current_depth: int = 0):
        """打印JSON响应（美化格式）"""
        if current_depth >= max_depth:
            print(f"{Colors.DIM}...{Colors.RESET}")
            return
        
        if isinstance(response, dict):
            for key, value in list(response.items())[:5]:  # 只显示前5个键
                print(f"{Colors.CYAN}{key}:{Colors.RESET}", end=" ")
                if isinstance(value, (dict, list)):
                    print()
                    OutputFormatter.print_json_response(value, max_depth, current_depth + 1)
                else:
                    print(value)
        elif isinstance(response, list):
            print(f"{Colors.DIM}[{len(response)} items]{Colors.RESET}")
        else:
            print(response)


def create_sample_test_suite() -> TestSuite:
    """创建示例测试套件"""
    suite = TestSuite(
        name="API Testing Demo",
        description="示例API测试套件，演示工具的各种功能"
    )
    
    # 设置环境变量
    suite.set_variable("base_url", "https://jsonplaceholder.typicode.com")
    suite.set_variable("user_id", "1")
    
    # 测试1: 获取用户信息
    test1 = TestCase(
        name="Get User Details",
        method="GET",
        url="${{{base_url}}}/users/${{{user_id}}}",
        assertions=[
            {"type": "status_code", "expected": 200},
            {"type": "response_time", "max_ms": 2000},
            {"type": "json_has_key", "key": "name"}
        ]
    )
    suite.add_test_case(test1)
    
    # 测试2: 获取文章列表
    test2 = TestCase(
        name="Get Posts",
        method="GET",
        url="${{{base_url}}}/posts",
        assertions=[
            {"type": "status_code", "expected": 200},
            {"type": "response_time", "max_ms": 3000},
            {"type": "json_has_key", "key": "id"}
        ]
    )
    suite.add_test_case(test2)
    
    # 测试3: 创建新文章
    test3 = TestCase(
        name="Create Post",
        method="POST",
        url="${{{base_url}}}/posts",
        headers={"Content-Type": "application/json"},
        body={
            "title": "Test Post",
            "body": "This is a test post created by API Tester",
            "userId": 1
        },
        assertions=[
            {"type": "status_code", "expected": 201},
            {"type": "json_path", "path": "title", "expected": "Test Post"}
        ]
    )
    suite.add_test_case(test3)
    
    # 测试4: 更新文章
    test4 = TestCase(
        name="Update Post",
        method="PUT",
        url="${{{base_url}}}/posts/1",
        headers={"Content-Type": "application/json"},
        body={
            "id": 1,
            "title": "Updated Title",
            "body": "Updated content",
            "userId": 1
        },
        assertions=[
            {"type": "status_code", "expected": 200},
            {"type": "json_path", "path": "title", "expected": "Updated Title"}
        ]
    )
    suite.add_test_case(test4)
    
    # 测试5: 删除文章
    test5 = TestCase(
        name="Delete Post",
        method="DELETE",
        url="${{{base_url}}}/posts/1",
        assertions=[
            {"type": "status_code", "expected": 200}
        ]
    )
    suite.add_test_case(test5)
    
    return suite


def interactive_mode():
    """交互式模式"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           Smart API Tester - Interactive Mode              ║")
    print("║                                                            ║")
    print("║  Commands:                                                 ║")
    print("║    run <file.json>    - Run test suite from file          ║")
    print("║    create             - Create new test suite             ║")
    print("║    list               - List saved test suites            ║")
    print("║    demo               - Run demo tests                    ║")
    print("║    help               - Show this help message            ║")
    print("║    quit               - Exit the program                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    tester = APITester(verbose=True)
    
    while True:
        try:
            cmd = input(f"{Colors.BLUE}➜ {Colors.RESET}").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            action = parts[0].lower()
            
            if action == "quit":
                print(f"\n{Colors.CYAN}Goodbye! 👋{Colors.RESET}\n")
                break
            
            elif action == "help":
                print(f"\n{Colors.BOLD}Help:{Colors.RESET}")
                print("  run <file>   - Execute test suite from JSON file")
                print("  create       - Create new test suite interactively")
                print("  list         - List all saved test suites")
                print("  demo         - Run built-in demo tests")
                print("  help         - Show this help message")
                print("  quit         - Exit the program\n")
            
            elif action == "demo":
                OutputFormatter.print_header("Running Demo Test Suite")
                suite = create_sample_test_suite()
                result = tester.run_suite(suite)
                
                for i, test_result in enumerate(result['tests'], 1):
                    OutputFormatter.print_test_result(test_result, i)
                
                OutputFormatter.print_suite_summary(result)
            
            elif action == "run":
                if len(parts) < 2:
                    print(f"{Colors.RED}Usage: run <file.json>{Colors.RESET}")
                    continue
                
                filepath = parts[1]
                if not os.path.exists(filepath):
                    print(f"{Colors.RED}File not found: {filepath}{Colors.RESET}")
                    continue
                
                OutputFormatter.print_header(f"Running Test Suite: {filepath}")
                suite = TestSuite.load_from_file(filepath)
                result = tester.run_suite(suite)
                
                for i, test_result in enumerate(result['tests'], 1):
                    OutputFormatter.print_test_result(test_result, i)
                
                OutputFormatter.print_suite_summary(result)
            
            elif action == "list":
                print(f"\n{Colors.BOLD}Saved Test Suites:{Colors.RESET}")
                if os.path.exists("test_suites"):
                    for f in os.listdir("test_suites"):
                        if f.endswith(".json"):
                            print(f"  {Colors.CYAN}•{Colors.RESET} {f}")
                else:
                    print(f"  {Colors.DIM}No saved test suites found{Colors.RESET}")
                print()
            
            elif action == "create":
                print(f"\n{Colors.BOLD}Creating New Test Suite{Colors.RESET}")
                name = input("  Suite name: ").strip()
                description = input("  Description: ").strip()
                
                suite = TestSuite(name=name, description=description)
                
                while True:
                    add_test = input("\n  Add test case? (y/n): ").strip().lower()
                    if add_test != 'y':
                        break
                    
                    test_name = input("    Test name: ").strip()
                    method = input("    Method (GET/POST/PUT/DELETE/PATCH): ").strip().upper()
                    url = input("    URL: ").strip()
                    
                    has_headers = input("    Add headers? (y/n): ").strip().lower() == 'y'
                    headers = {}
                    if has_headers:
                        while True:
                            key = input("      Header key (empty to finish): ").strip()
                            if not key:
                                break
                            value = input(f"      {key}: ").strip()
                            headers[key] = value
                    
                    has_body = input("    Add body? (y/n): ").strip().lower() == 'y'
                    body = None
                    if has_body and method in ['POST', 'PUT', 'PATCH']:
                        body_input = input("    Body (JSON string or leave empty): ").strip()
                        if body_input:
                            try:
                                body = json.loads(body_input)
                            except:
                                body = body_input
                    
                    test_case = TestCase(name=test_name, method=method, url=url, headers=headers, body=body)
                    suite.add_test_case(test_case)
                    print(f"    {Colors.GREEN}Test added!{Colors.RESET}")
                
                # 保存测试套件
                os.makedirs("test_suites", exist_ok=True)
                safe_name = name.lower().replace(" ", "_")
                filepath = f"test_suites/{safe_name}.json"
                suite.save_to_file(filepath)
                print(f"\n{Colors.GREEN}Test suite saved to: {filepath}{Colors.RESET}\n")
            
            else:
                print(f"{Colors.RED}Unknown command: {action}{Colors.RESET}")
                print(f"{Colors.DIM}Type 'help' for available commands.{Colors.RESET}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Use 'quit' to exit.{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Smart API Testing Tool - Test and validate REST APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s demo                          Run built-in demo tests
  %(prog)s run tests/api.json            Run test suite from file
  %(prog)s create                        Create new test suite interactively
  %(prog)s single -m GET -u https://httpbin.org/get
                                        Run single HTTP request
        """
    )
    
    parser.add_argument(
        'command',
        choices=['demo', 'run', 'create', 'single'],
        help='Command to execute'
    )
    
    # 单次请求参数
    parser.add_argument('-m', '--method', default='GET', choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                       help='HTTP method (default: GET)')
    parser.add_argument('-u', '--url', help='Request URL')
    parser.add_argument('-H', '--headers', help='Request headers (JSON format)')
    parser.add_argument('-d', '--data', help='Request body data')
    parser.add_argument('-j', '--json', action='store_true', help='Parse body as JSON')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # 测试套件参数
    parser.add_argument('-f', '--file', help='Test suite file path')
    parser.add_argument('--assert-status', type=int, help='Expected status code')
    assert_group = parser.add_argument_group('Assertions')
    assert_group.add_argument('--assert-time', type=int, help='Max response time (ms)')
    assert_group.add_argument('--assert-key', help='Required JSON key')
    assert_group.add_argument('--assert-contains', help='Response must contain text')
    
    args = parser.parse_args()
    
    tester = APITester(timeout=args.timeout, verbose=args.verbose)
    
    if args.command == 'demo':
        OutputFormatter.print_header("API Testing Demo Suite")
        suite = create_sample_test_suite()
        result = tester.run_suite(suite)
        
        for i, test_result in enumerate(result['tests'], 1):
            OutputFormatter.print_test_result(test_result, i)
        
        OutputFormatter.print_suite_summary(result)
    
    elif args.command == 'single':
        if not args.url:
            parser.error("URL is required for single request (-u/--url)")
        
        # 构建测试用例
        headers = {}
        if args.headers:
            try:
                headers = json.loads(args.headers)
            except:
                print(f"{Colors.RED}Invalid JSON headers{Colors.RESET}")
                sys.exit(1)
        
        body = args.data
        if args.json and args.data:
            try:
                body = json.loads(args.data)
            except:
                print(f"{Colors.RED}Invalid JSON body{Colors.RESET}")
                sys.exit(1)
        
        test_case = TestCase(
            name="Single Request",
            method=args.method,
            url=args.url,
            headers=headers,
            body=body
        )
        
        # 添加断言
        if args.assert_status:
            test_case.assertions.append({"type": "status_code", "expected": args.assert_status})
        if args.assert_time:
            test_case.assertions.append({"type": "response_time", "max_ms": args.assert_time})
        if args.assert_key:
            test_case.assertions.append({"type": "json_has_key", "key": args.assert_key})
        if args.assert_contains:
            test_case.assertions.append({"type": "response_contains", "text": args.assert_contains})
        
        OutputFormatter.print_header(f"Single Request: {args.method} {args.url}")
        result = tester.run_test(test_case)
        OutputFormatter.print_test_result(result, 1)
        
        if result['response']:
            OutputFormatter.print_suite_summary({
                'suite_name': 'Single Request',
                'total': 1,
                'passed': 1 if result['passed'] else 0,
                'failed': 0 if result['passed'] else 1,
                'duration_ms': result['response']['duration_ms']
            })
    
    elif args.command == 'run':
        if not args.file:
            parser.error("Test suite file is required (-f/--file)")
        
        if not os.path.exists(args.file):
            print(f"{Colors.RED}Test suite file not found: {args.file}{Colors.RESET}")
            sys.exit(1)
        
        OutputFormatter.print_header(f"Running Test Suite: {args.file}")
        suite = TestSuite.load_from_file(args.file)
        result = tester.run_suite(suite)
        
        for i, test_result in enumerate(result['tests'], 1):
            OutputFormatter.print_test_result(test_result, i)
        
        OutputFormatter.print_suite_summary(result)
    
    elif args.command == 'create':
        interactive_mode()


if __name__ == "__main__":
    main()
