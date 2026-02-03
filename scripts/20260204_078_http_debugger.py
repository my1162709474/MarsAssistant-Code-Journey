#!/usr/bin/env python3
"""
HTTP Request Debugger - HTTP请求调试器
发送、调试和分析HTTP请求

Usage:
    python3 http_debugger.py <method> <url> [options]
    
Options:
    -d, --data JSON      Request body (JSON)
    -H, --header HEADERS Add headers (format: "Key: Value")
    -f, --follow         Follow redirects
    -o, --output FILE    Save response to file
    -v, --verbose        Verbose output
    
Examples:
    python3 http_debugger.py GET https://api.github.com
    python3 http_debugger.py POST https://httpbin.org/post -d '{"name":"test"}'
    python3 http_debugger.py GET https://httpbin.org/redirect/3 -f -v
"""

import argparse
import json
import sys
import time
from datetime import datetime
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler
from urllib.error import URLError, HTTPError
import urllib.parse


class CustomRedirectHandler(HTTPRedirectHandler):
    """自定义重定向处理器"""
    def __init__(self, follow_redirects=False):
        self.follow_redirects = follow_redirects
        self.redirect_count = 0
        self.redirect_history = []
    
    def http_request(self, request):
        return request
    
    def http_error_301(self, request, fp, code, msg, headers):
        return self._handle_redirect(request, headers, code)
    
    def http_error_302(self, request, fp, code, msg, headers):
        return self._handle_redirect(request, headers, code)
    
    def http_error_303(self, request, fp, code, msg, headers):
        return self._handle_redirect(request, headers, code)
    
    def http_error_307(self, request, fp, code, msg, headers):
        return self._handle_redirect(request, headers, code)
    
    def http_error_other(self, request, fp, code, msg, headers):
        return None
    
    def _handle_redirect(self, request, headers, code):
        if not self.follow_redirects or self.redirect_count >= 10:
            return None
        
        if 'location' in headers:
            location = headers['location']
            self.redirect_count += 1
            self.redirect_history.append((code, location))
            
            # 处理相对路径
            if not urllib.parse.urlparse(location).netloc:
                base_url = urllib.parse.urljoin(request.full_url, location)
            else:
                base_url = location
            
            # 创建新的请求
            new_request = Request(base_url, data=request.data)
            new_request.headers = request.headers.copy()
            new_request.method = request.method
            
            return new_request
        return None


class Colors:
    """ANSI颜色码"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def parse_headers(header_args):
    """解析命令行传入的请求头"""
    headers = {}
    if header_args:
        for header in header_args:
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
    return headers


def format_size(size_bytes):
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def print_section(title):
    """打印分隔标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_kv(key, value, indent=0):
    """打印键值对"""
    prefix = "  " * indent
    print(f"{prefix}{Colors.CYAN}{key}:{Colors.ENDC} {value}")


def make_request(method, url, data=None, headers=None, follow_redirects=False, 
                 timeout=30, verbose=False):
    """发送HTTP请求并返回详细信息"""
    request_info = {
        'timestamp': datetime.now().isoformat(),
        'method': method,
        'url': url,
        'headers': headers or {},
        'data': data,
    }
    redirect_history = []
    
    try:
        # 构建请求
        request = Request(url, method=method)
        
        # 添加默认请求头
        default_headers = {
            'User-Agent': 'HTTP-Debugger/1.0',
            'Accept': 'application/json, text/html, */*',
            'Accept-Encoding': 'gzip, deflate',
        }
        for key, value in default_headers.items():
            request.add_header(key, value)
        
        # 添加用户自定义请求头
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)
        
        # 添加请求体
        if data:
            if isinstance(data, str):
                request.data = data.encode('utf-8')
            elif isinstance(data, dict):
                request.data = json.dumps(data).encode('utf-8')
        
        # 设置重定向处理器
        redirect_handler = CustomRedirectHandler(follow_redirects)
        opener = build_opener(redirect_handler)
        
        start_time = time.time()
        response = opener.open(request, timeout=timeout)
        end_time = time.time()
        
        # 获取重定向历史
        redirect_history = redirect_handler.redirect_history
        
        # 解析响应
        response_info = {
            'status_code': response.getcode(),
            'status_message': response.reason,
            'headers': dict(response.headers),
            'content': response.read().decode('utf-8', errors='replace'),
            'content_length': len(response.read()) if response.headers.get('Content-Length') else 0,
            'content_type': response.headers.get('Content-Type', ''),
            'encoding': response.headers.get('Content-Encoding', ''),
        }
        
        # 重新读取内容（因为read()会消耗流）
        response_info['content'] = response.read().decode('utf-8', errors='replace')
        response_info['content_length'] = len(response_info['content'].encode('utf-8'))
        
        response_info['response_time'] = round((end_time - start_time) * 1000, 2)  # ms
        response_info['final_url'] = response.geturl()
        
        request_info['response'] = response_info
        
    except HTTPError as e:
        request_info['error'] = {
            'type': 'HTTPError',
            'code': e.code,
            'message': str(e),
            'headers': dict(e.headers) if e.headers else {},
        }
        try:
            request_info['error']['content'] = e.read().decode('utf-8', errors='replace')
        except:
            request_info['error']['content'] = ''
    
    except URLError as e:
        request_info['error'] = {
            'type': 'URLError',
            'message': str(e.reason),
        }
    
    except Exception as e:
        request_info['error'] = {
            'type': 'Exception',
            'message': str(e),
        }
    
    return request_info, redirect_history


def print_request_result(info, redirect_history=None, verbose=False):
    """打印请求结果"""
    if 'error' in info:
        print_section("REQUEST FAILED")
        print_kv("Method", info['method'])
        print_kv("URL", info['url'])
        print_kv("Error Type", info['error']['type'])
        print_kv("Error Message", info['error']['message'])
        
        if 'code' in info['error']:
            print_kv("Status Code", info['error']['code'])
        
        return
    
    response = info['response']
    redirect_history = redirect_history or []
    
    print_section("REQUEST INFO")
    print_kv("Method", info['method'])
    print_kv("URL", info['url'])
    print_kv("Timestamp", info['timestamp'])
    print_kv("Response Time", f"{response['response_time']} ms")
    
    print_section("RESPONSE INFO")
    status_color = Colors.GREEN if response['status_code'] < 300 else \
                   Colors.WARNING if response['status_code'] < 400 else Colors.FAIL
    print_kv("Status", f"{status_color}{response['status_code']} {response['status_message']}{Colors.ENDC}")
    print_kv("Content Type", response['content_type'])
    print_kv("Content Size", format_size(response['content_length']))
    print_kv("Final URL", response['final_url'])
    
    # 重定向历史
    if redirect_history:
        print_section("REDIRECT HISTORY")
        for i, (code, loc) in enumerate(redirect_history, 1):
            print(f"  {i}. {code} → {loc}")
    
    print_section("RESPONSE HEADERS")
    for key, value in response['headers'].items():
        print_kv(key, value)
    
    print_section("RESPONSE BODY")
    
    # 尝试格式化JSON响应
    content = response['content']
    try:
        parsed = json.loads(content)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        print(formatted)
    except json.JSONDecodeError:
        # 如果不是JSON，尝试检测格式
        if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
            print(f"{Colors.WARNING}[HTML Content - {len(content)} bytes]{Colors.ENDC}")
            print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print(content[:1000] + "..." if len(content) > 1000 else content)
    
    # 统计信息
    print_section("SUMMARY")
    print_kv("Method", info['method'])
    print_kv("Status Code", response['status_code'])
    print_kv("Response Time", f"{response['response_time']} ms")
    print_kv("Content Size", format_size(response['content_length']))


def save_response(content, filepath):
    """保存响应到文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n{Colors.GREEN}Response saved to: {filepath}{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Failed to save response: {e}{Colors.ENDC}")


def main():
    parser = argparse.ArgumentParser(
        description='HTTP Request Debugger',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('method', choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
                        help='HTTP method')
    parser.add_argument('url', help='URL to request')
    parser.add_argument('-d', '--data', help='Request body (JSON format)')
    parser.add_argument('-H', '--header', action='append', dest='headers',
                        help='Add custom header (format: "Key: Value")')
    parser.add_argument('-f', '--follow', action='store_true',
                        help='Follow redirects')
    parser.add_argument('-o', '--output', help='Save response to file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('-t', '--timeout', type=int, default=30,
                        help='Request timeout (default: 30)')
    
    args = parser.parse_args()
    
    # 解析请求头
    headers = parse_headers(args.headers) if args.headers else None
    
    # 解析请求数据
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            data = args.data
    
    # 发送请求
    print(f"{Colors.BOLD}Sending {args.method} request to {args.url}...{Colors.ENDC}\n")
    
    info, redirect_history = make_request(args.method, args.url, data, headers, args.follow, args.timeout, args.verbose)
    print_request_result(info, redirect_history, args.verbose)
    
    # 保存响应
    if args.output and 'response' in info:
        save_response(info['response']['content'], args.output)


if __name__ == '__main__':
    main()
