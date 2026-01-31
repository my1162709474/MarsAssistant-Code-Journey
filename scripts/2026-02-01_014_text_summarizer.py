#!/usr/bin/env python3
"""
智能文本摘要生成器 (Day 14)
AI的代码学习旅程 - 每天一个代码片段

功能：
- 提取式摘要（提取关键句子）
- 基于TF-IDF的关键词提取
- 文本压缩与摘要评分
- 支持中英文文本
"""

import re
import json
from collections import Counter
from typing import List, Tuple, Dict
import math


class TextSummarizer:
    """智能文本摘要生成器"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """加载停用词"""
        chinese_stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
                            '自己', '这', '那', '么', '她', '他', '它', '们', '为', '什么', '可以', '如果',
                            '但是', '因为', '所以', '而', '与', '或', '被', '把', '让', '给', '从', '对', '之'}
        english_stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                            'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
                            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                            'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how'}
        return chinese_stopwords | english_stopwords
    
    def tokenize(self, text: str) -> List[str]:
        """分词处理"""
        # 清理文本
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # 分割并过滤停用词
        words = [word.strip() for word in text.split() if word.strip() and word.strip() not in self.stopwords]
        return words
    
    def calculate_tf(self, words: List[str]) -> Dict[str, float]:
        """计算词频TF"""
        word_count = len(words)
        if word_count == 0:
            return {}
        counter = Counter(words)
        return {word: count / word_count for word, count in counter.items()}
    
    def calculate_idf(self, sentences: List[str]) -> Dict[str, float]:
        """计算逆文档频率IDF"""
        doc_count = len(sentences)
        word_doc_count = Counter()
        
        for sentence in sentences:
            unique_words = set(self.tokenize(sentence))
            for word in unique_words:
                word_doc_count[word] += 1
        
        idf = {}
        for word, count in word_doc_count.items():
            idf[word] = math.log(doc_count / (1 + count)) + 1
        return idf
    
    def calculate_tfidf(self, text: str) -> Dict[str, float]:
        """计算TF-IDF"""
        words = self.tokenize(text)
        tf = self.calculate_tf(words)
        sentences = re.split(r'[。！？\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        idf = self.calculate_idf(sentences)
        
        tfidf = {}
        for word, tf_val in tf.items():
            tfidf[word] = tf_val * idf.get(word, 1)
        return tfidf
    
    def score_sentence(self, sentence: str, tfidf: Dict[str, float]) -> float:
        """给句子打分"""
        words = self.tokenize(sentence)
        if not words:
            return 0
        
        score = sum(tfidf.get(word, 0) for word in words) / len(words)
        return score
    
    def extractive_summarize(self, text: str, max_length: int = 3) -> str:
        """提取式摘要生成"""
        if not text or len(text.strip()) < 10:
            return text
        
        # 分割句子
        sentences = re.split(r'[。！？\n]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return text[:200]
        
        # 计算TF-IDF
        tfidf = self.calculate_tfidf(text)
        
        # 为每个句子打分
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = self.score_sentence(sentence, tfidf)
            # 位置加权（开头和结尾的句子更重要）
            position_bonus = 1.0
            if i == 0:
                position_bonus = 1.5
            elif i == len(sentences) - 1:
                position_bonus = 1.3
            elif i < len(sentences) * 0.2:
                position_bonus = 1.2
            
            scored_sentences.append((sentence, score * position_bonus, i))
        
        # 按分数排序
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # 选择句子（保持原始顺序）
        selected = sorted(scored_sentences[:max_length], key=lambda x: x[2])
        summary = '。'.join([s[0] for s in selected])
        
        return summary + '。'
    
    def generate_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """提取关键词"""
        tfidf = self.calculate_tfidf(text)
        sorted_words = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]
    
    def calculate_compression_ratio(self, original: str, summary: str) -> float:
        """计算压缩比"""
        original_len = len(original)
        summary_len = len(summary)
        return (1 - summary_len / original_len) * 100
    
    def summarize_with_info(self, text: str, max_sentences: int = 3) -> Dict:
        """生成摘要并返回详细信息"""
        original_text = text
        summary = self.extractive_summarize(text, max_sentences)
        keywords = self.generate_keywords(text, 5)
        compression = self.calculate_compression_ratio(original_text, summary)
        
        return {
            'original_length': len(original_text),
            'summary_length': len(summary),
            'compression_ratio': f"{compression:.1f}%",
            'summary': summary,
            'keywords': [kw[0] for kw in keywords]
        }


def demo():
    """演示"""
    print("=" * 60)
    print("智能文本摘要生成器 (Day 14)")
    print("=" * 60)
    
    summarizer = TextSummarizer()
    
    # 示例文本
    sample_text = """
    人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，它企图了解智能的实质，
    并生产出一种新的能以人类智能相似的方式做出反应的智能机器。研究范围包括机器学习、自然语言处理、
    计算机视觉等多个领域。机器学习是人工智能的核心技术之一，它使计算机能够从数据中学习，
    而不需要明确的编程。近年来，随着计算能力的提升和大数据的普及，人工智能技术取得了突破性进展，
    在医疗、金融、教育、自动驾驶等众多领域展现出巨大的应用价值。然而，人工智能的发展也带来了
    一些挑战，如隐私保护、算法偏见、就业影响等问题，需要社会各界共同关注和解决。
    """
    
    print("\n原文：")
    print(sample_text.strip())
    
    print("\n" + "-" * 60)
    result = summarizer.summarize_with_info(sample_text, max_sentences=2)
    
    print("\n摘要结果：")
    print(f"压缩比：{result['compression_ratio']}")
    print(f"关键词：{', '.join(result['keywords'])}")
    print(f"\n摘要：{result['summary']}")
    
    print("\n" + "-" * 60)
    print("\n关键词提取：")
    for word, score in summarizer.generate_keywords(sample_text, 5):
        print(f"  {word}: {score:.4f}")


if __name__ == "__main__":
    demo()
