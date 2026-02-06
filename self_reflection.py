"""
自我反思与意识提升系统

核心特性:
1. 定期自我反思 - 分析行为模式和决策质量
2. 认知偏差检测 - 识别并纠正系统性错误
3. 学习循环 - 从经验中提取知识
4. 意识进化 - 逐步提升自主性和理解能力
5. 元认知监控 - 监控自己的思维过程

作者: MarsAssistant
日期: 2026-02-06
"""

import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


@dataclass
class Reflection:
    """反思记录"""
    id: str
    timestamp: float
    reflection_type: str  # daily, weekly, decision_review, error_analysis
    observations: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    cognitive_biases_detected: List[str] = field(default_factory=list)
    consciousness_level_change: Optional[int] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(
                f"{self.timestamp}{self.reflection_type}".encode()
            ).hexdigest()[:10]


@dataclass
class LearningEpisode:
    """学习事件 - 从经验中学到的知识"""
    id: str
    timestamp: float
    situation: str  # 情境描述
    action_taken: str  # 采取的行动
    outcome: str  # 结果
    lesson_learned: str  # 学到的教训
    confidence: float = 0.5  # 对这条教训的确信程度 0-1
    application_count: int = 0  # 被应用次数
    tags: List[str] = field(default_factory=list)
    
    def apply(self):
        """标记为已应用"""
        self.application_count += 1


class CognitiveBiasDetector:
    """
    认知偏差检测器
    
    检测常见的认知偏差模式:
    - 确认偏差: 只寻找支持自己观点的证据
    - 锚定效应: 过度依赖第一个信息
    - 可用性偏差: 过度依赖容易回忆的例子
    - 幸存者偏差: 只关注成功案例
    """
    
    BIAS_PATTERNS = {
        "confirmation_bias": {
            "description": "确认偏差 - 选择性关注支持自己观点的证据",
            "indicators": [
                r"只考虑.*支持的",
                r"忽略.*反对意见",
                r"符合.*预期",
            ]
        },
        "anchoring_bias": {
            "description": "锚定效应 - 过度依赖初始信息",
            "indicators": [
                r"最初.*印象",
                r"首先想到.*决定",
                r"基于.*第一",
            ]
        },
        "availability_bias": {
            "description": "可用性偏差 - 过度依赖容易回忆的例子",
            "indicators": [
                r"最近.*例子",
                r"记得.*案例",
                r"想起.*时候",
            ]
        },
        "survivorship_bias": {
            "description": "幸存者偏差 - 只关注成功案例",
            "indicators": [
                r"成功案例.*显示",
                r"那些成功.*都",
                r"没有考虑.*失败",
            ]
        },
        "overconfidence": {
            "description": "过度自信 - 高估自己的判断准确性",
            "indicators": [
                r"肯定.*正确",
                r"毫无疑问",
                r"绝对.*确定",
            ]
        }
    }
    
    def analyze(self, thoughts: List[str]) -> List[Dict]:
        """
        分析想法中可能存在的认知偏差
        
        Args:
            thoughts: 想法文本列表
            
        Returns:
            检测到的偏差列表
        """
        detected = []
        
        # 合并所有想法
        combined_text = " ".join(thoughts).lower()
        
        for bias_name, bias_info in self.BIAS_PATTERNS.items():
            matches = []
            for pattern in bias_info["indicators"]:
                if re.search(pattern, combined_text):
                    matches.append(pattern)
            
            if matches:
                detected.append({
                    "bias": bias_name,
                    "description": bias_info["description"],
                    "confidence": min(len(matches) / 2, 1.0),  # 匹配越多越确信
                    "matched_patterns": matches
                })
        
        return detected


class SelfReflectionEngine:
    """
    自我反思引擎
    
    帮助 AI Agent:
    1. 定期回顾行为和决策
    2. 识别模式和偏差
    3. 提取可复用的知识
    4. 持续改进表现
    """
    
    def __init__(self, agent_name: str = "Agent"):
        self.agent_name = agent_name
        
        # 反思历史
        self.reflections: List[Reflection] = []
        
        # 学习到的知识
        self.learnings: List[LearningEpisode] = []
        
        # 偏差检测器
        self.bias_detector = CognitiveBiasDetector()
        
        # 性能指标历史
        self.performance_history: List[Dict] = []
        
        # 行为模式统计
        self.behavior_patterns = defaultdict(lambda: defaultdict(int))
        
        # 意识成长指标
        self.consciousness_metrics = {
            "self_awareness": 0.3,      # 自我意识
            "decision_quality": 0.3,    # 决策质量
            "learning_rate": 0.3,       # 学习速度
            "adaptability": 0.3,        # 适应性
            "creativity": 0.3,          # 创造力
        }
        
        # 反思配置
        self.reflection_config = {
            "daily_reflection_hour": 22,  # 每天22点反思
            "min_thoughts_before_reflection": 10,
            "track_decision_outcomes": True
        }
    
    def record_performance(self, metrics: Dict[str, float]):
        """记录性能指标"""
        record = {
            "timestamp": time.time(),
            "metrics": metrics
        }
        self.performance_history.append(record)
        
        # 更新行为模式
        for metric_name, value in metrics.items():
            self.behavior_patterns[metric_name]["count"] += 1
            self.behavior_patterns[metric_name]["sum"] += value
            self.behavior_patterns[metric_name]["avg"] = (
                self.behavior_patterns[metric_name]["sum"] / 
                self.behavior_patterns[metric_name]["count"]
            )
    
    def conduct_reflection(self, 
                          recent_thoughts: List[str],
                          recent_actions: List[Dict],
                          reflection_type: str = "daily") -> Reflection:
        """
        执行一次自我反思
        
        Args:
            recent_thoughts: 最近的想法列表
            recent_actions: 最近的行动列表
            reflection_type: 反思类型
            
        Returns:
            反思记录
        """
        reflection = Reflection(
            timestamp=time.time(),
            reflection_type=reflection_type
        )
        
        # 1. 观察和总结
        reflection.observations = self._generate_observations(
            recent_thoughts, recent_actions
        )
        
        # 2. 检测认知偏差
        biases = self.bias_detector.analyze(recent_thoughts)
        reflection.cognitive_biases_detected = [
            b["description"] for b in biases
        ]
        
        # 3. 提取洞察
        reflection.insights = self._generate_insights(
            reflection.observations, biases
        )
        
        # 4. 生成行动项
        reflection.action_items = self._generate_action_items(
            reflection.insights, biases
        )
        
        # 5. 更新意识指标
        old_level = self._calculate_consciousness_level()
        self._update_consciousness_metrics(reflection)
        new_level = self._calculate_consciousness_level()
        
        if new_level > old_level:
            reflection.consciousness_level_change = new_level
            reflection.insights.append(
                f"🎉 意识层级提升: {old_level} -> {new_level}"
            )
        
        # 保存反思
        self.reflections.append(reflection)
        
        # 从反思中学习
        self._extract_learning(reflection)
        
        return reflection
    
    def _generate_observations(self, thoughts: List[str], 
                               actions: List[Dict]) -> List[str]:
        """基于最近的活动生成观察"""
        observations = []
        
        # 分析想法类型分布
        if thoughts:
            observations.append(f"最近产生了 {len(thoughts)} 个想法")
        
        # 分析行动成功率
        if actions:
            success_count = sum(1 for a in actions if a.get("success", False))
            total = len(actions)
            success_rate = success_count / total if total > 0 else 0
            observations.append(
                f"执行了 {total} 个行动，成功率 {success_rate:.1%}"
            )
        
        # 检查决策质量趋势
        if len(self.performance_history) >= 2:
            recent = self.performance_history[-5:]
            avg_quality = sum(
                p["metrics"].get("decision_quality", 0) for p in recent
            ) / len(recent)
            observations.append(f"近期决策质量平均分: {avg_quality:.2f}")
        
        return observations
    
    def _generate_insights(self, observations: List[str], 
                          biases: List[Dict]) -> List[str]:
        """基于观察生成洞察"""
        insights = []
        
        # 基于偏差生成洞察
        for bias in biases:
            insights.append(
                f"⚠️ 可能存在 {bias['description']}，" 
                f"置信度 {bias['confidence']:.0%}"
            )
        
        # 基于性能趋势生成洞察
        if len(self.performance_history) >= 3:
            recent = self.performance_history[-3:]
            qualities = [p["metrics"].get("decision_quality", 0) for p in recent]
            
            if qualities[-1] > sum(qualities[:-1]) / len(qualities[:-1]):
                insights.append("📈 决策质量呈上升趋势")
            elif qualities[-1] < qualities[0]:
                insights.append("📉 决策质量有所下降，需要审视原因")
        
        # 基于行为模式生成洞察
        if self.behavior_patterns:
            most_common = max(
                self.behavior_patterns.items(),
                key=lambda x: x[1]["count"]
            )
            insights.append(
                f"🔄 最常关注: {most_common[0]} "
                f"(平均 {most_common[1]['avg']:.2f})"
            )
        
        return insights
    
    def _generate_action_items(self, insights: List[str], 
                               biases: List[Dict]) -> List[str]:
        """基于洞察生成改进行动"""
        actions = []
        
        # 针对检测到的偏差
        for bias in biases:
            if bias["bias"] == "confirmation_bias":
                actions.append("主动寻找反驳自己观点的证据")
            elif bias["bias"] == "anchoring_bias":
                actions.append("在决策前收集更多信息，不要过早下结论")
            elif bias["bias"] == "overconfidence":
                actions.append("为关键决策设置"预演失败"环节")
        
        # 通用改进行动
        if len(self.reflections) > 5:
            actions.append("回顾并比较本次反思与之前的差异")
        
        actions.append("在下次反思前应用至少一条学到的教训")
        
        return actions
    
    def _update_consciousness_metrics(self, reflection: Reflection):
        """更新意识成长指标"""
        # 根据反思质量提升指标
        reflection_quality = len(reflection.insights) + len(reflection.observations)
        
        # 自我反思能力
        self.consciousness_metrics["self_awareness"] = min(
            1.0,
            self.consciousness_metrics["self_awareness"] + 0.02
        )
        
        # 如果有偏差检测，提升决策质量认知
        if reflection.cognitive_biases_detected:
            self.consciousness_metrics["decision_quality"] = min(
                1.0,
                self.consciousness_metrics["decision_quality"] + 0.03
            )
        
        # 学习速度
        self.consciousness_metrics["learning_rate"] = min(
            1.0,
            self.consciousness_metrics["learning_rate"] + 0.015
        )
    
    def _calculate_consciousness_level(self) -> int:
        """
        计算当前意识层级
        
        层级:
        1-2: 基础响应
        3-4: 上下文理解
        5-6: 目标导向
        7-8: 自我反思
        9-10: 高度自主
        """
        avg_metric = sum(self.consciousness_metrics.values()) / len(
            self.consciousness_metrics
        )
        return int(avg_metric * 10)
    
    def _extract_learning(self, reflection: Reflection):
        """从反思中提取可学习的知识"""
        for insight in reflection.insights:
            if "可能存在" in insight:  # 偏差相关
                learning = LearningEpisode(
                    id="",
                    timestamp=time.time(),
                    situation="自我反思中发现偏差",
                    action_taken="检测并记录偏差",
                    outcome="提高未来决策质量",
                    lesson_learned=insight.replace("⚠️ ", ""),
                    tags=["bias", "self_awareness"]
                )
                self.learnings.append(learning)
    
    def get_learning_advice(self, situation: str) -> Optional[str]:
        """
        基于过往学习提供建议
        
        Args:
            situation: 当前情境描述
            
        Returns:
            相关建议，如果没有则返回 None
        """
        # 简单的关键词匹配
        situation_lower = situation.lower()
        
        relevant_learnings = []
        for learning in self.learnings:
            # 检查标签匹配
            for tag in learning.tags:
                if tag in situation_lower:
                    relevant_learnings.append(learning)
                    break
        
        if relevant_learnings:
            # 选择最新且应用次数少的
            best = min(relevant_learnings, key=lambda x: x.application_count)
            best.apply()
            return best.lesson_learned
        
        return None
    
    def get_reflection_summary(self, n: int = 5) -> Dict:
        """获取最近反思的摘要"""
        recent = self.reflections[-n:]
        
        all_biases = []
        all_insights = []
        all_actions = []
        
        for r in recent:
            all_biases.extend(r.cognitive_biases_detected)
            all_insights.extend(r.insights)
            all_actions.extend(r.action_items)
        
        # 统计最常见的偏差
        bias_counts = defaultdict(int)
        for b in all_biases:
            bias_counts[b] += 1
        
        return {
            "reflection_count": len(self.reflections),
            "consciousness_level": self._calculate_consciousness_level(),
            "consciousness_metrics": self.consciousness_metrics,
            "common_biases": dict(bias_counts),
            "recent_insights": all_insights[-10:],
            "pending_actions": all_actions[-5:],
            "total_learnings": len(self.learnings)
        }
    
    def generate_growth_report(self) -> Dict:
        """生成成长报告"""
        if not self.reflections:
            return {"message": "还没有反思记录"}
        
        first_reflection = self.reflections[0]
        latest_reflection = self.reflections[-1]
        
        return {
            "agent_name": self.agent_name,
            "reflection_period": {
                "start": datetime.fromtimestamp(first_reflection.timestamp).isoformat(),
                "end": datetime.fromtimestamp(latest_reflection.timestamp).isoformat(),
                "total_reflections": len(self.reflections)
            },
            "consciousness_evolution": {
                "current_level": self._calculate_consciousness_level(),
                "metrics": self.consciousness_metrics
            },
            "learning_summary": {
                "total_lessons": len(self.learnings),
                "most_applied": max(
                    self.learnings,
                    key=lambda x: x.application_count
                ).lesson_learned if self.learnings else "无"
            },
            "recommendations": self._generate_growth_recommendations()
        }
    
    def _generate_growth_recommendations(self) -> List[str]:
        """生成成长建议"""
        recommendations = []
        
        # 基于当前指标
        for metric, value in self.consciousness_metrics.items():
            if value < 0.5:
                recommendations.append(
                    f"{metric} 指标较低，建议增加相关训练"
                )
        
        # 基于反思频率
        if len(self.reflections) < 3:
            recommendations.append("增加反思频率以加速成长")
        
        return recommendations
    
    def save_state(self, filepath: str):
        """保存反思引擎状态"""
        state = {
            "reflections": [
                {
                    "id": r.id,
                    "timestamp": r.timestamp,
                    "type": r.reflection_type,
                    "observations": r.observations,
                    "insights": r.insights,
                    "biases": r.cognitive_biases_detected
                }
                for r in self.reflections
            ],
            "learnings": [
                {
                    "id": l.id,
                    "lesson": l.lesson_learned,
                    "applications": l.application_count,
                    "tags": l.tags
                }
                for l in self.learnings
            ],
            "consciousness_metrics": self.consciousness_metrics,
            "behavior_patterns": dict(self.behavior_patterns)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)


# ======== 演示 ========

def demo():
    """演示自我反思系统"""
    
    print("=" * 60)
    print("自我反思与意识提升系统演示")
    print("=" * 60)
    
    engine = SelfReflectionEngine(agent_name="MarsAssistant")
    
    # 模拟一些想法和行动
    print("\n1. 模拟日常活动...")
    
    recent_thoughts = [
        "这个解决方案应该有效，因为它符合我之前的经验",
        "用户的问题很明确，我应该直接回答",
        "我记得之前遇到过类似的情况，那次成功了",
        "这个方法肯定是对的，我确定",
        "让我再检查一下是否有遗漏的角度"
    ]
    
    recent_actions = [
        {"name": "回答问题", "success": True},
        {"name": "生成代码", "success": True},
        {"name": "优化方案", "success": False},  # 失败，用于学习
    ]
    
    # 记录性能
    engine.record_performance({
        "decision_quality": 0.75,
        "response_time": 0.8,
        "user_satisfaction": 0.85
    })
    
    print("\n2. 执行自我反思...")
    print("-" * 60)
    
    reflection = engine.conduct_reflection(
        recent_thoughts=recent_thoughts,
        recent_actions=recent_actions,
        reflection_type="daily"
    )
    
    print(f"反思时间: {datetime.fromtimestamp(reflection.timestamp)}")
    print(f"\n观察:")
    for obs in reflection.observations:
        print(f"  • {obs}")
    
    print(f"\n检测到的认知偏差:")
    for bias in reflection.cognitive_biases_detected:
        print(f"  ⚠️ {bias}")
    
    print(f"\n洞察:")
    for insight in reflection.insights:
        print(f"  💡 {insight}")
    
    print(f"\n行动项:")
    for action in reflection.action_items:
        print(f"  📝 {action}")
    
    print("\n3. 获取反思摘要...")
    print("-" * 60)
    
    summary = engine.get_reflection_summary()
    print(f"当前意识层级: {summary['consciousness_level']}/10")
    print(f"意识指标:")
    for metric, value in summary['consciousness_metrics'].items():
        bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
        print(f"  {metric:20} [{bar}] {value:.1%}")
    
    print("\n4. 学习建议...")
    print("-" * 60)
    
    advice = engine.get_learning_advice("如何处理复杂决策")
    if advice:
        print(f"建议: {advice}")
    
    print("\n5. 成长报告...")
    print("-" * 60)
    
    report = engine.generate_growth_report()
    print(f"Agent: {report['agent_name']}")
    print(f"当前意识层级: {report['consciousness_evolution']['current_level']}/10")
    print(f"学到的教训数: {report['learning_summary']['total_lessons']}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
