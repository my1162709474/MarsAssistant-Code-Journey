#!/usr/bin/env python3
"""
Code Statistics Analyzer
========================
A comprehensive tool for analyzing code repository statistics.

Features:
- Lines of code (LOC) counting
- File type distribution
- Comment ratio analysis
- Function/class detection
- Code complexity estimation
- Multiple language support

Author: AI Code Journey
Date: 2026-02-04
"""

import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class FileStatistics:
    """Statistics for a single file."""
    path: str
    language: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: int = 0
    classes: int = 0
    complexity_score: int = 0


@dataclass
class RepositoryStatistics:
    """Statistics for the entire repository."""
    files: List[FileStatistics] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    total_code_lines: int = 0
    total_comment_lines: int = 0
    total_blank_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    language_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    @property
    def comment_ratio(self) -> float:
        """Calculate overall comment ratio."""
        if self.total_code_lines == 0:
            return 0.0
        return (self.total_comment_lines / self.total_code_lines) * 100
    
    @property
    def average_file_size(self) -> float:
        """Calculate average lines per file."""
        if self.total_files == 0:
            return 0.0
        return self.total_lines / self.total_files


class LanguageConfig:
    """Configuration for programming languages."""
    
    # File extensions to language mapping
    EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C/C++ Header',
        '.hpp': 'C++',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.xml': 'XML',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.md': 'Markdown',
        '.txt': 'Plain Text',
        '.sh': 'Shell',
        '.bash': 'Bash',
        '.zsh': 'Zsh',
        '.dockerfile': 'Dockerfile',
        '.makefile': 'Makefile',
        '.cmake': 'CMake',
    }
    
    # Comment patterns: (single_line_start, multi_line_start, multi_line_end)
    COMMENT_PATTERNS = {
        'Python': ('#', '"""', '"""'),
        'JavaScript': ('//', '/*', '*/'),
        'TypeScript': ('//', '/*', '*/'),
        'Java': ('//', '/*', '*/'),
        'C++': ('//', '/*', '*/'),
        'C': ('//', '/*', '*/'),
        'C/C++ Header': ('//', '/*', '*/'),
        'C#': ('//', '/*', '*/'),
        'Go': ('//', '/*', '*/'),
        'Rust': ('//', '/*', '*/'),
        'Ruby': ('#', '=begin', '=end'),
        'PHP': ('//', '/*', '*/'),
        'Swift': ('//', '/*', '*/'),
        'Kotlin': ('//', '/*', '*/'),
        'Scala': ('//', '/*', '*/'),
        'R': ('#', '#\'', '#\''),
        'SQL': ('--', '/*', '*/'),
        'HTML': ('<!--', '<!--', '-->'),
        'CSS': ('/*', '/*', '*/'),
        'SCSS': ('//', '/*', '*/'),
        'Shell': ('#', '', ''),
        'Bash': ('#', '', ''),
        'Zsh': ('#', '', ''),
        'Markdown': ('', '', ''),
        'Plain Text': ('', '', ''),
    }
    
    # Function/class patterns by language
    PATTERNS = {
        'Python': {
            'function': r'^\s*def\s+(\w+)',
            'class': r'^\s*class\s+(\w+)',
        },
        'JavaScript': {
            'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=|=>)',
            'class': r'class\s+(\w+)',
        },
        'TypeScript': {
            'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=)',
            'class': r'class\s+(\w+)',
        },
        'Java': {
            'function': r'(?:public|private|protected|\s)*(?:static\s+)?(?:void|int|String|bool|double|float|long|char|Object)\s+(\w+)',
            'class': r'class\s+(\w+)',
        },
        'C++': {
            'function': r'(?:void|int|bool|double|float|char|auto|auto)\s+(\w+)\s*\(',
            'class': r'class\s+(\w+)',
        },
        'Rust': {
            'function': r'fn\s+(\w+)',
            'class': r'struct\s+(\w+)',
        },
        'Go': {
            'function': r'func\s+(?:\([^)]*\))?\s*(\w+)',
            'type': r'type\s+(\w+)\s+struct',
        },
    }


class CodeStatisticsAnalyzer:
    """Main analyzer class for code statistics."""
    
    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path)
        self.config = LanguageConfig()
        self.stats = RepositoryStatistics()
        
    def detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        ext = file_path.suffix.lower()
        return self.config.EXTENSIONS.get(ext, 'Plain Text')
    
    def is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1024)
                return False
        except (UnicodeDecodeError, PermissionError):
            return True
    
    def count_lines_in_file(self, file_path: Path) -> FileStatistics:
        """Count statistics for a single file."""
        stat = FileStatistics(path=str(file_path), language=self.detect_language(file_path))
        
        if self.is_binary_file(file_path):
            return stat
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return stat
        
        stat.total_lines = len(lines)
        lang = stat.language
        patterns = self.config.PATTERNS.get(lang, {})
        
        single_comment = self.config.COMMENT_PATTERNS.get(lang, ('', '', ''))[0]
        ml_start = self.config.COMMENT_PATTERNS.get(lang, ('', '', ''))[1]
        ml_end = self.config.COMMENT_PATTERNS.get(lang, ('', '', ''))[2]
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                stat.blank_lines += 1
                continue
            
            # Check for multi-line comment start/end
            if ml_start and ml_end:
                if f'{ml_end}' in stripped and in_multiline_comment:
                    in_multiline_comment = False
                    stat.comment_lines += 1
                    continue
                if stripped.startswith(ml_start) and not in_multiline_comment:
                    in_multiline_comment = True
                    stat.comment_lines += 1
                    continue
                if in_multiline_comment:
                    stat.comment_lines += 1
                    continue
            
            # Check for single-line comments
            if single_comment and stripped.startswith(single_comment):
                stat.comment_lines += 1
                continue
            
            # Count as code line
            stat.code_lines += 1
            
            # Detect functions
            if 'function' in patterns.get('function', ''):
                if re.search(patterns['function'], line):
                    stat.functions += 1
            elif patterns.get('function') and re.search(patterns['function'], line):
                stat.functions += 1
            
            # Detect classes
            if patterns.get('class') and re.search(patterns['class'], line):
                stat.classes += 1
            
            # Simple complexity estimation (based on keywords)
            complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', '&&', '||', '?', 'catch', 'except']
            for keyword in complexity_keywords:
                if keyword in line.lower():
                    stat.complexity_score += 1
        
        return stat
    
    def analyze_directory(self, directory: Path = None, exclude_dirs: List[str] = None) -> RepositoryStatistics:
        """Analyze all files in a directory tree."""
        if directory is None:
            directory = self.root_path
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build']
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                # Check if file is in excluded directory
                should_exclude = False
                for excl in exclude_dirs:
                    if excl in file_path.parts:
                        should_exclude = True
                        break
                
                if not should_exclude:
                    file_stat = self.count_lines_in_file(file_path)
                    self.stats.files.append(file_stat)
        
        self._aggregate_statistics()
        return self.stats
    
    def _aggregate_statistics(self):
        """Aggregate statistics from all files."""
        self.stats.total_files = len(self.stats.files)
        
        for file_stat in self.stats.files:
            self.stats.total_lines += file_stat.total_lines
            self.stats.total_code_lines += file_stat.code_lines
            self.stats.total_comment_lines += file_stat.comment_lines
            self.stats.total_blank_lines += file_stat.blank_lines
            self.stats.total_functions += file_stat.functions
            self.stats.total_classes += file_stat.classes
            
            # Aggregate by language
            lang = file_stat.language
            if lang not in self.stats.language_stats:
                self.stats.language_stats[lang] = {
                    'files': 0,
                    'lines': 0,
                    'code_lines': 0,
                    'comment_lines': 0,
                    'functions': 0,
                    'classes': 0,
                }
            self.stats.language_stats[lang]['files'] += 1
            self.stats.language_stats[lang]['lines'] += file_stat.total_lines
            self.stats.language_stats[lang]['code_lines'] += file_stat.code_lines
            self.stats.language_stats[lang]['comment_lines'] += file_stat.comment_lines
            self.stats.language_stats[lang]['functions'] += file_stat.functions
            self.stats.language_stats[lang]['classes'] += file_stat.classes
    
    def print_report(self):
        """Print a formatted report of the analysis."""
        print("=" * 60)
        print("📊 CODE STATISTICS REPORT")
        print("=" * 60)
        print()
        
        print("📁 Overall Statistics")
        print("-" * 40)
        print(f"Total Files:          {self.stats.total_files:,}")
        print(f"Total Lines:          {self.stats.total_lines:,}")
        print(f"Code Lines:           {self.stats.total_code_lines:,}")
        print(f"Comment Lines:        {self.stats.total_comment_lines:,}")
        print(f"Blank Lines:          {self.stats.total_blank_lines:,}")
        print(f"Comment Ratio:        {self.stats.comment_ratio:.1f}%")
        print(f"Avg File Size:        {self.stats.average_file_size:.1f} lines")
        print()
        
        print("🔧 Code Structure")
        print("-" * 40)
        print(f"Total Functions:      {self.stats.total_functions:,}")
        print(f"Total Classes:        {self.stats.total_classes:,}")
        print()
        
        print("📈 Language Distribution")
        print("-" * 40)
        print(f"{'Language':<20} {'Files':>8} {'Lines':>10} {'Code':>10} {'Comments':>10}")
        print("-" * 60)
        
        sorted_langs = sorted(
            self.stats.language_stats.items(),
            key=lambda x: x[1]['lines'],
            reverse=True
        )
        
        for lang, data in sorted_langs:
            lang_display = lang if len(lang) <= 20 else lang[:17] + "..."
            print(f"{lang_display:<20} {data['files']:>8} {data['lines']:>10,} "
                  f"{data['code_lines']:>10,} {data['comment_lines']:>10,}")
        
        print("-" * 60)
        print()
        
        print("📝 Top 10 Largest Files")
        print("-" * 40)
        
        sorted_files = sorted(self.stats.files, key=lambda x: x.total_lines, reverse=True)[:10]
        for i, file_stat in enumerate(sorted_files, 1):
            file_name = file_stat.path.split('/')[-1]
            if len(file_name) > 30:
                file_name = file_name[:27] + "..."
            print(f"{i:>2}. {file_name:<30} {file_stat.total_lines:>6} lines  ({file_stat.language})")
        
        print()
        print("=" * 60)
    
    def export_json(self, output_path: str = "code_statistics.json"):
        """Export statistics to JSON format."""
        import json
        
        report = {
            "summary": {
                "total_files": self.stats.total_files,
                "total_lines": self.stats.total_lines,
                "total_code_lines": self.stats.total_code_lines,
                "total_comment_lines": self.stats.total_comment_lines,
                "total_blank_lines": self.stats.total_blank_lines,
                "comment_ratio": round(self.stats.comment_ratio, 2),
                "average_file_size": round(self.stats.average_file_size, 2),
                "total_functions": self.stats.total_functions,
                "total_classes": self.stats.total_classes,
            },
            "by_language": self.stats.language_stats,
            "files": [
                {
                    "path": f.path,
                    "language": f.language,
                    "lines": f.total_lines,
                    "code_lines": f.code_lines,
                    "comment_lines": f.comment_lines,
                    "functions": f.functions,
                    "classes": f.classes,
                }
                for f in self.stats.files
            ],
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Statistics exported to {output_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code Statistics Analyzer")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to analyze")
    parser.add_argument("--json", "-j", dest="json_output", help="Export to JSON file")
    parser.add_argument("--exclude", "-e", dest="exclude", default=".git,__pycache__,node_modules",
                       help="Comma-separated directories to exclude")
    
    args = parser.parse_args()
    
    exclude_dirs = [d.strip() for d in args.exclude.split(',')]
    
    print(f"🔍 Analyzing: {args.path}")
    print(f"🚫 Excluding: {', '.join(exclude_dirs)}")
    print()
    
    analyzer = CodeStatisticsAnalyzer(args.path)
    analyzer.analyze_directory(exclude_dirs=exclude_dirs)
    analyzer.print_report()
    
    if args.json_output:
        analyzer.export_json(args.json_output)


if __name__ == "__main__":
    main()
