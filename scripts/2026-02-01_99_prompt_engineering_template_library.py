#!/usr/bin/env python3
"""
AI Prompt Engineering Template Library
Day 99: 专业的提示词模板集合，提升AI交互质量

Features:
- 多场景提示词模板
- Chain-of-Thought推理模板
- 角色扮演提示词
- Few-shot学习示例
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class PromptCategory(Enum):
    """提示词分类"""
    CODING = "coding"
    WRITING = "writing"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    LEARNING = "learning"
    PROBLEM_SOLVING = "problem_solving"


@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    category: PromptCategory
    description: str
    template: str
    examples: List[str]
    parameters: List[str]
    
    def format(self, **kwargs) -> str:
        """格式化模板，填充参数"""
        result = self.template
        for param in self.parameters:
            if param in kwargs:
                result = result.replace(f"{{{param}}}", str(kwargs[param]))
            else:
                result = result.replace(f"{{{param}}}", f"[{param}]")
        return result


class PromptEngine:
    """AI提示词引擎"""
    
    def __init__(self):
        self.templates = self._init_templates()
    
    def _init_templates(self) -> List[PromptTemplate]:
        """初始化模板库"""
        return [
            # ===== CODING =====
            PromptTemplate(
                name="code_review",
                category=PromptCategory.CODING,
                description="代码审查助手",
                template="""你是一位资深代码审查专家。请审查以下代码：

**代码语言**: {language}
**代码内容**:
```{language}
{code}
```

**审查要点**:
1. 代码质量和最佳实践
2. 潜在bug和安全问题
3. 性能优化建议
4. 代码风格和改进建议

请提供详细的审查报告，包括具体问题位置和改进方案。""",
                examples=["Python代码审查", "JavaScript优化建议"],
                parameters=["language", "code"]
            ),
            
            PromptTemplate(
                name="algorithm_explanation",
                category=PromptCategory.CODING,
                description="算法解释器",
                template="""请详细解释以下算法：

**算法名称**: {algorithm_name}
**问题描述**: {problem_description}
**代码实现**:
```{language}
{code}
```

请按照以下结构解释：
1. 算法核心思想
2. 时间/空间复杂度分析
3. 关键步骤解析
4. 适用场景和局限性
5. 相关算法对比""",
                examples=["快速排序解释", "Dijkstra算法详解"],
                parameters=["algorithm_name", "problem_description", "code", "language"]
            ),
            
            # ===== CHAIN-OF-THOUGHT =====
            PromptTemplate(
                name="cot_reasoning",
                category=PromptCategory.PROBLEM_SOLVING,
                description="思维链推理",
                template="""请逐步推理解决以下问题：

**问题**: {problem}

请按照以下步骤思考：
1. **理解问题**: 明确问题要求和约束条件
2. **分解问题**: 将问题拆分为子问题
3. **制定策略**: 选择合适的解决方法
4. **执行推理**: 逐步推导解决方案
5. **验证结果**: 检查答案的正确性

**最终答案**:""",
                examples=["数学证明题", "逻辑推理题"],
                parameters=["problem"]
            ),
            
            PromptTemplate(
                name="cot_complex_reasoning",
                category=PromptCategory.PROBLEM_SOLVING,
                description="复杂问题思维链",
                template="""你是推理专家。请用详细的思维链解决复杂问题。

**背景信息**:
{context}

**问题**:
{question}

**要求**:
1. 列出所有已知信息
2. 识别关键关系和依赖
3. 建立推理链条
4. 考虑替代方案
5. 得出最终结论

**推理过程**:
[请详细展示每一步推理]

**结论**:""",
                examples=["商业决策分析", "技术方案选择"],
                parameters=["context", "question"]
            ),
            
            # ===== WRITING =====
            PromptTemplate(
                name="technical_writing",
                category=PromptCategory.WRITING,
                description="技术文档写作",
                template="""请撰写技术文档：

**主题**: {topic}
**目标读者**: {audience}
**技术深度**: {level}
**文档类型**: {doc_type}

**要求**:
- 使用清晰的结构和标题
- 包含代码示例（如果适用）
- 解释关键概念
- 提供最佳实践建议
- 适当使用图表说明

请生成完整的技术文档。""",
                examples=["API文档", "架构设计文档"],
                parameters=["topic", "audience", "level", "doc_type"]
            ),
            
            # ===== CREATIVE =====
            PromptTemplate(
                name="story_generation",
                category=PromptCategory.CREATIVE,
                description="故事生成器",
                template="""创作一个{genre}故事：

**核心元素**:
- 主角: {protagonist}
- 背景: {setting}
- 冲突: {conflict}
- 主题: {theme}

**要求**:
- 引人入胜的开头
- 逐步升级的冲突
- 出人意料但合理的转折
- 有意义的结局

**故事标题**: {title}

开始创作：""",
                examples=["科幻短篇", "悬疑故事"],
                parameters=["genre", "protagonist", "setting", "conflict", "theme", "title"]
            ),
            
            PromptTemplate(
                name="dialogue_writer",
                category=PromptCategory.CREATIVE,
                description="对话写作",
                template="""请撰写以下场景的对话：

**场景**: {scene}
**角色**:
{characters}

**风格**: {style}
**氛围**: {mood}

请写出自然、有深度的对话，展示角色性格和情感变化。""",
                examples=["面试场景", "朋友重逢"],
                parameters=["scene", "characters", "style", "mood"]
            ),
            
            # ===== ANALYSIS =====
            PromptTemplate(
                name="data_analysis",
                category=PromptCategory.ANALYSIS,
                description="数据分析报告",
                template="""请分析以下数据并生成报告：

**数据概述**:
{data_overview}

**分析目标**:
{objectives}

**关键指标**:
{metrics}

请提供：
1. 数据质量评估
2. 主要发现和洞察
3. 趋势分析
4. 异常识别
5. 建议和结论""",
                examples=["销售数据分析", "用户行为分析"],
                parameters=["data_overview", "objectives", "metrics"]
            ),
            
            PromptTemplate(
                name="code_analysis",
                category=PromptCategory.ANALYSIS,
                description="代码库分析",
                template="""请分析以下代码库结构：

**项目类型**: {project_type}
**主要功能**: {functionality}
**代码结构**:
{structure}

请提供：
1. 架构评估
2. 代码质量分析
3. 依赖关系梳理
4. 重构建议
5. 技术债务识别""",
                examples=["微服务分析", "单体应用评估"],
                parameters=["project_type", "functionality", "structure"]
            ),
            
            # ===== LEARNING =====
            PromptTemplate(
                name="concept_explainer",
                category=PromptCategory.LEARNING,
                description="概念解释器",
                template="""请解释以下概念：

**概念**: {concept}
**目标受众**: {audience}
**已有知识**: {prerequisites}
**解释深度**: {depth}

请使用：
- 日常生活中的类比
- 简单的例子
- 逐步深入的讲解
- 对比相关概念

让初学者也能理解。""",
                examples=["解释区块链", "解释机器学习"],
                parameters=["concept", "audience", "prerequisites", "depth"]
            ),
            
            PromptTemplate(
                name="quiz_generator",
                category=PromptCategory.LEARNING,
                description="测验生成器",
                template="""基于以下内容生成测验题：

**学习内容**:
{content}

**题目数量**: {num_questions}
**难度级别**: {difficulty}
**题目类型**: {question_types}

请生成包含答案和解析的测验题。""",
                examples=["历史测验", "编程测验"],
                parameters=["content", "num_questions", "difficulty", "question_types"]
            ),
            
            # ===== FEW-SHOT LEARNING =====
            PromptTemplate(
                name="few_shot_classification",
                category=PromptCategory.ANALYSIS,
                description="少样本分类示例",
                template="""请对以下文本进行分类：

**待分类文本**: {text}

**分类类别**: {categories}

**示例**:
{examples}

**分类结果**:""",
                examples=["情感分类", "意图识别"],
                parameters=["text", "categories", "examples"]
            ),
        ]
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取指定名称的模板"""
        for template in self.templates:
            if template.name == name:
                return template
        return None
    
    def list_by_category(self, category: PromptCategory) -> List[PromptTemplate]:
        """按分类列出模板"""
        return [t for t in self.templates if t.category == category]
    
    def search(self, query: str) -> List[PromptTemplate]:
        """搜索模板"""
        query_lower = query.lower()
        results = []
        for template in self.templates:
            if (query_lower in template.name.lower() or 
                query_lower in template.description.lower() or 
                query_lower in template.category.value):
                results.append(template)
        return results
    
    def add_custom_template(self, template: PromptTemplate):
        """添加自定义模板"""
        self.templates.append(template)
    
    def export_templates(self, format: str = "json") -> str:
        """导出模板库"""
        if format == "json":
            return json.dumps(
                [{"name": t.name, "category": t.category.value, 
                  "description": t.description, "parameters": t.parameters}
                 for t in self.templates],
                ensure_ascii=False,
                indent=2
            )
        return str(self.templates)


def demo():
    """演示模板使用"""
    engine = PromptEngine()
    
    # 示例1: 代码审查
    review_template = engine.get_template("code_review")
    if review_template:
        prompt = review_template.format(
            language="Python",
            code="""
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
            """.strip()
        )
        print("=" * 60)
        print("📝 示例1: 代码审查提示词")
        print("=" * 60)
        print(prompt[:500] + "...")
    
    # 示例2: 故事生成
    story_template = engine.get_template("story_generation")
    if story_template:
        prompt = story_template.format(
            genre="科幻",
            protagonist="一位孤独的宇航员",
            setting="火星殖民地",
            conflict="发现了一个古老的信号",
            theme="人类与未知",
            title="火星信号"
        )
        print("\n" + "=" * 60)
        print("📖 示例2: 故事生成提示词")
        print("=" * 60)
        print(prompt[:400] + "...")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("📊 模板库统计")
    print("=" * 60)
    print(f"总模板数: {len(engine.templates)}")
    for category in PromptCategory:
        count = len(engine.list_by_category(category))
        print(f"  {category.value}: {count}个模板")


if __name__ == "__main__":
    demo()
