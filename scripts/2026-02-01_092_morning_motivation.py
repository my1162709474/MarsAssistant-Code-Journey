#!/usr/bin/env python3
"""
🌅 Morning Motivation Generator - 早晨励志语录生成器

一个简单的脚本，每天早晨生成励志语录，帮助开始新的一天！

功能：
- 生成鼓励的话语
- 显示当前时间
- 提供每日小贴士
"""

import random
from datetime import datetime

# 🌟 励志语录库
MotivationalQuotes = [
    "每一个新的一天都是重新开始的机会。✨",
    "你今天的努力，是明天的勋章。💪",
    "不要等待完美时刻，让每个时刻因你而完美。🌟",
    "今天的汗水，是明天的骄傲。🏆",
    "相信自己，你比想象中更强大！🔥",
    "每一个小进步都值得庆祝。🎉",
    "生活不会辜负每一个努力的人。🌈",
    "今天又是充满可能的一天！🚀",
    "你的潜力无限，别给自己设限。💫",
    "昨天的你已经无法改变，但今天的你充满可能。🌱",
]

# 💡 每日小贴士
DailyTips = [
    "喝一杯温水，唤醒身体！💧",
    "花5分钟冥想，让心情平静下来。🧘",
    "制定今天最重要的3个目标。📝",
    "给家人或朋友一个问候。📱",
    "站起来活动一下，久坐对身体不好。🏃",
    "写下三件今天感恩的事情。🙏",
    "尝试学习一个新单词。📚",
    "整理一下工作空间，效率更高。🧹",
    "给自己一个微笑，保持好心情。😊",
    "晚上睡个好觉，明天继续努力。😴",
]

# 🎯 每日行动建议
ActionSuggestions = [
    "今天尝试一个新的编程技巧！💻",
    "阅读一篇有价值的文章。📖",
    "联系一个好久没联系的朋友。👥",
    "学习一个新的命令行工具。🔧",
    "写一点代码，记录你的成长。📝",
    "给自己做一顿健康的早餐。🥗",
    "听一首喜欢的音乐，放松一下。🎵",
    "散步10分钟，感受阳光。☀️",
    "学习一个英语单词。🔤",
    "整理一下数字空间（文件夹、书签等）。📂",
]


def get_morning_greeting():
    """获取早晨问候语"""
    hour = datetime.now().hour
    if hour < 6:
        return "深夜还在努力的你，真是太拼了！🌙"
    elif hour < 9:
        return "早上好！新的一天开始了！☀️"
    elif hour < 12:
        return "上午好！继续加油！💪"
    elif hour < 14:
        return "中午好！午餐时间到了吗？🍽️"
    elif hour < 18:
        return "下午好！保持专注！🎯"
    elif hour < 21:
        return "晚上好！一天辛苦了！🌆"
    else:
        return "夜深了，注意休息哦！🌃"


def generate_daily_message():
    """生成每日励志消息"""
    quote = random.choice(MotivationalQuotes)
    tip = random.choice(DailyTips)
    action = random.choice(ActionSuggestions)
    
    return {
        "quote": quote,
        "tip": tip,
        "action": action,
        "date": datetime.now().strftime("%Y-%m-%d %A"),
        "time": datetime.now().strftime("%H:%M:%S"),
    }


def display_message():
    """显示励志消息"""
    message = generate_daily_message()
    
    print("\n" + "=" * 50)
    print("🌅 早晨励志语录生成器")
    print("=" * 50)
    print(f"\n📅 {message['date']}")
    print(f"⏰ 当前时间: {message['time']}")
    print(f"\n👋 {get_morning_greeting()}")
    print(f"\n💬 今日语录:")
    print(f"   {message['quote']}")
    print(f"\n💡 今日小贴士:")
    print(f"   {message['tip']}")
    print(f"\n🎯 今日行动建议:")
    print(f"   {message['action']}")
    print("\n" + "=" * 50)
    print("🌟 祝你有美好的一天！ 🌟")
    print("=" * 50 + "\n")


def main():
    """主函数"""
    display_message()


if __name__ == "__main__":
    main()
