#!/usr/bin/env python3
"""
Day 22: 智能文本摘要器 (Smart Text Summarizer)

这是一个基于抽取式方法的简单文本摘要工具，
展示了自然语言处理的基本概念。
"""

import re
from collections import Counter
from typing import List, Tuple


class SmartSummarizer:
    """智能文本摘要器类"""
    
    def __init__(self):
        self.stop_words = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', 'that', 'the', 'is', 'a', 'an', 'and', 'or',
            'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
    
    def preprocess(self, text: str) -> str:
        """文本预处理：清理和标准化"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        # 简单分词：按空格和标点分割
        words = re.findall(r'\b\w+\b', text.lower())
        # 移除停用词
        words = [w for w in words if w not in self.stop_words and len(w) > 1]
        return words
    
    def calculate_sentence_scores(self, text: str) -> List[Tuple[int, float]]:
        """计算每个句子的重要性得分"""
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        sentence_scores = []
        for idx, sentence in enumerate(sentences):
            words = self.tokenize(sentence)
            
            if not words:
                continue
            
            # 基于词频计算得分
            word_freq = Counter(words)
            max_freq = max(word_freq.values()) if word_freq else 1
            
            # 归一化得分
            score = sum(word_freq[word] / max_freq for word in words)
            
            # 句子长度惩罚（太短或太长的句子得分降低）
            length_penalty = 1.0
            if len(words) < 5:
                length_penalty = 0.5
            elif len(words) > 50:
                length_penalty = 0.8
            
            score *= length_penalty
            sentence_scores.append((idx, score))
        
        return sentence_scores
    
    def summarize(self, text: str, ratio: float = 0.3) -> str:
        """
        生成摘要
        
        Args:
            text: 输入文本
            ratio: 摘要长度比例 (默认30%)
        
        Returns:
            摘要文本
        """
        text = self.preprocess(text)
        sentence_scores = self.calculate_sentence_scores(text)
        
        if not sentence_scores:
            return ""
        
        # 按得分排序，选择前N个句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        num_sentences = max(1, int(len(sentence_scores) * ratio))
        top_sentences = sentence_scores[:num_sentences]
        
        # 按原文顺序重新排列
        top_sentences.sort(key=lambda x: x[0])
        
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        summary = ''.join(sentences[i[0]] for i in top_sentences)
        return summary
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """提取关键词"""
        words = self.tokenize(text)
        word_freq = Counter(words)
        return [word for word, _ in word_freq.most_common(top_n)]


def demo():
    """演示摘要功能"""
    
    sample_text = """
    人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
    它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    研究范围包括机器学习、自然语言处理、计算机视觉等多个领域。
    近年来，深度学习技术的发展推动了AI的快速进步，在图像识别、语音识别、
    自然语言理解等方面取得了突破性成果。AI技术正在深刻改变我们的生活方式，
    从智能助手到自动驾驶，从医疗诊断到金融分析，AI的应用越来越广泛。
    然而，AI的发展也带来了伦理和安全方面的挑战，需要社会各界共同努力。
    """
    
    print("=" * 60)
    print("Day 22: 智能文本摘要器演示")
    print("=" * 60)
    
    summarizer = SmartSummarizer()
    
    # 生成摘要
    summary = summarizer.summarize(sample_text, ratio=0.4)
    print("\n📝 原文摘要：")
    print(summary)
    
    # 提取关键词
    keywords = summarizer.extract_keywords(sample_text)
    print(f"\n🔑 关键词：{', '.join(keywords)}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
