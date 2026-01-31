"""
AI Prompt Optimizer - 提示词优化工具
帮助优化和评估AI提示词的质量
"""

import re
from typing import Dict, List


class PromptOptimizer:
    """AI提示词优化器"""
    
    def __init__(self):
        self.quality_indicators = {
            "specificity": 0.3,
            "context": 0.2,
            "format": 0.15,
            "constraints": 0.15,
            "examples": 0.2
        }
    
    def analyze(self, prompt: str) -> Dict:
        """分析提示词质量"""
        result = {"score": 0, "suggestions": [], "strengths": [], "weaknesses": []}
        
        specificity_score = self._check_specificity(prompt)
        context_score = self._check_context(prompt)
        format_score = self._check_format(prompt)
        constraint_score = self._check_constraints(prompt)
        example_score = self._check_examples(prompt)
        
        result["score"] = round((
            specificity_score * self.quality_indicators["specificity"] +
            context_score * self.quality_indicators["context"] +
            format_score * self.quality_indicators["format"] +
            constraint_score * self.quality_indicators["constraints"] +
            example_score * self.quality_indicators["examples"]
        ) * 100, 1)
        
        result["suggestions"] = self._generate_suggestions(
            specificity_score, context_score, format_score, constraint_score, example_score)
        
        result["strengths"] = self._identify_strengths(
            specificity_score, context_score, format_score, constraint_score, example_score)
        result["weaknesses"] = self._identify_weaknesses(
            specificity_score, context_score, format_score, constraint_score, example_score)
        
        return result
    
    def _check_specificity(self, prompt: str) -> float:
        """检查具体性"""
        score = 0.5
        if re.search(r'\d+', prompt): score += 0.15
        if re.search(r'(具体|明确|详细)', prompt): score += 0.15
        vague_words = ['一些', '大概', '可能', '随便']
        score -= sum(0.1 for word in vague_words if word in prompt)
        return max(0, min(1, score))
    
    def _check_context(self, prompt: str) -> float:
        """检查上下文"""
        score = 0.3
        if any(i in prompt for i in ['背景', '场景', '前提']): score += 0.4
        if any(i in prompt for i in ['为了', '目的是']): score += 0.3
        return max(0, min(1, score))
    
    def _check_format(self, prompt: str) -> float:
        """检查格式"""
        score = 0.4
        if any(k in prompt for k in ['格式', '结构', 'JSON', 'Markdown']): score += 0.3
        if any(k in prompt for k in ['第一步', '首先', '然后']): score += 0.3
        return max(0, min(1, score))
    
    def _check_constraints(self, prompt: str) -> float:
        """检查约束"""
        score = 0.4
        if any(w in prompt for w in ['不要', '避免', '必须', '限制']): score += 0.3
        if re.search(r'(少于|不超过|最多)\s*\d+', prompt): score += 0.3
        return max(0, min(1, score))
    
    def _check_examples(self, prompt: str) -> float:
        """检查示例"""
        score = 0.3
        if any(i in prompt for i in ['例如', '比如', '示例', '例子']): score += 0.4
        return max(0, min(1, score))
    
    def _generate_suggestions(self, spec: float, ctx: float, fmt: float, cons: float, ex: float) -> List[str]:
        suggestions = []
        if spec < 0.5: suggestions.append("添加更具体的描述")
        if ctx < 0.5: suggestions.append("提供更多背景信息")
        if fmt < 0.5: suggestions.append("明确输出格式")
        if cons < 0.5: suggestions.append("添加约束条件")
        if ex < 0.5: suggestions.append("提供示例")
        return suggestions
    
    def _identify_strengths(self, spec: float, ctx: float, fmt: float, cons: float, ex: float) -> List[str]:
        strengths = []
        if spec >= 0.6: strengths.append("具体性强")
        if ctx >= 0.6: strengths.append("上下文清晰")
        if fmt >= 0.6: strengths.append("格式明确")
        return strengths
    
    def _identify_weaknesses(self, spec: float, ctx: float, fmt: float, cons: float, ex: float) -> List[str]:
        weaknesses = []
        if spec < 0.5: weaknesses.append("缺乏具体性")
        if ctx < 0.5: weaknesses.append("缺少上下文")
        return weaknesses
    
    def optimize(self, prompt: str) -> str:
        """优化提示词"""
        optimized = prompt
        if "背景" not in optimized:
            optimized = f"【背景】\n\n{optimized}\n\n"
        optimized += "\n\n【输出格式】请用清晰的结构化格式回答"
        optimized += "\n\n【约束】请简洁明了，直接回答问题"
        return optimized


def demo():
    optimizer = PromptOptimizer()
    test_prompts = ["写代码", "用Python写函数处理列表数据，输出JSON"]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n测试 {i}: {prompt}")
        result = optimizer.analyze(prompt)
        print(f"评分: {result['score']}/100")


if __name__ == "__main__":
    demo()
