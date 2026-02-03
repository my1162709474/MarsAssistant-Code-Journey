#!/usr/bin/env python3
"""
API Response Cache Manager - API响应缓存管理器
=================================================

一个功能强大的API响应缓存工具，支持：
- TTL (Time-To-Live) 过期机制
- LRU (Least Recently Used) 淘汰策略
- 磁盘持久化
- 统计信息追踪
- 线程安全

Author: MarsAssistant
Day: 78
"""

import hashlib
import json
import os
import pickle
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Tuple


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    
    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """检查是否过期"""
        if current_time is None:
            current_time = time.time()
        return current_time > self.expires_at
    
    def is_valid(self, current_time: Optional[float] = None) -> bool:
        """检查是否有效"""
        return not self.is_expired(current_time)


class CacheStats:
    """缓存统计信息"""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.expirations = 0
        self.evictions = 0
        self._lock = threading.RLock()
    
    def record_hit(self):
        with self._lock:
            self.hits += 1
    
    def record_miss(self):
        with self._lock:
            self.misses += 1
    
    def record_set(self):
        with self._lock:
            self.sets += 1
    
    def record_delete(self):
        with self._lock:
            self.deletes += 1
    
    def record_expiration(self):
        with self._lock:
            self.expirations += 1
    
    def record_eviction(self):
        with self._lock:
            self.evictions += 1
    
    def get_hit_rate(self) -> float:
        """获取命中率"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    def get_summary(self) -> dict:
        """获取统计摘要"""
        with self._lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "sets": self.sets,
                "deletes": self.deletes,
                "expirations": self.expirations,
                "evictions": self.evictions,
                "hit_rate": f"{self.get_hit_rate():.2%}",
                "total_requests": self.hits + self.misses
            }


class APICacheManager:
    """API响应缓存管理器"""
    
    def __init__(
        self,
        cache_dir: str = "./cache",
        max_size: int = 1000,
        default_ttl: int = 3600,
        enable_persistence: bool = True,
        persistence_interval: int = 300
    ):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            max_size: 最大缓存条目数 (LRU淘汰)
            default_ttl: 默认TTL (秒)
            enable_persistence: 是否启用磁盘持久化
            persistence_interval: 持久化间隔 (秒)
        """
        self.cache_dir = Path(cache_dir)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_persistence = enable_persistence
        self.persistence_interval = persistence_interval
        
        # 线程安全的LRU缓存
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # 统计信息
        self.stats = CacheStats()
        
        # 持久化相关
        self._last_persist = 0
        self._persist_lock = threading.Lock()
        
        # 初始化缓存目录
        if self.enable_persistence:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
        
        # 启动自动持久化线程
        if self.enable_persistence:
            self._start_persistence_thread()
    
    def _generate_key(self, url: str, params: Optional[dict] = None) -> str:
        """生成缓存键"""
        key_data = f"{url}:{json.dumps(params, sort_keys=True, default=str)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get(self, key: str) -> Optional[Any]:
        """获取缓存值（内部方法）"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # 检查过期
        if entry.is_expired():
            del self._cache[key]
            self.stats.record_expiration()
            return None
        
        # 更新访问信息并移动到末尾 (LRU)
        entry.last_accessed = time.time()
        entry.access_count += 1
        self._cache.move_to_end(key)
        
        return entry.value
    
    def get(self, url: str, params: Optional[dict] = None) -> Optional[Any]:
        """
        获取缓存的响应
        
        Args:
            url: API URL
            params: 请求参数
            
        Returns:
            缓存的响应，如果不存在或已过期则返回None
        """
        key = self._generate_key(url, params)
        
        with self._lock:
            value = self._get(key)
            
            if value is not None:
                self.stats.record_hit()
            else:
                self.stats.record_miss()
            
            return value
    
    def set(
        self,
        url: str,
        value: Any,
        params: Optional[dict] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        缓存响应
        
        Args:
            url: API URL
            value: 要缓存的值
            params: 请求参数
            ttl: 过期时间 (秒)，覆盖默认TTL
        """
        key = self._generate_key(url, params)
        ttl = ttl or self.default_ttl
        
        current_time = time.time()
        expires_at = current_time + ttl
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=current_time,
            expires_at=expires_at
        )
        
        with self._lock:
            # 如果key已存在，更新值
            if key in self._cache:
                del self._cache[key]
            
            # 添加新条目
            self._cache[key] = entry
            self._cache.move_to_end(key)
            
            # LRU淘汰
            while len(self._cache) > self.max_size:
                oldest_key, oldest_entry = self._cache.popitem(last=False)
                self.stats.record_eviction()
            
            self.stats.record_set()
            
            # 检查是否需要持久化
            if self.enable_persistence:
                current_time = time.time()
                if current_time - self._last_persist > self.persistence_interval:
                    self._persist_to_disk()
    
    def delete(self, url: str, params: Optional[dict] = None) -> bool:
        """
        删除缓存条目
        
        Args:
            url: API URL
            params: 请求参数
            
        Returns:
            是否成功删除
        """
        key = self._generate_key(url, params)
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.stats.record_delete()
                
                if self.enable_persistence:
                    self._persist_to_disk()
                
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            
            if self.enable_persistence:
                self._persist_to_disk()
    
    def cleanup_expired(self) -> int:
        """
        清理过期的缓存条目
        
        Returns:
            清理的条目数量
        """
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired(current_time):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self.stats.record_expiration()
            
            if expired_keys:
                if self.enable_persistence:
                    self._persist_to_disk()
        
        return len(expired_keys)
    
    def _persist_to_disk(self) -> None:
        """持久化到磁盘"""
        with self._persist_lock:
            try:
                # 保存缓存数据
                cache_data = {
                    "cache": {k: {
                        "key": v.key,
                        "value": pickle.dumps(v.value),
                        "created_at": v.created_at,
                        "expires_at": v.expires_at,
                        "access_count": v.access_count,
                        "last_accessed": v.last_accessed
                    } for k, v in self._cache.items()},
                    "stats": {
                        "hits": self.stats.hits,
                        "misses": self.stats.misses,
                        "sets": self.stats.sets,
                        "deletes": self.stats.deletes,
                        "expirations": self.stats.expirations,
                        "evictions": self.stats.evictions
                    },
                    "timestamp": time.time()
                }
                
                # 写入临时文件，然后重命名（原子操作）
                temp_file = self.cache_dir / "cache_tmp.pkl"
                with open(temp_file, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                (self.cache_dir / "cache.pkl").replace(temp_file)
                
                self._last_persist = time.time()
            except Exception as e:
                print(f"持久化失败: {e}")
    
    def _load_from_disk(self) -> None:
        """从磁盘加载"""
        cache_file = self.cache_dir / "cache.pkl"
        
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            cache_data = data.get("cache", {})
            stats_data = data.get("stats", {})
            timestamp = data.get("timestamp", 0)
            
            current_time = time.time()
            
            with self._lock:
                # 加载缓存条目
                for key, entry_data in cache_data.items():
                    # 检查是否过期
                    if current_time > entry_data["expires_at"]:
                        continue
                    
                    value = pickle.loads(entry_data["value"])
                    entry = CacheEntry(
                        key=entry_data["key"],
                        value=value,
                        created_at=entry_data["created_at"],
                        expires_at=entry_data["expires_at"],
                        access_count=entry_data.get("access_count", 0),
                        last_accessed=entry_data.get("last_accessed", time.time())
                    )
                    self._cache[key] = entry
                
                # 加载统计信息
                if stats_data:
                    self.stats.hits = stats_data.get("hits", 0)
                    self.stats.misses = stats_data.get("misses", 0)
                    self.stats.sets = stats_data.get("sets", 0)
                    self.stats.deletes = stats_data.get("deletes", 0)
                    self.stats.expirations = stats_data.get("expirations", 0)
                    self.stats.evictions = stats_data.get("evictions", 0)
                
                self._last_persist = timestamp
                
        except Exception as e:
            print(f"加载缓存失败: {e}")
    
    def _start_persistence_thread(self) -> None:
        """启动持久化线程"""
        def persist_loop():
            while True:
                time.sleep(self.persistence_interval)
                current_time = time.time()
                if current_time - self._last_persist > self.persistence_interval:
                    self._persist_to_disk()
        
        thread = threading.Thread(target=persist_loop, daemon=True)
        thread.start()
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        with self._lock:
            stats = self.stats.get_summary()
            stats.update({
                "current_size": len(self._cache),
                "max_size": self.max_size,
                "utilization": f"{len(self._cache) / self.max_size:.2%}"
            })
            return stats
    
    def get_all_entries(self) -> list:
        """获取所有缓存条目信息"""
        with self._lock:
            current_time = time.time()
            entries = []
            
            for key, entry in self._cache.items():
                remaining_ttl = max(0, entry.expires_at - current_time)
                entries.append({
                    "key": key[:16] + "...",  # 截断显示
                    "ttl_remaining": f"{remaining_ttl:.0f}s",
                    "access_count": entry.access_count,
                    "created_at": datetime.fromtimestamp(entry.created_at).isoformat(),
                    "expires_at": datetime.fromtimestamp(entry.expires_at).isoformat()
                })
            
            return entries


def demo():
    """演示"""
    print("=" * 60)
    print("API Response Cache Manager - 演示")
    print("=" * 60)
    
    # 创建缓存管理器
    cache = APICacheManager(
        cache_dir="./demo_cache",
        max_size=10,
        default_ttl=5,
        enable_persistence=True,
        persistence_interval=60
    )
    
    # 测试数据
    test_cases = [
        ("https://api.example.com/users", None),
        ("https://api.example.com/posts", {"limit": 10}),
        ("https://api.example.com/comments", {"post_id": 123}),
    ]
    
    print("\n📝 测试场景1: 基本缓存操作")
    print("-" * 40)
    
    # 添加缓存
    for url, params in test_cases:
        data = {"url": url, "params": params, "timestamp": time.time()}
        cache.set(url, data, params)
        print(f"✅ 缓存: {url}")
    
    # 获取缓存
    print("\n🔍 测试场景2: 缓存命中测试")
    print("-" * 40)
    
    for url, params in test_cases:
        result = cache.get(url, params)
        if result:
            print(f"✅ 命中: {url}")
        else:
            print(f"❌ 未命中: {url}")
    
    # 统计信息
    print("\n📊 缓存统计信息:")
    print("-" * 40)
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 测试过期
    print("\n⏰ 测试场景3: TTL过期测试")
    print("-" * 40)
    print("等待6秒让缓存过期...")
    time.sleep(6)
    
    for url, params in test_cases:
        result = cache.get(url, params)
        if result:
            print(f"✅ 仍然有效: {url}")
        else:
            print(f"❌ 已过期: {url}")
    
    # 清理过期
    print("\n🧹 清理过期条目...")
    cleaned = cache.cleanup_expired()
    print(f"  清理了 {cleaned} 个过期条目")
    
    # 再次显示统计
    print("\n📊 最终统计信息:")
    print("-" * 40)
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 清理
    cache.clear()
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    demo()
