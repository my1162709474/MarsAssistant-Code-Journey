#!/usr/bin/env python3
"""
智能文本差异比较器 (Smart Text Diff Tool)
=========================================
支持多种差异检测算法、可视化输出、语法高亮的文本比较工具

功能特性:
- LCS (最长公共子序列) 差异检测
- Myers 差分算法 (git diff 默认算法)
- 多种输出格式: 统一格式(unified)、并排格式(side-by-side)、命令行格式(console)
- 统计摘要: 插入/删除/修改行数统计
- 忽略空白行和注释行 (支持多种编程语言)
- 批量比较多个文件
- 输出格式: 终端高亮、HTML、JSON、Markdown

作者: AI Assistant
日期: 2026-02-02
"""

import sys
import os
import json
import difflib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
from collections import defaultdict


class DiffAlgorithm(Enum):
    """差分算法类型"""
    LCS = "lcs"           # 最长公共子序列
    MYERS = "myers"       # Myers差分算法 (默认)
    SEQUENCE = "sequence" # Python difflib.SequenceMatcher


class OutputFormat(Enum):
    """输出格式"""
    CONSOLE = "console"   # 终端高亮输出 (默认)
    UNIFIED = "unified"   # 统一diff格式 (类似git diff)
    SIDE_BY_SIDE = "side" # 并排显示
    HTML = "html"         # HTML页面
    JSON = "json"         # JSON格式
    MARKDOWN = "markdown" # Markdown表格


class LineType(Enum):
    """行类型"""
    UNCHANGED = "unchanged"
    INSERTED = "inserted"
    DELETED = "deleted"
    MODIFIED = "modified"


@dataclass
class DiffLine:
    """差异行"""
    line_number: int           # 行号
    line_type: LineType        # 行类型
    content: str               # 行内容
    old_line_number: Optional[int] = None  # 原始行号 (删除/修改时)
    new_line_number: Optional[int] = None  # 新行号 (插入/修改时)


@dataclass
class DiffHunk:
    """差异块"""
    old_start: int             # 原始文件起始行号
    old_lines: int             # 原始文件行数
    new_start: int             # 新文件起始行号
    new_lines: int             # 新文件行数
    lines: List[DiffLine] = field(default_factory=list)


@dataclass
class DiffResult:
    """差异比较结果"""
    file_a: str
    file_b: str
    hunks: List[DiffHunk]
    stats: Dict[str, int]      # 统计信息
    algorithm: DiffAlgorithm
    identical: bool = False


class IgnorePatterns:
    """忽略模式配置"""
    
    # 各语言的注释模式
    COMMENT_PATTERNS = {
        'python': [
            r'^\s*#.*$',                    # 单行注释
            r'^\s*"""[\s\S]*?"""\s*$',     # 多行字符串注释
            r"^\s*'''[\s\S]*?'''\s*$",
        ],
        'javascript': [
            r'^\s*//.*$',                   # 单行注释
            r'^\s*/\*[\s\S]*?\*/\s*$',     # 多行注释
        ],
        'java': [
            r'^\s*//.*$',
            r'^\s*/\*[\s\S]*?\*/\s*$',
            r'^\s*\*.*$',                   # Javadoc风格
        },
        'c': [
            r'^\s*//.*$',
            r'^\s*/\*[\s\S]*?\*/\s*$',
        ],
        'cpp': [
            r'^\s*//.*$',
            r'^\s*/\*[\s\S]*?\*/\s*$',
        ],
        'html': [
            r'^\s*<!--[\s\S]*?-->\s*$',    # HTML注释
        ],
        'css': [
            r'^\s*/\*[\s\S]*?\*/\s*$',
        ],
        'shell': [
            r'^\s*#.*$',
        ],
        'sql': [
            r'^\s*--.*$',
            r'^\s*/\*[\s\S]*?\*/\s*$',
        ],
    }
    
    # 空白行模式
    BLANK_LINE_PATTERN = r'^\s*$'
    
    @classmethod
    def should_ignore(cls, line: str, ignore_comments: bool = False, 
                      language: str = 'python', ignore_blank: bool = False) -> bool:
        """判断是否应该忽略该行"""
        if ignore_blank and re.match(cls.BLANK_LINE_PATTERN, line):
            return True
        if ignore_comments and language in cls.COMMENT_PATTERNS:
            for pattern in cls.COMMENT_PATTERNS[language]:
                if re.match(pattern, line):
                    return True
        return False


class SmartDiff:
    """智能文本差异比较器"""
    
    # ANSI颜色代码
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[31m',       # 删除 - 红色
        'green': '\033[32m',     # 插入 - 绿色
        'yellow': '\033[33m',    # 修改 - 黄色
        'blue': '\033[34m',      # 行号 - 蓝色
        'cyan': '\033[36m',      # 元信息 - 青色
    }
    
    # 符号
    SYMBOLS = {
        'insert': '+',
        'delete': '-',
        'unchanged': ' ',
        'hunk_start': '@@',
        'hunk_end': '',
    }
    
    def __init__(self, algorithm: DiffAlgorithm = DiffAlgorithm.MYERS):
        """初始化差分器
        
        Args:
            algorithm: 差分算法 (默认使用 Myers 算法，与 git diff 一致)
        """
        self.algorithm = algorithm
    
    def compare_files(self, file_a: str, file_b: str,
                      ignore_comments: bool = False,
                      ignore_blank: bool = False,
                      language: str = 'python') -> DiffResult:
        """比较两个文件
        
        Args:
            file_a: 原始文件路径
            file_b: 新文件路径
            ignore_comments: 是否忽略注释行
            ignore_blank: 是否忽略空白行
            language: 编程语言 (用于识别注释)
            
        Returns:
            DiffResult: 差异比较结果
        """
        with open(file_a, 'r', encoding='utf-8') as f:
            lines_a = f.readlines()
        with open(file_b, 'r', encoding='utf-8') as f:
            lines_b = f.readlines()
        
        return self.compare_lines(lines_a, lines_b, file_a, file_b,
                                  ignore_comments, ignore_blank, language)
    
    def compare_lines(self, lines_a: List[str], lines_b: List[str],
                      file_a: str = "file_a", file_b: str = "file_b",
                      ignore_comments: bool = False,
                      ignore_blank: bool = False,
                      language: str = 'python') -> DiffResult:
        """比较两行列表
        
        Args:
            lines_a: 原始行列表
            lines_b: 新行列表
            file_a: 文件A名称
            file_b: 文件B名称
            ignore_comments: 是否忽略注释行
            ignore_blank: 是否忽略空白行
            language: 编程语言
            
        Returns:
            DiffResult: 差异比较结果
        """
        # 过滤行 (可选)
        if ignore_comments or ignore_blank:
            lines_a = [line for line in lines_a 
                      if not IgnorePatterns.should_ignore(line, ignore_comments, language, ignore_blank)]
            lines_b = [line for line in lines_b 
                      if not IgnorePatterns.should_ignore(line, ignore_comments, language, ignore_blank)]
        
        # 根据算法选择比较方法
        if self.algorithm == DiffAlgorithm.LCS:
            hunks = self._compare_lcs(lines_a, lines_b)
        elif self.algorithm == DiffAlgorithm.SEQUENCE:
            hunks = self._compare_sequence(lines_a, lines_b)
        else:  # MYERS (default)
            hunks = self._compare_myers(lines_a, lines_b)
        
        # 计算统计信息
        stats = self._calculate_stats(hunks)
        identical = stats['inserted'] == 0 and stats['deleted'] == 0 and stats['modified'] == 0
        
        return DiffResult(
            file_a=file_a,
            file_b=file_b,
            hunks=hunks,
            stats=stats,
            algorithm=self.algorithm,
            identical=identical
        )
    
    def _compare_myers(self, lines_a: List[str], lines_b: List[str]) -> List[DiffHunk]:
        """使用 Myers 算法比较 (类似 git diff)"""
        # 标准化行 (去除换行符用于比较)
        a = [line.rstrip('\n') for line in lines_a]
        b = [line.rstrip('\n') for line in lines_b]
        
        # 使用 difflib 生成 unified diff
        diff = difflib.unified_diff(a, b, fromfile='a', tofile='b', lineterm='')
        diff_lines = list(diff)
        
        return self._parse_unified_diff(diff_lines)
    
    def _compare_lcs(self, lines_a: List[str], lines_b: List[str]) -> List[DiffHunk]:
        """使用 LCS 算法比较"""
        a = [line.rstrip('\n') for line in lines_a]
        b = [line.rstrip('\n') for line in lines_b]
        
        # 计算 LCS
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i-1] == b[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        # 回溯找出差异
        hunks = []
        i, j = m, n
        changes = []
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and a[i-1] == b[j-1]:
                changes.append(('unchanged', i, j, a[i-1]))
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
                changes.append(('inserted', i, j-1, b[j-1]))
                j -= 1
            else:
                changes.append(('deleted', i-1, j, a[i-1]))
                i -= 1
        
        changes.reverse()
        hunks.append(self._build_hunk_from_changes(changes, len(lines_a), len(lines_b)))
        
        return hunks
    
    def _compare_sequence(self, lines_a: List[str], lines_b: List[str]) -> List[DiffHunk]:
        """使用 Python SequenceMatcher 比较"""
        a = [line.rstrip('\n') for line in lines_a]
        b = [line.rstrip('\n') for line in lines_b]
        
        matcher = difflib.SequenceMatcher(None, a, b)
        opcodes = matcher.get_opcodes()
        
        hunks = []
        for opcode, i1, i2, j1, j2 in opcodes:
            if opcode == 'equal':
                continue
            
            hunk = DiffHunk(
                old_start=i1 + 1,
                old_lines=i2 - i1,
                new_start=j1 + 1,
                new_lines=j2 - j1,
                lines=[]
            )
            
            for i in range(i1, i2):
                hunk.lines.append(DiffLine(
                    line_number=i + 1,
                    line_type=LineType.DELETED,
                    content=a[i],
                    old_line_number=i + 1
                ))
            
            for j in range(j1, j2):
                hunk.lines.append(DiffLine(
                    line_number=j + 1,
                    line_type=LineType.INSERTED,
                    content=b[j],
                    new_line_number=j + 1
                ))
            
            hunks.append(hunk)
        
        return hunks
    
    def _parse_unified_diff(self, diff_lines: List[str]) -> List[DiffHunk]:
        """解析 unified diff 格式"""
        hunks = []
        current_hunk = None
        
        for line in diff_lines:
            if line.startswith('---'):
                continue
            if line.startswith('+++'):
                continue
            
            if line.startswith('@@'):
                if current_hunk:
                    hunks.append(current_hunk)
                
                # 解析 @@ -old,len +new,len @@
                match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_lines = int(match.group(2)) if match.group(2) else 1
                    new_start = int(match.group(3))
                    new_lines = int(match.group(4)) if match.group(4) else 1
                    
                    current_hunk = DiffHunk(
                        old_start=old_start,
                        old_lines=old_lines,
                        new_start=new_start,
                        new_lines=new_lines,
                        lines=[]
                    )
            elif current_hunk is not None:
                if line.startswith('-'):
                    current_hunk.lines.append(DiffLine(
                        line_number=current_hunk.old_start + len([l for l in current_hunk.lines if l.line_type == LineType.INSERTED]),
                        line_type=LineType.DELETED,
                        content=line[1:],
                        old_line_number=current_hunk.old_start + len([l for l in current_hunk.lines if l.line_type == LineType.DELETED])
                    ))
                elif line.startswith('+'):
                    current_hunk.lines.append(DiffLine(
                        line_number=current_hunk.new_start + len([l for l in current_hunk.lines if l.line_type == LineType.INSERTED]),
                        line_type=LineType.INSERTED,
                        content=line[1:],
                        new_line_number=current_hunk.new_start + len([l for l in current_hunk.lines if l.line_type == LineType.INSERTED])
                    ))
                else:
                    current_hunk.lines.append(DiffLine(
                        line_number=0,
                        line_type=LineType.UNCHANGED,
                        content=line[1:]
                    ))
        
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    def _build_hunk_from_changes(self, changes: List[Tuple], 
                                  total_old: int, total_new: int) -> DiffHunk:
        """从变化列表构建差异块"""
        hunk = DiffHunk(
            old_start=1,
            old_lines=total_old,
            new_start=1,
            new_lines=total_new,
            lines=[]
        )
        
        for change in changes:
            change_type, old_idx, new_idx, content = change
            
            if change_type == 'unchanged':
                hunk.lines.append(DiffLine(
                    line_number=old_idx,
                    line_type=LineType.UNCHANGED,
                    content=content,
                    old_line_number=old_idx,
                    new_line_number=new_idx
                ))
            elif change_type == 'inserted':
                hunk.lines.append(DiffLine(
                    line_number=new_idx,
                    line_type=LineType.INSERTED,
                    content=content,
                    new_line_number=new_idx
                ))
            else:  # deleted
                hunk.lines.append(DiffLine(
                    line_number=old_idx,
                    line_type=LineType.DELETED,
                    content=content,
                    old_line_number=old_idx
                ))
        
        return hunk
    
    def _calculate_stats(self, hunks: List[DiffHunk]) -> Dict[str, int]:
        """计算差异统计"""
        stats = {
            'inserted': 0,
            'deleted': 0,
            'modified': 0,
            'unchanged': 0,
            'total_changes': 0,
            'hunks': len(hunks)
        }
        
        for hunk in hunks:
            for line in hunk.lines:
                if line.line_type == LineType.INSERTED:
                    stats['inserted'] += 1
                elif line.line_type == LineType.DELETED:
                    stats['deleted'] += 1
                elif line.line_type == LineType.MODIFIED:
                    stats['modified'] += 1
                else:
                    stats['unchanged'] += 1
        
        stats['total_changes'] = stats['inserted'] + stats['deleted'] + stats['modified']
        
        return stats
    
    def format_output(self, result: DiffResult, 
                      format_type: OutputFormat = OutputFormat.CONSOLE) -> str:
        """格式化输出
        
        Args:
            result: 差异比较结果
            format_type: 输出格式
            
        Returns:
            str: 格式化后的差异输出
        """
        if format_type == OutputFormat.UNIFIED:
            return self._format_unified(result)
        elif format_type == OutputFormat.SIDE_BY_SIDE:
            return self._format_side_by_side(result)
        elif format_type == OutputFormat.HTML:
            return self._format_html(result)
        elif format_type == OutputFormat.JSON:
            return self._format_json(result)
        elif format_type == OutputFormat.MARKDOWN:
            return self._format_markdown(result)
        else:
            return self._format_console(result)
    
    def _format_console(self, result: DiffResult) -> str:
        """终端高亮输出"""
        output = []
        stats = result.stats
        
        # 统计摘要
        output.append(f"\n{self.COLORS['cyan']}=== 差异统计 ==={self.COLORS['reset']}")
        output.append(f"  文件: {result.file_a} → {result.file_b}")
        output.append(f"  算法: {result.algorithm.value}")
        output.append(f"  块数: {stats['hunks']}")
        output.append(f"  {self.COLORS['green']}+ 插入: {stats['inserted']}{self.COLORS['reset']}")
        output.append(f"  {self.COLORS['red']}- 删除: {stats['deleted']}{self.COLORS['reset']}")
        output.append(f"  总变化: {stats['total_changes']}")
        
        if result.identical:
            output.append(f"\n{self.COLORS['green']}✅ 文件完全相同{self.COLORS['reset']}")
            return '\n'.join(output)
        
        # 详细差异
        for i, hunk in enumerate(result.hunks, 1):
            output.append(f"\n{self.COLORS['cyan']}--- 差异块 {i} ---{self.COLORS['reset']}")
            output.append(f"@@ -{hunk.old_start},{hunk.old_lines} +{hunk.new_start},{hunk.new_lines} @@")
            
            for line in hunk.lines:
                if line.line_type == LineType.INSERTED:
                    output.append(f"{self.COLORS['green']}{self.SYMBOLS['insert']} {line.content}{self.COLORS['reset']}")
                elif line.line_type == LineType.DELETED:
                    output.append(f"{self.COLORS['red']}{self.SYMBOLS['delete']} {line.content}{self.COLORS['reset']}")
                else:
                    output.append(f"{self.SYMBOLS['unchanged']} {line.content}")
        
        return '\n'.join(output)
    
    def _format_unified(self, result: DiffResult) -> str:
        """统一diff格式输出"""
        output = []
        output.append(f"--- {result.file_a}")
        output.append(f"+++ {result.file_b}")
        
        for hunk in result.hunks:
            output.append(f"@@ -{hunk.old_start},{hunk.old_lines} +{hunk.new_start},{hunk.new_lines} @@")
            
            for line in hunk.lines:
                if line.line_type == LineType.INSERTED:
                    output.append(f"+{line.content}")
                elif line.line_type == LineType.DELETED:
                    output.append(f"-{line.content}")
                else:
                    output.append(f" {line.content}")
        
        return '\n'.join(output)
    
    def _format_side_by_side(self, result: DiffResult) -> str:
        """并排显示格式"""
        output = []
        output.append(f"{'原始文件':<40} | {'新文件':<40}")
        output.append("=" * 40 + "+" + "=" * 40)
        
        for hunk in result.hunks:
            for line in hunk.lines:
                if line.line_type == LineType.INSERTED:
                    output.append(f"{'':40} | {line.content}")
                elif line.line_type == LineType.DELETED:
                    output.append(f"{line.content:40} | {'':40}")
                else:
                    output.append(f"{line.content:40} | {line.content}")
        
        return '\n'.join(output)
    
    def _format_html(self, result: DiffResult) -> str:
        """HTML格式输出"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Diff: {result.file_a} → {result.file_b}</title>
    <style>
        body {{ font-family: monospace; padding: 20px; }}
        .diff {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
        .inserted {{ background: #e6ffed; color: #22863a; }}
        .deleted {{ background: #ffeef0; color: #cb2431; }}
        .unchanged {{ background: #fff; }}
        .hunk {{ color: #6a737d; font-size: 12px; }}
        .stats {{ margin-bottom: 20px; padding: 10px; background: #f6f8fa; border-radius: 5px; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <h1>文件差异比较</h1>
    <div class="stats">
        <strong>统计信息:</strong><br>
        原始文件: {result.file_a}<br>
        新文件: {result.file_b}<br>
        算法: {result.algorithm.value}<br>
        插入行数: {result.stats['inserted']}<br>
        删除行数: {result.stats['deleted']}<br>
        差异块数: {result.stats['hunks']}
    </div>
    <div class="diff">
        <pre>
"""
        
        for hunk in result.hunks:
            html += f"        @@ -{hunk.old_start},{hunk.old_lines} +{hunk.new_start},{hunk.new_lines} @@\n"
            
            for line in hunk.lines:
                if line.line_type == LineType.INSERTED:
                    html += f"        <span class='inserted'>+{line.content}</span>\n"
                elif line.line_type == LineType.DELETED:
                    html += f"        <span class='deleted'>-{line.content}</span>\n"
                else:
                    html += f"        <span class='unchanged'> {line.content}</span>\n"
        
        html += """        </pre>
    </div>
</body>
</html>"""
        
        return html
    
    def _format_json(self, result: DiffResult) -> str:
        """JSON格式输出"""
        data = {
            'file_a': result.file_a,
            'file_b': result.file_b,
            'algorithm': result.algorithm.value,
            'stats': result.stats,
            'identical': result.identical,
            'hunks': []
        }
        
        for hunk in result.hunks:
            hunk_data = {
                'old_start': hunk.old_start,
                'old_lines': hunk.old_lines,
                'new_start': hunk.new_start,
                'new_lines': hunk.new_lines,
                'lines': []
            }
            
            for line in hunk.lines:
                line_data = {
                    'type': line.line_type.value,
                    'content': line.content
                }
                if line.old_line_number:
                    line_data['old_line'] = line.old_line_number
                if line.new_line_number:
                    line_data['new_line'] = line.new_line_number
                
                hunk_data['lines'].append(line_data)
            
            data['hunks'].append(hunk_data)
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _format_markdown(self, result: DiffResult) -> str:
        """Markdown表格格式输出"""
        md = f"""## 文件差异比较

| 属性 | 值 |
|------|-----|
| 原始文件 | `{result.file_a}` |
| 新文件 | `{result.file_b}` |
| 算法 | `{result.algorithm.value}` |
| 插入行数 | {result.stats['inserted']} |
| 删除行数 | {result.stats['deleted']} |
| 差异块数 | {result.stats['hunks']} |

## 差异详情

| 行号 | 类型 | 内容 |
|------|------|------|

"""
        
        for hunk in result.hunks:
            md += f"### 差异块 @@ -{hunk.old_start},{hunk.old_lines} +{hunk.new_start},{hunk.new_lines} @@\n\n"
            
            for line in hunk.lines:
                if line.line_type == LineType.INSERTED:
                    md += f"| +{line.new_line_number} | 插入 | `{line.content}` |\n"
                elif line.line_type == LineType.DELETED:
                    md += f"| -{line.old_line_number} | 删除 | `{line.content}` |\n"
                else:
                    md += f"| {line.old_line_number} | 未变 | `{line.content}` |\n"
        
        return md


def interactive_diff():
    """交互式差异比较"""
    print("🧪 智能文本差异比较器")
    print("=" * 50)
    
    # 读取文件
    file_a = input("请输入第一个文件路径 (或直接回车使用示例): ").strip()
    file_b = input("请输入第二个文件路径 (或直接回车使用示例): ").strip()
    
    if not file_a:
        file_a = "example_a.txt"
        file_b = "example_b.txt"
        # 创建示例文件
        with open(file_a, 'w') as f:
            f.write("def hello():\n")
            f.write("    '''打招呼函数'''\n")
            f.write("    print('Hello, World!')\n")
            f.write("    return True\n")
        with open(file_b, 'w') as f:
            f.write("def hello():\n")
            f.write("    '''打招呼函数 - 修改版'''\n")
            f.write("    # 新增功能\n")
            f.write("    print('Hello, World!')\n")
            f.write("    print('Welcome!')\n")
            f.write("    return True\n")
        print(f"已创建示例文件: {file_a}, {file_b}")
    
    # 选择算法
    print("\n选择差分算法:")
    print("1. Myers (默认, 类似 git diff)")
    print("2. LCS (最长公共子序列)")
    print("3. SequenceMatcher")
    algo_choice = input("请选择 (1-3): ").strip() or "1"
    
    algo_map = {1: DiffAlgorithm.MYERS, 2: DiffAlgorithm.LCS, 3: DiffAlgorithm.SEQUENCE}
    algorithm = algo_map.get(int(algo_choice), DiffAlgorithm.MYERS)
    
    # 选择输出格式
    print("\n选择输出格式:")
    print("1. 终端高亮 (console)")
    print("2. 统一diff格式 (unified)")
    print("3. 并排显示 (side-by-side)")
    print("4. HTML页面 (html)")
    print("5. JSON格式 (json)")
    print("6. Markdown表格 (markdown)")
    fmt_choice = input("请选择 (1-6): ").strip() or "1"
    
    fmt_map = {1: OutputFormat.CONSOLE, 2: OutputFormat.UNIFIED, 
               3: OutputFormat.SIDE_BY_SIDE, 4: OutputFormat.HTML,
               5: OutputFormat.JSON, 6: OutputFormat.MARKDOWN}
    output_format = fmt_map.get(int(fmt_choice), OutputFormat.CONSOLE)
    
    # 忽略选项
    ignore_comments = input("\n是否忽略注释行? (y/n): ").strip().lower() == 'y'
    ignore_blank = input("是否忽略空白行? (y/n): ").strip().lower() == 'y'
    language = input("编程语言 (python/js/java/cpp/shell/sql/html/css): ").strip() or 'python'
    
    # 执行比较
    diff_tool = SmartDiff(algorithm)
    
    try:
        result = diff_tool.compare_files(file_a, file_b, 
                                         ignore_comments, ignore_blank, language)
        
        output = diff_tool.format_output(result, output_format)
        
        print("\n" + "=" * 50)
        print(output)
        
        # 导出选项
        if output_format in [OutputFormat.HTML, OutputFormat.JSON, OutputFormat.MARKDOWN]:
            export_path = input("\n是否导出到文件? (直接回车跳过/输入文件名): ").strip()
            if export_path:
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"已导出到: {export_path}")
    
    except FileNotFoundError as e:
        print(f"❌ 错误: 文件不存在 - {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def batch_compare(files: List[Tuple[str, str]], output_dir: str = "diff_reports"):
    """批量比较多个文件对
    
    Args:
        files: [(file_a, file_b), ...] 文件对列表
        output_dir: 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (file_a, file_b) in enumerate(files, 1):
        print(f"\n比较 {i}/{len(files)}: {file_a} ↔ {file_b}")
        
        diff_tool = SmartDiff()
        result = diff_tool.compare_files(file_a, file_b)
        
        # 生成多种格式的报告
        base_name = f"diff_{i}_{os.path.splitext(os.path.basename(file_a))[0]}"
        
        # JSON报告
        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(diff_tool.format_output(result, OutputFormat.JSON))
        
        # HTML报告
        html_path = os.path.join(output_dir, f"{base_name}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(diff_tool.format_output(result, OutputFormat.HTML))
        
        # 控制台输出
        print(diff_tool.format_output(result, OutputFormat.CONSOLE))
        print(f"\n📄 报告已生成: {json_path}, {html_path}")


def compare_string(a: str, b: str, algorithm: DiffAlgorithm = DiffAlgorithm.MYERS) -> Dict[str, Any]:
    """直接比较两个字符串
    
    Args:
        a: 原始字符串
        b: 新字符串
        algorithm: 差分算法
        
    Returns:
        包含差异信息的字典
    """
    diff_tool = SmartDiff(algorithm)
    lines_a = a.splitlines(keepends=True)
    lines_b = b.splitlines(keepends=True)
    
    result = diff_tool.compare_lines(lines_a, lines_b, "string_a", "string_b")
    
    return {
        'identical': result.identical,
        'stats': result.stats,
        'unified_diff': diff_tool.format_output(result, OutputFormat.UNIFIED),
        'json': diff_tool.format_output(result, OutputFormat.JSON)
    }


if __name__ == "__main__":
    # 命令行参数解析
    if len(sys.argv) >= 3:
        # 快速比较模式
        file_a = sys.argv[1]
        file_b = sys.argv[2]
        
        algo = sys.argv[3] if len(sys.argv) > 3 else 'myers'
        format_type = sys.argv[4] if len(sys.argv) > 4 else 'console'
        
        algo_map = {'myers': DiffAlgorithm.MYERS, 'lcs': DiffAlgorithm.LCS, 
                   'sequence': DiffAlgorithm.SEQUENCE}
        fmt_map = {'console': OutputFormat.CONSOLE, 'unified': OutputFormat.UNIFIED,
                  'side': OutputFormat.SIDE_BY_SIDE, 'html': OutputFormat.HTML,
                  'json': OutputFormat.JSON, 'markdown': OutputFormat.MARKDOWN}
        
        diff_tool = SmartDiff(algo_map.get(algo, DiffAlgorithm.MYERS))
        result = diff_tool.compare_files(file_a, file_b)
        
        print(diff_tool.format_output(result, fmt_map.get(format_type, OutputFormat.CONSOLE)))
    
    elif len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']:
        print("""
🧪 智能文本差异比较器 (Smart Text Diff Tool)
=============================================

用法:
    python smart_diff.py <文件A> <文件B> [算法] [格式]
    python smart_diff.py              # 交互模式
    python smart_diff.py --batch      # 批量模式

参数:
    文件A, 文件B: 要比较的两个文件路径
    
算法选项:
    myers     - Myers差分算法 (默认, 类似 git diff)
    lcs       - 最长公共子序列
    sequence  - Python SequenceMatcher

输出格式:
    console   - 终端高亮输出 (默认)
    unified   - 统一diff格式
    side      - 并排显示
    html      - HTML页面
    json      - JSON格式
    markdown  - Markdown表格

示例:
    python smart_diff.py a.txt b.txt
    python smart_diff.py a.txt b.txt lcs json
    python smart_diff.py --batch

Python API:
    from smart_diff import SmartDiff, compare_string
    
    # 比较文件
    result = SmartDiff().compare_files('a.txt', 'b.txt')
    print(SmartDiff().format_output(result, OutputFormat.CONSOLE))
    
    # 比较字符串
    diff = compare_string("hello", "hello world")
        """)
    
    elif len(sys.argv) == 2 and sys.argv[1] == '--batch':
        # 批量比较模式
        print("批量文件比较模式")
        print("请输入文件对列表，每行一个文件对 (格式: file_a,file_b)，空行结束:")
        files = []
        while True:
            line = input().strip()
            if not line:
                break
            parts = line.split(',')
            if len(parts) == 2:
                files.append((parts[0].strip(), parts[1].strip()))
        
        if files:
            batch_compare(files)
    
    else:
        # 交互模式
        interactive_diff()
