#!/usr/bin/env python3
"""
智能API测试工具 - Smart API Tester
自动测试API端点、验证响应、生成测试报告

功能特性:
- 🚀 多种HTTP方法支持 (GET/POST/PUT/DELETE/PATCH)
- 📊 响应验证与断言
- 🔒 认证方式支持 (Bearer/API Key/Basic Auth)
- ⏱️ 性能测试与延迟统计
- 📈 测试报告生成
- 🔄 批量测试执行
- 🧪 测试用例管理

作者: AI Assistant
日期: 2026-02-03
"""

import json
import time
importstatistics
import requests
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


class HTTPMethod(Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AssertionType(Enum):
    """断言类型枚举"""
    STATUS_CODE = "status_code"
    JSON_VALID = "json_valid"
    JSON_KEY = "json_key"
    JSON_VALUE = "json_value"
    RESPONSE_TIME = "response_time"
    HEADER = "header"
    BODY_CONTAINS = "body_contains"
    BODY_EQUALS = "body_equals"


@dataclass
class Assertion:
    """断言定义"""
    type: AssertionType
    expected: Any
    description: str = ""
    
    def validate(self, response: requests.Response, response_time: float) -> tuple[bool, str]:
        """验证断言"""
        try:
            if self.type == AssertionType.STATUS_CODE:
                actual = response.status_code
                success = actual == self.expected
                return success, f"状态码: {actual} {'==' if success else '!='} {self.expected}"
            
            elif self.type == AssertionType.JSON_VALID:
                try:
                    response.json()
                    return True, "JSON格式有效"
                except:
                    return False, "JSON格式无效"
            
            elif self.type == AssertionType.JSON_KEY:
                try:
                    data = response.json()
                    keys = self.expected if isinstance(self.expected, list) else [self.expected]
                    for key in keys:
                        if key not in data:
                            return False, f"缺少键: {key}"
                    return True, f"包含所有键: {keys}"
                except:
                    return False, "JSON解析失败"
            
            elif self.type == AssertionType.JSON_VALUE:
                try:
                    data = response.json()
                    key, expected_val = self.expected
                    actual_val = data.get(key)
                    success = str(actual_val) == str(expected_val)
                    return success, f"{key}: {actual_val} {'==' if success else '!='} {expected_val}"
                except Exception as e:
                    return False, f"值验证失败: {e}"
            
            elif self.type == AssertionType.RESPONSE_TIME:
                # 响应时间阈值(毫秒)
                max_time = self.expected  # 毫秒
                actual_time = response_time * 1000  # 转换为毫秒
                success = actual_time <= max_time
                return success, f"响应时间: {actual_time:.2f}ms {'<=' if success else '>'} {max_time}ms"
            
            elif self.type == AssertionType.HEADER:
                header_name, expected_val = self.expected
                actual_val = response.headers.get(header_name)
                success = actual_val == expected_val
                return success, f"Header {header_name}: {actual_val} {'==' if success else '!='} {expected_val}"
            
            elif self.type == AssertionType.BODY_CONTAINS:
                success = self.expected in response.text
                return success, f"响应体{'包含' if success else '不包含'}: {self.expected[:50]}..."
            
            elif self.type == AssertionType.BODY_EQUALS:
                success = response.text.strip() == self.expected.strip()
                return success, f"响应体{'等于' if success else '不等于'}预期"
            
            return True, "未知断言类型"
        except Exception as e:
            return False, f"断言验证异常: {e}"


@dataclass
class TestCase:
    """测试用例"""
    name: str
    method: HTTPMethod
    endpoint: str
    description: str = ""
    
    # 请求参数
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Union[Dict, str]] = None
    
    # 认证
    auth_type: Optional[str] = None  # "bearer", "api_key", "basic"
    auth_credentials: Dict[str, str] = field(default_factory=dict)
    
    # 断言
    assertions: List[Assertion] = field(default_factory=list)
    
    # 设置/清理
    setup_hook: Optional[Callable] = None
    teardown_hook: Optional[Callable] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "method": self.method.value,
            "endpoint": self.endpoint,
            "description": self.description,
            "headers": self.headers,
            "params": self.params,
            "body": self.body,
            "auth_type": self.auth_type,
            "auth_credentials": self.auth_credentials,
            "assertions": [
                {
                    "type": a.type.value,
                    "expected": a.expected,
                    "description": a.description
                }
                for a in self.assertions
            ]
        }


@dataclass
class TestResult:
    """测试结果"""
    test_case: TestCase
    passed: bool
    status_code: Optional[int]
    response_time: float  # 秒
    response_body: Optional[Any]
    response_headers: Dict[str, str]
    assertions_result: List[tuple]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "name": self.test_case.name,
            "passed": self.passed,
            "status_code": self.status_code,
            "response_time_ms": round(self.response_time * 1000, 2),
            "response_body": self.response_body,
            "assertions": [
                {"passed": p, "description": d}
                for p, d in self.assertions_result
            ],
            "error": self.error_message
        }


class APITester:
    """API测试器主类"""
    
    def __init__(self, base_url: str = "", timeout: float = 30.0):
        """
        初始化API测试器
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间(秒)
        """
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.timeout = timeout
        self.session = requests.Session()
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
        
        # 环境变量
        self.env: Dict[str, str] = {}
    
    def add_header(self, key: str, value: str):
        """添加请求头"""
        self.session.headers[key] = value
        return self
    
    def set_auth(self, auth_type: str, **credentials):
        """设置认证"""
        self.session.auth = self._create_auth(auth_type, credentials)
        return self
    
    def _create_auth(self, auth_type: str, credentials: Dict) -> Any:
        """创建认证对象"""
        if auth_type.lower() == "bearer":
            from requests.auth import HTTPBearerAuth
            return HTTPBearerAuth(credentials.get("token", ""))
        elif auth_type.lower() == "basic":
            from requests.auth import HTTPBasicAuth
            return HTTPBasicAuth(
                credentials.get("username", ""),
                credentials.get("password", "")
            )
        return None
    
    def set_env(self, key: str, value: str):
        """设置环境变量(用于动态替换)"""
        self.env[key] = value
        return self
    
    def _replace_env_vars(self, text: Any) -> Any:
        """替换环境变量"""
        if isinstance(text, str):
            for key, value in self.env.items():
                text = text.replace(f"${{{key}}}", value)
                text = text.replace(f"${key}", value)
            return text
        elif isinstance(text, dict):
            return {k: self._replace_env_vars(v) for k, v in text.items()}
        elif isinstance(text, list):
            return [self._replace_env_vars(item) for item in text]
        return text
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
        return self
    
    def create_test_case(
        self,
        name: str,
        method: Union[str, HTTPMethod],
        endpoint: str,
        **kwargs
    ) -> TestCase:
        """创建并添加测试用例"""
        if isinstance(method, str):
            method = HTTPMethod(method.upper())
        
        test_case = TestCase(
            name=name,
            method=method,
            endpoint=endpoint,
            **kwargs
        )
        self.add_test_case(test_case)
        return test_case
    
    def execute_single(self, test_case: TestCase) -> TestResult:
        """执行单个测试用例"""
        start_time = time.time()
        error_msg = None
        status_code = None
        response_body = None
        response_headers = {}
        assertions_result = []
        
        try:
            # 替换环境变量
            endpoint = self._replace_env_vars(test_case.endpoint)
            url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
            
            params = self._replace_env_vars(test_case.params)
            headers = self._replace_env_vars(test_case.headers)
            body = self._replace_env_vars(test_case.body)
            
            # 处理认证头
            if test_case.auth_type:
                if test_case.auth_type.lower() == "bearer":
                    headers["Authorization"] = f"Bearer {test_case.auth_credentials.get('token', '')}"
                elif test_case.auth_type.lower() == "api_key":
                    header_name = test_case.auth_credentials.get("header_name", "X-API-Key")
                    headers[header_name] = test_case.auth_credentials.get("api_key", "")
            
            # 执行setup hook
            if test_case.setup_hook:
                test_case.setup_hook()
            
            # 发送请求
            response = self.session.request(
                method=test_case.method.value,
                url=url,
                headers=headers,
                params=params,
                json=body if isinstance(body, dict) else None,
                data=body if isinstance(body, str) else None,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            status_code = response.status_code
            response_headers = dict(response.headers)
            
            # 解析响应体
            try:
                response_body = response.json()
            except:
                response_body = response.text
            
            # 执行断言
            all_passed = True
            for assertion in test_case.assertions:
                passed, desc = assertion.validate(response, response_time)
                assertions_result.append((passed, desc))
                if not passed:
                    all_passed = False
            
            # 执行teardown hook
            if test_case.teardown_hook:
                test_case.teardown_hook()
            
            return TestResult(
                test_case=test_case,
                passed=all_passed,
                status_code=status_code,
                response_time=response_time,
                response_body=response_body,
                response_headers=response_headers,
                assertions_result=assertions_result
            )
            
        except requests.exceptions.Timeout:
            error_msg = f"请求超时 ({self.timeout}s)"
            return TestResult(
                test_case=test_case,
                passed=False,
                status_code=None,
                response_time=self.timeout,
                response_body=None,
                response_headers={},
                assertions_result=[],
                error_message=error_msg
            )
        except requests.exceptions.RequestException as e:
            error_msg = f"请求失败: {str(e)}"
            return TestResult(
                test_case=test_case,
                passed=False,
                status_code=None,
                response_time=time.time() - start_time,
                response_body=None,
                response_headers={},
                assertions_result=[],
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            return TestResult(
                test_case=test_case,
                passed=False,
                status_code=None,
                response_time=time.time() - start_time,
                response_body=None,
                response_headers={},
                assertions_result=[],
                error_message=error_msg
            )
    
    def execute_all(self, parallel: bool = False, max_workers: int = 5) -> List[TestResult]:
        """执行所有测试用例"""
        self.results = []
        
        if parallel:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.execute_single, tc): tc 
                    for tc in self.test_cases
                }
                for future in as_completed(futures):
                    self.results.append(future.result())
        else:
            for test_case in self.test_cases:
                result = self.execute_single(test_case)
                self.results.append(result)
        
        return self.results
    
    def generate_report(self, format: str = "text") -> str:
        """生成测试报告"""
        if not self.results:
            return "没有测试结果"
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results)) * 100
        
        response_times = [r.response_time for r in self.results]
        avg_time = statistics.mean(response_times) if response_times else 0
        min_time = min(response_times) if response_times else 0
        max_time = max(response_times) if response_times else 0
        
        if format == "json":
            return json.dumps({
                "summary": {
                    "total": len(self.results),
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": f"{pass_rate:.2f}%",
                    "avg_response_time_ms": round(avg_time * 1000, 2),
                    "min_response_time_ms": round(min_time * 1000, 2),
                    "max_response_time_ms": round(max_time * 1000, 2)
                },
                "results": [r.to_dict() for r in self.results]
            }, indent=2, ensure_ascii=False)
        
        # 文本格式
        lines = []
        lines.append("=" * 60)
        lines.append("📊 API测试报告")
        lines.append("=" * 60)
        lines.append(f"总测试数: {len(self.results)}")
        lines.append(f"✅ 通过: {passed}")
        lines.append(f"❌ 失败: {failed}")
        lines.append(f"📈 通过率: {pass_rate:.2f}%")
        lines.append(f"⏱️ 平均响应时间: {avg_time*1000:.2f}ms")
        lines.append(f"⚡ 最短响应时间: {min_time*1000:.2f}ms")
        lines.append(f"🐢 最长响应时间: {max_time*1000:.2f}ms")
        lines.append("-" * 60)
        lines.append("详细结果:")
        lines.append("-" * 60)
        
        for i, result in enumerate(self.results, 1):
            status = "✅" if result.passed else "❌"
            lines.append(f"\n{status} [{i}] {result.test_case.name}")
            lines.append(f"   端点: {result.test_case.method.value} {result.test_case.endpoint}")
            
            if result.error_message:
                lines.append(f"   错误: {result.error_message}")
            else:
                lines.append(f"   状态码: {result.status_code}")
                lines.append(f"   响应时间: {result.response_time*1000:.2f}ms")
                
                lines.append("   断言结果:")
                for passed, desc in result.assertions_result:
                    icon = "✅" if passed else "❌"
                    lines.append(f"     {icon} {desc}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def print_report(self):
        """打印测试报告"""
        print(self.generate_report())
    
    def save_report(self, filepath: str, format: str = "text"):
        """保存测试报告"""
        report = self.generate_report(format)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {filepath}")
    
    def load_test_cases_from_json(self, filepath: str):
        """从JSON文件加载测试用例"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data.get("test_cases", []):
            test_case = TestCase(
                name=item["name"],
                method=HTTPMethod(item["method"]),
                endpoint=item["endpoint"],
                description=item.get("description", ""),
                headers=item.get("headers", {}),
                params=item.get("params", {}),
                body=item.get("body"),
                auth_type=item.get("auth_type"),
                auth_credentials=item.get("auth_credentials", {}),
                assertions=[
                    Assertion(
                        type=AssertionType(a["type"]),
                        expected=a["expected"],
                        description=a.get("description", "")
                    )
                    for a in item.get("assertions", [])
                ]
            )
            self.add_test_case(test_case)
        
        if "base_url" in data:
            self.base_url = data["base_url"]
        
        print(f"📥 已加载 {len(self.test_cases)} 个测试用例")
        return self


# ==================== 便捷函数 ====================

def quick_test(
    url: str,
    method: str = "GET",
    expected_status: int = 200,
    max_time_ms: int = 3000
) -> TestResult:
    """快速测试单个API端点"""
    tester = APITester()
    test_case = TestCase(
        name=f"Quick Test: {method} {url}",
        method=HTTPMethod(method.upper()),
        endpoint=url,
        assertions=[
            Assertion(
                type=AssertionType.STATUS_CODE,
                expected=expected_status,
                description="验证状态码"
            ),
            Assertion(
                type=AssertionType.RESPONSE_TIME,
                expected=max_time_ms,
                description="验证响应时间"
            )
        ]
    )
    return tester.execute_single(test_case)


def create_test_suite(name: str, base_url: str = "") -> APITester:
    """创建测试套件"""
    return APITester(base_url=base_url)


# ==================== 示例和演示 ====================

def demo():
    """演示API测试器的使用"""
    print("🚀 智能API测试器演示")
    print("=" * 50)
    
    # 创建测试器
    tester = APITester(base_url="https://jsonplaceholder.typicode.com")
    
    # 添加测试用例
    tester.add_test_case(TestCase(
        name="获取用户列表",
        method=HTTPMethod.GET,
        endpoint="/users",
        description="验证用户列表接口",
        assertions=[
            Assertion(
                type=AssertionType.STATUS_CODE,
                expected=200,
                description="状态码应为200"
            ),
            Assertion(
                type=AssertionType.JSON_VALID,
                expected=True,
                description="响应应为有效JSON"
            ),
            Assertion(
                type=AssertionType.JSON_KEY,
                expected=["id", "name", "email"],
                description="响应应包含用户基本信息"
            ),
            Assertion(
                type=AssertionType.RESPONSE_TIME,
                expected=3000,
                description="响应时间应小于3秒"
            )
        ]
    ))
    
    tester.add_test_case(TestCase(
        name="获取单个用户",
        method=HTTPMethod.GET,
        endpoint="/users/1",
        description="验证单个用户接口",
        assertions=[
            Assertion(type=AssertionType.STATUS_CODE, expected=200),
            Assertion(
                type=AssertionType.JSON_VALUE,
                expected=("id", 1),
                description="用户ID应为1"
            )
        ]
    ))
    
    tester.add_test_case(TestCase(
        name="创建新帖子",
        method=HTTPMethod.POST,
        endpoint="/posts",
        description="验证创建帖子接口",
        headers={"Content-Type": "application/json"},
        body={"title": "测试标题", "body": "测试内容", "userId": 1},
        assertions=[
            Assertion(type=AssertionType.STATUS_CODE, expected=201),
            Assertion(
                type=AssertionType.JSON_KEY,
                expected=["id", "title"],
                description="响应应包含新创建帖子的信息"
            )
        ]
    ))
    
    # 设置环境变量
    tester.set_env("USER_ID", "1")
    
    # 执行测试
    print("\n📋 测试用例:")
    for i, tc in enumerate(tester.test_cases, 1):
        print(f"  {i}. {tc.name} - {tc.method.value} {tc.endpoint}")
    
    print("\n⚡ 执行测试...")
    results = tester.execute_all()
    
    # 生成报告
    print("\n" + tester.generate_report())
    
    # 保存JSON报告
    json_report = tester.generate_report("json")
    print("\n📊 JSON格式报告:")
    print(json_report)


if __name__ == "__main__":
    demo()
