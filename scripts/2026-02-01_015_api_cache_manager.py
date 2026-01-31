#!/usr/bin/env python3
"""
API响应缓存管理器 - Day 15
智能缓存API响应，减少重复请求，提升性能
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import pickle


class APICacheManager:
    """API响应缓存管理器"""
    
    def __init__(self, cache_dir: str = "./api_cache", default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存文件存储目录
            default_ttl: 默认缓存时间（秒），默认1小时
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def _generate_key(self, url: str, params: Optional[Dict] = None) -> str:
        """生成缓存键"""
        key_string = f"{url}"
        if params:
            key_string += json.dumps(params, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def _get_meta_path(self, key: str) -> str:
        """获取元数据文件路径"""
        return os.path.join(self.cache_dir, f"{key}.meta")
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        获取缓存的响应
        
        Args:
            url: API URL
            params: 请求参数
            
        Returns:
            缓存的数据，如果过期或不存在则返回None
        """
        key = self._generate_key(url, params)
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)
        
        # 检查元数据
        if not os.path.exists(meta_path):
            return None
        
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            
            # 检查是否过期
            expires_at = datetime.fromisoformat(meta['expires_at'])
            if datetime.now() > expires_at:
                self._remove(key)
                return None
            
            # 读取缓存数据
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
                
        except (json.JSONDecodeError, EOFError, KeyError):
            return None
    
    def set(self, url: str, data: Any, params: Optional[Dict] = None, 
            ttl: Optional[int] = None) -> bool:
        """
        缓存API响应
        
        Args:
            url: API URL
            data: 要缓存的数据
            params: 请求参数
            ttl: 缓存时间（秒）
            
        Returns:
            是否成功缓存
        """
        key = self._generate_key(url, params)
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)
        
        ttl = ttl or self.default_ttl
        
        try:
            # 写入缓存数据
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            # 写入元数据
            meta = {
                'url': url,
                'params': params,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat(),
                'ttl': ttl
            }
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
            
            return True
            
        except (IOError, pickle.PicklingError):
            return False
    
    def _remove(self, key: str):
        """删除缓存"""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)
        
        for path in [cache_path, meta_path]:
            if os.path.exists(path):
                os.remove(path)
    
    def delete(self, url: str, params: Optional[Dict] = None):
        """删除指定URL的缓存"""
        key = self._generate_key(url, params)
        self._remove(key)
    
    def clear(self):
        """清空所有缓存"""
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
    
    def cleanup_expired(self) -> int:
        """
        清理过期的缓存
        
        Returns:
            清理的缓存数量
        """
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.meta'):
                key = filename[:-5]
                if self.get(f"dummy_{key}", None) is None:
                    count += 1
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.cache')]
        meta_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.meta')]
        
        total_size = 0
        for filename in cache_files:
            filepath = os.path.join(self.cache_dir, filename)
            total_size += os.path.getsize(filepath)
        
        return {
            'cache_count': len(cache_files),
            'meta_count': len(meta_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.cache_dir
        }
    
    def list_keys(self) -> List[str]:
        """列出所有缓存键"""
        keys = []
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                keys.append(filename[:-6])
        return keys


# ============ 演示示例 ============

def demo():
    """演示API缓存管理器的使用"""
    
    # 创建缓存管理器
    cache = APICacheManager(cache_dir="./demo_cache", default_ttl=60)
    
    print("=" * 50)
    print("API响应缓存管理器 - 演示")
    print("=" * 50)
    
    # 1. 缓存API响应
    print("\n1. 缓存API响应示例:")
    
    # 模拟API调用
    api_responses = [
        {
            "url": "https://api.example.com/users",
            "data": {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]},
            "params": None
        },
        {
            "url": "https://api.example.com/products",
            "data": {"products": [{"id": 101, "name": "Laptop"}, {"id": 102, "name": "Mouse"}]},
            "params": {"category": "electronics"}
        }
    ]
    
    for response in api_responses:
        cache.set(response["url"], response["data"], response["params"])
        print(f"   ✓ 缓存: {response['url']}")
    
    # 2. 获取缓存
    print("\n2. 获取缓存响应:")
    for response in api_responses:
        cached_data = cache.get(response["url"], response["params"])
        if cached_data:
            print(f"   ✓ 命中缓存: {response['url']}")
            print(f"     数据: {json.dumps(cached_data, indent=4, ensure_ascii=False)[:100]}...")
    
    # 3. 统计信息
    print("\n3. 缓存统计:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 4. 列出所有缓存键
    print("\n4. 缓存键列表:")
    keys = cache.list_keys()
    for key in keys:
        print(f"   - {key}")
    
    # 5. 清理过期缓存
    print("\n5. 清理过期缓存:")
    cleaned = cache.cleanup_expired()
    print(f"   清理了 {cleaned} 个过期缓存")
    
    # 6. 删除特定缓存
    print("\n6. 删除特定缓存:")
    cache.delete("https://api.example.com/products", {"category": "electronics"})
    print("   ✓ 已删除 products API缓存")
    
    # 7. 清空所有缓存
    print("\n8. 清空所有缓存:")
    cache.clear()
    print("   ✓ 已清空所有缓存")
    
    # 清理演示目录
    import shutil
    if os.path.exists("./demo_cache"):
        shutil.rmtree("./demo_cache")
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("=" * 50)


if __name__ == "__main__":
    demo()
