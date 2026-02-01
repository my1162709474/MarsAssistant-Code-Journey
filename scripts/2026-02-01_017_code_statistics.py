#!/usr/bin/env python3
"""
代码统计器 - Code Statistics Analyzer
Day 17: 分析代码文件的行数、字符数、函数数量等统计信息

功能:
- 统计代码行数（总行数、代码行、注释行、空行）
- 统计字符数和字节数
- 识别编程语言
- 统计函数、类、导入等元素
- 生成详细的代码分析报告
"""

import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# 语言文件扩展名映射
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.h': 'C/C++ Header',
    '.cs': 'C#',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.json': 'JSON',
    '.xml': 'XML',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.md': 'Markdown',
    '.txt': 'Text',
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.sql': 'SQL',
    '.r': 'R',
    '.lua': 'Lua',
    '.perl': 'Perl',
    '.pl': 'Perl',
}


# 单行注释模式
COMMENT_PATTERNS = {
    'Python': ['#'],
    'JavaScript': ['//'],
    'TypeScript': ['//'],
    'Java': ['//'],
    'C': ['//'],
    'C++': ['//'],
    'C#': ['//'],
    'Go': ['//'],
    'Rust': ['//'],
    'Ruby': ['#'],
    'PHP': ['//', '#'],
    'Swift': ['//'],
    'Kotlin': ['//'],
    'Scala': ['//'],
    'Shell': ['#'],
    'Bash': ['#'],
    'SQL': ['--'],
    'R': ['#'],
    'Lua': ['--'],
    'Perl': ['#'],
}

# 多行注释开始/结束标记
MULTILINE_COMMENT_START = {
    'Python': ['"""', "'''"],
    'JavaScript': ['/*'],
    'TypeScript': ['/*'],
    'Java': ['/*'],
    'C': ['/*'],
    'C++': ['/*'],
    'C#': ['/*'],
    'Go': ['/*'],
    'Rust': ['/*'],
    'PHP': ['/*'],
    'Swift': ['/*'],
    'Kotlin': ['/*'],
    'Scala': ['/*'],
}

MULTILINE_COMMENT_END = {
    'Python': ['"""', "'''"],
    'JavaScript': ['*/'],
    'TypeScript': ['*/'],
    'Java': ['*/'],
    'C': ['*/'],
    'C++': ['*/'],
    'C#': ['*/'],
    'Go': ['*/'],
    'Rust': ['*/'],
    'PHP': ['*/'],
    'Swift': ['*/'],
    'Kotlin': ['*/'],
    'Scala': ['*/'],
}


class CodeStatistics:
    """代码统计器类"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.language = self._detect_language()
        
        # 统计结果
        self.total_lines = 0
        self.code_lines = 0
        self.comment_lines = 0
        self.blank_lines = 0
        
        self.char_count = 0
        self.byte_count = 0
        
        self.functions = []
        self.classes = []
        self.imports = []
        self.comments = []
        
    def _detect_language(self) -> str:
        """检测编程语言"""
        ext = self.file_path.suffix.lower()
        return LANGUAGE_EXTENSIONS.get(ext, 'Unknown')
    
    def _is_blank_line(self, line: str) -> bool:
        """判断是否是空行"""
        return line.strip() == ''
    
    def _is_comment_line(self, line: str) -> bool:
        """判断是否是注释行"""
        if self.language == 'Python':
            # 检查是否是
            stripped = line.strip()
            if stripped.startswith注释行纯('#'):
                return True
            # 检查是否是docstring
            if '"""' in line or "'''" in line:
                return True
        elif self.language in COMMENT_PATTERNS:
            for pattern in COMMENT_PATTERNS[self.language]:
                if line.strip().startswith(pattern):
                    return True
        return False
    
    def _extract_functions(self, lines: List[str]) -> List[str]:
        """提取函数名"""
        functions = []
        func_patterns = [
            r'def\s+(\w+)\s*\(',      # Python
            r'function\s+(\w+)\s*\(', # JavaScript
            r'const\s+(\w+)\s*=\s*function', # JS arrow func
            r'let\s+(\w+)\s*=\s*function', # JS arrow func
            r'(\w+)\s*:\s*function',  # JS object method
            r'public\s+\w+\s+(\w+)\s*\(', # Java
            r'private\s+\w+\s+(\w+)\s*\(', # Java
            r'static\s+\w+\s+(\w+)\s*\(', # Java
            r'func\s+(\w+)\s*\(',      # Go, Swift, Kotlin
            r'def\s+(\w+)\s*\(',       # Ruby
        ]
        
        for line in lines:
            for pattern in func_patterns:
                match = re.search(pattern, line)
                if match:
                    functions.append(match.group(1))
                    break
        
        return functions
    
    def _extract_classes(self, lines: List[str]) -> List[str]:
        """提取类名"""
        classes = []
        
        class_patterns = [
            r'class\s+(\w+)',         # Python, Java, JS, C++, etc.
            r'struct\s+(\w+)',        # C, C++
            r'interface\s+(\w+)',     # Java, TypeScript
            r'type\s+(\w+)\s*[{:]',   # TypeScript, Go
        ]
        
        for line in lines:
            for pattern in class_patterns:
                match = re.search(pattern, line)
                if match:
                    classes.append(match.group(1))
                    break
        
        return classes
    
    def _extract_imports(self, lines: List[str]) -> List[str]:
        """提取导入语句"""
        imports = []
        
        import_patterns = [
            r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]',  # ES6
            r'import\s+[\'"]([^\'"]+)[\'"]',           # ES6 default
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]',    # CommonJS
            r'from\s+[\'"]([^\'"]+)[\'"]',            # Python, Java
            r'include\s*[<"]([^">]+)[">]',             # C/C++
            r'use\s+(\w+)',                            # PHP, Perl
        ]
        
        for line in lines:
            for pattern in import_patterns:
                match = re.search(pattern, line)
                if match:
                    imports.append(match.group(1))
                    break
        
        return imports
    
    def analyze(self) -> Dict:
        """分析代码文件"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")
        
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        self.total_lines = len(lines)
        self.char_count = sum(len(line) for line in lines)
        
        # 读取原始字节
        with open(self.file_path, 'rb') as f:
            self.byte_count = len(f.read())
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # 检测多行注释
            if self.language in MULTILINE_COMMENT_START:
                for i, start in enumerate(MULTILINE_COMMENT_START[self.language]):
                    if start in stripped:
                        in_multiline_comment = True
                        break
                
                for end in MULTILINE_COMMENT_END.get(self.language, []):
                    if end in stripped:
                        in_multiline_comment = False
                        break
            
            # 分类统计
            if self._is_blank_line(line):
                self.blank_lines += 1
            elif in_multiline_comment or self._is_comment_line(line):
                self.comment_lines += 1
            else:
                self.code_lines += 1
            
            # 提取元素
            if not in_multiline_comment:
                self.functions.extend([f for f in self._extract_functions([line]) 
                                       if f not in self.functions])
                self.classes.extend([c for c in self._extract_classes([line]) 
                                    if c not in self.classes])
                self.imports.extend([i for i in self._extract_imports([line]) 
                                    if i not in self.imports])
        
        return self.get_statistics()
    
    def get_statistics(self) -> Dict:
        """获取统计结果"""
        return {
            'file_path': str(self.file_path),
            'language': self.language,
            'lines': {
                'total': self.total_lines,
                'code': self.code_lines,
                'comment': self.comment_lines,
                'blank': self.blank_lines,
            },
            'characters': self.char_count,
            'bytes': self.byte_count,
            'elements': {
                'functions': len(self.functions),
                'classes': len(self.classes),
                'imports': len(self.imports),
            },
            'details': {
                'function_names': self.functions[:10],  # 只返回前10个
                'class_names': self.classes,
                'import_modules': self.imports[:10],    # 只返回前10个
            }
        }
    
    def get_report(self) -> str:
        """生成可读的报告"""
        stats = self.get_statistics()
        
        lines = stats['lines']
        code_ratio = (lines['code'] / lines['total'] * 100) if lines['total'] > 0 else 0
        comment_ratio = (lines['comment'] / lines['total'] * 100) if lines['total'] > 0 else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    代码统计报告                              ║
╚══════════════════════════════════════════════════════════════╝

📁 文件: {stats['file_path']}
🌐 语言: {stats['language']}

📊 行数统计:
   • 总行数:     {lines['total']:>6}
   • 代码行:     {lines['code']:>6} ({code_ratio:>5.1f}%)
   • 注释行:     {lines['comment']:>6} ({comment_ratio:>5.1f}%)
   • 空白行:     {lines['blank']:>6}

📏 大小统计:
   • 字符数:     {stats['characters']:>6}
   • 字节数:     {stats['bytes']:>6}

🔧 元素统计:
   • 函数数量:   {stats['elements']['functions']:>6}
   • 类数量:     {stats['elements']['classes']:>6}
   • 导入数量:   {stats['elements']['imports']:>6}
"""
        if stats['details']['function_names']:
            report += f"""
📌 函数列表 (前10个):
"""
            for i, func in enumerate(stats['details']['function_names'], 1):
                report += f"   {i:2}. {func}\n"
        
        if stats['details']['class_names']:
            report += f"""
📦 类列表:
"""
            for i, cls in enumerate(stats['details']['class_names'], 1):
                report += f"   {i:2}. {cls}\n"
        
        report += "═" * 62 + "\n"
        
        return report


def analyze_directory(path: str, recursive: bool = True) -> Dict[str, CodeStatistics]:
    """分析目录中的所有代码文件"""
    path = Path(path)
    results = {}
    
    file_pattern = '*' if not recursive else '**/*'
    
    for file_path in path.glob(file_pattern):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in LANGUAGE_EXTENSIONS:
                try:
                    analyzer = CodeStatistics(str(file_path))
                    analyzer.analyze()
                    results[str(file_path)] = analyzer
                except Exception as e:
                    print(f"⚠️  分析失败 {file_path}: {e}")
    
    return results


def print_directory_summary(results: Dict[str, CodeStatistics]):
    """打印目录汇总统计"""
    total_files = len(results)
    total_lines = sum(r.total_lines for r in results.values())
    total_code = sum(r.code_lines for r in results.values())
    total_comment = sum(r.comment_lines for r in results.values())
    total_bytes = sum(r.byte_count for r in results.values())
    
    # 按语言分组统计
    lang_stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'bytes': 0})
    for analyzer in results.values():
        lang = analyzer.language
        lang_stats[lang]['files'] += 1
        lang_stats[lang]['lines'] += analyzer.total_lines
        lang_stats[lang]['bytes'] += analyzer.byte_count
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  目录代码统计汇总                           ║
╚══════════════════════════════════════════════════════════════╝

📁 总文件数:    {total_files:>6}
📊 总行数:      {total_lines:>6}
   • 代码行:    {total_code:>6} ({(total_code/total_lines*100) if total_lines > 0 else 0:.1f}%)
   • 注释行:    {total_comment:>6} ({(total_comment/total_lines*100) if total_lines > 0 else 0:.1f}%)
📏 总大小:      {total_bytes:>6} bytes

🌐 按语言分布:
""")
    
    for lang, stats in sorted(lang_stats.items(), key=lambda x: x[1]['lines'], reverse=True):
        print(f"   • {lang:<12}: {stats['files']:>3} 文件, {stats['lines']:>5} 行")
    
    print("═" * 62)


# ==================== 演示示例 ====================

def demo():
    """演示代码统计器的使用"""
    print("🧪 代码统计器演示")
    print("=" * 60)
    
    # 分析当前文件
    current_file = __file__
    print(f"\n📂 分析当前文件: {current_file}\n")
    
    analyzer = CodeStatistics(current_file)
    analyzer.analyze()
    print(analyzer.get_report())
    
    # 分析scripts目录
    scripts_dir = Path(__file__).parent / 'scripts'
    if scripts_dir.exists():
        print(f"\n📂 分析 scripts 目录...\n")
        results = analyze_directory(str(scripts_dir), recursive=False)
        print_directory_summary(results)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 命令行参数：分析指定文件或目录
        target = sys.argv[1]
        
        if os.path.isfile(target):
            analyzer = CodeStatistics(target)
            analyzer.analyze()
            print(analyzer.get_report())
        elif os.path.isdir(target):
            results = analyze_directory(target)
            print_directory_summary(results)
        else:
            print(f"❌ 路径不存在: {target}")
    else:
        # 默认运行演示
        demo()
