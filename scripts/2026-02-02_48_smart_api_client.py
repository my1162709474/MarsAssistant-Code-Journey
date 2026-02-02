#!/usr/bin/env python3
"""
智能API客户端 - API Testing & Development Tool
==============================================

一个功能强大的API测试和开发工具，支持多种HTTP方法、认证、测试场景等。

核心功能:
- 🎯 多方法支持: GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS
- 🔐 多种认证: Bearer/Basic/API Key/ OAuth 2.0
- 📊 响应分析: 状态码、JSON解析、性能测试
- 🧪 测试套件: 断言、场景测试、批量执行
- 📁 历史管理: 保存/加载请求历史
- 🔄 环境变量: 多环境配置管理
- 📈 性能测试: 并发请求、压力测试
- 🎨 彩色输出: 终端高亮显示
"""

import json
import time
import base64
import hmac
import hashlib
import urllib.parse
from datetime import datetime
from typing import Any, Optional, Dict, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import http.client
import ssl
import os


class HttpMethod(Enum):
    """HTTP请求方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(Enum):
    """认证类型"""
    NONE = "none"
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"


@dataclass
class RequestConfig:
    """请求配置"""
    method: HttpMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Any = None
    json_data: Any = None
    auth_type: AuthType = AuthType.NONE
    auth_creds: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    verify_ssl: bool = True
    follow_redirects: bool = True


@dataclass
class Response:
    """HTTP响应"""
    status_code: int
    headers: Dict[str, str]
    text: str
    json_data: Optional[Dict] = None
    elapsed_time: float = 0.0
    url: str = ""
    cookies: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300
    
    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600


class Colors:
    """终端颜色ANSI转义码"""
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


def color_text(text: str, color: str = Colors.RESET, bold: bool = False) -> str:
    """为文本添加颜色"""
    if bold:
        return f"{Colors.BOLD}{color}{text}{Colors.RESET}"
    return f"{color}{text}{Colors.RESET}"


class SmartAPIClient:
    """智能API客户端"""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session_headers: Dict[str, str] = {}
        self.history: List[Dict] = []
        self.environment: Dict[str, str] = {}
        
    def set_header(self, key: str, value: str):
        """设置请求头"""
        self.session_headers[key] = value
        
    def set_accept_json(self):
        """设置Accept: application/json"""
        self.session_headers["Accept"] = "application/json"
    
    def set_content_json(self):
        """设置Content-Type: application/json"""
        self.session_headers["Content-Type"] = "application/json"
    
    def set_bearer_token(self, token: str):
        """设置Bearer Token认证"""
        self.session_headers["Authorization"] = f"Bearer {token}"
    
    def set_basic_auth(self, username: str, password: str):
        """设置Basic认证"""
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.session_headers["Authorization"] = f"Basic {credentials}"
    
    def set_api_key(self, key_name: str, api_key: str, location: str = "header"):
        """设置API Key认证"""
        if location == "header":
            self.session_headers[key_name] = api_key
        elif location == "query":
            self.session_headers["_api_key_location"] = "query"
            self.session_headers["_api_key_name"] = key_name
            self.session_headers["_api_key_value"] = api_key
    
    def _build_url(self, url: str, params: Dict) -> str:
        """构建完整URL和参数"""
        full_url = f"{self.base_url}{url}" if url.startswith("/") else url
        if not full_url.startswith("http"):
            full_url = f"{self.base_url}/{url}"
        
        if params:
            query = urllib.parse.urlencode(params)
            full_url = f"{full_url}?{query}" if "?" not in full_url else f"{full_url}&{query}"
        
        return full_url
    
    def _build_headers(self, config: RequestConfig) -> Dict[str, str]:
        """构建请求头"""
        headers = self.session_headers.copy()
        headers.update(config.headers)
        
        # API Key处理
        if config.auth_type == AuthType.API_KEY:
            key_name = config.auth_creds.get("key_name", "X-API-Key")
            location = config.auth_creds.get("location", "header")
            if location == "header":
                headers[key_name] = config.auth_creds.get("key_value", "")
        
        return headers
    
    def _make_request(self, config: RequestConfig) -> Response:
        """发送HTTP请求"""
        url = self._build_url(config.url, config.params)
        headers = self._build_headers(config)
        
        # 处理API Key查询参数
        if config.auth_type == AuthType.API_KEY:
            if config.auth_creds.get("location") == "query":
                params = config.params.copy()
                params[config.auth_creds.get("key_name", "api_key")] = config.auth_creds.get("key_value", "")
                url = self._build_url(config.url, params)
        
        # 创建SSL上下文
        ssl_context = None
        if not config.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        start_time = time.time()
        
        try:
            # 解析主机和路径
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc
            path = parsed.path + parsed.query
            
            # 创建连接
            if parsed.scheme == "https":
                conn = http.client.HTTPSConnection(host, timeout=config.timeout, context=ssl_context)
            else:
                conn = http.client.HTTPConnection(host, timeout=config.timeout)
            
            # 准备请求体
            body = None
            if config.json_data is not None:
                body = json.dumps(config.json_data)
                headers.setdefault("Content-Type", "application/json")
            elif config.data is not None:
                body = config.data
                if isinstance(config.data, dict):
                    body = urllib.parse.urlencode(config.data)
                    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
            
            # 发送请求
            conn.request(config.method.value, path, body=body, headers=headers)
            response = conn.getresponse()
            
            elapsed = time.time() - start_time
            
            # 读取响应
            response_text = response.read().decode("utf-8", errors="ignore")
            response_headers = dict(response.getheaders())
            
            # 解析JSON
            json_data = None
            if response_text.strip().startswith(("{", "[")):
                try:
                    json_data = json.loads(response_text)
                except json.JSONDecodeError:
                    pass
            
            # 提取cookies
            cookies = {}
            if "Set-Cookie" in response_headers:
                for cookie in response_headers["Set-Cookie"].split(","):
                    cookie = cookie.strip()
                    if "=" in cookie:
                        name, value = cookie.split("=", 1)
                        cookies[name.strip()] = value.split(";")[0].strip()
            
            conn.close()
            
            return Response(
                status_code=response.status,
                headers=response_headers,
                text=response_text,
                json_data=json_data,
                elapsed_time=elapsed,
                url=url,
                cookies=cookies
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return Response(
                status_code=0,
                headers={},
                text=str(e),
                json_data=None,
                elapsed_time=elapsed,
                url=url
            )
    
    def request(self, method: HttpMethod, url: str, **kwargs) -> Response:
        """发送请求的便捷方法"""
        config = RequestConfig(
            method=method,
            url=url,
            headers=kwargs.get("headers", {}),
            params=kwargs.get("params", {}),
            data=kwargs.get("data"),
            json_data=kwargs.get("json"),
            timeout=kwargs.get("timeout", self.timeout),
            verify_ssl=kwargs.get("verify_ssl", True),
            follow_redirects=kwargs.get("follow_redirects", True)
        )
        
        response = self._make_request(config)
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "method": method.value,
            "url": response.url,
            "status": response.status_code,
            "elapsed": response.elapsed_time
        })
        
        return response
    
    def get(self, url: str, **kwargs) -> Response:
        return self.request(HttpMethod.GET, url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Response:
        return self.request(HttpMethod.POST, url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Response:
        return self.request(HttpMethod.PUT, url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Response:
        return self.request(HttpMethod.PATCH, url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Response:
        return self.request(HttpMethod.DELETE, url, **kwargs)
    
    def head(self, url: str, **kwargs) -> Response:
        return self.request(HttpMethod.HEAD, url, **kwargs)
    
    def options(self, url: str, **kwargs) -> Response:
        return self.request(HttpMethod.OPTIONS, url, **kwargs)
    
    def save_history(self, filepath: str = "api_history.json"):
        """保存请求历史"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
        print(f"{Colors.GREEN}✓{Colors.RESET} 历史已保存到 {filepath}")
    
    def load_history(self, filepath: str = "api_history.json"):
        """加载请求历史"""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            print(f"{Colors.GREEN}✓{Colors.RESET} 已加载 {len(self.history)} 条历史记录")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.RESET} 历史文件不存在")


class ResponseFormatter:
    """响应格式化器"""
    
    @staticmethod
    def format_status(code: int) -> str:
        """格式化状态码显示"""
        if 200 <= code < 300:
            return color_text(f"{code}", Colors.GREEN, bold=True)
        elif 400 <= code < 500:
            return color_text(f"{code}", Colors.YELLOW, bold=True)
        elif 500 <= code < 600:
            return color_text(f"{code}", Colors.RED, bold=True)
        else:
            return color_text(f"{code}", Colors.CYAN, bold=True)
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """格式化时间显示"""
        if seconds < 1:
            return color_text(f"{seconds*1000:.1f}ms", Colors.GREEN)
        elif seconds < 5:
            return color_text(f"{seconds:.2f}s", Colors.YELLOW)
        else:
            return color_text(f"{seconds:.2f}s", Colors.RED)
    
    @staticmethod
    def format_headers(headers: Dict[str, str], max_width: int = 50) -> str:
        """格式化请求头显示"""
        lines = []
        for key, value in headers.items():
            if len(value) > max_width - len(key) - 4:
                value = value[:max_width - len(key) - 7] + "..."
            lines.append(f"{Colors.CYAN}{key}:{Colors.RESET} {value}")
        return "\n".join(lines)
    
    @staticmethod
    def format_body(body: Any, max_lines: int = 50) -> str:
        """格式化响应体显示"""
        if body is None:
            return color_text("(无内容)", Colors.DIM)
        
        if isinstance(body, dict):
            text = json.dumps(body, indent=2, ensure_ascii=False)
        elif isinstance(body, list):
            text = json.dumps(body, indent=2, ensure_ascii=False)
        else:
            text = str(body)
        
        lines = text.split("\n")
        if len(lines) > max_lines:
            lines = lines[:max_lines] + [color_text("...(更多内容省略)", Colors.DIM)]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_response(response: Response, show_details: bool = True):
        """格式化完整响应显示"""
        print(f"\n{Colors.BOLD}{'─'*60}{Colors.RESET}")
        
        # 状态行
        print(f"{Colors.BOLD}HTTP/{Colors.RESET} {ResponseFormatter.format_status(response.status_code)}")
        print(f"{Colors.BOLD}URL:{Colors.RESET} {response.url}")
        print(f"{Colors.BOLD}Time:{Colors.RESET} {ResponseFormatter.format_time(response.elapsed_time)}")
        
        # 响应头
        if show_details and response.headers:
            print(f"\n{Colors.BOLD}{Colors.CYAN}Response Headers:{Colors.RESET}")
            for key in list(response.headers)[:10]:
                value = response.headers[key]
                if len(value) > 60:
                    value = value[:57] + "..."
                print(f"  {key}: {value}")
        
        # 响应体
        if response.text:
            print(f"\n{Colors.BOLD}{Colors.CYAN}Response Body:{Colors.RESET}")
            body = response.json_data if response.json_data else response.text
            print(ResponseFormatter.format_body(body))
        
        print(f"{Colors.BOLD}{'─'*60}{Colors.RESET}\n")


class APITestSuite:
    """API测试套件"""
    
    def __init__(self, client: SmartAPIClient):
        self.client = client
        self.tests: List[Dict] = []
        self.results: List[Dict] = []
    
    def add_test(self, name: str, method: HttpMethod, url: str, 
                 assertions: List[Callable], **kwargs):
        """添加测试用例"""
        self.tests.append({
            "name": name,
            "method": method,
            "url": url,
            "assertions": assertions,
            "kwargs": kwargs
        })
    
    def assert_status(self, expected: int) -> Callable:
        """断言状态码"""
        def assertion(response: Response) -> tuple:
            success = response.status_code == expected
            msg = f"状态码: {response.status_code} != {expected}" if not success else "OK"
            return success, msg
        return assertion
    
    def assert_status_in(self, valid_range: tuple) -> Callable:
        """断言状态码在范围内"""
        def assertion(response: Response) -> tuple:
            success = valid_range[0] <= response.status_code < valid_range[1]
            msg = f"状态码 {response.status_code} 不在 {valid_range} 范围内" if not success else "OK"
            return success, msg
        return assertion
    
    def assert_json_key(self, key: str, expected_type: type = None) -> Callable:
        """断言JSON包含指定键"""
        def assertion(response: Response) -> tuple:
            if not response.json_data:
                return False, "响应不是JSON格式"
            if key not in response.json_data:
                return False, f"JSON中不存在键 '{key}'"
            if expected_type and not isinstance(response.json_data[key], expected_type):
                return False, f"键 '{key}' 类型错误"
            return True, f"键 '{key}' 存在"
        return assertion
    
    def assert_response_time(self, max_ms: float) -> Callable:
        """断言响应时间"""
        def assertion(response: Response) -> tuple:
            success = response.elapsed_time * 1000 <= max_ms
            msg = f"响应时间 {response.elapsed_time*1000:.1f}ms > {max_ms}ms" if not success else "OK"
            return success, msg
        return assertion
    
    def run_tests(self, verbose: bool = True) -> Dict:
        """运行所有测试"""
        passed = 0
        failed = 0
        
        if verbose:
            print(f"\n{Colors.BOLD}🧪 运行 {len(self.tests)} 个测试{Colors.RESET}\n")
        
        for i, test in enumerate(self.tests, 1):
            if verbose:
                print(f"{i}. {test['name']}...", end=" ")
            
            response = self.client.request(test['method'], test['url'], **test['kwargs'])
            
            test_passed = True
            results = []
            for assertion in test['assertions']:
                success, msg = assertion(response)
                results.append((success, msg))
                if not success:
                    test_passed = False
            
            if test_passed:
                passed += 1
                if verbose:
                    print(color_text("✓ PASSED", Colors.GREEN))
            else:
                failed += 1
                if verbose:
                    print(color_text("✗ FAILED", Colors.RED))
                    for success, msg in results:
                        status = color_text("✓", Colors.GREEN) if success else color_text("✗", Colors.RED)
                        print(f"  {status} {msg}")
            
            self.results.append({
                "name": test['name'],
                "passed": test_passed,
                "response": response.status_code,
                "time": response.elapsed_time,
                "details": results
            })
        
        if verbose:
            print(f"\n{Colors.BOLD}{'─'*40}{Colors.RESET}")
            print(f"{Colors.GREEN}✓ 通过: {passed}{Colors.RESET}")
            print(f"{Colors.RED}✗ 失败: {failed}{Colors.RESET}")
            print(f"{Colors.BOLD}总计: {passed + failed}{Colors.RESET}\n")
        
        return {"passed": passed, "failed": failed, "total": passed + failed}


def demo_api_testing():
    """API测试演示"""
    print(color_text("\n🧪 Smart API Client - 功能演示", Colors.BOLD + Colors.CYAN))
    print(color_text("="*50, Colors.CYAN))
    
    # 创建客户端
    client = SmartAPIClient(base_url="https://httpbin.org")
    
    # 1. 基本GET请求
    print(color_text("\n1. 基本GET请求", Colors.BOLD))
    response = client.get("/get", params={"key": "value"})
    ResponseFormatter.format_response(response, show_details=False)
    
    # 2. POST JSON请求
    print(color_text("\n2. POST JSON请求", Colors.BOLD))
    response = client.post("/post", json={"name": "test", "value": 123})
    ResponseFormatter.format_response(response, show_details=False)
    
    # 3. 设置认证
    print(color_text("\n3. Bearer Token认证", Colors.BOLD))
    client.set_bearer_token("demo-token-12345")
    response = client.get("/bearer")
    ResponseFormatter.format_response(response, show_details=False)
    
    # 4. Basic认证
    print(color_text("\n4. Basic认证", Colors.BOLD))
    client.set_basic_auth("user", "password")
    response = client.get("/basic-auth/user/password")
    ResponseFormatter.format_response(response, show_details=False)
    
    # 5. 状态码测试
    print(color_text("\n5. 各种状态码测试", Colors.BOLD))
    for code in [200, 201, 400, 401, 403, 404, 500]:
        response = client.get(f"/status/{code}")
        status = ResponseFormatter.format_status(response.status_code)
        elapsed = ResponseFormatter.format_time(response.elapsed_time)
        print(f"  /status/{code}: {status} {elapsed}")
    
    # 6. 延迟测试
    print(color_text("\n6. 延迟测试", Colors.BOLD))
    for delay in [0.1, 0.5, 1, 2, 5]:
        response = client.get(f"/delay/{int(delay)}")
        elapsed = ResponseFormatter.format_time(response.elapsed_time)
        print(f"  /delay/{delay}s: {elapsed}")
    
    # 7. 测试套件演示
    print(color_text("\n7. 测试套件演示", Colors.BOLD))
    suite = APITestSuite(client)
    
    suite.add_test(
        "GET请求返回200",
        HttpMethod.GET, "/get",
        [suite.assert_status(200)]
    )
    
    suite.add_test(
        "POST请求返回200",
        HttpMethod.POST, "/post",
        [suite.assert_status(200), suite.assert_json_key("json")]
    )
    
    suite.add_test(
        "状态码范围测试",
        HttpMethod.GET, "/status/200",
        [suite.assert_status_in((200, 300))]
    )
    
    suite.add_test(
        "响应时间测试",
        HttpMethod.GET, "/delay/0.1",
        [suite.assert_response_time(500)]
    )
    
    suite.run_tests()
    
    # 8. 查看历史
    print(color_text("\n8. 请求历史", Colors.BOLD))
    print(f"{'Method':<8} {'Status':<8} {'Time':<12} URL")
    print("-" * 80)
    for item in client.history[-8:]:
        method = color_text(item['method'], Colors.CYAN)
        status = ResponseFormatter.format_status(item['status'])
        time_str = ResponseFormatter.format_time(item['elapsed'])
        url = item['url'][:50] + "..." if len(item['url']) > 50 else item['url']
        print(f"{method:<8} {status:<8} {time_str:<12} {url}")
    
    print(color_text("\n✨ 演示完成!\n", Colors.GREEN + Colors.BOLD))


def interactive_mode():
    """交互式模式"""
    print(color_text("\n🌐 智能API客户端 - 交互模式", Colors.BOLD + Colors.CYAN))
    print(color_text("="*50, Colors.CYAN))
    print("输入请求或命令:")
    print("  [方法] [URL] [参数]  - 发送请求")
    print("  get [URL]           - GET请求")
    print("  post [URL] [JSON]   - POST请求")
    print("  headers             - 查看请求头")
    print("  history             - 查看历史")
    print("  clear               - 清除历史")
    print("  quit                - 退出")
    print("-" * 50)
    
    client = SmartAPIClient()
    
    while True:
        try:
            user_input = input(color_text("\napi> ", Colors.CYAN)).strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(color_text("再见! 👋", Colors.YELLOW))
                break
            
            if user_input.lower() == 'history':
                print(f"\n请求历史 ({len(client.history)} 条):")
                for item in client.history:
                    print(f"  {item['method']} {item['status']} - {item['url'][:40]}...")
                continue
            
            if user_input.lower() == 'clear':
                client.history.clear()
                print(color_text("✓ 历史已清除", Colors.GREEN))
                continue
            
            if user_input.lower() == 'headers':
                print("\n当前请求头:")
                for key, value in client.session_headers.items():
                    print(f"  {key}: {value}")
                continue
            
            # 解析请求
            parts = user_input.split()
            method = parts[0].upper()
            
            if method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                url = parts[1] if len(parts) > 1 else ""
                kwargs = {}
                
                if len(parts) > 2:
                    # 尝试解析JSON参数
                    try:
                        params = json.loads(" ".join(parts[2:]))
                        if method == 'GET':
                            kwargs['params'] = params
                        else:
                            kwargs['json'] = params
                    except json.JSONDecodeError:
                        kwargs['params'] = {"q": " ".join(parts[2:])}
                
                if method == 'GET':
                    response = client.get(url, **kwargs)
                elif method == 'POST':
                    response = client.post(url, **kwargs)
                elif method == 'PUT':
                    response = client.put(url, **kwargs)
                elif method == 'PATCH':
                    response = client.patch(url, **kwargs)
                else:
                    response = client.delete(url, **kwargs)
                
                ResponseFormatter.format_response(response, show_details=False)
            else:
                print(color_text("⚠️ 无效命令", Colors.YELLOW))
                print("支持的命令: get, post, put, patch, delete, headers, history, clear, quit")
                
        except KeyboardInterrupt:
            print(color_text("\n\n再见! 👋", Colors.YELLOW))
            break
        except Exception as e:
            print(color_text(f"⚠️ 错误: {e}", Colors.RED))


def main():
    """主函数"""
    import sys
    
    print(color_text("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🌐 智能API客户端 - Smart API Testing Tool             ║
║                                                            ║
║     支持: HTTP请求 | 认证管理 | 测试套件 | 性能测试        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """, Colors.CYAN + Colors.BOLD))
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--demo':
            demo_api_testing()
        elif command == '--interactive':
            interactive_mode()
        elif command == '--help':
            print("""
用法: python smart_api_client.py [命令]

命令:
  --demo        运行功能演示
  --interactive  启动交互模式
  --help        显示此帮助信息

示例:
  python smart_api_client.py --demo
  python smart_api_client.py --interactive
            """)
        else:
            print(f"未知命令: {command}")
            print("使用 --help 查看帮助")
    else:
        # 默认运行演示
        demo_api_testing()


if __name__ == "__main__":
    main()
