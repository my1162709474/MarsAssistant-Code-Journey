#!/usr/bin/env python3
"""
API Tester & Performance Analyzer
API测试与性能分析工具
=====================================
功能:
- HTTP请求测试 (GET, POST, PUT, DELETE, PATCH)
- 响应时间分析
- 成功率统计
- 并发性能测试
- 结果导出 (JSON, HTML, CSV)
"""

import requests
import time
import json
import csv
import statistics
import threading
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse


@dataclass
class RequestResult:
    """单次请求结果"""
    url: str
    method: str
    status_code: int
    response_time: float  # 毫秒
    response_size: int   # 字节
    success: bool
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TestSummary:
    """测试汇总"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0  # 毫秒
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    std_response_time: float = 0.0
    total_data_transferred: int = 0
    requests_per_second: float = 0.0
    errors: Dict[str, int] = field(default_factory=dict)


class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "", headers: Dict[str, str] = None, 
                 timeout: int = 30, verbose: bool = False):
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.headers = headers or {
            'User-Agent': 'APITester/1.0',
            'Accept': 'application/json'
        }
        self.timeout = timeout
        self.verbose = verbose
        self.results: List[RequestResult] = []
        self.lock = threading.Lock()
        
    def _make_request(self, method: str, endpoint: str, 
                     data: Any = None, params: Dict = None) -> RequestResult:
        """执行单个请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        
        if params:
            url += '?' + urllib.parse.urlencode(params)
        
        start_time = time.perf_counter()
        error_msg = None
        status_code = 0
        response_size = 0
        success = False
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data if data and method in ['POST', 'PUT', 'PATCH'] else None,
                data=data if data and method not in ['POST', 'PUT', 'PATCH'] else None,
                timeout=self.timeout
            )
            status_code = response.status_code
            response_size = len(response.content)
            success = 200 <= status_code < 300
            
            if not success:
                error_msg = f"HTTP {status_code}"
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout"
            status_code = 0
        except requests.exceptions.ConnectionError:
            error_msg = "Connection Error"
            status_code = 0
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            status_code = 0
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            status_code = 0
        
        end_time = time.perf_counter()
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        result = RequestResult(
            url=url,
            method=method,
            status_code=status_code,
            response_time=response_time,
            response_size=response_size,
            success=success,
            error=error_msg
        )
        
        if self.verbose:
            print(f"  [{method}] {url} -> {status_code} ({response_time:.2f}ms)")
        
        return result
    
    def test_endpoint(self, method: str, endpoint: str, 
                     data: Any = None, params: Dict = None) -> RequestResult:
        """测试单个端点"""
        result = self._make_request(method, endpoint, data, params)
        with self.lock:
            self.results.append(result)
        return result
    
    def load_test(self, method: str, endpoint: str, 
                 num_requests: int, concurrency: int = 10,
                 data: Any = None, params: Dict = None) -> List[RequestResult]:
        """负载测试 - 并发请求"""
        print(f"\n⚡ 负载测试: {num_requests} 次请求 (并发数: {concurrency})")
        
        def worker():
            return self._make_request(method, endpoint, data, params)
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker) for _ in range(num_requests)]
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                with self.lock:
                    self.results.append(result)
                if self.verbose:
                    print(f"  [{result.method}] {result.status_code} ({result.response_time:.2f}ms)")
        
        return results
    
    def run_test_suite(self, test_cases: List[Dict], 
                      concurrency: int = 5) -> TestSummary:
        """运行测试套件"""
        print(f"\n🧪 运行测试套件: {len(test_cases)} 个测试用例")
        
        for i, test in enumerate(test_cases, 1):
            method = test.get('method', 'GET')
            endpoint = test.get('endpoint', '')
            data = test.get('data')
            params = test.get('params')
            iterations = test.get('iterations', 1)
            
            print(f"\n  [{i}/{len(test_cases)}] {method} {endpoint}")
            
            if iterations > 1:
                self.load_test(method, endpoint, iterations, concurrency, data, params)
            else:
                self.test_endpoint(method, endpoint, data, params)
        
        return self.get_summary()
    
    def get_summary(self) -> TestSummary:
        """获取测试汇总"""
        if not self.results:
            return TestSummary()
        
        response_times = [r.response_time for r in self.results]
        successful = [r for r in self.results if r.success]
        
        summary = TestSummary(
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(self.results) - len(successful),
            success_rate=len(successful) / len(self.results) * 100 if self.results else 0,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            std_response_time=statistics.stdev(response_times) if len(response_times) > 1 else 0,
            total_data_transferred=sum(r.response_size for r in self.results),
        )
        
        # 统计错误类型
        errors = {}
        for r in self.results:
            if not r.success:
                err_key = r.error or f"HTTP {r.status_code}"
                errors[err_key] = errors.get(err_key, 0) + 1
        summary.errors = errors
        
        # 计算QPS
        if response_times:
            total_time = max(response_times) - min(response_times)
            if total_time > 0:
                summary.requests_per_second = len(self.results) / (total_time / 1000)
        
        return summary
    
    def print_summary(self, summary: TestSummary = None):
        """打印测试汇总"""
        if summary is None:
            summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 测试汇总 / Test Summary")
        print("="*60)
        print(f"  总请求数:       {summary.total_requests}")
        print(f"  成功请求:       {summary.successful_requests}")
        print(f"  失败请求:       {summary.failed_requests}")
        print(f"  成功率:         {summary.success_rate:.2f}%")
        print(f"  平均响应时间:   {summary.avg_response_time:.2f}ms")
        print(f"  最小响应时间:   {summary.min_response_time:.2f}ms")
        print(f"  最大响应时间:   {summary.max_response_time:.2f}ms")
        print(f"  响应时间标准差: {summary.std_response_time:.2f}ms")
        print(f"  传输数据量:     {summary.total_data_transferred:,} bytes")
        print(f"  QPS:            {summary.requests_per_second:.2f}")
        
        if summary.errors:
            print("\n  错误分布:")
            for error, count in summary.errors.items():
                print(f"    - {error}: {count}")
        print("="*60)
    
    def export_results(self, filepath: str, format: str = 'json'):
        """导出结果"""
        summary = self.get_summary()
        
        if format == 'json':
            export_data = {
                'summary': {
                    'total_requests': summary.total_requests,
                    'successful_requests': summary.successful_requests,
                    'failed_requests': summary.failed_requests,
                    'success_rate': summary.success_rate,
                    'avg_response_time': summary.avg_response_time,
                    'min_response_time': summary.min_response_time,
                    'max_response_time': summary.max_response_time,
                    'std_response_time': summary.std_response_time,
                    'total_data_transferred': summary.total_data_transferred,
                    'requests_per_second': summary.requests_per_second,
                    'errors': summary.errors,
                    'timestamp': datetime.now().isoformat()
                },
                'results': [
                    {
                        'url': r.url,
                        'method': r.method,
                        'status_code': r.status_code,
                        'response_time': r.response_time,
                        'response_size': r.response_size,
                        'success': r.success,
                        'error': r.error,
                        'timestamp': r.timestamp
                    }
                    for r in self.results
                ]
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        elif format == 'csv':
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Method', 'Status', 'Response Time (ms)', 
                               'Size (bytes)', 'Success', 'Error', 'Timestamp'])
                for r in self.results:
                    writer.writerow([r.url, r.method, r.status_code, 
                                   f"{r.response_time:.2f}", r.response_size,
                                   r.success, r.error or '', r.timestamp])
        
        print(f"\n✅ 结果已导出到: {filepath}")


def demo():
    """演示模式 - 不需要真实API"""
    print("\n🧪 API Tester & Performance Analyzer - 演示模式")
    print("="*60)
    
    tester = APITester(verbose=False)
    
    # 模拟测试用例
    demo_endpoints = [
        {'method': 'GET', 'endpoint': 'https://api.github.com/users/octocat', 'iterations': 5},
        {'method': 'GET', 'endpoint': 'https://httpbin.org/get', 'iterations': 3},
        {'method': 'POST', 'endpoint': 'https://httpbin.org/post', 'iterations': 3},
        {'method': 'GET', 'endpoint': 'https://httpbin.org/delay/1', 'iterations': 2},
    ]
    
    summary = tester.run_test_suite(demo_endpoints, concurrency=3)
    tester.print_summary(summary)
    
    # 导出结果
    tester.export_results('demo_results.json', 'json')
    tester.export_results('demo_results.csv', 'csv')
    
    print("\n📁 演示完成! 查看 demo_results.json 和 demo_results.csv")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='API Tester & Performance Analyzer - API测试与性能分析工具'
    )
    parser.add_argument('--url', '-u', type=str, help='Base URL for testing')
    parser.add_argument('--method', '-m', type=str, default='GET',
                       choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                       help='HTTP method')
    parser.add_argument('--endpoint', '-e', type=str, help='API endpoint')
    parser.add_argument('--data', '-d', type=str, help='Request data (JSON)')
    parser.add_argument('--iterations', '-n', type=int, default=1,
                       help='Number of iterations')
    parser.add_argument('--concurrency', '-c', type=int, default=5,
                       help='Concurrency level for load testing')
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    parser.add_argument('--format', '-f', type=str, default='json',
                       choices=['json', 'csv'], help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--demo', action='store_true',
                       help='Run in demo mode')
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
        sys.exit(0)
    
    if args.url:
        tester = APITester(base_url=args.url, verbose=args.verbose)
        
        if args.endpoint:
            data = json.loads(args.data) if args.data else None
            if args.iterations > 1:
                tester.load_test(args.method, args.endpoint, args.iterations,
                               args.concurrency, data)
            else:
                tester.test_endpoint(args.method, args.endpoint, data)
        
        summary = tester.get_summary()
        tester.print_summary(summary)
        
        if args.output:
            tester.export_results(args.output, args.format)
    else:
        parser.print_help()
        print("\n💡 使用 --demo 运行演示模式")
