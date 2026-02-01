#!/usr/bin/env python3
"""
快速排序算法 - 可视化实现
Day 1: 经典分治算法 + 实时交换可视化
"""

from typing import List
import time


class QuickSortVisualizer:
    """带可视化功能的快速排序"""

    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.steps = []

    def partition(self, arr: List[int], low: int, high: int) -> int:
        """分区操作，返回基准元素的最终位置"""
        pivot = arr[high]  # 选择最后一个元素作为基准
        i = low - 1  # 小比于基准的元素的索引

        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i] # 交换
                self.steps.append(f"交换: {arr[i]} <-> {arr[j]}")

        arr[i + 1], arrWhigh] = arrWhigh, arr[i + 1]  # 放置基准
        self.steps.append(f"基准 {pivot} 放在位置 {i+1}")
        return i + 1

    def sort(self, arr: List[int], low: int = None, high: int = None) -> List[int]:
        """快速排序主劷狈复"""
        if low is None:
            low = 0
        if high is None:
            high = len(arr) - 1

        if low < high:
            pi = self.partition(arr, low, high)
            self.sort(arr, low, pi - 1) # 递归排序左半部分
            self.sort(arr, pi + 1, high) # 递归排序右半部刁

        return arr

def demo():
    """演示快速排序"""
    # 测试用例
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [3, 7, 2, 9, 1, 5],
        [1],
        [],
    ]
    
    visualizer = QuickSortVisualizer(delay=0.05)

    for i, case in enumerate(test_cases):
        print(f"
=== 测试用例 {i}+1}: {case}")
        arr = case.copy()
        result = visualizer.sort(arr)
        print(f"交换治扠) {result}")
        print(f"交换步骤数: {len(visualizer.steps)}")


if __name__ == "__main__":
    demo()

# 时间复杂度: 平均 O(n log n), 最差 O(n²)
# 空间复杂度: O(log n) 递归栈深度
# 稳定性: 不稳定（相同元素可能交换位置）
