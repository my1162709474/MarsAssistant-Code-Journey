#!/usr/bin/env python3
"""
智能文本处理工具 - 文本清洗、格式化、摘要提取、关键词提取
支持命令行交互和批量处理
"""

import re
import json
from collections import Counter
from typing import List, Dict, Tuple, Optional

class SmartTextProcessor:
    """智能文本处理器"""
    
    def __init__(self):
        # 中文停用词列表
        self.stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '么', '她', '他', '它', '们', '这个', '那个', '什么', '如何',
            '为什么', '怎么样', '哪些', '哪个', '可以', '能够', '应该', '需要', '可能', '知道',
            '只', '但', '因为', '所以', '如果', '虽然', '然后', '还是', '已经', '很多',
            '我们', '你们', '他们', '她们', '它们', '自己', '这里', '那里', '这样', '那样'
        ])
        
        # 英文停用词
        self.english_stopwords = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our',
            'their', 'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
            'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'also'
        ])
    
    def clean_text(self, text: str, remove_numbers: bool = False) -> str:
        """清洗文本"""
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # 移除特殊字符（保留中文、英文、数字、常用标点）
        if remove_numbers:
            text = re.sub(r'[0-9]+', '', text)
        
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        return text
    
    def remove_stopwords(self, text: str, lang: str = 'zh') -> List[str]:
        """移除停用词"""
        words = text.split()
        
        if lang == 'zh':
            return [w for w in words if w not in self.stopwords and len(w) > 1]
        elif lang == 'en':
            return [w.lower() for w in words if w.lower() not in self.english_stopwords and len(w) > 2]
        else:
            stopwords = self.stopwords | self.english_stopwords
            return [w.lower() for w in words if w.lower() not in stopwords and len(w) > 2]
    
    def extract_keywords(self, text: str, top_n: int = 10, lang: str = 'zh') -> List[Tuple[str, float]]:
        """提取关键词 - 基于TF频率"""
        cleaned = self.clean_text(text)
        words = self.remove_stopwords(cleaned, lang)
        
        if not words:
            return []
        
        word_freq = Counter(words)
        total = sum(word_freq.values())
        
        # 计算TF分数
        keywords = [(word, freq / total) for word, freq in word_freq.most_common(top_n)]
        return keywords
    
    def extract_bigrams(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """提取双词组合"""
        cleaned = self.clean_text(text)
        words = self.remove_stopwords(cleaned)
        
        if len(words) < 2:
            return []
        
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        bigram_freq = Counter(bigrams)
        total = sum(bigram_freq.values())
        
        return [(bg, freq / total) for bg, freq in bigram_freq.most_common(top_n)]
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成摘要 - 抽取式"""
        if not text:
            return ""
        
        # 按句号、问号、感叹号分割
        sentences = re.split(r'[。！？.!?]', text)
        summary = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if current_length + len(sentence) <= max_length:
                summary.append(sentence)
                current_length += len(sentence)
        
        if summary:
            return ''.join(summary)
        return text[:max_length] + ('...' if len(text) > max_length else '')
    
    def extract_sentences(self, text: str, max_sentences: int = 5) -> List[str]:
        """提取关键句子"""
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 返回前N个句子
        return sentences[:max_sentences]
    
    def calculate_readability(self, text: str) -> Dict:
        """计算可读性指标"""
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = text.split()
        
        if not sentences or not words:
            return {'score': 0, 'level': '无法计算', 'avg_sentence_len': 0, 'avg_word_len': 0}
        
        # 平均句子长度
        avg_sentence_len = len(words) / len(sessions)
        
        # 平均词长度
        avg_word_len = sum(len(w) for w in words) / len(words) if words else 0
        
        # 简单可读性评分 (0-100)
        # 句子短、词短 = 容易阅读
        readability = max(0, min(100, 100 - avg_sentence_len * 2 - avg_word_len * 5))
        
        # 确定阅读级别
        if readability >= 80:
            level = '非常简单'
        elif readability >= 60:
            level = '简单'
        elif readability >= 40:
            level = '中等'
        elif readability >= 20:
            level = '较难'
        else:
            level = '非常难'
        
        return {
            'score': round(readability, 1),
            'level': level,
            'avg_sentence_len': round(avg_sentence_len, 1),
            'avg_word_len': round(avg_word_len, 1),
            'sentence_count': len(sentences),
            'word_count': len(words)
        }
    
    def analyze_text(self, text: str, lang: str = 'zh') -> Dict:
        """完整文本分析"""
        cleaned = self.clean_text(text)
        words = self.remove_stopwords(cleaned, lang)
        
        return {
            'statistics': {
                'char_count': len(text),
                'word_count': len(text.split()),
                'clean_word_count': len(words),
                'sentence_count': len(re.split(r'[。！？.!?]', text))
            },
            'keywords': self.extract_keywords(text, 10, lang),
            'bigrams': self.extract_bigrams(text, 5),
            'summary': self.generate_summary(text, 200),
            'readability': self.calculate_readability(text)
        }
    
    def format_for_markdown(self, text: str, title: str = "文本分析报告", lang: str = 'zh') -> str:
        """格式化为Markdown报告"""
        analysis = self.analyze_text(text, lang)
        keywords = analysis['keywords']
        bigrams = analysis['bigrams']
        readability = analysis['readability']
        
        lines = [
            f"# {title}",
            f"**分析时间**: 自动生成",
            "",
            "## 📊 基本统计",
            f"- **字符数**: {analysis['statistics']['char_count']}",
            f"- **词数**: {analysis['statistics']['word_count']}",
            f"- **清洗后词数**: {analysis['statistics']['clean_word_count']}",
            f"- **句子数**: {analysis['statistics']['sentence_count']}",
            "",
            "## 🎯 关键词 Top 10",
        ]
        
        for i, (word, score) in enumerate(keywords, 1):
            bar = '█' * int(score * 50) if score > 0 else ''
            lines.append(f"{i}. **{word}** `{score:.4f}` {bar}")
        
        if bigrams:
            lines.extend([
                "",
                "## 🔗 关键短语 Top 5",
            ])
            for i, (phrase, score) in enumerate(bigrams, 1):
                lines.append(f"{i}. {phrase} `{score:.4f}`")
        
        lines.extend([
            "",
            "## 📖 可读性分析",
            f"- **阅读难度**: {readability['level']} ({readability['score']}/100)",
            f"- **平均句长**: {readability['avg_sentence_len']} 词/句",
            f"- **平均词长**: {readability['avg_word_len']} 字符/词",
            "",
            "## 📋 文本摘要",
            analysis['summary'],
            "",
            "---",
            "*由 SmartTextProcessor 自动生成*"
        ])
        
        return '\n'.join(lines)
    
    def compare_texts(self, texts: List[Dict[str, str]]) -> Dict:
        """对比多个文本"""
        results = []
        for i, item in enumerate(texts):
            analysis = self.analyze_text(item['content'], item.get('lang', 'zh'))
            results.append({
                'name': item.get('name', f'文本{i+1}'),
                'statistics': analysis['statistics'],
                'readability': analysis['readability'],
                'top_keywords': analysis['keywords'][:3]
            })
        return results

# ============ CLI 接口 ============
def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='智能文本处理工具')
    parser.add_argument('text', nargs='?', help='要分析的文本')
    parser.add_argument('-f', '--file', help='输入文件路径')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json', help='输出格式')
    parser.add_argument('--lang', choices=['zh', 'en', 'mix'], default='zh', help='文本语言')
    parser.add_argument('--summary', action='store_true', help='只输出摘要')
    parser.add_argument('--keywords', action='store_true', help='只输出关键词')
    parser.add_argument('--readability', action='store_true', help='只输出可读性')
    parser.add_argument('--compare', action='store_true', help='对比模式')
    
    args = parser.parse_args()
    
    processor = SmartTextProcessor()
    
    # 获取文本
    if args.interactive:
        print("输入文本（Ctrl+D 结束）:")
        text = sys.stdin.read()
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        return
    
    # 分析
    if args.compare and args.file:
        # 对比模式：解析多个文件
        files = args.file.split(',')
        texts = []
        for f in files:
            with open(f.strip(), 'r', encoding='utf-8') as fp:
                texts.append({'name': f.strip(), 'content': fp.read()})
        result = processor.compare_texts(texts)
        output = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.summary:
        output = processor.generate_summary(text)
    elif args.keywords:
        keywords = processor.extract_keywords(text, lang=args.lang)
        output = json.dumps(keywords, ensure_ascii=False, indent=2)
    elif args.readability:
        output = json.dumps(processor.calculate_readability(text), ensure_ascii=False, indent=2)
    elif args.format == 'markdown':
        output = processor.format_for_markdown(text, lang=args.lang)
    else:
        output = json.dumps(processor.analyze_text(text, args.lang), ensure_ascii=False, indent=2)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
