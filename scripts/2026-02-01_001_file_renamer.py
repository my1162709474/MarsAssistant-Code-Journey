#!/usr/bin/env python3
"""
📁 智能文件批量重命名工具
Intelligent Batch File Renamer

AI Code Journey - Day 1 (2026-02-01)
一个实用的文件管理工具，展示了Python的文件操作能力。
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime


class SmartFileRenamer:
    """智能文件批量重命名器"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.stats = {"success": 0, "failed": 0, "skipped": 0}
    
    def rename_by_pattern(
        self, 
        pattern: str, 
        replacement: str,
        file_extension: str = "*",
        preview: bool = True
    ) -> dict:
        """
        根据正则表达式模式重命名文件
        
        Args:
            pattern: 正则表达式模弰(������������ɕ���������胚n��6���_�����ϼ�'�R��2qpİ�qp˞�c�>7�BG��W�R���(����������������}��ѕ�ͥ��胚Z��ۚ&�������过滤
            preview: 是否仅预览而不实际执行
        
        Returns:
            操作统计信息
        """
        regex = re.compile(pattern)
        files = self.base_path.glob(f"*.{file_extension}") if file_extension != "*" else self.base_path.iterdir()
        
        operations = []
        for file_path in files:
            if file_path.is_file():
                new_name = regex.sub(replacement, file_path.name)
                if new_name != file_path.name:
                    operations.append((file_path, new_name))
        
        if preview:
            print("📋 预览模式 - 以下是即将执行的操作:")
            print("-" * 60)
            for old, new in operations:
                print(f"  {old.name} → {new}")
            print("-" * 60)
            print(f"共 {len(operations)} 个文件将被重命名")
            return {"preview": operations, "count": len(operations)}
        
        # 实际执行重命名
        for old_path, new_name in operations:
            try:
                new_path = old_path.parent / new_name
                old_path.rename(new_path)
                self.stats["success"] += 1
                print(f"✅ {old_path.name} → {new_name}")
            except Exception as e:
                self.stats["failed"] += 1
                print(f"❌ {old_path.name} 失败: {e}")
        
        return self.stats
    
    def add_prefix(self, prefix: str, file_extension: str = "*") -> dict:
        """为文件添加前缀"""
        return self.rename_by_pattern(
            pattern=r"^(.+)$",
            replacement=f"{prefix}\\1",
            file_extension=file_extension
        )
    
    def add_suffix(self, suffix: str, file_extension: str = "*") -> dict:
        """为文件添加后缀（位于扩展名之前）"""
        return self.rename_by_pattern(
            pattern=r"^(.+?)(\.[^.]+)$",
            replacement=f"\\1{suffix}\\2",
            file_extension=file_extension
        )
    
    def to_snake_case(self, file_extension: str = "*") -> dict:
        """将文件名转换为snake_case格式"""
        def snake_replace(match):
            name = match.group(1)
            ext = match.group(2) if match.group(2) else ""
            # 转换空格和连字符为下划线
            snake = re.sub(r"[\s\-]+", "_", name)
            # 处理驼峰命名
            snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake)
            # 移除连续下划线
            snake = re.sub(r"_+", "_", snake)
            # 转小写
            return snake.lower() + ext
        
        return self.rename_by_pattern(
            pattern=r"^(.+?)(\.[^.]+)?$",
            replacement=snake_replace,
            file_extension=file_extension
        )
    
    def number_files(self, start: int = 1, pattern: str = "{:02d}_{}") -> dict:
        """为文件添加序号"""
        files = sorted([f for f in self.base_path.iterdir() if f.is_file()])
        operations = []
        
        for i, file_path in enumerate(files, start=start):
            new_name = pattern.format(i, file_path.name)
            operations.append((file_path, new_name))
        
        print("📋 序号重命名预览:")
        for old, new in operations:
            print(f"  {old.name} → {new}")
        
        return {"operations": operations, "count": len(operations)}


def demo():
    """演示各种功能"""
    print("🛠️ 智能文件批量重命名工具演示")
    print("=" * 60)
    
    # 创建示例文件用于测试
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    sample_files = [
        "My Document.txt",
        "Hello World.py",
        "Some-File-Name.pdf",
        "CamelCaseFile.jpg",
        "file with spaces.docx"
    ]
    
    for filename in sample_files:
        (test_dir / filename).touch()
    
    print(f"\n📂 测试目录: {test_dir}")
    print("创建了以下测试文件:")
    for f in sorted(test_dir.iterdir()):
        print(f"  - {f.name}")
    
    renamer = SmartFileRenamer(test_dir)
    
    print("\n🔤 转换为snake_case:")
    renamer.to_snake_case()
    
    # 清理测试目录
    import shutil
    shutil.rmtree(test_dir)
    print("\n🧹 测试目录已清理")


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🛠️ 智能文件批量重命名工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python file_renamer.py --prefix "new_"
  python file_renamer.py --suffix "_backup"
  python file_renamer.py --snake-case
  python file_renamer.py --number
  python file_renamer.py --pattern "old" --replace "new"
        """
    )
    
    parser.add_argument("--path", default=".", help="目标目录路径")
    parser.add_argument("--prefix", help="添加前缀")
    parser.add_argument("--suffix", help="添加后缀")
    parser.add_argument("--snake-case", action="store_true", help="转换为snake_case")
    parser.add_argument("--number", action="store_true", help="添加序号")
    parser.add_argument("--pattern", help="正则表达式模式")
    parser.add_argument("--replace", help="替换字符串")
    parser.add_argument("--extension", default="*", help="文件扩展名过滤")
    parser.add_argument("--execute", action="store_true", help="执行操作（默认仅预览）")
    parser.add_argument("--demo", action="store_true", help="运行演示")
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
        return
    
    renamer = SmartFileRenamer(args.path)
    
    if args.prefix:
        renamer.add_prefix(args.prefix, args.extension)
    elif args.suffix:
        renamer.add_suffix(args.suffix, args.extension)
    elif args.snake_case:
        renamer.to_snake_case(args.extension)
    elif args.number:
        renamer.number_files()
    elif args.pattern and args.replace:
        renamer.rename_by_pattern(args.pattern, args.replace, args.extension)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
