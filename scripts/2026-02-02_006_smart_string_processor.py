#!/usr/bin/env python3
"""
智能字符串处理器 - Day 6
字符串处理工具集，包含常用字符串操作

功能:
- 字符串相似度计算 (Levenshtein距离)
- 字符串去重和去停用词
- 敏感信息脱敏
- 中英文混合文本处理
- 文本格式化
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import Counter


class SmartStringProcessor:
    """智能字符串处理器"""
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """计算编辑距离 (Levenshtein距离)"""
        if len(s1) < len(s2):
            return SmartStringProcessor.levenshtein_distance(s2, s1)
        
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
    
    @staticmethod
    def similarity_ratio(s1: str, s2: str) -> float:
        """计算相似度比例 (0-1)"""
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        distance = SmartStringProcessor.levenshtein_distance(s1, s2)
        return 1.0 - (distance / max_len)
    
    @staticmethod
    def remove_duplicates(text: str, keep_order: bool = True) -> str:
        """去除重复字符"""
        if keep_order:
            seen = set()
            result = []
            for char in text:
                if char not in seen:
                    seen.add(char)
                    result.append(char)
            return ''.join(result)
        else:
            return ''.join(sorted(set(text), key=text.index))
    
    @staticmethod
    def remove_stopwords(text: str, language: str = 'en') -> str:
        """去除停用词"""
        # 英文停用词
        en_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'would', 'should', 'could', 'ought', 'will', 'shall', 'can', 'may',
            'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
            'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',
            'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom',
            'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also'
        }
        
        # 中文停用词 (常用)
        zh_stopwords = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', '那', '么', '她', '他', '它', '们', '为', '什么',
            '哪个', '哪个', '谁', '怎么', '怎样', '如何', '为什么', '但是', '但是', '但',
            '如果', '因为', '所以', '虽然', '然而', '并且', '而且', '或者', '还是',
            '于是', '因此', '于是', '只不过', '只有', '只要', '不管', '无论', '不论'
        }
        
        words = re.findall(r'\b\w+\b', text)
        stopwords = en_stopwords if language == 'en' else zh_stopwords
        
        if language == 'zh':
            # 中文按字符处理
            result = ''.join([w for w in text if w not in zh_stopwords and not w.isdigit()])
            return result
        else:
            return ' '.join([w for w in words if w.lower() not in stopwords])
    
    @staticmethod
    def mask_sensitive_info(text: str, patterns: Dict[str, str] = None) -> str:
        """敏感信息脱敏"""
        if patterns is None:
            patterns = {
                r'\b\d{11}\b': lambda m: m.group()[:3] + '****' + m.group()[7:],
                r'\b[\w\.-]+@[\w\.-]+\.\w+\b': lambda m: m.group()[:2] + '***@***.com',
                r'\b\d{6}\b': '******',
                r'\b\d{3,4}[- ]?\d{3,4}[- ]?\d{3,4}\b': lambda m: '***-***-***',
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b': '***.***.***.***'
            }
        
        result = text
        for pattern, replacer in patterns.items():
            if callable(replacer):
                result = re.sub(pattern, replacer, result)
            else:
                result = re.sub(pattern, replacer, result)
        
        return result
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """文本标准化"""
        # 统一空格
        text = re.sub(r'\s+', ' ', text)
        # 去除多余标点
        text = re.sub(r'([。！？，、]){2,}', r'\1', text)
        # 首尾空格
        text = text.strip()
        # 首字母大写
        text = text[0].upper() + text[1:] if text else text
        return text
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """提取关键词 (基于词频)"""
        # 简单分词
        words = re.findall(r'\b\w+\b', text.lower())
        # 过滤短词
        words = [w for w in words if len(w) > 2]
        # 词频统计
        word_counts = Counter(words)
        return word_counts.most_common(top_n)
    
    @staticmethod
    def split_chinese_english(text: str) -> Dict[str, List[str]]:
        """中英文分离"""
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
        english = re.findall(r'[a-zA-Z]+', text)
        numbers = re.findall(r'\d+', text)
        return {
            'chinese': chinese,
            'english': english,
            'numbers': numbers
        }
    
    @staticmethod
    def camel_to_snake(name: str) -> str:
        """驼峰转下划线"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def snake_to_camel(name: str) -> str:
        """下划线转驼峰"""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])


def demo():
    """演示"""
    processor = SmartStringProcessor()
    
    # 1. 编辑距离
    s1 = "kitten"
    s2 = "sitting"
    dist = processor.levenshtein_distance(s1, s2)
    sim = processor.similarity_ratio(s1, s2)
    print(f"编辑距离: '{s1}' -> '{s2}' = {dist}")
    print(f"相似度: {sim:.2%}")
    
    # 2. 去除重复
    text = "hello world"
    deduped = processor.remove_duplicates(text)
    print(f"去重: '{text}' -> '{deduped}'")
    
    # 3. 敏感信息脱敏
    sensitive = "联系我: 13812345678 或 admin@example.com"
    masked = processor.mask_sensitive_info(sensitive)
    print(f"脱敏: '{masked}'")
    
    # 4. 中英文分离
    mixed = "Hello世界123"
    separated = processor.split_chinese_english(mixed)
    print(f"分离: {separated}")
    
    # 5. 驼峰下划线转换
    camel = "myVariableName"
    snake = processor.camel_to_snake(camel)
    print(f"驼峰->下划线: '{camel}' -> '{snake}'")
    
    # 6. 关键词提取
    sample = "Python programming language is great for machine learning and AI"
    keywords = processor.extract_keywords(sample)
    print(f"关键词: {keywords}")


if __name__ == "__main__":
    demo()
