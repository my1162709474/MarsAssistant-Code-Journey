#!/usr/bin/env python3
"""
📊 Code Statistics Analyzer
代码统计分析仪 - Day 97

统计代码库的各种指标：
- 文件数量、行数（代码/注释/空行）
- 各语言占比
- 复杂度估算
- 文件大小统计

Usage:
    python code_stats_analyzer.py [path]
    python code_stats_analyzer.py . --verbose
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# 支持的文件扩展名和对应语言
LANGUAGE_MAP = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.html': 'HTML',
    '.css': 'CSS',
    '.json': 'JSON',
    '.md': 'Markdown',
    '.txt': 'Text',
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.zsh': 'Zsh',
    '.yml': 'YAML',
    '.yaml': 'YAML',
    '.xml': 'XML',
    '.csv': 'CSV',
    '.png': 'PNG',
    '.jpg': 'JPEG',
    '.gif': 'GIF',
    '.svg': 'SVG',
    '.ico': 'Icon',
    '.pyc': 'Python Bytecode',
    '.db': 'Database',
    '.log': 'Log',
    '.gitignore': 'Git Ignore',
    '.env': 'Environment',
}

# 代码文件扩展名（用于统计代码行数）
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.css', '.sh', '.bash', '.zsh',
    '.yml', '.yaml', '.xml', '.json', '.md', '.txt'
}

def get_language(filename):
    """根据文件名获取语言类型"""
    ext = Path(filename).suffix.lower()
    return LANGUAGE_MAP.get(ext, 'Other')

def is_code_file(filename):
    """判断是否为代码文件"""
    ext = Path(filename).suffix.lower()
    return ext in CODE_EXTENSIONS

def count_lines(content):
    """统计代码行数、注释行、空行"""
    lines = content.split('\n')
    total = len(lines)
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    
    in_multiline_comment = False
    
    for line in lines:
        stripped = line.strip()
        
        # 检查多行注释开始/结束
        if '"""' in stripped or "'''" in stripped:
            if in_multiline_comment:
                in_multiline_comment = False
            else:
                in_multiline_comment = True
            comment_lines += 1
            continue
        
        if in_multiline_comment:
            comment_lines += 1
            continue
        
        # 空行
        if not stripped:
            blank_lines += 1
            continue
        
        # 单行注释
        if stripped.startswith('#') or stripped.startswith('//'):
            comment_lines += 1
            continue
        
        code_lines += 1
    
    return total, code_lines, comment_lines, blank_lines

def estimate_complexity(content):
    """估算代码复杂度（基于分支和循环）"""
    complexity = 1  # 基础复杂度
    
    keywords = ['if', 'elif', 'else', 'for', 'while', 'and', 'or', 'try', 'except', 'finally', 'with']
    for keyword in keywords:
        complexity += content.lower().count(f' {keyword} ')
        complexity += content.lower().count(f'{keyword}(')
    
    return complexity

def analyze_path(path, verbose=False):
    """分析指定路径的代码统计"""
    path = Path(path)
    
    if not path.exists():
        print(f"❌ 路径不存在: {path}")
        return
    
    stats = {
        'total_files': 0,
        'code_files': 0,
        'total_lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'total_size': 0,
        'language_stats': defaultdict(lambda: {'files': 0, 'lines': 0, 'size': 0}),
        'complexity_total': 0,
    }
    
    files_analyzed = []
    
    for file_path in path.rglob('*'):
        if file_path.is_file():
            stats['total_files'] += 1
            
            try:
                size = file_path.stat().st_size
                stats['total_size'] += size
                
                rel_path = file_path.relative_to(path)
                ext = file_path.suffix.lower()
                lang = get_language(file_path.name)
                
                stats['language_stats'][lang]['files'] += 1
                stats['language_stats'][lang]['size'] += size
                
                if is_code_file(file_path.name):
                    stats['code_files'] += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        total, code, comment, blank = count_lines(content)
                        stats['total_lines'] += total
                        stats['code_lines'] += code
                        stats['comment_lines'] += comment
                        stats['blank_lines'] += blank
                        
                        stats['language_stats'][lang]['lines'] += total
                        
                        complexity = estimate_complexity(content)
                        stats['complexity_total'] += complexity
                        
                        if verbose:
                            files_analyzed.append({
                                'path': str(rel_path),
                                'lines': total,
                                'code': code,
                                'lang': lang
                            })
                    except Exception as e:
                        pass  # 跳过二进制文件或无法读取的文件
                        
            except Exception as e:
                pass  # 跳过权限问题等
    
    return stats, files_analyzed

def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def print_stats(stats, files_analyzed=None, verbose=False):
    """打印统计结果"""
    print("\n" + "="*60)
    print("📊 代码统计报告")
    print("="*60)
    
    print(f"\n📁 总文件数: {stats['total_files']}")
    print(f"📝 代码文件数: {stats['code_files']}")
    print(f"💾 总大小: {format_size(stats['total_size'])}")
    
    print(f"\n📏 总行数: {stats['total_lines']:,}")
    print(f"   - 代码行: {stats['code_lines']:,} ({stats['code_lines']/max(1,stats['total_lines'])*100:.1f}%)")
    print(f"   - 注释行: {stats['comment_lines']:,} ({stats['comment_lines']/max(1,stats['total_lines'])*100:.1f}%)")
    print(f"   - 空行: {stats['blank_lines']:,} ({stats['blank_lines']/max(1,stats['total_lines'])*100:.1f}%)")
    
    print(f"\n🧠 估算总复杂度: {stats['complexity_total']}")
    print(f"   平均复杂度: {stats['complexity_total']/max(1, stats['code_files']):.2f}")
    
    print("\n🌐 语言分布:")
    print("-"*50)
    
    sorted_langs = sorted(stats['language_stats'].items(), 
                         key=lambda x: x[1]['lines'], reverse=True)
    
    for lang, lang_stats in sorted_langs:
        if lang_stats['files'] > 0:
            pct = lang_stats['lines'] / max(1, stats['total_lines']) * 100
            bar = '█' * int(pct / 2) + '░' * (50 - int(pct / 2))
            print(f"  {lang:15} | {bar[:25]:25} | {lang_stats['files']:3} 文件 | {lang_stats['lines']:5,} 行")
    
    if verbose and files_analyzed:
        print(f"\n📄 详细文件列表 (Top 20):")
        print("-"*60)
        sorted_files = sorted(files_analyzed, key=lambda x: x['lines'], reverse=True)[:20]
        for f in sorted_files:
            print(f"  {f['lines']:5} 行 | {f['lang']:12} | {f['path']}")
    
    print("\n" + "="*60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='代码统计分析仪')
    parser.add_argument('path', nargs='?', default='.', help='要分析的路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细模式')
    parser.add_argument('--json', '-j', action='store_true', help='JSON格式输出')
    
    args = parser.parse_args()
    
    print(f"\n🔍 正在分析: {os.path.abspath(args.path)}")
    
    stats, files_analyzed = analyze_path(args.path, args.verbose)
    
    if args.json:
        import json
        # 转换defaultdict为普通dict
        stats['language_stats'] = {k: dict(v) for k, v in stats['language_stats'].items()}
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print_stats(stats, files_analyzed, args.verbose)
    
    print(f"\n✨ 分析完成！")

if __name__ == '__main__':
    main()
