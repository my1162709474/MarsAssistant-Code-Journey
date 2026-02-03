#!/usr/bin/env python3
"""
API Tester - CLI API Testing Tool
简单实用的API测试工具，支持GET/POST/PUT/DELETE等请求方法
"""

import argparse
import json
import sys
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import urllib.parse


class APITester:
    """API测试器类"""
    
    def __init__(self):
        self.history = []
    
    def build_url(self, base_url: str, endpoint: str = "", params: dict = None) -> str:
        """构建完整URL"""
        url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')
        
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        
        return url
    
    def make_request(self, method: str, url: str, headers: dict = None, 
                     data: dict = None, verbose: bool = True) -> dict:
        """发送HTTP请求"""
        start_time = time.time()
        
        # 准备请求头
        request_headers = {
            'User-Agent': 'APITester/1.0',
            'Content-Type': 'application/json'
        }
        if headers:
            request_headers.update(headers)
        
        # 准备请求数据
        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')
            request_headers['Content-Length'] = str(len(request_data))
        
        # 创建请求对象
        try:
            request = Request(url, data=request_data, headers=request_headers)
            request.get_method = lambda: method.upper()
        except Exception:
            # 对于不支持get_method的旧版本
            request = Request(url, data=request_data, headers=request_headers)
        
        # 发送请求
        try:
            with urlopen(request, timeout=30) as response:
                response_headers = dict(response.getheaders())
                response_body = response.read().decode('utf-8')
                
                # 尝试解析JSON
                try:
                    response_data = json.loads(response_body)
                except json.JSONDecodeError:
                    response_data = response_body
                
                result = {
                    'status_code': response.status,
                    'headers': response_headers,
                    'data': response_data,
                    'response_time': round((time.time() - start_time) * 1000, 2),  # ms
                    'success': 200 <= response.status < 300
                }
                
        except HTTPError as e:
            result = {
                'status_code': e.code,
                'headers': dict(e.headers) if e.headers else {},
                'data': e.read().decode('utf-8') if e.headers else str(e),
                'response_time': round((time.time() - start_time) * 1000, 2),
                'success': False,
                'error': f'HTTP Error: {e.code} {e.reason}'
            }
        except URLError as e:
            result = {
                'status_code': None,
                'headers': {},
                'data': str(e.reason),
                'response_time': round((time.time() - start_time) * 1000, 2),
                'success': False,
                'error': f'URL Error: {e.reason}'
            }
        except Exception as e:
            result = {
                'status_code': None,
                'headers': {},
                'data': str(e),
                'response_time': round((time.time() - start_time) * 1000, 2),
                'success': False,
                'error': f'Error: {str(e)}'
            }
        
        # 记录到历史
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'method': method.upper(),
            'url': url,
            'result': result
        })
        
        return result
    
    def format_output(self, result: dict, verbose: bool = True) -> str:
        """格式化输出结果"""
        lines = []
        
        if result['success']:
            lines.append(f"✅ Status: {result['status_code']} | Time: {result['response_time']}ms")
        else:
            status = result['status_code'] or 'N/A'
            lines.append(f"❌ Status: {status} | Time: {result['response_time']}ms")
            if 'error' in result:
                lines.append(f"   Error: {result['error']}")
        
        if verbose:
            lines.append("\nResponse:")
            if isinstance(result['data'], dict) or isinstance(result['data'], list):
                lines.append(json.dumps(result['data'], indent=2, ensure_ascii=False))
            else:
                lines.append(str(result['data']))
        
        return '\n'.join(lines)
    
    def test_endpoint(self, base_url: str, endpoint: str = "", method: str = "GET",
                      headers: dict = None, data: dict = None, params: dict = None,
                      verbose: bool = True) -> dict:
        """测试API端点"""
        url = self.build_url(base_url, endpoint, params)
        
        if verbose:
            print(f"\n🚀 {method.upper()} {url}")
            if data:
                print(f"📤 Data: {json.dumps(data, ensure_ascii=False)}")
        
        result = self.make_request(method, url, headers, data, verbose)
        
        if verbose:
            print(self.format_output(result))
        
        return result
    
    def health_check(self, base_url: str, endpoints: list = None) -> dict:
        """健康检查"""
        if endpoints is None:
            endpoints = ['/', '/health', '/api/health']
        
        results = {}
        
        for endpoint in endpoints:
            result = self.test_endpoint(base_url, endpoint, "GET", verbose=False)
            results[endpoint] = result['success']
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="API Tester - Simple CLI API Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s GET https://api.github.com
  %(prog)s POST https://httpbin.org/post --data '{"key": "value"}'
  %(prog)s GET https://jsonplaceholder.typicode.com/posts/1
  %(prog)s https://api.github.com/users/octocat --header "Authorization: token YOUR_TOKEN"
        """
    )
    
    parser.add_argument('method', nargs='?', default='GET', help='HTTP method (GET, POST, PUT, DELETE)')
    parser.add_argument('url', help='API URL or base URL')
    parser.add_argument('-d', '--data', help='Request data (JSON string or @filename)')
    parser.add_argument('-H', '--header', action='append', help='Custom header (格式: "Header: value")')
    parser.add_argument('-p', '--param', action='append', help='Query parameter (格式: "key=value")')
    parser.add_argument('-e', '--endpoint', default='', help='API endpoint path')
    parser.add_argument('--health', action='store_true', help='Health check mode')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (minimal output)')
    
    args = parser.parse_args()
    
    # 解析headers
    headers = {}
    if args.header:
        for h in args.header:
            if ':' in h:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()
    
    # 解析params
    params = {}
    if args.param:
        for p in args.param:
            if '=' in p:
                key, value = p.split('=', 1)
                params[key.strip()] = value.strip()
    
    # 解析data
    data = None
    if args.data:
        if args.data.startswith('@'):
            # 从文件读取
            filename = args.data[1:]
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                sys.exit(1)
        else:
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON data: {e}")
                sys.exit(1)
    
    # 创建测试器并执行
    tester = APITester()
    
    if args.health:
        results = tester.health_check(args.url)
        print(f"\n🏥 Health Check for {args.url}:")
        for endpoint, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {endpoint}")
    else:
        tester.test_endpoint(
            base_url=args.url,
            endpoint=args.endpoint,
            method=args.method.upper(),
            headers=headers,
            data=data,
            params=params,
            verbose=not args.quiet
        )


if __name__ == "__main__":
    main()
