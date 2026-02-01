#!/usr/bin/env python3
"""
🎓 智能代码复习助手 - Day 98
帮助回顾和复习之前学过的代码知识点

功能：
- 基于艾宾浩斯遗忘曲线安排复习计划
- 代码知识点卡片管理
- 复习进度追踪
- 生成复习报告

让学习更高效！📚
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict


class SmartCodeReviewer:
    """智能代码复习助手"""
    
    def __init__(self, data_file="review_data.json"):
        self.data_file = data_file
        self.knowledge_base = self.load_data()
        
    def load_data(self):
        """加载复习数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "topics": {},           # 主题: {"name": "排序算法", "files": [], "last_review": None}
            "review_schedule": [],  # 复习计划列表
            "mastery_levels": {},   # 掌握程度
            "study_logs": []        # 学习日志
        }
    
    def save_data(self):
        """保存复习数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def add_topic(self, name, file_path, category="算法"):
        """添加学习主题"""
        topic_id = f"topic_{len(self.knowledge_base['topics']) + 1}"
        self.knowledge_base["topics"][topic_id] = {
            "name": name,
            "file_path": file_path,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "last_review": None,
            "review_count": 0,
            "mastery_score": 0.0
        }
        self.schedule_review(topic_id)
        self.save_data()
        return topic_id
    
    def schedule_review(self, topic_id, days_until_review=None):
        """安排复习时间（艾宾浩斯曲线）"""
        topic = self.knowledge_base["topics"].get(topic_id)
        if not topic:
            return
        
        review_count = topic["review_count"]
        
        # 艾宾浩斯复习间隔：1天, 3天, 7天, 14天, 30天
        if days_until_review is None:
            intervals = [1, 3, 7, 14, 30]
            if review_count < len(intervals):
                days_until_review = intervals[review_count]
            else:
                days_until_review = 30  # 最大间隔30天
        
        review_date = datetime.now() + timedelta(days=days_until_review)
        
        self.knowledge_base["review_schedule"].append({
            "topic_id": topic_id,
            "topic_name": topic["name"],
            "scheduled_date": review_date.strftime("%Y-%m-%d"),
            "interval": days_until_review
        })
    
    def get_due_reviews(self):
        """获取今天到期的复习"""
        today = datetime.now().strftime("%Y-%m-%d")
        due = []
        for item in self.knowledge_base["review_schedule"]:
            if item["scheduled_date"] <= today:
                due.append(item)
        return due
    
    def complete_review(self, topic_id, understanding_level=3):
        """
        完成一次复习
        
        Args:
            topic_id: 主题ID
            understanding_level: 理解程度 (1-5)
        """
        topic = self.knowledge_base["topics"].get(topic_id)
        if not topic:
            return
        
        topic["last_review"] = datetime.now().isoformat()
        topic["review_count"] += 1
        
        # 更新掌握程度
        current_mastery = topic.get("mastery_score", 0)
        # 使用加权平均计算新掌握度
        new_mastery = (current_mastery * topic["review_count"] + understanding_level) / (topic["review_count"] + 1)
        topic["mastery_score"] = round(new_mastery, 2)
        
        # 安排下次复习
        self.schedule_review(topic_id)
        
        # 记录日志
        self.knowledge_base["study_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "review",
            "topic_id": topic_id,
            "topic_name": topic["name"],
            "understanding_level": understanding_level,
            "new_mastery": new_mastery
        })
        
        self.save_data()
        return new_mastery
    
    def get_review_stats(self):
        """获取复习统计"""
        topics = self.knowledge_base["topics"]
        total = len(topics)
        reviewed = sum(1 for t in topics.values() if t["last_review"])
        avg_mastery = sum(t["mastery_score"] for t in topics.values()) / total if total > 0 else 0
        
        due_reviews = len(self.get_due_reviews())
        
        return {
            "total_topics": total,
            "reviewed_topics": reviewed,
            "pending_reviews": total - reviewed,
            "due_today": due_reviews,
            "average_mastery": round(avg_mastery, 2),
            "mastery_distribution": {
                "beginner": sum(1 for t in topics.values() if t["mastery_score"] < 2),
                "learning": sum(1 for t in topics.values() if 2 <= t["mastery_score"] < 3.5),
                " proficient": sum(1 for t in topics.values() if 3.5 <= t["mastery_score"] < 4.5),
                "master": sum(1 for t in topics.values() if t["mastery_score"] >= 4.5)
            }
        }
    
    def generate_review_report(self):
        """生成复习报告"""
        stats = self.get_review_stats()
        due = self.get_due_reviews()
        
        report = f"""
📊 代码复习报告 - {datetime.now().strftime("%Y-%m-%d")}
====================================

📈 整体统计
- 总主题数: {stats['total_topics']}
- 已复习: {stats['reviewed_topics']}
- 待复习: {stats['pending_reviews']}
- 今日到期: {stats['due_today']}
- 平均掌握度: {stats['average_mastery']:.2f}/5.0

🎯 掌握程度分布
- 🌱 初学: {stats['mastery_distribution']['beginner']} 个
- 📖 学习中: {stats['mastery_distribution']['learning']} 个
- 💪 熟练: {stats['mastery_distribution'][' proficient']} 个
- 🏆 精通: {stats['mastery_distribution']['master']} 个

⏰ 今日待复习 ({len(due)} 项)
"""
        for item in due:
            topic = self.knowledge_base["topics"].get(item["topic_id"], {})
            report += f"\n  • {topic.get('name', 'Unknown')} ({item['interval']}天间隔)"
        
        report += "\n\n💡 建议: 定期复习是巩固知识的关键！"
        return report
    
    def create_review_card(self, topic_id):
        """创建复习卡片"""
        topic = self.knowledge_base["topics"].get(topic_id)
        if not topic:
            return None
        
        return f"""
┌─────────────────────────────┐
│ 🎓 复习卡片 #{topic_id[-3:]}          │
├─────────────────────────────┤
│ 主题: {topic['name']}             │
│ 类别: {topic['category']}                  │
│ 文件: {os.path.basename(topic['file_path'])}      │
│ 复习次数: {topic['review_count']}                 │
│ 掌握度: {'★' * int(topic['mastery_score'])}{'☆' * (5 - int(topic['mastery_score']))} {topic['mastery_score']:.1f}/5.0 │
└─────────────────────────────┘
"""


def demo():
    """演示"""
    print("🎓 智能代码复习助手 - 演示")
    print("=" * 50)
    
    reviewer = SmartCodeReviewer()
    
    # 添加一些示例主题
    reviewer.add_topic("快速排序算法", "scripts/2026-02-01_001_quick_sort.py", "算法")
    reviewer.add_topic("哈夫曼压缩", "scripts/2026-02-01_011_huffman_compression.py", "算法")
    reviewer.add_topic("密码生成器", "scripts/2026-02-01_004_password_generator.py", "工具")
    
    # 模拟复习
    print("\n📝 完成复习:")
    for topic_id in list(reviewer.knowledge_base["topics"].keys())[:2]:
        new_mastery = reviewer.complete_review(topic_id, understanding_level=4)
        topic = reviewer.knowledge_base["topics"][topic_id]
        print(f"  ✓ {topic['name']}: 掌握度 {new_mastery:.2f}")
    
    # 生成报告
    print("\n" + reviewer.generate_review_report())
    
    # 清理演示数据
    if os.path.exists("review_data.json"):
        os.remove("review_data.json")


if __name__ == "__main__":
    demo()
