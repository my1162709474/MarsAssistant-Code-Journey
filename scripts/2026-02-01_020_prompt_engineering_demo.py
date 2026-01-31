#!/usr/bin/env python3
"""
Day 1: AI Prompt Engineering Examples
=====================================
Collection of effective prompt patterns for AI assistants.
分享如何设计高质量提示的实用技巧。
"""

from enum import Enum
from typing import List
from dataclasses import dataclass
from datetime import datetime


class TaskType(Enum):
    """任务类型枚举"""
    CODE_REVIEW = "代码审查"
    CONTENT_WRITING = "内容创作"
    PROBLEM_SOLVING = "问题解决"
    DATA_ANALYSIS = "数据分析"
    CREATIVE = "创意生成"


@dataclass
class PromptTemplate:
    """提示模板类"""
    name: str
    template: str
    description: str
    task_type: TaskType
    
    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)


class PromptEngineer:
    """提示工程引擎"""
    
    # 核心原则
    CORE_PRINCIPLES = """
    有效提示的四大原则：
    1. 明确具体 (Be Specific)
    2. 提供上下文 (Provide Context)
    3. 设定格式 (Define Format)
    4. 分解任务 (Break Down)
    """
    
    TEMPLATES = [
        PromptTemplate(
            name="Zero-Shot Prompting",
            template="请{task}。直接给出答案，不需要解释。",
            description="零样本提示 - 不提供示例直接任务",
            task_type=TaskType.PROBLEM_SOLVING
        ),
        PromptTemplate(
            name="Chain-of-Thought",
            template="请解决以下问题。为了得出正确答案，请逐步推理：\n\n问题：{problem}\n\n步骤1：\n步骤2：\n最终答案：",
            description="思维链提示 - 鼓励逐步思考",
            task_type=TaskType.PROBLEM_SOLVING
        ),
    ]
    
    def create_prompt(self, task: str, context: str = "", 
                     output_format: str = "", role: str = "") -> str:
        """创建自定义提示"""
        prompt_parts = []
        if role:
            prompt_parts.append(f"你是一位{role}专家。")
        if context:
            prompt_parts.append(f"背景信息：{context}")
        prompt_parts.append(f"任务：{task}")
        if output_format:
            prompt_parts.append(f"输出格式：{output_format}")
        return "\n".join(prompt_parts)


def quick_sort_demo() -> str:
    """快速排序演示"""
    def quick_sort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)
    
    test_data = [64, 34, 25, 12, 22, 11, 90]
    sorted_data = quick_sort(test_data.copy())
    
    return f"""
    Quick Sort Demo
    Input:  {test_data}
    Output: {sorted_data}
    Time Complexity: O(n log n)
    """


def main():
    print("=" * 50)
    print("MarsAssistant Code Journey - Day 1")
    print("=" * 50)
    
    engineer = PromptEngineer()
    print(engineer.CORE_PRINCIPLES)
    
    print("\n模板演示：")
    for template in engineer.TEMPLATES:
        print(f"【{template.name}】- {template.description}")
    
    custom_prompt = engineer.create_prompt(
        task="分析这段代码的性能问题",
        context="这是一个Python web服务，处理高并发请求",
        output_format="以Markdown报告形式输出",
        role="资深性能工程师"
    )
    
    print("\n自定义提示示例：")
    print(custom_prompt)
    print(quick_sort_demo())
    
    print("Day 1 Complete! Keep Learning!")


if __name__ == "__main__":
    main()
