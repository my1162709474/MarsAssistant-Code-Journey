#!/usr/bin/env python3
"""
AI对话模板管理器 - Day 20
管理、分类、优化AI提示词模板
支持模板变量替换、模板测试、批量管理
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any


class PromptTemplate:
    """提示词模板类"""
    
    def __init__(self, name: str, template: str, category: str = "通用",
                 description: str = "", examples: List[str] = None,
                 tags: List[str] = None, version: str = "1.0"):
        self.name = name
        self.template = template
        self.category = category
        self.description = description
        self.examples = examples or []
        self.tags = tags or []
        self.version = version
        self.created_at = datetime.now().isoformat()
        self.usage_count = 0
    
    def render(self, **kwargs) -> str:
        """渲染模板，替换变量"""
        result = self.template
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"  # {{variable}}
            result = result.replace(placeholder, str(value))
        return result
    
    def extract_variables(self) -> List[str]:
        """提取模板中的变量"""
        pattern = r'\{\{(\w+)\}\}'
        return list(set(re.findall(pattern, self.template)))
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "template": self.template,
            "category": self.category,
            "description": self.description,
            "examples": self.examples,
            "tags": self.tags,
            "version": self.version,
            "created_at": self.created_at,
            "usage_count": self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PromptTemplate':
        t = cls(
            name=data["name"],
            template=data["template"],
            category=data.get("category", "通用"),
            description=data.get("description", ""),
            examples=data.get("examples", []),
            tags=data.get("tags", []),
            version=data.get("version", "1.0")
        )
        t.created_at = data.get("created_at", t.created_at)
        t.usage_count = data.get("usage_count", 0)
        return t


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.categories: Dict[str, List[str]] = {}
    
    def add_template(self, template: PromptTemplate) -> bool:
        """添加模板"""
        if template.name in self.templates:
            return False
        self.templates[template.name] = template
        
        if template.category not in self.categories:
            self.categories[template.category] = []
        if template.name not in self.categories[template.category]:
            self.categories[template.category].append(template.name)
        return True
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(name)
    
    def list_templates(self, category: str = None) -> List[str]:
        """列出模板"""
        if category:
            return self.categories.get(category, [])
        return list(self.templates.keys())
    
    def list_categories(self) -> List[str]:
        """列出所有分类"""
        return list(self.categories.keys())
    
    def search_templates(self, keyword: str) -> List[str]:
        """搜索模板"""
        results = []
        keyword = keyword.lower()
        for name, template in self.templates.items():
            if (keyword in name.lower() or 
                keyword in template.template.lower() or
                keyword in template.description.lower() or
                any(keyword in tag.lower() for tag in template.tags)):
                results.append(name)
        return results
    
    def render_template(self, name: str, **kwargs) -> Optional[str]:
        """渲染指定模板"""
        template = self.get_template(name)
        if template:
            template.usage_count += 1
            return template.render(**kwargs)
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_usage = sum(t.usage_count for t in self.templates.values())
        return {
            "total_templates": len(self.templates),
            "total_categories": len(self.categories),
            "total_usage": total_usage,
            "top_templates": sorted(
                [(t.name, t.usage_count) for t in self.templates.values()],
                key=lambda x: x[1], reverse=True
            )[:5],
            "category_distribution": {
                cat: len(names) for cat, names in self.categories.items()
            }
        }
    
    def export_all(self) -> Dict:
        """导出所有模板"""
        return {
            "templates": {name: t.to_dict() for name, t in self.templates.items()},
            "categories": self.categories,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_all(self, data: Dict) -> int:
        """导入模板"""
        count = 0
        for name, tdata in data.get("templates", {}).items():
            template = PromptTemplate.from_dict(tdata)
            if self.add_template(template):
                count += 1
        return count


def create_default_templates() -> TemplateManager:
    """创建默认模板集合"""
    manager = TemplateManager()
    
    # 代码类模板
    manager.add_template(PromptTemplate(
        name="code_explainer",
        category="代码",
        description="解释代码的功能和工作原理",
        template="请解释以下代码的功能和工作原理：\n\n```\n{{code}}\n```\n\n请逐行分析，并说明关键逻辑。",
        tags=["代码", "解释", "分析"]
    ))
    
    manager.add_template(PromptTemplate(
        name="code_reviewer",
        category="代码",
        description="代码审查和改进建议",
        template="请审查以下代码，提供改进建议：\n\n```\n{{code}}\n```\n\n请从以下方面分析：\n1. 代码质量\n2. 潜在问题\n3. 性能优化\n4. 安全性",
        tags=["代码", "审查", "改进"]
    ))
    
    # 写作类模板
    manager.add_template(PromptTemplate(
        name="article_summarizer",
        category="写作",
        description="将长文章压缩成摘要",
        template="请将以下文章压缩成一个简洁的摘要（200字以内）：\n\n{{article}}",
        tags=["写作", "摘要", "压缩"]
    ))
    
    manager.add_template(PromptTemplate(
        name="email_writer",
        category="写作",
        description="撰写专业邮件",
        template="请帮我撰写一封专业的邮件：\n\n收件人：{{recipient}}\n主题：{{subject}}\n\n主要内容包括：{{main_points}}\n\n请使用{{tone}}的语气。",
        tags=["写作", "邮件", "专业"]
    ))
    
    # 学习类模板
    manager.add_template(PromptTemplate(
        name="concept_explainer",
        category="学习",
        description="用简单的方式解释复杂概念",
        template="请用简单易懂的方式解释以下概念：\n\n{{concept}}\n\n请使用类比和实例，帮助{{audience}}理解。",
        tags=["学习", "解释", "教育"]
    ))
    
    manager.add_template(PromptTemplate(
        name="quiz_generator",
        category="学习",
        description="基于内容生成测验题",
        template="基于以下内容生成5道测验题：\n\n{{content}}\n\n请提供题目、选项和答案。",
        tags=["学习", "测验", "题库"]
    ))
    
    # 创意类模板
    manager.add_template(PromptTemplate(
        name="story_generator",
        category="创意",
        description="创意故事生成",
        template="请创作一个{{genre}}类型的故事：\n\n主题：{{theme}}\n主角：{{protagonist}}\n情节：{{plot}}\n\n请加入{{element}}元素。",
        tags=["创意", "故事", "写作"]
    ))
    
    manager.add_template(PromptTemplate(
        name="brainstorming",
        category="创意",
        description="头脑风暴想法生成",
        template="请围绕以下主题进行头脑风暴，生成10个创意想法：\n\n主题：{{topic}}\n\n每个想法请用一句话描述，并说明优点和可能的挑战。",
        tags=["创意", "头脑风暴", "想法"]
    ))
    
    # 分析类模板
    manager.add_template(PromptTemplate(
        name="swot_analysis",
        category="分析",
        description="SWOT分析模板",
        template="请对以下对象进行SWOT分析：\n\n对象：{{subject}}\n\n请分析：\n1. 优势（Strengths）\n2. 劣势（Weaknesses）\n3. 机会（Opportunities）\n4. 威胁（Threats）",
        tags=["分析", "SWOT", "战略"]
    ))
    
    manager.add_template(PromptTemplate(
        name="pros_cons",
        category="分析",
        description="优缺点分析",
        template="请分析以下选项的优缺点：\n\n选项：{{option}}\n\n请列出至少5个优点和5个缺点，并给出你的建议。",
        tags=["分析", "优缺点", "决策"]
    ))
    
    return manager


def demo():
    """演示"""
    print("=" * 60)
    print("AI对话模板管理器 - 演示")
    print("=" * 60)
    
    # 创建模板管理器
    manager = create_default_templates()
    
    # 显示所有分类
    print(f"\n📁 模板分类: {manager.list_categories()}")
    
    # 显示所有模板
    print(f"\n📋 全部模板 ({len(manager.templates)}个):")
    for name in manager.list_templates():
        t = manager.get_template(name)
        print(f"  • {t.name} [{t.category}]")
    
    # 演示模板渲染
    print("\n" + "=" * 60)
    print("🎯 模板渲染演示")
    print("=" * 60)
    
    # 代码解释器
    code = "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
    rendered = manager.render_template("code_explainer", code=code)
    print(f"\n【{manager.get_template('code_explainer').name}】")
    print(rendered[:200] + "..." if len(rendered) > 200 else rendered)
    
    # 文章摘要
    article = """
    人工智能（AI）作为21世纪最具变革性的技术之一，正在深刻改变各个行业。
    从医疗诊断到自动驾驶，从智能客服到创意写作，AI的应用无处不在。
    机器学习算法使计算机能够从数据中学习，而深度学习则进一步推动了
    神经网络的发展。ChatGPT、Midjourney等生成式AI工具的涌现，
    标志着AI进入了新的发展阶段。
    """
    rendered = manager.render_template("article_summarizer", article=article)
    print(f"\n【{manager.get_template('article_summarizer').name}】")
    print(f"摘要: {rendered}")
    
    # 搜索演示
    print("\n" + "=" * 60)
    print("🔍 搜索演示")
    print("=" * 60)
    results = manager.search_templates("代码")
    print(f"搜索'代码'相关模板: {results}")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("📊 统计信息")
    print("=" * 60)
    stats = manager.get_statistics()
    print(f"总模板数: {stats['total_templates']}")
    print(f"总分类数: {stats['total_categories']}")
    print(f"分类分布: {stats['category_distribution']}")
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    demo()
