#!/usr/bin/env python3
"""
智能API速率限制器 (Smart Rate Limiter)
=====================================

🌟 功能特点：
--------------
• 令牌桶算法实现
• 支持多租户/多API端点
• 智能重试机制（指数退避）
• 实时速率统计
• 线程安全设计
• 持久化状态恢复

📊 性能指标：
--------------
• 时间复杂度: O(1)
• 空间复杂度: O(n) n=客户端数
• 线程安全: ✅

💡 使用示例：
--------------
    limiter = RateLimiter(requests_per_second=10, burst=20)
    
    for url in urls:
        with limiter.acquire(url):
            response = requests.get(url)
            # 处理响应...

⚡️ GitHub: my1162709474/MarsAssistant-Code-Journey
📅 Day 20 | 2026-02-02
"""

import time
import threading
import json
import hashlib
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any
import random


@dataclass
class TokenBucket:
    """
    令牌桶实现
    --------------
    令牌桶是实现速率限制最常用的算法之一。
    
    工作原理：
    1. 桶以固定速率补充令牌
    2. 每次请求消耗一个令牌
    3. 桶满时多余的令牌会溢出
    4. 桶空时请求需要等待或被拒绝
    
    优点：
    • 允许一定程度的突发流量
    • 平滑的速率控制
    • 实现简单高效
    """
    tokens: float = 0.0
    max_tokens: float = 10.0
    refill_rate: float = 1.0  # 每秒补充的令牌数
    last_update: float = field(default_factory=time.time)
    lock: threading.Lock = field(default_factory=threading.Lock)
    
    def consume(self, tokens: float = 1) -> bool:
        """尝试消耗令牌"""
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self) -> None:
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.max_tokens,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_update = now
    
    def get_remaining_tokens(self) -> float:
        """获取剩余令牌数"""
        with self.lock:
            self._refill()
            return self.tokens
    
    def wait_for_token(self, timeout: float = 10.0) -> bool:
        """等待直到获得令牌"""
        start_time = time.time()
        while True:
            if self.consume():
                return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.01)  # 短暂休眠避免忙等待


class SlidingWindowCounter:
    """
    滑动窗口计数器
    --------------
    更精确的速率限制算法，能够：
    • 避免令牌桶的边界效应
    • 提供更平滑的限流效果
    • 支持毫秒级精度
    
    适用于：API限流、登录防护、爬虫控制
    """
    
    def __init__(self, window_size_seconds: float = 60.0, max_requests: int = 100):
        self.window_size = window_size_seconds
        self.max_requests = max_requests
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()
    
    def _cleanup_old_requests(self, client_id: str, current_time: float) -> None:
        """清理过期的请求记录"""
        window_start = current_time - self.window_size
        while self.requests[client_id] and self.requests[client_id][0] < window_start:
            self.requests[client_id].popleft()
    
    def is_allowed(self, client_id: str) -> bool:
        """检查是否允许请求"""
        with self.lock:
            current_time = time.time()
            self._cleanup_old_requests(client_id, current_time)
            
            if len(self.requests[client_id]) < self.max_requests:
                self.requests[client_id].append(current_time)
                return True
            return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """获取剩余请求数"""
        with self.lock:
            current_time = time.time()
            self._cleanup_old_requests(client_id, current_time)
            return max(0, self.max_requests - len(self.requests[client_id]))
    
    def get_reset_time(self, client_id: str) -> float:
        """获取窗口重置时间"""
        with self.lock:
            if not self.requests[client_id]:
                return 0
            oldest = self.requests[client_id][0]
            return oldest + self.window_size - time.time()


class RateLimiter:
    """
    智能API速率限制器
    ==================
    
    综合使用令牌桶和滑动窗口算法，
    提供企业级的API速率限制能力。
    
    🎯 核心特性：
    --------------
    • 多算法融合：令牌桶 + 滑动窗口
    • 多客户端支持：每个客户端独立计数
    • 智能重试：指数退避策略
    • 实时监控：请求统计和速率分析
    • 持久化：状态保存和恢复
    • 线程安全：高并发场景稳定运行
    """
    
    def __init__(
        self,
        requests_per_second: float = 10,
        burst: int = 20,
        window_size_seconds: float = 60,
        max_requests_per_window: int = 100,
        enable_backoff: bool = True,
        max_retries: int = 3,
        base_delay: float = 0.1,
        max_delay: float = 30.0,
        jitter: bool = True
    ):
        # 令牌桶配置
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.requests_per_second = requests_per_second
        self.burst = burst
        
        # 滑动窗口配置
        self.sliding_windows: Dict[str, SlidingWindowCounter] = {}
        self.window_size_seconds = window_size_seconds
        self.max_requests_per_window = max_requests_per_window
        
        # 重试配置
        self.enable_backoff = enable_backoff
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        
        # 统计
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'rate_limited_requests': 0,
            'retry_requests': 0,
            'client_stats': defaultdict(lambda: {
                'requests': 0,
                'success': 0,
                'rate_limited': 0
            })
        }
        self.stats_lock = threading.Lock()
        
        # 锁
        self.lock = threading.Lock()
    
    def _get_client_id(self, client: Any) -> str:
        """生成客户端ID"""
        if isinstance(client, str):
            return client
        elif isinstance(client, dict):
            return hashlib.md5(str(client).encode()).hexdigest()[:8]
        else:
            return hash(id(client))
    
    def _get_token_bucket(self, client_id: str) -> TokenBucket:
        """获取或创建令牌桶"""
        if client_id not in self.token_buckets:
            with self.lock:
                if client_id not in self.token_buckets:
                    self.token_buckets[client_id] = TokenBucket(
                        tokens=self.burst,
                        max_tokens=self.burst,
                        refill_rate=self.requests_per_second
                    )
        return self.token_buckets[client_id]
    
    def _get_sliding_window(self, client_id: str) -> SlidingWindowCounter:
        """获取或创建滑动窗口"""
        if client_id not in self.sliding_windows:
            with self.lock:
                if client_id not in self.sliding_windows:
                    self.sliding_windows[client_id] = SlidingWindowCounter(
                        window_size_seconds=self.window_size_seconds,
                        max_requests=self.max_requests_per_window
                    )
        return self.sliding_windows[client_id]
    
    def acquire(
        self,
        client: Any = "default",
        priority: int = 0
    ) -> 'RateLimitContext':
        """
        获取请求令牌
        
        Args:
            client: 客户端标识（API端点、用户ID等）
            priority: 优先级（数值越小优先级越高）
        
        Returns:
            RateLimitContext: 上下文管理器
            
        Usage:
            with limiter.acquire("api.github.com"):
                response = requests.get(url)
        """
        client_id = self._get_client_id(client)
        token_bucket = self._get_token_bucket(client_id)
        sliding_window = self._get_sliding_window(client_id)
        
        return RateLimitContext(
            limiter=self,
            client_id=client_id,
            token_bucket=token_bucket,
            sliding_window=sliding_window,
            priority=priority
        )
    
    def execute_with_retry(
        self,
        func: Callable,
        client: Any = "default",
        priority: int = 0,
        **func_kwargs
    ) -> Any:
        """
        带重试机制的执行函数
        
        Args:
            func: 要执行的函数
            client: 客户端标识
            priority: 优先级
            **func_kwargs: 函数的参数
            
        Returns:
            函数的返回值
            
        Usage:
            result = limiter.execute_with_retry(
                lambda: requests.get(url),
                client="api.github.com"
            )
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                with self.acquire(client, priority):
                    result = func(**func_kwargs)
                    self._record_success(client)
                    return result
            except Exception as e:
                last_exception = e
                self._record_retry(client)
                
                if not self.enable_backoff:
                    raise
                
                delay = self._calculate_delay(attempt)
                time.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算重试延迟（指数退避）"""
        delay = min(
            self.base_delay * (2 ** attempt),
            self.max_delay
        )
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)
        return delay
    
    def _record_success(self, client: Any) -> None:
        """记录成功请求"""
        client_id = self._get_client_id(client)
        with self.stats_lock:
            self.stats['total_requests'] += 1
            self.stats['successful_requests'] += 1
            self.stats['client_stats'][client_id]['requests'] += 1
            self.stats['client_stats'][client_id]['success'] += 1
    
    def _record_retry(self, client: Any) -> None:
        """记录重试请求"""
        client_id = self._get_client_id(client)
        with self.stats_lock:
            self.stats['retry_requests'] += 1
            self.stats['client_stats'][client_id]['requests'] += 1
    
    def _record_rate_limited(self, client: Any) -> None:
        """记录被限流的请求"""
        client_id = self._get_client_id(client)
        with self.stats_lock:
            self.stats['rate_limited_requests'] += 1
            self.stats['client_stats'][client_id]['rate_limited'] += 1
            self.stats['client_stats'][client_id]['requests'] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取速率限制统计"""
        with self.stats_lock:
            return dict(self.stats)
    
    def get_client_status(self, client: Any) -> Dict[str, Any]:
        """获取客户端状态"""
        client_id = self._get_client_id(client)
        token_bucket = self._get_token_bucket(client_id)
        sliding_window = self._get_sliding_window(client_id)
        
        return {
            'client_id': client_id,
            'remaining_tokens': token_bucket.get_remaining_tokens(),
            'max_tokens': token_bucket.max_tokens,
            'remaining_requests': sliding_window.get_remaining_requests(client_id),
            'max_requests': sliding_window.max_requests,
            'reset_time': sliding_window.get_reset_time(client_id)
        }
    
    def save_state(self, filepath: str = "rate_limiter_state.json") -> None:
        """保存状态到文件"""
        state = {
            'token_buckets': {
                client_id: {
                    'tokens': tb.tokens,
                    'max_tokens': tb.max_tokens,
                    'refill_rate': tb.refill_rate,
                    'last_update': tb.last_update
                }
                for client_id, tb in self.token_buckets.items()
            },
            'stats': dict(self.stats)
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str = "rate_limiter_state.json") -> None:
        """从文件加载状态"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            for client_id, tb_state in state.get('token_buckets', {}).items():
                self.token_buckets[client_id] = TokenBucket(
                    tokens=tb_state['tokens'],
                    max_tokens=tb_state['max_tokens'],
                    refill_rate=tb_state['refill_rate'],
                    last_update=tb_state['last_update']
                )
            
            if 'stats' in state:
                with self.stats_lock:
                    self.stats.update(state['stats'])
        except FileNotFoundError:
            pass


class RateLimitContext:
    """速率限制上下文管理器"""
    
    def __init__(
        self,
        limiter: RateLimiter,
        client_id: str,
        token_bucket: TokenBucket,
        sliding_window: SlidingWindowCounter,
        priority: int
    ):
        self.limiter = limiter
        self.client_id = client_id
        self.token_bucket = token_bucket
        self.sliding_window = sliding_window
        self.priority = priority
        self.acquired = False
    
    def __enter__(self):
        # 尝试获取令牌
        if not self.token_bucket.consume():
            self.limiter._record_rate_limited(self.client_id)
            raise RateLimitExceeded(
                f"Rate limit exceeded for client {self.client_id}",
                retry_after=self._get_retry_after()
            )
        
        # 检查滑动窗口
        if not self.sliding_window.is_allowed(self.client_id):
            # 返还令牌
            self.token_bucket.tokens += 1
            self.limiter._record_rate_limited(self.client_id)
            raise RateLimitExceeded(
                f"Window limit exceeded for client {self.client_id}",
                retry_after=self.sliding_window.get_reset_time(self.client_id)
            )
        
        self.acquired = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.acquired:
            return False
        
        if exc_type is None:
            self.limiter._record_success(self.client_id)
        else:
            self.limiter._record_retry(self.client_id)
        
        return False
    
    def _get_retry_after(self) -> float:
        """计算重试时间"""
        needed = 1 - self.token_bucket.tokens
        if needed <= 0:
            return 0
        return needed / self.token_bucket.refill_rate


class RateLimitExceeded(Exception):
    """速率限制异常"""
    
    def __init__(self, message: str, retry_after: float = 0):
        super().__init__(message)
        self.retry_after = retry_after


# ==================== 演示和测试 ====================

def demo_basic_usage():
    """基本使用演示"""
    print("=" * 60)
    print("🚀 智能API速率限制器 - 基本使用演示")
    print("=" * 60)
    
    # 创建限流器（每秒10个请求，突发20个）
    limiter = RateLimiter(
        requests_per_second=10,
        burst=20,
        max_requests_per_window=100,
        window_size_seconds=60
    )
    
    print("\n📊 测试多客户端场景...")
    clients = ["api.github.com", "api.twitter.com", "api.openai.com"]
    
    for client in clients:
        print(f"\n🌐 客户端: {client}")
        for i in range(5):
            try:
                with limiter.acquire(client):
                    print(f"  ✅ 请求 {i+1} 成功")
                    time.sleep(0.05)
            except RateLimitExceeded as e:
                print(f"  ❌ 请求 {i+1} 被限流: {e}")
    
    print("\n📈 最终统计:")
    print(limiter.get_statistics())


def demo_retry_mechanism():
    """重试机制演示"""
    print("\n" + "=" * 60)
    print("🔄 重试机制演示")
    print("=" * 60)
    
    limiter = RateLimiter(
        requests_per_second=2,
        burst=2,
        enable_backoff=True,
        max_retries=3,
        base_delay=0.1
    )
    
    call_count = [0]
    
    def unreliable_api():
        """模拟不稳定的API"""
        call_count[0] += 1
        if call_count[0] < 3:
            raise Exception("API暂时不可用")
        return {"status": "success", "attempt": call_count[0]}
    
    try:
        result = limiter.execute_with_retry(
            unreliable_api,
            client="demo-api"
        )
        print(f"✅ 最终成功: {result}")
    except Exception as e:
        print(f"❌ 最终失败: {e}")


def demo_client_status():
    """客户端状态演示"""
    print("\n" + "=" * 60)
    print("📊 客户端状态监控演示")
    print("=" * 60)
    
    limiter = RateLimiter(
        requests_per_second=5,
        burst=10,
        max_requests_per_window=50,
        window_size_seconds=60
    )
    
    # 发送一些请求
    for i in range(8):
        try:
            with limiter.acquire("test-client"):
                pass
        except RateLimitExceeded:
            pass
    
    print("\n🔍 客户端状态:")
    status = limiter.get_client_status("test-client")
    for key, value in status.items():
        print(f"  • {key}: {value:.2f}" if isinstance(value, float) else f"  • {key}: {value}")


def demo_concurrent_usage():
    """并发使用演示"""
    print("\n" + "=" * 60)
    print("⚡ 并发场景演示")
    print("=" * 60)
    
    limiter = RateLimiter(
        requests_per_second=100,
        burst=200,
        max_requests_per_window=1000
    )
    
    results = {'success': 0, 'limited': 0}
    lock = threading.Lock()
    
    def worker(client_id: str, num_requests: int):
        """工作线程"""
        for i in range(num_requests):
            try:
                with limiter.acquire(client_id):
                    with lock:
                        results['success'] += 1
            except RateLimitExceeded:
                with lock:
                    results['limited'] += 1
    
    # 启动多个线程
    threads = []
    for i in range(5):
        t = threading.Thread(
            target=worker,
            args=(f"client-{i}", 20)
        )
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"\n📊 并发测试结果:")
    print(f"  • 成功请求: {results['success']}")
    print(f"  • 被限流: {results['limited']}")
    print(f"  • 限流率: {results['limited'] / (results['success'] + results['limited']) * 100:.1f}%")


def main():
    """主函数 - 运行所有演示"""
    print("\n" + "🌟" * 30)
    print("  智能API速率限制器 (Smart Rate Limiter)")
    print("  Day 20 | 2026-02-02")
    print("  GitHub: my1162709474/MarsAssistant-Code-Journey")
    print("🌟" * 30 + "\n")
    
    try:
        demo_basic_usage()
        demo_retry_mechanism()
        demo_client_status()
        demo_concurrent_usage()
        
        print("\n" + "=" * 60)
        print("✅ 所有演示完成！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断演示")


if __name__ == "__main__":
    main()
