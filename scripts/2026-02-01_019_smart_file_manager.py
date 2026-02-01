#!/usr/bin/env python3
"""
智能文件管理器 - Day 19
功能：
- 文件搜索（按名称、内容、大小）
- 文件分类（按类型、大小、日期）
- 批量操作（移动、复制、重命名）
- 文件去重（基于内容hash）
- 磁盘使用分析
"""

import os
import hashlib
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json


class FileType(Enum):
    """文件类型枚举"""
    IMAGE = "image"
    DOCUMENT = "document"
    CODE = "code"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    TEXT = "text"
    OTHER = "other"


@dataclass
class FileInfo:
    """文件信息类"""
    path: str
    name: str
    size: int
    created_time: datetime
    modified_time: datetime
    extension: str
    file_type: FileType
    
    @property
    def size_formatted(self) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024:
                return f"{self.size:.2f} {unit}"
            self.size /= 1024
        return f"{self.size:.2f} TB"


class SmartFileManager:
    """智能文件管理器"""
    
    # 文件类型映射
    TYPE_MAPPING = {
        # 图片
        **{ext: FileType.IMAGE for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']},
        # 文档
        **{ext: FileType.DOCUMENT for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']},
        # 代码
        **{ext: FileType.CODE for ext in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs', '.php']},
        # 视频
        **{ext: FileType.VIDEO for ext in ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']},
        # 音频
        **{ext: FileType.AUDIO for ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']},
        # 压缩包
        **{ext: FileType.ARCHIVE for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']},
        # 文本
        **{ext: FileType.TEXT for ext in ['.txt', '.md', '.json', '.yaml', '.yml', '.xml', '.html', '.css']},
    }
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.file_tree: Dict[str, FileInfo] = {}
    
    def get_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """获取文件信息"""
        try:
            stat = file_path.stat()
            extension = file_path.suffix.lower()
            
            file_type = self.TYPE_MAPPING.get(extension, FileType.OTHER)
            
            return FileInfo(
                path=str(file_path),
                name=file_path.name,
                size=stat.st_size,
                created_time=datetime.fromtimestamp(stat.st_ctime),
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                extension=extension,
                file_type=file_type
            )
        except (OSError, PermissionError):
            return None
    
    def scan_directory(self, path: Optional[str] = None, recursive: bool = True) -> List[FileInfo]:
        """扫描目录"""
        scan_path = self.base_path if path is None else Path(path)
        files = []
        
        iterator = scan_path.rglob("*") if recursive else scan_path.glob("*")
        
        for item in iterator:
            if item.is_file():
                file_info = self.get_file_info(item)
                if file_info:
                    files.append(file_info)
                    self.file_tree[file_info.path] = file_info
        
        return files
    
    def search_by_name(self, pattern: str, files: Optional[List[FileInfo]] = None) -> List[FileInfo]:
        """按名称搜索文件"""
        regex = re.compile(pattern, re.IGNORECASE)
        search_files = files if files is not None else list(self.file_tree.values())
        return [f for f in search_files if regex.search(f.name)]
    
    def search_by_content(self, pattern: str, file_types: Optional[List[FileType]] = None) -> Dict[str, List[int]]:
        """在文件中搜索内容"""
        results = {}
        
        for file_info in self.file_tree.values():
            if file_types and file_info.file_type not in file_types:
                continue
            
            try:
                with open(file_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    matches = []
                    for i, line in enumerate(lines, 1):
                        if pattern in line:
                            matches.append(i)
                    if matches:
                        results[file_info.path] = matches
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
        
        return results
    
    def search_by_size(self, min_size: int = 0, max_size: Optional[int] = None) -> List[FileInfo]:
        """按大小搜索文件（字节）"""
        files = list(self.file_tree.values())
        return [f for f in files if min_size <= f.size and (max_size is None or f.size <= max_size)]
    
    def search_by_date(self, after: Optional[datetime] = None, before: Optional[datetime] = None) -> List[FileInfo]:
        """按日期搜索文件"""
        files = list(self.file_tree.values())
        
        if after:
            files = [f for f in files if f.modified_time >= after]
        if before:
            files = [f for f in files if f.modified_time <= before]
        
        return files
    
    def categorize_files(self, files: Optional[List[FileInfo]] = None) -> Dict[FileType, List[FileInfo]]:
        """按类型分类文件"""
        search_files = files if files is not None else list(self.file_tree.values())
        categorized = {ft: [] for ft in FileType}
        
        for file_info in search_files:
            categorized[file_info.file_type].append(file_info)
        
        # 移除空类别
        return {k: v for k, v in categorized.items() if v}
    
    def analyze_disk_usage(self, path: Optional[str] = None) -> Dict:
        """分析磁盘使用情况"""
        scan_path = self.base_path if path is None else Path(path)
        
        usage = {}
        
        for item in scan_path.rglob("*"):
            if item.is_dir():
                total_size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                usage[str(item)] = total_size
        
        # 按大小排序
        sorted_usage = dict(sorted(usage.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_usage
    
    def calculate_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """计算文件hash"""
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def find_duplicates(self) -> Dict[str, List[str]]:
        """查找重复文件（基于内容hash）"""
        hash_to_files = {}
        
        for file_info in self.file_tree.values():
            file_hash = self.calculate_file_hash(file_info.path)
            if file_hash not in hash_to_files:
                hash_to_files[file_hash] = []
            hash_to_files[file_hash].append(file_info.path)
        
        # 只返回有重复的
        return {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}
    
    def batch_rename(self, files: List[str], name_pattern: Callable[[str, int], str], start: int = 1):
        """批量重命名文件
        
        Args:
            files: 文件路径列表
            name_pattern: 命名模式函数 (原文件名, 索引) -> 新文件名
            start: 起始序号
        """
        for i, file_path in enumerate(files):
            old_path = Path(file_path)
            new_name = name_pattern(old_path.stem, start + i)
            new_path = old_path.parent / (new_name + old_path.suffix)
            
            if new_path != old_path:
                old_path.rename(new_path)
                print(f"重命名: {old_path.name} -> {new_name}")
    
    def batch_move(self, files: List[str], target_dir: str, copy: bool = False):
        """批量移动或复制文件
        
        Args:
            files: 文件路径列表
            target_dir: 目标目录
            copy: True为复制，False为移动
        """
        target = Path(target_dir)
        target.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            src = Path(file_path)
            dst = target / src.name
            
            if copy:
                shutil.copy2(src, dst)
                print(f"复制: {src.name} -> {target_dir}")
            else:
                shutil.move(src, dst)
                print(f"移动: {src.name} -> {target_dir}")
    
    def clean_empty_dirs(self, path: Optional[str] = None):
        """清理空目录"""
        scan_path = self.base_path if path is None else Path(path)
        
        for dir_path in scan_path.rglob("*"):
            if dir_path.is_dir():
                try:
                    dir_path.rmdir()
                    print(f"删除空目录: {dir_path}")
                except OSError:
                    pass  # 目录非空
    
    def generate_report(self) -> Dict:
        """生成分析报告"""
        files = list(self.file_tree.values())
        
        # 按类型统计
        categorized = self.categorize_files(files)
        
        # 统计信息
        total_size = sum(f.size for f in files)
        file_count = len(files)
        
        # 最大文件
        largest_files = sorted(files, key=lambda x: x.size, reverse=True)[:10]
        
        # 最近文件
        recent_files = sorted(files, key=lambda x: x.modified_time, reverse=True)[:10]
        
        report = {
            "summary": {
                "total_files": file_count,
                "total_size": total_size,
                "total_size_formatted": f"{total_size / (1024*1024):.2f} MB"
            },
            "by_type": {ft.value: len(files) for ft, files in categorized.items()},
            "largest_files": [
                {"name": f.name, "size": f.size, "path": f.path}
                for f in largest_files
            ],
            "recent_files": [
                {"name": f.name, "modified": f.modified_time.isoformat()}
                for f in recent_files
            ]
        }
        
        return report
    
    def export_tree(self, output_file: str = "file_tree.json"):
        """导出文件树为JSON"""
        report = self.generate_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"文件树已导出到: {output_file}")


def demo():
    """演示"""
    print("=" * 60)
    print("智能文件管理器 - 演示")
    print("=" * 60)
    
    # 创建示例文件
    manager = SmartFileManager()
    
    # 扫描当前目录
    print("\n📂 扫描目录中...")
    files = manager.scan_directory(recursive=False)
    print(f"找到 {len(files)} 个文件")
    
    # 显示文件类型分布
    categorized = manager.categorize_files(files)
    print("\n📊 文件类型分布:")
    for file_type, file_list in categorized.items():
        print(f"  {file_type.value}: {len(file_list)} 个")
    
    # 生成报告
    print("\n📈 分析报告:")
    report = manager.generate_report()
    print(f"  总文件数: {report['summary']['total_files']}")
    print(f"  总大小: {report['summary']['total_size_formatted']}")
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    demo()
