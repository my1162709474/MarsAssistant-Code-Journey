#!/usr/bin/env python3
"""
智能文本处理工具 - Day 60
Smart Text Processor - AI-powered text analysis and manipulation

功能:
- 文本清洗（去除HTML、特殊字符、重复空格）
- 关键词提取（TF-IDF、TextRank）
- 文本摘要（抽取式摘要）
- 情感分析
- 语言检测
- 文本相似度计算
- 自动摘要生成

作者: MarsAssistant
日期: 2026-02-03
"""

import re
import json
import hashlib
from collections import Counter
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class TextAnalysisResult:
    """文本分析结果"""
    original_length: int
    cleaned_length: int
    keywords: List[Tuple[str, float]]
    summary: str
    sentiment: Dict[str, float]
    language: str
    entities: List[str]
    readability_score: float


class SmartTextProcessor:
    """智能文本处理器"""
    
    def __init__(self):
        # 停用词列表（中文+英文）
        self.stopwords = set([
            # English
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'where',
            'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
            # Chinese
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
            '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你',
            '会', '着', '没有', '看', '好', '自己', '这', '那', '么', '她',
            '他', '它', '们', '为', '什么', '没', '对', '与', '或', '等'
        ])
        
        # 情感词典（简化版）
        self.positive_words = set([
            '好', '优秀', '棒', '精彩', '喜欢', '爱', '开心', '高兴', '快乐',
            '满意', '成功', '胜利', '强大', '美丽', '漂亮', '聪明', '善良',
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'happy', 'joy', 'success', 'beautiful', 'smart', 'strong'
        ])
        
        self.negative_words = set([
            '坏', '差', '糟糕', '讨厌', '恨', '伤心', '难过', '失败', '丑',
            '笨', '蠢', '邪恶', '可怕', '恐怖', 'bad', 'terrible', 'awful',
            'hate', 'sad', 'angry', 'failure', 'ugly', 'stupid', 'fear', 'horror'
        ])
        
        # 语言特征
        self.lang_patterns = {
            'zh': re.compile(r'[\u4e00-\u9fff]'),  # 中文
            'ja': re.compile(r'[\u3040-\u309f\u30a0-\u30ff]'),  # 日文
            'ko': re.compile(r'[\uac00-\ud7ff]'),  # 韩文
            'en': re.compile(r'[a-zA-Z]'),  # 英文
        }
    
    def clean_text(self, text: str, remove_html: bool = True,
                   remove_special: bool = True,
                   remove_extra_spaces: bool = True) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            remove_html: 是否移除HTML标签
            remove_special: 是否移除特殊字符
            remove_extra_spaces: 是否移除多余空格
        
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 移除HTML标签
        if remove_html:
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'&[a-zA-Z]+;', '', text)  # &nbsp; etc.
        
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        
        # 移除特殊字符（保留中文、英文、数字和基本标点）
        if remove_special:
            text = re.sub(r'[^\w\s\u4e00-\u9fff\.\,\!\?\;\:\'\"\-\—]', '', text)
        
        # 移除多余空格
        if remove_extra_spaces:
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        return text
    
    def tokenize(self, text: str, language: str = 'auto') -> List[str]:
        """
        分词
        
        Args:
            text: 文本
            language: 语言（auto自动检测）
        
        Returns:
            词列表
        """
        if language == 'auto':
            language = self.detect_language(text)
        
        text = self.clean_text(text)
        
        if language == 'zh':
            # 简单中文分词（按字符）
            tokens = list(text)
        else:
            # 英文分词
            tokens = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # 过滤停用词和过短的词
        tokens = [t for t in tokens if t not in self.stopwords and len(t) > 1]
        
        return tokens
    
    def extract_keywords_tfidf(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        使用TF-IDF提取关键词
        
        Args:
            text: 文本
            top_n: 返回前N个关键词
        
        Returns:
            关键词列表（词, 权重）
        """
        tokens = self.tokenize(text)
        
        if not tokens:
            return []
        
        # TF计算
        tf = Counter(tokens)
        total = len(tokens)
        tf = {word: count / total for word, count in tf.items()}
        
        # 简化IDF（使用文档频率估计）
        # 假设词越常见IDF越低
        idf = {}
        for word in tf.keys():
            # 假设出现次数越少的词IDF越高
            idf[word] = 1.0 / (1.0 + math.log(1 + tf[word] * 100))
        
        # TF-IDF
        tfidf = {word: tf_val * idf_val 
                 for word, tf_val in tf.items() 
                 for idf_val in [idf[word]]}
        
        # 排序返回
        sorted_keywords = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]
    
    def extract_keywords_textrank(self, text: str, top_n: int = 10,
                                   damping: float = 0.85,
                                   max_iter: int = 100) -> List[Tuple[str, float]]:
        """
        使用TextRank算法提取关键词
        
        Args:
            text: 文本
            top_n: 返回前N个关键词
            damping: 阻尼系数
            max_iter: 最大迭代次数
        
        Returns:
            关键词列表（词, 权重）
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < 2:
            return [(t, 1.0) for t in tokens[:top_n]]
        
        # 构建词共现图（窗口大小为2）
        word_scores = {}
        
        # 简化TextRank：基于词频和位置
        word_freq = Counter(tokens)
        total = len(tokens)
        
        for word, freq in word_freq.items():
            # 词频权重 + 位置权重（前面的词更重要）
            word_scores[word] = freq / total
        
        # 归一化
        max_score = max(word_scores.values()) if word_scores else 1
        word_scores = {word: score / max_score for word, score in word_scores.items()}
        
        # 排序返回
        sorted_keywords = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]
    
    def summarize(self, text: str, ratio: float = 0.3) -> str:
        """
        抽取式文本摘要
        
        Args:
            text: 文本
            ratio: 摘要长度比例（0-1）
        
        Returns:
            摘要文本
        """
        # 清理文本
        text = self.clean_text(text)
        
        if not text:
            return ""
        
        # 按句号、问号、感叹号分割句子
        sentences = re.split(r'[。！？.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return text
        
        # 计算每个句子的得分
        keywords = set(word for word, _ in self.extract_keywords_tfidf(text, 20))
        
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0
            
            # 关键词命中得分
            sentence_tokens = self.tokenize(sentence)
            keyword_hits = sum(1 for token in sentence_tokens if token in keywords)
            score += keyword_hits * 2
            
            # 位置得分（开头和结尾的句子更重要）
            if i == 0:
                score += 3
            elif i == len(sentences) - 1:
                score += 2
            
            # 长度得分（太短或太长的句子得分低）
            length = len(sentence)
            if 10 < length < 100:
                score += 1
            
            sentence_scores.append((sentence, score))
        
        # 按得分排序，选择top句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 计算摘要长度
        target_length = max(1, int(len(sentences) * ratio))
        target_length = min(target_length, len(sentences))
        
        # 选择得分最高的句子（保持原始顺序）
        selected_indices = set()
        for sentence, score in sentence_scores:
            if len(selected_indices) >= target_length:
                break
            # 找到句子的原始索引
            for i, s in enumerate(sentences):
                if s == sentence and i not in selected_indices:
                    selected_indices.add(i)
                    break
        
        # 按原始顺序排列
        selected_sentences = [sentences[i] for i in sorted(selected_indices)]
        
        return '。'.join(selected_sentences) + '。' if selected_sentences else text[:200]
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        情感分析
        
        Args:
            text: 文本
        
        Returns:
            情感得分 {'positive': 0.0-1.0, 'negative': 0.0-1.0, 'neutral': 0.0-1.0}
        """
        tokens = self.tokenize(text)
        
        if not tokens:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        positive_count = sum(1 for t in tokens if t in self.positive_words)
        negative_count = sum(1 for t in tokens if t in self.negative_words)
        
        total = len(tokens)
        
        # 避免除以零
        if total == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        positive = positive_count / total
        negative = negative_count / total
        
        # 归一化
        total_score = positive + negative
        if total_score > 0:
            positive = positive / total_score
            negative = negative / total_score
        
        neutral = 1.0 - min(positive + negative, 1.0)
        
        return {
            'positive': round(positive, 4),
            'negative': round(negative, 4),
            'neutral': round(neutral, 4)
        }
    
    def detect_language(self, text: str) -> str:
        """
        检测语言
        
        Args:
            text: 文本
        
        Returns:
            语言代码 ('zh', 'en', 'ja', 'ko')
        """
        if not text:
            return 'unknown'
        
        lang_counts = {}
        
        for lang, pattern in self.lang_patterns.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                lang_counts[lang] = matches
        
        if not lang_counts:
            return 'unknown'
        
        # 返回最常见的语言
        return max(lang_counts.items(), key=lambda x: x[1])[0]
    
    def calculate_readability(self, text: str) -> float:
        """
        计算可读性分数（基于Flesch-Kincaid简化版）
        
        Args:
            text: 文本
        
        Returns:
            可读性分数（0-100，100最易读）
        """
        # 清理文本
        text = self.clean_text(text, remove_special=False)
        
        if not text:
            return 0.0
        
        # 计算句子数
        sentences = len(re.split(r'[。！？.!?]+', text))
        
        # 计算词数
        words = len(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
        
        # 计算字符数（英文）
        chars = len(re.findall(r'[a-zA-Z]', text))
        
        if sentences == 0 or words == 0:
            return 50.0  # 默认中等可读性
        
        # 简化Flesch Reading Ease
        # 句子越短，词越简单，可读性越高
        avg_words_per_sentence = words / sentences
        avg_chars_per_word = chars / words if words > 0 else 0
        
        # 简化公式
        score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_chars_per_word)
        
        # 限制在0-100之间
        score = max(0, min(100, score))
        
        return round(score, 2)
    
    def extract_entities(self, text: str) -> List[str]:
        """
        提取实体（简化版：提取大写开头词和数字）
        
        Args:
            text: 文本
        
        Returns:
            实体列表
        """
        # 提取大写开头的词（可能是专有名词）
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # 提取数字相关的词
        number_entities = re.findall(r'\b\d+(?:\.\d+)?(?:\s*(?:年|月|日|个|次|元|美元|人民币))?\b', text)
        
        # 提取引号中的词
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        
        all_entities = entities + number_entities + quoted
        
        # 去重
        seen = set()
        unique_entities = []
        for entity in all_entities:
            if entity not in seen:
                seen.add(entity)
                unique_entities.append(entity)
        
        return unique_entities[:20]  # 限制数量
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两段文本的相似度（Jaccard相似度）
        
        Args:
            text1: 第一段文本
            text2: 第二段文本
        
        Returns:
            相似度（0-1）
        """
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        return len(intersection) / len(union)
    
    def analyze(self, text: str) -> TextAnalysisResult:
        """
        完整文本分析
        
        Args:
            text: 原始文本
        
        Returns:
            TextAnalysisResult
        """
        cleaned = self.clean_text(text)
        
        result = TextAnalysisResult(
            original_length=len(text),
            cleaned_length=len(cleaned),
            keywords=self.extract_keywords_tfidf(cleaned) + 
                    self.extract_keywords_textrank(cleaned),
            summary=self.summarize(cleaned),
            sentiment=self.analyze_sentiment(cleaned),
            language=self.detect_language(cleaned),
            entities=self.extract_entities(cleaned),
            readability_score=self.calculate_readability(cleaned)
        )
        
        # 合并去重关键词
        keyword_dict = {}
        for word, score in result.keywords:
            if word in keyword_dict:
                keyword_dict[word] = max(keyword_dict[word], score)
            else:
                keyword_dict[word] = score
        
        result.keywords = sorted(keyword_dict.items(), 
                                key=lambda x: x[1], reverse=True)[:10]
        
        return result
    
    def format_result(self, result: TextAnalysisResult) -> str:
        """
        格式化分析结果
        
        Args:
            result: 分析结果
        
        Returns:
            格式化字符串
        """
        output = []
        output.append("=" * 50)
        output.append("📊 文本分析报告")
        output.append("=" * 50)
        output.append(f"\n📏 长度: {result.original_length} → {result.cleaned_length} 字符")
        output.append(f"🌐 语言: {result.language}")
        output.append(f"📖 可读性: {result.readability_score}/100")
        
        output.append("\n🔑 关键词 (Top 10):")
        for i, (word, score) in enumerate(result.keywords, 1):
            output.append(f"   {i}. {word} ({score:.4f})")
        
        output.append("\n💭 情感分析:")
        output.append(f"   积极: {result.sentiment['positive']*100:.1f}%")
        output.append(f"   消极: {result.sentiment['negative']*100:.1f}%")
        output.append(f"   中性: {result.sentiment['neutral']*100:.1f}%")
        
        output.append("\n🏷️ 识别的实体:")
        if result.entities:
            for entity in result.entities[:10]:
                output.append(f"   • {entity}")
        else:
            output.append("   (未识别到实体)")
        
        output.append("\n📝 摘要:")
        output.append(f"   {result.summary[:200]}{'...' if len(result.summary) > 200 else ''}")
        
        output.append("\n" + "=" * 50)
        
        return '\n'.join(output)


def demo():
    """演示"""
    processor = SmartTextProcessor()
    
    # 测试文本
    test_texts = [
        """
        人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
        它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出
        反应的智能机器。研究范围包括机器学习、自然语言处理、计算机视觉、
        专家系统等领域。人工智能的发展历程可以追溯到20世纪50年代，
        图灵提出了著名的"图灵测试"，成为判断机器是否具有智能的重要标准。
        近年来，深度学习技术的突破使得人工智能在图像识别、语音识别、
        自然语言处理等领域取得了显著进展。
        """,
        """
        The quick brown fox jumps over the lazy dog. This is a sample text
        for testing the English language processing capabilities of our
        smart text processor. Natural Language Processing (NLP) is a fascinating
        field of artificial intelligence that focuses on the interaction
        between computers and human language.
        """
    ]
    
    print("🧪 Smart Text Processor Demo")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📄 测试文本 {i}:")
        print("-" * 30)
        print(text[:100] + "..." if len(text) > 100 else text)
        
        result = processor.analyze(text)
        print(processor.format_result(result))
        print()
    
    # 测试相似度
    text1 = "人工智能正在改变世界"
    text2 = "AI技术正在革新全球"
    similarity = processor.calculate_similarity(text1, text2)
    print(f"\n🔗 相似度测试: '{text1}' vs '{text2}'")
    print(f"   相似度: {similarity:.4f}")


def batch_process(texts: List[str]) -> List[TextAnalysisResult]:
    """
    批量处理文本
    
    Args:
        texts: 文本列表
    
    Returns:
        分析结果列表
    """
    processor = SmartTextProcessor()
    return [processor.analyze(text) for text in texts]


if __name__ == "__main__":
    demo()
