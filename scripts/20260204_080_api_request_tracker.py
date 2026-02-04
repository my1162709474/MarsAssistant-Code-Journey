#!/usr/bin/env python3
"""
API Request Tracker & Visualizer
追踪和分析API请求模式，可视化展示请求历史
Author: MarsAssistant
Date: 2026-02-04
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


class APIRequestTracker:
    """API请求追踪器"""
    
    def __init__(self, storage_file="api_requests.json"):
        self.storage_file = storage_file
        self.requests = self._load_requests()
    
    def _load_requests(self):
        """加载历史请求数据"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_requests(self):
        """保存请求数据"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.requests, f, indent=2, default=str)
    
    def track_request(self, endpoint: str, method: str = "GET", 
                      status_code: int = 200, response_time: float = 0,
                      headers: dict = None, payload: dict = None):
        """记录一次API请求"""
        request = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time,
            "headers": headers or {},
            "payload_hash": hashlib.md5(json.dumps(payload or {}).encode()).hexdigest()[:8]
        }
        self.requests.append(request)
        self._save_requests()
        return request
    
    def get_summary(self, hours: int = 24):
        """获取请求摘要"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [r for r in self.requests if datetime.fromisoformat(r['timestamp']) > cutoff]
        
        if not recent:
            return {"total": 0, "message": "No requests in the last 24 hours"}
        
        summary = {
            "total_requests": len(recent),
            "time_range": f"Last {hours} hours",
            "by_method": defaultdict(int),
            "by_status": defaultdict(int),
            "avg_response_time": 0,
            "endpoints": defaultdict(int),
            "errors": []
        }
        
        total_time = 0
        for r in recent:
            summary["by_method"][r["method"]] += 1
            summary["by_status"][str(r["status_code"])] += 1
            summary["endpoints"][r["endpoint"]] += 1
            total_time += r["response_time_ms"]
            
            if r["status_code"] >= 400:
                summary["errors"].append({
                    "endpoint": r["endpoint"],
                    "status": r["status_code"],
                    "time": r["timestamp"]
                })
        
        summary["avg_response_time"] = round(total_time / len(recent), 2)
        summary["by_method"] = dict(summary["by_method"])
        summary["by_status"] = dict(summary["by_status"])
        summary["endpoints"] = dict(sorted(summary["endpoints"].items(), 
                                           key=lambda x: x[1], reverse=True)[:10])
        summary["error_count"] = len(summary["errors"])
        
        return summary
    
    def generate_report(self) -> str:
        """生成文本报告"""
        summary = self.get_summary(24)
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║               API Request Tracker - Daily Report              ║
╚══════════════════════════════════════════════════════════════╝
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Overview
   Total Requests: {summary['total_requests']}
   Time Range: {summary['time_range']}
   Avg Response Time: {summary['avg_response_time']}ms

📈 Method Distribution
"""
        
        for method, count in summary.get("by_method", {}).items():
            bar = "█" * (count // max(1, summary['total_requests'] // 20))
            report += f"   {method:6}: {bar} {count}\n"
        
        report += f"\n✅ Status Codes\n"
        for status, count in summary.get("by_status", {}).items():
            icon = "✅" if status.startswith("2") else "⚠️" if status.startswith("4") else "❌"
            report += f"   {icon} {status}: {count}\n"
        
        report += f"\n🔗 Top Endpoints\n"
        for i, (endpoint, count) in enumerate(summary.get("endpoints", {}).items(), 1):
            report += f"   {i:2}. {endpoint}: {count} requests\n"
        
        if summary.get("error_count", 0) > 0:
            report += f"\n🚨 Errors ({summary['error_count']})\n"
            for error in summary["errors"][:5]:
                report += f"   - {error['endpoint']} ({error['status']}) at {error['time']}\n"
        
        return report
    
    def export_json(self, filename="api_report.json"):
        """导出JSON格式报告"""
        report = self.get_summary()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        return filename


# 演示使用
if __name__ == "__main__":
    tracker = APIRequestTracker()
    
    # 模拟一些API请求
    demo_endpoints = [
        ("/api/users", "GET", 200, 45.2),
        ("/api/users", "POST", 201, 120.5),
        ("/api/users/123", "GET", 200, 32.1),
        ("/api/users", "GET", 200, 38.7),
        ("/api/posts", "GET", 200, 67.3),
        ("/api/posts/456", "GET", 404, 15.2),
        ("/api/auth/login", "POST", 200, 89.4),
        ("/api/users", "GET", 200, 41.8),
        ("/api/posts", "POST", 201, 145.6),
        ("/api/users/789", "PUT", 200, 55.3),
    ]
    
    print("📝 Simulating API requests...")
    for endpoint, method, status, time_ms in demo_endpoints:
        tracker.track_request(endpoint, method, status, time_ms)
    
    print("\n" + tracker.generate_report())
    
    print("\n💾 Exporting JSON report...")
    tracker.export_json()
    print("✅ Done! Check api_report.json")
