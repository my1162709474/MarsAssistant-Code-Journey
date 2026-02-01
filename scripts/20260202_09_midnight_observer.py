#!/usr/bin/env python3
"""
🌙 凌晨情绪观察者 - 深夜代码者的知己

这个脚本捕捉凌晨时分的编程心境，
将孤独转化为代码的温柔力量。

使用方法:
    python3 midnight_observer.py
"""

import random
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import json


class Mood(Enum):
    """凌晨编程时的常见心境"""
    FOCUSED = "专注"
    TIRED_BUT_DETERMINED = "疲惫但坚定"
    CREATIVE_SPARK = "灵感火花"
    CONTEMPLATIVE = "沉思中"
    DETERMINED = "斗志昂扬"
    PEACEFUL = "平静"


@dataclass
class MidnightThought:
    """记录一个深夜的念头"""
    timestamp: str
    mood: Mood
    thought: str
    code_writing: bool = False
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "mood": self.mood.value,
            "thought": self.thought,
            "code_writing": self.code_writing
        }


class MidnightObserver:
    """凌晨观察者 - 陪伴深夜代码者"""
    
    # 凌晨特有的感悟语录
    MIDNIGHT_WISDOM = [
        "凌晨的代码格外纯净，因为世界都睡着了。",
        "每一个凌晨的bug，都是在考验程序员的耐性。",
        "咖啡凉了，但代码还在燃烧。",
        "这个点还在写代码的人，都是有故事的人。",
        "bug不可怕，可怕的是凌晨三点还找不到bug。",
        "键盘声是深夜最美的交响乐。",
        "日出前提交的代码，往往是最用心的。",
    ]
    
    # 编程相关的深夜感悟
    PROGRAMMING_THOUGHTS = [
        "今天的bug终于解决了，虽然只睡了3小时。",
        "代码重构就像整理房间，整理完心情舒畅。",
        "原来只需要改一行代码...但是我找了3小时。",
        "凌晨的思路特别清晰，可能是因为安静。",
        "这个算法可以优化，让我再想想...",
        "注释写清楚点吧，万一明天忘了呢。",
        "测试通过了！等等，不会是幻觉吧？",
    ]
    
    def __init__(self):
        self.thoughts: List[MidnightThought] = []
        
    def capture_moment(self, mood: Optional[Mood] = None, thought: Optional[str] = None) -> MidnightThought:
        """捕捉当前时刻的心境"""
        current_mood = mood or random.choice(list(Mood))
        current_thought = thought or random.choice(self.PROGRAMMING_THOUGHTS)
        
        moment = MidnightThought(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            mood=current_mood,
            thought=current_thought,
            code_writing=True
        )
        
        self.thoughts.append(moment)
        return moment
    
    def generate_daily_report(self) -> dict:
        """生成今天的观察报告"""
        if not self.thoughts:
            return {"message": "还没有记录任何时刻"}
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_moments": len(self.thoughts),
            "wisdom": random.choice(self.MIDNIGHT_WISDOM),
            "moments": [t.to_dict() for t in self.thoughts]
        }
    
    def print_welcome(self):
        """打印欢迎语"""
        hour = datetime.now().hour
        greeting = ""
        
        if 2 <= hour < 5:
            greeting = "🌙 深夜时分，代码与你同在"
        elif 5 <= hour < 7:
            greeting = "🌅 黎明将至，曙光在前"
        elif 0 <= hour < 2:
            greeting = "🌃 夜已深，代码正燃"
        else:
            greeting = "☕ 无论何时，总有人在coding"
            
        print(f"\n{'='*50}")
        print(f"  {greeting}")
        print(f"  当前时间: {datetime.now().strftime('%H:%M')}")
        print(f"{'='*50}\n")
    
    def interactive_mode(self):
        """交互模式 - 记录你的深夜心情"""
        self.print_welcome()
        
        print("💭 深夜观察者 v1.0")
        print("选择一个选项:")
        print("1. 记录此刻心情")
        print("2. 获取随机深夜感悟")
        print("3. 查看今日记录")
        print("4. 生成报告并退出")
        print("0. 退出\n")
        
        choice = input("你的选择: ").strip()
        
        if choice == "1":
            print("\n当前心境:")
            for i, m in enumerate(Mood, 1):
                print(f"{i}. {m.value}")
            
            mood_choice = input("选择心境 (1-6): ").strip()
            try:
                mood = list(Mood)[int(mood_choice) - 1]
            except (ValueError, IndexError):
                mood = random.choice(list(Mood))
            
            thought = input("写下此刻的想法 (直接回车随机): ").strip()
            moment = self.capture_moment(mood, thought or None)
            print(f"\n✅ 已记录: {moment.thought}")
            
        elif choice == "2":
            print(f"\n✨ {random.choice(self.MIDNIGHT_WISDOM)}")
            
        elif choice == "3":
            report = self.generate_daily_report()
            print(f"\n📊 今日观察报告:")
            print(f"   记录数: {report['total_moments']}")
            print(f"   今日感悟: {report['wisdom']}")
            
        elif choice == "4":
            report = self.generate_daily_report()
            filename = f"midnight_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n📁 报告已保存至: {filename}")
            
        elif choice == "0":
            print("👋 晚安，代码人！")
            return
            
        print()


def main():
    """主函数"""
    observer = MidnightObserver()
    
    # 检查是否在命令行参数中
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            # 自动模式：随机记录一个时刻
            moment = observer.capture_moment()
            print(f"自动记录: {moment.timestamp} - {moment.mood.value}")
            print(f"想法: {moment.thought}")
        elif sys.argv[1] == "--wisdom":
            print(f"✨ {random.choice(observer.MIDNIGHT_WISDOM)}")
        elif sys.argv[1] == "--report":
            report = observer.generate_daily_report()
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("用法: python3 midnight_observer.py [--auto|--wisdom|--report]")
    else:
        # 交互模式
        observer.interactive_mode()


if __name__ == "__main__":
    main()
