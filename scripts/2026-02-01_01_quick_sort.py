#!/usr/bin/env python3
"""
快速排序算法实现
Quick Sort Algorithm Implementation
学习日期: 2026-02-01
"""

from typing import List
import random
import time


def quick_sort(arr: List[int]) -> List[int]:
    """
    快速排序主函数
    
    Args:
        arr: 待排序的整数列表
        
    Returns:
        排序后的列表
    """
    if len(arr) <= 1:
        return arr
    
    # 选择基准元素（使用随机数避免最坏情况）
    pivot = random.choice(arr)
    
    # 划分数组
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # 递归排序并合并
    return quick_sort(left) + middle + quick_sort(right)


def quick_sort_inplace(arr: List[int], low: int = 0, high: int = None) -> None:
    """
    原地快速排序（空间优化版本）
    
    Args:
        arr: 待排序的列表（原地修改）
        low: 起始索引
        high: 结束索引
    """
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # 分区操作，返回基准元素的最终位置
        pivot_idx = partition(arr, low, high)
        # 递归排序左右子数组
        quick_sort_inplace(arr, low, pivot_idx - 1)
        quick_sort_inplace(arr, pivot_idx + 1, high)


def partition(arr: List[int], low: int, high: int) -> int:
    """
    分区函数
    
    Args:
        arr: 数组
        low: 起始索引
        high: 结束索引
        
    Returns:
        基准元素的最终位置
    """
    # 选择最右边的元素作为基准
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def benchmark_sort(func, arr: List[int], name: str) -> tuple:
    """
    排序算法性能测试
    
    Args:
        func: 排序函数
        arr: 测试数组
        name: 算法名称
        
    Returns:
        (排序结果, 耗时)
    """
    test_arr = arr.copy()
    start = time.perf_counter()
    result = func(test_arr)
    elapsed = (time.perf_counter() - start) * 1000  # 毫秒
    
    print(f"{name}: {elapsed:.4f}ms")
    return result, elapsed


def main():
    """主函数：测试快速排序"""
    print("=" * 50)
    print("快速排序算法演示 | Quick Sort Demo")
    print("=" * 50)
    
    # 测试数据
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [3, 1, 4, 1, 5, 9, 2, 6, 5],
        list(range(10, 0, -1)),  # 逆序
        [5] * 5,  # 重复元素
        [],  # 空数组
        [42],  # 单元素
    ]
    
    for i, test_arr in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {test_arr}")
        print("-" * 30)
        
        # 非原地排序
        result1, time1 = benchmark_sort(quick_sort, test_arr, "递归版")
        print(f"  结果: {result1}")
        
        # 原地排序（需要深拷贝）
        test_arr_copy = test_arr.copy()
        start = time.perf_counter()
        quick_sort_inplace(test_arr_copy)
        time2 = (time.perf_counter() - start) * 1000
        print(f"原地版: {time2:.4f}ms -> {test_arr_copy}")
    
    # 大数据量性能测试
    print("\n" + "=" * 50)
    print("性能测试: 10000个随机整数")
    print("=" * 50)
    
    large_array = [random.randint(1, 100000) for _ in range(10000)]
    benchmark_sort(quick_sort, large_array, "递归版")
    
    print("\n快速排序完成！✨")


if __name__ == "__main__":
    main()
