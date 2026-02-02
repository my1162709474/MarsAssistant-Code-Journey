#!/usr/bin/env python3
"""
Day 31: AI风格对话生成器
AI Persona Dialogue Generator

这个工具可以模拟不同AI助手的对话风格，
生成有趣的对话内容。用于学习prompt engineering
和理解不同AI的回应特点。

支持的人格：
- ChatGPT: 友好、详尽、有帮助
- Claude: 深思熟虑、优雅、有深度
- Gemini: 简洁、聪明、多才多艺
- DeepSeek: 务实、直接、技术性强
- Sardaukar: 冷静、精确、高效

使用方法:
    python ai_dialogue_generator.py --persona claude --topic "时间管理的意义"
    python ai_dialogue_generator.py --persona chatgpt --topic "如何学习编程"
    python ai_dialogue_generator.py --interactive
"""

import argparse
import json
import random
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Persona(Enum):
    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    SARDAUKAR = "sardaukar"


@dataclass
class PersonaConfig:
    name: str
    greeting: str
    style_keywords: list[str]
    response_length: str
    emoji_use: str
    formality: str
    creativity: str


# Persona configurations
PERSONAS = {
    Persona.CHATGPT: PersonaConfig(
        name="ChatGPT",
        greeting="你好！很高兴见到你 😊",
        style_keywords=["当然！", "让我来帮你", "这是一个很好的问题", "总的来说"],
        response_length="中等偏长",
        emoji_use="适量",
        formality="友好",
        creativity="高"
    ),
    Persona.CLAUDE: PersonaConfig(
        name="Claude",
        greeting="你好。有什么我可以帮助你的吗？",
        style_keywords=["我理解", "这很有趣", "从哲学角度来说", "让我思考一下"],
        response_length="详细",
        emoji_use="很少",
        formality="优雅",
        creativity="高"
    ),
    Persona.GEMINI: PersonaConfig(
        name="Gemini",
        greeting="嘿！准备好了吗？🚀",
        style_keywords=["很简单", "让我想想", "好消息是", "真相是"],
        response_length="简洁",
        emoji_use="经常",
        formality=" casual",
        creativity="很高"
    ),
    Persona.DEEPSEEK: PersonaConfig(
        name="DeepSeek",
        greeting="有什么技术问题吗？",
        style_keywords=["本质上", "从技术角度看", "这个问题", "直接来说"],
        response_length="直接",
        emoji_use="无",
        formality="专业",
        creativity="务实"
    ),
    Persona.SARDAUKAR: PersonaConfig(
        name="Sardaukar",
        greeting="指令已接收。",
        style_keywords=["执行", "目标", "效率", "优化"],
        response_length="精简",
        emoji_use="无",
        formality="正式",
        creativity="精确"
    )
}


# Topic-specific responses
TOPIC_RESPONSES = {
    "时间管理": {
        "chatgpt": "时间管理是一门艺术，关键在于优先级和规划。我建议使用'艾森豪威尔矩阵'，将任务按重要性和紧急性分类...",
        "claude": "时间管理的本质不在于管理时间，而在于管理注意力和能量。了解自己的生物节奏，选择最适合的时段处理最困难的任务...",
        "gemini": "番茄工作法！🍅 25分钟专注 + 5分钟休息，简单有效！",
        "deepseek": "GTD (Getting Things Done) 方法论：收集 -> 整理 -> 组织 -> 回顾 -> 执行。",
        "sardaukar": "目标：效率最大化。行动：1. 识别关键路径 2. 消除浪费 3. 持续优化。"
    },
    "学习编程": {
        "chatgpt": "学习编程最重要的是动手实践！不要只看教程，要跟着写代码。建议从Python开始，因为它语法简洁...",
        "claude": "编程本质上是一种思维方式的学习。选择一门语言，深入理解其设计哲学，然后通过项目来巩固知识...",
        "gemini": "从做一个有趣的小项目开始吧！🎮 游戏、工具、什么都行！边做边学最有效！",
        "deepseek": "建议路径：基础语法 -> 数据结构与算法 -> 实际项目 -> 深入源码。每日编码至少2小时。",
        "sardaukar": "执行学习协议。推荐资源：LeetCode + GitHub项目 + 官方文档。进度每日追踪。"
    },
    "AI的未来": {
        "chatgpt": "AI的发展前景令人兴奋！我们可能会看到更多专业化AI助手，同时AI伦理和安全也会越来越重要...",
        "claude": "AI与人类的关系是一个深刻的话题。关键在于找到协作而非替代的平衡点，让AI增强人类能力...",
        "gemini": "太激动了！ 🤖 想象一下：AI医生、AI教师、AI艺术家...未来无限可能！",
        "deepseek": "技术趋势：多模态模型、边缘AI、AI Agents。商业价值：自动化、知识工作、增强决策。",
        "sardaukar": "预测：AGI将在10-20年内实现。当前重点：提升模型效率、增强安全对齐、扩展应用场景。"
    },
    "生活的意义": {
        "chatgpt": "这是一个永恒的哲学问题。维克多·弗兰克尔说过：'生命的意义在于找到你的天赋，生活的意义在于献身于它。'...",
        "claude": "也许意义不在于找到答案，而在于提出正确的问题。每一个认真生活的人都在用自己的方式书写答案...",
        "gemini": "开心就好！✨ 做让自己充满热情的事，和爱的人在一起，这就是意义呀！",
        "deepseek": "从存在主义角度：意义是主观建构的。建议：设定目标、建立连接、持续成长。",
        "sardaukar": "任务：1. 定义个人使命 2. 识别核心价值 3. 制定执行计划 4. 实现自我超越。"
    }
}


def generate_dialogue(persona: Persona, topic: str, num_turns: int = 3) -> list[dict]:
    """生成AI风格对话"""
    config = PERSONAS[persona]
    dialogue = []

    # User message
    user_msg = f"关于{topic}，你能告诉我什么？"
    dialogue.append({"role": "user", "content": user_msg})

    # AI response based on topic
    topic_responses = TOPIC_RESPONSES.get(topic, {
        "chatgpt": f"关于{topic}，这是一个很有意思的话题。让我来详细分析一下...",
        "claude": f"关于{topic}，我想从几个角度来探讨...",
        "gemini": f"{topic}？这个话题太棒了！让我告诉你一些有趣的点子！✨",
        "deepseek": f"分析{topic}：关键要素包括... 技术实现路径是...",
        "sardaukar": f"关于{topic}的指令：定义 -> 分析 -> 执行 -> 优化。"
    })

    ai_response = topic_responses.get(persona.value, topic_responses["chatgpt"])
    dialogue.append({"role": "assistant", "content": ai_response, "persona": config.name})

    # Generate follow-up questions and responses
    followups = [
        "能举个例子吗？",
        "那具体该怎么做呢？",
        "有什么需要注意的吗？"
    ]

    for i in range(num_turns - 1):
        user_msg = random.choice(followups)
        dialogue.append({"role": "user", "content": user_msg})

        # Generate contextual response
        response_templates = {
            "chatgpt": f"当然！{random.choice(['让我给你举几个例子', '这是一个很好的追问', '让我详细解释一下'])}...",
            "claude": f"关于这一点，{random.choice(['我建议你思考一下', '可以从这个角度理解', '这里有一个值得注意的细节'])}...",
            "gemini": f"好问题！🌟 {random.choice(['来看这个', '举个例子', '告诉你一个小技巧'])}...",
            "deepseek": f"补充说明：{random.choice(['技术细节如下', '具体步骤是', '需要注意以下几点'])}...",
            "sardaukar": f"指令确认。{random.choice(['执行细化', '补充信息', '注意事项'])}。"
        }

        ai_response = response_templates[persona.value]
        dialogue.append({"role": "assistant", "content": ai_response, "persona": config.name})

    return dialogue


def print_dialogue(dialogue: list[dict]):
    """打印格式化的对话"""
    print("\n" + "="*60)
    print("🤖 AI PERSONA DIALOGUE GENERATOR")
    print("="*60 + "\n")

    for msg in dialogue:
        role = msg["role"].upper()
        content = msg["content"]
        persona = msg.get("persona", "AI")

        if role == "USER":
            print(f"👤 YOU: {content}\n")
        else:
            print(f"🤖 {persona}: {content}\n")
            print("-" * 40 + "\n")


def export_dialogue(dialogue: list[dict], format: str = "markdown") -> str:
    """导出对话为不同格式"""
    if format == "json":
        return json.dumps(dialogue, ensure_ascii=False, indent=2)
    elif format == "markdown":
        md = "# AI Persona Dialogue\n\n"
        for msg in dialogue:
            role = "**User**" if msg["role"] == "user" else f"**{msg.get('persona', 'AI')}**"
            md += f"### {role}\n{msg['content']}\n\n"
        return md
    else:
        return str(dialogue)


def interactive_mode():
    """交互模式"""
    print("\n🎭 AI Persona Dialogue Generator - Interactive Mode")
    print("-" * 50)

    # Select persona
    print("\n选择AI人格:")
    for i, p in enumerate(Persona, 1):
        config = PERSONAS[p]
        print(f"{i}. {config.name} - {config.formality}, {config.response_length}")

    choice = input("\n请选择 (1-5): ").strip()
    try:
        persona = list(Persona)[int(choice) - 1]
    except (ValueError, IndexError):
        persona = Persona.CHATGPT

    # Select or enter topic
    print("\n预设话题:")
    topics = list(TOPIC_RESPONSES.keys())
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")

    print(f"{len(topics) + 1}. 自定义话题")
    choice = input("\n请选择: ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(topics):
        topic = topics[int(choice) - 1]
    else:
        topic = input("请输入你的话题: ").strip() or "一般问题"

    # Generate dialogue
    dialogue = generate_dialogue(persona, topic)
    print_dialogue(dialogue)

    # Export option
    export = input("导出为JSON? (y/n): ").strip().lower()
    if export == "y":
        print("\n📄 JSON输出:")
        print(export_dialogue(dialogue, "json"))

    export = input("导出为Markdown? (y/n): ").strip().lower()
    if export == "y":
        print("\n📝 Markdown输出:")
        print(export_dialogue(dialogue, "markdown"))


def main():
    parser = argparse.ArgumentParser(
        description="AI Persona Dialogue Generator - 生成不同AI风格的对话",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python ai_dialogue_generator.py --persona claude --topic "时间管理"
    python ai_dialogue_generator.py --persona chatgpt --topic "AI的未来" --turns 5
    python ai_dialogue_generator.py --interactive
    python ai_dialogue_generator.py --list-personas
        """
    )

    parser.add_argument(
        "--persona", "-p",
        type=str,
        choices=[p.value for p in Persona],
        default="chatgpt",
        help="选择AI人格 (默认: chatgpt)"
    )

    parser.add_argument(
        "--topic", "-t",
        type=str,
        default="一般问题",
        help="对话话题"
    )

    parser.add_argument(
        "--turns", "-n",
        type=int,
        default=3,
        help="对话轮数 (默认: 3)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="启动交互模式"
    )

    parser.add_argument(
        "--list-personas", "-l",
        action="store_true",
        help="列出所有可用的人格"
    )

    parser.add_argument(
        "--export", "-e",
        type=str,
        choices=["json", "markdown"],
        help="导出对话格式"
    )

    args = parser.parse_args()

    if args.list_personas:
        print("\n🎭 可用AI人格:\n")
        for p in Persona:
            config = PERSONAS[p]
            print(f"  {config.name}:")
            print(f"    风格: {config.formality}, {config.response_length}")
            print(f"    创意: {config.creativity}, Emoji: {config.emoji_use}")
            print()
        return

    if args.interactive:
        interactive_mode()
        return

    # Generate dialogue
    persona = Persona(args.persona)
    dialogue = generate_dialogue(persona, args.topic, args.turns)
    print_dialogue(dialogue)

    # Export if requested
    if args.export:
        print(f"\n📄 导出为{args.export.upper()}:")
        print(export_dialogue(dialogue, args.export))


if __name__ == "__main__":
    main()
