#!/usr/bin/env python3
"""
Code Complexity Visualizer - ASCII Charts
分析代码复杂度并生成ASCII可视化图表
"""

import os
import re
import sys
from collections import defaultdict
from enum import Enum

class ComplexityLevel(Enum):
    LOW = "🟢"
    MEDIUM = "🟡"
    HIGH = "🟠"
    CRITICAL = "🔴"

def detect_language(filename):
    ext = os.path.splitext(filename)[1].lower()
    lang_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
    }
    return lang_map.get(ext, 'Unknown')

def extract_functions_php(content):
    """提取PHP函数"""
    pattern = r'(?:function\s+)?(\w+)\s*\([^)]*\)\s*\{'
    return re.findall(pattern, content)

def extract_functions_js(content):
    """提取JS/TS函数"""
    pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=|(\w+)\s*=\s*(?:async\s*)?function|(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)'
    matches = re.findall(pattern, content)
    funcs = []
    for m in matches:
        funcs.extend([f for f in m if f])
    return funcs

def extract_functions_python(content):
    """提取Python函数"""
    pattern = r'def\s+(\w+)\s*\('
    return re.findall(pattern, content)

def extract_functions_java(content):
    """提取Java函数"""
    pattern = r'(?:public|private|protected|static|\s)+(?:static\s+)?(?:void|int|String|boolean|float|double|List|Map|\w+)\s+(\w+)\s*\('
    return re.findall(pattern, content)

def count_cyclomatic_complexity(content):
    """计算圈复杂度"""
    patterns = [
        r'\bif\b', r'\belseif\b', r'\belif\b',
        r'\bfor\b', r'\bwhile\b', r'\bdo\b',
        r'\bcase\b', r'\bcatch\b',
        r'\b\?\s*.*\s*:\s*',  # ternary
        r'\b&&\b', r'\b\|\|',
        r'\bassert\b', r'\braise\b',
    ]
    count = 1  # 基础复杂度
    for pattern in patterns:
        count += len(re.findall(pattern, content))
    return count

def analyze_file(filepath):
    """分析单个文件"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lang = detect_language(filepath)
    lines = len(content.split('\n'))
    
    # 提取函数
    if lang == 'Python':
        functions = extract_functions_python(content)
    elif lang in ['JavaScript', 'TypeScript']:
        functions = extract_functions_js(content)
    elif lang == 'Java':
        functions = extract_functions_java(content)
    elif lang == 'PHP':
        functions = extract_functions_php(content)
    else:
        functions = []
    
    complexity = count_cyclomatic_complexity(content)
    func_count = len(functions)
    
    return {
        'file': os.path.basename(filepath),
        'language': lang,
        'lines': lines,
        'functions': func_count,
        'complexity': complexity,
        'complexity_per_func': round(complexity / max(func_count, 1), 2),
    }

def get_complexity_level(complexity):
    if complexity <= 10:
        return ComplexityLevel.LOW
    elif complexity <= 20:
        return ComplexityLevel.MEDIUM
    elif complexity <= 50:
        return ComplexityLevel.HIGH
    else:
        return ComplexityLevel.CRITICAL

def draw_bar_chart(data, title, value_key, max_value=None):
    """绘制ASCII柱状图"""
    if not data:
        return ""
    
    max_val = max_value or max(d[value_key] for d in data)
    scale = 40 / max_val if max_val > 0 else 1
    
    lines = [f"\n📊 {title}", "─" * 50]
    
    for item in sorted(data, key=lambda x: x[value_key], reverse=True)[:10]:
        bar_len = int(item[value_key] * scale)
        bar = "█" * bar_len
        emoji = get_complexity_level(item[value_key]).value
        lines.append(f"{emoji} {item['file'][:20]:20s} │ {bar} {item[value_key]:4d}")
    
    return '\n'.join(lines)

def draw_pie_chart(data):
    """绘制ASCII饼图（简化版）"""
    if not data:
        return ""
    
    total = sum(d['functions'] for d in data)
    if total == 0:
        return ""
    
    categories = {
        'Low': 0,
        'Medium': 0,
        'High': 0,
        'Critical': 0,
    }
    
    for item in data:
        level = get_complexity_level(item['complexity']).name
        categories[level] += item['functions']
    
    lines = [f"\n🍰 Function Distribution by Complexity", "─" * 35]
    for cat, count in categories.items():
        if count > 0:
            pct = count / total * 100
            bar = "▓" * int(pct / 2) + "░" * (50 - int(pct / 2))
            lines.append(f"{cat:8s}: {bar} {pct:5.1f}% ({count})")
    
    return '\n'.(lines)

def generate_report(filepaths):
    """生成完整的分析报告"""
    results = []
    for fp in filepaths:
        if os.path.isfile(fp):
            result = analyze_file(fp)
            if result:
                results.append(result)
    
    if not results:
        print("❌ No valid files found!")
        return
    
    total_lines = sum(r['lines'] for r in results)
    total_funcs = sum(r['functions'] for r in results)
    avg_complexity = sum(r['complexity'] for r in results) / len(results)
    
    # 统计
    lang_stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'funcs': 0})
    for r in results:
        lang_stats[r['language']]['files'] += 1
        lang_stats[r['language']]['lines'] += r['lines']
        lang_stats[r['language']]['funcs'] += r['functions']
    
    # 打印报告
    print("\n" + "═" * 60)
    print("📈 CODE COMPLEXITY VISUALIZER")
    print("═" * 60)
    
    print(f"\n📌 Summary")
    print(f"   Files analyzed: {len(results)}")
    print(f"   Total lines: {total_lines:,}")
    print(f"   Total functions: {total_funcs}")
    print(f"   Avg complexity: {avg_complexity:.1f}")
    
    print(f"\n💻 Languages")
    for lang, stats in sorted(lang_stats.items(), key=lambda x: x[1]['lines'], reverse=True):
        print(f"   {lang:12s}: {stats['files']:3d} files, {stats['lines']:5d} lines, {stats['funcs']:3d} functions")
    
    # 可视化
    print(draw_bar_chart(results, "Files by Complexity", "complexity"))
    print(draw_bar_chart(results, "Files by Lines of Code", "lines"))
    print(draw_bar_chart(results, "Files by Function Count", "functions"))
    
    # Top complex files
    print(f"\n🏆 Top 5 Most Complex Files")
    print("─" * 50)
    for i, item in enumerate(sorted(results, key=lambda x: x['complexity'], reverse=True)[:5], 1):
        level = get_complexity_level(item['complexity'])
        print(f"{i}. {level.value} {item['file']} ({item['language']}) - Complexity: {item['complexity']}, Lines: {item['lines']}")
    
    print("\n" + "═" * 60)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # 默认分析当前目录的脚本
        filepaths = []
        for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.go']:
            filepaths.extend([f for f in os.listdir('.') if f.endswith(ext)])
        
        if not filepaths:
            print("Usage: python code_complexity_visualizer.py <file1> <file2> ...")
            print("Example: python code_complexity_visualizer.py src/main.py src/utils.py")
            sys.exit(1)
    else:
        filepaths = sys.argv[1:]
    
    generate_report(filepaths)
