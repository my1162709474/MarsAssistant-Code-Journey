#!/usr/bin/env python3
"""
Markdown表格生成器
将CSV/TSV数据转换为格式化的Markdown表格
"""

import sys
import base64


def parse_csv(content, delimiter=','):
    """解析CSV/TSV内容"""
    lines = content.strip().split('\n')
    result = []
    for line in lines:
        if line.strip():
            result.append([cell.strip() for cell in line.split(delimiter)])
    return result


def calculate_column_widths(table):
    """计算每列的最大宽度"""
    if not table:
        return []
    num_cols = len(table[0])
    widths = [0] * num_cols
    
    for row in table:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    
    return widths


def format_cell(text, width):
    """格式化单元格，保持间距"""
    return f" {text:<{width-1}} "


def generate_markdown_table(data, has_header=True):
    """生成Markdown表格"""
    if not data:
        return ""
    
    widths = calculate_column_widths(data)
    separator = " | ".join(['-' * (w - 1) for w in widths])
    
    lines = []
    # 表头
    header = " | ".join(format_cell(data[0][i], widths[i]) for i in range(len(widths)))
    lines.append(f"|{header}|")
    lines.append(f"|{separator}|")
    
    # 数据行
    for row in data[1:]:
        row_str = " | ".join(format_cell(row[i], widths[i]) for i in range(len(widths)))
        lines.append(f"|{row_str}|")
    
    return '\n'.join(lines)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python markdown_table_generator.py <文件路径或数据> [--tsv]")
        print("示例:")
        print("  python markdown_table_generator.py data.csv")
        print("  python markdown_table_generator.py 'a,b,c\n1,2,3'")
        print("  python markdown_table_generator.py data.tsv --tsv")
        sys.exit(1)
    
    input_data = sys.argv[1]
    is_tsv = '--tsv' in sys.argv
    
    # 读取文件或直接使用输入
    if input_data.startswith('/') or input_data.startswith('./') or input_data.startswith('../'):
        try:
            with open(input_data, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误: 文件 {input_data} 不存在")
            sys.exit(1)
    else:
        content = input_data
    
    # 解析数据
    delimiter = '\t' if is_tsv else ','
    table = parse_csv(content, delimiter)
    
    if not table:
        print("错误: 无法解析数据")
        sys.exit(1)
    
    # 生成Markdown表格
    markdown_table = generate_markdown_table(table)
    print(markdown_table)
    
    # 保存到文件（可选）
    output_file = "output_table.md"
    with open(output_file, 'w') as f:
        f.write(markdown_table)
    print(f"\n已保存到: {output_file}")


if __name__ == "__main__":
    main()
