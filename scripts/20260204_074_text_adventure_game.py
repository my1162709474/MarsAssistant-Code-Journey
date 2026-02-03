#!/usr/bin/env python3
"""
🎮 Text Adventure Game - 文字冒险游戏
=====================================
一个基于文本的互动冒险游戏，展示面向对象设计和游戏逻辑。

Day 74: Text Adventure Game - 文字冒险游戏

功能:
- 🔧 完整的游戏引擎 - 房间、物品、 NPC 交互
- 📊 状态管理系统 - 生命值、背包、任务进度
- 🏷️ 动态场景生成 - 可扩展的地图和故事
- 💾 游戏存档/读档 - 进度保存
- 🎯 多结局系统 - 根据选择影响故事走向

作者: AI Assistant
日期: 2026-02-04
"""

import json
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time


class ItemType(Enum):
    """物品类型枚举"""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    KEY = "key"
    TREASURE = "treasure"
    MISC = "misc"


class RoomType(Enum):
    """房间类型枚举"""
    START = "start"
    NORMAL = "normal"
    TREASURE = "treasure"
    DANGER = "danger"
    EXIT = "exit"
    SECRET = "secret"


@dataclass
class Item:
    """物品类"""
    id: str
    name: str
    description: str
    item_type: ItemType
    value: int = 0
    can_take: bool = True
    effect: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.item_type.value,
            "value": self.value,
            "can_take": self.can_take,
            "effect": self.effect
        }


@dataclass
class Room:
    """房间类"""
    id: str
    name: str
    description: str
    room_type: RoomType
    items: List[str] = field(default_factory=list)  # 物品ID列表
    enemies: List[str] = field(default_factory=list)  # 敌人ID列表
    exits: Dict[str, str] = field(default_factory=dict)  # 方向->房间ID
    is_locked: bool = False
    required_key: Optional[str] = None
    is_visited: bool = False
    story_text: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.room_type.value,
            "items": self.items,
            "exits": self.exits,
            "locked": self.is_locked,
            "key": self.required_key,
            "visited": self.is_visited
        }


@dataclass
class Enemy:
    """敌人类"""
    id: str
    name: str
    description: str
    health: int
    max_health: int
    damage: int
    reward_exp: int
    reward_gold: int = 0
    is_boss: bool = False
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "damage": self.damage,
            "exp": self.reward_exp,
            "gold": self.reward_gold,
            "boss": self.is_boss
        }


@dataclass
class Quest:
    """任务类"""
    id: str
    name: str
    description: str
    required_room: str
    required_item: Optional[str] = None
    required_enemy: Optional[str] = None
    reward_exp: int = 0
    reward_item: Optional[str] = None
    is_completed: bool = False
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "completed": self.is_completed,
            "reward_exp": self.reward_exp
        }


class Player:
    """玩家类"""
    
    def __init__(self, name: str = "Hero"):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 5
        self.gold = 0
        self.experience = 0
        self.level = 1
        self.inventory: List[str] = []  # 物品ID列表
        self.current_room = "start"
        self.completed_quests: List[str] = []
        self.attack_power = 10  # 基础攻击力
        self.defense_power = 5  # 基础防御力
    
    def add_item(self, item_id: str) -> bool:
        """添加物品到背包"""
        if item_id not in self.inventory:
            self.inventory.append(item_id)
            return True
        return False
    
    def remove_item(self, item_id: str) -> bool:
        """从背包移除物品"""
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False
    
    def has_item(self, item_id: str) -> bool:
        """检查是否拥有物品"""
        return item_id in self.inventory
    
    def take_damage(self, damage: int) -> int:
        """承受伤害"""
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """恢复生命"""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health
    
    def gain_exp(self, exp: int) -> bool:
        """获得经验值并检查升级"""
        self.experience += exp
        if self.experience >= self.level * 100:
            self.level += 1
            self.experience = 0
            self.max_health += 20
            self.health = self.max_health
            self.attack_power += 5
            self.defense_power += 3
            return True
        return False
    
    def equip_item(self, item: Item) -> bool:
        """装备物品"""
        if item.item_type == ItemType.WEAPON:
            self.attack_power = self.attack + item.value
            return True
        elif item.item_type == ItemType.ARMOR:
            self.defense_power = self.defense + item.value
            return True
        return False
    
    def use_potion(self, item: Item) -> bool:
        """使用药水"""
        if item.effect and "health" in item.effect:
            self.heal(item.effect["health"])
            return True
        return False
    
    def get_stats(self) -> str:
        """获取玩家状态"""
        return f"""
{'='*40}
🎖️  {self.name} - Level {self.level}
{'='*40}
❤️  生命值: {self.health}/{self.max_health}
⚔️  攻击力: {self.attack_power} (+{self.attack} 基础)
🛡️  防御力: {self.defense_power} (+{self.defense} 基础)
💰  金币: {self.gold}
✨  经验: {self.experience}/{self.level * 100}
🎒  背包: {len(self.inventory)} 个物品
📍  位置: {self.current_room}
{'='*40}
"""
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "level": self.level,
            "experience": self.experience,
            "gold": self.gold,
            "inventory": self.inventory,
            "current_room": self.current_room,
            "completed_quests": self.completed_quests
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        player = cls(data["name"])
        player.health = data["health"]
        player.max_health = data["max_health"]
        player.level = data["level"]
        player.experience = data["experience"]
        player.gold = data["gold"]
        player.inventory = data["inventory"]
        player.current_room = data["current_room"]
        player.completed_quests = data["completed_quests"]
        return player


class GameEngine:
    """游戏引擎"""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        self.enemies: Dict[str, Enemy] = {}
        self.quests: Dict[str, Quest] = {}
        self.player: Optional[Player] = None
        self.game_history: List[str] = []
        self.is_running = False
    
    def load_game_data(self, filename: str = "game_data.json"):
        """加载游戏数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._parse_game_data(data)
        except FileNotFoundError:
            self._create_default_game()
    
    def _parse_game_data(self, data: dict):
        """解析游戏数据"""
        # 解析物品
        for item_data in data.get("items", []):
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data["description"],
                item_type=ItemType(item_data["type"]),
                value=item_data.get("value", 0),
                can_take=item_data.get("can_take", True),
                effect=item_data.get("effect")
            )
            self.items[item.id] = item
        
        # 解析房间
        for room_data in data.get("rooms", []):
            room = Room(
                id=room_data["id"],
                name=room_data["name"],
                description=room_data["description"],
                room_type=RoomType(room_data["type"]),
                items=room_data.get("items", []),
                exits=room_data.get("exits", {}),
                is_locked=room_data.get("locked", False),
                required_key=room_data.get("key")
            )
            self.rooms[room.id] = room
        
        # 解析敌人
        for enemy_data in data.get("enemies", []):
            enemy = Enemy(
                id=enemy_data["id"],
                name=enemy_data["name"],
                description=enemy_data["description"],
                health=enemy_data["health"],
                max_health=enemy_data["health"],
                damage=enemy_data["damage"],
                reward_exp=enemy_data.get("exp", 0),
                reward_gold=enemy_data.get("gold", 0),
                is_boss=enemy_data.get("boss", False)
            )
            self.enemies[enemy.id] = enemy
    
    def _create_default_game(self):
        """创建默认游戏"""
        # 创建物品
        default_items = [
            Item("rusty_sword", "生锈的剑", "一把锈迹斑斑的剑,但仍能造成伤害", 
                 ItemType.WEAPON, value=5),
            Item("iron_sword", "铁剑", "一把锋利的铁剑", 
                 ItemType.WEAPON, value=15),
            Item("shield", "盾牌", "木质盾牌,提供基本防护", 
                 ItemType.ARMOR, value=8),
            Item("health_potion", "生命药水", "恢复50点生命值", 
                 ItemType.POTION, value=0, effect={"health": 50}),
            Item("golden_key", "金钥匙", "打开宝库的金色钥匙", 
                 ItemType.KEY, value=50),
            Item("treasure_chest", "宝箱", "内有珍贵宝物的箱子", 
                 ItemType.TREASURE, value=200, can_take=False),
            Item("treasure_map", "藏宝图", "标记着宝藏位置的地图", 
                 ItemType.MISC, value=25),
            Item("magic_ring", "魔法戒指", "提供额外防护的魔法戒指", 
                 ItemType.ARMOR, value=12),
            Item("dragon_scale", "龙鳞", "传说中的龙鳞", 
                 ItemType.TREASURE, value=100),
        ]
        for item in default_items:
            self.items[item.id] = item
        
        # 创建房间
        default_rooms = [
            Room("start", "起始大厅", "你站在一个昏暗的大厅入口", 
                 RoomType.START, 
                 exits={"north": "corridor", "east": "armory"}),
            Room("armory", "武器库", "墙上挂满了各种武器", 
                 RoomType.TREASURE,
                 items=["rusty_sword", "shield"],
                 exits={"west": "start"}),
            Room("corridor", "长廊", "一条长长的走廊,墙壁上刻着古老的符文", 
                 RoomType.NORMAL,
                 exits={"south": "start", "north": "throne_room", "east": "library"}),
            Room("library", "图书馆", "满是灰尘的书架和卷轴", 
                 RoomType.NORMAL,
                 items=["treasure_map", "health_potion"],
                 exits={"west": "corridor", "north": "secret_room"}),
            Room("secret_room", "密室", "一个隐藏的密室,空气中弥漫着魔法气息", 
                 RoomType.SECRET,
                 items=["magic_ring", "iron_sword"],
                 exits={"south": "library", "north": "treasure_room"}),
            Room("treasure_room", "宝库", "堆满金银财宝的房间", 
                 RoomType.TREASURE,
                 items=["golden_key", "dragon_scale"],
                 exits={"south": "secret_room"},
                 is_locked=True,
                 required_key="golden_key"),
            Room("throne_room", "王座室", "宏伟的王座室,尽头有一把空置的王座", 
                 RoomType.DANGER,
                 items=["treasure_chest"],
                 exits={"south": "corridor", "north": "boss_room"}),
            Room("boss_room", "龙穴", "一条巨龙在此守护", 
                 RoomType.DANGER,
                 enemies=["dragon"],
                 exits={"south": "throne_room"},
                 is_locked=True,
                 required_key="dragon_scale"),
            Room("victory", "胜利之门", "你成功击败了守护者!通往自由的大门就在眼前", 
                 RoomType.EXIT,
                 exits={}),
        ]
        for room in default_rooms:
            self.rooms[room.id] = room
        
        # 创建敌人
        default_enemies = [
            Enemy("goblin", "哥布林", "绿色的矮小生物", 
                  health=30, max_health=30, damage=8, 
                  reward_exp=20, reward_gold=10),
            Enemy("skeleton", "骷髅战士", "复活的古老战士", 
                  health=50, max_health=50, damage=12, 
                  reward_exp=30, reward_gold=15),
            Enemy("dragon", "远古巨龙", "守护宝藏的巨龙", 
                  health=200, max_health=200, damage=25, 
                  reward_exp=500, reward_gold=200, is_boss=True),
        ]
        for enemy in default_enemies:
            self.enemies[enemy.id] = enemy
    
    def start_game(self, player_name: str = "Hero"):
        """开始游戏"""
        self.player = Player(player_name)
        self.player.current_room = "start"
        self.is_running = True
        self._log(f"🎮 游戏开始! 欢迎, {player_name}!")
        self._log("输入 'help' 查看可用命令")
        self._show_current_room()
    
    def _log(self, message: str):
        """记录日志"""
        self.game_history.append(message)
        print(f"\n{message}")
    
    def _show_current_room(self):
        """显示当前房间信息"""
        if not self.player:
            return
        
        room = self.rooms.get(self.player.current_room)
        if not room:
            return
        
        room.is_visited = True
        
        print(f"\n{'='*60}")
        print(f"📍 {room.name}")
        print(f"{'='*60}")
        print(room.description)
        
        # 显示物品
        if room.items:
            visible_items = [self.items[i] for i in room.items 
                           if i in self.items and self.items[i].can_take]
            if visible_items:
                print("\n📦 可拾取物品:")
                for item in visible_items:
                    print(f"  • {item.name}: {item.description}")
        
        # 显示敌人
        if room.enemies:
            print("\n⚔️ 敌人:")
            for enemy_id in room.enemies:
                enemy = self.enemies.get(enemy_id)
                if enemy:
                    print(f"  • {enemy.name} (HP: {enemy.health}/{enemy.max_health})")
        
        # 显示出口
        print("\n🚪 出口:")
        for direction, room_id in room.exits.items():
            target_room = self.rooms.get(room_id)
            if target_room:
                status = "🔒 (已锁定)" if target_room.is_locked else ""
                print(f"  • {direction}: {target_room.name} {status}")
    
    def move(self, direction: str) -> bool:
        """移动到指定方向"""
        if not self.player:
            return False
        
        direction = direction.lower()
        room = self.rooms.get(self.player.current_room)
        
        if not room or direction not in room.exits:
            self._log("❌ 无法朝那个方向移动")
            return False
        
        target_room_id = room.exits[direction]
        target_room = self.rooms.get(target_room_id)
        
        if not target_room:
            return False
        
        # 检查是否锁定
        if target_room.is_locked:
            if target_room.required_key:
                if self.player.has_item(target_room.required_key):
                    self._log(f"🔑 你使用了{self.items[target_room.required_key].name}")
                    target_room.is_locked = False
                else:
                    self._log(f"❌ {target_room.name} 已锁定,需要特定钥匙")
                    return False
            else:
                self._log(f"❌ {target_room.name} 已锁定")
                return False
        
        self.player.current_room = target_room_id
        self._log(f"🚶 你向{direction}方移动...")
        self._show_current_room()
        return True
    
    def take_item(self, item_name: str) -> bool:
        """拾取物品"""
        if not self.player:
            return False
        
        room = self.rooms.get(self.player.current_room)
        if not room or not room.items:
            self._log("❌ 这里没有可拾取的物品")
            return False
        
        # 查找匹配的物品
        for item_id in room.items:
            item = self.items.get(item_id)
            if item and item.name == item_name and item.can_take:
                self.player.add_item(item_id)
                room.items.remove(item_id)
                self._log(f"✅ 你拾取了 {item.name}")
                return True
        
        self._log(f"❌ 未找到物品: {item_name}")
        return False
    
    def use_item(self, item_name: str) -> bool:
        """使用物品"""
        if not self.player:
            return False
        
        # 查找背包中的物品
        for item_id in self.player.inventory:
            item = self.items.get(item_id)
            if item and item.name == item_name:
                if item.item_type == ItemType.POTION:
                    if self.player.use_potion(item):
                        self._log(f"💊 你使用了 {item.name},恢复了50点生命值!")
                        self.player.remove_item(item_id)
                        return True
                elif item.item_type in [ItemType.WEAPON, ItemType.ARMOR]:
                    if self.player.equip_item(item):
                        self._log(f"⚔️ 你装备了 {item.name}")
                        return True
                else:
                    self._log(f"📦 {item.name}: {item.description}")
                    return True
        
        self._log(f"❌ 未找到物品: {item_name}")
        return False
    
    def show_inventory(self):
        """显示背包"""
        if not self.player:
            return
        
        print(f"\n{'='*40}")
        print("🎒 背包")
        print(f"{'='*40}")
        
        if not self.player.inventory:
            print("背包是空的")
            return
        
        for item_id in self.player.inventory:
            item = self.items.get(item_id)
            if item:
                print(f"  • {item.name}: {item.description}")
        
        print(f"\n💰 金币: {self.player.gold}")
    
    def attack_enemy(self, enemy_name: str) -> bool:
        """攻击敌人"""
        if not self.player:
            return False
        
        room = self.rooms.get(self.player.current_room)
        if not room or not room.enemies:
            self._log("❌ 这里没有敌人")
            return False
        
        # 查找敌人
        for enemy_id in room.enemies:
            enemy = self.enemies.get(enemy_id)
            if enemy and enemy.name == enemy_name:
                # 玩家攻击
                player_damage = random.randint(self.player.attack_power - 3, 
                                              self.player.attack_power + 3)
                enemy.health -= player_damage
                self._log(f"⚔️ 你对{enemy.name}造成了{player_damage}点伤害!")
                
                # 检查敌人是否死亡
                if enemy.health <= 0:
                    self._log(f"🎉 你击败了 {enemy.name}!")
                    self._log(f"✨ 获得 {enemy.reward_exp} 经验, {enemy.reward_gold} 金币")
                    self.player.gold += enemy.reward_gold
                    room.enemies.remove(enemy_id)
                    
                    # 检查升级
                    if self.player.gain_exp(enemy.reward_exp):
                        self._log("🎊 升级了!")
                    
                    # 检查是否是boss
                    if enemy.is_boss:
                        self._log("🐉 巨龙已除!前往龙穴的通道已经打开!")
                        throne_room = self.rooms.get("throne_room")
                        if throne_room:
                            throne_room.exits["north"] = "victory"
                    
                    return True
                
                # 敌人反击
                enemy_damage = random.randint(max(1, enemy.damage - 2), 
                                            enemy.damage + 2)
                actual_damage = self.player.take_damage(enemy_damage)
                self._log(f"💀 {enemy.name} 对你造成了 {actual_damage} 点伤害!")
                
                # 检查玩家是否死亡
                if self.player.health <= 0:
                    self._log("💀 你被击败了...游戏结束")
                    self.is_running = False
                    return False
                
                return True
        
        self._log(f"❌ 未找到敌人: {enemy_name}")
        return False
    
    def show_help(self):
        """显示帮助"""
        help_text = """
🎮 可用命令:
━━━━━━━━━━━━━━━
🚶 move <方向> - 移动 (north/south/east/west)
📦 take <物品名> - 拾取物品
📖 use <物品名> - 使用物品
⚔️ attack <敌人名> - 攻击敌人
🎒 inventory - 显示背包
📊 stats - 显示状态
📍 look - 查看当前房间
💾 save - 保存游戏
📜 history - 显示游戏历史
❓ help - 显示帮助
🚪 quit - 退出游戏
━━━━━━━━━━━━━━━
"""
        print(help_text)
    
    def save_game(self, filename: str = "savegame.json"):
        """保存游戏"""
        if not self.player:
            return False
        
        save_data = {
            "player": self.player.to_dict(),
            "rooms": {rid: r.to_dict() for rid, r in self.rooms.items()}
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            self._log(f"💾 游戏已保存到 {filename}")
            return True
        except Exception as e:
            self._log(f"❌ 保存失败: {e}")
            return False
    
    def load_game(self, filename: str = "savegame.json"):
        """加载游戏"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.player = Player.from_dict(save_data["player"])
            
            # 更新房间状态
            for rid, rdata in save_data.get("rooms", {}).items():
                if rid in self.rooms:
                    self.rooms[rid].is_visited = rdata.get("visited", False)
                    self.rooms[rid].is_locked = rdata.get("locked", True)
            
            self._log("📂 游戏已加载!")
            self._show_current_room()
            return True
        except FileNotFoundError:
            self._log("❌ 未找到存档文件")
            return False
        except Exception as e:
            self._log(f"❌ 加载失败: {e}")
            return False
    
    def process_command(self, command: str) -> bool:
        """处理玩家命令"""
        if not self.is_running:
            return False
        
        parts = command.strip().split()
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in ["n", "north", "s", "south", "e", "east", "w", "west"]:
            direction = {"n": "north", "s": "south", "e": "east", "w": "west"}.get(cmd, cmd)
            return self.move(direction)
        
        elif cmd in ["go", "move", "walk"]:
            if args:
                return self.move(args[0])
            else:
                self._log("❌ 请指定方向")
                return False
        
        elif cmd in ["take", "get", "pick"]:
            if args:
                item_name = " ".join(args)
                return self.take_item(item_name)
            else:
                self._log("❌ 请指定物品")
                return False
        
        elif cmd == "use":
            if args:
                item_name = " ".join(args)
                return self.use_item(item_name)
            else:
                self._log("❌ 请指定物品")
                return False
        
        elif cmd in ["attack", "fight", "hit"]:
            if args:
                enemy_name = " ".join(args)
                return self.attack_enemy(enemy_name)
            else:
                self._log("❌ 请指定敌人")
                return False
        
        elif cmd in ["inv", "inventory", "bag"]:
            self.show_inventory()
            return True
        
        elif cmd in ["stats", "status"]:
            print(self.player.get_stats())
            return True
        
        elif cmd in ["look", "l", "show"]:
            self._show_current_room()
            return True
        
        elif cmd in ["save"]:
            self.save_game()
            return True
        
        elif cmd in ["load"]:
            self.load_game()
            return True
        
        elif cmd in ["history", "log"]:
            print(f"\n游戏历史 (最近10条):")
            for msg in self.game_history[-10:]:
                print(f"  {msg}")
            return True
        
        elif cmd in ["help", "h", "?"]:
            self.show_help()
            return True
        
        elif cmd in ["quit", "exit", "q"]:
            self._log("👋 游戏结束,再见!")
            self.is_running = False
            return False
        
        else:
            self._log("❌ 未知命令,输入 'help' 查看帮助")
            return True
    
    def run(self):
        """运行游戏主循环"""
        if not self.player:
            self.start_game()
        
        while self.is_running:
            try:
                command = input("\n> ").strip()
                if command:
                    self.process_command(command)
                
                # 检查胜利条件
                if self.player and self.player.current_room == "victory":
                    self._log("\n" + "="*60)
                    self._log("🎊 恭喜!你成功通关了!")
                    self._log("="*60)
                    print(self.player.get_stats())
                    self.is_running = False
                
            except KeyboardInterrupt:
                self._log("\n\n👋 游戏被中断")
                break
            except EOFError:
                break


def create_demo_game():
    """创建演示游戏"""
    print("\n" + "="*60)
    print("🎮 Text Adventure Game - 文字冒险游戏演示")
    print("="*60 + "\n")
    
    engine = GameEngine()
    engine.load_game_data()
    
    print("📖 游戏预览:")
    print("-" * 40)
    print("创建了以下内容:")
    print(f"  • 房间: {len(engine.rooms)} 个")
    for rid, room in engine.rooms.items():
        print(f"    - {room.name}")
    print(f"  • 物品: {len(engine.items)} 个")
    for iid, item in engine.items.items():
        print(f"    - {item.name}")
    print(f"  • 敌人: {len(engine.enemies)} 个")
    for eid, enemy in engine.enemies.items():
        print(f"    - {enemy.name}")
    print("-" * 40)
    
    print("\n🚀 开始游戏? (输入 'start' 开始,或直接体验demo)")
    
    try:
        choice = input("> ").strip().lower()
        if choice == "start" or choice == "s":
            player_name = input("\n请输入你的名字: ").strip() or "Hero"
            engine.start_game(player_name)
            engine.run()
        else:
            # 展示游戏功能
            print("\n📦 展示物品系统...")
            engine.load_game_data()
            
            potion = engine.items.get("health_potion")
            sword = engine.items.get("iron_sword")
            
            if potion and sword:
                player = Player("Demo")
                player.add_item(potion.id)
                player.add_item(sword.id)
                
                print(f"\n玩家创建: {player.name}")
                print(player.get_stats())
                
                print(f"\n使用物品演示:")
                engine.player = player
                engine.use_item("生命药水")
                engine.use_item("铁剑")
                print(player.get_stats())
            
            print("\n✅ Demo 演示完成!")
    
    except KeyboardInterrupt:
        print("\n\n👋 演示结束")


if __name__ == "__main__":
    create_demo_game()
