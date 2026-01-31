#!/usr/bin/env python3
"""
文本相似度计算器 - Day 8: Text Similarity Calculator

支持多种相似度算法：
1. 余弦相似度 (Cosine Similarity)
2. Jaccard相似度
3. Levenshtein编辑距离
4. SimHash (用于大规模文本去重)

Author: AI Assistant
Date: 2026-02-01
"""

import math
from collections import Counter
import hashlib

def tokenize(text):
    """简单分词"""
    return text.lower().split()

def cosine_similarity(text1, text2):
    """计算余弦相似度"""
    words1 = set(tokenize(text1))
    words2 = set(tokenize(text2))
    
    all_words = words1 | words2
    vec1 = [1 if w in words1 else 0 for w in all_words]
    vec2 = [1 if w in words2 else 0 for w in all_words]
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(a * a for a in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def jaccard_similarity(text1, text2):
    """计算Jaccard相似度"""
    words1 = set(tokenize(text1))
    words2 = set(tokenize(text2))
    
    intersection = words1 & words2
    union = words1 | words2
    
    if len(union) == 0:
        return 1.0
    return len(intersection) / len(union)

def levenshtein_distance(s1, s2):
    """计算Levenshtein编辑距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
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

def normalized_levenshtein(s1, s2):
    """归一化Levenshtein相似度"""
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1 - (distance / max_len)

def simhash(text, fingerprint_size=64):
    """SimHash算法 - 用于大规模文本去重"""
    words = text.lower().split()
    shingles = []
    
    for i in range(len(words) - 1):
        shingle = ' '.join(words[i:i+2])
        shingles.append(shingle)
    
    if not shingles:
        shingles = words
    
    hash_vectors = []
    for shingle in shingles:
        h = int(hashlib.md5(shingle.encode()).hexdigest(), 16)
        hash_vectors.append([1 if (h >> i) & 1 else -1 for i in range(fingerprint_size)])
    
    fingerprint = [sum(v[i] for v in hash_vectors) for i in range(fingerprint_size)]
    result = sum(1 << i if fingerprint[i] > 0 else 0 for i in range(fingerprint_size))
    
    return result

def hamming_distance(hash1, hash2):
    """计算SimHash的海明距离"""
    return bin(hash1 ^ hash2).count('1')

class TextSimilarity:
    """文本相似度综合工具类"""
    
    def __init__(self):
        self.results = {}
    
    def analyze(self, text1, text2):
        """全面分析两个文本的相似度"""
        self.results = {
            'cosine': cosine_similarity(text1, text2),
            'jaccard': jaccard_similarity(text1, text2),
            'levenshtein_norm': normalized_levenshtein(text1, text2),
        }
        
        hash1 = simhash(text1)
        hash2 = simhash(text2)
        self.results['simhash_hamming'] = hamming_distance(hash1, hash2)
        
        return self.results
    
    def get_similarity_report(self, text1, text2):
        """生成相似度报告"""
        results = self.analyze(text1, text2)
        
        report = f"""
=== 文本相似度分析报告 ===

📊 相似度得分:
  • 余弦相似度: {results['cosine']:.4f}
  • Jaccard相似度: {results['jaccard']:.4f}
  • 归一化编辑距离: {results['levenshtein_norm']:.4f}
  • SimHash海明距离: {results['simhash_hamming']}

💡 解读:
  • 余弦相似度: 越高越相似 (范围: 0-1)
  • Jaccard相似度: 越高越相似 (范围: 0-1)
  • 编辑距离相似度: 越高越相似 (范围: 0-1)
  • SimHash距离: 越低越相似 (范围: 0-{64})
"""
        return report

def demo():
    """演示"""
    text1 = "人工智能是未来最有前途的领域之一"
    text2 = "AI是未来最有发展前景的技术方向"
    text3 = "今天天气真好，适合去公园散步"
    
    print("=" * 50)
    print("🎯 文本相似度计算器演示")
    print("=" * 50)
    
    analyzer = TextSimilarity()
    
    print("\n📝 对比1 - 相关主题:")
    print(f"文本1: {text1}")
    print(f"文本2: {text2}")
    print(analyzer.get_similarity_report(text1, text2))
    
    print("\n📝 对比2 - 不相关主题:")
    print(f"文本1: {text1}")
    print(f"文本3: {text3}")
    print(analyzer.get_similarity_report(text1, text3))

if __name__ == "__main__":
    demo()
