#!/usr/bin/env python3
"""
🎯 智能代码片段管理器 (Day 103)
智能代码片段管理、搜索和分类工具

功能特性:
- 📁 代码片段的添加、删除、更新和分类
- 🔍 多维度搜索（标签、关键词、编程语言）
- 📊 使用频率统计和热度分析
- 📂 支持自定义分类和标签系统
- 💾 JSON格式导入导出
- 🏷️ 智能标签推荐
"""

import json
import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field
from enum import Enum


class Language(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    BASH = "bash"
    OTHER = "other"


@dataclass
class CodeSnippet:
    """代码片段数据模型"""
    id: str
    title: str
    code: str
    language: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = "未分类"
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    favorite: bool = False
    notes: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeSnippet':
        return cls(**data)


class SnippetManager:
    """代码片段管理器"""
    
    # 编程语言关键词映射
    LANGUAGE_KEYWORDS = {
        Language.PYTHON: ['def ', 'class ', 'import ', 'from ', 'if __name__', 'print(', 'return '],
        Language.JAVASCRIPT: ['function ', 'const ', 'let ', '=>', 'console.log', 'import ', 'export '],
        Language.TYPESCRIPT: ['interface ', 'type ', ': string', ': number', ': any', '=>'],
        Language.JAVA: ['public class', 'public static', 'void ', 'System.out.', 'import '],
        Language.CPP: ['#include', 'std::', 'int main()', 'cout <<', 'cin >>'],
        Language.GO: ['func ', 'package ', 'import ', 'fmt.', 'struct '],
        Language.RUST: ['fn ', 'let mut', 'println!', 'struct ', 'impl '],
        Language.RUBY: ['def ', 'class ', 'require ', 'puts ', 'attr_'],
        Language.PHP: ['<?php', 'function ', 'echo ', '$', 'class '],
        Language.HTML: ['<html', '<div', '<script', '<style', '<!DOCTYPE'],
        Language.CSS: ['{', '}', ': ', ';', '.', '#', '@media'],
        Language.SQL: ['SELECT', 'FROM', 'WHERE', 'INSERT INTO', 'UPDATE ', 'DELETE FROM'],
        Language.BASH: ['#!/bin/', 'echo ', 'if [', 'fi', 'done', 'for '],
    }
    
    # 常见标签关键词
    TAG_KEYWORDS = {
        '排序': ['sort', 'sorted', '排序', 'compare'],
        '搜索': ['search', 'find', 'lookup', '查找', '搜索'],
        '列表': ['list', 'array', '[]', 'List', 'ArrayList'],
        '字符串': ['str', 'string', 'String', '字符串'],
        '文件': ['file', 'open', 'read', 'write', '文件'],
        '网络': ['http', 'request', 'url', '网络', 'API'],
        '日期': ['date', 'time', 'datetime', '日期', '时间'],
        '数据库': ['sql', 'query', 'database', 'db', '数据库'],
        '递归': ['recursive', 'recursion', '递归'],
        '动态规划': ['dp', 'dynamic', '动态规划'],
        '树': ['tree', 'node', 'root', '树', '节点'],
        '图': ['graph', 'edge', 'vertex', '图', '边'],
        '调试': ['debug', 'print', 'log', '调试', '日志'],
        '异常': ['try', 'except', 'catch', 'error', '异常', '错误'],
        '类': ['class', 'object', 'instance', '类', '对象'],
        '函数': ['function', 'def ', 'func', '函数'],
        '装饰器': ['decorator', '@', '装饰器'],
        '生成器': ['generator', 'yield', '生成器'],
        '异步': ['async', 'await', 'Promise', '异步', '并发'],
        '测试': ['test', 'assert', 'unittest', '测试', '断言'],
        '配置': ['config', 'setting', 'env', '配置', '环境'],
    }
    
    def __init__(self, storage_path: str = "snippets.json"):
        self.storage_path = storage_path
        self.snippets: Dict[str, CodeSnippet] = {}
        self.categories: set = set()
        self.tags: set = set()
        self.load()
    
    # ========== 文件操作 ==========
    
    def save(self) -> None:
        """保存到JSON文件"""
        data = {
            'snippets': {k: v.to_dict() for k, v in self.snippets.items()},
            'categories': list(self.categories),
            'tags': list(self.tags),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> None:
        """从JSON文件加载"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.snippets = {
                    k: CodeSnippet.from_dict(v) 
                    for k, v in data.get('snippets', {}).items()
                }
                self.categories = set(data.get('categories', []))
                self.tags = set(data.get('tags', []))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️ 加载片段失败: {e}，将创建新的存储")
                self.snippets = {}
        else:
            self.snippets = {}
            self.categories = {"未分类"}
            self.tags = set()
    
    def backup(self) -> str:
        """创建备份"""
        backup_path = f"snippets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = {
            'snippets': {k: v.to_dict() for k, v in self.snippets.items()},
            'categories': list(self.categories),
            'tags': list(self.tags),
            'backup_time': datetime.now().isoformat()
        }
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return backup_path
    
    # ========== 片段管理 ==========
    
    def add(self, title: str, code: str, language: str, 
            description: str = "", tags: Optional[List[str]] = None,
            category: str = "未分类", notes: str = "") -> str:
        """添加代码片段"""
        # 自动检测语言
        if language == 'auto':
            language = self.detect_language(code)
        
        # 自动生成标签
        if not tags:
            tags = self.auto_generate_tags(code)
        
        snippet_id = f"snippet_{len(self.snippets) + 1}_{int(datetime.now().timestamp())}"
        
        snippet = CodeSnippet(
            id=snippet_id,
            title=title,
            code=code,
            language=language,
            description=description,
            tags=tags,
            category=category,
            notes=notes
        )
        
        self.snippets[snippet_id] = snippet
        self.categories.add(category)
        self.tags.update(tags)
        self.save()
        
        print(f"✅ 已添加片段: {title} ({language})")
        return snippet_id
    
    def update(self, snippet_id: str, **kwargs) -> bool:
        """更新片段"""
        if snippet_id not in self.snippets:
            print(f"❌ 片段不存在: {snippet_id}")
            return False
        
        snippet = self.snippets[snippet_id]
        for key, value in kwargs.items():
            if hasattr(snippet, key):
                setattr(snippet, key, value)
        snippet.updated_at = datetime.now().isoformat()
        
        if 'tags' in kwargs:
            self.tags.update(kwargs['tags'])
        if 'category' in kwargs:
            self.categories.add(kwargs['category'])
        
        self.save()
        print(f"✅ 已更新片段: {snippet.title}")
        return True
    
    def delete(self, snippet_id: str) -> bool:
        """删除片段"""
        if snippet_id not in self.snippets:
            print(f"❌ 片段不存在: {snippet_id}")
            return False
        
        title = self.snippets[snippet_id].title
        del self.snippets[snippet_id]
        self.save()
        print(f"✅ 已删除片段: {title}")
        return True
    
    def get(self, snippet_id: str) -> Optional[CodeSnippet]:
        """获取片段"""
        return self.snippets.get(snippet_id)
    
    def duplicate(self, snippet_id: str, new_title: Optional[str] = None) -> Optional[str]:
        """复制片段"""
        if snippet_id not in self.snippets:
            print(f"❌ 片段不存在: {snippet_id}")
            return None
        
        original = self.snippets[snippet_id]
        return self.add(
            title=new_title or f"{original.title} (副本)",
            code=original.code,
            language=original.language,
            description=original.description,
            tags=original.tags.copy(),
            category=original.category,
            notes=original.notes
        )
    
    # ========== 搜索功能 ==========
    
    def search(self, query: str, search_mode: str = "all") -> List[CodeSnippet]:
        """搜索片段
        
        Args:
            query: 搜索关键词
            search_mode: 搜索模式 ('title', 'code', 'tags', 'all')
        """
        query = query.lower()
        results = []
        
        for snippet in self.snippets.values():
            matched = False
            
            if search_mode in ['title', 'all']:
                if query in snippet.title.lower():
                    matched = True
            
            if not matched and search_mode in ['code', 'all']:
                if query in snippet.code.lower():
                    matched = True
            
            if not matched and search_mode in ['tags', 'all']:
                if any(query in tag.lower() for tag in snippet.tags):
                    matched = True
            
            if not matched and search_mode == 'category':
                if query in snippet.category.lower():
                    matched = True
            
            if matched:
                results.append(snippet)
        
        # 按使用频率排序
        results.sort(key=lambda x: -x.usage_count)
        return results
    
    def search_by_language(self, language: str) -> List[CodeSnippet]:
        """按语言搜索"""
        return [s for s in self.snippets.values() 
                if s.language.lower() == language.lower()]
    
    def search_by_category(self, category: str) -> List[CodeSnippet]:
        """按分类搜索"""
        return [s for s in self.snippets.values() 
                if s.category.lower() == category.lower()]
    
    def search_by_tags(self, tags: List[str]) -> List[CodeSnippet]:
        """按标签搜索（AND逻辑）"""
        results = []
        for snippet in self.snippets.values():
            if all(tag.lower() in [t.lower() for t in snippet.tags] for tag in tags):
                results.append(snippet)
        return results
    
    def get_favorites(self) -> List[CodeSnippet]:
        """获取收藏的片段"""
        return [s for s in self.snippets.values() if s.favorite]
    
    def get_hot_snippets(self, limit: int = 10) -> List[CodeSnippet]:
        """获取热门片段"""
        return sorted(self.snippets.values(), 
                     key=lambda x: -x.usage_count)[:limit]
    
    def increment_usage(self, snippet_id: str) -> bool:
        """增加使用计数"""
        if snippet_id in self.snippets:
            self.snippets[snippet_id].usage_count += 1
            self.save()
            return True
        return False
    
    # ========== 统计分析 ==========
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.snippets)
        if total == 0:
            return {'total': 0}
        
        language_count = {}
        category_count = {}
        total_usage = 0
        
        for snippet in self.snippets.values():
            language_count[snippet.language] = language_count.get(snippet.language, 0) + 1
            category_count[snippet.category] = category_count.get(snippet.category, 0) + 1
            total_usage += snippet.usage_count
        
        return {
            'total': total,
            'categories': len(self.categories),
            'tags': len(self.tags),
            'total_usage': total_usage,
            'language_distribution': language_count,
            'category_distribution': category_count,
            'favorite_count': len(self.get_favorites())
        }
    
    # ========== 导出导入 ==========
    
    def export_json(self, filepath: Optional[str] = None) -> str:
        """导出为JSON"""
        if not filepath:
            filepath = f"snippets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'snippets': {k: v.to_dict() for k, v in self.snippets.items()},
            'categories': list(self.categories),
            'tags': list(self.tags),
            'export_time': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def import_json(self, filepath: str, merge: bool = True) -> int:
        """从JSON导入
        
        Args:
            filepath: 文件路径
            merge: 是否合并到现有片段
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        old_id_map = {}
        
        for old_id, snippet_data in data.get('snippets', {}).items():
            # 生成新ID
            new_id = f"imported_{len(self.snippets) + 1}_{int(datetime.now().timestamp())}"
            old_id_map[old_id] = new_id
            
            snippet = CodeSnippet.from_dict(snippet_data)
            snippet.id = new_id
            
            if not merge or snippet.id not in self.snippets:
                self.snippets[snippet.id] = snippet
                imported_count += 1
        
        self.categories.update(data.get('categories', []))
        self.tags.update(data.get('tags', []))
        self.save()
        
        print(f"✅ 已导入 {imported_count} 个片段")
        return imported_count
    
    def export_markdown(self, filepath: Optional[str] = None) -> str:
        """导出为Markdown文档"""
        if not filepath:
            filepath = f"snippets_{datetime.now().strftime('%Y%m%d')}.md"
        
        lines = [
            "# 代码片段集合",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"总计: {len(self.snippets)} 个片段",
            "",
            "---",
            ""
        ]
        
        # 按分类组织
        for category in sorted(self.categories):
            snippets_in_cat = [s for s in self.snippets.values() if s.category == category]
            if not snippets_in_cat:
                continue
            
            lines.append(f"## {category}")
            lines.append("")
            
            for snippet in sorted(snippets_in_cat, key=lambda x: -x.usage_count):
                lines.append(f"### {snippet.title}")
                lines.append(f"- 语言: {snippet.language}")
                lines.append(f"- 标签: {', '.join(snippet.tags) if snippet.tags else '无'}")
                lines.append(f"- 使用次数: {snippet.usage_count}")
                if snippet.description:
                    lines.append(f"- 说明: {snippet.description}")
                lines.append("")
                lines.append("```" + snippet.language)
                lines.append(snippet.code)
                lines.append("```")
                lines.append("")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return filepath
    
    # ========== 辅助功能 ==========
    
    def detect_language(self, code: str) -> str:
        """自动检测编程语言"""
        code_lower = code.lower()
        
        for lang, keywords in self.LANGUAGE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in code_lower)
            if score >= 2:
                return lang.value
        
        return Language.OTHER.value
    
    def auto_generate_tags(self, code: str) -> List[str]:
        """根据代码内容自动生成标签"""
        tags = []
        code_lower = code.lower()
        
        for tag, keywords in self.TAG_KEYWORDS.items():
            if any(kw.lower() in code_lower for kw in keywords):
                tags.append(tag)
        
        # 检测常见算法/数据结构
        if 'def ' in code or 'function ' in code:
            tags.append('函数')
        
        if 'class ' in code:
            tags.append('类')
        
        if 'if ' in code and 'else' in code:
            tags.append('条件语句')
        
        if 'for ' in code or 'while ' in code:
            tags.append('循环')
        
        if 'try:' in code or 'except' in code:
            tags.append('异常处理')
        
        return list(set(tags)) if tags else ['代码片段']
    
    def list_all(self, sort_by: str = "created") -> List[CodeSnippet]:
        """列出所有片段"""
        snippets = list(self.snippets.values())
        
        if sort_by == "title":
            snippets.sort(key=lambda x: x.title)
        elif sort_by == "language":
            snippets.sort(key=lambda x: x.language)
        elif sort_by == "category":
            snippets.sort(key=lambda x: x.category)
        elif sort_by == "usage":
            snippets.sort(key=lambda x: -x.usage_count)
        else:  # created or updated
            snippets.sort(key=lambda x: x.created_at, reverse=True)
        
        return snippets
    
    def toggle_favorite(self, snippet_id: str) -> bool:
        """切换收藏状态"""
        if snippet_id in self.snippets:
            self.snippets[snippet_id].favorite = not self.snippets[snippet_id].favorite
            self.save()
            return self.snippets[snippet_id].favorite
        return False
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return sorted(self.categories)
    
    def get_tags(self) -> List[str]:
        """获取所有标签"""
        return sorted(self.tags)
    
    def clear_all(self) -> int:
        """清空所有片段（谨慎使用）"""
        count = len(self.snippets)
        self.snippets = {}
        self.categories = {"未分类"}
        self.tags = set()
        self.save()
        print(f"🗑️ 已清空 {count} 个片段")
        return count


def demo():
    """演示示例"""
    print("=" * 50)
    print("🎯 智能代码片段管理器演示")
    print("=" * 50)
    
    # 创建管理器
    manager = SnippetManager("demo_snippets.json")
    
    # 添加示例片段
    print("\n📝 添加示例片段...")
    
    # Python 示例
    manager.add(
        title="快速排序算法",
        code='''def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)''',
        language="python",
        description="经典快速排序算法实现",
        tags=["排序", "算法", "递归"],
        category="算法"
    )
    
    # JavaScript 示例
    manager.add(
        title="数组去重",
        code='''function uniqueArray(arr) {
    return [...new Set(arr)];
}

// 或者
const unique = (arr) => Array.from(new Set(arr));''',
        language="javascript",
        description="使用Set实现数组去重",
        tags=["数组", "去重", "ES6"],
        category="工具函数"
    )
    
    manager.add(
        title="二分搜索",
        code='''def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',
        language="python",
        description="二分搜索算法",
        tags=["搜索", "算法", "二分"],
        category="算法"
    )
    
    # 统计信息
    print("\n📊 统计信息:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    - {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # 搜索演示
    print("\n🔍 搜索 '排序':")
    results = manager.search("排序")
    for snippet in results:
        print(f"  - {snippet.title} ({snippet.language})")
    
    print("\n🏷️ 按语言搜索 Python:")
    py_snippets = manager.search_by_language("python")
    for snippet in py_snippets:
        print(f"  - {snippet.title}")
    
    # 热门片段
    print("\n🔥 热门片段:")
    hot = manager.get_hot_snippets(3)
    for snippet in hot:
        print(f"  - {snippet.title}: {snippet.usage_count} 次使用")
    
    # 导出演示
    print("\n💾 导出文件:")
    json_path = manager.export_json("demo_export.json")
    print(f"  - JSON: {json_path}")
    md_path = manager.export_markdown("demo_export.md")
    print(f"  - Markdown: {md_path}")
    
    # 清理
    manager.clear_all()
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        # 交互式使用
        manager = SnippetManager()
        print("🎯 代码片段管理器已启动")
        print(f"📁 存储文件: {manager.storage_path}")
        print(f"📊 当前片段数: {len(manager.snippets)}")
        print("💡 使用 --demo 运行演示")
