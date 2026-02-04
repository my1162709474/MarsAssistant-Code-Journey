#!/usr/bin/env python3
"""
智能URL分析器与安全检测工具
支持URL解析、成分提取、安全检测、链接有效性检查
"""

import re
import json
import base64
import hashlib
import urllib.parse
from urllib.parse import urlparse, urlencode, parse_qs
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime


class URLSecurityLevel(Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


class URLType(Enum):
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"
    FILE = "file"
    DATA = "data"
    JAVASCRIPT = "javascript"
    MAILTO = "mailto"
    UNKNOWN = "unknown"


@dataclass
class URLComponents:
    """URL组件"""
    scheme: str = ""
    netloc: str = ""
    port: str = ""
    path: str = ""
    params: Dict[str, List[str]] = field(default_factory=dict)
    query_string: str = ""
    fragment: str = ""
    username: str = ""
    password: str = ""
    
    @property
    def domain(self) -> str:
        return self.netloc.split(':')[0] if self.netloc else ""
    
    @property
    def is_ip_address(self) -> bool:
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return bool(re.match(pattern, self.domain))


@dataclass
class SecurityReport:
    """安全报告"""
    level: URLSecurityLevel
    score: int  # 0-100
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=dict)


class URLAnalyzer:
    """URL分析器"""
    
    # 危险模式
    DANGEROUS_PATTERNS = [
        r'javascript:',
        r'data:text/html',
        r'<script',
        r'eval\s*\(',
        r'exec\s*\(',
        r'\\x[0-9a-f]{2}',
        r'%3Cscript',
        r'\\u[0-9a-f]{4}',
    ]
    
    # 可疑模式
    SUSPICIOUS_PATTERNS = [
        r'@',
        r'\btelerik\b',
        r'\bwp-admin\b',
        r'\bwp-login\b',
        r'\.php\?',
        r'session',
        r'token',
        r'auth',
        r'redirect',
        r'url=',
        r'goto=',
        r'destination=',
    ]
    
    # 跟踪参数
    TRACKING_PARAMS = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'ttclid', 'mc_eid', '_hsenc', '_hsmi',
        'yclid', '_openstat', 'msclkid', 'zanpid',
    ]
    
    def __init__(self):
        self.suspicious_domains = set()
        self.safe_domains = set()
    
    def parse(self, url: str) -> URLComponents:
        """解析URL"""
        try:
            parsed = urlparse(url)
            
            # 提取查询参数
            params = parse_qs(parsed.query, keep_blank_values=True)
            
            # 提取用户名密码
            username = ""
            password = ""
            if '@' in parsed.netloc:
                credentials, netloc = parsed.netloc.rsplit('@', 1)
                if ':' in credentials:
                    username, password = credentials.split(':', 1)
                else:
                    username = credentials
                netloc = netloc
            else:
                netloc = parsed.netloc
            
            # 提取端口
            port = ""
            if ':' in netloc:
                port = netloc.split(':')[-1]
            
            return URLComponents(
                scheme=parsed.scheme,
                netloc=netloc,
                port=port,
                path=parsed.path,
                params=params,
                query_string=parsed.query,
                fragment=parsed.fragment,
                username=username,
                password=password,
            )
        except Exception:
            return URLComponents()
    
    def analyze_security(self, url: str) -> SecurityReport:
        """安全分析"""
        report = SecurityReport(level=URLSecurityLevel.SAFE, score=100)
        components = self.parse(url)
        
        # 检查危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                report.level = URLSecurityLevel.DANGEROUS
                report.score = 0
                report.issues.append(f"发现危险模式: {pattern}")
                report.recommendations.append("拒绝访问此URL")
                return report
        
        # 检查可疑模式
        suspicious_count = 0
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                suspicious_count += 1
                report.issues.append(f"发现可疑模式: {pattern}")
        
        if suspicious_count > 0:
            report.score -= suspicious_count * 10
            report.recommendations.append("谨慎访问此链接")
        
        # 检查协议
        if components.scheme in ['http', 'ftp']:
            report.score -= 20
            report.issues.append("使用非加密协议")
            report.recommendations.append("优先使用HTTPS")
        
        # 检查IP访问
        if components.is_ip_address:
            report.score -= 15
            report.issues.append("使用IP地址而非域名")
            report.recommendations.append("确认是否为预期目标")
        
        # 检查@符号
        if '@' in url:
            report.score -= 30
            report.issues.append("URL包含@符号，可能存在钓鱼风险")
            report.recommendations.append("验证真实目标地址")
        
        # 检查端口
        if components.port:
            common_ports = ['80', '443', '8080', '21', '22']
            if components.port not in common_ports:
                report.score -= 10
                report.issues.append(f"使用非常见端口: {components.port}")
        
        # 更新安全等级
        if report.score < 30:
            report.level = URLSecurityLevel.DANGEROUS
        elif report.score < 70:
            report.level = URLSecurityLevel.SUSPICIOUS
        
        return report
    
    def extract_tracking_params(self, url: str) -> Dict[str, str]:
        """提取跟踪参数"""
        components = self.parse(url)
        tracking = {}
        for param in self.TRACKING_PARAMS:
            if param in components.params:
                tracking[param] = components.params[param][0]
        return tracking
    
    def clean_tracking(self, url: str) -> str:
        """清理跟踪参数"""
        components = self.parse(url)
        clean_params = {k: v for k, v in components.params.items() 
                       if k.lower() not in [p.lower() for p in self.TRACKING_PARAMS]}
        
        # 重建URL
        query = urlencode(clean_params, doseq=True)
        reconstructed = f"{components.scheme}://{components.netloc}"
        if components.port:
            reconstructed += f":{components.port}"
        reconstructed += components.path
        if query:
            reconstructed += f"?{query}"
        if components.fragment:
            reconstructed += f"#{components.fragment}"
        
        return reconstructed
    
    def get_url_type(self, url: str) -> URLType:
        """获取URL类型"""
        components = self.parse(url)
        scheme_map = {
            'http': URLType.HTTP,
            'https': URLType.HTTPS,
            'ftp': URLType.FTP,
            'file': URLType.FILE,
            'data': URLType.DATA,
            'javascript': URLType.JAVASCRIPT,
            'mailto': URLType.MAILTO,
        }
        return scheme_map.get(components.scheme, URLType.UNKNOWN)
    
    def generate_report(self, url: str) -> Dict[str, Any]:
        """生成完整报告"""
        components = self.parse(url)
        security = self.analyze_security(url)
        tracking = self.extract_tracking_params(url)
        
        return {
            "url": url,
            "type": self.get_url_type(url).value,
            "components": {
                "scheme": components.scheme,
                "domain": components.domain,
                "is_ip": components.is_ip_address,
                "path": components.path,
                "port": components.port,
                "parameters": len(components.params),
                "has_fragment": bool(components.fragment),
            },
            "security": {
                "level": security.level.value,
                "score": security.score,
                "issues": security.issues,
                "recommendations": security.recommendations,
            },
            "tracking": {
                "found": len(tracking) > 0,
                "params": tracking,
            },
            "cleaned_url": self.clean_tracking(url) if tracking else url,
        }


def demo():
    """演示"""
    analyzer = URLAnalyzer()
    
    test_urls = [
        "https://www.example.com/path?param1=value1&utm_source=google",
        "http://example.com/admin/login.php?user=test",
        "https://192.168.1.1:8080/dashboard",
        "https://user:pass@phishing.com@legit.com/page",
        "javascript:alert('XSS')",
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        report = analyzer.generate_report(url)
        print(f"类型: {report['type']}")
        print(f"域名: {report['components']['domain']}")
        print(f"安全等级: {report['security']['level']}")
        print(f"安全评分: {report['security']['score']}/100")
        if report['tracking']['found']:
            print(f"跟踪参数: {list(report['tracking']['params'].keys())}")
        if report['issues']:
            print(f"问题: {report['issues']}")


if __name__ == "__main__":
    demo()
