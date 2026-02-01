"""
AI Prompt Optimizer - Day 022
智能提示词优化器：自动分析和优化AI提示词，提升回复质量
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class PromptIssue(Enum):
    """提示词问题类型"""
    VAGUE = "vague"
    TOO_LONG = "too_long"
    TOO_SHORT = "too_short"
    NO_CONTEXT = "no_context"
    NO_EXAMPLES = "no_examples"
    AMBIGUOUS = "ambiguous"
    MISSING_FORMAT = "missing_format"
    COMPLEX = "too_complex"


@dataclass
class PromptAnalysis:
    """提示词分析结果"""
    score: int  # 0-100
    issues: List[PromptIssue]
    suggestions: List[str]
    clarity: str
    completeness: str


class AIPromptOptimizer:
    """AI提示词优化器"""
    
    def __init__(self):
        # 常用提示词模板
        self.excellent_patterns = [
            r".*明确的目标.*",
            r".*具体的上下文.*",
            r".*期望的输出格式.*",
            r".*示例.*",
            r".*约束条件.*",
        ]
        
        # 问题模式
        self.vague_patterns = [
            r"随便写写",
            r"帮我写点",
            r"做一些东西",
            r"看着办",
        ]
    
    def analyze(self, prompt: str) -> PromptAnalysis:
        """分析提示词质量"""
        score = 100
        issues = []
        suggestions = []
        
        # 1. 检查长度
        word_count = len(prompt.split())
        if word_count < 10:
            issues.append(PromptIssue.TOO_SHORT)
            score -= 20
            suggestions.append("提示词过短，建议添加更多细节和上下文")
        elif word_count > 500:
            issues.append(PromptIssue.TOO_LONG)
            score -= 15
            suggestions.append("提示词过长，建议精简，聚焦核心需求")
        
        # 2. 检查明确性
        has_verb = any(word in prompt.lower() for word in 
                      ['写', '创建', '分析', '生成', '设计', '实现', '解释'])
        if not has_verb:
            issues.append(PromptIssue.VAGUE)
            score -= 20
            suggestions.append("缺少明确的动词，建议使用具体的操作词（写、分析、生成等）")
        
        # 3. 检查上下文
        context_patterns = ['场景', '背景', '用途', '用于', '目的', '目标']
        has_context = any(pattern in prompt for pattern in context_patterns)
        if not has_context:
            issues.append(PromptIssue.NO_CONTEXT)
            score -= 15
            suggestions.append("建议添加使用场景或背景信息")
        
        # 4. 检查示例
        if '例如' not in prompt and '比如' not in prompt and '示例' not in prompt:
            issues.append(PromptIssue.NO_EXAMPLES)
            score -= 10
            suggestions.append("建议添加示例，帮助AI理解期望的输出")
        
        # 5. 检查输出格式
        format_patterns = ['格式', 'JSON', 'Markdown', '列表', '表格', '输出']
        has_format = any(pattern in prompt for pattern in format_patterns)
        if not has_format:
            issues.append(PromptIssue.MISSING_FORMAT)
            score -= 10
            suggestions.append("建议指定输出格式（如JSON、列表、Markdown等）")
        
        # 6. 模糊词汇检查
        vague_words = ['好', '漂亮', '专业', '好看', '正常']
        found_vague = [word for word in vague_words if word in prompt]
        if found_vague:
            issues.append(PromptIssue.AMBIGUOUS)
            score -= len(found_vague) * 5
            suggestions.append(f"'{', '.join(found_vague)}'是模糊词汇，建议用具体描述替代")
        
        # 生成详细建议
        if not issues:
            suggestions.append("👍 提示词结构良好！")
        else:
            suggestions.append("💡 优化建议：")
            for i, issue in enumerate(issues, 1):
                suggestions.append(f"  {i}. 解决{issue.value}问题")
        
        # 限制分数范围
        score = max(0, min(100, score))
        
        # 评估清晰度和完整性
        clarity = "优秀" if score >= 85 else "良好" if score >= 70 else "一般" if score >= 50 else "需改进"
        completeness = "完整" if has_context and has_format else "基本" if has_context or has_format else "不完整"
        
        return PromptAnalysis(
            score=score,
            issues=issues,
            suggestions=suggestions,
            clarity=clarity,
            completeness=completeness
        )
    
    def optimize(self, prompt: str) -> str:
        """生成优化后的提示词"""
        analysis = self.analyze(prompt)
        optimized = prompt
        
        # 添加上下文
        if PromptIssue.NO_CONTEXT in analysis.issues:
            optimized += "\n\n【背景说明】\n请根据实际应用场景提供专业建议。"
        
        # 添加格式要求
        if PromptIssue.MISSING_FORMAT in analysis.issues:
            optimized += "\n\n【输出格式】\n请以Markdown格式输出，包含清晰的标题和结构。"
        
        # 添加示例请求
        if PromptIssue.NO_EXAMPLES in analysis.issues:
            optimized += "\n\n【示例】\n请提供2-3个具体示例来说明。"
        
        return optimized


def demo():
    """演示"""
    optimizer = AIPromptOptimizer()
    
    test_prompts = [
        # 差的示例
        "帮我写点好代码",
        "做一个AI助手",
        
        # 好的示例  
        "作为Python专家，请帮我重构以下代码，要求：1.提高可读性 2.优化性能 3.添加类型注解 4.使用PEP8规范",
        "请分析这份用户反馈数据，找出主要痛点，并以表格形式呈现，包含问题分类、数量统计和改进建议",
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*60}")
        print(f"示例 {i}")
        print(f"{'='*60}")
        print(f"原始提示词：{prompt[:50]}...")
        
        result = optimizer.analyze(prompt)
        print(f"\n评分：{result.score}/100 ({result.clarity})")
        print(f"完整性：{result.completeness}")
        
        if result.issues:
            print(f"发现问题：{', '.join(issue.value for issue in result.issues)}")
        
        print(f"\n优化建议：")
        for suggestion in result.suggestions[:3]:
            print(f"  • {suggestion}")


if __name__ == "__main__":
    demo()
