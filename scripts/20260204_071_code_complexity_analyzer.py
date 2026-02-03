#!/usr/bin/env python3
"""
Day 71: Code Complexity Analyzer
智能代码复杂度分析器 - 分析代码的圈复杂度、代码行数、函数数量等指标

功能:
- 计算圈复杂度 (Cyclomatic Complexity)
- 统计代码行数、注释行、空白行
- 检测代码异味 (Code Smells)
- 生成HTML可视化报告
- 支持多种编程语言
"""

import os
import re
import json
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from html import escape


@dataclass
class FunctionMetrics:
    """函数级别的指标"""
    name: str
    start_line: int
    end_line: int
    cyclomatic_complexity: int = 1
    parameters: int = 0
    local_variables: int = 0
    code_lines: int = 0
    comment_lines: int = 0


@dataclass
class FileMetrics:
    """文件级别的指标"""
    path: str
    language: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: List[FunctionMetrics] = field(default_factory=list)
    classes: int = 0
    complexity_score: int = 0
    code_smells: List[str] = field(default_factory=list)


class CodeComplexityAnalyzer:
    """代码复杂度分析器主类"""
    
    # 语言到文件扩展名的映射
    LANGUAGE_EXTENSIONS = {
        'python': ['.py', '.pyw'],
        'javascript': ['.js', '.jsx', '.mjs'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
        'c': ['.c', '.h'],
        'csharp': ['.cs'],
        'go': ['.go'],
        'rust': ['.rs'],
        'ruby': ['.rb'],
        'php': ['.php'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
        'sql': ['.sql'],
        'shell': ['.sh', '.bash', '.zsh'],
    }
    
    # 代码异味检测规则
    CODE_SMELL_PATTERNS = {
        'long_function': (20, "函数过长 (>20 行代码)"),
        'too_many_parameters': (5, "参数过多 (>5 个参数)"),
        'high_complexity': (10, "圈复杂度过高 (>10)"),
        'long_method': (30, "方法过长 (>30 行)"),
        'too_many_methods': (15, "类中方法过多 (>15 个)"),
        'nested_depth': (4, "嵌套过深 (>4 层)"),
        'long_class': (300, "类定义过长 (>300 行)"),
    }
    
    def __init__(self):
        self.metrics: Dict[str, FileMetrics] = {}
        self.language_detectors = self._build_language_detectors()
    
    def _build_language_detectors(self) -> Dict[str, List[str]]:
        """构建语言检测正则表达式"""
        detectors = {
            'python': [
                r'^import\s+', r'^from\s+', r'def\s+\w+\s*\(', 
                r'class\s+\w+\s*[:(]', r'^\s*#!'
            ],
            'javascript': [
                r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'var\s+\w+\s*=',
                r'function\s+\w+\s*\(', r'=>', r'class\s+\w+\s*\{'
            ],
            'java': [
                r'public\s+class', r'private\s+class', r'void\s+\w+\s*\(',
                r'System\.out\.print', r'import\s+java'
            ],
            'cpp': [
                r'#include', r'std::', r'void\s+\w+\s*\(',
                r'int\s+main\s*\(', r'class\s+\w+\s*\{'
            ],
            'go': [
                r'package\s+\w+', r'func\s+\w+\s*\(', r'import\s*\(',
                r'fmt\.Print'
            ],
            'rust': [
                r'fn\s+\w+\s*\(', r'let\s+(mut\s+)?\w+',
                r'use\s+', r'impl\s+\w+'
            ],
        }
        return detectors
    
    def detect_language(self, file_path: str, content: str) -> str:
        """检测文件编程语言"""
        ext = Path(file_path).suffix.lower()
        
        # 通过扩展名检测
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        
        # 通过内容检测
        first_lines = '\n'.join(content.split('\n')[:10])
        for lang, patterns in self.language_detectors.items():
            for pattern in patterns:
                if re.search(pattern, first_lines, re.MULTILINE):
                    return lang
        
        return 'unknown'
    
    def count_lines(self, content: str) -> Tuple[int, int, int]:
        """统计代码行、注释行、空白行"""
        lines = content.split('\n')
        total = len(lines)
        blank = 0
        comment = 0
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # 检测多行注释
            if '"""' in stripped or "'''" in stripped:
                in_multiline_comment = not in_multiline_comment
            
            if in_multiline_comment:
                comment += 1
            elif not stripped:
                blank += 1
            elif stripped.startswith('#'):
                comment += 1
            elif stripped.startswith('//'):
                comment += 1
            else:
                pass  # 代码行
        
        code = total - blank - comment
        return total, code, comment, blank
    
    def calculate_python_complexity(self, content: str) -> List[FunctionMetrics]:
        """使用AST计算Python代码复杂度"""
        functions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func = FunctionMetrics(
                        name=node.name,
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno
                    )
                    
                    # 计算圈复杂度
                    complexity = 1
                    for child in ast.walk(node):
                        if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, 
                                              ast.With, ast.AsyncWith, ast.Assert,
                                              ast.BoolOp, ast.Compare)):
                            complexity += 1
                    
                    func.cyclomatic_complexity = complexity
                    func.parameters = len(node.args.args)
                    func.code_lines = (func.end_line - func.start_line + 1)
                    
                    # 统计局部变量
                    func.local_variables = len([n for n in ast.walk(node) 
                                               if isinstance(n, ast.Name) 
                                               and isinstance(n.ctx, ast.Store)])
                    
                    functions.append(func)
                
                elif isinstance(node, ast.ClassDef):
                    # 统计类中的方法数量
                    methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    if len(methods) > self.CODE_SMELL_PATTERNS['too_many_methods'][0]:
                        # 记录在后续处理
                        pass
        
        except SyntaxError:
            pass
        
        return functions
    
    def estimate_complexity_other(self, content: str, language: str) -> List[FunctionMetrics]:
        """使用正则表达式估算其他语言的复杂度"""
        functions = []
        
        # 检测函数/方法定义
        patterns = {
            'javascript': r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?function|(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)',
            'java': r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*\{',
            'cpp': r'(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*\{',
            'go': r'func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(',
            'rust': r'fn\s+(\w+)\s*\(',
        }
        
        pattern = patterns.get(language, r'(\w+)\s*\([^)]*\)\s*\{')
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1) if match.lastindex else f"anonymous_{i}"
                
                # 估算复杂度
                complexity = 1
                rest_of_file = '\n'.join(lines[i:])
                complexity += len(re.findall(r'\b(if|elif|else|for|while|switch|case|try|catch|except|&&|\|\|)\b', rest_of_file[:500]))
                
                functions.append(FunctionMetrics(
                    name=func_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    cyclomatic_complexity=min(complexity, 20)  # 限制最大值
                ))
        
        return functions[:20]  # 限制检测数量
    
    def detect_code_smells(self, file_metrics: FileMetrics) -> List[str]:
        """检测代码异味"""
        smells = []
        
        for func in file_metrics.functions:
            if func.code_lines > self.CODE_SMELL_PATTERNS['long_function'][0]:
                smells.append(f"函数 '{func.name}' 太长 ({func.code_lines} 行)")
            
            if func.parameters > self.CODE_SMELL_PATTERNS['too_many_parameters'][0]:
                smells.append(f"函数 '{func.name}' 参数过多 ({func.parameters} 个)")
            
            if func.cyclomatic_complexity > self.CODE_SMELL_PATTERNS['high_complexity'][0]:
                smells.append(f"函数 '{func.name}' 复杂度过高 ({func.cyclomatic_complexity})")
        
        if file_metrics.classes > 10:
            smells.append(f"类数量过多 ({file_metrics.classes})")
        
        return smells[:10]  # 限制报告数量
    
    def analyze_file(self, file_path: str) -> Optional[FileMetrics]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return None
        
        if not content.strip():
            return None
        
        language = self.detect_language(file_path, content)
        if language == 'unknown':
            language = 'text'
        
        total, code, comment, blank = self.count_lines(content)
        
        # 计算函数和复杂度
        if language == 'python':
            functions = self.calculate_python_complexity(content)
        else:
            functions = self.estimate_complexity_other(content, language)
        
        # 检测类定义数量
        class_patterns = {
            'python': r'^class\s+\w+',
            'javascript': r'class\s+\w+',
            'java': r'class\s+\w+',
            'cpp': r'class\s+\w+',
        }
        class_pattern = class_patterns.get(language, r'class\s+\w+')
        num_classes = len(re.findall(class_pattern, content, re.MULTILINE))
        
        metrics = FileMetrics(
            path=file_path,
            language=language,
            total_lines=total,
            code_lines=code,
            comment_lines=comment,
            blank_lines=blank,
            functions=functions,
            classes=num_classes
        )
        
        metrics.complexity_score = sum(f.cyclomatic_complexity for f in functions)
        metrics.code_smells = self.detect_code_smells(metrics)
        
        return metrics
    
    def analyze_directory(self, directory: str, recursive: bool = True) -> Dict[str, FileMetrics]:
        """递归分析目录下的所有文件"""
        self.metrics = {}
        
        path = Path(directory)
        pattern = '**/*' if recursive else '*'
        
        for file_path in path.glob(pattern):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', 
                          '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.sql', '.sh']:
                    metrics = self.analyze_file(str(file_path))
                    if metrics:
                        self.metrics[str(file_path)] = metrics
        
        return self.metrics
    
    def get_summary(self) -> Dict:
        """生成分析摘要"""
        if not self.metrics:
            return {}
        
        total_files = len(self.metrics)
        total_lines = sum(m.total_lines for m in self.metrics.values())
        total_code = sum(m.code_lines for m in self.metrics.values())
        total_functions = sum(len(m.functions) for m in self.metrics.values())
        total_complexity = sum(m.complexity_score for m in self.metrics.values())
        all_smells = []
        for m in self.metrics.values():
            all_smells.extend(m.code_smells)
        
        return {
            'files_analyzed': total_files,
            'total_lines': total_lines,
            'code_lines': total_code,
            'comment_ratio': f"{(sum(m.comment_lines for m in self.metrics.values())/total_lines*100):.1f}%" if total_lines else "0%",
            'total_functions': total_functions,
            'average_complexity': f"{total_complexity/total_functions:.2f}" if total_functions else "0",
            'code_smells_count': len(all_smells),
            'code_smells': all_smells[:20],
            'by_language': self._group_by_language()
        }
    
    def _group_by_language(self) -> Dict[str, Dict]:
        """按语言分组统计"""
        groups = defaultdict(lambda: {'files': 0, 'lines': 0, 'complexity': 0})
        
        for path, metrics in self.metrics.items():
            lang = metrics.language
            groups[lang]['files'] += 1
            groups[lang]['lines'] += metrics.code_lines
            groups[lang]['complexity'] += metrics.complexity_score
        
        return dict(groups)
    
    def generate_html_report(self, output_path: str = "complexity_report.html"):
        """生成HTML可视化报告"""
        summary = self.get_summary()
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码复杂度分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: white; text-align: center; margin-bottom: 30px; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: transform 0.3s; }}
        .card:hover {{ transform: translateY(-5px); }}
        .card h3 {{ color: #667eea; font-size: 0.9em; text-transform: uppercase; margin-bottom: 10px; }}
        .card .value {{ font-size: 2.5em; font-weight: bold; color: #333; }}
        .card .unit {{ font-size: 0.5em; color: #999; }}
        .section {{ background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .section h2 {{ color: #667eea; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
        th {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        tr:hover {{ background: #f8f9ff; }}
        .complexity-high {{ color: #e74c3c; font-weight: bold; }}
        .complexity-medium {{ color: #f39c12; font-weight: bold; }}
        .complexity-low {{ color: #27ae60; }}
        .smell {{ background: #fff3cd; padding: 8px 12px; border-radius: 5px; margin: 5px 0; border-left: 4px solid #ffc107; }}
        .language-tag {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }}
        .lang-python {{ background: #3776ab; color: white; }}
        .lang-javascript {{ background: #f7df1e; color: #333; }}
        .lang-java {{ background: #ed8b00; color: white; }}
        .lang-cpp {{ background: #00599c; color: white; }}
        .lang-other {{ background: #6c757d; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 代码复杂度分析报告</h1>
        
        <div class="summary">
            <div class="card">
                <h3>📁 分析文件</h3>
                <div class="value">{summary.get('files_analyzed', 0)}<span class="unit"> 个</span></div>
            </div>
            <div class="card">
                <h3>📝 代码行数</h3>
                <div class="value">{summary.get('code_lines', 0):,}<span class="unit"> 行</span></div>
            </div>
            <div class="card">
                <h3>⚙️ 函数数量</h3>
                <div class="value">{summary.get('total_functions', 0)}<span class="unit"> 个</span></div>
            </div>
            <div class="card">
                <h3>📈 平均复杂度</h3>
                <div class="value">{summary.get('average_complexity', '0')}</div>
            </div>
            <div class="card">
                <h3>🔍 代码异味</h3>
                <div class="value" style="color: {'#e74c3c' if summary.get('code_smells_count', 0) > 0 else '#27ae60'}">{summary.get('code_smells_count', 0)}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🌐 按语言统计</h2>
            <table>
                <tr><th>语言</th><th>文件数</th><th>代码行</th><th>总复杂度</th></tr>
"""
        
        for lang, data in summary.get('by_language', {}).items():
            lang_class = f"lang-{lang}" if lang in ['python', 'javascript', 'java', 'cpp'] else 'lang-other'
            html += f"""                <tr>
                    <td><span class="language-tag {lang_class}">{lang.upper()}</span></td>
                    <td>{data['files']}</td>
                    <td>{data['lines']:,}</td>
                    <td>{data['complexity']}</td>
                </tr>
"""
        
        html += """            </table>
        </div>
        
        <div class="section">
            <h2>🐛 代码异味检测</h2>
"""
        
        smells = summary.get('code_smells', [])
        if smells:
            for smell in smells:
                html += f'            <div class="smell">⚠️ {escape(smell)}</div>\n'
        else:
            html += '            <p style="color: #27ae60; padding: 20px;">✅ 恭喜！未检测到明显代码异味</p>\n'
        
        html += """        </div>
        
        <div class="section">
            <h2>📋 文件详情</h2>
            <table>
                <tr><th>文件</th><th>语言</th><th>代码行</th><th>函数</th><th>复杂度</th><th>类</th></tr>
"""
        
        for path, metrics in sorted(self.metrics.items(), key=lambda x: x[1].complexity_score, reverse=True):
            rel_path = path.split('/')[-1] if '/' in path else path
            complexity_class = 'complexity-high' if metrics.complexity_score > 50 else ('complexity-medium' if metrics.complexity_score > 20 else 'complexity-low')
            lang_class = f"lang-{metrics.language}" if metrics.language in ['python', 'javascript', 'java', 'cpp'] else 'lang-other'
            
            html += f"""                <tr>
                    <td title="{escape(path)}">{escape(rel_path)}</td>
                    <td><span class="language-tag {lang_class}">{metrics.language.upper()}</span></td>
                    <td>{metrics.code_lines}</td>
                    <td>{len(metrics.functions)}</td>
                    <td class="{complexity_class}">{metrics.complexity_score}</td>
                    <td>{metrics.classes}</td>
                </tr>
"""
        
        html += """            </table>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def print_summary(self):
        """打印分析摘要到控制台"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 代码复杂度分析报告")
        print("="*60)
        print(f"  📁 分析文件:    {summary.get('files_analyzed', 0)} 个")
        print(f"  📝 代码行数:    {summary.get('code_lines', 0):,} 行")
        print(f"  💬 注释率:      {summary.get('comment_ratio', '0%')}")
        print(f"  ⚙️ 函数数量:    {summary.get('total_functions', 0)} 个")
        print(f"  📈 平均复杂度:  {summary.get('average_complexity', '0')}")
        print(f"  🔍 代码异味:    {summary.get('code_smells_count', 0)} 个")
        print("="*60)
        
        print("\n🌐 按语言统计:")
        print("-"*50)
        for lang, data in summary.get('by_language', {}).items():
            print(f"  {lang.upper():12} | {data['files']:3} 文件 | {data['lines']:6,} 行 | 复杂度: {data['complexity']:4}")
        
        print("\n🐛 代码异味:")
        print("-"*50)
        smells = summary.get('code_smells', [])
        if smells:
            for smell in smells[:10]:
                print(f"  ⚠️ {smell}")
        else:
            print("  ✅ 未检测到明显代码异味")
        
        print()


def main():
    """主函数"""
    import sys
    
    analyzer = CodeComplexityAnalyzer()
    
    # 默认分析当前目录
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    recursive = '--recursive' in sys.argv or '-r' in sys.argv
    
    print(f"🔍 分析目录: {target} (递归: {'是' if recursive else '否'})")
    
    metrics = analyzer.analyze_directory(target, recursive)
    analyzer.print_summary()
    
    # 生成HTML报告
    report_path = analyzer.generate_html_report()
    print(f"📄 HTML报告已生成: {report_path}")
    
    # 保存JSON格式的结果
    result = {
        'summary': analyzer.get_summary(),
        'files': {
            path: {
                'language': m.language,
                'total_lines': m.total_lines,
                'code_lines': m.code_lines,
                'comment_lines': m.comment_lines,
                'functions': len(m.functions),
                'complexity_score': m.complexity_score,
                'classes': m.classes,
                'code_smells': m.code_smells
            }
            for path, m in metrics.items()
        }
    }
    
    json_path = "complexity_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📊 JSON报告已生成: {json_path}")


if __name__ == "__main__":
    main()
