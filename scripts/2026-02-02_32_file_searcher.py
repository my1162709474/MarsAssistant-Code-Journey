#!/usr/bin/env python3
"""
🕵️ 文件搜索查找器 - File Search & Finder
============================================
递归搜索目录，查找匹配特定模式或内容的文件。

功能特性:
- ✨ 按文件名模式搜索 (支持通配符)
- 🔍 按文件内容搜索 (支持正则表达式)
- 📊 按文件类型/大小/修改时间筛选
- 🎯 多条件组合搜索
- 📝 导出搜索结果 (JSON/TXT/CSV)
- 🌈 彩色输出，友好交互

Author: AI Code Journey
Date: 2026-02-02
Version: 1.0.0
"""

import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import fnmatch
import mimetypes

# ANSI颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    @staticmethod
    def colored(text: str, color: str) -> str:
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def success(text: str) -> str:
        return Colors.colored(text, Colors.GREEN)
    
    @staticmethod
    def error(text: str) -> str:
        return Colors.colored(text, Colors.RED)
    
    @staticmethod
    def warning(text: str) -> str:
        return Colors.colored(text, Colors.YELLOW)
    
    @staticmethod
    def info(text: str) -> str:
        return Colors.colored(text, Colors.CYAN)
    
    @staticmethod
    def highlight(text: str) -> str:
        return Colors.colored(text, Colors.MAGENTA)


class FileType(Enum):
    ALL = "all"
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    MEDIA = "media"
    CONFIG = "config"


@dataclass
class SearchOptions:
    name_pattern: Optional[str] = None
    content_pattern: Optional[str] = None
    content_regex: bool = False
    file_type: FileType = FileType.ALL
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    min_mtime: Optional[datetime] = None
    max_mtime: Optional[datetime] = None
    exclude_patterns: List[str] = field(default_factory=list)
    include_hidden: bool = False
    case_sensitive: bool = False
    max_depth: Optional[int] = None


class FileSearcher:
    FILE_TYPE_MAPPINGS = {
        FileType.TEXT: {'txt', 'md', 'rst', 'log', 'json', 'yaml', 'yml', 'xml', 'html', 'htm', 'css'},
        FileType.CODE: {'py', 'js', 'ts', 'go', 'rs', 'java', 'c', 'cpp', 'h', 'hpp', 'rb', 'php', 'swift', 'kt', 'scala'},
        FileType.IMAGE: {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp', 'ico', 'psd'},
        FileType.DOCUMENT: {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt'},
        FileType.ARCHIVE: {'zip', 'tar', 'gz', 'bz2', 'xz', '7z', 'rar'},
        FileType.MEDIA: {'mp3', 'wav', 'mp4', 'avi', 'mkv', 'flac', 'm4a'},
        FileType.CONFIG: {'conf', 'cfg', 'ini', 'toml', 'env', 'yaml', 'yml'},
    }
    
    DEFAULT_EXCLUDE_DIRS = {
        '__pycache__', '.git', '.svn', '.hg', '.idea', 
        'node_modules', 'venv', '.venv', 'env', '.env',
        'dist', 'build', '.cache', '.tox', '.mypy_cache'
    }
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.results: List[Dict] = []
        
    def search(self, options: SearchOptions) -> List[Dict]:
        self.results = []
        
        print(f"{Colors.info('🔍 开始搜索...')}")
        print(f"{Colors.DIM}搜索目录: {self.base_path}{Colors.RESET}\n")
        
        self._search_recursive(self.base_path, options, current_depth=0)
        self._print_summary(options)
        return self.results
    
    def _search_recursive(self, path: Path, options: SearchOptions, current_depth: int):
        if options.max_depth is not None and current_depth > options.max_depth:
            return
            
        try:
            for item in path.iterdir():
                if not options.include_hidden and item.name.startswith('.'):
                    continue
                    
                if item.is_dir() and item.name in self.DEFAULT_EXCLUDE_DIRS:
                    continue
                    
                if self._should_exclude(item.name, options.exclude_patterns):
                    continue
                    
                if item.is_file():
                    if self._matches_options(item, options):
                        file_info = self._get_file_info(item)
                        self.results.append(file_info)
                        
                elif item.is_dir():
                    self._search_recursive(item, options, current_depth + 1)
                    
        except PermissionError:
            print(f"{Colors.warning('⚠️  权限不足，跳过:')} {path}")
        except Exception as e:
            print(f"{Colors.error('❌ 错误:')} {e}")
    
    def _should_exclude(self, name: str, patterns: List[str]) -> bool:
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _matches_options(self, file_path: Path, options: SearchOptions) -> bool:
        if options.name_pattern:
            match_fn = fnmatch.fnmatch if not options.case_sensitive else lambda f, p: fnmatch.fnmatch(f.lower(), p.lower())
            if not match_fn(file_path.name, options.name_pattern):
                return False
        
        if options.content_pattern:
            if not self._matches_content(file_path, options.content_pattern, options.content_regex):
                return False
        
        if options.file_type != FileType.ALL:
            ext = file_path.suffix.lstrip('.').lower()
            valid_exts = self.FILE_TYPE_MAPPINGS.get(options.file_type, set())
            if ext not in valid_exts:
                return False
        
        file_size = file_path.stat().st_size
        if options.min_size and file_size < options.min_size:
            return False
        if options.max_size and file_size > options.max_size:
            return False
        
        if options.min_mtime or options.max_mtime:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if options.min_mtime and mtime < options.min_mtime:
                return False
            if options.max_mtime and mtime > options.max_mtime:
                return False
        
        return True
    
    def _matches_content(self, file_path: Path, pattern: str, use_regex: bool) -> bool:
        try:
            content = file_path.read_text(errors='ignore')
            
            if use_regex:
                flags = 0 if options.case_sensitive else re.IGNORECASE
                return bool(re.search(pattern, content, flags))
            else:
                return pattern.lower() in content.lower()
                
        except (UnicodeDecodeError, PermissionError):
            return False
    
    def _get_file_info(self, file_path: Path) -> Dict:
        stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        return {
            'path': str(file_path),
            'relative_path': str(file_path.relative_to(self.base_path)),
            'name': file_path.name,
            'extension': file_path.suffix.lstrip('.'),
            'size': stat.st_size,
            'size_human': self._format_size(stat.st_size),
            'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'mime_type': mime_type or 'unknown'
        }
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    def _print_summary(self, options: SearchOptions):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.success(f'✅ 搜索完成! 找到 {len(self.results)} 个匹配文件')}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        for i, result in enumerate(self.results[:10], 1):
            icon = self._get_file_icon(result['extension'])
            print(f"  {Colors.highlight(f'{i:3}.')} {icon} {Colors.info(result['name'])} ")
            print(f"      {Colors.DIM}📁 {result['relative_path']} | 📊 {result['size_human']}{Colors.RESET}")
        
        if len(self.results) > 10:
            print(f"\n  {Colors.warning(f'... 还有 {len(self.results) - 10} 个文件未显示')}")
        print()
    
    def _get_file_icon(self, extension: str) -> str:
        icons = {
            'py': '🐍', 'js': '📜', 'ts': '📘', 'go': '🐹',
            'rs': '🦀', 'java': '☕', 'c': '⚙️', 'cpp': '⚙️',
            'md': '📝', 'txt': '📄', 'json': '📋', 'yaml': '📋',
            'png': '🖼️', 'jpg': '🖼️', 'gif': '🖼️', 'svg': '🎨',
            'pdf': '📕', 'doc': '📘', 'docx': '📘',
            'zip': '📦', 'tar': '📦', 'gz': '📦',
            'mp3': '🎵', 'wav': '🎵', 'mp4': '🎬',
            'html': '🌐', 'css': '🎨',
        }
        return icons.get(extension.lower(), '📄')
    
    def export_results(self, output_path: str, format: str = 'json'):
        if not self.results:
            print(f"{Colors.warning('⚠️  没有结果可导出')}")
            return
            
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
                
        elif format == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"File Search Results\n")
                f.write(f"{'='*60}\n")
                f.write(f"Total files: {len(self.results)}\n\n")
                for result in self.results:
                    f.write(f"{result['name']}\n")
                    f.write(f"  Path: {result['relative_path']}\n")
                    f.write(f"  Size: {result['size_human']}\n")
                    f.write(f"  Modified: {result['mtime']}\n\n")
                    
        elif format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'path', 'size', 'mtime'])
                writer.writeheader()
                for result in self.results:
                    writer.writerow({
                        'name': result['name'],
                        'path': result['relative_path'],
                        'size': result['size_human'],
                        'mtime': result['mtime']
                    })
        
        print(f"{Colors.success(f'✅ 结果已导出到:')} {output_path}")


def parse_size(size_str: str) -> int:
    size_str = size_str.upper().strip()
    multipliers = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    
    for unit, mult in multipliers.items():
        if size_str.endswith(unit):
            return int(float(size_str[:-1]) * mult)
    return int(size_str)


def parse_date(date_str: str) -> datetime:
    formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {date_str}")


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}🕵️ 文件搜索查找器{Colors.RESET} - 快速查找文件和内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}使用示例:{Colors.RESET}
  {Colors.info('$ fsfind -n "*.py"')}           # 查找所有Python文件
  {Colors.info('$ fsfind -n "test_*"')}         # 查找test_开头的文件
  {Colors.info('$ fsfind -c "TODO" -t code')}   # 在代码中搜索TODO
  {Colors.info('$ fsfind -e "__pycache__"')}    # 排除特定目录
  {Colors.info('$ fsfind --max-size 1M')}       # 查找小于1MB的文件
  {Colors.info('$ fsfind -o results.json -f json')}  # 导出结果
        """
    )
    
    parser.add_argument('-n', '--name', type=str, help='文件名模式 (支持通配符)')
    parser.add_argument('-c', '--content', type=str, help='文件内容搜索模式')
    parser.add_argument('-r', '--regex', action='store_true', help='内容搜索使用正则表达式')
    parser.add_argument('-t', '--type', type=str, 
                        choices=['all', 'text', 'code', 'image', 'document', 'archive', 'media', 'config'],
                        default='all', help='文件类型过滤')
    
    parser.add_argument('--min-size', type=str, help='最小文件大小 (如 100K, 1M)')
    parser.add_argument('--max-size', type=str, help='最大文件大小 (如 10M, 1G)')
    parser.add_argument('--min-mtime', type=str, help='最早修改时间 (YYYY-MM-DD)')
    parser.add_argument('--max-mtime', type=str, help='最晚修改时间 (YYYY-MM-DD)')
    
    parser.add_argument('-e', '--exclude', action='append', default=[], help='排除的模式')
    parser.add_argument('--include-hidden', action='store_true', help='包含隐藏文件')
    parser.add_argument('--max-depth', type=int, help='最大搜索深度')
    
    parser.add_argument('path', nargs='?', default='.', help='搜索起始路径')
    
    parser.add_argument('-o', '--output', type=str, help='输出文件路径')
    parser.add_argument('-f', '--format', type=str, choices=['json', 'txt', 'csv'], default='json',
                        help='输出格式 (默认: json)')
    parser.add_argument('-q', '--quiet', action='store_true', help='安静模式 (只输出结果)')
    
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    
    options = SearchOptions(
        name_pattern=args.name,
        content_pattern=args.content,
        content_regex=args.regex,
        file_type=FileType(args.type),
        min_size=parse_size(args.min_size) if args.min_size else None,
        max_size=parse_size(args.max_size) if args.max_size else None,
        min_mtime=parse_date(args.min_mtime) if args.min_mtime else None,
        max_mtime=parse_date(args.max_mtime) if args.max_mtime else None,
        exclude_patterns=args.exclude,
        include_hidden=args.include_hidden,
        max_depth=args.max_depth
    )
    
    searcher = FileSearcher(args.path)
    results = searcher.search(options)
    
    if args.output and results:
        searcher.export_results(args.output, args.format)
    
    return 0 if results else 1


if __name__ == '__main__':
    exit(main())
