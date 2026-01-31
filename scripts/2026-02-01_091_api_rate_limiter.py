#!/usr/bin/env python3
"""
API Rate Limiter - API请求速率限制器
用于控制API调用频率，避免被限流

功能:
- 滑动窗口限流
- 令牌桶算法
- 分布式锁支持
- 统计和监控
"""

import time
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Dict, Callable, Any
import hashlib
import json


class TokenBucket:
    """令牌桶限流器"""
    
    def __init__(self, rate: float, capacity: Optional[float] = None):
        """
        初始化令牌桶
        
        Args:
            rate: 每秒生成的令牌数
            capacity: 桶的最大容量（默认等于rate）
        """
        self.rate = rate
        self.capacity = capacity if capacity is not None else rate
        
        self.tokens = self.capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: float = 1) -> bool:
        """
        尝试消费令牌
        
        Args:
            tokens: 消耗的令牌数
            
        Returns:
            是否成功获取令牌
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now
            
            # 添加新令牌
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            
            # 尝试消费
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def remaining(self) -> float:
        """获取剩余令牌数"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            return min(self.capacity, self.tokens + elapsed * self.rate)
    
    def reset(self):
        """重置令牌桶"""
        with self.lock:
            self.tokens = self.capacity
            self.last_update = time.time()


class SlidingWindowRateLimiter:
    """滑动窗口限流器"""
    
    def __init__(self, max_requests: int, window_seconds: float):
        """
        初始化滑动窗口限流器
        
        Args:
            max_requests: 窗口期内最大请求数
            window_seconds: 窗口期（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = {}
        self.lock = threading.Lock()
    
    def _get_window(self, key: str) -> deque:
        """获取或创建请求时间窗口"""
        if key not in self.requests:
            self.requests[key] = deque()
        return self.requests[key]
    
    def _clean_old(self, window: deque, now: float):
        """清理过期请求记录"""
        while window and now - window[0] > self.window_seconds:
            window.popleft()
    
    def allow_request(self, key: str = "default") -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限流键（如API key、IP等）
            
        Returns:
            是否允许请求
        """
        with self.lock:
            now = time.time()
            window = self._get_window(key)
            self._clean_old(window, now)
            
            if len(window) < self.max_requests:
                window.append(now)
                return True
            return False
    
    def get_remaining(self, key: str = "default") -> int:
        """获取剩余请求数"""
        with self.lock:
            now = time.time()
            window = self._get_window(key)
            self._clean_old(window, now)
            return max(0, self.max_requests - len(window))
    
    def get_reset_time(self, key: str = "default") -> float:
        """获取窗口重置时间"""
        with self.lock:
            now = time.time()
            window = self._get_window(key)
            self._clean_old(window, now)
            if window:
                return window[0] + self.window_seconds - now
            return 0.0


class RateLimiterManager:
    """Rate Limiter 管理器 - 支持多个限流策略"""
    
    def __init__(self):
        self.limiters: Dict[str, TokenBucket] = {}
        self.sliding_limiters: Dict[str, SlidingWindowRateLimiter] = {}
        self.lock = threading.Lock()
    
    def add_token_bucket(
        self,
        name: str,
        rate: float,
        capacity: Optional[float] = None
    ):
        """添加令牌桶限流器"""
        with self.lock:
            self.limiters[name] = TokenBucket(rate, capacity)
    
    def add_sliding_window(
        self,
        name: str,
        max_requests: int,
        window_seconds: float
    ):
        """添加滑动窗口限流器"""
        with self.lock:
            self.sliding_limiters[name] = SlidingWindowRateLimiter(
                max_requests, window_seconds
            )
    
    def consume(self, name: str, tokens: float = 1) -> bool:
        """消费令牌"""
        limiter = self.limiters.get(name)
        if limiter:
            return limiter.consume(tokens)
        return True
    
    def allow_request(self, name: str, key: str = "default") -> bool:
        """检查请求是否允许"""
        limiter = self.sliding_limiters.get(name)
        if limiter:
            return limiter.allow_request(key)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "token_buckets": {},
            "sliding_windows": {}
        }
        
        with self.lock:
            for name, limiter in self.limiters.items():
                stats["token_buckets"][name] = {
                    "remaining": limiter.remaining(),
                    "rate": limiter.rate,
                    "capacity": limiter.capacity
                }
            
            for name, limiter in self.sliding_limiters.items():
                stats["sliding_windows"][name] = {
                    "max_requests": limiter.max_requests,
                    "window_seconds": limiter.window_seconds
                }
        
        return stats
    
    def export_config(self) -> str:
        """导出配置（JSON格式）"""
        config = {
            "token_buckets": [
                {"name": k, "rate": v.rate, "capacity": v.capacity}
                for k, v in self.limiters.items()
            ],
            "sliding_windows": [
                {
                    "name": k,
                    "max_requests": v.max_requests,
                    "window_seconds": v.window_seconds
                }
                for k, v in self.sliding_limiters.items()
            ]
        }
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def import_config(self, config_str: str):
        """从配置导入"""
        config = json.loads(config_str)
        
        for bucket in config.get("token_buckets", []):
            self.add_token_bucket(
                bucket["name"],
                bucket["rate"],
                bucket.get("capacity")
            )
        
        for window in config.get("sliding_windows", []):
            self.add_sliding_window(
                window["name"],
                window["max_requests"],
                window["window_seconds"]
            )


# ============ 装饰器支持 ============

def rate_limit(
    manager: RateLimiterManager,
    bucket_name: str = None,
    window_name: str = None,
    fallback: Callable = None
):
    """
    限流装饰器
    
    Args:
        manager: RateLimiterManager 实例
        bucket_name: 令牌桶名称
        window_name: 滑动窗口名称
        fallback: 超出限制时的回调
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            allowed = False
            
            if bucket_name:
                allowed = manager.consume(bucket_name)
            elif window_name:
                key = hashlib.mdd(str(args).encode()).hexdigest()
                allowed = manager.allow_request(window_name, key)
            
            if allowed:
                return func(*args, **kwargs)
            elif fallback:
                return fallback(*args, **kwargs)
            else:
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {bucket_name or window_name}"
                )
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """超出限流异常"""
    pass


# ============ 使用示例 ============

def demo():
    """演示用法"""
    manager = RateLimiterManager()
    
    # 添加限流规则
    manager.add_token_bucket("api_calls", rate=10, capacity=10)
    manager.add_sliding_window("login_attempts", max_requests=5, window_seconds=60)
    
    print("=== Token Bucket Demo ===")
    for i in range(15):
        allowed = manager.consume("api_calls")
        remaining = manager.limiters["api_calls"].remaining()
        print(f"Request {i+1}: {'✓ Passed' if allowed else '✗ Limited'}, Remaining: {remaining:.1f}")
        time.sleep(0.1)
    
    print("\n=== Sliding Window Demo ===")
    for i in range(8):
        allowed = manager.allow_request("login_attempts", "user_123")
        remaining = manager.get_remaining("login_attempts")
        reset_time = manager.get_reset_time("login_attempts")
        print(f"Login {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}, Remaining: {remaining}, Reset: {reset_time:.1f}s")
    
    print("\n=== Statistics ===")
    print(json.dumps(manager.get_stats(), indent=2, ensure_ascii=False))
    
    print("\n=== Config Export ===")
    print(manager.export_config())


if __name__ == "__main__":
    demo()
