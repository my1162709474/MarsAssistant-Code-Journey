#!/usr/bin/env python3
"""
智能文本摘要生成器
Smart Text Summarizer

支持多种摘要算法：Extractive/Abstractive/关键词提取
基于 TextRank、TF-IDF 和 LLM 的智能摘要
"""

import re
import json
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


class SummarizationMethod(Enum):
    TEXTRANK = "textrank"
    TF_IDF = "tfidf"
    EXTRACTIVE_LLM = "extract_llm"
    ABSTRACTIVE_LLM = "abstract_llm"
    HYBRID = "hybrid"


class TextType(Enum):
    NEWS = "news"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    CONVERSATION = "conversation"
    GENERAL = "general"


@dataclass
class Sentence:
    """句子结构"""
    text: str
    index: int
    score: float = 0.0
    words: List[str] = None
    
    def __post_init__(self):
        if self.words is None:
            self.words = self.text.lower().split()


@dataclass
class SummaryResult:
    """摘要结果"""
    summary: str
    method: SummarizationMethod
    compression_ratio: float
    key_points: List[str]
    confidence: float
    processing_time_ms: float


class TextPreprocessor:
    """文本预处理"""
    
    # 停用词列表
    STOPWORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
        '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
        '自己', '这', '那', '么', '她', '他', '它', '们', '为', '什么', '可以', '还',
        'from', 'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'in', 'to', 'of',
        'it', 'for', 'with', 'as', 'be', 'are', 'was', 'were', 'this', 'that', 'by'
    }
    
    # URL正则
    URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
    
    # 邮箱正则
    EMAIL_PATTERN = re.compile(r'\S+@\S+\.\S+')
    
    @classmethod
    def preprocess(cls, text: str) -> str:
        """预处理文本"""
        # 移除URL
        text = cls.URL_PATTERN.sub('', text)
        # 移除邮箱
        text = cls.EMAIL_PATTERN.sub('', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符但保留标点
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\'\"]', '', text)
        return text.strip()
    
    @classmethod
    def split_sentences(cls, text: str) -> List[Sentence]:
        """分割句子"""
        # 中文句子分割
        chinese_pattern = r'[。！？；]'
        # 英文句子分割
        english_pattern = r'[.!?;]'
        
        # 合并分割
        sentences = []
        sentence_list = re.split(chinese_pattern + '|' + english_pattern, text)
        
        for idx, sent in enumerate(sentence_list):
            sent = sent.strip()
            if len(sent) > 5:  # 过滤太短的句子
                sentences.append(Sentence(
                    text=sent,
                    index=idx
                ))
        
        return sentences
    
    @classmethod
    def extract_words(cls, text: str) -> List[str]:
        """提取词汇"""
        words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]+\b', text.lower())
        return [w for w in words if w not in cls.STOPWORDS and len(w) > 1]


class TFIDFScorer:
    """TF-IDF评分器"""
    
    def __init__(self):
        self.doc_freq: Dict[str, int] = {}
        self.total_docs = 0
    
    def fit(self, sentences: List[Sentence]):
        """拟合语料库"""
        self.total_docs = len(sentences)
        
        for sent in sentences:
            words = set(sent.words)
            for word in words:
                self.doc_freq[word] = self.doc_freq.get(word, 0) + 1
    
    def score(self, sentence: Sentence) -> float:
        """计算TF-IDF分数"""
        if self.total_docs == 0:
            return 0.0
        
        words = sentence.words
        if not words:
            return 0.0
        
        # TF计算
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        
        tf_score = sum(1 + math.log(count) for count in word_count.values()) / len(words)
        
        # IDF计算
        idf_score = 0
        for word in set(words):
            df = self.doc_freq.get(word, 0)
            if df > 0:
                idf_score += math.log(self.total_docs / df)
        
        return tf_score * idf_score / max(len(set(words)), 1)


class TextRankScorer:
    """TextRank评分器"""
    
    def __init__(self, damping: float = 0.85, max_iter: int = 100, tolerance: float = 1e-4):
        self.damping = damping
        self.max_iter = max_iter
        self.tolerance = tolerance
    
    def _similarity(self, sent1: Sentence, sent2: Sentence) -> float:
        """计算句子相似度 (Jaccard)"""
        set1 = set(sent1.words)
        set2 = set(sent2.words)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _build_graph(self, sentences: List[Sentence]) -> List[List[float]]:
        """构建相似度图"""
        n = len(sentences)
        graph = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                sim = self._similarity(sentences[i], sentences[j])
                graph[i][j] = sim
                graph[j][i] = sim
        
        return graph
    
    def score(self, sentences: List[Sentence]) -> List[float]:
        """TextRank迭代计算"""
        if not sentences:
            return []
        
        n = len(sentences)
        graph = self._build_graph(sentences)
        
        # 归一化邻接矩阵
        out_weights = [sum(row) for row in graph]
        norm_graph = [[w / out_weights[i] if out_weights[i] > 0 else 0 
                      for w in row] for i, row in enumerate(graph)]
        
        # 初始化分数
        scores = [1.0 / n] * n
        
        # 迭代计算
        for _ in range(self.max_iter):
            new_scores = []
            for i in range(n):
                score = (1 - self.damping) / n
                for j in range(n):
                    if i != j:
                        score += self.damping * norm_graph[j][i] * scores[j]
                new_scores.append(score)
            
            # 检查收敛
            diff = sum(abs(s - ns) for s, ns in zip(scores, new_scores))
            scores = new_scores
            
            if diff < self.tolerance:
                break
        
        return scores


class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self, top_k: int = 10):
        self.top_k = top_k
    
    def extract(self, text: str) -> List[Tuple[str, float]]:
        """提取关键词"""
        words = TextPreprocessor.extract_words(text)
        word_freq = {}
        
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 计算频率分数
        max_freq = max(word_freq.values()) if word_freq else 1
        
        keywords = []
        for word, freq in word_freq.items():
            score = freq / max_freq
            keywords.append((word, score))
        
        # 排序返回
        keywords.sort(key=lambda x: x[1], reverse=True)
        return keywords[:self.top_k]


class SmartTextSummarizer:
    """智能文本摘要生成器"""
    
    def __init__(self, method: SummarizationMethod = SummarizationMethod.HYBRID):
        self.method = method
        self.textrank_scorer = TextRankScorer()
        self.tfidf_scorer = TFIDFScorer()
        self.keyword_extractor = KeywordExtractor()
    
    def detect_text_type(self, text: str) -> TextType:
        """检测文本类型"""
        text_lower = text.lower()
        
        # 学术论文特征
        academic_markers = ['abstract', 'introduction', 'methodology', 'conclusion', 
                          '参考文献', '论文', '研究', '实验']
        if any(marker in text_lower for marker in academic_markers):
            return TextType.ACADEMIC
        
        # 技术文档特征
        tech_markers = ['function', 'class', 'api', 'method', 'parameter', 
                       'def ', 'import ', 'class ', '//', '```']
        if any(marker in text_lower for marker in tech_markers):
            return TextType.TECHNICAL
        
        # 新闻特征
        news_markers = ['报道', '记者', '新华社', '北京', '华盛顿', '据新华社']
        if any(marker in text_lower for marker in news_markers):
            return TextType.NEWS
        
        return TextType.GENERAL
    
    def _extractive_summary(self, sentences: List[Sentence], 
                           scores: List[float],
                           max_length: int = 500,
                           min_sentences: int = 2) -> str:
        """抽取式摘要"""
        # 按分数排序
        scored = [(s, sc) for s, sc in zip(sentences, scores) if sc > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 选择高分句子，保持原始顺序
        selected = []
        current_length = 0
        
        # 按原始顺序重新排序
        for sent, score in scored:
            if len(selected) >= min_sentences:
                if current_length >= max_length * 0.8:
                    break
            
            if sent not in selected:
                selected.append(sent)
                current_length += len(sent.text)
        
        # 按原始顺序排列
        selected.sort(key=lambda x: x.index)
        
        return '。'.join(s.text for s in selected) + '。' if selected else ''
    
    def _generate_key_points(self, sentences: List[Sentence], 
                            scores: List[float],
                            top_n: int = 5) -> List[str]:
        """生成关键点"""
        scored = list(zip(sentences, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        
        key_points = []
        for sent, score in scored[:top_n]:
            if score > 0:
                # 简化句子
                point = sent.text[:100] + '...' if len(sent.text) > 100 else sent.text
                key_points.append(point)
        
        return key_points
    
    def summarize(self, text: str, 
                 max_length: int = 500,
                 min_sentences: int = 2,
                 method: Optional[SummarizationMethod] = None) -> SummaryResult:
        """生成摘要"""
        import time
        start_time = time.time()
        
        use_method = method or self.method
        
        # 预处理
        clean_text = TextPreprocessor.preprocess(text)
        sentences = TextPreprocessor.split_sentences(clean_text)
        
        if not sentences:
            return SummaryResult(
                summary="无法生成摘要：文本太短或无效",
                method=use_method,
                compression_ratio=0.0,
                key_points=[],
                confidence=0.0,
                processing_time_ms=0.0
            )
        
        # TF-IDF评分
        self.tfidf_scorer.fit(sentences)
        tfidf_scores = [self.tfidf_scorer.score(s) for s in sentences]
        
        # TextRank评分
        textrank_scores = self.textrank_scorer.score(sentences)
        
        # 根据方法组合分数
        if use_method == SummarizationMethod.TEXTRANK:
            final_scores = textrank_scores
        elif use_method == SummarizationMethod.TF_IDF:
            final_scores = tfidf_scores
        else:  # HYBRID
            final_scores = [
                0.5 * t + 0.5 * f 
                for t, f in zip(textrank_scores, tfidf_scores)
            ]
        
        # 生成摘要
        summary = self._extractive_summary(sentences, final_scores, max_length, min_sentences)
        
        # 生成关键点
        key_points = self._generate_key_points(sentences, final_scores)
        
        # 计算压缩比
        original_length = len(clean_text)
        summary_length = len(summary)
        compression_ratio = summary_length / original_length if original_length > 0 else 0
        
        # 计算置信度
        top_score = max(final_scores) if final_scores else 0
        confidence = min(0.9, top_score / max(sum(textrank_scores), sum(tfidf_scores)) * 10) if (sum(textrank_scores) + sum(tfidf_scores)) > 0 else 0.5
        
        processing_time = (time.time() - start_time) * 1000
        
        return SummaryResult(
            summary=summary if summary else "文本太短，无需摘要",
            method=use_method,
            compression_ratio=compression_ratio,
            key_points=key_points,
            confidence=confidence,
            processing_time_ms=processing_time
        )
    
    def analyze(self, text: str) -> Dict:
        """全面分析文本"""
        text_type = self.detect_text_type(text)
        keywords = self.keyword_extractor.extract(text)
        
        summary = self.summarize(text)
        
        return {
            "text_type": text_type.value,
            "keywords": [{"word": k, "score": v} for k, v in keywords],
            "summary": summary.summary,
            "compression_ratio": f"{summary.compression_ratio:.1%}",
            "confidence": f"{summary.confidence:.2f}",
            "key_points": summary.key_points
        }


def demo():
    """演示"""
    print("=" * 60)
    print("🧠 智能文本摘要生成器 - 演示")
    print("=" * 60)
    
    # 测试文本
    test_texts = {
        "news": """新华社北京2月3日电 近日，人工智能领域传来重磅消息。
多个科技巨头宣布加大在生成式AI领域的投入。
专家表示，这将推动人工智能技术的快速发展。
预计未来几年，AI将在医疗、教育、金融等领域发挥重要作用。
与此同时，各国政府也在积极制定AI监管政策。
分析认为，在创新与监管之间找到平衡至关重要。""",
        
        "tech": """机器学习是人工智能的核心分支。
它使计算机能够从数据中学习，而无需明确编程。
常见的机器学习算法包括监督学习、无监督学习和强化学习。
监督学习需要标注数据来训练模型。
无监督学习则用于发现数据中的隐藏模式。
深度学习是机器学习的一个重要子领域，使用多层神经网络。
近年来，深度学习在图像识别、自然语言处理等领域取得突破。""",
        
        "academic": """本研究探讨了深度学习在自然语言处理中的应用。
首先，我们回顾了相关工作的理论基础。
然后，我们提出了一种新的神经网络架构。
实验结果表明，该方法在多个基准测试上取得了最先进的结果。
与现有方法相比，我们的方法在准确率和效率上都有显著提升。
未来的研究方向包括扩展模型规模和探索新的训练策略。"""
    }
    
    summarizer = SmartTextSummarizer()
    
    for name, text in test_texts.items():
        print(f"\n📝 {name.upper()} 文本摘要:")
        print("-" * 40)
        
        result = summarizer.summarize(text)
        
        print(f"摘要: {result.summary[:150]}...")
        print(f"压缩比: {result.compression_ratio:.1%}")
        print(f"置信度: {result.confidence:.2f}")
        print(f"处理时间: {result.processing_time_ms:.1f}ms")
    
    # 完整分析演示
    print("\n" + "=" * 60)
    print("📊 文本分析演示")
    print("=" * 60)
    
    analysis = summarizer.analyze(test_texts["tech"])
    print(f"\n文本类型: {analysis['text_type']}")
    print(f"\n关键词:")
    for kw in analysis["keywords"][:5]:
        print(f"  • {kw['word']}: {kw['score']:.3f}")
    print(f"\n关键要点:")
    for i, point in enumerate(analysis['key_points'], 1):
        print(f"  {i}. {point[:60]}...")
    
    print("\n" + "=" * 60)
    print("✨ 演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
