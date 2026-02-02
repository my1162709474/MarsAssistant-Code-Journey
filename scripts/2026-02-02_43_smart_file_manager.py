#!/usr/bin/env python3
"""
智能文件管理器 - Smart File Manager
=====================================
一个功能强大的命令行文件管理工具，支持文件操作、批量重命名、
搜索查找、属性修改等功能。

功能特性:
- 📁 文件/目录基本操作 (复制/移动/删除/重命名)
- 🔍 高级文件搜索 (按名称/大小/时间/类型)
- 📊 批量重命名工具 (序号/日期/正则)
- 🏷️ 文件属性管理 (权限/时间戳)
- 📈 磁盘使用分析
- 🗜️ 压缩/解压支持
- 🔗 软链接管理

作者: MarsAssistant
日期: 2026-02-02
"""

import os
import sys
import shutil
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Callable
import hashlib


class Colors:
    """终端颜色代码"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    @classmethod
    def disable(cls):
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.PURPLE = cls.CYAN = cls.WHITE = ''
        cls.BOLD = cls.UNDERLINE = cls.RESET = ''


class FileManager:
    """智能文件管理器核心类"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.operations_count = 0
        self.errors = []
    
    def log(self, message: str, color: str = Colors.GREEN):
        """打印带颜色的日志信息"""
        if self.verbose:
            print(f"{color}[✓]{Colors.RESET} {message}")
    
    def error(self, message: str):
        """记录错误"""
        self.errors.append(message)
        print(f"{Colors.RED}[✗]{Colors.RESET} {message}")
    
    # ========== 基础文件操作 ==========
    
    def copy(self, src: str, dst: str, recursive: bool = True) -> bool:
        """复制文件或目录"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                self.error(f"源文件不存在: {src}")
                return False
            
            if src_path.is_dir() and recursive:
                shutil.copytree(src_path, dst_path)
                self.log(f"目录已复制: {src} → {dst}", Colors.CYAN)
            else:
                shutil.copy2(src_path, dst_path)
                self.log(f"文件已复制: {src} → {dst}")
            
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"复制失败 ({src} → {dst}): {e}")
            return False
    
    def move(self, src: str, dst: str) -> bool:
        """移动/重命名文件或目录"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                self.error(f"源文件不存在: {src}")
                return False
            
            shutil.move(str(src_path), str(dst_path))
            self.log(f"已移动: {src} → {dst}", Colors.CYAN)
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"移动失败 ({src} → {dst}): {e}")
            return False
    
    def delete(self, path: str, force: bool = False, recursive: bool = True) -> bool:
        """删除文件或目录"""
        try:
            target = Path(path)
            
            if not target.exists():
                self.error(f"文件不存在: {path}")
                return False
            
            if target.is_dir():
                if recursive:
                    shutil.rmtree(target)
                elif not force:
                    self.error(f"是目录，请使用 -r 选项: {path}")
                    return False
            else:
                target.unlink()
            
            self.log(f"已删除: {path}", Colors.YELLOW)
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"删除失败: {path} - {e}")
            return False
    
    def mkdir(self, path: str, parents: bool = True, exist_ok: bool = True) -> bool:
        """创建目录"""
        try:
            p = Path(path)
            if parents:
                p.mkdir(parents=True, exist_ok=exist_ok)
            else:
                p.mkdir(exist_ok=exist_ok)
            self.log(f"目录已创建: {path}", Colors.CYAN)
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"创建目录失败: {path} - {e}")
            return False
    
    # ========== 文件搜索 ==========
    
    def search_files(
        self,
        directory: str,
        pattern: Optional[str] = None,
        file_type: Optional[str] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        modified_after: Optional[datetime] = None,
        modified_before: Optional[datetime] = None,
        content_pattern: Optional[str] = None,
        recursive: bool = True
    ) -> List[Path]:
        """高级文件搜索"""
        directory = Path(directory)
        results = []
        
        if not directory.exists():
            self.error(f"搜索目录不存在: {directory}")
            return results
        
        def matches_criteria(filepath: Path) -> bool:
            # 名称匹配
            if pattern:
                if not re.search(pattern, filepath.name, re.IGNORECASE):
                    return False
            
            # 文件类型过滤
            if file_type:
                if file_type == 'dir' and not filepath.is_dir():
                    return False
                elif file_type == 'file' and not filepath.is_file():
                    return False
            
            # 大小过滤
            if filepath.is_file():
                size = filepath.stat().st_size
                if min_size and size < min_size:
                    return False
                if max_size and size > max_size:
                    return False
            
            # 时间过滤
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            if modified_after and mtime < modified_after:
                return False
            if modified_before and mtime > modified_before:
                return False
            
            # 内容搜索
            if content_pattern and filepath.is_file():
                try:
                    content = filepath.read_text(errors='ignore')
                    if not re.search(content_pattern, content):
                        return False
                except Exception:
                    return False
            
            return True
        
        # 执行搜索
        if recursive:
            iterator = directory.rglob("*")
        else:
            iterator = directory.glob("*")
        
        for item in iterator:
            if matches_criteria(item):
                results.append(item)
        
        self.log(f"搜索完成: 找到 {len(results)} 个匹配项", Colors.PURPLE)
        return results
    
    def find_duplicates(self, directory: str, by_content: bool = True) -> dict:
        """查找重复文件"""
        directory = Path(directory)
        duplicates = {}
        
        for filepath in directory.rglob("*"):
            if not filepath.is_file():
                continue
            
            if by_content:
                # 按内容哈希
                hasher = hashlib.md5()
                try:
                    with open(filepath, 'rb') as f:
                        hasher.update(f.read())
                    key = hasher.hexdigest()
                except Exception:
                    continue
            else:
                # 按大小和名称
                size = filepath.stat().st_size
                key = f"{size}_{filepath.name}"
            
            if key not in duplicates:
                duplicates[key] = []
            duplicates[key].append(filepath)
        
        # 只返回有重复的组
        return {k: v for k, v in duplicates.items() if len(v) > 1}
    
    # ========== 批量重命名 ==========
    
    def batch_rename(
        self,
        directory: str,
        pattern: str,
        replacement: str,
        use_regex: bool = True,
        start_num: int = 1,
        padding: int = 3,
        dry_run: bool = True
    ) -> bool:
        """批量重命名文件"""
        directory = Path(directory)
        files = sorted([f for f in directory.iterdir() if f.is_file()])
        
        if not files:
            self.error("目录中没有文件")
            return False
        
        compiled_pattern = re.compile(pattern) if use_regex else None
        
        operations = []
        for i, filepath in enumerate(files):
            if use_regex:
                match = compiled_pattern.search(filepath.name)
                if match:
                    new_name = compiled_pattern.sub(replacement, filepath.name)
                else:
                    continue
            else:
                new_name = filepath.name.replace(pattern, replacement)
            
            # 添加序号
            if '{num}' in new_name:
                new_name = new_name.format(num=str(i + start_num).zfill(padding))
            
            if new_name != filepath.name:
                operations.append((filepath, new_name))
                if not dry_run:
                    new_path = filepath.parent / new_name
                    filepath.rename(new_path)
        
        # 显示操作预览
        print(f"\n{Colors.CYAN}=== 重命名预览 ({len(operations)} 个文件) ==={Colors.RESET}")
        for old, new in operations:
            print(f"  {old.name} → {new}")
        
        if dry_run:
            print(f"\n{Colors.YELLOW}这是预览模式，使用 --apply 应用更改{Colors.RESET}")
            return True
        else:
            self.log(f"已完成 {len(operations)} 个重命名操作", Colors.GREEN)
            self.operations_count += len(operations)
            return True
    
    # ========== 文件属性管理 ==========
    
    def chmod(self, path: str, mode: str, recursive: bool = False) -> bool:
        """修改文件权限"""
        try:
            p = Path(path)
            
            if recursive and p.is_dir():
                for item in p.rglob("*"):
                    item.chmod(int(mode, 8))
                self.log(f"递归修改权限: {path} → {mode}", Colors.CYAN)
            else:
                p.chmod(int(mode, 8))
                self.log(f"修改权限: {path} → {mode}")
            
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"修改权限失败: {path} - {e}")
            return False
    
    def set_timestamp(
        self,
        path: str,
        created: Optional[datetime] = None,
        modified: Optional[datetime] = None
    ) -> bool:
        """设置文件时间戳"""
        try:
            import time
            
            p = Path(path)
            if not p.exists():
                self.error(f"文件不存在: {path}")
                return False
            
            # 设置修改时间
            if modified:
                times = (modified.timestamp(), modified.timestamp())
                os.utime(p, times)
            
            # 注意: 创建时间在大多数文件系统上不可更改
            if created:
                self.log(f"注意: 创建时间无法在当前文件系统上修改", Colors.YELLOW)
            
            self.log(f"时间戳已更新: {path}")
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"设置时间戳失败: {path} - {e}")
            return False
    
    # ========== 磁盘分析 ==========
    
    def disk_usage(self, path: str, human_readable: bool = True) -> dict:
        """分析磁盘使用情况"""
        p = Path(path)
        
        if not p.exists():
            self.error(f"路径不存在: {path}")
            return {}
        
        total = 0
        by_type = {}
        by_dir = {}
        
        for item in p.rglob("*"):
            try:
                if item.is_file():
                    size = item.stat().st_size
                    total += size
                    
                    # 按类型分组
                    ext = item.suffix.lower()
                    if ext:
                        by_type[ext] = by_type.get(ext, 0) + size
                    
                    # 按父目录分组
                    parent = str(item.parent)
                    by_dir[parent] = by_dir.get(parent, 0) + size
            except Exception:
                continue
        
        def format_size(size: int) -> str:
            if not human_readable:
                return str(size)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} PB"
        
        # 排序
        by_type = dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True))
        by_dir = dict(sorted(by_dir.items(), key=lambda x: x[1], reverse=True))
        
        return {
            'total': format_size(total),
            'total_bytes': total,
            'by_type': {k: format_size(v) for k, v in list(by_type.items())[:10]},
            'by_dir': {k: format_size(v) for k, v in list(by_dir.items())[:10]}
        }
    
    def find_large_files(self, path: str, min_size_mb: float = 10) -> List[tuple]:
        """查找大文件"""
        min_bytes = int(min_size_mb * 1024 * 1024)
        large_files = []
        
        for item in Path(path).rglob("*"):
            if item.is_file():
                try:
                    size = item.stat().st_size
                    if size >= min_bytes:
                        large_files.append((str(item), size))
                except Exception:
                    continue
        
        # 按大小排序
        large_files.sort(key=lambda x: x[1], reverse=True)
        return large_files
    
    # ========== 压缩/解压 ==========
    
    def compress(self, source: str, output: str, format: str = 'zip') -> bool:
        """压缩文件或目录"""
        try:
            source_path = Path(source)
            
            if format == 'zip':
                shutil.make_archive(
                    str(output).replace('.zip', ''),
                    'zip',
                    source_path
                )
                self.log(f"已压缩: {source} → {output}.zip", Colors.CYAN)
            elif format == 'tar':
                shutil.make_archive(
                    str(output).replace('.tar.gz', '').replace('.tar', ''),
                    'tar',
                    source_path
                )
                self.log(f"已压缩: {source} → {output}.tar", Colors.CYAN)
            else:
                self.error(f"不支持的格式: {format}")
                return False
            
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"压缩失败: {source} - {e}")
            return False
    
    def decompress(self, archive: str, output: Optional[str] = None) -> bool:
        """解压文件"""
        try:
            archive_path = Path(archive)
            
            if not archive_path.exists():
                self.error(f"压缩文件不存在: {archive}")
                return False
            
            if output is None:
                output = archive_path.parent
            
            if archive.endswith('.zip'):
                shutil.unpack_archive(archive, output, 'zip')
            elif archive.endswith(('.tar.gz', '.tgz')):
                shutil.unpack_archive(archive, output, 'gztar')
            elif archive.endswith('.tar'):
                shutil.unpack_archive(archive, output, 'tar')
            else:
                self.error(f"不支持的格式: {archive}")
                return False
            
            self.log(f"已解压: {archive} → {output}", Colors.CYAN)
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"解压失败: {archive} - {e}")
            return False
    
    # ========== 符号链接管理 ==========
    
    def create_symlink(self, target: str, link: str, force: bool = False) -> bool:
        """创建符号链接"""
        try:
            target_path = Path(target)
            link_path = Path(link)
            
            if link_path.exists() or link_path.is_symlink():
                if force:
                    if link_path.is_symlink():
                        link_path.unlink()
                    else:
                        self.error(f"目标已存在且不是符号链接: {link}")
                        return False
                else:
                    self.error(f"符号链接已存在: {link}")
                    return False
            
            link_path.symlink_to(target_path)
            self.log(f"已创建符号链接: {link} → {target}", Colors.CYAN)
            self.operations_count += 1
            return True
        except Exception as e:
            self.error(f"创建符号链接失败: {link} - {e}")
            return False
    
    def find_broken_symlinks(self, directory: str) -> List[str]:
        """查找损坏的符号链接"""
        broken = []
        
        for item in Path(directory).rglob("*"):
            if item.is_symlink():
                try:
                    if not item.resolve().exists():
                        broken.append(str(item))
                except Exception:
                    broken.append(str(item))
        
        return broken


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="智能文件管理器 - Smart File Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s copy file.txt backup/
  %(prog)s move old_name.txt new_name.txt
  %(prog)s delete file.txt
  %(prog)s search "*.py" --dir /project
  %(prog)s rename "*.txt" "*.md" --apply
  %(prog)s du /project
  %(prog)s large 100 --dir /project
  %(prog)s compress project/ output
  %(prog)s extract archive.zip
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 通用参数
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归操作')
    
    # copy 命令
    copy_parser = subparsers.add_parser('copy', help='复制文件或目录')
    copy_parser.add_argument('source', help='源路径')
    copy_parser.add_argument('destination', help='目标路径')
    
    # move 命令
    subparsers.add_parser('move', help='移动/重命名文件或目录').add_argument('source')
    subparsers.add_parser('destination', help='目标路径')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除文件或目录')
    delete_parser.add_argument('path', help='文件或目录路径')
    delete_parser.add_argument('-f', '--force', action='store_true', help='强制删除')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索文件')
    search_parser.add_argument('pattern', help='搜索模式')
    search_parser.add_argument('--dir', default='.', help='搜索目录')
    search_parser.add_argument('--type', choices=['file', 'dir'], help='文件类型')
    search_parser.add_argument('--min-size', type=int, help='最小大小(bytes)')
    search_parser.add_argument('--max-size', type=int, help='最大大小(bytes)')
    
    # rename 命令
    rename_parser = subparsers.add_parser('rename', help='批量重命名')
    rename_parser.add_argument('pattern', help='匹配模式')
    rename_parser.add_argument('replacement', help='替换内容')
    rename_parser.add_argument('--dir', default='.', help='操作目录')
    rename_parser.add_argument('--apply', action='store_true', help='应用更改')
    rename_parser.add_argument('--no-regex', action='store_true', help='不使用正则')
    
    # chmod 命令
    chmod_parser = subparsers.add_parser('chmod', help='修改权限')
    chmod_parser.add_argument('mode', help='权限模式(如 755)')
    chmod_parser.add_argument('path', help='文件路径')
    
    # du 命令
    du_parser = subparsers.add_parser('du', help='磁盘使用分析')
    du_parser.add_argument('path', nargs='?', default='.', help='分析路径')
    du_parser.add_argument('--json', action='store_true', help='JSON输出')
    
    # large 命令
    large_parser = subparsers.add_parser('large', help='查找大文件')
    large_parser.add_argument('size', type=float, help='最小大小(MB)')
    large_parser.add_argument('--dir', default='.', help='搜索目录')
    
    # compress 命令
    compress_parser = subparsers.add_parser('compress', help='压缩文件')
    compress_parser.add_argument('source', help='源路径')
    compress_parser.add_argument('output', help='输出文件名')
    compress_parser.add_argument('--format', default='zip', choices=['zip', 'tar'])
    
    # extract 命令
    subparsers.add_parser('extract', help='解压文件').add_argument('archive')
    
    args = parser.parse_args()
    
    # 初始化管理器
    manager = FileManager(verbose=args.verbose)
    
    # 执行命令
    if args.command == 'copy':
        manager.copy(args.source, args.destination, args.recursive)
    
    elif args.command == 'move':
        manager.move(args.source, args.destination)
    
    elif args.command == 'delete':
        manager.delete(args.path, args.force, args.recursive)
    
    elif args.command == 'search':
        results = manager.search_files(
            args.dir,
            args.pattern,
            args.type,
            args.min_size,
            args.max_size
        )
        for r in results:
            print(f"  {r}")
    
    elif args.command == 'rename':
        manager.batch_rename(
            args.dir,
            args.pattern,
            args.replacement,
            not args.no_regex,
            apply=args.apply
        )
    
    elif args.command == 'chmod':
        manager.chmod(args.path, args.mode, args.recursive)
    
    elif args.command == 'du':
        usage = manager.disk_usage(args.path)
        if args.json:
            import json
            print(json.dumps(usage, indent=2, ensure_ascii=False))
        else:
            print(f"\n{Colors.CYAN}=== 磁盘使用分析 ==={Colors.RESET}")
            print(f"总大小: {usage.get('total', 'N/A')}")
            print(f"\n按类型分布:")
            for ext, size in usage.get('by_type', {}).items():
                print(f"  {ext:10} {size}")
            print(f"\n按目录分布:")
            for dir_path, size in usage.get('by_dir', {}).items():
                print(f"  {dir_path:50} {size}")
    
    elif args.command == 'large':
        large = manager.find_large_files(args.dir, args.size)
        print(f"\n{Colors.YELLOW}大于 {args.size} MB 的大文件:{Colors        for path, size in large.RESET}")
:
            size_mb = size / (1024 * 1024)
            print(f"  {size_mb:8.2f} MB  {path}")
    
    elif args.command == 'compress':
        manager.compress(args.source, args.output, args.format)
    
    elif args.command == 'extract':
        manager.decompress(args.archive)
    
    else:
        parser.print_help()
    
    # 打印统计
    if manager.operations_count > 0:
        print(f"\n{Colors.GREEN}完成: {manager.operations_count} 个操作{Colors.RESET}")
    
    if manager.errors:
        print(f"{Colors.RED}错误: {len(manager.errors)} 个错误{Colors.RESET}")


if __name__ == '__main__':
    main()
