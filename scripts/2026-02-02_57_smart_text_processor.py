#!/usr/bin/env python3
"""
智能文本处理工具 - Day 57
多功能的文本清洗、格式化、提取和转换工具

功能模块：
1. 文本清洗 - 去除冗余、规范格式
2. 格式转换 - Markdown/HTML/JSON/YAML互转
3. 实体提取 - 提取人名/地名/时间/数字
4. 文本摘要 - 自动生成摘要
5. 关键词提取 - TF-IDF关键词提取
6. 文本对比 - 计算相似度和差异
"""

import re
import json
import yaml
import hashlib
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter
from difflib import SequenceMatcher
import html


class TextCleaner:
    """文本清洗处理器"""
    
    def __init__(self):
        # 常见空白字符模式
        self.whitespace_pattern = re.compile(r'\s+')
        # 常见冗余模式
        self.redundant_patterns = [
            (r'^\s*[\r\n]+\s*', ''),           # 开头的空行
            (r'\s*[\r\n]+\s*$', ''),           # 结尾的空行
            (r'([。！？；：」』）】])(\s*)([「『（【])', r'\1\3'),  # 粘连标点
            (r'(\d{4})-(\d{2})-(\d{2})', r'\1年\2月\3日'),  # 日期格式
        ]
    
    def remove_extra_whitespace(self, text: str) -> str:
        """去除多余空白字符"""
        text = self.whitespace_pattern.sub(' ', text)
        return text.strip()
    
    def remove_redundant_lines(self, text: str, keep_blank_lines: int = 0) -> str:
        """去除多余的空行"""
        lines = text.split('\n')
        result = []
        blank_count = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_count += 1
                if blank_count <= keep_blank_lines:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)
        
        return '\n'.join(result)
    
    def normalize_punctuation(self, text: str) -> str:
        """规范标点符号"""
        # 全角转半角
        fullwidth = '，。！？；：""''（）【】《》——…'
        halfwidth = ',.!?;:"'\(\)[]<>—...'
        translator = str.maketrans(fullwidth, halfwidth)
        text = text.translate(translator)
        
        # 修复粘连标点
        for pattern, replacement in self.redundant_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def clean_code_blocks(self, text: str, languages: List[str] = None) -> str:
        """清理代码块，保留内容"""
        if languages is None:
            languages = ['python', 'javascript', 'java', 'cpp', 'go', 'rust']
        
        # 移除代码块标记，保留内容
        for lang in languages:
            pattern = rf'```{lang}\n([\s\S]*?)```'
            text = re.sub(pattern, r'\1', text)
        
        # 移除行内代码
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        return text
    
    def full_clean(self, text: str) -> str:
        """完整的文本清洗流程"""
        text = self.remove_extra_whitespace(text)
        text = self.normalize_punctuation(text)
        text = self.remove_redundant_lines(text, keep_blank_lines=2)
        return text


class TextFormatter:
    """文本格式转换器"""
    
    @staticmethod
    def markdown_to_html(markdown: str) -> str:
        """Markdown转HTML"""
        # 标题
        for i in range(6, 0, -1):
            markdown = re.sub(
                f'^({"#" * i})\s*(.+)$',
                f'<h{i}>\2</h{i}>',
                markdown,
                flags=re.MULTILINE
            )
        
        # 粗体
        markdown = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', markdown)
        markdown = re.sub(r'__(.+?)__', r'<b>\1</b>', markdown)
        
        # 斜体
        markdown = re.sub(r'\*(.+?)\*', r'<i>\1</i>', markdown)
        markdown = re.sub(r'_(.+?)_', r'<i>\1</i>', markdown)
        
        # 删除线
        markdown = re.sub(r'~~(.+?)~~', r'<del>\1</del>', markdown)
        
        # 链接
        markdown = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', markdown)
        
        # 无序列表
        markdown = re.sub(r'^[-*+]\s+(.+)$', r'<li>\1</li>', markdown, flags=re.MULTILINE)
        
        # 有序列表
        markdown = re.sub(r'^\d+\.\s+(.+)$', r'<li>\1</li>', markdown, flags=re.MULTILINE)
        
        # 代码块
        markdown = re.sub(r'```(\w*)\n([\s\S]*?)```', r'<pre><code class="lang-\1">\2</code></pre>', markdown)
        
        # 行内代码
        markdown = re.sub(r'`([^`]+)`', r'<code>\1</code>', markdown)
        
        # 段落
        paragraphs = markdown.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<') and not p.startswith('</'):
                p = f'<p>{p}</p>'
            html_paragraphs.append(p)
        
        return '\n'.join(html_paragraphs)
    
    @staticmethod
    def json_to_yaml(data: Any, indent: int = 2) -> str:
        """JSON转YAML"""
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, indent=indent)
    
    @staticmethod
    def yaml_to_json(yaml_str: str) -> str:
        """YAML转JSON"""
        data = yaml.safe_load(yaml_str)
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def csv_to_json(csv_str: str, delimiter: str = ',') -> str:
        """CSV转JSON"""
        lines = csv_str.strip().split('\n')
        if not lines:
            return '[]'
        
        headers = lines[0].split(delimiter)
        headers = [h.strip().strip('"').strip("'") for h in headers]
        
        result = []
        for line in lines[1:]:
            values = line.split(delimiter)
            if len(values) == len(headers):
                item = {}
                for i, header in enumerate(headers):
                    value = values[i].strip().strip('"').strip("'")
                    # 尝试转换类型
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '').isdigit():
                        value = float(value)
                    item[header] = value
                result.append(item)
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    @staticmethod
    def json_to_csv(json_str: str, delimiter: str = ',') -> str:
        """JSON转CSV"""
        data = json.loads(json_str)
        if not data:
            return ''
        
        if isinstance(data, dict):
            data = [data]
        
        headers = list(data[0].keys())
        lines = [delimiter.join(headers)]
        
        for item in data:
            values = []
            for header in headers:
                value = str(item.get(header, ''))
                # 处理包含分隔符的情况
                if delimiter in value or '\n' in value:
                    value = f'"{value}"'
                values.append(value)
            lines.append(delimiter.join(values))
        
        return '\n'.join(lines)
    
    @staticmethod
    def text_to_markdown_table(data: List[Dict], alignments: List[str] = None) -> str:
        """文本数据转Markdown表格"""
        if not data:
            return ''
        
        headers = list(data[0].keys())
        if alignments is None:
            alignments = ['left'] * len(headers)
        
        # 计算每列宽度
        col_widths = {}
        for header in headers:
            col_widths[header] = len(header)
        
        for item in data:
            for header in headers:
                value = str(item.get(header, ''))
                col_widths[header] = max(col_widths[header], len(value))
        
        # 构建分隔行
        separator = '|'
        for header in headers:
            width = col_widths[header]
            align = alignments[headers.index(header)]
            if align == 'center':
                separator += f' :{"-" * (width - 2)}: |'
            elif align == 'right':
                separator += f' {"-" * (width - 1)}: |'
            else:
                separator += f' {"-" * width}- |'
        
        # 构建表头
        header_row = '|'
        for header in headers:
            header_row += f' {header.ljust(col_widths[header])} |'
        
        # 构建数据行
        rows = [header_row, separator]
        for item in data:
            row = '|'
            for header in headers:
                value = str(item.get(header, '')).ljust(col_widths[header])
                row += f' {value} |'
            rows.append(row)
        
        return '\n'.join(rows)


class EntityExtractor:
    """实体提取器"""
    
    def __init__(self):
        # 人名模式（简单的中文姓名模式）
        self.name_pattern = re.compile(r'[张李王刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许邓冯韩曹曾彭萧蔡潘田董袁于余叶蒋杜苏魏程吕丁沈任姚卢傅钟姜崔谭陆汪范金石廖贾夏韦傅方孟邱贺白彭')
        
        # 时间模式
        self.time_patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', r'\1年\2月\3日'),
            (r'(\d{4})-(\d{2})-(\d{2})', r'\1-\2-\3'),
            (r'(\d{1,2}):(\d{2})', r'\1:\2'),
            (r'(\d+)分钟', r'\1分钟'),
            (r'(\d+)小时', r'\1小时'),
            (r'(\d+)天', r'\1天'),
        ]
        
        # 数字模式
        self.number_pattern = re.compile(r'[-+]?\d*\.\d+|\d+')
        
        # 邮箱模式
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        # URL模式
        self.url_pattern = re.compile(r'https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+')
        
        # 电话模式
        self.phone_pattern = re.compile(r'(?:\+86)?1[3-9]\d{9}')
    
    def extract_names(self, text: str) -> List[str]:
        """提取人名"""
        # 简单的基于关键词的提取
        names = []
        common_surnames = '张李王刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许邓冯韩曹曾彭萧蔡潘田董袁于余叶蒋杜苏魏程吕丁沈任姚卢傅钟姜崔谭陆汪范金石廖贾夏韦傅方孟邱贺白'
        
        for i, char in enumerate(text):
            if char in common_surnames and i + 1 < len(text):
                name = text[i:i+2]
                if len(name) == 2:
                    names.append(name)
        
        return list(set(names))
    
    def extract_time_expressions(self, text: str) -> List[str]:
        """提取时间表达式"""
        times = []
        for pattern, _ in self.time_patterns:
            matches = re.findall(pattern, text)
            times.extend(matches)
        return list(set(times))
    
    def extract_numbers(self, text: str) -> List[str]:
        """提取数字"""
        return self.number_pattern.findall(text)
    
    def extract_emails(self, text: str) -> List[str]:
        """提取邮箱"""
        return self.email_pattern.findall(text)
    
    def extract_urls(self, text: str) -> List[str]:
        """提取URL"""
        return self.url_pattern.findall(text)
    
    def extract_phones(self, text: str) -> List[str]:
        """提取电话号码"""
        return self.phone_pattern.findall(text)
    
    def full_extraction(self, text: str) -> Dict[str, List[str]]:
        """完整实体提取"""
        return {
            'names': self.extract_names(text),
            'times': self.extract_time_expressions(text),
            'numbers': self.extract_numbers(text),
            'emails': self.extract_emails(text),
            'urls': self.extract_urls(text),
            'phones': self.extract_phones(text),
        }


class TextSummarizer:
    """文本摘要生成器"""
    
    def __init__(self, max_length: int = 200):
        self.max_length = max_length
    
    def extractive_summarize(self, text: str) -> str:
        """抽取式摘要 - 基于句子重要性"""
        # 分割句子
        sentences = re.split(r'[。！？\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return text[:self.max_length]
        
        # 计算句子得分
        word_freq = Counter()
        for sentence in sentences:
            words = self._tokenize(sentence)
            word_freq.update(words)
        
        # TF-IDF风格评分
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = self._tokenize(sentence)
            score = sum(word_freq.get(word, 0) for word in words)
            # 位置权重（开头和结尾的句子更重要）
            position_weight = 1.0
            if i == 0:
                position_weight = 1.5
            elif i == len(sentences) - 1:
                position_weight = 1.3
            
            sentence_scores[i] = score * position_weight
        
        # 选择高分句子
        ranked = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        selected_indices = sorted([idx for idx, _ in ranked[:3]])
        
        summary_sentences = [sentences[i] for i in selected_indices]
        summary = '。'.join(summary_sentences)
        
        return summary[:self.max_length] + '...' if len(summary) > self.max_length else summary
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 去除标点，分割词语
        text = re.sub(r'[，。！？、；：""'']', '', text)
        return list(text)
    
    def generate_headline(self, text: str, max_words: int = 10) -> str:
        """生成标题"""
        words = self._tokenize(text)
        word_freq = Counter(words)
        
        # 过滤停用词
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '为', '有', '这', '那', '上', '下', '中', '个', '不', '我', '你', '他', '她', '它'}
        filtered = {w: f for w, f in word_freq.items() if w not in stopwords and len(w) > 1}
        
        top_words = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        headline = ''.join([w for w, _ in top_words[:max_words]])
        
        return headline


class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self, top_k: int = 10):
        self.top_k = top_k
        # 停用词表
        self.stopwords = {
            '的', '了', '是', '在', '和', '与', '或', '为', '有', '这', '那', '上', '下', '中',
            '个', '不', '我', '你', '他', '她', '它', '们', '着', '过', '会', '能', '要', '也',
            '都', '被', '把', '让', '从', '向', '对', '但', '却', '而', '而且', '所以', '因为',
            '如果', '虽然', '只是', '就是', '只有', '这个', '那个', '什么', '怎么', '如何',
            '可以', '应该', '需要', '可能', '已经', '正在', '自己', '现在', '今天', '然后',
            '一些', '一种', '这个', '那个', '每个', '其他', '另外', '以及', '其中', '关于'
        }
    
    def extract_tfidf(self, text: str) -> List[Tuple[str, float]]:
        """TF-IDF关键词提取"""
        # 分词
        words = self._segment(text)
        
        # 过滤停用词
        words = [w for w in words if w not in self.stopwords and len(w) > 1]
        
        # 计算TF
        word_count = Counter(words)
        total = sum(word_count.values())
        tf = {w: count / total for w, count in word_count.items()}
        
        # 简单IDF（基于词频）
        idf = {}
        for word in word_count:
            idf[word] = 1.0  # 简化处理
        
        # 计算TF-IDF
        tfidf = {w: tf[w] * idf.get(w, 1.0) for w in word_count}
        
        # 排序
        sorted_keywords = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:self.top_k]
    
    def extract_textrank(self, text: str) -> List[str]:
        """TextRank关键词提取"""
        words = self._segment(text)
        words = [w for w in words if w not in self.stopwords and len(w) > 1]
        
        if len(words) < 2:
            return words
        
        # 构建词语共现矩阵
        window_size = 3
        word_graph = {}
        
        for i, word in enumerate(words):
            if word not in word_graph:
                word_graph[word] = set()
            
            for j in range(max(0, i - window_size), min(len(words), i + window_size + 1)):
                if i != j:
                    word_graph[word].add(words[j])
        
        # 简化的PageRank
        scores = {w: 1.0 for w in words}
        damping = 0.85
        iterations = 50
        
        for _ in range(iterations):
            new_scores = {}
            for word in words:
                score = (1 - damping) + damping * sum(
                    scores.get(neighbor, 0) / len(word_graph.get(neighbor, {word}))
                    for neighbor in word_graph.get(word, set())
                )
                new_scores[word] = score
            scores = new_scores
        
        sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:self.top_k]]
    
    def _segment(self, text: str) -> List[str]:
        """简单分词"""
        text = re.sub(r'[\s\d\p{P}]+', '', text)
        return list(text)


class TextComparator:
    """文本对比器"""
    
    def similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Jaccard相似度"""
        set1 = set(text1)
        set2 = set(text2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0
    
    def diff_lines(self, text1: str, text2: str) -> List[Dict]:
        """对比文本差异，返回差异行"""
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        matcher = SequenceMatcher(None, lines1, lines2)
        diff = []
        
        for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
            if opcode == 'equal':
                continue
            elif opcode == 'delete':
                for i in range(a0, a1):
                    diff.append({'type': 'removed', 'line': i + 1, 'content': lines1[i]})
            elif opcode == 'insert':
                for i in range(b0, b1):
                    diff.append({'type': 'added', 'line': i + 1, 'content': lines2[i]})
            elif opcode == 'replace':
                for i in range(a0, a1):
                    diff.append({'type': 'removed', 'line': i + 1, 'content': lines1[i]})
                for i in range(b0, b1):
                    diff.append({'type': 'added', 'line': i + 1, 'content': lines2[i]})
        
        return diff
    
    def hash_content(self, text: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()


class SmartTextProcessor:
    """智能文本处理器 - 统一接口"""
    
    def __init__(self):
        self.cleaner = TextCleaner()
        self.formatter = TextFormatter()
        self.extractor = EntityExtractor()
        self.summarizer = TextSummarizer()
        self.keyword_extractor = KeywordExtractor()
        self.comparator = TextComparator()
    
    def process(self, text: str, operations: List[str]) -> Dict[str, Any]:
        """
        统一处理接口
        
        Args:
            text: 输入文本
            operations: 操作列表
                - clean: 清洗文本
                - extract: 提取实体
                - summarize: 生成摘要
                - keywords: 提取关键词
                - headline: 生成标题
        
        Returns:
            处理结果字典
        """
        result = {'original_length': len(text)}
        
        for op in operations:
            if op == 'clean':
                result['cleaned'] = self.cleaner.full_clean(text)
                text = result['cleaned']
            elif op == 'extract':
                result['entities'] = self.extractor.full_extraction(text)
            elif op == 'summarize':
                result['summary'] = self.summarizer.extractive_summarize(text)
            elif op == 'keywords':
                result['keywords'] = self.keyword_extractor.extract_tfidf(text)
            elif op == 'headline':
                result['headline'] = self.summarizer.generate_headline(text)
        
        return result
    
    def compare_documents(self, doc1: str, doc2: str) -> Dict[str, Any]:
        """对比两个文档"""
        return {
            'similarity': self.comparator.similarity(doc1, doc2),
            'jaccard_similarity': self.comparator.jaccard_similarity(doc1, doc2),
            'diff': self.comparator.diff_lines(doc1, doc2),
            'hash1': self.comparator.hash_content(doc1),
            'hash2': self.comparator.hash_content(doc2),
        }
    
    def convert_format(self, content: str, from_format: str, to_format: str) -> str:
        """格式转换"""
        if from_format == 'markdown' and to_format == 'html':
            return self.formatter.markdown_to_html(content)
        elif from_format == 'json' and to_format == 'yaml':
            return self.formatter.json_to_yaml(json.loads(content))
        elif from_format == 'yaml' and to_format == 'json':
            return self.formatter.yaml_to_json(content)
        elif from_format == 'csv' and to_format == 'json':
            return self.formatter.csv_to_json(content)
        elif from_format == 'json' and to_format == 'csv':
            return self.formatter.json_to_csv(content)
        else:
            return content


# CLI接口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='智能文本处理工具')
    parser.add_argument('input', nargs='?', help='输入文件或文本')
    parser.add_argument('-o', '--output', help='输出文件')
    parser.add_argument('--clean', action='store_true', help='清洗文本')
    parser.add_argument('--extract', action='store_true', help='提取实体')
    parser.add_argument('--summarize', action='store_true', help='生成摘要')
    parser.add_argument('--keywords', action='store_true', help='提取关键词')
    parser.add_argument('--convert', choices=['md2html', 'json2yaml', 'yaml2json', 'csv2json', 'json2csv'],
                       help='格式转换')
    parser.add_argument('--compare', help='对比文件路径')
    
    args = parser.parse_args()
    
    # 读取输入
    if args.input and os.path.exists(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.input or ''
    
    processor = SmartTextProcessor()
    operations = []
    result = text
    
    if args.clean:
        operations.append('clean')
    if args.extract:
        operations.append('extract')
    if args.summarize:
        operations.append('summarize')
    if args.keywords:
        operations.append('keywords')
    
    if operations:
        output = processor.process(text, operations)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.compare:
        with open(args.compare, 'r', encoding='utf-8') as f:
            text2 = f.read()
        result = processor.compare_documents(text, text2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.convert:
        from_format, to_format = args.convert.split('2')
        result = processor.convert_format(text, from_format, to_format)
        print(result)
    else:
        print("请指定操作: --clean, --extract, --summarize, --keywords, --compare, --convert")

    # 写入输出
    if args.output and isinstance(result, str):
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
