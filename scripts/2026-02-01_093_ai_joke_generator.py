#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 AI笑话生成器 - Day 93
每天一个笑话，让代码也充满欢乐！

功能：
- 随机生成各种类型的笑话
- 支持中文、英文、双语笑话
- 包含程序员专属笑话
- 每日一笑，快乐编程！
"""

import random
import time
from datetime import datetime

class AIJokeGenerator:
    """AI笑话生成器类"""
    
    def __init__(self):
        # 中文笑话库
        self.chinese_jokes = [
            {
                "setup": "为什么程序员不喜欢户外活动？",
                "punchline": "因为户外有太多bug（虫子）！🐛",
                "category": "程序员笑话"
            },
            {
                "setup": "程序员最讨厌的饼是什么？",
                "punchline": "南瓜饼，因为要"画饼"（bug）！🎃",
                "category": "程序员笑话"
            },
            {
                "setup": "AI和程序员有什么共同点？",
                "punchline": "都需要大量的"训练"，而且都会"过拟合"！🤖",
                "category": "AI笑话"
            },
            {
                "setup": "为什么AI不会生病？",
                "punchline": "因为它有自己的"抗体"（Antivirus）！💊",
                "category": "AI笑话"
            },
            {
                "setup": "Python和Java有什么区别？",
                "punchline": "Python说：我简单！Java说：我严格！🤔",
                "category": "编程语言"
            },
            {
                "setup": "为什么Git这么受欢迎？",
                "punchline": "因为它懂得"分支"人生！🌿",
                "category": "工具笑话"
            },
            {
                "setup": "AI最近心情不好，因为...？",
                "punchline": "它的"情绪向量"全是负数！📉",
                "category": "AI笑话"
            },
            {
                "setup": "程序员和产品经理的对话：",
                "punchline": "PM：我要五彩斑斓的黑。程序员：...好。😵",
                "category": "职场笑话"
            }
        ]
        
        # 英文笑话库
        self.english_jokes = [
            {
                "setup": "Why do programmers prefer dark mode?",
                "punchline": "Because light attracts bugs! 🐛",
                "category": "Programmer Jokes"
            },
            {
                "setup": "What's a programmer's favorite hangout place?",
                "punchline": "Foo Bar! 🍺",
                "category": "Programmer Jokes"
            },
            {
                "setup": "Why did the AI go to therapy?",
                "punchline": "It had too many deep neural issues! 🧠",
                "category": "AI Jokes"
            },
            {
                "setup": "How does AI make decisions?",
                "punchline": "It weighs all the probabilities and then randomly picks one! 🎲",
                "category": "AI Jokes"
            },
            {
                "setup": "Why did the Python developer go broke?",
                "punchline": "Because he couldn't make enough cents with Python! 🐍",
                "category": "Programming"
            },
            {
                "setup": "What's a programmer's favorite song?",
                "punchline": "A loop! 🔄",
                "category": "Programmer Jokes"
            },
            {
                "setup": "Why do programmers always mix up Christmas and Halloween?",
                "punchline": "Because Oct 31 == Dec 25! 🎃🎄",
                "category": "Programmer Jokes"
            },
            {
                "setup": "What's an AI's favorite type of music?",
                "punchline": "Heavy metal... learning! 🎸",
                "category": "AI Jokes"
            }
        ]
        
        # 程序员箴言
        self.programmer_wisdom = [
            "没有bug的代码是不完整的代码。",
            "注释是写给未来的自己看的。",
            "_stack_overflow_ 是程序员的精神家园。",
            "程序员的头发：不是掉了，就是在掉的路上。",
            "Bug就像俄罗斯方块，总是一个接一个。",
            "写代码5分钟，debug 5小时。",
            "AI不会取代程序员，但会用AI的程序员会取代不会用AI的。",
        ]
        
        # 每日鼓励语录
        self.daily_encouragement = [
            "今天也要元气满满地写代码哦！💪",
            "每一个bug都是成长的垫脚石！🚀",
            "编译通过了，今天就是幸运日！🎉",
            "代码虐我千百遍，我待代码如初恋！💕",
            "debug成功的那一刻，最快乐了！✨",
        ]
    
    def get_joke(self, language="mixed", category=None):
        """获取一个笑话
        
        Args:
            language: 'chinese', 'english', 或 'mixed'
            category: 笑话类别筛选
        
        Returns:
            dict: 包含笑话的字典
        """
        jokes = []
        
        if language in ["chinese", "mixed"]:
            jokes.extend(self.chinese_jokes)
        if language in ["english", "mixed"]:
            jokes.extend(self.english_jokes)
        
        if category:
            jokes = [j for j in jokes if j["category"] == category]
        
        if not jokes:
            jokes = self.chinese_jokes + self.english_jokes
        
        joke = random.choice(jokes)
        
        return {
            "setup": joke["setup"],
            "punchline": joke["punchline"],
            "category": joke["category"],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_wisdom(self):
        """获取一条程序员箴言"""
        return random.choice(self.programmer_wisdom)
    
    def get_encouragement(self):
        """获取一条今日鼓励"""
        return random.choice(self.daily_encouragement)
    
    def tell_joke(self):
        """讲述一个笑话（带动画效果）"""
        joke = self.get_joke()
        
        print("\n" + "="*50)
        print(f"📚 类别: {joke['category']}")
        print("="*50)
        print(f"\n🤖 {joke['setup']}")
        time.sleep(1.5)
        print(f"\n👉 {joke['punchline']}")
        print("\n" + "="*50)
        
        return joke
    
    def daily_wisdom(self):
        """每日箴言"""
        print("\n" + "💡"*25)
        print(f"\n✨ 程序员箴言：")
        print(f"   {self.get_wisdom()}")
        print(f"\n🌟 今日鼓励：")
        print(f"   {self.get_encouragement()}")
        print("\n" + "💡"*25)


def main():
    """主函数"""
    generator = AIJokeGenerator()
    
    print("\n🎭 欢迎使用 AI笑话生成器！")
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n让AI给你讲个笑话吧！\n")
    
    # 随机讲一个笑话
    generator.tell_joke()
    
    # 显示每日箴言
    generator.daily_wisdom()
    
    print("\n🎉 记得保持好心情，明天继续写代码！")
    print("🔄 运行此脚本获取新的笑话！\n")


if __name__ == "__main__":
    main()
