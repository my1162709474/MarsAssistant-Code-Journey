#!/usr/bin/env python3
"""
智能倒计时工具 - Smart Countdown Timer
Day 27: 事件倒计时与时间计算工具

功能:
- 计算距离任意日期的时间差
- 支持公历和农历日期
- 多种显示格式（完整/简洁/emoji）
- 目标管理和提醒功能
- 循环事件支持（每年/每月/每周）
"""

import json
import os
import time
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Tuple
from enum import Enum

class DateType(Enum):
    """日期类型"""
    GREGORIAN = "gregorian"  # 公历
    LUNAR = "lunar"          # 农历

class DisplayFormat(Enum):
    """显示格式"""
    FULL = "full"            # 完整格式: 100天 5小时 30分 15秒
    COMPACT = "compact"      # 简洁格式: 100d 5h 30m 15s
    EMOJI = "emoji"          # Emoji格式: ⏰ 100天5小时
    SINGLE = "single"        # 单数字: 100
    PROGRESS = "progress"    # 进度条: [████░░░░░░] 33%

class LunarCalendar:
    """农历日期处理（简化版）"""
    
    # 农历月份名称
    LUNAR_MONTHS = [
        '正月', '二月', '三月', '四月', '五月', '六月',
        '七月', '八月', '九月', '十月', '冬月', '腊月'
    ]
    
    # 农历日期名称
    LUNAR_DAYS = [
        '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
        '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
        '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十'
    ]
    
    # 农历闰月映射
    LUNAR_LEAP_MONTHS = {0: False}  # 简化处理
    
    @staticmethod
    def get_lunar_date(gregorian_date: date) -> Tuple[int, int, int]:
        """
        将公历日期转换为农历日期
        返回: (月份, 日期, 是否闰月)
        简化实现：使用查表法
        """
        # 2024年春节是2月10日（农历正月初一）
        base_lunar = date(2024, 2, 10)
        base_gregorian = date(2024, 1, 1)
        
        days_diff = (gregorian_date - base_gregorian).days
        
        # 简化的农历计算（实际项目建议使用 lunarcalendar 库）
        lunar_month = 1
        lunar_day = 1
        is_leap = False
        
        # 这里是一个简化实现
        lunar_info = {
            1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (1, 4), 5: (1, 5),
            6: (1, 6), 7: (1, 7), 8: (1, 8), 9: (1, 9), 10: (1, 10),
        }
        
        if days_diff in lunar_info:
            lunar_month, lunar_day = lunar_info[days_diff]
        else:
            # 简化处理
            lunar_month = (days_diff // 29) % 12 + 1
            lunar_day = (days_diff % 29) + 1
        
        return (lunar_month, lunar_day, is_leap)
    
    @staticmethod
    def format_lunar(month: int, day: int, is_leap: bool = False) -> str:
        """格式化农历日期"""
        month_name = LunarCalendar.LUNAR_MONTHS[month - 1]
        day_name = LunarCalendar.LUNAR_DAYS[day - 1]
        leap_str = "闰" if is_leap else ""
        return f"{leap_str}{month_name}{day_name}"


class CountdownTimer:
    """倒计时管理器"""
    
    def __init__(self, storage_file: str = "countdown_data.json"):
        self.storage_file = storage_file
        self.events: Dict[str, dict] = {}
        self.load()
    
    def load(self):
        """加载保存的事件"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
            except:
                self.events = {}
    
    def save(self):
        """保存事件到文件"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
    
    def add_event(
        self,
        name: str,
        target_date: str,
        date_type: DateType = DateType.GREGORIAN,
        repeat: Optional[str] = None,
        description: str = ""
    ) -> str:
        """
        添加新事件
        
        Args:
            name: 事件名称
            target_date: 目标日期 (YYYY-MM-DD 或 农历格式)
            date_type: 日期类型
            repeat: 重复模式 (yearly/monthly/weekly/None)
            description: 事件描述
        
        Returns:
            事件ID
        """
        event_id = f"event_{len(self.events) + 1}_{int(time.time())}"
        
        self.events[event_id] = {
            "id": event_id,
            "name": name,
            "target_date": target_date,
            "date_type": date_type.value,
            "repeat": repeat,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        self.save()
        return event_id
    
    def remove_event(self, event_id: str) -> bool:
        """删除事件"""
        if event_id in self.events:
            del self.events[event_id]
            self.save()
            return True
        return False
    
    def get_time_diff(self, target_date: datetime) -> Dict[str, int]:
        """计算距离目标日期的时间差"""
        now = datetime.now()
        diff = target_date - now
        
        if diff.total_seconds() < 0:
            # 已经过去
            diff = -diff
            is_past = True
        else:
            is_past = False
        
        total_seconds = int(diff.total_seconds())
        
        days = total_seconds // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": total_seconds,
            "is_past": is_past
        }
    
    def parse_date(self, date_str: str, date_type: DateType) -> Optional[datetime]:
        """解析日期字符串"""
        try:
            if date_type == DateType.GREGORIAN:
                return datetime.strptime(date_str, "%Y-%m-%d")
            else:
                # 农历日期简化处理
                return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None
    
    def format_countdown(
        self,
        time_diff: Dict[str, int],
        format_type: DisplayFormat = DisplayFormat.FULL
    ) -> str:
        """格式化倒计时显示"""
        
        if format_type == DisplayFormat.FULL:
            parts = []
            if time_diff["days"] > 0:
                parts.append(f"{time_diff['days']}天")
            if time_diff["hours"] > 0:
                parts.append(f"{time_diff['hours']}小时")
            if time_diff["minutes"] > 0:
                parts.append(f"{time_diff['minutes']}分")
            if time_diff["seconds"] > 0:
                parts.append(f"{time_diff['seconds']}秒")
            return " ".join(parts) if parts else "0秒"
        
        elif format_type == DisplayFormat.COMPACT:
            parts = []
            if time_diff["days"] > 0:
                parts.append(f"{time_diff['days']}d")
            if time_diff["hours"] > 0:
                parts.append(f"{time_diff['hours']}h")
            if time_diff["minutes"] > 0:
                parts.append(f"{time_diff['minutes']}m")
            if time_diff["seconds"] > 0:
                parts.append(f"{time_diff['seconds']}s")
            return " ".join(parts) if parts else "0s"
        
        elif format_type == DisplayFormat.EMOJI:
            prefix = "⏰ " if not time_diff["is_past"] else "✅ "
            parts = []
            if time_diff["days"] > 0:
                parts.append(f"{time_diff['days']}天")
            if time_diff["hours"] > 0:
                parts.append(f"{time_diff['hours']}小时")
            return prefix + "".join(parts) if parts else prefix + "现在!"
        
        elif format_type == DisplayFormat.SINGLE:
            total_hours = (
                time_diff["days"] * 24 + 
                time_diff["hours"] + 
                time_diff["minutes"] / 60
            )
            if total_hours >= 24:
                return f"{time_diff['days']}天"
            elif total_hours >= 1:
                return f"{total_hours:.1f}小时"
            else:
                return f"{time_diff['minutes']}分"
        
        elif format_type == DisplayFormat.PROGRESS:
            # 假设总周期为100天，用于演示
            total = 100 * 24 * 3600
            elapsed = total - time_diff["total_seconds"]
            progress = max(0, min(100, elapsed / total * 100))
            bar_length = 10
            filled = int(progress / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            return f"[{bar}] {progress:.0f}%"
        
        return str(time_diff)
    
    def get_event_countdown(
        self,
        event_id: str,
        format_type: DisplayFormat = DisplayFormat.FULL
    ) -> Optional[str]:
        """获取事件的倒计时"""
        if event_id not in self.events:
            return None
        
        event = self.events[event_id]
        target_date = self.parse_date(
            event["target_date"],
            DateType(event["date_type"])
        )
        
        if not target_date:
            return "日期格式错误"
        
        # 处理重复事件
        if event["repeat"] and target_date < datetime.now():
            if event["repeat"] == "yearly":
                # 每年重复
                while target_date < datetime.now():
                    target_date = target_date.replace(year=target_date.year + 1)
            elif event["repeat"] == "monthly":
                # 每月重复
                while target_date < datetime.now():
                    if target_date.month == 12:
                        target_date = target_date.replace(year=target_date.year + 1, month=1)
                    else:
                        target_date = target_date.replace(month=target_date.month + 1)
            elif event["repeat"] == "weekly":
                # 每周重复
                while target_date < datetime.now():
                    target_date += timedelta(weeks=1)
        
        time_diff = self.get_time_diff(target_date)
        return self.format_countdown(time_diff, format_type)
    
    def list_events(self, format_type: DisplayFormat = DisplayFormat.EMOJI) -> str:
        """列出所有事件"""
        if not self.events:
            return "还没有设置任何事件"
        
        lines = ["📅 事件倒计时\n"]
        for event_id, event in self.items():
            countdown = self.get_event_countdown(event_id, format_type)
            status = "⏳" if not event.get("completed", False) else "✅"
            lines.append(f"{status} {event['name']}: {countdown}")
        
        return "\n".join(lines)
    
    def items(self):
        """按创建时间排序的事件列表"""
        sorted_events = sorted(
            self.events.items(),
            key=lambda x: x[1].get("created_at", "")
        )
        return sorted_events


def main():
    """命令行交互"""
    timer = CountdownTimer()
    
    # 添加示例事件
    print("🕐 智能倒计时工具\n")
    
    # 示例事件
    timer.add_event(
        "春节",
        "2027-02-17",
        DateType.GREGORIAN,
        "yearly",
        "中国传统节日"
    )
    
    timer.add_event(
        "生日",
        "2026-03-15",
        DateType.GREGORIAN,
        "yearly",
        "个人生日"
    )
    
    timer.add_event(
        "项目截止",
        "2026-02-28",
        DateType.GREGORIAN,
        None,
        "重要项目交付"
    )
    
    print(timer.list_events(DisplayFormat.EMOJI))
    print("\n" + "="*50)
    print("\n📊 详细倒计时:")
    print("-" * 30)
    
    for event_id, event in timer.items():
        countdown = timer.get_event_countdown(event_id, DisplayFormat.FULL)
        print(f"🎯 {event['name']}: {countdown}")


if __name__ == "__main__":
    main()
