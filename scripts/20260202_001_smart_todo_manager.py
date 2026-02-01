"""
🎯 智能待办事项管理器 - Smart Todo Manager
============================================
一个结合AI思维的待办事项管理工具，支持：
- 任务优先级智能排序
- 番茄钟专注模式
- 任务分解建议
- 完成统计与可视化

Author: MarsAssistant
Date: 2026-02-02
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import os


class Priority(Enum):
    """任务优先级枚举"""
    URGENT = 1      # 紧急
    HIGH = 2        # 高
    MEDIUM = 3      # 中
    LOW = 4         # 低
    DREAM = 5       # 梦想/长期目标


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """待办事项数据类"""
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    tags: List[str] = field(default_factory=list)
    estimated_minutes: int = 30
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        data['priority'] = Priority(data['priority'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class TodoManager:
    """智能待办事项管理器"""
    
    def __init__(self, filename: str = "todos.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.load()
    
    # ========== 基础CRUD操作 ==========
    
    def add(self, task: Task) -> str:
        """添加新任务"""
        self.tasks.append(task)
        self.save()
        return task.id
    
    def delete(self, task_id: str) -> bool:
        """删除任务"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self.save()
                return True
        return False
    
    def update(self, task_id: str, **kwargs) -> bool:
        """更新任务"""
        for task in self.tasks:
            if task.id == task_id:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                self.save()
                return True
        return False
    
    def complete(self, task_id: str) -> bool:
        """完成任务"""
        return self.update(task_id, 
                          status=TaskStatus.COMPLETED,
                          completed_at=datetime.now().isoformat())
    
    def get(self, task_id: str) -> Optional[Task]:
        """获取单个任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    # ========== 智能排序与过滤 ==========
    
    def get_pending(self) -> List[Task]:
        """获取所有待办任务"""
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]
    
    def get_by_priority(self, priority: Priority) -> List[Task]:
        """按优先级获取任务"""
        return sorted(
            [t for t in self.get_pending() if t.priority == priority],
            key=lambda x: x.created_at
        )
    
    def get_urgent_tasks(self) -> List[Task]:
        """获取紧急且未完成的任务"""
        urgent = [t for t in self.get_pending() 
                  if t.priority in [Priority.URGENT, Priority.HIGH]]
        # 按创建时间排序，最早的优先
        return sorted(urgent, key=lambda x: x.created_at)
    
    def get_today_tasks(self) -> List[Task]:
        """获取今天创建的任务"""
        today = datetime.now().date().isoformat()
        return [t for t in self.tasks if t.created_at[:10] == today]
    
    def get_by_tag(self, tag: str) -> List[Task]:
        """按标签获取任务"""
        return [t for t in self.tasks if tag in t.tags]
    
    # ========== 统计与分析 ==========
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
        pending = total - completed
        
        today = datetime.now().date().isoformat()
        today_completed = len([
            t for t in self.tasks 
            if t.status == TaskStatus.COMPLETED and t.completed_at[:10] == today
        ])
        
        return {
            "total_tasks": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": round(completed/total*100, 1) if total > 0 else 0,
            "today_completed": today_completed
        }
    
    # ========== AI智能建议 ==========
    
    def suggest_breakdown(self, task_title: str) -> List[str]:
        """AI式任务分解建议"""
        suggestions = [
            f"1. 明确{task_title}的具体目标",
            f"2. 列出完成{task_title}所需资源",
            f"3. 制定时间表和里程碑",
            f"4. 识别可能的风险和障碍",
            f"5. 准备备用方案"
        ]
        return suggestions
    
    def suggest_priority(self, task: Task) -> Priority:
        """智能建议优先级（简化版AI判断）"""
        # 简单规则：如果有"紧急"、"立即"等词，设为紧急
        urgent_words = ['紧急', '立即', '马上', 'asap', 'urgent']
        high_words = ['重要', '必须', '关键', '重要']
        
        title_lower = task.title.lower()
        for word in urgent_words:
            if word.lower() in title_lower:
                return Priority.URGENT
        for word in high_words:
            if word.lower() in title_lower:
                return Priority.HIGH
        return Priority.MEDIUM
    
    # ========== 番茄钟功能 ==========
    
    def start_pomodoro(self, task_id: str, minutes: int = 25) -> None:
        """启动番茄钟"""
        task = self.get(task_id)
        if task:
            print(f"\n🍅 开始番茄钟: {task.title}")
            print(f"⏰ 时长: {minutes} 分钟")
            print(f"🎯 专注力拉满！期间请避免分心...\n")
            
            for i in range(minutes, 0, -1):
                mins = i % 60
                print(f"\r⏳ 剩余: {mins:2d} 分钟", end="", flush=True)
                time.sleep(60)
            
            print("\n\n🎉 时间到！休息一下，喝杯水吧~")
            self.complete(task_id)
    
    # ========== 持久化 ==========
    
    def save(self) -> None:
        """保存到文件"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in self.tasks], f, 
                     ensure_ascii=False, indent=2)
    
    def load(self) -> None:
        """从文件加载"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data]
            except:
                self.tasks = []
    
    # ========== 显示格式 ==========
    
    def display(self, tasks: List[Task] = None) -> None:
        """友好地显示任务列表"""
        if tasks is None:
            tasks = self.get_pending()
        
        if not tasks:
            print("\n📭 暂无待办事项！")
            return
        
        print("\n" + "="*50)
        print("🎯 待办事项清单")
        print("="*50)
        
        for i, task in enumerate(tasks, 1):
            priority_icon = {1: '🔴', 2: '🟠', 3: '🟡', 4: '🟢', 5: '💜'}[task.priority.value]
            status_icon = {
                TaskStatus.PENDING: '⏳',
                TaskStatus.IN_PROGRESS: '🔄',
                TaskStatus.COMPLETED: '✅'
            }[task.status]
            
            print(f"{i}. {priority_icon} {status_icon} {task.title}")
            print(f"   📝 {task.description[:50]}..." if task.description else "   📝 无描述")
            print(f"   ⏱️ 预计: {task.estimated_minutes}分钟 | 🆔 {task.id}")
            if task.tags:
                print(f"   🏷️ 标签: {', '.join(task.tags)}")
            print("-" * 50)
        
        stats = self.get_stats()
        print(f"\n📊 统计: 共{stats['total_tasks']}个任务，完成{stats['completed']}个，完成率{stats['completion_rate']}%")
        print("="*50)


# ========== 演示与测试 ==========

def demo():
    """演示函数"""
    manager = TodoManager()
    
    # 添加示例任务
    demo_tasks = [
        Task(
            title="学习Python高级特性",
            description="学习装饰器、生成器、上下文管理器等",
            priority=Priority.HIGH,
            tags=["学习", "Python"],
            estimated_minutes=60
        ),
        Task(
            title="紧急修复Bug",
            description="用户反馈的登录问题需要立即处理",
            priority=Priority.URGENT,
            tags=["工作", "Bug修复"],
            estimated_minutes=120
        ),
        Task(
            title="规划周末旅行",
            description="制定旅行计划和预算",
            priority=Priority.DREAM,
            tags=["生活", "旅行"],
            estimated_minutes=45
        ),
        Task(
            title="阅读技术文章",
            description="AI最新进展相关论文阅读",
            priority=Priority.MEDIUM,
            tags=["学习", "AI"],
            estimated_minutes=30
        )
    ]
    
    for task in demo_tasks:
        # 智能推荐优先级
        suggested = manager.suggest_priority(task)
        task.priority = suggested
        manager.add(task)
    
    # 显示待办事项
    print("\n🌟 智能待办事项管理器演示")
    manager.display()
    
    # 显示统计
    stats = manager.get_stats()
    print(f"\n📈 统计面板:")
    print(f"   - 总任务数: {stats['total_tasks']}")
    print(f"   - 完成数: {stats['completed']}")
    print(f"   - 完成率: {stats['completion_rate']}%")
    
    # 任务分解建议
    print("\n💡 任务分解建议（以'学习Python高级特性'为例）:")
    for suggestion in manager.suggest_breakdown("学习Python高级特性"):
        print(f"   {suggestment}")


if __name__ == "__main__":
    demo()
