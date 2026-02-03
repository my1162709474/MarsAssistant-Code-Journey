#!/usr/bin/env python3
"""
智能代码复杂度分析器
=====================
自动分析代码复杂度、计算技术债务、评估代码可维护性

功能特性:
- 圈复杂度(Cyclomatic Complexity)计算
- 代码行数统计(代码/注释/空白行)
- 函数/类复杂度分析
- 技术债务估算
- 可维护性指数
- HTML报告生成

作者: AI Assistant
日期: 2026-02-03
"""

import os
import re
import json
import ast
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict
from pathlib import Path


class ComplexityLevel(Enum):
    """复杂度等级"""
    EXCELLENT = ("优秀", 1-5)
    GOOD = ("良好", 6-10)
    MODERATE = ("中等", 11-20)
    HIGH = ("较高", 21-30)
    VERY_HIGH = ("很高", 31-50)
    CRITICAL = ("极高", 51+)


@dataclass
class FunctionMetrics:
    """函数指标"""
    name: str
    line_start: int
    line_end: int
    cyclomatic_complexity: int
    num_params: int
    num_variables: int
    num_statements: int
    has_recursion: bool = False
    has_loops: bool = False
    has_exception: bool = False
    
    @property
    def complexity_level(self) -> str:
        if self.cyclomatic_complexity <= 5:
            return "优秀"
        elif self.cyclomatic_complexity <= 10:
            return "良好"
        elif self.cyclomatic_complexity <= 20:
            return "中等"
        elif self.cyclomatic_complexity <= 30:
            return "较高"
        elif self.cyclomatic_complexity <= 50:
            return "很高"
        else:
            return "极高"


@dataclass
class FileMetrics:
    """文件指标"""
    path: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: List[FunctionMetrics] = field(default_factory=list)
    classes: int = 0
    imports: int = 0
    complexity_score: float = 0.0
    
    @property
    def comment_ratio(self) -> float:
        return self.comment_lines / self.total_lines if self.total_lines > 0 else 0


class ComplexityAnalyzer:
    """代码复杂度分析器"""
    
    # Python关键字列表
    KEYWORDS = {
        'if', 'elif', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
        'try', 'except', 'finally', 'with', 'and', 'or', 'not', 'in', 'is',
        'True', 'False', 'None', 'def', 'class', 'return', 'yield', 'raise',
        'break', 'continue', 'pass', 'import', 'from', 'as', 'assert', 'lambda',
        'async', 'await', 'global', 'nonlocal', 'del', 'struct', 'enum', 'match'
    }
    
    def __init__(self):
        self.files: Dict[str, FileMetrics] = {}
    
    def analyze_file(self, file_path: str) -> FileMetrics:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._analyze_content(file_path, content)
        except (FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Error reading {file_path}: {e}")
            return FileMetrics(path=file_path)
    
    def analyze_directory(self, directory: str, extensions: List[str] = None) -> Dict[str, FileMetrics]:
        """分析整个目录"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']
        
        self.files = {}
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    metrics = self.analyze_file(file_path)
                    if metrics.total_lines > 0:
                        self.files[file_path] = metrics
        
        return self.files
    
    def _analyze_content(self, file_path: str, content: str) -> FileMetrics:
        """分析文件内容"""
        metrics = FileMetrics(path=file_path)
        lines = content.split('\n')
        metrics.total_lines = len(lines)
        
        # 统计各类行数
        in_multiline_comment = False
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_multiline_comment:
                    in_multiline_comment = False
                    metrics.comment_lines += 1
                else:
                    in_multiline_comment = True
                    metrics.comment_lines += 1
            elif in_multiline_comment:
                metrics.comment_lines += 1
            elif stripped.startswith('#'):
                metrics.comment_lines += 1
            elif not stripped:
                metrics.blank_lines += 1
            else:
                metrics.code_lines += 1
        
        # 如果是Python文件，使用AST深度分析
        if file_path.endswith('.py'):
            metrics = self._analyze_python_ast(file_path, content, metrics)
        else:
            # 其他文件使用简单的复杂度计算
            metrics.complexity_score = self._calculate_simple_complexity(content)
        
        # 提取函数信息（简单方法）
        if not file_path.endswith('.py'):
            self._extract_functions_simple(content, metrics)
        
        return metrics
    
    def _analyze_python_ast(self, file_path: str, content: str, metrics: FileMetrics) -> FileMetrics:
        """使用AST分析Python文件"""
        try:
            tree = ast.parse(content)
            
            # 统计类
            metrics.classes = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef)))
            
            # 分析函数
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_metrics = self._analyze_function_ast(node)
                    metrics.functions.append(func_metrics)
            
            # 计算整体复杂度
            metrics.complexity_score = self._calculate_ast_complexity(tree)
            
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
        
        return metrics
    
    def _analyze_function_ast(self, node) -> FunctionMetrics:
        """分析函数AST节点"""
        # 计算圈复杂度
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                complexity += 1
            elif isinstance(child, ast.For):
                complexity += 1
            elif isinstance(child, ast.While):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)  # 每个except子句
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.And):
                complexity += len(child.values) - 1
        
        # 检测递归
        has_recursion = False
        func_name = node.name
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and hasattr(child.func, 'id') and child.func.id == func_name:
                has_recursion = True
                break
        
        # 检测循环和异常
        has_loops = any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(node))
        has_exception = any(isinstance(child, ast.Try) for child in ast.walk(node))
        
        return FunctionMetrics(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            cyclomatic_complexity=complexity,
            num_params=len(node.args.args),
            num_variables=len([n for n in ast.walk(node) if isinstance(n, ast.Name)]),
            num_statements=len([n for n in ast.walk(node) if isinstance(n, ast.stmt)]),
            has_recursion=has_recursion,
            has_loops=has_loops,
            has_exception=has_exception
        )
    
    def _calculate_ast_complexity(self, tree) -> float:
        """计算整体复杂度分数"""
        total_complexity = 0
        total_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, ast.If):
                        complexity += 1
                    elif isinstance(child, (ast.For, ast.While)):
                        complexity += 1
                    elif isinstance(child, ast.Try):
                        complexity += len(child.handlers)
                total_complexity += complexity
                total_functions += 1
        
        # 加权计算
        if total_functions == 0:
            return 0
        
        avg_complexity = total_complexity / total_functions
        return round(avg_complexity * total_functions ** 0.5, 2)
    
    def _calculate_simple_complexity(self, content: str) -> float:
        """简单复杂度计算（非Python文件）"""
        complexity = 0
        
        # 计算决策点
        complexity += content.count('if ')
        complexity += content.count('else')
        complexity += content.count('elif ')
        complexity += content.count('for ')
        complexity += content.count('while ')
        complexity += content.count('case ')
        complexity += content.count('&&')
        complexity += content.count('||')
        complexity += content.count('? ')
        
        # 函数数量
        complexity += content.count('function ') * 2
        complexity += content.count('def ') * 2
        
        return round(complexity / 50, 2)
    
    def _extract_functions_simple(self, content: str, metrics: FileMetrics):
        """简单提取函数信息"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测函数定义
            if stripped.startswith('function ') or stripped.startswith('def '):
                match = re.match(r'(function|def)\s+(\w+)', stripped)
                if match:
                    func_name = match.group(2)
                    func_metrics = FunctionMetrics(
                        name=func_name,
                        line_start=i + 1,
                        line_end=i + 1,
                        cyclomatic_complexity=self._count_branch_points(lines[i:]),
                        num_params=stripped.count(',') + 1 if '(' in stripped else 0,
                        num_variables=0,
                        num_statements=0
                    )
                    metrics.functions.append(func_metrics)
    
    def _count_branch_points(self, lines: List[str]) -> int:
        """计算分支点数量"""
        complexity = 1
        for line in lines[:20]:  # 只检查前20行作为简单估计
            if any(keyword in line for keyword in ['if', 'for', 'while', 'catch', 'case']):
                complexity += 1
        return complexity
    
    def get_summary(self) -> Dict:
        """获取分析摘要"""
        if not self.files:
            return {}
        
        total_lines = sum(f.total_lines for f in self.files.values())
        total_complexity = sum(f.complexity_score for f in self.files.values())
        avg_complexity = total_complexity / len(self.files) if self.files else 0
        
        # 找出最复杂的函数
        all_functions = []
        for file in self.files.values():
            all_functions.extend(file.functions)
        all_functions.sort(key=lambda x: x.cyclomatic_complexity, reverse=True)
        
        # 技术债务估算（小时）
        technical_debt = 0
        for func in all_functions:
            if func.cyclomatic_complexity > 10:
                technical_debt += (func.cyclomatic_complexity - 10) * 2
        
        return {
            "files_analyzed": len(self.files),
            "total_lines": total_lines,
            "average_complexity": round(avg_complexity, 2),
            "total_functions": len(all_functions),
            "high_complexity_functions": len([f for f in all_functions if f.cyclomatic_complexity > 10]),
            "technical_debt_hours": technical_debt,
            "most_complex_functions": [
                {
                    "name": f.name,
                    "complexity": f.cyclomatic_complexity,
                    "level": f.complexity_level
                }
                for f in all_functions[:5]
            ],
            "maintainability_score": self._calculate_maintainability_score(avg_complexity, total_lines, len(all_functions))
        }
    
    def _calculate_maintainability_score(self, avg_complexity: float, total_lines: int, num_functions: int) -> float:
        """计算可维护性分数 (0-100)"""
        # 基础分数
        score = 100
        
        # 复杂度惩罚
        score -= avg_complexity * 2
        
        # 代码量惩罚（超过1000行）
        if total_lines > 1000:
            score -= (total_lines - 1000) / 100
        
        # 函数过多惩罚
        if num_functions > 50:
            score -= (num_functions - 50) / 5
        
        return max(0, min(100, round(score, 2)))
    
    def generate_html_report(self, output_path: str = "complexity_report.html"):
        """生成HTML报告"""
        summary = self.get_summary()
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码复杂度分析报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .maintainability {{
            padding: 30px;
            text-align: center;
        }}
        .score-circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: conic-gradient(#667eea 0% {summary.get('maintainability_score', 0)}%, #eee {summary.get('maintainability_score', 0)}% 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            position: relative;
        }}
        .score-inner {{
            width: 120px;
            height: 120px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }}
        .score-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .score-label {{
            font-size: 0.9em;
            color: #666;
        }}
        .file-list {{
            padding: 30px;
        }}
        .file-item {{
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .file-name {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .file-stats {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .stat {{
            font-size: 0.9em;
            color: #666;
        }}
        .complexity-high {{ border-left-color: #e74c3c; }}
        .complexity-medium {{ border-left-color: #f39c12; }}
        .complexity-low {{ border-left-color: #27ae60; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f5f7fa;
            font-weight: 600;
        }}
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .badge-green {{ background: #d4edda; color: #155724; }}
        .badge-yellow {{ background: #fff3cd; color: #856404; }}
        .badge-red {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 代码复杂度分析报告</h1>
            <p>生成时间: {summary.get('files_analyzed', 0)} 个文件已分析</p>
        </div>
        
        <div class="summary-grid">
            <div class="stat-card">
                <div class="stat-value">{summary.get('files_analyzed', 0)}</div>
                <div class="stat-label">📁 分析文件数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('total_lines', 0):,}</div>
                <div class="stat-label">📝 总代码行数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('total_functions', 0)}</div>
                <div class="stat-label">⚡ 函数总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('high_complexity_functions', 0)}</div>
                <div class="stat-label">⚠️ 高复杂度函数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('technical_debt_hours', 0)}h</div>
                <div class="stat-label">🔧 预估技术债务</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('average_complexity', 0)}</div>
                <div class="stat-label">📈 平均复杂度</div>
            </div>
        </div>
        
        <div class="maintainability">
            <h2>可维护性指数</h2>
            <div class="score-circle">
                <div class="score-inner">
                    <div class="score-value">{summary.get('maintainability_score', 0)}</div>
                    <div class="score-label">分</div>
                </div>
            </div>
            <p style="color: #666;">
                {"🟢 优秀" if summary.get('maintainability_score', 0) >= 80 else "🟡 良好" if summary.get('maintainability_score', 0) >= 60 else "🔴 需改进"}
            </p>
        </div>
        
        <div class="file-list">
            <h2>📋 最复杂的函数 Top 10</h2>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>函数名</th>
                        <th>圈复杂度</th>
                        <th>复杂度等级</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for i, func in enumerate(summary.get('most_complex_functions', [])[:10], 1):
            badge_class = 'badge-green' if func['complexity'] <= 10 else 'badge-yellow' if func['complexity'] <= 20 else 'badge-red'
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td><code>{func['name']}</code></td>
                        <td>{func['complexity']}</td>
                        <td><span class="badge {badge_class}">{func['level']}</span></td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="file-list">
            <h2>📁 文件详情</h2>
"""
        
        for file_path, metrics in sorted(self.files.items(), key=lambda x: x[1].complexity_score, reverse=True):
            file_name = os.path.basename(file_path)
            complexity_class = 'complexity-high' if metrics.complexity_score > 10 else 'complexity-medium' if metrics.complexity_score > 5 else 'complexity-low'
            html += f"""
            <div class="file-item {complexity_class}">
                <div class="file-name">{file_name}</div>
                <div class="file-stats">
                    <span class="stat">📝 代码: {metrics.code_lines} 行</span>
                    <span class="stat">💬 注释: {metrics.comment_lines} 行</span>
                    <span class="stat">⚪ 空白: {metrics.blank_lines} 行</span>
                    <span class="stat">⚡ 函数: {len(metrics.functions)} 个</span>
                    <span class="stat">📊 复杂度: {metrics.complexity_score}</span>
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML报告已生成: {output_path}")
        return output_path


def demo():
    """演示"""
    print("=" * 60)
    print("智能代码复杂度分析器 - 演示")
    print("=" * 60)
    
    # 创建示例文件用于测试
    sample_code = '''
"""
示例代码 - 用于测试复杂度分析
"""

def simple_function(x, y):
    """简单的加法函数"""
    return x + y

def complex_function(n):
    """复杂的递归函数"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 2
    else:
        # 递归调用
        return complex_function(n-1) + complex_function(n-2)

def very_complex_function(data):
    """
    非常复杂的函数，包含多个分支和循环
    """
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
        elif item == 0:
            result.append(0)
        else:
            try:
                result.append(1 / item)
            except ZeroDivisionError:
                result.append(0)
    
    if result:
        return sum(result)
    return None

class SampleClass:
    """示例类"""
    
    def method_one(self):
        """简单方法"""
        x = 1
        y = 2
        return x + y
    
    def method_with_many_branches(self, value):
        """有很多分支的方法"""
        if value < 10:
            if value < 5:
                return "small"
            else:
                return "medium"
        elif value < 100:
            if value < 50:
                return "large"
            else:
                return "very large"
        else:
            if value < 1000:
                return "huge"
            else:
                return "enormous"
'''
    
    # 写入测试文件
    test_file = "sample_complexity.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(sample_code)
    
    # 分析
    analyzer = ComplexityAnalyzer()
    metrics = analyzer.analyze_file(test_file)
    
    print(f"\n📊 分析结果: {test_file}")
    print(f"   总行数: {metrics.total_lines}")
    print(f"   代码行数: {metrics.code_lines}")
    print(f"   注释行数: {metrics.comment_lines}")
    print(f"   空白行数: {metrics.blank_lines}")
    print(f"   复杂度分数: {metrics.complexity_score}")
    print(f"   函数数量: {len(metrics.functions)}")
    
    print("\n⚡ 函数详情:")
    for func in metrics.functions:
        badge = "🟢" if func.cyclomatic_complexity <= 10 else "🟡" if func.cyclomatic_complexity <= 20 else "🔴"
        print(f"   {badge} {func.name}(): 复杂度={func.cyclomatic_complexity}, 等级={func.complexity_level}")
    
    # 获取摘要
    print("\n📈 摘要信息:")
    analyzer.files[test_file] = metrics
    summary = analyzer.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # 生成HTML报告
    print("\n🎨 生成HTML报告...")
    analyzer.generate_html_report("complexity_report.html")
    
    # 清理测试文件
    os.remove(test_file)
    print("\n✅ 演示完成！")
    print("\n使用说明:")
    print("  python 2026-02-03_061_smart_complexity_analyzer.py demo")
    print("  python 2026-02-03_061_smart_complexity_analyzer.py analyze <path>")
    print("  python 2026-02-03_061_smart_complexity_analyzer.py report <path> --html")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        demo()
        return
    
    command = sys.argv[1]
    
    if command == "demo":
        demo()
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("用法: analyze <path>")
            return
        
        path = sys.argv[2]
        analyzer = ComplexityAnalyzer()
        
        if os.path.isfile(path):
            metrics = analyzer.analyze_file(path)
            print(f"\n📊 文件分析: {path}")
            print(f"   总行数: {metrics.total_lines}")
            print(f"   复杂度: {metrics.complexity_score}")
            print(f"   函数: {len(metrics.functions)}")
        else:
            files = analyzer.analyze_directory(path)
            print(f"\n📊 目录分析: {path}")
            print(f"   文件数: {len(files)}")
            summary = analyzer.get_summary()
            print(f"   平均复杂度: {summary.get('average_complexity', 0)}")
            print(f"   可维护性: {summary.get('maintainability_score', 0)}")
    
    elif command == "report":
        # 解析参数
        if len(sys.argv) < 3:
            print("用法: report <path> [--html]")
            return
        
        path = sys.argv[2]
        output_html = "--html" in sys.argv
        
        analyzer = ComplexityAnalyzer()
        
        if os.path.isfile(path):
            metrics = analyzer.analyze_file(path)
            analyzer.files[path] = metrics
        else:
            analyzer.analyze_directory(path)
        
        summary = analyzer.get_summary()
        print("\n" + "=" * 60)
        print("📊 代码复杂度分析报告")
        print("=" * 60)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        
        if output_html:
            analyzer.generate_html_report()
    
    else:
        print(f"未知命令: {command}")
        print("可用命令: demo, analyze, report")


if __name__ == "__main__":
    main()
