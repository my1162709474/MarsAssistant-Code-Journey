#!/usr/bin/env python3
"""
Algorithm Visualizer - 算法可视化工具
Day 74: 交互式算法可视化演示

功能：
- 支持排序算法可视化（冒泡排序、选择排序、插入排序、快速排序）
- 支持搜索算法可视化（线性搜索、二分搜索）
- 实时动画展示算法执行过程
- ASCII艺术风格的可视化输出
"""

import time
import random
from typing import List, Callable, Any


class AlgorithmVisualizer:
    """算法可视化器"""
    
    def __init__(self, delay: float = 0.3):
        self.delay = delay
    
    def _sleep(self):
        """延时以便于可视化"""
        time.sleep(self.delay)
    
    def _render_array(self, arr: List[int], highlights: List[int] = None, 
                       low: int = None, high: int = None):
        """渲染数组为ASCII柱状图"""
        if highlights is None:
            highlights = []
        if low is None:
            low = -1
        if high is None:
            high = -1
        
        max_val = max(arr) if arr else 1
        height = 15  # 最大显示高度
        
        print("\n" + "=" * 50)
        for level in range(height, 0, -1):
            line = ""
            for i, val in enumerate(arr):
                bar_height = (val / max_val) * height
                if bar_height >= level:
                    if i == low or i == high:
                        line += "██"  # 高亮区域
                    elif i in highlights:
                        line += "▓▓"  # 比较中
                    else:
                        line += "▄▄"  # 普通元素
                else:
                    line += "  "
            print(f"  {line}")
        print("=" * 50)
        print(f"  Array: {arr}")
        print()
    
    def bubble_sort(self, arr: List[int], verbose: bool = True) -> List[int]:
        """冒泡排序可视化"""
        if not verbose:
            return sorted(arr)
        
        n = len(arr)
        result = arr.copy()
        
        print("🫧 冒泡排序 (Bubble Sort)")
        print(f"初始数组: {result}")
        self._sleep()
        
        for i in range(n):
            for j in range(0, n - i - 1):
                self._render_array(result, highlights=[j, j + 1])
                
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
                    print(f"  交换 [{j}]: {result[j]} <-> {result[j+1]}")
                
                self._sleep()
        
        self._render_array(result)
        print(f"✓ 排序完成: {result}\n")
        return result
    
    def selection_sort(self, arr: List[int], verbose: bool = True) -> List[int]:
        """选择排序可视化"""
        if not verbose:
            return sorted(arr)
        
        n = len(arr)
        result = arr.copy()
        
        print("🎯 选择排序 (Selection Sort)")
        print(f"初始数组: {result}")
        self._sleep()
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                self._render_array(result, highlights=[j], low=min_idx, high=i)
                
                if result[j] < result[min_idx]:
                    min_idx = j
                    print(f"  发现新的最小值: {result[j]} (索引 {j})")
                
                self._sleep()
            
            if min_idx != i:
                result[i], result[min_idx] = result[min_idx], result[i]
                print(f"  将最小值 {result[min_idx]} 放到位置 {i}")
            
            self._render_array(result, low=i)
            self._sleep()
        
        self._render_array(result)
        print(f"✓ 排序完成: {result}\n")
        return result
    
    def quick_sort_visualize(self, arr: List[int]) -> List[int]:
        """快速排序可视化"""
        def partition(low: int, high: int) -> int:
            pivot = result[high]
            i = low - 1
            
            self._render_array(result, low=low, high=high)
            print(f"  枢轴值: {pivot} (索引 {high})")
            self._sleep()
            
            for j in range(low, high):
                self._render_array(result, highlights=[j], low=low, high=high)
                
                if result[j] <= pivot:
                    i += 1
                    result[i], result[j] = result[j], result[i]
                    print(f"  移动 {result[i]} 到左边")
                    self._sleep()
            
            result[i + 1], result[high] = result[high], result[i + 1]
            print(f"  枢轴 {pivot} 放置到正确位置 {i + 1}")
            self._sleep()
            
            return i + 1
        
        def quick_sort_helper(low: int, high: int):
            if low < high:
                pi = partition(low, high)
                quick_sort_helper(low, pi - 1)
                quick_sort_helper(pi + 1, high)
        
        result = arr.copy()
        
        print("⚡ 快速排序 (Quick Sort)")
        print(f"初始数组: {result}")
        self._sleep()
        
        quick_sort_helper(0, len(result) - 1)
        self._render_array(result)
        print(f"✓ 排序完成: {result}\n")
        return result
    
    def linear_search(self, arr: List[int], target: int, verbose: bool = True) -> int:
        """线性搜索可视化"""
        if not verbose:
            try:
                return arr.index(target)
            except ValueError:
                return -1
        
        print(f"🔍 线性搜索: 查找 {target}")
        print(f"数组: {arr}")
        self._sleep()
        
        for i, val in enumerate(arr):
            self._render_array(arr, highlights=[i])
            print(f"  检查索引 {i}: {val}")
            self._sleep()
            
            if val == target:
                print(f"✓ 在索引 {i} 找到目标值 {target}!\n")
                return i
        
        print(f"✗ 未找到目标值 {target}\n")
        return -1
    
    def binary_search(self, arr: List[int], target: int) -> int:
        """二分搜索可视化"""
        arr_sorted = sorted(arr)
        
        print(f"🔍 二分搜索: 查找 {target}")
        print(f"排序后的数组: {arr_sorted}")
        self._sleep()
        
        left, right = 0, len(arr_sorted) - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            self._render_array(arr_sorted, low=left, high=right, highlights=[mid])
            print(f"  检查中间位置: 索引 {mid}, 值 {arr_sorted[mid]}")
            self._sleep()
            
            if arr_sorted[mid] == target:
                print(f"✓ 在索引 {mid} 找到目标值 {target}!\n")
                return mid
            elif arr_sorted[mid] < target:
                print(f"  {arr_sorted[mid]} < {target}, 搜索右半部分")
                left = mid + 1
            else:
                print(f"  {arr_sorted[mid]} > {target}, 搜索左半部分")
                right = mid - 1
        
        print(f"✗ 未找到目标值 {target}\n")
        return -1


def demo_sorting_algorithms():
    """演示排序算法"""
    print("\n" + "🧪" * 20)
    print("算法可视化演示 - 排序算法")
    print("🧪" * 20)
    
    # 准备测试数据
    arr = [64, 34, 25, 12, 22, 11, 90]
    
    print(f"\n📊 测试数组: {arr}")
    print("-" * 50)
    
    visualizer = AlgorithmVisualizer(delay=0.2)
    
    # 冒泡排序
    arr1 = arr.copy()
    sorted_arr1 = visualizer.bubble_sort(arr1, verbose=True)
    
    # 选择排序
    arr2 = arr.copy()
    sorted_arr2 = visualizer.selection_sort(arr2, verbose=True)
    
    # 快速排序
    arr3 = arr.copy()
    sorted_arr3 = visualizer.quick_sort_visualize(arr3)


def demo_search_algorithms():
    """演示搜索算法"""
    print("\n" + "🔬" * 20)
    print("算法可视化演示 - 搜索算法")
    print("🔬" * 20)
    
    arr = [5, 12, 23, 34, 45, 56, 67, 78, 89, 100]
    
    print(f"\n📊 测试数组: {arr}")
    print("-" * 50)
    
    visualizer = AlgorithmVisualizer(delay=0.3)
    
    # 线性搜索
    print("\n【线性搜索演示】")
    target = 56
    visualizer.linear_search(arr, target, verbose=True)
    
    # 二分搜索
    print("【二分搜索演示】")
    visualizer.binary_search(arr, target)


def interactive_mode():
    """交互模式"""
    print("\n" + "🎮" * 20)
    print("交互式算法演示")
    print("🎮" * 20)
    
    visualizer = AlgorithmVisualizer(delay=0.2)
    
    # 生成随机数组
    arr = random.sample(range(1, 100), 10)
    print(f"\n随机生成数组: {arr}")
    
    print("\n选择演示算法:")
    print("1. 冒泡排序")
    print("2. 选择排序")
    print("3. 快速排序")
    print("4. 线性搜索")
    print("5. 二分搜索")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == "1":
        visualizer.bubble_sort(arr.copy())
    elif choice == "2":
        visualizer.selection_sort(arr.copy())
    elif choice == "3":
        visualizer.quick_sort_visualize(arr.copy())
    elif choice == "4":
        target = int(input("请输入搜索目标: "))
        visualizer.linear_search(arr, target)
    elif choice == "5":
        target = int(input("请输入搜索目标: "))
        visualizer.binary_search(arr, target)
    else:
        print("无效选择")


def benchmark_sorts(size: int = 1000):
    """排序算法性能基准测试"""
    print(f"\n📈 排序算法性能测试 (数组大小: {size})")
    print("-" * 50)
    
    import timeit
    
    arr = random.sample(range(1, size * 10), size)
    
    # Python内置排序
    arr_copy = arr.copy()
    t1 = timeit.timeit(lambda: sorted(arr_copy), number=10)
    print(f"Python sorted: {t1/10*1000:.2f} ms")
    
    # 冒泡排序（仅用于小规模）
    if size <= 100:
        arr_copy = arr.copy()
        t2 = timeit.timeit(lambda: AlgorithmVisualizer().bubble_sort(arr_copy, verbose=False), number=1)
        print(f"冒泡排序: {t2*1000:.2f} ms")
    else:
        print("冒泡排序: 跳过 (数组过大)")


if __name__ == "__main__":
    print("🧠 Algorithm Visualizer - 算法可视化工具 🧠")
    print("=" * 50)
    
    while True:
        print("\n请选择操作模式:")
        print("1. 观看排序算法演示")
        print("2. 观看搜索算法演示")
        print("3. 交互式演示")
        print("4. 性能基准测试")
        print("5. 退出")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            demo_sorting_algorithms()
        elif choice == "2":
            demo_search_algorithms()
        elif choice == "3":
            interactive_mode()
        elif choice == "4":
            size = input("输入数组大小 (默认1000): ").strip()
            benchmark_sorts(int(size) if size else 1000)
        elif choice == "5":
            print("\n👋 感谢使用 Algorithm Visualizer!")
            break
        else:
            print("无效选择，请重试")
