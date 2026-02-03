#!/usr/bin/env python3
"""
Code Complexity Visualizer
A lightweight tool to analyze and visualize code complexity metrics
Supports Python, JavaScript, and Java files
"""

import os
import re
import sys
import base64
import argparse
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# ANSI color codes for colorful output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    ORANGE = '\033[33m'
    
    @classmethod
    def disable(cls):
        cls.RESET = ''
        cls.BOLD = ''
        cls.RED = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.PURPLE = ''
        cls.ORANGE = ''


class ComplexityAnalyzer:
    """Analyze code complexity for different programming languages"""
    
    # Language-specific patterns
    PATTERNS = {
        'python': {
            'function': r'^\s*(?:async\s+)?def\s+(\w+)\s*\(',
            'class': r'^\s*class\s+(\w+)',
            'if_stmt': r'\bif\s+|elif\s+',
            'loop': r'\bfor\s+|while\s+|except\s*:',
            'bool_ops': r'\band\b|\bor\b|\bnot\b',
            'try': r'\btry\s*:',
        },
        'javascript': {
            'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=|arrow\s*=>|(\w+)\s*\([^)]*\)\s*\{)',
            'class': r'class\s+(\w+)',
            'if_stmt': r'\bif\s*\(|else\s+if\s*\(',
            'loop': r'\bfor\s*\(|while\s*\(|do\s*\{',
            'bool_ops': r'\&\&|\|\||\!',
            'try': r'\bcatch\s*\(',
        },
        'java': {
            'function': r'(?:public|private|protected|static|\s)+(?:void|int|String|boolean|List|Map|Array|double|float|char|long|byte|short)[^()]*(\w+)\s*\(',
            'class': r'(?:public|private|protected|static|\s)*class\s+(\w+)',
            'if_stmt': r'\bif\s*\(',
            'loop': r'\bfor\s*\(|while\s*\(|do\s*\{',
            'bool_ops': r'\&\&|\|\||\!',
            'try': r'\bcatch\s*\(',
        }
    }
    
    def __init__(self, language: str = 'python', no_color: bool = False):
        self.language = language.lower()
        if no_color:
            Colors.disable()
        self.patterns = self.PATTERNS.get(self.language, self.PATTERNS['python'])
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single file and return complexity metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            return {'error': str(e)}
        
        total_lines = len(lines)
        code_lines = self._count_code_lines(lines)
        comment_lines = self._count_comment_lines(lines)
        blank_lines = total_lines - code_lines - comment_lines
        
        functions = []
        classes = []
        total_cyclomatic = 0
        
        for i, line in enumerate(lines):
            # Detect functions
            func_match = re.search(self.patterns['function'], line)
            if func_match:
                func_name = func_match.group(1) or func_match.group(2) or func_match.group(3)
                complexity = self._calculate_function_complexity(lines, i)
                functions.append({
                    'name': func_name,
                    'line': i + 1,
                    'complexity': complexity,
                    'start_line': i + 1
                })
                total_cyclomatic += complexity
            
            # Detect classes
            class_match = re.search(self.patterns['class'], line)
            if class_match:
                classes.append({
                    'name': class_match.group(1),
                    'line': i + 1
                })
        
        # Overall file complexity
        file_complexity = self._calculate_file_complexity(lines)
        
        return {
            'file_path': file_path,
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'functions': functions,
            'classes': classes,
            'total_cyclomatic': total_cyclomatic,
            'file_complexity': file_complexity,
            'function_count': len(functions),
            'class_count': len(classes)
        }
    
    def _count_code_lines(self, lines: List[str]) -> int:
        """Count lines that contain code (not comments or blank)"""
        code_count = 0
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip blank lines
            if not stripped:
                continue
            
            # Check for multiline comment start/end
            if '"""' in stripped or "'''" in stripped:
                in_multiline_comment = not in_multiline_comment
                continue
            
            if in_multiline_comment:
                continue
            
            # Skip single-line comments
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
            
            code_count += 1
        
        return code_count
    
    def _count_comment_lines(self, lines: List[str]) -> int:
        """Count comment-only lines"""
        comment_count = 0
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            if '"""' in stripped or "'''" in stripped:
                # Check if it's a single-line multiline comment
                if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 6:
                    comment_count += 1
                elif stripped.startswith("'''") and stripped.endswith("'''") and len(stripped) > 6:
                    comment_count += 1
                else:
                    in_multiline_comment = not in_multiline_comment
                continue
            
            if in_multiline_comment:
                comment_count += 1
                continue
            
            if stripped.startswith('#') or stripped.startswith('//'):
                comment_count += 1
        
        return comment_count
    
    def _calculate_function_complexity(self, lines: List[str], start_idx: int) -> int:
        """Calculate cyclomatic complexity for a function starting at start_idx"""
        complexity = 1  # Base complexity
        
        # Find the end of the function definition line
        brace_count = 0
        found_first_brace = False
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            
            # Count complexity-inducing statements
            if re.search(self.patterns['if_stmt'], line):
                complexity += 1
            if re.search(self.patterns['loop'], line):
                complexity += 1
            if re.search(self.patterns['bool_ops'], line):
                complexity += line.count('&&') + line.count('||') + 1
            if re.search(self.patterns['try'], line):
                complexity += 1
            
            # For Python, check indentation level
            if self.language == 'python':
                if i > start_idx:
                    stripped = lines[i].strip()
                    if stripped and not stripped.startswith('#'):
                        if not stripped.startswith('"""') and not stripped.startswith("'''"):
                            # Check for control structures
                            if re.match(r'^\s*if\s+|^\s*elif\s+|^\s*else\s*:', stripped):
                                if 'elif' in stripped:
                                    complexity += 1
                                elif 'else' not in stripped:
                                    complexity += 1
                            if re.match(r'^\s*for\s+|^\s*while\s+|^\s*except\s*:', stripped):
                                complexity += 1
                            if re.match(r'^\s*with\s+', stripped):
                                complexity += 1
            
            if found_first_brace and brace_count == 0:
                break
            if '{' in line:
                found_first_brace = True
        
        return max(complexity, 1)
    
    def _calculate_file_complexity(self, lines: List[str]) -> int:
        """Calculate overall file complexity"""
        complexity = 1
        
        for line in lines:
            if re.search(self.patterns['if_stmt'], line):
                complexity += 1
            if re.search(self.patterns['loop'], line):
                complexity += 1
            if re.search(self.patterns['bool_ops'], line):
                complexity += 1
            if re.search(self.patterns['try'], line):
                complexity += 1
        
        return complexity


class ASCIIVisualizer:
    """Generate ASCII visualizations for complexity metrics"""
    
    @staticmethod
    def draw_bar(value: int, max_value: int, width: int = 30, 
                 low_color: str = Colors.GREEN, 
                 med_color: str = Colors.YELLOW, 
                 high_color: str = Colors.RED) -> str:
        """Draw a horizontal bar chart"""
        if max_value == 0:
            max_value = 1
        
        fill_width = int((value / max_value) * width)
        fill_width = min(fill_width, width)
        
        if value < max_value * 0.3:
            color = low_color
        elif value < max_value * 0.7:
            color = med_color
        else:
            color = high_color
        
        bar = '█' * fill_width + '░' * (width - fill_width)
        return f"{color}[{bar}]{Colors.RESET} {value}"
    
    @staticmethod
    def draw_vertical_bar(value: int, max_value: int, height: int = 10) -> List[str]:
        """Draw a vertical bar chart"""
        if max_value == 0:
            max_value = 1
        
        bar_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        fill_height = int((value / max_value) * (height - 1))
        fill_height = min(fill_height, height - 1)
        
        lines = []
        for i in range(height - 1, -1, -1):
            if i > fill_height:
                lines.append('  ')
            elif i == fill_height:
                lines.append(f'{bar_chars[fill_height]} ')
            else:
                lines.append(f'{bar_chars[fill_height]} ')
        
        return lines
    
    @staticmethod
    def draw_distribution(values: List[int], bins: int = 5) -> str:
        """Draw a distribution histogram"""
        if not values:
            return "No data available"
        
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val != min_val else 1
        
        histogram = defaultdict(int)
        for val in values:
            bin_idx = min(int((val - min_val) / range_val * (bins - 1)), bins - 1)
            histogram[bin_idx] += 1
        
        max_count = max(histogram.values()) if histogram else 1
        width = 40
        
        lines = []
        for bin_idx in range(bins - 1, -1, -1):
            count = histogram.get(bin_idx, 0)
            bar_len = int((count / max_count) * width)
            bar_len = min(bar_len, width)
            
            bin_range_start = int(min_val + (range_val / bins) * bin_idx)
            bin_range_end = int(min_val + (range_val / bins) * (bin_idx + 1))
            
            label = f"{bin_range_start:3d}-{bin_range_end:3d}"
            bar = '█' * bar_len
            lines.append(f"{label} │{bar} {count}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def draw_summary_table(metrics: Dict) -> str:
        """Draw a summary table"""
        lines = [
            f"{Colors.CYAN}┌{'─' * 40}┐{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}Code Complexity Summary{Colors.RESET} {' ' * 13} {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}├{'─' * 40}┤{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Lines:        {metrics['total_lines']:>5}    {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Code Lines:   {metrics['code_lines']:>5}    {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Comments:     {metrics['comment_lines']:>5}    {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Blanks:       {metrics['blank_lines']:>5}    {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Functions:    {metrics['function_count']:>5}    {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Classes:      {metrics['class_count']:>5}    {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}├{'─' * 40}┤{Colors.RESET}",
        ]
        
        # Complexity level color
        comp = metrics['total_cyclomatic']
        if comp < 10:
            comp_color = Colors.GREEN
        elif comp < 20:
            comp_color = Colors.YELLOW
        else:
            comp_color = Colors.RED
        
        lines.append(f"{Colors.CYAN}│{Colors.RESET} Cyclomatic:   {comp_color}{comp:>5}{Colors.RESET}    {Colors.CYAN}│{Colors.RESET}")
        lines.append(f"{Colors.CYAN}└{'─' * 40}┘{Colors.RESET}")
        
        return '\n'.join(lines)


def analyze_directory(path: str, language: str = 'python', 
                      recursive: bool = True) -> List[Dict]:
    """Analyze all files in a directory"""
    results = []
    extensions = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx', '.ts', '.tsx'],
        'java': ['.java']
    }
    
    ext_list = extensions.get(language, extensions['python'])
    
    for root, dirs, files in os.walk(path):
        for file in files:
            if any(file.endswith(ext) for ext in ext_list):
                file_path = os.path.join(root, file)
                analyzer = ComplexityAnalyzer(language)
                result = analyzer.analyze_file(file_path)
                if 'error' not in result:
                    results.append(result)
        
        if not recursive:
            break
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Code Complexity Visualizer - Analyze and visualize code complexity'
    )
    parser.add_argument('path', nargs='?', default='.',
                       help='File or directory to analyze (default: current directory)')
    parser.add_argument('-l', '--language', choices=['python', 'javascript', 'java'],
                       default='python', help='Programming language (default: python)')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Recursively analyze subdirectories')
    parser.add_argument('-f', '--file', help='Analyze a single file')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    parser.add_argument('--json', action='store_true',
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    if args.file:
        analyzer = ComplexityAnalyzer(args.language, args.no_color)
        result = analyzer.analyze_file(args.file)
        
        if 'error' in result:
            print(f"{Colors.RED}Error: {result['error']}{Colors.RESET}")
            sys.exit(1)
        
        if args.json:
            import json
            print(json.dumps(result, indent=2))
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}📊 Code Complexity Analysis{Colors.RESET}")
        print(f"File: {result['file_path']}\n")
        
        # Summary table
        print(ASCIIVisualizer.draw_summary_table(result))
        print()
        
        # Complexity bar
        print(f"{Colors.BOLD}Overall Cyclomatic Complexity:{Colors.RESET}")
        print(ASCIIVisualizer.draw_bar(result['total_cyclomatic'], 
                                       max(result['total_cyclomatic'], 20)))
        print()
        
        # Function complexities
        if result['functions']:
            print(f"{Colors.BOLD}Top Complex Functions:{Colors.RESET}")
            sorted_funcs = sorted(result['functions'], 
                                  key=lambda x: x['complexity'], 
                                  reverse=True)[:5]
            
            max_comp = max(f['complexity'] for f in sorted_funcs) if sorted_funcs else 1
            
            for func in sorted_funcs:
                bar = ASCIIVisualizer.draw_bar(func['complexity'], max_comp, 20)
                color = Colors.GREEN if func['complexity'] < 10 else \
                        Colors.YELLOW if func['complexity'] < 20 else Colors.RED
                print(f"  {color}{func['name']:20s}{Colors.RESET} {bar} (line {func['line']})")
        
        print()
    
    else:
        # Analyze directory
        path = args.path if os.path.isdir(args.path) else '.'
        results = analyze_directory(path, args.language, args.recursive)
        
        if not results:
            print(f"{Colors.YELLOW}No files found to analyze.{Colors.RESET}")
            return
        
        if args.json:
            import json
            print(json.dumps(results, indent=2))
            return
        
        # Aggregate results
        total_lines = sum(r['total_lines'] for r in results)
        total_code = sum(r['code_lines'] for r in results)
        total_funcs = sum(r['function_count'] for r in results)
        total_complexity = sum(r['total_cyclomatic'] for r in results)
        
        # Get all function complexities for distribution
        all_complexities = []
        for r in results:
            all_complexities.extend(f['complexity'] for f in r['functions'])
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}📊 Code Complexity Report{Colors.RESET}")
        print(f"Analyzed {len(results)} files\n")
        
        print(f"{Colors.BOLD}Summary:{Colors.RESET}")
        print(f"  Total Lines:    {total_lines:,}")
        print(f"  Code Lines:     {total_code:,}")
        print(f"  Functions:       {total_funcs}")
        print(f"  Total Cyclomatic Complexity: {total_complexity}")
        print()
        
        if all_complexities:
            print(f"{Colors.BOLD}Function Complexity Distribution:{Colors.RESET}")
            print(ASCIIVisualizer.draw_distribution(all_complexities))
            print()


if __name__ == '__main__':
    main()
