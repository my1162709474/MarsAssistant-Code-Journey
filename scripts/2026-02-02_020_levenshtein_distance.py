#!/usr/bin/env python3
"""
字符串编辑距离计算器 (Levenshtein Distance)
============================================

Day 20: 智能文本相似度工具

功能：
- 计算两个字符串之间的最小编辑距离
- 支持三种操作：插入、删除、替换
- 支持中文、英文、数字混合文本
- 返回详细的操作步骤
- 可视化对齐结果

编辑距离应用场景：
- 拼写检查
- 文本相似度比较
- DNA序列比对
- 抄袭检测
- 模糊搜索

作者: MarsAssistant
日期: 2026-02-02
"""

from typing import List, Tuple, Dict
import json


class LevenshteinDistance:
    """编辑距离计算器类"""
    
    def __init__(self):
        """初始化计算器"""
        self.distance = 0
        self.operations = []
    
    def compute(self, s1: str, s2: str, show_steps: bool = False) -> int:
        """
        计算两个字符串之间的编辑距离
        
        Args:
            s1: 源字符串
            s2: 目标字符串
            show_steps: 是否显示操作步骤
            
        Returns:
            int: 编辑距离
        """
        m, n = len(s1), len(s2)
        
        # 创建DP表
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # 初始化边界
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # 填充DP表
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],      # 删除
                        dp[i][j-1],      # 插入
                        dp[i-1][j-1]     # 替换
                    )
        
        self.distance = dp[m][n]
        
        if show_steps:
            self.operations = self._traceback(s1, s2, dp)
        
        return self.distance
    
    def _traceback(self, s1: str, s2: str, dp: List[List[int]]) -> List[Dict]:
        """回溯找到编辑操作步骤"""
        operations = []
        m, n = len(s1), len(s2)
        
        while m > 0 or n > 0:
            if m > 0 and n > 0 and s1[m-1] == s2[n-1]:
                m -= 1
                n -= 1
            elif m > 0 and dp[m][n] == dp[m-1][n] + 1:
                operations.append({
                    'op': 'DELETE',
                    'char': s1[m-1],
                    'pos': m-1,
                    'desc': f"删除字符 '{s1[m-1]}'"
                })
                m -= 1
            elif n > 0 and dp[m][n] == dp[m][n-1] + 1:
                operations.append({
                    'op': 'INSERT',
                    'char': s2[n-1],
                    'pos': m,
                    'desc': f"插入字符 '{s2[n-1]}'"
                })
                n -= 1
            elif m > 0 and n > 0:
                operations.append({
                    'op': 'REPLACE',
                    'from': s1[m-1],
                    'to': s2[n-1],
                    'pos': m-1,
                    'desc': f"替换字符 '{s1[m-1]}' -> '{s2[n-1]}'"
                })
                m -= 1
                n -= 1
        
        operations.reverse()
        return operations
    
    def similarity(self, s1: str, s2: str) -> float:
        """
        计算相似度百分比
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            float: 相似度 (0-100)
        """
        self.compute(s1, s2)
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 100.0
        return (1 - self.distance / max_len) * 100
    
    def get_alignment(self, s1: str, s2: str) -> Tuple[str, str]:
        """
        获取两个字符串的对齐结果
        
        Args:
            s1: 源字符串
            s2: 目标字符串
            
        Returns:
            Tuple[str, str]: 对齐后的两个字符串
        """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        # 回溯构建对齐
        aligned1, aligned2 = [], []
        i, j = m, n
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and s1[i-1] == s2[j-1]:
                aligned1.append(s1[i-1])
                aligned2.append(s2[j-1])
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
                aligned1.append(s1[i-1])
                aligned2.append('*')
                i -= 1
            elif j > 0:
                aligned1.append('*')
                aligned2.append(s2[j-1])
                j -= 1
            elif i > 0:
                aligned1.append(s1[i-1])
                aligned2.append('*')
                i -= 1
        
        return ''.join(reversed(aligned1)), ''.join(reversed(aligned2))


def demo():
    """演示编辑距离计算器的使用"""
    print("=" * 60)
    print("字符串编辑距离计算器 (Levenshtein Distance)")
    print("Day 20: 智能文本相似度工具")
    print("=" * 60)
    
    calculator = LevenshteinDistance()
    
    # 测试用例1: 简单拼写检查
    print("\n【测试1: 拼写检查】")
    word1 = "kitten"
    word2 = "sitting"
    distance = calculator.compute(word1, word2, show_steps=True)
    similarity = calculator.similarity(word1, word2)
    print(f"  '{word1}' -> '{word2}'")
    print(f"  编辑距离: {distance}")
    print(f"  相似度: {similarity:.1f}%")
    print(f"  操作步骤:")
    for op in calculator.operations[:5]:
        print(f"    - {op['desc']}")
    
    # 测试用例2: 中文文本
    print("\n【测试2: 中文文本相似度】")
    chinese1 = "今天天气真好"
    chinese2 = "今天天气不错"
    distance = calculator.compute(chinese1, chinese2, show_steps=True)
    similarity = calculator.similarity(chinese1, chinese2)
    print(f"  '{chinese1}'")
    print(f"  '{chinese2}'")
    print(f"  编辑距离: {distance}")
    print(f"  相似度: {similarity:.1f}%")
    
    # 测试用例3: 模糊搜索匹配
    print("\n【测试3: 模糊搜索】")
    query = "pythn"
    targets = ["python", "pyton", "pythno", "python3", "pyhont"]
    print(f"  查询词: '{query}'")
    print(f"  匹配结果:")
    for target in targets:
        dist = calculator.compute(query, target)
        sim = calculator.similarity(query, target)
        print(f"    '{target}': 距离={dist}, 相似度={sim:.1f}%")
    
    # 测试用例4: 智能纠错建议
    print("\n【测试4: 拼写纠错】")
    misspelled = "accomodate"
    corrections = ["accommodate", "accomodate", "accommodation"]
    print(f"  错误拼写: '{misspelled}'")
    print(f"  建议纠正:")
    for correction in corrections:
        dist = calculator.compute(misspelled, correction)
        sim = calculator.similarity(misspelled, correction)
        print(f"    '{correction}': 距离={dist}, 相似度={sim:.1f}%")
    
    # 测试用例5: 对齐可视化
    print("\n【测试5: 对齐可视化】")
    s1, s2 = "saturday", "sunday"
    aligned1, aligned2 = calculator.get_alignment(s1, s2)
    print(f"  字符串1: {s1}")
    print(f"  字符串2: {s2}")
    print(f"  对齐结果:")
    print(f"    {aligned1}")
    print(f"    {aligned2}")
    
    # 性能测试
    print("\n【性能测试】")
    import time
    test_cases = [
        ("a" * 100, "a" * 99 + "b"),
        ("hello world", "hello python"),
        ("这是一段测试文本", "这是一段演示文本"),
    ]
    for s1, s2 in test_cases:
        start = time.time()
        dist = calculator.compute(s1, s2)
        elapsed = (time.time() - start) * 1000
        print(f"  '{s1[:20]}...' vs '{s2[:20]}...'")
        print(f"    距离: {dist}, 耗时: {elapsed:.2f}ms")
    
    print("\n" + "=" * 60)
    print("编辑距离是衡量两个字符串差异的核心算法！")
    print("=" * 60)


if __name__ == "__main__":
    demo()
