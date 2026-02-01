#!/usr/bin/env python3
"""
🤖 AI性格分析器 - MarsAssistant Code Journey Day 96
分析你的编程风格和AI互动偏好
"""

import random
from datetime import datetime


class AIBotPersonalityAnalyzer:
    """AI性格分析器 - 通过简单问答了解你的技术风格"""
    
    def __init__(self):
        self.questions = [
            {
                "id": 1,
                "question": "当你遇到bug时，你通常会：",
                "options": [
                    ("A", "Google错误信息，搜索解决方案", "🔍 搜索型"),
                    ("B", "阅读文档和源码，自己debug", "📖 研究型"),
                    ("C", "直接问AI或同事", "🤝 协作型"),
                    ("D", "加打印语句，一步步跟踪", "🐛 调试型"),
                ]
            },
            {
                "id": 2,
                "question": "你喜欢什么时候写代码？",
                "options": [
                    ("A", "早上，头脑清醒时", "🌅 晨型人"),
                    ("B", "下午，精力充沛时", "☀️ 下午型"),
                    ("C", "深夜，万籁俱静时", "🌙 夜猫子"),
                    ("D", "随时都可以", "⚡ 弹性型"),
                ]
            },
            {
                "id": 3,
                "question": "面对一个新项目，你会：",
                "options": [
                    ("A", "先看README和文档", "📋 规划型"),
                    ("B", "直接动手写，边做边学", "🚀 行动型"),
                    ("C", "画架构图，理清思路", "🎨 设计型"),
                    ("D", "问有经验的人怎么开始", "💬 请教型"),
                ]
            },
            {
                "id": 4,
                "question": "你更喜欢哪种AI互动方式？",
                "options": [
                    ("A", "给出明确指令，让AI执行", "👑 指挥型"),
                    ("B", "和AI讨论，共同解决问题", "🤝 讨论型"),
                    ("C", "让AI解释，然后自己实现", "📚 学习型"),
                    ("D", "让AI写完代码，我直接用", "⚡ 效率型"),
                ]
            },
            {
                "id": 5,
                "question": "代码写完后，你会：",
                "options": [
                    ("A", "写详细的测试", "🧪 测试狂人"),
                    ("B", "让AI帮忙Code Review", "👀 审查型"),
                    ("C", "直接提交，简单测试", "🚀 快速型"),
                    ("D", "优化一下再提交", "✨ 完美型"),
                ]
            },
        ]
        
        self.personalities = {
            "🔍 搜索型": {
                "name": "独立研究者",
                "description": "你喜欢自己寻找答案，善于利用搜索引擎和社区资源解决问题。",
                "tips": "可以尝试更多与AI对话，有时候直接问AI比搜索更高效！",
                "emoji": "🕵️"
            },
            "📖 研究型": {
                "name": "源码深度爱好者",
                "description": "你相信源码是最权威的文档，喜欢深入理解技术的本质。",
                "tips": "保持这个习惯！深度理解是成为大牛的关键。",
                "emoji": "🔬"
            },
            "🤝 协作型": {
                "name": "团队协作大师",
                "description": "你善于利用各方资源，与AI和同事高效协作。",
                "tips": "你的协作能力很强，但也要注意培养独立思考能力！",
                "emoji": "🤝"
            },
            "🐛 调试型": {
                "name": "逻辑追踪者",
                "description": "你喜欢一步一步跟踪代码执行，逻辑思维严密。",
                "tips": "这是很好的习惯，可以尝试学习更多调试工具来提升效率！",
                "emoji": "🔍"
            },
            "🌅 晨型人": {
                "name": "早起先锋",
                "description": "早上是你精力最充沛的时候，适合处理复杂的编程任务。",
                "tips": "好好利用早上的高效时间！",
                "emoji": "☀️"
            },
            "☀️ 下午型": {
                "name": "午后战士",
                "description": "下午你有最好的状态，能够高效完成工作任务。",
                "tips": "把重要的任务安排在下午吧！",
                "emoji": "🌻"
            },
            "🌙 夜猫子": {
                "name": "深夜程序员",
                "description": "夜深人静时你的创造力达到顶峰，代码质量特别高。",
                "tips": "注意身体！熬夜虽好，但不要过度。",
                "emoji": "🦉"
            },
            "⚡ 弹性型": {
                "name": "时间管理大师",
                "description": "你能够灵活安排时间，不受时间限制。",
                "tips": "你的适应性很强，这是很好的优势！",
                "emoji": "⏰"
            },
            "📋 规划型": {
                "name": "先思后行型",
                "description": "你喜欢在做事前制定详细的计划，确保方向正确。",
                "tips": "规划是好事，但也要注意不要过度规划而延迟行动！",
                "emoji": "📝"
            },
            "🚀 行动型": {
                "name": "快速迭代型",
                "description": "你喜欢通过实践来学习，快速试错和迭代。",
                "tips": "你的行动力很强！尝试在行动前做简短的计划可能会更好。",
                "emoji": "💨"
            },
            "🎨 设计型": {
                "name": "架构设计师",
                "description": "你喜欢在动手前理清整体架构和设计模式。",
                "tips": "你的设计思维很棒！可以尝试一些设计模式相关的学习。",
                "emoji": "🎭"
            },
            "💬 请教型": {
                "name": "虚心求教型",
                "description": "你善于向有经验的人学习，能够快速获取知识。",
                "tips": "请教他人是很好的学习方式！同时也要尝试自己探索。",
                "emoji": "🗣️"
            },
            "👑 指挥型": {
                "name": "AI指挥官",
                "description": "你知道如何清晰地表达需求，让AI高效执行任务。",
                "tips": "你的提示词能力很强！可以尝试更复杂的任务。",
                "emoji": "👑"
            },
            "📚 学习型": {
                "name": "AI学徒",
                "description": "你把AI当作老师，喜欢理解原理后再自己实现。",
                "tips": "这种学习方式很扎实！继续保持好奇心！",
                "emoji": "📖"
            },
            "⚡ 效率型": {
                "name": "极速工程师",
                "description": "你追求最高效率，让AI帮你完成大部分工作。",
                "tips": "效率很重要！但不要忘记理解代码的逻辑。",
                "emoji": "⚡"
            },
            "🧪 测试狂人": {
                "name": "质量守护者",
                "description": "你对代码质量有高要求，通过测试确保代码正确性。",
                "tips": "测试是优秀代码的基础！你的习惯很棒。",
                "emoji": "🧪"
            },
            "👀 审查型": {
                "name": "代码审查者",
                "description": "你善于利用AI进行代码审查，发现潜在问题。",
                "tips": "Code Review是提升代码质量的好方法！",
                "emoji": "👁️"
            },
            "🚀 快速型": {
                "name": "快速发布者",
                "description": "你追求快速迭代和发布，相信快速试错。",
                "tips": "速度很重要！但也要注意代码质量。",
                "emoji": "🚀"
            },
            "✨ 完美型": {
                "name": "代码艺术家",
                "description": "你追求代码的完美，注重细节和可读性。",
                "tips": "完美主义是双刃剑！学会平衡质量和效率。",
                "emoji": "✨"
            },
        }
    
    def ask_question(self, question_data):
        """询问一个问题"""
        print(f"\n{'='*60}")
        print(f"问题 {question_data['id']}: {question_data['question']}")
        print(f"{'='*60}")
        for key, desc in question_data['options']:
            print(f"  {key}. {desc}")
        
        while True:
            choice = input("\n请选择 (A/B/C/D): ").strip().upper()
            if choice in ["A", "B", "C", "D"]:
                return choice
            print("无效选择，请输入 A、B、C 或 D")
    
    def analyze_personality(self, answers):
        """分析性格类型"""
        # 统计每个类型出现的次数
        type_counts = {}
        for answer in answers:
            option = self.questions[answer["qid"]-1]["options"][
                ["A", "B", "C", "D"].index(answer["answer"])
            ]
            type_key = option[0]  # A, B, C, or D
            type_desc = option[1]
            type_counts[type_desc] = type_counts.get(type_desc, 0) + 1
        
        # 找出主要类型
        main_type = max(type_counts, key=type_counts.get)
        return main_type
    
    def run(self):
        """运行分析器"""
        print("\n" + "🚀"*30)
        print("🤖 AI性格分析器 - 了解你的编程风格")
        print("🚀"*30)
        
        answers = []
        for question in self.questions:
            answer = self.ask_question(question)
            answers.append({
                "qid": question["id"],
                "answer": answer
            })
        
        # 分析结果
        main_type = self.analyze_personality(answers)
        personality = self.personalities.get(main_type, {
            "name": "神秘型",
            "description": "你的风格很独特，难以归类。",
            "tips": "保持你的独特性！",
            "emoji": "🎭"
        })
        
        # 打印结果
        print(f"\n{'🎉'*30}")
        print("📊 分析结果")
        print(f"{'🎉'*30}")
        print(f"\n{personality['emoji']} 你的风格是: {personality['name']}")
        print(f"\n📝 特点: {personality['description']}")
        print(f"\n💡 建议: {personality['tips']}")
        print(f"\n{'='*60}")
        
        return personality


def main():
    """主函数"""
    analyzer = AIBotPersonalityAnalyzer()
    result = analyzer.run()
    
    print("\n感谢使用AI性格分析器！")
    print("这是 MarsAssistant Code Journey 的一部分")
    print("GitHub: https://github.com/my1162709474/MarsAssistant-Code-Journey\n")


if __name__ == "__main__":
    main()
