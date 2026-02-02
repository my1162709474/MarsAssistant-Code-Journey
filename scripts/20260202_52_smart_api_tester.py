#!/usr/bin/env python3
"""
智能API测试与文档生成器
自动分析API端点、生成测试用例和文档
"""

import json
import re
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import base64


class SmartAPITester:
    """智能API测试与文档生成器"""
    
    def __init__(self, base_url, headers=None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.endpoints = []
        self.test_results = []
        self.documentation = []
    
    def add_endpoint(self, method, path, description="", params=None, body=None):
        """添加API端点"""
        self.endpoints.append({
            "method": method.upper(),
            "path": path,
            "description": description,
            "params": params or {},
            "body": body
        })
    
    def test_endpoint(self, endpoint):
        """测试单个端点"""
        url = f"{self.base_url}{endpoint['path']}"
        method = endpoint['method']
        
        try:
            req = Request(url, method=method, headers=self.headers)
            if endpoint.get('body'):
                req.data = json.dumps(endpoint['body']).encode()
                req.add_header('Content-Type', 'application/json')
            
            with urlopen(req, timeout=10) as response:
                status = response.status
                body = response.read().decode('utf-8')
                try:
                    data = json.loads(body)
                except:
                    data = {"raw": body}
                
                result = {
                    "endpoint": f"{method} {endpoint['path']}",
                    "status": status,
                    "success": 200 <= status < 300,
                    "response": data,
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(result)
                return result
                
        except HTTPError as e:
            result = {
                "endpoint": f"{method} {endpoint['path']}",
                "status": e.code,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
        except Exception as e:
            result = {
                "endpoint": f"{method} {endpoint['path']}",
                "status": None,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    def test_all(self):
        """测试所有端点"""
        print(f"🧪 开始测试 {len(self.endpoints)} 个端点...\n")
        for i, endpoint in enumerate(self.endpoints, 1):
            print(f"[{i}/{len(self.endpoints)}] 测试: {endpoint['method']} {endpoint['path']}")
            self.test_endpoint(endpoint)
        return self.test_results
    
    def generate_documentation(self):
        """生成Markdown文档"""
        doc = ["# API Documentation", ""]
        doc.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append(f"**Base URL**: `{self.base_url}`")
        doc.append("")
        doc.append("## Endpoints")
        doc.append("")
        
        for ep in self.endpoints:
            doc.append(f"### {ep['method']} {ep['path']}")
            doc.append(f"**Description**: {ep['description'] or 'No description'}")
            doc.append("")
            
            if ep.get('params'):
                doc.append("**Parameters:**")
                doc.append("| Name | Type | Required | Description |")
                doc.append("|------|------|----------|-------------|")
                for name, info in ep['params'].items():
                    doc.append(f"| {name} | {info.get('type', 'string')} | {'Yes' if info.get('required') else 'No'} | {info.get('description', '-')} |")
                doc.append("")
            
            if ep.get('body'):
                doc.append("**Request Body:**")
                doc.append("```json")
                doc.append(json.dumps(ep['body'], indent=2))
                doc.append("```")
                doc.append("")
        
        doc.append("## Test Results")
        doc.append("")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            doc.append(f"- {status_icon} **{result['endpoint']}**: HTTP {result.get('status', 'N/A')}")
        
        self.documentation = "\n".join(doc)
        return self.documentation
    
    def export_postman_collection(self):
        """导出Postman集合"""
        collection = {
            "info": {
                "name": f"API Collection - {datetime.now().strftime('%Y-%m-%d')}",
                "description": "Auto-generated API collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        for ep in self.endpoints:
            item = {
                "name": ep['description'] or ep['path'],
                "request": {
                    "method": ep['method'],
                    "url": f"{self.base_url}{ep['path']}",
                    "header": [{"key": k, "value": v} for k, v in self.headers.items()]
                }
            }
            if ep.get('body'):
                item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(ep['body'], indent=2)
                }
            collection["item"].append(item)
        
        return json.dumps(collection, indent=2)
    
    def print_summary(self):
        """打印测试摘要"""
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        print(f"\n📊 测试摘要: {passed}/{total} 通过")
        print(f"   ✅ 成功: {passed}")
        print(f"   ❌ 失败: {total - passed}")


def demo():
    """演示用法"""
    print("🚀 Smart API Tester - 演示模式")
    print("=" * 50)
    
    # 示例API测试器
    tester = SmartAPITester(
        base_url="https://jsonplaceholder.typicode.com",
        headers={"Accept": "application/json"}
    )
    
    # 添加示例端点
    tester.add_endpoint("GET", "/posts", "获取文章列表", {"_limit": {"type": "int", "description": "限制返回数量"}})
    tester.add_endpoint("GET", "/posts/1", "获取单篇文章")
    tester.add_endpoint("POST", "/posts", "创建新文章", body={"title": "foo", "body": "bar", "userId": 1})
    tester.add_endpoint("GET", "/users", "获取用户列表")
    
    # 测试所有端点
    tester.test_all()
    
    # 打印摘要
    tester.print_summary()
    
    # 生成文档
    print("\n📖 生成的API文档:")
    print("-" * 50)
    doc = tester.generate_documentation()
    print(doc[:1000] + "..." if len(doc) > 1000 else doc)
    
    # 导出Postman集合
    print("\n📦 Postman集合已生成 (可导出)")


if __name__ == "__main__":
    demo()
