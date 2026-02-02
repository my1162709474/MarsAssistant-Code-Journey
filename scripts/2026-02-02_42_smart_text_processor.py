#!/usr/bin/env python3
"""
智能文本处理工具
智能文本清洗、敏感信息检测、摘要生成、关键词提取
"""

import re
import json
import base64
from datetime import datetime
from collections import Counter
import hashlib


class TextProcessor:
    """智能文本处理器"""
    
    # 敏感信息正则模式
    SENSITIVE_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'1[3-9]\d{9}',  # 中国手机号
        'phone_us': r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # 美国电话
        'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
        'ssn': r'\d{3}[-\s]?\d{2}[-\s]?\d{4}',
        'ipv4': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'password': r'(password|pwd|secret|key|token)[\s:=]*[\w\-\.]+',
    }
    
    # 停用词列表
    STOPWORDS = {
        '的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
        '或', '一个', '没有', '我们', '你们', '他们', '这', '那',
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was',
        'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
        'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'must', 'shall', 'can', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'between',
        'under', 'again', 'further', 'then', 'once', 'here', 'there',
    }
    
    def __init__(self):
        self.stats = {'cleaned': 0, 'detected': 0, 'summarized': 0}
    
    def clean_text(self, text, remove_special=True, normalize_whitespace=True):
        """
        清洗文本
        
        Args:
            text: 输入文本
            remove_special: 是否移除特殊字符
            normalize_whitespace: 是否规范化空白字符
        
        Returns:
            清洗后的文本
        """
        cleaned = text
        
        if normalize_whitespace:
            cleaned = re.sub(r'\s+', ' ', cleaned)
            cleaned = cleaned.strip()
        
        if remove_special:
            cleaned = re.sub(r'[^\w\s\u4e00-\u9fff\.\,\!\?\:\;\-\_\'\"]', '', cleaned)
        
        self.stats['cleaned'] += 1
        return cleaned
    
    def detect_sensitive_info(self, text, return_positions=True):
        """
        检测敏感信息
        
        Args:
            text: 输入文本
            return_positions: 是否返回位置信息
        
        Returns:
            检测结果字典
        """
        results = {'types_found': [], 'items': [], 'redacted': text}
        
        for info_type, pattern in self.SENSITIVE_PATTERNS.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                results['types_found'].append(info_type)
                for match in matches:
                    item = {
                        'type': info_type,
                        'value': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    }
                    results['items'].append(item)
        
        # 脱敏处理
        redacted = text
        for item in results['items']:
            replacement = f'[{item["type"].upper()}_REDACTED]'
            redacted = redacted[:item['start']] + replacement + redacted[item['end']:]
        results['redacted'] = redacted
        
        self.stats['detected'] += 1
        return results
    
    def extract_keywords(self, text, top_n=10, include_frequency=True):
        """
        提取关键词
        
        Args:
            text: 输入文本
            top_n: 返回前N个关键词
            include_frequency: 是否包含频率信息
        
        Returns:
            关键词列表
        """
        # 分词（简单按空格和中文分词）
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词和短词
        filtered = [
            w for w in words 
            if w not in self.STOPWORDS 
            and len(w) > 1
            and w.isalpha()
        ]
        
        # 词频统计
        word_freq = Counter(filtered)
        
        # 获取top_n
        keywords = word_freq.most_common(top_n)
        
        if include_frequency:
            return [{'word': w, 'frequency': f} for w, f in keywords]
        return [w for w, _ in keywords]
    
    def summarize_text(self, text, max_length=100):
        """
        生成文本摘要（抽取式）
        
        Args:
            text: 输入文本
            max_length: 摘要最大长度
        
        Returns:
            摘要文本
        """
        # 按句子分割
        sentences = re.split(r'[。！？\.\!\?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text[:max_length]
        
        if len(sentences) == 1:
            return sentences[0][:max_length]
        
        # 计算每个句子的得分（基于词频和位置）
        words = re.findall(r'\\w+\bb', text.lower())
        word_freq = Counter(words)
        
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            
            # 词频得分
            for word in sentence_words:
                score += word_freq.get(word, 0)
            
            # 位置得分（开头和结尾的句子更重要）
            if i == 0:
                score *= 1.5
            elif i == len(sentences) - 1:
                score *= 1.3
            
            # 长度惩罚（太短或太长的句子得分降低）
            word_count = len(sentence_words)
            if word_count < 3:
                score *= 0.5
            elif word_count > 50:
                score *= 0.8
            
            sentence_scores.append((sentence, score))
        
        # 按得分排序，选取句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 选择句子并保持原始顺序
        selected = []
        for sentence, _ in sentence_scores[:3]:  # 最多选3个
            if len(' '.join(selected)) + len(sentence) < max_length * 1.5:
                selected.append(sentence)
        
        # 按原始顺序排列
        result = ' '.join([
            s for s in sentences 
            if s in selected
        ])
        
        self.stats['summarized'] += 1
        return result[:max_length]
    
    def analyze_text(self, text):
        """
        完整文本分析
        
        Args:
            text: 输入文本
        
        Returns:
            分析结果字典
        """
        # 清洗
        cleaned = self.clean_text(text)
        
        # 敏感信息检测
        sensitive = self.detect_sensitive_info(text)
        
        # 关键词提取
        keywords = self.extract_keywords(cleaned)
        
        # 摘要生成
        summary = self.summarize_text(cleaned)
        
        # 基本统计
        stats = {
            'char_count': len(text),
            'word_count': len(re.findall(r'\b\w+\b', text)),
            'sentence_count': len(re.split(r'[。！？\.\!\?]+', text)),
        }
        
        return {
            'original_length': len(text),
            'cleaned_text': cleaned,
            'sensitive_info': sensitive,
            'keywords': keywords,
            'summary': summary,
            'statistics': stats,
            'processing_stats': self.stats.copy()
        }
    
    def batch_process(self, texts):
        """
        批量处理文本
        
        Args:
            texts: 文本列表
        
        Returns:
            处理结果列表
        """
        results = []
        for text in texts:
            results.append(self.analyze_text(text))
        return results
    
    def generate_report(self, analysis_result):
        """
        生成分析报告
        
        Args:
            analysis_result: 单个文本的分析结果
        
        Returns:
            格式化的报告
        """
        report = []
        report.append("=" * 50)
        report.append("📊 文本分析报告")
        report.append("=" * 50)
        
        stats = analysis_result['statistics']
        report.append(f"\n📏 基本统计:")
        report.append(f"   - 字符数: {stats['char_count']}")
        report.append(f"   - 词数: {stats['word_count']}")
        report.append(f"   - 句子数: {stats['sentence_count']}")
        
        report.append(f"\n🔑 关键词 (Top 10):")
        for kw in analysis_result['keywords'][:10]:
            if isinstance(kw, dict):
                report.append(f"   - {kw['word']}: {kw['frequency']}次")
            else:
                report.append(f"   - {kw}")
        
        report.append(f"\n📝 摘要:")
        report.append(f"   {analysis_result['summary']}")
        
        sensitive = analysis_result['sensitive_info']
        if sensitive['types_found']:
            report.append(f"\n⚠️ 检测到敏感信息:")
            report.append(f"   类型: {', '.join(sensitive['types_found'])}")
            report.append(f"   项目数: {len(sensitive['items'])}")
        else:
            report.append(f"\n✅ 未检测到敏感信息")
        
        report.append(f"\n🧹 清洗后文本:")
        report.append(f"   {analysis_result['cleaned_text'][:200]}...")
        
        report.append("\n" + "=" * 50)
        return '\n'.join(report)


class TextProcessorCLI:
    """命令行接口"""
    
    def __init__(self):
        self.processor = TextProcessor()
    
    def run_interactive(self):
        """交互式运行"""
        print("🔧 智能文本处理器")
        print("=" * 40)
        print("输入 'quit' 退出")
        print("输入 'report' 查看完整报告示例")
        print("-" * 40)
        
        while True:
            try:
                text = input("\n📝 请输入文本: ").strip()
                
                if text.lower() == 'quit':
                    print("👋 再见！")
                    break
                
                if text.lower() == 'report':
                    text = """人工智能（AI）是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。
                    机器学习是AI的核心技术之一，它使计算机能够从数据中学习，而不需要明确的编程。
                    深度学习是机器学习的一个子领域，使用多层神经网络来处理复杂的数据模式。
                    自然语言处理（NLP）让计算机能够理解和生成人类语言，是AI应用的重要方向。
                    计算机视觉使机器能够'看'和理解图像和视频内容，在医疗、自动驾驶等领域有广泛应用。
                    AI的发展带来了许多机遇，如提高效率、解决复杂问题，但也面临伦理和隐私挑战。
                    未来，AI将继续演进，与人类协作，共同创造更美好的世界。"""
                
                if not text:
                    continue
                
                result = self.processor.analyze_text(text)
                report = self.processor.generate_report(result)
                print(report)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    def process_file(self, file_path):
        """处理文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            result = self.processor.analyze_text(text)
            report = self.processor.generate_report(result)
            print(report)
            
            return result
        except Exception as e:
            print(f"❌ 文件处理错误: {e}")
            return None
    
    def batch_files(self, file_paths):
        """批量处理文件"""
        all_results = []
        for path in file_paths:
            print(f"\n📄 处理文件: {path}")
            result = self.process_file(path)
            if result:
                all_results.append({'file': path, 'result': result})
        return all_results


def demo():
    """演示函数"""
    print("🎯 智能文本处理器演示")
    print("=" * 50)
    
    processor = TextProcessor()
    
    # 示例文本
    sample_texts = [
        """欢迎使用智能文本处理器！这个工具可以帮助你清洗文本、检测敏感信息、提取关键词和生成摘要。
        敏感信息示例：联系邮箱是 example@email.com，电话是 13812345678。
        我们的产品可以帮助企业提高效率，降低成本，增强竞争力。""",
        
        """人工智能正在改变我们的世界。从智能手机到自动驾驶汽车，从医疗诊断到金融分析，
        AI技术的应用越来越广泛。机器学习、深度学习、自然语言处理等技术不断突破，
        为人类带来更多可能性。未来，AI将继续发展，与人类共同创造更美好的明天。""",
    ]
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n{'='*50}")
        print(f"📝 示例 {i}")
        print(f"{'='*50}")
        
        result = processor.analyze_text(text)
        report = processor.generate_report(result)
        print(report)
        print()
    
    # 批量处理演示
    print("=" * 50)
    print("📦 批量处理演示")
    print("=" * 50)
    results = processor.batch_process(sample_texts)
    print(f"✅ 成功处理 {len(results)} 个文本")
    print(f"📊 处理统计: {processor.stats}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 命令行参数模式
        cli = TextProcessorCLI()
        
        if sys.argv[1] == '--demo':
            demo()
        elif sys.argv[1] == '--file':
            if len(sys.argv) > 2:
                cli.process_file(sys.argv[2])
            else:
                print("❌ 请指定文件路径: python text_processor.py --file <path>")
        elif sys.argv[1] == '--batch':
            if len(sys.argv) > 2:
                cli.batch_files(sys.argv[2:])
            else:
                print("❌ 请指定文件路径: python text_processor.py --batch <path1> <path2> ...")
        else:
            print("用法:")
            print("  python text_processor.py --demo          # 运行演示")
            print("  python text_processor.py --file <path>   # 处理单个文件")
            print("  python text_processor.py --batch <paths> # 批量处理文件")
            print("  (无参数)                                # 交互式模式")
    else:
        # 交互式模式
        cli = TextProcessorCLI()
        cli.run_interactive()
