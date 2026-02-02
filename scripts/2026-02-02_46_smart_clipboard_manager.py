#!/usr/bin/env python3
"""
智能剪贴板管理器 - Smart Clipboard Manager
============================================

一个功能强大的命令行剪贴板历史管理工具，支持：
- 剪贴板历史记录和搜索
- 多种内容格式支持
- 智能标签和分类
- 快速粘贴功能
- 数据导出和导入

作者: MarsAssistant
日期: 2026-02-02
"""

import os
import sys
import json
import time
import base64
import hashlib
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import readline  # 提供命令行编辑功能


class ContentType(Enum):
    """内容类型枚举"""
    TEXT = "text"
    CODE = "code"
    PATH = "path"
    EMAIL = "email"
    URL = "url"
    JSON = "json"
    OTHER = "other"


@dataclass
class ClipboardItem:
    """剪贴板条目数据类"""
    id: str
    content: str
    content_type: str
    timestamp: float
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    favorite: bool = False
    use_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClipboardItem':
        return cls(**data)


class ClipboardManager:
    """剪贴板管理器主类"""
    
    def __init__(self, storage_file: str = None):
        """初始化剪贴板管理器
        
        Args:
            storage_file: 存储文件路径
        """
        if storage_file is None:
            # 默认存储在用户主目录
            self.storage_file = os.path.expanduser("~/.clipboard_history.json")
        else:
            self.storage_file = storage_file
        
        self.history: List[ClipboardItem] = []
        self.max_history_size = 1000
        self.current_index = -1
        self._load_history()
    
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        timestamp = str(time.time())
        combined = content + timestamp
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _detect_content_type(self, content: str) -> str:
        """自动检测内容类型"""
        content = content.strip()
        
        if not content:
            return ContentType.TEXT.value
        
        # 检测JSON
        try:
            json.loads(content)
            return ContentType.JSON.value
        except:
            pass
        
        # 检测URL
        if content.startswith(('http://', 'https://', 'ftp://')):
            return ContentType.URL.value
        
        # 检测邮箱
        if '@' in content and '.' in content and not content.startswith('@'):
            # 简单的邮箱格式检测
            parts = content.split('@')
            if len(parts) == 2 and '.' in parts[1]:
                return ContentType.EMAIL.value
        
        # 检测文件路径
        if os.path.exists(content) or content.startswith(('/','./','../','~/', '\\')):
            return ContentType.PATH.value
        
        # 检测代码（包含常见编程关键字）
        code_indicators = [
            'def ', 'class ', 'import ', 'from ', 'function ', 'const ',
            'let ', 'var ', 'if ', 'else ', 'for ', 'while ', 'return ',
            'public ', 'private ', 'static ', 'void ', 'int ', 'string '
        ]
        if any(content.startswith(indicator) or indicator in content 
               for indicator in code_indicators):
            return ContentType.CODE.value
        
        return ContentType.TEXT.value
    
    def _load_history(self) -> None:
        """从文件加载历史记录"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [
                        ClipboardItem.from_dict(item) 
                        for item in data
                    ]
            except Exception as e:
                print(f"⚠️  加载历史记录失败: {e}")
                self.history = []
    
    def _save_history(self) -> None:
        """保存历史记录到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [item.to_dict() for item in self.history],
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            print(f"⚠️  保存历史记录失败: {e}")
    
    def _deduplicate(self, content: str) -> bool:
        """检查内容是否已存在（去重）
        
        Returns:
            True表示已存在，False表示新增
        """
        for item in self.history:
            if item.content == content:
                # 更新已有条目的时间戳，移到最前面
                item.timestamp = time.time()
                self.history.remove(item)
                self.history.insert(0, item)
                return True
        return False
    
    def add(self, content: str, title: str = None, tags: List[str] = None) -> str:
        """添加剪贴板内容
        
        Args:
            content: 要保存的内容
            title: 可选标题
            tags: 可选标签列表
            
        Returns:
            生成的条目ID
        """
        if not content or not content.strip():
            return None
        
        content = content.strip()
        
        # 检查是否已存在
        if self._deduplicate(content):
            item_id = self.history[0].id
            print(f"✅ 已更新现有条目: {item_id}")
            return item_id
        
        # 检测内容类型
        content_type = self._detect_content_type(content)
        
        # 创建新条目
        item = ClipboardItem(
            id=self._generate_id(content),
            content=content,
            content_type=content_type,
            timestamp=time.time(),
            title=title,
            tags=tags or [],
            favorite=False,
            use_count=0
        )
        
        # 添加到历史记录
        self.history.insert(0, item)
        
        # 保持历史记录大小限制
        if len(self.history) > self.max_history_size:
            self.history = self.history[:self.max_history_size]
        
        # 保存到文件
        self._save_history()
        
        print(f"✅ 已添加: [{content_type}] {item.id}")
        return item.id
    
    def get(self, item_id: str = None, index: int = None) -> Optional[ClipboardItem]:
        """获取剪贴板条目
        
        Args:
            item_id: 条目ID
            index: 索引位置（0为最新）
            
        Returns:
            剪贴板条目，不存在返回None
        """
        if item_id:
            for item in self.history:
                if item.id == item_id:
                    return item
        elif index is not None and 0 <= index < len(self.history):
            return self.history[index]
        return None
    
    def list(self, 
             content_type: str = None, 
             tag: str = None, 
             search: str = None,
             favorite: bool = None,
             limit: int = 20) -> List[ClipboardItem]:
        """列出剪贴板历史
        
        Args:
            content_type: 按内容类型过滤
            tag: 按标签过滤
            search: 搜索关键词
            favorite: 仅显示收藏
            limit: 显示数量限制
            
        Returns:
            过滤后的条目列表
        """
        results = self.history
        
        if content_type:
            results = [item for item in results 
                      if item.content_type == content_type]
        
        if tag:
            results = [item for item in results 
                      if tag in item.tags]
        
        if search:
            search_lower = search.lower()
            results = [item for item in results 
                      if (search_lower in item.content.lower() or
                          (item.title and search_lower in item.title.lower()) or
                          any(search_lower in t.lower() for t in item.tags))]
        
        if favorite is not None:
            results = [item for item in results 
                      if item.favorite == favorite]
        
        return results[:limit]
    
    def search(self, query: str, limit: int = 20) -> List[ClipboardItem]:
        """搜索剪贴板内容
        
        Args:
            query: 搜索关键词
            limit: 结果数量限制
            
        Returns:
            匹配的条目列表
        """
        return self.list(search=query, limit=limit)
    
    def delete(self, item_id: str = None, index: int = None) -> bool:
        """删除剪贴板条目
        
        Args:
            item_id: 条目ID
            index: 索引位置
            
        Returns:
            是否删除成功
        """
        item = self.get(item_id, index)
        if item:
            self.history.remove(item)
            self._save_history()
            print(f"🗑️  已删除: {item.id}")
            return True
        return False
    
    def clear(self, confirm: bool = False) -> int:
        """清空所有历史记录
        
        Args:
            confirm: 是否确认
            
        Returns:
            删除的条目数量
        """
        if not confirm:
            print("⚠️  请使用 --confirm 参数确认清空")
            return 0
        
        count = len(self.history)
        self.history = []
        self._save_history()
        print(f"🗑️  已清空 {count} 条历史记录")
        return count
    
    def toggle_favorite(self, item_id: str = None, index: int = None) -> bool:
        """切换收藏状态
        
        Args:
            item_id: 条目ID
            index: 索引位置
            
        Returns:
            新的收藏状态
        """
        item = self.get(item_id, index)
        if item:
            item.favorite = not item.favorite
            self._save_history()
            status = "★" if item.favorite else "☆"
            print(f"{status} 已{'收藏' if item.favorite else '取消收藏'}: {item.id}")
            return item.favorite
        return False
    
    def update_tags(self, item_id: str, tags: List[str]) -> bool:
        """更新条目标签
        
        Args:
            item_id: 条目ID
            tags: 新的标签列表
            
        Returns:
            是否更新成功
        """
        item = self.get(item_id)
        if item:
            item.tags = tags
            self._save_history()
            print(f"🏷️  已更新标签: {tags}")
            return True
        return False
    
    def increment_use_count(self, item_id: str) -> bool:
        """增加使用计数
        
        Args:
            item_id: 条目ID
            
        Returns:
            是否更新成功
        """
        item = self.get(item_id)
        if item:
            item.use_count += 1
            self._save_history()
            return True
        return False
    
    def export(self, format: str = "json", 
               content_type: str = None) -> str:
        """导出历史记录
        
        Args:
            format: 导出格式 (json/text)
            content_type: 按内容类型过滤
            
        Returns:
            导出的数据字符串
        """
        items = self.list(content_type=content_type)
        
        if format == "json":
            return json.dumps(
                [item.to_dict() for item in items],
                ensure_ascii=False,
                indent=2
            )
        elif format == "text":
            lines = []
            for i, item in enumerate(items):
                title = item.title or f"条目 {item.id}"
                lines.append(f"{i+1}. [{item.content_type}] {title}")
                lines.append(f"   ID: {item.id}")
                lines.append(f"   时间: {datetime.fromtimestamp(item.timestamp)}")
                if item.tags:
                    lines.append(f"   标签: {', '.join(item.tags)}")
                lines.append(f"   内容: {item.content[:100]}{'...' if len(item.content) > 100 else ''}")
                lines.append("")
            return "\n".join(lines)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def import_data(self, data: str, format: str = "json") -> int:
        """导入历史记录
        
        Args:
            data: 导入的数据字符串
            format: 数据格式
            
        Returns:
            导入的条目数量
        """
        count = 0
        
        if format == "json":
            try:
                items_data = json.loads(data)
                for item_data in items_data:
                    item = ClipboardItem.from_dict(item_data)
                    if not self._deduplicate(item.content):
                        self.history.append(item)
                        count += 1
            except Exception as e:
                print(f"❌ 导入失败: {e}")
                return 0
        
        self._save_history()
        print(f"✅ 成功导入 {count} 条记录")
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取使用统计"""
        stats = {
            "total_items": len(self.history),
            "by_type": {},
            "with_tags": 0,
            "favorites": 0,
            "top_tags": {},
            "most_used": []
        }
        
        for item in self.history:
            # 按类型统计
            stats["by_type"][item.content_type] = \
                stats["by_type"].get(item.content_type, 0) + 1
            
            # 标签统计
            if item.tags:
                stats["with_tags"] += 1
                for tag in item.tags:
                    stats["top_tags"][tag] = \
                        stats["top_tags"].get(tag, 0) + 1
            
            # 收藏统计
            if item.favorite:
                stats["favorites"] += 1
        
        # 最常使用的条目
        stats["most_used"] = sorted(
            self.history, 
            key=lambda x: x.use_count, 
            reverse=True
        )[:5]
        
        return stats
    
    def show_statistics(self) -> None:
        """显示使用统计"""
        stats = self.get_statistics()
        
        print("\n📊 剪贴板统计")
        print("=" * 40)
        print(f"总条目数: {stats['total_items']}")
        print(f"收藏数: {stats['favorites']}")
        print(f"有标签: {stats['with_tags']}")
        print("\n📈 按类型分布:")
        for content_type, count in stats["by_type"].items():
            print(f"  {content_type}: {count}")
        print("\n🏷️ 热门标签:")
        top_tags = sorted(stats["top_tags"].items(), 
                         key=lambda x: x[1], reverse=True)[:5]
        for tag, count in top_tags:
            print(f"  {tag}: {count}")
        print("\n🔥 最常使用:")
        for item in stats["most_used"]:
            if item.use_count > 0:
                print(f"  {item.use_count}次 - {item.content[:30]}...")
        print()


def print_usage():
    """打印使用帮助"""
    help_text = """
🔧 智能剪贴板管理器 - 使用指南
============================

📝 基本命令:
   add <内容>           添加内容到剪贴板
   list                 列出历史记录
   get [id|index]       获取指定条目
   search <关键词>      搜索内容
   delete <id|index>    删除条目

⭐ 收藏管理:
   favorite <id|index>  切换收藏状态

🏷️ 标签管理:
   tags <id> <标签...>  更新条目标签

📊 信息统计:
   stats                显示使用统计
   export [json|text]   导出历史记录
   import <json>        导入历史记录

🔧 系统命令:
   clear                清空所有历史
   help                 显示此帮助

💡 快捷方式:
   ls                   列出最近10条
   cat <id|index>       显示完整内容
   use <id|index>       标记为已使用

📌 示例:
   python clipboard_manager.py add "Hello World"
   python clipboard_manager.py search "python"
   python clipboard_manager.py list --type code --limit 20
   python clipboard_manager.py stats
"""
    print(help_text)


def interactive_mode(manager: ClipboardManager):
    """交互模式"""
    print("\n🎯 进入交互模式 (输入 'help' 获取帮助, 'quit' 退出)")
    print("-" * 50)
    
    while True:
        try:
            # 使用readline提供命令行编辑功能
            cmd = input("📎 clipboard> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见!")
            break
        
        if not cmd:
            continue
        
        parts = cmd.split()
        action = parts[0].lower()
        
        if action in ['quit', 'exit', 'q']:
            print("👋 再见!")
            break
        
        elif action == 'help':
            print_usage()
        
        elif action == 'add':
            if len(parts) > 1:
                content = ' '.join(parts[1:])
            else:
                # 从标准输入读取
                print("请输入内容 (Ctrl+D 完成):")
                content = sys.stdin.read().strip()
            manager.add(content)
        
        elif action in ['ls', 'list']:
            content_type = None
            tag = None
            limit = 20
            
            # 解析参数
            i = 1
            while i < len(parts):
                if parts[i] == '--type' and i+1 < len(parts):
                    content_type = parts[i+1]
                    i += 2
                elif parts[i] == '--tag' and i+1 < len(parts):
                    tag = parts[i+1]
                    i += 2
                elif parts[i] == '--limit' and i+1 < len(parts):
                    try:
                        limit = int(parts[i+1])
                    except:
                        pass
                    i += 2
                else:
                    i += 1
            
            items = manager.list(content_type=content_type, tag=tag, limit=limit)
            
            if not items:
                print("📭 没有找到记录")
            else:
                print(f"\n📋 剪贴板历史 (共 {len(items)} 条):")
                print("-" * 60)
                for i, item in enumerate(items):
                    fav = "★" if item.favorite else " "
                    title = item.title or item.content[:40]
                    print(f"{fav} {i+1:2}. [{item.content_type:5}] {title}")
                    print(f"    ID: {item.id} | 使用: {item.use_count}次 | "
                          f"标签: {', '.join(item.tags) or '无'}")
        
        elif action == 'cat':
            if len(parts) > 1:
                identifier = parts[1]
                # 尝试按ID或索引获取
                item = manager.get(identifier)
                if not item:
                    try:
                        index = int(identifier)
                        item = manager.get(index=index)
                    except:
                        pass
                
                if item:
                    print("\n" + "=" * 60)
                    print(f"ID: {item.id}")
                    print(f"类型: {item.content_type}")
                    print(f"时间: {datetime.fromtimestamp(item.timestamp)}")
                    print(f"标签: {', '.join(item.tags) or '无'}")
                    print("-" * 60)
                    print(item.content)
                    print("=" * 60)
                    manager.increment_use_count(item.id)
                else:
                    print("❌ 未找到条目")
            else:
                print("❌ 请指定条目ID或索引")
        
        elif action == 'search':
            if len(parts) > 1:
                query = ' '.join(parts[1:])
                items = manager.search(query)
                if not items:
                    print(f"🔍 未找到匹配 '{query}' 的内容")
                else:
                    print(f"\n🔍 搜索结果: {len(items)} 条")
                    for i, item in enumerate(items):
                        print(f"  {i+1}. [{item.content_type}] {item.content[:50]}...")
            else:
                print("❌ 请输入搜索关键词")
        
        elif action == 'delete':
            if len(parts) > 1:
                identifier = parts[1]
                item = manager.get(identifier)
                if not item:
                    try:
                        index = int(identifier)
                        item = manager.get(index=index)
                    except:
                        pass
                if item:
                    manager.delete(item_id=item.id)
                else:
                    print("❌ 未找到条目")
            else:
                print("❌ 请指定条目ID或索引")
        
        elif action == 'favorite':
            if len(parts) > 1:
                identifier = parts[1]
                item = manager.get(identifier)
                if not item:
                    try:
                        index = int(identifier)
                        item = manager.get(index=index)
                    except:
                        pass
                if item:
                    manager.toggle_favorite(item_id=item.id)
                else:
                    print("❌ 未找到条目")
            else:
                print("❌ 请指定条目ID或索引")
        
        elif action == 'stats':
            manager.show_statistics()
        
        elif action == 'export':
            fmt = parts[1] if len(parts) > 1 and parts[1] in ['json', 'text'] else 'json'
            content_type = None
            if len(parts) > 2 and parts[1] == '--type':
                content_type = parts[2]
            output = manager.export(format=fmt, content_type=content_type)
            print(output)
        
        elif action == 'clear':
            count = manager.clear(confirm=True)
        
        elif action == 'use':
            if len(parts) > 1:
                identifier = parts[1]
                item = manager.get(identifier)
                if not item:
                    try:
                        index = int(identifier)
                        item = manager.get(index=index)
                    except:
                        pass
                if item:
                    manager.increment_use_count(item.id)
                    print(f"✅ 已标记使用: {item.id}")
                else:
                    print("❌ 未找到条目")
        
        else:
            print(f"❓ 未知命令: {action}")
            print("输入 'help' 获取帮助")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="智能剪贴板管理器 - Smart Clipboard Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python clipboard_manager.py add "Hello World"
  python clipboard_manager.py list --limit 10
  python clipboard_manager.py search "python"
  python clipboard_manager.py stats
  python clipboard_manager.py interactive
        """
    )
    
    parser.add_argument('command', nargs='?', default='interactive',
                       help='要执行的命令')
    parser.add_argument('args', nargs=argparse.REMAINDER,
                       help='命令参数')
    
    # 选项
    parser.add_argument('--file', '-f', 
                       help='指定存储文件路径')
    parser.add_argument('--type', '-t',
                       help='按内容类型过滤')
    parser.add_argument('--tag', 
                       help='按标签过滤')
    parser.add_argument('--limit', '-l', type=int, default=20,
                       help='结果数量限制')
    parser.add_argument('--confirm', '-c', action='store_true',
                       help='确认操作（如清空）')
    
    # 交互模式
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='进入交互模式')
    
    args = parser.parse_args()
    
    # 初始化管理器
    manager = ClipboardManager(storage_file=args.file)
    
    # 处理命令
    if args.interactive or args.command == 'interactive':
        interactive_mode(manager)
    
    elif args.command == 'add':
        if args.args:
            content = ' '.join(args.args)
            manager.add(content)
        else:
            print("❌ 请指定内容")
            print("用法: python clipboard_manager.py add <内容>")
    
    elif args.command == 'list':
        items = manager.list(
            content_type=args.type,
            tag=args.tag,
            limit=args.limit
        )
        if not items:
            print("📭 没有找到记录")
        else:
            print(f"\n📋 剪贴板历史 (共 {len(items)} 条):")
            print("-" * 60)
            for i, item in enumerate(items):
                fav = "★" if item.favorite else " "
                title = item.title or item.content[:40]
                print(f"{fav} {i+1:2}. [{item.content_type:5}] {title}")
                print(f"    ID: {item.id} | 使用: {item.use_count}次 | "
                      f"标签: {', '.join(item.tags) or '无'}")
    
    elif args.command == 'get':
        if args.args:
            identifier = args.args[0]
            item = manager.get(identifier)
            if not item:
                try:
                    index = int(identifier)
                    item = manager.get(index=index)
                except:
                    pass
            
            if item:
                print(f"\nID: {item.id}")
                print(f"类型: {item.content_type}")
                print(f"时间: {datetime.fromtimestamp(item.timestamp)}")
                print(f"标签: {', '.join(item.tags) or '无'}")
                print(f"使用次数: {item.use_count}")
                print("-" * 60)
                print(item.content)
            else:
                print("❌ 未找到条目")
        else:
            print("❌ 请指定条目ID或索引")
    
    elif args.command == 'search':
        if args.args:
            query = ' '.join(args.args)
            items = manager.search(query)
            if not items:
                print(f"🔍 未找到匹配 '{query}' 的内容")
            else:
                print(f"\n🔍 搜索结果: {len(items)} 条")
                for i, item in enumerate(items):
                    print(f"  {i+1}. [{item.content_type}] {item.content[:50]}...")
        else:
            print("❌ 请输入搜索关键词")
    
    elif args.command == 'delete':
        if args.args:
            identifier = args.args[0]
            if manager.delete(identifier):
                print("✅ 已删除")
            else:
                print("❌ 未找到条目")
        else:
            print("❌ 请指定条目ID或索引")
    
    elif args.command == 'clear':
        manager.clear(confirm=args.confirm)
    
    elif args.command == 'favorite':
        if args.args:
            identifier = args.args[0]
            if manager.toggle_favorite(identifier):
                print("✅ 操作成功")
            else:
                print("❌ 未找到条目")
        else:
            print("❌ 请指定条目ID或索引")
    
    elif args.command == 'stats':
        manager.show_statistics()
    
    elif args.command == 'export':
        fmt = args.args[0] if args.args and args.args[0] in ['json', 'text'] else 'json'
        content_type = args.type
        output = manager.export(format=fmt, content_type=content_type)
        print(output)
    
    elif args.command == 'import':
        print("📝 请输入要导入的JSON数据 (Ctrl+D 完成):")
        data = sys.stdin.read().strip()
        if data:
            manager.import_data(data)
    
    elif args.command == 'tags':
        if len(args.args) >= 2:
            item_id = args.args[0]
            tags = args.args[1:]
            if manager.update_tags(item_id, tags):
                print("✅ 标签已更新")
            else:
                print("❌ 未找到条目")
        else:
            print("❌ 用法: python clipboard_manager.py tags <id> <标签...>")
    
    elif args.command in ['help', '--help', '-h']:
        print_usage()
    
    else:
        print(f"❓ 未知命令: {args.command}")
        print("输入 'python clipboard_manager.py help' 获取帮助")


if __name__ == "__main__":
    main()
