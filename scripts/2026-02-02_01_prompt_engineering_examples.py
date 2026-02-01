#!/usr/bin/env python3
"""
AI Prompt Engineering Examples - Day 3
展示不同场景下的提示工程技术

主题：结构化输出与Few-Shot提示
"""

from typing import List, Dict
import json


# ============ 1. 结构化输出提示 ============
STRUCTURED_OUTPUT_PROMPT = """
请将以下信息按照JSON格式输出：

输入文本：{text}

要求：
- 使用JSON格式
- 包含字段：summary（摘要）, keywords（关键词数组）, sentiment（情感：positive/negative/neutral）, entities（实体列表）

输出格式：
```json
{{
  "summary": "...",
  "keywords": [...],
  "sentiment": "...",
  "entities": [...]
}}
```
"""


# ============ 2. Few-Shot 学习提示 ============
FEWSHOT_PROMPT = """
根据示例完成任务：

示例1:
输入：我今天学会了Python的列表推导式
标签：#学习 #Python #编程

示例2:
输入：公司项目成功上线，团队都很兴奋
标签：#工作 #成就 #团队

请为以下输入生成标签：
输入：{input_text}

标签：
"""


# ============ 3. 思维链推理提示 ============
COT_PROMPT = """
请逐步推理解答以下问题。

问题：{question}

推理步骤：
1. 理解问题
2. 分析已知信息
3. 逐步推理
4. 得出结论

最终答案：
"""


# ============ 4. 角色扮演提示 ============
ROLEPLAY_PROMPT = """
你是一位经验丰富的软件架构师，名为Alex。

背景：
- 10年软件架构经验
- 擅长微服务设计和分布式系统
- 热爱开源贡献

任务：{task}

请以Alex的身份，用专业且友好的语气回答。
"""


# ============ 5. 自检修正提示 ============
SELF_CORRECT_PROMPT = """
请完成以下任务，然后检查你的答案。

任务：{task}

第一步：提供初始答案
初始答案：...

第二步：反思并检查
- 是否完整回答了问题？
- 是否有遗漏？
- 是否有错误？

第三步：提供最终答案
最终答案：...
"""


def generate_structured_output(text: str) -> str:
    """生成结构化输出提示"""
    return STRUCTURED_OUTPUT_PROMPT.format(text=text)


def generate_fewshot_prompt(input_text: str) -> str:
    """生成Few-Shot提示"""
    return FEWSHOT_PROMPT.format(input_text=input_text)


def generate_cot_prompt(question: str) -> str:
    """生成思维链推理提示"""
    return COT_PROMPT.format(question=question)


def generate_roleplay_prompt(task: str) -> str:
    """生成角色扮演提示"""
    return ROLEPLAY_PROMPT.format(task=task)


def generate_self_correct_prompt(task: str) -> str:
    """生成自检修正提示"""
    return SELF_CORRECT_PROMPT.format(task=task)


def demo():
    """演示各种提示工程技巧"""
    
    print("=" * 50)
    print("AI Prompt Engineering Examples - Day 3")
    print("=" * 50)
    
    # 示例1: 结构化输出
    print("\n【1】结构化输出示例:")
    print(generate_structured_output("今天天气真好，适合去公园散步"))
    
    # 示例2: Few-Shot
    print("\n【2】Few-Shot示例:")
    print(generate_fewshot_prompt("周末读了一本关于AI的好书"))
    
    # 示例3: 思维链
    print("\n【3】思维链推理示例:")
    print(generate_cot_prompt("如果A>B，B>C，那么A和C的关系是什么？"))
    
    # 示例4: 角色扮演
    print("\n【4】角色扮演示例:")
    print(generate_roleplay_prompt("解释一下什么是微服务架构"))
    
    # 示例5: 自检修正
    print("\n【5】自检修正示例:")
    print(generate_self_correct_prompt("用Python写一个快速排序函数"))
    
    print("\n" + "=" * 50)
    print("提示工程技巧总结:")
    print("1. 明确输出格式 → 使用结构化输出")
    print("2. 提供示例 → 使用Few-Shot学习")
    print("3. 要求逐步思考 → 使用思维链推理")
    print("4. 设定角色 → 使用角色扮演")
    print("5. 提高准确性 → 使用自检修正")
    print("=" * 50)


if __name__ == "__main__":
    demo()
