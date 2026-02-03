#!/usr/bin/env python3
"""
CSV to Markdown Table Converter
自动将CSV文件转换为格式化的Markdown表格

功能:
- 自动检测分隔符（逗号、制表符、分号等）
- 支持自定义表头
- 自动对齐数字（右对齐）和文本（左对齐）
- 支持指定最大列宽
- 批量转换目录下的所有CSV文件
"""

import csv
import os
import argparse
import sys
from pathlib import Path
from typing import List, Optional


class CSVToMarkdownConverter:
    """CSV到Markdown表格转换器"""
    
    def __init__(self, max_width: int = 50):
        self.max_width = max_width
    
    def detect_delimiter(self, file_path: str) -> str:
        """自动检测CSV文件的分隔符"""
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = [f.readline() for _ in range(min(5, os.path.getsize(file_path)))]
            delimiters = [',', '\t', ';', '|', ':']
            best_delimiter = ','
            max_cols = 0
            
            for delim in delimiters:
                for line in first_lines:
                    if line.strip():
                        cols = line.count(delim) + 1
                        if cols > max_cols:
                            max_cols = cols
                            best_delimiter = delim
            
            return best_delimiter
    
    def truncate_text(self, text: str, max_len: int) -> str:
        """截断过长的文本"""
        text = str(text).strip()
        if len(text) > max_len:
            return text[:max_len - 3] + '...'
        return text
    
    def detect_column_types(self, rows: List[List[str]]) -> List[str]:
        """检测每列的数据类型（数字或文本）"""
        if not rows:
            return []
        
        num_cols = len(rows[0])
        is_numeric = [True] * num_cols
        
        for row in rows[:10]:  # 只检查前10行
            for i, cell in enumerate(row):
                if i >= num_cols:
                    break
                cell = cell.strip()
                if cell and i < len(is_numeric):
                    try:
                        float(cell.replace(',', '').replace('%', ''))
                    except ValueError:
                        is_numeric[i] = False
        
        return ['r' if is_numeric[i] else 'l' for i in range(num_cols)]
    
    def calculate_column_widths(self, rows: List[List[str]]) -> List[int]:
        """计算每列的最大宽度"""
        if not rows:
            return []
        
        num_cols = len(rows[0])
        widths = [0] * num_cols
        
        for row in rows:
            for i, cell in enumerate(row):
                if i < num_cols:
                    widths[i] = max(widths[i], len(cell.strip()))
        
        # 应用最大宽度限制
        return [min(w, self.max_width) for w in widths]
    
    def convert(self, csv_path: str, output_path: Optional[str] = None,
                has_header: bool = True, custom_header: Optional[List[str]] = None) -> str:
        """将CSV转换为Markdown表格"""
        
        delimiter = self.detect_delimiter(csv_path)
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
        
        if not rows:
            return ""
        
        # 处理表头
        if has_header:
            header = [self.truncate_text(cell, self.max_width) for cell in rows[0]]
            data_rows = rows[1:]
        elif custom_header:
            header = custom_header
            data_rows = rows
        else:
            header = [f"Column_{i+1}" for i in range(len(rows[0]))]
            data_rows = rows
        
        # 计算列宽
        all_rows = [header] + data_rows
        col_widths = self.calculate_column_widths(all_rows)
        col_types = self.detect_column_types(data_rows)
        
        # 生成分隔行
        def make_separator(widths: List[int], types: List[str]) -> str:
            parts = ['|']
            for w, t in zip(widths, types):
                parts.append('-' * (w + 2))
            parts.append('|')
            return ''.join(parts)
        
        separator = make_separator(col_widths, col_types)
        
        # 生成格式化行
        def format_row(row: List[str], widths: List[int], types: List[str]) -> str:
            cells = []
            for i, cell in enumerate(row):
                if i >= len(widths):
                    break
                cell = self.truncate_text(cell, widths[i])
                width = widths[i]
                if i < len(types) and types[i] == 'r':
                    cells.append(f" {cell:>{width}} ")
                else:
                    cells.append(f" {cell:<{width}} ")
            return '|' + '|'.join(cells) + '|'
        
        # 构建Markdown表格
        lines = []
        lines.append(format_row(header, col_widths, col_types))
        lines.append(separator)
        
        for row in data_rows:
            lines.append(format_row(row, col_widths, col_types))
        
        markdown_content = '\n'.join(lines)
        
        # 如果指定了输出路径，写入文件
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        return markdown_content
    
    def convert_directory(self, input_dir: str, output_dir: Optional[str] = None,
                         recursive: bool = False) -> dict:
        """批量转换目录下的所有CSV文件"""
        
        input_path = Path(input_dir)
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
        pattern = '**/*.csv' if recursive else '*.csv'
        
        for csv_file in input_path.glob(pattern):
            try:
                if output_dir:
                    relative_name = csv_file.stem
                    out_file = output_path / f"{relative_name}.md"
                    self.convert(str(csv_file), str(out_file))
                else:
                    self.convert(str(csv_file))
                
                results['success'].append(str(csv_file))
                print(f"✓ 转换成功: {csv_file.name}")
            
            except Exception as e:
                results['failed'].append({'file': str(csv_file), 'error': str(e)})
                print(f"✗ 转换失败: {csv_file.name} - {e}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='CSV to Markdown Table Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s data.csv                    # 转换单个文件
  %(prog)s data.csv -o output.md       # 指定输出文件
  %(prog)s data/ -o markdown/          # 批量转换目录
  %(prog)s data/ -r -o markdown/       # 递归转换所有子目录
        """
    )
    
    parser.add_argument('input', help='输入CSV文件或目录')
    parser.add_argument('-o', '--output', help='输出文件或目录')
    parser.add_argument('-w', '--max-width', type=int, default=50,
                        help='最大列宽 (默认: 50)')
    parser.add_argument('-n', '--no-header', action='store_true',
                        help='CSV文件没有表头')
    parser.add_argument('-H', '--header', nargs='+',
                        help='指定自定义表头 (空格分隔)')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='递归处理子目录')
    parser.add_argument('-v', '--version', action='version', version='1.0.0')
    
    args = parser.parse_args()
    
    converter = CSVToMarkdownConverter(max_width=args.max_width)
    
    if os.path.isfile(args.input):
        # 单文件转换
        output = converter.convert(
            args.input,
            output_path=args.output,
            has_header=not args.no_header,
            custom_header=args.header
        )
        
        if not args.output:
            print(output)
        else:
            print(f"✓ 已保存到: {args.output}")
    
    elif os.path.isdir(args.input):
        # 批量转换
        results = converter.convert_directory(
            args.input,
            output_dir=args.output,
            recursive=args.recursive
        )
        
        print(f"\n汇总:")
        print(f"  成功: {len(results['success'])}")
        print(f"  失败: {len(results['failed'])}")
    
    else:
        print(f"错误: 找不到文件或目录: {args.input}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
