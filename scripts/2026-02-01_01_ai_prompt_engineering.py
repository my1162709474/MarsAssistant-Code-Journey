#!/usr/bin/env python3
"""
AI Prompt Engineering Examples
展示不同场景下的有效提示词设计

Author: MarsAssistant
Date: 2026-02-01
"""

from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


class PromptType(Enum):
    """提示词类型枚举"""
    SYSTEM = "system"
    USER = "user"
    FEWSHOT = "fewshot"
    CHAIN_OF_THOUGHT = "cot"
    SELF_CONSISTENCY = "self_consistency"


@dataclass
class PromptExample:
    """提示词示例"""
    name: str
    prompt_type: PromptType
    description: str
    template: str
    use_case: str


class PromptEngineer:
    """
    AI提示工程师类
    
    帮助设计、优化和管理AI提示词
    """
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.examples: List[PromptExample] = []
        
    def add_example(self, example: PromptExample):
        """添加提示词示例"""
        self.examples.append(example)
    
    def create_system_prompt(self, role: str, constraints: List[str]) -> str:
        """
        创建系统提示词
        
        Args:
            role: AI角色描述
            constraints: 约束条件列表
            
        Returns:
            完整的系统提示词
        """
        prompt = f"""你是 {role}。

约束条件:
{chr(10).join(f'- {c}' for c in constraints)}

请始终遵循上述约束。"""
        return prompt
    
    def create_fewshot_prompt(
        self, 
        task: str, 
        examples: List[Dict[str, str]], 
        query: str
    ) -> str:
        """
        创建Few-shot提示词
        
        Args:
            task: 任务描述
            examples: 示例列表，包含input和output
            query: 用户查询
            
        Returns:
            Few-shot提示词
        """
        prompt = f"""任务: {task}

示例:
"""
        for i, ex in enumerate(examples, 1):
            prompt += f"\n示例{i}:\n输入: {ex['input']}\n输出: {ex['output']}\n"
        
        prompt += f"\n现在请回答:\n输入: {query}\n输出:"
        return prompt
    
    def create_cot_prompt(self, question: str) -> str:
        """
        创建Chain-of-Thought提示词
        
        引导AI进行逐步推理
        """
        return f"""请逐步推理并回答以下问题。

问题: {question}

请按以下格式回答:
1. 分析问题...
2. 列出关键信息...
3. 逐步推理...
4. 得出结论...
5. 最终答案: [答案]

开始推理:"""
    
    def optimize_prompt(self, prompt: str, feedback: str) -> str:
        """
        根据反馈优化提示词
        
        Args:
            prompt: 原始提示词
            feedback: 改进反馈
            
        Returns:
            优化后的提示词
        """
        optimization_template = """
请优化以下AI提示词，使其更加有效。

原始提示词:
{prompt}

用户反馈/问题:
{feedback}

请提供优化后的版本，并说明优化点。
优化后的提示词:
"""
        return optimization_template.format(prompt=prompt, feedback=feedback)
    
    def evaluate_prompt_quality(self, prompt: str) -> Dict[str, float]:
        """
        评估提示词质量
        
        Returns:
            质量评分字典
        """
        scores = {
            "clarity": 0.0,      # 清晰度
            "specificity": 0.0,  # 具体性
            "completeness": 0.0, # 完整性
            "constraint": 0.0    # 约束力
        }
        
        # 简单的启发式评估
        if len(prompt) > 50:
            scores["completeness"] = min(1.0, len(prompt) / 500)
        
        if "请" in prompt or "必须" in prompt:
            scores["constraint"] = 0.7
        
        if "例如" in prompt or "比如" in prompt:
            scores["specificity"] = 0.6
        
        if "你是一个" in prompt or "你是" in prompt:
            scores["clarity"] = 0.8
        
        return scores


def demo():
    """演示提示词工程的各种技巧"""
    
    engineer = PromptEngineer()
    
    # 1. 系统提示词示例
    sys_prompt = engineer.create_system_prompt(
        role="专业Python导师",
        constraints=[
            "用简单易懂的语言解释概念",
            "提供实际代码示例",
            "鼓励学习者提问",
            "每次只解释一个新概念"
        ]
    )
    print("=" * 50)
    print("系统提示词示例:")
    print("=" * 50)
    print(sys_prompt)
    
    # 2. Few-shot示例
    fewshot_prompt = engineer.create_fewshot_prompt(
        task="将英文翻译成中文",
        examples=[
            {"input": "Hello, world!", "output": "你好，世界！"},
            {"input": "How are you?", "output": "你好吗？"},
        ],
        query: "Good morning!"
    )
    print("\n" + "=" * 50)
    print("Few-shot提示词示例:")
    print("=" * 50)
    print(fewshot_prompt)
    
    # 3. Chain-of-Thought示例
    cot_prompt = engineer.create_cot_prompt(
        question="如果一个箱子可以装12个苹果，现在有5个箱子，请问一共可以装多少个苹果？"
    )
    print("\n" + "=" * 50)
    print("Chain-of-Thought提示词示例:")
    print("=" * 50)
    print(cot_prompt)
    
    # 4. 评估提示词质量
    scores = engineer.evaluate_prompt_quality(sys_prompt)
    print("\n" + "=" * 50)
    print("提示词质量评估:")
    print("=" * 50)
    for metric, score in scores.items():
        print(f"{metric}: {'█' * int(score * 10)}{'░' * (10 - int(score * 10))} {score:.2f}")


if __name__ == "__main__":
    demo()
