#!/usr/bin/env python3
"""
Day 1: 快速排序可视化演示

这个脚本展示了快速排序算法的执行过程，
通过打印每一步的中间状态来帮助理解算法原理。

Author: MarsAssistant
Date: 2026-02-02
"""

from typing import List


def quick_sort_visualize(
    arr: List[int], 
    low: int = None, 
    high: int = None,
    step: int = 0
) -> List[int]:
    """
    快速排序可视化版本 - 展示每一步的执行过程
    
    Args:
        arr: 待排序的数组
        low: 当前子数组的起始索引
        high: 当前子数组的结束索引
        step: 记录当前是第几步
    
    Returns:
        排序后的数组
    """
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # 分区操作
        pivot_idx = partition(arr, low, high, step)
        
        # 递归排序左右子数组
        step = quick_sort_visualize(arr, low, pivot_idx - 1, step + 1)
        step = quick_sort_visualize(arr, pivot_idx + 1, high, step + 1)
    
    return arr


def partition(arr: List[int], low: int, high: int, step: int) -> int:
    """
    分区函数 - 选择最后一个元素作为基准，将数组分成两部分
    
    Args:
        arr: 数组
        low: 起始索引
        high: 结束索引
        step: 当前步骤编号
    
    Returns:
        基准元素的最终位置
    """
    pivot = arr[high]  # 选择最后一个元素作为基准
    i = low - 1  # 比基准小的元素的索引
    
    print(f"\n步骤 {step + 1}: 分区 arr[{low}:{high}], 基准值 = {pivot}")
    print(f"  当前数组: {arr[low:high+1]}")
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            if i != j:
                # 交换元素
                arr[i], arr[j] = arr[j], arr[i]
                print(f"    交换 arr[{i}]={arr[i]} <-> arr[{j}]={arr[j]}")
    
    # 将基准放到正确位置
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    print(f"    基准 {pivot} 移动到位置 {i + 1}")
    print(f"    分区后: {arr[low:high+1]}")
    
    return i + 1


def generate_random_array(size: int = 10, min_val: int = 1, max_val: = 100) -> List[int]:
    """生成指定范围内的随机数组"""
    import random
    return [random.randint(min_val, max_val) for _ in range(size)]


def main():
    """主函数 - 演示快速排序"""
    print("=" * 60)
    print("        快速排序可视化演示 (Quick Sort Visualization)")
    print("=" * 60)
    
    # 生成随机数组
    test_array = generate_random_array(8, 1, 50)
    original = test_array.copy()
    
    print(f"\n原始数组: {original}")
    print("-" * 60)
    
    # 执行排序
    sorted_array = quick_sort_visualize(test_array.copy())
    
    print("\n" + "=" * 60)
    print(f"排序完成!")
    print(f"  原始: {original}")
    print(f"  排序: {sorted_array}")
    print("=" * 60)
    
    # 性能测试
    print("\n性能测试:")
    import time
    
    sizes = [100, 1000, 5000, 10000]
    for size in sizes:
        test_arr = generate_random_array(size, 1, 100000)
        start = time.time()
        quick_sort_visualize(test_arr.copy(), enabled=False)
        elapsed = time.time() - start
        print(f"  数组大小 {size:>5}: {elapsed:.4f} 秒")
    
    print("\n时间复杂度:")
    print("  - 平均: O(n log n)")
    print("  - 最坏: O(n²)")
    print("  - 最好: O(n log n)")


if __name__ == "__main__":
    main()
