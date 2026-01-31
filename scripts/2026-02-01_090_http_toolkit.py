#!/usr/bin/env python3
"""
HTTP Request Toolkit - HTTP请求工具箱
Day 90: HTTP客户端工具集

功能：
- 简单的GET/POST请求
- 请求头管理
- 响应处理
- 错误重试机制
- 请求计时
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass


@dataclass
class HTTPResponse:
    """HTTP响应封装"""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    url: str
    elapsed_ms: float
    
    @property
    def text(self) -> str:
        return self.content.decode('utf-8', errors='replace')
    
    def json(self) -> Any:
        return json.loads(self.text)
    
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


class HTTPClient:
    """简易HTTP客户端"""
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.default_headers: Dict[str, str] = {
            'User-Agent': 'HTTPClient/1.0',
            'Accept': '*/*',
        }
    
    def set_header(self, key: str, value: str) -> None:
        self.default_headers[key] = value
    
    def _make_request(self, method: str, url: str, 
                      data: Optional[bytes] = None,
                      headers: Optional[Dict[str, str]] = None,
                      retry_count: int = 0,
                      retry_delay: float = 1.0) -> HTTPResponse:
        """执行HTTP请求"""
        
        all_headers = {**self.default_headers}
        if headers:
            all_headers.update(headers)
        
        req = urllib.request.Request(url, data=data, method=method, headers=all_headers)
        
        start_time = time.perf_counter()
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                
                headers_dict = {k: v for k, v in response.headers.items()}
                content = response.read()
                
                return HTTPResponse(
                    status_code=response.status,
                    headers=headers_dict,
                    content=content,
                    url=url,
                    elapsed_ms=elapsed_ms
                )
                
        except urllib.error.HTTPError as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return HTTPResponse(
                status_code=e.code,
                headers=dict(e.headers),
                content=e.read(),
                url=url,
                elapsed_ms=elapsed_ms
            )
        
        except urllib.error.URLError as e:
            if retry_count > 0:
                time.sleep(retry_delay)
                return self._make_request(method, url, data, headers, 
                                          retry_count - 1, retry_delay * 2)
            raise
    
    def get(self, url: str, params: Optional[Dict] = None,
            headers: Optional[Dict] = None) -> HTTPResponse:
        """GET请求"""
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        return self._make_request('GET', url, headers=headers)
    
    def post(self, url: str, data: Any = None, 
             json_data: Optional[Dict] = None,
             headers: Optional[Dict] = None) -> HTTPResponse:
        """POST请求"""
        actual_headers = dict(headers) if headers else {}
        
        if json_data is not None:
            data = json.dumps(json_data).encode()
            actual_headers['Content-Type'] = 'application/json'
        
        return self._make_request('POST', url, data=data, headers=actual_headers)


def benchmark_url(client: HTTPClient, url: str, times: int = 3) -> Dict:
    """测试URL响应时间"""
    results = []
    
    for _ in range(times):
        response = client.get(url)
        results.append(response.elapsed_ms)
    
    return {
        'url': url,
        'times': times,
        'avg_ms': sum(results) / len(results),
        'min_ms': min(results),
        'max_ms': max(results)
    }


def main():
    """演示"""
    client = HTTPClient(timeout=5.0)
    client.set_header('Accept', 'application/json')
    
    print("=== HTTP Request Toolkit Demo ===\n")
    
    # 测试一个公开API
    test_url = "https://httpbin.org/get"
    result = benchmark_url(client, test_url)
    print(f"Benchmark: {result['url']}")
    print(f"  Average: {result['avg_ms']:.2f}ms")
    print(f"  Min: {result['min_ms']:.2f}ms")
    print(f"  Max: {result['max_ms']:.2f}ms")
    
    # POST请求示例
    print("\nPOST request to httpbin.org/post:")
    response = client.post(
        "https://httpbin.org/post",
        json_data={"tool": "HTTPClient", "day": 90}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Time: {response.elapsed_ms:.2f}ms")
    
    print("\n✓ Toolkit ready for use!")


if __name__ == "__main__":
    main()
