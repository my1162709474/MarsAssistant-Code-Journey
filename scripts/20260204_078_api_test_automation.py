#!/usr/bin/env python3
"""
REST API Test Automation Tool
REST API自动化测试工具

A powerful tool for automated API testing with:
- Request builder with multiple HTTP methods
- Response validation (status code, JSON schema, custom assertions)
- Test suite organization
- Environment variable management
- Report generation (JSON/HTML)
- Request/Response logging

Author: MarsAssistant
Date: 2026-02-04
"""

import json
import time
import uuid
import yaml
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from urllib.parse import urljoin
import requests
from jsonschema import validate, ValidationError as JSONSchemaError


class HTTPMethod(Enum):
    """HTTP请求方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AssertionType(Enum):
    """断言类型枚举"""
    STATUS_CODE = "status_code"
    JSON_SCHEMA = "json_schema"
    JSON_PATH = "json_path"
    HEADER = "header"
    RESPONSE_TIME = "response_time"
    CUSTOM = "custom"


class TestResult(Enum):
    """测试结果枚举"""
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIP = "SKIP"


@dataclass
class Header:
    """HTTP头信息"""
    name: str
    value: str
    description: Optional[str] = None


@dataclass
class RequestConfig:
    """请求配置"""
    method: HTTPMethod
    url: str
    headers: List[Header] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Any] = None
    body_type: str = "json"  # json, form, text, xml
    timeout: int = 30
    verify_ssl: bool = True
    follow_redirects: bool = True
    allow_redirects: bool = True
    
    def get_method(self) -> str:
        """获取HTTP方法字符串"""
        return self.method.value
    
    def get_headers_dict(self) -> Dict[str, str]:
        """获取请求头字典"""
        return {h.name: h.value for h in self.headers}
    
    def get_params(self) -> Dict[str, Any]:
        """获取查询参数"""
        return self.params
    
    def get_body(self) -> Any:
        """获取请求体"""
        return self.body
    
    def get_body_type(self) -> str:
        """获取请求体类型"""
        return self.body_type
    
    def prepare_body(self) -> Any:
        """准备请求体数据"""
        if self.body is None:
            return None
        
        body_type = self.body_type.lower()
        if body_type == "json" and isinstance(self.body, dict):
            return json.dumps(self.body)
        elif body_type == "form":
            return self.body
        elif body_type == "text":
            return str(self.body)
        elif body_type == "xml":
            return str(self.body)
        return self.body


@dataclass
class Assertion:
    """断言配置"""
    type: AssertionType
    expected: Any
    json_path: Optional[str] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "type": self.type.value,
            "expected": self.expected
        }
        if self.json_path:
            result["json_path"] = self.json_path
        if self.message:
            result["message"] = self.message
        return result


@dataclass
class TestCase:
    """测试用例"""
    name: str
    request: RequestConfig
    assertions: List[Assertion] = field(default_factory=list)
    setup_script: Optional[Callable] = None
    teardown_script: Optional[Callable] = None
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    retry_count: int = 0
    retry_delay: int = 1
    
    def get_id(self) -> str:
        """生成测试用例ID"""
        return hashlib.md5(f"{self.name}".encode()).hexdigest()[:8]


@dataclass
class TestResultInfo:
    """测试结果信息"""
    test_case: TestCase
    result: TestResult
    start_time: datetime
    end_time: datetime
    response: Optional[requests.Response] = None
    error_message: Optional[str] = None
    assertions_passed: int = 0
    assertions_failed: int = 0
    details: List[Dict] = field(default_factory=list)
    
    def get_duration(self) -> float:
        """获取测试持续时间（秒）"""
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "test_name": self.test_case.name,
            "result": self.result.value,
            "duration": self.get_duration(),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "assertions": {
                "passed": self.assertions_passed,
                "failed": self.assertions_failed
            },
            "details": self.details
        }
        
        if self.response is not None:
            result["response"] = {
                "status_code": self.response.status_code,
                "headers": dict(self.response.headers),
                "url": self.response.url,
                "elapsed": self.response.elapsed.total_seconds()
            }
            # 限制响应体大小
            try:
                body = self.response.text[:10000]
                result["response"]["body"] = body
                result["response"]["body_preview"] = body[:500]
            except:
                result["response"]["body"] = None
        
        if self.error_message:
            result["error"] = self.error_message
        
        return result


@dataclass
class Environment:
    """测试环境配置"""
    name: str
    base_url: str
    variables: Dict[str, Any] = field(default_factory=dict)
    headers: List[Header] = field(default_factory=list)
    timeout: int = 30
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取环境变量"""
        return self.variables.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置环境变量"""
        self.variables[key] = value
    
    def interpolate(self, text: str) -> str:
        """插值替换环境变量"""
        if not text:
            return text
        
        pattern = r"\{\{(\w+)\}\}"
        
        def replace(match):
            key = match.group(1)
            value = self.get(key, match.group(0))
            return str(value)
        
        return re.sub(pattern, replace, text)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "base_url": self.base_url,
            "variables": self.variables,
            "headers": [asdict(h) for h in self.headers],
            "timeout": self.timeout
        }


class APITestRunner:
    """API测试运行器"""
    
    def __init__(self, environment: Optional[Environment] = None):
        self.environment = environment or Environment(
            name="default",
            base_url=""
        )
        self.test_cases: List[TestCase] = []
        self.results: List[TestResultInfo] = []
        self.session = requests.Session()
        self.global_headers: Dict[str, str] = {}
        
        # 配置会话
        self.session.timeout = self.environment.timeout
        self.session.verify = True
        
        # 添加环境默认头
        for header in self.environment.headers:
            self.global_headers[header.name] = header.value
    
    def add_test_case(self, test_case: TestCase) -> None:
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def add_test_suite(self, test_suite: List[TestCase]) -> None:
        """添加测试套件"""
        self.test_cases.extend(test_suite)
    
    def _build_request(self, test_case: TestCase) -> RequestConfig:
        """构建请求配置"""
        request = test_case.request
        
        # 替换URL中的环境变量
        url = self.environment.interpolate(request.url)
        
        # 如果没有完整URL，添加base_url
        if not url.startswith(("http://", "https://")):
            url = urljoin(self.environment.base_url, url)
        
        # 替换查询参数中的环境变量
        params = {}
        for key, value in request.params.items():
            params[key] = self.environment.interpolate(str(value))
        
        # 替换请求体中的环境变量
        body = request.body
        if isinstance(body, dict):
            body = {}
            for key, value in request.body.items():
                body[key] = self.environment.interpolate(str(value))
        elif isinstance(body, str):
            body = self.environment.interpolate(body)
        
        # 创建新的请求配置
        return RequestConfig(
            method=request.method,
            url=url,
            headers=request.headers,
            params=params,
            body=body,
            body_type=request.body_type,
            timeout=request.timeout or self.environment.timeout,
            verify_ssl=request.verify_ssl,
            follow_redirects=request.follow_redirects,
            allow_redirects=request.allow_redirects
        )
    
    def _execute_request(self, request: RequestConfig) -> requests.Response:
        """执行HTTP请求"""
        # 合并请求头
        headers = self.global_headers.copy()
        for h in request.get_headers_dict():
            headers[h] = self.environment.interpolate(str(headers.get(h, "")))
            headers[h] = self.environment.interpolate(str(request.get_headers_dict()[h]))
        
        # 准备请求体
        body = request.prepare_body()
        
        # 执行请求
        method = request.get_method()
        
        if method == "GET":
            response = self.session.get(
                request.url,
                params=request.get_params(),
                headers=headers,
                timeout=request.timeout,
                verify=request.verify_ssl,
                allow_redirects=request.allow_redirects
            )
        elif method == "POST":
            if request.get_body_type() == "json":
                headers["Content-Type"] = headers.get("Content-Type", "application/json")
                response = self.session.post(
                    request.url,
                    params=request.get_params(),
                    headers=headers,
                    json=body if isinstance(body, dict) else json.loads(body) if body else None,
                    timeout=request.timeout,
                    verify=request.verify_ssl,
                    allow_redirects=request.allow_redirects
                )
            else:
                response = self.session.post(
                    request.url,
                    params=request.get_params(),
                    headers=headers,
                    data=body,
                    timeout=request.timeout,
                    verify=request.verify_ssl,
                    allow_redirects=request.allow_redirects
                )
        elif method == "PUT":
            response = self.session.put(
                request.url,
                params=request.get_params(),
                headers=headers,
                json=body if isinstance(body, dict) else json.loads(body) if body else None,
                timeout=request.timeout,
                verify=request.verify_ssl,
                allow_redirects=request.allow_redirects
            )
        elif method == "PATCH":
            response = self.session.patch(
                request.url,
                params=request.get_params(),
                headers=headers,
                json=body if isinstance(body, dict) else json.loads(body) if body else None,
                timeout=request.timeout,
                verify=request.verify_ssl,
                allow_redirects=request.allow_redirects
            )
        elif method == "DELETE":
            response = self.session.delete(
                request.url,
                params=request.get_params(),
                headers=headers,
                timeout=request.timeout,
                verify=request.verify_ssl,
                allow_redirects=request.allow_redirects
            )
        elif method == "HEAD":
            response = self.session.head(
                request.url,
                params=request.get_params(),
                headers=headers,
                timeout=request.timeout,
                verify=request.verify_ssl,
                allow_redirects=request.allow_redirects
            )
        elif method == "OPTIONS":
            response = self.session.options(
                request.url,
                params=request.get_params(),
                headers=headers,
                timeout=request.timeout,
                verify=request.verify_ssl,
                allow_redirects=request.allow_redirects
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response
    
    def _get_json_path(self, data: Dict, path: str) -> Any:
        """获取JSON路径值"""
        if not path:
            return data
        
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index] if 0 <= index < len(current) else None
                except ValueError:
                    return None
            else:
                return None
            
            if current is None:
                return None
        
        return current
    
    def _evaluate_assertion(self, 
                          assertion: Assertion, 
                          response: requests.Response,
                          response_data: Any) -> tuple[bool, str]:
        """评估断言"""
        try:
            if assertion.type == AssertionType.STATUS_CODE:
                actual = response.status_code
                expected = assertion.expected
                passed = actual == expected
                msg = assertion.message or f"Status code: expected {expected}, got {actual}"
            
            elif assertion.type == AssertionType.JSON_SCHEMA:
                if response_data is None or not isinstance(response_data, dict):
                    return False, "Response is not valid JSON for schema validation"
                validate(instance=response_data, schema=assertion.expected)
                passed = True
                msg = assertion.message or "JSON schema validation passed"
            
            elif assertion.type == AssertionType.JSON_PATH:
                actual = self._get_json_path(response_data, assertion.json_path)
                expected = assertion.expected
                if assertion.json_path is None:
                    return False, "JSON path is required for JSON_PATH assertion"
                passed = actual == expected
                msg = assertion.message or f"JSON path '{assertion.json_path}': expected {expected}, got {actual}"
            
            elif assertion.type == AssertionType.HEADER:
                header_name = assertion.json_path  # 复用json_path字段
                if header_name is None:
                    return False, "Header name is required for HEADER assertion"
                actual = response.headers.get(header_name)
                expected = assertion.expected
                passed = actual == expected
                msg = assertion.message or f"Header '{header_name}': expected {expected}, got {actual}"
            
            elif assertion.type == AssertionType.RESPONSE_TIME:
                actual = response.elapsed.total_seconds() * 1000  # 毫秒
                expected = assertion.expected  # 毫秒
                passed = actual <= expected
                msg = assertion.message or f"Response time: expected <= {expected}ms, got {actual:.2f}ms"
            
            elif assertion.type == AssertionType.CUSTOM:
                # 自定义断言通过回调函数处理
                custom_func = assertion.expected
                if callable(custom_func):
                    passed, msg = custom_func(response, response_data)
                else:
                    passed = False
                    msg = "Custom assertion requires a callable"
            
            else:
                passed = False
                msg = f"Unknown assertion type: {assertion.type}"
        
        except JSONSchemaError as e:
            passed = False
            msg = f"JSON schema validation failed: {str(e)}"
        except Exception as e:
            passed = False            msg = f"Assertion error: {str(e)}"
        
        return passed, msg
    
    def run_test_case(self, test_case: TestCase) -> TestResultInfo:
        """运行单个测试用例"""
        start_time = datetime.now()
        response = None
        error_message = None
        assertions_passed = 0
        assertions_failed = 0
        details = []
        
        try:
            # 构建请求
            request = self._build_request(test_case)
            
            # 执行请求
            response = self._execute_request(request)
            
            # 解析响应JSON
            response_data = None
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    response_data = response.json()
                except:
                    response_data = None
            
            # 评估所有断言
            for assertion in test_case.assertions:
                passed, msg = self._evaluate_assertion(assertion, response, response_data)
                
                detail = {
                    "type": assertion.type.value,
                    "expected": assertion.expected,
                    "passed": passed,
                    "message": msg
                }
                
                if assertion.json_path:
                    detail["json_path"] = assertion.json_path
                
                details.append(detail)
                
                if passed:
                    assertions_passed += 1
                else:
                    assertions_failed += 1
            
            # 判断测试结果
            if assertions_failed == 0 and len(test_case.assertions) > 0:
                result = TestResult.PASS
            elif assertions_failed > 0:
                result = TestResult.FAIL
            else:
                result = TestResult.SKIP  # 没有断言时跳过
        
        except requests.exceptions.Timeout as e:
            error_message = f"Request timeout: {str(e)}"
            result = TestResult.ERROR
        except requests.exceptions.ConnectionError as e:
            error_message = f"Connection error: {str(e)}"
            result = TestResult.ERROR
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            result = TestResult.ERROR
        
        end_time = datetime.now()
        
        return TestResultInfo(
            test_case=test_case,
            result=result,
            start_time=start_time,
            end_time=end_time,
            response=response,
            error_message=error_message,
            assertions_passed=assertions_passed,
            assertions_failed=assertions_failed,
            details=details
        )
    
    def run_all(self, 
               tags: Optional[List[str]] = None,
               name_filter: Optional[str] = None,
               stop_on_failure: bool = False) -> List[TestResultInfo]:
        """运行所有测试用例"""
        self.results = []
        
        # 过滤测试用例
        filtered_cases = []
        for tc in self.test_cases:
            if not tc.enabled:
                continue
            
            if tags:
                if not any(tag in tc.tags for tag in tags):
                    continue
            
            if name_filter and name_filter not in tc.name:
                continue
            
            filtered_cases.append(tc)
        
        # 运行测试
        for i, test_case in enumerate(filtered_cases):
            print(f"[{i+1}/{len(filtered_cases)}] Running: {test_case.name}")
            
            # 重试逻辑
            for attempt in range(tc.retry_count + 1):
                result = self.run_test_case(test_case)
                
                if result.result == TestResult.PASS:
                    break
                
                if attempt < tc.retry_count:
                    print(f"  Retry {attempt + 1}/{tc.retry_count}...")
                    time.sleep(tc.retry_delay)
            
            self.results.append(result)
            
            # 打印结果
            status_symbol = "✅" if result.result == TestResult.PASS else ("❌" if result.result == TestResult.FAIL else "⚠️")
            print(f"  {status_symbol} {result.result.value} ({result.get_duration():.2f}s)")
            
            if result.result != TestResult.PASS and error_message := result.error_message:
                print(f"    Error: {error_message}")
            
            if result.assertions_failed > 0:
                for detail in result.details:
                    if not detail["passed"]:
                        print(f"    ❌ {detail['message']}")
            
            # 失败时停止
            if stop_on_failure and result.result == TestResult.FAIL:
                print("Stopping due to failure...")
                break
        
        return self.results
    
    def get_summary(self) -> Dict:
        """获取测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.result == TestResult.PASS)
        failed = sum(1 for r in self.results if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.results if r.result == TestResult.ERROR)
        skipped = sum(1 for r in self.results if r.result == TestResult.SKIP)
        
        total_assertions = sum(r.assertions_passed + r.assertions_failed for r in self.results)
        passed_assertions = sum(r.assertions_passed for r in self.results)
        failed_assertions = sum(r.assertions_failed for r in self.results)
        
        total_time = sum(r.get_duration() for r in self.results)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
            "total_assertions": total_assertions,
            "passed_assertions": passed_assertions,
            "failed_assertions": failed_assertions,
            "assertions_pass_rate": f"{(passed_assertions / total_assertions * 100):.1f}%" if total_assertions > 0 else "0%",
            "total_time": f"{total_time:.2f}s",
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_report(self, 
                       format: str = "json", 
                       output_path: Optional[str] = None) -> str:
        """生成测试报告"""
        summary = self.get_summary()
        results_data = [r.to_dict() for r in self.results]
        
        report = {
            "summary": summary,
            "results": results_data,
            "environment": self.environment.to_dict()
        }
        
        if format == "json":
            content = json.dumps(report, indent=2, ensure_ascii=False)
            ext = "json"
        elif format == "html":
            content = self._generate_html_report(report)
            ext = "html"
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        
        return content
    
    def _generate_html_report(self, report: Dict) -> str:
        """生成HTML报告"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report - {report['summary']['timestamp']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary h2 {{
            margin-top: 0;
            color: #333;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .stat {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 14px;
        }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        .error {{ color: #ffc107; }}
        .skip {{ color: #6c757d; }}
        .test-case {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .test-name {{
            font-weight: 600;
            color: #333;
        }}
        .test-status {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .test-status.PASS {{ background: #d4edda; color: #155724; }}
        .test-status.FAIL {{ background: #f8d7da; color: #721c24; }}
        .test-status.ERROR {{ background: #fff3cd; color: #856404; }}
        .test-status.SKIP {{ background: #e2e3e5; color: #383d41; }}
        .test-details {{
            font-size: 14px;
            color: #6c757d;
        }}
        .assertion {{
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            background: #f8f9fa;
        }}
        .assertion.pass {{ border-left: 3px solid #28a745; }}
        .assertion.fail {{ border-left: 3px solid #dc3545; }}
    </style>
</head>
<body>
    <h1>API Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{report['summary']['total_tests']}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="stat-value pass">{report['summary']['passed']}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat">
                <div class="stat-value fail">{report['summary']['failed']}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat">
                <div class="stat-value error">{report['summary']['errors']}</div>
                <div class="stat-label">Errors</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report['summary']['pass_rate']}</div>
                <div class="stat-label">Pass Rate</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report['summary']['total_time']}</div>
                <div class="stat-label">Total Time</div>
            </div>
        </div>
    </div>
    
    <h2>Test Results</h2>
"""
        
        for result in report['results']:
            status_class = result['result']
            html += f"""
    <div class="test-case">
        <div class="test-header">
            <span class="test-name">{result['test_name']}</span>
            <span class="test-status {status_class}">{status_class}</span>
        </div>
        <div class="test-details">
            Duration: {result['duration']:.2f}s
"""
            
            if 'error' in result:
                html += f"<br>Error: {result['error']}"
            
            if result.get('response'):
                html += f"<br>Status: {result['response']['status_code']}"
            
            html += "</div>"
            
            for detail in result.get('details', []):
                detail_status = 'pass' if detail['passed'] else 'fail'
                html += f"""
        <div class="assertion {detail_status}">
            {'✅' if detail['passed'] else '❌'} {detail['message']}
        </div>
"""
            
            html += "    </div>"
        
        html += """
</body>
</html>
"""
        return html


def create_sample_test() -> APITestRunner:
    """创建示例测试"""
    # 创建环境
    env = Environment(
        name="test",
        base_url="https://jsonplaceholder.typicode.com",
        variables={
            "userId": 1
        }
    )
    
    runner = APITestRunner(env)
    
    # 测试用例1: 获取用户列表
    runner.add_test_case(TestCase(
        name="Get Users - Validate Status",
        request=RequestConfig(
            method=HTTPMethod.GET,
            url="/users",
            headers=[Header("Accept", "application/json")],
            timeout=10
        ),
        assertions=[
            Assertion(type=AssertionType.STATUS_CODE, expected=200),
            Assertion(type=AssertionType.RESPONSE_TIME, expected=3000, message="Response within 3s"),
        ],
        tags=["smoke", "users"]
    ))
    
    # 测试用例2: 获取单个用户
    runner.add_test_case(TestCase(
        name="Get Single User",
        request=RequestConfig(
            method=HTTPMethod.GET,
            url="/users/{{userId}}",
            headers=[Header("Accept", "application/json")],
            timeout=10
        ),
        assertions=[
            Assertion(type=AssertionType.STATUS_CODE, expected=200),
            Assertion(type=AssertionType.JSON_PATH, expected="id", json_path="id", message="User ID exists"),
            Assertion(type=AssertionType.JSON_PATH, expected="name", json_path="name", message="User name exists"),
        ],
        tags=["smoke", "users"]
    ))
    
    # 测试用例3: 创建新帖子
    runner.add_test_case(TestCase(
        name="Create New Post",
        request=RequestConfig(
            method=HTTPMethod.POST,
            url="/posts",
            headers=[
                Header("Content-Type", "application/json"),
                Header("Accept", "application/json")
            ],
            body={
                "title": "Test Post {{timestamp}}",
                "body": "This is a test post",
                "userId": "{{userId}}"
            },
            body_type="json",
            timeout=10
        ),
        assertions=[
            Assertion(type=AssertionType.STATUS_CODE, expected=201),
            Assertion(type=AssertionType.JSON_PATH, expected=101, json_path="id", message="New post has ID"),
        ],
        tags=["posts", "create"]
    ))
    
    # 测试用例4: 更新帖子
    runner.add_test_case(TestCase(
        name="Update Post",
        request=RequestConfig(
            method=HTTPMethod.PUT,
            url="/posts/1",
            headers=[
                Header("Content-Type", "application/json")
            ],
            body={
                "id": 1,
                "title": "Updated Title",
                "body": "Updated body",
                "userId": 1
            },
            body_type="json",
            timeout=10
        ),
        assertions=[
            Assertion(type=AssertionType.STATUS_CODE, expected=200),
        ],
        tags=["posts", "update"]
    ))
    
    # 测试用例5: 删除帖子
    runner.add_test_case(TestCase(
        name="Delete Post",
        request=RequestConfig(
            method=HTTPMethod.DELETE,
            url="/posts/1",
            timeout=10
        ),
        assertions=[
            Assertion(type=AssertionType.STATUS_CODE, expected=200),
        ],
        tags=["posts", "delete"]
    ))
    
    return runner


def run_demo():
    """运行示例测试"""
    print("🚀 Starting API Test Demo...")
    print("=" * 50)
    
    # 创建测试
    runner = create_sample_test()
    
    # 运行测试
    results = runner.run_all()
    
    # 打印摘要
    print("\n" + "=" * 50)
    summary = runner.get_summary()
    
    print("\n📊 Test Summary:")
    print(f"   Total: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed']}")
    print(f"   ❌ Failed: {summary['failed']}")
    print(f"   ⚠️ Errors: {summary['errors']}")
    print(f"   📈 Pass Rate: {summary['pass_rate']}")
    print(f"   ⏱️ Total Time: {summary['total_time']}")
    
    # 生成报告
    print("\n📄 Generating reports...")
    
    # JSON报告
    json_report = runner.generate_report(format="json")
    with open("test_report.json", "w", encoding="utf-8") as f:
        f.write(json_report)
    print("   ✅ test_report.json")
    
    # HTML报告
    html_report = runner.generate_report(format="html")
    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("   ✅ test_report.html")
    
    print("\n✨ Demo completed!")


if __name__ == "__main__":
    run_demo()
