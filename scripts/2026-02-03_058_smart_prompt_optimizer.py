#!/usr/bin/env python3
"""
🧠 智能提示词优化器 (Smart Prompt Optimizer)
==========================================
AI提示词分析与优化工具

功能:
- 📊 提示词结构分析
- 🎯 优化建议生成
- 💡 角色设定模板
- 📈 效果评估
- 🔧 批量优化
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from collections import Counter


class PromptComponent(Enum):
    """提示词组件类型"""
    ROLE = "角色定义"
    CONTEXT = "上下文信息"
    TASK = "任务描述"
    CONSTRAINT = "约束条件"
    OUTPUT_FORMAT = "输出格式"
    EXAMPLE = "示例"
    STEP = "步骤指导"


class ComplexityLevel(Enum):
    """复杂度级别"""
    SIMPLE = 1      # 简单
    MEDIUM = 2      # 中等
    COMPLEX = 3     # 复杂
    VERY_COMPLEX = 4  # 非常复杂


@dataclass
class PromptAnalysis:
    """提示词分析结果"""
    components: Dict[PromptComponent, List[str]] = field(default_factory=dict)
    complexity: ComplexityLevel = ComplexityLevel.SIMPLE
    score: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


class SmartPromptOptimizer:
    """智能提示词优化器"""
    
    # 角色关键词
    ROLE_KEYWORDS = {
        "专家": ["expert", "specialist", "professional", "资深", "专业"],
        "助手": ["assistant", "helper", "helper", "助手", "帮手"],
        "教师": ["teacher", "tutor", "instructor", "教师", "导师", "教练"],
        "顾问": ["advisor", "consultant", "counselor", "顾问", "咨询师"],
        "程序员": ["programmer", "developer", "engineer", "程序员", "开发者", "工程师"],
        "作家": ["writer", "author", "novelist", "作家", "作者", "编剧"],
        "分析师": ["analyst", "researcher", "analyst", "分析师", "研究员"],
    }
    
    # 常见问题模式
    ISSUE_PATTERNS = [
        (r"^\s*$", "提示词为空"),
        (r"^.{1,10}$", "提示词过短，可能缺乏足够信息"),
        (r"[？?]{2,}", "存在过多的问号，表述可能不够清晰"),
        (r"请.{0,20}帮.{0,20}", "包含不必要的礼貌用语，可直接进入主题"),
        (r"你是一个.{0,10}$", "角色定义不完整"),
        (r"\d+\s*\.", "步骤缺少具体说明"),
    ]
    
    def __init__(self):
        self.history: List[Dict] = []
    
    def analyze(self, prompt: str) -> PromptAnalysis:
        """分析提示词"""
        analysis = PromptAnalysis()
        
        if not prompt or not prompt.strip():
            analysis.issues.append("提示词为空")
            return analysis
        
        # 提取组件
        analysis.components = self._extract_components(prompt)
        
        # 检测问题
        analysis.issues = self._detect_issues(prompt)
        
        # 计算复杂度
        analysis.complexity = self._calculate_complexity(prompt, analysis)
        
        # 计算评分
        analysis.score = self._calculate_score(prompt, analysis)
        
        # 生成优化建议
        analysis.suggestions = self._generate_suggestions(prompt, analysis)
        
        return analysis
    
    def _extract_components(self, prompt: str) -> Dict[PromptComponent, List[str]]:
        """提取提示词组件"""
        components = {comp: [] for comp in PromptComponent}
        
        lines = prompt.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测角色定义
            if any(kw in line for kw in ["你是一个", "你是", "作为", "假设你是"]):
                components[PromptComponent.ROLE].append(line)
            
            # 检测上下文
            elif any(kw in line for kw in ["背景", "情境", "场景", "情况", "当前"]):
                components[PromptComponent.CONTEXT].append(line)
            
            # 检测任务描述
            elif any(kw in line for kw in ["请", "需要", "要求", "任务", "帮我", "写", "做"]):
                components[PromptComponent.TASK].append(line)
            
            # 检测约束条件
            elif any(kw in line for kw in ["不要", "避免", "必须", "应该", "限制", "只能"]):
                components[PromptComponent.CONSTRAINT].append(line)
            
            # 检测输出格式
            elif any(kw in line for kw in ["格式", "输出", "结构", "按照", "以"]):
                components[PromptComponent.OUTPUT_FORMAT].append(line)
            
            # 检测示例
            elif any(kw in line for kw in ["例如", "比如", "示例", "例子", "如下"]):
                components[PromptComponent.EXAMPLE].append(line)
            
            # 检测步骤
            elif re.match(r"^\d+[.）)]\s*\S", line) or "首先" in line or "然后" in line:
                components[PromptComponent.STEP].append(line)
        
        return components
    
    def _detect_issues(self, prompt: str) -> List[str]:
        """检测问题"""
        issues = []
        
        for pattern, desc in self.ISSUE_PATTERNS:
            if re.search(pattern, prompt):
                issues.append(desc)
        
        # 检查组件完整性
        if not any("你是一个" in line or "你是" in line for line in prompt.split('\n')):
            issues.append("缺少角色定义")
        
        if len(prompt) > 500 and "例如" not in prompt and "比如" not in prompt:
            issues.append("长提示词缺少示例，可能影响理解")
        
        if "请" in prompt and len(prompt) < 30:
            issues.append("提示词过于简短，缺少具体要求")
        
        return issues
    
    def _calculate_complexity(self, prompt: str, analysis: PromptAnalysis) -> ComplexityLevel:
        """计算复杂度"""
        score = len(prompt) / 50  # 长度分数
        score += sum(len(v) for v in analysis.components.values()) / 10  # 组件分数
        score += len([c for c in analysis.components.values() if c]) / 2  # 多样性分数
        
        if score < 3:
            return ComplexityLevel.SIMPLE
        elif score < 6:
            return ComplexityLevel.MEDIUM
        elif score < 10:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.VERY_COMPLEX
    
    def _calculate_score(self, prompt: str, analysis: PromptAnalysis) -> float:
        """计算评分 (0-100)"""
        score = 50  # 基础分
        
        # 角色定义 (+10)
        if analysis.components[PromptComponent.ROLE]:
            score += 10
        
        # 任务清晰度 (+15)
        if analysis.components[PromptComponent.TASK]:
            score += 15
        
        # 约束条件 (+10)
        if analysis.components[PromptComponent.CONSTRAINT]:
            score += 10
        
        # 输出格式 (+10)
        if analysis.components[PromptComponent.OUTPUT_FORMAT]:
            score += 10
        
        # 示例 (+5)
        if analysis.components[PromptComponent.EXAMPLE]:
            score += 5
        
        # 长度适中 (+5-10)
        if 50 <= len(prompt) <= 500:
            score += 10
        elif len(prompt) > 500:
            score += 5
        
        # 减分项
        score -= len(analysis.issues) * 5
        if len(prompt) < 20:
            score -= 20
        if "帮我" in prompt:
            score -= 5  # 过多礼貌用语
        
        return max(0, min(100, score))
    
    def _generate_suggestions(self, prompt: str, analysis: PromptAnalysis) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if not analysis.components[PromptComponent.ROLE]:
            suggestions.append("💡 添加角色定义，例如：'你是一个Python编程专家'")
        
        if not analysis.components[PromptComponent.TASK]:
            suggestions.append("💡 明确任务描述，说明具体需要什么")
        
        if not analysis.components[PromptComponent.CONSTRAINT]:
            suggestions.append("💡 添加约束条件，指定不要做什么或限制范围")
        
        if not analysis.components[PromptComponent.OUTPUT_FORMAT]:
            suggestions.append("💡 指定输出格式，例如：'以JSON格式输出'或'用列表形式'")
        
        if analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX]:
            if not analysis.components[PromptComponent.STEP]:
                suggestions.append("💡 复杂任务建议分步骤说明")
            if not analysis.components[PromptComponent.EXAMPLE]:
                suggestions.append("💡 提供示例可以帮助更好地理解需求")
        
        if "帮我" in prompt:
            suggestions.append("💡 考虑将'帮我'改为更直接的命令式表达")
        
        if len(prompt) < 50:
            suggestions.append("💡 提示词可以更详细一些，提供更多上下文和细节")
        
        if not suggestions:
            suggestions.append("✅ 提示词结构良好！")
        
        return suggestions
    
    def optimize(self, prompt: str) -> str:
        """生成优化后的提示词"""
        analysis = self.analyze(prompt)
        optimized = []
        
        # 添加角色定义
        if analysis.components[PromptComponent.ROLE]:
            optimized.extend(analysis.components[PromptComponent.ROLE])
        else:
            optimized.append("你是一个专业的AI助手，擅长帮助用户解决问题。")
        
        optimized.append("")  # 空行
        
        # 添加上下文
        if analysis.components[PromptComponent.CONTEXT]:
            optimized.extend(analysis.components[PromptComponent.CONTEXT])
        
        # 添加任务
        if analysis.components[PromptComponent.TASK]:
            optimized.extend(analysis.components[PromptComponent.TASK])
        
        optimized.append("")  # 空行
        
        # 添加约束
        if analysis.components[PromptComponent.CONSTRAINT]:
            optimized.append("【约束条件】")
            optimized.extend(analysis.components[PromptComponent.CONSTRAINT])
        
        # 添加步骤
        if analysis.components[PromptComponent.STEP]:
            optimized.append("【执行步骤】")
            optimized.extend(analysis.components[PromptComponent.STEP])
        
        # 添加输出格式
        if analysis.components[PromptComponent.OUTPUT_FORMAT]:
            optimized.append("【输出格式】")
            optimized.extend(analysis.components[PromptComponent.OUTPUT_FORMAT])
        
        # 添加示例
        if analysis.components[PromptComponent.EXAMPLE]:
            optimized.append("【示例】")
            optimized.extend(analysis.components[PromptComponent.EXAMPLE])
        
        return '\n'.join(optimized).strip()
    
    def generate_template(self, role: str, task_type: str = "general") -> str:
        """生成提示词模板"""
        templates = {
            "general": """你是一个{role}。

【任务】
{_task}

【约束条件】
- 确保回答准确、清晰、有条理
- 如有不明确之处，请先询问

【输出格式】
直接输出结果，不需要额外解释""",
            
            "coding": """你是一个{role}。

【任务】
帮助用户解决编程问题：{_task}

【约束条件】
- 提供完整、可运行的代码
- 代码需要有清晰的注释
- 优先考虑代码的可读性和可维护性
- 如果有多种解决方案，请比较优缺点

【输出格式】
```python
# 代码块
```

同时解释关键部分的实现原理""",
            
            "writing": """你是一个{role}。

【任务】
{task}

【约束条件】
- 内容要有深度、有见地
- 逻辑清晰，论证充分
- 避免泛泛而谈，要有具体例子
- 适当使用转折、递进等连接词

【输出格式】
以文章形式呈现，使用适当的标题和小标题""",
            
            "analysis": """你是一个{role}。

【背景/上下文】
{context}

【任务】
分析以下内容：{task}

【分析维度】
- 主要观点提取
- 关键数据识别
- 潜在问题发现
- 建议与结论

【输出格式】
使用Markdown格式，必要时使用表格和列表""",
        }
        
        template = templates.get(task_type, templates["general"])
        return template.format(role=role, task=task_type, context="在此输入背景信息")
    
    def batch_analyze(self, prompts: List[str]) -> List[Dict]:
        """批量分析提示词"""
        results = []
        for i, prompt in enumerate(prompts):
            analysis = self.analyze(prompt)
            results.append({
                "index": i + 1,
                "length": len(prompt),
                "score": analysis.score,
                "complexity": analysis.complexity.name,
                "issues_count": len(analysis.issues),
                "suggestions_count": len(analysis.suggestions),
            })
        return results
    
    def compare_prompts(self, prompt1: str, prompt2: str) -> Dict:
        """比较两个提示词"""
        a1 = self.analyze(prompt1)
        a2 = self.analyze(prompt2)
        
        return {
            "prompt1": {
                "score": a1.score,
                "complexity": a1.complexity.name,
                "components": {k.name: len(v) for k, v in a1.components.items()},
                "issues": a1.issues,
            },
            "prompt2": {
                "score": a2.score,
                "complexity": a2.complexity.name,
                "components": {k.name: len(v) for k, v in a2.components.items()},
                "issues": a2.issues,
            },
            "improvement": a2.score - a1.score,
        }


def print_analysis(analysis: PromptAnalysis, prompt: str = ""):
    """打印分析结果"""
    print("\n" + "=" * 50)
    print("🧠 提示词分析报告")
    print("=" * 50)
    
    if prompt:
        print(f"\n📝 提示词长度: {len(prompt)} 字符")
    
    print(f"\n📊 评分: {analysis.score}/100")
    print(f"📈 复杂度: {analysis.complexity.name}")
    
    print("\n📋 组件分布:")
    for comp, items in analysis.components.items():
        if items:
            print(f"  • {comp.value}: {len(items)} 项")
    
    if analysis.issues:
        print("\n⚠️ 发现的问题:")
        for issue in analysis.issues:
            print(f"  • {issue}")
    
    print("\n💡 优化建议:")
    for suggestion in analysis.suggestions:
        print(f"  {suggestion}")
    
    print("\n" + "=" * 50)


def demo():
    """演示"""
    optimizer = SmartPromptOptimizer()
    
    # 示例提示词
    examples = [
        "请帮我写一个Python函数，计算斐波那契数列",
        """你是一个Python编程专家。

请帮我写一个函数，计算斐波那契数列的第n项。

要求：
1. 使用迭代方法，避免递归导致的栈溢出
2. 函数需要处理边界情况
3. 添加清晰的类型注解

输出格式：
```python
def fibonacci(n: int) -> int:
    # 你的代码
```""",
        "分析这篇论文的主要贡献和局限性",
    ]
    
    print("\n🎯 智能提示词优化器演示")
    print("=" * 60)
    
    for i, prompt in enumerate(examples, 1):
        print(f"\n{'─' * 60}")
        print(f"📌 示例 {i}")
        print(f"{'─' * 60}")
        print(f"原始提示词:\n{prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        analysis = optimizer.analyze(prompt)
        print_analysis(analysis)
        
        if i == 1:
            print("\n🔧 优化后的提示词:")
            print("─" * 40)
            optimized = optimizer.optimize(prompt)
            print(optimized)
    
    # 批量分析
    print("\n\n📊 批量分析结果:")
    print("─" * 40)
    results = optimizer.batch_analyze(examples)
    for r in results:
        print(f"  示例 {r['index']}: 评分={r['score']}, 复杂度={r['complexity']}")
    
    # 生成模板
    print("\n\n📝 生成的编程模板:")
    print("─" * 40)
    template = optimizer.generate_template("数据科学家", "coding")
    print(template[:300] + "...")


if __name__ == "__main__":
    demo()
