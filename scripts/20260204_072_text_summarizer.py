"""
智能文本摘要生成器 - Day 72
Intelligent Text Summarizer
"""

import re
from collections import Counter
from typing import List, Tuple
import json


class TextSummarizer:
    """智能文本摘要生成器"""
    
    def __init__(self, language: str = "zh"):
        self.language = language
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """加载停用词"""
        if self.language == "zh":
            return {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', 
                   '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', 
                   '没有', '看', '好', '自己', '这', '个', '那', '吗', '什么', '怎么'}
        else:
            return {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                   'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                   'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could'}
    
    def preprocess(self, text: str) -> List[str]:
        """文本预处理"""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        return [w for w in words if w not in self.stopwords and len(w) > 1]
    
    def calculate_word_scores(self, sentences: List[str], words: List[str]) -> dict:
        """计算词频分数"""
        word_freq = Counter(words)
        max_freq = max(word_freq.values()) if word_freq else 1
        
        # 归一化词频
        scores = {}
        for word, freq in word_freq.items():
            scores[word] = freq / max_freq
        
        return scores
    
    def calculate_sentence_scores(self, sentences: List[str], word_scores: dict) -> dict:
        """计算句子分数"""
        scores = {}
        for i, sent in enumerate(sentences):
            words = self.preprocess(sent)
            if not words:
                continue
            
            # 句子分数 = 词频分数的平均值 * 位置权重
            word_score_sum = sum(word_scores.get(w, 0) for w in words)
            avg_score = word_score_sum / len(words)
            
            # 位置权重：开头和结尾的句子更重要
            position_weight = 1.0
            if i == 0:
                position_weight = 1.5  # 首句最重要
            elif i == len(sentences) - 1:
                position_weight = 1.3  # 末句也重要
            
            scores[i] = avg_score * position_weight
        
        return scores
    
    def extract_summary(self, text: str, ratio: float = 0.3) -> str:
        """提取摘要
        
        Args:
            text: 输入文本
            ratio: 摘要长度比例 (0.1 - 0.9)
        
        Returns:
            摘要文本
        """
        # 分句
        if self.language == "zh":
            sentences = re.split(r'[。！？；\n]+', text)
        else:
            sentences = re.split(r'[.!?;]+', text)
        
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) <= 2:
            return text
        
        # 预处理
        words = self.preprocess(text)
        
        # 计算分数
        word_scores = self.calculate_word_scores(sentences, words)
        sentence_scores = self.calculate_sentence_scores(sentences, word_scores)
        
        # 选择高分句子
        num_sentences = max(1, int(len(sentences) * ratio))
        top_sentences = sorted(sentence_scores.items(), 
                              key=lambda x: x[1], 
                              reverse=True)[:num_sentences]
        
        # 按原文顺序重新排序
        top_indices = sorted([idx for idx, _ in top_sentences])
        
        summary_sentences = [sentences[i] for i in top_indices]
        
        return ''.join(summary_sentences)
    
    def generate_abstractive_summary(self, text: str, max_length: int = 100) -> dict:
        """生成简短的抽象摘要"""
        # 提取关键词
        words = self.preprocess(text)
        word_freq = Counter(words)
        keywords = [word for word, _ in word_freq.most_common(5)]
        
        # 生成摘要信息
        return {
            "关键词": keywords,
            "原文长度": len(text),
            "摘要长度": min(len(text) // 3, max_length),
            "建议": "这是一段测试文本，建议使用 extract_summary() 方法获取完整摘要"
        }


def demo():
    """演示"""
    test_text = """
    人工智能（AI）是计算机科学的一个重要分支，它企图了解智能的实质，
    并生产出一种新的能以人类智能相似的方式做出反应的智能机器。研究范围
    包括机器学习、自然语言处理、计算机视觉等多个领域。人工智能的发展历程
    可以追溯到20世纪50年代，经过几十年的研究，已经取得了显著的进展。
    """
    
    summarizer = TextSummarizer(language="zh")
    
    print("=" * 50)
    print("智能文本摘要生成器 - Day 72")
    print("=" * 50)
    
    print("\n【原文】")
    print(test_text)
    
    print("\n【提取式摘要 (30%)】")
    summary = summarizer.extract_summary(test_text, ratio=0.3)
    print(summary)
    
    print("\n【抽象摘要信息】")
    info = summarizer.generate_abstractive_summary(test_text)
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    demo()
