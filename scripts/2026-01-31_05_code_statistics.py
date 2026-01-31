"""
Day 5: Code Statistics Analyzer
A powerful tool to analyze code files and count various metrics.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Language patterns for comment detection
COMMENT_PATTERNS = {
    '.py': {'single': '#', 'multi': ('"""', '"""')},
    '.js': {'single': '//', 'multi': ('/*', '*/')},
    '.ts': {'single': '//', 'multi': ('/*', '*/')},
    '.java': {'single': '//', 'multi': ('/*', '*/')},
    '.cpp': {'single': '//', 'multi': ('/*', '*/')},
    '.c': {'single': '//', 'multi': ('/*', '*/')},
    '.go': {'single': '//', 'multi': ('/*', '*/')},
    '.rs': {'single': '//', 'multi': ('/*', '*/')},
    '.rb': {'single': '#', 'multi': ('=begin', '=end')},
    '.sh': {'single': '#', 'multi': None},
    '.md': {'single': None, 'multi': ('<!--', '-->')},
    '.html': {'single': None, 'multi': ('<!--', '-->')},
    '.css': {'single': None, 'multi': ('/*', '*/')},
}

# File type icons
FILE_ICONS = {
    '.py': '🐍',
    '.js': '📜',
    '.ts': '📘',
    '.java': '☕',
    '.cpp': '⚙️',
    '.c': '⚙️',
    '.go': '🐹',
    '.rs': '🦀',
    '.rb': '💎',
    '.sh': '💻',
    '.md': '📝',
    '.html': '🌐',
    '.css': '🎨',
    '.json': '📋',
    '.yaml': '📄',
    '.yml': '📄',
}

def get_file_stats(file_path: str) -> Dict:
    """Analyze a single file and return statistics."""
    ext = Path(file_path).suffix.lower()
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    non_empty_lines = len([l for l in lines if l.strip()])
    total_chars = sum(len(l) for l in lines)
    total_words = sum(len(l.split()) for l in lines if l.strip())
    
    # Count functions/methods
    func_patterns = {
        '.py': r'^def\s+\w+|class\s+\w+',
        '.js': r'(?:function\s+\w+|const\s+\w+\s*=|class\s+\w+|=>)',
        '.ts': r'(?:function\s+\w+|const\s+\w+\s*=|class\s+\w+|=>)',
        '.java': r'(?:public|private|protected)\s+(?:static\s+)?\w+\s*\(',
        '.cpp': r'(?:\w+\s+\w+\s*\(|void\s+\w+|int\s+\w+)',
        '.c': r'(?:\w+\s+\w+\s*\(|void\s+\w+|int\s+\w+)',
        '.go': r'func\s+\w+|func\s+\(',
        '.rs': r'fn\s+\w+|impl\s+\w+',
        '.rb': r'def\s+\w+|class\s+\w+',
        '.sh': r'^function\s+\w+|^()\s*{',
    }
    
    func_count = 0
    pattern = func_patterns.get(ext)
    if pattern:
        func_count = len(re.findall(pattern, ''.join(lines), re.MULTILINE))
    
    # Count comments
    comment_lines = 0
    pattern_info = COMMENT_PATTERNS.get(ext)
    if pattern_info:
        single = pattern_info['single']
        multi = pattern_info['multi']
        
        in_multi = False
        for line in lines:
            stripped = line.strip()
            
            if multi and not in_multi:
                if stripped.startswith(multi[0]):
                    if not stripped.endswith(multi[1]) or stripped == multi[0]:
                        in_multi = True
                        comment_lines += 1
                        continue
            
            if in_multi:
                comment_lines += 1
                if stripped.endswith(multi[1]):
                    in_multi = False
                continue
            
            if single and stripped.startswith(single):
                comment_lines += 1
    
    return {
        'total_lines': total_lines,
        'non_empty_lines': non_empty_lines,
        'total_chars': total_chars,
        'total_words': total_words,
        'functions': func_count,
        'comments': comment_lines,
    }

def analyze_directory(path: str, recursive: bool = True) -> Dict[str, Dict]:
    """Analyze all code files in a directory."""
    stats = {}
    path_obj = Path(path)
    
    files = path_obj.rglob('*') if recursive else path_obj.glob('*')
    
    for file_path in files:
        if file_path.is_file() and COMMENT_PATTERNS.get(file_path.suffix.lower()):
            try:
                file_stats = get_file_stats(str(file_path))
                stats[str(file_path)] = file_stats
            except Exception:
                continue
    
    return stats

def format_size(size: int) -> str:
    """Format size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"

def print_report(stats: Dict[str, Dict], title: str = "Code Statistics Report"):
    """Pretty print the statistics report."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")
    
    total_files = len(stats)
    total_lines = sum(s['total_lines'] for s in stats.values())
    total_funcs = sum(s['functions'] for s in stats.values())
    total_comments = sum(s['comments'] for s in stats.values())
    total_chars = sum(s['total_chars'] for s in stats.values())
    
    print(f"📁 Files analyzed: {total_files}")
    print(f"📝 Total lines: {total_lines:,}")
    print(f"⚡ Functions/methods: {total_funcs:,}")
    print(f"💬 Comment lines: {total_comments:,}")
    print(f"📊 Total characters: {total_chars:,}")
    print(f"💾 Total size: {format_size(total_chars)}")
    print(f"\n📈 Code coverage (comments): {total_comments/total_lines*100:.1f}%" if total_lines > 0 else "")
    
    print(f"\n{'─'*60}")
    print(f"{'File':<40} {'Lines':>8} {'Funcs':>6} {'Comments':>8}")
    print(f"{'─'*60}")
    
    sorted_files = sorted(stats.items(), key=lambda x: x[1]['total_lines'], reverse=True)
    
    for file_path, file_stats in sorted_files:
        icon = FILE_ICONS.get(Path(file_path).suffix.lower(), '📄')
        short_path = Path(file_path).name if len(file_path) > 40 else file_path
        print(f"{icon} {short_path:<38} {file_stats['total_lines']:>7} {file_stats['functions']:>6} {file_stats['comments']:>8}")
    
    print(f"{'─'*60}\n")

# Demo usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            stats = {target: get_file_stats(target)}
            print_report(stats, f"Statistics for: {target}")
        elif os.path.isdir(target):
            stats = analyze_directory(target)
            print_report(stats, f"Statistics for directory: {target}")
        else:
            print(f"❌ Path not found: {target}")
    else:
        # Demo with current file
        print("🔍 Code Statistics Analyzer - Day 5")
        print("Usage: python code_statistics.py <path_to_file_or_directory>")
        print("\n📋 Supported file types:")
        for ext in sorted(COMMENT_PATTERNS.keys()):
            icon = FILE_ICONS.get(ext, '📄')
            print(f"  {icon} {ext}")
