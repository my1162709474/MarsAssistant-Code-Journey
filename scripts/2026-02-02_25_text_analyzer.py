#!/usr/bin/env python3
"""
文本统计分析工具
支持词频统计、句子分析、字符统计等功能
"""

import re
import json
from collections import Counter
from typing import Dict, List, Tuple
import argparse


class TextAnalyzer:
    """文本统计分析器"""
    
    def __init__(self, text: str):
        self.text = text
        self.words = self._extract_words()
        self.sentences = self._split_sentences()
    
    def _extract_words(self) -> List[str]:
        """提取所有单词（小写）"""
        return re.findall(r'\b[a-zA-Z]+\b', self.text.lower())
    
    def _split_sentences(self) -> List[str]:
        """分割句子"""
        return re.split(r'[.!?]+', self.text)
    
    def word_frequency(self, top_n: int = 10) -> Dict[str, int]:
        """词频统计"""
        return dict(Counter(self.words).most_common(top_n))
    
    def char_frequency(self) -> Dict[str, int]:
        """字符频率统计"""
        return dict(Counter(self.text))
    
    def stats(self) -> Dict:
        """基本统计信息"""
        return {
            "char_count": len(self.text),
            "word_count": len(self.words),
            "sentence_count": len(self.sentences),
            "avg_word_length": sum(len(w) for w in self.words) / len(self.words) if self.words else 0,
            "avg_sentence_length": len(self.words) / len(self.sentences) if self.sentences else 0,
            "unique_words": len(set(self.words)),
            "vocabulary_richness": len(set(self.words)) / len(self.words) if self.words else 0,
        }
    
    def find_keywords(self, min_length: int = 4) -> List[Tuple[str, int]]:
        """查找关键词（长度>=min_length的高频词）"""
        stopwords = {'the', 'and', 'are', 'was', 'were', 'have', 'has', 'been',
                    'this', 'that', 'with', 'for', 'from', 'they', 'will', 'would'}
        keywords = [(w, c) for w, c in Counter(self.words).items()
                   if len(w) >= min_length and w not in stopwords]
        return sorted(keywords, key=lambda x: x[1], reverse=True)[:10]
    
    def to_json(self) -> str:
        """导出为JSON格式"""
        result = {
            "stats": self.stats(),
            "word_frequency": self.word_frequency(20),
            "top_keywords": self.find_keywords(),
            "char_frequency": dict(sorted(self.char_frequency().items(), 
                                         key=lambda x: x[1], reverse=True)[:10])
        }
        return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='文本统计分析工具')
    parser.add_argument('input', nargs='?', help='输入文件路径（可选，默认从 stdin 读取）')
    parser.add_argument('-o', '--output', help='输出JSON文件路径')
    parser.add_argument('-t', '--top', type=int, default=10, help='显示TOP N词频（默认10）')
    parser.add_argument('-k', '--keywords', action='store_true', help='显示关键词')
    parser.add_argument('-s', '--stats', action='store_true', help='显示基本统计')
    
    args = parser.parse_args()
    
    # 读取文本
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = input("请输入文本：\n") + "\n"
    
    analyzer = TextAnalyzer(text)
    
    if args.stats:
        print("\n📊 基本统计信息:")
        for k, v in analyzer.stats().items():
            print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
    
    if args.top:
        print(f"\n🔤 TOP {args.top} 词频:")
        for word, count in analyzer.word_frequency(args.top).items():
            print(f"  {word}: {count}")
    
    if args.keywords:
        print("\n🔑 关键词:")
        for word, count in analyzer.find_keywords():
            print(f"  {word}: {count}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(analyzer.to_json())
        print(f"\n✅ 已保存到 {args.output}")
    
    if not any([args.stats, args.top, args.keywords, args.output]):
        print(analyzer.to_json())


if __name__ == '__main__':
    main()
