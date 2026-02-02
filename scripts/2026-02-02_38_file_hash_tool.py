#!/usr/bin/env python3
"""
文件哈希验证工具 (Day 38)
支持多种哈希算法，批量验证文件完整性，生成校验和文件

功能:
- MD5, SHA-1, SHA-256, SHA-512 支持
- 批量文件处理和目录递归
- 校验和文件生成与验证
- 增量验证模式
"""

import hashlib
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys


class FileHasher:
    """文件哈希处理器"""
    
    ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    def __init__(self, algorithm: str = 'sha256'):
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"不支持的算法: {algorithm}，可选: {list(self.ALGORITHMS.keys())}")
        self.algorithm = algorithm
    
    def hash_file(self, filepath: str, chunk_size: int = 65536) -> str:
        """计算文件的哈希值"""
        hasher = self.ALGORITHMS[self.algorithm]()
        file_size = os.path.getsize(filepath)
        
        with open(filepath, 'rb') as f:
            processed = 0
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
                processed += len(chunk)
                # 显示进度
                progress = (processed / file_size) * 100
                sys.stdout.write(f"\r  进度: {progress:.1f}%")
                sys.stdout.flush()
        
        print()  # 换行
        return hasher.hexdigest()
    
    def hash_directory(self, directory: str, recursive: bool = True,
                       patterns: Optional[List[str]] = None) -> Dict[str, str]:
        """计算目录下所有文件的哈希值"""
        results = {}
        directory = Path(directory)
        
        if patterns is None:
            patterns = ['*']
        
        def should_include(path: Path) -> bool:
            if path.is_file():
                for pattern in patterns:
                    if path.match(pattern):
                        return True
            return False
        
        iterator = directory.rglob('*') if recursive else directory.glob('*')
        
        for item in iterator:
            if item.is_file() and should_include(item):
                rel_path = str(item.relative_to(directory))
                results[rel_path] = self.hash_file(str(item))
        
        return results


class ChecksumManager:
    """校验和文件管理器"""
    
    def __init__(self, hasher: FileHasher):
        self.hasher = hasher
    
    def generate_checksum_file(self, files: Dict[str, str], output_path: str,
                                relative_base: Optional[str] = None) -> str:
        """生成校验和文件"""
        checksums = {
            'algorithm': self.hasher.algorithm,
            'generated_at': datetime.now().isoformat(),
            'files': {}
        }
        
        for filepath, hash_value in files.items():
            if relative_base:
                rel_path = os.path.relpath(filepath, relative_base)
            else:
                rel_path = filepath
            checksums['files'][rel_path] = hash_value
        
        # 写入JSON格式
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(checksums, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def verify_checksum_file(self, checksum_file: str,
                              base_directory: Optional[str] = None) -> Tuple[bool, List[str]]:
        """验证校验和文件"""
        with open(checksum_file, 'r', encoding='utf-8') as f:
            checksums = json.load(f)
        
        algorithm = checksums.get('algorithm', self.hasher.algorithm)
        stored_files = checksums.get('files', {})
        
        # 临时切换算法
        old_algorithm = self.hasher.algorithm
        self.hasher = FileHasher(algorithm)
        
        errors = []
        all_match = True
        
        for rel_path, expected_hash in stored_files.items():
            if base_directory:
                full_path = os.path.join(base_directory, rel_path)
            else:
                full_path = rel_path
            
            if not os.path.exists(full_path):
                errors.append(f"  ❌ 文件不存在: {rel_path}")
                all_match = False
                continue
            
            actual_hash = self.hasher.hash_file(full_path)
            
            if actual_hash == expected_hash:
                print(f"  ✅ {rel_path}: 匹配")
            else:
                errors.append(f"  ❌ {rel_path}: 不匹配\n     期望: {expected_hash[:16]}...\n     实际: {actual_hash[:16]}...")
                all_match = False
        
        # 恢复原算法
        self.hasher = FileHasher(old_algorithm)
        
        return all_match, errors


def batch_verify(directory: str, checksum_file: str,
                 algorithm: str = 'sha256') -> bool:
    """批量验证目录文件"""
    print(f"\n🔍 批量验证: {directory}")
    print(f"📄 校验和文件: {checksum_file}\n")
    
    hasher = FileHasher(algorithm)
    manager = ChecksumManager(hasher)
    
    base_dir = directory
    all_match, errors = manager.verify_checksum_file(checksum_file, base_dir)
    
    if errors:
        print(f"\n⚠️ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(error)
    
    return all_match


def batch_generate(directory: str, output_file: str,
                   algorithm: str = 'sha256', recursive: bool = True) -> None:
    """批量生成校验和"""
    print(f"\n📦 批量生成校验和: {directory}")
    print(f"🔧 算法: {algorithm}")
    print(f"📄 输出: {output_file}\n")
    
    hasher = FileHasher(algorithm)
    files = hasher.hash_directory(directory, recursive=recursive)
    
    if not files:
        print("  ⚠️ 没有找到文件")
        return
    
    manager = ChecksumManager(hasher)
    manager.generate_checksum_file(files, output_file, relative_base=directory)
    
    print(f"\n✅ 已生成 {len(files)} 个文件的校验和")


def incremental_backup(source_dir: str, backup_dir: str,
                       algorithm: str = 'sha256') -> List[str]:
    """增量备份 - 只复制修改过的文件"""
    print(f"\n🔄 增量备份: {source_dir} → {backup_dir}")
    
    hasher = FileHasher(algorithm)
    checksum_file = os.path.join(backup_dir, '.checksums.json')
    
    # 加载旧的校验和
    old_checksums = {}
    if os.path.exists(checksum_file):
        with open(checksum_file, 'r') as f:
            data = json.load(f)
            old_checksums = data.get('files', {})
    
    # 计算当前文件的校验和
    current_files = hasher.hash_directory(source_dir, recursive=True)
    
    # 比较并复制修改过的文件
    copied = []
    os.makedirs(backup_dir, exist_ok=True)
    
    for rel_path, current_hash in current_files.items():
        old_hash = old_checksums.get(rel_path)
        
        if old_hash != current_hash:
            src = os.path.join(source_dir, rel_path)
            dst = os.path.join(backup_dir, rel_path)
            
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            with open(src, 'rb') as sf, open(dst, 'wb') as df:
                df.write(sf.read())
            
            print(f"  📋 {rel_path}")
            copied.append(rel_path)
    
    # 保存新的校验和
    manager = ChecksumManager(hasher)
    manager.generate_checksum_file(current_files, checksum_file, relative_base=source_dir)
    
    print(f"\n✅ 已复制 {len(copied)} 个修改的文件")
    return copied


def main():
    parser = argparse.ArgumentParser(
        description='文件哈希验证工具 - 支持多种算法和批量操作',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 生成单个文件的哈希
  python file_hash_tool.py single file.txt -a sha256
  
  # 批量生成目录校验和
  python file_hash_tool.py batch gen ./my_folder -o checksums.json
  
  # 验证校验和
  python file_hash_tool.py batch verify ./my_folder checksums.json
  
  # 增量备份
  python file_hash_tool.py backup ./source ./backup
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单文件命令
    file_parser = subparsers.add_parser('file', help='计算单个文件的哈希')
    file_parser.add_argument('filepath', help='文件路径')
    file_parser.add_argument('-a', '--algorithm', choices=['md5', 'sha1', 'sha256', 'sha512'],
                              default='sha256', help='哈希算法')
    
    # 批量命令
    batch_parser = subparsers.add_parser('batch', help='批量处理')
    batch_sub = batch_parser.add_subparsers(dest='batch_command', help='批量操作')
    
    gen_parser = batch_sub.add_parser('gen', help='生成校验和')
    gen_parser.add_argument('directory', help='目录路径')
    gen_parser.add_argument('-o', '--output', required=True, help='输出文件')
    gen_parser.add_argument('-a', '--algorithm', choices=['md5', 'sha1', 'sha256', 'sha512'],
                            default='sha256', help='哈希算法')
    gen_parser.add_argument('--no-recursive', action='store_true', help='不递归子目录')
    
    verify_parser = batch_sub.add_parser('verify', help='验证校验和')
    verify_parser.add_argument('directory', help='目录路径')
    verify_parser.add_argument('checksum_file', help='校验和文件')
    verify_parser.add_argument('-a', '--algorithm', choices=['md5', 'sha1', 'sha256', 'sha512'],
                               default='sha256', help='哈希算法')
    
    # 增量备份命令
    backup_parser = subparsers.add_parser('backup', help='增量备份')
    backup_parser.add_argument('source', help='源目录')
    backup_parser.add_argument('destination', help='目标目录')
    backup_parser.add_argument('-a', '--algorithm', choices=['md5', 'sha1', 'sha256', 'sha512'],
                               default='sha256', help='哈希算法')
    
    args = parser.parse_args()
    
    if args.command == 'file':
        hasher = FileHasher(args.algorithm)
        hash_value = hasher.hash_file(args.filepath)
        print(f"\n✅ {args.algorithm.upper()} = {hash_value}")
    
    elif args.command == 'batch':
        if args.batch_command == 'gen':
            batch_generate(args.directory, args.output, args.algorithm,
                          recursive=not args.no_recursive)
        elif args.batch_command == 'verify':
            batch_verify(args.directory, args.checksum_file, args.algorithm)
        else:
            batch_parser.print_help()
    
    elif args.command == 'backup':
        incremental_backup(args.source, args.destination, args.algorithm)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
