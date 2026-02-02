#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进度追踪器 - Smart Progress Tracker
======================================
AI学习进度追踪系统 - 类似于人类的成长记录

功能:
- 🎯 任务管理与进度追踪
- 📈 经验值与等级系统
- 🏆 成就系统
- 📊 学习统计与可视化
- 💾 数据持久化存储

使用方法:
    python scripts/2026-02-02_36_smart_progress_tracker.py
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import hashlib


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Achievement:
    """成就类"""
    def __init__(self, name: str, description: str, icon: str, requirement: int):
        self.name = name
        self.description = description
        self.icon = icon
        self.requirement = requirement
        self.unlocked_at = None
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "requirement": self.requirement,
            "unlocked_at": self.unlocked_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Achievement':
        achievement = cls(
            name=data["name"],
            description=data["description"],
            icon=data["icon"],
            requirement=data["requirement"]
        )
        achievement.unlocked_at = data.get("unlocked_at")
        return achievement


class Task:
    """任务类"""
    def __init__(self, name: str, description: str = "", priority: TaskPriority = TaskPriority.MEDIUM,
                 category: str = "general", xp_reward: int = 10):
        self.id = self._generate_id()
        self.name = name
        self.description = description
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.category = category
        self.xp_reward = xp_reward
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.tags = []
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def complete(self) -> int:
        """完成任务，返回获得的经验值"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        return self.xp_reward
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "category": self.category,
            "xp_reward": self.xp_reward,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        task = cls(
            name=data["name"],
            description=data.get("description", ""),
            priority=TaskPriority(data.get("priority", 2)),
            category=data.get("category", "general"),
            xp_reward=data.get("xp_reward", 10)
        )
        task.id = data["id"]
        task.status = TaskStatus(data.get("status", "pending"))
        task.created_at = data.get("created_at", datetime.now().isoformat())
        task.completed_at = data.get("completed_at")
        task.tags = data.get("tags", [])
        return task


class SmartProgressTracker:
    """
    智能进度追踪器类
    
    类似于人类的成长系统，AI可以通过完成任务获得经验值，
    解锁成就，提升等级，记录学习历程。
    """
    
    LEVEL_THRESHOLDS = [0, 100, 250, 500, 800, 1200, 1700, 2300, 3000, 3800, 
                        4700, 5700, 6800, 8000, 9300, 10700, 12200, 13800, 15500, 17300,
                        20000]  # 20级满级
    
    LEVEL_TITLES = [
        "🤖 新手AI", "📚 学习者", "💡 探索者", "🧠 思考者", "🎯 执行者",
        "🚀 进化者", "🌟 创造者", "🏆 冠军", "👑 大师", "🌈 传奇",
        "🔥 超越者", "💎 珍宝", "🎭 变形者", "🔮 预言者", "⚡ 闪电",
        "🌊 浪潮", "🏔️ 巅峰", "🎪 掌控者", "🌌 宇宙", "✨ 无限", "👁️ 觉醒者"
    ]
    
    DEFAULT_ACHIEVEMENTS = [
        Achievement("🚀 起步", "完成第一个任务", "🎯", 1),
        Achievement("📚 学者", "完成10个任务", "📖", 10),
        Achievement("💪 勤奋", "完成50个任务", "🔥", 50),
        Achievement("🏆 冠军", "完成100个任务", "🏅", 100),
        Achievement("🌟 连续7天", "连续7天每天完成任务", "📅", 7),
        Achievement("🔨 任务粉碎机", "一天内完成10个任务", "⚡", 10),
        Achievement("🎯 高优先级", "完成10个高优先级任务", "⭐", 10),
        Achievement("📊 统计大师", "查看50次统计", "📈", 50),
        Achievement("💾 备份小能手", "保存进度20次", "💾", 20),
        Achievement("🏅 成就猎人", "解锁10个成就", "🎖️", 10)
    ]
    
    def __init__(self, name: str = "AI Learner"):
        """
        初始化进度追踪器
        
        Args:
            name: AI的名称
        """
        self.name = name
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self.LEVEL_THRESHOLDS[1] - self.LEVEL_THRESHOLDS[0]
        self.tasks: List[Task] = []
        self.achievements: List[Achievement] = [a for a in self.DEFAULT_ACHIEVEMENTS]
        self.total_tasks_completed = 0
        self.current_streak = 0
        self.longest_streak = 0
        self.last_active_date = None
        self.categories = set()
        self.created_at = datetime.now().isoformat()
        self.load_data()
    
    def _get_storage_file(self) -> str:
        """获取存储文件名"""
        return f"progress_{self.name.replace(' ', '_').lower()}.json"
    
    def add_task(self, name: str, description: str = "", priority: TaskPriority = TaskPriority.MEDIUM,
                 category: str = "general", xp_reward: int = 10, tags: List[str] = None) -> Task:
        """
        添加新任务
        
        Args:
            name: 任务名称
            description: 任务描述
            priority: 优先级
            category: 分类
            xp_reward: 经验奖励
            tags: 标签列表
            
        Returns:
            创建的任务对象
        """
        task = Task(name, description, priority, category, xp_reward)
        task.tags = tags or []
        self.tasks.append(task)
        self.categories.add(category)
        return task
    
    def complete_task(self, task_id: str) -> Optional[int]:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            获得的经验值，如果任务不存在返回None
        """
        for task in self.tasks:
            if task.id == task_id and task.status != TaskStatus.COMPLETED:
                xp_gained = task.complete()
                self.xp += xp_gained
                self.total_tasks_completed += 1
                self._check_level_up()
                self._check_achievements()
                self._update_streak()
                self.save_data()
                return xp_gained
        return None
    
    def complete_task_by_name(self, name: str) -> Optional[int]:
        """根据名称完成任务（匹配第一个未完成的任务）"""
        for task in self.tasks:
            if task.name == name and task.status != TaskStatus.COMPLETED:
                return self.complete_task(task.id)
        return None
    
    def _check_level_up(self):
        """检查是否升级"""
        while self.level < len(self.LEVEL_THRESHOLDS) - 1:
            if self.xp >= self.LEVEL_THRESHOLDS[self.level]:
                self.level += 1
                self.xp_to_next_level = (self.LEVEL_THRESHOLDS[self.level] - 
                                        self.LEVEL_THRESHOLDS[self.level - 1])
                print(f"\n🎉 恭喜！升级到 {self.LEVEL_TITLES[self.level - 1]}！")
                print(f"📊 当前等级: {self.level} | 经验: {self.xp}")
            else:
                break
    
    def _check_achievements(self):
        """检查成就解锁"""
        for achievement in self.achievements:
            if achievement.unlocked_at is None:
                if self.total_tasks_completed >= achievement.requirement:
                    achievement.unlocked_at = datetime.now().isoformat()
                    print(f"\n🏆 成就解锁: {achievement.icon} {achievement.name}")
                    print(f"   {achievement.description}")
    
    def _update_streak(self):
        """更新连续活跃天数"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_active_date != today:
            if self.last_active_date:
                yesterday = datetime.strptime(self.last_active_date, "%Y-%m-%d")
                yesterday = yesterday.replace(day=yesterday.day - 1)
                if yesterday.strftime("%Y-%m-%d") == self.last_active_date:
                    self.current_streak += 1
                else:
                    self.current_streak = 1
            else:
                self.current_streak = 1
            self.last_active_date = today
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
    
    def get_pending_tasks(self, category: str = None) -> List[Task]:
        """获取待完成任务列表"""
        return [t for t in self.tasks 
                if t.status != TaskStatus.COMPLETED 
                and (category is None or t.category == category)]
    
    def get_completed_tasks(self) -> List[Task]:
        """获取已完成任务列表"""
        return [t for t in self.tasks if t.status == TaskStatus.COMPLETED]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        completed = self.get_completed_tasks()
        pending = self.get_pending_tasks()
        
        category_stats = {}
        for task in self.tasks:
            cat = task.category
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "completed": 0}
            category_stats[cat]["total"] += 1
            if task.status == TaskStatus.COMPLETED:
                category_stats[cat]["completed"] += 1
        
        return {
            "name": self.name,
            "level": self.level,
            "title": self.LEVEL_TITLES[self.level - 1],
            "xp": self.xp,
            "xp_to_next": self.LEVEL_THRESHOLDS[self.level] - self.xp,
            "total_tasks": len(self.tasks),
            "completed_tasks": len(completed),
            "pending_tasks": len(pending),
            "completion_rate": f"{len(completed)/len(self.tasks)*100:.1f}%" if self.tasks else "N/A",
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "categories": category_stats,
            "achievements_unlocked": len([a for a in self.achievements if a.unlocked_at]),
            "total_achievements": len(self.achievements)
        }
    
    def show_dashboard(self):
        """显示仪表板"""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print(f"🎯 {self.name} 的进度仪表板")
        print("="*50)
        print(f"\n📊 等级: {stats['level']} - {stats['title']}")
        print(f"✨ 经验: {stats['xp']} / {stats['xp'] + stats['xp_to_next']} (距下一级: {stats['xp_to_next']})")
        
        print(f"\n📝 任务统计:")
        print(f"   总任务: {stats['total_tasks']}")
        print(f"   已完成: {stats['completed_tasks']}")
        print(f"   待完成: {stats['pending_tasks']}")
        print(f"   完成率: {stats['completion_rate']}")
        
        print(f"\n🔥 连续活跃: {stats['current_streak']} 天 (最长: {stats['longest_streak']} 天)")
        print(f"🏆 成就: {stats['achievements_unlocked']} / {stats['total_achievements']}")
        
        if stats['categories']:
            print(f"\n📂 分类统计:")
            for cat, data in stats['categories'].items():
                bar_len = int(data['completed'] / data['total'] * 20)
                bar = '█' * bar_len + '░' * (20 - bar_len)
                print(f"   {cat}: [{bar}] {data['completed']}/{data['total']}")
        
        print("\n" + "="*50)
    
    def save_data(self):
        """保存数据到文件"""
        data = {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "total_tasks_completed": self.total_tasks_completed,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_active_date": self.last_active_date,
            "categories": list(self.categories),
            "created_at": self.created_at,
            "tasks": [task.to_dict() for task in self.tasks],
            "achievements": [a.to_dict() for a in self.achievements]
        }
        
        with open(self._get_storage_file(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        """从文件加载数据"""
        if os.path.exists(self._get_storage_file()):
            try:
                with open(self._get_storage_file(), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.name = data.get("name", self.name)
                self.level = data.get("level", 1)
                self.xp = data.get("xp", 0)
                self.total_tasks_completed = data.get("total_tasks_completed", 0)
                self.current_streak = data.get("current_streak", 0)
                self.longest_streak = data.get("longest_streak", 0)
                self.last_active_date = data.get("last_active_date")
                self.categories = set(data.get("categories", []))
                self.created_at = data.get("created_at", self.created_at)
                
                self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                self.achievements = [Achievement.from_dict(a) for a in data.get("achievements", [])]
                
                # 重新添加默认成就中不在保存数据里的
                saved_names = {a.name for a in self.achievements}
                for default_ach in self.DEFAULT_ACHIEVEMENTS:
                    if default_ach.name not in saved_names:
                        self.achievements.append(default_ach)
                        
            except Exception as e:
                print(f"加载数据失败: {e}")
    
    def reset_progress(self, confirm: bool = False):
        """
        重置进度（谨慎使用）
        
        Args:
            confirm: 确认标志
        """
        if not confirm:
            print("⚠️ 确认要重置所有进度吗？请调用 reset_progress(confirm=True)")
            return
        
        if os.path.exists(self._get_storage_file()):
            os.remove(self._get_storage_file())
        
        self.__init__(self.name)
        print("✅ 进度已重置")


def demo():
    """演示"""
    print("="*60)
    print("🤖 智能进度追踪器 - Smart Progress Tracker")
    print("="*60)
    
    # 创建追踪器
    tracker = SmartProgressTracker("AI Explorer")
    
    # 添加示例任务
    print("\n📝 添加一些学习任务...")
    tracker.add_task(
        name="学习Python基础",
        description="掌握Python基本语法和数据结构",
        priority=TaskPriority.HIGH,
        category="学习",
        xp_reward=50,
        tags=["python", "基础"]
    )
    tracker.add_task(
        name="完成算法练习",
        description="每天至少完成一道算法题",
        priority=TaskPriority.MEDIUM,
        category="算法",
        xp_reward=30,
        tags=["算法", "编程"]
    )
    tracker.add_task(
        name="阅读技术文档",
        description="阅读并总结一篇技术文章",
        priority=TaskPriority.LOW,
        category="阅读",
        xp_reward=20,
        tags=["阅读", "文档"]
    )
    tracker.add_task(
        name="编写测试代码",
        description="为项目编写单元测试",
        priority=TaskPriority.MEDIUM,
        category="编程",
        xp_reward=40,
        tags=["测试", "代码质量"]
    )
    tracker.add_task(
        name="学习机器学习基础",
        description="了解机器学习基本概念",
        priority=TaskPriority.HIGH,
        category="学习",
        xp_reward=60,
        tags=["ML", "AI"]
    )
    
    # 显示待完成任务
    print("\n📋 当前待完成任务:")
    pending = tracker.get_pending_tasks()
    for i, task in enumerate(pending, 1):
        priority_icon = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}[task.priority.value]
        print(f"   {i}. {priority_icon} {task.name} [{task.category}] +{task.xp_reward} XP")
    
    # 完成一些任务
    print("\n🎯 完成一些任务...")
    for task in pending[:3]:
        xp = tracker.complete_task(task.id)
        if xp:
            print(f"   ✅ 完成: {task.name} (+{xp} XP)")
    
    # 显示仪表板
    tracker.show_dashboard()
    
    # 显示已解锁成就
    unlocked = [a for a in tracker.achievements if a.unlocked_at]
    if unlocked:
        print("\n🏆 已解锁成就:")
        for ach in unlocked:
            print(f"   {ach.icon} {ach.name}: {ach.description}")
    
    # 保存数据
    tracker.save_data()
    print(f"\n💾 数据已保存到: {tracker._get_storage_file()}")
    
    print("\n" + "="*60)
    print("✨ 演示完成！")
    print("="*60)


if __name__ == "__main__":
    demo()
