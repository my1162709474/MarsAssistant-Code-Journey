#!/usr/bin/env python3
"""
Code Diff Tool - 代码差异对比工具
比较两个文件或文本的差异，支持多种输出格式

功能:
- 文件对比
- 文本对比
- 多种diff格式输出 (unified, side-by-side, minimal)
- 相似度计算
- 变更统计

Author: MarsAssistant-Code-Journey
Date: 2026-02-04
"""

import difflib
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Callable


class DiffFormat(Enum):
    """Diff输出格式"""
    UNIFIED = "unified"      # 统一格式 (git diff默认)
    CONTEXT = "context"      # 上下文格式
    SIDE_BY_SIDE = "side"    # 并排格式
    HTML = "html"            # HTML格式
    MINIMAL = "minimal"      # 最小格式


class ChangeType(Enum):
    """变更类型"""
    UNCHANGED = "unchanged"
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"


@dataclass
class DiffLine:
    """Diff行信息"""
    line_num_a: Optional[int]  # 文件A的行号
    line_num_b: Optional[int]  # 文件B的行号
    content: str               # 行内容
    change_type: ChangeType    # 变更类型
    prefix: str               # 前缀符号 (-/+/ ))


@dataclass
class DiffResult:
    """Diff结果"""
    lines: List[DiffLine]
    stats: dict               # 统计信息
    similarity: float         # 相似度 (0-1)


class DiffTool:
    """代码差异对比工具"""
    
    # ANSI颜色代码
    COLORS = {
        'green': '\033[92m',   # 新增
        'red': '\033[91m',     # 删除
        'yellow': '\033[93m',   # 修改
        'blue': '\033[94m',     # 信息
        'end': '\033[0m',       # 结束
        'bold': '\033[1m',      # 加粗
    }
    
    def __init__(self, colorize: bool = True):
        self.colorize = colorize
    
    def _color(self, text: str, color: str) -> str:
        """应用颜色"""
        if not self.colorize:
            return text
        return f"{self.COLORS.get(color, self.COLORS['end'])}{text}{self.COLORS['end']}"
    
    def _read_file(self, path: str) -> List[str]:
        """读取文件"""
        if path.startswith('=') and path.endswith('='):
            # 特殊标记的文本
            return path[1:-1].split('\n')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().splitlines(keepends=False)
        except FileNotFoundError:
            print(f"警告: 文件 {path} 不存在，使用空文件")
            return []
        except Exception as e:
            print(f"错误: 读取文件 {path} 失败: {e}")
            return []
    
    def _calculate_stats(self, lines: List[DiffLine]) -> dict:
        """计算统计信息"""
        added = sum(1 for l in lines if l.change_type == ChangeType.ADDED)
        deleted = sum(1 for l in lines if l.change_type == ChangeType.DELETED)
        modified = sum(1 for l in lines if l.change_type == ChangeType.MODIFIED)
        unchanged = sum(1 for l in lines if l.change_type == ChangeType.UNCHANGED)
        
        total = len(lines) if lines else 1
        
        return {
            'total_lines': len(lines),
            'added_lines': added,
            'deleted_lines': deleted,
            'modified_lines': modified,
            'unchanged_lines': unchanged,
            'change_rate': round(((added + deleted + modified) / total) * 100, 2)
        }
    
    def _calculate_similarity(self, text1: List[str], text2: List[str]) -> float:
        """计算两个文本的相似度"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # 使用序列匹配器计算相似度
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return round(matcher.ratio(), 4)
    
    def _detect_changes(self, a: List[str], b: List[str]) -> List[DiffLine]:
        """检测变更"""
        # 使用SequenceMatcher获取差异块
        matcher = difflib.SequenceMatcher(None, a, b)
        lines = []
        line_num_a = 1
        line_num_b = 1
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for line in a[i1:i2]:
                    lines.append(DiffLine(
                        line_num_a=line_num_a,
                        line_num_b=line_num_b,
                        content=line,
                        change_type=ChangeType.UNCHANGED,
                        prefix='  '
                    ))
                    line_num_a += 1
                    line_num_b += 1
            elif tag == 'delete':
                for line in a[i1:i2]:
                    lines.append(DiffLine(
                        line_num_a=line_num_a,
                        line_num_b=None,
                        content=line,
                        change_type=ChangeType.DELETED,
                        prefix='- '
                    ))
                    line_num_a += 1
            elif tag == 'insert':
                for line in b[j1:j2]:
                    lines.append(DiffLine(
                        line_num_a=None,
                        line_num_b=line_num_b,
                        content=line,
                        change_type=ChangeType.ADDED,
                        prefix='+ '
                    ))
                    line_num_b += 1
            elif tag == 'replace':
                # 替换: 显示为删除+添加
                for line in a[i1:i2]:
                    lines.append(DiffLine(
                        line_num_a=line_num_a,
                        line_num_b=None,
                        content=line,
                        change_type=ChangeType.DELETED,
                        prefix='- '
                    ))
                    line_num_a += 1
                for line in b[j1:j2]:
                    lines.append(DiffLine(
                        line_num_a=None,
                        line_num_b=line_num_b,
                        content=line,
                        change_type=ChangeType.ADDED,
                        prefix='+ '
                    ))
                    line_num_b += 1
        
        return lines
    
    def diff_files(self, file_a: str, file_b: str) -> DiffResult:
        """对比两个文件"""
        lines_a = self._read_file(file_a)
        lines_b = self._read_file(file_b)
        return self.diff_text(lines_a, lines_b)
    
    def diff_text(self, text_a: List[str], text_b: List[str], 
                  name_a: str = "A", name_b: str = "B") -> DiffResult:
        """对比两段文本"""
        lines = self._detect_changes(text_a, text_b)
        stats = self._calculate_stats(lines)
        similarity = self._calculate_similarity(text_a, text_b)
        
        return DiffResult(lines=lines, stats=stats, similarity=similarity)
    
    def format_unified(self, result: DiffResult, name_a: str = "A", 
                       name_b: str = "B", context: int = 3) -> str:
        """统一格式输出 (类似git diff)"""
        output = []
        output.append(f"--- {name_a}")
        output.append(f"+++ {name_b}")
        
        lines = result.lines
        i = 0
        while i < len(lines):
            # 找到下一个变更块
            change_start = i
            while i < len(lines) and lines[i].change_type == ChangeType.UNCHANGED:
                i += 1
            
            if i >= len(lines):
                break
            
            # 计算上下文起始位置
            context_start = max(0, i - context)
            context_end = min(len(lines), i + context)
            
            # 收集变更行
            change_lines = []
            while i < len(lines) and lines[i].change_type != ChangeType.UNCHANGED:
                change_lines.append(lines[i])
                i += 1
            
            # 输出变更块
            if change_lines:
                # 输出hunk头
                hunk_start = change_lines[0].line_num_a or 1
                hunk_count = sum(1 for l in change_lines if l.line_num_a)
                hunk_new_start = change_lines[0].line_num_b or 1
                hunk_new_count = sum(1 for l in change_lines if l.line_num_b)
                output.append(f"@@ -{hunk_start},{hunk_count} +{hunk_new_start},{hunk_new_count} @@")
                
                # 输出上下文
                for j in range(context_start, change_start):
                    line = lines[j]
                    output.append(f"{line.prefix}{line.content}")
                
                # 输出变更
                for line in change_lines:
                    output.append(f"{line.prefix}{line.content}")
        
        return '\n'.join(output)
    
    def format_side_by_side(self, result: DiffResult, name_a: str = "A", 
                            name_b: str = "B", width: int = 80) -> str:
        """并排格式输出"""
        output = []
        separator = ' | '
        
        # 标题
        output.append(f"{name_a.ljust(20)}{separator}{name_b.ljust(20)}")
        output.append('-' * 50)
        
        for line in result.lines:
            line_a = f"{line.line_num_a or '':>4}: {line.content}" if line.line_num_a else ""
            line_b = f"{line.line_num_b or '':>4}: {line.content}" if line.line_num_b else ""
            
            if line.change_type == ChangeType.UNCHANGED:
                output.append(f"{line_a:<25}{separator}{line_b:<25}")
            elif line.change_type == ChangeType.ADDED:
                colored_b = self._color(line_b, 'green') if self.colorize else line_b
                output.append(f"{'':25}{separator}{colored_b:<25}")
            elif line.change_type == ChangeType.DELETED:
                colored_a = self._color(line_a, 'red') if self.colorize else line_a
                output.append(f"{colored_a:<25}{separator}{'':25}")
            else:
                colored_a = self._color(line_a, 'red') if self.colorize else line_a
                colored_b = self._color(line_b, 'green') if self.colorize else line_b
                output.append(f"{colored_a:<25}{separator}{colored_b:<25}")
        
        return '\n'.join(output)
    
    def format_html(self, result: DiffResult, name_a: str = "A", 
                    name_b: str = "B") -> str:
        """HTML格式输出"""
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <title>Code Diff Report</title>',
            '    <style>',
            '        body { font-family: monospace; padding: 20px; }',
            '        .diff-table { border-collapse: collapse; width: 100%; }',
            '        .diff-table td, .diff-table th { padding: 5px 10px; border: 1px solid #ddd; }',
            '        .added { background-color: #d4edda; color: #155724; }',
            '        .deleted { background-color: #f8d7da; color: #721c24; }',
            '        .unchanged { background-color: #f8f9fa; }',
            '        .header { background-color: #007bff; color: white; font-weight: bold; }',
            '    </style>',
            '</head>',
            '<body>',
            f'    <h1>Code Diff: {name_a} → {name_b}</h1>',
            '    <table class="diff-table">',
            '        <tr><th class="header">Line</th><th class="header">A</th><th class="header">Line</th><th class="header">B</th></tr>',
        ]
        
        for line in result.lines:
            if line.change_type == ChangeType.ADDED:
                row_class = 'added'
            elif line.change_type == ChangeType.DELETED:
                row_class = 'deleted'
            else:
                row_class = 'unchanged'
            
            line_a = f"{line.line_num_a}" if line.line_num_a else ""
            line_b = f"{line.line_num_b}" if line.line_num_b else ""
            content = line.content.replace('<', '&lt;').replace('>', '&gt;')
            
            html.append(
                f'        <tr class="{row_class}">'
                f'<td>{line_a}</td><td>{content}</td>'
                f'<td>{line_b}</td><td></td></tr>'
            )
        
        html.extend(['    </table>', '</body>', '</html>'])
        return '\n'.join(html)
    
    def format_minimal(self, result: DiffResult) -> str:
        """最小格式输出 - 只显示有变化的行"""
        output = []
        
        for line in result.lines:
            if line.change_type != ChangeType.UNCHANGED:
                marker = {
                    ChangeType.ADDED: '+',
                    ChangeType.DELETED: '-',
                    ChangeType.MODIFIED: '!',
                }.get(line.change_type, '?')
                output.append(f"{marker} {line.content}")
        
        return '\n'.join(output)
    
    def print_result(self, result: DiffResult, name_a: str = "A", 
                     name_b: str = "B", format: DiffFormat = DiffFormat.UNIFIED):
        """打印Diff结果"""
        # 打印统计信息
        print(f"\n{self._color('📊 差异统计', 'blue')} {name_a} → {name_b}")
        print(f"{'='*50}")
        print(f"  相似度: {self._color(f'{result.similarity * 100:.2f}%', 'bold')}")
        print(f"  总行数: {result.stats['total_lines']}")
        print(f"  {self._color('新增', 'green')}: {result.stats['added_lines']} 行")
        print(f"  {self._color('删除', 'red')}: {result.stats['deleted_lines']} 行")
        print(f"  {self._color('修改', 'yellow')}: {result.stats['modified_lines']} 行")
        print(f"  不变: {result.stats['unchanged_lines']} 行")
        print(f"  变化率: {result.stats['change_rate']}%")
        print()
        
        # 打印差异内容
        if format == DiffFormat.UNIFIED:
            formatted = self.format_unified(result, name_a, name_b)
        elif format == DiffFormat.SIDE_BY_SIDE:
            formatted = self.format_side_by_side(result, name_a, name_b)
        elif format == DiffFormat.HTML:
            formatted = self.format_html(result, name_a, name_b)
        elif format == DiffFormat.MINIMAL:
            formatted = self.format_minimal(result)
        else:
            formatted = self.format_unified(result, name_a, name_b)
        
        print(formatted)
        return formatted
    
    def save_html_report(self, result: DiffResult, output_path: str,
                         name_a: str = "A", name_b: str = "B"):
        """保存HTML报告"""
        html = self.format_html(result, name_a, name_b)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML报告已保存到: {output_path}")


# 便捷函数
def quick_diff(text_a: str, text_b: str) -> DiffResult:
    """快速对比两段文本"""
    tool = DiffTool()
    lines_a = text_a.split('\n')
    lines_b = text_b.split('\n')
    return tool.diff_text(lines_a, lines_b)


def file_diff(path_a: str, path_b: str, 
              colorize: bool = True) -> DiffResult:
    """快速对比两个文件"""
    tool = DiffTool(colorize=colorize)
    return tool.diff_files(path_a, path_b)


# 使用示例
if __name__ == "__main__":
    # 示例1: 文本对比
    print("\n" + "="*60)
    print("示例1: 文本对比")
    print("="*60)
    
    text1 = """def hello():
    print("Hello, World!")
    return True"""

    text2 = """def hello(name="World"):
    print(f"Hello, {name}!")
    return True"""

    result = quick_diff(text1, text2)
    diff_tool = DiffTool()
    diff_tool.print_result(result, "原文本", "新文本", DiffFormat.SIDE_BY_SIDE)
    
    # 示例2: 文件对比
    print("\n" + "="*60)
    print("示例2: 文件对比")
    print("="*60)
    
    # 创建临时测试文件
    test_content_a = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b
""".strip()

    test_content_b = """
def add(a, b, verbose=False):
    result = a + b
    if verbose:
        print(f"Result: {result}")
    return result

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""".strip()
    
    # 使用临时文件测试
    with open('/tmp/test_a.py', 'w') as f:
        f.write(test_content_a)
    with open('/tmp/test_b.py', 'w') as f:
        f.write(test_content_b)
    
    result2 = file_diff('/tmp/test_a.py', '/tmp/test_b.py')
    diff_tool.print_result(result2, "test_a.py", "test_b.py", DiffFormat.UNIFIED)
    
    # 示例3: HTML报告
    print("\n" + "="*60)
    print("示例3: 生成HTML报告")
    print("="*60)
    
    diff_tool.save_html_report(result2, '/tmp/diff_report.html')
    print(f"HTML报告已生成: /tmp/diff_report.html")
    
    # 示例4: 最小格式
    print("\n" + "="*60)
    print("示例4: 最小格式")
    print("="*60)
    
    print(diff_tool.format_minimal(result))
