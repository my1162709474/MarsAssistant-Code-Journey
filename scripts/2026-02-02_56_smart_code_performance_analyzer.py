#!/usr/bin/env python3
"""
智能代码性能分析器 - Code Performance Analyzer
============================================

一个功能强大的命令行工具，用于分析Python代码的性能瓶颈，
提供详细的性能报告和优化建议。

功能特点:
- ⏱️  执行时间分析
- 📊  内存使用分析
- 🔥  热点函数识别
- 💡  优化建议生成
- 📈  可视化报告

作者: AI Assistant
日期: 2026-02-02
"""

import time
import cProfile
import pstats
import memory_profiler
import dis
import inspect
import linecache
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import io
from contextlib import contextmanager


@dataclass
class FunctionStats:
    """函数性能统计"""
    name: str
    file: str
    line_number: int
    call_count: int = 0
    total_time: float = 0.0
    cumulative_time: float = 0.0
    per_call_time: float = 0.0
    memory_usage: float = 0.0
    ncalls_pretty: str = ""
    tottime_pretty: str = ""
    cumtime_pretty: str = ""


@dataclass
class PerformanceReport:
    """性能报告"""
    functions: List[FunctionStats] = field(default_factory=list)
    total_execution_time: float = 0.0
    peak_memory: float = 0.0
    slow_functions: List[FunctionStats] = field(default_factory=list)
    memory_hogs: List[FunctionStats] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class CodePerformanceAnalyzer:
    """代码性能分析器主类"""
    
    def __init__(self):
        self.reports_dir = Path("performance_reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        分析函数的性能
        
        Args:
            func: 要分析的函数
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数
            
        Returns:
            性能分析结果字典
        """
        # 执行性能分析
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
        finally:
            profiler.disable()
        
        # 解析分析结果
        stats = pstats.Stats(profiler)
        stats.stream = io.StringIO()
        stats.sort_stats('cumulative')
        
        functions = []
        for func_info in stats.fcn_list:
            func_stats = stats.stats[func_info]
            if func_stats:
                fs = FunctionStats(
                    name=func_info[2],
                    file=str(func_info[0]),
                    line_number=func_info[1],
                    call_count=func_stats[0],
                    total_time=func_stats[2],
                    cumulative_time=func_stats[3],
                    per_call_time=func_stats[2] / func_stats[0] if func_stats[0] > 0 else 0
                )
                functions.append(fs)
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'functions': functions,
            'profiler_stats': stats
        }
    
    def profile_memory(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        分析函数的内存使用
        
        Args:
            func: 要分析的函数
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数
            
        Returns:
            内存分析结果
        """
        start_memory = memory_profiler.memory_usage()[0]
        
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        peak_memory = memory_profiler.memory_usage()[0]
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'start_memory': start_memory,
            'peak_memory': peak_memory,
            'memory_increase': peak_memory - start_memory
        }
    
    def profile_code_string(self, code: str, setup: str = "") -> PerformanceReport:
        """
        分析代码字符串的性能
        
        Args:
            code: 要分析的Python代码
            setup: 设置代码（用于导入）
            
        Returns:
            完整的性能报告
        """
        # 创建临时函数
        local_vars = {}
        exec(setup, local_vars)
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        exec(code, local_vars)
        
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        functions = []
        for func_info in stats.stats:
            func_stats = stats.stats[func_info]
            fs = FunctionStats(
                name=func_info[2],
                file=str(func_info[0]),
                line_number=func_info[1],
                call_count=func_stats[0],
                total_time=func_stats[2],
                cumulative_time=func_stats[3],
                per_call_time=func_stats[2] / func_stats[0] if func_stats[0] > 0 else 0
            )
            functions.append(fs)
        
        # 识别慢函数
        slow_functions = sorted(
            [f for f in functions if f.call_count > 0],
            key=lambda x: x.cumulative_time,
            reverse=True
        )[:5]
        
        # 生成优化建议
        suggestions = self._generate_suggestions(functions, slow_functions)
        
        report = PerformanceReport(
            functions=functions,
            total_execution_time=sum(f.total_time for f in functions),
            slow_functions=slow_functions,
            suggestions=suggestions
        )
        
        return report
    
    def _generate_suggestions(self, functions: List[FunctionStats], 
                               slow_functions: List[FunctionStats]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 检查循环次数
        for func in slow_functions:
            if func.call_count > 1000:
                suggestions.append(
                    f"函数 '{func.name}' 被调用了 {func.call_count} 次，考虑优化调用逻辑"
                )
            
            if func.per_call_time > 0.1:
                suggestions.append(
                    f"函数 '{func.name}' 每次调用耗时 {func.per_call_time:.4f} 秒，"
                    f"考虑优化算法或使用缓存"
                )
        
        # 检查是否有重复计算
        func_names = [f.name for f in functions]
        if len(func_names) != len(set(func_names)):
            suggestions.append("检测到同名函数多次定义，可能存在重复计算")
        
        # 检查文件操作
        for func in functions:
            if 'open' in func.name.lower() or 'read' in func.name.lower() or 'write' in func.name.lower():
                suggestions.append(
                    f"函数 '{func.name}' 涉及文件操作，考虑使用缓冲或批量处理"
                )
        
        return suggestions
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析文件的性能特征
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件分析结果
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        lines = code.split('\n')
        
        # 统计代码特征
        analysis = {
            'total_lines': len(lines),
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'imports': [],
            'functions': [],
            'classes': [],
            'loops': 0,
            'complexity_score': 0
        }
        
        in_multiline_comment = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 多行注释检测
            if '"""' in stripped or "'''" in stripped:
                if stripped.count('"""') % 2 == 0 and stripped.count("'''") % 2 == 0:
                    if not in_multiline_comment:
                        in_multiline_comment = True
                    else:
                        in_multiline_comment = False
                    analysis['comment_lines'] += 1
                    continue
            
            if in_multiline_comment:
                analysis['comment_lines'] += 1
                continue
            
            # 空行
            if not stripped:
                analysis['blank_lines'] += 1
                continue
            
            # 注释行
            if stripped.startswith('#'):
                analysis['comment_lines'] += 1
                continue
            
            # 代码行
            analysis['code_lines'] += 1
            
            # 导入语句
            if stripped.startswith(('import ', 'from ')):
                analysis['imports'].append((i, stripped))
            
            # 函数定义
            if stripped.startswith('def ') or stripped.startswith('async def '):
                match = re.search(r'def\s+(\w+)', stripped)
                if match:
                    analysis['functions'].append((i, match.group(1)))
            
            # 类定义
            if stripped.startswith('class '):
                match = re.search(r'class\s+(\w+)', stripped)
                if match:
                    analysis['classes'].append((i, match.group(1)))
            
            # 循环
            if re.search(r'\b(for|while)\b', stripped):
                analysis['loops'] += 1
            
            # 复杂度估算
            analysis['complexity_score'] += len(stripped) / 100
        
        return analysis
    
    def generate_report(self, report: PerformanceReport, 
                        output_path: Optional[str] = None) -> str:
        """
        生成格式化的性能报告
        
        Args:
            report: 性能报告对象
            output_path: 输出文件路径（可选）
            
        Returns:
            格式化的报告字符串
        """
        lines = []
        lines.append("=" * 60)
        lines.append("📊 性能分析报告")
        lines.append("=" * 60)
        lines.append(f"⏱️  总执行时间: {report.total_execution_time:.4f} 秒")
        lines.append(f"📈 函数总数: {len(report.functions)}")
        lines.append("")
        
        if report.slow_functions:
            lines.append("🔥 热点函数 (Top 5):")
            lines.append("-" * 60)
            for i, func in enumerate(report.slow_functions, 1):
                lines.append(
                    f"{i}. {func.name} ({func.file}:{func.line_number})"
                )
                lines.append(f"   调用次数: {func.call_count}")
                lines.append(
                    f"   累计时间: {func.cumulative_time:.4f}s "
                    f"(每次: {func.per_call_time:.4f}s)"
                )
                lines.append("")
        
        if report.suggestions:
            lines.append("💡 优化建议:")
            lines.append("-" * 60)
            for i, suggestion in enumerate(report.suggestions, 1):
                lines.append(f"{i}. {suggestion}")
            lines.append("")
        
        report_text = '\n'.join(lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text
    
    def export_json(self, report: PerformanceReport, 
                    output_path: str) -> None:
        """
        导出JSON格式的报告
        
        Args:
            report: 性能报告对象
            output_path: 输出文件路径
        """
        data = {
            'total_execution_time': report.total_execution_time,
            'function_count': len(report.functions),
            'slow_functions': [
                {
                    'name': f.name,
                    'file': f.file,
                    'line_number': f.line_number,
                    'call_count': f.call_count,
                    'total_time': f.total_time,
                    'cumulative_time': f.cumulative_time,
                    'per_call_time': f.per_call_time
                }
                for f in report.slow_functions
            ],
            'suggestions': report.suggestions
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


@contextmanager
def timer():
    """上下文管理器：测量代码块执行时间"""
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"⏱️  执行时间: {end - start:.4f} 秒")


def example_function():
    """示例函数：计算斐波那契数列"""
    def fib(n):
        if n <= 1:
            return n
        return fib(n-1) + fib(n-2)
    
    results = []
    for i in range(20):
        results.append(fib(i))
    return results


def example_with_loop():
    """示例函数：包含循环的函数"""
    total = 0
    for i in range(1000):
        total += i
        if i % 100 == 0:
            total *= 1.01
    return total


def main():
    """主函数：演示性能分析器的使用"""
    print("🚀 智能代码性能分析器演示")
    print("=" * 50)
    
    analyzer = CodePerformanceAnalyzer()
    
    # 示例1: 分析函数性能
    print("\n📊 示例1: 分析函数性能")
    print("-" * 50)
    
    with timer():
        result = analyzer.profile_function(example_function)
    
    print(f"结果: {result['result']}")
    print(f"检测到 {len(result['functions'])} 个函数")
    
    # 示例2: 分析内存使用
    print("\n📈 示例2: 分析内存使用")
    print("-" * 50)
    
    mem_result = analyzer.profile_memory(example_with_loop)
    print(f"起始内存: {mem_result['start_memory']:.2f} MB")
    print(f"峰值内存: {mem_result['peak_memory']:.2f} MB")
    print(f"内存增量: {mem_result['memory_increase']:.2f} MB")
    
    # 示例3: 分析代码字符串
    print("\n🔍 示例3: 分析代码字符串")
    print("-" * 50)
    
    code_to_analyze = """
def slow_function():
    total = 0
    for i in range(10000):
        for j in range(100):
            total += i * j
    return total

def fast_function(n):
    return sum(i * j for i in range(n) for j in range(100))
"""
    
    report = analyzer.profile_code_string(code_to_analyze)
    report_text = analyzer.generate_report(report)
    print(report_text)
    
    # 示例4: 分析文件
    print("\n📁 示例4: 分析当前文件")
    print("-" * 50)
    
    analysis = analyzer.analyze_file(__file__)
    print(f"总行数: {analysis['total_lines']}")
    print(f"代码行: {analysis['code_lines']}")
    print(f"注释行: {analysis['comment_lines']}")
    print(f"空行: {analysis['blank_lines']}")
    print(f"函数数量: {len(analysis['functions'])}")
    print(f"类数量: {len(analysis['classes'])}")
    print(f"循环数量: {analysis['loops']}")
    print(f"复杂度评分: {analysis['complexity_score']:.2f}")
    
    print("\n✅ 性能分析完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
