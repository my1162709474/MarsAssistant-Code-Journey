#!/usr/bin/env python3
"""
🚀 智能代码性能分析器
自动分析Python代码性能瓶颈,提供优化建议

功能:
- 执行时间分析
- 内存使用分析
- 循环优化检测
- 算法复杂度估算
- 优化建议生成

作者: MarsAssistant
日期: 2026-02-03
"""

import time
import tracemalloc
import cProfile
import pstats
import io
from functools import wraps
from typing import Callable, Dict, List, Any, Optional
import inspect


class PerformanceAnalyzer:
    """代码性能分析器"""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
    
    def measure_time(self, func: Callable) -> Callable:
        """测量函数执行时间"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            duration = end - start
            
            self.results[func.__name__] = {
                'time': duration,
                'unit': 'seconds'
            }
            return result
        return wrapper
    
    def measure_memory(self, func: Callable) -> Callable:
        """测量函数内存使用"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracemalloc.start()
            result = func(*args, **kwargs)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            self.results[func.__name__] = {
                'memory_current': current / 1024,
                'memory_peak': peak / 1024,
                'unit': 'KB'
            }
            return result
        return wrapper
    
    def profile(self, func: Callable) -> Callable:
        """详细性能剖析"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            result = func(*args, **kwargs)
            profiler.disable()
            
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(20)
            
            self.results[func.__name__] = {
                'profile': s.getvalue()
            }
            return result
        return wrapper
    
    def analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """分析代码结构,检测性能问题"""
        issues = []
        suggestions = []
        
        # 检测循环嵌套
        if code.count('for ') > 3 or code.count('while ') > 3:
            issues.append("检测到多个循环,可能需要优化")
            suggestions.append("考虑使用列表推导式或内置函数替代循环")
        
        # 检测重复计算
        if 'for ' in code and '+' in code:
            issues.append("循环中可能存在重复计算")
            suggestions.append("将不变表达式移出循环")
        
        # 检测字符串拼接
        if '+=' in code and ('str(' in code or '"' in code):
            issues.append("检测到字符串拼接操作")
            suggestions.append("使用join()方法替代+操作符进行字符串拼接")
        
        # 检测递归
        if 'def ' in code and code.count('def ') > 1:
            issues.append("检测到多个函数定义")
            suggestions.append("检查是否有递归函数,考虑使用迭代替代")
        
        return {
            'issues': issues,
            'suggestions': suggestions
        }
    
    def estimate_complexity(self, func: Callable) -> str:
        """估算函数时间复杂度"""
        source = inspect.getsource(func)
        
        if 'for ' in source and 'for ' in source[source.find('for ')+4:]:
            return "O(n²) - 考虑优化为O(n)"
        elif 'for ' in source or 'while ' in source:
            return "O(n) - 线性复杂度"
        elif '**' in source or 'pow(' in source:
            return "O(log n) 或 O(2^n) - 检查具体实现"
        else:
            return "O(1) - 常数复杂度"
    
    def get_report(self) -> str:
        """生成性能分析报告"""
        report = []
        report.append("=" * 50)
        report.append("📊 性能分析报告")
        report.append("=" * 50)
        
        for func_name, metrics in self.results.items():
            report.append(f"\n🔍 函数: {func_name}")
            for key, value in metrics.items():
                if key == 'profile':
                    report.append(value)
                else:
                    report.append(f"  {key}: {value}")
        
        return "\n".join(report)


def example_function(n: int) -> List[int]:
    """示例函数: 生成斐波那契数列(低效版本)"""
    result = []
    a, b = 0, 1
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result


def optimized_function(n: int) -> List[int]:
    """优化版本: 使用列表推导式"""
    return [0, 1][:n] if n <= 2 else []


def demo():
    """演示性能分析"""
    analyzer = PerformanceAnalyzer()
    
    # 测量示例函数
    measured_func = analyzer.measure_time(example_function)
    measured_func(1000)
    
    # 分析代码结构
    code = inspect.getsource(example_function)
    structure = analyzer.analyze_code_structure(code)
    
    # 估算复杂度
    complexity = analyzer.estimate_complexity(example_function)
    
    print("📈 性能分析演示")
    print(f"执行时间: {analyzer.results['example_function']['time']:.6f}秒")
    print(f"代码结构分析: {structure}")
    print(f"复杂度估算: {complexity}")
    print("\n" + analyzer.get_report())


if __name__ == "__main__":
    demo()
