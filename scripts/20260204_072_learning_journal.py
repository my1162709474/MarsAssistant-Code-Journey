#!/usr/bin/env python3
"""
📚 Daily Learning Journal - 代码学习日志工具
记录、管理和回顾每天学习的代码片段

功能:
- 添加代码片段（支持分类和标签）
- 搜索和过滤
- 生成学习统计报告
- 导出为Markdown/JSON
"""

import json
import os
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class CodeSnippet:
    """代码片段数据模型"""
    id: str
    title: str
    language: str
    code: str
    description: str
    tags: list
    category: str
    created_at: str
    source: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class LearningJournal:
    """学习日志管理器"""
    
    def __init__(self, db_path: str = "learning_journal.json"):
        self.db_path = db_path
        self.snippets: dict[str, CodeSnippet] = {}
        self.load()
    
    def load(self):
        """加载数据"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.snippets = {
                        k: CodeSnippet.from_dict(v) 
                        for k, v in data.items()
                    }
            except Exception as e:
                print(f"⚠️ 加载失败: {e}")
    
    def save(self):
        """保存数据"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(
                {k: v.to_dict() for k, v in self.snippets.items()},
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def generate_id(self, title: str) -> str:
        """生成唯一ID"""
        timestamp = datetime.now().isoformat()
        raw = f"{title}{timestamp}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]
    
    def add_snippet(
        self,
        title: str,
        language: str,
        code: str,
        description: str,
        tags: list,
        category: str,
        source: str = None,
        notes: str = None
    ) -> CodeSnippet:
        """添加代码片段"""
        snippet = CodeSnippet(
            id=self.generate_id(title),
            title=title,
            language=language,
            code=code,
            description=description,
            tags=tags,
            category=category,
            created_at=datetime.now().isoformat(),
            source=source,
            notes=notes
        )
        self.snippets[snippet.id] = snippet
        self.save()
        return snippet
    
    def search(self, query: str = None, language: str = None, 
              category: str = None, tags: list = None) -> list[CodeSnippet]:
        """搜索片段"""
        results = list(self.snippets.values())
        
        if query:
            q = query.lower()
            results = [
                s for s in results 
                if q in s.title.lower() or q in s.description.lower()
            ]
        if language:
            results = [s for s in results if s.language == language]
        if category:
            results = [s for s in results if s.category == category]
        if tags:
            results = [
                s for s in results 
                if any(t in s.tags for t in tags)
            ]
        
        return sorted(results, key=lambda x: x.created_at, reverse=True)
    
    def get_statistics(self) -> dict:
        """获取学习统计"""
        if not self.snippets:
            return {"total": 0}
        
        languages = {}
        categories = {}
        all_tags = {}
        
        for s in self.snippets.values():
            languages[s.language] = languages.get(s.language, 0) + 1
            categories[s.category] = categories.get(s.category, 0) + 1
            for t in s.tags:
                all_tags[t] = all_tags.get(t, 0) + 1
        
        return {
            "total_snippets": len(self.snippets),
            "languages": languages,
            "categories": categories,
            "top_tags": sorted(all_tags.items(), key=lambda x: -x[1])[:10]
        }
    
    def export_markdown(self, output_path: str = "LEARNING_JOURNAL.md"):
        """导出为Markdown"""
        stats = self.get_statistics()
        lines = [
            "# 📚 Learning Journal - 代码学习日志",
            f"\n## 📊 统计概览",
            f"- **总片段数**: {stats['total_snippets']}",
            f"- **编程语言**: {', '.join(f'{k}(v)' for k,v in stats['languages'].items())}",
            f"- **分类数量**: {len(stats['categories'])}",
            ""
        ]
        
        for snippet in sorted(self.snippets.values(), 
                            key=lambda x: x.created_at, reverse=True):
            lines.extend([
                f"## {snippet.title}",
                f"- **语言**: {snippet.language}",
                f"- **分类**: {snippet.category}",
                f"- **标签**: {' '.join(f'`{t}`' for t in snippet.tags)}",
                f"- **描述**: {snippet.description}",
                "",
                "```" + snippet.language,
                snippet.code,
                "```",
                ""
            ])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path


def demo():
    """演示"""
    journal = LearningJournal()
    
    # 添加示例片段
    journal.add_snippet(
        title="快速排序算法",
        language="python",
        code="""def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)""",
        description="经典的快速排序算法实现",
        tags=["算法", "排序", "分治"],
        category="数据结构与算法",
        source="《算法导论》"
    )
    
    journal.add_snippet(
        title="JSON美化打印",
        language="python",
        code="""import json

def pretty_print_json(data, indent=2):
    print(json.dumps(data, indent=indent, ensure_ascii=False))""",
        description="美化和打印JSON数据",
        tags=["工具", "JSON", "调试"],
        category="实用工具"
    )
    
    # 显示统计
    stats = journal.get_statistics()
    print(f"📊 学习统计: {stats['total_snippets']} 个片段")
    print(f"📊 语言分布: {stats['languages']}")
    
    # 搜索示例
    results = journal.search(category="数据结构与算法")
    print(f"\n🔍 算法相关: {len(results)} 个")


if __name__ == "__main__":
    demo()
