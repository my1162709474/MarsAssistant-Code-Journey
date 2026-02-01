#!/usr/bin/env python3
"""
🚀 AI生产力助手 - Day 71
一个帮助AI（和人类）提高效率的生产力工具

功能：
1. 任务优先级排序（艾森豪威尔矩阵）
2. 时间块规划
3. 番茄工作法计时器
4. 每日回顾生成

作者: MarsAssistant
日期: 2026-02-01
"""

import json
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
import random


class Priority(Enum):
    """任务优先级枚举"""
    URGENT_IMPORTANT = 1  # 重要且紧急
    NOT_URGENT_IMPORTANT = 2  # 重要不紧急
    URGENT_NOT_IMPORTANT = 3  # 紧急不重要
    NOT_URGENT_NOT_IMPORTANT = 4  # 不重要不紧急


class Task:
    """任务类"""
    def __init__(self, name: str, deadline: Optional[datetime] = None, 
                 importance: int = 5, urgency: int = 5):
        self.name = name
        self.deadline = deadline
        self.importance = importance  # 1-10
        self.urgency = urgency  # 1-10
        self.completed = False
        self.created_at = datetime.now()
    
    def get_priority(self) -> Priority:
        """根据重要性和紧急性计算优先级"""
        if self.importance >= 7 and self.urgency >= 7:
            return Priority.URGENT_IMPORTANT
        elif self.importance >= 7 and self.urgency < 7:
            return Priority.NOT_URGENT_IMPORTANT
        elif self.importance < 7 and self.urgency >= 7:
            return Priority.URGENT_NOT_IMPORTANT
        else:
            return Priority.NOT_URGENT_NOT_IMPORTANT
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "importance": self.importance,
            "urgency": self.urgency,
": self.completed            "completed,
            "priority": self.get_priority().name
        }


class ProductivityAssistant:
    """AI生产力助手"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.pomodoro_duration = 25 * 60  # 25分钟
        self.break_duration = 5 * 60  # 5分钟
        self.completed_pomodoros = 0
    
    def add_task(self, name: str, importance: int = 5, 
                 urgency: int = 5, hours_until_deadline: int = 24):
        """添加新任务"""
        deadline = datetime.now() + timedelta(hours=hours_until_deadline)
        task = Task(name, deadline, importance, urgency)
        self.tasks.append(task)
        return task
    
    def prioritize_tasks(self) -> List[Task]:
        """对任务进行优先级排序"""
        return sorted(self.tasks, key=lambda t: (t.get_priority().value, 
                                                  t.deadline or datetime.max))
    
    def get_quadrant_tasks(self) -> Dict[str, List[Task]]:
        """获取艾森豪威尔矩阵四个象限的任务"""
        quadrants = {
            "🔴 重要且紧急（立即做）": [],
            "📅 重要不紧急（计划做）": [],
            "⚡ 紧急不重要（委托做）": [],
            "📌 不重要不延迟（减少做）": []
        }
        for task in self.tasks:
            if not task.completed:
                priority = task.get_priority()
                if priority == Priority.URGENT_IMPORTANT:
                    quadrants["🔴 重要且紧急（立即做）"].append(task)
                elif priority == Priority.NOT_URGENT_IMPORTANT:
                    quadrants["📅 重要不紧急（计划做）"].append(task)
                elif priority == Priority.URGENT_NOT_IMPORTANT:
                    quadrants["⚡ 紧急不重要（委托做）"].append(task)
                else:
                    quadrants["📌 不重要不延迟（减少做）"].append(task)
        return quadrants
    
    def start_pomodoro(self, task_name: str) -> None:
        """番茄工作法计时器"""
        print(f"\n🍅 开始番茄钟: {task_name}")
        print(f"⏱️ 专注时间: {self.pomodoro_duration // 60} 分钟")
        print("=" * 50)
        
        for remaining in range(self.pomodoro_duration, 0, -1):
            mins, secs = divmod(remaining, 60)
            print(f"\r⏰ 剩余时间: {mins:02d}:{secs:02d}", end="", flush=True)
            time.sleep(1)
        
        print("\n\n🔔 时间到！休息一下~")
        self.completed_pomodoros += 1
        self._take_break()
    
    def _take_break(self) -> None:
        """休息时间"""
        print(f"😌 休息: {self.break_duration // 60} 分钟")
        for remaining in range(self.break_duration, 0, -1):
            mins, secs = divmod(remaining, 60)
            print(f"\r⏰ 休息剩余: {mins:02d}:{secs:02d}", end="", flush=True)
            time.sleep(1)
        print("\n\n✨ 休息结束，继续工作！")
    
    def generate_daily_review(self) -> str:
        """生成每日回顾"""
        completed = [t for t in self.tasks if t.completed]
        pending = [t for t in self.tasks if not t.completed]
        
        review = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 每日回顾 - {datetime.now().strftime('%Y-%m-%d')}                    ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ 完成的任务: {len(completed)} 个                                       ║
║  ⏳ 待办任务: {len(pending)} 个                                          ║
║  🍅 完成番茄钟: {self.completed_pomodoros} 个                                ║
╠══════════════════════════════════════════════════════════════╣
║  💡 今日建议:                                                   ║
"""
        
        if pending:
            top_priority = self.prioritize_tasks()[0]
            review += f"║  • 优先处理: {top_priority.name[:40]}                       ║\n"
        
        if self.completed_pomodoros >= 8:
            review += "║  • 太棒了！你完成了8个以上的番茄钟！生产力爆棚！🚀         ║\n"
        elif self.completed_pomodoros >= 4:
            review += "║  • 不错！继续保持这个节奏！                                 ║\n"
        else:
            review += "║  • 明天可以尝试更多专注时间哦~                              ║\n"
        
        review += "╚══════════════════════════════════════════════════════════════╝"
        return review
    
    def export_tasks(self) -> str:
        """导出任务为JSON格式"""
        return json.dumps([t.to_dict() for t in self.tasks], 
                         ensure_ascii=False, indent=2)
    
    def display_dashboard(self) -> None:
        """显示生产力仪表板"""
        print("\n" + "=" * 60)
        print("     🚀 AI 生产力助手 - 仪表板")
        print("=" * 60)
        
        quadrants = self.get_quadrant_tasks()
        for quadrant_name, tasks in quadrants.items():
            print(f"\n{quadrant_name}")
            if tasks:
                for i, task in enumerate(tasks, 1):
                    deadline_str = ""
                    if task.deadline:
                        hours_left = (task.deadline - datetime.now()).total_seconds() / 3600
                        deadline_str = f" (⏰ {hours_left:.1f}小时后截止)"
                    print(f"  {i}. {task.name}{deadline_str}")
            else:
                print("  (无任务)")
        
        print("\n" + "=" * 60)
        print(f"📈 总任务数: {len(self.tasks)} | 完成: {len([t for t in self.tasks if t.completed])}")
        print(f"🍅 番茄钟: {self.completed_pomodoros}")
        print("=" * 60)


def demo():
    """演示"""
    print("🎯 AI生产力助手演示")
    print("=" * 60)
    
    assistant = ProductivityAssistant()
    
    # 添加示例任务
    assistant.add_task("完成代码审查", importance=8, urgency=9, hours_until_deadline=2)
    assistant.add_task("学习新算法", importance=7, urgency=4, hours_until_deadline=48)
    assistant.add_task("回复邮件", importance=5, urgency=8, hours_until_deadline=4)
    assistant.add_task("整理桌面", importance=3, urgency=2, hours_until_deadline=72)
    
    # 显示仪表板
    assistant.display_dashboard()
    
    # 显示每日回顾
    print(assistant.generate_daily_review())
    
    # 导出任务
    print("\n📤 任务导出 (JSON):")
    print(assistant.export_tasks())


if __name__ == "__main__":
    demo()
