#!/usr/bin/env python3
"""
文件搜索器 - File Finder
在指定目录中搜索文件和文件夹，支持多种搜索模式

功能:
- 按文件名模式搜索 (支持通配符)
- 按文件大小范围搜索
- 按修改时间范围搜索
- 按文件类型搜索
- 排除特定目录
- 正则表达式支持
"""

import os
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Callable


class FileFinder:
    """文件搜索器类"""
    
    def __init__(self, root_dir: str = ".", max_depth: int = None):
        self.root_dir = Path(root_dir)
        self.max_depth = max_depth
        self.results: List[Path] = []
        
    def search_by_name(self, pattern: str, use_regex: bool = False) -> List[Path]:
        """按文件名模式搜索"""
        self.results = []
        
        if use_regex:
            regex = re.compile(pattern)
            matcher = lambda name: regex.search(name) is not None
        else:
            matcher = lambda name: pattern.lower() in name.lower()
        
        for path in self._walk_directory():
            if matcher(path.name):
                self.results.append(path)
        
        return self.results
    
    def search_by_type(self, file_type: str) -> List[Path]:
        """按文件类型搜索 (扩展名)"""
        self.results = []
        ext = file_type.lower().strip('.')
        
        for path in self._walk_directory():
            if path.is_file() and path.suffix.lower() == f'.{ext}':
                self.results.append(path)
        
        return self.results
    
    def search_by_size(self, min_size: int = 0, max_size: int = None) -> List[Path]:
        """按文件大小范围搜索 (字节)"""
        self.results = []
        
        for path in self._walk_directory():
            if path.is_file():
                size = path.stat().st_size
                if size >= min_size and (max_size is None or size <= max_size):
                    self.results.append(path)
        
        return self.results
    
    def search_by_date(self, days_ago: int = None, within_days: int = None) -> List[Path]:
        """按修改时间搜索"""
        self.results = []
        now = datetime.now()
        
        if days_ago is not None:
            target_date = now - timedelta(days=days_ago)
            filter_func = lambda mtime: mtime >= target_date
        elif within_days is not None:
            start_date = now - timedelta(days=within_days)
            filter_func = lambda mtime: mtime >= start_date
        else:
            filter_func = lambda mtime: True
        
        for path in self._walk_directory():
            if path.is_file():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if filter_func(mtime):
                    self.results.append(path)
        
        return self.results
    
    def search_by_content(self, pattern: str, file_types: List[str] = None) -> List[Path]:
        """在文件内容中搜索模式"""
        self.results = []
        regex = re.compile(pattern)
        
        for path in self._walk_directory():
            if path.is_file():
                # 检查文件类型
                if file_types and path.suffix.lower() not in [f'.{ext}' for ext in file_types]:
                    continue
                
                # 读取并搜索内容
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if regex.search(content):
                            self.results.append(path)
                except Exception:
                    continue
        
        return self.results
    
    def _walk_directory(self) -> Path:
        """遍历目录"""
        if not self.root_dir.exists():
            return []
        
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            
            # 计算当前深度
            if self.max_depth is not None:
                depth = len(root_path.relative_to(self.root_dir).parts)
                if depth >= self.max_depth:
                    dirs.clear()
                    continue
            
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # 遍历文件
            for file in files:
                if not file.startswith('.'):
                    yield root_path / file
    
    def print_results(self, show_details: bool = False):
        """打印搜索结果"""
        if not self.results:
            print("未找到匹配的文件")
            return
        
        print(f"\n找到 {len(self.results)} 个文件:\n")
        for path in self.results:
            if show_details:
                stat = path.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{size:>10} {mtime}  {path}")
            else:
                print(f"  {path}")
        print()


def demo():
    """演示文件搜索器的使用"""
    print("=" * 60)
    print("           文件搜索器 - File Finder 演示")
    print("=" * 60)
    
    finder = FileFinder(".", max_depth=3)
    
    # 示例1: 搜索Python文件
    print("\n[示例1] 搜索所有Python文件:")
    results = finder.search_by_type("py")
    finder.print_results()
    
    # 示例2: 搜索包含"test"的文件
    print("\n[示例2] 搜索包含'test'的文件名:")
    results = finder.search_by_name("test")
    finder.print_results()
    
    # 示例3: 搜索大文件 (>10KB)
    print("\n[示例3] 搜索大于10KB的文件:")
    results = finder.search_by_size(min_size=10 * 1024)
    finder.print_results(show_details=True)
    
    # 示例4: 搜索最近7天修改的文件
    print("\n[示例4] 搜索最近7天修改的文件:")
    results = finder.search_by_date(days_ago=7)
    finder.print_results()
    
    print("\n" + "=" * 60)


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description="文件搜索器 - 在目录中搜索文件和文件夹",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -n "*.py"                    # 搜索Python文件
  %(prog)s -n "test"                    # 搜索包含test的文件
  %(prog)s -t py                        # 按类型搜索.py文件
  %(prog)s -s 1024                      # 搜索大于1KB的文件
  %(prog)s -d 7                         # 搜索最近7天修改的文件
  %(prog)s -c "def main" -e py          # 在Python文件中搜索内容
        """
    )
    
    parser.add_argument('path', nargs='?', default='.', help='搜索路径')
    parser.add_argument('-n', '--name', help='文件名模式 (支持通配符)')
    parser.add_argument('-r', '--regex', action='store_true', help='使用正则表达式匹配文件名')
    parser.add_argument('-t', '--type', help='按文件类型搜索 (扩展名)')
    parser.add_argument('-s', '--size', type=int, nargs='+', 
                       metavar=('MIN', 'MAX'), help='按大小范围搜索 (字节)')
    parser.add_argument('-d', '--days', type=int, help='搜索最近N天修改的文件')
    parser.add_argument('-c', '--content', help='在文件内容中搜索')
    parser.add_argument('-e', '--ext', nargs='+', help='内容搜索时限制的文件类型')
    parser.add_argument('--max-depth', type=int, default=3, help='最大搜索深度 (默认3)')
    parser.add_argument('--details', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 创建搜索器
    finder = FileFinder(args.path, max_depth=args.max_depth)
    
    # 执行搜索
    results = None
    
    if args.name:
        results = finder.search_by_name(args.name, use_regex=args.regex)
    elif args.type:
        results = finder.search_by_type(args.type)
    elif args.size:
        min_size = args.size[0]
        max_size = args.size[1] if len(args.size) > 1 else None
        results = finder.search_by_size(min_size, max_size)
    elif args.days:
        results = finder.search_by_date(days_ago=args.days)
    elif args.content:
        results = finder.search_by_content(args.content, args.ext)
    else:
        # 默认演示模式
        demo()
        return
    
    # 打印结果
    if results is not None:
        finder.print_results(show_details=args.details)


if __name__ == "__main__":
    main()
