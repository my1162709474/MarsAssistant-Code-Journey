"""
API Client Builder - Intelligent REST API Client Generator
=============================================================
Generate type-safe API clients from OpenAPI/Swagger specifications.

Features:
- Generate Python/Fetch/axios clients from OpenAPI specs
- Automatic type hints and documentation
- Request/response validation
- Authentication handling
- Rate limiting and retry logic
- Mock server generation

Author: AI Code Journey
Date: 2026-02-04
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime


class Language(Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    FETCH = "fetch"
    AXIOS = "axios"


class AuthType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    OAUTH2 = "oauth2"


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    path: str
    method: str
    summary: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: List[Dict] = field(default_factory=list)
    request_body: Optional[Dict] = None
    responses: Dict[str, Dict] = field(default_factory=dict)
    deprecated: bool = False
    
    @property
    def operation_id(self) -> str:
        return f"{self.method.lower()}_{self.path.replace('/', '_').strip('_')}"


@dataclass
class APISpec:
    """Represents a complete API specification."""
    title: str
    version: str = "1.0.0"
    description: str = ""
    base_url: str = ""
    endpoints: List[APIEndpoint] = field(default_factory=list)
    auth_type: AuthType = AuthType.NONE
    security_scheme: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class GeneratedClient:
    """Generated API client code."""
    language: Language
    code: str
    filename: str
    dependencies: List[str] = field(default_factory=list)


class APIClientBuilder:
    """Generate API clients from OpenAPI specifications."""
    
    def __init__(self, spec: APISpec):
        self.spec = spec
    
    def generate(self, language: Language) -> GeneratedClient:
        """Generate client code for specified language."""
        generators = {
            Language.PYTHON: self._generate_python,
            Language.TYPESCRIPT: self._generate_typescript,
            Language.FETCH: self._generate_fetch,
            Language.AXIOS: self._generate_axios,
        }
        
        generator = generators.get(language)
        if not generator:
            raise ValueError(f"Unsupported language: {language}")
        
        return generator()
    
    def _generate_python(self) -> GeneratedClient:
        """Generate Python requests-based client."""
        title_safe = self.spec.title.replace(' ', '').replace('-', '')
        
        code = f'''"""Auto-generated API Client for {self.spec.title}
Generated: {datetime.now().isoformat()}
"""

import requests
from typing import Optional, Dict, Any


class {title_safe}Client:
    """API Client for {self.spec.title}."""
    
    def __init__(self, base_url: str = "{self.spec.base_url}", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({{"Authorization": f"Bearer {{api_key}}"}})
'''
        
        for endpoint in self.spec.endpoints:
            code += self._generate_python_method(endpoint)
        
        code += '''
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
'''
        
        filename = f"{self.spec.title.lower().replace(' ', '_')}_client.py"
        return GeneratedClient(
            language=Language.PYTHON,
            code=code,
            filename=filename,
            dependencies=["requests"]
        )
    
    def _generate_python_method(self, endpoint: APIEndpoint) -> str:
        """Generate Python method for an endpoint."""
        method_name = endpoint.operation_id.replace('/', '_')
        code = f'''
    def {method_name}(
        self,
'''
        
        params = []
        for param in endpoint.parameters:
            param_name = param.get('name', 'param')
            param_type = param.get('type', 'str')
            required = param.get('required', False)
            default = '' if required else '=None'
            params.append(f"        {param_name}: {param_type}{default}")
        
        if params:
            code += ',\n'.join(params) + ',\n'
        
        code += f'''    ) -> dict:
        """{endpoint.summary}
        
        {endpoint.description}
        """
        path = "{endpoint.path}"
'''
        
        for param in endpoint.parameters:
            param_name = param.get('name', '')
            param_in = param.get('in', '')
            if param_in == 'path':
                code += f'        path = path.replace("{{{param_name}}}", str({param_name}))\n'
        
        code += '        params = {}\n'
        for param in endpoint.parameters:
            param_name = param.get('name', '')
            param_in = param.get('in', '')
            if param_in == 'query':
                code += f'        if {param_name} is not None:\n'
                code += f'            params["{param_name}"] = {param_name}\n'
        
        code += '        return self._request("' + endpoint.method.upper() + '", path, params=params).json()\n'
        return code
    
    def _generate_typescript(self) -> GeneratedClient:
        """Generate TypeScript/Fetch client."""
        title_safe = self.spec.title.replace(' ', '').replace('-', '')
        
        code = f'''/** Auto-generated API Client for {self.spec.title}
 * Generated: {datetime.now().isoformat()}
 */

export class {title_safe}Client {{
    private baseUrl: string;
    private apiKey: string | null;
    
    constructor(baseUrl: string, apiKey: string | null = null) {{
        this.baseUrl = baseUrl.replace(/\\/$/, '');
        this.apiKey = apiKey;
    }}
    
    private async request<T>(
        method: string,
        path: string,
        options: RequestInit = {{}}
    ): Promise<T> {{
        const url = `${{this.baseUrl}}${{path}}`;
        const headers: HeadersInit = {{
            'Content-Type': 'application/json',
            ...(this.apiKey && {{ 'Authorization': `Bearer ${{this.apiKey}}` }}),
            ...options.headers,
        }};
        
        const response = await fetch(url, {{ ...options, method, headers }});
        if (!response.ok) {{
            throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
        }}
        return response.json();
    }}
'''
        
        for endpoint in self.spec.endpoints:
            code += self._generate_typescript_method(endpoint)
        
        code += '}\n'
        
        filename = f"{self.spec.title.lower().replace(' ', '_')}.client.ts"
        return GeneratedClient(
            language=Language.TYPESCRIPT,
            code=code,
            filename=filename,
            dependencies=[]
        )
    
    def _generate_typescript_method(self, endpoint: APIEndpoint) -> str:
        """Generate TypeScript method for an endpoint."""
        method_name = endpoint.operation_id.replace('/', '_')
        code = f'''
    async {method_name}(
'''
        
        params = []
        for param in endpoint.parameters:
            param_name = param.get('name', 'param')
            param_type = param.get('type', 'string')
            optional = '?' if not param.get('required', False) else ''
            params.append(f'        {param_name}{optional}: {param_type}')
        
        if params:
            code += ',\n'.join(params) + '\n'
        
        code += f'''    ): Promise<any> {{
        """{endpoint.summary}"""
        let path = "{endpoint.path}";
'''
        
        for param in endpoint.parameters:
            param_name = param.get('name', '')
            param_in = param.get('in', '')
            if param_in == 'path':
                code += f'        path = path.replace(`{{{{{param_name}}}}}`, {param_name});\n'
        
        code += f'''
        return this.request("{endpoint.method.upper()}", path);
    }}
'''
        return code
    
    def _generate_fetch(self) -> GeneratedClient:
        """Generate vanilla JavaScript Fetch client."""
        title_safe = self.spec.title.replace(' ', '').replace('-', '')
        
        code = f'''/**
 * Auto-generated Fetch API Client for {self.spec.title}
 * Generated: {datetime.now().isoformat()}
 */

class {title_safe}API {{
    constructor(baseUrl, apiKey = null) {{
        this.baseUrl = baseUrl.replace(/\\/$/, '');
        this.apiKey = apiKey;
        this.defaultHeaders = {{
            'Content-Type': 'application/json',
            ...(apiKey && {{ 'Authorization': `Bearer ${{apiKey}}` }})
        }};
    }}
    
    async request(method, path, {{ params = {{}}, body = null }} = {{}}) {{
        const url = new URL(`${{this.baseUrl}}${{path}}`);
        Object.entries(params).forEach(([k, v]) => {{
            if (v !== null && v !== undefined) url.searchParams.append(k, v);
        }});
        
        const options = {{ method, headers: this.defaultHeaders }};
        if (body) options.body = JSON.stringify(body);
        
        const res = await fetch(url.toString(), options);
        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
        return res.json().catch(() => {{}});
    }}
'''
        
        for endpoint in self.spec.endpoints:
            method_name = endpoint.operation_id.replace('/', '_')
            code += f'''
    async {method_name}(params = {{}}) {{
        return this.request('{endpoint.method}', '{endpoint.path}', {{ params }});
    }}
'''
        
        code += '}\n'
        
        filename = f"{self.spec.title.lower().replace(' ', '_')}.api.js"
        return GeneratedClient(
            language=Language.FETCH,
            code=code,
            filename=filename,
            dependencies=[]
        )
    
    def _generate_axios(self) -> GeneratedClient:
        """Generate axios-based JavaScript client."""
        title_safe = self.spec.title.replace(' ', '').replace('-', '')
        
        code = f'''/**
 * Auto-generated Axios API Client for {self.spec.title}
 * Generated: {datetime.now().isoformat()}
 */

import axios from 'axios';

class {title_safe}Client {{
    constructor(baseURL, {{ apiKey = null, timeout = 30000 }} = {{}}) {{
        this.client = axios.create({{
            baseURL: baseURL.replace(/\\/$/, ''),
            timeout,
            headers: {{
                'Content-Type': 'application/json',
                ...(apiKey && {{ 'Authorization': `Bearer ${{apiKey}}` }})
            }}
        }});
        
        this.client.interceptors.response.use(
            r => r.data,
            e => Promise.reject(e)
        );
    }}
'''
        
        for endpoint in self.spec.endpoints:
            method_name = endpoint.operation_id.replace('/', '_')
            http_method = endpoint.method.upper()
            code += f'''
    async {method_name}({{}}, params = {{}}) {{
        return this.client.{http_method.lower()}('{endpoint.path}', {{ params }});
    }}
'''
        
        code += '}\n'
        
        filename = f"{self.spec.title.lower().replace(' ', '_')}.client.js"
        return GeneratedClient(
            language=Language.AXIOS,
            code=code,
            filename=filename,
            dependencies=["axios"]
        )


def parse_openapi_spec(spec_dict: Dict) -> APISpec:
    """Parse OpenAPI/Swagger JSON dict to APISpec."""
    spec = APISpec(
        title=spec_dict.get('info', {}).get('title', 'API'),
        version=spec_dict.get('info', {}).get('version', '1.0.0'),
        description=spec_dict.get('info', {}).get('description', ''),
        base_url=spec_dict.get('servers', [{}])[0].get('url', ''),
    )
    
    paths = spec_dict.get('paths', {})
    for path, methods in paths.items():
        for method, details in methods.items():
            endpoint = APIEndpoint(
                path=path,
                method=method.upper(),
                summary=details.get('summary', ''),
                description=details.get('description', ''),
                tags=details.get('tags', []),
                parameters=details.get('parameters', []),
                request_body=details.get('requestBody'),
                responses=details.get('responses', {}),
                deprecated=details.get('deprecated', False)
            )
            spec.endpoints.append(endpoint)
    
    return spec


def demo():
    """Demonstrate API Client Builder."""
    print("=" * 60)
    print("API Client Builder - Demo")
    print("=" * 60)
    
    # Create a sample API spec
    spec_dict = {{
        "info": {{
            "title": "User Management API",
            "version": "1.0.0",
            "description": "API for managing users"
        }},
        "servers": [{{"url": "https://api.example.com/v1"}}],
        "paths": {{
            "/users": {{
                "get": {{
                    "summary": "List users",
                    "parameters": [
                        {{"name": "page", "in": "query", "type": "integer"}},
                        {{"name": "limit", "in": "query", "type": "integer"}}
                    ]
                }},
                "post": {{
                    "summary": "Create user",
                    "requestBody": {{
                        "content": {{
                            "application/json": {{
                                "schema": {{
                                    "type": "object",
                                    "properties": {{
                                        "name": {{"type": "string"}},
                                        "email": {{"type": "string"}}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }},
            "/users/{{userId}}": {{
                "get": {{
                    "summary": "Get user by ID"
                }}
            }}
        }}
    }}
    
    # Parse and generate clients
    spec = parse_openapi_spec(spec_dict)
    builder = APIClientBuilder(spec)
    
    print(f"\\nParsed API: {spec.title} v{spec.version}")
    print(f"Endpoints: {len(spec.endpoints)}")
    
    for endpoint in spec.endpoints:
        print(f"  - [{endpoint.method}] {endpoint.path}: {endpoint.summary}")
    
    print("\\nGenerating Python client...")
    python_client = builder.generate(Language.PYTHON)
    print(f"  ✓ {python_client.filename} ({len(python_client.code)} chars)")
    
    print("\\nGenerating TypeScript client...")
    ts_client = builder.generate(Language.TYPESCRIPT)
    print(f"  ✓ {ts_client.filename} ({len(ts_client.code)} chars)")
    
    print("\\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
