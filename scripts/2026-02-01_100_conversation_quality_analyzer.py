#!/usr/bin/env python3
"""
AI Conversation Quality Analyzer
分析对话质量、完整性和有效性
"""

import re
import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class ConversationAnalyzer:
    """对话质量分析器"""
    
    def __init__(self):
        self.metrics = {
            'clarity_score': 0,
            'completeness_score': 0,
            'engagement_score': 0,
            'efficiency_score': 0
        }
        
    def analyze_conversation(self, messages: List[Dict]) -> Dict:
        """
        分析整个对话
        
        Args:
            messages: 消息列表 [{'role': 'user'|'assistant', 'content': '...'}]
            
        Returns:
            分析结果字典
        """
        if not messages:
            return {'error': 'No messages to analyze'}
            
        analysis = {
            'total_messages': len(messages),
            'user_messages': 0,
            'assistant_messages': 0,
            'avg_response_length': 0,
            'questions_asked': 0,
            'clarity_score': 0,
            'completeness_score': 0,
            'engagement_score': 0,
            'efficiency_score': 0,
            'suggestions': []
        }
        
        # 统计消息数量
        for msg in messages:
            role = msg.get('role', '').lower()
            if 'user' in role:
                analysis['user_messages'] += 1
            elif 'assistant' in role:
                analysis['assistant_messages'] += 1
                
        # 分析清晰度
        analysis['clarity_score'] = self._calculate_clarity(messages)
        
        # 分析完整性
        analysis['completeness_score'] = self._calculate_completeness(messages)
        
        # 分析参与度
        analysis['engagement_score'] = self._calculate_engagement(messages)
        
        # 分析效率
        analysis['efficiency_score'] = self._calculate_efficiency(messages)
        
        # 生成建议
        analysis['suggestions'] = self._generate_suggestions(analysis)
        
        return analysis
    
    def _calculate_clarity(self, messages: List[Dict]) -> float:
        """计算清晰度分数 (0-100)"""
        clarity_scores = []
        
        for msg in messages:
            content = msg.get('content', '')
            score = 50  # 基础分数
            
            # 长度适中 (+/-)
            word_count = len(content.split())
            if 10 <= word_count <= 200:
                score += 20
            elif word_count < 10:
                score -= 10
            elif word_count > 500:
                score -= 15
            
            # 包含具体信息
            if any(keyword in content.lower() for keyword in 
                   ['具体', '详细', '例子', '例如', '具体来说']):
                score += 15
                
            # 有明确的目标
            if any(keyword in content.lower() for keyword in 
                   ['帮我', '请', '需要', '想要', '希望']):
                score += 10
                
            # 避免模糊
           模糊词 = ['那个', '某些', '大概', '也许', '可能']
            if any(word in content for word in 模糊词):
                score -= 10
                
            clarity_scores.append(min(100, max(0, score)))
            
        return round(sum(clarity_scores) / len(clarity_scores), 2) if clarity_scores else 0
    
    def _calculate_completeness(self, messages: List[Dict]) -> float:
        """计算完整性分数 (0-100)"""
        if len(messages) < 2:
            return 50
            
        scores = []
        
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            
            if 'user' in prev_msg.get('role', '').lower():
                # 检查助手是否回答了问题
                user_content = prev_msg.get('content', '')
                assistant_content = curr_msg.get('content', '')
                
                # 检测问号
                has_question = '？' in user_content or '?' in user_content
                
                if has_question:
                    # 回答长度
                    if len(assistant_content) > 50:
                        scores.append(80)
                    elif len(assistant_content) > 20:
                        scores.append(60)
                    else:
                        scores.append(30)
                else:
                    scores.append(70)  # 没有问题，假设完整
            
            # 检查多轮对话的连贯性
            if i >= 2 and 'assistant' in prev_msg.get('role', '').lower():
                # 助手是否引用了之前的上下文
                if len(curr_msg.get('content', '')) > 50:
                    scores.append(75)
                    
        return round(sum(scores) / len(scores), 2) if scores else 50
    
    def _calculate_engagement(self, messages: List[Dict]) -> float:
        """计算参与度分数 (0-100)"""
        if len(messages) < 2:
            return 50
            
        # 计算对话轮数
        rounds = len([i for i in range(1, len(messages)) 
                     if 'user' in messages[i].get('role', '').lower()])
        
        # 基础分数
        score = min(100, rounds * 10 + 30)
        
        # 检查是否有后续问题
        for msg in messages:
            content = msg.get('content', '')
            if '?' in content or '？' in content:
                score += 5
                
        # 检查是否有互动
        if len(messages) > 3:
            score += 15
            
        return min(100, score)
    
    def _calculate_efficiency(self, messages: List[Dict]) -> float:
        """计算效率分数 (0-100)"""
        if len(messages) < 2:
            return 50
            
        # 理想情况下，问题应该被一次回答解决
        user_msgs = [m for m in messages if 'user' in m.get('role', '').lower()]
        assistant_msgs = [m for m in messages if 'assistant' in m.get('role', '').lower()]
        
        if not user_msgs or not assistant_msgs:
            return 50
            
        ratio = len(assistant_msgs) / len(user_msgs)
        
        # 效率在1.0-2.0之间为最佳
        if 0.8 <= ratio <= 1.5:
            score = 85
        elif 1.5 < ratio <= 3:
            score = 70
        elif ratio > 3:
            score = 50
        else:
            score = 70
            
        return score
    
    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if analysis['clarity_score'] < 60:
            suggestions.append('尝试更清楚地描述你的需求，包括具体细节和期望结果')
            
        if analysis['completeness_score'] < 60:
            suggestions.append('确保每个问题都有完整的上下文信息')
            
        if analysis['engagement_score'] < 60:
            suggestions.append('可以尝试多轮对话，深入探讨问题')
            
        if analysis['efficiency_score'] < 60:
            suggestions.append('尝试一次表达完整需求，减少来回沟通')
            
        if not suggestions:
            suggestions.append('对话质量很好！继续保持')
            
        return suggestions
    
    def print_report(self, analysis: Dict) -> str:
        """生成格式化的报告"""
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           AI Conversation Quality Report                  ║
╠══════════════════════════════════════════════════════════╣
║  📊 总消息数: {analysis['total_messages']:<28} ║
║  👤 用户消息: {analysis['user_messages']:<28} ║
║  🤖 助手消息: {analysis['assistant_messages']:<28} ║
╠══════════════════════════════════════════════════════════╣
║  📈 质量评分                                              ║
║  ├─ 清晰度:    {analysis['clarity_score']}/100                      ║
║  ├─ 完整性:    {analysis['completeness_score']}/100                      ║
║  ├─ 参与度:    {analysis['engagement_score']}/100                      ║
║  └─ 效率:      {analysis['efficiency_score']}/100                      ║
╠══════════════════════════════════════════════════════════╣
║  💡 改进建议                                              ║
"""
        for i, suggestion in enumerate(analysis['suggestions'], 1):
            report += f"║  {i}. {suggestion:<46} ║\n"
            
        report += "╚══════════════════════════════════════════════════════════╝"
        return report


def demo():
    """演示用例"""
    # 示例对话
    conversation = [
        {'role': 'user', 'content': '帮我写一个排序算法，具体来说是快速排序，需要Python实现'},
        {'role': 'assistant', 'content': '当然可以！以下是Python实现的快速排序算法：\n\n```python\ndef quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)\n\n# 测试\nprint(quicksort([3,6,8,10,1,2,1]))  # 输出: [1, 1, 2, 3, 6, 8, 10]\n```'},
        {'role': 'user', 'content': '能解释一下时间复杂度吗？还有，平均情况和最坏情况有什么区别？'},
        {'role': 'assistant', 'content': '## 时间复杂度分析\n\n### 快速排序时间复杂度：\n- **平均情况**: O(n log n) - 大多数情况下表现很好\n- **最坏情况**: O(n²) - 当数组已经有序或逆序时\n\n### 为什么平均情况是O(n log n)？\n因为理想情况下，每次都能选到中间大小的元素作为基准，将数组均匀分成两半。\n\n### 优化建议：\n1. 随机打乱数组\n2. 使用三数取中法选择基准'},
        {'role': 'user', 'content': '谢谢！我还想知道如何处理包含重复元素的情况'},
    ]
    
    analyzer = ConversationAnalyzer()
    analysis = analyzer.analyze_conversation(conversation)
    print(analyzer.print_report(analysis))


if __name__ == '__main__':
    demo()
