#!/usr/bin/env python3
"""
🧠 Smart Code Complexity Analyzer
智能代码复杂度分析器

分析代码复杂度、圈复杂度(Cyclomatic Complexity)、代码行数、函数嵌套深度等指标。
"""

import ast
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ComplexityLevel(Enum):
    """复杂度等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FunctionMetrics:
    """函数指标"""
    name: str
    line_start: int
    line_end: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    parameters_count: int
    return_statements: int
    nested_depth: int
    complexity_level: ComplexityLevel
    suggestions: List[str] = field(default_factory=list)


@dataclass
class FileMetrics:
    """文件指标"""
    file_path: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    functions_count: int
    classes_count: int
    imports_count: int
    complexity_level: ComplexityLevel
    overall_score: float
    functions: List[FunctionMetrics] = field(default_factory=list)


class CodeComplexityAnalyzer:
    """代码复杂度分析器"""

    def __init__(self):
        self.keywords = {'if', 'elif', 'else', 'for', 'while', 'except',
                        'and', 'or', 'with', 'try', 'finally', 'assert'}
        self.booster_keywords = {'except', 'finally'}

    def analyze_file(self, file_path: str) -> Optional[FileMetrics]:
        """分析整个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # 基础统计
            total_lines = len(lines)
            code_lines = len([l for l in lines if l.strip() and not self._is_comment(l)])
            comment_lines = len([l for l in lines if self._is_comment(l)])
            blank_lines = len([l for l in lines if not l.strip()])

            # 导入统计
            imports_count = len(re.findall(r'^import |^from ', content, re.MULTILINE))

            # AST解析
            try:
                tree = ast.parse(content)
            except:
                return None

            functions = []
            classes_count = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes_count += 1
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            func_metrics = self._analyze_function(item, lines, node.name)
                            functions.append(func_metrics)
                elif isinstance(node, ast.FunctionDef):
                    func_metrics = self._analyze_function(node, lines)
                    functions.append(func_metrics)

            # 计算整体复杂度
            avg_cyclomatic = sum(f.cyclomatic_complexity for f in functions) / max(len(functions), 1)
            total_cyclomatic = sum(f.cyclomatic_complexity for f in functions)
            max_complexity = max([f.cyclomatic_complexity for f in functions], default=0)

            if functions:
                overall_score = max_complexity * 0.6 + avg_cyclomatic * 0.4
            else:
                overall_score = 0

            file_metrics = FileMetrics(
                file_path=file_path,
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                functions_count=len(functions),
                classes_count=classes_count,
                imports_count=imports_count,
                complexity_level=self._calculate_complexity_level(overall_score, total_cyclomatic),
                overall_score=overall_score,
                functions=functions
            )

            return file_metrics

        except Exception as e:
            print(f"Error analyzing file: {e}")
            return None

    def _analyze_function(self, node: ast.FunctionDef, lines: List[str], class_name: str = None) -> FunctionMetrics:
        """分析单个函数"""
        # 圈复杂度计算
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, ast.If):
                complexity += 1
            elif isinstance(child, ast.For):
                complexity += 1
            elif isinstance(child, ast.While):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                if isinstance(child.op, ast.And):
                    complexity += len(child.values) - 1
                elif isinstance(child.op, ast.Or):
                    complexity += len(child.values) - 1
            elif isinstance(child, ast.Assert):
                complexity += 1

        # 认知复杂度（简化版）
        cognitive = self._calculate_cognitive_complexity(node)

        # 统计
        parameters = len(node.args.args)
        returns = len([n for n in ast.walk(node) if isinstance(n, ast.Return)])

        # 嵌套深度
        nested_depth = self._calculate_nested_depth(node)

        # 生成建议
        suggestions = self._generate_suggestions(complexity, cognitive, parameters, nested_depth, node)

        return FunctionMetrics(
            name=f"{class_name}.{node.name}" if class_name else node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            cyclomatic_complexity=complexity,
            cognitive_complexity=cognitive,
            parameters_count=parameters,
            return_statements=returns,
            nested_depth=nested_depth,
            complexity_level=self._calculate_function_complexity_level(complexity),
            suggestions=suggestions
        )

    def _calculate_cognitive_complexity(self, node: ast.FunctionDef) -> int:
        """计算认知复杂度（简化算法）"""
        complexity = 0

        for child in ast.iter_child_nodes(node):
            complexity += self._recursive_cognitive(child, 0)

        return complexity

    def _recursive_cognitive(self, node: ast.NodeVisitor, depth: int) -> int:
        """递归计算认知复杂度"""
        score = 0

        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            score += 1 + depth

        for child in ast.iter_child_nodes(node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                score += self._recursive_cognitive(child, depth + 1)
            else:
                score += self._recursive_cognitive(child, depth)

        return score

    def _calculate_nested_depth(self, node: ast.FunctionDef) -> int:
        """计算嵌套深度"""
        max_depth = 0
        current_depth = 0

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)

        return max_depth

    def _calculate_complexity_level(self, overall_score: float, total_cyclomatic: int) -> ComplexityLevel:
        """计算整体复杂度等级"""
        if overall_score < 10 or total_cyclomatic < 20:
            return ComplexityLevel.LOW
        elif overall_score < 30 or total_cyclomatic < 50:
            return ComplexityLevel.MEDIUM
        elif overall_score < 50 or total_cyclomatic < 100:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.CRITICAL

    def _calculate_function_complexity_level(self, cyclomatic: int) -> ComplexityLevel:
        """计算函数复杂度等级"""
        if cyclomatic <= 5:
            return ComplexityLevel.LOW
        elif cyclomatic <= 10:
            return ComplexityLevel.MEDIUM
        elif cyclomatic <= 20:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.CRITICAL

    def _generate_suggestions(self, cyclomatic: int, cognitive: int,
                              params: int, depth: int, node: ast.FunctionDef) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if cyclomatic > 10:
            suggestions.append("⚠️ 圈复杂度较高，考虑将函数拆分为多个小函数")

        if params > 5:
            suggestions.append(f"📦 参数过多({params}个)，考虑使用字典或类来封装参数")

        if depth > 3:
            suggestions.append("🔀 嵌套过深，考虑使用早期返回或卫语句")

        if cognitive > 20:
            suggestions.append("🧠 认知复杂度较高，代码难以理解，建议重构")

        if cyclomatic > 5 and isinstance(node, ast.FunctionDef):
            suggestions.append("💡 可以使用策略模式或状态模式简化条件逻辑")

        if not suggestions:
            suggestions.append("✅ 函数结构良好，保持！")

        return suggestions

    def _is_comment(self, line: str) -> bool:
        """判断是否为注释行"""
        stripped = line.strip()
        return stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''")

    def generate_report(self, metrics: FileMetrics) -> str:
        """生成分析报告"""
        report_lines = []

        report_lines.append("=" * 60)
        report_lines.append("🧠 代码复杂度分析报告")
        report_lines.append("=" * 60)
        report_lines.append(f"\n📁 文件: {metrics.file_path}")

        # 基础统计
        report_lines.append("\n📊 基础统计:")
        report_lines.append(f"  - 总行数: {metrics.total_lines}")
        report_lines.append(f"  - 代码行: {metrics.code_lines}")
        report_lines.append(f"  - 注释行: {metrics.comment_lines}")
        report_lines.append(f"  - 空行: {metrics.blank_lines}")
        report_lines.append(f"  - 导入数: {metrics.imports_count}")

        # 结构统计
        report_lines.append("\n🏗️ 结构统计:")
        report_lines.append(f"  - 类数量: {metrics.classes_count}")
        report_lines.append(f"  - 函数数量: {metrics.functions_count}")

        # 复杂度等级
        level_emoji = {
            ComplexityLevel.LOW: "🟢",
            ComplexityLevel.MEDIUM: "🟡",
            ComplexityLevel.HIGH: "🟠",
            ComplexityLevel.CRITICAL: "🔴"
        }
        report_lines.append(f"\n🎯 复杂度等级: {level_emoji[metrics.complexity_level]} {metrics.complexity_level.value.upper()}")
        report_lines.append(f"📈 综合评分: {metrics.overall_score:.1f}/100")

        # 函数详情
        if metrics.functions:
            report_lines.append("\n" + "=" * 60)
            report_lines.append("📋 函数详情:")
            report_lines.append("=" * 60)

            for func in sorted(metrics.functions, key=lambda x: x.cyclomatic_complexity, reverse=True):
                report_lines.append(f"\n🔹 {func.name} (第{func.line_start}-{func.line_end}行)")
                report_lines.append(f"   圈复杂度: {func.cyclomatic_complexity} | "
                                 f"认知复杂度: {func.cognitive_complexity}")
                report_lines.append(f"   参数: {func.parameters_count} | 返回: {func.return_statements} | "
                                 f"嵌套深度: {func.nested_depth}")
                report_lines.append(f"   等级: {level_emoji[func.complexity_level]} {func.complexity_level.value.upper()}")
                report_lines.append("   💡 建议:")
                for suggestion in func.suggestions:
                    report_lines.append(f"      {suggestion}")

        # 总结
        report_lines.append("\n" + "=" * 60)
        report_lines.append("📝 总结")
        report_lines.append("=" * 60)

        if metrics.complexity_level == ComplexityLevel.LOW:
            report_lines.append("✅ 代码复杂度低，可维护性好！")
        elif metrics.complexity_level == ComplexityLevel.MEDIUM:
            report_lines.append("⚠️ 代码复杂度中等，建议优化高复杂度函数")
        elif metrics.complexity_level == ComplexityLevel.HIGH:
            report_lines.append("🚨 代码复杂度较高，需要重点重构！")
        else:
            report_lines.append("🛑 代码复杂度极高，建议立即重构！")

        return '\n'.join(report_lines)


def demo():
    """演示"""
    analyzer = CodeComplexityAnalyzer()

    # 分析当前文件本身
    current_file = __file__
    print(f"\n🔍 分析文件: {current_file}\n")

    metrics = analyzer.analyze_file(current_file)

    if metrics:
        report = analyzer.generate_report(metrics)
        print(report)
    else:
        print("❌ 无法分析文件")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # 分析指定文件
        file_path = sys.argv[1]
        analyzer = CodeComplexityAnalyzer()
        metrics = analyzer.analyze_file(file_path)

        if metrics:
            report = analyzer.generate_report(metrics)
            print(report)
        else:
            print(f"❌ 无法分析文件: {file_path}")
    else:
        # 演示
        demo()
