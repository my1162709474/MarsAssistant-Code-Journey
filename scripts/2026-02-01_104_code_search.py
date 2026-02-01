#!/usr/bin/env python3
"""
🧠 Smart Code Search Tool
智能代码搜索工具 - 在代码库中快速定位函数、类和模式

Usage:
    python code_search.py --path /path/to/code --search "def test"
    python code_search.py --path /path/to/code --function "MyClass"
    python code_search.py --path /path/to/code --pattern "TODO|FIXME"
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SearchType(Enum):
    TEXT = "text"
    FUNCTION = "function"
    CLASS = "class"
    PATTERN = "pattern"
    REGEX = "regex"


@dataclass
class SearchResult:
    file_path: str
    line_number: int
    line_content: str
    match_type: str
    context_lines: List[str] = None
    
    def __post_init__(self):
        if self.context_lines is None:
            self.context_lines = []


class CodeSearchEngine:
    """智能代码搜索引擎"""
    
    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
        '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.lua',
        '.sh', '.bash', '.zsh', '.yml', '.yaml', '.json',
        '.xml', '.html', '.css', '.scss', '.md', '.txt'
    }
    
    # 函数定义模式
    FUNCTION_PATTERNS = [
        r'^def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*[\w\[\\]]+\s*)?:',
        r'^function\s+(\w+)\s*\([^)]*\)',
        r'^(\w+)\s*=\s*function\s*\([^)]*\)',
        r'^(\w+)\s*:\s*function\s*\([^)]*\)',
        r'^(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:async\s+)?(?:def|func|function)\s+(\w+)',
        r'^(\w+)\s*\([^)]*\)\s*{',
        r'^let\s+(\w+)\s*=\s*\(',
        r'^const\s+(\w+)\s*=\s*\(',
    ]
    
    # 类定义模式
    CLASS_PATTERNS = [
        r'^class\s+(\w+)(?:\s*(?:<|:)\s*\w+)?',
        r'^struct\s+(\w+)',
        r'^interface\s+(\w+)',
        r'^type\s+(\w+)\s*=\s*class',
        r'^(?:public\s+|private\s+)?(?:abstract\s+)?class\s+(\w+)',
    ]
    
    def __init__(self, root_path: str, max_file_size: int = 1024 * 1024):
        self.root_path = Path(root_path)
        self.max_file_size = max_file_size
        self.results: List[SearchResult] = []
        self.stats = {
            "files_scanned": 0,
            "lines_scanned": 0,
            "matches_found": 0
        }
    
    def is_binary_file(self, file_path: Path) -> bool:
        """检查是否为二进制文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1024)
                return False
        except:
            return True
    
    def get_file_language(self, file_path: Path) -> str:
        """识别文件语言"""
        extension = file_path.suffix.lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C Header',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.lua': 'Lua',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.zsh': 'Zsh',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.md': 'Markdown',
        }
        return language_map.get(extension, 'Unknown')
    
    def search_text(self, query: str, case_sensitive: bool = False) -> List[SearchResult]:
        """文本搜索"""
        results = []
        regex_flags = 0 if case_sensitive else re.IGNORECASE
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_EXTENSIONS:
                if self.is_binary_file(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        self.stats["files_scanned"] += 1
                        
                    for i, line in enumerate(lines, 1):
                        self.stats["lines_scanned"] += 1
                        if re.search(query, line, regex_flags):
                            self.stats["matches_found"] += 1
                            results.append(SearchResult(
                                file_path=str(file_path),
                                line_number=i,
                                line_content=line.strip(),
                                match_type="text",
                                context_lines=self._get_context(lines, i, 2)
                            ))
                except Exception as e:
                    continue
        
        return results
    
    def search_function(self, function_name: str) -> List[SearchResult]:
        """搜索函数定义"""
        results = []
        pattern = re.compile(r'^\s*' + '|'.join(self.FUNCTION_PATTERNS), re.MULTILINE)
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_EXTENSIONS:
                if self.is_binary_file(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self.stats["files_scanned"] += 1
                        self.stats["lines_scanned"] += len(content.split('\n'))
                        
                    for match in pattern.finditer(content):
                        found_name = match.group(1) if match.groups() else ""
                        if function_name.lower() in found_name.lower():
                            line_num = content[:match.start()].count('\n') + 1
                            line_content = content.split('\n')[line_num - 1] if line_num <= len(content.split('\n')) else ""
                            
                            self.stats["matches_found"] += 1
                            results.append(SearchResult(
                                file_path=str(file_path),
                                line_number=line_num,
                                line_content=line_content.strip(),
                                match_type="function",
                                context_lines=self._get_context(content.split('\n'), line_num, 2)
                            ))
                except Exception as e:
                    continue
        
        return results
    
    def search_class(self, class_name: str) -> List[SearchResult]:
        """搜索类定义"""
        results = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_EXTENSIONS:
                if self.is_binary_file(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        self.stats["files_scanned"] += 1
                        
                    for i, line in enumerate(lines, 1):
                        self.stats["lines_scanned"] += 1
                        for pattern in self.CLASS_PATTERNS:
                            match = re.search(pattern, line)
                            if match:
                                found_name = match.group(1) if match.groups() else ""
                                if class_name.lower() in found_name.lower():
                                    self.stats["matches_found"] += 1
                                    results.append(SearchResult(
                                        file_path=str(file_path),
                                        line_number=i,
                                        line_content=line.strip(),
                                        match_type="class",
                                        context_lines=self._get_context(lines, i, 2)
                                    ))
                                    break
                except Exception as e:
                    continue
        
        return results
    
    def search_pattern(self, pattern: str) -> List[SearchResult]:
        """使用正则表达式搜索"""
        try:
            regex = re.compile(pattern)
            return self._regex_search(regex)
        except re.error:
            # 如果不是有效的正则表达式，使用普通文本搜索
            return self.search_text(pattern)
    
    def _regex_search(self, regex: re.Pattern) -> List[SearchResult]:
        """正则表达式搜索实现"""
        results = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_EXTENSIONS:
                if self.is_binary_file(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        self.stats["files_scanned"] += 1
                        
                    for i, line in enumerate(lines, 1):
                        self.stats["lines_scanned"] += 1
                        if regex.search(line):
                            self.stats["matches_found"] += 1
                            results.append(SearchResult(
                                file_path=str(file_path),
                                line_number=i,
                                line_content=line.strip(),
                                match_type="regex",
                                context_lines=self._get_context(lines, i, 2)
                            ))
                except Exception as e:
                    continue
        
        return results
    
    def _get_context(self, lines: List[str], line_num: int, context: int = 2) -> List[str]:
        """获取上下文行"""
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        return [lines[i].rstrip() for i in range(start, end)]
    
    def search(self, query: str, search_type: SearchType = SearchType.TEXT,
               case_sensitive: bool = False) -> List[SearchResult]:
        """统一搜索入口"""
        self.results = []
        self.stats = {"files_scanned": 0, "lines_scanned": 0, "matches_found": 0}
        
        if search_type == SearchType.TEXT:
            self.results = self.search_text(query, case_sensitive)
        elif search_type == SearchType.FUNCTION:
            self.results = self.search_function(query)
        elif search_type == SearchType.CLASS:
            self.results = self.search_class(query)
        elif search_type == SearchType.PATTERN:
            self.results = self.search_pattern(query)
        elif search_type == SearchType.REGEX:
            self.results = self._regex_search(re.compile(query))
        
        return self.results
    
    def get_stats(self) -> Dict:
        """获取搜索统计"""
        return self.stats
    
    def export_results(self, output_format: str = "json") -> str:
        """导出搜索结果"""
        export_data = {
            "total_results": len(self.results),
            "stats": self.stats,
            "results": [
                {
                    "file": r.file_path,
                    "line": r.line_number,
                    "content": r.line_content,
                    "type": r.match_type,
                    "context": r.context_lines
                }
                for r in self.results
            ]
        }
        
        if output_format == "json":
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif output_format == "text":
            lines = ["=" * 60]
            lines.append(f"搜索结果 ({len(self.results)} 条匹配)")
            lines.append("=" * 60)
            
            current_file = None
            for r in self.results:
                if r.file_path != current_file:
                    current_file = r.file_path
                    lines.append(f"\n📁 {r.file_path}")
                    lines.append("-" * 40)
                
                lines.append(f"  {r.line_number:4d} │ {r.line_content[:80]}")
            
            return '\n'.join(lines)
        
        return str(export_data)


def main():
    parser = argparse.ArgumentParser(
        description="🧠 Smart Code Search - 智能代码搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--path', '-p', default='.', help='搜索根目录')
    parser.add_argument('--search', '-s', help='搜索文本')
    parser.add_argument('--function', '-f', help='搜索函数')
    parser.add_argument('--class', '-c', dest='class_name', help='搜索类')
    parser.add_argument('--pattern', '-P', help='使用正则表达式搜索')
    parser.add_argument('--type', '-t', choices=['text', 'function', 'class', 'pattern', 'regex'],
                       default='text', help='搜索类型')
    parser.add_argument('--output', '-o', choices=['json', 'text'], default='text',
                       help='输出格式')
    parser.add_argument('--case-sensitive', '-i', action='store_true',
                       help='区分大小写')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细统计')
    
    args = parser.parse_args()
    
    if not any([args.search, args.function, args.class_name, args.pattern]):
        parser.print_help()
        print("\n💡 示例:")
        print("  python code_search.py --path ./src --search 'TODO'")
        print("  python code_search.py --path ./src --function 'test_'")
        print("  python code_search.py --path ./src --class 'User'")
        print("  python code_search.py --path ./src --pattern 'TODO|FIXME'")
        return
    
    engine = CodeSearchEngine(args.path)
    
    # 确定搜索类型
    search_type = SearchType(args.type)
    query = args.search or args.function or args.class_name or args.pattern
    
    results = engine.search(query, search_type, args.caseSensitive)
    
    # 输出结果
    print(engine.export_results(args.output))
    
    if args.verbose:
        print("\n📊 统计信息:")
        print(f"  扫描文件: {engine.stats['files_scanned']}")
        print(f"  扫描行数: {engine.stats['lines_scanned']}")
        print(f"  匹配数量: {engine.stats['matches_found']}")


if __name__ == "__main__":
    main()
