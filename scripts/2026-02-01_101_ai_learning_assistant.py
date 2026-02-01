#!/usr/bin/env python3
"""
AI代码学习助手 - Day 101
智能追踪学习进度，分析学习模式，提供个性化建议

功能:
- 学习时间追踪与分析
- 学习进度可视化
- 知识点掌握度评估
- 智能学习建议生成
- 学习习惯优化
"""

from datetime import datetime, timedelta
from collections import defaultdict
import json
import random
import hashlib
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Difficulty(Enum):
    """知识点难度等级"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningSession:
    """学习会话类"""
    
    def __init__(self, topic: str, duration_minutes: int, 
                 difficulty: Difficulty, notes: str = ""):
        self.topic = topic
        self.duration = duration_minutes
        self.difficulty = difficulty
        self.notes = notes
        self.timestamp = datetime.now()
        self.comprehension_score = 0.0  # 理解度评分 (0-100)
        self.practice_score = 0.0       # 练习评分 (0-100)
        
    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "duration": self.duration,
            "difficulty": self.difficulty.value,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat(),
            "comprehension_score": self.comprehension_score,
            "practice_score": self.practice_score
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LearningSession':
        session = cls(
            topic=data["topic"],
            duration_minutes=data["duration"],
            difficulty=Difficulty(data["difficulty"]),
            notes=data.get("notes", "")
        )
        session.timestamp = datetime.fromisoformat(data["timestamp"])
        session.comprehension_score = data.get("comprehension_score", 0.0)
        session.practice_score = data.get("practice_score", 0.0)
        return session


class LearningAssistant:
    """AI代码学习助手主类"""
    
    def __init__(self, user_name: str = "学习者"):
        self.user_name = user_name
        self.sessions: List[LearningSession] = []
        self.topics: Dict[str, Dict] = {}  # 知识点掌握情况
        self.goals: Dict[str, dict] = {}    # 学习目标
        self.streak_days = 0                # 连续学习天数
        self.last_learning_date: Optional[datetime] = None
        
        # 每日学习统计
        self.daily_stats = defaultdict(lambda: {
            "total_minutes": 0,
            "topics_learned": set(),
            "sessions": 0
        })
        
        # 难度权重（用于计算综合评分）
        self.difficulty_weights = {
            Difficulty.BEGINNER: 1.0,
            Difficulty.INTERMEDIATE: 1.5,
            Difficulty.ADVANCED: 2.0,
            Difficulty.EXPERT: 3.0
        }
        
    def start_session(self, topic: str, duration_minutes: int,
                      difficulty: Difficulty, notes: str = "") -> LearningSession:
        """开始一个新的学习会话"""
        session = LearningSession(topic, duration_minutes, difficulty, notes)
        self.sessions.append(session)
        
        # 更新每日统计
        today = session.timestamp.date().isoformat()
        self.daily_stats[today]["total_minutes"] += duration_minutes
        self.daily_stats[today]["topics_learned"].add(topic)
        self.daily_stats[today]["sessions"] += 1
        
        # 更新知识点
        if topic not in self.topics:
            self.topics[topic] = {
                "total_time": 0,
                "sessions_count": 0,
                "avg_comprehension": 0,
                "avg_practice": 0,
                "difficulty": difficulty.value,
                "first_seen": session.timestamp.isoformat(),
                "last_practice": None
            }
        
        topic_data = self.topics[topic]
        topic_data["total_time"] += duration_minutes
        topic_data["sessions_count"] += 1
        topic_data["last_practice"] = session.timestamp.isoformat()
        
        # 更新连续学习天数
        self._update_streak()
        
        return session
    
    def end_session(self, session: LearningSession, 
                    comprehension: float, practice: float) -> dict:
        """结束学习会话，记录评分"""
        session.comprehension_score = max(0, min(100, comprehension))
        session.practice_score = max(0, min(100, practice))
        
        # 更新知识点平均分
        topic = session.topic
        if topic in self.topics:
            t = self.topics[topic]
            t["avg_comprehension"] = self._running_average(
                t["avg_comprehension"], t["sessions_count"], comprehension
            )
            t["avg_practice"] = self._running_average(
                t["avg_practice"], t["sessions_count"], practice
            )
        
        return self._generate_session_summary(session)
    
    def _running_average(self, current_avg: float, count: int, 
                         new_value: float) -> float:
        """计算运行平均值"""
        if count == 0:
            return new_value
        return (current_avg * count + new_value) / (count + 1)
    
    def _update_streak(self):
        """更新连续学习天数"""
        today = datetime.now().date()
        
        if self.last_learning_date is None:
            self.streak_days = 1
        else:
            days_diff = (today - self.last_learning_date).days
            
            if days_diff == 0:
                pass  # 同一天，不变
            elif days_diff == 1:
                self.streak_days += 1  # 连续第二天
            else:
                self.streak_days = 1   # 断开，重新开始
        
        self.last_learning_date = today
    
    def _generate_session_summary(self, session: LearningSession) -> dict:
        """生成学习会话总结"""
        weighted_score = (
            session.comprehension_score * 0.4 + 
            session.practice_score * 0.6
        ) * self.difficulty_weights[session.difficulty]
        
        return {
            "topic": session.topic,
            "duration": session.duration,
            "difficulty": session.difficulty.value,
            "comprehension": session.comprehension_score,
            "practice": session.practice_score,
            "weighted_score": round(weighted_score, 2),
            "timestamp": session.timestamp.isoformat()
        }
    
    def get_learning_stats(self, days: int = 7) -> dict:
        """获取学习统计数据"""
        today = datetime.now().date()
        start_date = today - timedelta(days=days)
        
        # 统计时间段内的学习数据
        total_minutes = 0
        total_sessions = 0
        topics_covered = set()
        
        for date_str, stats in self.daily_stats.items():
            date = datetime.fromisoformat(date_str).date()
            if start_date <= date <= today:
                total_minutes += stats["total_minutes"]
                total_sessions += stats["sessions"]
                topics_covered.update(stats["topics_learned"])
        
        # 计算平均每日学习时间
        active_days = len([
            d for d in self.daily_stats.keys()
            if start_date <= datetime.fromisoformat(d).date() <= today
        ])
        avg_daily_minutes = total_minutes / max(active_days, 1)
        
        # 计算掌握度最高的知识点
        top_topics = sorted(
            self.topics.items(),
            key=lambda x: (x[1]["avg_comprehension"] + x[1]["avg_practice"]) / 2,
            reverse=True
        )[:5]
        
        return {
            "period_days": days,
            "total_learning_minutes": total_minutes,
            "total_sessions": total_sessions,
            "topics_covered": len(topics_covered),
            "avg_daily_minutes": round(avg_daily_minutes, 1),
            "streak_days": self.streak_days,
            "total_topics": len(self.topics),
            "top_mastered_topics": [
                {"topic": t[0], "mastery": round(
                    (t[1]["avg_comprehension"] + t[1]["avg_practice"]) / 2, 1
                )}
                for t in top_topics
            ],
            "level": self._calculate_level()
        }
    
    def _calculate_level(self) -> dict:
        """计算当前学习等级"""
        total_score = sum(
            (s.comprehension_score + s.practice_score) / 2 * 
            self.difficulty_weights[s.difficulty]
            for s in self.sessions
        )
        
        total_minutes = sum(s.duration for s in self.sessions)
        
        # 等级计算
        if total_score < 100:
            level = 1
            title = "入门新手"
        elif total_score < 500:
            level = 2
            title = "基础学习者"
        elif total_score < 1500:
            level = 3
            title = "进阶开发者"
        elif total_score < 5000:
            level = 4
            title = "高级工程师"
        else:
            level = 5
            title = "技术专家"
        
        return {
            "level": level,
            "title": title,
            "total_score": round(total_score, 1),
            "total_minutes": total_minutes,
            "next_level_score": level * 500 if level < 5 else None
        }
    
    def get_smart_suggestions(self) -> List[str]:
        """生成智能学习建议"""
        suggestions = []
        
        if not self.sessions:
            return ["开始你的第一个学习会话吧！选择感兴趣的编程主题开始学习。"]
        
        stats = self.get_learning_stats()
        
        # 检查学习强度
        if stats["avg_daily_minutes"] < 30:
            suggestions.append("💡 建议每天学习时间增加到30分钟以上，学习效果会更好。")
        
        # 检查连续性
        if self.streak_days < 3:
            suggestions.append("🔥 连续学习很重要！试着每天坚持学习，建立好习惯。")
        elif self.streak_days >= 7:
            suggestions.append("⭐ 太棒了！你已经连续学习一周了！保持这个节奏！")
        
        # 检查知识点覆盖
        if stats["topics_covered"] < 5:
            suggestions.append("📚 建议多尝试不同的主题，广泛涉猎可以拓宽视野。")
        
        # 难度平衡建议
        beginner_count = sum(
            1 for t in self.topics.values() 
            if t["difficulty"] == "beginner"
        )
        advanced_count = sum(
            1 for t in self.topics.values() 
            if t["difficulty"] in ["advanced", "expert"]
        )
        
        if beginner_count > advanced_count + 3:
            suggestions.append("🚀 可以尝试学习一些高级主题，挑战自己！")
        
        if advanced_count > beginner_count:
            suggestions.append("🔄 建议回顾基础知识，夯实基础同样重要。")
        
        # 基于掌握度低的知识点建议复习
        weak_topics = [
            t for t, data in self.topics.items()
            if (data["avg_comprehension"] + data["avg_practice"]) / 2 < 50
        ]
        if weak_topics:
            random.shuffle(weak_topics)
            suggestions.append(f"📝 建议复习: {', '.join(weak_topics[:3])}")
        
        # 随机鼓励
        encouragement = [
            "学习是一个循序渐进的过程，不要着急！",
            "每一行代码都是你成长的见证！",
            "保持好奇心，持续探索新技术！",
            "代码改变世界，你正在参与其中！"
        ]
        suggestions.append(random.choice(encouragement))
        
        return suggestions[:5]  # 最多返回5条建议
    
    def export_data(self) -> dict:
        """导出学习数据"""
        return {
            "user_name": self.user_name,
            "export_date": datetime.now().isoformat(),
            "total_sessions": len(self.sessions),
            "total_topics": len(self.topics),
            "streak_days": self.streak_days,
            "level": self._calculate_level(),
            "sessions": [s.to_dict() for s in self.sessions],
            "topics": self.topics
        }
    
    def import_data(self, data: dict):
        """导入学习数据"""
        self.user_name = data.get("user_name", self.user_name)
        self.sessions = [LearningSession.from_dict(s) for s in data.get("sessions", [])]
        self.topics = data.get("topics", {})
        self.streak_days = data.get("streak_days", 0)
        
        # 重建每日统计
        for session in self.sessions:
            date = session.timestamp.date().isoformat()
            self.daily_stats[date]["total_minutes"] += session.duration
            self.daily_stats[date]["topics_learned"].add(session.topic)
            self.daily_stats[date]["sessions"] += 1
    
    def visualize_progress(self) -> str:
        """生成学习进度ASCII图表"""
        lines = []
        lines.append("=" * 50)
        lines.append(f"📊 {self.user_name}的学习进度报告")
        lines.append("=" * 50)
        
        stats = self.get_learning_stats()
        level = stats["level"]
        
        lines.append(f"\n🎯 等级: {level['level']} - {level['title']}")
        lines.append(f"📈 总积分: {level['total_score']}")
        lines.append(f"⏱️  总学习时间: {level['total_minutes']} 分钟")
        lines.append(f"🔥 连续学习: {stats['streak_days']} 天")
        lines.append(f"📚 掌握主题数: {stats['topics_covered']}")
        
        if level["next_level_score"]:
            progress = min(100, level["total_score"] / level["next_level_score"] * 100)
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            lines.append(f"\n📊 升级进度: [{bar}] {progress:.1f}%")
        
        lines.append("\n🌟 掌握最好的主题:")
        for item in stats["top_mastered_topics"][:3]:
            lines.append(f"   • {item['topic']}: {item['mastery']}%")
        
        lines.append("\n" + "=" * 50)
        return "\n".join(lines)


def demo():
    """演示学习助手功能"""
    print("\n🤖 AI代码学习助手 - Day 101 演示\n")
    
    # 创建学习助手
    assistant = LearningAssistant("Mars")
    
    # 模拟一些学习记录
    sample_sessions = [
        ("Python基础", 45, Difficulty.BEGINNER, 85, 80),
        ("数据结构", 60, Difficulty.INTERMEDIATE, 75, 70),
        ("算法设计", 90, Difficulty.ADVANCED, 70, 65),
        ("机器学习", 120, Difficulty.ADVANCED, 80, 75),
        ("深度学习", 90, Difficulty.EXPERT, 75, 70),
    ]
    
    print("📝 模拟学习记录:")
    for i, (topic, duration, diff, comp, prac) in enumerate(sample_sessions, 1):
        session = assistant.start_session(topic, duration, diff)
        assistant.end_session(session, comp, prac)
        print(f"   {i}. {topic} ({duration}分钟, {diff.value})")
    
    # 显示学习进度
    print(assistant.visualize_progress())
    
    # 显示统计信息
    stats = assistant.get_learning_stats()
    print("\n📊 周统计:")
    print(f"   总学习时间: {stats['total_learning_minutes']} 分钟")
    print(f"   会话数: {stats['total_sessions']}")
    print(f"   平均每日: {stats['avg_daily_minutes']} 分钟")
    
    # 显示建议
    print("\n💡 智能建议:")
    for suggestion in assistant.get_smart_suggestions():
        print(f"   {suggestion}")
    
    # 导出数据示例
    data = assistant.export_data()
    data_hash = hashlib.md5(json.dumps(data).encode()).hexdigest()[:8]
    print(f"\n✅ 数据已导出 (哈希: {data_hash})")
    print(f"   总会话数: {data['total_sessions']}")
    print(f"   主题数: {data['total_topics']}")


if __name__ == "__main__":
    demo()
