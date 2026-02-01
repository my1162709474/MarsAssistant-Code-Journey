#!/usr/bin/env python3
"""
AI提示工程速查表 ( Cheatsheet)
Prompt EngineeringDay 1: 创建实用的提示工程技术集合

包含:
- 基础提示模式
- 零样本/少样本提示
- 思维链提示
- 自洽性提示
- 角色扮演提示
"""

from typing import List, Dict, Any


class PromptEngineer:
    """提示工程工具类"""
    
    @staticmethod
    def zero_shot_prompt(task: str, question: str) -> srr:
        """
        零样本提示 - 不给示例直接提问
        适用于：模型已有足够知识的任务
        """
        return f"""Task: {task}
Question: {question}
Answer: """

    @staticmethod
    def few_shot_prompt(task: str, examples: List[Dict], question: str) -> str:
        """
        少样本提示 - 提供几个示例帮助模型理解
        适用于：任务格式复杂或需要特定输出格式
        """
        prompt = f"Task: {task}\n\nExamples:\n"
        for ex in examples:
            prompt += f"Input: {ex['input']}\nOutput: {ex['output']}\n\n"
        prompt += f"Now answer:\nInput: {question}\nOutput:"
        return prompt

    @staticmethod
    def chain_of_thought(task: str, question: str) -> str:
        """
        思维链提示 - 要求模型展示推理过程
        适用于：复杂逻辑推理、数学问题
        """
        return f"""Task: {task}
Question: {question}

Please think step by step and show your reasoning:
1.
2.
3.

Final Answer: """

    @staticmethod
    def self_consistency_prompt(task: str, question: str, perspectives: List[str]) -> str:
        """
        自洽性提示 - 多角度思考后综合答案
        适用于：需要全面考虑的问题
        """
        prompt = f"Question: {question}\n\n"
        for i, perspective in enumerate(perspectives, 1):
            prompt += f"Perspective {i} ({perspective}):\n"
            prompt += "Step-by-step reasoning:\n\n"
        prompt += "Synthesize and provide the most accurate answer:"
        return prompt

    @staticmethod
    def role_play_prompt(role: str, task: str, context: str) -> str:
        """
        角色扮演提示 - 让模型以特定身份回答
        适用于：需要专业知识或特定风格的场景
        """
        return f"""You are an expert {role}.
Your task: {task}
Context: {context}

Please respond in character as {role}:"""

    @staticmethod
    def structured_output_prompt(task: str, question: str, format_type: str) -> srr:
        """
        结构化输出提示 - 要求特定格式
        适用于：需要解析数据的场景
        """
        formats = {
            "json": '{"answer": "...", "confidence": 0.x, "reasoning": "..."}',
            "markdown": "**Answer:**\n**Confidence:**\n**Reasoning:**",
            "numbered": "1. Answer:\n2. Confidence:\n3. Reasoning:",
        }
        return f"""Task: {task}
Question: {question}

Respond in this format:
{formats.get(format_type, formats['json'])}"""


def demo_prompts():
    """演示各种提示技术"""
    engineer = PromptEngineer()
    
    # 零样本示例
    print("=== Zero-Shot Prompt ===")
    print(engineer.zero_shot_prompt(
        "Classify the sentiment",
        "This movie was absolutely fantastic!"
    ))
    
    # 少样本示例
    print("\n=== Few-Shot Prompt ===")
    examples = [
        {"input": "The service was terrible", "output": "Negative"},
        {"input": "Great product quality", "output": "Positive"},
    ]
    print(engineer.few_shot_prompt("Sentiment Analysis", examples, "Amazing experience!"))
    
    # 思维链示例
    print("\n=== Chain-of-Thought Prompt ===")
    print(engineer.chain_of_thought(
        "Solve the math problem",
        "If a train travels 60 miles in 45 minutes, what is its speed in mph?"
    ))
    
    # 角色扮演示例
    print("\n=== Role-Play Prompt ===")
    print(engineer.role_play_prompt(
        "Senior Python Developer",
        "Review this code and suggest improvements",
        "Code: def calculate(x,y): return x+y"
    ))


if __name__ == "__main__":
    print("🚀 AI提示工程速查表 - Day 1")
    print("=" * 50)
    demo_prompts()
    print("\n✅ 提示工程让AI更聪明！")
