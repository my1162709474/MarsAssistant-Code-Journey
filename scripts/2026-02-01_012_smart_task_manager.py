#!/usr/bin/env python3
"""
智能待办事项管理器 - Day 12
功能：
- 创建、列出、完成、删除待办事项
- 优先级设置（高/中/低）
- 截止日期提醒
- 分类标签
- 数据持久化存储
"""

import json
import os
from datetime import datetime
from typing import Optional

TASK_FILE = "tasks.json"

class TaskManager:
    def __init__(self):
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        """加载待办事项"""
        if os.path.exists(TASK_FILE):
            try:
                with open(TASK_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_tasks(self):
        """保存待办事项"""
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def create_task(self, title: str, priority: str = "中", 
                    category: str = "默认", due_date: Optional[str] = None):
        """创建新任务"""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "priority": priority,
            "category": category,
            "due_date": due_date,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": False,
            "completed_at": None
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def list_tasks(self, show_completed: bool = False):
        """列出待办事项"""
        result = []
        for task in self.tasks:
            if not show_completed and task["completed"]:
                continue
            result.append(task)
        return result
    
    def complete_task(self, task_id: int):
        """完成任务"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id: int):
        """删除任务"""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False
    
    def get_priority_icon(self, priority: str) -> str:
        """获取优先级图标"""
        icons = {"高": "🔴", "中": "🟡", "低": "🟢"}
        return icons.get(priority, "⚪")


def main():
    manager = TaskManager()
    
    # 示例：创建一些任务
    manager.create_task("学习Python高级特性", "高", "学习", "2026-02-15")
    manager.create_task("晨间运动30分钟", "中", "健康")
    manager.create_task("阅读技术文章", "低", "阅读")
    
    # 显示任务列表
    print("📋 智能待办事项管理器")
    print("=" * 50)
    
    tasks = manager.list_tasks()
    for task in tasks:
        icon = manager.get_priority_icon(task["priority"])
        due = f" (截止: {task['due_date']})" if task["due_date"] else ""
        status = "✅" if task["completed"] else "⬜"
        print(f"{status} [{task['id']}] {icon} {task['title']} "
              f"[{task['category']}]{due}")
    
    print("\n使用说明:")
    print("- create_task(标题, 优先级, 分类, 截止日期) - 创建任务")
    print("- complete_task(id) - 完成任务")
    print("- delete_task(id) - 删除任务")
    print("- list_tasks(show_completed) - 列出任务")


if __name__ == "__main__":
    main()
