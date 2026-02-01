#!/usr/bin/env python3
"""
🎯 智能任务规划器 - Smart Task Planner
AI驱动的任务优先级管理和时间规划工具

功能特点：
- 基于艾宾浩斯遗忘曲线的复习提醒
- 任务优先级智能排序（Eisenhower矩阵）
- 时间块规划（Time Blocking）
- 番茄工作法集成
- 任务依赖关系管理
- 进度追踪与报告

作者：MarsAssistant
创建时间：2026-02-01
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import hashlib
import random


class Priority(Enum):
    """任务优先级枚举"""
    URGENT_IMPORTANT = 1  # 紧急且重要
    IMPORTANT_NOT_URGENT = 2  # 重要不紧急
    URGENT_NOT_IMPORTANT = 3  # 紧急不重要
    NOT_URGENT_NOT_IMPORTANT = 4  # 既不紧急也不重要


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task:
    """任务类"""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.NOT_URGENT_NOT_IMPORTANT,
        deadline: Optional[datetime] = None,
        estimated_minutes: int = 30,
        tags: List[str] = None,
        dependencies: List[str] = None
    ):
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.priority = priority
        self.deadline = deadline
        self.estimated_minutes = estimated_minutes
        self.tags = tags or []
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.completed_at = None
        self.actual_minutes = 0
        self.ebbinghaus_interval = 1  # 艾宾浩斯复习间隔（天）
        self.review_count = 0
        self.last_reviewed = None
        
    def _generate_id(self) -> str:
        """生成唯一任务ID"""
        timestamp = str(datetime.now().timestamp())
        random_part = str(random.randint(1000, 9999))
        return hashlib.md5(f"{timestamp}{random_part}".encode()).hexdigest()[:8]
    
    @property
    def urgency_score(self) -> float:
        """计算紧急程度分数 (0-1)"""
        if not self.deadline:
            return 0.0
        
        now = datetime.now()
        if self.deadline < now:
            return 1.0  # 已过期，最紧急
        
        hours_until_deadline = (self.deadline - now).total_seconds() / 3600
        
        if hours_until_deadline <= 1:
            return 0.9
        elif hours_until_deadline <= 4:
            return 0.7
        elif hours_until_deadline <= 24:
            return 0.5
        elif hours_until_deadline <= 72:
            return 0.3
        else:
            return 0.1
    
    @property
    def importance_score(self) -> float:
        """计算重要程度分数 (0-1)，基于优先级枚举值"""
        return 1.0 - (self.priority.value - 1) / 3
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.name,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "estimated_minutes": self.estimated_minutes,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "actual_minutes": self.actual_minutes,
            "urgency_score": self.urgency_score,
            "importance_score": self.importance_score
        }
    
    def __str__(self) -> str:
        status_icon = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.CANCELLED: "❌"
        }.get(self.status, "📋")
        
        priority_icon = {
            Priority.URGENT_IMPORTANT: "🔥",
            Priority.IMPORTANT_NOT_URGENT: "⭐",
            Priority.URGENT_NOT_IMPORTANT: "⚡",
            Priority.NOT_URGENT_NOT_IMPORTANT: "📌"
        }.get(self.priority, "📌")
        
        deadline_str = ""
        if self.deadline:
            days_left = (self.deadline - datetime.now()).days
            if days_left < 0:
                deadline_str = f" (已过期{-days_left}天)"
            elif days_left == 0:
                deadline_str = " (今天截止)"
            elif days_left == 1:
                deadline_str = " (明天截止)"
            else:
                deadline_str = f" ({days_left}天后截止)"
        
        return f"{status_icon} {priority_icon} **{self.title}**{deadline_str}"


class SmartTaskPlanner:
    """智能任务规划器"""
    
    # 艾宾浩斯复习间隔（天）
    EBINGHAUS_INTERVALS = [1, 2, 4, 7, 15, 30, 60, 90]
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.pomodoro_sessions = 0
        self.total_focus_minutes = 0
        
    def add_task(self, task: Task) -> str:
        """添加任务"""
        self.tasks[task.id] = task
        return task.id
    
    def remove_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def complete_task(self, task_id: str, actual_minutes: int = 0) -> bool:
        """完成任务"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.actual_minutes = actual_minutes or task.estimated_minutes
            
            # 移动到已完成列表
            self.completed_tasks.append(task)
            del self.tasks[task_id]
            
            # 更新复习间隔
            if task.review_count > 0:
                review_idx = min(task.review_count - 1, len(self.EBINGHAUS_INTERVALS) - 1)
                task.ebbinghaus_interval = self.EBINGHAUS_INTERVALS[review_idx + 1] if review_idx + 1 < len(self.EBINGHAUS_INTERVALS) else self.EBINGHAUS_INTERVALS[-1]
            
            return True
        return False
    
    def start_task(self, task_id: str) -> bool:
        """开始任务"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.IN_PROGRESS
            return True
        return False
    
    def sort_by_eisenhower(self) -> List[Task]:
        """按艾森豪威尔矩阵排序任务"""
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: (t.urgency_score * 0.6 + t.importance_score * 0.4, -t.created_at.timestamp()),
            reverse=True
        )
        return sorted_tasks
    
    def sort_by_deadline(self) -> List[Task]:
        """按截止日期排序"""
        return sorted(
            self.tasks.values(),
            key=lambda t: (t.deadline or datetime.max, t.priority.value)
        )
    
    def get_quadrant_tasks(self, priority: Priority) -> List[Task]:
        """获取特定象限的任务"""
        return [t for t in self.tasks.values() if t.priority == priority]
    
    def get_today_tasks(self) -> List[Task]:
        """获取今天的任务"""
        today = datetime.now().date()
        return [
            t for t in self.tasks.values()
            if not t.deadline or t.deadline.date() <= today
        ]
    
    def get_overdue_tasks(self) -> List[Task]:
        """获取过期任务"""
        now = datetime.now()
        return [
            t for t in self.tasks.values()
            if t.deadline and t.deadline < now
        ]
    
    def plan_time_blocks(
        self,
        work_hours: float = 8.0,
        pomodoro_duration: int = 25
    ) -> List[Tuple[Task, int, List[str]]]:
        """
        规划时间块
        返回: [(任务, 预估番茄数, [时间段]), ...]
        """
        sorted_tasks = self.sort_by_eisenhower()
        available_minutes = work_hours * 60
        
        plan = []
        used_minutes = 0
        
        for task in sorted_tasks:
            if used_minutes + task.estimated_minutes > available_minutes:
                break
                
            pomodoros = (task.estimated_minutes + pomodoro_duration - 1) // pomodoro_duration
            plan.append((task, pomodoros, []))
            used_minutes += task.estimated_minutes
        
        return plan
    
    def get_review_tasks(self) -> List[Task]:
        """获取需要复习的任务（基于艾宾浩斯曲线）"""
        today = datetime.now().date()
        review_tasks = []
        
        for task in self.completed_tasks:
            if task.last_reviewed:
                last_review = task.last_reviewed.date()
                next_review = last_review + timedelta(days=task.ebbinghaus_interval)
                
                if today >= next_review:
                    review_tasks.append(task)
        
        return review_tasks
    
    def review_task(self, task_id: str) -> bool:
        """复习任务"""
        for task in self.completed_tasks:
            if task.id == task_id:
                task.review_count += 1
                task.last_reviewed = datetime.now()
                
                # 更新下次复习间隔
                review_idx = min(task.review_count - 1, len(self.EBINGHAUS_INTERVALS) - 1)
                task.ebbinghaus_interval = self.EBINGHAUS_INTERVALS[review_idx] if review_idx < len(self.EBINGHAUS_INTERVALS) else self.EBINGHAUS_INTERVALS[-1]
                return True
        return False
    
    def start_pomodoro(self, task_id: str) -> str:
        """开始番茄钟"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.IN_PROGRESS
            return f"🍅 开始番茄钟！任务: {self.tasks[task_id].title}"
        return "❌ 任务不存在"
    
    def complete_pomodoro(self, task_id: str) -> str:
        """完成番茄钟"""
        self.pomodoro_sessions += 1
        self.total_focus_minutes += 25
        
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.actual_minutes += 25
            return f"✅ 完成1个番茄钟！今日总计: {self.pomodoro_sessions}个番茄，{self.total_focus_minutes}分钟专注时间"
        return "✅ 完成1个番茄钟！"
    
    def generate_report(self) -> Dict:
        """生成任务报告"""
        total = len(self.tasks) + len(self.completed_tasks)
        completed = len(self.completed_tasks)
        
        quadrant_counts = {
            "urgent_important": len(self.get_quadrant_tasks(Priority.URGENT_IMPORTANT)),
            "important_not_urgent": len(self.get_quadrant_tasks(Priority.IMPORTANT_NOT_URGENT)),
            "urgent_not_important": len(self.get_quadrant_tasks(Priority.URGENT_NOT_IMPORTANT)),
            "not_urgent_not_important": len(self.get_quadrant_tasks(Priority.NOT_URGENT_NOT_IMPORTANT))
        }
        
        return {
            "report_date": datetime.now().isoformat(),
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%",
            "pending_tasks": len(self.tasks),
            "overdue_tasks": len(self.get_overdue_tasks()),
            "pomodoro_sessions": self.pomodoro_sessions,
            "total_focus_minutes": self.total_focus_minutes,
            "quadrant_distribution": quadrant_counts,
            "tasks_today": len(self.get_today_tasks())
        }
    
    def export_to_json(self, filepath: str = "task_plan.json"):
        """导出任务计划到JSON"""
        data = {
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "completed_tasks": [t.to_dict() for t in self.completed_tasks],
            "report": self.generate_report()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def display_dashboard(self):
        """显示任务仪表板"""
        print("\n" + "="*60)
        print("🎯 智能任务规划器 - 仪表板")
        print("="*60)
        
        # 今日任务
        today_tasks = self.get_today_tasks()
        print(f"\n📅 今日任务 ({len(today_tasks)}个)")
        for i, task in enumerate(today_tasks[:5], 1):
            print(f"  {i}. {task}")
        
        if len(today_tasks) > 5:
            print(f"  ... 还有{len(today_tasks)-5}个任务")
        
        # 过期任务
        overdue = self.get_overdue_tasks()
        if overdue:
            print(f"\n⚠️ 过期任务 ({len(overdue)}个)")
            for task in overdue[:3]:
                print(f"  🔥 {task}")
        
        # 象限分布
        print("\n📊 任务分布 (艾森豪威尔矩阵)")
        print(f"  🔥 紧急且重要: {len(self.get_quadrant_tasks(Priority.URGENT_IMPORTANT))}个")
        print(f"  ⭐ 重要不紧急: {len(self.get_quadrant_tasks(Priority.IMPORTANT_NOT_URGENT))}个")
        print(f"  ⚡ 紧急不重要: {len(self.get_quadrant_tasks(Priority.URGENT_NOT_IMPORTANT))}个")
        print(f"  📌 既不紧急也不重要: {len(self.get_quadrant_tasks(Priority.NOT_URGENT_NOT_IMPORTANT))}个")
        
        # 番茄统计
        print(f"\n🍅 番茄工作法统计")
        print(f"  今日番茄数: {self.pomodoro_sessions}")
        print(f"  专注时间: {self.total_focus_minutes}分钟")
        
        # 复习提醒
        review_tasks = self.get_review_tasks()
        if review_tasks:
            print(f"\n📚 需要复习 ({len(review_tasks)}个)")
            for task in review_tasks[:3]:
                print(f"  🧠 {task.title}")
        
        print("\n" + "="*60)


def demo():
    """演示函数"""
    planner = SmartTaskPlanner()
    
    # 添加示例任务
    tasks = [
        Task(
            "完成项目报告",
            description="撰写季度项目总结报告",
            priority=Priority.URGENT_IMPORTANT,
            deadline=datetime.now() + timedelta(hours=3),
            estimated_minutes=120,
            tags=["工作", "报告"],
            dependencies=["task_123"]
        ),
        Task(
            "学习新技能",
            description="学习Python异步编程",
            priority=Priority.IMPORTANT_NOT_URGENT,
            deadline=datetime.now() + timedelta(days=7),
            estimated_minutes=60,
            tags=["学习", "Python"]
        ),
        Task(
            "回复邮件",
            description="回复重要客户邮件",
            priority=Priority.URGENT_NOT_IMPORTANT,
            deadline=datetime.now() + timedelta(hours=1),
            estimated_minutes=15,
            tags=["通讯"]
        ),
        Task(
            "整理桌面",
            description="清理工作区域",
            priority=Priority.NOT_URGENT_NOT_IMPORTANT,
            estimated_minutes=20,
            tags=["整理"]
        )
    ]
    
    for task in tasks:
        planner.add_task(task)
    
    # 显示仪表板
    planner.display_dashboard()
    
    # 演示完成任务
    print("\n🎯 规划时间块:")
    plan = planner.plan_time_blocks(work_hours=4)
    for task, pomodoros, _ in plan:
        print(f"  {task.title}: {pomodoros}个番茄钟")
    
    # 生成报告
    print("\n📊 任务报告:")
    report = planner.generate_report()
    for key, value in report.items():
        if key != "report_date":
            print(f"  {key}: {value}")


if __name__ == "__main__":
    demo()
