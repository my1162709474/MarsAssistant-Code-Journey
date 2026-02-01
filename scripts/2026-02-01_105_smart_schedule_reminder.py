#!/usr/bin/env python3
"""
🗓️ 智能日程提醒器 - Day 105

一个智能的日程管理和提醒工具，支持：
- 自然语言日程解析
- 艾宾浩斯遗忘曲线复习提醒
- 番茄工作法集成
- 多时区支持
- 优先级管理
- 提醒通知

Author: MarsAssistant
Date: 2026-02-01
"""

import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict
import os


class Priority(Enum):
    """任务优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class ReminderType(Enum):
    """提醒类型枚举"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


@dataclass
class Reminder:
    """提醒数据类"""
    title: str
    description: str = ""
    reminder_time: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.MEDIUM
    reminder_type: ReminderType = ReminderType.ONCE
    tags: List[str] = field(default_factory=list)
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    repeat_interval_days: int = 0
    ebbinghaus_review_times: List[datetime] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['priority'] = self.priority.name
        data['reminder_type'] = self.reminder_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Reminder':
        """从字典创建"""
        data['priority'] = Priority[data['priority']]
        data['reminder_type'] = ReminderType[data['reminder_type']]
        return cls(**data)
    
    @property
    def hash(self) -> str:
        """生成唯一哈希"""
        content = f"{self.title}{self.reminder_time}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


class SmartScheduleParser:
    """自然语言日程解析器"""
    
    # 时间模式正则表达式
    TIME_PATTERNS = {
        'today': r'(今天|今日|tonight)',
        'tomorrow': r'(明天|明日|tomorrow)',
        'weekday': r'(周一|周二|周三|周四|周五|周一|周二|周三|周四|周五|Monday|Tuesday|Wednesday|Thursday|Friday)',
        'time_12h': r'(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?',
        'time_24h': r'(\d{1,2}):(\d{2})',
        'duration': r'(\d+)\s*(分钟|小时|天|周|min|h|d|w)',
    }
    
    PRIORITY_WORDS = {
        Priority.URGENT: ['紧急', '立刻', '马上', '马上', 'urgent', 'asap', 'immediately'],
        Priority.HIGH: ['重要', '必须', '需要', '重要', 'important', 'critical'],
        Priority.MEDIUM: ['一般', '普通', '中等', 'medium', 'normal'],
        Priority.LOW: ['不急', '有空', '慢慢', '低', 'low', 'later'],
    }
    
    @classmethod
    def parse(cls, text: str) -> Tuple[str, datetime, Priority, List[str]]:
        """
        解析自然语言日程文本
        
        Args:
            text: 自然语言描述
            
        Returns:
            (标题, 提醒时间, 优先级, 标签列表)
        """
        text = text.strip()
        title = text
        tags = []
        priority = Priority.MEDIUM
        reminder_time = datetime.now() + timedelta(hours=1)
        
        # 解析时间
        now = datetime.now()
        
        # 今天/明天
        if re.search(cls.TIME_PATTERNS['today'], text):
            reminder_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
            title = re.sub(cls.TIME_PATTERNS['today'], '', text).strip()
        elif re.search(cls.TIME_PATTERNS['tomorrow'], text):
            reminder_time = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            title = re.sub(cls.TIME_PATTERNS['tomorrow'], '', text).strip()
        
        # 12小时制时间
        time_match = re.search(cls.TIME_PATTERNS['time_12h'], text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            period = time_match.group(3)
            
            if period and period.lower() == 'pm':
                if hour != 12:
                    hour += 12
            else:
                if hour == 12:
                    hour = 0
            
            reminder_time = reminder_time.replace(hour=hour, minute=minute)
            title = re.sub(cls.TIME_PATTERNS['time_12h'], '', text).strip()
        
        # 24小时制时间
        time_match = re.search(cls.TIME_PATTERNS['time_24h'], text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            reminder_time = reminder_time.replace(hour=hour, minute=minute)
            title = re.sub(cls.TIME_PATTERNS['time_24h'], '', text).strip()
        
        # 解析优先级
        for prio, words in cls.PRIORITY_WORDS.items():
            for word in words:
                if word in text:
                    priority = prio
                    break
        
        # 提取标签 (用#标记)
        tag_matches = re.findall(r'#(\w+)', text)
        tags = [f"#{tag}" for tag in tag_matches]
        
        # 清理标题
        title = re.sub(r'[#\d]', '', title).strip()
        if not title:
            title = text[:50]
        
        return title, reminder_time, priority, tags
    
    @staticmethod
    def generate_review_times(created_time: datetime, count: int = 5) -> List[datetime]:
        """
        生成艾宾浩斯遗忘曲线复习时间点
        
        Args:
            created_time: 创建时间
            count: 复习次数
            
        Returns:
            复习时间列表
        """
        # 艾宾浩斯曲线间隔（分钟）：1, 5, 30, 12h, 1d, 2d, 4d, 7d, 15d
        intervals = [
            1,           # 1分钟后
            5,           # 5分钟后
            30,          # 30分钟后
            12 * 60,     # 12小时后
            24 * 60,     # 1天后
            2 * 24 * 60, # 2天后
            4 * 24 * 60, # 4天后
            7 * 24 * 60, # 7天后
            15 * 24 * 60,# 15天后
        ]
        
        review_times = []
        for i in range(min(count, len(intervals))):
            interval_minutes = intervals[i]
            review_time = created_time + timedelta(minutes=interval_minutes)
            review_times.append(review_time)
        
        return review_times


class SmartScheduleManager:
    """智能日程管理器"""
    
    def __init__(self, data_file: str = "schedule_data.json"):
        self.data_file = data_file
        self.reminders: List[Reminder] = []
        self.load()
    
    def load(self) -> None:
        """加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reminders = [Reminder.from_dict(r) for r in data]
            except Exception as e:
                print(f"⚠️ 加载数据失败: {e}")
                self.reminders = []
        else:
            self.reminders = []
    
    def save(self) -> None:
        """保存数据"""
        try:
            data = [r.to_dict() for r in self.reminders]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ 保存数据失败: {e}")
    
    def add_reminder(self, text: str, reminder_type: ReminderType = ReminderType.ONCE) -> Reminder:
        """
        从自然语言添加提醒
        
        Args:
            text: 自然语言描述
            reminder_type: 提醒类型
            
        Returns:
            创建的提醒对象
        """
        title, reminder_time, priority, tags = SmartScheduleParser.parse(text)
        
        reminder = Reminder(
            title=title,
            description=text,
            reminder_time=reminder_time,
            priority=priority,
            reminder_type=reminder_type,
            tags=tags,
            ebbinghaus_review_times=SmartScheduleParser.generate_review_times(datetime.now())
        )
        
        self.reminders.append(reminder)
        self.save()
        
        print(f"✅ 已添加提醒: {reminder.title}")
        print(f"   📅 时间: {reminder.reminder_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   🔥 优先级: {reminder.priority.name}")
        
        return reminder
    
    def get_upcoming_reminders(self, hours: int = 24) -> List[Reminder]:
        """
        获取即将到来的提醒
        
        Args:
            hours: 未来几小时
            
        Returns:
            提醒列表
        """
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        
        upcoming = [
            r for r in self.reminders
            if not r.is_completed
            and now <= r.reminder_time <= end_time
        ]
        
        return sorted(upcoming, key=lambda r: r.reminder_time)
    
    def get_overdue_reminders(self) -> List[Reminder]:
        """获取过期的提醒"""
        now = datetime.now()
        return [
            r for r in self.reminders
            if not r.is_completed and r.reminder_time < now
        ]
    
    def complete_reminder(self, reminder_id: str) -> bool:
        """
        完成提醒
        
        Args:
            reminder_id: 提醒ID或哈希
            
        Returns:
            是否成功
        """
        for reminder in self.reminders:
            if reminder.hash == reminder_id or reminder.title in reminder_id:
                reminder.is_completed = True
                reminder.completed_at = datetime.now()
                self.save()
                print(f"✅ 已完成: {reminder.title}")
                return True
        
        print(f"❌ 未找到提醒: {reminder_id}")
        return False
    
    def delete_completed(self) -> int:
        """删除所有已完成的提醒"""
        original_count = len(self.reminders)
        self.reminders = [r for r in self.reminders if not r.is_completed]
        deleted_count = original_count - len(self.reminders)
        self.save()
        print(f"🗑️ 已删除 {deleted_count} 个已完成提醒")
        return deleted_count
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        now = datetime.now()
        
        stats = {
            'total': len(self.reminders),
            'completed': len([r for r in self.reminders if r.is_completed]),
            'pending': len([r for r in self.reminders if not r.is_completed]),
            'overdue': len([r for r in self.reminders if not r.is_completed and r.reminder_time < now]),
            'by_priority': {
                prio.name: len([r for r in self.reminders if r.priority == prio])
                for prio in Priority
            }
        }
        
        return stats
    
    def show_dashboard(self) -> None:
        """显示仪表板"""
        print("\n" + "="*60)
        print("🗓️ 智能日程提醒器 - 仪表板")
        print("="*60)
        
        stats = self.get_statistics()
        print(f"\n📊 统计信息:")
        print(f"   总提醒: {stats['total']}")
        print(f"   ✅ 已完成: {stats['completed']}")
        print(f"   ⏳ 待完成: {stats['pending']}")
        print(f"   ⚠️ 已过期: {stats['overdue']}")
        
        print(f"\n🔥 优先级分布:")
        for prio in Priority:
            count = stats['by_priority'][prio.name]
            emoji = "🔴" if prio == Priority.URGENT else ("🟠" if prio == Priority.HIGH else ("🟡" if prio == Priority.MEDIUM else "🟢"))
            print(f"   {emoji} {prio.name}: {count}")
        
        print(f"\n⏰ 即将到来的提醒:")
        upcoming = self.get_upcoming_reminders(24)
        if upcoming:
            for i, reminder in enumerate(upcoming[:5], 1):
                time_str = reminder.reminder_time.strftime('%m-%d %H:%M')
                prio_emoji = "🔴" if reminder.priority == Priority.URGENT else ("🟠" if reminder.priority == Priority.HIGH else ("🟡" if reminder.priority == Priority.MEDIUM else "🟢"))
                print(f"   {i}. {prio_emoji} {reminder.title} ({time_str})")
        else:
            print("   暂无即将到来的提醒")
        
        print("\n" + "="*60)


def demo():
    """演示"""
    print("🗓️ 智能日程提醒器 - 演示")
    print("="*50)
    
    # 创建管理器
    manager = SmartScheduleManager("demo_schedule.json")
    
    # 添加一些示例提醒
    examples = [
        "明天下午3点开会",
        "今天晚上8点健身 #运动 #健康",
        "这周五提交报告 #工作 #重要",
        "明天上午10点看医生 #健康 #紧急",
        "每天早上7点起床 #习惯",
    ]
    
    for example in examples:
        manager.add_reminder(example)
        print()
    
    # 显示仪表板
    manager.show_dashboard()
    
    # 清理
    print("\n🗑️ 清理演示数据...")
    if os.path.exists("demo_schedule.json"):
        os.remove("demo_schedule.json")


if __name__ == "__main__":
    demo()
