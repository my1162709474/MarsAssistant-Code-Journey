#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本相似度计算器 - Text Similarity Calculator

创建于 2026-02-02
Day 023: 基于多种算法的文本相似度比较工具

功能：
- Jaccard 相似度
- 余弦相似度
- Levenshtein 距离
- N-gram 相似度
"""

import re
import math
from collections import Counter
import hashlib

class TextSimilarity:
    """文本相似度计算工具类"""
    
    def __init__(self):
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', 'the', 'a', 'an', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall'
        }
    
    def preprocess(self, text):
        """文本预处理：小写化、去除标点、分词"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [w for w in words if w not in self.stop_words and len(w) > 1]
    
    def jaccard_similarity(self, text1, text2):
        """
        Jaccard 相似度
        J(A,B) = |A ∩ B| / |A ∪ B|
        """
        set1 = set(self.preprocess(text1))
        set2 = set(self.preprocess(text2))
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def cosine_similarity(self, text1, text2):
        """
        余弦相似度
        cos(θ) = (A · B) / (||A|| × ||B||)
        """
        words1 = self.preprocess(text1)
        words2 = self.preprocess(text2)
        
        if not words1 and not words2:
            return 1.0
        
        vec1 = Counter(words1)
        vec2 = Counter(words2)
        
        # 计算点积
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in set(vec1) | set(vec2))
        
        # 计算向量模长
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def levenshtein_distance(self, s1, s2):
        """
        Levenshtein 编辑距离
        返回两个字符串之间的最小编辑次数
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                
                current_row.append(min(insertions, deletions, substitutions))
            
            previous_row = current_row
        
        return previous_row[-1]
    
    def levenshtein_similarity(self, text1, text2):
        """基于编辑距离的相似度"""
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        distance = self.levenshtein_distance(text1, text2)
        return 1 - (distance / max_len)
    
    def get_ngrams(self, text, n=2):
        """获取文本的 n-gram"""
        words = self.preprocess(text)
        return [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
    
    def ngram_similarity(self, text1, text2, n=2):
        """N-gram 相似度"""
        ngrams1 = set(self.get_ngrams(text1, n))
        ngrams2 = set(self.get_ngrams(text2, n))
        
        if not ngrams1 and not ngrams2:
            return 1.0
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        
        return intersection / union if union > 0 else 0.0
    
    def comprehensive_similarity(self, text1, text2):
        """
        综合相似度
        结合多种算法的加权平均
        """
        jac_sim = self.jaccard_similarity(text1, text2)
        cos_sim = self.cosine_similarity(text1, text2)
        lev_sim = self.levenshtein_similarity(text1, text2)
        ngram_sim = self.ngram_similarity(text1, text2)
        
        # 加权平均
        weights = {'jaccard': 0.2, 'cosine': 0.3, 'levenshtein': 0.3, 'ngram': 0.2}
        
        score = (
            weights['jaccard'] * jac_sim +
            weights['cosine'] * cos_sim +
            weights['levenshtein'] * lev_sim +
            weights['ngram'] * ngram_sim
        )
        
        return round(score, 4)


def demo():
    """示例演示"""
    calculator = TextSimilarity()
    
    test_pairs = [
        (
            "人工智能正在改变世界",
            "AI正在深刻改变我们的生活方式"
        ),
        (
            "Python是一门非常流行的编程语言",
            "Python is a very popular programming language"
        ),
        (
            "今天天气真好",
            "今天天气不错"
        ),
        (
            "Hello World",
            "Hello Python"
        )
    ]
    
    print("=" * 60)
    print("Text Similarity Calculator - Demo")
    print("=" * 60)
    
    for i, (text1, text2) in enumerate(test_pairs, 1):
        print(f"\n[比较 {i}]")
        print(f"文本1: {text1}")
        print(f"文本2: {text2}")
        print(f"\n相似度分析:")
        print(f"  Jaccard:      {calculator.jaccard_similarity(text1, text2):.4f}")
        print(f"  Cosine:       {calculator.cosine_similarity(text1, text2):.4f}")
        print(f"  Levenshtein:  {calculator.levenshtein_similarity(text1, text2):.4f}")
        print(f"  N-gram:       {calculator.ngram_similarity(text1, text2):.4f}")
        print(f"  综合得分:     {calculator.comprehensive_similarity(text1, text2):.4f}")


if __name__ == "__main__":
    demo()
