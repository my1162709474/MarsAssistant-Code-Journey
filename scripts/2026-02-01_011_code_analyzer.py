#!/usr/bin/env python3
"""
代码统计分析器 - Day 96
分析代码库的统计信息：行数、字符数、函数数、类数等
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class CodeAnalyzer:
    """代码统计分析器"""
    
    # 语言模式定义
    LANGUAGE_PATTERNS = {
        'python': {
            'extensions': ['.py', '.pyw'],
            'comment_single': '#',
            'comment_multi': ('"""', '"""'),
            'functions': r'def\s+(\w+)\s*\(',
            'classes': r'class\s+(\w+)\s*[:(]',
            'imports': r'^(?:import|from\s+\w+\s+import)',
        },
        'javascript': {
            'extensions': ['.js', '.jsx', '.ts', '.tsx'],
            'comment_single': '//',
            'comment_multi': ('/*', '*/'),
            'functions': r'(?:function\s+(\w+)|const\s+(\w+)\s*=|(\w+)\s*=\s*\()',
            'classes': r'class\s+(\w+)',
            'imports': r'^(?:import|export)',
        },
        'java': {
            'extensions': ['.java'],
            'comment_single': '//',
            'comment_multi': ('/*', '*/'),
            'functions': r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?\w+\s+(\w+)\s*\(',
            'classes': r'class\s+(\w+)',
            'imports': r'^import\s+',
        },
        'cpp': {
            'extensions': ['.cpp', '.cxx', '.cc', '.h', '.hpp'],
            'comment_single': '//',
            'comment_multi': ('/*', '*/'),
            'functions': r'(?:void|int|bool|std::\w+|auto)\s+(\w+)\s*\(',
            'classes': r'class\s+(\w+)',
            'imports': r'^(?:#include|using\s+namespace)',
        },
        'markdown': {
            'extensions': ['.md', '.markdown'],
            'comment_single': None,
            'comment_multi': None,
            'functions': None,
            'classes': None,
            'imports': None,
        },
    }
    
    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path)
        self.stats: Dict[str, int] = {}
        self.file_details: List[Dict] = []
    
    def count_lines(self, content: str) -> Tuple[int, int, int]:
        """计算总行数、空行数、代码行数"""
        lines = content.split('\n')
        total = len(lines)
        blank = sum(1 for line in lines if line.strip() == '')
        code = total - blank
        return total, blank, code
    
    def count_characters(self, content: str) -> int:
        """计算字符数（不含换行）"""
        return len(content.replace('\n', '').replace('\r', ''))
    
    def count_elements(self, content: str, language: str) -> Dict[str, int]:
        """统计函数、类、导入等元素"""
        pattern = self.LANGUAGE_PATTERNS.get(language, {})
        counts = {
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'comments': 0,
        }
        
        # 统计函数
        if pattern.get('functions'):
            matches = re.findall(pattern['functions'], content)
            counts['functions'] = len([m for m in matches if m])
        
        # 统计类
        if pattern.get('classes'):
            matches = re.findall(pattern['classes'], content)
            counts['classes'] = len(matches)
        
        # 统计导入
        if pattern.get('imports'):
            matches = re.findall(pattern['imports'], content, re.MULTILINE)
            counts['imports'] = len(matches)
        
        # 统计注释行
        if pattern.get('comment_single'):
            counts['comments'] += sum(1 for line in content.split('\n') 
                                     if line.strip().startswith(pattern['comment_single']))
        
        return counts
    
    def detect_language(self, file_path: Path) -> str:
        """检测文件语言"""
        ext = file_path.suffix.lower()
        for lang, config in self.LANGUAGE_PATTERNS.items():
            if ext in config['extensions']:
                return lang
        return 'unknown'
    
    def analyze_file(self, file_path: Path) -> Dict:
        """分析单个文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            language = self.detect_language(file_path)
            
            total_lines, blank_lines, code_lines = self.count_lines(content)
            char_count = self.count_characters(content)
            elements = self.count_elements(content, language)
            
            return {
                'path': str(file_path),
                'language': language,
                'total_lines': total_lines,
                'blank_lines': blank_lines,
                'code_lines': code_lines,
                'characters': char_count,
                'functions': elements['functions'],
                'classes': elements['classes'],
                'imports': elements['imports'],
                'comment_lines': elements['comments'],
            }
        except Exception as e:
            return {
                'path': str(file_path),
                'error': str(e),
            }
    
    def analyze_directory(self, ignore_dirs: List[str] = None) -> Dict:
        """分析整个目录"""
        if ignore_dirs is None:
            ignore_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_code_lines': 0,
            'total_blank_lines': 0,
            'total_characters': 0,
            'total_functions': 0,
            'total_classes': 0,
            'by_language': {},
            'files': [],
        }
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                # 跳过忽略的目录
                if any(ignore in str(file_path) for ignore in ignore_dirs):
                    continue
                
                detail = self.analyze_file(file_path)
                stats['files'].append(detail)
                stats['total_files'] += 1
                
                if 'error' not in detail:
                    stats['total_lines'] += detail['total_lines']
                    stats['total_code_lines'] += detail['code_lines']
                    stats['total_blank_lines'] += detail['blank_lines']
                    stats['total_characters'] += detail['characters']
                    stats['total_functions'] += detail['functions']
                    stats['total_classes'] += detail['classes']
                    
                    # 按语言统计
                    lang = detail['language']
                    if lang not in stats['by_language']:
                        stats['by_language'][lang] = {
                            'files': 0,
                            'lines': 0,
                            'code_lines': 0,
                            'functions': 0,
                            'classes': 0,
                        }
                    stats['by_language'][lang]['files'] += 1
                    stats['by_language'][lang]['lines'] += detail['total_lines']
                    stats['by_language'][lang]['code_lines'] += detail['code_lines']
                    stats['by_language'][lang]['functions'] += detail['functions']
                    stats['by_language'][lang]['classes'] += detail['classes']
        
        return stats
    
    def print_report(self, stats: Dict = None):
        """打印分析报告"""
        if stats is None:
            stats = self.analyze_directory()
        
        print("=" * 60)
        print("代码统计分析报告")
        print("=" * 60)
        print(f"分析路径: {self.root_path}")
        print("-" * 60)
        
        print(f"\n📊 总体统计:")
        print(f"  - 总文件数: {stats['total_files']}")
        print(f"  - 总行数: {stats['total_lines']:,}")
        print(f"  - 代码行数: {stats['total_code_lines']:,}")
        print(f"  - 空行数: {stats['total_blank_lines']:,}")
        print(f"  - 总字符数: {stats['total_characters']:,}")
        print(f"  - 总函数数: {stats['total_functions']}")
        print(f"  - 总类数: {stats['total_classes']}")
        
        print(f"\n📈 代码密度:")
        if stats['total_lines'] > 0:
            code_ratio = stats['total_code_lines'] / stats['total_lines'] * 100
            print(f"  - 代码占比: {code_ratio:.1f}%")
            avg_lines_per_file = stats['total_lines'] / stats['total_files']
            print(f"  - 平均每文件行数: {avg_lines_per_file:.1f}")
        
        print(f"\n🌍 按语言分布:")
        for lang, lang_stats in sorted(stats['by_language'].items(), 
                                        key=lambda x: x[1]['lines'], reverse=True):
            print(f"  - {lang}: {lang_stats['lines']:,}行 ({lang_stats['files']}文件, "
                  f"{lang_stats['functions']}函数, {lang_stats['classes']}类)")
        
        print("\n" + "=" * 60)


def main():
    """主函数"""
    import sys
    
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    analyzer = CodeAnalyzer(path)
    stats = analyzer.analyze_directory()
    analyzer.print_report(stats)


if __name__ == '__main__':
    main()
