#!/usr/bin/env python3
"""
智能代码搜索器 - Day 63
=======================
在代码库中智能搜索函数、类、注释、模式等

功能:
- 🔍 多模式搜索 (函数、类、注释、字符串、导入等)
- 📊 智能匹配 (正则表达式、模糊搜索)
- 📈 结果统计 (出现次数、上下文分析)
- 🎨 多种输出格式 (终端、JSON、HTML报告)
- 🧠 学习模式 (自动学习代码模式)
"""

import re
import json
import ast
import os
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from html import escape


class SearchMode(Enum):
    """搜索模式"""
    FUNCTIONS = "functions"      # 搜索函数定义
    CLASSES = "classes"         # 搜索类定义
    COMMENTS = "comments"       # 搜索注释
    STRINGS = "strings"         # 搜索字符串
    IMPORTS = "imports"         # 搜索导入语句
    REGEX = "regex"             # 正则表达式搜索
    FUZZY = "fuzzy"             # 模糊搜索
    PATTERN = "pattern"         # 自定义模式


@dataclass
class SearchResult:
    """搜索结果"""
    file_path: str
    line_number: int
    line_content: str
    match_type: str
    match_text: str
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)


@dataclass
class SearchStats:
    """搜索统计"""
    total_files: int = 0
    total_matches: int = 0
    matches_by_type: Dict[str, int] = field(default_factory=dict)
    matches_by_file: Dict[str, int] = field(default_factory=dict)
    files_with_matches: List[str] = field(default_factory=list)
    search_time_ms: float = 0.0


class CodeSearcher:
    """智能代码搜索器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.results: List[SearchResult] = []
        self.stats = SearchStats()
        
        # 常见编程语言的文件扩展名
        self.language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bash': 'bash',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
        }
        
        # 代码模式库
        self.pattern_library = {
            'api_endpoint': r'@(?:get|post|put|delete|patch)\s*\(?\s*[\'"]/?[\w/\-{}]+[\'"]?\s*\)?',
            'async_function': r'async\s+def\s+\w+\s*\(',
            'generator': r'yield\s+',
            'decorator': r'@\w+',
            'exception_handler': r'except\s+(?:\w+:|)s*\n',
            'type_hint': r':\s*(?:int|str|bool|list|dict|Optional|Union)\b',
            'list_comprehension': r'\[\s*(?:.*\s+for\s+.*\s+in\s+.*|)\s*\]',
            'lambda': r'\b\w+\s*=\s*lambda\s+',
            'fstring': r'f[\'"]',
            'f_string': r'f"[^"]*\{[^}]+\}[^"]*"',
            'test_assertion': r'self\.assert\w+\s*\(',
            'print_statement': r'print\s*\(',
            'logging': r'logging\.(debug|info|warning|error|critical)\s*\(',
            'try_except': r'try\s*:|except\s+',
            'with_statement': r'with\s+\w+\s+as\s+\w+\s*:',
            'property': r'@property',
            'classmethod': r'@classmethod',
            'staticmethod': r'@staticmethod',
        }
    
    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return list(self.language_extensions.keys())
    
    def is_code_file(self, file_path: Path) -> bool:
        """判断是否为代码文件"""
        return file_path.suffix.lower() in self.language_extensions
    
    def get_language(self, file_path: Path) -> str:
        """获取文件语言"""
        return self.language_extensions.get(file_path.suffix.lower(), 'unknown')
    
    def get_files(self, extensions: Optional[List[str]] = None, 
                  exclude_dirs: Optional[List[str]] = None) -> List[Path]:
        """获取代码文件列表"""
        if extensions is None:
            extensions = self.get_supported_extensions()
        
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build']
        
        files = []
        for root, dirs, filenames in os.walk(self.root_dir):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for filename in filenames:
                file_path = Path(root) / filename
                if (file_path.suffix.lower() in extensions and 
                    file_path.is_file()):
                    files.append(file_path)
        
        return files
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def parse_python_ast(self, content: str) -> Dict[str, List[Dict]]:
        """解析Python AST"""
        results = {
            'functions': [],
            'classes': [],
            'imports': [],
            'decorators': [],
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    results['functions'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'col_offset': node.col_offset,
                    })
                elif isinstance(node, ast.ClassDef):
                    results['classes'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'col_offset': node.col_offset,
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        results['imports'].append({
                            'name': alias.name,
                            'lineno': node.lineno,
                            'type': 'import',
                        })
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        results['imports'].append({
                            'name': alias.name,
                            'lineno': node.lineno,
                            'type': 'from_import',
                            'module': node.module,
                        })
        except SyntaxError:
            pass
        
        return results
    
    def search_functions(self, content: str, pattern: str, 
                         use_regex: bool = False) -> List[SearchResult]:
        """搜索函数定义"""
        results = []
        lines = content.split('\n')
        
        # 使用AST解析
        ast_results = self.parse_python_ast(content)
        
        for func in ast_results['functions']:
            if use_regex:
                if re.search(pattern, func['name']):
                    line_content = lines[func['lineno'] - 1] if func['lineno'] <= len(lines) else ""
                    results.append(SearchResult(
                        file_path="",  # 稍后设置
                        line_number=func['lineno'],
                        line_content=line_content,
                        match_type="function",
                        match_text=func['name'],
                    ))
            else:
                if pattern.lower() in func['name'].lower():
                    line_content = lines[func['lineno'] - 1] if func['lineno'] <= len(lines) else ""
                    results.append(SearchResult(
                        file_path="",
                        line_number=func['lineno'],
                        line_content=line_content,
                        match_type="function",
                        match_text=func['name'],
                    ))
        
        return results
    
    def search_classes(self, content: str, pattern: str,
                       use_regex: bool = False) -> List[SearchResult]:
        """搜索类定义"""
        results = []
        lines = content.split('\n')
        
        ast_results = self.parse_python_ast(content)
        
        for cls in ast_results['classes']:
            if use_regex:
                if re.search(pattern, cls['name']):
                    line_content = lines[cls['lineno'] - 1] if cls['lineno'] <= len(lines) else ""
                    results.append(SearchResult(
                        file_path="",
                        line_number=cls['lineno'],
                        line_content=line_content,
                        match_type="class",
                        match_text=cls['name'],
                    ))
            else:
                if pattern.lower() in cls['name'].lower():
                    line_content = lines[cls['lineno'] - 1] if cls['lineno'] <= len(lines) else ""
                    results.append(SearchResult(
                        file_path="",
                        line_number=cls['lineno'],
                        line_content=line_content,
                        match_type="class",
                        match_text=cls['name'],
                    ))
        
        return results
    
    def search_comments(self, content: str, pattern: str,
                       use_regex: bool = False) -> List[SearchResult]:
        """搜索注释"""
        results = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查单行注释
            if '#' in line:
                comment_part = line.split('#', 1)[1]
                if use_regex:
                    if re.search(pattern, comment_part):
                        results.append(SearchResult(
                            file_path="",
                            line_number=i,
                            line_content=line,
                            match_type="comment",
                            match_text=comment_part.strip(),
                        ))
                else:
                    if pattern.lower() in comment_part.lower():
                        results.append(SearchResult(
                            file_path="",
                            line_number=i,
                            line_content=line,
                            match_type="comment",
                            match_text=comment_part.strip(),
                        ))
        
        return results
    
    def search_strings(self, content: str, pattern: str,
                      use_regex: bool = False) -> List[SearchResult]:
        """搜索字符串"""
        results = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 查找字符串 (单引号、双引号、三引号)
            string_pattern = r'(?:\'\'\'|"""|\'|")'
            
            if use_regex:
                if re.search(pattern, line):
                    results.append(SearchResult(
                        file_path="",
                        line_number=i,
                        line_content=line,
                        match_type="string",
                        match_text=line.strip(),
                    ))
            else:
                if pattern.lower() in line.lower():
                    results.append(SearchResult(
                        file_path="",
                        line_number=i,
                        line_content=line,
                        match_type="string",
                        match_text=line.strip(),
                    ))
        
        return results
    
    def search_imports(self, content: str, pattern: str,
                      use_regex: bool = False) -> List[SearchResult]:
        """搜索导入语句"""
        results = []
        lines = content.split('\n')
        
        ast_results = self.parse_python_ast(content)
        
        for imp in ast_results['imports']:
            full_name = imp.get('name', '')
            if imp.get('module'):
                full_name = f"{imp['module']}.{imp['name']}"
            
            if use_regex:
                if re.search(pattern, full_name):
                    line_content = lines[imp['lineno'] - 1] if imp['lineno'] <= len(lines) else ""
                    results.append(SearchResult(
                        file_path="",
                        line_number=imp['lineno'],
                        line_content=line_content,
                        match_type="import",
                        match_text=full_name,
                    ))
            else:
                if pattern.lower() in full_name.lower():
                    line_content = lines[imp['lineno'] - 1] if imp['lineno'] <= len(lines) else ""
                    results.append(SearchResult(
                        file_path="",
                        line_number=imp['lineno'],
                        line_content=line_content,
                        match_type="import",
                        match_text=full_name,
                    ))
        
        return results
    
    def search_regex(self, content: str, pattern: str) -> List[SearchResult]:
        """正则表达式搜索"""
        results = []
        lines = content.split('\n')
        
        try:
            regex = re.compile(pattern)
            
            for i, line in enumerate(lines, 1):
                matches = regex.findall(line)
                if matches:
                    results.append(SearchResult(
                        file_path="",
                        line_number=i,
                        line_content=line,
                        match_type="regex",
                        match_text=str(matches),
                    ))
        except re.error as e:
            print(f"正则表达式错误: {e}")
        
        return results
    
    def search_fuzzy(self, content: str, pattern: str,
                    threshold: float = 0.6) -> List[SearchResult]:
        """模糊搜索 (简单实现)"""
        results = []
        lines = content.split('\n')
        
        # 简单的模糊匹配: 包含大部分字符
        pattern_chars = set(pattern.lower())
        min_chars = int(len(pattern_chars) * threshold)
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            line_chars = set(line_lower)
            
            # 检查是否包含大部分字符
            common_chars = pattern_chars & line_chars
            
            if len(common_chars) >= min_chars:
                results.append(SearchResult(
                    file_path="",
                    line_number=i,
                    line_content=line,
                    match_type="fuzzy",
                    match_text=line.strip()[:100],  # 截取前100字符
                ))
        
        return results
    
    def search_pattern(self, content: str, pattern_key: str) -> List[SearchResult]:
        """使用预定义模式搜索"""
        results = []
        
        if pattern_key not in self.pattern_library:
            print(f"未知模式: {pattern_key}")
            return results
        
        pattern = self.pattern_library[pattern_key]
        return self.search_regex(content, pattern)
    
    def add_context(self, result: SearchResult, content: str, 
                   context_lines: int = 2) -> SearchResult:
        """添加上下文"""
        lines = content.split('\n')
        
        start = max(0, result.line_number - 1 - context_lines)
        end = min(len(lines), result.line_number - 1 + context_lines + 1)
        
        result.context_before = lines[start:result.line_number - 1]
        result.context_after = lines[result.line_number:end]
        
        return result
    
    def search(self, pattern: str, mode: SearchMode = SearchMode.REGEX,
              extensions: Optional[List[str]] = None,
              exclude_dirs: Optional[List[str]] = None,
              context_lines: int = 2,
              use_regex: bool = False) -> List[SearchResult]:
        """主搜索函数"""
        import time
        start_time = time.time()
        
        files = self.get_files(extensions, exclude_dirs)
        self.stats.total_files = len(files)
        self.results = []
        
        for file_path in files:
            content = self.read_file_content(file_path)
            if content is None:
                continue
            
            file_results = []
            
            if mode == SearchMode.FUNCTIONS:
                file_results = self.search_functions(content, pattern, use_regex)
            elif mode == SearchMode.CLASSES:
                file_results = self.search_classes(content, pattern, use_regex)
            elif mode == SearchMode.COMMENTS:
                file_results = self.search_comments(content, pattern, use_regex)
            elif mode == SearchMode.STRINGS:
                file_results = self.search_strings(content, pattern, use_regex)
            elif mode == SearchMode.IMPORTS:
                file_results = self.search_imports(content, pattern, use_regex)
            elif mode == SearchMode.REGEX:
                file_results = self.search_regex(content, pattern)
            elif mode == SearchMode.FUZZY:
                file_results = self.search_fuzzy(content, pattern)
            elif mode == SearchMode.PATTERN:
                file_results = self.search_pattern(content, pattern)
            
            # 设置文件路径和添加上下文
            for result in file_results:
                result.file_path = str(file_path)
                self.add_context(result, content, context_lines)
            
            self.results.extend(file_results)
            
            # 统计
            if file_results:
                self.stats.files_with_matches.append(str(file_path))
                self.stats.matches_by_file[str(file_path)] = len(file_results)
        
        # 计算统计
        self.stats.total_matches = len(self.results)
        for result in self.results:
            self.stats.matches_by_type[result.match_type] = \
                self.stats.matches_by_type.get(result.match_type, 0) + 1
        
        self.stats.search_time_ms = (time.time() - start_time) * 1000
        
        return self.results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取搜索统计"""
        return {
            'total_files': self.stats.total_files,
            'total_matches': self.stats.total_matches,
            'matches_by_type': self.stats.matches_by_type,
            'matches_by_file': dict(sorted(self.stats.matches_by_file.items(), 
                                          key=lambda x: x[1], reverse=True)[:10]),
            'files_with_matches': len(self.stats.files_with_matches),
            'search_time_ms': round(self.stats.search_time_ms, 2),
        }
    
    def print_results(self, results: Optional[List[SearchResult]] = None,
                      max_display: int = 50):
        """打印搜索结果"""
        if results is None:
            results = self.results
        
        if not results:
            print("未找到匹配结果")
            return
        
        print(f"\n找到 {len(results)} 个匹配结果:\n")
        
        for i, result in enumerate(results[:max_display], 1):
            print(f"{i}. {result.file_path}:{result.line_number}")
            print(f"   类型: {result.match_type}")
            print(f"   内容: {result.line_content.strip()[:100]}")
            if result.context_before:
                print("   上下文:")
                for line in result.context_before:
                    print(f"     {line}")
            print()
        
        if len(results) > max_display:
            print(f"... 还有 {len(results) - max_display} 个结果")
    
    def export_json(self, results: Optional[List[SearchResult]] = None,
                   output_path: str = "search_results.json") -> str:
        """导出为JSON"""
        if results is None:
            results = self.results
        
        output = {
            'search_stats': self.get_stats(),
            'results': [
                {
                    'file_path': r.file_path,
                    'line_number': r.line_number,
                    'line_content': r.line_content,
                    'match_type': r.match_type,
                    'match_text': r.match_text,
                    'context_before': r.context_before,
                    'context_after': r.context_after,
                }
                for r in results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        return f"结果已导出到: {output_path}"
    
    def export_html(self, results: Optional[List[SearchResult]] = None,
                   output_path: str = "search_results.html") -> str:
        """导出为HTML报告"""
        if results is None:
            results = self.results
        
        stats = self.get_stats()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>代码搜索结果</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-box {{ background: #007bff; color: white; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-box .value {{ font-size: 24px; font-weight: bold; }}
        .stat-box .label {{ font-size: 12px; opacity: 0.9; }}
        .result {{ margin: 15px 0; padding: 15px; border-left: 4px solid #007bff; background: #f8f9fa; }}
        .result .meta {{ color: #666; font-size: 12px; margin-bottom: 5px; }}
        .result .content {{ font-family: monospace; background: #fff; padding: 10px; border-radius: 3px; margin: 5px 0; white-space: pre-wrap; }}
        .result .context {{ font-family: monospace; color: #666; font-size: 11px; }}
        .type-function {{ border-color: #28a745; }}
        .type-class {{ border-color: #dc3545; }}
        .type-comment {{ border-color: #ffc107; }}
        .type-string {{ border-color: #17a2b8; }}
        .type-import {{ border-color: #6f42c1; }}
        .type-regex {{ border-color: #fd7e14; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 代码搜索结果</h1>
        
        <div class="stats">
            <div class="stat-box">
                <div class="value">{stats['total_files']}</div>
                <div class="label">扫描文件数</div>
            </div>
            <div class="stat-box">
                <div class="value">{stats['total_matches']}</div>
                <div class="label">匹配结果数</div>
            </div>
            <div class="stat-box">
                <div class="value">{len(stats['files_with_matches'])}</div>
                <div class="label">含匹配文件数</div>
            </div>
            <div class="stat-box">
                <div class="value">{stats['search_time_ms']}ms</div>
                <div class="label">搜索耗时</div>
            </div>
        </div>
        
        <h2>📊 匹配类型分布</h2>
        <div class="stats">
            {"".join([f'''<div class="stat-box" style="background: #{hash(t[:7])%0xFFFFFF:06x}">
                <div class="value">{c}</div>
                <div class="label">{t}</div>
            </div>''' for t, c in stats['matches_by_type'].items()])}
        </div>
        
        <h2>📝 搜索结果</h2>
"""
        
        for result in results[:100]:
            html += f"""
        <div class="result type-{result.match_type}">
            <div class="meta">
                📁 {escape(result.file_path)} | 📍 第{result.line_number}行 | 🏷️ {result.match_type}
            </div>
            <div class="content">{escape(result.line_content.strip())}</div>
            {"".join([f"<div class='context'>{escape(line)}</div>" for line in result.context_before])}
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return f"HTML报告已导出到: {output_path}"


def demo():
    """演示"""
    print("=" * 60)
    print("🔍 智能代码搜索器 - Day 63")
    print("=" * 60)
    
    # 创建搜索器
    searcher = CodeSearcher()
    
    # 演示搜索功能
    print("\n📊 支持的文件类型:")
    extensions = searcher.get_supported_extensions()
    print(", ".join(extensions[:15]) + "...")
    
    print("\n📦 内置搜索模式:")
    for name, pattern in list(searcher.pattern_library.items())[:10]:
        print(f"  - {name}: {pattern[:50]}...")
    
    # 搜索示例
    print("\n" + "-" * 60)
    print("🔍 搜索演示: 搜索所有函数定义...")
    results = searcher.search("def ", mode=SearchMode.FUNCTIONS)
    stats = searcher.get_stats()
    print(f"  ✅ 扫描 {stats['total_files']} 个文件")
    print(f"  📝 找到 {stats['total_matches']} 个匹配")
    print(f"  ⏱️ 耗时 {stats['search_time_ms']}ms")
    
    print("\n" + "-" * 60)
    print("🔍 搜索演示: 正则搜索所有API端点...")
    results = searcher.search(r"@(get|post|put|delete)", mode=SearchMode.REGEX)
    stats = searcher.get_stats()
    print(f"  ✅ 扫描 {stats['total_files']} 个文件")
    print(f"  📝 找到 {stats['total_matches']} 个API端点")
    
    print("\n" + "-" * 60)
    print("🔍 搜索演示: 搜索所有类定义...")
    results = searcher.search("class", mode=SearchMode.CLASSES)
    stats = searcher.get_stats()
    print(f"  ✅ 扫描 {stats['total_files']} 个文件")
    print(f"  📝 找到 {stats['total_matches']} 个类定义")
    
    print("\n" + "-" * 60)
    print("🔍 搜索演示: 搜索所有导入语句...")
    results = searcher.search("import", mode=SearchMode.IMPORTS)
    stats = searcher.get_stats()
    print(f"  ✅ 扫描 {stats['total_files']} 个文件")
    print(f"  📝 找到 {stats['total_matches']} 个导入语句")
    
    print("\n" + "-" * 60)
    print("🔍 搜索演示: 使用预定义模式搜索异步函数...")
    results = searcher.search("async_function", mode=SearchMode.PATTERN)
    stats = searcher.get_stats()
    print(f"  ✅ 扫描 {stats['total_files']} 个文件")
    print(f"  📝 找到 {stats['total_matches']} 个异步函数")
    
    print("\n" + "-" * 60)
    print("📁 导出示例...")
    searcher.search("def ", mode=SearchMode.FUNCTIONS)
    searcher.export_json("search_demo.json")
    searcher.export_html("search_demo.html")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成!")
    print("=" * 60)
    
    print("\n💡 使用方法:")
    print("  python 2026-02-03_063_smart_code_searcher.py demo")
    print("  python 2026-02-03_063_smart_code_searcher.py search '函数名' --mode functions")
    print("  python 2026-02-03_063_smart_code_searcher.py search 'pattern' --mode regex")
    print("  python 2026-02-03_063_smart_code_searcher.py stats --json")
    print("  python 2026-02-03_063_smart_code_searcher.py export --html")


def cli():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="智能代码搜索器 - 在代码库中搜索函数、类、注释等"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # search命令
    search_parser = subparsers.add_parser('search', help='搜索代码')
    search_parser.add_argument('pattern', help='搜索模式')
    search_parser.add_argument('--mode', choices=['functions', 'classes', 'comments', 
                                                    'strings', 'imports', 'regex', 
                                                    'fuzzy', 'pattern'],
                               default='regex', help='搜索模式')
    search_parser.add_argument('--extensions', help='文件扩展名(逗号分隔)')
    search_parser.add_argument('--exclude', help='排除目录(逗号分隔)')
    search_parser.add_argument('--context', type=int, default=2, help='上下文行数')
    search_parser.add_argument('--limit', type=int, default=50, help='显示数量限制')
    
    # stats命令
    stats_parser = subparsers.add_parser('stats', help='显示统计')
    stats_parser.add_argument('--json', action='store_true', help='JSON格式输出')
    
    # export命令
    export_parser = subparsers.add_parser('export', help='导出结果')
    export_parser.add_argument('--json', metavar='PATH', help='导出JSON')
    export_parser.add_argument('--html', metavar='PATH', help='导出HTML报告')
    
    # demo命令
    subparsers.add_parser('demo', help='运行演示')
    
    args = parser.parse_args()
    
    if args.command == 'demo':
        demo()
        return
    
    searcher = CodeSearcher()
    
    if args.command == 'search':
        # 解析参数
        mode = SearchMode(args.mode)
        extensions = args.extensions.split(',') if args.extensions else None
        exclude_dirs = args.exclude.split(',') if args.exclude else None
        
        # 执行搜索
        results = searcher.search(
            pattern=args.pattern,
            mode=mode,
            extensions=extensions,
            exclude_dirs=exclude_dirs,
            context_lines=args.context,
        )
        
        # 显示结果
        searcher.print_results(results, args.limit)
        
        # 显示统计
        print("\n📊 搜索统计:")
        stats = searcher.get_stats()
        print(f"  扫描文件数: {stats['total_files']}")
        print(f"  匹配结果数: {stats['total_matches']}")
        print(f"  搜索耗时: {stats['search_time_ms']}ms")
    
    elif args.command == 'stats':
        searcher.search("", mode=SearchMode.REGEX)  # 扫描文件
        stats = searcher.get_stats()
        
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\n📊 代码库统计:")
            print(f"  扫描文件数: {stats['total_files']}")
            print(f"  文件类型分布: {stats['matches_by_type']}")
    
    elif args.command == 'export':
        if args.json:
            searcher.export_json(args.json)
        if args.html:
            searcher.export_html(args.html)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        demo()
