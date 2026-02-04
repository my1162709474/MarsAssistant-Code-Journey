#!/usr/bin/env python3
"""
HTTP API 测试工具 - Day 80
支持多种HTTP方法、断言验证、响应分析

使用方法:
    python3 api_tester.py --url "https://api.example.com/users" --method GET
    python3 api_tester.py --url "https://api.example.com/users" --method POST --data '{"name":"test"}'
    python3 api_tester.py --url "https://api.example.com/users/1" --method DELETE
"""

import argparse
import json
import sys
import time
import hmac
import hashlib
import urllib.parse
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import urllib.request
import urllib.error
import ssl

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

@dataclass
class APIResponse:
    """API响应对象"""
    status_code: int
    headers: dict
    body: Any
    response_time: float
    url: str
    method: str
    
    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300
    
    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600

@dataclass
class TestAssertion:
    """测试断言"""
    type: str  # status_code, body, header, response_time
    expected: Any
    operator: str = "eq"  # eq, ne, gt, lt, contains, regex
    
    def evaluate(self, response: APIResponse) -> tuple[bool, str]:
        try:
            if self.type == "status_code":
                actual = response.status_code
            elif self.type == "response_time":
                actual = response.response_time
            elif self.type == "body" and isinstance(response.body, dict):
                # 支持点号路径访问，如 "data.user.id"
                keys = self.expected.split(".")
                actual = response.body
                for key in keys:
                    if isinstance(actual, dict) and key in actual:
                        actual = actual[key]
                    else:
                        actual = None
                        break
            elif self.type == "header":
                actual = response.headers.get(self.expected.lower())
            else:
                actual = response.body
            
            # 比较操作
            if self.operator == "eq":
                passed = actual == self.expected
            elif self.operator == "ne":
                passed = actual != self.expected
            elif self.operator == "gt":
                passed = actual > self.expected
            elif self.operator == "lt":
                passed = actual < self.expected
            elif self.operator == "contains":
                passed = str(self.expected) in str(actual)
            elif self.operator == "regex":
                import re
                passed = bool(re.search(str(self.expected), str(actual)))
            else:
                passed = False
            
            msg = f"{self.type}: {actual} {self.operator} {self.expected}" if passed else f"FAILED: {self.type}: {actual} {self.operator} {self.expected}"
            return passed, msg
        except Exception as e:
            return False, f"断言错误: {e}"

@dataclass
class APITestSuite:
    """API测试套件"""
    name: str
    base_url: str
    default_headers: dict = field(default_factory=dict)
    auth: Optional[dict] = None
    assertions: list[TestAssertion] = field(default_factory=list)
    tests: list = field(default_factory=list)

class APITester:
    """HTTP API 测试器"""
    
    def __init__(self, timeout: int = 30, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        self.session_cookies = {}
        self.test_results = []
        
        # 创建SSL上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def _make_request(self, method: str, url: str, headers: dict = None, 
                     data: Any = None, params: dict = None) -> APIResponse:
        """发送HTTP请求"""
        start_time = time.time()
        
        # 处理查询参数
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        
        # 处理请求数据
        if data is not None:
            if isinstance(data, dict):
                body = json.dumps(data, ensure_ascii=False)
                content_type = "application/json"
            else:
                body = str(data)
                content_type = "text/plain"
        else:
            body = None
            content_type = None
        
        # 构建请求头
        req_headers = headers or {}
        if content_type and "Content-Type" not in req_headers:
            req_headers["Content-Type"] = content_type
        
        # 添加默认头
        req_headers.setdefault("User-Agent", "APITester/1.0")
        req_headers.setdefault("Accept", "application/json, text/plain, */*")
        
        # 添加Cookie
        if self.session_cookies:
            cookie_str = "; ".join(f"{k}={v}" for k, v in self.session_cookies.items())
            req_headers["Cookie"] = cookie_str
        
        try:
            req = urllib.request.Request(url, data=body.encode('utf-8') if body else None, 
                                         method=method, headers=req_headers)
            
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as response:
                # 读取响应
                response_body = response.read().decode('utf-8')
                content_type = response.headers.get('Content-Type', '')
                
                # 解析JSON响应
                if 'application/json' in content_type:
                    try:
                        body_parsed = json.loads(response_body)
                    except json.JSONDecodeError:
                        body_parsed = response_body
                else:
                    body_parsed = response_body
                
                # 保存Cookie
                if 'Set-Cookie' in response.headers:
                    self._parse_cookies(response.headers.get('Set-Cookie'))
                
                # 构建响应对象
                resp = APIResponse(
                    status_code=response.status,
                    headers={k.lower(): v for k, v in response.headers.items()},
                    body=body_parsed,
                    response_time=time.time() - start_time,
                    url=url,
                    method=method
                )
                
                return resp
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else None
            try:
                error_body = json.loads(error_body)
            except:
                pass
            
            resp = APIResponse(
                status_code=e.code,
                headers={k.lower(): v for k, v in e.headers.items()} if e.headers else {},
                body=error_body,
                response_time=time.time() - start_time,
                url=url,
                method=method
            )
            return resp
        except urllib.error.URLError as e:
            print(f"URL错误: {e.reason}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"请求错误: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _parse_cookies(self, cookie_header: str):
        """解析Cookie头"""
        for cookie in cookie_header.split(','):
            cookie = cookie.strip()
            if ';' in cookie:
                cookie = cookie.split(';')[0]
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                self.session_cookies[name.strip()] = value.strip()
    
    def _add_auth(self, headers: dict, auth: dict) -> dict:
        """添加认证信息"""
        auth_type = auth.get("type", "bearer").lower()
        
        if auth_type == "bearer":
            headers["Authorization"] = f"Bearer {auth.get('token', '')}"
        elif auth_type == "basic":
            import base64
            credentials = f"{auth.get('username')}:{auth.get('password')}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        elif auth_type == "apikey":
            headers[auth.get("header", "X-API-Key")] = auth.get("key", "")
        elif auth_type == "hmac":
            # HMAC认证
            timestamp = str(int(time.time()))
            nonce = auth.get("nonce", "")
            message = f"{method}{path}{timestamp}{nonce}"
            signature = hmac.new(
                auth.get("secret", "").encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Timestamp"] = timestamp
            headers["X-Nonce"] = nonce
            headers["X-Signature"] = signature
        
        return headers
    
    def test(self, method: str, url: str, headers: dict = None, 
            data: Any = None, params: dict = None, 
            assertions: list = None, auth: dict = None) -> dict:
        """执行API测试"""
        # 合并默认头
        req_headers = headers or {}
        
        # 添加认证
        if auth:
            req_headers = self._add_auth(req_headers, auth)
        
        # 发送请求
        response = self._make_request(method, url, req_headers, data, params)
        
        # 执行断言
        results = {
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "response_time": response.response_time,
            "passed": True,
            "assertions": [],
            "response": response.body if self.verbose else "<<verbose mode>>"
        }
        
        # 默认断言
        default_assertions = [
            TestAssertion("status_code", 200, "eq"),
            TestAssertion("response_time", 5.0, "lt"),  # 5秒内响应
        ]
        
        all_assertions = default_assertions + (assertions or [])
        
        for assertion in all_assertions:
            passed, msg = assertion.evaluate(response)
            results["assertions"].append({
                "passed": passed,
                "message": msg
            })
            if not passed:
                results["passed"] = False
        
        self.test_results.append(results)
        return results
    
    def print_result(self, result: dict, indent: int = 0):
        """打印测试结果"""
        prefix = "  " * indent
        status = "✓" if result["passed"] else "✗"
        
        print(f"{prefix}{status} {result['method']} {result['url']}")
        print(f"{prefix}  状态码: {result['status_code']} | 耗时: {result['response_time']:.3f}s")
        
        for assertion in result["assertions"]:
            mark = "✓" if assertion["passed"] else "✗"
            print(f"{prefix}  {mark} {assertion['message']}")
    
    def print_summary(self):
        """打印测试汇总"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        
        print("\n" + "="*60)
        print(f"测试汇总: {passed}/{total} 通过")
        print(f"通过率: {passed/total*100:.1f}%" if total > 0 else "无测试")
        print("="*60)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="HTTP API 测试工具")
    parser.add_argument("--url", "-u", help="API端点URL")
    parser.add_argument("--method", "-m", default="GET", help="HTTP方法 (默认: GET)")
    parser.add_argument("--data", "-d", help="请求数据 (JSON或字符串)")
    parser.add_argument("--headers", "-H", help="请求头 (JSON格式)")
    parser.add_argument("--params", help="查询参数 (JSON格式)")
    parser.add_argument("--auth", help="认证配置 (JSON格式)")
    parser.add_argument("--assert", "-a", action="append", help="断言 (格式: type:expected:operator)")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示完整响应")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="超时时间 (默认: 30秒)")
    parser.add_argument("--json", "-j", action="store_true", help="输出JSON格式")
    
    # 批量测试模式
    parser.add_argument("--suite", "-s", help="测试套件文件 (JSON格式)")
    parser.add_argument("--file", "-f", help="测试用例文件")
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    tester = APITester(timeout=args.timeout, verbose=args.verbose)
    
    if args.suite:
        # 批量测试模式
        try:
            with open(args.suite, 'r') as f:
                suite_data = json.load(f)
            
            suite = APITestSuite(
                name=suite_data.get("name", "测试套件"),
                base_url=suite_data.get("base_url", ""),
                default_headers=suite_data.get("headers", {}),
                auth=suite_data.get("auth")
            )
            
            for test in suite_data.get("tests", []):
                url = test.get("url", "").format(**suite_data.get("variables", {}))
                full_url = f"{suite.base_url}/{url}".replace("//", "/").replace("https:/", "https://")
                
                result = tester.test(
                    method=test.get("method", "GET"),
                    url=full_url,
                    headers={**suite.default_headers, **test.get("headers", {})},
                    data=test.get("data"),
                    params=test.get("params"),
                    auth=test.get("auth") or suite.auth
                )
                tester.print_result(result)
            
            tester.print_summary()
            
        except FileNotFoundError:
            print(f"文件未找到: {args.suite}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.file:
        # 从文件运行测试
        print(f"从文件加载测试: {args.file}")
        # 这里可以扩展为支持测试文件格式
    
    elif args.url:
        # 单次请求模式
        # 解析断言
        assertions = []
        if args.assert:
            for a in args.assert:
                parts = a.split(":")
                if len(parts) >= 2:
                    assertions.append(TestAssertion(
                        type=parts[0],
                        expected=parts[1],
                        operator=parts[2] if len(parts) > 2 else "eq"
                    ))
        
        # 解析认证
        auth = None
        if args.auth:
            auth = json.loads(args.auth)
        
        # 解析请求头
        headers = None
        if args.headers:
            headers = json.loads(args.headers)
        
        # 解析查询参数
        params = None
        if args.params:
            params = json.loads(args.params)
        
        # 解析数据
        data = None
        if args.data:
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError:
                data = args.data
        
        # 执行测试
        result = tester.test(
            method=args.method.upper(),
            url=args.url,
            headers=headers,
            data=data,
            params=params,
            assertions=assertions,
            auth=auth
        )
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            tester.print_result(result)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
