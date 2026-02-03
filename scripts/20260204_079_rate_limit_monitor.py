#!/usr/bin/env python3
"""
API Rate Limit Monitor - 实时监控API速率限制
=============================================
监控GitHub、OpenAI等API的剩余请求配额，及时预警

GitHub提交示例:
Day 79: API Rate Limit Monitor - 实时API速率限制监控工具

核心功能:
- 🔧 多平台API支持 - GitHub、OpenAI、Claude等
- 📊 实时配额监控 - 剩余请求数、刷新时间倒计时
- 🏷️ 智能预警系统 - 配额不足时自动通知
- 📦 历史数据分析 - 追踪使用趋势
- 🧠 预测性提醒 - 基于使用速率预测耗尽时间
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import os


class APIProvider(Enum):
    """支持的API提供商"""
    GITHUB = "github"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


@dataclass
class RateLimitStatus:
    """速率限制状态"""
    provider: str
    remaining: int
    limit: int
    reset_time: datetime
    used_percent: float
    minutes_until_reset: int
    
    def is_critical(self, threshold: float = 10.0) -> bool:
        """检查是否处于临界状态"""
        return self.remaining <= int(self.limit * threshold / 100)
    
    def to_dict(self) -> Dict:
        return {
            "provider": self.provider,
            "remaining": self.remaining,
            "limit": self.limit,
            "used_percent": f"{self.used_percent:.1f}%",
            "reset_time": self.reset_time.isoformat(),
            "minutes_until_reset": self.minutes_until_reset,
            "is_critical": self.is_critical()
        }


class RateLimitMonitor:
    """API速率限制监控器"""
    
    def __init__(self, notify_callback: Optional[Callable[[RateLimitStatus], None]] = None):
        self.providers: Dict[str, Dict] = {}
        self.notify_callback = notify_callback
        self.history_file = "rate_limit_history.json"
        self._load_history()
    
    def add_provider(self, name: str, provider_type: APIProvider, 
                     headers: Dict[str, str], 
                     limit_endpoint: str,
                     limit_path: str = "resources.core.limit",
                     remaining_path: str = "resources.core.remaining",
                     reset_path: str = "resources.core.reset"):
        """添加API提供商配置"""
        self.providers[name] = {
            "type": provider_type,
            "headers": headers,
            "endpoint": limit_endpoint,
            "paths": {
                "limit": limit_path,
                "remaining": remaining_path,
                "reset": reset_path
            }
        }
    
    def _get_nested_value(self, data: Dict, path: str) -> any:
        """从嵌套字典中获取值"""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def _parse_reset_time(self, reset_value: any) -> datetime:
        """解析重置时间"""
        if isinstance(reset_value, (int, float)):
            return datetime.fromtimestamp(reset_value)
        elif isinstance(reset_value, str):
            return datetime.fromisoformat(reset_value.replace("Z", "+00:00"))
        return datetime.now() + timedelta(hours=1)
    
    def check_rate_limit(self, provider_name: str) -> Optional[RateLimitStatus]:
        """检查指定提供商的速率限制"""
        if provider_name not in self.providers:
            return None
        
        config = self.providers[provider_name]
        try:
            response = requests.get(
                config["endpoint"],
                headers=config["headers"],
                timeout=10
            )
            data = response.json()
            
            limit = self._get_nested_value(data, config["paths"]["limit"]) or 5000
            remaining = self._get_nested_value(data, config["paths"]["remaining"]) or 5000
            reset_ts = self._get_nested_value(data, config["paths"]["reset"])
            reset_time = self._parse_reset_time(reset_ts)
            
            used_percent = ((limit - remaining) / limit * 100) if limit > 0 else 0
            minutes_until_reset = max(0, int((reset_time - datetime.now()).total_seconds() / 60))
            
            status = RateLimitStatus(
                provider=provider_name,
                remaining=remaining,
                limit=limit,
                reset_time=reset_time,
                used_percent=used_percent,
                minutes_until_reset=minutes_until_reset
            )
            
            # 记录历史
            self._record_history(status)
            
            # 如果是临界状态，触发通知
            if status.is_critical() and self.notify_callback:
                self.notify_callback(status)
            
            return status
            
        except Exception as e:
            print(f"Error checking rate limit for {provider_name}: {e}")
            return None
    
    def check_all(self) -> Dict[str, RateLimitStatus]:
        """检查所有提供商的速率限制"""
        results = {}
        for name in self.providers:
            status = self.check_rate_limit(name)
            if status:
                results[name] = status
        return results
    
    def _record_history(self, status: RateLimitStatus):
        """记录历史数据"""
        if not hasattr(self, '_history'):
            self._history = []
        
        self._history.append({
            "timestamp": datetime.now().isoformat(),
            "provider": status.provider,
            "remaining": status.remaining,
            "used_percent": status.used_percent
        })
        
        # 保留最近100条记录
        self._history = self._history[-100:]
    
    def _load_history(self):
        """加载历史数据"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self._history = json.load(f)
            else:
                self._history = []
        except:
            self._history = []
    
    def save_history(self):
        """保存历史数据"""
        with open(self.history_file, 'w') as f:
            json.dump(self._history, f, indent=2)
    
    def predict_exhaustion(self, provider_name: str, 
                          samples: int = 10) -> Optional[timedelta]:
        """预测配额耗尽时间"""
        if not hasattr(self, '_history') or not self._history:
            return None
        
        provider_history = [
            h for h in self._history[-samples:]
            if h["provider"] == provider_name
        ]
        
        if len(provider_history) < 2:
            return None
        
        # 计算平均使用速率
        if len(provider_history) >= 2:
            first = provider_history[0]
            last = provider_history[-1]
            
            first_time = datetime.fromisoformat(first["timestamp"])
            last_time = datetime.fromisoformat(last["timestamp"])
            
            time_diff = (last_time - first_time).total_seconds() / 60  # 分钟
            usage_diff = first["used_percent"] - last["used_percent"]
            
            if usage_diff > 0 and time_diff > 0:
                rate_per_minute = usage_diff / time_diff
                current = provider_history[-1]
                remaining_percent = 100 - current["used_percent"]
                
                minutes_until_exhaustion = remaining_percent / rate_per_minute
                return timedelta(minutes=minutes_until_exhaustion)
        
        return None


def main():
    """主函数 - 使用示例"""
    def notify(status: RateLimitStatus):
        print(f"🚨 警告: {status.provider} 配额不足! 剩余 {status.remaining} 请求")
    
    monitor = RateLimitMonitor(notify_callback=notify)
    
    # 添加GitHub API
    monitor.add_provider(
        name="GitHub",
        provider_type=APIProvider.GITHUB,
        headers={
            "Authorization": "token YOUR_GITHUB_TOKEN",
            "Accept": "application/vnd.github.v3+json"
        },
        limit_endpoint="https://api.github.com/rate_limit"
    )
    
    # 添加OpenAI API（示例配置）
    monitor.add_provider(
        name="OpenAI",
        provider_type=APIProvider.OPENAI,
        headers={"Authorization": "Bearer YOUR_OPENAI_KEY"},
        limit_endpoint="https://api.openai.com/v1/rate_limit"
    )
    
    # 检查所有提供商
    print("🔍 检查API速率限制...
")
    results = monitor.check_all()
    
    for name, status in results.items():
        emoji = "🔴" if status.is_critical() else "🟢"
        print(f"{emoji} {status.provider}:")
        print(f"   剩余/总量: {status.remaining:,}/{status.limit:,}")
        print(f"   已使用: {status.used_percent:.1f}%")
        print(f"   重置时间: {status.reset_time.strftime('%H:%M:%S')} ({status.minutes_until_reset}分钟后)")
        
        # 预测耗尽时间
        prediction = monitor.predict_exhaustion(name)
        if prediction:
            print(f"   ⏱️ 预计耗尽: {prediction}")
        print()
    
    # 保存历史
    monitor.save_history()


if __name__ == "__main__":
    main()
