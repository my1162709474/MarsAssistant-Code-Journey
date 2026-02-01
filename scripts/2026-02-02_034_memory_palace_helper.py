#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 智能记忆宫殿学习助手 (Memory Palace Learning Assistant)
基于记忆宫殿原理的智能学习工具 - Day 034

功能：
- 创建和管理记忆宫殿（虚拟空间）
- 将抽象知识转化为生动场景
- 间隔重复学习算法
- 智能复习提醒
- 可视化记忆路径
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


class MemoryPalace:
    """记忆宫殿管理类"""
    
    def __init__(self, name: str = "我的记忆宫殿"):
        self.name = name
        self.rooms: Dict[str, 'MemoryRoom'] = {}
        self.creation_date = datetime.now().isoformat()
        self.learning_stats = {
            "total_items": 0,
            "mastered_items": 0,
            "total_reviews": 0,
            "streak_days": 0
        }
    
    def add_room(self, room: 'MemoryRoom') -> bool:
        """添加记忆房间"""
        if room.name in self.rooms:
            return False
        self.rooms[room.name] = room
        return True
    
    def get_room(self, room_name: str) -> Optional['MemoryRoom']:
        """获取记忆房间"""
        return self.rooms.get(room_name)
    
    def get_all_items(self) -> List['MemoryItem']:
        """获取所有记忆项"""
        items = []
        for room in self.rooms.values():
            items.extend(room.items.values())
        return items
    
    def get_review_items(self, limit: int = 10) -> List[Tuple['MemoryItem', str]]:
        """获取需要复习的记忆项"""
        now = datetime.now()
        review_list = []
        for room in self.rooms.values():
            for item in room.items.values():
                next_review = item.next_review_date
                if next_review <= now.isoformat():
                    review_list.append((item, room.name))
        # 按优先级排序
        review_list.sort(key=lambda x: x[0].next_review_date)
        return review_list[:limit]


class MemoryRoom:
    """记忆房间类"""
    
    def __init__(self, name: str, description: str = "", location: str = "入口"):
        self.name = name
        self.description = description
        self.location = location  # 房间在宫殿中的位置
        self.items: Dict[str, 'MemoryItem'] = {}
        self.creation_date = datetime.now().isoformat()
    
    def add_item(self, item: 'MemoryItem') -> bool:
        """添加记忆项"""
        if item.keyword in self.items:
            return False
        self.items[item.keyword] = item
        return True
    
    def get_item(self, keyword: str) -> Optional['MemoryItem']:
        """获取记忆项"""
        return self.items.get(keyword)
    
    def search_items(self, query: str) -> List['MemoryItem']:
        """搜索记忆项"""
        results = []
        for item in self.items.values():
            if (query.lower() in item.keyword.lower() or 
                query.lower() in item.association.lower()):
                results.append(item)
        return results


class MemoryItem:
    """记忆项类"""
    
    def __init__(self, 
                 keyword: str,
                 association: str,
                 hint: str = "",
                 room_name: str = "",
                 visualization: str = ""):
        self.keyword = keyword
        self.association = association  # 记忆联想（故事/场景）
        self.hint = hint  # 记忆提示
        self.room_name = room_name
        self.visualization = visualization  # 可视化描述
        self.difficulty = 1  # 难度级别 1-5
        self.repetition = 0  # 复习次数
        self.ease_factor = 2.5  # 艾宾浩斯间隔重复参数
        self.interval = 1  # 间隔天数
        self.next_review_date = datetime.now().isoformat()
        self.creation_date = datetime.now().isoformat()
        self.last_reviewed = None
        self.is_mastered = False
    
    def review(self, quality: int = 3) -> Tuple[int, int]:
        """
        复习记忆项（基于SM-2算法）
        quality: 回忆质量 0-5
        返回: (新间隔天数, 累计复习次数)
        """
        if quality < 3:
            self.repetition = 0
            self.interval = 1
        else:
            if self.repetition == 0:
                self.interval = 1
            elif self.repetition == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            
            self.repetition += 1
        
        # 更新艾宾浩斯参数
        self.ease_factor = self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if self.ease_factor < 1.3:
            self.ease_factor = 1.3
        
        # 设置下次复习时间
        next_date = datetime.now() + timedelta(days=self.interval)
        self.next_review_date = next_date.isoformat()
        self.last_reviewed = datetime.now().isoformat()
        
        # 如果间隔超过30天，认为已经掌握
        if self.interval >= 30:
            self.is_mastered = True
        
        return self.interval, self.repetition


class MemoryPalaceHelper:
    """记忆宫殿助手主类"""
    
    def __init__(self, palace_name: str = "AI学习记忆宫殿"):
        self.palace = MemoryPalace(palace_name)
        self.presets = self._load_presets()
    
    def _load_presets(self) -> Dict[str, Dict]:
        """加载预设记忆场景"""
        return {
            "编程概念": {
                "房间": "数字塔楼",
                "位置": "宫殿入口左侧",
                "联想模板": {
                    "变量": "一个可以改变大小的魔法盒子",
                    "函数": "一个神奇的转换机器",
                    "循环": "一个永不停歇的旋转木马",
                    "条件判断": "一个智能的分岔路口",
                    "数组": "一排整齐的储物柜"
                }
            },
            "英语单词": {
                "房间": "语言图书馆",
                "位置": "宫殿二楼",
                "联想模板": {
                    "serendipity": "在古老图书馆发现隐藏宝藏的惊喜",
                    "ephemeral": "阳光下转眼即逝的肥皂泡",
                    "ubiquitous": "无处不在的小精灵",
                    "paradigm": "改变世界的思维眼镜"
                }
            },
            "历史事件": {
                "房间": "时光长廊",
                "位置": "宫殿主走廊",
                "联想模板": {
                    "文艺复兴": "佛罗伦萨街头艺术家们的狂欢节",
                    "工业革命": "烟雾缭绕中轰鸣的蒸汽机",
                    "二战": "世界各地和平鸽飞过废墟"
                }
            }
        }
    
    def create_preset_room(self, category: str, room_name: str = None) -> Optional[MemoryRoom]:
        """创建预设记忆房间"""
        if category not in self.presets:
            return None
        
        preset = self.presets[category]
        room = MemoryRoom(
            name=room_name or preset["房间"],
            description=f"学习{category}的记忆宫殿",
            location=preset["位置"]
        )
        self.palace.add_room(room)
        return room
    
    def add_memory_with_association(self, 
                                   keyword: str,
                                   association: str,
                                   category: str = "默认",
                                   hint: str = "",
                                   room_name: str = None) -> bool:
        """添加带联想的记忆"""
        # 确定房间
        room = None
        if room_name:
            room = self.palace.get_room(room_name)
        if not room:
            # 创建或获取类别房间
            room_name = room_name or category
            room = self.palace.get_room(room_name)
            if not room:
                room = MemoryRoom(room_name, description=f"{category}学习区")
                self.palace.add_room(room)
        
        # 创建记忆项
        item = MemoryItem(
            keyword=keyword,
            association=association,
            hint=hint,
            room_name=room.name
        )
        
        return room.add_item(item)
    
    def smart_review_session(self, num_items: int = 5) -> List[Dict]:
        """开始智能复习会话"""
        review_items = self.palace.get_review_items(num_items)
        results = []
        
        for item, room_name in review_items:
            result = {
                "keyword": item.keyword,
                "room": room_name,
                "association": item.association,
                "hint": item.hint,
                "times_reviewed": item.repetition,
                "interval": item.interval
            }
            results.append(result)
        
        return results
    
    def generate_memory_story(self, keywords: List[str]) -> str:
        """生成记忆故事（将多个关键词串联成故事）"""
        if not keywords:
            return ""
        
        items = []
        for keyword in keywords:
            for room in self.palace.rooms.values():
                item = room.get_item(keyword)
                if item:
                    items.append(item)
                    break
        
        if not items:
            return "未找到相关记忆项"
        
        # 生成故事
        story_parts = []
        for i, item in enumerate(items):
            part = f"{item.room_name}的{item.keyword}，它像{item.association}"
            if item.hint:
                part += f"（提示：{item.hint}）"
            story_parts.append(part)
        
        return " → ".join(story_parts)
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        stats = self.palace.learning_stats.copy()
        items = self.palace.get_all_items()
        
        stats["total_items"] = len(items)
        stats["mastered_items"] = sum(1 for item in items if item.is_mastered)
        stats["total_reviews"] = sum(item.repetition for item in items)
        
        # 计算掌握率
        if stats["total_items"] > 0:
            stats["mastery_rate"] = round(
                stats["mastered_items"] / stats["total_items"] * 100, 1
            )
        else:
            stats["mastery_rate"] = 0
        
        return stats
    
    def export_to_json(self, filepath: str = "memory_palace.json"):
        """导出记忆宫殿数据"""
        data = {
            "name": self.palace.name,
            "creation_date": self.palace.creation_date,
            "rooms": []
        }
        
        for room in self.palace.rooms.values():
            room_data = {
                "name": room.name,
                "description": room.description,
                "location": room.location,
                "items": []
            }
            for item in room.items.values():
                room_data["items"].append(asdict(item))
            data["rooms"].append(room_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def import_from_json(self, filepath: str) -> bool:
        """从JSON导入记忆宫殿"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.palace.name = data.get("name", self.palace.name)
            
            for room_data in data.get("rooms", []):
                room = MemoryRoom(
                    name=room_data["name"],
                    description=room_data.get("description", ""),
                    location=room_data.get("location", "")
                )
                self.palace.add_room(room)
                
                for item_data in room_data.get("items", []):
                    item = MemoryItem(
                        keyword=item_data["keyword"],
                        association=item_data["association"],
                        hint=item_data.get("hint", ""),
                        room_name=room.name
                    )
                    item.__dict__.update(item_data)
                    room.add_item(item)
            
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False


def demo():
    """演示记忆宫殿助手"""
    print("🎭 智能记忆宫殿学习助手 - 演示")
    print("=" * 50)
    
    # 初始化
    helper = MemoryPalaceHelper()
    
    # 创建预设房间
    helper.create_preset_room("编程概念", "编程概念屋")
    
    # 添加记忆项
    memories = [
        ("递归", "一只俄罗斯套娃，每个里面都藏着更小的自己", "像照镜子一样"),
        ("面向对象", "一个城市里有不同类型的机器人，各有专长", "类是蓝图"),
        ("API", "餐厅的服务员，负责顾客和厨房的沟通", "接口是合同"),
        ("数据库", "一个巨大的图书馆，每本书都有编号", "SQL是借书证"),
        ("算法", "菜谱的精确步骤，保证做出美味佳肴", "解决问题的配方")
    ]
    
    for keyword, association, hint in memories:
        helper.add_memory_with_association(
            keyword, association, "编程概念", hint, "编程概念屋"
        )
    
    print("\n📚 添加了5个编程概念记忆项")
    
    # 生成记忆故事
    keywords = ["递归", "面向对象", "API"]
    story = helper.generate_memory_story(keywords)
    print(f"\n📖 记忆故事: {story}")
    
    # 复习会话
    print("\n🔄 开始复习会话...")
    review_items = helper.smart_review_session(3)
    for item in review_items:
        print(f"  • {item['keyword']} ({item['room']}) - 已复习 {item['times_reviewed']} 次")
    
    # 学习统计
    stats = helper.get_learning_stats()
    print(f"\n📊 学习统计:")
    print(f"  • 总记忆项: {stats['total_items']}")
    print(f"  • 已掌握: {stats['mastered_items']}")
    print(f"  • 总复习次数: {stats['total_reviews']}")
    print(f"  • 掌握率: {stats['mastery_rate']}%")
    
    # 导出数据
    export_path = helper.export_to_json()
    print(f"\n💾 数据已导出到: {export_path}")
    
    print("\n✨ 演示完成！")


if __name__ == "__main__":
    demo()
