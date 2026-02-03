#!/usr/bin/env python3
"""
Smart Rate Limiter - Token Bucket Algorithm Implementation
Day 69 of Code Journey

A flexible rate limiter using the token bucket algorithm.
Supports both sync and async usage with decorator patterns.

Features:
- Token bucket algorithm for smooth rate limiting
- Configurable burst capacity
- Async support with asyncio
- Decorator pattern for easy integration
- Thread-safe implementation
"""

import time
import threading
import asyncio
from functools import wraps
from typing import Callable, Optional, Any
from dataclasses import dataclass, field


@dataclass
class RateLimiterStats:
    """Statistics for rate limiter usage."""
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    total_wait_time: float = 0.0
    
    @property
    def rejection_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.rejected_requests / self.total_requests
    
    @property
    def avg_wait_time(self) -> float:
        if self.allowed_requests == 0:
            return 0.0
        return self.total_wait_time / self.allowed_requests


class TokenBucket:
    """
    Token Bucket Rate Limiter Implementation.
    
    The token bucket algorithm works by:
    1. Tokens are added to bucket at a fixed rate
    2. Bucket has a maximum capacity (burst limit)
    3. Each request consumes one token
    4. If no tokens available, request is delayed/rejected
    
    Args:
        rate: Tokens added per second
        capacity: Maximum tokens in bucket (burst capacity)
    """
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = threading.Lock()
        self.stats = RateLimiterStats()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now
    
    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token from the bucket.
        
        Args:
            blocking: If True, wait for token; if False, return immediately
            timeout: Maximum time to wait (None = wait forever)
        
        Returns:
            True if token acquired, False otherwise
        """
        start_time = time.monotonic()
        deadline = start_time + timeout if timeout else None
        
        with self._lock:
            self.stats.total_requests += 1
            self._refill()
            
            if self.tokens >= 1:
                self.tokens -= 1
                self.stats.allowed_requests += 1
                return True
            
            if not blocking:
                self.stats.rejected_requests += 1
                return False
        
        # Wait for token to become available
        while True:
            wait_time = (1 - self.tokens) / self.rate if self.tokens < 1 else 0
            
            if deadline:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    with self._lock:
                        self.stats.rejected_requests += 1
                    return False
                wait_time = min(wait_time, remaining)
            
            time.sleep(wait_time)
            
            with self._lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    self.stats.allowed_requests += 1
                    self.stats.total_wait_time += time.monotonic() - start_time
                    return True
    
    async def acquire_async(self, timeout: Optional[float] = None) -> bool:
        """Async version of acquire."""
        start_time = time.monotonic()
        deadline = start_time + timeout if timeout else None
        
        with self._lock:
            self.stats.total_requests += 1
            self._refill()
            
            if self.tokens >= 1:
                self.tokens -= 1
                self.stats.allowed_requests += 1
                return True
        
        while True:
            with self._lock:
                self._refill()
                wait_time = (1 - self.tokens) / self.rate if self.tokens < 1 else 0
            
            if deadline:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    with self._lock:
                        self.stats.rejected_requests += 1
                    return False
                wait_time = min(wait_time, remaining)
            
            await asyncio.sleep(wait_time)
            
            with self._lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    self.stats.allowed_requests += 1
                    self.stats.total_wait_time += time.monotonic() - start_time
                    return True
    
    def get_stats(self) -> dict:
        """Get current statistics."""
        return {
            "total_requests": self.stats.total_requests,
            "allowed": self.stats.allowed_requests,
            "rejected": self.stats.rejected_requests,
            "rejection_rate": f"{self.stats.rejection_rate:.2%}",
            "avg_wait_time": f"{self.stats.avg_wait_time:.4f}s",
            "current_tokens": self.tokens,
        }


def rate_limit(rate: float, capacity: int = 10, blocking: bool = True):
    """
    Decorator for rate limiting function calls.
    
    Args:
        rate: Maximum calls per second
        capacity: Burst capacity
        blocking: Wait for rate limit or raise exception
    
    Example:
        @rate_limit(rate=5, capacity=10)
        def api_call():
            ...
    """
    bucket = TokenBucket(rate, capacity)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not bucket.acquire(blocking=blocking, timeout=30):
                raise Exception(f"Rate limit exceeded for {func.__name__}")
            return func(*args, **kwargs)
        
        wrapper.rate_limiter = bucket
        return wrapper
    
    return decorator


def async_rate_limit(rate: float, capacity: int = 10):
    """Async version of rate_limit decorator."""
    bucket = TokenBucket(rate, capacity)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not await bucket.acquire_async(timeout=30):
                raise Exception(f"Rate limit exceeded for {func.__name__}")
            return await func(*args, **kwargs)
        
        wrapper.rate_limiter = bucket
        return wrapper
    
    return decorator


# ============== Demo ==============
if __name__ == "__main__":
    print("=" * 50)
    print("🚦 Smart Rate Limiter Demo")
    print("=" * 50)
    
    # Create rate limiter: 5 requests per second, burst of 3
    limiter = TokenBucket(rate=5, capacity=3)
    
    print("\n📊 Testing burst capacity (3 quick requests)...")
    for i in range(3):
        start = time.monotonic()
        limiter.acquire()
        elapsed = time.monotonic() - start
        print(f"  Request {i+1}: {elapsed*1000:.2f}ms")
    
    print("\n⏳ Testing rate limiting (next 5 requests)...")
    for i in range(5):
        start = time.monotonic()
        limiter.acquire()
        elapsed = time.monotonic() - start
        print(f"  Request {i+4}: waited {elapsed*1000:.2f}ms")
    
    print("\n📈 Statistics:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Decorator example
    print("\n" + "=" * 50)
    print("🎯 Decorator Pattern Demo")
    print("=" * 50)
    
    @rate_limit(rate=2, capacity=2)
    def simulated_api_call(n: int) -> str:
        return f"Response #{n}"
    
    print("\nCalling rate-limited function 5 times...")
    for i in range(5):
        start = time.monotonic()
        result = simulated_api_call(i+1)
        elapsed = time.monotonic() - start
        print(f"  {result} (waited {elapsed*1000:.2f}ms)")
    
    print("\n✅ Rate limiter working correctly!")
    print("\nFeatures demonstrated:")
    print("  ✓ Token bucket algorithm")
    print("  ✓ Burst capacity handling")
    print("  ✓ Smooth rate limiting")
    print("  ✓ Decorator pattern")
    print("  ✓ Statistics tracking")
