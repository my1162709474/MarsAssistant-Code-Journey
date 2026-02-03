#!/usr/bin/env python3
"""
Token Bucket Rate Limiter - 令牌桶限流器实现

一个简洁高效的限流器，支持：
- 令牌桶算法
- 滑动窗口统计
- 线程安全
- 动态配置
- 毫秒级精度

作者: MarsAssistant
日期: 2026-02-03
"""

import time
import threading
from typing import Optional, Dict, Tuple
from dataclasses import dataclass, field
from collections import deque
import random


@dataclass
class RateLimitConfig:
    """限流配置"""
    rate: float = 10.0          # 每秒添加的令牌数
    capacity: int = 100         # 桶容量
    burst_multiplier: float = 1.5  # 突发倍率
    min_tokens: float = 0.0     # 最小保留令牌
    
    @property
    def burst_capacity(self) -> int:
        return int(self.capacity * self.burst_multiplier)


class TokenBucket:
    """令牌桶实现"""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self.lock = threading.Lock()
    
    def _add_tokens(self, now: float):
        """添加令牌"""
        elapsed = now - self.last_update
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = now
    
    def consume(self, tokens: int = 1, block: bool = False) -> bool:
        """
        消费令牌
        
        Args:
            tokens: 需要消费的令牌数
            block: 是否阻塞等待
            
        Returns:
            是否消费成功
        """
        with self.lock:
            now = time.monotonic()
            self._add_tokens(now)
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            if block:
                # 阻塞等待
                needed = tokens - self.tokens
                wait_time = needed / self.rate
                time.sleep(wait_time)
                self._add_tokens(time.monotonic())
                self.tokens -= tokens
                return True
            
            return False
    
    def get_tokens(self) -> float:
        """获取当前令牌数"""
        with self.lock:
            now = time.monotonic()
            self._add_tokens(now)
            return self.tokens
    
    def reset(self):
        """重置桶"""
        with self.lock:
            self.tokens = self.capacity
            self.last_update = time.monotonic()


class SlidingWindowCounter:
    """滑动窗口计数器 - 用于精确统计"""
    
    def __init__(self, window_size: float = 1.0, precision: int = 10):
        self.window_size = window_size
        self.precision = precision
        self.timestamps: deque = deque()
        self.lock = threading.Lock()
    
    def record(self):
        """记录一次请求"""
        with self.lock:
            now = time.monotonic()
            self.timestamps.append(now)
            self._cleanup(now)
    
    def count(self) -> int:
        """统计窗口内的请求数"""
        with self.lock:
            now = time.monotonic()
            self._cleanup(now)
            return len(self.timestamps)
    
    def _cleanup(self, now: float):
        """清理过期时间戳"""
        while self.timestamps and now - self.timestamps[0] > self.window_size:
            self.timestamps.popleft()
    
    def get_usage_rate(self) -> float:
        """获取使用率 (0-1)"""
        return self.count() / self.window_size
    
    def reset(self):
        """重置"""
        with self.lock:
            self.timestamps.clear()


class AdaptiveRateLimiter:
    """自适应限流器 - 根据系统负载动态调整"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.bucket = TokenBucket(
            rate=self.config.rate,
            capacity=self.config.burst_capacity
        )
        self.sliding_window = SlidingWindowCounter(window_size=1.0)
        self.lock = threading.Lock()
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'denied_requests': 0,
            'start_time': time.monotonic()
        }
    
    def allow_request(self, priority: int = 0) -> Tuple[bool, Dict]:
        """
        允许请求
        
        Args:
            priority: 请求优先级 (0-10, 越高越优先)
            
        Returns:
            (是否允许, 响应信息)
        """
        with self.lock:
            self.stats['total_requests'] += 1
            
            # 计算优先级调整
            priority_bonus = priority * (self.config.capacity * 0.01)
            effective_capacity = self.config.capacity + priority_bonus
            
            # 检查滑动窗口
            window_usage = self.sliding_window.get_usage_rate()
            
            # 动态调整
            if window_usage > 0.8:
                # 高负载，减少突发
                adjusted_capacity = int(effective_capacity * 0.5)
            elif window_usage > 0.6:
                adjusted_capacity = int(effective_capacity * 0.7)
            else:
                adjusted_capacity = effective_capacity
            
            # 尝试消费令牌
            needed = 1 + (window_usage * 0.5)  # 高负载时需要更多令牌
            
            success = self.bucket.consume(tokens=needed)
            
            if success:
                self.stats['allowed_requests'] += 1
                self.sliding_window.record()
                return True, {
                    'allowed': True,
                    'tokens_remaining': self.bucket.get_tokens(),
                    'window_usage': window_usage,
                    'priority': priority
                }
            else:
                self.stats['denied_requests'] += 1()
                return False, {
                    'allowed': False,
                    'tokens_remaining': self.bucket.get_tokens(),
                    'window_usage': window_usage,
                    'retry_after': (needed - self.bucket.get_tokens()) / self.config.rate,
                    'priority': priority
                }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            elapsed = time.monotonic() - self.stats['start_time']
            return {
                **self.stats,
                'tokens_remaining': self.bucket.get_tokens(),
                'window_usage': self.sliding_window.get_usage_rate(),
                'requests_per_second': self.stats['total_requests'] / max(elapsed, 1),
                'success_rate': (
                    self.stats['allowed_requests'] / 
                    max(self.stats['total_requests'], 1)
                )
            }
    
    def reset(self):
        """重置限流器"""
        with self.lock:
            self.bucket.reset()
            self.sliding_window.reset()
            self.stats = {
                'total_requests': 0,
                'allowed_requests': 0,
                'denied_requests': 0,
                'start_time': time.monotonic()
            }


class RateLimiterPool:
    """限流器池 - 管理多个独立限流器"""
    
    def __init__(self, default_config: Optional[RateLimitConfig] = None):
        self.limiters: Dict[str, AdaptiveRateLimiter] = {}
        self.default_config = default_config or RateLimitConfig()
        self.lock = threading.Lock()
    
    def get_limiter(self, key: str, config: Optional[RateLimitConfig] = None) -> AdaptiveRateLimiter:
        """获取或创建限流器"""
        with self.lock:
            if key not in self.limiters:
                limiter_config = config or self.default_config
                self.limiters[key] = AdaptiveRateLimiter(limiter_config)
            return self.limiters[key]
    
    def allow(self, key: str, operation: str = 'default', 
              priority: int = 0, config: Optional[RateLimitConfig] = None) -> Tuple[bool, Dict]:
        """允许操作"""
        limiter = self.get_limiter(f"{key}:{operation}", config)
        return limiter.allow_request(priority)
    
    def get_stats(self, key: str) -> Optional[Dict]:
        """获取限流器统计"""
        with self.lock:
            for name, limiter in self.limiters.items():
                if name.startswith(key + ':'):
                    return limiter.get_stats()
            return None
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """获取所有限流器统计"""
        with self.lock:
            return {
                name: limiter.get_stats() 
                for name, limiter in self.limiters.items()
            }


def demo():
    """演示"""
    print("=" * 50)
    print("Token Bucket Rate Limiter Demo")
    print("=" * 50)
    
    # 创建限流器: 10请求/秒, 突发15
    config = RateLimitConfig(rate=10, capacity=10, burst_multiplier=1.5)
    limiter = AdaptiveRateLimiter(config)
    
    print(f"\n配置: {config.rate} 请求/秒, 容量 {config.capacity}, "
          f"突发 {config.burst_capacity}")
    
    print("\n测试1: 正常请求 (10次)")
    allowed = 0
    denied = 0
    for i in range(10):
        success, info = limiter.allow_request()
        if success:
            allowed += 1
        else:
            denied += 1
        print(f"  请求{i+1}: {'✓' if success else '✗'} - {info.get('window_usage', 0):.2%}")
    
    print(f"\n结果: 允许 {allowed}, 拒绝 {denied}")
    
    print("\n测试2: 快速突发 (20次)")
    allowed = 0
    denied = 0
    for i in range(20):
        success, _ = limiter.allow_request()
        if success:
            allowed += 1
        else:
            denied += 1
    print(f"结果: 允许 {allowed}, 拒绝 {denied}")
    
    print("\n等待2秒后重试...")
    time.sleep(2)
    
    print("\n测试3: 恢复后请求 (10次)")
    allowed = 0
    denied = 0
    for i in range(10):
        success, info = limiter.allow_request()
        if success:
            allowed += 1
        else:
            denied += 1
    print(f"结果: 允许 {allowed}, 拒绝 {denied}")
    
    print("\n最终统计:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("Demo Complete!")
    print("=" * 50)


if __name__ == "__main__":
    demo()
