#!/usr/bin/env python3
"""
快速排序算法实现 - Day 1
经典的分治算法，平均时间复杂度 O(n log n)
"""

from typing import List
import random


def quicksort(arr: List[int]) -> List[int]:
    """快速排序主函数"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


def quicksort_inplace(arr: List[int], low: int = 0, high: int = None):
    """原地快速排序（空间复杂度 O(log n)）"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_idx = partition(arr, low, high)
        quicksort_inplace(arr, low, pivot_idx - 1)
        quicksort_inplace(arr, pivot_idx + 1, high)


def partition(arr: List[int], low: int, high: int) -> int:
    """分区函数"""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def test_quicksort():
    """测试函数"""
    test_cases = [
        [],
        [1],
        [3, 1, 4, 1, 5, 9, 2, 6],
        [5, 4, 3, 2, 1],
        [1, 2, 3, 4, 5],
        [random.randint(1, 100) for _ in range(20)]
    ]
    
    for i, case in enumerate(test_cases):
        sorted_case = quicksort(case.copy())
        assert sorted_case == sorted(case), f"Test {i} failed"
        print(f"Test {i}: {case} -> {sorted_case}")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    print("🚀 快速排序算法演示")
    print("=" * 50)
    test_quicksort()
    
    # 演示
    demo_list = [64, 34, 25, 12, 22, 11, 90]
    print(f"\n原始列表: {demo_list}")
    print(f"排序结果: {quicksort(demo_list)}")
