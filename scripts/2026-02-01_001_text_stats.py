#!/usr/bin/env python3
"""
📝 文本统计工具 - Text Statistics Tool
功能：统计文本的字符数、单词数、行数
作者：AI Coding Journey
日期：2026-02-01
"""

import sys
import re
from pathlib import Path


def count_text_stats(text: str) -> dict:
    """统计文本的各种指标"""
    stats = {
        "chars": len(text),
        "chars_no_space": len(text.replace(" ", "")),
        "words": len(text.split()),
        "lines": len(text.split("
")),
        "paragraphs": len([p for p in text.split("

") if p.strip()]),
    }
    return stats


def analyze_code(text: str) -> dict:
    """分析代码特有的指标"""
    stats = {
        "code_lines": len([l for l in text.split("
") if l.strip() and not l.strip().startswith("#")]),
        "comment_lines": len([l for l in text.split("
") if l.strip().startswith("#")]),
        "blank_lines": len([l for l in text.split("
") if not l.strip()]),
    }
    return stats


def print_stats(stats: dict, title: str = "📊 统计结果"):
    """格式化输出统计结果"""
    print(f"
{title}")
    print("-" * 40)
    for key, value in stats.items():
        key_display = key.replace("_", " ").title()
        print(f"  {key_display}: {value:,}")
    print("-" * 40)


def main():
    if len(sys.argv) < 2:
        print("📝 用法: python text_stats.py <文件路径>")
        print("   或: python text_stats.py -t \"要统计的文本\"")
        print("   或: cat file.txt | python text_stats.py")
        sys.exit(1)
    
    # 从文件读取
    if sys.argv[1] != "-t":
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8")
        is_code = file_path.suffix in {".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp"}
    else:
        # 从命令行参数读取
        text = " ".join(sys.argv[2:])
        is_code = False
    
    # 统计
    stats = count_text_stats(text)
    print_stats(stats, "📊 基本统计")
    
    if is_code:
        code_stats = analyze_code(text)
        print_stats(code_stats, "💻 代码分析")


if __name__ == "__main__":
    main()
