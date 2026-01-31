"""
路径分析器 - Path Analyzer
=======================
功能：分析文件路径，提取各种信息

Day 16: 路径分析器 - 帮助理解和管理文件路径
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PathAnalyzer:
    """路径分析器类"""
    
    def __init__(self):
        self.supported_formats = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.md': 'Markdown',
            '.txt': 'Text',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.html': 'HTML',
            '.css': 'CSS',
        }
    
    def analyze(self, path: str) -> Dict:
        """
        分析路径并返回详细信息
        
        Args:
            path: 文件或目录路径
            
        Returns:
            包含路径信息的字典
        """
        p = Path(path)
        
        result = {
            'path': str(p.absolute()),
            'name': p.name,
            'stem': p.stem,
            'suffix': p.suffix.lower(),
            'extension': p.suffix.lower(),
            'parent': str(p.parent),
            'parts': list(p.parts),
            'exists': p.exists(),
            'is_file': p.is_file(),
            'is_dir': p.is_dir(),
            'is_absolute': p.is_absolute(),
        }
        
        # 解析文件类型
        result['file_type'] = self._get_file_type(result['suffix'])
        
        # 获取文件大小
        if result['is_file']:
            result['size_bytes'] = p.stat().st_size
            result['size_formatted'] = self._format_size(result['size_bytes'])
        
        # 计算哈希
        if result['is_file']:
            result['md5'] = self._calculate_hash(p, 'md5')
            result['sha256'] = self._calculate_hash(p, 'sha256')
        
        # 获取修改时间
        if result['exists']:
            mtime = p.stat().st_mtime
            result['modified'] = datetime.fromtimestamp(mtime).isoformat()
        
        return result
    
    def _get_file_type(self, suffix: str) -> str:
        """获取文件类型描述"""
        return self.supported_formats.get(suffix, 'Unknown')
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    def _calculate_hash(self, path: Path, algorithm: str) -> str:
        """计算文件哈希值"""
        hash_func = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def find_files(self, directory: str, pattern: str = '*') -> List[Path]:
        """
        查找匹配模式的文件
        
        Args:
            directory: 搜索目录
            pattern: 文件名模式
            
        Returns:
            匹配的路径列表
        """
        p = Path(directory)
        return list(p.glob(pattern))
    
    def batch_analyze(self, paths: List[str]) -> List[Dict]:
        """批量分析路径"""
        return [self.analyze(path) for path in paths]
    
    def compare_paths(self, path1: str, path2: str) -> Dict:
        """比较两个路径的关系"""
        p1 = Path(path1)
        p2 = Path(path2)
        
        return {
            'path1': str(p1),
            'path2': str(p2),
            'is_same': p1 == p2,
            'is_parent': p1 in p2.parents,
            'is_child': p2 in p1.parents,
            'relative': str(p2.relative_to(p1)) if p1 in p2.parents else None,
            'common_parent': str(p1.parent) if p1.parent == p2.parent else None,
        }


def demo():
    """演示路径分析器功能"""
    analyzer = PathAnalyzer()
    
    # 分析当前文件
    current_file = __file__
    info = analyzer.analyze(current_file)
    
    print("=== 路径分析演示 ===")
    print(f"文件: {info['name']}")
    print(f"类型: {info['file_type']}")
    print(f"大小: {info['size_formatted']}")
    print(f"MD5: {info['md5'][:16]}...")
    print(f"修改时间: {info['modified']}")
    print(f"路径部分: {' → '.join(info['parts'][-3:])}")
    
    # 查找Python文件
    print("\n=== 查找Python文件 ===")
    py_files = analyzer.find_files('.', '*.py')
    print(f"找到 {len(py_files)} 个Python文件")
    
    return info


if __name__ == '__main__':
    demo()
