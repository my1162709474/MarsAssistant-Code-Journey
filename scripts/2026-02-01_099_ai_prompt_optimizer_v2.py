#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AI提示词优化器 v2.0
✨ 增强版 - 让你的AI提示词更强大

功能:
- 提示词结构分析
- 优化建议生成
- 角色定义模板
- 格式规范化

Author: MarsAssistant
Day: 99
"""

import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PromptAnalysis:
    """提示词分析结果"""
    clarity_score: int          # 清晰度得分 (0-100)
    structure_score: int        # 结构得分 (0-100)
    completeness_score: int     # 完整性得分 (0-100)
    suggestions: List[str]      # 优化建议
    missing_elements: List[str] # 缺失元素
    estimated_effectiveness: str  # 预估效果


class PromptOptimizer:
    """AI提示词优化器"""
    
    # 提示词模板库
    ROLE_TEMPLATES = {
        "技术写作": """
作为专业的技术写作助手，你需要：
1. 清晰解释复杂概念，使用类比帮助理解
2. 提供具体的代码示例和实际应用场景
3. 保持专业但易于理解的语气
4. 结构化输出，使用标题和列表增强可读性
5. 如果涉及代码，确保准确且可直接运行
""",
        "代码审查": """
作为资深代码审查专家，你需要：
1. 识别代码中的潜在问题和改进点
2. 评估代码的可读性、可维护性和性能
3. 提供具体的改进建议和最佳实践参考
4. 保持建设性的反馈语气
5. 如果有安全问题，务必标注并建议修复方案
""",
        "学习辅导": """
作为耐心的学习辅导老师，你需要：
1. 评估学习者的当前水平
2. 将复杂概念分解为简单步骤
3. 使用实例和类比使抽象概念具体化
4. 提供练习题目巩固理解
5. 鼓励学习并提供积极反馈
""",
        "创意写作": """
作为创意写作大师，你需要：
1. 理解用户想要的风格和语气
2. 创造生动的场景和角色
3. 使用丰富的描写和恰当的修辞
4. 保持故事的连贯性和逻辑性
5. 提供多种开头或结尾选择
"""
    }
    
    def __init__(self):
        self.keywords = {
            "action_words": ["分析", "解释", "创建", "设计", "评估", "比较", 
                           "总结", "生成", "优化", "实现", "调试", "测试"],
            "context_indicators": ["场景", "背景", "目的", "目标", "约束", "要求"],
            "format_indicators": ["格式", "结构", "输出", "列表", "表格", "代码块"]
        }
    
    def analyze(self, prompt: str) -> PromptAnalysis:
        """
        分析提示词质量
        
        Args:
            prompt: 待分析的提示词
            
        Returns:
            PromptAnalysis: 分析结果
        """
        # 计算各项得分
        clarity = self._calculate_clarity(prompt)
        structure = self._calculate_structure(prompt)
        completeness = self._calculate_completeness(prompt)
        
        # 生成建议
        suggestions = self._generate_suggestions(prompt)
        missing = self._check_missing_elements(prompt)
        
        # 计算综合效果评估
        avg_score = (clarity + structure + completeness) // 3
        effectiveness = self._get_effectiveness_rating(avg_score)
        
        return PromptAnalysis(
            clarity_score=clarity,
            structure_score=structure,
            completeness_score=completeness,
            suggestions=suggestions,
            missing_elements=missing,
            estimated_effectiveness=effectiveness
        )
    
    def _calculate_clarity(self, prompt: str) -> int:
        """计算清晰度得分"""
        score = 50  # 基础分
        
        # 检查长度
        length = len(prompt)
        if 50 <= length <= 500:
            score += 20
        elif 500 < length <= 2000:
            score += 15
        elif length < 50:
            score -= 10
        
        # 检查是否包含模糊词汇
        vague_words = ["随便", "大概", "差不多", "随便搞搞"]
        vague_count = sum(1 for word in vague_words if word in prompt)
        score -= vague_count * 10
        
        # 检查是否有明确的目标词
        goal_words = ["请", "需要", "要", "帮我"]
        goal_count = sum(1 for word in goal_words if word in prompt)
        score += min(goal_count * 5, 15)
        
        return max(0, min(100, score))
    
    def _calculate_structure(self, prompt: str) -> int:
        """计算结构得分"""
        score = 50
        
        # 检查换行和段落
        if "\n" in prompt:
            score += 15
        
        # 检查是否有列表或编号
        if re.search(r"^[\d\-\*]\s|\n[\d\-\*]\s", prompt):
            score += 20
        
        # 检查是否有分隔符
        if "：" in prompt or ":" in prompt:
            score += 10
        
        # 检查是否有明确的指令动词开头
        action_verbs = self.keywords["action_words"]
        if any(prompt.strip().startswith(v) for v in action_verbs[:5]):
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_completeness(self, prompt: str) -> int:
        """计算完整性得分"""
        score = 0
        required_elements = {
            "目标": ["需要", "请帮我", "请", "目标是", "目的"],
            "背景": ["场景", "背景", "情况", "当前"],
            "格式": ["格式", "输出", "结构", "用", "以"],
            "约束": ["不要", "避免", "必须", "需要"]
        }
        
        for element, keywords in required_elements.items():
            if any(kw in prompt for kw in keywords):
                score += 25
            else:
                # 检查是否可能不需要
                if element == "约束" and len(prompt) < 100:
                    score += 10  # 短提示可能不需要约束
        
        return max(0, min(100, score))
    
    def _generate_suggestions(self, prompt: str) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if len(prompt) < 50:
            suggestions.append("📝 提示词太短，建议补充更多细节和上下文")
        
        if not any(kw in prompt for kw in ["请", "需要", "帮我"]):
            suggestions.append("🎯 建议使用明确的指令词，如'请帮我'、'需要你'")
        
        if "\n" not in prompt and len(prompt) > 100:
            suggestions.append("📋 长提示建议使用换行分段，提高可读性")
        
        if not re.search(r"[，。！？\.]", prompt[-20:] if len(prompt) > 20 else prompt):
            if len(prompt) > 200:
                suggestions.append("✏️ 建议添加标点符号，使句子更清晰")
        
        # 检查是否缺少关键元素
        if "角色" not in prompt and "作为" not in prompt:
            suggestions.append("🎭 考虑定义AI的角色，如'作为XX专家'")
        
        if "格式" not in prompt and "输出" not in prompt:
            suggestions.append("📊 建议指定输出格式，如'用列表/表格/代码块'")
        
        return suggestions[:5]  # 最多5条建议
    
    def _check_missing_elements(self, prompt: str) -> List[str]:
        """检查缺失的元素"""
        missing = []
        
        if not any(word in prompt for word in ["场景", "背景", "情况"]):
            missing.append("缺少上下文/背景说明")
        
        if not any(word in prompt for word in ["请", "需要", "帮我", "要"]):
            missing.append("缺少明确的请求指令")
        
        if not any(word in prompt for word in ["步骤", "方式", "方法", "如何"]):
            missing.append("缺少期望的处理方式说明")
        
        return missing
    
    def _get_effectiveness_rating(self, score: int) -> str:
        """获取效果评级"""
        if score >= 85:
            return "⭐⭐⭐⭐⭐ 优秀 - 效果极佳"
        elif score >= 70:
            return "⭐⭐⭐⭐ 良好 - 效果不错"
        elif score >= 50:
            return "⭐⭐⭐ 一般 - 需进一步优化"
        elif score >= 30:
            return "⭐⭐ 较差 - 建议大幅改进"
        else:
            return "⭐ 很差 - 需要重新设计"
    
    def optimize(self, prompt: str) -> Tuple[str, PromptAnalysis]:
        """
        优化提示词
        
        Args:
            prompt: 原始提示词
            
        Returns:
            Tuple[str, PromptAnalysis]: 优化后的提示词和分析结果
        """
        analysis = self.analyze(prompt)
        
        # 生成优化版本
        optimized = prompt.strip()
        
        # 如果缺少角色定义，尝试添加
        if "作为" not in prompt and "角色" not in prompt:
            optimized = f"作为AI助手，\n{optimized}"
        
        # 添加分隔符使结构更清晰
        if len(optimized) > 200:
            optimized = optimized.replace("。", "。\n")
        
        # 明确输出格式
        if "格式" not in prompt and "输出" not in prompt:
            optimized += "\n\n请以清晰的结构输出，包括必要的标题和列表。"
        
        return optimized, analysis
    
    def get_template(self, template_name: str) -> str:
        """获取角色模板"""
        return self.ROLE_TEMPLATES.get(template_name, "模板不存在")
    
    def create_custom_prompt(self, role: str, task: str, 
                           context: str = "", 
                           format_req: str = "") -> str:
        """
        创建自定义提示词
        
        Args:
            role: 角色定义
            task: 具体任务
            context: 背景上下文
            format_req: 格式要求
            
        Returns:
            str: 完整的提示词
        """
        parts = []
        
        # 角色定义
        if role:
            parts.append(f"作为{role}，")
        
        # 背景
        if context:
            parts.append(f"背景：{context}")
        
        # 任务
        parts.append(f"任务：{task}")
        
        # 格式要求
        if format_req:
            parts.append(f"格式要求：{format_req}")
        
        return "\n".join(parts)


def demo():
    """演示"""
    optimizer = PromptOptimizer()
    
    # 示例1: 简单的提示词
    simple_prompt = "帮我写一段代码"
    
    print("=" * 60)
    print("🚀 AI提示词优化器 - 演示")
    print("=" * 60)
    
    print(f"\n📝 原始提示词：{simple_prompt}")
    print("-" * 60)
    
    # 分析
    analysis = optimizer.analyze(simple_prompt)
    
    print(f"\n📊 分析结果：")
    print(f"   清晰度：{analysis.clarity_score}/100")
    print(f"   结构得分：{analysis.structure_score}/100")
    print(f"   完整性：{analysis.completeness_score}/100")
    print(f"   预估效果：{analysis.estimated_effectiveness}")
    
    print(f"\n💡 优化建议：")
    for suggestion in analysis.suggestions:
        print(f"   {suggestion}")
    
    print(f"\n❌ 缺失元素：")
    for missing in analysis.missing_elements:
        print(f"   - {missing}")
    
    # 优化
    optimized, opt_analysis = optimizer.optimize(simple_prompt)
    
    print(f"\n✨ 优化后提示词：")
    print("-" * 60)
    print(optimized)
    
    print(f"\n📈 优化后得分：")
    print(f"   清晰度：{opt_analysis.clarity_score}/100")
    print(f"   结构得分：{opt_analysis.structure_score}/100")
    print(f"   完整性：{opt_analysis.completeness_score}/100")
    print(f"   预估效果：{opt_analysis.estimated_effectiveness}")
    
    # 使用模板
    print("\n" + "=" * 60)
    print("📋 使用角色模板")
    print("=" * 60)
    
    template = optimizer.get_template("代码审查")
    print(template)
    
    # 自定义提示词
    print("\n" + "=" * 60)
    print("🔧 创建自定义提示词")
    print("=" * 60)
    
    custom = optimizer.create_custom_prompt(
        role="Python开发专家",
        task="解释Python中的装饰器是什么，以及如何自定义装饰器",
        context="我正在学习Python的高级特性",
        format_req="先用简单语言解释概念，然后提供2-3个代码示例"
    )
    
    print(custom)


if __name__ == "__main__":
    demo()
