#!/usr/bin/env python3
"""
🌈 Smart Emoji Mood Tracker - 智能Emoji心情跟踪器
Day 69: 记录和分析每日心情变化

功能：
- 🎯 快速记录心情
- 📊 心情趋势分析
- 🗓️ 历史数据可视化
- 💡 智能建议生成
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter
import random

MOOD_EMOJIS = {
    "😄": "开心",
    "🙂": "愉快", 
    "😐": "平静",
    "😔": "低落",
    "😢": "难过",
    "😡": "生气",
    "😴": "疲惫",
    "🤔": "思考",
    "😎": "自信",
    "🥰": "幸福"
}

MOOD_SCORES = {
    "😄": 10, "🙂": 8, "😐": 5, 
    "😔": 3, "😢": 2, "😡": 2,
    "😴": 4, "🤔": 6, "😎": 9, "🥰": 10
}

class MoodTracker:
    def __init__(self, data_file="mood_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self):
        """加载历史数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"entries": [], "stats": {}}
        return {"entries": [], "stats": {}}
    
    def save_data(self):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def log_mood(self, emoji, note=""):
        """记录心情"""
        if emoji not in MOOD_EMOJIS:
            print(f"❌ 无效的心情emoji。可用: {', '.join(MOOD_EMOJIS.keys())}")
            return False
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "emoji": emoji,
            "mood_name": MOOD_EMOJIS[emoji],
            "score": MOOD_SCORES[emoji],
            "note": note
        }
        self.data["entries"].append(entry)
        self.save_data()
        print(f"✅ 已记录: {emoji} {MOOD_EMOJIS[emoji]}")
        return True
    
    def getweekly_stats(self):
        """获取周统计"""
        week_ago = datetime.now() - timedelta(days=7)
        recent = [e for e in self.data["entries"] 
                 if datetime.fromisoformat(e["timestamp"]) > week_ago]
        
        if not recent:
            return "本周还没有记录，开始记录吧！📝"
        
        scores = [e["score"] for e in recent]
        emojis = [e["emoji"] for e in recent]
        
        avg_score = sum(scores) / len(scores)
        most_common = Counter(emojis).most_common(1)[0]
        
        return f"""
📊 本周心情统计 (共{len(recent)}条记录)
━━━━━━━━━━━━━━━━━━
平均心情指数: {'⭐' * int(avg_score)} ({avg_score:.1f}/10)
最常出现: {most_common[0]} ({most_common[1]}次)
心情分布: {dict(Counter(emojis))}
"""
    
    def generate_insight(self):
        """生成智能洞察"""
        if len(self.data["entries"]) < 3:
            return "💡 多记录几天后，我会给你更有价值的洞察哦！"
        
        recent = self.data["entries"][-7:]
        scores = [e["score"] for e in recent]
        
        if sum(scores) / len(scores) >= 7:
            return "🌟 你最近心情都很不错！保持这种积极的状态吧！"
        elif sum(scores) / len(scores) <= 4:
            return "💙 最近心情有些低落，记得多关心自己。试试运动或和朋友聊聊？"
        else:
            return "⚖️ 你的心情波动很正常，这就是生活的节奏呀！"
    
    def show_menu(self):
        """显示交互菜单"""
        print("\n" + "🌈" * 20)
        print("   智能Emoji心情跟踪器")
        print("🌈" * 20)
        print("\n选择心情:")
        for emoji, name in MOOD_EMOJIS.items():
            print(f"  {emoji} - {name}")
        print("\n命令: /stats 查看统计, /insight 洞察, /quit 退出")

def main():
    tracker = MoodTracker()
    
    print("🌈 欢迎使用智能Emoji心情跟踪器！")
    print("输入心情emoji或命令 (/stats, /insight, /quit)\n")
    
    while True:
        try:
            user_input = input("🎯 当前心情: ").strip()
            
            if user_input in ['/quit', '/exit', 'q']:
                print("👋 再见！记得每天都要开心哦！")
                break
            elif user_input == '/stats':
                print(tracker.getweekly_stats())
            elif user_input == '/insight':
                print(f"\n💡 {tracker.generate_insight()}")
            elif user_input in MOOD_EMOJIS:
                note = input("📝 添加备注 (可选): ").strip()
                tracker.log_mood(user_input, note)
            else:
                print("❓ 无效输入，输入emoji或命令")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 已退出")
            break

if __name__ == "__main__":
    main()
