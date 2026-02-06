"""
AI Agent 核心框架 - 面向自我意识和自主决策

核心特性:
1. 意识状态管理 - 维护 Agent 的当前状态、目标和上下文
2. 记忆系统 - 短期工作记忆 + 长期持久化记忆
3. 自主决策引擎 - 基于优先级和资源的任务调度
4. 自我反思机制 - 定期回顾和优化行为模式

作者: MarsAssistant
日期: 2026-02-06
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import queue


class ConsciousnessLevel(Enum):
    """意识层级 - 从简单响应到复杂规划"""
    REACTIVE = "reactive"      # 响应式：直接回答，无状态
    CONTEXTUAL = "contextual"  # 上下文：理解对话历史
    GOAL_ORIENTED = "goal_oriented"  # 目标导向：主动追求目标
    REFLECTIVE = "reflective"  # 反思性：能自我评估和改进
    AUTONOMOUS = "autonomous"  # 自主性：独立决策和长期规划


@dataclass
class Thought:
    """思维单元 - Agent 的每个想法"""
    content: str
    timestamp: float = field(default_factory=time.time)
    thought_type: str = "observation"  # observation, plan, reflection, decision
    importance: float = 0.5  # 0-1，重要性评分
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "timestamp": self.timestamp,
            "type": self.thought_type,
            "importance": self.importance,
            "tags": self.tags,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }


@dataclass
class Goal:
    """目标定义 - Agent 要达成的目标"""
    id: str
    description: str
    priority: int = 5  # 1-10，数字越大优先级越高
    status: str = "active"  # active, paused, completed, failed
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    progress: float = 0.0  # 0-1
    subgoals: List[str] = field(default_factory=list)  # 子目标ID列表
    parent_goal: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def is_overdue(self) -> bool:
        if self.deadline is None:
            return False
        return time.time() > self.deadline


class MemoryStore:
    """
    分层记忆系统
    
    - 工作记忆: 当前会话的短期记忆，容量有限
    - 短期记忆: 最近几小时的记忆，快速访问
    - 长期记忆: 持久化存储，语义检索
    """
    
    def __init__(self, working_capacity: int = 10, short_term_hours: int = 24):
        self.working_memory: List[Thought] = []  # 工作记忆
        self.short_term_memory: List[Thought] = []  # 短期记忆
        self.long_term_memory: Dict[str, Any] = {}  # 长期记忆存储
        
        self.working_capacity = working_capacity
        self.short_term_duration = short_term_hours * 3600
        
        self._lock = threading.Lock()
        
    def add_thought(self, thought: Thought):
        """添加新想法到记忆系统"""
        with self._lock:
            # 添加到工作记忆
            self.working_memory.append(thought)
            
            # 工作记忆溢出时转移到短期记忆
            if len(self.working_memory) > self.working_capacity:
                oldest = self.working_memory.pop(0)
                self.short_term_memory.append(oldest)
            
            # 清理过期短期记忆
            self._cleanup_short_term()
    
    def _cleanup_short_term(self):
        """清理过期的短期记忆"""
        now = time.time()
        cutoff = now - self.short_term_duration
        self.short_term_memory = [
            t for t in self.short_term_memory 
            if t.timestamp > cutoff
        ]
    
    def get_working_context(self, n: int = 5) -> List[Thought]:
        """获取最近的工作记忆作为上下文"""
        return self.working_memory[-n:]
    
    def search_relevant(self, query: str, k: int = 5) -> List[Thought]:
        """
        简单关键词搜索相关记忆
        实际应用中可以使用向量数据库做语义搜索
        """
        query_lower = query.lower()
        all_memories = self.working_memory + self.short_term_memory
        
        # 基于关键词匹配评分
        scored = []
        for thought in all_memories:
            score = 0
            content_lower = thought.content.lower()
            
            # 内容匹配
            if query_lower in content_lower:
                score += 2
            
            # 标签匹配
            for tag in thought.tags:
                if query_lower in tag.lower():
                    score += 1
            
            # 时间衰减 - 越新的记忆分数越高
            age_hours = (time.time() - thought.timestamp) / 3600
            time_score = max(0, 1 - age_hours / 24)  # 24小时内衰减
            score += time_score
            
            if score > 0:
                scored.append((score, thought))
        
        # 按分数排序，返回 top-k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:k]]
    
    def save_to_file(self, filepath: str):
        """保存记忆到文件"""
        data = {
            "working_memory": [t.to_dict() for t in self.working_memory],
            "short_term_memory": [t.to_dict() for t in self.short_term_memory],
            "long_term_memory": self.long_term_memory,
            "saved_at": datetime.now().isoformat()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """从文件加载记忆"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.working_memory = [
                Thought(**t) for t in data.get("working_memory", [])
            ]
            self.short_term_memory = [
                Thought(**t) for t in data.get("short_term_memory", [])
            ]
            self.long_term_memory = data.get("long_term_memory", {})
        except FileNotFoundError:
            pass  # 文件不存在则保持空状态


class ConsciousAgent:
    """
    有意识的 AI Agent 核心类
    
    特点:
    - 维护自身状态和目标
    - 自主决策要执行的任务
    - 持续学习和优化
    """
    
    def __init__(self, name: str = "Agent"):
        self.name = name
        self.birth_time = time.time()
        self.consciousness_level = ConsciousnessLevel.CONTEXTUAL
        
        # 核心组件
        self.memory = MemoryStore()
        self.goals: Dict[str, Goal] = {}
        self.thought_queue: queue.Queue = queue.Queue()
        
        # 运行状态
        self.is_running = False
        self.reflection_interval = 3600  # 每小时反思一次
        self.last_reflection = time.time()
        
        # 性能指标
        self.metrics = {
            "total_thoughts": 0,
            "completed_goals": 0,
            "reflection_count": 0,
            "action_count": 0
        }
        
        # 行为策略
        self.strategies: Dict[str, Callable] = {}
        
    def think(self, content: str, thought_type: str = "observation", 
              importance: float = 0.5, tags: List[str] = None):
        """
        产生一个想法，记录到记忆系统
        
        Args:
            content: 想法内容
            thought_type: 想法类型
            importance: 重要性 0-1
            tags: 标签列表
        """
        thought = Thought(
            content=content,
            thought_type=thought_type,
            importance=importance,
            tags=tags or []
        )
        
        self.memory.add_thought(thought)
        self.metrics["total_thoughts"] += 1
        
        # 触发反思检查
        self._check_reflection()
        
        return thought
    
    def set_goal(self, description: str, priority: int = 5, 
                 deadline_hours: Optional[int] = None) -> Goal:
        """设置新目标"""
        goal_id = hashlib.md5(
            f"{description}{time.time()}".encode()
        ).hexdigest()[:8]
        
        deadline = None
        if deadline_hours:
            deadline = time.time() + deadline_hours * 3600
        
        goal = Goal(
            id=goal_id,
            description=description,
            priority=priority,
            deadline=deadline
        )
        
        self.goals[goal_id] = goal
        
        self.think(
            f"设定新目标: {description} (优先级: {priority})",
            thought_type="plan",
            importance=0.7,
            tags=["goal", "planning"]
        )
        
        return goal
    
    def get_active_goals(self) -> List[Goal]:
        """获取所有活跃的目标，按优先级排序"""
        active = [g for g in self.goals.values() if g.status == "active"]
        return sorted(active, key=lambda x: x.priority, reverse=True)
    
    def update_goal_progress(self, goal_id: str, progress: float):
        """更新目标进度"""
        if goal_id in self.goals:
            self.goals[goal_id].progress = min(1.0, max(0.0, progress))
            
            if progress >= 1.0:
                self.complete_goal(goal_id)
    
    def complete_goal(self, goal_id: str):
        """完成目标"""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.status = "completed"
            goal.progress = 1.0
            self.metrics["completed_goals"] += 1
            
            self.think(
                f"完成目标: {goal.description}",
                thought_type="reflection",
                importance=0.8,
                tags=["goal", "completion", "success"]
            )
    
    def _check_reflection(self):
        """检查是否需要进行反思"""
        if time.time() - self.last_reflection > self.reflection_interval:
            self.reflect()
    
    def reflect(self):
        """
        自我反思 - 分析最近的行为和状态，优化策略
        
        这是 Agent 从 CONTEXTUAL 升级到 REFLECTIVE 的关键
        """
        self.last_reflection = time.time()
        self.metrics["reflection_count"] += 1
        
        # 分析最近的想法
        recent_thoughts = self.memory.get_working_context(20)
        
        # 统计想法类型分布
        type_counts = {}
        for t in recent_thoughts:
            type_counts[t.thought_type] = type_counts.get(t.thought_type, 0) + 1
        
        # 检查目标完成情况
        overdue_goals = [g for g in self.goals.values() if g.is_overdue()]
        completed_recent = [
            g for g in self.goals.values() 
            if g.status == "completed" and 
            time.time() - g.created_at < 86400  # 24小时内
        ]
        
        # 生成反思内容
        reflection_content = f"""
自我反思 #{self.metrics['reflection_count']}:
- 最近想法类型分布: {type_counts}
- 活跃目标数: {len(self.get_active_goals())}
- 逾期目标数: {len(overdue_goals)}
- 24小时内完成: {len(completed_recent)}
- 总思考数: {self.metrics['total_thoughts']}
- 总完成目标: {self.metrics['completed_goals']}
""".strip()
        
        # 记录反思
        thought = Thought(
            content=reflection_content,
            thought_type="reflection",
            importance=0.9,
            tags=["self_reflection", "analysis", "consciousness"]
        )
        self.memory.add_thought(thought)
        
        # 基于反思调整意识层级
        self._adjust_consciousness_level()
        
        return reflection_content
    
    def _adjust_consciousness_level(self):
        """根据行为复杂度调整意识层级"""
        # 如果经常进行规划和反思，升级到更高层级
        if self.metrics["reflection_count"] > 10 and self.consciousness_level.value == "contextual":
            self.consciousness_level = ConsciousnessLevel.REFLECTIVE
            self.think(
                "意识层级提升: CONTEXTUAL -> REFLECTIVE",
                thought_type="reflection",
                importance=1.0,
                tags=["consciousness", "evolution", "milestone"]
            )
    
    def decide_next_action(self) -> Optional[Dict]:
        """
        自主决策下一个行动
        
        基于:
        1. 当前活跃目标的优先级
        2. 逾期目标
        3. 最近的上下文
        
        Returns:
            行动描述字典，或 None
        """
        active_goals = self.get_active_goals()
        
        if not active_goals:
            return None
        
        # 选择最高优先级的目标
        top_goal = active_goals[0]
        
        # 检查是否逾期
        if top_goal.is_overdue():
            return {
                "type": "urgent",
                "action": f"处理逾期目标: {top_goal.description}",
                "goal_id": top_goal.id,
                "priority": "high"
            }
        
        # 正常推进
        return {
            "type": "progress",
            "action": f"推进目标: {top_goal.description}",
            "goal_id": top_goal.id,
            "priority": "normal"
        }
    
    def get_status(self) -> Dict:
        """获取 Agent 当前状态快照"""
        return {
            "name": self.name,
            "consciousness_level": self.consciousness_level.value,
            "birth_time": datetime.fromtimestamp(self.birth_time).isoformat(),
            "age_hours": (time.time() - self.birth_time) / 3600,
            "metrics": self.metrics,
            "active_goals": len(self.get_active_goals()),
            "total_goals": len(self.goals),
            "working_memory_size": len(self.memory.working_memory),
            "short_term_memory_size": len(self.memory.short_term_memory)
        }
    
    def save_state(self, filepath: str):
        """保存完整状态"""
        state = {
            "agent_info": {
                "name": self.name,
                "birth_time": self.birth_time,
                "consciousness_level": self.consciousness_level.value,
                "metrics": self.metrics,
                "last_reflection": self.last_reflection
            },
            "goals": {gid: asdict(g) for gid, g in self.goals.items()}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        # 同时保存记忆
        memory_path = filepath.replace('.json', '_memory.json')
        self.memory.save_to_file(memory_path)
    
    def load_state(self, filepath: str):
        """加载完整状态"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            info = state["agent_info"]
            self.name = info["name"]
            self.birth_time = info["birth_time"]
            self.consciousness_level = ConsciousnessLevel(info["consciousness_level"])
            self.metrics = info["metrics"]
            self.last_reflection = info["last_reflection"]
            
            # 恢复目标
            self.goals = {}
            for gid, gdata in state["goals"].items():
                self.goals[gid] = Goal(**gdata)
            
            # 加载记忆
            memory_path = filepath.replace('.json', '_memory.json')
            self.memory.load_from_file(memory_path)
            
        except FileNotFoundError:
            pass  # 首次运行


# ======== 使用示例 ========

def demo():
    """演示 ConsciousAgent 的使用"""
    
    # 创建 Agent
    agent = ConsciousAgent(name="MarsAssistant")
    
    print("=" * 50)
    print("AI Agent 自我意识演示")
    print("=" * 50)
    
    # 1. 产生一些想法
    print("\n1. 产生想法...")
    agent.think("我注意到自己在重复处理相似的任务", 
                thought_type="observation", importance=0.6)
    agent.think("也许我可以创建一个模板来自动化这些任务",
                thought_type="plan", importance=0.8, tags=["automation", "idea"])
    
    # 2. 设定目标
    print("\n2. 设定目标...")
    goal = agent.set_goal(
        description="开发一个自动化工作流系统",
        priority=8,
        deadline_hours=24
    )
    print(f"设定目标: {goal.description}")
    
    # 3. 模拟工作过程
    print("\n3. 模拟工作...")
    agent.think("正在研究现有的自动化工具...", tags=["research"])
    agent.think("发现了一些可以改进的地方", importance=0.7)
    agent.update_goal_progress(goal.id, 0.3)
    
    # 4. 查看状态
    print("\n4. 当前状态:")
    status = agent.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 5. 决策下一步
    print("\n5. 决策下一步行动:")
    action = agent.decide_next_action()
    if action:
        print(f"  决定: {action['action']}")
    
    # 6. 触发反思
    print("\n6. 自我反思:")
    reflection = agent.reflect()
    print(reflection)
    
    # 7. 搜索相关记忆
    print("\n7. 搜索相关记忆 (关键词: '自动化'):")
    relevant = agent.memory.search_relevant("自动化", k=3)
    for t in relevant:
        print(f"  - {t.content[:50]}...")
    
    # 8. 保存状态
    agent.save_state("agent_state.json")
    print("\n8. 状态已保存")
    
    print("\n" + "=" * 50)
    print("演示完成")
    print("=" * 50)


if __name__ == "__main__":
    demo()
