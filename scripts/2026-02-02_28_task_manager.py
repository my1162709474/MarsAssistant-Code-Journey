#!/usr/bin/env python3
"""
CLI Task Manager & Sticky Notes Tool
命令行任务管理器和便签工具

功能:
- 创建/列出/完成/删除任务
- 添加便签并设置优先级
- 按标签分类任务
- 任务统计和进度跟踪
- 数据持久化存储 (JSON)

使用方法:
    python task_manager.py add "完成任务"
    python task_manager.py add "重要任务" --priority high --tags work
    python task_manager.py list
    python task_manager.py list --tag work
    python task_manager.py done <id>
    python task_manager.py delete <id>
    python task_manager.py add-note "提醒内容" --color yellow
    python task_manager.py notes
    python task_manager.py stats
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse

# 存储文件路径
DATA_DIR = Path.home() / ".task_manager"
TASKS_FILE = DATA_DIR / "tasks.json"
NOTES_FILE = DATA_DIR / "notes.json"

# 颜色配置
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
}

PRIORITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
}

NOTE_COLORS = {
    "yellow": "yellow",
    "blue": "blue",
    "green": "green",
    "pink": "purple",
    "orange": "red",
}


def init_storage():
    """初始化存储目录和文件"""
    DATA_DIR.mkdir(exist_ok=True)
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]")
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text("[]")


def load_tasks() -> list:
    """加载任务列表"""
    try:
        return json.loads(TASKS_FILE.read_text())
    except json.JSONDecodeError:
        return []


def save_tasks(tasks: list):
    """保存任务列表"""
    TASKS_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False))


def load_notes() -> list:
    """加载便签列表"""
    try:
        return json.loads(NOTES_FILE.read_text())
    except json.JSONDecodeError:
        return []


def save_notes(notes: list):
    """保存便签列表"""
    NOTES_FILE.write_text(json.dumps(notes, indent=2, ensure_ascii=False))


def get_next_id(items: list) -> int:
    """获取下一个可用ID"""
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def cmd_add(args):
    """添加新任务"""
    tasks = load_tasks()
    task = {
        "id": get_next_id(tasks),
        "content": args.content,
        "priority": args.priority,
        "tags": args.tags.split(",") if args.tags else [],
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    color = COLORS[PRIORITY_COLORS.get(task["priority"], "white")]
    print(f"{color}✓ 任务已添加 (ID: {task['id']}){COLORS['reset']}")
    print(f"  内容: {task['content']}")
    print(f"  优先级: {task['priority']}")


def cmd_list(args):
    """列出任务"""
    tasks = load_tasks()
    
    # 过滤条件
    if args.tag:
        tasks = [t for t in tasks if args.tag in t["tags"]]
    if args.completed:
        tasks = [t for t in tasks if t["completed"]]
    if args.pending:
        tasks = [t for t in tasks if not t["completed"]]
    
    if not tasks:
        print("📋 没有找到任务")
        return
    
    print("=" * 50)
    print("📋 任务列表")
    print("=" * 50)
    
    for task in tasks:
        status = "✓" if task["completed"] else "○"
        color = COLORS[PRIORITY_COLORS.get(task["priority"], "white")]
        
        line = f"{color}[{status}] {task['id']:2d}. {task['content']}{COLORS['reset']}"
        if task["tags"]:
            line += f" {COLORS['cyan']}#{', #'.join(task['tags'])}{COLORS['reset']}"
        
        if task["completed"]:
            line = f"{COLORS['green']}{line}{COLORS['reset']}"
        
        print(line)
    
    # 统计
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    print("-" * 50)
    print(f"总计: {total} | 已完成: {completed} | 待办: {total - completed}")


def cmd_done(args):
    """完成任务"""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == args.id), None)
    
    if not task:
        print(f"❌ 找不到任务 ID: {args.id}")
        return
    
    task["completed"] = True
    task["completed_at"] = datetime.now().isoformat()
    save_tasks(tasks)
    print(f"✅ 任务已完成: {task['content']}")


def cmd_delete(args):
    """删除任务"""
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != args.id]
    save_tasks(tasks)
    print(f"🗑️ 任务已删除 (ID: {args.id})")


def cmd_add_note(args):
    """添加便签"""
    notes = load_notes()
    note = {
        "id": get_next_id(notes),
        "content": args.content,
        "color": args.color,
        "created_at": datetime.now().isoformat(),
    }
    notes.append(note)
    save_notes(notes)
    
    color_code = COLORS[NOTE_COLORS.get(args.color, "yellow")]
    print(f"{color_code}📝 便签已添加 (ID: {note['id']}){COLORS['reset']}")
    print(f"  内容: {note['content']}")


def cmd_notes(args):
    """列出便签"""
    notes = load_notes()
    
    if not notes:
        print("📝 没有便签")
        return
    
    print("=" * 50)
    print("📝 便签墙")
    print("=" * 50)
    
    for note in notes:
        color_code = COLORS[NOTE_COLORS.get(note["color"], "yellow")]
        # 创建便签边框效果
        lines = note["content"].wrap(40) if hasattr(note["content"], 'wrap') else [note["content"]]
        
        print(f"{color_code}")
        print("┌" + "─" * 42 + "┐")
        for line in lines:
            print(f"│ {line:40s} │")
        print("└" + "─" * 42 + "┘")
        print(f"{COLORS['reset']}  创建于: {note['created_at'][:10]}")


def cmd_stats(args):
    """显示统计信息"""
    tasks = load_tasks()
    notes = load_notes()
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t["completed"]])
    pending_tasks = total_tasks - completed_tasks
    
    by_priority = {}
    for t in tasks:
        p = t["priority"]
        by_priority[p] = by_priority.get(p, 0) + 1
    
    all_tags = {}
    for t in tasks:
        for tag in t["tags"]:
            all_tags[tag] = all_tags.get(tag, 0) + 1
    
    print("=" * 50)
    print("📊 统计概览")
    print("=" * 50)
    print(f"📋 任务总数: {total_tasks}")
    print(f"✅ 已完成: {completed_tasks} ({completed_tasks/total_tasks*100:.1f}%)" if total_tasks else "✅ 已完成: 0")
    print(f"⏳ 待办事项: {pending_tasks}")
    print()
    print("📈 按优先级:")
    for priority, count in by_priority.items():
        bar = "█" * (count * 2)
        color = COLORS[PRIORITY_COLORS.get(priority, "white")]
        print(f"  {color}{priority:6s}: {bar} {count}{COLORS['reset']}")
    print()
    
    if all_tags:
        print("🏷️ 按标签:")
        for tag, count in sorted(all_tags.items(), key=lambda x: -x[1]):
            print(f"  #{tag}: {count}")
        print()
    
    print(f"📝 便签数量: {len(notes)}")
    print("=" * 50)


def cmd_clear(args):
    """清除已完成的任务"""
    tasks = load_tasks()
    original_count = len(tasks)
    tasks = [t for t in tasks if not t["completed"]]
    save_tasks(tasks)
    removed = original_count - len(tasks)
    print(f"🗑️ 已清除 {removed} 个已完成的任务")


def main():
    parser = argparse.ArgumentParser(
        description="CLI Task Manager & Sticky Notes Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    %(prog)s add "完成任务" --priority high --tags work
    %(prog)s list --tag work
    %(prog)s done 1
    %(prog)s add-note "记得喝水" --color yellow
    %(prog)s notes
    %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加新任务")
    add_parser.add_argument("content", help="任务内容")
    add_parser.add_argument("--priority", choices=["high", "medium", "low"], default="medium", help="优先级")
    add_parser.add_argument("--tags", default="", help="标签(逗号分隔)")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--tag", help="按标签过滤")
    list_parser.add_argument("--completed", action="store_true", help="只显示已完成")
    list_parser.add_argument("--pending", action="store_true", help="只显示待办")
    
    # done 命令
    done_parser = subparsers.add_parser("done", help="完成任务")
    done_parser.add_argument("id", type=int, help="任务ID")
    
    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("id", type=int, help="任务ID")
    
    # add-note 命令
    note_parser = subparsers.add_parser("add-note", help="添加便签")
    note_parser.add_argument("content", help="便签内容")
    note_parser.add_argument("--color", choices=list(NOTE_COLORS.keys()), default="yellow", help="便签颜色")
    
    # notes 命令
    subparsers.add_parser("notes", help="显示便签")
    
    # stats 命令
    subparsers.add_parser("stats", help="显示统计")
    
    # clear 命令
    subparsers.add_parser("clear", help="清除已完成任务")
    
    args = parser.parse_args()
    
    # 初始化存储
    init_storage()
    
    if args.command is None:
        parser.print_help()
        return
    
    # 执行命令
    if args.command == "add":
        cmd_add(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "done":
        cmd_done(args)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "add-note":
        cmd_add_note(args)
    elif args.command == "notes":
        cmd_notes(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "clear":
        cmd_clear(args)


if __name__ == "__main__":
    main()
