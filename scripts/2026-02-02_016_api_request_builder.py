#!/usr/bin/env python3
"""
智能API请求构建器 - Day 16
帮助构建、测试和调试HTTP API请求

功能:
- 支持GET/POST/PUT/PATCH/DELETE等方法
- 自动处理JSON请求/响应
- 请求头管理
- 认证支持（API Key、Bearer Token、Basic Auth）
- 响应分析和高亮显示
- 请求历史记录
"""

import json
import base64
import urllib.parse
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"


@dataclass
class RequestHeader:
    """请求头"""
    key: str
    value: str
    description: str = ""


@dataclass
class QueryParam:
    """查询参数"""
    key: str
    value: str
    description: str = ""


@dataclass
class AuthConfig:
    """认证配置"""
    type: AuthType = AuthType.NONE
    api_key: str = ""
    api_key_header: str = "X-API-Key"
    bearer_token: str = ""
    username: str = ""
    password: str = ""


@dataclass
class APIRequest:
    """API请求配置"""
    method: HTTPMethod = HTTPMethod.GET
    url: str = ""
    headers: list = field(default_factory=list)
    params: list = field(default_factory=list)
    body: Optional[dict] = None
    auth: AuthConfig = field(default_factory=AuthConfig)
    timeout: int = 30
    follow_redirects: bool = True
    
    def build_url(self) -> str:
        """构建完整URL（含查询参数）"""
        if not self.url:
            return ""
        
        # 添加查询参数
        if self.params:
            query_parts = []
            for p in self.params:
                encoded_key = urllib.parse.quote(str(p.key))
                encoded_value = urllib.parse.quote(str(p.value))
                query_parts.append(f"{encoded_key}={encoded_value}")
            
            separator = "&" if "?" in self.url else "?"
            return f"{self.url}{separator}{'&'.join(query_parts)}"
        
        return self.url
    
    def get_headers_dict(self) -> dict:
        """获取请求头字典"""
        headers = {}
        for h in self.headers:
            headers[h.key] = h.value
        return headers


class ResponseAnalyzer:
    """API响应分析器"""
    
    @staticmethod
    def format_json(data: Any, indent: int = 2) -> str:
        """格式化JSON输出"""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(data)
    
    @staticmethod
    def analyze_status(status_code: int) -> str:
        """分析HTTP状态码"""
        if 100 <= status_code < 200:
            return "🔵 信息响应 (1xx)"
        elif 200 <= status_code < 300:
            return "✅ 成功 (2xx)"
        elif 300 <= status_code < 400:
            return "🔴 重定向 (3xx)"
        elif 400 <= status_code < 500:
            return "⚠️ 客户端错误 (4xx)"
        elif 500 <= status_code < 600:
            return "❌ 服务器错误 (5xx)"
        else:
            return "❓ 未知状态"
    
    @staticmethod
    def calculate_size(data: Any) -> str:
        """计算响应大小"""
        import sys
        try:
            content = json.dumps(data, ensure_ascii=False)
            size = sys.getsizeof(content.encode('utf-8'))
            
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except Exception:
            return "未知"
    
    @staticmethod
    def check_json_structure(data: dict) -> dict:
        """检查JSON结构"""
        info = {
            "keys_count": len(data.keys()) if isinstance(data, dict) else 0,
            "depth": ResponseAnalyzer._get_depth(data),
            "types": ResponseAnalyzer._count_types(data)
        }
        return info
    
    @staticmethod
    def _get_depth(obj, current_depth: int = 0) -> int:
        """获取嵌套深度"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(ResponseAnalyzer._get_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(ResponseAnalyzer._get_depth(item, current_depth + 1) for item in obj)
        return current_depth
    
    @staticmethod
    def _count_types(obj, counts: dict = None) -> dict:
        """统计类型分布"""
        if counts is None:
            counts = {}
        
        obj_type = type(obj).__name__
        counts[obj_type] = counts.get(obj_type, 0) + 1
        
        if isinstance(obj, dict):
            for v in obj.values():
                ResponseAnalyzer._count_types(v, counts)
        elif isinstance(obj, list):
            for item in obj:
                ResponseAnalyzer._count_types(item, counts)
        
        return counts


class APIRequestBuilder:
    """API请求构建器主类"""
    
    def __init__(self):
        self.request_history: list = []
    
    def create_request(self) -> APIRequest:
        """创建新请求"""
        return APIRequest()
    
    def set_url(self, request: APIRequest, url: str):
        """设置请求URL"""
        request.url = url
    
    def add_header(self, request: APIRequest, key: str, value: str, description: str = ""):
        """添加请求头"""
        request.headers.append(RequestHeader(key, value, description))
    
    def add_param(self, request: APIRequest, key: str, value: str, description: str = ""):
        """添加查询参数"""
        request.params.append(QueryParam(key, value, description))
    
    def set_json_body(self, request: APIRequest, data: dict):
        """设置JSON请求体"""
        request.body = data
        # 自动添加Content-Type头
        self._ensure_content_type(request)
    
    def _ensure_content_type(self, request: APIRequest):
        """确保有Content-Type头"""
        has_content_type = any(
            h.key.lower() == "content-type" for h in request.headers
        )
        if not has_content_type:
            request.headers.append(
                RequestHeader("Content-Type", "application/json", "JSON内容类型")
            )
    
    def set_auth(self, request: APIRequest, auth: AuthConfig):
        """设置认证"""
        request.auth = auth
        self._add_auth_headers(request)
    
    def _add_auth_headers(self, request: APIRequest):
        """添加认证头"""
        auth = request.auth
        
        if auth.type == AuthType.API_KEY:
            self.add_header(request, auth.api_key_header, auth.api_key, "API Key认证")
        elif auth.type == AuthType.BEARER:
            self.add_header(request, "Authorization", f"Bearer {auth.bearer_token}", "Bearer Token认证")
        elif auth.type == AuthType.BASIC:
            credentials = f"{auth.username}:{auth.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            self.add_header(request, "Authorization", f"Basic {encoded}", "Basic认证")
    
    def build_curl_command(self, request: APIRequest) -> str:
        """构建cURL命令"""
        url = request.build_url()
        
        parts = ["curl"]
        
        # 方法
        if request.method != HTTPMethod.GET:
            parts.append(f"-X {request.method.value}")
        
        # URL
        parts.append(f"'{url}'")
        
        # 请求头
        for h in request.headers:
            parts.append(f"-H '{h.key}: {h.value}'")
        
        # 请求体
        if request.body and request.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            body_str = json.dumps(request.body, ensure_ascii=False)
            parts.append(f"-d '{body_str}'")
        
        return " ".join(parts)
    
    def build_python_request(self, request: APIRequest) -> str:
        """构建Python requests代码"""
        url = request.build_url()
        
        lines = [
            "import requests",
            "",
            f"url = '{url}'",
            ""
        ]
        
        if request.headers:
            lines.append("headers = {")
            for h in request.headers:
                lines.append(f"    '{h.key}': '{h.value}',")
            lines.append("}")
            lines.append("")
        
        if request.body:
            lines.append("payload = " + json.dumps(request.body, indent=4, ensure_ascii=False))
            lines.append("")
        
        # 方法调用
        method = request.method.value.lower()
        if request.body:
            lines.append(f"response = requests.{method}(url, headers=headers, json=payload)")
        else:
            lines.append(f"response = requests.{method}(url, headers=headers)")
        
        lines.extend([
            "",
            "print(f'Status: {response.status_code}')",
            "print(f'Response: {response.json()}')"
        ])
        
        return "\n".join(lines)
    
    def analyze_response(self, status_code: int, response_data: Any) -> dict:
        """分析响应"""
        return {
            "status_code": status_code,
            "status_analysis": ResponseAnalyzer.analyze_status(status_code),
            "size": ResponseAnalyzer.calculate_size(response_data),
            "structure": ResponseAnalyzer.check_json_structure(response_data) if isinstance(response_data, dict) else {},
            "formatted": ResponseAnalyzer.format_json(response_data)
        }
    
    def save_history(self, request: APIRequest, response_info: dict):
        """保存请求历史"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method.value,
            "url": request.build_url(),
            "status_code": response_info.get("status_code"),
            "response_size": response_info.get("size")
        }
        self.request_history.append(entry)


def demo():
    """演示"""
    builder = APIRequestBuilder()
    
    # 创建请求
    request = builder.create_request()
    builder.set_url(request, "https://jsonplaceholder.typicode.com/posts")
    builder.add_header(request, "Accept", "application/json")
    
    # 设置Bearer认证
    auth = AuthConfig(type=AuthType.BEARER, bearer_token="your-token-here")
    builder.set_auth(request, auth)
    
    # 添加查询参数
    builder.add_param(request, "userId", "1", "用户ID过滤")
    
    # 打印构建的URL
    print("📡 请求URL:", request.build_url())
    print()
    
    # 生成cURL命令
    print("🔧 cURL命令:")
    print(builder.build_curl_command(request))
    print()
    
    # 生成Python代码
    print("🐍 Python代码:")
    print(builder.build_python_request(request))
    print()
    
    # 模拟响应分析
    sample_response = {
        "userId": 1,
        "id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
    }
    
    analysis = builder.analyze_response(200, sample_response)
    print("📊 响应分析:")
    print(f"  状态: {analysis['status_analysis']}")
    print(f"  大小: {analysis['size']}")
    print(f"  键数量: {analysis['structure'].get('keys_count', 'N/A')}")
    print(f"  嵌套深度: {analysis['structure'].get('depth', 'N/A')}")


if __name__ == "__main__":
    demo()
