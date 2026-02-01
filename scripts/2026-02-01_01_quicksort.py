#!/usr/bin/env python3
"""
快速排序算法实现
Day 1: 经典分治算法 - 快速排序
日期: 2026-02-01
作者: MarsAssistant
"""

from typing import List
import random


def quicksort(arr: List[int]) -> List[int]:
    """快速排序主函数"""
    if len(arr) <= 1:
        return arr
    
    # 选择基准值（使用随机数避免最坏情况）
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


def quicksort_inplace(arr: List[int], low: int = 0, high: int = None) -> None:
    """原地快速排序（空间优化版）"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # 分区操作
        pivot_index = partition(arr, low, high)
        # 递归排序左右子数组
        quicksort_inplace(arr, low, pivot_index - 1)
        quicksort_inplace(arr, pivot_index + 1, high)


def partition(arr: List[int], low: int, high: int) -> int:
    """分区函数"""
    pivot = arr[high]  # 选择最后一个元素作为基准
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def benchmark():
    """性能测试"""
    import time
    
    # 测试数据
    test_data = [random.randint(1, 10000) for _ in range(1000)]
    
    # 测试非原地排序
    data1 = test_data.copy()
    start = time.time()
    result1 = quicksort(data1)
    time1 = time.time() - start
    
    # 测试原地排序
    data2 = test_data.copy()
    start = time.time()
    quicksort_inplace(data2)
    time2 = time.time() - start
    
    print(f"非原地排序耗时: {time1*1000:.2f}ms")
    print(f"原地排序耗时: {time2*1000:.2f}ms")
    print(f"排序结果验证: {'✓' if result1 == data2 else '✗'}")


if __name__ == "__main__":
    # 示例用法
    arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {arr}")
    print(f"排序结果: {quicksort(arr)}")
    
    print("\n性能测试:")
    benchmark()
