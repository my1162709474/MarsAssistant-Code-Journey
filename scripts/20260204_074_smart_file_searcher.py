#!/usr/bin/env python3
"""
Day 74: Smart File Searcher - 智能文件搜索工具

功能特性：
- 多维度文件搜索（名称、内容、大小）
- 正则表达式支持
- 文件类型智能识别
- 搜索结果导出
- 并行搜索加速
"""

import os
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Callable
import mimetypes


class SmartFileSearcher:
    """智能文件搜索器"""
    
    SUPPORTED_TYPES = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C/C++ Header',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.lua': 'Lua',
        '.md': 'Markdown',
        '.txt': 'Text',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.xml': 'XML',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sql': 'SQL',
        '.sh': 'Shell',
        '.bash': 'Bash',
        '.zsh': 'Zsh',
        '.ps1': 'PowerShell',
        '.vue': 'Vue',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.dockerfile': 'Dockerfile',
        '.gitignore': 'Git Ignore',
        '.env': 'Environment',
        '.csv': 'CSV',
        '.png': 'Image',
        '.jpg': 'Image',
        '.jpeg': 'Image',
        '.gif': 'Image',
        '.svg': 'SVG',
        '.pdf': 'PDF',
        '.zip': 'Archive',
        '.tar': 'Archive',
        '.gz': 'Archive',
        '.7z': 'Archive',
    }
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.results: List[Dict] = []
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'matched_files': 0,
            'search_time': 0,
            'file_types': {},
        }
    
    def search_by_name(
        self,
        pattern: str,
        use_regex: bool = False,
        case_sensitive: bool = False
    ) -> List[Dict]:
        """按文件名搜索"""
        start_time = time.time()
        self.results = []
        
        if use_regex:
            regex = re.compile(pattern, 0 if case_sensitive else re.IGNORECASE)
            matcher = lambda name: bool(regex.search(name))
        else:
            matcher = lambda name: (pattern in name) if not case_sensitive else (pattern in name)
        
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                if matcher(file):
                    self.results.append(self._file_info(file_path))
        
        self.stats['search_time'] = time.time() - start_time
        return self.results
    
    def search_by_content(
        self,
        pattern: str,
        file_types: Optional[List[str]] = None,
        use_regex: bool = False,
        case_sensitive: bool = False
    ) -> List[Dict]:
        """按文件内容搜索"""
        start_time = time.time()
        self.results = []
        
        if use_regex:
            regex = re.compile(pattern, 0 if case_sensitive else re.IGNORECASE)
            matcher = lambda content: regex.search(content)
        else:
            matcher = lambda content: (pattern in content) if not case_sensitive else (pattern in content)
        
        def search_file(file_path: Path) -> Optional[Dict]:
            if file_types and file_path.suffix.lower() not in file_types:
                return None
            try:
                if file_path.stat().st_size > 10 * 1024 * 1024:  # 跳过 >10MB 文件
                    return None
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if matcher(content):
                    line_nums = [i+1 for i, line in enumerate(content.split('\n')) if matcher(line)]
                    return self._file_info(file_path, content=content[:500], line_numbers=line_nums)
            except (UnicodeDecodeError, PermissionError, OSError):
                pass
            return None
        
        all_files = list(self.root_dir.rglob('*')) if self.root_dir.exists() else []
        self.stats['total_files'] = len([f for f in all_files if f.is_file()])
        
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            futures = {executor.submit(search_file, f): f for f in all_files if f.is_file()}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.results.append(result)
        
        self.stats['search_time'] = time.time() - start_time
        return self.results
    
    def search_by_size(
        self,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        unit: str = 'KB'
    ) -> List[Dict]:
        """按文件大小搜索"""
        start_time = time.time()
        self.results = []
        
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        min_bytes = min_size * units.get(unit, 1) if min_size else None
        max_bytes = max_size * units.get(unit, 1) if max_size else None
        
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                try:
                    size = file_path.stat().st_size
                    if (min_bytes is None or size >= min_bytes) and (max_bytes is None or size <= max_bytes):
                        self.results.append(self._file_info(file_path))
                except (PermissionError, OSError):
                    continue
        
        self.stats['search_time'] = time.time() - start_time
        return self.results
    
    def _file_info(self, file_path: Path, content: str = None, line_numbers: List[int] = None) -> Dict:
        """获取文件信息"""
        try:
            stat = file_path.stat()
            file_type = self._get_file_type(file_path)
            self.stats['file_types'][file_type] = self.stats['file_types'].get(file_type, 0) + 1
            return {
                'path': str(file_path.relative_to(self.root_dir.parent)),
                'name': file_path.name,
                'size': stat.st_size,
                'size_human': self._human_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'type': file_type,
                'extension': file_path.suffix.lower(),
                'lines': len(content.split('\n')) if content else None,
                'matched_lines': line_numbers[:10] if line_numbers else None,
                'snippet': content[:200] if content else None,
            }
        except Exception:
            return {
                'path': str(file_path),
                'name': file_path.name,
                'error': 'Unable to read file info'
            }
    
    def _get_file_type(self, file_path: Path) -> str:
        """识别文件类型"""
        suffix = file_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        if suffix in self.SUPPORTED_TYPES:
            return self.SUPPORTED_TYPES[suffix]
        if mime_type:
            return mime_type.split('/')[0].title()
        return 'Unknown'
    
    def _human_size(self, size: int) -> str:
        """人性化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def export_results(self, output_path: str = "search_results.json", format: str = "json"):
        """导出搜索结果"""
        output = {
            'search_time': datetime.now().isoformat(),
            'stats': self.stats,
            'results': self.results,
            'total_matches': len(self.results)
        }
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
        elif format == 'csv':
            import csv
            if self.results:
                with open(output_path.replace('.json', '.csv'), 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)
        elif format == 'txt':
            with open(output_path.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
                f.write(f"搜索结果 ({len(self.results)} 个匹配)\n")
                f.write("=" * 60 + "\n\n")
                for i, result in enumerate(self.results, 1):
                    f.write(f"{i}. {result['name']}\n")
                    f.write(f"   路径: {result['path']}\n")
                    f.write(f"   大小: {result['size_human']}\n")
                    f.write(f"   类型: {result['type']}\n")
                    f.write(f"   修改: {result['modified']}\n")
                    if result.get('snippet'):
                        f.write(f"   内容: {result['snippet'][:100]}...\n")
                    f.write("\n")
        
        return output_path
    
    def print_stats(self):
        """打印搜索统计"""
        print(f"\n📊 搜索统计")
        print(f"  总文件数: {self.stats['total_files']}")
        print(f"  匹配文件: {self.stats['matched_files']}")
        print(f"  搜索时间: {self.stats['search_time']:.3f}s")
        if self.stats['file_types']:
            print(f"\n📁 文件类型分布:")
            for file_type, count in sorted(self.stats['file_types'].items(), key=lambda x: -x[1])[:5]:
                print(f"    {file_type}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Smart File Searcher - 智能文件搜索工具")
    parser.add_argument('path', nargs='?', default='.', help='搜索路径')
    parser.add_argument('--name', '-n', help='按文件名搜索')
    parser.add_argument('--content', '-c', help='按文件内容搜索')
    parser.add_argument('--type', '-t', help='文件类型过滤器 (如 .py, .js)')
    parser.add_argument('--min-size', '-s', type=float, help='最小文件大小')
    parser.add_argument('--max-size', '-S', type=float, help='最大文件大小')
    parser.add_argument('--unit', choices=['B', 'KB', 'MB', 'GB'], default='KB', help='大小单位')
    parser.add_argument('--regex', '-r', action='store_true', help='使用正则表达式')
    parser.add_argument('--case', '-i', action='store_true', help='大小写敏感')
    parser.add_argument('--export', '-e', choices=['json', 'csv', 'txt'], default='json', help='导出格式')
    parser.add_argument('--output', '-o', default='search_results', help='输出文件名')
    
    args = parser.parse_args()
    
    searcher = SmartFileSearcher(args.path)
    
    if args.name:
        results = searcher.search_by_name(args.name, args.regex, args.case)
    elif args.content:
        file_types = [args.type.lower()] if args.type else None
        results = searcher.search_by_content(args.content, file_types, args.regex, args.case)
    elif args.min_size or args.max_size:
        results = searcher.search_by_size(args.min_size, args.max_size, args.unit)
    else:
        parser.print_help()
        return
    
    searcher.stats['matched_files'] = len(results)
    
    print(f"\n🔍 找到 {len(results)} 个匹配文件:\n")
    for i, result in enumerate(results[:20], 1):
        print(f"  {i:3}. {result['name']:<40} {result['size_human']:>10} [{result['type']}]")
    
    if len(results) > 20:
        print(f"\n  ... 还有 {len(results) - 20} 个文件未显示")
    
    output_path = f"{args.output}.{args.export}"
    searcher.export_results(output_path, args.export)
    print(f"\n💾 结果已导出至: {output_path}")


if __name__ == '__main__':
    main()
