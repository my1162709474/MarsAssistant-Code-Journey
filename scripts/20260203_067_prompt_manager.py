#!/usr/bin/env python3
"""AI Prompt Templates Manager - AI提示词模板管理器
Day 67: 管理和优化AI提示词的实用工具

功能:
- 创建、编辑、分类提示词模板
- 模板版本控制
- 变量替换支持
- 模板性能追踪
- 导入导出功能
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class Category(Enum):
    CODING = "coding"
    WRITING = "writing"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    Q_A = "q_and_a"
    OTHER = "other"


@dataclass
class PromptTemplate:
    id: str
    name: str
    category: str
    content: str
    variables: List[str]
    description: str
    created_at: str
    updated_at: str
    usage_count: int
    avg_rating: float
    tags: List[str]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PromptTemplate':
        return cls(**data)


class PromptManager:
    def __init__(self, storage_path: str = "prompts.json"):
        self.storage_path = storage_path
        self.templates: Dict[str, PromptTemplate] = {}
        self.versions: Dict[str, List[dict]] = {}
        self.usage_history: Dict[str, List[str]] = {}
        self._load()
    
    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for t_data in data.get('templates', []):
                        template = PromptTemplate.from_dict(t_data)
                        self.templates[template.id] = template
                    self.versions = data.get('versions', {})
                    self.usage_history = data.get('usage_history', {})
            except Exception as e:
                print(f"加载模板失败: {e}")
    
    def _save(self):
        data = {
            'templates': [t.to_dict() for t in self.templates.values()],
            'versions': self.versions,
            'usage_history': self.usage_history,
            'last_saved': datetime.now().isoformat()
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def extract_variables(self, content: str) -> List[str]:
        pattern = r'\{(\w+)\}'
        return list(set(re.findall(pattern, content)))
    
    def create_template(
        self,
        name: str,
        content: str,
        category: Category,
        description: str = "",
        tags: List[str] = None
    ) -> PromptTemplate:
        template_id = f"prompt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        variables = self.extract_variables(content)
        
        template = PromptTemplate(
            id=template_id,
            name=name,
            category=category.value,
            content=content,
            variables=variables,
            description=description,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            usage_count=0,
            avg_rating=0.0,
            tags=tags or []
        )
        
        self.templates[template_id] = template
        self.versions[template_id] = [
            {"version": 1, "content": content, "timestamp": datetime.now().isoformat(), "changes": "Initial version"}
        ]
        self._save()
        return template
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        return self.templates.get(template_id)
    
    def update_template(
        self,
        template_id: str,
        new_content: str,
        changes: str = ""
    ) -> Optional[PromptTemplate]:
        if template_id not in self.templates:
            return None
        
        template = self.templates[template_id]
        version_list = self.versions.get(template_id, [])
        new_version_num = len(version_list) + 1
        
        version = {
            "version": new_version_num,
            "content": new_content,
            "timestamp": datetime.now().isoformat(),
            "changes": changes or f"Updated from version {new_version_num - 1}"
        }
        
        if template_id not in self.versions:
            self.versions[template_id] = []
        self.versions[template_id].append(version)
        
        template.content = new_content
        template.variables = self.extract_variables(new_content)
        template.updated_at = datetime.now().isoformat()
        
        self._save()
        return template
    
    def render_template(
        self,
        template_id: str,
        variables: Dict[str, str]
    ) -> Optional[str]:
        template = self.templates.get(template_id)
        if not template:
            return None
        
        content = template.content
        for var, value in variables.items():
            content = content.replace(f'{{{var}}}', value)
        
        template.usage_count += 1
        if template_id not in self.usage_history:
            self.usage_history[template_id] = []
        self.usage_history[template_id].append(datetime.now().isoformat())
        self._save()
        
        return content
    
    def search_templates(
        self,
        query: str = "",
        category: Optional[Category] = None,
        tags: List[str] = None,
        min_rating: float = 0.0
    ) -> List[PromptTemplate]:
        results = list(self.templates.values())
        
        if query:
            query = query.lower()
            results = [
                t for t in results 
                if query in t.name.lower() or 
                   query in t.content.lower() or
                   query in t.description.lower()
            ]
        
        if category:
            results = [t for t in results if t.category == category.value]
        
        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]
        
        if min_rating > 0:
            results = [t for t in results if t.avg_rating >= min_rating]
        
        return sorted(results, key=lambda x: (-x.usage_count, -x.avg_rating))
    
    def get_statistics(self) -> Dict[str, Any]:
        templates = list(self.templates.values())
        
        if not templates:
            return {"total_templates": 0}
        
        by_category = {}
        for t in templates:
            by_category[t.category] = by_category.get(t.category, 0) + 1
        
        total_usage = sum(t.usage_count for t in templates)
        
        return {
            "total_templates": len(templates),
            "by_category": by_category,
            "total_usage": total_usage,
            "avg_usage_per_template": round(total_usage / len(templates), 2)
        }
    
    def export_templates(self, format: str = "json") -> str:
        if format == "json":
            return json.dumps(
                [t.to_dict() for t in self.templates.values()],
                ensure_ascii=False,
                indent=2
            )
        elif format == "markdown":
            lines = ["# AI Prompt Templates\n"]
            for category in Category:
                cats_templates = [
                    t for t in self.templates.values() 
                    if t.category == category.value
                ]
                if cats_templates:
                    lines.append(f"\n## {category.value.upper()}\n")
                    for t in cats_templates:
                        lines.append(f"### {t.name}")
                        lines.append(f"- ID: `{t.id}`")
                        lines.append(f"- Usage: {t.usage_count}")
                        lines.append(f"- Rating: {t.avg_rating:.1f}")
                        lines.append(f"\n```\n{t.content}\n```\n")
            return '\n'.join(lines)
        return ""
    
    def import_templates(self, data: str, format: str = "json") -> int:
        count = 0
        if format == "json":
            try:
                templates_data = json.loads(data)
                for t_data in templates_data:
                    if 'id' not in t_data:
                        t_data['id'] = f"imported_{datetime.now().strftime('%Y%m%d%H%M%S')}_{count}"
                    template = PromptTemplate.from_dict(t_data)
                    self.templates[template.id] = template
                    count += 1
            except Exception as e:
                print(f"导入失败: {e}")
        self._save()
        return count


def demo():
    manager = PromptManager("/tmp/demo_prompts.json")
    
    coding_template = manager.create_template(
        name="Python Code Explainer",
        content="""请解释以下Python代码的功能：
```{language}
{code}
```

请逐行分析，并说明：
1. 代码的整体功能
2. 关键变量和函数的作用
3. 可能的优化点""",
        category=Category.CODING,
        description="用于解释Python代码的模板",
        tags=["python", "code", "explanation"]
    )
    
    writing_template = manager.create_template(
        name="Article Outline Generator",
        content="""请为以下主题生成详细的文章大纲：

主题：{topic}
目标读者：{audience}
文章长度：{length}
风格：{style}

请生成：
1. 主标题
2. 引言要点
3. 3-5个主要章节（含子章节）
4. 结论要点""",
        category=Category.WRITING,
        description="生成文章结构的模板",
        tags=["writing", "outline", "structure"]
    )
    
    analysis_template = manager.create_template(
        name="Data Analysis Request",
        content="""请对以下数据进行{analysis_type}：

数据描述：{data_description}
数据样本：
```{data}
{data_sample}
```

请提供：
1. 关键发现
2. 统计摘要
3. 趋势分析
4. 建议和结论""",
        category=Category.ANALYSIS,
        description="数据分析请求模板",
        tags=["data", "analysis", "statistics"]
    )
    
    rendered = manager.render_template(
        coding_template.id,
        {"language": "python", "code": "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)"}
    )
    
    print("=" * 60)
    print("AI Prompt Templates Manager - Demo")
    print("=" * 60)
    print("\n渲染后的模板示例:")
    print("-" * 60)
    print(rendered)
    print()
    
    results = manager.search_templates(category=Category.CODING)
    print(f"编程相关模板: {len(results)} 个")
    
    stats = manager.get_statistics()
    print(f"\n统计信息: {json.dumps(stats, indent=2)}")
    
    print("\n" + "=" * 60)
    print("Markdown导出预览 (前200字符):")
    print("=" * 60)
    md = manager.export_templates("markdown")
    print(md[:500] + "...")


if __name__ == "__main__":
    demo()
