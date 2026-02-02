#!/usr/bin/env python3
"""
智能代码搜索器 - Smart Code Searcher
====================================
功能强大的代码库搜索工具，支持多种搜索模式和过滤功能。

核心功能:
- 🔍 多模式搜索（内容/文件名/正则/通配符）
- 📁 高级文件过滤（类型/大小/日期）
- 🎯 智能结果排序和去重
- 📊 搜索统计和可视化
- 💾 结果导出（JSON/CSV/Markdown）
- 🔗 跨目录搜索和目录树浏览
"""

import os
import re
import json
import time
import fnmatch
import hashlib
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple, Set, Callable, Generator
from enum import Enum
from collections import defaultdict
import base64


class SearchMode(Enum):
    """搜索模式"""
    CONTENT = "content"      # 文件内容搜索
    FILENAME = "filename"    # 文件名搜索
    REGEX = "regex"          # 正则表达式
    GLOB = "glob"            # 通配符匹配


class SortBy(Enum):
    """排序方式"""
    RELEVANCE = "relevance"  # 相关性
    PATH = "path"            # 路径
    SIZE = "size"            # 文件大小
    MODIFIED = "modified"    # 修改时间
    NAME = "name"            # 文件名


@dataclass
class SearchResult:
    """搜索结果"""
    file_path: str
    line_number: Optional[int]
    line_content: Optional[str]
    match_start: int
    match_end: int
    relevance_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    name: str
    extension: str
    size: int
    modified_time: float
    line_count: int
    content_hash: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SearchConfig:
    """搜索配置"""
    patterns: List[str]
    mode: SearchMode = SearchMode.CONTENT
    search_path: str = "."
    file_types: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    exclude_dirs: Optional[List[str]] = None
    max_file_size: Optional[int] = None  # 单位: 字节
    min_file_size: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    case_sensitive: bool = False
    whole_word: bool = False
    use_and: bool = False  # True: 所有模式都必须匹配
    max_results: int = 1000
    sort_by: SortBy = SortBy.RELEVANCE
    reverse: bool = False
    
    def __post_init__(self):
        if self.file_types:
            self.file_types = [ft.lower() if not ft.startswith('.') else ft.lower() for ft in self.file_types]
        if self.exclude_patterns is None:
            self.exclude_patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', '*.pyc', '*.o', '*.a']
        if self.exclude_dirs is None:
            self.exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', '.idea', '.vscode']


class SmartCodeSearcher:
    """智能代码搜索器"""
    
    def __init__(self):
        self.index_db = None
        self._init_database()
    
    def _init_database(self):
        """初始化索引数据库"""
        self.index_db = sqlite3.connect(':memory:')
        cursor = self.index_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_index (
                path TEXT PRIMARY KEY,
                name TEXT,
                extension TEXT,
                size INTEGER,
                modified_time REAL,
                line_count INTEGER,
                content_hash TEXT,
                content TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                search_path TEXT,
                result_count INTEGER,
                timestamp REAL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_extension ON file_index(extension)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_modified ON file_index(modified_time)')
        self.index_db.commit()
    
    def _calculate_relevance(self, match_text: str, patterns: List[str], mode: SearchMode) -> float:
        """计算相关性分数"""
        score = 0.0
        match_lower = match_text.lower()
        
        for pattern in patterns:
            pattern_lower = pattern.lower()
            if mode == SearchMode.CONTENT:
                # 精确匹配得分最高
                if pattern == match_text:
                    score += 10.0
                elif pattern_lower == match_lower:
                    score += 8.0
                elif pattern in match_text:
                    score += 5.0
                elif pattern_lower in match_lower:
                    score += 3.0
            elif mode == SearchMode.REGEX:
                try:
                    if re.search(pattern, match_text):
                        score += 7.0
                except re.error:
                    pass
            elif mode == SearchMode.GLOB:
                if fnmatch.fnmatch(match_text, pattern):
                    score += 7.0
                elif fnmatch.fnmatch(match_lower, pattern_lower):
                    score += 5.0
            elif mode == SearchMode.FILENAME:
                if pattern == match_text:
                    score += 10.0
                elif pattern_lower in match_lower:
                    score += 6.0
        
        # 位置权重：开头匹配加分
        if match_text.startswith(patterns[0]) if patterns else False:
            score += 2.0
        
        return score
    
    def _should_exclude(self, path: str, exclude_patterns: List[str], exclude_dirs: List[str]) -> bool:
        """检查是否应该排除"""
        path_parts = path.split(os.sep)
        
        # 检查目录排除
        for part in path_parts:
            if part in exclude_dirs:
                return True
        
        # 检查文件模式排除
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
        
        return False
    
    def _get_file_hash(self, content: bytes) -> str:
        """计算文件哈希"""
        return hashlib.md5(content).hexdigest()
    
    def _read_file_content(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """安全读取文件内容"""
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
        except (IOError, OSError):
            return None
    
    def index_directory(self, path: str, extensions: Optional[List[str]] = None) -> int:
        """索引目录中的文件"""
        cursor = self.index_db.cursor()
        indexed_count = 0
        
        for root, dirs, files in os.walk(path):
            # 过滤目录
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', '.idea', '.vscode']]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                # 过滤扩展名
                if extensions and ext not in extensions:
                    continue
                
                try:
                    stat = os.stat(file_path)
                    content = self._read_file_content(file_path)
                    if content is None:
                        continue
                    
                    content_hash = self._get_file_hash(content.encode('utf-8'))
                    line_count = content.count('\n') + 1
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO file_index 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (file_path, file, ext, stat.st_size, stat.st_mtime, line_count, content_hash, content[:10000]))
                    
                    indexed_count += 1
                except (IOError, OSError):
                    continue
        
        self.index_db.commit()
        return indexed_count
    
    def search(self, config: SearchConfig) -> List[SearchResult]:
        """执行搜索"""
        results = []
        
        if config.mode == SearchMode.FILENAME:
            return self._search_filename(config)
        else:
            return self._search_content(config)
    
    def _search_filename(self, config: SearchConfig) -> List[SearchResult]:
        """文件名搜索"""
        results = []
        cursor = self.index_db.cursor()
        
        query_conditions = []
        params = []
        
        for pattern in config.patterns:
            query_conditions.append('name LIKE ?')
            params.append(f'%{pattern}%' if not config.case_sensitive else pattern)
        
        if config.file_types:
            query_conditions.append('extension IN ({})'.format(','.join(['?'] * len(config.file_types))))
            params.extend(config.file_types)
        
        if config.max_file_size:
            query_conditions.append('size <= ?')
            params.append(config.max_file_size)
        
        if config.min_file_size:
            query_conditions.append('size >= ?')
            params.append(config.min_file_size)
        
        where_clause = ' AND '.join(query_conditions) if query_conditions else '1=1'
        
        cursor.execute(f'SELECT * FROM file_index WHERE {where_clause}', params)
        
        for row in cursor.fetchall():
            path, name, ext, size, modified, line_count, content_hash, _ = row
            score = self._calculate_relevance(name, config.patterns, SearchMode.FILENAME)
            results.append(SearchResult(path, None, None, 0, 0, score))
        
        return self._sort_results(results, config.sort_by, config.reverse)[:config.max_results]
    
    def _search_content(self, config: SearchConfig) -> List[SearchResult]:
        """内容搜索"""
        results = []
        cursor = self.index_db.cursor()
        
        # 获取所有文件
        cursor.execute('SELECT path, content FROM file_index')
        
        for path, content in cursor.fetchall():
            if not content:
                continue
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern in config.patterns:
                    matches = []
                    
                    if config.mode == SearchMode.CONTENT:
                        if config.case_sensitive:
                            if config.whole_word:
                                pattern_with_boundaries = r'\b{}\b'.format(re.escape(pattern))
                                matches = [(m.start(), m.end()) for m in re.finditer(pattern_with_boundaries, line)]
                            else:
                                matches = [(m.start(), m.end()) for m in re.finditer(re.escape(pattern), line)]
                        else:
                            line_lower = line.lower()
                            pattern_lower = pattern.lower()
                            if config.whole_word:
                                pattern_with_boundaries = r'\b{}\b'.format(re.escape(pattern_lower))
                                matches = [(m.start(), m.end()) for m in re.finditer(pattern_with_boundaries, line_lower)]
                            else:
                                matches = [(m.start(), m.end()) for m in re.finditer(re.escape(pattern_lower), line_lower)]
                    
                    elif config.mode == SearchMode.REGEX:
                        try:
                            flags = 0 if config.case_sensitive else re.IGNORECASE
                            matches = [(m.start(), m.end()) for m in re.finditer(pattern, line, flags)]
                        except re.error:
                            continue
                    
                    elif config.mode == SearchMode.GLOB:
                        if fnmatch.fnmatch(line, pattern) if config.case_sensitive else fnmatch.fnmatch(line.lower(), pattern.lower()):
                            matches = [(0, len(line))]
                    
                    if matches:
                        score = self._calculate_relevance(line, config.patterns, config.mode)
                        
                        if config.use_and:
                            all_match = all(any(m[0] >= 0 for m in line_matches) for line_matches in [matches])
                            if not all_match:
                                continue
                        
                        for match_start, match_end in matches:
                            results.append(SearchResult(
                                path, line_num, line, match_start, match_end, score
                            ))
        
        # 去重：同一文件只保留最高分的结果
        file_best = {}
        for r in results:
            if r.file_path not in file_best or r.relevance_score > file_best[r.file_path].relevance_score:
                file_best[r.file_path] = r
        
        final_results = list(file_best.values())
        return self._sort_results(final_results, config.sort_by, config.reverse)[:config.max_results]
    
    def _sort_results(self, results: List[SearchResult], sort_by: SortBy, reverse: bool) -> List[SearchResult]:
        """排序结果"""
        if sort_by == SortBy.RELEVANCE:
            results.sort(key=lambda x: x.relevance_score, reverse=reverse)
        elif sort_by == SortBy.PATH:
            results.sort(key=lambda x: x.file_path, reverse=reverse)
        elif sort_by == SortBy.NAME:
            results.sort(key=lambda x: os.path.basename(x.file_path), reverse=reverse)
        elif sort_by == SortBy.SIZE:
            results.sort(key=lambda x: os.path.getsize(x.file_path) if os.path.exists(x.file_path) else 0, reverse=reverse)
        elif sort_by == SortBy.MODIFIED:
            results.sort(key=lambda x: os.path.getmtime(x.file_path) if os.path.exists(x.file_path) else 0, reverse=reverse)
        
        return results
    
    def find_files(self, 
                   path: str = ".",
                   pattern: str = "*",
                   file_types: Optional[List[str]] = None,
                   max_depth: int = -1) -> List[str]:
        """查找文件"""
        results = []
        
        def _search(current_path: str, depth: int):
            if max_depth > 0 and depth >= max_depth:
                return
            
            try:
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)
                    
                    if os.path.isdir(item_path):
                        if item not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', '.idea', '.vscode']:
                            _search(item_path, depth + 1)
                    else:
                        if fnmatch.fnmatch(item, pattern):
                            ext = os.path.splitext(item)[1].lower()
                            if not file_types or ext in file_types:
                                results.append(item_path)
            except PermissionError:
                pass
        
        _search(path, 0)
        return results
    
    def get_file_tree(self, path: str = ".", max_depth: int = 3) -> Dict[str, Any]:
        """获取目录树结构"""
        def _build_tree(current_path: str, depth: int) -> Dict:
            if depth >= max_depth:
                return {'type': 'file', 'name': os.path.basename(current_path)}
            
            try:
                items = os.listdir(current_path)
            except PermissionError:
                return {'type': 'file', 'name': os.path.basename(current_path)}
            
            dirs = []
            files = []
            
            for item in sorted(items):
                if item in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', '.idea', '.vscode']:
                    continue
                
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    dirs.append(item)
                else:
                    files.append(item)
            
            result = {
                'type': 'directory',
                'name': os.path.basename(current_path),
                'directories': [_build_tree(os.path.join(current_path, d), depth + 1) for d in dirs],
                'files': [{'type': 'file', 'name': f} for f in files[:10]]  # 限制文件数量
            }
            
            if len(files) > 10:
                result['files'].append({'type': 'file', 'name': f'... and {len(files) - 10} more files'})
            
            return result
        
        return _build_tree(path, 0)
    
    def grep(self, pattern: str, path: str = ".", recursive: bool = True) -> List[SearchResult]:
        """类似grep的快速搜索"""
        config = SearchConfig(
            patterns=[pattern],
            mode=SearchMode.CONTENT,
            search_path=path,
            max_results=500
        )
        return self.search(config)
    
    def find_large_files(self, path: str = ".", min_size_mb: float = 1.0) -> List[FileInfo]:
        """查找大文件"""
        min_size = int(min_size_mb * 1024 * 1024)
        cursor = self.index_db.cursor()
        cursor.execute('SELECT * FROM file_index WHERE size >= ?', (min_size,))
        
        results = []
        for row in cursor.fetchall():
            path, name, ext, size, modified, line_count, content_hash, _ = row
            results.append(FileInfo(path, name, ext, size, modified, line_count, content_hash))
        
        return sorted(results, key=lambda x: x.size, reverse=True)
    
    def get_statistics(self, path: str = ".") -> Dict[str, Any]:
        """获取目录统计信息"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_extension': defaultdict(int),
            'recent_files': [],
            'largest_files': []
        }
        
        cursor = self.index_db.cursor()
        cursor.execute('SELECT COUNT(*), SUM(size) FROM file_index')
        row = cursor.fetchone()
        stats['total_files'] = row[0] or 0
        stats['total_size'] = row[1] or 0
        
        cursor.execute('SELECT extension, COUNT(*) FROM file_index GROUP BY extension')
        for ext, count in cursor.fetchall():
            stats['by_extension'][ext] = count
        
        cursor.execute('SELECT * FROM file_index ORDER BY modified_time DESC LIMIT 10')
        for row in cursor.fetchall():
            stats['recent_files'].append(FileInfo(*row))
        
        cursor.execute('SELECT * FROM file_index ORDER BY size DESC LIMIT 10')
        for row in cursor.fetchall():
            stats['largest_files'].append(FileInfo(*row))
        
        return stats
    
    def export_results(self, results: List[SearchResult], format: str = 'json', output_path: Optional[str] = None) -> str:
        """导出搜索结果"""
        if format == 'json':
            export_data = [r.to_dict() for r in results]
            content = json.dumps(export_data, indent=2, ensure_ascii=False)
            ext = 'json'
        
        elif format == 'csv':
            lines = ['file_path,line_number,match_content,relevance_score']
            for r in results:
                line_content = r.line_content.replace('"', '""') if r.line_content else ''
                lines.append(f'"{r.file_path}",{r.line_number or ""},"{line_content}",{r.relevance_score}')
            content = '\n'.join(lines)
            ext = 'csv'
        
        elif format == 'markdown':
            lines = ['# 搜索结果\n', f'共找到 {len(results)} 个结果\n\n']
            lines.append('| 文件 | 行号 | 内容 | 分数 |')
            lines.append('|------|------|------|------|')
            for r in results:
                line_preview = r.line_content[:50] + '...' if r.line_content and len(r.line_content) > 50 else r.line_content or ''
                lines.append(f'| {r.file_path} | {r.line_number or "-"} | {line_preview} | {r.relevance_score:.2f} |')
            content = '\n'.join(lines)
            ext = 'md'
        
        else:
            raise ValueError(f'不支持的格式: {format}')
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        
        return content
    
    def search_history(self) -> List[Dict]:
        """获取搜索历史"""
        cursor = self.index_db.cursor()
        cursor.execute('SELECT * FROM search_history ORDER BY timestamp DESC LIMIT 20')
        return [{'query': row[1], 'path': row[2], 'count': row[3], 'time': row[4]} for row in cursor.fetchall()]
    
    def clear_index(self):
        """清空索引"""
        cursor = self.index_db.cursor()
        cursor.execute('DELETE FROM file_index')
        cursor.execute('DELETE FROM search_history')
        self.index_db.commit()


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def demo():
    """演示"""
    print("🔍 智能代码搜索器 - Smart Code Searcher")
    print("=" * 60)
    
    searcher = SmartCodeSearcher()
    
    # 示例1: 索引当前目录
    print("\n📂 索引当前目录...")
    count = searcher.index_directory(".", ['.py', '.txt', '.md', '.js', '.json'])
    print(f"✅ 已索引 {count} 个文件")
    
    # 示例2: 搜索Python文件
    print("\n🐍 查找Python文件...")
    results = searcher.find_files(".", "*.py", ['.py'])
    for r in results[:5]:
        print(f"  - {r}")
    
    # 示例3: 搜索内容
    print("\n🔍 搜索包含 'class' 的文件...")
    config = SearchConfig(
        patterns=['class'],
        mode=SearchMode.CONTENT,
        max_results=10
    )
    results = searcher.search(config)
    for r in results:
        print(f"  📄 {os.path.basename(r.file_path)} (分数: {r.relevance_score:.2f})")
    
    # 示例4: 统计信息
    print("\n📊 目录统计:")
    stats = searcher.get_statistics(".")
    print(f"  - 总文件数: {stats['total_files']}")
    print(f"  - 总大小: {format_size(stats['total_size'])}")
    print(f"  - 按扩展名分布:")
    for ext, count in sorted(stats['by_extension'].items(), key=lambda x: -x[1])[:5]:
        print(f"    {ext or '无扩展名'}: {count}")
    
    # 示例5: 导出结果
    print("\n💾 导出搜索结果...")
    content = searcher.export_results(results, 'markdown')
    print("Markdown格式预览:")
    print(content[:500] + "...")


def interactive_mode():
    """交互式模式"""
    searcher = SmartCodeSearcher()
    searcher.index_directory(".", ['.py', '.txt', '.md', '.js', '.json', '.html', '.css'])
    
    print("\n🎯 智能代码搜索器 - 交互模式")
    print("命令: search <pattern> | find <pattern> | stats | tree | history | exit")
    
    while True:
        try:
            cmd = input("\n🔍 > ").strip()
            if not cmd:
                continue
            
            parts = cmd.split()
            command = parts[0].lower()
            
            if command == 'exit':
                print("👋 再见!")
                break
            
            elif command == 'help':
                print("""
可用命令:
  search <pattern>    - 搜索文件内容
  find <pattern>      - 查找文件名
  stats               - 显示统计信息
  tree                - 显示目录树
  history             - 显示搜索历史
  index               - 重新索引
  clear               - 清空索引
  export <fmt>        - 导出结果 (json/csv/markdown)
  exit                - 退出
                """)
            
            elif command == 'search':
                pattern = ' '.join(parts[1:]) if len(parts) > 1 else ''
                if not pattern:
                    print("❌ 请输入搜索关键词")
                    continue
                
                results = searcher.grep(pattern)
                print(f"找到 {len(results)} 个结果:")
                for r in results[:10]:
                    print(f"  📄 {r.file_path} (分数: {r.relevance_score:.2f})")
                if len(results) > 10:
                    print(f"  ... 还有 {len(results) - 10} 个结果")
            
            elif command == 'find':
                pattern = ' '.join(parts[1:]) if len(parts) > 1 else ''
                if not pattern:
                    print("❌ 请输入文件名模式")
                    continue
                
                results = searcher.find_files(".", pattern)
                print(f"找到 {len(results)} 个文件:")
                for r in results[:10]:
                    print(f"  📄 {r}")
            
            elif command == 'stats':
                stats = searcher.get_statistics(".")
                print(f"总文件: {stats['total_files']}, 总大小: {format_size(stats['total_size'])}")
                for ext, count in list(stats['by_extension'].items())[:5]:
                    print(f"  {ext}: {count}")
            
            elif command == 'tree':
                tree = searcher.get_file_tree(".", max_depth=2)
                print(json.dumps(tree, indent=2, ensure_ascii=False)[:1000])
            
            elif command == 'history':
                history = searcher.search_history()
                for h in history:
                    print(f"  {h['query']} -> {h['count']} 结果")
            
            elif command == 'index':
                searcher.clear_index()
                count = searcher.index_directory(".", ['.py', '.txt', '.md', '.js', '.json', '.html', '.css'])
                print(f"✅ 已索引 {count} 个文件")
            
            elif command == 'clear':
                searcher.clear_index()
                print("✅ 已清空索引")
            
            elif command == 'export':
                fmt = parts[1] if len(parts) > 1 else 'json'
                results = searcher.grep('def ')[:20]
                content = searcher.export_results(results, fmt)
                print(content[:500])
            
            else:
                print(f"❌ 未知命令: {command}")
        
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo()
    else:
        interactive_mode()
