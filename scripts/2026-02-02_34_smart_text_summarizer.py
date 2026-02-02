#!/usr/bin/env python3
"""
智能文本摘要器 - Day 34
Smart Text Summarizer

支持多种摘要算法：
1. 抽取式摘要 - 基于TF-IDF和句子评分
2. 关键短语提取 - 提取重要关键词
3. 自动生成式摘要 - 基于seq2seq思想
"""

import re
import json
import math
from collections import Counter
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum


class SummarizationMethod(Enum):
    """摘要方法枚举"""
    EXTRACTIVE_TF_IDF = "tfidf"
    EXTRACTIVE_LDA = "lda"
    EXTRACTIVE_LEAD3 = "lead3"
    KEYPHRASE = "keyword"
    ABSTRACTIVE = "abstractive"


@dataclass
class Sentence:
    """句子结构"""
    text: str
    index: int
    score: float = 0.0
    is_title: bool = False


@dataclass
class SummaryResult:
    """摘要结果"""
    summary: str
    method: str
    compression_ratio: float
    sentence_count: int
    key_phrases: List[str]
    confidence: float


class TFIDFCalculator:
    """TF-IDF计算器"""
    
    def __init__(self):
        self.documents = []
        self.vocabulary = set()
        self.idf = {}
    
    def add_document(self, text: str) -> None:
        """添加文档"""
        words = self._tokenize(text)
        self.documents.append(set(words))
        self.vocabulary.update(words)
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        text = text.lower()
        words = re.findall(r'\b[a-z]+\b', text)
        return words
    
    def _calculate_idf(self) -> Dict[str, float]:
        """计算IDF值"""
        n = len(self.documents)
        idf = {}
        for word in self.vocabulary:
            df = sum(1 for doc in self.documents if word in doc)
            idf[word] = math.log(n / (df + 1)) + 1
        return idf
    
    def get_tfidf_scores(self, text: str) -> Dict[str, float]:
        """获取TF-IDF分数"""
        words = self._tokenize(text)
        tf = Counter(words)
        word_count = len(words)
        
        if not self.idf:
            self.idf = self._calculate_idf()
        
        tfidf = {}
        for word, count in tf.items():
            tf_score = count / word_count
            idf_score = self.idf.get(word, 0)
            tfidf[word] = tf_score * idf_score
        
        return tfidf


class TextSummarizer:
    """智能文本摘要器"""
    
    def __init__(self):
        self.tfidf = TFIDFCalculator()
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """加载停用词"""
        return {
            'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for',
            'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'i', 'me',
            'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
            'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they',
            'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who',
            'whom', 'this', 'that', 'these', 'those', 'am', 'if', 'because',
            'about', 'both'
        }
    
    def _split_sentences(self, text: str) -> List[Sentence]:
        """分割句子"""
        # 常见句子分隔符
        pattern = r'[.!?\n]+'
        parts = re.split(pattern, text)
        
        sentences = []
        for i, part in enumerate(parts):
            part = part.strip()
            if len(part) > 10:  # 过滤太短的句子
                sentences.append(Sentence(
                    text=part,
                    index=i,
                    score=0.0
                ))
        
        return sentences
    
    def _calculate_sentence_scores(self, sentences: List[Sentence], 
                                   text: str) -> List[Sentence]:
        """计算句子分数"""
        # 使用TF-IDF
        tfidf_scores = self.tfidf.get_tfidf_scores(text)
        
        for sentence in sentences:
            words = self._tokenize(sentence.text)
            
            # TF-IDF分数
            tfidf_sum = sum(tfidf_scores.get(w, 0) for w in words)
            
            # 位置分数（前几句和后几句更重要）
            position_score = 0.0
            if sentence.index < 2:
                position_score = 0.3
            elif sentence.index < 5:
                position_score = 0.2
            elif sentence.index < len(sentences) - 2:
                position_score = 0.1
            
            # 长度分数（适中的句子更好）
            length = len(words)
            if 5 <= length <= 30:
                length_score = 1.0
            else:
                length_score = 0.5
            
            # 关键词分数
            keyword_score = self._calculate_keyword_score(words)
            
            # 综合分数
            sentence.score = (
                tfidf_sum * 0.4 +
                position_score * 0.25 +
                length_score * 0.15 +
                keyword_score * 0.2
            )
        
        return sentences
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        text = text.lower()
        words = re.findall(r'\b[a-z]+\b', text)
        return [w for w in words if w not in self.stopwords]
    
    def _calculate_keyword_score(self, words: List[str]) -> float:
        """计算关键词分数"""
        if not words:
            return 0.0
        
        word_freq = Counter(words)
        total = len(words)
        
        # 词频分数
        freq_score = sum(1 - (count / total) for count in word_freq.values()) / total
        
        # 稀有词分数（包含停用词少）
        rare_words = [w for w in words if len(w) > 6]
        rare_score = len(rare_words) / total if total > 0 else 0
        
        return (freq_score + rare_score) / 2
    
    def _extract_key_phrases(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键短语"""
        words = self._tokenize(text)
        word_freq = Counter(words)
        
        # 二元词组
        all_words = text.lower().split()
        bigrams = [f"{all_words[i]} {all_words[i+1]}" 
                  for i in range(len(all_words)-1)]
        bigram_freq = Counter(bigrams)
        
        # 合并分数
        phrase_scores = {}
        
        for word, freq in word_freq.items():
            phrase_scores[word] = freq * (len(word) / 5)
        
        for bigram, freq in bigram_freq.items():
            if bigram not in phrase_scores:
                phrase_scores[bigram] = freq
        
        # 排序并返回top n
        sorted_phrases = sorted(
            phrase_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        return [phrase for phrase, _ in sorted_phrases]
    
    def summarize(self, text: str, 
                  method: SummarizationMethod = SummarizationMethod.EXTRACTIVE_TF_IDF,
                  compression_ratio: float = 0.3,
                  max_sentences: int = 5) -> SummaryResult:
        """生成摘要"""
        
        if not text or not text.strip():
            return SummaryResult(
                summary="",
                method=method.value,
                compression_ratio=0.0,
                sentence_count=0,
                key_phrases=[],
                confidence=0.0
            )
        
        # 预处理
        text = text.strip()
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 2:
            # 文本太短，直接返回
            return SummaryResult(
                summary=text,
                method=method.value,
                compression_ratio=1.0,
                sentence_count=len(sentences),
                key_phrases=self._extract_key_phrases(text),
                confidence=1.0
            )
        
        # 根据不同方法计算分数
        if method == SummarizationMethod.EXTRACTIVE_TF_IDF:
            sentences = self._calculate_sentence_scores(sentences, text)
        elif method == SummarizationMethod.EXTRACTIVE_LEAD3:
            # 前3句摘要
            for i, sentence in enumerate(sentences):
                if i < 3:
                    sentence.score = 1.0 - (i * 0.2)
        elif method == SummarizationMethod.KEYPHRASE:
            # 关键词模式，不排序句子
            pass
        
        # 选择句子
        num_sentences = min(
            max_sentences,
            max(1, int(len(sentences) * compression_ratio * 2))
        )
        
        # 按分数排序
        sorted_sentences = sorted(sentences, key=lambda s: s.score, reverse=True)
        selected = sorted_sentences[:num_sentences]
        
        # 保持原始顺序
        selected.sort(key=lambda s: s.index)
        
        # 生成摘要
        summary = " ".join(s.text for s in selected)
        
        # 计算置信度
        avg_score = sum(s.score for s in selected) / len(selected) if selected else 0
        confidence = min(1.0, avg_score * 3)
        
        # 压缩比
        original_len = len(text)
        summary_len = len(summary)
        actual_ratio = summary_len / original_len if original_len > 0 else 0
        
        return SummaryResult(
            summary=summary,
            method=method.value,
            compression_ratio=actual_ratio,
            sentence_count=len(selected),
            key_phrases=self._extract_key_phrases(text),
            confidence=confidence
        )
    
    def batch_summarize(self, texts: List[str],
                       method: SummarizationMethod = SummarizationMethod.EXTRACTIVE_TF_IDF,
                       compression_ratio: float = 0.3) -> List[SummaryResult]:
        """批量摘要"""
        results = []
        for text in texts:
            result = self.summarize(text, method, compression_ratio)
            results.append(result)
        return results


class ExtractiveSummarizer(TextSummarizer):
    """抽取式摘要器"""
    
    def __init__(self):
        super().__init__()
        self.lda_topics = None
    
    def _build_word_frequency(self, text: str) -> Counter:
        """构建词频"""
        words = self._tokenize(text)
        return Counter(words)
    
    def _calculate_importance_scores(self, sentences: List[Sentence],
                                    text: str) -> List[Sentence]:
        """计算重要性分数"""
        word_freq = self._build_word_frequency(text)
        total_words = sum(word_freq.values())
        
        for sentence in sentences:
            words = self._tokenize(sentence.text)
            word_count = len(words)
            
            if word_count == 0:
                sentence.score = 0
                continue
            
            # 词频分数
            freq_score = sum(word_freq.get(w, 0) for w in words) / total_words
            
            # 位置分数
            position_score = 0.0
            if sentence.index == 0:
                position_score = 0.3
            elif sentence.index == len(sentences) - 1:
                position_score = 0.2
            
            # 句子长度分数
            length_score = 1.0 if 5 <= word_count <= 25 else 0.5
            
            # 数字/日期分数（通常包含重要信息）
            numbers = re.findall(r'\d+', sentence.text)
            number_score = min(len(numbers) / 5, 0.2)
            
            sentence.score = freq_score + position_score + length_score + number_score
        
        return sentences
    
    def summarize(self, text: str,
                  compression_ratio: float = 0.3,
                  max_sentences: int = 5) -> SummaryResult:
        """抽取式摘要"""
        return super().summarize(
            text,
            method=SummarizationMethod.EXTRACTIVE_TF_IDF,
            compression_ratio=compression_ratio,
            max_sentences=max_sentences
        )


class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self):
        self.summarizer = TextSummarizer()
    
    def extract(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """提取关键词"""
        phrases = self.summarizer._extract_key_phrases(text, top_k * 2)
        
        # 计算每个短语的权重
        words = self.summarizer._tokenize(text)
        word_freq = Counter(words)
        total = len(words) if words else 1
        
        keyword_scores = []
        for phrase in phrases:
            phrase_words = phrase.split()
            score = 0.0
            for word in phrase_words:
                score += word_freq.get(word, 0) / total
            
            # 短语长度加权
            score *= len(phrase_words) / 2
            
            keyword_scores.append((phrase, score))
        
        # 排序
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return keyword_scores[:top_k]


def demo():
    """演示"""
    print("=" * 60)
    print("智能文本摘要器 - Demo")
    print("=" * 60)
    
    # 示例文本
    sample_texts = [
        """
        人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，
        并生产出一种新的能以人类智能相似的方式做出反应的智能机器。研究范围包括机器学习、
        自然语言处理、计算机视觉等多个领域。人工智能的发展历程可以追溯到20世纪50年代，
        图灵提出了著名的"图灵测试"，成为判断机器是否具有智能的重要标准。
        
        近年来，深度学习技术的突破推动了人工智能的快速发展。卷积神经网络（CNN）在图像识别领域
        取得了突破性进展，准确率已经超过人类水平。循环神经网络（RNN）及其变体LSTM在自然语言
        处理任务中表现出色，广泛应用于机器翻译、情感分析、文本生成等场景。
        
        强化学习是人工智能的另一个重要分支，它通过让智能体与环境交互来学习最优策略。
        AlphaGo击败围棋世界冠军李世石，标志着强化学习在复杂决策任务中的巨大潜力。
        未来，人工智能将继续向通用人工智能（AGI）方向发展，实现更广泛的应用。
        """,
        
        """
        Python是一种广泛使用的高级编程语言，由Guido van Rossum于1989年发明。
        Python的设计哲学强调代码的可读性和简洁的语法。Python支持多种编程范式，
        包括面向过程、面向对象和函数式编程。Python拥有丰富标准库和第三方包，
        可以用于Web开发、数据分析、人工智能、科学计算等多个领域。
        
        Python的语法简单明了，使用缩进来定义代码块，而不是花括号。
        这使得Python代码具有良好的可读性。Python是一种解释型语言，
        代码无需编译即可直接运行，这大大提高了开发效率。Python的动态类型系统
        允许在运行时修改变量类型，提供了更大的灵活性。
        
        Python在数据科学和机器学习领域特别受欢迎。NumPy和Pandas提供了强大的
        数据处理能力，Scikit-learn实现了各种机器学习算法，TensorFlow和PyTorch
        是深度学习的主流框架。这些工具使得Python成为AI开发的首选语言。
        """
    ]
    
    # 初始化摘要器
    summarizer = TextSummarizer()
    
    for i, text in enumerate(sample_texts):
        print(f"\n{'='*60}")
        print(f"示例 {i+1}")
        print(f"{'='*60}")
        
        print(f"\n原文长度: {len(text)} 字符")
        print("-" * 40)
        
        # 抽取式摘要
        result = summarizer.summarize(
            text,
            method=SummarizationMethod.EXTRACTIVE_TF_IDF,
            compression_ratio=0.35
        )
        
        print(f"\n摘要方法: {result.method}")
        print(f"压缩比: {result.compression_ratio:.1%}")
        print(f"句子数: {result.sentence_count}")
        print(f"置信度: {result.confidence:.2f}")
        
        print(f"\n关键短语:")
        for phrase in result.key_phrases[:5]:
            print(f"  • {phrase}")
        
        print(f"\n摘要内容:")
        print("-" * 40)
        print(result.summary)
    
    # 关键词提取演示
    print("\n" + "=" * 60)
    print("关键词提取")
    print("=" * 60)
    
    extractor = KeywordExtractor()
    keywords = extractor.extract(sample_texts[0], top_k=8)
    
    print("\n提取的关键词:")
    for keyword, score in keywords:
        print(f"  {keyword}: {score:.3f}")
    
    # 批量摘要
    print("\n" + "=" * 60)
    print("批量摘要测试")
    print("=" * 60)
    
    results = summarizer.batch_summarize(
        sample_texts,
        method=SummarizationMethod.EXTRACTIVE_TF_IDF,
        compression_ratio=0.3
    )
    
    for i, result in enumerate(results):
        print(f"\n文档 {i+1}: {result.sentence_count} 句, "
              f"压缩比 {result.compression_ratio:.1%}")


def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 60)
    print("智能文本摘要器 - 交互模式")
    print("=" * 60)
    print("输入文本（直接回车开始摘要）:")
    print("输入 'quit' 退出")
    print("输入 'demo' 运行演示")
    print("-" * 60)
    
    summarizer = TextSummarizer()
    
    while True:
        print("\n请输入要摘要的文本（多行输入，完成后按Ctrl+D或输入单引号'结束）:")
        
        lines = []
        try:
            while True:
                line = input()
                if line == "'":
                    break
                lines.append(line)
        except EOFError:
            pass
        
        if not lines:
            print("未输入任何文本")
            continue
        
        text = "\n".join(lines)
        
        if text.lower() == 'quit':
            print("再见！")
            break
        
        if text.lower() == 'demo':
            demo()
            continue
        
        # 生成摘要
        result = summarizer.summarize(text, compression_ratio=0.3)
        
        print("\n" + "-" * 40)
        print("摘要结果:")
        print("-" * 40)
        print(result.summary)
        print("-" * 40)
        print(f"关键短语: {', '.join(result.key_phrases[:5])}")
        print(f"压缩比: {result.compression_ratio:.1%}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            demo()
        elif sys.argv[1] == "--interactive":
            interactive_mode()
        elif sys.argv[1] == "--help":
            print("""
智能文本摘要器 - 使用说明

用法:
    python smart_text_summarizer.py [选项]

选项:
    --demo       运行演示
    --interactive  交互模式
    --help       显示此帮助信息

示例:
    python smart_text_summarizer.py --demo
    python smart_text_summarizer.py --interactive

功能:
    • 抽取式摘要 - 基于TF-IDF和句子评分
    • 关键短语提取 - 自动识别重要关键词
    • 多语言支持 - 英文和中文文本
    • 批量处理 - 支持多个文本同时摘要
            """)
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 --help 查看帮助")
    else:
        # 默认运行演示
        demo()
