#!/usr/bin/env python3
"""
排序算法可视化工具
Sorting Algorithm Visualizer

展示不同排序算法的执行过程和效率对比
"""

import time
import random
from typing import List, Callable


class SortingVisualizer:
    """排序算法可视化器"""
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
    
    def bubble_sort(self, arr: List[int]) -> List[int]:
        """冒泡排序 - O(n²)"""
        result = arr.copy()
        n = len(result)
        comparisons = 0
        swaps = 0
        
        for i in range(n):
            for j in range(0, n - i - 1):
                comparisons += 1
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
                    swaps += 1
        
        return result, comparisons, swaps
    
    def quick_sort(self, arr: List[int]) -> List[int]:
        """快速排序 - O(n log n)"""
        result = arr.copy()
        comparisons = 0
        swaps = 0
        
        def partition(low: int, high: int) -> int:
            nonlocal comparisons, swaps
            pivot = result[high]
            i = low - 1
            
            for j in range(low, high):
                comparisons += 1
                if result[j] <= pivot:
                    i += 1
                    result[i], result[j] = result[j], result[i]
                    swaps += 1
            
            result[i + 1], result[high] = result[high], result[i + 1]
            swaps += 1
            return i + 1
        
        def sort(low: int, high: int):
            if low < high:
                pi = partition(low, high)
                sort(low, pi - 1)
                sort(pi + 1, high)
        
        sort(0, len(result) - 1)
        return result, comparisons, swaps
    
    def merge_sort(self, arr: List[int]) -> List[int]:
        """归并排序 - O(n log n)"""
        result = arr.copy()
        comparisons = 0
        swaps = 0
        
        def merge(left: int, mid: int, right: int):
            nonlocal comparisons, swaps
            left_arr = result[left:mid + 1]
            right_arr = result[mid + 1:right + 1]
            
            i = j = 0
            k = left
            
            while i < len(left_arr) and j < len(right_arr):
                comparisons += 1
                if left_arr[i] <= right_arr[j]:
                    result[k] = left_arr[i]
                    i += 1
                else:
                    result[k] = right_arr[j]
                    j += 1
                k += 1
                swaps += 1
            
            while i < len(left_arr):
                result[k] = left_arr[i]
                i += 1
                k += 1
                swaps += 1
            
            while j < len(right_arr):
                result[k] = right_arr[j]
                j += 1
                k += 1
                swaps += 1
        
        def sort(l: int, r: int):
            if l < r:
                mid = (l + r) // 2
                sort(l, mid)
                sort(mid + 1, r)
                merge(l, mid, r)
        
        sort(0, len(result) - 1)
        return result, comparisons, swaps
    
    def benchmark(self, arr: List[int], algorithm: Callable) -> dict:
        """测试排序算法性能"""
        start = time.time()
        sorted_arr, comparisons, swaps = algorithm(arr)
        elapsed = time.time() - start
        
        return {
            'sorted': sorted_arr,
            'comparisons': comparisons,
            'swaps': swaps,
            'time_ms': round(elapsed * 1000, 3)
        }


def generate_test_data(size: int = 100) -> List[int]:
    """生成测试数据"""
    return [random.randint(1, 1000) for _ in range(size)]


def print_comparison(results: dict):
    """打印算法对比结果"""
    print("\n" + "=" * 60)
    print("排序算法性能对比 (数组大小: 100)")
    print("=" * 60)
    print(f"{'算法':<15} {'比较次数':>12} {'交换次数':>10} {'时间(ms)':>12}")
    print("-" * 60)
    
    for name, data in results.items():
        print(f"{name:<15} {data['comparisons']:>12} {data['swaps']:>10} {data['time_ms']:>12.3f}")
    
    print("=" * 60)


if __name__ == "__main__":
    print("🎯 排序算法可视化工具")
    print("生成随机数组并测试不同排序算法...\n")
    
    # 设置随机种子以保证可复现
    random.seed(42)
    test_data = generate_test_data(100)
    
    print(f"原始数组(前10个): {test_data[:10]}...")
    
    visualizer = SortingVisualizer()
    
    results = {
        '冒泡排序': visualizer.benchmark(test_data, visualizer.bubble_sort),
        '快速排序': visualizer.benchmark(test_data, visualizer.quick_sort),
        '归并排序': visualizer.benchmark(test_data, visualizer.merge_sort),
    }
    
    print_comparison(results)
    
    # 验证排序正确性
    print("\n✅ 排序正确性验证:")
    sorted_check = sorted(test_data)
    for name, data in results.items():
        is_correct = data['sorted'] == sorted_check
        print(f"  {name}: {'✓ 正确' if is_correct else '✗ 错误'}")
