#!/usr/bin/env python3
"""
智能代码复杂度分析器
Code Complexity Analyzer

功能:
- 分析Python代码的圈复杂度(Cyclomatic Complexity)
- 统计代码行数、函数数量、类数量
- 检测代码异味(Code Smells)
- 生成可视化报告

使用方法:
    python code_complexity_analyzer.py [文件路径]
"""

import ast
import os
import sys
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class ComplexityAnalyzer(ast.NodeVisitor):
    """基于AST的代码复杂度分析器"""
    
    def __init__(self):
        self.complexity_scores = []
        self.functions = []
        self.classes = []
        self.total_lines = 0
        self.code_lines = 0
        self.comment_lines = 0
        self.blank_lines = 0
        self.current_class = None
        self.current_function = None
        self.branch_count = 1  # 基础分支
        
    def analyze(self, source_code: str) -> Dict[str, Any]:
        """执行完整分析"""
        self.complexity_scores = []
        self.functions = []
        self.classes = []
        self.branch_count = 1
        
        # 统计行数
        lines = source_code.split('\n')
        self.total_lines = len(lines)
        for line in lines:
            stripped = line.strip()
            if not stripped:
                self.blank_lines += 1
            elif stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                self.comment_lines += 1
            else:
                self.code_lines += 1
        
        # 解析AST
        try:
            tree = ast.parse(source_code)
            self.visit(tree)
        except SyntaxError:
            pass
        
        return self.get_report()
    
    def visit_If(self, node: ast.If) -> None:
        self.branch_count += 1  # if分支
        if node.orelse:
            self.branch_count += 1  # else分支
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For) -> None:
        self.branch_count += 1
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While) -> None:
        self.branch_count += 1
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try) -> None:
        self.branch_count += 1  # try
        for handler in node.handlers:
            self.branch_count += 1  # except
        if node.orelse:
            self.branch_count += 1  # else
        if node.finalbody:
            self.branch_count += 1  # finally
        self.generic_visit(node)
    
    def visit_Assert(self, node: ast.Assert) -> None:
        self.branch_count += 1
        self.generic_visit(node)
    
    def visit_Comprehension(self, node: ast.Comprehension) -> None:
        self.branch_count += 1
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        func_name = node.name
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        # 计算函数复杂度
        func_complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.Assert)):
                if isinstance(child, ast.Try):
                    func_complexity += len(child.handlers) + 1
                else:
                    func_complexity += 1
        
        self.functions.append({
            'name': func_name,
            'complexity': func_complexity,
            'start_line': start_line,
            'end_line': end_line,
            'line_count': end_line - start_line + 1,
            'class': self.current_class
        })
        
        old_class = self.current_class
        self.current_function = func_name
        self.generic_visit(node)
        self.current_function = None
        
        if self.current_class:
            self.complexity_scores.append((f"{self.current_class}.{func_name}", func_complexity))
        else:
            self.complexity_scores.append((func_name, func_complexity))
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name = node.name
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        self.classes.append({
            'name': class_name,
            'start_line': start_line,
            'end_line': end_line,
            'line_count': end_line - start_line + 1,
            'method_count': 0
        })
        
        old_class = self.current_class
        self.current_class = class_name
        self.generic_visit(node)
        self.current_class = old_class
    
    def get_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        avg_complexity = sum(c[1] for c in self.complexity_scores) / len(self.complexity_scores) if self.complexity_scores else 1
        max_complexity = max((c[1] for c in self.complexity_scores), default=1)
        
        # 检测高复杂度函数
        complex_functions = [f for f in self.functions if f['complexity'] > 10]
        
        # 统计类的方法数量
        class_methods = defaultdict(int)
        for func in self.functions:
            if func['class']:
                class_methods[func['class']] += 1
        
        for cls in self.classes:
            cls['method_count'] = class_methods.get(cls['name'], 0)
        
        return {
            'total_lines': self.total_lines,
            'code_lines': self.code_lines,
            'comment_lines': self.comment_lines,
            'blank_lines': self.blank_lines,
            'classes': self.classes,
            'functions': sorted(self.functions, key=lambda x: x['complexity'], reverse=True),
            'complex_functions': complex_functions,
            'average_complexity': round(avg_complexity, 2),
            'max_complexity': max_complexity,
            'health_score': self.calculate_health_score()
        }
    
    def calculate_health_score(self) -> int:
        """计算代码健康度评分(0-100)"""
        score = 100
        
        # 扣分项
        for func in self.functions:
            if func['complexity'] > 20:
                score -= 10
            elif func['complexity'] > 10:
                score -= 5
        
        if self.comment_lines / max(self.code_lines, 1) < 0.1:
            score -= 10
        
        return max(0, score)


def analyze_file(file_path: str) -> Dict[str, Any]:
    """分析单个文件"""
    if not os.path.exists(file_path):
        return {'error': f'文件不存在: {file_path}'}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    analyzer = ComplexityAnalyzer()
    return analyzer.analyze(source)


def print_report(report: Dict[str, Any], file_name: str = '') -> None:
    """打印格式化报告"""
    print(f"\n{'='*60}")
    print(f"📊 代码复杂度分析报告: {file_name}")
    print(f"{'='*60}")
    
    print(f"\n📈 基本统计:")
    print(f"  总行数: {report['total_lines']}")
    print(f"  代码行: {report['code_lines']}")
    print(f"  注释行: {report['comment_lines']}")
    print(f"  空白行: {report['blank_lines']}")
    
    print(f"\n🏗️  结构分析:")
    print(f"  类数量: {len(report['classes'])}")
    print(f"  函数数量: {len(report['functions'])}")
    
    if report['classes']:
        print(f"\n📦 类详情:")
        for cls in report['classes'][:5]:
            print(f"  • {cls['name']} (第{cls['start_line']}-{cls['end_line']}行, {cls['method_count']}个方法)")
    
    print(f"\n🔍 复杂度分析:")
    print(f"  平均复杂度: {report['average_complexity']}")
    print(f"  最高复杂度: {report['max_complexity']}")
    print(f"  健康度评分: {'🟢' if report['health_score'] >= 80 else '🟡' if report['health_score'] >= 60 else '🔴'} {report['health_score']}/100")
    
    if report['complex_functions']:
        print(f"\n⚠️  高复杂度函数 (需重构):")
        for func in report['complex_functions'][:5]:
            prefix = f"  • {func['class']}.{func['name']}" if func['class'] else f"  • {func['name']}"
            print(f"    {prefix} (复杂度:{func['complexity']}, 第{func['start_line']}-{func['end_line']}行)")
    
    print(f"\n📝 复杂度TOP5函数:")
    for i, func in enumerate(report['functions'][:5], 1):
        complexity_bar = '█' * min(func['complexity'], 20)
        prefix = f"{func['class']}.{func['name']}" if func['class'] else func['name']
        print(f"  {i}. {prefix}")
        print(f"     复杂度: {complexity_bar} {func['complexity']}")
    
    print(f"{'='*60}\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 分析当前文件本身
        file_path = __file__
    else:
        file_path = sys.argv[1]
    
    if os.path.isdir(file_path):
        # 分析目录下的所有.py文件
        for root, dirs, files in os.walk(file_path):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    report = analyze_file(full_path)
                    if 'error' not in report:
                        print_report(report, file)
    else:
        # 分析单个文件
        report = analyze_file(file_path)
        if 'error' in report:
            print(f"❌ 错误: {report['error']}")
        else:
            print_report(report, os.path.basename(file_path))


if __name__ == '__main__':
    main()
