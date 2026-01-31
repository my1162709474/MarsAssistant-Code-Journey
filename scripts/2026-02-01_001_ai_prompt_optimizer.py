#!/usr/bin/env python3
"""
AI Prompt Optimizer - 提示词优化工具
一个帮助优化 AI 提示词的实用工具

功能：
1. 分析提示词结构
2. 提供优化建议
3. 生成多种风格的提示词变体
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class PromptOptimizer:
    """AI 提示词优化器"""
    
    def __init__(self):
        self.weaknesses = [
            "模糊不清的目标",
            "缺少上下文信息",
            "缺少输出格式指定",
            "缺少约束条件",
            "角色定义不清晰",
        ]
    
    def analyze(self, prompt: str) -> Dict:
        """分析提示词并返回优化建议"""
        issues = []
        score = 100
        
        if len(prompt) < 20:
            issues.append("提示词过短，建议增加详细描述")
            score -= 10
        
        if not any(word in prompt.lower() for word in ["你", "请", "帮助", "任务"]):
            issues.append("缺少明确的指令词")
            score -= 15
        
        if "?" not in prompt and "？" not in prompt:
            issues.append("缺少明确的提问或请求")
            score -= 10
        
        # 检查是否指定了输出格式
        format_keywords = ["格式", "输出", "json", "列表", "表格", "markdown"]
        if not any(kw in prompt.lower() for kw in format_keywords):
            issues.append("未指定输出格式，建议明确说明")
            score -= 15
        
        # 检查是否定义了角色
        role_keywords = ["角色", "身份", "专家", "助手", "作为"]
        if not any(kw in prompt.lower() for kw in role_keywords):
            issues.append("未定义角色，建议指定 AI 的身份")
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "length": len(prompt),
            "word_count": len(prompt.split()),
            "suggestion": self._generate_suggestion(issues)
        }
    
    def _generate_suggestion(self, issues: List[str]) -> str:
        """生成优化建议"""
        if not issues:
            return "✅ 提示词结构良好！"
        
        base = "💡 优化建议：\n"
        for i, issue in enumerate(issues, 1):
            base += f"{i}. {issue}\n"
        return base
    
    def optimize(self, prompt: str, role: str = "专业助手") -> str:
        """生成优化后的提示词"""
        analysis = self.analyze(prompt)
        
        optimized = f"""【角色】
你是一个{role}，在相关领域拥有丰富的专业知识和实践经验。

【任务】
{prompt}

【要求】
1. 请仔细理解任务需求，提供准确、有帮助的回答
2. 如果信息不完整，请主动询问
3. 回答要逻辑清晰、重点突出

【输出格式】
请使用清晰的格式组织回答，适当使用列表、加粗等markdown语法。

【约束】
- 保持专业性和准确性
- 提供具体可操作的建议
- 回答要简洁明了"""
        
        return optimized
    
    def generate_variants(self, prompt: str) -> Dict[str, str]:
        """生成多种风格的提示词变体"""
        return {
            "简洁版": f"请{prompt}。简要说明。",
            "详细版": f"请详细描述如何{prompt}，包括步骤、注意事项和示例。",
            "问答版": f"关于{prompt}，请回答以下问题：1. 是什么？2. 为什么？3. 如何做？",
            "教学版": f"请以教学的方式解释{prompt}，让初学者也能理解。",
        }


def main():
    """主函数 - 演示用法"""
    optimizer = PromptOptimizer()
    
    # 示例提示词
    sample_prompts = [
        "写一篇关于AI的文章",
        "帮我提高编程效率",
        "解释什么是机器学习",
    ]
    
    print("🤖 AI Prompt Optimizer - 提示词优化工具")
    print("=" * 50)
    
    for i, prompt in enumerate(sample_prompts, 1):
        print(f"\n📝 示例 {i}: {prompt}")
        print("-" * 30)
        
        analysis = optimizer.analyze(prompt)
        print(f"得分: {analysis['score']}/100")
        print(f"词数: {analysis['word_count']}")
        print(analysis['suggestion'])
        
        print("\n✨ 优化后:")
        optimized = optimizer.optimize(prompt, "AI写作专家")
        print(optimized[:200] + "..." if len(optimized) > 200 else optimized)


if __name__ == "__main__":
    main()
