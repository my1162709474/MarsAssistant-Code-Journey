#!/usr/bin/env python3
"""
URL Shortener - 链接缩短与管理工具
Day 12: 实用工具开发 - 2026-02-02

功能：
- 链接缩短
- 链接还原
- 自定义短链接别名
- 链接有效期管理
"""

import hashlib
import time
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os

class URLShortener:
    """URL短链接生成器"""
    
    def __init__(self, storage_file: str = "shortened_urls.json"):
        self.storage_file = storage_file
        self.urls: Dict[str, Dict] = {}
        self.load()
    
    def load(self) -> None:
        """从文件加载链接数据"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.urls = json.load(f)
            except:
                self.urls = {}
    
    def save(self) -> None:
        """保存链接数据到文件"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.urls, f, ensure_ascii=False, indent=2)
    
    def _generate_code(self, url: str) -> str:
        """生成短链接码"""
        hash_value = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()[:6]
        return hash_value
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        pattern = r'^https?://[\w\-\.]+(\.[\w\-\.]+)+(/[^\s]*)?$'
        return re.match(pattern, url) is not None
    
    def shorten(self, url: str, custom_code: Optional[str] = None, 
                expiry_days: int = 30) -> Dict:
        """
        缩短URL
        
        Args:
            url: 原始URL
            custom_code: 自定义短码
            expiry_days: 有效期天数
        
        Returns:
            包含短链接信息的字典
        """
        if not self._is_valid_url(url):
            return {"success": False, "error": "无效的URL格式"}
        
        if custom_code:
            if custom_code in self.urls:
                return {"success": False, "error": "短码已被占用"}
            code = custom_code
        else:
            code = self._generate_code(url)
            # 避免冲突
            while code in self.urls:
                code = self._generate_code(url)
        
        expiry_date = datetime.now() + timedelta(days=expiry_days)
        
        self.urls[code] = {
            "original_url": url,
            "created_at": datetime.now().isoformat(),
            "expires_at": expiry_date.isoformat(),
            "clicks": 0
        }
        self.save()
        
        return {
            "success": True,
            "short_code": code,
            "short_url": f"http://short.url/{code}",
            "original_url": url,
            "expires_at": expiry_date.isoformat()
        }
    
    def expand(self, code: str) -> Dict:
        """还原短链接"""
        if code not in self.urls:
            return {"success": False, "error": "短链接不存在或已过期"}
        
        url_data = self.urls[code]
        
        # 检查是否过期
        if datetime.fromisoformat(url_data["expires_at"]) < datetime.now():
            del self.urls[code]
            self.save()
            return {"success": False, "error": "链接已过期"}
        
        url_data["clicks"] += 1
        self.save()
        
        return {
            "success": True,
            "original_url": url_data["original_url"],
            "created_at": url_data["created_at"],
            "expires_at": url_data["expires_at"],
            "clicks": url_data["clicks"]
        }
    
    def list_urls(self) -> List[Dict]:
        """列出所有有效链接"""
        valid_urls = []
        now = datetime.now()
        
        for code, data in self.urls.items():
            if datetime.fromisoformat(data["expires_at"]) > now:
                valid_urls.append({
                    "code": code,
                    "original_url": data["original_url"],
                    "expires_at": data["expires_at"],
                    "clicks": data["clicks"]
                })
        
        return valid_urls
    
    def delete(self, code: str) -> Dict:
        """删除短链接"""
        if code in self.urls:
            del self.urls[code]
            self.save()
            return {"success": True, "message": "链接已删除"}
        return {"success": False, "error": "链接不存在"}


def demo():
    """演示"""
    shortener = URLShortener()
    
    print("=== URL Shortener 演示 ===\n")
    
    # 缩短链接
    result1 = shortener.shorten(
        "https://github.com/my1162709474/MarsAssistant-Code-Journey",
        expiry_days=7
    )
    print(f"缩短GitHub仓库: {result1}")
    
    # 自定义短码
    result2 = shortener.shorten(
        "https://docs.python.org",
        custom_code="pydocs",
        expiry_days=30
    )
    print(f"\n自定义短码: {result2}")
    
    # 还原链接
    expand_result = shortener.expand("pydocs")
    print(f"\n还原链接: {expand_result}")
    
    # 列出所有链接
    print(f"\n所有有效链接:")
    for url in shortener.list_urls():
        print(f"  {url['code']}: {url['original_url'][:50]}...")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    demo()
