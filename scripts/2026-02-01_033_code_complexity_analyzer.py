#!/usr/bin/env python3
"""
代码复杂度分析器 - Code Complexity Analyzer
===========================================
分析Python代码的圈复杂度(Cyclomatic Complexity)和代码质量指标

功能:
- 计算圈复杂度 (Cyclomatic Complexity)
- 统计代码行数、函数数、类数
- 评估代码质量评分
- 生成详细分析报告
"""

import ast
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class ComplexityLevel(Enum):
    """复杂度等级"""
    A = "A"  # 非常简单 (1-5)
    B = "B"  # 简单 (6-10)
    C = "C"  # 中等 (11-20)
    D = "D"  # 复杂 (21-30)
    E = "E"  # 非常复杂 (31-40)
    F = "F"  # 极高 (>40)


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    complexity: int
    line_start: int
    line_end: int
    params_count: int
    docstring: str = ""
    nested_functions: List['FunctionInfo'] = field(default_factory=list)
    
    @property
    def complexity_level(self) -> ComplexityLevel:
        if self.complexity <= 5:
            return ComplexityLevel.A
        elif self.complexity <= 10:
            return ComplexityLevel.B
        elif self.complexity <= 20:
            return ComplexityLevel.C
        elif self.complexity <= 30:
            return ComplexityLevel.D
        elif self.complexity <= 40:
            return ComplexityLevel.E
        return ComplexityLevel.F


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    complexity: int
    line_start: int
    line_end: int
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: str = ""


@dataclass
class CodeAnalysisResult:
    """代码分析结果"""
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    quality_score: float = 0.0
    
    @property
    def avg_complexity(self) -> float:
        all_funcs = self.functions + [m for c in self.classes for m in c.methods]
        if not all_funcs:
            return 0.0
        return sum(f.complexity for f in all_funcs) / len(all_funcs)


class CodeComplexityAnalyzer:
    """代码复杂度分析器"""
    
    # 复杂度阈值
    COMPLEXITY_THRESHOLDS = {
        'excellent': 5,
        'good': 10,
        'acceptable': 20,
        'warning': 30,
        'critical': 40
    }
    
    def __init__(self, file_path: str = None, code: str = None):
        """
        初始化分析器
        
        Args:
            file_path: Python文件路径
            code: Python代码字符串
        """
        self.file_path = file_path
        self.code = code
        self._ast_tree: ast.AST = None
        
    def load_code(self) -> str:
        """加载代码"""
        if self.code is None and self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.code = f.read()
        return self.code
    
    def _count_lines(self) -> Tuple[int, int, int, int]:
        """统计代码行数"""
        if not self.code:
            return 0, 0, 0, 0
            
        lines = self.code.split('\n')
        total = len(lines)
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # 多行注释检测
            if '"""' in stripped or "'''" in stripped:
                # 简单的多行注释检测
                if not in_multiline_comment:
                    in_multiline_comment = True
                    comment_lines += 1
                    continue
                else:
                    in_multiline_comment = False
                    comment_lines += 1
                    continue
            
            if in_multiline_comment:
                comment_lines += 1
                continue
            
            # 单行注释
            if stripped.startswith('#'):
                comment_lines += 1
            elif not stripped:
                blank_lines += 1
            else:
                code_lines += 1
        
        return total, code_lines, comment_lines, blank_lines
    
    def _count_decisions(self, node: ast.AST) -> int:
        """
        计算决策点数量 (圈复杂度核心)
        
        决策点:
        - if, elif, while, for, except, with, assert, and, or, ternary (? :)
        """
        count = 1  # 基础路径
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                count += 1
            elif isinstance(child, ast.With):
                count += 1  # with 语句增加复杂度
            elif isinstance(child, ast.Assert):
                count += 1
            elif isinstance(child, ast.BoolOp):
                # and, or 运算符
                if isinstance(child.op, (ast.And, ast.Or)):
                    count += len(child.values)
            elif isinstance(child, ast.Ternary):
                count += 1
        
        return count
    
    def _extract_docstring(self, node: ast.AST) -> str:
        """提取文档字符串"""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.body and isinstance(node.body[0], ast.Expr):
                if isinstance(node.body[0].value, (ast.Constant, ast.Str)):
                    return ast.get_docstring(node) or ""
        return ""
    
    def _analyze_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """分析单个函数"""
        complexity = self._count_decisions(node)
        
        return FunctionInfo(
            name=node.name,
            complexity=complexity,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            params_count=len(node.args.args),
            docstring=self._extract_docstring(node)
        )
    
    def _analyze_class(self, node: ast.ClassDef) -> ClassInfo:
        """分析单个类"""
        class_info = ClassInfo(
            name=node.name,
            complexity=1,  # 基础复杂度
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            base_classes=[base.id for base in node.bases if isinstance(base, ast.Name)],
            docstring=self._extract_docstring(node)
        )
        
        # 分析类中的方法
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._analyze_function(item)
                class_info.complexity += method.complexity
                class_info.methods.append(method)
        
        return class_info
    
    def _extract_imports(self) -> List[str]:
        """提取导入语句"""
        imports = []
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        return imports
    
    def _calculate_quality_score(self, result: CodeAnalysisResult) -> float:
        """计算代码质量评分 (0-100)"""
        score = 100.0
        
        # 圈复杂度扣分
        avg_complexity = result.avg_complexity
        if avg_complexity > self.COMPLEXITY_THRESHOLDS['excellent']:
            score -= (avg_complexity - self.COMPLEXITY_THRESHOLDS['excellent']) * 2
        if avg_complexity > self.COMPLEXITY_THRESHOLDS['acceptable']:
            score -= 10
        
        # 文件过大扣分
        if result.code_lines > 500:
            score -= 5
        elif result.code_lines > 1000:
            score -= 10
        
        # 注释比例 (理想是15-30%)
        if result.total_lines > 0:
            comment_ratio = result.comment_lines / result.total_lines
            if comment_ratio < 0.05:
                score -= 10
            elif comment_ratio > 0.5:
                score -= 5
        
        # 缺少文档字符串扣分
        all_funcs = result.functions + [m for c in result.classes for m in c.methods]
        if all_funcs:
            undocumented = sum(1 for f in all_funcs if not f.docstring)
            if undocumented > len(all_funcs) * 0.5:
                score -= 10
        
        return max(0, min(100, score))
    
    def analyze(self) -> CodeAnalysisResult:
        """执行完整分析"""
        self.load_code()
        
        result = CodeAnalysisResult()
        
        # 1. 统计行数
        (result.total_lines, result.code_lines, 
         result.comment_lines, result.blank_lines) = self._count_lines()
        
        # 2. 解析AST
        try:
            self._ast_tree = ast.parse(self.code)
        except SyntaxError as e:
            print(f"⚠️  解析错误: {e}")
            return result
        
        # 3. 分析函数和类
        for node in ast.walk(self._ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 只处理顶层函数
                if isinstance(node.parent, (ast.Module, ast.FunctionDef)):
                    func_info = self._analyze_function(node)
                    result.functions.append(func_info)
                    
            elif isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node)
                result.classes.append(class_info)
        
        # 4. 提取导入
        result.imports = self._extract_imports()
        
        # 5. 计算复杂度分数
        total_complexity = sum(f.complexity for f in result.functions)
        for cls in result.classes:
            total_complexity += cls.complexity
            total_complexity += sum(m.complexity for m in cls.methods)
        
        result.complexity_score = total_complexity
        
        # 6. 计算质量分数
        result.quality_score = self._calculate_quality_score(result)
        
        return result
    
    def print_report(self, result: CodeAnalysisResult = None) -> str:
        """生成格式化的分析报告"""
        if result is None:
            result = self.analyze()
        
        report_lines = []
        
        # 标题
        report_lines.append("=" * 60)
        report_lines.append("📊 代码复杂度分析报告")
        report_lines.append("=" * 60)
        
        # 基础统计
        report_lines.append("\n📈 基础统计")
        report_lines.append("-" * 40)
        report_lines.append(f"  总行数:     {result.total_lines}")
        report_lines.append(f"  代码行:     {result.code_lines}")
        report_lines.append(f"  注释行:     {result.comment_lines}")
        report_lines.append(f"  空白行:     {result.blank_lines}")
        if result.total_lines > 0:
            comment_ratio = result.comment_lines / result.total_lines * 100
            report_lines.append(f"  注释比例:   {comment_ratio:.1f}%")
        
        # 复杂度统计
        report_lines.append("\n🔄 复杂度分析")
        report_lines.append("-" * 40)
        report_lines.append(f"  总复杂度:   {result.complexity_score}")
        report_lines.append(f"  平均复杂度: {result.avg_complexity:.2f}")
        report_lines.append(f"  质量评分:   {result.quality_score:.1f}/100")
        
        # 实体统计
        report_lines.append("\n📦 代码实体")
        report_lines.append("-" * 40)
        report_lines.append(f"  类数量:     {len(result.classes)}")
        report_lines.append(f"  函数数量:   {len(result.functions)}")
        report_lines.append(f"  导入数量:   {len(result.imports)}")
        
        # 复杂度详情
        all_funcs = result.functions + [m for c in result.classes for m in c.methods]
        if all_funcs:
            report_lines.append("\n🔥 高复杂度函数 TOP 10")
            report_lines.append("-" * 40)
            sorted_funcs = sorted(all_funcs, key=lambda x: x.complexity, reverse=True)[:10]
            for i, func in enumerate(sorted_funcs, 1):
                level = func.complexity_level.value
                level_emoji = {
                    'A': '🟢', 'B': '🔵', 'C': '🟡', 
                    'D': '🟠', 'E': '🔴', 'F': '⚫'
                }.get(level, '⚪')
                
                report_lines.append(
                    f"  {i:2d}. {level_emoji} {func.name}() "
                    f"[{func.complexity}] ({func.line_start}-{func.line_end}行)"
                )
        
        # 类详细信息
        if result.classes:
            report_lines.append("\n🏗️  类详细信息")
            report_lines.append("-" * 40)
            for cls in result.classes:
                method_count = len(cls.methods)
                avg_method_complexity = (
                    sum(m.complexity for m in cls.methods) / method_count 
                    if method_count > 0 else 0
                )
                report_lines.append(f"  📁 {cls.name}")
                report_lines.append(f"      方法数: {method_count}")
                report_lines.append(f"      复杂度: {cls.complexity}")
                report_lines.append(f"      平均方法复杂度: {avg_method_complexity:.2f}")
        
        # 质量评估
        report_lines.append("\n💯 质量评估")
        report_lines.append("-" * 40)
        score = result.quality_score
        if score >= 90:
            grade = "⭐⭐⭐⭐⭐ 优秀"
        elif score >= 80:
            grade = "⭐⭐⭐⭐ 良好"
        elif score >= 70:
            grade = "⭐⭐⭐ 一般"
        elif score >= 60:
            grade = "⭐⭐ 需改进"
        else:
            grade = "⭐ 需重构"
        
        report_lines.append(f"  评分: {score:.1f} - {grade}")
        
        # 建议
        report_lines.append("\n💡 改进建议")
        report_lines.append("-" * 40)
        
        avg_c = result.avg_complexity
        if avg_c > self.COMPLEXITY_THRESHOLDS['acceptable']:
            report_lines.append("  ⚠️  圈复杂度偏高，建议拆分复杂函数")
        if result.comment_lines / max(1, result.total_lines) < 0.1:
            report_lines.append("  📝  注释较少，建议增加文档说明")
        
        high_complexity_funcs = [f for f in all_funcs if f.complexity > 20]
        if high_complexity_funcs:
            report_lines.append(f"  🔧  有{len(high_complexity_funcs)}个函数复杂度>20，建议重构")
        
        report_lines.append("\n" + "=" * 60)
        
        report = '\n'.join(report_lines)
        print(report)
        return report
    
    @staticmethod
    def analyze_file(file_path: str) -> CodeAnalysisResult:
        """便捷方法: 分析文件"""
        analyzer = CodeComplexityAnalyzer(file_path=file_path)
        return analyzer.analyze()
    
    @staticmethod
    def analyze_code(code: str) -> CodeAnalysisResult:
        """便捷方法: 分析代码字符串"""
        analyzer = CodeComplexityAnalyzer(code=code)
        return analyzer.analyze()


# ========== 示例使用 ==========
if __name__ == "__main__":
    # 示例代码
    sample_code = '''
import os
import sys
from typing import List, Dict

class UserManager:
    """用户管理类"""
    
    def __init__(self):
        self.users = {}
    
    def add_user(self, name: str, age: int, email: str) -> bool:
        """添加用户"""
        if not name or not email:
            return False
        if age < 0 or age > 150:
            return False
        
        if email in self.users:
            return False
        
        self.users[email] = {"name": name, "age": age}
        return True
    
    def process_user(self, email: str) -> Dict:
        """处理用户逻辑"""
        if email not in self.users:
            return {}
        
        user = self.users[email]
        name = user.get("name", "")
        age = user.get("age", 0)
        
        # 复杂逻辑
        if age < 18:
            status = "minor"
        elif age < 60:
            status = "adult"
        else:
            status = "senior"
        
        if name and email and age:
            return {"status": status, "valid": True}
        return {"status": status, "valid": False}
    
    def validate_and_update(self, email: str, new_data: Dict) -> bool:
        """验证并更新用户"""
        if not email:
            return False
        
        if email not in self.users:
            return False
        
        user = self.users[email]
        
        # 嵌套条件
        if "name" in new_data and new_data["name"]:
            if len(new_data["name"]) > 0:
                user["name"] = new_data["name"]
        
        if "age" in new_data:
            if isinstance(new_data["age"], int):
                if 0 <= new_data["age"] <= 150:
                    user["age"] = new_data["age"]
        
        return True

def complex_function(a: int, b: int, c: int) -> int:
    """复杂函数示例"""
    result = 0
    
    if a > 0:
        if b > 0:
            if c > 0:
                result = a + b + c
            else:
                result = a + b
        else:
            if c > 0:
                result = a + c
            else:
                result = a
    else:
        if b > 0:
            if c > 0:
                result = b + c
            else:
                result = b
        else:
            if c > 0:
                result = c
            else:
                result = 0
    
    return result

def simple_adder(x: int, y: int) -> int:
    """简单加法函数"""
    return x + y
'''
    
    print("🧪 测试代码复杂度分析器...\n")
    
    # 分析示例代码
    analyzer = CodeComplexityAnalyzer(code=sample_code)
    result = analyzer.analyze()
    analyzer.print_report(result)
    
    print("\n" + "=" * 60)
    print("🎯 演示完成!")
