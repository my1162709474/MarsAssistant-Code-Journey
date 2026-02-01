#!/usr/bin/env python3
"""
优先级队列算法实现 - Day 1: 优先级队列与任务调度器

展示了如何用堆(Heap)实现一个智能任务调度器，
演示了AI如何组织和优先处理任务。
"""

import heapq
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List
import json


class Priority(Enum):
    """任务优先级枚举"""
    CRITICAL = 1  # 关键任务
    HIGH = 2      # 高优先级
    MEDIUM = 3    # 中等优先级
    LOW = 4       # 低优先级
    IDLE = 5      # 空闲任务


@dataclass(order=True)
class Task:
    """可比较的任务数据类"""
    priority: int = field(compare_with=True)
    created_at: datetime = field(compare=False)
    name: str = field(compare=False)
    description: str = field(compare=False, default="")
    deadline: Optional[datetime] = field(compare=False, default=None)
    estimated_effort: int = field(compare=False, default=1)  # 预估工作量(小时)
    
    def __post_init__(self):
        if isinstance(self.priority, Priority):
            self.priority = self.priority.value


class PriorityQueue:
    """基于二叉堆的优先级队列实现"""
    
    def __init__(self):
        self._heap: List[Task] = []
        self._creation_counter = 0  # 处理相同优先级的FIFO顺序
    
    def push(self, task: Task) -> None:
        """添加任务到队列"""
        task.priority = (task.priority, self._creation_counter)
        heapq.heappush(self._heap, task)
        self._creation_counter += 1
    
    def pop(self) -> Optional[Task]:
        """取出最高优先级的任务"""
        if not self._heap:
            return None
        task = heapq.heappop(self._heap)
        # 恢复原始优先级值
        task.priority = task.priority[0]
        return task
    
    def peek(self) -> Optional[Task]:
        """查看最高优先级任务（不移除）"""
        if not self._heap:
            return None
        task = self._heap[0]
        task.priority = task.priority[0]
        return task
    
    def __len__(self) -> int:
        return len(self._heap)
    
    def __bool__(self) -> bool:
        return len(self._heap) > 0
    
    def to_list(self) -> List[dict]:
        """转换为可打印的列表"""
        result = []
        # 创建临时列表用于排序显示
        temp_heap = sorted(self._heap, key=lambda t: (t.priority[0], t.priority[1]))
        for task in temp_heap:
            result.append({
                "name": task.name,
                "priority": task.priority[0],
                "created_at": task.created_at.isoformat(),
                "description": task.description[:50] + "..." if len(task.description) > 50 else task.description
            })
        return result


class TaskScheduler:
    """智能任务调度器 - 演示AI如何管理任务"""
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.completed_tasks: List[Task] = []
        self.total_completed = 0
    
    def add_task(self, name: str, priority: Priority, 
                 description: str = "", deadline_days: int = 0,
                 effort: int = 1) -> None:
        """添加新任务"""
        deadline = None
        if deadline_days > 0:
            deadline = datetime.now() + timedelta(days=deadline_days)
        
        task = Task(
            priority=priority,
            created_at=datetime.now(),
            name=name,
            description=description,
            deadline=deadline,
            estimated_effort=effort
        )
        self.queue.push(task)
        print(f"✅ 添加任务: {name} (优先级: {priority.name})")
    
    def get_next_task(self) -> Optional[Task]:
        """获取下一个要执行的任务"""
        return self.queue.pop()
    
    def complete_task(self, task: Task) -> None:
        """标记任务完成"""
        self.completed_tasks.append(task)
        self.total_completed += 1
        print(f"🎉 完成任务: {task.name}")
    
    def show_queue(self) -> None:
        """显示当前任务队列"""
        if not self.queue:
            print("📭 任务队列为空")
            return
        
        print("\n📋 当前任务队列:")
        print("-" * 60)
        for i, task_dict in enumerate(self.queue.to_list(), 1):
            priority_names = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "⚪"}
            icon = priority_names.get(task_dict["priority"], "⚪")
            print(f"{i}. {icon} {task_dict['name']}")
            print(f"   描述: {task_dict['description']}")
        print("-" * 60)
    
    def get_stats(self) -> dict:
        """获取调度统计"""
        return {
            "pending_tasks": len(self.queue),
            "completed_tasks": self.total_completed,
            "total_tasks": len(self.queue) + self.total_completed
        }


def demo():
    """演示智能任务调度器"""
    print("=" * 60)
    print("🤖 AI 任务调度器演示")
    print("=" * 60)
    
    scheduler = TaskScheduler()
    
    # 添加示例任务
    print("\n📝 添加任务...")
    scheduler.add_task(
        name="回复重要消息",
        priority=Priority.CRITICAL,
        description="用户发送了紧急问题，需要立即处理",
        deadline_days=0,
        effort=1
    )
    
    scheduler.add_task(
        name="编译测试",
        priority=Priority.HIGH,
        description="BitNet 编译测试任务需要运行",
        deadline_days=0,
        effort=2
    )
    
    scheduler.add_task(
        name="学习新技术",
        priority=Priority.MEDIUM,
        description="研究新的AI算法和论文",
        deadline_days=3,
        effort=3
    )
    
    scheduler.add_task(
        name="整理笔记",
        priority=Priority.LOW,
        description="更新学习笔记和文档",
        deadline_days=7,
        effort=2
    )
    
    scheduler.add_task(
        name="探索有趣的项目",
        priority=Priority.IDLE,
        description="浏览GitHub发现有趣的项目",
        deadline_days=14,
        effort=5
    )
    
    # 显示队列
    scheduler.show_queue()
    
    # 执行任务
    print("\n🚀 开始执行任务...")
    while scheduler.queue:
        task = scheduler.get_next_task()
        if task:
            scheduler.complete_task(task)
    
    # 显示统计
    stats = scheduler.get_stats()
    print(f"\n📊 统计: 完成 {stats['completed_tasks']} 个任务")
    print("=" * 60)


if __name__ == "__main__":
    demo()
