#!/usr/bin/env python3
"""
Day 62: 智能API客户端生成器 🤖
=============================
自动生成各种API的Python客户端代码，支持主流服务

功能:
- 自动检测API文档格式
- 生成完整的客户端代码
- 支持错误处理和重试机制
- 自动生成类型提示
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib


class APIDocFormat(Enum):
    """支持的API文档格式"""
    OPENAPI = "openapi"
    POSTMAN = "postman"
    RAML = "raml"
    GRAPHQL = "graphql"
    UNKNOWN = "unknown"


@dataclass
class APIEndpoint:
    """API端点信息"""
    path: str
    method: str
    summary: str
    description: str = ""
    parameters: List[Dict] = field(default_factory=list)
    request_body: Optional[Dict] = None
    responses: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class APIClientGenerator:
    """API客户端生成器"""
    
    def __init__(self, api_name: str, base_url: str):
        self.api_name = api_name
        self.base_url = base_url.rstrip('/')
        self.endpoints: List[APIEndpoint] = []
        self.auth_type = "bearer"
        self.imports = set()
        
    def add_endpoint(self, endpoint: APIEndpoint):
        """添加API端点"""
        self.endpoints.append(endpoint)
        
    def detect_doc_format(self, content: str) -> APIDocFormat:
        """检测API文档格式"""
        content = content.strip()
        
        if '"openapi"' in content or content.startswith('openapi:'):
            return APIDocFormat.OPENAPI
        elif '"info"' in content and '"paths"' in content:
            return APIDocFormat.OPENAPI
        elif '"postman"' in content or '{"info":' in content:
            return APIDocFormat.POSTMAN
        elif '#%RAML' in content:
            return APIDocFormat.RAML
        elif 'schema' in content and 'query' in content.lower():
            return APIDocFormat.GRAPHQL
            
        return APIDocFormat.UNKNOWN
    
    def parse_openapi(self, content: str) -> List[APIEndpoint]:
        """解析OpenAPI/Swagger文档"""
        try:
            data = json.loads(content)
            endpoints = []
            
            for path, methods in data.get('paths', {}).items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        endpoint = APIEndpoint(
                            path=path,
                            method=method.upper(),
                            summary=details.get('summary', ''),
                            description=details.get('description', ''),
                            parameters=details.get('parameters', []),
                            request_body=details.get('requestBody', {}),
                            responses=details.get('responses', {}),
                            tags=details.get('tags', [])
                        )
                        endpoints.append(endpoint)
                        
            return endpoints
        except json.JSONDecodeError:
            return []
    
    def generate_client_code(self) -> str:
        """生成完整的客户端代码"""
        lines = [
            f'#!/usr/bin/env python3',
            f'"""',
            f'Generated API Client for {self.api_name}',
            f'"""',
            '',
            'from typing import Dict, List, Optional, Any',
            'from dataclasses import dataclass',
            'import requests',
            'import time',
            'from enum import Enum',
            '',
            '',
            'class RetryStrategy:',
            '    """重试策略配置"""',
            '    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.5):',
            '        self.max_retries = max_retries',
            '        self.backoff_factor = backoff_factor',
            '',
            '    def get_delay(self, attempt: int) -> float:',
            '        """计算重试延迟"""',
            '        return self.backoff_factor * (2 ** attempt)',
            '',
            '',
            f'class {self.api_name}Client:',
            f'    """{self.api_name} API 客户端"""',
            '',
            f'    def __init__(self, api_key: str, base_url: str = "{self.base_url}", timeout: int = 30):',
            '        self.api_key = api_key',
            '        self.base_url = base_url',
            '        self.timeout = timeout',
            '        self.session = requests.Session()',
            '        self.session.headers.update({',
            '            "Authorization": f"Bearer {{api_key}}",',
            '            "Content-Type": "application/json"',
            '        })',
            '        self.retry_strategy = RetryStrategy()',
            '',
            '    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:',
            '        """发送API请求（带重试机制）"""',
            '        url = f"{{self.base_url}}{{endpoint}}"',
            '        last_error = None',
            '',
            '        for attempt in range(self.retry_strategy.max_retries):',
            '            try:',
            '                response = self.session.request(',
            '                    method, url, timeout=self.timeout, **kwargs',
            '                )',
            '                response.raise_for_status()',
            '                return response.json()',
            '            except requests.exceptions.RequestException as e:',
            '                last_error = e',
            '                delay = self.retry_strategy.get_delay(attempt)',
            '                if attempt < self.retry_strategy.max_retries - 1:',
            '                    time.sleep(delay)',
            '',
            '        raise Exception(f"请求失败: {{last_error}}")',
            '',
        ]
        
        # 为每个端点生成方法
        for ep in self.endpoints:
            method_name = self._generate_method_name(ep)
            lines.append('')
            lines.append(f'    def {method_name}(self, ', end='')
            
            # 参数处理
            params = []
            required_params = []
            optional_params = []
            
            for param in ep.parameters:
                param_name = param.get('name', 'param')
                param_name = param_name.replace('-', '_')
                param_required = param.get('required', False)
                
                if param_required:
                    required_params.append(param_name)
                else:
                    optional_params.append(f'{param_name}=None')
                    
            all_params = required_params + optional_params
            lines[0] = lines[0].rstrip('=') + ', '.join(all_params) + '):'
            
            # 方法文档
            lines.append(f'        """{ep.summary}"""')
            if ep.description:
                lines.append(f'        # {ep.description}')
                
            # 构建查询参数
            query_params = {}
            for param in ep.parameters:
                if param.get('in') == 'query':
                    param_name = param.get('name', 'param').replace('-', '_')
                    query_params[f'"{param_name}"'] = param_name
            
            # 生成请求
            if ep.method == 'GET':
                lines.append(f'        params = {{{", ".join([f"{k}: {v}" for k, v in query_params.items()])}}}')
                if required_params:
                    lines.append(f'        params.update({{{", ".join([f\'"{p}": {p}\' for p in required_params])}}})')
                lines.append(f'        return self._request("GET", "{ep.path}", params=params)')
            else:
                body_params = {}
                for param in ep.parameters:
                    if param.get('in') in ['body', 'formData']:
                        param_name = param.get('name', 'param').replace('-', '_')
                        body_params[f'"{param_name}"'] = param_name
                        
                if body_params:
                    lines.append(f'        data = {{{", ".join([f"{k}: {v}" for k, v in body_params.items()])}}}')
                    lines.append(f'        return self._request("{ep.method.upper()}", "{ep.path}", json=data)')
                else:
                    lines.append(f'        return self._request("{ep.method.upper()}", "{ep.path}")')
        
        lines.append('')
        lines.append('# 使用示例:')
        lines.append('# client = MyAPIClient("your-api-key")')
        lines.append('# result = client.get_users(page=1, limit=10)')
        
        return '\n'.join(lines)
    
    def _generate_method_name(self, endpoint: APIEndpoint) -> str:
        """生成方法名"""
        path_parts = endpoint.path.strip('/').split('/')
        method_name = endpoint.method.lower()
        
        for part in path_parts:
            if not part.startswith('{'):
                method_name += '_' + part.replace('-', '_')
        
        return method_name


class APIIntegrationBuilder:
    """API集成构建器 - 快速创建常用集成"""
    
    INTEGRATIONS = {
        'openai': {
            'base_url': 'https://api.openai.com/v1',
            'endpoints': [
                {'path': '/chat/completions', 'method': 'POST', 'summary': '创建聊天完成'}
            ]
        },
        'github': {
            'base_url': 'https://api.github.com',
            'endpoints': [
                {'path': '/user', 'method': 'GET', 'summary': '获取当前用户'},
                {'path': '/repos/{owner}/{repo}/contents/{path}', 'method': 'GET', 'summary': '获取文件内容'}
            ]
        },
        'weather': {
            'base_url': 'https://api.openweathermap.org/data/2.5',
            'endpoints': [
                {'path': '/weather', 'method': 'GET', 'summary': '获取天气'}
            ]
        }
    }
    
    @classmethod
    def create_integration(cls, name: str, api_key: str = None) -> APIClientGenerator:
        """创建预配置的集成"""
        if name not in cls.INTEGRATIONS:
            raise ValueError(f"未知集成: {name}")
            
        config = cls.INTEGRATIONS[name]
        client = APIClientGenerator(name.title(), config['base_url'])
        
        for ep_config in config['endpoints']:
            endpoint = APIEndpoint(**ep_config)
            client.add_endpoint(endpoint)
            
        return client


def main():
    """演示使用"""
    print("🤖 API客户端生成器演示")
    print("=" * 50)
    
    # 创建GitHub集成
    client = APIIntegrationBuilder.create_integration('github')
    
    # 添加自定义端点
    client.add_endpoint(APIEndpoint(
        path='/repos/{owner}/{repo}/issues',
        method='GET',
        summary='列出仓库问题',
        description='获取指定仓库的问题列表'
    ))
    
    # 生成代码
    code = client.generate_client_code()
    print(code)
    
    # 保存到文件
    filename = f"{client.api_name.lower()}_client.py"
    with open(filename, 'w') as f:
        f.write(code)
    print(f"\n✅ 已生成: {filename}")


if __name__ == '__main__':
    main()
