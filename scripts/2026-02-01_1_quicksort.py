"""
Day 1: 快速排序算法实现

快速排序是一种分治算法，通过选择基准元素将数组分成两部分，
然后递归地对子数组进行排序。

时间复杂度: O(n log n) 平均 | O(n²) 最差
空间复杂度: O(log n)
"""

from typing import List
import random


def quicksort(arr: List[int]) -> List[int]:
    """快速排序主函数"""
    if len(arr) <= 1:
        return arr
    
    # 选择最后一个元素作为基准
    pivot = arr[-1]
    
    # 分区操作
    left = [x for x in arr[:-1] if x <= pivot]
    right = [x for x in arr[:-1] if x > pivot]
    
    # 递归排序并合并
    return quicksort(left) + [pivot] + quicksort(right)


def quicksort_inplace(arr: List[int], low: int = 0, high: int = None) -> None:
    """原地版快速排序（节省空间）"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # 分区并获取基准索引
        pivot_idx = partition(arr, low, high)
        # 递归排序子数组
        quicksort_inplace(arr, low, pivot_idx - 1)
        quicksort_inplace(arr, pivot_idx + 1, high)


def partition(arr: List[int], low: int, high: int) -> int:
    """分区函数"""
    pivot = arr[high]  # 选择最后一个元素作为基准
    i = low - 1  # 小于基准的元素索引
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]  # 交换
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]  # 放置基准
    return i + 1


# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        [3, 6, 8, 10, 1, 2, 1],
        [5, 3, 8, 4, 2],
        [1],
        [],
        [2, 2, 2, 2],
        [9, 8, 7, 6, 5, 4, 3, 2, 1],
    ]
    
    print("🚀 快速排序算法演示")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        arr_copy = test.copy()
        result = quicksort(arr_copy)
        print(f"\n测试用例 {i}:")
        print(f"  输入:  {test}")
        print(f"  输出:  {result}")
        
        # 验证结果
        expected = sorted(test)
        status = "✅ 通过" if result == expected else "❌ 失败"
        print(f"  状态:  {status}")
    
    print("\n" + "=" * 50)
    print("✨ 快速排序完成！")
