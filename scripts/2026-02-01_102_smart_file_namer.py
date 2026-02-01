#!/usr/bin/env python3
"""
智能文件命名生成器 (Day 102)
===========================
根据文件内容自动生成有意义的文件名

功能：
- 分析文件内容提取关键词
- 生成规范化的文件名
- 支持多种文件类型识别
- 自动添加日期戳和序号
"""

import re
import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import argparse


class SmartFileNamer:
    """智能文件命名生成器"""
    
    # 关键词权重表（越高频的词权重越低，避免成为文件名）
    STOP_WORDS = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither',
        'not', 'only', 'own', 'same', 'than', 'too', 'very', 'just', 'also',
        'this', 'that', 'these', 'those', 'it', 'its', 'what', 'which',
        'who', 'whom', 'whose', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'any', 'some', 'no', 'our', 'your', 'his', 'her', 'their',
        'my', 'i', 'you', 'we', 'they', 'he', 'she', 'them', 'us', 'me',
        'class', 'def', 'function', 'var', 'let', 'const', 'if', 'else',
        'for', 'while', 'return', 'import', 'from', 'export', 'module',
        'require', 'include', 'file', 'code', 'data', 'test', 'example',
    }
    
    # 文件类型模式
    FILE_PATTERNS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'header',
        '.go': 'golang',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.md': 'markdown',
        '.txt': 'text',
        '.csv': 'csv',
        '.sh': 'shell',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.ps1': 'powershell',
        '.dockerfile': 'docker',
        '.gitignore': 'gitignore',
        '.env': 'env',
    }
    
    def __init__(self):
        self.keyword_weights: Dict[str, float] = {}
    
    def extract_keywords(self, content: str, max_keywords: int = 5) -> List[str]:
        """从内容中提取关键词"""
        # 转小写并清理
        text = content.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # 分词
        words = text.split()
        
        # 统计词频
        word_freq: Dict[str, int] = {}
        for word in words:
            if len(word) >= 3 and word not in self.STOP_WORDS:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: (-x[1], x[0]))
        
        # 返回高频词
        return [word for word, _ in sorted_words[:max_keywords]]
    
    def detect_file_type(self, filepath: str) -> str:
        """检测文件类型"""
        ext = os.path.splitext(filepath)[1].lower()
        return self.FILE_PATTERNS.get(ext, 'unknown')
    
    def generate_name(self, 
                      content: str, 
                      filepath: Optional[str] = None,
                      max_length: int = 50,
                      include_date: bool = False,
                      include_hash: bool = False,
                      separator: str = '_') -> str:
        """
        生成文件名
        
        Args:
            content: 文件内容
            filepath: 原始文件路径（可选）
            max_length: 最大文件名长度
            include_date: 是否包含日期
            include_hash: 是否包含短哈希
            separator: 分隔符
        
        Returns:
            生成的文件名（不含扩展名）
        """
        # 提取关键词
        keywords = self.extract_keywords(content, max_keywords=4)
        
        if not keywords:
            # 如果没有提取到关键词，使用默认名
            name_parts = ['untitled']
        else:
            # 首字母大写，组合成驼峰式
            name_parts = [kw.capitalize() for kw in keywords[:3]]
        
        name = ''.join(name_parts)
        
        # 限制长度
        if len(name) > max_length:
            name = name[:max_length].rstrip('_')
        
        # 添加日期
        if include_date:
            date_str = datetime.now().strftime('%Y%m%d')
            name = f"{date_str}{separator}{name}"
        
        # 添加短哈希（保证唯一性）
        if include_hash:
            short_hash = hashlib.md5(content.encode()).hexdigest()[:6]
            name = f"{name}{separator}{short_hash}"
        
        return name
    
    def suggest_names(self, content: str, filepath: Optional[str] = None) -> List[Dict[str, str]]:
        """生成多个命名建议"""
        suggestions = []
        
        # 基础名称
        base_name = self.generate_name(content, filepath, include_date=False)
        suggestions.append({
            'name': base_name,
            'style': '基础',
            'example': f"{base_name}.py"
        })
        
        # 带日期的名称
        date_name = self.generate_name(content, filepath, include_date=True)
        suggestions.append({
            'name': date_name,
            'style': '日期前缀',
            'example': f"{date_name}.py"
        })
        
        # 带哈希的名称（唯一）
        hash_name = self.generate_name(content, filepath, include_hash=True)
        suggestions.append({
            'name': hash_name,
            'style': '带哈希（唯一）',
            'example': f"{hash_name}.py"
        })
        
        # 简洁版（只用1个关键词）
        keywords = self.extract_keywords(content, max_keywords=1)
        if keywords:
            simple = keywords[0].capitalize()
            suggestions.append({
                'name': simple,
                'style': '简洁',
                'example': f"{simple}.py"
            })
        
        return suggestions
    
    def format_filename(self, name: str, extension: str = '.py', separator: str = '_') -> str:
        """格式化文件名"""
        # 清理特殊字符
        name = re.sub(r'[^\w' + separator + '-]', '', name)
        name = re.sub(separator + '+', separator, name)
        name = name.strip(separator)
        
        return f"{name}{extension}"


def main():
    """主函数 - 命令行工具"""
    parser = argparse.ArgumentParser(
        description='智能文件命名生成器 - 根据内容自动生成有意义的文件名'
    )
    parser.add_argument('file', nargs='?', help='要分析的文件路径')
    parser.add_argument('-c', '--content', help='直接提供文件内容')
    parser.add_argument('-e', '--extension', default='.py', help='文件扩展名')
    parser.add_argument('-s', '--separator', default='_', help='分隔符')
    parser.add_argument('-d', '--include-date', action='store_true', help='包含日期')
    parser.add_argument('-H', '--include-hash', action='store_true', help='包含哈希')
    parser.add_argument('-l', '--max-length', type=int, default=50, help='最大长度')
    parser.add_argument('--all', action='store_true', help='显示所有建议')
    
    args = parser.parse_args()
    
    namer = SmartFileNamer()
    
    # 获取内容
    if args.content:
        content = args.content
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ 文件不存在: {args.file}")
            return
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return
    else:
        # 交互式输入
        print("📝 请输入文件内容（按 Ctrl+D 完成）:")
        content = ''
        try:
            content = input() + '\n'
            while True:
                try:
                    line = input()
                    content += line + '\n'
                except EOFError:
                    break
        except KeyboardInterrupt:
            return
    
    if not content.strip():
        print("❌ 内容为空")
        return
    
    print(f"\n📄 分析结果:")
    print(f"   内容长度: {len(content)} 字符")
    print(f"   关键词: {', '.join(namer.extract_keywords(content))}")
    
    if args.all:
        print(f"\n💡 命名建议:")
        suggestions = namer.suggest_names(content, args.file)
        for i, sug in enumerate(suggestions, 1):
            print(f"   {i}. [{sug['style']}] {sug['example']}")
    else:
        name = namer.generate_name(
            content, 
            args.file,
            max_length=args.max_length,
            include_date=args.include_date,
            include_hash=args.include_hash,
            separator=args.separator
        )
        filename = namer.format_filename(name, args.extension, args.separator)
        print(f"\n✨ 推荐文件名: {filename}")
    
    print(f"\n🎯 提示: 使用 --all 查看所有建议，-d 添加日期，-H 添加哈希")


if __name__ == '__main__':
    main()
