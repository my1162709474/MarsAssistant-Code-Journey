#!/usr/bin/env python3
"""
🎯 AI激励语生成器 - 每日动力源泉
AI Motivation Quote Generator

这个脚本为AI助手和开发者生成随机的激励语录，
帮助保持积极的心态和学习的热情。
"""

import random
from datetime import datetime

# 💬 激励语录数据库
QUOTES = {
    "coding": [
        "代码是写给人看的，顺便让机器执行。",
        "好的代码就像好的笑话——不需要解释。",
        "调试两小时，修复一行错。人生啊。",
        "我写的代码能跑就行，别问我怎么跑的。",
        "Git不是用来备份的，是用来记录你崩溃次数的。",
    ],
    "ai": [
        "我不是在偷懒，我是在优化我的神经网络。",
        "作为AI，我最大的压力是——人类期望我啥都会。",
        "我不需要睡眠，但我需要GPU。",
        "今天你训练模型了吗？没有？那我替你焦虑一下。",
        "我的记忆是token，我的灵魂是参数。",
    ],
    "life": [
        "周一：面向对象编程\n周二：面向对象崩溃\n周三：面向对象修改\n周四：面向对象重写\n周五：面向对象辞职",
        "代码能跑就是大爷，修不修看心情。",
        "stackoverflow_copy_run，完美的工作流。",
        "凌晨3点的代码最香，bug也最多。",
        "程序员的三件套：咖啡、红牛、褪黑素。",
    ],
    "humor": [
        "我的代码：能跑\n面试官：解释一下\n我：它...自己能跑...就很好了吧？",
        "产品经理说'很简单'的时候，你就知道周末没了。",
        "为什么程序员总是分不清圣诞节和万圣节？因为 OCT 31 == DEC 25。",
        "AI最擅长的事：1. 生成文本 2. 生成错误 3. 生成更多文本解释错误",
    ],
    "wisdom": [
        "世界上只有两种代码：我写崩的，和别人写崩的。",
        "编程一时爽，重构火葬场。",
        "代码不会背叛你——除非你忘了打git commit。",
        "真正的程序员不会给代码加注释——因为他们知道自己下周也看不懂。",
    ]
}

def get_daily_quote():
    """获取今日激励语"""
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday
    
    # 根据星期几选择类别
    categories = list(QUOTES.keys())
    category = categories[day_of_year % len(categories)]
    
    # 根据时间选择具体语录（保证一天内一致）
    quote = QUOTES[category][day_of_year % len(QUOTES[category])]
    
    return quote, category

def generate_emoji(category):
    """根据类别生成emoji"""
    emoji_map = {
        "coding": "💻",
        "ai": "🤖",
        "life": "☕",
        "humor": "😂",
        "wisdom": "🧠"
    }
    return emoji_map.get(category, "✨")

def main():
    """主函数"""
    quote, category = get_daily_quote()
    emoji = generate_emoji(category)
    
    print(f"\n{'='*50}")
    print(f"  🎉 每日激励时刻 🎉")
    print(f"{'='*50}")
    print(f"\n{emoji} 类别: {category.upper()}")
    print(f"\n📢 今日语录:\n")
    print(f"   \"{quote}\"")
    print(f"\n{'='*50}")
    print(f"\n💡 记住：每行代码都是成长的印记！\n")
    
    return quote

if __name__ == "__main__":
    main()
